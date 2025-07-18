// src/store/modules/toast.js
import { toast } from 'vue3-toastify'
import 'vue3-toastify/dist/index.css'

const state = {}

const actions = {
  success(_, payload) {
    const message = typeof payload === 'string' ? payload : payload.message
    const duration = typeof payload === 'object' && payload.duration ? payload.duration : 3000

    toast.success(message, {
      autoClose: duration,
      position: 'top-right',
    })
  },

  error(_, payload) {
    const message = typeof payload === 'string' ? payload : payload.message
    const duration = typeof payload === 'object' && payload.duration ? payload.duration : 4000

    toast.error(message, {
      autoClose: duration,
      position: 'top-right',
    })
  },

  info(_, payload) {
    const message = typeof payload === 'string' ? payload : payload.message
    const duration = typeof payload === 'object' && payload.duration ? payload.duration : 3000

    toast.info(message, {
      autoClose: duration,
      position: 'top-right',
    })
  },

  warning(_, payload) {
    const message = typeof payload === 'string' ? payload : payload.message
    const duration = typeof payload === 'object' && payload.duration ? payload.duration : 3000

    toast.warning(message, {
      autoClose: duration,
      position: 'top-right',
    })
  },
}

export default {
  namespaced: true,
  state,
  actions,
}
