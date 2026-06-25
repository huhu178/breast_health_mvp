<template>
  <div class="patient-workspace">
    <section class="workspace-hero card">
      <div class="workspace-id">
        <button class="btn-link-lite" type="button" @click="$emit('back')">返回队列</button>
        <div>
          <div class="workspace-name">{{ patient.name || '未选择患者' }}</div>
          <div class="workspace-sub">{{ patient.gender }} · {{ patient.age }}岁 · {{ patient.phoneMasked }} · {{ patient.nodules }}</div>
        </div>
      </div>
      <div class="workspace-badges">
        <span class="pill" :data-tone="patient.riskTone">{{ patient.risk || '未评估' }}</span>
        <span class="status-tag" :data-s="statusKey(patient)">{{ statusLabel(patient) }}</span>
        <span class="wecom-badge" :data-on="isWecomBound(patient)">{{ wecomStatusText(patient) }}</span>
      </div>
    </section>

    <section class="workspace-flow card">
      <div v-for="step in flowSteps" :key="step.key" class="workspace-flow-node" :data-state="step.state">
        <span class="flow-dot">{{ step.no }}</span>
        <span>{{ step.label }}</span>
      </div>
    </section>

    <div class="workspace-grid">
      <section class="workspace-main">
        <section class="flow-section card">
          <div class="section-head">
            <div>
              <div class="section-title">一、患者档案与资料管理</div>
              <div class="section-sub">基础信息、病史、检查资料、影像报告和手机舌诊入口统一维护。</div>
            </div>
            <div class="section-actions" v-if="canOperatePatient">
              <button v-if="!editMode" class="btn" type="button" @click="$emit('start-patient-edit')">编辑患者信息</button>
              <button v-if="editMode" class="btn" type="button" @click="$emit('cancel-patient-edit')">取消</button>
              <button v-if="editMode" class="primary" type="button" @click="$emit('save-patient')">保存患者信息</button>
              <button class="btn" type="button" @click="$emit('edit-record', patient)">编辑档案</button>
            </div>
          </div>
          <div class="profile-grid">
            <label class="profile-field"><span>姓名</span><input :value="patient.name" :readonly="!editMode" @input="updatePatient('name', $event.target.value)"></label>
            <label class="profile-field"><span>性别</span><input :value="patient.gender" :readonly="!editMode" @input="updatePatient('gender', $event.target.value)"></label>
            <label class="profile-field"><span>年龄</span><input :value="patient.age" :readonly="!editMode" @input="updatePatient('age', $event.target.value)"></label>
            <label class="profile-field"><span>来源</span><input :value="patient.source" :readonly="!editMode" @input="updatePatient('source', $event.target.value)"></label>
            <label class="profile-field">
              <span>所属科室</span>
              <select v-if="editMode" :value="patient.department_id || ''" @change="updatePatient('department_id', $event.target.value)">
                <option value="">未分配</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.id">{{ dept.name }}</option>
              </select>
              <input v-else :value="patient.departmentName || '未分配'" readonly>
            </label>
            <label class="profile-field">
              <span>主要负责医生</span>
              <select v-if="editMode" :value="patient.primary_doctor_id || ''" @change="updatePatient('primary_doctor_id', $event.target.value)">
                <option value="">未分配</option>
                <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">{{ doctor.real_name || doctor.username }}</option>
              </select>
              <input v-else :value="patient.owner || patient.primaryDoctorName || '未分配'" readonly>
            </label>
            <label class="profile-field">
              <span>健康管理师/医生助手</span>
              <select v-if="editMode" :value="patient.manager_id || ''" @change="updatePatient('manager_id', $event.target.value)">
                <option value="">未分配</option>
                <option v-for="manager in managers" :key="manager.id" :value="manager.id">{{ manager.real_name || manager.username }}</option>
              </select>
              <input v-else :value="patient.managerName || '未分配'" readonly>
            </label>
            <label class="profile-field">
              <span>结节类型</span>
              <select v-if="editMode" :value="patient.noduleType || ''" @change="updatePatient('noduleType', $event.target.value)">
                <option value="breast">乳腺结节</option>
                <option value="thyroid">甲状腺结节</option>
                <option value="lung">肺结节</option>
                <option value="breast_thyroid">乳腺+甲状腺结节</option>
                <option value="breast_lung">乳腺+肺结节</option>
                <option value="lung_thyroid">肺+甲状腺结节</option>
                <option value="triple">三合并结节</option>
              </select>
              <input v-else :value="patient.nodules" readonly>
            </label>
            <label class="profile-field"><span>企微 external_userid</span><input :value="patient.wecomExternalUserid || '未绑定'" readonly></label>
          </div>
          <div class="profile-note">
            <label class="profile-field wide"><span>病史/既往史/体征</span><textarea :value="patient.profileNote" :readonly="!editMode" @input="updatePatient('profileNote', $event.target.value)"></textarea></label>
          </div>
          <div class="record-report-card">
            <div>
              <b>关联健康报告</b>
              <span v-if="patient.latestReport?.id">
                {{ patient.latestReport.report_code || `报告 #${patient.latestReport.id}` }} · {{ reportDbStatusLabel(patient.latestReport.status) }}
              </span>
              <span v-else>当前档案还没有生成健康报告</span>
            </div>
            <button v-if="patient.latestReport?.id" class="btn" type="button" @click="$emit('view-report', patient.latestReport.id)">查看报告</button>
          </div>

          <div class="workspace-summary-grid">
            <div class="workspace-summary-card">
              <span>档案记录</span>
              <b>{{ patient.workspaceRecords?.length || 0 }}</b>
              <em>{{ latestRecordLabel }}</em>
            </div>
            <div class="workspace-summary-card">
              <span>健康报告</span>
              <b>{{ patient.workspaceReports?.length || 0 }}</b>
              <em>{{ patient.latestReport?.status ? reportDbStatusLabel(patient.latestReport.status) : '未生成' }}</em>
            </div>
            <div class="workspace-summary-card">
              <span>随访计划</span>
              <b>{{ patient.workspacePlans?.length || 0 }}</b>
              <em>{{ activePlanLabel }}</em>
            </div>
            <div class="workspace-summary-card">
              <span>执行任务</span>
              <b>{{ patient.workspaceTasks?.length || 0 }}</b>
              <em>{{ taskExecutionSummary }}</em>
            </div>
          </div>

          <div class="upload-grid">
            <section class="upload-panel">
              <div class="upload-title">影像报告</div>
              <div class="upload-sub">支持 PDF、图片等文件；后续可接入结构化解析。</div>
              <input ref="imagingInputRef" type="file" multiple accept=".pdf,image/*" class="hidden-input" @change="$emit('imaging-upload', $event)">
              <button v-if="canOperatePatient" class="primary" type="button" @click="imagingInputRef?.click()">上传影像报告</button>
              <div class="file-list">
                <div v-for="file in patient.assets?.imagingReports || []" :key="file.id" class="file-row">
                  <div><b>{{ file.name }}</b><span>{{ file.uploadedAt }} · {{ file.uploader }}</span></div>
                  <button v-if="canOperatePatient" class="btn-link-lite" type="button" @click="$emit('remove-asset', 'imagingReports', file.id)">删除</button>
                </div>
                <div v-if="!(patient.assets?.imagingReports || []).length" class="empty-line">暂无影像报告</div>
              </div>
            </section>

            <section class="upload-panel">
              <div class="upload-title">手机舌诊 H5</div>
              <div class="upload-sub">B端只生成手机可访问的舌诊链接；请用患者手机或健康管理师手机打开，电脑和平板不作为采集终端。</div>
              <div class="tongue-h5-panel">
                <div class="tongue-h5-copy">
                  <input :value="patient.tongueMobileOpenUrl || patient.tongueH5Url || '生成后显示手机舌诊链接'" readonly>
                  <button class="btn-link-lite" type="button" @click="$emit('copy-tongue-link')" :disabled="!(patient.tongueMobileOpenUrl || patient.tongueH5Url)">复制链接</button>
                </div>
                <div class="tongue-h5-body">
                  <div class="tongue-qr">
                    <img v-if="tongueQrUrl" :src="tongueQrUrl" alt="舌诊H5二维码">
                    <span v-else>生成二维码</span>
                  </div>
                  <div class="tongue-h5-help">
                    <b>手机打开提示</b>
                    <span>生成链接后，用手机扫码或复制链接发送给患者；进入第三方 H5 后在手机内完成舌面图、舌下图采集。</span>
                    <span>检测完成后，结果通过报告回调或报告检索回流到本系统。</span>
                  </div>
                </div>
              </div>
              <div v-if="canOperatePatient" class="tongue-diagnosis-bar">
                <button class="primary" type="button" @click="$emit('start-tongue')" :disabled="tongueSubmitting || !patient.workspaceRecordId">
                  {{ tongueSubmitting ? '提交中...' : tongueActionLabel }}
                </button>
                <button class="btn" type="button" @click="$emit('sync-tongue')" :disabled="tongueSyncing || !patient.tongueTask?.id">
                  {{ tongueSyncing ? '同步中...' : '同步舌诊结果' }}
                </button>
                <span v-if="patient.tongueTask" class="tongue-status">{{ tongueStatusLabel }}</span>
              </div>
              <div v-if="patient.tongueTask?.tongue_feature" class="tongue-result">
                {{ patient.tongueTask.tongue_feature }}
              </div>
            </section>
          </div>
        </section>

        <section class="flow-section card">
          <div class="section-head">
            <div>
              <div class="section-title">二、风险评估</div>
              <div class="section-sub">按结节分级、大小、病史和资料完整度拆分展示，避免只给一个笼统结论。</div>
            </div>
            <span class="pill" :data-tone="computedRisk.tone">{{ computedRisk.level }}</span>
          </div>
          <div class="risk-layers">
            <div v-for="item in riskLayerItems" :key="item.key" class="risk-layer" :data-tone="item.tone">
              <div class="risk-layer-top"><b>{{ item.label }}</b><span>{{ item.level }}</span></div>
              <p>{{ item.reason }}</p>
            </div>
          </div>
        </section>

        <section class="flow-section card">
          <div class="section-head">
            <div>
              <div class="section-title">三、健康报告意见</div>
              <div class="section-sub">{{ adviceLocked ? '最终报告已归档，建议内容已锁定。' : 'AI意见作为可迭代草稿，支持再次生成、人工编辑、提交审核和历史版本留痕。' }}</div>
            </div>
            <div v-if="canOperatePatient" class="section-actions">
              <button class="btn" type="button" @click="$emit('regenerate-advice')" :disabled="adviceGenerating || adviceLocked">{{ adviceGenerating ? '生成中...' : '再次生成建议' }}</button>
              <button class="primary" type="button" @click="$emit('save-advice')" :disabled="adviceLocked">保存草稿</button>
              <button class="primary" type="button" @click="$emit('submit-advice')" :disabled="adviceLocked || advice.status === 'reviewing'">提交审核</button>
            </div>
          </div>
          <div class="advice-status-row">
            <span class="status-tag" :data-s="advice.status">{{ adviceStatusLabel(advice.status) }}</span>
            <span class="muted">当前版本：V{{ advice.version || 1 }} · {{ advice.updatedAt || '未保存' }}</span>
            <span v-if="adviceLocked" class="lock-chip">已锁定</span>
          </div>
          <textarea class="advice-editor" :value="advice.content" :readonly="adviceLocked" placeholder="生成后的建议会出现在这里，也可以人工编辑。" @input="$emit('update-advice-content', $event.target.value)"></textarea>
          <div class="version-list">
            <div v-for="v in advice.history || []" :key="v.id" class="version-row">
              <span>V{{ v.version }}</span><b>{{ adviceStatusLabel(v.status) }}</b><span>{{ v.savedAt }}</span>
            </div>
            <div v-if="!(advice.history || []).length" class="empty-line">暂无历史版本</div>
          </div>
        </section>

        <section class="flow-section card">
          <div class="section-head">
            <div>
              <div class="section-title">四、最终健康报告</div>
              <div class="section-sub">只有审核通过的建议才能写入最终报告，与草稿意见明确区分。</div>
            </div>
            <div v-if="canOperatePatient" class="section-actions">
              <button class="primary" type="button" @click="$emit('approve-advice')" :disabled="advice.status !== 'reviewing' || adviceLocked">审核通过并写入最终报告</button>
              <button
                v-if="patient.workspaceReportId && canCreateReportFollowup(patient.latestReport)"
                class="btn"
                type="button"
                @click="$emit('create-report-followup')"
                :disabled="isCreatingReportFollowup(patient.workspaceReportId) || !!existingReportFollowupTask(patient.workspaceReportId)"
              >
                {{ existingReportFollowupTask(patient.workspaceReportId) ? '已创建首次随访' : isCreatingReportFollowup(patient.workspaceReportId) ? '创建中...' : '创建首次随访任务' }}
              </button>
            </div>
          </div>
          <div v-if="patient.finalReport?.content" class="final-report-box">
            <div class="final-report-meta">已归档 · {{ patient.finalReport.archivedAt }} · 来源 V{{ patient.finalReport.version }}</div>
            <p>{{ patient.finalReport.content }}</p>
          </div>
          <div v-else class="empty-line">暂无最终报告。请先生成/编辑建议并完成审核。</div>
        </section>

        <section class="flow-section card">
          <div class="section-head">
            <div>
              <div class="section-title">五、报告随访建议</div>
              <div class="section-sub">医生查看报告后填写一段随访建议，健康管理师和医生助手可据此调整随访计划。</div>
            </div>
            <div class="section-actions">
              <button v-if="canEditReportFollowupAdvice" class="btn" type="button" @click="$emit('save-report-followup-advice')" :disabled="!patient.workspaceReportId">保存草稿</button>
              <button v-if="canEditReportFollowupAdvice" class="primary" type="button" @click="$emit('submit-report-followup-advice')" :disabled="!patient.workspaceReportId || !patient.reportFollowupAdviceDraft">提交建议</button>
            </div>
          </div>
          <div class="report-advice-grid">
            <label class="profile-field wide">
              <span>报告随访建议内容</span>
              <textarea
                :value="patient.reportFollowupAdviceDraft || latestReportFollowupAdvice(patient)?.advice_content || ''"
                placeholder="例如：建议6个月后复查乳腺超声，期间按计划随访。"
                :readonly="!canEditReportFollowupAdvice"
                @input="$emit('update-report-followup-advice', { field: 'advice_content', value: $event.target.value })"
              ></textarea>
            </label>
            <label class="profile-field">
              <span>建议下次随访时间</span>
              <input
                type="date"
                :value="patient.reportFollowupAdviceNextAt || latestReportFollowupAdvice(patient)?.suggested_next_followup_at || ''"
                :readonly="!canEditReportFollowupAdvice"
                @input="$emit('update-report-followup-advice', { field: 'suggested_next_followup_at', value: $event.target.value })"
              >
            </label>
          </div>
          <div class="version-list">
            <div v-for="item in reportFollowupAdvices(patient)" :key="item.id" class="version-row report-advice-row">
              <span>{{ item.status === 'submitted' ? '已提交' : '草稿' }}</span>
              <b>{{ item.doctor_name || '医生' }}</b>
              <span>{{ item.updated_at || item.created_at || '-' }}</span>
            </div>
            <div v-if="!reportFollowupAdvices(patient).length" class="empty-line">暂无报告随访建议</div>
          </div>
        </section>
      </section>

      <PatientFollowupPanel
        :patient="patient"
        :plan-status-label="planStatusLabel"
        :cycle-label-from-days="cycleLabelFromDays"
        :channel-label="channelLabel"
        :tracking-status-label="trackingStatusLabel"
        :task-type-label="taskTypeLabel"
        :report-db-status-label="reportDbStatusLabel"
        :can-create-report-followup="canCreateReportFollowup"
        :is-creating-report-followup="isCreatingReportFollowup"
        :existing-report-followup-task="existingReportFollowupTask"
        :can-operate="canOperatePatient"
        @update-follow-plan="$emit('update-follow-plan', $event)"
        @save-follow-plan="$emit('save-follow-plan')"
        @open-follow="$emit('open-follow')"
        @copy-task-link="$emit('copy-task-link', $event)"
        @view-report="$emit('view-report', $event)"
        @create-report-followup="$emit('create-report-followup', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PatientFollowupPanel from './PatientFollowupPanel.vue'

defineProps({
  patient: { type: Object, default: () => ({}) },
  editMode: { type: Boolean, default: false },
  canOperatePatient: { type: Boolean, default: true },
  canEditReportFollowupAdvice: { type: Boolean, default: true },
  departments: { type: Array, default: () => [] },
  doctors: { type: Array, default: () => [] },
  managers: { type: Array, default: () => [] },
  flowSteps: { type: Array, default: () => [] },
  latestRecordLabel: { type: String, default: '' },
  activePlanLabel: { type: String, default: '' },
  taskExecutionSummary: { type: String, default: '' },
  computedRisk: { type: Object, default: () => ({ level: '待评估', tone: 'g' }) },
  riskLayerItems: { type: Array, default: () => [] },
  advice: { type: Object, default: () => ({}) },
  adviceLocked: { type: Boolean, default: false },
  adviceGenerating: { type: Boolean, default: false },
  tongueSubmitting: { type: Boolean, default: false },
  tongueSyncing: { type: Boolean, default: false },
  tongueActionLabel: { type: String, default: '' },
  tongueStatusLabel: { type: String, default: '' },
  tongueQrUrl: { type: String, default: '' },
  planStatusLabel: { type: Function, required: true },
  cycleLabelFromDays: { type: Function, required: true },
  channelLabel: { type: Function, required: true },
  trackingStatusLabel: { type: Function, required: true },
  taskTypeLabel: { type: Function, required: true },
  reportDbStatusLabel: { type: Function, required: true },
  canCreateReportFollowup: { type: Function, required: true },
  isCreatingReportFollowup: { type: Function, required: true },
  existingReportFollowupTask: { type: Function, required: true },
  statusKey: { type: Function, required: true },
  statusLabel: { type: Function, required: true },
  isWecomBound: { type: Function, required: true },
  wecomStatusText: { type: Function, required: true },
  adviceStatusLabel: { type: Function, required: true },
})

const emit = defineEmits([
  'back',
  'edit-record',
  'start-patient-edit',
  'cancel-patient-edit',
  'save-patient',
  'update-patient',
  'view-report',
  'imaging-upload',
  'remove-asset',
  'copy-tongue-link',
  'start-tongue',
  'sync-tongue',
  'update-advice-content',
  'regenerate-advice',
  'save-advice',
  'submit-advice',
  'approve-advice',
  'update-report-followup-advice',
  'save-report-followup-advice',
  'submit-report-followup-advice',
  'create-report-followup',
  'update-follow-plan',
  'save-follow-plan',
  'open-follow',
  'copy-task-link',
])

const imagingInputRef = ref(null)

function updatePatient(field, value) {
  emit('update-patient', { field, value })
}

function reportFollowupAdvices(patient) {
  return patient?.reportFollowupAdvices || patient?.workspaceReportFollowupAdvices || patient?.followupAdvices || []
}

function latestReportFollowupAdvice(patient) {
  return reportFollowupAdvices(patient)[0] || null
}
</script>

<style scoped>
.patient-workspace{height:100%;min-height:0;overflow:auto;background:#f6f8fb;padding:14px;display:flex;flex-direction:column;gap:12px;scroll-padding-top:14px}
.card{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden}
.btn,.primary{height:36px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;color:#344054;padding:0 12px;font-weight:800;cursor:pointer}
.primary{border-color:#155eef;background:#155eef;color:#fff}
.btn:disabled,.primary:disabled{opacity:.6;cursor:not-allowed}
.btn-link-lite{border:0;background:transparent;color:#64748b;font-weight:950;font-size:12px;padding:4px 0;text-align:center;cursor:pointer}
.btn-link-lite:hover{color:#155eef}
.btn-link-lite:disabled{opacity:.55;cursor:not-allowed}
.muted{color:#64748b;font-weight:750}
.pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900}
.pill[data-tone="r"]{background:#fff1f2;color:#dc2626}
.pill[data-tone="o"]{background:#fff7ed;color:#c2410c}
.pill[data-tone="g"]{background:#ecfff3;color:#14843b}
.workspace-hero{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;flex-shrink:0;min-height:64px}
.workspace-id{display:flex;align-items:center;gap:12px;min-width:0}
.workspace-name{font-size:18px;font-weight:950;color:#0f172a}
.workspace-sub{font-size:12px;color:#64748b;margin-top:4px}
.workspace-badges{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.wecom-badge{display:inline-flex;align-items:center;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:900;background:#f8fafc;color:#64748b;white-space:nowrap}
.wecom-badge[data-on="true"]{background:#ecfdf5;color:#047857}
.status-tag{display:inline-flex;align-items:center;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:900;background:#f8fafc;color:#64748b;white-space:nowrap}
.status-tag[data-s="review"],.status-tag[data-s="reviewing"]{background:#eff6ff;color:#1d4ed8}
.status-tag[data-s="approved"],.status-tag[data-s="archived"],.status-tag[data-s="plan"],.status-tag[data-s="follow"]{background:#ecfdf5;color:#047857}
.workspace-flow{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;padding:10px 12px;flex-shrink:0;min-height:64px;box-sizing:border-box}
.workspace-flow-node{min-height:42px;border:1px solid #e6edf7;border-radius:10px;background:#fff;display:flex;align-items:center;justify-content:center;gap:8px;font-size:12px;font-weight:950;color:#64748b;line-height:1.2}
.workspace-flow-node[data-state="done"]{background:#ecfdf5;border-color:#bbf7d0;color:#047857}
.workspace-flow-node[data-state="current"]{background:#eff6ff;border-color:#bfdbfe;color:#1d4ed8}
.flow-dot{width:20px;height:20px;border-radius:999px;background:#f1f5f9;display:grid;place-items:center;font-size:11px}
.workspace-grid{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:12px;align-items:start}
.workspace-main{display:flex;flex-direction:column;gap:12px;min-width:0}
.flow-section{padding:14px}
.section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.section-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
.section-title{font-weight:950;color:#0f172a;font-size:14px}
.section-sub{font-size:12px;color:#64748b;margin-top:4px}
.profile-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.profile-note{margin-top:10px}
.profile-field{display:flex;flex-direction:column;gap:5px;font-size:12px;color:#64748b;font-weight:850;min-width:0}
.profile-field input,.profile-field select,.profile-field textarea{width:100%;box-sizing:border-box;border:1px solid #dbe5f2;border-radius:9px;background:#fff;padding:8px 10px;color:#0f172a;font-size:13px;font-weight:650}
.profile-field input[readonly],.profile-field textarea[readonly],.profile-field select:disabled{background:#f8fafc;color:#334155}
.profile-field textarea{min-height:76px;resize:vertical;line-height:1.6}
.profile-field.wide{grid-column:1/-1}
.record-report-card{margin-top:10px;border:1px solid #dbeafe;background:#eff6ff;border-radius:10px;padding:10px 12px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.record-report-card b{display:block;color:#1e3a8a;font-size:12px;margin-bottom:3px}
.record-report-card span{display:block;color:#334155;font-size:12px}
.workspace-summary-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:10px}
.workspace-summary-card{border:1px solid #e6edf7;border-radius:10px;background:#fff;padding:10px 12px;min-width:0}
.workspace-summary-card span{display:block;font-size:12px;color:#64748b;font-weight:850}
.workspace-summary-card b{display:block;font-size:22px;color:#0f172a;line-height:1.1;margin-top:4px}
.workspace-summary-card em{display:block;font-style:normal;font-size:11px;color:#94a3b8;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.upload-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;margin-top:12px}
.upload-panel{border:1px solid #e6edf7;border-radius:12px;background:#fbfdff;padding:12px;min-width:0}
.upload-title{font-weight:950;color:#0f172a}
.upload-sub{font-size:12px;color:#64748b;margin:4px 0 10px;line-height:1.5}
.hidden-input{display:none}
.file-list{display:grid;gap:8px;margin-top:10px}
.file-row{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid #eef2f7;border-radius:10px;background:#fff;padding:8px 10px;min-width:0}
.file-row b{display:block;font-size:12px;color:#0f172a;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.file-row span{display:block;font-size:11px;color:#94a3b8;margin-top:2px}
.empty-line{border:1px dashed #dbe5f2;border-radius:10px;padding:10px;color:#94a3b8;font-size:12px;background:#fff}
.tongue-h5-panel{border:1px solid #e6edf7;border-radius:10px;background:#fff;padding:10px;display:grid;gap:10px}
.tongue-h5-copy{display:flex;gap:8px;align-items:center;min-width:0}
.tongue-h5-copy input{height:32px;border:1px solid #dbe5f2;border-radius:8px;background:#f8fafc;padding:0 10px;color:#334155;font-size:12px;min-width:0;flex:1}
.tongue-h5-body{display:grid;grid-template-columns:104px minmax(0,1fr);gap:10px;align-items:center}
.tongue-qr{width:104px;height:104px;border:1px dashed #bfdbfe;border-radius:8px;background:#fff;display:grid;place-items:center;color:#94a3b8;font-size:12px;overflow:hidden}
.tongue-qr img{width:100%;height:100%;object-fit:contain}
.tongue-h5-help{display:grid;gap:5px;color:#64748b;font-size:12px;line-height:1.5}
.tongue-h5-help b{color:#0f172a;font-size:12px}
.tongue-diagnosis-bar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:10px;padding-top:10px;border-top:1px solid #e6edf7}
.tongue-status{font-size:12px;font-weight:850;color:#475569}
.tongue-result{margin-top:8px;border:1px solid #dbeafe;background:#eff6ff;border-radius:8px;padding:8px 10px;color:#1e3a8a;font-size:12px;line-height:1.6;white-space:pre-line}
.risk-layers{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.risk-layer{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:10px;min-width:0}
.risk-layer[data-tone="r"]{background:#fff1f2;border-color:#fecdd3}
.risk-layer[data-tone="o"]{background:#fff7ed;border-color:#fed7aa}
.risk-layer[data-tone="g"]{background:#f0fdf4;border-color:#bbf7d0}
.risk-layer-top{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:12px;color:#0f172a}
.risk-layer-top span{font-weight:950}
.risk-layer p{font-size:12px;color:#64748b;line-height:1.55;margin:8px 0 0}
.advice-status-row{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.advice-editor{width:100%;box-sizing:border-box;min-height:160px;border:1px solid #dbe5f2;border-radius:12px;padding:12px;font-size:13px;line-height:1.7;resize:vertical;color:#0f172a}
.advice-editor[readonly]{background:#f8fafc;color:#475569}
.lock-chip{display:inline-flex;align-items:center;border-radius:6px;background:#ecfdf5;color:#047857;padding:2px 8px;font-size:11px;font-weight:850}
.version-list{display:grid;gap:6px;margin-top:10px}
.version-row{display:grid;grid-template-columns:52px 90px 1fr;gap:8px;align-items:center;border:1px solid #eef2f7;border-radius:9px;background:#fff;padding:8px 10px;font-size:12px;color:#64748b}
.version-row b{color:#0f172a}
.final-report-box{border:1px solid #bbf7d0;border-radius:12px;background:#f0fdf4;padding:12px}
.final-report-meta{font-size:12px;color:#047857;font-weight:950;margin-bottom:8px}
.final-report-box p{margin:0;color:#0f172a;line-height:1.7;font-size:13px}
@media (max-width:1180px){
  .workspace-grid{grid-template-columns:1fr}
  .workspace-flow{grid-template-columns:repeat(3,minmax(0,1fr))}
  .workspace-summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .risk-layers{grid-template-columns:repeat(2,minmax(0,1fr))}
}
</style>
