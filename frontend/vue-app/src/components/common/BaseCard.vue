<template>
  <div class="base-card" :class="cardClass">
    <div v-if="$slots.header" class="base-card-header">
      <slot name="header"></slot>
    </div>
    <div class="base-card-body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="base-card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  hover: {
    type: Boolean,
    default: true
  },
  shadow: {
    type: String,
    default: 'md', // sm, md, lg, xl
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  }
})

const cardClass = computed(() => {
  return {
    'base-card-hover': props.hover,
    [`base-card-shadow-${props.shadow}`]: true
  }
})
</script>

<style scoped>
.base-card {
  background: var(--color-bg-primary, #ffffff);
  border-radius: var(--radius-xl, 16px);
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0, 0, 0, 0.08));
  transition: all var(--transition-base, 0.3s ease);
  overflow: hidden;
}

.base-card-shadow-sm {
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.base-card-shadow-md {
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0, 0, 0, 0.08));
}

.base-card-shadow-lg {
  box-shadow: var(--shadow-lg, 0 8px 24px rgba(0, 0, 0, 0.12));
}

.base-card-shadow-xl {
  box-shadow: var(--shadow-xl, 0 12px 32px rgba(0, 0, 0, 0.16));
}

.base-card-hover:hover {
  box-shadow: var(--shadow-lg, 0 8px 24px rgba(0, 0, 0, 0.12));
  transform: translateY(-2px);
}

.base-card-header {
  padding: var(--spacing-lg, 24px);
  border-bottom: 1px solid var(--color-border, #e2e8f0);
}

.base-card-body {
  padding: var(--spacing-lg, 24px);
}

.base-card-footer {
  padding: var(--spacing-lg, 24px);
  border-top: 1px solid var(--color-border, #e2e8f0);
  background: var(--color-bg-secondary, #f8fafc);
}
</style>

