import { computed, reactive, ref } from 'vue'

export function useWecomBinding({
  activePatient,
  apiJson,
  queue,
  toast,
}) {
  const wecomModalOpen = ref(false)
  const wecomBindingPatientId = ref('')
  const wecomBindingSaving = ref(false)
  const wecomForm = reactive({
    external_userid: '',
    userid: '',
  })

  const wecomBindingPatient = computed(() => {
    return queue.value.find((p) => p.id === wecomBindingPatientId.value) || activePatient.value || null
  })

  function isWecomBound(p) {
    return p?.wecomBindStatus === 'bound' || !!p?.wecomExternalUserid || !!p?.wecomUserid
  }

  function wecomStatusText(p) {
    return isWecomBound(p) ? '已绑定' : '未绑定'
  }

  function applyWecomBinding(patientData) {
    const apiId = patientData?.id
    const target = queue.value.find((p) => p._apiId === apiId || p.id === apiId)
    if (!target) return
    target.wecomExternalUserid = patientData.wecom_external_userid || ''
    target.wecomUserid = patientData.wecom_userid || ''
    target.wecomBindStatus = patientData.wecom_bind_status || (target.wecomExternalUserid || target.wecomUserid ? 'bound' : 'unbound')
    target.wecomBoundAt = patientData.wecom_bound_at || ''
  }

  function openWecomBind(p = activePatient.value) {
    if (!p?._apiId) {
      toast?.show('演示患者暂不支持绑定企业微信身份')
      return
    }
    wecomBindingPatientId.value = p.id
    wecomForm.external_userid = p.wecomExternalUserid || ''
    wecomForm.userid = p.wecomUserid || ''
    wecomModalOpen.value = true
  }

  async function submitWecomBind() {
    const p = wecomBindingPatient.value
    if (!p?._apiId) return
    const externalUserid = String(wecomForm.external_userid || '').trim()
    const userid = String(wecomForm.userid || '').trim()
    if (!externalUserid && !userid) {
      toast?.show('请至少填写 external_userid 或 userid')
      return
    }
    wecomBindingSaving.value = true
    try {
      const data = await apiJson(`/api/b/patients/${p._apiId}/wecom-bind`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wecom_external_userid: externalUserid,
          wecom_userid: userid,
        }),
      })
      applyWecomBinding(data)
      wecomModalOpen.value = false
      toast?.show('企业微信身份已绑定')
    } catch (e) {
      toast?.show(e.message || '绑定企业微信身份失败')
    } finally {
      wecomBindingSaving.value = false
    }
  }

  async function unbindWecom(p = activePatient.value) {
    if (!p?._apiId) {
      toast?.show('演示患者暂不支持解绑企业微信身份')
      return
    }
    if (!window.confirm(`确认解绑 ${p.name || '该患者'} 的企业微信身份？`)) return
    try {
      const data = await apiJson(`/api/b/patients/${p._apiId}/wecom-bind`, { method: 'DELETE' })
      applyWecomBinding(data)
      toast?.show('企业微信身份已解绑')
    } catch (e) {
      toast?.show(e.message || '解绑企业微信身份失败')
    }
  }

  return {
    isWecomBound,
    openWecomBind,
    submitWecomBind,
    unbindWecom,
    wecomBindingPatient,
    wecomBindingSaving,
    wecomForm,
    wecomModalOpen,
    wecomStatusText,
  }
}
