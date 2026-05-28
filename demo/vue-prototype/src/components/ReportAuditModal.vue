<template>
  <div class="rp-modal-mask" @click.self="$emit('close')">
    <div class="rp-modal">
      <div class="rp-modal-head">
        <div class="rp-modal-title">{{ title }}</div>
        <span class="muted">可直接编辑后点击审核通过</span>
        <button class="rp-modal-close" type="button" @click="$emit('close')">×</button>
      </div>
      <div class="rp-modal-body">
        <div v-if="status" class="rp-audit-state">
          <span class="status-tag" :data-s="status">{{ statusLabel }}</span>
          <span class="muted">当前版本：V{{ version || 1 }} · 已审核报告也可重新编辑并再次写入最终报告</span>
        </div>

        <div class="rp-audit-grid">
          <div class="rp-audit-block">
            <div class="rp-audit-label">影像报告建议</div>
            <textarea class="rp-audit-ta" :value="imagingAdvice" rows="5" @input="$emit('update:imagingAdvice', $event.target.value)" />
          </div>
          <div class="rp-audit-block">
            <div class="rp-audit-label">总体评估建议</div>
            <textarea class="rp-audit-ta" :value="overallAdvice" rows="5" @input="$emit('update:overallAdvice', $event.target.value)" />
          </div>
          <div class="rp-audit-block">
            <div class="rp-audit-label">风险评估建议</div>
            <textarea class="rp-audit-ta" :value="riskAdvice" rows="5" @input="$emit('update:riskAdvice', $event.target.value)" />
          </div>
          <div class="rp-audit-block">
            <div class="rp-audit-label">中医舌诊插入内容</div>
            <textarea
              class="rp-audit-ta"
              :value="tongueAdvice"
              rows="5"
              placeholder="舌诊完成后会从健康档案带入，也可以在这里编辑后写入最终报告。"
              @input="$emit('update:tongueAdvice', $event.target.value)"
            />
          </div>
        </div>

        <div class="modal-actions">
          <button class="primary" type="button" @click="$emit('finalize')" :disabled="finalizing">
            {{ finalizing ? '处理中...' : (wasReviewed ? '重新审核通过' : approveLabel) }}
          </button>
          <button class="btn" type="button" @click="$emit('close')">取消</button>
        </div>

        <div v-if="showFollowupNext" class="rp-followup-next">
          <div>
            <b>下一步：报告后首次随访</b>
            <span>{{ followupTask ? '该报告已创建首次随访任务，可进入执行跟踪或复制打卡链接。' : '审核通过后，可手动创建首次随访任务并生成公开打卡链接。' }}</span>
          </div>
          <div class="rp-followup-actions">
            <button v-if="!followupTask" class="primary" type="button" @click="$emit('create-followup')" :disabled="creatingFollowup">
              {{ creatingFollowup ? '创建中...' : '创建首次随访任务' }}
            </button>
            <button v-else class="btn" type="button" @click="$emit('open-followup')">打开执行跟踪</button>
            <button v-if="followupTask" class="btn" type="button" @click="$emit('copy-checkin-link')">复制打卡链接</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '报告审核' },
  status: { type: String, default: '' },
  statusLabel: { type: String, default: '' },
  version: { type: Number, default: 1 },
  imagingAdvice: { type: String, default: '' },
  overallAdvice: { type: String, default: '' },
  riskAdvice: { type: String, default: '' },
  tongueAdvice: { type: String, default: '' },
  finalizing: { type: Boolean, default: false },
  wasReviewed: { type: Boolean, default: false },
  approveLabel: { type: String, default: '审核通过' },
  showFollowupNext: { type: Boolean, default: false },
  followupTask: { type: Object, default: null },
  creatingFollowup: { type: Boolean, default: false },
})

defineEmits([
  'close',
  'finalize',
  'create-followup',
  'open-followup',
  'copy-checkin-link',
  'update:imagingAdvice',
  'update:overallAdvice',
  'update:riskAdvice',
  'update:tongueAdvice',
])
</script>

<style scoped>
.rp-modal-mask{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:9999;display:flex;align-items:center;justify-content:center}
.rp-modal{background:#fff;border-radius:12px;width:min(860px,96vw);max-height:88vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25)}
.rp-modal-head{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 20px;border-bottom:1px solid #e6edf7;flex-shrink:0}
.rp-modal-title{font-size:16px;font-weight:800;color:#111827}
.rp-modal-close{width:32px;height:32px;border:0;background:#f1f5f9;border-radius:8px;cursor:pointer;font-size:18px;color:#475569}
.rp-modal-body{padding:18px 20px;overflow:auto}
.muted{font-size:12px;color:#64748b}
.rp-audit-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.rp-audit-block{min-width:0}
.rp-audit-label{font-size:12px;font-weight:750;color:#334155;margin-bottom:4px}
.rp-audit-ta{width:100%;border:1px solid #d9e2ef;border-radius:6px;padding:8px 10px;font-size:13px;line-height:1.6;color:#1e293b;resize:vertical;outline:none;font-family:inherit}
.rp-audit-ta:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.1)}
.rp-audit-state{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:12px;padding:10px 12px;border:1px solid #e6edf7;border-radius:10px;background:#f8fafc}
.status-tag{display:inline-flex;align-items:center;border-radius:999px;padding:4px 9px;background:#eef2ff;color:#3730a3;font-size:11px;font-weight:900}
.status-tag[data-s="approved"],.status-tag[data-s="archived"]{background:#ecfdf5;color:#047857}
.status-tag[data-s="reviewing"]{background:#fff7ed;color:#c2410c}
.modal-actions{display:flex;gap:8px;margin-top:16px}
.btn,.primary{height:36px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;color:#344054;padding:0 12px;font-weight:800;cursor:pointer}
.primary{border-color:#155eef;background:#155eef;color:#fff}
.btn:disabled,.primary:disabled{opacity:.55;cursor:not-allowed}
.rp-followup-next{margin-top:14px;border:1px solid #dbeafe;border-radius:12px;background:#eff6ff;padding:12px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.rp-followup-next b{display:block;color:#0f172a;font-size:13px;margin-bottom:4px}
.rp-followup-next span{display:block;color:#475467;font-size:12px;line-height:1.5}
.rp-followup-actions{display:flex;align-items:center;justify-content:flex-end;gap:8px;flex-wrap:wrap;flex-shrink:0}
@media (max-width:720px){.rp-audit-grid{grid-template-columns:1fr}.rp-followup-next{display:grid}.rp-followup-actions{justify-content:flex-start}}
</style>
