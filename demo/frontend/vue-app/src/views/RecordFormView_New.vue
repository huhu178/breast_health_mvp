<template>
  <div class="record-form-view">
    <!-- 头部，与旧版风格统一 -->
    <header class="page-header-compact">
      <div class="header-left">
        <button class="btn-back" @click="router.back()">← 返回</button>
        <h2 class="page-title">乳腺结节档案</h2>
      </div>
      <div v-if="patient" class="patient-info">
        <span class="info-label">患者:</span>
        <span class="info-value">{{ patient.name }} ({{ patient.phone || '无电话信息' }})</span>
      </div>
    </header>

    <div class="form-layout">
      <el-form :model="form" ref="formRef" label-width="140px">
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

            <!-- 可填写字段（与报告模板第一部分保持一致） -->
            <div class="form-row" style="margin-top: 20px;">
              <div class="form-group">
                <label>身高（cm）</label>
                <input
                  v-model.number="form.height"
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
                  v-model.number="form.weight"
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
                  v-model="form.phone"
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
                      v-model="form.diabetes_history"
                    />
                    <span>无</span>
                  </label>
                  <label class="radio-item">
                    <input
                      type="radio"
                      value="有"
                      v-model="form.diabetes_history"
                    />
                    <span>有</span>
                  </label>
                </div>
              </div>
              <div class="form-group" style="grid-column: span 2;">
                <label>可接收膏方的收货地址</label>
                <input
                  v-model="form.gaofang_address"
                  type="text"
                  class="form-input"
                  placeholder="例如：XX省XX市XX区XX路XX号"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- （二）乳腺结节影像学与临床信息登记 -->
        <section class="form-section imaging-section">
          <div class="section-header">
            <div class="section-icon"></div>
            <h3 class="section-title">（二）乳腺结节影像学与临床信息登记</h3>
          </div>

          <!-- ⭐ 使用FormBuilder自动渲染所有字段（不包括基本信息） -->
          <!-- 前端填写什么，后端就保存什么，不区分（二）和（三） -->
          <FormBuilder 
            :fields="imagingFields" 
            v-model="form"
            :show-section-title="false" 
          />
        </section>

        <!-- 影像报告上传 -->
        <section class="form-section">
          <ImagingReportUpload v-model="uploadedFiles" />
        </section>
      </el-form>

      <!-- 表单按钮 -->
      <div class="form-actions">
        <button type="button" class="btn btn-default" @click="router.back()">
          取消
        </button>
        <button
          type="button"
          class="btn btn-success"
          @click="submitForm"
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? '保存中...' : '保存档案' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import FormBuilder from '@/components/FormBuilder.vue'
import ImagingReportUpload from '@/components/ImagingReportUpload.vue'
import { BREAST_FIELDS, getInitialFormData } from '@/config/breast-fields.js'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const patientId = route.params.patientId

const patient = ref(null)
const isSubmitting = ref(false)
const formRef = ref(null)
const uploadedFiles = ref([])  // 上传的文件列表

// ⭐ 使用配置文件自动生成表单初始值
const form = ref(getInitialFormData())

// 渲染所有「影像学特征」字段（包括原（二）和（三）部分的字段）
// 前端填写什么，后端就保存什么，不区分（二）和（三）
const imagingFields = computed(() => {
  const result = {}
  Object.entries(BREAST_FIELDS).forEach(([key, config]) => {
    if (config.section === '影像学特征') {
      result[key] = config
    }
  })
  return result
})

// 加载患者信息
async function loadPatient() {
  try {
    const response = await axios.get(`/api/b/patients/${patientId}`, {
      withCredentials: true
    })

    if (response.data.success) {
      patient.value = response.data.data

      // 预填充基本信息
      form.value.height = patient.value.height || ''
      form.value.weight = patient.value.weight || ''
      form.value.phone = patient.value.phone || ''
    }
  } catch (error) {
    console.error('加载患者信息失败:', error)
    ElMessage.error('加载患者信息失败')
  }
}

// 提交表单
async function submitForm() {
  try {
    isSubmitting.value = true

    // 检查是否有上传的文件
    const hasFiles = uploadedFiles.value && uploadedFiles.value.length > 0

    if (hasFiles) {
      // 如果有文件，使用multipart/form-data格式提交
      const formData = new FormData()
      
      // 添加表单字段
      formData.append('patient_id', patientId)
      
      // 遍历表单数据，处理数组字段
      Object.keys(form.value).forEach(key => {
        const value = form.value[key]
        // 如果是数组，转换为逗号分隔的字符串
        if (Array.isArray(value)) {
          formData.append(key, value.length > 0 ? value.join(',') : '')
        } else {
          formData.append(key, value !== null && value !== undefined ? value : '')
        }
      })
      
      // 添加文件（字段名：imaging_reports）
      uploadedFiles.value.forEach(file => {
        formData.append('imaging_reports', file)
      })

      console.log('提交数据（含文件）:', {
        patient_id: patientId,
        file_count: uploadedFiles.value.length,
        form_fields: Object.keys(form.value).length
      })

      const response = await axios.post('/api/b/records', formData, {
        withCredentials: true
      })

      if (response.data.success) {
        ElMessage.success('档案创建成功')
        router.push(`/patients/${patientId}`)
      } else {
        ElMessage.error(response.data.message || '创建失败')
      }
    } else {
      // 如果没有文件，使用JSON格式提交（保持向后兼容）
      const submitData = {
        patient_id: patientId
      }
      
      // 遍历表单数据，处理数组字段
      Object.keys(form.value).forEach(key => {
        const value = form.value[key]
        // 如果是数组，转换为逗号分隔的字符串
        if (Array.isArray(value)) {
          submitData[key] = value.length > 0 ? value.join(',') : ''
        } else {
          submitData[key] = value
        }
      })

      console.log('提交数据（无文件）:', submitData)

      const response = await axios.post('/api/b/records', submitData, {
        withCredentials: true
      })

      if (response.data.success) {
        ElMessage.success('档案创建成功')
        router.push(`/patients/${patientId}`)
      } else {
        ElMessage.error(response.data.message || '创建失败')
      }
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadPatient()
})
</script>

<style scoped>
.record-form-view {
  padding: 16px 24px;
  max-width: 1600px;
  margin: 0 auto;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 头部样式，复用旧版风格 */
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

.info-section {
  border-left: 4px solid #67c23a;
  background: linear-gradient(to right, #f0f9ff 0%, #fff 100%);
}

.imaging-section {
  border-left: 4px solid #1e88e5;
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
  border-bottom: 2px solid #e4e7ed; /* 标题下方的横线，更清晰一些 */
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

/* 单选按钮组 - 横向排列，用于“糖尿病史”等 */
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

  .patient-info {
    display: none;
  }

  .page-header-compact {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
