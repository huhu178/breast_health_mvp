<template>
  <section class="login-page">
    <div class="login-visual">
      <div class="login-pattern" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>
      <div class="login-wave" aria-hidden="true">
        <svg viewBox="0 0 800 260" preserveAspectRatio="none">
          <path d="M0 172 C130 128 235 210 360 158 C500 100 620 150 800 92 L800 260 L0 260 Z" fill="rgba(21,94,239,.20)"/>
          <path d="M0 206 C150 150 270 220 420 170 C560 122 650 170 800 130 L800 260 L0 260 Z" fill="rgba(21,94,239,.14)"/>
          <path d="M0 115 C90 76 168 145 245 104 C340 54 418 136 520 92 C645 38 708 92 800 58" fill="none" stroke="rgba(255,255,255,.72)" stroke-width="2"/>
          <path d="M0 150 C110 105 190 178 305 128 C420 78 515 155 638 105 C720 72 760 83 800 75" fill="none" stroke="rgba(255,255,255,.5)" stroke-width="1.5" stroke-dasharray="3 8"/>
          <g fill="rgba(255,255,255,.9)">
            <circle cx="72" cy="118" r="4"/><circle cx="198" cy="134" r="3"/><circle cx="346" cy="110" r="4"/><circle cx="510" cy="112" r="3"/><circle cx="670" cy="92" r="4"/>
          </g>
        </svg>
      </div>
      <div class="login-visual-inner">
        <div class="login-visual-icon">
          <div class="login-monitor"><span class="login-dots"></span></div>
        </div>
        <div class="login-visual-title">多结节随访管理系统</div>
        <div class="login-visual-sub">多机构统一登录，按场景进入对应工作台</div>
      </div>
    </div>

    <div class="login-panel-wrap">
      <div class="login-panel">
        <div class="login-title">登录</div>
        <div class="login-sub">请选择登录名称并输入管理员账号</div>

        <div class="login-field">
          <label for="loginOrg">登录名称</label>
          <select id="loginOrg" v-model="org">
            <option value="齐鲁医院">医院</option>
            <option value="北城社区卫生服务中心">社区</option>
            <option value="康宁大药房">药店</option>
            <option value="瑞康体检中心">体检中心</option>
          </select>
        </div>

        <div class="login-field">
          <label for="loginAccount">管理员账户</label>
          <input id="loginAccount" v-model="account" autocomplete="username" />
        </div>

        <div class="login-field">
          <label for="loginPassword">密码</label>
          <input id="loginPassword" v-model="password" type="password" autocomplete="current-password" />
        </div>

        <button class="login-submit" type="button" @click="onLogin">登录</button>

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

const org = ref('齐鲁医院')
const account = ref('admin')
const password = ref('123456')

/**
 * @description 登录（原型演示：写入本地标记并跳转）
 */
function onLogin() {
  localStorage.setItem('proto_org', org.value)
  localStorage.setItem('proto_user', account.value || '管理员')
  localStorage.setItem('proto_authed', 'true')
  router.push('/analytics')
}

/**
 * @description 重置登录表单到默认值
 */
function onReset() {
  org.value = '齐鲁医院'
  account.value = 'admin'
  password.value = '123456'
}
</script>

<style scoped>
*{box-sizing:border-box}
.login-page{position:fixed;inset:0;z-index:1000;display:grid;grid-template-columns:minmax(420px,1fr) minmax(420px,1fr);background:#f6f9ff;overflow:hidden}
.login-page::before{content:"";position:absolute;left:0;right:0;bottom:0;height:34%;pointer-events:none;background:
  radial-gradient(ellipse at 26% 100%,rgba(21,94,239,.24),transparent 52%),
  repeating-linear-gradient(165deg,rgba(21,94,239,.18) 0 1px,transparent 1px 18px);
  opacity:.5}
.login-visual{position:relative;overflow:hidden;background:
  radial-gradient(circle at 20% 18%,rgba(255,255,255,.95),transparent 12%),
  radial-gradient(circle at 38% 34%,rgba(21,94,239,.1),transparent 28%),
  linear-gradient(155deg,#f8fbff 0%,#eaf4ff 48%,#d8eaff 100%);
  color:#155eef;display:flex;align-items:center;justify-content:center;padding:48px}
.login-visual::before{content:"";position:absolute;inset:0;background-image:
  linear-gradient(rgba(21,94,239,.055) 1px,transparent 1px),
  linear-gradient(90deg,rgba(21,94,239,.055) 1px,transparent 1px);
  background-size:34px 34px;mask-image:linear-gradient(90deg,rgba(0,0,0,.85),rgba(0,0,0,.18));}
.login-visual::after{content:"";position:absolute;right:-22%;top:-12%;width:50%;height:124%;background:#f6f9ff;border-radius:50%;box-shadow:-18px 0 0 rgba(21,94,239,.06)}
.login-visual-inner{position:relative;z-index:1;width:min(420px,80%);display:flex;flex-direction:column;align-items:center;text-align:center;transform:translateX(-52px)}
.login-pattern{position:absolute;inset:0;z-index:0;pointer-events:none}
.login-pattern span{position:absolute;width:7px;height:7px;border-radius:50%;background:#fff;box-shadow:0 0 0 5px rgba(255,255,255,.35)}
.login-pattern span::after{content:"";position:absolute;left:7px;top:3px;width:118px;height:1px;background:linear-gradient(90deg,rgba(255,255,255,.85),transparent)}
.login-pattern span:nth-child(1){left:10%;top:22%}
.login-pattern span:nth-child(2){left:28%;top:14%}
.login-pattern span:nth-child(3){left:12%;bottom:30%}
.login-pattern span:nth-child(4){right:26%;top:32%}
.login-pattern span:nth-child(5){right:20%;bottom:22%}
.login-wave{position:absolute;left:0;right:0;bottom:0;height:34%;z-index:0;opacity:.78}
.login-wave svg{width:100%;height:100%;display:block}
.login-visual-icon{width:156px;height:112px;border-radius:14px;background:rgba(255,255,255,.92);border:1px solid #d8e8fb;display:flex;align-items:center;justify-content:center;margin-bottom:28px;box-shadow:0 22px 44px rgba(21,94,239,.14)}
.login-monitor{width:96px;height:64px;border-radius:8px;background:#334155;position:relative;box-shadow:0 12px 0 -7px rgba(21,94,239,.22)}
.login-monitor::before{content:"";position:absolute;inset:9px 12px;background:#fff;border-radius:3px}
.login-monitor::after{content:"";position:absolute;left:43px;bottom:-18px;width:10px;height:18px;background:#4b5563}
.login-dots{position:absolute;z-index:2;width:6px;height:6px;background:#155eef;border-radius:50%;box-shadow:0 14px 0 #80b7ff,0 28px 0 #b5d7ff;left:43px;top:18px}
.login-visual-title{font-size:22px;font-weight:850;letter-spacing:.2px;color:#0f172a;white-space:nowrap}
.login-visual-sub{font-size:13px;color:#64748b;margin-top:10px;white-space:nowrap}
.login-panel-wrap{position:relative;z-index:1;display:flex;align-items:center;justify-content:center;padding:48px;background:#f6f9ff}
.login-panel-wrap::before{content:"";position:absolute;left:-28%;top:-15%;width:54%;height:130%;border-radius:50%;background:#f6f9ff;box-shadow:-20px 0 0 rgba(21,94,239,.05);z-index:-1}
.login-panel{width:390px;background:#fff;border:1px solid #e1e9f5;border-radius:14px;padding:32px 34px;box-shadow:0 26px 70px rgba(15,23,42,.08)}
.login-title{font-size:24px;font-weight:900;color:#111827;margin-bottom:8px}
.login-sub{color:#64748b;margin-bottom:24px}
.login-field{display:flex;flex-direction:column;gap:7px;margin-bottom:14px}
.login-field label{font-weight:750;color:#334155}
.login-field input,.login-field select{height:40px;border:1px solid #d9e2ef;border-radius:5px;padding:0 12px;outline:none;background:#fff;color:#111827}
.login-field input:focus,.login-field select:focus{border-color:#155eef;box-shadow:0 0 0 3px rgba(21,94,239,.1)}
.login-submit{width:100%;height:42px;border:0;border-radius:5px;background:#155eef;color:#fff;font-weight:850;margin-top:8px}
.login-submit:hover{background:#0f4fd4}
.login-hint{display:flex;justify-content:space-between;color:#94a3b8;font-size:12px;margin-top:12px}
.login-hint button{border:0;background:transparent;color:#155eef;padding:0}
@media(max-width:900px){
  .login-page{grid-template-columns:1fr}
  .login-visual{display:none}
  .login-panel-wrap{padding:28px}
}
</style>

