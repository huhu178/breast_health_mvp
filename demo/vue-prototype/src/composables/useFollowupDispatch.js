import { computed, ref } from 'vue'

function cycleDaysFromLabel(cycle) {
  if (String(cycle || '').includes('3')) return 90
  if (String(cycle || '').includes('6')) return 180
  return 365
}

function channelToBackend(channel) {
  const text = String(channel || '')
  if (text.includes('企微')) return 'wecom'
  if (text.includes('电话')) return 'phone'
  if (text.includes('小程序')) return 'miniapp'
  return 'wecom'
}

export function useFollowupDispatch({
  activePatient,
  activePlanNodes,
  apiPostJson,
  channelLabel,
  cycleLabelFromDays,
  draft,
  followPatientId,
  followTasks,
  followupRecommendation,
  followupTemplates,
  getKbText,
  makeTaskFromPatient,
  normalizeBackendTask,
  pickIntro,
  planDay,
  planQuick,
  planState,
  selectTask,
  selectedFollowupTemplateId,
  selectedWorkflowTemplate,
  setSubTab,
  statusKey,
  toast,
}) {
  const followupPlanSaving = ref(false)

  function savePlanForActive() {
    const p = activePatient.value
    if (!p) return
    p.plan = {
      title: planState.value.title || '甲状腺结节合并肺结节健康管理方案（含心理）',
      day: planDay.value,
      sport: planQuick.value.sport,
      psych: planQuick.value.psych,
    }
    p.timeline = Array.isArray(p.timeline) ? p.timeline : []
    p.timeline.push({ at: '现在', tone: 'b', text: `更新任务计划：Day ${planDay.value.replace('day', '')}`, meta: '已保存' })
  }

  function applyDraftToPlan() {
    const p = activePatient.value
    if (!p) return
    const enabledKeys = Object.entries(draft.value.kbEnabled || {})
      .filter(([, v]) => !!v)
      .map(([k]) => k)

    const customEnabled = (draft.value.kbCustom || []).filter((x) => !!x.enabled)

    p.planTask = {
      day: planDay.value,
      cycle: draft.value.cycle,
      channel: draft.value.channel,
      reminder: draft.value.reminder,
      kb: {
        breakfast: enabledKeys.includes('breakfast') ? getKbText('breakfast') : null,
        lunch: enabledKeys.includes('lunch') ? getKbText('lunch') : null,
        dinner: enabledKeys.includes('dinner') ? getKbText('dinner') : null,
        knowledgeCard: enabledKeys.includes('knowledgeCard') ? getKbText('knowledgeCard') : null,
        medication: enabledKeys.includes('medication') ? getKbText('medication') : null,
        sport: enabledKeys.includes('sport') ? getKbText('sport') : null,
        psych: enabledKeys.includes('psych') ? getKbText('psych') : null,
        questionnaire: enabledKeys.includes('questionnaire') ? getKbText('questionnaire') : null,
        reminderScript: enabledKeys.includes('reminderScript') ? getKbText('reminderScript') : null,
        escalationRule: enabledKeys.includes('escalationRule') ? getKbText('escalationRule') : null,
        custom: customEnabled.map((x) => ({ key: x.key, label: x.label, text: String(x.text || '').trim() })),
        goal: pickIntro() || null,
      },
      note: draft.value.note
    }
    savePlanForActive()
    p.timeline = Array.isArray(p.timeline) ? p.timeline : []
    p.timeline.push({ at: '现在', tone: 'b', text: `生成健康管理任务：Day ${planDay.value.replace('day','')}`, meta: '已保存' })

    const newTask = makeTaskFromPatient(p)
    followTasks.value = [newTask, ...(followTasks.value || [])]
    selectTask(newTask.id)
  }

  async function ensureFollowupRecommendation(p) {
    const patient = p || activePatient.value
    if (!patient?._apiId) return null
    const rec = await apiPostJson('/api/b/followup/plans/recommend', {
      patient_id: patient._apiId,
      record_id: patient.workspaceRecordId || patient.latestRecordId || null,
      report_id: patient.latestReport?.id || patient.latestReportId || null,
      nodule_type: patient.noduleType,
      risk_level: patient.risk,
    })
    followupRecommendation.value = rec
    if (rec?.template?.id) selectedFollowupTemplateId.value = rec.template.id
    if (rec?.settings) {
      draft.value.cycle = cycleLabelFromDays(rec.settings.cycle_days)
      draft.value.channel = rec.settings.channel === 'wecom' ? '企微' : rec.settings.channel === 'phone' ? '电话' : rec.settings.channel === 'miniapp' ? '小程序' : draft.value.channel
      draft.value.reminder = rec.settings.reminder_strategy || draft.value.reminder
    }
    if (rec?.nodes?.length) {
      const firstNode = rec.nodes[0]
      if (firstNode?.day_offset) planDay.value = `day${firstNode.day_offset}`
      draft.value.kbCustom = rec.nodes.flatMap((node) => (node.matched_knowledge || []).map((item) => ({
        key: `api_${item.id}`,
        label: item.title,
        text: item.content,
        enabled: true,
      })))
    }
    return rec
  }

  async function recommendForActive() {
    const p = activePatient.value
    if (!p?._apiId) {
      toast?.show('演示患者已使用本地知识库推荐')
      return
    }
    try {
      await ensureFollowupRecommendation(p)
      toast?.show('已按患者画像匹配任务模板和知识库内容')
    } catch (e) {
      toast?.show(e.message || '任务模板推荐失败')
    }
  }

  async function saveBackendPatientPlan(p) {
    const patient = p || activePatient.value
    if (!patient?._apiId) return null
    followupPlanSaving.value = true
    try {
      const rec = followupRecommendation.value || await ensureFollowupRecommendation(patient)
      const template = selectedWorkflowTemplate.value || rec?.template || followupTemplates.value[0] || null
      const templateId = template?.id
      const nodes = template?.nodes || rec?.nodes || []
      const selectedKnowledgeIds = [
        ...(rec?.knowledge || []).map(item => item.id),
        ...(nodes || []).flatMap(node => node.knowledge_item_ids || [])
      ].filter(Boolean)
      const plan = await apiPostJson('/api/b/followup/patient-plans', {
        patient_id: patient._apiId,
        record_id: rec?.record_id || patient.workspaceRecordId || null,
        report_id: rec?.report_id || patient.latestReport?.id || null,
        template_id: templateId,
        name: `${patient.name}健康管理任务计划`,
        nodule_type: patient.noduleType,
        risk_level: patient.risk,
        settings: {
          cycle_days: template?.cycle_days || cycleDaysFromLabel(draft.value.cycle),
          channel: template?.default_channel || channelToBackend(draft.value.channel),
          reminder_strategy: template?.default_reminder_strategy || draft.value.reminder,
        },
        plan_content: {
          template,
          nodes,
        },
        selected_knowledge_ids: Array.from(new Set(selectedKnowledgeIds)),
      })
      patient._patientPlanId = plan.id
      patient.planTask = {
        ...(patient.planTask || {}),
        backendPlanId: plan.id,
        cycle: cycleLabelFromDays(template?.cycle_days),
        channel: channelLabel(template?.default_channel),
        reminder: template?.default_reminder_strategy || draft.value.reminder,
        day: planDay.value,
        kb: patient.planTask?.kb || {},
        note: draft.value.note,
      }
      toast?.show('任务计划已保存')
      return plan
    } finally {
      followupPlanSaving.value = false
    }
  }

  function applySelectedTemplateToPatient() {
    const p = activePatient.value
    const tpl = selectedWorkflowTemplate.value
    if (!p || !tpl) return
    const firstNode = (tpl.nodes || [])[0]
    if (firstNode?.day_offset) planDay.value = `day${firstNode.day_offset}`
    p.planTask = {
      ...(p.planTask || {}),
      title: tpl.name,
      day: planDay.value,
      cycle: cycleLabelFromDays(tpl.cycle_days),
      channel: channelLabel(tpl.default_channel),
      reminder: tpl.default_reminder_strategy,
      templateId: tpl.id,
      nodes: tpl.nodes || [],
    }
    savePlanForActive()
  }

  async function simulatePlanToFollowup() {
    const p = activePatient.value
    if (!p?.id) return
    if (p._apiId) {
      try {
        applySelectedTemplateToPatient()
        const plan = p._patientPlanId ? { id: p._patientPlanId } : await saveBackendPatientPlan(p)
        const activated = await apiPostJson(`/api/b/followup/patient-plans/${plan.id}/activate`, {})
        const apiTasks = (activated?.tasks || []).map(normalizeBackendTask)
        if (apiTasks.length) {
          followTasks.value = [...apiTasks, ...(followTasks.value || [])]
          selectTask(apiTasks[0].id)
        }
        p.stage = 'follow'
        p.stageLabel = '任务执行中'
        p.serviceStatus = '任务执行中'
        p.nextStep = '按计划执行任务'
        p.timeline = Array.isArray(p.timeline) ? p.timeline : []
        p.timeline.push({ at: '现在', tone: 'g', text: '已下发健康管理任务', meta: `${apiTasks.length} 个任务` })
        followPatientId.value = p.id
        setSubTab('follow')
        toast?.show('任务已下发，已生成后续提醒/打卡任务')
        return
      } catch (e) {
        toast?.show(e.message || '随访任务下发失败')
        return
      }
    }
    applySelectedTemplateToPatient()
    const t = makeTaskFromPatient(p)
    followTasks.value = [t, ...(followTasks.value || [])]
    selectTask(t.id)
    p.stage = 'follow'
    p.stageLabel = '任务执行中'
    p.serviceStatus = '任务执行中'
    toast?.show('任务已下发')
  }

  async function savePlanForActiveAndBackend() {
    const p = activePatient.value
    if (!p) return
    applySelectedTemplateToPatient()
    if (!p._apiId) {
      toast?.show('任务计划已保存')
      return
    }
    try {
      await saveBackendPatientPlan(p)
    } catch (e) {
      toast?.show(e.message || '保存下发设置失败')
    }
  }

  const planPipelineSteps = computed(() => {
    const hasTemplate = !!selectedWorkflowTemplate.value
    const hasPreview = activePlanNodes.value.length > 0
    const hasTask = !!activePatient.value?.planTask
    const isFollow = statusKey(activePatient.value) === 'follow'
    const currentStatus = statusKey(activePatient.value)
    const hasReviewed = ['plan', 'follow', 'push', 'abnormal'].includes(currentStatus) || !!activePatient.value?.finalReport?.content || !!activePatient.value?.latestReport
    return [
      { key: 'reviewed', icon: '1', title: '报告已审核', sub: hasReviewed ? '可下发任务' : '等待审核', state: hasReviewed ? 'done' : 'todo' },
      { key: 'recommend', icon: '2', title: '推荐模板', sub: selectedWorkflowTemplate.value?.name || '待推荐', state: hasTemplate ? 'done' : 'doing' },
      { key: 'preview', icon: '3', title: '预览任务', sub: hasPreview ? `${activePlanNodes.value.length} 个节点` : '待预览', state: hasPreview ? 'done' : 'todo' },
      { key: 'confirm', icon: '4', title: '确认下发', sub: hasTask ? '已保存' : '待确认', state: hasTask ? 'done' : 'doing' },
      { key: 'track', icon: '5', title: '执行跟踪', sub: isFollow ? '查看任务' : '待生成', state: isFollow ? 'done' : 'todo' },
    ]
  })

  const planDispatchSteps = computed(() => {
    return planPipelineSteps.value.slice(1, 5).map((step, idx) => ({
      ...step,
      icon: String(idx + 1),
    }))
  })

  return {
    applyDraftToPlan,
    applySelectedTemplateToPatient,
    ensureFollowupRecommendation,
    followupPlanSaving,
    planDispatchSteps,
    planPipelineSteps,
    recommendForActive,
    saveBackendPatientPlan,
    savePlanForActive,
    savePlanForActiveAndBackend,
    simulatePlanToFollowup,
  }
}
