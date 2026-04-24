export const kpis = {
  analytics: [
    { label: '患者总数', value: '12,486', delta: '较昨日 +128', tone: 'blue', icon: 'users' },
    { label: '高风险患者', value: '1,268', delta: '较昨日 +23', tone: 'orange', icon: 'shield' },
    { label: '待处理报告', value: '146', delta: '较昨日 -12', tone: 'blue', icon: 'file' },
    { label: '待医生复核', value: '82', delta: '较昨日 -5', tone: 'green', icon: 'check' },
    { label: '待推送患者', value: '95', delta: '较昨日 +7', tone: 'purple', icon: 'send' },
    { label: '随访完成率', value: '78.6%', delta: '较昨日 +1.8%', tone: 'cyan', icon: 'clock' }
  ]
}

export const patientQueue = [
  {
    id: 'p1',
    name: '张*国',
    gender: '男',
    age: 56,
    phone: '138****5678',
    source: '门诊',
    nodule: '肺部结节',
    risk: '高风险',
    stage: '待处理报告',
    lastExam: '胸部CT',
    next: '今天 15:30',
    owner: '健康管理师',
    wecom: { sent: true, read: false, replied: false },
    reportSummary: '胸部CT提示右上肺磨玻璃结节 8mm；建议进一步随访复查。'
  },
  {
    id: 'p2',
    name: '李*婷',
    gender: '女',
    age: 48,
    phone: '139****2468',
    source: '体检中心',
    nodule: '甲状腺结节',
    risk: '中风险',
    stage: '待医生复核',
    lastExam: '甲状腺超声',
    next: '今天 16:00',
    owner: '李医生',
    wecom: { sent: true, read: true, replied: true },
    reportSummary: 'TI-RADS 3 类，建议结合既往检查随访。'
  },
  {
    id: 'p3',
    name: '王*梅',
    gender: '女',
    age: 62,
    phone: '137****1357',
    source: '门诊',
    nodule: '乳腺结节 / 甲状腺结节',
    risk: '中风险',
    stage: '待推送患者',
    lastExam: '乳腺超声',
    next: '2026-07-01',
    owner: '赵医生',
    wecom: { sent: false, read: false, replied: false },
    reportSummary: 'BI-RADS 3 类，建议 6 个月复查。'
  }
]

export const messageThreads = [
  {
    id: 't1',
    patientId: 'p1',
    channel: '企微',
    title: '随访提醒 · 张*国',
    lastAt: '09:12',
    unread: 2,
    messages: [
      { from: '系统', at: '08:50', text: '已发送复查提醒与随访问卷。' },
      { from: '患者', at: '09:05', text: '最近有点咳嗽，需要马上去医院吗？' },
      { from: '健康管理师', at: '09:12', text: '先确认是否有咳血/胸痛/持续发热等情况；如有请立即就医。' }
    ]
  }
]

export const aiWorkspace = {
  summary: [
    { k: '风险分层', v: '高风险（建议 3 个月复查）' },
    { k: '关键字段', v: '磨玻璃结节 8mm / 右上肺' },
    { k: '下一步', v: '医生复核 → 允许推送 → 生成随访任务' }
  ],
  draft: {
    title: '健康管理报告草稿（示意）',
    bullets: [
      '解释：本次影像提示右上肺磨玻璃结节 8mm，需按时复查。',
      '建议：3 个月内复查胸部CT；如有异常症状提前就诊。',
      '触达：小程序推送复查提醒 + 企微随访问卷 + 电话确认。'
    ]
  },
  actions: [
    { label: '一键生成报告', primary: true },
    { label: '生成企微话术' },
    { label: '生成随访问卷' }
  ]
}

