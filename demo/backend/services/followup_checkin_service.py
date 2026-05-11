"""
随访打卡分析服务

第一版以规则点评为主，为后续接入视觉模型保留结构化输出。
"""
from __future__ import annotations

from typing import Any, Dict, List


DIET_SIGNALS = {
    'high_oil': ['油炸', '炸鸡', '炸串', '薯条', '油条', '肥肉', '火锅', '烧烤'],
    'high_sugar': ['奶茶', '甜饮', '蛋糕', '甜点', '糖水', '可乐', '雪碧'],
    'alcohol': ['啤酒', '白酒', '红酒', '酒'],
    'low_vegetable': ['没菜', '没有蔬菜', '只吃肉', '只吃面', '只吃饭'],
    'protein': ['鸡蛋', '鱼', '虾', '鸡肉', '牛肉', '豆腐', '牛奶'],
    'vegetable': ['青菜', '蔬菜', '西兰花', '菠菜', '番茄', '黄瓜', '生菜'],
}


def _hit_keywords(text: str, words: List[str]) -> List[str]:
    return [word for word in words if word in text]


class FollowupCheckinService:
    def analyze_diet(self, content_text: str = '', image_urls=None, structured_data=None) -> Dict[str, Any]:
        text = (content_text or '') + ' ' + ' '.join(str(x) for x in (image_urls or []))
        structured_data = structured_data or {}
        signals = []
        suggestions = []

        high_oil = _hit_keywords(text, DIET_SIGNALS['high_oil'])
        high_sugar = _hit_keywords(text, DIET_SIGNALS['high_sugar'])
        alcohol = _hit_keywords(text, DIET_SIGNALS['alcohol'])
        low_veg = _hit_keywords(text, DIET_SIGNALS['low_vegetable'])
        protein = _hit_keywords(text, DIET_SIGNALS['protein'])
        vegetable = _hit_keywords(text, DIET_SIGNALS['vegetable'])

        if high_oil:
            signals.append({'type': 'high_oil', 'label': '油脂偏高', 'keywords': high_oil})
            suggestions.append('下一餐建议减少油炸、烧烤、火锅等高油做法，优先选择清蒸、炖煮或少油快炒。')
        if high_sugar:
            signals.append({'type': 'high_sugar', 'label': '糖分偏高', 'keywords': high_sugar})
            suggestions.append('建议减少甜饮和甜点，把饮品换成白水、淡茶或无糖饮品。')
        if alcohol:
            signals.append({'type': 'alcohol', 'label': '出现饮酒', 'keywords': alcohol})
            suggestions.append('随访期建议避免饮酒，尤其是复查前和症状波动期。')
        if low_veg or (text and not vegetable):
            signals.append({'type': 'low_vegetable', 'label': '蔬菜可能不足', 'keywords': low_veg})
            suggestions.append('建议每餐增加一份绿叶菜或深色蔬菜，帮助改善膳食结构。')
        if text and not protein:
            signals.append({'type': 'low_protein', 'label': '优质蛋白可能不足', 'keywords': []})
            suggestions.append('下一餐可补充鸡蛋、鱼虾、瘦肉、豆制品或奶类等优质蛋白。')

        abnormal = any(s['type'] in ('high_oil', 'high_sugar', 'alcohol') for s in signals)
        if not suggestions:
            suggestions.append('这餐结构暂未发现明显异常。建议继续保持主食、蔬菜和优质蛋白的均衡搭配。')

        return {
            'review_type': 'diet_review',
            'signals': signals,
            'abnormal': abnormal,
            'summary': '；'.join(s['label'] for s in signals) if signals else '餐食结构基本可接受',
            'patient_reply': ''.join(suggestions),
            'structured_data': structured_data,
            'image_count': len(image_urls or [])
        }


followup_checkin_service = FollowupCheckinService()
