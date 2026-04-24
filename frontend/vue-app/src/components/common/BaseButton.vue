<template>
  <button
    :class="buttonClass"
    :disabled="disabled"
    :type="type"
    @click="$emit('click', $event)"
  >
    <slot name="icon"></slot>
    <span v-if="$slots.default"><slot></slot></span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary', // primary, secondary, success, warning, danger, link
    validator: (value) => ['primary', 'secondary', 'success', 'warning', 'danger', 'link'].includes(value)
  },
  size: {
    type: String,
    default: 'md', // sm, md, lg
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'button'
  },
  block: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const buttonClass = computed(() => {
  return {
    'base-button': true,
    [`base-button-${props.variant}`]: true,
    [`base-button-${props.size}`]: true,
    'base-button-block': props.block,
    'base-button-disabled': props.disabled
  }
})
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm, 8px);
  border: none;
  border-radius: var(--radius-md, 10px);
  font-family: inherit;
  font-weight: var(--font-weight-medium, 500);
  cursor: pointer;
  transition: all var(--transition-base, 0.3s ease);
  white-space: nowrap;
  user-select: none;
}

.base-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

/* 尺寸 */
.base-button-sm {
  padding: 8px 16px;
  font-size: var(--font-size-xs, 12px);
}

.base-button-md {
  padding: 12px 24px;
  font-size: var(--font-size-sm, 14px);
}

.base-button-lg {
  padding: 14px 28px;
  font-size: var(--font-size-md, 16px);
}

/* 变体 */
.base-button-primary {
  background: linear-gradient(135deg, #1e88e5 0%, #00acc1 100%);
  color: white;
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.base-button-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0, 0, 0, 0.08));
}

.base-button-secondary {
  background: var(--color-bg-primary, #ffffff);
  color: var(--color-text-primary, #1e293b);
  border: 2px solid var(--color-border, #e2e8f0);
}

.base-button-secondary:hover:not(:disabled) {
  border-color: var(--color-primary, #1e88e5);
  color: var(--color-primary, #1e88e5);
  transform: translateY(-2px);
}

.base-button-success {
  background: var(--color-success, #4caf50);
  color: white;
}

.base-button-warning {
  background: var(--color-warning, #ff9800);
  color: white;
}

.base-button-danger {
  background: var(--color-danger, #f44336);
  color: white;
}

.base-button-link {
  background: none;
  color: var(--color-primary, #1e88e5);
  padding: 0;
  box-shadow: none;
}

.base-button-link:hover:not(:disabled) {
  text-decoration: underline;
  transform: none;
}

/* 块级按钮 */
.base-button-block {
  width: 100%;
}
</style>



