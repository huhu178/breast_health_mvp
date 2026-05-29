import { reactive, ref } from 'vue'
import { apiJson, apiPostJson } from '../utils/apiClient'

export function splitKeywords(text) {
  return String(text || '')
    .split(/[,，、\n]/)
    .map(item => item.trim())
    .filter(Boolean)
}

export function joinKeywords(items) {
  return Array.isArray(items) ? items.join(',') : ''
}

export function useFollowupTemplateNodes({
  error,
  loadAll,
  selectedTemplateId,
  showToast,
  sortedNodes,
}) {
  const nodeModal = ref(false)
  const nodeForm = reactive({
    id: null,
    name: '',
    day_offset: 1,
    send_time: '09:00',
    task_type: 'knowledge_push',
    patient_action: 'reply_text',
    ai_action: 'reply',
    message_template: '',
    knowledge_item_ids: [],
    doctor_keywords_text: '',
    manual_keywords_text: '',
    no_reply_threshold: 3,
    completion_type: 'patient_reply',
    overdue_action: 'manual_handoff',
    is_required: true,
    is_active: true,
    sort_order: 0
  })

  function addNode() {
    Object.assign(nodeForm, {
      id: null,
      name: '新的任务节点',
      day_offset: Math.max(1, ...sortedNodes.value.map(n => Number(n.day_offset || 0) + 7)),
      send_time: '09:00',
      task_type: 'knowledge_push',
      patient_action: 'reply_text',
      ai_action: 'reply',
      message_template: '请按健康管理任务完成本次打卡或查看提醒。',
      knowledge_item_ids: [],
      doctor_keywords_text: '不适,疼痛,明显加重',
      manual_keywords_text: '焦虑,担心,睡不着',
      no_reply_threshold: 3,
      completion_type: 'patient_reply',
      overdue_action: 'manual_handoff',
      is_required: true,
      is_active: true,
      sort_order: Math.max(0, ...sortedNodes.value.map(n => Number(n.sort_order ?? n.day_offset ?? 0))) + 1
    })
    nodeModal.value = true
  }

  function editNode(node) {
    const escalationRule = node.escalation_rule || {}
    const completionRule = node.completion_rule || {}
    Object.assign(nodeForm, {
      id: node.id,
      name: node.name || '',
      day_offset: node.day_offset || 1,
      send_time: node.send_time || '09:00',
      task_type: node.task_type || 'knowledge_push',
      patient_action: node.patient_action || 'reply_text',
      ai_action: node.ai_action || 'reply',
      message_template: node.message_template || '',
      knowledge_item_ids: [...(node.knowledge_item_ids || [])],
      doctor_keywords_text: joinKeywords(escalationRule.doctor_keywords),
      manual_keywords_text: joinKeywords(escalationRule.manual_keywords),
      no_reply_threshold: Number(escalationRule.no_reply_threshold ?? 3),
      completion_type: completionRule.type || 'patient_reply',
      overdue_action: completionRule.overdue_action || 'manual_handoff',
      is_required: node.is_required !== false,
      is_active: node.is_active !== false,
      sort_order: node.sort_order ?? node.day_offset ?? 0
    })
    nodeModal.value = true
  }

  function buildEscalationRule() {
    const doctorKeywords = splitKeywords(nodeForm.doctor_keywords_text)
    const manualKeywords = splitKeywords(nodeForm.manual_keywords_text)
    return {
      doctor_keywords: doctorKeywords,
      manual_keywords: manualKeywords,
      no_reply_threshold: Number(nodeForm.no_reply_threshold) || 0,
      abnormal_actions: {
        doctor_keywords: 'doctor_handoff',
        manual_keywords: 'manual_handoff',
        no_reply: nodeForm.overdue_action
      }
    }
  }

  function buildCompletionRule() {
    return {
      type: nodeForm.completion_type,
      overdue_action: nodeForm.overdue_action,
      required: nodeForm.is_required !== false
    }
  }

  function nodePayloadFromNode(node, overrides = {}) {
    return {
      name: node.name,
      day_offset: node.day_offset,
      send_time: node.send_time,
      task_type: node.task_type,
      patient_action: node.patient_action,
      ai_action: node.ai_action,
      message_template: node.message_template,
      knowledge_item_ids: node.knowledge_item_ids || [],
      checkin_schema: node.checkin_schema || {},
      escalation_rule: node.escalation_rule || {},
      completion_rule: node.completion_rule || {},
      is_required: node.is_required !== false,
      is_active: node.is_active !== false,
      sort_order: node.sort_order ?? node.day_offset ?? 0,
      ...overrides
    }
  }

  async function saveNode() {
    try {
      const payload = {
        name: nodeForm.name,
        day_offset: Number(nodeForm.day_offset) || 1,
        send_time: nodeForm.send_time,
        task_type: nodeForm.task_type,
        patient_action: nodeForm.patient_action,
        ai_action: nodeForm.ai_action,
        message_template: nodeForm.message_template,
        knowledge_item_ids: nodeForm.knowledge_item_ids.map(Number),
        escalation_rule: buildEscalationRule(),
        completion_rule: buildCompletionRule(),
        is_required: nodeForm.is_required !== false,
        is_active: nodeForm.is_active !== false,
        sort_order: nodeForm.sort_order ?? (Number(nodeForm.day_offset) || 0)
      }
      if (nodeForm.id) {
        await apiJson(`/api/b/followup/nodes/${nodeForm.id}`, { method: 'PUT', body: JSON.stringify(payload) })
      } else {
        await apiPostJson(`/api/b/followup/templates/${selectedTemplateId.value}/nodes`, payload)
      }
      nodeModal.value = false
      await loadAll()
      showToast('节点已保存')
    } catch (e) {
      error.value = e?.message || '节点保存失败'
    }
  }

  async function toggleNodeActive(node) {
    await apiJson(`/api/b/followup/nodes/${node.id}`, {
      method: 'PUT',
      body: JSON.stringify(nodePayloadFromNode(node, { is_active: node.is_active === false }))
    })
    await loadAll()
    showToast(node.is_active === false ? '节点已启用' : '节点已停用')
  }

  async function copyNode(node) {
    const payload = nodePayloadFromNode(node, {
      node_code: `${node.node_code || 'NODE'}_COPY_${Date.now().toString().slice(-4)}`,
      name: `${node.name} 副本`,
      sort_order: Math.max(0, ...sortedNodes.value.map(item => Number(item.sort_order ?? item.day_offset ?? 0))) + 1
    })
    await apiPostJson(`/api/b/followup/templates/${selectedTemplateId.value}/nodes`, payload)
    await loadAll()
    showToast('节点已复制')
  }

  async function moveNode(node, direction) {
    const nodes = sortedNodes.value
    const index = nodes.findIndex(item => item.id === node.id)
    const target = nodes[index + direction]
    if (!target) return
    const currentOrder = Number(node.sort_order ?? index)
    const targetOrder = Number(target.sort_order ?? (index + direction))
    await Promise.all([
      apiJson(`/api/b/followup/nodes/${node.id}`, {
        method: 'PUT',
        body: JSON.stringify(nodePayloadFromNode(node, { sort_order: targetOrder }))
      }),
      apiJson(`/api/b/followup/nodes/${target.id}`, {
        method: 'PUT',
        body: JSON.stringify(nodePayloadFromNode(target, { sort_order: currentOrder }))
      })
    ])
    await loadAll()
    showToast('节点顺序已更新')
  }

  async function deleteNode() {
    await apiJson(`/api/b/followup/nodes/${nodeForm.id}`, { method: 'DELETE' })
    nodeModal.value = false
    await loadAll()
    showToast('节点已删除')
  }

  return {
    addNode,
    buildCompletionRule,
    buildEscalationRule,
    copyNode,
    deleteNode,
    editNode,
    joinKeywords,
    moveNode,
    nodeForm,
    nodeModal,
    nodePayloadFromNode,
    saveNode,
    splitKeywords,
    toggleNodeActive,
  }
}
