import { computed, ref } from 'vue'
import { apiJson } from '../utils/apiClient'

export function useFollowupWorkflowConfig() {
  const templates = ref([])
  const knowledgeItems = ref([])
  const aiRules = ref([])
  const selectedTemplateId = ref(null)
  const loading = ref(false)
  const importingExcel = ref(false)
  const error = ref('')
  const toast = ref('')

  const selectedTemplate = computed(() => templates.value.find(t => t.id === selectedTemplateId.value) || null)
  const sortedNodes = computed(() => [...(selectedTemplate.value?.nodes || [])].sort((a, b) => {
    const sortA = Number(a.sort_order ?? a.day_offset ?? 0)
    const sortB = Number(b.sort_order ?? b.day_offset ?? 0)
    if (sortA !== sortB) return sortA - sortB
    return (a.day_offset || 0) - (b.day_offset || 0)
  }))
  const totalNodes = computed(() => templates.value.reduce((sum, tpl) => sum + (tpl.nodes?.length || 0), 0))

  function showToast(text) {
    toast.value = text
    window.setTimeout(() => {
      if (toast.value === text) toast.value = ''
    }, 2200)
  }

  async function loadAll() {
    loading.value = true
    error.value = ''
    try {
      const [tpls, knowledge, rules] = await Promise.all([
        apiJson('/api/b/followup/templates?include_nodes=1'),
        apiJson('/api/b/followup/knowledge?per_page=100'),
        apiJson('/api/b/followup/ai-rules')
      ])
      templates.value = Array.isArray(tpls) ? tpls : []
      knowledgeItems.value = knowledge?.items || []
      aiRules.value = Array.isArray(rules) ? rules : []
      if (!selectedTemplateId.value && templates.value.length) selectedTemplateId.value = templates.value[0].id
    } catch (e) {
      error.value = e?.message || '加载随访知识库与模板失败'
    } finally {
      loading.value = false
    }
  }

  async function handleExcelImport(event) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    importingExcel.value = true
    error.value = ''
    try {
      const form = new FormData()
      form.append('file', file)
      form.append('replace_existing', 'true')
      form.append('name', '甲状腺结节合并肺结节90天健康管理模板')
      form.append('nodule_type', 'lung_thyroid')
      form.append('cycle_days', '90')
      form.append('default_channel', 'wecom')
      form.append('status', 'active')
      const res = await fetch('/api/b/followup/templates/import-excel', {
        method: 'POST',
        credentials: 'include',
        body: form
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok || data.success === false) throw new Error(data.message || `导入失败：${res.status}`)
      const result = data.data || data
      selectedTemplateId.value = result.template?.id || selectedTemplateId.value
      await loadAll()
      showToast(`已导入 ${result.days || 0} 天、${result.nodes || 0} 个任务节点`)
    } catch (e) {
      error.value = e?.message || 'Excel模板导入失败'
    } finally {
      importingExcel.value = false
    }
  }

  return {
    aiRules,
    error,
    handleExcelImport,
    importingExcel,
    knowledgeItems,
    loadAll,
    loading,
    selectedTemplate,
    selectedTemplateId,
    showToast,
    sortedNodes,
    templates,
    toast,
    totalNodes,
  }
}
