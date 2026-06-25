<template>
  <div class="dept-page">
    <header class="page-head">
      <div>
        <div class="eyebrow">科室主任看板</div>
        <h1>本科室患者管理总览</h1>
        <p>科室主任只查看本科室患者、医生、风险分层和随访完成情况。</p>
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

    <div class="board-grid">
      <section class="panel">
        <div class="panel-head">
          <div>
            <h2>风险分布</h2>
            <p>来自本科室患者报告风险等级。</p>
          </div>
        </div>
        <div class="risk-list">
          <div v-for="item in riskRows" :key="item.label" class="risk-row">
            <span>{{ item.label }}</span>
            <div class="bar"><i :style="{ width: item.width, background: item.color }"></i></div>
            <b>{{ item.value }}</b>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <div>
            <h2>医生统计</h2>
            <p>按本科室医生查看患者管理数量。</p>
          </div>
        </div>
        <div class="doctor-list">
          <div class="table-head"><span>医生</span><span>患者数</span><span>高风险</span><span>待建议</span><span>完成率</span></div>
          <div v-for="row in doctors" :key="row.doctor?.id" class="table-row">
            <span><b>{{ row.doctor?.real_name || row.doctor?.username || '-' }}</b><em>{{ row.doctor?.phone || '' }}</em></span>
            <span>{{ row.patient_count }}</span>
            <span>{{ row.high_risk_count }}</span>
            <span>{{ row.pending_advice_count }}</span>
            <span>{{ row.followup_completion_rate }}%</span>
          </div>
          <div v-if="!doctors.length" class="empty">暂无医生统计</div>
        </div>
      </section>

      <section class="panel abnormal-panel">
        <div class="panel-head">
          <div>
            <h2>异常患者</h2>
            <p>来自随访任务异常标记。</p>
          </div>
        </div>
        <div class="abnormal-list">
          <button v-for="row in abnormalPatients" :key="row.task?.id" class="abnormal-row" type="button" @click="openPatient(row.patient)">
            <span><b>{{ row.patient?.name || '-' }}</b><em>{{ row.patient?.primary_doctor_name || '未配置医生' }}</em></span>
            <span>{{ row.abnormal_reason || row.task?.abnormal_reason || '异常待处理' }}</span>
            <span>{{ row.latest_followup_at || row.task?.updated_at || row.task?.created_at || '-' }}</span>
          </button>
          <div v-if="!abnormalPatients.length" class="empty">暂无异常患者</div>
        </div>
      </section>
    </div>

    <div v-if="error" class="toast-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useHospitalApi } from '../composables/useHospitalApi'

const router = useRouter()
const api = useHospitalApi()
const summary = ref({})
const doctors = ref([])
const abnormalPatients = ref([])
const error = ref('')

const kpis = computed(() => [
  { label: '患者总数', value: summary.value.patient_count ?? 0, note: '本科室', tone: 'blue' },
  { label: '本月新增', value: summary.value.new_this_month ?? 0, note: '自然月', tone: 'green' },
  { label: '随访完成率', value: `${summary.value.followup_completion_rate ?? 0}%`, note: '全部任务', tone: 'blue' },
  { label: '超期任务', value: summary.value.overdue_task_count ?? 0, note: '需跟进', tone: 'red' },
])

const riskRows = computed(() => {
  const dist = summary.value.risk_distribution || {}
  const rows = [
    { label: '高风险', keys: ['高风险', '高危', 'high'], color: '#dc2626' },
    { label: '中风险', keys: ['中风险', '中危', 'medium', 'mid'], color: '#ea580c' },
    { label: '低风险', keys: ['低风险', '低危', 'low'], color: '#16a34a' },
    { label: '未评估', keys: ['未评估', null, ''], color: '#94a3b8' },
  ].map((item) => {
    const value = item.keys.reduce((sum, key) => sum + Number(dist[key] || 0), 0)
    return { ...item, value }
  })
  const max = Math.max(...rows.map((row) => row.value), 1)
  return rows.map((row) => ({ ...row, width: `${Math.max(8, Math.round((row.value / max) * 100))}%` }))
})

onMounted(loadData)

async function loadData() {
  error.value = ''
  try {
    const [summaryData, doctorsData, abnormalData] = await Promise.all([
      api.getDepartmentSummary(),
      api.getDepartmentDoctors(),
      api.getDepartmentAbnormalPatients(),
    ])
    summary.value = summaryData || {}
    doctors.value = doctorsData.doctors || []
    abnormalPatients.value = abnormalData.patients || []
  } catch (e) {
    error.value = e.message || '加载科室看板失败'
  }
}

function openPatient(patient) {
  if (!patient?.id) return
  router.push({ path: '/patient', query: { tab: 'detail', patient_id: patient.id } })
}
</script>

<style scoped>
.dept-page{display:grid;gap:16px;color:#0f172a}
.page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px}
.eyebrow{font-size:12px;font-weight:900;color:#2563eb;margin-bottom:4px}
h1{font-size:24px;line-height:1.2;margin:0 0 6px}p{margin:0;color:#64748b;font-size:13px}
.btn{height:34px;border-radius:8px;border:1px solid #d9e2ef;background:#fff;color:#334155;font-weight:850;cursor:pointer;padding:0 12px}
.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.kpi{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;display:grid;gap:6px}
.kpi span{font-size:12px;color:#64748b;font-weight:850}.kpi b{font-size:24px}.kpi em{font-style:normal;color:#94a3b8;font-size:12px}
.kpi[data-tone="green"] b{color:#16a34a}.kpi[data-tone="red"] b{color:#dc2626}
.board-grid{display:grid;grid-template-columns:1fr 1.3fr;gap:12px;align-items:start}
.panel{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;min-width:0}
.abnormal-panel{grid-column:1 / -1}
.panel-head{margin-bottom:12px}.panel h2{font-size:15px;margin:0 0 4px}
.risk-list{display:grid;gap:12px}.risk-row{display:grid;grid-template-columns:72px minmax(0,1fr) 50px;gap:10px;align-items:center;font-size:13px}
.bar{height:10px;border-radius:999px;background:#f1f5f9;overflow:hidden}.bar i{display:block;height:100%;border-radius:999px}
.doctor-list,.abnormal-list{border:1px solid #edf2f7;border-radius:8px;overflow:hidden}
.table-head,.table-row{display:grid;grid-template-columns:1.4fr .7fr .7fr .7fr .7fr;gap:10px;padding:10px 12px;align-items:center}
.table-head{background:#f8fafc;color:#64748b;font-size:12px;font-weight:900}.table-row{border-top:1px solid #edf2f7}
.table-row b,.abnormal-row b{display:block;font-size:13px}.table-row em,.abnormal-row em{display:block;color:#64748b;font-size:12px;font-style:normal;margin-top:3px}
.abnormal-row{width:100%;display:grid;grid-template-columns:1fr 1.4fr 1fr;gap:12px;padding:10px 12px;border:0;border-top:1px solid #edf2f7;background:#fff;text-align:left;cursor:pointer}
.abnormal-row:first-child{border-top:0}.empty{padding:20px;text-align:center;color:#94a3b8;font-size:13px}
.toast-error{position:fixed;right:20px;bottom:20px;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;border-radius:8px;padding:10px 12px;font-weight:850}
@media (max-width:900px){.kpi-grid{grid-template-columns:repeat(2,1fr)}.board-grid{grid-template-columns:1fr}}
</style>
