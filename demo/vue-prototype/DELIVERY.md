# 多结节工作台交付说明

## 交付范围

当前交付版本聚焦 B 端多结节健康管理工作台，已覆盖从建档、报告审核到报告后首次随访的核心闭环：

```text
患者建档 -> 影像资料维护 -> 健康报告生成/审核 -> 创建首次随访 -> 公开打卡 -> 执行跟踪
```

已完成能力：

- 患者管理：患者队列、患者详情、单结节和多结节建档保存。
- 多结节建档：肺+乳、甲+乳、肺+甲、三合并 4 类组合保存和字段落库。
- 影像资料：患者详情页上传/删除影像报告，并同步后端影像报告记录。
- 健康报告：报告列表、报告查看、审核建议编辑、审核归档、归档后锁定。
- 三合并报告：三合并结节档案可生成报告并进入审核归档。
- 随访闭环：审核后创建报告后首次随访任务，生成公开打卡链接，患者免登录打卡，B 端执行跟踪回看。
- 随访工作流配置：模板、节点、知识库、AI 规则保存类操作已覆盖。

## 启动方式

后端：

```bash
cd /root/20260402/breast_health_mvp/demo/backend
python3 app.py
```

前端：

```bash
cd /root/20260402/breast_health_mvp/demo/vue-prototype
npm run dev -- --host 0.0.0.0
```

访问入口：

```text
http://127.0.0.1:5173/login
```

测试账号：

```text
smoke_admin / Smoke@123456
```

## 推荐演示路径

1. 登录后进入 `患者管理`。
2. 在 `患者建档` 创建三合并或任一多结节档案。
3. 在 `健康报告` 查看待审核报告，编辑审核建议并审核通过。
4. 在审核弹窗中创建 `报告后首次随访`。
5. 打开公开打卡链接，模拟患者提交打卡。
6. 回到 `执行跟踪` 查看任务执行和患者回复。
7. 进入 `随访知识库与模板` 查看模板、节点、知识和 AI 规则配置。

## 自动验收

静态构建与组合式逻辑 smoke：

```bash
cd /root/20260402/breast_health_mvp/demo/vue-prototype
npm run smoke
```

后端 API 端到端 smoke：

```bash
cd /root/20260402/breast_health_mvp
python3 demo/backend/scripts/e2e_smoke.py
```

真实浏览器 UI 全量 smoke：

```bash
cd /root/20260402/breast_health_mvp/demo/vue-prototype
npm run smoke:all-ui
```

`smoke:all-ui` 会依次执行：

- `smoke:patient-save-ui`：浏览器建档保存，校验患者和档案落库。
- `smoke:report-audit-ui`：准备待审核报告，浏览器编辑建议并审核归档，校验归档锁定。
- `smoke:imaging-upload-ui`：患者详情上传/删除影像报告，校验后端记录同步变化。
- `smoke:audit-followup-ui`：审核弹窗创建首次随访，校验重复创建拦截、公开打卡链接和执行跟踪入口。
- `smoke:multi-nodule-ui`：肺+乳、甲+乳、肺+甲、三合并 4 类多结节建档保存。
- `smoke:triple-report-ui`：三合并档案生成报告，浏览器审核归档，校验报告 HTML 包含三类结节内容。
- `smoke:workflow-ui`：随访工作流配置页基础 UI 可用。
- `smoke:workflow-save-ui`：随访模板、节点、知识、AI 规则保存和清理。
- `smoke:ui`：报告到首次随访、公开打卡、执行跟踪回看完整闭环。

## 运行前提

- Flask 后端运行在 `http://127.0.0.1:5000`。
- Vue dev server 运行在 `http://127.0.0.1:5173`。
- 本地 PostgreSQL 和项目配置可用。
- Playwright Python 包和 Chromium 浏览器可用。
- 浏览器 UI smoke 需要在非沙箱环境运行 Chromium。

## 已知限制

- 企业微信真实发送未接入当前验收环境；未配置企微时走公开链接/人工触达模式。
- `manual` 渠道只生成公开打卡链接和发送记录，不做外部真实消息发送。
- LLM 相关能力依赖本地环境变量和后端配置；smoke 会尽量使用固定链路或后端已有降级逻辑。
- 执行跟踪页目前主要校验页面入口和任务链路，患者行强选择器仍可继续增强。
- 当前 UI smoke 会创建并清理测试患者；失败时可能留下测试数据，需要按患者名或脚本输出 ID 手动清理。

## 建议后续

- 增强执行跟踪页稳定选择器，补“创建任务确实显示在执行跟踪患者列表/任务表”的强断言。
- 统一前端错误提示，抽 `formatApiError` 和 toast helper。
- 补一条快速 API smoke，覆盖多结节建档、三合并报告生成、审核归档、创建首次随访，减少 CI 对浏览器的依赖。
- 视交付需要整理提交，将 UI smoke、报告审核修复、交付文档拆成清晰提交。
