import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    userRole: (state) => state.user?.system_role || null,
  },
  
  actions: {
    async login(email, password) {
      try {
        const response = await api.post('auth/login/', { email, password })
        this.accessToken = response.data.access
        this.refreshToken = response.data.refresh
        this.user = response.data.user
        
        localStorage.setItem('access_token', this.accessToken)
        localStorage.setItem('refresh_token', this.refreshToken)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return true
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },
    
    async logout() {
      try {
        if (this.refreshToken) {
          await api.post('auth/logout/', { refresh: this.refreshToken })
        }
      } catch (error) {
        console.error('Logout error ping:', error)
      } finally {
        this.clearAuth()
      }
    },
    
    clearAuth() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }
})
