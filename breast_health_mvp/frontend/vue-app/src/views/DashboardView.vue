<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 定义结节类型卡片数据
const noduleTypes = [
  {
    id: 'breast',
    title: '乳腺结节',
    color: '#1e88e5',
    route: '/patients',
    borderColor: '#1e88e5'
  },
  {
    id: 'lung',
    title: '肺结节',
    color: '#00acc1',
    route: '/patients',
    borderColor: '#00acc1'
  },
  {
    id: 'thyroid',
    title: '甲状腺结节',
    color: '#26a69a',
    route: '/patients',
    borderColor: '#26a69a'
  },
  {
    id: 'breast_lung',
    title: '乳腺+肺',
    color: '#43a047',
    route: '/patients',
    borderColor: '#43a047'
  },
  {
    id: 'breast_thyroid',
    title: '乳腺+甲状腺',
    color: '#5e35b1',
    route: '/patients',
    borderColor: '#5e35b1'
  },
  {
    id: 'lung_thyroid',
    title: '肺+甲状腺',
    color: '#00897b',
    route: '/patients',
    borderColor: '#00897b'
  },
  {
    id: 'triple',
    title: '三结节',
    color: '#00838f',
    route: '/patients',
    borderColor: '#00838f'
  }
]

// 点击卡片跳转
function navigateToNodule(nodule) {
  router.push({
    path: nodule.route,
    query: { nodule_type: nodule.id }
  })
}
</script>

<template>
  <div class="nodule-dashboard">
    <!-- 页面标题 -->
    <header class="page-header">
      <h1 class="main-title">多结节健康管理系统</h1>
      <p class="subtitle">请选择患者的结节类型开始管理</p>
    </header>

    <!-- 结节类型卡片网格 -->
    <div class="nodule-grid">
      <div
        v-for="nodule in noduleTypes"
        :key="nodule.id"
        class="nodule-card"
        @click="navigateToNodule(nodule)"
      >
        <div class="card-border" :style="{ backgroundColor: nodule.borderColor }"></div>
        <div class="card-content">
          <h3 class="card-title">{{ nodule.title }}</h3>
          <button class="card-action" :style="{ color: nodule.color }">
            查看/创建 →
          </button>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <section class="quick-actions">
      <h2 class="section-title">快速操作</h2>
      <div class="action-buttons">
        <button class="action-btn" @click="router.push('/wechat')">
          企业微信
        </button>
        <button class="action-btn" @click="router.push('/customers')">
          获客管理
        </button>
        <button class="action-btn" @click="router.push('/knowledge')">
          知识库管理
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.nodule-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 32px 40px;
}

/* 页面标题 */
.page-header {
  margin-bottom: 32px;
  padding: 28px 32px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 1600px;
  margin-left: auto;
  margin-right: auto;
}

.main-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #1e88e5 0%, #00acc1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

/* 结节类型卡片网格 */
.nodule-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 25px;
  max-width: 1600px;
  margin: 0 auto 50px;
}

@media (max-width: 1400px) {
  .nodule-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .nodule-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .nodule-grid {
    grid-template-columns: 1fr;
  }
}

/* 结节卡片 */
.nodule-card {
  background: white;
  border-radius: 12px;
  min-height: 160px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
  display: flex;
}

.nodule-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e1;
}

/* 左侧彩色边框 */
.card-border {
  width: 4px;
  flex-shrink: 0;
  transition: width 0.3s ease;
}

.nodule-card:hover .card-border {
  width: 5px;
}

/* 卡片内容 */
.card-content {
  flex: 1;
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.card-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  background: none;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: auto;
  color: inherit;
}

.card-action:hover {
  transform: translateX(2px);
}

/* 快速操作区 */
.quick-actions {
  max-width: 1600px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 24px 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #ffffff;
  background: linear-gradient(135deg, #1e88e5 0%, #00acc1 100%);
  box-shadow: 0 2px 4px rgba(30, 136, 229, 0.2);
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(30, 136, 229, 0.3);
}
</style>
