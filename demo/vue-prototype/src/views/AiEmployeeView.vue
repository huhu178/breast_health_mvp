<template>
  <div class="ai-page">
    <header class="ai-head">
      <div>
        <div class="eyebrow">{{ moduleEyebrow }}</div>
        <h1>{{ page.title }}</h1>
        <p>{{ page.desc }}</p>
      </div>
      <div class="head-actions">
        <label class="search-box">
          <span>搜索</span>
          <input v-model="search" type="search" :placeholder="page.search" />
        </label>
        <button class="primary" type="button">{{ page.action }}</button>
      </div>
    </header>

    <section v-if="section === 'overview'" class="dashboard-workbench">
      <div class="kpi-grid">
        <div v-for="item in growthBoardKpis" :key="item.label" class="kpi-card" :data-tone="item.tone">
          <span>{{ item.label }}</span><b>{{ item.value }}</b><em>{{ item.sub }}</em>
        </div>
      </div>
      <section class="card"><div class="card-head"><div><h2>报告前转化漏斗</h2><span>曝光到交接健康管理师</span></div></div><div class="funnel-card dashboard-funnel"><div v-for="(step, idx) in funnel" :key="step.label" class="funnel-step"><i>{{ idx + 1 }}</i><span>{{ step.label }}</span><b>{{ step.value }}</b></div></div></section>
      <section class="dashboard-grid">
        <article class="card"><div class="card-head"><div><h2>今日重点线索</h2><span>优先处理高意向、待交接和待人工跟进</span></div></div><div class="card-body"><LeadRows :rows="filteredLeads.slice(0, 4)" /></div></article>
        <article class="card"><div class="card-head"><div><h2>转化趋势</h2><span>近 7 日渠道表现</span></div></div><div class="trend-bars"><div v-for="bar in trendBars" :key="bar.day"><span>{{ bar.day }}</span><i><em :style="{ width: `${bar.rate}%` }"></em></i><b>{{ bar.value }}</b></div></div></article>
      </section>
      <section class="dashboard-grid">
        <article class="card"><div class="card-head"><div><h2>渠道转化排行</h2><span>按留资到交接转化率排序</span></div></div><div class="table-wrap"><table><thead><tr><th>渠道</th><th>线索</th><th>加企微</th><th>交接</th><th>转化率</th></tr></thead><tbody><tr v-for="row in dashboardRows" :key="row.channel"><td><b>{{ row.channel }}</b></td><td>{{ row.leads }}</td><td>{{ row.wecom }}</td><td>{{ row.handoff }}</td><td><span class="status-tag" data-s="follow">{{ row.rate }}</span></td></tr></tbody></table></div></article>
        <article class="card"><div class="card-head"><div><h2>{{ isHospital ? '运营边界' : 'AI边界' }}</h2><span>{{ isHospital ? '医生IP只做科普与承接，不替代诊疗' : '超级员工只做报告前增长转化' }}</span></div></div><div class="card-body"><div class="boundary-box"><b>{{ isHospital ? '职责止于科普承接' : '职责止于交接' }}</b><p>{{ boundaryText }}</p></div></div></article>
      </section>
      <section v-if="isHospital" class="dashboard-grid">
        <article class="card">
          <div class="card-head"><div><h2>医生IP获客入口</h2><span>把原引流获客入口合并到数据看板</span></div></div>
          <div class="table-wrap"><table><thead><tr><th>入口名称</th><th>平台</th><th>入口类型</th><th>转化目标</th><th>今日线索</th><th>负责人</th></tr></thead><tbody><tr v-for="entry in channels" :key="entry.name"><td><b>{{ entry.name }}</b><span>{{ entry.desc }}</span></td><td>{{ entry.platform }}</td><td>{{ entry.type }}</td><td>{{ entry.goal }}</td><td><b>{{ entry.leads }}</b></td><td>{{ entry.owner }}</td></tr></tbody></table></div>
        </article>
        <article class="card">
          <div class="card-head"><div><h2>线索转化队列</h2><span>把原线索转化合并到数据看板</span></div></div>
          <div class="card-body"><LeadRows :rows="filteredLeads" /></div>
        </article>
      </section>
    </section>

    <section v-else-if="section === 'super-employee'" class="embedded-workbench">
      <iframe
        class="embedded-frame"
        title="结节营销智脑超级员工"
        src="/nodule-super-employee/index.html"
      ></iframe>
    </section>

    <section v-else-if="section === 'channels'" class="channels-workbench">
      <section class="card channel-main">
        <div class="channel-stats">
          <div v-for="item in channelStats" :key="item.label" class="channel-stat">
            <div class="stat-icon" :data-tone="item.tone">{{ item.icon }}</div>
            <div>
              <span>{{ item.label }}</span>
              <b>{{ item.value }}</b>
              <em>{{ item.sub }}</em>
            </div>
          </div>
        </div>

        <div class="filter-bar">
          <div class="filter-title">入口筛选</div>
          <div class="filter-row">
            <div class="filter-item">
              <label>平台</label>
              <select><option>全部</option><option>小红书</option><option>视频号</option><option>公众号</option></select>
            </div>
            <div class="filter-item">
              <label>入口类型</label>
              <select><option>全部</option><option>落地页</option><option>企微活码</option><option>小程序表单</option></select>
            </div>
            <div class="filter-item">
              <label>负责人</label>
              <select><option>全部</option><option>赵婷</option><option>刘洋</option><option>王珊</option></select>
            </div>
            <div class="filter-actions">
              <button class="ghost" type="button">重置</button>
              <button class="primary" type="button">查询</button>
              <button class="primary" type="button">+ 新建入口</button>
            </div>
          </div>
        </div>

        <div class="q-table-head-row">
          <span class="muted">获客入口 共 {{ channels.length }} 条</span>
        </div>
        <div class="table-wrap channel-table-wrap">
          <table>
            <thead>
              <tr>
                <th style="width:190px">入口名称</th>
                <th style="width:92px">平台</th>
                <th style="width:96px">入口类型</th>
                <th style="width:132px">转化目标</th>
                <th style="width:78px">今日线索</th>
                <th style="width:78px">负责人</th>
                <th style="width:92px">状态</th>
                <th style="width:96px">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in channels" :key="entry.name" class="q-row" :class="{ active: entry.name === activeChannel.name }" @click="activeChannelName = entry.name">
                <td><b>{{ entry.name }}</b><span>{{ entry.desc }}</span></td>
                <td><span class="nodule-tag">{{ entry.platform }}</span></td>
                <td>{{ entry.type }}</td>
                <td>{{ entry.goal }}</td>
                <td><b>{{ entry.leads }}</b></td>
                <td>{{ entry.owner }}</td>
                <td><span class="status-tag" :data-s="entry.statusKey">{{ entry.status }}</span></td>
                <td><button class="tbl-act" type="button">查看</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <aside class="channel-side card">
        <div class="card-head compact">
          <div>
            <h2>入口详情</h2>
            <span>{{ activeChannel.platform }} · {{ activeChannel.type }}</span>
          </div>
          <span class="status-tag" :data-s="activeChannel.statusKey">{{ activeChannel.status }}</span>
        </div>
        <div class="channel-preview">
          <div class="qr-box">
            <div class="qr-grid" aria-hidden="true">
              <i v-for="n in 25" :key="n" :data-on="qrDots.includes(n)"></i>
            </div>
            <span>{{ activeChannel.type }}</span>
          </div>
          <div class="preview-copy">
            <b>{{ activeChannel.name }}</b>
            <span>{{ activeChannel.desc }}</span>
          </div>
        </div>
        <div class="info-list side-kv">
          <div><span>短链</span><b>{{ activeChannel.shortUrl }}</b></div>
          <div><span>绑定内容</span><b>{{ activeChannel.content }}</b></div>
          <div><span>渠道标签</span><b>{{ activeChannel.tags }}</b></div>
          <div><span>转化率</span><b>{{ activeChannel.rate }}</b></div>
        </div>
        <div class="side-actions">
          <button class="primary" type="button">复制入口</button>
          <button class="ghost" type="button">编辑配置</button>
        </div>
      </aside>
    </section>

    <section v-else-if="section === 'content'" class="workbench two-col">
      <section class="card main-panel">
        <div class="filter-bar">
          <div class="filter-title">内容筛选</div>
          <div class="filter-row">
            <div class="filter-item"><label>结节主题</label><select><option>全部</option><option>乳腺结节</option><option>甲状腺结节</option><option>肺结节</option></select></div>
            <div class="filter-item"><label>内容类型</label><select><option>全部</option><option>小红书</option><option>视频号</option><option>朋友圈</option></select></div>
            <div class="filter-item"><label>审核状态</label><select><option>全部</option><option>待审核</option><option>已通过</option><option>需修改</option></select></div>
            <div class="filter-actions"><button class="ghost" type="button">重置</button><button class="primary" type="button">查询</button><button class="primary" type="button">生成内容</button></div>
          </div>
        </div>
        <div class="topic-strip">
          <button v-for="topic in topics" :key="topic" type="button">{{ topic }}</button>
        </div>
        <div class="q-table-head-row"><span class="muted">内容任务 共 {{ contentItems.length }} 条</span></div>
        <div class="table-wrap compact-table">
          <table>
            <thead><tr><th style="width:210px">标题</th><th style="width:92px">平台</th><th style="width:92px">主题</th><th style="width:88px">状态</th><th style="width:78px">负责人</th><th style="width:96px">操作</th></tr></thead>
            <tbody>
              <tr v-for="item in contentItems" :key="item.title" class="q-row" :class="{ active: item.title === activeContent.title }" @click="activeContentTitle = item.title">
                <td><b>{{ item.title }}</b><span>{{ item.desc }}</span></td>
                <td><span class="nodule-tag">{{ item.platform }}</span></td>
                <td>{{ item.topic }}</td>
                <td><span class="status-tag" :data-s="item.statusKey">{{ item.status }}</span></td>
                <td>{{ item.owner }}</td>
                <td><button class="tbl-act" type="button">审核</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      <aside class="card side-panel">
        <div class="card-head compact"><div><h2>内容预览</h2><span>{{ activeContent.platform }} · {{ activeContent.topic }}</span></div><span class="status-tag" :data-s="activeContent.statusKey">{{ activeContent.status }}</span></div>
        <div class="draft-preview">
          <b>{{ activeContent.title }}</b>
          <p>{{ activeContent.copy }}</p>
          <div class="chip-row"><span v-for="tag in activeContent.tags" :key="tag">{{ tag }}</span></div>
        </div>
        <div class="side-actions"><button class="primary" type="button">通过审核</button><button class="ghost" type="button">退回修改</button></div>
      </aside>
    </section>

    <section v-else-if="section === 'leads'" class="workbench two-col">
      <section class="card main-panel">
        <div class="channel-stats">
          <div v-for="item in leadStats" :key="item.label" class="channel-stat"><div class="stat-icon" :data-tone="item.tone">{{ item.icon }}</div><div><span>{{ item.label }}</span><b>{{ item.value }}</b><em>{{ item.sub }}</em></div></div>
        </div>
        <div class="filter-bar">
          <div class="filter-title">线索筛选</div>
          <div class="filter-row">
            <div class="filter-item"><label>来源平台</label><select><option>全部</option><option>小红书</option><option>视频号</option><option>公众号</option></select></div>
            <div class="filter-item"><label>当前阶段</label><select><option>全部</option><option>新线索</option><option>已加企微</option><option>待交接</option></select></div>
            <div class="filter-item"><label>负责人</label><select><option>全部</option><option>赵婷</option><option>刘洋</option><option>王珊</option></select></div>
            <div class="filter-actions"><button class="ghost" type="button">重置</button><button class="primary" type="button">查询</button><button class="primary" type="button">批量分配</button></div>
          </div>
        </div>
        <div class="q-table-head-row"><span class="muted">线索列表 共 {{ filteredLeads.length }} 条</span></div>
        <div class="table-wrap compact-table">
          <table>
            <thead><tr><th style="width:92px">线索</th><th style="width:180px">来源</th><th style="width:96px">结节类型</th><th style="width:86px">意向</th><th style="width:92px">阶段</th><th style="width:78px">负责人</th><th style="width:120px">下一步</th></tr></thead>
            <tbody>
              <tr v-for="lead in filteredLeads" :key="lead.name" class="q-row" :class="{ active: lead.name === activeLead.name }" @click="activeLeadName = lead.name">
                <td><b>{{ lead.name }}</b><span>{{ lead.contact }}</span></td>
                <td>{{ lead.source }}</td>
                <td>{{ lead.type }}</td>
                <td><span class="status-tag" :data-s="lead.intentKey">{{ lead.intent }}</span></td>
                <td><span class="stage">{{ lead.stage }}</span></td>
                <td>{{ lead.owner }}</td>
                <td>{{ lead.next }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      <aside class="card side-panel">
        <div class="card-head compact"><div><h2>{{ activeLead.name }}</h2><span>{{ activeLead.type }} · {{ activeLead.stage }}</span></div><span class="status-tag" :data-s="activeLead.intentKey">{{ activeLead.intent }}</span></div>
        <div class="info-list side-kv">
          <div><span>联系方式</span><b>{{ activeLead.contact }}</b></div>
          <div><span>来源内容</span><b>{{ activeLead.source }}</b></div>
          <div><span>最近跟进</span><b>{{ activeLead.lastTouch }}</b></div>
          <div><span>咨询摘要</span><b>{{ activeLead.consultSummary }}</b></div>
          <div><span>分流结果</span><b>{{ activeLead.routing }}</b></div>
          <div><span>转人工规则</span><b>{{ activeLead.rule }}</b></div>
          <div><span>AI建议</span><b>{{ activeLead.aiAdvice }}</b></div>
          <div><span>交接资料</span><b>{{ activeLead.handoffPack }}</b></div>
        </div>
        <div class="side-actions"><button class="primary" type="button">交接健康管理师</button><button class="ghost" type="button">转人工</button><button class="ghost" type="button">写跟进</button></div>
      </aside>
    </section>

    <section v-else-if="section === 'assets'" class="workbench two-col">
      <section class="card main-panel">
        <div class="channel-stats">
          <div v-for="asset in assets" :key="asset.name" class="channel-stat"><div class="stat-icon">{{ asset.name.slice(0, 1) }}</div><div><span>{{ asset.name }}</span><b>{{ asset.count }}</b><em>{{ asset.desc }}</em></div></div>
        </div>
        <div class="table-wrap"><table><thead><tr><th>资产名称</th><th>类型</th><th>适用场景</th><th>状态</th><th>操作</th></tr></thead><tbody><tr v-for="asset in assetRows" :key="asset.name"><td><b>{{ asset.name }}</b><span>{{ asset.desc }}</span></td><td>{{ asset.type }}</td><td>{{ asset.scene }}</td><td><span class="status-tag" :data-s="asset.statusKey">{{ asset.status }}</span></td><td><button class="tbl-act">编辑</button></td></tr></tbody></table></div>
      </section>
      <aside class="card side-panel"><div class="card-head compact"><div><h2>合规提示</h2><span>医疗内容必须人工审核</span></div></div><div class="info-list side-kv"><div><span>禁用承诺</span><b>保证消除/治愈</b></div><div><span>高风险</span><b>转人工</b></div><div><span>发布前</span><b>医生或运营审核</b></div></div></aside>
    </section>

    <section v-else-if="section === 'employees'" class="workbench two-col">
      <section class="card main-panel">
        <div class="channel-stats">
          <div v-for="item in employeeStats" :key="item.label" class="channel-stat"><div class="stat-icon" :data-tone="item.tone">{{ item.icon }}</div><div><span>{{ item.label }}</span><b>{{ item.value }}</b><em>{{ item.sub }}</em></div></div>
        </div>
        <div class="q-table-head-row"><span class="muted">AI员工 共 {{ workers.length }} 个</span><button class="primary" type="button">新增员工</button></div>
        <div class="table-wrap compact-table">
          <table>
            <thead><tr><th style="width:130px">员工</th><th style="width:160px">负责场景</th><th style="width:140px">知识库</th><th style="width:112px">审核规则</th><th style="width:112px">转人工</th><th style="width:72px">状态</th></tr></thead>
            <tbody>
              <tr v-for="worker in workers" :key="worker.name" class="q-row" :class="{ active: worker.name === activeWorker.name }" @click="activeWorkerName = worker.name">
                <td><b>{{ worker.name }}</b><span>{{ worker.role }}</span></td>
                <td>{{ worker.scope }}</td>
                <td>{{ worker.kb }}</td>
                <td>{{ worker.audit }}</td>
                <td>{{ worker.handoff }}</td>
                <td><span class="status-tag" data-s="follow">启用</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      <aside class="card side-panel">
        <div class="card-head compact"><div><h2>{{ activeWorker.name }}</h2><span>{{ activeWorker.scope }}</span></div><span class="status-tag" data-s="follow">启用</span></div>
        <div class="info-list side-kv">
          <div><span>角色定位</span><b>{{ activeWorker.role }}</b></div>
          <div><span>可用知识库</span><b>{{ activeWorker.kb }}</b></div>
          <div><span>人工审核</span><b>{{ activeWorker.audit }}</b></div>
          <div><span>转人工规则</span><b>{{ activeWorker.handoff }}</b></div>
          <div><span>禁用行为</span><b>{{ activeWorker.ban }}</b></div>
        </div>
        <div class="side-actions"><button class="primary" type="button">保存配置</button><button class="ghost" type="button">停用</button></div>
      </aside>
    </section>

  </div>
</template>

<script setup>
import { computed, defineComponent, h, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getStoredScenario } from '../config/scenarios'

const LeadRows = defineComponent({
  props: { rows: Array },
  setup(props) {
    return () => h('div', { class: 'lead-rows' }, props.rows.map((row) => h('div', [
      h('b', row.name),
      h('span', `${row.type} · ${row.stage} · ${row.next}`),
    ])))
  },
})

const route = useRoute()
const scenario = computed(() => getStoredScenario())
const isHospital = computed(() => scenario.value.key === 'hospital')
const search = ref('')
const moduleEyebrow = computed(() => isHospital.value ? '医生IP打造 · 医生助手/管理师内容运营' : 'AI超级员工 · 报告前增长转化')
const boundaryText = computed(() => isHospital.value
  ? '医生IP内容只表达医生专业方向、科普观点和门诊服务入口；涉及诊断、治疗方案、风险判断和个体化建议必须回到医生或健康管理师工作台处理。'
  : '用户交接给健康管理师后，AI 超级员工链路结束；后续后链路工作由健康管理师工作台处理。')
const pages = computed(() => ({
  overview: isHospital.value
    ? { title: '数据看板', desc: '统一查看医生IP内容、获客入口、咨询线索、企微承接和转化表现。', search: '医生、内容、渠道、线索', action: '查看数据' }
    : { title: '增长看板', desc: '查看报告前获客、承接、初筛、交接和渠道转化表现。', search: '线索、渠道、负责人', action: '开始获客' },
  'super-employee': { title: '营销智脑', desc: '承载结节营销智脑超级员工页面，覆盖增长指挥、IP打造、内容生产、数字人、矩阵发布和私域成交。', search: '模块、线索、内容、素材', action: '打开原型' },
  channels: { title: '引流获客', desc: '管理落地页、企微活码、小程序表单、短链和渠道标签。', search: '渠道、入口、活动', action: '新建入口' },
  content: isHospital.value
    ? { title: '内容科普', desc: '围绕医生专长生成科普选题、短视频脚本、门诊宣教和私域答疑素材。', search: '医生、病种、选题、素材', action: '生成科普' }
    : { title: '内容营销', desc: '生成结节科普、私域话术和获客内容，人工审核后发布。', search: '选题、关键词、素材', action: '生成内容' },
  leads: { title: '线索转化', desc: '统一管理潜客阶段、咨询分流、意向等级、负责人和下一步动作。', search: '姓名、来源、阶段', action: '导入线索' },
  assets: { title: '知识资产库', desc: '沉淀话术、禁用词、合规提示、选题素材和案例素材。', search: '话术、禁用词、素材', action: '新增资产' },
  employees: isHospital.value
    ? { title: '员工设备', desc: '配置医生IP内容助手、医生助手和管理师运营协同规则。', search: '员工、医生、场景、规则', action: '配置员工' }
    : { title: '员工设备', desc: '配置 AI 内容、获客、线索转化和数据分析员工。', search: '员工、场景、规则', action: '配置员工' },
}))
const section = computed(() => {
  const raw = typeof route.params.section === 'string' ? route.params.section : 'overview'
  if (isHospital.value && ['channels', 'leads'].includes(raw)) return 'overview'
  return pages.value[raw] ? raw : 'overview'
})
const page = computed(() => pages.value[section.value])

const kpis = [
  { label: '新增线索', value: '86', sub: '较昨日 +18', tone: 'blue' },
  { label: '已加企微', value: '43', sub: '转化率 50.0%', tone: 'cyan' },
  { label: '已填初筛问卷', value: '27', sub: '待交接 9', tone: 'green' },
  { label: '待人工跟进', value: '14', sub: '高意向 6', tone: 'orange' },
  { label: '健康管理师交接', value: '11', sub: '今日已完成', tone: 'purple' },
]
const growthBoardKpis = [
  ...kpis,
  { label: '渠道转化率', value: '12.8%', sub: '留资到企微', tone: 'blue' },
  { label: '内容转化率', value: '4.4%', sub: '点击到留资', tone: 'green' },
  { label: '跟进及时率', value: '86%', sub: '30分钟内', tone: 'orange' },
  { label: '交接完成率', value: '73%', sub: '今日 11 人', tone: 'purple' },
]
const funnel = ['曝光', '点击', '留资', '加企微', '初筛问卷', '交接健康管理师'].map((label, index) => ({ label, value: ['12,680', '1,942', '86', '43', '27', '11'][index] }))
const topics = ['乳腺结节', '甲状腺结节', '肺结节', '三结节', '复查提醒', '报告前咨询', '饮食误区', '专家科普']
const channelStats = [
  { label: '有效入口', value: '18', sub: '运行中 15', tone: 'blue', icon: '入' },
  { label: '今日线索', value: '86', sub: '较昨日 +18', tone: 'green', icon: '线' },
  { label: '加企微', value: '43', sub: '转化率 50.0%', tone: 'purple', icon: '微' },
  { label: '待维护', value: '3', sub: '素材需更新', tone: 'orange', icon: '维' },
]
const channels = [
  { name: '乳腺结节科普落地页', desc: '体检发现乳腺结节后的报告前咨询入口', platform: '小红书', owner: '赵婷', goal: '留资 + 加企微', type: '落地页', leads: '31', status: '运行中', statusKey: 'follow', shortUrl: 'jiejie.online/breast-a', content: '乳腺结节科普笔记', tags: '乳腺结节 / 报告前 / 小红书', rate: '38.7%' },
  { name: '甲状腺复查提醒活码', desc: '视频号评论区和私信承接入口', platform: '视频号', owner: '刘洋', goal: '加企微', type: '企微活码', leads: '22', status: '运行中', statusKey: 'follow', shortUrl: 'jiejie.online/thyroid-wx', content: '甲状腺复查提醒短视频', tags: '甲状腺 / 复查 / 视频号', rate: '31.8%' },
  { name: '三结节初筛表单', desc: '公众号菜单和文章底部问卷入口', platform: '公众号', owner: '王珊', goal: '填写问卷', type: '小程序表单', leads: '18', status: '待优化', statusKey: 'review', shortUrl: 'jiejie.online/triple-form', content: '三结节初筛问卷', tags: '三结节 / 初筛 / 表单', rate: '24.1%' },
]
const activeChannelName = ref(channels[0].name)
const activeChannel = computed(() => channels.find((entry) => entry.name === activeChannelName.value) || channels[0])
const qrDots = [1, 2, 3, 5, 6, 7, 9, 11, 12, 15, 17, 18, 19, 21, 23, 24]
const contentItems = [
  { title: '体检发现乳腺结节先看哪几项', desc: '报告前咨询引导内容', platform: '小红书', topic: '乳腺结节', status: '待审核', statusKey: 'review', owner: '赵婷', copy: '不要只问严不严重，先看分级、大小、边界和既往对比，再决定是否需要进一步咨询。', tags: ['报告前', '科普', '留资'] },
  { title: '甲状腺结节复查时间怎么记', desc: '短视频脚本', platform: '视频号', topic: '甲状腺结节', status: '已通过', statusKey: 'follow', owner: '刘洋', copy: '不同分级的复查节奏不一样，建议保存报告并记录复查节点。', tags: ['复查提醒', '短视频'] },
  { title: '三结节人群初筛问卷', desc: '私域承接话术', platform: '朋友圈', topic: '三结节', status: '需修改', statusKey: 'review', owner: '王珊', copy: '先补充乳腺、甲状腺、肺部三类报告信息，再交给健康管理师接手。', tags: ['初筛', '问卷'] },
]
const activeContentTitle = ref(contentItems[0].title)
const activeContent = computed(() => contentItems.find((item) => item.title === activeContentTitle.value) || contentItems[0])
const leadStats = [
  { label: '高意向待交接', value: '9', sub: '优先处理', tone: 'green', icon: '高' },
  { label: '已加企微待问卷', value: '16', sub: '需提醒', tone: 'blue', icon: '微' },
  { label: '新线索待首触', value: '21', sub: '30分钟内', tone: 'orange', icon: '新' },
  { label: '超时未跟进', value: '4', sub: '需处理', tone: 'purple', icon: '超' },
]
const leads = [
  { name: '周女士', contact: '企微已添加', source: '小红书 · 乳腺结节笔记', type: '乳腺结节', stage: '已加企微', owner: '赵婷', next: '发送初筛问卷', intent: '中意向', intentKey: 'review', lastTouch: '12分钟前', consultSummary: '咨询报告前需要准备哪些信息', routing: '普通咨询', rule: '无高危词', aiAdvice: '补充报告照片后发送问卷', handoffPack: '来源 + 标签 + 咨询摘要' },
  { name: '陈先生', contact: '手机号 138****0921', source: '视频号 · 肺结节脚本', type: '肺结节', stage: '新线索', owner: '刘洋', next: '引导加企微', intent: '低意向', intentKey: 'gen', lastTouch: '未首触', consultSummary: '暂未咨询，仅留资', routing: '待首触', rule: '未触发', aiAdvice: '先发企微添加话术', handoffPack: '暂未满足交接条件' },
  { name: '李女士', contact: '问卷已提交', source: '公众号 · 三结节表单', type: '三结节', stage: '待交接', owner: '王珊', next: '分配健康管理师', intent: '高意向', intentKey: 'follow', lastTouch: '5分钟前', consultSummary: '已提交三结节初筛问卷', routing: '高意向', rule: '问卷完整', aiAdvice: '资料完整，可交接健康管理师', handoffPack: '来源 + 问卷摘要 + 风险标签' },
  { name: '郭女士', contact: '企微咨询中', source: '朋友圈 · 复查提醒', type: '甲状腺结节', stage: '待人工跟进', owner: '赵婷', next: '确认服务意向', intent: '高意向', intentKey: 'follow', lastTouch: '2分钟前', consultSummary: '咨询报告4A含义，情绪紧张', routing: '高风险转人工', rule: '4A触发', aiAdvice: '涉及4A，应人工承接', handoffPack: '来源 + 咨询摘要 + 高风险提醒' },
]
const activeLeadName = ref(leads[0].name)
const activeLead = computed(() => leads.find((lead) => lead.name === activeLeadName.value) || leads[0])
const assets = [
  { name: '合规话术', count: 126, desc: '私信、群发、客服回复' },
  { name: '禁用词', count: 43, desc: '医疗广告与承诺类表达' },
  { name: '选题素材', count: 218, desc: '多平台内容素材池' },
  { name: '案例素材', count: 36, desc: '已脱敏服务案例' },
]
const assetRows = [
  { name: '4A报告转人工提示', desc: '高风险咨询规则', type: '合规提示', scene: '线索转化', status: '启用', statusKey: 'follow' },
  { name: '小红书私信回复模板', desc: '报告前承接话术', type: '话术', scene: '内容获客', status: '启用', statusKey: 'follow' },
  { name: '疗效承诺禁用词', desc: '医疗广告风险词', type: '禁用词', scene: '内容审核', status: '启用', statusKey: 'follow' },
]
const employeeStats = [
  { label: '已启用员工', value: '5', sub: '前链路岗位', tone: 'blue', icon: '员' },
  { label: '需审核动作', value: '18', sub: '今日待处理', tone: 'orange', icon: '审' },
  { label: '转人工触发', value: '7', sub: '高风险/高意向', tone: 'purple', icon: '转' },
]
const workers = computed(() => {
  if (isHospital.value) {
    return [
      { name: '医生IP内容助手', role: '科普策划', scope: '医生专长选题、短视频脚本、图文草稿', kb: '医生专长库/科普素材库/合规库', audit: '医生或运营审核', handoff: '医疗判断转医生', ban: '诊断、疗效承诺、自动发布' },
      { name: '医生助手', role: '专业校对', scope: '医学术语、风险提示、门诊宣教口径', kb: '指南库/报告解读库/禁用词库', audit: '医生确认', handoff: '个体化建议转医生', ban: '替医生下结论、承诺疗效' },
      { name: '管理师运营助手', role: '承接运营', scope: '评论私信分层、企微承接、复诊提醒', kb: '线索阶段库/服务SOP库', audit: '人工确认交接', handoff: '高意向/高风险交接', ban: '越权诊疗、自动进入后链路' },
      { name: 'IP数据分析助手', role: '数据分析', scope: '内容表现、入口线索、转化趋势', kb: '指标库/渠道库', audit: '导出需确认', handoff: '异常指标提醒运营', ban: '篡改数据、夸大ROI' },
    ]
  }
  return [
    { name: 'AI内容员工', role: '内容生产', scope: '生成内容草稿', kb: '选题库/合规库', audit: '必须人工审核', handoff: '医疗判断转人工', ban: '诊断、疗效承诺、自动发布' },
    { name: 'AI获客员工', role: '入口运营', scope: '管理获客入口和渠道标签', kb: '渠道库/活动库', audit: '入口上线审核', handoff: '异常渠道转人工', ban: '自动投放、虚假宣传' },
    { name: 'AI转化员工', role: '线索分层', scope: '分层、咨询分流和提醒', kb: '线索阶段库/风险词库', audit: '人工确认交接', handoff: '高意向/高风险交接', ban: '承诺服务效果、自动进入后链路' },
    { name: 'AI数据分析员工', role: '增长分析', scope: '统计渠道和内容转化', kb: '指标库/渠道库', audit: '导出需确认', handoff: '异常指标提醒运营', ban: '篡改数据、夸大ROI' },
  ]
})
const activeWorkerName = ref(workers.value[0].name)
const activeWorker = computed(() => workers.value.find((worker) => worker.name === activeWorkerName.value) || workers.value[0])
const dashboardRows = [
  { channel: '小红书', leads: 31, wecom: 18, handoff: 12, rate: '38.7%' },
  { channel: '视频号', leads: 22, wecom: 11, handoff: 7, rate: '31.8%' },
  { channel: '公众号', leads: 18, wecom: 9, handoff: 5, rate: '27.8%' },
  { channel: '朋友圈', leads: 15, wecom: 5, handoff: 3, rate: '20.0%' },
]
const trendBars = [
  { day: '周一', rate: 42, value: '18' },
  { day: '周二', rate: 55, value: '24' },
  { day: '周三', rate: 48, value: '21' },
  { day: '周四', rate: 71, value: '31' },
  { day: '周五', rate: 63, value: '27' },
  { day: '周六', rate: 38, value: '16' },
  { day: '周日', rate: 52, value: '22' },
]
const filteredLeads = computed(() => {
  const keyword = search.value.trim().toLowerCase()
  if (!keyword) return leads
  return leads.filter((lead) => Object.values(lead).some((value) => String(value).toLowerCase().includes(keyword)))
})
</script>

<style scoped>
.ai-page{min-height:0;height:100%;display:flex;flex-direction:column;gap:12px;color:#0f172a;background:#fff;padding:12px;box-sizing:border-box;overflow:auto}
.ai-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:12px;flex-shrink:0}
.eyebrow{color:#64748b;font-weight:750;font-size:12px;margin-bottom:4px}
h1{margin:0;font-size:22px;line-height:1.2;letter-spacing:0}
p{margin:0}
.ai-head p{margin-top:4px;color:#64748b;font-weight:750;font-size:12px;max-width:760px}
.head-actions{display:flex;align-items:flex-end;gap:6px;min-width:430px}
.search-box{height:32px;border:1px solid #d9e2ef;background:#fff;border-radius:6px;display:flex;align-items:center;gap:8px;padding:0 10px;flex:1}
.search-box span{color:#64748b;font-size:11px;font-weight:700}
.search-box input{border:0;outline:0;min-width:0;flex:1;color:#334155;font-size:13px}
.search-box:focus-within{border-color:#155eef;box-shadow:0 0 0 2px rgba(21,94,239,.1)}
.primary,.ghost{display:inline-flex;align-items:center;justify-content:center;border-radius:10px;padding:5px 10px;font-weight:950;cursor:pointer;min-height:32px;line-height:1.3;white-space:nowrap;font-size:13px}
.primary{background:#155eef;border:1px solid #155eef;color:#fff}
.ghost{border:1px solid #d9e2ef;background:#fff;color:#475569}
.page-stack{display:grid;gap:12px}
.grid{display:grid;gap:12px}
.grid.two{grid-template-columns:repeat(2,minmax(0,1fr))}
.grid.three{grid-template-columns:repeat(3,minmax(0,1fr))}
.grid.four{grid-template-columns:repeat(4,minmax(0,1fr))}
.card{min-width:0;border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden}
.card-head{min-height:40px;height:auto;border-bottom:1px solid #eef2f7;padding:8px 12px;display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;background:#fff}
.card-head.compact{min-height:40px}
.card-body{padding:12px}
h2{margin:0;font-size:15px;font-weight:950}
.card-head span{display:block;color:#64748b;font-size:12px;font-weight:750;margin-top:4px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:10px;flex-shrink:0}
.kpi-card{min-width:0;display:block;background:#f8fafc;border:1px solid #e6edf7;border-radius:10px;padding:12px 14px}
.kpi-card span{display:block;color:#64748b;font-size:11px;font-weight:600;white-space:nowrap}
.kpi-card b{display:block;font-size:22px;font-weight:900;line-height:1.2;margin-top:1px;color:#111827}
.kpi-card em{display:block;font-style:normal;color:#64748b;font-size:11px;font-weight:700;margin-top:2px}
.kpi-card[data-tone="blue"] b{color:#155eef}.kpi-card[data-tone="cyan"] b{color:#0891b2}.kpi-card[data-tone="green"] b{color:#16a34a}.kpi-card[data-tone="orange"] b{color:#f97316}.kpi-card[data-tone="purple"] b{color:#7c3aed}
.funnel-card{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:12px;display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;flex-shrink:0}
.funnel-step{border:1px solid #e6edf7;border-radius:10px;background:#f8fafc;padding:10px;display:grid;grid-template-columns:30px minmax(0,1fr);column-gap:8px;align-items:center}
.funnel-step:not(:last-child)::after{content:none}
.funnel-step i{grid-row:1/3;width:28px;height:28px;border-radius:9px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-style:normal;font-weight:950;font-size:12px}
.funnel-step span{font-size:11px;color:#64748b;font-weight:700;white-space:nowrap}
.funnel-step b{font-size:18px;line-height:1.2}
.topic-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px}
.topic-grid button{height:36px;border:1px solid #d9e2ef;border-radius:10px;background:#fff;color:#334155;font-weight:950;cursor:pointer;font-size:13px}
.topic-grid button:hover{border-color:#155eef;background:#f8fbff;color:#155eef}
.draft-box{border:1px solid #e6edf7;border-radius:10px;background:#f8fafc;padding:10px}
.draft-box b{display:block;margin-bottom:7px}
.draft-box p{color:#334155;font-size:13px;font-weight:750;line-height:1.55}
.chip-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.chip-row span,.pill{display:inline-flex;align-items:center;border-radius:999px;background:#eef5ff;color:#155eef;padding:3px 8px;font-size:11px;font-weight:900}
.pill[data-risk="转人工"]{border-color:#fecaca;background:#fff1f2;color:#ef4444}
.pill[data-risk="高意向"]{border-color:#bbf7d0;background:#ecfdf5;color:#16a34a}
.info-list,.lead-rows{display:grid;gap:8px}
.info-list div,.lead-rows div{border:1px solid #eef2f7;border-radius:10px;background:#f8fafc;padding:9px;display:flex;justify-content:space-between;gap:10px}
.info-list span,.lead-rows span{color:#64748b;font-size:12px;font-weight:850}
.info-list b,.lead-rows b{color:#0f172a}
.lead-rows div{display:block}
.lead-rows span{display:block;margin-top:4px}
.boundary-box{border:1px solid #fed7aa;border-radius:10px;background:#fff7ed;padding:10px}
.boundary-box b{color:#c2410c}
.boundary-box p{margin-top:5px;color:#7c2d12;font-size:13px;line-height:1.6;font-weight:850}
.message-text{color:#334155;font-weight:850;line-height:1.6;margin-bottom:10px}
.metric{font-size:30px;font-weight:900;color:#111827}
.table-wrap{margin:12px;border:1px solid #e6edf7;border-radius:12px;overflow:auto}
table{width:100%;table-layout:fixed;border-collapse:collapse;min-width:820px;font-size:13px}
th{background:#f8fafc;color:#64748b;text-align:left;padding:9px 8px;font-size:13px;font-weight:900;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
td{border-top:1px solid #f1f5f9;padding:9px 8px;color:#334155;font-weight:750;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
td b{display:block;color:#0f172a}
td span{display:block;color:#64748b;font-size:12px;margin-top:2px}
.stage{display:inline-flex!important;border-radius:999px;background:#eef5ff;color:#155eef;padding:3px 9px;font-size:11px;font-weight:800}
.channels-workbench{min-height:0;display:grid;grid-template-columns:minmax(0,1fr) minmax(300px,340px);gap:12px}
.workbench.two-col{min-height:0;display:grid;grid-template-columns:minmax(0,1fr) minmax(300px,340px);gap:12px}
.main-panel{min-height:0;display:flex;flex-direction:column}
.side-panel{min-height:0;overflow:auto}
.channel-main{min-height:0;display:flex;flex-direction:column}
.channel-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:10px;padding:12px 12px 0}
.channel-stat{min-width:0;display:flex;align-items:center;gap:10px;background:#f8fafc;border:1px solid #e6edf7;border-radius:10px;padding:12px 14px}
.stat-icon{width:40px;height:40px;border-radius:10px;display:grid;place-items:center;flex-shrink:0;background:#eff6ff;color:#2563eb;font-weight:950}
.stat-icon[data-tone="green"]{background:#ecfdf5;color:#059669}
.stat-icon[data-tone="purple"]{background:#f5f3ff;color:#7c3aed}
.stat-icon[data-tone="orange"]{background:#fff7ed;color:#d97706}
.channel-stat span{display:block;font-size:11px;color:#64748b;font-weight:600;white-space:nowrap}
.channel-stat b{display:block;font-size:22px;font-weight:900;color:#111827;line-height:1.2}
.channel-stat em{display:block;font-style:normal;font-size:11px;font-weight:700;color:#64748b;margin-top:2px}
.filter-bar{padding:12px 12px 0}
.filter-title{font-size:13px;font-weight:800;color:#374151;margin-bottom:8px}
.filter-row{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}
.filter-item{display:flex;flex-direction:column;gap:4px}
.filter-item label{font-size:11px;font-weight:700;color:#64748b}
.filter-item select{height:32px;border:1px solid #d9e2ef;border-radius:6px;padding:0 10px;outline:none;font-size:13px;min-width:110px;background:#fff}
.filter-item select:focus{border-color:#155eef}
.filter-actions{display:flex;gap:6px;align-items:flex-end}
.q-table-head-row{display:flex;align-items:center;justify-content:space-between;padding:10px 12px 6px;font-size:13px}
.muted{color:#64748b;font-weight:750}
.channel-table-wrap{margin-top:0;flex:1}
.q-row{cursor:pointer}
.q-row:hover td{background:#f8fbff}
.q-row.active td{background:#eef5ff}
.nodule-tag{display:inline-flex!important;align-items:center;border-radius:6px;padding:2px 6px;font-size:11px;font-weight:700;background:#eef5ff;color:#155eef;max-width:100%}
.status-tag{display:inline-flex;align-items:center;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:800}
.status-tag[data-s="follow"]{background:#ecfdf5;color:#059669}
.status-tag[data-s="review"]{background:#fff7ed;color:#c2410c}
.tbl-act{border:0;background:transparent;color:#155eef;font-weight:900;cursor:pointer;padding:2px 0;font-size:12px}
.channel-side{min-height:0;overflow:auto}
.channel-preview{padding:12px;display:flex;gap:12px;align-items:center;border-bottom:1px solid #eef2f7}
.qr-box{width:106px;height:124px;border:1px solid #e6edf7;border-radius:12px;background:#f8fafc;display:grid;place-items:center;padding:10px;box-sizing:border-box;flex-shrink:0}
.qr-box span{font-size:11px;color:#64748b;font-weight:850}
.qr-grid{display:grid;grid-template-columns:repeat(5,10px);gap:4px}
.qr-grid i{width:10px;height:10px;border-radius:2px;background:#d9e2ef}
.qr-grid i[data-on="true"]{background:#0f172a}
.preview-copy{min-width:0}
.preview-copy b{display:block;color:#0f172a;font-size:14px}
.preview-copy span{display:block;margin-top:5px;color:#64748b;font-size:12px;line-height:1.55;font-weight:750}
.side-kv{padding:12px}
.side-actions{display:flex;gap:8px;padding:0 12px 12px}
.topic-strip{display:flex;gap:8px;flex-wrap:wrap;padding:12px 12px 0}
.topic-strip button{height:30px;border:1px solid #d9e2ef;border-radius:10px;background:#fff;color:#334155;font-size:12px;font-weight:900;padding:0 10px;cursor:pointer}
.compact-table{margin-top:0;flex:1}
.draft-preview{padding:12px;border-bottom:1px solid #eef2f7}
.draft-preview b{display:block;color:#0f172a;font-size:15px}
.draft-preview p{margin-top:8px;color:#334155;font-size:13px;line-height:1.65;font-weight:750}
.side-boundary{margin:12px}
.worker-actions{display:flex;gap:8px;padding:0 12px 12px}
.trend-bars{display:grid;gap:10px;padding:12px}
.trend-bars div{display:grid;grid-template-columns:44px minmax(0,1fr) 42px;gap:10px;align-items:center;font-size:13px;color:#334155;font-weight:850}
.trend-bars i{height:10px;background:#eef2f7;border-radius:999px;overflow:hidden}
.trend-bars em{display:block;height:100%;background:#155eef;border-radius:999px}
.dashboard-workbench{display:grid;gap:12px}
.dashboard-funnel{border:0;margin:0}
.dashboard-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(300px,360px);gap:12px}
.embedded-workbench{min-height:720px;display:flex;border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden}
.embedded-frame{width:100%;min-height:720px;border:0;background:#fff}
@media (max-width:1380px){
  .ai-head{align-items:flex-start;flex-direction:column}
  .head-actions{min-width:0;width:100%}
  .kpi-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
  .funnel-card{grid-template-columns:repeat(3,minmax(0,1fr))}
  .funnel-step:not(:last-child)::after{display:none}
  .grid.two,.grid.three,.grid.four{grid-template-columns:1fr}
  .channels-workbench{grid-template-columns:1fr}
  .workbench.two-col{grid-template-columns:1fr}
  .dashboard-grid{grid-template-columns:1fr}
}
</style>
