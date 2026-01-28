// app.js
/**
 * @file 小程序全局入口
 *
 * @description
 * - 本地联调阶段：通过设置 `globalData.apiBaseUrl` 指向本机后端（建议局域网IP）
 * - 生产阶段：切换为 HTTPS 域名，并在微信后台配置“request合法域名”
 */
App({
  /**
   * @description 全局数据
   */
  globalData: {
    /**
     * @description 后端 API 基地址
     * @example "http://192.168.1.10:5000"
     */
    apiBaseUrl: 'http://127.0.0.1:5000'
  }
})
