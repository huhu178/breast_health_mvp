# 小程序接口重构方案

## 问题
小程序接口 (`miniprogram_routes.py`) 重复实现了B端的业务逻辑，导致：
1. B端更新了字段处理逻辑（多结节场景），小程序没有同步
2. 代码重复，维护困难
3. 可能导致数据不一致

## 解决方案
让小程序接口直接调用B端的业务逻辑函数，而不是重复实现。

## 重构步骤

### 1. 提取B端核心业务逻辑为独立函数

将以下函数的业务逻辑提取为独立函数（不包含路由装饰器和登录验证）：

- `create_patient()` → `_create_b_patient(data, manager_id=None)`
- `create_patient_record()` → `_create_b_patient_record(patient_id, data, files=None, user_id=None)`
- `generate_patient_report()` → `_generate_b_patient_report(patient_id, record_id, patient_type='b_end')`

### 2. 修改小程序接口

让 `miniprogram_routes.py` 的 `submit_questionnaire()` 调用这些函数：

```python
# 1. 创建/查找患者
patient = _create_or_get_b_patient(phone, name, normalized_data, openid)

# 2. 创建档案（复用B端逻辑）
record = _create_b_patient_record(patient.id, normalized_data, files=None, user_id=None)

# 3. 生成报告（复用B端逻辑）
report = _generate_b_patient_report(patient.id, record.id)
```

### 3. 修改B端路由

让B端路由也调用这些提取的函数，而不是直接实现逻辑。

## 好处

1. **代码复用**：小程序和B端使用同一套业务逻辑
2. **同步更新**：B端更新字段处理逻辑时，小程序自动同步
3. **数据一致**：确保小程序和B端的数据处理完全一致
4. **易于维护**：只需在一个地方修改业务逻辑

## 注意事项

1. **登录验证**：
   - B端路由：需要 `@login_required`，使用 `g.user_id`
   - 小程序接口：不需要登录，`user_id` 传 `None`

2. **字段映射**：
   - 小程序提交的数据格式需要与B端一致
   - 可以使用 `normalize_miniprogram_data()` 进行格式转换

3. **文件上传**：
   - 小程序暂时不支持文件上传，`files` 传 `None`

