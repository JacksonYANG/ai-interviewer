import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Space,
  Tag,
  Statistic,
  Row,
  Col,
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  StopOutlined,
  CopyOutlined,
} from '@ant-design/icons'
import apiClient from '@/services/api'

function AdminInvitationCodes() {
  const [codes, setCodes] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    fetchCodes()
    fetchStats()
  }, [])

  const fetchCodes = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/admin/invitation-codes/list?limit=100')
      setCodes(response)
    } catch (error) {
      message.error('加载邀请码失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await apiClient.get('/admin/invitation-codes/stats')
      setStats(response)
    } catch (error) {
      console.error('加载统计失败', error)
    }
  }

  const handleCreate = async (values) => {
    try {
      await apiClient.post('/admin/invitation-codes/create', {
        code_type: values.code_type,
        max_uses: values.max_uses,
        notes: values.notes,
        expires_in_days: values.expires_in_days,
      })

      message.success('邀请码创建成功')
      setIsModalVisible(false)
      form.resetFields()
      fetchCodes()
      fetchStats()
    } catch (error) {
      message.error(error.response?.data?.detail || '创建失败')
    }
  }

  const handleDeactivate = async (codeId) => {
    try {
      await apiClient.post(`/admin/invitation-codes/deactivate/${codeId}`)
      message.success('邀请码已停用')
      fetchCodes()
      fetchStats()
    } catch (error) {
      message.error('停用失败')
    }
  }

  const copyToClipboard = (code) => {
    navigator.clipboard.writeText(code)
    message.success('邀请码已复制到剪贴板')
  }

  const columns = [
    {
      title: '邀请码',
      dataIndex: 'code',
      key: 'code',
      render: (text, record) => (
        <Space>
          <Tag color={record.is_active ? 'green' : 'red'}>{text}</Tag>
          <Button
            type="text"
            icon={<CopyOutlined />}
            onClick={() => copyToClipboard(text)}
            size="small"
          />
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'code_type',
      key: 'code_type',
      render: (type) => {
        const typeMap = {
          one_time: '一次性',
          limited: '有限次数',
          unlimited: '无限次'
        }
        return <Tag>{typeMap[type] || type}</Tag>
      },
    },
    {
      title: '使用情况',
      key: 'usage',
      render: (_, record) => (
        <span>
          {record.used_count} / {record.max_uses === null ? '∞' : record.max_uses}
        </span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'success' : 'error'}>
          {isActive ? '有效' : '已停用'}
        </Tag>
      ),
    },
    {
      title: '备注',
      dataIndex: 'notes',
      key: 'notes',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          {record.is_active && (
            <Button
              danger
              size="small"
              icon={<StopOutlined />}
              onClick={() => handleDeactivate(record.id)}
            >
              停用
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总邀请码" value={stats?.total || 0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="有效邀请码" value={stats?.active || 0} valueStyle={{ color: '#3f8600' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="已停用" value={stats?.inactive || 0} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="无限次邀请码"
              value={stats?.by_type?.unlimited || 0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="邀请码管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsModalVisible(true)}
          >
            创建邀请码
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={codes}
          loading={loading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      <Modal
        title="创建邀请码"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="code_type"
            label="邀请码类型"
            rules={[{ required: true, message: '请选择类型' }]}
          >
            <Select placeholder="请选择类型">
              <Select.Option value="one_time">一次性（使用后失效）</Select.Option>
              <Select.Option value="limited">有限次数（可设置使用次数）</Select.Option>
              <Select.Option value="unlimited">无限次（永久有效）</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) => {
              return prevValues?.code_type !== currentValues?.code_type
            }}
          >
            {({ getFieldValue }) =>
              getFieldValue('code_type') === 'limited' ? (
              <Form.Item
                name="max_uses"
                label="最大使用次数"
                rules={[{ required: true, message: '请输入使用次数' }]}
              >
                <InputNumber min={1} max={1000} placeholder="请输入使用次数" style={{ width: '100%' }} />
              </Form.Item>
            ) : null
            }
          </Form.Item>

          <Form.Item name="notes" label="备注">
            <Input.TextArea placeholder="请输入备注（可选）" rows={4} />
          </Form.Item>

          <Form.Item name="expires_in_days" label="有效期（天）">
            <InputNumber min={1} max={3650} placeholder="留空表示永不过期" style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default AdminInvitationCodes
