<template>
  <div class="workflow-page">
    <header class="page-head">
      <div>
        <p class="crumb">首页 / 随访知识库与模板</p>
        <h1>随访知识库与模板</h1>
        <p class="page-sub">{{ workflowCopy.pageSub }}</p>
      </div>
      <div class="head-actions">
        <button class="btn" type="button" @click="loadAll">刷新</button>
        <input ref="excelInputRef" type="file" accept=".xlsx,.xlsm" style="display:none" @change="handleExcelImport">
        <button class="btn" type="button" :disabled="importingExcel" @click="excelInputRef?.click()">
          {{ importingExcel ? '导入中...' : '导入Excel模板' }}
        </button>
        <button class="btn" type="button" @click="newKnowledge">新增知识</button>
        <button class="btn" type="button" @click="newRule">新增AI规则</button>
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
            <p>{{ workflowCopy.templateSub }}</p>
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
            <p>{{ workflowCopy.editorSub }}</p>
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

          <section class="editor-section">
            <div class="section-head compact-head">
              <div>
                <h3>知识库</h3>
                <p>{{ workflowCopy.knowledgeSub }}</p>
              </div>
              <button class="btn" type="button" @click="newKnowledge">新增知识</button>
            </div>
            <div class="side-filters">
              <input v-model.trim="knowledgeFilters.search" placeholder="搜索知识标题 / 内容 / 关键词">
              <div class="filter-row">
                <select v-model="knowledgeFilters.category">
                  <option value="">全部分类</option>
                  <option v-for="item in knowledgeCategoryOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
                </select>
                <select v-model="knowledgeFilters.task_type">
                  <option value="">全部任务类型</option>
                  <option v-for="item in taskTypeOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
                </select>
              </div>
            </div>
            <div class="knowledge-list">
              <button
                v-for="item in filteredKnowledgeItems"
                :key="item.id"
                class="knowledge-item"
                type="button"
                @click="editKnowledge(item)"
              >
                <b>{{ item.title }}</b>
                <span>{{ categoryText(item.category) }} · {{ taskTypeText(item.task_type) }}</span>
                <p>{{ item.content }}</p>
              </button>
              <div v-if="!filteredKnowledgeItems.length" class="empty compact-empty">暂无匹配知识</div>
            </div>
          </section>

          <section class="editor-section">
            <div class="section-head compact-head">
              <div>
                <h3>AI规则</h3>
                <p>{{ workflowCopy.ruleSub }}</p>
              </div>
              <button class="btn" type="button" @click="newRule">新增AI规则</button>
            </div>
            <div class="rule-list">
              <button
                v-for="rule in aiRules"
                :key="rule.id"
                class="rule-item"
                type="button"
                @click="editRule(rule)"
              >
                <b>{{ rule.name }}</b>
                <span>{{ ruleTypeText(rule.rule_type) }} · {{ taskTypeText(rule.task_type) }} · {{ actionText(rule.action) }}</span>
                <p>{{ rule.response_template || rule.trigger_keywords || '未配置回复模板' }}</p>
              </button>
              <div v-if="!aiRules.length" class="empty compact-empty">暂无 AI 规则</div>
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
          <label class="wide">触发关键词<input v-model.trim="knowledgeForm.trigger_keywords" :placeholder="workflowCopy.keywordPlaceholder"></label>
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
import { computed, onMounted, ref } from 'vue'
import { useFollowupAiRules } from '../composables/useFollowupAiRules'
import { useFollowupKnowledge } from '../composables/useFollowupKnowledge'
import { useFollowupTemplateNodes } from '../composables/useFollowupTemplateNodes'
import { useFollowupTemplates } from '../composables/useFollowupTemplates'
import { useFollowupWorkflowConfig } from '../composables/useFollowupWorkflowConfig'
import { getStoredScenario } from '../config/scenarios'

const excelInputRef = ref(null)
const scenario = computed(() => getStoredScenario())
const workflowCopy = computed(() => {
  if (scenario.value.key === 'pharmacy') {
    return {
      pageSub: '维护药店健康服务随访模板、用药提醒、报告解读提醒和药师回访话术',
      templateSub: '定义每日名师视频、用药提醒、健康打卡、复购提醒和药师回访周期',
      editorSub: '维护名师讲解视频、结节健康知识、药事提醒话术，并编排固定企业微信推送任务',
      knowledgeSub: '维护可复用的名师视频、报告解读、用药注意、饮食运动和药师回访素材',
      ruleSub: '配置视频未观看提醒、饮食点评、未回复提醒、资料上传提醒和药师重点跟进规则',
      keywordPlaceholder: '名师视频,用药,复购,报告解读,饮食,运动,结节'
    }
  }
  return {
    pageSub: '维护随访模板、知识库和 AI 规则',
    templateSub: '定义推送内容、打卡要求和执行周期',
    editorSub: '维护七大类知识库，并编排固定企业微信推送任务',
    knowledgeSub: '维护可复用的话术、知识卡和任务素材',
    ruleSub: '配置图片识别、饮食点评、未回复和重点关注规则',
    keywordPlaceholder: '饮食,运动,心理,乳腺结节'
  }
})

const taskTypeOptions = [
  { value: 'knowledge_push', label: '知识推送' },
  { value: 'video_push', label: '名师视频推送' },
  { value: 'daily_checkin', label: '每日打卡' },
  { value: 'diet_checkin', label: '饮食打卡/图片识别' },
  { value: 'exercise_reminder', label: '运动提醒' },
  { value: 'psych_reminder', label: '心理提醒' },
  { value: 'review_reminder', label: '复查提醒' }
]

const knowledgeCategoryOptions = [
  { value: 'expert_video', label: '名师讲解视频' },
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

const {
  aiRules,
  error,
  handleExcelImport,
  importingExcel,
  knowledgeItems,
  loadAll,
  loading,
  selectedTemplate,
  selectedTemplateId,
  showToast,
  sortedNodes,
  templates,
  toast,
  totalNodes,
} = useFollowupWorkflowConfig()
const {
  archiveTemplate,
  copyTemplate,
  createTemplate,
  deleteTemplate,
  fillTemplateForm,
  saveTemplate,
  saving,
  selectTemplate,
  templateForm,
  validateTemplate,
} = useFollowupTemplates({
  error,
  loadAll,
  selectedTemplate,
  selectedTemplateId,
  showToast,
  sortedNodes,
})
const {
  addNode,
  copyNode,
  deleteNode,
  editNode,
  moveNode,
  nodeForm,
  nodeModal,
  saveNode,
  toggleNodeActive,
} = useFollowupTemplateNodes({
  error,
  loadAll,
  selectedTemplateId,
  showToast,
  sortedNodes,
})
const {
  deleteKnowledge,
  editKnowledge,
  filteredKnowledgeItems,
  knowledgeFilters,
  knowledgeForm,
  knowledgeModal,
  newKnowledge,
  saveKnowledge,
} = useFollowupKnowledge({
  knowledgeItems,
  loadAll,
  showToast,
})
const {
  deleteRule,
  editRule,
  newRule,
  ruleForm,
  ruleModal,
  saveRule,
} = useFollowupAiRules({
  loadAll,
  showToast,
})

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

onMounted(async () => {
  await loadAll()
  fillTemplateForm(selectedTemplate.value)
})
</script>

<style scoped>
.workflow-page{height:100%;min-height:0;display:flex;flex-direction:column;gap:14px;color:#172033}
.page-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
.crumb{margin:0 0 4px;color:#667085;font-size:13px}
.page-sub{margin:6px 0 0;color:#667085;font-size:13px;line-height:1.5}
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
.filter-row{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.knowledge-list{max-height:340px;overflow:auto}
.knowledge-item p{margin:0;color:#667085;font-size:12px;line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
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
