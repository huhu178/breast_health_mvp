<template>
  <span :class="badgeClass">
    <slot></slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary', // primary, success, warning, danger, info
    validator: (value) => ['primary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  size: {
    type: String,
    default: 'md', // sm, md, lg
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const badgeClass = computed(() => {
  return {
    'base-badge': true,
    [`base-badge-${props.variant}`]: true,
    [`base-badge-${props.size}`]: true
  }
})
</script>

<style scoped>
.base-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full, 9999px);
  font-weight: var(--font-weight-medium, 500);
}

.base-badge-sm {
  padding: 2px 8px;
  font-size: var(--font-size-xs, 12px);
}

.base-badge-md {
  padding: 4px 12px;
  font-size: var(--font-size-xs, 12px);
}

.base-badge-lg {
  padding: 6px 16px;
  font-size: var(--font-size-sm, 14px);
}

.base-badge-primary {
  background: rgba(30, 136, 229, 0.1);
  color: var(--color-primary, #1e88e5);
}

.base-badge-success {
  background: rgba(76, 175, 80, 0.1);
  color: var(--color-success, #4caf50);
}

.base-badge-warning {
  background: rgba(255, 152, 0, 0.1);
  color: var(--color-warning, #ff9800);
}

.base-badge-danger {
  background: rgba(244, 67, 54, 0.1);
  color: var(--color-danger, #f44336);
}

.base-badge-info {
  background: rgba(0, 172, 193, 0.1);
  color: var(--color-info, #00acc1);
}
</style>



