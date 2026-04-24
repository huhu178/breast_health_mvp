<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  /**
   * @isdoc
   * @description 字段前缀（用于双结节/三结节，避免与乳腺/肺部字段冲突）
   * - 空/未传：使用旧字段（discovery_date/symptoms/symptoms_other/nodule_quantity...）
   * - 'thyroid'：使用 thyroid_discovery_date/thyroid_symptoms/thyroid_symptoms_other/thyroid_nodule_quantity...
   */
  fieldPrefix: {
    type: String,
    default: ''
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

// 兼容旧字段与 prefixed 字段（thyroid_*）
const discoveryDateKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_discovery_date` : 'discovery_date'))
const symptomsKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_symptoms` : 'symptoms'))
const symptomsOtherKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_symptoms_other` : 'symptoms_other'))
const noduleQuantityKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_nodule_quantity` : 'nodule_quantity'))
const noduleSizeKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_nodule_size` : 'nodule_size'))
const noduleCountKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_nodule_count` : 'nodule_count'))

// 多器官场景：家族史/用药史按器官拆分（与 fieldPrefix 同步）
const familyHistoryKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_family_history` : 'family_history'))
const familyHistoryOtherKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_family_history_other` : 'family_history_other'))
const medicationHistoryKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_medication_history` : 'medication_history'))
const medicationOtherKey = computed(() => (props.fieldPrefix ? `${props.fieldPrefix}_medication_other` : 'medication_other'))

// 甲状腺选项配置
const options = {
  tirads_levels: [
    { value: '不清楚', label: '不清楚' },
    { value: '1', label: 'TI-RADS 1 - 正常甲状腺' },
    { value: '2', label: 'TI-RADS 2 - 良性 (恶性风险0%)' },
    { value: '3', label: 'TI-RADS 3 - 可能良性 (恶性风险<5%)' },
    { value: '4A', label: 'TI-RADS 4A - 低度可疑 (恶性风险5%-10%)' },
    { value: '4B', label: 'TI-RADS 4B - 中度可疑 (恶性风险10%-50%)' },
    { value: '4C', label: 'TI-RADS 4C - 高度可疑 (恶性风险50%-95%)' },
    { value: '5', label: 'TI-RADS 5 - 高度提示恶性 (恶性风险>95%)' },
    { value: '6', label: 'TI-RADS 6 - 已确诊恶性' }
  ],
  symptoms_options: [
    '无症状',
    '颈部肿块',
    '压迫症状',
    '疼痛症状',
    '其他'
  ],
  nodule_quantity_options: [
    { value: 'single', label: '单发' },
    { value: 'multiple', label: '多发' }
  ],
  hypothyroidism_history_options: [
    '无',
    '甲状腺功能亢进（甲亢）',
    '甲状腺功能减退（甲减）',
    '桥本甲状腺炎',
    '亚急性甲状腺炎',
    '甲状腺癌病史',
    '其他'
  ],
  family_history_options: [
    '无',
    '一级亲属（父母、子女、亲兄弟姐妹）',
    '二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）',
    '三级亲属（表/堂兄妹）',
    '其他'
  ],
  medication_history_options: [
    '无',
    '甲状腺激素治疗',
    '抗甲状腺药物',
    '放射性碘治疗',
    '中成药治疗',
    '其他'
  ]
}

// 初始化数组字段
if (!formData.value[symptomsKey.value]) formData.value[symptomsKey.value] = []
if (!formData.value.hypothyroidism_history) formData.value.hypothyroidism_history = []
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
    array.push(value)
  }
}

// 根据数组获取字段名（用于"其他"选项）
function getFieldNameByArray(array) {
  if (array === formData.value[symptomsKey.value]) return symptomsKey.value
  if (array === formData.value.hypothyroidism_history) return 'hypothyroidism_history'
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
  <div class="thyroid-form-section">
    <!-- 结节发现时间 -->
    <div class="form-group">
      <label>结节发现时间</label>
      <input v-model="formData[discoveryDateKey]" type="date" class="form-input" />
    </div>

    <!-- 结节症状 -->
    <div class="form-group">
      <label>结节症状</label>
      <div class="checkbox-group-horizontal">
        <label v-for="symptom in options.symptoms_options" :key="symptom" class="checkbox-item-inline">
          <input type="checkbox" :checked="formData[symptomsKey].includes(symptom)"
            @change="toggleCheckbox(formData[symptomsKey], symptom)" />
          <span>{{ symptom }}</span>
        </label>
      </div>
      <div v-if="hasOtherOption(formData[symptomsKey])" class="other-input-wrapper">
        <input
          v-model="formData[symptomsOtherKey]"
          type="text"
          class="form-input other-input"
          placeholder="请输入其他症状的具体内容"
        />
      </div>
    </div>

    <!-- TI-RADS分级 -->
    <div class="form-group">
      <label>TI-RADS分级 <span class="required">*</span></label>
      <div class="radio-group-horizontal">
        <label v-for="level in options.tirads_levels" :key="level.value" class="radio-item-inline">
          <input
            type="radio"
            :value="level.value"
            v-model="formData.tirads_level"
            name="tirads_level"
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
              name="nodule_quantity_thyroid"
            />
            <span>{{ count.label }}</span>
          </label>
        </div>
      </div>

      <div class="form-group">
        <label>结节大小</label>
        <div class="input-with-unit">
          <input v-model="formData[noduleSizeKey]" type="text" class="form-input" placeholder="例如: 12.5" />
          <span class="unit-text">mm</span>
        </div>
      </div>

      <!-- 如果选择多发，显示个数输入框 -->
      <div class="form-group" v-if="formData[noduleQuantityKey] && formData[noduleQuantityKey].includes('多发')">
        <label>多发结节个数</label>
        <input v-model="formData[noduleCountKey]" type="number" class="form-input" placeholder="例如：3" />
      </div>
    </div>

    <!-- 基础疾病史 -->
    <div class="form-group">
      <label>基础疾病史</label>
      <div class="checkbox-group-horizontal">
        <label v-for="history in options.hypothyroidism_history_options" :key="history" class="checkbox-item-inline">
          <input type="checkbox" :checked="formData.hypothyroidism_history.includes(history)"
            @change="toggleCheckbox(formData.hypothyroidism_history, history)" />
          <span>{{ history }}</span>
        </label>
      </div>
      <div v-if="hasOtherOption(formData.hypothyroidism_history)" class="other-input-wrapper">
        <input
          v-model="formData.hypothyroidism_history_other"
          type="text"
          class="form-input other-input"
          placeholder="请输入其他基础疾病的具体内容"
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
.thyroid-form-section {
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
  background: linear-gradient(135deg, #26a69a 0%, #00acc1 100%);
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
  border-color: #26a69a;
  box-shadow: 0 0 0 2px rgba(38, 166, 154, 0.12);
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
  border-color: #26a69a;
}

.checkbox-item input[type="checkbox"] {
  margin-right: 8px;
  cursor: pointer;
}

.checkbox-item span {
  font-size: 13px;
  color: #606266;
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
  border-color: #26a69a;
}

.radio-item input[type="radio"] {
  margin-right: 8px;
  cursor: pointer;
}

.radio-item input[type="radio"]:checked + span {
  font-weight: 600;
  color: #26a69a;
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
  border-color: #26a69a;
  box-shadow: 0 0 0 2px rgba(38, 166, 154, 0.12);
  background: #fff;
}
</style>
