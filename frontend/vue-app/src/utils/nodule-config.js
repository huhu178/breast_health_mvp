/**
 * 结节类型配置
 * 统一管理所有结节类型的配置信息
 * 便于后续扩展和维护
 */

export const NODULE_TYPES = {
  breast: {
    id: 'breast',
    name: '乳腺结节',
    color: '#1e88e5',
    icon: '🫧',
    fields: ['birads_level', 'nodule_size', 'nodule_location', 'nodule_quantity'],
    formComponent: 'BreastFormSection',
    reportTemplate: 'breast_report.html',
    status: 'completed' // 已完成
  },
  lung: {
    id: 'lung',
    name: '肺结节',
    color: '#00acc1',
    icon: '🫁',
    fields: ['lung_rads_level', 'lung_nodule_size', 'lung_nodule_location'],
    formComponent: 'LungFormSection',
    reportTemplate: 'lung_report.html',
    status: 'pending' // 待开发
  },
  thyroid: {
    id: 'thyroid',
    name: '甲状腺结节',
    color: '#26a69a',
    icon: '🦋',
    fields: ['tirads_level', 'thyroid_nodule_size', 'thyroid_nodule_location'],
    formComponent: 'ThyroidFormSection',
    reportTemplate: 'thyroid_report.html',
    status: 'pending' // 待开发
  },
  breast_lung: {
    id: 'breast_lung',
    name: '乳腺+肺',
    color: '#43a047',
    icon: '🫧🫁',
    fields: ['breast', 'lung'],
    formComponent: ['BreastFormSection', 'LungFormSection'],
    reportTemplate: 'breast_lung_report.html',
    status: 'pending' // 待开发
  },
  breast_thyroid: {
    id: 'breast_thyroid',
    name: '乳腺+甲状腺',
    color: '#5e35b1',
    icon: '🫧🦋',
    fields: ['breast', 'thyroid'],
    formComponent: ['BreastFormSection', 'ThyroidFormSection'],
    reportTemplate: 'breast_thyroid_report.html',
    status: 'pending' // 待开发
  },
  lung_thyroid: {
    id: 'lung_thyroid',
    name: '肺+甲状腺',
    color: '#00897b',
    icon: '🫁🦋',
    fields: ['lung', 'thyroid'],
    formComponent: ['LungFormSection', 'ThyroidFormSection'],
    reportTemplate: 'lung_thyroid_report.html',
    status: 'pending' // 待开发
  },
  triple: {
    id: 'triple',
    name: '三结节',
    color: '#00838f',
    icon: '🫧🫁🦋',
    fields: ['breast', 'lung', 'thyroid'],
    formComponent: ['BreastFormSection', 'LungFormSection', 'ThyroidFormSection'],
    reportTemplate: 'triple_report.html',
    status: 'pending' // 待开发
  }
}

/**
 * 获取结节类型配置
 */
export function getNoduleConfig(noduleType) {
  return NODULE_TYPES[noduleType] || null
}

/**
 * 获取结节类型的颜色
 */
export function getNoduleColor(noduleType) {
  const config = getNoduleConfig(noduleType)
  return config?.color || '#1e88e5'
}

/**
 * 获取结节类型的名称
 */
export function getNoduleName(noduleType) {
  const config = getNoduleConfig(noduleType)
  return config?.name || '未知类型'
}

/**
 * 检查是否为组合类型
 */
export function isCombinedType(noduleType) {
  return ['breast_lung', 'breast_thyroid', 'lung_thyroid', 'triple'].includes(noduleType)
}

/**
 * 获取组合类型包含的单个类型
 */
export function getCombinedTypes(noduleType) {
  const mapping = {
    'breast_lung': ['breast', 'lung'],
    'breast_thyroid': ['breast', 'thyroid'],
    'lung_thyroid': ['lung', 'thyroid'],
    'triple': ['breast', 'lung', 'thyroid']
  }
  return mapping[noduleType] || []
}

