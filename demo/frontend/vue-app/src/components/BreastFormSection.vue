<script setup>
import { ref, computed } from 'vue'
import { BREAST_OPTIONS } from '@/config/breast-options'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  /**
   * @isdoc
   * @description 是否展示“家族史/用药史”（多器官表单建议只保留一处展示）
   */
  showCommonHistory: {
    type: Boolean,
    default: true
  },
  /**
   * @isdoc
   * @description 是否使用乳腺专属的家族史/用药史字段（用于双结节/三结节，避免与肺/甲状腺混淆）
   * - true: 使用 breast_family_history / breast_medication_history 等字段
   * - false: 使用 family_history / medication_history（旧字段）
   */
  usePerOrganHistory: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

// 使用计算属性同步数据
const formData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// ⭐ 使用配置文件中的选项（以后修改选项只需修改 breast-options.js）
const options = BREAST_OPTIONS

// 额外选项配置
const extraOptions = {
  disease_history_options: ['无', '乳腺增生病史', '乳腺纤维瘤病史', '乳腺囊肿病史', '乳腺炎病史', '乳腺癌病史', '其他'],
  family_history_options: ['无', '一级亲属（父母、子女、亲兄弟姐妹）', '二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）', '三级亲属（表/堂兄妹）', '其他'],
  medication_history_options: ['无', '中成药治疗', '激素调节药物', '维生素辅助治疗', '乳腺癌治疗药物', '其他']
}

// 初始化数组字段
if (!formData.value.breast_disease_history) formData.value.breast_disease_history = []

// 计算字段名（兼容旧字段与乳腺专属字段）
const familyHistoryKey = computed(() => (props.usePerOrganHistory ? 'breast_family_history' : 'family_history'))
const familyHistoryOtherKey = computed(() => (props.usePerOrganHistory ? 'breast_family_history_other' : 'family_history_other'))
const medicationHistoryKey = computed(() => (props.usePerOrganHistory ? 'breast_medication_history' : 'medication_history'))
const medicationOtherKey = computed(() => (props.usePerOrganHistory ? 'breast_medication_other' : 'medication_other'))

if (!formData.value[familyHistoryKey.value]) formData.value[familyHistoryKey.value] = []
if (!formData.value[medicationHistoryKey.value]) formData.value[medicationHistoryKey.value] = []
if (formData.value[medicationOtherKey.value] === undefined) formData.value[medicationOtherKey.value] = ''

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
    // “无/无症状”与其它选项互斥：选中“无(症状)”时清空其它；选中其它时移除“无(症状)”
    const noneOptions = new Set(['无', '无症状'])
    if (noneOptions.has(value)) {
      // 选中“无/无症状” => 只保留它，并清空其它相关的 other 输入
      array.splice(0, array.length, value)
      if (value === '无症状') {
        formData.value.symptoms_other = ''
      }
    } else {
      // 选中其它 => 移除“无/无症状”
      for (const noneOpt of noneOptions) {
        const i = array.indexOf(noneOpt)
        if (i > -1) array.splice(i, 1)
      }
    array.push(value)
    }
  }
}

// 根据数组获取字段名（用于"其他"选项）
function getFieldNameByArray(array) {
  if (array === formData.value.symptoms) return 'symptoms'
  if (array === formData.value.breast_disease_history) return 'breast_disease_history'
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
  <div class="breast-form-section">
    <!-- 结节发现时间 -->
    <div class="form-group">
      <label>结节发现时间 <span class="required">*</span></label>
      <input v-model="formData.discovery_date" type="date" class="form-input" required />
    </div>

    <!-- 结节症状 -->
    <div class="form-group">
      <label>结节症状</label>
      <div class="checkbox-group-horizontal">
        <label v-for="symptom in options.symptoms_options" :key="symptom" class="checkbox-item-inline">
          <input type="checkbox" :checked="formData.symptoms.includes(symptom)"
            @change="toggleCheckbox(formData.symptoms, symptom)" />
          <span>{{ symptom }}</span>
        </label>
      </div>
      <div v-if="hasOtherOption(formData.symptoms)" class="other-input-wrapper">
        <input
          v-model="formData.symptoms_other"
          type="text"
          class="form-input other-input"
          placeholder="请输入其他症状的具体内容"
        />
      </div>
    </div>

    <!-- BI-RADS分级 -->
    <div class="form-group">
      <label>BI-RADS分级 <span class="required">*</span></label>
      <div class="radio-group-horizontal">
        <label v-for="level in options.birads_levels" :key="level.value" class="radio-item-inline">
          <input type="radio" :value="level.value" v-model="formData.birads_level" name="birads_level" />
          <span>{{ level.value }}</span>
        </label>
      </div>
    </div>

    <!-- 结节数量和大小 -->
    <div class="form-row">
      <div class="form-group">
        <label>数量</label>
        <div class="radio-group-horizontal">
          <label v-for="count in options.nodule_count_options" :key="count.value" class="radio-item-inline">
            <input type="radio" :value="count.label" v-model="formData.nodule_quantity" name="nodule_quantity_breast" />
            <span>{{ count.label }}</span>
          </label>
        </div>
      </div>

      <div class="form-group">
        <label>结节大小</label>
        <div class="input-with-unit">
          <input v-model="formData.nodule_size" type="text" class="form-input" placeholder="例如: 12.5" />
          <span class="unit-text">mm</span>
        </div>
      </div>

      <!-- 如果选择多发，显示个数输入框 -->
      <div class="form-group" v-if="formData.nodule_quantity && formData.nodule_quantity.includes('多发')">
        <label>多发结节个数</label>
        <input v-model="formData.nodule_count" type="number" class="form-input" placeholder="例如：3" />
      </div>
    </div>

    <!-- 基础疾病史 -->
    <div class="form-group">
      <label>基础疾病史</label>
      <div class="checkbox-group-horizontal">
        <label v-for="disease in extraOptions.disease_history_options" :key="disease" class="checkbox-item-inline">
          <input type="checkbox" :checked="formData.breast_disease_history.includes(disease)"
            @change="toggleCheckbox(formData.breast_disease_history, disease)" />
          <span>{{ disease }}</span>
        </label>
      </div>
      <div v-if="hasOtherOption(formData.breast_disease_history)" class="other-input-wrapper">
        <input
          v-model="formData.breast_disease_history_other"
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
          <label v-for="history in extraOptions.family_history_options" :key="history" class="checkbox-item-inline">
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
          <label v-for="medication in extraOptions.medication_history_options" :key="medication" class="checkbox-item-inline">
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
.breast-form-section {
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
  background: linear-gradient(135deg, #1e88e5 0%, #00acc1 100%);
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
  border-color: #1e88e5;
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.12);
}

.checkbox-group {
  display: grid;
  grid-template-columns: 1fr;
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
  background: #e3f2fd;
  border-color: #1e88e5;
}

.checkbox-item input[type="checkbox"] {
  margin-right: 8px;
  cursor: pointer;
}

.checkbox-item span {
  font-size: 13px;
  color: #606266;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
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
  border-color: #1e88e5;
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.12);
  background: #fff;
}
</style>
