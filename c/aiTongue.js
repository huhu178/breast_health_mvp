/**
 * @isdoc
 * @description 导出到舌诊插件的全局方法文件（供插件调用）
 * - judgeCheck：从检测记录列表进入报告页时的校验钩子（这里默认放行）
 * - backHome：插件内“返回小程序”时的兜底行为（重启回首页）
 */

function judgeCheck(resultId, toResult, resultData) {
  // 目前不做支付校验，直接进入结果页
  if (typeof toResult === 'function') toResult()
}

function backHome() {
  wx.restartMiniProgram({
    path: '/pages/index/index'
  })
}

module.exports = {
  judgeCheck,
  backHome
}


