"""
从数据库导出知识库为JSON格式
用于分析和设计决策树
"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from models import db, KnowledgeItem

app = create_app()

with app.app_context():
    print("📚 正在导出知识库...")
    
    # 查询所有知识
    items = KnowledgeItem.query.order_by(KnowledgeItem.source_type, KnowledgeItem.priority.desc()).all()
    
    # 转换为JSON
    knowledge_data = []
    for item in items:
        knowledge_data.append({
            'id': item.id,
            'title': item.title,
            'content': item.content,
            'priority': item.priority,
            'source_type': item.source_type,
            'risk_level': item.risk_level,
            'age_min': item.age_min,
            'age_max': item.age_max,
            'age_range': item.age_range,
            'birads_min': item.birads_min,
            'birads_max': item.birads_max,
            'course_stage': item.course_stage,
            'tnm_stage': item.tnm_stage,
            'symptoms': item.symptoms,
            'symptom_subtype': item.symptom_subtype,
            'pain_type': item.pain_type,
            'family_history': item.family_history,
            'family_category': item.family_category,
            'family_subcategory': item.family_subcategory,
            'rhythm_type': item.rhythm_type,
            'cycle_phase': item.cycle_phase,
            'phase_timing': item.phase_timing,
            'core_task': item.core_task,
            'sleep_quality': item.sleep_quality,
            'sleep_condition': item.sleep_condition,
            'exam_history_type': item.exam_history_type,
            'exam_subcategory': item.exam_subcategory,
            'nodule_location': item.nodule_location,
            'nodule_size': item.nodule_size,
            'boundary_features': item.boundary_features,
            'internal_echo': item.internal_echo,
            'risk_features': item.risk_features,
            'blood_flow_signal': item.blood_flow_signal,
            'elasticity_score': item.elasticity_score,
            'alert_rule': item.alert_rule,
            'interventions': item.interventions,
            'details': item.details
        })
    
    # 保存到文件
    output_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'knowledge_export.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 成功导出 {len(items)} 条知识")
    print(f"📁 保存位置: {output_file}")
    
    # 统计信息
    print("\n📊 按来源类型统计:")
    stats = {}
    for item in items:
        stats[item.source_type] = stats.get(item.source_type, 0) + 1
    
    for source, count in sorted(stats.items()):
        print(f"  - {source}: {count}条")
    
    # 导出简化版（仅核心字段）
    simplified = []
    for item in items:
        simplified.append({
            'id': item.id,
            'title': item.title,
            'source_type': item.source_type,
            'priority': item.priority,
            'age_range': item.age_range,
            'birads': f"{item.birads_min}-{item.birads_max}" if item.birads_min else None,
            'symptoms': item.symptoms,
            'family_history': item.family_history,
            'risk_level': item.risk_level
        })
    
    simplified_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'knowledge_simplified.json')
    with open(simplified_file, 'w', encoding='utf-8') as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 简化版导出完成: {simplified_file}")



