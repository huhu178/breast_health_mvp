<template>
  <div class="rws">
    <div class="head">
      <div>
        <div class="title">真实世界研究</div>
        <div class="muted">入组筛选 · 随访结局 · AI与人工一致性 · 脱敏导出（示意）</div>
      </div>
      <div class="actions">
        <button class="btn" type="button">新建研究</button>
        <button class="primary" type="button">脱敏导出</button>
      </div>
    </div>

    <div class="grid">
      <section class="card">
        <div class="card-head">
          <div class="card-title">研究队列</div>
          <div class="muted">当前在研 3 项</div>
        </div>
        <div class="card-body">
          <div class="queue">
            <div class="q" v-for="q in queues" :key="q.name">
              <div class="q-top">
                <b>{{ q.name }}</b>
                <span class="pill">{{ q.state }}</span>
              </div>
              <div class="muted">{{ q.desc }}</div>
              <div class="q-kpis">
                <div class="kpi"><span class="muted">入组</span><b>{{ q.n }}</b></div>
                <div class="kpi"><span class="muted">随访中</span><b>{{ q.fu }}</b></div>
                <div class="kpi"><span class="muted">结局</span><b>{{ q.outcome }}</b></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="card-head">
          <div class="card-title">入组筛选</div>
          <div class="muted">规则驱动 + 人工确认</div>
        </div>
        <div class="card-body">
          <div class="filters">
            <label class="fi">结节类型
              <select><option>全部</option><option>肺部结节</option><option>甲状腺结节</option><option>乳腺结节</option></select>
            </label>
            <label class="fi">风险等级
              <select><option>全部</option><option>高风险</option><option>中风险</option><option>低风险</option></select>
            </label>
            <label class="fi">随访状态
              <select><option>全部</option><option>AI随访中</option><option>异常预警</option><option>复查待回收</option></select>
            </label>
            <label class="fi">时间范围
              <input type="date" value="2026-01-01" />
            </label>
            <div class="fi">
              <button class="primary" type="button">筛选</button>
            </div>
          </div>

          <div class="table-wrap">
            <table class="table">
              <thead>
                <tr>
                  <th>候选患者</th><th>结节/风险</th><th>关键字段</th><th>AI建议</th><th>人工确认</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in candidates" :key="c.name">
                  <td><b>{{ c.name }}</b><div class="muted">{{ c.meta }}</div></td>
                  <td>{{ c.nodule }} · <b>{{ c.risk }}</b></td>
                  <td class="muted">{{ c.key }}</td>
                  <td class="muted">{{ c.ai }}</td>
                  <td><button class="btn" type="button">纳入</button> <button class="btn" type="button">排除</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section class="card span2">
        <div class="card-head">
          <div class="card-title">一致性与结局</div>
          <div class="muted">AI vs 人工审核（示意）</div>
        </div>
        <div class="card-body">
          <div class="kpi-row">
            <div class="k"><span class="muted">一致性</span><b>91.6%</b></div>
            <div class="k"><span class="muted">需复审</span><b>38</b></div>
            <div class="k"><span class="muted">脱落</span><b>12</b></div>
            <div class="k"><span class="muted">结局事件</span><b>27</b></div>
          </div>
          <div class="note muted">
            数据展示为静态示意：后续可接入“随访结局”字段（复查完成、异常转诊、手术/病理结果等）与一致性审计日志。
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
const queues = [
  { name: '肺结节高风险随访队列', state: '进行中', desc: '纳入 ≥6mm 磨玻璃结节；随访周期 3 个月', n: 812, fu: 604, outcome: 76 },
  { name: '甲状腺结节 TI-RADS 3 随访', state: '进行中', desc: '纳入 TI-RADS 3/4a；随访周期 6-12 个月', n: 702, fu: 518, outcome: 54 },
  { name: '乳腺结节 BI-RADS 3 随访', state: '筹备', desc: '纳入 BI-RADS 3；随访周期 6 个月', n: 0, fu: 0, outcome: 0 }
]

const candidates = [
  { name: '张*国', meta: '男 · 56岁 · 门诊', nodule: '肺部结节', risk: '高风险', key: '磨玻璃结节 8mm / 右上肺', ai: '建议 3 个月复查；随访+异常监测' },
  { name: '李*婷', meta: '女 · 48岁 · 体检中心', nodule: '甲状腺结节', risk: '中风险', key: 'TI-RADS 3 类 / 既往对比', ai: '建议 6-12 个月复查超声' }
]
</script>

<style scoped>
.rws{height:100%;overflow:auto;display:grid;gap:12px;align-content:start}
.head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.title{font-size:20px;font-weight:950;color:#0f172a}
.actions{display:flex;gap:8px}
.btn{border:1px solid #d9e2ef;border-radius:10px;background:#fff;color:#475569;padding:8px 12px;font-weight:900;cursor:pointer}
.primary{background:#155eef;border:1px solid #155eef;color:#fff;border-radius:10px;padding:8px 12px;cursor:pointer;font-weight:900}
.muted{color:#64748b;font-weight:750}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;align-items:start}
.span2{grid-column:1 / -1}
.card{background:#fff;border:1px solid #e6edf7;border-radius:12px;box-shadow:0 6px 18px rgba(15,23,42,.04);overflow:hidden}
.card-head{height:46px;border-bottom:1px solid #eef2f7;display:flex;align-items:center;justify-content:space-between;padding:0 14px}
.card-title{font-weight:950;color:#0f172a}
.card-body{padding:12px 14px}
.queue{display:grid;gap:10px}
.q{border:1px solid #eef2f7;border-radius:12px;padding:12px;background:#fbfdff}
.q-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.pill{border-radius:999px;padding:3px 10px;border:1px solid #e6edf7;background:#fff;font-weight:900;color:#526175}
.q-kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px}
.kpi{border:1px solid #eef2f7;border-radius:12px;background:#fff;padding:10px;display:flex;align-items:center;justify-content:space-between}
.filters{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;align-items:end;margin-bottom:10px}
.fi{display:flex;flex-direction:column;gap:6px;font-weight:850;color:#475569}
.fi select,.fi input{height:34px;border:1px solid #d9e2ef;border-radius:10px;padding:0 10px;outline:none}
.table-wrap{overflow:auto}
.table{width:100%;border-collapse:collapse;min-width:860px}
.table th{background:#f8fafc;color:#64748b;font-size:12px;text-align:left;padding:10px 9px;border-bottom:1px solid #e5edf7;white-space:nowrap}
.table td{padding:10px 9px;border-bottom:1px solid #edf2f7;white-space:nowrap;vertical-align:top}
.kpi-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.k{border:1px solid #eef2f7;border-radius:12px;background:#fff;padding:12px;display:flex;align-items:center;justify-content:space-between}
.note{margin-top:10px;line-height:1.7}
</style>

