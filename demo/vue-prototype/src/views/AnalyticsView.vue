<template>
  <div class="page">
    <section class="kpi-row" aria-label="关键指标">
      <article v-for="m in metrics" :key="m.label" class="kpi" :data-tone="m.tone">
        <div class="kpi-ico" aria-hidden="true">
          <svg v-if="m.icon === 'users'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <path d="M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          <svg v-else-if="m.icon === 'shield'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="M9 12l2 2 4-4" />
          </svg>
          <svg v-else-if="m.icon === 'file'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <path d="M14 2v6h6" />
            <path d="M8 13h8M8 17h6" />
          </svg>
          <svg v-else-if="m.icon === 'check'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 11l3 3L22 4" />
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
          <svg v-else-if="m.icon === 'send'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 2L11 13" />
            <path d="M22 2l-7 20-4-9-9-4z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 20a8 8 0 1 0-8-8 8 8 0 0 0 8 8z" />
            <path d="M12 6v6l4 2" />
          </svg>
        </div>
        <div class="kpi-label">{{ m.label }}</div>
        <div class="kpi-value">{{ m.value }}</div>
        <div class="kpi-delta">{{ m.delta }}</div>
        <svg class="spark" viewBox="0 0 70 26" aria-hidden="true">
          <path :d="sparkPathByDelta(m.delta)" />
        </svg>
      </article>
    </section>

    <div class="grid">
      <section class="card span3">
        <header class="card-head">
          <div class="head-left">
            <div class="card-title">七类结节运营总览</div>
            <div class="muted head-tip">点击“进入队列”进入工作台首屏</div>
          </div>
        </header>
        <div class="card-body">
          <table class="table">
            <thead>
              <tr>
                <th>结节类型</th>
                <th>患者数</th>
                <th>今日新增</th>
                <th class="r">高风险</th>
                <th class="o">中风险</th>
                <th class="g">低风险</th>
                <th>待处理报告</th>
                <th>待复核</th>
                <th>待推送</th>
                <th>随访中</th>
                <th class="r">异常处理</th>
                <th>随访完成率</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.type">
                <td class="type">
                  <span class="type-ico" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7z" />
                      <path d="M12 9a2.2 2.2 0 1 0 0 .01" />
                    </svg>
                  </span>
                  {{ row.type }}
                </td>
                <td><b>{{ row.total }}</b></td>
                <td class="inc">+{{ row.inc }}</td>
                <td class="r">{{ row.high }}</td>
                <td class="o">{{ row.mid }}</td>
                <td class="g">{{ row.low }}</td>
                <td>{{ row.todoReport }}</td>
                <td>{{ row.todoReview }}</td>
                <td>{{ row.todoPush }}</td>
                <td>{{ row.following }}</td>
                <td class="r">{{ row.abnormal }}</td>
                <td class="rate">
                  {{ row.doneRate }}
                  <span class="mini-bar"><span class="mini-in" :style="{ width: row.doneRate }"></span></span>
                </td>
                <td><button class="mini-link" type="button" @click="goWorkbench()">进入队列</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div class="panel-grid">
        <section class="card panel donut-panel">
          <header class="card-head">
            <div class="card-title">结节类型占比</div>
          </header>
          <div class="card-body">
            <div class="donut-wrap">
              <div class="donut" aria-hidden="true"></div>
              <div class="donut-center"><b>12,486</b><span class="muted">总患者数</span></div>
            </div>
            <div class="legend">
              <div v-for="it in donutLegend" :key="it.name" class="leg">
                <span class="dot" :style="{ background: it.color }"></span>
                <span class="muted">{{ it.name }}</span>
                <b>{{ it.pct }}</b>
              </div>
            </div>
          </div>
        </section>

        <section class="card panel risk-panel">
          <header class="card-head">
            <div class="card-title">风险分布</div>
            <div class="muted">单位：人</div>
          </header>
          <div class="card-body">
            <div class="bar-row"><span>高风险</span><div class="bar2"><span style="width:28%;background:#ef4444"></span></div><b>1,348</b></div>
            <div class="bar-row"><span>中风险</span><div class="bar2"><span style="width:54%;background:#f97316"></span></div><b>3,244</b></div>
            <div class="bar-row"><span>低风险</span><div class="bar2"><span style="width:86%;background:#65a30d"></span></div><b>7,894</b></div>
            <div class="pill r">高风险占比 10.8%</div>
          </div>
        </section>

        <section class="card panel follow-panel">
          <header class="card-head">
            <div class="card-title">随访状态分布</div>
            <div class="muted">单位：人</div>
          </header>
          <div class="card-body">
            <div class="bar3"><span class="muted">待处理报告</span><div class="b3"><span style="width:18%;background:#5b8ff9"></span></div><b>146</b></div>
            <div class="bar3"><span class="muted">待医生复核</span><div class="b3"><span style="width:12%;background:#5ad8a6"></span></div><b>82</b></div>
            <div class="bar3"><span class="muted">待推送患者</span><div class="b3"><span style="width:14%;background:#6dc8ec"></span></div><b>95</b></div>
            <div class="bar3"><span class="muted">随访中</span><div class="b3"><span style="width:86%;background:#4f83f1"></span></div><b>7,361</b></div>
            <div class="bar3"><span class="muted">异常预警处理</span><div class="b3"><span style="width:20%;background:#f97316"></span></div><b>102</b></div>
            <div class="bar3"><span class="muted">随访已完成</span><div class="b3"><span style="width:92%;background:#65a30d"></span></div><b>9,248</b></div>
          </div>
        </section>

        <section class="card panel todo-panel">
          <header class="card-head">
            <div class="card-title">今日待办</div>
            <button class="ghost" type="button">刷新</button>
          </header>
          <div class="card-body">
            <div class="todo"><b>待处理报告</b><span class="pill r">146</span><span class="muted">影像报告待处理</span></div>
            <div class="todo"><b>待复核</b><span class="pill o">82</span><span class="muted">医生确认待办</span></div>
            <div class="todo"><b>待推送</b><span class="pill b">95</span><span class="muted">报告待推送</span></div>
            <div class="todo"><b>异常预警</b><span class="pill r">102</span><span class="muted">异常结果待处理</span></div>
            <div class="split"></div>
            <div class="subhead">重要提醒</div>
            <div class="remind"><span>高风险患者张*国已逾期 7 天，请尽快处理</span><span class="muted">08:45</span></div>
            <div class="remind"><span>有 18 份报告超 24 小时未处理</span><span class="muted">08:30</span></div>
          </div>
        </section>

        <section class="mini-cards">
          <div v-for="x in miniCards" :key="x.label" class="mini-card">
            <div class="mini-top"><span class="muted">{{ x.label }}</span><span class="muted">今日</span></div>
            <div class="mini-val">{{ x.value }}</div>
            <div class="mini-sub"><span class="muted">较昨日</span><span :class="x.deltaClass">{{ x.delta }}</span></div>
            <svg class="mini-spark" :class="x.sparkToneClass" viewBox="0 0 120 34" aria-hidden="true">
              <path :d="miniSparkPathByDelta(x.delta)" />
            </svg>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { kpis } from '../mocks/workbenchMock'

const router = useRouter()
const metrics = computed(() => kpis.analytics)

function isDeltaDown(delta) {
  const s = String(delta ?? '')
  return /-\s*\d/.test(s) || /↓/.test(s)
}

function sparkPathByDelta(delta) {
  // 上升/下降两套路径（装饰用），确保与数字方向一致
  return isDeltaDown(delta)
    ? 'M2 12 C10 10 14 12 18 11 C26 10 30 16 34 15 C40 14 44 20 48 19 C55 18 58 22 68 23'
    : 'M2 20 C10 18 12 16 18 17 C25 18 28 10 34 12 C40 14 42 6 48 7 C55 8 57 17 68 12'
}

function miniSparkPathByDelta(delta) {
  return isDeltaDown(delta)
    ? 'M2 10 C18 12 24 8 36 12 C50 16 62 12 74 18 C88 24 98 20 118 26'
    : 'M2 26 C18 22 24 28 36 24 C50 18 62 24 74 16 C88 8 98 12 118 6'
}

const miniCards = computed(() => ([
  { label: '报告生成率', value: '92.4%', delta: '+2.1%', deltaClass: 'up', sparkToneClass: '' },
  { label: '医生复核率', value: '88.7%', delta: '-1.3%', deltaClass: 'down', sparkToneClass: 'tone2' },
  { label: '患者触达率', value: '93.6%', delta: '+1.7%', deltaClass: 'up', sparkToneClass: 'tone3' }
]))

const rows = [
  { type: '乳腺结节', total: '3,256', inc: 32, high: 356, mid: 812, low: '2,088', todoReport: 38, todoReview: 22, todoPush: 19, following: '2,456', abnormal: 26, doneRate: '81.2%' },
  { type: '甲状腺结节', total: '3,128', inc: 28, high: 312, mid: 790, low: '2,026', todoReport: 29, todoReview: 18, todoPush: 15, following: '2,389', abnormal: 21, doneRate: '79.4%' },
  { type: '肺部结节', total: '4,012', inc: 41, high: 428, mid: '1,102', low: '2,482', todoReport: 42, todoReview: 24, todoPush: 28, following: '2,976', abnormal: 34, doneRate: '77.8%' },
  { type: '肺部合并乳腺结节', total: 812, inc: 9, high: 96, mid: 208, low: 508, todoReport: 10, todoReview: 6, todoPush: 8, following: 604, abnormal: 8, doneRate: '74.4%' },
  { type: '肺部合并甲状腺结节', total: 702, inc: 7, high: 84, mid: 176, low: 442, todoReport: 8, todoReview: 4, todoPush: 6, following: 518, abnormal: 6, doneRate: '76.1%' },
  { type: '甲状腺合并乳腺结节', total: 456, inc: 5, high: 52, mid: 120, low: 284, todoReport: 6, todoReview: 3, todoPush: 4, following: 332, abnormal: 5, doneRate: '77.2%' },
  { type: '三合并结节', total: 120, inc: 2, high: 20, mid: 36, low: 64, todoReport: 3, todoReview: 2, todoPush: 2, following: 86, abnormal: 2, doneRate: '72.0%' }
]

const donutLegend = [
  { name: '乳腺结节', pct: '26.1%', color: '#f6bd16' },
  { name: '甲状腺结节', pct: '25.1%', color: '#5b8ff9' },
  { name: '肺部结节', pct: '32.1%', color: '#5ad8a6' },
  { name: '肺部合并乳腺结节', pct: '6.5%', color: '#6dc8ec' },
  { name: '肺部合并甲状腺结节', pct: '5.6%', color: '#d3adf7' },
  { name: '甲状腺合并乳腺结节', pct: '3.7%', color: '#fb7185' },
  { name: '三合并结节', pct: '1.0%', color: '#94a3b8' }
]

function goWorkbench() {
  router.push('/workbench')
}
</script>

<style scoped>
.page{height:100%;overflow:auto;display:grid;gap:12px;align-content:start}
.kpi-row{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}
.kpi{position:relative;background:#fff;border:1px solid #e6edf7;border-radius:12px;padding:14px 14px;box-shadow:0 6px 18px rgba(15,23,42,.04);overflow:hidden}
.kpi-ico{width:34px;height:34px;border-radius:12px;border:1px solid #e6edf7;background:#f8fafc;color:#64748b;display:grid;place-items:center;margin-bottom:6px}
.kpi[data-tone="orange"] .kpi-ico{background:#fff7ed;border-color:#fed7aa;color:#f97316}
.kpi[data-tone="green"] .kpi-ico{background:#ecfdf5;border-color:#bbf7d0;color:#16a34a}
.kpi[data-tone="purple"] .kpi-ico{background:#f5f3ff;border-color:#ddd6fe;color:#8b5cf6}
.kpi[data-tone="cyan"] .kpi-ico{background:#eafcff;border-color:#c7f9ff;color:#0ea5b7}
.kpi-label{color:#526175;font-weight:850;font-size:12px}
.kpi-value{font-size:22px;font-weight:950;color:#0f172a;margin-top:8px}
.kpi-delta{font-size:12px;color:#94a3b8;margin-top:8px;font-weight:800}
.spark{position:absolute;right:12px;bottom:12px;width:66px;height:24px}
.spark path{fill:none;stroke:#5b8ff9;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.kpi[data-tone="orange"] .spark path{stroke:#f97316}
.kpi[data-tone="green"] .spark path{stroke:#16a34a}
.kpi[data-tone="purple"] .spark path{stroke:#8b5cf6}
.kpi[data-tone="cyan"] .spark path{stroke:#0ea5b7}

.grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:12px;align-items:start}
.card{background:#fff;border:1px solid #e6edf7;border-radius:12px;box-shadow:0 6px 18px rgba(15,23,42,.04);overflow:hidden}
.card-head{height:46px;display:flex;align-items:center;justify-content:space-between;padding:0 14px;border-bottom:1px solid #eef2f7}
.card-title{font-weight:950;color:#0f172a}
.muted{color:#64748b;font-weight:750}
.card-body{padding:12px 14px}
.span2{grid-column:1 / span 1}
.span3{grid-column:1 / -1}
.head-left{display:flex;align-items:center;gap:14px;min-width:0}
.head-tip{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.table{width:100%;border-collapse:collapse;min-width:1080px}
.table th{background:#f8fafc;color:#64748b;text-align:left;font-size:12px;padding:10px 8px;border-bottom:1px solid #e5edf7;white-space:nowrap}
.table td{padding:10px 8px;border-bottom:1px solid #edf2f7;white-space:nowrap}
.type{display:flex;align-items:center;gap:8px;font-weight:900}
.type-ico{width:24px;height:24px;border-radius:10px;background:#eef5ff;color:#155eef;display:grid;place-items:center;border:1px solid #cfe0ff}
.r{color:#dc2626}.o{color:#ea580c}.g{color:#15803d}.b{color:#155eef}
.inc{color:#64748b;font-weight:850}
.rate{min-width:170px}
.mini-bar{display:inline-block;width:84px;height:6px;background:#e8eef8;border-radius:999px;overflow:hidden;margin-left:8px;vertical-align:middle}
.mini-in{display:block;height:100%;background:#4f83f1;border-radius:999px}
.mini-link{border:1px solid #e6edf7;background:#f8fafc;color:#155eef;border-radius:10px;padding:6px 10px;font-weight:900}
.ghost{border:0;background:transparent;color:#155eef;font-weight:900}
.subhead{font-weight:950;color:#0f172a;margin:8px 0 4px}

.bar-row{display:grid;grid-template-columns:72px 1fr 44px;gap:8px;align-items:center;margin:10px 0;color:#64748b}
.bar2{height:8px;background:#edf2f7;border-radius:999px;overflow:hidden}
.bar2 span{display:block;height:100%;border-radius:999px}
.pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900}
.pill.r{background:#fff1f2;color:#dc2626}
.pill.o{background:#fff7ed;color:#c2410c}
.pill.b{background:#eef5ff;color:#155eef}
.todo{display:grid;grid-template-columns:92px 44px 1fr;gap:10px;align-items:center;background:#f8fafc;border-radius:12px;padding:10px 12px;margin-bottom:10px}
.split{height:1px;background:#eef2f7;margin:12px 0}
.remind{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-top:1px solid #eef2f7}

.panel-grid{grid-column:1 / -1;display:grid;grid-template-columns:1.1fr 1fr 1.1fr 1.35fr;grid-template-rows:auto auto;gap:12px;align-items:stretch}
.panel{min-height:0}
.donut-panel{grid-column:1;grid-row:1}
.risk-panel{grid-column:2;grid-row:1}
.follow-panel{grid-column:3;grid-row:1}
.todo-panel{grid-column:4;grid-row:1 / span 2}
.mini-cards{grid-column:1 / span 3;grid-row:2;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}

.mini-card{background:#fff;border:1px solid #e6edf7;border-radius:12px;box-shadow:0 6px 18px rgba(15,23,42,.04);padding:12px 14px;position:relative;overflow:hidden;min-height:128px}
.mini-top{display:flex;justify-content:space-between;gap:10px;font-weight:900}
.mini-val{font-size:22px;font-weight:950;color:#0f172a;margin-top:10px}
.mini-sub{display:flex;gap:8px;margin-top:8px;font-weight:850}
.up{color:#16a34a}
.down{color:#dc2626}
.mini-spark{position:absolute;right:12px;bottom:10px;width:120px;height:34px}
.mini-spark path{fill:none;stroke:#5b8ff9;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;opacity:.9}
.mini-spark.tone2 path{stroke:#16a34a}
.mini-spark.tone3 path{stroke:#8b5cf6}

.donut-wrap{position:relative;display:flex;align-items:center;justify-content:center;padding:10px 0 6px}
.donut{width:160px;height:160px;border-radius:50%;background:conic-gradient(#f6bd16 0 26.1%,#5b8ff9 26.1% 51.2%,#5ad8a6 51.2% 83.3%,#6dc8ec 83.3% 89.8%,#d3adf7 89.8% 95.4%,#fb7185 95.4% 99.1%,#94a3b8 99.1%)}
.donut-center{position:absolute;inset:0;display:grid;place-items:center;text-align:center;pointer-events:none}
.donut-center b{display:block;font-size:18px;font-weight:950;color:#0f172a;line-height:1}
.donut-center .muted{display:block;margin-top:6px}
.legend{display:grid;gap:8px;margin-top:8px}
.leg{display:grid;grid-template-columns:14px 1fr 60px;gap:8px;align-items:center}
.leg .dot{width:10px;height:10px;border-radius:3px}

.bar3{display:grid;grid-template-columns:96px 1fr 64px;gap:10px;align-items:center;margin:10px 0}
.b3{height:8px;background:#edf2f7;border-radius:999px;overflow:hidden}
.b3 span{display:block;height:100%;border-radius:999px}

</style>

