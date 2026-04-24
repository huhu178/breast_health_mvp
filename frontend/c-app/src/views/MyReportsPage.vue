<template>
  <div class="my-reports-page">
    <header class="page-header">
      <h1>💙 我的健康报告</h1>
      <button class="new-consultation-btn" @click="startNewConsultation">
        开始新咨询
      </button>
    </header>

    <div class="container">
      <!-- Loading -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- 报告列表 -->
      <div v-else-if="reports.length > 0" class="reports-list">
        <div 
          v-for="report in reports" 
          :key="report.id" 
          class="report-card"
          @click="viewReport(report)"
        >
          <div class="report-header">
            <span class="report-code">{{ report.report_code }}</span>
            <span :class="['risk-badge', getRiskClass(report.risk_level)]">
              {{ getRiskLabel(report.risk_level) }}
            </span>
          </div>
          <div class="report-summary">
            {{ report.report_summary || '暂无摘要' }}
          </div>
          <div class="report-footer">
            <span class="report-date">{{ formatDate(report.generated_at) }}</span>
            <div class="report-actions">
              <button class="btn-view" @click.stop="viewReport(report)">
                查看详情
              </button>
              <button class="btn-download" @click.stop="downloadPDF(report)">
                下载PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">📋</div>
        <h2>您还没有健康报告</h2>
        <p>开始AI问诊，获取专业健康报告</p>
        <button class="start-btn" @click="startNewConsultation">
          开始免费咨询
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'MyReportsPage',
  setup() {
    const router = useRouter()
    const loading = ref(true)
    const reports = ref([])

    // 加载报告列表
    const loadReports = async () => {
      try {
        loading.value = true
        // 从localStorage获取手机号
        const phone = localStorage.getItem('user_phone')
        if (!phone) {
          // 如果没有登录信息，跳转到首页
          router.push('/')
          return
        }

        // 调用后端接口查询报告列表
        const response = await api.get(`/c/reports/list?phone=${phone}`)
        
        // 响应格式：{ code: 0, data: [...], message: '...' }
        if (response.code === 0) {
          reports.value = response.data || []
        } else {
          console.error('查询失败:', response.message)
          reports.value = []
        }
      } catch (error) {
        console.error('加载报告失败:', error)
        alert('加载报告失败，请重试')
        reports.value = []
      } finally {
        loading.value = false
      }
    }

    // 查看报告详情
    const viewReport = (report) => {
      // 传递reportId和token到详情页
      router.push({
        path: `/report/${report.id}`,
        query: { token: report.download_token }
      })
    }

    // 下载PDF
    const downloadPDF = async (report) => {
      try {
        // 直接使用浏览器下载
        const downloadUrl = `/api/c/reports/${report.id}/pdf?token=${report.download_token}`
        
        // 创建隐藏的a标签触发下载
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = `健康报告_${report.report_code}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // 提示用户
        setTimeout(() => {
          alert('✅ PDF下载已开始，请稍候...')
        }, 500)
      } catch (error) {
        console.error('下载PDF失败:', error)
        alert('下载PDF失败，请重试')
      }
    }

    // 开始新咨询
    const startNewConsultation = () => {
      router.push('/')
    }

    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return '未知日期'
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    // 获取风险等级样式
    const getRiskClass = (riskLevel) => {
      const level = (riskLevel || '').toLowerCase()
      if (level.includes('低危') || level.includes('良性')) return 'risk-low'
      if (level.includes('中危')) return 'risk-medium'
      if (level.includes('高危')) return 'risk-high'
      return 'risk-unknown'
    }

    // 获取风险等级标签
    const getRiskLabel = (riskLevel) => {
      if (!riskLevel) return '未知'
      return riskLevel
    }

    onMounted(() => {
      loadReports()
    })

    return {
      loading,
      reports,
      viewReport,
      downloadPDF,
      startNewConsultation,
      formatDate,
      getRiskClass,
      getRiskLabel
    }
  }
}
</script>

<style scoped>
.my-reports-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  color: white;
}

.page-header h1 {
  font-size: 28px;
  margin: 0;
}

.new-consultation-btn {
  background: white;
  color: #667eea;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.new-consultation-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

/* Loading */
.loading {
  text-align: center;
  padding: 60px 20px;
  color: white;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 报告列表 */
.reports-list {
  display: grid;
  gap: 20px;
}

.report-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.report-code {
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

.risk-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.risk-low {
  background: #e8f5e9;
  color: #2e7d32;
}

.risk-medium {
  background: #fff3e0;
  color: #ef6c00;
}

.risk-high {
  background: #ffebee;
  color: #c62828;
}

.risk-unknown {
  background: #f5f5f5;
  color: #666;
}

.report-summary {
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
  font-size: 14px;
}

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.report-date {
  color: #999;
  font-size: 13px;
}

.report-actions {
  display: flex;
  gap: 10px;
}

.btn-view,
.btn-download {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-view {
  background: #667eea;
  color: white;
}

.btn-view:hover {
  background: #5568d3;
}

.btn-download {
  background: #f5f5f5;
  color: #666;
}

.btn-download:hover {
  background: #e0e0e0;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.3;
}

.empty-state h2 {
  color: #333;
  margin-bottom: 12px;
  font-size: 24px;
}

.empty-state p {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

.start-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 16px 40px;
  border-radius: 25px;
  font-size: 18px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102,126,234,0.4);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .report-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .report-actions {
    flex-direction: column;
  }

  .btn-view,
  .btn-download {
    width: 100%;
  }
}
</style>
