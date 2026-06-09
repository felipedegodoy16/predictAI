import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Global Loading State Manager
let activeRequests = 0

const updateLoadingState = () => {
  window.dispatchEvent(new CustomEvent('global-loading', { detail: activeRequests > 0 }))
}

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    // Only track non-silent requests
    const isSilent = config.silent || (config.headers && config.headers['X-Silent'])
    if (!isSilent) {
      activeRequests++
      updateLoadingState()
    }
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token expiration (401)
api.interceptors.response.use(
  (response) => {
    const isSilent = response.config.silent || (response.config.headers && response.config.headers['X-Silent'])
    if (!isSilent) {
      activeRequests = Math.max(0, activeRequests - 1)
      updateLoadingState()
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config || {}
    
    const isSilent = originalRequest.silent || (originalRequest.headers && originalRequest.headers['X-Silent'])
    if (!isSilent) {
      activeRequests = Math.max(0, activeRequests - 1)
      updateLoadingState()
    }
    
    // Se o erro foi 401 e não tentamos dar refresh na mesma requisição
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          // Tenta pegar um novo access token usando axios puro (sem passar pelo _retry loop infinito)
          const res = await axios.post('http://localhost:8000/api/auth/refresh/', { 
            refresh: refreshToken 
          })
          
          if (res.status === 200) {
            localStorage.setItem('access_token', res.data.access)
            originalRequest.headers.Authorization = `Bearer ${res.data.access}`
            return api(originalRequest)
          }
        }
      } catch (refreshError) {
        // Se o refresh expirar também, limpar sessão e possivelmente redirecionar (handled pelo App root ou pinia)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
