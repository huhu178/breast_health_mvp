import { computed, ref, watch } from 'vue'

export function normalizeAdvicePayload(advice, fallback = {}) {
  const sections = advice?.sections || fallback.sections || {}
  return {
    version: advice?.version || fallback.version || 1,
    status: advice?.status || fallback.status || 'draft',
    updatedAt: advice?.updated_at || advice?.updatedAt || fallback.updatedAt || '',
    content: advice?.content || fallback.content || '',
    sections: {
      imaging_report_advice: sections.imaging_report_advice || advice?.content || fallback.content || '',
      overall_assessment: sections.overall_assessment || '',
      risk_assessment: sections.risk_assessment || '',
      tongue_conclusion: sections.tongue_conclusion || ''
    },
    history: (advice?.history || fallback.history || []).map((h, idx) => ({
      id: h.id || `${h.saved_at || h.savedAt || idx}-${h.version || idx}`,
      version: h.version || 1,
      status: h.status || 'draft',
      content: h.content || '',
      sections: h.sections || {},
      savedAt: h.saved_at || h.savedAt || ''
    }))
  }
}

function makeDefaultAdvice(p) {
  return {
    version: 1,
    status: 'draft',
    updatedAt: '',
    content: p?.aiReadSummary || p?.report?.summary || '',
    history: []
  }
}

export function usePatientWorkspace({
  activePatient,
  activePatientId,
  apiJson,
  createReportFollowupTask,
  defaultOwner,
  existingReportFollowupTask,
  formatDateInput,
  generateReportJob,
  goRecord,
  isReportGenerating,
  loadReports,
  markReportGenerating,
  nextFollowDateByCycle,
  noduleTypeLabel,
  rememberReportFollowupTasks,
  reportFollowupCreatingId,
  riskLevelLabel,
  riskToneFromLevel,
  rpLoaded,
  setSubTab,
  statusLabel,
  toast,
  unmarkReportGenerating,
}) {
  const adviceGenerating = ref(false)
  const tongueSubmitting = ref(false)
  const tongueSyncing = ref(false)

  function nowText() {
    return new Date().toLocaleString('zh-CN', { hour12: false })
  }

  function normalizeImagingReport(item) {
    return {
      id: item.id,
      name: item.file_name || item.name || '影像报告',
      size: item.file_size || item.size || 0,
      uploadedAt: item.uploaded_at || item.uploadedAt || '',
      uploader: item.uploader_name || item.uploaded_by || defaultOwner.value,
      type: item.file_type || item.type || 'file',
      backend: true
    }
  }

  function ensurePatientWorkflow(p) {
    if (!p || !p.id) return p
    p.profileNote = p.profileNote || '既往史、家族史、症状、体征信息待完善。'
    p.assets = p.assets || {}
    p.assets.imagingReports = Array.isArray(p.assets.imagingReports) ? p.assets.imagingReports : []
    p.tongueTask = p.tongueTask || null
    p.tongueH5Url = p.tongueH5Url || p.tongueTask?.h5_url || ''
    p.tongueMobileOpenUrl = p.tongueMobileOpenUrl || ''
    p.workspaceRecords = Array.isArray(p.workspaceRecords) ? p.workspaceRecords : []
    p.workspaceReports = Array.isArray(p.workspaceReports) ? p.workspaceReports : []
    p.workspacePlans = Array.isArray(p.workspacePlans) ? p.workspacePlans : []
    p.workspaceTasks = Array.isArray(p.workspaceTasks) ? p.workspaceTasks : []
    p.latestReport = p.latestReport || null
    p.adviceDraft = p.adviceDraft || makeDefaultAdvice(p)
    p.finalReport = p.finalReport || { content: '', archivedAt: '', version: '' }
    p.followPlan = p.followPlan || {
      cycle: p.planTask?.cycle || (p.riskTone === 'r' ? '3个月' : p.riskTone === 'o' ? '6个月' : '12个月'),
      channel: p.planTask?.channel || '小程序',
      note: `${p.nodules || '结节'}随访，关注分级、大小、症状变化和资料补充。`
    }
    p.managementLogs = Array.isArray(p.managementLogs) ? p.managementLogs : [
      { id: `${p.id}-log-1`, at: '建档后', by: p.owner || defaultOwner.value, action: '建立患者档案', note: p.nodules || '' },
      { id: `${p.id}-log-2`, at: '待处理', by: '系统', action: '等待报告意见审核', note: statusLabel(p) },
    ]
    return p
  }

  function buildProfileNote(records, fallback = '') {
    const list = Array.isArray(records) ? records : []
    const latest = list
      .slice()
      .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))[0]
    if (!latest) return fallback || '既往史、家族史、症状、体征信息待完善。'
    const fields = [
      latest.main_complaint,
      latest.medical_history,
      latest.past_history,
      latest.family_history,
      latest.symptoms,
      latest.physical_exam,
      latest.health_condition
    ].filter(Boolean)
    if (fields.length) return fields.join('\n')
    return fallback || `最近档案：${latest.record_code || latest.created_at || `#${latest.id}`}`
  }

  watch(
    () => activePatient.value?.id,
    () => ensurePatientWorkflow(activePatient.value),
    { immediate: true }
  )

  async function openPatientWorkspace(p) {
    if (p?.id && activePatientId) activePatientId.value = p.id
    const current = ensurePatientWorkflow(p || activePatient.value)
    setSubTab('detail')
    await hydratePatientWorkspace(current)
  }

  async function hydratePatientWorkspace(p) {
    if (!p?._apiId) return
    p.workspaceLoading = true
    try {
      const [detail, records, reports, plans, tasks] = await Promise.all([
        apiJson(`/api/b/patients/${p._apiId}`),
        apiJson(`/api/b/patients/${p._apiId}/records`),
        apiJson(`/api/b/reports?patient_id=${p._apiId}&per_page=20`),
        apiJson(`/api/b/followup/patient-plans?patient_id=${p._apiId}`),
        apiJson(`/api/b/followup/tasks?patient_id=${p._apiId}&per_page=50`)
      ])
      if (detail?.name) {
        p.name = detail.name || p.name
        p.gender = detail.gender || p.gender
        p.age = detail.age || p.age
        p.phone = detail.phone || p.phone
        p.phoneMasked = detail.phone ? detail.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : p.phoneMasked
        p.nodules = noduleTypeLabel(detail.nodule_type || p.noduleType)
        p.noduleType = detail.nodule_type || p.noduleType
        p.source = detail.source_channel || p.source
        p.department_id = detail.department_id ?? p.department_id
        p.departmentName = detail.department_name || p.departmentName || ''
        p.primary_doctor_id = detail.primary_doctor_id ?? p.primary_doctor_id
        p.primaryDoctorName = detail.primary_doctor_name || p.primaryDoctorName || ''
        p.owner = detail.primary_doctor_name || detail.manager_name || p.owner
        p.manager_id = detail.manager_id ?? p.manager_id
        p.managerName = detail.manager_name || p.managerName || ''
        p.wecomExternalUserid = detail.wecom_external_userid || p.wecomExternalUserid
        p.wecomUserid = detail.wecom_userid || p.wecomUserid
        p.wecomBindStatus = detail.wecom_bind_status || p.wecomBindStatus
        p.profileNote = buildProfileNote(detail.health_records || records, p.profileNote)
      }
      p.workspaceRecords = (Array.isArray(records) ? records : [])
        .slice()
        .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
      p.workspaceReports = (reports.reports || reports.items || [])
        .slice()
        .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
      p.workspacePlans = (Array.isArray(plans) ? plans : [])
        .slice()
        .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
      p.workspaceTasks = (tasks.items || tasks || [])
        .slice()
        .sort((a, b) => String(b.scheduled_send_at || b.due_at || b.created_at || '').localeCompare(String(a.scheduled_send_at || a.due_at || a.created_at || '')))
      rememberReportFollowupTasks(p.workspaceTasks)

      const latestRecord = p.workspaceRecords[0]
      if (latestRecord?.id) {
        p.workspaceRecordId = latestRecord.id
        p.latestReport = latestRecord.latest_report || null
        const imaging = await apiJson(`/api/b/records/${latestRecord.id}/imaging-reports`)
        p.assets.imagingReports = (imaging.items || []).map(normalizeImagingReport)
        const tongue = await apiJson(`/api/b/tongue-diagnosis/tasks/by-record/${latestRecord.id}`)
        p.tongueTask = (tongue.items || [])[0] || null
        p.tongueH5Url = p.tongueTask?.h5_url || p.tongueH5Url || ''
        p.tongueMobileOpenUrl = p.tongueTask?.mobile_open_url || p.tongueMobileOpenUrl || ''
      }

      const latestReport = p.workspaceReports[0]
      if (latestReport?.id) {
        p.workspaceReportId = latestReport.id
        p.latestReport = {
          id: latestReport.id,
          report_code: latestReport.report_code,
          status: latestReport.status,
          risk_level: latestReport.risk_level,
          report_summary: latestReport.report_summary,
          imaging_conclusion: latestReport.imaging_conclusion,
          reviewed_at: latestReport.reviewed_at,
          created_at: latestReport.created_at,
          updated_at: latestReport.updated_at
        }
        p.risk = riskLevelLabel(latestReport.risk_level || p.risk)
        p.riskTone = riskToneFromLevel(latestReport.risk_level || p.risk)
        try {
          const followupAdvice = await apiJson(`/api/hospital/health-reports/${latestReport.id}/followup-advice`)
          p.workspaceReportFollowupAdvices = followupAdvice.advices || []
          const latestFollowupAdvice = p.workspaceReportFollowupAdvices[0]
          p.reportFollowupAdviceDraft = latestFollowupAdvice?.advice_content || p.reportFollowupAdviceDraft || ''
          p.reportFollowupAdviceNextAt = latestFollowupAdvice?.suggested_next_followup_at || p.reportFollowupAdviceNextAt || ''
        } catch (e) {
          p.workspaceReportFollowupAdvices = p.workspaceReportFollowupAdvices || []
        }
        const advice = await apiJson(`/api/b/reports/${latestReport.id}/advice`)
        p.adviceDraft = normalizeAdvicePayload(advice.advice, p.adviceDraft)
        if (latestReport.status === 'finalized' || latestReport.status === 'published' || p.adviceDraft.status === 'archived') {
          p.finalReport = {
            content: p.adviceDraft.content || latestReport.imaging_conclusion || latestReport.report_summary || '',
            archivedAt: latestReport.reviewed_at || p.adviceDraft.updatedAt || '',
            version: p.adviceDraft.version || 1
          }
          p.stage = 'plan'
        }
      }
    } catch (e) {
      console.error('加载患者工作台失败', e)
    } finally {
      p.workspaceLoading = false
    }
  }

  async function generateReportForPatient(p) {
    const patient = ensurePatientWorkflow(p || activePatient.value)
    if (!patient?._apiId) {
      toast?.show('请先保存患者信息后再生成报告')
      return
    }
    if (isReportGenerating(patient.id)) return

    markReportGenerating(patient.id)
    try {
      if (!patient.workspaceRecordId) {
        await hydratePatientWorkspace(patient)
      }
      if (!patient.workspaceRecordId) {
        toast?.show('请先完成患者建档，再生成健康报告')
        goRecord(patient)
        return
      }

      toast?.show('报告生成任务已提交，AI处理中...')
      const { completed } = await generateReportJob(patient.workspaceRecordId)

      rpLoaded.value = false
      await hydratePatientWorkspace(patient)
      await loadReports()
      if (completed) {
        patient.stage = 'review'
        toast?.show('健康报告已生成，请到健康报告审核中确认')
        setSubTab('review')
      } else {
        toast?.show('报告仍在生成中，请稍后到健康报告审核查看')
      }
    } catch (e) {
      toast?.show(e.message || '生成健康报告失败')
    } finally {
      unmarkReportGenerating(patient.id)
    }
  }

  const activeAdvice = computed(() => {
    const p = ensurePatientWorkflow(activePatient.value)
    return p?.adviceDraft || makeDefaultAdvice(p)
  })

  function updateActivePatientField({ field, value }) {
    if (!field) return
    const p = ensurePatientWorkflow(activePatient.value)
    if (!p) return
    p[field] = value
  }

  function updateActiveAdviceContent(value) {
    const p = ensurePatientWorkflow(activePatient.value)
    if (!p) return
    p.adviceDraft = p.adviceDraft || makeDefaultAdvice(p)
    p.adviceDraft.content = value
  }

  function updateReportFollowupAdvice({ field, value }) {
    const p = ensurePatientWorkflow(activePatient.value)
    if (!p) return
    if (field === 'suggested_next_followup_at') p.reportFollowupAdviceNextAt = value
    else p.reportFollowupAdviceDraft = value
  }

  async function saveReportFollowupAdviceDraft() {
    return saveReportFollowupAdvice('draft')
  }

  async function submitReportFollowupAdvice() {
    return saveReportFollowupAdvice('submitted')
  }

  async function saveReportFollowupAdvice(status = 'draft') {
    const p = ensurePatientWorkflow(activePatient.value)
    if (!p?.workspaceReportId) {
      toast?.show('请先生成健康报告')
      return null
    }
    const payload = {
      advice_content: p.reportFollowupAdviceDraft || '',
      suggested_next_followup_at: p.reportFollowupAdviceNextAt || ''
    }
    const url = `/api/hospital/health-reports/${p.workspaceReportId}/followup-advice/${status === 'submitted' ? 'submit' : 'draft'}`
    try {
      const data = await apiJson(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const advice = data.advice
      if (advice) {
        p.workspaceReportFollowupAdvices = [
          advice,
          ...(p.workspaceReportFollowupAdvices || []).filter((item) => item.id !== advice.id)
        ]
      }
      toast?.show(status === 'submitted' ? '报告随访建议已提交' : '报告随访建议草稿已保存')
      return advice
    } catch (e) {
      toast?.show(e.message || '保存报告随访建议失败')
      return null
    }
  }

  const adviceLocked = computed(() => {
    const p = ensurePatientWorkflow(activePatient.value)
    const status = p?.adviceDraft?.status
    const reportStatus = p?.latestReport?.status
    return !!p?.finalReport?.content || ['archived', 'approved'].includes(status) || ['finalized', 'published', 'archived'].includes(reportStatus)
  })

  const workspaceTongueActionLabel = computed(() => {
    const task = activePatient.value?.tongueTask
    if (task?.status === 'h5_sso_created') return '重新打开舌诊 H5'
    if (task?.status === 'completed') return '已完成舌诊'
    return '打开舌诊 H5'
  })

  const workspaceTongueStatusLabel = computed(() => {
    const status = activePatient.value?.tongueTask?.status
    const map = {
      h5_sso_created: 'H5已生成',
      completed: '舌诊已完成',
      failed: '检测失败',
      waiting_inquiry: '待完成'
    }
    return map[status] || status || ''
  })

  const workspaceTongueQrUrl = computed(() => {
    const url = activePatient.value?.tongueMobileOpenUrl || activePatient.value?.tongueH5Url || ''
    if (!url) return ''
    return `https://api.qrserver.com/v1/create-qr-code/?size=180x180&margin=8&data=${encodeURIComponent(url)}`
  })

  function adviceStatusLabel(status) {
    const map = {
      draft: '草稿',
      reviewing: '待审核',
      approved: '审核通过',
      archived: '已写入最终报告',
    }
    return map[status] || '草稿'
  }

  const patientFlowSteps = computed(() => {
    const p = ensurePatientWorkflow(activePatient.value)
    const adviceStatus = p?.adviceDraft?.status || 'draft'
    const hasFinal = !!p?.finalReport?.content
    const hasPlan = !!p?.followPlan?.note
    const nodes = [
      { key: 'archive', no: 1, label: '档案' },
      { key: 'risk', no: 2, label: '评估' },
      { key: 'advice', no: 3, label: '建议' },
      { key: 'review', no: 4, label: '审核' },
      { key: 'final', no: 5, label: '最终报告' },
      { key: 'follow', no: 6, label: '随访管理' },
    ]
    const current = hasFinal && hasPlan ? 5 : hasFinal ? 4 : adviceStatus === 'reviewing' ? 3 : 2
    return nodes.map((n, idx) => ({ ...n, state: idx < current ? 'done' : idx === current ? 'current' : 'todo' }))
  })

  const computedRisk = computed(() => {
    const p = activePatient.value || {}
    if (p.riskTone === 'r' || p.risk === '高风险') return { level: '高风险', tone: 'r' }
    if (p.riskTone === 'o' || p.risk === '中风险') return { level: '中风险', tone: 'o' }
    if (p.riskTone === 'g' || p.risk === '低风险') return { level: '低风险', tone: 'g' }
    return { level: '待评估', tone: 'g' }
  })

  const riskLayerItems = computed(() => {
    const p = ensurePatientWorkflow(activePatient.value)
    const completenessRisk = (p.assets?.imagingReports || []).length ? { level: '资料较完整', tone: 'g' } : { level: '资料缺口', tone: 'o' }
    const tongueRisk = p.tongueTask?.status === 'completed'
      ? { level: '舌诊已回流', tone: 'g' }
      : p.tongueH5Url
        ? { level: 'H5链接已生成', tone: 'g' }
        : { level: '待生成手机链接', tone: 'o' }
    return [
      { key: 'nodule', label: '结节分层', level: computedRisk.value.level, tone: computedRisk.value.tone, reason: `${p.nodules || '结节'}当前标记为${computedRisk.value.level}，需结合分级、大小、数量和症状复核。` },
      { key: 'material', label: '资料完整度', level: completenessRisk.level, tone: completenessRisk.tone, reason: (p.assets?.imagingReports || []).length ? '已上传影像报告，可进入报告解析/复核。' : '缺少原始影像报告，AI只能基于表单生成初步建议。' },
      { key: 'history', label: '病史风险', level: p.profileNote?.includes('家族') ? '需关注' : '常规', tone: p.profileNote?.includes('家族') ? 'o' : 'g', reason: p.profileNote || '病史信息待完善。' },
      { key: 'tongue', label: '舌诊资料', level: tongueRisk.level, tone: tongueRisk.tone, reason: 'B端生成手机H5链接，由患者手机或健康管理师手机完成采集；结果回流后写入档案和报告。' },
    ]
  })

  function addManagementLog(action, note = '') {
    const p = ensurePatientWorkflow(activePatient.value)
    p.managementLogs = p.managementLogs || []
    p.managementLogs.unshift({ id: `${Date.now()}-${Math.random()}`, at: nowText(), by: p.owner || defaultOwner.value, action, note })
  }

  async function handleImagingUpload(event) {
    const p = ensurePatientWorkflow(activePatient.value)
    const files = Array.from(event.target.files || [])
    if (!files.length) return
    try {
      if (p.workspaceRecordId) {
        const form = new FormData()
        files.forEach(file => form.append('imaging_reports', file))
        const data = await apiJson(`/api/b/records/${p.workspaceRecordId}/imaging-reports`, { method: 'POST', body: form })
        const existing = (p.assets.imagingReports || []).filter(x => !x.backend)
        p.assets.imagingReports = [...(data.items || []).map(normalizeImagingReport), ...existing]
      } else {
        files.forEach(file => {
          p.assets.imagingReports.unshift({
            id: `${Date.now()}-${file.name}-${Math.random()}`,
            name: file.name,
            size: file.size,
            uploadedAt: nowText(),
            uploader: p.owner || defaultOwner.value,
            type: file.type || 'file'
          })
        })
      }
      addManagementLog('上传影像报告', files.map(f => f.name).join('、'))
    } catch (e) {
      toast?.show(e.message || '影像报告上传失败')
    } finally {
      event.target.value = ''
    }
  }

  async function startWorkspaceTongueDiagnosis() {
    const p = ensurePatientWorkflow(activePatient.value)
    if (!p._apiId || !p.workspaceRecordId) {
      toast?.show('请先保存患者档案，再发起舌诊')
      return
    }
    tongueSubmitting.value = true
    try {
      const data = await apiJson('/api/b/tongue-diagnosis/h5-sso', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: p._apiId, record_id: p.workspaceRecordId })
      })
      p.tongueTask = data.task
      p.tongueH5Url = data.h5_url || data.task?.h5_url || ''
      p.tongueMobileOpenUrl = data.mobile_open_url || ''
      addManagementLog('打开舌诊H5', data.task?.out_id || '')
      if (p.tongueH5Url) window.open(p.tongueH5Url, '_blank', 'noopener')
      toast?.show('手机舌诊链接已生成')
    } catch (e) {
      toast?.show(e.message || 'H5舌诊打开失败')
    } finally {
      tongueSubmitting.value = false
    }
  }

  async function copyWorkspaceTongueLink() {
    const url = activePatient.value?.tongueMobileOpenUrl || activePatient.value?.tongueH5Url || ''
    if (!url) return
    try {
      await navigator.clipboard.writeText(url)
      toast?.show('舌诊链接已复制')
    } catch (e) {
      toast?.show('复制失败，请手动选择链接')
    }
  }

  async function syncWorkspaceTongueReport() {
    const p = ensurePatientWorkflow(activePatient.value)
    const taskId = p.tongueTask?.id
    if (!taskId) {
      toast?.show('请先生成舌诊H5链接')
      return
    }
    tongueSyncing.value = true
    try {
      const data = await apiJson(`/api/b/tongue-diagnosis/tasks/${taskId}/sync-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      p.tongueTask = data.task || p.tongueTask
      p.tongueH5Url = p.tongueTask?.h5_url || p.tongueH5Url || ''
      p.tongueMobileOpenUrl = p.tongueTask?.mobile_open_url || p.tongueMobileOpenUrl || ''
      addManagementLog('同步舌诊结果', p.tongueTask?.status || '')
      toast?.show(p.tongueTask?.tongue_feature ? '舌诊结果已同步' : '暂未查询到舌诊报告')
    } catch (e) {
      toast?.show(e.message || '舌诊结果同步失败')
    } finally {
      tongueSyncing.value = false
    }
  }

  async function removeAsset(type, id) {
    const p = ensurePatientWorkflow(activePatient.value)
    const hit = (p.assets[type] || []).find(x => x.id === id)
    if (type === 'imagingReports' && hit?.backend && p.workspaceRecordId) {
      try {
        await apiJson(`/api/b/records/${p.workspaceRecordId}/imaging-reports/${id}`, { method: 'DELETE' })
      } catch (e) {
        toast?.show(e.message || '删除影像报告失败')
        return
      }
    }
    p.assets[type] = (p.assets[type] || []).filter(x => x.id !== id)
    addManagementLog('删除资料', type)
  }

  async function regenerateAdviceForActive() {
    const p = ensurePatientWorkflow(activePatient.value)
    if (adviceLocked.value) {
      toast?.show('最终报告已归档，不能再次生成建议')
      return
    }
    adviceGenerating.value = true
    try {
      const previous = p.adviceDraft.content
      if (previous) {
        p.adviceDraft.history = p.adviceDraft.history || []
        p.adviceDraft.history.unshift({
          id: `${Date.now()}-${p.adviceDraft.version}`,
          version: p.adviceDraft.version || 1,
          status: p.adviceDraft.status || 'draft',
          content: previous,
          savedAt: p.adviceDraft.updatedAt || nowText()
        })
      }
      p.adviceDraft.version = (p.adviceDraft.version || 1) + 1
      p.adviceDraft.status = 'draft'
      p.adviceDraft.updatedAt = nowText()
      p.adviceDraft.content = `基于${p.name}当前档案，${p.nodules}建议按${computedRisk.value.level}路径管理。请补充原始影像报告，结合分级、大小、症状、病史进行复核；若分级不清或资料缺失，应优先完善检查资料后再形成最终报告。随访建议：${p.followPlan?.cycle || '6个月'}复查，通过${p.followPlan?.channel || '小程序'}进行提醒和记录。`
      if (p.workspaceReportId) {
        const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: p.adviceDraft.content, preserve_history: true })
        })
        p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
      }
      addManagementLog('再次生成建议草稿', `V${p.adviceDraft.version}`)
    } catch (e) {
      toast?.show(e.message || '再次生成建议失败')
    } finally {
      adviceGenerating.value = false
    }
  }

  async function saveAdviceDraft() {
    const p = ensurePatientWorkflow(activePatient.value)
    if (adviceLocked.value) {
      toast?.show('最终报告已归档，不能编辑建议')
      return false
    }
    if (!String(p.adviceDraft.content || '').trim()) {
      toast?.show('请先生成或填写建议内容')
      return false
    }
    if (p.workspaceReportId) {
      try {
        const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: p.adviceDraft.content, preserve_history: true })
        })
        p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
      } catch (e) {
        toast?.show(e.message || '保存建议草稿失败')
        return false
      }
    }
    p.adviceDraft.status = 'draft'
    p.adviceDraft.updatedAt = nowText()
    addManagementLog('保存建议草稿', `V${p.adviceDraft.version || 1}`)
    return true
  }

  async function submitAdviceReview() {
    const p = ensurePatientWorkflow(activePatient.value)
    if (adviceLocked.value) {
      toast?.show('最终报告已归档，不能再次提交审核')
      return
    }
    if (!String(p.adviceDraft.content || '').trim()) {
      toast?.show('请先生成或填写建议内容')
      return
    }
    if (p.workspaceReportId) {
      try {
        const saved = await saveAdviceDraft()
        if (!saved) return
        const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice/submit-review`, { method: 'POST' })
        p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
      } catch (e) {
        toast?.show(e.message || '提交建议审核失败')
        return
      }
    }
    p.adviceDraft.status = 'reviewing'
    p.adviceDraft.updatedAt = nowText()
    p.stage = 'review'
    addManagementLog('提交建议审核', `V${p.adviceDraft.version || 1}`)
  }

  async function approveAdviceToFinal() {
    const p = ensurePatientWorkflow(activePatient.value)
    if (adviceLocked.value) {
      toast?.show('最终报告已归档')
      return
    }
    if (p.adviceDraft.status !== 'reviewing') return
    if (p.workspaceReportId) {
      try {
        const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice/approve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: p.adviceDraft.content, summary: p.report?.summary || '' })
        })
        p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
      } catch (e) {
        toast?.show(e.message || '审核通过失败')
        return
      }
    }
    p.adviceDraft.status = 'archived'
    p.finalReport = {
      content: p.adviceDraft.content,
      archivedAt: nowText(),
      version: p.adviceDraft.version || 1
    }
    p.stage = 'plan'
    addManagementLog('审核通过并写入最终报告', `V${p.adviceDraft.version || 1}`)
    rpLoaded.value = false
    await hydratePatientWorkspace(p)
  }

  async function createFirstFollowupTaskForActive(reportId = null) {
    const p = ensurePatientWorkflow(activePatient.value)
    const targetReportId = reportId || p.workspaceReportId || p.latestReport?.id
    if (!targetReportId) {
      toast?.show('请先生成并审核健康报告')
      return
    }
    if (existingReportFollowupTask(targetReportId, p)) {
      toast?.show('该报告已存在首次随访任务')
      return
    }
    reportFollowupCreatingId.value = String(targetReportId)
    try {
      const task = await createReportFollowupTask(targetReportId)
      p.workspaceTasks = [task, ...(p.workspaceTasks || [])]
      addManagementLog('创建首次随访任务', `${task.title || '报告后首次随访'} · ${task.due_at || '待排期'}`)
      toast?.show('已创建报告后首次随访任务')
      await hydratePatientWorkspace(p)
    } catch (e) {
      if (e.status === 409) {
        toast?.show('该报告已存在随访任务')
        await hydratePatientWorkspace(p)
      } else {
        toast?.show(e.message || '创建首次随访任务失败')
      }
    } finally {
      reportFollowupCreatingId.value = ''
    }
  }

  function updateActiveFollowPlan({ field, value }) {
    if (!field) return
    const p = ensurePatientWorkflow(activePatient.value)
    if (!p) return
    p.followPlan = p.followPlan || {}
    p.followPlan[field] = value
  }

  async function saveFollowPlan() {
    const p = ensurePatientWorkflow(activePatient.value)
    if (!p?._apiId) {
      toast?.show('请先保存患者信息后再保存任务配置')
      return
    }
    try {
      const data = await apiJson(`/api/b/patients/${p._apiId}/follow-ups`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          follow_up_type: p.followPlan.channel || '小程序',
          follow_up_date: formatDateInput(new Date()),
          content: p.followPlan.note || '',
          next_follow_up_date: nextFollowDateByCycle(p.followPlan.cycle),
          next_follow_up_action: `${p.followPlan.cycle || '6个月'}复查；${p.followPlan.channel || '小程序'}触达`
        })
      })
      p.followPlan.savedAt = data.created_at || nowText()
      p.followPlan.backendId = data.id
      p.stage = p.finalReport?.content ? 'follow' : 'plan'
      addManagementLog('保存任务配置', `${p.followPlan.cycle} · ${p.followPlan.channel}`)
      toast?.show('任务配置已保存')
    } catch (e) {
      toast?.show(e.message || '保存任务配置失败')
    }
  }

  return {
    activeAdvice,
    addManagementLog,
    adviceGenerating,
    adviceLocked,
    adviceStatusLabel,
    approveAdviceToFinal,
    computedRisk,
    copyWorkspaceTongueLink,
    createFirstFollowupTaskForActive,
    ensurePatientWorkflow,
    generateReportForPatient,
    handleImagingUpload,
    hydratePatientWorkspace,
    openPatientWorkspace,
    patientFlowSteps,
    regenerateAdviceForActive,
    removeAsset,
    riskLayerItems,
    saveAdviceDraft,
    saveFollowPlan,
    startWorkspaceTongueDiagnosis,
    submitAdviceReview,
    syncWorkspaceTongueReport,
    tongueSubmitting,
    tongueSyncing,
    updateActiveAdviceContent,
    updateActiveFollowPlan,
    updateActivePatientField,
    updateReportFollowupAdvice,
    saveReportFollowupAdviceDraft,
    submitReportFollowupAdvice,
    workspaceTongueActionLabel,
    workspaceTongueQrUrl,
    workspaceTongueStatusLabel,
  }
}
