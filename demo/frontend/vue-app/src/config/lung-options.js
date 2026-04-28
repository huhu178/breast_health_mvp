/**
 * 肺结节表单选项配置
 * 从 LungFormSection.vue 提取
 * 修改选项只需修改这个文件
 *
 * 注意：此配置仅包含报告模板中实际使用的字段
 */

export const LUNG_OPTIONS = {
  // Lung-RADS分级选项
  lung_rads_levels: [
    { value: '不清楚', label: '不清楚' },
    { value: '1', label: 'LR 1 - 阴性 (几乎为0%，年度筛查)' },
    { value: '2', label: 'LR 2 - 良性发现 (<1%，年度筛查)' },
    { value: '3', label: 'LR 3 - 可能良性 (1%-2%，6个月随访LDCT)' },
    { value: '4A', label: 'LR 4A - 低度可疑 (5%-15%，3个月随访CT或PET/CT)' },
    { value: '4B', label: 'LR 4B - 高度可疑 (>15%，PET/CT或活检)' },
    { value: '4X', label: 'LR 4X - 附加高度可疑 (>50%，极高风险)' }
  ],

  // 肺部症状选项
  symptoms_options: [
    '无症状',
    '咳嗽',
    '胸痛',
    '呼吸困难',
    '咯血',
    '全身症状',
    '其他'
  ],

  // 结节数量选项
  nodule_quantity_options: [
    { value: 'single', label: '单发' },
    { value: 'multiple', label: '多发' }
  ],

  // 肺部基础疾病史选项
  lung_disease_history_options: [
    '无',
    '肺炎病史',
    '肺结核病史',
    '慢性阻塞性肺疾病',
    '肺纤维化',
    '肺癌病史',
    '其他'
  ],

  // 家族史选项
  family_history_options: [
    '无',
    '一级亲属（父母、子女、亲兄弟姐妹）',
    '二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）',
    '三级亲属（表/堂兄妹）',
    '其他'
  ],

  // 药物使用史选项
  medication_history_options: [
    '无',
    '抗感染治疗',
    '激素治疗',
    '抗肿瘤治疗',
    '抗炎药物',
    '其他'
  ]
}
