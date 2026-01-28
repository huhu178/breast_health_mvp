import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: () => import('../views/ChatPage.vue'),
    meta: { title: 'AI健康咨询 - 乳腺健康管理' }
  },
  {
    path: '/save-report',
    name: 'SaveReport',
    component: () => import('../views/SaveReportPage.vue'),
    meta: { title: '保存报告 - 乳腺健康管理' }
  },
  {
    path: '/my-reports',
    name: 'MyReports',
    component: () => import('../views/MyReportsPage.vue'),
    meta: { title: '我的报告 - 乳腺健康管理' }
  },
  {
    path: '/report/:id',
    name: 'ReportDetail',
    component: () => import('../views/ReportDetailPage.vue'),
    meta: { title: '报告详情 - 乳腺健康管理' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '乳腺健康管理'
  
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    const patientCode = localStorage.getItem('patientCode')
    if (!patientCode) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  next()
})

export default router

