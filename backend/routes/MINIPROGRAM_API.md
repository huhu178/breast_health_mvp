# 微信小程序接口文档

## 概述

本接口用于微信小程序提交问卷数据，并复用B端系统的报告生成流程（知识库匹配 → 决策树 → LLM生成）。

## 接口列表

### 1. 微信授权登录

**接口地址**: `POST /api/miniprogram/auth/wechat`

**请求参数**:
```json
{
  "code": "微信登录code（通过wx.login获取）"
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 0,
  "message": "授权成功",
  "data": {
    "openid": "OPENID_xxx",
    "token": "TOKEN_xxx"
  }
}
```

**说明**: 
- 当前为临时实现，需要接入微信API（配置 `WECHAT_APPID` 和 `WECHAT_SECRET`）
- 实际使用时需要调用 `https://api.weixin.qq.com/sns/jscode2session` 获取真实 openid

---

### 2. 提交问卷并生成报告

**接口地址**: `POST /api/miniprogram/questionnaire/submit`

**请求参数**:
```json
{
  "openid": "微信OpenID（可选）",
  "phone": "13800138000",
  "name": "张三",
  "questionnaire_data": {
    // 基本信息
    "age": 35,
    "gender": "女",
    "height": 165.0,
    "weight": 60.0,
    
    // 结节类型（必填）
    "nodule_type": "breast",  // breast/lung/thyroid/breast_lung/breast_thyroid/lung_thyroid/triple
    
    // 影像学信息
    "birads_level": "4A",
    "nodule_size": "1.2cm",
    "nodule_location": "左乳外上象限",
    "boundary_features": "边界清晰",
    "internal_echo": "低回声",
    "blood_flow_signal": "有",
    "elasticity_score": "3",
    
    // 症状
    "symptoms": "乳房肿块,疼痛",  // 字符串或数组
    "symptoms_other": "其他症状说明",
    "pain_level": 3,
    "pain_type": "胀痛",
    
    // 家族史
    "family_history": "一级亲属",
    
    // 发现时间
    "breast_discovery_date": "2024-01-15",  // YYYY-MM-DD格式
    
    // 其他字段（参考B端健康档案字段）
    "diabetes_history": "无",
    "gaofang_address": "浙江省杭州市...",
    "course_stage": "早期",
    "rhythm_type": "规律",
    "sleep_quality": "良好",
    "exercise_frequency": "每周3次",
    "lifestyle": "规律"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 0,
  "message": "问卷提交成功，报告已生成",
  "data": {
    "report_id": 123,
    "report_code": "BRPT20240119123456",
    "report_html": "<div>...</div>",
    "risk_level": "中危",
    "risk_score": 45,
    "patient_code": "BP20240119123456",
    "openid": "OPENID_xxx"
  }
}
```

**说明**:
- 会自动创建或更新B端患者（`BPatient`）
- 创建B端健康档案（`BHealthRecord`）
- 复用B端报告生成流程（知识库匹配 → 决策树 → LLM）
- 生成B端报告（`BReport`），状态为 `published`，来源标记为 `miniprogram`
- 返回完整的HTML报告，小程序可以直接展示

---

### 3. 查看报告详情

**接口地址**: `GET /api/miniprogram/reports/<report_id>`

**请求参数**（Query）:
- `openid`: 微信OpenID（可选，用于验证）
- `phone`: 手机号（可选，用于验证）

**响应示例**:
```json
{
  "success": true,
  "code": 0,
  "message": "获取成功",
  "data": {
    "report_id": 123,
    "report_code": "BRPT20240119123456",
    "report_html": "<div>...</div>",
    "risk_level": "中危",
    "risk_score": 45,
    "generated_at": "2024-01-19 12:34:56"
  }
}
```

**说明**:
- 如果提供了 `openid` 或 `phone`，会验证是否匹配报告所属患者
- 只返回来源为 `miniprogram` 的报告

---

### 4. 查询用户报告列表

**接口地址**: `GET /api/miniprogram/reports/list`

**请求参数**（Query）:
- `phone`: 手机号（必填）
- `openid`: 微信OpenID（可选，用于验证）

**响应示例**:
```json
{
  "success": true,
  "code": 0,
  "message": "查询成功，共2份报告",
  "data": {
    "reports": [
      {
        "report_id": 123,
        "report_code": "BRPT20240119123456",
        "risk_level": "中危",
        "risk_score": 45,
        "generated_at": "2024-01-19 12:34:56"
      },
      {
        "report_id": 124,
        "report_code": "BRPT20240120123456",
        "risk_level": "低危",
        "risk_score": 25,
        "generated_at": "2024-01-20 12:34:56"
      }
    ],
    "patient_name": "张三",
    "patient_code": "BP20240119123456"
  }
}
```

**说明**:
- 只返回来源为 `miniprogram` 的报告
- 如果提供了 `openid`，会验证是否匹配患者

---

## 数据字段映射

小程序提交的问卷数据会自动映射到B端健康档案字段：

| 小程序字段 | B端字段 | 说明 |
|----------|--------|------|
| `age` | `age` | 年龄（整数） |
| `gender` | `gender` | 性别 |
| `height` | `height` | 身高（cm，浮点数） |
| `weight` | `weight` | 体重（kg，浮点数） |
| `phone` | `phone` | 手机号 |
| `nodule_type` | `patient.nodule_type` | 结节类型 |
| `birads_level` | `birads_level` | BI-RADS分级 |
| `nodule_size` | `nodule_size` | 结节大小 |
| `symptoms` | `symptoms` | 症状（字符串或数组，自动转换） |
| `family_history` | `family_history` | 家族史 |
| `breast_discovery_date` | `breast_discovery_date` | 乳腺发现时间（日期格式） |
| `lung_discovery_date` | `lung_discovery_date` | 肺发现时间 |
| `thyroid_discovery_date` | `thyroid_discovery_date` | 甲状腺发现时间 |

更多字段请参考 `BHealthRecord` 模型定义。

---

## 小程序调用示例

### 微信小程序代码（JavaScript）

```javascript
// 1. 微信登录获取code
wx.login({
  success: (res) => {
    const code = res.code;
    
    // 2. 调用授权接口（可选）
    wx.request({
      url: 'https://your-domain.com/api/miniprogram/auth/wechat',
      method: 'POST',
      data: { code },
      success: (authRes) => {
        const openid = authRes.data.data.openid;
        
        // 3. 提交问卷
        wx.request({
          url: 'https://your-domain.com/api/miniprogram/questionnaire/submit',
          method: 'POST',
          data: {
            openid: openid,
            phone: '13800138000',
            name: '张三',
            questionnaire_data: {
              age: 35,
              gender: '女',
              nodule_type: 'breast',
              birads_level: '4A',
              nodule_size: '1.2cm',
              symptoms: ['乳房肿块', '疼痛'],
              family_history: '一级亲属',
              breast_discovery_date: '2024-01-15'
            }
          },
          success: (submitRes) => {
            if (submitRes.data.success) {
              const reportId = submitRes.data.data.report_id;
              const reportHtml = submitRes.data.data.report_html;
              
              // 4. 展示报告（使用web-view或rich-text）
              // 方式1: 使用web-view
              wx.navigateTo({
                url: `/pages/report/report?reportId=${reportId}&openid=${openid}`
              });
              
              // 方式2: 使用rich-text（需要处理HTML）
              // this.setData({ reportHtml: reportHtml });
            }
          }
        });
      }
    });
  }
});
```

---

## 注意事项

1. **微信授权**: 当前 `wechat_auth` 接口为临时实现，需要接入真实的微信API
2. **数据格式**: 日期字段必须为 `YYYY-MM-DD` 格式
3. **结节类型**: 必须指定 `nodule_type`，支持的类型见上方
4. **报告来源**: 所有小程序生成的报告都会标记 `source_channel='miniprogram'`
5. **报告状态**: 小程序生成的报告直接为 `published` 状态，无需审核
6. **数据复用**: 小程序数据会创建B端患者和档案，可在B端管理系统中查看和管理

---

## 环境变量配置

如需接入真实微信API，需要在 `.env` 中配置：

```bash
WECHAT_APPID=your_appid
WECHAT_SECRET=your_secret
```

然后在 `miniprogram_routes.py` 的 `wechat_auth` 函数中取消注释相关代码。


