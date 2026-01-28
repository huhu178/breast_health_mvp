<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import BreastFormSection from '../components/BreastFormSection.vue'
import ThyroidFormSection from '../components/ThyroidFormSection.vue'
import ImagingReportUpload from '../components/ImagingReportUpload.vue'
import '@/assets/styles/form-common.css'

const route = useRoute()
const router = useRouter()
const patientId = route.params.patientId

const patient = ref(null)
const isSubmitting = ref(false)
const uploadedFiles = ref([])

// 表单数据 - 对应乳腺+甲状腺双结节报告模板字段
const formData = ref({
  // （一）基本信息
  age: '',
  height: '',
  weight: '',
  phone: '',
  diabetes_history: '无',
  gaofang_address: '',

  // （二）乳腺影像学特征
  discovery_date: '',
  symptoms: [],
  symptoms_other: '',
  birads_level: '',
  nodule_location: [],
  nodule_location_other: '',
  boundary_features: [],
  boundary_features_other: '',
  internal_echo: [],
  internal_echo_other: '',
  blood_flow_signal: [],
  blood_flow_signal_other: '',
  nodule_quantity: '',
  nodule_size: '',
  nodule_count: '',
  breast_disease_history: [],
  breast_disease_history_other: '',
  breast_family_history: [],
  breast_family_history_other: '',
  breast_medication_history: [],
  breast_medication_other: '',

  // （三）甲状腺影像学特征
  thyroid_discovery_date: '',
  thyroid_symptoms: [],
  thyroid_symptoms_other: '',
  tirads_level: '',
  thyroid_nodule_quantity: '',
  thyroid_nodule_size: '',
  thyroid_nodule_count: '',
  hypothyroidism_history: [],
  hypothyroidism_history_other: '',
  thyroid_family_history: [],
  thyroid_family_history_other: '',
  thyroid_medication_history: [],
  thyroid_medication_other: ''
})

async function loadPatient() {
  try {
    const response = await axios.get(`/api/b/patients/${patientId}`, {
      withCredentials: true
    })

    if (response.data.success) {
      patient.value = response.data.data
      // 自动填充基本信息
      if (patient.value.age) formData.value.age = patient.value.age
      if (patient.value.height) formData.value.height = patient.value.height
      if (patient.value.weight) formData.value.weight = patient.value.weight
      if (patient.value.phone) formData.value.phone = patient.value.phone
    }
  } catch (error) {
    console.error('加载患者信息失败:', error)
    alert('加载患者信息失败：' + (error.response?.data?.message || error.message))
  }
}

function validateForm() {
  // 乳腺结节验证
  if (!formData.value.birads_level) {
    alert('请选择BI-RADS分级！')
    return false
  }
  if (!formData.value.discovery_date) {
    alert('请填写乳腺结节发现时间！')
    return false
  }

  // 甲状腺结节验证
  if (!formData.value.tirads_level) {
    alert('请选择TI-RADS分级！')
    return false
  }
  if (!formData.value.thyroid_discovery_date) {
    alert('请填写甲状腺结节发现时间！')
    return false
  }

  return true
}

async function submitForm() {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true
  try {
    const hasFiles = uploadedFiles.value && uploadedFiles.value.length > 0

    if (hasFiles) {
      // 使用 multipart/form-data 格式提交
      const formDataObj = new FormData()

      // 添加基本字段
      formDataObj.append('patient_id', patientId)
      formDataObj.append('nodule_types', 'breast_thyroid')

      // （一）基本信息
      formDataObj.append('age', formData.value.age || '')
      formDataObj.append('height', formData.value.height || '')
      formDataObj.append('weight', formData.value.weight || '')
      formDataObj.append('phone', formData.value.phone || '')
      formDataObj.append('diabetes_history', formData.value.diabetes_history || '无')
      formDataObj.append('gaofang_address', formData.value.gaofang_address || '')

      // （二）乳腺影像学特征
      formDataObj.append('breast_discovery_date', formData.value.discovery_date || '')
      formDataObj.append('symptoms_breast', Array.isArray(formData.value.symptoms)
        ? formData.value.symptoms.join(',')
        : (formData.value.symptoms || ''))
      formDataObj.append('symptoms_other', formData.value.symptoms_other || '')
      formDataObj.append('birads_level', formData.value.birads_level || '')
      formDataObj.append('nodule_location', Array.isArray(formData.value.nodule_location)
        ? formData.value.nodule_location.join(',')
        : (formData.value.nodule_location || ''))
      formDataObj.append('nodule_location_other', formData.value.nodule_location_other || '')
      formDataObj.append('boundary_features', Array.isArray(formData.value.boundary_features)
        ? formData.value.boundary_features.join(',')
        : (formData.value.boundary_features || ''))
      formDataObj.append('boundary_features_other', formData.value.boundary_features_other || '')
      formDataObj.append('internal_echo', Array.isArray(formData.value.internal_echo)
        ? formData.value.internal_echo.join(',')
        : (formData.value.internal_echo || ''))
      formDataObj.append('internal_echo_other', formData.value.internal_echo_other || '')
      formDataObj.append('blood_flow_signal', Array.isArray(formData.value.blood_flow_signal)
        ? formData.value.blood_flow_signal.join(',')
        : (formData.value.blood_flow_signal || ''))
      formDataObj.append('blood_flow_signal_other', formData.value.blood_flow_signal_other || '')
      formDataObj.append('nodule_quantity_breast', formData.value.nodule_quantity || '')
      formDataObj.append('breast_size', formData.value.nodule_size || '')
      formDataObj.append('nodule_count_breast', formData.value.nodule_count || '')
      formDataObj.append('breast_disease_history', Array.isArray(formData.value.breast_disease_history)
        ? formData.value.breast_disease_history.join(',')
        : (formData.value.breast_disease_history || ''))
      formDataObj.append('breast_disease_history_other', formData.value.breast_disease_history_other || '')
      // 乳腺家族史/用药史（按器官）
      formDataObj.append('breast_family_history', Array.isArray(formData.value.breast_family_history)
        ? formData.value.breast_family_history.join(',')
        : (formData.value.breast_family_history || ''))
      formDataObj.append('breast_family_history_other', formData.value.breast_family_history_other || '')
      formDataObj.append('breast_medication_history', Array.isArray(formData.value.breast_medication_history)
        ? formData.value.breast_medication_history.join(',')
        : (formData.value.breast_medication_history || ''))
      formDataObj.append('breast_medication_other', formData.value.breast_medication_other || '')

      // （三）甲状腺影像学特征
      formDataObj.append('thyroid_discovery_date', formData.value.thyroid_discovery_date || '')
      formDataObj.append('symptoms_thyroid', Array.isArray(formData.value.thyroid_symptoms)
        ? formData.value.thyroid_symptoms.join(',')
        : (formData.value.thyroid_symptoms || ''))
      formDataObj.append('thyroid_symptoms_other', formData.value.thyroid_symptoms_other || '')
      formDataObj.append('tirads_level', formData.value.tirads_level || '')
      formDataObj.append('nodule_quantity_thyroid', formData.value.thyroid_nodule_quantity || '')
      formDataObj.append('thyroid_size', formData.value.thyroid_nodule_size || '')
      formDataObj.append('nodule_count_thyroid', formData.value.thyroid_nodule_count || '')
      formDataObj.append('hypothyroidism_history', Array.isArray(formData.value.hypothyroidism_history)
        ? formData.value.hypothyroidism_history.join(',')
        : (formData.value.hypothyroidism_history || ''))
      formDataObj.append('hypothyroidism_history_other', formData.value.hypothyroidism_history_other || '')
      // 甲状腺家族史/用药史（按器官）
      formDataObj.append('thyroid_family_history', Array.isArray(formData.value.thyroid_family_history)
        ? formData.value.thyroid_family_history.join(',')
        : (formData.value.thyroid_family_history || ''))
      formDataObj.append('thyroid_family_history_other', formData.value.thyroid_family_history_other || '')
      formDataObj.append('thyroid_medication_history', Array.isArray(formData.value.thyroid_medication_history)
        ? formData.value.thyroid_medication_history.join(',')
        : (formData.value.thyroid_medication_history || ''))
      formDataObj.append('thyroid_medication_other', formData.value.thyroid_medication_other || '')

      // 添加文件
      uploadedFiles.value.forEach(file => {
        formDataObj.append('imaging_reports', file)
      })

      const response = await axios.post(`/api/b/patients/${patientId}/records`, formDataObj, {
        withCredentials: true
      })

      if (response.data.success) {
        alert('✅ 乳腺+甲状腺双结节健康档案创建成功！')
        router.push(`/patients/${patientId}`)
      } else {
        alert('❌ 创建失败：' + response.data.message)
      }
    } else {
      // 使用 JSON 格式提交
      const submitData = {
        patient_id: parseInt(patientId),
        nodule_types: 'breast_thyroid',

        // （一）基本信息
        age: formData.value.age,
        height: formData.value.height,
        weight: formData.value.weight,
        phone: formData.value.phone,
        diabetes_history: formData.value.diabetes_history,
        gaofang_address: formData.value.gaofang_address,

        // （二）乳腺影像学特征
        discovery_date: formData.value.discovery_date,
        symptoms: Array.isArray(formData.value.symptoms)
          ? formData.value.symptoms.join(',')
          : formData.value.symptoms,
        symptoms_other: formData.value.symptoms_other,
        birads_level: formData.value.birads_level,
        nodule_location: Array.isArray(formData.value.nodule_location)
          ? formData.value.nodule_location.join(',')
          : formData.value.nodule_location,
        nodule_location_other: formData.value.nodule_location_other,
        boundary_features: Array.isArray(formData.value.boundary_features)
          ? formData.value.boundary_features.join(',')
          : formData.value.boundary_features,
        boundary_features_other: formData.value.boundary_features_other,
        internal_echo: Array.isArray(formData.value.internal_echo)
          ? formData.value.internal_echo.join(',')
          : formData.value.internal_echo,
        internal_echo_other: formData.value.internal_echo_other,
        blood_flow_signal: Array.isArray(formData.value.blood_flow_signal)
          ? formData.value.blood_flow_signal.join(',')
          : formData.value.blood_flow_signal,
        blood_flow_signal_other: formData.value.blood_flow_signal_other,
        nodule_quantity: formData.value.nodule_quantity,
        nodule_size: formData.value.nodule_size,
        nodule_count: formData.value.nodule_count,
        breast_disease_history: Array.isArray(formData.value.breast_disease_history)
          ? formData.value.breast_disease_history.join(',')
          : formData.value.breast_disease_history,
        breast_disease_history_other: formData.value.breast_disease_history_other,
        breast_family_history: Array.isArray(formData.value.breast_family_history)
          ? formData.value.breast_family_history.join(',')
          : formData.value.breast_family_history,
        breast_family_history_other: formData.value.breast_family_history_other,
        breast_medication_history: Array.isArray(formData.value.breast_medication_history)
          ? formData.value.breast_medication_history.join(',')
          : formData.value.breast_medication_history,
        breast_medication_other: formData.value.breast_medication_other,

        // （三）甲状腺影像学特征
        thyroid_discovery_date: formData.value.thyroid_discovery_date,
        thyroid_symptoms: Array.isArray(formData.value.thyroid_symptoms)
          ? formData.value.thyroid_symptoms.join(',')
          : formData.value.thyroid_symptoms,
        thyroid_symptoms_other: formData.value.thyroid_symptoms_other,
        tirads_level: formData.value.tirads_level,
        thyroid_nodule_quantity: formData.value.thyroid_nodule_quantity,
        thyroid_nodule_size: formData.value.thyroid_nodule_size,
        thyroid_nodule_count: formData.value.thyroid_nodule_count,
        hypothyroidism_history: Array.isArray(formData.value.hypothyroidism_history)
          ? formData.value.hypothyroidism_history.join(',')
          : formData.value.hypothyroidism_history,
        hypothyroidism_history_other: formData.value.hypothyroidism_history_other
        ,
        thyroid_family_history: Array.isArray(formData.value.thyroid_family_history)
          ? formData.value.thyroid_family_history.join(',')
          : formData.value.thyroid_family_history,
        thyroid_family_history_other: formData.value.thyroid_family_history_other,
        thyroid_medication_history: Array.isArray(formData.value.thyroid_medication_history)
          ? formData.value.thyroid_medication_history.join(',')
          : formData.value.thyroid_medication_history,
        thyroid_medication_other: formData.value.thyroid_medication_other
      }

      const response = await axios.post(`/api/b/patients/${patientId}/records`, submitData, {
        withCredentials: true
      })

      if (response.data.success) {
        alert('✅ 乳腺+甲状腺双结节健康档案创建成功！')
        router.push(`/patients/${patientId}`)
      } else {
        alert('❌ 创建失败：' + response.data.message)
      }
    }
  } catch (error) {
    console.error('提交失败:', error)
    alert('❌ 提交失败：' + (error.response?.data?.message || error.message))
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadPatient()
})
</script>

<template>
  <div class="record-form-view">
    <!-- 头部 -->
    <header class="page-header-compact">
      <div class="header-left">
        <button class="btn-back" @click="router.back()">← 返回</button>
        <h2 class="page-title">乳腺+甲状腺双结节档案</h2>
      </div>
      <div v-if="patient" class="patient-info">
        <span class="info-label">患者:</span>
        <span class="info-value">{{ patient.name }} ({{ patient.phone || '无电话信息' }})</span>
      </div>
    </header>

    <div class="form-layout">
      <form @submit.prevent="submitForm">
        <!-- （一）基本信息 -->
        <section class="form-section info-section">
          <div class="section-header">
            <div class="section-icon"></div>
            <h3 class="section-title">（一）基本信息</h3>
          </div>

          <div v-if="!patient" class="loading-state">
            <span>加载患者信息中...</span>
          </div>

          <div v-else>
            <!-- 只读信息 -->
            <div class="info-grid">
              <div class="info-item">
                <label>姓名</label>
                <div class="info-value">{{ patient.name }}</div>
              </div>
              <div class="info-item">
                <label>性别</label>
                <div class="info-value">{{ patient.gender || '-' }}</div>
              </div>
              <div class="info-item">
                <label>年龄</label>
                <div class="info-value">{{ patient.age || '-' }} 岁</div>
              </div>
            </div>

            <!-- 可填写字段 -->
            <div class="form-row" style="margin-top: 20px;">
              <div class="form-group">
                <label>身高（cm）</label>
                <input
                  v-model.number="formData.height"
                  type="number"
                  class="form-input"
                  placeholder="例如：165"
                  min="100"
                  max="250"
                />
              </div>
              <div class="form-group">
                <label>体重（kg）</label>
                <input
                  v-model.number="formData.weight"
                  type="number"
                  class="form-input"
                  placeholder="例如：60"
                  min="30"
                  max="200"
                />
              </div>
              <div class="form-group">
                <label>联系电话</label>
                <input
                  v-model="formData.phone"
                  type="tel"
                  class="form-input"
                  :placeholder="patient.phone || '请输入联系电话'"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>糖尿病史</label>
                <div class="radio-group-inline">
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="无"
                      v-model="formData.diabetes_history"
                    />
                    <span>无</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="有"
                      v-model="formData.diabetes_history"
                    />
                    <span>有</span>
                  </label>
                </div>
              </div>
              <div class="form-group" style="grid-column: span 2;">
                <label>可接收膏方的收货地址</label>
                <input
                  v-model="formData.gaofang_address"
                  type="text"
                  class="form-input"
                  placeholder="例如：XX省XX市XX区XX路XX号"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- （二）双结节影像学特征 - 并列布局 -->
        <div class="dual-nodule-container">
          <!-- 乳腺影像学特征 -->
          <section class="form-section imaging-section">
            <div class="section-header">
              <div class="section-icon"></div>
              <h3 class="section-title">（二）乳腺影像学特征</h3>
            </div>

            <!-- 使用 BreastFormSection 组件 -->
            <BreastFormSection v-model="formData" :usePerOrganHistory="true" />
          </section>

          <!-- 甲状腺影像学特征 -->
          <section class="form-section imaging-section-thyroid">
            <div class="section-header">
              <div class="section-icon"></div>
              <h3 class="section-title">（三）甲状腺影像学特征</h3>
            </div>

            <!-- 使用 ThyroidFormSection 组件 -->
            <ThyroidFormSection v-model="formData" fieldPrefix="thyroid" :showCommonHistory="true" />
          </section>
        </div>

        <!-- 影像报告上传 -->
        <section class="form-section">
          <ImagingReportUpload v-model="uploadedFiles" />
        </section>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <button type="button" class="btn btn-default" @click="router.back()">
            取消
          </button>
          <button
            type="submit"
            class="btn btn-success"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? '保存中...' : '保存档案' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.record-form-view {
  padding: 16px 24px;
  max-width: 1600px;
  margin: 0 auto;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 头部样式 */
.page-header-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 12px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back {
  background: none;
  border: none;
  color: #409eff;
  font-size: 14px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: #ecf5ff;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.patient-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: #f0f9ff;
  border-radius: 6px;
}

.info-label {
  font-size: 13px;
  color: #909399;
}

.info-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.form-layout {
  max-width: 1400px;
  margin: 0 auto;
}

.form-section {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 双结节并列布局容器 */
.dual-nodule-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.dual-nodule-container .form-section {
  margin-bottom: 0;
}

.info-section {
  border-left: 4px solid #67c23a;
  background: linear-gradient(to right, #f0f9ff 0%, #fff 100%);
}

.imaging-section {
  border-left: 4px solid #1e88e5;
  background: linear-gradient(to right, #f3f8ff 0%, #ffffff 45%, #f7fbff 100%);
}

.imaging-section-thyroid {
  border-left: 4px solid #26a69a;
  background: linear-gradient(to right, #f3f8ff 0%, #ffffff 45%, #f7fbff 100%);
}

.loading-state {
  padding: 30px;
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.info-item .info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e4e7ed;
}

.section-icon {
  width: 20px;
  height: 20px;
  border-radius: 999px;
  margin-right: 10px;
  background: linear-gradient(135deg, #1e88e5 0%, #00acc1 100%);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(135deg, #1e88e5 0%, #00acc1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  margin-bottom: 8px;
}

/* 单选按钮组 - 横向排列 */
.radio-group-inline {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.radio-item {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
}

.radio-item input[type="radio"] {
  margin-right: 6px;
  cursor: pointer;
}

.radio-item span {
  font-size: 13px;
  color: #606266;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 13px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 24px 0;
  margin-top: 20px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.btn {
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 140px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-default {
  background: #fff;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.btn-default:hover:not(:disabled) {
  color: #409eff;
  border-color: #409eff;
}

.btn-success {
  background: #67c23a;
  color: #fff;
}

.btn-success:hover:not(:disabled) {
  background: #85ce61;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .dual-nodule-container {
    grid-template-columns: 1fr;
  }

  .patient-info {
    display: none;
  }

  .page-header-compact {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
