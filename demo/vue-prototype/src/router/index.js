import { createRouter, createWebHistory } from 'vue-router'

const auth = { requiresAuth: true }
const view = (name) => () => import(`../views/${name}.vue`)

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'login', component: view('LoginView') },
    { path: '/followup-checkin/:taskCode', name: 'followup-checkin', component: view('FollowupCheckinView') },
    { path: '/analytics', name: 'analytics', component: view('AnalyticsView'), meta: auth },
    { path: '/queue', name: 'queue', component: view('QueueView'), meta: auth },      // 兼容旧入口（不在主导航展示）
    { path: '/report', name: 'report', component: view('ReportView'), meta: auth },   // 兼容旧入口（不在主导航展示）
    { path: '/review', name: 'review', component: view('ReviewView'), meta: auth },   // 兼容旧入口（不在主导航展示）
    { path: '/push', name: 'push', component: view('PushView'), meta: auth },         // 兼容旧入口（不在主导航展示）
    { path: '/followup', name: 'followup', component: view('FollowupView'), meta: auth }, // 兼容旧入口（不在主导航展示）
    { path: '/followup-workflow', name: 'followup-workflow', component: view('FollowupWorkflowView'), meta: auth },
    { path: '/stats', redirect: '/analytics' },      // 已合并到工作台
    { path: '/patient', name: 'patient', component: view('PatientManagementView'), meta: auth },
    { path: '/doctor-workbench', name: 'doctor-workbench', component: view('DoctorWorkbenchView'), meta: auth },
    { path: '/department-dashboard', name: 'department-dashboard', component: view('DepartmentDashboardView'), meta: auth },
    { path: '/system', name: 'system', component: view('SystemManagementView'), meta: auth },
    { path: '/record', name: 'record', component: view('RecordView'), meta: auth },
    { path: '/ai-employee', redirect: '/ai-employee/overview' },
    { path: '/ai-employee/dashboard', redirect: '/ai-employee/overview' },
    { path: '/ai-employee/consultation', redirect: '/ai-employee/leads' },
    { path: '/ai-employee/conversation', redirect: '/ai-employee/leads' },
    { path: '/ai-employee/handoff', redirect: '/ai-employee/leads' },
    { path: '/ai-employee/:section', name: 'ai-employee', component: view('AiEmployeeView'), meta: auth },
    { path: '/rws', name: 'rws', component: view('RwsView'), meta: auth },
    { path: '/scenario-workspace', name: 'scenario-workspace', component: view('ScenarioWorkspaceView'), meta: auth }
  ]
})

router.beforeEach((to) => {
  if (['login', 'followup-checkin'].includes(to.name)) return true
  if (to.meta?.requiresAuth) {
    const authed = localStorage.getItem('proto_authed') === 'true'
    if (!authed) return { name: 'login' }
    const role = localStorage.getItem('proto_role') || ''
    if (to.name === 'analytics' && ['doctor', 'department_director'].includes(role)) return roleHome(role)
    if (to.name === 'doctor-workbench' && role !== 'doctor') return roleHome(role)
    if (to.name === 'department-dashboard' && role !== 'department_director') return roleHome(role)
    if (to.name === 'system' && !['system_admin', 'admin'].includes(role)) return roleHome(role)
    if (role === 'doctor' && ['patient', 'record', 'followup-workflow'].includes(to.name)) return roleHome(role)
    if (['rws', 'ai-employee', 'scenario-workspace'].includes(to.name) && !['system_admin', 'admin'].includes(role)) return roleHome(role)
  }
  return true
})

function roleHome(role) {
  if (role === 'doctor') return { name: 'doctor-workbench' }
  if (role === 'department_director') return { name: 'department-dashboard' }
  if (['system_admin', 'admin'].includes(role)) return { name: 'system' }
  return { name: 'analytics' }
}

export default router
