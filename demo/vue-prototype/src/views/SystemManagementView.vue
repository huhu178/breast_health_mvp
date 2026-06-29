<template>
  <div class="system-page">
    <header class="page-head">
      <div>
        <div class="eyebrow">平台管理员</div>
        <h1>系统管理</h1>
        <p>维护账号、科室医生、随访规则、基础字典和平台扩展模块，不参与患者日常随访操作。</p>
      </div>
    </header>

    <section class="kpi-grid">
      <article v-for="item in kpis" :key="item.label" class="kpi">
        <span>{{ item.label }}</span>
        <b>{{ item.value }}</b>
        <em>{{ item.note }}</em>
      </article>
    </section>

    <section class="module-grid">
      <article v-for="item in modules" :key="item.title" class="module-card">
        <div class="module-icon">{{ item.icon }}</div>
        <div>
          <h2>{{ item.title }}</h2>
          <p>{{ item.desc }}</p>
        </div>
        <button type="button" @click="go(item.path)">{{ item.action }}</button>
      </article>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const kpis = [
  { label: '启用角色', value: '4', note: '健康管理员 / 医生 / 科室主任 / 平台管理员' },
  { label: '默认科室', value: '4', note: '健康管理中心、乳腺科、甲状腺科、呼吸科' },
  { label: '配置模块', value: '5', note: '账号、科室、规则、模板、日志' },
  { label: '业务边界', value: '只配置', note: '不直接处理患者随访任务' },
]

const modules = [
  { icon: '账', title: '账号与角色', desc: '维护健康管理员、医生、科室主任和平台管理员账号。', action: '查看配置', path: '/system' },
  { icon: '科', title: '科室与医生', desc: '维护科室、医生归属和患者默认分配关系。', action: '查看配置', path: '/system' },
  { icon: '规', title: '随访规则', desc: '维护随访知识库、模板、节点和异常升级规则。', action: '进入知识库', path: '/followup-workflow' },
  { icon: '字', title: '系统字典', desc: '维护结节类型、风险等级、患者状态和来源渠道。', action: '查看配置', path: '/system' },
  { icon: '志', title: '操作日志', desc: '查看账号登录、报告审核、随访任务和配置变更记录。', action: '查看日志', path: '/system' },
  { icon: '研', title: '真实世界研究', desc: '面向课题、队列、入组和随访数据分析的扩展模块。', action: '进入模块', path: '/rws' },
  { icon: '营', title: 'AI营销', desc: '面向医生IP、内容科普、线索承接和营销智脑的扩展模块。', action: '进入模块', path: '/ai-employee/overview' },
]

function go(path) {
  router.push(path)
}
</script>

<style scoped>
.system-page{display:grid;gap:16px;color:#0f172a}
.page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px}
.eyebrow{font-size:12px;font-weight:900;color:#2563eb;margin-bottom:4px}
h1{font-size:24px;line-height:1.2;margin:0 0 6px}
p{margin:0;color:#64748b;font-size:13px;line-height:1.6}
.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.kpi{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;display:grid;gap:6px}
.kpi span{font-size:12px;color:#64748b;font-weight:850}
.kpi b{font-size:22px;color:#0f172a}
.kpi em{font-style:normal;color:#94a3b8;font-size:12px;line-height:1.4}
.module-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.module-card{background:#fff;border:1px solid #e6edf7;border-radius:8px;padding:14px;display:grid;grid-template-columns:42px minmax(0,1fr) auto;gap:12px;align-items:center}
.module-icon{width:42px;height:42px;border-radius:10px;background:#eef5ff;color:#155eef;display:grid;place-items:center;font-weight:950}
.module-card h2{margin:0 0 4px;font-size:15px}
.module-card button{height:32px;border-radius:8px;border:1px solid #d9e2ef;background:#fff;color:#155eef;font-weight:850;cursor:pointer;padding:0 12px}
@media(max-width:1000px){.kpi-grid,.module-grid{grid-template-columns:1fr}.module-card{grid-template-columns:42px minmax(0,1fr)}.module-card button{grid-column:2}}
</style>
