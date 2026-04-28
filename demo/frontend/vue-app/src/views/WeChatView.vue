<script setup>
// 企业微信占位页面
</script>

<template>
  <div class="wechat-view">
    <div class="placeholder">
      <div class="icon">💬</div>
      <h2>企业微信</h2>
      <p>功能开发中，敬请期待...</p>
      <div class="feature-list">
        <div class="feature-item">
          <span class="check">✓</span>
          <span>客户消息管理</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>群发消息</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>客户标签管理</span>
        </div>
        <div class="feature-item">
          <span class="check">✓</span>
          <span>自动回复设置</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wechat-view {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
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

