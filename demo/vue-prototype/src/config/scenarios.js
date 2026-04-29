export const SCENARIOS = {
  hospital: {
    key: 'hospital',
    loginLabel: '医院',
    orgType: '医院',
    orgName: '齐鲁医院',
    brandTitle: '医院多结节随访管理系统',
    navPatient: '患者管理',
    queueLabel: '患者队列',
    recordLabel: '患者建档',
    personLabel: '患者',
    reportLabel: '健康报告',
    sourceOptions: ['门诊', '体检中心'],
    importLabel: '从门诊系统导入',
    defaultOwner: '李医生',
    workspaceLabel: '真实世界研究',
    workspacePath: '/rws',
    theme: { primary: '#155eef', soft: '#eef5ff', bg: '#f3f6fb', accent: '#16a34a' },
  },
  checkup: {
    key: 'checkup',
    loginLabel: '健康体检中心',
    orgType: '健康体检中心',
    orgName: '仁康健康体检中心',
    brandTitle: '健康体检中心结节筛查随访系统',
    navPatient: '患者管理',
    queueLabel: '患者队列',
    recordLabel: '患者建档',
    personLabel: '患者',
    reportLabel: '体检解读报告',
    sourceOptions: ['体检套餐', '单位团检', '个人体检', '复查预约'],
    importLabel: '从体检系统导入',
    defaultOwner: '体检医生',
    workspaceLabel: '筛查中心',
    workspacePath: '/scenario-workspace',
    theme: { primary: '#0891b2', soft: '#ecfeff', bg: '#f0fdfa', accent: '#14b8a6' },
  },
  pharmacy: {
    key: 'pharmacy',
    loginLabel: '药店',
    orgType: '药店',
    orgName: '益民连锁药房',
    brandTitle: '药店健康服务随访管理系统',
    navPatient: '患者管理',
    queueLabel: '患者队列',
    recordLabel: '患者建档',
    personLabel: '患者',
    reportLabel: '健康评估报告',
    sourceOptions: ['到店咨询', '购药记录', '慢病服务', '线上问诊'],
    importLabel: '从药店健康服务系统导入',
    defaultOwner: '执业药师',
    workspaceLabel: '药事服务',
    workspacePath: '/scenario-workspace',
    theme: { primary: '#ea580c', soft: '#fff7ed', bg: '#fff7ed', accent: '#16a34a' },
  },
  community: {
    key: 'community',
    loginLabel: '社区家庭医生',
    orgType: '社区',
    orgName: '南城社区家庭医生团队',
    brandTitle: '社区家庭医生随访管理系统',
    navPatient: '患者管理',
    queueLabel: '患者队列',
    recordLabel: '患者建档',
    personLabel: '患者',
    reportLabel: '健康管理报告',
    sourceOptions: ['家庭医生签约', '社区筛查', '上级医院转回', '入户随访'],
    importLabel: '从社区健康档案导入',
    defaultOwner: '家庭医生',
    workspaceLabel: '家医随访',
    workspacePath: '/scenario-workspace',
    theme: { primary: '#4f46e5', soft: '#eef2ff', bg: '#f5f3ff', accent: '#10b981' },
  },
}

export const SCENARIO_OPTIONS = Object.values(SCENARIOS)

export function getScenario(key) {
  return SCENARIOS[key] || SCENARIOS.hospital
}

export function getStoredScenario() {
  return getScenario(localStorage.getItem('proto_scenario') || 'hospital')
}

export function scenarioFromOrgType(orgType) {
  return SCENARIO_OPTIONS.find((s) => s.orgType === orgType) || SCENARIOS.hospital
}
