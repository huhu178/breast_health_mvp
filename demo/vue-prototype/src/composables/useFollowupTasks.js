import { computed, ref, watch } from 'vue'
import {
  aiActionLabel,
  patientActionLabel,
  previewTasksFromPatient,
} from './usePatientTracking.js'

export function useFollowupTasks({
  activePatientId,
  apiJson,
  followPatientId,
  getDraft,
  noduleTypeLabel,
  planDay,
  planPatients,
  queue,
  riskToneFromLevel,
  scenario,
  subTab,
}) {
  const taskFilters = ref({
    q: '',
    risk: '',
    channel: '',
    owner: '',
    source: '',
    nodule: '',
    status: '',
  })
  const followTasks = ref([])
  const activeTaskId = ref('')

  const activeTask = computed(() => (followTasks.value || []).find((t) => t.id === activeTaskId.value) || null)
  const followPatient = computed(() => queue.value.find(p => p.id === followPatientId.value) || queue.value[0])

  const filteredPlanPatients = computed(() => {
    const q = String(taskFilters.value.q || '').trim()
    const risk = String(taskFilters.value.risk || '')
    const owner = String(taskFilters.value.owner || '').trim()
    return (planPatients.value || []).filter((p) => {
      if (q) {
        const hay = `${p.name} ${p.phoneMasked}`.toLowerCase()
        if (!hay.includes(q.toLowerCase())) return false
      }
      if (risk && p.risk !== risk) return false
      if (owner && !String(p.owner || '').includes(owner)) return false
      return true
    })
  })

  function resetTaskFilters() {
    taskFilters.value = { q: '', risk: '', channel: '', owner: '' }
  }

  function selectTask(id) {
    activeTaskId.value = id
    const t = (followTasks.value || []).find((x) => x.id === id)
    if (t?.patientId) {
      activePatientId.value = t.patientId
      followPatientId.value = t.patientId
    }
  }

  function makeTaskFromPatient(p) {
    const id = `t_${Date.now()}_${Math.random().toString(16).slice(2, 6)}`
    const planNode = (p.planTask?.nodes || [])[0] || {}
    const message = planNode.message_template || p.planTask?.note || '请按计划完成今日健康管理任务。'
    const draft = getDraft?.() || {}
    return {
      id,
      patientId: p.id,
      patientName: p.name,
      gender: p.gender,
      age: p.age,
      phoneMasked: p.phoneMasked,
      nodules: p.nodules,
      risk: p.risk,
      riskTone: p.riskTone,
      owner: p.owner || '',
      channel: draft.channel,
      cycle: draft.cycle,
      reminder: draft.reminder,
      day: planDay.value,
      time: planNode.send_time || '09:00',
      scheduledAt: '模拟排程',
      status: p.owner ? 'scheduled' : 'pending',
      node: planNode,
      message,
      patientAction: patientActionLabel(planNode.patient_action),
      aiAction: aiActionLabel(planNode.ai_action),
      kbSnapshot: JSON.parse(JSON.stringify(draft.kbEnabled || {})),
      logs: [{ at: '现在', by: '医生/运营', action: 'task_created_from_patient_plan', note: `Day ${planDay.value.replace('day', '')} · ${draft.channel} · ${draft.cycle}` }],
    }
  }

  function normalizeBackendTask(task) {
    const patient = task.patient || {}
    const node = task.task_payload?.node || {}
    const messages = task.messages || []
    const sentMessage = messages.find((m) => m.direction === 'outbound' && m.sent_at)
    return {
      id: `api-task-${task.id}`,
      _apiTaskId: task.id,
      patientId: patient.id || task.patient_id,
      patientName: patient.name || '患者',
      gender: patient.gender || '—',
      age: patient.age || '—',
      phoneMasked: patient.phone ? patient.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '—',
      nodules: noduleTypeLabel(task.nodule_type || patient.nodule_type),
      risk: task.risk_level || '—',
      riskTone: riskToneFromLevel(task.risk_level),
      owner: task.manager_name || scenario.value.defaultOwner,
      channel: task.channel === 'wecom' ? '企微' : task.channel === 'phone' ? '电话' : task.channel === 'miniapp' ? '小程序' : (task.channel || '企微'),
      cycle: '—',
      reminder: task.task_payload?.reminder_strategy || '',
      day: `day${task.plan_day || 1}`,
      time: String(task.scheduled_send_at || task.due_at || '').slice(11, 16) || node.send_time || '09:00',
      scheduledAt: task.scheduled_send_at || task.due_at || '',
      sentAt: sentMessage?.sent_at || '',
      status: task.status === 'completed' ? 'completed' : (task.status || 'scheduled'),
      node,
      taskPayload: task.task_payload || {},
      message: node.message_template || task.ai_summary || '',
      patientAction: patientActionLabel(node.patient_action),
      aiAction: aiActionLabel(node.ai_action),
      messages,
      kbSnapshot: {},
      logs: (task.events || []).map(e => ({ at: e.created_at || '现在', by: e.actor_type || '系统', action: e.event_type, note: e.summary || '' })),
      createdAt: task.created_at || '',
    }
  }

  async function loadFollowupTasks() {
    try {
      const data = await apiJson('/api/b/followup/tasks?per_page=100')
      const items = data.items || data || []
      const apiTasks = items.map(normalizeBackendTask)
      if (apiTasks.length) {
        const localOnly = (followTasks.value || []).filter((t) => !t._apiTaskId)
        followTasks.value = [...apiTasks, ...localOnly]
        if (!activeTaskId.value || !followTasks.value.some((t) => t.id === activeTaskId.value)) {
          const firstForPatient = followPatientId.value
            ? followTasks.value.find((t) => String(t.patientId) === String(followPatientId.value))
            : null
          if (firstForPatient || followTasks.value[0]) selectTask((firstForPatient || followTasks.value[0]).id)
        }
      }
    } catch (e) {
      console.warn('加载随访任务失败', e)
    }
  }

  watch(
    () => subTab.value,
    (k) => {
      if (k !== 'follow') return
      loadFollowupTasks()
    },
    { immediate: true }
  )

  watch(
    () => [subTab.value, planPatients.value.length],
    () => {
      if (subTab.value !== 'followup-plan') return
      const list = planPatients.value || []
      if (!list.length) return
      if (!list.some((p) => p.id === activePatientId.value)) activePatientId.value = list[0].id
      if (!(followTasks.value || []).length) {
        const seeded = list.filter((p) => p?.planTask).slice(0, 8).flatMap((p) => previewTasksFromPatient(p, planDay.value))
        followTasks.value = seeded
        if (seeded[0]) selectTask(seeded[0].id)
      }
    },
    { immediate: true }
  )

  return {
    activeTask,
    activeTaskId,
    filteredPlanPatients,
    followPatient,
    followTasks,
    loadFollowupTasks,
    makeTaskFromPatient,
    normalizeBackendTask,
    resetTaskFilters,
    selectTask,
    taskFilters,
  }
}
