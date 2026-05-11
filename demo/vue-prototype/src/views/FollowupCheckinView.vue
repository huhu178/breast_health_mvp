<template>
  <main class="checkin-page">
    <section class="checkin-shell">
      <div class="brand-row">
        <div>
          <p class="eyebrow">健康管理任务</p>
          <h1>{{ pageTitle }}</h1>
        </div>
        <span class="status-chip" :class="statusClass">{{ statusText }}</span>
      </div>

      <div v-if="loading" class="state-box">正在加载任务...</div>
      <div v-else-if="error" class="state-box error-box">{{ error }}</div>

      <template v-else>
        <section class="task-panel">
          <div class="patient-line">
            <strong>{{ task.patient?.name || '患者' }}</strong>
            <span>{{ task.patient?.phone || '未登记手机号' }}</span>
          </div>
          <h2>{{ node.name || task.title || '健康打卡' }}</h2>
          <p>{{ node.message_template || task.content || '请按要求完成本次健康管理任务。' }}</p>
        </section>

        <form class="checkin-form" @submit.prevent="submitCheckin">
          <label>
            <span>{{ contentLabel }}</span>
            <textarea
              v-model.trim="form.content_text"
              rows="6"
              :placeholder="contentPlaceholder"
              :disabled="submitting || submitted"
            />
          </label>

          <label v-if="isDietTask">
            <span>图片链接</span>
            <textarea
              v-model.trim="imageUrlText"
              rows="3"
              placeholder="每行一张图片链接，可先填写企业微信或对象存储返回的图片地址"
              :disabled="submitting || submitted"
            />
          </label>

          <button type="submit" :disabled="submitting || submitted || !canSubmit">
            {{ submitButtonText }}
          </button>
        </form>

        <section v-if="result" class="result-panel" :class="{ abnormal: result.abnormal }">
          <p class="result-title">{{ result.abnormal ? '已提醒健康管理师关注' : '已完成本次打卡' }}</p>
          <p>{{ result.patient_reply || result.summary || '本次记录已提交。' }}</p>
          <ul v-if="result.flags.length">
            <li v-for="flag in result.flags" :key="flag">{{ flag }}</li>
          </ul>
        </section>
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const taskCode = computed(() => String(route.params.taskCode || ''))

const loading = ref(true)
const submitting = ref(false)
const submitted = ref(false)
const error = ref('')
const task = ref({})
const imageUrlText = ref('')
const result = ref(null)
const form = reactive({
  content_text: ''
})

const node = computed(() => task.value.node || task.value.task_payload?.node || {})
const taskType = computed(() => node.value.task_type || task.value.task_type || 'daily_checkin')
const isDietTask = computed(() => taskType.value === 'diet_checkin')
const pageTitle = computed(() => {
  if (isDietTask.value) return '餐饮图片打卡'
  if (taskType.value === 'exercise_reminder') return '运动打卡'
  if (taskType.value === 'psych_reminder') return '心理睡眠打卡'
  return '每日健康打卡'
})
const canSubmit = computed(() => Boolean(form.content_text || imageUrlText.value))
const statusText = computed(() => {
  if (submitted.value) return '已提交'
  if (task.value.status === 'manual_processing') return '待处理'
  if (task.value.status === 'completed') return '已完成'
  return '待打卡'
})
const statusClass = computed(() => ({
  done: submitted.value || task.value.status === 'completed',
  alert: task.value.status === 'manual_processing'
}))
const contentLabel = computed(() => isDietTask.value ? '本餐记录' : '今日情况')
const contentPlaceholder = computed(() => (
  isDietTask.value
    ? '例如：午餐吃了半碗米饭、清蒸鱼、青菜，饭后步行20分钟。'
    : '例如：睡眠7小时，晚饭清淡，步行20分钟，情绪平稳。'
))
const submitButtonText = computed(() => {
  if (submitted.value) return '已提交'
  if (submitting.value) return '提交中...'
  return '提交打卡'
})

async function publicApi(url, options = {}) {
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok || data.success === false) {
    throw new Error(data.message || `请求失败：${res.status}`)
  }
  return data.data ?? data
}

function parseImageUrls(text) {
  return String(text || '')
    .split(/[\n,，]/)
    .map(item => item.trim())
    .filter(Boolean)
}

function normalizeSubmitResult(data) {
  const aiResult = data?.ai_result || data?.analysis || {}
  const signals = Array.isArray(aiResult.signals) ? aiResult.signals : []
  return {
    abnormal: Boolean(aiResult.abnormal || aiResult.is_abnormal || data?.checkin?.abnormal_flag),
    patient_reply: aiResult.patient_reply || aiResult.reply || '',
    summary: aiResult.summary || data?.checkin?.abnormal_reason || '',
    flags: signals.map(signal => signal.label || signal.type).filter(Boolean)
  }
}

async function loadTask() {
  loading.value = true
  error.value = ''
  try {
    task.value = await publicApi(`/api/followup/checkin/${taskCode.value}`)
  } catch (e) {
    error.value = e?.message || '任务加载失败'
  } finally {
    loading.value = false
  }
}

async function submitCheckin() {
  if (!canSubmit.value || submitting.value) return
  submitting.value = true
  error.value = ''
  try {
    const data = await publicApi(`/api/followup/checkin/${taskCode.value}`, {
      method: 'POST',
      body: JSON.stringify({
        checkin_type: taskType.value,
        content_text: form.content_text,
        image_urls: parseImageUrls(imageUrlText.value),
        analyze: true
      })
    })
    result.value = normalizeSubmitResult(data)
    submitted.value = true
  } catch (e) {
    error.value = e?.message || '提交失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}

onMounted(loadTask)
</script>

<style scoped>
.checkin-page {
  min-height: 100vh;
  background: #f6f8fb;
  color: #172033;
  padding: 28px 16px;
}

.checkin-shell {
  max-width: 560px;
  margin: 0 auto;
}

.brand-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #667085;
  font-size: 13px;
}

h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
}

.status-chip {
  flex: 0 0 auto;
  border-radius: 999px;
  padding: 6px 12px;
  background: #eaf2ff;
  color: #175cd3;
  font-size: 13px;
  font-weight: 700;
}

.status-chip.done {
  background: #e8f7ef;
  color: #067647;
}

.status-chip.alert {
  background: #fff3e6;
  color: #b54708;
}

.task-panel,
.checkin-form,
.result-panel,
.state-box {
  background: #fff;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  padding: 18px;
  box-shadow: 0 12px 28px rgba(16, 24, 40, 0.06);
}

.state-box {
  color: #475467;
}

.error-box {
  border-color: #fecdca;
  color: #b42318;
}

.patient-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #667085;
  font-size: 14px;
  margin-bottom: 12px;
}

.patient-line strong {
  color: #172033;
}

h2 {
  margin: 0 0 10px;
  font-size: 20px;
  line-height: 1.3;
}

.task-panel p,
.result-panel p {
  margin: 0;
  color: #475467;
  line-height: 1.7;
}

.checkin-form {
  margin-top: 14px;
  display: grid;
  gap: 14px;
}

label {
  display: grid;
  gap: 8px;
  color: #344054;
  font-weight: 700;
  font-size: 14px;
}

textarea {
  width: 100%;
  resize: vertical;
  min-height: 120px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  padding: 12px;
  color: #172033;
  font: inherit;
  line-height: 1.6;
  box-sizing: border-box;
}

textarea:focus {
  border-color: #2e90fa;
  outline: 3px solid rgba(46, 144, 250, 0.16);
}

button {
  height: 46px;
  border: 0;
  border-radius: 8px;
  background: #155eef;
  color: #fff;
  font-weight: 800;
  cursor: pointer;
}

button:disabled {
  background: #98a2b3;
  cursor: not-allowed;
}

.result-panel {
  margin-top: 14px;
  border-color: #abefc6;
}

.result-panel.abnormal {
  border-color: #fedf89;
}

.result-title {
  color: #067647 !important;
  font-weight: 800;
  margin-bottom: 8px !important;
}

.result-panel.abnormal .result-title {
  color: #b54708 !important;
}

ul {
  margin: 10px 0 0;
  padding-left: 18px;
  color: #475467;
  line-height: 1.7;
}

@media (max-width: 520px) {
  .checkin-page {
    padding: 20px 12px;
  }

  h1 {
    font-size: 24px;
  }

  .patient-line {
    display: grid;
  }
}
</style>
