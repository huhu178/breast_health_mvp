import { computed, ref } from 'vue'

const KB_DEFAULT_ITEMS = [
  { key: 'breakfast', label: '早餐建议' },
  { key: 'lunch', label: '午餐建议' },
  { key: 'dinner', label: '晚餐建议' },
  { key: 'knowledgeCard', label: '知识卡' },
  { key: 'medication', label: '用药/禁忌提醒' },
  { key: 'sport', label: '运动处方' },
  { key: 'psych', label: '心理干预' },
  { key: 'questionnaire', label: '随访问卷' },
  { key: 'reminderScript', label: '提醒话术' },
  { key: 'escalationRule', label: '异常转人工规则' },
]

export function useFollowupContent({
  activeAssistant,
  currentAssistant,
  currentPlanRows,
  followPatient,
  followupKnowledgeItems,
  isCheckupScenario,
  planDay,
}) {
  const draft = ref({
    cycle: '6个月',
    channel: '企微/电话/小程序',
    reminder: '到期前3天提醒',
    kbEnabled: {
      breakfast: true,
      lunch: true,
      dinner: true,
      knowledgeCard: true,
      medication: true,
      sport: true,
      psych: true,
      questionnaire: false,
      reminderScript: true,
      escalationRule: true,
    },
    kbOverrides: {},
    kbCustom: [],
    note: '',
  })

  function pickFirst(prefix) {
    const hit = currentPlanRows.value.find((row) => {
      const summary = String(row?.summary ?? '').trim()
      return summary === prefix || summary.includes(prefix)
    })
    if (!hit) return ''
    const summary = String(hit.summary ?? '').trim()
    const remind = String(hit.remind ?? '').trim()
    const text = (summary === prefix || summary.length <= 3) ? remind : (remind ? `${summary}\n${remind}` : summary)
    return text.split('\n').map((line) => line.trim()).filter(Boolean)[0] || text
  }

  const planQuick = computed(() => ({
    sport: pickFirst('运动'),
    psych: pickFirst('心理'),
  }))

  function pickRowLike(query) {
    const key = String(query || '').trim()
    if (!key) return null
    return currentPlanRows.value.find((row) => String(row?.summary ?? '').includes(key)) || null
  }

  function pickRowText(query) {
    const hit = pickRowLike(query)
    if (!hit) return ''
    const summary = String(hit.summary ?? '').trim()
    const remind = String(hit.remind ?? '').trim()
    if (remind && (summary === query || summary.length <= 6)) return remind
    return remind ? `${summary}\n${remind}` : summary
  }

  function pickIntro() {
    const first = currentPlanRows.value.find((row) => !String(row?.time ?? '').trim()) || currentPlanRows.value[0]
    const summary = String(first?.summary ?? '').trim()
    const remind = String(first?.remind ?? '').trim()
    return remind ? `${summary}\n${remind}`.trim() : summary
  }

  function pickMeals() {
    return {
      breakfast: pickRowText('早餐打卡跟进'),
      lunch: pickRowText('午餐打卡跟进'),
      dinner: pickRowText('晚餐打卡跟进'),
    }
  }

  function pickKnowledge() {
    return pickRowText('知识卡')
  }

  function pickSport() {
    return pickRowText('运动')
  }

  function pickPsych() {
    return pickRowText('心理')
  }

  function pickCautions() {
    const text = pickKnowledge()
    if (!text) return ''
    const lines = text.split('\n').map((line) => line.trim()).filter(Boolean)
    const hit = lines.filter((line) => /^注意|^避免|^提示|^推荐|^空腹服药/.test(line)).slice(0, 6)
    return hit.join('\n') || lines.slice(0, 4).join('\n')
  }

  function getKbText(key) {
    const override = String(draft.value.kbOverrides?.[key] || '').trim()
    if (override) return override

    const meals = pickMeals()
    const knowledge = pickKnowledge()
    const sport = pickSport()
    const psych = pickPsych()
    const cautions = pickCautions()

    if (key === 'breakfast') return meals.breakfast || ''
    if (key === 'lunch') return meals.lunch || ''
    if (key === 'dinner') return meals.dinner || ''
    if (key === 'knowledgeCard') return knowledge || ''
    if (key === 'medication') return cautions || knowledge || ''
    if (key === 'sport') return sport || ''
    if (key === 'psych') return psych || ''
    if (key === 'questionnaire') return [
      '1）今天是否有持续咳嗽/胸闷/气短？（无/轻/中/重）',
      '2）是否有吞咽不适/声音嘶哑/颈部压迫感？（无/有）',
      '3）睡眠与情绪状态如何？（良好/一般/较差）',
      '4）是否按计划完成运动与饮食？（是/否）',
    ].join('\n')
    if (key === 'reminderScript') return [
      `您好，已为您更新 Day ${planDay.value.replace('day', '')} 健康管理任务。`,
      `请按“${draft.value.cycle}复查周期”执行，并完成饮食/运动/心理打卡。`,
      '如出现持续咳嗽、胸痛、咳血、明显吞咽困难等情况，请及时就医并联系医生。',
    ].join('\n')
    if (key === 'escalationRule') return [
      '异常转人工/医生规则：',
      '- 出现咳血/胸痛/呼吸困难/持续发热 → 立即转医生',
      '- 出现声音嘶哑加重/吞咽困难 → 48小时内转医生评估',
      '- 连续 3 天未打卡或失联 → 转人工电话随访',
    ].join('\n')
    return ''
  }

  function setKbEnabled(key, value) {
    draft.value.kbEnabled = draft.value.kbEnabled || {}
    draft.value.kbEnabled[key] = !!value
  }

  function setCustomEnabled(key, value) {
    draft.value.kbCustom = Array.isArray(draft.value.kbCustom) ? draft.value.kbCustom : []
    const hit = draft.value.kbCustom.find((item) => item.key === key)
    if (hit) hit.enabled = !!value
  }

  const kbItems = computed(() => {
    const base = KB_DEFAULT_ITEMS.map((item) => ({
      key: item.key,
      label: item.label,
      enabled: !!draft.value.kbEnabled?.[item.key],
      text: getKbText(item.key),
      isCustom: false,
    }))
    const custom = (draft.value.kbCustom || []).map((item) => ({
      key: item.key,
      label: item.label || '自定义条目',
      enabled: !!item.enabled,
      text: String(item.text || '').trim(),
      isCustom: true,
    }))
    const backend = (followupKnowledgeItems.value || []).map((item) => ({
      key: `api_${item.id}`,
      apiId: item.id,
      label: item.title,
      enabled: true,
      text: item.content,
      isCustom: true,
      category: item.category,
      taskType: item.task_type,
    }))
    return [...backend, ...base, ...custom]
  })

  const kbSelected = computed(() => kbItems.value.filter((item) => item.enabled))

  const assistantPlanPanels = computed(() => {
    const meals = pickMeals()
    const intro = pickIntro()
    const knowledge = pickKnowledge()
    const sport = pickSport()
    const psych = pickPsych()
    const cautions = pickCautions()
    const mk = (key, name, ico, bg, color, summary, sections) => ({ key, name, ico, bg, color, summary, sections })

    return [
      mk('hlp', '名医分身', '名', '#eef5ff', '#155eef', '知识卡/重点提示', [
        { h: '知识卡（重点）', p: knowledge || '—' },
        { h: '注意事项', p: cautions || '—' },
      ]),
      mk('health', '健康管理', '健', '#ecfff3', '#16a34a', '三餐+健康习惯', [
        { h: '早餐', p: meals.breakfast || '—' },
        { h: '午餐', p: meals.lunch || '—' },
        { h: '晚餐', p: meals.dinner || '—' },
        { h: '今日提醒', p: cautions || '—' },
      ]),
      mk('pharma', 'AI药师', '药', '#fff7ed', '#f97316', '用药/禁忌提醒', [
        { h: '用药与禁忌（从知识卡提取）', p: cautions || knowledge || '—' },
      ]),
      mk('chronic', '慢病管理', '慢', '#f5f3ff', '#8b5cf6', '运动+代谢管理', [
        { h: '运动处方', p: sport || '—' },
        { h: '饮食与代谢提示', p: cautions || '—' },
      ]),
      mk('psych', '心理咨询', '心', '#fff1f2', '#ef4444', '心理干预', [
        { h: '心理练习', p: psych || '—' },
      ]),
      mk('rehab', '运动康复', '动', '#ecfff3', '#16a34a', '运动训练', [
        { h: '今日运动', p: sport || '—' },
      ]),
      mk('lifestyle', '生活规划', '活', '#fffbeb', '#d97706', '今日目标+习惯', [
        { h: '今日目标', p: intro || '—' },
        { h: '习惯提醒', p: cautions || '—' },
      ]),
      mk('tcm', '中医药膳', '膳', '#f5f0ff', '#8b5cf6', '中医调理要点', [
        { h: '调理思路', p: intro || '—' },
        { h: '药膳/饮食建议', p: meals.breakfast || meals.dinner || '—' },
      ]),
      mk('welfare', '健康福利', '福', '#ecfdf5', '#16a34a', '提醒与权益', [
        { h: '随访提醒', p: `已为您生成 Day ${planDay.value.replace('day','')} 随访内容，可按计划执行并打卡。` },
        { h: '关键提醒', p: cautions || '—' },
      ]),
    ]
  })

  const activeAssistantPlan = computed(() => {
    const key = activeAssistant.value
    return (assistantPlanPanels.value || []).find((panel) => panel.key === key) || null
  })

  const followPatientPlanTask = computed(() => followPatient.value?.planTask || null)

  const followContentConfigRows = computed(() => {
    const task = followPatientPlanTask.value
    const kb = task?.kb || {}
    if (isCheckupScenario.value) {
      return [
        { key: 'knowledgeCard', label: '体检报告解读卡', reason: kb.knowledgeCard ? '来自已保存任务' : '基于异常项与风险等级推荐', enabled: !!kb.knowledgeCard || !!draft.value.kbEnabled?.knowledgeCard },
        { key: 'sport', label: '生活方式干预建议', reason: kb.sport ? '来自方案组合' : '可作为检后改善模块加入', enabled: !!kb.sport || !!draft.value.kbEnabled?.sport },
        { key: 'questionnaire', label: '复查前症状自评', reason: kb.questionnaire ? '来自问卷库' : '用于判断是否需要提前就医', enabled: !!kb.questionnaire || !!draft.value.kbEnabled?.questionnaire },
        { key: 'reminderScript', label: '复查预约提醒', reason: kb.reminderScript ? '来自提醒话术模板' : '用于提升复查到检率', enabled: !!kb.reminderScript || !!draft.value.kbEnabled?.reminderScript },
      ]
    }
    return [
      { key: 'knowledgeCard', label: '低碘饮食指导', reason: kb.knowledgeCard ? '来自已保存任务' : '基于病种与阶段推荐', enabled: !!kb.knowledgeCard || !!draft.value.kbEnabled?.knowledgeCard },
      { key: 'sport', label: '术后/日常运动提醒', reason: kb.sport ? '来自方案组合' : '可作为生活方式模块加入', enabled: !!kb.sport || !!draft.value.kbEnabled?.sport },
      { key: 'questionnaire', label: '症状自评问卷', reason: kb.questionnaire ? '来自问卷库' : 'Day1 建议加入基线症状评估', enabled: !!kb.questionnaire || !!draft.value.kbEnabled?.questionnaire },
      { key: 'reminderScript', label: '晚间打卡提醒', reason: kb.reminderScript ? '来自提醒话术模板' : '用于提升依从性', enabled: !!kb.reminderScript || !!draft.value.kbEnabled?.reminderScript },
    ]
  })

  const followGeneratedRows = computed(() => {
    const task = followPatientPlanTask.value
    const kb = task?.kb || {}
    const rows = isCheckupScenario.value
      ? [
        { key: 'summary', name: '体检摘要消息', type: '摘要卡', source: '系统生成', assistant: currentAssistant.value?.shortName || '总检解读', enabled: true },
        { key: 'knowledgeCard', name: 'Day1解读卡：体检异常项说明', type: '解读卡', source: kb.knowledgeCard ? '体检中心标准版 v2.1' : '体检知识库', assistant: '总检解读', enabled: !!kb.knowledgeCard || !!draft.value.kbEnabled?.knowledgeCard },
        { key: 'questionnaire', name: '复查前症状自评', type: '任务卡', source: '问卷库 v2.0', assistant: '检后管理', enabled: !!kb.questionnaire || !!draft.value.kbEnabled?.questionnaire },
        { key: 'reminderScript', name: '复查预约提醒', type: '提醒卡', source: '体检中心模板', assistant: '复查预约', enabled: !!kb.reminderScript || !!draft.value.kbEnabled?.reminderScript },
      ]
      : [
        { key: 'summary', name: '摘要消息', type: '摘要卡', source: '系统生成', assistant: currentAssistant.value?.shortName || '名医分身', enabled: true },
        { key: 'knowledgeCard', name: 'Day1知识卡：低碘饮食指导', type: '知识卡', source: kb.knowledgeCard ? '院内标准版 v2.1' : '院内指南', assistant: '名医分身', enabled: !!kb.knowledgeCard || !!draft.value.kbEnabled?.knowledgeCard },
        { key: 'questionnaire', name: '症状自评问卷', type: '任务卡', source: '问卷库 v2.0', assistant: '健康管理师', enabled: !!kb.questionnaire || !!draft.value.kbEnabled?.questionnaire },
        { key: 'reminderScript', name: '晚间打卡提醒', type: '提醒卡', source: '系统模板', assistant: '健康管理师', enabled: !!kb.reminderScript || !!draft.value.kbEnabled?.reminderScript },
      ]
    return rows.filter((row) => row.enabled)
  })

  const simulatedAssistantChat = computed(() => {
    const assistant = currentAssistant.value
    const plan = activeAssistantPlan.value
    const task = followPatientPlanTask.value
    const dayNum = String(task?.day || planDay.value).replace('day', '')
    const patientName = followPatient.value?.name || '您'
    const assistantName = assistant?.name || 'AI助手'

    if (task?.kb) {
      const kb = task.kb || {}
      const firstText = String(kb.knowledgeCard || kb.reminderScript || kb.sport || kb.psych || '').split('\n').map((line) => line.trim()).filter(Boolean)[0]
      return [
        { from: 'ai', text: `您好，${patientName}。我是${assistantName}，已根据您的任务计划生成 Day ${dayNum} 内容。` },
        ...(firstText ? [{ from: 'ai', text: `摘要：${firstText}` }] : []),
        { type: 'card', ico: '任', title: `Day ${dayNum} 健康管理任务`, sub: `${task.channel || draft.value.channel} · ${task.cycle || draft.value.cycle} · 已配置内容包` },
        { type: 'card', ico: '问', title: '症状自评与打卡', sub: kb.questionnaire ? '问卷已加入 · 点击填写' : '饮食/运动/心理打卡入口' },
        { from: 'ai', text: kb.reminderScript ? String(kb.reminderScript).split('\n')[0] : '请按计划完成今日打卡，如有明显不适请及时联系医生。' },
      ]
    }

    if (!plan) {
      return [
        { from: 'ai', text: `您好，我是${assistantName}，将为您提供随访支持。` },
        { from: 'ai', text: `当前 Day ${dayNum} 暂无可展示内容。` },
      ]
    }

    const sections = Array.isArray(plan.sections) ? plan.sections : []
    const firstSec = sections.find((section) => String(section?.p || '').trim()) || sections[0]
    const firstText = String(firstSec?.p || '').trim().split('\n').map((line) => line.trim()).filter(Boolean)[0] || ''

    return [
      { from: 'ai', text: `您好，${patientName}。我是${assistantName}，已为您生成 Day ${dayNum} 的任务内容摘要。` },
      ...(firstText ? [{ from: 'ai', text: `摘要：${firstText}` }] : []),
      { type: 'card', ico: '🧾', title: `查看并填写健康管理任务（Day ${dayNum}）`, sub: `${plan.name} · 点击在右侧完成下发` },
      { from: 'ai', text: '提示：内容较长已折叠，请在右侧表单中选择知识库条目并保存。' },
    ]
  })

  return {
    draft,
    followContentConfigRows,
    followGeneratedRows,
    getKbText,
    pickIntro,
    planQuick,
    setKbEnabled,
    simulatedAssistantChat,
  }
}
