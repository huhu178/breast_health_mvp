<template>
  <div class="recommendation-card" :class="cardClass">
    <div class="card-header">
      <div class="header-left">
        <span class="category-badge" :style="categoryStyle">{{ recommendation.category }}</span>
        <span v-if="recommendation.subcategory" class="subcategory">{{ recommendation.subcategory }}</span>
        <span class="priority-badge" :class="priorityClass">
          优先级 {{ recommendation.priority }}
        </span>
      </div>
      <div class="header-right">
        <span v-if="recommendation.is_approved" class="status-badge approved">已批准</span>
        <span v-else class="status-badge pending">待审核</span>
      </div>
    </div>

    <div class="card-body">
      <div v-if="!isEditing" class="recommendation-text">
        {{ recommendation.recommendation }}
      </div>
      <div v-else class="recommendation-edit">
        <textarea 
          v-model="editedText" 
          class="edit-textarea"
          rows="4"
          placeholder="编辑建议内容..."
        ></textarea>
      </div>

      <div class="knowledge-sources">
        <div class="sources-header" @click="toggleSources">
          <span class="sources-title">
            知识库来源（{{ recommendation.knowledge_sources.length }}条）
          </span>
          <span class="toggle-icon">{{ showSources ? '收起' : '展开' }}</span>
        </div>
        
        <div v-if="showSources" class="sources-list">
          <div 
            v-for="(source, idx) in recommendation.knowledge_sources" 
            :key="idx"
            class="source-item"
          >
            <div class="source-header">
              <span class="source-id">#{{ source.id }}</span>
              <span class="source-title">{{ source.title }}</span>
            </div>
            <div class="source-content">{{ truncateText(source.content, 200) }}</div>
          </div>
        </div>
      </div>
    </div>

      <div class="card-footer">
        <div class="footer-left">
          <button v-if="!isEditing" @click="startEdit" class="btn btn-edit">
            编辑
          </button>
          <button v-else @click="saveEdit" class="btn btn-save">
            保存
          </button>
          <button v-if="isEditing" @click="cancelEdit" class="btn btn-cancel">
            取消
          </button>
          <button @click="confirmDelete" class="btn btn-delete">
            删除
          </button>
        </div>
        <div class="footer-right">
          <button 
            v-if="!recommendation.is_approved" 
            @click="approve" 
            class="btn btn-approve"
          >
            批准
          </button>
          <button 
            v-else 
            @click="unapprove" 
            class="btn btn-unapprove"
          >
            撤销批准
          </button>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  recommendation: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update', 'delete', 'approve'])

const isEditing = ref(false)
const editedText = ref('')
const showSources = ref(false)

const cardClass = computed(() => ({
  'approved': props.recommendation.is_approved,
  'high-priority': props.recommendation.priority <= 3
}))

const priorityClass = computed(() => {
  const p = props.recommendation.priority
  if (p <= 3) return 'priority-high'
  if (p <= 6) return 'priority-medium'
  return 'priority-low'
})

const categoryStyle = computed(() => {
  const colors = {
    '结论与预警': '#d32f2f',
    '风险因素评估': '#f57c00',
    '影像学建议': '#1976d2',
    '症状管理': '#388e3c',
    '家族史管理': '#00796b',
    '年龄相关建议': '#0288d1',
    '病程时间轴建议': '#5d4037',
    '检查史管理': '#00796b',
    '生物节律调节': '#00897b',
    '睡眠管理': '#1565c0',
    '疾病史管理': '#689f38',
    '遗传史管理': '#e64a19',
    '当前病史管理': '#0097a7'
  }
  const color = colors[props.recommendation.category] || '#757575'
  return { backgroundColor: color }
})

function toggleSources() {
  showSources.value = !showSources.value
}

function startEdit() {
  editedText.value = props.recommendation.recommendation
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  editedText.value = ''
}

function saveEdit() {
  if (!editedText.value.trim()) {
    alert('建议内容不能为空')
    return
  }
  
  emit('update', {
    index: props.index,
    recommendation: editedText.value.trim()
  })
  
  isEditing.value = false
}

function approve() {
  emit('approve', {
    index: props.index,
    is_approved: true
  })
}

function unapprove() {
  emit('approve', {
    index: props.index,
    is_approved: false
  })
}

function confirmDelete() {
  if (confirm(`确定要删除这条"${props.recommendation.category}"建议吗？`)) {
    emit('delete', props.index)
  }
}

function truncateText(text, maxLength) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
</script>

<style scoped>
.recommendation-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  background: white;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.recommendation-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.recommendation-card.approved {
  border-color: #4caf50;
  background: #f1f8f4;
}

.recommendation-card.high-priority {
  border-left: 6px solid #f44336;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.category-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.subcategory {
  padding: 4px 10px;
  background: #f5f5f5;
  border-radius: 12px;
  font-size: 13px;
  color: #666;
}

.priority-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.priority-high {
  background: #ffebee;
  color: #c62828;
}

.priority-medium {
  background: #fff3e0;
  color: #e65100;
}

.priority-low {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
}

.status-badge.approved {
  background: #4caf50;
  color: white;
}

.status-badge.pending {
  background: #ff9800;
  color: white;
}

.card-body {
  margin-bottom: 15px;
}

.recommendation-text {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  padding: 15px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 15px;
}

.edit-textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #2196f3;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.8;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 15px;
}

.knowledge-sources {
  background: #f9f9f9;
  border-radius: 8px;
  overflow: hidden;
}

.sources-header {
  padding: 12px 15px;
  background: #eeeeee;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
  transition: background 0.2s;
}

.sources-header:hover {
  background: #e0e0e0;
}

.sources-title {
  font-weight: bold;
  font-size: 14px;
  color: #555;
}

.toggle-icon {
  color: #999;
  font-size: 12px;
}

.sources-list {
  padding: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.source-item {
  padding: 12px;
  background: white;
  border-radius: 6px;
  margin-bottom: 10px;
  border-left: 3px solid #2196f3;
}

.source-item:last-child {
  margin-bottom: 0;
}

.source-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.source-id {
  background: #2196f3;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: bold;
}

.source-title {
  font-weight: bold;
  font-size: 13px;
  color: #333;
}

.source-content {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.footer-left, .footer-right {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.btn-edit {
  background: #2196f3;
  color: white;
}

.btn-edit:hover {
  background: #1976d2;
}

.btn-save {
  background: #4caf50;
  color: white;
}

.btn-save:hover {
  background: #388e3c;
}

.btn-cancel {
  background: #9e9e9e;
  color: white;
}

.btn-cancel:hover {
  background: #757575;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.btn-delete:hover {
  background: #d32f2f;
}

.btn-approve {
  background: #4caf50;
  color: white;
  font-weight: bold;
}

.btn-approve:hover {
  background: #388e3c;
}

.btn-unapprove {
  background: #ff9800;
  color: white;
}

.btn-unapprove:hover {
  background: #f57c00;
}
</style>



