import { computed, watch } from 'vue'

export function stageForTab(tab) {
  if (tab === 'followup-plan') return 'plan'
  if (tab === 'follow') return 'follow'
  if (tab === 'review') return 'review'
  if (tab === 'record') return 'gen'
  return 'all'
}

export function usePatientManagementNavigation({
  activePatientId,
  activeStage,
  filteredQueue,
  followPatientId,
  isCheckupScenario,
  loadReports,
  planPatients,
  queue,
  recordPatient,
  rpLoaded,
  setSubTab,
  statusKey,
  subTab,
}) {
  watch(
    () => subTab.value,
    (tab) => {
      const stage = stageForTab(tab)
      activeStage.value = stage

      const list = stage === 'plan'
        ? planPatients.value
        : stage === 'follow'
          ? queue.value.filter((p) => statusKey(p) === 'follow')
          : stage === 'review'
            ? queue.value.filter((p) => statusKey(p) === 'review')
            : stage === 'gen'
              ? queue.value.filter((p) => statusKey(p) === 'gen')
              : queue.value

      if (list.length && !list.some((p) => p.id === activePatientId.value)) {
        activePatientId.value = list[0].id
      }
      if (tab === 'follow' && list.length && !list.some((p) => p.id === followPatientId.value)) {
        followPatientId.value = list[0].id
      }
      if (tab === 'review') {
        rpLoaded.value = false
        loadReports()
      }
    },
    { immediate: true }
  )

  const midTitle = computed(() => {
    const map = {
      queue: '闭环处置工作台',
      record: '患者建档',
      review: isCheckupScenario.value ? '体检报告确认' : '健康报告审核',
      follow: '任务执行'
    }
    return map[subTab.value] || '患者管理'
  })

  function setStage(key) {
    activeStage.value = key
    const list = filteredQueue.value
    if (list.length && !list.some((p) => p.id === activePatientId.value)) {
      activePatientId.value = list[0].id
    }
    if (subTab.value !== 'queue') setSubTab('queue')
  }

  function goRecord(p = null) {
    recordPatient.value = p?.id ? p : null
    if (p?.id) activePatientId.value = p.id
    setSubTab('record')
  }

  function backToQueue() {
    setSubTab('queue')
  }

  function openQueueFollowupPlan(p) {
    if (p?.id) activePatientId.value = p.id
    setSubTab('followup-plan')
  }

  return {
    backToQueue,
    goRecord,
    midTitle,
    openQueueFollowupPlan,
    setStage,
  }
}
