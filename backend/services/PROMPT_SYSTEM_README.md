# 提示词管理系统使用说明

## 📋 系统概述

本系统实现了统一的LLM提示词管理，支持**7种结节类型**的**2类提示词**（影像学评估 + 疾病史风险评估）。

---

## 🎯 提示词类型

### 1. imaging（影像学评估）
- **依据**：影像学特征（BI-RADS/Lung-RADS/TI-RADS分级、结节大小、边界、回声、血流等）
- **输出格式**：
```json
{
  "conclusion": "400-500字的总体评估与随访建议",
  "risk_warning": "300字的风险提示"
}
```

### 2. western_medical（疾病史风险评估）
- **依据**：疾病史和风险因素（病史、家族史、吸烟史、辐射史、糖尿病等）
- **输出格式**：
```json
{
  "conclusion": "400-500字的总体评估与随访建议",
  "risk_warning": "300字的风险提示",
  "risk_score": 75,  // 0-100分
  "risk_level": "高危"  // 低危/中危/高危
}
```

---

## 📂 文件结构

```
backend/
├── prompt_config.py          # 提示词配置文件（统一管理14个提示词）
├── services/
│   └── llm_service.py        # LLM服务（使用western_medical提示词）
└── routes/
    └── llm_helpers.py        # LLM辅助函数（使用imaging提示词）
```

---

## 🔧 使用方法

### 1. 获取提示词模板

```python
from prompt_config import get_prompt_template, format_prompt

# 获取乳腺结节的影像学评估提示词
template = get_prompt_template('breast', 'imaging')

# 获取肺结节的疾病史风险评估提示词
template = get_prompt_template('lung', 'western_medical')
```

### 2. 格式化提示词

```python
# 准备患者数据
prompt_vars = {
    'age': 45,
    'birads_level': '4A',
    'nodule_size': '1.2cm',
    'boundary_features': '边界不清',
    # ... 其他字段
}

# 格式化提示词
prompt = format_prompt(template, **prompt_vars)
```

### 3. 解析JSON响应

```python
from routes.llm_helpers import parse_json_response

# 调用LLM
response = llm_generator._call_llm_api(prompt)

# 解析JSON响应
result = parse_json_response(response)

# 使用结果
conclusion = result['conclusion']
risk_warning = result['risk_warning']
```

---

## 🌍 支持的结节类型

| 结节类型 | 代码标识 | imaging提示词 | western_medical提示词 |
|---------|---------|--------------|---------------------|
| 乳腺结节 | `breast` | ✅ | ✅ |
| 肺部结节 | `lung` | ✅ | ✅ |
| 甲状腺结节 | `thyroid` | ✅ | ✅ |
| 乳腺+肺部 | `breast_lung` | ✅ | ✅ |
| 乳腺+甲状腺 | `breast_thyroid` | ✅ | ✅ |
| 肺部+甲状腺 | `lung_thyroid` | ✅ | ✅ |
| 三合一 | `triple` | ✅ | ✅ |

---

## 📝 提示词字段说明

### 通用字段
- `age`: 年龄
- `height`: 身高
- `weight`: 体重
- `bmi_info`: BMI信息

### 乳腺相关字段
- `birads_level`: BI-RADS分级
- `nodule_size`: 结节大小
- `nodule_location`: 结节位置
- `boundary_features`: 边界特征
- `internal_echo`: 内部回声
- `blood_flow_signal`: 血流信号
- `elasticity_score`: 弹性评分
- `hyperplasia`: 乳腺增生病史
- `fibroadenoma`: 乳腺纤维瘤病史
- `cyst`: 乳腺囊肿病史
- `inflammation`: 乳腺炎病史
- `cancer_history`: 乳腺癌病史

### 肺部相关字段
- `lung_rads_level`: Lung-RADS分级
- `lung_nodule_size`: 结节大小
- `lung_nodule_location`: 结节位置
- `lung_boundary_features`: 边界特征
- `lung_internal_density`: 内部密度
- `lung_calcification`: 钙化情况
- `lung_nodule_count`: 结节数量
- `smoking_history`: 吸烟史
- `dust_exposure`: 粉尘接触史
- `lung_disease_history`: 肺部疾病史
- `lung_cancer_history`: 肺癌病史

### 甲状腺相关字段
- `tirads_level`: TI-RADS分级
- `thyroid_nodule_size`: 结节大小
- `thyroid_nodule_location`: 结节位置
- `thyroid_boundary_features`: 边界特征
- `thyroid_internal_echo`: 内部回声
- `thyroid_blood_flow_signal`: 血流信号
- `thyroid_calcification`: 钙化情况
- `thyroid_nodule_count`: 结节数量
- `hyperthyroidism_history`: 甲亢病史
- `hypothyroidism_history`: 甲减病史
- `hashimoto_history`: 桥本甲状腺炎病史
- `thyroid_cancer_history`: 甲状腺癌病史

### 其他风险因素
- `diabetes`: 糖尿病
- `radiation_exposure`: 辐射暴露史
- `autoimmune`: 自身免疫疾病
- `medication`: 药物使用史
- `tumor_marker`: 肿瘤标志物检查
- `hereditary`: 遗传性病史
- `contraceptive_risk`: 避孕药物风险档位
- `smoking_risk`: 吸烟风险档位
- `diabetes_control`: 糖尿病控制档位

---

## ⚠️ 注意事项

1. **JSON格式严格**：所有提示词要求LLM输出纯JSON格式，不能有markdown标记
2. **字数要求**：
   - `conclusion`: 400-500字
   - `risk_warning`: 300字左右
3. **字段验证**：系统会自动验证必需字段，如果缺失会抛出异常
4. **默认值**：所有字段都有默认值，缺失字段会自动填充

---

## 🔄 扩展新结节类型

如需添加新的结节类型，只需在 `prompt_config.py` 中添加：

```python
PROMPTS = {
    # ... 现有类型

    'new_nodule_type': {
        'imaging': """...""",
        'western_medical': """..."""
    }
}
```

---

## 📊 系统优势

1. ✅ **统一管理**：14个提示词集中在一个文件中
2. ✅ **易于维护**：修改提示词无需修改业务代码
3. ✅ **格式统一**：所有提示词输出JSON格式
4. ✅ **类型安全**：自动验证字段和数据类型
5. ✅ **可扩展**：添加新结节类型只需修改配置文件

---

## 🎉 升级说明

### 从旧系统迁移

**旧系统**：
```python
# 旧代码：硬编码提示词
prompt = f"你是一位医生，{patient_data}..."
conclusion = llm.call(prompt)  # 返回纯文本
```

**新系统**：
```python
# 新代码：使用统一提示词管理
template = get_prompt_template('breast', 'imaging')
prompt = format_prompt(template, **patient_data)
response = llm.call(prompt)
result = parse_json_response(response)  # 返回结构化JSON
```

---

## 📞 技术支持

如有问题，请参考：
- `prompt_config.py` - 查看所有提示词模板
- `llm_service.py` - 查看western_medical使用示例
- `llm_helpers.py` - 查看imaging使用示例
