-- 为 c_conversations 表添加缺失的字段

ALTER TABLE public.c_conversations 
ADD COLUMN IF NOT EXISTS collected_data JSONB;

ALTER TABLE public.c_conversations 
ADD COLUMN IF NOT EXISTS summary TEXT;

ALTER TABLE public.c_conversations 
ADD COLUMN IF NOT EXISTS keywords TEXT;

-- 完成
SELECT 'C 端表字段添加完成！' AS status;

