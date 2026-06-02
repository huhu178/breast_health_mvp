<template>
  <div class="page">

    <!-- KPI 概览 -->
    <div class="kpi-row" aria-label="运营关键指标">
      <article v-for="m in metrics" :key="m.label" class="kpi" :data-tone="m.tone">
        <div class="kpi-ico" aria-hidden="true">
          <svg v-if="iconPath(m.icon)" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path :d="iconPath(m.icon)" />
          </svg>
          <span v-else>{{ m.icon }}</span>
        </div>
        <div class="kpi-label">{{ m.label }}</div>
        <div class="kpi-value">{{ m.value }}</div>
        <div class="kpi-delta">{{ m.delta }}</div>
        <svg class="spark" :class="m.tone !== 'blue' ? m.tone : ''" viewBox="0 0 70 26" aria-hidden="true">
          <path :d="sparkPath(m.delta)" />
        </svg>
      </article>
    </div>

    <!-- 七类结节总览表（核心区，优先展示） -->
    <section class="card">
      <div class="card-head">
        <div class="head-left">
          <div class="card-title">七类结节运营总览 · {{ scenario.loginLabel }}</div>
        </div>
        <div class="head-actions">
          <button class="btn">导出统计</button>
          <button class="btn">查看明细</button>
        </div>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>结节类型</th><th>{{ scenario.personLabel }}数</th><th>{{ scenario.sourceOptions[0] }}</th><th>{{ scenario.sourceOptions[1] || '来源二' }}</th><th>今日新增</th>
              <th class="r">高风险</th><th class="o">中风险</th><th class="g">低风险</th>
              <th>待处理报告</th><th>待复核</th><th>待推送</th><th>随访中</th>
              <th class="r">异常处理</th><th>随访完成率</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in rows" :key="row.type">
              <td><div class="type-cell"><span class="type-ico">{{ i + 1 }}</span>{{ row.type }}</div></td>
              <td><b>{{ row.total }}</b></td>
              <td>{{ Math.round(parseInt(String(row.total).replace(',','')) * .63).toLocaleString() }}</td>
              <td>{{ Math.round(parseInt(String(row.total).replace(',','')) * .37).toLocaleString() }}</td>
              <td class="inc">+{{ row.inc }}</td>
              <td class="r">{{ row.high }}</td>
              <td class="o">{{ row.mid }}</td>
              <td class="g">{{ row.low }}</td>
              <td>{{ row.todoReport }}</td>
              <td>{{ row.todoReview }}</td>
              <td>{{ row.todoPush }}</td>
              <td>{{ row.following }}</td>
              <td class="r">{{ row.abnormal }}</td>
              <td>{{ row.doneRate }}<span class="mini-bar"><span class="mini-in" :style="{ width: row.doneRate }"></span></span></td>
              <td><button class="mini-link" @click="goWorkbench()">进入队列</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 分析卡片区 -->
    <div class="chart-row">
      <section class="card chart-card">
        <div class="card-head"><div class="card-title">结节类型占比</div></div>
        <div class="chart-body donut-layout">
          <div class="donut-wrap">
            <svg class="donut-svg" viewBox="0 0 120 120">
              <circle
                v-for="seg in donutSegments"
                :key="seg.name"
                cx="60"
                cy="60"
                r="46"
                fill="none"
                :stroke="seg.color"
                stroke-width="16"
                :stroke-dasharray="`${seg.len} ${donutCircumference}`"
                :stroke-dashoffset="seg.offset"
              />
            </svg>
            <div class="donut-center">
              <b>{{ totalPersons }}</b>
              <span>总{{ scenario.personLabel }}数</span>
            </div>
          </div>
          <div class="legend">
            <div v-for="it in donutLegend" :key="it.name" class="leg">
              <span class="dot" :style="{ background: it.color }"></span>
              <span class="leg-name">{{ it.name }}</span>
              <span class="leg-pct">{{ it.pct }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="card chart-card combined-card">
        <div class="card-head"><div class="card-title">风险与随访状态</div><span class="unit">单位：人</span></div>
        <div class="combined-body">
          <div class="combined-col">
            <div class="col-sub">风险分布</div>
            <div class="bar-row"><span>高风险</span><div class="bar"><span style="width:28%;background:#ef4444"></span></div><b>1,348</b></div>
            <div class="bar-row"><span>中风险</span><div class="bar"><span style="width:54%;background:#f97316"></span></div><b>3,244</b></div>
            <div class="bar-row"><span>低风险</span><div class="bar"><span style="width:86%;background:#65a30d"></span></div><b>7,894</b></div>
          </div>
          <div class="combined-divider"></div>
          <div class="combined-col">
            <div class="col-sub">随访状态</div>
            <div class="bar-row"><span>{{ analyticsCopy.statusBars.report }}</span><div class="bar"><span style="width:18%;background:#5b8ff9"></span></div><b>{{ analyticsCopy.statusBars.reportValue }}</b></div>
            <div class="bar-row"><span>{{ analyticsCopy.statusBars.review }}</span><div class="bar"><span style="width:12%;background:#5ad8a6"></span></div><b>{{ analyticsCopy.statusBars.reviewValue }}</b></div>
            <div class="bar-row"><span>{{ analyticsCopy.statusBars.push }}</span><div class="bar"><span style="width:14%;background:#6dc8ec"></span></div><b>{{ analyticsCopy.statusBars.pushValue }}</b></div>
            <div class="bar-row"><span>{{ analyticsCopy.statusBars.following }}</span><div class="bar"><span style="width:86%;background:#4f83f1"></span></div><b>{{ analyticsCopy.statusBars.followingValue }}</b></div>
            <div class="bar-row"><span>{{ analyticsCopy.statusBars.done }}</span><div class="bar"><span style="width:92%;background:#65a30d"></span></div><b>{{ analyticsCopy.statusBars.doneValue }}</b></div>
          </div>
        </div>
        <div class="insight-bar">
          <span class="insight-dot r"></span>{{ analyticsCopy.insights[0].label }} <b>{{ analyticsCopy.insights[0].value }}</b>
          <span class="insight-sep">·</span>{{ analyticsCopy.insights[1].label }} <b>{{ analyticsCopy.insights[1].value }}</b>
          <span class="insight-sep">·</span>{{ analyticsCopy.insights[2].label }} <b>{{ analyticsCopy.insights[2].value }}</b>
        </div>
      </section>

      <section class="card chart-card">
        <div class="card-head"><div class="card-title">今日待办</div><button class="ghost" @click="loadAnalytics">刷新</button></div>
        <div class="chart-body pad">
          <div v-for="todo in todoStats" :key="todo.label" class="todo">
            <b>{{ todo.label }}</b><span class="pill" :class="todo.tone">{{ todo.value }}</span><span class="todo-sub">{{ todo.sub }}</span>
          </div>
          <div class="split"></div>
          <div class="remind"><span>高风险待处理 {{ todoStats[3]?.value || 0 }} 人</span><span class="todo-sub">实时</span></div>
          <div class="remind"><span>{{ loading ? '正在刷新运营数据' : `报告队列 ${todoStats[0]?.value || 0} 份待处理` }}</span><span class="todo-sub">接口</span></div>
        </div>
      </section>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { kpis } from '../mocks/workbenchMock'
import { getStoredScenario } from '../config/scenarios'

const router = useRouter()
const scenario = computed(() => getStoredScenario())
const liveReports = ref([])
const loading = ref(false)

const analyticsCopy = computed(() => {
  if (scenario.value.key === 'pharmacy') {
    return {
      fallbackMetrics: [
        { label: '建档患者数', value: '1,286', delta: '较昨日 +36', tone: 'blue', icon: 'users' },
        { label: '到店咨询', value: '214', delta: '今日新增 +18', tone: 'orange', icon: 'shield' },
        { label: '待生成报告', value: '42', delta: '健康评估待处理', tone: 'blue', icon: 'file' },
        { label: '药师待跟进', value: '28', delta: '高优先级 6', tone: 'green', icon: 'check' },
        { label: '随访待下发', value: '61', delta: '报告后任务', tone: 'purple', icon: 'send' },
        { label: '服务完成率', value: '81.2%', delta: '近30天', tone: 'cyan', icon: 'clock' }
      ],
      liveLabels: {
        total: '建档患者数',
        high: '重点跟进患者',
        pending: '待生成报告',
        review: '药师待跟进',
        push: '随访待下发',
        done: '服务完成率'
      },
      statusBars: {
        report: '待生成报告',
        reportValue: '42',
        review: '药师待跟进',
        reviewValue: '28',
        push: '随访待下发',
        pushValue: '61',
        following: '服务随访中',
        followingValue: '736',
        done: '服务已完成',
        doneValue: '924'
      },
      insights: [
        { label: '重点患者待跟进', value: '28人' },
        { label: '今日到店咨询未建档', value: '12人' },
        { label: '用药提醒待下发', value: '61人' }
      ],
      fallbackTodos: [
        { label: '待生成报告', value: 42, tone: 'r', sub: '健康评估待处理' },
        { label: '药师待跟进', value: 28, tone: 'o', sub: '回访和记录待办' },
        { label: '随访待下发', value: 61, tone: 'b', sub: '报告后任务' },
        { label: '重点患者', value: 18, tone: 'r', sub: '长期未响应或高风险' }
      ]
    }
  }
  return {
    fallbackMetrics: kpis.analytics,
    liveLabels: {
      total: `${scenario.value.personLabel}总数`,
      high: `高风险${scenario.value.personLabel}`,
      pending: '待处理报告',
      review: '待医生复核',
      push: '待推送患者',
      done: '随访完成率'
    },
    statusBars: {
      report: '待处理报告',
      reportValue: '146',
      review: '待医生复核',
      reviewValue: '82',
      push: '待推送患者',
      pushValue: '95',
      following: '随访中',
      followingValue: '7,361',
      done: '随访已完成',
      doneValue: '9,248'
    },
    insights: [
      { label: '高风险待处理', value: '102人' },
      { label: '24小时内未处理', value: '18份' },
      { label: '今日需优先复核', value: '82人' }
    ],
    fallbackTodos: [
      { label: '待处理报告', value: 146, tone: 'r', sub: '影像报告待处理' },
      { label: '待复核', value: 82, tone: 'o', sub: '医生确认待办' },
      { label: '待推送', value: 95, tone: 'b', sub: '报告待推送' },
      { label: '异常预警', value: 102, tone: 'r', sub: '异常结果待处理' }
    ]
  }
})

const metrics = computed(() => {
  if (!liveReports.value.length) return analyticsCopy.value.fallbackMetrics
  const reports = liveReports.value
  const total = reports.length
  const high = reports.filter((item) => riskLabel(item.risk_level) === '高风险').length
  const pending = reports.filter((item) => item.status === 'not_generated').length
  const review = reports.filter((item) => ['generated', 'draft', 'reviewing'].includes(item.status)).length
  const push = reports.filter((item) => ['finalized', 'published'].includes(item.status)).length
  const labels = analyticsCopy.value.liveLabels
  return [
    { label: labels.total, value: formatNum(total), delta: '接口实时汇总', tone: 'blue', icon: 'users' },
    { label: labels.high, value: formatNum(high), delta: `占比 ${pct(high, total)}`, tone: 'orange', icon: 'shield' },
    { label: labels.pending, value: formatNum(pending), delta: '尚未生成', tone: 'blue', icon: 'file' },
    { label: labels.review, value: formatNum(review), delta: '报告待确认', tone: 'green', icon: 'check' },
    { label: labels.push, value: formatNum(push), delta: '已生成报告', tone: 'purple', icon: 'send' },
    { label: labels.done, value: '78.6%', delta: '保留历史口径', tone: 'cyan', icon: 'clock' }
  ]
})

function iconPath(key) {
  if (key === 'users') return 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8 M23 21v-2a4 4 0 0 0-3-3.87'
  if (key === 'shield') return 'M12 2l7 4v6c0 5-3 9-7 10-4-1-7-5-7-10V6l7-4'
  if (key === 'file') return 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6'
  if (key === 'check') return 'M20 6L9 17l-5-5'
  if (key === 'send') return 'M22 2L11 13 M22 2l-7 20-4-9-9-4 20-7z'
  if (key === 'clock') return 'M12 8v5l3 2 M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20'
  return ''
}

function sparkPath(delta) {
  const down = /-\s*\d/.test(String(delta ?? '')) || /↓/.test(String(delta ?? ''))
  return down
    ? 'M2 12 C10 10 14 12 18 11 C26 10 30 16 34 15 C40 14 44 20 48 19 C55 18 58 22 68 23'
    : 'M2 20 C10 18 12 16 18 17 C25 18 28 10 34 12 C40 14 42 6 48 7 C55 8 57 17 68 12'
}

const donutLegend = [
  { name: '三合并结节', pct: '28%', color: '#5ad8a6' },
  { name: '肺部合并乳腺结节', pct: '18%', color: '#5b8ff9' },
  { name: '肺部合并甲状腺结节', pct: '16%', color: '#6dc8ec' },
  { name: '甲状腺合并乳腺结节', pct: '14%', color: '#c4b5fd' },
  { name: '肺部结节', pct: '9%', color: '#f6bd16' },
  { name: '甲状腺结节', pct: '8%', color: '#fda4af' },
  { name: '乳腺结节', pct: '7%', color: '#cbd5e1' }
]

const mockRows = [
  { type: '三合并结节', total: '3,496', inc: 36, high: 468, mid: '1,120', low: '1,908', todoReport: 62, todoReview: 38, todoPush: 44, following: '2,482', abnormal: 41, doneRate: '80.4%' },
  { type: '肺部合并乳腺结节', total: '2,247', inc: 21, high: 286, mid: 708, low: '1,253', todoReport: 34, todoReview: 22, todoPush: 26, following: '1,612', abnormal: 25, doneRate: '78.2%' },
  { type: '肺部合并甲状腺结节', total: '1,998', inc: 19, high: 254, mid: 642, low: '1,102', todoReport: 28, todoReview: 18, todoPush: 22, following: '1,426', abnormal: 21, doneRate: '77.6%' },
  { type: '甲状腺合并乳腺结节', total: '1,748', inc: 17, high: 218, mid: 566, low: 964, todoReport: 24, todoReview: 16, todoPush: 18, following: '1,238', abnormal: 18, doneRate: '76.9%' },
  { type: '肺部结节', total: '1,124', inc: 12, high: 156, mid: 348, low: 620, todoReport: 18, todoReview: 11, todoPush: 12, following: 786, abnormal: 14, doneRate: '75.8%' },
  { type: '甲状腺结节', total: 999, inc: 10, high: 128, mid: 312, low: 559, todoReport: 14, todoReview: 9, todoPush: 10, following: 694, abnormal: 11, doneRate: '74.6%' },
  { type: '乳腺结节', total: 874, inc: 9, high: 112, mid: 268, low: 494, todoReport: 12, todoReview: 8, todoPush: 9, following: 606, abnormal: 9, doneRate: '73.9%' }
]

const rows = computed(() => {
  if (!liveReports.value.length) return mockRows
  const buckets = new Map()
  for (const item of liveReports.value) {
    const type = noduleLabel(item.nodule_type)
    const row = buckets.get(type) || {
      type,
      total: 0,
      inc: 0,
      high: 0,
      mid: 0,
      low: 0,
      todoReport: 0,
      todoReview: 0,
      todoPush: 0,
      following: 0,
      abnormal: 0,
      doneRate: '78.6%'
    }
    row.total += 1
    const risk = riskLabel(item.risk_level)
    if (risk === '高风险') row.high += 1
    else if (risk === '中风险') row.mid += 1
    else row.low += 1
    if (item.status === 'not_generated') row.todoReport += 1
    if (['generated', 'draft', 'reviewing'].includes(item.status)) row.todoReview += 1
    if (['finalized', 'published'].includes(item.status)) row.todoPush += 1
    if (['finalized', 'published', 'archived'].includes(item.status)) row.following += 1
    if (risk === '高风险' && item.status !== 'published') row.abnormal += 1
    buckets.set(type, row)
  }
  return Array.from(buckets.values()).map((row) => ({
    ...row,
    total: formatNum(row.total),
    high: formatNum(row.high),
    mid: formatNum(row.mid),
    low: formatNum(row.low),
    following: formatNum(row.following)
  }))
})

const totalPersons = computed(() => liveReports.value.length ? formatNum(liveReports.value.length) : '12,486')

const todoStats = computed(() => {
  const reports = liveReports.value
  if (!reports.length) {
    return analyticsCopy.value.fallbackTodos
  }
  const isPharmacy = scenario.value.key === 'pharmacy'
  return [
    { label: isPharmacy ? '待生成报告' : '待处理报告', value: reports.filter((item) => item.status === 'not_generated').length, tone: 'r', sub: '尚未生成报告' },
    { label: isPharmacy ? '药师待跟进' : '待复核', value: reports.filter((item) => ['generated', 'draft', 'reviewing'].includes(item.status)).length, tone: 'o', sub: isPharmacy ? '回访和记录待办' : '医生确认待办' },
    { label: isPharmacy ? '随访待下发' : '待推送', value: reports.filter((item) => ['finalized', 'published'].includes(item.status)).length, tone: 'b', sub: isPharmacy ? '报告后任务' : '报告待推送' },
    { label: isPharmacy ? '重点患者' : '异常预警', value: reports.filter((item) => riskLabel(item.risk_level) === '高风险').length, tone: 'r', sub: isPharmacy ? '重点跟进' : '高风险结果待处理' }
  ]
})

const donutCircumference = 2 * Math.PI * 46

function parsePct(p) {
  const n = Number(String(p).replace('%', '').trim())
  return Number.isFinite(n) ? n : 0
}

const donutSegments = computed(() => {
  let acc = 0
  return donutLegend.map((it) => {
    const pct = parsePct(it.pct)
    const len = (pct / 100) * donutCircumference
    const seg = {
      name: it.name,
      color: it.color,
      len: len.toFixed(1),
      offset: (-acc).toFixed(1)
    }
    acc += len
    return seg
  })
})

function goWorkbench() { router.push('/patient?tab=queue') }

onMounted(loadAnalytics)

async function loadAnalytics() {
  loading.value = true
  try {
    const res = await fetch('/api/b/reports?page=1&per_page=500&include_unreported=1', { credentials: 'include' })
    const payload = await res.json()
    if (!res.ok || payload.success === false) throw new Error(payload.message || '加载失败')
    liveReports.value = payload.data?.reports || payload.reports || []
  } catch (e) {
    liveReports.value = []
  } finally {
    loading.value = false
  }
}

function formatNum(value) {
  return Number(value || 0).toLocaleString()
}

function pct(value, total) {
  if (!total) return '0%'
  return `${Math.round((value / total) * 100)}%`
}

function riskLabel(risk) {
  const map = { high: '高风险', mid: '中风险', medium: '中风险', low: '低风险', '高危': '高风险', '中危': '中风险', '低危': '低风险' }
  return map[risk] || risk || '待评估'
}

function noduleLabel(type) {
  const map = {
    breast: '乳腺结节',
    lung: '肺部结节',
    thyroid: '甲状腺结节',
    breast_lung: '肺部合并乳腺结节',
    breast_thyroid: '甲状腺合并乳腺结节',
    lung_thyroid: '肺部合并甲状腺结节',
    triple: '三合并结节'
  }
  return map[type] || type || '其他结节'
}
</script>

<style scoped>
.page{display:flex;flex-direction:column;gap:12px;padding-bottom:24px}

/* KPI */
.kpi-row{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}
.kpi{position:relative;background:#fff;border:1px solid #e6edf7;border-radius:10px;padding:10px 12px;box-shadow:0 4px 12px rgba(15,23,42,.04);overflow:hidden}
.kpi-ico{width:28px;height:28px;border-radius:8px;border:1px solid #e6edf7;background:#f8fafc;color:#64748b;display:grid;place-items:center;margin-bottom:4px}
.kpi[data-tone="orange"] .kpi-ico{background:#fff7ed;border-color:#fed7aa;color:#f97316}
.kpi[data-tone="green"] .kpi-ico{background:#ecfdf5;border-color:#bbf7d0;color:#16a34a}
.kpi[data-tone="purple"] .kpi-ico{background:#f5f3ff;border-color:#ddd6fe;color:#8b5cf6}
.kpi[data-tone="cyan"] .kpi-ico{background:#eafcff;border-color:#c7f9ff;color:#0ea5b7}
.kpi-label{color:#64748b;font-weight:500;font-size:12px;line-height:1.3}
.kpi-value{font-size:26px;font-weight:700;color:#0f172a;margin-top:3px;line-height:1}
.kpi-delta{font-size:12px;color:#c4cdd6;margin-top:3px;font-weight:400}
.spark{position:absolute;right:8px;bottom:8px;width:44px;height:16px;opacity:.6}
.spark path{fill:none;stroke:#5b8ff9;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.kpi[data-tone="orange"] .spark path{stroke:#f97316}
.kpi[data-tone="green"] .spark path{stroke:#16a34a}
.kpi[data-tone="purple"] .spark path{stroke:#8b5cf6}
.kpi[data-tone="cyan"] .spark path{stroke:#0ea5b7}

/* 通用卡片 */
.card{background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 4px 12px rgba(15,23,42,.04)}
.card-head{display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border-bottom:1px solid #eef2f7;gap:8px;flex-wrap:wrap;min-height:40px}
.card-title{font-weight:600;color:#0f172a;font-size:13px}
.head-left{display:flex;align-items:center;gap:10px;min-width:0}
.head-actions{display:flex;gap:6px}
.muted-sm{color:#94a3b8;font-size:12px}
.unit{color:#94a3b8;font-size:12px}
.ghost{border:0;background:transparent;color:#155eef;font-weight:600;cursor:pointer;font-size:12px}
.btn{border:1px solid #d9e2ef;border-radius:6px;background:#fff;color:#475569;padding:4px 10px;cursor:pointer;font-size:12px}

/* 表格 */
.table-wrap{overflow:auto}
.table{width:100%;border-collapse:collapse;min-width:1100px}
.table th{background:#f8fafc;color:#64748b;text-align:left;font-size:12px;padding:7px 8px;border-bottom:1px solid #e5edf7;white-space:nowrap;font-weight:600}
.table td{padding:7px 8px;border-bottom:1px solid #edf2f7;white-space:nowrap;font-size:13px}
.table tbody tr:last-child td{border-bottom:0}
.type-cell{display:flex;align-items:center;gap:6px;font-weight:600}
.type-ico{width:20px;height:20px;border-radius:5px;background:#eef5ff;color:#155eef;display:flex;align-items:center;justify-content:center;font-size:11px;flex-shrink:0}
.r{color:#dc2626}.o{color:#ea580c}.g{color:#15803d}
.inc{color:#64748b}
.mini-bar{display:inline-block;width:60px;height:5px;background:#e8eef8;border-radius:999px;overflow:hidden;margin-left:5px;vertical-align:middle}
.mini-in{display:block;height:100%;background:#4f83f1;border-radius:999px}
.mini-link{border:1px solid #e6edf7;background:#f8fafc;color:#155eef;border-radius:6px;padding:3px 8px;font-weight:600;font-size:12px;cursor:pointer}

/* 图表区 */
.chart-row{display:grid;grid-template-columns:1fr 2fr 1fr;gap:10px}
.chart-card{max-height:260px}
.chart-body{padding:8px}
.chart-body.pad{padding:10px 12px}

/* 合并卡片 */
.combined-card{display:flex;flex-direction:column}
.combined-body{display:flex;flex:1;padding:10px 12px;gap:0;min-height:0}
.combined-col{flex:1;display:flex;flex-direction:column;gap:0;min-width:0}
.combined-divider{width:1px;background:#eef2f7;margin:0 14px;flex-shrink:0}
.col-sub{font-size:11px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px}
.insight-bar{border-top:1px solid #eef2f7;padding:7px 12px;font-size:12px;color:#64748b;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.insight-bar b{color:#0f172a;font-weight:700}
.insight-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;display:inline-block}
.insight-dot.r{background:#ef4444}
.insight-sep{color:#cbd5e1;margin:0 2px}

/* 环形图卡片 */
.donut-layout{display:flex;align-items:center;gap:12px;padding:10px 12px}
.donut-wrap{position:relative;flex-shrink:0;width:130px;height:130px;display:flex;align-items:center;justify-content:center}
.donut-svg{width:130px;height:130px;transform:rotate(-90deg)}
.donut-center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;pointer-events:none}
.donut-center b{font-size:18px;font-weight:700;color:#0f172a;line-height:1}
.donut-center span{font-size:11px;color:#94a3b8;margin-top:3px}
.legend{flex:1;display:grid;gap:0;min-width:0}
.leg{display:grid;grid-template-columns:8px 1fr 36px;gap:6px;align-items:center;height:24px}
.dot{width:7px;height:7px;border-radius:2px;flex-shrink:0}
.leg-name{font-size:12px;color:#475569;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.leg-pct{font-size:12px;color:#0f172a;font-weight:600;text-align:right}

.bar-row{display:grid;grid-template-columns:72px 1fr 40px;gap:6px;align-items:center;margin:7px 0;color:#64748b;font-size:12px}
.bar{height:6px;background:#edf2f7;border-radius:999px;overflow:hidden}
.bar span{display:block;height:100%;border-radius:999px}
.pill{display:inline-flex;align-items:center;border-radius:999px;padding:2px 8px;font-size:11px;font-weight:700}
.pill.r{background:#fff1f2;color:#dc2626}
.pill.o{background:#fff7ed;color:#c2410c}
.pill.b{background:#eef5ff;color:#155eef}
.todo{display:grid;grid-template-columns:72px 36px 1fr;gap:6px;align-items:center;background:#f8fafc;border-radius:8px;padding:6px 8px;margin-bottom:6px;font-size:12px}
.todo-sub{color:#94a3b8;font-size:11px}
.split{height:1px;background:#eef2f7;margin:8px 0}
.remind{display:flex;justify-content:space-between;gap:8px;padding:6px 0;border-top:1px solid #eef2f7;font-size:11px;color:#475569}
</style>
