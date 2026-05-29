import { computed, reactive, ref } from 'vue'
import { apiJson, apiPostJson } from '../utils/apiClient'

export function useFollowupKnowledge({
  knowledgeItems,
  loadAll,
  showToast,
}) {
  const knowledgeModal = ref(false)
  const knowledgeFilters = reactive({
    search: '',
    category: '',
    task_type: ''
  })
  const knowledgeForm = reactive({
    id: null,
    title: '',
    category: 'script',
    task_type: '',
    priority: 5,
    trigger_keywords: '',
    content: ''
  })

  const filteredKnowledgeItems = computed(() => {
    const search = knowledgeFilters.search.toLowerCase()
    return knowledgeItems.value.filter(item => {
      if (knowledgeFilters.category && item.category !== knowledgeFilters.category) return false
      if (knowledgeFilters.task_type && item.task_type !== knowledgeFilters.task_type) return false
      if (!search) return true
      return `${item.title || ''} ${item.content || ''} ${item.trigger_keywords || ''}`.toLowerCase().includes(search)
    })
  })

  function newKnowledge() {
    Object.assign(knowledgeForm, { id: null, title: '', category: 'diet', task_type: '', priority: 5, trigger_keywords: '', content: '' })
    knowledgeModal.value = true
  }

  function editKnowledge(item) {
    Object.assign(knowledgeForm, {
      id: item.id,
      title: item.title || '',
      category: item.category || 'script',
      task_type: item.task_type || '',
      priority: item.priority || 5,
      trigger_keywords: item.trigger_keywords || '',
      content: item.content || ''
    })
    knowledgeModal.value = true
  }

  async function saveKnowledge() {
    const payload = {
      title: knowledgeForm.title,
      category: knowledgeForm.category,
      task_type: knowledgeForm.task_type || null,
      priority: Number(knowledgeForm.priority) || 5,
      trigger_keywords: knowledgeForm.trigger_keywords,
      content: knowledgeForm.content,
      is_active: true
    }
    if (knowledgeForm.id) {
      await apiJson(`/api/b/followup/knowledge/${knowledgeForm.id}`, { method: 'PUT', body: JSON.stringify(payload) })
    } else {
      await apiPostJson('/api/b/followup/knowledge', payload)
    }
    knowledgeModal.value = false
    await loadAll()
    showToast('知识库已保存')
  }

  async function deleteKnowledge() {
    await apiJson(`/api/b/followup/knowledge/${knowledgeForm.id}`, { method: 'DELETE' })
    knowledgeModal.value = false
    await loadAll()
    showToast('知识条目已删除')
  }

  return {
    deleteKnowledge,
    editKnowledge,
    filteredKnowledgeItems,
    knowledgeFilters,
    knowledgeForm,
    knowledgeModal,
    newKnowledge,
    saveKnowledge,
  }
}
