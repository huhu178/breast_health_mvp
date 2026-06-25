# 医院场景多结节健康管理系统数据模型设计 V1.0

## 1. 文档目的

本文件描述医院场景一期需要的数据对象、核心字段和关系，用于指导数据库设计、接口设计和前端页面字段。

## 2. 设计原则

1. 一个患者归属一个科室。
2. 一个患者有一个主要负责医生。
3. 一个患者可有多个结节/病灶。
4. 医生只填写报告随访建议。
5. 科室主任只查看本科室数据。
6. 患者端小程序和公开链接提交的数据统一进入随访任务和随访记录。

## 3. 核心实体关系

```text
Department 科室
  └─ User 医生/科室主任/健康管理师/医生助手

Patient 患者
  ├─ Department 所属科室
  ├─ User 主要负责医生
  ├─ User 负责管理人员
  ├─ Nodule 结节/病灶
  ├─ ImagingReport 影像报告
  ├─ HealthReport 健康报告
  ├─ ReportFollowupAdvice 报告随访建议
  ├─ FollowupPlan 随访计划
  └─ FollowupTask 随访任务
```

## 4. 用户 User

用途：系统登录人员，包括健康管理师、医生助手、医生、科室主任、系统管理员。

核心字段：

- `id`
- `username`
- `password_hash`
- `real_name`
- `phone`
- `role`
- `department_id`
- `is_active`
- `created_at`
- `last_login`

角色枚举：

- `health_manager`：健康管理师
- `doctor_assistant`：医生助手
- `doctor`：医生
- `department_director`：科室主任
- `admin`：系统管理员

## 5. 科室 Department

用途：患者归属、医生归属、科室主任看板数据范围。

核心字段：

- `id`
- `name`
- `code`
- `hospital_name`
- `is_active`
- `created_at`
- `updated_at`

一期规则：

- 患者只归属一个科室。
- 科室主任只能查看本科室患者。

## 6. 患者 Patient

用途：系统管理的基础对象。

核心字段：

- `id`
- `patient_code`
- `name`
- `gender`
- `age`
- `phone`
- `department_id`
- `primary_doctor_id`
- `manager_id`
- `source_channel`
- `risk_level`
- `status`
- `is_new`
- `created_at`
- `updated_at`

状态建议：

- `pending_profile`：待完善
- `pending_report`：待报告
- `pending_review`：待复核
- `following`：随访中
- `abnormal_pending`：异常待处理
- `completed`：已完成
- `archived`：已归档

## 7. 结节/病灶 Nodule

用途：记录患者名下一个或多个结节/病灶。

核心字段：

- `id`
- `patient_id`
- `nodule_type`
- `nodule_no`
- `body_part`
- `side`
- `location`
- `size`
- `quantity`
- `imaging_features`
- `grade_type`
- `grade_value`
- `risk_level`
- `latest_report_id`
- `created_at`
- `updated_at`

类型建议：

- `breast`：乳腺
- `lung`：肺部
- `thyroid`：甲状腺

分级字段：

- `grade_type`：`BI-RADS` / `Lung-RADS` / `TI-RADS`
- `grade_value`：分级值

一期规则：

- 结节不强制单独指定医生。
- 多结节默认归患者主要负责医生查看。

## 8. 影像报告 ImagingReport

用途：管理患者检查报告文件和结构化字段。

核心字段：

- `id`
- `patient_id`
- `nodule_id`
- `report_type`
- `exam_date`
- `file_url`
- `file_name`
- `summary`
- `structured_data`
- `uploaded_by`
- `status`
- `created_at`

状态建议：

- `active`
- `voided`

## 9. 健康报告 HealthReport

用途：系统生成并审核归档的健康管理报告。

核心字段：

- `id`
- `patient_id`
- `report_code`
- `report_type`
- `html_content`
- `status`
- `risk_level`
- `risk_basis`
- `generated_by`
- `reviewed_by`
- `finalized_at`
- `created_at`
- `updated_at`

状态建议：

- `not_generated`
- `draft`
- `pending_review`
- `pending_advice`
- `finalized`
- `archived`
- `voided`

## 10. 报告随访建议 ReportFollowupAdvice

用途：医生查看报告后填写的简化建议。

核心字段：

- `id`
- `patient_id`
- `report_id`
- `nodule_id`
- `doctor_id`
- `advice_content`
- `suggested_next_followup_at`
- `status`
- `created_at`
- `updated_at`

状态建议：

- `draft`
- `submitted`

一期规则：

- 不拆分多种建议类型。
- 不做复杂审批流。
- 建议用于健康管理师/医生助手调整随访计划时参考。

## 11. 随访计划 FollowupPlan

用途：定义患者后续随访周期和节点。

核心字段：

- `id`
- `patient_id`
- `nodule_id`
- `plan_name`
- `risk_level`
- `source`
- `rule_id`
- `recommend_reason`
- `cycle_days`
- `next_followup_at`
- `status`
- `adjust_reason`
- `created_by`
- `created_at`
- `updated_at`

来源枚举：

- `rule_recommended`
- `manual`

状态建议：

- `draft`
- `active`
- `paused`
- `completed`
- `cancelled`

## 12. 随访任务 FollowupTask

用途：具体执行的随访事项。

核心字段：

- `id`
- `patient_id`
- `plan_id`
- `task_code`
- `title`
- `task_type`
- `scheduled_at`
- `executed_at`
- `channel`
- `status`
- `feedback_summary`
- `is_abnormal`
- `handled_by`
- `handled_at`
- `created_at`
- `updated_at`

渠道枚举：

- `mini_program`
- `public_link`
- `phone`
- `wecom`
- `sms`

状态建议：

- `pending_dispatch`
- `dispatched`
- `pending_execute`
- `completed`
- `no_response`
- `abnormal_pending`
- `closed`
- `cancelled`

## 13. 小程序随访反馈 FollowupFeedback

用途：保存患者通过小程序或公开链接提交的反馈。

核心字段：

- `id`
- `task_id`
- `patient_id`
- `source`
- `answers`
- `uploaded_files`
- `is_abnormal`
- `abnormal_reason`
- `submitted_at`

来源枚举：

- `mini_program`
- `public_link`

## 14. 操作日志 OperationLog

用途：记录关键操作，满足可追溯要求。

核心字段：

- `id`
- `user_id`
- `action`
- `target_type`
- `target_id`
- `detail`
- `created_at`

关键日志：

- 患者资料修改
- 影像报告上传/作废
- 健康报告审核/归档
- 报告随访建议提交
- 随访计划调整
- 随访任务执行
- 异常反馈处理

## 15. 数据权限规则

- 健康管理师/医生助手：查看和操作自己负责或被分配的患者。
- 医生：查看 `primary_doctor_id` 为自己的患者。
- 科室主任：查看 `department_id` 为本科室的患者。
- 系统管理员：管理用户、角色、科室和配置。
