// src/store/index.js
import { createStore } from 'vuex'
import auth from './modules/auth'
// import language from './modules/language' //sau này cần thì triển khai lại
import toast from './modules/toast';

const store = createStore({
  modules: {
    auth,
    toast,
  }
})

export default store
