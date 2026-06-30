<template>
  <div class="assistant-page">
    <header class="page-head">
      <div>
        <div class="eyebrow">医生助理工作台</div>
        <h1>线上智脑营销与线下医生患者池</h1>
        <p>线上承接智脑营销，线下按科室、医生和患者路径跟进手术/非手术服务。</p>
      </div>
      <button class="btn" type="button" @click="loadOffline">刷新</button>
    </header>

    <div class="mode-tabs">
      <button type="button" :class="{ active: mode === 'online' }" @click="mode = 'online'">线上 · 智脑营销</button>
      <button type="button" :class="{ active: mode === 'offline' }" @click="mode = 'offline'">线下 · 医生患者池</button>
    </div>

    <section v-if="mode === 'online'" class="online-grid">
      <article v-for="item in onlineCards" :key="item.title" class="online-card">
        <span>{{ item.icon }}</span>
        <b>{{ item.title }}</b>
        <p>{{ item.desc }}</p>
        <button class="primary" type="button" @click="goMarketing(item.path)">进入</button>
      </article>
    </section>

    <section v-else class="offline-layout">
      <div class="kpi-grid">
        <article class="kpi"><span>医生数</span><b>{{ doctors.length }}</b><em>可按医生查看</em></article>
        <article class="kpi red"><span>手术路径</span><b>{{ pathCounts.surgery || 0 }}</b><em>术前注意事项</em></article>
        <article class="kpi orange"><span>非手术用药</span><b>{{ pathCounts.non_surgery_medication || 0 }}</b><em>首诊/复诊/换药</em></article>
        <article class="kpi green"><span>非手术观察</span><b>{{ pathCounts.non_surgery_observation || 0 }}</b><em>不用药复查跟进</em></article>
      </div>

      <div class="filters">
        <select v-model="doctorId" @change="loadOffline">
          <option value="">全部医生</option>
          <option v-for="item in doctors" :key="item.doctor.id" :value="item.doctor.id">{{ item.doctor.real_name || item.doctor.username }}</option>
        </select>
        <select v-model="pathFilter">
          <option value="">全部路径</option>
          <option value="surgery">手术</option>
          <option value="non_surgery_medication">非手术 · 用药</option>
          <option value="non_surgery_observation">非手术 · 不吃药</option>
        </select>
      </div>

      <main class="offline-grid">
        <section class="panel doctors-panel">
          <div class="panel-head">
            <h2>医生维度</h2>
            <p>按医生名下患者查看服务路径。</p>
          </div>
          <button
            v-for="item in doctors"
            :key="item.doctor.id"
            type="button"
            class="doctor-row"
            :class="{ active: String(doctorId) === String(item.doctor.id) }"
            @click="selectDoctor(item.doctor.id)"
          >
            <b>{{ item.doctor.real_name || item.doctor.username }}</b>
            <span>{{ item.patient_count }} 人 · 手术 {{ item.surgery_count }} · 用药 {{ item.medication_count }} · 观察 {{ item.observation_count }}</span>
          </button>
        </section>

        <section class="panel patient-panel">
          <div class="panel-head">
            <h2>患者服务池</h2>
            <p>线下跟进口径：手术前注意事项、用药首诊复诊换药、不吃药复查观察。</p>
          </div>
          <div class="patient-table">
            <div class="table-head"><span>患者</span><span>医生</span><span>路径</span><span>后续动作</span></div>
            <article v-for="patient in filteredPatients" :key="patient.id" class="patient-row">
              <span><b>{{ patient.name }}</b><em>{{ noduleLabel(patient.nodule_type) }} · {{ riskLabel(patient.latest_report_risk_level) }}</em></span>
              <span>{{ patient.primary_doctor_name || '-' }}</span>
              <span><strong :data-path="patient.path">{{ patient.path_label }}</strong><em>{{ patient.service_focus }}</em></span>
              <span>{{ patient.next_action }}</span>
            </article>
            <div v-if="!filteredPatients.length" class="empty">暂无匹配患者</div>
          </div>
        </section>
      </main>
    </section>

    <div v-if="error" class="toast-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useHospitalApi } from '../composables/useHospitalApi'

const router = useRouter()
const api = useHospitalApi()
const mode = ref('online')
const doctors = ref([])
const patients = ref([])
const pathCounts = ref({})
const doctorId = ref('')
const pathFilter = ref('')
const error = ref('')

const onlineCards = [
  { icon: '营', title: '智脑营销看板', desc: '医生 IP、内容触达、线索承接与转化概览。', path: '/ai-employee/overview' },
  { icon: '脑', title: '营销智脑', desc: '按医生和科室配置线上内容、话术和触达策略。', path: '/ai-employee/super-employee' },
  { icon: '文', title: '内容科普', desc: '围绕术前注意事项、用药指导和复查提醒生成内容。', path: '/ai-employee/content' },
]

const filteredPatients = computed(() => {
  let list = patients.value
  if (pathFilter.value) list = list.filter((item) => item.path === pathFilter.value)
  return list
})

onMounted(loadOffline)

async function loadOffline() {
  error.value = ''
  try {
    const data = await api.getAssistantOffline({ doctor_id: doctorId.value })
    doctors.value = data.doctors || []
    patients.value = data.patients || []
    pathCounts.value = data.path_counts || {}
  } catch (e) {
    error.value = e.message || '加载医生助理工作台失败'
  }
}

function selectDoctor(id) {
  doctorId.value = String(id || '')
  loadOffline()
}

function goMarketing(path) {
  router.push(path)
}

function riskLabel(value) {
  const map = { high: '高风险', medium: '中风险', mid: '中风险', low: '低风险', '高危': '高风险', '中危': '中风险', '低危': '低风险' }
  return map[value] || value || '未评估'
}

function noduleLabel(type) {
  const map = { breast: '乳腺结节', lung: '肺部结节', thyroid: '甲状腺结节', breast_lung: '乳腺+肺部', breast_thyroid: '乳腺+甲状腺', lung_thyroid: '肺部+甲状腺', triple: '三合并' }
  return map[type] || type || '-'
}
</script>

<style scoped>
.assistant-page{display:grid;gap:16px;color:#0f172a}
.page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px}
.eyebrow{font-size:12px;font-weight:900;color:#2563eb;margin-bottom:4px}
h1{font-size:24px;line-height:1.2;margin:0 0 6px}p{margin:0;color:#64748b;font-size:13px;line-height:1.6}
.btn,.primary{height:34px;border-radius:8px;border:1px solid #d9e2ef;background:#fff;color:#334155;font-weight:850;cursor:pointer;padding:0 12px}.primary{background:#2563eb;border-color:#2563eb;color:#fff}
.mode-tabs{display:flex;gap:8px}.mode-tabs button{height:36px;border:1px solid #d9e2ef;border-radius:8px;background:#fff;color:#334155;font-weight:900;padding:0 14px;cursor:pointer}.mode-tabs button.active{background:#eff6ff;border-color:#2563eb;color:#1d4ed8}
.online-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.online-card{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:16px;display:grid;gap:10px}.online-card span{width:36px;height:36px;border-radius:8px;background:#eff6ff;color:#2563eb;display:grid;place-items:center;font-weight:950}.online-card b{font-size:16px}
.offline-layout{display:grid;gap:12px}.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.kpi{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;display:grid;gap:6px}.kpi span{font-size:12px;color:#64748b;font-weight:850}.kpi b{font-size:24px}.kpi em{font-style:normal;color:#94a3b8;font-size:12px}.kpi.red b{color:#dc2626}.kpi.orange b{color:#ea580c}.kpi.green b{color:#16a34a}
.filters{display:flex;gap:10px}.filters select{height:36px;border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:0 10px;color:#334155;font-weight:850}
.offline-grid{display:grid;grid-template-columns:320px minmax(0,1fr);gap:12px}.panel{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;min-width:0}.panel-head{margin-bottom:12px}.panel h2{font-size:15px;margin:0 0 4px}
.doctor-row{width:100%;border:1px solid #edf2f7;border-radius:8px;background:#fff;padding:10px;text-align:left;display:grid;gap:4px;margin-bottom:8px;cursor:pointer}.doctor-row.active{border-color:#2563eb;background:#eff6ff}.doctor-row b{font-size:13px}.doctor-row span{font-size:12px;color:#64748b}
.patient-table{border:1px solid #edf2f7;border-radius:8px;overflow:hidden}.table-head,.patient-row{display:grid;grid-template-columns:1.2fr .8fr 1fr 1.6fr;gap:10px;align-items:center;padding:10px 12px}.table-head{background:#f8fafc;color:#64748b;font-size:12px;font-weight:900}.patient-row{border-top:1px solid #edf2f7}.patient-row b{display:block;font-size:13px}.patient-row em{display:block;color:#64748b;font-size:12px;font-style:normal;margin-top:3px}.patient-row strong{display:inline-block;font-size:12px;border-radius:999px;padding:3px 8px;background:#eff6ff;color:#1d4ed8}.patient-row strong[data-path="surgery"]{background:#fff1f2;color:#be123c}.patient-row strong[data-path="non_surgery_medication"]{background:#fff7ed;color:#c2410c}.patient-row strong[data-path="non_surgery_observation"]{background:#f0fdf4;color:#15803d}
.empty{padding:20px;text-align:center;color:#94a3b8;font-size:13px}.toast-error{position:fixed;right:20px;bottom:20px;background:#fee2e2;color:#991b1b;border:1px solid #fecaca;border-radius:8px;padding:10px 12px;font-weight:850}
@media (max-width:1000px){.online-grid,.kpi-grid{grid-template-columns:repeat(2,1fr)}.offline-grid{grid-template-columns:1fr}.table-head,.patient-row{grid-template-columns:1fr}}
</style>
