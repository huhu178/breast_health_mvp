-- ===================================
-- 检查C端数据存储情况
-- ===================================

-- 1. 检查患者表中的手机号
SELECT 
    id,
    patient_code,
    name,
    phone,
    source_channel,
    created_at
FROM patients
ORDER BY created_at DESC
LIMIT 10;

-- 2. 检查AI对话会话表
SELECT 
    id,
    patient_id,
    session_id,
    status,
    start_time,
    end_time,
    collected_data,
    summary
FROM ai_conversations
ORDER BY start_time DESC
LIMIT 10;

-- 3. 检查AI对话消息表
SELECT 
    am.id,
    am.conversation_id,
    am.message_type,
    am.content,
    am.created_at,
    ac.patient_id
FROM ai_messages am
LEFT JOIN ai_conversations ac ON am.conversation_id = ac.id
ORDER BY am.created_at DESC
LIMIT 20;

-- 4. 检查报告表
SELECT 
    r.id,
    r.report_code,
    r.patient_id,
    r.risk_level,
    p.name AS patient_name,
    p.phone AS patient_phone,
    r.created_at
FROM reports_mvp r
LEFT JOIN patients p ON r.patient_id = p.id
ORDER BY r.created_at DESC
LIMIT 10;

-- 5. 检查最后一次C端测试的完整数据
SELECT 
    p.id AS patient_id,
    p.name AS patient_name,
    p.phone AS patient_phone,
    p.patient_code,
    ac.session_id,
    ac.status AS conversation_status,
    r.report_code,
    r.risk_level,
    COUNT(am.id) AS message_count
FROM patients p
LEFT JOIN ai_conversations ac ON p.id = ac.patient_id
LEFT JOIN reports_mvp r ON p.id = r.patient_id
LEFT JOIN ai_messages am ON ac.id = am.conversation_id
WHERE p.source_channel = 'AI对话问诊'
GROUP BY p.id, p.name, p.phone, p.patient_code, ac.session_id, ac.status, r.report_code, r.risk_level
ORDER BY p.created_at DESC;

