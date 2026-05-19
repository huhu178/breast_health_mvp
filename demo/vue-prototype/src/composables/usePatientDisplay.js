export function usePatientDisplay({ scenario, isCheckupScenario }) {
  function statusKey(patient) {
    const stage = String(patient?.stage || '')
    if (['record', 'upload', 'aiGen', 'push', 'recall'].includes(stage)) return 'gen'
    if (stage === 'review') return 'review'
    if (stage === 'follow') return 'follow'
    return 'plan'
  }

  function statusLabel(patient) {
    const key = statusKey(patient)
    const reportLabel = scenario.value.reportLabel
    if (key === 'gen') return `${reportLabel}待生成`
    if (key === 'review') return isCheckupScenario.value ? '待总检确认' : '健康报告待审核'
    if (key === 'plan') return '任务待下发'
    return '任务执行中'
  }

  function riskLevelLabel(risk) {
    const map = {
      high: '高风险',
      mid: '中风险',
      medium: '中风险',
      low: '低风险',
      '高危': '高风险',
      '中危': '中风险',
      '低危': '低风险'
    }
    return map[risk] || risk || '通用风险'
  }

  function riskToneFromLevel(risk) {
    const label = riskLevelLabel(risk)
    if (label === '高风险') return 'r'
    if (label === '中风险') return 'o'
    if (label === '低风险') return 'g'
    return 'g'
  }

  function noduleTypeLabel(type) {
    const map = {
      breast: '乳腺结节',
      lung: '肺部结节',
      thyroid: '甲状腺结节',
      breast_lung: '乳腺+肺部结节',
      breast_thyroid: '乳腺+甲状腺结节',
      lung_thyroid: '肺部+甲状腺结节',
      triple: '三合并结节'
    }
    return map[type] || type || '—'
  }

  function channelLabel(channel) {
    const map = { wecom: '企业微信', phone: '电话', miniapp: '小程序' }
    return map[channel] || channel || '企业微信'
  }

  function templateStatusLabel(status) {
    const map = { draft: '草稿', active: '启用', paused: '暂停', archived: '归档' }
    return map[status] || status || '模板'
  }

  function planStatusLabel(status) {
    const map = { draft: '草稿', active: '执行中', paused: '已暂停', completed: '已完成', cancelled: '已取消' }
    return map[status] || status || '计划'
  }

  function taskTypeLabel(type) {
    const map = {
      knowledge: '知识推送',
      knowledge_push: '知识推送',
      daily_checkin: '每日打卡',
      diet_checkin: '饮食打卡',
      diet_image_checkin: '餐饮图片打卡',
      breakfast_checkin: '早餐打卡',
      lunch_checkin: '午餐打卡',
      dinner_checkin: '晚餐打卡',
      exercise_reminder: '运动提醒',
      psych_reminder: '心理关怀',
      review_reminder: '复查提醒',
      manual: '人工处理'
    }
    return map[type] || type || '随访任务'
  }

  return {
    channelLabel,
    noduleTypeLabel,
    planStatusLabel,
    riskLevelLabel,
    riskToneFromLevel,
    statusKey,
    statusLabel,
    taskTypeLabel,
    templateStatusLabel
  }
}
