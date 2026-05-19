<template>
  <RouterView v-if="isPublicPage" />
  <AppShell v-else>
    <RouterView />
  </AppShell>
</template>

<script setup>
import AppShell from './components/AppShell.vue'
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const isPublicPage = computed(() => ['login', 'followup-checkin'].includes(route.name))
</script>
