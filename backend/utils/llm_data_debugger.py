"""
LLM数据调试工具
用于查看完整传递给LLM的数据
"""
import json
from typing import Dict, Any

def print_full_llm_data(patient_data: Dict, prompt_vars: Dict, nodule_type: str, prompt_type: str = 'imaging'):
    """
    打印完整传递给LLM的数据
    
    Args:
        patient_data: 原始患者数据
        prompt_vars: 处理后的提示词变量
        nodule_type: 结节类型
        prompt_type: 提示词类型（imaging/western_medical）
    """
    print("\n" + "="*80)
    print("📊 LLM数据完整调试信息")
    print("="*80)
    
    # 1. 原始patient_data
    print("\n【1】原始patient_data（从数据库提取）")
    print("-" * 80)
    print(json.dumps(patient_data, ensure_ascii=False, indent=2, default=str))
    
    # 2. 处理后的prompt_vars
    print("\n【2】处理后的prompt_vars（传递给提示词模板）")
    print("-" * 80)
    print(json.dumps(prompt_vars, ensure_ascii=False, indent=2, default=str))
    
    # 3. 数据完整性检查
    print("\n【3】数据完整性检查")
    print("-" * 80)
    
    # 检查基本信息
    basic_fields = ['age', 'gender', 'height', 'weight']
    print("\n✓ 基本信息:")
    for field in basic_fields:
        value = patient_data.get(field)
        status = "✅" if value is not None and value != '' else "❌"
        print(f"  {status} {field}: {value}")
    
    # 检查乳腺相关字段
    if nodule_type == 'triple' or 'breast' in nodule_type:
        print("\n✓ 乳腺相关字段:")
        breast_fields = [
            'birads_level', 'nodule_size', 'nodule_location', 
            'boundary_features', 'internal_echo', 'blood_flow_signal',
            'elasticity_score', 'symptoms', 'breast_discovery_date',
            'breast_hyperplasia_history', 'breast_fibroadenoma_history',
            'breast_cyst_history', 'breast_inflammation_history',
            'breast_cancer_history', 'hereditary_breast_history'
        ]
        for field in breast_fields:
            value = patient_data.get(field)
            status = "✅" if value is not None and value != '' else "❌"
            print(f"  {status} {field}: {value}")
    
    # 检查肺部相关字段
    if nodule_type == 'triple' or 'lung' in nodule_type:
        print("\n✓ 肺部相关字段:")
        lung_fields = [
            'lung_rads_level', 'lung_nodule_size', 'lung_nodule_location',
            'lung_boundary_features', 'lung_internal_echo', 'lung_blood_flow_signal',
            'lung_nodule_count', 'lung_calcification', 'lung_symptoms',
            'lung_discovery_date', 'pneumonia_history', 'tb_history',
            'copd_history', 'fibrosis_history', 'lung_cancer_history',
            'hereditary_lung_history'
        ]
        for field in lung_fields:
            value = patient_data.get(field)
            status = "✅" if value is not None and value != '' else "❌"
            print(f"  {status} {field}: {value}")
    
    # 检查甲状腺相关字段
    if nodule_type == 'triple' or 'thyroid' in nodule_type:
        print("\n✓ 甲状腺相关字段:")
        thyroid_fields = [
            'tirads_level', 'thyroid_nodule_size', 'thyroid_nodule_location',
            'thyroid_boundary_features', 'thyroid_internal_echo',
            'thyroid_blood_flow_signal', 'thyroid_nodule_count',
            'thyroid_calcification', 'thyroid_symptoms', 'thyroid_discovery_date',
            'hyperthyroidism_history', 'hypothyroidism_history', 'hashimoto_history',
            'subacute_thyroiditis_history', 'thyroid_cancer_history',
            'hereditary_thyroid_history'
        ]
        for field in thyroid_fields:
            value = patient_data.get(field)
            status = "✅" if value is not None and value != '' else "❌"
            print(f"  {status} {field}: {value}")
    
    # 检查通用风险因素
    print("\n✓ 通用风险因素:")
    risk_fields = [
        'diabetes_history', 'radiation_exposure_history',
        'autoimmune_disease_history', 'medication_history',
        'tumor_marker_test', 'smoking_risk_level',
        'diabetes_control_level', 'dust_exposure_history'
    ]
    for field in risk_fields:
        value = patient_data.get(field)
        status = "✅" if value is not None and value != '' else "❌"
        print(f"  {status} {field}: {value}")
    
    # 4. 缺失字段统计
    print("\n【4】缺失字段统计")
    print("-" * 80)
    missing_fields = []
    for key, value in patient_data.items():
        if value is None or value == '' or value == []:
            missing_fields.append(key)
    
    if missing_fields:
        print(f"❌ 发现 {len(missing_fields)} 个缺失字段:")
        for field in missing_fields[:20]:  # 只显示前20个
            print(f"  - {field}")
        if len(missing_fields) > 20:
            print(f"  ... 还有 {len(missing_fields) - 20} 个字段")
    else:
        print("✅ 所有字段都有值")
    
    # 5. prompt_vars与patient_data的映射关系
    print("\n【5】prompt_vars字段映射检查")
    print("-" * 80)
    print("检查prompt_vars中的字段是否都来自patient_data:")
    unmapped_fields = []
    for key in prompt_vars.keys():
        if key not in ['knowledge_items']:  # 知识库是特殊处理的
            # 检查是否在patient_data中
            if key not in patient_data:
                # 检查是否有对应的字段（如lung_internal_density对应lung_internal_echo）
                if key == 'lung_internal_density' and 'lung_internal_echo' in patient_data:
                    print(f"  ✅ {key} -> lung_internal_echo (字段名映射)")
                else:
                    unmapped_fields.append(key)
                    print(f"  ⚠️ {key} - 在patient_data中未找到")
            else:
                print(f"  ✅ {key}")
    
    if unmapped_fields:
        print(f"\n⚠️ 发现 {len(unmapped_fields)} 个未映射的字段（可能是默认值）")
    
    print("\n" + "="*80)
    print("调试信息输出完成")
    print("="*80 + "\n")


def save_llm_prompt_to_file(prompt: str, filename: str = None):
    """
    保存完整的prompt到文件（用于调试）
    
    Args:
        prompt: 完整的prompt字符串
        filename: 文件名（可选）
    """
    import os
    from datetime import datetime
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"llm_prompt_debug_{timestamp}.txt"
    
    debug_dir = os.path.join(os.path.dirname(__file__), '..', 'debug_prompts')
    os.makedirs(debug_dir, exist_ok=True)
    
    filepath = os.path.join(debug_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("LLM Prompt 完整内容\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        f.write(prompt)
    
    print(f"📄 Prompt已保存到: {filepath}")
    return filepath




