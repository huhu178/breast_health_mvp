<template>
  <div class="home-page">
    <!-- 头部导航 -->
    <header class="header">
      <div class="container">
        <div class="nav">
          <h1 class="logo">🏥 乳腺健康管理</h1>
          <div class="nav-actions">
            <router-link to="/login" class="btn btn-outline">登录</router-link>
          </div>
        </div>
      </div>
    </header>

    <!-- 英雄区 -->
    <section class="hero">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">查看您的健康报告</h1>
          <p class="hero-subtitle">
            专业的乳腺结节健康管理报告 · 随时随地查看
          </p>
          <div class="hero-actions">
            <button class="btn btn-primary btn-lg" @click="handleWechatLogin">
              💬 微信登录查看
            </button>
            <router-link to="/verify" class="btn btn-outline btn-lg">
              手机号验证
            </router-link>
          </div>
        </div>
        <div class="hero-image">
          <div class="hero-illustration">
            <div class="illustration-circle">
              <svg width="200" height="200" viewBox="0 0 200 200">
                <circle cx="100" cy="100" r="80" fill="#667eea" opacity="0.1"/>
                <circle cx="100" cy="100" r="60" fill="#764ba2" opacity="0.2"/>
                <text x="100" y="110" text-anchor="middle" font-size="60" fill="#667eea">💙</text>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 特色功能 -->
    <section id="features" class="features">
      <div class="container">
        <h2 class="section-title">我们的服务</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>AI智能问诊</h3>
            <p>通过人工智能引导式对话，全面了解您的健康状况</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>专业报告解读</h3>
            <p>基于医学知识库，生成易懂的个性化健康报告</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">💡</div>
            <h3>健康建议</h3>
            <p>提供针对性的生活方式和随访建议</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h3>隐私保护</h3>
            <p>严格保护您的个人健康信息安全</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 使用流程 -->
    <section class="process">
      <div class="container">
        <h2 class="section-title">简单三步，获得专业报告</h2>
        <div class="process-steps">
          <div class="process-step">
            <div class="step-number">1</div>
            <h3>登录注册</h3>
            <p>使用手机号或微信快速登录</p>
          </div>
          <div class="process-arrow">→</div>
          <div class="process-step">
            <div class="step-number">2</div>
            <h3>AI问诊</h3>
            <p>回答AI顾问的问题，提供健康信息</p>
          </div>
          <div class="process-arrow">→</div>
          <div class="process-step">
            <div class="step-number">3</div>
            <h3>查看报告</h3>
            <p>获得专业健康报告和建议</p>
          </div>
        </div>
        <div class="process-cta">
          <router-link to="/login" class="btn btn-primary btn-lg">
            开始使用
          </router-link>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="footer">
      <div class="container">
        <p>© 2025 乳腺健康管理平台 | 专业 · 可信赖 · 关爱</p>
        <p class="footer-disclaimer">
          ⚠️ 本平台提供的健康建议仅供参考，不能替代专业医疗诊断
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// 首页组件
const handleWechatLogin = () => {
  // 微信登录逻辑
  alert('请在微信中打开此页面，或扫描二维码登录\n\n开发中...')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* 头部导航 */
.header {
  background: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
}

/* 英雄区 */
.hero {
  padding: 4rem 0;
}

.hero .container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
}

.hero-content {
  padding: 2rem 0;
}

.hero-title {
  font-size: 3rem;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 1rem;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

.hero-illustration {
  display: flex;
  justify-content: center;
  align-items: center;
}

.illustration-circle {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

/* 特色功能 */
.features {
  padding: 4rem 0;
  background: white;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 3rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  border-radius: 1rem;
  background: var(--bg-gray);
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-10px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 使用流程 */
.process {
  padding: 4rem 0;
}

.process-steps {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  margin-bottom: 3rem;
}

.process-step {
  flex: 1;
  max-width: 250px;
  text-align: center;
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.step-number {
  width: 60px;
  height: 60px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.process-arrow {
  font-size: 2rem;
  color: var(--primary-color);
  font-weight: bold;
}

.process-step h3 {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.process-step p {
  color: var(--text-secondary);
}

.process-cta {
  text-align: center;
}

/* 底部 */
.footer {
  background: #2d3748;
  color: white;
  padding: 3rem 0;
  text-align: center;
}

.footer p {
  margin-bottom: 0.5rem;
}

.footer-disclaimer {
  color: #fbbf24;
  font-size: 0.9rem;
}

/* 响应式 */
@media (max-width: 768px) {
  .hero .container {
    grid-template-columns: 1fr;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-actions {
    flex-direction: column;
  }
  
  .hero-actions .btn {
    width: 100%;
  }
  
  .process-steps {
    flex-direction: column;
  }
  
  .process-arrow {
    transform: rotate(90deg);
  }
}
</style>

