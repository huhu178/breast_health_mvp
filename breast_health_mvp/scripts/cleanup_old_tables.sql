-- ============================================
-- 清理旧表SQL脚本
-- 删除已被B端C端分离表替代的旧表
-- ============================================

-- 删除旧表
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS health_records_mvp CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS reports_mvp CASCADE;
DROP TABLE IF EXISTS ai_conversations CASCADE;
DROP TABLE IF EXISTS ai_messages CASCADE;
DROP TABLE IF EXISTS follow_up_records CASCADE;
DROP TABLE IF EXISTS wechat_config CASCADE;
DROP TABLE IF EXISTS wechat_messages CASCADE;
DROP TABLE IF EXISTS wechat_templates CASCADE;
DROP TABLE IF EXISTS wechat_users CASCADE;

-- 验证删除结果
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 显示保留的表
SELECT '✅ 清理完成！保留的表:' as status;
SELECT table_name, pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND (table_name LIKE 'b_%' OR table_name LIKE 'c_%' OR table_name IN ('users'))
ORDER BY table_name;
