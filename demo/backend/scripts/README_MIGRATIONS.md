# 数据库迁移说明

当前项目仍保留开发期的 `db.create_all()` 和少量启动时自修复逻辑。为了让新环境部署更可控，生产或联调环境应显式执行迁移脚本。

## 推荐顺序

```bash
psql "$DATABASE_URL" -f demo/backend/scripts/add_patient_wecom_binding_fields.sql
psql "$DATABASE_URL" -f demo/backend/scripts/add_followup_workflow_tables.sql
psql "$DATABASE_URL" -f demo/backend/scripts/add_followup_planning_tables.sql
```

这些脚本使用 `CREATE TABLE IF NOT EXISTS`、`CREATE INDEX IF NOT EXISTS` 或 `ADD COLUMN IF NOT EXISTS`，可重复执行。

## 当前随访链路依赖

- `b_followup_tasks`
- `b_followup_messages`
- `b_followup_events`
- `b_followup_knowledge_items`
- `b_followup_plan_templates`
- `b_followup_plan_nodes`
- `b_followup_ai_rules`
- `b_followup_patient_plans`
- `b_followup_checkins`
- `b_patients.wecom_external_userid`
- `b_patients.wecom_userid`
- `b_patients.wecom_bind_status`
- `b_patients.wecom_bound_at`

## 后续建议

下一步应引入 Alembic 或等价迁移系统，把启动时的 `ALTER TABLE` 自修复逻辑迁到版本化 migration 中。当前 README 先固定执行顺序，避免继续依赖隐式建表。
