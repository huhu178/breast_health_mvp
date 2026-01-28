<template>
  <div class="dynamic-form-field">
    <!-- 日期选择器 -->
    <el-form-item
      v-if="config.type === 'date'"
      :label="config.label"
      :required="config.required"
    >
      <el-date-picker
        :model-value="modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
        type="date"
        placeholder="选择日期"
        value-format="YYYY-MM-DD"
        style="width: 100%"
      />
    </el-form-item>

    <!-- 数字输入框 -->
    <el-form-item
      v-else-if="config.type === 'number'"
      :label="config.label"
      :required="config.required"
    >
      <el-input
        :model-value="modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
        type="number"
        :placeholder="config.placeholder"
        style="width: 100%"
      >
        <template #append v-if="config.unit">{{ config.unit }}</template>
      </el-input>
    </el-form-item>

    <!-- 单选按钮组（Radio） -->
    <el-form-item
      v-else-if="config.type === 'radio'"
      :label="config.label"
      :required="config.required"
    >
      <el-radio-group
        :model-value="modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
      >
        <el-radio
          v-for="opt in config.options"
          :key="opt.value || opt"
          :label="opt.value || opt"
        >
          {{ opt.label || opt }}
        </el-radio>
      </el-radio-group>
    </el-form-item>

    <!-- 多选框组（Checkbox Group） -->
    <el-form-item
      v-else-if="config.type === 'checkbox-group'"
      :label="config.label"
      :required="config.required"
    >
      <el-checkbox-group
        v-model="localCheckboxValue"
        @change="handleCheckboxChange"
      >
        <el-checkbox
          v-for="opt in config.options"
          :key="opt"
          :label="opt"
        >
          {{ opt }}
        </el-checkbox>
      </el-checkbox-group>
      <!-- 当选中"其他"时，显示输入框 -->
      <div v-if="hasOtherOption && isOtherSelected" class="other-input-wrapper">
        <el-input
          :model-value="otherValue"
          @update:model-value="handleOtherInputChange($event)"
          :placeholder="config.otherPlaceholder || '请输入其他内容'"
          style="margin-top: 10px; width: 100%"
        />
      </div>
    </el-form-item>

    <!-- 隐藏字段（不显示） -->
    <div v-else-if="config.type === 'hidden'" style="display: none;">
      <!-- 隐藏字段，只用于数据存储，不显示在界面上 -->
    </div>

    <!-- 文本输入框（默认） -->
    <el-form-item
      v-else
      :label="config.label"
      :required="config.required"
    >
      <el-input
        :model-value="modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
        :placeholder="config.placeholder"
      />
    </el-form-item>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  config: {
    type: Object,
    required: true
  },
  modelValue: {
    required: true
  },
  otherValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'update:otherValue'])

// 检查是否有"其他"选项
const hasOtherOption = computed(() => {
  return props.config.options && props.config.options.includes('其他')
})

// 处理checkbox的值，确保始终是数组
const checkboxValue = computed(() => {
  const value = props.modelValue
  
  // 处理 null、undefined、空字符串
  if (value === null || value === undefined || value === '') {
    return []
  }
  // 如果已经是数组，创建新数组引用以确保响应式更新
  if (Array.isArray(value)) {
    return [...value]  // 创建新数组引用
  }
  // 如果是字符串（逗号分隔），转换为数组
  if (typeof value === 'string') {
    const parts = value.split(',').filter(v => v && v.trim())
    return parts.length > 0 ? parts : []
  }
  return []
})

// 本地响应式值，用于 v-model
const localCheckboxValue = ref([...checkboxValue.value])

// 监听 props.modelValue 变化，同步到本地值
watch(() => props.modelValue, (newValue) => {
  const newArray = (() => {
    if (newValue === null || newValue === undefined || newValue === '') {
      return []
    }
    if (Array.isArray(newValue)) {
      return [...newValue]
    }
    if (typeof newValue === 'string') {
      const parts = newValue.split(',').filter(v => v && v.trim())
      return parts.length > 0 ? parts : []
    }
    return []
  })()
  
  // 只有当数组内容不同时才更新，避免无限循环
  if (JSON.stringify(localCheckboxValue.value.sort()) !== JSON.stringify(newArray.sort())) {
    localCheckboxValue.value = newArray
  }
}, { immediate: true, deep: true })

// 检查是否选中了"其他"
const isOtherSelected = computed(() => {
  return localCheckboxValue.value.includes('其他')
})

// 处理checkbox变化
function handleCheckboxChange(value) {
  // 确保value是数组，并且创建一个新数组引用
  const newValue = Array.isArray(value) ? [...value] : []
  
  // 更新本地值
  localCheckboxValue.value = newValue
  
  // 直接emit更新，让Element Plus的checkbox-group正常工作
  // 确保emit的是新数组，触发响应式更新
  emit('update:modelValue', newValue)
  
  // 如果取消选中"其他"，清空"其他"输入框的值
  if (!newValue.includes('其他')) {
    emit('update:otherValue', '')
  }
}

// 处理"其他"输入框变化
function handleOtherInputChange(value) {
  emit('update:otherValue', value)
}
</script>

<style scoped>
.other-input-wrapper {
  margin-top: 10px;
  padding-left: 20px;
  border-left: 3px solid #409eff;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
}
</style>
