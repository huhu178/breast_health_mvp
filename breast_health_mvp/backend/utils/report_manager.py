"""
报告模板管理器
统一管理7种结节类型的模板选择和字段提取
"""

from datetime import datetime

# ==================== 模板映射配置 ====================

TEMPLATE_MAPPING = {
    'breast': 'reports/breast_report.html',
    'lung': 'reports/lung_report.html',
    'thyroid': 'reports/thyroid_report.html',
    'breast_lung': 'reports/breast_lung_report.html',
    'breast_thyroid': 'reports/breast_thyroid_report.html',
    'lung_thyroid': 'reports/lung_thyroid_report.html',
    'triple': 'reports/triple_report.html',
}


def get_template_path(nodule_type: str) -> str:
    """
    根据结节类型获取对应的模板路径

    Args:
        nodule_type: 结节类型 (breast/lung/thyroid/breast_lung/breast_thyroid/lung_thyroid/triple)

    Returns:
        模板路径

    Raises:
        ValueError: 不支持的结节类型
    """
    template = TEMPLATE_MAPPING.get(nodule_type)
    if not template:
        raise ValueError(f'不支持的结节类型: {nodule_type}，支持的类型: {list(TEMPLATE_MAPPING.keys())}')
    return template


# ==================== 字段提取函数 ====================

def extract_common_fields(patient, record) -> dict:
    """提取所有报告通用的字段"""
    return {
        # 基本信息
        'patient_name': patient.name,
        'patient_gender': patient.gender if hasattr(patient, 'gender') else '女',
        'patient_age': record.age,
        'height': record.height if hasattr(record, 'height') else None,
        'weight': record.weight if hasattr(record, 'weight') else None,
        'phone': record.phone if hasattr(record, 'phone') else (patient.phone if hasattr(patient, 'phone') else None),
        'diabetes_history': record.diabetes_history if hasattr(record, 'diabetes_history') else '无',
        'gaofang_address': record.gaofang_address if hasattr(record, 'gaofang_address') else None,

        # 报告信息
        'report_date': datetime.now().strftime('%Y年%m月%d日'),
    }


def extract_breast_fields(record) -> dict:
    """提取乳腺结节相关字段（兼容BHealthRecord和NoduleHealthRecord两种模型）"""
    # 判断是多结节系统还是单结节系统
    # 多结节系统有breast_nodule_size字段，单结节系统有nodule_size字段
    is_nodule_system = hasattr(record, 'breast_nodule_size')
    
    return {
        # 影像学特征
        'birads_level': record.birads_level if hasattr(record, 'birads_level') else None,
        # 兼容两种字段名：多结节系统用breast_nodule_size，单结节系统用nodule_size
        'nodule_size': (
            record.breast_nodule_size if is_nodule_system and hasattr(record, 'breast_nodule_size') and record.breast_nodule_size is not None
            else (record.nodule_size if hasattr(record, 'nodule_size') and record.nodule_size is not None else None)
        ),
        # 注意：以下字段已从前端表单移除，不再提取：
        # - nodule_location (结节位置)
        # - boundary_features (边界特征)
        # - internal_echo (内部回声)
        # - blood_flow_signal (血流信号)
        # - elasticity_score (弹性评分)
        'symptoms': (
            record.breast_symptoms if is_nodule_system and hasattr(record, 'breast_symptoms') and record.breast_symptoms else
            (record.symptoms if hasattr(record, 'symptoms') and record.symptoms else None)
        ),
        'symptoms_other': record.breast_symptoms_other if hasattr(record, 'breast_symptoms_other') and record.breast_symptoms_other else (
            record.symptoms_other if hasattr(record, 'symptoms_other') and record.symptoms_other else ''
        ),
        'breast_symptoms_other': record.breast_symptoms_other if hasattr(record, 'breast_symptoms_other') and record.breast_symptoms_other else '',
        
        # 结节数量信息
        'nodule_quantity': record.nodule_quantity if hasattr(record, 'nodule_quantity') and record.nodule_quantity else None,
        'nodule_count': record.nodule_count if hasattr(record, 'nodule_count') and record.nodule_count is not None else None,
        # 合并类/三结节模板 & 提示词专用：避免与肺/甲状腺的 nodule_quantity 键冲突
        'nodule_quantity_breast': record.nodule_quantity if hasattr(record, 'nodule_quantity') and record.nodule_quantity else None,
        'nodule_count_breast': record.nodule_count if hasattr(record, 'nodule_count') and record.nodule_count is not None else None,

        # 病史（只提取前端表单实际使用的字段）
        'breast_disease_history': (
            record.breast_disease_history 
            if hasattr(record, 'breast_disease_history') and record.breast_disease_history and record.breast_disease_history.strip() 
            else '无'
        ),
        'breast_disease_history_other': record.breast_disease_history_other if hasattr(record, 'breast_disease_history_other') and record.breast_disease_history_other else '',
        # 家族史/用药史：多器官优先读乳腺专属字段，兼容旧字段
        'family_history': (
            record.breast_family_history
            if hasattr(record, 'breast_family_history') and record.breast_family_history and str(record.breast_family_history).strip()
            else (record.family_history if hasattr(record, 'family_history') and record.family_history and str(record.family_history).strip() else '无')
        ),
        'family_history_other': (
            record.breast_family_history_other
            if hasattr(record, 'breast_family_history_other') and record.breast_family_history_other
            else (record.family_history_other if hasattr(record, 'family_history_other') and record.family_history_other else '')
        ),
        'medication_history': (
            record.breast_medication_history
            if hasattr(record, 'breast_medication_history') and record.breast_medication_history and str(record.breast_medication_history).strip()
            else (record.medication_history if hasattr(record, 'medication_history') and record.medication_history and str(record.medication_history).strip() else '无')
        ),
        'medication_other': (
            record.breast_medication_other
            if hasattr(record, 'breast_medication_other') and record.breast_medication_other
            else (record.medication_other if hasattr(record, 'medication_other') and record.medication_other else '')
        ),
        # 显式输出乳腺专属字段（供合并类提示词/模板使用）
        'breast_family_history': record.breast_family_history if hasattr(record, 'breast_family_history') and record.breast_family_history else '',
        'breast_family_history_other': record.breast_family_history_other if hasattr(record, 'breast_family_history_other') and record.breast_family_history_other else '',
        'breast_medication_history': record.breast_medication_history if hasattr(record, 'breast_medication_history') and record.breast_medication_history else '',
        'breast_medication_other': record.breast_medication_other if hasattr(record, 'breast_medication_other') and record.breast_medication_other else '',
        
        # 注意：diabetes_history 已经在 extract_common_fields 中提取，这里不需要重复

        # 乳腺结节发现时间
        'breast_discovery_date': record.breast_discovery_date.strftime('%Y年%m月%d日') if hasattr(record, 'breast_discovery_date') and record.breast_discovery_date else (
            record.nodule_discovery_time.strftime('%Y年%m月%d日') if record.nodule_discovery_time else '未知'
        ),
    }


def extract_lung_fields(record) -> dict:
    """提取肺结节相关字段（仅包含报告模板实际使用的字段）"""
    return {
        # 影像学特征
        'lung_rads_level': record.lung_rads_level if hasattr(record, 'lung_rads_level') else None,
        'lung_nodule_size': record.lung_nodule_size if hasattr(record, 'lung_nodule_size') else None,
        'lung_symptoms': record.lung_symptoms if hasattr(record, 'lung_symptoms') else None,
        'symptoms_other': record.lung_symptoms_other if hasattr(record, 'lung_symptoms_other') and record.lung_symptoms_other else (
            record.symptoms_other if hasattr(record, 'symptoms_other') and record.symptoms_other else ''
        ),
        'lung_symptoms_other': record.lung_symptoms_other if hasattr(record, 'lung_symptoms_other') and record.lung_symptoms_other else '',

        # 结节数量信息
        'nodule_quantity': (
            record.lung_nodule_quantity if hasattr(record, 'lung_nodule_quantity') and record.lung_nodule_quantity
            else (record.nodule_quantity if hasattr(record, 'nodule_quantity') and record.nodule_quantity else None)
        ),
        # 合并类/三结节模板 & 提示词专用：显式肺部数量字段，避免覆盖乳腺/甲状腺
        'nodule_quantity_lung': (
            record.lung_nodule_quantity if hasattr(record, 'lung_nodule_quantity') and record.lung_nodule_quantity
            else (record.nodule_quantity if hasattr(record, 'nodule_quantity') and record.nodule_quantity else None)
        ),
        'lung_nodule_count': record.lung_nodule_count if hasattr(record, 'lung_nodule_count') and record.lung_nodule_count is not None else None,
        'nodule_count_lung': record.lung_nodule_count if hasattr(record, 'lung_nodule_count') and record.lung_nodule_count is not None else None,

        # 基础疾病史（整合为lung_cancer_history字段）
        'lung_cancer_history': (
            record.lung_cancer_history
            if hasattr(record, 'lung_cancer_history') and record.lung_cancer_history and record.lung_cancer_history.strip()
            else '无'
        ),
        'lung_cancer_history_other': record.lung_cancer_history_other if hasattr(record, 'lung_cancer_history_other') and record.lung_cancer_history_other else '',

        # 家族史/用药史：多器官优先读肺部专属字段，兼容旧字段
        'family_history': (
            record.lung_family_history
            if hasattr(record, 'lung_family_history') and record.lung_family_history and str(record.lung_family_history).strip()
            else (record.family_history if hasattr(record, 'family_history') and record.family_history and str(record.family_history).strip() else '无')
        ),
        'family_history_other': (
            record.lung_family_history_other
            if hasattr(record, 'lung_family_history_other') and record.lung_family_history_other
            else (record.family_history_other if hasattr(record, 'family_history_other') and record.family_history_other else '')
        ),
        'medication_history': (
            record.lung_medication_history
            if hasattr(record, 'lung_medication_history') and record.lung_medication_history and str(record.lung_medication_history).strip()
            else (record.medication_history if hasattr(record, 'medication_history') and record.medication_history and str(record.medication_history).strip() else '无')
        ),
        'medication_other': (
            record.lung_medication_other
            if hasattr(record, 'lung_medication_other') and record.lung_medication_other
            else (record.medication_other if hasattr(record, 'medication_other') and record.medication_other else '')
        ),
        # 显式输出肺部专属字段（供合并类提示词/模板使用）
        'lung_family_history': record.lung_family_history if hasattr(record, 'lung_family_history') and record.lung_family_history else '',
        'lung_family_history_other': record.lung_family_history_other if hasattr(record, 'lung_family_history_other') and record.lung_family_history_other else '',
        'lung_medication_history': record.lung_medication_history if hasattr(record, 'lung_medication_history') and record.lung_medication_history else '',
        'lung_medication_other': record.lung_medication_other if hasattr(record, 'lung_medication_other') and record.lung_medication_other else '',

        # 肺结节发现时间
        'lung_discovery_date': record.lung_discovery_date.strftime('%Y年%m月%d日') if hasattr(record, 'lung_discovery_date') and record.lung_discovery_date else (
            record.nodule_discovery_time.strftime('%Y年%m月%d日') if hasattr(record, 'nodule_discovery_time') and record.nodule_discovery_time else '未知'
        ),

        # 注意：以下字段已从报告模板移除，不再提取：
        # - lung_nodule_location (结节位置)
        # - lung_boundary_features (边界特征)
        # - lung_internal_echo (内部回声)
        # - lung_blood_flow_signal (血流信号)
        # - pneumonia_history, tb_history, copd_history, fibrosis_history (单独的病史字段已合并到lung_cancer_history)
    }


def extract_thyroid_fields(record) -> dict:
    """提取甲状腺结节相关字段"""
    thyroid_count = (
        record.thyroid_nodule_count
        if hasattr(record, 'thyroid_nodule_count') and record.thyroid_nodule_count
        else (record.nodule_count if hasattr(record, 'nodule_count') and record.nodule_count else None)
    )
    return {
        # 影像学特征
        'tirads_level': record.tirads_level if hasattr(record, 'tirads_level') else None,
        'thyroid_nodule_size': record.thyroid_nodule_size if hasattr(record, 'thyroid_nodule_size') else None,
        'thyroid_nodule_location': record.thyroid_nodule_location if hasattr(record, 'thyroid_nodule_location') else None,
        'thyroid_boundary_features': record.thyroid_boundary_features if hasattr(record, 'thyroid_boundary_features') else None,
        'thyroid_internal_echo': record.thyroid_internal_echo if hasattr(record, 'thyroid_internal_echo') else None,
        'thyroid_blood_flow_signal': record.thyroid_blood_flow_signal if hasattr(record, 'thyroid_blood_flow_signal') else None,
        # 甲状腺“多发结节个数”（注意与“数量：单发/多发”区分）
        'thyroid_nodule_count': record.thyroid_nodule_count if hasattr(record, 'thyroid_nodule_count') else None,
        'thyroid_symptoms': record.thyroid_symptoms if hasattr(record, 'thyroid_symptoms') else None,
        # “其他”说明（用于提示词完整表达；不同表单会把“其他”统一落到 symptoms_other）
        'symptoms_other': record.thyroid_symptoms_other if hasattr(record, 'thyroid_symptoms_other') and record.thyroid_symptoms_other else (
            record.symptoms_other if hasattr(record, 'symptoms_other') and record.symptoms_other else ''
        ),
        'thyroid_symptoms_other': record.thyroid_symptoms_other if hasattr(record, 'thyroid_symptoms_other') and record.thyroid_symptoms_other else '',
        
        # 通用结节数量信息（新表单字段体系）
        'nodule_quantity': (
            record.thyroid_nodule_quantity if hasattr(record, 'thyroid_nodule_quantity') and record.thyroid_nodule_quantity
            else (record.nodule_quantity if hasattr(record, 'nodule_quantity') and record.nodule_quantity else None)
        ),
        # 单甲状腺：nodule_count 即甲状腺“多发个数”；多器官：优先使用 thyroid_nodule_count，避免被乳腺 nodule_count 覆盖
        'nodule_count': thyroid_count,
        # 合并类/三结节模板 & 提示词专用：显式甲状腺数量字段，避免覆盖乳腺/肺
        'nodule_quantity_thyroid': (
            record.thyroid_nodule_quantity if hasattr(record, 'thyroid_nodule_quantity') and record.thyroid_nodule_quantity
            else (record.nodule_quantity if hasattr(record, 'nodule_quantity') and record.nodule_quantity else None)
        ),
        'nodule_count_thyroid': thyroid_count,
        # 钙化情况（如果数据库中有这个字段）
        'thyroid_calcification': record.thyroid_calcification if hasattr(record, 'thyroid_calcification') else None,

        # 病史
        'hyperthyroidism_history': record.hyperthyroidism_history if hasattr(record, 'hyperthyroidism_history') else '无',
        'hypothyroidism_history': record.hypothyroidism_history if hasattr(record, 'hypothyroidism_history') else '无',
        'hypothyroidism_history_other': record.hypothyroidism_history_other if hasattr(record, 'hypothyroidism_history_other') and record.hypothyroidism_history_other else '',
        'hashimoto_history': record.hashimoto_history if hasattr(record, 'hashimoto_history') else '无',
        'subacute_thyroiditis_history': record.subacute_thyroiditis_history if hasattr(record, 'subacute_thyroiditis_history') else '无',
        'thyroid_cancer_history': record.thyroid_cancer_history if hasattr(record, 'thyroid_cancer_history') else '无',
        'hereditary_thyroid_history': record.hereditary_thyroid_history if hasattr(record, 'hereditary_thyroid_history') else '无',

        # 家族史/用药史：多器官优先读甲状腺专属字段，兼容旧字段
        'family_history': (
            record.thyroid_family_history
            if hasattr(record, 'thyroid_family_history') and record.thyroid_family_history and str(record.thyroid_family_history).strip()
            else (record.family_history if hasattr(record, 'family_history') and record.family_history and str(record.family_history).strip() else '无')
        ),
        'family_history_other': (
            record.thyroid_family_history_other
            if hasattr(record, 'thyroid_family_history_other') and record.thyroid_family_history_other
            else (record.family_history_other if hasattr(record, 'family_history_other') and record.family_history_other else '')
        ),
        'medication_history': (
            record.thyroid_medication_history
            if hasattr(record, 'thyroid_medication_history') and record.thyroid_medication_history and str(record.thyroid_medication_history).strip()
            else (record.medication_history if hasattr(record, 'medication_history') and record.medication_history and str(record.medication_history).strip() else '无')
        ),
        'medication_other': (
            record.thyroid_medication_other
            if hasattr(record, 'thyroid_medication_other') and record.thyroid_medication_other
            else (record.medication_other if hasattr(record, 'medication_other') and record.medication_other else '')
        ),
        # 显式输出甲状腺专属字段（供合并类提示词/模板使用）
        'thyroid_family_history': record.thyroid_family_history if hasattr(record, 'thyroid_family_history') and record.thyroid_family_history else '',
        'thyroid_family_history_other': record.thyroid_family_history_other if hasattr(record, 'thyroid_family_history_other') and record.thyroid_family_history_other else '',
        'thyroid_medication_history': record.thyroid_medication_history if hasattr(record, 'thyroid_medication_history') and record.thyroid_medication_history else '',
        'thyroid_medication_other': record.thyroid_medication_other if hasattr(record, 'thyroid_medication_other') and record.thyroid_medication_other else '',

        # 甲状腺结节发现时间
        'thyroid_discovery_date': record.thyroid_discovery_date.strftime('%Y年%m月%d日') if hasattr(record, 'thyroid_discovery_date') and record.thyroid_discovery_date else (
            record.nodule_discovery_time.strftime('%Y年%m月%d日') if record.nodule_discovery_time else '未知'
        ),
    }


def extract_template_fields(patient, record, nodule_type: str) -> dict:
    """
    根据结节类型提取渲染模板所需的所有字段

    Args:
        patient: 患者对象
        record: 健康档案对象
        nodule_type: 结节类型

    Returns:
        包含所有字段的字典
    """
    # 先获取通用字段
    fields = extract_common_fields(patient, record)

    # 根据结节类型添加特定字段
    if nodule_type == 'breast':
        fields.update(extract_breast_fields(record))
        # 单一类型使用通用的discovery_date
        fields['discovery_date'] = fields.get('breast_discovery_date', '未知')
        # 添加兼容字段名（模板可能使用history而不是breast_disease_history）
        fields['history'] = fields.get('breast_disease_history', '无')

    elif nodule_type == 'lung':
        lung_fields = extract_lung_fields(record)
        fields.update(lung_fields)
        fields['discovery_date'] = fields.get('lung_discovery_date', '未知')
        # 添加不带前缀的字段名（模板兼容）
        fields['symptoms'] = lung_fields.get('lung_symptoms')
        fields['nodule_size'] = lung_fields.get('lung_nodule_size')
        fields['nodule_count'] = lung_fields.get('lung_nodule_count')
        # 注意：以下字段已从报告模板移除，不再映射：
        # - nodule_location, boundary_features, internal_echo, blood_flow_signal

    elif nodule_type == 'thyroid':
        thyroid_fields = extract_thyroid_fields(record)
        fields.update(thyroid_fields)
        fields['discovery_date'] = fields.get('thyroid_discovery_date', '未知')
        # 添加不带前缀的字段名（模板兼容）
        fields['symptoms'] = thyroid_fields.get('thyroid_symptoms')
        fields['nodule_location'] = thyroid_fields.get('thyroid_nodule_location')
        fields['nodule_size'] = thyroid_fields.get('thyroid_nodule_size')
        fields['boundary_features'] = thyroid_fields.get('thyroid_boundary_features')
        fields['internal_echo'] = thyroid_fields.get('thyroid_internal_echo')
        fields['blood_flow_signal'] = thyroid_fields.get('thyroid_blood_flow_signal')

    elif nodule_type == 'breast_lung':
        breast_fields = extract_breast_fields(record)
        lung_fields = extract_lung_fields(record)
        fields.update(breast_fields)
        fields.update(lung_fields)

        # 为组合模板添加特殊字段映射（模板期望 symptoms_breast 格式）
        # 乳腺字段映射
        fields['symptoms_breast'] = breast_fields.get('symptoms')
        fields['location_breast'] = breast_fields.get('nodule_location')
        fields['boundary_breast'] = breast_fields.get('boundary_features')
        fields['echo_breast'] = breast_fields.get('internal_echo')
        fields['flow_breast'] = breast_fields.get('blood_flow_signal')
        fields['breast_size'] = breast_fields.get('nodule_size')

        # 肺字段映射
        fields['symptoms_lung'] = lung_fields.get('lung_symptoms')
        fields['location_lung'] = lung_fields.get('lung_nodule_location')
        fields['boundary_lung'] = lung_fields.get('lung_boundary_features')
        fields['echo_lung'] = lung_fields.get('lung_internal_echo')
        fields['flow_lung'] = lung_fields.get('lung_blood_flow_signal')
        fields['lung_size'] = lung_fields.get('lung_nodule_size')
        fields['lungrads_level'] = lung_fields.get('lung_rads_level')

    elif nodule_type == 'breast_thyroid':
        breast_fields = extract_breast_fields(record)
        thyroid_fields = extract_thyroid_fields(record)
        fields.update(breast_fields)
        fields.update(thyroid_fields)

        # 乳腺字段映射
        fields['symptoms_breast'] = breast_fields.get('symptoms')
        fields['location_breast'] = breast_fields.get('nodule_location')
        fields['boundary_breast'] = breast_fields.get('boundary_features')
        fields['echo_breast'] = breast_fields.get('internal_echo')
        fields['flow_breast'] = breast_fields.get('blood_flow_signal')
        fields['breast_size'] = breast_fields.get('nodule_size')

        # 甲状腺字段映射
        fields['symptoms_thyroid'] = thyroid_fields.get('thyroid_symptoms')
        fields['location_thyroid'] = thyroid_fields.get('thyroid_nodule_location')
        fields['boundary_thyroid'] = thyroid_fields.get('thyroid_boundary_features')
        fields['echo_thyroid'] = thyroid_fields.get('thyroid_internal_echo')
        fields['flow_thyroid'] = thyroid_fields.get('thyroid_blood_flow_signal')
        fields['thyroid_size'] = thyroid_fields.get('thyroid_nodule_size')

    elif nodule_type == 'lung_thyroid':
        lung_fields = extract_lung_fields(record)
        thyroid_fields = extract_thyroid_fields(record)
        fields.update(lung_fields)
        fields.update(thyroid_fields)

        # 肺字段映射
        fields['symptoms_lung'] = lung_fields.get('lung_symptoms')
        fields['nodule_location_lung'] = lung_fields.get('lung_nodule_location')
        fields['boundary_lung'] = lung_fields.get('lung_boundary_features')
        fields['echo_lung'] = lung_fields.get('lung_internal_echo')
        fields['flow_lung'] = lung_fields.get('lung_blood_flow_signal')
        fields['lung_size'] = lung_fields.get('lung_nodule_size')
        fields['lungrads_level'] = lung_fields.get('lung_rads_level')

        # 甲状腺字段映射
        fields['symptoms_thyroid'] = thyroid_fields.get('thyroid_symptoms')
        fields['nodule_location_thyroid'] = thyroid_fields.get('thyroid_nodule_location')
        fields['boundary_thyroid'] = thyroid_fields.get('thyroid_boundary_features')
        fields['echo_thyroid'] = thyroid_fields.get('thyroid_internal_echo')
        fields['flow_thyroid'] = thyroid_fields.get('thyroid_blood_flow_signal')
        fields['thyroid_size'] = thyroid_fields.get('thyroid_nodule_size')

    elif nodule_type == 'triple':
        breast_fields = extract_breast_fields(record)
        lung_fields = extract_lung_fields(record)
        thyroid_fields = extract_thyroid_fields(record)
        fields.update(breast_fields)
        fields.update(lung_fields)
        fields.update(thyroid_fields)

        # 乳腺字段映射
        fields['symptoms_breast'] = breast_fields.get('symptoms')
        fields['location_breast'] = breast_fields.get('nodule_location')
        fields['boundary_breast'] = breast_fields.get('boundary_features')
        fields['echo_breast'] = breast_fields.get('internal_echo')
        fields['flow_breast'] = breast_fields.get('blood_flow_signal')
        fields['breast_size'] = breast_fields.get('nodule_size')

        # 肺字段映射
        fields['symptoms_lung'] = lung_fields.get('lung_symptoms')
        fields['location_lung'] = lung_fields.get('lung_nodule_location')
        fields['boundary_lung'] = lung_fields.get('lung_boundary_features')
        fields['echo_lung'] = lung_fields.get('lung_internal_echo')
        fields['flow_lung'] = lung_fields.get('lung_blood_flow_signal')
        fields['lung_size'] = lung_fields.get('lung_nodule_size')
        fields['lungrads_level'] = lung_fields.get('lung_rads_level')

        # 甲状腺字段映射
        fields['symptoms_thyroid'] = thyroid_fields.get('thyroid_symptoms')
        fields['location_thyroid'] = thyroid_fields.get('thyroid_nodule_location')
        fields['boundary_thyroid'] = thyroid_fields.get('thyroid_boundary_features')
        fields['echo_thyroid'] = thyroid_fields.get('thyroid_internal_echo')
        fields['flow_thyroid'] = thyroid_fields.get('thyroid_blood_flow_signal')
        fields['thyroid_size'] = thyroid_fields.get('thyroid_nodule_size')

    else:
        raise ValueError(f'不支持的结节类型: {nodule_type}')

    return fields


# ==================== LLM数据准备 ====================

def prepare_llm_patient_data(record, nodule_type: str, patient=None) -> dict:
    """
    准备传递给LLM的患者数据
    用于生成影像学评估和疾病史评估
    
    注意：如果健康档案有关联的影像报告，会优先使用报告中的提取数据（以报告为准）

    Args:
        record: 健康档案对象
        nodule_type: 结节类型
        patient: 患者对象（可选，用于获取性别等基本信息）

    Returns:
        LLM所需的患者数据字典
    """
    # 基本信息（所有类型都需要）
    patient_data = {
        'height': record.height if hasattr(record, 'height') and record.height is not None else None,
        'weight': record.weight if hasattr(record, 'weight') and record.weight is not None else None,
    }
    
    # 添加年龄信息（优先从record获取，如果没有则从patient获取）
    if hasattr(record, 'age') and record.age is not None:
        patient_data['age'] = record.age
    elif patient and hasattr(patient, 'age') and patient.age is not None:
        patient_data['age'] = patient.age
    elif hasattr(record, 'patient_id'):
        # 如果提供了record但没有patient，尝试从record关联的patient获取
        try:
            from models import BPatient, NodulePatient
            # 尝试从BPatient获取
            b_patient = BPatient.query.get(record.patient_id)
            if b_patient and hasattr(b_patient, 'age') and b_patient.age is not None:
                patient_data['age'] = b_patient.age
            else:
                # 尝试从NodulePatient获取
                nodule_patient = NodulePatient.query.get(record.patient_id)
                if nodule_patient and hasattr(nodule_patient, 'age') and nodule_patient.age is not None:
                    patient_data['age'] = nodule_patient.age
        except:
            pass
    
    # 添加性别信息（从patient对象获取）
    if patient and hasattr(patient, 'gender'):
        patient_data['gender'] = patient.gender
    elif hasattr(record, 'patient_id'):
        # 如果提供了record但没有patient，尝试从record关联的patient获取
        try:
            from models import BPatient, NodulePatient
            # 尝试从BPatient获取
            b_patient = BPatient.query.get(record.patient_id)
            if b_patient and hasattr(b_patient, 'gender'):
                patient_data['gender'] = b_patient.gender
            else:
                # 尝试从NodulePatient获取
                nodule_patient = NodulePatient.query.get(record.patient_id)
                if nodule_patient and hasattr(nodule_patient, 'gender'):
                    patient_data['gender'] = nodule_patient.gender
        except:
            pass

    # 根据结节类型添加特定字段
    # 修复：对于'triple'类型，需要同时提取三种结节的数据
    if nodule_type == 'triple' or 'breast' in nodule_type:
        breast_data = extract_breast_fields(record)
        # 保留发现时间字段（提示词模板要求包含发现时间信息）
        # 将格式化的日期字符串转换为更简洁的格式，便于LLM理解
        if 'breast_discovery_date' in breast_data and breast_data['breast_discovery_date']:
            # 保持原有格式（如：2025年12月05日），LLM可以理解
            pass
        patient_data.update(breast_data)

    if nodule_type == 'triple' or 'lung' in nodule_type:
        lung_data = extract_lung_fields(record)
        # 保留发现时间字段（提示词模板要求包含发现时间信息）
        patient_data.update(lung_data)

    if nodule_type == 'triple' or 'thyroid' in nodule_type:
        thyroid_data = extract_thyroid_fields(record)
        # 保留发现时间字段（提示词模板要求包含发现时间信息）
        patient_data.update(thyroid_data)

    # 注意：只添加前端表单实际使用的字段
    # diabetes_history 已经在 extract_common_fields 中提取
    # medication_history 已经在 extract_breast_fields 中提取
    # 以下字段前端表单中没有，不再添加：
    # - radiation_exposure_history
    # - autoimmune_disease_history
    # - tumor_marker_test
    # - smoking_risk_level
    # - diabetes_control_level

    # 整合影像报告数据（以报告为准）
    # 检查健康档案是否有关联的影像报告
    if hasattr(record, 'imaging_reports') and record.imaging_reports:
        print(f"\n📎 发现 {len(record.imaging_reports)} 个影像报告，开始整合数据...")
        
        # 遍历所有影像报告，合并提取的数据（以报告为准）
        for imaging_report in record.imaging_reports:
            if imaging_report.extracted_data:
                print(f"📊 整合影像报告数据: {imaging_report.file_name}")
                # 将报告提取的数据合并到patient_data中（覆盖表单数据）
                for key, value in imaging_report.extracted_data.items():
                    if value is not None:  # 只覆盖非空值
                        old_value = patient_data.get(key)
                        patient_data[key] = value
                        if old_value != value:
                            print(f"  ✅ {key}: {old_value} -> {value} (以报告为准)")
        
        print(f"✅ 影像报告数据整合完成\n")
    
    return patient_data
