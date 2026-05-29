import { computed, ref } from 'vue'

export function useReportAudit({
  apiJson,
  generateReportJob,
  goRecord,
  isReportGenerating,
  loadReportFollowupTask,
  loadReports,
  makeReportFlow,
  markReportGenerating,
  normalizeAdvicePayload,
  openAuditOnReady = true,
  queue,
  reportTerms,
  rpActiveId,
  rpAuditId: externalRpAuditId,
  rpList,
  rpLoaded,
  toast,
  unmarkReportGenerating,
}) {
  const rpAuditId = externalRpAuditId || ref('')
  const rpAuditPara1 = ref('')
  const rpAuditPara2 = ref('')
  const rpAuditImagingAdvice = ref('')
  const rpAuditOverallAdvice = ref('')
  const rpAuditRiskAdvice = ref('')
  const rpAuditTongueAdvice = ref('')
  const rpAuditStatus = ref('')
  const rpAuditVersion = ref(1)
  const rpAuditWasReviewed = ref(false)
  const rpFinalizing = ref(false)

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

  async function finalizeReport(reportId) {
    if (!reportId) return
    rpFinalizing.value = true
    try {
      if (!String(reportId || '').startsWith('r')) {
        await apiJson(`/api/b/reports/${reportId}/advice`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: rpAuditImagingAdvice.value,
            sections: currentAuditSections(),
            preserve_history: true
          })
        })
        const data = await apiJson(`/api/b/reports/${reportId}/advice/approve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: rpAuditImagingAdvice.value,
            summary: rpAuditOverallAdvice.value,
            sections: currentAuditSections()
          })
        })
        const r = rpList.value.find(x => x.id === reportId)
        if (r) {
          r.reportStatus = '已审核'
          r.aiStatus = '已完成'
          r.summary = rpAuditOverallAdvice.value
          r.aiReadSummary = rpAuditImagingAdvice.value
          r.flow = makeReportFlow(r.uploadAt, true)
        }
        rpAuditStatus.value = data.advice?.status || 'archived'
        rpAuditVersion.value = data.advice?.version || rpAuditVersion.value
        rpAuditWasReviewed.value = true
        rpLoaded.value = false
        await loadReports()
        await loadReportFollowupTask(reportId)
        return
      }
    } catch (e) {
      console.error('审核报告失败', e)
      if (!String(reportId || '').startsWith('r')) {
        toast?.show(e.message || '审核失败')
        return
      }
    } finally {
      rpFinalizing.value = false
    }

    try {
      const r = rpList.value.find(x => x.id === reportId)
      if (r) r.reportStatus = '已审核'
      rpAuditId.value = ''
    } finally {
      rpFinalizing.value = false
    }
  }

  async function generateReportForReportRow(r) {
    if (!r?.rawRecordId) {
      toast?.show('该患者还没有健康档案，请先建档后再生成报告')
      const patient = queue.value.find(p => p._apiId === r?.rawPatientId)
      if (patient) goRecord(patient)
      return
    }

    const generateKey = r.rawPatientId || r.id
    if (isReportGenerating(generateKey)) return
    markReportGenerating(generateKey)

    try {
      toast?.show('报告生成任务已提交，AI处理中...')
      const { completed } = await generateReportJob(r.rawRecordId)

      rpLoaded.value = false
      await loadReports()
      if (completed) {
        toast?.show('健康报告已生成，请审核确认')
      } else {
        toast?.show('报告仍在生成中，请稍后刷新查看')
      }
    } catch (e) {
      toast?.show(e.message || '生成健康报告失败')
    } finally {
      unmarkReportGenerating(generateKey)
    }
  }

  async function openReportRowPrimary(r) {
    if (!r) return
    if (r.isReportPlaceholder) {
      await generateReportForReportRow(r)
      return
    }
    if (openAuditOnReady) openAudit(r)
  }

  return {
    closeAudit,
    finalizeReport,
    generateReportForReportRow,
    openReportRowPrimary,
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
    rpFinalizing,
    showAuditFollowupNext,
  }
}
