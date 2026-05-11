"""
AI随访服务

当前实现以稳定规则为主：生成可发送话术、识别异常信号、判断是否转人工。
后续可以在 build_outbound_message / analyze_patient_reply 内接入 LLM，但不应绕过异常
信号规则和人工交接策略。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional


HIGH_RISK_KEYWORDS = (
    '咳血', '血丝', '胸痛', '呼吸困难', '气促', '发热不退', '持续发热',
    '疼痛加重', '明显变大', '吞咽困难', '声音嘶哑', '乳头溢血', '皮肤凹陷',
    '红肿热痛', '头晕', '晕厥'
)

MEDIUM_RISK_KEYWORDS = (
    '胸闷', '咳嗽加重', '睡不好', '焦虑', '担心', '疼', '不舒服',
    '乏力', '咽部不适', '异物感', '复查推迟'
)


@dataclass
class FollowupAIResult:
    content: str
    summary: str
    intent: str
    risk_signal: str = ''
    abnormal: bool = False
    requires_manual_review: bool = False
    handoff_to: str = ''

    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'summary': self.summary,
            'intent': self.intent,
            'risk_signal': self.risk_signal,
            'abnormal': self.abnormal,
            'requires_manual_review': self.requires_manual_review,
            'handoff_to': self.handoff_to
        }


def _normalize_risk(risk_level: Optional[str]) -> str:
    text = (risk_level or '').strip().lower()
    if text in ('high', '高', '高危', '高风险'):
        return 'high'
    if text in ('mid', 'medium', '中', '中危', '中风险'):
        return 'mid'
    if text in ('low', '低', '低危', '低风险'):
        return 'low'
    return 'unknown'


def _risk_label(risk: str) -> str:
    return {'high': '高风险', 'mid': '中风险', 'low': '低风险'}.get(risk, '待评估')


def _nodule_label(nodule_type: Optional[str]) -> str:
    mapping = {
        'breast': '乳腺结节',
        'lung': '肺部结节',
        'thyroid': '甲状腺结节',
        'breast_lung': '乳腺合并肺部结节',
        'breast_thyroid': '乳腺合并甲状腺结节',
        'lung_thyroid': '肺部合并甲状腺结节',
        'thyroid_lung': '甲状腺合并肺部结节',
        'triple': '三合并结节',
        'thyroid_breast_lung': '甲状腺、乳腺合并肺部结节',
    }
    return mapping.get(nodule_type or '', nodule_type or '结节')


def _find_first_keyword(text: str, keywords: Iterable[str]) -> str:
    for keyword in keywords:
        if keyword in text:
            return keyword
    return ''


class FollowupAIService:
    """AI随访话术与预警判定"""

    def build_outbound_message(self, task, patient=None, report=None, plan_rows=None) -> FollowupAIResult:
        patient = patient or getattr(task, 'patient', None)
        report = report or getattr(task, 'report', None)
        name = getattr(patient, 'name', '') or '您好'
        payload = getattr(task, 'task_payload', None) if isinstance(getattr(task, 'task_payload', None), dict) else {}
        node = payload.get('node') if isinstance(payload.get('node'), dict) else {}
        risk = _normalize_risk(getattr(task, 'risk_level', None) or getattr(report, 'risk_level', None))
        nodule = _nodule_label(getattr(task, 'nodule_type', None) or getattr(patient, 'nodule_type', None))
        plan_day = getattr(task, 'plan_day', None) or 1

        node_template = str(node.get('message_template') or '').strip()
        if node_template:
            content = node_template
            if name and not content.startswith(str(name)):
                content = f'{name}，{content}'
            return FollowupAIResult(
                content=content,
                summary=f"生成第{plan_day}天随访话术：{node.get('name') or getattr(task, 'title', '') or '计划节点'}",
                intent=node.get('task_type') or 'followup_node'
            )

        review_hint = ''
        if risk == 'high':
            review_hint = '请重点留意咳血、胸痛、呼吸困难、疼痛明显加重、肿块快速增大等变化。'
        elif risk == 'mid':
            review_hint = '请留意症状变化，并按计划完成复查或资料补充。'
        else:
            review_hint = '请保持规律作息，按计划复查即可。'

        report_hint = ''
        if report and getattr(report, 'reviewed_at', None):
            report_hint = '您的报告已完成审核，'
        elif report:
            report_hint = '您的健康管理建议已生成，'

        content = (
            f'{name}，{report_hint}这是第 {plan_day} 天随访提醒。'
            f'当前管理类型：{nodule}，风险分层：{_risk_label(risk)}。'
            f'{review_hint}'
            '如有新的不适、复查结果或用药问题，请直接回复本消息；'
            '如出现明显异常症状，请及时就医并联系医生。'
        )

        if plan_rows:
            summaries = [
                str(row.get('summary', '')).strip()
                for row in plan_rows
                if isinstance(row, dict) and row.get('summary')
            ][:2]
            if summaries:
                content += ' 今日建议：' + '；'.join(summaries) + '。'

        return FollowupAIResult(
            content=content,
            summary=f'生成第{plan_day}天随访话术：{_risk_label(risk)}，{nodule}',
            intent='followup_reminder'
        )

    def analyze_patient_reply(self, text: str, task=None) -> FollowupAIResult:
        raw = (text or '').strip()
        compact = re.sub(r'\s+', '', raw)
        if not compact:
            return FollowupAIResult(
                content='已收到空回复，建议人工确认患者情况。',
                summary='患者回复为空，需人工确认',
                intent='empty_reply',
                requires_manual_review=True,
                handoff_to='health_manager'
            )

        high_keyword = _find_first_keyword(compact, HIGH_RISK_KEYWORDS)
        if high_keyword:
            return FollowupAIResult(
                content=(
                    '已收到您的反馈。您提到的情况需要医生进一步判断，'
                    '系统已为您转人工/医生处理。若症状明显或持续加重，请及时就医。'
                ),
                summary=f'患者回复触发高优先级预警：{high_keyword}',
                intent='abnormal_alert',
                risk_signal=high_keyword,
                abnormal=True,
                requires_manual_review=True,
                handoff_to='doctor'
            )

        medium_keyword = _find_first_keyword(compact, MEDIUM_RISK_KEYWORDS)
        if medium_keyword:
            return FollowupAIResult(
                content=(
                    '已记录您的反馈。建议继续观察变化并按计划复查；'
                    '如症状持续或加重，健康管理师会协助您进一步处理。'
                ),
                summary=f'患者回复包含需关注信号：{medium_keyword}',
                intent='symptom_followup',
                risk_signal=medium_keyword,
                requires_manual_review=True,
                handoff_to='health_manager'
            )

        return FollowupAIResult(
            content='已收到您的反馈，当前未识别到明显异常信号。请继续按计划复查，并保持规律作息。',
            summary='患者回复未触发异常预警',
            intent='normal_reply'
        )


followup_ai_service = FollowupAIService()
