<template>
  <div class="chat-page">
    <!-- 顶部导航 -->
    <header class="chat-header">
      <div class="logo">💙 乳腺健康AI顾问</div>
      <div class="progress-bar" v-if="currentQuestionIndex > 0">
        <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        <span class="progress-text">{{ currentQuestionIndex }}/{{ totalQuestions }}</span>
      </div>
    </header>

    <!-- 对话区域 -->
    <div class="chat-container" ref="chatContainer">
      <div class="chat-card">
      <div class="messages">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="welcome-icon">
            <div class="icon-circle">
              <svg width="120" height="120" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="55" fill="#667eea" opacity="0.1"/>
                <circle cx="60" cy="60" r="45" fill="#764ba2" opacity="0.15"/>
                <text x="60" y="75" text-anchor="middle" font-size="50">💙</text>
              </svg>
            </div>
          </div>
          <h1 class="welcome-title">您好，我是小智 👋</h1>
          <p class="welcome-subtitle">您的专属乳腺健康AI顾问</p>
          
          <div class="welcome-description">
            <div class="desc-item">
              <span class="desc-icon">✨</span>
              <span>智能问诊，10-15个简单问题</span>
            </div>
            <div class="desc-item">
              <span class="desc-icon">📋</span>
              <span>生成专业健康报告</span>
            </div>
            <div class="desc-item">
              <span class="desc-icon">🔒</span>
              <span>隐私保护，信息安全</span>
            </div>
          </div>

          <div class="welcome-tips">
            <p class="tips-title">💡 温馨提示：</p>
            <ul class="tips-list">
              <li>整个过程大约需要 <strong>5-10分钟</strong></li>
              <li>请准备好您的<strong>体检报告</strong>（如有）</li>
              <li>如实回答问题，以获得准确的健康建议</li>
            </ul>
          </div>

          <button class="start-btn" @click="startChat">
            <span class="btn-icon">🚀</span>
            开始健康咨询
          </button>
          
          <p class="welcome-privacy">
            <span class="privacy-icon">🔐</span>
            我们严格遵守隐私保护政策，您的健康信息绝对安全
          </p>
        </div>

        <!-- 对话消息 -->
        <div 
          v-for="(message, index) in messages" 
          :key="index" 
          :class="['message', message.role]"
        >
          <div class="message-avatar">
            {{ message.role === 'assistant' ? '🤖' : '👤' }}
          </div>
          <div class="message-content">
            <div class="message-text" v-html="message.content"></div>
          </div>
        </div>

        <!-- 加载动画 -->
        <div v-if="isLoading" class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <!-- 生成报告中 -->
        <div v-if="isGeneratingReport" class="generating-report">
          <div class="spinner"></div>
          <p>正在为您生成专业健康报告...</p>
          <p class="sub-text">这可能需要几秒钟，请稍候 ☕</p>
        </div>
      </div>

      <!-- 底部输入区域 -->
      <div v-if="chatStarted && !isGeneratingReport" class="input-area">
      <!-- 快速选择（如果有选项） -->
      <div v-if="currentOptions && currentOptions.length > 0" class="quick-options">
        <div class="quick-options-label">💡 快速选择（点击填充）：</div>
        <div class="quick-options-buttons">
          <button
            v-for="option in currentOptions"
            :key="option.value"
            :class="['quick-option-btn', { selected: isQuickSelected(option.value) }]"
            @click="fillQuickOption(option)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-box">
        <input
          ref="mainInput"
          v-model="currentInput"
          type="text"
          :placeholder="currentPlaceholder"
          @keyup.enter="submitCurrentInput"
          class="main-input"
        />
        <button 
          @click="submitCurrentInput" 
          :disabled="!canSubmit"
          class="send-btn"
        >
          {{ currentInputType === 'multiple' && selectedOptions.length > 0 
            ? `确认选择 (${selectedOptions.length})` 
            : '发送' }}
        </button>
      </div>
      </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'ChatPage',
  setup() {
    const router = useRouter()
    const chatContainer = ref(null)
    const messages = ref([])
    const isLoading = ref(false)
    const isGeneratingReport = ref(false)
    const sessionId = ref(null)
    
    // 输入相关
    const textInput = ref('')
    const numberInput = ref(null)
    const selectedOptions = ref([])
    const currentInput = ref('')
    const mainInput = ref(null)
    const chatStarted = ref(false)
    
    // 问题流程控制
    const currentQuestionIndex = ref(0)
    const collectedData = ref({})
    
    // 问题配置（基于知识库字段）
    const questions = ref([
      // Q1: 年龄
      {
        id: 'age',
        question: '首先，让我了解一下您的基本情况。<br><strong>请问您今年多大年龄？</strong>',
        inputType: 'number',
        placeholder: '请输入您的年龄',
        field: 'age',
        required: true
      },
      
      // Q2: BI-RADS分级
      {
        id: 'birads',
        question: '您最近做过乳腺检查吗？<br><strong>检查报告中的BI-RADS分级是多少？</strong>',
        inputType: 'single',
        options: [
          { value: '0', label: '0级 - 需要补充检查' },
          { value: '1', label: '1级 - 完全正常' },
          { value: '2', label: '2级 - 明确良性' },
          { value: '3', label: '3级 - 可能良性' },
          { value: '4a', label: '4A级 - 低度可疑' },
          { value: '4b', label: '4B级 - 中度可疑' },
          { value: '4c', label: '4C级 - 高度可疑' },
          { value: '5', label: '5级 - 高度怀疑恶性' },
          { value: 'unknown', label: '❓ 没做过检查/不清楚' }
        ],
        field: 'birads_level',
        required: true
      },
      
      // Q3: 结节大小（条件：BI-RADS >= 2）
      {
        id: 'nodule_size',
        question: '<strong>检查报告中有提到结节大小吗？大约是多大？</strong>',
        inputType: 'single',
        options: [
          { value: '<=5mm', label: '🔹 微小结节（≤5mm）' },
          { value: '5-10mm', label: '🔹 小结节（5-10mm）' },
          { value: '10-20mm', label: '🔹 中等结节（10-20mm）' },
          { value: '>20mm', label: '🔹 较大结节（>20mm）' },
          { value: 'unknown', label: '❓ 不清楚/未提及' }
        ],
        field: 'nodule_size',
        condition: (data) => data.birads_level && data.birads_level !== 'unknown' && data.birads_level !== '0'
      },
      
      // Q4: 症状筛查
      {
        id: 'symptoms',
        question: '<strong>您目前有以下哪些症状？</strong><br><span style="color: #999; font-size: 14px;">（可多选）</span>',
        inputType: 'multiple',
        options: [
          { value: '疼痛', label: '☑️ 疼痛/胀痛' },
          { value: '乳头溢液', label: '☑️ 乳头溢液' },
          { value: '皮肤变化', label: '☑️ 皮肤变化（凹陷、橘皮样）' },
          { value: '触摸到肿块', label: '☑️ 触摸到肿块' },
          { value: '腋窝淋巴结肿大', label: '☑️ 腋窝淋巴结肿大' },
          { value: '无症状', label: '☑️ 无症状' }
        ],
        field: 'symptoms',
        required: true
      },
      
      // Q4.1: 疼痛详情（条件：选择了"疼痛"）
      {
        id: 'pain_type',
        question: '<strong>您的疼痛是什么样的？</strong>',
        inputType: 'single',
        options: [
          { value: '周期性疼痛', label: '🔹 周期性疼痛（月经前加重）' },
          { value: '持续性钝痛', label: '🔹 持续性钝痛' },
          { value: '刺痛', label: '🔹 刺痛' },
          { value: '触痛明显', label: '🔹 触痛明显' }
        ],
        field: 'pain_type',
        condition: (data) => data.symptoms && data.symptoms.includes('疼痛')
      },
      
      // Q5: 家族史
      {
        id: 'family_history',
        question: '<strong>您的直系亲属中，有人患过乳腺癌或卵巢癌吗？</strong>',
        inputType: 'single',
        options: [
          { value: '无', label: '🔹 无家族史' },
          { value: '一级亲属', label: '🔹 有（一级亲属：母亲/姐妹）' },
          { value: '二级亲属', label: '🔹 有（二级亲属：姨妈/姑姑/外婆）' },
          { value: '三级以上亲属', label: '🔹 有（三级以上亲属）' }
        ],
        field: 'family_history',
        required: true
      },
      
      // Q6: 月经状态
      {
        id: 'rhythm_type',
        question: '<strong>您目前的月经情况是？</strong>',
        inputType: 'single',
        options: [
          { value: '规律月经', label: '🔹 规律月经（周期正常）' },
          { value: '月经不规律', label: '🔹 月经不规律' },
          { value: '围绝经期', label: '🔹 围绝经期（月经逐渐减少）' },
          { value: '已绝经', label: '🔹 已绝经（>1年无月经）' },
          { value: '人工绝经', label: '🔹 人工绝经（手术/化疗）' }
        ],
        field: 'rhythm_type',
        required: true
      },
      
      // Q6.1: 周期阶段（条件：规律月经）
      {
        id: 'cycle_phase',
        question: '<strong>您目前处于月经周期的哪个阶段？</strong>',
        inputType: 'single',
        options: [
          { value: '月经期', label: '🔹 月经期（1-5天）' },
          { value: '卵泡期', label: '🔹 卵泡期（6-13天）' },
          { value: '排卵期', label: '🔹 排卵期（14天前后）' },
          { value: '黄体期', label: '🔹 黄体期（15-28天）' },
          { value: '不清楚', label: '❓ 不清楚' }
        ],
        field: 'cycle_phase',
        condition: (data) => data.rhythm_type === '规律月经'
      },
      
      // Q7: 检查历史
      {
        id: 'exam_history',
        question: '<strong>您之前做过哪些乳腺检查？</strong><br><span style="color: #999; font-size: 14px;">（可多选）</span>',
        inputType: 'multiple',
        options: [
          { value: '超声检查', label: '☑️ 超声检查' },
          { value: '钼靶检查', label: '☑️ 钼靶检查' },
          { value: 'MRI', label: '☑️ MRI（核磁共振）' },
          { value: '穿刺活检', label: '☑️ 穿刺活检' },
          { value: '基因检测', label: '☑️ 基因检测' },
          { value: '从未检查过', label: '☑️ 从未检查过' }
        ],
        field: 'exam_history_type',
        required: true
      },
      
      // Q8: 睡眠质量
      {
        id: 'sleep_quality',
        question: '<strong>您最近的睡眠质量如何？</strong>',
        inputType: 'single',
        options: [
          { value: '很好', label: '🔹 很好（7-8小时，深度睡眠）' },
          { value: '一般', label: '🔹 一般（6-7小时，偶尔失眠）' },
          { value: '较差', label: '🔹 较差（<6小时，经常失眠）' },
          { value: '很差', label: '🔹 很差（严重失眠）' }
        ],
        field: 'sleep_quality',
        required: true
      },
      
      // Q9: 主要顾虑
      {
        id: 'main_concern',
        question: '最后，<strong>请告诉我您最担心或最关心的问题是什么？</strong><br><span style="color: #999; font-size: 14px;">（例如：害怕是恶性的、不知道是否需要手术等）</span>',
        inputType: 'text',
        placeholder: '请输入您的顾虑或关心的问题...',
        field: 'main_concern',
        required: false
      }
    ])
    
    // 计算总问题数（动态，基于条件）
    const totalQuestions = computed(() => {
      return questions.value.filter(q => !q.condition || q.condition(collectedData.value)).length
    })
    
    // 进度百分比
    const progressPercentage = computed(() => {
      if (totalQuestions.value === 0) return 0
      return Math.round((currentQuestionIndex.value / totalQuestions.value) * 100)
    })
    
    // 当前问题的选项
    const currentOptions = computed(() => {
      const latestMessage = messages.value.find(msg => msg.isLatest)
      return latestMessage?.options || []
    })
    
    // 当前输入类型
    const currentInputType = computed(() => {
      const latestMessage = messages.value.find(msg => msg.isLatest)
      return latestMessage?.inputType || 'text'
    })
    
    // 当前占位符
    const currentPlaceholder = computed(() => {
      const latestMessage = messages.value.find(msg => msg.isLatest)
      if (currentInputType.value === 'multiple') {
        return '可多选，点击上方选项后按发送'
      }
      return latestMessage?.placeholder || '您也可以直接输入自己的答案...'
    })
    
    // 是否可以提交
    const canSubmit = computed(() => {
      if (currentInputType.value === 'multiple') {
        return selectedOptions.value.length > 0
      }
      return currentInput.value.trim().length > 0
    })
    
    // 开始对话
    const startChat = async () => {
      try {
        isLoading.value = true
        const response = await api.post('/c/chat/start', {})
        if (response.code === 0) {  // 修正：code: 0 表示成功
          sessionId.value = response.data.session_id
          chatStarted.value = true
          askNextQuestion()
        } else {
          alert('启动对话失败，请重试')
        }
      } catch (error) {
        console.error('启动对话失败:', error)
        alert('启动对话失败，请重试')
      } finally {
        isLoading.value = false
      }
    }
    
    // 询问下一个问题
    const askNextQuestion = () => {
      const availableQuestions = questions.value.filter(q => 
        !q.condition || q.condition(collectedData.value)
      )
      
      if (currentQuestionIndex.value >= availableQuestions.length) {
        // 所有问题完成，生成报告
        generateReport()
        return
      }
      
      const question = availableQuestions[currentQuestionIndex.value]
      
      // 标记之前的消息不再是最新的
      messages.value.forEach(msg => msg.isLatest = false)
      
      // 添加AI问题消息
      messages.value.push({
        role: 'assistant',
        content: question.question,
        options: question.options || null,
        inputType: question.inputType,
        placeholder: question.placeholder,
        questionId: question.id,
        field: question.field,
        isLatest: true
      })
      
      currentQuestionIndex.value++
      scrollToBottom()
    }
    
    // 选择选项
    const selectOption = async (option) => {
      const latestMessage = messages.value[messages.value.length - 1]
      
      if (latestMessage.inputType === 'single') {
        // 单选：直接提交
        selectedOptions.value = [option.value]
        await submitAnswer(option.value, option.label)
      } else if (latestMessage.inputType === 'multiple') {
        // 多选：切换选中状态
        const index = selectedOptions.value.indexOf(option.value)
        if (index > -1) {
          selectedOptions.value.splice(index, 1)
        } else {
          // 如果选择"无症状"，清除其他选项
          if (option.value === '无症状') {
            selectedOptions.value = ['无症状']
          } else {
            // 如果选择其他选项，移除"无症状"
            const noneIndex = selectedOptions.value.indexOf('无症状')
            if (noneIndex > -1) {
              selectedOptions.value.splice(noneIndex, 1)
            }
            selectedOptions.value.push(option.value)
          }
        }
      }
    }
    
    // 提交文本输入
    const submitTextInput = async () => {
      if (!textInput.value.trim()) return
      const value = textInput.value.trim()
      await submitAnswer(value, value)
      textInput.value = ''
    }
    
    // 提交数字输入
    const submitNumberInput = async () => {
      if (!numberInput.value) return
      const value = numberInput.value
      await submitAnswer(value, value.toString())
      numberInput.value = null
    }
    
    // 判断是否选中
    const isSelected = (value) => {
      return selectedOptions.value.includes(value)
    }
    
    // 提交多选答案
    const submitMultipleChoice = async () => {
      if (selectedOptions.value.length === 0) return
      
      const latestMessage = messages.value[messages.value.length - 1]
      const selectedLabels = latestMessage.options
        .filter(opt => selectedOptions.value.includes(opt.value))
        .map(opt => opt.label.replace('☑️ ', ''))
      
      await submitAnswer(selectedOptions.value, selectedLabels.join('、'))
    }
    
    // 新增：快速选项填充
    const fillQuickOption = (option) => {
      const latestMessage = messages.value[messages.value.length - 1]
      
      if (latestMessage.inputType === 'single') {
        // 单选：直接使用option.value（不包含emoji），避免Unicode编码问题
        const cleanValue = option.value
        const cleanLabel = option.label.replace(/^[🔹☑️❓]\s*/, '')
        submitAnswerDirect(cleanValue, cleanLabel)
        return
      } else if (latestMessage.inputType === 'multiple') {
        // 多选：切换选中状态
        const index = selectedOptions.value.indexOf(option.value)
        if (index > -1) {
          selectedOptions.value.splice(index, 1)
        } else {
          if (option.value === '无症状') {
            selectedOptions.value = ['无症状']
          } else {
            const noneIndex = selectedOptions.value.indexOf('无症状')
            if (noneIndex > -1) {
              selectedOptions.value.splice(noneIndex, 1)
            }
            selectedOptions.value.push(option.value)
          }
        }
      }
    }
    
    // 新增：判断快速选项是否选中
    const isQuickSelected = (value) => {
      return selectedOptions.value.includes(value)
    }
    
    // 新增：提交当前输入
    const submitCurrentInput = async () => {
      const latestMessage = messages.value[messages.value.length - 1]
      
      if (latestMessage.inputType === 'multiple') {
        // 多选：提交已选项
        if (selectedOptions.value.length === 0) return
        
        const selectedLabels = latestMessage.options
          .filter(opt => selectedOptions.value.includes(opt.value))
          .map(opt => opt.label.replace(/^[🔹☑️❓]\s*/, ''))
        
        await submitAnswer(selectedOptions.value, selectedLabels.join('、'))
      } else {
        // 单选/文本/数字：提交输入框内容
        if (!currentInput.value.trim()) return
        
        const value = currentInput.value.trim()
        await submitAnswer(value, value)
      }
      
      // 清空输入
      currentInput.value = ''
      selectedOptions.value = []
    }
    
    // 提交答案
    const submitAnswer = async (value, displayLabel) => {
      const latestMessage = messages.value[messages.value.length - 1]
      
      // 保存到collected_data
      collectedData.value[latestMessage.field] = value
      
      // 添加用户回复消息
      messages.value.push({
        role: 'user',
        content: displayLabel,
        isLatest: false
      })
      
      // 清空多选状态
      selectedOptions.value = []
      
      // 发送消息到后端
      try {
        await api.post('/c/chat/message', {
          session_id: sessionId.value,
          message: displayLabel,
          intent: latestMessage.questionId
        })
      } catch (error) {
        console.error('发送消息失败:', error)
      }
      
      // 显示加载动画
      isLoading.value = true
      await new Promise(resolve => setTimeout(resolve, 800)) // 模拟思考
      isLoading.value = false
      
      // 添加鼓励提示
      if (currentQuestionIndex.value === 3) {
        messages.value.push({
          role: 'assistant',
          content: '很好！我已经了解了您的基本情况 👍',
          isLatest: false
        })
        await new Promise(resolve => setTimeout(resolve, 1000))
      } else if (currentQuestionIndex.value === 6) {
        messages.value.push({
          role: 'assistant',
          content: '您做得很棒！还有最后几个问题 💪',
          isLatest: false
        })
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
      
      // 询问下一个问题
      askNextQuestion()
    }
    
    // 新增：直接提交答案（用于快速选择）
    const submitAnswerDirect = async (value, displayLabel) => {
      await submitAnswer(value, displayLabel)
    }
    
    // 生成报告
    const generateReport = async () => {
      messages.value.push({
        role: 'assistant',
        content: '感谢您的配合！正在为您生成专业报告... ✨',
        isLatest: false
      })
      
      isGeneratingReport.value = true
      scrollToBottom()
      
      try {
        const response = await api.post('/c/chat/complete', {
          session_id: sessionId.value,
          collected_data: collectedData.value
        })
        
        if (response.code === 0) {  // 修正：code: 0 表示成功
          const { report_code, download_token, risk_level } = response.data
          
          // 保存到localStorage
          localStorage.setItem('latest_report', JSON.stringify({
            report_code,
            download_token,
            risk_level,
            session_id: sessionId.value
          }))
          
          // 跳转到保存报告页面
          router.push('/save-report')
        } else {
          alert('生成报告失败：' + response.message)
          isGeneratingReport.value = false
        }
      } catch (error) {
        console.error('生成报告失败:', error)
        alert('生成报告失败，请重试')
        isGeneratingReport.value = false
      }
    }
    
    // 滚动到底部
    const scrollToBottom = async () => {
      await nextTick()
      // 滚动messages区域而不是chatContainer
      const messagesEl = document.querySelector('.messages')
      if (messagesEl) {
        messagesEl.scrollTop = messagesEl.scrollHeight
      }
    }
    
    onMounted(() => {
      // 如果有未完成的会话，可以在这里恢复
    })
    
    return {
      chatContainer,
      messages,
      isLoading,
      isGeneratingReport,
      currentQuestionIndex,
      totalQuestions,
      progressPercentage,
      textInput,
      numberInput,
      selectedOptions,
      currentInput,
      mainInput,
      chatStarted,
      currentOptions,
      currentInputType,
      currentPlaceholder,
      canSubmit,
      startChat,
      selectOption,
      submitTextInput,
      submitNumberInput,
      submitMultipleChoice,
      isSelected,
      fillQuickOption,
      isQuickSelected,
      submitCurrentInput,
      submitAnswerDirect
    }
  }
}
</script>

<style scoped>
.chat-page {
  min-height: 100vh;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 头部 */
.chat-header {
  background: white;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 10;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 12px;
  text-align: center;
}

.progress-bar {
  position: relative;
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.5s ease;
  border-radius: 3px;
}

.progress-text {
  position: absolute;
  right: 8px;
  top: -24px;
  font-size: 12px;
  color: #666;
  font-weight: 600;
}

/* 对话容器 */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 对话卡片 */
.chat-card {
  max-width: 900px;
  width: 100%;
  height: 75vh; /* 固定高度 */
  background: white;
  border-radius: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px;
  scroll-behavior: smooth;
}

/* 自定义滚动条 */
.messages::-webkit-scrollbar {
  width: 8px;
}

.messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 欢迎消息 */
.welcome-message {
  padding: 40px 32px;
  text-align: center;
  animation: fadeIn 0.5s;
}

.welcome-icon {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.icon-circle {
  animation: float 3s ease-in-out infinite;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #1a202c;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 18px;
  color: #718096;
  margin-bottom: 32px;
  font-weight: 500;
}

.welcome-description {
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 28px;
}

.desc-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 10px;
  font-size: 16px;
  color: #2d3748;
}

.desc-icon {
  font-size: 24px;
}

.welcome-tips {
  background: #fff5e6;
  border-left: 4px solid #fbbf24;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 32px;
  text-align: left;
}

.tips-title {
  font-size: 16px;
  font-weight: 600;
  color: #92400e;
  margin-bottom: 12px;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  padding: 8px 0;
  color: #78350f;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  padding-left: 24px;
}

.tips-list li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #fbbf24;
  font-weight: bold;
}

.tips-list li strong {
  color: #92400e;
  font-weight: 600;
}

.welcome-privacy {
  margin-top: 24px;
  font-size: 13px;
  color: #a0aec0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.privacy-icon {
  font-size: 16px;
}

.start-btn {
  margin-top: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 18px 60px;
  border-radius: 30px;
  font-size: 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.start-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(102,126,234,0.4);
}

/* 消息样式 */
.message {
  display: flex;
  margin-bottom: 24px;
  animation: slideIn 0.4s ease-out;
}

.message.assistant {
  justify-content: flex-start;
}

.message.user {
  justify-content: flex-end;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.message.assistant .message-avatar {
  background: white;
  margin-right: 12px;
}

.message.user .message-avatar {
  background: rgba(255,255,255,0.3);
  margin-left: 12px;
  order: 2;
}

.message-content {
  max-width: 70%;
  min-width: 200px;
}

.message-text {
  background: white;
  padding: 16px 20px;
  border-radius: 16px;
  line-height: 1.6;
  color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.message.user .message-text {
  background: rgba(255,255,255,0.95);
  color: #667eea;
  font-weight: 600;
}

/* 选项按钮 */
.message-options {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.option-btn {
  background: white;
  border: 2px solid #e0e0e0;
  padding: 14px 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
  font-size: 15px;
  color: #333;
}

.option-btn:hover {
  border-color: #667eea;
  background: #f8f9ff;
  transform: translateX(4px);
}

.option-btn.selected {
  border-color: #667eea;
  background: #667eea;
  color: white;
  font-weight: 600;
}

/* 多选提交按钮 */
.submit-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 16px 20px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  margin-top: 12px;
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102,126,234,0.4);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 输入框 */
.message-input {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

.message-input input {
  flex: 1;
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.3s;
}

.message-input input:focus {
  border-color: #667eea;
}

.message-input button {
  background: #667eea;
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.message-input button:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
}

.message-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 16px 20px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

/* 生成报告中 */
.generating-report {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  animation: fadeIn 0.5s;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(102,126,234,0.2);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 24px;
}

.generating-report p {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
  font-weight: 600;
}

.generating-report .sub-text {
  font-size: 14px;
  color: #999;
  font-weight: normal;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 底部输入区域 */
.input-area {
  background: white;
  border-top: 2px solid #f0f0f0;
  flex-shrink: 0;
}

/* 快速选择区域 */
.quick-options {
  padding: 12px 20px 8px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
  max-height: 180px;
  overflow-y: auto;
}

.quick-options-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 10px;
  font-weight: 500;
}

.quick-options-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-option-btn {
  padding: 8px 16px;
  background: white;
  border: 1.5px solid #ddd;
  border-radius: 20px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.quick-option-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f0f4ff;
}

.quick-option-btn.selected {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
}

/* 输入框区域 */
.input-box {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  gap: 12px;
}

.main-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 24px;
  font-size: 15px;
  outline: none;
  transition: all 0.2s;
}

.main-input:focus {
  border-color: #667eea;
  background: #f9fafe;
}

.send-btn {
  padding: 12px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .welcome-message {
    padding: 40px 24px;
  }

  .welcome-message h1 {
    font-size: 28px;
  }

  .welcome-message p {
    font-size: 16px;
  }

  .start-btn {
    padding: 16px 48px;
    font-size: 18px;
  }

  .message-content {
    max-width: 85%;
    min-width: 150px;
  }

  .chat-container {
    padding: 12px;
  }
  
  .chat-card {
    max-height: 90vh;
    border-radius: 16px;
  }
  
  .messages {
    padding: 16px;
  }

  .quick-options {
    padding: 12px 16px 8px;
  }

  .quick-option-btn {
    font-size: 13px;
    padding: 6px 12px;
  }

  .input-box {
    padding: 12px 16px;
  }

  .main-input {
    font-size: 14px;
    padding: 10px 14px;
  }

  .send-btn {
    padding: 10px 20px;
    font-size: 14px;
  }
}
</style>
