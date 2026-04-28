<template>
  <div class="page">
    <div class="head">
      <div class="title">工作台</div>
      <div class="crumb">首页 / <b>工作台</b></div>
    </div>

    <div class="kpi-row" aria-label="统计概览">
      <KpiCard
        v-for="k in kpiList"
        :key="k.label"
        :label="k.label"
        :value="k.value"
        :delta="k.delta"
        :tone="k.tone"
        :icon="k.icon"
      />
    </div>

    <div class="tri">
      <!-- 左：患者队列 -->
      <section class="card">
        <header class="card-head">
          <div class="card-title">患者队列</div>
          <button class="btn-lite" type="button">+ 新建档案</button>
        </header>
        <div class="card-body">
          <div class="filters">
            <label class="field">
              <span>姓名/手机号</span>
              <input v-model="keyword" placeholder="请输入姓名或手机号">
            </label>
            <label class="field">
              <span>结节类型</span>
              <select v-model="nodule">
                <option value="all">全部</option>
                <option value="肺部结节">肺部结节</option>
                <option value="甲状腺结节">甲状腺结节</option>
                <option value="乳腺结节">乳腺结节</option>
              </select>
            </label>
            <label class="field">
              <span>风险等级</span>
              <select v-model="risk">
                <option value="all">全部</option>
                <option value="高风险">高风险</option>
                <option value="中风险">中风险</option>
                <option value="低风险">低风险</option>
              </select>
            </label>
          </div>

          <div class="tabs">
            <button v-for="t in tabs" :key="t" type="button" class="tab" :class="{ active: stage === t }" @click="stage = t">
              {{ t }}
            </button>
          </div>

          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>患者</th>
                  <th>来源</th>
                  <th>结节类型</th>
                  <th>风险</th>
                  <th>状态</th>
                  <th>最近检查</th>
                  <th>下次随访</th>
                  <th>负责人</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in filtered"
                  :key="p.id"
                  :class="{ active: p.id === currentId }"
                  @click="currentId = p.id"
                >
                  <td>
                    <div class="pname">{{ p.name }}</div>
                    <div class="psub">{{ p.gender }} · {{ p.age }}岁 · {{ p.phone }}</div>
                  </td>
                  <td>{{ p.source }}</td>
                  <td><span class="tag blue">{{ p.nodule }}</span></td>
                  <td><span class="tag" :class="riskClass(p.risk)">{{ p.risk }}</span></td>
                  <td><span class="tag blue">{{ p.stage }}</span></td>
                  <td>{{ p.lastExam }}</td>
                  <td>{{ p.next }}</td>
                  <td>{{ p.owner }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 中：患者沟通 -->
      <section class="card">
        <header class="card-head">
          <div class="card-title">患者沟通</div>
          <div class="mini">
            <span class="pill" :class="wecom.sent ? 'b' : ''">已发送</span>
            <span class="pill" :class="wecom.read ? 'g' : ''">已读</span>
            <span class="pill" :class="wecom.replied ? 'o' : ''">已回复</span>
          </div>
        </header>
        <div class="card-body">
          <div class="conv-head">
            <div>
              <div class="conv-title">{{ current.name }} · {{ current.phone }}</div>
              <div class="muted">最近报告：{{ current.reportSummary }}</div>
            </div>
            <div class="conv-actions">
              <button class="btn-lite" type="button">发起电话随访</button>
              <button class="btn-lite" type="button">推送小程序</button>
            </div>
          </div>

          <div class="bubble-list">
            <div v-for="m in thread.messages" :key="m.at + m.text" class="bubble" :class="{ mine: m.from !== '患者' }">
              <div class="meta">
                <b>{{ m.from }}</b>
                <span class="muted">{{ m.at }}</span>
              </div>
              <div class="text">{{ m.text }}</div>
            </div>
          </div>

          <div class="composer">
            <input class="composer-input" placeholder="输入随访话术或快速回复…">
            <button class="primary" type="button">发送</button>
          </div>
        </div>
      </section>

      <!-- 右：AI工作区 -->
      <section class="card">
        <header class="card-head">
          <div class="card-title">AI工作区</div>
          <button class="ghost" type="button">刷新</button>
        </header>
        <div class="card-body">
          <div class="ai-box">
            <div class="ai-title">当前患者摘要</div>
            <div class="kv" v-for="r in ai.summary" :key="r.k">
              <span class="k">{{ r.k }}</span>
              <span class="v">{{ r.v }}</span>
            </div>
          </div>

          <div class="split"></div>

          <div class="draft">
            <div class="ai-title">{{ ai.draft.title }}</div>
            <ul class="ul">
              <li v-for="b in ai.draft.bullets" :key="b">{{ b }}</li>
            </ul>
          </div>

          <div class="split"></div>

          <div class="ai-actions">
            <button
              v-for="a in ai.actions"
              :key="a.label"
              type="button"
              :class="a.primary ? 'primary' : 'btn-lite'"
            >
              {{ a.label }}
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import KpiCard from '../components/KpiCard.vue'
import { kpis, patientQueue, messageThreads, aiWorkspace } from '../mocks/workbenchMock'

const keyword = ref('')
const risk = ref('all')
const nodule = ref('all')
const stage = ref('全部')
const tabs = ['全部', '待处理报告', '待医生复核', '待推送患者', '异常']

const kpiList = kpis.analytics

const currentId = ref(patientQueue[0]?.id)

const filtered = computed(() => {
  return patientQueue.filter((p) => {
    const byKeyword = !keyword.value || (p.name + p.phone + p.nodule).includes(keyword.value)
    const byRisk = risk.value === 'all' || p.risk === risk.value
    const byNodule = nodule.value === 'all' || p.nodule.includes(nodule.value)
    const byStage = stage.value === '全部' || stage.value === '全部' ? true : p.stage === stage.value
    return byKeyword && byRisk && byNodule && byStage
  })
})

const current = computed(() => patientQueue.find((p) => p.id === currentId.value) ?? patientQueue[0])
const thread = computed(() => messageThreads.find((t) => t.patientId === current.value.id) ?? messageThreads[0])
const wecom = computed(() => current.value.wecom)
const ai = aiWorkspace

function riskClass(r) {
  if (r === '高风险') return 'high'
  if (r === '中风险') return 'orange'
  return 'green'
}
</script>

<style scoped>
.page{display:grid;gap:12px}
.head{display:flex;align-items:flex-end;justify-content:space-between}
.title{font-size:20px;font-weight:950;color:#0f172a}
.crumb{color:#94a3b8;font-weight:850}

.kpi-row{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:12px}
.kpi{position:relative;background:#fff;border:1px solid #e6edf7;border-radius:14px;padding:14px 14px;box-shadow:0 6px 18px rgba(15,23,42,.04);overflow:hidden}
.kpi-label{color:#526175;font-weight:850;font-size:12px}
.kpi-value{font-size:22px;font-weight:950;color:#0f172a;margin-top:8px}
.kpi-delta{font-size:12px;color:#94a3b8;margin-top:8px;font-weight:800}
.spark{position:absolute;right:12px;bottom:12px;width:66px;height:24px}
.spark path{fill:none;stroke:#5b8ff9;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

.tri{display:grid;grid-template-columns:minmax(420px,1.2fr) minmax(360px,1fr) minmax(360px,1fr);gap:12px;min-height:calc(100vh - 56px - 14px - 18px - 104px - 36px)}
.card{background:#fff;border:1px solid #e6edf7;border-radius:14px;box-shadow:0 6px 18px rgba(15,23,42,.04);overflow:hidden;min-height:0;display:flex;flex-direction:column}
.card-head{height:46px;display:flex;align-items:center;justify-content:space-between;padding:0 14px;border-bottom:1px solid #eef2f7;gap:10px}
.card-title{font-weight:950;color:#0f172a}
.card-body{padding:12px 14px;min-height:0;display:flex;flex-direction:column;gap:10px}
.btn-lite{height:34px;border-radius:12px;border:1px solid #d9e2ef;background:#fff;color:#155eef;font-weight:900;padding:0 12px}
.primary{height:34px;border-radius:12px;border:1px solid #155eef;background:#155eef;color:#fff;font-weight:950;padding:0 12px}
.ghost{border:0;background:transparent;color:#155eef;font-weight:950}
.muted{color:#64748b;font-weight:750}

.filters{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:10px}
.field span{display:block;color:#64748b;font-weight:800;font-size:12px;margin-bottom:6px}
.field input,.field select{height:34px;border:1px solid #d9e2ef;border-radius:12px;padding:0 10px;outline:none;background:#fff}
.tabs{display:flex;gap:8px;flex-wrap:wrap}
.tab{height:32px;border-radius:999px;border:1px solid #e6edf7;background:#fff;color:#526175;font-weight:900;padding:0 12px}
.tab.active{border-color:#155eef;background:#eef5ff;color:#155eef}

.table-wrap{flex:1;min-height:0;overflow:auto;border:1px solid #eef2f7;border-radius:12px}
.table{width:100%;border-collapse:collapse;min-width:920px}
.table th{position:sticky;top:0;background:#f8fafc;color:#64748b;text-align:left;font-size:12px;padding:10px 10px;border-bottom:1px solid #e5edf7;white-space:nowrap}
.table td{padding:10px 10px;border-bottom:1px solid #edf2f7;white-space:nowrap}
.table tbody tr:hover{background:#f8fbff}
.table tbody tr.active{background:#eef5ff}
.pname{font-weight:950;color:#0f172a}
.psub{font-size:12px;color:#64748b;margin-top:2px}
.tag{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900;line-height:1.4}
.tag.blue{background:#eef5ff;color:#155eef}
.tag.high{background:#fff1f2;color:#dc2626}
.tag.orange{background:#fff7ed;color:#c2410c}
.tag.green{background:#ecfff3;color:#14843b}

.mini{display:flex;gap:6px}
.pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900;background:#f1f5f9;color:#64748b}
.pill.b{background:#eef5ff;color:#155eef}
.pill.g{background:#ecfff3;color:#14843b}
.pill.o{background:#fff7ed;color:#c2410c}

.conv-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.conv-title{font-weight:950;color:#0f172a}
.conv-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.bubble-list{flex:1;min-height:0;overflow:auto;display:grid;gap:10px;padding:10px 0}
.bubble{border:1px solid #eef2f7;border-radius:14px;padding:10px 12px;background:#fff}
.bubble.mine{background:#f8fbff;border-color:#dbeafe}
.meta{display:flex;justify-content:space-between;gap:10px;align-items:center}
.text{margin-top:6px;line-height:1.65;color:#334155}
.composer{display:flex;gap:10px;align-items:center}
.composer-input{flex:1;height:36px;border-radius:12px;border:1px solid #d9e2ef;padding:0 12px;outline:none}

.ai-box{border:1px solid #dbeafe;background:#f8fbff;border-radius:14px;padding:12px 12px}
.ai-title{font-weight:950;color:#0f172a}
.kv{display:flex;justify-content:space-between;gap:10px;margin-top:10px}
.kv .k{color:#64748b;font-weight:850}
.kv .v{color:#0f172a;font-weight:950;text-align:right}
.split{height:1px;background:#eef2f7}
.draft .ul{margin:10px 0 0 16px;color:#334155;line-height:1.7}
.ai-actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}
</style>

