export function usePatientStageActions({
  generateReportForPatient,
  goRecord,
  isCheckupScenario,
  openPatientWorkspace,
  reportGeneratingIds,
  scenario,
  setSubTab,
  statusKey,
}) {
  function nextHintV2(p) {
    const k = statusKey(p)
    if (k === 'gen') return `系统将根据档案资料生成${scenario.value.reportLabel}草稿。`
    if (k === 'review') return `${scenario.value.reportLabel}已生成，建议优先完成确认。`
    if (k === 'plan') return `${scenario.value.reportLabel}已确认，等待下发随访任务。`
    if (k === 'follow') return '患者任务执行中，可查看任务记录。'
    return `请先完成患者档案建立，后续才能生成${scenario.value.reportLabel}。`
  }

  function flowNodes(p) {
    const k = statusKey(p)
    const labels = [
      { k: 'a', label: '建立档案' },
      { k: 'b', label: `${scenario.value.reportLabel}生成` },
      { k: 'c', label: isCheckupScenario.value ? '总检确认' : '健康报告审核' },
      { k: 'd', label: '随访任务下发' },
      { k: 'e', label: '任务执行' },
    ]
    const curIdx = k === 'follow' ? 4 : k === 'plan' ? 3 : k === 'review' ? 2 : 1

    return labels.map((x, i) => ({
      ...x,
      state: i < curIdx ? 'done' : i === curIdx ? 'current' : 'todo'
    }))
  }

  function stageActions(p) {
    const k = statusKey(p)
    if (k === 'gen') {
      const generating = reportGeneratingIds.value.has(p?.id)
      return [
        { label: generating ? '生成中...' : (isCheckupScenario.value ? '生成解读' : '生成报告'), primary: true, disabled: generating, onClick: () => generateReportForPatient(p) },
        { label: '全流程管理', primary: false, onClick: () => openPatientWorkspace(p) },
      ]
    }
    if (k === 'review') {
      return [
        { label: isCheckupScenario.value ? '总检确认' : '审核报告', primary: true, onClick: () => openPatientWorkspace(p) },
        { label: '报告列表', primary: false, onClick: () => setSubTab('review') },
      ]
    }
    if (k === 'plan') {
      return [{ label: '随访任务下发', primary: true, onClick: () => openPatientWorkspace(p) }]
    }
    if (k === 'follow') {
      return [
        { label: '查看全流程', primary: true, onClick: () => openPatientWorkspace(p) },
        { label: '执行跟踪', primary: false, onClick: () => setSubTab('follow') },
      ]
    }
    return [{ label: '建立档案', primary: true, onClick: () => goRecord(p) }]
  }

  function stageTimeline(p) {
    const k = statusKey(p)
    const baseAt = String(p?.timeline?.[p.timeline.length - 1]?.at || '刚刚')
    if (k === 'gen' || k === 'new') {
      return [
        { at: baseAt, tone: 'b', text: '档案资料已提交' },
        { at: '—', tone: 'b', text: '检查报告已归档' },
        { at: '—', tone: 'o', text: `等待生成${scenario.value.reportLabel}` },
      ]
    }
    if (k === 'review') {
      return [
        { at: baseAt, tone: 'p', text: `${scenario.value.reportLabel}已生成` },
        { at: '—', tone: 'o', text: isCheckupScenario.value ? '进入总检确认队列' : '进入待审核队列' },
        { at: '—', tone: 'o', text: isCheckupScenario.value ? '等待总检确认' : '等待人工审核' },
      ]
    }
    if (k === 'plan') {
      return [
        { at: baseAt, tone: 'g', text: `${scenario.value.reportLabel}已确认` },
        { at: '—', tone: 'b', text: '患者报告已推送' },
        { at: '—', tone: 'o', text: '等待下发随访任务' },
      ]
    }
    return [
      { at: baseAt, tone: 'b', text: '任务已下发' },
      { at: '—', tone: 'g', text: '等待用户打卡' },
      { at: '—', tone: 'p', text: '可查看任务执行记录' },
    ]
  }

  return {
    flowNodes,
    nextHintV2,
    stageActions,
    stageTimeline,
  }
}
