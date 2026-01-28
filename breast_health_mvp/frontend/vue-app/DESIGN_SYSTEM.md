# 统一设计系统使用指南

## 📋 概述

本项目采用统一的设计系统，确保所有结节类型（乳腺、肺、甲状腺等）的界面风格一致，便于后续扩展和维护。

## 🎨 设计系统结构

```
src/
├── assets/
│   └── styles/
│       ├── design-system.css    # 统一设计系统（核心）
│       └── form-common.css      # 表单通用样式（使用设计系统）
├── components/
│   └── common/                  # 通用基础组件
│       ├── BaseCard.vue         # 卡片组件
│       ├── BaseButton.vue       # 按钮组件
│       ├── BaseInput.vue        # 输入框组件
│       └── BaseBadge.vue        # 徽章组件
└── utils/
    └── nodule-config.js         # 结节类型配置
```

## 🎯 核心设计原则

### 1. 色彩系统
- **主色调**：医疗蓝系（#1e88e5 → #00acc1）
- **结节类型专属色**：每种结节类型有专属颜色
- **语义化颜色**：success, warning, danger, info

### 2. 间距系统
- 使用统一的间距变量：`--spacing-xs` 到 `--spacing-3xl`
- 确保所有组件间距一致

### 3. 圆角系统
- 统一的圆角变量：`--radius-sm` 到 `--radius-full`
- 卡片使用 `--radius-xl` (16px)

### 4. 字体系统
- 统一的字体大小和行高
- 标题使用渐变文字效果

## 📦 基础组件使用

### BaseCard（卡片组件）

```vue
<template>
  <BaseCard>
    <template #header>
      <h3>标题</h3>
    </template>
    
    <p>卡片内容</p>
    
    <template #footer>
      <button>操作按钮</button>
    </template>
  </BaseCard>
</template>

<script setup>
import BaseCard from '@/components/common/BaseCard.vue'
</script>
```

**Props:**
- `hover` (Boolean): 是否启用悬停效果，默认 `true`
- `shadow` (String): 阴影大小，可选 `sm`, `md`, `lg`, `xl`，默认 `md`

### BaseButton（按钮组件）

```vue
<template>
  <BaseButton variant="primary" size="md" @click="handleClick">
    点击我
  </BaseButton>
</template>

<script setup>
import BaseButton from '@/components/common/BaseButton.vue'
</script>
```

**Props:**
- `variant` (String): 按钮类型，可选 `primary`, `secondary`, `success`, `warning`, `danger`, `link`
- `size` (String): 按钮大小，可选 `sm`, `md`, `lg`
- `disabled` (Boolean): 是否禁用
- `block` (Boolean): 是否块级按钮（100%宽度）

### BaseInput（输入框组件）

```vue
<template>
  <BaseInput
    v-model="value"
    label="姓名"
    placeholder="请输入姓名"
    required
    :error="errorMessage"
    hint="这是提示信息"
  />
</template>

<script setup>
import { ref } from 'vue'
import BaseInput from '@/components/common/BaseInput.vue'

const value = ref('')
const errorMessage = ref('')
</script>
```

**Props:**
- `modelValue` (String|Number): 输入值（v-model）
- `label` (String): 标签文字
- `type` (String): 输入类型，默认 `text`
- `placeholder` (String): 占位符
- `required` (Boolean): 是否必填（显示*）
- `error` (String): 错误信息
- `hint` (String): 提示信息
- `size` (String): 输入框大小，可选 `sm`, `md`, `lg`

### BaseBadge（徽章组件）

```vue
<template>
  <BaseBadge variant="primary" size="md">标签</BaseBadge>
</template>

<script setup>
import BaseBadge from '@/components/common/BaseBadge.vue'
</script>
```

**Props:**
- `variant` (String): 徽章类型，可选 `primary`, `success`, `warning`, `danger`, `info`
- `size` (String): 徽章大小，可选 `sm`, `md`, `lg`

## 🔧 结节类型配置

### 使用结节配置

```javascript
import { getNoduleConfig, getNoduleColor, getNoduleName } from '@/utils/nodule-config'

// 获取结节配置
const config = getNoduleConfig('breast')
console.log(config.name) // '乳腺结节'
console.log(config.color) // '#1e88e5'

// 获取颜色
const color = getNoduleColor('breast') // '#1e88e5'

// 获取名称
const name = getNoduleName('breast') // '乳腺结节'
```

### 结节类型列表

- `breast`: 乳腺结节
- `lung`: 肺结节
- `thyroid`: 甲状腺结节
- `breast_lung`: 乳腺+肺
- `breast_thyroid`: 乳腺+甲状腺
- `lung_thyroid`: 肺+甲状腺
- `triple`: 三结节

## 🎨 CSS变量使用

### 在组件中使用CSS变量

```vue
<style scoped>
.custom-component {
  color: var(--color-primary);
  background: var(--color-bg-primary);
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}
</style>
```

### 常用CSS变量

**颜色：**
- `--color-primary`: 主色调
- `--color-text-primary`: 主要文字颜色
- `--color-bg-primary`: 主要背景色
- `--color-border`: 边框颜色

**间距：**
- `--spacing-xs`: 4px
- `--spacing-sm`: 8px
- `--spacing-md`: 16px
- `--spacing-lg`: 24px
- `--spacing-xl`: 32px

**圆角：**
- `--radius-sm`: 6px
- `--radius-md`: 10px
- `--radius-lg`: 12px
- `--radius-xl`: 16px

**阴影：**
- `--shadow-sm`: 小阴影
- `--shadow-md`: 中等阴影
- `--shadow-lg`: 大阴影

## 📝 开发规范

### 1. 新组件开发
- 优先使用基础组件（BaseCard, BaseButton等）
- 使用CSS变量而非硬编码颜色/间距
- 遵循设计系统的间距和圆角规范

### 2. 结节类型扩展
- 在 `nodule-config.js` 中添加新类型配置
- 复用现有组件和样式
- 保持视觉风格一致

### 3. 样式覆盖
- 尽量避免覆盖基础组件样式
- 如需自定义，使用CSS变量
- 保持响应式设计

## 🚀 后续优化计划

1. **组件库完善**
   - [ ] BaseSelect（下拉选择）
   - [ ] BaseCheckbox（复选框）
   - [ ] BaseRadio（单选框）
   - [ ] BaseModal（模态框）
   - [ ] BaseTable（表格）
   - [ ] BasePagination（分页）

2. **设计系统增强**
   - [ ] 深色模式支持
   - [ ] 动画系统
   - [ ] 响应式断点系统

3. **结节类型实现**
   - [x] 乳腺结节（已完成）
   - [ ] 肺结节
   - [ ] 甲状腺结节
   - [ ] 组合类型（复用组件）

## 📚 参考资源

- 设计系统文件：`src/assets/styles/design-system.css`
- 结节配置：`src/utils/nodule-config.js`
- 基础组件：`src/components/common/`



