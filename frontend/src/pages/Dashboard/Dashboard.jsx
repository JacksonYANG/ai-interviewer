import { useEffect, useState } from 'react'
import { Row, Col, Typography } from 'antd'
import StatCard from '@/components/Dashboard/StatCard'

const { Title } = Typography

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const { getUserStats } = await import('@/services/interviewService')
        const data = await getUserStats()
        setStats({
          totalInterviews: data.total_interviews,
          completedInterviews: data.completed_interviews,
          averageScore: data.average_score,
          pendingInterviews: data.pending_interviews,
        })
      } catch (error) {
        console.error('获取统计数据失败:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  return (
    <div>
      <Title
        level={2}
        style={{
          marginBottom: 32,
          fontSize: 24,
          fontWeight: 600,
          color: 'var(--color-text-primary)',
        }}
      >
        面试系统仪表盘
      </Title>

      {/* 统计卡片网格：2x2布局 */}
      <Row gutter={[24, 24]}>
        <Col xs={24} sm={12} lg={12}>
          <StatCard
            label="总面试次数"
            value={stats?.totalInterviews || 0}
            variant="primary"
            loading={loading}
          />
        </Col>

        <Col xs={24} sm={12} lg={12}>
          <StatCard
            label="已完成面试"
            value={stats?.completedInterviews || 0}
            variant="info"
            loading={loading}
          />
        </Col>

        <Col xs={24} sm={12} lg={12}>
          <StatCard
            label="平均分数"
            value={stats?.averageScore || 0}
            unit="分"
            variant="success"
            loading={loading}
          />
        </Col>

        <Col xs={24} sm={12} lg={12}>
          <StatCard
            label="待完成面试"
            value={stats?.pendingInterviews || 0}
            variant="warning"
            loading={loading}
          />
        </Col>
      </Row>

      {/* 后续会添加更多内容,如最近面试列表、分数趋势图等 */}
    </div>
  )
}

export default Dashboard
