<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const patientId = ref(route.params.id)
// 患者来源：b_end/c_end，默认b_end
const patientSource = ref(route.query.source || 'b_end')

const patient = ref(null)
const records = ref([])
const reports = ref([])
const isLoading = ref(true)
const isEditing = ref(false)
const isGenerating = ref(false)
const activeTab = ref('info') // 'info', 'records', 'reports'

// 健康档案详情相关
const showRecordDetail = ref(false)
const currentRecord = ref(null)
const isEditingRecord = ref(false)

// 创建档案 - 结节类型选择
const showNoduleTypeDialog = ref(false)
const selectedNoduleType = ref('')

const noduleTypeOptions = [
  { value: 'breast', label: '乳腺结节', icon: '🔴' },
  { value: 'lung', label: '肺部结节', icon: '🫁' },
  { value: 'thyroid', label: '甲状腺结节', icon: '🦋' },
  { value: 'breast_lung', label: '乳腺+肺部双结节', icon: '🔴🫁' },
  { value: 'breast_thyroid', label: '乳腺+甲状腺双结节', icon: '🔴🦋' },
  { value: 'lung_thyroid', label: '肺部+甲状腺双结节', icon: '🫁🦋' },
  { value: 'triple', label: '三结节（乳腺+肺部+甲状腺）', icon: '🔴🫁🦋' }
]

// 结节数量选项
const noduleCountOptions = [
  { value: '单发', label: '单发' },
  { value: '多发', label: '多发' }
]

/**
 * @isdoc
 * @description 健康档案详情弹窗-编辑态使用的「乳腺基础疾病史」选项（与表单保持一致）
 */
const breastDiseaseHistoryOptions = [
  '无',
  '乳腺增生病史',
  '乳腺纤维瘤病史',
  '乳腺囊肿病史',
  '乳腺炎病史',
  '乳腺癌病史',
  '其他'
]

/**
 * @isdoc
 * @description 将后端返回的字符串（逗号分隔）/数组/空值 统一转换为数组，便于复选框渲染
 * @param {unknown} value
 * @returns {string[]}
 */
function normalizeToArray(value) {
  if (value === null || value === undefined || value === '') return []
  if (Array.isArray(value)) return value.map(v => String(v).trim()).filter(v => v)
  if (typeof value === 'string') return value.split(',').map(v => v.trim()).filter(v => v)
  return [String(value).trim()].filter(v => v)
}

/**
 * @isdoc
 * @description 复选框切换：把选中值写回到 currentRecord 的字符串字段（逗号分隔）
 * - 支持“无”与其它选项互斥
 * - 取消“其他”时自动清空 other 字段
 * @param {string} fieldName 例如：'breast_disease_history'
 * @param {string} option 当前点击的选项
 * @param {string} [otherFieldName] 例如：'breast_disease_history_other'
 */
function toggleCheckboxStringField(fieldName, option, otherFieldName) {
  if (!currentRecord.value) return

  const selected = normalizeToArray(currentRecord.value[fieldName])
  const exists = selected.includes(option)

  let next = exists ? selected.filter(v => v !== option) : [...selected, option]

  // “无”与其它选项互斥
  if (!exists) {
    if (option === '无') {
      next = ['无']
    } else {
      next = next.filter(v => v !== '无')
    }
  }

  // 取消“其他”时清空输入框
  if (exists && option === '其他' && otherFieldName) {
    currentRecord.value[otherFieldName] = ''
  }

  currentRecord.value[fieldName] = next.join(',')
}

const editForm = ref({
  name: '',
  phone: '',
  wechat_id: '',
  gender: '',
  age: '',
  id_number: ''
})

async function loadPatientDetail() {
  isLoading.value = true
  try {
    // 加载患者基本信息
    const patientResponse = await axios.get(`/api/b/patients/${patientId.value}`, {
      params: { type: patientSource.value || 'b_end' },
      withCredentials: true
    })
    
    if (patientResponse.data.success) {
      patient.value = patientResponse.data.data
      // 初始化编辑表单
      editForm.value = {
        name: patient.value.name || '',
        phone: patient.value.phone || '',
        wechat_id: patient.value.wechat_id || '',
        gender: patient.value.gender || '女',
        age: patient.value.age || '',
        id_number: patient.value.id_number || ''
      }
    }
    
    // 加载患者关联的健康档案
    const recordsResponse = await axios.get(`/api/b/patients/${patientId.value}/records`, {
      params: { type: patientSource.value || 'b_end' },
      withCredentials: true
    })
    
    if (recordsResponse.data.success) {
      records.value = recordsResponse.data.data || []
    }
    
    // 加载患者关联的报告
    const reportsResponse = await axios.get(`/api/b/patients/${patientId.value}/reports`, {
      params: { type: patientSource.value || 'b_end' },
      withCredentials: true
    })
    
    if (reportsResponse.data.success) {
      reports.value = reportsResponse.data.data || []
    }
  } catch (error) {
    console.error('加载患者详情失败:', error)
    alert('加载失败：' + (error.response?.data?.message || error.message))
  } finally {
    isLoading.value = false
  }
}

function startEdit() {
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  // 恢复原始数据
  editForm.value = {
    name: patient.value.name || '',
    phone: patient.value.phone || '',
    wechat_id: patient.value.wechat_id || '',
    gender: patient.value.gender || '女',
    age: patient.value.age || '',
    id_number: patient.value.id_number || ''
  }
}

async function saveEdit() {
  try {
    const payload = {
      ...editForm.value,
      type: patientSource.value || 'b_end'
    }
    const response = await axios.put(`/api/b/patients/${patientId.value}`, payload, {
      withCredentials: true
    })
    
    if (response.data.success) {
      alert('保存成功！')
      isEditing.value = false
      loadPatientDetail()
    } else {
      alert(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败：' + (error.response?.data?.message || error.message))
  }
}

function createRecord() {
  // 如果患者已有结节类型，直接跳转；否则显示选择对话框
  if (patient.value.nodule_type) {
    // 根据已有的结节类型跳转到对应的表单页面
    const routeMap = {
      'breast': `/records/new/${patientId.value}`,
      'lung': `/records/lung/${patientId.value}`,
      'thyroid': `/records/thyroid/${patientId.value}`,
      'breast_lung': `/records/breast-lung/${patientId.value}`,
      'breast_thyroid': `/records/breast-thyroid/${patientId.value}`,
      'lung_thyroid': `/records/lung-thyroid/${patientId.value}`,
      'triple': `/records/triple/${patientId.value}`
    }
    const targetRoute = routeMap[patient.value.nodule_type] || `/records/new/${patientId.value}`
    router.push(targetRoute)
  } else {
    showNoduleTypeDialog.value = true
    selectedNoduleType.value = 'breast' // 默认选中乳腺
  }
}

async function confirmCreateRecord() {
  if (!selectedNoduleType.value) {
    alert('⚠️ 请选择结节类型！')
    return
  }

  try {
    // 更新患者的结节类型
    const response = await axios.put(`/api/b/patients/${patientId.value}`, {
      nodule_type: selectedNoduleType.value,
      type: patientSource.value || 'b_end'
    }, { withCredentials: true })

    if (response.data.success) {
      // 关闭对话框
      showNoduleTypeDialog.value = false
      // 刷新患者信息
      await loadPatientDetail()

      // 根据结节类型跳转到对应的表单页面
      const routeMap = {
        'breast': `/records/new/${patientId.value}`,
        'lung': `/records/lung/${patientId.value}`,
        'thyroid': `/records/thyroid/${patientId.value}`,
        'breast_lung': `/records/breast-lung/${patientId.value}`,
        'breast_thyroid': `/records/breast-thyroid/${patientId.value}`,
        'lung_thyroid': `/records/lung-thyroid/${patientId.value}`,
        'triple': `/records/triple/${patientId.value}`
      }

      const targetRoute = routeMap[selectedNoduleType.value]
      if (targetRoute) {
        router.push(targetRoute)
      } else {
        alert('❌ 未知的结节类型：' + selectedNoduleType.value)
      }
    } else {
      alert('❌ 设置失败：' + response.data.message)
    }
  } catch (error) {
    alert('❌ 设置失败：' + (error.response?.data?.message || error.message))
  }
}

function cancelNoduleTypeDialog() {
  showNoduleTypeDialog.value = false
  selectedNoduleType.value = ''
}

async function viewRecord(recordId) {
  try {
    const response = await axios.get(`/api/b/records/${recordId}`, {
      params: { type: patientSource.value || 'b_end' },
      withCredentials: true
    })
    
    if (response.data.success) {
      currentRecord.value = response.data.data
      showRecordDetail.value = true
      isEditingRecord.value = false
    }
  } catch (error) {
    console.error('加载档案详情失败:', error)
    alert('加载失败：' + (error.response?.data?.message || error.message))
  }
}

function closeRecordDetail() {
  showRecordDetail.value = false
  currentRecord.value = null
  isEditingRecord.value = false
}

function startEditRecord() {
  isEditingRecord.value = true
}

function cancelEditRecord() {
  isEditingRecord.value = false
}

async function saveRecordEdit() {
  if (!currentRecord.value) return
  
  try {
    // 保存时保持向后兼容：把可能的数组值统一转成逗号分隔字符串
    const payload = { ...currentRecord.value }
    if (Array.isArray(payload.breast_disease_history)) {
      payload.breast_disease_history = payload.breast_disease_history.join(',')
    }

    const response = await axios.put(`/api/b/records/${currentRecord.value.id}`, payload, {
      params: { type: patientSource.value || 'b_end' },
      withCredentials: true
    })
    
    if (response.data.success) {
      alert('✅ 保存成功！')
      isEditingRecord.value = false
      // 刷新档案列表
      await loadPatientDetail()
    } else {
      alert('❌ 保存失败：' + response.data.message)
    }
  } catch (error) {
    console.error('保存档案失败:', error)
    alert('❌ 保存失败：' + (error.response?.data?.message || error.message))
  }
}

async function generateReport(recordId) {
  if (isGenerating.value) return
  
  if (!confirm('确认为此档案生成健康报告吗？\n\n生成过程需要10-30秒，请耐心等待...')) {
    return
  }
  
  isGenerating.value = true
  try {
    const response = await axios.post(`/api/b/patients/${patientId.value}/reports/generate`,
      { record_id: recordId, type: patientSource.value || 'b_end' },
      { withCredentials: true }
    )
    
    if (response.data.success) {
      alert('✅ 报告生成成功！')
      // 刷新报告列表
      await loadPatientDetail()
      // 切换到报告标签
      activeTab.value = 'reports'
      // 如果返回了报告ID，可以直接跳转查看
      if (response.data.data && response.data.data.id) {
        const shouldView = confirm('报告已生成！是否立即查看？')
        if (shouldView) {
          viewReport(response.data.data.id)
        }
      }
    } else {
      alert('❌ 生成失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('生成报告失败:', error)
    alert('❌ 生成失败：' + (error.response?.data?.message || error.message))
  } finally {
    isGenerating.value = false
  }
}

function viewReport(reportId) {
  // 查看报告：跳转到报告详情页，显示完整报告（已发布）或提示（草稿）
  router.push({
    path: `/reports/${reportId}`,
    query: { source: patientSource.value || 'b_end' }
  })
}

// 删除患者
async function deletePatient() {
  if (!confirm('⚠️ 确定要删除此患者吗？\n\n删除后将同时删除该患者的所有健康档案、报告和随访记录，此操作不可恢复！')) {
    return
  }
  
  try {
    const response = await axios.delete(`/api/b/patients/${patientId.value}`, {
      params: { type: patientSource.value || 'b_end' },
      withCredentials: true
    })
    
    if (response.data.success) {
      alert('✅ 患者删除成功！')
      router.push('/patients')
    } else {
      alert('❌ 删除失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('删除患者失败:', error)
    alert('❌ 删除失败：' + (error.response?.data?.message || error.message))
  }
}

// 删除健康档案
async function deleteRecord(recordId) {
  if (!confirm('⚠️ 确定要删除此健康档案吗？\n\n删除后将同时删除该档案关联的影像报告文件，此操作不可恢复！')) {
    return
  }
  
  try {
    const response = await axios.delete(`/api/b/records/${recordId}`, {
      params: { type: patientSource.value || 'b_end' },
      withCredentials: true
    })
    
    if (response.data.success) {
      alert('✅ 健康档案删除成功！')
      // 刷新列表
      await loadPatientDetail()
    } else {
      alert('❌ 删除失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('删除健康档案失败:', error)
    alert('❌ 删除失败：' + (error.response?.data?.message || error.message))
  }
}

// 删除健康报告
async function deleteReport(reportId) {
  if (!confirm('⚠️ 确定要删除此健康报告吗？\n\n此操作不可恢复！')) {
    return
  }
  
  try {
    const response = await axios.delete(`/api/b/reports/${reportId}`, {
      params: { type: patientSource.value || 'b_end' },
      withCredentials: true
    })
    
    if (response.data.success) {
      alert('✅ 健康报告删除成功！')
      // 刷新列表
      await loadPatientDetail()
    } else {
      alert('❌ 删除失败：' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('删除健康报告失败:', error)
    alert('❌ 删除失败：' + (error.response?.data?.message || error.message))
  }
}

// 格式化checkbox值（可能是数组或逗号分隔的字符串）
function formatCheckboxValue(value) {
  // 处理空值
  if (value === null || value === undefined) {
    return '无'
  }
  
  // 转换为字符串进行处理
  let strValue = ''
  if (Array.isArray(value)) {
    if (value.length === 0) return '无'
    strValue = value.join(',')
  } else if (typeof value === 'string') {
    strValue = value
  } else if (typeof value === 'object') {
    // 对象转换为字符串
    try {
      strValue = JSON.stringify(value)
    } catch (e) {
      return '无'
    }
  } else {
    strValue = String(value)
  }
  
  // 处理空字符串
  if (!strValue || strValue.trim() === '') {
    return '无'
  }
  
  // 去除首尾空格
  strValue = strValue.trim()
  
  // 处理特殊格式：{} 或 {其他} 等（必须优先处理）
  if (strValue === '{}' || strValue === '[]') {
    return '无'
  }
  
  // 处理花括号格式：{其他} 或 {值1,值2} 等
  if (strValue.startsWith('{') && strValue.endsWith('}')) {
    // 提取花括号内的内容
    const content = strValue.slice(1, -1).trim()
    // 如果花括号内为空，返回'无'
    if (!content || content === '') {
      return '无'
    }
    // 如果内容包含逗号，说明是多个值
    if (content.includes(',')) {
      const parts = content.split(',').map(v => v.trim()).filter(v => v && v !== '{}' && v !== '[]' && v !== '')
      if (parts.length === 0) return '无'
      return parts.join('、')
    }
    // 单个值，直接返回
    return content
  }
  
  // 如果是JSON格式的数组字符串，尝试解析
  if (strValue.startsWith('[') && strValue.endsWith(']')) {
    try {
      const parsed = JSON.parse(strValue)
      if (Array.isArray(parsed) && parsed.length > 0) {
        const filtered = parsed.filter(v => v && String(v).trim() && v !== '{}' && v !== '[]')
        if (filtered.length === 0) return '无'
        return filtered.map(v => String(v).trim()).join('、')
      }
      return '无'
    } catch (e) {
      // 解析失败，继续处理
    }
  }
  
  // 处理逗号分隔的字符串
  const parts = strValue.split(',').map(v => v.trim()).filter(v => {
    // 过滤掉空值、空对象、空数组
    return v && v !== '{}' && v !== '[]' && v !== ''
  })
  
  if (parts.length === 0) {
    return '无'
  }
  
  return parts.join('、')
}

function reviewReport(reportId) {
  // 审核报告：跳转到报告详情页，强制显示审核界面（可以编辑）
  router.push({
    path: `/reports/${reportId}`,
    query: { 
      review: 'true',
      source: patientSource.value || 'b_end'  // 传递患者来源，确保C端报告能正确加载
    }
  })
}

function getRiskClass(riskLevel) {
  if (!riskLevel) return 'badge-default'
  const level = riskLevel.toLowerCase()
  if (level.includes('高') || level.includes('high')) return 'badge-danger'
  if (level.includes('中') || level.includes('medium')) return 'badge-warning'
  return 'badge-success'
}

onMounted(() => {
  loadPatientDetail()
})
</script>

<template>
  <div class="patient-detail-view">
    <div v-if="isLoading" class="loading">加载中...</div>
    
    <template v-else-if="patient">
      <!-- 页面头部 -->
      <header class="page-header">
        <div class="header-left">
          <button class="btn-back" @click="router.back()">← 返回</button>
          <h2 class="page-title">患者详情</h2>
        </div>
        <div class="header-actions">
          <button v-if="!isEditing" class="btn btn-danger" @click="deletePatient" style="margin-right: 10px;">
            🗑️ 删除患者
          </button>
          <button v-if="!isEditing" class="btn btn-primary" @click="createRecord">
            创建健康档案
          </button>
        </div>
      </header>

      <!-- Tab 导航 -->
      <div class="tabs">
        <button 
          class="tab-item" 
          :class="{ active: activeTab === 'info' }"
          @click="activeTab = 'info'"
        >
          👤 基本信息
        </button>
        <button 
          class="tab-item" 
          :class="{ active: activeTab === 'records' }"
          @click="activeTab = 'records'"
        >
          📋 健康档案 ({{ records.length }})
        </button>
        <button 
          class="tab-item" 
          :class="{ active: activeTab === 'reports' }"
          @click="activeTab = 'reports'"
        >
          📄 健康报告 ({{ reports.length }})
        </button>
      </div>

      <!-- Tab 内容：基本信息 -->
      <section v-show="activeTab === 'info'" class="card">
        <div class="card-header">
          <h3 class="card-title">👤 基本信息</h3>
          <div class="card-actions">
            <template v-if="!isEditing">
              <button class="btn btn-text" @click="startEdit">编辑</button>
            </template>
            <template v-else>
              <button class="btn btn-text" @click="cancelEdit">取消</button>
              <button class="btn btn-success" @click="saveEdit">保存</button>
            </template>
          </div>
        </div>
        
        <div v-if="!isEditing" class="info-grid">
          <div class="info-item">
            <label>患者编号</label>
            <div class="info-value">{{ patient.patient_code || '-' }}</div>
          </div>
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
            <div class="info-value">{{ patient.age || '-' }}</div>
          </div>
          <div class="info-item">
            <label>手机号</label>
            <div class="info-value">{{ patient.phone }}</div>
          </div>
          <div class="info-item">
            <label>微信号</label>
            <div class="info-value">{{ patient.wechat_id || '-' }}</div>
          </div>
          <div class="info-item">
            <label>身份证号</label>
            <div class="info-value">{{ patient.id_number || '-' }}</div>
          </div>
          <div class="info-item">
            <label>注册时间</label>
            <div class="info-value">{{ patient.created_at }}</div>
          </div>
          <div class="info-item">
            <label>患者ID</label>
            <div class="info-value">{{ patient.id }}</div>
          </div>
        </div>
        
        <div v-else class="edit-form">
          <div class="form-row">
            <div class="form-group" style="flex: 1;">
              <label>姓名 *</label>
              <input v-model="editForm.name" type="text" class="form-input" required />
            </div>
            <div class="form-group" style="flex: 1; margin-left: 12px;">
              <label>性别</label>
              <select v-model="editForm.gender" class="form-input">
                <option value="女">女</option>
                <option value="男">男</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group" style="flex: 1;">
              <label>手机号 *</label>
              <input v-model="editForm.phone" type="text" class="form-input" required />
            </div>
            <div class="form-group" style="flex: 1; margin-left: 12px;">
              <label>微信号</label>
              <input v-model="editForm.wechat_id" type="text" class="form-input" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group" style="flex: 1;">
              <label>年龄</label>
              <input v-model="editForm.age" type="number" class="form-input" />
            </div>
            <div class="form-group" style="flex: 1; margin-left: 12px;">
              <label>身份证号</label>
              <input v-model="editForm.id_number" type="text" class="form-input" />
            </div>
          </div>
        </div>
      </section>

      <!-- Tab 内容：健康档案 -->
      <section v-show="activeTab === 'records'" class="card">
        <div class="card-header">
          <h3 class="card-title">📋 健康档案 ({{ records.length }})</h3>
          <button class="btn btn-primary" @click="router.push(`/records/new/${patientId}`)">
            ➕ 新建档案
          </button>
        </div>
        
        <div v-if="records.length === 0" class="empty">
          暂无健康档案，请点击右上角"新建档案"按钮创建
        </div>
        
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>档案编号</th>
              <th>年龄</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in records" :key="record.id">
              <td>{{ record.record_code }}</td>
              <td>{{ record.age || '-' }}</td>
              <td>{{ record.created_at }}</td>
              <td>
                <button class="btn-link" @click="viewRecord(record.id)">查看</button>
                <button class="btn-link" @click="generateReport(record.id)">生成报告</button>
                <button class="btn-link btn-danger" @click="deleteRecord(record.id)" style="color: #f56c6c;">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Tab 内容：健康报告 -->
      <section v-show="activeTab === 'reports'" class="card">
        <div class="card-header">
          <h3 class="card-title">📄 健康报告 ({{ reports.length }})</h3>
        </div>
        
        <div v-if="reports.length === 0" class="empty">
          暂无健康报告
        </div>
        
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>报告编号</th>
              <th>档案ID</th>
              <th>风险等级</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="report in reports" :key="report.id">
              <td>{{ report.report_code || report.id }}</td>
              <td>{{ report.record_id }}</td>
              <td>
                <span class="badge" :class="getRiskClass(report.risk_level)">
                  {{ report.risk_level || '未评估' }}
                </span>
              </td>
              <td>{{ report.created_at }}</td>
              <td>
                <button class="btn-link" @click="reviewReport(report.id)">📝 审核</button>
                <button class="btn-link" @click="viewReport(report.id)">👁️ 查看</button>
                <button class="btn-link btn-danger" @click="deleteReport(report.id)" style="color: #f56c6c;">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
    
    <div v-else class="error">
      患者不存在或已被删除
    </div>

    <!-- 健康档案详情模态框 -->
    <div v-if="showRecordDetail && currentRecord" class="modal-overlay" @click.self="closeRecordDetail">
      <div class="modal-content record-detail-modal">
        <!-- 模态框头部 -->
        <div class="modal-header">
            <h3>健康档案详情</h3>
            <div class="header-actions">
              <button v-if="!isEditingRecord" class="btn btn-primary" @click="startEditRecord">
                编辑
              </button>
              <button v-else class="btn btn-success" @click="saveRecordEdit">
                保存
              </button>
              <button v-if="isEditingRecord" class="btn btn-default" @click="cancelEditRecord">
                取消
              </button>
              <button class="btn-close" @click="closeRecordDetail">✕</button>
            </div>
        </div>

        <!-- 模态框内容 - 对应前端表单三大类 -->
        <div class="modal-body">
          <div style="padding: 10px 0; margin-bottom: 20px; border-bottom: 2px solid #e4e7ed;">
            <p style="color: #606266; font-size: 14px;">
              档案编号：<strong>{{ currentRecord.record_code }}</strong>
              &nbsp;&nbsp;|&nbsp;&nbsp;
              {{ new Date(currentRecord.created_at).toLocaleString('zh-CN') }}
            </p>
          </div>

          <!-- ========== （一）基本信息 ========== -->
          <section class="detail-section">
            <h4 class="section-title">（一）基本信息</h4>
            <div class="detail-grid">
              <div class="detail-item">
                <label>身高(cm)：</label>
                <input v-if="isEditingRecord" v-model="currentRecord.height" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                <span v-else>{{ currentRecord.height || '-' }}</span>
              </div>
              <div class="detail-item">
                <label>体重(kg)：</label>
                <input v-if="isEditingRecord" v-model="currentRecord.weight" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                <span v-else>{{ currentRecord.weight || '-' }}</span>
              </div>
              <div class="detail-item">
                <label>联系电话：</label>
                <input v-if="isEditingRecord" v-model="currentRecord.phone" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 150px;" />
                <span v-else>{{ currentRecord.phone || patient?.phone || '-' }}</span>
              </div>
              <div class="detail-item">
                <label>糖尿病史：</label>
                <input v-if="isEditingRecord" v-model="currentRecord.diabetes_history" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                <span v-else>{{ currentRecord.diabetes_history || '-' }}</span>
              </div>
              <div class="detail-item full-width">
                <label>可接收膏方的收货地址：</label>
                <input v-if="isEditingRecord" v-model="currentRecord.gaofang_address" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100%;" />
                <span v-else>{{ currentRecord.gaofang_address || '-' }}</span>
              </div>
            </div>
          </section>

          <!-- ========== （二）影像学与临床信息登记（随结节类型动态展示） ========== -->
          <section class="detail-section">
            <h4 class="section-title">
              {{
                patient?.nodule_type === 'lung'
                  ? '（二）肺部影像学特征'
                  : (patient?.nodule_type === 'thyroid'
                      ? '（二）甲状腺结节影像学特征'
                      : (patient?.nodule_type === 'breast'
                          ? '（二）乳腺结节影像学与临床信息登记'
                          : '（二）影像学与临床信息登记'))
              }}
            </h4>

            <!-- 乳腺结节数据 -->
            <div v-if="['breast', 'breast_lung', 'breast_thyroid', 'triple'].includes(patient.nodule_type)">
              <h5 style="color: #409eff; font-size: 15px; margin: 15px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #e4e7ed;">
                乳腺结节数据
              </h5>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>发现时间：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.breast_discovery_date" type="date" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 150px;" />
                  <span v-else>{{ currentRecord.breast_discovery_date || '' }}</span>
                </div>
                <div class="detail-item">
                  <label>结节症状：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.symptoms" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.symptoms) }}
                    <span v-if="currentRecord.breast_symptoms_other || currentRecord.symptoms_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.breast_symptoms_other || currentRecord.symptoms_other }}）
                    </span>
                  </span>
                </div>
                <div class="detail-item">
                  <label>BI-RADS分级：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.birads_level" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                  <span v-else>{{ currentRecord.birads_level || '' }}</span>
                </div>
                <div class="detail-item">
                  <label>数量：</label>
                  <select
                    v-if="isEditingRecord"
                    v-model="currentRecord.nodule_quantity"
                    style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;"
                  >
                    <option value="">请选择</option>
                    <option value="单发">单发</option>
                    <option value="多发">多发</option>
                  </select>
                  <span v-else>
                    {{ currentRecord.nodule_quantity === '单发' ? '1' : (currentRecord.nodule_quantity === '多发' ? (currentRecord.nodule_count || '-') : (currentRecord.nodule_count || currentRecord.nodule_quantity || '-')) }}
                  </span>
                </div>
                <div class="detail-item" v-if="currentRecord.nodule_quantity === '多发'">
                  <label>多发结节个数：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.nodule_count" type="number" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                  <span v-else>{{ currentRecord.nodule_count || '-' }}</span>
                </div>
                <div class="detail-item">
                  <label>结节大小(mm)：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.nodule_size" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                  <span v-else>{{ currentRecord.nodule_size || '-' }}</span>
                </div>
                <!-- 基础疾病史、家族史、药物使用史（前端表单中的字段） -->
                <div class="detail-item">
                  <label>基础疾病史：</label>
                  <div v-if="isEditingRecord" class="detail-checkbox-group">
                    <label
                      v-for="opt in breastDiseaseHistoryOptions"
                      :key="opt"
                      class="detail-checkbox-item"
                    >
                      <input
                        type="checkbox"
                        :checked="normalizeToArray(currentRecord.breast_disease_history).includes(opt)"
                        @change="toggleCheckboxStringField('breast_disease_history', opt, 'breast_disease_history_other')"
                      />
                      <span>{{ opt }}</span>
                    </label>
                    <input
                      v-if="normalizeToArray(currentRecord.breast_disease_history).includes('其他')"
                      v-model="currentRecord.breast_disease_history_other"
                      type="text"
                      class="detail-other-input"
                      placeholder="请输入其他基础疾病史的具体内容"
                    />
                  </div>
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.breast_disease_history) }}
                    <span v-if="currentRecord.breast_disease_history_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.breast_disease_history_other }}）
                    </span>
                  </span>
                </div>
                <div class="detail-item">
                  <label>家族史：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.family_history" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.family_history) }}
                    <span v-if="currentRecord.family_history_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.family_history_other }}）
                    </span>
                  </span>
                </div>
                <div class="detail-item">
                  <label>药物使用史：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.medication_history" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.medication_history) }}
                    <span v-if="currentRecord.medication_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.medication_other }}）
                    </span>
                  </span>
                </div>
              </div>
            </div>

            <!-- 甲状腺结节数据 -->
            <div v-if="['thyroid', 'breast_thyroid', 'lung_thyroid', 'triple'].includes(patient.nodule_type)">
              <h5 style="color: #409eff; font-size: 15px; margin: 15px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #e4e7ed;">
                甲状腺结节数据
              </h5>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>发现时间：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.thyroid_discovery_date" type="date" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 150px;" />
                  <span v-else>{{ currentRecord.thyroid_discovery_date || '' }}</span>
                </div>
                <div class="detail-item">
                  <label>结节症状：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.thyroid_symptoms" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.thyroid_symptoms || currentRecord.symptoms) }}
                    <span v-if="currentRecord.thyroid_symptoms_other || currentRecord.symptoms_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.thyroid_symptoms_other || currentRecord.symptoms_other }}）
                    </span>
                  </span>
                </div>
                <div class="detail-item">
                  <label>TI-RADS分级：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.tirads_level" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                  <span v-else>{{ currentRecord.tirads_level || '' }}</span>
                </div>
                <div class="detail-item">
                  <label>数量：</label>
                  <select v-if="isEditingRecord" v-model="currentRecord.thyroid_nodule_quantity" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;">
                    <option value="">请选择</option>
                    <option value="单发">单发</option>
                    <option value="多发">多发</option>
                  </select>
                  <span v-else>{{ currentRecord.thyroid_nodule_quantity || currentRecord.nodule_quantity || '-' }}</span>
                </div>
                <div class="detail-item" v-if="(currentRecord.thyroid_nodule_quantity || currentRecord.nodule_quantity) === '多发'">
                  <label>多发结节个数：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.thyroid_nodule_count" type="number" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                  <span v-else>{{ currentRecord.thyroid_nodule_count || currentRecord.nodule_count || '-' }}</span>
                </div>
                <div class="detail-item">
                  <label>结节大小(mm)：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.thyroid_nodule_size" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                  <span v-else>{{ currentRecord.thyroid_nodule_size || '' }}</span>
                </div>
                <div class="detail-item">
                  <label>基础疾病史：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.hypothyroidism_history" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.hypothyroidism_history) }}
                    <span v-if="currentRecord.hypothyroidism_history_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.hypothyroidism_history_other }}）
                    </span>
                  </span>
                </div>
                <div class="detail-item">
                  <label>家族史：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.thyroid_family_history" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.thyroid_family_history || currentRecord.family_history) }}
                    <span v-if="currentRecord.thyroid_family_history_other || currentRecord.family_history_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.thyroid_family_history_other || currentRecord.family_history_other }}）
                    </span>
                  </span>
                </div>
                <div class="detail-item">
                  <label>药物使用史：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.thyroid_medication_history" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.thyroid_medication_history || currentRecord.medication_history) }}
                    <span v-if="currentRecord.thyroid_medication_other || currentRecord.medication_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.thyroid_medication_other || currentRecord.medication_other }}）
                    </span>
                  </span>
                </div>
              </div>
            </div>

            <!-- 肺部结节数据 -->
            <div v-if="['lung', 'breast_lung', 'lung_thyroid', 'triple'].includes(patient.nodule_type)">
              <h5 style="color: #409eff; font-size: 15px; margin: 15px 0 10px 0; padding-bottom: 5px; border-bottom: 1px solid #e4e7ed;">
                肺部结节数据
              </h5>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>发现时间：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.lung_discovery_date" type="date" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 150px;" />
                  <span v-else>{{ currentRecord.lung_discovery_date || '' }}</span>
                </div>
                <div class="detail-item">
                  <label>肺部症状：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.lung_symptoms" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.lung_symptoms) }}
                    <span v-if="currentRecord.lung_symptoms_other || currentRecord.symptoms_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.lung_symptoms_other || currentRecord.symptoms_other }}）
                    </span>
                  </span>
                </div>
                <div class="detail-item">
                  <label>Lung-RADS分级：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.lung_rads_level" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                  <span v-else>{{ currentRecord.lung_rads_level || '' }}</span>
                </div>
                <div class="detail-item">
                  <label>数量：</label>
                  <select
                    v-if="isEditingRecord && patient.nodule_type === 'lung'"
                    v-model="currentRecord.nodule_quantity"
                    style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;"
                  >
                    <option value="">请选择</option>
                    <option value="单发">单发</option>
                    <option value="多发">多发</option>
                  </select>
                  <select
                    v-else-if="isEditingRecord"
                    v-model="currentRecord.lung_nodule_quantity"
                    style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;"
                  >
                    <option value="">请选择</option>
                    <option value="单发">单发</option>
                    <option value="多发">多发</option>
                  </select>
                  <span v-else>{{ (patient.nodule_type === 'lung' ? currentRecord.nodule_quantity : currentRecord.lung_nodule_quantity) || '-' }}</span>
                </div>
                <div class="detail-item" v-if="(patient.nodule_type === 'lung' ? currentRecord.nodule_quantity : currentRecord.lung_nodule_quantity) === '多发'">
                  <label>多发结节个数：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.lung_nodule_count" type="number" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                  <span v-else>{{ currentRecord.lung_nodule_count || '-' }}</span>
                </div>
                <div class="detail-item">
                  <label>结节大小(mm)：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.lung_nodule_size" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 100px;" />
                  <span v-else>{{ currentRecord.lung_nodule_size || '' }}</span>
                </div>
                <div class="detail-item">
                  <label>基础疾病史：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.lung_cancer_history" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.lung_cancer_history) }}
                    <span v-if="currentRecord.lung_cancer_history_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.lung_cancer_history_other }}）
                    </span>
                  </span>
                </div>
                <div class="detail-item">
                  <label>家族史：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.lung_family_history" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.lung_family_history || currentRecord.family_history) }}
                    <span v-if="currentRecord.lung_family_history_other || currentRecord.family_history_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.lung_family_history_other || currentRecord.family_history_other }}）
                    </span>
                  </span>
                </div>
                <div class="detail-item">
                  <label>药物使用史：</label>
                  <input v-if="isEditingRecord" v-model="currentRecord.lung_medication_history" type="text" style="padding: 5px; border: 1px solid #dcdfe6; border-radius: 4px; width: 200px;" />
                  <span v-else>
                    {{ formatCheckboxValue(currentRecord.lung_medication_history || currentRecord.medication_history) }}
                    <span v-if="currentRecord.lung_medication_other || currentRecord.medication_other" style="color: #409eff; margin-left: 8px;">
                      （其他：{{ currentRecord.lung_medication_other || currentRecord.medication_other }}）
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </section>

          <!-- （三）部分已删除，所有字段已整合到（二）部分 -->
          <!-- 前端表单填写什么，健康档案就显示什么，保持一致 -->
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.patient-detail-view {
  padding: 24px;
}

.loading,
.error {
  text-align: center;
  padding: 60px;
  color: #909399;
}

.error {
  color: #f56c6c;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

/* Tab 样式 */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #e4e7ed;
  padding-bottom: 0;
}

.tab-item {
  padding: 12px 24px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: #606266;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: -2px;
}

.tab-item:hover {
  color: #409eff;
}

.tab-item.active {
  color: #409eff;
  border-bottom-color: #409eff;
  font-weight: 600;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  background: none;
  border: none;
  color: #409eff;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: #ecf5ff;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f5f7fa;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.info-item label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.info-value {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.edit-form {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.form-input {
  padding: 10px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #409eff;
}

.empty {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
}

.data-table th {
  background: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.data-table td {
  color: #606266;
}

.text-truncate {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #409eff;
  color: #fff;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-success {
  background: #67c23a;
  color: #fff;
  padding: 8px 16px;
}

.btn-success:hover {
  background: #85ce61;
}

.btn-text {
  background: none;
  border: none;
  color: #409eff;
  cursor: pointer;
  padding: 8px 16px;
  font-size: 14px;
}

.btn-text:hover {
  background: #ecf5ff;
  border-radius: 4px;
}

.btn-link {
  background: none;
  border: none;
  color: #409eff;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 14px;
  margin-right: 8px;
}

.btn-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-success {
  background: #f0f9ff;
  color: #67c23a;
}

.badge-warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.badge-danger {
  background: #fef0f0;
  color: #f56c6c;
}

.badge-default {
  background: #f4f4f5;
  color: #909399;
}

.badge-birads-low {
  background: #f0f9ff;
  color: #409eff;
}

.badge-birads-medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.badge-birads-high {
  background: #fef0f0;
  color: #f56c6c;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  overflow: auto;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  height: 90vh;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.record-detail-modal {
  width: 1000px;
  max-width: 95vw;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 10;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #909399;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-close:hover {
  background: #f5f7fa;
  color: #606266;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.detail-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  align-items: center;
}

.detail-checkbox-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #303133;
  user-select: none;
}

.detail-other-input {
  margin-top: 10px;
  padding: 6px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  width: 320px;
}

.detail-section {
  margin-bottom: 32px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.detail-item span {
  font-size: 14px;
  color: #303133;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 36px;
  display: flex;
  align-items: center;
}

.detail-item input,
.detail-item select,
.detail-item textarea {
  font-size: 14px;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: border-color 0.3s;
}

.detail-item input:focus,
.detail-item select:focus,
.detail-item textarea:focus {
  outline: none;
  border-color: #409eff;
}

.detail-item textarea {
  resize: vertical;
  font-family: inherit;
}

.btn-default {
  background: #fff;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.btn-default:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

</style>

<script>
export default {
  methods: {
    getBiradsClass(level) {
      if (!level) return 'badge-birads-low'
      if (level <= 2) return 'badge-birads-low'
      if (level === 3) return 'badge-birads-medium'
      return 'badge-birads-high'
    }
  }
}
</script>

