<template>
  <div class="plan-page">
    <div class="plan-workbench">
      <section class="card plan-task-list">
        <div class="card-head one-line">
          <div class="card-title">
            选择患者
            <span class="muted count">· {{ patients.length }} 人</span>
          </div>
        </div>
        <div class="pad pad-lg search-pad">
          <div class="left-search-row">
            <input class="pf-in" :value="taskQuery" placeholder="搜索患者姓名/手机号" @input="$emit('update-task-query', $event.target.value)" />
            <button class="btn-link-lite" type="button" @click="$emit('reset-task-filters')">重置</button>
          </div>
        </div>
        <div class="pat-table">
          <div class="pat-rows">
            <div v-for="p in patients" :key="p.id" class="pat-row plan-patient-card" :data-active="p.id === activePatientId">
              <button type="button" class="pat-main" @click="$emit('select-patient', p)">
                <div class="patient-card-top">
                  <div>
                    <div class="pat-name"><b>{{ p.name }}</b><span class="muted">（{{ p.gender }}·{{ p.age }}岁）</span></div>
                    <div class="muted patient-meta">{{ p.nodules }} · {{ p.phoneMasked }}</div>
                  </div>
                  <span class="pill mini" :data-tone="p.riskTone">{{ p.risk }}</span>
                </div>
              </button>
            </div>
            <div v-if="!patients.length" class="muted empty-line">暂无匹配患者</div>
          </div>
        </div>
      </section>

      <section class="card plan-task-detail">
        <div class="card-head plan-editor-head">
          <div class="plan-detail-title">
            <div class="card-title">随访任务下发</div>
          </div>
          <div class="panel-tools">
            <button class="primary" type="button" @click="$emit('recommend')">推荐随访模板</button>
            <button class="btn-link-lite" type="button" @click="$emit('open-workflow')">随访知识库与模板</button>
          </div>
        </div>

        <div class="pad pad-lg">
          <div v-if="!activeTask" class="plan-empty">
            <b>请选择左侧患者</b>
            <span>选择后可在这里查看患者摘要、匹配模板并预览即将生成的任务。</span>
          </div>
          <template v-else>
            <section class="plan-step-strip">
              <div v-for="s in planDispatchSteps" :key="s.key" class="step-chip" :data-state="s.state">
                <span>{{ s.icon }}</span>
                <b>{{ s.title }}</b>
              </div>
            </section>

            <section class="detail-card patient-summary-card">
              <div class="patient-avatar-sm">患</div>
              <div class="patient-summary-main">
                <div class="patient-summary-title">
                  <b>{{ activeTask.patientName }}</b>
                  <span class="muted">（{{ activeTask.gender }} · {{ activeTask.age }}岁）</span>
                  <span class="pill mini" :data-tone="activeTask.riskTone">{{ activeTask.risk }}</span>
                </div>
                <div class="patient-summary-meta">
                  <span>{{ activeTask.nodules }}</span>
                  <span>{{ activeTask.phoneMasked }}</span>
                  <span>负责人：{{ activeTask.owner || '未分派' }}</span>
                </div>
              </div>
            </section>

            <div class="plan-editor-stack">
              <section class="detail-card template-section">
                <div class="detail-title-row">
                  <div>
                    <div class="detail-title">选择随访模板</div>
                  </div>
                  <button class="btn-link-lite" type="button" @click="$emit('open-workflow')">维护模板</button>
                </div>

                <div class="template-choice-list">
                  <button
                    v-for="tpl in templates"
                    :key="tpl.id"
                    type="button"
                    class="template-choice"
                    :class="{ active: tpl.id === selectedTemplateId }"
                    @click="$emit('select-template', tpl)"
                  >
                    <span class="template-choice-head">
                      <span class="template-choice-title">{{ tpl.name }}</span>
                      <span class="preview-status">{{ templateStatusLabel(tpl.status) }}</span>
                    </span>
                    <span class="template-choice-meta">
                      {{ noduleTypeLabel(tpl.nodule_type) }} · {{ riskLevelLabel(tpl.risk_level) }} · {{ tpl.cycle_days || 90 }}天 · {{ channelLabel(tpl.default_channel) }} · {{ (tpl.nodes || []).length }}个任务
                    </span>
                    <span v-if="tpl.description || tpl.default_reminder_strategy" class="template-choice-desc">{{ tpl.description || tpl.default_reminder_strategy }}</span>
                  </button>
                  <div v-if="!templates.length" class="muted empty-line">暂无可用模板，请先到随访知识库与模板页面创建并启用模板。</div>
                </div>
              </section>

              <section class="detail-card">
                <div class="detail-title-row">
                  <div>
                    <div class="detail-title">任务节点预览</div>
                  </div>
                  <select class="stage-select" :value="planDay" :disabled="planLoading || !!planError" @change="$emit('update-plan-day', $event.target.value)">
                    <option v-for="d in planDayList" :key="d" :value="d">第 {{ d.replace('day','') }} 天</option>
                  </select>
                </div>
                <div class="node-preview-list">
                  <div v-for="node in nodePreviews" :key="node.key" class="node-preview-row">
                    <div class="node-day">
                      <b>第 {{ node.day }} 天</b>
                      <span>{{ node.time }}</span>
                    </div>
                    <div class="node-main">
                      <div class="node-title">{{ node.name }}</div>
                      <div class="node-meta">
                        <span>{{ node.type }}</span>
                        <span>{{ node.patientAction }}</span>
                        <span>{{ node.aiAction }}</span>
                      </div>
                      <p v-if="node.message" class="node-message">{{ node.message }}</p>
                    </div>
                  </div>
                  <div v-if="!nodePreviews.length" class="muted empty-line">当前模板暂无任务节点，请先维护模板节点。</div>
                </div>

                <div class="confirm-bar">
                  <div>
                    <b>{{ selectedTemplate?.name || '未选择模板' }}</b>
                  </div>
                  <div class="confirm-actions">
                    <button class="btn-link-lite" type="button" @click="$emit('save-plan')" :disabled="saving || !selectedTemplate">
                      {{ saving ? '保存中...' : '保存设置' }}
                    </button>
                    <button class="primary" type="button" @click="$emit('simulate-plan')" :disabled="saving || !selectedTemplate">确认下发</button>
                  </div>
                </div>
              </section>
            </div>
          </template>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
defineProps({
  patients: { type: Array, default: () => [] },
  activePatientId: { type: [String, Number], default: '' },
  taskQuery: { type: String, default: '' },
  activeTask: { type: Object, default: null },
  planDispatchSteps: { type: Array, default: () => [] },
  templates: { type: Array, default: () => [] },
  selectedTemplateId: { type: [String, Number], default: '' },
  selectedTemplate: { type: Object, default: null },
  nodePreviews: { type: Array, default: () => [] },
  planDay: { type: String, default: 'day1' },
  planDayList: { type: Array, default: () => [] },
  planLoading: { type: Boolean, default: false },
  planError: { type: [String, Boolean, Object], default: '' },
  saving: { type: Boolean, default: false },
  templateStatusLabel: { type: Function, required: true },
  noduleTypeLabel: { type: Function, required: true },
  riskLevelLabel: { type: Function, required: true },
  channelLabel: { type: Function, required: true },
})

defineEmits([
  'update-task-query',
  'reset-task-filters',
  'select-patient',
  'recommend',
  'open-workflow',
  'select-template',
  'update-plan-day',
  'save-plan',
  'simulate-plan',
])
</script>

<style scoped>
.plan-page{flex:1;min-height:0;display:flex;flex-direction:column;background:#fff}
.plan-workbench{flex:1;min-height:0;display:grid;grid-template-columns:280px minmax(0,1fr);gap:12px;overflow:hidden}
.card{background:#fff;border:1px solid #e6edf7;border-radius:12px;box-shadow:0 1px 2px rgba(15,23,42,.04)}
.card-head{min-height:48px;padding:10px 12px;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;gap:10px}
.card-head.one-line{align-items:center}
.card-title{font-size:14px;font-weight:950;color:#0f172a}
.muted{color:#667085}
.count{font-size:12px;font-weight:700}
.pad{padding:12px}
.pad-lg{padding:12px}
.search-pad{padding-bottom:0}
.plan-task-list{min-height:0;display:flex;flex-direction:column;overflow:hidden}
.left-search-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;margin-bottom:8px}
.pf-in,.stage-select{height:34px;border:1px solid #d0d5dd;border-radius:8px;padding:0 10px;background:#fff;color:#172033;font-size:13px;min-width:0}
.pat-table{padding:10px 12px;display:flex;flex-direction:column;gap:10px;min-height:0;overflow:hidden}
.pat-rows{display:grid;gap:8px;overflow:auto;min-height:0;flex:1;scrollbar-width:thin}
.pat-row{display:grid;grid-template-columns:1fr;gap:0;align-items:stretch;border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px}
.pat-row[data-active="true"]{border-color:#155eef;background:#eef5ff}
.pat-main{border:none;background:transparent;text-align:left;cursor:pointer;min-width:0}
.patient-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}
.pat-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.patient-meta{font-size:12px;margin-top:4px}
.pill{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;font-weight:950;white-space:nowrap}
.pill.mini{height:22px;padding:0 8px;font-size:11px}
.pill[data-tone="r"]{background:#fff1f2;color:#be123c}
.pill[data-tone="o"]{background:#fff7ed;color:#c2410c}
.pill[data-tone="g"]{background:#f0fdf4;color:#15803d}
.plan-task-detail{min-height:0;display:flex;flex-direction:column;overflow:hidden}
.plan-task-detail .pad{overflow:auto;flex:1;min-height:0}
.plan-editor-head{align-items:flex-start}
.plan-detail-title{min-width:0;flex:1}
.panel-tools{display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
.btn-link-lite{border:0;background:transparent;color:#475467;font-size:12px;font-weight:850;cursor:pointer;padding:0}
.btn-link-lite:hover{color:#155eef}
.btn-link-lite:disabled{opacity:.55;cursor:not-allowed}
.primary{height:36px;border:1px solid #155eef;border-radius:8px;background:#155eef;color:#fff;padding:0 12px;font-weight:800;cursor:pointer}
.primary:disabled{opacity:.6;cursor:not-allowed}
.plan-empty{border:1px dashed #cbd5e1;background:#fff;border-radius:12px;padding:26px;display:grid;gap:6px;color:#64748b}
.plan-empty b{color:#0f172a;font-size:15px}
.plan-step-strip{display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap}
.step-chip{height:28px;border:1px solid #e6edf7;background:#fff;border-radius:999px;padding:0 10px;display:inline-flex;align-items:center;gap:6px;color:#64748b;font-size:12px;font-weight:900}
.step-chip span{width:18px;height:18px;border-radius:999px;background:#e2e8f0;color:#334155;display:grid;place-items:center;font-size:11px}
.step-chip[data-state="done"]{border-color:#bbf7d0;background:#f0fdf4;color:#15803d}
.step-chip[data-state="done"] span{background:#16a34a;color:#fff}
.step-chip[data-state="doing"]{border-color:#bfdbfe;background:#eff6ff;color:#155eef}
.step-chip[data-state="doing"] span{background:#155eef;color:#fff}
.detail-card{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:12px}
.patient-summary-card{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.patient-avatar-sm{width:34px;height:34px;border-radius:999px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-weight:950;flex-shrink:0}
.patient-summary-main{display:grid;gap:4px;min-width:0}
.patient-summary-title{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.patient-summary-title b{font-size:15px;color:#0f172a}
.patient-summary-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:12px;color:#64748b}
.plan-editor-stack{display:grid;gap:12px}
.detail-title{font-weight:950;color:#0f172a;margin-bottom:6px}
.detail-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:10px}
.template-choice-list{display:grid;gap:8px;grid-template-columns:repeat(2,minmax(0,1fr))}
.template-choice{border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 12px;text-align:left;display:grid;gap:5px;cursor:pointer}
.template-choice.active{border-color:#155eef;background:#eff6ff}
.template-choice-head{display:flex;align-items:center;justify-content:space-between;gap:8px;min-width:0}
.template-choice-title{font-weight:950;color:#0f172a}
.template-choice-meta,.template-choice-desc{font-size:12px;color:#64748b;line-height:1.5}
.preview-status{font-size:11px;color:#16a34a;font-weight:950;text-align:right}
.node-preview-list{display:grid;gap:8px}
.node-preview-row{border:1px solid #eef2f7;background:#fbfdff;border-radius:12px;padding:10px 12px;display:grid;grid-template-columns:82px minmax(0,1fr);gap:12px;align-items:start}
.node-day{display:grid;gap:3px}
.node-day b{font-size:12px;color:#0f172a}
.node-day span{font-size:12px;color:#64748b;font-weight:850}
.node-main{display:grid;gap:6px;min-width:0}
.node-title{font-weight:950;color:#0f172a;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.node-meta{display:flex;gap:6px;flex-wrap:wrap}
.node-meta span{border:1px solid #e6edf7;background:#fff;border-radius:999px;padding:3px 8px;font-size:11px;color:#475569;font-weight:850}
.node-message{margin:4px 0 0;color:#334155;font-size:13px;line-height:1.7;white-space:pre-wrap}
.confirm-bar{margin-top:12px;border-top:1px solid #eef2f7;padding-top:12px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.confirm-bar b{display:block;color:#0f172a;font-size:13px;margin-bottom:3px}
.confirm-actions{display:flex;align-items:center;gap:8px;flex-shrink:0}
.empty-line{font-size:12px;padding:8px 0}
@media (max-width: 980px){
  .plan-workbench{grid-template-columns:1fr}
  .template-choice-list{grid-template-columns:1fr}
}
</style>
