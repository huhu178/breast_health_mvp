<template>
  <div class="page">

    <!-- 七类结节总览表（核心区，优先展示） -->
    <section class="card">
      <div class="card-head">
        <div class="head-left">
          <div class="card-title">七类结节运营总览</div>
          <span class="muted-sm">点击"进入队列"进入工作台</span>
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
              <th>结节类型</th><th>患者数</th><th>门诊</th><th>体检</th><th>今日新增</th>
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
              <circle cx="60" cy="60" r="46" fill="none" stroke="#f6bd16" stroke-width="16"
                stroke-dasharray="163.4 282.7" stroke-dashoffset="0" />
              <circle cx="60" cy="60" r="46" fill="none" stroke="#5b8ff9" stroke-width="16"
                stroke-dasharray="156.9 282.7" stroke-dashoffset="-163.4" />
              <circle cx="60" cy="60" r="46" fill="none" stroke="#5ad8a6" stroke-width="16"
                stroke-dasharray="200.7 282.7" stroke-dashoffset="-320.3" />
              <circle cx="60" cy="60" r="46" fill="none" stroke="#6dc8ec" stroke-width="16"
                stroke-dasharray="40.6 282.7" stroke-dashoffset="-521.0" />
              <circle cx="60" cy="60" r="46" fill="none" stroke="#c4b5fd" stroke-width="16"
                stroke-dasharray="35.0 282.7" stroke-dashoffset="-561.6" />
              <circle cx="60" cy="60" r="46" fill="none" stroke="#fda4af" stroke-width="16"
                stroke-dasharray="23.2 282.7" stroke-dashoffset="-596.6" />
              <circle cx="60" cy="60" r="46" fill="none" stroke="#cbd5e1" stroke-width="16"
                stroke-dasharray="6.3 282.7" stroke-dashoffset="-619.8" />
            </svg>
            <div class="donut-center">
              <b>12,486</b>
              <span>总患者数</span>
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
            <div class="bar-row"><span>待处理报告</span><div class="bar"><span style="width:18%;background:#5b8ff9"></span></div><b>146</b></div>
            <div class="bar-row"><span>待医生复核</span><div class="bar"><span style="width:12%;background:#5ad8a6"></span></div><b>82</b></div>
            <div class="bar-row"><span>待推送患者</span><div class="bar"><span style="width:14%;background:#6dc8ec"></span></div><b>95</b></div>
            <div class="bar-row"><span>随访中</span><div class="bar"><span style="width:86%;background:#4f83f1"></span></div><b>7,361</b></div>
            <div class="bar-row"><span>随访已完成</span><div class="bar"><span style="width:92%;background:#65a30d"></span></div><b>9,248</b></div>
          </div>
        </div>
        <div class="insight-bar">
          <span class="insight-dot r"></span>高风险待处理 <b>102</b> 人
          <span class="insight-sep">·</span>24小时内未处理 <b>18</b> 份
          <span class="insight-sep">·</span>今日需优先复核 <b>82</b> 人
        </div>
      </section>

      <section class="card chart-card">
        <div class="card-head"><div class="card-title">今日待办</div><button class="ghost">刷新</button></div>
        <div class="chart-body pad">
          <div class="todo"><b>待处理报告</b><span class="pill r">146</span><span class="todo-sub">影像报告待处理</span></div>
          <div class="todo"><b>待复核</b><span class="pill o">82</span><span class="todo-sub">医生确认待办</span></div>
          <div class="todo"><b>待推送</b><span class="pill b">95</span><span class="todo-sub">报告待推送</span></div>
          <div class="todo"><b>异常预警</b><span class="pill r">102</span><span class="todo-sub">异常结果待处理</span></div>
          <div class="split"></div>
          <div class="remind"><span>高风险患者张*国已逾期 7 天</span><span class="todo-sub">08:45</span></div>
          <div class="remind"><span>有 18 份报告超 24 小时未处理</span><span class="todo-sub">08:30</span></div>
        </div>
      </section>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { kpis } from '../mocks/workbenchMock'

const router = useRouter()
const metrics = computed(() => kpis.analytics)

function sparkPath(delta) {
  const down = /-\s*\d/.test(String(delta ?? '')) || /↓/.test(String(delta ?? ''))
  return down
    ? 'M2 12 C10 10 14 12 18 11 C26 10 30 16 34 15 C40 14 44 20 48 19 C55 18 58 22 68 23'
    : 'M2 20 C10 18 12 16 18 17 C25 18 28 10 34 12 C40 14 42 6 48 7 C55 8 57 17 68 12'
}

const donutLegend = [
  { name: '乳腺结节', pct: '26.1%', color: '#f6bd16' },
  { name: '甲状腺结节', pct: '25.1%', color: '#5b8ff9' },
  { name: '肺部结节', pct: '32.1%', color: '#5ad8a6' },
  { name: '肺部合并乳腺结节', pct: '6.5%', color: '#6dc8ec' },
  { name: '肺部合并甲状腺结节', pct: '5.6%', color: '#c4b5fd' },
  { name: '甲状腺合并乳腺结节', pct: '3.7%', color: '#fda4af' },
  { name: '三合并结节', pct: '1.0%', color: '#cbd5e1' }
]

const rows = [
  { type: '乳腺结节', total: '3,256', inc: 32, high: 356, mid: 812, low: '2,088', todoReport: 38, todoReview: 22, todoPush: 19, following: '2,456', abnormal: 26, doneRate: '81.2%' },
  { type: '甲状腺结节', total: '3,128', inc: 28, high: 312, mid: 790, low: '2,026', todoReport: 29, todoReview: 18, todoPush: 15, following: '2,389', abnormal: 21, doneRate: '79.4%' },
  { type: '肺部结节', total: '4,012', inc: 41, high: 428, mid: '1,102', low: '2,482', todoReport: 42, todoReview: 24, todoPush: 28, following: '2,976', abnormal: 34, doneRate: '77.8%' },
  { type: '肺部合并乳腺结节', total: 812, inc: 9, high: 96, mid: 208, low: 508, todoReport: 10, todoReview: 6, todoPush: 8, following: 604, abnormal: 8, doneRate: '74.4%' },
  { type: '肺部合并甲状腺结节', total: 702, inc: 7, high: 84, mid: 176, low: 442, todoReport: 8, todoReview: 4, todoPush: 6, following: 518, abnormal: 6, doneRate: '76.1%' },
  { type: '甲状腺合并乳腺结节', total: 456, inc: 5, high: 52, mid: 120, low: 284, todoReport: 6, todoReview: 3, todoPush: 4, following: 332, abnormal: 5, doneRate: '77.2%' },
  { type: '三合并结节', total: 120, inc: 2, high: 20, mid: 36, low: 64, todoReport: 3, todoReview: 2, todoPush: 2, following: 86, abnormal: 2, doneRate: '72.0%' }
]

function goWorkbench() { router.push('/patient?tab=queue') }
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
