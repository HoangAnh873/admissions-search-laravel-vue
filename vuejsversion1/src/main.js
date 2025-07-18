import './assets/backend/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store' 

import UIkit from 'uikit'
import Icons from 'uikit/dist/js/uikit-icons'

import  Vue3Toastify  from 'vue3-toastify'
import 'vue3-toastify/dist/index.css'

import { createI18n } from 'vue-i18n'
import vn from '@/lang/vn/sidebar'
import en from '@/lang/en/sidebar'

const i18n = createI18n({
  legacy: false, // dùng Composition API
  locale: 'vn',  // ngôn ngữ mặc định
  messages: {
    vn,
    en,
  }
})

UIkit.use(Icons)

const app = createApp(App)

app.use(router)
app.use(store)
app.use(i18n)
app.use(Vue3Toastify, {
  autoClose: 3000,
  position: 'top-right',
})

app.mount('#app')
