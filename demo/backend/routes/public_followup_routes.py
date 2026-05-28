"""
患者免登录随访打卡接口
"""
from flask import Blueprint, request

from datetime import datetime

from models import db, BFollowUpTask, BFollowUpCheckin, BFollowUpEvent, BFollowUpMessage
from services.followup_checkin_service import followup_checkin_service
from services.followup_ai_service import followup_ai_service
from utils.response import Response


public_followup_bp = Blueprint('public_followup', __name__, url_prefix='/api/followup')


def _task_public_payload(task):
    node = ((task.task_payload or {}).get('node') if isinstance(task.task_payload, dict) else {}) or {}
    patient = task.patient
    return {
        'task_code': task.task_code,
        'title': task.title,
        'status': task.status,
        'plan_name': task.plan_name,
        'plan_day': task.plan_day,
        'due_at': task.due_at.strftime('%Y-%m-%d %H:%M:%S') if task.due_at else None,
        'patient': {
            'name': patient.name if patient else '',
            'gender': patient.gender if patient else '',
            'age': patient.age if patient else None,
            'phone': patient.phone if patient else '',
            'nodule_type': patient.nodule_type if patient else '',
        },
        'node': {
            'name': node.get('name') or task.title,
            'task_type': node.get('task_type') or 'general',
            'patient_action': node.get('patient_action') or 'reply_text',
            'ai_action': node.get('ai_action') or 'reply',
            'message_template': node.get('message_template') or '',
            'checkin_schema': node.get('checkin_schema') or {},
        }
    }


@public_followup_bp.route('/checkin/<task_code>', methods=['GET'])
def get_checkin_task(task_code):
    task = BFollowUpTask.query.filter_by(task_code=task_code).first()
    if not task:
        return Response.error('随访任务不存在或链接无效', 404)
    return Response.success(_task_public_payload(task))


@public_followup_bp.route('/checkin/<task_code>', methods=['POST'])
def submit_checkin(task_code):
    task = BFollowUpTask.query.filter_by(task_code=task_code).first()
    if not task:
        return Response.error('随访任务不存在或链接无效', 404)

    data = request.json or {}
    node = ((task.task_payload or {}).get('node') if isinstance(task.task_payload, dict) else {}) or {}
    checkin_type = data.get('checkin_type') or node.get('task_type') or 'general'
    image_urls = data.get('image_urls') or []
    content_text = data.get('content_text') or ''
    structured_data = data.get('structured_data') or {}

    ai_result = {}
    abnormal_flag = False
    abnormal_reason = None
    if data.get('analyze', True) and checkin_type == 'diet_checkin':
        ai_result = followup_checkin_service.analyze_diet(content_text, image_urls, structured_data)
        abnormal_flag = bool(ai_result.get('abnormal'))
        abnormal_reason = ai_result.get('summary') if abnormal_flag else None
    elif data.get('analyze', True) and checkin_type == 'symptom_checkin':
        ai = followup_ai_service.analyze_patient_reply(content_text, task)
        ai_result = ai.to_dict()
        abnormal_flag = bool(ai.abnormal or ai.requires_manual_review)
        abnormal_reason = ai.summary if abnormal_flag else None

    status = 'alert' if abnormal_flag else 'analyzed' if ai_result else 'submitted'
    checkin = BFollowUpCheckin(
        task_id=task.id,
        patient_plan_id=(task.task_payload or {}).get('patient_plan_id') if isinstance(task.task_payload, dict) else None,
        patient_id=task.patient_id,
        checkin_type=checkin_type,
        content_text=content_text,
        image_urls=image_urls,
        structured_data=structured_data,
        ai_result=ai_result,
        status=status,
        abnormal_flag=abnormal_flag,
        abnormal_reason=abnormal_reason
    )
    db.session.add(checkin)
    db.session.flush()

    inbound = BFollowUpMessage(
        task_id=task.id,
        patient_id=task.patient_id,
        direction='inbound',
        sender_type='patient',
        channel='public_checkin',
        content_type='text',
        content=content_text or '患者已提交随访打卡',
        ai_intent=ai_result.get('intent') if isinstance(ai_result, dict) else None,
        risk_signal=ai_result.get('risk_signal') if isinstance(ai_result, dict) else None,
        requires_manual_review=abnormal_flag,
        send_status='replied',
        provider_payload={
            'source': 'public_checkin',
            'checkin_id': checkin.id,
            'image_urls': image_urls,
            'structured_data': structured_data,
        },
        received_at=datetime.now(),
    )
    db.session.add(inbound)
    db.session.flush()

    old_status = task.status
    task.status = 'manual_processing' if abnormal_flag else 'replied'
    task.last_message_id = inbound.id
    task.abnormal_flag = abnormal_flag or task.abnormal_flag
    task.abnormal_reason = abnormal_reason or task.abnormal_reason
    task.ai_summary = ai_result.get('summary') or task.ai_summary
    event = BFollowUpEvent(
        task_id=task.id,
        event_type='public_checkin_submitted',
        from_status=old_status,
        to_status=task.status,
        actor_type='patient',
        actor_id='public_checkin',
        summary=abnormal_reason or '患者已提交随访打卡',
        payload={'checkin_type': checkin_type, 'ai_result': ai_result}
    )
    db.session.add(event)
    db.session.commit()
    return Response.success({
        'checkin': checkin.to_dict(),
        'task': _task_public_payload(task),
        'ai_result': ai_result,
    }, '打卡提交成功')
