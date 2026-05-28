import { ref } from 'vue'

export function useReportViewer({
  apiJson,
  buildReportPreviewHtml,
  reportDbStatusLabel,
  rpAuditPara1,
  rpAuditPara2,
  rpList,
  toast,
}) {
  const rpViewHtml = ref('')
  const rpViewVisible = ref(false)

  async function viewReport(reportId) {
    const mockReport = rpList.value.find((report) => report.id === reportId)
    if (mockReport?.isReportPlaceholder || String(reportId || '').startsWith('patient-')) {
      toast?.show('该患者尚未生成健康报告，请先点击“去生成”')
      return
    }
    try {
      const data = await apiJson(`/api/b/reports/${reportId}`)
      const html = data.report_html || data.final_report_html || ''
      if (html) {
        rpViewHtml.value = html
        rpViewVisible.value = true
        return
      }
      if (data.imaging_conclusion || data.report_summary || data.summary || data.advice_draft) {
        rpViewHtml.value = buildReportPreviewHtml(data, reportId, reportDbStatusLabel)
        rpViewVisible.value = true
        return
      }
      toast?.show('报告详情暂未生成可查看内容')
    } catch (e) {
      if (!mockReport) {
        toast?.show(e.message || '查看报告失败')
        return
      }
    }
    if (mockReport) {
      rpViewHtml.value = buildReportPreviewHtml({
        report_code: mockReport.reportNo || mockReport.id,
        status: mockReport.reportStatus,
        patient: { name: mockReport.name },
        nodule_type: mockReport.noduleType,
        risk_level: mockReport.risk,
        report_summary: rpAuditPara1.value || mockReport.summary || '',
        imaging_conclusion: rpAuditPara2.value || mockReport.aiReadSummary || '',
        created_at: mockReport.uploadAt,
      }, reportId, reportDbStatusLabel)
      rpViewVisible.value = true
    }
  }

  function downloadReport(reportId) {
    const row = rpList.value.find((report) => report.id === reportId)
    if (row?.isReportPlaceholder || String(reportId || '').startsWith('patient-')) {
      toast?.show('该患者尚未生成健康报告，暂不能下载')
      return
    }
    if (!reportId || String(reportId).startsWith('r')) {
      toast?.show('示例报告暂无可下载文件')
      return
    }
    window.open(`/api/b/reports/${reportId}/export-pdf`, '_blank')
  }

  function closeReportView() {
    rpViewVisible.value = false
  }

  return {
    closeReportView,
    downloadReport,
    rpViewHtml,
    rpViewVisible,
    viewReport,
  }
}
