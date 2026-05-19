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

  return {
    riskLevelLabel,
    riskToneFromLevel,
    statusKey,
    statusLabel
  }
}
