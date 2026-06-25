<template>
  <div class="shell" :style="themeVars">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">医</div>
        <div class="brand-text">{{ scenario.brandTitle }}</div>
      </div>

      <nav class="nav" aria-label="主导航">
        <RouterLink v-if="canSeeOperatorNav" class="nav-item" :to="scenario.workspacePath">
          <span class="nav-ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19V5" />
              <path d="M8 12h12" />
              <path d="M8 7h12" />
              <path d="M8 17h12" />
            </svg>
          </span>
          <span class="nav-label">{{ scenario.workspaceLabel }}</span>
        </RouterLink>

        <RouterLink v-if="canSeeOperatorNav" class="nav-item" to="/analytics">
          <span class="nav-ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 13h6v8H3zM10 3h6v18h-6zM17 8h4v13h-4z" />
            </svg>
          </span>
          <span class="nav-label">工作台</span>
        </RouterLink>

        <RouterLink class="nav-item" to="/patient">
          <span class="nav-ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </span>
          <span class="nav-label">{{ scenario.navPatient }}</span>
        </RouterLink>

        <RouterLink v-if="canSeeDoctorWorkbench" class="nav-item" to="/doctor-workbench">
          <span class="nav-ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0-8 0" />
              <path d="M6 21v-2a6 6 0 0 1 12 0v2" />
              <path d="M12 11v6M9 14h6" />
            </svg>
          </span>
          <span class="nav-label">医生工作台</span>
        </RouterLink>

        <RouterLink v-if="canSeeDepartmentDashboard" class="nav-item" to="/department-dashboard">
          <span class="nav-ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 21h18" />
              <path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16" />
              <path d="M9 7h1M14 7h1M9 11h1M14 11h1M9 15h1M14 15h1" />
            </svg>
          </span>
          <span class="nav-label">科室看板</span>
        </RouterLink>

        <div v-if="showPatientSubnav" class="subnav" :aria-label="`${scenario.navPatient}二级标题`">
          <RouterLink class="subnav-item" :class="{ active: activeTab === 'queue' }" :to="{ path: '/patient', query: { tab: 'queue' } }">{{ scenario.queueLabel }}</RouterLink>
          <RouterLink v-if="canSeeOperatorNav" class="subnav-item" :class="{ active: activeTab === 'record' }" :to="{ path: '/patient', query: { tab: 'record' } }">{{ scenario.recordLabel }}</RouterLink>
          <RouterLink v-if="canSeeOperatorNav" class="subnav-item" :class="{ active: activeTab === 'review' }" :to="{ path: '/patient', query: { tab: 'review' } }">{{ scenario.reportLabel }}</RouterLink>
          <RouterLink v-if="canSeeOperatorNav" class="subnav-item" :class="{ active: activeTab === 'followup-plan' }" :to="{ path: '/patient', query: { tab: 'followup-plan' } }">随访任务下发</RouterLink>
          <RouterLink v-if="canSeeOperatorNav" class="subnav-item" :class="{ active: activeTab === 'follow' }" :to="{ path: '/patient', query: { tab: 'follow' } }">执行跟踪</RouterLink>
          <RouterLink v-if="canSeeOperatorNav" class="subnav-item" :class="{ active: activeTab === 'workflow' }" to="/followup-workflow">随访知识库与模板</RouterLink>
        </div>

        <RouterLink v-if="canSeeOperatorNav" class="nav-item" to="/ai-employee/overview">
          <span class="nav-ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="4" y="6" width="16" height="12" rx="3" />
              <path d="M8 6V4M16 6V4M9 12h.01M15 12h.01M10 16h4" />
            </svg>
          </span>
          <span class="nav-label">{{ aiEmployeeNavLabel }}</span>
        </RouterLink>

        <div v-if="showAiEmployeeSubnav" class="subnav" :aria-label="`${aiEmployeeNavLabel}二级标题`">
          <RouterLink v-for="item in aiEmployeeTabs" :key="item.key" class="subnav-item" :class="{ active: aiEmployeeTab === item.key }" :to="`/ai-employee/${item.key}`">{{ item.label }}</RouterLink>
        </div>

      </nav>

      <div class="sidebar-foot">
        <button class="ghost" type="button" @click="logout">退出登录</button>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div class="top-left">
          <div class="org-pill">当前机构：<b>{{ org }}</b><span class="chev">▾</span></div>
        </div>
        <div class="top-right">
          <div class="time-pill">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M8 2v3M16 2v3M3 9h18" />
              <path d="M5 6h14a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z" />
            </svg>
            {{ now }}
          </div>
          <button class="icon-btn" type="button" aria-label="通知">
            <span class="dot" aria-hidden="true"></span>
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 8a6 6 0 10-12 0c0 7-3 7-3 7h18s-3 0-3-7" />
              <path d="M13.7 21a2 2 0 01-3.4 0" />
            </svg>
          </button>
          <div class="user-pill">
            <span class="avatar" aria-hidden="true"></span>
            {{ user }} <span class="chev">▾</span>
          </div>
        </div>
      </header>

      <section class="content">
        <slot />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { getStoredScenario } from '../config/scenarios'

const router = useRouter()
const route = useRoute()
const scenario = computed(() => getStoredScenario())
const org = computed(() => localStorage.getItem('proto_org') || scenario.value.orgName)
const user = computed(() => localStorage.getItem('proto_user') || '管理员')
const role = computed(() => localStorage.getItem('proto_role') || '')
const canSeeOperatorNav = computed(() => !['doctor', 'department_director'].includes(role.value))
const canSeeDoctorWorkbench = computed(() => ['doctor', 'admin', 'system_admin'].includes(role.value) || !role.value)
const canSeeDepartmentDashboard = computed(() => ['department_director', 'admin', 'system_admin'].includes(role.value) || !role.value)

const now = new Date().toLocaleString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', hour12: false
}).replace(/\//g, '-')

const showPatientSubnav = computed(() => route.path.startsWith('/patient') || route.path.startsWith('/record') || route.path.startsWith('/followup-workflow'))
const activeTab = computed(() => {
  if (route.path.startsWith('/followup-workflow')) return 'workflow'
  return typeof route.query.tab === 'string' ? route.query.tab : 'queue'
})
const aiEmployeeNavLabel = computed(() => scenario.value.key === 'hospital' ? '医生IP打造' : 'AI超级员工')
const aiEmployeeTabs = computed(() => {
  if (scenario.value.key === 'hospital') {
    return [
      { key: 'overview', label: '数据看板' },
      { key: 'content', label: '内容科普' },
      { key: 'assets', label: '知识资产库' },
      { key: 'employees', label: '员工设备' },
    ]
  }
  return [
    { key: 'overview', label: '增长看板' },
    { key: 'channels', label: '引流获客' },
    { key: 'content', label: '内容营销' },
    { key: 'leads', label: '线索转化' },
    { key: 'assets', label: '知识资产库' },
    { key: 'employees', label: '员工设备' },
  ]
})
const showAiEmployeeSubnav = computed(() => route.path.startsWith('/ai-employee'))
const aiEmployeeTab = computed(() => {
  const raw = typeof route.params.section === 'string' ? route.params.section : 'overview'
  if (scenario.value.key === 'hospital' && ['channels', 'leads'].includes(raw)) return 'overview'
  return raw
})
const themeVars = computed(() => ({
  '--scenario-primary': scenario.value.theme?.primary || '#155eef',
  '--scenario-soft': scenario.value.theme?.soft || '#eef5ff',
  '--scenario-bg': scenario.value.theme?.bg || '#f3f6fb',
  '--scenario-accent': scenario.value.theme?.accent || '#16a34a',
}))

onMounted(() => {
  const v = localStorage.getItem('proto_org')
  if (!v || v === '平邑县中医院') {
    localStorage.setItem('proto_org', scenario.value.orgName)
  }
})

function logout() {
  localStorage.removeItem('proto_authed')
  localStorage.removeItem('proto_org')
  localStorage.removeItem('proto_org_type')
  localStorage.removeItem('proto_user_id')
  localStorage.removeItem('proto_role')
  localStorage.removeItem('proto_department_id')
  router.push('/login')
}
</script>

<style scoped>
.shell{height:100%;display:grid;grid-template-columns:180px minmax(0,1fr);background:var(--scenario-bg,#f3f6fb);color:#0f172a;overflow:hidden}
.sidebar{background:#fff;border-right:1px solid #e6edf7;display:flex;flex-direction:column;min-height:0}
.brand{display:flex;align-items:center;gap:10px;padding:16px 14px;border-bottom:1px solid #eef2f7}
.brand-mark{width:34px;height:34px;border-radius:10px;background:var(--scenario-primary,#155eef);color:#fff;display:grid;place-items:center;font-weight:950}
.brand-text{font-weight:950;color:#0f172a;font-size:13px;line-height:1.4}
.nav{padding:10px 6px;display:grid;gap:4px;overflow-y:auto;min-height:0}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:12px;color:#526175;text-decoration:none;font-weight:850;border-left:3px solid transparent}
.nav-ico{width:30px;height:30px;border-radius:10px;border:1px solid #e6edf7;background:#f1f5f9;display:grid;place-items:center;color:#64748b;flex-shrink:0}
.nav-item.router-link-active{background:var(--scenario-soft,#eef5ff);color:var(--scenario-primary,#155eef);border-left-color:var(--scenario-primary,#155eef)}
.nav-item.router-link-active .nav-ico{background:var(--scenario-soft,#e7f0ff);border-color:color-mix(in srgb,var(--scenario-primary,#155eef) 24%,#fff);color:var(--scenario-primary,#155eef)}
.nav-item:hover:not(.router-link-active){background:#f8fbff;color:var(--scenario-primary,#155eef)}
.subnav{margin:-2px 0 8px 40px;display:grid;gap:2px}
.subnav-item{padding:8px 10px;border-radius:10px;color:#64748b;text-decoration:none;font-weight:850}
.subnav-item:hover{background:#f8fbff;color:var(--scenario-primary,#155eef)}
.subnav-item.active{background:var(--scenario-soft,#eef5ff);color:var(--scenario-primary,#155eef)}
.sidebar-foot{margin-top:auto;padding:12px;flex-shrink:0}
.ghost{width:100%;height:36px;border-radius:12px;border:1px solid #e6edf7;background:#fff;color:#64748b;font-weight:900;cursor:pointer}

.main{display:flex;flex-direction:column;min-width:0;height:100%;overflow:hidden}
.topbar{height:56px;background:#fff;border-bottom:1px solid #e6edf7;display:flex;align-items:center;justify-content:space-between;padding:0 16px;gap:12px;flex-shrink:0}
.top-left{display:flex;align-items:center;gap:10px;min-width:0}
.org-pill{height:34px;border:1px solid color-mix(in srgb,var(--scenario-primary,#155eef) 22%,#d9e2ef);border-radius:12px;padding:0 12px;display:flex;align-items:center;gap:6px;color:#334155;background:var(--scenario-soft,#fff);font-weight:850;white-space:nowrap}
.top-right{display:flex;align-items:center;gap:10px}
.time-pill{height:34px;border:1px solid #d9e2ef;border-radius:12px;padding:0 12px;display:flex;align-items:center;gap:8px;color:#334155;background:#fff;font-weight:850;white-space:nowrap}
.icon-btn{position:relative;width:34px;height:34px;border-radius:12px;border:1px solid #e6edf7;background:#fff;display:grid;place-items:center;color:#64748b;cursor:pointer}
.icon-btn .dot{position:absolute;right:8px;top:8px;width:8px;height:8px;border-radius:50%;background:#ef4444;border:2px solid #fff}
.user-pill{height:34px;border:1px solid #d9e2ef;border-radius:12px;padding:0 12px;display:flex;align-items:center;gap:8px;color:#334155;background:#fff;font-weight:850;white-space:nowrap}
.avatar{width:18px;height:18px;border-radius:50%;background:var(--scenario-primary,#155eef)}
.chev{color:#94a3b8}
.content{flex:1;min-height:0;padding:16px 20px;background:linear-gradient(180deg,var(--scenario-bg,#fff) 0,#fff 180px);overflow-y:auto;overflow-x:hidden}
</style>
