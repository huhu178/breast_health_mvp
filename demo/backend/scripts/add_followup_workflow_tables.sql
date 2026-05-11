-- 随访任务 / AI随访 / 企业微信触达工作流表
-- 适用于现有 PostgreSQL 库；开发环境也会通过 SQLAlchemy db.create_all 自动建新表。

CREATE TABLE IF NOT EXISTS public.b_followup_tasks (
    id SERIAL PRIMARY KEY,
    task_code VARCHAR(50) UNIQUE NOT NULL,
    patient_id INTEGER NOT NULL REFERENCES public.b_patients(id),
    record_id INTEGER REFERENCES public.b_health_records(id),
    report_id INTEGER REFERENCES public.b_reports(id),
    manager_id INTEGER NOT NULL REFERENCES public.users(id),
    status VARCHAR(32) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'normal',
    risk_level VARCHAR(20),
    nodule_type VARCHAR(50),
    source VARCHAR(32) DEFAULT 'manual',
    title VARCHAR(200),
    plan_name VARCHAR(200),
    plan_day INTEGER DEFAULT 1,
    due_at TIMESTAMP,
    scheduled_send_at TIMESTAMP,
    completed_at TIMESTAMP,
    channel VARCHAR(32) DEFAULT 'wecom',
    channel_recipient VARCHAR(120),
    last_message_id INTEGER,
    ai_enabled BOOLEAN DEFAULT TRUE,
    ai_summary TEXT,
    abnormal_flag BOOLEAN DEFAULT FALSE,
    abnormal_reason TEXT,
    handoff_to VARCHAR(80),
    task_payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.b_followup_messages (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES public.b_followup_tasks(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES public.b_patients(id),
    direction VARCHAR(16) NOT NULL,
    sender_type VARCHAR(24) DEFAULT 'system',
    channel VARCHAR(32) DEFAULT 'wecom',
    content_type VARCHAR(32) DEFAULT 'text',
    content TEXT NOT NULL,
    ai_intent VARCHAR(80),
    risk_signal VARCHAR(80),
    requires_manual_review BOOLEAN DEFAULT FALSE,
    send_status VARCHAR(32) DEFAULT 'created',
    provider_message_id VARCHAR(120),
    provider_payload JSON,
    provider_response JSON,
    error_message TEXT,
    sent_at TIMESTAMP,
    received_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'b_followup_tasks_last_message_fk'
    ) THEN
        ALTER TABLE public.b_followup_tasks
            ADD CONSTRAINT b_followup_tasks_last_message_fk
            FOREIGN KEY (last_message_id) REFERENCES public.b_followup_messages(id);
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS public.b_followup_events (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES public.b_followup_tasks(id) ON DELETE CASCADE,
    event_type VARCHAR(64) NOT NULL,
    from_status VARCHAR(32),
    to_status VARCHAR(32),
    actor_type VARCHAR(32) DEFAULT 'system',
    actor_id VARCHAR(80),
    summary TEXT,
    payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_b_followup_tasks_patient_id ON public.b_followup_tasks(patient_id);
CREATE INDEX IF NOT EXISTS idx_b_followup_tasks_manager_status ON public.b_followup_tasks(manager_id, status);
CREATE INDEX IF NOT EXISTS idx_b_followup_tasks_due_at ON public.b_followup_tasks(due_at);
CREATE INDEX IF NOT EXISTS idx_b_followup_tasks_abnormal ON public.b_followup_tasks(abnormal_flag);
CREATE INDEX IF NOT EXISTS idx_b_followup_messages_task_id ON public.b_followup_messages(task_id);
CREATE INDEX IF NOT EXISTS idx_b_followup_messages_patient_id ON public.b_followup_messages(patient_id);
CREATE INDEX IF NOT EXISTS idx_b_followup_events_task_id ON public.b_followup_events(task_id);
CREATE INDEX IF NOT EXISTS idx_b_followup_events_type ON public.b_followup_events(event_type);
