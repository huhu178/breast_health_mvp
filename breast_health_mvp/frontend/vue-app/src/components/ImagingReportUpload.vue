<template>
  <div class="imaging-report-upload">
    <div class="section-header">
      <div class="section-icon"></div>
      <h3 class="section-title">影像报告上传</h3>
      <span class="section-tip">支持PDF格式，可上传多个文件</span>
    </div>

    <!-- 文件上传区域 -->
    <div class="upload-area">
      <input
        ref="fileInputRef"
        type="file"
        multiple
        accept=".pdf"
        @change="handleFileSelect"
        style="display: none"
      />
      <div
        class="upload-dropzone"
        @click="triggerFileInput"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleFileDrop"
        :class="{ 'is-dragging': isDragging }"
      >
        <div class="upload-icon">📎</div>
        <div class="upload-text">
          <p>点击或拖拽文件到此处上传</p>
          <p class="upload-hint">支持PDF格式，单个文件不超过10MB</p>
        </div>
      </div>
    </div>

    <!-- 已上传文件列表 -->
    <div v-if="files.length > 0" class="file-list">
      <div
        v-for="(file, index) in files"
        :key="index"
        class="file-item"
      >
        <div class="file-info">
          <span class="file-icon">📄</span>
          <div class="file-details">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-meta">
              {{ formatFileSize(file.size) }} · 
              {{ file.uploadTime ? formatTime(file.uploadTime) : '刚刚上传' }}
            </div>
          </div>
        </div>
        <div class="file-actions">
          <button
            v-if="file.url"
            class="btn-preview"
            @click="previewFile(file)"
            title="预览"
          >
            预览
          </button>
          <button
            class="btn-delete"
            @click="removeFile(index)"
            title="删除"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const fileInputRef = ref(null)
const isDragging = ref(false)
const files = ref([])

// 触发文件选择
function triggerFileInput() {
  fileInputRef.value?.click()
}

// 处理文件选择
function handleFileSelect(event) {
  const selectedFiles = Array.from(event.target.files || [])
  addFiles(selectedFiles)
  // 清空input，允许重复选择同一文件
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// 处理拖拽上传
function handleFileDrop(event) {
  isDragging.value = false
  const droppedFiles = Array.from(event.dataTransfer.files || [])
  addFiles(droppedFiles)
}

// 添加文件
function addFiles(newFiles) {
  const validFiles = []
  
  for (const file of newFiles) {
    // 检查文件类型
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      ElMessage.warning(`文件 ${file.name} 不是PDF格式，已跳过`)
      continue
    }
    
    // 检查文件大小（10MB）
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.warning(`文件 ${file.name} 超过10MB限制，已跳过`)
      continue
    }
    
    // 检查是否已存在同名文件
    if (files.value.some(f => f.name === file.name && f.size === file.size)) {
      ElMessage.warning(`文件 ${file.name} 已存在，已跳过`)
      continue
    }
    
    validFiles.push({
      file: file,  // 原始File对象
      name: file.name,
      size: file.size,
      uploadTime: new Date()
    })
  }
  
  if (validFiles.length > 0) {
    files.value.push(...validFiles)
    emit('update:modelValue', files.value.map(f => f.file))
    ElMessage.success(`成功添加 ${validFiles.length} 个文件`)
  }
}

// 删除文件
function removeFile(index) {
  files.value.splice(index, 1)
  emit('update:modelValue', files.value.map(f => f.file))
}

// 预览文件
function previewFile(file) {
  if (file.url) {
    window.open(file.url, '_blank')
  } else if (file.file) {
    // 创建临时URL预览
    const url = URL.createObjectURL(file.file)
    window.open(url, '_blank')
    // 注意：预览后需要清理URL，避免内存泄漏
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 格式化时间
function formatTime(date) {
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (seconds < 60) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return date.toLocaleDateString('zh-CN')
}

// 暴露方法：获取文件列表（用于表单提交）
defineExpose({
  getFiles: () => files.value.map(f => f.file)
})
</script>

<style scoped>
.imaging-report-upload {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #409eff;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.section-icon {
  width: 4px;
  height: 20px;
  background: #409eff;
  border-radius: 2px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.section-tip {
  font-size: 13px;
  color: #909399;
  margin-left: auto;
}

.upload-area {
  margin-bottom: 20px;
}

.upload-dropzone {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.upload-dropzone:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.upload-dropzone.is-dragging {
  border-color: #409eff;
  background: #e6f7ff;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.upload-text p {
  margin: 8px 0;
  color: #606266;
}

.upload-hint {
  font-size: 13px;
  color: #909399;
}

.file-list {
  margin-top: 20px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.file-item:hover {
  background: #ebedf0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.file-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.file-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-preview,
.btn-delete {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.btn-preview {
  background: #409eff;
  color: #fff;
}

.btn-preview:hover {
  background: #66b1ff;
}

.btn-delete {
  background: #f56c6c;
  color: #fff;
}

.btn-delete:hover {
  background: #f78989;
}
</style>




