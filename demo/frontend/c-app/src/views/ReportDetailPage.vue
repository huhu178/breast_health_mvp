<template>
  <div class="report-detail-page">
    <div class="report-container">
      <div class="report-header">
        <button class="btn-back" @click="$router.push('/reports')">← 返回列表</button>
        <h1>健康报告详情</h1>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="report" class="report-content">
        <div class="report-meta">
          <div class="meta-item">
            <span class="label">报告编号：</span>
            <span class="value">{{ report.report_code }}</span>
          </div>
          <div class="meta-item">
            <span class="label">生成时间：</span>
            <span class="value">{{ report.created_at }}</span>
          </div>
          <div class="meta-item">
            <span class="label">风险评估：</span>
            <span :class="['value', 'risk-badge', report.risk_level]">
              {{ getRiskLabel(report.risk_level) }}
            </span>
          </div>
        </div>

        <div class="report-body" v-html="report.report_html"></div>

        <div class="report-actions">
          <button class="btn btn-primary" @click="downloadPDF">
            📥 下载PDF报告
          </button>
        </div>
      </div>

      <div v-else class="error-state">
        <p>报告不存在或已过期</p>
        <router-link to="/" class="btn btn-outline">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { cAPI } from '../services/api'

const route = useRoute()
const loading = ref(true)
const report = ref(null)

onMounted(async () => {
  await loadReport()
})

const loadReport = async () => {
  try {
    const reportId = route.params.id
    const token = route.query.token
    
    if (!token) {
      alert('缺少访问令牌，请从我的报告页面进入')
      return
    }
    
    const response = await cAPI.reports.getReport(reportId, token)
    
    // 响应格式：{ code: 0, data: {...}, message: '...' }
    if (response.code === 0) {
      report.value = response.data
    } else {
      alert('加载报告失败：' + response.message)
    }
  } catch (error) {
    console.error('Load report failed:', error)
    alert('加载报告失败，请重试')
  } finally {
    loading.value = false
  }
}

const downloadPDF = async () => {
  try {
    const reportId = route.params.id
    const token = route.query.token
    
    // 直接使用浏览器下载
    const downloadUrl = `/api/c/reports/${reportId}/pdf?token=${token}`
    
    // 创建隐藏的a标签触发下载
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `健康报告_${report.value.report_code}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // 提示用户
    setTimeout(() => {
      alert('✅ PDF下载已开始，请稍候...')
    }, 500)
  } catch (error) {
    console.error('Download PDF failed:', error)
    alert('下载失败，请稍后重试')
  }
}

const getRiskLabel = (level) => {
  const labels = {
    'low': '低风险',
    'medium': '中风险',
    'high': '高风险'
  }
  return labels[level] || '未评估'
}
</script>

<style scoped>
.report-detail-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

.report-container {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.report-header {
  position: relative;
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
}

.btn-back {
  position: absolute;
  left: 0;
  top: 0;
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 1rem;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 3rem;
}

.report-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--bg-gray);
  border-radius: 0.75rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-item .label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.meta-item .value {
  font-weight: 500;
  color: var(--text-primary);
}

.risk-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
}

.risk-badge.low {
  background: #d1fae5;
  color: #065f46;
}

.risk-badge.medium {
  background: #fed7aa;
  color: #92400e;
}

.risk-badge.high {
  background: #fecaca;
  color: #991b1b;
}

.report-body {
  margin-bottom: 2rem;
  line-height: 1.8;
}

.report-body :deep(h1),
.report-body :deep(h2),
.report-body :deep(h3) {
  color: var(--primary-color);
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.report-body :deep(p) {
  margin-bottom: 1rem;
}

.report-actions {
  text-align: center;
  padding-top: 2rem;
  border-top: 2px solid var(--border-color);
}

@media (max-width: 768px) {
  .report-container {
    padding: 1.5rem;
  }
  
  .report-meta {
    grid-template-columns: 1fr;
  }
}
</style>

