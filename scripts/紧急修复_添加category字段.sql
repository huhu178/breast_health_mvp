-- ============================================
-- 紧急修复：添加 category 字段
-- 这是让系统运行的最小必要修复
-- ============================================

-- 添加 category 字段
ALTER TABLE ai_agents.unified_knowledge_base 
ADD COLUMN IF NOT EXISTS category VARCHAR(50);

-- 为现有数据设置默认值
UPDATE ai_agents.unified_knowledge_base
SET category = '综合建议'
WHERE category IS NULL;

-- 验证
SELECT COUNT(*) as total_records, 
       COUNT(category) as has_category
FROM ai_agents.unified_knowledge_base;

-- ============================================
-- 在 DBeaver 中执行步骤：
-- 1. 打开 DBeaver
-- 2. 连接到数据库
-- 3. 复制上面3条SQL语句
-- 4. 点击执行（Ctrl+Enter）
-- 5. 查看最后的验证结果，确认两个数字相同
-- ============================================



