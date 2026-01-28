-- 检查知识库表的所有字段
SELECT 
    column_name AS 字段名,
    data_type AS 数据类型
FROM information_schema.columns 
WHERE table_schema = 'ai_agents' 
  AND table_name = 'unified_knowledge_base'
ORDER BY ordinal_position;



