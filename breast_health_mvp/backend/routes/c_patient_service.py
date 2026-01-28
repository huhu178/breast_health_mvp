"""
C端患者服务路由（无需登录）
包含：AI对话、报告查看
"""
from flask import Blueprint, request, jsonify
from models import (
    db, CPatient, CHealthRecord, CReport, CConversation, CMessage
)
from utils.response import Response
from services.llm_service import llm_generator
from routes.llm_helpers_c import normalize_patient_data_for_c
from config import Config
from datetime import datetime
import uuid
import re

# 创建蓝图
c_patient_bp = Blueprint('c_patient', __name__, url_prefix='/api/c')

# LLM服务已在 llm_service.py 模块加载时自动配置，无需重复设置

# ============================================
# 手机号验证
# ============================================

def verify_phone(phone):
    """验证手机号格式"""
    if not phone:
        return False, "手机号不能为空"
    
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return False, "手机号格式错误"
    
    return True, "验证通过"

# ============================================
# AI对话
# ============================================

@c_patient_bp.route('/chat/start', methods=['POST'])
def start_chat():
    """开始AI对话（支持匿名会话：先对话，后登录）"""
    data = request.json or {}
    phone = data.get('phone')  # 可选
    name = data.get('name', '')
    source_channel = data.get('source_channel', 'web')
    campaign_code = data.get('campaign_code')
    entry_url = data.get('entry_url')
    channel = data.get('channel', 'web')

    try:
        now = datetime.utcnow()
        patient = None

        # 如果提供了手机号，验证并创建/查找患者
        if phone:
            is_valid, message = verify_phone(phone)
            if not is_valid:
                return Response.error(message)

            patient = CPatient.query.filter_by(phone=phone).first()

            if not patient:
                patient_code = f"CP{now.strftime('%Y%m%d%H%M%S')}"
                patient = CPatient(
                    patient_code=patient_code,
                    name=name or '访客',
                    phone=phone,
                    source_channel=source_channel,
                    campaign_code=campaign_code,
                    entry_url=entry_url,
                    lead_status='new',
                    status='active',
                    is_contacted=False,
                    first_visit_at=now,
                    last_activity_at=now
                )
                db.session.add(patient)
                db.session.flush()
            else:
                patient.name = name or patient.name
                patient.source_channel = source_channel or patient.source_channel
                patient.campaign_code = campaign_code or patient.campaign_code
                patient.entry_url = entry_url or patient.entry_url
                patient.last_activity_at = now
                if not patient.first_visit_at:
                    patient.first_visit_at = now

        # 创建会话（即使是匿名用户）
        session_id = f"CONV{now.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"
        conversation = CConversation(
            lead_id=patient.id if patient else None,
            session_id=session_id,
            status='active',
            start_time=now,
            last_message_at=now,
            channel=channel,
            collected_data={}
        )
        db.session.add(conversation)
        db.session.commit()

        return Response.success({
            'session_id': session_id,
            'patient_id': patient.id if patient else None,
            'patient_code': patient.patient_code if patient else None,
            'is_anonymous': not bool(patient)
        }, '对话开始成功')

    except Exception as e:
        db.session.rollback()
        return Response.error(f'开始对话失败: {str(e)}')


@c_patient_bp.route('/chat/message', methods=['POST'])
def send_message():
    """发送消息"""
    data = request.json or {}
    session_id = data.get('session_id')
    message_content = data.get('message')
    channel = data.get('channel', 'web')
    extra_data = data.get('extra_data') or {}
    
    if not session_id or not message_content:
        return Response.error('会话ID和消息内容不能为空')
    
    try:
        # 获取对话会话
        conversation = CConversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            return Response.error('会话不存在')
        
        now = datetime.utcnow()

        # 保存用户消息
        user_message = CMessage(
            conversation_id=conversation.id,
            role='user',
            content=message_content,
            intent='user_input',
            channel=channel,
            extra_data=extra_data
        )
        db.session.add(user_message)
        
        # 这里应该调用AI对话服务
        # 暂时返回模拟回复
        ai_response = "感谢您的信息，我正在为您分析..."
        
        # 保存AI回复
        ai_message = CMessage(
            conversation_id=conversation.id,
            role='assistant',
            content=ai_response,
            intent='ai_response',
            channel=channel
        )
        db.session.add(ai_message)
        
        conversation.last_message_at = now
        if conversation.patient:
            conversation.patient.last_activity_at = now

        db.session.commit()
        
        return Response.success({
            'message': ai_response,
            'session_id': session_id
        })
        
    except Exception as e:
        db.session.rollback()
        return Response.error(f'发送消息失败: {str(e)}')


@c_patient_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """获取对话历史"""
    try:
        # 获取对话会话
        conversation = CConversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            return Response.error('会话不存在', 404)
        
        # 获取所有消息
        messages = CMessage.query.filter_by(conversation_id=conversation.id).order_by(CMessage.created_at).all()
        
        message_list = [msg.to_dict() for msg in messages]
        
        return Response.success({
            'session_id': session_id,
            'conversation': conversation.to_dict(),
            'messages': message_list,
            'message_count': len(message_list)
        })
        
    except Exception as e:
        return Response.error(f'获取对话历史失败: {str(e)}')


@c_patient_bp.route('/chat/complete', methods=['POST'])
def complete_chat():
    """完成对话并生成报告"""
    data = request.json or {}
    session_id = data.get('session_id')
    collected_data = data.get('collected_data', {})
    
    if not session_id:
        return Response.error('会话ID不能为空')
    
    try:
        # 获取对话会话
        conversation = CConversation.query.filter_by(session_id=session_id).first()
        if not conversation:
            return Response.error('会话不存在')
        
        # 清理collected_data中的无效Unicode字符（避免代理项错误）
        def clean_unicode(obj):
            """递归清理字典/列表中的无效Unicode字符"""
            if isinstance(obj, dict):
                return {k: clean_unicode(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_unicode(item) for item in obj]
            elif isinstance(obj, str):
                # 移除孤立的Unicode代理项（U+D800 到 U+DFFF）
                return obj.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            else:
                return obj
        
        cleaned_data = clean_unicode(collected_data)
        normalized_data = normalize_patient_data_for_c(cleaned_data)
        
        now = datetime.utcnow()
        conversation.collected_data = normalized_data
        conversation.status = 'completed'
        conversation.end_time = now
        conversation.last_message_at = now
        conversation.summary = normalized_data.get('summary', 'C端AI对话完成')
        
        # 暂时跳过健康档案创建（数据库表结构需要完善）
        # 所有数据已保存在conversation.collected_data中，不影响报告生成
        health_record = None
        print("⏭️ 跳过健康档案创建（数据已保存在对话中）")
        
        # 知识库匹配和决策树处理（已移除，直接使用空值）
        # 注：知识库只有乳腺数据，其他结节类型暂不支持，后续可添加
        matched_knowledge = []  # 空列表，LLM会显示"无相关医学知识"
        decision_result = {}  # 空字典，LLM会使用默认值
        print(f"📚 知识库匹配和决策树: 已移除（使用空值）")
        
        # 生成C端友好报告
        print("🤖 开始生成LLM报告...")
        report_result = llm_generator.generate_patient_friendly_report(
            normalized_data,
            decision_result,
            matched_knowledge
        )
        print(f"✅ 报告生成成功！长度: {len(report_result.get('report_html', ''))} 字符")
        
        # 保存报告
        report_code = f"CRPT{now.strftime('%Y%m%d%H%M%S')}"
        download_token = f"TOKEN{now.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"

        report = CReport(
            patient_id=conversation.patient_id,  # 可以为None（匿名用户）
            record_id=health_record.id if health_record else None,
            conversation_id=conversation.id,
            report_code=report_code,
            report_html=report_result['report_html'],
            report_summary=report_result['report_summary'],
            risk_level=None,  # 不再使用风险评估
            report_type='patient_friendly',
            access_level='c_accessible',
            download_token=download_token,
            status='generated',
            generated_at=now
        )
        db.session.add(report)
        
        if conversation.patient:
            conversation.patient.lead_status = 'reported'
            conversation.patient.last_activity_at = now
        
        db.session.commit()
        
        response_data = {
            'report_code': report_code,
            'download_token': download_token,
        }
        print(f"✅ 返回数据: {response_data}")
        
        return Response.success(response_data, '对话完成，报告生成成功')
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ 报告生成失败:")
        print(error_trace)
        return Response.error(f'完成对话失败: {str(e)}')


# ============================================
# 报告查看
# ============================================

@c_patient_bp.route('/reports/list', methods=['GET'])
def get_reports_list():
    """查询用户的所有报告"""
    phone = request.args.get('phone')
    
    if not phone:
        return Response.error('手机号不能为空')
    
    try:
        # 根据手机号查询患者
        patient = CPatient.query.filter_by(phone=phone).first()
        if not patient:
            return Response.success([], '暂无报告')
        
        # 查询该患者的所有报告
        reports = CReport.query.filter_by(patient_id=patient.id)\
            .order_by(CReport.generated_at.desc())\
            .all()
        
        report_list = []
        for r in reports:
            report_list.append({
                'id': r.id,
                'report_code': r.report_code,
                'risk_level': r.risk_level,
                'report_summary': r.report_summary,
                'generated_at': r.generated_at.strftime('%Y-%m-%d %H:%M:%S') if r.generated_at else None,
                'download_token': r.download_token
            })
        
        return Response.success(report_list, f'查询成功，共{len(report_list)}份报告')
        
    except Exception as e:
        import traceback
        print(f"❌ 查询报告列表失败: {e}")
        traceback.print_exc()
        return Response.error(f'查询失败: {str(e)}')


@c_patient_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report_detail(report_id):
    """获取报告详情"""
    token = request.args.get('token')
    
    if not token:
        return Response.error('缺少访问凭证')
    
    try:
        # 通过report_id和token查询报告
        report = CReport.query.filter_by(
            id=report_id,
            download_token=token
        ).first()
        
        if not report:
            return Response.error('报告不存在或访问凭证无效')
        
        # 更新最后下载时间
        report.last_download_at = datetime.utcnow()
        db.session.commit()
        
        return Response.success({
            'id': report.id,
            'report_code': report.report_code,
            'report_html': report.report_html,
            'report_summary': report.report_summary,
            'risk_level': report.risk_level,
            'report_type': report.report_type,
            'generated_at': report.generated_at.strftime('%Y-%m-%d %H:%M:%S') if report.generated_at else None
        }, '获取成功')
        
    except Exception as e:
        import traceback
        print(f"❌ 获取报告详情失败: {e}")
        traceback.print_exc()
        return Response.error(f'获取失败: {str(e)}')


@c_patient_bp.route('/reports/<int:report_id>/pdf', methods=['GET'])
def download_report_pdf(report_id):
    """下载报告PDF"""
    token = request.args.get('token')
    
    if not token:
        return Response.error('缺少访问凭证')
    
    try:
        # 验证报告和token
        report = CReport.query.filter_by(
            id=report_id,
            download_token=token
        ).first()
        
        if not report:
            return Response.error('报告不存在或访问凭证无效')
        
        # 生成PDF
        from services.pdf_service import pdf_service
        from flask import send_file
        import io
        
        print(f"📥 开始生成PDF: {report.report_code}")
        
        pdf_bytes = pdf_service.generate_report_pdf(
            report.report_html,
            report.report_code
        )
        
        print(f"✅ PDF生成成功: {len(pdf_bytes)} 字节")
        
        # 更新下载时间
        report.last_download_at = datetime.utcnow()
        db.session.commit()
        
        # 返回PDF文件
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'健康报告_{report.report_code}.pdf'
        )
        
    except Exception as e:
        import traceback
        print(f"❌ PDF生成失败: {e}")
        traceback.print_exc()
        return Response.error(f'PDF生成失败: {str(e)}')


@c_patient_bp.route('/reports/verify', methods=['POST'])
def verify_phone_for_report():
    """验证手机号查看报告"""
    data = request.json or {}
    phone = data.get('phone')
    
    # 验证手机号
    is_valid, message = verify_phone(phone)
    if not is_valid:
        return Response.error(message)
    
    try:
        # 查找患者
        patient = CPatient.query.filter_by(phone=phone).first()
        if not patient:
            return Response.error('未找到相关报告')
        
        # 获取患者的报告
        reports = CReport.query.filter_by(patient_id=patient.id).all()
        
        if not reports:
            return Response.error('暂无报告')
        
        # 返回报告列表（不包含详细内容）
        report_list = []
        for report in reports:
            report_list.append({
                'report_id': report.id,
                'report_code': report.report_code,
                'risk_level': report.risk_level,
                'created_at': (report.generated_at or report.created_at).strftime('%Y-%m-%d %H:%M:%S') if (report.generated_at or report.created_at) else None,
                'download_token': report.download_token
            })
        
        return Response.success({
            'patient_name': patient.name,
            'reports': report_list
        })
        
    except Exception as e:
        return Response.error(f'验证失败: {str(e)}')


@c_patient_bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report_by_token(report_id):
    """通过访问token查看报告详情"""
    download_token = request.args.get('token')
    
    if not download_token:
        return Response.error('访问token不能为空')
    
    try:
        # 查找报告
        report = CReport.query.filter_by(id=report_id, download_token=download_token).first()
        if not report:
            return Response.error('报告不存在或访问token无效')
        
        # 获取患者信息
        patient = CPatient.query.get(report.patient_id)
        
        report_data = {
            'report_id': report.id,
            'report_code': report.report_code,
            'risk_level': report.risk_level,
            'report_html': report.report_html,
            'report_summary': report.report_summary,
            'patient_name': patient.name if patient else '未知',
            'created_at': (report.generated_at or report.created_at).strftime('%Y-%m-%d %H:%M:%S') if (report.generated_at or report.created_at) else None
        }
        
        return Response.success(report_data)
        
    except Exception as e:
        return Response.error(f'获取报告失败: {str(e)}')


# ============================================
# 统计信息
# ============================================

@c_patient_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取C端统计信息"""
    try:
        # 患者统计
        total_patients = CPatient.query.count()
        new_patients = CPatient.query.filter_by(is_contacted=False).count()
        contacted_patients = CPatient.query.filter_by(is_contacted=True).count()
        
        # 报告统计
        total_reports = CReport.query.count()
        
        # 对话统计
        total_conversations = CConversation.query.count()
        completed_conversations = CConversation.query.filter_by(status='completed').count()
        
        return Response.success({
            'patients': {
                'total': total_patients,
                'new': new_patients,
                'contacted': contacted_patients
            },
            'reports': {
                'total': total_reports
            },
            'conversations': {
                'total': total_conversations,
                'completed': completed_conversations
            }
        })
        
    except Exception as e:
        return Response.error(f'获取统计信息失败: {str(e)}')
