<template>
  <div class="follow-workbench">
    <div class="follow-stats-bar">
      <div class="follow-stat-item">
        <div class="follow-stat-label">任务执行中</div>
        <div class="follow-stat-value stat-blue">{{ stats.runningPatients || 0 }}</div>
      </div>
      <div class="follow-stat-div"></div>
      <div class="follow-stat-item">
        <div class="follow-stat-label">高风险</div>
        <div class="follow-stat-value stat-red">{{ stats.highRisk || 0 }}</div>
      </div>
      <div class="follow-stat-div"></div>
      <div class="follow-stat-item">
        <div class="follow-stat-label">中风险</div>
        <div class="follow-stat-value stat-orange">{{ stats.midRisk || 0 }}</div>
      </div>
      <div class="follow-stat-div"></div>
      <div class="follow-stat-item">
        <div class="follow-stat-label">低风险</div>
        <div class="follow-stat-value stat-green">{{ stats.lowRisk || 0 }}</div>
      </div>
      <div class="follow-stat-div"></div>
      <div class="follow-stat-item">
        <div class="follow-stat-label">今日待配置</div>
        <div class="follow-stat-value stat-purple">{{ stats.unconfigured || 0 }}</div>
      </div>
      <div class="follow-stat-div"></div>
      <div class="follow-stat-item">
        <div class="follow-stat-label">已配置随访</div>
        <div class="follow-stat-value stat-cyan">{{ stats.configured || 0 }}</div>
      </div>
      <div class="follow-stat-div"></div>
      <div class="follow-stat-item">
        <div class="follow-stat-label">当前筛选</div>
        <div class="follow-stat-value stat-slate">{{ patients.length }}</div>
      </div>
    </div>

    <section class="follow-compose-head card">
      <div>
        <div class="chain-eyebrow">AI 随访内容生成与预览</div>
        <div class="chain-title">随访内容由 AI 助手策略与知识库内容共同生成，支持可解释推荐、模块替换与预览下发。</div>
      </div>
      <div class="follow-flow">
        <div v-for="s in flowSteps" :key="s.title" class="follow-flow-step">
          <div class="follow-flow-ico">{{ s.icon }}</div>
          <div class="follow-flow-title">{{ s.title }}</div>
          <div class="follow-flow-sub">{{ s.sub }}</div>
        </div>
      </div>
    </section>

    <div class="follow-patient-col">
      <div class="fp-filters">
        <input class="fp-search" :value="search" placeholder="搜索姓名 / 手机号" @input="$emit('update-search', $event.target.value)" />
        <div class="fp-filter-row">
          <select class="fp-select" :value="riskFilter" @change="$emit('update-risk-filter', $event.target.value)">
            <option value="">全部风险</option>
            <option value="高风险">高风险</option>
            <option value="中风险">中风险</option>
            <option value="低风险">低风险</option>
          </select>
          <select class="fp-select" :value="stageFilter" @change="$emit('update-stage-filter', $event.target.value)">
            <option value="">全部阶段</option>
            <option v-for="t in stageOptions" :key="t.key" :value="t.key">{{ t.label }}</option>
          </select>
        </div>
        <div class="fp-count muted">共 {{ patients.length }} 人</div>
      </div>

      <div class="follow-patient-list">
        <button
          v-for="p in patients"
          :key="p.id"
          type="button"
          class="fp-row"
          :class="{ active: selectedPatientId === p.id }"
          @click="$emit('select-patient', p.id)"
        >
          <div class="fp-row-line fp-row-line--top">
            <div class="fp-row-left">
              <span class="fp-name">{{ p.name }}</span>
              <span class="fp-demog muted">{{ p.gender }}·{{ p.age }}岁</span>
            </div>
            <span class="pill mini fp-risk" :data-tone="p.riskTone">{{ p.risk }}</span>
          </div>
          <div class="fp-row-line fp-row-line--bottom">
            <div class="fp-row-left">
              <span class="fp-nodule">{{ p.nodules }}</span>
              <span class="fp-last muted">{{ lastTouchLabel(p) }}</span>
            </div>
            <span class="fp-stage-tag">{{ statusLabel(p) }}</span>
          </div>
        </button>
      </div>
    </div>

    <section class="tracking-list-col">
      <div class="tracking-head">
        <div>
          <div class="card-title">患者聊天记录</div>
          <div class="tracking-patient">企业微信 · {{ patient?.name || '未选择患者' }}</div>
        </div>
      </div>
      <div class="tracking-chat-card as-main">
        <div class="mini-phone">
          <div class="mini-phone-head">
            <span class="mini-back">‹</span>
            <div>
              <b>企业微信</b>
              <span>{{ patient?.name || '患者' }}</span>
            </div>
            <span class="mini-more">···</span>
          </div>
          <div class="mini-chat">
            <div class="mini-date">今天 {{ activeTask?.time || '09:00' }}</div>
            <div v-for="msg in messages" :key="msg.key" class="mini-msg" :class="msg.direction">
              <div class="mini-avatar">{{ msg.direction === 'inbound' ? '患' : '医' }}</div>
              <div class="mini-msg-main">
                <div class="mini-msg-name">{{ msg.sender }}</div>
                <div v-if="msg.type === 'image'" class="mini-image-card">
                  <div class="mini-image-placeholder">餐饮图片</div>
                  <span>{{ msg.content }}</span>
                </div>
                <div v-else class="mini-bubble">{{ msg.content }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="tracking-detail-col">
      <div class="tracking-head">
        <div>
          <div class="card-title">任务执行表</div>
          <div class="tracking-patient">{{ patient?.name || '未选择患者' }} · {{ patient?.nodules || '-' }}</div>
        </div>
        <button class="btn" type="button" @click="$emit('refresh')">刷新</button>
      </div>

      <div class="tracking-summary">
        <div><b>{{ trackingStats.total }}</b><span>总任务</span></div>
        <div><b>{{ trackingStats.waiting }}</b><span>待发送</span></div>
        <div><b>{{ trackingStats.running }}</b><span>执行中</span></div>
        <div><b>{{ trackingStats.alert }}</b><span>异常</span></div>
      </div>

      <div class="tracking-task-list compact">
        <template v-for="group in taskGroups" :key="group.day">
          <div class="tracking-day-title">第 {{ group.day }} 天</div>
          <button
            v-for="task in group.tasks"
            :key="task.id"
            type="button"
            class="tracking-task-row"
            :class="{ active: activeTask?.id === task.id }"
            @click="$emit('select-task', task.id)"
          >
            <div class="tracking-time">{{ task.time }}</div>
            <div class="tracking-main">
              <b>{{ task.title }}</b>
              <span>{{ task.messageBrief }}</span>
            </div>
            <span class="tracking-status" :data-status="task.status">{{ trackingStatusLabel(task.status) }}</span>
          </button>
        </template>
        <div v-if="!tasks.length" class="tracking-empty">
          暂无已生成任务。请先在“随访任务下发”中确认下发。
        </div>
      </div>

      <template v-if="activeTask">
        <div class="tracking-detail-card">
          <div class="tracking-detail-head">
            <div>
              <div class="card-title">{{ activeTask.title }}</div>
              <div class="tracking-patient">第 {{ activeTask.dayNum }} 天 · {{ activeTask.time }} · {{ activeTask.channel }}</div>
            </div>
            <span class="tracking-status big" :data-status="activeTask.status">{{ trackingStatusLabel(activeTask.status) }}</span>
          </div>

          <div class="tracking-kv-grid">
            <div><span>计划发送</span><b>{{ activeTask.scheduledAt || '-' }}</b></div>
            <div><span>实际发送</span><b>{{ activeTask.sentAt || '未发送' }}</b></div>
            <div><span>患者动作</span><b>{{ activeTask.patientAction || '-' }}</b></div>
            <div><span>AI处理</span><b>{{ activeTask.aiAction || '-' }}</b></div>
          </div>

          <div class="tracking-block">
            <div class="tracking-block-title">执行过程</div>
            <div class="tracking-timeline">
              <div v-for="event in events" :key="event.key" class="tracking-event">
                <span></span>
                <div>
                  <b>{{ event.title }}</b>
                  <em>{{ event.time }}</em>
                  <p>{{ event.note }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <div v-else class="tracking-empty detail">请选择任务查看执行详情</div>
    </section>
  </div>
</template>

<script setup>
defineProps({
  stats: { type: Object, default: () => ({}) },
  flowSteps: { type: Array, default: () => [] },
  patients: { type: Array, default: () => [] },
  selectedPatientId: { type: [String, Number], default: '' },
  search: { type: String, default: '' },
  riskFilter: { type: String, default: '' },
  stageFilter: { type: String, default: '' },
  stageOptions: { type: Array, default: () => [] },
  patient: { type: Object, default: null },
  messages: { type: Array, default: () => [] },
  trackingStats: { type: Object, default: () => ({ total: 0, waiting: 0, running: 0, alert: 0 }) },
  taskGroups: { type: Array, default: () => [] },
  tasks: { type: Array, default: () => [] },
  activeTask: { type: Object, default: null },
  events: { type: Array, default: () => [] },
  lastTouchLabel: { type: Function, required: true },
  statusLabel: { type: Function, required: true },
  trackingStatusLabel: { type: Function, required: true },
})

defineEmits([
  'update-search',
  'update-risk-filter',
  'update-stage-filter',
  'select-patient',
  'refresh',
  'select-task',
])
</script>

<style scoped>
.follow-workbench{display:contents}
.card{background:#fff;border:1px solid #e6edf7;border-radius:12px;box-shadow:0 1px 2px rgba(15,23,42,.04)}
.card-title{font-size:14px;font-weight:950;color:#0f172a}
.muted{color:#64748b;font-weight:750}
.btn{height:36px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;color:#344054;padding:0 12px;font-weight:800;cursor:pointer}
.pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900}
.pill[data-tone="r"]{background:#fff1f2;color:#dc2626}
.pill[data-tone="o"]{background:#fff7ed;color:#c2410c}
.pill[data-tone="g"]{background:#ecfff3;color:#14843b}
.pill.mini{padding:2px 8px;font-size:11px}
.follow-stats-bar{display:none}
.follow-stat-item{flex:1;text-align:center;min-width:0}
.follow-stat-div{width:1px;height:32px;background:#e6edf7;flex-shrink:0;margin:0 4px}
.follow-stat-label{font-size:11px;color:#64748b;font-weight:600;white-space:nowrap}
.follow-stat-value{font-size:20px;font-weight:800;margin-top:2px;line-height:1}
.stat-blue{color:#2563eb}.stat-red{color:#dc2626}.stat-orange{color:#d97706}.stat-green{color:#059669}.stat-purple{color:#7c3aed}.stat-cyan{color:#0891b2}.stat-slate{color:#475569}
.follow-compose-head{grid-column:2;grid-row:1;display:none;grid-template-columns:1fr;gap:12px;align-items:center;padding:12px 14px;min-height:0}
.chain-eyebrow{font-size:12px;color:#155eef;font-weight:950;letter-spacing:.02em}
.chain-title{font-size:14px;color:#0f172a;font-weight:950;line-height:1.5}
.follow-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
.follow-flow-step{border:1px solid #e6edf7;background:#f8fafc;border-radius:10px;padding:8px;text-align:center;min-width:0}
.follow-flow-ico{width:30px;height:30px;border-radius:10px;background:#eef5ff;color:#155eef;display:grid;place-items:center;margin:0 auto 6px;font-weight:950;font-size:12px}
.follow-flow-title{font-size:12px;color:#0f172a;font-weight:950;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.follow-flow-sub{font-size:11px;color:#64748b;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.follow-patient-col{grid-column:1;grid-row:1 / span 2;display:flex;flex-direction:column;min-height:0;background:#fff;border:1px solid #e6edf7;border-radius:10px;overflow:hidden}
.fp-filters{flex-shrink:0;padding:8px 8px 6px;border-bottom:1px solid #eef2f7;display:flex;flex-direction:column;gap:5px;background:#f8fafc}
.fp-search{height:30px;border:1px solid #d9e2ef;border-radius:7px;padding:0 9px;font-size:12px;outline:none;background:#fff;color:#0f172a;width:100%;box-sizing:border-box}
.fp-search:focus{border-color:#155eef;box-shadow:0 0 0 2px rgba(21,94,239,.10)}
.fp-filter-row{display:grid;grid-template-columns:1fr 1fr;gap:5px}
.fp-select{height:26px;border:1px solid #d9e2ef;border-radius:6px;padding:0 6px;font-size:11px;outline:none;background:#fff;color:#334155;cursor:pointer}
.fp-count{font-size:11px;padding:0 1px}
.follow-patient-list{flex:1;overflow-y:auto;padding:4px;display:flex;flex-direction:column;gap:2px;scrollbar-width:thin}
.fp-row{border:1px solid transparent;border-left:3px solid transparent;border-radius:10px;background:#fff;padding:10px;text-align:left;cursor:pointer;transition:background .12s,border-color .12s;display:flex;flex-direction:column;justify-content:center;gap:6px;min-height:72px;line-height:1.25}
.fp-row:hover{background:#f8fbff;border-color:#e6edf7;border-left-color:#cfe0ff}
.fp-row.active{background:#eef5ff;border-color:#cfe0ff;border-left-color:#155eef}
.fp-row-line{display:flex;align-items:center;justify-content:space-between;gap:8px;min-width:0}
.fp-row-left{display:flex;align-items:baseline;gap:8px;min-width:0;flex:1}
.fp-name{font-weight:950;color:#0f172a;font-size:14px;flex-shrink:0}
.fp-demog{font-size:12px;white-space:nowrap}
.fp-risk{flex-shrink:0}
.fp-nodule{font-size:12px;color:#475569;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.fp-last{flex-shrink:0;font-size:11px;white-space:nowrap}
.fp-stage-tag{flex-shrink:0;font-size:11px;color:#64748b;background:#f1f5f9;border-radius:6px;padding:2px 8px;white-space:nowrap;max-width:150px;overflow:hidden;text-overflow:ellipsis}
.tracking-list-col,.tracking-detail-col{min-width:0;min-height:0;background:#fff;border:1px solid #e6edf7;border-radius:10px;display:flex;flex-direction:column}
.tracking-list-col{overflow:hidden}
.tracking-detail-col{overflow:auto;scrollbar-width:thin}
.tracking-head{min-height:54px;padding:12px 14px;border-bottom:1px solid #eef2f7;display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.tracking-patient{font-size:12px;color:#64748b;font-weight:800;margin-top:4px}
.tracking-summary{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #eef2f7}
.tracking-summary div{padding:10px 8px;text-align:center;border-right:1px solid #eef2f7}
.tracking-summary div:last-child{border-right:0}
.tracking-summary b{display:block;font-size:18px;color:#0f172a;line-height:1.2}
.tracking-summary span{display:block;font-size:11px;color:#64748b;font-weight:850;margin-top:3px}
.tracking-task-list{padding:10px;display:grid;gap:8px;overflow:auto;min-height:0}
.tracking-task-list.compact{flex:0 0 auto;max-height:340px;border-bottom:1px solid #eef2f7}
.tracking-day-title{font-size:12px;color:#334155;font-weight:950;padding:6px 2px 2px}
.tracking-task-row{border:1px solid #e6edf7;background:#fbfdff;border-radius:10px;padding:10px;display:grid;grid-template-columns:46px minmax(0,1fr) 82px;gap:10px;align-items:center;text-align:left;cursor:pointer}
.tracking-task-row:hover,.tracking-task-row.active{border-color:#155eef;background:#eff6ff}
.tracking-time{font-size:12px;color:#0f172a;font-weight:950}
.tracking-main{display:grid;gap:4px;min-width:0}
.tracking-main b{font-size:13px;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tracking-main span{font-size:12px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tracking-status{justify-self:end;border-radius:999px;padding:4px 8px;font-size:11px;font-weight:950;background:#f1f5f9;color:#475569;white-space:nowrap}
.tracking-status[data-status="scheduled"],.tracking-status[data-status="pending"],.tracking-status[data-status="assigned"]{background:#eff6ff;color:#155eef}
.tracking-status[data-status="sent"],.tracking-status[data-status="replied"],.tracking-status[data-status="executing"],.tracking-status[data-status="review"]{background:#f0fdf4;color:#15803d}
.tracking-status[data-status="completed"],.tracking-status[data-status="done"]{background:#ecfdf5;color:#047857}
.tracking-status[data-status="alert"],.tracking-status[data-status="manual_processing"],.tracking-status[data-status="failed"]{background:#fff1f2;color:#dc2626}
.tracking-status.big{font-size:12px;padding:6px 10px}
.tracking-empty{border:1px dashed #cbd5e1;border-radius:10px;padding:22px;text-align:center;color:#64748b;font-size:13px;font-weight:850;background:#fbfdff}
.tracking-empty.detail{margin:12px}
.tracking-detail-card,.tracking-chat-card{margin:10px;border:1px solid #eef2f7;border-radius:10px;background:#fff;overflow:hidden}
.tracking-detail-card{display:grid;gap:12px;padding:12px}
.tracking-detail-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.tracking-kv-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.tracking-kv-grid div{border:1px solid #eef2f7;border-radius:9px;background:#fbfdff;padding:9px 10px;min-width:0}
.tracking-kv-grid span{display:block;color:#64748b;font-size:11px;font-weight:850;margin-bottom:4px}
.tracking-kv-grid b{display:block;color:#0f172a;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tracking-block{display:grid;gap:8px}
.tracking-block-title{font-size:13px;color:#0f172a;font-weight:950}
.tracking-timeline{display:grid;gap:10px}
.tracking-event{display:grid;grid-template-columns:16px minmax(0,1fr);gap:8px}
.tracking-event>span{width:9px;height:9px;border-radius:999px;background:#155eef;margin-top:6px}
.tracking-event b{display:block;color:#0f172a;font-size:12px}
.tracking-event em{display:block;color:#64748b;font-size:11px;font-style:normal;margin-top:2px}
.tracking-event p{margin:4px 0 0;color:#334155;font-size:12px;line-height:1.6}
.tracking-chat-card{padding:12px;display:grid;gap:10px;min-height:0}
.tracking-chat-card.as-main{flex:1;padding:12px;min-height:0;overflow:hidden;border:0;margin:0}
.mini-phone{border:1px solid #e6edf7;border-radius:18px;background:#f3f6fb;overflow:hidden;box-shadow:0 8px 24px rgba(15,23,42,.06);display:flex;flex-direction:column;height:min(520px,58vh);min-height:320px}
.tracking-chat-card.as-main .mini-phone{height:100%;min-height:0}
.mini-phone-head{height:48px;background:#fff;border-bottom:1px solid #eef2f7;display:grid;grid-template-columns:32px minmax(0,1fr) 32px;align-items:center;color:#0f172a;padding:0 10px}
.mini-phone-head b{display:block;font-size:13px;text-align:center}
.mini-phone-head span:not(.mini-back):not(.mini-more){display:block;font-size:11px;color:#64748b;text-align:center;margin-top:2px}
.mini-back,.mini-more{font-size:20px;color:#64748b;font-weight:900;text-align:center}
.mini-chat{padding:14px;display:grid;gap:10px;overflow-y:auto;overflow-x:hidden;background:#f3f6fb;min-height:0;flex:1;scrollbar-width:thin;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}
.mini-date{text-align:center;color:#94a3b8;font-size:11px;font-weight:850;margin:2px 0 4px}
.mini-msg{display:flex;align-items:flex-start;gap:8px}
.mini-msg.inbound{flex-direction:row-reverse}
.mini-avatar{width:28px;height:28px;border-radius:8px;background:#155eef;color:#fff;display:grid;place-items:center;font-size:12px;font-weight:950;flex-shrink:0}
.mini-msg.inbound .mini-avatar{background:#16a34a}
.mini-msg-main{display:grid;gap:3px;max-width:78%}
.mini-msg.inbound .mini-msg-main{justify-items:end}
.mini-msg-name{font-size:11px;color:#94a3b8;font-weight:850}
.mini-bubble{border-radius:12px 12px 12px 4px;background:#fff;padding:10px 12px;color:#334155;font-size:13px;line-height:1.65;box-shadow:0 1px 3px rgba(15,23,42,.06);white-space:pre-wrap}
.mini-msg.inbound .mini-bubble{background:#d1fae5;color:#065f46;border-radius:12px 12px 4px 12px}
.mini-image-card{width:168px;border-radius:12px 12px 4px 12px;background:#d1fae5;padding:8px;display:grid;gap:6px;color:#065f46;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.mini-image-placeholder{height:96px;border-radius:8px;background:linear-gradient(135deg,#fde68a,#fb923c);display:grid;place-items:center;color:#7c2d12;font-size:13px;font-weight:950}
.mini-image-card span{font-size:11px;font-weight:850;color:#047857}
@media (max-width: 1500px){
  .follow-workbench{grid-template-columns:minmax(240px,280px) minmax(320px,.85fr) minmax(380px,1fr)}
  .follow-flow-step{padding:7px 6px}
}
@media (max-width: 1280px){
  .follow-workbench{grid-template-columns:250px minmax(0,1fr);grid-template-rows:auto minmax(420px,1fr)}
  .follow-patient-col{grid-column:1;grid-row:1 / span 2}
  .tracking-list-col{grid-column:2;grid-row:1}
  .tracking-detail-col{grid-column:2;grid-row:2}
}
</style>
