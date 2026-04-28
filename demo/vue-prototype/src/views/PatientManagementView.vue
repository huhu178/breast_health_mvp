<template>
  <div class="pm">
    <section class="pm-shell" aria-label="患者管理三栏工作台">
      <!-- tab=queue：总览（对齐你截图的双栏布局） -->
      <div v-if="subTab === 'queue'" class="pm-overview">
        <!-- 左：患者任务队列（大表格） -->
        <section class="card overview-left">

          <!-- 统计卡片 -->
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
                <div class="stat-val">{{ queue.filter(p=>p.riskTone==='r').length }}</div>
                <div class="stat-sub" style="color:#dc2626">较昨日 +2</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background:#fffbeb;color:#d97706">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              </div>
              <div class="stat-body">
                <div class="stat-label">待处理报告</div>
                <div class="stat-val">{{ queue.filter(p=>statusKey(p)==='review').length }}</div>
                <div class="stat-sub" style="color:#d97706">较昨日 -1</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background:#ecfdf5;color:#059669">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </div>
              <div class="stat-body">
                <div class="stat-label">待审核报告</div>
                <div class="stat-val">{{ queue.filter(p=>p.stage==='review').length }}</div>
                <div class="stat-sub" style="color:#059669">较昨日 -1</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background:#f5f3ff;color:#7c3aed">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </div>
              <div class="stat-body">
                <div class="stat-label">待推送患者</div>
                <div class="stat-val">{{ queue.filter(p=>p.stage==='push').length }}</div>
                <div class="stat-sub" style="color:#7c3aed">较昨日 +1</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background:#fff1f2;color:#e11d48">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              </div>
              <div class="stat-body">
                <div class="stat-label">异常待处理</div>
                <div class="stat-val">{{ queue.filter(p=>p.stage==='abnormal').length }}</div>
                <div class="stat-sub" style="color:#e11d48">较昨日 +2</div>
              </div>
            </div>
          </div>

          <!-- 筛选条件 -->
          <div class="q-filter-bar">
            <div class="q-filter-title">筛选条件</div>
            <div class="q-filter-row">
              <div class="q-filter-item">
                <label>姓名/手机号</label>
                <input class="q-filter-input" v-model="qSearch" placeholder="请输入姓名或手机号" />
              </div>
              <div class="q-filter-item">
                <label>患者来源</label>
                <select class="q-filter-select" v-model="qSource">
                  <option value="">全部</option>
                  <option>门诊</option>
                  <option>体检中心</option>
                  <option>社区</option>
                  <option>药店</option>
                </select>
              </div>
              <div class="q-filter-item">
                <label>结节类型</label>
                <select class="q-filter-select" v-model="qNodule">
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
                <select class="q-filter-select" v-model="qRisk">
                  <option value="">全部</option>
                  <option>高风险</option>
                  <option>中风险</option>
                  <option>低风险</option>
                </select>
              </div>
              <div class="q-filter-item">
                <label>当前状态</label>
                <select class="q-filter-select" v-model="qStatus">
                  <option value="">全部</option>
                  <option value="gen">建立档案</option>
                  <option value="review">待医生复核</option>
                  <option value="plan">随访计划制定</option>
                  <option value="follow">AI随访中</option>
                  <option value="push">待推送</option>
                  <option value="abnormal">异常待处理</option>
                </select>
              </div>
              <div class="q-filter-actions">
                <button class="btn" type="button" @click="qSearch='';qSource='';qNodule='';qRisk='';qStatus=''">重置</button>
                <button class="primary" type="button">查询</button>
                <button class="primary" type="button" @click="goRecord">+ 新建档案</button>
              </div>
            </div>
          </div>

          <!-- 表格 -->
          <div class="q-table-head-row">
            <span class="muted">患者列表 共 {{ queueFiltered.length }} 条</span>
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
                  <th style="width:72px">负责人</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in queueFiltered"
                  :key="p.id"
                  class="q-row"
                  :class="{ active: p.id === activePatientId }"
                  @click="activePatientId = p.id"
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
                  <td class="muted">{{ p.owner }}</td>
                  <td>
                    <div style="display:flex;gap:8px">
                      <button class="tbl-act" type="button" @click.stop="setSubTab('review')">查看</button>
                      <button class="tbl-act" type="button" @click.stop="setSubTab('follow')">随访</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pager">
            <span class="muted">共 {{ queueFiltered.length }} 条</span>
            <div class="pages">
              <button class="page-btn" type="button">‹</button>
              <button class="page-btn active" type="button">1</button>
              <button class="page-btn" type="button">2</button>
              <button class="page-btn" type="button">›</button>
            </div>
            <div class="muted">10 条/页</div>
          </div>
        </section>

        <!-- 右：患者操作面板 -->
        <aside class="overview-right">
          <div v-if="!queue.length" class="side-empty">加载中...</div>
          <!-- 合并面板：患者详情 / 标签 / 下一步 / 流程 / 操作 / 动态 -->
          <section v-else class="card side-panel">
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
                  <button
                    :class="a.primary ? 'primary full' : 'btn-link-lite'"
                    type="button"
                    @click="a.onClick()"
                  >
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

      <!-- record tab：患者建档（表单） -->
      <div v-else-if="subTab === 'record'" class="pm-record">
        <RecordView :embedded="true" @back="backToQueue" />
      </div>

      <!-- followup-plan tab：随访计划制定（展示计划内容） -->
      <div v-else-if="subTab === 'followup-plan'" class="plan-page">

        <!-- 统计卡片 -->
        <div class="stat-cards" style="padding:0 0 0">
          <div class="stat-card">
            <div class="stat-icon" style="background:#eff6ff;color:#2563eb">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">今日随访</div>
              <div class="stat-val">{{ filteredTasks.filter(t=>t.status==='pending').length }}</div>
              <div class="stat-sub" style="color:#2563eb">较昨日 +3</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#fffbeb;color:#d97706">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">待随访</div>
              <div class="stat-val">{{ followTasks.filter(t=>t.status==='pending').length }}</div>
              <div class="stat-sub" style="color:#d97706">较昨日 +5</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#ecfdf5;color:#059669">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">已完成</div>
              <div class="stat-val">{{ followTasks.filter(t=>t.status==='done').length }}</div>
              <div class="stat-sub" style="color:#059669">较昨日 +8</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#fff1f2;color:#dc2626">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">逾期随访</div>
              <div class="stat-val">{{ followTasks.filter(t=>t.status==='overdue').length }}</div>
              <div class="stat-sub" style="color:#dc2626">较昨日 +1</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#fdf4ff;color:#a21caf">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">异常反馈</div>
              <div class="stat-val">{{ followTasks.filter(t=>t.status==='abnormal').length }}</div>
              <div class="stat-sub" style="color:#a21caf">较昨日 +2</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#f0fdf4;color:#16a34a">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">自动提醒中</div>
              <div class="stat-val">{{ followTasks.filter(t=>t.channel==='小程序').length }}</div>
              <div class="stat-sub" style="color:#16a34a">较昨日 +4</div>
            </div>
          </div>
        </div>

        <!-- 顶部筛选条 -->
        <section class="card plan-filter">
          <div class="q-filter-title" style="padding:10px 16px 0;font-size:13px;font-weight:800;color:#374151">筛选条件</div>
          <div class="pad pad-lg plan-filter-row" style="padding-top:8px">
            <label class="pf" style="min-width:180px">
              <span class="k">患者姓名/手机号</span>
              <input class="pf-in" v-model="taskFilters.q" placeholder="姓名 / 手机号" />
            </label>
            <label class="pf">
              <span class="k">患者来源</span>
              <select class="pf-in" v-model="taskFilters.source">
                <option value="">全部</option>
                <option>门诊</option>
                <option>体检中心</option>
                <option>社区</option>
              </select>
            </label>
            <label class="pf">
              <span class="k">结节类型</span>
              <select class="pf-in" v-model="taskFilters.nodule">
                <option value="">全部</option>
                <option>乳腺结节</option>
                <option>肺部结节</option>
                <option>甲状腺结节</option>
                <option>乳腺+肺部结节</option>
                <option>三合并结节</option>
              </select>
            </label>
            <label class="pf">
              <span class="k">风险等级</span>
              <select class="pf-in" v-model="taskFilters.risk">
                <option value="">全部</option>
                <option value="高风险">高风险</option>
                <option value="中风险">中风险</option>
                <option value="低风险">低风险</option>
              </select>
            </label>
            <label class="pf">
              <span class="k">随访状态</span>
              <select class="pf-in" v-model="taskFilters.status">
                <option value="">全部</option>
                <option value="pending">待随访</option>
                <option value="done">已完成</option>
                <option value="overdue">逾期</option>
                <option value="abnormal">异常反馈</option>
              </select>
            </label>
            <label class="pf">
              <span class="k">触达方式</span>
              <select class="pf-in" v-model="taskFilters.channel">
                <option value="">全部</option>
                <option value="企微">企微</option>
                <option value="电话">电话</option>
                <option value="小程序">小程序</option>
              </select>
            </label>
            <label class="pf">
              <span class="k">负责人</span>
              <input class="pf-in" v-model="taskFilters.owner" placeholder="例如：张医生" />
            </label>
            <div class="plan-filter-actions">
              <button class="btn-link-lite" type="button" @click="resetTaskFilters">重置</button>
              <button class="primary" type="button">查询</button>
              <button class="primary" type="button" @click="openNewTaskFromActive">新建随访任务</button>
            </div>
          </div>
        </section>

        <div class="plan-workbench">
          <!-- 左：任务列表 -->
          <section class="card plan-task-list">
            <div class="card-head one-line">
              <div class="card-title" style="display:flex;align-items:center;gap:10px;min-width:0">
                <span>工作台列表</span>
                <span class="muted" style="font-size:12px;font-weight:700">· 患者 {{ filteredPlanPatients.length }} · 任务 {{ filteredTasks.length }}</span>
              </div>
              <div class="panel-tools">
                <div class="seg-tabs">
                  <button class="seg-tab" type="button" :data-on="planLeftMode==='patients'" @click="planLeftMode='patients'">患者</button>
                  <button class="seg-tab" type="button" :data-on="planLeftMode==='tasks'" @click="planLeftMode='tasks'">任务</button>
                </div>
                <template v-if="planLeftMode==='tasks'">
                  <button class="btn-link-lite" type="button" @click="toggleAllTaskSelection">{{ allTasksSelected ? '取消全选' : '全选' }}</button>
                  <button class="btn-link-lite" type="button" @click="bulkAssignSelected">批量分派</button>
                </template>
              </div>
            </div>
            <div class="pad pad-lg" style="padding-bottom:0">
              <div class="muted" style="font-size:12px">先在“患者”里选择并制定任务，再在“任务”里批量分派与执行闭环。</div>
            </div>
            <div v-if="planLeftMode==='patients'" class="pat-table">
              <div class="pat-head">
                <div>患者</div>
                <div>结节类型</div>
                <div>风险</div>
                <div>负责人</div>
                <div style="text-align:right">操作</div>
              </div>
              <div class="pat-rows">
                <div v-for="p in filteredPlanPatients" :key="p.id" class="pat-row" :data-active="p.id===activePatientId">
                  <button type="button" class="pat-main" @click="activePatientId=p.id">
                    <div class="pat-name"><b>{{ p.name }}</b></div>
                    <div class="muted" style="font-size:12px">{{ p.gender }}·{{ p.age }}岁 · {{ p.phoneMasked }}</div>
                  </button>
                  <div class="pat-cell">{{ p.nodules }}</div>
                  <div class="pat-cell"><span class="pill mini" :data-tone="p.riskTone">{{ p.risk }}</span></div>
                  <div class="pat-cell">{{ p.owner || '未分派' }}</div>
                  <div class="pat-cell" style="text-align:right">
                    <button class="kb-act" type="button" @click="createTaskForPatient(p)">制定任务</button>
                  </div>
                </div>
                <div v-if="!filteredPlanPatients.length" class="muted" style="font-size:12px;padding:10px 12px">暂无匹配患者</div>
              </div>
            </div>

            <div v-else class="task-rows">
              <button
                v-for="t in filteredTasks"
                :key="t.id"
                type="button"
                class="task-row"
                :class="{ active: t.id === activeTaskId }"
                @click="selectTask(t.id)"
              >
                <div class="tr-top">
                  <b style="min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ t.patientName }}</b>
                  <span class="pill mini" :data-tone="t.riskTone">{{ t.risk }}</span>
                </div>
                <div class="tr-sub muted">{{ t.gender }}·{{ t.age }}岁 · {{ t.phoneMasked }}</div>
                <div class="tr-meta">
                  <span class="tag2">{{ taskStatusLabel(t.status) }}</span>
                  <span class="muted" style="font-size:12px">{{ t.channel }}</span>
                  <span class="muted" style="font-size:12px">· {{ t.owner || '未分派' }}</span>
                </div>
                <div class="tr-ck">
                  <input type="checkbox" :checked="selectedTaskIds.has(t.id)" @click.stop @change="toggleTaskSelection(t.id, $event.target.checked)" />
                </div>
              </button>
              <div v-if="!filteredTasks.length" class="muted" style="font-size:12px;padding:10px 12px">暂无任务，可先在“患者”中制定任务。</div>
            </div>
            <div class="pager" style="margin-top:10px">
              <div class="muted" style="font-size:12px">分页（示意）</div>
              <div style="display:flex;gap:8px;align-items:center">
                <button class="btn-link-lite" type="button">上一页</button>
                <span class="muted" style="font-size:12px">1 / 1</span>
                <button class="btn-link-lite" type="button">下一页</button>
              </div>
            </div>
          </section>

          <!-- 右：任务详情 -->
          <section class="card plan-task-detail">
            <div class="card-head one-line">
              <div class="card-title">随访任务详情</div>
              <div class="panel-tools">
                <select class="stage-select" v-model="planDay" :disabled="planState.loading || !!planState.error">
                  <option v-for="d in planDayList" :key="d" :value="d">Day {{ d.replace('day','') }}</option>
                </select>
                <button class="btn-link-lite" type="button" @click="loadPlan">刷新计划</button>
              </div>
            </div>

            <div class="pad pad-lg">
              <div v-if="!activeTask" class="muted">请选择左侧一条随访任务。</div>
              <template v-else>
                <div class="detail-grid">
                  <section class="detail-card">
                    <div class="detail-top">
                      <div class="detail-top-main">
                        <div class="detail-top-title">
                          <b>{{ activeTask.patientName }}</b>
                          <span class="muted">（{{ activeTask.gender }}·{{ activeTask.age }}岁）</span>
                          <span class="pill mini" :data-tone="activeTask.riskTone" style="margin-left:8px">{{ activeTask.risk }}</span>
                        </div>
                        <div class="detail-top-sub muted">{{ activeTask.phoneMasked }} · {{ activeTask.owner || '未分派' }} · {{ activeTask.channel }}</div>
                      </div>
                      <div class="detail-top-actions">
                        <button class="btn-link-lite" type="button" @click="bulkAssignSelected">分派</button>
                      </div>
                    </div>
                  </section>

                  <section class="detail-card">
                    <div class="detail-title">随访任务制定</div>
                    <div class="detail-sub muted">{{ planState.title || '随访计划模板' }} · Day {{ planDay.replace('day','') }}</div>

                    <div class="plan-form" style="margin-bottom:0">
                      <div class="plan-flow-title" style="margin-bottom:8px">表单 / 知识库</div>
                      <div class="pf-grid" style="grid-template-columns:1fr 1fr 1fr">
                        <label class="pf">
                          <span class="k">复查周期</span>
                          <select class="pf-in" v-model="draft.cycle">
                            <option value="3个月">3个月</option>
                            <option value="6个月">6个月</option>
                            <option value="12个月">12个月</option>
                          </select>
                        </label>
                        <label class="pf">
                          <span class="k">触达方式</span>
                          <select class="pf-in" v-model="draft.channel">
                            <option value="企微">企微</option>
                            <option value="电话">电话</option>
                            <option value="小程序">小程序</option>
                            <option value="企微/电话/小程序">企微/电话/小程序</option>
                          </select>
                        </label>
                        <label class="pf">
                          <span class="k">提醒策略</span>
                          <select class="pf-in" v-model="draft.reminder">
                            <option value="到期前3天提醒">到期前3天提醒</option>
                            <option value="到期前7天提醒">到期前7天提醒</option>
                            <option value="逾期转人工">逾期转人工</option>
                            <option value="异常优先转医生">异常优先转医生</option>
                          </select>
                        </label>

                        <div class="pf" style="grid-column:1/-1">
                          <div class="kb-head">
                            <div>
                              <div class="k">内容库（仅选用）</div>
                              <div class="muted" style="font-size:12px;margin-top:4px">按分组选择条目；正文预览在右侧抽屉。修改/导入在“管理知识库”。</div>
                            </div>
                            <div class="kb-head-actions">
                              <button class="btn-link-lite" type="button" @click="kbUi.managerOpen = true">管理知识库</button>
                            </div>
                          </div>

                          <div class="kb-groups">
                            <button v-for="g in KB_GROUPS" :key="g.key" type="button" class="kb-group" @click="openKbDrawer(g.key)">
                              <div class="kb-group-title">{{ g.label }}</div>
                              <div class="kb-group-sub muted">已选 {{ (kbSelectedByGroup[g.key] || []).length }} 项</div>
                              <div class="kb-group-tags">
                                <span v-for="it in (kbSelectedByGroup[g.key] || []).slice(0, 3)" :key="it.key" class="kb-tag">{{ it.label }}</span>
                                <span v-if="(kbSelectedByGroup[g.key] || []).length > 3" class="kb-tag muted">+{{ (kbSelectedByGroup[g.key] || []).length - 3 }}</span>
                              </div>
                            </button>
                          </div>

                          <div class="kb-picked muted" style="font-size:12px">
                            已选：<span v-if="kbSelected.length">{{ kbSelected.map(x=>x.label).slice(0, 8).join('、') }}<span v-if="kbSelected.length>8"> 等{{ kbSelected.length }}项</span></span>
                            <span v-else>暂无</span>
                          </div>
                        </div>

                        <label class="pf" style="grid-column:1/-1">
                          <span class="k">备注</span>
                          <textarea class="pf-in" v-model="draft.note" style="height:76px;padding:10px;resize:vertical"></textarea>
                        </label>
                      </div>
                      <div class="plan-flow-actions" style="justify-content:flex-start;margin-top:10px">
                        <button class="primary" type="button" @click="applyDraftToPlan">生成并保存任务</button>
                        <button class="btn-link-lite" type="button" @click="savePlanForActive">保存计划</button>
                        <button class="btn-link-lite" type="button" @click="startAiFollowup">开启 AI 随访</button>
                      </div>
                    </div>
                  </section>

                  <section class="detail-card">
                    <div class="detail-title">执行记录</div>
                    <div class="exec-list">
                      <div v-for="(e, idx) in activeTask.logs" :key="idx" class="exec-row">
                        <div class="exec-at">{{ e.at }}</div>
                        <div class="exec-main">
                          <div class="exec-line"><b>{{ e.by }}</b> · {{ e.action }}</div>
                          <div class="muted" style="white-space:pre-wrap">{{ e.note }}</div>
                        </div>
                      </div>
                      <div v-if="!activeTask.logs?.length" class="muted" style="font-size:12px">暂无执行记录</div>
                    </div>
                  </section>
                </div>

                <!-- 内容库抽屉：选择 + 预览 -->
                <div v-if="kbUi.drawerOpen" class="kb-drawer" role="dialog" aria-modal="true">
                  <div class="kb-drawer-card">
                    <div class="kb-drawer-head">
                      <div class="kb-drawer-title">选择内容 · {{ (KB_GROUPS.find(x=>x.key===kbUi.drawerGroup)?.label) || '内容库' }}</div>
                      <button class="kb-x" type="button" @click="kbUi.drawerOpen=false">×</button>
                    </div>
                    <div class="kb-drawer-body">
                      <div class="kb-drawer-left">
                        <div class="kb-drawer-search">
                          <input class="pf-in" v-model="kbUi.drawerQuery" placeholder="搜索条目标题" />
                        </div>
                        <div class="kb-drawer-list">
                          <button
                            v-for="it in kbDrawerItems"
                            :key="it.key"
                            type="button"
                            class="kb-li"
                            :data-on="kbUi.drawerActiveKey===it.key"
                            @click="kbUi.drawerActiveKey=it.key"
                          >
                            <label class="kb-li-ck" @click.stop>
                              <input
                                type="checkbox"
                                :checked="it.enabled"
                                @change="it.isCustom ? setCustomEnabled(it.key, $event.target.checked) : setKbEnabled(it.key, $event.target.checked)"
                              />
                            </label>
                            <div class="kb-li-main">
                              <div class="kb-li-title">{{ it.label }}</div>
                              <div class="kb-li-sub muted">{{ it.isCustom ? '自定义条目' : '模板条目' }}</div>
                            </div>
                          </button>
                          <div v-if="!kbDrawerItems.length" class="muted" style="font-size:12px;padding:10px 12px">无匹配条目</div>
                        </div>
                      </div>
                      <div class="kb-drawer-right">
                        <div class="kb-prev-head">
                          <div class="kb-prev-title">{{ kbDrawerActive?.label || '—' }}</div>
                          <div class="kb-prev-actions">
                            <button class="btn-link-lite" type="button" @click="kbUi.managerOpen=true">管理知识库</button>
                            <button class="btn-link-lite" type="button" @click="openKbEditor({ key: kbDrawerActive?.key, label: kbDrawerActive?.label, text: kbDrawerActive?.isCustom ? kbDrawerActive?.text : getKbText(kbDrawerActive?.key) })">编辑此条</button>
                          </div>
                        </div>
                        <div class="kb-prev-body">{{ kbDrawerActive ? (kbDrawerActive.isCustom ? (kbDrawerActive.text || '—') : (getKbText(kbDrawerActive.key) || '—')) : '—' }}</div>
                      </div>
                    </div>
                    <div class="kb-drawer-actions">
                      <button class="btn-link-lite" type="button" @click="kbUi.drawerOpen=false">完成</button>
                    </div>
                  </div>
                </div>

                <!-- 知识库管理（独立弹窗） -->
                <div v-if="kbUi.managerOpen" class="kb-modal" role="dialog" aria-modal="true">
                  <div class="kb-modal-card">
                    <div class="kb-modal-head">
                      <div class="kb-modal-title">知识库管理</div>
                      <button class="kb-x" type="button" @click="kbUi.managerOpen=false">×</button>
                    </div>
                    <div class="kb-modal-body">
                      <div class="kb-toolbar">
                        <button class="btn-link-lite" type="button" @click="openKbEditor({ key: (kbItems.find(x=>!x.isCustom)?.key || 'knowledgeCard') })">修改模板</button>
                        <button class="btn-link-lite" type="button" @click="openKbEditor({})">添加条目</button>
                        <button class="btn-link-lite" type="button" @click="kbUploadInputRef?.click()">上传</button>
                        <button class="btn-link-lite" type="button" @click="kbImportInputRef?.click()">导入(JSON)</button>
                      </div>

                      <div class="kb-list" role="list" style="margin-top:10px">
                        <div v-for="it in kbItems" :key="it.key" class="kb-row" role="listitem">
                          <div class="kb-ck" style="cursor:default">
                            <span class="kb-name">{{ it.label }}</span>
                            <span class="muted" style="font-size:12px">{{ it.isCustom ? '自定义' : '模板' }}</span>
                          </div>
                          <div class="kb-actions">
                            <button class="kb-act" type="button" @click="openKbEditor({ key: it.key, label: it.label, text: it.isCustom ? it.text : getKbText(it.key) })">编辑</button>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="kb-modal-actions">
                      <button class="btn-link-lite" type="button" @click="kbUi.managerOpen=false">关闭</button>
                    </div>
                  </div>
                </div>

                <!-- 条目编辑器（复用） -->
                <div v-if="kbUi.editorOpen" class="kb-modal" role="dialog" aria-modal="true">
                  <div class="kb-modal-card">
                    <div class="kb-modal-head">
                      <div class="kb-modal-title">知识库条目{{ kbUi.editorKey ? '修改' : '添加' }}</div>
                      <button class="kb-x" type="button" @click="kbUi.editorOpen=false">×</button>
                    </div>
                    <div class="kb-modal-body">
                      <label class="pf" style="gap:6px">
                        <span class="k">标题</span>
                        <input class="pf-in" v-model="kbUi.editorLabel" placeholder="例如：复查提醒 / 护理要点" />
                      </label>
                      <label class="pf" style="gap:6px;margin-top:10px">
                        <span class="k">内容</span>
                        <textarea class="pf-in" v-model="kbUi.editorText" style="height:180px;padding:10px;resize:vertical" placeholder="输入条目正文（支持换行）"></textarea>
                      </label>
                    </div>
                    <div class="kb-modal-actions">
                      <button class="btn-link-lite" type="button" @click="kbUi.editorOpen=false">取消</button>
                      <button class="primary" type="button" @click="saveKbEditor">保存</button>
                    </div>
                  </div>
                </div>

                <input ref="kbImportInputRef" class="kb-file" type="file" accept="application/json" @change="onKbImport($event)" />
                <input ref="kbUploadInputRef" class="kb-file" type="file" accept=".xlsx,.xls" @change="onKbUpload($event)" />
              </template>
            </div>
          </section>
        </div>
      </div>

      <!-- follow tab：患者随访聊天记录查看（三栏：患者列表 | 手机聊天 | 助手面板） -->
      <div v-else-if="subTab === 'follow'" class="follow-workbench">

        <!-- 左：患者选择列表 -->
        <div class="follow-patient-col">
          <!-- 搜索 + 筛选（固定顶部） -->
          <div class="fp-filters">
            <input class="fp-search" v-model="followSearch" placeholder="搜索姓名 / 手机号" />
            <div class="fp-filter-row">
              <select class="fp-select" v-model="followRiskFilter">
                <option value="">全部风险</option>
                <option value="高风险">高风险</option>
                <option value="中风险">中风险</option>
                <option value="低风险">低风险</option>
              </select>
              <select class="fp-select" v-model="followStageFilter">
                <option value="">全部阶段</option>
                <option v-for="t in stageTabs.slice(1)" :key="t.key" :value="t.key">{{ t.label }}</option>
              </select>
            </div>
            <div class="fp-count muted">共 {{ followFilteredQueue.length }} 人</div>
          </div>
          <!-- 患者列表（独立滚动） -->
          <div class="follow-patient-list">
            <button
              v-for="p in followFilteredQueue"
              :key="p.id"
              type="button"
              class="fp-row"
              :class="{ active: followPatientId === p.id }"
              @click="followPatientId = p.id"
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

        <!-- 中：手机聊天记录预览 -->
        <div class="follow-phone-col">
          <div class="phone-preview-label">
            <span>{{ followPatient?.name }} · 随访记录</span>
            <span class="muted" style="font-size:11px">{{ currentAssistant?.name }}</span>
          </div>
          <div class="device-outer-lg">
            <div class="device-btn-l" style="top:100px"></div>
            <div class="device-btn-l" style="top:140px"></div>
            <div class="device-btn-l" style="top:180px"></div>
            <div class="device-btn-r" style="top:140px"></div>
            <div class="device-body">
              <div class="device-notch">
                <div class="device-camera"></div>
                <div class="device-speaker"></div>
              </div>
              <div class="device-screen">
                <div class="screen-status">
                  <span>09:41</span>
                  <span style="display:flex;gap:4px;align-items:center">
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
                      <div class="screen-sub">{{ followPatient?.name }} · 健康随访</div>
                    </div>
                  </div>
                  <span style="color:#94a3b8;font-size:15px;letter-spacing:1px">···</span>
                </div>
                <div class="screen-chat-lg">
                  <div class="screen-date-divider">今天</div>
                  <template v-for="(msg, i) in simulatedAssistantChat" :key="i">
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
                  <div class="screen-input-field">发送消息…</div>
                  <button class="screen-send-btn" type="button">
                    <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4z"/></svg>
                  </button>
                </div>
              </div>
              <div class="device-home-bar-wrap"><div class="device-home-bar"></div></div>
            </div>
          </div>
        </div>

        <!-- 右：助手切换控制面板 -->
        <div class="follow-ctrl-col">
          <!-- 当前助手：状态 + 建议 + 一键动作（主焦点） -->
          <section class="assist-focus card">
            <div class="card-head">
              <div class="card-title">当前助手</div>
              <span class="assist-state" :data-tone="assistantStatus(currentAssistant?.key)">
                {{ assistantStatus(currentAssistant?.key) === 'g' ? '已启用' : '待启用' }}
              </span>
            </div>
            <div class="assist-focus-body">
              <div class="assist-img-wrap" v-if="currentAssistant?.image" :key="currentAssistant?.key">
                <img
                  class="assist-intro-img"
                  :key="currentAssistant?.image"
                  :src="currentAssistant.image"
                  :alt="currentAssistant.name"
                />
              </div>

              <!-- 九宫格：放在图片下面 -->
              <div class="assist-selector">
                <div class="assist-selector-title">切换助手 <span class="muted" style="font-weight:400">· 点击切换</span></div>
                <div class="assist-grid">
                  <button
                    v-for="a in aiAssistants"
                    :key="a.key"
                    type="button"
                    class="assist-card"
                    :class="{ active: activeAssistant === a.key }"
                    @click="activeAssistant = a.key"
                  >
                    <div class="assist-ico" :style="{ background: a.bg, color: a.color }">{{ a.ico }}</div>
                    <div class="assist-name">{{ a.shortName }}</div>
                    <span class="assist-dot" :data-tone="assistantStatus(a.key)"></span>
                  </button>
                </div>
              </div>

              <div class="assist-plan-zone" ref="assistPlanZoneRef">
                <div class="assist-selector-title" style="margin-top:12px">
                  今日随访内容 <span class="muted" style="font-weight:400">· Day {{ planDay.replace('day','') }}</span>
                </div>
                <div v-if="planState.loading" class="muted" style="padding:8px 0">计划加载中…</div>
                <div v-else-if="planState.error" class="muted" style="padding:8px 0">{{ planState.error }}</div>
                <div v-else class="assist-plan-list">
                  <details v-for="p in orderedAssistantPlanPanels" :key="p.key" class="assist-plan" :open="p.key === activeAssistant">
                    <summary class="assist-plan-sum">
                      <span class="assist-plan-ico" :style="{ background: p.bg, color: p.color }">{{ p.ico }}</span>
                      <span class="assist-plan-name">{{ p.name }}</span>
                      <span class="assist-plan-mini muted">{{ p.summary || '点击展开查看' }}</span>
                    </summary>
                    <div class="assist-plan-body">
                      <div v-for="(s, idx) in p.sections" :key="idx" class="assist-plan-sec">
                        <div class="assist-plan-sec-h">{{ s.h }}</div>
                        <div class="assist-plan-sec-p">{{ s.p }}</div>
                      </div>
                    </div>
                  </details>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>

      <!-- review tab：健康报告（报告处理主页面） -->
      <div v-else-if="subTab === 'review'" class="rp-page">

        <!-- 统计卡片 -->
        <div class="stat-cards" style="padding:12px 0 0">
          <div class="stat-card">
            <div class="stat-icon" style="background:#eff6ff;color:#2563eb">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">待处理报告</div>
              <div class="stat-val">{{ rpList.filter(r=>r.reportStatus!=='已审核').length }}</div>
              <div class="stat-sub" style="color:#2563eb">较昨日 -2</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#fdf4ff;color:#a21caf">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">AI解析中</div>
              <div class="stat-val">{{ rpList.filter(r=>r.aiStatus==='AI解析中').length }}</div>
              <div class="stat-sub" style="color:#a21caf">较昨日 +1</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#ecfdf5;color:#059669">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">解析完成</div>
              <div class="stat-val">{{ rpList.filter(r=>r.aiStatus==='待审核').length }}</div>
              <div class="stat-sub" style="color:#059669">较昨日 +3</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#fffbeb;color:#d97706">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">待生成报告</div>
              <div class="stat-val">{{ rpList.filter(r=>r.reportStatus==='待审核').length }}</div>
              <div class="stat-sub" style="color:#d97706">较昨日 +1</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#ecfdf5;color:#059669">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">待医生复核</div>
              <div class="stat-val">{{ rpList.filter(r=>r.reportStatus==='待审核').length }}</div>
              <div class="stat-sub" style="color:#059669">较昨日 -1</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#fff1f2;color:#dc2626">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">异常报告</div>
              <div class="stat-val">{{ rpList.filter(r=>r.risk==='高风险').length }}</div>
              <div class="stat-sub" style="color:#dc2626">较昨日 +1</div>
            </div>
          </div>
        </div>

        <!-- 筛选栏 -->
        <div class="rp-filter-bar card">
          <div class="rp-filter-row">
            <div class="rp-filter-item">
              <div class="rp-filter-label">患者姓名/手机号</div>
              <input class="rp-filter-input" v-model="rpSearch" placeholder="请输入姓名或手机号" />
            </div>
            <div class="rp-filter-item">
              <div class="rp-filter-label">患者来源</div>
              <select class="rp-filter-select" v-model="rpSource">
                <option value="">门诊 / 体检中心</option>
                <option>门诊</option>
                <option>体检中心</option>
              </select>
            </div>
            <div class="rp-filter-item">
              <div class="rp-filter-label">结节类型</div>
              <select class="rp-filter-select" v-model="rpNodule">
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
              <select class="rp-filter-select" v-model="rpRisk">
                <option value="">高风险 / 中风险 / 低风险</option>
                <option>高风险</option>
                <option>中风险</option>
                <option>低风险</option>
              </select>
            </div>
            <div class="rp-filter-actions">
              <button class="btn" type="button" @click="rpSearch='';rpSource='';rpNodule='';rpRisk=''">重置</button>
              <button class="primary" type="button">查询</button>
            </div>
          </div>
        </div>

        <!-- 主体：列表 + 详情 -->
        <div class="rp-body">
          <!-- 左：报告列表 -->
          <section class="card rp-list-card">
            <div class="card-head">
              <div class="card-title">报告列表 <span class="rp-count">共 268 条</span></div>
              <div style="display:flex;gap:6px">
                <button class="btn" type="button">
                  <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>导出
                </button>
                <button class="btn" type="button">批量分派</button>
              </div>
            </div>
            <div class="q-table-wrap">
              <table class="q-table">
                <thead>
                  <tr>
                    <th style="width:80px">患者</th>
                    <th style="width:88px">结节类型</th>
                    <th style="width:110px">上传时间</th>
                    <th style="width:80px">AI解析</th>
                    <th style="width:72px">风险</th>
                    <th style="width:60px">负责人</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in rpFilteredList" :key="r.id" class="q-row" :class="{ active: r.id === rpActiveId }" @click="rpActiveId = r.id">
                    <td>
                      <div style="font-weight:700;font-size:13px">{{ r.name }}</div>
                      <div class="muted" style="font-size:11px">{{ r.gender }}/{{ r.age }}岁 · {{ r.phone }}</div>
                    </td>
                    <td><span class="nodule-tag" :data-type="r.noduleKey">{{ r.nodules }}</span></td>
                    <td class="muted" style="font-size:11px">{{ r.uploadAt }}</td>
                    <td><span class="rp-status-tag" :data-s="r.aiStatus">{{ r.aiStatus }}</span></td>
                    <td><span class="pill" :data-tone="r.riskTone">{{ r.risk }}</span></td>
                    <td class="muted">{{ r.owner }}</td>
                    <td>
                      <div style="display:flex;gap:8px">
                        <button class="tbl-act" type="button" @click.stop="openAudit(r)" :disabled="r.reportStatus === '已审核'">{{ r.reportStatus === '已审核' ? '已审核' : '审核' }}</button>
                        <button class="tbl-act" type="button" @click.stop="viewReport(r.id)">查看</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="pager">
              <span class="muted">共 268 条</span>
              <div class="pages">
                <button class="page-btn" type="button">‹</button>
                <button class="page-btn active" type="button">1</button>
                <button class="page-btn" type="button">2</button>
                <button class="page-btn" type="button">3</button>
                <span class="muted">…</span>
                <button class="page-btn" type="button">27</button>
                <button class="page-btn" type="button">›</button>
              </div>
              <div class="muted">10 条/页</div>
            </div>
          </section>

          <!-- 右：报告详情 -->
          <aside class="rp-detail">
            <template v-if="rpActive">
              <!-- 患者基本信息 -->
              <section class="card">
                <div class="card-head"><div class="card-title">报告详情</div></div>
                <div class="rp-detail-info">
                  <div class="rp-info-grid">
                    <div class="rp-info-row"><span class="rp-ik">患者姓名：</span><span class="rp-iv">{{ rpActive.name }}</span></div>
                    <div class="rp-info-row"><span class="rp-ik">来　　源：</span><span class="rp-iv">{{ rpActive.source }}</span></div>
                    <div class="rp-info-row"><span class="rp-ik">性　　别：</span><span class="rp-iv">{{ rpActive.gender }}</span></div>
                    <div class="rp-info-row"><span class="rp-ik">负 责 人：</span><span class="rp-iv">{{ rpActive.owner }}</span></div>
                    <div class="rp-info-row"><span class="rp-ik">年　　龄：</span><span class="rp-iv">{{ rpActive.age }}岁</span></div>
                    <div class="rp-info-row"><span class="rp-ik">报告类型：</span><span class="rp-iv">{{ rpActive.reportType }}</span></div>
                    <div class="rp-info-row"><span class="rp-ik">手 机 号：</span><span class="rp-iv">{{ rpActive.phone }}</span></div>
                    <div class="rp-info-row"><span class="rp-ik">上传时间：</span><span class="rp-iv">{{ rpActive.uploadAt }}</span></div>
                  </div>
                  <button class="rp-doc-btn" type="button">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg>
                  </button>
                </div>
              </section>

              <!-- 处理流程 -->
              <section class="card">
                <div class="card-head"><div class="card-title">处理流程</div></div>
                <div class="rp-flow">
                  <div v-for="(s, i) in rpActive.flow" :key="s.label" class="rp-flow-step" :data-done="s.done" :data-cur="s.cur">
                    <div class="rp-flow-dot">
                      <svg v-if="s.done" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg>
                      <span v-else>{{ i + 1 }}</span>
                    </div>
                    <div class="rp-flow-label">{{ s.label }}</div>
                    <div class="rp-flow-time">{{ s.time }}</div>
                  </div>
                </div>
              </section>

              <!-- 快捷操作 -->
              <section class="card">
                <div class="card-head"><div class="card-title">快捷操作</div></div>
                <div class="rp-actions">
                  <button class="primary" type="button" @click="openAudit(rpActive)" :disabled="rpActive.reportStatus === '已审核'">
                    {{ rpActive.reportStatus === '已审核' ? '已审核' : '审核AI建议' }}
                  </button>
                  <button class="btn" type="button" @click="viewReport(rpActive.id)">查看报告</button>
                  <button class="btn" type="button">创建随访任务</button>
                </div>
              </section>

              <!-- 审核面板：点击"审核AI建议"后展开 -->
              <section v-if="rpAuditId === rpActive.id" class="card rp-audit-panel">
                <div class="card-head"><div class="card-title">审核AI生成内容</div><span class="muted" style="font-size:12px">可直接编辑后点击审核通过</span></div>
                <div class="rp-audit-body">
                  <div class="rp-audit-label">影像解读摘要</div>
                  <textarea class="rp-audit-ta" v-model="rpAuditPara1" rows="4"></textarea>
                  <div class="rp-audit-label" style="margin-top:10px">AI健康建议</div>
                  <textarea class="rp-audit-ta" v-model="rpAuditPara2" rows="4"></textarea>
                  <div style="display:flex;gap:8px;margin-top:12px">
                    <button class="primary" type="button" @click="finalizeReport(rpAuditId)" :disabled="rpFinalizing">{{ rpFinalizing ? '处理中...' : '审核通过' }}</button>
                    <button class="btn" type="button" @click="rpAuditId=''">取消</button>
                  </div>
                </div>
              </section>
            </template>
            <div v-else class="rp-empty">请从左侧选择一条报告</div>
          </aside>
        </div>
      </div>

      <!-- 其它 tab（abnormal）：左侧队列 + 右侧内容 -->
      <div v-else class="pm-detail">
        <!-- 左：患者任务队列 -->
        <section class="card overview-left">
          <div class="card-head">
            <div class="card-title">患者任务队列</div>
            <div class="panel-tools">
              <input class="search" placeholder="姓名/手机号" />
              <select class="stage-select" :value="activeStage" @change="setStage($event.target.value)">
                <option v-for="t in stageTabs" :key="t.key" :value="t.key">{{ t.label }}</option>
              </select>
            </div>
          </div>
          <div class="q-table-wrap">
            <table class="q-table">
              <thead>
                <tr>
                  <th style="width:88px">姓名</th>
                  <th style="width:92px">性别/年龄</th>
                  <th style="width:122px">手机</th>
                  <th style="width:72px">来源</th>
                  <th>结节类型</th>
                  <th style="width:76px">风险</th>
                  <th style="width:168px">当前阶段</th>
                  
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in filteredQueue" :key="p.id" class="q-row" :class="{ active: p.id === activePatientId }" @click="activePatientId = p.id">
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
              <span class="muted">…</span>
              <button class="page-btn" type="button">124</button>
              <button class="page-btn" type="button">›</button>
            </div>
            <div class="muted">10 条/页</div>
          </div>
        </section>

        <!-- 右：当前模块内容 -->
        <aside class="detail-right">
          <section class="card">
            <div class="card-head">
              <div class="card-title">{{ midTitle }}</div>
              <div class="detail-actions">
                <template v-if="subTab === 'abnormal'">
                  <button class="btn" type="button">创建电话随访</button>
                  <button class="primary" type="button">创建复查提醒</button>
                </template>
              </div>
            </div>
            <div class="pad detail-head" :class="{ compact: subTab === 'record' }">
              <div class="dh-left">
                <div class="dh-name">{{ activePatient.name }}</div>
                <div class="muted">{{ activePatient.gender }} · {{ activePatient.age }}岁 · {{ activePatient.phoneMasked }}</div>
              </div>
              <div class="dh-right">
                <span class="pill" :data-tone="activePatient.riskTone">{{ activePatient.risk }}</span>
                <span v-if="subTab !== 'record'" class="tag2">{{ statusLabel(activePatient) }}</span>
              </div>
            </div>
          </section>

          <!-- tab=record：档案与报告 -->
          <template v-if="subTab === 'record'">

            <!-- 档案基础信息 -->
            <section class="card">
              <div class="card-head one-line">
                <div class="card-title">档案信息</div>
                <button class="btn btn-sm" type="button" @click="goRecord">编辑档案</button>
              </div>
              <div class="pad pad-lg">
                <div class="info-grid">
                  <div class="kv"><div class="k">结节类型</div><div class="v">{{ activePatient.nodules }}</div></div>
                  <div class="kv"><div class="k">来源</div><div class="v">{{ sourceLabel(activePatient.source) }}</div></div>
                  
                  <div class="kv"><div class="k">服务状态</div><div class="v">{{ activePatient.serviceStatus }}</div></div>
                </div>
              </div>
            </section>

            <!-- 原始报告 -->
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
                        <button class="icon-more" type="button" @click="toast?.show('文件操作（示意）')">⋯</button>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="empty">
                    <div class="empty-title">暂无原始报告</div>
                    <div class="muted" style="font-size:12px;margin-top:4px">上传检查报告后，AI 将自动解析并生成健康管理报告</div>
                    <div class="empty-actions">
                      <button class="primary" type="button">上传报告</button>
                      <button class="btn" type="button">从门诊系统导入</button>
                    </div>
                  </div>
                </template>
              </div>
            </section>

            <!-- AI 解读摘要 -->
            <section class="card">
              <div class="card-head one-line">
                <div class="card-title">AI 解读摘要</div>
                <div style="display:flex;gap:8px;align-items:center">
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
                  <div class="muted" style="font-size:13px">上传原始报告后，AI 将自动生成解读摘要。</div>
                </template>
              </div>
            </section>

          </template>

          <!-- tab=abnormal：异常与复查 -->
          <template v-else-if="subTab === 'abnormal'">
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

    </section>
  </div>

  <!-- 报告查看弹窗 -->
  <div v-if="rpViewVisible" class="rp-modal-mask" @click.self="rpViewVisible=false">
    <div class="rp-modal">
      <div class="rp-modal-head">
        <div class="rp-modal-title">健康管理报告</div>
        <button class="rp-modal-close" type="button" @click="rpViewVisible=false">✕</button>
      </div>
      <div class="rp-modal-body" v-html="rpViewHtml"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import RecordView from './RecordView.vue'

const router = useRouter()
const route = useRoute()

// 当前子页（必须在 watch 之前声明，避免 immediate 回调引用未初始化变量）
const subTab = ref('queue')

// 子页定义（URL query.tab -> subTab）
const subTabs = [
  { key: 'queue', label: '患者队列' },
  { key: 'record', label: '档案与报告' },
  { key: 'review', label: '健康报告审核' },
  { key: 'followup-plan', label: '随访计划' },
  { key: 'follow', label: 'AI助手随访' },
  { key: 'abnormal', label: '异常与复查' }
]
const allowedSubTabs = new Set(subTabs.map((t) => t.key))

watch(
  () => route.query.tab,
  (tab) => {
    const key = typeof tab === 'string' ? tab : ''
    if (allowedSubTabs.has(key)) subTab.value = key
    else subTab.value = 'queue'
  },
  { immediate: true }
)

/**
 * @isdoc
 * @description 统一切换患者管理子页（写入 URL，并立即更新本地 subTab）
 * @param {string} key
 * @returns {void}
 */
function setSubTab(key) {
  const k = String(key || '').trim()
  if (!allowedSubTabs.has(k)) return
  subTab.value = k
  if (route.name !== 'patient') return
  if (route.query.tab === k) return
  router.replace({ query: { ...route.query, tab: k } })
}

const activeStage = ref('all')
const activePatientId = ref('p1')
const followPatientId = ref('p1')
const followSearch = ref('')
const followRiskFilter = ref('')
const followStageFilter = ref('')
const showAllTimeline = ref(false)
const reviewReject = ref(false)
const activeAssistant = ref('hlp')
const assistPlanZoneRef = ref(null)

const planState = ref({
  loading: true,
  error: '',
  title: '',
  sourceFile: '',
  days: {}
})
const planDay = ref('day1')

// 患者队列（必须提前声明，避免 watcher immediate 引用 TDZ）
const queue = ref([])

// 随访任务工作台（筛选 + 列表 + 详情）
const taskFilters = ref({
  q: '',
  risk: '',
  channel: '',
  owner: '',
  source: '',
  nodule: '',
  status: '',
})

const planLeftMode = ref('patients') // patients | tasks

const followTasks = ref([])
const activeTaskId = ref('')
const selectedTaskIds = ref(new Set())

const activeTask = computed(() => (followTasks.value || []).find((t) => t.id === activeTaskId.value) || null)

const filteredTasks = computed(() => {
  const q = String(taskFilters.value.q || '').trim()
  const risk = String(taskFilters.value.risk || '')
  const channel = String(taskFilters.value.channel || '')
  const owner = String(taskFilters.value.owner || '').trim()
  const status = String(taskFilters.value.status || '')
  const nodule = String(taskFilters.value.nodule || '')

  return (followTasks.value || []).filter((t) => {
    if (q) {
      const hay = `${t.patientName} ${t.phoneMasked}`.toLowerCase()
      if (!hay.includes(q.toLowerCase())) return false
    }
    if (risk && t.risk !== risk) return false
    if (channel && t.channel !== channel) return false
    if (owner && !String(t.owner || '').includes(owner)) return false
    if (status && t.status !== status) return false
    if (nodule && !String(t.nodules || '').includes(nodule)) return false
    return true
  })
})

const filteredPlanPatients = computed(() => {
  const q = String(taskFilters.value.q || '').trim()
  const risk = String(taskFilters.value.risk || '')
  const owner = String(taskFilters.value.owner || '').trim()
  return (planPatients.value || []).filter((p) => {
    if (q) {
      const hay = `${p.name} ${p.phoneMasked}`.toLowerCase()
      if (!hay.includes(q.toLowerCase())) return false
    }
    if (risk && p.risk !== risk) return false
    if (owner && !String(p.owner || '').includes(owner)) return false
    return true
  })
})

watch(
  () => (followTasks.value || []).length,
  (n) => {
    if (n > 0 && planLeftMode.value === 'patients') planLeftMode.value = 'tasks'
  }
)

const allTasksSelected = computed(() => {
  const list = filteredTasks.value || []
  if (!list.length) return false
  return list.every((t) => selectedTaskIds.value.has(t.id))
})

// 初始：把“已存在 planTask 的患者”放进任务队列（示意）
watch(
  () => subTab.value,
  (k) => {
    if (k !== 'followup-plan') return
    if ((followTasks.value || []).length) return
    const seeded = (queue.value || [])
      .filter((p) => p?.planTask)
      .slice(0, 8)
      .map((p) => makeTaskFromPatient(p))
    followTasks.value = seeded
    if (seeded[0]) selectTask(seeded[0].id)
  },
  { immediate: true }
)

/**
 * @isdoc
 * @description 加载随访计划（从 public/plans 读取 JSON）
 * @returns {Promise<void>}
 */
async function loadPlan() {
  planState.value.loading = true
  planState.value.error = ''
  try {
    const res = await fetch('/plans/thyroid-lung-psych.json', { cache: 'no-cache' })
    if (!res.ok) throw new Error(`加载计划失败：${res.status}`)
    const data = await res.json()
    planState.value = {
      loading: false,
      error: '',
      title: data?.title ?? '',
      sourceFile: data?.sourceFile ?? '',
      days: data?.days ?? {}
    }
    if (!planState.value.days?.[planDay.value]) {
      const first = Object.keys(planState.value.days ?? {})[0]
      if (first) planDay.value = first
    }
  } catch (e) {
    planState.value.loading = false
    planState.value.error = e?.message || '加载计划失败'
  }
}

/**
 * @isdoc
 * @description 重置筛选条件
 * @returns {void}
 */
function resetTaskFilters() {
  taskFilters.value = { q: '', risk: '', channel: '', owner: '' }
}

/**
 * @isdoc
 * @description 任务状态展示文案
 * @param {'draft'|'assigned'|'executing'|'review'|'done'} s
 * @returns {string}
 */
function taskStatusLabel(s) {
  // 状态收敛：仅保留 待分派 / 待执行 / 已完成
  if (s === 'draft') return '待分派'
  if (s === 'done') return '已完成'
  // executing/review/assigned 统一归为“待执行”
  return '待执行'
  return '—'
}

/**
 * @isdoc
 * @description 选择任务并联动患者
 * @param {string} id
 * @returns {void}
 */
function selectTask(id) {
  activeTaskId.value = id
  const t = (followTasks.value || []).find((x) => x.id === id)
  if (t?.patientId) activePatientId.value = t.patientId
}

/**
 * @isdoc
 * @description 勾选任务
 * @param {string} id
 * @param {boolean} checked
 * @returns {void}
 */
function toggleTaskSelection(id, checked) {
  const s = new Set(selectedTaskIds.value)
  if (checked) s.add(id)
  else s.delete(id)
  selectedTaskIds.value = s
}

/**
 * @isdoc
 * @description 全选/取消全选
 * @returns {void}
 */
function toggleAllTaskSelection() {
  const list = filteredTasks.value || []
  const s = new Set(selectedTaskIds.value)
  if (allTasksSelected.value) {
    list.forEach((t) => s.delete(t.id))
  } else {
    list.forEach((t) => s.add(t.id))
  }
  selectedTaskIds.value = s
}

/**
 * @isdoc
 * @description 批量分派（示意：使用输入框）
 * @returns {void}
 */
function bulkAssignSelected() {
  const owner = window.prompt('输入负责人（示例：运营A/张医生）：', taskFilters.value.owner || '') || ''
  if (!owner.trim()) return
  const ids = Array.from(selectedTaskIds.value)
  followTasks.value = (followTasks.value || []).map((t) => {
    if (!ids.includes(t.id)) return t
    const next = { ...t, owner, status: t.status === 'draft' ? 'assigned' : t.status }
    next.logs = Array.isArray(next.logs) ? next.logs : []
    next.logs.unshift({ at: '现在', by: '系统', action: '批量分派', note: `负责人：${owner}` })
    return next
  })
}

/**
 * @isdoc
 * @description 由患者+表单生成一条任务
 * @param {any} p
 * @returns {any}
 */
function makeTaskFromPatient(p) {
  const id = `t_${Date.now()}_${Math.random().toString(16).slice(2, 6)}`
  return {
    id,
    patientId: p.id,
    patientName: p.name,
    gender: p.gender,
    age: p.age,
    phoneMasked: p.phoneMasked,
    risk: p.risk,
    riskTone: p.riskTone,
    owner: p.owner || '',
    channel: draft.value.channel,
    cycle: draft.value.cycle,
    reminder: draft.value.reminder,
    day: planDay.value,
    status: p.owner ? 'assigned' : 'draft',
    kbSnapshot: JSON.parse(JSON.stringify(draft.value.kbEnabled || {})),
    logs: [{ at: '现在', by: '医生/运营', action: '创建任务', note: `Day ${planDay.value.replace('day', '')} · ${draft.value.channel} · ${draft.value.cycle}` }],
  }
}

/**
 * @isdoc
 * @description 新建任务入口（基于当前患者）
 * @returns {void}
 */
function openNewTaskFromActive() {
  if (!activePatient.value) return
  const t = makeTaskFromPatient(activePatient.value)
  followTasks.value = [t, ...(followTasks.value || [])]
  selectTask(t.id)
}

/**
 * @isdoc
 * @description 从患者行创建任务并进入详情
 * @param {any} p
 * @returns {void}
 */
function createTaskForPatient(p) {
  if (!p?.id) return
  activePatientId.value = p.id
  const t = makeTaskFromPatient(p)
  followTasks.value = [t, ...(followTasks.value || [])]
  selectTask(t.id)
  planLeftMode.value = 'tasks'
}

/**
 * @isdoc
 * @description 任务流程节点（示意）
 * @param {any} t
 * @returns {{k:string,label:string,state:'todo'|'doing'|'done'}[]}
 */
function taskFlowNodes(t) {
  const s = t?.status || 'draft'
  const at = (k) => {
    if (s === 'draft') return k === 'assign' ? 'doing' : 'todo'
    if (s === 'assigned') return (k === 'assign' ? 'done' : k === 'execute' ? 'doing' : 'todo')
    if (s === 'executing') return (k === 'assign' ? 'done' : k === 'execute' ? 'done' : k === 'review' ? 'doing' : 'todo')
    if (s === 'review') return (k === 'assign' || k === 'execute' ? 'done' : k === 'review' ? 'done' : k === 'done' ? 'doing' : 'todo')
    if (s === 'done') return (k === 'assign' || k === 'execute' || k === 'review' || k === 'done') ? 'done' : 'todo'
    return 'todo'
  }
  return [
    { k: 'assign', label: '分派', state: at('assign') },
    { k: 'execute', label: '执行', state: at('execute') },
    { k: 'review', label: '复核', state: at('review') },
    { k: 'done', label: '闭环', state: at('done') },
  ]
}

/**
 * @isdoc
 * @description 推进任务状态并写入日志
 * @param {'assign'|'execute'|'review'|'done'} action
 * @returns {void}
 */
function advanceTask(action) {
  const t = activeTask.value
  if (!t) return
  let nextStatus = t.status
  if (action === 'assign') nextStatus = 'assigned'
  if (action === 'execute') nextStatus = 'executing'
  if (action === 'review') nextStatus = 'review'
  if (action === 'done') nextStatus = 'done'

  const note = window.prompt('补充说明（可选）：', '') || ''
  followTasks.value = (followTasks.value || []).map((x) => {
    if (x.id !== t.id) return x
    const y = { ...x, status: nextStatus }
    y.logs = Array.isArray(y.logs) ? y.logs : []
    y.logs.unshift({ at: '现在', by: '操作员', action: `状态变更：${taskStatusLabel(nextStatus)}`, note })
    return y
  })
}

onMounted(() => {
  loadPlan()
  loadPatients()
  loadReports()
})

const planDayList = computed(() => {
  const keys = Object.keys(planState.value.days ?? {})
  return keys.sort((a, b) => Number(a.replace('day', '')) - Number(b.replace('day', '')))
})

const currentPlanRows = computed(() => planState.value.days?.[planDay.value] ?? [])

function pickFirst(prefix) {
  const hit = currentPlanRows.value.find((r) => {
    const s = String(r?.summary ?? '').trim()
    return s === prefix || s.includes(prefix)
  })
  if (!hit) return ''
  const s = String(hit.summary ?? '').trim()
  const r = String(hit.remind ?? '').trim()
  // 这类行通常 summary 只是“运动/心理”，正文在 remind
  const text = (s === prefix || s.length <= 3) ? r : (r ? `${s}\n${r}` : s)
  // 取首段作为“要点”
  return text.split('\n').map((x) => x.trim()).filter(Boolean)[0] || text
}

const planQuick = computed(() => {
  const sport = pickFirst('运动')
  const psych = pickFirst('心理')
  return { sport, psych }
})

const KB_DEFAULT_ITEMS = [
  { key: 'breakfast', label: '早餐建议' },
  { key: 'lunch', label: '午餐建议' },
  { key: 'dinner', label: '晚餐建议' },
  { key: 'knowledgeCard', label: '知识卡' },
  { key: 'medication', label: '用药/禁忌提醒' },
  { key: 'sport', label: '运动处方' },
  { key: 'psych', label: '心理干预' },
  { key: 'questionnaire', label: '随访问卷' },
  { key: 'reminderScript', label: '提醒话术' },
  { key: 'escalationRule', label: '异常转人工规则' },
]

const draft = ref({
  cycle: '6个月',
  channel: '企微/电话/小程序',
  reminder: '到期前3天提醒',
  kbEnabled: {
    breakfast: true,
    lunch: true,
    dinner: true,
    knowledgeCard: true,
    medication: true,
    sport: true,
    psych: true,
    questionnaire: false,
    reminderScript: true,
    escalationRule: true,
  },
  /** @type {Record<string, string>} */
  kbOverrides: {},
  /** @type {{ key: string, label: string, text: string, enabled: boolean }[]} */
  kbCustom: [],
  note: ''
})

const kbUi = ref({
  editorOpen: false,
  editorKey: '',
  editorLabel: '',
  editorText: '',
  managerOpen: false,
  drawerOpen: false,
  drawerGroup: 'diet',
  drawerQuery: '',
  drawerActiveKey: '',
})

const kbImportInputRef = ref(null)
const kbUploadInputRef = ref(null)

/**
 * @isdoc
 * @description 将表单草稿应用到当前患者计划（保存到内存）
 * @returns {void}
 */
function applyDraftToPlan() {
  const p = activePatient.value
  if (!p) return
  const meals = pickMeals()
  const knowledge = pickKnowledge()
  const sport = pickSport()
  const psych = pickPsych()
  const cautions = pickCautions()
  const intro = pickIntro()

  const kbText = (key) => {
    const ov = String(draft.value.kbOverrides?.[key] || '').trim()
    if (ov) return ov
    if (key === 'breakfast') return meals.breakfast || ''
    if (key === 'lunch') return meals.lunch || ''
    if (key === 'dinner') return meals.dinner || ''
    if (key === 'knowledgeCard') return knowledge || ''
    if (key === 'medication') return cautions || knowledge || ''
    if (key === 'sport') return sport || ''
    if (key === 'psych') return psych || ''
    if (key === 'questionnaire') return [
      '1）今天是否有持续咳嗽/胸闷/气短？（无/轻/中/重）',
      '2）是否有吞咽不适/声音嘶哑/颈部压迫感？（无/有）',
      '3）睡眠与情绪状态如何？（良好/一般/较差）',
      '4）是否按计划完成运动与饮食？（是/否）',
    ].join('\n')
    if (key === 'reminderScript') return [
      `您好，已为您更新 Day ${planDay.value.replace('day', '')} 随访任务。`,
      `请按“${draft.value.cycle}复查周期”执行，并完成饮食/运动/心理打卡。`,
      '如出现持续咳嗽、胸痛、咳血、明显吞咽困难等情况，请及时就医并联系医生。',
    ].join('\n')
    if (key === 'escalationRule') return [
      '异常转人工/医生规则（示意）：',
      '- 出现咳血/胸痛/呼吸困难/持续发热 → 立即转医生',
      '- 出现声音嘶哑加重/吞咽困难 → 48小时内转医生评估',
      '- 连续 3 天未打卡或失联 → 转人工电话随访',
    ].join('\n')
    return ''
  }

  const enabledKeys = Object.entries(draft.value.kbEnabled || {})
    .filter(([, v]) => !!v)
    .map(([k]) => k)

  const customEnabled = (draft.value.kbCustom || []).filter((x) => !!x.enabled)

  p.planTask = {
    day: planDay.value,
    cycle: draft.value.cycle,
    channel: draft.value.channel,
    reminder: draft.value.reminder,
    kb: {
      breakfast: enabledKeys.includes('breakfast') ? kbText('breakfast') : null,
      lunch: enabledKeys.includes('lunch') ? kbText('lunch') : null,
      dinner: enabledKeys.includes('dinner') ? kbText('dinner') : null,
      knowledgeCard: enabledKeys.includes('knowledgeCard') ? kbText('knowledgeCard') : null,
      medication: enabledKeys.includes('medication') ? kbText('medication') : null,
      sport: enabledKeys.includes('sport') ? kbText('sport') : null,
      psych: enabledKeys.includes('psych') ? kbText('psych') : null,
      questionnaire: enabledKeys.includes('questionnaire') ? kbText('questionnaire') : null,
      reminderScript: enabledKeys.includes('reminderScript') ? kbText('reminderScript') : null,
      escalationRule: enabledKeys.includes('escalationRule') ? kbText('escalationRule') : null,
      custom: customEnabled.map((x) => ({ key: x.key, label: x.label, text: String(x.text || '').trim() })),
      goal: intro || null,
    },
    note: draft.value.note
  }
  // 也同步写入 plan（用于后续开启 AI随访）
  savePlanForActive()
  p.timeline = Array.isArray(p.timeline) ? p.timeline : []
  p.timeline.push({ at: '现在', tone: 'b', text: `生成随访任务：Day ${planDay.value.replace('day','')}`, meta: '已保存' })

  // 同步生成/更新随访任务队列（工作台左侧列表）
  const newTask = makeTaskFromPatient(p)
  followTasks.value = [newTask, ...(followTasks.value || [])]
  selectTask(newTask.id)
}

function pickRowLike(q) {
  const key = String(q || '').trim()
  if (!key) return null
  return currentPlanRows.value.find((r) => String(r?.summary ?? '').includes(key)) || null
}

function pickRowText(q) {
  const hit = pickRowLike(q)
  if (!hit) return ''
  const s = String(hit.summary ?? '').trim()
  const r = String(hit.remind ?? '').trim()
  if (r && (s === q || s.length <= 6)) return r
  return r ? `${s}\n${r}` : s
}

function pickIntro() {
  const first = currentPlanRows.value.find((r) => !String(r?.time ?? '').trim()) || currentPlanRows.value[0]
  const s = String(first?.summary ?? '').trim()
  const r = String(first?.remind ?? '').trim()
  return r ? `${s}\n${r}`.trim() : s
}

function pickMeals() {
  const breakfast = pickRowText('早餐打卡跟进')
  const lunch = pickRowText('午餐打卡跟进')
  const dinner = pickRowText('晚餐打卡跟进')
  return { breakfast, lunch, dinner }
}

function pickKnowledge() {
  // 表里可能是“知识卡”或“DayX 知识卡…”
  return pickRowText('知识卡')
}

function pickSport() {
  return pickRowText('运动')
}

function pickPsych() {
  return pickRowText('心理')
}

function pickCautions() {
  const t = pickKnowledge()
  if (!t) return ''
  const lines = t.split('\n').map((x) => x.trim()).filter(Boolean)
  const hit = lines.filter((x) => /^注意|^避免|^提示|^推荐|^空腹服药/.test(x)).slice(0, 6)
  return hit.join('\n') || lines.slice(0, 4).join('\n')
}

/**
 * @isdoc
 * @description 获取知识库条目正文（含覆盖与动态生成）
 * @param {string} key
 * @returns {string}
 */
function getKbText(key) {
  const ov = String(draft.value.kbOverrides?.[key] || '').trim()
  if (ov) return ov

  const meals = pickMeals()
  const knowledge = pickKnowledge()
  const sport = pickSport()
  const psych = pickPsych()
  const cautions = pickCautions()

  if (key === 'breakfast') return meals.breakfast || ''
  if (key === 'lunch') return meals.lunch || ''
  if (key === 'dinner') return meals.dinner || ''
  if (key === 'knowledgeCard') return knowledge || ''
  if (key === 'medication') return cautions || knowledge || ''
  if (key === 'sport') return sport || ''
  if (key === 'psych') return psych || ''
  if (key === 'questionnaire') return [
    '1）今天是否有持续咳嗽/胸闷/气短？（无/轻/中/重）',
    '2）是否有吞咽不适/声音嘶哑/颈部压迫感？（无/有）',
    '3）睡眠与情绪状态如何？（良好/一般/较差）',
    '4）是否按计划完成运动与饮食？（是/否）',
  ].join('\n')
  if (key === 'reminderScript') return [
    `您好，已为您更新 Day ${planDay.value.replace('day', '')} 随访任务。`,
    `请按“${draft.value.cycle}复查周期”执行，并完成饮食/运动/心理打卡。`,
    '如出现持续咳嗽、胸痛、咳血、明显吞咽困难等情况，请及时就医并联系医生。',
  ].join('\n')
  if (key === 'escalationRule') return [
    '异常转人工/医生规则（示意）：',
    '- 出现咳血/胸痛/呼吸困难/持续发热 → 立即转医生',
    '- 出现声音嘶哑加重/吞咽困难 → 48小时内转医生评估',
    '- 连续 3 天未打卡或失联 → 转人工电话随访',
  ].join('\n')
  return ''
}

/**
 * @isdoc
 * @description 切换知识库条目启用状态
 * @param {string} key
 * @param {boolean} val
 * @returns {void}
 */
function setKbEnabled(key, val) {
  draft.value.kbEnabled = draft.value.kbEnabled || {}
  draft.value.kbEnabled[key] = !!val
}

/**
 * @isdoc
 * @description 切换自定义条目启用状态
 * @param {string} key
 * @param {boolean} val
 * @returns {void}
 */
function setCustomEnabled(key, val) {
  draft.value.kbCustom = Array.isArray(draft.value.kbCustom) ? draft.value.kbCustom : []
  const hit = draft.value.kbCustom.find((x) => x.key === key)
  if (hit) hit.enabled = !!val
}

/**
 * @isdoc
 * @description 打开编辑器（支持新增/修改）
 * @param {{ key?: string, label?: string, text?: string, isCustom?: boolean }=} opt
 * @returns {void}
 */
function openKbEditor(opt = {}) {
  const key = String(opt.key || '').trim()
  const label = String(opt.label || '').trim()
  kbUi.value.editorOpen = true
  kbUi.value.editorKey = key
  kbUi.value.editorLabel = label || (KB_DEFAULT_ITEMS.find((x) => x.key === key)?.label || '自定义条目')
  kbUi.value.editorText = String(opt.text ?? (key ? getKbText(key) : '')).trim()
}

/**
 * @isdoc
 * @description 保存编辑内容到覆盖/自定义条目
 * @returns {void}
 */
function saveKbEditor() {
  const key = String(kbUi.value.editorKey || '').trim()
  const label = String(kbUi.value.editorLabel || '').trim() || '自定义条目'
  const text = String(kbUi.value.editorText || '').trim()

  if (key && KB_DEFAULT_ITEMS.some((x) => x.key === key)) {
    draft.value.kbOverrides = draft.value.kbOverrides || {}
    draft.value.kbOverrides[key] = text
    setKbEnabled(key, true)
  } else {
    const newKey = key || `custom_${Date.now()}`
    draft.value.kbCustom = Array.isArray(draft.value.kbCustom) ? draft.value.kbCustom : []
    const idx = draft.value.kbCustom.findIndex((x) => x.key === newKey)
    const item = { key: newKey, label, text, enabled: true }
    if (idx >= 0) draft.value.kbCustom.splice(idx, 1, item)
    else draft.value.kbCustom.unshift(item)
  }

  kbUi.value.editorOpen = false
}

const kbItems = computed(() => {
  const base = KB_DEFAULT_ITEMS.map((x) => ({
    key: x.key,
    label: x.label,
    enabled: !!draft.value.kbEnabled?.[x.key],
    text: getKbText(x.key),
    isCustom: false,
  }))
  const custom = (draft.value.kbCustom || []).map((x) => ({
    key: x.key,
    label: x.label || '自定义条目',
    enabled: !!x.enabled,
    text: String(x.text || '').trim(),
    isCustom: true,
  }))
  return [...base, ...custom]
})

const KB_GROUPS = [
  { key: 'diet', label: '饮食', items: ['breakfast', 'lunch', 'dinner'] },
  { key: 'knowledge', label: '知识卡', items: ['knowledgeCard', 'medication'] },
  { key: 'sport', label: '运动', items: ['sport'] },
  { key: 'psych', label: '心理', items: ['psych'] },
  { key: 'ops', label: '运营工具', items: ['questionnaire', 'reminderScript', 'escalationRule'] },
  { key: 'custom', label: '自定义', items: [] },
]

const kbSelected = computed(() => kbItems.value.filter((x) => x.enabled))

const kbSelectedByGroup = computed(() => {
  const map = {}
  for (const g of KB_GROUPS) map[g.key] = []
  kbSelected.value.forEach((it) => {
    const baseKey = it.isCustom ? 'custom' : (KB_GROUPS.find((g) => g.items.includes(it.key))?.key || 'ops')
    map[baseKey] = map[baseKey] || []
    map[baseKey].push(it)
  })
  return map
})

/**
 * @isdoc
 * @description 打开知识库抽屉（分组选择/预览）
 * @param {string} groupKey
 * @returns {void}
 */
function openKbDrawer(groupKey) {
  kbUi.value.drawerOpen = true
  kbUi.value.drawerGroup = groupKey || 'diet'
  kbUi.value.drawerQuery = ''
  const first = (kbDrawerItems.value || [])[0]
  kbUi.value.drawerActiveKey = first?.key || ''
}

const kbDrawerItems = computed(() => {
  const g = String(kbUi.value.drawerGroup || 'diet')
  const q = String(kbUi.value.drawerQuery || '').trim().toLowerCase()

  const group = KB_GROUPS.find((x) => x.key === g) || KB_GROUPS[0]
  const inGroup = (it) => {
    if (g === 'custom') return !!it.isCustom
    if (it.isCustom) return false
    return group.items.includes(it.key)
  }
  return kbItems.value
    .filter(inGroup)
    .filter((it) => (q ? `${it.label} ${it.key}`.toLowerCase().includes(q) : true))
})

const kbDrawerActive = computed(() => {
  const key = String(kbUi.value.drawerActiveKey || '')
  return kbDrawerItems.value.find((x) => x.key === key) || kbDrawerItems.value[0] || null
})

/**
 * @isdoc
 * @description 导入知识库条目（JSON）
 * @param {Event} e
 * @returns {void}
 */
function onKbImport(e) {
  const input = e?.target
  const file = input?.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    try {
      const json = JSON.parse(String(reader.result || '{}'))
      const items = Array.isArray(json?.items) ? json.items : (Array.isArray(json) ? json : [])
      const normalized = items
        .map((x) => ({
          key: String(x?.key || '').trim() || `custom_${Date.now()}_${Math.random().toString(16).slice(2, 6)}`,
          label: String(x?.label || '自定义条目').trim(),
          text: String(x?.text || '').trim(),
          enabled: x?.enabled !== false,
        }))
        .filter((x) => x.text || x.label)
      draft.value.kbCustom = [...normalized, ...(draft.value.kbCustom || [])]
    } catch (err) {
      // 轻量 demo：忽略错误
    }
  }
  reader.readAsText(file)
  if (input) input.value = ''
}

/**
 * @isdoc
 * @description 上传原表（示意：仅记录文件名）
 * @param {Event} e
 * @returns {void}
 */
function onKbUpload(e) {
  const input = e?.target
  const file = input?.files?.[0]
  if (!file) return
  draft.value.note = `${draft.value.note || ''}${draft.value.note ? '\n' : ''}已上传原表：${file.name}`.trim()
  if (input) input.value = ''
}

const assistantPlanPanels = computed(() => {
  const meals = pickMeals()
  const intro = pickIntro()
  const knowledge = pickKnowledge()
  const sport = pickSport()
  const psych = pickPsych()
  const cautions = pickCautions()

  const mk = (key, name, ico, bg, color, summary, sections) => ({ key, name, ico, bg, color, summary, sections })

  return [
    mk('hlp', '名医分身', '名', '#eef5ff', '#155eef', '知识卡/重点提示', [
      { h: '知识卡（重点）', p: knowledge || '—' },
      { h: '注意事项', p: cautions || '—' },
    ]),
    mk('health', '健康管理', '健', '#ecfff3', '#16a34a', '三餐+健康习惯', [
      { h: '早餐', p: meals.breakfast || '—' },
      { h: '午餐', p: meals.lunch || '—' },
      { h: '晚餐', p: meals.dinner || '—' },
      { h: '今日提醒', p: cautions || '—' },
    ]),
    mk('pharma', 'AI药师', '药', '#fff7ed', '#f97316', '用药/禁忌提醒', [
      { h: '用药与禁忌（从知识卡提取）', p: cautions || knowledge || '—' },
    ]),
    mk('chronic', '慢病管理', '慢', '#f5f3ff', '#8b5cf6', '运动+代谢管理', [
      { h: '运动处方', p: sport || '—' },
      { h: '饮食与代谢提示', p: cautions || '—' },
    ]),
    mk('psych', '心理咨询', '心', '#fff1f2', '#ef4444', '心理干预', [
      { h: '心理练习', p: psych || '—' },
    ]),
    mk('rehab', '运动康复', '动', '#ecfff3', '#16a34a', '运动训练', [
      { h: '今日运动', p: sport || '—' },
    ]),
    mk('lifestyle', '生活规划', '活', '#fffbeb', '#d97706', '今日目标+习惯', [
      { h: '今日目标', p: intro || '—' },
      { h: '习惯提醒', p: cautions || '—' },
    ]),
    mk('tcm', '中医药膳', '膳', '#f5f0ff', '#8b5cf6', '中医调理要点', [
      { h: '调理思路', p: intro || '—' },
      { h: '药膳/饮食建议', p: meals.breakfast || meals.dinner || '—' },
    ]),
    mk('welfare', '健康福利', '福', '#ecfdf5', '#16a34a', '提醒与权益', [
      { h: '随访提醒', p: `已为您生成 Day ${planDay.value.replace('day','')} 随访内容，可按计划执行并打卡。` },
      { h: '关键提醒', p: cautions || '—' },
    ]),
  ]
})

const orderedAssistantPlanPanels = computed(() => {
  const list = assistantPlanPanels.value || []
  const key = activeAssistant.value
  const idx = list.findIndex((x) => x.key === key)
  if (idx <= 0) return list
  return [list[idx], ...list.slice(0, idx), ...list.slice(idx + 1)]
})

watch(
  () => activeAssistant.value,
  async () => {
    await nextTick()
    assistPlanZoneRef.value?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
  }
)

/**
 * @isdoc
 * @description 将当前选择的 Day 与计划摘要保存到当前患者对象（mock：写入内存）
 * @returns {void}
 */
function savePlanForActive() {
  const p = activePatient.value
  if (!p) return
  p.plan = {
    title: planState.value.title || '甲状腺结节合并肺结节健康管理方案（含心理）',
    day: planDay.value,
    sport: planQuick.value.sport,
    psych: planQuick.value.psych,
  }
  p.timeline = Array.isArray(p.timeline) ? p.timeline : []
  p.timeline.push({ at: '现在', tone: 'b', text: `更新随访计划：Day ${planDay.value.replace('day', '')}`, meta: '已保存' })
}

/**
 * @isdoc
 * @description 保存患者表单（mock：写入时间线，提示已保存）
 * @returns {void}
 */
function savePatientForm() {
  const p = activePatient.value
  if (!p) return
  p.timeline = Array.isArray(p.timeline) ? p.timeline : []
  p.timeline.push({ at: '现在', tone: 'b', text: '更新患者信息', meta: '已保存' })
}

/**
 * @isdoc
 * @description 开启 AI 随访：状态切换为 follow，并跳转到 AI随访页展示
 * @returns {void}
 */
function startAiFollowup() {
  const p = activePatient.value
  if (!p) return
  // 先保存一次，保证计划存在
  savePlanForActive()

  p.stage = 'follow'
  p.stageLabel = 'AI随访中'
  p.serviceStatus = 'AI随访中'
  p.nextStep = '按计划随访'

  p.timeline = Array.isArray(p.timeline) ? p.timeline : []
  p.timeline.push({ at: '现在', tone: 'g', text: '开启 AI随访', meta: `Day ${planDay.value.replace('day', '')}` })

  // 在聊天里塞一条“AI随访建议”提示（若结构存在）
  p.chat = Array.isArray(p.chat) ? p.chat : []
  p.chat.push({ from: 'ai', text: `已开启AI随访（Day ${planDay.value.replace('day', '')}）。我将按随访任务向您推送摘要与打卡入口。` })
  p.chat.push({ type: 'card', ico: '🧾', title: `查看随访任务（Day ${planDay.value.replace('day', '')}）`, sub: '随访任务已生成 · 点击查看' })

  followPatientId.value = p.id
  setSubTab('follow')
}

const aiAssistants = [
  {
    key: 'hlp', name: 'AI名医数字分身', shortName: '名医分身', ico: '名', bg: '#eef5ff', color: '#155eef',
    image: '/images/ai-assistants/demo01.png',
    tagline: '专家解读 · 权威科普 · 复查建议，为患者提供专业级随访指导',
    capabilities: ['专家知识问答', '报告重点解读', '复查建议生成', '就诊提醒判断', '阶段性健康规划'],
    workflow: ['患者问题', 'AI专家解读', '生成建议', '医生确认', '推送患者'],
    stats: { reach: 89, read: 76, reply: 34, transfer: 3 },
    desc: '阶段性健康规划、高风险路径建议、专家级随访指导',
    scene: '高风险随访 · 专家路径规划',
    tpl: '您好，根据您的检查结果，我为您制定了个性化随访路径，请查阅并按计划执行。',
    execLog: [
      { at: '08:30', action: '推送高风险随访路径', note: '肺结节高风险 · 3个月复查方案', state: '已读', tone: 'g' },
      { at: '昨天 09:00', action: '发送阶段性健康建议', note: '第2阶段随访建议', state: '已送达', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI名医数字分身，将为您提供专业的随访指导。' },
      { from: 'ai', text: '根据您的检查结果，肺部磨玻璃结节 8mm，建议按高风险路径随访：3个月复查胸部CT，同时注意以下事项。' },
      { type: 'card', ico: '🩺', title: '查看个性化随访路径', sub: '高风险 · 专家级随访方案' },
      { from: 'patient', text: '请问我需要做什么准备？' },
      { from: 'ai', text: '复查前无需特殊准备，建议穿宽松衣物，避免佩戴金属饰品。如有症状变化请提前告知医生。' }
    ]
  },
  {
    key: 'health', name: 'AI健康管理师', shortName: '健康管理', ico: '健', bg: '#ecfff3', color: '#16a34a',
    image: '/images/ai-assistants/demo02.png',
    tagline: '随访提醒 · 复查计划 · 健康档案，全程陪伴患者健康管理',
    capabilities: ['随访计划制定', '复查提醒推送', '健康档案管理', '症状自评问卷', '健康报告解读'],
    workflow: ['档案建立', '随访计划', '定期提醒', '问卷收集', '报告更新'],
    stats: { reach: 124, read: 108, reply: 67, transfer: 2 },
    desc: '随访提醒、复查计划、健康档案管理',
    scene: '结节随访 · 复查提醒',
    tpl: '您好，您的随访计划已更新，请按时完成复查。如有不适请及时联系我们。',
    execLog: [
      { at: '09:20', action: '发送复查提醒', note: '3个月复查胸部CT', state: '已送达', tone: 'g' },
      { at: '昨天 15:00', action: '发送随访问卷', note: '症状自评问卷', state: '已读', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，您的体检报告已完成解读，以下是您的健康管理报告摘要，请查阅。' },
      { type: 'card', ico: '📋', title: '查看健康管理报告', sub: '健康管理报告 · 点击查看详情' },
      { from: 'ai', text: '根据您的检查结果，建议您 3 个月后复查胸部 CT。如有持续咳嗽或胸痛，请及时就医。' },
      { from: 'patient', text: '好的，我知道了，谢谢。' },
      { from: 'ai', text: '已为您创建复查提醒，届时将通过小程序和企业微信通知您。祝您健康！' }
    ]
  },
  {
    key: 'pharma', name: 'AI药师', shortName: 'AI药师', ico: '药', bg: '#fff7ed', color: '#f97316',
    image: '/images/ai-assistants/demo03.png',
    tagline: '用药核对 · 服药提醒 · 药物相互作用，守护患者用药安全',
    capabilities: ['用药计划核对', '服药定时提醒', '药物相互作用提示', '不良反应询问', '漏服处理建议'],
    workflow: ['用药档案', '服药提醒', '依从性跟踪', '异常上报', '医生确认'],
    stats: { reach: 56, read: 49, reply: 28, transfer: 1 },
    desc: '用药核对、服药提醒、药物相互作用提示',
    scene: '用药管理 · 服药提醒',
    tpl: '您好，您的用药计划已更新，请按时服药，如有不适请及时告知。',
    execLog: [
      { at: '08:00', action: '发送晨间服药提醒', note: '阿司匹林 100mg', state: '已读', tone: 'g' },
      { at: '昨天 20:00', action: '发送晚间服药提醒', note: '降压药', state: '已送达', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI药师，负责协助您管理用药计划。' },
      { from: 'ai', text: '根据您的档案，您目前正在服用阿司匹林和降压药，请注意按时服药。阿司匹林建议饭后服用，降压药建议每天固定时间服用。' },
      { type: 'card', ico: '💊', title: '查看用药计划', sub: '点击查看完整用药清单' },
      { from: 'patient', text: '我最近忘记吃药了，有影响吗？' },
      { from: 'ai', text: '偶尔漏服影响不大，但请尽量保持规律服药。如果连续漏服超过 3 天，建议联系您的主治医生。' }
    ]
  },
  {
    key: 'chronic', name: 'AI慢病管理师', shortName: '慢病管理', ico: '慢', bg: '#f5f3ff', color: '#8b5cf6',
    image: '/images/ai-assistants/demo04.png',
    tagline: '合并慢病评估 · 干预方案 · 长期管理，助力慢病患者全程管控',
    capabilities: ['慢病风险评估', '血压血糖监测提醒', '干预方案推送', '复诊提醒', '异常指标预警'],
    workflow: ['慢病建档', '指标监测', '异常预警', '干预推送', '复诊跟踪'],
    stats: { reach: 78, read: 65, reply: 41, transfer: 5 },
    desc: '合并慢病评估、干预方案、长期管理',
    scene: '慢病干预 · 综合管理',
    tpl: '您好，根据您的慢病档案，为您推送本周健康管理建议，请参考执行。',
    execLog: [
      { at: '09:00', action: '推送慢病管理建议', note: '高血压合并结节随访', state: '已读', tone: 'g' },
      { at: '前天 10:00', action: '发送血压监测提醒', note: '请记录今日血压', state: '未回复', tone: 'o' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI慢病管理师，负责协助您管理合并慢性疾病。' },
      { from: 'ai', text: '根据您的档案，您合并有高血压，建议每天早晨测量血压并记录，目标控制在 130/80 mmHg 以下。' },
      { type: 'card', ico: '📊', title: '查看慢病管理方案', sub: '高血压 · 个性化管理计划' },
      { from: 'patient', text: '我最近血压有点高，需要调整用药吗？' },
      { from: 'ai', text: '血压偏高时请先记录数值，如连续 3 天超过 140/90 mmHg，建议联系主治医生评估是否需要调整用药方案。' }
    ]
  },
  {
    key: 'psych', name: 'AI心理咨询师', shortName: '心理咨询', ico: '心', bg: '#fff1f2', color: '#dc2626',
    image: '/images/ai-assistants/demo05.png',
    tagline: '检后焦虑评估 · 情绪疏导 · 心理支持，陪伴患者走过每个难关',
    capabilities: ['焦虑情绪评估', '情绪疏导对话', '睡眠质量询问', '压力干预建议', '必要时转人工'],
    workflow: ['情绪评估', 'AI疏导', '持续关怀', '风险识别', '人工介入'],
    stats: { reach: 43, read: 38, reply: 29, transfer: 8 },
    desc: '检后焦虑评估、情绪疏导、心理支持',
    scene: '心理关怀 · 焦虑干预',
    tpl: '您好，检查结果出来后有任何担忧都可以告诉我，我们一起面对。',
    execLog: [
      { at: '10:00', action: '发送心理关怀问候', note: '检后焦虑评估', state: '未回复', tone: 'o' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI心理咨询师，收到检查报告后心情如何？有任何担忧都可以告诉我。' },
      { from: 'patient', text: '我很担心，一直在想会不会是癌症。' },
      { from: 'ai', text: '您的担心完全可以理解，这是很正常的反应。目前的检查结果需要进一步随访观察，并不代表一定是恶性病变。' },
      { from: 'ai', text: '建议您：① 保持规律作息；② 避免过度查阅网络信息；③ 如果焦虑影响到日常生活，可以申请专业心理咨询。我们会一直陪伴您。' },
      { from: 'patient', text: '谢谢，我会尽量放松的。' }
    ]
  },
  {
    key: 'rehab', name: 'AI运动康复师', shortName: '运动康复', ico: '动', bg: '#ecfdf5', color: '#059669',
    image: '/images/ai-assistants/demo06.png',
    tagline: '个性化运动处方 · 康复计划 · 运动监测，科学运动助力康复',
    capabilities: ['运动处方制定', '运动计划推送', '运动依从性跟踪', '运动禁忌提醒', '康复进度评估'],
    workflow: ['健康评估', '处方制定', '计划推送', '依从跟踪', '效果评估'],
    stats: { reach: 67, read: 58, reply: 32, transfer: 1 },
    desc: '个性化运动处方、康复计划、运动监测',
    scene: '运动干预 · 康复管理',
    tpl: '您好，您的本周运动计划已更新，请按计划执行，循序渐进。',
    execLog: [
      { at: '18:30', action: '推送运动计划', note: '低强度快走 20min', state: '已读', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI运动康复师，根据您的健康状况，为您制定了本周运动计划：' },
      { from: 'ai', text: '建议：每天快走 20-30 分钟，心率控制在 100-120 次/分钟，避免剧烈运动。运动前后做好热身和拉伸。' },
      { type: 'card', ico: '🏃', title: '查看本周运动计划', sub: '低强度有氧 · 个性化方案' },
      { from: 'patient', text: '我最近膝盖有点不舒服，还能运动吗？' },
      { from: 'ai', text: '膝盖不适时建议暂停快走，改为游泳或骑固定自行车等低冲击运动。如症状持续请就医检查。' }
    ]
  },
  {
    key: 'lifestyle', name: 'AI健康生活方式规划师', shortName: '生活规划', ico: '活', bg: '#fefce8', color: '#ca8a04',
    image: '/images/ai-assistants/demo07.png',
    tagline: '饮食 · 作息 · 生活习惯综合建议，全方位优化健康生活方式',
    capabilities: ['饮食方案推荐', '作息规律建议', '生活习惯干预', '营养摄入指导', '健康目标设定'],
    workflow: ['生活评估', '方案制定', '建议推送', '习惯跟踪', '方案调整'],
    stats: { reach: 92, read: 81, reply: 44, transfer: 0 },
    desc: '饮食、作息、生活习惯综合建议',
    scene: '生活方式干预 · 综合规划',
    tpl: '您好，根据您的健康状况，为您推荐本周生活方式建议，请参考执行。',
    execLog: [
      { at: '12:00', action: '推送饮食建议', note: '低盐低脂食谱', state: '已读', tone: 'g' },
      { at: '昨天 18:00', action: '推送作息建议', note: '规律作息提醒', state: '未读', tone: 'o' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI健康生活方式规划师，根据您的体检结果，为您推荐本周生活方式建议：' },
      { from: 'ai', text: '饮食：① 减少高盐食物；② 增加蔬菜水果；③ 主食以粗粮为主。作息：建议每天 22:30 前入睡，保证 7-8 小时睡眠。' },
      { type: 'card', ico: '🥗', title: '查看本周生活方式建议', sub: '饮食 · 作息 · 习惯综合方案' },
      { from: 'patient', text: '我可以吃海鲜吗？' },
      { from: 'ai', text: '可以适量食用，建议每周 1-2 次，选择清蒸或水煮方式，避免油炸。如有痛风史请减少贝类摄入。' }
    ]
  },
  {
    key: 'tcm', name: 'AI中医药膳师', shortName: '中医药膳', ico: '膳', bg: '#fdf4ff', color: '#a21caf',
    image: '/images/ai-assistants/demo08.png',
    tagline: '中医体质辨识 · 药膳食疗方案 · 调理建议，传统智慧守护健康',
    capabilities: ['体质辨识分析', '药膳食谱推荐', '食疗方案制定', '禁忌食物提醒', '调理进度跟踪'],
    workflow: ['体质辨识', '方案制定', '食谱推送', '调理跟踪', '效果评估'],
    stats: { reach: 51, read: 44, reply: 26, transfer: 0 },
    desc: '中医体质辨识、药膳食疗方案、调理建议',
    scene: '中医调理 · 药膳食疗',
    tpl: '您好，根据您的中医体质辨识结果，为您推荐本周药膳食疗方案，请参考执行。',
    execLog: [
      { at: '12:00', action: '推送药膳食谱', note: '晚餐控糖食谱', state: '已读', tone: 'g' },
      { at: '前天 09:00', action: '发送体质调理建议', note: '气虚体质调理方案', state: '已送达', tone: 'g' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI中医药膳师，根据您的体质辨识结果，您属于气虚质，建议以补气健脾为主。' },
      { from: 'ai', text: '推荐本周药膳：① 山药薏米粥（健脾益气）；② 黄芪炖鸡汤（补气固表）；③ 红枣枸杞茶（养血安神）。' },
      { type: 'card', ico: '🍵', title: '查看本周药膳食谱', sub: '气虚质 · 补气健脾方案' },
      { from: 'patient', text: '我可以喝绿茶吗？' },
      { from: 'ai', text: '气虚体质建议少喝绿茶，绿茶性凉，容易伤脾胃。可以改喝红茶或普洱茶，温性更适合您的体质。' }
    ]
  },
  {
    key: 'welfare', name: 'AI健康福利官', shortName: '健康福利', ico: '福', bg: '#f0fdf4', color: '#15803d',
    image: '/images/ai-assistants/demo09.png',
    tagline: '权益匹配 · 服务说明 · 复查提醒，让每位患者享受应有的健康权益',
    capabilities: ['权益匹配推送', '服务说明生成', '复查周期提醒', '触达状态跟踪', '人工补触达'],
    workflow: ['权益匹配', 'AI说明', '推送患者', '状态跟踪', '人工补触达'],
    stats: { reach: 38, read: 33, reply: 19, transfer: 1 },
    desc: '健康权益提醒、增值服务推送、福利兑换',
    scene: '权益提醒 · 福利服务',
    tpl: '您好，您有新的健康权益待使用，请查阅并及时兑换，避免过期。',
    execLog: [
      { at: '09:05', action: '推送健康权益提醒', note: '本月免费复查名额', state: '已读', tone: 'g' },
      { at: '前天 10:00', action: '推送福利兑换提醒', note: '健康礼包待领取', state: '未读', tone: 'o' }
    ],
    chat: [
      { from: 'ai', text: '您好，我是您的AI健康福利官，为您提供健康权益管理服务。' },
      { from: 'ai', text: '您本月有 1 次免费复查名额，有效期至 2026-04-30，请尽快预约使用，避免过期。' },
      { type: 'card', ico: '🎁', title: '查看我的健康权益', sub: '本月剩余权益 · 点击查看' },
      { from: 'patient', text: '怎么预约免费复查？' },
      { from: 'ai', text: '您可以点击上方卡片进入权益中心，选择"免费复查"后按提示预约即可。如需帮助请随时联系我。' }
    ]
  },
]

const currentAssistant = computed(() => aiAssistants.find(a => a.key === activeAssistant.value))

const followPatient = computed(() => queue.value.find(p => p.id === followPatientId.value) || queue.value[0])

const followFilteredQueue = computed(() => {
  // AI随访页：只展示 AI随访中的患者
  return queue.value.filter((p) => statusKey(p) === 'follow').filter(p => {
    const s = followSearch.value.trim().toLowerCase()
    if (s && !p.name.toLowerCase().includes(s) && !p.phoneMasked.includes(s)) return false
    if (followRiskFilter.value && p.risk !== followRiskFilter.value) return false
    if (followStageFilter.value && statusKey(p) !== followStageFilter.value) return false
    return true
  })
})

const currentAssistantChat = computed(() => currentAssistant.value?.chat || [])

const activeAssistantPlan = computed(() => {
  const key = activeAssistant.value
  return (assistantPlanPanels.value || []).find((p) => p.key === key) || null
})

const simulatedAssistantChat = computed(() => {
  const a = currentAssistant.value
  const plan = activeAssistantPlan.value
  const dayNum = planDay.value.replace('day', '')
  const patientName = followPatient.value?.name || '您'
  const assistantName = a?.name || 'AI助手'

  if (!plan) {
    return [
      { from: 'ai', text: `您好，我是${assistantName}，将为您提供随访支持。` },
      { from: 'ai', text: `当前 Day ${dayNum} 暂无可展示内容。` },
    ]
  }

  // 手机端不刷屏长文：只给摘要 + 引导去右侧“制定/预览”面板查看详情
  const sections = Array.isArray(plan.sections) ? plan.sections : []
  const firstSec = sections.find((s) => String(s?.p || '').trim()) || sections[0]
  const firstText = String(firstSec?.p || '').trim().split('\n').map((x) => x.trim()).filter(Boolean)[0] || ''

  return [
    { from: 'ai', text: `您好，${patientName}。我是${assistantName}，已为您生成 Day ${dayNum} 的随访建议摘要。` },
    ...(firstText ? [{ from: 'ai', text: `摘要：${firstText}` }] : []),
    { type: 'card', ico: '🧾', title: `查看并填写随访任务（Day ${dayNum}）`, sub: `${plan.name} · 点击在右侧完成制定` },
    { from: 'ai', text: '提示：内容较长已折叠，请在右侧表单中选择知识库条目并保存。' },
  ]
})

const rpSearch = ref('')
const rpSource = ref('')
const rpNodule = ref('')
const rpRisk = ref('')
const rpActiveId = ref(1)

const rpList = ref([])
const rpLoading = ref(false)

async function loadReports() {
  rpLoading.value = true
  try {
    const res = await fetch('/api/b/reports?per_page=50', { credentials: 'include' })
    const data = await res.json()
    if (data.success) {
      rpList.value = (data.data?.reports || []).map(r => ({
        id: r.id,
        name: r.patient_name || '—',
        gender: r.patient?.gender || '—',
        age: r.patient?.age || '—',
        phone: r.patient?.phone ? r.patient.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '—',
        source: r.patient?.source || '—',
        reportType: '健康报告',
        nodules: noduleTypeLabel(r.nodule_type),
        noduleKey: r.nodule_type || 'breast',
        uploadAt: r.created_at ? r.created_at.slice(0, 16).replace('T', ' ') : '—',
        aiStatus: r.status === 'draft' ? '待审核' : r.status === 'finalized' ? '已完成' : r.status || '—',
        risk: r.risk_level || '—',
        riskTone: r.risk_level === '高风险' ? 'r' : r.risk_level === '中风险' ? 'o' : 'g',
        owner: r.created_by_name || '—',
        summary: r.summary || '',
        reportStatus: r.status === 'finalized' ? '已完成' : '待审核',
        reportHtml: r.report_html || '',
        flow: [
          { label: '建档', done: true, cur: false, time: '' },
          { label: '生成报告', done: true, cur: false, time: r.created_at ? r.created_at.slice(0, 16).replace('T', ' ') : '' },
          { label: '人工审核', done: r.status === 'finalized', cur: r.status !== 'finalized', time: r.status === 'finalized' ? '已完成' : '当前步骤' },
          { label: '推送患者', done: false, cur: false, time: '待处理' },
        ]
      }))
      if (rpList.value.length) rpActiveId.value = rpList.value[0].id
    }
  } catch (e) {
    console.error('加载报告列表失败', e)
  } finally {
    rpLoading.value = false
  }
  // 后端无数据时用 mock
  if (!rpList.value.length) {
    rpList.value = [
      { id:'r1', name:'张*国', gender:'男', age:56, phone:'138****5678', source:'门诊', reportType:'健康报告', nodules:'肺部结节', noduleKey:'lung', uploadAt:'2026-04-20 09:15', aiStatus:'待审核', risk:'高风险', riskTone:'r', owner:'李医生', summary:'患者右肺上叶发现直径约8mm磨玻璃结节，边界清晰，建议3个月后复查CT。', aiReadSummary:'综合影像学表现，该结节具有一定恶性风险，建议密切随访，必要时行穿刺活检。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-20 09:15'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r2', name:'李*婷', gender:'女', age:48, phone:'139****2468', source:'体检中心', reportType:'健康报告', nodules:'甲状腺结节', noduleKey:'thyroid', uploadAt:'2026-04-19 14:30', aiStatus:'待审核', risk:'中风险', riskTone:'o', owner:'王医生', summary:'甲状腺左叶发现低回声结节，大小约6×4mm，TI-RADS 3类，建议6个月后复查超声。', aiReadSummary:'结节形态规则，边界清晰，暂无明显恶性征象，建议定期随访观察。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-19 14:30'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r3', name:'王*梅', gender:'女', age:62, phone:'137****1357', source:'门诊', reportType:'健康报告', nodules:'乳腺结节', noduleKey:'breast', uploadAt:'2026-04-18 10:00', aiStatus:'已完成', risk:'中风险', riskTone:'o', owner:'赵医生', summary:'右乳外上象限发现低回声结节，大小约10×8mm，BI-RADS 3类，建议6个月后复查。', aiReadSummary:'结节边界清晰，内部回声均匀，暂无恶性征象，建议定期随访。', reportStatus:'已审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-18 10:00'},{label:'人工审核',done:true,cur:false,time:'已完成'},{label:'推送患者',done:false,cur:true,time:'待处理'}] },
      { id:'r4', name:'赵*强', gender:'男', age:59, phone:'136****8899', source:'体检中心', reportType:'健康报告', nodules:'肺部结节', noduleKey:'lung', uploadAt:'2026-04-17 16:45', aiStatus:'待审核', risk:'高风险', riskTone:'r', owner:'刘医生', summary:'左肺下叶发现实性结节，直径约12mm，边缘有毛刺，建议尽快行增强CT检查。', aiReadSummary:'结节形态不规则，边缘毛刺征，恶性风险较高，建议尽快就诊胸外科。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-17 16:45'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r5', name:'陈*霞', gender:'女', age:45, phone:'138****3344', source:'门诊', reportType:'健康报告', nodules:'乳腺+肺部结节', noduleKey:'breast_lung', uploadAt:'2026-04-16 11:20', aiStatus:'待审核', risk:'低风险', riskTone:'g', owner:'周医生', summary:'双侧乳腺多发小结节，最大约5mm，BI-RADS 2类；右肺微小结节约3mm，建议年度复查。', aiReadSummary:'乳腺及肺部结节均为良性可能性大，建议常规年度随访。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-16 11:20'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r6', name:'刘*峰', gender:'男', age:71, phone:'139****7788', source:'体检中心', reportType:'健康报告', nodules:'肺部+甲状腺结节', noduleKey:'lung_thyroid', uploadAt:'2026-04-15 09:00', aiStatus:'已完成', risk:'低风险', riskTone:'g', owner:'陈医生', summary:'右肺微小磨玻璃结节约4mm；甲状腺右叶小结节约5mm，TI-RADS 2类，均建议年度复查。', aiReadSummary:'两处结节均为低风险，建议年度随访，无需特殊处理。', reportStatus:'已审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-15 09:00'},{label:'人工审核',done:true,cur:false,time:'已完成'},{label:'推送患者',done:false,cur:true,time:'待处理'}] },
      { id:'r7', name:'孙*英', gender:'女', age:52, phone:'137****6677', source:'门诊', reportType:'健康报告', nodules:'乳腺结节', noduleKey:'breast', uploadAt:'2026-04-14 15:30', aiStatus:'待审核', risk:'低风险', riskTone:'g', owner:'李医生', summary:'左乳内下象限发现囊性结节，大小约8×6mm，BI-RADS 2类，建议6个月后复查超声。', aiReadSummary:'囊性结节，良性可能性极大，建议定期随访，无需手术干预。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-14 15:30'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r8', name:'周*明', gender:'男', age:64, phone:'138****9900', source:'门诊', reportType:'健康报告', nodules:'肺部+甲状腺结节', noduleKey:'lung_thyroid', uploadAt:'2026-04-13 10:45', aiStatus:'待审核', risk:'中风险', riskTone:'o', owner:'赵医生', summary:'右肺中叶磨玻璃结节约7mm，建议3个月后复查；甲状腺左叶结节TI-RADS 3类，建议6个月复查。', aiReadSummary:'肺部结节需密切随访，甲状腺结节暂无恶性征象，建议综合管理。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-13 10:45'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r9', name:'吴*丽', gender:'女', age:39, phone:'150****4455', source:'社区', reportType:'健康报告', nodules:'乳腺+甲状腺结节', noduleKey:'breast_thyroid', uploadAt:'2026-04-12 14:00', aiStatus:'待审核', risk:'高风险', riskTone:'r', owner:'王医生', summary:'右乳发现低回声结节约15×12mm，BI-RADS 4A类，建议穿刺活检；甲状腺结节TI-RADS 4类。', aiReadSummary:'乳腺结节具有一定恶性风险，建议尽快行穿刺活检明确诊断；甲状腺结节亦需进一步评估。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-12 14:00'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r10', name:'郑*涛', gender:'男', age:67, phone:'136****2233', source:'体检中心', reportType:'健康报告', nodules:'三合并结节', noduleKey:'triple', uploadAt:'2026-04-11 09:30', aiStatus:'待审核', risk:'高风险', riskTone:'r', owner:'刘医生', summary:'肺部、甲状腺、乳腺三处均发现结节，其中肺部结节约10mm，建议多学科会诊。', aiReadSummary:'三处结节并存，综合风险较高，建议多学科会诊，制定个体化管理方案。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-11 09:30'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
    ]
    rpActiveId.value = 'r1'
  }
}

const rpFinalizing = ref(false)
const rpViewHtml = ref('')
const rpViewVisible = ref(false)
const rpAuditId = ref('')
const rpAuditPara1 = ref('')
const rpAuditPara2 = ref('')

function openAudit(r) {
  rpAuditId.value = r.id
  rpAuditPara1.value = r.summary || '暂无影像解读摘要'
  rpAuditPara2.value = r.aiReadSummary || '暂无AI健康建议'
  rpActiveId.value = r.id
}

async function finalizeReport(reportId) {
  if (!reportId) return
  rpFinalizing.value = true
  try {
    const res = await fetch(`/api/b/reports/${reportId}/finalize`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ summary: rpAuditPara1.value, ai_read_summary: rpAuditPara2.value })
    })
    const data = await res.json()
    if (data.success) {
      const r = rpList.value.find(x => x.id === reportId)
      if (r) r.reportStatus = '已审核'
      rpAuditId.value = ''
      await loadReports()
    } else {
      // mock fallback: mark as approved locally
      const r = rpList.value.find(x => x.id === reportId)
      if (r) r.reportStatus = '已审核'
      rpAuditId.value = ''
    }
  } catch (e) {
    const r = rpList.value.find(x => x.id === reportId)
    if (r) r.reportStatus = '已审核'
    rpAuditId.value = ''
  } finally {
    rpFinalizing.value = false
  }
}

async function approveReport(reportId) {
  if (!reportId) return
  rpFinalizing.value = true
  try {
    // 审核AI建议：调用 approve-all 接口，只批准建议，不触发LLM重新生成
    const res = await fetch(`/api/b/reports/${reportId}/recommendations/approve-all`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await res.json()
    if (data.success) {
      // 本地更新状态
      const r = rpList.value.find(x => x.id === reportId)
      if (r) r.reportStatus = '已审核'
    } else {
      alert(data.message || '审核失败')
    }
  } catch (e) {
    console.error('审核失败', e)
  } finally {
    rpFinalizing.value = false
  }
}

async function viewReport(reportId) {
  try {
    const res = await fetch(`/api/b/reports/${reportId}`, { credentials: 'include' })
    const data = await res.json()
    if (data.success) {
      rpViewHtml.value = data.data?.report_html || data.data?.summary || '暂无报告内容'
      rpViewVisible.value = true
    }
  } catch (e) {
    console.error('获取报告失败', e)
  }
}

const rpFilteredList = computed(() => {
  return rpList.value.filter(r => {
    if (rpSearch.value && !r.name.includes(rpSearch.value) && !r.phone.includes(rpSearch.value)) return false
    if (rpSource.value && r.source !== rpSource.value) return false
    if (rpRisk.value && r.risk !== rpRisk.value) return false
    return true
  })
})

const rpActive = computed(() => rpList.value.find(r => r.id === rpActiveId.value) || rpList.value[0])

/**
 * @isdoc
 * @description 来源展示：仅保留「门诊 / 体检中心」
 * @param {string} src
 * @returns {string}
 */
function sourceLabel(src) {
  const s = String(src || '').trim()
  if (s.includes('门诊')) return '门诊'
  return '体检中心'
}

function assistantStatus(key) {
  const enabledKeys = new Set(['hlp', 'health', 'psych', 'rehab', 'tcm'])
  return enabledKeys.has(key) ? 'g' : 'o'
}

function assistantStatusLabel(key) {
  return assistantStatus(key) === 'g' ? '已启用' : '待启用'
}

/**
 * @isdoc
 * @description 负责人展示：统一为“×医生”
 * @param {string} owner
 * @returns {string}
 */
function ownerLabel(owner) {
  const s = String(owner || '').trim()
  if (!s) return '—'
  return s.includes('医生') ? s : `${s.replace(/(师|员|岗|管理师)$/,'')}医生`
}

/**
 * @isdoc
 * @description 右侧“下一步说明”
 * @param {any} p
 * @returns {string}
 */
function nextHint(p) {
  const k = statusKey(p)
  if (k === 'new') return '请先完成患者建档信息，后续才能上传检查报告并生成健康报告。'
  if (k === 'gen') return '请上传/补全检查报告，系统将自动解析并生成健康报告草稿。'
  if (k === 'review') return '健康报告已生成，等待人工审核后进入随访计划制定。'
  if (k === 'plan') return '请制定随访计划，明确复查周期与触达方式，随后进入 AI 随访执行。'
  return '当前处于 AI 随访中，可查看随访记录与最近触达情况。'
}

/**
 * @isdoc
 * @description 阶段说明（按你给的文案）
 * @param {any} p
 * @returns {string}
 */
function nextHintV2(p) {
  const k = statusKey(p)
  if (k === 'gen') return '系统将根据档案资料生成健康报告草稿。'
  if (k === 'review') return `健康报告已生成，建议优先完成审核。`
  if (k === 'plan') return '健康报告已审核，等待制定随访计划。'
  if (k === 'follow') return '患者正在 AI随访中，可查看随访记录。'
  return '请先完成患者档案建立，后续才能生成健康报告。'
}

/**
 * @isdoc
 * @description 流程节点（5节点）与状态
 * @param {any} p
 * @returns {{k:string,label:string,state:'done'|'current'|'todo'}[]}
 */
function flowNodes(p) {
  const k = statusKey(p)
  const labels = [
    { k: 'a', label: '建立档案' },
    { k: 'b', label: '健康报告生成' },
    { k: 'c', label: '健康报告审核' },
    { k: 'd', label: '随访计划制定' },
    { k: 'e', label: 'AI随访' },
  ]

  // 当前节点：按“当前状态”定位到主流程节点
  // 健康报告待生成 → 当前=健康报告生成
  // 健康报告待审核 → 当前=健康报告审核
  // 随访计划待制定 → 当前=随访计划制定
  // AI随访中 → 当前=AI随访
  const curIdx = k === 'follow' ? 4 : k === 'plan' ? 3 : k === 'review' ? 2 : 1

  return labels.map((x, i) => {
    const state = i < curIdx ? 'done' : i === curIdx ? 'current' : 'todo'
    return { ...x, state }
  })
}

/**
 * @isdoc
 * @description 阶段操作按钮（最多2个）
 * @param {any} p
 * @returns {{label:string,primary:boolean,onClick:()=>void}[]}
 */
function stageActions(p) {
  const k = statusKey(p)
  if (k === 'gen') {
    return [
      { label: '生成报告', primary: true, onClick: () => toast?.show('生成健康报告（示意）') },
      { label: '编辑档案', primary: false, onClick: () => goRecord() },
    ]
  }
  if (k === 'review') {
    return [
      { label: '审核报告', primary: true, onClick: () => setSubTab('review') },
      { label: '退回修改', primary: false, onClick: () => toast?.show('退回修改（示意）') },
    ]
  }
  if (k === 'plan') {
    return [{ label: '制定随访计划', primary: true, onClick: () => setSubTab('followup-plan') }]
  }
  if (k === 'follow') {
    return [
      { label: '查看随访记录', primary: true, onClick: () => setSubTab('follow') },
      { label: '人工接管', primary: false, onClick: () => toast?.show('人工接管（示意）') },
    ]
  }
  return [{ label: '建立档案', primary: true, onClick: () => goRecord() }]
}

/**
 * @isdoc
 * @description 右侧主操作按钮文案
 * @param {any} p
 * @returns {string}
 */
function primaryLabel(p) {
  const k = statusKey(p)
  if (k === 'new') return '新建档案'
  if (k === 'gen') return '上传报告'
  if (k === 'review') return '审核报告'
  if (k === 'plan') return '制定随访计划'
  return '查看随访详情'
}

/**
 * @isdoc
 * @description 右侧主操作按钮行为（原型：路由/切换tab/提示）
 * @param {any} p
 */
function doPrimary(p) {
  const k = statusKey(p)
  if (k === 'new') return goRecord()
  if (k === 'gen') return setSubTab('record')
  if (k === 'review') return setSubTab('review')
  if (k === 'plan') return setSubTab('followup-plan')
  return setSubTab('follow')
}

/**
 * @isdoc
 * @description 右侧最近动态：严格按当前阶段展示（2-3条），避免越级出现 AI 随访/异常等内容
 * @param {any} p
 * @returns {{at:string,text:string,meta?:string,tone:string}[]}
 */
function stageTimeline(p) {
  const k = statusKey(p)
  const baseAt = String(p?.timeline?.[p.timeline.length - 1]?.at || '刚刚')
  if (k === 'gen' || k === 'new') {
    return [
      { at: baseAt, tone: 'b', text: '档案资料已提交' },
      { at: '—', tone: 'b', text: '检查报告已归档' },
      { at: '—', tone: 'o', text: '等待生成健康报告' },
    ]
  }
  if (k === 'review') {
    return [
      { at: baseAt, tone: 'p', text: '健康报告已生成' },
      { at: '—', tone: 'o', text: '进入待审核队列' },
      { at: '—', tone: 'o', text: '等待人工审核' },
    ]
  }
  if (k === 'plan') {
    return [
      { at: baseAt, tone: 'g', text: '健康报告已审核通过' },
      { at: '—', tone: 'b', text: '患者报告已推送' },
      { at: '—', tone: 'o', text: '等待制定随访计划' },
    ]
  }
  // follow
  return [
    { at: baseAt, tone: 'b', text: 'AI已发送随访消息' },
    { at: '—', tone: 'g', text: '患者已回复' },
    { at: '—', tone: 'p', text: 'AI助手推送建议', meta: '待人工确认' },
  ]
}


/**
 * @isdoc
 * @description 获取患者最近一次互动/更新的时间文本（mock：取 chat 最后一次，其次 timeline 最后一次）
 * @param {any} p 患者对象
 * @returns {string}
 */
function lastTouchLabel(p) {
  const at = String(p?.chat?.[p.chat.length - 1]?.at || p?.timeline?.[p.timeline.length - 1]?.at || '').trim()
  return at ? `最近：${at}` : '最近：—'
}

/**
 * @isdoc
 * @description 判断最近一条消息的发送方（用于计算待回复/待患者回复）
 * @param {any} p 患者对象
 * @returns {'patient' | 'ai' | 'none'}
 */
function lastChatRole(p) {
  const last = p?.chat?.[p.chat.length - 1]
  const from = String(last?.from || '').trim()
  if (!from) return 'none'
  if (from === '患者' || /患者/.test(from)) return 'patient'
  if (from === '系统' || /AI/.test(from) || /系统/.test(from)) return 'ai'
  return 'ai'
}

const steps = computed(() => ([
  { label: '建档', ic: '档', sub: '04-10', cls: 'done' },
  { label: '上传上报', ic: '云', sub: '待上传', cls: 'active' },
  { label: 'AI健康报告', ic: 'AI', sub: '待生成', cls: '' },
  { label: '人工审核', ic: '审', sub: '待审核', cls: '' },
  { label: '推送患者', ic: '推', sub: '待推送', cls: '' },
  { label: '匹配AI助手', ic: '机', sub: '进行中', cls: '' },
  { label: '异常识别', ic: '警', sub: '监测', cls: '' },
  { label: '复查提醒', ic: '铃', sub: '已排程', cls: '' },
  { label: '复查回收', ic: '收', sub: '待回收', cls: '' },
  { label: '档案更新', ic: '更', sub: '—', cls: '' }
]))

// subTabs/allowedSubTabs/setSubTab 已提前定义（由路由 query.tab 驱动）

/**
 * @isdoc
 * @description 将旧阶段映射为5个“对外状态”
 * @param {any} p 患者对象
 * @returns {'new'|'gen'|'review'|'plan'|'follow'}
 */
function statusKey(p) {
  const stage = String(p?.stage || '')
  // 健康报告待生成：包含“待生成/上传/推送/建档/复查回收”等都归到生成链路前
  if (['record', 'upload', 'aiGen', 'push', 'recall'].includes(stage)) return 'gen'
  // 健康报告待审核
  if (stage === 'review') return 'review'
  // AI随访中
  if (stage === 'follow') return 'follow'
  // 其它（包括 abnormal）统一归为“随访计划待制定”
  return 'plan'
}

/**
 * @isdoc
 * @description 获取4状态的展示文案
 * @param {any} p 患者对象
 * @returns {string}
 */
function statusLabel(p) {
  const k = statusKey(p)
  if (k === 'gen') return '健康报告待生成'
  if (k === 'review') return '健康报告待审核'
  if (k === 'plan') return '随访计划待制定'
  return 'AI随访中'
}

const stageTabs = computed(() => {
  const count = (k) => queue.value.filter((p) => statusKey(p) === k).length
  return [
    { key: 'all', label: '全部', count: queue.value.length },
    { key: 'gen', label: '健康报告待生成', count: count('gen') },
    { key: 'review', label: '健康报告待审核', count: count('review') },
    { key: 'plan', label: '随访计划待制定', count: count('plan') },
    { key: 'follow', label: 'AI随访中', count: count('follow') },
  ]
})

const nextActions = [
  '上传复查报告',
  '推送健康管理报告',
  '开启AI随访',
  '发送饮食建议',
  '发送运动计划',
  '创建电话随访',
  '标记异常',
  '创建复查提醒'
]

queue.value = []

// 10条本地 mock 数据（后端无数据时展示）
const MOCK_QUEUE = [
  { id:'m1', name:'张*国', gender:'男', age:56, phoneMasked:'138****5678', source:'门诊', owner:'李医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'review', lastReport:'CT报告' },
  { id:'m2', name:'李*婷', gender:'女', age:48, phoneMasked:'139****2468', source:'体检中心', owner:'王医生', nodules:'甲状腺结节', noduleType:'thyroid', risk:'中风险', riskTone:'o', stage:'review', lastReport:'超声报告' },
  { id:'m3', name:'王*梅', gender:'女', age:62, phoneMasked:'137****1357', source:'门诊', owner:'赵医生', nodules:'乳腺结节', noduleType:'breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day1', channel:'小程序', cycle:'每月' } },
  { id:'m4', name:'赵*强', gender:'男', age:59, phoneMasked:'136****8899', source:'体检中心', owner:'刘医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'plan', lastReport:'CT报告', planTask:{ day:'day1', channel:'电话', cycle:'每两周' } },
  { id:'m5', name:'陈*霞', gender:'女', age:45, phoneMasked:'138****3344', source:'门诊', owner:'周医生', nodules:'乳腺+肺部结节', noduleType:'breast_lung', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day2', channel:'小程序', cycle:'每月' } },
  { id:'m6', name:'刘*峰', gender:'男', age:71, phoneMasked:'139****7788', source:'体检中心', owner:'陈医生', nodules:'肺部+甲状腺结节', noduleType:'lung_thyroid', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'医生复核中', planTask:{ day:'day1', channel:'短信', cycle:'每季度' } },
  { id:'m7', name:'孙*英', gender:'女', age:52, phoneMasked:'137****6677', source:'门诊', owner:'李医生', nodules:'乳腺结节', noduleType:'breast', risk:'低风险', riskTone:'g', stage:'gen', lastReport:'超声报告' },
  { id:'m8', name:'周*明', gender:'男', age:64, phoneMasked:'138****9900', source:'门诊', owner:'赵医生', nodules:'肺部+甲状腺结节', noduleType:'lung_thyroid', risk:'中风险', riskTone:'o', stage:'plan', lastReport:'CT报告', planTask:{ day:'day2', channel:'电话', cycle:'每月' } },
  { id:'m9', name:'吴*丽', gender:'女', age:39, phoneMasked:'150****4455', source:'社区', owner:'王医生', nodules:'乳腺+甲状腺结节', noduleType:'breast_thyroid', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'超声报告', planTask:{ day:'day1', channel:'小程序', cycle:'每两周' } },
  { id:'m10', name:'郑*涛', gender:'男', age:67, phoneMasked:'136****2233', source:'体检中心', owner:'刘医生', nodules:'三合并结节', noduleType:'triple', risk:'高风险', riskTone:'r', stage:'plan', lastReport:'CT报告', planTask:{ day:'day3', channel:'电话', cycle:'每月' } },
]

// 筛选条件
const qSearch = ref('')
const qSource = ref('')
const qNodule = ref('')
const qRisk = ref('')
const qStatus = ref('')


async function loadPatients() {
  try {
    const res = await fetch('/api/b/patients?per_page=50', { credentials: 'include' })
    const data = await res.json()
    if (data.success) {
      const items = data.data?.items || data.data || []
      queue.value = items.map(p => ({
        id: p.id,
        _apiId: p.id,
        name: p.name || '—',
        gender: p.gender || '—',
        age: p.age || '—',
        phoneMasked: p.phone ? p.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '—',
        source: p.source_channel === 'manual' ? '门诊' : (p.source_channel || '门诊'),
        owner: p.manager_name || '—',
        nodules: noduleTypeLabel(p.nodule_type),
        noduleType: p.nodule_type || 'breast',
        risk: p.risk_level || (p.reports?.[0]?.risk_level) || '—',
        riskTone: (p.risk_level || p.reports?.[0]?.risk_level) === '高风险' ? 'r' : (p.risk_level || p.reports?.[0]?.risk_level) === '中风险' ? 'o' : 'g',
        stage: p.reports?.length ? 'review' : 'gen',
        stageLabel: p.reports?.length ? '健康报告待审核' : '健康报告待生成',
        nextStep: '',
        serviceStatus: '',
        report: { status: '—', summary: '' },
        rawReports: [],
        aiReadSummary: '',
        reportDoc: { title: '', sections: [] },
        auditTrail: [],
        chat: [],
        followTodos: [],
        abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
        reviewers: '',
        assistants: [],
        timeline: [],
        planTask: null,
      }))
    }
  } catch (e) {
    console.error('加载患者列表失败', e)
  }
  // 后端无数据时用 mock
  if (!queue.value.length) queue.value = MOCK_QUEUE.map(p => ({
    ...p,
    stageLabel: '', nextStep: '', serviceStatus: '',
    report: { status: '—', summary: '' }, rawReports: [],
    aiReadSummary: '', reportDoc: { title: '', sections: [] },
    auditTrail: [], chat: [], followTodos: [],
    abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
    reviewers: '', assistants: [], timeline: [], planTask: null,
  }))
}

function noduleTypeLabel(t) {
  const map = {
    breast: '乳腺结节', lung: '肺部结节', thyroid: '甲状腺结节',
    breast_lung: '乳腺+肺部结节', breast_thyroid: '乳腺+甲状腺结节',
    lung_thyroid: '肺部+甲状腺结节', triple: '三合并结节'
  }
  return map[t] || t || '—'
}

function noduleTags(p) {
  const type = p.noduleType || ''
  const parts = type.split('_')
  if (parts.length === 1 && type) return [{ label: noduleTypeLabel(type), type }]
  const map = { breast: '乳腺结节', lung: '肺部结节', thyroid: '甲状腺结节', triple: '三合并' }
  if (type === 'triple') return [{ label: '三合并结节', type: 'triple' }]
  return parts.map(k => ({ label: map[k] || k, type: k }))
}

const queueFiltered = computed(() => {
  let list = queue.value
  if (qSearch.value) list = list.filter(p => p.name.includes(qSearch.value) || (p.phoneMasked || '').includes(qSearch.value))
  if (qSource.value) list = list.filter(p => sourceLabel(p.source) === qSource.value || p.source === qSource.value)
  if (qNodule.value) list = list.filter(p => p.nodules === qNodule.value)
  if (qRisk.value) list = list.filter(p => p.risk === qRisk.value)
  if (qStatus.value) list = list.filter(p => statusKey(p) === qStatus.value)
  return list
})

const filteredQueue = computed(() => {
  if (activeStage.value === 'all') return queue.value
  return queue.value.filter((p) => statusKey(p) === activeStage.value)
})

// 随访计划页：只展示“随访计划待制定”的患者
const planPatients = computed(() => queue.value.filter((p) => statusKey(p) === 'plan'))

const activePatient = computed(() => {
  return queue.value.find((p) => p.id === activePatientId.value) || queue.value[0] || {}
})

watch(
  () => activePatientId.value,
  () => {
    // 若患者已保存过计划 day，则切换到该 day
    const d = activePatient.value?.plan?.day
    if (typeof d === 'string' && d.startsWith('day')) planDay.value = d
  },
  { immediate: true }
)

/**
 * @isdoc
 * @description 根据当前子页(tab)强制绑定患者池(stage)
 * @param {string} tab
 * @returns {'all'|'gen'|'review'|'plan'|'follow'}
 */
function stageForTab(tab) {
  if (tab === 'followup-plan') return 'plan'
  if (tab === 'follow') return 'follow'
  if (tab === 'review') return 'review'
  if (tab === 'record') return 'gen'
  return 'all'
}

watch(
  () => subTab.value,
  (tab) => {
    // 强制让每个子页只看自己的患者池
    const stage = stageForTab(tab)
    activeStage.value = stage

    const list = stage === 'plan'
      ? planPatients.value
      : stage === 'follow'
        ? queue.value.filter((p) => statusKey(p) === 'follow')
        : stage === 'review'
          ? queue.value.filter((p) => statusKey(p) === 'review')
          : stage === 'gen'
            ? queue.value.filter((p) => statusKey(p) === 'gen')
            : queue.value

    if (list.length && !list.some((p) => p.id === activePatientId.value)) {
      activePatientId.value = list[0].id
    }
    if (tab === 'follow' && list.length && !list.some((p) => p.id === followPatientId.value)) {
      followPatientId.value = list[0].id
    }
  },
  { immediate: true }
)

const midTitle = computed(() => {
  const map = {
    queue: '闭环处置工作台',
    record: '患者建档',
    review: '健康报告审核',
    follow: 'AI助手随访',
    abnormal: '异常与复查'
  }
  return map[subTab.value] || '患者管理'
})

const midSub = computed(() => {
  const map = {
    queue: '选中患者后联动闭环时间线与操作区',
    record: '原始报告 / 历史报告 / AI解读摘要',
    review: 'AI健康管理报告审核通过后才能推送患者',
    follow: '随访推送与聊天融合展示',
    abnormal: '异常识别、人工介入、复查回收与档案更新'
  }
  return map[subTab.value] || ''
})

const rightTitle = computed(() => {
  const map = {
    queue: '下一步动作',
    record: '处置与动作',
    review: '审核与推送',
    follow: 'AI健康服务团队',
    abnormal: '处置与动作'
  }
  return map[subTab.value] || '操作区'
})

const rightSub = computed(() => {
  const map = {
    queue: '快速跳转各功能区',
    record: '围绕档案与原始报告',
    review: '面向患者推送前最后一道关',
    follow: '9类助手矩阵',
    abnormal: '异常/复查闭环动作'
  }
  return map[subTab.value] || ''
})

/**
 * @description 设置当前阶段筛选，并保证选中患者存在
 * @param {string} key 阶段key
 */
function setStage(key) {
  activeStage.value = key
  showAllTimeline.value = false
  const list = filteredQueue.value
  if (list.length && !list.some((p) => p.id === activePatientId.value)) {
    activePatientId.value = list[0].id
  }
  if (subTab.value !== 'queue') setSubTab('queue')
}

// countBy 已废弃：状态统计改为 statusKey 映射

/**
 * @description 跳转到「患者建档」页面
 */
function goRecord() {
  router.push({ path: '/patient', query: { ...route.query, tab: 'record' } })
}

/**
 * @isdoc
 * @description 返回患者队列（用于患者建档页头返回按钮）
 */
function backToQueue() {
  setSubTab('queue')
}
</script>

<style scoped>
.pm{height:100%;display:flex;flex-direction:column;overflow:hidden;margin:-16px -20px}
.pm-shell{flex:1;min-height:0;background:#fff;display:flex;flex-direction:column;overflow:hidden}
.pm-record{flex:1;min-height:0;overflow:auto;background:#f3f6fb;padding:12px}

/* 随访计划页 */
.plan-page{flex:1;min-height:0;overflow:auto;background:#f3f6fb;padding:12px}
.plan-filter{margin-bottom:12px}
.plan-filter-row{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end}
.plan-filter-actions{margin-left:auto;display:flex;gap:10px;align-items:center}

.plan-workbench{display:grid;grid-template-columns:520px minmax(0,1fr);gap:12px;align-items:start}
.plan-task-list{min-height:620px;display:flex;flex-direction:column}
.seg-tabs{display:flex;align-items:center;border:1px solid #e6edf7;border-radius:999px;overflow:hidden;background:#fff}
.seg-tab{height:28px;padding:0 12px;border:none;background:transparent;font-weight:950;color:#334155;cursor:pointer}
.seg-tab[data-on="true"]{background:#eef5ff;color:#155eef}
.seg-tab + .seg-tab{border-left:1px solid #e6edf7}

.pat-table{padding:10px 12px;display:grid;gap:10px;min-height:0;overflow:auto}
.pat-head{display:grid;grid-template-columns:1.1fr 1.6fr .7fr .8fr .7fr;gap:10px;padding:8px 10px;border:1px solid #eef2f7;background:#f8fafc;border-radius:12px;font-weight:950;color:#0f172a;font-size:12px}
.pat-rows{display:grid;gap:10px}
.pat-row{display:grid;grid-template-columns:1.1fr 1.6fr .7fr .8fr .7fr;gap:10px;align-items:center;border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 10px}
.pat-row[data-active="true"]{border-color:#155eef;background:#eef5ff}
.pat-main{border:none;background:transparent;text-align:left;cursor:pointer;min-width:0}
.pat-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pat-cell{font-size:12px;color:#334155;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.task-rows{padding:10px 12px;display:grid;gap:10px;overflow:auto;min-height:0}
.task-row{position:relative;border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 10px;text-align:left;cursor:pointer}
.task-row.active{border-color:#155eef;background:#eef5ff}
.tr-top{display:flex;align-items:center;justify-content:space-between;gap:8px}
.tr-sub{margin-top:4px;font-size:12px;line-height:1.5;color:#334155}
.tr-meta{margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tr-ck{position:absolute;right:10px;bottom:10px}
.plan-task-detail{min-height:620px;display:flex;flex-direction:column}
.plan-task-detail .pad{overflow:auto;flex:1;min-height:0}
.detail-grid{display:grid;grid-template-columns:1fr;gap:12px}
.detail-card{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:12px}
.detail-title{font-weight:950;color:#0f172a;margin-bottom:6px}
.detail-sub{font-size:12px;margin-bottom:10px}
.detail-top{display:flex;gap:12px;align-items:flex-start;justify-content:space-between}
.detail-top-title{font-size:13px;color:#0f172a;font-weight:950;display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.detail-top-sub{font-size:12px;margin-top:4px}
.detail-top-actions{display:flex;gap:8px;align-items:center}
.exec-list{display:grid;gap:10px}
.exec-row{display:grid;grid-template-columns:86px minmax(0,1fr);gap:10px;align-items:start}
.exec-at{color:#64748b;font-weight:950;font-size:12px;white-space:nowrap;line-height:1.6}
.exec-line{color:#0f172a;font-weight:800;font-size:12px}
.pf-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px 12px}
.pf{display:flex;flex-direction:column;gap:6px}
.pf .k{color:#64748b;font-weight:850;font-size:12px}
.pf-in{height:34px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;outline:none;background:#fff}
.pf-in:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}

.plan-card{min-height:520px}
.plan-quick{display:grid;gap:8px;margin-bottom:12px}
.plan-quick-item{background:#f8fafc;border:1px solid #eef2f7;border-radius:12px;padding:10px 12px;color:#334155;line-height:1.7}
.plan-flow{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:12px;margin-bottom:12px}
.plan-flow-title{font-weight:950;color:#0f172a;margin-bottom:10px}
.plan-flow-bar{margin-top:6px}
.plan-flow-actions{display:flex;gap:10px;justify-content:flex-end;margin-top:10px;flex-wrap:wrap}
.plan-form{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:12px;margin-bottom:12px}
.kb-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.kb-head-actions{display:flex;gap:10px;align-items:center}
.kb-groups{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:10px}
.kb-group{border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 12px;text-align:left;cursor:pointer}
.kb-group:hover{border-color:#cfe0ff;background:#fbfdff}
.kb-group-title{font-weight:950;color:#0f172a}
.kb-group-sub{font-size:12px;margin-top:2px}
.kb-group-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.kb-tag{border:1px solid #e6edf7;background:#f8fafc;border-radius:999px;padding:2px 8px;font-size:12px;color:#334155;font-weight:850}
.kb-picked{margin-top:10px}

.kb-toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:6px 0 10px}
.kb-list{border:1px solid #eef2f7;border-radius:12px;background:#fbfdff;overflow:hidden}
.kb-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 12px;border-top:1px solid #eef2f7}
.kb-row:first-child{border-top:none}
.kb-ck{display:flex;align-items:center;gap:10px;min-width:0;cursor:pointer}
.kb-ck input{width:16px;height:16px}
.kb-name{font-weight:950;color:#0f172a;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kb-actions{display:flex;gap:8px;align-items:center}
.kb-act{border:1px solid #e6edf7;background:#fff;border-radius:10px;height:28px;padding:0 10px;font-weight:900;color:#334155;cursor:pointer}
.kb-act:hover{border-color:#cfe0ff;background:#eef5ff;color:#155eef}
.kb-preview{display:grid;gap:8px;margin-top:8px}
.kb-panel{border:1px solid #eef2f7;border-radius:12px;background:#fff;overflow:hidden}
.kb-panel > summary{list-style:none;cursor:pointer;padding:10px 12px;font-weight:950;color:#0f172a;display:flex;align-items:center;justify-content:space-between}
.kb-panel > summary::-webkit-details-marker{display:none}
.kb-panel[open] > summary{background:#fbfdff;border-bottom:1px solid #eef2f7}
.kb-body{padding:10px 12px;color:#475569;font-size:12px;line-height:1.75;white-space:pre-wrap}
.kb-body:empty{color:#94a3b8}
.kb-drawer{position:fixed;inset:0;background:rgba(15,23,42,.35);display:flex;align-items:stretch;justify-content:flex-end;z-index:60}
.kb-drawer-card{width:min(980px,92vw);height:100%;background:#fff;border-left:1px solid #e6edf7;box-shadow:-18px 0 60px rgba(15,23,42,.18);display:flex;flex-direction:column}
.kb-drawer-head{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-bottom:1px solid #eef2f7}
.kb-drawer-title{font-weight:950;color:#0f172a}
.kb-drawer-body{display:grid;grid-template-columns:380px minmax(0,1fr);gap:0;flex:1;min-height:0}
.kb-drawer-left{border-right:1px solid #eef2f7;display:flex;flex-direction:column;min-height:0}
.kb-drawer-search{padding:12px 12px;border-bottom:1px solid #eef2f7;background:#fbfdff}
.kb-drawer-list{flex:1;min-height:0;overflow:auto;padding:10px 10px;display:grid;gap:8px}
.kb-li{display:grid;grid-template-columns:26px minmax(0,1fr);gap:10px;align-items:center;border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 10px;text-align:left;cursor:pointer}
.kb-li[data-on="true"]{border-color:#155eef;background:#eef5ff}
.kb-li-ck input{width:16px;height:16px}
.kb-li-title{font-weight:950;color:#0f172a;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kb-li-sub{font-size:12px;margin-top:2px}
.kb-drawer-right{padding:12px 14px;min-height:0;overflow:auto}
.kb-prev-head{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:10px}
.kb-prev-title{font-weight:950;color:#0f172a}
.kb-prev-actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.kb-prev-body{white-space:pre-wrap;line-height:1.75;color:#334155;font-size:12px}
.kb-drawer-actions{padding:12px 14px;border-top:1px solid #eef2f7;background:#fbfdff;display:flex;justify-content:flex-end}
.kb-modal{position:fixed;inset:0;background:rgba(15,23,42,.45);display:flex;align-items:center;justify-content:center;z-index:50;padding:16px}
.kb-modal-card{width:min(720px,96vw);background:#fff;border-radius:14px;box-shadow:0 18px 60px rgba(15,23,42,.20);border:1px solid rgba(255,255,255,.6);overflow:hidden}
.kb-modal-head{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-bottom:1px solid #eef2f7}
.kb-modal-title{font-weight:950;color:#0f172a}
.kb-x{width:30px;height:30px;border-radius:10px;border:1px solid #e6edf7;background:#fff;cursor:pointer;font-size:18px;line-height:1;color:#334155}
.kb-modal-body{padding:12px 14px}
.kb-modal-actions{display:flex;justify-content:flex-end;gap:10px;padding:12px 14px;border-top:1px solid #eef2f7;background:#fbfdff}
.kb-file{position:absolute;left:-9999px;opacity:0;width:1px;height:1px}
.plan-items{border-top:1px dashed #e6edf7;padding-top:12px;display:grid;gap:10px;max-height:520px;overflow:auto}
.plan-item{border:1px solid #eef2f7;border-radius:12px;background:#fff;overflow:hidden}
.plan-sum-row{list-style:none;display:grid;grid-template-columns:86px minmax(0,1fr);gap:10px;align-items:start;padding:10px 12px;cursor:pointer}
.plan-sum-row::-webkit-details-marker{display:none}
.plan-time{color:#64748b;font-weight:950;font-size:12px;white-space:nowrap;line-height:1.6}
.plan-sum{color:#0f172a;font-weight:750;line-height:1.7;font-size:13px;white-space:pre-wrap}
.plan-detail{border-top:1px solid #eef2f7;padding:10px 12px;background:#fbfdff}
.plan-remind{color:#64748b;line-height:1.7;font-size:12px;white-space:pre-wrap}

.pm-body{flex:1;min-height:0;display:grid;grid-template-columns:320px minmax(0,1fr) 360px;gap:12px;padding:12px;background:#fff}
.panel{min-height:0}
.panel.left,.panel.mid,.panel.right{display:flex;flex-direction:column;gap:10px}
.panel-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 12px;border:1px solid #e6edf7;border-radius:12px;background:#fff}
.panel-title{font-weight:950;color:#0f172a}
.mid-tab{display:flex;flex-direction:column;align-items:flex-end;gap:4px;text-align:right}
.mid-chip{display:inline-flex;align-items:center;height:26px;border-radius:999px;border:1px solid #cfe0ff;background:#eef5ff;color:#155eef;font-weight:950;padding:0 10px}
.panel-tools{display:flex;gap:8px;align-items:center}
.search{height:32px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;outline:none;min-width:140px}
.stage-select{height:32px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;outline:none;font-weight:850}

.list{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:auto;flex:1;padding:10px;display:grid;gap:10px}
.row{border:1px solid #eef2f7;border-radius:12px;background:#fff;padding:10px;text-align:left;cursor:pointer}
.row.active{border-color:#155eef;background:#eef5ff}
.row-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.row-sub{margin-top:4px}
.row-meta{margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tag2{border:1px solid #cfe0ff;background:#eef5ff;color:#155eef;border-radius:999px;padding:3px 8px;font-weight:900;font-size:12px}

.pager{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:10px 12px}
.pages{display:flex;gap:8px;align-items:center}
.page-btn{border:1px solid #d9e2ef;background:#fff;border-radius:10px;padding:5px 9px;color:#475569;font-weight:950;cursor:pointer;font-size:13px}
.page-btn.active{background:#155eef;color:#fff;border-color:#155eef}

.card{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:hidden}
/* 用 min-height + padding，避免固定高度导致裁字 */
.card-head{min-height:40px;height:auto;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:8px 12px;gap:10px;flex-wrap:wrap}
.card-title{font-weight:950;color:#0f172a;font-size:13px;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.info{padding:8px 10px}
.info-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px 10px}
.kv .k{color:#94a3b8;font-size:12px;font-weight:850}
.kv .v{margin-top:3px;font-weight:900;color:#0f172a;font-size:13px;line-height:1.45}

/* 右侧整体正文行高，避免压线裁切 */
.overview-right,
.detail-right{line-height:1.5}

.flow .steps{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));gap:8px;padding:10px 12px}
.step{border:1px solid #eef2f7;border-radius:12px;background:#fbfdff;padding:10px;text-align:center}
.step .ic{width:28px;height:28px;border-radius:10px;background:#eef5ff;color:#155eef;display:grid;place-items:center;margin:0 auto 6px;font-weight:950}
.step .t{font-weight:950;color:#0f172a;font-size:12px}
.step.done{border-color:#bbf7d0;background:#f1fff6}
.step.done .ic{background:#ecfff3;color:#16a34a}
.step.active{border-color:#cfe0ff;background:#eef5ff}

.comm{flex:1;display:flex;flex-direction:column;min-height:0}
.tabs{display:flex;gap:6px;align-items:center}
.tab{border:1px solid #e6edf7;background:#fff;border-radius:999px;padding:5px 9px;font-weight:900;color:#526175;cursor:pointer}
.tab.active{border-color:#155eef;background:#eef5ff;color:#155eef}
.comm-body{padding:10px 12px;overflow:auto;flex:1;display:grid;gap:10px}
.evt2{display:grid;grid-template-columns:64px 1fr auto;gap:10px;align-items:start;border-top:1px solid #eef2f7;padding-top:10px}
.evt2:first-child{border-top:0;padding-top:0}
.evt3{display:grid;grid-template-columns:64px 1fr;gap:10px;align-items:start;border-top:1px solid #eef2f7;padding-top:10px}
.evt3:first-child{border-top:0;padding-top:0}
.time{color:#94a3b8;font-weight:900}
.line{color:#0f172a;font-weight:850;line-height:1.5}
.comm-foot{padding:10px 12px;border-top:1px solid #eef2f7;display:flex;gap:8px}
.input{flex:1;height:34px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;outline:none}
.primary{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  background:#155eef;
  border:1px solid #155eef;
  color:#fff;
  border-radius:10px;
  padding:5px 10px;
  font-weight:950;
  cursor:pointer;
  min-height:32px;
  line-height:1.3;
  white-space:nowrap;
  font-size:13px;
}
.btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  border:1px solid #d9e2ef;
  border-radius:10px;
  background:#fff;
  color:#475569;
  padding:5px 10px;
  font-weight:950;
  cursor:pointer;
  min-height:32px;
  line-height:1.3;
  white-space:nowrap;
  font-size:13px;
}
.btn-sm{min-height:30px;padding:4px 10px;font-size:12px;border-radius:10px}
.primary.btn-sm{min-height:30px;padding:4px 10px;font-size:12px}

/* 右侧 record 区：卡片头部固定单行 */
.card-head.one-line{flex-wrap:nowrap}
.card-head.one-line .card-title{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ghost{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  width:100%;
  min-height:32px;
  border-radius:10px;
  border:1px solid #cfe0ff;
  background:#eef5ff;
  color:#155eef;
  font-weight:950;
  cursor:pointer;
  padding:5px 10px;
  line-height:1.3;
  white-space:nowrap;
  font-size:13px;
}

.ai-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;padding:10px 12px}
.ai-tile{border:1px solid #eef2f7;border-radius:12px;background:#fbfdff;padding:10px;text-align:center}
.ai-ico{width:32px;height:32px;border-radius:12px;background:#eef5ff;color:#155eef;display:grid;place-items:center;margin:0 auto 6px;font-weight:950}
.ai-ico[data-tone="g"]{background:#ecfff3;color:#16a34a}
.ai-ico[data-tone="o"]{background:#fff7ed;color:#f97316}
.ai-name{font-weight:900;color:#0f172a;font-size:12px;line-height:1.3}

.audit-box{padding:10px 12px;display:grid;gap:8px}
.row2{display:flex;gap:8px;align-items:baseline}
.next{padding:10px 12px;display:grid;gap:8px}
.next-actions{display:flex;gap:8px;margin-top:6px}

.pad{padding:8px 10px}
.pad.pad-lg{padding:12px 12px}
.hline{height:1px;background:#eef2f7;margin:12px 0}
.stack{display:grid;gap:8px}
.full{width:100%}
.long{color:#0f172a;line-height:1.7;font-size:13px}
.file-list{display:grid;gap:10px}
.file-row{display:flex;align-items:center;justify-content:space-between;gap:10px;border:1px solid #eef2f7;border-radius:12px;background:#fff;padding:10px 12px}
.file-left{display:flex;align-items:center;gap:10px;min-width:0;flex:1}
.file-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
.file-ico{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;font-weight:950;color:#fff;flex:0 0 auto}
.file-ico[data-type="pdf"]{background:#ef4444}
.file-ico[data-type="zip"]{background:#f97316}
.file-main{min-width:0;flex:1}
.file-name{font-weight:950;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.file-sub{font-size:12px;margin-top:2px}
.icon-more{width:32px;height:32px;border-radius:10px;border:1px solid #e6edf7;background:#fff;color:#64748b;font-weight:950;cursor:pointer}
.icon-more:hover{border-color:#cfe0ff;background:#f8fbff;color:#155eef}
.empty{border:1px dashed #cbd5e1;background:#fbfdff;border-radius:12px;padding:14px}
.empty-title{font-weight:950;color:#0f172a}
.empty-actions{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.review-actions{display:flex;gap:8px;flex-wrap:wrap}
.doc-sec{border-top:1px solid #eef2f7;padding-top:10px;margin-top:10px}
.doc-sec:first-child{border-top:0;padding-top:0;margin-top:0}
.doc-h{font-weight:950;color:#0f172a;font-size:13px}
.doc-p{margin-top:6px;color:#334155;line-height:1.7;font-size:13px}
.audit-row{display:flex;gap:10px;align-items:flex-start;border-top:1px solid #eef2f7;padding-top:10px}
.audit-row:first-child{border-top:0;padding-top:0}
.audit-at{width:64px;flex:0 0 auto;color:#94a3b8;font-weight:900}
.audit-line{color:#0f172a;font-weight:850;font-size:13px}
.todo-list{display:grid;gap:10px}
.todo-row{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;border:1px solid #eef2f7;border-radius:12px;background:#fff;padding:10px}
.todo-title{font-weight:950;color:#0f172a}
.kw{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.kw-pill{border:1px solid #fed7aa;background:#fff7ed;color:#c2410c;border-radius:999px;padding:4px 10px;font-weight:950;font-size:12px}
.row3{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.row3-main{font-weight:900;color:#0f172a}

.q-table-wrap{border:1px solid #e6edf7;border-radius:12px;background:#fff;overflow:auto;flex:1}
.q-table{width:100%;border-collapse:collapse;font-size:13px}
.q-table thead tr{border-bottom:1px solid #eef2f7;background:#f8fafc}
.q-table th{padding:10px 12px;text-align:left;color:#64748b;font-weight:900;white-space:nowrap}
.q-table td{padding:10px 12px;border-bottom:1px solid #f1f5f9;white-space:nowrap}
.q-row{cursor:pointer}
.q-row:hover td{background:#f8fbff}
.q-row.active td{background:#eef5ff}
.q-row:last-child td{border-bottom:0}
.truncate{max-width:360px;overflow:hidden;text-overflow:ellipsis}

.pm-overview{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:12px;padding:12px;background:#fff;overflow:hidden}
.overview-left{min-height:0;display:flex;flex-direction:column;overflow:hidden}

/* 统计卡片 */
.stat-cards{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;padding:12px 12px 0}
.stat-card{display:flex;align-items:center;gap:10px;background:#f8fafc;border:1px solid #e6edf7;border-radius:10px;padding:12px 14px}
.stat-icon{width:40px;height:40px;border-radius:10px;display:grid;place-items:center;flex-shrink:0}
.stat-body{min-width:0}
.stat-label{font-size:11px;color:#64748b;font-weight:600;white-space:nowrap}
.stat-val{font-size:22px;font-weight:900;color:#111827;line-height:1.2}
.stat-sub{font-size:11px;font-weight:700;margin-top:2px}

/* 筛选栏 */
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

/* 表格头行 */
.q-table-head-row{display:flex;align-items:center;justify-content:space-between;padding:10px 12px 6px;font-size:13px}

/* 状态标签 */
.status-tag{display:inline-flex;align-items:center;border-radius:999px;padding:3px 9px;font-size:11px;font-weight:800}
.status-tag[data-s="gen"]{background:#eff6ff;color:#1d4ed8}
.status-tag[data-s="review"]{background:#fff7ed;color:#c2410c}
.status-tag[data-s="plan"]{background:#f5f3ff;color:#6d28d9}
.status-tag[data-s="follow"]{background:#ecfdf5;color:#059669}
.status-tag[data-s="push"]{background:#fdf4ff;color:#a21caf}
.status-tag[data-s="abnormal"]{background:#fff1f2;color:#dc2626}
.overview-right{min-height:0;height:100%;display:flex;flex-direction:column;gap:12px;overflow-y:auto;overflow-x:hidden;padding-right:12px;padding-bottom:12px;box-sizing:border-box}
.side-empty{display:flex;align-items:center;justify-content:center;height:120px;color:#94a3b8;font-size:13px}
.workbench{display:grid;gap:10px}
.wb-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.wb-name{font-weight:950;color:#0f172a}
.wb-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px 12px;border-top:1px solid #eef2f7;padding-top:10px;margin-top:2px}
.wb-kv .k{color:#94a3b8;font-size:12px;font-weight:850}
.wb-kv .v{margin-top:4px;font-weight:900;color:#0f172a;line-height:1.35}

/* 右侧极简标题 */
.side-title{min-width:0;display:flex;flex-direction:column;gap:2px}
.side-name{font-weight:950;color:#0f172a}
.side-sub{color:#64748b;font-weight:850;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.side-explain{color:#334155;line-height:1.65;font-size:13px}

.mini-kv2{display:grid;grid-template-columns:1fr 1fr;gap:10px 12px}
.kv2 .k{color:#94a3b8;font-size:12px;font-weight:850}
.kv2 .v{margin-top:4px;font-weight:900;color:#0f172a;line-height:1.35}

.tag-grid{display:grid;gap:10px}
.tagline{display:flex;align-items:center;justify-content:space-between;gap:10px}
.tagline .t{color:#94a3b8;font-size:12px;font-weight:850}
.tagline .v{font-weight:900;color:#0f172a;line-height:1.35;text-align:right}

/* 横向流程进度（参考图样式） */
.flow5h{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;align-items:start}
.flow5h-node{position:relative;display:grid;grid-template-rows:18px auto;justify-items:center;min-width:0}
.flow5h-node .pt{position:relative;width:18px;height:18px;display:grid;place-items:center}
.flow5h-node .dot{width:10px;height:10px;border-radius:50%;background:#cbd5e1;display:block}
.flow5h-node .check{position:absolute;inset:0;display:grid;place-items:center;font-size:12px;font-weight:950;color:#16a34a}
.flow5h-node .lab{
  margin-top:8px;
  font-size:11px;
  font-weight:900;
  color:#94a3b8;
  text-align:center;
  line-height:1.25;
  white-space:normal;        /* 允许换行，避免遮挡 */
  word-break:break-all;      /* 中文/长词都能断行 */
  max-width:72px;            /* 限宽后两行更稳定 */
  min-height:28px;           /* 预留两行高度，防止挤压 */
}
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
.btn-link-lite{
  border:0;
  background:transparent;
  color:#64748b;
  font-weight:950;
  font-size:12px;
  padding:4px 0;
  text-align:center;
  cursor:pointer;
}
.btn-link-lite:hover{color:#155eef}

.side-panel{overflow:hidden}
.panel-split{height:1px;background:#eef2f7}
.sec-h{font-weight:950;color:#0f172a;font-size:12px;margin-bottom:8px}

/* 右侧合并面板：整体字号下调 */
.side-panel .side-name{font-size:16px}
.side-panel .side-sub{font-size:12px}
.side-panel .pill{font-size:11px}
.side-panel .tag2{font-size:11px}

.side-panel .kv2 .k{font-size:11px}
.side-panel .kv2 .v{font-size:13px;font-weight:900}

.side-panel .tagline .t{font-size:11px}
.side-panel .tagline .v{font-size:12px}

.side-panel .side-explain{font-size:12px}

.side-panel .btn.full,
.side-panel .primary.full{font-size:12px;min-height:34px}
.quick-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.quick-card{display:flex;align-items:center;gap:10px;border:1px solid #eef2f7;border-radius:12px;background:#fbfdff;padding:12px;text-align:left;cursor:pointer}
.quick-card:hover{border-color:#cfe0ff;background:#eef5ff}
.qc-ico{width:34px;height:34px;border-radius:12px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-weight:950;flex:0 0 auto}
.qc-ico2{background:#ecfff3;color:#16a34a}
.qc-ico3{background:#f5f3ff;color:#8b5cf6}
.qc-ico-r{background:#fff1f2;color:#dc2626}
.qc-title{font-weight:950;color:#0f172a}
.qc-main{min-width:0}

.pm-detail{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:12px;padding:12px;background:#fff;overflow:hidden}
.detail-right{min-height:0;height:100%;display:flex;flex-direction:column;gap:10px;overflow-y:auto;overflow-x:hidden;padding-right:12px;padding-bottom:12px;box-sizing:border-box}

.detail-actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.detail-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.detail-head.compact{align-items:center}
.dh-name{font-weight:950;color:#0f172a;font-size:14px}
.dh-right{display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end}

.quick-links{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.quick-btn{display:flex;align-items:center;gap:10px;border:1px solid #e6edf7;border-radius:12px;background:#fbfdff;padding:10px 12px;text-align:left;cursor:pointer}
.quick-btn:hover{border-color:#cfe0ff;background:#eef5ff}
.quick-ico{width:32px;height:32px;border-radius:10px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-weight:950;flex-shrink:0}
.quick-ico-r{background:#fff1f2;color:#dc2626}
.quick-label{font-weight:950;color:#0f172a;font-size:13px}

.pill{display:inline-flex;align-items:center;border-radius:999px;padding:3px 10px;font-size:12px;font-weight:900}
.pill[data-tone="r"]{background:#fff1f2;color:#dc2626}
.pill[data-tone="o"]{background:#fff7ed;color:#c2410c}
.pill[data-tone="g"]{background:#ecfff3;color:#14843b}
.pill.mini{padding:2px 8px;font-size:11px}
.muted{color:#64748b;font-weight:750}

.stage-actions{display:flex;gap:8px;flex-wrap:wrap}
.stage-actions .full{width:100%}

.tl-row{display:grid;grid-template-columns:16px 1fr;gap:10px;align-items:start;padding:8px 0;border-top:1px solid #f1f5f9}
.tl-row:first-child{border-top:0;padding-top:0}
.tl-dot{width:8px;height:8px;border-radius:50%;margin-top:3px;flex-shrink:0}
.tl-dot[data-tone="b"]{background:#5b8ff9}
.tl-dot[data-tone="g"]{background:#16a34a}
.tl-dot[data-tone="r"]{background:#ef4444}
.tl-dot[data-tone="o"]{background:#f97316}
.tl-dot[data-tone="p"]{background:#8b5cf6}
.tl-dot[data-tone="y"]{background:#f59e0b}

.field-label{color:#475569;font-weight:850;font-size:12px;margin-bottom:6px}
.check-item{display:flex;align-items:center;gap:6px;font-size:13px;color:#334155;font-weight:850;cursor:pointer}
.review-note{width:100%;border:1px solid #d9e2ef;border-radius:8px;padding:8px 10px;outline:none;font-size:13px;color:#334155;resize:vertical;line-height:1.6}
.review-note:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.10)}
.reject-box{border:1px solid #fecaca;background:#fff5f5;border-radius:10px;padding:12px}

/* ── AI助手随访工作台 ── */
.follow-workbench{flex:1;min-height:0;display:grid;grid-template-columns:280px minmax(0,1fr) 420px;gap:10px;padding:12px;overflow:hidden}
.follow-patient-col{display:flex;flex-direction:column;min-height:0;background:#fff;border:1px solid #e6edf7;border-radius:10px;overflow:hidden}

/* 搜索+筛选固定区 */
.fp-filters{flex-shrink:0;padding:8px 8px 6px;border-bottom:1px solid #eef2f7;display:flex;flex-direction:column;gap:5px;background:#f8fafc}
.fp-search{height:30px;border:1px solid #d9e2ef;border-radius:7px;padding:0 9px;font-size:12px;outline:none;background:#fff;color:#0f172a;width:100%;box-sizing:border-box}
.fp-search:focus{border-color:#155eef;box-shadow:0 0 0 2px rgba(21,94,239,.10)}
.fp-filter-row{display:grid;grid-template-columns:1fr 1fr;gap:5px}
.fp-select{height:26px;border:1px solid #d9e2ef;border-radius:6px;padding:0 6px;font-size:11px;outline:none;background:#fff;color:#334155;cursor:pointer}
.fp-count{font-size:11px;padding:0 1px}

/* 患者列表独立滚动 */
.follow-patient-list{flex:1;overflow-y:auto;padding:4px;display:flex;flex-direction:column;gap:2px;scrollbar-width:thin}

/* 患者行：固定高度，禁止压扁裁字 */
.fp-row{
  border:1px solid transparent;
  border-left:3px solid transparent;
  border-radius:10px;
  background:#fff;
  padding:10px 10px;
  text-align:left;
  cursor:pointer;
  transition:background .12s,border-color .12s;
  display:flex;
  flex-direction:column;
  justify-content:center;
  gap:6px;
  min-height:72px; /* 目标：68-76px */
  line-height:1.25;
}
.fp-row:hover{background:#f8fbff;border-color:#e6edf7;border-left-color:#cfe0ff}
.fp-row.active{background:#eef5ff;border-color:#cfe0ff;border-left-color:#155eef}

/* 两行信息布局：第一行（姓名/性别年龄/风险），第二行（结节类型/阶段） */
.fp-row-line{display:flex;align-items:center;justify-content:space-between;gap:8px;min-width:0}
.fp-row-left{display:flex;align-items:baseline;gap:8px;min-width:0;flex:1}
.fp-name{font-weight:950;color:#0f172a;font-size:14px;flex-shrink:0}
.fp-demog{font-size:12px;white-space:nowrap}
.fp-risk{flex-shrink:0}
.fp-nodule{
  font-size:12px;
  color:#475569;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
  min-width:0;
}
.fp-last{flex-shrink:0;font-size:11px;white-space:nowrap}
.fp-stage-tag{
  flex-shrink:0;
  font-size:11px;
  color:#64748b;
  background:#f1f5f9;
  border-radius:6px;
  padding:2px 8px;
  white-space:nowrap;
  max-width:150px;
  overflow:hidden;
  text-overflow:ellipsis;
}

.follow-phone-col{display:flex;flex-direction:column;align-items:center;gap:8px;min-height:0;overflow-y:auto;padding:0 0 16px 0;scrollbar-width:thin}
.follow-ctrl-col{display:flex;flex-direction:column;gap:10px;min-height:0;overflow-y:auto;padding:0 2px 16px 0;scrollbar-width:thin}

/* 手机外壳（中间列，保持真实比例） */
.device-outer-lg{position:relative;width:290px;flex-shrink:0;align-self:center;margin-top:22px}
.device-outer-lg .device-btn-l{position:absolute;left:-5px;width:4px;height:28px;background:#2d3748;border-radius:2px 0 0 2px}
.device-outer-lg .device-btn-r{position:absolute;right:-5px;width:4px;height:42px;background:#2d3748;border-radius:0 2px 2px 0}
.screen-chat-lg{background:#f3f6fb;padding:8px;display:flex;flex-direction:column;gap:7px;overflow-y:auto;flex:1;min-height:0;max-height:580px}

/* 助手选择器 */
.assist-selector{background:#fff;border:1px solid #e6edf7;border-radius:10px;padding:10px 12px;box-shadow:0 4px 12px rgba(15,23,42,.04)}
.assist-selector-title{font-size:12px;font-weight:600;color:#64748b;margin-bottom:8px}
.assist-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.assist-card{position:relative;display:flex;flex-direction:column;align-items:center;gap:4px;border:1px solid #e6edf7;border-radius:10px;background:#fff;padding:8px 4px;cursor:pointer;transition:border-color .15s}
.assist-card:hover{border-color:#cfe0ff;background:#f8fbff}
.assist-card.active{border-color:#155eef;background:#eef5ff;box-shadow:0 0 0 2px rgba(21,94,239,.12)}
.assist-ico{width:32px;height:32px;border-radius:9px;display:grid;place-items:center;font-weight:950;font-size:13px;flex-shrink:0}
.assist-name{font-size:10px;font-weight:850;color:#334155;text-align:center;line-height:1.3;word-break:keep-all}
.assist-dot{position:absolute;top:6px;right:6px;width:6px;height:6px;border-radius:50%;border:1.5px solid #fff}
.assist-dot[data-tone="g"]{background:#16a34a}
.assist-dot[data-tone="o"]{background:#f97316}

/* 助手-计划折叠面板 */
.assist-plan-zone{background:#fff;border:1px solid #e6edf7;border-radius:10px;padding:10px 12px;box-shadow:0 4px 12px rgba(15,23,42,.04)}
.assist-plan-list{display:grid;gap:8px}
.assist-plan{border:1px solid #eef2f7;border-radius:10px;background:#fff;overflow:hidden}
.assist-plan-sum{list-style:none;display:grid;grid-template-columns:30px 72px 1fr;gap:10px;align-items:center;padding:9px 10px;cursor:pointer}
.assist-plan-sum::-webkit-details-marker{display:none}
.assist-plan-ico{width:26px;height:26px;border-radius:9px;display:grid;place-items:center;font-weight:950;font-size:12px;flex-shrink:0}
.assist-plan-name{font-weight:950;color:#0f172a;font-size:12px;white-space:nowrap}
.assist-plan-mini{font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.assist-plan-body{border-top:1px solid #eef2f7;padding:10px 10px;background:#fbfdff;display:grid;gap:10px}
.assist-plan-sec{display:grid;gap:6px}
.assist-plan-sec-h{font-weight:950;color:#0f172a;font-size:12px}
.assist-plan-sec-p{color:#334155;line-height:1.7;font-size:12px;white-space:pre-wrap}

/* 助手介绍图（右侧控制面板） */
.assist-img-wrap{
  background:#fff;
  border:1px solid #e6edf7;
  border-radius:10px;
  overflow:hidden;
  flex:1;
  min-height:0;
  display:flex;
  align-items:stretch;
  justify-content:stretch;
  padding:4px; /* 减少卡片内部留白 */
}
.assist-intro-img{
  width:100%;
  height:100%;
  object-fit:contain;
  display:block;
  max-height:560px; /* 放大展示区域 */
}

/* 右侧主焦点：当前助手卡片（不裁切，内容可滚动） */
.assist-focus{
  flex:1;
  min-height:0;
  display:flex;
  flex-direction:column;
  overflow:hidden; /* 保留圆角裁边 */
}
.assist-focus-body{
  padding:12px 12px 14px;
  display:grid;
  gap:10px;
  min-height:0;
  overflow:auto; /* 关键：避免“展示不完整”被直接裁掉 */
}
.assist-state{font-size:11px;font-weight:950;border-radius:999px;padding:3px 10px;background:#f1f5f9;color:#64748b;white-space:nowrap}
.assist-state[data-tone="g"]{background:#ecfff3;color:#14843b}
.assist-state[data-tone="o"]{background:#fff7ed;color:#c2410c}


/* 手机预览区 */
.phone-preview-wrap{display:flex;flex-direction:column;gap:8px;align-items:center;flex-shrink:0}
.phone-preview-label{width:100%;display:flex;justify-content:space-between;align-items:center;padding:0 2px;font-size:12px;font-weight:600;color:#334155}

/* 手机设备外壳（窄版，真实手机比例） */
.device-outer{position:relative;width:320px;flex-shrink:0;align-self:center}
.device-btn-l{position:absolute;left:-5px;width:4px;height:26px;background:#2d3748;border-radius:2px 0 0 2px}
.device-btn-r{position:absolute;right:-5px;width:4px;height:40px;background:#2d3748;border-radius:0 2px 2px 0}
.device-body{background:#1a1a2e;border-radius:36px;padding:8px;box-shadow:0 0 0 2px #2d3748,0 16px 48px rgba(0,0,0,.5),inset 0 0 0 1px rgba(255,255,255,.06)}
.device-notch{display:flex;align-items:center;justify-content:center;gap:7px;height:20px;margin-bottom:3px}
.device-camera{width:8px;height:8px;border-radius:50%;background:#0d0d1a;border:2px solid #2d3748}
.device-speaker{width:44px;height:4px;border-radius:999px;background:#0d0d1a}
.device-screen{background:#fff;border-radius:24px;overflow:hidden;display:flex;flex-direction:column}
.device-home-bar-wrap{display:flex;justify-content:center;padding:7px 0 3px}
.device-home-bar{width:80px;height:3px;background:#3d3d5c;border-radius:999px}

/* 屏幕内容 */
.screen-status{background:#f8fafc;padding:4px 12px;display:flex;justify-content:space-between;align-items:center;font-size:10px;font-weight:850;color:#334155}
.screen-topbar{background:#fff;padding:7px 10px;display:flex;align-items:center;gap:7px;border-bottom:1px solid #eef2f7}
.screen-back{font-size:18px;color:#155eef;font-weight:900;cursor:pointer;flex-shrink:0;line-height:1}
.screen-contact{display:flex;align-items:center;gap:7px;flex:1}
.screen-avatar{width:26px;height:26px;border-radius:50%;display:grid;place-items:center;font-weight:950;font-size:11px;flex-shrink:0}
.screen-name{font-weight:950;color:#0f172a;font-size:12px}
.screen-sub{font-size:10px;color:#94a3b8;margin-top:1px}
.screen-chat{background:#f3f6fb;padding:8px;display:flex;flex-direction:column;gap:7px;overflow-y:auto;flex:1;min-height:0;max-height:320px}
.screen-date-divider{text-align:center;font-size:10px;color:#94a3b8;padding:2px 0 4px}
.screen-input-bar{background:#fff;border-top:1px solid #eef2f7;padding:6px 8px;display:flex;align-items:center;gap:6px}
.screen-input-field{flex:1;height:28px;border:1px solid #e6edf7;border-radius:14px;background:#f8fafc;padding:0 10px;font-size:11px;color:#94a3b8;display:flex;align-items:center}
.screen-send-btn{width:28px;height:28px;border-radius:50%;background:#155eef;border:0;color:#fff;display:grid;place-items:center;cursor:pointer;flex-shrink:0}

/* 聊天气泡（屏幕内） */
.sc-msg{display:flex;gap:6px;align-items:flex-start}
.sc-msg.patient{flex-direction:row-reverse}
.sc-avatar{width:24px;height:24px;border-radius:50%;display:grid;place-items:center;font-size:10px;font-weight:950;flex-shrink:0}
.sc-bubble{border-radius:10px;padding:7px 9px;font-size:11px;line-height:1.55;max-width:78%}
.sc-bubble.ai-bubble{background:#fff;color:#334155;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.sc-bubble.patient-bubble{background:#d1fae5;color:#065f46}
.sc-card{background:#fff;border:1px solid #e6edf7;border-radius:9px;padding:8px 10px;display:flex;align-items:center;gap:8px;cursor:pointer;max-width:78%;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.sc-card-ico{font-size:16px;flex-shrink:0}
.sc-card-body{flex:1;min-width:0}
.sc-card-title{font-weight:950;color:#0f172a;font-size:11px}
.sc-card-sub{font-size:10px;color:#94a3b8;margin-top:1px}

/* 随访配置面板 */
.scene-tag{display:inline-block;background:#eef5ff;color:#155eef;border-radius:6px;padding:3px 10px;font-size:12px;font-weight:850}
.tpl-box{background:#f8fafc;border:1px solid #e6edf7;border-radius:8px;padding:10px 12px;font-size:12px;color:#334155;line-height:1.6}
.follow-actions{display:flex;gap:8px;justify-content:flex-end;padding:4px 0}

/* 助手身份展示卡 */
.assist-profile-card{display:flex;gap:16px;padding:14px;align-items:flex-start}
.assist-profile-img{width:180px;height:auto;object-fit:contain;border-radius:10px;flex-shrink:0;border:1px solid #e6edf7;background:#f8fafc;max-height:200px}
.assist-profile-info{flex:1;min-width:0;display:flex;flex-direction:column;gap:8px}
.assist-profile-name{font-size:15px;font-weight:950;color:#0f172a;line-height:1.3;word-break:keep-all}
.assist-profile-tagline{font-size:12px;color:#64748b;line-height:1.6}
.assist-profile-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.assist-caps{display:flex;flex-wrap:wrap;gap:5px;margin-top:2px}
.cap-tag{border:1px solid #e6edf7;background:#f8fafc;color:#475569;border-radius:6px;padding:2px 8px;font-size:11px;font-weight:850}

/* 服务计划工作流 */
.workflow-row{display:flex;align-items:center;flex-wrap:wrap;gap:6px;padding:12px 14px}
.wf-step{display:flex;align-items:center;gap:5px;font-size:12px;color:#334155;font-weight:850;background:#f1f5f9;border-radius:6px;padding:4px 10px;white-space:nowrap}
.wf-num{width:16px;height:16px;border-radius:50%;background:#155eef;color:#fff;font-size:10px;font-weight:950;display:grid;place-items:center;flex-shrink:0}
.wf-arrow{color:#94a3b8;font-size:13px;font-weight:400;flex-shrink:0}

/* 执行数据 */
.exec-stats{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #eef2f7}
.exec-stat{display:flex;flex-direction:column;align-items:center;padding:12px 8px;border-right:1px solid #eef2f7;min-height:0}
.exec-stat:last-child{border-right:0}
.exec-stat b{font-size:20px;font-weight:950;color:#0f172a;line-height:1.2}
.exec-stat span{font-size:11px;color:#94a3b8;margin-top:4px;text-align:center;line-height:1.3}

/* ── 健康报告审核（复用 pm-detail 布局） ── */
.review-workbench{flex:1;min-height:0;display:grid;grid-template-columns:minmax(280px,1fr) minmax(360px,1.2fr);gap:12px;padding:12px;overflow:hidden}

/* 消息气泡 */
.phone-msg{display:flex;gap:8px;align-items:flex-start}
.phone-msg.patient{flex-direction:row-reverse}
.phone-msg-avatar{width:30px;height:30px;border-radius:50%;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-size:11px;font-weight:950;flex-shrink:0}
.phone-msg-avatar.patient-av{background:#dcfce7;color:#16a34a}
.phone-msg-body{display:flex;flex-direction:column;gap:3px;max-width:82%}
.phone-msg-name{font-size:11px;color:#94a3b8;font-weight:750;margin-bottom:2px}
.phone-bubble{background:#fff;border-radius:10px;padding:9px 11px;font-size:13px;color:#334155;line-height:1.6;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.phone-bubble.patient-bubble{background:#d1fae5;color:#065f46}
.risk-bubble{display:grid;gap:4px}
.risk-row{display:flex;align-items:flex-start;gap:8px}
.risk-label{font-size:12px;color:#94a3b8;font-weight:850;white-space:nowrap;min-width:52px;padding-top:1px}

/* 报告卡片消息 */
.phone-card-msg{background:#fff;border:1px solid #e6edf7;border-radius:10px;padding:10px 12px;display:flex;align-items:center;gap:10px;cursor:pointer;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.phone-card-msg:hover{border-color:#cfe0ff;background:#f8fbff}
.phone-card-ico{font-size:20px;flex-shrink:0}
.phone-card-info{flex:1;min-width:0}
.phone-card-title{font-weight:950;color:#0f172a;font-size:13px}
.phone-card-sub{font-size:11px;color:#94a3b8;margin-top:2px}

/* 操作按钮行 */
.phone-actions{display:flex;gap:8px;padding:4px 0}
.phone-action-btn{flex:1;height:36px;border-radius:8px;border:1px solid #d9e2ef;background:#fff;color:#334155;font-weight:850;font-size:13px;cursor:pointer}
.phone-action-btn.primary-btn{background:#155eef;border-color:#155eef;color:#fff}

/* 聊天气泡 */
.chat-list{padding:10px 12px;display:grid;gap:12px;max-height:260px;overflow-y:auto}
.chat-row{display:flex;gap:8px;align-items:flex-start}
.chat-row.mine{flex-direction:row-reverse}
.chat-avatar{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;font-size:11px;font-weight:950;flex-shrink:0;background:#e0e7ff;color:#4f46e5}
.chat-avatar.patient{background:#dcfce7;color:#16a34a}
.chat-bubble-wrap{display:flex;flex-direction:column;gap:3px;max-width:80%}
.chat-row.mine .chat-bubble-wrap{align-items:flex-end}
.chat-meta{font-size:11px;color:#94a3b8;font-weight:750}
.chat-bubble{background:#f1f5f9;border-radius:12px;padding:8px 10px;font-size:13px;color:#334155;line-height:1.6}
.chat-row.mine .chat-bubble{background:#eef5ff;color:#1e40af}
/* ── 健康报告页面 ─────────────────────────────────────────── */
.rp-page{flex:1;min-height:0;display:flex;flex-direction:column;gap:10px;padding:12px;background:#fff;overflow:hidden}

/* KPI */
.rp-kpi-row{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;flex-shrink:0}
.rp-kpi{background:#fff;border:1px solid #e6edf7;border-radius:10px;padding:10px 12px;position:relative;overflow:hidden}
.rp-kpi-ico{width:28px;height:28px;border-radius:8px;border:1px solid #e6edf7;background:#f8fafc;color:#64748b;display:grid;place-items:center;margin-bottom:4px}
.rp-kpi[data-tone="purple"] .rp-kpi-ico{background:#f5f3ff;border-color:#ddd6fe;color:#8b5cf6}
.rp-kpi[data-tone="green"] .rp-kpi-ico{background:#ecfdf5;border-color:#bbf7d0;color:#16a34a}
.rp-kpi[data-tone="orange"] .rp-kpi-ico{background:#fff7ed;border-color:#fed7aa;color:#f97316}
.rp-kpi[data-tone="red"] .rp-kpi-ico{background:#fff1f2;border-color:#fecdd3;color:#dc2626}
.rp-kpi-label{font-size:12px;color:#64748b;font-weight:500}
.rp-kpi-val{font-size:26px;font-weight:700;color:#0f172a;line-height:1;margin-top:3px}
.rp-kpi-delta{font-size:12px;color:#94a3b8;margin-top:3px}

/* 筛选栏 */
.rp-filter-bar{padding:10px 14px;flex-shrink:0}
.rp-filter-row{display:flex;align-items:flex-end;gap:10px;flex-wrap:wrap}
.rp-filter-item{display:flex;flex-direction:column;gap:4px;min-width:0}
.rp-filter-label{font-size:11px;color:#64748b;font-weight:850;white-space:nowrap}
.rp-filter-input{height:32px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;font-size:13px;color:#111827;outline:none;min-width:160px}
.rp-filter-input:focus{border-color:#155eef}
.rp-filter-select{height:32px;border:1px solid #d9e2ef;border-radius:8px;padding:0 10px;font-size:13px;color:#111827;outline:none;min-width:140px;background:#fff}
.rp-filter-select:focus{border-color:#155eef}
.rp-filter-actions{display:flex;gap:6px;align-items:flex-end;margin-left:auto}

/* 主体 */
.rp-body{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:10px;overflow:hidden}
.rp-list-card{min-height:0;display:flex;flex-direction:column;overflow:hidden}
.rp-count{font-size:12px;color:#94a3b8;font-weight:500;margin-left:6px}

/* 结节标签 */
.nodule-tag{display:inline-flex;align-items:center;border-radius:6px;padding:2px 7px;font-size:11px;font-weight:700;background:#eef5ff;color:#155eef}
.nodule-tag[data-type="lung"]{background:#ecfdf5;color:#15803d}
.nodule-tag[data-type="thyroid"]{background:#fff7ed;color:#c2410c}
.nodule-tag[data-type="breast"]{background:#fdf4ff;color:#a21caf}
.nodule-tag[data-type="triple"]{background:#fff1f2;color:#dc2626}

/* AI状态标签 */
.rp-status-tag{display:inline-flex;align-items:center;border-radius:6px;padding:2px 7px;font-size:11px;font-weight:700;background:#f1f5f9;color:#475569}
.rp-status-tag[data-s="解析完成"]{background:#ecfdf5;color:#15803d}
.rp-status-tag[data-s="AI解析中"]{background:#f5f3ff;color:#8b5cf6}
.rp-status-tag[data-s="待生成报告"]{background:#fff7ed;color:#c2410c}
.rp-status-tag[data-s="待医生复核"]{background:#eff6ff;color:#1d4ed8}
.rp-status-tag[data-s="异常报告"]{background:#fff1f2;color:#dc2626}

/* 详情面板 */
.rp-detail{display:flex;flex-direction:column;gap:8px;overflow-y:auto;min-height:0}
.rp-detail-info{display:flex;align-items:flex-start;gap:10px;padding:10px 12px}
.rp-info-grid{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:4px 0}
.rp-info-row{display:flex;gap:4px;font-size:12px;line-height:1.8}
.rp-ik{color:#94a3b8;font-weight:850;white-space:nowrap}
.rp-iv{color:#0f172a;font-weight:700}
.rp-doc-btn{width:44px;height:44px;border-radius:10px;border:1px solid #e6edf7;background:#f8fafc;color:#64748b;display:grid;place-items:center;cursor:pointer;flex-shrink:0}
.rp-pad{padding:10px 12px;font-size:13px;color:#334155;line-height:1.6}
.rp-ai-grid{display:grid;grid-template-columns:1fr 1fr;gap:2px 0;padding:10px 12px}
.rp-ai-row{display:flex;gap:4px;font-size:12px;line-height:1.8}
.rp-ak{color:#94a3b8;font-weight:850;white-space:nowrap}
.rp-risk-bar{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;background:#fff7ed;border:1px solid #fed7aa}
.rp-risk-bar[data-tone="r"]{background:#fff1f2;border-color:#fecdd3}
.rp-risk-label{font-weight:950;font-size:13px;color:#c2410c;white-space:nowrap}
.rp-risk-bar[data-tone="r"] .rp-risk-label{color:#dc2626}
.rp-risk-desc{font-size:12px;color:#64748b}
.rp-gen-status{display:inline-flex;align-items:center;border-radius:6px;padding:2px 8px;font-size:11px;font-weight:700;background:#fff7ed;color:#c2410c}
.rp-gen-status[data-s="待审核"]{background:#eff6ff;color:#1d4ed8}

/* 处理流程 */
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

/* 快捷操作 */
.rp-actions{display:flex;gap:8px;padding:10px 12px;flex-wrap:wrap}
.rp-audit-panel{}
.rp-audit-body{padding:10px 12px}
.rp-audit-label{font-size:12px;font-weight:750;color:#334155;margin-bottom:4px}
.rp-audit-ta{width:100%;border:1px solid #d9e2ef;border-radius:6px;padding:8px 10px;font-size:13px;line-height:1.6;color:#1e293b;resize:vertical;outline:none;font-family:inherit}
.rp-audit-ta:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.1)}
.rp-empty{display:flex;align-items:center;justify-content:center;height:200px;color:#94a3b8;font-size:13px}

/* 报告查看弹窗 */
.rp-modal-mask{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:9999;display:flex;align-items:center;justify-content:center}
.rp-modal{background:#fff;border-radius:12px;width:min(860px,96vw);max-height:88vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.25)}
.rp-modal-head{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid #e6edf7;flex-shrink:0}
.rp-modal-title{font-size:16px;font-weight:800;color:#111827}
.rp-modal-close{border:0;background:transparent;font-size:18px;color:#94a3b8;cursor:pointer;padding:0 4px}
.rp-modal-close:hover{color:#374151}
.rp-modal-body{padding:20px 24px;overflow-y:auto;flex:1;font-size:14px;line-height:1.8;color:#1e293b}
.rp-modal-body h1,.rp-modal-body h2,.rp-modal-body h3{color:#111827;margin:16px 0 8px}
.rp-modal-body p{margin:6px 0}
</style>

