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
      <div v-else-if="subTab === 'follow'" class="follow-page-shell">

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
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import RecordView from './RecordView.vue'
import FollowTrackingTab from '../components/FollowTrackingTab.vue'
import OtherPatientTabs from '../components/OtherPatientTabs.vue'
import PatientDetailWorkspace from '../components/PatientDetailWorkspace.vue'
import PatientQueueOverview from '../components/PatientQueueOverview.vue'
import PlanDispatchTab from '../components/PlanDispatchTab.vue'
import ReportAuditModal from '../components/ReportAuditModal.vue'
import ReportReviewTab from '../components/ReportReviewTab.vue'
import { getStoredScenario } from '../config/scenarios'
import { useFollowupContent } from '../composables/useFollowupContent'
import { useFollowupDispatch } from '../composables/useFollowupDispatch'
import { useFollowupPlanning } from '../composables/useFollowupPlanning'
import { useFollowupTasks } from '../composables/useFollowupTasks'
import { usePatientDisplay } from '../composables/usePatientDisplay'
import { usePatientManagementNavigation } from '../composables/usePatientManagementNavigation'
import { usePatientQueue } from '../composables/usePatientQueue'
import { usePatientStageActions } from '../composables/usePatientStageActions'
import {
  aiActionLabel,
  patientActionLabel,
  trackingStatusLabel,
  usePatientTracking
} from '../composables/usePatientTracking'
import { useReportAudit } from '../composables/useReportAudit'
import { useReportFollowupTasks } from '../composables/useReportFollowupTasks'
import { useReportGeneration } from '../composables/useReportGeneration'
import { useReportList } from '../composables/useReportList'
import { useReportViewer } from '../composables/useReportViewer'
import {
  normalizeAdvicePayload,
  usePatientWorkspace
} from '../composables/usePatientWorkspace'
import { useWecomBinding } from '../composables/useWecomBinding'

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

const activePatientId = ref('p1')
const recordPatient = ref(null)
const followPatientId = ref('p1')
const followSearch = ref('')
const followRiskFilter = ref('')
const followStageFilter = ref('')
const patientEditMode = ref(false)
const activeAssistant = ref('hlp')

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
const {
  activeStage,
  filteredQueue,
  loadPatients,
  noduleTags,
  ownerLabel,
  planPatients,
  qNodule,
  qRisk,
  qSearch,
  qSource,
  qStatus,
  queueFiltered,
  resetQueueFilters,
  sourceLabel,
  stageTabs,
} = usePatientQueue({
  isCheckupScenario,
  noduleTypeLabel,
  queue,
  riskLevelLabel,
  riskToneFromLevel,
  scenario,
  statusKey,
  statusLabel,
})

const {
  activeTask,
  activeTaskId,
  filteredPlanPatients,
  followPatient,
  followTasks,
  loadFollowupTasks,
  makeTaskFromPatient,
  normalizeBackendTask,
  resetTaskFilters,
  selectTask,
  taskFilters,
} = useFollowupTasks({
  activePatientId,
  apiJson,
  followPatientId,
  getDraft: () => draft.value,
  noduleTypeLabel,
  planDay,
  planPatients,
  queue,
  riskToneFromLevel,
  scenario,
  subTab,
})

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

const aiFollowFlowSteps = [
  { icon: '患', title: '患者画像', sub: '病种/风险/阶段' },
  { icon: '策', title: '助手策略', sub: '确定输出倾向' },
  { icon: '库', title: '知识匹配', sub: '匹配内容库' },
  { icon: '文', title: '生成内容', sub: '摘要/任务/提醒' },
  { icon: '发', title: '患者预览', sub: '预览后下发' },
]

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
  backToQueue,
  goRecord,
  midTitle,
  openQueueFollowupPlan,
  setStage,
} = usePatientManagementNavigation({
  activePatientId,
  activeStage,
  filteredQueue,
  followPatientId,
  isCheckupScenario,
  loadReports,
  planPatients,
  queue,
  recordPatient,
  rpLoaded,
  setSubTab,
  statusKey,
  subTab,
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

const activePatient = computed(() => {
  return queue.value.find((p) => p.id === activePatientId.value) || queue.value[0] || {}
})
const defaultOwner = computed(() => scenario.value.defaultOwner)
const rpAuditId = ref('')
const onAuditFollowupTaskCreated = ref(null)
const {
  auditFollowupTask,
  canCreateReportFollowup,
  copyTaskCheckinLink,
  createAuditFollowupTask,
  createReportFollowupTask,
  existingReportFollowupTask,
  isCreatingReportFollowup,
  loadReportFollowupTask,
  openReportFollowupTask,
  rememberReportFollowupTasks,
  reportFollowupCreatingId,
} = useReportFollowupTasks({
  activePatient,
  apiJson,
  apiPostJson,
  followPatientId,
  followTasks,
  loadFollowupTasks,
  onAuditFollowupTaskCreated,
  queue,
  rpAuditId,
  selectTask,
  setSubTab,
  toast,
})
const {
  closeAudit,
  finalizeReport,
  openReportRowPrimary,
  rpAuditImagingAdvice,
  rpAuditOverallAdvice,
  rpAuditPara1,
  rpAuditPara2,
  rpAuditRiskAdvice,
  rpAuditStatus,
  rpAuditTongueAdvice,
  rpAuditVersion,
  rpAuditWasReviewed,
  rpFinalizing,
  showAuditFollowupNext,
} = useReportAudit({
  apiJson,
  generateReportJob,
  goRecord,
  isReportGenerating,
  loadReportFollowupTask,
  loadReports,
  makeReportFlow,
  markReportGenerating,
  normalizeAdvicePayload,
  queue,
  reportTerms,
  rpActiveId,
  rpAuditId,
  rpList,
  rpLoaded,
  toast,
  unmarkReportGenerating,
})
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

function assistantStatus(key) {
  const enabledKeys = new Set(['hlp', 'health', 'psych', 'rehab', 'tcm'])
  return enabledKeys.has(key) ? 'g' : 'o'
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

const {
  activeAdvice,
  addManagementLog,
  adviceGenerating,
  adviceLocked,
  adviceStatusLabel,
  approveAdviceToFinal,
  computedRisk,
  copyWorkspaceTongueLink,
  createFirstFollowupTaskForActive,
  ensurePatientWorkflow,
  generateReportForPatient,
  handleImagingUpload,
  hydratePatientWorkspace,
  openPatientWorkspace,
  patientFlowSteps,
  regenerateAdviceForActive,
  removeAsset,
  riskLayerItems,
  saveAdviceDraft,
  saveFollowPlan,
  startWorkspaceTongueDiagnosis,
  submitAdviceReview,
  syncWorkspaceTongueReport,
  tongueSubmitting,
  tongueSyncing,
  updateActiveAdviceContent,
  updateActiveFollowPlan,
  updateActivePatientField,
  workspaceTongueActionLabel,
  workspaceTongueQrUrl,
  workspaceTongueStatusLabel,
} = usePatientWorkspace({
  activePatient,
  activePatientId,
  apiJson,
  createReportFollowupTask,
  defaultOwner,
  existingReportFollowupTask,
  formatDateInput,
  generateReportJob,
  goRecord,
  isReportGenerating,
  loadReports,
  markReportGenerating,
  nextFollowDateByCycle,
  noduleTypeLabel,
  rememberReportFollowupTasks,
  reportFollowupCreatingId,
  riskLevelLabel,
  riskToneFromLevel,
  rpLoaded,
  setSubTab,
  statusLabel,
  toast,
  unmarkReportGenerating,
})
onAuditFollowupTaskCreated.value = async (task) => {
  const patient = queue.value.find(p => String(p._apiId || p.id) === String(task.patient_id))
  if (patient) await hydratePatientWorkspace(patient)
}
const {
  flowNodes,
  nextHintV2,
  stageActions,
  stageTimeline,
} = usePatientStageActions({
  generateReportForPatient,
  goRecord,
  isCheckupScenario,
  openPatientWorkspace,
  reportGeneratingIds,
  scenario,
  setSubTab,
  statusKey,
})
const {
  isWecomBound,
  openWecomBind,
  submitWecomBind,
  unbindWecom,
  wecomBindingPatient,
  wecomBindingSaving,
  wecomForm,
  wecomModalOpen,
  wecomStatusText,
} = useWecomBinding({
  activePatient,
  apiJson,
  queue,
  toast,
})
const {
  ensureFollowupRecommendation,
  followupPlanSaving,
  planDispatchSteps,
  recommendForActive,
  savePlanForActiveAndBackend,
  simulatePlanToFollowup,
} = useFollowupDispatch({
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
})

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

function cycleLabelFromDays(days) {
  const n = Number(days || 0)
  if (n <= 100) return '3个月'
  if (n <= 220) return '6个月'
  return '12个月'
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

watch(
  () => activePatientId.value,
  () => {
    // 若患者已保存过计划 day，则切换到该 day
    const d = activePatient.value?.plan?.day
    if (typeof d === 'string' && d.startsWith('day')) planDay.value = d
  },
  { immediate: true }
)

// countBy 已废弃：状态统计改为 statusKey 映射
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

/* 随访执行页外层容器。三列布局由 FollowTrackingTab 自身接管。 */
.follow-page-shell{flex:1;min-height:0;padding:12px;overflow:hidden;background:#fff}

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
