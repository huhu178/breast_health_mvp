<template>
  <section class="login-page">
    <div class="login-brand">
      <div class="login-brand-mark">医</div>
      <div class="login-brand-name">多结节健康管理随访系统</div>
    </div>

    <div class="login-panel-wrap">
      <div class="login-panel">
        <div class="login-title">登录</div>
        <div class="login-sub">请选择登录名称并输入管理员账号</div>

        <div class="login-field">
          <label for="loginOrg">机构类型</label>
          <select id="loginOrg" v-model="org">
            <option v-for="o in ORG_OPTIONS" :key="o.value" :value="o.value">{{ o.label }}</option>
          </select>
        </div>

        <div class="login-field">
          <label for="loginAccount">管理员账户</label>
          <input id="loginAccount" v-model="account" autocomplete="username" @keyup.enter="onLogin" />
        </div>

        <div class="login-field">
          <label for="loginPassword">密码</label>
          <input id="loginPassword" v-model="password" type="password" autocomplete="current-password" @keyup.enter="onLogin" />
        </div>

        <div v-if="errMsg" class="login-err">{{ errMsg }}</div>

        <button class="login-submit" type="button" @click="onLogin" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <div class="login-hint">
          <span>默认账户：admin</span>
          <button type="button" @click="onReset">重置</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 机构选项：key=org_type 传给后端，label=显示名
const ORG_OPTIONS = [
  { value: '医院', label: '医院' },
  { value: '社区', label: '社区卫生服务中心' },
  { value: '药店', label: '药店' },
  { value: '健康体检中心', label: '健康体检中心' },
]

const org = ref('医院')
const account = ref('admin')
const password = ref('123456')
const errMsg = ref('')
const loading = ref(false)

async function onLogin() {
  errMsg.value = ''
  if (!account.value.trim() || !password.value.trim()) {
    errMsg.value = '请输入账户和密码'
    return
  }
  loading.value = true
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        username: account.value.trim(),
        password: password.value,
        org_type: org.value
      })
    })
    const data = await res.json()
    if (data.success) {
      const user = data.data?.user || {}
      localStorage.setItem('proto_org', org.value)
      localStorage.setItem('proto_user', user.real_name || user.username || account.value)
      localStorage.setItem('proto_authed', 'true')
      localStorage.setItem('proto_user_id', user.id || '')
      router.push('/analytics')
    } else {
      errMsg.value = data.message || '登录失败，请检查账户和密码'
    }
  } catch (e) {
    errMsg.value = '网络错误，请确认后端服务已启动'
  } finally {
    loading.value = false
  }
}

function onReset() {
  org.value = '医院'
  account.value = 'admin'
  password.value = '123456'
  errMsg.value = ''
}
</script>

<style scoped>
*{box-sizing:border-box}
.login-page{
  position:fixed;inset:0;z-index:1000;
  background-image:url('/demo13.png');
  background-size:cover;
  background-position:center center;
  display:flex;align-items:center;justify-content:flex-end;
  padding-right:8%;
}
.login-page::after{
  content:"";
  position:absolute;inset:0;
  background:linear-gradient(to right, transparent 30%, rgba(240,247,255,.55) 55%, rgba(248,251,255,.92) 75%, #f8fbff 90%);
  pointer-events:none;
  z-index:0;
}
.login-brand{position:absolute;top:36px;left:44px;display:flex;align-items:center;gap:10px;z-index:2}
.login-brand-mark{width:36px;height:36px;border-radius:10px;background:#155eef;color:#fff;display:grid;place-items:center;font-weight:900;font-size:15px;flex-shrink:0}
.login-brand-name{font-size:18px;font-weight:700;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.35);letter-spacing:.3px}

.login-panel-wrap{position:relative;z-index:1;display:flex;align-items:center;justify-content:center}
.login-panel{width:390px;background:rgba(255,255,255,.96);border:1px solid #dce8f5;border-radius:14px;padding:32px 34px;box-shadow:0 8px 32px rgba(15,23,42,.10),0 1px 3px rgba(15,23,42,.06)}
.login-title{font-size:24px;font-weight:900;color:#111827;margin-bottom:8px}
.login-sub{color:#64748b;margin-bottom:24px}
.login-field{display:flex;flex-direction:column;gap:7px;margin-bottom:14px}
.login-field label{font-weight:750;color:#334155}
.login-field input,.login-field select{height:40px;border:1px solid #d9e2ef;border-radius:5px;padding:0 12px;outline:none;background:#fff;color:#111827}
.login-field input:focus,.login-field select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.1)}
.login-submit{width:100%;height:42px;border:0;border-radius:5px;background:#155eef;color:#fff;font-weight:850;margin-top:8px;cursor:pointer}
.login-submit:hover{background:#0f4fd4}
.login-submit:disabled{background:#93b4f5;cursor:not-allowed}
.login-err{color:#dc2626;font-size:13px;margin-bottom:8px;padding:8px 10px;background:#fef2f2;border-radius:5px;border:1px solid #fecaca}
.login-hint{display:flex;justify-content:space-between;color:#94a3b8;font-size:12px;margin-top:12px}
.login-hint button{border:0;background:transparent;color:#155eef;padding:0;cursor:pointer}
@media(max-width:900px){
  .login-page{justify-content:center;padding-right:0;padding:24px}
}
</style>

