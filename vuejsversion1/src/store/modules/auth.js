// src/store/modules/auth.js
import axios from '@/config/axios'
import csrf from '@/config/csrf'

const state = {
  token: sessionStorage.getItem('auth_token') || null,
  user: JSON.parse(sessionStorage.getItem('auth_user')) || null,
}

const mutations = {
  setToken(state, token) {
    state.token = token
    sessionStorage.setItem('auth_token', token)
  },
  setUser(state, user) {
    state.user = user
    sessionStorage.setItem('auth_user', JSON.stringify(user))
  },
  logout(state) {
    state.token = null
    state.user = null
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('auth_user')
  },
}

const getters = {
  isAuthenticated: state => !!state.token,
  getUser: state => state.user,
}

const actions = {
  async login({ commit }, { email, password }) {
    try {
      await csrf.getCookie()

      const { token, user } = await axios.post('/api/auth/login', { email, password })

      if (token && user) {
        commit('setToken', token)
        commit('setUser', user)
        return { success: true }
      } else {
        throw new Error('Token hoặc user không tồn tại trong phản hồi')
      }
    } catch (error) {
      console.error('Lỗi đăng nhập:', error)
      throw error
    }
  },

  logout({ commit }) {
    commit('logout')
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}
