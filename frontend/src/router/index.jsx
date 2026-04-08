import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from '@/pages/Dashboard/Dashboard'
import InterviewConfig from '@/pages/InterviewConfig/InterviewConfig'
import InterviewList from '@/pages/InterviewList/InterviewList'
import InterviewExecution from '@/pages/InterviewExecution/InterviewExecution'
import Login from '@/pages/Login/Login'
import Register from '@/pages/Register/Register'
import AdminInvitationCodes from '@/pages/Admin/AdminInvitationCodes'
import Report from '@/pages/Report/Report'
import MainLayout from '@/components/Layout/MainLayout'
import ProtectedRoute from '@/components/ProtectedRoute/ProtectedRoute'

function Router() {
  return (
    <Routes>
      {/* 认证相关路由 - 不使用MainLayout */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* 受保护的路由 - 使用MainLayout */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Routes>
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

                {/* 报告页面 */}
                <Route path="/report/:sessionId" element={<Report />} />

                {/* 管理员路由 - 仅管理员可访问 */}
                <Route path="/admin/invitation-codes" element={<AdminInvitationCodes />} />

                {/* 默认路由重定向到 Dashboard */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </MainLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default Router
