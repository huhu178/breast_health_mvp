<template>
  <div class="form-builder">
    <!-- 按section分组显示 -->
    <div v-for="(sectionFields, sectionName) in groupedFields" :key="sectionName">
      <div class="form-section" v-if="sectionFields.length > 0">
        <h3 class="section-title" v-if="showSectionTitle">{{ sectionName }}</h3>

        <DynamicFormField
          v-for="field in sectionFields"
          :key="field.key"
          :config="field"
          :model-value="modelValue[field.dbColumn]"
          :other-value="getOtherValue(field)"
          @update:model-value="updateField(field.dbColumn, $event)"
          @update:other-value="updateOtherField(field, $event)"
          v-show="shouldShowField(field) && field.type !== 'hidden'"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import DynamicFormField from './DynamicFormField.vue'

const props = defineProps({
  fields: {
    type: Object,
    required: true
  },
  modelValue: {
    type: Object,
    required: true
  },
  showSectionTitle: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

// 按section分组字段
const groupedFields = computed(() => {
  const groups = {}

  Object.entries(props.fields).forEach(([key, config]) => {
    const section = config.section || '基本信息'

    if (!groups[section]) {
      groups[section] = []
    }

    groups[section].push({
      key,
      ...config
    })
  })

  return groups
})

// 更新字段值
function updateField(fieldName, value) {
  // 创建新对象以触发响应式更新
  // 使用展开运算符创建新对象，确保Vue能检测到变化
  const newValue = {
    ...props.modelValue,
    [fieldName]: value
  }
  // 确保emit的值是新的对象引用，触发Vue的响应式更新
  emit('update:modelValue', newValue)
}

// 获取"其他"字段的值
function getOtherValue(field) {
  const otherFieldName = field.otherField || `${field.dbColumn}_other`
  return props.modelValue[otherFieldName] || ''
}

// 更新"其他"字段的值
function updateOtherField(field, value) {
  const otherFieldName = field.otherField || `${field.dbColumn}_other`
  // 创建新对象以触发响应式更新
  // 使用展开运算符创建新对象，确保Vue能检测到变化
  const newValue = {
    ...props.modelValue,
    [otherFieldName]: value
  }
  emit('update:modelValue', newValue)
}

// 判断字段是否应该显示（处理条件显示逻辑）
function shouldShowField(field) {
  if (!field.showWhen) return true

  const { field: dependField, value: dependValue } = field.showWhen
  const dependFieldConfig = props.fields[dependField]

  if (!dependFieldConfig) return true

  const currentValue = props.modelValue[dependFieldConfig.dbColumn]

  return currentValue === dependValue
}
</script>

<style scoped>
.form-builder {
  width: 100%;
}

.form-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409EFF;
}
</style>
