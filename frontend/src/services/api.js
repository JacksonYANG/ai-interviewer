/**
 * API 客户端 - 封装 axios 请求
 */
import axios from 'axios'
import { message } from 'antd'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 添加 token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一错误处理
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config

    // 特殊处理 401 错误 - 尝试刷新token
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          // 尝试使用refresh_token获取新的access_token
          const response = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/auth/refresh`,
            { refresh_token: refreshToken }
          )

          const { access_token, refresh_token: newRefreshToken } = response.data

          // 保存新token
          localStorage.setItem('token', access_token)
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken)
          }

          // 更新请求头中的token
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          originalRequest._retry = true

          // 重试原请求
          return apiClient(originalRequest)
        } catch (refreshError) {
          // 刷新失败，清除所有token并重定向到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user_id')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // 没有refresh_token，直接重定向到登录页
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }

    // 其他错误
    const errorMessage = error.response?.data?.detail || error.message || '请求失败'
    message.error(errorMessage)

    return Promise.reject(error)
  }
)

export default apiClient
