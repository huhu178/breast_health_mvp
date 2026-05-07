# AI 舌诊 H5 接入说明

## 1. 结论

当前这套第三方应用参数应走 `H5 会员单点登录` 接入，**不走 API 直连方案**。

这意味着：

- 不再调用 `/backend/interfacesvc/...` 这类预判、确认提交、问诊 API
- 不再维护本地图片直传到第三方的 API 直连流程
- 不再依赖 `aesKey` 做 `encryptData` 加解密
- 改为：
  1. 后端获取企业应用 `access_token`
  2. 后端生成 H5 单点登录 URL
  3. 前端打开 H5 页面
  4. 用户在 H5 页面内完成检测
  5. 我方通过报告回调或报告检索获取结果
  6. 将需要的结果字段写入现有文档/报告

## 2. 当前应保留的接口

### 2.1 获取企业应用 access_token

- 地址：`POST https://www.ai-tongue.com/backend/auth/invoker/pwd/signin`
- 传参方式：`form-data`

参数：

- `devid`
- `devsecret`

响应中关键字段：

- `data.access_token`
- `data.expires_in`

后续 H5 单点登录和会员创建接口都使用这个 `access_token`。

## 3. 会员单点登录

### 3.1 请求地址

`GET https://www.ai-tongue.com/h5/sso`

### 3.2 必填参数

- `access_token`
- `encryptedThirdId`
- `signEncryptedThirdId`

### 3.3 参数说明

- `access_token`
  - 通过企业应用授权接口获取

- `encryptedThirdId`
  - 使用平台公钥 `rsaPublicKey`
  - 对第三方用户唯一标识 `thirdId` 做 RSA 加密后的字符串

- `signEncryptedThirdId`
  - 使用应用私钥 `devRsaPrivateKey`
  - 对 `encryptedThirdId` 做 RSA 签名后的字符串

### 3.4 常用可选参数

- `userName`
- `sex`
- `birthday`
- `phone`
- `capture`
- `diseaseCode`
- `memberInit`
- `excludePages`
- `includePages`
- `toPage`
- `backToMAPath`
- `payMAPath`
- `maUserOpenId`

### 3.5 推荐参数

如果当前只希望用户在 H5 内完成舌诊，建议优先尝试：

- `capture=all`
- `diseaseCode=C00.D00`
- `excludePages=allFaceImage,sideFaceImage,bottomTab,edition,instruction,share`

如果需要更简洁的页面，还可以追加：

- `excludePages=allFaceImage,sideFaceImage,bottomTab,edition,instruction,share,backBtn`

### 3.6 当前项目实现

后端接口：

- `POST /api/b/tongue-diagnosis/h5-sso`

请求参数：

- `patient_id`
- `record_id`
- `third_id`（可选；不传则后端自动生成）

返回：

- `h5_url`
- `mobile_open_url`
- `third_id`
- `third_user_init_response`
- `task`

当前前端入口已经改为生成 H5 地址，并提供复制链接、二维码和手机打开提示；二维码优先使用本系统 `mobile_open_url` 跳转地址，不直接暴露第三方 H5 token 长链接；不再调用 `/backend/interfacesvc/...` 预判/确认检测接口。

如果 B 端部署在公网域名下，建议补充：

```env
TONGUE_PUBLIC_BASE_URL=https://your-b-domain.example.com
```

该地址用于生成手机扫码入口：`/api/b/tongue-diagnosis/open/{task_id}`。

## 4. 会员创建接口

该接口用于将业务系统用户提前同步到平台。

### 4.1 请求地址

`POST https://www.ai-tongue.com/backend/check/i/secret/thirdUser/init`

### 4.2 请求头

`Authorization: Bearer {access_token}`

### 4.3 请求体

JSON 格式。

关键字段：

- `devId`
- `thirdId`
- `encryptedThirdId`
- `signEncryptedThirdId`
- `thirdName`
- `sex`
- `birthday`
- `phone`
- `thirdVip`
- `maUserOpenId`

### 4.4 用途

调用成功后：

- 普通会员单点登录时可无需短信验证码

### 4.5 特殊情况

如果返回：

```json
{
  "code": 2410112,
  "msg": "不支持用户初始化接口"
}
```

说明当前应用未开通该能力，需要联系对方开通。

## 5. H5 接入实现建议

### 5.1 后端需要实现

1. 获取并缓存 `access_token`
2. 生成稳定唯一的 `thirdId`
3. 使用平台公钥对 `thirdId` 做 RSA 加密，得到 `encryptedThirdId`
4. 使用应用私钥对 `encryptedThirdId` 做 RSA 签名，得到 `signEncryptedThirdId`
5. 拼装最终 H5 URL
6. 可选：先调用会员创建接口

### 5.2 前端需要实现

1. 在患者页面增加“进入舌诊”按钮
2. 点击后请求后端获取 H5 单点登录 URL
3. 打开 H5 页面
4. 用户在 H5 页面内完成检测

## 6. thirdId 建议

建议 `thirdId` 使用系统内稳定唯一值，例如：

- `patient_{patientId}`
- `org_{orgCode}_patient_{patientId}`

不要使用会变化的临时值。

## 7. 结果回流

H5 检测完成后，应通过以下方式把结果拿回本系统：

1. 检测报告回调
2. 检测报告检索

然后从返回结果中提取需要的字段写入现有文档。

如果当前需求只关心舌诊结果，建议优先提取：

- `tongueFeature`

其他可选字段：

- `healthIndex`
- `constitutionNames`
- `symptomName`
- `pdf`
- `time`

## 8. 本次不再做的内容

以下内容应从本次实现范围中移除：

- 纯舌诊 API 预判接口
- 纯舌诊 API 确认提交接口
- 纯舌诊 API 问诊接口
- 舌面象 API 直连
- 本地图片直传第三方的 API 直连流程
- `aesKey` 相关 `encryptData` 加解密实现
- 以 `/backend/interfacesvc/...` 为核心的检测流程

## 9. 给 Claude 的执行说明

可以直接把下面这段发给 Claude：

```text
不要再继续实现或保留 AI 舌诊 API 直连方案。对方已明确当前应用需要走 H5 会员单点登录接入，而不是 /backend/interfacesvc/... 这类接口服务。

请按以下方向调整：

1. 删除或停用纯舌诊 API 直连代码，包括预判、确认提交、问诊、回调处理等与 /backend/interfacesvc/... 相关的逻辑
2. 保留并实现 H5 路线：
   - 获取企业应用 access_token
   - 生成 thirdId
   - 使用平台公钥加密 thirdId，得到 encryptedThirdId
   - 使用应用私钥对 encryptedThirdId 签名，得到 signEncryptedThirdId
   - 拼装 https://www.ai-tongue.com/h5/sso 单点登录 URL
3. 可选接入会员创建接口 /backend/check/i/secret/thirdUser/init
4. 前端只保留“进入舌诊”入口，打开 H5 页面
5. 后续通过报告回调或报告检索获取结果，并将舌诊结果写入现有文档

本次不再保留 API 直连检测流程，不再依赖 aesKey。
```

## 10. 当前联调记录

已生成一条 H5 SSO 测试任务：

- `thirdId/outId`：`H5-TONGUE-20260507-001`
- 本地任务状态：`h5_sso_created`
- H5 地址生成成功
- 会员创建接口 `/backend/check/i/secret/thirdUser/init` 已真实调用

会员创建接口原始返回：

```json
{
  "_http_status": 200,
  "code": 1008999,
  "msg": "系统未知异常，请联系软件公司！",
  "data": null
}
```

该错误不阻塞首版 H5 打开。后续需要对方确认会员初始化接口字段格式或接口开通状态。
