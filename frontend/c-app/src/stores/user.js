import { defineStore } from 'pinia'
import { cAPI } from '../services/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    patientCode: localStorage.getItem('patientCode') || null,
    sessionToken: localStorage.getItem('sessionToken') || null,
    userInfo: null,
    isLoggedIn: false
  }),
  
  actions: {
    // 手机号登录
    async loginByPhone(phone, name) {
      try {
        const response = await cAPI.auth.loginByPhone(phone, name)
        
        if (response.success) {
          const { patient, session_token } = response.data
          
          this.patientCode = patient.patient_code
          this.sessionToken = session_token
          this.userInfo = patient
          this.isLoggedIn = true
          
          localStorage.setItem('patientCode', patient.patient_code)
          localStorage.setItem('sessionToken', session_token)
          localStorage.setItem('userInfo', JSON.stringify(patient))
          
          return { success: true, data: patient }
        }
        
        return { success: false, message: response.message }
      } catch (error) {
        console.error('Login failed:', error)
        return { success: false, message: '登录失败，请稍后重试' }
      }
    },
    
    // 微信登录
    async loginByWechat(code, nickname) {
      try {
        const response = await cAPI.auth.loginByWechat(code, nickname)
        
        if (response.success) {
          const { patient, session_token } = response.data
          
          this.patientCode = patient.patient_code
          this.sessionToken = session_token
          this.userInfo = patient
          this.isLoggedIn = true
          
          localStorage.setItem('patientCode', patient.patient_code)
          localStorage.setItem('sessionToken', session_token)
          localStorage.setItem('userInfo', JSON.stringify(patient))
          
          return { success: true, data: patient }
        }
        
        return { success: false, message: response.message }
      } catch (error) {
        console.error('WeChat login failed:', error)
        return { success: false, message: '微信登录失败，请稍后重试' }
      }
    },
    
    // 加载用户信息
    async loadUserInfo() {
      if (!this.patientCode) return
      
      try {
        const response = await cAPI.auth.getProfile(this.patientCode)
        
        if (response.success) {
          this.userInfo = response.data.patient
          this.isLoggedIn = true
          localStorage.setItem('userInfo', JSON.stringify(response.data.patient))
        }
      } catch (error) {
        console.error('Load user info failed:', error)
      }
    },
    
    // 登出
    logout() {
      this.patientCode = null
      this.sessionToken = null
      this.userInfo = null
      this.isLoggedIn = false
      
      localStorage.removeItem('patientCode')
      localStorage.removeItem('sessionToken')
      localStorage.removeItem('userInfo')
    },
    
    // 初始化（从localStorage恢复状态）
    init() {
      const patientCode = localStorage.getItem('patientCode')
      const sessionToken = localStorage.getItem('sessionToken')
      const userInfoStr = localStorage.getItem('userInfo')
      
      if (patientCode && sessionToken) {
        this.patientCode = patientCode
        this.sessionToken = sessionToken
        this.isLoggedIn = true
        
        if (userInfoStr) {
          try {
            this.userInfo = JSON.parse(userInfoStr)
          } catch (e) {
            console.error('Parse user info failed:', e)
          }
        }
      }
    }
  }
})

