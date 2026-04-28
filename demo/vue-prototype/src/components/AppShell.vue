<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">医</div>
        <div class="brand-text">医院多结节随访管理系统</div>
      </div>

      <nav class="nav" aria-label="主导航">
        <RouterLink class="nav-item" to="/analytics">
          <span class="nav-ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 13h6v8H3zM10 3h6v18h-6zM17 8h4v13h-4z" />
            </svg>
          </span>
          <span class="nav-label">运营看板</span>
        </RouterLink>

        <RouterLink class="nav-item" to="/patient">
          <span class="nav-ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          </span>
          <span class="nav-label">患者管理</span>
        </RouterLink>

        <div v-if="showPatientSubnav" class="subnav" aria-label="患者管理二级标题">
          <RouterLink class="subnav-item" :class="{ active: activeTab === 'queue' }" :to="{ path: '/patient', query: { tab: 'queue' } }">患者队列</RouterLink>
          <RouterLink class="subnav-item" :class="{ active: activeTab === 'record' }" :to="{ path: '/patient', query: { tab: 'record' } }">患者建档</RouterLink>
          <RouterLink class="subnav-item" :class="{ active: activeTab === 'review' }" :to="{ path: '/patient', query: { tab: 'review' } }">健康报告</RouterLink>
          <RouterLink class="subnav-item" :class="{ active: activeTab === 'followup-plan' }" :to="{ path: '/patient', query: { tab: 'followup-plan' } }">随访计划</RouterLink>
          <RouterLink class="subnav-item" :class="{ active: activeTab === 'follow' }" :to="{ path: '/patient', query: { tab: 'follow' } }">AI随访</RouterLink>
          <RouterLink class="subnav-item" :class="{ active: activeTab === 'abnormal' }" :to="{ path: '/patient', query: { tab: 'abnormal' } }">异常与复查</RouterLink>
        </div>

        <RouterLink class="nav-item" to="/rws">
          <span class="nav-ico" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19V5" />
              <path d="M8 12h12" />
              <path d="M8 7h12" />
              <path d="M8 17h12" />
            </svg>
          </span>
          <span class="nav-label">真实世界研究</span>
        </RouterLink>
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

const router = useRouter()
const route = useRoute()
const org = computed(() => localStorage.getItem('proto_org') || '齐鲁医院')
const user = computed(() => localStorage.getItem('proto_user') || '管理员')

const now = new Date().toLocaleString('zh-CN', {
  year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', hour12: false
}).replace(/\//g, '-')

const showPatientSubnav = computed(() => route.path.startsWith('/patient') || route.path.startsWith('/record'))
const activeTab = computed(() => (typeof route.query.tab === 'string' ? route.query.tab : 'queue'))

onMounted(() => {
  const v = localStorage.getItem('proto_org')
  if (!v || v === '平邑县中医院') {
    localStorage.setItem('proto_org', '齐鲁医院')
  }
})

function logout() {
  localStorage.removeItem('proto_authed')
  router.push('/login')
}
</script>

<style scoped>
.shell{height:100%;display:grid;grid-template-columns:180px minmax(0,1fr);background:var(--bg,#f3f6fb);color:#0f172a;overflow:hidden}
.sidebar{background:#fff;border-right:1px solid #e6edf7;display:flex;flex-direction:column;min-height:0}
.brand{display:flex;align-items:center;gap:10px;padding:16px 14px;border-bottom:1px solid #eef2f7}
.brand-mark{width:34px;height:34px;border-radius:10px;background:#155eef;color:#fff;display:grid;place-items:center;font-weight:950}
.brand-text{font-weight:950;color:#0f172a;font-size:13px;line-height:1.4}
.nav{padding:10px 6px;display:grid;gap:4px}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:12px;color:#526175;text-decoration:none;font-weight:850;border-left:3px solid transparent}
.nav-ico{width:30px;height:30px;border-radius:10px;border:1px solid #e6edf7;background:#f1f5f9;display:grid;place-items:center;color:#64748b;flex-shrink:0}
.nav-item.router-link-active{background:#eef5ff;color:#155eef;border-left-color:#155eef}
.nav-item.router-link-active .nav-ico{background:#e7f0ff;border-color:#cfe0ff;color:#155eef}
.nav-item:hover:not(.router-link-active){background:#f8fbff;color:#155eef}
.subnav{margin:-2px 0 8px 40px;display:grid;gap:2px}
.subnav-item{padding:8px 10px;border-radius:10px;color:#64748b;text-decoration:none;font-weight:850}
.subnav-item:hover{background:#f8fbff;color:#155eef}
.subnav-item.active{background:#eef5ff;color:#155eef}
.sidebar-foot{margin-top:auto;padding:12px}
.ghost{width:100%;height:36px;border-radius:12px;border:1px solid #e6edf7;background:#fff;color:#64748b;font-weight:900;cursor:pointer}

.main{display:flex;flex-direction:column;min-width:0;height:100%;overflow:hidden}
.topbar{height:56px;background:#fff;border-bottom:1px solid #e6edf7;display:flex;align-items:center;justify-content:space-between;padding:0 16px;gap:12px;flex-shrink:0}
.top-left{display:flex;align-items:center;gap:10px;min-width:0}
.org-pill{height:34px;border:1px solid #d9e2ef;border-radius:12px;padding:0 12px;display:flex;align-items:center;gap:6px;color:#334155;background:#fff;font-weight:850;white-space:nowrap}
.top-right{display:flex;align-items:center;gap:10px}
.time-pill{height:34px;border:1px solid #d9e2ef;border-radius:12px;padding:0 12px;display:flex;align-items:center;gap:8px;color:#334155;background:#fff;font-weight:850;white-space:nowrap}
.icon-btn{position:relative;width:34px;height:34px;border-radius:12px;border:1px solid #e6edf7;background:#fff;display:grid;place-items:center;color:#64748b;cursor:pointer}
.icon-btn .dot{position:absolute;right:8px;top:8px;width:8px;height:8px;border-radius:50%;background:#ef4444;border:2px solid #fff}
.user-pill{height:34px;border:1px solid #d9e2ef;border-radius:12px;padding:0 12px;display:flex;align-items:center;gap:8px;color:#334155;background:#fff;font-weight:850;white-space:nowrap}
.avatar{width:18px;height:18px;border-radius:50%;background:#155eef}
.chev{color:#94a3b8}
.content{flex:1;min-height:0;padding:16px 20px;background:#fff;overflow-y:auto;overflow-x:hidden}
</style>
