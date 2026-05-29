import assert from 'node:assert/strict'
import { ref } from 'vue'
import { useFollowupTasks } from '../src/composables/useFollowupTasks.js'
import { usePatientDisplay } from '../src/composables/usePatientDisplay.js'
import { stageForTab } from '../src/composables/usePatientManagementNavigation.js'
import { useReportFollowupTasks } from '../src/composables/useReportFollowupTasks.js'

const scenario = ref({ defaultOwner: '王医生', reportLabel: '健康报告', key: 'hospital' })
const display = usePatientDisplay({ scenario, isCheckupScenario: ref(false) })

assert.equal(display.statusLabel({ stage: 'follow' }), '任务执行中')
assert.equal(display.riskLevelLabel('mid'), '中风险')
assert.equal(display.riskToneFromLevel('高危'), 'r')
assert.equal(display.noduleTypeLabel('breast_lung'), '乳腺+肺部结节')
assert.equal(display.channelLabel('wecom'), '企业微信')
assert.equal(stageForTab('followup-plan'), 'plan')
assert.equal(stageForTab('follow'), 'follow')
assert.equal(stageForTab('record'), 'gen')
assert.equal(stageForTab('detail'), 'all')

const activePatientId = ref('p1')
const followPatientId = ref('p1')
const planDay = ref('day1')
const planPatients = ref([])
const queue = ref([{ id: 'p1', name: '张三' }])
const followupTasks = useFollowupTasks({
  activePatientId,
  apiJson: async () => ({ items: [] }),
  followPatientId,
  getDraft: () => ({ channel: '企微', cycle: '3个月', reminder: '每日提醒', kbEnabled: { sport: true } }),
  noduleTypeLabel: display.noduleTypeLabel,
  planDay,
  planPatients,
  queue,
  riskToneFromLevel: display.riskToneFromLevel,
  scenario,
  subTab: ref('queue'),
})

const normalized = followupTasks.normalizeBackendTask({
  id: 7,
  patient_id: 11,
  patient: { id: 'p1', name: '张三', gender: '女', age: 45, phone: '18812345678', nodule_type: 'breast' },
  nodule_type: 'breast',
  risk_level: 'mid',
  channel: 'wecom',
  plan_day: 3,
  scheduled_send_at: '2026-05-29 09:30:00',
  task_payload: { node: { name: '早餐打卡', patient_action: 'upload_image', ai_action: 'diet_review' } },
  messages: [{ direction: 'outbound', sent_at: '2026-05-29 09:31:00' }],
  events: [{ created_at: '2026-05-29 09:31:00', actor_type: 'system', event_type: 'message_sent', summary: '已发送' }],
})

assert.equal(normalized.id, 'api-task-7')
assert.equal(normalized.phoneMasked, '188****5678')
assert.equal(normalized.risk, 'mid')
assert.equal(normalized.riskTone, 'o')
assert.equal(normalized.day, 'day3')
assert.equal(normalized.time, '09:30')
assert.equal(normalized.patientAction, '上传餐饮图片')
assert.equal(normalized.aiAction, '饮食点评')

const localTask = followupTasks.makeTaskFromPatient({
  id: 'p2',
  name: '李四',
  gender: '女',
  age: 39,
  phoneMasked: '188****0000',
  nodules: '乳腺结节',
  risk: '中风险',
  riskTone: 'o',
  owner: '王医生',
  planTask: { nodes: [{ send_time: '10:00', patient_action: 'reply_text', ai_action: 'reply', message_template: '请回复今日状态' }] },
})

assert.equal(localTask.channel, '企微')
assert.equal(localTask.cycle, '3个月')
assert.equal(localTask.time, '10:00')
assert.equal(localTask.patientAction, '文字回复')

const activePatient = ref({
  workspaceTasks: [
    { id: 1, report_id: 99, source: 'report', status: 'scheduled' },
    { id: 2, report_id: 100, source: 'report', status: 'cancelled' },
  ],
})
const reportFollowups = useReportFollowupTasks({
  activePatient,
  apiJson: async (url) => {
    const reportId = Number(new URL(url, 'http://local').searchParams.get('report_id'))
    return { items: reportId === 101 ? [{ id: 3, report_id: 101, source: 'report', status: 'scheduled' }] : [] }
  },
  apiPostJson: async (url) => ({ id: 4, report_id: Number(url.split('/').pop()), source: 'report', status: 'scheduled' }),
  followPatientId: ref('p1'),
  followTasks: ref([]),
  getHydratePatientWorkspace: () => null,
  loadFollowupTasks: async () => {},
  queue: ref([]),
  rpAuditId: ref(''),
  selectTask: () => {},
  setSubTab: () => {},
  toast: { show: () => {} },
})

assert.equal(reportFollowups.canCreateReportFollowup({ status: 'finalized' }), true)
assert.equal(reportFollowups.canCreateReportFollowup({ status: 'draft' }), false)
assert.equal(reportFollowups.existingReportFollowupTask(99).id, 1)
assert.equal(reportFollowups.existingReportFollowupTask(100), null)

const loaded = await reportFollowups.loadReportFollowupTask(101)
assert.equal(loaded.id, 3)
assert.equal(reportFollowups.existingReportFollowupTask(101).id, 3)

const created = await reportFollowups.createReportFollowupTask(102)
assert.equal(created.id, 4)
assert.equal(reportFollowups.existingReportFollowupTask(102).id, 4)

console.log('[OK] composable smoke checks passed')
