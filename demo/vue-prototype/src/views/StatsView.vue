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

    <section class="card" style="margin-top:12px">
      <div class="card-head">
        <div class="card-title">提示</div>
      </div>
      <div style="padding:12px 14px;color:#64748b;line-height:1.7">
        本页面统计已精简。请前往左侧导航的 <b>运营看板</b> 查看所有统计数据。
      </div>
    </section>
  </div>
  <ToastMsg ref="toast" />
</template>

<script setup>
import { ref } from 'vue'
import ToastMsg from '../components/ToastMsg.vue'

const toast = ref(null)
const activeTab = ref('总览')
const tabs = ['总览', '结节类型', '风险分层', '随访效果', '医生效率']
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
