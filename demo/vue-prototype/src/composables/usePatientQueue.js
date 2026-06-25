import { computed, ref } from 'vue'

const MOCK_QUEUE = [
  { id:'m1', name:'张*国', gender:'男', age:56, phoneMasked:'138****5678', source:'门诊', owner:'李医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'review', lastReport:'CT报告' },
  { id:'m2', name:'李*婷', gender:'女', age:48, phoneMasked:'139****2468', source:'体检中心', owner:'李医生', nodules:'甲状腺结节', noduleType:'thyroid', risk:'中风险', riskTone:'o', stage:'review', lastReport:'超声报告' },
  { id:'m3', name:'王*梅', gender:'女', age:62, phoneMasked:'137****1357', source:'门诊', owner:'李医生', nodules:'乳腺结节', noduleType:'breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day1', channel:'小程序', cycle:'每月' } },
  { id:'m4', name:'赵*强', gender:'男', age:59, phoneMasked:'136****8899', source:'体检中心', owner:'李医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'plan', lastReport:'CT报告', planTask:{ day:'day1', channel:'电话', cycle:'每两周' } },
  { id:'m5', name:'陈*霞', gender:'女', age:45, phoneMasked:'138****3344', source:'门诊', owner:'李医生', nodules:'乳腺+肺部结节', noduleType:'breast_lung', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day2', channel:'小程序', cycle:'每月' } },
  { id:'m6', name:'刘*峰', gender:'男', age:71, phoneMasked:'139****7788', source:'体检中心', owner:'李医生', nodules:'肺部+甲状腺结节', noduleType:'lung_thyroid', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'医生复核中', planTask:{ day:'day1', channel:'短信', cycle:'每季度' } },
  { id:'m7', name:'孙*英', gender:'女', age:52, phoneMasked:'137****6677', source:'门诊', owner:'李医生', nodules:'乳腺结节', noduleType:'breast', risk:'低风险', riskTone:'g', stage:'gen', lastReport:'超声报告' },
  { id:'m8', name:'周*明', gender:'男', age:64, phoneMasked:'138****9900', source:'门诊', owner:'李医生', nodules:'肺部+甲状腺结节', noduleType:'lung_thyroid', risk:'中风险', riskTone:'o', stage:'plan', lastReport:'CT报告', planTask:{ day:'day2', channel:'电话', cycle:'每月' } },
  { id:'m9', name:'吴*丽', gender:'女', age:39, phoneMasked:'150****4455', source:'社区', owner:'李医生', nodules:'乳腺+甲状腺结节', noduleType:'breast_thyroid', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'超声报告', planTask:{ day:'day1', channel:'小程序', cycle:'每两周' } },
  { id:'m10', name:'郑*涛', gender:'男', age:67, phoneMasked:'136****2233', source:'体检中心', owner:'李医生', nodules:'三合并结节', noduleType:'triple', risk:'高风险', riskTone:'r', stage:'plan', lastReport:'CT报告', planTask:{ day:'day3', channel:'电话', cycle:'每月' } },
  { id:'m11', name:'黄*芳', gender:'女', age:44, phoneMasked:'135****1122', source:'门诊', owner:'王医生', nodules:'乳腺结节', noduleType:'breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day3', channel:'小程序', cycle:'每月' } },
  { id:'m12', name:'林*海', gender:'男', age:58, phoneMasked:'132****8866', source:'体检中心', owner:'王医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'CT报告', planTask:{ day:'day7', channel:'电话', cycle:'每两周' } },
  { id:'m13', name:'何*秀', gender:'女', age:51, phoneMasked:'133****5544', source:'门诊', owner:'王医生', nodules:'甲状腺结节', noduleType:'thyroid', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'超声报告', planTask:{ day:'day14', channel:'小程序', cycle:'每季度' } },
  { id:'m14', name:'马*军', gender:'男', age:63, phoneMasked:'139****3311', source:'体检中心', owner:'李医生', nodules:'肺部+乳腺结节', noduleType:'lung_breast', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day7', channel:'小程序', cycle:'每月' } },
  { id:'m15', name:'谢*云', gender:'女', age:37, phoneMasked:'136****7700', source:'社区', owner:'王医生', nodules:'甲状腺+乳腺结节', noduleType:'thyroid_breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'超声报告', planTask:{ day:'day21', channel:'小程序', cycle:'每月' } },
  { id:'m16', name:'徐*刚', gender:'男', age:55, phoneMasked:'138****4499', source:'门诊', owner:'李医生', nodules:'肺部结节', noduleType:'lung', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'CT报告', planTask:{ day:'day30', channel:'电话', cycle:'每季度' } },
]

export function usePatientQueue({
  isCheckupScenario,
  noduleTypeLabel,
  queue,
  riskLevelLabel,
  riskToneFromLevel,
  scenario,
  statusKey,
  statusLabel,
}) {
  const activeStage = ref('all')
  const qSearch = ref('')
  const qSource = ref('')
  const qNodule = ref('')
  const qRisk = ref('')
  const qStatus = ref('')
  const qDepartment = ref('')
  const qDoctor = ref('')
  const qManager = ref('')

  function sourceLabel(src) {
    const s = String(src || '').trim()
    const hit = scenario.value.sourceOptions.find((x) => s.includes(x) || x.includes(s))
    if (hit) return hit
    return scenario.value.sourceOptions[0] || s || '—'
  }

  function ownerLabel(owner) {
    const s = String(owner || '').trim()
    if (!s) return '—'
    return s.includes('医生') ? s : `${s.replace(/(师|员|岗|管理师)$/,'')}医生`
  }

  function adaptMockQueueByScenario(list) {
    const sources = scenario.value.sourceOptions || []
    const owner = scenario.value.defaultOwner || '李医生'
    return list.map((p, idx) => ({
      ...p,
      source: sources[idx % Math.max(sources.length, 1)] || p.source,
      owner: idx % 3 === 0 ? owner : p.owner?.replace('医生', scenario.value.key === 'pharmacy' ? '药师' : scenario.value.key === 'community' ? '家医' : '医生'),
    }))
  }

  async function loadPatients() {
    try {
      const query = new URLSearchParams({ page_size: '100' })
      if (qSearch.value) query.set('keyword', qSearch.value)
      if (qDepartment.value) query.set('department_id', qDepartment.value)
      if (qDoctor.value) query.set('doctor_id', qDoctor.value)
      if (qManager.value) query.set('manager_id', qManager.value)
      const noduleMap = {
        '乳腺结节': 'breast',
        '肺部结节': 'lung',
        '甲状腺结节': 'thyroid',
        '乳腺+肺部结节': 'breast_lung',
        '乳腺+甲状腺结节': 'breast_thyroid',
        '肺部+甲状腺结节': 'lung_thyroid',
        '三合并结节': 'triple',
      }
      if (qNodule.value) query.set('nodule_type', noduleMap[qNodule.value] || qNodule.value)
      const res = await fetch(`/api/hospital/patients?${query}`, { credentials: 'include' })
      const data = await res.json()
      if (data.success) {
        const items = (data.data?.patients || data.data?.items || data.data || [])
        queue.value = items.map(p => ({
          id: p.id,
          _apiId: p.id,
          name: p.name || '—',
          gender: p.gender || '—',
          age: p.age || '—',
          phoneMasked: p.phone ? p.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '—',
          phone: p.phone || '',
          wecomExternalUserid: p.wecom_external_userid || '',
          wecomUserid: p.wecom_userid || '',
          wecomBindStatus: p.wecom_bind_status || ((p.wecom_external_userid || p.wecom_userid) ? 'bound' : 'unbound'),
          wecomBoundAt: p.wecom_bound_at || '',
          source: p.source_channel === 'manual' ? scenario.value.sourceOptions[0] : (p.source_channel || scenario.value.sourceOptions[0]),
          owner: p.primary_doctor_name || p.manager_name || scenario.value.defaultOwner,
          managerName: p.manager_name || '',
          departmentName: p.department_name || '',
          department_id: p.department_id,
          primary_doctor_id: p.primary_doctor_id,
          manager_id: p.manager_id,
          nodules: noduleTypeLabel(p.nodule_type),
          noduleType: p.nodule_type || 'breast',
          risk: riskLevelLabel(p.latest_report_risk_level || p.risk_level || (p.reports?.[0]?.risk_level) || '—'),
          riskTone: riskToneFromLevel(p.latest_report_risk_level || p.risk_level || p.reports?.[0]?.risk_level),
          stage: p.risk_level ? 'plan' : (p.reports?.length ? 'review' : 'gen'),
          stageLabel: p.risk_level ? statusLabel({ stage: 'plan' }) : (p.reports?.length ? statusLabel({ stage: 'review' }) : statusLabel({ stage: 'aiGen' })),
          nextStep: '',
          serviceStatus: '',
          report: { status: '—', summary: '' },
          rawReports: [],
          aiReadSummary: '',
          reportDoc: { title: '', sections: [] },
          auditTrail: [],
          chat: [],
          followTodos: [],
          abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
          reviewers: '',
          assistants: [],
          timeline: [],
          planTask: null,
        }))
      }
    } catch (e) {
      console.error('加载患者列表失败', e)
    }
    if (!queue.value.length) queue.value = adaptMockQueueByScenario(MOCK_QUEUE).map(p => ({
      ...p,
      stageLabel: '', nextStep: '', serviceStatus: '',
      report: { status: '—', summary: '' }, rawReports: [],
      aiReadSummary: '', reportDoc: { title: '', sections: [] },
      auditTrail: [], chat: [], followTodos: [],
      abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
      reviewers: '', assistants: [], timeline: [],
    }))
    const followMocks = adaptMockQueueByScenario(MOCK_QUEUE).filter(p => p.stage === 'follow').map(p => ({
      ...p,
      stageLabel: '任务执行中', nextStep: '', serviceStatus: '任务执行中',
      report: { status: '—', summary: '' }, rawReports: [],
      aiReadSummary: '', reportDoc: { title: '', sections: [] },
      auditTrail: [], chat: [], followTodos: [],
      abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
      reviewers: '', assistants: [], timeline: [],
    }))
    const existingIds = new Set(queue.value.map(p => p.id))
    followMocks.forEach(p => { if (!existingIds.has(p.id)) queue.value.push(p) })
  }

  function noduleTags(p) {
    const type = p.noduleType || ''
    const parts = type.split('_')
    if (parts.length === 1 && type) return [{ label: noduleTypeLabel(type), type }]
    const map = { breast: '乳腺结节', lung: '肺部结节', thyroid: '甲状腺结节', triple: '三合并' }
    if (type === 'triple') return [{ label: '三合并结节', type: 'triple' }]
    return parts.map(k => ({ label: map[k] || k, type: k }))
  }

  const queueFiltered = computed(() => {
    let list = queue.value
    if (qSearch.value) list = list.filter(p => p.name.includes(qSearch.value) || (p.phoneMasked || '').includes(qSearch.value))
    if (qSource.value) list = list.filter(p => sourceLabel(p.source) === qSource.value || p.source === qSource.value)
    if (qNodule.value) list = list.filter(p => p.nodules === qNodule.value)
    if (qRisk.value) list = list.filter(p => p.risk === qRisk.value)
    if (qStatus.value) list = list.filter(p => statusKey(p) === qStatus.value)
    return list
  })

  function resetQueueFilters() {
    qSearch.value = ''
    qSource.value = ''
    qNodule.value = ''
    qRisk.value = ''
    qStatus.value = ''
    qDepartment.value = ''
    qDoctor.value = ''
    qManager.value = ''
  }

  const filteredQueue = computed(() => {
    if (activeStage.value === 'all') return queue.value
    return queue.value.filter((p) => statusKey(p) === activeStage.value)
  })

  const planPatients = computed(() => queue.value.filter((p) => statusKey(p) === 'plan'))

  const stageTabs = computed(() => {
    const count = (k) => queue.value.filter((p) => statusKey(p) === k).length
    return [
      { key: 'all', label: '全部', count: queue.value.length },
      { key: 'gen', label: `${scenario.value.reportLabel}待生成`, count: count('gen') },
      { key: 'review', label: isCheckupScenario.value ? '待总检确认' : '健康报告待审核', count: count('review') },
      { key: 'plan', label: '任务待下发', count: count('plan') },
      { key: 'follow', label: '任务执行中', count: count('follow') },
    ]
  })

  return {
    activeStage,
    filteredQueue,
    loadPatients,
    noduleTags,
    ownerLabel,
    planPatients,
    qNodule,
    qRisk,
    qSearch,
    qSource,
    qStatus,
    qDepartment,
    qDoctor,
    qManager,
    queueFiltered,
    resetQueueFilters,
    sourceLabel,
    stageTabs,
  }
}
