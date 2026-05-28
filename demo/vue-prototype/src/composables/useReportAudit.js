import { computed, ref } from 'vue'

export function useReportAudit({
  apiJson,
  loadReportFollowupTask,
  normalizeAdvicePayload,
  reportTerms,
  rpActiveId,
}) {
  const rpAuditId = ref('')
  const rpAuditPara1 = ref('')
  const rpAuditPara2 = ref('')
  const rpAuditImagingAdvice = ref('')
  const rpAuditOverallAdvice = ref('')
  const rpAuditRiskAdvice = ref('')
  const rpAuditTongueAdvice = ref('')
  const rpAuditStatus = ref('')
  const rpAuditVersion = ref(1)
  const rpAuditWasReviewed = ref(false)

  const showAuditFollowupNext = computed(() => (
    !!rpAuditId.value
    && !String(rpAuditId.value).startsWith('r')
    && (rpAuditWasReviewed.value || ['archived', 'approved'].includes(String(rpAuditStatus.value || '').toLowerCase()))
  ))

  function currentAuditSections() {
    return {
      imaging_report_advice: rpAuditImagingAdvice.value,
      overall_assessment: rpAuditOverallAdvice.value,
      risk_assessment: rpAuditRiskAdvice.value,
      tongue_conclusion: rpAuditTongueAdvice.value,
    }
  }

  function closeAudit() {
    rpAuditId.value = ''
  }

  async function openAudit(report) {
    rpAuditId.value = report.id
    rpAuditPara1.value = report.summary || `暂无${reportTerms.value.summaryLabel}`
    rpAuditPara2.value = report.aiReadSummary || `暂无${reportTerms.value.adviceLabel}`
    rpAuditImagingAdvice.value = report.aiReadSummary || ''
    rpAuditOverallAdvice.value = report.summary || ''
    rpAuditRiskAdvice.value = report.risk ? `当前风险等级：${report.risk}` : ''
    rpAuditTongueAdvice.value = ''
    rpAuditStatus.value = ''
    rpAuditVersion.value = 1
    rpAuditWasReviewed.value = report.reportStatus === '已审核'
    rpActiveId.value = report.id
    if (!String(report.id || '').startsWith('r')) {
      try {
        const data = await apiJson(`/api/b/reports/${report.id}/advice`)
        const advice = normalizeAdvicePayload(data.advice, {})
        rpAuditPara2.value = advice.content || rpAuditPara2.value
        rpAuditImagingAdvice.value = advice.sections.imaging_report_advice || rpAuditPara2.value
        rpAuditOverallAdvice.value = advice.sections.overall_assessment || rpAuditPara1.value
        rpAuditRiskAdvice.value = advice.sections.risk_assessment || rpAuditRiskAdvice.value
        rpAuditTongueAdvice.value = advice.sections.tongue_conclusion || ''
        rpAuditStatus.value = advice.status || ''
        rpAuditVersion.value = advice.version || 1

        const detail = await apiJson(`/api/b/reports/${report.id}`)
        rpAuditPara1.value = detail.report_summary || detail.summary || rpAuditPara1.value
        rpAuditOverallAdvice.value = rpAuditOverallAdvice.value || rpAuditPara1.value
        rpAuditRiskAdvice.value = rpAuditRiskAdvice.value || detail.imaging_risk_warning || ''
        rpAuditTongueAdvice.value = rpAuditTongueAdvice.value || detail.record?.tongue_result_summary || ''
        report.summary = rpAuditPara1.value
        report.aiReadSummary = rpAuditImagingAdvice.value || rpAuditPara2.value
        if (['finalized', 'published', 'archived'].includes(String(detail.status || '').toLowerCase())) {
          await loadReportFollowupTask(report.id)
        }
      } catch (e) {
        console.error('加载报告建议失败', e)
      }
    }
  }

  return {
    closeAudit,
    currentAuditSections,
    openAudit,
    rpAuditId,
    rpAuditImagingAdvice,
    rpAuditOverallAdvice,
    rpAuditPara1,
    rpAuditPara2,
    rpAuditRiskAdvice,
    rpAuditStatus,
    rpAuditTongueAdvice,
    rpAuditVersion,
    rpAuditWasReviewed,
    showAuditFollowupNext,
  }
}
