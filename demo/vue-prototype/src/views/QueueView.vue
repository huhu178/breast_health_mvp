<template>
  <div class="page">
    <div class="page-head">
      <div class="page-title">患者队列</div>
      <div class="crumb">首页 / <b>患者队列</b></div>
    </div>

    <!-- 筛选 -->
    <section class="card filters-card">
      <div class="card-title" style="margin-bottom:12px">筛选条件</div>
      <div class="filter-grid">
        <label class="fi">姓名/手机号<input v-model="keyword" placeholder="请输入姓名或手机号"></label>
        <label class="fi">患者来源
          <select v-model="source">
            <option value="all">全部</option>
            <option>门诊</option>
            <option>体检中心</option>
          </select>
        </label>
        <label class="fi">结节类型
          <select v-model="noduleFilter">
            <option value="all">全部</option>
            <option v-for="t in noduleTypes" :key="t[0]" :value="t[0]">{{ t[1] }}</option>
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
        <label class="fi">当前状态
          <select v-model="stageFilter">
            <option value="all">全部</option>
            <option v-for="(v,k) in stageLabels" :key="k" :value="k">{{ v }}</option>
          </select>
        </label>
        <div class="fi-btns">
          <button class="btn" @click="resetFilters">重置</button>
          <button class="primary" @click="newPatient">+ 新建档案</button>
        </div>
      </div>
    </section>

    <div class="layout">
      <!-- 列表 -->
      <section class="card">
        <div class="card-head">
          <div class="card-title">患者列表 <span class="muted">共 {{ filtered.length }} 条</span></div>
          <div class="head-actions">
            <button class="btn" @click="toast.show('导出中...')">导出</button>
            <button class="btn" @click="toast.show('批量分派')">批量分派</button>
          </div>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>患者姓名</th><th>性别/年龄/手机号</th><th>患者来源</th>
                <th>结节类型</th><th>风险等级</th><th>当前状态</th>
                <th>下次随访</th><th>负责人</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in filtered" :key="p.id"
                :class="{ active: p.id === store.currentPatientId }"
                @click="store.currentPatientId = p.id">
                <td><b>{{ p.name }}</b></td>
                <td>{{ p.gender }} / {{ p.age }}岁 / {{ p.phone }}</td>
                <td>{{ p.source }}</td>
                <td><TagBadge :text="p.nodule" tone="blue" /></td>
                <td><TagBadge :text="riskText(p.risk)" :tone="riskClass(p.risk)" /></td>
                <td><TagBadge :text="stageLabels[p.stage]" :tone="stageClass(p.stage)" /></td>
                <td>{{ p.next }}</td>
                <td>{{ p.owner }}</td>
                <td>
                  <div class="row-actions">
                    <span class="act" @click.stop="store.currentPatientId = p.id">查看</span>
                    <span class="act" @click.stop="toast.show('报告处理')">报告</span>
                    <span class="act" @click.stop="toast.show('随访任务')">随访</span>
                    <span class="act" @click.stop="toast.show('患者触达')">触达</span>
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

      <!-- 详情 -->
      <section class="card detail-card" v-if="current">
        <div class="card-head">
          <div class="card-title">患者详情</div>
          <button class="ghost" @click="store.currentPatientId = null">×</button>
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
            <div class="kv"><div class="k">患者来源</div><div class="v">{{ current.source }}</div></div>
            <div class="kv"><div class="k">下次随访</div><div class="v">{{ current.next }}</div></div>
          </div>

          <div class="hline"></div>
          <div class="detail-line"><b>报告摘要</b></div>
          <div class="detail-text">{{ current.report }}</div>

          <div class="hline"></div>
          <div class="detail-line"><b>流程进度</b></div>
          <div class="flow-line">
            <div v-for="(node, i) in flowNodes" :key="i"
              class="flow-node" :class="node.cls">
              <div class="flow-dot">{{ node.done ? '✓' : i + 1 }}</div>
              <div>{{ node.label }}</div>
              <div class="muted" style="font-size:10px">{{ node.sub }}</div>
            </div>
          </div>

          <div class="action-bar">
            <button class="primary" @click="toast.show('处理报告')">处理报告</button>
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
const stageFilter = ref('all')

const noduleTypes = [
  ['breast','乳腺结节'],['thyroid','甲状腺结节'],['lung','肺部结节'],
  ['lung_breast','肺部合并乳腺结节'],['lung_thyroid','肺部合并甲状腺结节'],
  ['thyroid_breast','甲状腺合并乳腺结节'],['thyroid_breast_lung','甲状腺、乳腺合并肺部结节'],
  ['triple','三合并结节']
]

const filtered = computed(() => store.patients.filter(p => {
  if (keyword.value && !`${p.name}${p.phone}${p.nodule}`.includes(keyword.value)) return false
  if (source.value !== 'all' && p.source !== source.value) return false
  if (noduleFilter.value !== 'all' && p.noduleType !== noduleFilter.value) return false
  if (riskFilter.value !== 'all' && p.risk !== riskFilter.value) return false
  if (stageFilter.value !== 'all' && p.stage !== stageFilter.value) return false
  return true
}))

const current = computed(() => store.patients.find(p => p.id === store.currentPatientId))

const flowNodes = computed(() => {
  if (!current.value) return []
  const order = ['report','parsed','review','push','followup']
  const idx = order.indexOf(current.value.stage)
  return [
    { label: '建档', sub: '已完成' },
    { label: '报告上传', sub: '已完成' },
    { label: 'AI解析', sub: '已完成' },
    { label: '医生复核', sub: idx >= 2 ? '已完成' : '进行中' },
    { label: '推送', sub: idx >= 3 ? '已完成' : '待处理' },
    { label: '随访', sub: idx >= 4 ? '已完成' : '待处理' }
  ].map((n, i) => ({
    ...n,
    done: i < idx,
    cls: i < idx ? 'done' : (i === idx ? 'active' : '')
  }))
})

function resetFilters() {
  keyword.value = ''
  source.value = 'all'
  noduleFilter.value = 'all'
  riskFilter.value = 'all'
  stageFilter.value = 'all'
}

function newPatient() {
  toast.value?.show('新建患者档案')
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
.filter-grid{display:grid;grid-template-columns:1.35fr 1fr 1fr 1fr 1fr auto;gap:12px 18px;align-items:end}
.fi{display:flex;flex-direction:column;gap:6px;color:#475569;font-weight:750;font-size:13px}
.fi input,.fi select{height:34px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none}
.fi input:focus,.fi select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.fi-btns{display:flex;gap:8px;align-items:flex-end}
.layout{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(380px,.9fr);gap:12px;align-items:start}
.table-wrap{overflow:auto}
.table{width:100%;border-collapse:collapse;min-width:860px}
.table th{background:#f8fafc;color:#64748b;font-size:12px;text-align:left;padding:10px 9px;border-bottom:1px solid #e5edf7;white-space:nowrap}
.table td{padding:10px 9px;border-bottom:1px solid #edf2f7;white-space:nowrap}
.table tbody tr{cursor:pointer}
.table tbody tr:hover{background:#f8fbff}
.table tbody tr.active{background:#eef5ff}
.row-actions{display:flex;gap:6px;color:#155eef;font-size:12px;font-weight:750}
.row-actions .act{cursor:pointer}
.row-actions .act:hover{text-decoration:underline}
.pagination{display:flex;align-items:center;justify-content:center;gap:8px;padding:12px;border-top:1px solid #edf2f7}
.page-btn{border:1px solid #d9e2ef;background:#fff;border-radius:8px;padding:6px 10px;color:#475569;font-weight:850;cursor:pointer}
.page-btn.active{background:#155eef;color:#fff;border-color:#155eef}
.detail-card{min-height:420px}
.detail-body{padding:14px 16px}
.detail-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:12px}
.detail-name{font-size:16px;font-weight:950;color:#0f172a}
.badge-row{display:flex;gap:8px;flex-wrap:wrap}
.kv-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px 18px;margin-bottom:12px}
.kv .k{color:#94a3b8;font-size:12px}
.kv .v{font-weight:900;color:#0f172a;margin-top:4px}
.hline{height:1px;background:#edf2f7;margin:12px 0}
.detail-line{font-weight:850;margin-bottom:6px}
.detail-text{color:#334155;line-height:1.7;font-size:13px}
.flow-line{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;margin:10px 0;text-align:center;font-size:11px;color:#64748b}
.flow-node{position:relative}
.flow-dot{width:18px;height:18px;border-radius:50%;background:#cbd5e1;margin:0 auto 6px;display:grid;place-items:center;color:#fff;font-size:11px;font-weight:900}
.flow-node.done .flow-dot{background:#22c55e}
.flow-node.active .flow-dot{background:#155eef}
.action-bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.btn{border:1px solid #d9e2ef;border-radius:6px;background:#fff;color:#475569;padding:6px 10px;cursor:pointer}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:6px;padding:6px 10px;cursor:pointer;font-weight:750}
.ghost{border:0;background:transparent;color:#64748b;cursor:pointer;font-size:16px}
.muted{color:#64748b}
</style>
