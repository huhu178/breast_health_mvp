/**
 * 乳腺结节字段配置
 * 根据 breast_report.html 模板提取
 * 用途：前端表单自动生成、数据库字段映射、模板变量统一
 */

export const BREAST_FIELDS = {
  // ==================== （一）基本信息 ====================
  diabetes_history: {
    label: '糖尿病史',
    type: 'radio',
    dbColumn: 'diabetes_history',
    templateVar: 'diabetes_history',
    section: '基本信息',
    options: [
      { value: '无', label: '无' },
      { value: '有', label: '有' }
    ]
  },

  height: {
    label: '身高',
    type: 'number',
    unit: 'cm',
    dbColumn: 'height',
    templateVar: 'height',
    placeholder: '例如: 165'
  },

  weight: {
    label: '体重',
    type: 'number',
    unit: 'kg',
    dbColumn: 'weight',
    templateVar: 'weight',
    placeholder: '例如: 60'
  },

  gaofang_address: {
    label: '可接收膏方的收货地址',
    type: 'text',
    dbColumn: 'gaofang_address',
    templateVar: 'gaofang_address',
    section: '基本信息',
    placeholder: '如：XX省XX市XX区XX路XX号'
  },

  // ==================== （二）乳腺结节影像学与临床信息登记 ====================

  discovery_date: {
    label: '结节发现时间',
    type: 'date',
    dbColumn: 'breast_discovery_date',  // 对应数据库字段
    templateVar: 'discovery_date',
    required: true,
    section: '影像学特征'
  },

  symptoms: {
    label: '结节症状',
    type: 'checkbox-group',
    dbColumn: 'symptoms',
    templateVar: 'symptoms',
    section: '影像学特征',
    options: [
      '无症状',
      '乳房肿块',
      '乳房疼痛',
      '乳房胀满感',
      '乳头溢液',
      '乳房皮肤改变',
      '腋下淋巴结肿大',
      '其他'
    ],
    otherField: 'symptoms_other',
    otherPlaceholder: '请输入其他症状'
  },

  birads_level: {
    label: 'BI-RADS分级',
    type: 'radio',
    dbColumn: 'birads_level',
    templateVar: 'birads_level',
    required: true,
    section: '影像学特征',
    options: [
      { value: '不清楚', label: '不清楚' },
      { value: '1', label: '1级' },
      { value: '2', label: '2级' },
      { value: '3', label: '3级' },
      { value: '4A', label: '4A级' },
      { value: '4B', label: '4B级' },
      { value: '4C', label: '4C级' },
      { value: '5', label: '5级' },
      { value: '6', label: '6级' }
    ]
  },

  nodule_quantity: {
    label: '数量',
    type: 'radio',
    dbColumn: 'nodule_quantity',
    templateVar: 'nodule_quantity',
    section: '影像学特征',
    options: [
      { value: '单发', label: '单发' },
      { value: '多发', label: '多发' }
    ]
  },

  nodule_count: {
    label: '多发结节个数',
    type: 'number',
    dbColumn: 'nodule_count',
    templateVar: 'nodule_count',
    section: '影像学特征',
    placeholder: '例如: 3',
    showWhen: { field: 'nodule_quantity', value: '多发' }  // 条件显示
  },

  nodule_size: {
    label: '结节大小',
    type: 'number',
    unit: 'mm',
    dbColumn: 'nodule_size',
    templateVar: 'nodule_size',
    section: '影像学特征',
    placeholder: '例如: 12.5'
  },

  history: {
    label: '基础疾病史',
    type: 'checkbox-group',
    dbColumn: 'breast_disease_history',  // 对应数据库字段
    templateVar: 'history',
    section: '影像学特征',
    options: [
      '无',
      '乳腺增生病史',
      '乳腺纤维瘤病史',
      '乳腺囊肿病史',
      '乳腺炎病史',
      '乳腺癌病史',
      '其他'
    ],
    otherField: 'breast_disease_history_other',
    otherPlaceholder: '请输入其他基础疾病史'
  },

  family_history: {
    label: '家族史',
    type: 'checkbox-group',
    dbColumn: 'family_history',
    templateVar: 'family_history',
    section: '影像学特征',
    options: [
      '无',
      '一级亲属（父母、子女、亲兄弟姐妹）',
      '二级亲属（伯父、姑妈、舅舅、姨妈、祖父母）',
      '三级亲属（表/堂兄妹）',
      '其他'
    ],
    otherField: 'family_history_other',
    otherPlaceholder: '请输入其他家族史'
  },

  medication_history: {
    label: '药物使用史',
    type: 'checkbox-group',
    dbColumn: 'medication_history',
    templateVar: 'medication_history',
    section: '影像学特征',
    options: [
      '无',
      '中成药治疗',
      '激素调节药物',
      '维生素辅助治疗',
      '乳腺癌治疗药物',
      '其他'
    ],
    otherField: 'medication_other',
    otherPlaceholder: '请输入其他药物使用史'
  },

  // ==================== "其他"选项的输入字段 ====================
  symptoms_other: {
    label: '',
    type: 'hidden', // 隐藏字段，只用于存储
    dbColumn: 'symptoms_other',
    templateVar: 'symptoms_other',
    section: '影像学特征'
  },
  breast_disease_history_other: {
    label: '',
    type: 'hidden',
    dbColumn: 'breast_disease_history_other',
    templateVar: 'breast_disease_history_other',
    section: '影像学特征'
  },
  family_history_other: {
    label: '',
    type: 'hidden',
    dbColumn: 'family_history_other',
    templateVar: 'family_history_other',
    section: '影像学特征'
  },
  medication_other: {
    label: '',
    type: 'hidden',
    dbColumn: 'medication_other',
    templateVar: 'medication_other',
    section: '影像学特征'
  }
}

/**
 * 根据 section 分组字段
 * @returns {Object} 按section分组的字段配置
 */
export function getFieldsBySection() {
  const sections = {
    '基本信息': [],
    '影像学特征': []
  }

  Object.entries(BREAST_FIELDS).forEach(([key, config]) => {
    const section = config.section || '基本信息'
    sections[section].push({ key, ...config })
  })

  return sections
}

/**
 * 获取表单初始值
 * @returns {Object} 表单初始值对象
 */
export function getInitialFormData() {
  const formData = {}

  Object.entries(BREAST_FIELDS).forEach(([key, config]) => {
    const fieldName = config.dbColumn

    if (config.type === 'checkbox-group') {
      formData[fieldName] = []
    } else if (config.type === 'number') {
      formData[fieldName] = null
    } else if (config.type === 'hidden') {
      // 隐藏字段初始化为空字符串
      formData[fieldName] = ''
    } else {
      formData[fieldName] = ''
    }
  })

  formData.phone = ''

  return formData
}
