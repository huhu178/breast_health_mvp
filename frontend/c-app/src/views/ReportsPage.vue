<template>
  <div class="reports-page">
    <div class="container">
      <h1>我的报告</h1>
      <div class="reports-list">
        <div v-if="reports.length === 0" class="empty-state">
          <p>暂无报告</p>
          <router-link to="/chat" class="btn btn-primary">开始咨询</router-link>
        </div>
        <div v-else v-for="report in reports" :key="report.id" class="report-card">
          <div class="report-info">
            <h3>健康报告 {{ report.report_code }}</h3>
            <p>生成时间：{{ report.created_at }}</p>
            <span :class="['risk-badge', report.risk_level]">
              {{ getRiskLabel(report.risk_level) }}
            </span>
          </div>
          <div class="report-actions">
            <router-link :to="`/report/${report.id}?token=${report.download_token}`" class="btn btn-primary">
              查看详情
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { cAPI } from '../services/api'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const reports = ref([])

onMounted(async () => {
  await loadReports()
})

const loadReports = async () => {
  try {
    const phone = userStore.userInfo?.phone
    if (!phone) return
    
    const response = await cAPI.reports.verifyPhone(phone)
    if (response.success) {
      reports.value = response.data.reports || []
    }
  } catch (error) {
    console.error('Load reports failed:', error)
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
.reports-page {
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.container h1 {
  margin-bottom: 2rem;
  color: var(--text-primary);
}

.reports-list {
  display: grid;
  gap: 1.5rem;
}

.report-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.report-info h3 {
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.report-info p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.risk-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  margin-top: 0.5rem;
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

.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 1rem;
}

.empty-state p {
  margin-bottom: 1rem;
  color: var(--text-secondary);
}
</style>

