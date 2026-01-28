<template>
  <div class="risk-score-panel">
    <div class="panel-header">
      <h3>动态风险评分</h3>
      <button 
        v-if="formData" 
        @click="calculateRisk" 
        class="refresh-btn"
        :disabled="isCalculating"
      >
        {{ isCalculating ? '计算中...' : '刷新评分' }}
      </button>
    </div>

    <div v-if="isCalculating" class="loading">
      <span class="spinner"></span>
      <span>正在计算风险评分...</span>
    </div>

      <div v-else-if="riskData" class="risk-content">
      <!-- 总分展示 -->
      <div class="total-score">
        <div class="score-circle" :class="`risk-${getRiskClass(riskData.comprehensive_risk)}`">
          <div class="score-value">{{ riskData.total_score }}</div>
          <div class="score-label">综合评分</div>
        </div>
        <div class="risk-badge" :class="`badge-${getRiskClass(riskData.comprehensive_risk)}`">
          {{ riskData.comprehensive_risk }}
        </div>
      </div>

      <!-- 各维度评分 -->
      <div class="dimensions">
        <div 
          v-for="(dimension, key) in dimensions" 
          :key="key"
          class="dimension-item"
        >
          <div class="dimension-header">
            <span class="dimension-name">{{ dimension.name }}</span>
            <span class="dimension-score">
              {{ '★'.repeat(riskData.risk_scores[key] || 1) }}
              {{ '☆'.repeat(3 - (riskData.risk_scores[key] || 1)) }}
            </span>
          </div>
          
          <!-- 详细信息（可展开） -->
          <div 
            v-if="riskData.risk_details && riskData.risk_details[key] && riskData.risk_details[key].level"
            class="dimension-details"
          >
            <div class="detail-badge" :class="`badge-${getRiskClass(riskData.risk_details[key].level)}`">
              {{ riskData.risk_details[key].level }}
            </div>
            <div class="detail-text">
              <strong>标准：</strong>{{ riskData.risk_details[key].criteria }}
            </div>
          </div>
        </div>
      </div>

      <!-- 监测建议 -->
      <div v-if="riskData.monitoring_recommendations" class="monitoring-section">
        <h4>监测建议</h4>
        <div class="monitoring-item">
          <strong>监测频率：</strong>
          <span>{{ riskData.monitoring_recommendations.monitoring_frequency }}</span>
        </div>
        <div class="monitoring-item">
          <strong>干预优先级：</strong>
          <span>{{ riskData.monitoring_recommendations.intervention_priority }}</span>
        </div>
        
        <div v-if="riskData.monitoring_recommendations.upgrade_conditions && riskData.monitoring_recommendations.upgrade_conditions.length > 0" class="upgrade-conditions">
          <strong>升级条件：</strong>
          <ul>
            <li v-for="(condition, index) in riskData.monitoring_recommendations.upgrade_conditions" :key="index">
              {{ condition }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>请填写表单后查看风险评分</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, defineProps } from 'vue'
import axios from 'axios'

const props = defineProps({
  formData: {
    type: Object,
    required: true
  }
})

const dimensions = {
  family_history: { name: '家族史', weight: 0.30 },
  disease_history: { name: '疾病史', weight: 0.30 },
  imaging: { name: '影像学', weight: 0.25 },
  biomarker: { name: '分子标志物', weight: 0.15 }
}

const riskData = ref(null)
const isCalculating = ref(false)

// 监听表单关键字段变化，自动重新计算
watch(
  () => [
    props.formData.age,
    props.formData.birads_level,
    props.formData.family_history,
    props.formData.breast_disease_history,
    props.formData.tnm_stage,
    props.formData.ca153_value
  ],
  () => {
    // 延迟500ms后自动计算（避免频繁请求）
    setTimeout(() => {
      if (shouldCalculate()) {
        calculateRisk()
      }
    }, 500)
  },
  { deep: true }
)

function shouldCalculate() {
  // 至少有一个关键字段有值
  return props.formData.age || 
         props.formData.birads_level || 
         props.formData.family_history ||
         (props.formData.breast_disease_history && props.formData.breast_disease_history.length > 0)
}

async function calculateRisk() {
  if (!props.formData) return
  
  isCalculating.value = true
  
  try {
    const response = await axios.post('/api/risk/calculate', props.formData, {
      withCredentials: true
    })
    
    if (response.data.success) {
      riskData.value = response.data.data
    } else {
      console.error('风险计算失败:', response.data.message)
    }
  } catch (error) {
    console.error('风险计算请求失败:', error)
  } finally {
    isCalculating.value = false
  }
}

function getRiskClass(riskLevel) {
  if (!riskLevel) return 'low'
  if (riskLevel.includes('高')) return 'high'
  if (riskLevel.includes('中')) return 'medium'
  return 'low'
}

// 初始加载
if (shouldCalculate()) {
  calculateRisk()
}
</script>

<style scoped>
.risk-score-panel {
  background: linear-gradient(135deg, #1e88e5 0%, #00acc1 100%);
  border-radius: 12px;
  padding: 20px;
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  position: sticky;
  top: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 30px;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.total-score {
  text-align: center;
  margin-bottom: 25px;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 auto 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 4px solid white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.score-circle.risk-high {
  border-color: #ff4757;
  background: rgba(255, 71, 87, 0.3);
}

.score-circle.risk-medium {
  border-color: #ffa502;
  background: rgba(255, 165, 2, 0.3);
}

.score-circle.risk-low {
  border-color: #2ed573;
  background: rgba(46, 213, 115, 0.3);
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  line-height: 1;
}

.score-label {
  font-size: 12px;
  margin-top: 5px;
  opacity: 0.9;
}

.risk-badge {
  display: inline-block;
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 16px;
}

.badge-high {
  background: #ff4757;
}

.badge-medium {
  background: #ffa502;
}

.badge-low {
  background: #2ed573;
}

.dimensions {
  margin-bottom: 20px;
}

.dimension-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 10px;
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.dimension-name {
  font-weight: bold;
  font-size: 14px;
}

.dimension-score {
  color: #ffd700;
  font-size: 16px;
}

.dimension-details {
  font-size: 12px;
  opacity: 0.9;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.detail-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  margin-bottom: 5px;
}

.detail-text {
  margin-top: 5px;
  line-height: 1.5;
}

.monitoring-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  font-size: 13px;
}

.monitoring-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
}

.monitoring-item {
  margin-bottom: 10px;
  line-height: 1.6;
}

.monitoring-item strong {
  display: block;
  margin-bottom: 3px;
}

.upgrade-conditions {
  margin-top: 12px;
}

.upgrade-conditions ul {
  margin: 5px 0 0 0;
  padding-left: 20px;
}

.upgrade-conditions li {
  margin-bottom: 5px;
  line-height: 1.5;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  opacity: 0.8;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}
</style>

