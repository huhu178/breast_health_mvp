<template>
  <div class="pm">
    <section class="pm-shell" aria-label="患者管理三栏工作台">
      <!-- tab=queue：总览（对齐你截图的双栏布局） -->
      <div v-if="subTab === 'queue'" class="pm-overview">
        <!-- 左：患者任务队列（大表格） -->
        <section class="card overview-left">
          <div class="card-head">
            <div class="card-title">患者任务队列</div>
            <div class="panel-tools">
              <input class="search" placeholder="姓名/手机号" />
              <select class="stage-select" :value="activeStage" @change="setStage($event.target.value)">
                <option v-for="t in stageTabs" :key="t.key" :value="t.key">{{ t.label }}</option>
              </select>
              <button class="primary" type="button" @click="goRecord">+ 新建档案</button>
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
                <tr
                  v-for="p in filteredQueue"
                  :key="p.id"
                  class="q-row"
                  :class="{ active: p.id === activePatientId }"
                  @click="activePatientId = p.id"
                >
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

        <!-- 右：患者操作面板 -->
        <aside class="overview-right">
          <!-- 合并面板：患者详情 / 标签 / 下一步 / 流程 / 操作 / 动态 -->
          <section class="card side-panel">
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

      <!-- record tab：嵌入建档表单 -->
      <div v-else-if="subTab === 'record'" class="pm-record">
        <RecordView :embedded="true" @back="backToQueue" />
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
                  <template v-for="(msg, i) in currentAssistantChat" :key="i">
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
            </div>
          </section>
        </div>
      </div>

      <!-- review tab：健康报告（报告处理主页面） -->
      <div v-else-if="subTab === 'review'" class="rp-page">

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
            <div class="rp-filter-item">
              <div class="rp-filter-label">处理状态</div>
              <select class="rp-filter-select" v-model="rpStatus">
                <option value="">待处理等 6 种</option>
                <option>待处理</option>
                <option>AI解析中</option>
                <option>待生成报告</option>
                <option>待医生复核</option>
                <option>已完成</option>
                <option>异常报告</option>
              </select>
            </div>
            <div class="rp-filter-actions">
              <button class="btn" type="button" @click="rpSearch='';rpSource='';rpNodule='';rpRisk='';rpStatus=''">重置</button>
              <button class="primary" type="button">查询</button>
              <button class="primary" type="button" style="display:flex;align-items:center;gap:5px">
                <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                上传报告
              </button>
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
                    <th style="width:60px">来源</th>
                    <th style="width:72px">报告类型</th>
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
                    <td class="muted">{{ r.source }}</td>
                    <td class="muted">{{ r.reportType }}</td>
                    <td><span class="nodule-tag" :data-type="r.noduleKey">{{ r.nodules }}</span></td>
                    <td class="muted" style="font-size:11px">{{ r.uploadAt }}</td>
                    <td><span class="rp-status-tag" :data-s="r.aiStatus">{{ r.aiStatus }}</span></td>
                    <td><span class="pill" :data-tone="r.riskTone">{{ r.risk }}</span></td>
                    <td class="muted">{{ r.owner }}</td>
                    <td>
                      <div style="display:flex;gap:4px">
                        <button class="mini-link" type="button">查看</button>
                        <button class="mini-link" type="button">处理</button>
                        <button class="mini-link" type="button">复核</button>
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
                  <button class="primary" type="button">处理报告</button>
                  <button class="btn" type="button">发起患者</button>
                  <button class="btn" type="button">推送患者</button>
                  <button class="btn" type="button">创建随访任务</button>
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
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import RecordView from './RecordView.vue'

const router = useRouter()
const route = useRoute()

const activeStage = ref('all')
const activePatientId = ref('p1')
const followPatientId = ref('p1')
const followSearch = ref('')
const followRiskFilter = ref('')
const followStageFilter = ref('')
const subTab = ref('queue')
const showAllTimeline = ref(false)
const reviewReject = ref(false)
const activeAssistant = ref('hlp')

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
  return queue.value.filter(p => {
    const s = followSearch.value.trim().toLowerCase()
    if (s && !p.name.toLowerCase().includes(s) && !p.phoneMasked.includes(s)) return false
    if (followRiskFilter.value && p.risk !== followRiskFilter.value) return false
    if (followStageFilter.value && statusKey(p) !== followStageFilter.value) return false
    return true
  })
})

const currentAssistantChat = computed(() => currentAssistant.value?.chat || [])

const rpSearch = ref('')
const rpSource = ref('')
const rpNodule = ref('')
const rpRisk = ref('')
const rpStatus = ref('')
const rpActiveId = ref(1)

const rpList = ref([
  { id: 1, name: '张*国', gender: '男', age: 56, phone: '138****5678', source: '门诊', reportType: 'CT报告', nodules: '肺部合并乳腺结节', noduleKey: 'combo', uploadAt: '2026-04-23 08:15', aiStatus: '解析完成', risk: '中高风险', riskTone: 'o', owner: '李医生',
    summary: '胸部CT提示右上肺见约8mm磨玻璃结节，边界尚清，建议3个月复查；左乳外上象限见结节影，建议进一步乳腺超声评估。',
    aiFields: { site: '肺部/乳腺', count: 2, size: '8mm', feature: '磨玻璃', birads: '3类', advice: '随访复查' },
    noduleTags: ['肺部结节', '乳腺结节', '肺部合并乳腺结节'],
    reportStatus: '待生成',
    flow: [
      { label: '上传报告', time: '04-23 08:15', done: true, cur: false },
      { label: 'AI解析', time: '04-23 08:16', done: true, cur: false },
      { label: '结构化结果', time: '04-23 08:17', done: true, cur: false },
      { label: '生成健康报告', time: '当前步骤', done: false, cur: true },
      { label: '送医生复核', time: '待处理', done: false, cur: false },
    ]
  },
  { id: 2, name: '李*华', gender: '女', age: 48, phone: '159****2468', source: '体检中心', reportType: '超声报告', nodules: '甲状腺结节', noduleKey: 'thyroid', uploadAt: '2026-04-23 08:05', aiStatus: 'AI解析中', risk: '低风险', riskTone: 'g', owner: '王医生',
    summary: '甲状腺超声示右叶见约5mm低回声结节，边界清晰，TI-RADS 3类，建议6个月随访复查。',
    aiFields: { site: '甲状腺', count: 1, size: '5mm', feature: '低回声', birads: 'TI-RADS 3类', advice: '6个月随访' },
    noduleTags: ['甲状腺结节'],
    reportStatus: '待生成',
    flow: [
      { label: '上传报告', time: '04-23 08:05', done: true, cur: false },
      { label: 'AI解析', time: '进行中', done: false, cur: true },
      { label: '结构化结果', time: '待处理', done: false, cur: false },
      { label: '生成健康报告', time: '待处理', done: false, cur: false },
      { label: '送医生复核', time: '待处理', done: false, cur: false },
    ]
  },
  { id: 3, name: '王*明', gender: '男', age: 62, phone: '136****1123', source: '门诊', reportType: 'CT报告', nodules: '肺部结节', noduleKey: 'lung', uploadAt: '2026-04-23 07:58', aiStatus: '待处理', risk: '高风险', riskTone: 'r', owner: '未分派',
    summary: '胸部CT示左上肺见约12mm实性结节，边缘不规则，建议进一步PET-CT检查排除恶性。',
    aiFields: { site: '肺部', count: 1, size: '12mm', feature: '实性', birads: 'Lung-RADS 4B', advice: '进一步检查' },
    noduleTags: ['肺部结节'],
    reportStatus: '待生成',
    flow: [
      { label: '上传报告', time: '04-23 07:58', done: true, cur: false },
      { label: 'AI解析', time: '待处理', done: false, cur: true },
      { label: '结构化结果', time: '待处理', done: false, cur: false },
      { label: '生成健康报告', time: '待处理', done: false, cur: false },
      { label: '送医生复核', time: '待处理', done: false, cur: false },
    ]
  },
  { id: 4, name: '赵*丽', gender: '女', age: 45, phone: '186****3344', source: '体检中心', reportType: '体检报告', nodules: '三合并结节', noduleKey: 'triple', uploadAt: '2026-04-23 07:45', aiStatus: '异常报告', risk: '高风险', riskTone: 'r', owner: '李医生',
    summary: '体检报告提示肺部、甲状腺、乳腺均发现结节，建议分别进行专科评估，优先处理肺部高风险结节。',
    aiFields: { site: '肺/甲/乳', count: 3, size: '10mm', feature: '混合', birads: '多类型', advice: '专科评估' },
    noduleTags: ['肺部结节', '甲状腺结节', '乳腺结节'],
    reportStatus: '待生成',
    flow: [
      { label: '上传报告', time: '04-23 07:45', done: true, cur: false },
      { label: 'AI解析', time: '04-23 07:46', done: true, cur: false },
      { label: '结构化结果', time: '异常标记', done: false, cur: true },
      { label: '生成健康报告', time: '待处理', done: false, cur: false },
      { label: '送医生复核', time: '待处理', done: false, cur: false },
    ]
  },
  { id: 5, name: '陈*强', gender: '男', age: 59, phone: '137****8899', source: '门诊', reportType: 'CT报告', nodules: '肺部结节', noduleKey: 'lung', uploadAt: '2026-04-23 07:30', aiStatus: '待生成报告', risk: '中风险', riskTone: 'o', owner: '刘医生',
    summary: '胸部CT示右下肺见约6mm磨玻璃结节，边界清晰，Lung-RADS 3类，建议3个月随访。',
    aiFields: { site: '肺部', count: 1, size: '6mm', feature: '磨玻璃', birads: 'Lung-RADS 3类', advice: '3个月随访' },
    noduleTags: ['肺部结节'],
    reportStatus: '待生成',
    flow: [
      { label: '上传报告', time: '04-23 07:30', done: true, cur: false },
      { label: 'AI解析', time: '04-23 07:31', done: true, cur: false },
      { label: '结构化结果', time: '04-23 07:32', done: true, cur: false },
      { label: '生成健康报告', time: '当前步骤', done: false, cur: true },
      { label: '送医生复核', time: '待处理', done: false, cur: false },
    ]
  },
  { id: 6, name: '刘*芳', gender: '女', age: 53, phone: '139****6677', source: '门诊', reportType: '超声报告', nodules: '乳腺结节', noduleKey: 'breast', uploadAt: '2026-04-23 07:18', aiStatus: '解析完成', risk: '低风险', riskTone: 'g', owner: '王医生',
    summary: '乳腺超声示左乳外上象限见约7mm低回声结节，边界清晰，BI-RADS 3类，建议6个月随访。',
    aiFields: { site: '乳腺', count: 1, size: '7mm', feature: '低回声', birads: 'BI-RADS 3类', advice: '6个月随访' },
    noduleTags: ['乳腺结节'],
    reportStatus: '待生成',
    flow: [
      { label: '上传报告', time: '04-23 07:18', done: true, cur: false },
      { label: 'AI解析', time: '04-23 07:19', done: true, cur: false },
      { label: '结构化结果', time: '04-23 07:20', done: true, cur: false },
      { label: '生成健康报告', time: '当前步骤', done: false, cur: true },
      { label: '送医生复核', time: '待处理', done: false, cur: false },
    ]
  },
  { id: 7, name: '孙*军', gender: '男', age: 61, phone: '158****9900', source: '体检中心', reportType: '体检报告', nodules: '甲状腺合并乳腺结节', noduleKey: 'combo', uploadAt: '2026-04-23 07:05', aiStatus: 'AI解析中', risk: '中风险', riskTone: 'o', owner: '未分派',
    summary: '体检报告提示甲状腺右叶及左乳均见结节，建议分别进行超声精查。',
    aiFields: { site: '甲状腺/乳腺', count: 2, size: '9mm', feature: '低回声', birads: '多类型', advice: '超声精查' },
    noduleTags: ['甲状腺结节', '乳腺结节'],
    reportStatus: '待生成',
    flow: [
      { label: '上传报告', time: '04-23 07:05', done: true, cur: false },
      { label: 'AI解析', time: '进行中', done: false, cur: true },
      { label: '结构化结果', time: '待处理', done: false, cur: false },
      { label: '生成健康报告', time: '待处理', done: false, cur: false },
      { label: '送医生复核', time: '待处理', done: false, cur: false },
    ]
  },
  { id: 8, name: '周*萍', gender: '女', age: 47, phone: '150****2211', source: '门诊', reportType: '钼靶报告', nodules: '乳腺结节', noduleKey: 'breast', uploadAt: '2026-04-23 06:50', aiStatus: '待医生复核', risk: '中风险', riskTone: 'o', owner: '李医生',
    summary: '钼靶报告示右乳外上象限见约8mm高密度结节，边缘清晰，BI-RADS 3类，建议超声进一步评估。',
    aiFields: { site: '乳腺', count: 1, size: '8mm', feature: '高密度', birads: 'BI-RADS 3类', advice: '超声评估' },
    noduleTags: ['乳腺结节'],
    reportStatus: '待审核',
    flow: [
      { label: '上传报告', time: '04-23 06:50', done: true, cur: false },
      { label: 'AI解析', time: '04-23 06:51', done: true, cur: false },
      { label: '结构化结果', time: '04-23 06:52', done: true, cur: false },
      { label: '生成健康报告', time: '04-23 06:53', done: true, cur: false },
      { label: '送医生复核', time: '当前步骤', done: false, cur: true },
    ]
  },
])

const rpFilteredList = computed(() => {
  return rpList.value.filter(r => {
    if (rpSearch.value && !r.name.includes(rpSearch.value) && !r.phone.includes(rpSearch.value)) return false
    if (rpSource.value && r.source !== rpSource.value) return false
    if (rpRisk.value && r.risk !== rpRisk.value) return false
    if (rpStatus.value && r.aiStatus !== rpStatus.value) return false
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
      { label: '审核报告', primary: true, onClick: () => (subTab.value = 'review') },
      { label: '退回修改', primary: false, onClick: () => toast?.show('退回修改（示意）') },
    ]
  }
  if (k === 'plan') {
    return [{ label: '制定随访计划', primary: true, onClick: () => toast?.show('制定随访计划（示意）') }]
  }
  if (k === 'follow') {
    return [
      { label: '查看随访记录', primary: true, onClick: () => (subTab.value = 'follow') },
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
  if (k === 'gen') return (subTab.value = 'record')
  if (k === 'review') return (subTab.value = 'review')
  if (k === 'plan') return toast?.show('制定随访计划（示意）')
  return (subTab.value = 'follow')
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

const subTabs = [
  { key: 'queue', label: '患者队列' },
  { key: 'record', label: '档案与报告' },
  { key: 'review', label: '健康报告审核' },
  { key: 'follow', label: 'AI助手随访' },
  { key: 'abnormal', label: '异常与复查' }
]

const allowedSubTabs = new Set(subTabs.map((t) => t.key))

watch(
  () => route.query.tab,
  (tab) => {
    const key = typeof tab === 'string' ? tab : ''
    if (allowedSubTabs.has(key)) subTab.value = key
  },
  { immediate: true }
)

watch(
  () => subTab.value,
  (key) => {
    if (route.name !== 'patient') return
    if (route.query.tab === key) return
    router.replace({ query: { ...route.query, tab: key } })
  },
  { immediate: true }
)

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

const queue = ref([
  {
    id: 'p1',
    name: '王先生',
    gender: '男',
    age: 58,
    phoneMasked: '138****5678',
    source: '门诊',
    owner: '健康管理师',
    nodules: '肺结节合并甲状腺结节',
    risk: '高风险',
    riskTone: 'r',
    stage: 'review',
    stageLabel: '健康管理报告待审核',
    nextStep: '医生确认后推送患者',
    serviceStatus: '报告待审核',
    report: {
      status: '待审核',
      summary: '肺部磨玻璃结节 8mm，建议 3 个月复查；甲状腺结节 TI-RADS 3 类，建议随访复查。'
    },
    rawReports: [
      { type: 'pdf', name: '20260420_胸部CT报告.pdf', size: '1.32 MB', at: '2026-04-20', state: '已上传', stateTone: 'g' },
      { type: 'zip', name: '胸部CT原始影像(DICOM).zip', size: '256.7 MB', at: '2026-04-20', state: '解析中', stateTone: 'o' },
      { type: 'pdf', name: '20260420_甲状腺超声报告.pdf', size: '0.84 MB', at: '2026-04-20', state: '已上传', stateTone: 'g' }
    ],
    aiReadSummary: '影像提示右上肺磨玻璃结节 8mm，倾向炎性/腺瘤样病变可能；建议 3 个月复查。甲状腺 TI-RADS 3 类，建议随访复查并结合既往对比。',
    reportDoc: {
      title: '健康管理报告（示意）',
      sections: [
        { h: '一、结节概况', p: '本次检查提示肺部磨玻璃结节 8mm，甲状腺结节 TI-RADS 3 类。' },
        { h: '二、风险分层', p: '综合结节大小、形态及患者基础情况，建议按高风险路径随访。' },
        { h: '三、随访建议', p: '建议 3 个月复查胸部 CT；甲状腺建议 6-12 个月复查超声。' },
        { h: '四、生活方式建议', p: '规律作息、控糖控盐、适度有氧运动；如出现持续咳嗽/胸痛等症状及时就医。' }
      ]
    },
    auditTrail: [
      { at: '08:18', by: 'AI', action: '生成健康管理报告', note: '生成摘要与建议' },
      { at: '08:30', by: '李医生', action: '审核通过', note: '同意推送患者' }
    ],
    chat: [
      { at: '09:20', from: 'AI健康管理师', text: '已为您安排 3 个月复查提醒，近期如有咳嗽加重请及时就医。' },
      { at: '20:10', from: '患者', text: '最近有点咳嗽，需要马上去医院吗？' },
      { at: '20:12', from: 'AI健康管理师', text: '请确认是否有咳血/胸痛/持续发热等；如有请立即就医，我们也建议安排电话随访。' }
    ],
    followTodos: [
      { title: '复查提醒', state: '已排程', tone: 'g', detail: '3个月复查胸部CT提醒已创建' },
      { title: '饮食建议', state: '待推送', tone: 'o', detail: '控糖食谱与晚餐建议' },
      { title: '运动计划', state: '已推送', tone: 'g', detail: '低强度快走 20min' }
    ],
    abnormal: {
      keywords: ['持续咳嗽', '高风险', '复查逾期'],
      interventions: [
        { at: '20:12', by: 'AI', action: '异常识别', note: '建议人工电话随访' },
        { at: '20:30', by: '健管师', action: '电话随访', note: '已沟通症状与就医建议' }
      ],
      recallPlan: '已创建 3 个月复查提醒（小程序 + 企微 + 短信）',
      recallState: '待回收',
      recallTone: 'o',
      recallHint: '复查报告未回收，建议二次提醒'
    },
    reviewers: '医生 / 药师 / 健管师',
    assistants: [
      { name: 'AI中医药膳师', state: '已启用', stateTone: 'g', todayTask: '晚餐控糖食谱，待推送', response: '未读' },
      { name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '3个月复查提醒，已排程', response: '已读' },
      { name: 'AI药师', state: '待启用', stateTone: 'o', todayTask: '用药核对提醒，待配置', response: '—' },
      { name: 'AI慢病管理师', state: '待启用', stateTone: 'o', todayTask: '合并慢病评估，待配置', response: '—' },
      { name: 'AI心理咨询师', state: '已启用', stateTone: 'o', todayTask: '检后焦虑评估，患者未回复', response: '未回复' },
      { name: 'AI运动康复师', state: '已启用', stateTone: 'g', todayTask: '低强度快走计划，已推送', response: '已读' },
      { name: 'AI健康生活方式规划师', state: '已启用', stateTone: 'g', todayTask: '饮食/作息建议，待推送', response: '未读' },
      { name: 'AI健康福利官', state: '待启用', stateTone: 'o', todayTask: '服务权益提醒，待配置', response: '—' },
      { name: 'AI名医数字分身/AIHLP健康规划师', state: '已启用', stateTone: 'g', todayTask: '阶段性建议（高风险路径）', response: '待人工确认' }
    ],
    timeline: [
      { at: '08:10', tone: 'b', text: '创建患者档案' },
      { at: '08:15', tone: 'b', text: '上传胸部CT报告、甲状腺超声报告', meta: '原始报告已入库，等待解析' },
      { at: '08:18', tone: 'p', text: 'AI生成健康管理报告', meta: '生成摘要与随访建议' },
      { at: '08:30', tone: 'g', text: '健康管理报告审核通过', meta: '待推送患者' },
      { at: '08:35', tone: 'b', text: '推送小程序，企微同步提醒' },
      { at: '09:20', tone: 'p', text: 'AI健康管理师发送复查提醒' },
      { at: '12:00', tone: 'p', text: 'AI中医药膳师推送晚餐控糖食谱' },
      { at: '18:30', tone: 'p', text: 'AI运动康复师推送低强度快走计划' },
      { at: '20:10', tone: 'y', text: '患者反馈“最近有点咳嗽”', meta: '来自企微聊天' },
      { at: '20:12', tone: 'r', text: 'AI识别异常，建议人工电话随访', meta: '异常：持续咳嗽/风险升高' }
    ]
  },
  {
    id: 'p2',
    name: '李女士',
    gender: '女',
    age: 46,
    phoneMasked: '139****2468',
    source: '体检',
    owner: '张医生',
    nodules: '乳腺结节',
    risk: '中风险',
    riskTone: 'o',
    stage: 'upload',
    stageLabel: '原始报告待上传',
    nextStep: '上传体检报告后生成健康管理报告',
    serviceStatus: '待上传报告',
    report: { status: '未生成', summary: '等待上传原始检查/体检报告。' },
    rawReports: [],
    aiReadSummary: '暂无原始报告，无法生成 AI 解读摘要。',
    reportDoc: { title: '健康管理报告（未生成）', sections: [{ h: '提示', p: '请先上传原始检查/体检报告。' }] },
    auditTrail: [{ at: '09:05', by: '系统', action: '建档完成', note: '等待上传报告' }],
    chat: [{ at: '09:08', from: '系统', text: '已提醒上传体检报告，上传后将自动生成健康管理报告。' }],
    followTodos: [{ title: '上传原始报告', state: '待完成', tone: 'o', detail: '体检中心 PDF / 影像 DICOM' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '待创建', recallState: '—', recallTone: 'g', recallHint: '暂无' },
    reviewers: '医生 / 药师 / 健管师',
    assistants: [
      { name: 'AI中医药膳师', state: '待启用', stateTone: 'o', todayTask: '入组后生成食谱建议', response: '—' },
      { name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '完成建档后自动启用随访', response: '—' },
      { name: 'AI药师', state: '待启用', stateTone: 'o', todayTask: '用药史采集与核对', response: '—' },
      { name: 'AI慢病管理师', state: '待启用', stateTone: 'o', todayTask: '慢病风险评估', response: '—' },
      { name: 'AI心理咨询师', state: '待启用', stateTone: 'o', todayTask: '检后焦虑评估', response: '—' },
      { name: 'AI运动康复师', state: '待启用', stateTone: 'o', todayTask: '运动处方生成', response: '—' },
      { name: 'AI健康生活方式规划师', state: '待启用', stateTone: 'o', todayTask: '生活方式建议', response: '—' },
      { name: 'AI健康福利官', state: '待启用', stateTone: 'o', todayTask: '服务权益提醒', response: '—' },
      { name: 'AI名医数字分身/AIHLP健康规划师', state: '待启用', stateTone: 'o', todayTask: '阶段性建议', response: '—' }
    ],
    timeline: [
      { at: '09:05', tone: 'b', text: '创建患者档案' },
      { at: '09:08', tone: 'y', text: '提醒上传体检报告', meta: '短信/企微双通道' }
    ]
  },
  {
    id: 'p3',
    name: '张先生',
    gender: '男',
    age: 62,
    phoneMasked: '137****1357',
    source: '门诊',
    owner: '刘医生',
    nodules: '甲状腺结节',
    risk: '低风险',
    riskTone: 'g',
    stage: 'follow',
    stageLabel: 'AI随访中',
    nextStep: '按计划执行复查提醒与生活方式干预',
    serviceStatus: 'AI随访中',
    report: { status: '已推送', summary: 'TI-RADS 3 类，建议 6-12 个月随访复查。' },
    rawReports: [
      { type: 'pdf', name: '20260318_甲状腺超声报告.pdf', size: '0.62 MB', at: '2026-03-18', state: '已归档', stateTone: 'g' }
    ],
    aiReadSummary: 'TI-RADS 3 类倾向良性，建议 6-12 个月随访复查，并关注结节大小变化。',
    reportDoc: {
      title: '健康管理报告（已推送）',
      sections: [
        { h: '结节概况', p: '甲状腺结节 TI-RADS 3 类，倾向良性。' },
        { h: '随访建议', p: '建议 6-12 个月复查超声；如出现吞咽不适、声音嘶哑等及时就医。' }
      ]
    },
    auditTrail: [{ at: '07:20', by: '张医生', action: '审核通过并推送', note: '小程序已送达' }],
    chat: [
      { at: '07:40', from: 'AI健康管理师', text: '已为您安排 6 个月复查提醒，请按计划复查。' },
      { at: '10:00', from: '患者', text: '问卷已填写，谢谢。' }
    ],
    followTodos: [
      { title: '复查提醒', state: '已排程', tone: 'g', detail: '6个月复查超声提醒' },
      { title: '生活方式建议', state: '已推送', tone: 'g', detail: '本周作息建议' }
    ],
    abnormal: {
      keywords: ['复查提醒'],
      interventions: [{ at: '07:40', by: 'AI', action: '推送提醒', note: '小程序 + 企微' }],
      recallPlan: '已创建 6 个月复查提醒',
      recallState: '进行中',
      recallTone: 'g',
      recallHint: '暂无异常'
    },
    reviewers: '医生 / 药师 / 健管师',
    assistants: [
      { name: 'AI中医药膳师', state: '已启用', stateTone: 'g', todayTask: '养生建议，已推送', response: '已读' },
      { name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '6个月复查提醒，已排程', response: '已读' },
      { name: 'AI药师', state: '待启用', stateTone: 'o', todayTask: '用药提醒，待配置', response: '—' },
      { name: 'AI慢病管理师', state: '待启用', stateTone: 'o', todayTask: '慢病评估，待配置', response: '—' },
      { name: 'AI心理咨询师', state: '待启用', stateTone: 'o', todayTask: '情绪评估，待配置', response: '—' },
      { name: 'AI运动康复师', state: '已启用', stateTone: 'g', todayTask: '轻量运动建议，已推送', response: '已读' },
      { name: 'AI健康生活方式规划师', state: '已启用', stateTone: 'g', todayTask: '本周作息建议，已推送', response: '已读' },
      { name: 'AI健康福利官', state: '待启用', stateTone: 'o', todayTask: '服务权益提醒，待配置', response: '—' },
      { name: 'AI名医数字分身/AIHLP健康规划师', state: '已启用', stateTone: 'g', todayTask: '阶段性建议（低风险路径）', response: '已确认' }
    ],
    timeline: [
      { at: '07:40', tone: 'b', text: '复查提醒已推送', meta: '小程序 + 企微' },
      { at: '10:00', tone: 'p', text: 'AI随访问卷回收', meta: '患者已填写' }
    ]
  },
  {
    id: 'p4', name: '陈女士', gender: '女', age: 52, phoneMasked: '136****8899', source: '体检', owner: '李医生',
    nodules: '乳腺结节', risk: '高风险', riskTone: 'r', stage: 'abnormal', stageLabel: '异常预警',
    nextStep: '升级医生复核', serviceStatus: '异常处置中',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260415_乳腺超声报告.pdf', size: '0.91 MB', at: '2026-04-15', state: '已归档', stateTone: 'g' }],
    aiReadSummary: 'BI-RADS 4A 类，建议穿刺活检或 3 个月复查。',
    reportDoc: { title: '健康管理报告', sections: [{ h: '结节概况', p: 'BI-RADS 4A，建议活检。' }] },
    auditTrail: [{ at: '10:00', by: 'AI', action: '异常识别', note: '建议人工介入' }],
    chat: [{ at: '10:05', from: 'AI健康管理师', text: '已识别异常，建议尽快就医。' }],
    followTodos: [{ title: '电话随访', state: '待完成', tone: 'r', detail: '确认患者是否已就医' }],
    abnormal: { keywords: ['BI-RADS 4A', '高风险', '未就医'], interventions: [{ at: '10:00', by: 'AI', action: '异常识别', note: '建议人工电话随访' }], recallPlan: '待创建', recallState: '待处置', recallTone: 'r', recallHint: '需尽快处置' },
    reviewers: '医生 / 药师 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '异常跟进', response: '待处理' }],
    timeline: [{ at: '10:00', tone: 'r', text: 'AI识别异常', meta: 'BI-RADS 4A 高风险' }]
  },
  {
    id: 'p5', name: '赵先生', gender: '男', age: 45, phoneMasked: '135****3344', source: '门诊', owner: '王医生',
    nodules: '肺结节', risk: '低风险', riskTone: 'g', stage: 'push', stageLabel: '待推送患者',
    nextStep: '推送健康管理报告', serviceStatus: '待推送',
    report: { status: '审核通过' }, rawReports: [{ type: 'pdf', name: '20260418_胸部CT报告.pdf', size: '1.1 MB', at: '2026-04-18', state: '已上传', stateTone: 'g' }],
    aiReadSummary: '右下肺小结节 5mm，倾向良性，建议 12 个月复查。',
    reportDoc: { title: '健康管理报告', sections: [{ h: '结节概况', p: '右下肺小结节 5mm，低风险。' }, { h: '随访建议', p: '12 个月复查胸部 CT。' }] },
    auditTrail: [{ at: '09:00', by: '王医生', action: '审核通过', note: '可推送患者' }],
    chat: [],
    followTodos: [{ title: '推送报告', state: '待完成', tone: 'o', detail: '小程序 + 企微' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '12个月复查提醒', recallState: '待创建', recallTone: 'o', recallHint: '推送后自动创建' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '推送后启用', response: '—' }],
    timeline: [{ at: '09:00', tone: 'g', text: '健康管理报告审核通过', meta: '待推送患者' }]
  },
  {
    id: 'p6', name: '孙女士', gender: '女', age: 39, phoneMasked: '139****5566', source: '体检中心', owner: '健康管理师',
    nodules: '甲状腺结节', risk: '低风险', riskTone: 'g', stage: 'aiGen', stageLabel: '待生成报告',
    nextStep: '生成AI健康管理报告', serviceStatus: '待生成报告',
    report: { status: '未生成' }, rawReports: [{ type: 'pdf', name: '20260419_甲状腺超声报告.pdf', size: '0.55 MB', at: '2026-04-19', state: '已上传', stateTone: 'g' }],
    aiReadSummary: '暂未生成，报告已上传待处理。',
    reportDoc: { title: '健康管理报告（未生成）', sections: [{ h: '提示', p: '请生成AI健康管理报告。' }] },
    auditTrail: [{ at: '08:40', by: '系统', action: '报告上传完成', note: '等待AI生成' }],
    chat: [],
    followTodos: [{ title: '生成AI报告', state: '待完成', tone: 'o', detail: '甲状腺超声报告已上传' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '待创建', recallState: '—', recallTone: 'g', recallHint: '暂无' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '生成报告后启用', response: '—' }],
    timeline: [{ at: '08:40', tone: 'b', text: '上传甲状腺超声报告', meta: '等待AI生成报告' }]
  },
  {
    id: 'p7', name: '周先生', gender: '男', age: 67, phoneMasked: '137****7788', source: '门诊', owner: '刘医生',
    nodules: '肺结节合并乳腺结节', risk: '高风险', riskTone: 'r', stage: 'recall', stageLabel: '复查待回收',
    nextStep: '催收复查报告', serviceStatus: '复查待回收',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260101_胸部CT报告.pdf', size: '1.5 MB', at: '2026-01-01', state: '已归档', stateTone: 'g' }],
    aiReadSummary: '肺部结节 10mm，高风险，已逾期复查。',
    reportDoc: { title: '健康管理报告（已推送）', sections: [{ h: '结节概况', p: '肺部结节 10mm，高风险。' }] },
    auditTrail: [{ at: '2026-01-05', by: '刘医生', action: '审核通过并推送', note: '已送达' }],
    chat: [{ at: '2026-04-01', from: 'AI健康管理师', text: '您的复查时间已到，请尽快安排复查。' }],
    followTodos: [{ title: '复查回收', state: '逾期', tone: 'r', detail: '3个月复查已逾期' }],
    abnormal: { keywords: ['复查逾期', '高风险'], interventions: [{ at: '2026-04-01', by: 'AI', action: '发送复查提醒', note: '患者未回复' }], recallPlan: '已创建复查提醒', recallState: '逾期未回收', recallTone: 'r', recallHint: '建议电话催收' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '催收复查报告', response: '未回复' }],
    timeline: [{ at: '2026-04-01', tone: 'r', text: '复查逾期未回收', meta: '建议电话催收' }]
  },
  {
    id: 'p8', name: '吴女士', gender: '女', age: 55, phoneMasked: '138****2233', source: '体检', owner: '张医生',
    nodules: '乳腺结节', risk: '中风险', riskTone: 'o', stage: 'review', stageLabel: '健康管理报告待审核',
    nextStep: '医生审核后推送', serviceStatus: '报告待审核',
    report: { status: '待审核' }, rawReports: [{ type: 'pdf', name: '20260421_乳腺超声报告.pdf', size: '0.78 MB', at: '2026-04-21', state: '已上传', stateTone: 'g' }],
    aiReadSummary: 'BI-RADS 3 类，建议 6 个月复查超声。',
    reportDoc: { title: '健康管理报告', sections: [{ h: '结节概况', p: 'BI-RADS 3 类，倾向良性。' }, { h: '随访建议', p: '6 个月复查超声。' }] },
    auditTrail: [{ at: '09:30', by: 'AI', action: '生成健康管理报告', note: '待审核' }],
    chat: [],
    followTodos: [{ title: '审核报告', state: '待完成', tone: 'o', detail: '等待医生审核' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '6个月复查提醒', recallState: '待创建', recallTone: 'o', recallHint: '审核通过后创建' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '审核通过后启用', response: '—' }],
    timeline: [{ at: '09:30', tone: 'p', text: 'AI生成健康管理报告', meta: '待医生审核' }]
  },
  {
    id: 'p9', name: '郑先生', gender: '男', age: 50, phoneMasked: '136****4455', source: '门诊', owner: '王医生',
    nodules: '甲状腺结节', risk: '中风险', riskTone: 'o', stage: 'follow', stageLabel: 'AI随访中',
    nextStep: '按计划随访', serviceStatus: 'AI随访中',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260310_甲状腺超声报告.pdf', size: '0.6 MB', at: '2026-03-10', state: '已归档', stateTone: 'g' }],
    aiReadSummary: 'TI-RADS 4A 类，建议 3 个月复查。',
    reportDoc: { title: '健康管理报告（已推送）', sections: [{ h: '结节概况', p: 'TI-RADS 4A，中风险。' }] },
    auditTrail: [{ at: '08:00', by: '王医生', action: '审核通过并推送', note: '已送达' }],
    chat: [{ at: '08:10', from: 'AI健康管理师', text: '已安排 3 个月复查提醒。' }],
    followTodos: [{ title: '复查提醒', state: '已排程', tone: 'g', detail: '3个月复查超声' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '3个月复查提醒', recallState: '进行中', recallTone: 'g', recallHint: '暂无异常' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '随访中', response: '已读' }],
    timeline: [{ at: '08:10', tone: 'b', text: '复查提醒已推送', meta: '小程序 + 企微' }]
  },
  {
    id: 'p10', name: '冯女士', gender: '女', age: 43, phoneMasked: '135****6677', source: '体检中心', owner: '健康管理师',
    nodules: '肺结节', risk: '低风险', riskTone: 'g', stage: 'upload', stageLabel: '原始报告待上传',
    nextStep: '上传体检报告', serviceStatus: '待上传报告',
    report: { status: '未生成' }, rawReports: [],
    aiReadSummary: '暂无原始报告。',
    reportDoc: { title: '健康管理报告（未生成）', sections: [{ h: '提示', p: '请上传原始报告。' }] },
    auditTrail: [{ at: '10:20', by: '系统', action: '建档完成', note: '等待上传报告' }],
    chat: [],
    followTodos: [{ title: '上传原始报告', state: '待完成', tone: 'o', detail: '体检中心 PDF' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '待创建', recallState: '—', recallTone: 'g', recallHint: '暂无' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '上传后启用', response: '—' }],
    timeline: [{ at: '10:20', tone: 'b', text: '创建患者档案', meta: '等待上传报告' }]
  },
  {
    id: 'p11', name: '蒋先生', gender: '男', age: 61, phoneMasked: '139****8800', source: '门诊', owner: '李医生',
    nodules: '肺结节', risk: '高风险', riskTone: 'r', stage: 'abnormal', stageLabel: '异常预警',
    nextStep: '电话随访确认症状', serviceStatus: '异常处置中',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260320_胸部CT报告.pdf', size: '1.2 MB', at: '2026-03-20', state: '已归档', stateTone: 'g' }],
    aiReadSummary: '左上肺磨玻璃结节 9mm，高风险，患者反馈胸痛。',
    reportDoc: { title: '健康管理报告（已推送）', sections: [{ h: '结节概况', p: '左上肺磨玻璃结节 9mm，高风险。' }] },
    auditTrail: [{ at: '2026-03-22', by: '李医生', action: '审核通过并推送', note: '已送达' }],
    chat: [{ at: '2026-04-20', from: '患者', text: '最近胸口有点痛，需要复查吗？' }],
    followTodos: [{ title: '电话随访', state: '待完成', tone: 'r', detail: '确认胸痛症状' }],
    abnormal: { keywords: ['胸痛', '高风险'], interventions: [{ at: '2026-04-20', by: 'AI', action: '异常识别', note: '患者反馈胸痛' }], recallPlan: '紧急复查', recallState: '待处置', recallTone: 'r', recallHint: '建议立即电话随访' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '异常跟进', response: '待处理' }],
    timeline: [{ at: '2026-04-20', tone: 'r', text: '患者反馈胸痛', meta: '建议紧急随访' }]
  },
  {
    id: 'p12', name: '韩女士', gender: '女', age: 48, phoneMasked: '137****1122', source: '体检', owner: '张医生',
    nodules: '乳腺结节', risk: '低风险', riskTone: 'g', stage: 'follow', stageLabel: 'AI随访中',
    nextStep: '按计划随访', serviceStatus: 'AI随访中',
    report: { status: '已推送' }, rawReports: [{ type: 'pdf', name: '20260228_乳腺超声报告.pdf', size: '0.7 MB', at: '2026-02-28', state: '已归档', stateTone: 'g' }],
    aiReadSummary: 'BI-RADS 2 类，良性，建议 12 个月常规复查。',
    reportDoc: { title: '健康管理报告（已推送）', sections: [{ h: '结节概况', p: 'BI-RADS 2 类，良性。' }] },
    auditTrail: [{ at: '2026-03-01', by: '张医生', action: '审核通过并推送', note: '已送达' }],
    chat: [{ at: '2026-03-02', from: 'AI健康管理师', text: '已安排 12 个月复查提醒。' }],
    followTodos: [{ title: '复查提醒', state: '已排程', tone: 'g', detail: '12个月复查超声' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '12个月复查提醒', recallState: '进行中', recallTone: 'g', recallHint: '暂无异常' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '已启用', stateTone: 'g', todayTask: '随访中', response: '已读' }],
    timeline: [{ at: '2026-03-02', tone: 'b', text: '复查提醒已推送', meta: '小程序' }]
  },
  {
    id: 'p13', name: '杨先生', gender: '男', age: 54, phoneMasked: '138****9900', source: '门诊', owner: '刘医生',
    nodules: '甲状腺结节合并肺结节', risk: '中风险', riskTone: 'o', stage: 'aiGen', stageLabel: '待生成报告',
    nextStep: '生成AI健康管理报告', serviceStatus: '待生成报告',
    report: { status: '未生成' }, rawReports: [{ type: 'pdf', name: '20260422_甲状腺超声报告.pdf', size: '0.65 MB', at: '2026-04-22', state: '已上传', stateTone: 'g' }, { type: 'pdf', name: '20260422_胸部CT报告.pdf', size: '1.0 MB', at: '2026-04-22', state: '已上传', stateTone: 'g' }],
    aiReadSummary: '暂未生成，报告已上传待处理。',
    reportDoc: { title: '健康管理报告（未生成）', sections: [{ h: '提示', p: '请生成AI健康管理报告。' }] },
    auditTrail: [{ at: '11:00', by: '系统', action: '报告上传完成', note: '等待AI生成' }],
    chat: [],
    followTodos: [{ title: '生成AI报告', state: '待完成', tone: 'o', detail: '两份报告已上传' }],
    abnormal: { keywords: [], interventions: [], recallPlan: '待创建', recallState: '—', recallTone: 'g', recallHint: '暂无' },
    reviewers: '医生 / 健管师',
    assistants: [{ name: 'AI健康管理师', state: '待启用', stateTone: 'o', todayTask: '生成报告后启用', response: '—' }],
    timeline: [{ at: '11:00', tone: 'b', text: '上传甲状腺超声 + 胸部CT报告', meta: '等待AI生成报告' }]
  }
])

const filteredQueue = computed(() => {
  if (activeStage.value === 'all') return queue.value
  return queue.value.filter((p) => statusKey(p) === activeStage.value)
})

const activePatient = computed(() => {
  return queue.value.find((p) => p.id === activePatientId.value) || queue.value[0]
})

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
  if (subTab.value !== 'queue') subTab.value = 'queue'
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
  subTab.value = 'queue'
  router.replace({ path: '/patient', query: { ...route.query, tab: 'queue' } })
}
</script>

<style scoped>
.pm{height:100%;display:flex;flex-direction:column;overflow:hidden;margin:-16px -20px}
.pm-shell{flex:1;min-height:0;background:#fff;display:flex;flex-direction:column;overflow:hidden}
.pm-record{flex:1;min-height:0;overflow:auto;background:#f3f6fb;padding:12px}

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
.overview-left{min-height:0;display:flex;flex-direction:column}
.overview-right{min-height:0;height:100%;display:flex;flex-direction:column;gap:12px;overflow-y:auto;overflow-x:hidden;padding-right:12px;padding-bottom:12px;box-sizing:border-box}
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
.rp-empty{display:flex;align-items:center;justify-content:center;height:200px;color:#94a3b8;font-size:13px}
</style>

