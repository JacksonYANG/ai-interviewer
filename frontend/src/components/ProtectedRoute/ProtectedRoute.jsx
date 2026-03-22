import { Navigate } from 'react-router-dom'

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')

  if (!token) {
    // 未登录，重定向到登录页
    return <Navigate to="/login" replace />
  }

  // 已登录，渲染子组件
  return children
}

export default ProtectedRoute
