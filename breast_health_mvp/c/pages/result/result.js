// pages/result/result.js
Page({
  data: {
    report_id: '',
    report_code: '',
    patient_code: '',
    patient_id: '',
    need_review: false,
    manager_contact: null
  },

  /**
   * @isdoc
   * @description 结果页初始化：展示报告编号信息，并尝试拉取健康管理师联系方式（用于一键联系）
   * @param {Record<string, string>} options
   */
  onLoad(options) {
    this.setData({
      report_id: options.report_id || '',
      report_code: options.report_code || '',
      patient_code: options.patient_code || '',
      patient_id: options.patient_id || '',
      need_review: String(options.need_review || '') === '1'
    })

    this.loadReportSummary()
  },

  /**
   * @isdoc
   * @description 拉取报告摘要（含健康管理师联系方式）
   */
  loadReportSummary() {
    const app = getApp()
    const apiBaseUrl = (app && app.globalData && app.globalData.apiBaseUrl) ? app.globalData.apiBaseUrl : ''
    const base = String(apiBaseUrl || '').replace(/\/+$/, '')
    if (!base) return

    const reportId = this.data.report_id
    const reportCode = this.data.report_code
    if (!reportId || !reportCode) return

    wx.request({
      url: `${base}/api/miniprogram/reports/${encodeURIComponent(reportId)}/summary`,
      method: 'GET',
      timeout: 20000,
      data: { report_code: reportCode },
      success: (res) => {
        const body = res.data || {}
        if (body && body.success) {
          const d = body.data || {}
          this.setData({
            need_review: !!d.need_review,
            patient_code: d.patient_code || this.data.patient_code,
            manager_contact: d.manager_contact || null
          })
        }
      }
    })
  },

  /**
   * @isdoc
   * @description 一键拨打健康管理师电话
   */
  callManager() {
    const phone = this.data.manager_contact && this.data.manager_contact.manager_phone
    if (!phone) return
    wx.makePhoneCall({ phoneNumber: phone })
  },

  /**
   * @isdoc
   * @description 复制健康管理师微信号
   */
  copyManagerWechat() {
    const wechat = this.data.manager_contact && this.data.manager_contact.manager_wechat
    if (!wechat) return
    wx.setClipboardData({
      data: wechat,
      success: () => wx.showToast({ title: '已复制微信号', icon: 'success', duration: 1500 })
    })
  },

  backHome() {
    wx.reLaunch({ url: '/pages/index/index' })
  },

  /**
   * @isdoc
   * @description 跳转到舌诊检测页（插件组件）
   */
  goTongueCheck() {
    wx.redirectTo({
      url: `/pages/tongue_check/tongue_check?patient_id=${encodeURIComponent(this.data.patient_id || '')}&report_id=${encodeURIComponent(this.data.report_id || '')}&report_code=${encodeURIComponent(this.data.report_code || '')}`
    })
  }
})


