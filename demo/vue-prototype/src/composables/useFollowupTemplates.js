import { reactive, ref } from 'vue'
import { apiJson, apiPostJson } from '../utils/apiClient'

export function useFollowupTemplates({
  error,
  loadAll,
  selectedTemplate,
  selectedTemplateId,
  showToast,
  sortedNodes,
}) {
  const saving = ref(false)
  const templateForm = reactive({
    id: null,
    name: '',
    description: '',
    nodule_type: '',
    risk_level: '',
    cycle_days: 90,
    default_channel: 'wecom',
    default_reminder_strategy: '每日固定时间提醒；未打卡继续提醒；餐饮图片自动分析',
    status: 'draft'
  })

  function fillTemplateForm(tpl) {
    templateForm.id = tpl?.id || null
    templateForm.name = tpl?.name || ''
    templateForm.description = tpl?.description || ''
    templateForm.nodule_type = tpl?.nodule_type || ''
    templateForm.risk_level = tpl?.risk_level || ''
    templateForm.cycle_days = tpl?.cycle_days || 90
    templateForm.default_channel = tpl?.default_channel || 'wecom'
    templateForm.default_reminder_strategy = tpl?.default_reminder_strategy || '每日固定时间提醒；未打卡继续提醒；餐饮图片自动分析'
    templateForm.status = tpl?.status || 'draft'
  }

  function selectTemplate(id) {
    selectedTemplateId.value = id
    fillTemplateForm(selectedTemplate.value)
  }

  function createTemplate() {
    selectedTemplateId.value = null
    fillTemplateForm({
      name: '新的健康管理任务模板',
      nodule_type: '',
      risk_level: '',
      cycle_days: 90,
      default_channel: 'wecom',
      status: 'draft'
    })
  }

  function getTemplateIssues() {
    const issues = []
    if (!templateForm.name) issues.push('模板名称不能为空')
    if (!selectedTemplateId.value) return issues
    const nodes = sortedNodes.value
    if (!nodes.length) issues.push('至少需要 1 个节点')
    nodes.forEach((node) => {
      if (node.is_active === false) return
      if (!node.name) issues.push(`Day ${node.day_offset || 1} 缺少节点名称`)
      if (!String(node.message_template || '').trim()) issues.push(`${node.name || `Day ${node.day_offset || 1}`} 缺少发送话术`)
      if (node.task_type === 'diet_checkin' && node.ai_action !== 'diet_review') issues.push(`${node.name || '饮食打卡节点'} 应配置饮食点评 AI 动作`)
      if (node.task_type === 'diet_checkin' && !['diet_review', 'image_recognition'].includes(node.ai_action)) issues.push(`${node.name || '饮食打卡节点'} 应配置饮食点评或图片识别`)
    })
    return issues
  }

  function validateTemplate() {
    const issues = getTemplateIssues()
    if (issues.length) {
      error.value = `校验未通过：${issues.join('；')}`
      return
    }
    error.value = ''
    showToast('模板校验通过，可以启用并下发给用户')
  }

  async function saveTemplate() {
    saving.value = true
    error.value = ''
    try {
      templateForm.default_channel = 'wecom'
      if (templateForm.status === 'active') {
        const issues = getTemplateIssues()
        if (issues.length) {
          error.value = `模板暂不能启用：${issues.join('；')}`
          return
        }
      }
      const payload = {
        name: templateForm.name,
        description: templateForm.description,
        nodule_type: templateForm.nodule_type || null,
        risk_level: templateForm.risk_level || null,
        cycle_days: Number(templateForm.cycle_days) || 90,
        default_channel: templateForm.default_channel,
        default_reminder_strategy: templateForm.default_reminder_strategy,
        status: templateForm.status
      }
      const saved = templateForm.id
        ? await apiJson(`/api/b/followup/templates/${templateForm.id}`, { method: 'PUT', body: JSON.stringify(payload) })
        : await apiPostJson('/api/b/followup/templates', payload)
      selectedTemplateId.value = saved.id
      await loadAll()
      fillTemplateForm(selectedTemplate.value)
      showToast('模板已保存')
    } catch (e) {
      error.value = e?.message || '模板保存失败'
    } finally {
      saving.value = false
    }
  }

  async function copyTemplate(tpl) {
    if (!tpl?.id) return
    const payload = {
      name: `${tpl.name} 副本`,
      description: tpl.description,
      nodule_type: tpl.nodule_type,
      risk_level: tpl.risk_level,
      cycle_days: tpl.cycle_days,
      default_channel: tpl.default_channel,
      default_reminder_strategy: tpl.default_reminder_strategy,
      status: 'draft',
      nodes: (tpl.nodes || []).map(node => ({
        node_code: `${node.node_code || 'NODE'}_COPY`,
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
        sort_order: node.sort_order || 0
      }))
    }
    const saved = await apiPostJson('/api/b/followup/templates', payload)
    selectedTemplateId.value = saved.id
    await loadAll()
    fillTemplateForm(selectedTemplate.value)
    showToast('模板已复制为草稿')
  }

  async function archiveTemplate(tpl) {
    if (!tpl?.id) return
    const nextStatus = tpl.status === 'archived' ? 'draft' : 'archived'
    await apiJson(`/api/b/followup/templates/${tpl.id}`, {
      method: 'PUT',
      body: JSON.stringify({ status: nextStatus })
    })
    await loadAll()
    fillTemplateForm(selectedTemplate.value)
    showToast(nextStatus === 'archived' ? '模板已归档' : '模板已恢复为草稿')
  }

  async function deleteTemplate(tpl) {
    if (!tpl?.id) return
    if (!window.confirm(`确认删除模板「${tpl.name}」？已被患者计划引用的模板会删除失败，可改为归档。`)) return
    try {
      await apiJson(`/api/b/followup/templates/${tpl.id}`, { method: 'DELETE' })
      if (selectedTemplateId.value === tpl.id) selectedTemplateId.value = null
      await loadAll()
      fillTemplateForm(selectedTemplate.value)
      showToast('模板已删除')
    } catch (e) {
      error.value = e?.message || '模板删除失败，可先归档'
    }
  }

  return {
    archiveTemplate,
    copyTemplate,
    createTemplate,
    deleteTemplate,
    fillTemplateForm,
    getTemplateIssues,
    saveTemplate,
    saving,
    selectTemplate,
    templateForm,
    validateTemplate,
  }
}
