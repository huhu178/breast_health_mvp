<template>
  <div class="page">
    <div class="page-head">
      <div class="page-title">随访任务</div>
      <div class="crumb">首页 / <b>随访任务</b></div>
    </div>

    <div class="kpi-row">
      <KpiCard v-for="m in kpis" :key="m.label" v-bind="m" />
    </div>

    <section class="card filters-card">
      <div class="card-title" style="margin-bottom:12px">筛选条件</div>
      <div class="filter-grid">
        <label class="fi">姓名/手机号<input v-model="keyword" placeholder="请输入姓名或手机号"></label>
        <label class="fi">结节类型
          <select v-model="noduleFilter">
            <option value="all">全部</option>
            <option value="lung">肺部结节</option>
            <option value="breast">乳腺结节</option>
            <option value="thyroid">甲状腺结节</option>
          </select>
        </label>
        <label class="fi">风险等级
          <select v-model="riskFilter">
            <option value="all">全部</option>
            <option value="high">高风险</option>
            <option value="mid">中风险</option>
            <option value="low">低风险</option>
          </select>
        </label>
        <label class="fi">随访状态
          <select v-model="followStatus">
            <option value="all">全部</option>
            <option value="followup">随访中</option>
            <option value="alert">异常待处理</option>
            <option value="done">已闭环</option>
          </select>
        </label>
        <label class="fi">随访时间
          <div class="date-pair">
            <input placeholder="开始日期">
            <span>-</span>
            <input placeholder="结束日期">
          </div>
        </label>
        <div class="fi-btns">
          <button class="btn" @click="resetFilters">重置</button>
          <button class="primary" @click="toast.show('查询中...')">查询</button>
        </div>
      </div>
    </section>

    <div class="layout">
      <section class="card">
        <div class="card-head">
          <div class="card-title">随访列表 <span class="muted">共 {{ filtered.length }} 条</span></div>
          <div class="head-actions">
            <button class="btn" @click="toast.show('导出中...')">导出</button>
            <button class="btn" @click="toast.show('批量发送提醒')">批量提醒</button>
          </div>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>患者</th><th>结节类型</th><th>风险</th><th>随访状态</th>
                <th>下次随访</th><th>随访方式</th><th>负责人</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in filtered" :key="p.id"
                :class="{ active: p.id === store.currentPatientId }"
                @click="store.currentPatientId = p.id">
                <td>
                  <div><b>{{ p.name }}</b></div>
                  <div class="muted" style="font-size:11px">{{ p.age }}岁 · {{ p.phone }}</div>
                </td>
                <td><TagBadge :text="p.nodule" tone="blue" /></td>
                <td><TagBadge :text="riskText(p.risk)" :tone="riskClass(p.risk)" /></td>
                <td><TagBadge :text="stageLabels[p.stage]" :tone="stageClass(p.stage)" /></td>
                <td>{{ p.next }}</td>
                <td>
                  <div class="channel-row">
                    <span class="channel">企微</span>
                    <span class="channel">电话</span>
                  </div>
                </td>
                <td>{{ p.owner }}</td>
                <td>
                  <div class="row-actions">
                    <span class="act" @click.stop="store.currentPatientId = p.id">详情</span>
                    <span class="act" @click.stop="doRecord(p)">记录</span>
                    <span class="act" @click.stop="toast.show('发送复查提醒')">提醒</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination">
          <button class="page-btn">‹</button>
          <button class="page-btn active">1</button>
          <button class="page-btn">2</button>
          <button class="page-btn">3</button>
          <span>...</span>
          <button class="page-btn">›</button>
          <span class="muted">10 条/页</span>
        </div>
      </section>

      <section class="card" v-if="current">
        <div class="card-head">
          <div class="card-title">随访详情</div>
          <button class="ico-btn" @click="store.currentPatientId = null">×</button>
        </div>
        <div class="detail-body">
          <div v-if="current.stage === 'alert'" class="alert-tip">
            <span>⚠ 患者反馈异常症状，需立即转医生处理</span>
            <button class="btn-x" @click="toast.show('已转医生处理')">×</button>
          </div>

          <div class="detail-top">
            <div>
              <div class="detail-name">{{ current.name }}</div>
              <div class="muted" style="margin-top:4px">{{ current.gender }} · {{ current.age }}岁 · {{ current.phone }}</div>
            </div>
            <div class="badge-row">
              <TagBadge :text="riskText(current.risk)" :tone="riskClass(current.risk)" />
              <TagBadge :text="stageLabels[current.stage]" :tone="stageClass(current.stage)" />
            </div>
          </div>

          <div class="seg">
            <div class="seg-title"><span class="idx">1</span>随访任务信息</div>
            <div class="mini-kv">
              <div><div class="k">结节类型</div><div class="v">{{ current.nodule }}</div></div>
              <div><div class="k">负责人</div><div class="v">{{ current.owner }}</div></div>
              <div><div class="k">下次随访</div><div class="v">{{ current.next }}</div></div>
              <div><div class="k">随访周期</div><div class="v">{{ current.risk === 'high' ? '3个月' : current.risk === 'mid' ? '6个月' : '12个月' }}</div></div>
            </div>
          </div>

          <div class="seg">
            <div class="seg-title"><span class="idx">2</span>随访记录</div>
            <div class="timeline">
              <div v-for="(event, i) in current.events" :key="i" class="event">
                <div class="event-time">{{ i === current.events.length - 1 ? '最新' : '记录' }}</div>
                <div class="event-text">{{ event }}</div>
              </div>
            </div>
          </div>

          <div class="seg">
            <div class="seg-title"><span class="idx">3</span>AI随访建议</div>
            <div class="ai-box">{{ current.ai }}</div>
          </div>

          <div class="action-bar">
            <button class="primary" @click="doRecord(current)">记录随访结果</button>
            <button class="btn" @click="toast.show('发送复查提醒')">发送复查提醒</button>
            <button v-if="current.stage === 'alert'" class="btn danger" @click="toast.show('已转医生处理')">转医生处理</button>
          </div>
        </div>
      </section>
    </div>
  </div>
  <ToastMsg ref="toast" />
</template>

<script setup>
import { ref, computed } from 'vue'
import { store } from '../store/index.js'
import { stageLabels, riskText, riskClass, stageClass } from '../mocks/patients.js'
import TagBadge from '../components/TagBadge.vue'
import KpiCard from '../components/KpiCard.vue'
import ToastMsg from '../components/ToastMsg.vue'

const toast = ref(null)
const keyword = ref('')
const noduleFilter = ref('all')
const riskFilter = ref('all')
const followStatus = ref('all')

const kpis = [
  { label: '今日随访', value: '128', delta: '较昨日 +18', tone: 'blue', icon: '访' },
  { label: '待随访', value: '246', delta: '较昨日 +124', tone: 'orange', icon: '⏲' },
  { label: '已完成', value: '89', delta: '较昨日 +15', tone: 'green', icon: '✓' },
  { label: '逾期随访', value: '36', delta: '较昨日 +6', tone: 'orange', icon: '!' },
  { label: '异常反馈', value: '18', delta: '较昨日 +4', tone: 'purple', icon: '铃' },
  { label: '自动提醒中', value: '74', delta: '较昨日 +11', tone: 'cyan', icon: '✈' }
]

const filtered = computed(() => store.patients.filter(p => {
  if (!['followup','alert','done'].includes(p.stage) && followStatus.value === 'all') return ['followup','alert','done'].includes(p.stage)
  if (keyword.value && !`${p.name}${p.phone}${p.nodule}`.includes(keyword.value)) return false
  if (noduleFilter.value !== 'all' && !p.noduleType.includes(noduleFilter.value)) return false
  if (riskFilter.value !== 'all' && p.risk !== riskFilter.value) return false
  if (followStatus.value !== 'all' && p.stage !== followStatus.value) return false
  return ['followup','alert','done'].includes(p.stage)
}))

const current = computed(() => store.patients.find(p => p.id === store.currentPatientId))

function doRecord(p) {
  if (p.stage === 'followup' || p.stage === 'alert') {
    store.setStage(p.id, 'done', '随访结果已记录，当前闭环完成')
    toast.value?.show('随访结果已记录，当前闭环完成')
  } else {
    toast.value?.show('记录随访结果')
  }
}

function resetFilters() {
  keyword.value = ''
  noduleFilter.value = 'all'
  riskFilter.value = 'all'
  followStatus.value = 'all'
}
</script>

<style scoped>
.page{min-height:100%}
.page-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.page-title{font-size:20px;font-weight:950;color:#0f172a}
.crumb{color:#64748b;font-weight:700}
.kpi-row{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px;margin-bottom:14px}
.card{background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 6px 18px rgba(15,23,42,.04);margin-bottom:12px}
.filters-card{padding:14px 16px}
.card-title{font-weight:900;color:#0f172a}
.card-head{height:46px;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:0 14px}
.head-actions{display:flex;gap:6px}
.filter-grid{display:grid;grid-template-columns:1.15fr 1fr 1fr 1fr 1fr auto;gap:12px 18px;align-items:end}
.fi{display:flex;flex-direction:column;gap:6px;color:#475569;font-weight:750;font-size:13px}
.fi input,.fi select{height:34px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none}
.fi input:focus,.fi select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.date-pair{display:grid;grid-template-columns:1fr 16px 1fr;gap:4px;align-items:center}
.fi-btns{display:flex;gap:8px;align-items:flex-end}
.layout{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(460px,.95fr);gap:12px;align-items:start}
.table-wrap{overflow:auto}
.table{width:100%;border-collapse:collapse;min-width:900px}
.table th{background:#f8fafc;color:#64748b;font-size:12px;text-align:left;padding:10px 9px;border-bottom:1px solid #e5edf7;white-space:nowrap}
.table td{padding:10px 9px;border-bottom:1px solid #edf2f7;white-space:nowrap}
.table tbody tr{cursor:pointer}
.table tbody tr:hover{background:#f8fbff}
.table tbody tr.active{background:#eef5ff}
.channel-row{display:flex;gap:4px}
.channel{background:#eef5ff;color:#155eef;border-radius:4px;padding:2px 6px;font-size:11px;font-weight:750}
.row-actions{display:flex;gap:6px;color:#155eef;font-size:12px;font-weight:750}
.row-actions .act{cursor:pointer}
.pagination{display:flex;align-items:center;justify-content:center;gap:8px;padding:12px;border-top:1px solid #edf2f7}
.page-btn{border:1px solid #d9e2ef;background:#fff;border-radius:8px;padding:6px 10px;color:#475569;font-weight:850;cursor:pointer}
.page-btn.active{background:#155eef;color:#fff;border-color:#155eef}
.detail-body{padding:14px 16px}
.alert-tip{background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;border-radius:10px;padding:8px 10px;font-weight:800;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;font-size:13px}
.btn-x{border:0;background:transparent;color:#c2410c;font-weight:950;cursor:pointer}
.detail-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:12px}
.detail-name{font-size:16px;font-weight:950;color:#0f172a}
.badge-row{display:flex;gap:8px;flex-wrap:wrap}
.seg{border:1px solid #eef2f7;border-radius:10px;background:#fff;padding:12px;margin-bottom:10px}
.seg-title{font-weight:950;color:#0f172a;display:flex;align-items:center;gap:8px;margin-bottom:8px}
.idx{width:18px;height:18px;border-radius:6px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-size:12px;font-weight:950;flex-shrink:0}
.mini-kv{display:grid;grid-template-columns:1fr 1fr;gap:10px 14px}
.mini-kv .k{color:#94a3b8;font-size:12px}
.mini-kv .v{font-weight:900;color:#0f172a;margin-top:4px}
.timeline{display:grid;gap:0}
.event{display:grid;grid-template-columns:48px minmax(0,1fr);gap:9px;padding:8px 0;border-bottom:1px solid #edf2f7}
.event:last-child{border-bottom:0}
.event-time{color:#94a3b8;font-size:12px}
.event-text{line-height:1.6;font-size:13px}
.ai-box{background:#f8fbff;border:1px solid #dce8f8;border-radius:7px;padding:11px 12px;line-height:1.7;color:#253247;font-size:13px}
.action-bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.btn{border:1px solid #d9e2ef;border-radius:6px;background:#fff;color:#475569;padding:6px 10px;cursor:pointer}
.btn.danger{border-color:#fecdd3;color:#dc2626;background:#fff1f2}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:6px;padding:6px 10px;cursor:pointer;font-weight:750}
.ico-btn{width:34px;height:34px;border-radius:10px;border:1px solid #d9e2ef;background:#fff;color:#64748b;cursor:pointer}
.muted{color:#64748b}
</style>
