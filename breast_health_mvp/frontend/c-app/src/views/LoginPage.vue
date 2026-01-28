<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1>🏥 乳腺健康管理</h1>
          <p>开始您的健康咨询之旅</p>
        </div>

        <div class="login-form">
          <!-- 手机号登录 -->
          <div class="form-section">
            <h2>手机号登录</h2>
            <div class="input-group">
              <label>手机号</label>
              <input 
                v-model="phone" 
                type="tel" 
                placeholder="请输入手机号"
                maxlength="11"
                @keyup.enter="handlePhoneLogin"
              />
            </div>
            <div class="input-group">
              <label>姓名</label>
              <input 
                v-model="name" 
                type="text" 
                placeholder="请输入您的姓名"
                @keyup.enter="handlePhoneLogin"
              />
            </div>
            <button 
              class="btn btn-primary"
              :disabled="loading"
              @click="handlePhoneLogin"
            >
              <span v-if="loading" class="loading"></span>
              <span v-else>立即登录</span>
            </button>
          </div>

          <!-- 微信登录 -->
          <div class="divider">
            <span>或</span>
          </div>

          <div class="form-section">
            <button class="btn btn-wechat" @click="handleWechatLogin">
              <span>💬</span>
              微信快捷登录
            </button>
          </div>
        </div>

        <div class="login-footer">
          <p class="disclaimer">
            登录即表示您同意我们的<a href="#">隐私政策</a>和<a href="#">服务条款</a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const phone = ref('')
const name = ref('')
const loading = ref(false)

// 手机号登录
const handlePhoneLogin = async () => {
  if (!phone.value) {
    alert('请输入手机号')
    return
  }
  
  if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    alert('手机号格式不正确')
    return
  }
  
  if (!name.value) {
    alert('请输入姓名')
    return
  }
  
  loading.value = true
  
  try {
    const result = await userStore.loginByPhone(phone.value, name.value)
    
    if (result.success) {
      alert('登录成功！')
      router.push('/chat')
    } else {
      alert('登录失败：' + result.message)
    }
  } finally {
    loading.value = false
  }
}

// 微信登录
const handleWechatLogin = () => {
  alert('微信登录功能开发中...\n请使用手机号登录')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.login-container {
  width: 100%;
  max-width: 450px;
}

.login-card {
  background: white;
  border-radius: 1.5rem;
  padding: 3rem;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h1 {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.login-header p {
  color: var(--text-secondary);
}

.form-section {
  margin-bottom: 1.5rem;
}

.form-section h2 {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.divider {
  text-align: center;
  margin: 2rem 0;
  position: relative;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: var(--border-color);
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.divider span {
  background: white;
  padding: 0 1rem;
  color: var(--text-secondary);
  position: relative;
  z-index: 1;
}

.btn-wechat {
  background: #07c160;
  color: white;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-wechat:hover {
  background: #06ad56;
}

.btn-wechat span:first-child {
  font-size: 1.5rem;
}

.login-footer {
  margin-top: 2rem;
  text-align: center;
}

.disclaimer {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.disclaimer a {
  color: var(--primary-color);
  text-decoration: none;
}

.disclaimer a:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-card {
    padding: 2rem 1.5rem;
  }
}
</style>

