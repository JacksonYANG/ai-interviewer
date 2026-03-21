import { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Steps,
  Space,
  Alert,
  Spin,
  Typography,
  Divider,
  Tag,
  Row,
  Col,
  message,
  Modal,
  List,
} from 'antd'
import {
  CheckCircleOutlined,
  LoadingOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import {
  analyzeInterviewRounds,
  createInterviewConfig,
  createInterviewRound,
} from '@/services/interviewService'

const { Title, Text, Paragraph } = Typography
const { Step } = Steps
const { TextArea } = Input
const { Option } = Select

function InterviewConfig() {
  const [form] = Form.useForm()
  const navigate = useNavigate()

  // 步骤状态
  const [currentStep, setCurrentStep] = useState(0)
  const [analyzing, setAnalyzing] = useState(false)
  const [saving, setSaving] = useState(false)

  // AI 分析结果
  const [aiAnalysis, setAiAnalysis] = useState(null)

  // 面试轮次配置
  const [rounds, setRounds] = useState([])
  const [editingRound, setEditingRound] = useState(null)
  const [roundModalVisible, setRoundModalVisible] = useState(false)
  const [roundForm] = Form.useForm()

  // 保存的配置 ID
  const [savedConfigId, setSavedConfigId] = useState(null)

  /**
   * 处理 AI 分析
   */
  const handleAnalyze = async () => {
    try {
      const values = await form.validateFields()
      setAnalyzing(true)

      const requestData = {
        position_name: values.position_name,
        position_level: values.position_level,
        company_type: values.company_type,
        industry: values.industry,
        salary_range: values.salary_range,
        job_description: values.job_description,
      }

      const result = await analyzeInterviewRounds(requestData)

      setAiAnalysis(result)
      setRounds(
        result.rounds.map((round) => ({
          ...round,
          scoring_weights: '',
        }))
      )

      message.success('AI 分析完成！')
      setCurrentStep(1)
    } catch (error) {
      console.error('AI 分析失败:', error)
      message.error('AI 分析失败，请重试')
    } finally {
      setAnalyzing(false)
    }
  }

  /**
   * 跳过 AI 分析，手动配置
   */
  const handleSkipAnalyze = () => {
    setRounds([])
    setCurrentStep(1)
  }

  /**
   * 手动添加轮次
   */
  const handleAddRound = () => {
    setEditingRound(null)
    roundForm.resetFields()
    setRoundModalVisible(true)
  }

  /**
   * 编辑轮次
   */
  const handleEditRound = (round) => {
    setEditingRound(round)
    roundForm.setFieldsValue(round)
    setRoundModalVisible(true)
  }

  /**
   * 删除轮次
   */
  const handleDeleteRound = (roundNumber) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除第 ${roundNumber} 轮面试吗？`,
      onOk: () => {
        setRounds(rounds.filter((r) => r.round_number !== roundNumber))
        message.success('删除成功')
      },
    })
  }

  /**
   * 保存轮次
   */
  const handleSaveRound = () => {
    roundForm.validateFields().then((values) => {
      if (editingRound) {
        // 编辑模式
        setRounds(
          rounds.map((r) =>
            r.round_number === editingRound.round_number
              ? { ...values, round_number: editingRound.round_number }
              : r
          )
        )
        message.success('轮次更新成功')
      } else {
        // 新增模式
        const roundNumber = rounds.length + 1
        setRounds([...rounds, { ...values, round_number }])
        message.success('轮次添加成功')
      }

      setRoundModalVisible(false)
      roundForm.resetFields()
    })
  }

  /**
   * 保存面试配置
   */
  const handleSaveConfig = async () => {
    try {
      // 验证基本信息
      const basicInfo = await form.validateFields()

      // 验证至少有一轮
      if (rounds.length === 0) {
        message.error('请至少添加一轮面试')
        return
      }

      setSaving(true)

      // 创建配置
      const configData = {
        position_name: basicInfo.position_name,
        company_name: basicInfo.company_name,
        job_description: basicInfo.job_description,
        position_level: basicInfo.position_level,
        company_type: basicInfo.company_type,
        industry: basicInfo.industry,
        salary_range: basicInfo.salary_range,
        actual_rounds: rounds.length,
        is_template: basicInfo.is_template || false,
        template_name: basicInfo.template_name,
      }

      const config = await createInterviewConfig(configData)
      setSavedConfigId(config.id)

      // 创建轮次
      for (const round of rounds) {
        await createInterviewRound(config.id, {
          round_number: round.round_number,
          interviewer_role: round.interviewer_role,
          role_description: round.role_description,
          question_count: round.question_count,
          scoring_weights: round.scoring_weights,
        })
      }

      message.success('面试配置保存成功！')
      setCurrentStep(2)
    } catch (error) {
      console.error('保存失败:', error)
      message.error('保存失败，请重试')
    } finally {
      setSaving(false)
    }
  }

  /**
   * 完成配置，返回列表
   */
  const handleFinish = () => {
    navigate('/interviews')
  }

  /**
   * 返回上一步
   */
  const handlePrev = () => {
    setCurrentStep(currentStep - 1)
  }

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <Card>
        <Title level={2}>配置面试流程</Title>
        <Paragraph type="secondary">
          分步配置您的面试流程，AI 会根据职位信息自动推荐合适的面试轮次。
        </Paragraph>

        <Steps current={currentStep} style={{ marginBottom: '32px' }}>
          <Step title="职位信息" description="填写基本信息" />
          <Step title="轮次配置" description="配置面试轮次" />
          <Step title="完成" description="配置完成" />
        </Steps>

        {/* 步骤 1: 职位信息 */}
        {currentStep === 0 && (
          <>
            <Form
              form={form}
              layout="vertical"
              initialValues={{
                position_level: undefined,
                company_type: undefined,
              }}
            >
              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item
                    label="职位名称"
                    name="position_name"
                    rules={[{ required: true, message: '请输入职位名称' }]}
                  >
                    <Input placeholder="例如: 高级前端工程师" />
                  </Form.Item>
                </Col>

                <Col xs={24} md={12}>
                  <Form.Item label="公司名称" name="company_name">
                    <Input placeholder="例如: 字节跳动" />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item label="职位级别" name="position_level">
                    <Select placeholder="请选择职位级别">
                      <Option value="junior">初级</Option>
                      <Option value="middle">中级</Option>
                      <Option value="senior">高级</Option>
                      <Option value="expert">专家</Option>
                      <Option value="director">总监</Option>
                    </Select>
                  </Form.Item>
                </Col>

                <Col xs={24} md={12}>
                  <Form.Item label="公司类型" name="company_type">
                    <Select placeholder="请选择公司类型">
                      <Option value="startup">初创公司</Option>
                      <Option value="sme">中小企业</Option>
                      <Option value="large">大型企业</Option>
                      <Option value="foreign">外企</Option>
                    </Select>
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col xs={24} md={12}>
                  <Form.Item label="行业" name="industry">
                    <Input placeholder="例如: 互联网、金融、医疗" />
                  </Form.Item>
                </Col>

                <Col xs={24} md={12}>
                  <Form.Item label="薪资范围" name="salary_range">
                    <Input placeholder="例如: 20k-35k" />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item label="职位描述" name="job_description">
                <TextArea
                  rows={6}
                  placeholder="请输入职位描述，包括岗位职责、任职要求等信息..."
                />
              </Form.Item>
            </Form>

            <Divider />

            <Space style={{ float: 'right' }}>
              <Button onClick={handleSkipAnalyze}>跳过 AI 分析</Button>
              <Button
                type="primary"
                onClick={handleAnalyze}
                loading={analyzing}
                icon={analyzing ? <LoadingOutlined /> : <CheckCircleOutlined />}
              >
                {analyzing ? 'AI 分析中...' : 'AI 分析轮数'}
              </Button>
            </Space>
          </>
        )}

        {/* 步骤 2: 轮次配置 */}
        {currentStep === 1 && (
          <>
            {aiAnalysis && (
              <Alert
                message="AI 推荐结果"
                description={
                  <div>
                    <Paragraph>
                      <Text strong>推荐轮数: </Text>
                      <Tag color="blue" style={{ fontSize: '16px' }}>
                        {aiAnalysis.suggested_rounds} 轮
                      </Tag>
                    </Paragraph>
                    <Paragraph>
                      <Text strong>推荐理由: </Text>
                      <br />
                      <Text type="secondary">{aiAnalysis.reasoning}</Text>
                    </Paragraph>
                  </div>
                }
                type="info"
                showIcon
                style={{ marginBottom: '24px' }}
              />
            )}

            <div style={{ marginBottom: '16px' }}>
              <Space>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={handleAddRound}
                >
                  添加轮次
                </Button>
                <Text type="secondary">
                  当前共 {rounds.length} 轮面试
                </Text>
              </Space>
            </div>

            <List
              dataSource={rounds}
              renderItem={(round) => (
                <List.Item
                  actions={[
                    <Button
                      type="link"
                      icon={<EditOutlined />}
                      onClick={() => handleEditRound(round)}
                    >
                      编辑
                    </Button>,
                    <Button
                      type="link"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleDeleteRound(round.round_number)}
                    >
                      删除
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    title={`第 ${round.round_number} 轮: ${round.interviewer_role}`}
                    description={
                      <div>
                        <Paragraph style={{ marginBottom: '8px' }}>
                          {round.role_description}
                        </Paragraph>
                        <Space>
                          <Tag>问题数: {round.question_count}</Tag>
                          {round.reasoning && (
                            <Tag color="blue">{round.reasoning}</Tag>
                          )}
                        </Space>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />

            <Divider />

            <Space style={{ float: 'right' }}>
              <Button onClick={handlePrev}>上一步</Button>
              <Button
                type="primary"
                onClick={handleSaveConfig}
                loading={saving}
              >
                {saving ? '保存中...' : '保存配置'}
              </Button>
            </Space>
          </>
        )}

        {/* 步骤 3: 完成 */}
        {currentStep === 2 && (
          <div style={{ textAlign: 'center', padding: '48px 0' }}>
            <CheckCircleOutlined
              style={{ fontSize: '72px', color: '#52c41a', marginBottom: '24px' }}
            />
            <Title level={3}>面试配置保存成功！</Title>
            <Paragraph type="secondary">
              您的面试配置已保存，可以开始面试了。
            </Paragraph>
            <Space>
              <Button onClick={handleFinish}>返回列表</Button>
              <Button type="primary">开始面试</Button>
            </Space>
          </div>
        )}
      </Card>

      {/* 轮次编辑弹窗 */}
      <Modal
        title={editingRound ? '编辑轮次' : '添加轮次'}
        open={roundModalVisible}
        onOk={handleSaveRound}
        onCancel={() => setRoundModalVisible(false)}
        width={600}
      >
        <Form form={roundForm} layout="vertical">
          <Form.Item
            label="面试官角色"
            name="interviewer_role"
            rules={[{ required: true, message: '请输入面试官角色' }]}
          >
            <Select
              placeholder="请选择或输入角色"
              showSearch
              allowClear
              optionFilterProp="children"
            >
              <Option value="业务领导1">业务领导1 (直属领导)</Option>
              <Option value="业务领导2">业务领导2 (同组/跨组)</Option>
              <Option value="部门总监">部门总监</Option>
              <Option value="CP面试官">CP面试官 (跨部门)</Option>
              <Option value="HR">HR</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="角色描述"
            name="role_description"
            rules={[{ required: true, message: '请输入角色描述' }]}
          >
            <TextArea rows={3} placeholder="请输入该面试官的角色和考察重点" />
          </Form.Item>

          <Form.Item
            label="问题数量"
            name="question_count"
            rules={[{ required: true, message: '请输入问题数量' }]}
          >
            <Input type="number" min={3} max={10} placeholder="建议 5-7 个问题" />
          </Form.Item>

          <Form.Item label="评分权重配置 (JSON)" name="scoring_weights">
            <TextArea
              rows={4}
              placeholder='例如: {"技术能力": 40, "沟通能力": 30, "团队协作": 30}'
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default InterviewConfig
