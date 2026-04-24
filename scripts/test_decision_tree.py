"""
测试决策树功能
"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from models import db, KnowledgeItem
from services.decision_tree import decision_tree

app = create_app()

with app.app_context():
    print("🌳 测试决策树引擎")
    print("=" * 80)
    
    # 测试案例：35岁女性，BI-RADS 4级，有家族史
    patient_data = {
        "age": 35,
        "birads_level": 4,
        "family_history": "有",
        "symptoms": "疼痛",
        "pain_type": "周期性",
        "nodule_size": "1.2cm",
        "boundary_features": "清晰",
        "sleep_quality": "差",
        "exercise_frequency": "很少",
        "rhythm_type": "月经周期相关"
    }
    
    print("\n📋 测试案例：")
    print(json.dumps(patient_data, ensure_ascii=False, indent=2))
    
    # 步骤1：匹配知识库
    print("\n\n第1步：知识库智能匹配...")
    matched_knowledge = KnowledgeItem.query.filter(
        (KnowledgeItem.age_min.is_(None) | (KnowledgeItem.age_min <= 35)) &
        (KnowledgeItem.age_max.is_(None) | (KnowledgeItem.age_max >= 35))
    ).all()
    
    print(f"✅ 匹配到 {len(matched_knowledge)} 条知识")
    
    # 步骤2：决策树处理
    print("\n\n第2步：决策树处理...")
    result = decision_tree.process(patient_data, matched_knowledge)
    
    # 输出结果
    print("\n" + "=" * 80)
    print("📊 决策树处理结果")
    print("=" * 80)
    
    print("\n【决策路径】")
    for i, step in enumerate(result['decision_path'], 1):
        print(f"  {i}. {step}")
    
    print("\n【风险评估】")
    risk = result['risk_assessment']
    print(f"  风险等级: {risk['risk_level']} （评分: {risk['risk_score']}/100）")
    print(f"  立即行动:")
    for action in risk['immediate_actions']:
        print(f"    - {action}")
    print(f"  关联知识: {risk['knowledge_count']}条")
    
    if result.get('imaging_findings'):
        print("\n【影像学发现】")
        imaging = result['imaging_findings']
        print(f"  分类: {imaging['category']}")
        print(f"  紧急度: {imaging['urgency']}")
        print(f"  建议:")
        for rec in imaging['recommendations']:
            print(f"    - {rec}")
    
    if result.get('symptom_management'):
        print("\n【症状管理】")
        symptom = result['symptom_management']
        print(f"  症状类型: {', '.join(symptom['symptom_types'])}")
        print(f"  建议:")
        for rec in symptom['recommendations']:
            print(f"    - {rec}")
    
    if result.get('rhythm_regulation'):
        print("\n【生物节律调节】")
        rhythm = result['rhythm_regulation']
        print(f"  节律类型: {rhythm.get('rhythm_type', '未记录')}")
        print(f"  睡眠质量: {rhythm.get('sleep_quality', '未记录')}")
        print(f"  建议:")
        for rec in rhythm['recommendations']:
            print(f"    - {rec}")
    
    if result.get('lifestyle_recommendations'):
        print("\n【生活方式干预】")
        lifestyle = result['lifestyle_recommendations']
        print(f"  运动水平: {lifestyle.get('exercise_level', '未记录')}")
        print(f"  建议:")
        for rec in lifestyle['recommendations'][:5]:  # 只显示前5条
            print(f"    - {rec[:80]}...")
    
    if result.get('family_management'):
        print("\n【家族史管理】")
        family = result['family_management']
        print(f"  有家族史: {family.get('has_family_history', False)}")
        print(f"  建议:")
        for rec in family['recommendations']:
            print(f"    - {rec}")
    
    if result.get('follow_up_plan'):
        print("\n【随访计划】")
        follow_up = result['follow_up_plan']
        print(f"  计划类型: {follow_up['plan_type']}")
        print(f"  随访频率: {follow_up['frequency']}")
        print(f"  持续时间: {follow_up['duration']}")
        print(f"  检查方式: {', '.join(follow_up['modalities'])}")
        if 'escalation' in follow_up:
            print(f"  升级条件: {follow_up['escalation']}")
    
    print(f"\n【知识引用】")
    print(f"  共引用 {len(result['knowledge_references'])} 条知识")
    print(f"  前5条:")
    for i, ref in enumerate(result['knowledge_references'][:5], 1):
        print(f"    {i}. [{ref['id']}] {ref['title']} ({ref['source_type']}, 优先级{ref['priority']})")
    
    print("\n" + "=" * 80)
    print("✅ 决策树测试完成！")
    print("=" * 80)
    
    # 保存结果到文件
    output_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'decision_tree_test_result.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        # 转换为可序列化的格式
        serializable_result = {
            key: value for key, value in result.items()
            if key not in ['knowledge_references']  # 跳过复杂对象
        }
        serializable_result['knowledge_references'] = [
            {k: v for k, v in ref.items()}
            for ref in result['knowledge_references']
        ]
        json.dump(serializable_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细结果已保存: {output_file}")



