import { computed } from 'vue'

const MOCK_TRACKING_NODES = [
  {
    name: '早餐打卡',
    send_time: '07:00',
    task_type: 'diet_checkin',
    patient_action: 'upload_image',
    ai_action: 'diet_review',
    message_template: '早上好，请上传今天早餐图片。系统会从主食、蛋白质、蔬菜和油脂搭配角度给出饮食建议。',
  },
  {
    name: '午餐打卡',
    send_time: '11:00',
    task_type: 'diet_checkin',
    patient_action: 'upload_image',
    ai_action: 'diet_review',
    message_template: '午餐前后请上传餐食图片，便于记录今天的饮食结构，并获得下一餐调整建议。',
  },
  {
    name: '知识推送',
    send_time: '12:30',
    task_type: 'knowledge_push',
    patient_action: 'read',
    ai_action: 'send_message',
    message_template: '今天的健康知识：甲状腺结节和肺结节管理重点是规律复查、稳定作息、减少焦虑，并持续记录身体变化。',
  },
  {
    name: '晚餐打卡',
    send_time: '17:30',
    task_type: 'diet_checkin',
    patient_action: 'upload_image',
    ai_action: 'diet_review',
    message_template: '请上传今天晚餐图片。建议晚餐清淡、不过量，注意优质蛋白和蔬菜搭配。',
  },
  {
    name: '运动提醒',
    send_time: '19:00',
    task_type: 'exercise_reminder',
    patient_action: 'reply_text',
    ai_action: 'none',
    message_template: '今天建议完成20-30分钟低到中等强度活动，如散步、拉伸或八段锦。量力而行，贵在坚持。',
  },
  {
    name: '心理提醒',
    send_time: '20:00',
    task_type: 'psych_reminder',
    patient_action: 'reply_text',
    ai_action: 'reply',
    message_template: '睡前可以做3分钟呼吸放松，记录今天的压力和睡眠准备情况。若持续焦虑或失眠，可以回复说明。',
  },
]

export function patientActionLabel(action) {
  const map = {
    none: '无需患者操作',
    read: '患者阅读',
    checkin: '患者打卡',
    fill_form: '填写表单',
    upload_image: '上传餐饮图片',
    upload_report: '上传报告',
    reply: '患者回复',
    reply_text: '文字回复',
    confirm: '患者确认',
  }
  return map[action] || action || '无需患者操作'
}

export function aiActionLabel(action) {
  const map = {
    none: '无自动处理',
    send_message: '自动发送提醒',
    reply: '自动回复',
    analyze_image: '自动分析图片',
    image_recognition: '图片识别',
    diet_review: '饮食点评',
    summarize: '自动汇总',
    alert: '异常提醒',
    route_manual: '转人工处理',
  }
  return map[action] || action || '无自动处理'
}

export function trackingStatusLabel(status) {
  const map = {
    draft: '待创建',
    assigned: '待发送',
    scheduled: '待发送',
    pending: '待发送',
    sent: '已发送',
    replied: '患者已回复',
    executing: '执行中',
    review: '待复核',
    completed: '已完成',
    done: '已完成',
    alert: '异常待处理',
    manual_processing: '人工处理中',
    failed: '发送失败',
    cancelled: '已取消',
  }
  return map[status] || '待发送'
}

export function taskStatusLabel(status) {
  if (status === 'draft') return '待分派'
  if (status === 'done') return '已完成'
  return '待执行'
}

function trackingEventTitle(action) {
  const text = String(action || '')
  const map = {
    task_created_from_patient_plan: '任务已创建',
    message_sent: '消息已发送',
    message_failed: '发送失败',
    wecom_message_received: '收到患者消息',
    checkin_submitted: '患者已打卡',
    task_completed: '任务已完成',
  }
  return map[text] || text.replace(/_/g, ' ') || '任务状态更新'
}

export function usePatientTracking({ followPatient, followTasks, activeTaskId, planDay }) {
  function previewTasksFromPatient(patient) {
    if (!patient) return []
    const nodes = (patient.planTask?.nodes || []).length ? patient.planTask.nodes : MOCK_TRACKING_NODES
    const day = patient.planTask?.day || planDay.value || 'day1'
    return nodes.slice(0, 6).map((node, idx) => {
      const message = node.message_template || '请按计划完成今日健康管理任务。'
      return {
        id: `preview-${patient.id}-${String(day).replace('day', '')}-${idx}`,
        patientId: patient.id,
        patientName: patient.name,
        gender: patient.gender,
        age: patient.age,
        phoneMasked: patient.phoneMasked,
        nodules: patient.nodules,
        risk: patient.risk,
        riskTone: patient.riskTone,
        owner: patient.owner || '',
        channel: patient.planTask?.channel || '企微',
        cycle: patient.planTask?.cycle || '90天',
        reminder: patient.planTask?.reminder || '',
        day,
        time: node.send_time || '09:00',
        scheduledAt: '模拟排程',
        status: idx === 0 ? 'scheduled' : 'pending',
        node,
        message,
        patientAction: patientActionLabel(node.patient_action),
        aiAction: aiActionLabel(node.ai_action),
        logs: [{ at: '模拟', by: '系统', action: 'task_created_from_patient_plan', note: '模拟展示：真实企微接入后会写入实际发送与回调记录。' }],
      }
    })
  }

  const trackingTasksForPatient = computed(() => {
    const patient = followPatient.value
    if (!patient) return []
    const tasks = (followTasks.value || []).filter((task) => String(task.patientId) === String(patient.id))
    if (!tasks.length) return previewTasksFromPatient(patient)
    if (tasks.length === 1 && !tasks[0].node?.message_template && !tasks[0].message) return previewTasksFromPatient(patient)
    return tasks
  })

  const activeTrackingTask = computed(() => {
    const current = trackingTasksForPatient.value.find((task) => task.id === activeTaskId.value) || trackingTasksForPatient.value[0] || null
    if (!current) return null
    const node = current.node || current.taskPayload?.node || {}
    const message = current.message || node.message_template || ''
    return {
      ...current,
      dayNum: Number(String(current.day || 'day1').replace('day', '')) || 1,
      time: current.time || current.scheduledAt?.slice(11, 16) || node.send_time || '09:00',
      title: current.title || node.name || '健康管理任务',
      message,
      messageBrief: current.messageBrief || String(message || '暂无推送内容').replace(/\s+/g, ' ').slice(0, 48),
      patientAction: current.patientAction || patientActionLabel(node.patient_action),
      aiAction: current.aiAction || aiActionLabel(node.ai_action),
    }
  })

  const trackingTaskGroups = computed(() => {
    const groups = new Map()
    trackingTasksForPatient.value.forEach((task) => {
      const day = Number(String(task.day || 'day1').replace('day', '')) || 1
      if (!groups.has(day)) groups.set(day, [])
      const node = task.node || task.taskPayload?.node || {}
      const message = task.message || node.message_template || ''
      groups.get(day).push({
        ...task,
        dayNum: day,
        time: task.time || task.scheduledAt?.slice(11, 16) || node.send_time || '09:00',
        messageBrief: String(message || '暂无推送内容').replace(/\s+/g, ' ').slice(0, 48),
      })
    })
    return Array.from(groups.entries())
      .sort((a, b) => a[0] - b[0])
      .slice(0, 7)
      .map(([day, tasks]) => ({
        day,
        tasks: tasks.sort((a, b) => String(a.time).localeCompare(String(b.time))),
      }))
  })

  const trackingStats = computed(() => {
    const list = trackingTasksForPatient.value
    return {
      total: list.length,
      waiting: list.filter((task) => ['draft', 'assigned', 'scheduled', 'pending'].includes(task.status)).length,
      running: list.filter((task) => ['sent', 'replied', 'executing', 'review'].includes(task.status)).length,
      alert: list.filter((task) => ['alert', 'manual_processing', 'failed'].includes(task.status)).length,
    }
  })

  const activeTrackingEvents = computed(() => {
    const task = activeTrackingTask.value
    if (!task) return []
    const logs = Array.isArray(task.logs) ? task.logs : []
    const base = logs.map((log, idx) => ({
      key: `log-${idx}`,
      title: trackingEventTitle(log.action),
      time: log.at || '现在',
      note: log.note || '任务状态已更新',
    }))
    if (!base.length) {
      base.push({
        key: 'created',
        title: '任务已创建',
        time: task.createdAt || '现在',
        note: '系统已根据随访模板生成该任务，等待到达计划发送时间。',
      })
    }
    if (['sent', 'replied', 'done', 'completed'].includes(task.status)) {
      base.push({ key: 'sent', title: '消息已发送', time: task.sentAt || '模拟时间', note: '企业微信发送结果会在接入真实接口后写入这里。' })
    }
    return base
  })

  const activeTrackingMessages = computed(() => {
    const task = activeTrackingTask.value
    if (!task) return []
    const messages = Array.isArray(task.messages) ? task.messages : []
    if (messages.length) {
      return messages.map((msg, idx) => ({
        key: `msg-${idx}`,
        direction: msg.direction === 'inbound' ? 'inbound' : 'outbound',
        sender: msg.direction === 'inbound' ? '患者' : '健康管理师',
        type: msg.content_type || 'text',
        content: msg.content || '',
      }))
    }
    const needsImage = String(task.patientAction || '').includes('上传餐饮图片')
    const needsAiReview = String(task.aiAction || '').includes('饮食点评')
    return [
      { key: 'preview-1', direction: 'outbound', sender: '健康管理师', type: 'text', content: task.message || '暂无推送内容' },
      ...(needsImage ? [{ key: 'preview-2', direction: 'inbound', sender: '患者', type: 'image', content: '患者上传后显示真实图片' }] : []),
      ...(needsAiReview ? [{ key: 'preview-3', direction: 'outbound', sender: 'AI饮食点评', type: 'text', content: '图片识别完成后，这里会显示AI饮食点评和下一餐建议。' }] : []),
      ...(!needsImage && ['replied', 'done', 'completed'].includes(task.status) ? [{ key: 'preview-4', direction: 'inbound', sender: '患者', type: 'text', content: '患者回复内容会显示在这里。' }] : []),
    ]
  })

  return {
    activeTrackingEvents,
    activeTrackingMessages,
    activeTrackingTask,
    previewTasksFromPatient,
    trackingStats,
    trackingTaskGroups,
    trackingTasksForPatient,
  }
}
