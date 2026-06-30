<template>
  <div class="doctor-page">
    <header class="page-head">
      <div>
        <div class="eyebrow">医生工作台</div>
        <h1>患者复查与随访指导</h1>
        <p>医生只查看本人负责患者，处理院外复查、用药随访指导、复查资料和转手术判断。</p>
      </div>
      <button class="btn" type="button" @click="loadData">刷新</button>
    </header>

    <div class="kpi-grid">
      <article v-for="item in kpis" :key="item.label" class="kpi" :data-tone="item.tone">
        <span>{{ item.label }}</span>
        <b>{{ item.value }}</b>
        <em>{{ item.note }}</em>
      </article>
    </div>

    <div class="work-grid">
      <section class="panel patient-panel">
        <div class="panel-head">
          <div>
            <h2>我的患者</h2>
            <p>按主要负责医生归属展示，不提供建档入口。</p>
          </div>
        </div>
        <div class="path-tabs">
          <button
            v-for="tab in carePathTabs"
            :key="tab.key"
            type="button"
            :class="{ active: pathFilter === tab.key }"
            @click="pathFilter = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
        <div class="patient-list">
          <button
            v-for="patient in filteredPatients"
            :key="patient.id"
            class="patient-row"
            :class="{ active: activePatientId === patient.id }"
            type="button"
            @click="selectPatient(patient)"
          >
            <span>
              <b>{{ patient.name }}</b>
              <em>{{ patient.gender || '-' }} · {{ patient.age || '-' }}岁 · {{ patient.phone || patient.phoneMasked || '-' }}</em>
            </span>
            <strong>{{ riskLabel(patient.latest_report_risk_level || patient.risk_level || '') }}</strong>
            <i>{{ patient.path_label || '未分组' }}</i>
            <small>{{ patient.next_followup_at || '待安排复查' }}</small>
          </button>
          <div v-if="!filteredPatients.length" class="empty">暂无匹配患者</div>
        </div>
      </section>

      <section class="panel detail-panel">
        <div class="panel-head">
          <div>
            <h2>患者具体信息</h2>
            <p>{{ activePatient ? `${activePatient.name} · ${noduleLabel(activePatient.nodule_type)}` : '请选择左侧患者' }}</p>
          </div>
        </div>

        <div v-if="activePatient" class="detail-grid">
          <div class="info-card">
            <div class="card-title">基础信息</div>
            <dl>
              <div><dt>姓名</dt><dd>{{ activePatient.name }}</dd></div>
              <div><dt>性别/年龄</dt><dd>{{ activePatient.gender || '-' }} / {{ activePatient.age || '-' }}岁</dd></div>
              <div><dt>手机号</dt><dd>{{ activePatient.phone || '-' }}</dd></div>
              <div><dt>结节类型</dt><dd>{{ noduleLabel(activePatient.nodule_type) }}</dd></div>
              <div><dt>健康管理师</dt><dd>{{ activePatient.manager_name || '-' }}</dd></div>
            </dl>
          </div>

          <div class="info-card" :data-tone="surgeryDecision.tone">
            <div class="card-title">是否需要转手术</div>
            <div class="decision">{{ surgeryDecision.label }}</div>
            <p>{{ surgeryDecision.reason }}</p>
          </div>

          <div class="info-card">
            <div class="card-title">院外复查</div>
            <div v-if="latestTask" class="timeline">
              <div><b>{{ latestTask.title || latestTask.plan_name || '复查随访任务' }}</b><span>{{ taskStatusLabel(latestTask.status) }}</span></div>
              <p>计划时间：{{ latestTask.due_at || latestTask.scheduled_send_at || '-' }}</p>
              <p>触达方式：{{ channelLabel(latestTask.channel) }} · {{ latestTask.manager_name || '健康管理师' }}</p>
              <p v-if="latestTask.abnormal_flag">异常提示：{{ latestTask.abnormal_reason || '患者回复需要医生关注' }}</p>
            </div>
            <div v-else class="empty small">暂无院外复查任务</div>
          </div>

          <div class="info-card">
            <div class="card-title">复查信息</div>
            <div v-if="checkins.length" class="checkin-list">
              <article v-for="item in checkins.slice(0, 4)" :key="item.id">
                <b>{{ checkinTypeLabel(item.checkin_type) }}</b>
                <span>{{ item.submitted_at }} · {{ checkinStatusLabel(item.status) }}</span>
                <p>{{ item.content_text || item.abnormal_reason || '患者已提交复查资料' }}</p>
              </article>
            </div>
            <div v-else class="empty small">暂无患者提交的复查资料</div>
          </div>
        </div>
        <div v-else class="empty">选择患者后查看详情</div>
      </section>

      <section class="panel advice-panel">
        <div class="panel-head">
          <div>
            <h2>用药与复查随访指导</h2>
            <p>{{ activeReport ? activeReport.report_code || `报告 #${activeReport.id}` : '选择患者或报告后填写' }}</p>
          </div>
        </div>

        <div class="report-strip">
          <button
            v-for="report in patientReports"
            :key="report.id"
            class="report-chip"
            :class="{ active: activeReport?.id === report.id }"
            type="button"
            @click="selectReport(report)"
          >
            {{ report.report_code || `报告 #${report.id}` }} · {{ riskLabel(report.risk_level) }}
          </button>
          <div v-if="!patientReports.length" class="empty small">暂无可填写指导的报告</div>
        </div>

        <div v-if="activeReport" class="advice-form">
          <label>
            <span>医生指导</span>
            <textarea
              v-model="adviceForm.advice_content"
              placeholder="填写院外复查周期、用药/禁忌提醒、需要提前返院的症状，以及是否建议外科进一步评估。"
            ></textarea>
          </label>
          <label>
            <span>建议下次复查时间</span>
            <input v-model="adviceForm.suggested_next_followup_at" type="date">
          </label>
          <div class="form-actions">
            <button class="btn" type="button" @click="saveDraft" :disabled="saving">保存草稿</button>
            <button class="primary" type="button" @click="submitAdvice" :disabled="saving || !adviceForm.advice_content.trim()">提交指导</button>
          </div>
        </div>
      </section>

      <section class="panel reports-panel">
        <div class="panel-head">
          <div>
            <h2>待处理报告</h2>
            <p>需要医生补充复查、用药或转诊判断的报告。</p>
          </div>
        </div>
        <div class="pending-list">
          <article v-for="report in pendingReports" :key="report.id" class="pending-row">
            <div>
              <b>{{ report.patient_name || report.patient?.name || `报告 #${report.id}` }}</b>
              <span>{{ report.report_code || '未生成编号' }} · {{ reportStatusLabel(report.status) }}</span>
            </div>
            <em>{{ riskLabel(report.risk_level) }}</em>
            <button class="mini-btn" type="button" @click="selectPendingReport(report)">处理</button>
          </article>
          <div v-if="!pendingReports.length" class="empty">暂无待处理报告</div>
        </div>
      </section>
    </div>

    <div v-if="error" class="toast-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useHospitalApi } from '../composables/useHospitalApi'

const router = useRouter()
const api = useHospitalApi()
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const summary = ref({})
const patients = ref([])
const pendingReports = ref([])
const activePatientId = ref(null)
const activePatient = ref(null)
const patientDetail = ref(null)
const activeReport = ref(null)
const pathFilter = ref('all')
const adviceForm = reactive({ advice_content: '', suggested_next_followup_at: '' })

const carePathTabs = [
  { key: 'all', label: '全部' },
  { key: 'surgery', label: '手术' },
  { key: 'non_surgery_medication', label: '非手术用药' },
  { key: 'non_surgery_observation', label: '非手术观察' },
]
const filteredPatients = computed(() => {
  if (pathFilter.value === 'all') return patients.value
  return patients.value.filter((patient) => patient.path === pathFilter.value)
})
const patientReports = computed(() => patientDetail.value?.reports || [])
const checkins = computed(() => patientDetail.value?.checkins || [])
const latestTask = computed(() => (patientDetail.value?.followup_tasks || [])[0] || null)
const latestReport = computed(() => patientReports.value[0] || activeReport.value || null)
const latestRecord = computed(() => (patientDetail.value?.records || [])[0] || null)
const surgeryDecision = computed(() => makeSurgeryDecision(latestReport.value, latestRecord.value))

const kpis = computed(() => [
  { label: '我的患者', value: summary.value.patient_count ?? patients.value.length, note: '只读查看', tone: 'blue' },
  { label: '待写指导', value: summary.value.pending_advice_count ?? pendingReports.value.length, note: '复查/用药/转诊', tone: 'orange' },
  { label: '高风险患者', value: summary.value.high_risk_count ?? 0, note: '优先判断转诊', tone: 'red' },
  { label: '近期复查', value: summary.value.recent_review_count ?? 0, note: '30天内', tone: 'green' },
])

onMounted(loadData)

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [summaryData, patientsData, reportsData] = await Promise.all([
      api.getDoctorSummary(),
      api.getDoctorPatients(),
      api.getDoctorPendingAdvice(),
    ])
    summary.value = summaryData || {}
    patients.value = patientsData.patients || []
    pendingReports.value = reportsData.reports || []
    if (!activePatient.value && patients.value.length) await selectPatient(patients.value[0])
    if (!activeReport.value && pendingReports.value.length) await selectReport(pendingReports.value[0])
  } catch (e) {
    if (e.status === 403) {
      error.value = ''
      router.replace(roleHome())
    } else {
      error.value = e.message || '加载医生工作台失败'
    }
  } finally {
    loading.value = false
  }
}

async function selectPatient(patient) {
  if (!patient?.id) return
  activePatientId.value = patient.id
  activePatient.value = patient
  patientDetail.value = null
  error.value = ''
  try {
    const detail = await api.getPatientDetail(patient.id)
    patientDetail.value = detail || {}
    activePatient.value = detail.patient || patient
    if (patientReports.value.length) await selectReport(patientReports.value[0])
  } catch (e) {
    error.value = e.message || '加载患者详情失败'
  }
}

async function selectPendingReport(report) {
  const patient = report.patient || patients.value.find((item) => item.id === report.patient_id)
  if (patient) await selectPatient(patient)
  await selectReport(report)
}

async function selectReport(report) {
  if (!report?.id) return
  activeReport.value = report
  adviceForm.advice_content = ''
  adviceForm.suggested_next_followup_at = ''
  try {
    const data = await api.getReportFollowupAdvice(report.id)
    const existing = (data.advices || [])[0]
    if (existing) {
      adviceForm.advice_content = existing.advice_content || ''
      adviceForm.suggested_next_followup_at = existing.suggested_next_followup_at || ''
    }
  } catch (e) {
    // 读取失败不阻断医生填写新指导。
  }
}

async function saveDraft() {
  if (!activeReport.value) return
  await save('draft')
}

async function submitAdvice() {
  if (!activeReport.value) return
  await save('submitted')
}

async function save(status) {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...adviceForm }
    if (status === 'draft') await api.saveReportFollowupAdviceDraft(activeReport.value.id, payload)
    else await api.submitReportFollowupAdvice(activeReport.value.id, payload)
    await loadData()
  } catch (e) {
    error.value = e.message || '保存医生指导失败'
  } finally {
    saving.value = false
  }
}

function makeSurgeryDecision(report, record) {
  const risk = riskLabel(report?.risk_level || '')
  const text = [
    report?.imaging_conclusion,
    report?.risk_advice,
    report?.report_summary,
    record?.birads_level,
    record?.tirads_level,
    record?.thyroid_tirads_level,
    record?.lung_rads_level,
  ].filter(Boolean).join(' ')
  if (/5|4B|4C|高风险|高危|手术|活检|穿刺|外科|恶性|转诊/.test(`${risk} ${text}`)) {
    return { label: '建议外科/专科进一步评估', tone: 'red', reason: '报告或分级提示高风险，需要医生结合影像和病史判断是否转手术。' }
  }
  if (/4A|中风险|中危|进一步检查|密切复查/.test(`${risk} ${text}`)) {
    return { label: '暂不直接转手术，需密切复查', tone: 'orange', reason: '当前更适合按医嘱复查或补充检查，异常变化时再评估转外科。' }
  }
  return { label: '暂不需要转手术', tone: 'green', reason: '当前资料未提示明确手术指征，继续院外复查和随访观察。' }
}

function roleHome() {
  const role = localStorage.getItem('proto_role') || ''
  if (role === 'department_director') return '/department-dashboard'
  if (['admin', 'system_admin'].includes(role)) return '/system'
  return '/analytics'
}

function riskLabel(value) {
  const map = { high: '高风险', medium: '中风险', mid: '中风险', low: '低风险', '高危': '高风险', '中危': '中风险', '低危': '低风险' }
  return map[value] || value || '未评估'
}

function reportStatusLabel(value) {
  const map = { draft: '草稿', generated: '待复核', pending_review: '待复核', finalized: '已归档', archived: '已归档' }
  return map[value] || value || '未知状态'
}

function noduleLabel(type) {
  const map = { breast: '乳腺结节', lung: '肺部结节', thyroid: '甲状腺结节', breast_lung: '乳腺+肺部', breast_thyroid: '乳腺+甲状腺', lung_thyroid: '肺部+甲状腺', triple: '三合并' }
  return map[type] || type || '-'
}

function taskStatusLabel(status) {
  const map = { pending: '待发送', scheduled: '已计划', sent: '已发送', replied: '患者已回复', alert: '异常提醒', manual_processing: '人工处理中', completed: '已完成', cancelled: '已取消' }
  return map[status] || status || '-'
}

function channelLabel(channel) {
  const map = { wecom: '企业微信', miniapp: '小程序', manual: '公开链接', phone: '电话', sms: '短信' }
  return map[channel] || channel || '-'
}

function checkinTypeLabel(type) {
  const map = { report_review: '复查资料', symptom: '症状反馈', lifestyle: '生活方式', medication: '用药反馈', review: '复查反馈' }
  return map[type] || type || '复查反馈'
}

function checkinStatusLabel(status) {
  const map = { submitted: '已提交', analyzed: '已分析', alert: '异常', closed: '已关闭' }
  return map[status] || status || '-'
}
</script>

<style scoped>
.doctor-page{display:grid;gap:16px;color:#0f172a}
.page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px}
.eyebrow{font-size:12px;font-weight:900;color:#2563eb;margin-bottom:4px}
h1{font-size:24px;line-height:1.2;margin:0 0 6px}
p{margin:0;color:#64748b;font-size:13px;line-height:1.6}
.btn,.primary,.mini-btn{height:34px;border-radius:8px;border:1px solid #d9e2ef;background:#fff;color:#334155;font-weight:850;cursor:pointer;padding:0 12px}
.primary{background:#2563eb;border-color:#2563eb;color:#fff}
.mini-btn{height:28px;padding:0 9px}
.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.kpi{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;display:grid;gap:6px}
.kpi span{font-size:12px;color:#64748b;font-weight:850}.kpi b{font-size:24px}.kpi em{font-style:normal;color:#94a3b8;font-size:12px}
.kpi[data-tone="orange"] b{color:#ea580c}.kpi[data-tone="red"] b{color:#dc2626}.kpi[data-tone="green"] b{color:#16a34a}
.work-grid{display:grid;grid-template-columns:340px minmax(0,1fr);gap:12px;align-items:start}
.panel{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;min-width:0}
.advice-panel,.reports-panel{grid-column:1 / -1}
.panel-head{display:flex;justify-content:space-between;gap:12px;margin-bottom:12px}
.panel h2{font-size:15px;margin:0 0 4px}
.path-tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}.path-tabs button{height:30px;border:1px solid #d9e2ef;border-radius:8px;background:#fff;color:#334155;font-size:12px;font-weight:900;padding:0 9px;cursor:pointer}.path-tabs button.active{background:#eff6ff;border-color:#2563eb;color:#1d4ed8}
.patient-list,.pending-list,.checkin-list{display:grid;gap:8px}
.patient-row,.pending-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;border:1px solid #edf2f7;border-radius:8px;background:#fff;padding:10px;text-align:left;cursor:pointer}
.patient-row.active{border-color:#2563eb;background:#eff6ff}
.patient-row b,.pending-row b{display:block;font-size:13px}.patient-row em,.pending-row span{display:block;color:#64748b;font-size:12px;font-style:normal;margin-top:3px}
.patient-row strong{font-size:12px;color:#dc2626}.patient-row i{justify-self:start;font-style:normal;font-size:12px;border-radius:999px;background:#f1f5f9;color:#334155;padding:3px 8px}.patient-row small{grid-column:1 / -1;color:#64748b;font-size:12px}
.detail-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.info-card{border:1px solid #edf2f7;border-radius:8px;padding:12px;background:#fff}
.info-card[data-tone="red"]{background:#fff1f2;border-color:#fecdd3}.info-card[data-tone="orange"]{background:#fff7ed;border-color:#fed7aa}.info-card[data-tone="green"]{background:#f0fdf4;border-color:#bbf7d0}
.card-title{font-size:12px;font-weight:900;color:#64748b;margin-bottom:10px}
.decision{font-size:18px;font-weight:950;margin-bottom:6px}
dl{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0}dl div{display:grid;gap:3px}dt{font-size:11px;color:#94a3b8;font-weight:850}dd{margin:0;font-size:13px;font-weight:850}
.timeline{display:grid;gap:5px}.timeline div{display:flex;justify-content:space-between;gap:8px}.timeline b{font-size:13px}.timeline span{font-size:12px;color:#2563eb;font-weight:900}
.checkin-list article{border-top:1px solid #edf2f7;padding-top:8px}.checkin-list article:first-child{border-top:0;padding-top:0}.checkin-list b{font-size:13px}.checkin-list span{display:block;color:#94a3b8;font-size:12px;margin-top:3px}
.report-strip{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}.report-chip{height:32px;border:1px solid #d9e2ef;border-radius:8px;background:#fff;color:#334155;font-weight:850;padding:0 10px;cursor:pointer}.report-chip.active{background:#eff6ff;border-color:#2563eb;color:#1d4ed8}
.advice-form{display:grid;gap:12px}.advice-form label{display:grid;gap:6px;font-size:12px;color:#64748b;font-weight:850}
textarea,input{border:1px solid #d9e2ef;border-radius:8px;padding:10px;font:inherit;color:#0f172a}
textarea{min-height:150px;resize:vertical}.form-actions{display:flex;justify-content:flex-end;gap:8px}
.pending-row{grid-template-columns:minmax(0,1fr) auto auto}.pending-row em{font-style:normal;font-size:12px;color:#dc2626;font-weight:900}
.empty{padding:20px;text-align:center;color:#94a3b8;font-size:13px}.empty.small{padding:8px;text-align:left}
.toast-error{position:fixed;right:20px;bottom:20px;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;border-radius:8px;padding:10px 12px;font-weight:850}
@media (max-width:1000px){.kpi-grid{grid-template-columns:repeat(2,1fr)}.work-grid{grid-template-columns:1fr}.advice-panel,.reports-panel{grid-column:auto}.detail-grid{grid-template-columns:1fr}}
</style>
