import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from '@/pages/Dashboard/Dashboard'
import InterviewConfig from '@/pages/InterviewConfig/InterviewConfig'
import InterviewList from '@/pages/InterviewList/InterviewList'
import InterviewExecution from '@/pages/InterviewExecution/InterviewExecution'

function Router() {
  return (
    <Routes>
      {/* 默认路由重定向到 Dashboard */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Dashboard 页面 */}
      <Route path="/dashboard" element={<Dashboard />} />

      {/* 面试配置相关路由 */}
      <Route path="/interview-config" element={<InterviewConfig />} />
      <Route path="/interview-config/:id" element={<InterviewConfig />} />
      <Route path="/interviews" element={<InterviewList />} />

      {/* 面试执行路由 */}
      <Route
        path="/interview/:configId/round/:roundId/execute"
        element={<InterviewExecution />}
      />

      {/* 后续会添加 Login, Register, Report 等路由 */}
      {/* <Route path="/login" element={<Login />} /> */}
      {/* <Route path="/register" element={<Register />} /> */}
      {/* <Route path="/report/:sessionId" element={<Report />} /> */}

      {/* 404 页面 */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default Router
