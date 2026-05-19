# 风险分层梳理

## 当前结论

当前系统里的 `risk_level` 是健康管理工作流分层字段，用于患者队列排序、报告审核筛选、随访模板匹配和随访话术，不作为诊断结论或治疗决策。

## B 端报告风险来源

1. 优先使用中医/舌诊/手诊健康指数。
   - 入口：`demo/backend/utils/report_manager.py::derive_tcm_risk_level`
   - 健康指数 `>=80` 映射为低风险，`60-79` 映射为中风险，`<60` 映射为高风险。
   - 返回 `risk_level`、`risk_score`、`risk_basis`。

2. 没有中医健康指数时，使用影像分级兜底。
   - 入口：`demo/backend/routes/b_report_management.py::_derive_report_risk_level`
   - 乳腺：BI-RADS 1/2 为低风险，3 为中风险，4/5/6 为高风险。
   - 肺部：Lung-RADS 1/2 为低风险，3 为中风险，4 为高风险。
   - 甲状腺：TI-RADS 1/2 为低风险，3 为中风险，4/5/6 为高风险。
   - 多器官结节取最高风险等级。
   - 分级缺失时返回中风险，并标记资料缺口。

3. LLM 输出里的 `risk_warning` 是报告文字内容，不是系统主分层来源。

## 接口字段

B 端报告接口会返回：

- `risk_level`：低风险 / 中风险 / 高风险 / 未评估
- `risk_score`：25 / 55 / 85 等工作流分数
- `risk_basis`：分层依据
- `risk_source`：`tcm_health_index` / `imaging_grade` / `data_gap` / `unknown`
- `risk_scope`：固定为 `workflow_triage`
- `risk_disclaimer`：风险分层用途说明

## 下游使用

- 患者队列：用于风险标签和高风险统计。
- 报告审核：用于筛选与审核优先级。
- 随访模板：用 `risk_level` 匹配模板和知识条目。
- 随访任务：高风险任务默认高优先级。
- 随访 AI：根据风险等级生成不同强度的话术提醒。

## 后续建议

短期继续保持三档风险，避免引入过细等级导致模板、队列、随访规则不一致。

中期可以把分层逻辑从 `b_report_management.py` 抽到独立服务，例如 `services/risk_assessment_service.py`，同时保留当前接口字段，减少迁移成本。
