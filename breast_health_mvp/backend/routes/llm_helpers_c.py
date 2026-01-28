"""C端专用的知识库匹配与数据规范化工具"""

from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Tuple

from routes.llm_helpers import match_knowledge as base_match_knowledge


_FAMILY_HISTORY_MAP = {
    '无': '无家族史',
    '无家族史': '无家族史',
    '否': '无家族史',
    'none': '无家族史',
    '一级亲属': '高危家族史',
    '一級親屬': '高危家族史',
    '一级亲属（母亲/姐妹）': '高危家族史',
    '二级亲属': '中危家族史',
    '三级以上亲属': '低危家族史',
}


def _strip_invalid_unicode(value: Any) -> Any:
    """移除字符串中的孤立代理项，避免写入数据库时报错"""
    if isinstance(value, str):
        return value.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore').strip()
    if isinstance(value, list):
        return [_strip_invalid_unicode(item) for item in value]
    if isinstance(value, dict):
        return {k: _strip_invalid_unicode(v) for k, v in value.items()}
    return value


def _ensure_int(value: Any) -> Any:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        match = re.search(r'(\d+)', value)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return value
    return value


def _normalize_symptoms(symptoms: Any) -> List[str]:
    if not symptoms:
        return []
    if isinstance(symptoms, list):
        return [item for item in (_strip_invalid_unicode(s) for s in symptoms) if item]
    if isinstance(symptoms, str):
        parts = re.split(r'[、，,\s]+', symptoms)
        return [part for part in (_strip_invalid_unicode(p) for p in parts) if part]
    return []


def normalize_patient_data_for_c(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """将C端收集的字段转换为B端/知识库通用格式"""
    data = _strip_invalid_unicode(copy.deepcopy(raw_data or {}))

    if 'age' in data:
        data['age'] = _ensure_int(data['age'])

    if 'birads_level' in data:
        data['birads_level'] = _ensure_int(data['birads_level'])

    if 'family_history' in data and data['family_history']:
        key = str(data['family_history']).strip().lower()
        # 先按原值查找，再按小写查找
        mapped = _FAMILY_HISTORY_MAP.get(data['family_history']) or _FAMILY_HISTORY_MAP.get(key)
        if mapped:
            data['family_history'] = mapped

    if 'symptoms' in data:
        data['symptoms'] = _normalize_symptoms(data['symptoms'])

    # pain_type 等子字段若不存在，保持原值；若出现 emoji 已去除

    return data


def match_knowledge_for_c(patient_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Any]]:
    """对C端数据进行规范化后复用B端知识库匹配逻辑"""
    normalized = normalize_patient_data_for_c(patient_data)
    matched = base_match_knowledge(normalized)
    return normalized, matched





