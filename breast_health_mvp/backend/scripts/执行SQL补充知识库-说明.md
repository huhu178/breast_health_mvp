# SQL补充知识库 - 执行指南

## 📋 补充内容

- **文件**：`补充缺失知识库.sql`
- **条目数**：10条
- **总耗时**：约30秒

## 🚀 执行步骤

### 方法1：使用SQLite命令行（推荐）

```bash
# 1. 进入项目根目录
cd d:\1work\20251016

# 2. 执行SQL文件
sqlite3 breast_nodule.db < breast_health_mvp/backend/scripts/补充缺失知识库.sql

# 3. 验证结果
sqlite3 breast_nodule.db "SELECT COUNT(*) FROM unified_knowledge_base WHERE source_type = 'timeline';"
```

**预期结果**：应显示 `45`（原35条 + 新增10条）

---

### 方法2：使用DB Browser for SQLite

1. 下载安装 [DB Browser for SQLite](https://sqlitebrowser.org/dl/)
2. 打开 `d:\1work\20251016\breast_nodule.db`
3. 点击"执行SQL"标签页
4. 复制粘贴 `补充缺失知识库.sql` 的全部内容
5. 点击"执行"按钮（▶️）
6. 查看执行结果

---

### 方法3：使用Python脚本

```python
# 在 backend 目录下运行
cd breast_health_mvp/backend
python -c "
import sqlite3
conn = sqlite3.connect('../../breast_nodule.db')
with open('scripts/补充缺失知识库.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
conn.executescript(sql)
conn.commit()
print('✅ 补充完成！')
conn.close()
"
```

---

## ✅ 验证补充结果

执行以下SQL查询验证：

```sql
-- 1. 检查总数（应为45条）
SELECT COUNT(*) as 总数 
FROM unified_knowledge_base 
WHERE source_type = 'timeline';

-- 2. 查看新增的10条
SELECT id, title, age_range, tnm_stage, course_stage
FROM unified_knowledge_base
WHERE source_type = 'timeline'
ORDER BY id DESC
LIMIT 10;

-- 3. 分年龄段统计
SELECT 
    age_range,
    COUNT(*) as 条目数
FROM unified_knowledge_base
WHERE source_type = 'timeline'
GROUP BY age_range
ORDER BY age_min;
```

**预期结果**：
```
年龄段    条目数
20-35     10条
36-45     10条
46-60     11条
60+       14条
总计      45条
```

---

## 📊 补充的10条明细

| 序号 | 年龄段 | 病程 | TNM期 | 标题 |
|------|--------|------|-------|------|
| 1 | 20-35 | 新发 | 1期 | 时间轴建议-20-35岁新发TNM1期 |
| 2 | 36-45 | 新发 | 5期 | 时间轴建议-36-45岁新发TNM5期 |
| 3 | 36-45 | 新发 | 6期 | 时间轴建议-36-45岁新发TNM6期 |
| 4 | 36-45 | 稳定 | 3期 | 时间轴建议-36-45岁稳定TNM3期 |
| 5 | 36-45 | 稳定 | 4期 | 时间轴建议-36-45岁稳定TNM4期 |
| 6 | 46-60 | 稳定 | 6期 | 时间轴建议-46-60岁稳定TNM6期 |
| 7 | 60+ | 新发 | 6期 | 时间轴建议-60+岁新发TNM6期 |
| 8 | 60+ | 稳定 | 3期 | 时间轴建议-60+岁稳定TNM3期 |
| 9 | 60+ | 稳定 | 5期 | 时间轴建议-60+岁稳定TNM5期 |
| 10 | 60+ | 稳定 | 6期 | 时间轴建议-60+岁稳定TNM6期 |

---

## ⚠️ 注意事项

1. **备份数据库**（可选但推荐）
   ```bash
   copy breast_nodule.db breast_nodule_backup_20251030.db
   ```

2. **检查SQLite版本**
   ```bash
   sqlite3 --version
   # 推荐版本：3.35+
   ```

3. **字符编码**
   - 确保SQL文件是 UTF-8 编码
   - 内容包含中文，需要正确的编码支持

---

## 🔧 常见问题

### Q1: 执行后ID不连续怎么办？
**A**: 正常现象，不影响功能。SQLite会自动分配下一个可用ID。

### Q2: 如何撤销补充？
**A**: 执行以下SQL删除新增的10条：
```sql
DELETE FROM unified_knowledge_base 
WHERE source_type = 'timeline' 
AND id > 39;
```

### Q3: 如何重新执行？
**A**: 先删除（见Q2），再重新执行SQL文件。

---

## 📞 支持

遇到问题请检查：
1. 数据库文件路径是否正确
2. SQL文件编码是否为UTF-8
3. SQLite版本是否过低

执行成功后，你的知识库就完整了！🎉

