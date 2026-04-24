<template>
  <Teleport to="body">
    <div class="toast" :class="{ show: visible }" role="status" aria-live="polite">{{ message }}</div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
let timer = null

function show(text) {
  message.value = text
  visible.value = true
  clearTimeout(timer)
  timer = setTimeout(() => { visible.value = false }, 1700)
}

defineExpose({ show })
</script>

<style scoped>
.toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%) translateY(16px);background:#111827;color:#fff;padding:10px 16px;border-radius:8px;opacity:0;transition:.2s;pointer-events:none;z-index:9999;white-space:nowrap}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
