# 报告模板与提示词统一管理系统设计方案

## 一、问题分析

### 当前问题
1. **6个独立模板**：`comprehensive_report.html`（乳腺）、`fei_report.html`（肺）、`jia_report.html`（甲状腺）、`ru_fei.html`（乳腺+肺）、`ru_jia.html`（乳腺+甲状腺）、`jia_fei_report.html`（甲状腺+肺）
2. **模板结构不统一**：第一部分的前三部分（基本信息、影像学特征、既往病史）来自表单，但第（四）部分和第二部分内容不同
3. **提示词硬编码**：`llm_service.py` 中提示词只针对乳腺结节
4. **字段映射不完整**：`b_patient_management.py` 只传递乳腺字段，没有根据结节类型传递对应字段

### 模板结构分析

#### 共同部分（所有模板都有）
- **封面页**：患者姓名、标题
- **寄语页**：固定内容
- **第一部分 - 健康风险评估**：
  - （一）基本信息：姓名、性别、年龄、身高、体重、电话
  - （二）影像学特征：**根据结节类型不同**（乳腺/肺/甲状腺）
  - （三）既往病史与风险分层：**根据结节类型不同**
  - （四）动态风险评级：**内容不同**
  - （五）医学监测矩阵：**内容不同**
  - （六）监测频率分层管理表：**内容不同**
  - （七）动态调整机制：**内容不同**
  - （八）分层监测策略：**内容不同**
  - （九）分级管理要点：**内容不同**

#### 第二部分 - 健康管理建议（所有模板都有）
- （一）饮食建议：**根据结节类型不同**
- （二）运动建议：**根据结节类型不同**
- （三）情绪管理：**根据结节类型不同**
- （四）生活方式：**根据结节类型不同**

#### LLM生成内容位置
- **（二）影像学特征** 后面的"影像学分析结论"框
- **（三）既往病史** 后面的"综合分析结论"框

## 二、统一方案设计

### 方案1：模板继承 + 动态包含（推荐）

#### 架构设计
```
base_report_template.html（基础模板）
├── 封面页（固定）
├── 寄语页（固定）
├── 第一部分 - 健康风险评估
│   ├── （一）基本信息（固定，从表单填充）
│   ├── （二）影像学特征（动态包含）
│   │   ├── _breast_imaging_section.html
│   │   ├── _lung_imaging_section.html
│   │   └── _thyroid_imaging_section.html
│   ├── （三）既往病史（动态包含）
│   │   ├── _breast_history_section.html
│   │   ├── _lung_history_section.html
│   │   └── _thyroid_history_section.html
│   └── （四）~（九）部分（动态包含）
│       ├── _breast_risk_sections.html
│       ├── _lung_risk_sections.html
│       └── _thyroid_risk_sections.html
└── 第二部分 - 健康管理建议（动态包含）
    ├── _breast_lifestyle_section.html
    ├── _lung_lifestyle_section.html
    └── _thyroid_lifestyle_section.html
```

#### 实现步骤
1. 创建 `base_report_template.html` 基础模板
2. 将6个模板的公共部分提取到基础模板
3. 将结节类型特定的部分提取为独立的section文件
4. 根据 `patient.nodule_type` 动态包含对应的section

### 方案2：配置驱动模板（备选）

使用配置文件定义每个结节类型的模板结构，然后动态渲染。

## 三、提示词管理系统设计

### 提示词结构
```python
class PromptManager:
    """提示词管理器"""
    
    def get_prompt_config(self, nodule_type: str) -> Dict:
        """根据结节类型获取提示词配置"""
        
    def build_imaging_prompt(self, patient_data: Dict, nodule_type: str) -> str:
        """构建影像学分析提示词"""
        
    def build_comprehensive_prompt(self, patient_data: Dict, nodule_type: str) -> str:
        """构建综合分析提示词"""
```

### 提示词内容
1. **影像学分析提示词**（填写到（二）部分后面）：
   - 根据结节类型传递对应的影像学字段
   - 生成"总体评估与随访建议"、"风险提示"、"中医简要分析"

2. **综合分析提示词**（填写到（三）部分后面）：
   - 根据结节类型传递对应的病史字段
   - 生成"总体评估与随访建议"、"风险提示"

## 四、字段映射系统

### 字段映射表
```python
NODULE_FIELD_MAPPING = {
    'breast': {
        'imaging': ['birads_level', 'nodule_location', 'nodule_size', 
                   'boundary_features', 'internal_echo', 'blood_flow_signal', 
                   'elasticity_score', 'symptoms'],
        'history': ['breast_disease_history', 'family_genetic_history', 
                   'previous_biopsy_history', 'contraceptive_risk_level', 
                   'smoking_risk_level', 'diabetes_control_level']
    },
    'lung': {
        'imaging': ['lung_rads_level', 'lung_nodule_location', 'lung_nodule_size',
                   'lung_boundary_features', 'lung_internal_echo', 
                   'lung_blood_flow_signal', 'lung_symptoms'],
        'history': ['pneumonia_history', 'tb_history', 'copd_history',
                   'fibrosis_history', 'lung_cancer_history', 
                   'hereditary_lung_history']
    },
    'thyroid': {
        'imaging': ['tirads_level', 'thyroid_nodule_location', 'thyroid_nodule_size',
                   'thyroid_boundary_features', 'thyroid_internal_echo',
                   'thyroid_blood_flow_signal', 'thyroid_symptoms'],
        'history': ['hyperthyroidism_history', 'hypothyroidism_history',
                   'hashimoto_history', 'thyroid_cancer_history',
                   'hereditary_thyroid_history']
    }
}
```

## 五、报告生成流程

### 新流程
```
1. 获取患者数据和结节类型
   ↓
2. 根据结节类型选择模板配置
   ↓
3. 提取表单数据（使用字段映射）
   ↓
4. 渲染模板第一部分（一）~（三）（填充表单数据）
   ↓
5. 调用LLM生成影像学分析结论（传递影像学字段）
   ↓
6. 将LLM结果插入到（二）部分后面
   ↓
7. 调用LLM生成综合分析结论（传递病史字段）
   ↓
8. 将LLM结果插入到（三）部分后面
   ↓
9. 渲染模板第一部分（四）~（九）（根据结节类型）
   ↓
10. 渲染模板第二部分（根据结节类型）
   ↓
11. 合并生成最终HTML报告
```

## 六、实施建议

### 阶段1：创建基础架构
1. 创建 `PromptManager` 类
2. 创建字段映射配置
3. 创建基础模板结构

### 阶段2：重构模板系统
1. 提取公共部分到基础模板
2. 将结节特定部分提取为section文件
3. 实现动态包含逻辑

### 阶段3：重构报告生成
1. 修改 `b_patient_management.py` 的 `generate_patient_report`
2. 使用模板系统替代LLM生成完整HTML
3. LLM只生成分析结论片段

### 阶段4：测试与优化
1. 测试6种结节类型的报告生成
2. 优化提示词质量
3. 优化模板渲染性能








