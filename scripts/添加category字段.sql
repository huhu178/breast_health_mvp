-- ============================================
-- 添加 category 字段到 ai_agents.unified_knowledge_base
-- ============================================

-- 1. 添加 category 字段
ALTER TABLE ai_agents.unified_knowledge_base 
ADD COLUMN IF NOT EXISTS category VARCHAR(50);

-- 2. 创建索引以优化查询性能
CREATE INDEX IF NOT EXISTS idx_knowledge_category 
ON ai_agents.unified_knowledge_base(category);

-- 3. 为现有数据设置默认值（根据 source_type 推断）
UPDATE ai_agents.unified_knowledge_base
SET category = CASE 
    WHEN source_type LIKE '%影像%' THEN '影像学'
    WHEN source_type LIKE '%症状%' THEN '症状管理'
    WHEN source_type LIKE '%生物节律%' OR source_type LIKE '%睡眠%' THEN '生物节律'
    WHEN source_type LIKE '%家族史%' THEN '家族史管理'
    WHEN source_type LIKE '%生活方式%' THEN '生活方式'
    WHEN source_type LIKE '%随访%' THEN '随访管理'
    WHEN source_type LIKE '%检查%' THEN '检查历史'
    WHEN source_type LIKE '%风险%' THEN '风险评估'
    ELSE '综合建议'
END
WHERE category IS NULL;

-- 4. 验证字段是否添加成功
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'ai_agents' 
  AND table_name = 'unified_knowledge_base' 
  AND column_name = 'category';

-- 5. 查看各分类的数量
SELECT 
    category,
    COUNT(*) as count
FROM ai_agents.unified_knowledge_base
GROUP BY category
ORDER BY count DESC;

-- ============================================
-- 执行说明
-- ============================================
-- 1. 在 DBeaver 中打开此文件
-- 2. 选中所有SQL语句
-- 3. 点击执行（或按 Ctrl+Enter）
-- 4. 检查输出，确认字段添加成功
-- ============================================



