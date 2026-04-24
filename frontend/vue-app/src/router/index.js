import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '../views/LoginView.vue'
import PatientsView from '../views/PatientsView.vue'
import PatientDetailView from '../views/PatientDetailView.vue'
import RecordFormViewNew from '../views/RecordFormView_New.vue'
import ReportViewView from '../views/ReportViewView.vue'
import WeChatView from '../views/WeChatView.vue'
import CustomersView from '../views/CustomersView.vue'
import KnowledgeView from '../views/KnowledgeView.vue'
// 多结节表单
import LungRecordFormView from '../views/LungRecordFormView.vue'
import ThyroidRecordFormView from '../views/ThyroidRecordFormView.vue'
import ThyroidLungFormView from '../views/ThyroidLungFormView.vue'
import BreastLungFormView from '../views/BreastLungFormView.vue'
import BreastThyroidFormView from '../views/BreastThyroidFormView.vue'
import TripleNoduleFormView from '../views/TripleNoduleFormView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/patients',
      name: 'patients',
      component: PatientsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/patients/:id',
      name: 'patient-detail',
      component: PatientDetailView,
      meta: { requiresAuth: true }
    },
    {
      path: '/records/new/:patientId',
      name: 'record-form',
      component: RecordFormViewNew,
      meta: { requiresAuth: true }
    },
    {
      path: '/reports/:id',
      name: 'report-view',
      component: ReportViewView,
      meta: { requiresAuth: true }
    },
    {
      path: '/wechat',
      name: 'wechat',
      component: WeChatView,
      meta: { requiresAuth: true }
    },
    {
      path: '/customers',
      name: 'customers',
      component: CustomersView,
      meta: { requiresAuth: true }
    },
    {
      path: '/knowledge',
      name: 'knowledge',
      component: KnowledgeView,
      meta: { requiresAuth: true }
    },
    // 多结节表单路由
    {
      path: '/records/lung/:patientId',
      name: 'lung-record',
      component: LungRecordFormView,
      meta: { requiresAuth: true }
    },
    {
      path: '/records/thyroid/:patientId',
      name: 'thyroid-record',
      component: ThyroidRecordFormView,
      meta: { requiresAuth: true }
    },
    {
      path: '/records/lung-thyroid/:patientId',
      name: 'lung-thyroid',
      component: ThyroidLungFormView,
      meta: { requiresAuth: true }
    },
    {
      path: '/records/breast-lung/:patientId',
      name: 'breast-lung',
      component: BreastLungFormView,
      meta: { requiresAuth: true }
    },
    {
      path: '/records/breast-thyroid/:patientId',
      name: 'breast-thyroid',
      component: BreastThyroidFormView,
      meta: { requiresAuth: true }
    },
    {
      path: '/records/triple/:patientId',
      name: 'triple-nodule',
      component: TripleNoduleFormView,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router

