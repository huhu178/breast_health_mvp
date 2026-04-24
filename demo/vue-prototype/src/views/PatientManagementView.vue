<template>
  <div class="pm">
    <section class="pm-shell" aria-label="患者管理三栏工作台">
      <header class="pm-top">
        <div class="pm-top-left">
          <div class="pm-title">患者管理总览</div>
          <div class="muted" style="font-size:11px">数据更新于：2026-04-23 09:30</div>
        </div>
        <div class="pm-kpis">
          <button v-for="k in kpiStrip" :key="k.key" class="kpi" :data-tone="k.tone" :class="{ active: activeStage === k.key }" type="button" @click="setStage(k.key)">
            <div class="kpi-k">{{ k.label }}</div>
            <div class="kpi-v">{{ k.value }}</div>
            <div class="kpi-d muted">{{ k.delta }}</div>
          </button>
        </div>
      </header>

      <!-- tab=queue：总览（对齐你截图的双栏布局） -->
      <div v-if="subTab === 'queue'" class="pm-overview">
        <!-- 左：患者任务队列（大表格） -->
        <section class="card overview-left">
          <div class="card-head">
            <div class="card-title">患者任务队列</div>
            <div class="panel-tools">
              <input class="search" placeholder="姓名/手机号" />
              <select class="stage-select" :value="activeStage" @change="setStage($event.target.value)">
                <option v-for="t in stageTabs" :key="t.key" :value="t.key">{{ t.label }}</option>
              </select>
            </div>
          </div>

          <div class="q-table-wrap">
            <table class="q-table">
              <thead>
                <tr>
                  <th style="width:88px">姓名</th>
                  <th style="width:92px">性别/年龄</th>
                  <th style="width:122px">手机</th>
                  <th style="width:72px">来源</th>
                  <th>结节类型</th>
                  <th style="width:76px">风险</th>
                  <th style="width:168px">当前阶段</th>
                  <th style="width:88px">负责人</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in filteredQueue"
                  :key="p.id"
                  class="q-row"
                  :class="{ active: p.id === activePatientId }"
                  @click="activePatientId = p.id"
                >
                  <td><b>{{ p.name }}</b></td>
                  <td class="muted">{{ p.gender }} · {{ p.age }}岁</td>
                  <td class="muted">{{ p.phoneMasked }}</td>
                  <td class="muted">{{ p.source }}</td>
                  <td class="truncate">{{ p.nodules }}</td>
                  <td><span class="pill" :data-tone="p.riskTone">{{ p.risk }}</span></td>
                  <td><span class="tag2">{{ p.stageLabel }}</span></td>
                  <td class="muted">{{ p.owner }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pager">
            <span class="muted">共 1,236 条</span>
            <div class="pages">
              <button class="page-btn" type="button">‹</button>
              <button class="page-btn active" type="button">1</button>
              <button class="page-btn" type="button">2</button>
              <button class="page-btn" type="button">3</button>
              <span class="muted">…</span>
              <button class="page-btn" type="button">124</button>
              <button class="page-btn" type="button">›</button>
            </div>
            <div class="muted">10 条/页</div>
          </div>
        </section>

        <!-- 右：工作台 -->
        <aside class="overview-right">
          <section class="card">
            <div class="card-head">
              <div class="card-title">工作台</div>
            </div>
            <div class="pad workbench">
              <div class="wb-top">
                <div class="wb-who">
                  <div class="wb-name">{{ activePatient.name }}</div>
                  <div class="muted">{{ activePatient.phoneMasked }}</div>
                </div>
                <div class="pill" :data-tone="activePatient.riskTone">{{ activePatient.risk }}</div>
              </div>

              <div class="wb-grid">
                <div class="wb-kv"><div class="k">门诊来源</div><div class="v">{{ activePatient.source }}</div></div>
                <div class="wb-kv"><div class="k">结节类型</div><div class="v">{{ activePatient.nodules }}</div></div>
                <div class="wb-kv"><div class="k">最大直径</div><div class="v">8mm</div></div>
                <div class="wb-kv"><div class="k">服务状态</div><div class="v">{{ activePatient.serviceStatus }}</div></div>
                <div class="wb-kv"><div class="k">当前阶段</div><div class="v">{{ activePatient.stageLabel }}</div></div>
                <div class="wb-kv"><div class="k">负责人</div><div class="v">{{ activePatient.owner }}</div></div>
              </div>
            </div>
          </section>
        </aside>
      </div>

      <!-- 其它 tab：保持原三栏结构 -->
      <div v-else class="pm-detail">
        <!-- 左：患者任务队列（同患者队列样式） -->
        <section class="card overview-left">
          <div class="card-head">
            <div class="card-title">患者任务队列</div>
            <div class="panel-tools">
              <input class="search" placeholder="姓名/手机号" />
              <select class="stage-select" :value="activeStage" @change="setStage($event.target.value)">
                <option v-for="t in stageTabs" :key="t.key" :value="t.key">{{ t.label }}</option>
              </select>
            </div>
          </div>

          <div class="q-table-wrap">
            <table class="q-table">
              <thead>
                <tr>
                  <th style="width:88px">姓名</th>
                  <th style="width:92px">性别/年龄</th>
                  <th style="width:122px">手机</th>
                  <th style="width:72px">来源</th>
                  <th>结节类型</th>
                  <th style="width:76px">风险</th>
                  <th style="width:168px">当前阶段</th>
                  <th style="width:88px">负责人</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in filteredQueue"
                  :key="p.id"
                  class="q-row"
                  :class="{ active: p.id === activePatientId }"
                  @click="activePatientId = p.id"
                >
                  <td><b>{{ p.name }}</b></td>
                  <td class="muted">{{ p.gender }} · {{ p.age }}岁</td>
                  <td class="muted">{{ p.phoneMasked }}</td>
                  <td class="muted">{{ p.source }}</td>
                  <td class="truncate">{{ p.nodules }}</td>
                  <td><span class="pill" :data-tone="p.riskTone">{{ p.risk }}</span></td>
                  <td><span class="tag2">{{ p.stageLabel }}</span></td>
                  <td class="muted">{{ p.owner }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pager">
            <span class="muted">共 1,236 条</span>
            <div class="pages">
              <button class="page-btn" type="button">‹</button>
              <button class="page-btn active" type="button">1</button>
              <button class="page-btn" type="button">2</button>
              <button class="page-btn" type="button">3</button>
              <span class="muted">…</span>
              <button class="page-btn" type="button">124</button>
              <button class="page-btn" type="button">›</button>
            </div>
            <div class="muted">10 条/页</div>
          </div>
        </section>

        <!-- 右：当前模块内容（卡片栈） -->
        <aside class="detail-right">
          <section class="card">
            <div class="card-head">
              <div class="card-title">{{ midTitle }}</div>
              <div class="detail-actions">
                <template v-if="subTab === 'record'">
                  <button class="btn" type="button">导入报告</button>
                  <button class="primary" type="button">上传原始报告</button>
                </template>
                <template v-else-if="subTab === 'review'">
                  <button class="btn" type="button">退回修改</button>
                  <button class="primary" type="button">审核通过并推送</button>
                </template>
                <template v-else-if="subTab === 'follow'">
                  <button class="primary" type="button">创建随访任务</button>
                </template>
                <template v-else-if="subTab === 'abnormal'">
                  <button class="btn" type="button">创建电话随访</button>
                  <button class="primary" type="button">创建复查提醒</button>
                </template>
              </div>
            </div>
            <div class="pad detail-head">
              <div class="dh-left">
                <div class="dh-name">{{ activePatient.name }}</div>
                <div class="muted">{{ activePatient.gender }} · {{ activePatient.age }}岁 · {{ activePatient.phoneMasked }}</div>
              </div>
              <div class="dh-right">
                <span class="pill" :data-tone="activePatient.riskTone">{{ activePatient.risk }}</span>
                <span class="tag2">{{ activePatient.stageLabel }}</span>
              </div>
            </div>
          </section>

          <!-- tab=record：档案与报告 -->
          <template v-if="subTab === 'record'">
            <section class="card">
              <div class="card-head">
                <div class="card-title">AI解读摘要</div>
                <button class="btn" type="button">复制摘要</button>
              </div>
              <div class="pad">
                <div class="long">{{ activePatient.aiReadSummary }}</div>
              </div>
            </section>
          </template>

          <!-- tab=review：健康报告审核 -->
          <template v-else-if="subTab === 'review'">
            <section class="card">
              <div class="card-head">
                <div class="card-title">{{ activePatient.reportDoc?.title || '健康管理报告（示意）' }}</div>
                <div class="review-actions">
                  <button class="btn" type="button">退回修改</button>
                  <button class="primary" type="button">审核通过</button>
                </div>
              </div>
              <div class="pad">
                <div v-for="s in (activePatient.reportDoc?.sections || [])" :key="s.h" class="doc-sec">
                  <div class="doc-h">{{ s.h }}</div>
                  <div class="doc-p">{{ s.p }}</div>
                </div>
              </div>
            </section>
          </template>

          <!-- tab=follow：AI助手随访 -->
          <template v-else-if="subTab === 'follow'">
          </template>

          <!-- tab=abnormal：异常与复查 -->
          <template v-else-if="subTab === 'abnormal'">
            <section class="card">
              <div class="card-head">
                <div class="card-title">处置记录</div>
                <div class="review-actions">
                  <button class="btn" type="button">创建电话随访</button>
                  <button class="primary" type="button">创建复查提醒</button>
                </div>
              </div>
              <div class="pad">
                <div v-for="e in (activePatient.abnormal?.interventions || [])" :key="e.at + e.action" class="audit-row">
                  <div class="audit-at">{{ e.at }}</div>
                  <div class="audit-main">
                    <div class="audit-line"><b>{{ e.by }}</b> · {{ e.action }}</div>
                    <div class="muted">{{ e.note }}</div>
                  </div>
                </div>
                <div class="hline"></div>
                <div class="row3">
                  <div class="muted">复查计划：</div>
                  <div class="row3-main">{{ activePatient.abnormal?.recallPlan }}</div>
                </div>
                <div class="row3">
                  <div class="muted">回收状态：</div>
                  <span class="pill mini" :data-tone="activePatient.abnormal?.recallTone || 'g'">{{ activePatient.abnormal?.recallState }}</span>
                  <span class="muted">{{ activePatient.abnormal?.recallHint }}</span>
                </div>
              </div>
            </section>
          </template>
        </aside>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const activeStage = ref('all')
const activePatientId = ref('p1')
const subTab = ref('queue')
const showAllTimeline = ref(false)

// demo11.png 风格：顶部为“任务概览KPI”（展示型mock，不用队列计数）
const kpiStrip = computed(() => ([
  { key: 'record', label: '新建档案', value: 128, delta: '今日 +12', tone: 'blue' },
  { key: 'upload', label: '待上传报告', value: 156, delta: '今日 +6', tone: 'green' },
  { key: 'aiGen', label: '待生成报告', value: 89, delta: '今日 +3', tone: 'purple' },
  { key: 'review', label: '待审核', value: 64, delta: '今日 -2', tone: 'orange' },
  { key: 'push', label: '待推送', value: 48, delta: '今日 +1', tone: 'blue2' },
  { key: 'follow', label: 'AI随访中', value: '1,236', delta: '进行中', tone: 'indigo' },
  { key: 'abnormal', label: '异常预警', value: 32, delta: '今日 +0', tone: 'red' },
  { key: 'recall', label: '复查待回收', value: 215, delta: '今日 +2', tone: 'teal' }
]))

const steps = computed(() => ([
  { label: '建档', ic: '档', sub: '04-10', cls: 'done' },
  { label: '上传上报', ic: '云', sub: '待上传', cls: 'active' },
  { label: 'AI健康报告', ic: 'AI', sub: '待生成', cls: '' },
  { label: '人工审核', ic: '审', sub: '待审核', cls: '' },
  { label: '推送患者', ic: '推', sub: '待推送', cls: '' },
  { label: '匹配AI助手', ic: '机', sub: '进行中', cls: '' },
  { label: '异常识别', ic: '警', sub: '监测', cls: '' },
  { label: '复查提醒', ic: '铃', sub: '已排程', cls: '' },
  { label: '复查回收', ic: '收', sub: '待回收', cls: '' },
  { label: '档案更新', ic: '更', sub: '—', cls: '' }
]))

const subTabs = [
  { key: 'queue', label: '患者队列' },
  { key: 'record', label: '档案与报告' },
  { key: 'review', label: '健康报告审核' },
  { key: 'follow', label: 'AI助手随访' },
  { key: 'abnormal', label: '异常与复查' }
]

const allowedSubTabs = new Set(subTabs.map((t) => t.key))

watch(
  () => route.query.tab,
  (tab) => {
    const key = typeof tab === 'string' ? tab : ''
    if (allowedSubTabs.has(key)) subTab.value = key
  },
  { immediate: true }
)

watch(
  () => subTab.value,
  (key) => {
    if (route.name !== 'patient') return
    if (route.query.tab === key) return
    router.replace({ query: { ...route.query, tab: key } })
  },
  { immediate: true }
)

const stageTabs = computed(() => {
  const base = [
    { key: 'all', label: '全部', count: queue.value.length },
    { key: 'record', label: '新建档案', count: countBy('record') },
    { key: 'upload', label: '待上传报告', count: countBy('upload') },
    { key: 'aiGen', label: '待生成报告', count: countBy('aiGen') },
    { key: 'review', label: '待审核', count: countBy('review') },
    { key: 'push', label: '待推送', count: countBy('push') },
    { key: 'follow', label: 'AI随访中', count: countBy('follow') },
    { key: 'abnormal', label: '异常预警', count: countBy('abnormal') },
    { key: 'recall', label: '复查待回收', count: countBy('recall') }
  ]
  return base
})

const nextActions = [
  '上传复查报告',
  '推送健康管理报告',
  '开启AI随访',
  '发送饮食建议',
  '发送运动计划',
  '创建电话随访',
  '标记异常',
  '创建复查提醒'
]

const queue = ref([
  {
    id: 'p1',
    name: '王先生',
    gender: '男',
    age: 58,
    phoneMasked: '138****5678',
    source: '门诊',
    owner: '健康管理师',
    nodules: '肺结节合并甲状腺结节',
    risk: '高风险',
    riskTone: 'r',
    stage: 'review',
    stageLabel: '健康管理报告待审核',
    nextStep: '医生确认后推送患者',
    serviceStatus: '报告待审核',
    report: {
      status: '待审核',
      summary: '肺部磨玻璃结节 8mm，建议 3 个月复查；甲状腺结节 TI-RADS 3 类，建议随访复查。'
    },
    rawReports: [
      { type: 'pdf', name: '20260420_胸部CT报告.pdf', size: '1.32 MB', at: '2026-04-20', state: '已上传', stateTone: 'g' },
      { type: 'zip', name: '胸部CT原始影像(DICOM).zip', size: '256.7 MB', at: '2026-04-20', state: '解析中', stateTone: 'o' },
      { type: 'pdf', name: '20260420_甲状腺超声报告.pdf', size: '0.84 MB', at: '2026-04-20', state: '已上传', stateTone: 'g' }
    ],
    aiReadSummary: '影像提示右上肺磨玻璃结节 8mm，倾向炎性/腺瘤样病变可能；建议 3 个月复查。甲状腺 TI-RADS 3 类，建议随访复查并结合既往对比。',
    reportDoc: {
      title: '健康管理报告（示意）',
      sections: [
        { h: '一、结节概况', p: '本次检查提示肺部磨玻璃结节 8mm，甲状腺结节 TI-RADS 3 类。' },
        { h: '二、风险分层', p: '综合结节大小、形态及患者基础情况，建议按高风险路径随访。' },
        { h: '三、随访建议', p: '建议 3 个月复查胸部 CT；甲状腺建议 6-12 个月复查超声。' },
        { h: '四、生活方式建议', p: '规律作息、控糖控盐、适度有氧运动；如出现持续咳嗽/胸痛等症状及时就医。' }
      ]
    },
    auditTrail: [
      { at: '08:18', by: 'AI', action: '生成健康管理报告', note: '生成摘要与建议' },
      { at: '08:30', by: '李医生', action: '审核通过', note: '同意推送患者' }
    ],
    chat: [
      { at: '09:20', from: 'AI健康管理师', text: '已为您安排 3 个月复查提醒，近期如有咳嗽加重请及时就医。' },
      { at: '20:10', from: '患者', text: '最近有点咳嗽，需要马上去医院吗？' },
      { at: '20:12', from: 'AI健康管理师', text: '请确认是否有咳血/胸痛/持续发热等；如有请立即就医，我们也建议安排电话随访。' }
    ],
    followTodos: [
      { title: '复查提醒', state: '已排程', tone: 'g', detail: '3个月复查胸部CT提醒已创建' },
      { title: '饮食建议', state: '待推送', tone: 'o', detail: '控糖食谱与晚餐建议' },
      { title: '运动计划', state: '已推送', tone: 'g', detail: '低强度快走 20min' }
    ],
    abnormal: {
      keywords: ['持续咳嗽', '高风险', '复查逾期'],
      interventions: [
        { at: '20:12', by: 'AI', action: '异常识别', note: '建议人工电话随访' },
        { at: '20:30', by: '健管师', action: '电话随访', note: '已沟通症状与就医建议' }
      ],
      recallPlan: '已创建 3 个月复查提醒（小程序 + 企微 + 短信）',
      recallState: '待回收',
      recallTone: 'o',
      recallHint: '复查报告未回收，建议二次提醒'
    },
    reviewers: '医生 / 药师 / 健管师',
    assistants: [
      { name: 'AI中医药膳师', state: '已启用', stateTone: 'g', todayTask: '晚餐控糖食谱，待推送', response: '未读' },
      { name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '3个月复查提醒，已排程', response: '已读' },
      { name: 'AI药师', state: '待启用', stateTone: 'o', todayTask: '用药核对提醒，待配置', response: '—' },
      { name: 'AI慢病管理师', state: '待启用', stateTone: 'o', todayTask: '合并慢病评估，待配置', response: '—' },
      { name: 'AI心理咨询师', state: '已启用', stateTone: 'o', todayTask: '检后焦虑评估，患者未回复', response: '未回复' },
      { name: 'AI运动康复师', state: '已启用', stateTone: 'g', todayTask: '低强度快走计划，已推送', response: '已读' },
      { name: 'AI健康生活方式规划师', state: '已启用', stateTone: 'g', todayTask: '饮食/作息建议，待推送', response: '未读' },
      { name: 'AI健康福利官', state: '待启用', stateTone: 'o', todayTask: '服务权益提醒，待配置', response: '—' },
      { name: 'AI名医数字分身/AIHLP健康规划师', state: '已启用', stateTone: 'g', todayTask: '阶段性建议（高风险路径）', response: '待人工确认' }
    ],
    timeline: [
      { at: '08:10', tone: 'b', text: '创建患者档案' },
      { at: '08:15', tone: 'b', text: '上传胸部CT报告、甲状腺超声报告', meta: '原始报告已入库，等待解析' },
      { at: '08:18', tone: 'p', text: 'AI生成健康管理报告', meta: '生成摘要与随访建议' },
      { at: '08:30', tone: 'g', text: '健康管理报告审核通过', meta: '待推送患者' },
      { at: '08:35', tone: 'b', text: '推送小程序，企微同步提醒' },
      { at: '09:20', tone: 'p', text: 'AI健康管理师发送复查提醒' },
      { at: '12:00', tone: 'p', text: 'AI中医药膳师推送晚餐控糖食谱' },
      { at: '18:30', tone: 'p', text: 'AI运动康复师推送低强度快走计划' },
      { at: '20:10', tone: 'y', text: '患者反馈“最近有点咳嗽”', meta: '来自企微聊天' },
      { at: '20:12', tone: 'r', text: 'AI识别异常，建议人工电话随访', meta: '异常：持续咳嗽/风险升高' }
    ]
  },
  {
    id: 'p2',
    name: '李女士',
    gender: '女',
    age: 46,
    phoneMasked: '139****2468',
    source: '体检',
    owner: '张医生',
    nodules: '乳腺结节',
    risk: '中风险',
    riskTone: 'o',
    stage: 'upload',
    stageLabel: '原始报告待上传',
    nextStep: '上传体检报告后生成健康管理报告',
    serviceStatus: '待上传报告',
    report: { status: '未生成', summary: '等待上传原始检查/体检报告。' },
    rawReports: [],
    aiReadSummary: '暂无原始报告，无法生成 AI 解读摘要。',
    reportDoc: { title: '健康管理报告（未生成）', sections: [{ h: '提示', p: '请先上传原始检查/体检报告。' }] },
    auditTrail: [{ at: '09:05', by: '系统', action: '建档完成', note: '等待上传报告' }],
    chat: [{ at: '09:08', from: '系统', text: '已提醒上传体检报告，上传后将自动生成健康管理报告。' }],
    followTodos: [{ title: '上传原始报告', state: '待完成', tone: 'o', detail: '体检中心 PDF / 影像 DICOM' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '待创建', recallState: '—', recallTone: 'g', recallHint: '暂无' },
    reviewers: '医生 / 药师 / 健管师',
    assistants: [
      { name: 'AI中医药膳师', state: '待启用', stateTone: 'o', todayTask: '入组后生成食谱建议', response: '—' },
      { name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '完成建档后自动启用随访', response: '—' },
      { name: 'AI药师', state: '待启用', stateTone: 'o', todayTask: '用药史采集与核对', response: '—' },
      { name: 'AI慢病管理师', state: '待启用', stateTone: 'o', todayTask: '慢病风险评估', response: '—' },
      { name: 'AI心理咨询师', state: '待启用', stateTone: 'o', todayTask: '检后焦虑评估', response: '—' },
      { name: 'AI运动康复师', state: '待启用', stateTone: 'o', todayTask: '运动处方生成', response: '—' },
      { name: 'AI健康生活方式规划师', state: '待启用', stateTone: 'o', todayTask: '生活方式建议', response: '—' },
      { name: 'AI健康福利官', state: '待启用', stateTone: 'o', todayTask: '服务权益提醒', response: '—' },
      { name: 'AI名医数字分身/AIHLP健康规划师', state: '待启用', stateTone: 'o', todayTask: '阶段性建议', response: '—' }
    ],
    timeline: [
      { at: '09:05', tone: 'b', text: '创建患者档案' },
      { at: '09:08', tone: 'y', text: '提醒上传体检报告', meta: '短信/企微双通道' }
    ]
  },
  {
    id: 'p3',
    name: '张先生',
    gender: '男',
    age: 62,
    phoneMasked: '137****1357',
    source: '门诊',
    owner: '刘医生',
    nodules: '甲状腺结节',
    risk: '低风险',
    riskTone: 'g',
    stage: 'follow',
    stageLabel: 'AI随访中',
    nextStep: '按计划执行复查提醒与生活方式干预',
    serviceStatus: 'AI随访中',
    report: { status: '已推送', summary: 'TI-RADS 3 类，建议 6-12 个月随访复查。' },
    rawReports: [
      { type: 'pdf', name: '20260318_甲状腺超声报告.pdf', size: '0.62 MB', at: '2026-03-18', state: '已归档', stateTone: 'g' }
    ],
    aiReadSummary: 'TI-RADS 3 类倾向良性，建议 6-12 个月随访复查，并关注结节大小变化。',
    reportDoc: {
      title: '健康管理报告（已推送）',
      sections: [
        { h: '结节概况', p: '甲状腺结节 TI-RADS 3 类，倾向良性。' },
        { h: '随访建议', p: '建议 6-12 个月复查超声；如出现吞咽不适、声音嘶哑等及时就医。' }
      ]
    },
    auditTrail: [{ at: '07:20', by: '张医生', action: '审核通过并推送', note: '小程序已送达' }],
    chat: [
      { at: '07:40', from: 'AI健康管理师', text: '已为您安排 6 个月复查提醒，请按计划复查。' },
      { at: '10:00', from: '患者', text: '问卷已填写，谢谢。' }
    ],
    followTodos: [
      { title: '复查提醒', state: '已排程', tone: 'g', detail: '6个月复查超声提醒' },
      { title: '生活方式建议', state: '已推送', tone: 'g', detail: '本周作息建议' }
    ],
    abnormal: {
      keywords: ['复查提醒'],
      interventions: [{ at: '07:40', by: 'AI', action: '推送提醒', note: '小程序 + 企微' }],
      recallPlan: '已创建 6 个月复查提醒',
      recallState: '进行中',
      recallTone: 'g',
      recallHint: '暂无异常'
    },
    reviewers: '医生 / 药师 / 健管师',
    assistants: [
      { name: 'AI中医药膳师', state: '已启用', stateTone: 'g', todayTask: '养生建议，已推送', response: '已读' },
      { name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '6个月复查提醒，已排程', response: '已读' },
      { name: 'AI药师', state: '待启用', stateTone: 'o', todayTask: '用药提醒，待配置', response: '—' },
      { name: 'AI慢病管理师', state: '待启用', stateTone: 'o', todayTask: '慢病评估，待配置', response: '—' },
      { name: 'AI心理咨询师', state: '待启用', stateTone: 'o', todayTask: '情绪评估，待配置', response: '—' },
      { name: 'AI运动康复师', state: '已启用', stateTone: 'g', todayTask: '轻量运动建议，已推送', response: '已读' },
      { name: 'AI健康生活方式规划师', state: '已启用', stateTone: 'g', todayTask: '本周作息建议，已推送', response: '已读' },
      { name: 'AI健康福利官', state: '待启用', stateTone: 'o', todayTask: '服务权益提醒，待配置', response: '—' },
      { name: 'AI名医数字分身/AIHLP健康规划师', state: '已启用', stateTone: 'g', todayTask: '阶段性建议（低风险路径）', response: '已确认' }
    ],
    timeline: [
      { at: '07:40', tone: 'b', text: '复查提醒已推送', meta: '小程序 + 企微' },
      { at: '10:00', tone: 'p', text: 'AI随访问卷回收', meta: '患者已填写' }
    ]
  },
  {
    id: 'p4', name: '陈女士', gender: '女', age: 52, phoneMasked: '136****8899', source: '体检', owner: '李医生',
    nodules: '乳腺结节', risk: '高风险', riskTone: 'r', stage: 'abnormal', stageLabel: '异常预警',
    nextStep: '升级医生复核', serviceStatus: '异常处置中',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260415_乳腺超声报告.pdf', size: '0.91 MB', at: '2026-04-15', state: '已归档', stateTone: 'g' }],
    aiReadSummary: 'BI-RADS 4A 类，建议穿刺活检或 3 个月复查。',
    reportDoc: { title: '健康管理报告', sections: [{ h: '结节概况', p: 'BI-RADS 4A，建议活检。' }] },
    auditTrail: [{ at: '10:00', by: 'AI', action: '异常识别', note: '建议人工介入' }],
    chat: [{ at: '10:05', from: 'AI健康管理师', text: '已识别异常，建议尽快就医。' }],
    followTodos: [{ title: '电话随访', state: '待完成', tone: 'r', detail: '确认患者是否已就医' }],
    abnormal: { keywords: ['BI-RADS 4A', '高风险', '未就医'], interventions: [{ at: '10:00', by: 'AI', action: '异常识别', note: '建议人工电话随访' }], recallPlan: '待创建', recallState: '待处置', recallTone: 'r', recallHint: '需尽快处置' },
    reviewers: '医生 / 药师 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '异常跟进', response: '待处理' }],
    timeline: [{ at: '10:00', tone: 'r', text: 'AI识别异常', meta: 'BI-RADS 4A 高风险' }]
  },
  {
    id: 'p5', name: '赵先生', gender: '男', age: 45, phoneMasked: '135****3344', source: '门诊', owner: '王医生',
    nodules: '肺结节', risk: '低风险', riskTone: 'g', stage: 'push', stageLabel: '待推送患者',
    nextStep: '推送健康管理报告', serviceStatus: '待推送',
    report: { status: '审核通过' }, rawReports: [{ type: 'pdf', name: '20260418_胸部CT报告.pdf', size: '1.1 MB', at: '2026-04-18', state: '已上传', stateTone: 'g' }],
    aiReadSummary: '右下肺小结节 5mm，倾向良性，建议 12 个月复查。',
    reportDoc: { title: '健康管理报告', sections: [{ h: '结节概况', p: '右下肺小结节 5mm，低风险。' }, { h: '随访建议', p: '12 个月复查胸部 CT。' }] },
    auditTrail: [{ at: '09:00', by: '王医生', action: '审核通过', note: '可推送患者' }],
    chat: [],
    followTodos: [{ title: '推送报告', state: '待完成', tone: 'o', detail: '小程序 + 企微' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '12个月复查提醒', recallState: '待创建', recallTone: 'o', recallHint: '推送后自动创建' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '推送后启用', response: '—' }],
    timeline: [{ at: '09:00', tone: 'g', text: '健康管理报告审核通过', meta: '待推送患者' }]
  },
  {
    id: 'p6', name: '孙女士', gender: '女', age: 39, phoneMasked: '139****5566', source: '社区', owner: '健康管理师',
    nodules: '甲状腺结节', risk: '低风险', riskTone: 'g', stage: 'aiGen', stageLabel: '待生成报告',
    nextStep: '生成AI健康管理报告', serviceStatus: '待生成报告',
    report: { status: '未生成' }, rawReports: [{ type: 'pdf', name: '20260419_甲状腺超声报告.pdf', size: '0.55 MB', at: '2026-04-19', state: '已上传', stateTone: 'g' }],
    aiReadSummary: '暂未生成，报告已上传待处理。',
    reportDoc: { title: '健康管理报告（未生成）', sections: [{ h: '提示', p: '请生成AI健康管理报告。' }] },
    auditTrail: [{ at: '08:40', by: '系统', action: '报告上传完成', note: '等待AI生成' }],
    chat: [],
    followTodos: [{ title: '生成AI报告', state: '待完成', tone: 'o', detail: '甲状腺超声报告已上传' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '待创建', recallState: '—', recallTone: 'g', recallHint: '暂无' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '生成报告后启用', response: '—' }],
    timeline: [{ at: '08:40', tone: 'b', text: '上传甲状腺超声报告', meta: '等待AI生成报告' }]
  },
  {
    id: 'p7', name: '周先生', gender: '男', age: 67, phoneMasked: '137****7788', source: '门诊', owner: '刘医生',
    nodules: '肺结节合并乳腺结节', risk: '高风险', riskTone: 'r', stage: 'recall', stageLabel: '复查待回收',
    nextStep: '催收复查报告', serviceStatus: '复查待回收',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260101_胸部CT报告.pdf', size: '1.5 MB', at: '2026-01-01', state: '已归档', stateTone: 'g' }],
    aiReadSummary: '肺部结节 10mm，高风险，已逾期复查。',
    reportDoc: { title: '健康管理报告（已推送）', sections: [{ h: '结节概况', p: '肺部结节 10mm，高风险。' }] },
    auditTrail: [{ at: '2026-01-05', by: '刘医生', action: '审核通过并推送', note: '已送达' }],
    chat: [{ at: '2026-04-01', from: 'AI健康管理师', text: '您的复查时间已到，请尽快安排复查。' }],
    followTodos: [{ title: '复查回收', state: '逾期', tone: 'r', detail: '3个月复查已逾期' }],
    abnormal: { keywords: ['复查逾期', '高风险'], interventions: [{ at: '2026-04-01', by: 'AI', action: '发送复查提醒', note: '患者未回复' }], recallPlan: '已创建复查提醒', recallState: '逾期未回收', recallTone: 'r', recallHint: '建议电话催收' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '催收复查报告', response: '未回复' }],
    timeline: [{ at: '2026-04-01', tone: 'r', text: '复查逾期未回收', meta: '建议电话催收' }]
  },
  {
    id: 'p8', name: '吴女士', gender: '女', age: 55, phoneMasked: '138****2233', source: '体检', owner: '张医生',
    nodules: '乳腺结节', risk: '中风险', riskTone: 'o', stage: 'review', stageLabel: '健康管理报告待审核',
    nextStep: '医生审核后推送', serviceStatus: '报告待审核',
    report: { status: '待审核' }, rawReports: [{ type: 'pdf', name: '20260421_乳腺超声报告.pdf', size: '0.78 MB', at: '2026-04-21', state: '已上传', stateTone: 'g' }],
    aiReadSummary: 'BI-RADS 3 类，建议 6 个月复查超声。',
    reportDoc: { title: '健康管理报告', sections: [{ h: '结节概况', p: 'BI-RADS 3 类，倾向良性。' }, { h: '随访建议', p: '6 个月复查超声。' }] },
    auditTrail: [{ at: '09:30', by: 'AI', action: '生成健康管理报告', note: '待审核' }],
    chat: [],
    followTodos: [{ title: '审核报告', state: '待完成', tone: 'o', detail: '等待医生审核' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '6个月复查提醒', recallState: '待创建', recallTone: 'o', recallHint: '审核通过后创建' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '审核通过后启用', response: '—' }],
    timeline: [{ at: '09:30', tone: 'p', text: 'AI生成健康管理报告', meta: '待医生审核' }]
  },
  {
    id: 'p9', name: '郑先生', gender: '男', age: 50, phoneMasked: '136****4455', source: '门诊', owner: '王医生',
    nodules: '甲状腺结节', risk: '中风险', riskTone: 'o', stage: 'follow', stageLabel: 'AI随访中',
    nextStep: '按计划随访', serviceStatus: 'AI随访中',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260310_甲状腺超声报告.pdf', size: '0.6 MB', at: '2026-03-10', state: '已归档', stateTone: 'g' }],
    aiReadSummary: 'TI-RADS 4A 类，建议 3 个月复查。',
    reportDoc: { title: '健康管理报告（已推送）', sections: [{ h: '结节概况', p: 'TI-RADS 4A，中风险。' }] },
    auditTrail: [{ at: '08:00', by: '王医生', action: '审核通过并推送', note: '已送达' }],
    chat: [{ at: '08:10', from: 'AI健康管理师', text: '已安排 3 个月复查提醒。' }],
    followTodos: [{ title: '复查提醒', state: '已排程', tone: 'g', detail: '3个月复查超声' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '3个月复查提醒', recallState: '进行中', recallTone: 'g', recallHint: '暂无异常' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '随访中', response: '已读' }],
    timeline: [{ at: '08:10', tone: 'b', text: '复查提醒已推送', meta: '小程序 + 企微' }]
  },
  {
    id: 'p10', name: '冯女士', gender: '女', age: 43, phoneMasked: '135****6677', source: '社区', owner: '健康管理师',
    nodules: '肺结节', risk: '低风险', riskTone: 'g', stage: 'upload', stageLabel: '原始报告待上传',
    nextStep: '上传体检报告', serviceStatus: '待上传报告',
    report: { status: '未生成' }, rawReports: [],
    aiReadSummary: '暂无原始报告。',
    reportDoc: { title: '健康管理报告（未生成）', sections: [{ h: '提示', p: '请上传原始报告。' }] },
    auditTrail: [{ at: '10:20', by: '系统', action: '建档完成', note: '等待上传报告' }],
    chat: [],
    followTodos: [{ title: '上传原始报告', state: '待完成', tone: 'o', detail: '体检中心 PDF' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '待创建', recallState: '—', recallTone: 'g', recallHint: '暂无' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '上传后启用', response: '—' }],
    timeline: [{ at: '10:20', tone: 'b', text: '创建患者档案', meta: '等待上传报告' }]
  },
  {
    id: 'p11', name: '蒋先生', gender: '男', age: 61, phoneMasked: '139****8800', source: '门诊', owner: '李医生',
    nodules: '肺结节', risk: '高风险', riskTone: 'r', stage: 'abnormal', stageLabel: '异常预警',
    nextStep: '电话随访确认症状', serviceStatus: '异常处置中',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260320_胸部CT报告.pdf', size: '1.2 MB', at: '2026-03-20', state: '已归档', stateTone: 'g' }],
    aiReadSummary: '左上肺磨玻璃结节 9mm，高风险，患者反馈胸痛。',
    reportDoc: { title: '健康管理报告（已推送）', sections: [{ h: '结节概况', p: '左上肺磨玻璃结节 9mm，高风险。' }] },
    auditTrail: [{ at: '2026-03-22', by: '李医生', action: '审核通过并推送', note: '已送达' }],
    chat: [{ at: '2026-04-20', from: '患者', text: '最近胸口有点痛，需要复查吗？' }],
    followTodos: [{ title: '电话随访', state: '待完成', tone: 'r', detail: '确认胸痛症状' }],
    abnormal: { keywords: ['胸痛', '高风险'], interventions: [{ at: '2026-04-20', by: 'AI', action: '异常识别', note: '患者反馈胸痛' }], recallPlan: '紧急复查', recallState: '待处置', recallTone: 'r', recallHint: '建议立即电话随访' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '异常跟进', response: '待处理' }],
    timeline: [{ at: '2026-04-20', tone: 'r', text: '患者反馈胸痛', meta: '建议紧急随访' }]
  },
  {
    id: 'p12', name: '韩女士', gender: '女', age: 48, phoneMasked: '137****1122', source: '体检', owner: '张医生',
    nodules: '乳腺结节', risk: '低风险', riskTone: 'g', stage: 'follow', stageLabel: 'AI随访中',
    nextStep: '按计划随访', serviceStatus: 'AI随访中',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260228_乳腺超声报告.pdf', size: '0.7 MB', at: '2026-02-28', state: '已归档', stateTone: 'g' }],
    aiReadSummary: 'BI-RADS 2 类，良性，建议 12 个月常规复查。',
    reportDoc: { title: '健康管理报告（已推送）', sections: [{ h: '结节概况', p: 'BI-RADS 2 类，良性。' }] },
    auditTrail: [{ at: '2026-03-01', by: '张医生', action: '审核通过并推送', note: '已送达' }],
    chat: [{ at: '2026-03-02', from: 'AI健康管理师', text: '已安排 12 个月复查提醒。' }],
    followTodos: [{ title: '复查提醒', state: '已排程', tone: 'g', detail: '12个月复查超声' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '12个月复查提醒', recallState: '进行中', recallTone: 'g', recallHint: '暂无异常' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '随访中', response: '已读' }],
    timeline: [{ at: '2026-03-02', tone: 'b', text: '复查提醒已推送', meta: '小程序' }]
  },
  {
    id: 'p13', name: '杨先生', gender: '男', age: 54, phoneMasked: '138****9900', source: '门诊', owner: '刘医生',
    nodules: '甲状腺结节合并肺结节', risk: '中风险', riskTone: 'o', stage: 'aiGen', stageLabel: '待生成报告',
    nextStep: '生成AI健康管理报告', serviceStatus: '待生成报告',
    report: { status: '未生成' }, rawReports: [{ type: 'pdf', name: '20260422_甲状腺超声报告.pdf', size: '0.65 MB', at: '2026-04-22', state: '已上传', stateTone: 'g' }, { type: 'pdf', name: '20260422_胸部CT报告.pdf', size: '1.0 MB', at: '2026-04-22', state: '已上传', stateTone: 'g' }],
    aiReadSummary: '暂未生成，报告已上传待处理。',
    reportDoc: { title: '健康管理报告（未生成）', sections: [{ h: '提示', p: '请生成AI健康管理报告。' }] },
    auditTrail: [{ at: '11:00', by: '系统', action: '报告上传完成', note: '等待AI生成' }],
    chat: [],
    followTodos: [{ title: '生成AI报告', state: '待完成', tone: 'o', detail: '两份报告已上传' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '待创建', recallState: '—', recallTone: 'g', recallHint: '暂无' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '生成报告后启用', response: '—' }],
    timeline: [{ at: '11:00', tone: 'b', text: '上传甲状腺超声 + 胸部CT报告', meta: '等待AI生成报告' }]
  }
])

const filteredQueue = computed(() => {
  if (activeStage.value === 'all') return queue.value
  return queue.value.filter((p) => p.stage === activeStage.value)
})

const activePatient = computed(() => {
  return queue.value.find((p) => p.id === activePatientId.value) || queue.value[0]
})

const midTitle = computed(() => {
  const map = {
    queue: '闭环处置工作台',
    record: '档案与报告',
    review: '健康报告审核',
    follow: 'AI助手随访',
    abnormal: '异常与复查'
  }
  return map[subTab.value] || '患者管理'
})

const midSub = computed(() => {
  const map = {
    queue: '选中患者后联动闭环时间线与操作区',
    record: '原始报告 / 历史报告 / AI解读摘要',
    review: 'AI健康管理报告审核通过后才能推送患者',
    follow: '随访推送与聊天融合展示',
    abnormal: '异常识别、人工介入、复查回收与档案更新'
  }
  return map[subTab.value] || ''
})

const rightTitle = computed(() => {
  const map = {
    queue: '下一步动作',
    record: '处置与动作',
    review: '审核与推送',
    follow: 'AI健康服务团队',
    abnormal: '处置与动作'
  }
  return map[subTab.value] || '操作区'
})

const rightSub = computed(() => {
  const map = {
    queue: '快速跳转各功能区',
    record: '围绕档案与原始报告',
    review: '面向患者推送前最后一道关',
    follow: '9类助手矩阵',
    abnormal: '异常/复查闭环动作'
  }
  return map[subTab.value] || ''
})

/**
 * @description 设置当前阶段筛选，并保证选中患者存在
 * @param {string} key 阶段key
 */
function setStage(key) {
  activeStage.value = key
  showAllTimeline.value = false
  const list = filteredQueue.value
  if (list.length && !list.some((p) => p.id === activePatientId.value)) {
    activePatientId.value = list[0].id
  }
  if (subTab.value !== 'queue') subTab.value = 'queue'
}

/**
 * @description 统计某阶段患者数
 * @param {string} key 阶段key
 * @returns {number} 数量
 */
function countBy(key) {
  return queue.value.filter((p) => p.stage === key).length
}

/**
 * @description 跳转到「患者建档」页面
 */
function goRecord() {
  router.push('/record')
}
</script>

<style scoped>
.pm{height:100%;display:flex;flex-direction:column;overflow:hidden}
.pm-shell{flex:1;min-height:0;background:#fff;border:1px solid #e6edf7;border-radius:14px;box-shadow:0 10px 30px rgba(15,23,42,.06);display:flex;flex-direction:column;overflow:hidden}
.pm-top{flex-shrink:0;display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:14px 14px;border-bottom:1px solid #eef2f7;background:#fbfdff}
.pm-title{font-size:14px;font-weight:950;color:#0f172a}
.pm-kpis{display:grid;grid-template-columns:repeat(8,minmax(104px,1fr));gap:10px;flex:1}
.kpi{border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 10px;text-align:left;cursor:pointer}
.kpi-k{color:#64748b;font-weight:950;font-size:12px}
.kpi-v{font-weight:950;color:#0f172a;font-size:18px;margin-top:6px}
.kpi-d{font-size:12px;margin-top:6px}
.kpi.active{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.12)}
.kpi[data-tone="blue"] .kpi-v{color:#155eef}
.kpi[data-tone="blue2"] .kpi-v{color:#2563eb}
.kpi[data-tone="green"] .kpi-v{color:#16a34a}
.kpi[data-tone="purple"] .kpi-v{color:#7c3aed}
.kpi[data-tone="orange"] .kpi-v{color:#f97316}
.kpi[data-tone="indigo"] .kpi-v{color:#4f46e5}
.kpi[data-tone="red"] .kpi-v{color:#ef4444}
.kpi[data-tone="teal"] .kpi-v{color:#0ea5b7}

.pm-body{flex:1;min-height:0;display:grid;grid-template-columns:320px minmax(0,1fr) 360px;gap:12px;padding:12px;background:#fff}
.panel{min-height:0}
.panel.left,.panel.mid,.panel.right{display:flex;flex-direction:column;gap:10px}
.panel-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 12px;border:1px solid #e6edf7;border-radius:12px;background:#fff}
.panel-title{font-weight:950;color:#0f172a}
.mid-tab{display:flex;flex-direction:column;align-items:flex-end;gap:4px;text-align:right}
.mid-chip{display:inline-flex;align-items:center;height:26px;border-radius:999px;border:1px solid #cfe0ff;background:#eef5ff;color:#155eef;font-weight:950;padding:0 10px}
.panel-tools{display:flex;gap:8px;align-items:center}
.search{height:32px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;outline:none;min-width:140px}
.stage-select{height:32px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;outline:none;font-weight:850}

.list{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:auto;flex:1;padding:10px;display:grid;gap:10px}
.row{border:1px solid #eef2f7;border-radius:12px;background:#fff;padding:10px;text-align:left;cursor:pointer}
.row.active{border-color:#155eef;background:#eef5ff}
.row-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.row-sub{margin-top:4px}
.row-meta{margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tag2{border:1px solid #cfe0ff;background:#eef5ff;color:#155eef;border-radius:999px;padding:3px 8px;font-weight:900;font-size:12px}

.pager{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:10px 12px}
.pages{display:flex;gap:8px;align-items:center}
.page-btn{border:1px solid #d9e2ef;background:#fff;border-radius:10px;padding:5px 9px;color:#475569;font-weight:950;cursor:pointer;font-size:13px}
.page-btn.active{background:#155eef;color:#fff;border-color:#155eef}

.card{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden}
/* 用 min-height + padding，避免固定高度导致裁字 */
.card-head{min-height:40px;height:auto;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:8px 12px;gap:10px;flex-wrap:wrap}
.card-title{font-weight:950;color:#0f172a;font-size:13px;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.info{padding:8px 10px}
.info-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px 10px}
.kv .k{color:#94a3b8;font-size:12px;font-weight:850}
.kv .v{margin-top:3px;font-weight:900;color:#0f172a;font-size:13px;line-height:1.45}

/* 右侧整体正文行高，避免压线裁切 */
.overview-right,
.detail-right{line-height:1.5}

.flow .steps{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:8px;padding:10px 12px}
.step{border:1px solid #eef2f7;border-radius:12px;background:#fbfdff;padding:10px;text-align:center}
.step .ic{width:28px;height:28px;border-radius:10px;background:#eef5ff;color:#155eef;display:grid;place-items:center;margin:0 auto 6px;font-weight:950}
.step .t{font-weight:950;color:#0f172a;font-size:12px}
.step.done{border-color:#bbf7d0;background:#f1fff6}
.step.done .ic{background:#ecfff3;color:#16a34a}
.step.active{border-color:#cfe0ff;background:#eef5ff}

.comm{flex:1;display:flex;flex-direction:column;min-height:0}
.tabs{display:flex;gap:6px;align-items:center}
.tab{border:1px solid #e6edf7;background:#fff;border-radius:999px;padding:5px 9px;font-weight:900;color:#526175;cursor:pointer}
.tab.active{border-color:#155eef;background:#eef5ff;color:#155eef}
.comm-body{padding:10px 12px;overflow:auto;flex:1;display:grid;gap:10px}
.evt2{display:grid;grid-template-columns:64px 1fr auto;gap:10px;align-items:start;border-top:1px solid #eef2f7;padding-top:10px}
.evt2:first-child{border-top:0;padding-top:0}
.evt3{display:grid;grid-template-columns:64px 1fr;gap:10px;align-items:start;border-top:1px solid #eef2f7;padding-top:10px}
.evt3:first-child{border-top:0;padding-top:0}
.time{color:#94a3b8;font-weight:900}
.line{color:#0f172a;font-weight:850;line-height:1.5}
.comm-foot{padding:10px 12px;border-top:1px solid #eef2f7;display:flex;gap:8px}
.input{flex:1;height:34px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;outline:none}
.primary{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  background:#155eef;
  border:1px solid #155eef;
  color:#fff;
  border-radius:10px;
  padding:5px 10px;
  font-weight:950;
  cursor:pointer;
  min-height:32px;
  line-height:1.3;
  white-space:nowrap;
  font-size:13px;
}
.btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  border:1px solid #d9e2ef;
  border-radius:10px;
  background:#fff;
  color:#475569;
  padding:5px 10px;
  font-weight:950;
  cursor:pointer;
  min-height:32px;
  line-height:1.3;
  white-space:nowrap;
  font-size:13px;
}
.ghost{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  width:100%;
  min-height:32px;
  border-radius:10px;
  border:1px solid #cfe0ff;
  background:#eef5ff;
  color:#155eef;
  font-weight:950;
  cursor:pointer;
  padding:5px 10px;
  line-height:1.3;
  white-space:nowrap;
  font-size:13px;
}

.ai-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;padding:10px 12px}
.ai-tile{border:1px solid #eef2f7;border-radius:12px;background:#fbfdff;padding:10px;text-align:center}
.ai-ico{width:32px;height:32px;border-radius:12px;background:#eef5ff;color:#155eef;display:grid;place-items:center;margin:0 auto 6px;font-weight:950}
.ai-ico[data-tone="g"]{background:#ecfff3;color:#16a34a}
.ai-ico[data-tone="o"]{background:#fff7ed;color:#f97316}
.ai-name{font-weight:900;color:#0f172a;font-size:12px;line-height:1.3}

.audit-box{padding:10px 12px;display:grid;gap:8px}
.row2{display:flex;gap:8px;align-items:baseline}
.next{padding:10px 12px;display:grid;gap:8px}
.next-actions{display:flex;gap:8px;margin-top:6px}

.pad{padding:8px 10px}
.hline{height:1px;background:#eef2f7;margin:12px 0}
.stack{display:grid;gap:8px}
.full{width:100%}
.long{color:#0f172a;line-height:1.7;font-size:13px}
.file-list{display:grid;gap:10px}
.file-row{display:flex;align-items:center;gap:10px;border:1px solid #eef2f7;border-radius:12px;background:#fff;padding:10px}
.file-ico{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;font-weight:950;color:#fff;flex:0 0 auto}
.file-ico[data-type="pdf"]{background:#ef4444}
.file-ico[data-type="zip"]{background:#f97316}
.file-main{min-width:0;flex:1}
.file-name{font-weight:950;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.empty{border:1px dashed #cbd5e1;background:#fbfdff;border-radius:12px;padding:14px}
.empty-title{font-weight:950;color:#0f172a}
.empty-actions{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.review-actions{display:flex;gap:8px;flex-wrap:wrap}
.doc-sec{border-top:1px solid #eef2f7;padding-top:10px;margin-top:10px}
.doc-sec:first-child{border-top:0;padding-top:0;margin-top:0}
.doc-h{font-weight:950;color:#0f172a;font-size:13px}
.doc-p{margin-top:6px;color:#334155;line-height:1.7;font-size:13px}
.audit-row{display:flex;gap:10px;align-items:flex-start;border-top:1px solid #eef2f7;padding-top:10px}
.audit-row:first-child{border-top:0;padding-top:0}
.audit-at{width:64px;flex:0 0 auto;color:#94a3b8;font-weight:900}
.audit-line{color:#0f172a;font-weight:850;font-size:13px}
.todo-list{display:grid;gap:10px}
.todo-row{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;border:1px solid #eef2f7;border-radius:12px;background:#fff;padding:10px}
.todo-title{font-weight:950;color:#0f172a}
.kw{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.kw-pill{border:1px solid #fed7aa;background:#fff7ed;color:#c2410c;border-radius:999px;padding:4px 10px;font-weight:950;font-size:12px}
.row3{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.row3-main{font-weight:900;color:#0f172a}

.q-table-wrap{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:auto;flex:1}
.q-table{width:100%;border-collapse:collapse;font-size:13px}
.q-table thead tr{border-bottom:1px solid #eef2f7;background:#f8fafc}
.q-table th{padding:10px 12px;text-align:left;color:#64748b;font-weight:900;white-space:nowrap}
.q-table td{padding:10px 12px;border-bottom:1px solid #f1f5f9;white-space:nowrap}
.q-row{cursor:pointer}
.q-row:hover td{background:#f8fbff}
.q-row.active td{background:#eef5ff}
.q-row:last-child td{border-bottom:0}
.truncate{max-width:360px;overflow:hidden;text-overflow:ellipsis}

.pm-overview{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:12px;padding:12px;background:#fff;overflow:hidden}
.overview-left{min-height:0;display:flex;flex-direction:column}
.overview-right{min-height:0;height:100%;display:flex;flex-direction:column;gap:12px;overflow-y:auto;overflow-x:hidden;padding-right:12px;padding-bottom:12px;box-sizing:border-box}
.workbench{display:grid;gap:10px}
.wb-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.wb-name{font-weight:950;color:#0f172a}
.wb-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px 12px;border-top:1px solid #eef2f7;padding-top:10px;margin-top:2px}
.wb-kv .k{color:#94a3b8;font-size:12px;font-weight:850}
.wb-kv .v{margin-top:4px;font-weight:900;color:#0f172a;line-height:1.35}
.quick-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.quick-card{display:flex;align-items:center;gap:10px;border:1px solid #eef2f7;border-radius:12px;background:#fbfdff;padding:12px;text-align:left;cursor:pointer}
.quick-card:hover{border-color:#cfe0ff;background:#eef5ff}
.qc-ico{width:34px;height:34px;border-radius:12px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-weight:950;flex:0 0 auto}
.qc-ico2{background:#ecfff3;color:#16a34a}
.qc-ico3{background:#f5f3ff;color:#8b5cf6}
.qc-ico-r{background:#fff1f2;color:#dc2626}
.qc-title{font-weight:950;color:#0f172a}
.qc-main{min-width:0}

.pm-detail{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:12px;padding:12px;background:#fff;overflow:hidden}
.detail-right{min-height:0;height:100%;display:flex;flex-direction:column;gap:10px;overflow-y:auto;overflow-x:hidden;padding-right:12px;padding-bottom:12px;box-sizing:border-box}

.detail-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.detail-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.dh-name{font-weight:950;color:#0f172a;font-size:14px}
.dh-right{display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end}

.quick-links{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.quick-btn{display:flex;align-items:center;gap:10px;border:1px solid #e6edf7;border-radius:12px;background:#fbfdff;padding:10px 12px;text-align:left;cursor:pointer}
.quick-btn:hover{border-color:#cfe0ff;background:#eef5ff}
.quick-ico{width:32px;height:32px;border-radius:10px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-weight:950;flex-shrink:0}
.quick-ico-r{background:#fff1f2;color:#dc2626}
.quick-label{font-weight:950;color:#0f172a;font-size:13px}

.pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900}
.pill[data-tone="r"]{background:#fff1f2;color:#dc2626}
.pill[data-tone="o"]{background:#fff7ed;color:#c2410c}
.pill[data-tone="g"]{background:#ecfff3;color:#14843b}
.pill.mini{padding:2px 8px;font-size:11px}
.muted{color:#64748b;font-weight:750}
</style>

