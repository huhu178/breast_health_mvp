import { reactive } from 'vue'
import { patients as initialPatients } from '../mocks/patients.js'

export const store = reactive({
  patients: initialPatients.map(p => ({ ...p })),
  currentPatientId: 'p1',
  currentModule: 'workbench',
  org: localStorage.getItem('proto_org') || '齐鲁医院',
  user: localStorage.getItem('proto_user') || '管理员',

  get currentPatient() {
    return this.patients.find(p => p.id === this.currentPatientId) || this.patients[0]
  },

  setStage(patientId, nextStage, eventText) {
    const p = this.patients.find(x => x.id === patientId)
    if (p) {
      p.stage = nextStage
      p.events.push(eventText)
    }
  }
})
