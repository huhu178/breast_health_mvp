<template>
  <div class="scenario-page" :class="{ 'checkup-page': scenario.key === 'checkup' }" :style="themeVars">
    <template v-if="scenario.key === '__legacy_checkup'">
      <header class="scenario-head checkup-head">
        <div>
          <div class="scenario-title">筛查中心</div>
          <div class="scenario-sub">体检异常处置工作台 | 批量处理、AI辅助决策、人工确认、后续处置闭环</div>
        </div>
        <div class="head-actions">
          <button class="btn" type="button">导入体检批次</button>
          <button class="primary" type="button">批量生成AI建议</button>
        </div>
      </header>

      <section class="checkup-flow card">
        <div v-for="(step, idx) in checkupFlow" :key="step.title" class="flow-step">
          <div class="flow-no">{{ idx + 1 }}</div>
          <div>
            <b>{{ step.title }}</b>
            <span>{{ step.sub }}</span>
          </div>
        </div>
      </section>

      <section class="kpi-row checkup-kpis">
        <article v-for="k in checkupKpis" :key="k.label" class="kpi">
          <div class="kpi-icon" :data-tone="k.tone">{{ k.icon }}</div>
          <div>
            <div class="kpi-label">{{ k.label }}</div>
            <div class="kpi-value">{{ k.value }}</div>
            <div class="kpi-sub">{{ k.sub }}</div>
          </div>
        </article>
      </section>

      <main class="checkup-grid">
        <section class="card checkup-table-card">
          <div class="card-head table-head">
            <div>
              <div class="card-title">异常结果处理队列</div>
              <div class="muted">按批次、异常类型、风险等级与处置状态进行高效处理</div>
            </div>
          </div>
          <div class="checkup-filters">
            <label>体检批次<select><option>全部</option><option>春季单位体检批次A-03</option><option>春季单位体检批次A-02</option></select></label>
            <label>异常类型<select><option>全部</option><option>肺结节</option><option>甲状腺结节</option><option>乳腺结节</option></select></label>
            <label>风险等级<select><option>全部</option><option>高风险</option><option>中风险</option><option>低风险</option></select></label>
            <label>推荐动作<select><option>全部</option><option>建议转诊</option><option>建议复查</option><option>建议随访</option></select></label>
            <label>当前状态<select><option>全部</option><option>待人工确认</option><option>已确认待发送</option><option>已加入随访</option></select></label>
            <div class="table-search">搜索患者姓名/手机号</div>
            <button class="btn small" type="button">筛选</button>
            <button class="btn small" type="button">重置</button>
            <button class="primary small" type="button">批量确认</button>
          </div>
          <div class="screening-table">
            <div class="screening-head">
              <span></span><span>患者信息</span><span>批次/套餐</span><span>异常类型</span><span>风险等级</span><span>AI推荐动作</span><span>当前状态</span><span>异常结果摘要</span><span>操作</span>
            </div>
            <button v-for="(row, idx) in checkupRows" :key="row.name" type="button" class="screening-row" :class="{ active: idx === 0 }">
              <span class="check-cell"><span class="check-mark" :data-on="idx === 0"></span></span>
              <span class="patient-cell"><b>{{ row.name }}</b><em>{{ row.meta }}</em></span>
              <span>{{ row.batch }}</span>
              <span><i class="type-pill">{{ row.type }}</i></span>
              <span><i class="risk-pill" :data-tone="row.tone">{{ row.risk }}</i></span>
              <span><i class="action-pill" :data-tone="row.tone">{{ row.action }}</i></span>
              <span><i class="state-chip">{{ row.state }}</i></span>
              <span class="summary-cell">{{ row.summary }}</span>
              <span class="table-link">查看详情</span>
            </button>
          </div>
          <div class="table-pager">
            <span>共 256 条</span>
            <select><option>10条/页</option></select>
            <button type="button">‹</button><b>1</b><button type="button">2</button><button type="button">3</button><button type="button">4</button><button type="button">5</button><span>...</span><button type="button">26</button><button type="button">›</button>
            <span>前往</span><input value="1"><span>页</span>
          </div>
        </section>

        <aside class="card decision-card">
          <div class="card-head compact">
            <div class="card-title">处置决策面板</div>
            <button class="link-btn" type="button">收起</button>
          </div>
          <div class="decision-body">
            <section v-for="block in decisionBlocks" :key="block.title" class="decision-block">
              <h3>{{ block.title }}</h3>
              <p v-for="line in block.lines" :key="line">{{ line }}</p>
            </section>
            <div class="decision-result">
              <b>操作结果说明</b>
              <p>确认转诊后，将生成转诊建议单并进入「待发送报告」；创建复查后，将同步至「复查预约队列」；加入随访计划后，将进入随访管理流程。</p>
            </div>
            <div class="decision-actions">
              <button class="primary" type="button">确认转诊</button>
              <button class="btn" type="button">创建复查预约</button>
              <button class="btn" type="button">加入随访计划</button>
              <button class="btn" type="button">发送解读报告</button>
              <button class="btn" type="button">驳回AI建议</button>
              <button class="btn" type="button">重新判定</button>
            </div>
          </div>
        </aside>
      </main>

      <section class="checkup-bottom">
        <section class="card progress-card">
          <div class="card-head compact"><div class="card-title">批次处理进度</div></div>
          <div class="progress-body">
            <div class="stack-bar"><span style="width:34%"></span><span style="width:28%"></span><span style="width:16%"></span><span style="width:22%"></span></div>
            <div class="progress-metrics">
              <div><i></i><span>已导入</span><b>128</b><em>100%</em></div>
              <div><i></i><span>已识别</span><b>96</b><em>75%</em></div>
              <div><i></i><span>待确认</span><b>26</b><em>20%</em></div>
              <div><i></i><span>已处置</span><b>64</b><em>50%</em></div>
            </div>
          </div>
        </section>
        <section class="card bars-card">
          <div class="card-head compact"><div class="card-title">转诊建议分布 <span>TOP科室</span></div></div>
          <div class="dept-bars">
            <div v-for="bar in deptBars" :key="bar.label"><span>{{ bar.label }}</span><em><i :style="{ width: bar.width }"></i></em><b>{{ bar.value }}</b></div>
          </div>
        </section>
        <section class="card trend-card">
          <div class="card-head compact"><div class="card-title">复查预约趋势 <span>近7天</span></div></div>
          <div class="trend-chart">
            <svg viewBox="0 0 360 130" preserveAspectRatio="none">
              <polyline points="12,92 62,70 112,62 162,48 212,78 272,56 342,44" fill="none" stroke="var(--workspace-primary)" stroke-width="3" />
              <g v-for="p in trendPoints" :key="p.x">
                <circle :cx="p.x" :cy="p.y" r="4" fill="var(--workspace-primary)" />
                <text :x="p.x" :y="p.y - 10" text-anchor="middle">{{ p.v }}</text>
              </g>
            </svg>
          </div>
        </section>
        <section class="card donut-card">
          <div class="card-head compact"><div class="card-title">异常类型分布 <span>今日</span></div></div>
          <div class="donut-body">
            <div class="donut"><b>112</b><span>总计</span></div>
            <div class="legend">
              <p><i></i>肺结节 <b>46 (41.1%)</b></p>
              <p><i></i>甲状腺结节 <b>28 (25.0%)</b></p>
              <p><i></i>乳腺结节 <b>18 (16.1%)</b></p>
              <p><i></i>肝囊肿 <b>12 (10.7%)</b></p>
            </div>
          </div>
        </section>
      </section>
    </template>

    <template v-else>
      <header class="scenario-head">
        <div>
          <div class="scenario-title">{{ workspace.title }}</div>
          <div class="scenario-sub">{{ workspace.subtitle }}</div>
        </div>
        <div class="head-actions">
          <button class="btn" type="button">{{ workspace.secondaryAction }}</button>
          <button class="primary" type="button">{{ workspace.primaryAction }}</button>
        </div>
      </header>

      <section class="kpi-row">
        <article v-for="k in workspace.kpis" :key="k.label" class="kpi" :class="{ clickable: k.action }" @click="goAction(k.action)">
          <div class="kpi-icon">{{ k.icon }}</div>
          <div>
            <div class="kpi-label">{{ k.label }}</div>
            <div class="kpi-value">{{ k.value }}</div>
            <div class="kpi-sub">{{ k.sub }}</div>
          </div>
        </article>
      </section>

      <main class="workspace-grid">
        <section class="card main-list">
          <div class="card-head">
            <div>
              <div class="card-title">{{ workspace.queueTitle }}</div>
              <div class="muted">{{ workspace.queueSub }}</div>
            </div>
            <div class="filters">
              <select><option>{{ workspace.filterA }}</option></select>
              <select><option>{{ workspace.filterB }}</option></select>
              <button class="primary small" type="button">筛选</button>
            </div>
          </div>
          <div class="rows">
            <button v-for="row in workspace.rows" :key="row.name" type="button" class="queue-row" @click="goAction(row.action || 'patient-detail')">
              <div class="row-main">
                <b>{{ row.name }}</b>
                <span>{{ row.meta }}</span>
              </div>
              <div class="row-desc">{{ row.desc }}</div>
              <span class="row-status" :data-tone="row.tone">{{ row.status }}</span>
            </button>
          </div>
        </section>

        <aside class="card detail-card">
          <div class="card-head">
            <div class="card-title">{{ workspace.detailTitle }}</div>
            <span class="state-pill">{{ workspace.detailState }}</span>
          </div>
          <div class="detail-body">
            <div v-for="item in workspace.detailItems" :key="item.k" class="detail-row">
              <span>{{ item.k }}</span>
              <b>{{ item.v }}</b>
            </div>
            <div class="explain-box">
              <div class="explain-title">{{ workspace.explainTitle }}</div>
              <p>{{ workspace.explain }}</p>
            </div>
            <div class="action-grid">
              <button v-for="a in workspace.actions" :key="actionLabel(a)" class="btn" type="button" @click="goAction(a)">{{ actionLabel(a) }}</button>
            </div>
          </div>
        </aside>
      </main>

      <section v-if="isPharmacy" class="pharmacy-insights">
        <section class="card funnel-card">
          <div class="card-head compact">
            <div>
              <div class="card-title">健康服务转化漏斗</div>
              <div class="muted">咨询到建档、报告、随访和完成的闭环转化</div>
            </div>
          </div>
          <div class="funnel-body">
            <button
              v-for="step in pharmacyFunnel"
              :key="step.label"
              type="button"
              class="funnel-step"
              :style="{ '--w': step.width }"
              @click="goAction(step.action)"
            >
              <span>{{ step.label }}</span>
              <b>{{ step.value }}</b>
              <em>{{ step.rate }}</em>
            </button>
          </div>
        </section>

        <section class="card source-card">
          <div class="card-head compact">
            <div>
              <div class="card-title">服务来源占比</div>
              <div class="muted">到店咨询、购药记录、慢病服务和线上问诊</div>
            </div>
          </div>
          <div class="source-body">
            <button v-for="item in pharmacySources" :key="item.label" type="button" class="source-row" @click="goAction(item.action)">
              <span>{{ item.label }}</span>
              <i><em :style="{ width: item.width }"></em></i>
              <b>{{ item.value }}</b>
            </button>
          </div>
        </section>
      </section>

      <section class="bottom-grid">
        <section v-for="panel in workspace.panels" :key="panel.title" class="card panel">
          <div class="card-head compact"><div class="card-title">{{ panel.title }}</div></div>
          <div class="panel-body">
            <button v-for="it in panel.items" :key="it.label" type="button" class="panel-line" @click="goAction(it.action || panel.action || it.label)">
              <span>{{ it.label }}</span>
              <b>{{ it.value }}</b>
            </button>
          </div>
        </section>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { getStoredScenario } from '../config/scenarios'

const router = useRouter()
const scenario = computed(() => getStoredScenario())
const isPharmacy = computed(() => scenario.value.key === 'pharmacy')

const themeVars = computed(() => ({
  '--workspace-primary': scenario.value.theme?.primary || '#155eef',
  '--workspace-soft': scenario.value.theme?.soft || '#eef5ff',
  '--workspace-bg': scenario.value.theme?.bg || '#f3f6fb',
  '--workspace-accent': scenario.value.theme?.accent || '#16a34a',
}))

const workspaceMap = {
  checkup: {
    title: '筛查质控',
    subtitle: '体检批次质量 · 阳性检出 · 报告解读效率 · 随访完成率',
    primaryAction: '查看质控明细',
    secondaryAction: '导入体检批次',
    queueTitle: '筛查批次质控',
    queueSub: '按体检批次、套餐、结节类型和随访状态查看筛查质量',
    filterA: '体检批次：全部',
    filterB: '风险等级：全部',
    detailTitle: '批次质控详情',
    detailState: '处理中',
    explainTitle: '质控口径',
    explain: '系统基于体检报告结构化字段、结节类型、风险分层、报告解读状态和随访触达状态，统计筛查质量与后续管理完成情况。',
    kpis: [
      { icon: '批', label: '今日体检批次', value: '12', sub: '已导入 9 批' },
      { icon: '阳', label: '结节检出', value: '86', sub: '高风险 14' },
      { icon: '解', label: '待解读报告', value: '31', sub: '较昨日 +5' },
      { icon: '访', label: '随访完成率', value: '78.6%', sub: '近30天' },
    ],
    rows: [
      { name: '春季单位体检A-03', meta: '单位团检 · 286人', desc: '结节检出 46 人，高风险 8 人，31 份报告待解读', status: '处理中', tone: 'o' },
      { name: '肺结节专项筛查', meta: '专项套餐 · 128人', desc: '肺结节检出率 18.7%，高风险患者已进入患者管理队列', status: '待随访', tone: 'b' },
      { name: '女性健康专项', meta: '个人体检 · 96人', desc: '乳腺/甲状腺结节患者已生成报告解读和随访任务', status: '已完成', tone: 'g' },
    ],
    detailItems: [
      { k: '体检批次', v: '春季单位体检A-03' },
      { k: '筛查人数', v: '286人' },
      { k: '结节检出', v: '46人' },
      { k: '报告解读', v: '31份待处理' },
    ],
    actions: ['查看患者队列', '查看报告解读', '查看随访完成率', '导出质控表'],
    panels: [
      { title: '批次处理进度', items: [{ label: '已解析报告', value: '286' }, { label: '待解读报告', value: '31' }, { label: '已发送解读', value: '142' }] },
      { title: '筛查质量', items: [{ label: '结节检出率', value: '16.1%' }, { label: '高风险占比', value: '2.8%' }, { label: '报告结构化率', value: '92.4%' }] },
      { title: '随访触达', items: [{ label: '待下发任务', value: '42' }, { label: '已触达患者', value: '118' }, { label: '完成打卡', value: '76' }] },
    ],
  },
  pharmacy: {
    title: '药事服务分析',
    subtitle: '到店咨询 · 慢病服务 · 用药提醒 · 随访触达 · 服务转化',
    primaryAction: '查看转化明细',
    secondaryAction: '导入服务记录',
    queueTitle: '重点跟进队列',
    queueSub: '按服务来源、药师任务和随访状态查看需要继续跟进的患者',
    filterA: '服务类型：全部',
    filterB: '慢病标签：全部',
    detailTitle: '服务质量详情',
    detailState: '待跟进',
    explainTitle: '统计口径',
    explain: '系统结合患者来源、购药记录、健康咨询、随访任务和触达结果，统计药店健康服务的完成情况和后续跟进质量。',
    kpis: [
      { icon: '咨', label: '到店咨询', value: '214', sub: '转建档 36', action: 'queue' },
      { icon: '药', label: '药师待跟进', value: '28', sub: '高优先级 6', action: 'follow' },
      { icon: '视', label: '名师视频', value: '156', sub: '已观看 102', action: 'followup-plan' },
      { icon: '成', label: '服务完成率', value: '81.2%', sub: '近30天', action: 'follow' },
    ],
    rows: [
      { name: '赵*强', meta: '男 59岁 · 慢病服务', desc: '近期购药记录已同步，健康报告已生成，等待药师回访记录', status: '待跟进', tone: 'r', action: 'detail' },
      { name: '陈*霞', meta: '女 45岁 · 到店咨询', desc: '咨询结节报告与保健品使用，已建档并等待报告解读提醒', status: '待回复', tone: 'o', action: 'review' },
      { name: '刘*峰', meta: '男 71岁 · 购药记录', desc: '慢病药物即将用尽，可下发用药提醒和每日名师视频', status: '可触达', tone: 'b', action: 'followup-plan' },
    ],
    detailItems: [
      { k: '服务类型', v: '慢病服务' },
      { k: '近期用药', v: '降压药、降糖药' },
      { k: '服务状态', v: '待跟进' },
      { k: '建议动作', v: '药师回访' },
    ],
    actions: [
      { label: '查看患者详情', action: 'detail' },
      { label: '下发名师视频', action: 'followup-plan' },
      { label: '创建随访任务', action: 'followup-plan' },
      { label: '记录药师意见', action: 'follow' }
    ],
    panels: [
      { title: '服务来源分析', action: 'queue', items: [{ label: '到店咨询建档', value: '36' }, { label: '购药记录关联', value: '58' }, { label: '线上问诊转入', value: '22' }] },
      { title: '药师工作量', action: 'follow', items: [{ label: '待回复咨询', value: '9' }, { label: '已完成回访', value: '46' }, { label: '待跟进任务', value: '18' }] },
      { title: '健康服务转化', action: 'review', items: [{ label: '咨询转建档', value: '16.8%' }, { label: '建档转报告', value: '72.4%' }, { label: '报告转随访', value: '61.5%' }] },
      { title: '每日名师视频', action: 'followup-plan', items: [{ label: '今日待推送', value: '156' }, { label: '已观看', value: '102' }, { label: '未观看提醒', value: '31' }] },
      { title: '用药与健康提醒', action: 'followup-plan', items: [{ label: '用药提醒', value: '34' }, { label: '复购提醒', value: '17' }, { label: '报告解读提醒', value: '28' }] },
      { title: '重点患者跟进', action: 'follow', items: [{ label: '长期未响应', value: '12' }, { label: '报告未生成', value: '42', action: 'review' }, { label: '随访未完成', value: '18', action: 'follow' }] },
    ],
  },
  community: {
    title: '家医随访',
    subtitle: '签约管理 · 慢病随访 · 入户记录 · 复查提醒 · 结果回收',
    primaryAction: '创建随访任务',
    secondaryAction: '导入社区档案',
    queueTitle: '家庭医生随访队列',
    queueSub: '按签约状态、慢病标签和网格归属查看家医随访质量',
    filterA: '签约状态：全部',
    filterB: '社区网格：全部',
    detailTitle: '家医随访详情',
    detailState: '待随访',
    explainTitle: '随访建议依据',
    explain: '系统结合签约档案、慢病管理记录、社区筛查来源和近期复查状态，统计家医随访任务、触达结果和复查资料回收情况。',
    kpis: [
      { icon: '签', label: '签约患者', value: '1,246', sub: '重点 186' },
      { icon: '访', label: '今日随访', value: '72', sub: '电话 48' },
      { icon: '慢', label: '慢病共管', value: '318', sub: '双病 64' },
      { icon: '收', label: '资料回收', value: '37', sub: '待补充 8' },
    ],
    rows: [
      { name: '黄*芳', meta: '女 44岁 · 南城三网格', desc: '签约患者，乳腺结节随访到期，建议电话随访并提醒复查', status: '今日随访', tone: 'b' },
      { name: '林*海', meta: '男 58岁 · 第一家医团队', desc: '肺部结节高风险，近期复查资料未回收，需家医继续跟进', status: '待跟进', tone: 'r' },
      { name: '何*秀', meta: '女 51岁 · 老年人管理', desc: '甲状腺结节低风险，适合纳入季度随访', status: '随访中', tone: 'g' },
    ],
    detailItems: [
      { k: '签约状态', v: '已签约' },
      { k: '家医团队', v: '第一家庭医生团队' },
      { k: '社区网格', v: '南城三网格' },
      { k: '建议动作', v: '电话随访 + 资料回收' },
    ],
    actions: ['查看患者详情', '创建电话随访', '安排入户', '回收复查结果'],
    panels: [
      { title: '签约服务', items: [{ label: '已签约', value: '1,246' }, { label: '重点人群', value: '186' }, { label: '待签约', value: '42' }] },
      { title: '慢病共管', items: [{ label: '高血压', value: '156' }, { label: '糖尿病', value: '98' }, { label: '双病共管', value: '64' }] },
      { title: '资料回收', items: [{ label: '待回收', value: '15' }, { label: '已补充', value: '23' }, { label: '结果回收', value: '37' }] },
    ],
  },
}

const workspace = computed(() => workspaceMap[scenario.value.key] || workspaceMap.checkup)

const pharmacyFunnel = [
  { label: '到店/线上咨询', value: '214', rate: '100%', width: '100%', action: 'queue' },
  { label: '完成建档', value: '36', rate: '16.8%', width: '74%', action: 'record' },
  { label: '生成健康报告', value: '26', rate: '72.4%', width: '58%', action: 'review' },
  { label: '下发名师视频', value: '19', rate: '73.1%', width: '46%', action: 'followup-plan' },
  { label: '完成观看/打卡', value: '13', rate: '68.4%', width: '34%', action: 'follow' },
]

const pharmacySources = [
  { label: '到店咨询', value: '36', width: '72%', action: 'queue' },
  { label: '购药记录', value: '58', width: '88%', action: 'queue' },
  { label: '慢病服务', value: '42', width: '64%', action: 'queue' },
  { label: '线上问诊', value: '22', width: '38%', action: 'queue' },
]

function actionLabel(action) {
  return typeof action === 'string' ? action : action?.label || ''
}

function actionKey(action) {
  return typeof action === 'string' ? action : action?.action || ''
}

function goAction(action) {
  const key = actionKey(action)
  const routeMap = {
    queue: { path: '/patient', query: { tab: 'queue' } },
    detail: { path: '/patient', query: { tab: 'detail' } },
    'patient-detail': { path: '/patient', query: { tab: 'detail' } },
    record: { path: '/patient', query: { tab: 'record' } },
    review: { path: '/patient', query: { tab: 'review' } },
    'followup-plan': { path: '/patient', query: { tab: 'followup-plan' } },
    follow: { path: '/patient', query: { tab: 'follow' } },
  }
  const target = routeMap[key]
  if (target) router.push(target)
}

const checkupFlow = [
  { title: '导入批次', sub: '导入体检数据' },
  { title: '异常识别', sub: '识别异常结果' },
  { title: 'AI建议', sub: '生成处置建议' },
  { title: '人工确认', sub: '医生确认决策' },
  { title: '转诊/复查/随访', sub: '完成后续处置闭环' },
]

const checkupKpis = [
  { icon: '待', label: '待确认建议', value: '26', sub: '较昨日 +3', tone: 'blue' },
  { icon: '转', label: '建议转诊', value: '18', sub: '高风险 6', tone: 'red' },
  { icon: '发', label: '待发送报告', value: '31', sub: '较昨日 +5', tone: 'green' },
  { icon: '复', label: '待创建复查', value: '14', sub: '今日新增 6', tone: 'purple' },
]

const checkupRows = [
  { name: '孙*', meta: '女 48岁 | 138****5678', batch: '春季单位体检批次A-03\n肺结节专项', type: '肺结节', risk: '高风险', tone: 'r', action: '建议转诊', state: '待人工确认', summary: '肺部磨玻璃结节 7mm，建议门诊进一步评估' },
  { name: '李*华', meta: '男 55岁 | 139****4321', batch: '春季单位体检批次A-03\n肺结节专项', type: '肺结节', risk: '中风险', tone: 'o', action: '建议复查', state: '建议待确认', summary: '右肺上叶磨玻璃结节 5mm，建议定期复查' },
  { name: '王*', meta: '女 37岁 | 136****8890', batch: '春季单位体检批次A-02\n乳腺专项', type: '乳腺结节', risk: '低风险', tone: 'g', action: '建议随访', state: '已确认待发送', summary: '右乳BI-RADS 3 类，建议 6 个月随访' },
  { name: '赵*强', meta: '男 62岁 | 137****5577', batch: '春季单位体检批次A-02\n甲状腺专项', type: '甲状腺结节', risk: '中风险', tone: 'o', action: '建议复查', state: '已创建复查', summary: '甲状腺结节 TI-RADS 4A，建议 3 个月复查' },
  { name: '刘*', meta: '女 45岁 | 135****2211', batch: '春季单位体检批次A-01\n肝脏专项', type: '肝囊肿', risk: '低风险', tone: 'g', action: '建议随访', state: '已加入随访', summary: '肝囊肿约 12mm，建议 12 个月随访' },
]

const decisionBlocks = [
  {
    title: 'A. 基本信息',
    lines: ['患者姓名：孙*（女 48岁）　手机：138****5678', '体检套餐：肺结节专项　批次号：A-03-20260415', '异常指标：肺部磨玻璃结节 7mm（右肺上叶）', '推荐去向：呼吸科门诊　复查周期：建议门诊进一步评估'],
  },
  {
    title: 'B. 风险判断依据',
    lines: ['肺部磨玻璃结节 7mm', '既往影像对比未见明显缩小', '年龄 48 岁，吸烟史不详'],
  },
  {
    title: 'C. AI推荐逻辑',
    lines: ['根据结节大小（≥6mm）及磨玻璃性质，风险分层为中-高风险', '结合年龄、结节位置等因素，建议转诊至呼吸科门诊评估', '遵循《肺结节管理规范 v2025》分层管理策略'],
  },
  {
    title: 'D. 规则/指南来源',
    lines: ['肺结节管理规范 v2025，体检异常分层规则库 v3.2', '院内随访SOP v2.1'],
  },
]

const deptBars = [
  { label: '呼吸科', value: 12, width: '86%' },
  { label: '甲乳外科', value: 6, width: '56%' },
  { label: '内分泌科', value: 4, width: '42%' },
  { label: '乳腺外科', value: 3, width: '34%' },
  { label: '胸外科', value: 2, width: '26%' },
]

const trendPoints = [
  { x: 12, y: 92, v: 18 },
  { x: 62, y: 70, v: 24 },
  { x: 112, y: 62, v: 27 },
  { x: 162, y: 48, v: 31 },
  { x: 212, y: 78, v: 22 },
  { x: 272, y: 56, v: 28 },
  { x: 342, y: 44, v: 31 },
]
</script>

<style scoped>
.scenario-page{min-height:100%;display:flex;flex-direction:column;gap:12px;background:linear-gradient(180deg,var(--workspace-bg),#fff 260px);padding-bottom:18px}
.checkup-page{gap:10px;background:#f6fbff}
.scenario-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.checkup-head{padding:2px 4px 0}
.scenario-title{font-size:22px;font-weight:950;color:#0f172a}
.scenario-sub,.muted{font-size:12px;color:#64748b;font-weight:750}
.head-actions,.filters,.action-grid{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.btn,.primary{height:34px;border-radius:10px;padding:0 13px;font-weight:950;border:1px solid #d9e2ef;background:#fff;color:#475569;cursor:pointer}
.primary{background:var(--workspace-primary);border-color:var(--workspace-primary);color:#fff}
.small{height:32px}
.checkup-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));padding:14px 18px;gap:20px;overflow:visible}
.flow-step{display:grid;grid-template-columns:38px minmax(0,1fr);align-items:center;gap:10px;position:relative}
.flow-step:not(:last-child)::after{content:"";position:absolute;left:calc(100% + 2px);top:50%;width:28px;height:1px;background:#9ab4d6}
.flow-no{width:34px;height:34px;border-radius:999px;background:linear-gradient(135deg,#67c7dd,#2f82db);color:#fff;display:grid;place-items:center;font-weight:950}
.flow-step b{display:block;font-size:14px;color:#172033}.flow-step span{font-size:12px;color:#64748b;font-weight:750}
.kpi-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.kpi{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:14px;display:flex;gap:12px;align-items:center}
.kpi.clickable{cursor:pointer}
.kpi.clickable:hover{border-color:var(--workspace-primary);background:var(--workspace-soft)}
.kpi-icon{width:42px;height:42px;border-radius:12px;background:var(--workspace-soft);color:var(--workspace-primary);display:grid;place-items:center;font-weight:950}
.checkup-kpis .kpi{min-height:104px}.checkup-kpis .kpi:first-child{border-left:4px solid var(--workspace-primary)}
.kpi-icon[data-tone="blue"]{background:linear-gradient(135deg,#93c5fd,#3b82f6);color:#fff}
.kpi-icon[data-tone="red"]{background:linear-gradient(135deg,#fb923c,#ef4444);color:#fff}
.kpi-icon[data-tone="green"]{background:linear-gradient(135deg,#34d399,#10b981);color:#fff}
.kpi-icon[data-tone="purple"]{background:linear-gradient(135deg,#a78bfa,#7c3aed);color:#fff}
.kpi-label{font-size:12px;color:#64748b;font-weight:850}.kpi-value{font-size:26px;font-weight:950;color:#0f172a;line-height:1.1}.kpi-sub{font-size:12px;color:#64748b}
.workspace-grid{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:12px;min-height:420px}
.checkup-grid{display:grid;grid-template-columns:minmax(0,1fr) 410px;gap:12px;align-items:start}
.card{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden;min-width:0}
.card-head{min-height:48px;border-bottom:1px solid #eef2f7;padding:10px 12px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.card-head.compact{min-height:40px}.card-title{font-weight:950;color:#0f172a}
.filters select{height:32px;border:1px solid #d9e2ef;border-radius:9px;padding:0 10px;color:#334155;background:#fff;font-weight:850}
.checkup-filters{display:grid;grid-template-columns:88px 88px 88px 96px 96px minmax(130px,1fr) auto auto auto;gap:8px;padding:10px 12px;border-bottom:1px solid #eef2f7;align-items:end}
.checkup-filters label{display:grid;gap:4px;font-size:11px;color:#64748b;font-weight:850}.checkup-filters select{height:30px;min-width:0;border:1px solid #d9e2ef;border-radius:7px;background:#fff;color:#334155;font-weight:850;padding:0 8px}
.table-search{height:30px;border:1px solid #d9e2ef;border-radius:7px;color:#94a3b8;font-size:12px;font-weight:750;display:flex;align-items:center;padding:0 10px}
.screening-table{overflow:auto}
.screening-head,.screening-row{display:grid;grid-template-columns:34px 132px 138px 86px 76px 100px 108px minmax(210px,1fr) 74px;gap:8px;align-items:center;min-width:1010px;padding:0 12px}
.screening-head{height:38px;background:#f8fafc;border-bottom:1px solid #e6edf7;color:#64748b;font-size:12px;font-weight:950}
.screening-row{width:100%;height:48px;border:0;border-bottom:1px solid #eef2f7;background:#fff;text-align:left;color:#334155;font-size:12px;cursor:pointer}
.screening-row.active{background:#eff6ff;box-shadow:inset 3px 0 0 var(--workspace-primary)}
.check-cell{display:flex;align-items:center}.check-mark{width:14px;height:14px;border:1px solid #cbd5e1;border-radius:3px;background:#fff}.check-mark[data-on="true"]{background:var(--workspace-primary);border-color:var(--workspace-primary);position:relative}.check-mark[data-on="true"]::after{content:"";position:absolute;left:3px;top:2px;width:6px;height:4px;border-left:2px solid #fff;border-bottom:2px solid #fff;transform:rotate(-45deg)}
.patient-cell{display:grid;gap:2px}.patient-cell b{font-size:13px;color:#0f172a}.patient-cell em{font-style:normal;color:#64748b;font-size:11px}.screening-row span{white-space:pre-line}.summary-cell{line-height:1.4;color:#475569}
.type-pill,.risk-pill,.action-pill,.state-chip{font-style:normal;border-radius:999px;padding:4px 9px;font-size:12px;font-weight:950;white-space:nowrap;background:#f1f5f9;color:#475569}
.risk-pill[data-tone="r"],.action-pill[data-tone="r"]{background:#fff1f2;color:#ef4444}.risk-pill[data-tone="o"],.action-pill[data-tone="o"]{background:#fff7ed;color:#f97316}.risk-pill[data-tone="g"],.action-pill[data-tone="g"]{background:#ecfdf5;color:#16a34a}
.state-chip{background:#eaf3ff;color:#2563eb}.table-link{color:#155eef;font-weight:950;text-align:right}.table-pager{height:48px;display:flex;align-items:center;justify-content:center;gap:14px;border-top:1px solid #eef2f7;color:#334155;font-size:12px}.table-pager button,.table-pager input,.table-pager select{height:30px;border:1px solid #d9e2ef;border-radius:7px;background:#fff;color:#334155;text-align:center}.table-pager b{width:30px;height:30px;border-radius:7px;background:#eef5ff;color:#155eef;display:grid;place-items:center}.table-pager input{width:42px}
.decision-card{align-self:stretch}.decision-body{padding:10px 14px 12px;display:grid;gap:9px}.link-btn{border:0;background:transparent;color:#155eef;font-weight:900;cursor:pointer}.decision-block{border-bottom:1px solid #eef2f7;padding-bottom:8px}.decision-block h3{margin:0 0 6px;font-size:13px;color:#172033}.decision-block p{margin:3px 0;color:#334155;font-size:12px;line-height:1.55}.decision-result{border:1px solid #dbeafe;background:#f8fbff;border-radius:10px;padding:10px 12px}.decision-result b{font-size:12px;color:#0f172a}.decision-result p{margin:5px 0 0;color:#475569;font-size:12px;line-height:1.55}.decision-actions{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}.decision-actions .primary,.decision-actions .btn{height:36px;padding:0 8px}
.rows{padding:10px;display:grid;gap:8px;max-height:420px;overflow:auto}
.queue-row{display:grid;grid-template-columns:170px minmax(0,1fr) 86px;gap:12px;align-items:center;border:1px solid #eef2f7;background:#fff;border-radius:10px;padding:12px;text-align:left}
.queue-row:hover{border-color:var(--workspace-primary);background:var(--workspace-soft)}
.row-main{display:grid;gap:4px}.row-main b{color:#0f172a}.row-main span,.row-desc{font-size:12px;color:#64748b;line-height:1.5}
.row-status{border-radius:999px;padding:4px 10px;text-align:center;font-size:12px;font-weight:950;background:#eef5ff;color:#155eef}
.row-status[data-tone="r"]{background:#fff1f2;color:#ef4444}.row-status[data-tone="o"]{background:#fff7ed;color:#f97316}.row-status[data-tone="g"]{background:#ecfdf5;color:#16a34a}.row-status[data-tone="b"]{background:#eef5ff;color:#155eef}
.detail-body{padding:12px;display:grid;gap:10px}
.state-pill{border-radius:999px;padding:4px 10px;background:var(--workspace-soft);color:var(--workspace-primary);font-weight:950;font-size:12px}
.detail-row{display:flex;justify-content:space-between;gap:12px;border:1px solid #eef2f7;border-radius:10px;padding:9px 10px;font-size:12px}.detail-row span{color:#64748b}.detail-row b{color:#0f172a;text-align:right}
.explain-box{border:1px solid color-mix(in srgb,var(--workspace-primary) 24%,#e6edf7);background:var(--workspace-soft);border-radius:12px;padding:10px 12px}
.explain-title{font-weight:950;color:#0f172a;margin-bottom:6px}.explain-box p{margin:0;color:#334155;font-size:12px;line-height:1.7}
.action-grid{display:grid;grid-template-columns:1fr 1fr}
.pharmacy-insights{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(320px,.85fr);gap:12px}
.funnel-body{padding:14px;display:grid;gap:10px}
.funnel-step{width:100%;border:0;background:transparent;display:grid;grid-template-columns:minmax(0,1fr) 56px 56px;gap:10px;align-items:center;text-align:left;cursor:pointer;color:#334155}
.funnel-step span{position:relative;min-height:34px;border-radius:10px;background:linear-gradient(90deg,var(--workspace-primary),color-mix(in srgb,var(--workspace-primary) 30%,#fff));color:#fff;font-weight:950;display:flex;align-items:center;padding:0 12px;width:var(--w)}
.funnel-step b{font-size:18px;color:#0f172a;text-align:right}
.funnel-step em{font-style:normal;color:#64748b;font-size:12px;text-align:right}
.funnel-step:hover span{filter:brightness(.94)}
.source-body{padding:14px;display:grid;gap:12px}
.source-row{display:grid;grid-template-columns:72px minmax(0,1fr) 42px;gap:10px;align-items:center;border:0;background:transparent;padding:0;text-align:left;cursor:pointer;color:#334155;font-size:12px}
.source-row i{height:8px;background:#eef2f7;border-radius:999px;overflow:hidden}
.source-row em{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,#fb923c,var(--workspace-primary))}
.source-row b{text-align:right;color:#0f172a}
.source-row:hover span{color:var(--workspace-primary);font-weight:950}
.bottom-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.checkup-bottom{display:grid;grid-template-columns:1.1fr 1fr 1.25fr 1fr;gap:12px}
.panel-body{padding:12px;display:grid;gap:8px}
.panel-line{display:flex;justify-content:space-between;border:1px solid #eef2f7;border-radius:10px;padding:10px;font-size:12px;color:#64748b;background:#fff;cursor:pointer;text-align:left}.panel-line b{color:#0f172a}.panel-line:hover{border-color:var(--workspace-primary);background:var(--workspace-soft)}
.progress-body{padding:14px}.stack-bar{height:18px;border-radius:5px;overflow:hidden;display:flex;background:#eef2f7}.stack-bar span:nth-child(1){background:#3b82f6}.stack-bar span:nth-child(2){background:#61c6e6}.stack-bar span:nth-child(3){background:#f6b84a}.stack-bar span:nth-child(4){background:#39b98b}.progress-metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px}.progress-metrics div{display:grid;gap:3px;text-align:center;color:#64748b;font-size:12px}.progress-metrics i{width:7px;height:7px;border-radius:50%;background:#3b82f6;margin:auto}.progress-metrics div:nth-child(2) i{background:#61c6e6}.progress-metrics div:nth-child(3) i{background:#f6b84a}.progress-metrics div:nth-child(4) i{background:#39b98b}.progress-metrics b{font-size:18px;color:#0f172a}.progress-metrics em{font-style:normal;font-size:11px}
.card-title span{font-size:11px;color:#64748b;font-weight:800}.dept-bars{padding:14px;display:grid;gap:11px}.dept-bars div{display:grid;grid-template-columns:62px minmax(0,1fr) 24px;gap:8px;align-items:center;font-size:12px;color:#334155}.dept-bars em{height:7px;background:#eef2f7;border-radius:999px;overflow:hidden}.dept-bars i{display:block;height:100%;background:linear-gradient(90deg,#93c5fd,#3b82f6);border-radius:999px}.dept-bars b{color:#334155}
.trend-chart{height:150px;padding:12px}.trend-chart svg{width:100%;height:100%}.trend-chart text{font-size:11px;fill:#334155;font-weight:800}
.donut-body{padding:14px;display:grid;grid-template-columns:116px minmax(0,1fr);gap:12px;align-items:center}.donut{width:96px;height:96px;border-radius:50%;background:conic-gradient(#3b82f6 0 41%,#14b8a6 41% 66%,#f59e0b 66% 82%,#94a3b8 82% 100%);position:relative;display:grid;place-items:center;margin:auto}.donut::after{content:"";position:absolute;width:56px;height:56px;border-radius:50%;background:#fff}.donut b,.donut span{position:relative;z-index:1}.donut b{font-size:22px;color:#0f172a}.donut span{font-size:11px;color:#64748b;margin-top:28px;margin-left:-28px}.legend{display:grid;gap:8px}.legend p{margin:0;font-size:12px;color:#334155;display:flex;align-items:center;justify-content:space-between;gap:8px}.legend i{width:9px;height:9px;border-radius:50%;background:#3b82f6;display:inline-block;margin-right:5px}.legend p:nth-child(2) i{background:#14b8a6}.legend p:nth-child(3) i{background:#f59e0b}.legend p:nth-child(4) i{background:#94a3b8}
@media(max-width:1500px){.checkup-grid{grid-template-columns:minmax(0,1fr) 380px}.checkup-filters{grid-template-columns:repeat(5,86px) minmax(120px,1fr) auto auto auto}.decision-actions{grid-template-columns:1fr 1fr}.checkup-bottom{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:1400px){.workspace-grid,.checkup-grid,.pharmacy-insights{grid-template-columns:1fr}.detail-card{min-height:auto}.kpi-row,.bottom-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.decision-card{order:2}.checkup-flow{grid-template-columns:repeat(3,minmax(0,1fr))}.flow-step::after{display:none}}
</style>
