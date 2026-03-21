import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Typography } from 'antd'

const { Title } = Typography

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: 从后端 API 加载统计数据
    // const fetchStats = async () => {
    //   try {
    //     const response = await axios.get('/api/stats')
    //     setStats(response.data)
    //   } catch (error) {
    //     console.error('获取统计数据失败:', error)
    //   } finally {
    //     setLoading(false)
    //   }
    // }
    // fetchStats()

    // 临时模拟数据
    setTimeout(() => {
      setStats({
        totalInterviews: 12,
        completedInterviews: 8,
        averageScore: 85.5,
        pendingInterviews: 4,
      })
      setLoading(false)
    }, 500)
  }, [])

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <Title level={2}>面试系统仪表盘</Title>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <Statistic
              title="总面试次数"
              value={stats?.totalInterviews || 0}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <Statistic
              title="已完成面试"
              value={stats?.completedInterviews || 0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <Statistic
              title="平均分数"
              value={stats?.averageScore || 0}
              precision={1}
              suffix="分"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card loading={loading}>
            <Statistic
              title="待完成面试"
              value={stats?.pendingInterviews || 0}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 后续会添加更多内容,如最近面试列表、分数趋势图等 */}
    </div>
  )
}

export default Dashboard
