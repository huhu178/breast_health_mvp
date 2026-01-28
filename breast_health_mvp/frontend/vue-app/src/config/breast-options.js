/**
 * 乳腺结节表单选项配置
 * 从 BreastFormSection.vue 提取
 * 修改选项只需修改这个文件
 */

export const BREAST_OPTIONS = {
  // BI-RADS分级选项
  birads_levels: [
    { value: '0', label: '0类 - 评估不完全 (需结合其他检查)' },
    { value: '1', label: '1类 - 阴性 (正常)' },
    { value: '2', label: '2类 - 良性 (如囊肿)' },
    { value: '3', label: '3类 - 可能良性 (建议短期随访)' },
    { value: '4A', label: '4A类 - 低度可疑 (恶性风险 2-10%)' },
    { value: '4B', label: '4B类 - 中度可疑 (恶性风险 10-50%)' },
    { value: '4C', label: '4C类 - 高度可疑 (恶性风险 50-95%)' },
    { value: '5', label: '5类 - 高度提示恶性 (≥95%)' },
    { value: '6', label: '6类 - 已活检确诊恶性' }
  ],

  // 症状选项
  symptoms_options: [
    '无症状',
    '乳房肿块',
    '乳房疼痛',
    '乳房胀满感',
    '乳头溢液',
    '乳房皮肤改变',
    '腋下淋巴结肿大',
    '其他'
  ],

  // 结节位置选项
  nodule_location_options: [
    '左侧乳房',
    '右侧乳房',
    '双侧乳房',
    '其他'
  ],

  // 边界特征选项
  boundary_features_options: [
    '光滑',
    '模糊',
    '分叶状',
    '毛刺化（微钙化/粗大毛刺化）',
    '毛刺痕',
    '其他'
  ],

  // 内部回声选项
  internal_echo_options: [
    '无回声（囊性）',
    '等回声（实性）',
    '低回声',
    '混合回声',
    '其他'
  ],

  // 血流信号选项
  blood_flow_options: [
    '无',
    '稀疏',
    '丰富（内部/周边）',
    '其他'
  ],

  // 结节数量选项
  nodule_count_options: [
    { value: 'single', label: '单发' },
    { value: 'multiple', label: '多发' }
  ]
}
