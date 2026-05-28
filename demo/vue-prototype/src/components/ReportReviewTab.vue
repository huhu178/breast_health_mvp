<template>
  <div class="rp-page">
    <div class="stat-cards review-stat-cards">
      <div class="stat-card">
        <div class="stat-icon stat-blue">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">{{ reportTerms.pending }}</div>
          <div class="stat-val">{{ reports.filter(r => r.reportStatus !== '已审核').length }}</div>
          <div class="stat-sub stat-blue-text">较昨日 -2</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-purple">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">{{ reportTerms.parsing }}</div>
          <div class="stat-val">{{ reports.filter(r => r.aiStatus === 'AI解析中').length }}</div>
          <div class="stat-sub stat-purple-text">较昨日 +1</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-green">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">{{ reportTerms.parsed }}</div>
          <div class="stat-val">{{ reports.filter(r => r.aiStatus === '待审核').length }}</div>
          <div class="stat-sub stat-green-text">较昨日 +3</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-orange">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">{{ reportTerms.toGenerate }}</div>
          <div class="stat-val">{{ reports.filter(r => r.reportStatus === '待审核').length }}</div>
          <div class="stat-sub stat-orange-text">较昨日 +1</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-green">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">{{ reportTerms.toReview }}</div>
          <div class="stat-val">{{ reports.filter(r => r.reportStatus === '待审核').length }}</div>
          <div class="stat-sub stat-green-text">较昨日 -1</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-red">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-label">{{ reportTerms.abnormal }}</div>
          <div class="stat-val">{{ reports.filter(r => r.risk === '高风险').length }}</div>
          <div class="stat-sub stat-red-text">较昨日 +1</div>
        </div>
      </div>
    </div>

    <div class="rp-filter-bar card">
      <div class="rp-filter-row">
        <div class="rp-filter-item">
          <div class="rp-filter-label">{{ scenario.personLabel }}姓名/手机号</div>
          <input class="rp-filter-input" :value="search" placeholder="请输入姓名或手机号" @input="$emit('update-search', $event.target.value)" />
        </div>
        <div class="rp-filter-item">
          <div class="rp-filter-label">{{ scenario.personLabel }}来源</div>
          <select class="rp-filter-select" :value="source" @change="$emit('update-source', $event.target.value)">
            <option value="">{{ scenario.sourceOptions.join(' / ') }}</option>
            <option v-for="src in scenario.sourceOptions" :key="src">{{ src }}</option>
          </select>
        </div>
        <div class="rp-filter-item">
          <div class="rp-filter-label">结节类型</div>
          <select class="rp-filter-select" :value="nodule" @change="$emit('update-nodule', $event.target.value)">
            <option value="">乳腺结节等 7 种</option>
            <option>乳腺结节</option>
            <option>甲状腺结节</option>
            <option>肺部结节</option>
            <option>肺+甲</option>
            <option>肺+乳</option>
            <option>甲+乳</option>
            <option>三合并</option>
          </select>
        </div>
        <div class="rp-filter-item">
          <div class="rp-filter-label">风险等级</div>
          <select class="rp-filter-select" :value="risk" @change="$emit('update-risk', $event.target.value)">
            <option value="">高风险 / 中风险 / 低风险</option>
            <option>高风险</option>
            <option>中风险</option>
            <option>低风险</option>
          </select>
        </div>
        <div class="rp-filter-actions">
          <button class="btn" type="button" @click="$emit('reset-filters')">重置</button>
          <button class="primary" type="button">查询</button>
        </div>
      </div>
    </div>

    <div class="rp-body">
      <section class="card rp-list-card">
        <div class="card-head">
          <div class="card-title">{{ reportTerms.listTitle }} <span class="rp-count">共 268 条</span></div>
          <div class="list-actions">
            <button class="btn" type="button">
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>导出
            </button>
            <button class="btn" type="button">批量分派</button>
          </div>
        </div>
        <div class="q-table-wrap">
          <table class="q-table">
            <thead>
              <tr>
                <th class="col-patient">患者</th>
                <th class="col-nodule">结节类型</th>
                <th class="col-time">上传时间</th>
                <th class="col-ai">AI解析</th>
                <th class="col-risk">风险</th>
                <th class="col-owner">负责人</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in filteredReports" :key="r.id" class="q-row" :class="{ active: r.id === activeId }" @click="$emit('select-report', r.id)">
                <td>
                  <div class="patient-name">{{ r.name }}</div>
                  <div class="muted patient-sub">{{ r.gender }}/{{ r.age }}岁 · {{ r.phone }}</div>
                </td>
                <td><span class="nodule-tag" :data-type="r.noduleKey">{{ r.nodules }}</span></td>
                <td class="muted patient-sub">{{ r.uploadAt }}</td>
                <td><span class="rp-status-tag" :data-s="r.aiStatus">{{ r.aiStatus }}</span></td>
                <td><span class="pill" :data-tone="r.riskTone">{{ r.risk }}</span></td>
                <td class="muted">{{ r.owner }}</td>
                <td>
                  <div class="rp-row-actions">
                    <button class="tbl-act" type="button" @click.stop="$emit('view-report', r.id)">查看</button>
                    <button class="tbl-act" type="button" @click.stop="$emit('primary-action', r)" :disabled="generatingIds.has(r.rawPatientId || r.id)">{{ generatingIds.has(r.rawPatientId || r.id) ? '生成中...' : (r.isReportPlaceholder ? '去生成' : (r.reportStatus === '已审核' ? '复审/编辑' : reportTerms.reviewAction)) }}</button>
                    <button class="tbl-act" type="button" @click.stop="$emit('download-report', r.id)">下载</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pager">
          <span class="muted">共 {{ filteredReports.length }} 条</span>
          <div class="pages">
            <button class="page-btn" type="button">‹</button>
            <button class="page-btn active" type="button">1</button>
            <button class="page-btn" type="button">2</button>
            <button class="page-btn" type="button">3</button>
            <span class="muted">...</span>
            <button class="page-btn" type="button">27</button>
            <button class="page-btn" type="button">›</button>
          </div>
          <div class="muted">10 条/页</div>
        </div>
      </section>

      <aside class="rp-detail">
        <template v-if="activeReport">
          <section class="card">
            <div class="card-head"><div class="card-title">{{ reportTerms.detailTitle }}</div></div>
            <div class="rp-detail-info">
              <div class="rp-info-grid">
                <div class="rp-info-row"><span class="rp-ik">患者姓名：</span><span class="rp-iv">{{ activeReport.name }}</span></div>
                <div class="rp-info-row"><span class="rp-ik">来　　源：</span><span class="rp-iv">{{ activeReport.source }}</span></div>
                <div class="rp-info-row"><span class="rp-ik">性　　别：</span><span class="rp-iv">{{ activeReport.gender }}</span></div>
                <div class="rp-info-row"><span class="rp-ik">负 责 人：</span><span class="rp-iv">{{ activeReport.owner }}</span></div>
                <div class="rp-info-row"><span class="rp-ik">年　　龄：</span><span class="rp-iv">{{ activeReport.age }}岁</span></div>
                <div class="rp-info-row"><span class="rp-ik">报告类型：</span><span class="rp-iv">{{ activeReport.reportType }}</span></div>
                <div class="rp-info-row"><span class="rp-ik">手 机 号：</span><span class="rp-iv">{{ activeReport.phone }}</span></div>
                <div class="rp-info-row"><span class="rp-ik">上传时间：</span><span class="rp-iv">{{ activeReport.uploadAt }}</span></div>
              </div>
              <button class="rp-doc-btn" type="button">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>
              </button>
            </div>
          </section>

          <section class="card">
            <div class="card-head"><div class="card-title">{{ reportTerms.flowTitle }}</div></div>
            <div class="rp-flow">
              <div v-for="(s, i) in activeReport.flow" :key="s.label" class="rp-flow-step" :data-done="s.done" :data-cur="s.cur">
                <div class="rp-flow-dot">
                  <svg v-if="s.done" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg>
                  <span v-else>{{ i + 1 }}</span>
                </div>
                <div class="rp-flow-label">{{ s.label }}</div>
                <div class="rp-flow-time">{{ s.time }}</div>
              </div>
            </div>
          </section>

          <section class="card">
            <div class="card-head"><div class="card-title">快捷操作</div></div>
            <div class="rp-actions">
              <button class="primary" type="button" @click="$emit('primary-action', activeReport)">
                {{ activeReport.isReportPlaceholder ? '去生成报告' : (activeReport.reportStatus === '已审核' ? '复审/编辑报告' : reportTerms.auditAi) }}
              </button>
              <button class="btn" type="button" @click="$emit('view-report', activeReport.id)">查看报告</button>
              <button class="btn" type="button" @click="$emit('download-report', activeReport.id)">下载报告</button>
              <button class="btn" type="button">{{ reportTerms.createTask }}</button>
            </div>
          </section>
        </template>
        <div v-else class="rp-empty">请从左侧选择一条报告</div>
      </aside>
    </div>
  </div>
</template>

<script setup>
defineProps({
  reportTerms: { type: Object, required: true },
  scenario: { type: Object, required: true },
  reports: { type: Array, default: () => [] },
  filteredReports: { type: Array, default: () => [] },
  activeReport: { type: Object, default: null },
  activeId: { type: [String, Number], default: '' },
  search: { type: String, default: '' },
  source: { type: String, default: '' },
  nodule: { type: String, default: '' },
  risk: { type: String, default: '' },
  generatingIds: { type: Object, default: () => new Set() },
})

defineEmits([
  'update-search',
  'update-source',
  'update-nodule',
  'update-risk',
  'reset-filters',
  'select-report',
  'view-report',
  'primary-action',
  'download-report',
])
</script>

<style scoped>
.rp-page{flex:1;min-height:0;display:flex;flex-direction:column;gap:10px;padding:12px;background:#fff;overflow:hidden}
.card{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden}
.card-head{min-height:40px;height:auto;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:8px 12px;gap:10px;flex-wrap:wrap}
.card-title{font-weight:950;color:#0f172a;font-size:13px;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.btn,.primary{height:36px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;color:#344054;padding:0 12px;font-weight:800;cursor:pointer}
.primary{border-color:#155eef;background:#155eef;color:#fff}
.tbl-act{border:0;background:transparent;color:#155eef;font-size:12px;font-weight:850;cursor:pointer;padding:0}
.tbl-act:disabled{opacity:.55;cursor:not-allowed}
.muted{color:#64748b;font-weight:750}
.pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900}
.pill[data-tone="r"]{background:#fff1f2;color:#dc2626}
.pill[data-tone="o"]{background:#fff7ed;color:#c2410c}
.pill[data-tone="g"]{background:#ecfff3;color:#14843b}
.stat-cards{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;padding:12px 12px 0}
.review-stat-cards{padding:12px 0 0}
.stat-card{display:flex;align-items:center;gap:10px;background:#f8fafc;border:1px solid #e6edf7;border-radius:10px;padding:12px 14px}
.stat-icon{width:40px;height:40px;border-radius:10px;display:grid;place-items:center;flex-shrink:0}
.stat-blue{background:#eff6ff;color:#2563eb}.stat-purple{background:#fdf4ff;color:#a21caf}.stat-green{background:#ecfdf5;color:#059669}.stat-orange{background:#fffbeb;color:#d97706}.stat-red{background:#fff1f2;color:#dc2626}
.stat-blue-text{color:#2563eb}.stat-purple-text{color:#a21caf}.stat-green-text{color:#059669}.stat-orange-text{color:#d97706}.stat-red-text{color:#dc2626}
.stat-body{min-width:0}
.stat-label{font-size:11px;color:#64748b;font-weight:600;white-space:nowrap}
.stat-val{font-size:22px;font-weight:900;color:#111827;line-height:1.2}
.stat-sub{font-size:11px;font-weight:700;margin-top:2px}
.rp-filter-bar{padding:10px 14px;flex-shrink:0}
.rp-filter-row{display:flex;align-items:flex-end;gap:10px;flex-wrap:wrap}
.rp-filter-item{display:flex;flex-direction:column;gap:4px;min-width:0}
.rp-filter-label{font-size:11px;color:#64748b;font-weight:850;white-space:nowrap}
.rp-filter-input{height:32px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;font-size:13px;color:#111827;outline:none;min-width:160px}
.rp-filter-input:focus{border-color:#155eef}
.rp-filter-select{height:32px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;font-size:13px;color:#111827;outline:none;min-width:140px;background:#fff}
.rp-filter-select:focus{border-color:#155eef}
.rp-filter-actions{display:flex;gap:6px;align-items:flex-end;margin-left:auto}
.rp-body{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:10px;overflow:hidden}
.rp-list-card{min-height:0;display:flex;flex-direction:column;overflow:hidden}
.rp-count{font-size:12px;color:#94a3b8;font-weight:500;margin-left:6px}
.list-actions{display:flex;gap:6px}
.btn-icon{margin-right:4px}
.q-table-wrap{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:auto;flex:1}
.q-table{width:100%;border-collapse:collapse;font-size:13px}
.q-table thead tr{border-bottom:1px solid #eef2f7;background:#f8fafc}
.q-table th{padding:10px 12px;text-align:left;color:#64748b;font-weight:900;white-space:nowrap}
.q-table td{padding:10px 12px;border-bottom:1px solid #f1f5f9;white-space:nowrap}
.q-row{cursor:pointer}
.q-row:hover td{background:#f8fbff}
.q-row.active td{background:#eef5ff}
.q-row:last-child td{border-bottom:0}
.col-patient{width:80px}.col-nodule{width:88px}.col-time{width:110px}.col-ai{width:80px}.col-risk{width:72px}.col-owner{width:60px}
.patient-name{font-weight:700;font-size:13px}
.patient-sub{font-size:11px}
.nodule-tag{display:inline-flex;align-items:center;border-radius:6px;padding:2px 7px;font-size:11px;font-weight:700;background:#eef5ff;color:#155eef}
.nodule-tag[data-type="lung"]{background:#ecfdf5;color:#15803d}
.nodule-tag[data-type="thyroid"]{background:#fff7ed;color:#c2410c}
.nodule-tag[data-type="breast"]{background:#fdf4ff;color:#a21caf}
.nodule-tag[data-type="triple"]{background:#fff1f2;color:#dc2626}
.rp-status-tag{display:inline-flex;align-items:center;border-radius:6px;padding:2px 7px;font-size:11px;font-weight:700;background:#f1f5f9;color:#475569}
.rp-status-tag[data-s="解析完成"]{background:#ecfdf5;color:#15803d}
.rp-status-tag[data-s="AI解析中"]{background:#f5f3ff;color:#8b5cf6}
.rp-status-tag[data-s="待生成报告"]{background:#fff7ed;color:#c2410c}
.rp-status-tag[data-s="待医生复核"]{background:#eff6ff;color:#1d4ed8}
.rp-status-tag[data-s="异常报告"]{background:#fff1f2;color:#dc2626}
.rp-row-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.pager{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:10px 12px}
.pages{display:flex;gap:8px;align-items:center}
.page-btn{border:1px solid #d9e2ef;background:#fff;border-radius:10px;padding:5px 9px;color:#475569;font-weight:950;cursor:pointer;font-size:13px}
.page-btn.active{background:#155eef;color:#fff;border-color:#155eef}
.rp-detail{display:flex;flex-direction:column;gap:8px;overflow-y:auto;min-height:0}
.rp-detail-info{display:flex;align-items:flex-start;gap:10px;padding:10px 12px}
.rp-info-grid{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:4px 0}
.rp-info-row{display:flex;gap:4px;font-size:12px;line-height:1.8}
.rp-ik{color:#94a3b8;font-weight:850;white-space:nowrap}
.rp-iv{color:#0f172a;font-weight:700}
.rp-doc-btn{width:44px;height:44px;border-radius:10px;border:1px solid #e6edf7;background:#f8fafc;color:#64748b;display:grid;place-items:center;cursor:pointer;flex-shrink:0}
.rp-flow{display:flex;align-items:flex-start;gap:0;padding:10px 12px;overflow-x:auto}
.rp-flow-step{display:flex;flex-direction:column;align-items:center;gap:4px;flex:1;min-width:60px;position:relative}
.rp-flow-step:not(:last-child)::after{content:"";position:absolute;top:11px;left:calc(50% + 12px);right:calc(-50% + 12px);height:2px;background:#e6edf7}
.rp-flow-step[data-done="true"]:not(:last-child)::after{background:#22c55e}
.rp-flow-dot{width:22px;height:22px;border-radius:50%;border:2px solid #e6edf7;background:#fff;display:grid;place-items:center;font-size:11px;font-weight:950;color:#94a3b8;z-index:1;flex-shrink:0}
.rp-flow-step[data-done="true"] .rp-flow-dot{background:#22c55e;border-color:#22c55e;color:#fff}
.rp-flow-step[data-cur="true"] .rp-flow-dot{background:#155eef;border-color:#155eef;color:#fff}
.rp-flow-label{font-size:11px;color:#64748b;font-weight:850;text-align:center;white-space:nowrap}
.rp-flow-step[data-cur="true"] .rp-flow-label{color:#155eef;font-weight:950}
.rp-flow-time{font-size:10px;color:#94a3b8;text-align:center;white-space:nowrap}
.rp-actions{display:flex;gap:8px;padding:10px 12px;flex-wrap:wrap}
.rp-empty{display:flex;align-items:center;justify-content:center;height:200px;color:#94a3b8;font-size:13px}
</style>
