<template>
  <div class="followup-page">
    <header class="page-head">
      <div>
        <p class="crumb">首页 / 随访任务执行</p>
        <h1>随访任务执行</h1>
      </div>
      <div class="head-actions">
        <button class="btn" type="button" @click="loadDashboard">刷新</button>
        <button class="primary" type="button" :disabled="runningScheduler" @click="runScheduler">
          {{ runningScheduler ? '调度中...' : '运行调度器' }}
        </button>
      </div>
    </header>

    <section class="metric-grid">
      <article v-for="item in metricCards" :key="item.key" class="metric-card" :data-tone="item.tone">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <em>{{ item.hint }}</em>
      </article>
    </section>

    <div v-if="error" class="notice error">{{ error }}</div>
    <div v-if="toastText" class="notice">{{ toastText }}</div>

    <section class="board-grid">
      <aside class="task-panel">
        <div class="panel-head">
          <div>
            <h2>任务队列</h2>
            <p>共 {{ filteredTasks.length }} 条</p>
          </div>
        </div>

        <div class="filters">
          <input v-model.trim="filters.search" placeholder="患者姓名 / 手机 / 任务码">
          <select v-model="filters.status">
            <option value="">全部状态</option>
            <option value="pending">待发送</option>
            <option value="scheduled">待调度</option>
            <option value="sent">已发送</option>
            <option value="replied">已回复</option>
            <option value="manual_processing">待处理</option>
            <option value="alert">重点关注</option>
            <option value="completed">已完成</option>
            <option value="failed">失败</option>
          </select>
          <select v-model="filters.due">
            <option value="">全部时间</option>
            <option value="today">今日到期</option>
            <option value="overdue">已逾期</option>
          </select>
        </div>

        <div class="task-list">
          <button
            v-for="task in filteredTasks"
            :key="task.id"
            type="button"
            class="task-item"
            :class="{ active: task.id === selectedTaskId }"
            @click="selectTask(task)"
          >
            <span class="task-top">
              <b>{{ task.patient?.name || `患者${task.patient_id}` }}</b>
              <em :data-status="task.status">{{ statusText(task.status) }}</em>
            </span>
            <span class="task-title">{{ task.title }}</span>
            <span class="task-meta">{{ task.plan_name || '健康管理计划' }} · Day {{ task.plan_day || 1 }}</span>
            <span class="task-meta">{{ task.due_at || '未设置到期时间' }}</span>
          </button>
          <div v-if="!filteredTasks.length" class="empty">暂无匹配任务</div>
        </div>
      </aside>

      <main class="detail-panel" v-if="selectedTask">
        <section class="detail-card hero-card">
          <div>
            <p class="eyebrow">任务 {{ selectedTask.task_code }}</p>
            <h2>{{ selectedTask.title }}</h2>
            <div class="hero-meta">
              <span>{{ selectedTask.patient?.name || '-' }}</span>
              <span>{{ selectedTask.patient?.phone || '未登记手机号' }}</span>
              <span>{{ noduleText(selectedTask.nodule_type || selectedTask.patient?.nodule_type) }}</span>
              <span>{{ riskText(selectedTask.risk_level) }}</span>
            </div>
          </div>
          <span class="status-pill" :data-status="selectedTask.status">{{ statusText(selectedTask.status) }}</span>
        </section>

        <section class="detail-grid">
          <article class="detail-card">
            <h3>任务信息</h3>
            <div class="kv-grid">
              <div><span>计划</span><b>{{ selectedTask.plan_name || '-' }}</b></div>
              <div><span>节点</span><b>{{ nodeName }}</b></div>
              <div><span>任务类型</span><b>{{ taskTypeText(nodeInfo.task_type) }}</b></div>
              <div><span>触达通道</span><b>{{ channelText(selectedTask.channel) }}</b></div>
              <div><span>计划发送</span><b>{{ selectedTask.scheduled_send_at || '-' }}</b></div>
              <div><span>到期时间</span><b>{{ selectedTask.due_at || '-' }}</b></div>
            </div>
          </article>

          <article class="detail-card">
            <h3>执行操作</h3>
            <div class="action-grid">
              <button class="primary" type="button" @click="sendTask">发送提醒</button>
              <button class="btn" type="button" @click="openReplyModal">录入打卡/回复</button>
              <button class="btn" type="button" @click="openManualModal">健康管理师处理</button>
              <button class="btn" type="button" @click="completeTask">标记完成</button>
              <button class="btn" type="button" @click="copyCheckinLink">复制打卡链接</button>
              <button class="btn" type="button" @click="openCheckinLink">打开打卡页</button>
              <button class="btn" type="button" @click="copyOutboundContent" :disabled="!latestOutboundMessage">复制发送文案</button>
            </div>
            <div class="send-state-grid">
              <div class="send-state">
                <span>发送状态</span>
                <b :data-status="latestSendStatus">{{ sendStatusText(latestSendStatus) }}</b>
                <small>{{ latestOutboundMessage?.error_message || latestOutboundMessage?.provider_response?.message || '任务可通过公开打卡链接继续流转' }}</small>
              </div>
              <div class="send-state">
                <span>公开打卡链接</span>
                <b>{{ checkinLink ? '已生成' : '未生成' }}</b>
                <small>{{ checkinLink || '发送或创建任务后生成' }}</small>
              </div>
            </div>
          </article>
        </section>

        <section v-if="selectedTask.abnormal_flag || ['alert', 'manual_processing', 'failed'].includes(selectedTask.status)" class="alert-card">
          <strong>需要健康管理师处理</strong>
          <span>{{ selectedTask.abnormal_reason || selectedTask.ai_summary || '任务处于重点关注或待处理状态，请健康管理师跟进。' }}</span>
          <button class="btn" type="button" @click="openManualModal">记录处理</button>
        </section>

        <section class="columns">
          <article class="detail-card">
            <div class="card-title-row">
              <h3>消息记录</h3>
              <span>{{ messages.length }} 条</span>
            </div>
            <div class="timeline-list">
              <div v-for="msg in messages" :key="msg.id" class="message-row" :data-dir="msg.direction">
                <div class="row-time">{{ msg.created_at || msg.sent_at || msg.received_at || '-' }}</div>
                <b>{{ senderText(msg) }}</b>
                <p>{{ msg.content }}</p>
                <small>{{ sendStatusText(msg.send_status) || msg.ai_intent || '' }}</small>
              </div>
              <div v-if="!messages.length" class="empty">暂无消息记录</div>
            </div>
          </article>

          <article class="detail-card">
            <div class="card-title-row">
              <h3>患者打卡</h3>
              <span>{{ checkins.length }} 条</span>
            </div>
            <div class="timeline-list">
              <div v-for="item in checkins" :key="item.id" class="checkin-row" :class="{ alert: item.abnormal_flag }">
                <div class="row-time">{{ item.submitted_at }}</div>
                <b>{{ taskTypeText(item.checkin_type) }}</b>
                <p>{{ item.content_text || '患者已提交图片/结构化打卡' }}</p>
                <div v-if="item.image_urls?.length" class="checkin-images">
                  <a v-for="url in item.image_urls" :key="url" :href="url" target="_blank" rel="noreferrer">
                    <img :src="url" alt="患者打卡图片">
                  </a>
                </div>
                <small>{{ item.abnormal_reason || item.ai_result?.summary || statusText(item.status) }}</small>
                <button class="mini-btn" type="button" @click="reviewCheckin(item)">标记已查看</button>
              </div>
              <div v-if="!checkins.length" class="empty">暂无打卡记录</div>
            </div>
          </article>
        </section>

        <section class="detail-card">
          <div class="card-title-row">
            <h3>事件流水</h3>
            <span>{{ events.length }} 条</span>
          </div>
          <div class="event-list">
            <div v-for="event in events" :key="event.id" class="event-row">
              <span>{{ event.created_at }}</span>
              <b>{{ eventTypeText(event.event_type) }}</b>
              <p>{{ event.summary || '-' }}</p>
              <em v-if="event.from_status || event.to_status">{{ statusText(event.from_status) }} -> {{ statusText(event.to_status) }}</em>
            </div>
            <div v-if="!events.length" class="empty">暂无事件记录</div>
          </div>
        </section>
      </main>

      <main class="detail-panel empty-detail" v-else>
        <div class="empty">请选择左侧任务</div>
      </main>
    </section>

    <div v-if="replyModalOpen" class="modal-mask" @click.self="replyModalOpen = false">
      <section class="modal-card">
        <div class="modal-head">
          <h2>录入用户打卡/回复</h2>
          <button class="icon-close" type="button" @click="replyModalOpen = false">×</button>
        </div>
        <label>内容<textarea v-model.trim="replyForm.content" rows="5" placeholder="例如：用户今日已完成饮食和运动打卡，睡眠正常。"></textarea></label>
        <div class="modal-actions">
          <button class="btn" type="button" @click="replyModalOpen = false">取消</button>
          <button class="primary" type="button" @click="submitReply">保存记录</button>
        </div>
      </section>
    </div>

    <div v-if="manualModalOpen" class="modal-mask" @click.self="manualModalOpen = false">
      <section class="modal-card">
        <div class="modal-head">
          <h2>健康管理师处理</h2>
          <button class="icon-close" type="button" @click="manualModalOpen = false">×</button>
        </div>
        <label>处理动作
          <select v-model="manualForm.action">
            <option value="manual_followed">已跟进</option>
            <option value="doctor_handoff">重点关注</option>
            <option value="close_alert">关闭关注并完成</option>
          </select>
        </label>
        <label>处理备注<textarea v-model.trim="manualForm.note" rows="5" placeholder="记录沟通情况、打卡说明、饮食建议或关闭原因。"></textarea></label>
        <div class="modal-actions">
          <button class="btn" type="button" @click="manualModalOpen = false">取消</button>
          <button class="primary" type="button" @click="submitManualAction">提交处理</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

const tasks = ref([])
const metrics = ref({})
const selectedTaskId = ref(null)
const selectedTaskDetail = ref(null)
const checkins = ref([])
const loadingDetail = ref(false)
const runningScheduler = ref(false)
const error = ref('')
const toastText = ref('')
const replyModalOpen = ref(false)
const manualModalOpen = ref(false)

const filters = reactive({
  search: '',
  status: '',
  due: ''
})

const replyForm = reactive({
  content: ''
})

const manualForm = reactive({
  action: 'manual_followed',
  note: ''
})

const selectedTask = computed(() => selectedTaskDetail.value || tasks.value.find(task => task.id === selectedTaskId.value) || null)
const messages = computed(() => selectedTask.value?.messages || [])
const events = computed(() => selectedTask.value?.events || [])
const nodeInfo = computed(() => selectedTask.value?.task_payload?.node || {})
const nodeName = computed(() => nodeInfo.value.name || selectedTask.value?.title || '-')
const checkinLink = computed(() => {
  const task = selectedTask.value
  if (!task) return ''
  const path = task.public_checkin_path || (task.task_code ? `/followup-checkin/${task.task_code}` : '')
  if (!path) return ''
  if (/^https?:\/\//.test(path)) return path
  return `${window.location.origin}${path}`
})
const latestOutboundMessage = computed(() => {
  return [...messages.value].reverse().find(msg => msg.direction === 'outbound') || null
})
const latestSendStatus = computed(() => latestOutboundMessage.value?.send_status || selectedTask.value?.status || '')

const filteredTasks = computed(() => tasks.value.filter(task => {
  const text = `${task.task_code || ''} ${task.title || ''} ${task.patient?.name || ''} ${task.patient?.phone || ''}`
  if (filters.search && !text.includes(filters.search)) return false
  if (filters.status && task.status !== filters.status) return false
  if (filters.due === 'today' && !isToday(task.due_at)) return false
  if (filters.due === 'overdue' && !isOverdue(task)) return false
  return true
}))

const metricCards = computed(() => [
  { key: 'today', label: '今日到期', value: metrics.value.today_due ?? 0, hint: '需要触达', tone: 'blue' },
  { key: 'pending', label: '待发送', value: metrics.value.pending ?? 0, hint: '待调度/待发送', tone: 'orange' },
  { key: 'sent', label: '已发送/已打卡', value: metrics.value.sent ?? 0, hint: '执行中', tone: 'cyan' },
  { key: 'alert', label: '重点关注', value: metrics.value.alert ?? 0, hint: '需健康管理师处理', tone: 'red' },
  { key: 'completed', label: '已完成', value: metrics.value.completed ?? 0, hint: `完成率 ${metrics.value.completion_rate ?? 0}%`, tone: 'green' },
  { key: 'overdue', label: '逾期', value: metrics.value.overdue ?? 0, hint: '建议跟进', tone: 'purple' },
])

watch(selectedTaskId, async (id) => {
  if (id) await loadTaskDetail(id)
})

onMounted(loadDashboard)

async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok || data?.success === false) throw new Error(data?.message || `请求失败：${res.status}`)
  return data.data ?? data
}

async function loadDashboard() {
  error.value = ''
  try {
    const [taskPage, metricData] = await Promise.all([
      apiFetch('/api/b/followup/tasks?per_page=100'),
      apiFetch('/api/b/followup/tasks/metrics')
    ])
    tasks.value = taskPage?.items || []
    metrics.value = metricData || {}
    if (!selectedTaskId.value && tasks.value[0]?.id) selectedTaskId.value = tasks.value[0].id
    if (selectedTaskId.value) await loadTaskDetail(selectedTaskId.value)
  } catch (e) {
    error.value = e?.message || '任务加载失败'
  }
}

async function loadTaskDetail(taskId) {
  loadingDetail.value = true
  error.value = ''
  try {
    const [detail, checkinItems] = await Promise.all([
      apiFetch(`/api/b/followup/tasks/${taskId}`),
      apiFetch(`/api/b/followup/tasks/${taskId}/checkins`)
    ])
    selectedTaskDetail.value = detail
    checkins.value = Array.isArray(checkinItems) ? checkinItems : []
  } catch (e) {
    error.value = e?.message || '任务详情加载失败'
  } finally {
    loadingDetail.value = false
  }
}

function selectTask(task) {
  selectedTaskId.value = task.id
}

async function runScheduler() {
  runningScheduler.value = true
  error.value = ''
  try {
    const result = await apiFetch('/api/b/followup/scheduler/run-once', {
      method: 'POST',
      body: JSON.stringify({ limit: 50 })
    })
    showToast(`调度完成：处理 ${result?.processed ?? 0} 个任务`)
    await loadDashboard()
  } catch (e) {
    error.value = e?.message || '调度执行失败'
  } finally {
    runningScheduler.value = false
  }
}

async function sendTask() {
  if (!selectedTask.value?.id) return
  try {
    const task = await apiFetch(`/api/b/followup/tasks/${selectedTask.value.id}/send`, {
      method: 'POST',
      body: JSON.stringify({})
    })
    selectedTaskDetail.value = task
    showToast(task.messages?.some(msg => msg.send_status === 'dry_run') ? '已生成公开打卡链接' : '任务提醒已处理')
    await loadTaskDetail(selectedTask.value.id)
    await loadDashboard()
  } catch (e) {
    error.value = e?.message || '发送失败'
  }
}

async function completeTask() {
  if (!selectedTask.value?.id) return
  try {
    await apiFetch(`/api/b/followup/tasks/${selectedTask.value.id}/complete`, {
      method: 'POST',
      body: JSON.stringify({ summary: '健康管理师在执行看板标记完成' })
    })
    showToast('任务已标记完成')
    await loadDashboard()
  } catch (e) {
    error.value = e?.message || '标记完成失败'
  }
}

function openReplyModal() {
  replyForm.content = ''
  replyModalOpen.value = true
}

async function submitReply() {
  if (!selectedTask.value?.id || !replyForm.content) return
  try {
    await apiFetch(`/api/b/followup/tasks/${selectedTask.value.id}/reply`, {
      method: 'POST',
      body: JSON.stringify({ content: replyForm.content, channel: selectedTask.value.channel })
    })
    replyModalOpen.value = false
    showToast('用户记录已录入')
    await loadDashboard()
  } catch (e) {
    error.value = e?.message || '录入回复失败'
  }
}

function openManualModal() {
  manualForm.action = selectedTask.value?.status === 'completed' ? 'manual_followed' : 'manual_followed'
  manualForm.note = selectedTask.value?.abnormal_reason || ''
  manualModalOpen.value = true
}

async function submitManualAction() {
  if (!selectedTask.value?.id) return
  try {
    await apiFetch(`/api/b/followup/tasks/${selectedTask.value.id}/manual-action`, {
      method: 'POST',
      body: JSON.stringify({ action: manualForm.action, note: manualForm.note })
    })
    manualModalOpen.value = false
    showToast('人工处理已记录')
    await loadDashboard()
  } catch (e) {
    error.value = e?.message || '人工处理失败'
  }
}

async function reviewCheckin(item) {
  try {
    await apiFetch(`/api/b/followup/checkins/${item.id}/review`, {
      method: 'POST',
      body: JSON.stringify({ status: 'closed', note: '健康管理师已查看打卡记录' })
    })
    showToast('打卡记录已查看')
    await loadTaskDetail(selectedTask.value.id)
  } catch (e) {
    error.value = e?.message || '打卡记录处理失败'
  }
}

async function copyCheckinLink() {
  if (!checkinLink.value) return
  try {
    await navigator.clipboard.writeText(checkinLink.value)
    showToast('打卡链接已复制')
  } catch (e) {
    showToast(checkinLink.value)
  }
}

async function copyOutboundContent() {
  const content = latestOutboundMessage.value?.content || ''
  if (!content) return
  try {
    await navigator.clipboard.writeText(content)
    showToast('发送文案已复制')
  } catch (e) {
    showToast(content)
  }
}

function openCheckinLink() {
  if (checkinLink.value) window.open(checkinLink.value, '_blank')
}

function showToast(text) {
  toastText.value = text
  window.setTimeout(() => {
    if (toastText.value === text) toastText.value = ''
  }, 2400)
}

function isToday(value) {
  if (!value) return false
  return String(value).slice(0, 10) === new Date().toISOString().slice(0, 10)
}

function isOverdue(task) {
  if (!task?.due_at || ['completed', 'cancelled'].includes(task.status)) return false
  return new Date(task.due_at.replace(' ', 'T')).getTime() < Date.now()
}

function statusText(status) {
  return ({
    pending: '待发送',
    scheduled: '待调度',
    sent: '已发送',
    replied: '已回复',
    manual_processing: '待处理',
    alert: '重点关注',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
    analyzed: '已分析',
    submitted: '已提交'
  }[status] || status || '-')
}

function riskText(risk) {
  const text = String(risk || '').toLowerCase()
  if (['high', '高危', '高风险'].includes(text)) return '高风险'
  if (['mid', 'medium', '中危', '中风险'].includes(text)) return '中风险'
  if (['low', '低危', '低风险'].includes(text)) return '低风险'
  return risk || '-'
}

function noduleText(type) {
  return ({ breast: '乳腺', thyroid: '甲状腺', lung: '肺部' }[type] || type || '-')
}

function channelText(channel) {
  return ({ wecom: '企业微信', phone: '电话', miniapp: '小程序', manual: '公开链接/人工触达', public_checkin: '公开打卡页' }[channel] || channel || '-')
}

function sendStatusText(status) {
  return ({
    created: '已创建',
    dry_run: '公开链接模式',
    sent: '已发送',
    delivered: '已送达',
    read: '已读',
    replied: '已回复',
    failed: '发送失败'
  }[status] || status || '')
}

function taskTypeText(type) {
  return ({
    knowledge_push: '知识推送',
    daily_checkin: '每日打卡',
    diet_checkin: '饮食打卡/图片识别',
    exercise_reminder: '运动提醒',
    psych_reminder: '心理提醒',
    review_reminder: '复查提醒'
  }[type] || type || '-')
}

function senderText(msg) {
  if (msg.sender_type === 'patient') return '患者'
  if (msg.sender_type === 'ai') return 'AI机器人'
  if (msg.sender_type === 'staff') return '健康管理师'
  return msg.sender_type || msg.direction || '-'
}

function eventTypeText(type) {
  return ({
    task_created: '任务创建',
    task_created_from_report: '报告生成任务',
    scheduler_message_sent: '调度发送',
    scheduler_message_failed: '调度失败',
    scheduler_error: '调度错误',
    message_sent: '消息发送',
    message_failed: '消息失败',
    patient_reply_analyzed: '患者回复分析',
    public_checkin_submitted: '患者打卡',
    checkin_alert: '打卡关注',
    task_completed: '任务完成'
  }[type] || type || '-')
}
</script>

<style scoped>
.followup-page{display:grid;gap:14px;color:#172033}
.page-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
.crumb{margin:0 0 4px;color:#667085;font-size:13px}
h1{margin:0;font-size:24px;line-height:1.2}
h2,h3{margin:0}
.head-actions{display:flex;gap:8px}
.btn,.primary,.mini-btn{height:36px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;color:#344054;padding:0 12px;font-weight:800;cursor:pointer}
.primary{border-color:#155eef;background:#155eef;color:#fff}
.mini-btn{height:30px;font-size:12px;justify-self:start}
button:disabled{opacity:.6;cursor:not-allowed}
.metric-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}
.metric-card{background:#fff;border:1px solid #e4e7ec;border-radius:8px;padding:13px;display:grid;gap:5px;box-shadow:0 8px 22px rgba(16,24,40,.05)}
.metric-card span{color:#667085;font-size:13px}
.metric-card strong{font-size:25px;line-height:1}
.metric-card em{font-style:normal;color:#98a2b3;font-size:12px}
.metric-card[data-tone="red"] strong{color:#d92d20}
.metric-card[data-tone="green"] strong{color:#079455}
.metric-card[data-tone="orange"] strong{color:#dc6803}
.metric-card[data-tone="cyan"] strong{color:#088ab2}
.metric-card[data-tone="purple"] strong{color:#7a5af8}
.notice{border:1px solid #b2ddff;background:#eff8ff;color:#175cd3;border-radius:8px;padding:10px 12px;font-weight:700}
.notice.error{border-color:#fecdca;background:#fffbfa;color:#b42318}
.board-grid{display:grid;grid-template-columns:340px minmax(0,1fr);gap:14px;align-items:start}
.task-panel,.detail-card,.detail-panel{background:#fff;border:1px solid #e4e7ec;border-radius:8px;box-shadow:0 8px 22px rgba(16,24,40,.05)}
.task-panel{padding:14px;position:sticky;top:0}
.panel-head,.card-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.panel-head p,.card-title-row span{margin:4px 0 0;color:#667085;font-size:12px}
.filters{display:grid;gap:8px;margin-bottom:12px}
input,select{width:100%;box-sizing:border-box;border:1px solid #d0d5dd;border-radius:8px;padding:9px 10px;color:#172033;font:inherit;background:#fff}
.task-list{display:grid;gap:8px;max-height:calc(100vh - 285px);overflow:auto;padding-right:2px}
.task-item{border:1px solid #e4e7ec;background:#fff;border-radius:8px;padding:11px;text-align:left;display:grid;gap:5px;cursor:pointer}
.task-item.active{border-color:#155eef;background:#eff6ff}
.task-top{display:flex;align-items:center;justify-content:space-between;gap:8px}
.task-top b{color:#172033}
.task-top em,.status-pill{font-style:normal;border-radius:999px;padding:4px 8px;background:#eef4ff;color:#155eef;font-size:12px;font-weight:800}
[data-status="alert"],[data-status="manual_processing"],[data-status="failed"]{background:#fff1f3!important;color:#c01048!important}
[data-status="completed"]{background:#ecfdf3!important;color:#067647!important}
[data-status="pending"],[data-status="scheduled"]{background:#fff7ed!important;color:#b54708!important}
.task-title{font-weight:800;color:#344054}
.task-meta{font-size:12px;color:#667085}
.detail-panel{display:grid;gap:12px;padding:14px}
.empty-detail{min-height:360px;place-items:center}
.hero-card{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;padding:16px}
.eyebrow{margin:0 0 5px;color:#667085;font-size:12px}
.hero-card h2{font-size:20px;line-height:1.3}
.hero-meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.hero-meta span{border:1px solid #e4e7ec;border-radius:999px;padding:4px 8px;color:#475467;font-size:12px;background:#fff}
.detail-grid,.columns{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.detail-card{padding:14px}
.detail-card h3{font-size:16px;margin-bottom:12px}
.kv-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.kv-grid div{border:1px solid #eef2f7;border-radius:8px;padding:10px;display:grid;gap:5px}
.kv-grid span{color:#667085;font-size:12px}
.kv-grid b{font-size:13px;color:#172033}
.action-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.send-state-grid{margin-top:10px;display:grid;grid-template-columns:1fr;gap:8px}
.send-state{border:1px solid #e4e7ec;border-radius:8px;padding:9px;background:#f8fafc;display:grid;gap:3px;min-width:0}
.send-state span{color:#667085;font-size:12px}
.send-state b{color:#172033;font-size:13px}
.send-state b[data-status="dry_run"]{color:#155eef}
.send-state b[data-status="failed"]{color:#b42318}
.send-state b[data-status="sent"],.send-state b[data-status="replied"]{color:#027a48}
.send-state small{color:#667085;font-size:12px;line-height:1.45;word-break:break-all}
.alert-card{border:1px solid #fedf89;background:#fffaeb;color:#93370d;border-radius:8px;padding:12px;display:grid;gap:5px}
.timeline-list,.event-list{display:grid;gap:8px;max-height:360px;overflow:auto}
.message-row,.checkin-row,.event-row{border:1px solid #eef2f7;border-radius:8px;padding:10px;display:grid;gap:4px}
.message-row[data-dir="inbound"]{background:#f8fafc}
.checkin-row.alert{border-color:#fedf89;background:#fffaeb}
.row-time,.event-row span{font-size:12px;color:#98a2b3}
.message-row p,.checkin-row p,.event-row p{margin:0;color:#475467;line-height:1.55}
.message-row small,.checkin-row small,.event-row em{color:#667085;font-size:12px;font-style:normal}
.checkin-images{display:flex;gap:8px;flex-wrap:wrap;margin-top:2px}
.checkin-images a{display:block;width:72px;height:72px;border:1px solid #e4e7ec;border-radius:8px;overflow:hidden;background:#f8fafc}
.checkin-images img{width:100%;height:100%;object-fit:cover;display:block}
.empty{border:1px dashed #d0d5dd;border-radius:8px;padding:18px;text-align:center;color:#667085}
.modal-mask{position:fixed;inset:0;background:rgba(15,23,42,.42);display:grid;place-items:center;z-index:60;padding:20px}
.modal-card{width:min(560px,100%);background:#fff;border-radius:10px;padding:16px;box-shadow:0 24px 80px rgba(15,23,42,.28);display:grid;gap:14px}
.modal-head{display:flex;align-items:center;justify-content:space-between}
.icon-close{width:32px;height:32px;border:1px solid #e4e7ec;border-radius:8px;background:#fff;font-size:22px;line-height:1;cursor:pointer}
.modal-card label{display:grid;gap:7px;color:#344054;font-weight:800;font-size:13px}
textarea{width:100%;box-sizing:border-box;border:1px solid #d0d5dd;border-radius:8px;padding:10px;color:#172033;font:inherit;resize:vertical}
.modal-actions{display:flex;justify-content:flex-end;gap:8px}
@media (max-width:1180px){.metric-grid{grid-template-columns:repeat(3,1fr)}.board-grid,.detail-grid,.columns{grid-template-columns:1fr}.task-panel{position:static}.task-list{max-height:420px}}
@media (max-width:720px){.metric-grid{grid-template-columns:1fr 1fr}.page-head,.hero-card{display:grid}.kv-grid,.action-grid{grid-template-columns:1fr}}
</style>
