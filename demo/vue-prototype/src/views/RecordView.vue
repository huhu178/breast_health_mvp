<template>
  <div class="record-page">
    <div class="record-card">
      <div class="record-card-head">
        <div class="record-page-title">患者建档</div>
        <div class="record-page-sub">填写患者基础信息与结节数据，完成后可生成健康档案</div>
      </div>
      <div class="record-layout">
      <div class="record-form">

        <!-- 1. 患者基础信息 -->
        <section class="form-sec">
          <div class="sec-h"><span class="no">一</span>患者基础信息</div>
          <div class="grid-12">
            <!-- 第1行：姓名、性别、出生日期/年龄、手机号 -->
            <div class="field col-3 required">
              <div class="label">姓名</div>
              <input v-model="form.name" placeholder="请输入姓名">
            </div>
            <div class="field col-2 required">
              <div class="label">性别</div>
              <select v-model="form.gender">
                <option>男</option><option>女</option>
              </select>
            </div>
            <div class="field col-3 required">
              <div class="label">出生日期</div>
              <input v-model="form.birthDate" type="date">
            </div>
            <div class="field col-1">
              <div class="label">年龄</div>
              <input v-model="form.age" type="number" min="0" placeholder="—">
            </div>
            <div class="field col-3 required phone">
              <div class="label">手机号</div>
              <input v-model="form.phone" placeholder="请输入手机号">
            </div>

            <!-- 第1.5行：身高、体重、糖尿病史 -->
            <div class="field col-2">
              <div class="label">身高（cm）</div>
              <input v-model="form.height" type="number" min="80" max="250" placeholder="例如：165">
            </div>
            <div class="field col-2">
              <div class="label">体重（kg）</div>
              <input v-model="form.weight" type="number" min="20" max="300" placeholder="例如：60">
            </div>
            <div class="field col-2">
              <div class="label">糖尿病史</div>
              <select v-model="form.diabetesHistory">
                <option>无</option>
                <option>有</option>
              </select>
            </div>

            <!-- 第2行：身份证号、联系地址、紧急联系人关系 -->
            <div class="field col-4 idno">
              <div class="label">身份证号</div>
              <input v-model="form.idNo" placeholder="请输入身份证号">
            </div>
            <div class="field col-5 addr">
              <div class="label">联系地址</div>
              <input v-model="form.addr" placeholder="省/市/区/详细地址">
            </div>
            <div class="field col-3">
              <div class="label">紧急联系人关系</div>
              <select v-model="form.emergency">
                <option>配偶</option><option>子女</option><option>父母</option><option>其他</option>
              </select>
            </div>

            <!-- 第3行：紧急联系人姓名、紧急联系人电话、备注 -->
            <div class="field col-3">
              <div class="label">紧急联系人姓名</div>
              <input v-model="form.emergencyName" placeholder="请输入姓名">
            </div>
            <div class="field col-3 phone">
              <div class="label">紧急联系人电话</div>
              <input v-model="form.emergencyPhone" placeholder="请输入电话">
            </div>
            <div class="field col-6 note">
              <div class="label">备注</div>
              <input v-model="form.note" placeholder="简短备注（不超过一行）">
            </div>

            <!-- 第4行：身高、体重、糖尿病史 -->
            <div class="field col-2">
              <div class="label">身高（cm）</div>
              <input v-model="form.height" type="number" placeholder="例如：165">
            </div>
            <div class="field col-2">
              <div class="label">体重（kg）</div>
              <input v-model="form.weight" type="number" placeholder="例如：60">
            </div>
            <div class="field col-2">
              <div class="label">糖尿病史</div>
              <select v-model="form.diabetes_history">
                <option>无</option><option>有</option>
              </select>
            </div>
          </div>
        </section>

        <!-- 2. 患者来源 -->
        <section class="form-sec">
          <div class="sec-h"><span class="no">二</span>患者来源</div>
          <div class="grid-12">
            <div class="field col-2 required">
              <div class="label">来源类型</div>
              <select v-model="form.source">
                <option>门诊</option>
                <option>体检中心</option>
              </select>
            </div>
            <div class="field col-2 required">
              <div class="label">负责人</div>
              <select v-model="form.doctor">
                <option>李医生</option>
                <option>王医生</option>
                <option>张医生</option>
                <option>赵医生</option>
              </select>
            </div>
            <div class="field col-3 required">
              <div class="label">检查日期</div>
              <input v-model="form.examDate" type="date">
            </div>
          </div>
        </section>

        <!-- 3. 结节信息 -->
        <section class="form-sec">
          <div class="sec-h"><span class="no">三</span>结节信息</div>
          <div class="field-row">
            <div class="field-label"><span class="req">结节类型（可多选）</span></div>
            <div class="tag-row">
              <button
                v-for="t in organTags"
                :key="t"
                type="button"
                class="tag-btn"
                :class="{ active: selectedTag === t }"
                @click="toggleOrganType(t)"
              >
                {{ t }}
              </button>

              <span class="tag-divider" aria-hidden="true"></span>

              <button
                v-for="p in presetTags"
                :key="p.id"
                type="button"
                class="tag-btn preset"
                :class="{ active: selectedTag === p.id }"
                @click="applyPreset(p.id)"
              >
                {{ p.label }}
              </button>
            </div>
          </div>


          <div v-if="visibleNodules.includes('肺部结节')" class="nodule-mini">
            <div class="nodule-mini-title">肺部结节</div>
            <div class="form-grid cols3">
              <div class="form-field required">
                <div class="label">结节发现时间</div>
                <input v-model="form.lung_discovery_date" type="date">
              </div>
              <div class="form-field required">
                <div class="label">Lung-RADS分级</div>
                <select v-model="form.lung_rads_level">
                  <option>不清楚</option>
                  <option>1</option><option>2</option><option>3</option>
                  <option>4A</option><option>4B</option><option>4X</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">数量</div>
                <select v-model="form.lung_nodule_quantity">
                  <option value="">—</option>
                  <option>单发</option>
                  <option>多发</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">结节大小</div>
                <div class="input-unit">
                  <input v-model="form.lung_nodule_size" placeholder="例如：12.5">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div v-if="String(form.lung_nodule_quantity||'').includes('多发')" class="form-field">
                <div class="label">多发结节个数</div>
                <input v-model="form.lung_nodule_count" type="number" min="1" placeholder="例如：3">
              </div>

              <div class="form-field full">
                <div class="label">肺部症状（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无症状','咳嗽','咳痰','胸痛','气短','咯血','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.lung_symptoms||[]).includes(s) }"
                    @click="toggleArr(form.lung_symptoms, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.lung_symptoms||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.lung_symptoms_other" placeholder="请输入其他症状">
                </div>
              </div>
            </div>
          </div>

          <div v-if="visibleNodules.includes('甲状腺结节')" class="nodule-mini">
            <div class="nodule-mini-title">甲状腺结节</div>
            <div class="form-grid cols3">
              <div class="form-field">
                <div class="label">结节发现时间</div>
                <input v-model="form.thyroid_discovery_date" type="date">
              </div>
              <div class="form-field required">
                <div class="label">TI-RADS分级</div>
                <select v-model="form.tirads_level">
                  <option>不清楚</option>
                  <option>1</option><option>2</option><option>3</option>
                  <option>4A</option><option>4B</option><option>4C</option>
                  <option>5</option><option>6</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">数量</div>
                <select v-model="form.thyroid_nodule_quantity">
                  <option value="">—</option>
                  <option>单发</option>
                  <option>多发</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">结节大小</div>
                <div class="input-unit">
                  <input v-model="form.thyroid_nodule_size" placeholder="例如：12.5">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div v-if="String(form.thyroid_nodule_quantity||'').includes('多发')" class="form-field">
                <div class="label">多发结节个数</div>
                <input v-model="form.thyroid_nodule_count" type="number" min="1" placeholder="例如：3">
              </div>

              <div class="form-field full">
                <div class="label">结节症状（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无症状','颈部肿块','压迫症状','疼痛症状','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.thyroid_symptoms||[]).includes(s) }"
                    @click="toggleArr(form.thyroid_symptoms, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.thyroid_symptoms||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.thyroid_symptoms_other" placeholder="请输入其他症状">
                </div>
              </div>
            </div>
          </div>

          <div v-if="visibleNodules.includes('乳腺结节')" class="nodule-mini">
            <div class="nodule-mini-title">乳腺结节</div>
            <div class="form-grid cols3">
              <div class="form-field required">
                <div class="label">结节发现时间</div>
                <input v-model="form.breast_discovery_date" type="date">
              </div>
              <div class="form-field required">
                <div class="label">BI-RADS分级</div>
                <select v-model="form.birads_level">
                  <option>不清楚</option>
                  <option>1</option><option>2</option><option>3</option>
                  <option>4A</option><option>4B</option><option>4C</option>
                  <option>5</option><option>6</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">数量</div>
                <select v-model="form.nodule_quantity">
                  <option>单发</option>
                  <option>多发</option>
                </select>
              </div>
              <div class="form-field">
                <div class="label">结节大小</div>
                <div class="input-unit">
                  <input v-model="form.nodule_size" placeholder="例如：12.5">
                  <span class="unit">mm</span>
                </div>
              </div>
              <div v-if="String(form.nodule_quantity||'').includes('多发')" class="form-field">
                <div class="label">多发结节个数</div>
                <input v-model="form.nodule_count" type="number" min="1" placeholder="例如：3">
              </div>

              <div class="form-field full">
                <div class="label">结节症状（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无症状','乳房肿块','乳房疼痛','乳房胀满感','乳头溢液','乳房皮肤改变','腋下淋巴结肿大','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.symptoms||[]).includes(s) }"
                    @click="toggleArr(form.symptoms, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.symptoms||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.symptoms_other" placeholder="请输入其他症状">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">基础疾病史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','乳腺增生病史','乳腺纤维瘤病史','乳腺囊肿病史','乳腺炎病史','乳腺癌病史','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.history||[]).includes(s) }"
                    @click="toggleArr(form.history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.breast_disease_history_other" placeholder="请输入其他基础疾病史">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">家族史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','一级亲属（父母、子女、亲兄弟姐妹）','二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）','三级亲属（表/堂兄妹）','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.family_history||[]).includes(s) }"
                    @click="toggleArr(form.family_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.family_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.family_history_other" placeholder="请输入其他家族史">
                </div>
              </div>

              <div class="form-field full">
                <div class="label">药物使用史（多选）</div>
                <div class="tag-row">
                  <button
                    v-for="s in ['无','中成药治疗','激素调节药物','维生素辅助治疗','乳腺癌治疗药物','其他']"
                    :key="s"
                    type="button"
                    class="tag-btn"
                    :class="{ active: (form.medication_history||[]).includes(s) }"
                    @click="toggleArr(form.medication_history, s)"
                  >{{ s }}</button>
                </div>
                <div v-if="(form.medication_history||[]).includes('其他')" style="margin-top:8px">
                  <input v-model="form.medication_other" placeholder="请输入其他药物使用史">
                </div>
              </div>
            </div>
          </div>

          <!-- 综合风险 + 是否复核（公共，始终显示） -->
          <div class="grid-12" style="margin-top:10px">
            <div class="field col-2 required">
              <div class="label">综合风险等级</div>
              <select v-model="form.risk">
                <option>高风险</option><option>中风险</option><option>低风险</option>
              </select>
            </div>
            <div class="field col-2 required">
              <div class="label">是否医生复核</div>
              <div class="toggle-row">
                <span class="toggle" :class="{ on: form.needReview }" @click="form.needReview = !form.needReview"></span>
                <span class="muted" style="font-weight:800">{{ form.needReview ? '是' : '否' }}</span>
              </div>
            </div>
            <div class="field col-3 required">
              <div class="label">负责医生</div>
              <div class="cur-doctor">{{ user }}</div>
            </div>
            <div class="field col-5" style="display:flex;align-items:flex-end;gap:8px">
              <button class="mini-action" type="button" @click="save" :disabled="saving">{{ saving ? '保存中...' : '保存档案' }}</button>
              <button class="mini-action primary-action" type="button" @click="generateReport" :disabled="generating">{{ generating ? 'AI生成中...' : '生成健康档案' }}</button>
            </div>
          </div>
        </section>
      </div>

      <aside class="record-side">
        <section class="side-card">
          <div class="side-title">建档后流程</div>
          <div class="flow-steps">
            <div class="flow-step done"><span class="dot">1</span><span>建档</span></div>
            <div class="flow-step"><span class="dot">2</span><span>AI解析</span></div>
            <div class="flow-step"><span class="dot">3</span><span>生成健康档案</span></div>
            <div class="flow-step"><span class="dot">4</span><span>审核健康档案</span></div>
            <div class="flow-step"><span class="dot">5</span><span>指定随访任务</span></div>
            <div class="flow-step"><span class="dot">6</span><span>AI随访</span></div>
          </div>
        </section>

        <section class="side-card">
          <div class="side-title">档案预览</div>
          <div class="preview-grid">
            <div class="pv-row"><span class="k">姓名</span><span class="v">{{ form.name || '—' }}</span></div>
            <div class="pv-row"><span class="k">来源</span><span class="v">{{ previewSource }}</span></div>
            <div class="pv-row"><span class="k">结节类型</span><span class="v">{{ visibleNodules.join('、') || '—' }}</span></div>
            <div class="pv-row"><span class="k">风险等级</span><span class="v">{{ form.risk || '—' }}</span></div>
            <div class="pv-row"><span class="k">负责人</span><span class="v">{{ form.doctor || '—' }}</span></div>
          </div>
        </section>

        <section class="side-card">
          <div class="side-title">资料完整度</div>
          <div class="progress">
            <div class="bar"><div class="fill" :style="{ width: `${completeness}%` }"></div></div>
            <div class="muted" style="font-size:12px;margin-top:8px">{{ completeness }}%</div>
          </div>
          <div class="muted" style="font-size:12px;line-height:1.6;margin-top:10px">
            建议优先补全：手机号、出生日期、来源信息、至少选择一种结节类型。
          </div>
        </section>

        <section class="side-card">
          <div class="side-title">下一步提示</div>
          <div class="next-box">
            <div class="next-main">{{ nextTip }}</div>
            <div class="muted" style="font-size:12px;line-height:1.6;margin-top:8px">
              保存后可进入“上传报告 → AI结构化解析 → 生成健康管理报告”流程。
            </div>
          </div>
        </section>
      </aside>
    </div>

    <!-- 底部操作栏 -->
    <div class="record-foot" v-if="!embedded">
      <button class="btn" type="button" @click="back">取消</button>
      <div style="margin-left:auto;display:flex;gap:8px;align-items:center">
        <div class="more-wrap">
          <button class="btn" type="button" @click="moreOpen = !moreOpen">更多操作 ▾</button>
          <div v-if="moreOpen" class="more-menu">
            <button type="button" @click="toast('保存并上传报告')">保存并上传报告</button>
            <button type="button" @click="toast('保存并发送问卷')">保存并发送问卷</button>
            <button type="button" @click="toast('保存并进入报告处理')">保存并进入报告处理</button>
          </div>
        </div>
        <button class="primary" type="button" @click="save">保存档案</button>
      </div>
    </div>
    </div>

    <ToastMsg ref="toastRef" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import ToastMsg from '../components/ToastMsg.vue'

const props = defineProps({
  embedded: { type: Boolean, default: false }
})
const emit = defineEmits(['back'])

const router = useRouter()
const toastRef = ref(null)
const user = computed(() => localStorage.getItem('proto_user') || '管理员')

const moreOpen = ref(false)
const saving = ref(false)
const generating = ref(false)

const isImport = computed(() => true)

const organTags = ['肺部结节', '甲状腺结节', '乳腺结节']
const presetTags = [
  { id: 'lung_thyroid', label: '肺+甲' },
  { id: 'lung_breast', label: '肺+乳' },
  { id: 'thyroid_breast', label: '甲+乳' },
  { id: 'triple', label: '三合并' }
]

const selectedTag = ref('乳腺结节')

const tagToOrgans = {
  '肺部结节': ['肺部结节'],
  '甲状腺结节': ['甲状腺结节'],
  '乳腺结节': ['乳腺结节'],
  'lung_thyroid': ['肺部结节', '甲状腺结节'],
  'lung_breast': ['肺部结节', '乳腺结节'],
  'thyroid_breast': ['甲状腺结节', '乳腺结节'],
  'triple': ['肺部结节', '甲状腺结节', '乳腺结节'],
}

// 结节类型 -> 后端 nodule_type 字段值
const tagToNoduleType = {
  '肺部结节': 'lung',
  '甲状腺结节': 'thyroid',
  '乳腺结节': 'breast',
  'lung_thyroid': 'lung_thyroid',
  'lung_breast': 'breast_lung',
  'thyroid_breast': 'breast_thyroid',
  'triple': 'triple',
}

const visibleNodules = computed(() => tagToOrgans[selectedTag.value] || [])

const form = ref({
  // 基础信息
  age: '',
  name: '', gender: '女', birthDate: '',
  phone: '', idNo: '', addr: '',
  height: '', weight: '',
  diabetes_history: '无',
  gaofang_address: '',
  emergency: '配偶', emergencyName: '', emergencyPhone: '',
  note: '',
  source: '门诊', dept: '', doctor: '李医生',
  examDate: '',
  batchNo: '',
  risk: '中风险', needReview: true,

  // 乳腺结节字段（对齐 breast-fields.js）
  breast_discovery_date: '',
  symptoms: [],
  symptoms_other: '',
  birads_level: '不清楚',
  nodule_quantity: '单发',
  nodule_size: '',
  nodule_count: '',
  history: [],
  breast_disease_history_other: '',
  family_history: [],
  family_history_other: '',
  medication_history: [],
  medication_other: '',

  // 甲状腺结节字段
  thyroid_discovery_date: '',
  thyroid_symptoms: [],
  thyroid_symptoms_other: '',
  tirads_level: '不清楚',
  thyroid_nodule_quantity: '',
  thyroid_nodule_size: '',
  thyroid_nodule_count: '',

  // 肺部结节字段
  lung_discovery_date: '',
  lung_symptoms: [],
  lung_symptoms_other: '',
  lung_rads_level: '不清楚',
  lung_nodule_quantity: '',
  lung_nodule_size: '',
  lung_nodule_count: '',
})

function toggleOrganType(t) {
  selectedTag.value = t
}

function applyPreset(id) {
  selectedTag.value = id
}

function toggleArr(arr, v) {
  if (!Array.isArray(arr)) return
  const idx = arr.indexOf(v)
  if (idx >= 0) arr.splice(idx, 1)
  else arr.push(v)
}

const activeOrgan = computed(() => {
  const list = visibleNodules.value
  if (list.includes('肺部结节')) return '肺部结节'
  if (list.includes('甲状腺结节')) return '甲状腺结节'
  if (list.includes('乳腺结节')) return '乳腺结节'
  return '乳腺结节'
})

const isLung = computed(() => activeOrgan.value === '肺部结节')
const isThyroid = computed(() => activeOrgan.value === '甲状腺结节')
const isBreast = computed(() => activeOrgan.value === '乳腺结节')

const activeSite = computed({
  get() {
    if (isLung.value) return form.value.lungSite
    if (isThyroid.value) return form.value.thyroidSite
    return form.value.breastSite
  },
  set(v) {
    if (isLung.value) form.value.lungSite = v
    else if (isThyroid.value) form.value.thyroidSite = v
    else form.value.breastSite = v
  }
})

const activeSize = computed({
  get() {
    if (isLung.value) return form.value.lung_nodule_size
    if (isThyroid.value) return form.value.thyroid_nodule_size
    return form.value.nodule_size
  },
  set(v) {
    if (isLung.value) form.value.lung_nodule_size = v
    else if (isThyroid.value) form.value.thyroid_nodule_size = v
    else form.value.nodule_size = v
  }
})

const activeGradeLabel = computed(() => {
  if (isLung.value) return 'Lung-RADS'
  if (isThyroid.value) return 'TI-RADS'
  return 'BI-RADS'
})

const activeGradeOptions = computed(() => {
  if (isLung.value) return ['1类', '2类', '3类', '4A类', '4B类', '4X类']
  if (isThyroid.value) return ['1类', '2类', '3类', '4A类', '4B类', '5类']
  return ['1类', '2类', '3类', '4A类', '4B类', '4C类', '5类']
})

const activeGrade = computed({
  get() {
    if (isLung.value) return form.value.lung_rads_level
    if (isThyroid.value) return form.value.tirads_level
    return form.value.birads_level
  },
  set(v) {
    if (isLung.value) form.value.lung_rads_level = v
    else if (isThyroid.value) form.value.tirads_level = v
    else form.value.birads_level = v
  }
})

const activeAdviceOptions = computed(() => {
  if (isLung.value) return ['建议随访复查', '建议进一步检查', '建议活检']
  if (isThyroid.value) return ['建议随访复查', '建议穿刺活检', '建议手术']
  return ['建议随访复查', '建议穿刺活检', '建议手术']
})

const activeAdvice = computed({
  get() {
    if (isLung.value) return form.value.lungAdvice
    if (isThyroid.value) return form.value.thyroidAdvice
    return form.value.breastAdvice
  },
  set(v) {
    if (isLung.value) form.value.lungAdvice = v
    else if (isThyroid.value) form.value.thyroidAdvice = v
    else form.value.breastAdvice = v
  }
})

const activeSiteOptions = computed(() => {
  if (isLung.value) return ['右上肺', '右中肺', '右下肺', '左上肺', '左下肺']
  if (isThyroid.value) return ['左叶', '右叶', '峡部']
  return ['左乳', '右乳', '双侧']
})

const previewSource = computed(() => {
  const src = form.value.source || ''
  const dept = form.value.dept || ''
  const doc = form.value.doctor || ''
  if (!src && !dept && !doc) return '—'
  return [src, dept, doc].filter(Boolean).join(' · ')
})

const completeness = computed(() => {
  const fields = [
    form.value.name,
    form.value.gender,
    form.value.phone,
    form.value.source,
    visibleNodules.value.length ? 'ok' : ''
  ]
  const total = fields.length
  const done = fields.filter(Boolean).length
  return Math.round((done / total) * 100)
})

const nextTip = computed(() => {
  if (completeness.value < 70) return '建议先补全关键字段，再保存建档。'
  return '可以保存建档，并继续生成健康档案。'
})

function toast(text) {
  moreOpen.value = false
  toastRef.value?.show(text)
}

function back() {
  if (props.embedded) {
    emit('back')
    return
  }
  router.push('/patient')
}

// 将数组字段转为逗号分隔字符串
function arrToStr(v) {
  if (Array.isArray(v)) return v.join(',')
  return v || ''
}

// 构建提交给后端的患者数据
function buildPatientPayload() {
  const f = form.value
  return {
    name: f.name,
    age: f.age ? parseInt(f.age) : null,
    gender: f.gender,
    phone: f.phone,
    nodule_type: tagToNoduleType[selectedTag.value] || 'breast',
    source_channel: f.source || 'manual',
    manager_name: f.doctor || '李医生',
  }
}

// 构建提交给后端的档案数据
function buildRecordPayload() {
  const f = form.value
  return {
    age: f.age ? parseInt(f.age) : null,
    height: f.height ? parseFloat(f.height) : null,
    weight: f.weight ? parseFloat(f.weight) : null,
    phone: f.phone,
    diabetes_history: f.diabetes_history,
    gaofang_address: f.gaofang_address,

    // 乳腺
    breast_discovery_date: f.breast_discovery_date || null,
    birads_level: f.birads_level,
    nodule_quantity: f.nodule_quantity,
    nodule_size: f.nodule_size,
    nodule_count: f.nodule_count,
    symptoms: arrToStr(f.symptoms),
    symptoms_other: f.symptoms_other,
    family_history: arrToStr(f.family_history),
    family_history_other: f.family_history_other,
    breast_family_history: arrToStr(f.family_history),
    breast_family_history_other: f.family_history_other,
    breast_disease_history: arrToStr(f.history),
    breast_disease_history_other: f.breast_disease_history_other,
    medication_history: arrToStr(f.medication_history),
    medication_other: f.medication_other,

    // 甲状腺
    thyroid_discovery_date: f.thyroid_discovery_date || null,
    tirads_level: f.tirads_level,
    thyroid_nodule_quantity: f.thyroid_nodule_quantity,
    thyroid_nodule_size: f.thyroid_nodule_size,
    thyroid_nodule_count: f.thyroid_nodule_count,
    thyroid_symptoms: arrToStr(f.thyroid_symptoms),
    thyroid_symptoms_other: f.thyroid_symptoms_other,

    // 肺部
    lung_discovery_date: f.lung_discovery_date || null,
    lung_rads_level: f.lung_rads_level,
    lung_nodule_quantity: f.lung_nodule_quantity,
    lung_nodule_size: f.lung_nodule_size,
    lung_nodule_count: f.lung_nodule_count,
    lung_symptoms: arrToStr(f.lung_symptoms),
    lung_symptoms_other: f.lung_symptoms_other,
  }
}

async function save() {
  if (!form.value.name || !form.value.phone) {
    toast('请填写姓名和手机号')
    return
  }
  saving.value = true
  try {
    // 1. 创建患者
    const patRes = await fetch('/api/b/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(buildPatientPayload())
    })
    const patData = await patRes.json()
    if (!patData.success) {
      toast('创建患者失败：' + (patData.message || ''))
      return
    }
    const patientId = patData.data.id
    toast('患者已创建，正在保存档案...')

    // 2. 创建健康档案
    const recPayload = { ...buildRecordPayload(), patient_id: patientId }
    const recRes = await fetch(`/api/b/patients/${patientId}/records`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(recPayload)
    })
    const recData = await recRes.json()
    if (!recData.success) {
      toast('保存档案失败：' + (recData.message || ''))
      return
    }
    toast('档案已保存！')
    // 跳转到患者队列
    setTimeout(() => {
      if (props.embedded) emit('back')
      else router.push('/patient')
    }, 1200)
  } catch (e) {
    toast('网络错误，请确认后端服务已启动')
  } finally {
    saving.value = false
  }
}

async function generateReport() {
  if (!form.value.name || !form.value.phone) {
    toast('请先填写姓名和手机号')
    return
  }
  generating.value = true
  try {
    // 1. 创建患者
    const patRes = await fetch('/api/b/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(buildPatientPayload())
    })
    const patData = await patRes.json()
    if (!patData.success) {
      toast('创建患者失败：' + (patData.message || ''))
      return
    }
    const patientId = patData.data.id
    toast('患者已创建，正在保存档案...')

    // 2. 创建健康档案
    const recPayload = { ...buildRecordPayload(), patient_id: patientId }
    const recRes = await fetch(`/api/b/patients/${patientId}/records`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(recPayload)
    })
    const recData = await recRes.json()
    if (!recData.success) {
      toast('保存档案失败：' + (recData.message || ''))
      return
    }
    const recordId = recData.data?.id || recData.data?.record_id
    toast('档案已保存，正在生成健康报告（AI处理中，请稍候）...')

    // 3. 生成报告
    const rptRes = await fetch('/api/b/reports/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ record_id: recordId })
    })
    const rptData = await rptRes.json()
    if (!rptData.success) {
      toast('生成报告失败：' + (rptData.message || ''))
      return
    }
    toast('健康报告已生成！正在跳转到报告审核页...')
    setTimeout(() => {
      router.push('/patient?tab=review')
    }, 1500)
  } catch (e) {
    toast('网络错误，请确认后端服务已启动')
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.record-page{height:100%;display:flex;flex-direction:column;overflow:hidden;margin:-16px -20px;background:#f3f6fb;padding:12px}
.record-card{flex:1;min-height:0;border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:auto;display:flex;flex-direction:column}
.record-card-head{display:flex;align-items:center;gap:12px;padding:10px 16px 10px;border-bottom:1px solid #e6edf7;flex-shrink:0}
.record-page-title{font-size:13px;font-weight:950;color:#0f172a}
.record-page-sub{font-size:12px;color:#94a3b8;font-weight:500}
.record-layout{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:16px;align-items:start;padding:14px 16px;flex:1}
.record-form .form-sec{border:1px solid #e9eff8;border-radius:12px;background:rgba(255,255,255,.92);padding:12px 16px;margin-bottom:10px}
.record-form .sec-h{font-weight:950;color:#0f172a;margin-bottom:6px;display:flex;align-items:center;gap:8px;font-size:12px}
.record-form .sec-h .no{width:20px;height:20px;border-radius:6px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-size:11px;font-weight:950}
.subsec-h{margin-top:12px;margin-bottom:8px;padding-top:10px;border-top:1px dashed #e6edf7;font-weight:950;color:#0f172a;font-size:12px}
.req::after{content:" *";color:#ef4444;font-weight:900}
.field-label{color:#475569;font-weight:750;font-size:12px;margin-bottom:8px}
.form-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px 12px;align-items:start}
.form-grid.cols3{grid-template-columns:repeat(3,minmax(0,1fr))}
.form-grid.cols4{grid-template-columns:repeat(4,minmax(0,1fr))}
.form-grid .full{grid-column:1 / -1}
.import-hint{display:flex;align-items:flex-start;gap:6px;margin-top:6px;padding:6px 8px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;color:#1d4ed8;font-size:11px;line-height:1.45}
.sync-tip{display:flex;align-items:center;gap:6px;margin-top:6px;color:#64748b;font-size:11px}
.sync-tip.after-note{margin-top:6px;line-height:1.35}
.emg-row{display:none}
.nodule-block{display:none}
.nodule-block-title{display:none}
.input-unit{display:flex;gap:8px;align-items:center}
.input-unit input{flex:1}
.unit{color:#64748b;font-size:13px;white-space:nowrap}
.toggle-row{display:flex;align-items:center;gap:10px;height:32px}
.field-row{display:grid;gap:6px;margin-bottom:10px}
.tag-row{display:flex;flex-wrap:wrap;gap:6px}
.tag-btn{border:1px solid #e6edf7;background:#fff;border-radius:999px;padding:3px 10px;color:#475569;font-weight:850;cursor:pointer;font-size:12px;line-height:1.2;display:inline-flex;align-items:center;gap:6px}
.tag-btn.selected{border-color:#93c5fd;background:#f8fbff}
.tag-btn.active{border-color:#155eef;background:#eef5ff;color:#155eef}
.tag-x{font-size:14px;line-height:1;margin-left:2px;color:inherit;opacity:.9}
.tag-divider{width:1px;height:16px;background:#e6edf7;align-self:center;margin:0 2px}
.tag-btn.preset{background:#fff}

.nodule-mini{border:1px solid #eef2f7;border-radius:10px;background:#fbfdff;padding:8px 10px;margin-top:8px}
.nodule-mini-title{font-weight:950;color:#155eef;font-size:12px;margin-bottom:6px}
.upload-zone{border:1px dashed #cbd5e1;border-radius:10px;padding:8px;text-align:center;color:#64748b;background:#fbfdff;font-size:12px}
.file-card2{display:flex;align-items:center;gap:8px;border:1px solid #eef2f7;border-radius:10px;padding:8px 10px;background:#fff}
.file-card2 .fi{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;font-weight:950;color:#fff}
.file-card2 .fi.pdf{background:#ef4444}
.record-foot{position:sticky;bottom:0;left:0;right:0;padding:10px 16px;background:#fff;border-top:1px solid #e6edf7;display:flex;gap:8px;flex-wrap:wrap;align-items:center;z-index:2;flex-shrink:0}
.more-wrap{position:relative}
.more-menu{position:absolute;bottom:calc(100% + 6px);right:0;background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 8px 24px rgba(15,23,42,.10);min-width:160px;overflow:hidden;z-index:10}
.more-menu button{display:block;width:100%;padding:10px 14px;text-align:left;border:0;background:transparent;color:#334155;font-weight:850;cursor:pointer;font-size:13px}
.more-menu button:hover{background:#f8fbff;color:#155eef}
.form-field{display:flex;flex-direction:column;gap:5px;min-width:0}
.form-field .label{color:#64748b;font-weight:850;font-size:11px;white-space:nowrap}
.form-field.required .label::after{content:" *";color:#ef4444;font-weight:900}
.form-field.full{grid-column:1 / -1}
.form-field.span-2{grid-column:span 2}

.form-field input,
.form-field select{height:32px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none;font-size:13px;width:100%;box-sizing:border-box;max-width:260px}
.form-field.span-2 input,
.form-field.span-2 select,
.form-field.full input,
.form-field.full select{max-width:none}
.form-field input:focus,
.form-field select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.form-field input:disabled,
.form-field select:disabled{background:#f8fafc;color:#94a3b8;cursor:not-allowed}

.note-box{border:1px solid #d9e2ef;border-radius:10px;padding:8px 10px;display:grid;gap:6px;background:#fff;max-width:none}
.note-box textarea{width:100%;border:0;outline:none;padding:0;resize:none;height:60px;min-height:60px;max-height:68px;font-size:13px;line-height:1.4;color:#111827;background:transparent}
.note-foot{display:flex;align-items:flex-start;gap:10px}
.note-count{margin-left:auto;flex:0 0 auto;font-size:11px;line-height:1.2;white-space:nowrap}
.muted{color:#64748b}
.btn{border:1px solid #d9e2ef;border-radius:10px;background:#fff;color:#475569;padding:7px 12px;font-weight:850;cursor:pointer}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:10px;padding:7px 12px;cursor:pointer;font-weight:850}
.tag{display:inline-flex;align-items:center;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:900;line-height:1.4}
.tag.high{background:#fff1f1;color:#dc2626}
.tag.blue{background:#eef5ff;color:#155eef}
.tag.green{background:#ecfff3;color:#14843b}
.toggle{width:36px;height:20px;border-radius:999px;background:#e5e7eb;position:relative;transition:.2s;flex:0 0 auto;cursor:pointer;display:inline-block}
.toggle::after{content:"";position:absolute;left:3px;top:3px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(15,23,42,.15);transition:.2s}
.toggle.on{background:#155eef}
.toggle.on::after{left:19px}

/* 12列稳定栅格（高密度但可读） */
.grid-12{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:8px 12px;align-items:end}
.col-1{grid-column:span 1}
.col-2{grid-column:span 2}
.col-3{grid-column:span 3}
.col-4{grid-column:span 4}
.col-5{grid-column:span 5}
.col-6{grid-column:span 6}
.field{min-width:0}
.field .label{font-size:12px;color:#64748b;font-weight:900;margin-bottom:6px;white-space:nowrap}
.field.required .label::after{content:" *";color:#ef4444;font-weight:900;margin-left:2px}
.field input,.field select{height:34px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;background:#fff;color:#111827;outline:none;font-size:13px;box-sizing:border-box;width:100%}
.field input:focus,.field select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.field.phone input,.field.phone select{min-width:180px}
.field.idno input,.field.idno select{min-width:180px}
.field.addr input,.field.addr select{min-width:260px}
.field.note input,.field.note select{min-width:320px}
.field.dept select{min-width:180px}
.toggle-row{display:flex;align-items:center;gap:8px;height:34px}
.mini-action{height:34px;border:1px solid #d9e2ef;border-radius:10px;background:#fff;color:#155eef;padding:0 10px;font-weight:900;cursor:pointer;width:100%}
.mini-action.ghost{color:#475569}
.mini-action.primary-action{background:#155eef;border-color:#155eef;color:#fff}
.cur-doctor{height:34px;border:1px solid #e6edf7;border-radius:8px;padding:0 10px;background:#f8fafc;color:#334155;font-size:13px;display:flex;align-items:center;font-weight:850}

@media (max-width: 1100px){
  .record-layout{grid-template-columns:minmax(0,1fr)}
  .form-grid.cols4{grid-template-columns:repeat(2,minmax(0,1fr))}
  .form-grid.cols3{grid-template-columns:repeat(2,minmax(0,1fr))}
  .form-field.span-2{grid-column:1 / -1}
  .dense-grid.cols5{grid-template-columns:repeat(2,minmax(180px,1fr))}
  .dense-grid.cols4{grid-template-columns:repeat(2,minmax(180px,1fr))}
}

@media (max-width: 640px){
  .record-page{padding:12px 12px 56px}
  .record-form .form-sec{padding:14px 14px}
  .form-grid.cols4,.form-grid.cols3{grid-template-columns:1fr}
  .form-field.span-2{grid-column:auto}
}

.record-side{position:sticky;top:12px;display:flex;flex-direction:column;gap:10px}
.side-card{background:#fff;border:1px solid #e6edf7;border-radius:12px;box-shadow:0 6px 18px rgba(15,23,42,.04);padding:12px}
.side-title{font-size:12px;font-weight:950;color:#0f172a;margin-bottom:8px}
.flow-steps{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}
.flow-step{display:flex;align-items:center;gap:8px;color:#475569;font-weight:850;font-size:12px;padding:6px 8px;border:1px solid #eef2f7;border-radius:10px;background:#fbfdff}
.flow-step .dot{width:18px;height:18px;border-radius:6px;display:grid;place-items:center;background:#e2e8f0;color:#334155;font-weight:950;font-size:11px}
.flow-step.done .dot{background:#dcfce7;color:#16a34a}
.preview-grid{display:flex;flex-direction:column;gap:8px}
.pv-row{display:flex;justify-content:space-between;gap:10px;font-size:12px}
.pv-row .k{color:#94a3b8;font-weight:850;white-space:nowrap}
.pv-row .v{color:#0f172a;font-weight:900;text-align:right}
.progress .bar{height:10px;border-radius:999px;background:#eef2f7;overflow:hidden}
.progress .fill{height:100%;background:linear-gradient(90deg,#155eef,#22c55e);border-radius:999px}
.next-box{border:1px solid #eef2f7;background:#fbfdff;border-radius:12px;padding:10px}
.next-main{font-weight:950;color:#0f172a;font-size:12px;line-height:1.45}

/* 高密度横向表单 */
.dense-grid{display:grid;gap:8px 14px;align-items:center}
.dense-grid.cols3{grid-template-columns:repeat(3,minmax(0,1fr))}
.dense-grid.cols4{grid-template-columns:repeat(4,minmax(180px,1fr))}
.dense-grid.cols5{grid-template-columns:repeat(5,minmax(160px,1fr))}
.dense-grid .full{grid-column:1 / -1}
.dense-grid .span-2{grid-column:span 2}
.hfield{display:grid;grid-template-columns:68px minmax(0,1fr);gap:6px;align-items:center;min-width:140px}
.hfield.required .hl::after{content:" *";color:#ef4444;font-weight:900;margin-left:2px}
.hl{color:#64748b;font-weight:900;font-size:12px;white-space:nowrap}
.hfield input,.hfield select{height:32px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none;font-size:13px;box-sizing:border-box;width:100%;min-width:140px}
.hfield input:focus,.hfield select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.hfield.full{grid-column:1 / -1}
.hfield.phone input,.hfield.phone select{min-width:180px}
.hfield.idno input,.hfield.idno select{min-width:180px}
.hfield.addr input,.hfield.addr select{min-width:260px}
.hfield.note input,.hfield.note select{min-width:320px}
.hfield.dept select{min-width:180px}
.hpair{display:flex;align-items:center;gap:8px;min-width:0}
.hpair .grow{flex:1;min-width:0}
.hpair .age{width:86px;flex:0 0 auto}
.unit{color:#64748b;font-size:12px;white-space:nowrap}
.toggle-row{display:flex;align-items:center;gap:8px;height:32px}
</style>
