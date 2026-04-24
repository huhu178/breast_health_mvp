-- 为 c_patients 表添加新字段
-- 执行前请备份数据库！

-- 添加 age, gender, nodule_type 字段到 c_patients 表
ALTER TABLE c_patients 
ADD COLUMN IF NOT EXISTS age INTEGER,
ADD COLUMN IF NOT EXISTS gender VARCHAR(10),
ADD COLUMN IF NOT EXISTS nodule_type VARCHAR(20);

-- 为 c_health_records 表添加新字段
ALTER TABLE c_health_records
ADD COLUMN IF NOT EXISTS height FLOAT,
ADD COLUMN IF NOT EXISTS weight FLOAT,
ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS diabetes_history VARCHAR(50),
ADD COLUMN IF NOT EXISTS gaofang_address VARCHAR(255);

-- 验证字段是否添加成功
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'c_patients' 
AND column_name IN ('age', 'gender', 'nodule_type');

SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'c_health_records' 
AND column_name IN ('height', 'weight', 'phone', 'diabetes_history', 'gaofang_address');

