<template>
  <article class="kpi" :data-tone="tone">
    <div class="kpi-icon" :class="tone !== 'blue' ? tone : ''" aria-hidden="true">
      <svg v-if="iconPath" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <path :d="iconPath" />
      </svg>
      <span v-else>{{ icon }}</span>
    </div>
    <div class="kpi-label">{{ label }}</div>
    <div class="kpi-value">{{ value }}</div>
    <div class="kpi-hint">{{ delta }}</div>
    <svg class="spark" :class="tone !== 'blue' ? tone : ''" viewBox="0 0 70 26" aria-hidden="true">
      <path d="M2 20 C10 18 12 16 18 17 C25 18 28 10 34 12 C40 14 42 6 48 7 C55 8 57 17 68 12"/>
    </svg>
  </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ label: String, value: String, delta: String, tone: String, icon: String })

const iconPath = computed(() => {
  const key = props.icon
  if (key === 'users') return 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8 M23 21v-2a4 4 0 0 0-3-3.87'
  if (key === 'shield') return 'M12 2l7 4v6c0 5-3 9-7 10-4-1-7-5-7-10V6l7-4'
  if (key === 'file') return 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6'
  if (key === 'check') return 'M20 6L9 17l-5-5'
  if (key === 'send') return 'M22 2L11 13 M22 2l-7 20-4-9-9-4 20-7z'
  if (key === 'clock') return 'M12 8v5l3 2 M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20'
  return ''
})
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
