# 多结节工作台 Vue 原型

这是 B 端多场景工作台原型，当前重点链路是：

```text
健康报告审核 -> 手动创建报告后首次随访 -> 生成公开打卡链接 -> 患者免登录打卡 -> B 端执行跟踪回看
```

完整交付范围、验收命令和演示路径见 [DELIVERY.md](./DELIVERY.md)。

## 启动

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

默认访问：

```text
http://127.0.0.1:5173
```

## 验证

前端构建与静态冒烟：

```bash
cd /root/20260402/breast_health_mvp/demo/vue-prototype
npm run smoke
```

后端端到端冒烟：

```bash
cd /root/20260402/breast_health_mvp
python3 demo/backend/scripts/e2e_smoke.py
```

真实浏览器 UI 冒烟，需要后端和前端开发服务器都已启动：

```bash
cd /root/20260402/breast_health_mvp/demo/vue-prototype
npm run smoke:patient-save-ui
npm run smoke:report-audit-ui
npm run smoke:imaging-upload-ui
npm run smoke:audit-followup-ui
npm run smoke:multi-nodule-ui
npm run smoke:triple-report-ui
npm run smoke:ui
```

`smoke:patient-save-ui` 会通过浏览器填写患者建档表单，验证患者和档案已真实保存到后端，并在结束时清理测试患者。

`smoke:report-audit-ui` 会自动准备待审核报告，通过浏览器编辑审核建议并审核归档，验证最终报告锁定后不能再次保存草稿。

`smoke:imaging-upload-ui` 会自动准备患者档案，通过浏览器上传并删除影像报告，验证后端影像报告记录同步变化。

`smoke:audit-followup-ui` 会自动准备待审核报告，通过审核弹窗创建首次随访任务，验证重复创建拦截、公开打卡链接和执行跟踪入口。

`smoke:multi-nodule-ui` 会通过浏览器分别保存肺+乳、甲+乳、肺+甲、三合并 4 类多结节档案，验证患者结节类型和各器官档案字段落库。

`smoke:triple-report-ui` 会自动准备三合并结节档案并生成报告，通过浏览器审核归档，验证三类结节内容进入报告 HTML。

`smoke:ui` 会自动创建临时患者和 finalized 报告，用浏览器点击创建首次随访，提交公开打卡，并在结束时清理测试患者。

## 说明

- 企业微信不是当前随访闭环的必需条件；未配置企微时会走公开链接/人工触达模式。
- `manual` 渠道表示生成公开打卡链接并记录消息，不做真实外部发送。
- 如果本地 Python 在沙箱里无法连接 PostgreSQL，需要在非沙箱环境执行后端和 UI 冒烟测试。
