<template>
  <div class="doctor-page">
    <header class="page-head">
      <div>
        <div class="eyebrow">医生工作台</div>
        <h1>我的患者与报告随访建议</h1>
        <p>医生只查看本人相关患者，并填写报告随访建议。</p>
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
      <section class="panel">
        <div class="panel-head">
          <div>
            <h2>待填写报告随访建议</h2>
            <p>报告审核后，医生填写一段随访建议即可。</p>
          </div>
        </div>
        <div class="report-list">
          <article v-for="report in pendingReports" :key="report.id" class="report-row" :class="{ active: activeReport?.id === report.id }" @click="selectReport(report)">
            <div>
              <b>{{ report.patient_name || report.patient?.name || `报告 #${report.id}` }}</b>
              <span>{{ report.report_code || '未生成编号' }} · {{ reportStatusLabel(report.status) }}</span>
            </div>
            <em>{{ riskLabel(report.risk_level) }}</em>
            <button class="mini-btn" type="button" @click.stop="openPatient(report.patient || { id: report.patient_id })">详情</button>
          </article>
          <div v-if="!pendingReports.length" class="empty">暂无待填写建议的报告</div>
        </div>
      </section>

      <section class="panel advice-panel">
        <div class="panel-head">
          <div>
            <h2>报告随访建议</h2>
            <p>{{ activeReport ? activeReport.report_code || `报告 #${activeReport.id}` : '请选择左侧报告' }}</p>
          </div>
        </div>
        <div v-if="activeReport" class="advice-form">
          <label>
            <span>建议内容</span>
            <textarea v-model="adviceForm.advice_content" placeholder="例如：建议6个月后复查乳腺超声，期间按计划随访。"></textarea>
          </label>
          <label>
            <span>建议下次随访时间</span>
            <input v-model="adviceForm.suggested_next_followup_at" type="date">
          </label>
          <div class="form-actions">
            <button class="btn" type="button" @click="saveDraft" :disabled="saving">保存草稿</button>
            <button class="primary" type="button" @click="submitAdvice" :disabled="saving || !adviceForm.advice_content.trim()">提交建议</button>
          </div>
        </div>
        <div v-else class="empty">选择一份报告后填写建议</div>
      </section>

      <section class="panel patients-panel">
        <div class="panel-head">
          <div>
            <h2>我的患者</h2>
            <p>仅展示当前医生作为主要负责医生的患者。</p>
          </div>
        </div>
        <div class="patient-table">
          <div class="table-head"><span>患者</span><span>结节</span><span>风险</span><span>下次随访</span></div>
          <button v-for="patient in patients" :key="patient.id" class="table-row" type="button" @click="openPatient(patient)">
            <span><b>{{ patient.name }}</b><em>{{ patient.gender || '-' }} · {{ patient.age || '-' }}岁</em></span>
            <span>{{ noduleLabel(patient.nodule_type) }}</span>
            <span>{{ riskLabel(patient.latest_report_risk_level || patient.risk_level || '') }}</span>
            <span>{{ patient.next_followup_at || '-' }}</span>
          </button>
          <div v-if="!patients.length" class="empty">暂无患者</div>
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
const activeReport = ref(null)
const adviceForm = reactive({ advice_content: '', suggested_next_followup_at: '' })

const kpis = computed(() => [
  { label: '我的患者', value: summary.value.patient_count ?? patients.value.length, note: '当前医生负责', tone: 'blue' },
  { label: '待写建议', value: summary.value.pending_advice_count ?? pendingReports.value.length, note: '报告随访建议', tone: 'orange' },
  { label: '高风险患者', value: summary.value.high_risk_count ?? 0, note: '优先查看', tone: 'red' },
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
    if (!activeReport.value && pendingReports.value.length) selectReport(pendingReports.value[0])
  } catch (e) {
    error.value = e.message || '加载医生工作台失败'
  } finally {
    loading.value = false
  }
}

async function selectReport(report) {
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
    // 读取失败不阻断医生填写新建议。
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
    error.value = e.message || '保存报告随访建议失败'
  } finally {
    saving.value = false
  }
}

function openPatient(patient) {
  router.push({ path: '/patient', query: { tab: 'detail', patient_id: patient.id } })
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
</script>

<style scoped>
.doctor-page{display:grid;gap:16px;color:#0f172a}
.page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px}
.eyebrow{font-size:12px;font-weight:900;color:#2563eb;margin-bottom:4px}
h1{font-size:24px;line-height:1.2;margin:0 0 6px}
p{margin:0;color:#64748b;font-size:13px}
.btn,.primary{height:34px;border-radius:8px;border:1px solid #d9e2ef;background:#fff;color:#334155;font-weight:850;cursor:pointer;padding:0 12px}
.primary{background:#2563eb;border-color:#2563eb;color:#fff}
.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.kpi{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;display:grid;gap:6px}
.kpi span{font-size:12px;color:#64748b;font-weight:850}.kpi b{font-size:24px}.kpi em{font-style:normal;color:#94a3b8;font-size:12px}
.kpi[data-tone="orange"] b{color:#ea580c}.kpi[data-tone="red"] b{color:#dc2626}.kpi[data-tone="green"] b{color:#16a34a}
.work-grid{display:grid;grid-template-columns:360px minmax(0,1fr);gap:12px;align-items:start}
.panel{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;min-width:0}
.patients-panel{grid-column:1 / -1}
.panel-head{display:flex;justify-content:space-between;gap:12px;margin-bottom:12px}
.panel h2{font-size:15px;margin:0 0 4px}
.report-list{display:grid;gap:8px}
.report-row{display:grid;grid-template-columns:minmax(0,1fr) auto auto;align-items:center;gap:12px;border:1px solid #edf2f7;border-radius:8px;padding:10px;cursor:pointer}
.report-row.active{border-color:#2563eb;background:#eff6ff}
.report-row b,.table-row b{display:block;font-size:13px}.report-row span,.table-row em{display:block;color:#64748b;font-size:12px;font-style:normal;margin-top:3px}
.report-row em{font-style:normal;font-size:12px;color:#dc2626;font-weight:900}
.mini-btn{height:28px;border:1px solid #d9e2ef;border-radius:7px;background:#fff;color:#334155;font-weight:850;cursor:pointer;padding:0 9px}
.advice-form{display:grid;gap:12px}.advice-form label{display:grid;gap:6px;font-size:12px;color:#64748b;font-weight:850}
textarea,input{border:1px solid #d9e2ef;border-radius:8px;padding:10px;font:inherit;color:#0f172a}
textarea{min-height:160px;resize:vertical}.form-actions{display:flex;justify-content:flex-end;gap:8px}
.patient-table{display:grid;gap:0;border:1px solid #edf2f7;border-radius:8px;overflow:hidden}
.table-head,.table-row{display:grid;grid-template-columns:1.4fr 1fr .8fr 1.2fr;gap:10px;align-items:center;padding:10px 12px}
.table-head{background:#f8fafc;color:#64748b;font-size:12px;font-weight:900}.table-row{border:0;border-top:1px solid #edf2f7;background:#fff;text-align:left;cursor:pointer}
.empty{padding:20px;text-align:center;color:#94a3b8;font-size:13px}
.toast-error{position:fixed;right:20px;bottom:20px;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;border-radius:8px;padding:10px 12px;font-weight:850}
@media (max-width:900px){.kpi-grid{grid-template-columns:repeat(2,1fr)}.work-grid{grid-template-columns:1fr}}
</style>
