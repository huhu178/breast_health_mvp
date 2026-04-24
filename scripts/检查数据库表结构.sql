-- ============================================
-- 数据库表结构完整性检查脚本
-- 检查所有必需的表和字段是否存在
-- ============================================

-- 第1部分：检查所有必需的表是否存在
-- ============================================
SELECT '==================== 📋 表存在性检查 ====================' AS 检查项;

SELECT 
    '1. users (用户表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '2. patients (患者表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'patients') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '3. health_records_mvp (健康档案表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'health_records_mvp') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '4. reports (报告表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reports') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '5. ai_conversations (AI对话会话表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_conversations') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '6. ai_messages (AI对话消息表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ai_messages') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '7. follow_up_records (跟进记录表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'follow_up_records') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '8. wechat_config (企业微信配置表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'wechat_config') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '9. wechat_users (企业微信用户表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'wechat_users') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '10. wechat_templates (企业微信模板表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'wechat_templates') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '11. wechat_messages (企业微信消息表)' AS 表名,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'wechat_messages') 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态
UNION ALL
SELECT 
    '12. ai_agents.unified_knowledge_base (知识库表)' AS 表名,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'ai_agents' 
            AND table_name = 'unified_knowledge_base'
        ) 
        THEN '✅ 已存在' 
        ELSE '❌ 缺失' 
    END AS 状态;


-- 第2部分：检查 health_records_mvp 表的所有字段
-- ============================================
SELECT '==================== 📋 health_records_mvp 字段检查 ====================' AS 检查项;

SELECT 
    column_name AS 字段名,
    data_type AS 数据类型,
    CASE 
        WHEN is_nullable = 'YES' THEN '允许空值'
        ELSE '不允许空值'
    END AS 是否可空
FROM information_schema.columns 
WHERE table_name = 'health_records_mvp'
ORDER BY ordinal_position;


-- 第3部分：检查必需字段是否存在
-- ============================================
SELECT '==================== 📋 health_records_mvp 必需字段检查 ====================' AS 检查项;

SELECT 
    '基本字段' AS 分类,
    'patient_id' AS 字段名,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'health_records_mvp' AND column_name = 'patient_id'
        ) 
        THEN '✅' ELSE '❌' 
    END AS 状态
UNION ALL
SELECT '基本字段', 'record_code',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'health_records_mvp' AND column_name = 'record_code') THEN '✅' ELSE '❌' END
UNION ALL
SELECT '基本字段', 'age',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'health_records_mvp' AND column_name = 'age') THEN '✅' ELSE '❌' END
UNION ALL
SELECT '基本字段', 'birads_level',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'health_records_mvp' AND column_name = 'birads_level') THEN '✅' ELSE '❌' END
UNION ALL
SELECT '基本字段', 'family_history',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'health_records_mvp' AND column_name = 'family_history') THEN '✅' ELSE '❌' END
UNION ALL
SELECT '症状字段', 'symptoms',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'health_records_mvp' AND column_name = 'symptoms') THEN '✅' ELSE '❌' END
UNION ALL
SELECT '影像字段', 'nodule_size',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'health_records_mvp' AND column_name = 'nodule_size') THEN '✅' ELSE '❌' END
UNION ALL
SELECT '生活方式', 'sleep_quality',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'health_records_mvp' AND column_name = 'sleep_quality') THEN '✅' ELSE '❌' END
UNION ALL
SELECT '生活方式', 'exercise_frequency',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'health_records_mvp' AND column_name = 'exercise_frequency') THEN '✅' ELSE '❌' END
UNION ALL
SELECT '生活方式', 'lifestyle',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'health_records_mvp' AND column_name = 'lifestyle') THEN '✅' ELSE '❌' END;


-- 第4部分：检查 reports 表的字段
-- ============================================
SELECT '==================== 📋 reports 表字段检查 ====================' AS 检查项;

SELECT 
    column_name AS 字段名,
    data_type AS 数据类型
FROM information_schema.columns 
WHERE table_name = 'reports'
ORDER BY ordinal_position;


-- 第5部分：检查数据统计
-- ============================================
SELECT '==================== 📊 数据统计 ====================' AS 检查项;

SELECT 
    'users' AS 表名,
    COUNT(*) AS 记录数
FROM users
UNION ALL
SELECT 'patients', COUNT(*) FROM patients
UNION ALL
SELECT 'health_records_mvp', COUNT(*) FROM health_records_mvp
UNION ALL
SELECT 'reports', COUNT(*) FROM reports
UNION ALL
SELECT 'ai_conversations', COUNT(*) FROM ai_conversations
UNION ALL
SELECT 'ai_messages', COUNT(*) FROM ai_messages
UNION ALL
SELECT 'follow_up_records', COUNT(*) FROM follow_up_records;


-- 第6部分：检查知识库
-- ============================================
SELECT '==================== 📚 知识库检查 ====================' AS 检查项;

SELECT 
    COUNT(*) AS 知识库记录数,
    COUNT(DISTINCT category) AS 分类数量,
    MIN(created_at) AS 最早记录时间,
    MAX(created_at) AS 最新记录时间
FROM ai_agents.unified_knowledge_base
WHERE is_active = TRUE;


-- 完成提示
-- ============================================
SELECT '==================== ✅ 检查完成 ====================' AS 检查项;

SELECT 
    '数据库表结构检查完成！' AS 消息,
    '请查看上面的检查结果，如有 ❌ 标记的项目需要修复' AS 说明;



