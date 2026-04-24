<template>
  <div class="page">
    <div class="page-head">
      <div class="page-title">管理统计</div>
      <div class="crumb">首页 / <b>管理统计</b></div>
    </div>

    <!-- 统计维度切换 -->
    <div class="tabs-bar">
      <button v-for="t in tabs" :key="t" class="tab" :class="{ active: activeTab === t }" @click="activeTab = t">{{ t }}</button>
    </div>

    <!-- KPI -->
    <div class="kpi-row">
      <KpiCard v-for="m in kpis" :key="m.label" v-bind="m" />
    </div>

    <!-- 图表区 -->
    <div class="chart-row">
      <section class="card chart-card">
        <div class="card-head"><div class="card-title">结节类型占比</div></div>
        <div class="chart-body">
          <div class="donut"></div>
          <div class="legend">
            <div v-for="item in donutLegend" :key="item.label" class="legend-item">
              <span class="dot" :style="{ background: item.color }"></span>
              <span>{{ item.label }}</span>
              <span class="muted">{{ item.pct }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="card chart-card">
        <div class="card-head"><div class="card-title">风险分布 <span class="muted" style="float:right">单位：人</span></div></div>
        <div class="chart-body" style="padding:12px 16px">
          <div v-for="bar in riskBars" :key="bar.label" class="bar-row">
            <span class="bar-label">{{ bar.label }}</span>
            <div class="bar"><span :style="{ width: bar.pct, background: bar.color }"></span></div>
            <b>{{ bar.value }}</b>
          </div>
          <div class="tag high" style="margin-top:6px;display:inline-flex">高风险占比 10.8%</div>
        </div>
      </section>

      <section class="card chart-card">
        <div class="card-head"><div class="card-title">随访状态分布 <span class="muted" style="float:right">单位：人</span></div></div>
        <div class="chart-body" style="padding:12px 16px">
          <div v-for="bar in stageBars" :key="bar.label" class="bar-row">
            <span class="bar-label">{{ bar.label }}</span>
            <div class="bar"><span :style="{ width: bar.pct, background: bar.color }"></span></div>
            <b>{{ bar.value }}</b>
          </div>
        </div>
      </section>

      <section class="card chart-card">
        <div class="card-head"><div class="card-title">关键率指标</div></div>
        <div class="chart-body" style="padding:12px 16px">
          <div v-for="m in rateMetrics" :key="m.label" class="rate-row">
            <div class="rate-label">{{ m.label }}</div>
            <div class="rate-value" :style="{ color: m.color }">{{ m.value }}</div>
            <div class="muted" style="font-size:11px">{{ m.delta }}</div>
          </div>
        </div>
      </section>
    </div>

    <!-- 结节类型运营总览 -->
    <section class="card" style="margin-top:12px">
      <div class="card-head">
        <div class="card-title">七类结节运营总览</div>
        <div class="head-actions">
          <button class="btn" @click="toast.show('导出统计')">导出统计</button>
          <button class="btn" @click="toast.show('查看明细')">查看明细</button>
        </div>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>结节类型</th><th>患者数</th><th>门诊</th><th>体检</th><th>今日新增</th>
              <th>高风险</th><th>中风险</th><th>低风险</th>
              <th>待处理报告</th><th>待医生复核</th><th>待推送患者</th>
              <th>随访中</th><th>异常处理</th><th>随访完成率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in tableRows" :key="i">
              <td><div class="type-cell"><span class="type-icon">{{ i + 1 }}</span>{{ r[0] }}</div></td>
              <td><b>{{ r[1] }}</b></td>
              <td>{{ Math.round(parseInt(r[1].replace(',','')) * .63).toLocaleString() }}</td>
              <td>{{ Math.round(parseInt(r[1].replace(',','')) * .37).toLocaleString() }}</td>
              <td>{{ r[2] }}</td>
              <td class="metric-red">{{ r[3] }}</td>
              <td class="metric-orange">{{ r[4] }}</td>
              <td class="metric-green">{{ r[5] }}</td>
              <td>{{ r[6] }}</td><td>{{ r[7] }}</td><td>{{ r[8] }}</td><td>{{ r[9] }}</td>
              <td class="metric-red">{{ r[10] }}</td>
              <td>
                {{ r[11] }}
                <span class="progress"><span :style="{ width: r[11] }"></span></span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 预警列表 -->
    <section class="card" style="margin-top:12px">
      <div class="card-head">
        <div class="card-title">异常预警</div>
        <button class="ghost" @click="toast.show('查看更多')">查看更多</button>
      </div>
      <div style="padding:0 14px 12px">
        <div v-for="w in warnings" :key="w.text" class="warn-row">
          <div class="warn-ico" :class="w.tone">{{ w.icon }}</div>
          <div>
            <div class="warn-title">{{ w.title }}</div>
            <div class="warn-text">{{ w.text }}</div>
            <button class="warn-link" @click="toast.show(w.title)">立即处理</button>
          </div>
        </div>
      </div>
    </section>
  </div>
  <ToastMsg ref="toast" />
</template>

<script setup>
import { ref } from 'vue'
import KpiCard from '../components/KpiCard.vue'
import ToastMsg from '../components/ToastMsg.vue'

const toast = ref(null)
const activeTab = ref('总览')
const tabs = ['总览', '结节类型', '风险分层', '随访效果', '医生效率']

const kpis = [
  { label: '管理患者总数', value: '12,486', delta: '较上月 +8.6%', tone: 'blue', icon: '👥' },
  { label: '新增患者数', value: '326', delta: '较上月 +5.2%', tone: 'green', icon: '＋' },
  { label: '高风险患者数', value: '1,268', delta: '较上月 +12.4%', tone: 'orange', icon: '盾' },
  { label: '报告生成率', value: '92.4%', delta: '较上月 +2.1pp', tone: 'blue', icon: '文' },
  { label: '医生复核率', value: '88.7%', delta: '较上月 +1.6pp', tone: 'purple', icon: '医' },
  { label: '患者触达率', value: '93.6%', delta: '较上月 +0.8pp', tone: 'green', icon: '✉' },
  { label: '复查转化率', value: '61.3%', delta: '较上月 +1.7pp', tone: 'cyan', icon: '↻' }
]

const donutLegend = [
  { label: '肺部结节', color: '#5b8ff9', pct: '32.1%' },
  { label: '甲状腺结节', color: '#5ad8a6', pct: '25.1%' },
  { label: '乳腺结节', color: '#f6bd16', pct: '26.1%' },
  { label: '肺部合并乳腺', color: '#6dc8ec', pct: '6.5%' },
  { label: '其他合并', color: '#d3adf7', pct: '10.2%' }
]

const riskBars = [
  { label: '高风险', pct: '28%', color: '#ef4444', value: '1,348' },
  { label: '中风险', pct: '54%', color: '#f97316', value: '3,244' },
  { label: '低风险', pct: '86%', color: '#65a30d', value: '7,894' }
]

const stageBars = [
  { label: '待处理报告', pct: '18%', color: '#a855f7', value: '146' },
  { label: '待医生复核', pct: '12%', color: '#38bdf8', value: '82' },
  { label: '待推送患者', pct: '15%', color: '#84cc16', value: '95' },
  { label: '随访中', pct: '82%', color: '#4f83f1', value: '7,361' }
]

const rateMetrics = [
  { label: '报告生成率', value: '92.4%', delta: '较上月 +2.1pp', color: '#155eef' },
  { label: '医生复核率', value: '88.7%', delta: '较上月 +1.6pp', color: '#16a34a' },
  { label: '患者触达率', value: '93.6%', delta: '较上月 +0.8pp', color: '#8b5cf6' },
  { label: '随访完成率', value: '78.6%', delta: '较上月 +1.8pp', color: '#0ea5b7' }
]

const tableRows = [
  ['乳腺结节','3,256','+32','356','812','2,088','38','22','19','2,456','26','81.2%'],
  ['甲状腺结节','3,128','+28','312','790','2,026','29','18','15','2,389','21','79.4%'],
  ['肺部结节','4,012','+41','428','1,102','2,482','42','24','28','2,976','34','77.8%'],
  ['肺部合并乳腺结节','812','+9','96','208','508','10','6','8','604','8','74.4%'],
  ['肺部合并甲状腺结节','702','+7','84','176','442','8','4','6','518','6','76.1%'],
  ['甲状腺合并乳腺结节','456','+5','52','120','284','6','3','4','332','5','77.2%'],
  ['三合并结节','120','+2','20','36','64','3','2','2','86','2','72.0%']
]

const warnings = [
  { tone: 'orange', icon: '!', title: '高风险患者逾期随访', text: '张国斌已逾期 7 天，请尽快处理。' },
  { tone: 'red', icon: '⚠', title: '报告超时未处理', text: '有 18 份报告超 24 小时未处理。' },
  { tone: 'yellow', icon: '⏰', title: '批量随访提醒待发送', text: '本周有 46 名患者需要发送复查提醒。' },
  { tone: 'blue', icon: 'i', title: '新增高风险患者', text: '本周新增高风险患者 23 人，较上周增加 12%。' }
]
</script>

<style scoped>
.page{height:100%;overflow:auto}
.page-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.page-title{font-size:20px;font-weight:950;color:#0f172a}
.crumb{color:#64748b;font-weight:700}
.tabs-bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.tab{border:1px solid #e6edf7;background:#fff;border-radius:10px;padding:7px 12px;color:#526175;font-weight:900;cursor:pointer}
.tab.active{border-color:#155eef;background:#eef5ff;color:#155eef}
.kpi-row{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:12px;margin-bottom:14px}
.chart-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:0}
.card{background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 6px 18px rgba(15,23,42,.04)}
.card-head{height:46px;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:0 14px}
.card-title{font-weight:900;color:#0f172a}
.head-actions{display:flex;gap:6px}
.chart-card{min-height:200px}
.chart-body{padding:8px}
.donut{width:104px;height:104px;border-radius:50%;background:conic-gradient(#5b8ff9 0 32%,#5ad8a6 32% 57%,#f6bd16 57% 73%,#6dc8ec 73% 89%,#d3adf7 89%);display:grid;place-items:center;margin:8px auto}
.donut::after{content:"12,486\A总患者数";white-space:pre;text-align:center;width:62px;height:62px;border-radius:50%;background:#fff;display:grid;place-items:center;font-weight:900;font-size:12px;color:#0f172a}
.legend{padding:0 8px}
.legend-item{display:flex;align-items:center;gap:6px;font-size:12px;padding:3px 0;color:#475569}
.legend-item .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.legend-item .muted{margin-left:auto}
.bar-row{display:grid;grid-template-columns:72px minmax(0,1fr) 44px;gap:8px;align-items:center;margin:10px 0;color:#64748b;font-size:13px}
.bar-label{font-size:12px}
.bar{height:8px;background:#edf2f7;border-radius:99px;overflow:hidden}
.bar span{display:block;height:100%;border-radius:99px}
.rate-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #edf2f7}
.rate-row:last-child{border-bottom:0}
.rate-label{flex:1;font-size:13px;color:#475569}
.rate-value{font-size:18px;font-weight:950}
.table-wrap{overflow:auto}
.table{width:100%;border-collapse:collapse;min-width:920px}
.table th{background:#f8fafc;color:#64748b;font-size:12px;text-align:left;padding:10px 9px;border-bottom:1px solid #e5edf7;white-space:nowrap}
.table td{padding:10px 9px;border-bottom:1px solid #edf2f7;white-space:nowrap}
.type-cell{display:flex;align-items:center;gap:8px;font-weight:800}
.type-icon{width:22px;height:22px;border-radius:6px;background:#eef5ff;color:#155eef;display:flex;align-items:center;justify-content:center;font-size:12px}
.metric-red{color:#dc2626}
.metric-orange{color:#ea580c}
.metric-green{color:#15803d}
.progress{width:78px;height:6px;background:#e8eef8;border-radius:99px;overflow:hidden;display:inline-block;vertical-align:middle;margin-left:6px}
.progress span{display:block;height:100%;background:#4f83f1;border-radius:99px}
.warn-row{display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-top:1px solid #edf2f7}
.warn-ico{width:26px;height:26px;border-radius:10px;display:grid;place-items:center;font-weight:950;flex-shrink:0}
.warn-ico.orange{background:#fff7ed;color:#c2410c;border:1px solid #fed7aa}
.warn-ico.red{background:#fff1f2;color:#dc2626;border:1px solid #fecdd3}
.warn-ico.yellow{background:#fefce8;color:#a16207;border:1px solid #fde047}
.warn-ico.blue{background:#eef5ff;color:#155eef;border:1px solid #cfe0ff}
.warn-title{font-weight:950;color:#0f172a}
.warn-text{color:#64748b;line-height:1.6;margin-top:4px;font-size:13px}
.warn-link{margin-top:6px;color:#155eef;font-weight:850;background:transparent;border:0;padding:0;cursor:pointer;font-size:13px}
.btn{border:1px solid #d9e2ef;border-radius:6px;background:#fff;color:#475569;padding:6px 10px;cursor:pointer}
.ghost{border:0;background:transparent;color:#155eef;cursor:pointer;font-weight:750}
.muted{color:#64748b}
.tag.high{background:#fff1f1;color:#dc2626;display:inline-flex;align-items:center;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:900}
</style>
