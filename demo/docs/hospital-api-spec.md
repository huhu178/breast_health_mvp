# 医院场景多结节健康管理系统接口清单 V1.0

## 1. 文档目的

本文件定义医院场景一期需要的主要接口清单，用于前后端开发对齐。字段命名可根据现有后端风格微调，但业务语义应保持一致。

## 2. 通用约定

基础返回格式：

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```

分页参数：

- `page`
- `page_size`

权限原则：

- 所有 B 端接口需要登录。
- 接口层必须按角色过滤数据范围。
- 前端隐藏按钮不能替代后端权限控制。

## 3. 认证与用户

### 3.1 登录

`POST /api/auth/login`

请求：

```json
{
  "username": "doctor01",
  "password": "password"
}
```

返回：

```json
{
  "user": {
    "id": 1,
    "real_name": "张医生",
    "role": "doctor",
    "department_id": 1
  }
}
```

### 3.2 当前用户

`GET /api/auth/me`

返回当前登录用户、角色、科室和菜单权限。

## 4. 基础字典

### 4.1 科室列表

`GET /api/hospital/departments`

用途：患者建档、用户配置、筛选项。

### 4.2 医生列表

`GET /api/hospital/doctors?department_id=1`

用途：患者建档选择主要负责医生。

### 4.3 管理人员列表

`GET /api/hospital/managers`

用途：患者分配健康管理师/医生助手。

## 5. 患者管理

### 5.1 患者列表

`GET /api/hospital/patients`

查询参数：

- `keyword`
- `department_id`
- `doctor_id`
- `manager_id`
- `risk_level`
- `status`
- `nodule_type`
- `page`
- `page_size`

返回重点字段：

- 患者基础信息
- 所属科室
- 主要负责医生
- 负责管理人员
- 风险等级
- 最近随访时间
- 下次随访时间

### 5.2 患者详情

`GET /api/hospital/patients/{patient_id}`

返回聚合信息：

- 患者基础信息
- 结节列表
- 影像报告
- 健康报告
- 风险评估
- 报告随访建议
- 随访计划
- 随访任务
- 操作记录摘要

### 5.3 新增患者

`POST /api/hospital/patients`

请求重点字段：

```json
{
  "name": "李某",
  "gender": "女",
  "age": 45,
  "phone": "13800000000",
  "department_id": 1,
  "primary_doctor_id": 10,
  "manager_id": 20,
  "source_channel": "manual"
}
```

### 5.4 编辑患者

`PUT /api/hospital/patients/{patient_id}`

权限：健康管理师、医生助手、系统管理员可配置。

## 6. 多结节管理

### 6.1 新增结节

`POST /api/hospital/patients/{patient_id}/nodules`

请求重点字段：

```json
{
  "nodule_type": "breast",
  "body_part": "乳腺",
  "side": "左侧",
  "location": "外上象限",
  "size": "8mm",
  "quantity": 1,
  "grade_type": "BI-RADS",
  "grade_value": "3",
  "imaging_features": "边界清晰"
}
```

### 6.2 编辑结节

`PUT /api/hospital/nodules/{nodule_id}`

### 6.3 删除/作废结节

`DELETE /api/hospital/nodules/{nodule_id}`

建议软删除或作废，不做物理删除。

## 7. 影像报告

### 7.1 上传影像报告

`POST /api/hospital/patients/{patient_id}/imaging-reports`

类型：`multipart/form-data`

字段：

- `file`
- `nodule_id`
- `report_type`
- `exam_date`
- `summary`
- `structured_data`

### 7.2 影像报告列表

`GET /api/hospital/patients/{patient_id}/imaging-reports`

### 7.3 作废影像报告

`DELETE /api/hospital/imaging-reports/{report_id}`

## 8. 健康报告

### 8.1 生成报告草稿

`POST /api/hospital/patients/{patient_id}/health-reports/generate`

### 8.2 报告列表

`GET /api/hospital/health-reports`

查询参数：

- `status`
- `risk_level`
- `department_id`
- `doctor_id`
- `keyword`

### 8.3 报告详情

`GET /api/hospital/health-reports/{report_id}`

### 8.4 审核归档报告

`POST /api/hospital/health-reports/{report_id}/finalize`

说明：归档后不可直接覆盖编辑。

## 9. 报告随访建议

### 9.1 保存草稿

`POST /api/hospital/health-reports/{report_id}/followup-advice/draft`

请求：

```json
{
  "advice_content": "建议6个月后复查乳腺超声，期间按计划随访。",
  "suggested_next_followup_at": "2026-12-25"
}
```

### 9.2 提交建议

`POST /api/hospital/health-reports/{report_id}/followup-advice/submit`

权限：医生。

### 9.3 获取建议

`GET /api/hospital/health-reports/{report_id}/followup-advice`

## 10. 随访计划

### 10.1 推荐随访计划

`POST /api/hospital/patients/{patient_id}/followup-plans/recommend`

返回：

- 推荐计划
- 推荐依据
- 匹配规则
- 建议节点

### 10.2 创建随访计划

`POST /api/hospital/patients/{patient_id}/followup-plans`

### 10.3 调整随访计划

`PUT /api/hospital/followup-plans/{plan_id}`

请求必须包含：

- `adjust_reason`

### 10.4 随访计划详情

`GET /api/hospital/followup-plans/{plan_id}`

## 11. 随访任务

### 11.1 任务列表

`GET /api/hospital/followup-tasks`

查询参数：

- `status`
- `risk_level`
- `patient_id`
- `manager_id`
- `date_from`
- `date_to`

### 11.2 创建任务

`POST /api/hospital/followup-tasks`

### 11.3 生成患者端入口

`POST /api/hospital/followup-tasks/{task_id}/checkin-link`

返回：

- 小程序路径
- 公开链接
- 有效期

### 11.4 执行/关闭任务

`POST /api/hospital/followup-tasks/{task_id}/complete`

## 12. 患者端小程序/公开链接

### 12.1 获取随访任务

公开链接：

`GET /api/followup/checkin/{task_code}`

小程序：

`GET /api/miniprogram/followup/tasks/{task_code}`

返回本次随访所需字段，不返回完整患者隐私信息。

### 12.2 提交随访反馈

公开链接：

`POST /api/followup/checkin/{task_code}`

小程序：

`POST /api/miniprogram/followup/tasks/{task_code}/submit`

请求：

```json
{
  "checkin_type": "symptom_checkin",
  "content_text": "症状稳定，已完成复查。",
  "image_urls": ["uploads/miniprogram/followup/xxx.jpg"],
  "uploaded_files": [
    {
      "upload_id": 1,
      "file_name": "复查报告.jpg",
      "file_type": "image",
      "file_path": "uploads/miniprogram/followup/xxx.jpg"
    }
  ],
  "structured_data": {},
  "analyze": true
}
```

### 12.3 上传复查资料

`POST /api/miniprogram/followup/tasks/{task_code}/files`

表单字段：

- `file`: PDF/JPG/PNG/WebP，最大 20MB
- `phone`: 可选
- `openid`: 可选

返回：

```json
{
  "upload_id": 1,
  "file_name": "复查报告.jpg",
  "file_type": "image",
  "file_size": 12345,
  "file_path": "uploads/miniprogram/followup/xxx.jpg",
  "task_code": "FU..."
}
```

## 13. 医生工作台

### 13.1 医生概览

`GET /api/hospital/doctor-workbench/summary`

返回：

- 我的患者数
- 待填写建议数
- 高风险患者数
- 近期复查患者数

### 13.2 我的患者

`GET /api/hospital/doctor-workbench/patients`

数据范围：`primary_doctor_id` 为当前医生。

### 13.3 待填写建议

`GET /api/hospital/doctor-workbench/pending-advice`

## 14. 科室主任看板

### 14.1 科室概览

`GET /api/hospital/department-dashboard/summary`

数据范围：当前主任所属科室。

返回：

- 患者总数
- 本月新增
- 高/中/低风险分布
- 随访完成率
- 超期随访数
- 待报告/待复核数

### 14.2 医生统计

`GET /api/hospital/department-dashboard/doctors`

### 14.3 异常患者

`GET /api/hospital/department-dashboard/abnormal-patients`

## 15. 知识库规则

### 15.1 规则列表

`GET /api/hospital/followup-rules`

### 15.2 启用/停用规则

`POST /api/hospital/followup-rules/{rule_id}/toggle`

### 15.3 更新规则

`PUT /api/hospital/followup-rules/{rule_id}`

## 16. 操作日志

### 16.1 患者操作日志

`GET /api/hospital/patients/{patient_id}/operation-logs`

返回患者关键操作记录。
