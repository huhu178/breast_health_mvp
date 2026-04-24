-- 修复 b_health_records 表 - 添加缺失字段

-- 添加病程信息字段
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS nodule_discovery_time DATE;
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS course_stage VARCHAR(50);
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS tnm_stage VARCHAR(10);

-- 添加症状详细字段
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS nipple_discharge_type VARCHAR(50);
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS skin_change_type VARCHAR(50);

-- 添加影像学字段
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS boundary_features VARCHAR(100);
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS internal_echo VARCHAR(50);
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS blood_flow_signal VARCHAR(50);
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS elasticity_score VARCHAR(20);

-- 添加生物节律字段
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS rhythm_type VARCHAR(50);
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS cycle_phase VARCHAR(50);
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS sleep_condition VARCHAR(50);

-- 添加检查历史字段
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS exam_history_type VARCHAR(50);
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS exam_history_detail VARCHAR(200);
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS previous_exam_history TEXT;

-- 添加生活方式字段
ALTER TABLE b_health_records ADD COLUMN IF NOT EXISTS lifestyle VARCHAR(50);

-- 验证结果
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'b_health_records' 
ORDER BY ordinal_position;



