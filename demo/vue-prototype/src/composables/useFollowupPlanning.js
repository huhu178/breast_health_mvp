import { computed, ref } from 'vue'

export function useFollowupPlanning({
  apiJson,
  aiActionLabel,
  patientActionLabel,
  taskTypeLabel,
}) {
  const planState = ref({
    loading: true,
    error: '',
    title: '',
    sourceFile: '',
    days: {},
  })
  const planDay = ref('day1')
  const followupTemplates = ref([])
  const followupRecommendation = ref(null)
  const selectedFollowupTemplateId = ref(null)
  const followupKnowledgeItems = ref([])

  async function loadPlan() {
    planState.value.loading = true
    planState.value.error = ''
    try {
      const res = await fetch('/plans/thyroid-lung-psych.json', { cache: 'no-cache' })
      if (!res.ok) throw new Error(`加载计划失败：${res.status}`)
      const data = await res.json()
      planState.value = {
        loading: false,
        error: '',
        title: data?.title ?? '',
        sourceFile: data?.sourceFile ?? '',
        days: data?.days ?? {},
      }
      if (!planState.value.days?.[planDay.value]) {
        const first = Object.keys(planState.value.days ?? {})[0]
        if (first) planDay.value = first
      }
    } catch (e) {
      planState.value.loading = false
      planState.value.error = e?.message || '加载计划失败'
    }
  }

  async function loadFollowupPlanningConfig() {
    try {
      const templates = await apiJson('/api/b/followup/templates?status=active&include_nodes=1')
      followupTemplates.value = Array.isArray(templates) ? templates : []
      if (!selectedFollowupTemplateId.value && followupTemplates.value[0]?.id) {
        selectedFollowupTemplateId.value = followupTemplates.value[0].id
      }
      const knowledge = await apiJson('/api/b/followup/knowledge?per_page=100')
      followupKnowledgeItems.value = knowledge?.items || []
    } catch (e) {
      followupTemplates.value = []
      followupKnowledgeItems.value = []
    }
  }

  const planDayList = computed(() => {
    const keys = Object.keys(planState.value.days ?? {})
    return keys.sort((a, b) => Number(a.replace('day', '')) - Number(b.replace('day', '')))
  })

  const currentPlanRows = computed(() => planState.value.days?.[planDay.value] ?? [])

  const availableFollowupTemplates = computed(() => followupTemplates.value || [])

  const selectedWorkflowTemplate = computed(() => {
    return availableFollowupTemplates.value.find((tpl) => tpl.id === selectedFollowupTemplateId.value) || availableFollowupTemplates.value[0] || null
  })

  function selectFollowupTemplate(tpl) {
    if (!tpl?.id) return
    selectedFollowupTemplateId.value = tpl.id
    if (tpl.nodes?.[0]?.day_offset) planDay.value = `day${tpl.nodes[0].day_offset}`
  }

  const activePlanNodes = computed(() => {
    const nodes = selectedWorkflowTemplate.value?.nodes || followupRecommendation.value?.nodes || []
    return Array.isArray(nodes) ? nodes : []
  })

  const activePlanNodePreviews = computed(() => {
    const selectedDay = Number(String(planDay.value || 'day1').replace('day', '')) || 1
    return activePlanNodes.value.filter((node) => {
      return Number(node.day_offset || 1) === selectedDay
    }).map((node, idx) => ({
      key: node.node_code || node.id || idx,
      day: Number(node.day_offset || 1),
      time: node.send_time || '09:00',
      name: node.name || `随访任务 ${idx + 1}`,
      type: taskTypeLabel(node.task_type),
      patientAction: patientActionLabel(node.patient_action),
      aiAction: aiActionLabel(node.ai_action),
      message: node.message_template || node.content || node.description || '',
    }))
  })

  return {
    activePlanNodePreviews,
    activePlanNodes,
    availableFollowupTemplates,
    currentPlanRows,
    followupKnowledgeItems,
    followupRecommendation,
    followupTemplates,
    loadFollowupPlanningConfig,
    loadPlan,
    planDay,
    planDayList,
    planState,
    selectFollowupTemplate,
    selectedFollowupTemplateId,
    selectedWorkflowTemplate,
  }
}
