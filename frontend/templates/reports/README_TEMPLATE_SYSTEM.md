# 统一结节报告模板系统说明

## 📁 文件结构

```
frontend/templates/reports/
├── unified_nodule_report.html      # 主模板（100行）
└── sections/                        # 组件目录
    ├── _common_header.html          # 公共头部（封面+寄语）
    ├── _common_footer.html          # 公共尾部（建议+免责声明）
    ├── _breast_section.html         # 乳腺结节专用
    ├── _lung_section.html           # 肺结节专用
    └── _thyroid_section.html        # 甲状腺结节专用
```

## 🎯 核心设计理念

**一个主模板 + 动态组件加载 = 支持所有结节类型组合**

根据 `nodule_types` 字段自动选择对应的section：
- `nodule_types='breast'` → 只显示乳腺部分
- `nodule_types='lung'` → 只显示肺部分
- `nodule_types='thyroid'` → 只显示甲状腺部分
- `nodule_types='breast,lung'` → 显示乳腺+肺两部分
- `nodule_types='breast,lung,thyroid'` → 显示全部三部分

## 🔧 后端使用方法

### 方法1：使用统一模板（推荐）

```python
from flask import render_template

# 获取患者档案
record = BHealthRecord.query.get(record_id)

# 一行代码渲染任意组合
report_html = render_template(
    'reports/unified_nodule_report.html',
    nodule_types=record.nodule_types,  # 例如: 'breast,lung'
    patient_name=patient.name,
    patient_age=record.age,
    # ... 其他字段
)
```

### 方法2：向后兼容（仍然可用）

```python
# 如果不传nodule_types，默认显示乳腺（向后兼容）
report_html = render_template(
    'reports/unified_nodule_report.html',
    patient_name=patient.name,
    birads_level=record.birads_level,
    # ... 乳腺字段
)
```

## 📋 必需字段清单

### 公共字段（所有报告必需）
- `patient_name` - 患者姓名
- `patient_age` - 年龄
- `patient_gender` - 性别
- `report_code` - 报告编号
- `report_date` - 报告日期
- `nodule_types` - 结节类型（可选，默认'breast'）

### 乳腺结节字段
- `birads_level` - BI-RADS分级
- `nodule_location` - 结节位置
- `nodule_size` - 结节大小
- `boundary_features` - 边界特征
- `internal_echo` - 内部回声
- `blood_flow_signal` - 血流信号
- `elasticity_score` - 弹性评分
- `breast_hyperplasia_history` - 乳腺增生病史
- `breast_cancer_history` - 乳腺癌病史
- ...（其他乳腺字段）

### 肺结节字段
- `lung_rads_level` - Lung-RADS分级
- `lung_nodule_location` - 结节位置
- `lung_nodule_size` - 结节大小
- `lung_nodule_type` - 结节类型（实性/磨玻璃）
- `lung_pneumonia_history` - 肺炎病史
- `lung_cancer_history` - 肺癌病史
- ...（其他肺部字段）

### 甲状腺结节字段
- `thyroid_tirads_level` - TI-RADS分级
- `thyroid_nodule_location` - 结节位置
- `thyroid_nodule_size` - 结节大小
- `thyroid_hyperthyroidism_history` - 甲亢病史
- `thyroid_cancer_history` - 甲状腺癌病史
- ...（其他甲状腺字段）

## 💡 使用示例

### 示例1：纯乳腺结节报告
```python
render_template(
    'reports/unified_nodule_report.html',
    nodule_types='breast',
    patient_name='张女士',
    patient_age=45,
    birads_level='3',
    nodule_size='8mm',
    # ...
)
```

### 示例2：乳腺+肺双结节报告
```python
render_template(
    'reports/unified_nodule_report.html',
    nodule_types='breast,lung',
    patient_name='李女士',
    patient_age=52,
    # 乳腺字段
    birads_level='3',
    nodule_size='10mm',
    # 肺部字段
    lung_rads_level='2',
    lung_nodule_size='5mm',
    # ...
)
```

### 示例3：三结节报告
```python
render_template(
    'reports/unified_nodule_report.html',
    nodule_types='breast,lung,thyroid',
    patient_name='王女士',
    patient_age=48,
    # 乳腺字段
    birads_level='3',
    # 肺部字段
    lung_rads_level='2',
    # 甲状腺字段
    thyroid_tirads_level='3',
    # ...
)
```

## 🔄 从旧模板迁移

如果您之前使用 `comprehensive_report.html`：

```python
# 旧代码
render_template('reports/comprehensive_report.html', ...)

# 新代码（只需改模板名）
render_template('reports/unified_nodule_report.html', nodule_types='breast', ...)
```

## 📊 自动标题生成

模板会根据 `nodule_types` 自动生成报告标题：
- `'breast'` → "乳腺结节健康管理方案"
- `'lung'` → "肺结节健康管理方案"
- `'thyroid'` → "甲状腺结节健康管理方案"
- `'breast,lung'` → "乳腺合并肺结节健康管理方案"
- `'breast,lung,thyroid'` → "多器官（乳腺+肺+甲状腺）结节健康管理方案"

## ⚙️ 扩展性

### 新增结节类型
1. 在 `sections/` 目录创建新的section文件（如 `_liver_section.html`）
2. 在 `unified_nodule_report.html` 添加判断逻辑：
   ```jinja2
   {% if 'liver' in types_list %}
       {% include 'reports/sections/_liver_section.html' %}
   {% endif %}
   ```
3. 完成！无需修改其他代码

## 🐛 故障排查

### 问题：报告显示空白
- 检查是否传入了 `nodule_types` 字段
- 检查字段名拼写是否正确

### 问题：section未显示
- 确认 `nodule_types` 值格式正确（如 `'breast,lung'`，不能有空格）
- 检查对应的section文件是否存在

### 问题：PDF导出失败
- 确认所有必需的CSS样式已包含在 `_common_header.html` 中

## 📞 技术支持

如有问题，请查看：
- 数据库模型：`backend/models.py`
- 后端路由：`backend/routes/b_report_management.py`
- 示例数据：`backend/test_data/`
