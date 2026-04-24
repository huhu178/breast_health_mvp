<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const knowledgeItems = ref([])
const isLoading = ref(true)
const currentPage = ref(1)
const totalItems = ref(0)
const searchKeyword = ref('')
const selectedCategory = ref('')

const categories = [
  { value: '', label: '全部分类' },
  { value: 'risk_assessment', label: '风险评估' },
  { value: 'lifestyle', label: '生活方式' },
  { value: 'diet', label: '饮食建议' },
  { value: 'follow_up', label: '随访建议' }
]

async function loadKnowledgeItems() {
  isLoading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: 20
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    
    const response = await axios.get('/api/knowledge', {
      params,
      withCredentials: true
    })
    
    if (response.data.success) {
      knowledgeItems.value = response.data.data.items || []
      totalItems.value = response.data.data.total || 0
    }
  } catch (error) {
    console.error('加载知识库失败:', error)
  } finally {
    isLoading.value = false
  }
}

function viewDetail(itemId) {
  alert(`知识详情 ID: ${itemId}`)
}

onMounted(() => {
  loadKnowledgeItems()
})
</script>

<template>
  <div class="knowledge-view">
    <header class="page-header">
      <h2 class="page-title">📚 知识库管理</h2>
      <div class="header-actions">
        <select v-model="selectedCategory" class="category-select" @change="loadKnowledgeItems">
          <option v-for="cat in categories" :key="cat.value" :value="cat.value">
            {{ cat.label }}
          </option>
        </select>
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索关键词"
          class="search-input"
          @keyup.enter="loadKnowledgeItems"
        />
        <button class="btn btn-primary" @click="loadKnowledgeItems">搜索</button>
      </div>
    </header>
    
    <section class="card">
      <div v-if="isLoading" class="loading">加载中...</div>
      
      <div v-else class="knowledge-grid">
        <div v-if="!knowledgeItems.length" class="empty">
          暂无知识库数据
        </div>
        
        <div 
          v-for="item in knowledgeItems" 
          :key="item.id" 
          class="knowledge-card"
          @click="viewDetail(item.id)"
        >
          <div class="card-header">
            <span class="category-badge">{{ item.category || '未分类' }}</span>
            <span v-if="item.match_type" class="match-type">{{ item.match_type }}</span>
          </div>
          
          <h3 class="card-title">{{ item.title || '无标题' }}</h3>
          
          <div class="card-content">
            <p class="content-text">{{ item.content || '暂无内容' }}</p>
          </div>
          
          <div class="card-footer">
            <span class="info-item" v-if="item.birads_level">
              BI-RADS: {{ item.birads_level }}级
            </span>
            <span class="info-item" v-if="item.age_group">
              年龄: {{ item.age_group }}
            </span>
          </div>
        </div>
      </div>
      
      <div v-if="totalItems > 0" class="pagination">
        <span>共 {{ totalItems }} 条知识</span>
      </div>
    </section>
  </div>
</template>

<style scoped>
.knowledge-view {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.category-select {
  padding: 10px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  background: #fff;
}

.category-select:focus {
  outline: none;
  border-color: #409eff;
}

.search-input {
  padding: 10px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  width: 200px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #409eff;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.loading {
  text-align: center;
  padding: 60px;
  color: #909399;
}

.empty {
  text-align: center;
  padding: 60px;
  color: #909399;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.knowledge-card {
  background: #f9fafb;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.knowledge-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  border-color: #409eff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.category-badge {
  display: inline-block;
  padding: 4px 12px;
  background: #ecf5ff;
  color: #409eff;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.match-type {
  font-size: 12px;
  color: #909399;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.card-content {
  margin-bottom: 12px;
}

.content-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-footer {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.info-item {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #409eff;
  color: #fff;
}

.btn-primary:hover {
  background: #66b1ff;
}

.pagination {
  margin-top: 20px;
  text-align: right;
  color: #606266;
  font-size: 14px;
}
</style>

