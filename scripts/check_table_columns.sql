-- ============================================
-- 检查表字段是否完整
-- ============================================

-- 1. 查看 b_health_records 表的所有字段
SELECT 
    column_name AS "字段名",
    data_type AS "数据类型",
    character_maximum_length AS "最大长度",
    is_nullable AS "可为空"
FROM information_schema.columns 
WHERE table_name = 'b_health_records' 
ORDER BY ordinal_position;

-- 2. 统计字段数量
SELECT 
    COUNT(*) AS "b_health_records字段总数"
FROM information_schema.columns 
WHERE table_name = 'b_health_records';

-- 3. 查看 c_health_records 表的所有字段
SELECT 
    column_name AS "字段名",
    data_type AS "数据类型",
    character_maximum_length AS "最大长度",
    is_nullable AS "可为空"
FROM information_schema.columns 
WHERE table_name = 'c_health_records' 
ORDER BY ordinal_position;

-- 4. 统计字段数量
SELECT 
    COUNT(*) AS "c_health_records字段总数"
FROM information_schema.columns 
WHERE table_name = 'c_health_records';

-- 5. 检查关键字段是否存在
SELECT 
    table_name AS "表名",
    EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='b_health_records' AND column_name='nodule_discovery_time') AS "有nodule_discovery_time",
    EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='b_health_records' AND column_name='boundary_features') AS "有boundary_features",
    EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='b_health_records' AND column_name='internal_echo') AS "有internal_echo",
    EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='b_health_records' AND column_name='rhythm_type') AS "有rhythm_type",
    EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='b_health_records' AND column_name='exam_history_type') AS "有exam_history_type",
    EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='b_health_records' AND column_name='lifestyle') AS "有lifestyle"
FROM (SELECT 'b_health_records' AS table_name) t;

-- 6. 完整的字段列表对照（应该有的字段）
/*
应该有以下32个字段：
1. id
2. patient_id
3. record_code
4. age
5. birads_level
6. family_history
7. nodule_discovery_time  ← 缺失检查
8. course_stage           ← 缺失检查
9. tnm_stage             ← 缺失检查
10. symptoms
11. pain_level
12. pain_type
13. nipple_discharge_type ← 缺失检查
14. skin_change_type      ← 缺失检查
15. nodule_location
16. nodule_size
17. boundary_features     ← 缺失检查
18. internal_echo         ← 缺失检查
19. blood_flow_signal     ← 缺失检查
20. elasticity_score      ← 缺失检查
21. rhythm_type           ← 缺失检查
22. cycle_phase           ← 缺失检查
23. sleep_quality
24. sleep_condition       ← 缺失检查
25. exam_history_type     ← 缺失检查
26. exam_history_detail   ← 缺失检查
27. previous_exam_history ← 缺失检查
28. exercise_frequency
29. lifestyle             ← 缺失检查
30. data_completeness (B端) / source (C端)
31. created_by (B端) / conversation_id (C端)
32. status
33. created_at
34. updated_at

总共：B端应该有33个字段，C端应该有32-34个字段
*/

