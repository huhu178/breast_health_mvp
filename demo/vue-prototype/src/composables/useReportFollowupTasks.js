import { computed, ref } from 'vue'

export function useReportFollowupTasks({
  activePatient,
  apiJson,
  apiPostJson,
  followPatientId,
  followTasks,
  loadFollowupTasks,
  onAuditFollowupTaskCreated,
  queue,
  rpAuditId,
  selectTask,
  setSubTab,
  toast,
}) {
  const reportFollowupCreatingId = ref('')
  const reportFollowupTaskMap = ref({})

  const auditFollowupTask = computed(() => existingReportFollowupTask(rpAuditId.value, null))

  function canCreateReportFollowup(report) {
    const status = String(report?.status || '').toLowerCase()
    return ['finalized', 'published', 'archived'].includes(status)
  }

  function existingReportFollowupTask(reportId, patient = activePatient.value) {
    if (!reportId) return null
    const cached = reportFollowupTaskMap.value[String(reportId)]
    if (cached && cached.status !== 'cancelled') return cached
    if (!patient) return null
    return (patient.workspaceTasks || []).find((task) => (
      String(task.report_id || task.reportId || task.task_payload?.report_id || '') === String(reportId)
      && task.source === 'report'
      && task.status !== 'cancelled'
    )) || null
  }

  function rememberReportFollowupTasks(tasks = []) {
    const next = { ...reportFollowupTaskMap.value }
    ;(tasks || []).forEach((task) => {
      const reportId = task.report_id || task.reportId || task.task_payload?.report_id
      if (reportId && task.source === 'report' && task.status !== 'cancelled') {
        next[String(reportId)] = task
      }
    })
    reportFollowupTaskMap.value = next
  }

  async function loadReportFollowupTask(reportId) {
    if (!reportId) return null
    try {
      const data = await apiJson(`/api/b/followup/tasks?report_id=${encodeURIComponent(reportId)}&source=report&per_page=1`)
      const task = (data.items || [])[0] || null
      if (task) rememberReportFollowupTasks([task])
      return task
    } catch (e) {
      console.warn('查询报告随访任务失败', e)
      return null
    }
  }

  function isCreatingReportFollowup(reportId) {
    return String(reportFollowupCreatingId.value || '') === String(reportId || '')
  }

  function taskCheckinUrl(task) {
    if (!task) return ''
    const path = task.public_checkin_path || (task.task_code ? `/followup-checkin/${task.task_code}` : '')
    if (!path) return ''
    if (/^https?:\/\//.test(path)) return path
    return `${window.location.origin}${path}`
  }

  async function copyTaskCheckinLink(task) {
    const url = taskCheckinUrl(task)
    if (!url) return
    try {
      await navigator.clipboard.writeText(url)
      toast?.show('打卡链接已复制')
    } catch (e) {
      toast?.show('复制失败，请手动选择链接')
    }
  }

  async function createReportFollowupTask(reportId) {
    const existing = await loadReportFollowupTask(reportId)
    if (existing) {
      const err = new Error('该报告已存在首次随访任务')
      err.status = 409
      err.existingTask = existing
      throw err
    }
    const task = await apiPostJson(`/api/b/followup/tasks/from-report/${reportId}`, {})
    rememberReportFollowupTasks([task])
    return task
  }

  async function createAuditFollowupTask() {
    if (!rpAuditId.value) return
    reportFollowupCreatingId.value = String(rpAuditId.value)
    try {
      const task = await createReportFollowupTask(rpAuditId.value)
      toast?.show('已创建报告后首次随访任务')
      await onAuditFollowupTaskCreated?.value?.(task)
    } catch (e) {
      if (e.status === 409) {
        toast?.show('该报告已存在随访任务')
        if (e.existingTask) rememberReportFollowupTasks([e.existingTask])
      } else {
        toast?.show(e.message || '创建首次随访任务失败')
      }
    } finally {
      reportFollowupCreatingId.value = ''
    }
  }

  async function openReportFollowupTask(reportId) {
    const task = existingReportFollowupTask(reportId, null) || await loadReportFollowupTask(reportId)
    if (!task) {
      toast?.show('未找到该报告的随访任务')
      return
    }
    const patient = queue.value.find(p => String(p._apiId || p.id) === String(task.patient_id))
    if (patient) followPatientId.value = patient.id
    await loadFollowupTasks()
    const matched = (followTasks.value || []).find(t => String(t._apiTaskId || '').replace('api-task-', '') === String(task.id) || String(t.id) === `api-task-${task.id}`)
    if (matched) selectTask(matched.id)
    rpAuditId.value = ''
    setSubTab('follow')
  }

  return {
    auditFollowupTask,
    canCreateReportFollowup,
    copyTaskCheckinLink,
    createAuditFollowupTask,
    createReportFollowupTask,
    existingReportFollowupTask,
    isCreatingReportFollowup,
    loadReportFollowupTask,
    rememberReportFollowupTasks,
    reportFollowupCreatingId,
    taskCheckinUrl,
    openReportFollowupTask,
  }
}
