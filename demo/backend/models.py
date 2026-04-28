"""
B端C端完全分离的数据模型
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()

# ============================================
# 共享表
# ============================================

class User(db.Model):
    """B端用户表 - 健康管理师"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    wechat_id = db.Column(db.String(50))  # 健康管理师微信号（用于C端展示与联系）
    role = db.Column(db.String(20), default='health_manager')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'email': self.email,
            'phone': self.phone,
            'wechat_id': self.wechat_id,
            'role': self.role
        }


class KnowledgeItem(db.Model):
    """知识库表 - 统一知识库"""
    __tablename__ = 'unified_knowledge_base'
    __table_args__ = {'schema': 'ai_agents'}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    priority = db.Column(db.Integer, default=5)
    source_type = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # 匹配维度字段
    risk_level = db.Column(db.Text)
    age_min = db.Column(db.Integer)
    age_max = db.Column(db.Integer)
    age_range = db.Column(db.Text)
    birads_min = db.Column(db.Integer)
    birads_max = db.Column(db.Integer)
    birads_category = db.Column(db.String(50))
    course_stage = db.Column(db.Text)
    tnm_stage = db.Column(db.Integer)
    symptom_type = db.Column(db.String(100))
    family_history_type = db.Column(db.String(50))
    rhythm_category = db.Column(db.String(50))
    sleep_pattern = db.Column(db.String(50))
    exam_history_type = db.Column(db.String(50))
    recommendation_level = db.Column(db.String(20))
    evidence_level = db.Column(db.String(20))
    symptoms = db.Column(db.Text)
    symptom_subtype = db.Column(db.Text)
    pain_type = db.Column(db.Text)
    family_history = db.Column(db.Text)
    family_category = db.Column(db.Text)
    family_subcategory = db.Column(db.Text)
    rhythm_type = db.Column(db.Text)
    cycle_phase = db.Column(db.Text)
    phase_timing = db.Column(db.Text)
    core_task = db.Column(db.Text)
    sleep_quality = db.Column(db.Text)
    sleep_condition = db.Column(db.Text)
    exam_history_type = db.Column(db.Text)
    exam_subcategory = db.Column(db.Text)
    nodule_location = db.Column(db.Text)
    nodule_size = db.Column(db.Text)
    boundary_features = db.Column(db.Text)
    internal_echo = db.Column(db.Text)
    risk_features = db.Column(db.Text)
    blood_flow_signal = db.Column(db.Text)
    elasticity_score = db.Column(db.Text)
    alert_rule = db.Column(db.Text)
    interventions = db.Column(db.Text)
    details = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def _format_checkbox_value(value):
        """
        ISDoc
        @description 格式化checkbox值，兼容数据库中可能出现的 {} / [] / {a,b} 等格式
        @param value 原始值
        @returns {str|None} 格式化后的字符串或None
        """
        if value is None:
            return None
        if value == '':
            return ''
        try:
            value_str = str(value).strip()
            if value_str in ('{}', '[]'):
                return ''
            if value_str.startswith('{') and value_str.endswith('}'):
                content = value_str[1:-1].strip()
                return content or ''
            return value_str
        except Exception:
            return value
    
    def format_checkbox_value(self, value):
        """
        ISDoc
        @description 兼容旧调用：KnowledgeItem.format_checkbox_value(...)
        @param value 原始值
        @returns {str|None} 格式化后的字符串或None
        """
        return self._format_checkbox_value(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'source_type': self.source_type,
            'risk_level': self.risk_level,
            'age_range': self.age_range,
            'birads_min': self.birads_min,
            'birads_max': self.birads_max,
            'symptoms': self.symptoms,
            'family_history': self._format_checkbox_value(self.family_history),
            'nodule_location': self.nodule_location,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class RiskAssessmentRule(db.Model):
    """风险评估规则表"""
    __tablename__ = 'risk_assessment_rules'
    __table_args__ = {'schema': 'ai_agents'}
    
    id = db.Column(db.Integer, primary_key=True)
    dimension = db.Column(db.Text, nullable=False)              # 评估维度：家族史/疾病史/影像学/分子标志物
    risk_level = db.Column(db.Text, nullable=False)             # 风险等级：低危/中危/高危
    criteria = db.Column(db.Text, nullable=False)               # 判定标准
    monitoring_frequency = db.Column(db.Text)                   # 监测频率
    upgrade_conditions = db.Column(db.Text)                     # 升级条件
    intervention_priority = db.Column(db.Text)                  # 干预优先级
    weight_percentage = db.Column(db.Integer)                   # 权重百分比
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'dimension': self.dimension,
            'risk_level': self.risk_level,
            'criteria': self.criteria,
            'monitoring_frequency': self.monitoring_frequency,
            'upgrade_conditions': self.upgrade_conditions,
            'intervention_priority': self.intervention_priority,
            'weight_percentage': self.weight_percentage
        }


# ============================================
# B端专用表
# ============================================

class BPatient(db.Model):
    """B端患者表"""
    __tablename__ = 'b_patients'

    id = db.Column(db.Integer, primary_key=True)
    patient_code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    wechat_id = db.Column(db.String(50))

    # B端特有字段
    nodule_type = db.Column(db.String(50))  # 结节类型：breast/lung/thyroid/breast_lung/breast_thyroid/lung_thyroid/triple
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    source_channel = db.Column(db.String(50), default='b_end')
    status = db.Column(db.String(20), default='active')
    is_new = db.Column(db.Boolean, default=True)  # 新患者提醒
    
    # 时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    manager = db.relationship('User', foreign_keys=[manager_id])  # 管理师关系
    records = db.relationship('BHealthRecord', backref='patient', lazy='dynamic')
    reports = db.relationship('BReport', backref='patient', lazy='dynamic')
    follow_ups = db.relationship('BFollowUpRecord', backref='patient', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_code': self.patient_code,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'wechat_id': self.wechat_id,
            'nodule_type': self.nodule_type,
            'source_channel': self.source_channel,
            'status': self.status,
            'is_new': self.is_new,
            'manager_id': self.manager_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class BHealthRecord(db.Model):
    """B端健康档案表"""
    __tablename__ = 'b_health_records'
    
    @staticmethod
    def _format_checkbox_value(value):
        """格式化checkbox值，处理 {} 和 {其他} 等格式"""
        if value is None:
            return None
        if value == '':
            return ''
        try:
            value_str = str(value).strip()
            # 处理 {} 格式
            if value_str == '{}' or value_str == '[]':
                return ''
            # 处理 {其他} 或 {值1,值2} 格式
            if value_str.startswith('{') and value_str.endswith('}'):
                content = value_str[1:-1].strip()
                if not content:
                    return ''
                # 如果包含逗号，说明是多个值，返回逗号分隔的字符串
                if ',' in content:
                    return content
                return content
            return value_str
        except Exception as e:
            # 如果格式化失败，返回原值
            return value
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('b_patients.id'), nullable=False)
    record_code = db.Column(db.String(50), unique=True)
    
    # 基本健康信息
    age = db.Column(db.Integer)
    height = db.Column(db.Float)  # 身高(cm)
    weight = db.Column(db.Float)  # 体重(kg)
    phone = db.Column(db.String(20))  # 联系电话
    diabetes_history = db.Column(db.String(50))  # 糖尿病史
    gaofang_address = db.Column(db.String(500))  # 可接收膏方的收货地址
    birads_level = db.Column(db.String(10))  # BI-RADS分级（支持4A/4B/4C等）
    family_history = db.Column(db.String(100))
    
    # 病程信息
    nodule_discovery_time = db.Column(db.Date)  # 通用结节发现时间（用于单一结节类型）
    breast_discovery_date = db.Column(db.Date)  # 乳腺结节发现时间
    lung_discovery_date = db.Column(db.Date)    # 肺结节发现时间
    thyroid_discovery_date = db.Column(db.Date) # 甲状腺结节发现时间
    course_stage = db.Column(db.String(50))
    tnm_stage = db.Column(db.String(10))
    
    # 症状信息
    symptoms = db.Column(db.String(200))
    symptoms_other = db.Column(db.String(200))  # 其他症状
    # 多器官场景下“其他症状”需要分开存储，避免乳腺/肺/甲状腺互相覆盖
    breast_symptoms_other = db.Column(db.String(200))  # 乳腺症状“其他”说明
    lung_symptoms_other = db.Column(db.String(200))    # 肺部症状“其他”说明
    thyroid_symptoms_other = db.Column(db.String(200)) # 甲状腺症状“其他”说明
    pain_level = db.Column(db.Integer)
    pain_type = db.Column(db.String(50))
    nipple_discharge_type = db.Column(db.String(50))
    skin_change_type = db.Column(db.String(50))
    
    # 影像学信息
    nodule_location = db.Column(db.String(50))
    nodule_size = db.Column(db.String(50))
    boundary_features = db.Column(db.String(100))
    internal_echo = db.Column(db.String(50))
    blood_flow_signal = db.Column(db.String(50))
    elasticity_score = db.Column(db.String(20))
    
    # 生物节律
    rhythm_type = db.Column(db.String(50))
    cycle_phase = db.Column(db.String(50))
    sleep_quality = db.Column(db.String(100))
    sleep_condition = db.Column(db.String(50))
    
    # 检查历史
    exam_history_type = db.Column(db.String(50))
    exam_special_situation = db.Column(db.String(100))  # 特殊检查史情况
    exam_subcategory = db.Column(db.String(100))  # 检查史子分类
    exam_history_detail = db.Column(db.String(200))
    previous_exam_history = db.Column(db.Text)
    
    # 生活方式
    exercise_frequency = db.Column(db.String(50))
    lifestyle = db.Column(db.String(50))
    
    # 疾病史与风险因素（新增：对应知识库匹配）
    breast_disease_history = db.Column(db.String(200))  # 乳腺疾病史（多选，逗号分隔）
    breast_disease_history_other = db.Column(db.String(200))  # 其他基础疾病史
    family_genetic_history = db.Column(db.String(100))  # 家族遗传史（单选）
    family_history_other = db.Column(db.String(200))  # 其他家族史
    previous_biopsy_history = db.Column(db.String(100))  # 既往活检史（多选，逗号分隔）
    contraceptive_risk_level = db.Column(db.String(20))  # 避孕药风险档位（无/5-10年/>10年）
    smoking_risk_level = db.Column(db.String(20))  # 吸烟风险档位（无/1-10包年/10-20包年/>20包年）
    diabetes_control_level = db.Column(db.String(20))  # 糖尿病控制档位（无/控制良好/控制不良）
    
    # === 乳腺基础疾病史字段 ===
    breast_hyperplasia_history = db.Column(db.String(50))  # 乳腺增生病史
    breast_fibroadenoma_history = db.Column(db.String(50))  # 乳腺纤维瘤病史
    breast_cyst_history = db.Column(db.String(50))  # 乳腺囊肿病史
    breast_inflammation_history = db.Column(db.String(50))  # 乳腺炎病史
    breast_cancer_history = db.Column(db.String(50))  # 乳腺癌病史
    
    # === 其他风险因素字段 ===
    dust_exposure_history = db.Column(db.String(50))  # 粉尘/有害气体接触史
    # 注意：diabetes_history 已在上面定义（第208行），这里不再重复定义
    radiation_exposure_history = db.Column(db.String(200))  # 辐射暴露史（多选，逗号分隔）
    radiation_other = db.Column(db.String(200))  # 其他辐射暴露
    autoimmune_disease_history = db.Column(db.String(200))  # 自身免疫疾病（多选，逗号分隔）
    autoimmune_other = db.Column(db.String(200))  # 其他自身免疫疾病
    medication_history = db.Column(db.String(200))  # 药物使用史（多选，逗号分隔，历史字段：单器官/旧版共用）
    medication_other = db.Column(db.String(200))  # 其他药物使用（历史字段：单器官/旧版共用）

    # 多器官场景：家族史/用药史按器官拆分，避免双结节/三结节混淆
    breast_family_history = db.Column(db.String(200))  # 乳腺家族史（多选，逗号分隔）
    breast_family_history_other = db.Column(db.String(200))  # 乳腺家族史“其他”说明
    breast_medication_history = db.Column(db.String(200))  # 乳腺用药史（多选，逗号分隔）
    breast_medication_other = db.Column(db.String(200))  # 乳腺用药史“其他”说明

    lung_family_history = db.Column(db.String(200))  # 肺部家族史（多选，逗号分隔）
    lung_family_history_other = db.Column(db.String(200))  # 肺部家族史“其他”说明
    lung_medication_history = db.Column(db.String(200))  # 肺部用药史（多选，逗号分隔）
    lung_medication_other = db.Column(db.String(200))  # 肺部用药史“其他”说明

    thyroid_family_history = db.Column(db.String(200))  # 甲状腺家族史（多选，逗号分隔）
    thyroid_family_history_other = db.Column(db.String(200))  # 甲状腺家族史“其他”说明
    thyroid_medication_history = db.Column(db.String(200))  # 甲状腺用药史（多选，逗号分隔）
    thyroid_medication_other = db.Column(db.String(200))  # 甲状腺用药史“其他”说明
    tumor_marker_test = db.Column(db.String(50))  # 肿瘤标志物检查
    hereditary_breast_history = db.Column(db.String(50))  # 遗传性乳腺病史
    
    # === 乳腺结节数量字段 ===
    nodule_quantity = db.Column(db.String(20))  # 数量：单发/多发
    nodule_count = db.Column(db.String(20))  # 多发结节个数（当nodule_quantity为"多发"时填写）
    
    # === 肺/甲状腺数量字段（多器官场景避免与乳腺nodule_quantity冲突） ===
    lung_nodule_quantity = db.Column(db.String(20))  # 肺结节数量：单发/多发
    thyroid_nodule_quantity = db.Column(db.String(20))  # 甲状腺结节数量：单发/多发

    # === 肺结节字段 ===
    lung_rads_level = db.Column(db.String(10))  # Lung-RADS分级
    lung_symptoms = db.Column(db.Text)  # 肺部症状（多选，逗号分隔）
    lung_nodule_location = db.Column(db.Text)  # 肺结节位置（多选）
    lung_boundary_features = db.Column(db.Text)  # 肺结节边界特征（多选）
    lung_internal_echo = db.Column(db.Text)  # 肺结节内部回声（多选）
    lung_blood_flow_signal = db.Column(db.Text)  # 肺结节血流信号（多选）
    lung_nodule_count = db.Column(db.String(20))  # 肺结节数量
    lung_nodule_size = db.Column(db.String(50))  # 肺结节大小(mm)

    # 肺部病史
    pneumonia_history = db.Column(db.String(50))  # 肺炎病史（已废弃，合并到lung_cancer_history）
    tb_history = db.Column(db.String(50))  # 肺结核病史（已废弃，合并到lung_cancer_history）
    copd_history = db.Column(db.String(50))  # 慢性阻塞性肺疾病（已废弃，合并到lung_cancer_history）
    fibrosis_history = db.Column(db.String(50))  # 肺纤维化病史（已废弃，合并到lung_cancer_history）
    lung_cancer_history = db.Column(db.String(200))  # 肺部基础疾病史（多选，逗号分隔）
    lung_cancer_history_other = db.Column(db.String(200))  # 其他肺部基础疾病史
    hereditary_lung_history = db.Column(db.String(50))  # 遗传性肺部病史（已废弃，合并到lung_cancer_history）

    # === 甲状腺结节字段 ===
    tirads_level = db.Column(db.String(10))  # TI-RADS分级
    thyroid_symptoms = db.Column(db.Text)  # 甲状腺症状（多选）
    thyroid_nodule_location = db.Column(db.Text)  # 甲状腺结节位置（多选）
    thyroid_boundary_features = db.Column(db.Text)  # 甲状腺结节边界特征（多选）
    thyroid_internal_echo = db.Column(db.Text)  # 甲状腺结节内部回声（多选）
    thyroid_blood_flow_signal = db.Column(db.Text)  # 甲状腺结节血流信号（多选）
    thyroid_nodule_count = db.Column(db.String(20))  # 甲状腺结节数量
    thyroid_nodule_size = db.Column(db.String(50))  # 甲状腺结节大小(mm)

    # 甲状腺病史
    hyperthyroidism_history = db.Column(db.String(50))  # 甲亢病史
    hypothyroidism_history = db.Column(db.String(50))  # 甲减病史
    hypothyroidism_history_other = db.Column(db.String(200))  # 甲状腺基础疾病史“其他”说明
    hashimoto_history = db.Column(db.String(50))  # 桥本甲状腺炎
    subacute_thyroiditis_history = db.Column(db.String(50))  # 亚急性甲状腺炎
    thyroid_cancer_history = db.Column(db.String(50))  # 甲状腺癌病史
    hereditary_thyroid_history = db.Column(db.String(50))  # 遗传性甲状腺病史

    # B端特有字段
    data_completeness = db.Column(db.String(20), default='full')  # full/partial
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'record_code': self.record_code,
            
            # 基本信息
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'phone': self.phone,
            'diabetes_history': self.diabetes_history,
            'gaofang_address': self.gaofang_address,
            'birads_level': self.birads_level,
            'family_history': self._format_checkbox_value(self.family_history),
            'breast_family_history': self._format_checkbox_value(self.breast_family_history),
            'breast_family_history_other': self.breast_family_history_other,
            'lung_family_history': self._format_checkbox_value(self.lung_family_history),
            'lung_family_history_other': self.lung_family_history_other,
            'thyroid_family_history': self._format_checkbox_value(self.thyroid_family_history),
            'thyroid_family_history_other': self.thyroid_family_history_other,
            
            # 病程信息
            'nodule_discovery_time': self.nodule_discovery_time.strftime('%Y-%m-%d') if self.nodule_discovery_time else None,
            'breast_discovery_date': self.breast_discovery_date.strftime('%Y-%m-%d') if self.breast_discovery_date else None,
            'lung_discovery_date': self.lung_discovery_date.strftime('%Y-%m-%d') if self.lung_discovery_date else None,
            'thyroid_discovery_date': self.thyroid_discovery_date.strftime('%Y-%m-%d') if self.thyroid_discovery_date else None,
            'course_stage': self.course_stage,
            'tnm_stage': self.tnm_stage,
            
            # 症状信息
            'symptoms': self._format_checkbox_value(self.symptoms),
            'symptoms_other': self.symptoms_other,
            'breast_symptoms_other': self.breast_symptoms_other,
            'lung_symptoms_other': self.lung_symptoms_other,
            'thyroid_symptoms_other': self.thyroid_symptoms_other,
            'pain_level': self.pain_level,
            'pain_type': self.pain_type,
            'nipple_discharge_type': self.nipple_discharge_type,
            'skin_change_type': self.skin_change_type,
            
            # 影像学信息
            'nodule_location': self.nodule_location,
            'nodule_size': self.nodule_size,
            'boundary_features': self.boundary_features,
            'internal_echo': self.internal_echo,
            'blood_flow_signal': self.blood_flow_signal,
            'elasticity_score': self.elasticity_score,
            
            # 生物节律
            'rhythm_type': self.rhythm_type,
            'cycle_phase': self.cycle_phase,
            'sleep_quality': self.sleep_quality,
            'sleep_condition': self.sleep_condition,
            
            # 检查历史
            'exam_history_type': self.exam_history_type,
            'exam_special_situation': self.exam_special_situation,
            'exam_subcategory': self.exam_subcategory,
            'exam_history_detail': self.exam_history_detail,
            'previous_exam_history': self.previous_exam_history,
            
            # 生活方式
            'exercise_frequency': self.exercise_frequency,
            'lifestyle': self.lifestyle,
            
            # 疾病史与风险因素（新增6个字段）
            'breast_disease_history': self._format_checkbox_value(self.breast_disease_history),
            'breast_disease_history_other': self.breast_disease_history_other,
            'family_genetic_history': self.family_genetic_history,
            'family_history_other': self.family_history_other,
            'previous_biopsy_history': self.previous_biopsy_history,
            'contraceptive_risk_level': self.contraceptive_risk_level,
            'smoking_risk_level': self.smoking_risk_level,
            'diabetes_control_level': self.diabetes_control_level,
            
            # 乳腺基础疾病史
            'breast_hyperplasia_history': self.breast_hyperplasia_history,
            'breast_fibroadenoma_history': self.breast_fibroadenoma_history,
            'breast_cyst_history': self.breast_cyst_history,
            'breast_inflammation_history': self.breast_inflammation_history,
            'breast_cancer_history': self.breast_cancer_history,
            
            # 其他风险因素
            'dust_exposure_history': self.dust_exposure_history,
            'diabetes_history': self.diabetes_history,
            'radiation_exposure_history': self.radiation_exposure_history,
            'radiation_other': self.radiation_other,
            'autoimmune_disease_history': self.autoimmune_disease_history,
            'autoimmune_other': self.autoimmune_other,
            'medication_history': self._format_checkbox_value(self.medication_history),
            'medication_other': self.medication_other,
            'breast_medication_history': self._format_checkbox_value(self.breast_medication_history),
            'breast_medication_other': self.breast_medication_other,
            'lung_medication_history': self._format_checkbox_value(self.lung_medication_history),
            'lung_medication_other': self.lung_medication_other,
            'thyroid_medication_history': self._format_checkbox_value(self.thyroid_medication_history),
            'thyroid_medication_other': self.thyroid_medication_other,
            'tumor_marker_test': self.tumor_marker_test,
            'hereditary_breast_history': self.hereditary_breast_history,
            
            # 乳腺结节数量
            'nodule_quantity': self.nodule_quantity,
            'nodule_count': self.nodule_count,
            'lung_nodule_quantity': self.lung_nodule_quantity,
            'thyroid_nodule_quantity': self.thyroid_nodule_quantity,

            # 肺结节字段（仅返回报告实际使用的字段）
            'lung_rads_level': self.lung_rads_level,
            'lung_symptoms': self.lung_symptoms,
            'lung_nodule_count': self.lung_nodule_count,
            'lung_nodule_size': self.lung_nodule_size,
            'lung_cancer_history': self.lung_cancer_history,
            'lung_cancer_history_other': self.lung_cancer_history_other,
            # 注意：以下字段已从报告移除，但仍保留在数据库中（兼容性）：
            # - lung_nodule_location, lung_boundary_features, lung_internal_echo, lung_blood_flow_signal
            # - pneumonia_history, tb_history, copd_history, fibrosis_history, hereditary_lung_history

            # 甲状腺结节字段
            'tirads_level': self.tirads_level,
            'thyroid_symptoms': self.thyroid_symptoms,
            'thyroid_nodule_location': self.thyroid_nodule_location,
            'thyroid_boundary_features': self.thyroid_boundary_features,
            'thyroid_internal_echo': self.thyroid_internal_echo,
            'thyroid_blood_flow_signal': self.thyroid_blood_flow_signal,
            'thyroid_nodule_count': self.thyroid_nodule_count,
            'thyroid_nodule_size': self.thyroid_nodule_size,
            'hyperthyroidism_history': self.hyperthyroidism_history,
            'hypothyroidism_history': self.hypothyroidism_history,
            'hashimoto_history': self.hashimoto_history,
            'subacute_thyroiditis_history': self.subacute_thyroiditis_history,
            'thyroid_cancer_history': self.thyroid_cancer_history,
            'hereditary_thyroid_history': self.hereditary_thyroid_history,
            'hypothyroidism_history_other': self.hypothyroidism_history_other,

            # 状态
            'data_completeness': self.data_completeness,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class BImagingReport(db.Model):
    """B端影像报告表"""
    __tablename__ = 'b_imaging_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('b_health_records.id'), nullable=False)  # 关联健康档案
    
    # 文件信息
    file_name = db.Column(db.String(255), nullable=False)  # 原始文件名
    file_path = db.Column(db.String(500), nullable=False)  # 文件存储路径
    file_size = db.Column(db.Integer)  # 文件大小（字节）
    file_type = db.Column(db.String(50))  # 文件类型：pdf/word/image
    
    # 解析内容
    extracted_text = db.Column(db.Text)  # 解析后的原始文本（给LLM用）
    
    # LLM提取的结构化信息（JSON格式）
    extracted_data = db.Column(db.JSON)  # 存储LLM提取的字段：{birads_level: "4A", nodule_size: "8mm", ...}
    
    # LLM分析结果（可选）
    llm_analysis = db.Column(db.Text)  # LLM生成的分析意见（可选）
    
    # 元信息
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 上传者
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    record = db.relationship('BHealthRecord', backref='imaging_reports')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'record_id': self.record_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'extracted_text': self.extracted_text,
            'extracted_data': self.extracted_data,
            'llm_analysis': self.llm_analysis,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if self.uploaded_at else None
        }


class MiniprogramImagingUpload(db.Model):
    """
    ISDoc
    @description 小程序临时上传的影像报告（提交问卷前暂存；提交后转存为BImagingReport并清理）
    """
    __tablename__ = 'miniprogram_imaging_uploads'

    id = db.Column(db.Integer, primary_key=True)

    phone = db.Column(db.String(20), index=True)
    openid = db.Column(db.String(100), index=True)
    nodule_type = db.Column(db.String(50))

    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # bytes
    file_type = db.Column(db.String(50))  # pdf/image

    extracted_text = db.Column(db.Text)
    extracted_data = db.Column(db.JSON)

    status = db.Column(db.String(20), default='uploaded')  # uploaded/processed/deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'openid': self.openid,
            'nodule_type': self.nodule_type,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class BReport(db.Model):
    """B端报告表"""
    __tablename__ = 'b_reports'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('b_patients.id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('b_health_records.id'))

    report_code = db.Column(db.String(50), unique=True)

    # 报告状态：draft（草稿）/ published（已发布）/ archived（已归档）
    status = db.Column(db.String(20), default='draft')

    # AI生成的评估内容（可编辑）
    imaging_conclusion = db.Column(db.Text)  # 影像学评估结论
    imaging_risk_warning = db.Column(db.Text)  # 影像学风险提示
    medical_conclusion = db.Column(db.Text)  # 疾病史评估结论
    medical_risk_warning = db.Column(db.Text)  # 疾病史风险提示
    risk_score = db.Column(db.Integer)  # 风险评分（0-100）
    risk_level = db.Column(db.String(20))  # 风险等级（低危/中危/高危）

    # 审核信息
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 审核人
    reviewed_at = db.Column(db.DateTime)  # 审核时间
    review_notes = db.Column(db.Text)  # 审核备注

    # 旧字段（保留兼容性）
    recommendations_draft = db.Column(db.JSON)  # 草稿建议（按类别分组，管理师审核用）
    report_html = db.Column(db.Text)  # 最终打印报告（整合后的完整HTML）
    report_summary = db.Column(db.Text)

    # B端特有字段
    report_type = db.Column(db.String(20), default='professional')
    access_level = db.Column(db.String(20), default='b_only')
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    source_channel = db.Column(db.String(50), default='b_end')  # 报告来源：b_end/miniprogram
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'record_id': self.record_id,
            'report_code': self.report_code,

            # 报告状态
            'status': self.status,

            # AI评估内容
            'imaging_conclusion': self.imaging_conclusion,
            'imaging_risk_warning': self.imaging_risk_warning,
            'medical_conclusion': self.medical_conclusion,
            'medical_risk_warning': self.medical_risk_warning,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,

            # 审核信息
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if self.reviewed_at else None,
            'review_notes': self.review_notes,

            # 旧字段（兼容性）
            'recommendations_draft': self.recommendations_draft,
            'report_html': self.report_html,
            'report_summary': self.report_summary,

            'report_type': self.report_type,
            'access_level': self.access_level,
            'generated_by': self.generated_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class BFollowUpRecord(db.Model):
    """B端跟进记录表"""
    __tablename__ = 'b_follow_up_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('b_patients.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 跟进信息
    follow_up_type = db.Column(db.String(20))  # phone, wechat, visit, other
    follow_up_date = db.Column(db.Date)
    content = db.Column(db.Text)
    
    # 下次跟进计划
    next_follow_up_date = db.Column(db.Date)
    next_follow_up_action = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'manager_id': self.manager_id,
            'follow_up_type': self.follow_up_type,
            'follow_up_date': self.follow_up_date.strftime('%Y-%m-%d') if self.follow_up_date else None,
            'content': self.content,
            'next_follow_up_date': self.next_follow_up_date.strftime('%Y-%m-%d') if self.next_follow_up_date else None,
            'next_follow_up_action': self.next_follow_up_action,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


# ============================================
# C端专用表
# ============================================

class CPatient(db.Model):
    """C端患者/线索表（统一管理线索与客户生命周期）"""
    __tablename__ = 'c_patients'

    id = db.Column(db.Integer, primary_key=True)
    patient_code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20), unique=True)  # C端主要标识
    wechat_openid = db.Column(db.String(100), unique=True)
    wechat_unionid = db.Column(db.String(100))
    wechat_id = db.Column(db.String(50))  # 兼容旧字段

    # 基本信息（小程序问卷提交时填写）
    age = db.Column(db.Integer)  # 年龄
    gender = db.Column(db.String(10))  # 性别：男/女
    nodule_type = db.Column(db.String(20))  # 结节类型：breast/lung/thyroid等

    # 线索信息
    source_channel = db.Column(db.String(50), default='unknown')  # 公众号、短视频、线下活动等
    campaign_code = db.Column(db.String(50))  # 活动编号
    entry_url = db.Column(db.String(255))
    lead_status = db.Column(db.String(20), default='new')  # new/contacted/booked/reported/conversion/lost
    lead_stage_notes = db.Column(db.Text)
    assigned_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 生命周期时间
    first_visit_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity_at = db.Column(db.DateTime)

    # 客户状态
    status = db.Column(db.String(20), default='active')
    is_contacted = db.Column(db.Boolean, default=False)

    # 时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    manager = db.relationship('User', backref=db.backref('c_patients', lazy='dynamic'))
    records = db.relationship('CHealthRecord', backref='patient', lazy='dynamic')
    reports = db.relationship('CReport', backref='patient', lazy='dynamic')
    conversations = db.relationship('CConversation', backref='patient', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_code': self.patient_code,
            'name': self.name,
            'phone': self.phone,
            'age': self.age,
            'gender': self.gender,
            'nodule_type': self.nodule_type,
            'wechat_openid': self.wechat_openid,
            'wechat_id': self.wechat_id,
            'source_channel': self.source_channel,
            'campaign_code': self.campaign_code,
            'entry_url': self.entry_url,
            'lead_status': self.lead_status,
            'lead_stage_notes': self.lead_stage_notes,
            'assigned_manager_id': self.assigned_manager_id,
            'first_visit_at': self.first_visit_at.strftime('%Y-%m-%d %H:%M:%S') if self.first_visit_at else None,
            'last_activity_at': self.last_activity_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_activity_at else None,
            'status': self.status,
            'is_contacted': self.is_contacted,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class CHealthRecord(db.Model):
    """C端健康档案表"""
    __tablename__ = 'c_health_records'
    
    @staticmethod
    def _format_checkbox_value(value):
        """
        ISDoc
        @description 复用B端健康档案的checkbox格式化逻辑，兼容 {} / [] / {a,b} 等格式
        @param value 原始值
        @returns {str|None} 格式化后的字符串或None
        """
        return BHealthRecord._format_checkbox_value(value)
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('c_patients.id'), nullable=False)
    record_code = db.Column(db.String(50), unique=True)
    
    # 基本信息（通过AI对话收集或小程序问卷提交）
    age = db.Column(db.Integer)
    height = db.Column(db.Float)  # 身高(cm)
    weight = db.Column(db.Float)  # 体重(kg)
    phone = db.Column(db.String(20))  # 联系电话
    diabetes_history = db.Column(db.String(50))  # 糖尿病史
    gaofang_address = db.Column(db.String(255))  # 可接收膏方的收货地址
    birads_level = db.Column(db.Integer)
    family_history = db.Column(db.String(100))
    family_history_other = db.Column(db.String(200))  # 其他家族史
    symptoms = db.Column(db.String(200))
    symptoms_other = db.Column(db.String(200))  # 其他症状
    breast_symptoms_other = db.Column(db.String(200))  # 乳腺症状"其他"说明
    pain_level = db.Column(db.Integer)
    pain_type = db.Column(db.String(50))
    nodule_location = db.Column(db.String(50))
    nodule_size = db.Column(db.String(50))
    nodule_quantity = db.Column(db.String(20))  # 数量：单发/多发
    nodule_count = db.Column(db.String(20))  # 多发结节个数（当nodule_quantity为"多发"时填写）
    boundary_features = db.Column(db.String(100))
    internal_echo = db.Column(db.String(50))
    blood_flow_signal = db.Column(db.String(50))
    elasticity_score = db.Column(db.String(20))
    rhythm_type = db.Column(db.String(50))
    sleep_quality = db.Column(db.String(100))
    exam_history_type = db.Column(db.String(50))
    exercise_frequency = db.Column(db.String(50))
    
    # 发现时间（各结节类型）
    breast_discovery_date = db.Column(db.Date)  # 乳腺结节发现时间
    lung_discovery_date = db.Column(db.Date)    # 肺结节发现时间
    thyroid_discovery_date = db.Column(db.Date) # 甲状腺结节发现时间
    
    # 疾病史和用药史
    breast_disease_history = db.Column(db.String(200))  # 乳腺疾病史（多选，逗号分隔）
    breast_disease_history_other = db.Column(db.String(200))  # 其他基础疾病史
    medication_history = db.Column(db.String(200))  # 药物使用史（多选，逗号分隔）
    medication_other = db.Column(db.String(200))  # 其他药物使用
    breast_medication_history = db.Column(db.String(200))  # 乳腺用药史（多选，逗号分隔）
    breast_medication_other = db.Column(db.String(200))  # 乳腺用药史"其他"说明
    
    # C端特有字段
    data_completeness = db.Column(db.String(20), default='partial')
    conversation_id = db.Column(db.Integer, db.ForeignKey('c_conversations.id'))
    status = db.Column(db.String(20), default='completed')
    
    # === 中医/舌诊结果（外部插件/外部公司返回）===
    tongue_check_result_id = db.Column(db.String(50))  # 外部检测结果ID（插件resultId等）
    tongue_result_raw = db.Column(db.Text)  # 原始结果JSON（字符串化）
    tongue_result_summary = db.Column(db.Text)  # 摘要（用于后续写入报告）
    tongue_checked_at = db.Column(db.DateTime)  # 舌诊完成时间

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'record_code': self.record_code,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'phone': self.phone,
            'diabetes_history': self.diabetes_history,
            'gaofang_address': self.gaofang_address,
            'birads_level': self.birads_level,
            'family_history': self._format_checkbox_value(self.family_history),
            'family_history_other': self.family_history_other,
            'symptoms': self.symptoms,
            'symptoms_other': self.symptoms_other,
            'breast_symptoms_other': self.breast_symptoms_other,
            'pain_level': self.pain_level,
            'pain_type': self.pain_type,
            'nodule_location': self.nodule_location,
            'nodule_size': self.nodule_size,
            'nodule_quantity': self.nodule_quantity,
            'nodule_count': self.nodule_count,
            'boundary_features': self.boundary_features,
            'internal_echo': self.internal_echo,
            'blood_flow_signal': self.blood_flow_signal,
            'elasticity_score': self.elasticity_score,
            'rhythm_type': self.rhythm_type,
            'sleep_quality': self.sleep_quality,
            'exam_history_type': self.exam_history_type,
            'exercise_frequency': self.exercise_frequency,
            # 发现时间
            'breast_discovery_date': self.breast_discovery_date.strftime('%Y-%m-%d') if self.breast_discovery_date else None,
            'lung_discovery_date': self.lung_discovery_date.strftime('%Y-%m-%d') if self.lung_discovery_date else None,
            'thyroid_discovery_date': self.thyroid_discovery_date.strftime('%Y-%m-%d') if self.thyroid_discovery_date else None,
            # 疾病史和用药史
            'breast_disease_history': self._format_checkbox_value(self.breast_disease_history),
            'breast_disease_history_other': self.breast_disease_history_other,
            'medication_history': self._format_checkbox_value(self.medication_history),
            'medication_other': self.medication_other,
            'breast_medication_history': self._format_checkbox_value(self.breast_medication_history),
            'breast_medication_other': self.breast_medication_other,
            # 舌诊结果
            'tongue_check_result_id': self.tongue_check_result_id,
            'tongue_result_summary': self.tongue_result_summary,
            'tongue_checked_at': self.tongue_checked_at.strftime('%Y-%m-%d %H:%M:%S') if self.tongue_checked_at else None,
            'data_completeness': self.data_completeness,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class CReport(db.Model):
    """C端报告表"""
    __tablename__ = 'c_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('c_patients.id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('c_health_records.id'))
    conversation_id = db.Column(db.Integer, db.ForeignKey('c_conversations.id'))

    report_code = db.Column(db.String(50), unique=True)
    report_html = db.Column(db.Text)
    report_summary = db.Column(db.Text)
    risk_level = db.Column(db.String(20))
    # 审核用字段（与B端报告保持一致）
    imaging_conclusion = db.Column(db.Text)  # 影像学评估结论（总体评估与随访建议）
    imaging_risk_warning = db.Column(db.Text)  # 影像学风险提示

    # C端特有字段
    report_type = db.Column(db.String(20), default='patient_friendly')
    access_level = db.Column(db.String(20), default='c_accessible')
    download_token = db.Column(db.String(100))
    status = db.Column(db.String(20), default='generated')  # generated/shared/downloaded
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_download_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'record_id': self.record_id,
            'conversation_id': self.conversation_id,
            'report_code': self.report_code,
            'risk_level': self.risk_level,
            'imaging_conclusion': self.imaging_conclusion,
            'imaging_risk_warning': self.imaging_risk_warning,
            'report_type': self.report_type,
            'access_level': self.access_level,
            'status': self.status,
            'generated_at': self.generated_at.strftime('%Y-%m-%d %H:%M:%S') if self.generated_at else None,
            'last_download_at': self.last_download_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_download_at else None
        }


class CConversation(db.Model):
    """C端AI对话会话表"""
    __tablename__ = 'c_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('c_patients.id'))  # 线索ID（统一使用lead_id）
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    
    # 会话状态
    status = db.Column(db.String(20), default='active')  # active, completed, failed
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    last_message_at = db.Column(db.DateTime)
    channel = db.Column(db.String(20), default='web')  # web, wechat, app
    
    # 收集到的信息（JSON格式）
    collected_data = db.Column(db.JSON)
    
    # 会话摘要
    summary = db.Column(db.Text)
    
    # 关键词（用于搜索）
    keywords = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系（不定义 backref，避免与数据库的 patient_id 字段冲突）
    messages = db.relationship('CMessage', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    report = db.relationship('CReport', backref='conversation', uselist=False)
    
    # 兼容属性（旧代码可能使用 patient_id）
    @property
    def patient_id(self):
        return self.lead_id
    
    @patient_id.setter
    def patient_id(self, value):
        self.lead_id = value
    
    @property
    def patient(self):
        """获取关联的患者对象"""
        if self.lead_id:
            return CPatient.query.get(self.lead_id)
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_id': self.lead_id,
            'patient_id': self.lead_id,  # 兼容性
            'session_id': self.session_id,
            'status': self.status,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'last_message_at': self.last_message_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_message_at else None,
            'channel': self.channel,
            'collected_data': self.collected_data,
            'summary': self.summary,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class CMessage(db.Model):
    """C端对话消息表"""
    __tablename__ = 'c_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('c_conversations.id'), nullable=False)
    
    # 消息信息
    role = db.Column(db.String(20))  # user/assistant/system
    content = db.Column(db.Text)
    intent = db.Column(db.String(50))  # 意图识别
    channel = db.Column(db.String(20))  # wechat/h5/app
    
    # 元数据（extra_data 用于存储附加信息）
    extra_data = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'intent': self.intent,
            'channel': self.channel,
            'extra_data': self.extra_data,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
