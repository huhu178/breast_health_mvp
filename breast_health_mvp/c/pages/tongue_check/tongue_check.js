/**
 * @isdoc
 * @description 舌诊检测页面（插件组件页）
 * - 当前未配置 idCode 时，仅展示“待开通”提示，不阻塞主流程
 * - 检测完成后，把 resultData 写入后端 CHealthRecord（先入档案）
 */

const plugin = requirePlugin('ai-tongue')

Page({
  data: {
    isReady: false,
    patient_id: '',
    report_id: '',
    report_code: '',
    // 舌诊插件初始化参数（没有idCode也能开发，拿到后只需填配置）
    idCode: '',
    appId: ''
  },

  /**
   * @param {Record<string, string>} options
   */
  onLoad(options) {
    const app = getApp()
    const appId = (wx.getAccountInfoSync && wx.getAccountInfoSync().miniProgram && wx.getAccountInfoSync().miniProgram.appId) || ''

    this.setData({
      patient_id: options.patient_id || '',
      report_id: options.report_id || '',
      report_code: options.report_code || '',
      appId
    })

    // 从后端拉取运行时配置（避免拿到idCode后还要发版）
    this.loadRemoteConfigAndInit()
  },

  /**
   * @isdoc
   * @description 拉取后端配置并初始化舌诊插件
   */
  loadRemoteConfigAndInit() {
    const app = getApp()
    const apiBaseUrl = (app && app.globalData && app.globalData.apiBaseUrl) ? app.globalData.apiBaseUrl : ''
    const base = String(apiBaseUrl || '').replace(/\/+$/, '')
    if (!base) {
      this.setData({ isReady: false })
      return
    }

    wx.request({
      url: `${base}/api/miniprogram/config`,
      method: 'GET',
      timeout: 15000,
      success: (res) => {
        const body = res.data || {}
        const idCode = (body && body.success && body.data && body.data.ai_tongue && body.data.ai_tongue.id_code) ? String(body.data.ai_tongue.id_code) : ''
        this.setData({ idCode, isReady: !!idCode })
        if (!idCode) return

        // userInfo：按插件文档传入（phone/nickname/sex/age等）
        // 这里先用最小字段，后续可根据你们已有问卷信息补全
        const userInfo = {
          phone: '',
          nickname: '',
          sex: 2,
          age: 0
        }

        plugin.init(idCode, this.data.appId, userInfo).then(() => {
          console.log('✅ 舌诊插件初始化成功')
          this.setData({ isReady: true })
        }).catch((e) => {
          console.error('❌ 舌诊插件初始化失败', e)
          this.setData({ isReady: false })
          wx.showToast({ title: '舌诊初始化失败', icon: 'none' })
        })
      },
      fail: () => {
        this.setData({ isReady: false })
      }
    })
  },

  /**
   * @isdoc
   * @description 检测完成回调：先入档案，等待管理师审核后再入报告
   */
  finish(e) {
    const obj = (e && e.detail) ? e.detail : {}
    if (obj.code !== 'success') {
      wx.showToast({ title: obj.msg || '舌诊检测失败', icon: 'none' })
      return
    }

    const resultId = obj.resultId
    const resultData = obj.resultData || {}

    this.submitTongueResult(resultId, resultData)
  },

  /**
   * @isdoc
   * @description 调后端接口写入 CHealthRecord
   */
  submitTongueResult(tongueResultId, tongueResultData) {
    const app = getApp()
    const apiBaseUrl = (app && app.globalData && app.globalData.apiBaseUrl) ? app.globalData.apiBaseUrl : ''
    const base = String(apiBaseUrl || '').replace(/\/+$/, '')
    if (!base) {
      wx.showToast({ title: '未配置后端地址', icon: 'none' })
      return
    }

    wx.request({
      url: `${base}/api/miniprogram/tongue/result/submit`,
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      timeout: 30000,
      data: {
        patient_id: this.data.patient_id,
        report_id: this.data.report_id,
        tongue_result_id: String(tongueResultId || ''),
        tongue_result_data: tongueResultData
      },
      success: (res) => {
        const body = res.data || {}
        if (body && body.success) {
          wx.showToast({ title: '舌诊结果已提交', icon: 'success' })
          // 返回结果页（保持原报告信息）
          wx.redirectTo({
            url: `/pages/result/result?report_id=${encodeURIComponent(this.data.report_id || '')}&report_code=${encodeURIComponent(this.data.report_code || '')}&patient_code=&need_review=1`
          })
        } else {
          const msg = (body && body.message) || `提交失败（HTTP ${res.statusCode}）`
          wx.showToast({ title: msg, icon: 'none', duration: 3000 })
        }
      },
      fail: (err) => {
        const msg = `网络失败：${err && err.errMsg ? err.errMsg : 'unknown'}`
        wx.showToast({ title: msg, icon: 'none', duration: 3000 })
      }
    })
  }
})


