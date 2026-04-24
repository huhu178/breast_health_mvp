# 多结节健康管理系统 PRD + 技术实施方案 + 分阶段开发任务书

> 版本：v1.0 | 日期：2026-04-22 | 状态：待确认

---

## 一、项目背景

### 1.1 现有资产

**旧项目（已开发，部分上线）**

- 后端：Flask + PostgreSQL，已有完整的患者建档、健康档案（100+字段，支持乳腺/肺/甲状腺及6种组合结节）、报告生成（LLM驱动）、报告复核、PDF导出能力
- B端前端：Vue 3 + Element Plus，已有患者列表、患者详情、多结节表单（6种组合）、报告查看、知识库、企微管理页面
- C端前端：Vue 3，已有AI健康咨询对话、报告查看、小程序问卷
- 微信小程序：原生小程序，支持问卷填写、报告查看、舌象采集
- AI能力：OpenRouter/Qwen LLM驱动的报告生成、风险评估决策树、知识库匹配（50+维度）
- 数据库：已有 users、b_patients、b_health_records、b_reports、b_follow_up_records、c_patients、c_conversations、c_messages 等核心表

**新原型（已完成交互设计，待落地）**

- 文件：`结节项目四场景demo原型.html`
- 内容：多场景B端工作台，包含医院问诊、医院体检中心、社区、健康管理中心、药店管理5个场景
- 结构：三栏主工作台（患者队列 + 企微会话 + AI助手工作区）+ 底部面板（待办/随访/指标）+ 真实世界研究视图
- 状态：纯前端演示，全部假数据，无后端对接

### 1.2 当前目标

**不是**推翻旧项目重写，**不是**把原型做成孤立静态页面。

**是**：以旧项目已有的前后端能力为基础，将新原型的页面结构、交互方式和业务场景逐步合并，形成一套**多结节核心能力 × 多机构版本化交付**的完整系统。

---

## 二、项目定位

### 2.1 核心定位

**多结节健康管理系统的多机构版本化交付平台**

- 核心能力层：患者建档、多结节健康档案、AI报告生成、风险分层、随访管理、AI助手服务
- 版本层：同一套核心能力，面向医院、体检中心、社区、药店/健康管理中心形成差异化配置版本
- 不是四个独立系统，不是一个后台四个Tab，而是**一套引擎 + 多套皮肤 + 多套业务规则**

### 2.2 产品形态

| 端 | 形态 | 用户 |
|---|---|---|
| B端工作台 | Vue 3 SPA（PC） | 医生、健康管理师、药师、家庭医生、体检中心工作人员 |
| C端小程序 | 微信小程序 | 患者/居民/会员 |
| C端H5 | Vue 3 SPA（移动） | 患者/居民/会员（非小程序场景） |
| 企微AI助手 | 企业微信服务池 | 患者（企微侧）+ 管理师（B端监控） |
| 管理后台 | B端工作台子模块 | 平台管理员、机构管理员 |

---

## 三、核心业务闭环

```
患者来源（门诊/体检/社区活动/药店到访/小程序扫码/企微推广）
    │
    ▼
建立患者档案
（B端录入 / 小程序自助建档 / 体检数据导入 / 门店扫码建档）
    │
    ▼
填写问卷 / 录入健康档案
（多结节信息 + 症状 + 家族史 + 慢病史 + 生活方式 + 影像报告上传）
    │
    ▼
上传或录入检查信息
（影像报告PDF解析 / 手动录入BI-RADS/Lung-RADS/TI-RADS分级）
    │
    ▼
AI生成多结节健康管理报告
（风险分层 + 影像评估 + 疾病史评估 + 个性化建议 + 随访计划）
    │
    ▼
专业人员复核
（医生/健康管理师/药师 在B端工作台审核、修改、签发）
    │
    ▼
小程序展示 / 患者确认
（患者在小程序查看报告 + 确认已读 + 可下载PDF）
    │
    ▼
获取患者微信 / 添加企业微信
（报告页引导添加企微 / 管理师主动添加 / 小程序授权）
    │
    ▼
进入企业微信AI助手服务池
（患者进入企微后自动分配AI助手 + 标签打标 + 服务分层）
    │
    ▼
AI助手持续管理
（复查提醒 / 随访问卷 / 健康科普 / 用药提醒 / 情绪疏导）
    │
    ▼
异常情况转人工
（高危信号 / 患者情绪危机 / 手术确认 / 药师审核 → 转对应专业人员）
    │
    ▼
随访 / 复查提醒 / 转诊
（按随访计划执行 + 逾期自动提醒 + 高危上转 + 术后下转）
    │
    ▼
数据沉淀与统计分析
（患者数 / 报告数 / 随访率 / 转化率 / 高危跟进率 / 真实世界研究入组）
```

---

## 四、用户角色

| 角色 | 所属版本 | 主要职责 | 系统权限 |
|---|---|---|---|
| 患者/居民/会员 | 全版本 | 填写问卷、查看报告、接收随访、企微沟通 | C端小程序/H5 |
| 医生 | 医院版 | 复核报告、确认手术指征、接收转诊 | B端工作台（复核权限） |
| 健康管理师 | 全版本 | 建档、报告管理、随访执行、企微服务 | B端工作台（全功能） |
| 家庭医生 | 社区版 | 签约管理、异常干预、双向转诊 | B端工作台（社区模块） |
| 药师 | 药店版/医院版 | 用药审核、药事咨询、药食同源建议 | B端工作台（药师审核权限） |
| 社区工作人员 | 社区版 | 居民档案管理、活动组织、随访协助 | B端工作台（社区权限） |
| 体检中心工作人员 | 体检版 | 体检数据导入、检后解释、复查路径 | B端工作台（体检权限） |
| 药店店员/店长 | 药店版 | 门店建档、会员管理、药师转接 | B端工作台（药店权限） |
| 平台管理员 | 全版本 | 机构管理、用户管理、版本配置、数据统计 | 管理后台（超级权限） |
| AI助手 | 全版本 | 自动随访、健康咨询、内容推送、转人工判断 | 企微服务池（系统角色） |

---

## 五、版本/解决方案范围

### 5.1 医院版多结节系统

**使用对象**：门诊医生、健康管理师

**业务目标**：门诊结节人群分层管理，健康报告生成、随访编排、转诊提示与多角色协同

**核心流程**：
门诊就诊 → 医生/管理师建档 → 录入影像信息 → AI生成报告 → 医生复核签发 → 患者小程序查看 → 添加企微 → AI助手随访 → 异常转医生 → 手术/复查跟踪

**工作台模块**：患者队列（含风险分层）、企微会话区、AI助手工作区、待办任务、随访记录、运行指标

**AI助手配置**：AI健康管理师（主）、AI心理咨询师、AI慢病管理师、AI运动康复师、AI药师、AI健康生活方式规划师、AI健康福利官

**专业复核角色**：主治医生（手术指征确认）、健康管理师（报告审核）

**关键指标**：院外随访率、术后跟踪率、医生复核命中数、今日新建档案数

**与小程序/企微的关系**：患者通过小程序查看报告后引导添加企微；企微AI助手承接术后随访和复查提醒

---

### 5.2 体检中心版多结节系统

**使用对象**：体检中心工作人员、健康管理师

**业务目标**：承接院内体检阳性患者，完成检后解释、复查路径确认、高危转门诊

**核心流程**：
体检完成 → 阳性结果自动识别 → 批量建档/导入 → AI生成检后解释报告 → 管理师复核 → 患者小程序查看 → 添加企微 → AI助手检后触达 → 高危转门诊提示

**工作台模块**：患者队列（体检批次管理）、检后解释工作区、企微会话区、待办任务（批量处理）、运行指标

**AI助手配置**：AI健康管理师（主）、AI慢病管理师、AI健康福利官、AI中医药膳师、AI心理咨询师

**专业复核角色**：健康管理师（报告审核）、体检中心医生（高危确认）

**关键指标**：阳性触达率、高危跟进率、随访反馈率、体检再检率

**与小程序/企微的关系**：体检报告通过小程序推送；企微AI助手承接检后解释和复查提醒

---

### 5.3 社区版多结节系统

**使用对象**：家庭医生、社区工作人员、健康管理师

**业务目标**：以AI名医分身和慢病大讲堂为入口，沉淀辖区居民健康档案，按病种完成分层随访、家庭医生干预和双向转诊

**核心流程**：
社区活动/名医大讲堂 → 居民扫码建档 → 填写问卷 → AI生成报告 → 家庭医生复核 → 居民小程序查看 → 添加企微 → AI助手随访 → 异常上转医院 → 术后下转承接

**工作台模块**：患者队列（辖区居民）、家庭医生任务区、企微会话区、双向转诊管理、随访记录、运行指标

**AI助手配置**：AI健康管理师（主）、AI慢病管理师、AI中医药膳师、AI心理咨询师、AI运动康复师

**专业复核角色**：家庭医生（报告审核 + 转诊决策）

**关键指标**：患者识别率、自动随访率、异常处理率、转诊成功率

**与小程序/企微的关系**：社区活动通过小程序扫码建档；企微AI助手承接长期慢病随访

---

### 5.4 药店版/健康管理中心版多结节系统

**使用对象**：药店店员/店长、药师、健康管理师

**业务目标**：以药店数字人/健康管理中心为入口，围绕健康科普、药师审核和用药随访，完成会员健康管理与高危转医院闭环

**核心流程**：
门店到访/扫码 → 建档 → 舌象采集（可选）→ 填写问卷 → AI生成报告 → 药师/管理师复核 → 会员小程序查看 → 添加企微 → AI助手随访 → 高危转医院提示

**工作台模块**：患者队列（会员管理）、药师审核工作区、企微会话区、待办任务、运行指标

**AI助手配置**：AI药师（主）、AI健康管理师、AI中医药膳师、AI健康生活方式规划师、AI健康福利官

**专业复核角色**：药师（药事建议审核）、健康管理师（报告审核）

**关键指标**：今日建档数、舌象采集数、药师审核数、转诊线索数

**与小程序/企微的关系**：门店扫码进入小程序建档；企微AI助手承接用药随访和复查提醒

---

## 六、核心功能模块 PRD

### 6.1 患者建档模块

**建档入口**

| 入口 | 场景 | 说明 |
|---|---|---|
| B端手动录入 | 医院/体检/社区/药店 | 管理师在工作台直接录入患者基本信息 |
| 小程序自助建档 | 全版本 | 患者扫码进入小程序，填写基本信息和问卷 |
| 体检数据导入 | 体检版 | 批量导入体检系统阳性结果（CSV/API对接） |
| 门店扫码建档 | 药店版 | 药店数字人/二维码引导到访会员扫码建档 |
| 企微活动建档 | 全版本 | 企微推广活动链接引导用户进入小程序建档 |

**必填字段**

- 姓名、性别、年龄、手机号
- 结节类型（乳腺/肺/甲状腺/组合）
- 来源渠道
- 归属管理师

**选填字段**

- 微信号、企微状态
- 身份证号（用于体检数据匹配）
- 机构/门店信息

**患者状态流转**（详见第七章）

**与其他模块的关系**

- 建档后自动创建健康档案记录（空档案）
- 建档后可立即发起问卷填写
- 建档后可关联小程序用户（通过手机号或openid）
- 建档后可关联企微用户（通过手机号或企微unionid）

---

### 6.2 问卷与健康档案模块

**问卷类型**

| 问卷 | 触发时机 | 填写方 |
|---|---|---|
| 基础风险问卷 | 建档后 | 患者（小程序）/ 管理师代填（B端） |
| 多结节健康档案 | 建档后 | 管理师（B端）/ 患者（小程序辅助） |
| 随访问卷 | 随访任务触发 | 患者（小程序/企微）/ 管理师代填 |
| 术后康复问卷 | 手术后 | 患者（小程序）/ 管理师代填 |

**健康档案采集维度**（基于现有 b_health_records 表）

- 基本信息：年龄、身高、体重、联系方式
- 结节信息（按类型）：
  - 乳腺：BI-RADS分级、结节位置/大小/边界/回声/血流、发现时间、数量
  - 肺：Lung-RADS分级、结节位置/大小/边界特征、发现时间、数量
  - 甲状腺：TI-RADS分级、结节位置/大小/边界/回声/血流、发现时间、数量
- 症状信息：各器官症状（多选）、疼痛程度、乳头溢液、皮肤改变
- 疾病史：各器官基础疾病史、既往活检史、手术史
- 家族史：各器官家族遗传史
- 风险因素：吸烟史、辐射暴露、避孕药使用、糖尿病控制情况
- 用药史：各器官相关用药
- 生活方式：运动频率、睡眠质量、生物节律
- 影像报告：PDF上传（自动解析）或手动录入

**多结节组合支持**（现有6种，需在新工作台中统一入口）

- 单结节：乳腺 / 肺 / 甲状腺
- 双结节：乳腺+肺 / 乳腺+甲状腺 / 肺+甲状腺
- 三结节：乳腺+肺+甲状腺

**填写方式**

- B端代填：管理师在工作台打开患者档案，逐步填写
- 小程序自填：患者在小程序完成问卷，数据同步到B端
- 影像报告解析：上传PDF，后端自动提取关键字段（现有能力）

---

### 6.3 多结节报告生成模块

**报告生成入口**

- B端工作台：患者详情页 → 生成报告按钮
- B端工作台：企微会话区快捷操作 → 生成健康报告
- 小程序：患者完成问卷后自动触发（可配置）

**生成条件**

- 患者已建档
- 健康档案完整度 ≥ 60%（可配置阈值）
- 至少有一种结节的影像信息（分级或报告）

**报告内容结构**

1. 患者基本信息摘要
2. 结节概况（各结节类型、分级、发现时间）
3. 影像学评估（AI分析 + 风险提示）
4. 疾病史与风险因素评估
5. 综合风险评分（0-100）+ 风险等级（低危/中危/高危）
6. 个性化管理建议（复查频率、生活方式、注意事项）
7. 随访计划（下次复查时间、随访方式）
8. 专业人员签名区（复核后显示）

**风险分层规则**（基于现有决策树 decision_tree.py）

- 低危：BI-RADS 1-2 / Lung-RADS 1-2 / TI-RADS 1-2，无高危因素
- 中危：BI-RADS 3 / Lung-RADS 3 / TI-RADS 3，或有部分风险因素
- 高危：BI-RADS 4A及以上 / Lung-RADS 4及以上 / TI-RADS 4及以上，或多重风险因素叠加

**报告状态流转**（详见第七章）

**PDF/小程序展示**

- B端：在线预览HTML版 + 下载PDF（Playwright生成）
- 小程序：患者端查看简化版报告 + 确认已读
- 企微：可发送报告摘要链接给患者

**专业复核流程**

1. 报告生成后状态为"待复核"
2. 系统通知对应复核人（医生/管理师/药师）
3. 复核人在B端工作台查看、修改、填写复核意见
4. 复核通过后状态变为"已复核"，可发送给患者
5. 复核拒绝后退回，管理师修改后重新提交

---

### 6.4 小程序患者端模块

**功能列表**

| 功能 | 说明 | 现有状态 |
|---|---|---|
| 建档/注册 | 手机号验证 + 基本信息填写 | 已有（c_auth_routes） |
| 问卷填写 | 多结节问卷，支持影像报告上传 | 已有（miniprogram_routes） |
| 查看报告 | 查看已复核的健康管理报告 | 已有（c_patient_service） |
| 确认已读 | 患者确认查看报告 | 需新增状态字段 |
| 添加微信/企微 | 报告页展示管理师企微二维码 | 已有展示，需完善状态回写 |
| 接收复查提醒 | 企微/小程序消息推送 | 需新增推送逻辑 |
| 随访反馈 | 填写随访问卷，反馈症状变化 | 需新增随访问卷模块 |
| AI健康咨询 | 与AI助手对话 | 已有（c_patient_service chat） |

**小程序与B端的数据同步**

- 患者在小程序填写的问卷数据 → 同步到 b_health_records（通过手机号关联）
- 患者查看报告的状态 → 回写到 b_reports（patient_viewed_at 字段）
- 患者添加企微的状态 → 回写到 b_patients（wechat_status 字段）

---

### 6.5 企业微信AI助手端模块

**企微患者服务池**

- 患者添加企微后自动进入服务池
- 服务池按风险等级分层：高危优先队列 / 中危常规队列 / 低危自动队列
- 每个患者关联：基本信息、报告摘要、随访计划、历史对话记录
- 管理师可在B端工作台查看服务池状态和会话记录

**AI助手会话**

- 患者发送消息 → AI助手自动回复
- 回复内容基于：患者档案 + 报告信息 + 知识库 + 随访计划
- 支持多轮对话，保留上下文
- 会话记录实时同步到B端工作台

**多AI协同机制**

每个版本配置不同的AI助手组合，AI助手按职责分工：

| AI角色 | 职责 | 触发条件 |
|---|---|---|
| AI健康管理师 | 主助手，随访执行、方案解释、日常对话 | 默认激活 |
| AI药师 | 用药咨询、相互作用提醒 | 患者提及用药问题时激活 |
| AI慢病管理师 | 高血压/糖尿病等共病长期管理 | 档案有慢病史时激活 |
| AI心理咨询师 | 结节焦虑疏导、情绪支持 | 检测到焦虑情绪时激活 |
| AI运动康复师 | 术后运动康复、强度控制 | 术后随访阶段激活 |
| AI健康生活方式规划师 | 饮食、作息、控烟计划 | 生活方式干预阶段激活 |
| AI健康福利官 | 复查提醒、权益说明 | 定期触达时激活 |
| AI中医药膳师 | 体质辨识与药膳建议（需合规审核） | 药店/社区版，患者主动询问时激活 |

**转人工规则**（按版本配置）

- 医院版：胸痛/咯血 → 转医生；手术判断 → 转主治医生；患者情绪危机 → 转心理科
- 体检版：高风险报告 → 提示转门诊医生；患者拒绝复查 → 通知体检中心
- 社区版：异常预警 → 转家庭医生；高风险 → 上转建议；术后下转 → 承接随访
- 药店版：高危信号 → 提示转医院；用药冲突 → 药师审核；体质异常 → 生活方式干预

**任务生成**

- AI助手在对话中识别到需要人工处理的事项，自动生成待办任务
- 任务推送到B端工作台待办列表
- 管理师处理后，结果回写到对话记录

**内容话术模板**

- 复查提醒模板（按结节类型、风险等级、距上次复查时间）
- 随访问卷推送模板
- 健康科普推送模板（按结节类型）
- 节日关怀模板
- 高危预警通知模板

**服务记录回写**

- 所有AI对话记录 → 存储到 enterprise_wechat_sessions / enterprise_wechat_messages 表
- 关键事件（转人工、任务生成、患者确认）→ 回写到 b_follow_up_records
- 患者标签变更 → 回写到 patient_tags 表

**患者标签与分层**

- 系统标签（自动）：风险等级、结节类型、随访状态、企微状态
- 业务标签（手动）：重点关注、术后患者、逾期复查、高依从性
- 标签用于：AI助手个性化回复、批量推送筛选、统计分析

**与其他模块的关系**

- 企微会话 ↔ B端工作台：实时同步，管理师可在工作台查看和介入
- 企微会话 ↔ 报告模块：AI助手可发送报告摘要链接
- 企微会话 ↔ 随访任务：随访任务触发企微消息推送
- 企微会话 ↔ 小程序：引导患者在小程序完成随访问卷

---

### 6.6 B端工作台模块

**整体布局**（基于新原型三栏结构）

```
┌─────────────────────────────────────────────────────────┐
│  顶部导航：Logo + 场景切换 + 用户信息 + 机构/角色标识    │
├──────────┬──────────────────────────────────────────────┤
│          │  状态栏：待办数 / 待确认数 / 转人工数 / 逾期数 │
│  侧边栏  ├────────────┬──────────────┬──────────────────┤
│  场景导航 │  患者队列  │  企微会话区  │  AI助手工作区    │
│          │  （左栏）  │  （中栏）    │  （右栏）        │
│          ├────────────┴──────────────┴──────────────────┤
│          │  底部面板：待办任务 | 随访记录 | 运行指标      │
└──────────┴──────────────────────────────────────────────┘
```

**患者队列（左栏）**

- 搜索：姓名/手机号/患者编号
- 筛选：风险等级（高危/中危/低危）、结节类型、状态、企微状态
- 列表项：患者姓名、结节类型标签、风险等级标签、当前状态、最近随访时间
- 操作：点击进入患者详情、快速新建档案

**企微会话区（中栏）**

- 患者信息卡：姓名、结节类型、风险等级、下次复查时间
- 快捷操作按钮：生成健康报告、查看报告、安排复查、发送科普、转医生、生成随访表
- 消息流：AI消息、患者消息、系统通知（三种气泡样式）
- 输入区：管理师可直接发送消息（以人工身份）
- 会话切换：点击患者队列中的患者切换会话

**AI助手工作区（右栏）**

- AI员工列表：显示当前激活的AI助手及状态
- 转人工规则：当前版本的转人工触发条件
- AI助手配置入口：管理员可调整AI助手组合

**待办任务（底部左列）**

- 优先级标签（高/中/低）
- 任务描述
- 任务状态（待确认/待处理/待触达/运行中）
- 来源（AI生成/手动创建）
- 操作：标记完成、转派

**随访记录（底部中列）**

- 随访类型（报告/术后/对话/体检/问卷/方案）
- 随访标题和摘要
- 随访时间
- 操作：查看详情、新建随访

**运行指标（底部右列）**

- 4个核心指标（按版本不同显示不同指标）
- 数字 + 标签的简洁展示

**不同版本工作台差异**

| 模块 | 医院版 | 体检版 | 社区版 | 药店版 |
|---|---|---|---|---|
| 患者队列筛选 | 风险/状态/结节类型 | 体检批次/风险/状态 | 辖区/家庭医生/风险 | 门店/会员等级/风险 |
| 快捷操作 | 生成报告/转医生/手术确认 | 生成解释/复查建议/转诊提示 | 预约复查/同步家医/上转建议 | 生成报告/药师审核/转医院提示 |
| 转人工规则 | 手术判断/情绪危机 | 高风险/拒绝复查 | 异常预警/高风险上转 | 高危信号/用药冲突 |
| 运行指标 | 院外随访率/术后跟踪率 | 阳性触达率/高危跟进率 | 患者识别率/转诊成功率 | 今日建档/药师审核数 |
| 专项模块 | 手术确认工作流 | 体检批次管理 | 家庭医生任务/双向转诊 | 药师审核工作区/舌象管理 |

---

### 6.7 社区专项模块

**AI名医大讲堂**

- 功能：AI名医分身在企微/小程序进行健康科普直播或图文推送
- 内容：结节科普、慢病管理、生活方式干预
- 入口：社区活动二维码 → 小程序 → 建档
- 数据：参与人数、建档转化率、问卷完成率

**慢病大讲堂**

- 功能：针对高血压、糖尿病等慢病合并结节人群的专项管理
- 内容：慢病+结节共管方案、用药注意事项、生活方式建议
- 触发：档案中有慢病史的患者自动纳入

**病种管理包**

- 功能：按结节类型+慢病类型组合，提供标准化管理方案包
- 内容：随访计划模板、科普内容包、转诊标准
- 配置：管理员在后台配置，家庭医生可调整

**家庭医生任务**

- 功能：家庭医生在工作台查看签约患者的待处理任务
- 任务类型：异常预警确认、上转建议审批、随访计划调整、下转患者承接
- 通知：系统消息 + 企微通知

**双向转诊**

- 上转：社区识别高危患者 → 生成上转建议 → 家庭医生确认 → 推送给患者 → 患者到医院就诊 → 结果回传
- 下转：医院术后患者 → 生成下转单 → 社区承接 → 纳入术后随访队列

---

### 6.8 药店专项模块

**药店数字人**

- 功能：药店门口/收银台展示AI数字人，引导到访顾客扫码建档
- 入口：扫码 → 小程序 → 建档 + 问卷
- 数据：扫码数、建档转化率

**会员健康教育**

- 功能：针对药店会员推送结节相关健康科普
- 内容：结节科普、用药注意事项、饮食建议
- 触发：建档后自动推送 + 定期推送

**用药随访**

- 功能：针对有用药史的患者，定期随访用药情况
- 内容：用药依从性、副作用、药食同源建议
- 触发：随访计划中包含用药随访节点

**药师审核**

- 功能：AI药师生成的用药建议需要真实药师审核后才能发送给患者
- 流程：AI生成建议 → 待审核队列 → 药师审核 → 通过/修改 → 发送患者
- 工作台：药师审核专属工作区，显示待审核列表

**高危转医院提示**

- 触发条件：报告风险等级为高危 / 出现高危症状 / 用药冲突严重
- 处理：AI助手发送转医院提示 → 管理师确认 → 推送给患者 → 记录转诊线索

---

### 6.9 统计与数据沉淀模块

**核心指标（全版本）**

| 指标 | 说明 | 数据来源 |
|---|---|---|
| 患者总数 | 已建档患者数 | b_patients |
| 报告生成数 | 已生成报告数 | b_reports |
| 微信添加率 | 已添加企微/已建档 | b_patients.wechat_status |
| 企微服务率 | 企微服务中/已添加企微 | enterprise_wechat_sessions |
| 随访完成率 | 已完成随访/应完成随访 | follow_up_tasks |
| 高危转人工数 | 触发转人工规则次数 | enterprise_wechat_sessions |
| 复查完成率 | 已复查/应复查 | follow_up_tasks |
| 报告复核率 | 已复核/已生成 | b_reports |

**各版本差异指标**

- 医院版：院外随访率、术后跟踪率、医生复核命中数
- 体检版：阳性触达率、高危跟进率、体检再检率
- 社区版：患者识别率、转诊成功率、家庭医生任务完成率
- 药店版：今日建档数、舌象采集数、药师审核数、转诊线索数

**真实世界研究（RWS）数据沉淀**

- 研究项目管理：入组标准、排除标准、主要终点、次要终点
- 患者入组：符合条件的患者自动提示入组
- 随访数据采集：按研究方案的随访节点采集数据
- 数据质控：缺失字段提醒、异常值标记
- 数据导出：符合研究要求的结构化数据导出

---

## 七、状态流转设计

### 7.1 患者状态机

```
未建档
  │ 建档（B端录入/小程序/体检导入）
  ▼
已建档（档案空）
  │ 填写问卷/健康档案
  ▼
档案填写中
  │ 档案完整度 ≥ 60%
  ▼
已完成档案
  │ 触发报告生成
  ▼
报告生成中
  │ 报告生成完成
  ▼
待复核
  │ 专业人员复核通过
  ▼
已复核（可发送患者）
  │ 发送给患者
  ▼
已发送患者
  │ 患者在小程序查看
  ▼
患者已查看报告
  │ 患者添加企微
  ▼
已添加企微
  │ 进入服务池
  ▼
企微服务中
  │ 持续随访
  ▼
随访中（长期状态）
  │ 出现异常
  ├──→ 需人工介入
  │ 完成随访周期
  └──→ 随访完成/归档
```

**患者状态枚举值**

| 状态值 | 显示名 | 说明 |
|---|---|---|
| `new` | 新建档 | 刚建档，档案未填写 |
| `filling` | 填写中 | 档案填写进行中 |
| `pending_report` | 待生成报告 | 档案完整，等待生成报告 |
| `pending_review` | 待复核 | 报告已生成，等待专业人员复核 |
| `report_ready` | 报告已就绪 | 报告已复核，可发送患者 |
| `report_sent` | 报告已发送 | 报告已推送给患者 |
| `report_viewed` | 已查看报告 | 患者已在小程序查看报告 |
| `wechat_pending` | 待添加企微 | 已引导添加，等待患者操作 |
| `wechat_added` | 已添加企微 | 患者已添加企微 |
| `in_service` | 服务中 | 在企微AI助手服务池中 |
| `following_up` | 随访中 | 进入随访计划执行阶段 |
| `overdue` | 逾期 | 随访或复查逾期未完成 |
| `transferred` | 已转诊 | 已上转或下转 |
| `archived` | 已归档 | 随访完成或失访 |

---

### 7.2 报告状态机

```
（触发生成）
  │
  ▼
生成中（generating）
  │ LLM生成完成
  ▼
草稿（draft）
  │ 提交复核
  ▼
待复核（pending_review）
  │ 复核通过          │ 复核拒绝
  ▼                   ▼
已复核（reviewed）   已退回（rejected）
  │                   │ 管理师修改后重新提交
  │ 发送给患者         └──→ 待复核
  ▼
已发布（published）
  │ 患者查看
  ▼
患者已查看（patient_viewed）
  │ 有新档案信息，需更新
  ▼
已归档（archived）
```

---

### 7.3 微信/企微状态机

```
未获取微信（none）
  │ 患者填写微信号 / 小程序授权
  ▼
已获取微信号（wechat_id_collected）
  │ 管理师主动添加 / 系统引导患者添加
  ▼
待添加（pending_add）
  │ 患者通过好友申请
  ▼
已添加个人微信（personal_wechat_added）
  │ 迁移到企微 / 直接添加企微
  ▼
待进入企微服务池（enterprise_pending）
  │ 患者添加企微账号
  ▼
已进入企微服务池（in_enterprise_pool）
  │ AI助手开始服务
  ▼
企微服务中（enterprise_serving）
  │ 出现需人工介入情况
  ├──→ 需人工介入（human_required）
  │ 患者长期未响应
  └──→ 静默（silent）
```

---

### 7.4 随访任务状态机

```
待生成（pending_create）
  │ 报告复核后自动生成 / 手动创建
  ▼
待执行（pending）
  │ 到达执行时间
  ▼
执行中（in_progress）
  │ AI助手发送消息/问卷
  ▼
已触达（contacted）
  │ 患者回复/完成问卷
  ├──→ 已完成（completed）
  │ 患者未回复，超过截止时间
  ├──→ 逾期（overdue）
  │ 出现异常情况
  └──→ 转人工（transferred_to_human）
```

---

## 八、数据模型草案

### 8.1 现有表（旧项目已有）

**users（B端用户表）**
- 作用：健康管理师、医生、药师等B端用户账号
- 关键字段：id, username, password_hash, real_name, role, wechat_id
- 需扩展：`org_type`（机构类型）、`org_id`（所属机构）、`scene_permissions`（场景权限）

**b_patients（B端患者表）**
- 作用：B端管理的患者档案
- 关键字段：id, patient_code, name, age, gender, phone, wechat_id, nodule_type, manager_id, source_channel, status
- 需扩展：`wechat_status`（企微状态）、`risk_level`（风险等级缓存）、`last_report_id`（最新报告）、`org_id`（所属机构）、`patient_viewed_at`（患者查看报告时间）

**b_health_records（健康档案表）**
- 作用：患者多结节健康档案，100+字段
- 关键字段：patient_id, birads_level, lung_rads_level, tirads_level, 各器官症状/病史/影像字段
- 现状：字段已非常完整，基本不需要改动

**b_reports（报告表）**
- 作用：AI生成的健康管理报告
- 关键字段：patient_id, record_id, status, risk_score, risk_level, report_html, reviewed_by, reviewed_at
- 需扩展：`patient_viewed_at`（患者查看时间）、`sent_to_patient_at`（发送时间）、`miniprogram_url`（小程序查看链接）

**b_follow_up_records（随访记录表）**
- 作用：随访执行记录
- 关键字段：patient_id, manager_id, follow_up_type, follow_up_date, content, next_follow_up_date
- 现状：基础字段已有，需与新的随访任务表区分（记录 vs 计划）

**c_patients（C端患者表）**
- 作用：小程序/H5端患者账号，线索管理
- 关键字段：phone, wechat_openid, lead_status, source_channel, assigned_manager_id
- 需扩展：`b_patient_id`（关联B端患者，实现C端B端打通）

**c_conversations / c_messages（AI对话表）**
- 作用：C端AI健康咨询对话记录
- 现状：已有，用于小程序AI咨询

---

### 8.2 需新增的表

**organizations（机构表）**
- 作用：多机构管理，每个机构对应一个版本配置
- 关键字段：id, name, org_type（hospital/physical_exam/community/pharmacy/health_center）, solution_config_id, is_active, created_at
- 关系：users.org_id → organizations.id；b_patients.org_id → organizations.id

**solution_configs（版本配置表）**
- 作用：每个版本的功能配置，控制工作台显示哪些模块、AI助手组合、转人工规则
- 关键字段：id, org_type, scene_name, ai_staff_config（JSON）, transfer_rules（JSON）, quick_actions（JSON）, metrics_config（JSON）, enabled_modules（JSON）
- 关系：organizations.solution_config_id → solution_configs.id

**b_todos（待办任务表）**
- 作用：B端工作台待办任务，来源于AI生成或手动创建
- 关键字段：id, patient_id, manager_id, priority（high/mid/low）, title, description, status（pending/in_progress/completed/overdue）, source（ai/manual）, due_date, created_at
- 关系：patient_id → b_patients.id；manager_id → users.id

**follow_up_tasks（随访任务计划表）**
- 作用：随访任务计划（区别于 b_follow_up_records 的执行记录）
- 关键字段：id, patient_id, manager_id, task_type（phone/wechat/miniprogram/enterprise_wechat）, scheduled_at, status（pending/in_progress/contacted/completed/overdue/transferred）, content_template_id, actual_executed_at, result_summary
- 关系：patient_id → b_patients.id

**enterprise_wechat_sessions（企微会话表）**
- 作用：B端视角的企微会话管理，记录每个患者的企微服务状态
- 关键字段：id, patient_id, manager_id, enterprise_wechat_user_id, status（active/silent/human_required/closed）, last_message_at, ai_staff_active（JSON，当前激活的AI助手列表）, created_at
- 关系：patient_id → b_patients.id

**enterprise_wechat_messages（企微消息表）**
- 作用：企微会话消息记录（B端视角）
- 关键字段：id, session_id, sender_type（patient/ai/human_manager）, sender_id, content, message_type（text/image/link/template）, sent_at, is_read
- 关系：session_id → enterprise_wechat_sessions.id

**ai_staff_configs（AI助手配置表）**
- 作用：各版本AI助手的配置，包括激活条件、话术模板、转人工规则
- 关键字段：id, org_type, staff_name, staff_role, activation_conditions（JSON）, prompt_template, is_active, priority
- 关系：org_type 对应 organizations.org_type

**patient_tags（患者标签表）**
- 作用：患者标签管理，支持系统自动打标和手动打标
- 关键字段：id, patient_id, tag_name, tag_type（system/manual）, tag_value, created_by, created_at
- 关系：patient_id → b_patients.id

**rws_projects（真实世界研究项目表）**
- 作用：研究项目管理
- 关键字段：id, name, research_type（prospective/cohort/retrospective）, period_start, period_end, inclusion_criteria（JSON）, exclusion_criteria（JSON）, primary_endpoints（JSON）, secondary_endpoints（JSON）, target_enrollment, status
- 关系：独立表，通过 rws_enrollments 关联患者

**rws_enrollments（研究入组表）**
- 作用：患者入组记录
- 关键字段：id, project_id, patient_id, enrolled_at, enrollment_stage, followup_status, qc_issues_count, notes
- 关系：project_id → rws_projects.id；patient_id → b_patients.id

---

### 8.3 数据模型关系图（文字版）

```
organizations (1) ──→ (N) users
organizations (1) ──→ (1) solution_configs
organizations (1) ──→ (N) b_patients

users (1) ──→ (N) b_patients [manager_id]
b_patients (1) ──→ (1) b_health_records
b_patients (1) ──→ (N) b_reports
b_patients (1) ──→ (N) b_follow_up_records
b_patients (1) ──→ (N) b_todos
b_patients (1) ──→ (N) follow_up_tasks
b_patients (1) ──→ (1) enterprise_wechat_sessions
b_patients (1) ──→ (N) patient_tags
b_patients (N) ──→ (N) rws_projects [通过 rws_enrollments]

enterprise_wechat_sessions (1) ──→ (N) enterprise_wechat_messages

c_patients (1) ──→ (1) b_patients [b_patient_id，C端B端打通]
c_patients (1) ──→ (N) c_conversations
c_conversations (1) ──→ (N) c_messages
```

---

## 九、旧项目合并方案

### 9.1 已有功能清单

| 功能 | 位置 | 完成度 |
|---|---|---|
| B端登录/注册 | auth_routes.py | ✅ 完整 |
| 患者CRUD | b_patient_management.py | ✅ 完整 |
| 健康档案（多结节6种组合） | b_record_management.py | ✅ 完整 |
| 报告生成（LLM驱动） | b_report_management.py | ✅ 完整 |
| 报告复核 | b_report_update.py | ✅ 完整 |
| PDF导出 | pdf_service.py | ✅ 完整 |
| 影像报告PDF解析 | imaging_report_service.py | ✅ 完整 |
| 风险评估决策树 | decision_tree.py | ✅ 完整 |
| 知识库管理 | knowledge_routes.py | ✅ 完整 |
| C端AI对话 | c_patient_service.py | ✅ 完整 |
| C端登录/注册 | c_auth_routes.py | ✅ 完整 |
| 小程序问卷 | miniprogram_routes.py | ✅ 完整 |
| 舌象采集 | ai_tongue_platform_routes.py | ✅ 完整 |
| B端患者列表页 | PatientsView.vue | ✅ 完整 |
| B端患者详情页 | PatientDetailView.vue | ✅ 完整 |
| B端多结节表单（6种） | *FormView.vue | ✅ 完整 |
| B端报告查看页 | ReportViewView.vue | ✅ 完整 |
| B端知识库页 | KnowledgeView.vue | ✅ 完整 |
| B端Dashboard | DashboardView.vue | ⚠️ 基础版，需重组 |
| B端企微管理页 | WeChatView.vue | ⚠️ 基础版，需扩展 |
| C端小程序AI咨询 | ChatPage.vue | ✅ 完整 |
| C端报告查看 | ReportDetailPage.vue | ✅ 完整 |

---

### 9.2 可复用接口（直接对接新工作台）

| 旧接口 | 新工作台模块 | 复用方式 |
|---|---|---|
| `GET /api/b/patients` | 患者队列左栏 | 直接调用，加风险等级筛选参数 |
| `POST /api/b/patients` | 新建档案 | 直接调用 |
| `GET /api/b/patients/<id>` | 患者详情卡片 | 直接调用 |
| `PUT /api/b/patients/<id>` | 患者信息更新 | 直接调用 |
| `GET /api/b/records/<id>` | 患者档案详情 | 直接调用 |
| `POST /api/b/reports` | 快捷操作"生成健康报告" | 直接调用 |
| `GET /api/b/reports/<id>` | 快捷操作"查看报告" | 直接调用 |
| `PUT /api/b/reports/<id>` | 报告复核 | 直接调用 |
| `POST /api/b/reports/<id>/export` | PDF导出 | 直接调用 |
| `GET /api/b/follow_up_records` | 随访记录底部面板 | 直接调用 |
| `POST /api/auth/login` | 登录页 | 直接调用 |
| `GET /api/knowledge` | 知识库 | 直接调用 |

---

### 9.3 可复用页面/组件

| 旧组件 | 复用方式 |
|---|---|
| `BreastFormSection.vue` | 嵌入新工作台的档案填写弹窗 |
| `LungFormSection.vue` | 同上 |
| `ThyroidFormSection.vue` | 同上 |
| `ImagingReportUpload.vue` | 嵌入档案填写流程 |
| `RecommendationCard.vue` | 报告详情弹窗中复用 |
| `RiskScorePanel.vue` | 患者详情卡片中复用 |
| `FormBuilder.vue` | 随访问卷表单复用 |
| `DynamicFormField.vue` | 同上 |
| `BaseInput/BaseCard/BaseButton/BaseBadge` | 全局复用 |

---

### 9.4 需要改造的地方

| 位置 | 改造内容 | 原因 |
|---|---|---|
| `AppLayout.vue` | 重写为新三栏工作台布局 | 旧布局是简单侧边栏+内容区，新原型是复杂三栏+底部面板 |
| `router/index.js` | 新增工作台路由，保留旧路由 | 新增 WorkbenchView、RwsView 等路由 |
| `DashboardView.vue` | 改造为运行指标面板组件 | 旧Dashboard是独立页面，新原型是工作台底部的指标区 |
| `WeChatView.vue` | 扩展为企微会话区组件 | 旧页面只有基础企微管理，新原型需要完整会话流 |
| `b_patients` 表 | 新增字段（不删除旧字段） | 需要 wechat_status、risk_level、org_id 等字段 |
| `users` 表 | 新增字段 | 需要 org_type、org_id 字段 |
| `b_reports` 表 | 新增字段 | 需要 patient_viewed_at、sent_to_patient_at 字段 |
| `GET /api/b/patients` | 新增筛选参数 | 支持按风险等级、企微状态、场景筛选 |

---

### 9.5 需要新增的地方

| 类型 | 内容 |
|---|---|
| 新前端页面 | `WorkbenchView.vue`（主工作台）、`RwsView.vue`（真实世界研究） |
| 新前端组件 | `PatientQueue.vue`、`ChatWorkspace.vue`、`AiStaffPanel.vue`、`BottomPanel.vue`、`SceneSwitcher.vue` |
| 新Pinia Store | `scene.js`（场景状态）、`workbench.js`（工作台状态） |
| 新后端接口 | 统计接口、待办任务CRUD、企微会话管理、随访任务管理 |
| 新数据库表 | organizations、solution_configs、b_todos、follow_up_tasks、enterprise_wechat_sessions、enterprise_wechat_messages、ai_staff_configs、patient_tags、rws_projects、rws_enrollments |

---

### 9.6 不建议动的地方

| 位置 | 原因 |
|---|---|
| `b_health_records` 表结构 | 字段已非常完整，100+字段，改动风险高 |
| `decision_tree.py` | 风险评估逻辑稳定，不要轻易改动 |
| `llm_helpers.py` | LLM调用逻辑复杂，改动影响报告生成质量 |
| `imaging_report_service.py` | 影像报告解析逻辑稳定 |
| `pdf_service.py` | PDF生成逻辑稳定 |
| C端小程序代码 | 独立运行，不受B端改动影响 |
| 旧的 `*FormView.vue` | 保留作为备用，新工作台通过弹窗/抽屉复用其中的Section组件 |

---

### 9.7 新原型拆分为Vue组件方案

```
新原型 HTML 结构 → Vue 组件拆分

#loginPage          → views/LoginView.vue（改造现有登录页，加机构类型/角色选择）
#topnav             → components/layout/TopNav.vue
#sidebar + navList  → components/layout/Sidebar.vue（含场景切换逻辑）
#sceneView          → views/WorkbenchView.vue（主工作台容器）
  #statusbar        → components/workbench/StatusBar.vue
  #col-left         → components/workbench/PatientQueue.vue
  #col-mid          → components/workbench/ChatWorkspace.vue
  #col-right        → components/workbench/AiStaffPanel.vue
  #bottom           → components/workbench/BottomPanel.vue
    #todoCol        → components/workbench/TodoList.vue
    #followupCol    → components/workbench/FollowupList.vue
    #metricsCol     → components/workbench/MetricsPanel.vue
#rwsView            → views/RwsView.vue（真实世界研究）
  #rwsLeft          → components/rws/RwsProjectList.vue
  #rwsMain          → components/rws/RwsDetail.vue
  #rwsRight         → components/rws/RwsSupport.vue
#modal              → components/common/Modal.vue（全局弹窗）
#toast              → components/common/Toast.vue（全局提示）
```

---

### 9.8 旧接口与新模块映射表

| 新工作台模块 | 旧接口 | 状态 | 备注 |
|---|---|---|---|
| 患者队列列表 | `GET /api/b/patients` | 直接复用 | 需加 risk_level、wechat_status 筛选参数 |
| 患者详情卡片 | `GET /api/b/patients/<id>` | 直接复用 | — |
| 档案完整度 | `GET /api/b/records/<id>` | 直接复用 | 前端计算完整度百分比 |
| 生成报告（快捷操作） | `POST /api/b/reports` | 直接复用 | — |
| 查看报告（快捷操作） | `GET /api/b/reports/<id>` | 直接复用 | — |
| 报告复核 | `PUT /api/b/reports/<id>` | 直接复用 | — |
| 随访记录面板 | `GET /api/b/follow_up_records` | 直接复用 | 加 patient_id 筛选 |
| 企微会话区 | 无对应旧接口 | 新增 | 新建 enterprise_wechat_sessions 接口 |
| 待办任务面板 | 无对应旧接口 | 新增 | 新建 b_todos 接口 |
| 运行指标面板 | 无对应旧接口 | 新增 | 新建统计聚合接口 |
| 场景切换 | 无对应旧接口 | 新增（前端） | 前端 Pinia store 管理，后端通过 org_type 过滤 |
| 真实世界研究 | 无对应旧接口 | 新增 | 第四阶段实现 |

---

## 十、接口需求

### 10.1 登录/权限

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| POST | `/api/auth/login` | 登录，返回JWT + 用户信息 + 机构信息 | P0 | 复用，需扩展返回 org_type |
| POST | `/api/auth/register` | 注册 | P1 | 复用 |
| GET | `/api/auth/me` | 获取当前用户信息 | P0 | 复用 |
| PUT | `/api/auth/profile` | 更新用户信息（含 org_type） | P1 | 新增 |
| GET | `/api/auth/permissions` | 获取当前用户的功能权限列表 | P1 | 新增 |

**登录接口扩展返回字段**：
```json
{
  "user": { "id", "username", "real_name", "role", "org_type", "org_id" },
  "solution_config": { "scene_name", "ai_staff_config", "quick_actions", "metrics_config", "enabled_modules" },
  "token": "..."
}
```

---

### 10.2 患者档案

| 方法 | 路径 | 用途 | 入参 | 优先级 | 状态 |
|---|---|---|---|---|---|
| GET | `/api/b/patients` | 患者列表 | page, per_page, search, risk_level, nodule_type, wechat_status, status, org_id | P0 | 复用，需加筛选参数 |
| POST | `/api/b/patients` | 新建患者 | name, age, gender, phone, nodule_type, source_channel | P0 | 复用 |
| GET | `/api/b/patients/<id>` | 患者详情 | — | P0 | 复用 |
| PUT | `/api/b/patients/<id>` | 更新患者信息 | 任意字段 | P0 | 复用 |
| DELETE | `/api/b/patients/<id>` | 删除患者 | — | P2 | 复用 |
| PUT | `/api/b/patients/<id>/wechat-status` | 更新企微状态 | wechat_status, enterprise_wechat_user_id | P1 | 新增 |
| GET | `/api/b/patients/<id>/timeline` | 患者完整时间线 | — | P1 | 新增 |

---

### 10.3 问卷/健康档案

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| GET | `/api/b/records` | 档案列表 | P1 | 复用 |
| POST | `/api/b/records` | 新建档案 | P0 | 复用 |
| GET | `/api/b/records/<id>` | 档案详情 | P0 | 复用 |
| PUT | `/api/b/records/<id>` | 更新档案 | P0 | 复用 |
| POST | `/api/b/records/<id>/upload-imaging` | 上传影像报告PDF | P1 | 复用 |
| GET | `/api/b/records/<id>/completeness` | 获取档案完整度 | P1 | 新增（前端可计算，后端可选） |

---

### 10.4 报告生成

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| POST | `/api/b/reports` | 生成报告 | P0 | 复用 |
| GET | `/api/b/reports` | 报告列表 | P0 | 复用 |
| GET | `/api/b/reports/<id>` | 报告详情 | P0 | 复用 |
| PUT | `/api/b/reports/<id>` | 更新报告内容 | P0 | 复用 |
| POST | `/api/b/reports/<id>/export` | 导出PDF | P1 | 复用 |
| POST | `/api/b/reports/<id>/send-to-patient` | 发送报告给患者 | P1 | 新增 |
| PUT | `/api/b/reports/<id>/patient-viewed` | 标记患者已查看 | P1 | 新增 |

---

### 10.5 报告复核

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| POST | `/api/b/reports/<id>/submit-review` | 提交复核 | P0 | 复用 |
| PUT | `/api/b/reports/<id>/review` | 复核通过/拒绝 | P0 | 复用 |
| GET | `/api/b/reports/pending-review` | 待复核报告列表 | P1 | 新增 |

---

### 10.6 小程序

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| POST | `/api/miniprogram/questionnaire` | 提交问卷 | P0 | 复用 |
| GET | `/api/miniprogram/report/<code>` | 获取报告（小程序端） | P0 | 复用 |
| POST | `/api/miniprogram/report/<code>/viewed` | 标记已查看 | P1 | 新增 |
| POST | `/api/miniprogram/tongue-check` | 舌象采集 | P2 | 复用 |
| GET | `/api/miniprogram/follow-up-questionnaire/<task_id>` | 获取随访问卷 | P1 | 新增 |
| POST | `/api/miniprogram/follow-up-questionnaire/<task_id>/submit` | 提交随访问卷 | P1 | 新增 |

---

### 10.7 微信绑定

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| PUT | `/api/b/patients/<id>/wechat` | 更新患者微信号 | P1 | 复用（字段已有） |
| POST | `/api/b/patients/<id>/wechat-add-record` | 记录添加微信操作 | P1 | 新增 |
| GET | `/api/b/patients/<id>/wechat-qrcode` | 获取管理师企微二维码 | P1 | 新增 |

---

### 10.8 企业微信服务池

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| GET | `/api/b/enterprise-wechat/sessions` | 企微会话列表 | P1 | 新增 |
| GET | `/api/b/enterprise-wechat/sessions/<id>` | 会话详情 + 消息记录 | P1 | 新增 |
| POST | `/api/b/enterprise-wechat/sessions/<id>/messages` | 管理师发送消息 | P1 | 新增 |
| PUT | `/api/b/enterprise-wechat/sessions/<id>/transfer` | 转人工/转回AI | P1 | 新增 |
| GET | `/api/b/enterprise-wechat/pool` | 服务池概览（按状态分组） | P1 | 新增 |

---

### 10.9 AI助手会话

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| POST | `/api/c/chat/start` | 开始AI对话（C端） | P0 | 复用 |
| POST | `/api/c/chat/message` | 发送消息（C端） | P0 | 复用 |
| GET | `/api/c/chat/<conversation_id>` | 获取对话历史（C端） | P0 | 复用 |
| GET | `/api/b/ai-staff/configs` | 获取当前版本AI助手配置 | P1 | 新增 |
| PUT | `/api/b/ai-staff/configs` | 更新AI助手配置（管理员） | P2 | 新增 |

---

### 10.10 随访任务

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| GET | `/api/b/follow-up-tasks` | 随访任务列表 | P1 | 新增 |
| POST | `/api/b/follow-up-tasks` | 创建随访任务 | P1 | 新增 |
| PUT | `/api/b/follow-up-tasks/<id>` | 更新任务状态 | P1 | 新增 |
| POST | `/api/b/follow-up-tasks/<id>/execute` | 执行随访（发送消息/问卷） | P1 | 新增 |
| GET | `/api/b/follow-up-records` | 随访执行记录 | P0 | 复用 |
| POST | `/api/b/follow-up-records` | 新建随访记录 | P0 | 复用 |

---

### 10.11 待办任务

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| GET | `/api/b/todos` | 待办列表 | P1 | 新增 |
| POST | `/api/b/todos` | 创建待办 | P1 | 新增 |
| PUT | `/api/b/todos/<id>` | 更新待办状态 | P1 | 新增 |
| DELETE | `/api/b/todos/<id>` | 删除待办 | P2 | 新增 |

---

### 10.12 统计指标

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| GET | `/api/b/stats/overview` | 工作台状态栏统计（待办数/待确认/转人工/逾期） | P1 | 新增 |
| GET | `/api/b/stats/metrics` | 运行指标面板数据（按版本返回不同指标） | P1 | 新增 |
| GET | `/api/b/stats/patients` | 患者统计（总数/新增/风险分布） | P2 | 新增 |
| GET | `/api/b/stats/reports` | 报告统计（生成数/复核率/发送率） | P2 | 新增 |
| GET | `/api/b/stats/followup` | 随访统计（完成率/逾期率） | P2 | 新增 |

---

### 10.13 版本配置

| 方法 | 路径 | 用途 | 优先级 | 状态 |
|---|---|---|---|---|
| GET | `/api/b/solution-config` | 获取当前用户的版本配置 | P0 | 新增 |
| GET | `/api/admin/organizations` | 机构列表（管理员） | P2 | 新增 |
| POST | `/api/admin/organizations` | 创建机构 | P2 | 新增 |
| PUT | `/api/admin/organizations/<id>/config` | 更新机构版本配置 | P2 | 新增 |



---

## 十一、开发阶段计划

### 阶段0：项目梳理与PRD确认（当前阶段）

**目标**：确认需求、对齐技术方案、确定第一版MVP范围

**开发内容**：
- 完成本PRD文档
- 确认四个版本的优先级（建议先做医院版或健康管理中心版）
- 确认企微是真实接入还是先模拟
- 确认旧项目接口稳定性
- 确认数据库扩展字段清单

**验收标准**：PRD确认完毕，开发优先级明确，无重大歧义

**风险点**：业务需求不清晰会导致后续返工

---

### 阶段1：新B端工作台壳子迁移（约1-2周）

**目标**：把新原型的视觉结构和导航框架移植到Vue项目，旧接口不动，数据全部mock

**开发内容**：

前端：
- 重写 `AppLayout.vue`：顶部导航 + 侧边栏 + 场景切换
- 新建 `WorkbenchView.vue`：三栏主工作台容器
- 新建 `PatientQueue.vue`：患者队列左栏（mock数据）
- 新建 `ChatWorkspace.vue`：企微会话中栏（mock数据）
- 新建 `AiStaffPanel.vue`：AI助手右栏（mock数据）
- 新建 `BottomPanel.vue`：底部三列面板（mock数据）
- 新建 `StatusBar.vue`：状态栏统计
- 新建 `RwsView.vue`：真实世界研究视图（全mock）
- 改造 `LoginView.vue`：加机构类型/角色选择
- 新建 `stores/scene.js`：场景状态管理
- 更新 `router/index.js`：新增工作台路由

后端：无改动

数据库：无改动

**涉及前端文件**：
```
frontend/vue-app/src/
  components/layout/TopNav.vue          [新建]
  components/layout/Sidebar.vue         [新建]
  components/workbench/StatusBar.vue    [新建]
  components/workbench/PatientQueue.vue [新建]
  components/workbench/ChatWorkspace.vue [新建]
  components/workbench/AiStaffPanel.vue [新建]
  components/workbench/BottomPanel.vue  [新建]
  components/workbench/TodoList.vue     [新建]
  components/workbench/FollowupList.vue [新建]
  components/workbench/MetricsPanel.vue [新建]
  views/WorkbenchView.vue               [新建]
  views/RwsView.vue                     [新建]
  views/LoginView.vue                   [改造]
  stores/scene.js                       [新建]
  router/index.js                       [更新]
  App.vue                               [更新]
```

**验收标准**：
- 新工作台页面可正常访问
- 场景切换（医院/体检/社区/药店）可切换，颜色主题随之变化
- 三栏布局、底部面板、侧边栏正常显示
- 旧的患者列表、表单、报告页面仍可通过旧路由访问
- 登录页可选择机构类型和角色

**风险点**：
- Element Plus 组件与原型自定义CSS样式冲突，需要决定样式方案
- 旧路由与新路由共存，需要避免路由冲突

---

### 阶段2：接入患者建档、问卷、报告生成、小程序状态（约2-3周）

**目标**：患者队列、档案、报告接入真实接口；小程序查看报告状态回写B端

**开发内容**：

前端：
- `PatientQueue.vue` 接入 `GET /api/b/patients`（加风险等级筛选）
- 患者详情卡片接入 `GET /api/b/patients/<id>` + `GET /api/b/records/<id>`
- 快捷操作"生成健康报告"接入 `POST /api/b/reports`
- 快捷操作"查看报告"接入 `GET /api/b/reports/<id>`
- 随访记录面板接入 `GET /api/b/follow_up_records`
- 新建档案弹窗（复用旧表单组件）

后端：
- `GET /api/b/patients` 新增筛选参数：risk_level、wechat_status、org_id
- 新增 `GET /api/b/stats/overview`（状态栏统计数据）
- `b_patients` 表新增字段：risk_level、wechat_status、org_id
- `b_reports` 表新增字段：patient_viewed_at、sent_to_patient_at

数据库：
```sql
ALTER TABLE b_patients ADD COLUMN risk_level VARCHAR(20);
ALTER TABLE b_patients ADD COLUMN wechat_status VARCHAR(30) DEFAULT 'none';
ALTER TABLE b_patients ADD COLUMN org_id INTEGER;
ALTER TABLE b_reports ADD COLUMN patient_viewed_at TIMESTAMP;
ALTER TABLE b_reports ADD COLUMN sent_to_patient_at TIMESTAMP;
```

**验收标准**：
- 患者队列显示真实患者数据
- 风险等级筛选正常工作
- 点击患者可查看真实档案信息
- 生成报告功能正常
- 状态栏显示真实统计数字
- 旧的患者列表页、表单页仍正常工作

**风险点**：
- `nodule_type` 枚举值需要与新原型的结节分类标签对齐
- 患者状态字段值需要映射到新原型的状态标签

---

### 阶段3：接入添加微信和企业微信AI助手服务池（约3-4周）

**目标**：企微会话区接入真实数据；添加微信状态完整闭环；AI助手会话可用

**开发内容**：

前端：
- `ChatWorkspace.vue` 接入企微会话接口
- 患者详情卡片显示企微状态
- 添加企微引导流程（报告页展示二维码 + 状态回写）
- AI助手工作区接入配置接口

后端：
- 新建 `enterprise_wechat_sessions` 表和接口
- 新建 `enterprise_wechat_messages` 表和接口
- 新建 `ai_staff_configs` 表和接口
- 新建 `GET /api/b/solution-config`（版本配置接口）
- 新建 `organizations` 表（基础版）
- `users` 表新增 org_type、org_id 字段

数据库：
```sql
CREATE TABLE organizations (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  org_type VARCHAR(30) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE enterprise_wechat_sessions (...);
CREATE TABLE enterprise_wechat_messages (...);
CREATE TABLE ai_staff_configs (...);
ALTER TABLE users ADD COLUMN org_type VARCHAR(30);
ALTER TABLE users ADD COLUMN org_id INTEGER;
```

**注意**：企微是否真实接入需要在阶段0确认。若先模拟，则企微会话区使用mock数据，但接口结构按真实设计，方便后续替换。

**验收标准**：
- 企微会话区可显示会话列表和消息记录（真实或mock）
- 患者的企微状态可在B端更新
- 不同版本登录后工作台显示对应的AI助手配置和快捷操作
- 添加企微的状态变更可回写到患者档案

**风险点**：
- 企微真实接入需要企业微信开发者账号和API权限
- 多AI协同的会话上下文管理复杂度较高

---

### 阶段4：完善随访任务、转人工、AI助手配置（约2-3周）

**目标**：随访任务完整闭环；转人工规则可配置；待办任务接真实接口

**开发内容**：

前端：
- 待办任务面板接入 `GET /api/b/todos`
- 随访任务管理界面
- 转人工操作按钮和流程
- AI助手配置管理界面（管理员）

后端：
- 新建 `b_todos` 表和 CRUD 接口
- 新建 `follow_up_tasks` 表和接口
- 实现随访任务自动生成逻辑（报告复核后触发）
- 实现转人工规则引擎（基于关键词/风险等级触发）
- 新建 `patient_tags` 表和接口

数据库：
```sql
CREATE TABLE b_todos (
  id SERIAL PRIMARY KEY,
  patient_id INTEGER REFERENCES b_patients(id),
  manager_id INTEGER REFERENCES users(id),
  priority VARCHAR(10) DEFAULT 'mid',
  title VARCHAR(200) NOT NULL,
  description TEXT,
  status VARCHAR(20) DEFAULT 'pending',
  source VARCHAR(20) DEFAULT 'manual',
  due_date DATE,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE follow_up_tasks (...);
CREATE TABLE patient_tags (...);
```

**验收标准**：
- 待办任务面板显示真实数据，可标记完成
- 随访任务可自动生成和手动创建
- 转人工规则触发后，B端工作台收到通知
- 患者标签可自动打标和手动管理

**风险点**：
- 随访任务自动生成逻辑需要与报告生成流程紧密配合
- 转人工规则引擎的准确性需要业务验证

---

### 阶段5：医院/体检/社区/药店版本化配置（约3-4周）

**目标**：四个版本的差异化功能完整实现；版本配置可在管理后台调整

**开发内容**：

前端：
- 社区版专项模块：家庭医生任务、双向转诊
- 药店版专项模块：药师审核工作区、舌象管理
- 体检版专项模块：体检批次管理
- 版本配置管理界面（管理员）

后端：
- 完善 `solution_configs` 表和配置逻辑
- 社区版：双向转诊接口
- 药店版：药师审核接口
- 体检版：体检批次导入接口
- 完善权限中间件（按 org_type 和 role 控制接口访问）

**验收标准**：
- 四个版本登录后工作台显示对应的模块和配置
- 社区版家庭医生任务正常工作
- 药店版药师审核流程完整
- 体检版可批量导入体检数据
- 管理员可在后台调整版本配置

**风险点**：
- 四个版本的业务差异需要充分的产品确认
- 权限体系复杂度较高，需要仔细设计

---

### 阶段6：统计分析、RWS、多机构权限（持续迭代）

**目标**：完善数据统计、真实世界研究模块、多机构隔离

**开发内容**：

前端：
- 完善统计分析页面
- 真实世界研究模块接入真实接口
- 多机构管理界面

后端：
- 完善统计聚合接口
- 新建 `rws_projects`、`rws_enrollments` 表和接口
- 多机构数据隔离（所有查询加 org_id 过滤）
- 数据导出功能

**验收标准**：
- 统计数据准确，与实际数据一致
- RWS模块可管理研究项目和入组患者
- 不同机构的数据完全隔离
- 数据可导出为CSV/Excel

---

## 十二、MVP 范围

### MVP 必须包含（第一版上线标准）

| 模块 | 具体内容 |
|---|---|
| 患者建档 | B端手动录入 + 小程序自助建档 |
| 问卷/健康档案 | 多结节档案填写（B端代填 + 小程序自填） |
| 报告生成 | AI生成 + 专业人员复核 + PDF导出 |
| 小程序查看报告 | 患者在小程序查看已复核报告 |
| 添加微信状态 | 记录患者是否已添加企微（状态字段） |
| B端患者队列 | 患者列表 + 风险筛选 + 基本信息卡片 |
| 报告复核/查看 | B端工作台报告复核流程 |
| 企微服务池基础列表 | 显示企微服务状态（可先mock会话内容） |
| AI助手模拟会话 | 企微会话区显示AI对话（可先mock，接口结构按真实设计） |
| 随访任务基础版 | 随访记录查看 + 手动创建随访任务 |
| 新工作台布局 | 三栏布局 + 场景切换 + 底部面板 |

### MVP 可以暂缓

| 模块 | 暂缓原因 |
|---|---|
| 真实世界研究（RWS） | 业务复杂，优先级低 |
| 多AI复杂协同 | 技术复杂，先用单AI助手 |
| 完整药店/社区专项运营 | 先做医院版或健康管理中心版 |
| 高级统计分析 | 先做基础指标 |
| 复杂多机构权限 | 先做单机构，后扩展 |
| 体检批次导入 | 先做手动建档 |
| 双向转诊完整流程 | 先做基础转诊记录 |
| 药师审核完整流程 | 先做基础审核标记 |

### MVP 建议版本

**建议先做"健康管理中心版"MVP**，原因：
1. 业务流程最完整（建档→问卷→报告→企微→随访）
2. 没有医院版的复杂多角色协同
3. 没有社区版的双向转诊复杂性
4. 没有药店版的药师审核合规要求
5. 可以快速验证核心业务闭环

---

## 十三、验收标准

### 13.1 功能验收

| 模块 | 验收项 |
|---|---|
| 患者建档 | 可通过B端录入患者；可通过小程序建档；建档后患者出现在队列中 |
| 健康档案 | 可填写多结节档案；影像报告可上传并自动解析；档案完整度正确计算 |
| 报告生成 | 档案完整后可触发报告生成；报告内容包含风险评分和建议；可导出PDF |
| 报告复核 | 复核人可查看待复核报告；可修改内容；复核通过后状态变更 |
| 小程序 | 患者可在小程序查看已复核报告；查看后状态回写B端 |
| 企微状态 | 患者企微状态可在B端更新；不同状态显示不同标签 |
| 工作台布局 | 三栏布局正常；场景切换正常；底部面板可折叠 |
| 随访记录 | 随访记录可查看；可新建随访记录 |
| 待办任务 | 待办任务可查看；可标记完成 |
| 运行指标 | 指标数字与实际数据一致 |

### 13.2 数据验收

- 患者数据不丢失（旧项目数据迁移后完整）
- 报告数据不丢失
- 随访记录不丢失
- 新增字段有默认值，不影响旧数据查询

### 13.3 流程验收

完整走通以下流程：
1. 管理师登录 → 选择场景 → 进入工作台
2. 新建患者档案 → 填写健康档案 → 上传影像报告
3. 生成报告 → 复核报告 → 发送给患者
4. 患者在小程序查看报告 → B端状态更新
5. 更新患者企微状态 → 企微服务池显示
6. 新建随访任务 → 执行随访 → 记录结果

### 13.4 UI验收

- 新工作台与原型视觉一致度 ≥ 80%
- 场景主题色切换正常
- 响应式布局在1366px宽度下正常显示
- 旧页面样式不受影响

### 13.5 接口验收

- 所有P0接口响应时间 < 2秒
- 报告生成接口响应时间 < 30秒（LLM调用）
- 接口错误有明确的错误码和提示信息
- 旧接口签名不变，返回格式兼容

---

## 十四、待确认问题

以下问题需要在开始开发前确认：

### 优先级类

1. **四个版本的开发优先级是什么？** 建议先做一个版本跑通完整流程，再扩展其他版本。推荐顺序：健康管理中心版 → 医院版 → 体检版 → 社区版 → 药店版。

2. **第一版MVP是否只做一个版本？** 如果是，选哪个版本？

### 企微类

3. **企微是真实接入还是先模拟？** 真实接入需要企业微信开发者账号、API权限申请，周期较长。建议先模拟会话界面，接口结构按真实设计，后续替换数据源。

4. **企微会话的数据来源是什么？** 是通过企微API拉取真实消息记录，还是系统内部记录管理师与患者的沟通？两者数据模型不同。

5. **AI助手是否已经在企微中部署？** 还是需要从零搭建企微AI助手服务？

### 微信/添加微信类

6. **添加微信的流程目前做到哪一步？** 是只记录"已添加"状态，还是需要自动化引导流程（报告页展示二维码 → 患者扫码 → 系统自动检测添加状态）？

7. **是添加个人微信还是企业微信？** 两者的技术实现完全不同。

### 报告复核类

8. **报告复核由谁完成？** 医院版由医生复核，其他版本由健康管理师复核？还是所有版本都由健康管理师复核？

9. **复核是否需要电子签名？** 还是只需要点击"通过"即可？

### 技术类

10. **旧项目接口是否稳定？** 是否有正在进行的改动会影响接口签名？

11. **数据库是否可以直接加字段？** 还是需要走数据库变更审批流程？

12. **前端样式方案如何选择？** 继续用Element Plus组件，还是参考原型的轻量CSS风格？两者混用会有样式冲突风险。

13. **小程序是否需要同步更新？** 新工作台上线后，小程序端是否需要同步更新随访问卷等功能？

### 业务类

14. **四个场景的患者数据是共享还是隔离？** 同一个患者可以在多个场景中出现吗？

15. **"真实世界研究"模块的优先级如何？** 是否在MVP范围内？

16. **舌象采集功能是否继续保留？** 目前已有AI舌象平台对接，是否在新工作台中继续使用？

---

*文档结束 | 下一步：确认待确认问题 → 确定MVP范围 → 开始阶段1开发*
