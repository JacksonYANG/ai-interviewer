import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Typography, Descriptions, List, Tag, Table, Spin, Button, message } from 'antd'
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, Tooltip
} from 'recharts'
import { getSessionReport } from '@/services/interviewService'
import './Report.css'

const { Title, Text } = Typography

function Report() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReport()
  }, [sessionId])

  const loadReport = async () => {
    try {
      setLoading(true)
      const data = await getSessionReport(sessionId)
      setReport(data)
    } catch (error) {
      message.error('加载报告失败')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="report-loading">
        <Spin size="large" tip="加载报告中..." />
      </div>
    )
  }

  if (!report) {
    return (
      <div className="report-error">
        <Text>报告加载失败</Text>
        <Button onClick={() => navigate('/dashboard')}>返回仪表盘</Button>
      </div>
    )
  }

  // 雷达图数据
  const radarData = [
    { subject: '专业能力', score: report.average_professional_score, fullMark: 100 },
    { subject: '沟通表达', score: report.average_communication_score, fullMark: 100 },
    { subject: '自信程度', score: report.average_confidence_score, fullMark: 100 },
    { subject: '时间管理', score: report.average_time_score, fullMark: 100 },
  ]

  // 问题评分表格列定义
  const columns = [
    {
      title: '问题',
      dataIndex: 'question_text',
      key: 'question_text',
      ellipsis: true,
      width: 300,
    },
    {
      title: '专业',
      dataIndex: 'professional_score',
      key: 'professional_score',
      width: 80,
      render: (score) => <Tag color={score >= 80 ? 'green' : score >= 60 ? 'blue' : 'red'}>{score}</Tag>
    },
    {
      title: '沟通',
      dataIndex: 'communication_score',
      key: 'communication_score',
      width: 80,
      render: (score) => <Tag color={score >= 80 ? 'green' : score >= 60 ? 'blue' : 'red'}>{score}</Tag>
    },
    {
      title: '自信',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      width: 80,
      render: (score) => <Tag color={score >= 80 ? 'green' : score >= 60 ? 'blue' : 'red'}>{score}</Tag>
    },
    {
      title: '时间',
      dataIndex: 'time_score',
      key: 'time_score',
      width: 80,
      render: (score) => <Tag color={score >= 80 ? 'green' : score >= 60 ? 'blue' : 'red'}>{score}</Tag>
    },
    {
      title: '总分',
      dataIndex: 'overall_score',
      key: 'overall_score',
      width: 80,
      render: (score) => <Tag color={score >= 80 ? 'green' : score >= 60 ? 'blue' : 'red'}>{score.toFixed(1)}</Tag>
    },
  ]

  const priorityColors = {
    high: 'red',
    medium: 'orange',
    low: 'blue'
  }

  return (
    <div className="report-container">
      <div className="report-header">
        <Title level={2}>面试报告</Title>
        <Button onClick={() => navigate('/dashboard')}>返回仪表盘</Button>
      </div>

      {/* 总览卡片 */}
      <Card className="report-overview">
        <Descriptions column={2}>
          <Descriptions.Item label="候选人">{report.candidate_name}</Descriptions.Item>
          <Descriptions.Item label="职位">{report.position_name}</Descriptions.Item>
          <Descriptions.Item label="总分">
            <span className="overall-score">{report.overall_score.toFixed(1)}</span>
          </Descriptions.Item>
          <Descriptions.Item label="回答问题">{report.answered_questions} / {report.total_questions}</Descriptions.Item>
        </Descriptions>
      </Card>

      <div className="report-content">
        {/* 雷达图 */}
        <Card title="能力维度分析" className="report-radar">
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" />
              <PolarRadiusAxis angle={30} domain={[0, 100]} />
              <Radar
                name="得分"
                dataKey="score"
                stroke="#1890ff"
                fill="#1890ff"
                fillOpacity={0.6}
              />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </Card>

        {/* 总结 */}
        <Card title="综合评价" className="report-summary">
          <Text>{report.summary}</Text>
        </Card>

        {/* 优势 */}
        <Card title="优势亮点" className="report-strengths">
          <List
            dataSource={report.strengths}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  title={item.title}
                  description={item.description}
                />
              </List.Item>
            )}
          />
        </Card>

        {/* 改进建议 */}
        <Card title="改进建议" className="report-improvements">
          <List
            dataSource={report.improvements}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <>
                      {item.title}
                      <Tag color={priorityColors[item.priority]} style={{ marginLeft: 8 }}>
                        {item.priority === 'high' ? '高' : item.priority === 'medium' ? '中' : '低'}
                      </Tag>
                    </>
                  }
                  description={item.description}
                />
              </List.Item>
            )}
          />
        </Card>

        {/* 问题评分详情 */}
        <Card title="问题评分详情" className="report-details">
          <Table
            columns={columns}
            dataSource={report.question_scores}
            rowKey="question_id"
            pagination={false}
            scroll={{ x: 700 }}
          />
        </Card>
      </div>
    </div>
  )
}

export default Report
