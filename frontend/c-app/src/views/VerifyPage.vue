<template>
  <div class="verify-page">
    <div class="verify-container">
      <div class="verify-card">
        <div class="verify-header">
          <button class="btn-back" @click="$router.push('/')">← 返回</button>
          <h1>验证手机号</h1>
          <p>输入您的手机号查看健康报告</p>
        </div>

        <div class="verify-form">
          <div class="input-group">
            <label>手机号</label>
            <input 
              v-model="phone" 
              type="tel" 
              placeholder="请输入您的手机号"
              maxlength="11"
              @keyup.enter="handleVerify"
            />
          </div>

          <button 
            class="btn btn-primary"
            :disabled="loading || !phone"
            @click="handleVerify"
          >
            <span v-if="loading" class="loading"></span>
            <span v-else>查看我的报告</span>
          </button>
        </div>

        <div class="verify-tips">
          <p>💡 提示：</p>
          <ul>
            <li>请输入您在咨询时使用的手机号</li>
            <li>如果您是通过微信咨询的，请在微信中打开此页面</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { cAPI } from '../services/api'

const router = useRouter()
const phone = ref('')
const loading = ref(false)

// 验证手机号
const handleVerify = async () => {
  if (!phone.value) {
    alert('请输入手机号')
    return
  }
  
  if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    alert('手机号格式不正确')
    return
  }
  
  loading.value = true
  
  try {
    const response = await cAPI.reports.verifyPhone(phone.value)
    
    if (response.success) {
      // 保存手机号到本地
      localStorage.setItem('verified_phone', phone.value)
      
      if (response.data.reports && response.data.reports.length > 0) {
        // 有报告，跳转到报告列表
        router.push('/reports')
      } else {
        alert('未找到您的报告\n\n请确认手机号是否正确，或联系客服')
      }
    } else {
      alert(response.message || '验证失败')
    }
  } catch (error) {
    console.error('Verify failed:', error)
    alert('验证失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.verify-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.verify-container {
  width: 100%;
  max-width: 500px;
}

.verify-card {
  background: white;
  border-radius: 1.5rem;
  padding: 3rem;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}

.verify-header {
  text-align: center;
  margin-bottom: 2rem;
  position: relative;
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
  padding: 0.5rem;
}

.verify-header h1 {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.verify-header p {
  color: var(--text-secondary);
}

.verify-form {
  margin-bottom: 2rem;
}

.verify-tips {
  background: #eff6ff;
  padding: 1.5rem;
  border-radius: 0.75rem;
  border-left: 4px solid #3b82f6;
}

.verify-tips p {
  font-weight: 500;
  color: #1e40af;
  margin-bottom: 0.5rem;
}

.verify-tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.verify-tips li {
  color: #3b82f6;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  padding-left: 1.5rem;
  position: relative;
}

.verify-tips li::before {
  content: '•';
  position: absolute;
  left: 0.5rem;
}

@media (max-width: 480px) {
  .verify-card {
    padding: 2rem 1.5rem;
  }
}
</style>

