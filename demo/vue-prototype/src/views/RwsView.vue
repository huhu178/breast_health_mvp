<template>
  <div class="rws-page">
    <header class="rws-head">
      <div>
        <div class="rws-title">真实世界研究工作台</div>
        <div class="rws-sub">研究治理 · 可解释审核 · 质量追踪 · 数据导出合规</div>
      </div>
      <div class="head-actions">
        <button class="btn" type="button">研究设置</button>
        <button class="btn" type="button">新建研究</button>
        <button class="primary" type="button">脱敏导出</button>
      </div>
    </header>

    <section class="flow-card">
      <div v-for="(step, idx) in flowSteps" :key="step" class="flow-step">
        <span class="flow-ico">{{ idx + 1 }}</span>
        <b>{{ step }}</b>
      </div>
    </section>

    <section class="rws-kpis">
      <div v-for="item in kpis" :key="item.label" class="kpi-card" :data-tone="item.tone">
        <div class="kpi-ico">{{ item.icon }}</div>
        <div>
          <div class="kpi-label">{{ item.label }}</div>
          <div class="kpi-value">{{ item.value }}</div>
          <div class="kpi-sub">{{ item.sub }}</div>
        </div>
      </div>
    </section>

    <main class="rws-main">
      <section class="card project-panel">
        <div class="card-head">
          <div>
            <div class="card-title">研究项目导航</div>
            <div class="muted">当前在研 3 项 · 1 项待启动</div>
          </div>
          <button class="icon-btn" type="button">设</button>
        </div>
        <div class="project-list">
          <button
            v-for="project in projects"
            :key="project.name"
            type="button"
            class="project-item"
            :class="{ active: project.name === activeProject.name }"
            @click="activeProjectName = project.name"
          >
            <div class="project-top">
              <b>{{ project.name }}</b>
              <span class="state-pill" :data-state="project.state">{{ project.state }}</span>
            </div>
            <div class="project-desc">{{ project.desc }}</div>
            <div class="project-kpis">
              <div><span>入组数</span><b>{{ project.n }}</b></div>
              <div><span>随访中</span><b>{{ project.fu }}</b></div>
              <div><span>结局数</span><b>{{ project.outcome }}</b></div>
            </div>
            <div class="project-foot">
              <span>待确认 {{ project.confirm }}</span>
              <span>脱落 {{ project.drop }}</span>
              <span>缺失 {{ project.missing }}</span>
              <span class="progress">进度 {{ project.progress }}%</span>
            </div>
            <div class="bar"><i :style="{ width: `${project.progress}%` }"></i></div>
          </button>
        </div>
      </section>

      <section class="card review-panel">
        <div class="card-head review-head">
          <div>
            <div class="card-title">入组筛选与审核台</div>
            <div class="muted">规则驱动 + AI建议 + 人工确认</div>
          </div>
          <div class="filter-row">
            <select><option>结节类型：全部</option><option>肺部结节</option><option>甲状腺结节</option><option>乳腺结节</option></select>
            <select><option>风险等级：全部</option><option>高风险</option><option>中风险</option><option>低风险</option></select>
            <select><option>随访状态：全部</option><option>随访中</option><option>待人工确认</option><option>需补充证据</option></select>
            <input value="2026/04/01 ~ 2026/04/29" readonly />
            <button class="primary" type="button">筛选</button>
            <button class="btn" type="button">重置</button>
          </div>
        </div>

        <div class="table-wrap">
          <table class="review-table">
            <thead>
              <tr>
                <th>候选患者</th>
                <th>命中规则</th>
                <th>AI建议</th>
                <th>证据来源</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in candidates"
                :key="row.name"
                :class="{ active: row.name === activeCandidate.name }"
                @click="activeCandidateName = row.name"
              >
                <td><b>{{ row.name }}</b><span>{{ row.meta }}</span></td>
                <td>{{ row.rule }}</td>
                <td><span class="ai-tag" :data-tone="row.tone">{{ row.ai }}</span></td>
                <td>{{ row.evidence }}</td>
                <td><span class="status" :data-status="row.status">{{ row.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <section class="candidate-detail">
          <div class="detail-title">候选患者解释链路（当前：{{ activeCandidate.name }}）</div>
          <div class="detail-grid">
            <div>
              <div class="detail-label">基本信息</div>
              <p>{{ activeCandidate.basic }}</p>
            </div>
            <div>
              <div class="detail-label">命中规则</div>
              <p>{{ activeCandidate.rule }}</p>
            </div>
            <div>
              <div class="detail-label">AI建议原因</div>
              <p>{{ activeCandidate.reason }}</p>
            </div>
            <div>
              <div class="detail-label">证据来源</div>
              <div class="evidence-tags">
                <span v-for="e in activeCandidate.sources" :key="e">{{ e }}</span>
              </div>
            </div>
          </div>
          <div class="explain-row">
            <span>解释链路</span>
            <b>{{ activeCandidate.path }}</b>
          </div>
          <div class="detail-actions">
            <button class="btn blue" type="button">查看原始证据</button>
            <button class="primary" type="button">确认入组</button>
            <button class="btn" type="button">暂缓</button>
            <button class="danger" type="button">排除并填写原因</button>
          </div>
        </section>
      </section>
    </main>

    <section class="bottom-grid">
      <section class="card quality-card">
        <div class="card-head compact"><div class="card-title">研究质量与结局追踪</div></div>
        <div class="quality-grid">
          <div><span>AI与人工一致性</span><b>91.6%</b><em class="up">较上周 +1.2%</em></div>
          <div><span>需复审样本</span><b>38</b><em>较昨日 +5</em></div>
          <div><span>脱落样本</span><b>12</b><em class="down">较昨日 +2</em></div>
          <div><span>结局事件</span><b>27</b><em class="up">较昨日 +3</em></div>
        </div>
      </section>

      <section class="card trend-card">
        <div class="card-head compact"><div class="card-title">一致性趋势（近8周）</div></div>
        <div class="trend">
          <div v-for="p in trend" :key="p.date" class="trend-point">
            <span :style="{ height: `${p.value - 70}%` }"></span>
            <b>{{ p.value }}%</b>
            <em>{{ p.date }}</em>
          </div>
        </div>
      </section>

      <section class="card donut-card">
        <div class="card-head compact"><div class="card-title">脱落原因（近30天）</div></div>
        <div class="donut-wrap">
          <div class="donut"><b>12</b><span>总数</span></div>
          <div class="legend">
            <span><i style="background:#3b82f6"></i>失访 5</span>
            <span><i style="background:#22c55e"></i>资料缺失 3</span>
            <span><i style="background:#f59e0b"></i>拒绝继续 2</span>
            <span><i style="background:#a855f7"></i>转外院 2</span>
          </div>
        </div>
      </section>

      <section class="card outcome-card">
        <div class="card-head compact"><div class="card-title">结局事件分类（近90天）</div></div>
        <div class="bar-list">
          <div v-for="b in outcomes" :key="b.name">
            <span>{{ b.name }}</span>
            <i><em :style="{ width: `${b.rate}%`, background: b.color }"></em></i>
            <b>{{ b.count }}</b>
          </div>
        </div>
      </section>

      <section class="card export-card">
        <div class="card-head compact"><div class="card-title">脱敏导出准备度</div></div>
        <div class="export-list">
          <div><span>字段脱敏规则已启用</span><b>通过</b></div>
          <div><span>敏感信息校验通过</span><b>通过</b></div>
          <div><span>导出日志</span><b>2 条</b></div>
        </div>
        <button class="primary full" type="button">检查并生成数据包</button>
      </section>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const flowSteps = ['研究项目管理', '入组筛选', 'AI建议', '人工确认', '一致性审核', '结局追踪', '脱敏导出']

const kpis = [
  { label: '当前在研数', value: '3', sub: '较昨日 +0', tone: 'blue', icon: '研' },
  { label: '待人工确认', value: '18', sub: '需优先处理 6', tone: 'orange', icon: '审' },
  { label: 'AI与人工一致性', value: '91.6%', sub: '较上周 +1.2%', tone: 'green', icon: '合' },
  { label: '今日新增候选', value: '26', sub: '较昨日 +3', tone: 'purple', icon: '新' },
  { label: '脱落预警', value: '12', sub: '较昨日 +2', tone: 'red', icon: '警' },
  { label: '待导出数据包', value: '2', sub: '待检查后导出', tone: 'blue', icon: '数' },
]

const projects = [
  { name: '肺结节高风险随访队列', state: '进行中', desc: '纳入标准：纳入 >=6mm 磨玻璃结节；年龄 35-75 岁；随访周期：3个月', n: 812, fu: 604, outcome: 76, confirm: 8, drop: 3, missing: 5, progress: 76 },
  { name: '甲状腺结节 TI-RADS 3 随访', state: '进行中', desc: '纳入标准：TI-RADS 3 类结节；年龄 18-75 岁；随访周期：6-12个月', n: 702, fu: 518, outcome: 54, confirm: 6, drop: 4, missing: 3, progress: 71 },
  { name: '乳腺结节 BI-RADS 3 随访', state: '筹备中', desc: '纳入标准：BI-RADS 3 类；年龄 18-70 岁；随访周期：6个月', n: 0, fu: 0, outcome: 0, confirm: 0, drop: 0, missing: 0, progress: 0 },
  { name: '肺结节低风险随访队列', state: '待启动', desc: '纳入标准：实性结节 <6mm；年龄 35-75 岁；随访周期：12个月', n: 0, fu: 0, outcome: 0, confirm: 0, drop: 0, missing: 0, progress: 0 },
]

const activeProjectName = ref(projects[0].name)
const activeProject = computed(() => projects.find((p) => p.name === activeProjectName.value) || projects[0])

const candidates = [
  { name: '张*国', meta: '男 56岁 · 门诊', rule: '肺部结节 + 高风险 + 首次随访', ai: '建议入组', tone: 'green', evidence: '影像报告、门诊病历', status: '待人工确认', basic: '男 56岁；门诊号：0002345678；就诊日期：2026-04-28', reason: '影像提示 8mm 磨玻璃结节，符合高风险纳入标准，建议入组并启动随访。', sources: ['门诊', '影像', '检验', '病理'], path: '门诊诊断（肺部结节） → 影像提示 8mm 磨玻璃结节 → 满足高风险规则 → 推荐纳入' },
  { name: '李*婷', meta: '女 48岁 · 体检中心', rule: '甲状腺结节 TI-RADS 3 类', ai: '建议入组', tone: 'green', evidence: '超声报告、既往检查', status: '需补充证据', basic: '女 48岁；体检中心；检查日期：2026-04-27', reason: '甲状腺结节 TI-RADS 3 类，缺少既往超声对比，需补充证据后确认。', sources: ['超声报告', '既往检查'], path: '体检报告 → TI-RADS 3 类 → 缺少既往对比 → 需补充证据' },
  { name: '王*军', meta: '男 62岁 · 门诊', rule: '肺部结节 + 中风险', ai: '暂缓入组', tone: 'blue', evidence: '影像报告、随访记录', status: '暂缓', basic: '男 62岁；门诊；最近随访：2026-04-26', reason: '当前风险等级为中风险，随访周期未达研究纳入窗口，建议暂缓。', sources: ['影像报告', '随访记录'], path: '影像提示结节 → 中风险 → 未到入组窗口 → 暂缓' },
  { name: '刘*芬', meta: '女 45岁 · 门诊', rule: '甲状腺结节 TI-RADS 3 类', ai: '建议入组', tone: 'green', evidence: '超声报告、门诊病历', status: '待人工确认', basic: '女 45岁；门诊；就诊日期：2026-04-25', reason: '符合 TI-RADS 3 队列纳入条件，且资料完整。', sources: ['超声报告', '门诊病历'], path: '门诊诊断 → 超声 TI-RADS 3 → 资料完整 → 推荐纳入' },
]

const activeCandidateName = ref(candidates[0].name)
const activeCandidate = computed(() => candidates.find((c) => c.name === activeCandidateName.value) || candidates[0])

const trend = [
  { date: '03-07', value: 89.1 },
  { date: '03-21', value: 88.0 },
  { date: '04-04', value: 89.7 },
  { date: '04-18', value: 90.4 },
  { date: '04-29', value: 91.6 },
]

const outcomes = [
  { name: '复查完成', count: '14 (51.9%)', rate: 92, color: '#2563eb' },
  { name: '异常转诊', count: '6 (22.2%)', rate: 58, color: '#06b6d4' },
  { name: '手术/病理结果', count: '4 (14.8%)', rate: 42, color: '#f59e0b' },
  { name: '持续观察', count: '3 (11.1%)', rate: 32, color: '#a855f7' },
]
</script>

<style scoped>
.rws-page{min-height:100%;display:flex;flex-direction:column;gap:10px;background:#fff;overflow:visible}
.rws-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-shrink:0}
.rws-title{font-size:22px;font-weight:950;color:#0f172a;line-height:1.2}
.rws-sub,.muted{color:#64748b;font-weight:750;font-size:12px}
.head-actions{display:flex;gap:10px;align-items:center}
.btn,.primary,.danger{height:36px;border-radius:10px;padding:0 14px;font-weight:950;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;white-space:nowrap}
.btn{border:1px solid #d9e2ef;background:#fff;color:#475569}
.btn.blue{background:#eef5ff;border-color:#cfe0ff;color:#155eef}
.primary{border:1px solid #155eef;background:#155eef;color:#fff}
.danger{border:1px solid #fecaca;background:#fff;color:#ef4444}
.full{width:100%;margin-top:10px}
.flow-card{height:58px;border:1px solid #e6edf7;border-radius:12px;background:#fff;display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px;padding:10px 14px;flex-shrink:0}
.flow-step{display:flex;align-items:center;justify-content:center;gap:8px;color:#334155;min-width:0}
.flow-step:not(:last-child)::after{content:'>'; color:#94a3b8;margin-left:auto}
.flow-ico{width:28px;height:28px;border-radius:9px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-size:12px;font-weight:950;flex-shrink:0}
.flow-step b{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rws-kpis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;flex-shrink:0}
.kpi-card{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:12px;display:flex;gap:12px;align-items:center;min-width:0}
.kpi-ico{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-weight:950;flex-shrink:0}
.kpi-card[data-tone="blue"] .kpi-ico{background:#eef5ff;color:#155eef}
.kpi-card[data-tone="orange"] .kpi-ico{background:#fff7ed;color:#f97316}
.kpi-card[data-tone="green"] .kpi-ico{background:#ecfdf5;color:#16a34a}
.kpi-card[data-tone="purple"] .kpi-ico{background:#f5f3ff;color:#8b5cf6}
.kpi-card[data-tone="red"] .kpi-ico{background:#fff1f2;color:#ef4444}
.kpi-label{font-size:12px;color:#64748b;font-weight:850}
.kpi-value{font-size:26px;font-weight:950;color:#0f172a;line-height:1.1;margin-top:2px}
.kpi-sub{font-size:12px;color:#64748b;font-weight:750}
.rws-main{display:grid;grid-template-columns:470px minmax(0,1fr);gap:10px;min-height:520px}
.card{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden;min-width:0}
.card-head{min-height:44px;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 12px}
.card-head.compact{min-height:38px}
.card-title{font-weight:950;color:#0f172a}
.icon-btn{width:30px;height:30px;border-radius:10px;border:1px solid #d9e2ef;background:#fff;color:#64748b;font-weight:950}
.project-panel{display:flex;flex-direction:column;min-height:520px}
.project-list{padding:10px;display:grid;gap:8px;overflow:auto;min-height:0;max-height:462px}
.project-item{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:10px;text-align:left;cursor:pointer}
.project-item.active{border-color:#155eef;background:#f8fbff;box-shadow:inset 0 0 0 1px rgba(21,94,239,.14)}
.project-top{display:flex;align-items:center;justify-content:space-between;gap:8px}
.project-top b{color:#0f172a;font-size:13px}
.state-pill{border-radius:999px;padding:3px 8px;font-size:12px;font-weight:950;background:#eef5ff;color:#155eef;border:1px solid #cfe0ff;white-space:nowrap}
.state-pill[data-state="筹备中"]{background:#ecfdf5;color:#16a34a;border-color:#bbf7d0}
.state-pill[data-state="待启动"]{background:#f1f5f9;color:#64748b;border-color:#e2e8f0}
.project-desc{margin-top:6px;color:#475569;font-size:12px;line-height:1.55}
.project-kpis{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:8px}
.project-kpis div{border:1px solid #eef2f7;background:#fff;border-radius:8px;padding:7px 8px;display:flex;justify-content:space-between;align-items:center}
.project-kpis span,.project-foot{font-size:12px;color:#64748b;font-weight:850}
.project-kpis b{color:#0f172a}
.project-foot{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:8px}
.project-foot span{border:1px solid #fed7aa;background:#fff7ed;color:#c2410c;border-radius:7px;padding:2px 7px}
.project-foot .progress{margin-left:auto;background:transparent;border:none;color:#64748b}
.bar{height:5px;background:#e2e8f0;border-radius:999px;overflow:hidden;margin-top:8px}
.bar i{display:block;height:100%;background:#155eef;border-radius:999px}
.review-panel{display:flex;flex-direction:column;min-height:520px}
.review-head{align-items:flex-start;flex-wrap:wrap}
.filter-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.filter-row select,.filter-row input{height:32px;border:1px solid #d9e2ef;border-radius:8px;background:#fff;padding:0 10px;color:#334155;font-weight:850;min-width:116px}
.filter-row input{width:190px}
.table-wrap{margin:10px 12px 0;border:1px solid #e6edf7;border-radius:10px;overflow:auto;flex-shrink:0;max-height:190px}
.review-table{width:100%;border-collapse:collapse;min-width:840px;font-size:12px}
.review-table th{background:#f8fafc;color:#64748b;text-align:left;padding:9px 10px;font-weight:950;white-space:nowrap}
.review-table td{border-top:1px solid #eef2f7;padding:8px 10px;white-space:nowrap;color:#334155}
.review-table tr{cursor:pointer}
.review-table tr.active td{background:#eef5ff}
.review-table td b{display:block;color:#0f172a}
.review-table td span{display:block;color:#64748b;margin-top:2px}
.ai-tag{display:inline-flex!important;border-radius:7px;padding:2px 7px;font-weight:950}
.ai-tag[data-tone="green"]{background:#ecfdf5;color:#16a34a}
.ai-tag[data-tone="blue"]{background:#eef5ff;color:#155eef}
.status{display:inline-flex!important;border-radius:7px;padding:2px 7px;font-weight:950;background:#fff7ed;color:#c2410c}
.status[data-status="需补充证据"]{background:#fff1f2;color:#ef4444}
.status[data-status="暂缓"]{background:#eef5ff;color:#155eef}
.candidate-detail{border:1px solid #e6edf7;border-radius:12px;margin:10px 12px 12px;padding:12px;background:#fff;min-height:230px}
.detail-title{font-weight:950;color:#0f172a;margin-bottom:10px}
.detail-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;border-bottom:1px solid #eef2f7;padding-bottom:10px}
.detail-label{color:#64748b;font-size:12px;font-weight:950;margin-bottom:5px}
.detail-grid p{margin:0;color:#334155;font-size:12px;line-height:1.55}
.evidence-tags{display:flex;gap:6px;flex-wrap:wrap}
.evidence-tags span{border:1px solid #e6edf7;background:#f8fafc;border-radius:8px;padding:4px 10px;color:#334155;font-size:12px;font-weight:850}
.explain-row{display:flex;gap:10px;align-items:center;padding:10px 0;color:#64748b;font-size:12px}
.explain-row b{color:#334155}
.detail-actions{display:flex;gap:10px;justify-content:flex-end;flex-wrap:wrap}
.bottom-grid{display:grid;grid-template-columns:1.1fr 1fr 1fr 1.2fr .9fr;gap:10px;min-height:142px;padding-bottom:12px}
.quality-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:10px}
.quality-grid div{border:1px solid #eef2f7;border-radius:10px;padding:8px;background:#fff}
.quality-grid span{display:block;color:#64748b;font-size:12px;font-weight:850}
.quality-grid b{display:block;color:#0f172a;font-size:20px;margin-top:2px}
.quality-grid em{font-style:normal;color:#64748b;font-size:12px}
.quality-grid .up{color:#16a34a}.quality-grid .down{color:#ef4444}
.trend{height:104px;display:flex;align-items:end;gap:14px;padding:10px 16px}
.trend-point{flex:1;display:grid;gap:4px;justify-items:center;font-size:11px;color:#64748b}
.trend-point span{width:100%;min-height:18px;border-radius:8px 8px 0 0;background:linear-gradient(180deg,#2563eb,#93c5fd)}
.trend-point b{color:#155eef}.trend-point em{font-style:normal}
.donut-wrap{display:flex;align-items:center;gap:16px;padding:12px}
.donut{width:86px;height:86px;border-radius:50%;background:conic-gradient(#3b82f6 0 42%,#22c55e 42% 67%,#f59e0b 67% 84%,#a855f7 84%);display:grid;place-items:center;color:#0f172a;position:relative}
.donut::after{content:'';position:absolute;inset:18px;border-radius:50%;background:#fff}
.donut b,.donut span{position:relative;z-index:1}.donut b{font-size:22px}.donut span{font-size:11px;color:#64748b}
.legend{display:grid;gap:7px;font-size:12px;color:#334155;font-weight:850}
.legend i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
.bar-list{padding:10px 12px;display:grid;gap:9px}
.bar-list div{display:grid;grid-template-columns:86px minmax(0,1fr) 78px;gap:8px;align-items:center;font-size:12px;color:#334155}
.bar-list i{height:8px;background:#eef2f7;border-radius:999px;overflow:hidden}.bar-list em{display:block;height:100%;border-radius:999px}
.export-list{padding:10px 12px;display:grid;gap:8px}
.export-list div{display:flex;justify-content:space-between;gap:8px;font-size:12px;color:#334155}.export-list b{color:#16a34a}
@media (max-width:1500px){
  .rws-main{grid-template-columns:430px minmax(0,1fr)}
  .bottom-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
  .export-card{grid-column:auto}
}
</style>
