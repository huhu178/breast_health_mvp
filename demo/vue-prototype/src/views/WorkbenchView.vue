<template>
  <div class="page">
    <header class="page-head">
      <div>
        <div class="title">医生工作台</div>
        <div class="sub">表单配置、AI助手和复核任务集中管理</div>
      </div>
      <div class="head-actions">
        <button class="btn" type="button">导入模板</button>
        <button class="primary" type="button">新建表单</button>
      </div>
    </header>

    <div class="kpi-row" aria-label="医生工作台概览">
      <article v-for="item in summaryCards" :key="item.label" class="kpi" :data-tone="item.tone">
        <div class="kpi-label">{{ item.label }}</div>
        <div class="kpi-value">{{ item.value }}</div>
        <div class="kpi-note">{{ item.note }}</div>
      </article>
    </div>

    <div class="workspace-grid">
      <section class="card forms-card">
        <div class="card-head">
          <div>
            <div class="card-title">表单管理</div>
            <div class="card-sub">建档、复查、随访问卷模板</div>
          </div>
          <div class="seg">
            <button
              v-for="tab in formTabs"
              :key="tab"
              type="button"
              :class="{ active: formTab === tab }"
              @click="formTab = tab"
            >
              {{ tab }}
            </button>
          </div>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>表单名称</th>
                <th>适用场景</th>
                <th>字段</th>
                <th>状态</th>
                <th>最近更新</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="form in visibleForms" :key="form.id" :class="{ active: selectedFormId === form.id }" @click="selectedFormId = form.id">
                <td>
                  <div class="main-text">{{ form.name }}</div>
                  <div class="muted">{{ form.owner }}</div>
                </td>
                <td>{{ form.scene }}</td>
                <td>{{ form.fields }}项</td>
                <td><span class="tag" :data-tone="form.statusTone">{{ form.status }}</span></td>
                <td>{{ form.updatedAt }}</td>
                <td><button class="link-btn" type="button">配置</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card task-card">
        <div class="card-head">
          <div>
            <div class="card-title">医生复核队列</div>
            <div class="card-sub">按风险和超时优先级排序</div>
          </div>
          <button class="btn" type="button" @click="loadWorkbenchData">刷新</button>
        </div>
        <div class="task-list">
          <article v-for="task in reviewTasks" :key="task.id" class="task-item">
            <div class="task-top">
              <div>
                <div class="main-text">{{ task.patient }}</div>
                <div class="muted">{{ task.report }} · {{ task.source }}</div>
              </div>
              <span class="tag" :data-tone="task.tone">{{ task.risk }}</span>
            </div>
            <div class="task-meta">
              <span>{{ task.owner }}</span>
              <span>{{ task.deadline }}</span>
              <span>{{ task.status }}</span>
            </div>
            <div class="task-actions">
              <button class="btn" type="button" @click="openPatient(task)">打开档案</button>
              <button class="primary" type="button" @click="openReview(task)">进入复核</button>
            </div>
          </article>
        </div>
      </section>

      <section class="card ai-card">
        <div class="card-head">
          <div>
            <div class="card-title">AI助手管理</div>
            <div class="card-sub">报告、话术、随访任务生成能力</div>
          </div>
          <button class="btn" type="button">模型设置</button>
        </div>

        <div class="assistant-list">
          <article v-for="bot in assistants" :key="bot.id" class="assistant">
            <div class="assistant-head">
              <div>
                <div class="main-text">{{ bot.name }}</div>
                <div class="muted">{{ bot.desc }}</div>
              </div>
              <label class="switch">
                <input v-model="bot.enabled" type="checkbox">
                <span></span>
              </label>
            </div>
            <div class="assistant-metrics">
              <span>今日 {{ bot.today }}</span>
              <span>准确率 {{ bot.accuracy }}</span>
              <span>{{ bot.latency }}</span>
            </div>
          </article>
        </div>

        <div class="config-box">
          <div class="card-title small">当前表单联动</div>
          <div class="selected-form">
            <b>{{ selectedForm.name }}</b>
            <span>{{ selectedForm.scene }} · {{ selectedForm.fields }}项字段</span>
          </div>
          <div class="rules">
            <div v-for="rule in selectedForm.rules" :key="rule" class="rule">
              <span class="dot"></span>{{ rule }}
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const liveReports = ref([])
const loading = ref(false)

const summaryCards = computed(() => {
  const reports = liveReports.value
  const reviewCount = reports.length ? reviewTasks.value.length : 82
  const highRiskCount = reports.filter((item) => riskTone(item.risk_level) === 'red').length
  const generatedCount = reports.filter((item) => !['not_generated', 'finalized', 'published', 'archived'].includes(item.status)).length
  return [
    { label: '启用表单', value: '18', note: '覆盖7类结节场景', tone: 'blue' },
    { label: '今日待复核', value: String(reviewCount), note: reports.length ? `高风险 ${highRiskCount} 份` : '18份已超24小时', tone: 'orange' },
    { label: 'AI生成任务', value: reports.length ? String(generatedCount) : '236', note: reports.length ? '来自报告接口' : '报告/话术/问卷', tone: 'green' },
    { label: '医生平均处理', value: '11.6分', note: loading.value ? '正在刷新' : '较昨日 -1.8分', tone: 'purple' }
  ]
})

const formTabs = ['全部', '建档', '复查', '随访']
const formTab = ref('全部')

const forms = [
  { id: 'f1', type: '建档', name: '乳腺结节首诊建档表', scene: '门诊/体检导入', fields: 42, status: '已启用', statusTone: 'green', owner: '李医生', updatedAt: '05-18 16:20', rules: ['BI-RADS 4A及以上自动标记高风险', '缺少影像报告时提示补充上传', '同步生成报告草稿字段映射'] },
  { id: 'f2', type: '建档', name: '肺部结节联合评估表', scene: '胸部CT复核', fields: 38, status: '已启用', statusTone: 'green', owner: '王医生', updatedAt: '05-17 10:45', rules: ['Lung-RADS 4类进入优先复核', '磨玻璃结节自动匹配3个月随访模板', '吸烟史字段参与风险提示'] },
  { id: 'f3', type: '复查', name: '多结节复查结果表', scene: '复查资料回收', fields: 31, status: '试运行', statusTone: 'orange', owner: '赵医生', updatedAt: '05-16 18:12', rules: ['结节增大自动进入异常队列', '复查时间超期触发企微提醒', '支持补充PDF影像报告'] },
  { id: 'f4', type: '随访', name: '术后/穿刺后随访问卷', scene: '小程序打卡', fields: 26, status: '已启用', statusTone: 'green', owner: '李医生', updatedAt: '05-15 09:30', rules: ['疼痛/出血等异常答案触发人工交接', '自动汇总给随访AI生成回复', '7天未填报进入待联系队列'] }
]

const selectedFormId = ref(forms[0].id)
const visibleForms = computed(() => forms.filter((item) => formTab.value === '全部' || item.type === formTab.value))
const selectedForm = computed(() => forms.find((item) => item.id === selectedFormId.value) || forms[0])

const mockReviewTasks = [
  { id: 't1', patient: '张*国', report: '肺部结节健康报告', source: '胸部CT', risk: '高风险', tone: 'red', owner: '李医生', deadline: '剩余 1小时', status: '待医生复核' },
  { id: 't2', patient: '吴*丽', report: '乳腺+甲状腺报告', source: '超声报告', risk: '高风险', tone: 'red', owner: '王医生', deadline: '已超时 2小时', status: '待补充意见' },
  { id: 't3', patient: '周*明', report: '肺部+甲状腺报告', source: 'CT/超声', risk: '中风险', tone: 'orange', owner: '李医生', deadline: '今天 17:30', status: '待复核' }
]

const liveReviewTasks = computed(() => {
  return liveReports.value
    .filter((item) => !['not_generated', 'finalized', 'published', 'archived'].includes(item.status))
    .slice(0, 8)
    .map((item) => ({
      id: item.id,
      patientId: item.patient_id,
      patient: item.patient_name || item.patient?.name || '未命名患者',
      report: item.report_code || item.report_type || '健康报告',
      source: noduleLabel(item.nodule_type),
      risk: riskLabel(item.risk_level),
      tone: riskTone(item.risk_level),
      owner: item.patient?.manager_name || '李医生',
      deadline: deadlineLabel(item.updated_at || item.created_at),
      status: reportStatusLabel(item.status)
    }))
})

const reviewTasks = computed(() => liveReviewTasks.value.length ? liveReviewTasks.value : mockReviewTasks)

const assistants = reactive([
  { id: 'a1', name: '报告生成助手', desc: '按表单字段生成报告草稿与风险提示', enabled: true, today: 126, accuracy: '96.8%', latency: '12秒' },
  { id: 'a2', name: '随访话术助手', desc: '按风险等级生成企微/电话随访话术', enabled: true, today: 74, accuracy: '94.1%', latency: '8秒' },
  { id: 'a3', name: '异常预警助手', desc: '识别打卡异常和复查资料变化', enabled: true, today: 31, accuracy: '92.6%', latency: '5秒' },
  { id: 'a4', name: '表单质控助手', desc: '发现缺失字段、冲突字段和补录建议', enabled: false, today: 5, accuracy: '试运行', latency: '待启用' }
])

onMounted(loadWorkbenchData)

async function loadWorkbenchData() {
  loading.value = true
  try {
    const res = await fetch('/api/b/reports?page=1&per_page=50&include_unreported=1', { credentials: 'include' })
    const payload = await res.json()
    if (!res.ok || payload.success === false) throw new Error(payload.message || '加载失败')
    liveReports.value = payload.data?.reports || payload.reports || []
  } catch (e) {
    liveReports.value = []
  } finally {
    loading.value = false
  }
}

function openPatient(task) {
  router.push({ path: '/patient', query: { tab: 'detail', patient_id: task.patientId || '' } })
}

function openReview(task) {
  router.push({ path: '/patient', query: { tab: 'review', patient_id: task.patientId || '' } })
}

function riskLabel(risk) {
  const map = { high: '高风险', mid: '中风险', medium: '中风险', low: '低风险', '高危': '高风险', '中危': '中风险', '低危': '低风险' }
  return map[risk] || risk || '待评估'
}

function riskTone(risk) {
  const label = riskLabel(risk)
  if (label === '高风险') return 'red'
  if (label === '中风险') return 'orange'
  return 'green'
}

function noduleLabel(type) {
  const map = {
    breast: '乳腺结节',
    lung: '肺部结节',
    thyroid: '甲状腺结节',
    breast_lung: '乳腺+肺部结节',
    breast_thyroid: '乳腺+甲状腺结节',
    lung_thyroid: '肺部+甲状腺结节',
    triple: '三合并结节'
  }
  return map[type] || type || '结节随访'
}

function reportStatusLabel(status) {
  const map = {
    draft: '待医生复核',
    generated: '待医生复核',
    reviewing: '审核中',
    not_generated: '待生成报告'
  }
  return map[status] || status || '待处理'
}

function deadlineLabel(value) {
  if (!value) return '待处理'
  const time = new Date(value.replace?.(' ', 'T') || value)
  if (Number.isNaN(time.getTime())) return '待处理'
  const hours = Math.floor((Date.now() - time.getTime()) / 36e5)
  if (hours >= 24) return `已等待 ${Math.floor(hours / 24)}天`
  if (hours >= 1) return `已等待 ${hours}小时`
  return '刚刚更新'
}
</script>

<style scoped>
.page{display:grid;gap:12px;padding-bottom:20px}
.page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px}
.title{font-size:20px;font-weight:800;color:#0f172a}
.sub,.card-sub,.muted{color:#64748b;font-size:12px}
.head-actions,.task-actions{display:flex;gap:8px;flex-wrap:wrap}
.btn,.primary,.link-btn{height:32px;border-radius:6px;padding:0 10px;font-weight:600;cursor:pointer}
.btn{border:1px solid #d9e2ef;background:#fff;color:#475569}
.primary{border:1px solid #155eef;background:#155eef;color:#fff}
.link-btn{border:0;background:transparent;color:#155eef;padding:0}
.kpi-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.kpi{background:#fff;border:1px solid #e6edf7;border-radius:10px;padding:12px;box-shadow:0 4px 12px rgba(15,23,42,.04)}
.kpi-label{color:#64748b;font-size:12px}
.kpi-value{font-size:26px;font-weight:800;color:#0f172a;margin-top:6px}
.kpi-note{font-size:12px;color:#94a3b8;margin-top:4px}
.kpi[data-tone="orange"] .kpi-value{color:#ea580c}
.kpi[data-tone="green"] .kpi-value{color:#15803d}
.kpi[data-tone="purple"] .kpi-value{color:#6d28d9}
.workspace-grid{display:grid;grid-template-columns:minmax(520px,1.4fr) minmax(300px,.8fr) minmax(360px,1fr);gap:12px;align-items:start}
.card{background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 4px 12px rgba(15,23,42,.04);overflow:hidden}
.card-head{min-height:48px;border-bottom:1px solid #eef2f7;padding:10px 12px;display:flex;align-items:center;justify-content:space-between;gap:10px}
.card-title{font-weight:800;color:#0f172a}
.card-title.small{font-size:13px}
.seg{display:flex;gap:4px;border:1px solid #e6edf7;border-radius:8px;padding:3px;background:#f8fafc}
.seg button{height:26px;border:0;border-radius:6px;background:transparent;color:#64748b;font-weight:600;padding:0 8px;cursor:pointer}
.seg button.active{background:#fff;color:#155eef;box-shadow:0 1px 3px rgba(15,23,42,.08)}
.table-wrap{overflow:auto}
.table{width:100%;border-collapse:collapse;min-width:720px}
.table th{background:#f8fafc;color:#64748b;text-align:left;font-size:12px;font-weight:600;padding:8px;border-bottom:1px solid #e5edf7;white-space:nowrap}
.table td{padding:9px 8px;border-bottom:1px solid #edf2f7;white-space:nowrap;font-size:13px}
.table tr.active{background:#eef5ff}
.main-text{font-weight:800;color:#0f172a}
.tag{display:inline-flex;align-items:center;border-radius:999px;padding:3px 8px;font-size:12px;font-weight:700;background:#eef5ff;color:#155eef}
.tag[data-tone="green"]{background:#ecfdf5;color:#15803d}
.tag[data-tone="orange"]{background:#fff7ed;color:#c2410c}
.tag[data-tone="red"]{background:#fff1f2;color:#dc2626}
.task-list,.assistant-list{display:grid;gap:10px;padding:12px}
.task-item,.assistant,.config-box{border:1px solid #edf2f7;border-radius:8px;padding:10px;background:#fff}
.task-top,.assistant-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.task-meta,.assistant-metrics{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;color:#64748b;font-size:12px}
.task-meta span,.assistant-metrics span{background:#f8fafc;border:1px solid #edf2f7;border-radius:999px;padding:3px 8px}
.task-actions{margin-top:10px;justify-content:flex-end}
.ai-card{display:flex;flex-direction:column}
.switch{position:relative;display:inline-block;width:38px;height:22px;flex-shrink:0}
.switch input{opacity:0;width:0;height:0}
.switch span{position:absolute;inset:0;background:#cbd5e1;border-radius:999px;cursor:pointer;transition:.15s}
.switch span::before{content:"";position:absolute;width:18px;height:18px;left:2px;top:2px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(15,23,42,.2);transition:.15s}
.switch input:checked + span{background:#155eef}
.switch input:checked + span::before{transform:translateX(16px)}
.config-box{margin:0 12px 12px;background:#f8fbff;border-color:#dbeafe}
.selected-form{display:grid;gap:3px;margin-top:10px}
.selected-form span{color:#64748b;font-size:12px}
.rules{display:grid;gap:8px;margin-top:10px}
.rule{display:flex;align-items:flex-start;gap:8px;color:#334155;font-size:13px;line-height:1.5}
.dot{width:7px;height:7px;border-radius:50%;background:#155eef;margin-top:6px;flex-shrink:0}
@media(max-width:1200px){
  .workspace-grid{grid-template-columns:1fr}
  .kpi-row{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:720px){
  .page-head{align-items:flex-start;flex-direction:column}
  .kpi-row{grid-template-columns:1fr}
  .card-head{align-items:flex-start;flex-direction:column}
}
</style>
