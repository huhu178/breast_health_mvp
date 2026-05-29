import { reactive, ref } from 'vue'
import { apiJson, apiPostJson } from '../utils/apiClient'

export function useFollowupAiRules({
  loadAll,
  showToast,
}) {
  const ruleModal = ref(false)
  const ruleForm = reactive({
    id: null,
    name: '',
    rule_type: 'no_reply',
    task_type: 'daily_checkin',
    action: 'manual_handoff',
    trigger_keywords: '',
    response_template: ''
  })

  function newRule() {
    Object.assign(ruleForm, {
      id: null,
      name: '',
      rule_type: 'no_reply',
      task_type: 'daily_checkin',
      action: 'manual_handoff',
      trigger_keywords: '',
      response_template: ''
    })
    ruleModal.value = true
  }

  function editRule(rule) {
    Object.assign(ruleForm, {
      id: rule.id,
      name: rule.name || '',
      rule_type: rule.rule_type || 'no_reply',
      task_type: rule.task_type || '',
      action: rule.action || 'manual_handoff',
      trigger_keywords: rule.trigger_keywords || '',
      response_template: rule.response_template || ''
    })
    ruleModal.value = true
  }

  async function saveRule() {
    const payload = {
      name: ruleForm.name,
      rule_type: ruleForm.rule_type,
      task_type: ruleForm.task_type || null,
      action: ruleForm.action,
      trigger_keywords: ruleForm.trigger_keywords,
      response_template: ruleForm.response_template,
      is_active: true
    }
    if (ruleForm.id) {
      await apiJson(`/api/b/followup/ai-rules/${ruleForm.id}`, { method: 'PUT', body: JSON.stringify(payload) })
    } else {
      await apiPostJson('/api/b/followup/ai-rules', payload)
    }
    ruleModal.value = false
    await loadAll()
    showToast(ruleForm.id ? 'AI规则已更新' : 'AI规则已创建')
  }

  async function deleteRule() {
    if (!ruleForm.id) return
    await apiJson(`/api/b/followup/ai-rules/${ruleForm.id}`, { method: 'DELETE' })
    ruleModal.value = false
    await loadAll()
    showToast('AI规则已删除')
  }

  return {
    deleteRule,
    editRule,
    newRule,
    ruleForm,
    ruleModal,
    saveRule,
  }
}
