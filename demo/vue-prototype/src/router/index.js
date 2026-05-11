import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'
import QueueView from '../views/QueueView.vue'
import ReportView from '../views/ReportView.vue'
import ReviewView from '../views/ReviewView.vue'
import PushView from '../views/PushView.vue'
import FollowupView from '../views/FollowupView.vue'
import FollowupCheckinView from '../views/FollowupCheckinView.vue'
import FollowupWorkflowView from '../views/FollowupWorkflowView.vue'
import PatientManagementView from '../views/PatientManagementView.vue'
import RecordView from '../views/RecordView.vue'
import RwsView from '../views/RwsView.vue'
import ScenarioWorkspaceView from '../views/ScenarioWorkspaceView.vue'

const auth = { requiresAuth: true }

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/followup-checkin/:taskCode', name: 'followup-checkin', component: FollowupCheckinView },
    { path: '/analytics', name: 'analytics', component: AnalyticsView, meta: auth },
    { path: '/workbench', redirect: '/patient' },
    { path: '/queue', name: 'queue', component: QueueView, meta: auth },      // 兼容旧入口（不在主导航展示）
    { path: '/report', name: 'report', component: ReportView, meta: auth },   // 兼容旧入口（不在主导航展示）
    { path: '/review', name: 'review', component: ReviewView, meta: auth },   // 兼容旧入口（不在主导航展示）
    { path: '/push', name: 'push', component: PushView, meta: auth },         // 兼容旧入口（不在主导航展示）
    { path: '/followup', name: 'followup', component: FollowupView, meta: auth }, // 兼容旧入口（不在主导航展示）
    { path: '/followup-workflow', name: 'followup-workflow', component: FollowupWorkflowView, meta: auth },
    { path: '/stats', redirect: '/analytics' },      // 已合并到运营看板
    { path: '/patient', name: 'patient', component: PatientManagementView, meta: auth },
    { path: '/record', name: 'record', component: RecordView, meta: auth },
    { path: '/rws', name: 'rws', component: RwsView, meta: auth },
    { path: '/scenario-workspace', name: 'scenario-workspace', component: ScenarioWorkspaceView, meta: auth }
  ]
})

router.beforeEach((to) => {
  if (['login', 'followup-checkin'].includes(to.name)) return true
  if (to.meta?.requiresAuth) {
    const authed = localStorage.getItem('proto_authed') === 'true'
    if (!authed) return { name: 'login' }
  }
  return true
})

export default router
