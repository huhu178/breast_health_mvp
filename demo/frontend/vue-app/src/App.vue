<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from './components/AppLayout.vue'

const route = useRoute()
const isLoginPage = computed(() => route.name === 'login')
</script>

<template>
  <div v-if="isLoginPage">
    <router-view />
  </div>
  <AppLayout v-else>
    <router-view />
  </AppLayout>
</template>
