import { useState } from 'react'
import { Form, Input, Button, Card, Typography, message, Tabs } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined, KeyOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import apiClient from '@/services/api'
import '../../styles/theme.css'

const { Title, Text } = Typography

function Login() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (values) => {
    setLoading(true)
    try {
      const response = await apiClient.post('/auth/login', {
        email: values.email,
        password: values.password,
      })

      // 保存token
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      localStorage.setItem('user_id', response.user_id)

      message.success('登录成功')

      // 跳转到仪表盘
      navigate('/dashboard')
    } catch (error) {
      message.error(error.response?.data?.detail || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'var(--color-bg-secondary)',
    }}>
      <Card
        style={{
          width: 400,
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
          border: '1px solid var(--color-border)',
          borderRadius: 16,
        }}
        bodyStyle={{
          padding: 40,
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title
            level={2}
            style={{
              marginBottom: 8,
              fontSize: 24,
              fontWeight: 600,
              color: 'var(--color-text-primary)',
            }}
          >
            智能面试练习系统
          </Title>
          <Text type="secondary" style={{ fontSize: 14 }}>
            请登录您的账号
          </Text>
        </div>

        <Form
          name="login"
          onFinish={handleLogin}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
            style={{ marginBottom: 16 }}
          >
            <Input
              prefix={<MailOutlined style={{ color: 'var(--color-text-tertiary)' }} />}
              placeholder="邮箱"
              size="large"
              style={{
                borderRadius: 8,
                padding: '12px 16px',
              }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
            style={{ marginBottom: 24 }}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: 'var(--color-text-tertiary)' }} />}
              placeholder="密码"
              size="large"
              style={{
                borderRadius: 8,
                padding: '12px 16px',
              }}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              size="large"
              block
              style={{
                height: 44,
                borderRadius: 8,
                fontWeight: 500,
              }}
            >
              登录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center', fontSize: 14 }}>
            <Text style={{ color: 'var(--color-text-secondary)' }}>
              还没有账号？
            </Text>{' '}
            <a
              onClick={() => navigate('/register')}
              style={{
                color: 'var(--color-primary)',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              立即注册
            </a>
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default Login
