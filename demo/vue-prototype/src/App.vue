<template>
  <RouterView v-if="isLogin" />
  <AppShell v-else>
    <RouterView />
  </AppShell>
</template>

<script setup>
import AppShell from './components/AppShell.vue'
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const isLogin = computed(() => route.name === 'login')
</script>
