<script setup>
import { ref, computed } from 'vue'
import { LUNG_OPTIONS } from '@/config/lung-options'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  /**
   * @isdoc
   * @description 是否使用 lung_ 前缀字段（用于双结节/三结节，避免与乳腺/甲状腺字段冲突）
   * - true: 使用 lung_symptoms_other / lung_nodule_quantity
   * - false: 使用 symptoms_other / nodule_quantity（单肺结节旧字段）
   */
  usePrefixedFields: {
    type: Boolean,
    default: false
  },
  /**
   * @isdoc
   * @description 是否展示“家族史/用药史”（多器官表单建议只保留一处展示）
   */
  showCommonHistory: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

const formData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// ⭐ 使用配置文件中的选项
const options = LUNG_OPTIONS

// 初始化数组字段
if (!formData.value.lung_symptoms) formData.value.lung_symptoms = []
if (!formData.value.lung_cancer_history) formData.value.lung_cancer_history = []

// 多器官场景：家族史/用药史按器官拆分（与 usePrefixedFields 同步）
const familyHistoryKey = computed(() => (props.usePrefixedFields ? 'lung_family_history' : 'family_history'))
const familyHistoryOtherKey = computed(() => (props.usePrefixedFields ? 'lung_family_history_other' : 'family_history_other'))
const medicationHistoryKey = computed(() => (props.usePrefixedFields ? 'lung_medication_history' : 'medication_history'))
const medicationOtherKey = computed(() => (props.usePrefixedFields ? 'lung_medication_other' : 'medication_other'))

if (!formData.value[familyHistoryKey.value]) formData.value[familyHistoryKey.value] = []
if (!formData.value[medicationHistoryKey.value]) formData.value[medicationHistoryKey.value] = []
if (formData.value[medicationOtherKey.value] === undefined) formData.value[medicationOtherKey.value] = ''

// 计算字段名（兼容单肺结节与多器官表单）
const symptomsOtherKey = computed(() => (props.usePrefixedFields ? 'lung_symptoms_other' : 'symptoms_other'))
const noduleQuantityKey = computed(() => (props.usePrefixedFields ? 'lung_nodule_quantity' : 'nodule_quantity'))

// 复选框切换函数
function toggleCheckbox(array, value) {
  const index = array.indexOf(value)
  if (index > -1) {
    // 如果取消选择"其他"，清空对应的输入框
    if (value === '其他') {
      const fieldName = getFieldNameByArray(array)
      if (fieldName) {
        // medication_history 的“其他”字段使用 medicationOtherKey
        if (fieldName === medicationHistoryKey.value) {
          formData.value[medicationOtherKey.value] = ''
        } else {
          formData.value[fieldName + '_other'] = ''
        }
      }
    }
    array.splice(index, 1)
  } else {
    array.push(value)
  }
}

// 根据数组获取字段名（用于"其他"选项）
function getFieldNameByArray(array) {
  if (array === formData.value.lung_symptoms) return 'lung_symptoms'
  if (array === formData.value.lung_cancer_history) return 'lung_cancer_history'
  if (array === formData.value[familyHistoryKey.value]) return familyHistoryKey.value
  if (array === formData.value[medicationHistoryKey.value]) return medicationHistoryKey.value
  return null
}

// 检查是否选择了"其他"
function hasOtherOption(array) {
  return array && array.includes('其他')
}
</script>

<template>
  <div class="lung-form-section">
    <!-- 结节发现时间 -->
    <div class="form-group">
      <label>结节发现时间 <span class="required">*</span></label>
      <input v-model="formData.lung_discovery_date" type="date" class="form-input" required />
    </div>

    <!-- 肺部症状 -->
    <div class="form-group">
      <label>肺部症状</label>
      <div class="checkbox-group-horizontal">
        <label v-for="symptom in options.symptoms_options" :key="symptom" class="checkbox-item-inline">
          <input type="checkbox" :checked="formData.lung_symptoms.includes(symptom)"
            @change="toggleCheckbox(formData.lung_symptoms, symptom)" />
          <span>{{ symptom }}</span>
        </label>
      </div>
      <div v-if="hasOtherOption(formData.lung_symptoms)" class="other-input-wrapper">
        <input
          v-model="formData[symptomsOtherKey]"
          type="text"
          class="form-input other-input"
          placeholder="请输入其他症状的具体内容"
        />
      </div>
    </div>

    <!-- Lung-RADS分级 -->
    <div class="form-group">
      <label>Lung-RADS分级 <span class="required">*</span></label>
      <div class="radio-group-horizontal">
        <label v-for="level in options.lung_rads_levels" :key="level.value" class="radio-item-inline">
          <input
            type="radio"
            :value="level.value"
            v-model="formData.lung_rads_level"
            name="lung_rads_level"
          />
          <span>{{ level.value }}</span>
        </label>
      </div>
    </div>

    <!-- 结节数量和大小 -->
    <div class="form-row">
      <div class="form-group">
        <label>数量</label>
        <div class="radio-group-horizontal">
          <label v-for="count in options.nodule_quantity_options" :key="count.value" class="radio-item-inline">
            <input
              type="radio"
              :value="count.label"
              v-model="formData[noduleQuantityKey]"
              name="nodule_quantity_lung"
            />
            <span>{{ count.label }}</span>
          </label>
        </div>
      </div>

      <div class="form-group">
        <label>结节大小</label>
        <div class="input-with-unit">
          <input v-model="formData.lung_nodule_size" type="text" class="form-input" placeholder="例如: 12.5" />
          <span class="unit-text">mm</span>
        </div>
      </div>

      <!-- 如果选择多发，显示个数输入框 -->
      <div class="form-group" v-if="formData[noduleQuantityKey] && formData[noduleQuantityKey].includes('多发')">
        <label>多发结节个数</label>
        <input v-model="formData.lung_nodule_count" type="number" class="form-input" placeholder="例如：3" />
      </div>
    </div>

    <!-- 基础疾病史 -->
    <div class="form-group">
      <label>基础疾病史</label>
      <div class="checkbox-group-horizontal">
        <label v-for="disease in options.lung_disease_history_options" :key="disease" class="checkbox-item-inline">
          <input type="checkbox" :checked="formData.lung_cancer_history.includes(disease)"
            @change="toggleCheckbox(formData.lung_cancer_history, disease)" />
          <span>{{ disease }}</span>
        </label>
      </div>
      <div v-if="hasOtherOption(formData.lung_cancer_history)" class="other-input-wrapper">
        <input
          v-model="formData.lung_cancer_history_other"
          type="text"
          class="form-input other-input"
          placeholder="请输入其他基础疾病史的具体内容"
        />
      </div>
    </div>

    <template v-if="showCommonHistory">
      <!-- 家族史 -->
      <div class="form-group">
        <label>家族史</label>
        <div class="checkbox-group-horizontal">
          <label v-for="history in options.family_history_options" :key="history" class="checkbox-item-inline">
          <input type="checkbox" :checked="formData[familyHistoryKey].includes(history)"
            @change="toggleCheckbox(formData[familyHistoryKey], history)" />
            <span>{{ history }}</span>
          </label>
        </div>
      <div v-if="hasOtherOption(formData[familyHistoryKey])" class="other-input-wrapper">
          <input
          v-model="formData[familyHistoryOtherKey]"
            type="text"
            class="form-input other-input"
            placeholder="请输入其他家族史的具体内容"
          />
        </div>
      </div>

      <!-- 药物使用史 -->
      <div class="form-group">
        <label>药物使用史</label>
        <div class="checkbox-group-horizontal">
          <label v-for="medication in options.medication_history_options" :key="medication" class="checkbox-item-inline">
          <input type="checkbox" :checked="formData[medicationHistoryKey].includes(medication)"
            @change="toggleCheckbox(formData[medicationHistoryKey], medication)" />
            <span>{{ medication }}</span>
          </label>
        </div>
      <div v-if="hasOtherOption(formData[medicationHistoryKey])" class="other-input-wrapper">
          <input
          v-model="formData[medicationOtherKey]"
            type="text"
            class="form-input other-input"
            placeholder="请输入其他药物使用史的具体内容"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.lung-form-section {
  /* 外层容器已经有 border-left，这里不需要了 */
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f5f7fa;
}

.section-icon {
  width: 20px;
  height: 20px;
  border-radius: 999px;
  margin-right: 12px;
  background: linear-gradient(135deg, #00acc1 0%, #26a69a 100%);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  margin-bottom: 8px;
}

.required {
  color: #f56c6c;
  margin-left: 3px;
}

.form-input,
.form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #00acc1;
  box-shadow: 0 0 0 2px rgba(0, 172, 193, 0.12);
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-with-unit .form-input {
  flex: 1;
  min-width: 0;
}

.unit-text {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
}

/* 横向复选框组 */
.checkbox-group-horizontal {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.checkbox-item-inline {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  margin: 0;
  padding: 0;
}

.checkbox-item-inline input[type="checkbox"] {
  margin-right: 4px;
  cursor: pointer;
}

.checkbox-item-inline span {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.checkbox-item:hover {
  background: #e0f7fa;
  border-color: #00acc1;
}

.checkbox-item input[type="checkbox"] {
  margin-right: 8px;
  cursor: pointer;
}

.checkbox-item span {
  font-size: 13px;
  color: #606266;
}

/* 横向单选按钮组 */
.radio-group-horizontal {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.radio-item-inline {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  margin: 0;
  padding: 0;
}

.radio-item-inline input[type="radio"] {
  margin-right: 4px;
  cursor: pointer;
}

.radio-item-inline span {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.radio-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.radio-item:hover {
  background: #e0f7fa;
  border-color: #00acc1;
}

.radio-item input[type="radio"] {
  margin-right: 8px;
  cursor: pointer;
}

.radio-item input[type="radio"]:checked + span {
  font-weight: 600;
  color: #00acc1;
}

.radio-item span {
  font-size: 13px;
  color: #606266;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.other-input-wrapper {
  margin-top: 12px;
  padding-left: 8px;
}

.other-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
  background: #fafafa;
}

.other-input:focus {
  outline: none;
  border-color: #00acc1;
  box-shadow: 0 0 0 2px rgba(0, 172, 193, 0.12);
  background: #fff;
}
</style>
