<template>
  <div class="pm-overview">
    <section class="card overview-left">
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-icon" style="background:#eff6ff;color:#2563eb">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div class="stat-body">
            <div class="stat-label">患者总数</div>
            <div class="stat-val">{{ queue.length }}</div>
            <div class="stat-sub" style="color:#2563eb">较昨日 +{{ Math.max(0, queue.length - 8) }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#fff1f2;color:#dc2626">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          </div>
          <div class="stat-body">
            <div class="stat-label">高风险患者</div>
            <div class="stat-val">{{ queue.filter((p) => p.riskTone === 'r').length }}</div>
            <div class="stat-sub" style="color:#dc2626">较昨日 +2</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#fffbeb;color:#d97706">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          </div>
          <div class="stat-body">
            <div class="stat-label">待处理报告</div>
            <div class="stat-val">{{ queue.filter((p) => statusKey(p) === 'review').length }}</div>
            <div class="stat-sub" style="color:#d97706">较昨日 -1</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#ecfdf5;color:#059669">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
          <div class="stat-body">
            <div class="stat-label">{{ reportTerms.toReview }}</div>
            <div class="stat-val">{{ queue.filter((p) => p.stage === 'review').length }}</div>
            <div class="stat-sub" style="color:#059669">较昨日 -1</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#f5f3ff;color:#7c3aed">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </div>
          <div class="stat-body">
            <div class="stat-label">待推送患者</div>
            <div class="stat-val">{{ queue.filter((p) => p.stage === 'push').length }}</div>
            <div class="stat-sub" style="color:#7c3aed">较昨日 +1</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#fff1f2;color:#e11d48">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <div class="stat-body">
            <div class="stat-label">异常待处理</div>
            <div class="stat-val">{{ queue.filter((p) => p.stage === 'abnormal').length }}</div>
            <div class="stat-sub" style="color:#e11d48">较昨日 +2</div>
          </div>
        </div>
      </div>

      <div class="q-filter-bar">
        <div class="q-filter-title">筛选条件</div>
        <div class="q-filter-row">
          <div class="q-filter-item">
            <label>姓名/手机号</label>
            <input class="q-filter-input" :value="search" placeholder="请输入姓名或手机号" @input="$emit('update-search', $event.target.value)" />
          </div>
          <div class="q-filter-item">
            <label>{{ scenario.personLabel }}来源</label>
            <select class="q-filter-select" :value="source" @change="$emit('update-source', $event.target.value)">
              <option value="">全部</option>
              <option v-for="src in scenario.sourceOptions" :key="src">{{ src }}</option>
            </select>
          </div>
          <div class="q-filter-item">
            <label>结节类型</label>
            <select class="q-filter-select" :value="nodule" @change="$emit('update-nodule', $event.target.value)">
              <option value="">全部</option>
              <option>乳腺结节</option>
              <option>肺部结节</option>
              <option>甲状腺结节</option>
              <option>乳腺+肺部结节</option>
              <option>乳腺+甲状腺结节</option>
              <option>肺部+甲状腺结节</option>
              <option>三合并结节</option>
            </select>
          </div>
          <div class="q-filter-item">
            <label>风险等级</label>
            <select class="q-filter-select" :value="risk" @change="$emit('update-risk', $event.target.value)">
              <option value="">全部</option>
              <option>高风险</option>
              <option>中风险</option>
              <option>低风险</option>
            </select>
          </div>
          <div class="q-filter-item">
            <label>当前状态</label>
            <select class="q-filter-select" :value="status" @change="$emit('update-status', $event.target.value)">
              <option value="">全部</option>
              <option value="gen">建立档案</option>
              <option value="review">{{ reportTerms.toReview }}</option>
              <option value="plan">任务待下发</option>
              <option value="follow">任务执行中</option>
              <option value="push">待推送</option>
              <option value="abnormal">异常待处理</option>
            </select>
          </div>
          <div class="q-filter-actions">
            <button class="btn" type="button" @click="$emit('reset-filters')">重置</button>
            <button class="primary" type="button">查询</button>
            <button class="primary" type="button" @click="$emit('new-record')">+ 新建档案</button>
          </div>
        </div>
      </div>

      <div class="q-table-head-row">
        <span class="muted">患者列表 共 {{ filteredQueue.length }} 条</span>
      </div>
      <div class="q-table-wrap">
        <table class="q-table">
          <thead>
            <tr>
              <th style="width:90px">患者姓名</th>
              <th style="width:130px">性别/年龄/手机号</th>
              <th style="width:160px">结节类型</th>
              <th style="width:72px">风险等级</th>
              <th style="width:100px">当前状态</th>
              <th style="width:80px">企微</th>
              <th style="width:72px">负责人</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in filteredQueue"
              :key="p.id"
              class="q-row"
              :class="{ active: p.id === activePatientId }"
              @click="$emit('select-patient', p.id)"
            >
              <td><b>{{ p.name }}</b></td>
              <td class="muted" style="font-size:11px">{{ p.gender }} / {{ p.age }}岁 / {{ p.phoneMasked }}</td>
              <td>
                <div style="display:flex;gap:3px;flex-wrap:wrap">
                  <span v-for="tag in noduleTags(p)" :key="tag.label" class="nodule-tag" :data-type="tag.type">{{ tag.label }}</span>
                </div>
              </td>
              <td><span class="pill" :data-tone="p.riskTone">{{ p.risk }}</span></td>
              <td><span class="status-tag" :data-s="statusKey(p)">{{ statusLabel(p) }}</span></td>
              <td><span class="wecom-badge" :data-on="isWecomBound(p)">{{ wecomStatusText(p) }}</span></td>
              <td class="muted">{{ p.owner }}</td>
              <td>
                <div style="display:flex;gap:8px">
                  <button class="tbl-act" type="button" @click.stop="$emit('open-workspace', p)">查看</button>
                  <button class="tbl-act" type="button" @click.stop="$emit('open-followup-plan', p)">任务</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pager">
        <span class="muted">共 {{ filteredQueue.length }} 条</span>
        <div class="pages">
          <button class="page-btn" type="button">‹</button>
          <button class="page-btn active" type="button">1</button>
          <button class="page-btn" type="button">2</button>
          <button class="page-btn" type="button">›</button>
        </div>
        <div class="muted">10 条/页</div>
      </div>
    </section>

    <aside class="overview-right">
      <div v-if="!queue.length" class="side-empty">加载中...</div>
      <section v-else-if="activePatient" class="card side-panel">
        <div class="card-head one-line">
          <div class="side-title">
            <div class="side-name">{{ activePatient.name }}</div>
            <div class="side-sub">{{ statusLabel(activePatient) }}</div>
          </div>
          <span class="pill" :data-tone="activePatient.riskTone">{{ activePatient.risk }}</span>
        </div>

        <div class="pad pad-lg">
          <div class="sec-h">患者详情</div>
          <div class="mini-kv2">
            <div class="kv2"><div class="k">性别</div><div class="v">{{ activePatient.gender }}</div></div>
            <div class="kv2"><div class="k">年龄</div><div class="v">{{ activePatient.age }}岁</div></div>
            <div class="kv2"><div class="k">手机号</div><div class="v">{{ activePatient.phoneMasked }}</div></div>
            <div class="kv2"><div class="k">来源</div><div class="v">{{ sourceLabel(activePatient.source) }}</div></div>
            <div class="kv2"><div class="k">负责人</div><div class="v">{{ ownerLabel(activePatient.owner) }}</div></div>
            <div class="kv2"><div class="k">企微</div><div class="v"><span class="wecom-badge" :data-on="isWecomBound(activePatient)">{{ wecomStatusText(activePatient) }}</span></div></div>
          </div>
          <div class="wecom-bind-row">
            <div class="wecom-bind-main">
              <b>{{ activePatient.wecomExternalUserid || activePatient.wecomUserid || '未绑定企业微信身份' }}</b>
              <span>{{ isWecomBound(activePatient) ? '可用于后续企微触达和患者会话识别' : '绑定 external_userid 后才能做真实企微随访' }}</span>
            </div>
            <div class="wecom-bind-actions">
              <button class="tbl-act" type="button" @click="$emit('open-wecom-bind', activePatient)">{{ isWecomBound(activePatient) ? '修改' : '绑定' }}</button>
              <button v-if="isWecomBound(activePatient)" class="tbl-act danger" type="button" @click="$emit('unbind-wecom', activePatient)">解绑</button>
            </div>
          </div>
        </div>

        <div class="panel-split"></div>

        <div class="pad pad-lg">
          <div class="sec-h">标签信息</div>
          <div class="tag-grid">
            <div class="tagline"><span class="t">结节类型</span><span class="v">{{ activePatient.nodules }}</span></div>
            <div class="tagline"><span class="t">风险等级</span><span class="pill mini" :data-tone="activePatient.riskTone">{{ activePatient.risk }}</span></div>
            <div class="tagline"><span class="t">当前状态</span><span class="tag2">{{ statusLabel(activePatient) }}</span></div>
          </div>
        </div>

        <div class="panel-split"></div>

        <div class="pad pad-lg">
          <div class="sec-h">下一步</div>
          <div class="side-explain">{{ nextHintV2(activePatient) }}</div>
        </div>

        <div class="panel-split"></div>

        <div class="pad pad-lg">
          <div class="sec-h">流程进度</div>
          <div class="flow5h">
            <div v-for="(n, i) in flowNodes(activePatient)" :key="n.k" class="flow5h-node" :data-state="n.state">
              <div class="pt">
                <span class="dot"></span>
                <span v-if="n.state === 'done'" class="check">✓</span>
              </div>
              <div class="lab">{{ n.label }}</div>
              <div v-if="i < 4" class="seg"></div>
            </div>
          </div>
        </div>

        <div class="panel-split"></div>

        <div class="pad pad-lg">
          <div class="sec-h">操作</div>
          <div class="ops">
            <template v-for="(a, i) in stageActions(activePatient)" :key="a.label + i">
              <button :class="a.primary ? 'primary full' : 'btn-link-lite'" type="button" :disabled="a.disabled" @click="a.onClick()">
                {{ a.label }}
              </button>
            </template>
          </div>
        </div>

        <div class="panel-split"></div>

        <div class="pad pad-lg">
          <div class="sec-h">最近动态</div>
          <div style="display:grid;gap:0">
            <div v-for="(t, i) in stageTimeline(activePatient)" :key="t.at + t.text + i" class="tl-row">
              <div class="tl-dot" :data-tone="t.tone"></div>
              <div style="min-width:0">
                <div style="font-size:12px;color:#0f172a;font-weight:850">{{ t.text }}</div>
                <div class="muted" style="font-size:11px;margin-top:2px">{{ t.at }}<span v-if="t.meta"> · {{ t.meta }}</span></div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </aside>
  </div>
</template>

<script setup>
defineProps({
  queue: { type: Array, default: () => [] },
  filteredQueue: { type: Array, default: () => [] },
  activePatientId: { type: [String, Number], default: '' },
  activePatient: { type: Object, default: null },
  reportTerms: { type: Object, required: true },
  scenario: { type: Object, required: true },
  search: { type: String, default: '' },
  source: { type: String, default: '' },
  nodule: { type: String, default: '' },
  risk: { type: String, default: '' },
  status: { type: String, default: '' },
  noduleTags: { type: Function, required: true },
  statusKey: { type: Function, required: true },
  statusLabel: { type: Function, required: true },
  sourceLabel: { type: Function, required: true },
  ownerLabel: { type: Function, required: true },
  isWecomBound: { type: Function, required: true },
  wecomStatusText: { type: Function, required: true },
  nextHintV2: { type: Function, required: true },
  flowNodes: { type: Function, required: true },
  stageActions: { type: Function, required: true },
  stageTimeline: { type: Function, required: true },
})

defineEmits([
  'update-search',
  'update-source',
  'update-nodule',
  'update-risk',
  'update-status',
  'reset-filters',
  'new-record',
  'select-patient',
  'open-workspace',
  'open-followup-plan',
  'open-wecom-bind',
  'unbind-wecom',
])
</script>

<style scoped>
.pm-overview{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:12px;padding:12px;background:#fff;overflow:hidden}
.overview-left{min-height:0;display:flex;flex-direction:column;overflow:hidden}
.overview-right{min-height:0;height:100%;line-height:1.5;display:flex;flex-direction:column;gap:12px;overflow-y:auto;overflow-x:hidden;padding-right:12px;padding-bottom:12px;box-sizing:border-box}

.card{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden}
.card-head{min-height:40px;height:auto;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:8px 12px;gap:10px;flex-wrap:wrap}
.card-head.one-line{flex-wrap:nowrap}
.primary,.btn{display:inline-flex;align-items:center;justify-content:center;border-radius:10px;padding:5px 10px;font-weight:950;cursor:pointer;min-height:32px;line-height:1.3;white-space:nowrap;font-size:13px}
.primary{background:#155eef;border:1px solid #155eef;color:#fff}
.btn{border:1px solid #d9e2ef;background:#fff;color:#475569}
.full{width:100%}
.muted{color:#64748b;font-weight:750}
.pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900}
.pill[data-tone="r"]{background:#fff1f2;color:#dc2626}
.pill[data-tone="o"]{background:#fff7ed;color:#c2410c}
.pill[data-tone="g"]{background:#ecfff3;color:#14843b}
.pill.mini{padding:2px 8px;font-size:11px}
.tag2{border:1px solid #cfe0ff;background:#eef5ff;color:#155eef;border-radius:999px;padding:3px 8px;font-weight:900;font-size:11px}

.stat-cards{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;padding:12px 12px 0}
.stat-card{display:flex;align-items:center;gap:10px;background:#f8fafc;border:1px solid #e6edf7;border-radius:10px;padding:12px 14px}
.stat-icon{width:40px;height:40px;border-radius:10px;display:grid;place-items:center;flex-shrink:0}
.stat-body{min-width:0}
.stat-label{font-size:11px;color:#64748b;font-weight:600;white-space:nowrap}
.stat-val{font-size:22px;font-weight:900;color:#111827;line-height:1.2}
.stat-sub{font-size:11px;font-weight:700;margin-top:2px}

.q-filter-bar{padding:12px 12px 0}
.q-filter-title{font-size:13px;font-weight:800;color:#374151;margin-bottom:8px}
.q-filter-row{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}
.q-filter-item{display:flex;flex-direction:column;gap:4px}
.q-filter-item label{font-size:11px;font-weight:700;color:#64748b}
.q-filter-input{height:32px;border:1px solid #d9e2ef;border-radius:6px;padding:0 10px;outline:none;min-width:160px;font-size:13px}
.q-filter-input:focus{border-color:#155eef;box-shadow:0 0 0 2px rgba(21,94,239,.1)}
.q-filter-select{height:32px;border:1px solid #d9e2ef;border-radius:6px;padding:0 10px;outline:none;font-size:13px;min-width:110px;background:#fff}
.q-filter-select:focus{border-color:#155eef}
.q-filter-actions{display:flex;gap:6px;align-items:flex-end;padding-bottom:0}

.q-table-head-row{display:flex;align-items:center;justify-content:space-between;padding:10px 12px 6px;font-size:13px}
.q-table-wrap{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:auto;flex:1}
.q-table{width:100%;border-collapse:collapse;font-size:13px}
.q-table thead tr{border-bottom:1px solid #eef2f7;background:#f8fafc}
.q-table th{padding:10px 12px;text-align:left;color:#64748b;font-weight:900;white-space:nowrap}
.q-table td{padding:10px 12px;border-bottom:1px solid #f1f5f9;white-space:nowrap}
.q-row{cursor:pointer}
.q-row:hover td{background:#f8fbff}
.q-row.active td{background:#eef5ff}
.q-row:last-child td{border-bottom:0}
.nodule-tag{display:inline-flex;align-items:center;border-radius:6px;padding:2px 7px;font-size:11px;font-weight:700;background:#eef5ff;color:#155eef}
.nodule-tag[data-type="lung"]{background:#ecfdf5;color:#15803d}
.nodule-tag[data-type="thyroid"]{background:#fff7ed;color:#c2410c}
.nodule-tag[data-type="breast"]{background:#fdf4ff;color:#a21caf}
.nodule-tag[data-type="triple"]{background:#fff1f2;color:#dc2626}
.status-tag{display:inline-flex;align-items:center;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:800}
.status-tag[data-s="gen"]{background:#eff6ff;color:#1d4ed8}
.status-tag[data-s="review"]{background:#fff7ed;color:#c2410c}
.status-tag[data-s="plan"]{background:#f5f3ff;color:#6d28d9}
.status-tag[data-s="follow"]{background:#ecfdf5;color:#059669}
.status-tag[data-s="push"]{background:#fdf4ff;color:#a21caf}
.status-tag[data-s="abnormal"]{background:#fff1f2;color:#dc2626}
.pager{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:10px 12px}
.pages{display:flex;gap:8px;align-items:center}
.page-btn{border:1px solid #d9e2ef;background:#fff;border-radius:10px;padding:5px 9px;color:#475569;font-weight:950;cursor:pointer;font-size:13px}
.page-btn.active{background:#155eef;color:#fff;border-color:#155eef}

.side-empty{display:flex;align-items:center;justify-content:center;height:120px;color:#94a3b8;font-size:13px}
.side-panel{overflow:hidden}
.side-panel .side-name{font-size:16px}
.side-panel .side-sub{font-size:12px}
.side-panel .pill{font-size:11px}
.side-panel .kv2 .k{font-size:11px}
.side-panel .kv2 .v{font-size:13px;font-weight:900}
.side-panel .tagline .t{font-size:11px}
.side-panel .tagline .v{font-size:12px}
.side-panel .side-explain{font-size:12px}
.side-panel .btn.full,.side-panel .primary.full{font-size:12px;min-height:34px}
.side-title{min-width:0;display:flex;flex-direction:column;gap:2px}
.side-name{font-weight:950;color:#0f172a}
.side-sub{color:#64748b;font-weight:850;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.side-explain{color:#334155;line-height:1.65;font-size:13px}
.pad{padding:8px 10px}
.pad.pad-lg{padding:12px 12px}
.panel-split{height:1px;background:#eef2f7}
.sec-h{font-weight:950;color:#0f172a;font-size:12px;margin-bottom:8px}
.mini-kv2{display:grid;grid-template-columns:1fr 1fr;gap:10px 12px}
.kv2 .k{color:#94a3b8;font-size:12px;font-weight:850}
.kv2 .v{margin-top:4px;font-weight:900;color:#0f172a;line-height:1.35}
.wecom-badge{display:inline-flex;align-items:center;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:900;background:#f8fafc;color:#64748b;white-space:nowrap}
.wecom-badge[data-on="true"]{background:#ecfdf5;color:#047857}
.wecom-bind-row{margin-top:12px;border:1px solid #eef2f7;border-radius:10px;background:#fbfdff;padding:10px;display:flex;align-items:center;justify-content:space-between;gap:10px}
.wecom-bind-main{min-width:0;display:grid;gap:3px}
.wecom-bind-main b{font-size:12px;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.wecom-bind-main span{font-size:12px;color:#64748b;line-height:1.45}
.wecom-bind-actions{display:flex;gap:8px;align-items:center;flex-shrink:0}
.tag-grid{display:grid;gap:10px}
.tagline{display:flex;align-items:center;justify-content:space-between;gap:10px}
.tagline .t{color:#94a3b8;font-size:12px;font-weight:850}
.tagline .v{font-weight:900;color:#0f172a;line-height:1.35;text-align:right}
.flow5h{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;align-items:start}
.flow5h-node{position:relative;display:grid;grid-template-rows:18px auto;justify-items:center;min-width:0}
.flow5h-node .pt{position:relative;width:18px;height:18px;display:grid;place-items:center}
.flow5h-node .dot{width:10px;height:10px;border-radius:50%;background:#cbd5e1;display:block}
.flow5h-node .check{position:absolute;inset:0;display:grid;place-items:center;font-size:12px;font-weight:950;color:#16a34a}
.flow5h-node .lab{margin-top:8px;font-size:11px;font-weight:900;color:#94a3b8;text-align:center;line-height:1.25;white-space:normal;word-break:break-all;max-width:72px;min-height:28px}
.flow5h-node .seg{position:absolute;top:8px;left:50%;right:-50%;height:2px;background:#e5e7eb}
.flow5h-node[data-state="done"] .dot{background:#16a34a}
.flow5h-node[data-state="done"] .lab{color:#14843b}
.flow5h-node[data-state="done"] .seg{background:#16a34a}
.flow5h-node[data-state="current"] .dot{background:#155eef}
.flow5h-node[data-state="current"] .lab{color:#155eef}
.flow5h-node[data-state="current"] .seg{background:linear-gradient(90deg,#155eef 0%,#e5e7eb 70%)}
.ops{display:grid;gap:8px}
.tbl-act{border:0;background:transparent;color:#155eef;font-size:12px;font-weight:700;padding:0;cursor:pointer}
.tbl-act:hover{color:#0f4fd4;text-decoration:underline}
.tbl-act.danger{color:#dc2626}
.tbl-act.danger:hover{color:#b91c1c}
.btn-link-lite{border:0;background:transparent;color:#64748b;font-weight:950;font-size:12px;padding:4px 0;text-align:center;cursor:pointer}
.btn-link-lite:hover{color:#155eef}
.tl-row{display:grid;grid-template-columns:16px 1fr;gap:10px;align-items:start;padding:8px 0;border-top:1px solid #f1f5f9}
.tl-row:first-child{border-top:0;padding-top:0}
.tl-dot{width:8px;height:8px;border-radius:50%;margin-top:3px;flex-shrink:0}
.tl-dot[data-tone="b"]{background:#5b8ff9}
.tl-dot[data-tone="g"]{background:#16a34a}
.tl-dot[data-tone="r"]{background:#ef4444}
.tl-dot[data-tone="o"]{background:#f97316}
.tl-dot[data-tone="p"]{background:#8b5cf6}
.tl-dot[data-tone="y"]{background:#f59e0b}
</style>
