// src/middleware/auth.js

import store from '@/store'

export function authMiddleware(to, from, next) {
  let isAuthenticated = store.getters['auth/isAuthenticated']

  // Nếu Vuex chưa có nhưng sessionStorage vẫn còn (do reload)
  if (!isAuthenticated && sessionStorage.getItem('auth_token')) {
    const token = sessionStorage.getItem('auth_token')
    const user = JSON.parse(sessionStorage.getItem('auth_user'))

    store.commit('auth/setToken', token)
    store.commit('auth/setUser', user)
    isAuthenticated = true
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && isAuthenticated) {
    next({ name: 'dashboard.index' })
  } else {
    next()
  }
}
