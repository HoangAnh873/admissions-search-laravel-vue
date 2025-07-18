// Hiện tại chỉ đang chuyển ngôn ngữ trực tiếp từ Sidebar.vue 
// chưa có xử lý bên trong CSDL nếu sau này cần thì triển khái tiếp phần này

// src/store/modules/language.js 
import axios from '@/config/axios'
import csrf from '@/config/csrf'

const state = {
  language: 'vn'
}

const getters = {
  currentLanguage: (state) => state.language
}

const mutations = {
  SET_LANGUAGE(state, lang) {
    state.language = lang
  }
}

const actions = {
  async changeLanguage({ commit }, lang) {
    await csrf() // nếu bạn cần CSRF trước request

    try {
      // Nếu bạn muốn lưu language vào server (nếu không thì bỏ phần axios)
      await axios.post('/api/user/set-language', { language: lang })

      // Cập nhật trong store
      commit('SET_LANGUAGE', lang)

      // Đồng bộ với i18n
      const { locale } = await import('vue-i18n')
      locale.value = lang
    } catch (error) {
      console.error('Failed to change language:', error)
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
