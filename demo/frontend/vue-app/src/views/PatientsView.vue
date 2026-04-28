<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const patients = ref([])
const isLoading = ref(true)
const searchKeyword = ref('')
const currentPage = ref(1)
const totalPatients = ref(0)
const noduleType = ref(route.query.nodule_type || '')  // 从路由获取结节类型
// 患者来源：all/b_end/c_end
const patientSource = ref(route.query.source || 'b_end')

/**
 * @isdoc
 * @description 当前页多选：仅作用于当前列表页（翻页/重新搜索会清空）
 */
const selectedPatientIds = ref(new Set())

/**
 * @isdoc
 * @description 是否全选当前页
 */
const isAllSelectedOnPage = ref(false)

/**
 * @isdoc
 * @description 批量模式开关：默认不显示复选框；开启后才显示多选与批量删除
 */
const isBatchMode = ref(false)

async function loadPatients() {
  isLoading.value = true
  try {
    const response = await axios.get('/api/b/patients', {
      params: {
        page: currentPage.value,
        per_page: 20,
        type: patientSource.value || 'all',
        search: searchKeyword.value,
        nodule_type: noduleType.value  // 传递结节类型筛选
      },
      withCredentials: true
    })
    
    if (response.data.success) {
      patients.value = response.data.data.items || []
      totalPatients.value = response.data.data.total || 0
      // 刷新列表时清空勾选（避免跨页误删）
      selectedPatientIds.value = new Set()
      isAllSelectedOnPage.value = false
      // 列表刷新时退出批量模式（避免筛选/翻页后误删）
      isBatchMode.value = false
    }
  } catch (error) {
    console.error('加载患者列表失败:', error)
  } finally {
    isLoading.value = false
  }
}

function viewDetail(patientId) {
  router.push({
    path: `/patients/${patientId}`,
    query: {
      source: patientSource.value || 'all'
    }
  })
}

async function createRecord(patientId) {
  // 根据当前页面的结节类型筛选条件跳转到对应的表单
  const routeMap = (realPatientId) => ({
    breast: `/records/new/${realPatientId}`,
    lung: `/records/lung/${realPatientId}`,
    thyroid: `/records/thyroid/${realPatientId}`,
    breast_lung: `/records/breast-lung/${realPatientId}`,
    breast_thyroid: `/records/breast-thyroid/${realPatientId}`,
    lung_thyroid: `/records/lung-thyroid/${realPatientId}`,
    triple: `/records/triple/${realPatientId}`
  })

  // 先根据当前行找到完整患者对象（用于获取 nodule_type 等）
  const patient = patients.value.find(p => p.id === patientId)

  // 默认认为传入的是 B 端患者 ID
  let realPatientId = patientId

  // 如果当前列表是 C 端患者（type=c_end），需要先把 C 端患者同步为 B 端患者
  if (patientSource.value === 'c_end') {
    try {
      const resp = await axios.post(
        `/api/b/patients/from-c/${patientId}/ensure-b`,
        {},
        { withCredentials: true }
      )
      if (!resp.data?.success) {
        alert(resp.data?.message || '无法为该C端患者创建B端档案')
        return
      }
      realPatientId = resp.data.data.b_patient_id
    } catch (error) {
      console.error('从C端同步B端患者失败:', error)
      alert('无法为该C端患者创建B端档案：' + (error.response?.data?.message || error.message))
      return
    }
  }

  // 优先使用筛选条件中的结节类型，其次使用患者自身的结节类型
  const baseNoduleType = noduleType.value || patient?.nodule_type || ''
  const routes = routeMap(realPatientId)

  // 如果有结节类型筛选，使用对应的路由；否则默认跳转到患者详情页（已是 B 端患者 ID）
  const targetRoute = baseNoduleType ? (routes[baseNoduleType] || `/patients/${realPatientId}`) : `/patients/${realPatientId}`
  router.push(targetRoute)
}

function addPatient() {
  // 显示添加患者对话框
  showAddDialog.value = true
}

/**
 * @isdoc
 * @description 切换单行勾选状态
 * @param {number} patientId
 * @param {boolean} checked
 */
function toggleSelectPatient(patientId, checked) {
  const next = new Set(selectedPatientIds.value)
  if (checked) next.add(patientId)
  else next.delete(patientId)
  selectedPatientIds.value = next

  // 同步“全选本页”状态
  const idsOnPage = patients.value.map(p => p.id)
  isAllSelectedOnPage.value = idsOnPage.length > 0 && idsOnPage.every(id => next.has(id))
}

/**
 * @isdoc
 * @description 全选/取消全选（仅当前页）
 * @param {boolean} checked
 */
function toggleSelectAllOnPage(checked) {
  const next = new Set(selectedPatientIds.value)
  const idsOnPage = patients.value.map(p => p.id)
  if (checked) {
    idsOnPage.forEach(id => next.add(id))
  } else {
    idsOnPage.forEach(id => next.delete(id))
  }
  selectedPatientIds.value = next
  isAllSelectedOnPage.value = checked
}

/**
 * @isdoc
 * @description 进入批量模式：显示复选框列与批量删除按钮
 */
function enterBatchMode() {
  isBatchMode.value = true
  selectedPatientIds.value = new Set()
  isAllSelectedOnPage.value = false
}

/**
 * @isdoc
 * @description 退出批量模式：隐藏复选框并清空勾选
 */
function exitBatchMode() {
  isBatchMode.value = false
  selectedPatientIds.value = new Set()
  isAllSelectedOnPage.value = false
}

/**
 * @isdoc
 * @description 批量删除患者（仅删除当前勾选的患者）
 * - 复用单个删除接口：DELETE /api/b/patients/:id?type=b_end
 * - 串行删除，避免服务端压力过大；失败会汇总提示
 */
async function batchDeleteSelectedPatients() {
  const ids = Array.from(selectedPatientIds.value)
  if (ids.length === 0) {
    alert('请先勾选需要删除的患者')
    return
  }

  if (!confirm(`⚠️ 确认批量删除选中的 ${ids.length} 个患者吗？\n\n此操作不可恢复，且会删除关联档案/报告等数据。`)) {
    return
  }

  const failed = []
  for (const id of ids) {
    try {
      await axios.delete(`/api/b/patients/${id}`, {
        params: { type: 'b_end' },
        withCredentials: true
      })
    } catch (e) {
      failed.push({
        id,
        message: e.response?.data?.message || e.message
      })
    }
  }

  await loadPatients()

  if (failed.length === 0) {
    alert('✅ 批量删除成功')
    return
  }

  const preview = failed.slice(0, 5).map(x => `- 患者ID ${x.id}: ${x.message}`).join('\n')
  alert(`⚠️ 批量删除完成，但有 ${failed.length} 个失败：\n${preview}${failed.length > 5 ? '\n...' : ''}`)
}

const showAddDialog = ref(false)
const newPatient = ref({
  name: '',
  phone: '',
  wechat_id: '',
  age: '',
  gender: '女',
  id_number: ''
})

async function submitNewPatient() {
  // 验证必填项
  if (!newPatient.value.name || !newPatient.value.name.trim()) {
    alert('请输入姓名！')
    return
  }
  
  if (!newPatient.value.phone || !newPatient.value.phone.trim()) {
    alert('请输入手机号！')
    return
  }
  
  // 验证手机号格式（11位数字）
  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(newPatient.value.phone)) {
    alert('请输入正确的11位手机号！')
    return
  }
  
  // 如果填写了身份证号，验证格式（15位或18位）
  if (newPatient.value.id_number && newPatient.value.id_number.trim()) {
    const idRegex = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
    if (!idRegex.test(newPatient.value.id_number)) {
      alert('请输入正确的身份证号（15位或18位）！')
      return
    }
  }
  
  try {
    const patientData = {
      ...newPatient.value,
      nodule_type: noduleType.value  // 自动填充结节类型
    }

    const response = await axios.post('/api/b/patients', patientData, {
      withCredentials: true
    })

    if (response.data.success) {
      alert('添加成功！')
      showAddDialog.value = false
      newPatient.value = { name: '', phone: '', wechat_id: '', age: '', gender: '女', id_number: '' }
      loadPatients()
    }
  } catch (error) {
    alert('添加失败：' + (error.response?.data?.message || error.message))
  }
}

function cancelAdd() {
  showAddDialog.value = false
  newPatient.value = { name: '', phone: '', wechat_id: '', age: '', gender: '女', id_number: '' }
}

onMounted(() => {
  loadPatients()
})
</script>

<template>
  <div class="patients-view">
    <header class="page-header">
      <h2 class="page-title">👥 患者管理</h2>
      <div class="header-actions">
        <!-- 患者来源筛选：全部 / B端 / C端 -->
        <select
          v-model="patientSource"
          class="source-select"
          @change="() => { currentPage = 1; loadPatients(); }"
          title="按来源筛选患者"
        >
          <option value="all">全部来源</option>
          <option value="b_end">B端患者</option>
          <option value="c_end">C端患者</option>
        </select>
        <template v-if="isBatchMode">
          <button
            class="btn btn-danger"
            :disabled="selectedPatientIds.size === 0"
            @click="batchDeleteSelectedPatients"
            title="仅删除当前页已勾选的患者"
          >
            删除已选（{{ selectedPatientIds.size }}）
          </button>
          <button class="btn btn-default" @click="exitBatchMode">取消</button>
        </template>
        <template v-else>
          <button class="btn btn-danger" @click="enterBatchMode" title="进入批量删除模式">
            批量删除
          </button>
        </template>
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索患者姓名或手机号"
          class="search-input"
          @keyup.enter="loadPatients"
        />
        <button class="btn btn-secondary" @click="loadPatients">搜索</button>
        <button class="btn btn-primary" @click="addPatient">+ 添加患者</button>
      </div>
    </header>
    
    <section class="card">
      <div v-if="isLoading" class="loading">加载中...</div>
      
      <table v-else class="data-table">
        <thead>
          <tr>
            <th v-if="isBatchMode" class="checkbox-col">
              <input
                type="checkbox"
                :checked="isAllSelectedOnPage"
                :disabled="patients.length === 0"
                @change="toggleSelectAllOnPage($event.target.checked)"
                title="全选当前页"
              />
            </th>
            <th>患者编号</th>
            <th>来源</th>
            <th>姓名</th>
            <th>性别</th>
            <th>年龄</th>
            <th>手机号</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!patients.length">
            <td :colspan="isBatchMode ? 8 : 7" class="empty">暂无患者数据</td>
          </tr>
          <tr v-for="patient in patients" :key="patient.id">
            <td v-if="isBatchMode" class="checkbox-col">
              <input
                type="checkbox"
                :checked="selectedPatientIds.has(patient.id)"
                @change="toggleSelectPatient(patient.id, $event.target.checked)"
              />
            </td>
            <td>{{ patient.patient_code }}</td>
            <td>{{ patient.patient_type === 'c_end' ? 'C端' : 'B端' }}</td>
            <td>{{ patient.name }}</td>
            <td>{{ patient.gender || '-' }}</td>
            <td>{{ patient.age || '-' }}</td>
            <td>{{ patient.phone || '-' }}</td>
            <td>{{ patient.created_at }}</td>
            <td>
              <button class="btn-link" @click="viewDetail(patient.id)">查看</button>
              <button class="btn-link" @click="createRecord(patient.id)">创建档案</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="totalPatients > 0" class="pagination">
        <span>共 {{ totalPatients }} 条</span>
      </div>
    </section>

    <!-- 添加患者对话框 -->
    <div v-if="showAddDialog" class="modal-overlay" @click="cancelAdd">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>添加患者</h3>
          <button class="close-btn" @click="cancelAdd">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>姓名 *</label>
            <input v-model="newPatient.name" type="text" class="form-input" placeholder="请输入姓名" />
          </div>
          <div class="form-group">
            <label>手机号 *</label>
            <input v-model="newPatient.phone" type="text" class="form-input" placeholder="请输入手机号" />
          </div>
          <div class="form-group">
            <label>微信号</label>
            <input v-model="newPatient.wechat_id" type="text" class="form-input" placeholder="请输入微信号" />
          </div>
          <div class="form-group">
            <label>身份证号</label>
            <input v-model="newPatient.id_number" type="text" class="form-input" placeholder="请输入身份证号" />
          </div>
          <div class="form-row">
            <div class="form-group" style="flex: 1;">
              <label>年龄</label>
              <input v-model="newPatient.age" type="number" class="form-input" placeholder="请输入年龄" />
            </div>
            <div class="form-group" style="flex: 1; margin-left: 12px;">
              <label>性别</label>
              <select v-model="newPatient.gender" class="form-input">
                <option value="女">女</option>
                <option value="男">男</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-default" @click="cancelAdd">取消</button>
          <button class="btn btn-primary" @click="submitNewPatient">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.patients-view {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.checkbox-col {
  width: 44px;
  text-align: center;
}

.search-input {
  padding: 10px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  width: 300px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #409eff;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.loading {
  text-align: center;
  padding: 60px;
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

.empty {
  text-align: center;
  color: #909399;
  padding: 60px;
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

.btn-secondary {
  background: #909399;
  color: #fff;
}

.btn-secondary:hover {
  background: #a6a9ad;
}

.btn-default {
  background: #fff;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.btn-default:hover {
  color: #409eff;
  border-color: #409eff;
}

.btn-link {
  background: none;
  border: none;
  color: #409eff;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 14px;
}

.btn-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.pagination {
  margin-top: 20px;
  text-align: right;
  color: #606266;
  font-size: 14px;
}

/* 对话框样式 */
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
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #909399;
  cursor: pointer;
  line-height: 1;
}

.close-btn:hover {
  color: #409eff;
}

.modal-body {
  padding: 24px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #409eff;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #ebeef5;
}
</style>

