<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const reportId = route.params.id

// 检查是否是审核模式（通过查询参数 review=true）
const isReviewMode = computed(() => route.query.review === 'true')
// C端报告预览：/reports/:id?source=c_end
const isCEndSource = computed(() => route.query?.source === 'c_end')

const report = ref(null)
const reportHtml = ref(null)
const isLoading = ref(true)
const isPrinting = ref(false)
const isPublishing = ref(false)

// 编辑状态
const editingImagingConclusion = ref(false)
const editingImagingWarning = ref(false)
const editingMedicalConclusion = ref(false)
const editingMedicalWarning = ref(false)
const editingImagingConclusionText = ref('')
const editingImagingWarningText = ref('')
const editingMedicalConclusionText = ref('')
const editingMedicalWarningText = ref('')

// 计算报告状态
// 单结节系统：根据status字段判断（draft/published）
// 多结节系统：没有status字段，所有报告都视为已发布
// 如果是审核模式（review=true），强制显示审核界面
const isDraft = computed(() => {
  if (!report.value) return false
  // 审核模式：强制显示审核界面
  if (isReviewMode.value) return true
  // 单结节系统有status字段
  if (report.value._isNoduleSystem === false) {
    return report.value.status === 'draft'
  }
  // 多结节系统没有status字段，视为已发布
  return false
})
const isPublished = computed(() => {
  if (!report.value) return false
  // 审核模式：不显示已发布内容
  if (isReviewMode.value) return false
  // 单结节系统：检查status字段
  if (report.value._isNoduleSystem === false) {
    return report.value.status === 'published'
  }
  // 多结节系统：所有报告都视为已发布
  return true
})

// 是否允许“审核通过并发布”
// - 仅单结节系统（BReport）有发布流程
// - C端报告（source=c_end）不走发布流程（生成即查看）
const canPublish = computed(() => {
  if (!report.value) return false
  if (isCEndSource.value) return false
  return report.value._isNoduleSystem === false
})

// C端审核按钮：仅在审核模式 + C端来源时显示
const canApproveCEnd = computed(() => {
  if (!report.value) return false
  if (!isCEndSource.value) return false
  return isReviewMode.value
})

// 编辑功能：影像学评估结论
function startEditImagingConclusion() {
  // 从 HTML 中提取纯文本（去除标签）
  const div = document.createElement('div')
  div.innerHTML = report.value.imaging_conclusion || ''
  editingImagingConclusionText.value = div.textContent || div.innerText || ''
  editingImagingConclusion.value = true
}

function cancelEditImagingConclusion() {
  editingImagingConclusion.value = false
  editingImagingConclusionText.value = ''
}

async function saveImagingConclusion() {
  if (!editingImagingConclusionText.value.trim()) {
    alert('评估结论不能为空')
    return
  }
  
  try {
    // 单结节系统：调用更新API
    if (report.value._isNoduleSystem === false) {
      const response = await axios.put(`/api/b/reports/${reportId}`, {
        imaging_conclusion: editingImagingConclusionText.value,
        // 审核模式允许对已发布报告做勘误更新
        review_mode: isReviewMode.value
      }, { withCredentials: true })
      
      if (response.data.success) {
        report.value.imaging_conclusion = editingImagingConclusionText.value
        editingImagingConclusion.value = false
        alert('✅ 保存成功')
      }
    } else {
      // 多结节系统暂时不支持编辑
      alert('多结节系统报告编辑功能开发中')
      editingImagingConclusion.value = false
    }
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败：' + (error.response?.data?.message || error.message))
  }
}

// 编辑功能：影像学风险提示
function startEditImagingWarning() {
  const div = document.createElement('div')
  div.innerHTML = report.value.imaging_risk_warning || ''
  editingImagingWarningText.value = div.textContent || div.innerText || ''
  editingImagingWarning.value = true
}

function cancelEditImagingWarning() {
  editingImagingWarning.value = false
  editingImagingWarningText.value = ''
}

async function saveImagingWarning() {
  try {
    // 单结节系统：调用更新API
    if (report.value._isNoduleSystem === false) {
      const response = await axios.put(`/api/b/reports/${reportId}`, {
        imaging_risk_warning: editingImagingWarningText.value,
        // 审核模式允许对已发布报告做勘误更新
        review_mode: isReviewMode.value
      }, { withCredentials: true })
      
      if (response.data.success) {
        report.value.imaging_risk_warning = editingImagingWarningText.value
        editingImagingWarning.value = false
        alert('✅ 保存成功')
      }
    } else {
      // 多结节系统暂时不支持编辑
      alert('多结节系统报告编辑功能开发中')
      editingImagingWarning.value = false
    }
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败：' + (error.response?.data?.message || error.message))
  }
}

// 编辑功能：疾病史评估结论
function startEditMedicalConclusion() {
  const div = document.createElement('div')
  div.innerHTML = report.value.medical_conclusion || ''
  editingMedicalConclusionText.value = div.textContent || div.innerText || ''
  editingMedicalConclusion.value = true
}

function cancelEditMedicalConclusion() {
  editingMedicalConclusion.value = false
  editingMedicalConclusionText.value = ''
}

async function saveMedicalConclusion() {
  if (!editingMedicalConclusionText.value.trim()) {
    alert('评估结论不能为空')
    return
  }
  
  try {
    // 单结节系统：调用更新API
    if (report.value._isNoduleSystem === false) {
      const response = await axios.put(`/api/b/reports/${reportId}`, {
        medical_conclusion: editingMedicalConclusionText.value,
        // 审核模式允许对已发布报告做勘误更新
        review_mode: isReviewMode.value
      }, { withCredentials: true })
      
      if (response.data.success) {
        report.value.medical_conclusion = editingMedicalConclusionText.value
        editingMedicalConclusion.value = false
        alert('✅ 保存成功')
      }
    } else {
      // 多结节系统暂时不支持编辑
      alert('多结节系统报告编辑功能开发中')
      editingMedicalConclusion.value = false
    }
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败：' + (error.response?.data?.message || error.message))
  }
}

// 编辑功能：疾病史风险提示
function startEditMedicalWarning() {
  const div = document.createElement('div')
  div.innerHTML = report.value.medical_risk_warning || ''
  editingMedicalWarningText.value = div.textContent || div.innerText || ''
  editingMedicalWarning.value = true
}

function cancelEditMedicalWarning() {
  editingMedicalWarning.value = false
  editingMedicalWarningText.value = ''
}

async function saveMedicalWarning() {
  try {
    // 单结节系统：调用更新API
    if (report.value._isNoduleSystem === false) {
      const response = await axios.put(`/api/b/reports/${reportId}`, {
        medical_risk_warning: editingMedicalWarningText.value,
        // 审核模式允许对已发布报告做勘误更新
        review_mode: isReviewMode.value
      }, { withCredentials: true })
      
      if (response.data.success) {
        report.value.medical_risk_warning = editingMedicalWarningText.value
        editingMedicalWarning.value = false
        alert('✅ 保存成功')
      }
    } else {
      // 多结节系统暂时不支持编辑
      alert('多结节系统报告编辑功能开发中')
      editingMedicalWarning.value = false
    }
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败：' + (error.response?.data?.message || error.message))
  }
}

async function loadReport() {
  isLoading.value = true
  try {
    const source = route.query?.source || 'b_end'
    // C端报告：直接走B端统一接口（携带type=c_end），避免落到单结节/多结节系统判定
    if (source === 'c_end') {
      const resp = await axios.get(`/api/b/reports/${reportId}`, {
        params: { type: 'c_end' },
        withCredentials: true,
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      })
      if (resp.data && resp.data.success) {
        report.value = resp.data.data
        report.value._isNoduleSystem = true
        // C端报告直接使用 report_html
        reportHtml.value = report.value.report_html || ''
        return
      }
    }

    // 先尝试多结节系统，如果不存在则回退到单结节系统
    let response
    let isNoduleSystem = true
    
    try {
      // 尝试多结节系统
      response = await axios.get(`/api/nodule/reports/${reportId}`, {
        withCredentials: true,
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      })
      
      if (response.data && response.data.success) {
        isNoduleSystem = true
      } else {
        throw new Error('多结节系统未找到报告')
      }
    } catch (error) {
      // 如果多结节系统找不到，尝试单结节系统
      if (error.response?.status === 404 || error.message.includes('多结节系统未找到')) {
        console.log(`[报告加载] 多结节系统未找到报告 ${reportId}，尝试单结节系统...`)
        try {
          response = await axios.get(`/api/b/reports/${reportId}`, {
            withCredentials: true,
            headers: {
              'Cache-Control': 'no-cache',
              'Pragma': 'no-cache'
            }
          })
          
          if (response.data && response.data.success) {
            isNoduleSystem = false
            console.log(`[报告加载] ✅ 在单结节系统中找到报告 ${reportId}`)
          } else {
            throw new Error('单结节系统也未找到报告')
          }
        } catch (bError) {
          // 两个系统都找不到
          const errorMsg = bError.response?.data?.message || '报告不存在'
          alert(`报告不存在：${errorMsg}\n\n报告ID: ${reportId}\n\n提示：该报告在多结节和单结节系统中都不存在`)
          router.back()
          return
        }
      } else {
        throw error
      }
    }

    if (response.data && response.data.success) {
      report.value = response.data.data
      report.value._isNoduleSystem = isNoduleSystem // 标记报告来源
      // 加载HTML
      await loadReportHtml(isNoduleSystem)
    } else {
      const errorMsg = response.data?.message || '报告不存在'
      alert(`报告不存在：${errorMsg}\n\n报告ID: ${reportId}`)
      router.back()
    }
  } catch (error) {
    console.error('加载报告失败:', error)
    let errorMsg = error.message
    if (error.response) {
      if (error.response.data) {
        if (typeof error.response.data === 'object' && error.response.data.message) {
          errorMsg = error.response.data.message
        } else if (typeof error.response.data === 'string') {
          try {
            const json = JSON.parse(error.response.data)
            errorMsg = json.message || errorMsg
          } catch {
            errorMsg = error.response.data || errorMsg
          }
        }
      }
    }
    alert(`加载失败：${errorMsg}\n\n报告ID: ${reportId}`)
    router.back()
  } finally {
    isLoading.value = false
  }
}

async function loadReportHtml(isNoduleSystem = true) {
  try {
    // C端报告：直接用 report_html，不再请求额外接口
    if (route.query?.source === 'c_end') {
      reportHtml.value = (report.value && report.value.report_html) ? report.value.report_html : ''
      return
    }

    if (isNoduleSystem) {
      // 使用多结节系统的HTML生成API
      const response = await axios.get(`/api/nodule/reports/${reportId}/html`, {
        withCredentials: true,
        responseType: 'text'  // 直接获取HTML文本
      })

      if (typeof response.data === 'string') {
        reportHtml.value = response.data
      }
    } else {
      // 单结节系统：优先从report_html字段获取，如果没有则调用API生成
      if (report.value && report.value.report_html) {
        reportHtml.value = report.value.report_html
      } else {
        // 如果没有report_html，尝试调用API生成（已发布状态）
        if (report.value && report.value.status === 'published') {
          console.log('[报告HTML] 已发布报告没有report_html，尝试调用API生成...')
          try {
            const response = await axios.get(`/api/b/reports/${reportId}/comprehensive`, {
              withCredentials: true,
              responseType: 'text'
            })
            
            if (typeof response.data === 'string') {
              reportHtml.value = response.data
              console.log('[报告HTML] ✅ HTML生成成功')
            }
          } catch (htmlError) {
            console.error('[报告HTML] 生成HTML失败:', htmlError)
            reportHtml.value = '<p>报告HTML内容不可用，请重新生成报告</p>'
          }
        } else if (report.value && report.value.status === 'draft') {
          // 草稿状态显示提示
          reportHtml.value = `
            <div style="padding: 40px; text-align: center; background: #f5f5f5; border-radius: 8px; margin: 20px;">
              <h3 style="color: #666; margin-bottom: 20px;">📋 报告草稿</h3>
              <p style="color: #999; font-size: 14px; line-height: 1.8;">
                该报告为草稿状态，尚未生成完整报告内容。<br>
                请先审核并发布报告后，再查看完整报告内容。
              </p>
              <p style="color: #666; margin-top: 20px; font-size: 12px;">
                报告编号: ${report.value.report_code || ''}<br>
                状态: 草稿 (draft)
              </p>
            </div>
          `
        } else {
          reportHtml.value = '<p>报告HTML内容不可用，请重新生成报告</p>'
        }
      }
    }
  } catch (error) {
    console.error('加载报告HTML失败:', error)
    alert('加载完整报告失败：' + (error.response?.data?.message || error.message))
  }
}

function printReport() {
  isPrinting.value = true
  setTimeout(() => {
    window.print()
    isPrinting.value = false
  }, 100)
}

async function publishReport() {
  if (!report.value) {
    alert('报告不存在')
    return
  }

  // C端报告（source=c_end）：审核通过（status: generated -> shared）
  if (isCEndSource.value) {
    if (!confirm('确认审核通过该报告？')) return
    try {
      isPublishing.value = true
      const response = await axios.post(`/api/b/reports/${reportId}/publish`, {}, {
        params: { type: 'c_end' },
        withCredentials: true
      })
      if (response.data.success) {
        await loadReport()
        alert('✅ 已审核通过')
      }
    } catch (error) {
      console.error('审核失败:', error)
      alert('审核失败：' + (error.response?.data?.message || error.message))
    } finally {
      isPublishing.value = false
    }
    return
  }

  // 单结节系统：调用发布API
  if (report.value._isNoduleSystem === false) {
    const isDraftStatus = report.value.status === 'draft'
    // 审核模式下允许覆盖发布已发布报告
    if (!isDraftStatus && !isReviewMode.value) {
      alert('只能发布草稿状态的报告')
      return
    }

    const confirmText = isDraftStatus
      ? '确认发布该报告？发布后将无法再编辑。'
      : '确认覆盖发布该报告？将重新生成最终报告并覆盖当前已发布内容。'
    if (!confirm(confirmText)) return

    try {
      isPublishing.value = true
      const response = await axios.post(`/api/b/reports/${reportId}/publish`, {
        review_notes: '审核通过，准予发布',
        review_mode: isReviewMode.value
      }, { withCredentials: true })

      if (response.data.success) {
        // 重新加载完整报告数据（包括report_html）
        await loadReport()
        alert('✅ 报告已发布成功')
      }
    } catch (error) {
      console.error('发布失败:', error)
      alert('发布失败：' + (error.response?.data?.message || error.message))
    } finally {
      isPublishing.value = false
    }
  } else {
    // 多结节系统没有发布流程
    alert('多结节系统报告生成后即可查看，无需发布流程')
  }
}

async function exportPDF() {
  if (!report.value) {
    alert('报告不存在')
    return
  }

  try {
    console.log('📄 开始导出PDF...')
    
    // 显示加载提示（非阻塞）
    const loadingMsg = '正在生成PDF，请稍候...'
    console.log(loadingMsg)
    
    // 根据报告来源选择API
    // - C端报告（source=c_end）：走B端统一导出接口（type=c_end）
    // - 多结节系统：/api/nodule/reports/:id/pdf
    // - 单结节系统：/api/b/reports/:id/export-pdf
    const isNoduleSystem = report.value._isNoduleSystem !== false // 默认为多结节系统
    let apiPath
    let apiParams = undefined
    if (isCEndSource.value) {
      apiPath = `/api/b/reports/${reportId}/export-pdf`
      apiParams = { type: 'c_end' }
    } else if (isNoduleSystem) {
      apiPath = `/api/nodule/reports/${reportId}/pdf`
    } else {
      apiPath = `/api/b/reports/${reportId}/export-pdf`
    }
    
    // 调用PDF导出API
    const response = await axios.get(apiPath, {
      withCredentials: true,
      params: apiParams,
      responseType: 'blob'  // 接收二进制文件
    })

    // 防呆：后端如果返回JSON错误，会被当作blob下载成“1KB PDF”
    const contentType = String(response.headers?.['content-type'] || '')
    const blob = new Blob([response.data], { type: contentType || 'application/pdf' })
    if (!contentType.includes('application/pdf')) {
      const text = await blob.text()
      let msg = text
      try {
        const j = JSON.parse(text)
        msg = j?.message || j?.error || text
      } catch {}
      alert(`❌ 导出PDF失败：${msg}`)
      return
    }
    if (blob.size < 10 * 1024) {
      alert(`❌ 导出PDF失败：生成的PDF过小（${blob.size}字节），请检查后端PDF生成依赖（Playwright/Chromium）`)
      return
    }
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `健康报告_${report.value.report_code}_${new Date().toISOString().split('T')[0]}.pdf`)
    document.body.appendChild(link)
    link.click()
    
    // 清理
    link.remove()
    window.URL.revokeObjectURL(url)
    
    console.log('✅ PDF导出成功')
  } catch (error) {
    console.error('❌ 导出PDF失败:', error)
    // 提取错误消息
    let errorMsg = error.message
    if (error.response) {
      if (error.response.data && typeof error.response.data === 'object') {
        errorMsg = error.response.data.message || error.response.data.error || errorMsg
      } else if (typeof error.response.data === 'string') {
        try {
          const json = JSON.parse(error.response.data)
          errorMsg = json.message || json.error || errorMsg
        } catch {
          errorMsg = error.response.data || errorMsg
        }
      }
    }
    alert(`❌ 导出PDF失败：${errorMsg}\n\n备用方案：请使用"🖨️ 打印报告"按钮，然后选择"另存为PDF"`)
  }
}

onMounted(() => {
  loadReport()
})
</script>

<template>
  <div class="report-view-container">
    <div v-if="isLoading" class="loading">
      <div class="loading-spinner"></div>
      <p>正在加载报告...</p>
    </div>

    <template v-else-if="report">
      <!-- 操作工具栏（打印时隐藏） -->
      <div class="toolbar no-print">
        <button class="btn-back" @click="router.back()">← 返回</button>
        <div class="toolbar-actions">
          <div class="report-info">
            <span class="label">报告编号:</span>
            <span class="value">{{ report.report_code }}</span>
            <span class="label" style="margin-left: 20px;">结节类型:</span>
            <span class="value">{{ report.nodule_type || '未知' }}</span>
            <span class="label" style="margin-left: 20px;">生成时间:</span>
            <span class="value">{{ report.created_at }}</span>
          </div>

          <!-- 根据报告来源/状态/模式显示不同的操作按钮 -->
          <template v-if="canPublish && (isDraft || isReviewMode)">
            <!-- 单结节系统：草稿状态或审核模式：显示发布按钮 -->
            <button class="btn btn-primary" @click="publishReport" :disabled="isPublishing">
              {{ isPublishing ? '发布中...' : '✅ 审核通过并发布' }}
            </button>
            <button v-if="isReviewMode && !isDraft" class="btn btn-default" @click="router.push(`/reports/${reportId}`)">
              👁️ 查看报告
            </button>
          </template>
          <template v-else-if="canApproveCEnd">
            <!-- C端报告：审核通过（不走发布流程） -->
            <button class="btn btn-primary" @click="publishReport" :disabled="isPublishing">
              {{ isPublishing ? '提交中...' : '✅ 审核通过' }}
            </button>
          </template>
          <template v-else>
            <!-- C端/多结节系统：无发布流程；或单结节已发布（非审核模式） -->
            <button class="btn btn-primary" @click="exportPDF">
              📄 导出PDF
            </button>
          </template>
        </div>
      </div>

      <!-- 单结节系统：草稿状态显示审核界面 -->
      <div v-if="isDraft" class="draft-content">
        <div class="draft-notice">
          <div class="notice-icon">📝</div>
          <div class="notice-text">
            <h3>报告草稿</h3>
            <p>AI已完成健康评估，请审核后发布</p>
          </div>
        </div>

        <div class="assessment-section">
          <h2>📋 总体评估与随访建议</h2>
          <div class="assessment-item">
            <div class="item-header">
              <h3>1. 总体评估与随访建议</h3>
              <button v-if="!editingImagingConclusion" @click="startEditImagingConclusion" class="btn-edit-small">✏️ 编辑</button>
              <div v-else class="edit-actions">
                <button @click="saveImagingConclusion" class="btn-save-small">💾 保存</button>
                <button @click="cancelEditImagingConclusion" class="btn-cancel-small">❌ 取消</button>
              </div>
            </div>
            <div v-if="!editingImagingConclusion" class="content-box" v-html="report.imaging_conclusion || '暂无'"></div>
            <textarea v-else v-model="editingImagingConclusionText" class="edit-textarea-large" rows="10"></textarea>
          </div>
          <div class="assessment-item">
            <div class="item-header">
              <h3>2. 风险提示</h3>
              <button v-if="!editingImagingWarning" @click="startEditImagingWarning" class="btn-edit-small">✏️ 编辑</button>
              <div v-else class="edit-actions">
                <button @click="saveImagingWarning" class="btn-save-small">💾 保存</button>
                <button @click="cancelEditImagingWarning" class="btn-cancel-small">❌ 取消</button>
              </div>
            </div>
            <div v-if="!editingImagingWarning" class="content-box warning" v-html="report.imaging_risk_warning || '暂无'"></div>
            <textarea v-else v-model="editingImagingWarningText" class="edit-textarea-large" rows="8"></textarea>
          </div>
        </div>

        <div class="risk-summary">
          <div class="risk-item">
            <span class="label">风险等级:</span>
            <span class="risk-level" :class="report.risk_level">
              {{ report.risk_level || '未评估' }}
            </span>
            <span class="risk-level-desc" v-if="report.risk_level">
              <span v-if="report.risk_level === '低危'">（风险较低，建议定期随访）</span>
              <span v-else-if="report.risk_level === '中危'">（存在一定风险，需要密切监测）</span>
              <span v-else-if="report.risk_level === '高危'">（风险较高，建议及时就医）</span>
            </span>
          </div>
        </div>
      </div>

      <!-- 已发布状态：显示完整HTML报告 -->
      <div v-else-if="isPublished" class="report-content-wrapper">
        <div v-if="reportHtml" v-html="reportHtml" class="report-html-content"></div>
        <div v-else class="loading">
          <div class="loading-spinner"></div>
          <p>正在加载完整报告...</p>
        </div>
      </div>
    </template>

    <div v-else class="error">
      <p>❌ 报告不存在或已被删除</p>
      <button class="btn btn-primary" @click="router.back()">返回</button>
    </div>
  </div>
</template>

<style scoped>
.report-view-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

.loading {
  text-align: center;
  padding: 80px 20px;
  color: #909399;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #e4e7ed;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading p {
  font-size: 16px;
  margin: 0;
}

.error {
  text-align: center;
  padding: 80px 20px;
  color: #f56c6c;
}

.error p {
  font-size: 18px;
  margin-bottom: 24px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.btn-back {
  background: none;
  border: none;
  color: #409eff;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: #ecf5ff;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.report-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-right: 16px;
  border-right: 1px solid #dcdfe6;
}

.report-info .label {
  color: #909399;
  font-size: 13px;
}

.report-info .value {
  color: #303133;
  font-weight: 500;
  font-size: 13px;
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

.btn-default {
  background: #fff;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.btn-default:hover {
  color: #409eff;
  border-color: #409eff;
}

.btn-primary {
  background: #409eff;
  color: #fff;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-warning {
  background: #e6a23c;
  color: #fff;
  font-weight: 600;
}

.btn-warning:hover {
  background: #ebb563;
}

.btn-warning:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 状态徽章 */
.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.draft {
  background: #fff3e0;
  color: #e6a23c;
}

.status-badge.published {
  background: #e7f7e7;
  color: #67c23a;
}

/* 草稿内容 */
.draft-content {
  max-width: 1000px;
  margin: 0 auto;
}

.draft-notice {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px 32px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 32px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.notice-icon {
  font-size: 48px;
  line-height: 1;
}

.notice-text h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
}

.notice-text p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.assessment-section {
  background: #fff;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.assessment-section h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 12px;
}

.assessment-item {
  margin-bottom: 24px;
}

.assessment-item:last-child {
  margin-bottom: 0;
}

.assessment-item h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #606266;
  font-weight: 600;
}

.content-box {
  background: #f5f7fa;
  border-left: 4px solid #409eff;
  padding: 16px 20px;
  border-radius: 4px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-line;
}

.content-box.warning {
  background: #fff3e0;
  border-left-color: #e6a23c;
  color: #cf711f;
}

.risk-summary {
  background: #fff;
  border-radius: 12px;
  padding: 24px 32px;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.risk-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.item-header h3 {
  margin: 0;
}

.btn-edit-small, .btn-save-small, .btn-cancel-small {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit-small {
  background: #409eff;
  color: white;
}

.btn-edit-small:hover {
  background: #66b1ff;
}

.btn-save-small {
  background: #67c23a;
  color: white;
  margin-right: 8px;
}

.btn-save-small:hover {
  background: #85ce61;
}

.btn-cancel-small {
  background: #909399;
  color: white;
}

.btn-cancel-small:hover {
  background: #a6a9ad;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.edit-textarea-large {
  width: 100%;
  padding: 15px;
  border: 2px solid #409eff;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.8;
  font-family: inherit;
  resize: vertical;
  min-height: 200px;
}

.content-box :deep(p) {
  margin: 0.8em 0;
  line-height: 1.8;
}

.content-box :deep(p:first-child) {
  margin-top: 0;
}

.content-box :deep(p:last-child) {
  margin-bottom: 0;
}

.risk-item .label {
  color: #909399;
  font-size: 14px;
}

.risk-level {
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 600;
}

.risk-level.低危 {
  background: #e7f7e7;
  color: #67c23a;
}

.risk-level.中危 {
  background: #fff3e0;
  color: #e6a23c;
}

.risk-level.高危 {
  background: #fef0f0;
  color: #f56c6c;
}

.risk-level-desc {
  margin-left: 12px;
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.risk-score {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}

/* 报告内容容器 */
.report-content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

/* 报告HTML内容样式 */
.report-html-content {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* 确保报告内部的样式正常显示 */
.report-html-content >>> * {
  max-width: 100%;
}

.report-html-content >>> img {
  max-width: 100%;
  height: auto;
}

/* 打印样式 */
@media print {
  .no-print {
    display: none !important;
  }

  .report-view-container {
    background: #fff;
    padding: 0;
  }

  .report-content-wrapper {
    max-width: 100%;
  }

  .report-html-content {
    box-shadow: none;
    border-radius: 0;
  }

  /* 草稿内容打印样式 */
  .draft-content {
    max-width: 100%;
  }

  .draft-notice {
    background: #f0f0f0 !important;
    color: #333 !important;
    box-shadow: none;
  }

  .assessment-section {
    box-shadow: none;
    border: 1px solid #ddd;
    page-break-inside: avoid;
  }

  .risk-summary {
    box-shadow: none;
    border: 1px solid #ddd;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .report-view-container {
    padding: 12px;
  }
  
  .toolbar {
    flex-direction: column;
    gap: 16px;
  }
  
  .toolbar-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }
  
  .report-info {
    border-right: none;
    border-bottom: 1px solid #dcdfe6;
    padding-bottom: 12px;
    padding-right: 0;
    flex-wrap: wrap;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
