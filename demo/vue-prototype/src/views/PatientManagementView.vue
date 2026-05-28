<template>
  <div class="pm">
    <section class="pm-shell" aria-label="患者管理三栏工作台">
      <PatientQueueOverview
        v-if="subTab === 'queue'"
        :queue="queue"
        :filtered-queue="queueFiltered"
        :active-patient-id="activePatientId"
        :active-patient="activePatient"
        :report-terms="reportTerms"
        :scenario="scenario"
        :search="qSearch"
        :source="qSource"
        :nodule="qNodule"
        :risk="qRisk"
        :status="qStatus"
        :nodule-tags="noduleTags"
        :status-key="statusKey"
        :status-label="statusLabel"
        :source-label="sourceLabel"
        :owner-label="ownerLabel"
        :is-wecom-bound="isWecomBound"
        :wecom-status-text="wecomStatusText"
        :next-hint-v2="nextHintV2"
        :flow-nodes="flowNodes"
        :stage-actions="stageActions"
        :stage-timeline="stageTimeline"
        @update-search="qSearch = $event"
        @update-source="qSource = $event"
        @update-nodule="qNodule = $event"
        @update-risk="qRisk = $event"
        @update-status="qStatus = $event"
        @reset-filters="resetQueueFilters"
        @new-record="goRecord(null)"
        @select-patient="activePatientId = $event"
        @open-workspace="openPatientWorkspace"
        @open-followup-plan="openQueueFollowupPlan"
        @open-wecom-bind="openWecomBind"
        @unbind-wecom="unbindWecom"
      />
      <!-- record tab：患者建档（表单） -->
      <div v-else-if="subTab === 'record'" class="pm-record">
        <RecordView :embedded="true" :patient="recordPatient" @back="backToQueue" />
      </div>

      <!-- detail tab：患者全流程管理工作台 -->
      <PatientDetailWorkspace
        v-else-if="subTab === 'detail'"
        :patient="activePatient"
        :edit-mode="patientEditMode"
        :flow-steps="patientFlowSteps"
        :latest-record-label="latestRecordLabel"
        :active-plan-label="activePlanLabel"
        :task-execution-summary="taskExecutionSummary"
        :computed-risk="computedRisk"
        :risk-layer-items="riskLayerItems"
        :advice="activeAdvice"
        :advice-locked="adviceLocked"
        :advice-generating="adviceGenerating"
        :tongue-submitting="tongueSubmitting"
        :tongue-syncing="tongueSyncing"
        :tongue-action-label="workspaceTongueActionLabel"
        :tongue-status-label="workspaceTongueStatusLabel"
        :tongue-qr-url="workspaceTongueQrUrl"
        :plan-status-label="planStatusLabel"
        :cycle-label-from-days="cycleLabelFromDays"
        :channel-label="channelLabel"
        :tracking-status-label="trackingStatusLabel"
        :task-type-label="taskTypeLabel"
        :report-db-status-label="reportDbStatusLabel"
        :can-create-report-followup="canCreateReportFollowup"
        :is-creating-report-followup="isCreatingReportFollowup"
        :existing-report-followup-task="existingReportFollowupTask"
        :status-key="statusKey"
        :status-label="statusLabel"
        :is-wecom-bound="isWecomBound"
        :wecom-status-text="wecomStatusText"
        :advice-status-label="adviceStatusLabel"
        @back="setSubTab('queue')"
        @edit-record="goRecord"
        @update-patient="updateActivePatientField"
        @view-report="viewReport"
        @imaging-upload="handleImagingUpload"
        @remove-asset="removeAsset"
        @copy-tongue-link="copyWorkspaceTongueLink"
        @start-tongue="startWorkspaceTongueDiagnosis"
        @sync-tongue="syncWorkspaceTongueReport"
        @update-advice-content="updateActiveAdviceContent"
        @regenerate-advice="regenerateAdviceForActive"
        @save-advice="saveAdviceDraft"
        @submit-advice="submitAdviceReview"
        @approve-advice="approveAdviceToFinal"
        @create-report-followup="createFirstFollowupTaskForActive"
        @update-follow-plan="updateActiveFollowPlan"
        @save-follow-plan="saveFollowPlan"
        @open-follow="setSubTab('follow')"
        @copy-task-link="copyTaskCheckinLink"
      />

      <!-- followup-plan tab：随访任务下发 -->
      <PlanDispatchTab
        v-else-if="subTab === 'followup-plan'"
        :patients="filteredPlanPatients"
        :active-patient-id="activePatientId"
        :task-query="taskFilters.q"
        :active-task="activeTask"
        :plan-dispatch-steps="planDispatchSteps"
        :templates="availableFollowupTemplates"
        :selected-template-id="selectedFollowupTemplateId"
        :selected-template="selectedWorkflowTemplate"
        :node-previews="activePlanNodePreviews"
        :plan-day="planDay"
        :plan-day-list="planDayList"
        :plan-loading="planState.loading"
        :plan-error="planState.error"
        :saving="followupPlanSaving"
        :template-status-label="templateStatusLabel"
        :nodule-type-label="noduleTypeLabel"
        :risk-level-label="riskLevelLabel"
        :channel-label="channelLabel"
        @update-task-query="taskFilters.q = $event"
        @reset-task-filters="resetTaskFilters"
        @select-patient="createTaskForPatient"
        @recommend="recommendForActive"
        @open-workflow="goFollowupWorkflow"
        @select-template="selectFollowupTemplate"
        @update-plan-day="planDay = $event"
        @save-plan="savePlanForActiveAndBackend"
        @simulate-plan="simulatePlanToFollowup"
      />

      <!-- follow tab：患者随访聊天记录查看（三栏：患者列表 | 手机聊天 | 助手面板） -->
      <div v-else-if="subTab === 'follow'" class="follow-workbench">

        <FollowTrackingTab
          :stats="followTrackingStats"
          :flow-steps="aiFollowFlowSteps"
          :patients="followFilteredQueue"
          :selected-patient-id="followPatientId"
          :search="followSearch"
          :risk-filter="followRiskFilter"
          :stage-filter="followStageFilter"
          :stage-options="stageTabs.slice(1)"
          :patient="followPatient"
          :messages="activeTrackingMessages"
          :tracking-stats="trackingStats"
          :task-groups="trackingTaskGroups"
          :tasks="trackingTasksForPatient"
          :active-task="activeTrackingTask"
          :events="activeTrackingEvents"
          :last-touch-label="lastTouchLabel"
          :status-label="statusLabel"
          :tracking-status-label="trackingStatusLabel"
          @update-search="followSearch = $event"
          @update-risk-filter="followRiskFilter = $event"
          @update-stage-filter="followStageFilter = $event"
          @select-patient="followPatientId = $event"
          @refresh="loadFollowupTasks"
          @select-task="selectTask"
        />

        <LegacyFollowAssistantPreview
          :plan-day="planDay"
          :patient="followPatient"
          :current-assistant="currentAssistant"
          :chat-messages="simulatedAssistantChat"
          :assistants="followAssistants"
          :active-assistant="activeAssistant"
          :content-rows="followContentConfigRows"
          :generated-rows="followGeneratedRows"
          :assistant-status="assistantStatus"
          @update-active-assistant="activeAssistant = $event"
          @enable-kb="setKbEnabled($event, true)"
        />
      </div>

      <!-- review tab：报告处理主页面 -->
      <ReportReviewTab
        v-else-if="subTab === 'review'"
        :report-terms="reportTerms"
        :scenario="scenario"
        :reports="rpList"
        :filtered-reports="rpFilteredList"
        :active-report="rpActive"
        :active-id="rpActiveId"
        :search="rpSearch"
        :source="rpSource"
        :nodule="rpNodule"
        :risk="rpRisk"
        :generating-ids="reportGeneratingIds"
        @update-search="rpSearch = $event"
        @update-source="rpSource = $event"
        @update-nodule="rpNodule = $event"
        @update-risk="rpRisk = $event"
        @reset-filters="resetReportFilters"
        @select-report="rpActiveId = $event"
        @view-report="viewReport"
        @primary-action="openReportRowPrimary"
        @download-report="downloadReport"
      />

      <!-- 其它 tab（abnormal）：左侧队列 + 右侧内容 -->
      <OtherPatientTabs
        v-else
        :tab="subTab"
        :title="midTitle"
        :patients="filteredQueue"
        :active-patient="activePatient"
        :active-patient-id="activePatientId"
        :active-stage="activeStage"
        :stage-tabs="stageTabs"
        :scenario="scenario"
        :source-label="sourceLabel"
        :status-label="statusLabel"
        @set-stage="setStage"
        @select-patient="activePatientId = $event"
        @go-record="goRecord"
        @file-action="toast?.show('文件操作')"
      />

    </section>
  </div>

  <!-- 报告查看弹窗 -->
  <div v-if="rpViewVisible" class="rp-modal-mask" @click.self="closeReportView">
    <div class="rp-modal">
      <div class="rp-modal-head">
        <div class="rp-modal-title">{{ scenario.reportLabel }}</div>
        <button class="rp-modal-close" type="button" @click="closeReportView">✕</button>
      </div>
      <div class="rp-modal-body" v-html="rpViewHtml"></div>
    </div>
  </div>

  <ReportAuditModal
    v-if="rpAuditId"
    :title="reportTerms.auditModalTitle"
    :status="rpAuditStatus"
    :status-label="adviceStatusLabel(rpAuditStatus)"
    :version="rpAuditVersion"
    v-model:imaging-advice="rpAuditImagingAdvice"
    v-model:overall-advice="rpAuditOverallAdvice"
    v-model:risk-advice="rpAuditRiskAdvice"
    v-model:tongue-advice="rpAuditTongueAdvice"
    :finalizing="rpFinalizing"
    :was-reviewed="rpAuditWasReviewed"
    :approve-label="reportTerms.approveAction"
    :show-followup-next="showAuditFollowupNext"
    :followup-task="auditFollowupTask"
    :creating-followup="isCreatingReportFollowup(rpAuditId)"
    @close="closeAudit"
    @finalize="finalizeReport(rpAuditId)"
    @create-followup="createAuditFollowupTask"
    @open-followup="openReportFollowupTask(rpAuditId)"
    @copy-checkin-link="copyTaskCheckinLink(auditFollowupTask)"
  />

  <!-- 企业微信身份绑定 -->
  <div v-if="wecomModalOpen" class="rp-modal-mask" @click.self="wecomModalOpen=false">
    <div class="rp-modal wecom-modal">
      <div class="rp-modal-head">
        <div>
          <div class="rp-modal-title">绑定企业微信身份</div>
          <div class="muted" style="font-size:12px;margin-top:3px">{{ wecomBindingPatient?.name || '当前患者' }}</div>
        </div>
        <button class="rp-modal-close" type="button" @click="wecomModalOpen=false">✕</button>
      </div>
      <div class="rp-modal-body">
        <div class="wecom-form-grid">
          <label class="profile-field wide">
            <span>external_userid</span>
            <input v-model.trim="wecomForm.external_userid" placeholder="企业微信客户 external_userid">
          </label>
          <label class="profile-field wide">
            <span>userid</span>
            <input v-model.trim="wecomForm.userid" placeholder="内部员工 userid，可选">
          </label>
        </div>
        <div class="wecom-form-hint">真实企微回调拿到 external_userid 后，会用这个字段把消息、图片和打卡记录归属到患者。</div>
        <div class="wecom-modal-actions">
          <button class="btn" type="button" @click="wecomModalOpen=false">取消</button>
          <button class="primary" type="button" @click="submitWecomBind" :disabled="wecomBindingSaving">{{ wecomBindingSaving ? '保存中...' : '保存绑定' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import RecordView from './RecordView.vue'
import FollowTrackingTab from '../components/FollowTrackingTab.vue'
import LegacyFollowAssistantPreview from '../components/LegacyFollowAssistantPreview.vue'
import OtherPatientTabs from '../components/OtherPatientTabs.vue'
import PatientDetailWorkspace from '../components/PatientDetailWorkspace.vue'
import PatientQueueOverview from '../components/PatientQueueOverview.vue'
import PlanDispatchTab from '../components/PlanDispatchTab.vue'
import ReportAuditModal from '../components/ReportAuditModal.vue'
import ReportReviewTab from '../components/ReportReviewTab.vue'
import { getStoredScenario } from '../config/scenarios'
import { useFollowupContent } from '../composables/useFollowupContent'
import { useFollowupPlanning } from '../composables/useFollowupPlanning'
import { usePatientDisplay } from '../composables/usePatientDisplay'
import {
  aiActionLabel,
  patientActionLabel,
  taskStatusLabel,
  trackingStatusLabel,
  usePatientTracking
} from '../composables/usePatientTracking'
import { useReportAudit } from '../composables/useReportAudit'
import { useReportGeneration } from '../composables/useReportGeneration'
import { useReportList } from '../composables/useReportList'
import { useReportViewer } from '../composables/useReportViewer'

const router = useRouter()
const route = useRoute()
const toast = { show: (msg) => window.alert(msg) }
const scenario = computed(() => getStoredScenario())
const isCheckupScenario = computed(() => scenario.value.key === 'checkup')
const {
  channelLabel,
  noduleTypeLabel,
  planStatusLabel,
  riskLevelLabel,
  riskToneFromLevel,
  statusKey,
  statusLabel,
  taskTypeLabel,
  templateStatusLabel
} = usePatientDisplay({ scenario, isCheckupScenario })

function goFollowupWorkflow() {
  router.push('/followup-workflow')
}

const reportTerms = computed(() => {
  if (isCheckupScenario.value) {
    return {
      pending: '待处理体检报告',
      parsing: 'AI结构化中',
      parsed: '解读完成',
      toGenerate: '待生成解读',
      toReview: '待总检确认',
      abnormal: '高风险提醒',
      listTitle: '体检报告列表',
      detailTitle: '体检报告详情',
      flowTitle: '体检报告流程',
      reviewed: '已确认',
      reviewAction: '确认',
      auditAi: '确认AI建议',
      createTask: '创建复查任务',
      auditModalTitle: '确认AI解读内容',
      summaryLabel: '体检结果摘要',
      adviceLabel: 'AI复查建议',
      approveAction: '确认通过',
      flowBuild: '建档',
      flowGenerate: '生成解读',
      flowReview: '总检确认',
      flowPush: '推送患者',
    }
  }
  return {
    pending: '待处理报告',
    parsing: 'AI解析中',
    parsed: '解析完成',
    toGenerate: '待生成报告',
    toReview: '待医生复核',
    abnormal: '异常报告',
    listTitle: '报告列表',
    detailTitle: '报告详情',
    flowTitle: '处理流程',
    reviewed: '已审核',
    reviewAction: '审核',
    auditAi: '审核AI建议',
    createTask: '创建任务',
    auditModalTitle: '审核AI生成内容',
    summaryLabel: '影像解读摘要',
    adviceLabel: 'AI健康建议',
    approveAction: '审核通过',
    flowBuild: '建档',
    flowGenerate: '生成报告',
    flowReview: '人工审核',
    flowPush: '推送患者',
  }
})

// 当前子页（必须在 watch 之前声明，避免 immediate 回调引用未初始化变量）
const subTab = ref('queue')

// 子页定义（URL query.tab -> subTab）
const subTabs = [
  { key: 'queue', label: '患者队列' },
  { key: 'detail', label: '患者详情' },
  { key: 'record', label: '档案与报告' },
  { key: 'review', label: isCheckupScenario.value ? '体检报告确认' : '健康报告审核' },
  { key: 'followup-plan', label: '随访任务下发' },
  { key: 'follow', label: '执行跟踪' }
]
const allowedSubTabs = new Set(subTabs.map((t) => t.key))

watch(
  () => route.query.tab,
  (tab) => {
    const key = typeof tab === 'string' ? tab : ''
    if (allowedSubTabs.has(key)) subTab.value = key
    else subTab.value = 'queue'
  },
  { immediate: true }
)

/**
 * @isdoc
 * @description 统一切换患者管理子页（写入 URL，并立即更新本地 subTab）
 * @param {string} key
 * @returns {void}
 */
function setSubTab(key) {
  const k = String(key || '').trim()
  if (!allowedSubTabs.has(k)) return
  subTab.value = k
  if (route.name !== 'patient') return
  if (route.query.tab === k) return
  router.replace({ query: { ...route.query, tab: k } })
}

const activeStage = ref('all')
const activePatientId = ref('p1')
const recordPatient = ref(null)
const followPatientId = ref('p1')
const followSearch = ref('')
const followRiskFilter = ref('')
const followStageFilter = ref('')
const patientEditMode = ref(false)
const adviceGenerating = ref(false)
const tongueSubmitting = ref(false)
const tongueSyncing = ref(false)
const activeAssistant = ref('hlp')
const wecomModalOpen = ref(false)
const wecomBindingPatientId = ref('')
const wecomBindingSaving = ref(false)
const wecomForm = reactive({
  external_userid: '',
  userid: '',
})

const followupPlanSaving = ref(false)
const {
  activePlanNodePreviews,
  activePlanNodes,
  availableFollowupTemplates,
  currentPlanRows,
  followupKnowledgeItems,
  followupRecommendation,
  followupTemplates,
  loadFollowupPlanningConfig,
  loadPlan,
  planDay,
  planDayList,
  planState,
  selectFollowupTemplate,
  selectedFollowupTemplateId,
  selectedWorkflowTemplate,
} = useFollowupPlanning({
  apiJson,
  aiActionLabel,
  patientActionLabel,
  taskTypeLabel,
})

// 患者队列（必须提前声明，避免 watcher immediate 引用 TDZ）
const queue = ref([])

// 健康管理任务工作台（筛选 + 列表 + 详情）
const taskFilters = ref({
  q: '',
  risk: '',
  channel: '',
  owner: '',
  source: '',
  nodule: '',
  status: '',
})

const followTasks = ref([])
const activeTaskId = ref('')

const activeTask = computed(() => (followTasks.value || []).find((t) => t.id === activeTaskId.value) || null)
const followPatient = computed(() => queue.value.find(p => p.id === followPatientId.value) || queue.value[0])
const {
  activeTrackingEvents,
  activeTrackingMessages,
  activeTrackingTask,
  previewTasksFromPatient,
  trackingStats,
  trackingTaskGroups,
  trackingTasksForPatient,
} = usePatientTracking({ followPatient, followTasks, activeTaskId, planDay })

const latestRecordLabel = computed(() => {
  const records = activePatient.value?.workspaceRecords || []
  const latest = records[0]
  if (!latest) return '暂无档案'
  return latest.record_code || latest.created_at || `档案 #${latest.id}`
})

const activePlanLabel = computed(() => {
  const plans = activePatient.value?.workspacePlans || []
  const active = plans.find((plan) => plan.status === 'active') || plans[0]
  if (!active) return '待下发'
  return `${planStatusLabel(active.status)} · ${cycleLabelFromDays(active.cycle_days)}`
})

const taskExecutionSummary = computed(() => {
  const tasks = activePatient.value?.workspaceTasks || []
  if (!tasks.length) return '暂无任务'
  const open = tasks.filter((task) => !['completed', 'cancelled'].includes(task.status)).length
  const alert = tasks.filter((task) => task.abnormal_flag || task.status === 'alert').length
  if (alert) return `${alert} 个异常待处理`
  return open ? `${open} 个进行中` : '全部完成'
})

const filteredPlanPatients = computed(() => {
  const q = String(taskFilters.value.q || '').trim()
  const risk = String(taskFilters.value.risk || '')
  const owner = String(taskFilters.value.owner || '').trim()
  return (planPatients.value || []).filter((p) => {
    if (q) {
      const hay = `${p.name} ${p.phoneMasked}`.toLowerCase()
      if (!hay.includes(q.toLowerCase())) return false
    }
    if (risk && p.risk !== risk) return false
    if (owner && !String(p.owner || '').includes(owner)) return false
    return true
  })
})

// 初始：把“已存在 planTask 的患者”放进任务队列（示意）
watch(
  () => subTab.value,
  (k) => {
    if (k !== 'followup-plan') return
    if ((followTasks.value || []).length) return
    const seeded = (queue.value || [])
      .filter((p) => p?.planTask)
      .slice(0, 8)
      .flatMap((p) => previewTasksFromPatient(p))
    followTasks.value = seeded
    if (seeded[0]) selectTask(seeded[0].id)
  },
  { immediate: true }
)

watch(
  () => subTab.value,
  (k) => {
    if (k !== 'follow') return
    loadFollowupTasks()
  },
  { immediate: true }
)

/**
 * @isdoc
 * @description 重置筛选条件
 * @returns {void}
 */
function resetTaskFilters() {
  taskFilters.value = { q: '', risk: '', channel: '', owner: '' }
}

/**
 * @isdoc
 * @description 选择任务并联动患者
 * @param {string} id
 * @returns {void}
 */
function selectTask(id) {
  activeTaskId.value = id
  const t = (followTasks.value || []).find((x) => x.id === id)
  if (t?.patientId) {
    activePatientId.value = t.patientId
    followPatientId.value = t.patientId
  }
}

/**
 * @isdoc
 * @description 由患者+表单生成一条任务
 * @param {any} p
 * @returns {any}
 */
function makeTaskFromPatient(p) {
  const id = `t_${Date.now()}_${Math.random().toString(16).slice(2, 6)}`
  const planNode = (p.planTask?.nodes || [])[0] || {}
  const message = planNode.message_template || p.planTask?.note || '请按计划完成今日健康管理任务。'
  return {
    id,
    patientId: p.id,
    patientName: p.name,
    gender: p.gender,
    age: p.age,
    phoneMasked: p.phoneMasked,
    nodules: p.nodules,
    risk: p.risk,
    riskTone: p.riskTone,
    owner: p.owner || '',
    channel: draft.value.channel,
    cycle: draft.value.cycle,
    reminder: draft.value.reminder,
    day: planDay.value,
    time: planNode.send_time || '09:00',
    scheduledAt: '模拟排程',
    status: p.owner ? 'scheduled' : 'pending',
    node: planNode,
    message,
    patientAction: patientActionLabel(planNode.patient_action),
    aiAction: aiActionLabel(planNode.ai_action),
    kbSnapshot: JSON.parse(JSON.stringify(draft.value.kbEnabled || {})),
    logs: [{ at: '现在', by: '医生/运营', action: 'task_created_from_patient_plan', note: `Day ${planDay.value.replace('day', '')} · ${draft.value.channel} · ${draft.value.cycle}` }],
  }
}

/**
 * @isdoc
 * @description 新建任务入口（基于当前患者）
 * @returns {void}
 */
function openNewTaskFromActive() {
  // 已移除“新建任务”按钮入口：任务仅从患者行“任务下发”进入
}

/**
 * @isdoc
 * @description 从患者行创建任务并进入详情
 * @param {any} p
 * @returns {void}
 */
function createTaskForPatient(p) {
  if (!p?.id) return
  activePatientId.value = p.id
  const t = makeTaskFromPatient(p)
  followTasks.value = [t, ...(followTasks.value || [])]
  selectTask(t.id)
  if (p._apiId) {
    ensureFollowupRecommendation(p).catch((e) => {
      toast?.show(e.message || '知识库推荐失败，已保留本地草稿')
    })
  }
  // 左侧固定展示患者列表
}

/**
 * @isdoc
 * @description 任务流程节点（示意）
 * @param {any} t
 * @returns {{k:string,label:string,state:'todo'|'doing'|'done'}[]}
 */
function taskFlowNodes(t) {
  const s = t?.status || 'draft'
  const at = (k) => {
    if (s === 'draft') return k === 'assign' ? 'doing' : 'todo'
    if (s === 'assigned') return (k === 'assign' ? 'done' : k === 'execute' ? 'doing' : 'todo')
    if (s === 'executing') return (k === 'assign' ? 'done' : k === 'execute' ? 'done' : k === 'review' ? 'doing' : 'todo')
    if (s === 'review') return (k === 'assign' || k === 'execute' ? 'done' : k === 'review' ? 'done' : k === 'done' ? 'doing' : 'todo')
    if (s === 'done') return (k === 'assign' || k === 'execute' || k === 'review' || k === 'done') ? 'done' : 'todo'
    return 'todo'
  }
  return [
    { k: 'assign', label: '分派', state: at('assign') },
    { k: 'execute', label: '执行', state: at('execute') },
    { k: 'review', label: '复核', state: at('review') },
    { k: 'done', label: '闭环', state: at('done') },
  ]
}

/**
 * @isdoc
 * @description 推进任务状态并写入日志
 * @param {'assign'|'execute'|'review'|'done'} action
 * @returns {void}
 */
function advanceTask(action) {
  const t = activeTask.value
  if (!t) return
  let nextStatus = t.status
  if (action === 'assign') nextStatus = 'assigned'
  if (action === 'execute') nextStatus = 'executing'
  if (action === 'review') nextStatus = 'review'
  if (action === 'done') nextStatus = 'done'

  const note = window.prompt('补充说明（可选）：', '') || ''
  followTasks.value = (followTasks.value || []).map((x) => {
    if (x.id !== t.id) return x
    const y = { ...x, status: nextStatus }
    y.logs = Array.isArray(y.logs) ? y.logs : []
    y.logs.unshift({ at: '现在', by: '操作员', action: `状态变更：${taskStatusLabel(nextStatus)}`, note })
    return y
  })
}

onMounted(() => {
  loadPlan()
  loadFollowupPlanningConfig()
  loadPatients()
  loadReports()
})

const kbUi = ref({
  editorOpen: false,
  editorKey: '',
  editorLabel: '',
  editorText: '',
  editorCategory: 'script',
  editorTaskType: '',
  editorRiskLevel: '',
  managerOpen: false,
  drawerOpen: false,
  drawerGroup: 'diet',
  drawerQuery: '',
  drawerActiveKey: '',
})

/**
 * @isdoc
 * @description 将表单草稿应用到当前患者计划（保存到内存）
 * @returns {void}
 */
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
  // 也同步写入 plan（用于后续下发任务）
  savePlanForActive()
  p.timeline = Array.isArray(p.timeline) ? p.timeline : []
  p.timeline.push({ at: '现在', tone: 'b', text: `生成健康管理任务：Day ${planDay.value.replace('day','')}`, meta: '已保存' })

  // 同步生成/更新任务队列（工作台左侧列表）
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

/**
 * @isdoc
 * @description 保存并激活任务计划，生成后续提醒/打卡任务
 * @returns {void}
 */
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

const aiFollowFlowSteps = [
  { icon: '患', title: '患者画像', sub: '病种/风险/阶段' },
  { icon: '策', title: '助手策略', sub: '确定输出倾向' },
  { icon: '库', title: '知识匹配', sub: '匹配内容库' },
  { icon: '文', title: '生成内容', sub: '摘要/任务/提醒' },
  { icon: '发', title: '患者预览', sub: '预览后下发' },
]

/**
 * @isdoc
 * @description 将当前选择的 Day 与计划摘要保存到当前患者对象（mock：写入内存）
 * @returns {void}
 */
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

/**
 * @isdoc
 * @description 保存患者表单（mock：写入时间线，提示已保存）
 * @returns {void}
 */
function savePatientForm() {
  const p = activePatient.value
  if (!p) return
  p.timeline = Array.isArray(p.timeline) ? p.timeline : []
  p.timeline.push({ at: '现在', tone: 'b', text: '更新患者信息', meta: '已保存' })
}

/**
 * @isdoc
 * @description 下发任务：状态切换为 follow，并进入执行跟踪页
 * @returns {void}
 */
async function startAiFollowup() {
  const p = activePatient.value
  if (!p) return
  if (p._apiId) {
    await simulatePlanToFollowup()
    return
  }
  // 先保存一次，保证计划和内容包存在
  applySelectedTemplateToPatient()

  p.stage = 'follow'
  p.stageLabel = '任务执行中'
  p.serviceStatus = '任务执行中'
  p.nextStep = '按计划执行任务'

  p.timeline = Array.isArray(p.timeline) ? p.timeline : []
  p.timeline.push({ at: '现在', tone: 'g', text: '下发健康管理任务', meta: `Day ${planDay.value.replace('day', '')}` })

  // 在聊天里保留一条任务提示（兼容原型预览数据）
  p.chat = Array.isArray(p.chat) ? p.chat : []
  p.chat.push({ from: 'ai', text: `已下发健康管理任务（Day ${planDay.value.replace('day', '')}），将按任务模板推送提醒和打卡入口。` })
  p.chat.push({ type: 'card', ico: '🧾', title: `查看健康管理任务（Day ${planDay.value.replace('day', '')}）`, sub: '任务已生成 · 点击查看' })

  followPatientId.value = p.id
  setSubTab('follow')
}

const aiAssistants = [
  {
    key: 'hlp', name: 'AI名医数字分身', shortName: '名医分身', ico: '名', bg: '#eef5ff', color: '#155eef',
    image: '/images/ai-assistants/demo01.png',
    tagline: '专家解读 · 权威科普 · 复查建议，为患者提供专业级随访指导',
    capabilities: ['专家知识问答', '报告重点解读', '复查建议生成', '就诊提醒判断', '阶段性健康规划'],
    workflow: ['患者问题', 'AI专家解读', '生成建议', '医生确认', '推送患者'],
    stats: { reach: 89, read: 76, reply: 34, transfer: 3 },
    desc: '阶段性健康规划、高风险路径建议、专家级随访指导',
    scene: '高风险随访 · 专家路径规划',
    tpl: '您好，根据您的检查结果，我为您制定了个性化随访路径，请查阅并按计划执行。',
    execLog: [
      { at: '08:30', action: '推送高风险随访路径', note: '肺结节高风险 · 3个月复查方案', state: '已读', tone: 'g' },
      { at: '昨天 09:00', action: '发送阶段性健康建议', note: '第2阶段随访建议', state: '已送达', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI名医数字分身，将为您提供专业的随访指导。' },
      { from: 'ai', text: '根据您的检查结果，肺部磨玻璃结节 8mm，建议按高风险路径随访：3个月复查胸部CT，同时注意以下事项。' },
      { type: 'card', ico: '🩺', title: '查看个性化随访路径', sub: '高风险 · 专家级随访方案' },
      { from: 'patient', text: '请问我需要做什么准备？' },
      { from: 'ai', text: '复查前无需特殊准备，建议穿宽松衣物，避免佩戴金属饰品。如有症状变化请提前告知医生。' }
    ]
  },
  {
    key: 'health', name: 'AI健康管理师', shortName: '健康管理', ico: '健', bg: '#ecfff3', color: '#16a34a',
    image: '/images/ai-assistants/demo02.png',
    tagline: '随访提醒 · 复查计划 · 健康档案，全程陪伴患者健康管理',
    capabilities: ['任务模板下发', '复查提醒推送', '健康档案管理', '日常打卡', '健康报告解读'],
    workflow: ['档案建立', '随访任务下发', '定期提醒', '打卡收集', '报告更新'],
    stats: { reach: 124, read: 108, reply: 67, transfer: 2 },
    desc: '随访提醒、复查计划、健康档案管理',
    scene: '结节随访 · 复查提醒',
    tpl: '您好，您的健康管理任务已更新，请按时完成打卡和复查提醒。如有不适请及时联系我们。',
    execLog: [
      { at: '09:20', action: '发送复查提醒', note: '3个月复查胸部CT', state: '已送达', tone: 'g' },
      { at: '昨天 15:00', action: '发送随访问卷', note: '症状自评问卷', state: '已读', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，您的体检报告已完成解读，以下是您的健康管理报告摘要，请查阅。' },
      { type: 'card', ico: '📋', title: '查看健康管理报告', sub: '健康管理报告 · 点击查看详情' },
      { from: 'ai', text: '根据您的检查结果，建议您 3 个月后复查胸部 CT。如有持续咳嗽或胸痛，请及时就医。' },
      { from: 'patient', text: '好的，我知道了，谢谢。' },
      { from: 'ai', text: '已为您创建复查提醒，届时将通过小程序和企业微信通知您。祝您健康！' }
    ]
  },
  {
    key: 'pharma', name: 'AI药师', shortName: 'AI药师', ico: '药', bg: '#fff7ed', color: '#f97316',
    image: '/images/ai-assistants/demo03.png',
    tagline: '用药核对 · 服药提醒 · 药物相互作用，守护患者用药安全',
    capabilities: ['用药计划核对', '服药定时提醒', '药物相互作用提示', '不良反应询问', '漏服处理建议'],
    workflow: ['用药档案', '服药提醒', '依从性跟踪', '异常上报', '医生确认'],
    stats: { reach: 56, read: 49, reply: 28, transfer: 1 },
    desc: '用药核对、服药提醒、药物相互作用提示',
    scene: '用药管理 · 服药提醒',
    tpl: '您好，您的用药计划已更新，请按时服药，如有不适请及时告知。',
    execLog: [
      { at: '08:00', action: '发送晨间服药提醒', note: '阿司匹林 100mg', state: '已读', tone: 'g' },
      { at: '昨天 20:00', action: '发送晚间服药提醒', note: '降压药', state: '已送达', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI药师，负责协助您管理用药计划。' },
      { from: 'ai', text: '根据您的档案，您目前正在服用阿司匹林和降压药，请注意按时服药。阿司匹林建议饭后服用，降压药建议每天固定时间服用。' },
      { type: 'card', ico: '💊', title: '查看用药计划', sub: '点击查看完整用药清单' },
      { from: 'patient', text: '我最近忘记吃药了，有影响吗？' },
      { from: 'ai', text: '偶尔漏服影响不大，但请尽量保持规律服药。如果连续漏服超过 3 天，建议联系您的主治医生。' }
    ]
  },
  {
    key: 'chronic', name: 'AI慢病管理师', shortName: '慢病管理', ico: '慢', bg: '#f5f3ff', color: '#8b5cf6',
    image: '/images/ai-assistants/demo04.png',
    tagline: '合并慢病评估 · 干预方案 · 长期管理，助力慢病患者全程管控',
    capabilities: ['慢病风险评估', '血压血糖监测提醒', '干预方案推送', '复诊提醒', '异常指标预警'],
    workflow: ['慢病建档', '指标监测', '异常预警', '干预推送', '复诊跟踪'],
    stats: { reach: 78, read: 65, reply: 41, transfer: 5 },
    desc: '合并慢病评估、干预方案、长期管理',
    scene: '慢病干预 · 综合管理',
    tpl: '您好，根据您的慢病档案，为您推送本周健康管理建议，请参考执行。',
    execLog: [
      { at: '09:00', action: '推送慢病管理建议', note: '高血压合并结节随访', state: '已读', tone: 'g' },
      { at: '前天 10:00', action: '发送血压监测提醒', note: '请记录今日血压', state: '未回复', tone: 'o' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI慢病管理师，负责协助您管理合并慢性疾病。' },
      { from: 'ai', text: '根据您的档案，您合并有高血压，建议每天早晨测量血压并记录，目标控制在 130/80 mmHg 以下。' },
      { type: 'card', ico: '📊', title: '查看慢病管理方案', sub: '高血压 · 个性化管理计划' },
      { from: 'patient', text: '我最近血压有点高，需要调整用药吗？' },
      { from: 'ai', text: '血压偏高时请先记录数值，如连续 3 天超过 140/90 mmHg，建议联系主治医生评估是否需要调整用药方案。' }
    ]
  },
  {
    key: 'psych', name: 'AI心理咨询师', shortName: '心理咨询', ico: '心', bg: '#fff1f2', color: '#dc2626',
    image: '/images/ai-assistants/demo05.png',
    tagline: '检后焦虑评估 · 情绪疏导 · 心理支持，陪伴患者走过每个难关',
    capabilities: ['焦虑情绪评估', '情绪疏导对话', '睡眠质量询问', '压力干预建议', '必要时转人工'],
    workflow: ['情绪评估', 'AI疏导', '持续关怀', '风险识别', '人工介入'],
    stats: { reach: 43, read: 38, reply: 29, transfer: 8 },
    desc: '检后焦虑评估、情绪疏导、心理支持',
    scene: '心理关怀 · 焦虑干预',
    tpl: '您好，检查结果出来后有任何担忧都可以告诉我，我们一起面对。',
    execLog: [
      { at: '10:00', action: '发送心理关怀问候', note: '检后焦虑评估', state: '未回复', tone: 'o' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI心理咨询师，收到检查报告后心情如何？有任何担忧都可以告诉我。' },
      { from: 'patient', text: '我很担心，一直在想会不会是癌症。' },
      { from: 'ai', text: '您的担心完全可以理解，这是很正常的反应。目前的检查结果需要进一步随访观察，并不代表一定是恶性病变。' },
      { from: 'ai', text: '建议您：① 保持规律作息；② 避免过度查阅网络信息；③ 如果焦虑影响到日常生活，可以申请专业心理咨询。我们会一直陪伴您。' },
      { from: 'patient', text: '谢谢，我会尽量放松的。' }
    ]
  },
  {
    key: 'rehab', name: 'AI运动康复师', shortName: '运动康复', ico: '动', bg: '#ecfdf5', color: '#059669',
    image: '/images/ai-assistants/demo06.png',
    tagline: '个性化运动处方 · 康复计划 · 运动监测，科学运动助力康复',
    capabilities: ['运动处方制定', '运动计划推送', '运动依从性跟踪', '运动禁忌提醒', '康复进度评估'],
    workflow: ['健康评估', '处方制定', '计划推送', '依从跟踪', '效果评估'],
    stats: { reach: 67, read: 58, reply: 32, transfer: 1 },
    desc: '个性化运动处方、康复计划、运动监测',
    scene: '运动干预 · 康复管理',
    tpl: '您好，您的本周运动计划已更新，请按计划执行，循序渐进。',
    execLog: [
      { at: '18:30', action: '推送运动计划', note: '低强度快走 20min', state: '已读', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI运动康复师，根据您的健康状况，为您制定了本周运动计划：' },
      { from: 'ai', text: '建议：每天快走 20-30 分钟，心率控制在 100-120 次/分钟，避免剧烈运动。运动前后做好热身和拉伸。' },
      { type: 'card', ico: '🏃', title: '查看本周运动计划', sub: '低强度有氧 · 个性化方案' },
      { from: 'patient', text: '我最近膝盖有点不舒服，还能运动吗？' },
      { from: 'ai', text: '膝盖不适时建议暂停快走，改为游泳或骑固定自行车等低冲击运动。如症状持续请就医检查。' }
    ]
  },
  {
    key: 'lifestyle', name: 'AI健康生活方式规划师', shortName: '生活规划', ico: '活', bg: '#fefce8', color: '#ca8a04',
    image: '/images/ai-assistants/demo07.png',
    tagline: '饮食 · 作息 · 生活习惯综合建议，全方位优化健康生活方式',
    capabilities: ['饮食方案推荐', '作息规律建议', '生活习惯干预', '营养摄入指导', '健康目标设定'],
    workflow: ['生活评估', '方案制定', '建议推送', '习惯跟踪', '方案调整'],
    stats: { reach: 92, read: 81, reply: 44, transfer: 0 },
    desc: '饮食、作息、生活习惯综合建议',
    scene: '生活方式干预 · 综合规划',
    tpl: '您好，根据您的健康状况，为您推荐本周生活方式建议，请参考执行。',
    execLog: [
      { at: '12:00', action: '推送饮食建议', note: '低盐低脂食谱', state: '已读', tone: 'g' },
      { at: '昨天 18:00', action: '推送作息建议', note: '规律作息提醒', state: '未读', tone: 'o' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI健康生活方式规划师，根据您的体检结果，为您推荐本周生活方式建议：' },
      { from: 'ai', text: '饮食：① 减少高盐食物；② 增加蔬菜水果；③ 主食以粗粮为主。作息：建议每天 22:30 前入睡，保证 7-8 小时睡眠。' },
      { type: 'card', ico: '🥗', title: '查看本周生活方式建议', sub: '饮食 · 作息 · 习惯综合方案' },
      { from: 'patient', text: '我可以吃海鲜吗？' },
      { from: 'ai', text: '可以适量食用，建议每周 1-2 次，选择清蒸或水煮方式，避免油炸。如有痛风史请减少贝类摄入。' }
    ]
  },
  {
    key: 'tcm', name: 'AI中医药膳师', shortName: '中医药膳', ico: '膳', bg: '#fdf4ff', color: '#a21caf',
    image: '/images/ai-assistants/demo08.png',
    tagline: '中医体质辨识 · 药膳食疗方案 · 调理建议，传统智慧守护健康',
    capabilities: ['体质辨识分析', '药膳食谱推荐', '食疗方案制定', '禁忌食物提醒', '调理进度跟踪'],
    workflow: ['体质辨识', '方案制定', '食谱推送', '调理跟踪', '效果评估'],
    stats: { reach: 51, read: 44, reply: 26, transfer: 0 },
    desc: '中医体质辨识、药膳食疗方案、调理建议',
    scene: '中医调理 · 药膳食疗',
    tpl: '您好，根据您的中医体质辨识结果，为您推荐本周药膳食疗方案，请参考执行。',
    execLog: [
      { at: '12:00', action: '推送药膳食谱', note: '晚餐控糖食谱', state: '已读', tone: 'g' },
      { at: '前天 09:00', action: '发送体质调理建议', note: '气虚体质调理方案', state: '已送达', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI中医药膳师，根据您的体质辨识结果，您属于气虚质，建议以补气健脾为主。' },
      { from: 'ai', text: '推荐本周药膳：① 山药薏米粥（健脾益气）；② 黄芪炖鸡汤（补气固表）；③ 红枣枸杞茶（养血安神）。' },
      { type: 'card', ico: '🍵', title: '查看本周药膳食谱', sub: '气虚质 · 补气健脾方案' },
      { from: 'patient', text: '我可以喝绿茶吗？' },
      { from: 'ai', text: '气虚体质建议少喝绿茶，绿茶性凉，容易伤脾胃。可以改喝红茶或普洱茶，温性更适合您的体质。' }
    ]
  },
  {
    key: 'welfare', name: 'AI健康福利官', shortName: '健康福利', ico: '福', bg: '#f0fdf4', color: '#15803d',
    image: '/images/ai-assistants/demo09.png',
    tagline: '权益匹配 · 服务说明 · 复查提醒，让每位患者享受应有的健康权益',
    capabilities: ['权益匹配推送', '服务说明生成', '复查周期提醒', '触达状态跟踪', '人工补触达'],
    workflow: ['权益匹配', 'AI说明', '推送患者', '状态跟踪', '人工补触达'],
    stats: { reach: 38, read: 33, reply: 19, transfer: 1 },
    desc: '健康权益提醒、增值服务推送、福利兑换',
    scene: '权益提醒 · 福利服务',
    tpl: '您好，您有新的健康权益待使用，请查阅并及时兑换，避免过期。',
    execLog: [
      { at: '09:05', action: '推送健康权益提醒', note: '本月免费复查名额', state: '已读', tone: 'g' },
      { at: '前天 10:00', action: '推送福利兑换提醒', note: '健康礼包待领取', state: '未读', tone: 'o' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI健康福利官，为您提供健康权益管理服务。' },
      { from: 'ai', text: '您本月有 1 次免费复查名额，有效期至 2026-04-30，请尽快预约使用，避免过期。' },
      { type: 'card', ico: '🎁', title: '查看我的健康权益', sub: '本月剩余权益 · 点击查看' },
      { from: 'patient', text: '怎么预约免费复查？' },
      { from: 'ai', text: '您可以点击上方卡片进入权益中心，选择"免费复查"后按提示预约即可。如需帮助请随时联系我。' }
    ]
  },
]

const followAssistants = computed(() => {
  if (!isCheckupScenario.value) return aiAssistants
  const overrides = {
    hlp: {
      name: 'AI总检医生助手', shortName: '总检解读', ico: '总',
      tagline: '体检结论解读 · 风险分层 · 复查建议，为患者提供清晰的检后管理指引',
      capabilities: ['体检结论解读', '风险分层说明', '复查建议生成', '转诊提醒判断', '专项筛查规划'],
      scene: '体检后解读 · 高风险路径规划',
      tpl: '您好，您的体检报告已完成解读，请查看重点异常项和复查安排。',
      chat: [
        { from: 'ai', text: '您好，我是AI总检医生助手，已根据您的体检结果整理重点异常项。' },
        { from: 'ai', text: '本次重点关注肺部结节与甲状腺结节，建议按风险等级完成复查或报告解读。' },
        { type: 'card', ico: '报', title: '查看体检解读报告', sub: '异常项汇总 · 复查建议 · 风险说明' },
        { from: 'patient', text: '我需要马上去医院吗？' },
        { from: 'ai', text: '当前建议先完成复查预约和总检确认，如出现持续咳嗽、胸痛等症状，请提前联系医生。' }
      ]
    },
    health: {
      name: 'AI健康管理师', shortName: '检后管理', ico: '管',
      tagline: '报告解读提醒 · 复查预约 · 健康档案，全程衔接体检后管理',
      capabilities: ['复查计划制定', '报告解读提醒', '健康档案管理', '症状自评问卷', '异常指标跟踪'],
      scene: '检后管理 · 复查提醒',
      tpl: '您好，您的体检后管理计划已更新，请按时完成报告解读和复查。',
      chat: [
        { from: 'ai', text: '您好，您的体检解读报告已生成，以下是今日需要完成的事项。' },
        { type: 'card', ico: '复', title: '复查预约提醒', sub: '3个月胸部CT · 6个月甲状腺超声' },
        { from: 'ai', text: '建议您先确认报告解读结果，并根据风险等级完成复查预约。' },
        { from: 'patient', text: '好的，我今天看一下。' },
        { from: 'ai', text: '已为您保留提醒入口，临近复查日期会再次通知。' }
      ]
    },
    pharma: {
      name: 'AI复查预约助手', shortName: '复查预约', ico: '约',
      tagline: '复查项目匹配 · 预约提醒 · 转诊建议，提升体检后闭环效率',
      capabilities: ['复查项目匹配', '预约时间提醒', '转诊科室建议', '检查注意事项', '到检状态跟踪'],
      scene: '复查预约 · 转诊衔接',
      tpl: '您好，您的复查项目已匹配，请选择合适时间完成预约。',
    },
    chronic: {
      name: 'AI异常指标管理师', shortName: '指标管理', ico: '指',
      tagline: '异常指标跟踪 · 慢病风险评估 · 干预建议，帮助患者理解体检异常',
      capabilities: ['异常指标解释', '慢病风险评估', '指标复测提醒', '生活方式建议', '趋势跟踪'],
      scene: '异常指标 · 趋势管理',
      tpl: '您好，本次体检有部分指标需要关注，已为您整理复测和干预建议。',
    },
    psych: {
      name: 'AI检后关怀助手', shortName: '检后关怀', ico: '关',
      tagline: '检后焦虑评估 · 报告疑问收集 · 人工转接，降低患者等待期焦虑',
      capabilities: ['焦虑情绪评估', '报告疑问收集', '解读预约提醒', '人工转接', '持续关怀'],
      scene: '检后关怀 · 报告疑问',
      tpl: '您好，如果您对体检结果有疑问，可以先告诉我，我会协助整理给健康管理师。',
    },
    rehab: {
      name: 'AI生活方式干预师', shortName: '生活干预', ico: '活',
      tagline: '饮食运动建议 · 体重管理 · 生活方式跟踪，承接体检后健康改善',
      capabilities: ['饮食建议', '运动计划', '体重管理', '睡眠建议', '习惯跟踪'],
      scene: '体检后改善 · 生活方式干预',
      tpl: '您好，根据您的体检结果，为您推荐本周生活方式改善建议。',
    },
  }
  return aiAssistants
    .filter((a) => ['hlp', 'health', 'pharma', 'chronic', 'psych', 'rehab'].includes(a.key))
    .map((a) => ({ ...a, ...(overrides[a.key] || {}) }))
})

const currentAssistant = computed(() => followAssistants.value.find(a => a.key === activeAssistant.value) || followAssistants.value[0])
const {
  draft,
  followContentConfigRows,
  followGeneratedRows,
  getKbText,
  pickIntro,
  planQuick,
  setKbEnabled,
  simulatedAssistantChat,
} = useFollowupContent({
  activeAssistant,
  currentAssistant,
  currentPlanRows,
  followPatient,
  followupKnowledgeItems,
  isCheckupScenario,
  planDay,
})

const {
  buildReportPreviewHtml,
  loadReports,
  makeReportFlow,
  resetReportFilters,
  rpActive,
  rpActiveId,
  rpFilteredList,
  rpList,
  rpLoaded,
  rpNodule,
  rpRisk,
  rpSearch,
  rpSource,
} = useReportList({
  isCheckupScenario,
  noduleTypeLabel,
  reportTerms,
  riskLevelLabel,
  riskToneFromLevel,
  scenario,
  sourceLabel,
  toast,
})
const {
  generateReportJob,
  isGenerating: isReportGenerating,
  markGenerating: markReportGenerating,
  reportGeneratingIds,
  unmarkGenerating: unmarkReportGenerating,
} = useReportGeneration({ apiJson })

const followFilteredQueue = computed(() => {
  const taskPatientIds = new Set((followTasks.value || []).map((t) => String(t.patientId)))
  return queue.value.filter((p) => statusKey(p) === 'follow' || taskPatientIds.has(String(p.id))).filter(p => {
    const s = followSearch.value.trim().toLowerCase()
    if (s && !p.name.toLowerCase().includes(s) && !p.phoneMasked.includes(s)) return false
    if (followRiskFilter.value && p.risk !== followRiskFilter.value) return false
    if (followStageFilter.value && statusKey(p) !== followStageFilter.value) return false
    return true
  })
})

const followTrackingStats = computed(() => {
  const list = queue.value || []
  const followList = list.filter((p) => statusKey(p) === 'follow')
  return {
    runningPatients: followList.length,
    highRisk: followList.filter((p) => p.riskTone === 'r').length,
    midRisk: followList.filter((p) => p.riskTone === 'o').length,
    lowRisk: followList.filter((p) => p.riskTone === 'g').length,
    unconfigured: followList.filter((p) => !p.planTask || !p.planTask.day).length,
    configured: followList.filter((p) => p.planTask && p.planTask.day).length,
  }
})

watch(
  () => followPatientId.value,
  () => {
    const d = followPatient.value?.planTask?.day
    if (typeof d === 'string' && d.startsWith('day')) planDay.value = d
    const firstTask = trackingTasksForPatient.value[0]
    if (firstTask && !trackingTasksForPatient.value.some((t) => t.id === activeTaskId.value)) {
      activeTaskId.value = firstTask.id
    }
  }
)

const reportFollowupCreatingId = ref('')
const reportFollowupTaskMap = ref({})
const {
  closeAudit,
  currentAuditSections,
  openAudit,
  rpAuditId,
  rpAuditImagingAdvice,
  rpAuditOverallAdvice,
  rpAuditPara1,
  rpAuditPara2,
  rpAuditRiskAdvice,
  rpAuditStatus,
  rpAuditTongueAdvice,
  rpAuditVersion,
  rpAuditWasReviewed,
  showAuditFollowupNext,
} = useReportAudit({
  apiJson,
  loadReportFollowupTask,
  normalizeAdvicePayload,
  reportTerms,
  rpActiveId,
})
const auditFollowupTask = computed(() => existingReportFollowupTask(rpAuditId.value, null))
const {
  closeReportView,
  downloadReport,
  rpViewHtml,
  rpViewVisible,
  viewReport,
} = useReportViewer({
  apiJson,
  buildReportPreviewHtml,
  reportDbStatusLabel,
  rpAuditPara1,
  rpAuditPara2,
  rpList,
  toast,
})

async function finalizeReport(reportId) {
  if (!reportId) return
  rpFinalizing.value = true
  try {
    if (!String(reportId || '').startsWith('r')) {
      await apiJson(`/api/b/reports/${reportId}/advice`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: rpAuditImagingAdvice.value,
          sections: currentAuditSections(),
          preserve_history: true
        })
      })
      const data = await apiJson(`/api/b/reports/${reportId}/advice/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: rpAuditImagingAdvice.value,
          summary: rpAuditOverallAdvice.value,
          sections: currentAuditSections()
        })
      })
      const r = rpList.value.find(x => x.id === reportId)
      if (r) {
        r.reportStatus = '已审核'
        r.aiStatus = '已完成'
        r.summary = rpAuditOverallAdvice.value
        r.aiReadSummary = rpAuditImagingAdvice.value
        r.flow = makeReportFlow(r.uploadAt, true)
      }
      rpAuditStatus.value = data.advice?.status || 'archived'
      rpAuditVersion.value = data.advice?.version || rpAuditVersion.value
      rpAuditWasReviewed.value = true
      rpLoaded.value = false
      await loadReports()
      await loadReportFollowupTask(reportId)
      return
    }
  } catch (e) {
    console.error('审核报告失败', e)
    if (!String(reportId || '').startsWith('r')) {
      toast?.show(e.message || '审核失败')
      return
    }
  } finally {
    rpFinalizing.value = false
  }

  try {
    const r = rpList.value.find(x => x.id === reportId)
    if (r) r.reportStatus = '已审核'
    rpAuditId.value = ''
  } finally {
    rpFinalizing.value = false
  }
}

async function approveReport(reportId) {
  if (!reportId) return
  rpFinalizing.value = true
  try {
    // 审核AI建议：调用 approve-all 接口，只批准建议，不触发LLM重新生成
    const res = await fetch(`/api/b/reports/${reportId}/recommendations/approve-all`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await res.json()
    if (data.success) {
      // 本地更新状态
      const r = rpList.value.find(x => x.id === reportId)
      if (r) r.reportStatus = '已审核'
    } else {
      alert(data.message || '审核失败')
    }
  } catch (e) {
    console.error('审核失败', e)
  } finally {
    rpFinalizing.value = false
  }
}

async function openReportRowPrimary(r) {
  if (!r) return
  if (r.isReportPlaceholder) {
    await generateReportForReportRow(r)
    return
  }
  openAudit(r)
}

async function generateReportForReportRow(r) {
  if (!r?.rawRecordId) {
    toast?.show('该患者还没有健康档案，请先建档后再生成报告')
    const patient = queue.value.find(p => p._apiId === r?.rawPatientId)
    if (patient) goRecord(patient)
    return
  }

  const generateKey = r.rawPatientId || r.id
  if (isReportGenerating(generateKey)) return
  markReportGenerating(generateKey)

  try {
    toast?.show('报告生成任务已提交，AI处理中...')
    const { completed } = await generateReportJob(r.rawRecordId)

    rpLoaded.value = false
    await loadReports()
    if (completed) {
      toast?.show('健康报告已生成，请审核确认')
    } else {
      toast?.show('报告仍在生成中，请稍后刷新查看')
    }
  } catch (e) {
    toast?.show(e.message || '生成健康报告失败')
  } finally {
    unmarkReportGenerating(generateKey)
  }
}

/**
 * @isdoc
 * @description 来源展示：仅保留「门诊 / 体检中心」
 * @param {string} src
 * @returns {string}
 */
function sourceLabel(src) {
  const s = String(src || '').trim()
  const hit = scenario.value.sourceOptions.find((x) => s.includes(x) || x.includes(s))
  if (hit) return hit
  return scenario.value.sourceOptions[0] || s || '—'
}

function assistantStatus(key) {
  const enabledKeys = new Set(['hlp', 'health', 'psych', 'rehab', 'tcm'])
  return enabledKeys.has(key) ? 'g' : 'o'
}

function assistantStatusLabel(key) {
  return assistantStatus(key) === 'g' ? '已启用' : '待启用'
}

/**
 * @isdoc
 * @description 负责人展示：统一为“×医生”
 * @param {string} owner
 * @returns {string}
 */
function ownerLabel(owner) {
  const s = String(owner || '').trim()
  if (!s) return '—'
  return s.includes('医生') ? s : `${s.replace(/(师|员|岗|管理师)$/,'')}医生`
}

/**
 * @isdoc
 * @description 右侧“下一步说明”
 * @param {any} p
 * @returns {string}
 */
function nextHint(p) {
  const k = statusKey(p)
  if (k === 'new') return `请先完成患者建档信息，后续才能上传检查报告并生成${scenario.value.reportLabel}。`
  if (k === 'gen') return `请上传/补全检查报告，系统将自动解析并生成${scenario.value.reportLabel}草稿。`
  if (k === 'review') return `${scenario.value.reportLabel}已生成，等待人工确认后进入随访任务下发。`
  if (k === 'plan') return '请选择随访任务模板，预览任务节点并确认下发。'
  return '当前处于任务执行中，可查看已下发任务与打卡记录。'
}

/**
 * @isdoc
 * @description 阶段说明（按你给的文案）
 * @param {any} p
 * @returns {string}
 */
function nextHintV2(p) {
  const k = statusKey(p)
  if (k === 'gen') return `系统将根据档案资料生成${scenario.value.reportLabel}草稿。`
  if (k === 'review') return `${scenario.value.reportLabel}已生成，建议优先完成确认。`
  if (k === 'plan') return `${scenario.value.reportLabel}已确认，等待下发随访任务。`
  if (k === 'follow') return '患者任务执行中，可查看任务记录。'
  return `请先完成患者档案建立，后续才能生成${scenario.value.reportLabel}。`
}

/**
 * @isdoc
 * @description 流程节点（5节点）与状态
 * @param {any} p
 * @returns {{k:string,label:string,state:'done'|'current'|'todo'}[]}
 */
function flowNodes(p) {
  const k = statusKey(p)
  const labels = [
    { k: 'a', label: '建立档案' },
    { k: 'b', label: `${scenario.value.reportLabel}生成` },
    { k: 'c', label: isCheckupScenario.value ? '总检确认' : '健康报告审核' },
    { k: 'd', label: '随访任务下发' },
    { k: 'e', label: '任务执行' },
  ]

  // 当前节点：按“当前状态”定位到主流程节点
  // 健康报告待生成 → 当前=健康报告生成
  // 健康报告待审核 → 当前=健康报告审核
  // 任务待下发 → 当前=随访任务下发
  // 任务执行中 → 当前=任务执行
  const curIdx = k === 'follow' ? 4 : k === 'plan' ? 3 : k === 'review' ? 2 : 1

  return labels.map((x, i) => {
    const state = i < curIdx ? 'done' : i === curIdx ? 'current' : 'todo'
    return { ...x, state }
  })
}

/**
 * @isdoc
 * @description 阶段操作按钮（最多2个）
 * @param {any} p
 * @returns {{label:string,primary:boolean,onClick:()=>void}[]}
 */
function stageActions(p) {
  const k = statusKey(p)
  if (k === 'gen') {
    const generating = reportGeneratingIds.value.has(p?.id)
    return [
      { label: generating ? '生成中...' : (isCheckupScenario.value ? '生成解读' : '生成报告'), primary: true, disabled: generating, onClick: () => generateReportForPatient(p) },
      { label: '全流程管理', primary: false, onClick: () => openPatientWorkspace(p) },
    ]
  }
  if (k === 'review') {
    return [
      { label: isCheckupScenario.value ? '总检确认' : '审核报告', primary: true, onClick: () => openPatientWorkspace(p) },
      { label: '报告列表', primary: false, onClick: () => setSubTab('review') },
    ]
  }
  if (k === 'plan') {
    return [{ label: '随访任务下发', primary: true, onClick: () => openPatientWorkspace(p) }]
  }
  if (k === 'follow') {
    return [
      { label: '查看全流程', primary: true, onClick: () => openPatientWorkspace(p) },
      { label: '执行跟踪', primary: false, onClick: () => setSubTab('follow') },
    ]
  }
  return [{ label: '建立档案', primary: true, onClick: () => goRecord(p) }]
}

/**
 * @isdoc
 * @description 右侧主操作按钮文案
 * @param {any} p
 * @returns {string}
 */
function primaryLabel(p) {
  const k = statusKey(p)
  if (k === 'new') return '新建档案'
  if (k === 'gen') return '上传报告'
  if (k === 'review') return isCheckupScenario.value ? '总检确认' : '审核报告'
  if (k === 'plan') return '随访任务下发'
  return '执行跟踪'
}

/**
 * @isdoc
 * @description 右侧主操作按钮行为（原型：路由/切换tab/提示）
 * @param {any} p
 */
function doPrimary(p) {
  const k = statusKey(p)
  if (k === 'new') return goRecord()
  if (k === 'gen') return setSubTab('record')
  if (k === 'review') return setSubTab('review')
  if (k === 'plan') return setSubTab('followup-plan')
  return setSubTab('follow')
}

/**
 * @isdoc
 * @description 右侧最近动态：严格按当前阶段展示（2-3条），避免越级出现 AI 随访/异常等内容
 * @param {any} p
 * @returns {{at:string,text:string,meta?:string,tone:string}[]}
 */
function stageTimeline(p) {
  const k = statusKey(p)
  const baseAt = String(p?.timeline?.[p.timeline.length - 1]?.at || '刚刚')
  if (k === 'gen' || k === 'new') {
    return [
      { at: baseAt, tone: 'b', text: '档案资料已提交' },
      { at: '—', tone: 'b', text: '检查报告已归档' },
      { at: '—', tone: 'o', text: `等待生成${scenario.value.reportLabel}` },
    ]
  }
  if (k === 'review') {
    return [
      { at: baseAt, tone: 'p', text: `${scenario.value.reportLabel}已生成` },
      { at: '—', tone: 'o', text: isCheckupScenario.value ? '进入总检确认队列' : '进入待审核队列' },
      { at: '—', tone: 'o', text: isCheckupScenario.value ? '等待总检确认' : '等待人工审核' },
    ]
  }
  if (k === 'plan') {
    return [
      { at: baseAt, tone: 'g', text: `${scenario.value.reportLabel}已确认` },
      { at: '—', tone: 'b', text: '患者报告已推送' },
      { at: '—', tone: 'o', text: '等待下发随访任务' },
    ]
  }
  // follow
  return [
    { at: baseAt, tone: 'b', text: '任务已下发' },
    { at: '—', tone: 'g', text: '等待用户打卡' },
    { at: '—', tone: 'p', text: '可查看任务执行记录' },
  ]
}


/**
 * @isdoc
 * @description 获取患者最近一次互动/更新的时间文本（mock：取 chat 最后一次，其次 timeline 最后一次）
 * @param {any} p 患者对象
 * @returns {string}
 */
function lastTouchLabel(p) {
  const at = String(p?.chat?.[p.chat.length - 1]?.at || p?.timeline?.[p.timeline.length - 1]?.at || '').trim()
  return at ? `最近：${at}` : '最近：—'
}

/**
 * @isdoc
 * @description 判断最近一条消息的发送方（用于计算待回复/待患者回复）
 * @param {any} p 患者对象
 * @returns {'patient' | 'ai' | 'none'}
 */
function lastChatRole(p) {
  const last = p?.chat?.[p.chat.length - 1]
  const from = String(last?.from || '').trim()
  if (!from) return 'none'
  if (from === '患者' || /患者/.test(from)) return 'patient'
  if (from === '系统' || /AI/.test(from) || /系统/.test(from)) return 'ai'
  return 'ai'
}

const steps = computed(() => ([
  { label: '建档', ic: '档', sub: '04-10', cls: 'done' },
  { label: '上传上报', ic: '云', sub: '待上传', cls: 'active' },
  { label: `AI${scenario.value.reportLabel}`, ic: 'AI', sub: '待生成', cls: '' },
  { label: isCheckupScenario.value ? '总检确认' : '人工审核', ic: '审', sub: isCheckupScenario.value ? '待确认' : '待审核', cls: '' },
  { label: '推送患者', ic: '推', sub: '待推送', cls: '' },
  { label: '匹配AI助手', ic: '机', sub: '进行中', cls: '' },
  { label: '异常识别', ic: '警', sub: '监测', cls: '' },
  { label: '复查提醒', ic: '铃', sub: '已排程', cls: '' },
  { label: '复查回收', ic: '收', sub: '待回收', cls: '' },
  { label: '档案更新', ic: '更', sub: '—', cls: '' }
]))

// subTabs/allowedSubTabs/setSubTab 已提前定义（由路由 query.tab 驱动）

const stageTabs = computed(() => {
  const count = (k) => queue.value.filter((p) => statusKey(p) === k).length
  return [
    { key: 'all', label: '全部', count: queue.value.length },
    { key: 'gen', label: `${scenario.value.reportLabel}待生成`, count: count('gen') },
    { key: 'review', label: isCheckupScenario.value ? '待总检确认' : '健康报告待审核', count: count('review') },
    { key: 'plan', label: '任务待下发', count: count('plan') },
    { key: 'follow', label: '任务执行中', count: count('follow') },
  ]
})

const nextActions = [
  '上传复查报告',
  `推送${scenario.value.reportLabel}`,
  '下发健康管理任务',
  '发送饮食建议',
  '发送运动计划',
  '创建电话随访',
  '标记异常',
  '创建复查提醒'
]

queue.value = []

// 10条本地 mock 数据（后端无数据时展示）
const MOCK_QUEUE = [
  { id:'m1', name:'张*国', gender:'男', age:56, phoneMasked:'138****5678', source:'门诊', owner:'李医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'review', lastReport:'CT报告' },
  { id:'m2', name:'李*婷', gender:'女', age:48, phoneMasked:'139****2468', source:'体检中心', owner:'李医生', nodules:'甲状腺结节', noduleType:'thyroid', risk:'中风险', riskTone:'o', stage:'review', lastReport:'超声报告' },
  { id:'m3', name:'王*梅', gender:'女', age:62, phoneMasked:'137****1357', source:'门诊', owner:'李医生', nodules:'乳腺结节', noduleType:'breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day1', channel:'小程序', cycle:'每月' } },
  { id:'m4', name:'赵*强', gender:'男', age:59, phoneMasked:'136****8899', source:'体检中心', owner:'李医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'plan', lastReport:'CT报告', planTask:{ day:'day1', channel:'电话', cycle:'每两周' } },
  { id:'m5', name:'陈*霞', gender:'女', age:45, phoneMasked:'138****3344', source:'门诊', owner:'李医生', nodules:'乳腺+肺部结节', noduleType:'breast_lung', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day2', channel:'小程序', cycle:'每月' } },
  { id:'m6', name:'刘*峰', gender:'男', age:71, phoneMasked:'139****7788', source:'体检中心', owner:'李医生', nodules:'肺部+甲状腺结节', noduleType:'lung_thyroid', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'医生复核中', planTask:{ day:'day1', channel:'短信', cycle:'每季度' } },
  { id:'m7', name:'孙*英', gender:'女', age:52, phoneMasked:'137****6677', source:'门诊', owner:'李医生', nodules:'乳腺结节', noduleType:'breast', risk:'低风险', riskTone:'g', stage:'gen', lastReport:'超声报告' },
  { id:'m8', name:'周*明', gender:'男', age:64, phoneMasked:'138****9900', source:'门诊', owner:'李医生', nodules:'肺部+甲状腺结节', noduleType:'lung_thyroid', risk:'中风险', riskTone:'o', stage:'plan', lastReport:'CT报告', planTask:{ day:'day2', channel:'电话', cycle:'每月' } },
  { id:'m9', name:'吴*丽', gender:'女', age:39, phoneMasked:'150****4455', source:'社区', owner:'李医生', nodules:'乳腺+甲状腺结节', noduleType:'breast_thyroid', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'超声报告', planTask:{ day:'day1', channel:'小程序', cycle:'每两周' } },
  { id:'m10', name:'郑*涛', gender:'男', age:67, phoneMasked:'136****2233', source:'体检中心', owner:'李医生', nodules:'三合并结节', noduleType:'triple', risk:'高风险', riskTone:'r', stage:'plan', lastReport:'CT报告', planTask:{ day:'day3', channel:'电话', cycle:'每月' } },
  { id:'m11', name:'黄*芳', gender:'女', age:44, phoneMasked:'135****1122', source:'门诊', owner:'王医生', nodules:'乳腺结节', noduleType:'breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day3', channel:'小程序', cycle:'每月' } },
  { id:'m12', name:'林*海', gender:'男', age:58, phoneMasked:'132****8866', source:'体检中心', owner:'王医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'CT报告', planTask:{ day:'day7', channel:'电话', cycle:'每两周' } },
  { id:'m13', name:'何*秀', gender:'女', age:51, phoneMasked:'133****5544', source:'门诊', owner:'王医生', nodules:'甲状腺结节', noduleType:'thyroid', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'超声报告', planTask:{ day:'day14', channel:'小程序', cycle:'每季度' } },
  { id:'m14', name:'马*军', gender:'男', age:63, phoneMasked:'139****3311', source:'体检中心', owner:'李医生', nodules:'肺部+乳腺结节', noduleType:'lung_breast', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day7', channel:'小程序', cycle:'每月' } },
  { id:'m15', name:'谢*云', gender:'女', age:37, phoneMasked:'136****7700', source:'社区', owner:'王医生', nodules:'甲状腺+乳腺结节', noduleType:'thyroid_breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'超声报告', planTask:{ day:'day21', channel:'小程序', cycle:'每月' } },
  { id:'m16', name:'徐*刚', gender:'男', age:55, phoneMasked:'138****4499', source:'门诊', owner:'李医生', nodules:'肺部结节', noduleType:'lung', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'CT报告', planTask:{ day:'day30', channel:'电话', cycle:'每季度' } },
]

function adaptMockQueueByScenario(list) {
  const sources = scenario.value.sourceOptions || []
  const owner = scenario.value.defaultOwner || '李医生'
  return list.map((p, idx) => ({
    ...p,
    source: sources[idx % Math.max(sources.length, 1)] || p.source,
    owner: idx % 3 === 0 ? owner : p.owner?.replace('医生', scenario.value.key === 'pharmacy' ? '药师' : scenario.value.key === 'community' ? '家医' : '医生'),
  }))
}

// 筛选条件
const qSearch = ref('')
const qSource = ref('')
const qNodule = ref('')
const qRisk = ref('')
const qStatus = ref('')


async function loadPatients() {
  try {
    const res = await fetch('/api/b/patients?per_page=50', { credentials: 'include' })
    const data = await res.json()
    if (data.success) {
      const items = (data.data?.items || data.data || [])
      queue.value = items.map(p => ({
        id: p.id,
        _apiId: p.id,
        name: p.name || '—',
        gender: p.gender || '—',
        age: p.age || '—',
        phoneMasked: p.phone ? p.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '—',
        phone: p.phone || '',
        wecomExternalUserid: p.wecom_external_userid || '',
        wecomUserid: p.wecom_userid || '',
        wecomBindStatus: p.wecom_bind_status || ((p.wecom_external_userid || p.wecom_userid) ? 'bound' : 'unbound'),
        wecomBoundAt: p.wecom_bound_at || '',
        source: p.source_channel === 'manual' ? scenario.value.sourceOptions[0] : (p.source_channel || scenario.value.sourceOptions[0]),
        owner: p.manager_name || scenario.value.defaultOwner,
        nodules: noduleTypeLabel(p.nodule_type),
        noduleType: p.nodule_type || 'breast',
        risk: riskLevelLabel(p.risk_level || (p.reports?.[0]?.risk_level) || '—'),
        riskTone: riskToneFromLevel(p.risk_level || p.reports?.[0]?.risk_level),
        stage: p.risk_level ? 'plan' : (p.reports?.length ? 'review' : 'gen'),
        stageLabel: p.risk_level ? statusLabel({ stage: 'plan' }) : (p.reports?.length ? statusLabel({ stage: 'review' }) : statusLabel({ stage: 'aiGen' })),
        nextStep: '',
        serviceStatus: '',
        report: { status: '—', summary: '' },
        rawReports: [],
        aiReadSummary: '',
        reportDoc: { title: '', sections: [] },
        auditTrail: [],
        chat: [],
        followTodos: [],
        abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
        reviewers: '',
        assistants: [],
        timeline: [],
        planTask: null,
      }))
    }
  } catch (e) {
    console.error('加载患者列表失败', e)
  }
  // 后端无数据时用 mock
  if (!queue.value.length) queue.value = adaptMockQueueByScenario(MOCK_QUEUE).map(p => ({
    ...p,
    stageLabel: '', nextStep: '', serviceStatus: '',
    report: { status: '—', summary: '' }, rawReports: [],
    aiReadSummary: '', reportDoc: { title: '', sections: [] },
    auditTrail: [], chat: [], followTodos: [],
    abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
    reviewers: '', assistants: [], timeline: [],
  }))
  // 始终追加 follow 阶段的 mock 患者（确保任务执行列表有演示数据）
  const followMocks = adaptMockQueueByScenario(MOCK_QUEUE).filter(p => p.stage === 'follow').map(p => ({
    ...p,
    stageLabel: '任务执行中', nextStep: '', serviceStatus: '任务执行中',
    report: { status: '—', summary: '' }, rawReports: [],
    aiReadSummary: '', reportDoc: { title: '', sections: [] },
    auditTrail: [], chat: [], followTodos: [],
    abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
    reviewers: '', assistants: [], timeline: [],
  }))
  const existingIds = new Set(queue.value.map(p => p.id))
  followMocks.forEach(p => { if (!existingIds.has(p.id)) queue.value.push(p) })
}

function noduleTags(p) {
  const type = p.noduleType || ''
  const parts = type.split('_')
  if (parts.length === 1 && type) return [{ label: noduleTypeLabel(type), type }]
  const map = { breast: '乳腺结节', lung: '肺部结节', thyroid: '甲状腺结节', triple: '三合并' }
  if (type === 'triple') return [{ label: '三合并结节', type: 'triple' }]
  return parts.map(k => ({ label: map[k] || k, type: k }))
}

const queueFiltered = computed(() => {
  let list = queue.value
  if (qSearch.value) list = list.filter(p => p.name.includes(qSearch.value) || (p.phoneMasked || '').includes(qSearch.value))
  if (qSource.value) list = list.filter(p => sourceLabel(p.source) === qSource.value || p.source === qSource.value)
  if (qNodule.value) list = list.filter(p => p.nodules === qNodule.value)
  if (qRisk.value) list = list.filter(p => p.risk === qRisk.value)
  if (qStatus.value) list = list.filter(p => statusKey(p) === qStatus.value)
  return list
})

function resetQueueFilters() {
  qSearch.value = ''
  qSource.value = ''
  qNodule.value = ''
  qRisk.value = ''
  qStatus.value = ''
}

const filteredQueue = computed(() => {
  if (activeStage.value === 'all') return queue.value
  return queue.value.filter((p) => statusKey(p) === activeStage.value)
})

// 任务下发页：展示待下发与执行中的患者
const planPatients = computed(() => queue.value.filter((p) => statusKey(p) === 'plan'))

const activePatient = computed(() => {
  return queue.value.find((p) => p.id === activePatientId.value) || queue.value[0] || {}
})

const wecomBindingPatient = computed(() => {
  return queue.value.find((p) => p.id === wecomBindingPatientId.value) || activePatient.value || null
})

function isWecomBound(p) {
  return p?.wecomBindStatus === 'bound' || !!p?.wecomExternalUserid || !!p?.wecomUserid
}

function wecomStatusText(p) {
  return isWecomBound(p) ? '已绑定' : '未绑定'
}

function applyWecomBinding(patientData) {
  const apiId = patientData?.id
  const target = queue.value.find((p) => p._apiId === apiId || p.id === apiId)
  if (!target) return
  target.wecomExternalUserid = patientData.wecom_external_userid || ''
  target.wecomUserid = patientData.wecom_userid || ''
  target.wecomBindStatus = patientData.wecom_bind_status || (target.wecomExternalUserid || target.wecomUserid ? 'bound' : 'unbound')
  target.wecomBoundAt = patientData.wecom_bound_at || ''
}

function openWecomBind(p = activePatient.value) {
  if (!p?._apiId) {
    toast?.show('演示患者暂不支持绑定企业微信身份')
    return
  }
  wecomBindingPatientId.value = p.id
  wecomForm.external_userid = p.wecomExternalUserid || ''
  wecomForm.userid = p.wecomUserid || ''
  wecomModalOpen.value = true
}

async function submitWecomBind() {
  const p = wecomBindingPatient.value
  if (!p?._apiId) return
  const externalUserid = String(wecomForm.external_userid || '').trim()
  const userid = String(wecomForm.userid || '').trim()
  if (!externalUserid && !userid) {
    toast?.show('请至少填写 external_userid 或 userid')
    return
  }
  wecomBindingSaving.value = true
  try {
    const data = await apiJson(`/api/b/patients/${p._apiId}/wecom-bind`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wecom_external_userid: externalUserid,
        wecom_userid: userid,
      }),
    })
    applyWecomBinding(data)
    wecomModalOpen.value = false
    toast?.show('企业微信身份已绑定')
  } catch (e) {
    toast?.show(e.message || '绑定企业微信身份失败')
  } finally {
    wecomBindingSaving.value = false
  }
}

async function unbindWecom(p = activePatient.value) {
  if (!p?._apiId) {
    toast?.show('演示患者暂不支持解绑企业微信身份')
    return
  }
  if (!window.confirm(`确认解绑 ${p.name || '该患者'} 的企业微信身份？`)) return
  try {
    const data = await apiJson(`/api/b/patients/${p._apiId}/wecom-bind`, { method: 'DELETE' })
    applyWecomBinding(data)
    toast?.show('企业微信身份已解绑')
  } catch (e) {
    toast?.show(e.message || '解绑企业微信身份失败')
  }
}

function nowText() {
  return new Date().toLocaleString('zh-CN', { hour12: false })
}

function formatDateInput(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function nextFollowDateByCycle(cycle) {
  const date = new Date()
  const months = String(cycle || '').includes('3') ? 3 : String(cycle || '').includes('6') ? 6 : 12
  date.setMonth(date.getMonth() + months)
  return formatDateInput(date)
}

function cycleDaysFromLabel(cycle) {
  if (String(cycle || '').includes('3')) return 90
  if (String(cycle || '').includes('6')) return 180
  return 365
}

function cycleLabelFromDays(days) {
  const n = Number(days || 0)
  if (n <= 100) return '3个月'
  if (n <= 220) return '6个月'
  return '12个月'
}

function channelToBackend(channel) {
  const text = String(channel || '')
  if (text.includes('企微')) return 'wecom'
  if (text.includes('电话')) return 'phone'
  if (text.includes('小程序')) return 'miniapp'
  return 'wecom'
}

async function loadFollowupTasks() {
  try {
    const data = await apiJson('/api/b/followup/tasks?per_page=100')
    const items = data.items || data || []
    const apiTasks = items.map(normalizeBackendTask)
    if (apiTasks.length) {
      const localOnly = (followTasks.value || []).filter((t) => !t._apiTaskId)
      followTasks.value = [...apiTasks, ...localOnly]
      if (!activeTaskId.value || !followTasks.value.some((t) => t.id === activeTaskId.value)) {
        const firstForPatient = followPatientId.value
          ? followTasks.value.find((t) => String(t.patientId) === String(followPatientId.value))
          : null
        if (firstForPatient || followTasks.value[0]) selectTask((firstForPatient || followTasks.value[0]).id)
      }
    }
  } catch (e) {
    console.warn('加载随访任务失败', e)
  }
}

function normalizeBackendTask(task) {
  const patient = task.patient || {}
  const node = task.task_payload?.node || {}
  const messages = task.messages || []
  const sentMessage = messages.find((m) => m.direction === 'outbound' && m.sent_at)
  return {
    id: `api-task-${task.id}`,
    _apiTaskId: task.id,
    patientId: patient.id || task.patient_id,
    patientName: patient.name || '患者',
    gender: patient.gender || '—',
    age: patient.age || '—',
    phoneMasked: patient.phone ? patient.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '—',
    nodules: noduleTypeLabel(task.nodule_type || patient.nodule_type),
    risk: task.risk_level || '—',
    riskTone: riskToneFromLevel(task.risk_level),
    owner: task.manager_name || scenario.value.defaultOwner,
    channel: task.channel === 'wecom' ? '企微' : task.channel === 'phone' ? '电话' : task.channel === 'miniapp' ? '小程序' : (task.channel || '企微'),
    cycle: '—',
    reminder: task.task_payload?.reminder_strategy || '',
    day: `day${task.plan_day || 1}`,
    time: String(task.scheduled_send_at || task.due_at || '').slice(11, 16) || node.send_time || '09:00',
    scheduledAt: task.scheduled_send_at || task.due_at || '',
    sentAt: sentMessage?.sent_at || '',
    status: task.status === 'completed' ? 'completed' : (task.status || 'scheduled'),
    node,
    taskPayload: task.task_payload || {},
    message: node.message_template || task.ai_summary || '',
    patientAction: patientActionLabel(node.patient_action),
    aiAction: aiActionLabel(node.ai_action),
    messages,
    kbSnapshot: {},
    logs: (task.events || []).map(e => ({ at: e.created_at || '现在', by: e.actor_type || '系统', action: e.event_type, note: e.summary || '' })),
    createdAt: task.created_at || '',
  }
}

function canCreateReportFollowup(report) {
  const status = String(report?.status || '').toLowerCase()
  return ['finalized', 'published', 'archived'].includes(status)
}

function existingReportFollowupTask(reportId, patient = activePatient.value) {
  if (!reportId) return null
  const cached = reportFollowupTaskMap.value[String(reportId)]
  if (cached && cached.status !== 'cancelled') return cached
  if (!patient) return null
  return (patient.workspaceTasks || []).find((task) => (
    String(task.report_id || task.reportId || task.task_payload?.report_id || '') === String(reportId)
    && task.source === 'report'
    && task.status !== 'cancelled'
  )) || null
}

function rememberReportFollowupTasks(tasks = []) {
  const next = { ...reportFollowupTaskMap.value }
  ;(tasks || []).forEach((task) => {
    const reportId = task.report_id || task.reportId || task.task_payload?.report_id
    if (reportId && task.source === 'report' && task.status !== 'cancelled') {
      next[String(reportId)] = task
    }
  })
  reportFollowupTaskMap.value = next
}

async function loadReportFollowupTask(reportId) {
  if (!reportId) return null
  try {
    const data = await apiJson(`/api/b/followup/tasks?report_id=${encodeURIComponent(reportId)}&source=report&per_page=1`)
    const task = (data.items || [])[0] || null
    if (task) rememberReportFollowupTasks([task])
    return task
  } catch (e) {
    console.warn('查询报告随访任务失败', e)
    return null
  }
}

function isCreatingReportFollowup(reportId) {
  return String(reportFollowupCreatingId.value || '') === String(reportId || '')
}

function taskCheckinUrl(task) {
  if (!task) return ''
  const path = task.public_checkin_path || (task.task_code ? `/followup-checkin/${task.task_code}` : '')
  if (!path) return ''
  if (/^https?:\/\//.test(path)) return path
  return `${window.location.origin}${path}`
}

async function copyTaskCheckinLink(task) {
  const url = taskCheckinUrl(task)
  if (!url) return
  try {
    await navigator.clipboard.writeText(url)
    toast?.show('打卡链接已复制')
  } catch (e) {
    toast?.show('复制失败，请手动选择链接')
  }
}

function reportDbStatusLabel(status) {
  const map = {
    draft: '草稿',
    generated: '已生成待审核',
    reviewing: '审核中',
    finalized: '已审核',
    published: '已发布',
    archived: '已归档'
  }
  return map[status] || status || '未生成'
}

function normalizeAdvicePayload(advice, fallback = {}) {
  const sections = advice?.sections || fallback.sections || {}
  return {
    version: advice?.version || fallback.version || 1,
    status: advice?.status || fallback.status || 'draft',
    updatedAt: advice?.updated_at || advice?.updatedAt || fallback.updatedAt || '',
    content: advice?.content || fallback.content || '',
    sections: {
      imaging_report_advice: sections.imaging_report_advice || advice?.content || fallback.content || '',
      overall_assessment: sections.overall_assessment || '',
      risk_assessment: sections.risk_assessment || '',
      tongue_conclusion: sections.tongue_conclusion || ''
    },
    history: (advice?.history || fallback.history || []).map((h, idx) => ({
      id: h.id || `${h.saved_at || h.savedAt || idx}-${h.version || idx}`,
      version: h.version || 1,
      status: h.status || 'draft',
      content: h.content || '',
      sections: h.sections || {},
      savedAt: h.saved_at || h.savedAt || ''
    }))
  }
}

function normalizeImagingReport(item) {
  return {
    id: item.id,
    name: item.file_name || item.name || '影像报告',
    size: item.file_size || item.size || 0,
    uploadedAt: item.uploaded_at || item.uploadedAt || '',
    uploader: item.uploader_name || item.uploaded_by || scenario.value.defaultOwner,
    type: item.file_type || item.type || 'file',
    backend: true
  }
}

async function apiJson(url, options = {}) {
  const res = await fetch(url, { credentials: 'include', ...options })
  const data = await res.json().catch(() => ({}))
  if (!res.ok || data.success === false) {
    const err = new Error(data.message || `请求失败：${res.status}`)
    err.status = res.status
    err.payload = data
    throw err
  }
  return data.data ?? data
}

async function apiPostJson(url, payload = {}) {
  return apiJson(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

function makeDefaultAdvice(p) {
  return {
    version: 1,
    status: 'draft',
    updatedAt: '',
    content: p?.aiReadSummary || p?.report?.summary || '',
    history: []
  }
}

function ensurePatientWorkflow(p) {
  if (!p || !p.id) return p
  p.profileNote = p.profileNote || '既往史、家族史、症状、体征信息待完善。'
  p.assets = p.assets || {}
  p.assets.imagingReports = Array.isArray(p.assets.imagingReports) ? p.assets.imagingReports : []
  p.tongueTask = p.tongueTask || null
  p.tongueH5Url = p.tongueH5Url || p.tongueTask?.h5_url || ''
  p.tongueMobileOpenUrl = p.tongueMobileOpenUrl || ''
  p.workspaceRecords = Array.isArray(p.workspaceRecords) ? p.workspaceRecords : []
  p.workspaceReports = Array.isArray(p.workspaceReports) ? p.workspaceReports : []
  p.workspacePlans = Array.isArray(p.workspacePlans) ? p.workspacePlans : []
  p.workspaceTasks = Array.isArray(p.workspaceTasks) ? p.workspaceTasks : []
  p.latestReport = p.latestReport || null
  p.adviceDraft = p.adviceDraft || makeDefaultAdvice(p)
  p.finalReport = p.finalReport || { content: '', archivedAt: '', version: '' }
  p.followPlan = p.followPlan || {
    cycle: p.planTask?.cycle || (p.riskTone === 'r' ? '3个月' : p.riskTone === 'o' ? '6个月' : '12个月'),
    channel: p.planTask?.channel || '小程序',
    note: `${p.nodules || '结节'}随访，关注分级、大小、症状变化和资料补充。`
  }
  p.managementLogs = Array.isArray(p.managementLogs) ? p.managementLogs : [
    { id: `${p.id}-log-1`, at: '建档后', by: p.owner || scenario.value.defaultOwner, action: '建立患者档案', note: p.nodules || '' },
    { id: `${p.id}-log-2`, at: '待处理', by: '系统', action: '等待报告意见审核', note: statusLabel(p) },
  ]
  return p
}

watch(
  () => activePatient.value?.id,
  () => ensurePatientWorkflow(activePatient.value),
  { immediate: true }
)

async function openPatientWorkspace(p) {
  if (p?.id) activePatientId.value = p.id
  const current = ensurePatientWorkflow(p || activePatient.value)
  setSubTab('detail')
  await hydratePatientWorkspace(current)
}

function openQueueFollowupPlan(p) {
  if (p?.id) activePatientId.value = p.id
  setSubTab('followup-plan')
}

function buildProfileNote(records, fallback = '') {
  const list = Array.isArray(records) ? records : []
  const latest = list
    .slice()
    .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))[0]
  if (!latest) return fallback || '既往史、家族史、症状、体征信息待完善。'
  const fields = [
    latest.main_complaint,
    latest.medical_history,
    latest.past_history,
    latest.family_history,
    latest.symptoms,
    latest.physical_exam,
    latest.health_condition
  ].filter(Boolean)
  if (fields.length) return fields.join('\n')
  return fallback || `最近档案：${latest.record_code || latest.created_at || `#${latest.id}`}`
}

async function hydratePatientWorkspace(p) {
  if (!p?._apiId) return
  p.workspaceLoading = true
  try {
    const [detail, records, reports, plans, tasks] = await Promise.all([
      apiJson(`/api/b/patients/${p._apiId}`),
      apiJson(`/api/b/patients/${p._apiId}/records`),
      apiJson(`/api/b/reports?patient_id=${p._apiId}&per_page=20`),
      apiJson(`/api/b/followup/patient-plans?patient_id=${p._apiId}`),
      apiJson(`/api/b/followup/tasks?patient_id=${p._apiId}&per_page=50`)
    ])
    if (detail?.name) {
      p.name = detail.name || p.name
      p.gender = detail.gender || p.gender
      p.age = detail.age || p.age
      p.phone = detail.phone || p.phone
      p.phoneMasked = detail.phone ? detail.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : p.phoneMasked
      p.nodules = noduleTypeLabel(detail.nodule_type || p.noduleType)
      p.noduleType = detail.nodule_type || p.noduleType
      p.source = detail.source_channel || p.source
      p.wecomExternalUserid = detail.wecom_external_userid || p.wecomExternalUserid
      p.wecomUserid = detail.wecom_userid || p.wecomUserid
      p.wecomBindStatus = detail.wecom_bind_status || p.wecomBindStatus
      p.profileNote = buildProfileNote(detail.health_records || records, p.profileNote)
    }
    p.workspaceRecords = (Array.isArray(records) ? records : [])
      .slice()
      .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
    p.workspaceReports = (reports.reports || reports.items || [])
      .slice()
      .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
    p.workspacePlans = (Array.isArray(plans) ? plans : [])
      .slice()
      .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
    p.workspaceTasks = (tasks.items || tasks || [])
      .slice()
      .sort((a, b) => String(b.scheduled_send_at || b.due_at || b.created_at || '').localeCompare(String(a.scheduled_send_at || a.due_at || a.created_at || '')))
    rememberReportFollowupTasks(p.workspaceTasks)

    const latestRecord = p.workspaceRecords[0]
    if (latestRecord?.id) {
      p.workspaceRecordId = latestRecord.id
      p.latestReport = latestRecord.latest_report || null
      const imaging = await apiJson(`/api/b/records/${latestRecord.id}/imaging-reports`)
      p.assets.imagingReports = (imaging.items || []).map(normalizeImagingReport)
      const tongue = await apiJson(`/api/b/tongue-diagnosis/tasks/by-record/${latestRecord.id}`)
      p.tongueTask = (tongue.items || [])[0] || null
      p.tongueH5Url = p.tongueTask?.h5_url || p.tongueH5Url || ''
      p.tongueMobileOpenUrl = p.tongueTask?.mobile_open_url || p.tongueMobileOpenUrl || ''
    }

    const latestReport = p.workspaceReports[0]
    if (latestReport?.id) {
      p.workspaceReportId = latestReport.id
      p.latestReport = {
        id: latestReport.id,
        report_code: latestReport.report_code,
        status: latestReport.status,
        risk_level: latestReport.risk_level,
        report_summary: latestReport.report_summary,
        imaging_conclusion: latestReport.imaging_conclusion,
        reviewed_at: latestReport.reviewed_at,
        created_at: latestReport.created_at,
        updated_at: latestReport.updated_at
      }
      p.risk = riskLevelLabel(latestReport.risk_level || p.risk)
      p.riskTone = riskToneFromLevel(latestReport.risk_level || p.risk)
      const advice = await apiJson(`/api/b/reports/${latestReport.id}/advice`)
      p.adviceDraft = normalizeAdvicePayload(advice.advice, p.adviceDraft)
      if (latestReport.status === 'finalized' || latestReport.status === 'published' || p.adviceDraft.status === 'archived') {
        p.finalReport = {
          content: p.adviceDraft.content || latestReport.imaging_conclusion || latestReport.report_summary || '',
          archivedAt: latestReport.reviewed_at || p.adviceDraft.updatedAt || '',
          version: p.adviceDraft.version || 1
        }
        p.stage = 'plan'
      }
    }
  } catch (e) {
    console.error('加载患者工作台失败', e)
  } finally {
    p.workspaceLoading = false
  }
}

async function generateReportForPatient(p) {
  const patient = ensurePatientWorkflow(p || activePatient.value)
  if (!patient?._apiId) {
    toast?.show('请先保存患者信息后再生成报告')
    return
  }
  if (isReportGenerating(patient.id)) return

  markReportGenerating(patient.id)
  try {
    if (!patient.workspaceRecordId) {
      await hydratePatientWorkspace(patient)
    }
    if (!patient.workspaceRecordId) {
      toast?.show('请先完成患者建档，再生成健康报告')
      goRecord(patient)
      return
    }

    toast?.show('报告生成任务已提交，AI处理中...')
    const { completed } = await generateReportJob(patient.workspaceRecordId)

    rpLoaded.value = false
    await hydratePatientWorkspace(patient)
    await loadReports()
    if (completed) {
      patient.stage = 'review'
      toast?.show('健康报告已生成，请到健康报告审核中确认')
      setSubTab('review')
    } else {
      toast?.show('报告仍在生成中，请稍后到健康报告审核查看')
    }
  } catch (e) {
    toast?.show(e.message || '生成健康报告失败')
  } finally {
    unmarkReportGenerating(patient.id)
  }
}

const activeAdvice = computed(() => {
  const p = ensurePatientWorkflow(activePatient.value)
  return p?.adviceDraft || makeDefaultAdvice(p)
})

function updateActivePatientField({ field, value }) {
  if (!field) return
  const p = ensurePatientWorkflow(activePatient.value)
  if (!p) return
  p[field] = value
}

function updateActiveAdviceContent(value) {
  const p = ensurePatientWorkflow(activePatient.value)
  if (!p) return
  p.adviceDraft = p.adviceDraft || makeDefaultAdvice(p)
  p.adviceDraft.content = value
}

const adviceLocked = computed(() => {
  const p = ensurePatientWorkflow(activePatient.value)
  const status = p?.adviceDraft?.status
  const reportStatus = p?.latestReport?.status
  return !!p?.finalReport?.content || ['archived', 'approved'].includes(status) || ['finalized', 'published', 'archived'].includes(reportStatus)
})

const workspaceTongueActionLabel = computed(() => {
  const task = activePatient.value?.tongueTask
  if (task?.status === 'h5_sso_created') return '重新打开舌诊 H5'
  if (task?.status === 'completed') return '已完成舌诊'
  return '打开舌诊 H5'
})

const workspaceTongueStatusLabel = computed(() => {
  const status = activePatient.value?.tongueTask?.status
  const map = {
    h5_sso_created: 'H5已生成',
    completed: '舌诊已完成',
    failed: '检测失败',
    waiting_inquiry: '待完成'
  }
  return map[status] || status || ''
})

const workspaceTongueQrUrl = computed(() => {
  const url = activePatient.value?.tongueMobileOpenUrl || activePatient.value?.tongueH5Url || ''
  if (!url) return ''
  return `https://api.qrserver.com/v1/create-qr-code/?size=180x180&margin=8&data=${encodeURIComponent(url)}`
})

function adviceStatusLabel(status) {
  const map = {
    draft: '草稿',
    reviewing: '待审核',
    approved: '审核通过',
    archived: '已写入最终报告',
  }
  return map[status] || '草稿'
}

const patientFlowSteps = computed(() => {
  const p = ensurePatientWorkflow(activePatient.value)
  const adviceStatus = p?.adviceDraft?.status || 'draft'
  const hasFinal = !!p?.finalReport?.content
  const hasPlan = !!p?.followPlan?.note
  const nodes = [
    { key: 'archive', no: 1, label: '档案' },
    { key: 'risk', no: 2, label: '评估' },
    { key: 'advice', no: 3, label: '建议' },
    { key: 'review', no: 4, label: '审核' },
    { key: 'final', no: 5, label: '最终报告' },
    { key: 'follow', no: 6, label: '随访管理' },
  ]
  const current = hasFinal && hasPlan ? 5 : hasFinal ? 4 : adviceStatus === 'reviewing' ? 3 : 2
  return nodes.map((n, idx) => ({ ...n, state: idx < current ? 'done' : idx === current ? 'current' : 'todo' }))
})

const computedRisk = computed(() => {
  const p = activePatient.value || {}
  if (p.riskTone === 'r' || p.risk === '高风险') return { level: '高风险', tone: 'r' }
  if (p.riskTone === 'o' || p.risk === '中风险') return { level: '中风险', tone: 'o' }
  if (p.riskTone === 'g' || p.risk === '低风险') return { level: '低风险', tone: 'g' }
  return { level: '待评估', tone: 'g' }
})

const riskLayerItems = computed(() => {
  const p = ensurePatientWorkflow(activePatient.value)
  const completenessRisk = (p.assets?.imagingReports || []).length ? { level: '资料较完整', tone: 'g' } : { level: '资料缺口', tone: 'o' }
  const tongueRisk = p.tongueTask?.status === 'completed'
    ? { level: '舌诊已回流', tone: 'g' }
    : p.tongueH5Url
      ? { level: 'H5链接已生成', tone: 'g' }
      : { level: '待生成手机链接', tone: 'o' }
  return [
    { key: 'nodule', label: '结节分层', level: computedRisk.value.level, tone: computedRisk.value.tone, reason: `${p.nodules || '结节'}当前标记为${computedRisk.value.level}，需结合分级、大小、数量和症状复核。` },
    { key: 'material', label: '资料完整度', level: completenessRisk.level, tone: completenessRisk.tone, reason: (p.assets?.imagingReports || []).length ? '已上传影像报告，可进入报告解析/复核。' : '缺少原始影像报告，AI只能基于表单生成初步建议。' },
    { key: 'history', label: '病史风险', level: p.profileNote?.includes('家族') ? '需关注' : '常规', tone: p.profileNote?.includes('家族') ? 'o' : 'g', reason: p.profileNote || '病史信息待完善。' },
    { key: 'tongue', label: '舌诊资料', level: tongueRisk.level, tone: tongueRisk.tone, reason: 'B端生成手机H5链接，由患者手机或健康管理师手机完成采集；结果回流后写入档案和报告。' },
  ]
})

function addManagementLog(action, note = '') {
  const p = ensurePatientWorkflow(activePatient.value)
  p.managementLogs = p.managementLogs || []
  p.managementLogs.unshift({ id: `${Date.now()}-${Math.random()}`, at: nowText(), by: p.owner || scenario.value.defaultOwner, action, note })
}

async function handleImagingUpload(event) {
  const p = ensurePatientWorkflow(activePatient.value)
  const files = Array.from(event.target.files || [])
  if (!files.length) return
  try {
    if (p.workspaceRecordId) {
      const form = new FormData()
      files.forEach(file => form.append('imaging_reports', file))
      const data = await apiJson(`/api/b/records/${p.workspaceRecordId}/imaging-reports`, { method: 'POST', body: form })
      const existing = (p.assets.imagingReports || []).filter(x => !x.backend)
      p.assets.imagingReports = [...(data.items || []).map(normalizeImagingReport), ...existing]
    } else {
      files.forEach(file => {
        p.assets.imagingReports.unshift({
          id: `${Date.now()}-${file.name}-${Math.random()}`,
          name: file.name,
          size: file.size,
          uploadedAt: nowText(),
          uploader: p.owner || scenario.value.defaultOwner,
          type: file.type || 'file'
        })
      })
    }
    addManagementLog('上传影像报告', files.map(f => f.name).join('、'))
  } catch (e) {
    toast?.show(e.message || '影像报告上传失败')
  } finally {
    event.target.value = ''
  }
}

async function startWorkspaceTongueDiagnosis() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (!p._apiId || !p.workspaceRecordId) {
    toast?.show('请先保存患者档案，再发起舌诊')
    return
  }
  tongueSubmitting.value = true
  try {
    const data = await apiJson('/api/b/tongue-diagnosis/h5-sso', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient_id: p._apiId, record_id: p.workspaceRecordId })
    })
    p.tongueTask = data.task
    p.tongueH5Url = data.h5_url || data.task?.h5_url || ''
    p.tongueMobileOpenUrl = data.mobile_open_url || ''
    addManagementLog('打开舌诊H5', data.task?.out_id || '')
    if (p.tongueH5Url) window.open(p.tongueH5Url, '_blank', 'noopener')
    toast?.show('手机舌诊链接已生成')
  } catch (e) {
    toast?.show(e.message || 'H5舌诊打开失败')
  } finally {
    tongueSubmitting.value = false
  }
}

async function copyWorkspaceTongueLink() {
  const url = activePatient.value?.tongueMobileOpenUrl || activePatient.value?.tongueH5Url || ''
  if (!url) return
  try {
    await navigator.clipboard.writeText(url)
    toast?.show('舌诊链接已复制')
  } catch (e) {
    toast?.show('复制失败，请手动选择链接')
  }
}

async function syncWorkspaceTongueReport() {
  const p = ensurePatientWorkflow(activePatient.value)
  const taskId = p.tongueTask?.id
  if (!taskId) {
    toast?.show('请先生成舌诊H5链接')
    return
  }
  tongueSyncing.value = true
  try {
    const data = await apiJson(`/api/b/tongue-diagnosis/tasks/${taskId}/sync-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    p.tongueTask = data.task || p.tongueTask
    p.tongueH5Url = p.tongueTask?.h5_url || p.tongueH5Url || ''
    p.tongueMobileOpenUrl = p.tongueTask?.mobile_open_url || p.tongueMobileOpenUrl || ''
    addManagementLog('同步舌诊结果', p.tongueTask?.status || '')
    toast?.show(p.tongueTask?.tongue_feature ? '舌诊结果已同步' : '暂未查询到舌诊报告')
  } catch (e) {
    toast?.show(e.message || '舌诊结果同步失败')
  } finally {
    tongueSyncing.value = false
  }
}

async function removeAsset(type, id) {
  const p = ensurePatientWorkflow(activePatient.value)
  const hit = (p.assets[type] || []).find(x => x.id === id)
  if (type === 'imagingReports' && hit?.backend && p.workspaceRecordId) {
    try {
      await apiJson(`/api/b/records/${p.workspaceRecordId}/imaging-reports/${id}`, { method: 'DELETE' })
    } catch (e) {
      toast?.show(e.message || '删除影像报告失败')
      return
    }
  }
  p.assets[type] = (p.assets[type] || []).filter(x => x.id !== id)
  addManagementLog('删除资料', type)
}

async function regenerateAdviceForActive() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (adviceLocked.value) {
    toast?.show('最终报告已归档，不能再次生成建议')
    return
  }
  adviceGenerating.value = true
  try {
    const previous = p.adviceDraft.content
    if (previous) {
      p.adviceDraft.history = p.adviceDraft.history || []
      p.adviceDraft.history.unshift({
        id: `${Date.now()}-${p.adviceDraft.version}`,
        version: p.adviceDraft.version || 1,
        status: p.adviceDraft.status || 'draft',
        content: previous,
        savedAt: p.adviceDraft.updatedAt || nowText()
      })
    }
    p.adviceDraft.version = (p.adviceDraft.version || 1) + 1
    p.adviceDraft.status = 'draft'
    p.adviceDraft.updatedAt = nowText()
    p.adviceDraft.content = `基于${p.name}当前档案，${p.nodules}建议按${computedRisk.value.level}路径管理。请补充原始影像报告，结合分级、大小、症状、病史进行复核；若分级不清或资料缺失，应优先完善检查资料后再形成最终报告。随访建议：${p.followPlan?.cycle || '6个月'}复查，通过${p.followPlan?.channel || '小程序'}进行提醒和记录。`
    if (p.workspaceReportId) {
      const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: p.adviceDraft.content, preserve_history: true })
      })
      p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
    }
    addManagementLog('再次生成建议草稿', `V${p.adviceDraft.version}`)
  } catch (e) {
    toast?.show(e.message || '再次生成建议失败')
  } finally {
    adviceGenerating.value = false
  }
}

async function saveAdviceDraft() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (adviceLocked.value) {
    toast?.show('最终报告已归档，不能编辑建议')
    return false
  }
  if (!String(p.adviceDraft.content || '').trim()) {
    toast?.show('请先生成或填写建议内容')
    return false
  }
  if (p.workspaceReportId) {
    try {
      const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: p.adviceDraft.content, preserve_history: true })
      })
      p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
    } catch (e) {
      toast?.show(e.message || '保存建议草稿失败')
      return false
    }
  }
  p.adviceDraft.status = 'draft'
  p.adviceDraft.updatedAt = nowText()
  addManagementLog('保存建议草稿', `V${p.adviceDraft.version || 1}`)
  return true
}

async function submitAdviceReview() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (adviceLocked.value) {
    toast?.show('最终报告已归档，不能再次提交审核')
    return
  }
  if (!String(p.adviceDraft.content || '').trim()) {
    toast?.show('请先生成或填写建议内容')
    return
  }
  if (p.workspaceReportId) {
    try {
      const saved = await saveAdviceDraft()
      if (!saved) return
      const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice/submit-review`, { method: 'POST' })
      p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
    } catch (e) {
      toast?.show(e.message || '提交建议审核失败')
      return
    }
  }
  p.adviceDraft.status = 'reviewing'
  p.adviceDraft.updatedAt = nowText()
  p.stage = 'review'
  addManagementLog('提交建议审核', `V${p.adviceDraft.version || 1}`)
}

async function approveAdviceToFinal() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (adviceLocked.value) {
    toast?.show('最终报告已归档')
    return
  }
  if (p.adviceDraft.status !== 'reviewing') return
  if (p.workspaceReportId) {
    try {
      const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: p.adviceDraft.content, summary: p.report?.summary || '' })
      })
      p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
    } catch (e) {
      toast?.show(e.message || '审核通过失败')
      return
    }
  }
  p.adviceDraft.status = 'archived'
  p.finalReport = {
    content: p.adviceDraft.content,
    archivedAt: nowText(),
    version: p.adviceDraft.version || 1
  }
  p.stage = 'plan'
  addManagementLog('审核通过并写入最终报告', `V${p.adviceDraft.version || 1}`)
  rpLoaded.value = false
  await hydratePatientWorkspace(p)
}

async function createFirstFollowupTaskForActive(reportId = null) {
  const p = ensurePatientWorkflow(activePatient.value)
  const targetReportId = reportId || p.workspaceReportId || p.latestReport?.id
  if (!targetReportId) {
    toast?.show('请先生成并审核健康报告')
    return
  }
  if (existingReportFollowupTask(targetReportId, p)) {
    toast?.show('该报告已存在首次随访任务')
    return
  }
  reportFollowupCreatingId.value = String(targetReportId)
  try {
    const task = await createReportFollowupTask(targetReportId)
    p.workspaceTasks = [task, ...(p.workspaceTasks || [])]
    addManagementLog('创建首次随访任务', `${task.title || '报告后首次随访'} · ${task.due_at || '待排期'}`)
    toast?.show('已创建报告后首次随访任务')
    await hydratePatientWorkspace(p)
  } catch (e) {
    if (e.status === 409) {
      toast?.show('该报告已存在随访任务')
      await hydratePatientWorkspace(p)
    } else {
      toast?.show(e.message || '创建首次随访任务失败')
    }
  } finally {
    reportFollowupCreatingId.value = ''
  }
}

async function createReportFollowupTask(reportId) {
  const existing = await loadReportFollowupTask(reportId)
  if (existing) {
    const err = new Error('该报告已存在首次随访任务')
    err.status = 409
    err.existingTask = existing
    throw err
  }
  const task = await apiPostJson(`/api/b/followup/tasks/from-report/${reportId}`, {})
  rememberReportFollowupTasks([task])
  return task
}

async function createAuditFollowupTask() {
  if (!rpAuditId.value) return
  reportFollowupCreatingId.value = String(rpAuditId.value)
  try {
    const task = await createReportFollowupTask(rpAuditId.value)
    toast?.show('已创建报告后首次随访任务')
    const patient = queue.value.find(p => String(p._apiId || p.id) === String(task.patient_id))
    if (patient) await hydratePatientWorkspace(patient)
  } catch (e) {
    if (e.status === 409) {
      toast?.show('该报告已存在随访任务')
      if (e.existingTask) rememberReportFollowupTasks([e.existingTask])
    } else {
      toast?.show(e.message || '创建首次随访任务失败')
    }
  } finally {
    reportFollowupCreatingId.value = ''
  }
}

async function openReportFollowupTask(reportId) {
  const task = existingReportFollowupTask(reportId, null) || await loadReportFollowupTask(reportId)
  if (!task) {
    toast?.show('未找到该报告的随访任务')
    return
  }
  const patient = queue.value.find(p => String(p._apiId || p.id) === String(task.patient_id))
  if (patient) followPatientId.value = patient.id
  await loadFollowupTasks()
  const matched = (followTasks.value || []).find(t => String(t._apiTaskId || '').replace('api-task-', '') === String(task.id) || String(t.id) === `api-task-${task.id}`)
  if (matched) selectTask(matched.id)
  rpAuditId.value = ''
  setSubTab('follow')
}

function updateActiveFollowPlan({ field, value }) {
  if (!field) return
  const p = ensurePatientWorkflow(activePatient.value)
  if (!p) return
  p.followPlan = p.followPlan || {}
  p.followPlan[field] = value
}

async function saveFollowPlan() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (!p?._apiId) {
    toast?.show('请先保存患者信息后再保存任务配置')
    return
  }
  try {
    const data = await apiJson(`/api/b/patients/${p._apiId}/follow-ups`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        follow_up_type: p.followPlan.channel || '小程序',
        follow_up_date: formatDateInput(new Date()),
        content: p.followPlan.note || '',
        next_follow_up_date: nextFollowDateByCycle(p.followPlan.cycle),
        next_follow_up_action: `${p.followPlan.cycle || '6个月'}复查；${p.followPlan.channel || '小程序'}触达`
      })
    })
    p.followPlan.savedAt = data.created_at || nowText()
    p.followPlan.backendId = data.id
    p.stage = p.finalReport?.content ? 'follow' : 'plan'
    addManagementLog('保存任务配置', `${p.followPlan.cycle} · ${p.followPlan.channel}`)
    toast?.show('任务配置已保存')
  } catch (e) {
    toast?.show(e.message || '保存任务配置失败')
  }
}

watch(
  () => [subTab.value, planPatients.value.length],
  () => {
    if (subTab.value !== 'followup-plan') return
    const list = planPatients.value || []
    if (!list.length) return
    if (!list.some((p) => p.id === activePatientId.value)) activePatientId.value = list[0].id
    if (!(followTasks.value || []).length) {
      const seeded = list.filter((p) => p?.planTask).slice(0, 8).flatMap((p) => previewTasksFromPatient(p))
      followTasks.value = seeded
      if (seeded[0]) selectTask(seeded[0].id)
    }
  },
  { immediate: true }
)

watch(
  () => activePatientId.value,
  () => {
    // 若患者已保存过计划 day，则切换到该 day
    const d = activePatient.value?.plan?.day
    if (typeof d === 'string' && d.startsWith('day')) planDay.value = d
  },
  { immediate: true }
)

/**
 * @isdoc
 * @description 根据当前子页(tab)强制绑定患者池(stage)
 * @param {string} tab
 * @returns {'all'|'gen'|'review'|'plan'|'follow'}
 */
function stageForTab(tab) {
  if (tab === 'followup-plan') return 'plan'
  if (tab === 'follow') return 'follow'
  if (tab === 'review') return 'review'
  if (tab === 'record') return 'gen'
  return 'all'
}

watch(
  () => subTab.value,
  (tab) => {
    // 强制让每个子页只看自己的患者池
    const stage = stageForTab(tab)
    activeStage.value = stage

    const list = stage === 'plan'
      ? planPatients.value
      : stage === 'follow'
        ? queue.value.filter((p) => statusKey(p) === 'follow')
        : stage === 'review'
          ? queue.value.filter((p) => statusKey(p) === 'review')
          : stage === 'gen'
            ? queue.value.filter((p) => statusKey(p) === 'gen')
            : queue.value

    if (list.length && !list.some((p) => p.id === activePatientId.value)) {
      activePatientId.value = list[0].id
    }
    if (tab === 'follow' && list.length && !list.some((p) => p.id === followPatientId.value)) {
      followPatientId.value = list[0].id
    }
    if (tab === 'review') {
      rpLoaded.value = false
      loadReports()
    }
  },
  { immediate: true }
)

const midTitle = computed(() => {
  const map = {
    queue: '闭环处置工作台',
    record: '患者建档',
    review: isCheckupScenario.value ? '体检报告确认' : '健康报告审核',
    follow: '任务执行'
  }
  return map[subTab.value] || '患者管理'
})

/**
 * @description 设置当前阶段筛选，并保证选中患者存在
 * @param {string} key 阶段key
 */
function setStage(key) {
  activeStage.value = key
  const list = filteredQueue.value
  if (list.length && !list.some((p) => p.id === activePatientId.value)) {
    activePatientId.value = list[0].id
  }
  if (subTab.value !== 'queue') setSubTab('queue')
}

// countBy 已废弃：状态统计改为 statusKey 映射

/**
 * @description 跳转到「患者建档」页面
 */
function goRecord(p = null) {
  recordPatient.value = p?.id ? p : null
  if (p?.id) activePatientId.value = p.id
  setSubTab('record')
}

/**
 * @isdoc
 * @description 返回患者队列（用于患者建档页头返回按钮）
 */
function backToQueue() {
  setSubTab('queue')
}
</script>

<style scoped>
.pm{height:100%;display:flex;flex-direction:column;overflow:hidden;margin:0}
.pm-shell{flex:1;min-height:0;background:#fff;display:flex;flex-direction:column;overflow:hidden}
.pm-record{flex:1;min-height:0;overflow:auto;background:#f3f6fb;padding:12px}


.primary{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  background:#155eef;
  border:1px solid #155eef;
  color:#fff;
  border-radius:10px;
  padding:5px 10px;
  font-weight:950;
  cursor:pointer;
  min-height:32px;
  line-height:1.3;
  white-space:nowrap;
  font-size:13px;
}
.primary:disabled{opacity:.6;cursor:not-allowed}
.btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  border:1px solid #d9e2ef;
  border-radius:10px;
  background:#fff;
  color:#475569;
  padding:5px 10px;
  font-weight:950;
  cursor:pointer;
  min-height:32px;
  line-height:1.3;
  white-space:nowrap;
  font-size:13px;
}
.muted{color:#64748b;font-weight:750}
.profile-field{display:flex;flex-direction:column;gap:5px;font-size:12px;color:#64748b;font-weight:850;min-width:0}
.profile-field input{width:100%;box-sizing:border-box;border:1px solid #dbe5f2;border-radius:9px;background:#fff;padding:8px 10px;color:#0f172a;font-size:13px;font-weight:650}
.profile-field.wide{grid-column:1/-1}

/* 随访执行页外层网格。内部列由 FollowTrackingTab/LegacyFollowAssistantPreview 接管。 */
.follow-workbench{flex:1;min-height:0;display:grid;grid-template-columns:minmax(260px,300px) minmax(420px,.95fr) minmax(420px,1.05fr);gap:10px;padding:12px;overflow:hidden}
@media (max-width:1500px){.follow-workbench{grid-template-columns:minmax(240px,280px) minmax(320px,.85fr) minmax(380px,1fr)}}
@media (max-width:1280px){.follow-workbench{grid-template-columns:250px minmax(0,1fr);grid-template-rows:auto minmax(420px,1fr)}}

/* 报告查看弹窗 */
.rp-modal-mask{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:9999;display:flex;align-items:center;justify-content:center}
.rp-modal{background:#fff;border-radius:12px;width:min(860px,96vw);max-height:88vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25)}
.rp-modal-head{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid #e6edf7;flex-shrink:0}
.rp-modal-title{font-size:16px;font-weight:800;color:#111827}
.rp-modal-close{border:0;background:transparent;font-size:18px;color:#94a3b8;cursor:pointer;padding:0 4px}
.rp-modal-close:hover{color:#374151}
.rp-modal-body{padding:20px 24px;overflow-y:auto;flex:1;font-size:14px;line-height:1.8;color:#1e293b}
.rp-modal-body h1,.rp-modal-body h2,.rp-modal-body h3{color:#111827;margin:16px 0 8px}
.rp-modal-body p{margin:6px 0}
.wecom-modal{width:min(560px,96vw)}
.wecom-form-grid{display:grid;gap:12px}
.wecom-form-hint{margin-top:12px;border:1px solid #eef2f7;border-radius:10px;background:#fbfdff;padding:10px 12px;color:#64748b;font-size:12px;line-height:1.7}
.wecom-modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:16px}

</style>
