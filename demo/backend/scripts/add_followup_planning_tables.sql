-- 随访知识库 / 计划模板 / 患者计划 / 打卡记录
-- 开发环境会通过 SQLAlchemy db.create_all 自动建表；生产可显式执行本脚本。

CREATE TABLE IF NOT EXISTS public.b_followup_knowledge_items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    nodule_type VARCHAR(50),
    risk_level VARCHAR(20),
    task_type VARCHAR(50),
    age_min INTEGER,
    age_max INTEGER,
    gender VARCHAR(10),
    trigger_keywords TEXT,
    action_type VARCHAR(50),
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    source VARCHAR(100),
    metadata_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.b_followup_plan_templates (
    id SERIAL PRIMARY KEY,
    template_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    nodule_type VARCHAR(50),
    risk_level VARCHAR(20),
    cycle_days INTEGER DEFAULT 90,
    default_channel VARCHAR(32) DEFAULT 'wecom',
    default_reminder_strategy VARCHAR(100) DEFAULT '到期前3天提醒；逾期转人工；异常转医生',
    audience_rule JSON,
    status VARCHAR(20) DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    created_by INTEGER REFERENCES public.users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.b_followup_plan_nodes (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES public.b_followup_plan_templates(id) ON DELETE CASCADE,
    node_code VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    day_offset INTEGER DEFAULT 1,
    send_time VARCHAR(8) DEFAULT '09:00',
    task_type VARCHAR(50) NOT NULL,
    patient_action VARCHAR(50),
    ai_action VARCHAR(50),
    message_template TEXT NOT NULL,
    knowledge_item_ids JSON,
    checkin_schema JSON,
    escalation_rule JSON,
    completion_rule JSON,
    is_required BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.b_followup_ai_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    rule_type VARCHAR(50) NOT NULL,
    nodule_type VARCHAR(50),
    risk_level VARCHAR(20),
    task_type VARCHAR(50),
    trigger_keywords TEXT,
    condition_json JSON,
    action VARCHAR(50) NOT NULL,
    response_template TEXT,
    priority INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.b_followup_patient_plans (
    id SERIAL PRIMARY KEY,
    plan_code VARCHAR(50) UNIQUE NOT NULL,
    patient_id INTEGER NOT NULL REFERENCES public.b_patients(id),
    record_id INTEGER REFERENCES public.b_health_records(id),
    report_id INTEGER REFERENCES public.b_reports(id),
    template_id INTEGER REFERENCES public.b_followup_plan_templates(id),
    manager_id INTEGER NOT NULL REFERENCES public.users(id),
    name VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    nodule_type VARCHAR(50),
    risk_level VARCHAR(20),
    cycle_days INTEGER DEFAULT 90,
    channel VARCHAR(32) DEFAULT 'wecom',
    reminder_strategy VARCHAR(100),
    start_at TIMESTAMP,
    activated_at TIMESTAMP,
    completed_at TIMESTAMP,
    plan_content JSON,
    selected_knowledge_ids JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.b_followup_checkins (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES public.b_followup_tasks(id),
    patient_plan_id INTEGER REFERENCES public.b_followup_patient_plans(id),
    patient_id INTEGER NOT NULL REFERENCES public.b_patients(id),
    checkin_type VARCHAR(50) NOT NULL,
    content_text TEXT,
    image_urls JSON,
    structured_data JSON,
    ai_result JSON,
    status VARCHAR(20) DEFAULT 'submitted',
    abnormal_flag BOOLEAN DEFAULT FALSE,
    abnormal_reason TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by INTEGER REFERENCES public.users(id)
);

CREATE INDEX IF NOT EXISTS idx_b_fuk_category ON public.b_followup_knowledge_items(category);
CREATE INDEX IF NOT EXISTS idx_b_fuk_match ON public.b_followup_knowledge_items(nodule_type, risk_level, task_type);
CREATE INDEX IF NOT EXISTS idx_b_fuk_active ON public.b_followup_knowledge_items(is_active);
CREATE INDEX IF NOT EXISTS idx_b_fpt_match ON public.b_followup_plan_templates(nodule_type, risk_level, status);
CREATE INDEX IF NOT EXISTS idx_b_fpn_template ON public.b_followup_plan_nodes(template_id);
CREATE INDEX IF NOT EXISTS idx_b_far_match ON public.b_followup_ai_rules(rule_type, nodule_type, risk_level, task_type);
CREATE INDEX IF NOT EXISTS idx_b_fpp_patient_status ON public.b_followup_patient_plans(patient_id, status);
CREATE INDEX IF NOT EXISTS idx_b_fci_patient ON public.b_followup_checkins(patient_id);
CREATE INDEX IF NOT EXISTS idx_b_fci_task ON public.b_followup_checkins(task_id);
