<script setup>
// 获客管理（C端）占位页面
</script>

<template>
  <div class="customers-view">
    <div class="placeholder">
      <div class="icon">🎯</div>
      <h2>获客管理（C端）</h2>
      <p>功能开发中，敬请期待...</p>
      <div class="feature-list">
        <div class="feature-item">
          <span class="check">✓</span>
          <span>C端客户列表</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>AI对话记录</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>C端报告管理</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>客户转化跟踪</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.customers-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.placeholder {
  text-align: center;
  padding: 60px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 500px;
}

.icon {
  font-size: 80px;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

h2 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 12px;
}

p {
  color: #909399;
  font-size: 16px;
  margin-bottom: 40px;
}

.feature-list {
  text-align: left;
  display: inline-block;
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  color: #606266;
  font-size: 15px;
}

.check {
  color: #67c23a;
  font-weight: bold;
  margin-right: 12px;
  font-size: 18px;
}
</style>

