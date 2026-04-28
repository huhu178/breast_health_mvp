import { createApp } from 'vue'
import './style.css'
// 引入统一设计系统（必须在其他样式之前）
import './assets/styles/design-system.css'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.mount('#app')
