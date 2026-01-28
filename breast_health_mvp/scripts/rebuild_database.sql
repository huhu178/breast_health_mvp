-- ============================================
-- 数据库重建SQL脚本 - B端C端分离
-- 在DBeaver中执行此脚本
-- ============================================

-- 开始事务
BEGIN;

-- 设置错误处理级别
SET client_min_messages = WARNING;

-- ============================================
-- 1. 删除现有表（保留用户表和知识库表）
-- ============================================

-- 删除现有表
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS health_records CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS ai_conversations CASCADE;
DROP TABLE IF EXISTS ai_messages CASCADE;
DROP TABLE IF EXISTS follow_up_records CASCADE;
DROP TABLE IF EXISTS wechat_configs CASCADE;
DROP TABLE IF EXISTS wechat_users CASCADE;
DROP TABLE IF EXISTS wechat_templates CASCADE;
DROP TABLE IF EXISTS wechat_messages CASCADE;

-- ============================================
-- 2. 创建B端专用表
-- ============================================

-- B端患者表
CREATE TABLE b_patients (
    id SERIAL PRIMARY KEY,
    patient_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    phone VARCHAR(20),
    wechat_id VARCHAR(50),
    
    -- B端特有字段
    manager_id INTEGER REFERENCES users(id),
    source_channel VARCHAR(50) DEFAULT 'b_end',
    status VARCHAR(20) DEFAULT 'active',
    is_new BOOLEAN DEFAULT TRUE,
    
    -- 时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- B端健康档案表
CREATE TABLE b_health_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES b_patients(id) ON DELETE CASCADE,
    record_code VARCHAR(50) UNIQUE NOT NULL,
    
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
    
    -- B端特有字段
    data_completeness VARCHAR(20) DEFAULT 'full',
    created_by INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- B端报告表
CREATE TABLE b_reports (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES b_patients(id) ON DELETE CASCADE,
    record_id INTEGER REFERENCES b_health_records(id),
    
    report_code VARCHAR(50) UNIQUE NOT NULL,
    report_html TEXT,
    report_summary TEXT,
    risk_level VARCHAR(20),
    
    -- B端特有字段
    report_type VARCHAR(20) DEFAULT 'professional',
    access_level VARCHAR(20) DEFAULT 'b_only',
    generated_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- B端跟进记录表
CREATE TABLE b_follow_up_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES b_patients(id) ON DELETE CASCADE,
    manager_id INTEGER REFERENCES users(id),
    
    -- 跟进信息
    follow_up_type VARCHAR(20),
    follow_up_date DATE,
    content TEXT,
    
    -- 下次跟进计划
    next_follow_up_date DATE,
    next_follow_up_action TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. 创建C端专用表
-- ============================================

-- C端患者表
CREATE TABLE c_patients (
    id SERIAL PRIMARY KEY,
    patient_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,  -- C端主要标识
    wechat_id VARCHAR(50),
    
    -- C端特有字段
    source_channel VARCHAR(50) DEFAULT 'c_end',
    status VARCHAR(20) DEFAULT 'active',
    is_contacted BOOLEAN DEFAULT FALSE,
    
    -- 时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- C端健康档案表
CREATE TABLE c_health_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES c_patients(id) ON DELETE CASCADE,
    record_code VARCHAR(50) UNIQUE NOT NULL,
    
    -- 基本信息（通过AI对话收集）
    age INTEGER,
    birads_level INTEGER,
    family_history VARCHAR(100),
    symptoms VARCHAR(200),
    pain_level INTEGER,
    pain_type VARCHAR(50),
    nodule_location VARCHAR(50),
    nodule_size VARCHAR(50),
    boundary_features VARCHAR(100),
    internal_echo VARCHAR(50),
    blood_flow_signal VARCHAR(50),
    elasticity_score VARCHAR(20),
    rhythm_type VARCHAR(50),
    sleep_quality VARCHAR(100),
    exam_history_type VARCHAR(50),
    exercise_frequency VARCHAR(50),
    
    -- C端特有字段
    data_completeness VARCHAR(20) DEFAULT 'partial',
    conversation_id INTEGER,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- C端报告表
CREATE TABLE c_reports (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES c_patients(id) ON DELETE CASCADE,
    record_id INTEGER REFERENCES c_health_records(id),
    
    report_code VARCHAR(50) UNIQUE NOT NULL,
    report_html TEXT,
    report_summary TEXT,
    risk_level VARCHAR(20),
    
    -- C端特有字段
    report_type VARCHAR(20) DEFAULT 'patient_friendly',
    access_level VARCHAR(20) DEFAULT 'c_accessible',
    access_token VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- C端AI对话会话表
CREATE TABLE c_conversations (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES c_patients(id),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- 会话状态
    status VARCHAR(20) DEFAULT 'active',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    
    -- 收集到的信息
    collected_data JSONB,
    
    -- 会话摘要
    summary TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- C端对话消息表
CREATE TABLE c_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES c_conversations(id) ON DELETE CASCADE,
    
    -- 消息信息
    message_type VARCHAR(20),
    content TEXT,
    intent VARCHAR(50),
    
    -- 元数据
    extra_data JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. 创建索引
-- ============================================

-- B端索引
CREATE INDEX idx_b_patients_manager_id ON b_patients(manager_id);
CREATE INDEX idx_b_patients_status ON b_patients(status);
CREATE INDEX idx_b_patients_is_new ON b_patients(is_new);
CREATE INDEX idx_b_health_records_patient_id ON b_health_records(patient_id);
CREATE INDEX idx_b_reports_patient_id ON b_reports(patient_id);
CREATE INDEX idx_b_reports_report_type ON b_reports(report_type);
CREATE INDEX idx_b_follow_up_records_patient_id ON b_follow_up_records(patient_id);

-- C端索引
CREATE INDEX idx_c_patients_phone ON c_patients(phone);
CREATE INDEX idx_c_patients_status ON c_patients(status);
CREATE INDEX idx_c_patients_is_contacted ON c_patients(is_contacted);
CREATE INDEX idx_c_health_records_patient_id ON c_health_records(patient_id);
CREATE INDEX idx_c_reports_patient_id ON c_reports(patient_id);
CREATE INDEX idx_c_reports_access_token ON c_reports(access_token);
CREATE INDEX idx_c_conversations_patient_id ON c_conversations(patient_id);
CREATE INDEX idx_c_conversations_session_id ON c_conversations(session_id);
CREATE INDEX idx_c_messages_conversation_id ON c_messages(conversation_id);

-- ============================================
-- 5. 插入测试数据
-- ============================================

-- 首先检查users表是否存在数据
DO $$
DECLARE
    user_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    
    -- 如果users表为空，插入测试用户
    IF user_count = 0 THEN
        INSERT INTO users (username, password_hash, real_name, email, phone, role, is_active)
        VALUES 
            ('admin', 'pbkdf2:sha256:260000$...', '系统管理员', 'admin@example.com', '13800000001', 'admin', true),
            ('manager1', 'pbkdf2:sha256:260000$...', '张医生', 'zhang@example.com', '13800000002', 'health_manager', true),
            ('manager2', 'pbkdf2:sha256:260000$...', '李医生', 'li@example.com', '13800000003', 'health_manager', true);
        
        RAISE NOTICE '已插入测试用户数据';
    ELSE
        RAISE NOTICE 'users表已有数据，跳过用户插入';
    END IF;
END $$;

-- 插入B端测试患者（使用实际的用户ID）
INSERT INTO b_patients (patient_code, name, age, gender, phone, wechat_id, manager_id, source_channel, status, is_new)
SELECT 
    'BP20250116001', '王女士', 35, '女', '13900000001', 'wang_001', 
    (SELECT id FROM users WHERE username = 'manager1' LIMIT 1), 
    'b_end', 'active', true
WHERE EXISTS (SELECT 1 FROM users WHERE username = 'manager1')
UNION ALL
SELECT 
    'BP20250116002', '刘女士', 42, '女', '13900000002', 'liu_002', 
    (SELECT id FROM users WHERE username = 'manager2' LIMIT 1), 
    'b_end', 'active', false
WHERE EXISTS (SELECT 1 FROM users WHERE username = 'manager2');

-- 插入C端测试患者
INSERT INTO c_patients (patient_code, name, phone, wechat_id, source_channel, status, is_contacted)
VALUES 
    ('CP20250116001', '陈女士', '13900000003', 'chen_003', 'c_end', 'active', false),
    ('CP20250116002', '赵女士', '13900000004', 'zhao_004', 'c_end', 'active', true);

-- ============================================
-- 6. 验证表创建
-- ============================================

-- 查询所有表
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE table_schema = 'public' 
    AND (tablename LIKE 'b_%' OR tablename LIKE 'c_%' OR tablename IN ('users', 'unified_knowledge_base'))
ORDER BY tablename;

-- 统计表记录数
SELECT 
    'b_patients' as table_name, COUNT(*) as record_count FROM b_patients
UNION ALL
SELECT 
    'c_patients' as table_name, COUNT(*) as record_count FROM c_patients
UNION ALL
SELECT 
    'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 
    'unified_knowledge_base' as table_name, COUNT(*) as record_count FROM unified_knowledge_base;

-- 提交事务
COMMIT;

-- ============================================
-- 完成提示
-- ============================================
SELECT '✅ 数据库重建完成！' as status;
