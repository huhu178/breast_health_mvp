export const patients = [
  {
    id: 'p1', name: '王先生', age: 58, phone: '138****4256', gender: '男',
    source: '门诊', noduleType: 'lung_thyroid', nodule: '肺部合并甲状腺结节',
    risk: 'high', stage: 'report', owner: '健康管理师',
    report: '胸部CT提示右上肺磨玻璃结节 8mm；甲状腺超声提示 TI-RADS 4A。',
    ai: 'AI已提取肺结节大小、密度、位置、甲状腺分级，并建议进入高风险随访路径。诊疗判断需医生复核。',
    next: '今天 15:30', events: ['建档完成', '问卷已回收', '影像报告待处理'],
    uploadTime: '2026-04-23 08:15', aiStatus: '解析完成',
    noduleCount: 2, maxDiameter: '8mm', density: '磨玻璃', grade: 'TI-RADS 4A',
    timeline: [
      { type: 'system', at: '08:15', text: '影像报告已上传，AI结构化解析完成。' },
      { type: 'system', at: '08:20', text: '风险分层：高风险，建议3个月复查。' },
      { type: 'patient', at: '09:05', text: '最近有点咳嗽，需要马上去医院吗？' },
      { type: 'staff', at: '09:12', from: '健康管理师', text: '先确认是否有咳血/胸痛/持续发热等情况；如有请立即就医。' }
    ]
  },
  {
    id: 'p2', name: '李女士', age: 43, phone: '136****8831', gender: '女',
    source: '体检中心', noduleType: 'breast', nodule: '乳腺结节',
    risk: 'mid', stage: 'review', owner: '医生',
    report: '乳腺超声提示 BI-RADS 3 类，建议结合既往影像随访。',
    ai: 'AI已生成健康管理报告草稿：解释报告、复查周期、生活方式建议、随访问卷。',
    next: '今天 16:00', events: ['报告已解析', '健康管理报告已生成', '等待医生复核'],
    uploadTime: '2026-04-23 08:05', aiStatus: 'AI解析中',
    noduleCount: 1, maxDiameter: '6mm', density: '实性', grade: 'BI-RADS 3',
    timeline: [
      { type: 'system', at: '08:05', text: '超声报告已上传，AI解析中。' },
      { type: 'system', at: '08:18', text: 'AI健康管理报告草稿已生成，等待医生复核。' },
      { type: 'wecom', at: '08:30', text: '企微消息已发送：请您配合完成随访问卷。' },
      { type: 'patient', at: '09:20', text: '好的，我已经填写了问卷。' }
    ]
  },
  {
    id: 'p3', name: '陈女士', age: 51, phone: '139****1902', gender: '女',
    source: '门诊', noduleType: 'lung_breast', nodule: '肺部合并乳腺结节',
    risk: 'high', stage: 'push', owner: '健康管理师',
    report: '肺部实性小结节伴乳腺结节，需医生确认复查建议后推送。',
    ai: '医生已确认报告内容，系统等待通过小程序和企微推送患者。',
    next: '今天 17:20', events: ['AI解析完成', '医生已复核', '待推送患者'],
    uploadTime: '2026-04-23 07:55', aiStatus: '待处理报告',
    noduleCount: 2, maxDiameter: '5mm', density: '实性', grade: 'BI-RADS 3',
    timeline: [
      { type: 'system', at: '07:55', text: '双部位报告已上传，AI结构化完成。' },
      { type: 'system', at: '08:10', text: '医生已复核，允许推送患者。' },
      { type: 'wecom', at: '08:15', text: '企微话术已准备，待确认推送。' }
    ]
  },
  {
    id: 'p4', name: '赵先生', age: 62, phone: '137****7719', gender: '男',
    source: '体检中心', noduleType: 'lung', nodule: '肺部结节',
    risk: 'high', stage: 'alert', owner: '医生',
    report: '患者随访反馈咳血症状，系统触发异常预警。',
    ai: 'AI仅做预警分级和材料整理，已建议立即转医生处理，不自动输出诊疗结论。',
    next: '立即处理', events: ['随访中', '患者反馈异常症状', '已触发转医生'],
    uploadTime: '2026-04-23 07:48', aiStatus: '异常报告',
    noduleCount: 1, maxDiameter: '12mm', density: '实性', grade: 'Lung-RADS 4B',
    timeline: [
      { type: 'system', at: '07:48', text: '随访问卷已发送。' },
      { type: 'patient', at: '09:30', text: '最近咳嗽有血丝，很担心。' },
      { type: 'system', at: '09:31', text: '⚠ 异常症状预警已触发，已通知医生。' },
      { type: 'staff', at: '09:35', from: '医生', text: '请立即来院就诊，我已安排优先接诊。' }
    ]
  },
  {
    id: 'p5', name: '刘女士', age: 39, phone: '135****6027', gender: '女',
    source: '门诊', noduleType: 'thyroid', nodule: '甲状腺结节',
    risk: 'low', stage: 'followup', owner: '随访护士',
    report: '甲状腺超声低风险结节，已进入定期复查提醒。',
    ai: '系统已生成90天复查提醒和企微随访问卷。',
    next: '2026-07-21', events: ['已推送患者', '随访任务已生成', '等待到期提醒'],
    uploadTime: '2026-04-22 14:30', aiStatus: '解析完成',
    noduleCount: 1, maxDiameter: '4mm', density: '囊实性', grade: 'TI-RADS 3',
    timeline: [
      { type: 'system', at: '14:30', text: '报告已推送至患者小程序。' },
      { type: 'system', at: '14:32', text: '90天复查提醒已设置，下次随访：2026-07-21。' },
      { type: 'patient', at: '15:10', text: '收到了，谢谢！' }
    ]
  },
  {
    id: 'p6', name: '周女士', age: 55, phone: '132****2811', gender: '女',
    source: '门诊', noduleType: 'triple', nodule: '三合并结节',
    risk: 'high', stage: 'review', owner: '医生',
    report: '胸部CT、甲状腺超声、乳腺超声均提示需纳入重点随访。',
    ai: 'AI已生成三合并结节管理报告草稿，包含多病种复查节奏、风险提示和患者触达话术。',
    next: '今天 18:10', events: ['三类报告已归档', 'AI生成报告草稿', '等待医生复核'],
    uploadTime: '2026-04-22 16:00', aiStatus: '解析完成',
    noduleCount: 3, maxDiameter: '9mm', density: '混合', grade: '多部位高风险',
    timeline: [
      { type: 'system', at: '16:00', text: '三类检查报告已归档，AI结构化完成。' },
      { type: 'system', at: '16:15', text: '三合并结节管理报告草稿已生成，等待医生复核。' }
    ]
  },
  {
    id: 'p7', name: '孙女士', age: 46, phone: '131****6820', gender: '女',
    source: '体检中心', noduleType: 'thyroid_breast', nodule: '甲状腺合并乳腺结节',
    risk: 'mid', stage: 'parsed', owner: '健康管理师',
    report: '甲状腺超声提示 TI-RADS 3 类；乳腺超声提示 BI-RADS 3 类，需结合既往检查随访。',
    ai: 'AI已完成甲状腺与乳腺报告结构化，建议生成合并结节健康管理报告并进入医生复核。',
    next: '今天 16:40', events: ['双部位报告已上传', 'AI结构化解析完成'],
    uploadTime: '2026-04-22 11:20', aiStatus: '解析完成',
    noduleCount: 2, maxDiameter: '7mm', density: '实性', grade: 'TI-RADS 3 / BI-RADS 3',
    timeline: [
      { type: 'system', at: '11:20', text: '双部位报告已上传。' },
      { type: 'system', at: '11:28', text: 'AI结构化解析完成，建议生成健康管理报告。' }
    ]
  },
  {
    id: 'p8', name: '郑女士', age: 49, phone: '130****3391', gender: '女',
    source: '门诊', noduleType: 'thyroid_breast_lung', nodule: '甲状腺、乳腺合并肺部结节',
    risk: 'high', stage: 'report', owner: '健康管理师',
    report: '肺部CT、甲状腺超声、乳腺超声均有结节记录，待系统统一结构化。',
    ai: '待AI提取三类检查字段，生成跨病种风险分层和随访节奏建议。',
    next: '今天 19:00', events: ['患者建档完成', '三类检查资料待处理'],
    uploadTime: '2026-04-23 09:00', aiStatus: '待处理报告',
    noduleCount: 3, maxDiameter: '10mm', density: '混合', grade: '待解析',
    timeline: [
      { type: 'system', at: '09:00', text: '患者建档完成，三类检查资料待处理。' }
    ]
  },
  {
    id: 'p9', name: '吴女士', age: 44, phone: '133****5512', gender: '女',
    source: '体检中心', noduleType: 'breast', nodule: '乳腺结节',
    risk: 'mid', stage: 'followup', owner: '健康管理师',
    report: '乳腺超声 BI-RADS 3 类，已进入6个月随访周期。',
    ai: 'AI已发送第14天随访问卷，患者反馈良好，无异常症状。',
    next: '2026-05-08', events: ['随访任务已生成', '第14天问卷已回收', '无异常'],
    uploadTime: '2026-04-09 10:20', aiStatus: '解析完成',
    noduleCount: 1, maxDiameter: '6mm', density: '实性', grade: 'BI-RADS 3',
    timeline: [
      { type: 'system', at: '10:20', text: '随访任务已生成，AI问卷已发送。' },
      { type: 'patient', at: '11:05', text: '没有不舒服，就是有点担心。' },
      { type: 'staff', at: '11:10', from: '健康管理师', text: 'BI-RADS 3 属于良性可能性大，按时复查即可，不必过度焦虑。' }
    ]
  },
  {
    id: 'p10', name: '张先生', age: 67, phone: '139****0044', gender: '男',
    source: '门诊', noduleType: 'lung', nodule: '肺部结节',
    risk: 'high', stage: 'followup', owner: '医生',
    report: '右下肺实性结节 11mm，Lung-RADS 4A，已进入3个月高风险随访。',
    ai: 'AI已完成第30天随访，患者无新增症状，建议按计划复查。',
    next: '2026-05-23', events: ['高风险随访启动', '第30天随访完成', '复查预约中'],
    uploadTime: '2026-03-24 09:00', aiStatus: '解析完成',
    noduleCount: 1, maxDiameter: '11mm', density: '实性', grade: 'Lung-RADS 4A',
    timeline: [
      { type: 'system', at: '09:00', text: '高风险随访计划已启动，3个月复查周期。' },
      { type: 'system', at: '09:05', text: '第30天AI随访问卷已发送并回收。' },
      { type: 'patient', at: '10:30', text: '没有咳嗽加重，就是偶尔胸闷。' },
      { type: 'staff', at: '10:45', from: '医生', text: '胸闷需关注，已安排5月23日复查CT，请按时就诊。' }
    ]
  },
  {
    id: 'p11', name: '林女士', age: 38, phone: '136****7723', gender: '女',
    source: '体检中心', noduleType: 'thyroid', nodule: '甲状腺结节',
    risk: 'low', stage: 'done', owner: '随访护士',
    report: '甲状腺超声 TI-RADS 2 类，低风险，已完成12个月随访闭环。',
    ai: 'AI随访全程完成，患者依从性良好，已归档。',
    next: '2027-04-15', events: ['随访全程完成', '复查结果稳定', '已闭环归档'],
    uploadTime: '2025-04-15 14:00', aiStatus: '解析完成',
    noduleCount: 1, maxDiameter: '3mm', density: '囊性', grade: 'TI-RADS 2',
    timeline: [
      { type: 'system', at: '14:00', text: '12个月随访计划已完成，结节稳定。' },
      { type: 'system', at: '14:05', text: '已闭环归档，下次随访：2027-04-15。' }
    ]
  },
  {
    id: 'p12', name: '黄女士', age: 52, phone: '137****8890', gender: '女',
    source: '门诊', noduleType: 'breast_thyroid', nodule: '乳腺合并甲状腺结节',
    risk: 'mid', stage: 'alert', owner: '健康管理师',
    report: '患者随访反馈乳房局部疼痛加重，触发异常预警。',
    ai: 'AI已触发中风险异常预警，建议转健康管理师人工跟进，不自动输出诊疗结论。',
    next: '立即处理', events: ['随访中', '患者反馈疼痛加重', '已触发预警'],
    uploadTime: '2026-04-20 08:30', aiStatus: '异常报告',
    noduleCount: 2, maxDiameter: '8mm', density: '实性', grade: 'BI-RADS 3 / TI-RADS 3',
    timeline: [
      { type: 'system', at: '08:30', text: '随访问卷已发送。' },
      { type: 'patient', at: '10:15', text: '最近乳房这边疼得比较厉害，比上次严重。' },
      { type: 'system', at: '10:16', text: '⚠ 症状加重预警已触发，已通知健康管理师。' },
      { type: 'staff', at: '10:25', from: '健康管理师', text: '已收到预警，请您今天方便时来院复查，我会提前安排。' }
    ]
  },
  {
    id: 'p13', name: '马先生', age: 71, phone: '138****2267', gender: '男',
    source: '体检中心', noduleType: 'lung', nodule: '肺部结节',
    risk: 'high', stage: 'followup', owner: '医生',
    report: '左上肺磨玻璃结节 9mm，Lung-RADS 4A，高龄高风险，3个月随访中。',
    ai: 'AI已完成第7天随访，患者配合度高，无新增症状。',
    next: '2026-05-15', events: ['高风险随访启动', '第7天随访完成'],
    uploadTime: '2026-04-08 11:00', aiStatus: '解析完成',
    noduleCount: 1, maxDiameter: '9mm', density: '磨玻璃', grade: 'Lung-RADS 4A',
    timeline: [
      { type: 'system', at: '11:00', text: '高风险随访计划已启动。' },
      { type: 'patient', at: '14:20', text: '我按时吃药了，没有特别不舒服。' }
    ]
  },
  {
    id: 'p14', name: '何女士', age: 41, phone: '135****4401', gender: '女',
    source: '门诊', noduleType: 'breast', nodule: '乳腺结节',
    risk: 'mid', stage: 'done', owner: '随访护士',
    report: '乳腺超声 BI-RADS 3 类，6个月随访已完成，结节无明显变化。',
    ai: 'AI随访6个月完成，结节稳定，已闭环。',
    next: '2026-10-28', events: ['6个月随访完成', '结节稳定', '已闭环'],
    uploadTime: '2025-10-28 09:30', aiStatus: '解析完成',
    noduleCount: 1, maxDiameter: '5mm', density: '实性', grade: 'BI-RADS 3',
    timeline: [
      { type: 'system', at: '09:30', text: '6个月随访计划完成，结节无明显变化，已闭环。' }
    ]
  },
  {
    id: 'p15', name: '徐女士', age: 56, phone: '132****9934', gender: '女',
    source: '体检中心', noduleType: 'thyroid_lung', nodule: '甲状腺合并肺部结节',
    risk: 'high', stage: 'followup', owner: '健康管理师',
    report: '甲状腺 TI-RADS 4A 合并肺部磨玻璃结节，双高风险，3个月随访中。',
    ai: 'AI已完成第21天随访，患者反馈轻微咽部不适，已记录并提示关注。',
    next: '2026-05-19', events: ['双高风险随访启动', '第21天随访完成', '咽部不适已记录'],
    uploadTime: '2026-03-29 10:00', aiStatus: '解析完成',
    noduleCount: 2, maxDiameter: '8mm', density: '混合', grade: 'TI-RADS 4A / Lung-RADS 3',
    timeline: [
      { type: 'system', at: '10:00', text: '双高风险随访计划已启动。' },
      { type: 'patient', at: '11:30', text: '喉咙有点不舒服，不知道和结节有没有关系。' },
      { type: 'staff', at: '11:40', from: '健康管理师', text: '已记录，甲状腺结节有时会引起咽部异物感，建议下次复查时告知医生。' }
    ]
  },
  {
    id: 'p16', name: '谢先生', age: 59, phone: '139****6618', gender: '男',
    source: '门诊', noduleType: 'lung', nodule: '肺部结节',
    risk: 'mid', stage: 'followup', owner: '随访护士',
    report: '右肺中叶实性结节 6mm，Lung-RADS 3，6个月随访中。',
    ai: 'AI已完成第45天随访，患者无异常反馈，依从性良好。',
    next: '2026-06-10', events: ['中风险随访启动', '第45天随访完成'],
    uploadTime: '2026-02-25 14:00', aiStatus: '解析完成',
    noduleCount: 1, maxDiameter: '6mm', density: '实性', grade: 'Lung-RADS 3',
    timeline: [
      { type: 'system', at: '14:00', text: '6个月随访计划已启动。' },
      { type: 'patient', at: '16:00', text: '没有什么不舒服，按时复查就好。' }
    ]
  }
]

export const stageLabels = {
  intake: '待补资料',
  report: '待处理报告',
  parsed: 'AI解析完成',
  review: '待医生复核',
  push: '待推送患者',
  followup: '随访中',
  alert: '异常待处理',
  done: '已闭环'
}

export const riskText = (risk) =>
  risk === 'high' ? '高风险' : risk === 'mid' ? '中风险' : '低风险'

export const riskClass = (risk) =>
  risk === 'high' ? 'high' : risk === 'mid' ? 'orange' : 'green'

export const stageClass = (stage) => {
  if (stage === 'alert') return 'high'
  if (['report', 'parsed'].includes(stage)) return 'orange'
  if (['review', 'push'].includes(stage)) return 'blue'
  if (stage === 'followup') return 'green'
  return 'gray'
}
