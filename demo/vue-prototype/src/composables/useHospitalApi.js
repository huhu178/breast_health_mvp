import { apiJson, apiPostJson } from '../utils/apiClient'

export function useHospitalApi() {
  const getDepartments = () => apiJson('/api/hospital/departments')
  const getDoctors = (departmentId) => {
    const q = departmentId ? `?department_id=${encodeURIComponent(departmentId)}` : ''
    return apiJson(`/api/hospital/doctors${q}`)
  }
  const getManagers = (departmentId) => {
    const q = departmentId ? `?department_id=${encodeURIComponent(departmentId)}` : ''
    return apiJson(`/api/hospital/managers${q}`)
  }
  const getPatients = (params = {}) => {
    const q = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') q.set(key, value)
    })
    return apiJson(`/api/hospital/patients${q.toString() ? `?${q}` : ''}`)
  }
  const getPatientDetail = (patientId) => apiJson(`/api/hospital/patients/${patientId}`)
  const updatePatient = (patientId, payload) => apiJson(`/api/hospital/patients/${patientId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  const saveReportFollowupAdviceDraft = (reportId, payload) => apiPostJson(`/api/hospital/health-reports/${reportId}/followup-advice/draft`, payload)
  const submitReportFollowupAdvice = (reportId, payload) => apiPostJson(`/api/hospital/health-reports/${reportId}/followup-advice/submit`, payload)
  const getReportFollowupAdvice = (reportId) => apiJson(`/api/hospital/health-reports/${reportId}/followup-advice`)
  const getDoctorSummary = () => apiJson('/api/hospital/doctor-workbench/summary')
  const getDoctorPatients = () => apiJson('/api/hospital/doctor-workbench/patients')
  const getDoctorPendingAdvice = () => apiJson('/api/hospital/doctor-workbench/pending-advice')
  const getDepartmentSummary = () => apiJson('/api/hospital/department-dashboard/summary')
  const getDepartmentDoctors = () => apiJson('/api/hospital/department-dashboard/doctors')
  const getDepartmentAbnormalPatients = () => apiJson('/api/hospital/department-dashboard/abnormal-patients')
  const getNoduleOverview = () => apiJson('/api/hospital/analytics/nodule-overview')
  const getAssistantOffline = (params = {}) => {
    const q = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') q.set(key, value)
    })
    return apiJson(`/api/hospital/assistant-workbench/offline${q.toString() ? `?${q}` : ''}`)
  }

  return {
    getDepartments,
    getDoctors,
    getManagers,
    getPatients,
    getPatientDetail,
    updatePatient,
    saveReportFollowupAdviceDraft,
    submitReportFollowupAdvice,
    getReportFollowupAdvice,
    getDoctorSummary,
    getDoctorPatients,
    getDoctorPendingAdvice,
    getDepartmentSummary,
    getDepartmentDoctors,
    getDepartmentAbnormalPatients,
    getNoduleOverview,
    getAssistantOffline,
  }
}
