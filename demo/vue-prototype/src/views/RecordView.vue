<template>
  <div class="record-page">
    <div class="queue-head">
      <div class="queue-title">患者建档</div>
      <div class="crumb">首页 / 患者建档</div>
    </div>

    <div class="record-layout">
      <div class="record-form">
        <section class="form-sec">
          <div class="sec-h"><span class="no">0</span>建档方式</div>
          <div class="method-grid">
            <button type="button" class="method-card" :class="{ active: method === 'manual' }" @click="method = 'manual'">
              <span class="chk">{{ method === 'manual' ? '✓' : '' }}</span>
              <div class="ico">＋</div>
              <div class="t">手动建档</div>
              <div class="s">由工作人员录入患者基础信息与结节资料。</div>
            </button>
            <button type="button" class="method-card" :class="{ active: method === 'clinic' }" @click="method = 'clinic'">
              <span class="chk">{{ method === 'clinic' ? '✓' : '' }}</span>
              <div class="ico">门</div>
              <div class="t">门诊导入</div>
              <div class="s">从门诊系统同步患者与检查信息。</div>
            </button>
            <button type="button" class="method-card" :class="{ active: method === 'checkup' }" @click="method = 'checkup'">
              <span class="chk">{{ method === 'checkup' ? '✓' : '' }}</span>
              <div class="ico">检</div>
              <div class="t">体检中心导入</div>
              <div class="s">从体检系统批量导入检查报告。</div>
            </button>
            <button type="button" class="method-card" :class="{ active: method === 'batch' }" @click="method = 'batch'">
              <span class="chk">{{ method === 'batch' ? '✓' : '' }}</span>
              <div class="ico">批</div>
              <div class="t">批量导入</div>
              <div class="s">按模板导入多名患者档案。</div>
            </button>
          </div>
        </section>

        <section class="form-sec">
          <div class="sec-h"><span class="no">一</span>患者基础信息</div>
          <div class="form-grid">
            <label class="filter-item"><span class="req">姓名</span><input v-model="form.name" placeholder="请输入患者姓名"></label>
            <label class="filter-item"><span class="req">性别</span><select v-model="form.gender"><option>男</option><option>女</option></select></label>
            <label class="filter-item"><span class="req">年龄</span><div style="display:flex;gap:8px;align-items:center"><input v-model="form.age" style="flex:1"><span class="muted">岁</span></div></label>
            <label class="filter-item"><span class="req">手机号</span><input v-model="form.phone" placeholder="请输入手机号"></label>
            <label class="filter-item">身份证号<input v-model="form.idNo" placeholder="请输入身份证号"></label>
            <label class="filter-item">联系地址<input v-model="form.addr" placeholder="省 / 市 / 区 / 详细地址"></label>
            <label class="filter-item">紧急联系人<select v-model="form.emergency"><option>配偶</option><option>子女</option><option>父母</option><option>其他</option></select></label>
            <label class="filter-item full">备注<textarea v-model="form.note" rows="3" placeholder="可填写过敏史、既往史等" style="resize:vertical;border:1px solid #d9e2ef;border-radius:8px;padding:8px 10px;outline:none;width:100%"></textarea><div class="muted" style="text-align:right;margin-top:4px;font-size:12px">{{ form.note.length }} / 100</div></label>
          </div>
        </section>

        <section class="form-sec">
          <div class="sec-h"><span class="no">二</span>患者来源</div>
          <div class="form-grid cols3">
            <label class="filter-item"><span class="req">来源类型</span><select v-model="form.source"><option>门诊</option><option>体检中心</option><option>其他</option></select></label>
            <label class="filter-item"><span class="req">来源科室</span><select v-model="form.dept"><option>呼吸内科</option><option>乳腺外科</option><option>甲状腺外科</option></select></label>
            <label class="filter-item"><span class="req">就诊医生</span><select v-model="form.doctor"><option>李医生</option><option>王医生</option></select></label>
            <label class="filter-item"><span class="req">检查日期</span><input v-model="form.examDate" type="date"></label>
            <label class="filter-item">导入批次号<input v-model="form.batchNo" placeholder="系统自动生成或手填"></label>
            <div></div>
          </div>
        </section>

        <section class="form-sec">
          <div class="sec-h"><span class="no">三</span>结节信息</div>
          <div style="margin-bottom:12px">
            <div class="muted" style="font-size:12px;font-weight:800;margin-bottom:8px"><span class="req">结节类型</span></div>
            <div class="tag-row">
              <button v-for="t in noduleTags" :key="t" type="button" class="tag-btn" :class="{ active: form.noduleTag === t }" @click="form.noduleTag = t">{{ t }}</button>
            </div>
          </div>
          <div class="form-grid cols3">
            <label class="filter-item"><span class="req">初始风险等级</span><select v-model="form.risk"><option>高风险</option><option>中风险</option><option>低风险</option></select></label>
            <label class="filter-item"><span class="req">结节部位</span><select v-model="form.site"><option>右上肺</option><option>左上肺</option><option>右下肺</option></select></label>
            <label class="filter-item"><span class="req">最大直径</span><div style="display:flex;gap:8px;align-items:center"><input v-model="form.size" style="flex:1"><span class="muted">mm</span></div></label>
            <label class="filter-item"><span class="req">影像特征</span><select v-model="form.feature"><option>磨玻璃</option><option>实性</option><option>混合</option></select></label>
            <label class="filter-item"><span class="req">初步建议</span><select v-model="form.advice"><option>建议随访复查</option><option>建议进一步检查</option></select></label>
            <label class="filter-item"><span class="req">是否需要医生复核</span><div style="display:flex;align-items:center;gap:10px;height:34px"><span class="toggle" :class="{ on: form.needReview }" @click="form.needReview = !form.needReview" aria-hidden="true"></span><span class="muted" style="font-weight:800">{{ form.needReview ? '是' : '否' }}</span></div></label>
          </div>
        </section>

        <section class="form-sec">
          <div class="sec-h"><span class="no">四</span>报告资料</div>
          <div class="form-grid">
            <label class="filter-item"><span class="req">报告类型</span><select><option>CT报告</option><option>超声报告</option><option>病理报告</option></select></label>
            <label class="filter-item"><span class="req">上传检查报告</span><input type="file" disabled style="opacity:.75"></label>
          </div>
          <div style="display:grid;gap:10px;margin-top:10px">
            <div class="file-card2">
              <div class="fi pdf">PDF</div>
              <div style="flex:1;min-width:0">
                <div style="font-weight:950;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">肺部CT_20260420.pdf</div>
                <div class="muted" style="font-size:12px;margin-top:2px">2.4 MB · 已校验</div>
              </div>
              <span class="tag green">✓</span>
            </div>
            <div class="file-card2">
              <div class="fi zip">ZIP</div>
              <div style="flex:1;min-width:0">
                <div style="font-weight:950;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">影像附件包.zip</div>
                <div class="muted" style="font-size:12px;margin-top:2px">18.6 MB · 已校验</div>
              </div>
              <span class="tag green">✓</span>
            </div>
            <div class="upload-zone">☁ 拖拽文件到此处，或 <b style="color:#155eef">稍后上传</b></div>
          </div>
        </section>

        <section class="form-sec">
          <div class="sec-h"><span class="no">五</span>负责人设置</div>
          <div class="form-grid cols3">
            <label class="filter-item"><span class="req">负责医生</span><select><option>李医生</option><option>王医生</option></select></label>
            <label class="filter-item"><span class="req">健康管理师</span><select><option>杨健管</option><option>赵健管</option></select></label>
            <label class="filter-item"><span class="req">随访护士</span><select><option>韩护士</option><option>刘护士</option></select></label>
            <label class="filter-item full"><span class="req">所属科室</span><select><option>健康管理科</option><option>呼吸内科</option></select></label>
          </div>
        </section>
      </div>

      <aside class="record-side">
        <div class="side-card">
          <div class="dash-title" style="margin-bottom:10px">建档后流程</div>
          <div class="wf-grid">
            <div class="wf-node"><div class="ic">档</div><div style="font-weight:900;color:#0f172a">建档</div><div class="muted" style="font-size:11px;margin-top:4px">完成</div></div>
            <div class="wf-node"><div class="ic">报</div><div style="font-weight:900;color:#0f172a">上传报告</div><div class="muted" style="font-size:11px;margin-top:4px">待处理</div></div>
            <div class="wf-node"><div class="ic">AI</div><div style="font-weight:900;color:#0f172a">AI解析</div><div class="muted" style="font-size:11px;margin-top:4px">排队</div></div>
            <div class="wf-node"><div class="ic">稿</div><div style="font-weight:900;color:#0f172a">生成健康报告</div><div class="muted" style="font-size:11px;margin-top:4px">草稿</div></div>
          </div>
          <div class="wf-arrow">↓</div>
          <div class="wf-grid">
            <div class="wf-node"><div class="ic">医</div><div style="font-weight:900;color:#0f172a">医生复核</div><div class="muted" style="font-size:11px;margin-top:4px">待办</div></div>
            <div class="wf-node"><div class="ic">推</div><div style="font-weight:900;color:#0f172a">推送患者</div><div class="muted" style="font-size:11px;margin-top:4px">待办</div></div>
            <div class="wf-node"><div class="ic">随</div><div style="font-weight:900;color:#0f172a">随访任务</div><div class="muted" style="font-size:11px;margin-top:4px">生成</div></div>
            <div class="wf-node"><div class="ic">环</div><div style="font-weight:900;color:#0f172a">闭环</div><div class="muted" style="font-size:11px;margin-top:4px">目标</div></div>
          </div>
          <div class="muted" style="margin-top:10px;line-height:1.65">闭环管理，确保每位患者获得及时、规范的随访服务。</div>
        </div>

        <div class="side-card">
          <div class="dash-title" style="margin-bottom:10px">档案预览</div>
          <div class="kvs">
            <div><div class="k">患者姓名</div><div class="v">{{ form.name }}</div></div>
            <div><div class="k">来源</div><div class="v">{{ form.source }} · {{ form.dept }}</div></div>
            <div><div class="k">结节类型</div><div class="v"><span class="tag blue">{{ form.noduleTag }}</span></div></div>
            <div><div class="k">风险等级</div><div class="v"><span class="tag high">{{ form.risk }}</span></div></div>
            <div><div class="k">负责人</div><div class="v">李医生 / 杨健管 / 韩护士</div></div>
            <div><div class="k">下一步</div><div class="v">上传报告 → AI解析</div></div>
          </div>
        </div>

        <div class="follow-tip" style="margin:0">
          <div>患者信息由医院工作人员录入与管理，请确保信息真实准确。</div>
          <button type="button" class="x" title="关闭" @click="showTip = false" v-if="showTip">×</button>
        </div>
      </aside>
    </div>

    <div class="record-foot">
      <button class="primary" type="button" @click="save">保存档案</button>
      <button class="btn" type="button" @click="toast('保存并上传报告')">保存并上传报告</button>
      <button class="btn" type="button" @click="toast('保存并发送问卷')">保存并发送问卷</button>
      <button class="btn" type="button" @click="toast('保存并进入报告处理')">保存并进入报告处理</button>
      <button class="btn" type="button" style="margin-right:auto" @click="back">取消</button>
    </div>

    <ToastMsg ref="toastRef" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ToastMsg from '../components/ToastMsg.vue'

const router = useRouter()
const toastRef = ref(null)

const method = ref('manual')
const showTip = ref(true)

const noduleTags = ['乳腺结节', '甲状腺结节', '肺部结节', '肺+甲', '肺+乳', '甲+乳', '三合并']

const form = ref({
  name: '张*国',
  gender: '男',
  age: '56',
  phone: '138****5678',
  idNo: '',
  addr: '山东省济南市历下区xx路123号',
  emergency: '配偶',
  note: '已电话确认可随访，注意保护隐私。',
  source: '门诊',
  dept: '呼吸内科',
  doctor: '李医生',
  examDate: '2026-04-20',
  batchNo: '',
  noduleTag: '肺部结节',
  risk: '高风险',
  site: '右上肺',
  size: '8',
  feature: '磨玻璃',
  advice: '建议随访复查',
  needReview: true
})

/**
 * @description 轻提示
 * @param {string} text 提示文案
 */
function toast(text) {
  toastRef.value?.show(text)
}

/**
 * @description 保存档案（原型示意）
 */
function save() {
  toast('已保存档案（示意）')
}

/**
 * @description 返回患者管理页
 */
function back() {
  router.push('/patient')
}
</script>

<style scoped>
/* 复刻自 demo/医院场景样子版.html 的建档页样式 */
.record-page{min-height:100%;overflow:auto;padding:14px 18px 96px;background:#f3f6fb}
.record-layout{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(320px,.75fr);gap:12px;align-items:start}
.record-form .form-sec{border:1px solid #eef2f7;border-radius:10px;background:#fff;padding:14px 14px;margin-bottom:12px}
.record-form .sec-h{font-weight:950;color:#0f172a;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.record-form .sec-h .no{width:22px;height:22px;border-radius:6px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-size:12px;font-weight:950}
.req::after{content:" *";color:#ef4444;font-weight:900}
.form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 18px}
.form-grid.cols3{grid-template-columns:repeat(3,minmax(0,1fr))}
.form-grid .full{grid-column:1 / -1}
.method-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.method-card{border:1px solid #e6edf7;border-radius:10px;background:#fff;padding:12px 12px;position:relative;cursor:pointer;text-align:left}
.method-card.active{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.12)}
.method-card .ico{width:34px;height:34px;border-radius:10px;background:#f8fbff;border:1px solid #dbeafe;display:grid;place-items:center;color:#155eef;font-weight:950}
.method-card .t{margin-top:8px;font-weight:950;color:#0f172a}
.method-card .s{margin-top:4px;color:#64748b;font-size:12px;line-height:1.55}
.method-card .chk{position:absolute;right:10px;top:10px;width:18px;height:18px;border-radius:6px;border:1px solid #e6edf7;display:grid;place-items:center;color:#fff;font-weight:950;font-size:12px}
.method-card.active .chk{background:#155eef;border-color:#155eef}
.tag-row{display:flex;flex-wrap:wrap;gap:8px}
.tag-btn{border:1px solid #e6edf7;background:#fff;border-radius:999px;padding:6px 12px;color:#475569;font-weight:850;cursor:pointer}
.tag-btn.active{border-color:#155eef;background:#eef5ff;color:#155eef}
.upload-zone{border:1px dashed #cbd5e1;border-radius:10px;padding:16px;text-align:center;color:#64748b;background:#fbfdff}
.file-card2{display:flex;align-items:center;gap:10px;border:1px solid #eef2f7;border-radius:10px;padding:10px 12px;background:#fff}
.file-card2 .fi{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;font-weight:950;color:#fff}
.file-card2 .fi.pdf{background:#ef4444}.file-card2 .fi.zip{background:#f97316}
.record-side .side-card{border:1px solid #eef2f7;border-radius:10px;background:#fff;padding:12px 14px;margin-bottom:12px}
.wf-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;align-items:start}
.wf-node{border:1px solid #eef2f7;border-radius:10px;padding:10px;text-align:center;background:#fbfdff}
.wf-node .ic{width:34px;height:34px;border-radius:10px;margin:0 auto 6px;display:grid;place-items:center;background:#eef5ff;color:#155eef;font-weight:950}
.wf-arrow{text-align:center;color:#94a3b8;font-weight:950;padding:6px 0}
.record-foot{position:sticky;bottom:0;left:0;right:0;margin:12px -18px -14px;padding:12px 18px;background:#fff;border-top:1px solid #e6edf7;display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end;z-index:2}

.queue-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.queue-title{font-size:20px;font-weight:950;color:#0f172a}
.crumb{color:#64748b;font-weight:700}
.filter-item{display:flex;flex-direction:column;gap:6px;color:#475569;font-weight:750}
.filter-item input,.filter-item select{height:34px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;background:#fff;color:#111827;outline:none}
.filter-item input:focus,.filter-item select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.muted{color:#64748b}
.btn{border:1px solid #d9e2ef;border-radius:8px;background:#fff;color:#475569;padding:8px 14px;font-weight:850;cursor:pointer}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:8px;padding:8px 14px;cursor:pointer;font-weight:850}
.tag{display:inline-flex;align-items:center;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:900;line-height:1.4}
.tag.high{background:#fff1f1;color:#dc2626}
.tag.blue{background:#eef5ff;color:#155eef}
.tag.green{background:#ecfff3;color:#14843b}
.kvs{display:grid;grid-template-columns:1fr 1fr;gap:10px 14px;margin-top:10px}
.kvs .k{color:#94a3b8;font-size:12px}
.kvs .v{font-weight:900;color:#0f172a;margin-top:4px}
.dash-title{font-weight:950;color:#0f172a}
.follow-tip{background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;border-radius:10px;padding:8px 10px;font-weight:800;margin-bottom:10px;display:flex;justify-content:space-between;gap:10px;align-items:center}
.follow-tip .x{border:0;background:transparent;color:#c2410c;font-weight:950;cursor:pointer}
.toggle{width:38px;height:22px;border-radius:999px;background:#e5e7eb;position:relative;transition:.2s;flex:0 0 auto;cursor:pointer}
.toggle::after{content:"";position:absolute;left:3px;top:3px;width:16px;height:16px;border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(15,23,42,.15);transition:.2s}
.toggle.on{background:#155eef}
.toggle.on::after{left:19px}
</style>

