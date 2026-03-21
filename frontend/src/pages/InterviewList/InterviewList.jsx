import { useState, useEffect } from 'react'
import { Card, Table, Button, Space, Tag, Typography, message, Modal, Popconfirm, List } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { getInterviewConfigs, deleteInterviewConfig, getInterviewConfigDetail } from '@/services/interviewService'

const { Title, Text } = Typography

function InterviewList() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [configs, setConfigs] = useState([])
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  })

  // 轮次选择弹窗
  const [roundModalVisible, setRoundModalVisible] = useState(false)
  const [selectedConfig, setSelectedConfig] = useState(null)
  const [rounds, setRounds] = useState([])

  /**
   * 加载面试配置列表
   */
  const loadConfigs = async (page = 1, pageSize = 10) => {
    try {
      setLoading(true)
      const data = await getInterviewConfigs({ page, page_size: pageSize })
      setConfigs(data)
      setPagination({
        current: page,
        pageSize,
        total: data.length || 0,
      })
    } catch (error) {
      console.error('加载配置列表失败:', error)
      message.error('加载配置列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConfigs()
  }, [])

  /**
   * 删除配置
   */
  const handleDelete = async (configId) => {
    try {
      await deleteInterviewConfig(configId)
      message.success('删除成功')
      loadConfigs(pagination.current, pagination.pageSize)
    } catch (error) {
      console.error('删除失败:', error)
      message.error('删除失败')
    }
  }

  /**
   * 开始面试 - 显示轮次选择弹窗
   */
  const handleStartInterview = async (config) => {
    try {
      setLoading(true)
      const detail = await getInterviewConfigDetail(config.id)
      setSelectedConfig(config)
      setRounds(detail.rounds || [])
      setRoundModalVisible(true)
    } catch (error) {
      console.error('加载轮次失败:', error)
      message.error('加载轮次失败')
    } finally {
      setLoading(false)
    }
  }

  /**
   * 选择轮次并开始面试
   */
  const handleSelectRound = (roundId) => {
    setRoundModalVisible(false)
    navigate(`/interview/${selectedConfig.id}/round/${roundId}/execute`)
  }

  /**
   * 编辑配置
   */
  const handleEdit = (configId) => {
    navigate(`/interview-config/${configId}`)
  }

  /**
   * 创建新配置
   */
  const handleCreate = () => {
    navigate('/interview-config')
  }

  const columns = [
    {
      title: '职位名称',
      dataIndex: 'position_name',
      key: 'position_name',
      width: 200,
    },
    {
      title: '公司名称',
      dataIndex: 'company_name',
      key: 'company_name',
      width: 150,
      render: (text) => text || '-',
    },
    {
      title: '职位级别',
      dataIndex: 'position_level',
      key: 'position_level',
      width: 100,
      render: (level) => {
        const levelMap = {
          junior: '初级',
          middle: '中级',
          senior: '高级',
          expert: '专家',
          director: '总监',
        }
        return level ? <Tag color="blue">{levelMap[level]}</Tag> : '-'
      },
    },
    {
      title: '面试轮数',
      dataIndex: 'actual_rounds',
      key: 'actual_rounds',
      width: 100,
      render: (rounds) => <Tag color="green">{rounds} 轮</Tag>,
    },
    {
      title: '是否模板',
      dataIndex: 'is_template',
      key: 'is_template',
      width: 100,
      render: (isTemplate) =>
        isTemplate ? <Tag color="purple">模板</Tag> : <Tag>非模板</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleStartInterview(record.id)}
          >
            开始面试
          </Button>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record.id)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确认删除"
            description="确定要删除这个面试配置吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
          <Title level={2} style={{ margin: 0 }}>
            面试配置列表
          </Title>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建配置
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={configs}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => loadConfigs(page, pageSize),
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 轮次选择弹窗 */}
      <Modal
        title="选择面试轮次"
        open={roundModalVisible}
        onCancel={() => setRoundModalVisible(false)}
        footer={null}
        width={600}
      >
        <div>
          <Text strong style={{ marginBottom: '16px', display: 'block' }}>
            {selectedConfig?.position_name} - 共 {rounds.length} 轮面试
          </Text>

          <List
            dataSource={rounds}
            renderItem={(round) => (
              <List.Item
                actions={[
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    onClick={() => handleSelectRound(round.id)}
                  >
                    开始
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  title={`第 ${round.round_number} 轮: ${round.interviewer_role}`}
                  description={
                    <Space>
                      <Text type="secondary">{round.role_description}</Text>
                      <Tag>{round.question_count} 个问题</Tag>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        </div>
      </Modal>
    </div>
  )
}

export default InterviewList
