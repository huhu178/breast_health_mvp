# C端B端流程说明

## 📋 目录
1. [C端报告生成](#c端报告生成)
2. [C端用户存储](#c端用户存储)
3. [B端管理C端](#b端管理c端)
4. [报告审核流程](#报告审核流程)

---

## ✅ C端报告生成

### 当前状态：**可以正常生成报告**

### 生成流程

1. **C端AI对话完成** → `/api/c/chat/complete` (POST)
   - 用户通过AI对话收集健康信息
   - 数据保存在 `CConversation.collected_data` (JSON格式)

2. **数据规范化**
   - 使用 `normalize_patient_data_for_c()` 规范化数据
   - 清理无效Unicode字符

3. **调用LLM生成报告**
   - 使用 `llm_generator.generate_patient_friendly_report()`
   - 生成C端友好型HTML报告

4. **保存报告**
   - 保存到 `c_reports` 表
   - 状态：`generated`（已生成，无需审核）
   - 报告类型：`patient_friendly`（患者友好型）

### 代码位置
- 路由：`backend/routes/c_patient_service.py`
- 函数：`complete_chat()` (第202行)

### 报告特点
- ✅ 直接生成，无需审核
- ✅ 状态为 `generated`（不是 `draft`）
- ✅ 用户可立即查看和下载

---

## 💾 C端用户存储

### 数据库表结构

C端数据存储在以下表中：

#### 1. **c_patients** - C端患者/线索表
```python
- id: 主键
- patient_code: 患者编号（唯一）
- name: 姓名
- phone: 手机号（唯一，主要标识）
- wechat_openid: 微信OpenID（唯一）
- source_channel: 来源渠道（公众号、短视频等）
- lead_status: 线索状态（new/contacted/booked/reported/conversion/lost）
- assigned_manager_id: 分配的管理师ID（外键关联 users 表）
- first_visit_at: 首次访问时间
- last_activity_at: 最后活动时间
```

#### 2. **c_health_records** - C端健康档案表
```python
- id: 主键
- patient_id: 患者ID（外键）
- record_code: 档案编号（唯一）
- conversation_id: 对话ID（外键）
- 健康信息字段：age, birads_level, family_history, symptoms 等
```

#### 3. **c_reports** - C端报告表
```python
- id: 主键
- patient_id: 患者ID（外键，可为None，支持匿名用户）
- record_id: 档案ID（外键，可为None）
- conversation_id: 对话ID（外键）
- report_code: 报告编号（唯一）
- report_html: HTML格式报告
- report_summary: 报告摘要
- status: 状态（generated/shared/downloaded）
- download_token: 下载令牌
```

#### 4. **c_conversations** - C端AI对话会话表
```python
- id: 主键
- lead_id: 线索ID（外键，关联 c_patients）
- session_id: 会话ID（唯一）
- status: 状态（active/completed/failed）
- collected_data: 收集的数据（JSON格式）
- start_time: 开始时间
- end_time: 结束时间
```

### 数据关系

```
c_patients (患者)
  ├── c_health_records (健康档案)
  ├── c_reports (报告)
  └── c_conversations (对话)
      └── collected_data (JSON格式的健康数据)
```

### 代码位置
- 模型定义：`backend/models.py`
- CPatient: 第755行
- CHealthRecord: 第816行
- CReport: 第864行
- CConversation: 第902行

---

## 🔧 B端管理C端

### 当前状态：**B端可以管理C端用户**

### 管理功能

#### 1. **查看所有患者（B端+C端）**
- 路由：`GET /api/b/patients`
- 参数：
  - `type`: `all`（B端+C端）/ `b_end`（仅B端）/ `c_end`（仅C端）
  - `search`: 搜索关键词（姓名/手机号/患者编号）
  - `status`: 状态筛选
  - `is_new`: 新患者筛选

#### 2. **查看患者详情**
- 路由：`GET /api/b/patients/<patient_id>?type=c_end`
- 返回：患者信息 + 健康档案 + 报告列表

#### 3. **生成C端报告（B端代为生成）**
- 路由：`POST /api/b/patients/<patient_id>/reports/generate`
- 参数：`{"record_id": xxx, "type": "c_end"}`
- 功能：B端管理师可以为C端患者生成报告

#### 4. **查看新患者提醒**
- 路由：`GET /api/b/patients/new`
- 返回：B端新患者 + C端未联系患者

### 代码位置
- 路由：`backend/routes/b_patient_management.py`
- 函数：
  - `get_all_patients()` (第27行) - 获取所有患者
  - `get_patient_detail()` (第297行) - 获取患者详情
  - `generate_patient_report()` (第707行) - 生成报告（支持C端）

### 管理能力总结

| 功能 | B端患者 | C端患者 |
|------|---------|---------|
| 查看列表 | ✅ | ✅ |
| 查看详情 | ✅ | ✅ |
| 创建患者 | ✅ | ❌（C端用户通过对话自动创建）|
| 编辑患者 | ✅ | ⚠️ 部分支持 |
| 生成报告 | ✅ | ✅ |
| 分配管理师 | ✅ | ✅（通过 assigned_manager_id）|

---

## 📝 报告审核流程

### B端报告审核流程

#### 1. **报告生成（草稿状态）**
- 路由：`POST /api/b/reports/generate`
- 状态：`draft`（草稿）
- 内容：AI生成的评估内容（可编辑）

#### 2. **建议审核**
- 路由：`PUT /api/b/reports/<report_id>/recommendations/<index>`
- 功能：逐条审核分类建议，标记 `is_approved`

#### 3. **生成最终报告**
- 路由：`POST /api/b/reports/<report_id>/finalize`
- 功能：整合所有已批准的建议，生成最终报告

#### 4. **审核发布**
- 路由：`POST /api/b/reports/<report_id>/publish`
- 功能：将报告状态从 `draft` 改为 `published`
- 记录：`reviewed_by`（审核人）、`reviewed_at`（审核时间）

#### 5. **报告导出**
- 路由：`GET /api/b/reports/<report_id>/export`
- 要求：只能导出 `published` 状态的报告

### C端报告审核流程

#### **C端报告：无需审核**

- 路由：`POST /api/c/chat/complete`
- 状态：`generated`（已生成）
- 特点：
  - ✅ 直接生成，无需审核
  - ✅ 用户可立即查看
  - ✅ 状态不会变为 `published`

### 小程序报告审核流程

#### **小程序报告：无需审核**

- 路由：`POST /api/miniprogram/questionnaire/submit`
- 状态：`published`（直接发布）
- 特点：
  - ✅ 直接发布，无需审核
  - ✅ 同时保存B端和C端报告

### 报告状态对比

| 报告类型 | 生成时状态 | 是否需要审核 | 最终状态 |
|---------|-----------|------------|---------|
| **B端报告** | `draft` | ✅ **需要** | `published` |
| **C端报告** | `generated` | ❌ **不需要** | `generated` |
| **小程序报告** | `published` | ❌ **不需要** | `published` |

### 审核相关代码

- 审核路由：`backend/routes/b_report_update.py`
- 建议审核：`backend/routes/b_report_management.py` (第280-400行)
- 发布报告：`backend/routes/b_report_update.py` (第77行)

---

## 📊 数据流程总结

### C端用户流程

```
用户访问C端
  ↓
创建/获取CPatient（c_patients表）
  ↓
开始AI对话（CConversation）
  ↓
收集健康数据（collected_data JSON）
  ↓
完成对话，生成报告（CReport，status='generated'）
  ↓
用户查看/下载报告
```

### B端管理流程

```
B端管理师登录
  ↓
查看患者列表（B端+C端）
  ↓
选择C端患者查看详情
  ↓
（可选）为C端患者生成报告
  ↓
（仅B端报告）审核并发布报告
```

---

## ⚠️ 注意事项

1. **C端报告无需审核**
   - C端报告状态为 `generated`，不是 `draft`
   - 没有审核流程，直接可用

2. **B端可以管理C端**
   - B端可以查看C端患者列表和详情
   - B端可以为C端患者生成报告
   - C端患者可以分配给B端管理师（`assigned_manager_id`）

3. **报告状态区别**
   - B端报告：`draft` → `published`（需要审核）
   - C端报告：`generated`（无需审核）
   - 小程序报告：`published`（无需审核）

4. **数据存储**
   - C端用户数据存储在独立的C端表中（`c_patients`, `c_reports` 等）
   - 与B端数据完全分离，但B端可以访问

---

**最后更新**：2026-01-20


