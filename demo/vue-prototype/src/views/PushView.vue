<template>
  <div class="page">
    <div class="page-head">
      <div class="page-title">患者触达</div>
      <div class="crumb">首页 / <b>患者触达</b></div>
    </div>

    <div class="kpi-row">
      <KpiCard v-for="m in kpis" :key="m.label" v-bind="m" />
    </div>

    <div class="layout">
      <!-- 待推送列表 -->
      <section class="card">
        <div class="card-head">
          <div class="card-title">待推送患者 <span class="muted">共 {{ pushList.length }} 人</span></div>
          <div class="head-actions">
            <button class="btn" @click="toast.show('批量推送中...')">批量推送</button>
            <button class="btn" @click="toast.show('导出')">导出</button>
          </div>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr>
                <th>患者</th><th>结节类型</th><th>风险</th><th>推送渠道</th>
                <th>推送内容</th><th>负责人</th><th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in pushList" :key="p.id"
                :class="{ active: p.id === store.currentPatientId }"
                @click="store.currentPatientId = p.id">
                <td>
                  <div><b>{{ p.name }}</b></div>
                  <div class="muted" style="font-size:11px">{{ p.age }}岁 · {{ p.phone }}</div>
                </td>
                <td><TagBadge :text="p.nodule" tone="blue" /></td>
                <td><TagBadge :text="riskText(p.risk)" :tone="riskClass(p.risk)" /></td>
                <td>
                  <div class="channel-row">
                    <span class="channel">小程序</span>
                    <span class="channel">企微</span>
                    <span class="channel">短信</span>
                  </div>
                </td>
                <td>健康管理报告 + 复查提醒</td>
                <td>{{ p.owner }}</td>
                <td>
                  <div class="row-actions">
                    <span class="act" @click.stop="doPush(p)">推送</span>
                    <span class="act" @click.stop="toast.show('预览小程序')">预览</span>
                    <span class="act" @click.stop="toast.show('企微话术')">话术</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- 推送详情 -->
      <section class="card" v-if="current">
        <div class="card-head">
          <div class="card-title">推送详情</div>
          <button class="ico-btn" @click="store.currentPatientId = null">×</button>
        </div>
        <div class="detail-body">
          <div class="detail-top">
            <div>
              <div class="detail-name">{{ current.name }}</div>
              <div class="muted" style="margin-top:4px">{{ current.gender }} · {{ current.age }}岁 · {{ current.phone }}</div>
            </div>
            <TagBadge :text="riskText(current.risk)" :tone="riskClass(current.risk)" />
          </div>

          <div class="hline"></div>
          <div class="section-label">推送渠道配置</div>
          <div class="channel-config">
            <div class="ch-item active">
              <div class="ch-icon">📱</div>
              <div>
                <div class="ch-name">小程序</div>
                <div class="muted" style="font-size:11px">健康管理报告 + 复查提醒</div>
              </div>
              <span class="tag green">已选</span>
            </div>
            <div class="ch-item active">
              <div class="ch-icon">💬</div>
              <div>
                <div class="ch-name">企业微信</div>
                <div class="muted" style="font-size:11px">随访问卷 + 话术消息</div>
              </div>
              <span class="tag green">已选</span>
            </div>
            <div class="ch-item">
              <div class="ch-icon">📨</div>
              <div>
                <div class="ch-name">短信</div>
                <div class="muted" style="font-size:11px">复查提醒短信</div>
              </div>
              <span class="tag gray">可选</span>
            </div>
          </div>

          <div class="hline"></div>
          <div class="section-label">推送内容预览</div>
          <div class="ai-box">
            <b>健康管理报告摘要</b><br>
            {{ current.report }}<br><br>
            <b>AI建议</b><br>
            {{ current.ai }}
          </div>

          <div class="action-bar">
            <button class="primary" @click="doPush(current)">确认推送</button>
            <button class="btn" @click="toast.show('预览小程序')">预览小程序</button>
            <button class="btn" @click="toast.show('企微话术')">企微话术</button>
          </div>
        </div>
      </section>
    </div>
  </div>
  <ToastMsg ref="toast" />
</template>

<script setup>
import { ref, computed } from 'vue'
import { store } from '../store/index.js'
import { riskText, riskClass } from '../mocks/patients.js'
import TagBadge from '../components/TagBadge.vue'
import KpiCard from '../components/KpiCard.vue'
import ToastMsg from '../components/ToastMsg.vue'

const toast = ref(null)

const kpis = [
  { label: '待推送患者', value: '95', delta: '较昨日 +7', tone: 'blue', icon: '发' },
  { label: '今日已推送', value: '48', delta: '较昨日 +12', tone: 'green', icon: '✓' },
  { label: '小程序触达', value: '82.4%', delta: '较昨日 +1.2%', tone: 'purple', icon: '📱' },
  { label: '企微触达', value: '76.8%', delta: '较昨日 +0.8%', tone: 'cyan', icon: '💬' },
  { label: '患者已读', value: '68.3%', delta: '较昨日 +2.1%', tone: 'orange', icon: '👁' }
]

const pushList = computed(() => store.patients.filter(p => p.stage === 'push'))
const current = computed(() => store.patients.find(p => p.id === store.currentPatientId))

function doPush(p) {
  store.setStage(p.id, 'followup', '已推送小程序与企微，随访任务已生成')
  toast.value?.show('已推送小程序与企微，随访任务已生成')
}
</script>

<style scoped>
.page{min-height:100%}
.page-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.page-title{font-size:20px;font-weight:950;color:#0f172a}
.crumb{color:#64748b;font-weight:700}
.kpi-row{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-bottom:14px}
.card{background:#fff;border:1px solid #e6edf7;border-radius:10px;box-shadow:0 6px 18px rgba(15,23,42,.04);margin-bottom:12px}
.card-head{height:46px;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:0 14px}
.card-title{font-weight:900;color:#0f172a}
.head-actions{display:flex;gap:6px}
.layout{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(380px,.9fr);gap:12px;align-items:start}
.table-wrap{overflow:auto}
.table{width:100%;border-collapse:collapse;min-width:700px}
.table th{background:#f8fafc;color:#64748b;font-size:12px;text-align:left;padding:10px 9px;border-bottom:1px solid #e5edf7;white-space:nowrap}
.table td{padding:10px 9px;border-bottom:1px solid #edf2f7;white-space:nowrap}
.table tbody tr{cursor:pointer}
.table tbody tr:hover{background:#f8fbff}
.table tbody tr.active{background:#eef5ff}
.channel-row{display:flex;gap:4px}
.channel{background:#eef5ff;color:#155eef;border-radius:4px;padding:2px 6px;font-size:11px;font-weight:750}
.row-actions{display:flex;gap:6px;color:#155eef;font-size:12px;font-weight:750}
.row-actions .act{cursor:pointer}
.detail-body{padding:14px 16px}
.detail-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;margin-bottom:12px}
.detail-name{font-size:16px;font-weight:950;color:#0f172a}
.hline{height:1px;background:#edf2f7;margin:12px 0}
.section-label{font-weight:850;margin-bottom:8px;color:#0f172a}
.channel-config{display:grid;gap:8px}
.ch-item{display:flex;align-items:center;gap:10px;border:1px solid #eef2f7;border-radius:10px;padding:10px 12px;background:#fbfdff}
.ch-item.active{border-color:#cfe0ff;background:#f0f7ff}
.ch-icon{font-size:20px;width:36px;text-align:center}
.ch-name{font-weight:850;color:#0f172a}
.ai-box{background:#f8fbff;border:1px solid #dce8f8;border-radius:7px;padding:11px 12px;line-height:1.7;color:#253247;font-size:13px}
.action-bar{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.btn{border:1px solid #d9e2ef;border-radius:6px;background:#fff;color:#475569;padding:6px 10px;cursor:pointer}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:6px;padding:6px 10px;cursor:pointer;font-weight:750}
.ico-btn{width:34px;height:34px;border-radius:10px;border:1px solid #d9e2ef;background:#fff;color:#64748b;cursor:pointer}
.muted{color:#64748b}
.tag{display:inline-flex;align-items:center;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:900}
.tag.green{background:#ecfff3;color:#14843b}
.tag.gray{background:#f1f5f9;color:#64748b}
</style>
