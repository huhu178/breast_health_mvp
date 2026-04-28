# -*- coding: utf-8 -*-
"""
B端报告管理路由
处理专业报告的生成、查看、管理
"""
from flask import Blueprint, request, jsonify, render_template, send_file
from models import db, BPatient, BHealthRecord, BReport, KnowledgeItem, CPatient, CHealthRecord, CReport
from utils.decorators import login_required
from utils.response import Response
from services.llm_service import llm_generator
from config import Config
from datetime import datetime
import random
import string
import io

b_report_bp = Blueprint('b_report', __name__, url_prefix='/api/b/reports')

# LLM服务已在 llm_service.py 模块加载时自动配置，无需重复设置

# 导入统一的ID生成工具
from utils.id_generator import generate_report_code


@b_report_bp.route('', methods=['GET'])
@login_required
def get_all_reports(current_user):
    """获取所有报告（支持分页和筛选）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        patient_id = request.args.get('patient_id', type=int)
        risk_level = request.args.get('risk_level')
        
        query = BReport.query
        
        # 筛选条件
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        if risk_level:
            query = query.filter_by(risk_level=risk_level)
        
        # 排序
        query = query.order_by(BReport.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        reports_data = []
        for report in pagination.items:
            report_dict = report.to_dict()
            # 添加患者信息
            patient = BPatient.query.get(report.patient_id)
            if patient:
                report_dict['patient_name'] = patient.name
                report_dict['patient_code'] = patient.patient_code
            # 添加报告类型
            report_dict['report_type'] = 'b_end'
            reports_data.append(report_dict)
        
        return Response.success({
            'reports': reports_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        return Response.error(f'获取报告列表失败: {str(e)}')


@b_report_bp.route('/<int:report_id>', methods=['GET'])
@login_required
def get_report_detail(current_user, report_id):
    """
    获取报告详情

    ISDoc
    @description 兼容B端/C端两套报告：通过 query 参数 type=b_end/c_end 区分
    @queryParam type {string} 可选，默认 b_end
    """
    try:
        report_type = request.args.get('type', 'b_end')

        if report_type == 'c_end':
            report = CReport.query.get(report_id)
            if not report:
                return Response.error('报告不存在', 404)
            
            report_dict = report.to_dict()
            # C端报告页需要 HTML
            report_dict['report_html'] = report.report_html
            patient = CPatient.query.get(report.patient_id)
            if patient:
                report_dict['patient'] = patient.to_dict()
                report_dict['nodule_type'] = getattr(patient, 'nodule_type', None) or 'breast'
            if report.record_id:
                record = CHealthRecord.query.get(report.record_id)
                if record:
                    report_dict['record'] = record.to_dict()
            report_dict['report_type'] = 'c_end'
            return Response.success(report_dict)

        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)

        report_dict = report.to_dict()
        patient = BPatient.query.get(report.patient_id)
        if patient:
            report_dict['patient'] = patient.to_dict()
            if hasattr(patient, 'nodule_type') and patient.nodule_type:
                report_dict['nodule_type'] = patient.nodule_type
            else:
                report_dict['nodule_type'] = 'breast'
        if report.record_id:
            record = BHealthRecord.query.get(report.record_id)
            if record:
                report_dict['record'] = record.to_dict()
        report_dict['report_type'] = 'b_end'
        
        return Response.success(report_dict)
        
    except Exception as e:
        return Response.error(f'获取报告详情失败: {str(e)}')


@b_report_bp.route('/generate', methods=['POST'])
@login_required
def generate_report(current_user):
    """
    生成专业健康管理报告
    
    流程：
    1. 获取健康档案
    2. 匹配知识库
    3. 决策树处理
    4. LLM生成报告
    5. 保存报告
    """
    try:
        data = request.json
        record_id = data.get('record_id')
        
        # 1. 获取健康档案
        record = BHealthRecord.query.get(record_id)
        if not record:
            return Response.error('健康档案不存在', 404)
        
        patient = BPatient.query.get(record.patient_id)
        if not patient:
            return Response.error('患者不存在', 404)
        
        # 2. 获取患者的结节类型，默认为breast
        nodule_type = patient.nodule_type if hasattr(patient, 'nodule_type') and patient.nodule_type else 'breast'

        # 3. 构建患者数据（使用report_manager的函数，根据nodule_type自动提取正确字段）
        from utils.report_manager import prepare_llm_patient_data
        patient_data = prepare_llm_patient_data(record, nodule_type, patient)

        print(f"\n[报告生成] 患者ID: {patient.id}, 结节类型: {nodule_type}")
        print(f"[报告生成] 提取的字段数量: {len([k for k,v in patient_data.items() if v is not None and v != ''])}")

        # 添加一些旧逻辑需要的字段格式（兼容处理）
        if record.symptoms:
            patient_data['symptoms'] = record.symptoms.split(',') if isinstance(record.symptoms, str) else record.symptoms
        # 注意：以下字段前端表单中没有，不再添加：
        # - nodule_discovery_time (已使用 breast_discovery_date)
        # - course_stage (前端表单中没有)
        # - tnm_stage (前端表单中没有)
        
        # 3. 知识库匹配和决策树处理（已移除，直接使用空值）
        # 注：知识库只有乳腺数据，其他结节类型暂不支持，后续可添加
        matched_knowledge = []  # 空列表，LLM会显示"无相关医学知识"
        tree_result = {}  # 空字典，LLM会使用默认值

        # 5. 生成LLM报告内容
        from routes.llm_helpers import (
            generate_comprehensive_conclusion_with_llm, 
            generate_imaging_conclusion_with_llm,
            generate_recommendations_by_category
        )
        
        # 5.1 生成按类别分组的建议草稿（新增）
        print("\n" + "="*60)
        print("📝 生成分类建议草稿...")
        print("="*60)
        recommendations_draft = generate_recommendations_by_category(
            patient_data, matched_knowledge
        )
        print(f"✅ 已生成 {len(recommendations_draft.get('recommendations', []))} 条分类建议")
        
        # 5.2 生成影像学综合结论（包含影像学评估、综合分析和随访建议）
        # 注意：不再单独生成疾病史评估，因为已经包含在影像学评估的"其次"部分
        imaging_conclusion_dict = generate_imaging_conclusion_with_llm(
            patient_data, tree_result, matched_knowledge, nodule_type=nodule_type
        )
        
        # 格式化换行，确保"首先"、"其次"、"最后"前面有换行
        from routes.llm_helpers import clean_markdown_formatting, format_text_with_line_breaks
        conclusion = clean_markdown_formatting(imaging_conclusion_dict.get('conclusion', ''))
        risk_warning = clean_markdown_formatting(imaging_conclusion_dict.get('risk_warning', ''))
        # 将换行符转换为HTML的<br/>标签
        conclusion = format_text_with_line_breaks(conclusion)
        risk_warning = format_text_with_line_breaks(risk_warning)
        imaging_conclusion_dict['conclusion'] = conclusion
        imaging_conclusion_dict['risk_warning'] = risk_warning

        # 6. 生成报告编号（提前生成，用于HTML）
        report_code_generated = generate_report_code()
        current_date = datetime.now().strftime('%Y-%m-%d')

        # 7. 渲染HTML报告（使用报告管理器根据结节类型选择正确模板）
        from utils.report_manager import get_template_path, extract_template_fields

        # 7.1 获取正确的模板路径（根据nodule_type: breast/lung/thyroid/breast_lung/breast_thyroid/lung_thyroid/triple）
        template_path = get_template_path(nodule_type)

        # 7.2 提取模板所需字段（根据nodule_type自动提取相应字段）
        template_fields = extract_template_fields(patient, record, nodule_type)

        # 7.3 添加LLM生成的内容和其他动态字段
        # 正确解包imaging_conclusion字典（包含影像学评估、综合分析和随访建议）
        template_fields.update({
            'report_code': report_code_generated,
            'current_date': current_date,
            'imaging_conclusion': imaging_conclusion_dict.get('conclusion', ''),  # 总体评估与随访建议
            'imaging_risk_warning': imaging_conclusion_dict.get('risk_warning', ''),  # 风险提示
        })

        # 7.4 渲染报告
        report_html = render_template(template_path, **template_fields)

        print(f"✅ 使用模板: {template_path} 生成 {patient.nodule_type} 报告")
        
        # 8. 生成报告摘要
        report_summary = f"BI-RADS {record.birads_level}级"
        
        # 10. 保存报告（使用之前生成的report_code）
        report = BReport(
            patient_id=patient.id,
            record_id=record.id,
            report_code=report_code_generated,
            recommendations_draft=recommendations_draft,  # 保存分类建议草稿（JSON格式）
            report_html=report_html,  # 临时保存预览版报告
            report_summary=report_summary,
            risk_level=None,  # 不再使用风险评估
            risk_score=None,  # 不再使用风险评估
            generated_by=current_user.id,
            # 保存影像学评估结论（包含影像学评估、综合分析和随访建议）
            imaging_conclusion=imaging_conclusion_dict.get('conclusion', ''),
            imaging_risk_warning=imaging_conclusion_dict.get('risk_warning', ''),
            # 不再单独保存疾病史评估，因为已包含在imaging_conclusion中
            medical_conclusion=None,  # 清空旧数据
            medical_risk_warning=None  # 清空旧数据
        )
        
        db.session.add(report)
        db.session.commit()
        
        return Response.success({
            'id': report.id,  # 前端需要id字段
            'report_id': report.id,
            'report_code': report.report_code
        }, '报告生成成功', 201)
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Response.error(f'生成报告失败: {str(e)}')


@b_report_bp.route('/<int:report_id>', methods=['DELETE'])
@login_required
def delete_report(current_user, report_id):
    """
    删除报告

    ISDoc
    @description 兼容B端/C端两套报告：通过 query 参数 type=b_end/c_end 区分
    @queryParam type {string} 可选，默认 b_end
    """
    try:
        report_type = request.args.get('type', 'b_end')
        if report_type == 'c_end':
            report = CReport.query.get(report_id)
            if not report:
                return Response.error('报告不存在', 404)
            db.session.delete(report)
            db.session.commit()
            return Response.success(None, '报告删除成功')

        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)
        
        db.session.delete(report)
        db.session.commit()
        
        return Response.success(None, '报告删除成功')
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'删除报告失败: {str(e)}')


@b_report_bp.route('/<int:report_id>/recommendations', methods=['GET'])
@login_required
def get_recommendations(current_user, report_id):
    """获取报告的分类建议草稿"""
    try:
        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)
        
        if not report.recommendations_draft:
            return Response.error('报告尚未生成分类建议', 404)
        
        return Response.success({
            'report_id': report.id,
            'report_code': report.report_code,
            'recommendations': report.recommendations_draft.get('recommendations', [])
        }, '获取成功')
        
    except Exception as e:
        return Response.error(f'获取建议失败: {str(e)}')


@b_report_bp.route('/<int:report_id>/recommendations/<int:index>', methods=['PUT'])
@login_required
def update_recommendation(current_user, report_id, index):
    """更新某条建议"""
    try:
        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)
        
        if not report.recommendations_draft:
            return Response.error('报告尚未生成分类建议', 404)
        
        data = request.get_json()
        recommendations = report.recommendations_draft.get('recommendations', [])
        
        if index < 0 or index >= len(recommendations):
            return Response.error('建议索引无效', 400)
        
        # 更新建议内容
        if 'recommendation' in data:
            recommendations[index]['recommendation'] = data['recommendation']
        if 'is_approved' in data:
            recommendations[index]['is_approved'] = data['is_approved']
        
        # 保存更新（使用flag_modified确保JSON字段被标记为已修改）
        from sqlalchemy.orm.attributes import flag_modified
        report.recommendations_draft = {'recommendations': recommendations}
        flag_modified(report, 'recommendations_draft')
        db.session.commit()
        
        print(f"✅ 建议 #{index} 已更新: is_approved={recommendations[index].get('is_approved', False)}")
        
        return Response.success({
            'recommendation': recommendations[index]
        }, '更新成功')
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'更新建议失败: {str(e)}')


@b_report_bp.route('/<int:report_id>/recommendations/<int:index>', methods=['DELETE'])
@login_required
def delete_recommendation(current_user, report_id, index):
    """删除某条建议"""
    try:
        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)
        
        if not report.recommendations_draft:
            return Response.error('报告尚未生成分类建议', 404)
        
        recommendations = report.recommendations_draft.get('recommendations', [])
        
        if index < 0 or index >= len(recommendations):
            return Response.error('建议索引无效', 400)
        
        # 删除建议
        deleted_rec = recommendations.pop(index)
        
        # 保存更新
        report.recommendations_draft = {'recommendations': recommendations}
        db.session.commit()
        
        return Response.success({
            'deleted_recommendation': deleted_rec,
            'remaining_count': len(recommendations)
        }, '删除成功')
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'删除建议失败: {str(e)}')


@b_report_bp.route('/<int:report_id>/recommendations/approve-all', methods=['POST'])
@login_required
def approve_all_recommendations(current_user, report_id):
    """批准所有建议"""
    try:
        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)
        
        if not report.recommendations_draft:
            return Response.error('报告尚未生成分类建议', 404)
        
        recommendations = report.recommendations_draft.get('recommendations', [])
        
        # 全部标记为已批准
        for rec in recommendations:
            rec['is_approved'] = True
        
        # 保存更新（使用flag_modified确保JSON字段被标记为已修改）
        from sqlalchemy.orm.attributes import flag_modified
        report.recommendations_draft = {'recommendations': recommendations}
        flag_modified(report, 'recommendations_draft')
        db.session.commit()
        
        print(f"✅ 已批准所有 {len(recommendations)} 条建议")
        
        return Response.success({
            'approved_count': len(recommendations)
        }, '全部批准成功')
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'批准失败: {str(e)}')


@b_report_bp.route('/<int:report_id>/finalize', methods=['POST'])
@login_required
def finalize_report(current_user, report_id):
    """生成最终打印报告（整合所有已批准的建议）"""
    try:
        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)

        # 若没有 recommendations_draft，直接用已有 report_html 完成审核
        if not report.recommendations_draft:
            report.status = 'finalized'
            db.session.commit()
            return Response.success({
                'report_id': report.id,
                'report_html': report.report_html or ''
            }, '审核通过')

        recommendations = report.recommendations_draft.get('recommendations', [])

        # 若没有手动批准的建议，自动将全部建议标记为已批准
        approved_recs = [rec for rec in recommendations if rec.get('is_approved', False)]
        if not approved_recs:
            for rec in recommendations:
                rec['is_approved'] = True
            report.recommendations_draft = {**report.recommendations_draft, 'recommendations': recommendations}
            db.session.flush()
            approved_recs = recommendations

        # 使用LLM整合所有已批准的建议为流畅的报告
        from routes.llm_helpers import llm_generator, clean_markdown_formatting
        
        # 构建提示词
        # 构建建议文本，处理可能的字段名不一致
        recommendations_text = '\n\n'.join([
            f"【{rec.get('category', '未知类别')}】\n{rec.get('recommendation', rec.get('content', '无内容'))}"
            for rec in approved_recs
        ])
        
        # 调试：打印建议文本长度
        print(f"📝 建议文本总长度: {len(recommendations_text)} 字符")
        print(f"📝 建议文本预览: {recommendations_text[:200]}...")
        
        # 获取患者和档案信息
        patient = BPatient.query.get(report.patient_id)
        record = BHealthRecord.query.get(report.record_id)
        
        prompt = f"""你是一位专业的乳腺健康管理师，请将以下分类建议整合成一份详细、温暖、专业的健康管理报告：

患者信息：
- 姓名：{patient.name if patient else '未知'}
- 年龄：{record.age if record else '未知'}岁
- BI-RADS分级：{record.birads_level if record else '未知'}级
- 结节大小：{record.nodule_size if record else '未知'}

分类建议（{len(approved_recs)}条）：
{recommendations_text}

要求：
1. **突出重点**（关键！）：
   - 将最重要、最紧急的建议放在前面，使用"首先"、"特别重要"、"务必"、"必须"等强调词汇
   - 对于高风险情况（如BI-RADS 4级及以上、有家族史、有症状等），要明确强调其紧迫性和重要性
   - 使用"⚠️"标记或加粗语气突出关键信息
   - 将最关键的3-5条建议在开头段落中重点强调

2. **详细充分**：每个维度的建议都要充分展开，给出具体的理由和执行方法

3. **开头温暖问候+重点提示**：以"亲爱的XX女士/先生"开头，紧接着用1-2句话强调当前最重要的健康管理任务（50-100字）

4. **结构完整**，按重要性排序，分段清晰：
   - 第一段：风险评估总结+最重要建议（120-150字，必须突出最关键的健康管理任务）
   - 第二段：随访监测计划（100-120字，强调复查的紧迫性和重要性）
   - 第三段：饮食营养建议（150-180字）
   - 第四段：运动与生活方式（120-150字）
   - 第五段：症状管理与心理调适（100-120字）
   - 第六段：特殊关注事项（80-100字，再次强调需要特别注意的事项）
   - 结尾：温暖鼓励+行动号召（50-80字）

5. **语言流畅**：像健康管理师亲自写的报告，温暖贴心但不失专业

6. **保留具体数值**：如"每天400g蔬菜"、"每周150分钟运动"、"每6个月复查"等精确信息

7. **实用性强**：每条建议都要具有可操作性，告诉患者如何执行

8. **总字数700-900字**

9. **优先级排序原则**：
   - 结论与预警 > 风险因素 > 影像学建议 > 症状管理 > 其他建议
   - 高风险情况（BI-RADS 4级及以上）的建议必须放在最前面强调

直接输出完整报告，分段清晰，不要额外标题，不要"报告如下"等开场白。"""

        # 调用LLM生成最终报告
        print("\n" + "="*60)
        print("📄 生成最终打印报告...")
        print("="*60)
        
        final_report_text = llm_generator._call_llm_api(prompt)
        
        if not final_report_text:
            return Response.error('LLM生成最终报告失败', 500)
        
        # 清理markdown格式标记
        final_report_text = clean_markdown_formatting(final_report_text)
        
        # 渲染为HTML（用于打印）
        from flask import render_template
        
        final_report_html = render_template(
            'reports/final_report.html',
            patient_name=patient.name if patient else '未知',
            patient_age=record.age if record else '未知',
            report_date=datetime.now().strftime('%Y年%m月%d日'),
            report_code=report.report_code,
            risk_level=report.risk_level,
            final_content=final_report_text,
            birads_level=record.birads_level if record else '未知',
            nodule_size=record.nodule_size if record else '未知',
            symptoms=record.symptoms if record else '无',
            family_history=record.family_history if record else '无'
        )
        
        # 保存最终报告（覆盖原来的 report_html）
        report.report_html = final_report_html
        report.status = 'finalized'
        db.session.commit()
        
        print(f"✅ 最终报告生成成功")
        
        return Response.success({
            'report_id': report.id,
            'report_code': report.report_code,
            'final_report_html': final_report_html,
            'approved_recommendations_count': len(approved_recs)
        }, '最终报告生成成功')
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Response.error(f'生成最终报告失败: {str(e)}')


@b_report_bp.route('/<int:report_id>/export-pdf', methods=['GET'])
@login_required
def export_report_pdf(current_user, report_id):
    """
    导出报告为PDF文件（一键下载）
    
    ISDoc
    @description 兼容B端/C端两套报告：通过 query 参数 type=b_end/c_end 区分
    @queryParam type {string} 可选，默认 b_end
    """
    try:
        print(f"\n📄 开始导出报告 #{report_id} 为PDF")
        
        report_type = request.args.get('type', 'b_end')
        
        # 兼容C端报告
        if report_type == 'c_end':
            report = CReport.query.get(report_id)
            if not report:
                print(f"❌ C端报告 #{report_id} 不存在")
                return Response.error('报告不存在', 404)
            
            # C端报告直接使用 report_html
            if not report.report_html:
                print(f"❌ C端报告 #{report_id} 的HTML内容为空")
                return Response.error('报告HTML内容为空，无法导出PDF', 400)
            
            report_html = report.report_html
            report_code = report.report_code
            print(f"✅ 使用C端报告HTML（长度: {len(report_html)} 字符）")
        else:
            report = BReport.query.get(report_id)
            if not report:
                print(f"❌ B端报告 #{report_id} 不存在")
                return Response.error('报告不存在', 404)
            
            report_code = report.report_code
        
            # 如果report_html为空，尝试生成它
            if not report.report_html:
                print(f"⚠️ B端报告 #{report_id} 的HTML内容为空，尝试生成...")
                
                # 获取患者和档案
                patient = BPatient.query.get(report.patient_id)
                record = BHealthRecord.query.get(report.record_id)
                
                if not patient or not record:
                    return Response.error('患者或档案不存在', 404)
                
                # 获取结节类型
                nodule_type = patient.nodule_type if hasattr(patient, 'nodule_type') and patient.nodule_type else 'breast'
                
                # 使用工具模块准备数据
                from utils.report_manager import get_template_path, extract_template_fields
                
                # 获取模板路径
                template_path = get_template_path(nodule_type)
                
                # 提取所有模板需要的字段
                template_fields = extract_template_fields(patient, record, nodule_type)
                
                # 使用报告中保存的AI评估内容（已审核的）
                imaging_warning = report.imaging_risk_warning or report.medical_risk_warning or ''
                if nodule_type == 'triple':
                    template_fields.update({
                        'imaging_conclusion': report.imaging_conclusion or '',
                        'imaging_risk_warning': imaging_warning,
                        'risk_warning': imaging_warning,  # 兼容旧变量名
                        'comprehensive_conclusion': report.medical_conclusion or report.imaging_conclusion or '',
                        'tcm_analysis': '（中医分析接口数据待接入）',
                        'risk_score': report.risk_score,
                        'risk_level': report.risk_level,
                        'report_code': report.report_code,
                    })
                elif nodule_type in ['breast_lung', 'breast_thyroid', 'lung_thyroid']:
                    template_fields.update({
                        'imaging_conclusion': report.imaging_conclusion or '',
                        'imaging_risk_warning': imaging_warning,
                        'risk_warning': imaging_warning,  # 兼容旧变量名
                        'comprehensive_conclusion': report.medical_conclusion or report.imaging_conclusion or '',
                        'risk_score': report.risk_score,
                        'risk_level': report.risk_level,
                        'report_code': report.report_code,
                    })
                else:
                    # 单结节类型（breast/lung/thyroid）：只使用影像学评估（包含综合分析和随访建议）
                    template_fields.update({
                        'imaging_conclusion': report.imaging_conclusion or '',
                        'imaging_risk_warning': report.imaging_risk_warning or '',
                        'risk_score': report.risk_score,
                        'risk_level': report.risk_level,
                        'report_code': report.report_code,
                    })
                
                # 渲染模板
                report_html = render_template(template_path, **template_fields)
                
                # 保存到数据库（可选，用于下次快速访问）
                report.report_html = report_html
                db.session.commit()
                
                print(f"✅ B端报告HTML已生成并保存（长度: {len(report_html)} 字符）")
            else:
                report_html = report.report_html
                print(f"✅ 使用已保存的B端报告HTML（长度: {len(report_html)} 字符）")
        
        # 在导入 Playwright 之前设置环境变量
        import os
        import platform
        # 只在非Windows系统上添加Linux路径（Windows使用自己的PATH管理）
        if platform.system() != 'Windows':
            original_path = os.environ.get('PATH', '')
            os.environ['PATH'] = '/usr/bin:/usr/local/bin:' + original_path
        # ⚠️ 注意：不要把 PLAYWRIGHT_BROWSERS_PATH 指到 site-packages/playwright/driver
        # 该目录是 Playwright driver，不是浏览器安装目录。
        # 如果错误设置，会导致 Playwright 一直去错误路径找 chromium 可执行文件，
        # 即便已执行 `python -m playwright install chromium` 也会报 Executable doesn't exist。
        #
        # 这里显式清理该变量，让 Playwright 使用其默认的浏览器缓存目录（如 ~/.cache/ms-playwright）。
        os.environ.pop('PLAYWRIGHT_BROWSERS_PATH', None)
        
        # 尝试导入playwright
        try:
            from playwright.sync_api import sync_playwright
            print("✅ Playwright导入成功")
        except ImportError as e:
            print(f"❌ Playwright导入失败: {e}")
            return Response.error('PDF生成库未安装，请运行: pip install playwright && playwright install chromium', 500)
        
        # 使用Playwright生成PDF（利用浏览器的完美分页）
        print("📝 开始使用浏览器生成PDF...")
        try:
            import tempfile
            
            # 注入完整的PDF打印样式（确保旧报告也能正确导出）
            pdf_print_styles = """
            <style>
                @media print {
                    @page {
                        size: A4;
                        margin: 10mm 12mm;  /* 上下10mm（减小），左右12mm */
                    }
                    /* 封面页优化 - 确保独占一页，不会溢出到下一页 */
                    .cover-page {
                        position: relative !important;
                        page-break-after: always !important;
                        page-break-inside: avoid !important;
                        /* A4页面高度297mm，减去上下边距20mm（10mm*2），内容区域约277mm */
                        /* 但考虑到padding，实际可用高度更小，设置为250mm更安全 */
                        height: 250mm !important;
                        min-height: 250mm !important;
                        max-height: 250mm !important;
                        overflow: hidden !important;
                        box-sizing: border-box !important;
                        margin: 0 !important;
                        padding: 40px !important;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                        display: flex !important;
                        flex-direction: column !important;
                        justify-content: center !important;
                        align-items: center !important;
                    }
                    body {
                        margin: 0;
                        padding: 0;
                        background: white;
                        font-size: 11px;
                    }
                    .container {
                        width: 100% !important;
                        max-width: none !important;
                        box-shadow: none !important;
                        margin: 0 !important;
                        padding: 8px 0 !important;  /* 只保留上下内边距 */
                        border-radius: 0 !important;
                    }
                    table {
                        width: 100% !important;
                        table-layout: auto !important;
                        font-size: 10px !important;
                        page-break-inside: auto;
                    }
                    td, th {
                        word-wrap: break-word !important;
                        word-break: break-word !important;
                        white-space: normal !important;
                        padding: 5px !important;
                    }
                    tr {
                        page-break-inside: avoid;
                    }
                    h1, h2, h3 {
                        page-break-after: avoid;
                        page-break-inside: avoid;
                    }
                    .page-break {
                        page-break-after: always !important;
                        height: 0 !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        visibility: hidden !important;
                        display: none !important;  /* PDF中完全隐藏 */
                    }
                    /* 免责声明和footer优化 */
                    .disclaimer {
                        page-break-before: avoid !important;
                        page-break-inside: avoid !important;
                        page-break-after: avoid !important;
                        background-color: #f5f5f5 !important;
                    }
                    footer {
                        page-break-before: avoid !important;
                        page-break-inside: avoid !important;
                        page-break-after: avoid !important;  /* 防止footer后分页导致重复 */
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                        color: white !important;
                        padding: 15px 12px !important;
                        margin-top: 10px !important;
                        margin-bottom: 0 !important;  /* 移除底部边距，避免空白 */
                    }
                    /* 防止footer在分页时重复显示 */
                    footer:not(:last-of-type) {
                        display: none !important;  /* 隐藏多余的footer */
                    }
                    footer h3, footer strong, footer p {
                        color: white !important;
                    }
                }
            </style>
            """
            
            # 将样式注入HTML（使用生成的report_html变量）
            html_with_styles = report_html
            if '</head>' in html_with_styles:
                html_with_styles = html_with_styles.replace('</head>', f'{pdf_print_styles}</head>')
            elif '<body' in html_with_styles:
                html_with_styles = html_with_styles.replace('<body', f'{pdf_print_styles}<body')
            else:
                html_with_styles = pdf_print_styles + html_with_styles
            
            # 创建临时HTML文件
            import pathlib
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_with_styles)
                temp_html = f.name
            
            # 转换为绝对路径（Windows兼容）
            temp_html_path = pathlib.Path(temp_html).absolute()
            # 转换为file:// URL格式（Windows自动处理路径分隔符）
            file_url = temp_html_path.as_uri()
            
            print(f"📄 临时HTML文件: {temp_html}")
            print(f"📄 文件URL: {file_url}")
            
            # 使用Playwright打开浏览器并打印为PDF
            # 环境变量已在导入 Playwright 之前设置
            # 打印环境变量用于调试
            print(f"🔍 PATH环境变量: {os.environ.get('PATH', 'NOT SET')[:200]}")
            # Windows兼容：只在非Windows系统上使用which命令
            if platform.system() != 'Windows':
                try:
                    node_path = os.popen('which node 2>/dev/null').read().strip()
                    print(f"🔍 Node.js路径: {node_path or 'NOT FOUND'}")
                except:
                    pass
            
            with sync_playwright() as p:
                print("✅ Playwright 上下文管理器创建成功")
                browser = p.chromium.launch(headless=True)
                print("✅ 浏览器启动成功")
                
                # 设置A4页面尺寸的viewport（确保内容不被截断）
                page = browser.new_page(viewport={
                    'width': 794,   # A4宽度（像素，96dpi）
                    'height': 1123  # A4高度（像素，96dpi）
                })
                
                # 加载HTML（使用标准file:// URL）
                page.goto(file_url, wait_until='networkidle', timeout=30000)
                
                # 等待页面完全加载（包括样式渲染）
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(500)  # 额外等待500ms确保样式完全应用
                
                # 生成PDF（使用浏览器的打印功能，分页完美）
                pdf_bytes = page.pdf(
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '0mm',     # CSS @page 已设置边距
                        'bottom': '0mm',
                        'left': '0mm',
                        'right': '0mm'
                    },
                    prefer_css_page_size=True,  # ✅ 使用CSS中的@page设置
                    display_header_footer=False   # 不显示页眉页脚
                )
                
                browser.close()
            
            # 删除临时文件
            os.unlink(temp_html)
            
            print(f"✅ PDF生成成功，大小: {len(pdf_bytes)} 字节")
        except Exception as pdf_error:
            print(f"❌ PDF生成失败: {pdf_error}")
            import traceback
            traceback.print_exc()
            return Response.error(f'PDF生成失败: {str(pdf_error)}', 500)
        
        # 重新创建文件流用于下载
        download_stream = io.BytesIO(pdf_bytes)
        download_stream.seek(0)
        
        # 生成文件名
        filename = f"健康报告_{report_code}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        print(f"✅ 准备下载文件: {filename}")
        
        # 返回PDF文件（浏览器会自动下载）
        return send_file(
            download_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ 导出PDF异常: {e}")
        print(f"详细错误信息:\n{error_detail}")
        # 返回更详细的错误信息（包含错误类型）
        error_msg = f'导出PDF失败: {type(e).__name__}: {str(e)}'
        return Response.error(error_msg, 500)


@b_report_bp.route('/<int:report_id>/comprehensive', methods=['GET'])
@login_required
def generate_comprehensive_report(current_user, report_id):
    """
    生成综合评估报告HTML（支持7种结节类型）

    新流程：
    1. 获取已发布(published)的报告
    2. 使用报告中保存的AI评估内容
    3. 根据结节类型选择模板并渲染
    4. 返回完整的HTML报告
    """
    try:
        # 1. 获取报告
        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)

        # 2. 检查报告状态（只能渲染已发布的报告）
        if report.status != 'published':
            return Response.error(f'只能导出已发布的报告（当前状态：{report.status}）。请先审核并发布报告。', 400)

        # 3. 获取患者和档案
        patient = BPatient.query.get(report.patient_id)
        record = BHealthRecord.query.get(report.record_id)

        if not patient or not record:
            return Response.error('患者或档案不存在', 404)

        # 4. 获取结节类型
        nodule_type = patient.nodule_type if hasattr(patient, 'nodule_type') and patient.nodule_type else 'breast'
        print(f"\n{'='*60}")
        print(f"📄 渲染 {nodule_type} 类型报告（使用已审核的评估内容）...")
        print(f"{'='*60}")

        # 5. 使用工具模块准备数据
        from utils.report_manager import get_template_path, extract_template_fields

        # 获取模板路径
        template_path = get_template_path(nodule_type)

        # 提取所有模板需要的字段
        template_fields = extract_template_fields(patient, record, nodule_type)

        # 6. 使用报告中保存的AI评估内容（已审核的）
        # 对于三结节和双结节类型，需要特殊处理字段映射
        imaging_warning = report.imaging_risk_warning or report.medical_risk_warning or ''
        if nodule_type == 'triple':
            template_fields.update({
                'imaging_conclusion': report.imaging_conclusion or '',
                'imaging_risk_warning': imaging_warning,
                'risk_warning': imaging_warning,  # 兼容旧变量名
                'comprehensive_conclusion': report.medical_conclusion or report.imaging_conclusion or '',
                'tcm_analysis': '（中医分析接口数据待接入）',
                'risk_score': report.risk_score,
                'risk_level': report.risk_level,
                'report_code': report.report_code,
            })
        elif nodule_type in ['breast_lung', 'breast_thyroid', 'lung_thyroid']:
            # 双结节类型：模板仍用 imaging_risk_warning 渲染“风险提示”
            template_fields.update({
                'imaging_conclusion': report.imaging_conclusion or '',
                'imaging_risk_warning': imaging_warning,
                'risk_warning': imaging_warning,  # 兼容旧变量名
                'comprehensive_conclusion': report.medical_conclusion or report.imaging_conclusion or '',
                'risk_score': report.risk_score,
                'risk_level': report.risk_level,
                'report_code': report.report_code,
            })
        else:
            # 单结节类型（breast/lung/thyroid）：只使用影像学评估（包含综合分析和随访建议）
            template_fields.update({
                'imaging_conclusion': report.imaging_conclusion or '',
                'imaging_risk_warning': report.imaging_risk_warning or '',
                'risk_score': report.risk_score,
                'risk_level': report.risk_level,
                'report_code': report.report_code,
            })

        # 7. 渲染模板
        report_html = render_template(template_path, **template_fields)

        print(f"✅ {nodule_type} 类型报告渲染成功")
        print(f"   报告状态: {report.status}")
        print(f"   审核人: {report.reviewed_by}")
        print(f"   审核时间: {report.reviewed_at}")
        return report_html

    except Exception as e:
        print(f"❌ 生成综合报告失败: {e}")
        import traceback
        traceback.print_exc()
        return Response.error(f'生成综合报告失败: {str(e)}')

