<template>
  <div class="page">
    <div class="page-head">
      <div class="page-title">患者建档</div>
      <div class="crumb">首页 / <b>患者建档</b></div>
    </div>

    <div class="layout">
      <!-- 左侧主表单 -->
      <div class="form-col">

        <!-- 建档方式 -->
        <section class="card section-card">
          <div class="section-title">建档方式</div>
          <div class="method-grid">
            <div v-for="m in methods" :key="m.id"
              class="method-card" :class="{ selected: form.method === m.id }"
              @click="form.method = m.id">
              <div class="method-check" v-if="form.method === m.id">✓</div>
              <div class="method-icon" v-html="m.icon"></div>
              <div class="method-name">{{ m.name }}</div>
              <div class="method-desc">{{ m.desc }}</div>
            </div>
          </div>
        </section>

        <!-- 一、患者基础信息 -->
        <section class="card section-card">
          <div class="section-title">一、患者基础信息</div>
          <div class="form-grid">
            <label class="fi required">姓名
              <input v-model="form.name" placeholder="请输入姓名">
            </label>
            <label class="fi required">性别
              <select v-model="form.gender">
                <option>男</option>
                <option>女</option>
              </select>
            </label>
            <label class="fi required">年龄
              <div class="input-unit">
                <input v-model="form.age" type="number" placeholder="请输入年龄">
                <span class="unit">岁</span>
              </div>
            </label>
            <label class="fi required">手机号
              <input v-model="form.phone" placeholder="请输入手机号">
            </label>
            <label class="fi required">身份证号
              <input v-model="form.idCard" placeholder="请输入身份证号">
            </label>
            <label class="fi required">联系地址
              <input v-model="form.address" placeholder="请输入联系地址">
            </label>
            <label class="fi required">紧急联系人
              <input v-model="form.emergency" placeholder="姓名（关系）">
            </label>
            <label class="fi">备注
              <div class="textarea-wrap">
                <textarea v-model="form.remark" placeholder="请输入备注信息" maxlength="100" rows="2"></textarea>
                <span class="char-count">{{ form.remark.length }}/100</span>
              </div>
            </label>
          </div>
        </section>

        <!-- 二、患者来源 -->
        <section class="card section-card">
          <div class="section-title">二、患者来源</div>
          <div class="form-grid">
            <label class="fi required">就诊类型
              <select v-model="form.visitType">
                <option>门诊</option>
                <option>住院</option>
                <option>体检</option>
              </select>
            </label>
            <label class="fi required">来源科室
              <select v-model="form.dept">
                <option>呼吸内科</option>
                <option>乳腺外科</option>
                <option>甲状腺外科</option>
                <option>体检中心</option>
              </select>
            </label>
            <label class="fi required">就诊医生
              <input v-model="form.doctor" placeholder="请输入就诊医生">
            </label>
            <label class="fi required">检查日期
              <input v-model="form.examDate" type="date">
            </label>
            <label class="fi">导入批次号（选填·体检中心）
              <input v-model="form.batchNo" placeholder="请输入导入批次号">
            </label>
          </div>
        </section>

        <!-- 三、结节信息 -->
        <section class="card section-card">
          <div class="section-title">三、结节信息</div>
          <div class="form-row">
            <div class="fi required" style="flex:1">
              <span class="fi-label">结节类型（可多选）</span>
              <div class="tag-group">
                <button v-for="t in noduleTypeOptions" :key="t.value"
                  class="tag-btn" :class="{ active: form.noduleTypes.includes(t.value) }"
                  type="button" @click="toggleNodule(t.value)">
                  {{ t.label }}
                  <span v-if="form.noduleTypes.includes(t.value)" class="tag-x" @click.stop="toggleNodule(t.value)">×</span>
                </button>
              </div>
            </div>
          </div>
          <div class="form-grid" style="margin-top:12px">
            <label class="fi required">追踪结节等级
              <select v-model="form.riskLevel">
                <option>高风险</option>
                <option>中风险</option>
                <option>低风险</option>
              </select>
            </label>
            <label class="fi required">结节部位
              <select v-model="form.location">
                <option>右上肺</option>
                <option>左上肺</option>
                <option>右下肺</option>
                <option>左下肺</option>
                <option>甲状腺左叶</option>
                <option>甲状腺右叶</option>
                <option>左乳</option>
                <option>右乳</option>
              </select>
            </label>
            <label class="fi required">最大直径
              <div class="input-unit">
                <input v-model="form.diameter" type="number" placeholder="请输入">
                <span class="unit">mm</span>
              </div>
            </label>
            <label class="fi required">影像特征
              <select v-model="form.imageFeature">
                <option>被膜状结节</option>
                <option>磨玻璃结节</option>
                <option>实性结节</option>
                <option>囊实性结节</option>
                <option>钙化结节</option>
              </select>
            </label>
            <label class="fi required">初步建议
              <select v-model="form.suggestion">
                <option>建议3个月复查</option>
                <option>建议6个月复查</option>
                <option>建议12个月复查</option>
                <option>建议立即就诊</option>
              </select>
            </label>
            <div class="fi">
              <span class="fi-label required-label">是否需要医生复核</span>
              <div class="toggle-row">
                <button class="toggle" :class="{ on: form.needReview }" type="button"
                  @click="form.needReview = !form.needReview">
                  <span class="toggle-thumb"></span>
                </button>
                <span class="toggle-text">{{ form.needReview ? '是' : '否' }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- 四、报告资料 -->
        <section class="card section-card">
          <div class="section-title">四、报告资料</div>
          <div class="upload-grid">
            <div class="upload-block">
              <div class="fi-label required-label">上传检查报告</div>
              <label class="fi" style="margin-top:6px">报告类型
                <select v-model="form.reportType">
                  <option>胸部CT</option>
                  <option>乳腺超声</option>
                  <option>甲状腺超声</option>
                </select>
              </label>
              <div v-if="form.reportFile" class="file-item">
                <span class="file-icon pdf">PDF</span>
                <div class="file-info">
                  <div class="file-name">{{ form.reportFile.name }}</div>
                  <div class="file-size">{{ formatSize(form.reportFile.size) }}</div>
                </div>
                <span class="file-ok">✓</span>
                <button class="file-rm" type="button" @click="form.reportFile = null">×</button>
              </div>
              <label v-else class="upload-area" for="report-upload">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#94a3b8" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                <span>拖拽/点击上传检查报告</span>
                <input id="report-upload" type="file" accept=".pdf,.jpg,.png" style="display:none" @change="onReportFile">
              </label>
            </div>

            <div class="upload-block">
              <div class="fi-label required-label">上传影像资料（DICOM影像文件）</div>
              <div v-if="form.imageFile" class="file-item" style="margin-top:6px">
                <span class="file-icon dcm">DCM</span>
                <div class="file-info">
                  <div class="file-name">{{ form.imageFile.name }}</div>
                  <div class="file-size">{{ formatSize(form.imageFile.size) }}</div>
                </div>
                <span class="file-ok">✓</span>
                <button class="file-rm" type="button" @click="form.imageFile = null">×</button>
              </div>
              <label v-else class="upload-area" for="image-upload" style="margin-top:6px">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#94a3b8" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                <span>拖拽/点击上传影像资料</span>
                <input id="image-upload" type="file" accept=".zip,.dcm" style="display:none" @change="onImageFile">
              </label>
            </div>

            <div class="upload-block">
              <div class="fi-label">预约上传</div>
              <label class="upload-area" for="reserve-upload" style="margin-top:6px">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#94a3b8" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                <span>拖拽/点击上传影像或报告</span>
                <input id="reserve-upload" type="file" style="display:none">
              </label>
            </div>
          </div>
        </section>

        <!-- 五、负责人设置 -->
        <section class="card section-card">
          <div class="section-title">五、负责人设置</div>
          <div class="form-grid">
            <label class="fi required">负责医生
              <select v-model="form.ownerDoctor">
                <option>张医生（呼吸内科）</option>
                <option>李医生（乳腺外科）</option>
                <option>王医生（甲状腺外科）</option>
              </select>
            </label>
            <label class="fi required">健康管理师
              <select v-model="form.ownerManager">
                <option>李慧（健康管理师）</option>
                <option>王芳（健康管理师）</option>
              </select>
            </label>
            <label class="fi required">随访护士
              <select v-model="form.ownerNurse">
                <option>刘洋（随访护士）</option>
                <option>陈静（随访护士）</option>
              </select>
            </label>
            <label class="fi required">所属科室
              <select v-model="form.ownerDept">
                <option>呼吸内科</option>
                <option>乳腺外科</option>
                <option>甲状腺外科</option>
              </select>
            </label>
          </div>
        </section>

        <!-- 底部操作 -->
        <div class="action-bar">
          <button class="primary" type="button" @click="save('save')">保存档案</button>
          <button class="btn" type="button" @click="save('upload')">保存并上传报告</button>
          <button class="btn" type="button" @click="save('survey')">保存并发送问卷</button>
          <button class="btn" type="button" @click="save('report')">保存并进入报告处理</button>
          <button class="ghost-btn" type="button" @click="cancel">取消</button>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="right-col">
        <!-- 建档后流程 -->
        <section class="card side-card">
          <div class="side-title">建档后流程</div>
          <div class="flow-steps">
            <div v-for="(step, i) in flowSteps" :key="i" class="flow-step">
              <div class="step-icon" v-html="step.icon"></div>
              <div class="step-label">{{ step.label }}</div>
              <div class="step-num">{{ i + 1 }}</div>
              <div v-if="i < flowSteps.length - 1" class="step-arrow">→</div>
            </div>
          </div>
          <div class="flow-desc">闭环管理，确保每位患者得到及时、规范的随访服务</div>
        </section>

        <!-- 档案预览 -->
        <section class="card side-card">
          <div class="side-title">档案预览</div>
          <div class="preview-grid">
            <div class="pv-row"><span class="pv-k">患者姓名</span><span class="pv-v">{{ form.name || '—' }}</span></div>
            <div class="pv-row"><span class="pv-k">来源</span><span class="pv-v">{{ previewSource }}</span></div>
            <div class="pv-row">
              <span class="pv-k">结节类型</span>
              <span class="pv-v">
                <span v-if="form.noduleTypes.length" class="tag-preview">{{ nodulePreviewLabel }}</span>
                <span v-else>—</span>
              </span>
            </div>
            <div class="pv-row">
              <span class="pv-k">风险等级</span>
              <span class="pv-v">
                <span v-if="form.riskLevel" class="risk-tag" :class="riskTagClass">{{ form.riskLevel }}</span>
                <span v-else>—</span>
              </span>
            </div>
            <div class="pv-row"><span class="pv-k">负责人</span><span class="pv-v">{{ previewOwner }}</span></div>
            <div class="pv-row"><span class="pv-k">下一步动作</span><span class="pv-v">{{ nextAction }}</span></div>
          </div>
          <div class="preview-warn">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#f59e0b" stroke-width="2"><path d="M12 9v4M12 17h.01"/><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/></svg>
            患者信息经工作人员录入并管理，请确保信息真实准确。
          </div>
        </section>
      </div>
    </div>
  </div>
  <ToastMsg ref="toast" />
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import ToastMsg from '../components/ToastMsg.vue'

const router = useRouter()
const toast = ref(null)

const form = ref({
  method: 'manual',
  name: '李*明',
  gender: '男',
  age: 56,
  phone: '138****5678',
  idCard: '370**********1234',
  address: '山东省济南市历下区经十路123号',
  emergency: '王**（配偶）138****1234',
  remark: '既往吸烟史20年，已戒烟5年。',
  visitType: '门诊',
  dept: '呼吸内科',
  doctor: '张医生',
  examDate: '2026-04-20',
  batchNo: '',
  noduleTypes: ['lung'],
  riskLevel: '高风险',
  location: '右上肺',
  diameter: 8,
  imageFeature: '被膜状结节',
  suggestion: '建议3个月复查',
  needReview: true,
  reportType: '胸部CT',
  reportFile: null,
  imageFile: null,
  ownerDoctor: '张医生（呼吸内科）',
  ownerManager: '李慧（健康管理师）',
  ownerNurse: '刘洋（随访护士）',
  ownerDept: '呼吸内科'
})

const methods = [
  {
    id: 'manual', name: '1. 手动建档',
    desc: '手动录入患者信息\n适定随访建档',
    icon: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#155eef" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/><path d="M12 14v4M10 16h4"/></svg>'
  },
  {
    id: 'outpatient', name: '2. 门诊导入',
    desc: '从HIS门诊信息中\n选择患者导入',
    icon: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#64748b" stroke-width="2"><path d="M6 2h9l3 3v17H6z"/><path d="M9 12h6M9 16h6M9 8h3"/></svg>'
  },
  {
    id: 'physical', name: '3. 体检中心导入',
    desc: '从体检体检信息中\n选择患者导入',
    icon: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#64748b" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 12h6M12 9v6"/></svg>'
  },
  {
    id: 'batch', name: '4. 批量导入',
    desc: '通过模板批量导入\n多名患者信息',
    icon: '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#64748b" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>'
  }
]

const noduleTypeOptions = [
  { value: 'solid', label: '实性结节' },
  { value: 'thyroid', label: '甲状腺结节' },
  { value: 'lung', label: '肺部结节' },
  { value: 'lung_breast', label: '肺部合并乳腺结节' },
  { value: 'lung_thyroid', label: '肺部合并甲状腺结节' },
  { value: 'thyroid_breast', label: '甲状腺合并乳腺结节' },
  { value: 'triple', label: '三合并结节' }
]

const flowSteps = [
  { label: '建档', icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>' },
  { label: '上传报告', icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>' },
  { label: 'AI解析', icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>' },
  { label: '生成健康管理策略', icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 2h9l3 3v17H6z"/><path d="M9 12h6M9 16h6"/></svg>' },
  { label: '医生复核', icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4"/><path d="M4 4h16v16H4z"/></svg>' },
  { label: '推送患者', icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"/></svg>' },
  { label: '生成随访任务', icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/></svg>' }
]

function toggleNodule(val) {
  const idx = form.value.noduleTypes.indexOf(val)
  if (idx >= 0) form.value.noduleTypes.splice(idx, 1)
  else form.value.noduleTypes.push(val)
}

function onReportFile(e) {
  form.value.reportFile = e.target.files[0] || null
}

function onImageFile(e) {
  form.value.imageFile = e.target.files[0] || null
}

function formatSize(bytes) {
  if (!bytes) return ''
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

const previewSource = computed(() => {
  const d = form.value.dept || ''
  const doc = form.value.doctor || ''
  if (!d && !doc) return '—'
  return `${form.value.visitType}（${d}·${doc}）`
})

const nodulePreviewLabel = computed(() => {
  const map = Object.fromEntries(noduleTypeOptions.map(t => [t.value, t.label]))
  return form.value.noduleTypes.map(v => map[v] || v).join('、')
})

const riskTagClass = computed(() => {
  if (form.value.riskLevel === '高风险') return 'risk-high'
  if (form.value.riskLevel === '中风险') return 'risk-mid'
  return 'risk-low'
})

const previewOwner = computed(() => {
  const parts = [form.value.ownerDoctor, form.value.ownerManager, form.value.ownerNurse]
    .filter(Boolean).map(s => s.split('（')[0])
  return parts.join(' / ') || '—'
})

const nextAction = computed(() => {
  if (form.value.reportFile) return '上传报告并进入报告处理'
  return '保存档案'
})

function save(type) {
  const msgs = {
    save: '档案已保存',
    upload: '档案已保存，请上传报告',
    survey: '档案已保存，问卷已发送',
    report: '档案已保存，正在进入报告处理...'
  }
  toast.value?.show(msgs[type] || '已保存')
  if (type === 'report') {
    setTimeout(() => router.push('/report'), 1200)
  }
}

function cancel() {
  router.back()
}
</script>

<style scoped>
.page{min-height:100%}
.page-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.page-title{font-size:20px;font-weight:950;color:#0f172a}
.crumb{color:#64748b;font-weight:700}

.layout{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:14px;align-items:start}
.form-col{display:flex;flex-direction:column;gap:12px}
.right-col{display:flex;flex-direction:column;gap:12px;position:sticky;top:0}

.card{background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 6px 18px rgba(15,23,42,.04)}
.section-card{padding:16px 18px}
.section-title{font-size:14px;font-weight:950;color:#0f172a;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #eef2f7}

/* 建档方式 */
.method-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.method-card{position:relative;border:2px solid #e6edf7;border-radius:10px;padding:14px 12px;cursor:pointer;text-align:center;transition:border-color .15s}
.method-card:hover{border-color:#93c5fd}
.method-card.selected{border-color:#155eef;background:#f0f6ff}
.method-check{position:absolute;top:8px;right:8px;width:18px;height:18px;border-radius:50%;background:#155eef;color:#fff;font-size:11px;display:grid;place-items:center;font-weight:900}
.method-icon{display:flex;justify-content:center;margin-bottom:8px}
.method-name{font-weight:900;font-size:13px;color:#0f172a;margin-bottom:4px}
.method-desc{font-size:11px;color:#64748b;white-space:pre-line;line-height:1.5}

/* 表单 */
.form-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px 16px}
.form-row{display:flex;gap:16px}
.fi{display:flex;flex-direction:column;gap:6px;color:#475569;font-weight:750;font-size:13px}
.fi-label{color:#475569;font-weight:750;font-size:13px}
.fi input,.fi select{height:34px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none;font-size:13px}
.fi input:focus,.fi select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.fi.required > *:first-child::before,.required-label::before{content:'* ';color:#ef4444}
.input-unit{display:flex;align-items:center;border:1px solid #d9e2ef;border-radius:8px;overflow:hidden;background:#fff}
.input-unit input{border:none;flex:1;height:34px;padding:0 10px;outline:none;font-size:13px}
.input-unit:focus-within{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.unit{padding:0 10px;color:#64748b;font-size:13px;background:#f8fafc;border-left:1px solid #e6edf7;height:34px;display:flex;align-items:center}
.textarea-wrap{position:relative}
.textarea-wrap textarea{width:100%;border:1px solid #d9e2ef;border-radius:8px;padding:8px 10px;resize:none;font-size:13px;color:#111827;outline:none;box-sizing:border-box}
.textarea-wrap textarea:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.char-count{position:absolute;bottom:6px;right:8px;font-size:11px;color:#94a3b8}

/* 结节类型标签 */
.tag-group{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}
.tag-btn{border:1px solid #d9e2ef;border-radius:20px;padding:5px 14px;background:#fff;color:#475569;font-size:13px;cursor:pointer;display:flex;align-items:center;gap:4px;transition:all .15s}
.tag-btn:hover{border-color:#93c5fd;color:#155eef}
.tag-btn.active{background:#155eef;border-color:#155eef;color:#fff}
.tag-x{font-size:14px;line-height:1;margin-left:2px}

/* 开关 */
.toggle-row{display:flex;align-items:center;gap:8px;margin-top:4px}
.toggle{width:40px;height:22px;border-radius:11px;border:none;background:#cbd5e1;cursor:pointer;position:relative;transition:background .2s;padding:0}
.toggle.on{background:#155eef}
.toggle-thumb{position:absolute;top:3px;left:3px;width:16px;height:16px;border-radius:50%;background:#fff;transition:left .2s;display:block}
.toggle.on .toggle-thumb{left:21px}
.toggle-text{font-size:13px;color:#334155;font-weight:750}

/* 上传 */
.upload-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.upload-block{display:flex;flex-direction:column}
.upload-area{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;border:1.5px dashed #d9e2ef;border-radius:8px;padding:18px 10px;cursor:pointer;color:#94a3b8;font-size:12px;text-align:center;transition:border-color .15s;min-height:80px}
.upload-area:hover{border-color:#93c5fd;color:#155eef}
.file-item{display:flex;align-items:center;gap:8px;border:1px solid #e6edf7;border-radius:8px;padding:8px 10px;margin-top:6px}
.file-icon{width:32px;height:32px;border-radius:6px;display:grid;place-items:center;font-size:10px;font-weight:900;color:#fff;flex-shrink:0}
.file-icon.pdf{background:#ef4444}
.file-icon.dcm{background:#6366f1}
.file-info{flex:1;min-width:0}
.file-name{font-size:12px;font-weight:750;color:#0f172a;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.file-size{font-size:11px;color:#94a3b8}
.file-ok{color:#22c55e;font-size:16px}
.file-rm{border:none;background:none;color:#94a3b8;cursor:pointer;font-size:16px;padding:0}

/* 底部操作 */
.action-bar{display:flex;gap:10px;flex-wrap:wrap;padding:14px 0 4px}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:8px;padding:9px 18px;cursor:pointer;font-weight:750;font-size:14px}
.btn{border:1px solid #d9e2ef;border-radius:8px;background:#fff;color:#475569;padding:9px 14px;cursor:pointer;font-weight:750;font-size:14px}
.ghost-btn{border:1px solid #d9e2ef;border-radius:8px;background:#fff;color:#64748b;padding:9px 14px;cursor:pointer;font-size:14px}

/* 右侧面板 */
.side-card{padding:14px 16px}
.side-title{font-size:13px;font-weight:950;color:#0f172a;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #eef2f7}
.flow-steps{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:10px}
.flow-step{display:flex;flex-direction:column;align-items:center;gap:4px;position:relative}
.step-icon{width:36px;height:36px;border-radius:10px;background:#eef5ff;border:1px solid #cfe0ff;display:grid;place-items:center;color:#155eef}
.step-label{font-size:10px;color:#475569;font-weight:750;text-align:center;max-width:50px;line-height:1.3}
.step-num{font-size:10px;color:#94a3b8}
.step-arrow{font-size:14px;color:#94a3b8;align-self:flex-start;margin-top:8px;margin-left:2px;margin-right:2px}
.flow-desc{font-size:11px;color:#64748b;line-height:1.6;border-top:1px solid #eef2f7;padding-top:8px;margin-top:4px}

/* 档案预览 */
.preview-grid{display:flex;flex-direction:column;gap:8px;margin-bottom:10px}
.pv-row{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;font-size:13px}
.pv-k{color:#94a3b8;flex-shrink:0}
.pv-v{color:#0f172a;font-weight:750;text-align:right}
.tag-preview{background:#dbeafe;color:#1d4ed8;border-radius:4px;padding:2px 8px;font-size:12px}
.risk-tag{border-radius:4px;padding:2px 8px;font-size:12px;font-weight:750}
.risk-high{background:#fee2e2;color:#dc2626}
.risk-mid{background:#ffedd5;color:#ea580c}
.risk-low{background:#dcfce7;color:#16a34a}
.preview-warn{display:flex;align-items:flex-start;gap:6px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:8px 10px;font-size:12px;color:#92400e;line-height:1.5}
</style>
