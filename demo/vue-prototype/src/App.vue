<template>
  <RouterView v-if="isPublicPage" v-slot="{ Component }">
    <Suspense>
      <component :is="Component" />
      <template #fallback>
        <div class="route-loading">页面加载中...</div>
      </template>
    </Suspense>
  </RouterView>
  <AppShell v-else>
    <RouterView v-slot="{ Component }">
      <Suspense>
        <component :is="Component" />
        <template #fallback>
          <div class="route-loading in-shell">页面加载中...</div>
        </template>
      </Suspense>
    </RouterView>
  </AppShell>
</template>

<script setup>
import AppShell from './components/AppShell.vue'
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const isPublicPage = computed(() => ['login', 'followup-checkin'].includes(route.name))
</script>

<style scoped>
.route-loading{min-height:100vh;display:grid;place-items:center;background:#f3f6fb;color:#475569;font-size:14px;font-weight:850}
.route-loading.in-shell{min-height:100%;height:100%;background:#fff}
</style>
