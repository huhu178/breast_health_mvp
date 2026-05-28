<template>
  <div class="follow-phone-col">
    <div class="phone-preview-label">
      <span>Day {{ planDay.replace('day','') }} 随访内容预览</span>
      <span class="muted send-rhythm">发送节奏：上午 09:00 · 晚间提醒 20:00</span>
    </div>
    <div class="device-outer-lg">
      <div class="device-btn-l btn-top-1"></div>
      <div class="device-btn-l btn-top-2"></div>
      <div class="device-btn-l btn-top-3"></div>
      <div class="device-btn-r btn-top-2"></div>
      <div class="device-body">
        <div class="device-notch">
          <div class="device-camera"></div>
          <div class="device-speaker"></div>
        </div>
        <div class="device-screen">
          <div class="screen-status">
            <span>09:41</span>
            <span class="screen-icons">
              <svg viewBox="0 0 24 24" width="11" height="11" fill="currentColor"><path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/></svg>
              <svg viewBox="0 0 16 10" width="18" height="11" fill="currentColor"><rect x="0" y="1" width="13" height="8" rx="2" fill="none" stroke="currentColor" stroke-width="1.2"/><rect x="1" y="2" width="9" height="6" rx="1"/><rect x="13.5" y="3.5" width="2" height="3" rx="1"/></svg>
            </span>
          </div>
          <div class="screen-topbar">
            <span class="screen-back">‹</span>
            <div class="screen-contact">
              <div class="screen-avatar" :style="{ background: currentAssistant?.bg, color: currentAssistant?.color }">{{ currentAssistant?.ico }}</div>
              <div>
                <div class="screen-name">{{ currentAssistant?.name }}</div>
                <div class="screen-sub">{{ patient?.name }} · 健康随访</div>
              </div>
            </div>
            <span class="screen-more">···</span>
          </div>
          <div class="screen-chat-lg">
            <div class="screen-date-divider">今天</div>
            <template v-for="(msg, i) in chatMessages" :key="i">
              <div v-if="msg.from === 'ai'" class="sc-msg ai">
                <div class="sc-avatar" :style="{ background: currentAssistant?.bg, color: currentAssistant?.color }">{{ currentAssistant?.ico }}</div>
                <div class="sc-bubble ai-bubble">{{ msg.text }}</div>
              </div>
              <div v-else-if="msg.type === 'card'" class="sc-msg ai">
                <div class="sc-avatar" :style="{ background: currentAssistant?.bg, color: currentAssistant?.color }">{{ currentAssistant?.ico }}</div>
                <div class="sc-card">
                  <div class="sc-card-ico">{{ msg.ico }}</div>
                  <div class="sc-card-body">
                    <div class="sc-card-title">{{ msg.title }}</div>
                    <div class="sc-card-sub">{{ msg.sub }}</div>
                  </div>
                  <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="#94a3b8" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
                </div>
              </div>
              <div v-else class="sc-msg patient">
                <div class="sc-bubble patient-bubble">{{ msg.text }}</div>
                <div class="sc-avatar patient-av">患</div>
              </div>
            </template>
          </div>
          <div class="screen-input-bar">
            <div class="screen-input-field">发送消息...</div>
            <button class="screen-send-btn" type="button">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4z"/></svg>
            </button>
          </div>
        </div>
        <div class="device-home-bar-wrap"><div class="device-home-bar"></div></div>
      </div>
    </div>
  </div>

  <div class="follow-ctrl-col">
    <section class="assist-focus card">
      <div class="card-head">
        <div class="card-title">A. AI助手策略中心</div>
        <span class="assist-state" :data-tone="assistantStatus(currentAssistant?.key)">
          {{ assistantStatus(currentAssistant?.key) === 'g' ? '当前策略已启用' : '待启用' }}
        </span>
      </div>
      <div class="assist-focus-body">
        <div class="strategy-box">
          <div class="strategy-modules">
            <button
              v-for="a in assistants.slice(0, 6)"
              :key="a.key"
              type="button"
              class="strategy-module"
              :class="{ active: activeAssistant === a.key }"
              @click="$emit('update-active-assistant', a.key)"
            >
              <span class="assist-ico" :style="{ background: a.bg, color: a.color }">{{ a.ico }}</span>
              <b>{{ a.shortName }}</b>
              <em v-if="assistantStatus(a.key)==='g'">推荐</em>
            </button>
          </div>
          <div class="strategy-current">当前生成策略：{{ currentAssistant?.shortName }} + {{ patient?.risk }} + Day {{ planDay.replace('day','') }} 随访阶段</div>
        </div>

        <div class="content-config">
          <div class="assist-selector-title">B. 知识库来源与内容配置</div>
          <div class="config-list">
            <div v-for="row in contentRows" :key="row.key" class="config-row">
              <span class="config-dot" :data-on="row.enabled"></span>
              <div class="config-main">
                <b>{{ row.label }}</b>
                <span>{{ row.reason }}</span>
              </div>
              <button class="kb-act" type="button" @click="$emit('enable-kb', row.key)">{{ row.enabled ? '已加入' : '加入模块' }}</button>
            </div>
          </div>
        </div>

        <div class="generated-panel">
          <div class="assist-selector-title">C. 今日随访内容明细 <span class="muted">（已生成 {{ generatedRows.length }} 项）</span></div>
          <div class="generated-table">
            <div class="generated-head">
              <span>序号</span>
              <span>模块名称</span>
              <span>内容类型</span>
              <span>来源</span>
              <span>关联助手</span>
              <span>状态</span>
              <span>操作</span>
            </div>
            <div v-for="(row, idx) in generatedRows" :key="row.key" class="generated-row">
              <span>{{ idx + 1 }}</span>
              <b>{{ row.name }}</b>
              <span>{{ row.type }}</span>
              <span>{{ row.source }}</span>
              <span>{{ row.assistant }}</span>
              <span class="generated-state">已加入</span>
              <button class="tbl-act" type="button">预览</button>
            </div>
          </div>
        </div>

        <div class="follow-bottom-actions">
          <button class="btn" type="button">查看生成逻辑</button>
          <button class="btn" type="button">重新推荐</button>
          <button class="btn" type="button">保存配置</button>
          <button class="primary" type="button">预览下发</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
defineProps({
  planDay: { type: String, default: 'day1' },
  patient: { type: Object, default: null },
  currentAssistant: { type: Object, default: null },
  chatMessages: { type: Array, default: () => [] },
  assistants: { type: Array, default: () => [] },
  activeAssistant: { type: String, default: '' },
  contentRows: { type: Array, default: () => [] },
  generatedRows: { type: Array, default: () => [] },
  assistantStatus: { type: Function, required: true },
})

defineEmits(['update-active-assistant', 'enable-kb'])
</script>

<style scoped>
.follow-phone-col,.follow-ctrl-col{display:none}
.card{background:#fff;border:1px solid #e6edf7;border-radius:12px;box-shadow:0 1px 2px rgba(15,23,42,.04)}
.card-head{min-height:48px;padding:10px 12px;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;gap:10px}
.card-title{font-size:14px;font-weight:950;color:#0f172a}
.muted{color:#64748b;font-weight:750}
.btn,.primary{height:36px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;color:#344054;padding:0 12px;font-weight:800;cursor:pointer}
.primary{border-color:#155eef;background:#155eef;color:#fff}
.tbl-act,.kb-act{border:0;background:transparent;color:#155eef;font-size:12px;font-weight:850;cursor:pointer;padding:0}
.phone-preview-label{width:min(520px,100%);display:flex;justify-content:space-between;align-items:center;padding:0 12px;font-size:12px;font-weight:850;color:#334155}
.send-rhythm{font-size:11px}
.device-outer-lg{position:relative;width:330px;flex-shrink:0;align-self:center;margin-top:12px}
.device-btn-l{position:absolute;left:-5px;width:4px;height:28px;background:#2d3748;border-radius:2px 0 0 2px}
.device-btn-r{position:absolute;right:-5px;width:4px;height:42px;background:#2d3748;border-radius:0 2px 2px 0}
.btn-top-1{top:100px}.btn-top-2{top:140px}.btn-top-3{top:180px}
.device-body{background:#1a1a2e;border-radius:36px;padding:8px;box-shadow:0 0 0 2px #2d3748,0 16px 48px rgba(0,0,0,.5),inset 0 0 0 1px rgba(255,255,255,.06)}
.device-notch{display:flex;align-items:center;justify-content:center;gap:7px;height:20px;margin-bottom:3px}
.device-camera{width:8px;height:8px;border-radius:50%;background:#0d0d1a;border:2px solid #2d3748}
.device-speaker{width:44px;height:4px;border-radius:999px;background:#0d0d1a}
.device-screen{background:#fff;border-radius:24px;overflow:hidden;display:flex;flex-direction:column}
.device-home-bar-wrap{display:flex;justify-content:center;padding:7px 0 3px}
.device-home-bar{width:80px;height:3px;background:#3d3d5c;border-radius:999px}
.screen-status{background:#f8fafc;padding:4px 12px;display:flex;justify-content:space-between;align-items:center;font-size:10px;font-weight:850;color:#334155}
.screen-icons{display:flex;gap:4px;align-items:center}
.screen-topbar{background:#fff;padding:7px 10px;display:flex;align-items:center;gap:7px;border-bottom:1px solid #eef2f7}
.screen-back{font-size:18px;color:#155eef;font-weight:900;cursor:pointer;flex-shrink:0;line-height:1}
.screen-contact{display:flex;align-items:center;gap:7px;flex:1}
.screen-avatar,.sc-avatar{border-radius:50%;display:grid;place-items:center;font-weight:950;flex-shrink:0}
.screen-avatar{width:26px;height:26px;font-size:11px}
.screen-name{font-weight:950;color:#0f172a;font-size:12px}
.screen-sub{font-size:10px;color:#94a3b8;margin-top:1px}
.screen-more{color:#94a3b8;font-size:15px;letter-spacing:1px}
.screen-chat-lg{background:#f3f6fb;padding:8px;display:flex;flex-direction:column;gap:7px;overflow-y:auto;flex:1;min-height:0;max-height:580px}
.screen-date-divider{text-align:center;font-size:10px;color:#94a3b8;padding:2px 0 4px}
.screen-input-bar{background:#fff;border-top:1px solid #eef2f7;padding:6px 8px;display:flex;align-items:center;gap:6px}
.screen-input-field{flex:1;height:28px;border:1px solid #e6edf7;border-radius:14px;background:#f8fafc;padding:0 10px;font-size:11px;color:#94a3b8;display:flex;align-items:center}
.screen-send-btn{width:28px;height:28px;border-radius:50%;background:#155eef;border:0;color:#fff;display:grid;place-items:center;cursor:pointer;flex-shrink:0}
.sc-msg{display:flex;gap:6px;align-items:flex-start}
.sc-msg.patient{flex-direction:row-reverse}
.sc-avatar{width:24px;height:24px;font-size:10px}
.patient-av{background:#16a34a;color:#fff}
.sc-bubble{border-radius:10px;padding:7px 9px;font-size:11px;line-height:1.55;max-width:78%}
.ai-bubble{background:#fff;color:#334155;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.patient-bubble{background:#d1fae5;color:#065f46}
.sc-card{background:#fff;border:1px solid #e6edf7;border-radius:9px;padding:8px 10px;display:flex;align-items:center;gap:8px;cursor:pointer;max-width:78%;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.sc-card-ico{font-size:16px;flex-shrink:0}
.sc-card-body{flex:1;min-width:0}
.sc-card-title{font-weight:950;color:#0f172a;font-size:11px}
.sc-card-sub{font-size:10px;color:#94a3b8;margin-top:1px}
.assist-state{font-size:11px;font-weight:950;border-radius:999px;padding:3px 10px;background:#f1f5f9;color:#64748b;white-space:nowrap}
.assist-state[data-tone="g"]{background:#ecfff3;color:#14843b}
.assist-state[data-tone="o"]{background:#fff7ed;color:#c2410c}
.assist-focus{flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden}
.assist-focus-body{padding:12px 12px 14px;display:grid;gap:10px;min-height:0;overflow:auto}
.strategy-box,.content-config,.generated-panel{background:#fff;border:1px solid #e6edf7;border-radius:10px;padding:10px 12px;box-shadow:0 4px 12px rgba(15,23,42,.04)}
.assist-selector-title{font-size:12px;font-weight:600;color:#64748b;margin-bottom:8px}
.strategy-modules{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.strategy-module{position:relative;border:1px solid #e6edf7;border-radius:10px;background:#fff;min-height:72px;padding:8px 6px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;cursor:pointer}
.strategy-module.active{border-color:#155eef;background:#eef5ff;box-shadow:0 0 0 2px rgba(21,94,239,.10)}
.strategy-module b{font-size:11px;color:#0f172a;line-height:1.2}
.strategy-module em{position:absolute;top:5px;right:5px;font-style:normal;font-size:10px;color:#16a34a;font-weight:950}
.assist-ico{width:32px;height:32px;border-radius:9px;display:grid;place-items:center;font-weight:950;font-size:13px;flex-shrink:0}
.strategy-current{margin-top:8px;border-top:1px solid #eef2f7;padding-top:8px;font-size:12px;color:#334155;line-height:1.5}
.config-list{display:grid;gap:8px}
.config-row{display:grid;grid-template-columns:14px minmax(0,1fr) auto;gap:8px;align-items:center;border:1px solid #eef2f7;background:#fbfdff;border-radius:10px;padding:8px}
.config-dot{width:10px;height:10px;border-radius:999px;background:#cbd5e1}
.config-dot[data-on="true"]{background:#16a34a}
.config-main{display:grid;gap:2px;min-width:0}
.config-main b{font-size:12px;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.config-main span{font-size:11px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.generated-table{border:1px solid #eef2f7;border-radius:10px;overflow:auto;background:#fff}
.generated-head,.generated-row{display:grid;grid-template-columns:36px minmax(130px,1.4fr) 64px minmax(92px,1fr) 76px 52px 44px;gap:6px;align-items:center;padding:8px 10px;font-size:12px;min-width:520px}
.generated-head{background:#f8fafc;color:#64748b;font-weight:950}
.generated-row{border-top:1px solid #eef2f7;color:#334155}
.generated-row b{font-size:12px;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.generated-state{color:#16a34a;font-weight:950}
.follow-bottom-actions{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
</style>
