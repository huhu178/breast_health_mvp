"""
随访任务调度服务

MVP 先提供 run_once：扫描到期任务，生成 AI 话术，调用企业微信服务发送/记录。
后续可由 APScheduler/Celery 定时调用。
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from models import db, BFollowUpTask, BFollowUpMessage, BFollowUpEvent
from services.followup_ai_service import followup_ai_service
from services.wecom_service import wecom_service


class FollowupSchedulerService:
    def _event(self, task, event_type, summary='', from_status=None, to_status=None, payload=None):
        event = BFollowUpEvent(
            task_id=task.id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            actor_type='scheduler',
            actor_id='system',
            summary=summary,
            payload=payload or {}
        )
        db.session.add(event)
        return event

    def run_once(self, limit: int = 50) -> Dict[str, Any]:
        now = datetime.now()
        tasks = BFollowUpTask.query.filter(
            BFollowUpTask.status.in_(['pending', 'scheduled']),
            BFollowUpTask.scheduled_send_at <= now,
        ).order_by(BFollowUpTask.scheduled_send_at.asc()).limit(limit).all()

        results: List[Dict[str, Any]] = []
        for task in tasks:
            old_status = task.status
            try:
                ai_result = followup_ai_service.build_outbound_message(task)
                checkin_url = f"/followup-checkin/{task.task_code}"
                content = f"{ai_result.content}\n\n打卡入口：{checkin_url}"
                send_result = wecom_service.send_text(task.channel_recipient, content)
                status = send_result.get('status') or ('sent' if send_result.get('ok') else 'failed')
                message = BFollowUpMessage(
                    task_id=task.id,
                    patient_id=task.patient_id,
                    direction='outbound',
                    sender_type='ai',
                    channel=task.channel,
                    content_type='text',
                    content=content,
                    ai_intent=ai_result.intent,
                    send_status=status,
                    provider_message_id=send_result.get('provider_message_id'),
                    provider_payload=send_result.get('payload'),
                    provider_response=send_result.get('response') or send_result,
                    error_message='' if send_result.get('ok') else send_result.get('reason') or str(send_result),
                    sent_at=now if send_result.get('ok') else None,
                )
                db.session.add(message)
                db.session.flush()

                task.last_message_id = message.id
                task.ai_summary = ai_result.summary
                task.status = 'sent' if send_result.get('ok') else 'failed'
                task.updated_at = now
                payload = {
                    'message_id': message.id,
                    'checkin_url': checkin_url,
                    'send_result': send_result,
                }
                self._event(
                    task,
                    'scheduler_message_sent' if send_result.get('ok') else 'scheduler_message_failed',
                    ai_result.summary,
                    from_status=old_status,
                    to_status=task.status,
                    payload=payload
                )
                results.append({'task_id': task.id, 'status': task.status, 'message_id': message.id})
            except Exception as e:
                task.status = 'failed'
                task.updated_at = now
                task.abnormal_reason = str(e)
                self._event(
                    task,
                    'scheduler_error',
                    str(e),
                    from_status=old_status,
                    to_status='failed',
                    payload={'error': str(e)}
                )
                results.append({'task_id': task.id, 'status': 'failed', 'error': str(e)})

        db.session.commit()
        return {'processed': len(results), 'results': results}


followup_scheduler_service = FollowupSchedulerService()
