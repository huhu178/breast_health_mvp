<template>
  <div class="pm-detail">
    <section class="card overview-left">
      <div class="card-head">
        <div class="card-title">患者任务队列</div>
        <div class="panel-tools">
          <input class="search" placeholder="姓名/手机号" />
          <select class="stage-select" :value="activeStage" @change="$emit('set-stage', $event.target.value)">
            <option v-for="t in stageTabs" :key="t.key" :value="t.key">{{ t.label }}</option>
          </select>
        </div>
      </div>
      <div class="q-table-wrap">
        <table class="q-table">
          <thead>
            <tr>
              <th class="col-name">姓名</th>
              <th class="col-demo">性别/年龄</th>
              <th class="col-phone">手机</th>
              <th class="col-source">来源</th>
              <th>结节类型</th>
              <th class="col-risk">风险</th>
              <th class="col-stage">当前阶段</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in patients" :key="p.id" class="q-row" :class="{ active: p.id === activePatientId }" @click="$emit('select-patient', p.id)">
              <td><b>{{ p.name }}</b></td>
              <td class="muted">{{ p.gender }} · {{ p.age }}岁</td>
              <td class="muted">{{ p.phoneMasked }}</td>
              <td class="muted">{{ sourceLabel(p.source) }}</td>
              <td class="truncate">{{ p.nodules }}</td>
              <td><span class="pill" :data-tone="p.riskTone">{{ p.risk }}</span></td>
              <td><span class="tag2">{{ statusLabel(p) }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pager">
        <span class="muted">共 1,236 条</span>
        <div class="pages">
          <button class="page-btn" type="button">‹</button>
          <button class="page-btn active" type="button">1</button>
          <button class="page-btn" type="button">2</button>
          <button class="page-btn" type="button">3</button>
          <span class="muted">...</span>
          <button class="page-btn" type="button">124</button>
          <button class="page-btn" type="button">›</button>
        </div>
        <div class="muted">10 条/页</div>
      </div>
    </section>

    <aside class="detail-right">
      <section class="card">
        <div class="card-head">
          <div class="card-title">{{ title }}</div>
          <div class="detail-actions">
            <template v-if="tab === 'abnormal'">
              <button class="btn" type="button">创建电话随访</button>
              <button class="primary" type="button">创建复查提醒</button>
            </template>
          </div>
        </div>
        <div class="pad detail-head" :class="{ compact: tab === 'record' }">
          <div class="dh-left">
            <div class="dh-name">{{ activePatient.name }}</div>
            <div class="muted">{{ activePatient.gender }} · {{ activePatient.age }}岁 · {{ activePatient.phoneMasked }}</div>
          </div>
          <div class="dh-right">
            <span class="pill" :data-tone="activePatient.riskTone">{{ activePatient.risk }}</span>
            <span v-if="tab !== 'record'" class="tag2">{{ statusLabel(activePatient) }}</span>
          </div>
        </div>
      </section>

      <template v-if="tab === 'record'">
        <section class="card">
          <div class="card-head one-line">
            <div class="card-title">档案信息</div>
            <button class="btn btn-sm" type="button" @click="$emit('go-record')">编辑档案</button>
          </div>
          <div class="pad pad-lg">
            <div class="info-grid">
              <div class="kv"><div class="k">结节类型</div><div class="v">{{ activePatient.nodules }}</div></div>
              <div class="kv"><div class="k">来源</div><div class="v">{{ sourceLabel(activePatient.source) }}</div></div>
              <div class="kv"><div class="k">服务状态</div><div class="v">{{ activePatient.serviceStatus }}</div></div>
            </div>
          </div>
        </section>

        <section class="card">
          <div class="card-head one-line">
            <div class="card-title">原始报告</div>
            <div class="detail-actions">
              <button class="btn btn-sm" type="button">导入报告</button>
              <button class="primary btn-sm" type="button">上传报告</button>
            </div>
          </div>
          <div class="pad pad-lg">
            <template v-if="activePatient.rawReports && activePatient.rawReports.length">
              <div class="file-list">
                <div v-for="f in activePatient.rawReports" :key="f.name" class="file-row">
                  <div class="file-left">
                    <div class="file-ico" :data-type="f.type">{{ f.type.toUpperCase() }}</div>
                    <div class="file-main">
                      <div class="file-name">{{ f.name }}</div>
                      <div class="file-sub muted">{{ f.size }} · {{ f.at }}</div>
                    </div>
                  </div>
                  <div class="file-right">
                    <span class="pill mini" :data-tone="f.stateTone === 'g' ? 'g' : 'o'">{{ f.state }}</span>
                    <button class="icon-more" type="button" @click="$emit('file-action')">...</button>
                  </div>
                </div>
              </div>
            </template>
            <template v-else>
              <div class="empty">
                <div class="empty-title">暂无原始报告</div>
                <div class="muted empty-sub">上传检查报告后，AI 将自动解析并生成{{ scenario.reportLabel }}</div>
                <div class="empty-actions">
                  <button class="primary" type="button">上传报告</button>
                  <button class="btn" type="button">{{ scenario.importLabel }}</button>
                </div>
              </div>
            </template>
          </div>
        </section>

        <section class="card">
          <div class="card-head one-line">
            <div class="card-title">AI 解读摘要</div>
            <div class="inline-actions">
              <span v-if="activePatient.rawReports && activePatient.rawReports.length" class="pill mini" data-tone="g">已生成</span>
              <span v-else class="pill mini" data-tone="o">待生成</span>
              <button class="btn btn-sm" type="button">复制摘要</button>
            </div>
          </div>
          <div class="pad pad-lg">
            <template v-if="activePatient.rawReports && activePatient.rawReports.length">
              <div class="long">{{ activePatient.aiReadSummary }}</div>
            </template>
            <template v-else>
              <div class="muted note-text">上传原始报告后，AI 将自动生成解读摘要。</div>
            </template>
          </div>
        </section>
      </template>

      <template v-else-if="tab === 'abnormal'">
        <section class="card">
          <div class="card-head">
            <div class="card-title">处置记录</div>
            <div class="review-actions">
              <button class="btn" type="button">创建电话随访</button>
              <button class="primary" type="button">创建复查提醒</button>
            </div>
          </div>
          <div class="pad">
            <div v-for="e in (activePatient.abnormal?.interventions || [])" :key="e.at + e.action" class="audit-row">
              <div class="audit-at">{{ e.at }}</div>
              <div class="audit-main">
                <div class="audit-line"><b>{{ e.by }}</b> · {{ e.action }}</div>
                <div class="muted">{{ e.note }}</div>
              </div>
            </div>
            <div class="hline"></div>
            <div class="row3">
              <div class="muted">复查计划：</div>
              <div class="row3-main">{{ activePatient.abnormal?.recallPlan }}</div>
            </div>
            <div class="row3">
              <div class="muted">回收状态：</div>
              <span class="pill mini" :data-tone="activePatient.abnormal?.recallTone || 'g'">{{ activePatient.abnormal?.recallState }}</span>
              <span class="muted">{{ activePatient.abnormal?.recallHint }}</span>
            </div>
          </div>
        </section>
      </template>
    </aside>
  </div>
</template>

<script setup>
defineProps({
  tab: { type: String, default: 'abnormal' },
  title: { type: String, default: '' },
  patients: { type: Array, default: () => [] },
  activePatient: { type: Object, default: () => ({}) },
  activePatientId: { type: [String, Number], default: '' },
  activeStage: { type: String, default: 'all' },
  stageTabs: { type: Array, default: () => [] },
  scenario: { type: Object, required: true },
  sourceLabel: { type: Function, required: true },
  statusLabel: { type: Function, required: true },
})

defineEmits(['set-stage', 'select-patient', 'go-record', 'file-action'])
</script>

<style scoped>
.pm-detail{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:12px;padding:12px;background:#fff;overflow:hidden}
.card{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden}
.card-head{min-height:40px;height:auto;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:8px 12px;gap:10px;flex-wrap:wrap}
.card-head.one-line{align-items:center}
.card-title{font-weight:950;color:#0f172a;font-size:13px;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.overview-left{min-height:0;display:flex;flex-direction:column;overflow:hidden}
.panel-tools{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.search,.stage-select{height:32px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;padding:0 10px;color:#172033;font-size:13px;min-width:0}
.q-table-wrap{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:auto;flex:1}
.q-table{width:100%;border-collapse:collapse;font-size:13px}
.q-table thead tr{border-bottom:1px solid #eef2f7;background:#f8fafc}
.q-table th{padding:10px 12px;text-align:left;color:#64748b;font-weight:900;white-space:nowrap}
.q-table td{padding:10px 12px;border-bottom:1px solid #f1f5f9;white-space:nowrap}
.q-row{cursor:pointer}
.q-row:hover td{background:#f8fbff}
.q-row.active td{background:#eef5ff}
.q-row:last-child td{border-bottom:0}
.col-name{width:88px}.col-demo{width:92px}.col-phone{width:122px}.col-source{width:72px}.col-risk{width:76px}.col-stage{width:168px}
.truncate{max-width:360px;overflow:hidden;text-overflow:ellipsis}
.muted{color:#64748b;font-weight:750}
.pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900}
.pill[data-tone="r"]{background:#fff1f2;color:#dc2626}
.pill[data-tone="o"]{background:#fff7ed;color:#c2410c}
.pill[data-tone="g"]{background:#ecfff3;color:#14843b}
.pill.mini{padding:2px 8px;font-size:11px}
.tag2{border:1px solid #cfe0ff;background:#eef5ff;color:#155eef;border-radius:999px;padding:3px 8px;font-weight:900;font-size:12px}
.pager{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:10px 12px}
.pages{display:flex;gap:8px;align-items:center}
.page-btn{border:1px solid #d9e2ef;background:#fff;border-radius:10px;padding:5px 9px;color:#475569;font-weight:950;cursor:pointer;font-size:13px}
.page-btn.active{background:#155eef;color:#fff;border-color:#155eef}
.detail-right{min-height:0;height:100%;display:flex;flex-direction:column;gap:10px;overflow-y:auto;overflow-x:hidden;padding-right:12px;padding-bottom:12px;box-sizing:border-box;line-height:1.5}
.detail-actions,.review-actions,.inline-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;align-items:center}
.pad{padding:10px 12px}
.pad-lg{padding:12px}
.detail-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.detail-head.compact{align-items:center}
.dh-name{font-weight:950;color:#0f172a;font-size:14px}
.dh-right{display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
.btn,.primary{height:36px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;color:#344054;padding:0 12px;font-weight:800;cursor:pointer}
.primary{border-color:#155eef;background:#155eef;color:#fff}
.btn-sm{height:30px;padding:0 10px;font-size:12px}
.info-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px 10px}
.kv{border:1px solid #eef2f7;background:#fbfdff;border-radius:10px;padding:9px 10px}
.kv .k{font-size:12px;color:#94a3b8;font-weight:850}
.kv .v{font-size:13px;color:#0f172a;font-weight:900;margin-top:3px}
.file-list{display:grid;gap:8px}
.file-row{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid #eef2f7;border-radius:10px;background:#fff;padding:8px 10px}
.file-left{display:flex;align-items:center;gap:10px;min-width:0}
.file-ico{width:34px;height:34px;border-radius:8px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-size:10px;font-weight:950;flex-shrink:0}
.file-main{min-width:0}
.file-name{font-weight:950;color:#0f172a;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.file-sub{font-size:11px;margin-top:2px}
.file-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
.icon-more{border:0;background:transparent;color:#64748b;font-size:16px;cursor:pointer}
.empty{border:1px dashed #dbe5f2;border-radius:12px;background:#fbfdff;padding:22px;text-align:center}
.empty-title{font-weight:950;color:#0f172a}
.empty-sub{font-size:12px;margin-top:4px}
.empty-actions{display:flex;gap:8px;justify-content:center;margin-top:12px;flex-wrap:wrap}
.long{font-size:13px;color:#334155;line-height:1.7;white-space:pre-wrap}
.note-text{font-size:13px}
.audit-row{display:flex;gap:10px;align-items:flex-start;border-top:1px solid #eef2f7;padding-top:10px}
.audit-row:first-child{border-top:0;padding-top:0}
.audit-at{min-width:70px;color:#94a3b8;font-size:12px;font-weight:850}
.audit-main{display:grid;gap:4px;min-width:0}
.audit-line{font-size:13px;color:#334155}
.hline{height:1px;background:#eef2f7;margin:12px 0}
.row3{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.row3-main{font-weight:900;color:#0f172a}
</style>
