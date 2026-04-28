<template>
  <div class="save-report-page">
    <div class="save-container">
      <div class="save-card">
        <div class="card-header">
          <h1>保存您的健康报告</h1>
          <p>输入手机号或使用微信登录，随时随地查看您的报告</p>
        </div>

        <div class="login-options">
          <!-- 手机号登录 -->
          <div class="option-section">
            <h3>📱 手机号保存</h3>
            <div class="input-group">
              <input 
                v-model="phone" 
                type="tel" 
                placeholder="请输入您的手机号"
                maxlength="11"
                @keyup.enter="saveByPhone"
              />
            </div>
            <div class="input-group">
              <input 
                v-model="name" 
                type="text" 
                placeholder="请输入您的姓名"
                @keyup.enter="saveByPhone"
              />
            </div>
            <button 
              class="btn btn-primary" 
              @click="saveByPhone"
              :disabled="loading"
            >
              <span v-if="loading" class="loading"></span>
              <span v-else>保存并查看报告</span>
            </button>
          </div>

          <div class="divider">
            <span>或</span>
          </div>

          <!-- 微信登录 -->
          <div class="option-section">
            <h3>💬 微信保存</h3>
            <p class="wechat-tip">使用微信扫码或在微信中打开可直接保存</p>
            <button class="btn btn-wechat" @click="saveByWechat">
              <span>💬</span>
              微信快捷保存
            </button>
          </div>
        </div>

        <div class="privacy-notice">
          <p>🔒 您的隐私和数据安全是我们的首要关注</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { cAPI } from '../services/api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const phone = ref('')
const name = ref('')
const loading = ref(false)
const reportData = ref(null)

onMounted(() => {
  // 获取报告数据（与ChatPage保持一致）
  const tempData = localStorage.getItem('latest_report')
  if (tempData) {
    reportData.value = JSON.parse(tempData)
  } else {
    // 如果没有数据，返回首页重新开始
    alert('未找到报告数据，请重新开始咨询')
    router.push('/')
  }
})

// 手机号保存
const saveByPhone = async () => {
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
    // 1. 先登录/注册
    const loginResult = await userStore.loginByPhone(phone.value, name.value)
    
    if (!loginResult.success) {
      alert('登录失败：' + loginResult.message)
      return
    }
    
    // 2. 开始对话
    const chatResponse = await cAPI.chat.start(phone.value)
    if (!chatResponse.success) {
      alert('创建对话失败')
      return
    }
    
    const sessionId = chatResponse.data.session_id
    
    // 3. 完成对话并生成报告
    const completeResponse = await cAPI.chat.complete(sessionId, reportData.value)
    
    if (completeResponse.success) {
      // 保存手机号，用于后续查询报告列表
      localStorage.setItem('user_phone', phone.value)
      
      // 清除临时数据
      localStorage.removeItem('tempReportData')
      localStorage.removeItem('latest_report')
      
      alert('报告已保存！')
      
      // 跳转到我的报告
      router.push('/my-reports')
    } else {
      alert('保存报告失败：' + completeResponse.message)
    }
  } catch (error) {
    console.error('Save failed:', error)
    alert('保存失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 微信保存
const saveByWechat = () => {
  alert('微信登录功能开发中...\n\n请在微信中打开此页面，或使用手机号保存')
}
</script>

<style scoped>
.save-report-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
}

.save-container {
  width: 100%;
  max-width: 500px;
}

.save-card {
  background: white;
  border-radius: 1.5rem;
  padding: 3rem 2rem;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h1 {
  font-size: 1.75rem;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.card-header p {
  color: #6b7280;
  font-size: 0.95rem;
}

.option-section {
  margin-bottom: 2rem;
}

.option-section h3 {
  font-size: 1.1rem;
  color: #1f2937;
  margin-bottom: 1rem;
}

.input-group {
  margin-bottom: 1rem;
}

.input-group input {
  width: 100%;
  padding: 0.875rem 1.25rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.input-group input:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-wechat {
  background: #07c160;
  color: white;
}

.btn-wechat:hover {
  background: #06ad56;
  transform: translateY(-2px);
}

.btn-wechat span:first-child {
  font-size: 1.25rem;
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
  width: 42%;
  height: 1px;
  background: #e5e7eb;
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
  color: #9ca3af;
  position: relative;
  z-index: 1;
  font-size: 0.875rem;
}

.wechat-tip {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  text-align: center;
}

.privacy-notice {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
  text-align: center;
}

.privacy-notice p {
  color: #6b7280;
  font-size: 0.875rem;
}

@media (max-width: 480px) {
  .save-card {
    padding: 2rem 1.5rem;
  }
}
</style>

