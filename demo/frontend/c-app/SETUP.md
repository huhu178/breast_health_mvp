# C端应用部署和使用指南

## 🚀 快速开始

### 1. 安装依赖

```powershell
cd D:\1work\20251016\breast_health_mvp\frontend\c-app
npm install
```

### 2. 启动开发服务器

```powershell
npm run dev
```

访问：http://localhost:5174

### 3. 构建生产版本

```powershell
npm run build
```

构建文件将生成在 `dist/` 目录

## 📱 功能说明

### 主要流程

1. **用户访问首页** → 选择登录方式
   - 微信登录（扫码或微信内打开）
   - 手机号验证（Web端快速查看）

2. **验证身份** → 输入手机号
   - 系统自动查询该手机号关联的报告

3. **查看报告列表** → 选择要查看的报告

4. **查看报告详情** → 下载PDF

### 页面说明

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | `/` | 落地页，展示服务并引导登录 |
| 验证页 | `/verify` | 手机号验证入口 |
| 报告列表 | `/reports` | 显示用户的所有报告 |
| 报告详情 | `/report/:id` | 查看单个报告详情和下载PDF |

## 🔗 与后端对接

### API端点

所有请求都通过 `/api/c/` 前缀：

```javascript
// 认证
POST /api/c/auth/phone        // 手机号登录
POST /api/c/auth/wechat       // 微信登录

// 报告
POST /api/c/reports/verify    // 验证手机号查看报告
GET  /api/c/reports/:id       // 获取报告详情
GET  /api/c/reports/:id/pdf   // 下载PDF
```

### 数据流转

```
C端用户（微信/Web）
     ↓
   登录认证
     ↓
C端报告查看（API）
     ↓
B端管理员可见（管理后台）
```

## 🔧 与B端对接

### B端可见数据

1. **线索信息**（`c_patients`）
   - 手机号、姓名
   - 来源渠道（微信/Web）
   - 首次访问时间
   - 线索状态

2. **对话记录**（`c_conversations`, `c_messages`）
   - 完整对话历史
   - 收集的健康信息

3. **报告数据**（`c_reports`）
   - 生成的报告
   - 查看次数
   - 下载记录

### B端管理功能

B端管理员通过管理后台（http://localhost:5173）可以：
- 查看所有C端线索
- 查看对话记录
- 管理报告
- 导出数据统计

## 📊 微信集成（TODO）

### 微信公众号/小程序配置

1. 在微信公众平台配置 JS安全域名
2. 配置授权回调域名
3. 获取 AppID 和 AppSecret
4. 在 `.env` 文件中配置：

```env
WECHAT_APPID=your_appid
WECHAT_SECRET=your_secret
```

### 微信登录流程

```javascript
// 前端
1. 用户点击"微信登录"
2. 跳转到微信授权页面
3. 用户同意授权
4. 微信回调返回 code
5. 前端发送 code 到后端

// 后端
6. 使用 code 换取 access_token 和 openid
7. 查询或创建用户
8. 返回 session_token
```

## 🎨 UI定制

### 主题颜色

在 `src/style.css` 中修改：

```css
:root {
  --primary-color: #667eea;     /* 主色 */
  --secondary-color: #764ba2;   /* 辅助色 */
  --success-color: #10b981;     /* 成功色 */
  --warning-color: #f59e0b;     /* 警告色 */
  --danger-color: #ef4444;      /* 危险色 */
}
```

## 🐛 常见问题

### 1. API请求失败（CORS错误）

确保 Flask 后端已配置 CORS：

```python
CORS(app, supports_credentials=True, origins=['http://localhost:5174'])
```

### 2. 页面404

检查 Vite 代理配置（`vite.config.js`）

### 3. 报告不显示

检查：
- 手机号是否正确
- 后端API是否正常
- 是否有生成的报告

## 📦 生产部署

### 构建

```bash
npm run build
```

### 部署到Flask

1. 构建完成后，将 `dist/` 目录复制到 Flask 的 `static/c-app/`
2. Flask 配置静态文件服务
3. 访问：http://yourdomain.com/c-app/

### 独立部署

使用 Nginx 等Web服务器托管 `dist/` 目录

