<template>
  <div class="page">
    <div class="page-head">
      <div class="page-title">医生复核</div>
      <div class="crumb">首页 / <b>医生复核</b></div>
    </div>

    <section class="card filters-card">
      <div class="card-title" style="margin-bottom:12px">筛选条件</div>
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
        <label class="fi">复核状态
          <select v-model="reviewStatus">
            <option value="all">全部</option>
            <option value="review">待复核</option>
            <option value="push">已复核</option>
          </select>
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
          <div class="card-title">待复核列表 <span class="muted">共 {{ filtered.length }} 条</span></div>
          <div class="head-actions">
            <button class="btn" @click="toast.show('导出中...')">导出</button>
            <button class="btn" @click="toast.show('批量分派')">批量分派</button>
          </div>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>患者</th><th>性别/年龄/手机号</th><th>患者来源</th>
                <th>结节类型</th><th>报告类型</th><th>AI结构化</th>
                <th>AI建议状态</th><th>复核状态</th><th>更新时间</th><th>负责人</th><th>操作</th>
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
                <td>{{ p.noduleType.includes('lung') ? 'CT报告' : '超声报告' }}</td>
                <td><TagBadge :text="p.aiStatus.includes('异常') ? '异常' : '已完成'" :tone="p.aiStatus.includes('异常') ? 'high' : 'green'" /></td>
                <td><TagBadge :text="p.risk === 'high' ? '高风险提醒' : '建议复核'" :tone="p.risk === 'high' ? 'high' : 'orange'" /></td>
                <td><TagBadge :text="stageLabels[p.stage]" :tone="stageClass(p.stage)" /></td>
                <td>{{ p.uploadTime }}</td>
                <td>{{ p.owner }}</td>
                <td>
                  <div class="row-actions">
                    <span class="act" @click.stop="store.currentPatientId = p.id">详情</span>
                    <span class="act" @click.stop="doReview(p)">复核</span>
                    <span class="act" @click.stop="toast.show('已退回修改')">退回</span>
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
          <button class="page-btn">13</button>
          <button class="page-btn">›</button>
          <span class="muted">10 条/页</span>
        </div>
      </section>

      <section class="card" v-if="current">
        <div class="card-head">
          <div class="card-title">复核详情</div>
          <div class="head-actions">
            <span class="muted" style="font-size:12px">AI建议仅供参考</span>
            <button class="ico-btn" @click="store.currentPatientId = null">×</button>
          </div>
        </div>
        <div class="review-detail">
          <div class="review-sections">
            <div class="review-top2">
              <div class="review-section">
                <div class="sec-title"><span class="idx">1</span>患者基础信息</div>
                <div class="mini-kv">
                  <div><div class="k">患者姓名</div><div class="v">{{ current.name }}</div></div>
                  <div><div class="k">性别</div><div class="v">{{ current.gender }}</div></div>
                  <div><div class="k">年龄</div><div class="v">{{ current.age }}岁</div></div>
                  <div><div class="k">手机号</div><div class="v">{{ current.phone }}</div></div>
                  <div><div class="k">来源</div><div class="v">{{ current.source }}</div></div>
                  <div><div class="k">负责人</div><div class="v">{{ current.owner }}</div></div>
                </div>
              </div>
              <div class="review-section">
                <div class="sec-title"><span class="idx">2</span>结节检查摘要</div>
                <div class="sec-text">{{ current.report }}</div>
              </div>
            </div>

            <div class="review-section">
              <div class="sec-title"><span class="idx">3</span>AI结构化结果</div>
              <div class="mini-kv">
                <div><div class="k">结节数量</div><div class="v">{{ current.noduleCount }}</div></div>
                <div><div class="k">最大直径</div><div class="v">{{ current.maxDiameter }}</div></div>
                <div><div class="k">密度</div><div class="v">{{ current.density }}</div></div>
                <div><div class="k">分级</div><div class="v">{{ current.grade }}</div></div>
              </div>
              <div class="badge-row" style="margin-top:8px">
                <TagBadge :text="stageLabels[current.stage]" :tone="stageClass(current.stage)" />
                <TagBadge v-if="current.risk === 'high'" text="高风险确认" tone="high" />
                <TagBadge text="需补充随访材料" tone="gray" />
              </div>
            </div>

            <div class="review-section">
              <div class="sec-title"><span class="idx">4</span>AI建议管理报告草稿</div>
              <div class="sec-text">{{ current.ai }}</div>
            </div>

            <div class="review-section">
              <div class="sec-title"><span class="idx">5</span>医生复核意见</div>
              <div class="sec-text muted">复核意见将影响风险分层与后续推送策略，请谨慎确认。</div>
              <div class="hline"></div>
              <div class="sec-text">
                <b>风险分层：</b>
                <TagBadge :text="riskText(current.risk)" :tone="riskClass(current.risk)" />
                <span class="muted">（建议复查周期 {{ current.risk === 'high' ? '3' : '6' }} 个月）</span>
              </div>
            </div>

            <div class="review-section">
              <div class="sec-title"><span class="idx">6</span>处理流程</div>
              <div class="flow-line">
                <div v-for="(node, i) in flowNodes" :key="i" class="flow-node" :class="node.cls">
                  <div class="flow-dot">{{ node.done ? '✓' : i + 1 }}</div>
                  <div>{{ node.label }}</div>
                  <div class="muted" style="font-size:10px">{{ node.sub }}</div>
                </div>
              </div>
              <div class="switch-row">
                <div class="sw">
                  <span>是否同意推送患者</span>
                  <span class="toggle on" aria-hidden="true"></span>
                </div>
                <div class="sw">
                  <span>是否开启随访任务</span>
                  <span class="toggle" aria-hidden="true"></span>
                </div>
              </div>
            </div>
          </div>

          <div class="action-bar">
            <button class="primary" @click="doReview(current)">确认复核</button>
            <button class="btn" @click="toast.show('已退回修改')">退回修改</button>
            <button class="btn" @click="toast.show('查看原始报告')">查看原始报告</button>
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
const reviewStatus = ref('all')

const filtered = computed(() => store.patients.filter(p => {
  if (keyword.value && !`${p.name}${p.phone}${p.nodule}`.includes(keyword.value)) return false
  if (source.value !== 'all' && p.source !== source.value) return false
  if (noduleFilter.value !== 'all' && !p.noduleType.includes(noduleFilter.value)) return false
  if (riskFilter.value !== 'all' && p.risk !== riskFilter.value) return false
  if (reviewStatus.value !== 'all' && p.stage !== reviewStatus.value) return false
  return true
}))

const current = computed(() => store.patients.find(p => p.id === store.currentPatientId))

const flowNodes = computed(() => {
  if (!current.value) return []
  const order = ['report','parsed','review','push','followup']
  const idx = order.indexOf(current.value.stage)
  return [
    { label: '上传报告', sub: current.value.uploadTime },
    { label: 'AI解析', sub: '已完成' },
    { label: '结构化结果', sub: '已完成' },
    { label: '医生复核', sub: '进行中' },
    { label: '允许推送', sub: idx >= 3 ? '已完成' : '待处理' },
    { label: '随访闭环', sub: idx >= 4 ? '已完成' : '待处理' }
  ].map((n, i) => ({
    ...n,
    done: i < idx,
    cls: i < idx ? 'done' : (i === idx ? 'active' : '')
  }))
})

function doReview(p) {
  store.setStage(p.id, 'push', '医生已复核，允许推送患者')
  toast.value?.show('医生已复核，允许推送患者')
}

function resetFilters() {
  keyword.value = ''
  source.value = 'all'
  noduleFilter.value = 'all'
  riskFilter.value = 'all'
  reviewStatus.value = 'all'
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
.head-actions{display:flex;gap:6px;align-items:center}
.filter-grid{display:grid;grid-template-columns:1.15fr 1fr 1fr 1fr 1fr auto;gap:12px 18px;align-items:end}
.fi{display:flex;flex-direction:column;gap:6px;color:#475569;font-weight:750;font-size:13px}
.fi input,.fi select{height:34px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none}
.fi input:focus,.fi select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.fi-btns{display:flex;gap:8px;align-items:flex-end}
.layout{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(440px,.9fr);gap:12px;align-items:start}
.table-wrap{overflow:auto}
.table{width:100%;border-collapse:collapse;min-width:1040px}
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
.review-detail{padding:14px 16px}
.review-sections{display:grid;gap:10px}
.review-top2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.review-section{border:1px solid #eef2f7;border-radius:10px;padding:12px;background:#fff}
.sec-title{font-weight:950;color:#0f172a;display:flex;align-items:center;gap:8px;margin-bottom:8px}
.idx{width:18px;height:18px;border-radius:6px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-size:12px;font-weight:950;flex-shrink:0}
.sec-text{line-height:1.75;color:#334155;font-size:13px}
.mini-kv{display:grid;grid-template-columns:1fr 1fr;gap:10px 14px}
.mini-kv .k{color:#94a3b8;font-size:12px}
.mini-kv .v{font-weight:900;color:#0f172a;margin-top:4px}
.badge-row{display:flex;gap:8px;flex-wrap:wrap}
.hline{height:1px;background:#edf2f7;margin:10px 0}
.flow-line{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;margin:10px 0;text-align:center;font-size:11px;color:#64748b}
.flow-dot{width:18px;height:18px;border-radius:50%;background:#cbd5e1;margin:0 auto 6px;display:grid;place-items:center;color:#fff;font-size:11px;font-weight:900}
.flow-node.done .flow-dot{background:#22c55e}
.flow-node.active .flow-dot{background:#155eef}
.switch-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}
.sw{display:flex;align-items:center;justify-content:space-between;border:1px solid #eef2f7;border-radius:10px;padding:10px 12px;background:#fff;font-size:13px}
.toggle{width:38px;height:22px;border-radius:999px;background:#e5e7eb;position:relative;flex-shrink:0}
.toggle::after{content:"";position:absolute;left:3px;top:3px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(15,23,42,.15)}
.toggle.on{background:#155eef}
.toggle.on::after{left:19px}
.action-bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.btn{border:1px solid #d9e2ef;border-radius:6px;background:#fff;color:#475569;padding:6px 10px;cursor:pointer}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:6px;padding:6px 10px;cursor:pointer;font-weight:750}
.ico-btn{width:34px;height:34px;border-radius:10px;border:1px solid #d9e2ef;background:#fff;color:#64748b;cursor:pointer}
.muted{color:#64748b}
</style>
