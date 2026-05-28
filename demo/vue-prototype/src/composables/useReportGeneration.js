import { ref } from 'vue'

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function useReportGeneration({ apiJson }) {
  const reportGeneratingIds = ref(new Set())

  function isGenerating(id) {
    return reportGeneratingIds.value.has(id)
  }

  function markGenerating(id) {
    reportGeneratingIds.value = new Set([...reportGeneratingIds.value, id])
  }

  function unmarkGenerating(id) {
    const next = new Set(reportGeneratingIds.value)
    next.delete(id)
    reportGeneratingIds.value = next
  }

  async function generateReportJob(recordId) {
    const job = await apiJson('/api/b/reports/generate-jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ record_id: recordId }),
    })
    const jobId = job.job_id
    if (!jobId) throw new Error('报告生成任务未返回任务ID')

    let completed = false
    for (let attempt = 0; attempt < 90; attempt += 1) {
      await sleep(attempt < 10 ? 2000 : 5000)
      const statusData = await apiJson(`/api/b/reports/generate-jobs/${jobId}`)
      if (statusData.status === 'completed') {
        completed = true
        break
      }
      if (statusData.status === 'failed') {
        throw new Error(statusData.message || 'AI生成失败')
      }
    }
    return { jobId, completed }
  }

  return {
    generateReportJob,
    isGenerating,
    markGenerating,
    reportGeneratingIds,
    unmarkGenerating,
  }
}
