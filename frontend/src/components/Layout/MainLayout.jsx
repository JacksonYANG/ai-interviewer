import { useState, useEffect } from 'react'
import { Layout, Menu, theme, Button, Dropdown, message } from 'antd'
import {
  DashboardOutlined,
  SettingOutlined,
  UnorderedListOutlined,
  UserOutlined,
  LogoutOutlined,
  KeyOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import apiClient from '@/services/api'

const { Header, Content, Sider } = Layout

function MainLayout({ children }) {
  const [collapsed, setCollapsed] = useState(false)
  const [userRole, setUserRole] = useState('user')
  const navigate = useNavigate()
  const location = useLocation()

  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  useEffect(() => {
    // 获取用户信息
    const fetchUserInfo = async () => {
      try {
        const user_id = localStorage.getItem('user_id')
        if (user_id) {
          // 这里可以添加获取用户信息的API
          // 暂时从localStorage读取（登录时应该保存用户角色）
          const token = localStorage.getItem('token')
          if (token) {
            // 解析token获取用户信息（简化版）
            // 实际应该调用API获取用户信息
            const payload = JSON.parse(atob(token.split('.')[1]))
            // 这里可以添加获取用户角色的逻辑
          }
        }
      } catch (error) {
        console.error('获取用户信息失败', error)
      }
    }

    fetchUserInfo()
  }, [])

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/interview-config',
      icon: <SettingOutlined />,
      label: '面试配置',
    },
    {
      key: '/interviews',
      icon: <UnorderedListOutlined />,
      label: '面试列表',
    },
  ]

  // 只有管理员才能看到的管理菜单
  if (userRole === 'admin') {
    menuItems.push({
      key: '/admin/invitation-codes',
      icon: <KeyOutlined />,
      label: '邀请码管理',
    })
  }

  const handleMenuClick = ({ key }) => {
    // 检查管理员权限
    if (key === '/admin/invitation-codes' && userRole !== 'admin') {
      message.warning('只有管理员可以访问此页面')
      return
    }
    navigate(key)
  }

  // 获取当前选中的菜单项
  const getSelectedKey = () => {
    const path = location.pathname
    if (path.startsWith('/interview-config')) return '/interview-config'
    if (path.startsWith('/interview/')) return '/interviews'
    if (path.startsWith('/admin/')) return path
    return path
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_id')
    navigate('/login')
  }

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div
          style={{
            height: 32,
            margin: 16,
            color: '#fff',
            fontSize: 20,
            fontWeight: 'bold',
            textAlign: 'center',
          }}
        >
          {collapsed ? 'AI' : 'AI面试官'}
        </div>
        <Menu
          theme="dark"
          selectedKeys={[getSelectedKey()]}
          mode="inline"
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <h2 style={{ margin: 0 }}>智能面试练习系统</h2>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Button icon={<UserOutlined />}>
              {userRole === 'admin' ? '管理员' : '个人中心'}
            </Button>
          </Dropdown>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout
