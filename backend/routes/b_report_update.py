"""
报告审核相关API
包括：更新报告内容、审核通过（发布/标记已审核）
"""
from flask import Blueprint, request, g, render_template
from models import db, BReport, BPatient, BHealthRecord, CReport, CHealthRecord
from utils.decorators import login_required
from utils.response import Response
from datetime import datetime

b_report_update_bp = Blueprint('b_report_update', __name__, url_prefix='/api/b/reports')


@b_report_update_bp.route('/<int:report_id>', methods=['PUT'])
@login_required
def update_report(current_user, report_id):
    """
    更新报告内容（管理师编辑AI生成的评估内容）

    默认只能更新草稿(draft)状态的报告。
    审核模式允许在已发布(published)状态下进行勘误更新（用于“review=true”审核页编辑）。

    ISDoc
    @description
    - type=b_end：更新 BReport（draft/published 审核流）
    - type=c_end：更新 CReport（仅用于勘误/完善；C端不走 draft/published）
    @queryParam type {string} 可选，默认 b_end
    """
    try:
        report_type = request.args.get('type', 'b_end')
        data = request.get_json(silent=True) or {}

        # ========== C端报告（c_end）：允许更新审核用字段 ==========
        if report_type == 'c_end':
            report = CReport.query.get(report_id)
            if not report:
                return Response.error('报告不存在', 404)

            # 允许更新审核用字段（与B端对齐）
            if 'imaging_conclusion' in data:
                report.imaging_conclusion = data['imaging_conclusion']
            if 'imaging_risk_warning' in data:
                report.imaging_risk_warning = data['imaging_risk_warning']

            db.session.commit()
            return Response.success(report.to_dict(), '报告更新成功')

        # ========== B端报告（b_end）：保持原有逻辑 ==========
        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)

        # 只能更新草稿状态的报告（审核模式例外：允许对已发布报告进行勘误）
        review_mode = bool(data.get('review_mode')) or (request.args.get('review') == 'true')
        if report.status != 'draft':
            if not (review_mode and report.status == 'published'):
                return Response.error(f'只能编辑草稿状态的报告（当前状态：{report.status}）', 400)

        # 更新评估内容
        if 'imaging_conclusion' in data:
            report.imaging_conclusion = data['imaging_conclusion']

        if 'imaging_risk_warning' in data:
            report.imaging_risk_warning = data['imaging_risk_warning']

        if 'medical_conclusion' in data:
            report.medical_conclusion = data['medical_conclusion']

        if 'medical_risk_warning' in data:
            report.medical_risk_warning = data['medical_risk_warning']

        if 'risk_score' in data:
            report.risk_score = data['risk_score']

        if 'risk_level' in data:
            report.risk_level = data['risk_level']

        if 'review_notes' in data:
            report.review_notes = data['review_notes']

        # 若已发布报告在审核模式下被勘误更新，为避免导出/预览继续使用旧HTML，清空 report_html 触发下次重渲染
        if review_mode and report.status == 'published':
            report.report_html = None

        # 更新时间戳
        report.updated_at = datetime.utcnow()

        db.session.commit()

        print(f"✅ 报告 {report_id} 更新成功")

        return Response.success(report.to_dict(), '报告更新成功')

    except Exception as e:
        db.session.rollback()
        print(f"❌ 更新报告失败: {e}")
        return Response.error(f'更新报告失败: {str(e)}')


@b_report_update_bp.route('/<int:report_id>/publish', methods=['POST'])
@login_required
def publish_report(current_user, report_id):
    """
    审核通过并发布报告

    默认：将报告状态从 draft 改为 published
    覆盖发布（review_mode）：允许对已发布(published)的报告再次发布，用于勘误后覆盖最终稿

    ISDoc
    @description
    - type=b_end：BReport 走 draft/published 发布
    - type=c_end：CReport 不走发布，改为标记“已审核可发送”（status: generated -> shared）
    @queryParam type {string} 可选，默认 b_end
    """
    try:
        report_type = request.args.get('type', 'b_end')

        data = request.get_json(silent=True) or {}
        # ========== C端报告审核：generated -> shared ==========
        if report_type == 'c_end':
            report = CReport.query.get(report_id)
            if not report:
                return Response.error('报告不存在', 404)

            # C端报告不走 draft/published；用 status 表示审核状态
            # generated：已生成待审核；shared：已审核可发送；downloaded：患者已下载
            if report.status == 'downloaded':
                return Response.error('报告已被患者下载，无法再标记审核', 400)

            # 将舌诊摘要写入报告（仅在审核时写入，符合“先入档案，审核后入报告”）
            try:
                record = CHealthRecord.query.get(report.record_id) if report.record_id else None
                if record and record.tongue_result_summary and report.report_html:
                    placeholder = '（中医分析接口数据待接入）'
                    summary_html = (
                        '<div style="margin-top:8px;line-height:1.6;">'
                        + '<div style="font-weight:700;margin-bottom:6px;">舌诊摘要</div>'
                        + '<div style="white-space:pre-line;">'
                        + (record.tongue_result_summary or '')
                        + '</div></div>'
                    )
                    if placeholder in report.report_html:
                        report.report_html = report.report_html.replace(placeholder, summary_html)
                    else:
                        # 若模板中不存在占位符，则在 </body> 前追加（尽量不破坏原结构）
                        if '</body>' in report.report_html:
                            report.report_html = report.report_html.replace('</body>', f'{summary_html}</body>')
                        else:
                            report.report_html = report.report_html + summary_html
            except Exception as inject_err:
                # 不阻塞审核流程，但记录日志
                print(f"WARNING: 注入舌诊摘要失败: {inject_err}")

            report.status = 'shared'
            db.session.commit()
            return Response.success(report.to_dict(), '报告已审核通过')

        # ========== B端报告发布：原有逻辑 ==========
        report = BReport.query.get(report_id)
        if not report:
            return Response.error('报告不存在', 404)

        # 审核模式：允许覆盖发布已发布报告
        review_mode = bool(data.get('review_mode')) or (request.args.get('review') == 'true')

        # 允许的发布状态：
        # - draft：首次发布
        # - published + review_mode：覆盖发布
        if report.status != 'draft':
            if not (review_mode and report.status == 'published'):
                return Response.error(f'只能发布草稿状态的报告（当前状态：{report.status}）', 400)

        # 更新状态
        # draft -> published；覆盖发布则保持 published
        if report.status == 'draft':
            report.status = 'published'

        # 记录审核信息
        report.reviewed_by = g.user_id
        report.reviewed_at = datetime.utcnow()

        if 'review_notes' in data:
            report.review_notes = data['review_notes']

        report.updated_at = datetime.utcnow()

        # 覆盖发布：确保重新生成HTML（即使之前已有 report_html）
        if review_mode and report.status == 'published':
            report.report_html = None

        # 发布后自动生成HTML报告
        from utils.report_manager import get_template_path, extract_template_fields
        
        patient = BPatient.query.get(report.patient_id)
        record = BHealthRecord.query.get(report.record_id)
        
        if patient and record:
            # 获取结节类型
            nodule_type = patient.nodule_type if hasattr(patient, 'nodule_type') and patient.nodule_type else 'breast'
            
            # 获取模板路径
            try:
                template_path = get_template_path(nodule_type)
                
                # 提取所有模板需要的字段
                template_fields = extract_template_fields(patient, record, nodule_type)
                
                # 使用报告中保存的AI评估内容（已审核的）
                # 说明：所有报告模板统一使用 imaging_risk_warning 变量名渲染“风险提示”。
                # 为兼容旧模板/旧逻辑，同时保留 risk_warning 变量名。
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
                    template_fields.update({
                        'imaging_conclusion': report.imaging_conclusion or '',
                        'imaging_risk_warning': report.imaging_risk_warning or '',
                        'medical_conclusion': report.medical_conclusion,
                        'medical_risk_warning': report.medical_risk_warning,
                        'risk_score': report.risk_score,
                        'risk_level': report.risk_level,
                        'report_code': report.report_code,
                    })
                
                # 渲染模板并保存到report_html
                report_html = render_template(template_path, **template_fields)
                report.report_html = report_html
                
                print(f"✅ 报告HTML已生成并保存（长度: {len(report.report_html)} 字符）")
            except Exception as html_error:
                print(f"⚠️ 生成报告HTML失败: {html_error}")
                import traceback
                traceback.print_exc()
                # 即使HTML生成失败，也继续发布流程

        db.session.commit()

        if review_mode:
            print(f"✅ 报告 {report_id} 已覆盖发布（review_mode）")
        else:
            print(f"✅ 报告 {report_id} 已审核通过并发布")
        print(f"   审核人: {g.user_id}")
        print(f"   审核时间: {report.reviewed_at}")

        return Response.success(report.to_dict(), '报告已审核通过并发布')

    except Exception as e:
        db.session.rollback()
        print(f"❌ 发布报告失败: {e}")
        return Response.error(f'发布报告失败: {str(e)}')
