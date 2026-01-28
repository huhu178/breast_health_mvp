-- ============================================
-- 乳腺结节健康管理系统 - 完整数据库表结构
-- 创建时间: 2025-10-27
-- 说明: 包含所有系统需要的表
-- ============================================

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50),
    role VARCHAR(20) DEFAULT 'manager',
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 患者表
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    patient_code VARCHAR(50) UNIQUE,
    name VARCHAR(50) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    phone VARCHAR(20),
    wechat_id VARCHAR(50),
    id_card VARCHAR(20),
    address TEXT,
    source_channel VARCHAR(50),
    status VARCHAR(20) DEFAULT 'new',
    manager_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 健康档案表（完整版 - 包含所有字段）
CREATE TABLE IF NOT EXISTS health_records_mvp (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    record_code VARCHAR(50) UNIQUE,
    
    -- 基本健康信息
    age INTEGER,
    birads_level INTEGER,
    family_history VARCHAR(100),
    
    -- 病程信息
    nodule_discovery_time DATE,
    course_stage VARCHAR(50),
    tnm_stage VARCHAR(10),
    
    -- 症状信息
    symptoms VARCHAR(200),
    pain_level INTEGER,
    pain_type VARCHAR(50),
    nipple_discharge_type VARCHAR(50),
    skin_change_type VARCHAR(50),
    
    -- 影像学信息
    nodule_location VARCHAR(50),
    nodule_size VARCHAR(50),
    boundary_features VARCHAR(100),
    internal_echo VARCHAR(50),
    blood_flow_signal VARCHAR(50),
    elasticity_score VARCHAR(20),
    
    -- 生物节律
    rhythm_type VARCHAR(50),
    cycle_phase VARCHAR(50),
    sleep_quality VARCHAR(100),
    sleep_condition VARCHAR(50),
    
    -- 检查历史
    exam_history_type VARCHAR(50),
    exam_history_detail VARCHAR(200),
    previous_exam_history TEXT,
    
    -- 生活方式
    exercise_frequency VARCHAR(50),
    lifestyle VARCHAR(50),
    
    -- 状态
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 报告表
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    report_code VARCHAR(50) UNIQUE,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    record_id INTEGER REFERENCES health_records_mvp(id),
    report_type VARCHAR(50),
    report_html TEXT,
    report_summary TEXT,
    risk_level VARCHAR(20),
    recommendations TEXT,
    generated_by VARCHAR(50),
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. AI对话会话表
CREATE TABLE IF NOT EXISTS ai_conversations (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    collected_data JSON,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. AI对话消息表
CREATE TABLE IF NOT EXISTS ai_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    message_type VARCHAR(20),
    content TEXT,
    intent VARCHAR(50),
    extra_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 患者跟进记录表
CREATE TABLE IF NOT EXISTS follow_up_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    manager_id INTEGER NOT NULL REFERENCES users(id),
    follow_up_type VARCHAR(20),
    follow_up_date DATE,
    content TEXT,
    next_follow_up_date DATE,
    next_follow_up_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 企业微信配置表
CREATE TABLE IF NOT EXISTS wechat_config (
    id SERIAL PRIMARY KEY,
    corp_id VARCHAR(100),
    agent_id VARCHAR(50),
    secret VARCHAR(200),
    token VARCHAR(100),
    encoding_aes_key VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. 企业微信用户关联表
CREATE TABLE IF NOT EXISTS wechat_users (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    wechat_user_id VARCHAR(100),
    wechat_name VARCHAR(50),
    department VARCHAR(100),
    bind_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 企业微信消息模板表
CREATE TABLE IF NOT EXISTS wechat_templates (
    id SERIAL PRIMARY KEY,
    template_code VARCHAR(50) UNIQUE,
    template_name VARCHAR(100),
    template_type VARCHAR(50),
    content_template TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. 企业微信消息记录表
CREATE TABLE IF NOT EXISTS wechat_messages (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    template_id INTEGER REFERENCES wechat_templates(id),
    message_type VARCHAR(50),
    content TEXT,
    send_status VARCHAR(20),
    send_time TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. 创建知识库 schema（如果不存在）
CREATE SCHEMA IF NOT EXISTS ai_agents;

-- 13. 统一知识库表
CREATE TABLE IF NOT EXISTS ai_agents.unified_knowledge_base (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    
    -- 多维度匹配字段
    age_range VARCHAR(50),
    birads_category VARCHAR(50),
    symptom_type VARCHAR(100),
    family_history_type VARCHAR(50),
    rhythm_category VARCHAR(50),
    sleep_pattern VARCHAR(50),
    exam_history_type VARCHAR(50),
    
    -- 优先级和证据
    recommendation_level VARCHAR(20),
    evidence_level VARCHAR(20),
    priority INTEGER DEFAULT 5,
    
    -- 元信息
    source VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 创建索引
-- ============================================

-- 患者表索引
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_status ON patients(status);
CREATE INDEX IF NOT EXISTS idx_patients_manager ON patients(manager_id);

-- 健康档案表索引
CREATE INDEX IF NOT EXISTS idx_records_patient ON health_records_mvp(patient_id);
CREATE INDEX IF NOT EXISTS idx_records_birads ON health_records_mvp(birads_level);
CREATE INDEX IF NOT EXISTS idx_records_created ON health_records_mvp(created_at);

-- 报告表索引
CREATE INDEX IF NOT EXISTS idx_reports_patient ON reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_reports_record ON reports(record_id);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at);

-- AI对话表索引
CREATE INDEX IF NOT EXISTS idx_conversations_patient ON ai_conversations(patient_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON ai_conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON ai_messages(conversation_id);

-- 跟进记录表索引
CREATE INDEX IF NOT EXISTS idx_followups_patient ON follow_up_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_followups_manager ON follow_up_records(manager_id);
CREATE INDEX IF NOT EXISTS idx_followups_date ON follow_up_records(follow_up_date);
CREATE INDEX IF NOT EXISTS idx_followups_next_date ON follow_up_records(next_follow_up_date);

-- 知识库索引
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON ai_agents.unified_knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_birads ON ai_agents.unified_knowledge_base(birads_category);
CREATE INDEX IF NOT EXISTS idx_knowledge_age ON ai_agents.unified_knowledge_base(age_range);
CREATE INDEX IF NOT EXISTS idx_knowledge_active ON ai_agents.unified_knowledge_base(is_active);

-- ============================================
-- 完成提示
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE '✅ 数据库表结构创建完成！';
    RAISE NOTICE '============================================';
    RAISE NOTICE '已创建的表：';
    RAISE NOTICE '1. users - 用户表';
    RAISE NOTICE '2. patients - 患者表';
    RAISE NOTICE '3. health_records_mvp - 健康档案表';
    RAISE NOTICE '4. reports - 报告表';
    RAISE NOTICE '5. ai_conversations - AI对话会话表';
    RAISE NOTICE '6. ai_messages - AI对话消息表';
    RAISE NOTICE '7. follow_up_records - 患者跟进记录表';
    RAISE NOTICE '8. wechat_config - 企业微信配置表';
    RAISE NOTICE '9. wechat_users - 企业微信用户关联表';
    RAISE NOTICE '10. wechat_templates - 企业微信消息模板表';
    RAISE NOTICE '11. wechat_messages - 企业微信消息记录表';
    RAISE NOTICE '12. ai_agents.unified_knowledge_base - 统一知识库表';
    RAISE NOTICE '============================================';
    RAISE NOTICE '已创建索引以优化查询性能';
    RAISE NOTICE '============================================';
END $$;

