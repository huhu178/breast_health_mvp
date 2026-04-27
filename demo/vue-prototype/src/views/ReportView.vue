<template>
  <div class="page">
    <div class="page-head">
      <div class="page-title">报告处理</div>
      <div class="crumb">首页 / <b>报告处理</b></div>
    </div>

    <section class="card filters-card">
      <div class="card-title" style="margin-bottom:12px">
        筛选条件 <span class="muted" style="margin-left:8px;font-weight:700">可按姓名、手机号、结节类型、风险等级、当前状态筛选</span>
      </div>
      <div class="filter-grid">
        <label class="fi">姓名/手机号<input v-model="keyword" placeholder="请输入姓名或手机号"></label>
        <label class="fi">患者来源
          <select v-model="source">
            <option value="all">门诊 / 体检中心</option>
            <option>门诊</option>
            <option>体检中心</option>
          </select>
        </label>
        <label class="fi">结节类型
          <select v-model="noduleFilter">
            <option value="all">全部结节类型</option>
            <option value="lung">肺部结节</option>
            <option value="breast">乳腺结节</option>
            <option value="thyroid">甲状腺结节</option>
            <option value="triple">多部位合并</option>
          </select>
        </label>
        <label class="fi">风险等级
          <select v-model="riskFilter">
            <option value="all">高风险 / 中风险 / 低风险</option>
            <option value="high">高风险</option>
            <option value="mid">中风险</option>
            <option value="low">低风险</option>
          </select>
        </label>
        <label class="fi">AI解析状态
          <select v-model="aiFilter">
            <option value="all">全部状态</option>
            <option>待处理报告</option>
            <option>AI解析中</option>
            <option>解析完成</option>
            <option>异常报告</option>
          </select>
        </label>
        <div class="fi-btns">
          <button class="btn" @click="resetFilters">重置</button>
          <button class="primary" @click="toast.show('查询中...')">查询</button>
          <button class="primary" @click="toast.show('上传报告')">上传报告</button>
        </div>
      </div>
    </section>

    <div class="layout">
      <section class="card">
        <div class="card-head">
          <div class="card-title">报告列表 <span class="muted">共 {{ filtered.length }} 条</span></div>
          <div class="head-actions">
            <button class="btn" @click="toast.show('导出中...')">导出</button>
            <button class="btn" @click="toast.show('批量分派')">批量分派</button>
          </div>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>患者</th><th>来源</th><th>报告类型</th><th>结节类型</th>
                <th>上传时间</th><th>AI解析状态</th><th>风险等级</th><th>负责人</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in filtered" :key="p.id"
                :class="{ active: p.id === store.currentPatientId }"
                @click="store.currentPatientId = p.id">
                <td><b>{{ p.name }}</b></td>
                <td>{{ p.source }}</td>
                <td>{{ p.noduleType.includes('lung') ? 'CT报告' : '超声报告' }}</td>
                <td><TagBadge :text="p.nodule" tone="blue" /></td>
                <td>{{ p.uploadTime }}</td>
                <td><TagBadge :text="p.aiStatus" :tone="aiStatusTone(p.aiStatus)" /></td>
                <td><TagBadge :text="riskText(p.risk)" :tone="riskClass(p.risk)" /></td>
                <td>{{ p.owner }}</td>
                <td>
                  <div class="row-actions">
                    <span class="act" @click.stop="store.currentPatientId = p.id">详情</span>
                    <span class="act" @click.stop="handleProcess(p)">处理</span>
                    <span class="act" @click.stop="toast.show('随访任务')">随访</span>
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
          <button class="page-btn">27</button>
          <button class="page-btn">›</button>
          <span class="muted">10 条/页</span>
        </div>
      </section>

      <section class="card" v-if="current">
        <div class="card-head">
          <div class="card-title">报告详情</div>
          <button class="ico-btn" @click="store.currentPatientId = null">×</button>
        </div>
        <div class="detail-body">
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

          <div class="kv-grid">
            <div class="kv"><div class="k">结节类型</div><div class="v">{{ current.nodule }}</div></div>
            <div class="kv"><div class="k">负责人</div><div class="v">{{ current.owner }}</div></div>
            <div class="kv"><div class="k">上传时间</div><div class="v">{{ current.uploadTime }}</div></div>
            <div class="kv"><div class="k">最近检查</div><div class="v">{{ current.noduleType.includes('lung') ? '胸部CT' : '超声' }}</div></div>
          </div>

          <div class="hline"></div>
          <div class="section-label">AI结构化字段</div>
          <div class="kv-grid">
            <div class="kv"><div class="k">结节数量</div><div class="v">{{ current.noduleCount }}</div></div>
            <div class="kv"><div class="k">最大直径</div><div class="v">{{ current.maxDiameter }}</div></div>
            <div class="kv"><div class="k">密度</div><div class="v">{{ current.density }}</div></div>
            <div class="kv"><div class="k">分级</div><div class="v">{{ current.grade }}</div></div>
          </div>

          <div class="hline"></div>
          <div class="section-label">流程进度</div>
          <div class="flow-line">
            <div v-for="(node, i) in flowNodes" :key="i" class="flow-node" :class="node.cls">
              <div class="flow-dot">{{ node.done ? '✓' : i + 1 }}</div>
              <div>{{ node.label }}</div>
              <div class="muted" style="font-size:10px">{{ node.sub }}</div>
            </div>
          </div>

          <div class="action-bar">
            <button class="primary" @click="handleProcess(current)">处理报告</button>
            <button class="btn" @click="toast.show('发起复核')">发起复核</button>
            <button class="btn" @click="toast.show('推送患者')">推送患者</button>
            <button class="btn" @click="toast.show('创建随访任务')">创建随访任务</button>
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
import ToastMsg from '../components/ToastMsg.vue'

const toast = ref(null)
const keyword = ref('')
const source = ref('all')
const noduleFilter = ref('all')
const riskFilter = ref('all')
const aiFilter = ref('all')

const filtered = computed(() => store.patients.filter(p => {
  if (keyword.value && !`${p.name}${p.phone}${p.nodule}`.includes(keyword.value)) return false
  if (source.value !== 'all' && p.source !== source.value) return false
  if (noduleFilter.value !== 'all' && !p.noduleType.includes(noduleFilter.value)) return false
  if (riskFilter.value !== 'all' && p.risk !== riskFilter.value) return false
  if (aiFilter.value !== 'all' && p.aiStatus !== aiFilter.value) return false
  return true
}))

const current = computed(() => store.patients.find(p => p.id === store.currentPatientId))

const flowNodes = computed(() => {
  if (!current.value) return []
  const order = ['report','parsed','review','push','followup']
  const idx = order.indexOf(current.value.stage)
  return [
    { label: '上传报告', sub: current.value.uploadTime },
    { label: 'AI解析', sub: 'AI处理中' },
    { label: '结构化结果', sub: '字段提取' },
    { label: '医生复核', sub: idx >= 2 ? '已完成' : '待处理' },
    { label: '返回队列', sub: idx >= 4 ? '已完成' : '待处理' }
  ].map((n, i) => ({
    ...n,
    done: i < idx,
    cls: i < idx ? 'done' : (i === idx ? 'active' : '')
  }))
})

function aiStatusTone(status) {
  if (status.includes('异常')) return 'high'
  if (status.includes('解析中')) return 'orange'
  if (status.includes('完成')) return 'green'
  return 'gray'
}

function handleProcess(p) {
  if (p.stage === 'report') {
    store.setStage(p.id, 'parsed', 'AI结构化解析完成')
    toast.value?.show('AI结构化解析完成')
  } else {
    toast.value?.show('报告处理中...')
  }
}

function resetFilters() {
  keyword.value = ''
  source.value = 'all'
  noduleFilter.value = 'all'
  riskFilter.value = 'all'
  aiFilter.value = 'all'
}
</script>

<style scoped>
.page{min-height:100%}
.page-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.page-title{font-size:20px;font-weight:950;color:#0f172a}
.crumb{color:#64748b;font-weight:700}
.card{background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 6px 18px rgba(15,23,42,.04);margin-bottom:12px}
.filters-card{padding:14px 16px}
.card-title{font-weight:900;color:#0f172a}
.card-head{height:46px;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:0 14px}
.head-actions{display:flex;gap:6px}
.filter-grid{display:grid;grid-template-columns:1.2fr 1fr 1fr 1fr 1fr auto;gap:12px 18px;align-items:end}
.fi{display:flex;flex-direction:column;gap:6px;color:#475569;font-weight:750;font-size:13px}
.fi input,.fi select{height:34px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none}
.fi input:focus,.fi select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.fi-btns{display:flex;gap:8px;align-items:flex-end}
.layout{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(420px,.85fr);gap:12px;align-items:start}
.table-wrap{overflow:auto}
.table{width:100%;border-collapse:collapse;min-width:980px}
.table th{background:#f8fafc;color:#64748b;font-size:12px;text-align:left;padding:10px 9px;border-bottom:1px solid #e5edf7;white-space:nowrap}
.table td{padding:10px 9px;border-bottom:1px solid #edf2f7;white-space:nowrap}
.table tbody tr{cursor:pointer}
.table tbody tr:hover{background:#f8fbff}
.table tbody tr.active{background:#eef5ff}
.row-actions{display:flex;gap:6px;color:#155eef;font-size:12px;font-weight:750}
.row-actions .act{cursor:pointer}
.pagination{display:flex;align-items:center;justify-content:center;gap:8px;padding:12px;border-top:1px solid #edf2f7}
.page-btn{border:1px solid #d9e2ef;background:#fff;border-radius:8px;padding:6px 10px;color:#475569;font-weight:850;cursor:pointer}
.page-btn.active{background:#155eef;color:#fff;border-color:#155eef}
.detail-body{padding:14px 16px}
.detail-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:12px}
.detail-name{font-size:16px;font-weight:950;color:#0f172a}
.badge-row{display:flex;gap:8px;flex-wrap:wrap}
.kv-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px 18px;margin-bottom:12px}
.kv .k{color:#94a3b8;font-size:12px}
.kv .v{font-weight:900;color:#0f172a;margin-top:4px}
.hline{height:1px;background:#edf2f7;margin:12px 0}
.section-label{font-weight:850;margin-bottom:8px;color:#0f172a}
.flow-line{display:grid;grid-template-columns:repeat(5,1fr);gap:4px;margin:10px 0;text-align:center;font-size:11px;color:#64748b}
.flow-dot{width:18px;height:18px;border-radius:50%;background:#cbd5e1;margin:0 auto 6px;display:grid;place-items:center;color:#fff;font-size:11px;font-weight:900}
.flow-node.done .flow-dot{background:#22c55e}
.flow-node.active .flow-dot{background:#155eef}
.action-bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.btn{border:1px solid #d9e2ef;border-radius:6px;background:#fff;color:#475569;padding:6px 10px;cursor:pointer}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:6px;padding:6px 10px;cursor:pointer;font-weight:750}
.ico-btn{width:34px;height:34px;border-radius:10px;border:1px solid #d9e2ef;background:#fff;color:#64748b;cursor:pointer}
.muted{color:#64748b}
</style>
