<template>
  <div class="workflow-page">
    <header class="page-head">
      <div>
        <p class="crumb">首页 / 随访知识库与模板</p>
        <h1>随访知识库与模板</h1>
      </div>
      <div class="head-actions">
        <button class="btn" type="button" @click="loadAll">刷新</button>
        <input ref="excelInputRef" type="file" accept=".xlsx,.xlsm" style="display:none" @change="handleExcelImport">
        <button class="btn" type="button" :disabled="importingExcel" @click="excelInputRef?.click()">
          {{ importingExcel ? '导入中...' : '导入Excel模板' }}
        </button>
        <button class="primary" type="button" @click="createTemplate">新建随访模板</button>
      </div>
    </header>

    <div v-if="error" class="notice error">{{ error }}</div>
    <div v-if="toast" class="notice">{{ toast }}</div>

    <section class="workflow-grid">
      <aside class="panel template-panel">
        <div class="panel-head">
          <div>
            <h2>随访任务模板</h2>
            <p>定义推送内容、打卡要求和执行周期</p>
          </div>
        </div>

        <div class="template-list">
          <article
            v-for="tpl in templates"
            :key="tpl.id"
            class="template-item"
            :class="{ active: tpl.id === selectedTemplateId }"
          >
            <button class="template-select" type="button" @click="selectTemplate(tpl.id)">
              <span class="item-title">{{ tpl.name }}</span>
              <span class="item-meta">{{ noduleText(tpl.nodule_type) }} · {{ riskText(tpl.risk_level) }} · {{ tpl.cycle_days }}天</span>
              <span class="item-foot">
                <b>{{ statusText(tpl.status) }}</b>
                <em>{{ (tpl.nodes || []).length }} 个节点</em>
              </span>
            </button>
            <details class="template-more">
              <summary>更多</summary>
              <div class="template-menu">
                <button type="button" @click="copyTemplate(tpl)">复制模板</button>
                <button type="button" @click="archiveTemplate(tpl)">{{ tpl.status === 'archived' ? '恢复模板' : '归档模板' }}</button>
                <button class="danger-text" type="button" @click="deleteTemplate(tpl)">删除模板</button>
              </div>
            </details>
          </article>
        </div>
      </aside>

      <main class="panel editor-panel">
        <div class="panel-head">
          <div>
            <h2>知识库与模板编辑</h2>
            <p>维护七大类知识库，并编排固定企业微信推送任务</p>
          </div>
          <div class="editor-actions">
            <button class="primary" type="button" :disabled="!templateForm.name || saving" @click="saveTemplate">
              {{ saving ? '保存中...' : '保存模板' }}
            </button>
          </div>
        </div>

        <div class="editor-stack">
          <section class="editor-section">
            <div class="section-head compact-head">
              <div>
                <h3>基础信息</h3>
                <p>定义模板适用结节、风险等级和启用状态</p>
              </div>
            </div>
            <div class="form-grid">
              <label class="wide">模板名称<input v-model.trim="templateForm.name" placeholder="如：乳腺结节30天随访任务"></label>
              <label>适用结节
                <select v-model="templateForm.nodule_type">
                  <option value="">通用</option>
                  <option value="breast">乳腺</option>
                  <option value="thyroid">甲状腺</option>
                  <option value="lung">肺部</option>
                  <option value="breast_lung">乳腺+肺部</option>
                  <option value="breast_thyroid">乳腺+甲状腺</option>
                  <option value="lung_thyroid">肺部+甲状腺</option>
                  <option value="triple">三合并结节</option>
                </select>
              </label>
              <label>风险等级
                <select v-model="templateForm.risk_level">
                  <option value="">全部</option>
                  <option value="high">高风险</option>
                  <option value="mid">中风险</option>
                  <option value="low">低风险</option>
                </select>
              </label>
              <label>状态
                <select v-model="templateForm.status">
                  <option value="draft">草稿</option>
                  <option value="active">启用</option>
                  <option value="paused">暂停</option>
                  <option value="archived">归档</option>
                </select>
              </label>
            </div>
          </section>

          <section class="editor-section">
            <div class="section-head compact-head">
              <div>
                <h3>任务节点</h3>
                <p>每个节点会生成对应的提醒、打卡或图片识别任务</p>
              </div>
              <button class="btn" type="button" :disabled="!selectedTemplateId" @click="addNode">添加节点</button>
            </div>

            <div class="node-list">
              <article v-for="(node, index) in sortedNodes" :key="node.id" class="node-card" :class="{ inactive: node.is_active === false }">
                <div class="node-top">
                  <div class="day-badge">第 {{ node.day_offset || 1 }} 天<br><span>{{ node.send_time || '09:00' }}</span></div>
                  <div class="node-main">
                    <strong>{{ node.name }}</strong>
                    <span>{{ taskTypeText(node.task_type) }} · {{ patientActionText(node.patient_action) }} · {{ aiActionText(node.ai_action) }}</span>
                  </div>
                  <div class="node-actions">
                    <button class="mini-btn" type="button" :disabled="index === 0" @click="moveNode(node, -1)">上移</button>
                    <button class="mini-btn" type="button" :disabled="index === sortedNodes.length - 1" @click="moveNode(node, 1)">下移</button>
                    <button class="mini-btn" type="button" @click="toggleNodeActive(node)">{{ node.is_active === false ? '启用' : '停用' }}</button>
                    <button class="mini-btn" type="button" @click="editNode(node)">编辑</button>
                    <details class="node-more" @click.stop>
                      <summary>更多</summary>
                      <div class="template-menu">
                        <button type="button" @click="copyNode(node)">复制节点</button>
                      </div>
                    </details>
                  </div>
                </div>
                <p>{{ node.message_template || '未配置推送内容' }}</p>
                <div class="node-tags">
                  <span v-for="id in node.knowledge_item_ids || []" :key="id">{{ knowledgeTitle(id) }}</span>
                  <span v-if="node.escalation_rule && Object.keys(node.escalation_rule).length">关注规则已配置</span>
                  <span>{{ node.is_active === false ? '已停用' : '启用中' }}</span>
                </div>
              </article>
              <div v-if="!sortedNodes.length" class="empty">还没有节点，先添加知识推送、每日打卡、饮食图片识别、运动提醒或心理提醒。</div>
            </div>
          </section>
        </div>
      </main>
    </section>

    <div v-if="nodeModal" class="modal-mask" @click.self="nodeModal = false">
      <section class="modal">
        <div class="modal-head">
          <h2>{{ nodeForm.id ? '编辑任务节点' : '新增任务节点' }}</h2>
          <button class="icon-close" type="button" @click="nodeModal = false">×</button>
        </div>
        <div class="form-grid">
          <label>节点名称<input v-model.trim="nodeForm.name"></label>
          <label>第几天<input v-model.number="nodeForm.day_offset" type="number" min="0"></label>
          <label>发送时间<input v-model.trim="nodeForm.send_time" placeholder="09:00"></label>
          <label>任务类型
            <select v-model="nodeForm.task_type">
              <option v-for="item in taskTypeOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
            </select>
          </label>
          <label>患者动作
            <select v-model="nodeForm.patient_action">
              <option value="none">无需动作</option>
              <option value="reply_text">回复文本</option>
              <option value="upload_image">上传图片</option>
              <option value="upload_report">上传报告</option>
              <option value="fill_form">填写表单</option>
            </select>
          </label>
          <label>AI动作
            <select v-model="nodeForm.ai_action">
              <option v-for="item in aiActionOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
            </select>
          </label>
          <label class="wide">关联知识库
            <select v-model="nodeForm.knowledge_item_ids" multiple>
              <option v-for="item in knowledgeItems" :key="item.id" :value="item.id">{{ item.title }}</option>
            </select>
          </label>
          <label class="wide">推送内容<textarea v-model.trim="nodeForm.message_template" rows="4"></textarea></label>
          <div class="wide rule-box">
            <div class="rule-box-title">提醒规则</div>
            <div class="form-grid compact">
              <label>重点关注关键词<input v-model.trim="nodeForm.doctor_keywords_text" placeholder="不适, 疼痛, 明显加重"></label>
              <label>健康管理师关注关键词<input v-model.trim="nodeForm.manual_keywords_text" placeholder="焦虑, 睡不着, 担心"></label>
              <label>连续未回复次数<input v-model.number="nodeForm.no_reply_threshold" type="number" min="0"></label>
            </div>
          </div>
          <div class="wide rule-box">
            <div class="rule-box-title">完成规则</div>
            <div class="form-grid compact">
              <label>完成条件
                <select v-model="nodeForm.completion_type">
                  <option value="message_sent">消息发送后完成</option>
                  <option value="patient_reply">用户回复后完成</option>
                  <option value="checkin_submitted">用户打卡后完成</option>
                  <option value="manual_confirm">人工确认后完成</option>
                </select>
              </label>
              <label>是否必做
                <select v-model="nodeForm.is_required">
                  <option :value="true">必做</option>
                  <option :value="false">选做</option>
                </select>
              </label>
              <label>逾期处理
                <select v-model="nodeForm.overdue_action">
                  <option value="remind">继续提醒</option>
                  <option value="manual_handoff">提醒健康管理师</option>
                  <option value="doctor_handoff">重点关注</option>
                  <option value="none">不处理</option>
                </select>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn danger" v-if="nodeForm.id" type="button" @click="deleteNode">删除</button>
          <span></span>
          <button class="btn" type="button" @click="nodeModal = false">取消</button>
          <button class="primary" type="button" @click="saveNode">保存任务节点</button>
        </div>
      </section>
    </div>

    <div v-if="knowledgeModal" class="modal-mask" @click.self="knowledgeModal = false">
      <section class="modal">
        <div class="modal-head">
          <h2>{{ knowledgeForm.id ? '编辑知识' : '新增知识' }}</h2>
          <button class="icon-close" type="button" @click="knowledgeModal = false">×</button>
        </div>
        <div class="form-grid">
          <label>标题<input v-model.trim="knowledgeForm.title"></label>
          <label>分类
            <select v-model="knowledgeForm.category">
              <option v-for="item in knowledgeCategoryOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
            </select>
          </label>
          <label>任务类型
            <select v-model="knowledgeForm.task_type">
              <option value="">通用</option>
              <option v-for="item in taskTypeOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
            </select>
          </label>
          <label>优先级<input v-model.number="knowledgeForm.priority" type="number"></label>
          <label class="wide">触发关键词<input v-model.trim="knowledgeForm.trigger_keywords" placeholder="饮食,运动,心理,乳腺结节"></label>
          <label class="wide">内容<textarea v-model.trim="knowledgeForm.content" rows="5"></textarea></label>
        </div>
        <div class="modal-actions">
          <button class="btn danger" v-if="knowledgeForm.id" type="button" @click="deleteKnowledge">删除</button>
          <span></span>
          <button class="btn" type="button" @click="knowledgeModal = false">取消</button>
          <button class="primary" type="button" @click="saveKnowledge">保存知识</button>
        </div>
      </section>
    </div>

    <div v-if="ruleModal" class="modal-mask" @click.self="ruleModal = false">
      <section class="modal">
        <div class="modal-head">
          <h2>{{ ruleForm.id ? '编辑AI规则' : '新增AI规则' }}</h2>
          <button class="icon-close" type="button" @click="ruleModal = false">×</button>
        </div>
        <div class="form-grid">
          <label>规则名称<input v-model.trim="ruleForm.name"></label>
          <label>规则类型
            <select v-model="ruleForm.rule_type">
              <option value="diet_review">饮食点评</option>
              <option value="image_recognition">图片识别</option>
              <option value="no_reply">未打卡/未回复</option>
              <option value="escalation">重点关注</option>
            </select>
          </label>
          <label>任务类型
            <select v-model="ruleForm.task_type">
              <option value="">通用</option>
              <option v-for="item in taskTypeOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
            </select>
          </label>
          <label>动作
            <select v-model="ruleForm.action">
              <option value="ai_reply">AI回复</option>
              <option value="manual_handoff">提醒健康管理师</option>
              <option value="doctor_handoff">重点关注</option>
              <option value="notify">通知</option>
              <option value="close">完成</option>
            </select>
          </label>
          <label class="wide">触发关键词<input v-model.trim="ruleForm.trigger_keywords" placeholder="咳血,胸痛,呼吸困难"></label>
          <label class="wide">回复模板<textarea v-model.trim="ruleForm.response_template" rows="4"></textarea></label>
        </div>
        <div class="modal-actions">
          <button class="btn danger" v-if="ruleForm.id" type="button" @click="deleteRule">删除</button>
          <button class="btn" type="button" @click="ruleModal = false">取消</button>
          <button class="primary" type="button" @click="saveRule">保存规则</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { apiJson, apiPostJson } from '../utils/apiClient'

const templates = ref([])
const knowledgeItems = ref([])
const aiRules = ref([])
const selectedTemplateId = ref(null)
const loading = ref(false)
const saving = ref(false)
const importingExcel = ref(false)
const error = ref('')
const toast = ref('')
const nodeModal = ref(false)
const knowledgeModal = ref(false)
const ruleModal = ref(false)
const excelInputRef = ref(null)
const knowledgeFilters = reactive({
  search: '',
  category: '',
  task_type: ''
})

const taskTypeOptions = [
  { value: 'knowledge_push', label: '知识推送' },
  { value: 'daily_checkin', label: '每日打卡' },
  { value: 'diet_checkin', label: '饮食打卡/图片识别' },
  { value: 'exercise_reminder', label: '运动提醒' },
  { value: 'psych_reminder', label: '心理提醒' },
  { value: 'review_reminder', label: '复查提醒' }
]

const knowledgeCategoryOptions = [
  { value: 'breast_nodule', label: '乳腺结节' },
  { value: 'lung_nodule', label: '肺结节' },
  { value: 'thyroid_nodule', label: '甲状腺结节' },
  { value: 'diet', label: '饮食' },
  { value: 'exercise', label: '运动' },
  { value: 'psych', label: '心理' },
  { value: 'review', label: '复查提醒' }
]

const aiActionOptions = [
  { value: 'reply', label: '自动回复' },
  { value: 'diet_review', label: '饮食点评' },
  { value: 'image_recognition', label: '图片识别' },
  { value: 'none', label: '不处理' }
]

const templateForm = reactive({
  id: null,
  name: '',
  description: '',
  nodule_type: '',
  risk_level: '',
  cycle_days: 90,
  default_channel: 'wecom',
  default_reminder_strategy: '每日固定时间提醒；未打卡继续提醒；餐饮图片自动分析',
  status: 'draft'
})

const nodeForm = reactive({
  id: null,
  name: '',
  day_offset: 1,
  send_time: '09:00',
  task_type: 'knowledge_push',
  patient_action: 'reply_text',
  ai_action: 'reply',
  message_template: '',
  knowledge_item_ids: [],
  doctor_keywords_text: '',
  manual_keywords_text: '',
  no_reply_threshold: 3,
  completion_type: 'patient_reply',
  overdue_action: 'manual_handoff',
  is_required: true,
  is_active: true,
  sort_order: 0
})

const knowledgeForm = reactive({
  id: null,
  title: '',
  category: 'script',
  task_type: '',
  priority: 5,
  trigger_keywords: '',
  content: ''
})

const ruleForm = reactive({
  id: null,
  name: '',
  rule_type: 'no_reply',
  task_type: 'daily_checkin',
  action: 'manual_handoff',
  trigger_keywords: '',
  response_template: ''
})

const selectedTemplate = computed(() => templates.value.find(t => t.id === selectedTemplateId.value) || null)
const sortedNodes = computed(() => [...(selectedTemplate.value?.nodes || [])].sort((a, b) => {
  const sortA = Number(a.sort_order ?? a.day_offset ?? 0)
  const sortB = Number(b.sort_order ?? b.day_offset ?? 0)
  if (sortA !== sortB) return sortA - sortB
  return (a.day_offset || 0) - (b.day_offset || 0)
}))
const totalNodes = computed(() => templates.value.reduce((sum, tpl) => sum + (tpl.nodes?.length || 0), 0))
const filteredKnowledgeItems = computed(() => {
  const search = knowledgeFilters.search.toLowerCase()
  return knowledgeItems.value.filter(item => {
    if (knowledgeFilters.category && item.category !== knowledgeFilters.category) return false
    if (knowledgeFilters.task_type && item.task_type !== knowledgeFilters.task_type) return false
    if (!search) return true
    return `${item.title || ''} ${item.content || ''} ${item.trigger_keywords || ''}`.toLowerCase().includes(search)
  })
})

async function postJson(url, payload) {
  return apiPostJson(url, payload)
}

function showToast(text) {
  toast.value = text
  window.setTimeout(() => {
    if (toast.value === text) toast.value = ''
  }, 2200)
}

function fillTemplateForm(tpl) {
  templateForm.id = tpl?.id || null
  templateForm.name = tpl?.name || ''
  templateForm.description = tpl?.description || ''
  templateForm.nodule_type = tpl?.nodule_type || ''
  templateForm.risk_level = tpl?.risk_level || ''
  templateForm.cycle_days = tpl?.cycle_days || 90
  templateForm.default_channel = tpl?.default_channel || 'wecom'
  templateForm.default_reminder_strategy = tpl?.default_reminder_strategy || '每日固定时间提醒；未打卡继续提醒；餐饮图片自动分析'
  templateForm.status = tpl?.status || 'draft'
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [tpls, knowledge, rules] = await Promise.all([
      apiJson('/api/b/followup/templates?include_nodes=1'),
      apiJson('/api/b/followup/knowledge?per_page=100'),
      apiJson('/api/b/followup/ai-rules')
    ])
    templates.value = Array.isArray(tpls) ? tpls : []
    knowledgeItems.value = knowledge?.items || []
    aiRules.value = Array.isArray(rules) ? rules : []
    if (!selectedTemplateId.value && templates.value.length) selectedTemplateId.value = templates.value[0].id
    if (selectedTemplate.value) fillTemplateForm(selectedTemplate.value)
  } catch (e) {
    error.value = e?.message || '加载随访知识库与模板失败'
  } finally {
    loading.value = false
  }
}

async function handleExcelImport(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  importingExcel.value = true
  error.value = ''
  try {
    const form = new FormData()
    form.append('file', file)
    form.append('replace_existing', 'true')
    form.append('name', '甲状腺结节合并肺结节90天健康管理模板')
    form.append('nodule_type', 'lung_thyroid')
    form.append('cycle_days', '90')
    form.append('default_channel', 'wecom')
    form.append('status', 'active')
    const res = await fetch('/api/b/followup/templates/import-excel', {
      method: 'POST',
      credentials: 'include',
      body: form
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok || data.success === false) throw new Error(data.message || `导入失败：${res.status}`)
    const result = data.data || data
    selectedTemplateId.value = result.template?.id || selectedTemplateId.value
    await loadAll()
    showToast(`已导入 ${result.days || 0} 天、${result.nodes || 0} 个任务节点`)
  } catch (e) {
    error.value = e?.message || 'Excel模板导入失败'
  } finally {
    importingExcel.value = false
  }
}

function selectTemplate(id) {
  selectedTemplateId.value = id
  fillTemplateForm(selectedTemplate.value)
}

function createTemplate() {
  selectedTemplateId.value = null
  fillTemplateForm({
    name: '新的健康管理任务模板',
    nodule_type: '',
    risk_level: '',
    cycle_days: 90,
    default_channel: 'wecom',
    status: 'draft'
  })
}

async function saveTemplate() {
  saving.value = true
  error.value = ''
  try {
    templateForm.default_channel = 'wecom'
    if (templateForm.status === 'active') {
      const issues = getTemplateIssues()
      if (issues.length) {
        error.value = `模板暂不能启用：${issues.join('；')}`
        return
      }
    }
    const payload = {
      name: templateForm.name,
      description: templateForm.description,
      nodule_type: templateForm.nodule_type || null,
      risk_level: templateForm.risk_level || null,
      cycle_days: Number(templateForm.cycle_days) || 90,
      default_channel: templateForm.default_channel,
      default_reminder_strategy: templateForm.default_reminder_strategy,
      status: templateForm.status
    }
    const saved = templateForm.id
      ? await apiJson(`/api/b/followup/templates/${templateForm.id}`, { method: 'PUT', body: JSON.stringify(payload) })
      : await postJson('/api/b/followup/templates', payload)
    selectedTemplateId.value = saved.id
    await loadAll()
    showToast('模板已保存')
  } catch (e) {
    error.value = e?.message || '模板保存失败'
  } finally {
    saving.value = false
  }
}

function getTemplateIssues() {
  const issues = []
  if (!templateForm.name) issues.push('模板名称不能为空')
  if (!selectedTemplateId.value) return issues
  const nodes = sortedNodes.value
  if (!nodes.length) issues.push('至少需要 1 个节点')
  nodes.forEach((node) => {
    if (node.is_active === false) return
    if (!node.name) issues.push(`Day ${node.day_offset || 1} 缺少节点名称`)
    if (!String(node.message_template || '').trim()) issues.push(`${node.name || `Day ${node.day_offset || 1}`} 缺少发送话术`)
    if (node.task_type === 'diet_checkin' && node.ai_action !== 'diet_review') issues.push(`${node.name || '饮食打卡节点'} 应配置饮食点评 AI 动作`)
    if (node.task_type === 'diet_checkin' && !['diet_review', 'image_recognition'].includes(node.ai_action)) issues.push(`${node.name || '饮食打卡节点'} 应配置饮食点评或图片识别`)
  })
  return issues
}

function validateTemplate() {
  const issues = getTemplateIssues()
  if (issues.length) {
    error.value = `校验未通过：${issues.join('；')}`
    return
  }
  error.value = ''
  showToast('模板校验通过，可以启用并下发给用户')
}

async function copyTemplate(tpl) {
  if (!tpl?.id) return
  const payload = {
    name: `${tpl.name} 副本`,
    description: tpl.description,
    nodule_type: tpl.nodule_type,
    risk_level: tpl.risk_level,
    cycle_days: tpl.cycle_days,
    default_channel: tpl.default_channel,
    default_reminder_strategy: tpl.default_reminder_strategy,
    status: 'draft',
    nodes: (tpl.nodes || []).map(node => ({
      node_code: `${node.node_code || 'NODE'}_COPY`,
      name: node.name,
      day_offset: node.day_offset,
      send_time: node.send_time,
      task_type: node.task_type,
      patient_action: node.patient_action,
      ai_action: node.ai_action,
      message_template: node.message_template,
      knowledge_item_ids: node.knowledge_item_ids || [],
      checkin_schema: node.checkin_schema || {},
      escalation_rule: node.escalation_rule || {},
      completion_rule: node.completion_rule || {},
      is_required: node.is_required !== false,
      is_active: node.is_active !== false,
      sort_order: node.sort_order || 0
    }))
  }
  const saved = await postJson('/api/b/followup/templates', payload)
  selectedTemplateId.value = saved.id
  await loadAll()
  showToast('模板已复制为草稿')
}

async function archiveTemplate(tpl) {
  if (!tpl?.id) return
  const nextStatus = tpl.status === 'archived' ? 'draft' : 'archived'
  await apiJson(`/api/b/followup/templates/${tpl.id}`, {
    method: 'PUT',
    body: JSON.stringify({ status: nextStatus })
  })
  await loadAll()
  showToast(nextStatus === 'archived' ? '模板已归档' : '模板已恢复为草稿')
}

async function deleteTemplate(tpl) {
  if (!tpl?.id) return
  if (!window.confirm(`确认删除模板「${tpl.name}」？已被患者计划引用的模板会删除失败，可改为归档。`)) return
  try {
    await apiJson(`/api/b/followup/templates/${tpl.id}`, { method: 'DELETE' })
    if (selectedTemplateId.value === tpl.id) selectedTemplateId.value = null
    await loadAll()
    showToast('模板已删除')
  } catch (e) {
    error.value = e?.message || '模板删除失败，可先归档'
  }
}

function addNode() {
  Object.assign(nodeForm, {
    id: null,
    name: '新的任务节点',
    day_offset: Math.max(1, ...sortedNodes.value.map(n => Number(n.day_offset || 0) + 7)),
    send_time: '09:00',
    task_type: 'knowledge_push',
    patient_action: 'reply_text',
    ai_action: 'reply',
    message_template: '请按健康管理任务完成本次打卡或查看提醒。',
    knowledge_item_ids: [],
    doctor_keywords_text: '不适,疼痛,明显加重',
    manual_keywords_text: '焦虑,担心,睡不着',
    no_reply_threshold: 3,
    completion_type: 'patient_reply',
    overdue_action: 'manual_handoff',
    is_required: true,
    is_active: true,
    sort_order: Math.max(0, ...sortedNodes.value.map(n => Number(n.sort_order ?? n.day_offset ?? 0))) + 1
  })
  nodeModal.value = true
}

function editNode(node) {
  const escalationRule = node.escalation_rule || {}
  const completionRule = node.completion_rule || {}
  Object.assign(nodeForm, {
    id: node.id,
    name: node.name || '',
    day_offset: node.day_offset || 1,
    send_time: node.send_time || '09:00',
    task_type: node.task_type || 'knowledge_push',
    patient_action: node.patient_action || 'reply_text',
    ai_action: node.ai_action || 'reply',
    message_template: node.message_template || '',
    knowledge_item_ids: [...(node.knowledge_item_ids || [])],
    doctor_keywords_text: joinKeywords(escalationRule.doctor_keywords),
    manual_keywords_text: joinKeywords(escalationRule.manual_keywords),
    no_reply_threshold: Number(escalationRule.no_reply_threshold ?? 3),
    completion_type: completionRule.type || 'patient_reply',
    overdue_action: completionRule.overdue_action || 'manual_handoff',
    is_required: node.is_required !== false,
    is_active: node.is_active !== false,
    sort_order: node.sort_order ?? node.day_offset ?? 0
  })
  nodeModal.value = true
}

function splitKeywords(text) {
  return String(text || '')
    .split(/[,，、\n]/)
    .map(item => item.trim())
    .filter(Boolean)
}

function joinKeywords(items) {
  return Array.isArray(items) ? items.join(',') : ''
}

function buildEscalationRule() {
  const doctorKeywords = splitKeywords(nodeForm.doctor_keywords_text)
  const manualKeywords = splitKeywords(nodeForm.manual_keywords_text)
  return {
    doctor_keywords: doctorKeywords,
    manual_keywords: manualKeywords,
    no_reply_threshold: Number(nodeForm.no_reply_threshold) || 0,
    abnormal_actions: {
      doctor_keywords: 'doctor_handoff',
      manual_keywords: 'manual_handoff',
      no_reply: nodeForm.overdue_action
    }
  }
}

function buildCompletionRule() {
  return {
    type: nodeForm.completion_type,
    overdue_action: nodeForm.overdue_action,
    required: nodeForm.is_required !== false
  }
}

async function saveNode() {
  try {
    const payload = {
      name: nodeForm.name,
      day_offset: Number(nodeForm.day_offset) || 1,
      send_time: nodeForm.send_time,
      task_type: nodeForm.task_type,
      patient_action: nodeForm.patient_action,
      ai_action: nodeForm.ai_action,
      message_template: nodeForm.message_template,
      knowledge_item_ids: nodeForm.knowledge_item_ids.map(Number),
      escalation_rule: buildEscalationRule(),
      completion_rule: buildCompletionRule(),
      is_required: nodeForm.is_required !== false,
      is_active: nodeForm.is_active !== false,
      sort_order: nodeForm.sort_order ?? (Number(nodeForm.day_offset) || 0)
    }
    if (nodeForm.id) {
      await apiJson(`/api/b/followup/nodes/${nodeForm.id}`, { method: 'PUT', body: JSON.stringify(payload) })
    } else {
      await postJson(`/api/b/followup/templates/${selectedTemplateId.value}/nodes`, payload)
    }
    nodeModal.value = false
    await loadAll()
    showToast('节点已保存')
  } catch (e) {
    error.value = e?.message || '节点保存失败'
  }
}

function nodePayloadFromNode(node, overrides = {}) {
  return {
    name: node.name,
    day_offset: node.day_offset,
    send_time: node.send_time,
    task_type: node.task_type,
    patient_action: node.patient_action,
    ai_action: node.ai_action,
    message_template: node.message_template,
    knowledge_item_ids: node.knowledge_item_ids || [],
    checkin_schema: node.checkin_schema || {},
    escalation_rule: node.escalation_rule || {},
    completion_rule: node.completion_rule || {},
    is_required: node.is_required !== false,
    is_active: node.is_active !== false,
    sort_order: node.sort_order ?? node.day_offset ?? 0,
    ...overrides
  }
}

async function toggleNodeActive(node) {
  await apiJson(`/api/b/followup/nodes/${node.id}`, {
    method: 'PUT',
    body: JSON.stringify(nodePayloadFromNode(node, { is_active: node.is_active === false }))
  })
  await loadAll()
  showToast(node.is_active === false ? '节点已启用' : '节点已停用')
}

async function copyNode(node) {
  const payload = nodePayloadFromNode(node, {
    node_code: `${node.node_code || 'NODE'}_COPY_${Date.now().toString().slice(-4)}`,
    name: `${node.name} 副本`,
    sort_order: Math.max(0, ...sortedNodes.value.map(item => Number(item.sort_order ?? item.day_offset ?? 0))) + 1
  })
  await postJson(`/api/b/followup/templates/${selectedTemplateId.value}/nodes`, payload)
  await loadAll()
  showToast('节点已复制')
}

async function moveNode(node, direction) {
  const nodes = sortedNodes.value
  const index = nodes.findIndex(item => item.id === node.id)
  const target = nodes[index + direction]
  if (!target) return
  const currentOrder = Number(node.sort_order ?? index)
  const targetOrder = Number(target.sort_order ?? (index + direction))
  await Promise.all([
    apiJson(`/api/b/followup/nodes/${node.id}`, {
      method: 'PUT',
      body: JSON.stringify(nodePayloadFromNode(node, { sort_order: targetOrder }))
    }),
    apiJson(`/api/b/followup/nodes/${target.id}`, {
      method: 'PUT',
      body: JSON.stringify(nodePayloadFromNode(target, { sort_order: currentOrder }))
    })
  ])
  await loadAll()
  showToast('节点顺序已更新')
}

async function deleteNode() {
  await apiJson(`/api/b/followup/nodes/${nodeForm.id}`, { method: 'DELETE' })
  nodeModal.value = false
  await loadAll()
  showToast('节点已删除')
}

function newKnowledge() {
  Object.assign(knowledgeForm, { id: null, title: '', category: 'diet', task_type: '', priority: 5, trigger_keywords: '', content: '' })
  knowledgeModal.value = true
}

function editKnowledge(item) {
  Object.assign(knowledgeForm, {
    id: item.id,
    title: item.title || '',
    category: item.category || 'script',
    task_type: item.task_type || '',
    priority: item.priority || 5,
    trigger_keywords: item.trigger_keywords || '',
    content: item.content || ''
  })
  knowledgeModal.value = true
}

async function saveKnowledge() {
  const payload = {
    title: knowledgeForm.title,
    category: knowledgeForm.category,
    task_type: knowledgeForm.task_type || null,
    priority: Number(knowledgeForm.priority) || 5,
    trigger_keywords: knowledgeForm.trigger_keywords,
    content: knowledgeForm.content,
    is_active: true
  }
  if (knowledgeForm.id) {
    await apiJson(`/api/b/followup/knowledge/${knowledgeForm.id}`, { method: 'PUT', body: JSON.stringify(payload) })
  } else {
    await postJson('/api/b/followup/knowledge', payload)
  }
  knowledgeModal.value = false
  await loadAll()
  showToast('知识库已保存')
}

async function deleteKnowledge() {
  await apiJson(`/api/b/followup/knowledge/${knowledgeForm.id}`, { method: 'DELETE' })
  knowledgeModal.value = false
  await loadAll()
  showToast('知识条目已删除')
}

function newRule() {
  Object.assign(ruleForm, {
    id: null,
    name: '',
    rule_type: 'no_reply',
    task_type: 'daily_checkin',
    action: 'manual_handoff',
    trigger_keywords: '',
    response_template: ''
  })
  ruleModal.value = true
}

function editRule(rule) {
  Object.assign(ruleForm, {
    id: rule.id,
    name: rule.name || '',
    rule_type: rule.rule_type || 'no_reply',
    task_type: rule.task_type || '',
    action: rule.action || 'manual_handoff',
    trigger_keywords: rule.trigger_keywords || '',
    response_template: rule.response_template || ''
  })
  ruleModal.value = true
}

async function saveRule() {
  const payload = {
    name: ruleForm.name,
    rule_type: ruleForm.rule_type,
    task_type: ruleForm.task_type || null,
    action: ruleForm.action,
    trigger_keywords: ruleForm.trigger_keywords,
    response_template: ruleForm.response_template,
    is_active: true
  }
  if (ruleForm.id) {
    await apiJson(`/api/b/followup/ai-rules/${ruleForm.id}`, { method: 'PUT', body: JSON.stringify(payload) })
  } else {
    await postJson('/api/b/followup/ai-rules', payload)
  }
  ruleModal.value = false
  await loadAll()
  showToast(ruleForm.id ? 'AI规则已更新' : 'AI规则已创建')
}

async function deleteRule() {
  if (!ruleForm.id) return
  await apiJson(`/api/b/followup/ai-rules/${ruleForm.id}`, { method: 'DELETE' })
  ruleModal.value = false
  await loadAll()
  showToast('AI规则已删除')
}

function knowledgeTitle(id) {
  return knowledgeItems.value.find(item => item.id === Number(id))?.title || `知识#${id}`
}

function noduleText(v) {
  return ({
    breast: '乳腺',
    thyroid: '甲状腺',
    lung: '肺部',
    breast_lung: '乳腺+肺部',
    breast_thyroid: '乳腺+甲状腺',
    lung_thyroid: '肺部+甲状腺',
    triple: '三合并结节'
  }[v] || '通用')
}

function riskText(v) {
  return ({ high: '高风险', mid: '中风险', medium: '中风险', low: '低风险' }[v] || '全部风险')
}

function statusText(v) {
  return ({ draft: '草稿', active: '启用', paused: '暂停', archived: '归档' }[v] || v || '草稿')
}

function taskTypeText(v) {
  return (taskTypeOptions.find(item => item.value === v)?.label || '通用')
}

function patientActionText(v) {
  return ({ none: '无需动作', reply_text: '回复文本', upload_image: '上传图片', upload_report: '上传报告', fill_form: '填写表单' }[v] || '回复文本')
}

function aiActionText(v) {
  return ({ reply: 'AI回复', diet_review: '饮食点评', image_recognition: '图片识别', none: '不处理' }[v] || 'AI回复')
}

function categoryText(v) {
  return (knowledgeCategoryOptions.find(item => item.value === v)?.label || v || '知识')
}

function ruleTypeText(v) {
  return ({ diet_review: '饮食点评', image_recognition: '图片识别', no_reply: '未打卡/未回复', escalation: '重点关注' }[v] || v)
}

function actionText(v) {
  return ({ ai_reply: 'AI回复', manual_handoff: '提醒健康管理师', doctor_handoff: '重点关注', notify: '通知', close: '完成' }[v] || v)
}

onMounted(loadAll)
</script>

<style scoped>
.workflow-page{height:100%;min-height:0;display:flex;flex-direction:column;gap:14px;color:#172033}
.page-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
.crumb{margin:0 0 4px;color:#667085;font-size:13px}
h1{margin:0;font-size:24px;line-height:1.2}
h2{margin:0;font-size:16px}
h3{margin:0;font-size:15px}
.head-actions,.modal-actions{display:flex;align-items:center;gap:8px}
.btn,.primary,.mini-btn{border:1px solid #d0d5dd;background:#fff;color:#344054;border-radius:8px;height:36px;padding:0 12px;font-weight:800;cursor:pointer}
.primary{background:#155eef;border-color:#155eef;color:#fff}
.mini-btn{height:30px;padding:0 10px;font-size:12px}
.danger{border-color:#fecdca;color:#b42318}
button:disabled{opacity:.6;cursor:not-allowed}
.notice{border:1px solid #b2ddff;background:#eff8ff;color:#175cd3;border-radius:8px;padding:10px 12px;font-weight:700}
.notice.error{border-color:#fecdca;background:#fffbfa;color:#b42318}
.workflow-grid{flex:1;min-height:0;display:grid;grid-template-columns:280px minmax(0,1fr);gap:14px;align-items:stretch}
.panel{background:#fff;border:1px solid #e4e7ec;border-radius:8px;padding:14px;box-shadow:0 8px 22px rgba(16,24,40,.05)}
.template-panel,.editor-panel{min-height:0;overflow:hidden;display:flex;flex-direction:column}
.editor-panel{overflow:auto}
.panel-head,.section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.editor-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.section-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.panel-head p,.section-head p{margin:4px 0 0;color:#667085;font-size:12px;line-height:1.5}
.template-list,.knowledge-list,.rule-list,.node-list{display:grid;gap:10px}
.template-list{overflow:auto;min-height:0;scrollbar-width:thin;padding-right:2px}
.template-item,.knowledge-item{width:100%;border:1px solid #e4e7ec;background:#fff;border-radius:8px;padding:11px;text-align:left;display:grid;gap:6px;position:relative}
.template-item.active{border-color:#155eef;background:#eff6ff}
.template-select{border:0;background:transparent;padding:0;text-align:left;display:grid;gap:6px;cursor:pointer}
.item-title,.knowledge-item b{font-weight:900;color:#172033}
.item-meta,.knowledge-item span,.rule-item span,.node-top span{color:#667085;font-size:12px}
.item-foot{display:flex;justify-content:space-between;color:#475467;font-size:12px}
.item-foot b{color:#155eef}
.item-foot em{font-style:normal}
.template-more,.node-more{position:relative;justify-self:start}
.template-more > summary,.node-more > summary{list-style:none;color:#155eef;font-size:12px;font-weight:900;cursor:pointer}
.template-more > summary::-webkit-details-marker,.node-more > summary::-webkit-details-marker{display:none}
.template-menu{position:absolute;z-index:10;top:22px;left:0;width:118px;border:1px solid #e4e7ec;border-radius:8px;background:#fff;box-shadow:0 12px 28px rgba(16,24,40,.14);padding:6px;display:grid;gap:2px}
.template-menu button{border:0;background:#fff;text-align:left;border-radius:6px;padding:7px 8px;font-size:12px;font-weight:800;color:#344054;cursor:pointer}
.template-menu button:hover{background:#f2f4f7}
.danger-text{color:#b42318 !important}
.editor-stack{display:grid;gap:12px}
.editor-section{border:1px solid #e4e7ec;border-radius:8px;background:#fff;padding:14px}
.compact-head{border:0;margin:0 0 12px;padding:0}
.form-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.form-grid.compact{grid-template-columns:repeat(3,minmax(0,1fr))}
label{display:grid;gap:6px;color:#344054;font-size:13px;font-weight:800}
input,select,textarea{width:100%;box-sizing:border-box;border:1px solid #d0d5dd;border-radius:8px;padding:9px 10px;color:#172033;font:inherit;background:#fff}
select[multiple]{min-height:110px}
textarea{resize:vertical;line-height:1.6}
.wide{grid-column:1/-1}
.rule-box{border:1px solid #e4e7ec;border-radius:8px;padding:12px;background:#f8fafc;display:grid;gap:10px}
.rule-box-title{font-weight:900;color:#172033;font-size:14px}
.section-head{margin-top:18px;padding-top:14px;border-top:1px solid #eef2f7}
.node-card{border:1px solid #e4e7ec;border-radius:8px;padding:12px;background:#fbfdff;display:grid;gap:10px}
.node-card.inactive{opacity:.68;background:#f8fafc}
.node-top{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:10px}
.node-main{display:grid;gap:3px;min-width:0}
.node-main strong{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.node-actions{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.day-badge{background:#155eef;color:#fff;border-radius:8px;padding:7px 9px;font-size:12px;font-weight:900}
.day-badge span{font-size:11px;color:rgba(255,255,255,.82)}
.node-card p{margin:0;color:#475467;line-height:1.6}
.node-tags{display:flex;flex-wrap:wrap;gap:6px}
.node-tags span{border:1px solid #d0d5dd;border-radius:999px;padding:4px 8px;color:#475467;font-size:12px;background:#fff}
.empty{border:1px dashed #d0d5dd;border-radius:8px;padding:20px;color:#667085;text-align:center}
.side-filters{display:grid;gap:8px;margin-bottom:10px}
.knowledge-list{max-height:340px;overflow:auto}
.rule-item{border:1px solid #e4e7ec;border-radius:8px;padding:10px;display:grid;gap:5px;background:#fff;text-align:left;cursor:pointer}
.rule-item:hover{border-color:#155eef;background:#eff6ff}
.rule-item p{margin:0;color:#667085;font-size:12px;line-height:1.5}
.compact-empty{padding:12px;font-size:12px}
.modal-mask{position:fixed;inset:0;background:rgba(15,23,42,.42);display:grid;place-items:center;z-index:50;padding:20px}
.modal{width:min(860px,100%);max-height:90vh;overflow:auto;background:#fff;border-radius:10px;padding:16px;box-shadow:0 24px 80px rgba(15,23,42,.28)}
.modal-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.icon-close{width:32px;height:32px;border:1px solid #e4e7ec;border-radius:8px;background:#fff;font-size:22px;line-height:1;cursor:pointer}
.modal-actions{display:grid;grid-template-columns:auto 1fr auto auto;margin-top:14px}
@media (max-width:1200px){.workflow-grid{grid-template-columns:240px minmax(0,1fr)}}
@media (max-width:820px){.workflow-page{height:auto}.workflow-grid,.form-grid{grid-template-columns:1fr}.page-head{display:grid}.modal-actions{grid-template-columns:1fr 1fr}.modal-actions span{display:none}.node-top{grid-template-columns:1fr}.node-actions{justify-content:flex-start}}
</style>
