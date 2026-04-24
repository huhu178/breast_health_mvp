<template>
  <span class="tag" :class="tone">{{ text }}</span>
</template>

<script setup>
defineProps({ text: String, tone: String })
</script>

<style scoped>
.tag{display:inline-flex;align-items:center;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:900;line-height:1.4}
.tag.high{background:#fff1f1;color:#dc2626}
.tag.orange{background:#fff7e6;color:#c26a00}
.tag.mid{background:#fff7e6;color:#c26a00}
.tag.low{background:#ecfff3;color:#14843b}
.tag.green{background:#ecfff3;color:#14843b}
.tag.blue{background:#eef5ff;color:#155eef}
.tag.purple{background:#f5f0ff;color:#8b5cf6}
.tag.gray{background:#f1f5f9;color:#64748b}
</style>
