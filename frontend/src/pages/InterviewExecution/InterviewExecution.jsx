import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Button,
  Space,
  Typography,
  Steps,
  Alert,
  Spin,
  message,
  Modal,
  Input,
  Progress,
  Divider,
  Tag,
  Row,
  Col,
} from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  CheckCircleOutlined,
  ArrowLeftOutlined,
  AudioOutlined,
} from '@ant-design/icons'
import { AudioRecorder } from '@/components/recording'
import {
  createInterviewSession,
  getCurrentQuestion,
  submitAnswer,
  completeSession,
} from '@/services/interviewService'

const { Title, Text, Paragraph } = Typography
const { TextArea } = Input

function InterviewExecution() {
  const { configId, roundId } = useParams()
  const navigate = useNavigate()

  // 会话状态
  const [session, setSession] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  // 答案状态
  const [textAnswer, setTextAnswer] = useState('')
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [hasRecorded, setHasRecorded] = useState(false)

  // 完成确认弹窗
  const [completeModalVisible, setCompleteModalVisible] = useState(false)
  const [sessionNotes, setSessionNotes] = useState('')

  /**
   * 初始化会话
   */
  const initSession = async () => {
    try {
      setLoading(true)

      // 创建会话
      const sessionData = await createInterviewSession({
        config_id: parseInt(configId),
        round_id: parseInt(roundId),
      })

      setSession(sessionData)
      message.success('面试会话创建成功！')

      // 获取第一个问题
      await fetchCurrentQuestion(sessionData.id)
    } catch (error) {
      console.error('初始化会话失败:', error)
      message.error('初始化会话失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  /**
   * 获取当前问题
   */
  const fetchCurrentQuestion = async (sessionId) => {
    try {
      const question = await getCurrentQuestion(sessionId)
      setCurrentQuestion(question)
      setTextAnswer('')
      setAudioBlob(null)
      setAudioUrl(null)
      setHasRecorded(false)
    } catch (error) {
      console.error('获取问题失败:', error)
      message.error('获取问题失败')
    }
  }

  /**
   * 录音完成回调
   */
  const handleRecordingComplete = (blob, url) => {
    setAudioBlob(blob)
    setAudioUrl(url)
    setHasRecorded(true)
  }

  /**
   * 提交答案
   */
  const handleSubmitAnswer = async () => {
    // 验证至少有一种答案形式
    if (!textAnswer.trim() && !audioBlob) {
      message.warning('请提供文字答案或录音答案')
      return
    }

    try {
      setSubmitting(true)

      // TODO: 如果有音频，需要先上传音频文件
      // 这里暂时只处理文字答案
      const answerData = {
        question_id: currentQuestion.id,
        text_answer: textAnswer || undefined,
        answered_at: new Date().toISOString(),
      }

      // 如果有音频文件，需要先上传
      if (audioBlob) {
        // TODO: 实现音频文件上传
        message.info('音频上传功能开发中，已保存文字答案')
      }

      await submitAnswer(session.id, answerData)
      message.success('答案提交成功！')

      // 判断是否还有下一个问题
      if (session.current_question_index < session.total_questions - 1) {
        // 获取下一个问题
        await fetchCurrentQuestion(session.id)
        // 更新会话状态
        setSession((prev) => ({
          ...prev,
          current_question_index: prev.current_question_index + 1,
        }))
      } else {
        // 所有问题已完成，显示完成确认
        setCompleteModalVisible(true)
      }
    } catch (error) {
      console.error('提交答案失败:', error)
      message.error('提交答案失败，请重试')
    } finally {
      setSubmitting(false)
    }
  }

  /**
   * 完成面试会话
   */
  const handleCompleteSession = async () => {
    try {
      setSubmitting(true)

      await completeSession(session.id, {
        notes: sessionNotes,
      })

      message.success('面试会话已完成！')
      setCompleteModalVisible(false)

      // 跳转到报告页面（暂时跳转到列表）
      navigate('/interviews')
    } catch (error) {
      console.error('完成会话失败:', error)
      message.error('完成会话失败，请重试')
    } finally {
      setSubmitting(false)
    }
  }

  /**
   * 跳过当前问题
   */
  const handleSkipQuestion = async () => {
    Modal.confirm({
      title: '确认跳过',
      content: '确定要跳过当前问题吗？',
      onOk: async () => {
        try {
          setSubmitting(true)

          // 提交空答案
          await submitAnswer(session.id, {
            question_id: currentQuestion.id,
            text_answer: '[跳过]',
            answered_at: new Date().toISOString(),
          })

          message.success('已跳过当前问题')

          // 获取下一个问题
          if (session.current_question_index < session.total_questions - 1) {
            await fetchCurrentQuestion(session.id)
            setSession((prev) => ({
              ...prev,
              current_question_index: prev.current_question_index + 1,
            }))
          } else {
            setCompleteModalVisible(true)
          }
        } catch (error) {
          console.error('跳过失败:', error)
          message.error('跳过失败，请重试')
        } finally {
          setSubmitting(false)
        }
      },
    })
  }

  // 初始化
  useEffect(() => {
    if (configId && roundId) {
      initSession()
    }
  }, [configId, roundId])

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" tip="正在初始化面试会话..." />
      </div>
    )
  }

  if (!session || !currentQuestion) {
    return (
      <div style={{ padding: '24px' }}>
        <Alert
          message="错误"
          description="无法加载面试会话"
          type="error"
          showIcon
        />
      </div>
    )
  }

  // 计算进度
  const progress =
    ((session.current_question_index + 1) / session.total_questions) * 100

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <Card>
        {/* 头部 */}
        <div style={{ marginBottom: '24px' }}>
          <Space style={{ marginBottom: '16px' }}>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/interviews')}
            >
              返回列表
            </Button>
            <Tag color="blue">面试进行中</Tag>
          </Space>

          <Title level={2}>面试执行</Title>

          {/* 进度显示 */}
          <div style={{ marginBottom: '16px' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '8px',
              }}
            >
              <Text strong>
                问题 {session.current_question_index + 1} /{' '}
                {session.total_questions}
              </Text>
              <Text type="secondary">{Math.round(progress)}%</Text>
            </div>
            <Progress percent={progress} status="active" />
          </div>
        </div>

        <Divider />

        {/* 当前问题 */}
        <Card
          title={
            <Space>
              <PlayCircleOutlined />
              <Text strong>当前问题</Text>
            </Space>
          }
          style={{ marginBottom: '24px' }}
        >
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <Text strong style={{ fontSize: '18px' }}>
                {currentQuestion.question_text}
              </Text>
            </div>

            {currentQuestion.category && (
              <Tag color="geekblue">{currentQuestion.category}</Tag>
            )}

            {currentQuestion.expected_points && (
              <div>
                <Text type="secondary">考察要点： </Text>
                <Paragraph type="secondary" style={{ display: 'inline' }}>
                  {currentQuestion.expected_points}
                </Paragraph>
              </div>
            )}

            {currentQuestion.time_limit && (
              <Tag color="orange">
                建议时长：{currentQuestion.time_limit} 分钟
              </Tag>
            )}
          </Space>
        </Card>

        {/* 答案区域 */}
        <Card
          title={
            <Space>
              <AudioOutlined />
              <Text strong>您的回答</Text>
            </Space>
          }
          style={{ marginBottom: '24px' }}
        >
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            {/* 文字答案 */}
            <div>
              <Text strong style={{ marginBottom: '8px', display: 'block' }}>
                文字回答（可选）
              </Text>
              <TextArea
                rows={6}
                placeholder="请输入您的回答..."
                value={textAnswer}
                onChange={(e) => setTextAnswer(e.target.value)}
                maxLength={5000}
                showCount
              />
            </div>

            <Divider orientation="left">或</Divider>

            {/* 录音答案 */}
            <div>
              <Text strong style={{ marginBottom: '8px', display: 'block' }}>
                语音回答（可选）
              </Text>
              <AudioRecorder
                onRecordingComplete={handleRecordingComplete}
                maxDuration={300}
              />
            </div>
          </Space>
        </Card>

        {/* 操作按钮 */}
        <Space style={{ float: 'right' }}>
          <Button onClick={handleSkipQuestion} disabled={submitting}>
            跳过问题
          </Button>
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            onClick={handleSubmitAnswer}
            loading={submitting}
            size="large"
          >
            {submitting ? '提交中...' : '提交答案'}
          </Button>
        </Space>
      </Card>

      {/* 完成确认弹窗 */}
      <Modal
        title="完成面试"
        open={completeModalVisible}
        onOk={handleCompleteSession}
        onCancel={() => setCompleteModalVisible(false)}
        confirmLoading={submitting}
        width={600}
      >
        <div style={{ padding: '16px 0' }}>
          <CheckCircleOutlined
            style={{
              fontSize: '48px',
              color: '#52c41a',
              display: 'block',
              margin: '0 auto 16px',
            }}
          />
          <Title level={4} style={{ textAlign: 'center' }}>
            恭喜！您已完成所有问题
          </Title>
          <Paragraph type="secondary" style={{ textAlign: 'center' }}>
            您已完成 {session.total_questions} 个面试问题，可以结束本次面试了。
          </Paragraph>

          <Divider />

          <div>
            <Text strong style={{ marginBottom: '8px', display: 'block' }}>
              面试备注（可选）
            </Text>
            <TextArea
              rows={4}
              placeholder="记录您对本次面试的备注或感想..."
              value={sessionNotes}
              onChange={(e) => setSessionNotes(e.target.value)}
              maxLength={2000}
            />
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default InterviewExecution
