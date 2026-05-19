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
                <div class="stat-label">{{ reportTerms.toReview }}</div>
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
                <label>{{ scenario.personLabel }}来源</label>
                <select class="q-filter-select" v-model="qSource">
                  <option value="">全部</option>
                  <option v-for="src in scenario.sourceOptions" :key="src">{{ src }}</option>
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
                  <option value="review">{{ reportTerms.toReview }}</option>
                  <option value="plan">任务待下发</option>
                  <option value="follow">任务执行中</option>
                  <option value="push">待推送</option>
                  <option value="abnormal">异常待处理</option>
                </select>
              </div>
              <div class="q-filter-actions">
                <button class="btn" type="button" @click="qSearch='';qSource='';qNodule='';qRisk='';qStatus=''">重置</button>
                <button class="primary" type="button">查询</button>
                <button class="primary" type="button" @click="goRecord(null)">+ 新建档案</button>
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
                  <th style="width:80px">企微</th>
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
                  <td><span class="wecom-badge" :data-on="isWecomBound(p)">{{ wecomStatusText(p) }}</span></td>
                  <td class="muted">{{ p.owner }}</td>
                  <td>
                    <div style="display:flex;gap:8px">
                      <button class="tbl-act" type="button" @click.stop="openPatientWorkspace(p)">查看</button>
                      <button class="tbl-act" type="button" @click.stop="setSubTab('followup-plan')">任务</button>
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
                <div class="kv2"><div class="k">企微</div><div class="v"><span class="wecom-badge" :data-on="isWecomBound(activePatient)">{{ wecomStatusText(activePatient) }}</span></div></div>
              </div>
              <div class="wecom-bind-row">
                <div class="wecom-bind-main">
                  <b>{{ activePatient.wecomExternalUserid || activePatient.wecomUserid || '未绑定企业微信身份' }}</b>
                  <span>{{ isWecomBound(activePatient) ? '可用于后续企微触达和患者会话识别' : '绑定 external_userid 后才能做真实企微随访' }}</span>
                </div>
                <div class="wecom-bind-actions">
                  <button class="tbl-act" type="button" @click="openWecomBind(activePatient)">{{ isWecomBound(activePatient) ? '修改' : '绑定' }}</button>
                  <button v-if="isWecomBound(activePatient)" class="tbl-act danger" type="button" @click="unbindWecom(activePatient)">解绑</button>
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
                  <button
                    :class="a.primary ? 'primary full' : 'btn-link-lite'"
                    type="button"
                    @click="a.onClick()"
                    :disabled="a.disabled"
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
        <RecordView :embedded="true" :patient="recordPatient" @back="backToQueue" />
      </div>

      <!-- detail tab：患者全流程管理工作台 -->
      <div v-else-if="subTab === 'detail'" class="patient-workspace">
        <section class="workspace-hero card">
          <div class="workspace-id">
            <button class="btn-link-lite" type="button" @click="setSubTab('queue')">返回队列</button>
            <div>
              <div class="workspace-name">{{ activePatient.name || '未选择患者' }}</div>
              <div class="workspace-sub">{{ activePatient.gender }} · {{ activePatient.age }}岁 · {{ activePatient.phoneMasked }} · {{ activePatient.nodules }}</div>
            </div>
          </div>
          <div class="workspace-badges">
            <span class="pill" :data-tone="activePatient.riskTone">{{ activePatient.risk || '未评估' }}</span>
            <span class="status-tag" :data-s="statusKey(activePatient)">{{ statusLabel(activePatient) }}</span>
            <span class="wecom-badge" :data-on="isWecomBound(activePatient)">{{ wecomStatusText(activePatient) }}</span>
          </div>
        </section>

        <section class="workspace-flow card">
          <div v-for="step in patientFlowSteps" :key="step.key" class="workspace-flow-node" :data-state="step.state">
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
                <button class="btn" type="button" @click="goRecord(activePatient)">编辑档案</button>
              </div>
              <div class="profile-grid">
                <label class="profile-field"><span>姓名</span><input v-model="activePatient.name" :readonly="!patientEditMode"></label>
                <label class="profile-field"><span>性别</span><input v-model="activePatient.gender" :readonly="!patientEditMode"></label>
                <label class="profile-field"><span>年龄</span><input v-model="activePatient.age" :readonly="!patientEditMode"></label>
                <label class="profile-field"><span>来源</span><input v-model="activePatient.source" :readonly="!patientEditMode"></label>
                <label class="profile-field"><span>负责人</span><input v-model="activePatient.owner" :readonly="!patientEditMode"></label>
                <label class="profile-field"><span>结节类型</span><input v-model="activePatient.nodules" :readonly="!patientEditMode"></label>
                <label class="profile-field"><span>企微 external_userid</span><input :value="activePatient.wecomExternalUserid || '未绑定'" readonly></label>
              </div>
              <div class="profile-note">
                <label class="profile-field wide"><span>病史/既往史/体征</span><textarea v-model="activePatient.profileNote" :readonly="!patientEditMode"></textarea></label>
              </div>
              <div class="record-report-card">
                <div>
                  <b>关联健康报告</b>
                  <span v-if="activePatient.latestReport?.id">
                    {{ activePatient.latestReport.report_code || `报告 #${activePatient.latestReport.id}` }} · {{ reportDbStatusLabel(activePatient.latestReport.status) }}
                  </span>
                  <span v-else>当前档案还没有生成健康报告</span>
                </div>
                <button
                  v-if="activePatient.latestReport?.id"
                  class="btn"
                  type="button"
                  @click="viewReport(activePatient.latestReport.id)"
                >
                  查看报告
                </button>
              </div>

              <div class="workspace-summary-grid">
                <div class="workspace-summary-card">
                  <span>档案记录</span>
                  <b>{{ activePatient.workspaceRecords?.length || 0 }}</b>
                  <em>{{ latestRecordLabel }}</em>
                </div>
                <div class="workspace-summary-card">
                  <span>健康报告</span>
                  <b>{{ activePatient.workspaceReports?.length || 0 }}</b>
                  <em>{{ activePatient.latestReport?.status ? reportDbStatusLabel(activePatient.latestReport.status) : '未生成' }}</em>
                </div>
                <div class="workspace-summary-card">
                  <span>随访计划</span>
                  <b>{{ activePatient.workspacePlans?.length || 0 }}</b>
                  <em>{{ activePlanLabel }}</em>
                </div>
                <div class="workspace-summary-card">
                  <span>执行任务</span>
                  <b>{{ activePatient.workspaceTasks?.length || 0 }}</b>
                  <em>{{ taskExecutionSummary }}</em>
                </div>
              </div>

              <div class="upload-grid">
                <section class="upload-panel">
                  <div class="upload-title">影像报告</div>
                  <div class="upload-sub">支持 PDF、图片等文件；后续可接入结构化解析。</div>
                  <input ref="imagingInputRef" type="file" multiple accept=".pdf,image/*" style="display:none" @change="handleImagingUpload">
                  <button class="primary" type="button" @click="imagingInputRef?.click()">上传影像报告</button>
                  <div class="file-list">
                    <div v-for="file in activePatient.assets?.imagingReports || []" :key="file.id" class="file-row">
                      <div><b>{{ file.name }}</b><span>{{ file.uploadedAt }} · {{ file.uploader }}</span></div>
                      <button class="btn-link-lite" type="button" @click="removeAsset('imagingReports', file.id)">删除</button>
                    </div>
                    <div v-if="!(activePatient.assets?.imagingReports || []).length" class="empty-line">暂无影像报告</div>
                  </div>
                </section>

                <section class="upload-panel">
                  <div class="upload-title">手机舌诊 H5</div>
                  <div class="upload-sub">B端只生成手机可访问的舌诊链接；请用患者手机或健康管理师手机打开，电脑和平板不作为采集终端。</div>
                  <div class="tongue-h5-panel">
                    <div class="tongue-h5-copy">
                      <input :value="activePatient.tongueMobileOpenUrl || activePatient.tongueH5Url || '生成后显示手机舌诊链接'" readonly>
                      <button class="btn-link-lite" type="button" @click="copyWorkspaceTongueLink" :disabled="!(activePatient.tongueMobileOpenUrl || activePatient.tongueH5Url)">复制链接</button>
                    </div>
                    <div class="tongue-h5-body">
                      <div class="tongue-qr">
                        <img v-if="workspaceTongueQrUrl" :src="workspaceTongueQrUrl" alt="舌诊H5二维码">
                        <span v-else>生成二维码</span>
                      </div>
                      <div class="tongue-h5-help">
                        <b>手机打开提示</b>
                        <span>生成链接后，用手机扫码或复制链接发送给患者；进入第三方 H5 后在手机内完成舌面图、舌下图采集。</span>
                        <span>检测完成后，结果通过报告回调或报告检索回流到本系统。</span>
                      </div>
                    </div>
                  </div>
                  <div class="tongue-diagnosis-bar">
                    <button
                      class="primary"
                      type="button"
                      @click="startWorkspaceTongueDiagnosis"
                      :disabled="tongueSubmitting || !activePatient.workspaceRecordId"
                    >
                      {{ tongueSubmitting ? '提交中...' : workspaceTongueActionLabel }}
                    </button>
                    <button
                      class="btn"
                      type="button"
                      @click="syncWorkspaceTongueReport"
                      :disabled="tongueSyncing || !activePatient.tongueTask?.id"
                    >
                      {{ tongueSyncing ? '同步中...' : '同步舌诊结果' }}
                    </button>
                    <span v-if="activePatient.tongueTask" class="tongue-status">{{ workspaceTongueStatusLabel }}</span>
                  </div>
                  <div v-if="activePatient.tongueTask?.tongue_feature" class="tongue-result">
                    {{ activePatient.tongueTask.tongue_feature }}
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
                  <div class="section-sub">AI意见作为可迭代草稿，支持再次生成、人工编辑、提交审核和历史版本留痕。</div>
                </div>
                <div class="section-actions">
                  <button class="btn" type="button" @click="regenerateAdviceForActive" :disabled="adviceGenerating">{{ adviceGenerating ? '生成中...' : '再次生成建议' }}</button>
                  <button class="primary" type="button" @click="saveAdviceDraft">保存草稿</button>
                  <button class="primary" type="button" @click="submitAdviceReview">提交审核</button>
                </div>
              </div>
              <div class="advice-status-row">
                <span class="status-tag" :data-s="activeAdvice.status">{{ adviceStatusLabel(activeAdvice.status) }}</span>
                <span class="muted">当前版本：V{{ activeAdvice.version || 1 }} · {{ activeAdvice.updatedAt || '未保存' }}</span>
              </div>
              <textarea class="advice-editor" v-model="activeAdvice.content" placeholder="生成后的建议会出现在这里，也可以人工编辑。"></textarea>
              <div class="version-list">
                <div v-for="v in activeAdvice.history || []" :key="v.id" class="version-row">
                  <span>V{{ v.version }}</span><b>{{ adviceStatusLabel(v.status) }}</b><span>{{ v.savedAt }}</span>
                </div>
                <div v-if="!(activeAdvice.history || []).length" class="empty-line">暂无历史版本</div>
              </div>
            </section>

            <section class="flow-section card">
              <div class="section-head">
                <div>
                  <div class="section-title">四、最终健康报告</div>
                  <div class="section-sub">只有审核通过的建议才能写入最终报告，与草稿意见明确区分。</div>
                </div>
                <button class="primary" type="button" @click="approveAdviceToFinal" :disabled="activeAdvice.status !== 'reviewing'">审核通过并写入最终报告</button>
              </div>
              <div v-if="activePatient.finalReport?.content" class="final-report-box">
                <div class="final-report-meta">已归档 · {{ activePatient.finalReport.archivedAt }} · 来源 V{{ activePatient.finalReport.version }}</div>
                <p>{{ activePatient.finalReport.content }}</p>
              </div>
              <div v-else class="empty-line">暂无最终报告。请先生成/编辑建议并完成审核。</div>
            </section>
          </section>

          <aside class="workspace-side">
            <section class="card side-flow-card">
              <div class="section-title">健康管理任务与后续管理</div>
              <div class="follow-plan-box">
                <label class="profile-field"><span>复查周期</span><select v-model="activePatient.followPlan.cycle"><option>3个月</option><option>6个月</option><option>12个月</option></select></label>
                <label class="profile-field"><span>触达方式</span><select v-model="activePatient.followPlan.channel"><option>小程序</option><option>电话</option><option>企微</option><option>小程序+电话</option></select></label>
                <label class="profile-field wide"><span>任务重点</span><textarea v-model="activePatient.followPlan.note"></textarea></label>
                <button class="primary full" type="button" @click="saveFollowPlan">保存任务配置</button>
              </div>
            </section>

            <section class="card side-flow-card">
              <div class="section-title">管理记录</div>
              <div class="mgmt-log">
                <div v-for="log in activePatient.managementLogs || []" :key="log.id" class="mgmt-log-row">
                  <b>{{ log.action }}</b>
                  <span>{{ log.at }} · {{ log.by }}</span>
                  <p v-if="log.note">{{ log.note }}</p>
                </div>
              </div>
            </section>

            <section class="card side-flow-card">
              <div class="section-title">随访计划</div>
              <div class="chain-list">
                <div v-for="plan in activePatient.workspacePlans || []" :key="plan.id" class="chain-row">
                  <div>
                    <b>{{ plan.name }}</b>
                    <span>{{ planStatusLabel(plan.status) }} · {{ cycleLabelFromDays(plan.cycle_days) }} · {{ channelLabel(plan.channel) }}</span>
                  </div>
                  <em>{{ plan.activated_at || plan.created_at || '未启用' }}</em>
                </div>
                <div v-if="!(activePatient.workspacePlans || []).length" class="empty-line">暂无随访计划</div>
              </div>
            </section>

            <section class="card side-flow-card">
              <div class="section-title">任务执行记录</div>
              <div class="chain-list">
                <div v-for="task in activePatient.workspaceTasks || []" :key="task.id" class="chain-row" :data-alert="task.abnormal_flag">
                  <div>
                    <b>{{ task.title || taskTypeLabel(task.task_payload?.node?.task_type) }}</b>
                    <span>{{ trackingStatusLabel(task.status) }} · {{ channelLabel(task.channel) }} · {{ task.scheduled_send_at || task.due_at || '未排期' }}</span>
                  </div>
                  <em>{{ task.abnormal_flag ? '异常' : task.priority || 'normal' }}</em>
                </div>
                <div v-if="!(activePatient.workspaceTasks || []).length" class="empty-line">暂无执行任务</div>
              </div>
              <button class="btn full" type="button" @click="setSubTab('follow')" style="margin-top:10px">进入执行跟踪</button>
            </section>

            <section class="card side-flow-card">
              <div class="section-title">报告与舌诊链路</div>
              <div class="chain-list">
                <div v-for="report in activePatient.workspaceReports || []" :key="report.id" class="chain-row">
                  <div>
                    <b>{{ report.report_code || `报告 #${report.id}` }}</b>
                    <span>{{ reportDbStatusLabel(report.status) }} · {{ report.risk_level || '未评估' }}</span>
                  </div>
                  <button class="btn-link-lite" type="button" @click="viewReport(report.id)">查看</button>
                </div>
                <div v-if="!(activePatient.workspaceReports || []).length" class="empty-line">暂无健康报告</div>
                <div class="integration-note">
                  舌诊流程：B端生成 H5 单点登录链接 → 患者手机采集 → 结果回流到档案和报告。
                </div>
              </div>
            </section>
          </aside>
        </div>
      </div>

      <!-- followup-plan tab：随访任务下发 -->
      <div v-else-if="subTab === 'followup-plan'" class="plan-page">
        <div class="plan-workbench">
          <!-- 左：患者选择 -->
          <section class="card plan-task-list">
            <div class="card-head one-line">
              <div class="card-title">
                选择患者
                <span class="muted" style="font-size:12px;font-weight:700">· {{ filteredPlanPatients.length }} 人</span>
              </div>
            </div>
            <div class="pad pad-lg" style="padding-bottom:0">
              <div class="left-search-row">
                <input class="pf-in" v-model="taskFilters.q" placeholder="搜索患者姓名/手机号" />
                <button class="btn-link-lite" type="button" @click="resetTaskFilters">重置</button>
              </div>
            </div>
            <div class="pat-table">
              <div class="pat-rows">
                <div v-for="p in filteredPlanPatients" :key="p.id" class="pat-row plan-patient-card" :data-active="p.id===activePatientId">
                  <button type="button" class="pat-main" @click="activePatientId=p.id; createTaskForPatient(p)">
                    <div class="patient-card-top">
                      <div>
                        <div class="pat-name"><b>{{ p.name }}</b><span class="muted">（{{ p.gender }}·{{ p.age }}岁）</span></div>
                        <div class="muted" style="font-size:12px;margin-top:4px">{{ p.nodules }} · {{ p.phoneMasked }}</div>
                      </div>
                      <span class="pill mini" :data-tone="p.riskTone">{{ p.risk }}</span>
                    </div>
                  </button>
                </div>
                <div v-if="!filteredPlanPatients.length" class="muted" style="font-size:12px;padding:10px 12px">暂无匹配患者</div>
              </div>
            </div>
          </section>

          <!-- 中：下发操作 -->
          <section class="card plan-task-detail">
            <div class="card-head plan-editor-head">
              <div class="plan-detail-title">
                <div class="card-title">随访任务下发</div>
              </div>
              <div class="panel-tools">
                <button class="primary" type="button" @click="recommendForActive">推荐随访模板</button>
                <button class="btn-link-lite" type="button" @click="goFollowupWorkflow">随访知识库与模板</button>
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
                      <button class="btn-link-lite" type="button" @click="goFollowupWorkflow">维护模板</button>
                    </div>

                    <div class="template-choice-list">
                      <button
                        v-for="tpl in availableFollowupTemplates"
                        :key="tpl.id"
                        type="button"
                        class="template-choice"
                        :class="{ active: tpl.id === selectedFollowupTemplateId }"
                        @click="selectFollowupTemplate(tpl)"
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
                      <div v-if="!availableFollowupTemplates.length" class="muted" style="font-size:12px">暂无可用模板，请先到随访知识库与模板页面创建并启用模板。</div>
                    </div>

                  </section>

                  <section class="detail-card">
                    <div class="detail-title-row">
                      <div>
                        <div class="detail-title">任务节点预览</div>
                      </div>
                      <select class="stage-select" v-model="planDay" :disabled="planState.loading || !!planState.error">
                        <option v-for="d in planDayList" :key="d" :value="d">第 {{ d.replace('day','') }} 天</option>
                      </select>
                    </div>
                    <div class="node-preview-list">
                      <div v-for="node in activePlanNodePreviews" :key="node.key" class="node-preview-row">
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
                      <div v-if="!activePlanNodePreviews.length" class="muted" style="font-size:12px">当前模板暂无任务节点，请先维护模板节点。</div>
                    </div>

                    <div class="confirm-bar">
                      <div>
                        <b>{{ selectedWorkflowTemplate?.name || '未选择模板' }}</b>
                      </div>
                      <div class="confirm-actions">
                        <button class="btn-link-lite" type="button" @click="savePlanForActiveAndBackend" :disabled="followupPlanSaving || !selectedWorkflowTemplate">
                          {{ followupPlanSaving ? '保存中...' : '保存设置' }}
                        </button>
                        <button class="primary" type="button" @click="simulatePlanToFollowup" :disabled="followupPlanSaving || !selectedWorkflowTemplate">确认下发</button>
                      </div>
                    </div>
                  </section>

                </div>

              </template>
            </div>
          </section>
        </div>
      </div>

      <!-- follow tab：患者随访聊天记录查看（三栏：患者列表 | 手机聊天 | 助手面板） -->
      <div v-else-if="subTab === 'follow'" class="follow-workbench">

        <!-- 顶部统计区 -->
        <div class="follow-stats-bar">
          <div class="follow-stat-item">
            <div class="follow-stat-label">任务执行中</div>
            <div class="follow-stat-value" style="color:#2563eb">{{ queue.filter(p=>statusKey(p)==='follow').length }}</div>
          </div>
          <div class="follow-stat-div"></div>
          <div class="follow-stat-item">
            <div class="follow-stat-label">高风险</div>
            <div class="follow-stat-value" style="color:#dc2626">{{ queue.filter(p=>statusKey(p)==='follow'&&p.riskTone==='r').length }}</div>
          </div>
          <div class="follow-stat-div"></div>
          <div class="follow-stat-item">
            <div class="follow-stat-label">中风险</div>
            <div class="follow-stat-value" style="color:#d97706">{{ queue.filter(p=>statusKey(p)==='follow'&&p.riskTone==='o').length }}</div>
          </div>
          <div class="follow-stat-div"></div>
          <div class="follow-stat-item">
            <div class="follow-stat-label">低风险</div>
            <div class="follow-stat-value" style="color:#059669">{{ queue.filter(p=>statusKey(p)==='follow'&&p.riskTone==='g').length }}</div>
          </div>
          <div class="follow-stat-div"></div>
          <div class="follow-stat-item">
            <div class="follow-stat-label">今日待配置</div>
            <div class="follow-stat-value" style="color:#7c3aed">{{ queue.filter(p=>statusKey(p)==='follow'&&(!p.planTask||!p.planTask.day)).length }}</div>
          </div>
          <div class="follow-stat-div"></div>
          <div class="follow-stat-item">
            <div class="follow-stat-label">已配置随访</div>
            <div class="follow-stat-value" style="color:#0891b2">{{ queue.filter(p=>statusKey(p)==='follow'&&p.planTask&&p.planTask.day).length }}</div>
          </div>
          <div class="follow-stat-div"></div>
          <div class="follow-stat-item">
            <div class="follow-stat-label">当前筛选</div>
            <div class="follow-stat-value" style="color:#475569">{{ followFilteredQueue.length }}</div>
          </div>
        </div>

        <section class="follow-compose-head card">
          <div>
            <div class="chain-eyebrow">AI 随访内容生成与预览</div>
            <div class="chain-title">随访内容由 AI 助手策略与知识库内容共同生成，支持可解释推荐、模块替换与预览下发。</div>
          </div>
          <div class="follow-flow">
            <div v-for="s in aiFollowFlowSteps" :key="s.title" class="follow-flow-step">
              <div class="follow-flow-ico">{{ s.icon }}</div>
              <div class="follow-flow-title">{{ s.title }}</div>
              <div class="follow-flow-sub">{{ s.sub }}</div>
            </div>
          </div>
        </section>

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

        <!-- 中：患者聊天记录 -->
        <section class="tracking-list-col">
          <div class="tracking-head">
            <div>
              <div class="card-title">患者聊天记录</div>
              <div class="tracking-patient">企业微信 · {{ followPatient?.name || '未选择患者' }}</div>
            </div>
          </div>
          <div class="tracking-chat-card as-main">
            <div class="mini-phone">
              <div class="mini-phone-head">
                <span class="mini-back">‹</span>
                <div>
                  <b>企业微信</b>
                  <span>{{ followPatient?.name || '患者' }}</span>
                </div>
                <span class="mini-more">···</span>
              </div>
              <div class="mini-chat">
                <div class="mini-date">今天 {{ activeTrackingTask?.time || '09:00' }}</div>
                <div v-for="msg in activeTrackingMessages" :key="msg.key" class="mini-msg" :class="msg.direction">
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

        <!-- 右：任务执行表与详情 -->
        <section class="tracking-detail-col">
          <div class="tracking-head">
            <div>
              <div class="card-title">任务执行表</div>
              <div class="tracking-patient">{{ followPatient?.name || '未选择患者' }} · {{ followPatient?.nodules || '—' }}</div>
            </div>
            <button class="btn" type="button" @click="loadFollowupTasks">刷新</button>
          </div>

          <div class="tracking-summary">
            <div><b>{{ trackingStats.total }}</b><span>总任务</span></div>
            <div><b>{{ trackingStats.waiting }}</b><span>待发送</span></div>
            <div><b>{{ trackingStats.running }}</b><span>执行中</span></div>
            <div><b>{{ trackingStats.alert }}</b><span>异常</span></div>
          </div>

          <div class="tracking-task-list compact">
            <template v-for="group in trackingTaskGroups" :key="group.day">
              <div class="tracking-day-title">第 {{ group.day }} 天</div>
              <button
                v-for="task in group.tasks"
                :key="task.id"
                type="button"
                class="tracking-task-row"
                :class="{ active: activeTrackingTask?.id === task.id }"
                @click="selectTask(task.id)"
              >
                <div class="tracking-time">{{ task.time }}</div>
                <div class="tracking-main">
                  <b>{{ task.title }}</b>
                  <span>{{ task.messageBrief }}</span>
                </div>
                <span class="tracking-status" :data-status="task.status">{{ trackingStatusLabel(task.status) }}</span>
              </button>
            </template>
            <div v-if="!trackingTasksForPatient.length" class="tracking-empty">
              暂无已生成任务。请先在“随访任务下发”中确认下发。
            </div>
          </div>

          <template v-if="activeTrackingTask">
            <div class="tracking-detail-card">
              <div class="tracking-detail-head">
                <div>
                  <div class="card-title">{{ activeTrackingTask.title }}</div>
                  <div class="tracking-patient">第 {{ activeTrackingTask.dayNum }} 天 · {{ activeTrackingTask.time }} · {{ activeTrackingTask.channel }}</div>
                </div>
                <span class="tracking-status big" :data-status="activeTrackingTask.status">{{ trackingStatusLabel(activeTrackingTask.status) }}</span>
              </div>

              <div class="tracking-kv-grid">
                <div><span>计划发送</span><b>{{ activeTrackingTask.scheduledAt || '—' }}</b></div>
                <div><span>实际发送</span><b>{{ activeTrackingTask.sentAt || '未发送' }}</b></div>
                <div><span>患者动作</span><b>{{ activeTrackingTask.patientAction || '—' }}</b></div>
                <div><span>AI处理</span><b>{{ activeTrackingTask.aiAction || '—' }}</b></div>
              </div>

              <div class="tracking-block">
                <div class="tracking-block-title">执行过程</div>
                <div class="tracking-timeline">
                  <div v-for="event in activeTrackingEvents" :key="event.key" class="tracking-event">
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

        <!-- 旧手机聊天记录预览：已隐藏，保留代码便于后续对照迁移 -->
        <div class="follow-phone-col">
          <div class="phone-preview-label">
            <span>Day {{ planDay.replace('day','') }} 随访内容预览</span>
            <span class="muted" style="font-size:11px">发送节奏：上午 09:00 · 晚间提醒 20:00</span>
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
              <div class="card-title">A. AI助手策略中心</div>
              <span class="assist-state" :data-tone="assistantStatus(currentAssistant?.key)">
                {{ assistantStatus(currentAssistant?.key) === 'g' ? '当前策略已启用' : '待启用' }}
              </span>
            </div>
            <div class="assist-focus-body">
              <div class="strategy-box">
                <div class="strategy-modules">
                  <button
                    v-for="a in followAssistants.slice(0, 6)"
                    :key="a.key"
                    type="button"
                    class="strategy-module"
                    :class="{ active: activeAssistant === a.key }"
                    @click="activeAssistant = a.key"
                  >
                    <span class="assist-ico" :style="{ background: a.bg, color: a.color }">{{ a.ico }}</span>
                    <b>{{ a.shortName }}</b>
                    <em v-if="assistantStatus(a.key)==='g'">推荐</em>
                  </button>
                </div>
                <div class="strategy-current">当前生成策略：{{ currentAssistant?.shortName }} + {{ followPatient?.risk }} + Day {{ planDay.replace('day','') }} 随访阶段</div>
              </div>

              <div class="content-config">
                <div class="assist-selector-title">B. 知识库来源与内容配置</div>
                <div class="config-list">
                  <div v-for="row in followContentConfigRows" :key="row.key" class="config-row">
                    <span class="config-dot" :data-on="row.enabled"></span>
                    <div class="config-main">
                      <b>{{ row.label }}</b>
                      <span>{{ row.reason }}</span>
                    </div>
                    <button class="kb-act" type="button" @click="setKbEnabled(row.key, true)">{{ row.enabled ? '已加入' : '加入模块' }}</button>
                  </div>
                </div>
              </div>

              <div class="generated-panel">
                <div class="assist-selector-title">C. 今日随访内容明细 <span class="muted">（已生成 {{ followGeneratedRows.length }} 项）</span></div>
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
                  <div v-for="(row, idx) in followGeneratedRows" :key="row.key" class="generated-row">
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
      </div>

      <!-- review tab：报告处理主页面 -->
      <div v-else-if="subTab === 'review'" class="rp-page">

        <!-- 统计卡片 -->
        <div class="stat-cards" style="padding:12px 0 0">
          <div class="stat-card">
            <div class="stat-icon" style="background:#eff6ff;color:#2563eb">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">{{ reportTerms.pending }}</div>
              <div class="stat-val">{{ rpList.filter(r=>r.reportStatus!=='已审核').length }}</div>
              <div class="stat-sub" style="color:#2563eb">较昨日 -2</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#fdf4ff;color:#a21caf">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">{{ reportTerms.parsing }}</div>
              <div class="stat-val">{{ rpList.filter(r=>r.aiStatus==='AI解析中').length }}</div>
              <div class="stat-sub" style="color:#a21caf">较昨日 +1</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#ecfdf5;color:#059669">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">{{ reportTerms.parsed }}</div>
              <div class="stat-val">{{ rpList.filter(r=>r.aiStatus==='待审核').length }}</div>
              <div class="stat-sub" style="color:#059669">较昨日 +3</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#fffbeb;color:#d97706">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">{{ reportTerms.toGenerate }}</div>
              <div class="stat-val">{{ rpList.filter(r=>r.reportStatus==='待审核').length }}</div>
              <div class="stat-sub" style="color:#d97706">较昨日 +1</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#ecfdf5;color:#059669">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">{{ reportTerms.toReview }}</div>
              <div class="stat-val">{{ rpList.filter(r=>r.reportStatus==='待审核').length }}</div>
              <div class="stat-sub" style="color:#059669">较昨日 -1</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon" style="background:#fff1f2;color:#dc2626">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </div>
            <div class="stat-body">
              <div class="stat-label">{{ reportTerms.abnormal }}</div>
              <div class="stat-val">{{ rpList.filter(r=>r.risk==='高风险').length }}</div>
              <div class="stat-sub" style="color:#dc2626">较昨日 +1</div>
            </div>
          </div>
        </div>

        <!-- 筛选栏 -->
        <div class="rp-filter-bar card">
          <div class="rp-filter-row">
            <div class="rp-filter-item">
              <div class="rp-filter-label">{{ scenario.personLabel }}姓名/手机号</div>
              <input class="rp-filter-input" v-model="rpSearch" placeholder="请输入姓名或手机号" />
            </div>
            <div class="rp-filter-item">
              <div class="rp-filter-label">{{ scenario.personLabel }}来源</div>
              <select class="rp-filter-select" v-model="rpSource">
                <option value="">{{ scenario.sourceOptions.join(' / ') }}</option>
                <option v-for="src in scenario.sourceOptions" :key="src">{{ src }}</option>
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
              <div class="card-title">{{ reportTerms.listTitle }} <span class="rp-count">共 268 条</span></div>
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
                      <div class="rp-row-actions">
                        <button class="tbl-act" type="button" @click.stop="viewReport(r.id)">查看</button>
                        <button class="tbl-act" type="button" @click.stop="openReportRowPrimary(r)" :disabled="reportGeneratingIds.has(r.rawPatientId || r.id)">{{ reportGeneratingIds.has(r.rawPatientId || r.id) ? '生成中...' : (r.isReportPlaceholder ? '去生成' : (r.reportStatus === '已审核' ? '复审/编辑' : reportTerms.reviewAction)) }}</button>
                        <button class="tbl-act" type="button" @click.stop="downloadReport(r.id)">下载</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="pager">
              <span class="muted">共 {{ rpFilteredList.length }} 条</span>
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
                <div class="card-head"><div class="card-title">{{ reportTerms.detailTitle }}</div></div>
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
                <div class="card-head"><div class="card-title">{{ reportTerms.flowTitle }}</div></div>
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
                  <button class="primary" type="button" @click="openReportRowPrimary(rpActive)">
                    {{ rpActive.isReportPlaceholder ? '去生成报告' : (rpActive.reportStatus === '已审核' ? '复审/编辑报告' : reportTerms.auditAi) }}
                  </button>
                  <button class="btn" type="button" @click="viewReport(rpActive.id)">查看报告</button>
                  <button class="btn" type="button" @click="downloadReport(rpActive.id)">下载报告</button>
                  <button class="btn" type="button">{{ reportTerms.createTask }}</button>
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
                        <button class="icon-more" type="button" @click="toast?.show('文件操作')">⋯</button>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="empty">
                    <div class="empty-title">暂无原始报告</div>
                    <div class="muted" style="font-size:12px;margin-top:4px">上传检查报告后，AI 将自动解析并生成{{ scenario.reportLabel }}</div>
                    <div class="empty-actions">
                      <button class="primary" type="button">上传报告</button>
                      <button class="btn" type="button">{{ scenario.importLabel }}</button>
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
        <div class="rp-modal-title">{{ scenario.reportLabel }}</div>
        <button class="rp-modal-close" type="button" @click="rpViewVisible=false">✕</button>
      </div>
      <div class="rp-modal-body" v-html="rpViewHtml"></div>
    </div>
  </div>

  <!-- 审核AI建议弹窗 -->
  <div v-if="rpAuditId" class="rp-modal-mask" @click.self="rpAuditId=''">
    <div class="rp-modal">
      <div class="rp-modal-head">
        <div class="rp-modal-title">{{ reportTerms.auditModalTitle }}</div>
        <span class="muted" style="font-size:12px">可直接编辑后点击审核通过</span>
        <button class="rp-modal-close" type="button" @click="rpAuditId=''">✕</button>
      </div>
      <div class="rp-modal-body">
        <div v-if="rpAuditStatus" class="rp-audit-state">
          <span class="status-tag" :data-s="rpAuditStatus">{{ adviceStatusLabel(rpAuditStatus) }}</span>
          <span class="muted">当前版本：V{{ rpAuditVersion || 1 }} · 已审核报告也可重新编辑并再次写入最终报告</span>
        </div>
        <div class="rp-audit-grid">
          <div class="rp-audit-block">
            <div class="rp-audit-label">影像报告建议</div>
            <textarea class="rp-audit-ta" v-model="rpAuditImagingAdvice" rows="5"></textarea>
          </div>
          <div class="rp-audit-block">
            <div class="rp-audit-label">总体评估建议</div>
            <textarea class="rp-audit-ta" v-model="rpAuditOverallAdvice" rows="5"></textarea>
          </div>
          <div class="rp-audit-block">
            <div class="rp-audit-label">风险评估建议</div>
            <textarea class="rp-audit-ta" v-model="rpAuditRiskAdvice" rows="5"></textarea>
          </div>
          <div class="rp-audit-block">
            <div class="rp-audit-label">中医舌诊插入内容</div>
            <textarea class="rp-audit-ta" v-model="rpAuditTongueAdvice" rows="5" placeholder="舌诊完成后会从健康档案带入，也可以在这里编辑后写入最终报告。"></textarea>
          </div>
        </div>
        <div style="display:flex;gap:8px;margin-top:16px">
          <button class="primary" type="button" @click="finalizeReport(rpAuditId)" :disabled="rpFinalizing">{{ rpFinalizing ? '处理中...' : (rpAuditWasReviewed ? '重新审核通过' : reportTerms.approveAction) }}</button>
          <button class="btn" type="button" @click="rpAuditId=''">取消</button>
        </div>
      </div>
    </div>
  </div>

  <!-- 企业微信身份绑定 -->
  <div v-if="wecomModalOpen" class="rp-modal-mask" @click.self="wecomModalOpen=false">
    <div class="rp-modal wecom-modal">
      <div class="rp-modal-head">
        <div>
          <div class="rp-modal-title">绑定企业微信身份</div>
          <div class="muted" style="font-size:12px;margin-top:3px">{{ wecomBindingPatient?.name || '当前患者' }}</div>
        </div>
        <button class="rp-modal-close" type="button" @click="wecomModalOpen=false">✕</button>
      </div>
      <div class="rp-modal-body">
        <div class="wecom-form-grid">
          <label class="profile-field wide">
            <span>external_userid</span>
            <input v-model.trim="wecomForm.external_userid" placeholder="企业微信客户 external_userid">
          </label>
          <label class="profile-field wide">
            <span>userid</span>
            <input v-model.trim="wecomForm.userid" placeholder="内部员工 userid，可选">
          </label>
        </div>
        <div class="wecom-form-hint">真实企微回调拿到 external_userid 后，会用这个字段把消息、图片和打卡记录归属到患者。</div>
        <div class="wecom-modal-actions">
          <button class="btn" type="button" @click="wecomModalOpen=false">取消</button>
          <button class="primary" type="button" @click="submitWecomBind" :disabled="wecomBindingSaving">{{ wecomBindingSaving ? '保存中...' : '保存绑定' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import RecordView from './RecordView.vue'
import { getStoredScenario } from '../config/scenarios'

const router = useRouter()
const route = useRoute()
const toast = { show: (msg) => window.alert(msg) }
const scenario = computed(() => getStoredScenario())
const isCheckupScenario = computed(() => scenario.value.key === 'checkup')
function goFollowupWorkflow() {
  router.push('/followup-workflow')
}

const reportTerms = computed(() => {
  if (isCheckupScenario.value) {
    return {
      pending: '待处理体检报告',
      parsing: 'AI结构化中',
      parsed: '解读完成',
      toGenerate: '待生成解读',
      toReview: '待总检确认',
      abnormal: '高风险提醒',
      listTitle: '体检报告列表',
      detailTitle: '体检报告详情',
      flowTitle: '体检报告流程',
      reviewed: '已确认',
      reviewAction: '确认',
      auditAi: '确认AI建议',
      createTask: '创建复查任务',
      auditModalTitle: '确认AI解读内容',
      summaryLabel: '体检结果摘要',
      adviceLabel: 'AI复查建议',
      approveAction: '确认通过',
      flowBuild: '建档',
      flowGenerate: '生成解读',
      flowReview: '总检确认',
      flowPush: '推送患者',
    }
  }
  return {
    pending: '待处理报告',
    parsing: 'AI解析中',
    parsed: '解析完成',
    toGenerate: '待生成报告',
    toReview: '待医生复核',
    abnormal: '异常报告',
    listTitle: '报告列表',
    detailTitle: '报告详情',
    flowTitle: '处理流程',
    reviewed: '已审核',
    reviewAction: '审核',
    auditAi: '审核AI建议',
    createTask: '创建任务',
    auditModalTitle: '审核AI生成内容',
    summaryLabel: '影像解读摘要',
    adviceLabel: 'AI健康建议',
    approveAction: '审核通过',
    flowBuild: '建档',
    flowGenerate: '生成报告',
    flowReview: '人工审核',
    flowPush: '推送患者',
  }
})

// 当前子页（必须在 watch 之前声明，避免 immediate 回调引用未初始化变量）
const subTab = ref('queue')

// 子页定义（URL query.tab -> subTab）
const subTabs = [
  { key: 'queue', label: '患者队列' },
  { key: 'detail', label: '患者详情' },
  { key: 'record', label: '档案与报告' },
  { key: 'review', label: isCheckupScenario.value ? '体检报告确认' : '健康报告审核' },
  { key: 'followup-plan', label: '随访任务下发' },
  { key: 'follow', label: '执行跟踪' }
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
const recordPatient = ref(null)
const followPatientId = ref('p1')
const followSearch = ref('')
const followRiskFilter = ref('')
const followStageFilter = ref('')
const showAllTimeline = ref(false)
const reviewReject = ref(false)
const patientEditMode = ref(false)
const adviceGenerating = ref(false)
const tongueSubmitting = ref(false)
const tongueSyncing = ref(false)
const reportGeneratingIds = ref(new Set())
const imagingInputRef = ref(null)
const activeAssistant = ref('hlp')
const assistPlanZoneRef = ref(null)
const wecomModalOpen = ref(false)
const wecomBindingPatientId = ref('')
const wecomBindingSaving = ref(false)
const wecomForm = reactive({
  external_userid: '',
  userid: '',
})

const planState = ref({
  loading: true,
  error: '',
  title: '',
  sourceFile: '',
  days: {}
})
const planDay = ref('day1')
const followupTemplates = ref([])
const followupRecommendation = ref(null)
const selectedFollowupTemplateId = ref(null)
const followupPlanSaving = ref(false)
const followupKnowledgeItems = ref([])

// 患者队列（必须提前声明，避免 watcher immediate 引用 TDZ）
const queue = ref([])

// 健康管理任务工作台（筛选 + 列表 + 详情）
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

const latestRecordLabel = computed(() => {
  const records = activePatient.value?.workspaceRecords || []
  const latest = records[0]
  if (!latest) return '暂无档案'
  return latest.record_code || latest.created_at || `档案 #${latest.id}`
})

const activePlanLabel = computed(() => {
  const plans = activePatient.value?.workspacePlans || []
  const active = plans.find((plan) => plan.status === 'active') || plans[0]
  if (!active) return '待下发'
  return `${planStatusLabel(active.status)} · ${cycleLabelFromDays(active.cycle_days)}`
})

const taskExecutionSummary = computed(() => {
  const tasks = activePatient.value?.workspaceTasks || []
  if (!tasks.length) return '暂无任务'
  const open = tasks.filter((task) => !['completed', 'cancelled'].includes(task.status)).length
  const alert = tasks.filter((task) => task.abnormal_flag || task.status === 'alert').length
  if (alert) return `${alert} 个异常待处理`
  return open ? `${open} 个进行中` : '全部完成'
})

const MOCK_TRACKING_NODES = [
  {
    name: '早餐打卡',
    send_time: '07:00',
    task_type: 'diet_checkin',
    patient_action: 'upload_image',
    ai_action: 'diet_review',
    message_template: '早上好，请上传今天早餐图片。系统会从主食、蛋白质、蔬菜和油脂搭配角度给出饮食建议。',
  },
  {
    name: '午餐打卡',
    send_time: '11:00',
    task_type: 'diet_checkin',
    patient_action: 'upload_image',
    ai_action: 'diet_review',
    message_template: '午餐前后请上传餐食图片，便于记录今天的饮食结构，并获得下一餐调整建议。',
  },
  {
    name: '知识推送',
    send_time: '12:30',
    task_type: 'knowledge_push',
    patient_action: 'read',
    ai_action: 'send_message',
    message_template: '今天的健康知识：甲状腺结节和肺结节管理重点是规律复查、稳定作息、减少焦虑，并持续记录身体变化。',
  },
  {
    name: '晚餐打卡',
    send_time: '17:30',
    task_type: 'diet_checkin',
    patient_action: 'upload_image',
    ai_action: 'diet_review',
    message_template: '请上传今天晚餐图片。建议晚餐清淡、不过量，注意优质蛋白和蔬菜搭配。',
  },
  {
    name: '运动提醒',
    send_time: '19:00',
    task_type: 'exercise_reminder',
    patient_action: 'reply_text',
    ai_action: 'none',
    message_template: '今天建议完成20-30分钟低到中等强度活动，如散步、拉伸或八段锦。量力而行，贵在坚持。',
  },
  {
    name: '心理提醒',
    send_time: '20:00',
    task_type: 'psych_reminder',
    patient_action: 'reply_text',
    ai_action: 'reply',
    message_template: '睡前可以做3分钟呼吸放松，记录今天的压力和睡眠准备情况。若持续焦虑或失眠，可以回复说明。',
  },
]

function previewTasksFromPatient(p) {
  if (!p) return []
  const nodes = (p.planTask?.nodes || []).length ? p.planTask.nodes : MOCK_TRACKING_NODES
  const day = p.planTask?.day || planDay.value || 'day1'
  return nodes.slice(0, 6).map((node, idx) => {
    const message = node.message_template || '请按计划完成今日健康管理任务。'
    return {
      id: `preview-${p.id}-${String(day).replace('day', '')}-${idx}`,
      patientId: p.id,
      patientName: p.name,
      gender: p.gender,
      age: p.age,
      phoneMasked: p.phoneMasked,
      nodules: p.nodules,
      risk: p.risk,
      riskTone: p.riskTone,
      owner: p.owner || '',
      channel: p.planTask?.channel || '企微',
      cycle: p.planTask?.cycle || '90天',
      reminder: p.planTask?.reminder || '',
      day,
      time: node.send_time || '09:00',
      scheduledAt: '模拟排程',
      status: idx === 0 ? 'scheduled' : 'pending',
      node,
      message,
      patientAction: patientActionLabel(node.patient_action),
      aiAction: aiActionLabel(node.ai_action),
      logs: [{ at: '模拟', by: '系统', action: 'task_created_from_patient_plan', note: '模拟展示：真实企微接入后会写入实际发送与回调记录。' }],
    }
  })
}

const trackingTasksForPatient = computed(() => {
  const p = followPatient.value
  if (!p) return []
  const tasks = (followTasks.value || []).filter((t) => String(t.patientId) === String(p.id))
  if (!tasks.length) return previewTasksFromPatient(p)
  if (tasks.length === 1 && !tasks[0].node?.message_template && !tasks[0].message) return previewTasksFromPatient(p)
  return tasks
})

const activeTrackingTask = computed(() => {
  const current = trackingTasksForPatient.value.find((t) => t.id === activeTaskId.value) || trackingTasksForPatient.value[0] || null
  if (!current) return null
  const node = current.node || current.taskPayload?.node || {}
  const message = current.message || node.message_template || ''
  return {
    ...current,
    dayNum: Number(String(current.day || 'day1').replace('day', '')) || 1,
    time: current.time || current.scheduledAt?.slice(11, 16) || node.send_time || '09:00',
    title: current.title || node.name || '健康管理任务',
    message,
    messageBrief: current.messageBrief || String(message || '暂无推送内容').replace(/\s+/g, ' ').slice(0, 48),
    patientAction: current.patientAction || patientActionLabel(node.patient_action),
    aiAction: current.aiAction || aiActionLabel(node.ai_action),
  }
})

const trackingTaskGroups = computed(() => {
  const groups = new Map()
  trackingTasksForPatient.value.forEach((task) => {
    const day = Number(String(task.day || 'day1').replace('day', '')) || 1
    if (!groups.has(day)) groups.set(day, [])
    const node = task.node || task.taskPayload?.node || {}
    const message = task.message || node.message_template || ''
    groups.get(day).push({
      ...task,
      dayNum: day,
      time: task.time || task.scheduledAt?.slice(11, 16) || node.send_time || '09:00',
      messageBrief: String(message || '暂无推送内容').replace(/\s+/g, ' ').slice(0, 48),
    })
  })
  return Array.from(groups.entries())
    .sort((a, b) => a[0] - b[0])
    .slice(0, 7)
    .map(([day, tasks]) => ({
      day,
      tasks: tasks.sort((a, b) => String(a.time).localeCompare(String(b.time))),
    }))
})

const trackingStats = computed(() => {
  const list = trackingTasksForPatient.value
  return {
    total: list.length,
    waiting: list.filter((t) => ['draft', 'assigned', 'scheduled', 'pending'].includes(t.status)).length,
    running: list.filter((t) => ['sent', 'replied', 'executing', 'review'].includes(t.status)).length,
    alert: list.filter((t) => ['alert', 'manual_processing', 'failed'].includes(t.status)).length,
  }
})

const activeTrackingEvents = computed(() => {
  const t = activeTrackingTask.value
  if (!t) return []
  const logs = Array.isArray(t.logs) ? t.logs : []
  const base = logs.map((log, idx) => ({
    key: `log-${idx}`,
    title: trackingEventTitle(log.action),
    time: log.at || '现在',
    note: log.note || '任务状态已更新',
  }))
  if (!base.length) {
    base.push({
      key: 'created',
      title: '任务已创建',
      time: t.createdAt || '现在',
      note: '系统已根据随访模板生成该任务，等待到达计划发送时间。',
    })
  }
  if (['sent', 'replied', 'done', 'completed'].includes(t.status)) {
    base.push({ key: 'sent', title: '消息已发送', time: t.sentAt || '模拟时间', note: '企业微信发送结果会在接入真实接口后写入这里。' })
  }
  return base
})

const activeTrackingMessages = computed(() => {
  const t = activeTrackingTask.value
  if (!t) return []
  const messages = Array.isArray(t.messages) ? t.messages : []
  if (messages.length) {
    return messages.map((msg, idx) => ({
      key: `msg-${idx}`,
      direction: msg.direction === 'inbound' ? 'inbound' : 'outbound',
      sender: msg.direction === 'inbound' ? '患者' : '健康管理师',
      type: msg.content_type || 'text',
      content: msg.content || '',
    }))
  }
  const needsImage = String(t.patientAction || '').includes('上传餐饮图片')
  const needsAiReview = String(t.aiAction || '').includes('饮食点评')
  return [
    { key: 'preview-1', direction: 'outbound', sender: '健康管理师', type: 'text', content: t.message || '暂无推送内容' },
    ...(needsImage ? [{ key: 'preview-2', direction: 'inbound', sender: '患者', type: 'image', content: '患者上传后显示真实图片' }] : []),
    ...(needsAiReview ? [{ key: 'preview-3', direction: 'outbound', sender: 'AI饮食点评', type: 'text', content: '图片识别完成后，这里会显示AI饮食点评和下一餐建议。' }] : []),
    ...(!needsImage && ['replied', 'done', 'completed'].includes(t.status) ? [{ key: 'preview-4', direction: 'inbound', sender: '患者', type: 'text', content: '患者回复内容会显示在这里。' }] : []),
  ]
})

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
    // 左侧固定展示患者列表，不再切换到任务视图
    void n
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
      .flatMap((p) => previewTasksFromPatient(p))
    followTasks.value = seeded
    if (seeded[0]) selectTask(seeded[0].id)
  },
  { immediate: true }
)

watch(
  () => subTab.value,
  (k) => {
    if (k !== 'follow') return
    loadFollowupTasks()
  },
  { immediate: true }
)

/**
 * @isdoc
 * @description 加载健康管理任务内容（从 public/plans 读取 JSON）
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

async function loadFollowupPlanningConfig() {
  try {
    const templates = await apiJson('/api/b/followup/templates?status=active&include_nodes=1')
    followupTemplates.value = Array.isArray(templates) ? templates : []
    if (!selectedFollowupTemplateId.value && followupTemplates.value[0]?.id) selectedFollowupTemplateId.value = followupTemplates.value[0].id
    const knowledge = await apiJson('/api/b/followup/knowledge?per_page=100')
    followupKnowledgeItems.value = knowledge?.items || []
  } catch (e) {
    followupTemplates.value = []
    followupKnowledgeItems.value = []
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

function trackingStatusLabel(s) {
  const map = {
    draft: '待创建',
    assigned: '待发送',
    scheduled: '待发送',
    pending: '待发送',
    sent: '已发送',
    replied: '患者已回复',
    executing: '执行中',
    review: '待复核',
    completed: '已完成',
    done: '已完成',
    alert: '异常待处理',
    manual_processing: '人工处理中',
    failed: '发送失败',
    cancelled: '已取消',
  }
  return map[s] || '待发送'
}

function trackingEventTitle(action) {
  const text = String(action || '')
  const map = {
    task_created_from_patient_plan: '任务已创建',
    message_sent: '消息已发送',
    message_failed: '发送失败',
    wecom_message_received: '收到患者消息',
    checkin_submitted: '患者已打卡',
    task_completed: '任务已完成',
  }
  return map[text] || text.replace(/_/g, ' ') || '任务状态更新'
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
  if (t?.patientId) {
    activePatientId.value = t.patientId
    followPatientId.value = t.patientId
  }
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
  const owner = window.prompt('输入负责人（例如：运营A/张医生）：', taskFilters.value.owner || '') || ''
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
  const planNode = (p.planTask?.nodes || [])[0] || {}
  const message = planNode.message_template || p.planTask?.note || '请按计划完成今日健康管理任务。'
  return {
    id,
    patientId: p.id,
    patientName: p.name,
    gender: p.gender,
    age: p.age,
    phoneMasked: p.phoneMasked,
    nodules: p.nodules,
    risk: p.risk,
    riskTone: p.riskTone,
    owner: p.owner || '',
    channel: draft.value.channel,
    cycle: draft.value.cycle,
    reminder: draft.value.reminder,
    day: planDay.value,
    time: planNode.send_time || '09:00',
    scheduledAt: '模拟排程',
    status: p.owner ? 'scheduled' : 'pending',
    node: planNode,
    message,
    patientAction: patientActionLabel(planNode.patient_action),
    aiAction: aiActionLabel(planNode.ai_action),
    kbSnapshot: JSON.parse(JSON.stringify(draft.value.kbEnabled || {})),
    logs: [{ at: '现在', by: '医生/运营', action: 'task_created_from_patient_plan', note: `Day ${planDay.value.replace('day', '')} · ${draft.value.channel} · ${draft.value.cycle}` }],
  }
}

/**
 * @isdoc
 * @description 新建任务入口（基于当前患者）
 * @returns {void}
 */
function openNewTaskFromActive() {
  // 已移除“新建任务”按钮入口：任务仅从患者行“任务下发”进入
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
  if (p._apiId) {
    ensureFollowupRecommendation(p).catch((e) => {
      toast?.show(e.message || '知识库推荐失败，已保留本地草稿')
    })
  }
  // 左侧固定展示患者列表
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
  loadFollowupPlanningConfig()
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
  editorCategory: 'script',
  editorTaskType: '',
  editorRiskLevel: '',
  managerOpen: false,
  drawerOpen: false,
  drawerGroup: 'diet',
  drawerQuery: '',
  drawerActiveKey: '',
})

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
      `您好，已为您更新 Day ${planDay.value.replace('day', '')} 健康管理任务。`,
      `请按“${draft.value.cycle}复查周期”执行，并完成饮食/运动/心理打卡。`,
      '如出现持续咳嗽、胸痛、咳血、明显吞咽困难等情况，请及时就医并联系医生。',
    ].join('\n')
    if (key === 'escalationRule') return [
      '异常转人工/医生规则：',
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
  // 也同步写入 plan（用于后续下发任务）
  savePlanForActive()
  p.timeline = Array.isArray(p.timeline) ? p.timeline : []
  p.timeline.push({ at: '现在', tone: 'b', text: `生成健康管理任务：Day ${planDay.value.replace('day','')}`, meta: '已保存' })

  // 同步生成/更新任务队列（工作台左侧列表）
  const newTask = makeTaskFromPatient(p)
  followTasks.value = [newTask, ...(followTasks.value || [])]
  selectTask(newTask.id)
}

async function ensureFollowupRecommendation(p) {
  const patient = p || activePatient.value
  if (!patient?._apiId) return null
  const rec = await apiPostJson('/api/b/followup/plans/recommend', {
    patient_id: patient._apiId,
    record_id: patient.workspaceRecordId || patient.latestRecordId || null,
    report_id: patient.latestReport?.id || patient.latestReportId || null,
    nodule_type: patient.noduleType,
    risk_level: patient.risk,
  })
  followupRecommendation.value = rec
  if (rec?.template?.id) selectedFollowupTemplateId.value = rec.template.id
  if (rec?.settings) {
    draft.value.cycle = cycleLabelFromDays(rec.settings.cycle_days)
    draft.value.channel = rec.settings.channel === 'wecom' ? '企微' : rec.settings.channel === 'phone' ? '电话' : rec.settings.channel === 'miniapp' ? '小程序' : draft.value.channel
    draft.value.reminder = rec.settings.reminder_strategy || draft.value.reminder
  }
  if (rec?.nodes?.length) {
    const firstNode = rec.nodes[0]
    if (firstNode?.day_offset) planDay.value = `day${firstNode.day_offset}`
    draft.value.kbCustom = rec.nodes.flatMap((node) => (node.matched_knowledge || []).map((item) => ({
      key: `api_${item.id}`,
      label: item.title,
      text: item.content,
      enabled: true,
    })))
  }
  return rec
}

async function recommendForActive() {
  const p = activePatient.value
  if (!p?._apiId) {
    toast?.show('演示患者已使用本地知识库推荐')
    return
  }
  try {
    await ensureFollowupRecommendation(p)
    toast?.show('已按患者画像匹配任务模板和知识库内容')
  } catch (e) {
    toast?.show(e.message || '任务模板推荐失败')
  }
}

async function saveBackendPatientPlan(p) {
  const patient = p || activePatient.value
  if (!patient?._apiId) return null
  followupPlanSaving.value = true
  try {
    const rec = followupRecommendation.value || await ensureFollowupRecommendation(patient)
    const template = selectedWorkflowTemplate.value || rec?.template || followupTemplates.value[0] || null
    const templateId = template?.id
    const nodes = template?.nodes || rec?.nodes || []
    const selectedKnowledgeIds = [
      ...(rec?.knowledge || []).map(item => item.id),
      ...(nodes || []).flatMap(node => node.knowledge_item_ids || [])
    ].filter(Boolean)
    const plan = await apiPostJson('/api/b/followup/patient-plans', {
      patient_id: patient._apiId,
      record_id: rec?.record_id || patient.workspaceRecordId || null,
      report_id: rec?.report_id || patient.latestReport?.id || null,
      template_id: templateId,
      name: `${patient.name}健康管理任务计划`,
      nodule_type: patient.noduleType,
      risk_level: patient.risk,
      settings: {
        cycle_days: template?.cycle_days || cycleDaysFromLabel(draft.value.cycle),
        channel: template?.default_channel || channelToBackend(draft.value.channel),
        reminder_strategy: template?.default_reminder_strategy || draft.value.reminder,
      },
      plan_content: {
        template,
        nodes,
      },
      selected_knowledge_ids: Array.from(new Set(selectedKnowledgeIds)),
    })
    patient._patientPlanId = plan.id
    patient.planTask = {
      ...(patient.planTask || {}),
      backendPlanId: plan.id,
      cycle: cycleLabelFromDays(template?.cycle_days),
      channel: channelLabel(template?.default_channel),
      reminder: template?.default_reminder_strategy || draft.value.reminder,
      day: planDay.value,
      kb: patient.planTask?.kb || {},
      note: draft.value.note,
    }
    toast?.show('任务计划已保存')
    return plan
  } finally {
    followupPlanSaving.value = false
  }
}

/**
 * @isdoc
 * @description 保存并激活任务计划，生成后续提醒/打卡任务
 * @returns {void}
 */
async function simulatePlanToFollowup() {
  const p = activePatient.value
  if (!p?.id) return
  if (p._apiId) {
    try {
      applySelectedTemplateToPatient()
      const plan = p._patientPlanId ? { id: p._patientPlanId } : await saveBackendPatientPlan(p)
      const activated = await apiPostJson(`/api/b/followup/patient-plans/${plan.id}/activate`, {})
      const apiTasks = (activated?.tasks || []).map(normalizeBackendTask)
      if (apiTasks.length) {
        followTasks.value = [...apiTasks, ...(followTasks.value || [])]
        selectTask(apiTasks[0].id)
      }
      p.stage = 'follow'
      p.stageLabel = '任务执行中'
      p.serviceStatus = '任务执行中'
      p.nextStep = '按计划执行任务'
      p.timeline = Array.isArray(p.timeline) ? p.timeline : []
      p.timeline.push({ at: '现在', tone: 'g', text: '已下发健康管理任务', meta: `${apiTasks.length} 个任务` })
      followPatientId.value = p.id
      setSubTab('follow')
      toast?.show('任务已下发，已生成后续提醒/打卡任务')
      return
    } catch (e) {
      toast?.show(e.message || '随访任务下发失败')
      return
    }
  }
  applySelectedTemplateToPatient()
  const t = makeTaskFromPatient(p)
  followTasks.value = [t, ...(followTasks.value || [])]
  selectTask(t.id)
  p.stage = 'follow'
  p.stageLabel = '任务执行中'
  p.serviceStatus = '任务执行中'
  toast?.show('任务已下发')
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
    `您好，已为您更新 Day ${planDay.value.replace('day', '')} 健康管理任务。`,
    `请按“${draft.value.cycle}复查周期”执行，并完成饮食/运动/心理打卡。`,
    '如出现持续咳嗽、胸痛、咳血、明显吞咽困难等情况，请及时就医并联系医生。',
  ].join('\n')
  if (key === 'escalationRule') return [
    '异常转人工/医生规则：',
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
  const backend = (followupKnowledgeItems.value || []).map((x) => ({
    key: `api_${x.id}`,
    apiId: x.id,
    label: x.title,
    enabled: true,
    text: x.content,
    isCustom: true,
    category: x.category,
    taskType: x.task_type,
  }))
  return [...backend, ...base, ...custom]
})

const kbSelected = computed(() => kbItems.value.filter((x) => x.enabled))

const availableFollowupTemplates = computed(() => followupTemplates.value || [])

const selectedWorkflowTemplate = computed(() => {
  return availableFollowupTemplates.value.find((tpl) => tpl.id === selectedFollowupTemplateId.value) || availableFollowupTemplates.value[0] || null
})

function selectFollowupTemplate(tpl) {
  if (!tpl?.id) return
  selectedFollowupTemplateId.value = tpl.id
  if (tpl.nodes?.[0]?.day_offset) planDay.value = `day${tpl.nodes[0].day_offset}`
}

const planRecommendTags = computed(() => {
  const p = activePatient.value || {}
  const tpl = selectedWorkflowTemplate.value
  return [
    p.nodules || '结节随访',
    p.risk || '风险分层',
    tpl?.name || '待选择模板',
    cycleLabelFromDays(tpl?.cycle_days),
    `Day ${planDay.value.replace('day', '')}`,
    channelLabel(tpl?.default_channel),
  ].filter(Boolean)
})

const activePlanNodes = computed(() => {
  const nodes = selectedWorkflowTemplate.value?.nodes || followupRecommendation.value?.nodes || []
  return Array.isArray(nodes) ? nodes : []
})

const activePlanNodePreviews = computed(() => {
  const selectedDay = Number(String(planDay.value || 'day1').replace('day', '')) || 1
  return activePlanNodes.value.filter((node) => {
    return Number(node.day_offset || 1) === selectedDay
  }).map((node, idx) => ({
    key: node.node_code || node.id || idx,
    day: Number(node.day_offset || 1),
    time: node.send_time || '09:00',
    name: node.name || `随访任务 ${idx + 1}`,
    type: taskTypeLabel(node.task_type),
    patientAction: patientActionLabel(node.patient_action),
    aiAction: aiActionLabel(node.ai_action),
    message: node.message_template || node.content || node.description || '',
  }))
})

const planPipelineSteps = computed(() => {
  const hasTemplate = !!selectedWorkflowTemplate.value
  const hasPreview = activePlanNodes.value.length > 0
  const hasTask = !!activePatient.value?.planTask
  const isFollow = statusKey(activePatient.value) === 'follow'
  const currentStatus = statusKey(activePatient.value)
  const hasReviewed = ['plan', 'follow', 'push', 'abnormal'].includes(currentStatus) || !!activePatient.value?.finalReport?.content || !!activePatient.value?.latestReport
  return [
    { key: 'reviewed', icon: '1', title: '报告已审核', sub: hasReviewed ? '可下发任务' : '等待审核', state: hasReviewed ? 'done' : 'todo' },
    { key: 'recommend', icon: '2', title: '推荐模板', sub: selectedWorkflowTemplate.value?.name || '待推荐', state: hasTemplate ? 'done' : 'doing' },
    { key: 'preview', icon: '3', title: '预览任务', sub: hasPreview ? `${activePlanNodes.value.length} 个节点` : '待预览', state: hasPreview ? 'done' : 'todo' },
    { key: 'confirm', icon: '4', title: '确认下发', sub: hasTask ? '已保存' : '待确认', state: hasTask ? 'done' : 'doing' },
    { key: 'track', icon: '5', title: '执行跟踪', sub: isFollow ? '查看任务' : '待生成', state: isFollow ? 'done' : 'todo' },
  ]
})

const planDispatchSteps = computed(() => {
  return planPipelineSteps.value.slice(1, 5).map((step, idx) => ({
    ...step,
    icon: String(idx + 1),
  }))
})

const aiFollowFlowSteps = [
  { icon: '患', title: '患者画像', sub: '病种/风险/阶段' },
  { icon: '策', title: '助手策略', sub: '确定输出倾向' },
  { icon: '库', title: '知识匹配', sub: '匹配内容库' },
  { icon: '文', title: '生成内容', sub: '摘要/任务/提醒' },
  { icon: '发', title: '患者预览', sub: '预览后下发' },
]

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
  p.timeline.push({ at: '现在', tone: 'b', text: `更新任务计划：Day ${planDay.value.replace('day', '')}`, meta: '已保存' })
}

function applySelectedTemplateToPatient() {
  const p = activePatient.value
  const tpl = selectedWorkflowTemplate.value
  if (!p || !tpl) return
  const firstNode = (tpl.nodes || [])[0]
  if (firstNode?.day_offset) planDay.value = `day${firstNode.day_offset}`
  p.planTask = {
    ...(p.planTask || {}),
    title: tpl.name,
    day: planDay.value,
    cycle: cycleLabelFromDays(tpl.cycle_days),
    channel: channelLabel(tpl.default_channel),
    reminder: tpl.default_reminder_strategy,
    templateId: tpl.id,
    nodes: tpl.nodes || [],
  }
  savePlanForActive()
}

async function savePlanForActiveAndBackend() {
  const p = activePatient.value
  if (!p) return
  applySelectedTemplateToPatient()
  if (!p._apiId) {
    toast?.show('任务计划已保存')
    return
  }
  try {
    await saveBackendPatientPlan(p)
  } catch (e) {
    toast?.show(e.message || '保存下发设置失败')
  }
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
 * @description 下发任务：状态切换为 follow，并进入执行跟踪页
 * @returns {void}
 */
async function startAiFollowup() {
  const p = activePatient.value
  if (!p) return
  if (p._apiId) {
    await simulatePlanToFollowup()
    return
  }
  // 先保存一次，保证计划和内容包存在
  applySelectedTemplateToPatient()

  p.stage = 'follow'
  p.stageLabel = '任务执行中'
  p.serviceStatus = '任务执行中'
  p.nextStep = '按计划执行任务'

  p.timeline = Array.isArray(p.timeline) ? p.timeline : []
  p.timeline.push({ at: '现在', tone: 'g', text: '下发健康管理任务', meta: `Day ${planDay.value.replace('day', '')}` })

  // 在聊天里保留一条任务提示（兼容原型预览数据）
  p.chat = Array.isArray(p.chat) ? p.chat : []
  p.chat.push({ from: 'ai', text: `已下发健康管理任务（Day ${planDay.value.replace('day', '')}），将按任务模板推送提醒和打卡入口。` })
  p.chat.push({ type: 'card', ico: '🧾', title: `查看健康管理任务（Day ${planDay.value.replace('day', '')}）`, sub: '任务已生成 · 点击查看' })

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
    capabilities: ['任务模板下发', '复查提醒推送', '健康档案管理', '日常打卡', '健康报告解读'],
    workflow: ['档案建立', '随访任务下发', '定期提醒', '打卡收集', '报告更新'],
    stats: { reach: 124, read: 108, reply: 67, transfer: 2 },
    desc: '随访提醒、复查计划、健康档案管理',
    scene: '结节随访 · 复查提醒',
    tpl: '您好，您的健康管理任务已更新，请按时完成打卡和复查提醒。如有不适请及时联系我们。',
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

const followAssistants = computed(() => {
  if (!isCheckupScenario.value) return aiAssistants
  const overrides = {
    hlp: {
      name: 'AI总检医生助手', shortName: '总检解读', ico: '总',
      tagline: '体检结论解读 · 风险分层 · 复查建议，为患者提供清晰的检后管理指引',
      capabilities: ['体检结论解读', '风险分层说明', '复查建议生成', '转诊提醒判断', '专项筛查规划'],
      scene: '体检后解读 · 高风险路径规划',
      tpl: '您好，您的体检报告已完成解读，请查看重点异常项和复查安排。',
      chat: [
        { from: 'ai', text: '您好，我是AI总检医生助手，已根据您的体检结果整理重点异常项。' },
        { from: 'ai', text: '本次重点关注肺部结节与甲状腺结节，建议按风险等级完成复查或报告解读。' },
        { type: 'card', ico: '报', title: '查看体检解读报告', sub: '异常项汇总 · 复查建议 · 风险说明' },
        { from: 'patient', text: '我需要马上去医院吗？' },
        { from: 'ai', text: '当前建议先完成复查预约和总检确认，如出现持续咳嗽、胸痛等症状，请提前联系医生。' }
      ]
    },
    health: {
      name: 'AI健康管理师', shortName: '检后管理', ico: '管',
      tagline: '报告解读提醒 · 复查预约 · 健康档案，全程衔接体检后管理',
      capabilities: ['复查计划制定', '报告解读提醒', '健康档案管理', '症状自评问卷', '异常指标跟踪'],
      scene: '检后管理 · 复查提醒',
      tpl: '您好，您的体检后管理计划已更新，请按时完成报告解读和复查。',
      chat: [
        { from: 'ai', text: '您好，您的体检解读报告已生成，以下是今日需要完成的事项。' },
        { type: 'card', ico: '复', title: '复查预约提醒', sub: '3个月胸部CT · 6个月甲状腺超声' },
        { from: 'ai', text: '建议您先确认报告解读结果，并根据风险等级完成复查预约。' },
        { from: 'patient', text: '好的，我今天看一下。' },
        { from: 'ai', text: '已为您保留提醒入口，临近复查日期会再次通知。' }
      ]
    },
    pharma: {
      name: 'AI复查预约助手', shortName: '复查预约', ico: '约',
      tagline: '复查项目匹配 · 预约提醒 · 转诊建议，提升体检后闭环效率',
      capabilities: ['复查项目匹配', '预约时间提醒', '转诊科室建议', '检查注意事项', '到检状态跟踪'],
      scene: '复查预约 · 转诊衔接',
      tpl: '您好，您的复查项目已匹配，请选择合适时间完成预约。',
    },
    chronic: {
      name: 'AI异常指标管理师', shortName: '指标管理', ico: '指',
      tagline: '异常指标跟踪 · 慢病风险评估 · 干预建议，帮助患者理解体检异常',
      capabilities: ['异常指标解释', '慢病风险评估', '指标复测提醒', '生活方式建议', '趋势跟踪'],
      scene: '异常指标 · 趋势管理',
      tpl: '您好，本次体检有部分指标需要关注，已为您整理复测和干预建议。',
    },
    psych: {
      name: 'AI检后关怀助手', shortName: '检后关怀', ico: '关',
      tagline: '检后焦虑评估 · 报告疑问收集 · 人工转接，降低患者等待期焦虑',
      capabilities: ['焦虑情绪评估', '报告疑问收集', '解读预约提醒', '人工转接', '持续关怀'],
      scene: '检后关怀 · 报告疑问',
      tpl: '您好，如果您对体检结果有疑问，可以先告诉我，我会协助整理给健康管理师。',
    },
    rehab: {
      name: 'AI生活方式干预师', shortName: '生活干预', ico: '活',
      tagline: '饮食运动建议 · 体重管理 · 生活方式跟踪，承接体检后健康改善',
      capabilities: ['饮食建议', '运动计划', '体重管理', '睡眠建议', '习惯跟踪'],
      scene: '体检后改善 · 生活方式干预',
      tpl: '您好，根据您的体检结果，为您推荐本周生活方式改善建议。',
    },
  }
  return aiAssistants
    .filter((a) => ['hlp', 'health', 'pharma', 'chronic', 'psych', 'rehab'].includes(a.key))
    .map((a) => ({ ...a, ...(overrides[a.key] || {}) }))
})

const currentAssistant = computed(() => followAssistants.value.find(a => a.key === activeAssistant.value) || followAssistants.value[0])

const followPatient = computed(() => queue.value.find(p => p.id === followPatientId.value) || queue.value[0])

const followFilteredQueue = computed(() => {
  const taskPatientIds = new Set((followTasks.value || []).map((t) => String(t.patientId)))
  return queue.value.filter((p) => statusKey(p) === 'follow' || taskPatientIds.has(String(p.id))).filter(p => {
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

const followPatientPlanTask = computed(() => followPatient.value?.planTask || null)

const followContentConfigRows = computed(() => {
  const task = followPatientPlanTask.value
  const kb = task?.kb || {}
  if (isCheckupScenario.value) {
    return [
      { key: 'knowledgeCard', label: '体检报告解读卡', reason: kb.knowledgeCard ? '来自已保存任务' : '基于异常项与风险等级推荐', enabled: !!kb.knowledgeCard || !!draft.value.kbEnabled?.knowledgeCard },
      { key: 'sport', label: '生活方式干预建议', reason: kb.sport ? '来自方案组合' : '可作为检后改善模块加入', enabled: !!kb.sport || !!draft.value.kbEnabled?.sport },
      { key: 'questionnaire', label: '复查前症状自评', reason: kb.questionnaire ? '来自问卷库' : '用于判断是否需要提前就医', enabled: !!kb.questionnaire || !!draft.value.kbEnabled?.questionnaire },
      { key: 'reminderScript', label: '复查预约提醒', reason: kb.reminderScript ? '来自提醒话术模板' : '用于提升复查到检率', enabled: !!kb.reminderScript || !!draft.value.kbEnabled?.reminderScript },
    ]
  }
  return [
    { key: 'knowledgeCard', label: '低碘饮食指导', reason: kb.knowledgeCard ? '来自已保存任务' : '基于病种与阶段推荐', enabled: !!kb.knowledgeCard || !!draft.value.kbEnabled?.knowledgeCard },
    { key: 'sport', label: '术后/日常运动提醒', reason: kb.sport ? '来自方案组合' : '可作为生活方式模块加入', enabled: !!kb.sport || !!draft.value.kbEnabled?.sport },
    { key: 'questionnaire', label: '症状自评问卷', reason: kb.questionnaire ? '来自问卷库' : 'Day1 建议加入基线症状评估', enabled: !!kb.questionnaire || !!draft.value.kbEnabled?.questionnaire },
    { key: 'reminderScript', label: '晚间打卡提醒', reason: kb.reminderScript ? '来自提醒话术模板' : '用于提升依从性', enabled: !!kb.reminderScript || !!draft.value.kbEnabled?.reminderScript },
  ]
})

const followGeneratedRows = computed(() => {
  const task = followPatientPlanTask.value
  const kb = task?.kb || {}
  const rows = isCheckupScenario.value
    ? [
      { key: 'summary', name: '体检摘要消息', type: '摘要卡', source: '系统生成', assistant: currentAssistant.value?.shortName || '总检解读', enabled: true },
      { key: 'knowledgeCard', name: 'Day1解读卡：体检异常项说明', type: '解读卡', source: kb.knowledgeCard ? '体检中心标准版 v2.1' : '体检知识库', assistant: '总检解读', enabled: !!kb.knowledgeCard || !!draft.value.kbEnabled?.knowledgeCard },
      { key: 'questionnaire', name: '复查前症状自评', type: '任务卡', source: '问卷库 v2.0', assistant: '检后管理', enabled: !!kb.questionnaire || !!draft.value.kbEnabled?.questionnaire },
      { key: 'reminderScript', name: '复查预约提醒', type: '提醒卡', source: '体检中心模板', assistant: '复查预约', enabled: !!kb.reminderScript || !!draft.value.kbEnabled?.reminderScript },
    ]
    : [
      { key: 'summary', name: '摘要消息', type: '摘要卡', source: '系统生成', assistant: currentAssistant.value?.shortName || '名医分身', enabled: true },
      { key: 'knowledgeCard', name: 'Day1知识卡：低碘饮食指导', type: '知识卡', source: kb.knowledgeCard ? '院内标准版 v2.1' : '院内指南', assistant: '名医分身', enabled: !!kb.knowledgeCard || !!draft.value.kbEnabled?.knowledgeCard },
      { key: 'questionnaire', name: '症状自评问卷', type: '任务卡', source: '问卷库 v2.0', assistant: '健康管理师', enabled: !!kb.questionnaire || !!draft.value.kbEnabled?.questionnaire },
      { key: 'reminderScript', name: '晚间打卡提醒', type: '提醒卡', source: '系统模板', assistant: '健康管理师', enabled: !!kb.reminderScript || !!draft.value.kbEnabled?.reminderScript },
    ]
  return rows.filter((x) => x.enabled)
})

const simulatedAssistantChat = computed(() => {
  const a = currentAssistant.value
  const plan = activeAssistantPlan.value
  const task = followPatientPlanTask.value
  const dayNum = String(task?.day || planDay.value).replace('day', '')
  const patientName = followPatient.value?.name || '您'
  const assistantName = a?.name || 'AI助手'

  if (task?.kb) {
    const kb = task.kb || {}
    const firstText = String(kb.knowledgeCard || kb.reminderScript || kb.sport || kb.psych || '').split('\n').map((x) => x.trim()).filter(Boolean)[0]
    return [
      { from: 'ai', text: `您好，${patientName}。我是${assistantName}，已根据您的任务计划生成 Day ${dayNum} 内容。` },
      ...(firstText ? [{ from: 'ai', text: `摘要：${firstText}` }] : []),
      { type: 'card', ico: '任', title: `Day ${dayNum} 健康管理任务`, sub: `${task.channel || draft.value.channel} · ${task.cycle || draft.value.cycle} · 已配置内容包` },
      { type: 'card', ico: '问', title: '症状自评与打卡', sub: kb.questionnaire ? '问卷已加入 · 点击填写' : '饮食/运动/心理打卡入口' },
      { from: 'ai', text: kb.reminderScript ? String(kb.reminderScript).split('\n')[0] : '请按计划完成今日打卡，如有明显不适请及时联系医生。' },
    ]
  }

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
    { from: 'ai', text: `您好，${patientName}。我是${assistantName}，已为您生成 Day ${dayNum} 的任务内容摘要。` },
    ...(firstText ? [{ from: 'ai', text: `摘要：${firstText}` }] : []),
    { type: 'card', ico: '🧾', title: `查看并填写健康管理任务（Day ${dayNum}）`, sub: `${plan.name} · 点击在右侧完成下发` },
    { from: 'ai', text: '提示：内容较长已折叠，请在右侧表单中选择知识库条目并保存。' },
  ]
})

watch(
  () => followPatientId.value,
  () => {
    const d = followPatient.value?.planTask?.day
    if (typeof d === 'string' && d.startsWith('day')) planDay.value = d
    const firstTask = trackingTasksForPatient.value[0]
    if (firstTask && !trackingTasksForPatient.value.some((t) => t.id === activeTaskId.value)) {
      activeTaskId.value = firstTask.id
    }
  }
)

const rpSearch = ref('')
const rpSource = ref('')
const rpNodule = ref('')
const rpRisk = ref('')
const rpActiveId = ref(1)

const rpList = ref([])
const rpLoading = ref(false)
const rpLoaded = ref(false)

function makeReportFlow(createdAt = '', finalized = false) {
  return [
    { label: reportTerms.value.flowBuild, done: true, cur: false, time: '' },
    { label: reportTerms.value.flowGenerate, done: true, cur: false, time: createdAt || '' },
    { label: reportTerms.value.flowReview, done: finalized, cur: !finalized, time: finalized ? '已完成' : '当前步骤' },
    { label: reportTerms.value.flowPush, done: false, cur: false, time: '待处理' },
  ]
}

function toScenarioReport(r, idx = 0) {
  if (!isCheckupScenario.value) return { ...r, reportType: scenario.value.reportLabel }
  const sources = scenario.value.sourceOptions
  const owners = ['总检医生', '健康管理师', '体检医生', '复查专员']
  return {
    ...r,
    source: sources[idx % sources.length],
    owner: owners[idx % owners.length],
    reportType: scenario.value.reportLabel,
    aiStatus: r.aiStatus === '已完成' ? '已完成' : '待确认',
    summary: r.summary || '体检报告已完成结构化解析，请结合异常指标和既往体检记录确认复查建议。',
    aiReadSummary: r.aiReadSummary || '建议根据风险等级完成体检报告解读、复查预约和必要的专科转诊。',
    flow: makeReportFlow(r.uploadAt, r.reportStatus === '已审核'),
  }
}

async function loadReports() {
  if (rpLoaded.value || rpLoading.value) return
  rpLoading.value = true
  try {
      const allReports = []
      let page = 1
      let pages = 1
      do {
        const res = await fetch(`/api/b/reports?page=${page}&per_page=100&include_unreported=1`, { credentials: 'include' })
        const data = await res.json()
      if (!data.success) {
        rpList.value = []
        toast?.show(data.message || '加载真实报告列表失败')
        return
      }
        allReports.push(...(data.data?.reports || []))
        pages = data.data?.pages || 1
        page += 1
      } while (page <= pages)

      rpList.value = allReports
        .map((r) => {
          const patient = r.patient || {}
          const record = r.record || {}
          const gender = patient.gender || r.patient_gender || r.gender || '—'
          const age = record.age || r.patient_age || patient.age || r.age || '—'
          const phoneRaw = patient.phone || r.patient_phone || r.phone || ''
          const phoneMasked = phoneRaw
            ? String(phoneRaw).replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
            : '—'
          const sourceRaw = patient.source || patient.source_channel || r.patient_source || r.source || '—'
          const nType = r.nodule_type || patient.nodule_type || r.patient_nodule_type || 'breast'

          return ({
            id: r.id,
            rawPatientId: r.patient_id,
            rawRecordId: r.record_id,
            isReportPlaceholder: !!r.is_report_placeholder,
            name: r.patient_name || '—',
            gender,
            age,
            phone: phoneMasked,
            source: sourceLabel(sourceRaw) || sourceRaw,
            reportType: scenario.value.reportLabel,
            nodules: noduleTypeLabel(nType),
            noduleKey: nType,
            uploadAt: r.created_at ? r.created_at.slice(0, 16).replace('T', ' ') : '—',
            aiStatus: r.status === 'not_generated' ? '待生成' : r.status === 'finalized' || r.status === 'published' ? '已完成' : '待审核',
            risk: r.risk_level || '未评估',
            riskTone: r.risk_level === '高风险' ? 'r' : r.risk_level === '中风险' ? 'o' : 'g',
            owner: r.created_by_name || scenario.value.defaultOwner,
            summary: r.report_summary || r.summary || '',
            aiReadSummary: r.imaging_conclusion || r.ai_read_summary || '',
            reportStatus: r.status === 'not_generated' ? '待生成' : r.status === 'finalized' || r.status === 'published' ? '已审核' : '待审核',
            reportHtml: '',
            flow: makeReportFlow(r.created_at ? r.created_at.slice(0, 16).replace('T', ' ') : '', r.status === 'finalized')
          })
        })
        .map(toScenarioReport)
      if (rpList.value.length) rpActiveId.value = rpList.value[0].id
      rpLoaded.value = true
  } catch (e) {
    console.error('加载报告列表失败', e)
    rpList.value = []
    toast?.show('加载真实报告列表失败，请确认后端服务和登录状态')
  } finally {
    rpLoading.value = false
  }
}

function useMockReports() {
  if (rpList.value.length) return
  rpList.value = [
      { id:'r1', name:'张*国', gender:'男', age:56, phone:'138****5678', source:'门诊', reportType:'健康报告', nodules:'肺部结节', noduleKey:'lung', uploadAt:'2026-04-20 09:15', aiStatus:'未完成', risk:'高风险', riskTone:'r', owner:'李医生', summary:'患者右肺上叶发现直径约8mm磨玻璃结节，边界清晰，建议3个月后复查CT。', aiReadSummary:'综合影像学表现，该结节具有一定恶性风险，建议密切随访，必要时行穿刺活检。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-20 09:15'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r2', name:'李*婷', gender:'女', age:48, phone:'139****2468', source:'体检中心', reportType:'健康报告', nodules:'甲状腺结节', noduleKey:'thyroid', uploadAt:'2026-04-19 14:30', aiStatus:'未完成', risk:'中风险', riskTone:'o', owner:'李医生', summary:'甲状腺左叶发现低回声结节，大小约6×4mm，TI-RADS 3类，建议6个月后复查超声。', aiReadSummary:'结节形态规则，边界清晰，暂无明显恶性征象，建议定期随访观察。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-19 14:30'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r3', name:'王*梅', gender:'女', age:62, phone:'137****1357', source:'门诊', reportType:'健康报告', nodules:'乳腺结节', noduleKey:'breast', uploadAt:'2026-04-18 10:00', aiStatus:'已完成', risk:'中风险', riskTone:'o', owner:'李医生', summary:'右乳外上象限发现低回声结节，大小约10×8mm，BI-RADS 3类，建议6个月后复查。', aiReadSummary:'结节边界清晰，内部回声均匀，暂无恶性征象，建议定期随访。', reportStatus:'已审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-18 10:00'},{label:'人工审核',done:true,cur:false,time:'已完成'},{label:'推送患者',done:false,cur:true,time:'待处理'}] },
      { id:'r4', name:'赵*强', gender:'男', age:59, phone:'136****8899', source:'体检中心', reportType:'健康报告', nodules:'肺部结节', noduleKey:'lung', uploadAt:'2026-04-17 16:45', aiStatus:'未完成', risk:'高风险', riskTone:'r', owner:'李医生', summary:'左肺下叶发现实性结节，直径约12mm，边缘有毛刺，建议尽快行增强CT检查。', aiReadSummary:'结节形态不规则，边缘毛刺征，恶性风险较高，建议尽快就诊胸外科。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-17 16:45'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r5', name:'陈*霞', gender:'女', age:45, phone:'138****3344', source:'门诊', reportType:'健康报告', nodules:'乳腺+肺部结节', noduleKey:'breast_lung', uploadAt:'2026-04-16 11:20', aiStatus:'未完成', risk:'低风险', riskTone:'g', owner:'李医生', summary:'双侧乳腺多发小结节，最大约5mm，BI-RADS 2类；右肺微小结节约3mm，建议年度复查。', aiReadSummary:'乳腺及肺部结节均为良性可能性大，建议常规年度随访。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-16 11:20'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r6', name:'刘*峰', gender:'男', age:71, phone:'139****7788', source:'体检中心', reportType:'健康报告', nodules:'肺部+甲状腺结节', noduleKey:'lung_thyroid', uploadAt:'2026-04-15 09:00', aiStatus:'已完成', risk:'低风险', riskTone:'g', owner:'李医生', summary:'右肺微小磨玻璃结节约4mm；甲状腺右叶小结节约5mm，TI-RADS 2类，均建议年度复查。', aiReadSummary:'两处结节均为低风险，建议年度随访，无需特殊处理。', reportStatus:'已审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-15 09:00'},{label:'人工审核',done:true,cur:false,time:'已完成'},{label:'推送患者',done:false,cur:true,time:'待处理'}] },
      { id:'r7', name:'孙*英', gender:'女', age:52, phone:'137****6677', source:'门诊', reportType:'健康报告', nodules:'乳腺结节', noduleKey:'breast', uploadAt:'2026-04-14 15:30', aiStatus:'未完成', risk:'低风险', riskTone:'g', owner:'李医生', summary:'左乳内下象限发现囊性结节，大小约8×6mm，BI-RADS 2类，建议6个月后复查超声。', aiReadSummary:'囊性结节，良性可能性极大，建议定期随访，无需手术干预。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-14 15:30'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r8', name:'周*明', gender:'男', age:64, phone:'138****9900', source:'门诊', reportType:'健康报告', nodules:'肺部+甲状腺结节', noduleKey:'lung_thyroid', uploadAt:'2026-04-13 10:45', aiStatus:'未完成', risk:'中风险', riskTone:'o', owner:'李医生', summary:'右肺中叶磨玻璃结节约7mm，建议3个月后复查；甲状腺左叶结节TI-RADS 3类，建议6个月复查。', aiReadSummary:'肺部结节需密切随访，甲状腺结节暂无恶性征象，建议综合管理。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-13 10:45'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r9', name:'吴*丽', gender:'女', age:39, phone:'150****4455', source:'社区', reportType:'健康报告', nodules:'乳腺+甲状腺结节', noduleKey:'breast_thyroid', uploadAt:'2026-04-12 14:00', aiStatus:'未完成', risk:'高风险', riskTone:'r', owner:'李医生', summary:'右乳发现低回声结节约15×12mm，BI-RADS 4A类，建议穿刺活检；甲状腺结节TI-RADS 4类。', aiReadSummary:'乳腺结节具有一定恶性风险，建议尽快行穿刺活检明确诊断；甲状腺结节亦需进一步评估。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-12 14:00'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
      { id:'r10', name:'郑*涛', gender:'男', age:67, phone:'136****2233', source:'体检中心', reportType:'健康报告', nodules:'三合并结节', noduleKey:'triple', uploadAt:'2026-04-11 09:30', aiStatus:'未完成', risk:'高风险', riskTone:'r', owner:'李医生', summary:'肺部、甲状腺、乳腺三处均发现结节，其中肺部结节约10mm，建议多学科会诊。', aiReadSummary:'三处结节并存，综合风险较高，建议多学科会诊，制定个体化管理方案。', reportStatus:'待审核', reportHtml:'', flow:[{label:'建档',done:true,cur:false,time:''},{label:'生成报告',done:true,cur:false,time:'2026-04-11 09:30'},{label:'人工审核',done:false,cur:true,time:'当前步骤'},{label:'推送患者',done:false,cur:false,time:'待处理'}] },
  ].map(toScenarioReport)
  rpActiveId.value = 'r1'
}

const rpFinalizing = ref(false)
const rpViewHtml = ref('')
const rpViewVisible = ref(false)
const rpAuditId = ref('')
const rpAuditPara1 = ref('')
const rpAuditPara2 = ref('')
const rpAuditImagingAdvice = ref('')
const rpAuditOverallAdvice = ref('')
const rpAuditRiskAdvice = ref('')
const rpAuditTongueAdvice = ref('')
const rpAuditStatus = ref('')
const rpAuditVersion = ref(1)
const rpAuditWasReviewed = ref(false)

function currentAuditSections() {
  return {
    imaging_report_advice: rpAuditImagingAdvice.value,
    overall_assessment: rpAuditOverallAdvice.value,
    risk_assessment: rpAuditRiskAdvice.value,
    tongue_conclusion: rpAuditTongueAdvice.value
  }
}

async function openAudit(r) {
  rpAuditId.value = r.id
  rpAuditPara1.value = r.summary || `暂无${reportTerms.value.summaryLabel}`
  rpAuditPara2.value = r.aiReadSummary || `暂无${reportTerms.value.adviceLabel}`
  rpAuditImagingAdvice.value = r.aiReadSummary || ''
  rpAuditOverallAdvice.value = r.summary || ''
  rpAuditRiskAdvice.value = r.risk ? `当前风险等级：${r.risk}` : ''
  rpAuditTongueAdvice.value = ''
  rpAuditStatus.value = ''
  rpAuditVersion.value = 1
  rpAuditWasReviewed.value = r.reportStatus === '已审核'
  rpActiveId.value = r.id
  if (!String(r.id || '').startsWith('r')) {
    try {
      const data = await apiJson(`/api/b/reports/${r.id}/advice`)
      const advice = normalizeAdvicePayload(data.advice, {})
      rpAuditPara2.value = advice.content || rpAuditPara2.value
      rpAuditImagingAdvice.value = advice.sections.imaging_report_advice || rpAuditPara2.value
      rpAuditOverallAdvice.value = advice.sections.overall_assessment || rpAuditPara1.value
      rpAuditRiskAdvice.value = advice.sections.risk_assessment || rpAuditRiskAdvice.value
      rpAuditTongueAdvice.value = advice.sections.tongue_conclusion || ''
      rpAuditStatus.value = advice.status || ''
      rpAuditVersion.value = advice.version || 1

      const detail = await apiJson(`/api/b/reports/${r.id}`)
      rpAuditPara1.value = detail.report_summary || detail.summary || rpAuditPara1.value
      rpAuditOverallAdvice.value = rpAuditOverallAdvice.value || rpAuditPara1.value
      rpAuditRiskAdvice.value = rpAuditRiskAdvice.value || detail.imaging_risk_warning || ''
      rpAuditTongueAdvice.value = rpAuditTongueAdvice.value || detail.record?.tongue_result_summary || ''
      r.summary = rpAuditPara1.value
      r.aiReadSummary = rpAuditImagingAdvice.value || rpAuditPara2.value
    } catch (e) {
      console.error('加载报告建议失败', e)
    }
  }
}

async function finalizeReport(reportId) {
  if (!reportId) return
  rpFinalizing.value = true
  try {
    if (!String(reportId || '').startsWith('r')) {
      await apiJson(`/api/b/reports/${reportId}/advice`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: rpAuditImagingAdvice.value,
          sections: currentAuditSections(),
          preserve_history: true
        })
      })
      const data = await apiJson(`/api/b/reports/${reportId}/advice/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: rpAuditImagingAdvice.value,
          summary: rpAuditOverallAdvice.value,
          sections: currentAuditSections()
        })
      })
      const r = rpList.value.find(x => x.id === reportId)
      if (r) {
        r.reportStatus = '已审核'
        r.aiStatus = '已完成'
        r.summary = rpAuditOverallAdvice.value
        r.aiReadSummary = rpAuditImagingAdvice.value
        r.flow = makeReportFlow(r.uploadAt, true)
      }
      rpAuditStatus.value = data.advice?.status || 'archived'
      rpAuditVersion.value = data.advice?.version || rpAuditVersion.value
      rpAuditId.value = ''
      rpLoaded.value = false
      await loadReports()
      return
    }
  } catch (e) {
    console.error('审核报告失败', e)
    if (!String(reportId || '').startsWith('r')) {
      toast?.show(e.message || '审核失败')
      return
    }
  } finally {
    rpFinalizing.value = false
  }

  try {
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
  const mockR = rpList.value.find(x => x.id === reportId)
  if (mockR?.isReportPlaceholder || String(reportId || '').startsWith('patient-')) {
    toast?.show('该患者尚未生成健康报告，请先点击“去生成”')
    return
  }
  try {
    const data = await apiJson(`/api/b/reports/${reportId}`)
    const html = data.report_html || data.final_report_html || ''
    if (html) {
      rpViewHtml.value = html
      rpViewVisible.value = true
      return
    }
    if (data.imaging_conclusion || data.report_summary || data.summary || data.advice_draft) {
      rpViewHtml.value = buildReportPreviewHtml(data, reportId)
      rpViewVisible.value = true
      return
    }
    toast?.show('报告详情暂未生成可查看内容')
  } catch (e) {
    if (!mockR) {
      toast?.show(e.message || '查看报告失败')
      return
    }
  }
  // mock fallback: build simple HTML from local data
  if (mockR) {
    rpViewHtml.value = buildReportPreviewHtml({
      report_code: mockR.reportNo || mockR.id,
      status: mockR.reportStatus,
      patient: { name: mockR.name },
      nodule_type: mockR.noduleType,
      risk_level: mockR.risk,
      report_summary: rpAuditPara1.value || mockR.summary || '',
      imaging_conclusion: rpAuditPara2.value || mockR.aiReadSummary || '',
      created_at: mockR.uploadAt
    }, reportId)
    rpViewVisible.value = true
  }
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function paragraphHtml(value) {
  const text = escapeHtml(value || '暂无')
  return text.replace(/\n/g, '<br>')
}

function buildReportPreviewHtml(report, reportId) {
  const advice = report.advice_draft?.content || report.imaging_conclusion || report.ai_read_summary || ''
  const sections = report.advice_draft?.sections || {}
  const patientName = report.patient?.name || report.patient_name || '—'
  const nodule = noduleTypeLabel(report.nodule_type || report.record?.nodule_type)
  const reviewedAt = report.reviewed_at || report.updated_at || report.created_at || '—'
  return `
    <h2>${escapeHtml(scenario.value.reportLabel)}（报告内容预览）</h2>
    <p><b>报告编号：</b>${escapeHtml(report.report_code || reportId)} &nbsp; <b>状态：</b>${escapeHtml(reportDbStatusLabel(report.status))}</p>
    <p><b>患者：</b>${escapeHtml(patientName)} &nbsp; <b>结节类型：</b>${escapeHtml(nodule)} &nbsp; <b>风险等级：</b>${escapeHtml(report.risk_level || '未评估')}</p>
    <h3>${escapeHtml(reportTerms.value.summaryLabel)}</h3>
    <p>${paragraphHtml(report.report_summary || report.summary || sections.overall_assessment)}</p>
    <h3>${escapeHtml(reportTerms.value.adviceLabel)}</h3>
    <p>${paragraphHtml(advice || sections.imaging_report_advice)}</p>
    ${sections.risk_assessment ? `<h3>风险提示</h3><p>${paragraphHtml(sections.risk_assessment)}</p>` : ''}
    ${sections.tongue_conclusion ? `<h3>舌诊结论</h3><p>${paragraphHtml(sections.tongue_conclusion)}</p>` : ''}
    <p style="color:#94a3b8;font-size:12px;margin-top:20px">最后更新时间：${escapeHtml(reviewedAt)}</p>
  `
}

function downloadReport(reportId) {
  const row = rpList.value.find(x => x.id === reportId)
  if (row?.isReportPlaceholder || String(reportId || '').startsWith('patient-')) {
    toast?.show('该患者尚未生成健康报告，暂不能下载')
    return
  }
  if (!reportId || String(reportId).startsWith('r')) {
    toast?.show('示例报告暂无可下载文件')
    return
  }
  window.open(`/api/b/reports/${reportId}/export-pdf`, '_blank')
}

const rpFilteredList = computed(() => {
  return rpList.value.filter(r => {
    if (rpSearch.value && !String(r.name || '').includes(rpSearch.value) && !String(r.phone || '').includes(rpSearch.value)) return false
    if (rpSource.value && r.source !== rpSource.value) return false
    if (rpNodule.value && r.nodules !== rpNodule.value) return false
    if (rpRisk.value && r.risk !== rpRisk.value) return false
    return true
  })
})

const rpActive = computed(() => rpList.value.find(r => r.id === rpActiveId.value) || rpList.value[0])

async function openReportRowPrimary(r) {
  if (!r) return
  if (r.isReportPlaceholder) {
    await generateReportForReportRow(r)
    return
  }
  openAudit(r)
}

async function generateReportForReportRow(r) {
  if (!r?.rawRecordId) {
    toast?.show('该患者还没有健康档案，请先建档后再生成报告')
    const patient = queue.value.find(p => p._apiId === r?.rawPatientId)
    if (patient) goRecord(patient)
    return
  }

  const generateKey = r.rawPatientId || r.id
  if (reportGeneratingIds.value.has(generateKey)) return
  reportGeneratingIds.value = new Set([...reportGeneratingIds.value, generateKey])

  try {
    const job = await apiJson('/api/b/reports/generate-jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ record_id: r.rawRecordId })
    })
    const jobId = job.job_id
    if (!jobId) throw new Error('报告生成任务未返回任务ID')
    toast?.show('报告生成任务已提交，AI处理中...')

    let completed = false
    for (let attempt = 0; attempt < 90; attempt += 1) {
      await sleep(attempt < 10 ? 2000 : 5000)
      const statusData = await apiJson(`/api/b/reports/generate-jobs/${jobId}`)
      if (statusData.status === 'completed') {
        completed = true
        break
      }
      if (statusData.status === 'failed') {
        throw new Error(statusData.message || 'AI生成失败')
      }
    }

    rpLoaded.value = false
    await loadReports()
    if (completed) {
      toast?.show('健康报告已生成，请审核确认')
    } else {
      toast?.show('报告仍在生成中，请稍后刷新查看')
    }
  } catch (e) {
    toast?.show(e.message || '生成健康报告失败')
  } finally {
    const next = new Set(reportGeneratingIds.value)
    next.delete(generateKey)
    reportGeneratingIds.value = next
  }
}

/**
 * @isdoc
 * @description 来源展示：仅保留「门诊 / 体检中心」
 * @param {string} src
 * @returns {string}
 */
function sourceLabel(src) {
  const s = String(src || '').trim()
  const hit = scenario.value.sourceOptions.find((x) => s.includes(x) || x.includes(s))
  if (hit) return hit
  return scenario.value.sourceOptions[0] || s || '—'
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
  if (k === 'new') return `请先完成患者建档信息，后续才能上传检查报告并生成${scenario.value.reportLabel}。`
  if (k === 'gen') return `请上传/补全检查报告，系统将自动解析并生成${scenario.value.reportLabel}草稿。`
  if (k === 'review') return `${scenario.value.reportLabel}已生成，等待人工确认后进入随访任务下发。`
  if (k === 'plan') return '请选择随访任务模板，预览任务节点并确认下发。'
  return '当前处于任务执行中，可查看已下发任务与打卡记录。'
}

/**
 * @isdoc
 * @description 阶段说明（按你给的文案）
 * @param {any} p
 * @returns {string}
 */
function nextHintV2(p) {
  const k = statusKey(p)
  if (k === 'gen') return `系统将根据档案资料生成${scenario.value.reportLabel}草稿。`
  if (k === 'review') return `${scenario.value.reportLabel}已生成，建议优先完成确认。`
  if (k === 'plan') return `${scenario.value.reportLabel}已确认，等待下发随访任务。`
  if (k === 'follow') return '患者任务执行中，可查看任务记录。'
  return `请先完成患者档案建立，后续才能生成${scenario.value.reportLabel}。`
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
    { k: 'b', label: `${scenario.value.reportLabel}生成` },
    { k: 'c', label: isCheckupScenario.value ? '总检确认' : '健康报告审核' },
    { k: 'd', label: '随访任务下发' },
    { k: 'e', label: '任务执行' },
  ]

  // 当前节点：按“当前状态”定位到主流程节点
  // 健康报告待生成 → 当前=健康报告生成
  // 健康报告待审核 → 当前=健康报告审核
  // 任务待下发 → 当前=随访任务下发
  // 任务执行中 → 当前=任务执行
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
    const generating = reportGeneratingIds.value.has(p?.id)
    return [
      { label: generating ? '生成中...' : (isCheckupScenario.value ? '生成解读' : '生成报告'), primary: true, disabled: generating, onClick: () => generateReportForPatient(p) },
      { label: '全流程管理', primary: false, onClick: () => openPatientWorkspace(p) },
    ]
  }
  if (k === 'review') {
    return [
      { label: isCheckupScenario.value ? '总检确认' : '审核报告', primary: true, onClick: () => openPatientWorkspace(p) },
      { label: '报告列表', primary: false, onClick: () => setSubTab('review') },
    ]
  }
  if (k === 'plan') {
    return [{ label: '随访任务下发', primary: true, onClick: () => openPatientWorkspace(p) }]
  }
  if (k === 'follow') {
    return [
      { label: '查看全流程', primary: true, onClick: () => openPatientWorkspace(p) },
      { label: '执行跟踪', primary: false, onClick: () => setSubTab('follow') },
    ]
  }
  return [{ label: '建立档案', primary: true, onClick: () => goRecord(p) }]
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
  if (k === 'review') return isCheckupScenario.value ? '总检确认' : '审核报告'
  if (k === 'plan') return '随访任务下发'
  return '执行跟踪'
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
      { at: '—', tone: 'o', text: `等待生成${scenario.value.reportLabel}` },
    ]
  }
  if (k === 'review') {
    return [
      { at: baseAt, tone: 'p', text: `${scenario.value.reportLabel}已生成` },
      { at: '—', tone: 'o', text: isCheckupScenario.value ? '进入总检确认队列' : '进入待审核队列' },
      { at: '—', tone: 'o', text: isCheckupScenario.value ? '等待总检确认' : '等待人工审核' },
    ]
  }
  if (k === 'plan') {
    return [
      { at: baseAt, tone: 'g', text: `${scenario.value.reportLabel}已确认` },
      { at: '—', tone: 'b', text: '患者报告已推送' },
      { at: '—', tone: 'o', text: '等待下发随访任务' },
    ]
  }
  // follow
  return [
    { at: baseAt, tone: 'b', text: '任务已下发' },
    { at: '—', tone: 'g', text: '等待用户打卡' },
    { at: '—', tone: 'p', text: '可查看任务执行记录' },
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
  { label: `AI${scenario.value.reportLabel}`, ic: 'AI', sub: '待生成', cls: '' },
  { label: isCheckupScenario.value ? '总检确认' : '人工审核', ic: '审', sub: isCheckupScenario.value ? '待确认' : '待审核', cls: '' },
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
  // 任务执行中
  if (stage === 'follow') return 'follow'
  // 其它（包括 abnormal）统一归为“任务待下发”
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
  if (k === 'gen') return `${scenario.value.reportLabel}待生成`
  if (k === 'review') return isCheckupScenario.value ? '待总检确认' : '健康报告待审核'
  if (k === 'plan') return '任务待下发'
  return '任务执行中'
}

const stageTabs = computed(() => {
  const count = (k) => queue.value.filter((p) => statusKey(p) === k).length
  return [
    { key: 'all', label: '全部', count: queue.value.length },
    { key: 'gen', label: `${scenario.value.reportLabel}待生成`, count: count('gen') },
    { key: 'review', label: isCheckupScenario.value ? '待总检确认' : '健康报告待审核', count: count('review') },
    { key: 'plan', label: '任务待下发', count: count('plan') },
    { key: 'follow', label: '任务执行中', count: count('follow') },
  ]
})

const nextActions = [
  '上传复查报告',
  `推送${scenario.value.reportLabel}`,
  '下发健康管理任务',
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
  { id:'m2', name:'李*婷', gender:'女', age:48, phoneMasked:'139****2468', source:'体检中心', owner:'李医生', nodules:'甲状腺结节', noduleType:'thyroid', risk:'中风险', riskTone:'o', stage:'review', lastReport:'超声报告' },
  { id:'m3', name:'王*梅', gender:'女', age:62, phoneMasked:'137****1357', source:'门诊', owner:'李医生', nodules:'乳腺结节', noduleType:'breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day1', channel:'小程序', cycle:'每月' } },
  { id:'m4', name:'赵*强', gender:'男', age:59, phoneMasked:'136****8899', source:'体检中心', owner:'李医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'plan', lastReport:'CT报告', planTask:{ day:'day1', channel:'电话', cycle:'每两周' } },
  { id:'m5', name:'陈*霞', gender:'女', age:45, phoneMasked:'138****3344', source:'门诊', owner:'李医生', nodules:'乳腺+肺部结节', noduleType:'breast_lung', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day2', channel:'小程序', cycle:'每月' } },
  { id:'m6', name:'刘*峰', gender:'男', age:71, phoneMasked:'139****7788', source:'体检中心', owner:'李医生', nodules:'肺部+甲状腺结节', noduleType:'lung_thyroid', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'医生复核中', planTask:{ day:'day1', channel:'短信', cycle:'每季度' } },
  { id:'m7', name:'孙*英', gender:'女', age:52, phoneMasked:'137****6677', source:'门诊', owner:'李医生', nodules:'乳腺结节', noduleType:'breast', risk:'低风险', riskTone:'g', stage:'gen', lastReport:'超声报告' },
  { id:'m8', name:'周*明', gender:'男', age:64, phoneMasked:'138****9900', source:'门诊', owner:'李医生', nodules:'肺部+甲状腺结节', noduleType:'lung_thyroid', risk:'中风险', riskTone:'o', stage:'plan', lastReport:'CT报告', planTask:{ day:'day2', channel:'电话', cycle:'每月' } },
  { id:'m9', name:'吴*丽', gender:'女', age:39, phoneMasked:'150****4455', source:'社区', owner:'李医生', nodules:'乳腺+甲状腺结节', noduleType:'breast_thyroid', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'超声报告', planTask:{ day:'day1', channel:'小程序', cycle:'每两周' } },
  { id:'m10', name:'郑*涛', gender:'男', age:67, phoneMasked:'136****2233', source:'体检中心', owner:'李医生', nodules:'三合并结节', noduleType:'triple', risk:'高风险', riskTone:'r', stage:'plan', lastReport:'CT报告', planTask:{ day:'day3', channel:'电话', cycle:'每月' } },
  { id:'m11', name:'黄*芳', gender:'女', age:44, phoneMasked:'135****1122', source:'门诊', owner:'王医生', nodules:'乳腺结节', noduleType:'breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day3', channel:'小程序', cycle:'每月' } },
  { id:'m12', name:'林*海', gender:'男', age:58, phoneMasked:'132****8866', source:'体检中心', owner:'王医生', nodules:'肺部结节', noduleType:'lung', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'CT报告', planTask:{ day:'day7', channel:'电话', cycle:'每两周' } },
  { id:'m13', name:'何*秀', gender:'女', age:51, phoneMasked:'133****5544', source:'门诊', owner:'王医生', nodules:'甲状腺结节', noduleType:'thyroid', risk:'低风险', riskTone:'g', stage:'follow', lastReport:'超声报告', planTask:{ day:'day14', channel:'小程序', cycle:'每季度' } },
  { id:'m14', name:'马*军', gender:'男', age:63, phoneMasked:'139****3311', source:'体检中心', owner:'李医生', nodules:'肺部+乳腺结节', noduleType:'lung_breast', risk:'高风险', riskTone:'r', stage:'follow', lastReport:'AI解析完成', planTask:{ day:'day7', channel:'小程序', cycle:'每月' } },
  { id:'m15', name:'谢*云', gender:'女', age:37, phoneMasked:'136****7700', source:'社区', owner:'王医生', nodules:'甲状腺+乳腺结节', noduleType:'thyroid_breast', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'超声报告', planTask:{ day:'day21', channel:'小程序', cycle:'每月' } },
  { id:'m16', name:'徐*刚', gender:'男', age:55, phoneMasked:'138****4499', source:'门诊', owner:'李医生', nodules:'肺部结节', noduleType:'lung', risk:'中风险', riskTone:'o', stage:'follow', lastReport:'CT报告', planTask:{ day:'day30', channel:'电话', cycle:'每季度' } },
]

function adaptMockQueueByScenario(list) {
  const sources = scenario.value.sourceOptions || []
  const owner = scenario.value.defaultOwner || '李医生'
  return list.map((p, idx) => ({
    ...p,
    source: sources[idx % Math.max(sources.length, 1)] || p.source,
    owner: idx % 3 === 0 ? owner : p.owner?.replace('医生', scenario.value.key === 'pharmacy' ? '药师' : scenario.value.key === 'community' ? '家医' : '医生'),
  }))
}

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
      const items = (data.data?.items || data.data || [])
      queue.value = items.map(p => ({
        id: p.id,
        _apiId: p.id,
        name: p.name || '—',
        gender: p.gender || '—',
        age: p.age || '—',
        phoneMasked: p.phone ? p.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '—',
        phone: p.phone || '',
        wecomExternalUserid: p.wecom_external_userid || '',
        wecomUserid: p.wecom_userid || '',
        wecomBindStatus: p.wecom_bind_status || ((p.wecom_external_userid || p.wecom_userid) ? 'bound' : 'unbound'),
        wecomBoundAt: p.wecom_bound_at || '',
        source: p.source_channel === 'manual' ? scenario.value.sourceOptions[0] : (p.source_channel || scenario.value.sourceOptions[0]),
        owner: p.manager_name || scenario.value.defaultOwner,
        nodules: noduleTypeLabel(p.nodule_type),
        noduleType: p.nodule_type || 'breast',
        risk: p.risk_level || (p.reports?.[0]?.risk_level) || '—',
        riskTone: (p.risk_level || p.reports?.[0]?.risk_level) === '高风险' ? 'r' : (p.risk_level || p.reports?.[0]?.risk_level) === '中风险' ? 'o' : 'g',
        stage: p.risk_level ? 'plan' : (p.reports?.length ? 'review' : 'gen'),
        stageLabel: p.risk_level ? statusLabel({ stage: 'plan' }) : (p.reports?.length ? statusLabel({ stage: 'review' }) : statusLabel({ stage: 'aiGen' })),
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
  if (!queue.value.length) queue.value = adaptMockQueueByScenario(MOCK_QUEUE).map(p => ({
    ...p,
    stageLabel: '', nextStep: '', serviceStatus: '',
    report: { status: '—', summary: '' }, rawReports: [],
    aiReadSummary: '', reportDoc: { title: '', sections: [] },
    auditTrail: [], chat: [], followTodos: [],
    abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
    reviewers: '', assistants: [], timeline: [],
  }))
  // 始终追加 follow 阶段的 mock 患者（确保任务执行列表有演示数据）
  const followMocks = adaptMockQueueByScenario(MOCK_QUEUE).filter(p => p.stage === 'follow').map(p => ({
    ...p,
    stageLabel: '任务执行中', nextStep: '', serviceStatus: '任务执行中',
    report: { status: '—', summary: '' }, rawReports: [],
    aiReadSummary: '', reportDoc: { title: '', sections: [] },
    auditTrail: [], chat: [], followTodos: [],
    abnormal: { keywords: [], interventions: [], recallPlan: '', recallState: '—', recallTone: 'g', recallHint: '' },
    reviewers: '', assistants: [], timeline: [],
  }))
  const existingIds = new Set(queue.value.map(p => p.id))
  followMocks.forEach(p => { if (!existingIds.has(p.id)) queue.value.push(p) })
}

function noduleTypeLabel(t) {
  const map = {
    breast: '乳腺结节', lung: '肺部结节', thyroid: '甲状腺结节',
    breast_lung: '乳腺+肺部结节', breast_thyroid: '乳腺+甲状腺结节',
    lung_thyroid: '肺部+甲状腺结节', triple: '三合并结节'
  }
  return map[t] || t || '—'
}

function riskLevelLabel(risk) {
  const map = { high: '高风险', mid: '中风险', medium: '中风险', low: '低风险' }
  return map[risk] || risk || '通用风险'
}

function channelLabel(channel) {
  const map = { wecom: '企业微信', phone: '电话', miniapp: '小程序' }
  return map[channel] || channel || '企业微信'
}

function templateStatusLabel(status) {
  const map = { draft: '草稿', active: '启用', paused: '暂停', archived: '归档' }
  return map[status] || status || '模板'
}

function planStatusLabel(status) {
  const map = { draft: '草稿', active: '执行中', paused: '已暂停', completed: '已完成', cancelled: '已取消' }
  return map[status] || status || '计划'
}

function taskTypeLabel(type) {
  const map = {
    knowledge: '知识推送',
    knowledge_push: '知识推送',
    daily_checkin: '每日打卡',
    diet_checkin: '饮食打卡',
    diet_image_checkin: '餐饮图片打卡',
    breakfast_checkin: '早餐打卡',
    lunch_checkin: '午餐打卡',
    dinner_checkin: '晚餐打卡',
    exercise_reminder: '运动提醒',
    psych_reminder: '心理关怀',
    review_reminder: '复查提醒',
    manual: '人工处理',
  }
  return map[type] || type || '随访任务'
}

function patientActionLabel(action) {
  const map = {
    none: '无需患者操作',
    read: '患者阅读',
    checkin: '患者打卡',
    fill_form: '填写表单',
    upload_image: '上传餐饮图片',
    upload_report: '上传报告',
    reply: '患者回复',
    reply_text: '文字回复',
    confirm: '患者确认',
  }
  return map[action] || action || '无需患者操作'
}

function aiActionLabel(action) {
  const map = {
    none: '无自动处理',
    send_message: '自动发送提醒',
    reply: '自动回复',
    analyze_image: '自动分析图片',
    image_recognition: '图片识别',
    diet_review: '饮食点评',
    summarize: '自动汇总',
    alert: '异常提醒',
    route_manual: '转人工处理',
  }
  return map[action] || action || '无自动处理'
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

// 任务下发页：展示待下发与执行中的患者
const planPatients = computed(() => queue.value.filter((p) => statusKey(p) === 'plan'))

const activePatient = computed(() => {
  return queue.value.find((p) => p.id === activePatientId.value) || queue.value[0] || {}
})

const wecomBindingPatient = computed(() => {
  return queue.value.find((p) => p.id === wecomBindingPatientId.value) || activePatient.value || null
})

function isWecomBound(p) {
  return p?.wecomBindStatus === 'bound' || !!p?.wecomExternalUserid || !!p?.wecomUserid
}

function wecomStatusText(p) {
  return isWecomBound(p) ? '已绑定' : '未绑定'
}

function applyWecomBinding(patientData) {
  const apiId = patientData?.id
  const target = queue.value.find((p) => p._apiId === apiId || p.id === apiId)
  if (!target) return
  target.wecomExternalUserid = patientData.wecom_external_userid || ''
  target.wecomUserid = patientData.wecom_userid || ''
  target.wecomBindStatus = patientData.wecom_bind_status || (target.wecomExternalUserid || target.wecomUserid ? 'bound' : 'unbound')
  target.wecomBoundAt = patientData.wecom_bound_at || ''
}

function openWecomBind(p = activePatient.value) {
  if (!p?._apiId) {
    toast?.show('演示患者暂不支持绑定企业微信身份')
    return
  }
  wecomBindingPatientId.value = p.id
  wecomForm.external_userid = p.wecomExternalUserid || ''
  wecomForm.userid = p.wecomUserid || ''
  wecomModalOpen.value = true
}

async function submitWecomBind() {
  const p = wecomBindingPatient.value
  if (!p?._apiId) return
  const externalUserid = String(wecomForm.external_userid || '').trim()
  const userid = String(wecomForm.userid || '').trim()
  if (!externalUserid && !userid) {
    toast?.show('请至少填写 external_userid 或 userid')
    return
  }
  wecomBindingSaving.value = true
  try {
    const data = await apiJson(`/api/b/patients/${p._apiId}/wecom-bind`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wecom_external_userid: externalUserid,
        wecom_userid: userid,
      }),
    })
    applyWecomBinding(data)
    wecomModalOpen.value = false
    toast?.show('企业微信身份已绑定')
  } catch (e) {
    toast?.show(e.message || '绑定企业微信身份失败')
  } finally {
    wecomBindingSaving.value = false
  }
}

async function unbindWecom(p = activePatient.value) {
  if (!p?._apiId) {
    toast?.show('演示患者暂不支持解绑企业微信身份')
    return
  }
  if (!window.confirm(`确认解绑 ${p.name || '该患者'} 的企业微信身份？`)) return
  try {
    const data = await apiJson(`/api/b/patients/${p._apiId}/wecom-bind`, { method: 'DELETE' })
    applyWecomBinding(data)
    toast?.show('企业微信身份已解绑')
  } catch (e) {
    toast?.show(e.message || '解绑企业微信身份失败')
  }
}

function nowText() {
  return new Date().toLocaleString('zh-CN', { hour12: false })
}

function formatDateInput(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function nextFollowDateByCycle(cycle) {
  const date = new Date()
  const months = String(cycle || '').includes('3') ? 3 : String(cycle || '').includes('6') ? 6 : 12
  date.setMonth(date.getMonth() + months)
  return formatDateInput(date)
}

function cycleDaysFromLabel(cycle) {
  if (String(cycle || '').includes('3')) return 90
  if (String(cycle || '').includes('6')) return 180
  return 365
}

function cycleLabelFromDays(days) {
  const n = Number(days || 0)
  if (n <= 100) return '3个月'
  if (n <= 220) return '6个月'
  return '12个月'
}

function channelToBackend(channel) {
  const text = String(channel || '')
  if (text.includes('企微')) return 'wecom'
  if (text.includes('电话')) return 'phone'
  if (text.includes('小程序')) return 'miniapp'
  return 'wecom'
}

async function loadFollowupTasks() {
  try {
    const data = await apiJson('/api/b/followup/tasks?per_page=100')
    const items = data.items || data || []
    const apiTasks = items.map(normalizeBackendTask)
    if (apiTasks.length) {
      const localOnly = (followTasks.value || []).filter((t) => !t._apiTaskId)
      followTasks.value = [...apiTasks, ...localOnly]
      if (!activeTaskId.value || !followTasks.value.some((t) => t.id === activeTaskId.value)) {
        const firstForPatient = followPatientId.value
          ? followTasks.value.find((t) => String(t.patientId) === String(followPatientId.value))
          : null
        if (firstForPatient || followTasks.value[0]) selectTask((firstForPatient || followTasks.value[0]).id)
      }
    }
  } catch (e) {
    console.warn('加载随访任务失败', e)
  }
}

function normalizeBackendTask(task) {
  const patient = task.patient || {}
  const node = task.task_payload?.node || {}
  const messages = task.messages || []
  const sentMessage = messages.find((m) => m.direction === 'outbound' && m.sent_at)
  return {
    id: `api-task-${task.id}`,
    _apiTaskId: task.id,
    patientId: patient.id || task.patient_id,
    patientName: patient.name || '患者',
    gender: patient.gender || '—',
    age: patient.age || '—',
    phoneMasked: patient.phone ? patient.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : '—',
    nodules: noduleTypeLabel(task.nodule_type || patient.nodule_type),
    risk: task.risk_level || '—',
    riskTone: task.risk_level === '高风险' || task.risk_level === '高危' || task.risk_level === 'high' ? 'r' : task.risk_level === '中风险' || task.risk_level === '中危' || task.risk_level === 'mid' ? 'o' : 'g',
    owner: task.manager_name || scenario.value.defaultOwner,
    channel: task.channel === 'wecom' ? '企微' : task.channel === 'phone' ? '电话' : task.channel === 'miniapp' ? '小程序' : (task.channel || '企微'),
    cycle: '—',
    reminder: task.task_payload?.reminder_strategy || '',
    day: `day${task.plan_day || 1}`,
    time: String(task.scheduled_send_at || task.due_at || '').slice(11, 16) || node.send_time || '09:00',
    scheduledAt: task.scheduled_send_at || task.due_at || '',
    sentAt: sentMessage?.sent_at || '',
    status: task.status === 'completed' ? 'completed' : (task.status || 'scheduled'),
    node,
    taskPayload: task.task_payload || {},
    message: node.message_template || task.ai_summary || '',
    patientAction: patientActionLabel(node.patient_action),
    aiAction: aiActionLabel(node.ai_action),
    messages,
    kbSnapshot: {},
    logs: (task.events || []).map(e => ({ at: e.created_at || '现在', by: e.actor_type || '系统', action: e.event_type, note: e.summary || '' })),
    createdAt: task.created_at || '',
  }
}

function reportDbStatusLabel(status) {
  const map = {
    draft: '草稿',
    generated: '已生成待审核',
    reviewing: '审核中',
    finalized: '已审核',
    published: '已发布',
    archived: '已归档'
  }
  return map[status] || status || '未生成'
}

function normalizeAdvicePayload(advice, fallback = {}) {
  const sections = advice?.sections || fallback.sections || {}
  return {
    version: advice?.version || fallback.version || 1,
    status: advice?.status || fallback.status || 'draft',
    updatedAt: advice?.updated_at || advice?.updatedAt || fallback.updatedAt || '',
    content: advice?.content || fallback.content || '',
    sections: {
      imaging_report_advice: sections.imaging_report_advice || advice?.content || fallback.content || '',
      overall_assessment: sections.overall_assessment || '',
      risk_assessment: sections.risk_assessment || '',
      tongue_conclusion: sections.tongue_conclusion || ''
    },
    history: (advice?.history || fallback.history || []).map((h, idx) => ({
      id: h.id || `${h.saved_at || h.savedAt || idx}-${h.version || idx}`,
      version: h.version || 1,
      status: h.status || 'draft',
      content: h.content || '',
      sections: h.sections || {},
      savedAt: h.saved_at || h.savedAt || ''
    }))
  }
}

function normalizeImagingReport(item) {
  return {
    id: item.id,
    name: item.file_name || item.name || '影像报告',
    size: item.file_size || item.size || 0,
    uploadedAt: item.uploaded_at || item.uploadedAt || '',
    uploader: item.uploader_name || item.uploaded_by || scenario.value.defaultOwner,
    type: item.file_type || item.type || 'file',
    backend: true
  }
}

async function apiJson(url, options = {}) {
  const res = await fetch(url, { credentials: 'include', ...options })
  const data = await res.json().catch(() => ({}))
  if (!res.ok || data.success === false) throw new Error(data.message || `请求失败：${res.status}`)
  return data.data ?? data
}

async function apiPostJson(url, payload = {}) {
  return apiJson(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function makeDefaultAdvice(p) {
  return {
    version: 1,
    status: 'draft',
    updatedAt: '',
    content: p?.aiReadSummary || p?.report?.summary || '',
    history: []
  }
}

function ensurePatientWorkflow(p) {
  if (!p || !p.id) return p
  p.profileNote = p.profileNote || '既往史、家族史、症状、体征信息待完善。'
  p.assets = p.assets || {}
  p.assets.imagingReports = Array.isArray(p.assets.imagingReports) ? p.assets.imagingReports : []
  p.tongueTask = p.tongueTask || null
  p.tongueH5Url = p.tongueH5Url || p.tongueTask?.h5_url || ''
  p.tongueMobileOpenUrl = p.tongueMobileOpenUrl || ''
  p.workspaceRecords = Array.isArray(p.workspaceRecords) ? p.workspaceRecords : []
  p.workspaceReports = Array.isArray(p.workspaceReports) ? p.workspaceReports : []
  p.workspacePlans = Array.isArray(p.workspacePlans) ? p.workspacePlans : []
  p.workspaceTasks = Array.isArray(p.workspaceTasks) ? p.workspaceTasks : []
  p.latestReport = p.latestReport || null
  p.adviceDraft = p.adviceDraft || makeDefaultAdvice(p)
  p.finalReport = p.finalReport || { content: '', archivedAt: '', version: '' }
  p.followPlan = p.followPlan || {
    cycle: p.planTask?.cycle || (p.riskTone === 'r' ? '3个月' : p.riskTone === 'o' ? '6个月' : '12个月'),
    channel: p.planTask?.channel || '小程序',
    note: `${p.nodules || '结节'}随访，关注分级、大小、症状变化和资料补充。`
  }
  p.managementLogs = Array.isArray(p.managementLogs) ? p.managementLogs : [
    { id: `${p.id}-log-1`, at: '建档后', by: p.owner || scenario.value.defaultOwner, action: '建立患者档案', note: p.nodules || '' },
    { id: `${p.id}-log-2`, at: '待处理', by: '系统', action: '等待报告意见审核', note: statusLabel(p) },
  ]
  return p
}

watch(
  () => activePatient.value?.id,
  () => ensurePatientWorkflow(activePatient.value),
  { immediate: true }
)

async function openPatientWorkspace(p) {
  if (p?.id) activePatientId.value = p.id
  const current = ensurePatientWorkflow(p || activePatient.value)
  setSubTab('detail')
  await hydratePatientWorkspace(current)
}

function buildProfileNote(records, fallback = '') {
  const list = Array.isArray(records) ? records : []
  const latest = list
    .slice()
    .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))[0]
  if (!latest) return fallback || '既往史、家族史、症状、体征信息待完善。'
  const fields = [
    latest.main_complaint,
    latest.medical_history,
    latest.past_history,
    latest.family_history,
    latest.symptoms,
    latest.physical_exam,
    latest.health_condition
  ].filter(Boolean)
  if (fields.length) return fields.join('\n')
  return fallback || `最近档案：${latest.record_code || latest.created_at || `#${latest.id}`}`
}

async function hydratePatientWorkspace(p) {
  if (!p?._apiId) return
  p.workspaceLoading = true
  try {
    const [detail, records, reports, plans, tasks] = await Promise.all([
      apiJson(`/api/b/patients/${p._apiId}`),
      apiJson(`/api/b/patients/${p._apiId}/records`),
      apiJson(`/api/b/reports?patient_id=${p._apiId}&per_page=20`),
      apiJson(`/api/b/followup/patient-plans?patient_id=${p._apiId}`),
      apiJson(`/api/b/followup/tasks?patient_id=${p._apiId}&per_page=50`)
    ])
    if (detail?.name) {
      p.name = detail.name || p.name
      p.gender = detail.gender || p.gender
      p.age = detail.age || p.age
      p.phone = detail.phone || p.phone
      p.phoneMasked = detail.phone ? detail.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2') : p.phoneMasked
      p.nodules = noduleTypeLabel(detail.nodule_type || p.noduleType)
      p.noduleType = detail.nodule_type || p.noduleType
      p.source = detail.source_channel || p.source
      p.wecomExternalUserid = detail.wecom_external_userid || p.wecomExternalUserid
      p.wecomUserid = detail.wecom_userid || p.wecomUserid
      p.wecomBindStatus = detail.wecom_bind_status || p.wecomBindStatus
      p.profileNote = buildProfileNote(detail.health_records || records, p.profileNote)
    }
    p.workspaceRecords = (Array.isArray(records) ? records : [])
      .slice()
      .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
    p.workspaceReports = (reports.reports || reports.items || [])
      .slice()
      .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
    p.workspacePlans = (Array.isArray(plans) ? plans : [])
      .slice()
      .sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
    p.workspaceTasks = (tasks.items || tasks || [])
      .slice()
      .sort((a, b) => String(b.scheduled_send_at || b.due_at || b.created_at || '').localeCompare(String(a.scheduled_send_at || a.due_at || a.created_at || '')))

    const latestRecord = p.workspaceRecords[0]
    if (latestRecord?.id) {
      p.workspaceRecordId = latestRecord.id
      p.latestReport = latestRecord.latest_report || null
      const imaging = await apiJson(`/api/b/records/${latestRecord.id}/imaging-reports`)
      p.assets.imagingReports = (imaging.items || []).map(normalizeImagingReport)
      const tongue = await apiJson(`/api/b/tongue-diagnosis/tasks/by-record/${latestRecord.id}`)
      p.tongueTask = (tongue.items || [])[0] || null
      p.tongueH5Url = p.tongueTask?.h5_url || p.tongueH5Url || ''
      p.tongueMobileOpenUrl = p.tongueTask?.mobile_open_url || p.tongueMobileOpenUrl || ''
    }

    const latestReport = p.workspaceReports[0]
    if (latestReport?.id) {
      p.workspaceReportId = latestReport.id
      p.latestReport = {
        id: latestReport.id,
        report_code: latestReport.report_code,
        status: latestReport.status,
        risk_level: latestReport.risk_level,
        report_summary: latestReport.report_summary,
        imaging_conclusion: latestReport.imaging_conclusion,
        reviewed_at: latestReport.reviewed_at,
        created_at: latestReport.created_at,
        updated_at: latestReport.updated_at
      }
      p.risk = latestReport.risk_level || p.risk
      p.riskTone = latestReport.risk_level === '高风险' ? 'r' : latestReport.risk_level === '中风险' ? 'o' : latestReport.risk_level === '低风险' ? 'g' : p.riskTone
      const advice = await apiJson(`/api/b/reports/${latestReport.id}/advice`)
      p.adviceDraft = normalizeAdvicePayload(advice.advice, p.adviceDraft)
      if (latestReport.status === 'finalized' || latestReport.status === 'published' || p.adviceDraft.status === 'archived') {
        p.finalReport = {
          content: p.adviceDraft.content || latestReport.imaging_conclusion || latestReport.report_summary || '',
          archivedAt: latestReport.reviewed_at || p.adviceDraft.updatedAt || '',
          version: p.adviceDraft.version || 1
        }
        p.stage = 'plan'
      }
    }
  } catch (e) {
    console.error('加载患者工作台失败', e)
  } finally {
    p.workspaceLoading = false
  }
}

async function generateReportForPatient(p) {
  const patient = ensurePatientWorkflow(p || activePatient.value)
  if (!patient?._apiId) {
    toast?.show('请先保存患者信息后再生成报告')
    return
  }
  if (reportGeneratingIds.value.has(patient.id)) return

  reportGeneratingIds.value = new Set([...reportGeneratingIds.value, patient.id])
  try {
    if (!patient.workspaceRecordId) {
      await hydratePatientWorkspace(patient)
    }
    if (!patient.workspaceRecordId) {
      toast?.show('请先完成患者建档，再生成健康报告')
      goRecord(patient)
      return
    }

    const job = await apiJson('/api/b/reports/generate-jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ record_id: patient.workspaceRecordId })
    })
    const jobId = job.job_id
    if (!jobId) throw new Error('报告生成任务未返回任务ID')
    toast?.show('报告生成任务已提交，AI处理中...')

    let completed = false
    for (let attempt = 0; attempt < 90; attempt += 1) {
      await sleep(attempt < 10 ? 2000 : 5000)
      const statusData = await apiJson(`/api/b/reports/generate-jobs/${jobId}`)
      if (statusData.status === 'completed') {
        completed = true
        break
      }
      if (statusData.status === 'failed') {
        throw new Error(statusData.message || 'AI生成失败')
      }
    }

    rpLoaded.value = false
    await hydratePatientWorkspace(patient)
    await loadReports()
    if (completed) {
      patient.stage = 'review'
      toast?.show('健康报告已生成，请到健康报告审核中确认')
      setSubTab('review')
    } else {
      toast?.show('报告仍在生成中，请稍后到健康报告审核查看')
    }
  } catch (e) {
    toast?.show(e.message || '生成健康报告失败')
  } finally {
    const next = new Set(reportGeneratingIds.value)
    next.delete(patient.id)
    reportGeneratingIds.value = next
  }
}

const activeAdvice = computed(() => {
  const p = ensurePatientWorkflow(activePatient.value)
  return p?.adviceDraft || makeDefaultAdvice(p)
})

const workspaceTongueActionLabel = computed(() => {
  const task = activePatient.value?.tongueTask
  if (task?.status === 'h5_sso_created') return '重新打开舌诊 H5'
  if (task?.status === 'completed') return '已完成舌诊'
  return '打开舌诊 H5'
})

const workspaceTongueStatusLabel = computed(() => {
  const status = activePatient.value?.tongueTask?.status
  const map = {
    h5_sso_created: 'H5已生成',
    completed: '舌诊已完成',
    failed: '检测失败',
    waiting_inquiry: '待完成'
  }
  return map[status] || status || ''
})

const workspaceTongueQrUrl = computed(() => {
  const url = activePatient.value?.tongueMobileOpenUrl || activePatient.value?.tongueH5Url || ''
  if (!url) return ''
  return `https://api.qrserver.com/v1/create-qr-code/?size=180x180&margin=8&data=${encodeURIComponent(url)}`
})

function adviceStatusLabel(status) {
  const map = {
    draft: '草稿',
    reviewing: '待审核',
    approved: '审核通过',
    archived: '已写入最终报告',
  }
  return map[status] || '草稿'
}

const patientFlowSteps = computed(() => {
  const p = ensurePatientWorkflow(activePatient.value)
  const adviceStatus = p?.adviceDraft?.status || 'draft'
  const hasFinal = !!p?.finalReport?.content
  const hasPlan = !!p?.followPlan?.note
  const nodes = [
    { key: 'archive', no: 1, label: '档案' },
    { key: 'risk', no: 2, label: '评估' },
    { key: 'advice', no: 3, label: '建议' },
    { key: 'review', no: 4, label: '审核' },
    { key: 'final', no: 5, label: '最终报告' },
    { key: 'follow', no: 6, label: '随访管理' },
  ]
  const current = hasFinal && hasPlan ? 5 : hasFinal ? 4 : adviceStatus === 'reviewing' ? 3 : 2
  return nodes.map((n, idx) => ({ ...n, state: idx < current ? 'done' : idx === current ? 'current' : 'todo' }))
})

const computedRisk = computed(() => {
  const p = activePatient.value || {}
  if (p.riskTone === 'r' || p.risk === '高风险') return { level: '高风险', tone: 'r' }
  if (p.riskTone === 'o' || p.risk === '中风险') return { level: '中风险', tone: 'o' }
  if (p.riskTone === 'g' || p.risk === '低风险') return { level: '低风险', tone: 'g' }
  return { level: '待评估', tone: 'g' }
})

const riskLayerItems = computed(() => {
  const p = ensurePatientWorkflow(activePatient.value)
  const completenessRisk = (p.assets?.imagingReports || []).length ? { level: '资料较完整', tone: 'g' } : { level: '资料缺口', tone: 'o' }
  const tongueRisk = p.tongueTask?.status === 'completed'
    ? { level: '舌诊已回流', tone: 'g' }
    : p.tongueH5Url
      ? { level: 'H5链接已生成', tone: 'g' }
      : { level: '待生成手机链接', tone: 'o' }
  return [
    { key: 'nodule', label: '结节分层', level: computedRisk.value.level, tone: computedRisk.value.tone, reason: `${p.nodules || '结节'}当前标记为${computedRisk.value.level}，需结合分级、大小、数量和症状复核。` },
    { key: 'material', label: '资料完整度', level: completenessRisk.level, tone: completenessRisk.tone, reason: (p.assets?.imagingReports || []).length ? '已上传影像报告，可进入报告解析/复核。' : '缺少原始影像报告，AI只能基于表单生成初步建议。' },
    { key: 'history', label: '病史风险', level: p.profileNote?.includes('家族') ? '需关注' : '常规', tone: p.profileNote?.includes('家族') ? 'o' : 'g', reason: p.profileNote || '病史信息待完善。' },
    { key: 'tongue', label: '舌诊资料', level: tongueRisk.level, tone: tongueRisk.tone, reason: 'B端生成手机H5链接，由患者手机或健康管理师手机完成采集；结果回流后写入档案和报告。' },
  ]
})

function addManagementLog(action, note = '') {
  const p = ensurePatientWorkflow(activePatient.value)
  p.managementLogs = p.managementLogs || []
  p.managementLogs.unshift({ id: `${Date.now()}-${Math.random()}`, at: nowText(), by: p.owner || scenario.value.defaultOwner, action, note })
}

async function handleImagingUpload(event) {
  const p = ensurePatientWorkflow(activePatient.value)
  const files = Array.from(event.target.files || [])
  if (!files.length) return
  try {
    if (p.workspaceRecordId) {
      const form = new FormData()
      files.forEach(file => form.append('imaging_reports', file))
      const data = await apiJson(`/api/b/records/${p.workspaceRecordId}/imaging-reports`, { method: 'POST', body: form })
      const existing = (p.assets.imagingReports || []).filter(x => !x.backend)
      p.assets.imagingReports = [...(data.items || []).map(normalizeImagingReport), ...existing]
    } else {
      files.forEach(file => {
        p.assets.imagingReports.unshift({
          id: `${Date.now()}-${file.name}-${Math.random()}`,
          name: file.name,
          size: file.size,
          uploadedAt: nowText(),
          uploader: p.owner || scenario.value.defaultOwner,
          type: file.type || 'file'
        })
      })
    }
    addManagementLog('上传影像报告', files.map(f => f.name).join('、'))
  } catch (e) {
    toast?.show(e.message || '影像报告上传失败')
  } finally {
    event.target.value = ''
  }
}

async function startWorkspaceTongueDiagnosis() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (!p._apiId || !p.workspaceRecordId) {
    toast?.show('请先保存患者档案，再发起舌诊')
    return
  }
  tongueSubmitting.value = true
  try {
    const data = await apiJson('/api/b/tongue-diagnosis/h5-sso', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient_id: p._apiId, record_id: p.workspaceRecordId })
    })
    p.tongueTask = data.task
    p.tongueH5Url = data.h5_url || data.task?.h5_url || ''
    p.tongueMobileOpenUrl = data.mobile_open_url || ''
    addManagementLog('打开舌诊H5', data.task?.out_id || '')
    if (p.tongueH5Url) window.open(p.tongueH5Url, '_blank', 'noopener')
    toast?.show('手机舌诊链接已生成')
  } catch (e) {
    toast?.show(e.message || 'H5舌诊打开失败')
  } finally {
    tongueSubmitting.value = false
  }
}

async function copyWorkspaceTongueLink() {
  const url = activePatient.value?.tongueMobileOpenUrl || activePatient.value?.tongueH5Url || ''
  if (!url) return
  try {
    await navigator.clipboard.writeText(url)
    toast?.show('舌诊链接已复制')
  } catch (e) {
    toast?.show('复制失败，请手动选择链接')
  }
}

async function syncWorkspaceTongueReport() {
  const p = ensurePatientWorkflow(activePatient.value)
  const taskId = p.tongueTask?.id
  if (!taskId) {
    toast?.show('请先生成舌诊H5链接')
    return
  }
  tongueSyncing.value = true
  try {
    const data = await apiJson(`/api/b/tongue-diagnosis/tasks/${taskId}/sync-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    p.tongueTask = data.task || p.tongueTask
    p.tongueH5Url = p.tongueTask?.h5_url || p.tongueH5Url || ''
    p.tongueMobileOpenUrl = p.tongueTask?.mobile_open_url || p.tongueMobileOpenUrl || ''
    addManagementLog('同步舌诊结果', p.tongueTask?.status || '')
    toast?.show(p.tongueTask?.tongue_feature ? '舌诊结果已同步' : '暂未查询到舌诊报告')
  } catch (e) {
    toast?.show(e.message || '舌诊结果同步失败')
  } finally {
    tongueSyncing.value = false
  }
}

async function removeAsset(type, id) {
  const p = ensurePatientWorkflow(activePatient.value)
  const hit = (p.assets[type] || []).find(x => x.id === id)
  if (type === 'imagingReports' && hit?.backend && p.workspaceRecordId) {
    try {
      await apiJson(`/api/b/records/${p.workspaceRecordId}/imaging-reports/${id}`, { method: 'DELETE' })
    } catch (e) {
      toast?.show(e.message || '删除影像报告失败')
      return
    }
  }
  p.assets[type] = (p.assets[type] || []).filter(x => x.id !== id)
  addManagementLog('删除资料', type)
}

async function regenerateAdviceForActive() {
  const p = ensurePatientWorkflow(activePatient.value)
  adviceGenerating.value = true
  try {
    const previous = p.adviceDraft.content
    if (previous) {
      p.adviceDraft.history = p.adviceDraft.history || []
      p.adviceDraft.history.unshift({
        id: `${Date.now()}-${p.adviceDraft.version}`,
        version: p.adviceDraft.version || 1,
        status: p.adviceDraft.status || 'draft',
        content: previous,
        savedAt: p.adviceDraft.updatedAt || nowText()
      })
    }
    p.adviceDraft.version = (p.adviceDraft.version || 1) + 1
    p.adviceDraft.status = 'draft'
    p.adviceDraft.updatedAt = nowText()
    p.adviceDraft.content = `基于${p.name}当前档案，${p.nodules}建议按${computedRisk.value.level}路径管理。请补充原始影像报告，结合分级、大小、症状、病史进行复核；若分级不清或资料缺失，应优先完善检查资料后再形成最终报告。随访建议：${p.followPlan?.cycle || '6个月'}复查，通过${p.followPlan?.channel || '小程序'}进行提醒和记录。`
    if (p.workspaceReportId) {
      const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: p.adviceDraft.content, preserve_history: true })
      })
      p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
    }
    addManagementLog('再次生成建议草稿', `V${p.adviceDraft.version}`)
  } catch (e) {
    toast?.show(e.message || '再次生成建议失败')
  } finally {
    adviceGenerating.value = false
  }
}

async function saveAdviceDraft() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (!String(p.adviceDraft.content || '').trim()) {
    toast?.show('请先生成或填写建议内容')
    return false
  }
  if (p.workspaceReportId) {
    try {
      const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: p.adviceDraft.content, preserve_history: true })
      })
      p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
    } catch (e) {
      toast?.show(e.message || '保存建议草稿失败')
      return false
    }
  }
  p.adviceDraft.status = 'draft'
  p.adviceDraft.updatedAt = nowText()
  addManagementLog('保存建议草稿', `V${p.adviceDraft.version || 1}`)
  return true
}

async function submitAdviceReview() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (!String(p.adviceDraft.content || '').trim()) {
    toast?.show('请先生成或填写建议内容')
    return
  }
  if (p.workspaceReportId) {
    try {
      const saved = await saveAdviceDraft()
      if (!saved) return
      const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice/submit-review`, { method: 'POST' })
      p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
    } catch (e) {
      toast?.show(e.message || '提交建议审核失败')
      return
    }
  }
  p.adviceDraft.status = 'reviewing'
  p.adviceDraft.updatedAt = nowText()
  p.stage = 'review'
  addManagementLog('提交建议审核', `V${p.adviceDraft.version || 1}`)
}

async function approveAdviceToFinal() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (p.adviceDraft.status !== 'reviewing') return
  if (p.workspaceReportId) {
    try {
      const data = await apiJson(`/api/b/reports/${p.workspaceReportId}/advice/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: p.adviceDraft.content, summary: p.report?.summary || '' })
      })
      p.adviceDraft = normalizeAdvicePayload(data.advice, p.adviceDraft)
    } catch (e) {
      toast?.show(e.message || '审核通过失败')
      return
    }
  }
  p.adviceDraft.status = 'archived'
  p.finalReport = {
    content: p.adviceDraft.content,
    archivedAt: nowText(),
    version: p.adviceDraft.version || 1
  }
  p.stage = 'plan'
  addManagementLog('审核通过并写入最终报告', `V${p.adviceDraft.version || 1}`)
  rpLoaded.value = false
  await hydratePatientWorkspace(p)
}

async function saveFollowPlan() {
  const p = ensurePatientWorkflow(activePatient.value)
  if (!p?._apiId) {
    toast?.show('请先保存患者信息后再保存任务配置')
    return
  }
  try {
    const data = await apiJson(`/api/b/patients/${p._apiId}/follow-ups`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        follow_up_type: p.followPlan.channel || '小程序',
        follow_up_date: formatDateInput(new Date()),
        content: p.followPlan.note || '',
        next_follow_up_date: nextFollowDateByCycle(p.followPlan.cycle),
        next_follow_up_action: `${p.followPlan.cycle || '6个月'}复查；${p.followPlan.channel || '小程序'}触达`
      })
    })
    p.followPlan.savedAt = data.created_at || nowText()
    p.followPlan.backendId = data.id
    p.stage = p.finalReport?.content ? 'follow' : 'plan'
    addManagementLog('保存任务配置', `${p.followPlan.cycle} · ${p.followPlan.channel}`)
    toast?.show('任务配置已保存')
  } catch (e) {
    toast?.show(e.message || '保存任务配置失败')
  }
}

watch(
  () => [subTab.value, planPatients.value.length],
  () => {
    if (subTab.value !== 'followup-plan') return
    const list = planPatients.value || []
    if (!list.length) return
    if (!list.some((p) => p.id === activePatientId.value)) activePatientId.value = list[0].id
    if (!(followTasks.value || []).length) {
      const seeded = list.filter((p) => p?.planTask).slice(0, 8).flatMap((p) => previewTasksFromPatient(p))
      followTasks.value = seeded
      if (seeded[0]) selectTask(seeded[0].id)
    }
  },
  { immediate: true }
)

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
    if (tab === 'review') {
      rpLoaded.value = false
      loadReports()
    }
  },
  { immediate: true }
)

const midTitle = computed(() => {
  const map = {
    queue: '闭环处置工作台',
    record: '患者建档',
    review: isCheckupScenario.value ? '体检报告确认' : '健康报告审核',
    follow: '任务执行'
  }
  return map[subTab.value] || '患者管理'
})

const midSub = computed(() => {
  const map = {
    queue: '选中患者后联动闭环时间线与操作区',
    record: '原始报告 / 历史报告 / AI解读摘要',
    review: isCheckupScenario.value ? 'AI体检解读内容经总检确认后推送患者' : 'AI健康管理报告审核通过后才能推送患者',
    follow: '查看已下发任务与打卡记录'
  }
  return map[subTab.value] || ''
})

const rightTitle = computed(() => {
  const map = {
    queue: '下一步动作',
    record: '处置与动作',
    review: '审核与推送',
    follow: '任务执行记录'
  }
  return map[subTab.value] || '操作区'
})

const rightSub = computed(() => {
  const map = {
    queue: '快速跳转各功能区',
    record: '围绕档案与原始报告',
    review: '面向患者推送前最后一道关',
    follow: '提醒与打卡'
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
function goRecord(p = null) {
  recordPatient.value = p?.id ? p : null
  if (p?.id) activePatientId.value = p.id
  setSubTab('record')
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
.pm{height:100%;display:flex;flex-direction:column;overflow:hidden;margin:0}
.pm-shell{flex:1;min-height:0;background:#fff;display:flex;flex-direction:column;overflow:hidden}
.pm-record{flex:1;min-height:0;overflow:auto;background:#f3f6fb;padding:12px}

/* 任务下发页 */
.plan-page{flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden;background:#f3f6fb;padding:12px}
.plan-filter{display:none}
.plan-filter-row{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end}
.plan-filter-actions{margin-left:auto;display:flex;gap:10px;align-items:center}
.chain-strip{display:grid;grid-template-columns:260px minmax(0,1fr) auto;gap:14px;align-items:center;padding:12px 14px;flex-shrink:0}
.chain-eyebrow{font-size:12px;color:#155eef;font-weight:950;margin-bottom:4px}
.chain-title{font-size:14px;color:#0f172a;font-weight:950;line-height:1.45}
.chain-steps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
.chain-step{display:flex;align-items:center;gap:8px;border:1px solid #e6edf7;background:#f8fafc;border-radius:10px;padding:8px 10px;min-width:0}
.chain-step[data-state="done"]{border-color:#bbf7d0;background:#f0fdf4}
.chain-step[data-state="doing"]{border-color:#bfdbfe;background:#eff6ff}
.chain-dot{width:24px;height:24px;border-radius:999px;background:#e2e8f0;color:#334155;display:grid;place-items:center;font-weight:950;font-size:12px;flex-shrink:0}
.chain-step[data-state="done"] .chain-dot{background:#16a34a;color:#fff}
.chain-step[data-state="doing"] .chain-dot{background:#155eef;color:#fff}
.chain-step-title{font-size:12px;color:#0f172a;font-weight:950;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chain-step-sub{font-size:11px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.plan-workbench{flex:1;min-height:0;display:grid;grid-template-columns:280px minmax(0,1fr);gap:12px;overflow:hidden}
.plan-task-list{min-height:0;display:flex;flex-direction:column;overflow:hidden}
.left-search-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;margin-bottom:8px}
.seg-tabs{display:flex;align-items:center;border:1px solid #e6edf7;border-radius:999px;overflow:hidden;background:#fff}
.seg-tab{height:28px;padding:0 12px;border:none;background:transparent;font-weight:950;color:#334155;cursor:pointer}
.seg-tab[data-on="true"]{background:#eef5ff;color:#155eef}
.seg-tab + .seg-tab{border-left:1px solid #e6edf7}

.pat-table{padding:10px 12px;display:flex;flex-direction:column;gap:10px;min-height:0;overflow:hidden}
.pat-rows{display:grid;gap:8px;overflow:auto;min-height:0;flex:1;scrollbar-width:thin}
.pat-row{display:grid;grid-template-columns:1.1fr 1.6fr .7fr .8fr .7fr;gap:10px;align-items:center;border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 10px}
.pat-row[data-active="true"]{border-color:#155eef;background:#eef5ff}
.plan-patient-card{grid-template-columns:1fr !important;gap:0 !important;align-items:stretch !important;padding:10px !important}
.pat-main{border:none;background:transparent;text-align:left;cursor:pointer;min-width:0}
.pat-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pat-cell{font-size:12px;color:#334155;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.patient-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}
.patient-card-meta{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:8px;color:#475569;font-size:12px}
.patient-card-actions{display:none}
.task-rows{padding:10px 12px;display:grid;gap:10px;overflow:auto;min-height:0}
.task-row{position:relative;border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 10px;text-align:left;cursor:pointer}
.task-row.active{border-color:#155eef;background:#eef5ff}
.tr-top{display:flex;align-items:center;justify-content:space-between;gap:8px}
.tr-sub{margin-top:4px;font-size:12px;line-height:1.5;color:#334155}
.tr-meta{margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.tr-ck{position:absolute;right:10px;bottom:10px}
.plan-task-detail{min-height:0;display:flex;flex-direction:column;overflow:hidden}
.plan-task-detail .pad{overflow:auto;flex:1;min-height:0}
.plan-editor-head{align-items:flex-start}
.plan-detail-title{min-width:0;flex:1}
.plan-empty{border:1px dashed #cbd5e1;background:#fff;border-radius:12px;padding:26px;display:grid;gap:6px;color:#64748b}
.plan-empty b{color:#0f172a;font-size:15px}
.plan-patient-hero{border:1px solid #cfe0ff;background:#fff;border-radius:12px;padding:10px 12px;display:flex;align-items:center;gap:10px;margin-bottom:10px}
.patient-avatar-sm{width:34px;height:34px;border-radius:999px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-weight:950;flex-shrink:0}
.hero-info{display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:12px;color:#334155}
.hero-info b{font-size:14px;color:#0f172a}
.plan-step-strip{display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap}
.step-chip{height:28px;border:1px solid #e6edf7;background:#fff;border-radius:999px;padding:0 10px;display:inline-flex;align-items:center;gap:6px;color:#64748b;font-size:12px;font-weight:900}
.step-chip span{width:18px;height:18px;border-radius:999px;background:#e2e8f0;color:#334155;display:grid;place-items:center;font-size:11px}
.step-chip[data-state="done"]{border-color:#bbf7d0;background:#f0fdf4;color:#15803d}
.step-chip[data-state="done"] span{background:#16a34a;color:#fff}
.step-chip[data-state="doing"]{border-color:#bfdbfe;background:#eff6ff;color:#155eef}
.step-chip[data-state="doing"] span{background:#155eef;color:#fff}
.plan-flow-card{border:1px solid #e6edf7;background:#fbfdff;border-radius:12px;padding:10px 12px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin-bottom:10px}
.flow-node{display:flex;align-items:center;justify-content:center;gap:8px;min-height:48px;border-radius:10px;background:#fff;border:1px solid #eef2f7;color:#64748b;font-weight:950;font-size:12px;padding:6px 8px;min-width:0}
.flow-node[data-state="done"]{border-color:#bbf7d0;background:#f0fdf4;color:#15803d}
.flow-node[data-state="doing"]{border-color:#bfdbfe;background:#eff6ff;color:#155eef}
.flow-node-dot{width:20px;height:20px;border-radius:999px;background:currentColor;color:#fff;display:grid;place-items:center;font-size:11px}
.flow-node-copy{min-width:0}
.flow-node-title{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.flow-node-sub{font-size:10px;font-weight:800;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}
.patient-summary-card{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.patient-summary-main{display:grid;gap:4px;min-width:0}
.patient-summary-title{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.patient-summary-title b{font-size:15px;color:#0f172a}
.patient-summary-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:12px;color:#64748b}
.plan-editor-stack{display:grid;gap:12px}
.detail-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(360px,.85fr);gap:12px;align-items:start}
.detail-grid .detail-card:nth-child(3){grid-column:1/-1}
.detail-card{border:1px solid #e6edf7;border-radius:12px;background:#fff;padding:12px}
.detail-title{font-weight:950;color:#0f172a;margin-bottom:6px}
.detail-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:10px}
.detail-sub{font-size:12px;margin-bottom:10px}
.recommend-box{border:1px solid #cfe0ff;background:#f8fbff;border-radius:12px;padding:10px 12px;margin-bottom:10px}
.recommend-title{font-size:12px;color:#334155;font-weight:850;line-height:1.5}
.recommend-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.template-choice-list{display:grid;gap:8px;grid-template-columns:repeat(2,minmax(0,1fr))}
.template-choice{border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 12px;text-align:left;display:grid;gap:5px;cursor:pointer}
.template-choice.active{border-color:#155eef;background:#eff6ff}
.template-choice-head{display:flex;align-items:center;justify-content:space-between;gap:8px;min-width:0}
.template-choice-title{font-weight:950;color:#0f172a}
.template-choice-meta,.template-choice-desc{font-size:12px;color:#64748b;line-height:1.5}
.plan-preview-grid{display:grid;grid-template-columns:1fr;gap:12px}
.preview-list{display:grid;gap:8px}
.preview-row{display:grid;grid-template-columns:22px minmax(0,1fr) 44px;gap:8px;align-items:center;border:1px solid #eef2f7;background:#fbfdff;border-radius:10px;padding:8px 10px}
.preview-no{width:18px;height:18px;border-radius:999px;background:#16a34a;color:#fff;display:grid;place-items:center;font-size:11px;font-weight:950}
.preview-main{display:grid;gap:2px;min-width:0}
.preview-main b{font-size:12px;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.preview-main span{font-size:11px;color:#64748b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
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
.confirm-bar span{display:block;color:#64748b;font-size:12px}
.confirm-actions{display:flex;align-items:center;gap:8px;flex-shrink:0}
.delivery-card{border:1px solid #e6edf7;background:#fff;border-radius:12px;padding:10px 12px;display:grid;gap:8px;font-size:12px;color:#334155;font-weight:850}
.detail-top{display:flex;gap:12px;align-items:flex-start;justify-content:space-between}
.detail-top-title{font-size:13px;color:#0f172a;font-weight:950;display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.detail-top-sub{font-size:12px;margin-top:4px}
.detail-top-actions{display:flex;gap:8px;align-items:center}
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
.tbl-act.danger{color:#dc2626}
.tbl-act.danger:hover{color:#b91c1c}
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

/* ── 旧任务预览工作台（当前主入口已隐藏） ── */
.follow-workbench{flex:1;min-height:0;display:grid;grid-template-columns:minmax(260px,300px) minmax(420px,.95fr) minmax(420px,1.05fr);gap:10px;padding:12px;overflow:hidden}
.follow-workbench .follow-stats-bar,.follow-workbench .follow-compose-head,.follow-workbench .follow-phone-col,.follow-workbench .follow-ctrl-col{display:none}
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
.follow-stats-bar{display:none}
.follow-stat-item{flex:1;text-align:center;min-width:0}
.follow-stat-div{width:1px;height:32px;background:#e6edf7;flex-shrink:0;margin:0 4px}
.follow-stat-label{font-size:11px;color:#64748b;font-weight:600;white-space:nowrap}
.follow-stat-value{font-size:20px;font-weight:800;margin-top:2px;line-height:1}
.follow-compose-head{grid-column:2;grid-row:1;display:grid;grid-template-columns:1fr;gap:12px;align-items:center;padding:12px 14px;min-height:0}
.follow-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
.follow-flow-step{border:1px solid #e6edf7;background:#f8fafc;border-radius:10px;padding:8px 8px;text-align:center;min-width:0}
.follow-flow-ico{width:30px;height:30px;border-radius:10px;background:#eef5ff;color:#155eef;display:grid;place-items:center;margin:0 auto 6px;font-weight:950;font-size:12px}
.follow-flow-title{font-size:12px;color:#0f172a;font-weight:950;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.follow-flow-sub{font-size:11px;color:#64748b;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.follow-patient-col{grid-column:1;grid-row:1 / span 2;display:flex;flex-direction:column;min-height:0;background:#fff;border:1px solid #e6edf7;border-radius:10px;overflow:hidden}

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

.follow-phone-col{grid-column:2;grid-row:2;display:flex;flex-direction:column;align-items:center;gap:8px;min-width:0;min-height:0;overflow-y:auto;padding:0 0 16px 0;scrollbar-width:thin;background:#fff;border:1px solid #e6edf7;border-radius:10px;padding-top:12px}
.follow-ctrl-col{grid-column:3;grid-row:1 / span 2;display:flex;flex-direction:column;gap:10px;min-width:0;min-height:0;overflow-y:auto;padding:0;scrollbar-width:thin}

/* 手机外壳（中间列，保持真实比例） */
.device-outer-lg{position:relative;width:330px;flex-shrink:0;align-self:center;margin-top:12px}
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
.strategy-box,.content-config,.generated-panel{background:#fff;border:1px solid #e6edf7;border-radius:10px;padding:10px 12px;box-shadow:0 4px 12px rgba(15,23,42,.04)}
.strategy-title{font-size:12px;font-weight:950;color:#0f172a;margin-bottom:8px}
.strategy-modules{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.strategy-module{position:relative;border:1px solid #e6edf7;border-radius:10px;background:#fff;min-height:72px;padding:8px 6px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;cursor:pointer}
.strategy-module.active{border-color:#155eef;background:#eef5ff;box-shadow:0 0 0 2px rgba(21,94,239,.10)}
.strategy-module b{font-size:11px;color:#0f172a;line-height:1.2}
.strategy-module em{position:absolute;top:5px;right:5px;font-style:normal;font-size:10px;color:#16a34a;font-weight:950}
.strategy-current{margin-top:8px;border-top:1px solid #eef2f7;padding-top:8px;font-size:12px;color:#334155;line-height:1.5}
.config-list{display:grid;gap:8px}
.config-row{display:grid;grid-template-columns:14px minmax(0,1fr) auto;gap:8px;align-items:center;border:1px solid #eef2f7;background:#fbfdff;border-radius:10px;padding:8px 8px}
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

@media (max-width: 1500px){
  .follow-workbench{grid-template-columns:minmax(240px,280px) minmax(320px,.85fr) minmax(380px,1fr)}
  .device-outer-lg{width:300px}
  .follow-flow-step{padding:7px 6px}
  .follow-bottom-actions{grid-template-columns:repeat(2,minmax(0,1fr))}
}

@media (max-width: 1280px){
  .follow-workbench{grid-template-columns:250px minmax(0,1fr);grid-template-rows:auto auto minmax(420px,1fr)}
  .follow-patient-col{grid-column:1;grid-row:1 / span 3}
  .follow-compose-head{grid-column:2;grid-row:1}
  .follow-phone-col{grid-column:2;grid-row:2;min-height:430px}
  .follow-ctrl-col{grid-column:2;grid-row:3;min-height:0}
}
.assist-state{font-size:11px;font-weight:950;border-radius:999px;padding:3px 10px;background:#f1f5f9;color:#64748b;white-space:nowrap}
.assist-state[data-tone="g"]{background:#ecfff3;color:#14843b}
.assist-state[data-tone="o"]{background:#fff7ed;color:#c2410c}


/* 手机预览区 */
.phone-preview-wrap{display:flex;flex-direction:column;gap:8px;align-items:center;flex-shrink:0}
.phone-preview-label{width:min(520px,100%);display:flex;justify-content:space-between;align-items:center;padding:0 12px;font-size:12px;font-weight:850;color:#334155}

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
.rp-row-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
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
.rp-audit-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.rp-audit-block{min-width:0}
.rp-audit-label{font-size:12px;font-weight:750;color:#334155;margin-bottom:4px}
.rp-audit-ta{width:100%;border:1px solid #d9e2ef;border-radius:6px;padding:8px 10px;font-size:13px;line-height:1.6;color:#1e293b;resize:vertical;outline:none;font-family:inherit}
.rp-audit-ta:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.1)}
.rp-audit-state{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:12px;padding:10px 12px;border:1px solid #e6edf7;border-radius:10px;background:#f8fafc}
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
.wecom-modal{width:min(560px,96vw)}
.wecom-form-grid{display:grid;gap:12px}
.wecom-form-hint{margin-top:12px;border:1px solid #eef2f7;border-radius:10px;background:#fbfdff;padding:10px 12px;color:#64748b;font-size:12px;line-height:1.7}
.wecom-modal-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:16px}
@media (max-width: 720px){.rp-audit-grid{grid-template-columns:1fr}}

/* 患者全流程详情工作台 */
.patient-workspace{height:100%;min-height:0;overflow:auto;background:#f6f8fb;padding:14px;display:flex;flex-direction:column;gap:12px;scroll-padding-top:14px}
.workspace-hero{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;flex-shrink:0;min-height:64px}
.workspace-id{display:flex;align-items:center;gap:12px;min-width:0}
.workspace-name{font-size:18px;font-weight:950;color:#0f172a}
.workspace-sub{font-size:12px;color:#64748b;margin-top:4px}
.workspace-badges{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.workspace-flow{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;padding:10px 12px;flex-shrink:0;min-height:64px;box-sizing:border-box}
.workspace-flow-node{min-height:42px;border:1px solid #e6edf7;border-radius:10px;background:#fff;display:flex;align-items:center;justify-content:center;gap:8px;font-size:12px;font-weight:950;color:#64748b;line-height:1.2}
.workspace-flow-node[data-state="done"]{background:#ecfdf5;border-color:#bbf7d0;color:#047857}
.workspace-flow-node[data-state="current"]{background:#eff6ff;border-color:#bfdbfe;color:#1d4ed8}
.flow-dot{width:20px;height:20px;border-radius:999px;background:#f1f5f9;display:grid;place-items:center;font-size:11px}
.workspace-grid{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:12px;align-items:start}
.workspace-main{display:flex;flex-direction:column;gap:12px;min-width:0}
.workspace-side{display:flex;flex-direction:column;gap:12px;min-width:0}
.flow-section,.side-flow-card{padding:14px}
.section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.section-title{font-weight:950;color:#0f172a;font-size:14px}
.section-sub{font-size:12px;color:#64748b;margin-top:4px}
.section-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
.profile-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.profile-note{margin-top:10px}
.record-report-card{margin-top:10px;border:1px solid #dbeafe;background:#eff6ff;border-radius:10px;padding:10px 12px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.record-report-card b{display:block;color:#1e3a8a;font-size:12px;margin-bottom:3px}
.record-report-card span{display:block;color:#334155;font-size:12px}
.workspace-summary-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:10px}
.workspace-summary-card{border:1px solid #e6edf7;border-radius:10px;background:#fff;padding:10px 12px;min-width:0}
.workspace-summary-card span{display:block;font-size:12px;color:#64748b;font-weight:850}
.workspace-summary-card b{display:block;font-size:22px;color:#0f172a;line-height:1.1;margin-top:4px}
.workspace-summary-card em{display:block;font-style:normal;font-size:11px;color:#94a3b8;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.profile-field{display:flex;flex-direction:column;gap:5px;font-size:12px;color:#64748b;font-weight:850;min-width:0}
.profile-field input,.profile-field select,.profile-field textarea{width:100%;box-sizing:border-box;border:1px solid #dbe5f2;border-radius:9px;background:#fff;padding:8px 10px;color:#0f172a;font-size:13px;font-weight:650}
.profile-field input[readonly],.profile-field textarea[readonly]{background:#f8fafc;color:#334155}
.profile-field textarea{min-height:76px;resize:vertical;line-height:1.6}
.profile-field.wide{grid-column:1/-1}
.upload-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;margin-top:12px}
.upload-panel{border:1px solid #e6edf7;border-radius:12px;background:#fbfdff;padding:12px;min-width:0}
.upload-title{font-weight:950;color:#0f172a}
.upload-sub{font-size:12px;color:#64748b;margin:4px 0 10px;line-height:1.5}
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
.version-list{display:grid;gap:6px;margin-top:10px}
.version-row{display:grid;grid-template-columns:52px 90px 1fr;gap:8px;align-items:center;border:1px solid #eef2f7;border-radius:9px;background:#fff;padding:8px 10px;font-size:12px;color:#64748b}
.version-row b{color:#0f172a}
.final-report-box{border:1px solid #bbf7d0;border-radius:12px;background:#f0fdf4;padding:12px}
.final-report-meta{font-size:12px;color:#047857;font-weight:950;margin-bottom:8px}
.final-report-box p{margin:0;color:#0f172a;line-height:1.7;font-size:13px}
.follow-plan-box{display:grid;gap:10px;margin-top:10px}
.primary.full{width:100%}
.mgmt-log{display:grid;gap:8px;margin-top:10px;max-height:280px;overflow:auto}
.mgmt-log-row{border-left:3px solid #bfdbfe;background:#f8fafc;border-radius:8px;padding:8px 10px}
.mgmt-log-row b{display:block;font-size:12px;color:#0f172a}
.mgmt-log-row span{display:block;font-size:11px;color:#94a3b8;margin-top:2px}
.mgmt-log-row p{margin:5px 0 0;font-size:12px;color:#64748b;line-height:1.5}
.integration-note{font-size:12px;color:#64748b;line-height:1.7;margin-top:8px;background:#f8fafc;border:1px solid #eef2f7;border-radius:10px;padding:10px}
.chain-list{display:grid;gap:8px;margin-top:10px}
.chain-row{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;border:1px solid #eef2f7;border-radius:10px;background:#fff;padding:9px 10px;min-width:0}
.chain-row[data-alert="true"]{background:#fff1f2;border-color:#fecdd3}
.chain-row b{display:block;font-size:12px;color:#0f172a;line-height:1.35}
.chain-row span{display:block;font-size:11px;color:#64748b;margin-top:3px;line-height:1.4}
.chain-row em{font-style:normal;font-size:11px;color:#94a3b8;white-space:nowrap}
.btn.full{width:100%}
.status-tag[data-s="draft"]{background:#f8fafc;color:#475569}
.status-tag[data-s="reviewing"]{background:#eff6ff;color:#1d4ed8}
.status-tag[data-s="approved"],.status-tag[data-s="archived"]{background:#ecfdf5;color:#047857}
@media (max-width: 1180px){
  .workspace-grid{grid-template-columns:1fr}
  .workspace-flow{grid-template-columns:repeat(3,minmax(0,1fr))}
  .workspace-summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  .risk-layers{grid-template-columns:repeat(2,minmax(0,1fr))}
}
</style>
