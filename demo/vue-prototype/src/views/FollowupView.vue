<template>
  <div class="page">
    <div class="page-head">
      <div class="page-title">随访任务</div>
      <div class="crumb">首页 / <b>随访任务</b></div>
    </div>

    <!-- KPI 行（对齐截图样式） -->
    <section class="kpi-row" aria-label="随访关键指标">
      <article v-for="m in metrics" :key="m.label" class="kpi" :data-tone="m.tone">
        <div class="kpi-ico" aria-hidden="true">
          <svg v-if="m.icon === 'today'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /><path d="M8 14h4M8 18h6" />
          </svg>
          <svg v-else-if="m.icon === 'clock'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
          </svg>
          <svg v-else-if="m.icon === 'check'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 6L9 17l-5-5" /><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
          </svg>
          <svg v-else-if="m.icon === 'alert'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><path d="M12 9v4M12 17h.01" />
          </svg>
          <svg v-else-if="m.icon === 'bell'" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8a6 6 0 1 0-12 0c0 7-3 7-3 7h18s-3 0-3-7" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 2L11 13" /><path d="M22 2l-7 20-4-9-9-4z" />
          </svg>
        </div>
        <div class="kpi-label">{{ m.label }}</div>
        <div class="kpi-value">{{ m.value }}</div>
        <div class="kpi-delta">{{ m.delta }}</div>
        <svg class="spark" viewBox="0 0 70 26" aria-hidden="true">
          <path :d="sparkPath(m.delta)" />
        </svg>
      </article>
    </section>

    <section class="card filters-card">
      <div class="card-title" style="margin-bottom:12px">筛选条件</div>
      <div class="filter-grid">
        <label class="fi">姓名/手机号<input v-model="keyword" placeholder="请输入姓名或手机号"></label>
        <label class="fi">患者来源
          <select v-model="sourceFilter">
            <option value="all">门诊 / 体检中心</option>
            <option value="门诊">门诊</option>
            <option value="体检中心">体检中心</option>
          </select>
        </label>
        <label class="fi">结节类型
          <select v-model="noduleFilter">
            <option value="all">乳腺、甲状腺、肺部等</option>
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
        <label class="fi">随访方式
          <select v-model="channelFilter">
            <option value="all">企微 / 电话 / 小程序</option>
            <option value="wecom">企微</option>
            <option value="phone">电话</option>
            <option value="miniapp">小程序</option>
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
        <label class="fi">负责人
          <select v-model="ownerFilter">
            <option value="all">负责人（全部）</option>
            <option value="健康管理师">健康管理师</option>
            <option value="李医生">李医生</option>
            <option value="王医生">王医生</option>
            <option value="未分派">未分派</option>
          </select>
        </label>
        <div class="fi-btns">
          <button class="btn" @click="resetFilters">重置</button>
          <button class="primary" @click="toast.show('查询中...')">查询</button>
          <button class="primary" @click="toast.show('新建随访任务')">新建随访任务</button>
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
            <div class="seg-title"><span class="idx">A</span>基本信息</div>
            <div class="mini-kv">
              <div><div class="k">结节类型</div><div class="v">{{ current.nodule }}</div></div>
              <div><div class="k">负责人</div><div class="v">{{ current.owner }}</div></div>
              <div><div class="k">下次随访时间</div><div class="v">{{ current.next }}</div></div>
              <div><div class="k">随访周期</div><div class="v">{{ current.risk === 'high' ? '3个月' : current.risk === 'mid' ? '6个月' : '12个月' }}</div></div>
            </div>
          </div>

          <div class="seg">
            <div class="seg-title"><span class="idx">B</span>随访计划</div>
            <div class="plan-grid">
              <div class="plan-row">
                <span class="k">计划来源</span>
                <span class="v">
                  {{ planState.title || '甲状腺结节合并肺结节健康管理方案（含心理）' }}
                  <a class="plan-link" href="/plans/9 甲状腺结节合并肺结节健康管理方案加心理.xlsx" target="_blank" rel="noreferrer">下载原表</a>
                </span>
              </div>
              <div class="plan-row">
                <span class="k">计划天数</span>
                <span class="v">
                  <span v-if="planState.loading" class="muted">加载中…</span>
                  <span v-else-if="planState.error" class="muted">{{ planState.error }}</span>
                  <span v-else>Day {{ planDay.replace('day','') }} / {{ planDayList.length }}</span>
                </span>
              </div>
              <div class="plan-row">
                <span class="k">选择天数</span>
                <span class="v">
                  <select class="plan-select" v-model="planDay" :disabled="planState.loading || !!planState.error">
                    <option v-for="d in planDayList" :key="d" :value="d">Day {{ d.replace('day','') }}</option>
                  </select>
                  <button class="btn" type="button" @click="loadPlan">刷新</button>
                </span>
              </div>
              <div class="plan-row"><span class="k">随访方式</span><span class="v">企微 / 电话 / 小程序</span></div>
              <div class="plan-row"><span class="k">提醒策略</span><span class="v">到期前 3 天自动提醒；逾期转人工；异常优先转医生</span></div>
              <div class="plan-row"><span class="k">计划说明</span><span class="v">按风险分层触达，饮食+运动+心理协同；化痰不伤阴、理气不耗气</span></div>
            </div>

            <div v-if="!planState.loading && !planState.error" class="plan-items">
              <div class="plan-item" v-for="(r, idx) in currentPlanRows" :key="idx">
                <div class="plan-time">{{ r.time || '—' }}</div>
                <div class="plan-main">
                  <div class="plan-sum">{{ r.summary }}</div>
                  <div v-if="r.remind" class="plan-remind">{{ r.remind }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="seg">
            <div class="seg-title"><span class="idx">C</span>随访内容</div>
            <div class="checklist">
              <label class="ck"><input type="checkbox" checked>复查时间确认</label>
              <label class="ck"><input type="checkbox" checked>症状询问与分级</label>
              <label class="ck"><input type="checkbox">复查预约与材料准备</label>
              <label class="ck"><input type="checkbox">用药/生活方式建议</label>
            </div>
          </div>

          <div class="seg">
            <div class="seg-title"><span class="idx">D</span>患者反馈</div>
            <div class="ai-box">
              <div class="ai-block">
                <div class="ai-sub">患者反馈</div>
                <div class="ai-text">{{ current.ai }}</div>
              </div>
              <div v-if="planQuick.psych || planQuick.sport" class="ai-split"></div>
              <div v-if="planQuick.psych || planQuick.sport" class="ai-block">
                <div class="ai-sub">AI随访建议（来自 Day {{ planDay.replace('day','') }}）</div>
                <div v-if="planQuick.sport" class="ai-text"><b>运动：</b>{{ planQuick.sport }}</div>
                <div v-if="planQuick.psych" class="ai-text" style="margin-top:8px"><b>心理：</b>{{ planQuick.psych }}</div>
              </div>
            </div>
          </div>

          <div class="seg">
            <div class="seg-title"><span class="idx">E</span>重要节点记录</div>
            <div class="timeline">
              <div v-for="(event, i) in current.events" :key="i" class="event">
                <div class="event-time">{{ i === current.events.length - 1 ? '最新' : '记录' }}</div>
                <div class="event-text">{{ event }}</div>
              </div>
            </div>
          </div>

          <div class="seg">
            <div class="seg-title"><span class="idx">F</span>随访进度</div>
            <div class="flow-line">
              <div v-for="(n, i) in followFlow" :key="n.label" class="flow-node" :class="n.cls">
                <div class="flow-dot">{{ n.done ? '✓' : i + 1 }}</div>
                <div class="flow-label">{{ n.label }}</div>
                <div class="muted" style="font-size:10px">{{ n.sub }}</div>
              </div>
            </div>
          </div>

          <div class="action-bar">
            <button class="primary" @click="doRecord(current)">录随访</button>
            <button class="btn" @click="toast.show('发送提醒')">发送提醒</button>
            <button class="btn" @click="toast.show('已完成闭环')">已完成闭环</button>
            <button v-if="current.stage === 'alert'" class="btn danger" @click="toast.show('转人工/医生处理')">转人工</button>
            <button class="btn" @click="toast.show('标记完成')">标记完成</button>
          </div>
        </div>
      </section>
    </div>
  </div>
  <ToastMsg ref="toast" />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { store } from '../store/index.js'
import { stageLabels, riskText, riskClass, stageClass } from '../mocks/patients.js'
import TagBadge from '../components/TagBadge.vue'
import ToastMsg from '../components/ToastMsg.vue'

const toast = ref(null)
const keyword = ref('')
const sourceFilter = ref('all')
const noduleFilter = ref('all')
const riskFilter = ref('all')
const channelFilter = ref('all')
const followStatus = ref('all')
const ownerFilter = ref('all')

const planState = ref({
  loading: true,
  error: '',
  title: '',
  sourceFile: '',
  days: {}
})
const planDay = ref('day1')

/**
 * @description 加载随访计划（从 public/plans 读取 JSON）
 */
async function loadPlan() {
  planState.value.loading = true
  planState.value.error = ''
  try {
    const res = await fetch('/plans/thyroid-lung-psych.json', { cache: 'no-cache' })
    if (!res.ok) throw new Error(`加载计划失败：${res.status}`)
    const data = await res.json()
    planState.value = {
      loading: false,
      error: '',
      title: data?.title ?? '',
      sourceFile: data?.sourceFile ?? '',
      days: data?.days ?? {}
    }
    if (!planState.value.days?.[planDay.value]) {
      const first = Object.keys(planState.value.days ?? {})[0]
      if (first) planDay.value = first
    }
  } catch (e) {
    planState.value.loading = false
    planState.value.error = e?.message || '加载计划失败'
  }
}

onMounted(() => {
  loadPlan()
})

const planDayList = computed(() => {
  const keys = Object.keys(planState.value.days ?? {})
  // day1..day90 排序
  return keys.sort((a, b) => Number(a.replace('day', '')) - Number(b.replace('day', '')))
})

const currentPlanRows = computed(() => planState.value.days?.[planDay.value] ?? [])

function pickFirst(prefix) {
  return currentPlanRows.value.find((r) => String(r?.summary ?? '').includes(prefix))?.summary || ''
}

const planQuick = computed(() => {
  const sport = pickFirst('运动')
  const psych = pickFirst('心理')
  const knowledge = pickFirst('知识卡')
  return { sport, psych, knowledge }
})

const metrics = computed(() => ([
  { label: '今日随访', value: '128', delta: '较昨日 +18', tone: 'blue', icon: 'today' },
  { label: '待随访', value: '246', delta: '较昨日 +124', tone: 'orange', icon: 'clock' },
  { label: '已完成', value: '89', delta: '较昨日 +15', tone: 'green', icon: 'check' },
  { label: '逾期随访', value: '36', delta: '较昨日 +6', tone: 'red', icon: 'alert' },
  { label: '异常反馈', value: '18', delta: '较昨日 +4', tone: 'purple', icon: 'bell' },
  { label: '自动提醒中', value: '74', delta: '较昨日 +11', tone: 'cyan', icon: 'send' },
]))

function sparkPath(delta) {
  const down = /-\s*\d/.test(String(delta ?? '')) || /↓/.test(String(delta ?? ''))
  return down
    ? 'M2 12 C10 10 14 12 18 11 C26 10 30 16 34 15 C40 14 44 20 48 19 C55 18 58 22 68 23'
    : 'M2 20 C10 18 12 16 18 17 C25 18 28 10 34 12 C40 14 42 6 48 7 C55 8 57 17 68 12'
}

const filtered = computed(() => store.patients.filter(p => {
  if (!['followup','alert','done'].includes(p.stage) && followStatus.value === 'all') return ['followup','alert','done'].includes(p.stage)
  if (keyword.value && !`${p.name}${p.phone}${p.nodule}`.includes(keyword.value)) return false
  if (sourceFilter.value !== 'all' && p.source !== sourceFilter.value) return false
  if (noduleFilter.value !== 'all' && !p.noduleType.includes(noduleFilter.value)) return false
  if (riskFilter.value !== 'all' && p.risk !== riskFilter.value) return false
  if (followStatus.value !== 'all' && p.stage !== followStatus.value) return false
  if (ownerFilter.value !== 'all' && p.owner !== ownerFilter.value) return false
  return ['followup','alert','done'].includes(p.stage)
}))

const current = computed(() => store.patients.find(p => p.id === store.currentPatientId))

const followFlow = computed(() => {
  if (!current.value) return []
  const stage = current.value.stage
  const idx = stage === 'done' ? 4 : (stage === 'alert' ? 2 : 3)
  return [
    { label: '任务生成', sub: '自动/手动' },
    { label: '触达患者', sub: '企微/电话' },
    { label: '结果记录', sub: '问卷/回访' },
    { label: '复核确认', sub: '异常转人工' },
    { label: '闭环完成', sub: '归档' },
  ].map((n, i) => ({
    ...n,
    done: i < idx,
    cls: i < idx ? 'done' : (i === idx ? 'active' : '')
  }))
})

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
  sourceFilter.value = 'all'
  noduleFilter.value = 'all'
  riskFilter.value = 'all'
  channelFilter.value = 'all'
  followStatus.value = 'all'
  ownerFilter.value = 'all'
}
</script>

<style scoped>
.page{min-height:100%}
.page-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.page-title{font-size:20px;font-weight:950;color:#0f172a}
.crumb{color:#64748b;font-weight:700}
.kpi-row{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin-bottom:12px}
.kpi{position:relative;background:#fff;border:1px solid #e6edf7;border-radius:10px;padding:10px 12px;box-shadow:0 4px 12px rgba(15,23,42,.04);overflow:hidden}
.kpi-ico{width:28px;height:28px;border-radius:8px;border:1px solid #e6edf7;background:#f8fafc;color:#64748b;display:grid;place-items:center;margin-bottom:4px}
.kpi[data-tone="orange"] .kpi-ico{background:#fff7ed;border-color:#fed7aa;color:#f97316}
.kpi[data-tone="green"] .kpi-ico{background:#ecfdf5;border-color:#bbf7d0;color:#16a34a}
.kpi[data-tone="purple"] .kpi-ico{background:#f5f3ff;border-color:#ddd6fe;color:#8b5cf6}
.kpi[data-tone="cyan"] .kpi-ico{background:#eafcff;border-color:#c7f9ff;color:#0ea5b7}
.kpi[data-tone="red"] .kpi-ico{background:#fff1f2;border-color:#fecdd3;color:#dc2626}
.kpi-label{color:#64748b;font-weight:500;font-size:12px;line-height:1.3}
.kpi-value{font-size:26px;font-weight:700;color:#0f172a;margin-top:3px;line-height:1}
.kpi-delta{font-size:12px;color:#c4cdd6;margin-top:3px;font-weight:400}
.spark{position:absolute;right:8px;bottom:8px;width:44px;height:16px;opacity:.6}
.spark path{fill:none;stroke:#5b8ff9;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.kpi[data-tone="orange"] .spark path{stroke:#f97316}
.kpi[data-tone="green"] .spark path{stroke:#16a34a}
.kpi[data-tone="purple"] .spark path{stroke:#8b5cf6}
.kpi[data-tone="cyan"] .spark path{stroke:#0ea5b7}
.kpi[data-tone="red"] .spark path{stroke:#dc2626}

.card{background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 6px 18px rgba(15,23,42,.04);margin-bottom:12px}
.filters-card{padding:14px 16px}
.card-title{font-weight:900;color:#0f172a}
.card-head{height:46px;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:0 14px}
.head-actions{display:flex;gap:6px}
.filter-grid{display:grid;grid-template-columns:1.15fr 1fr 1fr 1fr 1fr 1fr 1fr auto;gap:12px 18px;align-items:end}
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
.plan-grid{display:grid;gap:8px}
.plan-row{display:grid;grid-template-columns:88px minmax(0,1fr);gap:8px;align-items:start}
.plan-row .k{color:#94a3b8;font-size:12px}
.plan-row .v{color:#0f172a;font-weight:700;line-height:1.7;font-size:13px}
.plan-select{height:34px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none;margin-right:8px}
.plan-select:disabled{background:#f5f7fa;color:#94a3b8}
.plan-link{margin-left:10px;color:#155eef;text-decoration:none;font-weight:800}
.plan-link:hover{text-decoration:underline}
.plan-items{margin-top:12px;border-top:1px dashed #e6edf7;padding-top:10px;display:grid;gap:10px;max-height:320px;overflow:auto}
.plan-item{display:grid;grid-template-columns:86px minmax(0,1fr);gap:10px;align-items:flex-start}
.plan-time{color:#64748b;font-weight:850;font-size:12px;white-space:nowrap}
.plan-sum{color:#0f172a;font-weight:750;line-height:1.7;font-size:13px}
.plan-remind{margin-top:6px;color:#64748b;line-height:1.7;font-size:12px}
.checklist{display:grid;grid-template-columns:1fr 1fr;gap:8px 10px}
.ck{display:flex;gap:8px;align-items:center;font-size:13px;color:#334155}
.ck input{accent-color:#155eef}
.timeline{display:grid;gap:0}
.event{display:grid;grid-template-columns:48px minmax(0,1fr);gap:9px;padding:8px 0;border-bottom:1px solid #edf2f7}
.event:last-child{border-bottom:0}
.event-time{color:#94a3b8;font-size:12px}
.event-text{line-height:1.6;font-size:13px}
.ai-box{background:#f8fbff;border:1px solid #dce8f8;border-radius:7px;padding:11px 12px;color:#253247;font-size:13px}
.ai-block{display:block}
.ai-sub{font-weight:950;color:#0f172a;margin-bottom:6px}
.ai-text{line-height:1.7;white-space:pre-wrap}
.ai-split{height:1px;background:#dce8f8;margin:10px 0}

.flow-line{display:grid;grid-template-columns:repeat(5,1fr);gap:4px;margin:4px 0 0;text-align:center;font-size:11px;color:#64748b}
.flow-dot{width:18px;height:18px;border-radius:50%;background:#cbd5e1;margin:0 auto 6px;display:grid;place-items:center;color:#fff;font-size:11px;font-weight:900}
.flow-node.done .flow-dot{background:#22c55e}
.flow-node.active .flow-dot{background:#155eef}
.flow-label{font-weight:850;color:#334155}

.action-bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.btn{border:1px solid #d9e2ef;border-radius:6px;background:#fff;color:#475569;padding:6px 10px;cursor:pointer}
.btn.danger{border-color:#fecdd3;color:#dc2626;background:#fff1f2}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:6px;padding:6px 10px;cursor:pointer;font-weight:750}
.ico-btn{width:34px;height:34px;border-radius:10px;border:1px solid #d9e2ef;background:#fff;color:#64748b;cursor:pointer}
.muted{color:#64748b}
</style>
