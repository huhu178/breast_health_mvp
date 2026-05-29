import { computed, watch } from 'vue'

export function useFollowupTrackingView({
  activeTaskId,
  followPatient,
  followPatientId,
  followRiskFilter,
  followSearch,
  followStageFilter,
  followTasks,
  planDay,
  queue,
  statusKey,
  trackingTasksForPatient,
}) {
  const followFilteredQueue = computed(() => {
    const taskPatientIds = new Set((followTasks.value || []).map((t) => String(t.patientId)))
    return queue.value
      .filter((p) => statusKey(p) === 'follow' || taskPatientIds.has(String(p.id)))
      .filter((p) => {
        const s = followSearch.value.trim().toLowerCase()
        if (s && !p.name.toLowerCase().includes(s) && !p.phoneMasked.includes(s)) return false
        if (followRiskFilter.value && p.risk !== followRiskFilter.value) return false
        if (followStageFilter.value && statusKey(p) !== followStageFilter.value) return false
        return true
      })
  })

  const followTrackingStats = computed(() => {
    const list = queue.value || []
    const followList = list.filter((p) => statusKey(p) === 'follow')
    return {
      runningPatients: followList.length,
      highRisk: followList.filter((p) => p.riskTone === 'r').length,
      midRisk: followList.filter((p) => p.riskTone === 'o').length,
      lowRisk: followList.filter((p) => p.riskTone === 'g').length,
      unconfigured: followList.filter((p) => !p.planTask || !p.planTask.day).length,
      configured: followList.filter((p) => p.planTask && p.planTask.day).length,
    }
  })

  watch(
    () => followPatientId.value,
    () => {
      const d = followPatient.value?.planTask?.day
      if (typeof d === 'string' && d.startsWith('day')) planDay.value = d
      const firstTask = trackingTasksForPatient.value[0]
      if (firstTask && !trackingTasksForPatient.value.some((t) => t.id === activeTaskId.value)) {
        activeTaskId.value = firstTask.id
      }
    }
  )

  return {
    followFilteredQueue,
    followTrackingStats,
  }
}
