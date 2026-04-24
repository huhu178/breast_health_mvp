<template>
  <article class="kpi" :data-tone="tone">
    <div class="kpi-icon" :class="tone !== 'blue' ? tone : ''">{{ icon }}</div>
    <div class="kpi-label">{{ label }}</div>
    <div class="kpi-value">{{ value }}</div>
    <div class="kpi-hint">{{ delta }}</div>
    <svg class="spark" :class="tone !== 'blue' ? tone : ''" viewBox="0 0 70 26" aria-hidden="true">
      <path d="M2 20 C10 18 12 16 18 17 C25 18 28 10 34 12 C40 14 42 6 48 7 C55 8 57 17 68 12"/>
    </svg>
  </article>
</template>

<script setup>
defineProps({ label: String, value: String, delta: String, tone: String, icon: String })
</script>

<style scoped>
.kpi{position:relative;padding:13px 15px;border:1px solid #dbe6f4;border-radius:8px;background:#fff;box-shadow:0 4px 14px rgba(15,23,42,.04);overflow:hidden;display:grid;grid-template-columns:30px minmax(0,1fr);column-gap:10px}
.kpi-icon{grid-row:1/span 3;width:27px;height:27px;border-radius:7px;display:flex;align-items:center;justify-content:center;background:#eef5ff;color:#155eef;font-weight:900;font-size:14px;margin-top:8px}
.kpi-icon.orange{background:#fff4e8;color:#f97316}
.kpi-icon.green{background:#ecfdf5;color:#16a34a}
.kpi-icon.purple{background:#f5f0ff;color:#8b5cf6}
.kpi-icon.cyan{background:#eafcff;color:#0ea5b7}
.kpi-label{color:#526175;font-weight:800;font-size:11px}
.kpi-value{font-size:21px;font-weight:950;margin-top:7px;color:#155eef;line-height:1}
.kpi-hint{font-size:10px;color:#8a9bb1;margin-top:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:700}
.spark{position:absolute;right:12px;bottom:12px;width:62px;height:22px}
.spark path{fill:none;stroke:#5b8ff9;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.spark.orange path{stroke:#f97316}
.spark.green path{stroke:#16a34a}
.spark.purple path{stroke:#8b5cf6}
.spark.cyan path{stroke:#0ea5b7}
</style>
