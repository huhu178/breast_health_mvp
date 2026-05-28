<template>
  <aside class="workspace-side">
    <section class="card side-flow-card">
      <div class="section-title">健康管理任务与后续管理</div>
      <div class="follow-plan-box">
        <label class="profile-field">
          <span>复查周期</span>
          <select :value="patient?.followPlan?.cycle" @change="updateFollowPlan('cycle', $event.target.value)">
            <option>3个月</option>
            <option>6个月</option>
            <option>12个月</option>
          </select>
        </label>
        <label class="profile-field">
          <span>触达方式</span>
          <select :value="patient?.followPlan?.channel" @change="updateFollowPlan('channel', $event.target.value)">
            <option>小程序</option>
            <option>电话</option>
            <option>企微</option>
            <option>小程序+电话</option>
          </select>
        </label>
        <label class="profile-field wide">
          <span>任务重点</span>
          <textarea :value="patient?.followPlan?.note" @input="updateFollowPlan('note', $event.target.value)" />
        </label>
        <button class="primary full" type="button" @click="$emit('save-follow-plan')">保存任务配置</button>
      </div>
    </section>

    <section class="card side-flow-card">
      <div class="section-title">管理记录</div>
      <div class="mgmt-log">
        <div v-for="log in patient?.managementLogs || []" :key="log.id" class="mgmt-log-row">
          <b>{{ log.action }}</b>
          <span>{{ log.at }} · {{ log.by }}</span>
          <p v-if="log.note">{{ log.note }}</p>
        </div>
      </div>
    </section>

    <section class="card side-flow-card">
      <div class="section-title">随访计划</div>
      <div class="chain-list">
        <div v-for="plan in patient?.workspacePlans || []" :key="plan.id" class="chain-row">
          <div>
            <b>{{ plan.name }}</b>
            <span>{{ planStatusLabel(plan.status) }} · {{ cycleLabelFromDays(plan.cycle_days) }} · {{ channelLabel(plan.channel) }}</span>
          </div>
          <em>{{ plan.activated_at || plan.created_at || '未启用' }}</em>
        </div>
        <div v-if="!(patient?.workspacePlans || []).length" class="empty-line">暂无随访计划</div>
      </div>
    </section>

    <section class="card side-flow-card">
      <div class="section-title">任务执行记录</div>
      <div class="chain-list">
        <div v-for="task in patient?.workspaceTasks || []" :key="task.id" class="chain-row" :data-alert="task.abnormal_flag">
          <div>
            <b>{{ task.title || taskTypeLabel(task.task_payload?.node?.task_type) }}</b>
            <span>{{ trackingStatusLabel(task.status) }} · {{ channelLabel(task.channel) }} · {{ task.scheduled_send_at || task.due_at || '未排期' }}</span>
          </div>
          <div class="chain-actions-mini">
            <em>{{ task.abnormal_flag ? '异常' : task.priority || 'normal' }}</em>
            <button v-if="task.public_checkin_path" class="btn-link-lite" type="button" @click="$emit('copy-task-link', task)">复制链接</button>
          </div>
        </div>
        <div v-if="!(patient?.workspaceTasks || []).length" class="empty-line">暂无执行任务</div>
      </div>
      <button class="btn full" type="button" @click="$emit('open-follow')" style="margin-top:10px">进入执行跟踪</button>
    </section>

    <section class="card side-flow-card">
      <div class="section-title">报告与舌诊链路</div>
      <div class="chain-list">
        <div v-for="report in patient?.workspaceReports || []" :key="report.id" class="chain-row">
          <div>
            <b>{{ report.report_code || `报告 #${report.id}` }}</b>
            <span>{{ reportDbStatusLabel(report.status) }} · {{ report.risk_level || '未评估' }}</span>
          </div>
          <div class="chain-actions-mini">
            <button class="btn-link-lite" type="button" @click="$emit('view-report', report.id)">查看</button>
            <button
              v-if="canCreateReportFollowup(report)"
              class="btn-link-lite"
              type="button"
              @click="$emit('create-report-followup', report.id)"
              :disabled="isCreatingReportFollowup(report.id) || !!existingReportFollowupTask(report.id)"
            >
              {{ existingReportFollowupTask(report.id) ? '已建随访' : '建随访' }}
            </button>
          </div>
        </div>
        <div v-if="!(patient?.workspaceReports || []).length" class="empty-line">暂无健康报告</div>
        <div class="integration-note">
          舌诊流程：B端生成 H5 单点登录链接 → 患者手机采集 → 结果回流到档案和报告。
        </div>
      </div>
    </section>
  </aside>
</template>

<script setup>
const props = defineProps({
  patient: { type: Object, default: null },
  planStatusLabel: { type: Function, required: true },
  cycleLabelFromDays: { type: Function, required: true },
  channelLabel: { type: Function, required: true },
  trackingStatusLabel: { type: Function, required: true },
  taskTypeLabel: { type: Function, required: true },
  reportDbStatusLabel: { type: Function, required: true },
  canCreateReportFollowup: { type: Function, required: true },
  isCreatingReportFollowup: { type: Function, required: true },
  existingReportFollowupTask: { type: Function, required: true },
})

const emit = defineEmits([
  'update-follow-plan',
  'save-follow-plan',
  'open-follow',
  'copy-task-link',
  'view-report',
  'create-report-followup',
])

function updateFollowPlan(field, value) {
  emit('update-follow-plan', { field, value })
}
</script>

<style scoped>
.workspace-side{display:grid;gap:14px;align-content:start}
.card{background:#fff;border:1px solid #e6edf7;border-radius:12px;box-shadow:0 1px 2px rgba(15,23,42,.04)}
.side-flow-card{padding:12px}
.section-title{font-size:14px;font-weight:950;color:#0f172a}
.follow-plan-box{display:grid;gap:10px;margin-top:10px}
.profile-field{display:grid;gap:5px;min-width:0}
.profile-field span{font-size:12px;color:#667085;font-weight:850}
.profile-field input,.profile-field select,.profile-field textarea{width:100%;border:1px solid #d0d5dd;border-radius:8px;padding:8px 10px;font-size:13px;color:#172033;background:#fff}
.profile-field textarea{min-height:74px;resize:vertical}
.profile-field.wide{grid-column:1/-1}
.btn,.primary{height:36px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;color:#344054;padding:0 12px;font-weight:800;cursor:pointer}
.primary{border-color:#155eef;background:#155eef;color:#fff}
.full{width:100%}
.mgmt-log{display:grid;gap:8px;margin-top:10px}
.mgmt-log-row{border:1px solid #eef2f7;border-radius:10px;padding:9px 10px;background:#fbfdff}
.mgmt-log-row b{display:block;font-size:12px;color:#0f172a}
.mgmt-log-row span{display:block;margin-top:3px;font-size:11px;color:#94a3b8}
.mgmt-log-row p{margin:6px 0 0;color:#475467;font-size:12px;line-height:1.5}
.chain-list{display:grid;gap:8px;margin-top:10px}
.chain-row{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;border:1px solid #eef2f7;border-radius:10px;background:#fff;padding:9px 10px;min-width:0}
.chain-row[data-alert="true"]{background:#fff1f2;border-color:#fecdd3}
.chain-row b{display:block;font-size:12px;color:#0f172a;line-height:1.35}
.chain-row span{display:block;font-size:11px;color:#64748b;margin-top:3px;line-height:1.4}
.chain-row em{font-style:normal;font-size:11px;color:#94a3b8;white-space:nowrap}
.chain-actions-mini{display:flex;align-items:center;justify-content:flex-end;gap:8px;flex-wrap:wrap;flex-shrink:0}
.btn-link-lite{border:0;background:transparent;color:#475467;font-size:12px;font-weight:850;cursor:pointer;padding:0}
.btn-link-lite:hover{color:#155eef}
.btn-link-lite:disabled{opacity:.55;cursor:not-allowed}
.empty-line{font-size:12px;color:#94a3b8;padding:8px 0}
.integration-note{border:1px dashed #dbe4f0;border-radius:10px;background:#fbfdff;color:#64748b;font-size:12px;line-height:1.6;padding:9px 10px}
</style>
