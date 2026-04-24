import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 180000,  // 增加到180秒（3分钟），LLM生成报告可能需要较长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加token
    const sessionToken = localStorage.getItem('sessionToken')
    if (sessionToken) {
      config.headers['Authorization'] = `Bearer ${sessionToken}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// C端API
export const cAPI = {
  // 认证相关
  auth: {
    // 手机号登录
    loginByPhone(phone, name, sourceChannel = 'web') {
      return api.post('/c/auth/phone', {
        phone,
        name,
        source_channel: sourceChannel,
        entry_url: window.location.href
      })
    },
    
    // 微信登录
    loginByWechat(code, nickname) {
      return api.post('/c/auth/wechat', {
        code,
        nickname,
        source_channel: 'wechat'
      })
    },
    
    // 绑定手机号
    bindPhone(patientCode, phone) {
      return api.post('/c/auth/bind-phone', {
        patient_code: patientCode,
        phone
      })
    },
    
    // 获取用户信息
    getProfile(patientCode) {
      return api.get(`/c/auth/profile/${patientCode}`)
    }
  },
  
  // 对话相关
  chat: {
    // 开始对话
    start(phone, channel = 'web') {
      return api.post('/c/chat/start', {
        phone,
        channel
      })
    },
    
    // 发送消息
    sendMessage(sessionId, message, channel = 'web') {
      return api.post('/c/chat/message', {
        session_id: sessionId,
        message,
        channel
      })
    },
    
    // 获取对话历史
    getHistory(sessionId) {
      return api.get(`/c/chat/history/${sessionId}`)
    },
    
    // 完成对话
    complete(sessionId, collectedData) {
      return api.post('/c/chat/complete', {
        session_id: sessionId,
        collected_data: collectedData
      })
    }
  },
  
  // 报告相关
  reports: {
    // 验证手机号查看报告
    verifyPhone(phone) {
      return api.post('/c/reports/verify', {
        phone
      })
    },
    
    // 获取报告详情
    getReport(reportId, token) {
      return api.get(`/c/reports/${reportId}`, {
        params: { token }
      })
    },
    
    // 下载PDF
    downloadPDF(reportId, token) {
      return api.get(`/c/reports/${reportId}/pdf`, {
        params: { token },
        responseType: 'blob'
      })
    }
  }
}

export default api

