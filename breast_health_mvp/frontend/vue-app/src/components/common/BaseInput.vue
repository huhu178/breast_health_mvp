<template>
  <div class="base-input-group">
    <label v-if="label" :for="inputId" class="base-input-label">
      {{ label }}
      <span v-if="required" class="base-input-required">*</span>
    </label>
    <input
      :id="inputId"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="inputClass"
      @input="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('blur', $event)"
      @focus="$emit('focus', $event)"
    />
    <div v-if="error" class="base-input-error">{{ error }}</div>
    <div v-if="hint" class="base-input-hint">{{ hint }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md', // sm, md, lg
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const inputClass = computed(() => {
  return {
    'base-input': true,
    [`base-input-${props.size}`]: true,
    'base-input-error-state': !!props.error,
    'base-input-disabled': props.disabled
  }
})
</script>

<style scoped>
.base-input-group {
  margin-bottom: var(--spacing-lg, 24px);
}

.base-input-label {
  display: block;
  margin-bottom: var(--spacing-sm, 8px);
  font-size: var(--font-size-sm, 14px);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--color-text-primary, #1e293b);
}

.base-input-required {
  color: var(--color-danger, #f44336);
  margin-left: 4px;
}

.base-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--color-border, #e2e8f0);
  border-radius: var(--radius-md, 10px);
  font-size: var(--font-size-sm, 14px);
  font-family: inherit;
  color: var(--color-text-primary, #1e293b);
  background: var(--color-bg-primary, #ffffff);
  transition: all var(--transition-base, 0.3s ease);
}

.base-input:focus {
  outline: none;
  border-color: var(--color-primary, #1e88e5);
  box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.12);
}

.base-input::placeholder {
  color: var(--color-text-tertiary, #94a3b8);
}

.base-input-error-state {
  border-color: var(--color-danger, #f44336);
}

.base-input-error-state:focus {
  border-color: var(--color-danger, #f44336);
  box-shadow: 0 0 0 3px rgba(244, 67, 54, 0.12);
}

.base-input-disabled {
  background: var(--color-bg-tertiary, #f1f5f9);
  cursor: not-allowed;
  opacity: 0.6;
}

.base-input-sm {
  padding: 8px 12px;
  font-size: var(--font-size-xs, 12px);
}

.base-input-lg {
  padding: 14px 20px;
  font-size: var(--font-size-md, 16px);
}

.base-input-error {
  margin-top: var(--spacing-xs, 4px);
  font-size: var(--font-size-xs, 12px);
  color: var(--color-danger, #f44336);
}

.base-input-hint {
  margin-top: var(--spacing-xs, 4px);
  font-size: var(--font-size-xs, 12px);
  color: var(--color-text-secondary, #64748b);
}
</style>



