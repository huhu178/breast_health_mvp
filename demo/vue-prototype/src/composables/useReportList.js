import { computed, ref } from 'vue'

export function useReportList({
  isCheckupScenario,
  noduleTypeLabel,
  reportTerms,
  riskLevelLabel,
  riskToneFromLevel,
  scenario,
  sourceLabel,
  toast,
}) {
  const rpSearch = ref('')
  const rpSource = ref('')
  const rpNodule = ref('')
  const rpRisk = ref('')
  const rpActiveId = ref(1)
  const rpList = ref([])
  const rpLoading = ref(false)
  const rpLoaded = ref(false)

  function makeReportFlow(createdAt = '', finalized = false) {
    return [
      { label: reportTerms.value.flowBuild, done: true, cur: false, time: '' },
      { label: reportTerms.value.flowGenerate, done: true, cur: false, time: createdAt || '' },
      { label: reportTerms.value.flowReview, done: finalized, cur: !finalized, time: finalized ? '已完成' : '当前步骤' },
      { label: reportTerms.value.flowPush, done: false, cur: false, time: '待处理' },
    ]
  }

  function toScenarioReport(report, idx = 0) {
    if (!isCheckupScenario.value) return { ...report, reportType: scenario.value.reportLabel }
    const sources = scenario.value.sourceOptions
    const owners = ['总检医生', '健康管理师', '体检医生', '复查专员']
    return {
      ...report,
      source: sources[idx % sources.length],
      owner: owners[idx % owners.length],
      reportType: scenario.value.reportLabel,
      aiStatus: report.aiStatus === '已完成' ? '已完成' : '待确认',
      summary: report.summary || '体检报告已完成结构化解析，请结合异常指标和既往体检记录确认复查建议。',
      aiReadSummary: report.aiReadSummary || '建议根据风险等级完成体检报告解读、复查预约和必要的专科转诊。',
      flow: makeReportFlow(report.uploadAt, report.reportStatus === '已审核'),
    }
  }

  async function loadReports() {
    if (rpLoaded.value || rpLoading.value) return
    rpLoading.value = true
    try {
      const allReports = []
      let page = 1
      let pages = 1
      do {
        const res = await fetch(`/api/b/reports?page=${page}&per_page=100&include_unreported=1`, { credentials: 'include' })
        const data = await res.json()
        if (!data.success) {
          rpList.value = []
          toast?.show(data.message || '加载真实报告列表失败')
          return
        }
        allReports.push(...(data.data?.reports || []))
        pages = data.data?.pages || 1
        page += 1
      } while (page <= pages)

      rpList.value = allReports
        .map((report) => {
          const patient = report.patient || {}
          const record = report.record || {}
          const gender = patient.gender || report.patient_gender || report.gender || '—'
          const age = record.age || report.patient_age || patient.age || report.age || '—'
          const phoneRaw = patient.phone || report.patient_phone || report.phone || ''
          const phoneMasked = phoneRaw
            ? String(phoneRaw).replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
            : '—'
          const sourceRaw = patient.source || patient.source_channel || report.patient_source || report.source || '—'
          const nType = report.nodule_type || patient.nodule_type || report.patient_nodule_type || 'breast'

          return {
            id: report.id,
            rawPatientId: report.patient_id,
            rawRecordId: report.record_id,
            isReportPlaceholder: !!report.is_report_placeholder,
            name: report.patient_name || '—',
            gender,
            age,
            phone: phoneMasked,
            source: sourceLabel(sourceRaw) || sourceRaw,
            reportType: scenario.value.reportLabel,
            nodules: noduleTypeLabel(nType),
            noduleKey: nType,
            uploadAt: report.created_at ? report.created_at.slice(0, 16).replace('T', ' ') : '—',
            aiStatus: report.status === 'not_generated' ? '待生成' : report.status === 'finalized' || report.status === 'published' ? '已完成' : '待审核',
            risk: riskLevelLabel(report.risk_level || '未评估'),
            riskTone: riskToneFromLevel(report.risk_level),
            owner: report.created_by_name || scenario.value.defaultOwner,
            summary: report.report_summary || report.summary || '',
            aiReadSummary: report.imaging_conclusion || report.ai_read_summary || '',
            reportStatus: report.status === 'not_generated' ? '待生成' : report.status === 'finalized' || report.status === 'published' ? '已审核' : '待审核',
            reportHtml: '',
            flow: makeReportFlow(report.created_at ? report.created_at.slice(0, 16).replace('T', ' ') : '', report.status === 'finalized'),
          }
        })
        .map(toScenarioReport)
      if (rpList.value.length) rpActiveId.value = rpList.value[0].id
      rpLoaded.value = true
    } catch (e) {
      console.error('加载报告列表失败', e)
      rpList.value = []
      toast?.show('加载真实报告列表失败，请确认后端服务和登录状态')
    } finally {
      rpLoading.value = false
    }
  }

  function useMockReports() {
    if (rpList.value.length) return
    rpList.value = [
      { id:'r1', name:'张*国', gender:'男', age:56, phone:'138****5678', source:'门诊', reportType: scenario.value.reportLabel, nodules:'肺部结节', uploadAt:'2025-04-10 09:20', aiStatus:'已完成', risk:'高风险', riskTone:'r', owner:'李医生', summary:'右上肺磨玻璃结节约8mm，建议3个月复查低剂量CT。', aiReadSummary:'结合吸烟史与影像特征，建议进入高风险随访路径。', reportStatus:'待审核', flow: makeReportFlow('2025-04-10 09:20') },
      { id:'r2', name:'李*婷', gender:'女', age:48, phone:'139****2468', source:'体检中心', reportType: scenario.value.reportLabel, nodules:'甲状腺结节', uploadAt:'2025-04-09 15:12', aiStatus:'已完成', risk:'中风险', riskTone:'o', owner:'王医生', summary:'甲状腺右叶结节TI-RADS 4A，建议结合超声随访。', aiReadSummary:'建议6个月复查超声，关注结节边界与血流变化。', reportStatus:'待审核', flow: makeReportFlow('2025-04-09 15:12') },
      { id:'r3', name:'王*梅', gender:'女', age:62, phone:'137****1357', source:'门诊', reportType: scenario.value.reportLabel, nodules:'乳腺结节', uploadAt:'2025-04-08 10:33', aiStatus:'已完成', risk:'中风险', riskTone:'o', owner:'赵医生', summary:'乳腺BI-RADS 3类结节，建议定期复查。', aiReadSummary:'建议6个月复查乳腺超声，并记录疼痛、溢液等症状。', reportStatus:'已审核', flow: makeReportFlow('2025-04-08 10:33', true) },
    ].map(toScenarioReport)
    rpActiveId.value = 'r1'
  }

  const rpFilteredList = computed(() => {
    return rpList.value.filter((report) => {
      if (rpSearch.value && !String(report.name || '').includes(rpSearch.value) && !String(report.phone || '').includes(rpSearch.value)) return false
      if (rpSource.value && report.source !== rpSource.value) return false
      if (rpNodule.value && report.nodules !== rpNodule.value) return false
      if (rpRisk.value && report.risk !== rpRisk.value) return false
      return true
    })
  })

  function resetReportFilters() {
    rpSearch.value = ''
    rpSource.value = ''
    rpNodule.value = ''
    rpRisk.value = ''
  }

  const rpActive = computed(() => rpList.value.find((report) => report.id === rpActiveId.value) || rpList.value[0])

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
  }

  function paragraphHtml(value) {
    const text = escapeHtml(value || '暂无')
    return text.replace(/\n/g, '<br>')
  }

  function buildReportPreviewHtml(report, reportId, reportDbStatusLabel) {
    const advice = report.advice_draft?.content || report.imaging_conclusion || report.ai_read_summary || ''
    const sections = report.advice_draft?.sections || {}
    const patientName = report.patient?.name || report.patient_name || '—'
    const nodule = noduleTypeLabel(report.nodule_type || report.record?.nodule_type)
    const reviewedAt = report.reviewed_at || report.updated_at || report.created_at || '—'
    return `
      <h2>${escapeHtml(scenario.value.reportLabel)}（报告内容预览）</h2>
      <p><b>报告编号：</b>${escapeHtml(report.report_code || reportId)} &nbsp; <b>状态：</b>${escapeHtml(reportDbStatusLabel(report.status))}</p>
      <p><b>患者：</b>${escapeHtml(patientName)} &nbsp; <b>结节类型：</b>${escapeHtml(nodule)} &nbsp; <b>风险等级：</b>${escapeHtml(report.risk_level || '未评估')}</p>
      <h3>${escapeHtml(reportTerms.value.summaryLabel)}</h3>
      <p>${paragraphHtml(report.report_summary || report.summary || sections.overall_assessment)}</p>
      <h3>${escapeHtml(reportTerms.value.adviceLabel)}</h3>
      <p>${paragraphHtml(advice || sections.imaging_report_advice)}</p>
      ${sections.risk_assessment ? `<h3>风险提示</h3><p>${paragraphHtml(sections.risk_assessment)}</p>` : ''}
      ${sections.tongue_conclusion ? `<h3>舌诊结论</h3><p>${paragraphHtml(sections.tongue_conclusion)}</p>` : ''}
      <p style="color:#94a3b8;font-size:12px;margin-top:20px">最后更新时间：${escapeHtml(reviewedAt)}</p>
    `
  }

  return {
    buildReportPreviewHtml,
    loadReports,
    makeReportFlow,
    resetReportFilters,
    rpActive,
    rpActiveId,
    rpFilteredList,
    rpList,
    rpLoaded,
    rpLoading,
    rpNodule,
    rpRisk,
    rpSearch,
    rpSource,
    toScenarioReport,
    useMockReports,
  }
}
