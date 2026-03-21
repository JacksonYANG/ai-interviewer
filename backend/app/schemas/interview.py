"""
面试配置相关的Pydantic schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


class InterviewConfigCreate(BaseModel):
    """创建面试配置请求"""
    position_name: str = Field(..., min_length=2, max_length=200, description="职位名称")
    company_name: Optional[str] = Field(None, max_length=200, description="公司名称")
    job_description: Optional[str] = Field(None, max_length=2000, description="职位描述")
    position_level: Optional[str] = Field(
        None,
        pattern="^(junior|middle|senior|expert|director)$",
        description="职位级别"
    )
    company_type: Optional[str] = Field(
        None,
        pattern="^(startup|sme|large|foreign)$",
        description="公司类型"
    )
    industry: Optional[str] = Field(None, max_length=100, description="行业")
    salary_range: Optional[str] = Field(None, max_length=100, description="薪资范围")
    actual_rounds: int = Field(..., ge=2, le=5, description="实际面试轮数")
    is_template: bool = Field(False, description="是否保存为模板")
    template_name: Optional[str] = Field(None, max_length=200, description="模板名称")


class InterviewRoundCreate(BaseModel):
    """创建面试轮次请求"""
    round_number: int = Field(..., ge=1, le=5, description="轮次编号")
    interviewer_role: str = Field(..., min_length=2, max_length=100, description="面试官角色")
    role_description: Optional[str] = Field(None, max_length=1000, description="角色描述")
    question_count: int = Field(6, ge=3, le=10, description="问题数量")
    scoring_weights: Optional[str] = Field(None, max_length=500, description="评分权重配置")


class InterviewConfigUpdate(BaseModel):
    """更新面试配置请求"""
    position_name: Optional[str] = Field(None, min_length=2, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    job_description: Optional[str] = Field(None, max_length=2000)
    position_level: Optional[str] = Field(
        None,
        pattern="^(junior|middle|senior|expert|director)$"
    )
    company_type: Optional[str] = Field(
        None,
        pattern="^(startup|sme|large|foreign)$"
    )
    industry: Optional[str] = Field(None, max_length=100)
    salary_range: Optional[str] = Field(None, max_length=100)
    actual_rounds: Optional[int] = Field(None, ge=2, le=5)
    is_template: Optional[bool] = None
    template_name: Optional[str] = Field(None, max_length=200)


class InterviewRoundResponse(BaseModel):
    """面试轮次响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    round_number: int
    interviewer_role: str
    role_description: Optional[str]
    question_count: int
    scoring_weights: Optional[str]


class InterviewConfigResponse(BaseModel):
    """面试配置响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    position_name: str
    company_name: Optional[str]
    job_description: Optional[str]
    position_level: Optional[str]
    company_type: Optional[str]
    industry: Optional[str]
    salary_range: Optional[str]
    ai_suggested_rounds: Optional[int]
    actual_rounds: int
    is_template: bool
    template_name: Optional[str]
    created_at: datetime


class InterviewConfigDetail(InterviewConfigResponse):
    """面试配置详情(包含轮次)"""
    rounds: List[InterviewRoundResponse]


class AIAnalysisRequest(BaseModel):
    """AI分析请求"""
    position_name: str = Field(..., min_length=2, max_length=200)
    position_level: Optional[str] = Field(None, pattern="^(junior|middle|senior|expert|director)$")
    company_type: Optional[str] = Field(None, pattern="^(startup|sme|large|foreign)$")
    industry: Optional[str] = Field(None, max_length=100)
    salary_range: Optional[str] = Field(None, max_length=100)
    job_description: Optional[str] = Field(None, max_length=2000)


class AIRoundRecommendation(BaseModel):
    """AI推荐的面试轮次"""
    round_number: int
    interviewer_role: str
    role_description: str
    question_count: int
    reasoning: str


class AIAnalysisResponse(BaseModel):
    """AI分析响应"""
    suggested_rounds: int
    reasoning: str
    rounds: List[AIRoundRecommendation]


class LLMConfig(BaseModel):
    """LLM配置"""
    provider: str = Field(..., pattern="^(qwen|openai|anthropic)$")
    api_key: str = Field(..., min_length=10)
    base_url: Optional[str] = Field(None, max_length=500)
    model_name: str = Field(..., min_length=2, max_length=100)
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(2000, ge=100, le=8000)


# ==================== 面试会话相关 ====================

class InterviewSessionCreate(BaseModel):
    """创建面试会话请求"""
    config_id: int = Field(..., description="面试配置ID")
    round_id: int = Field(..., description="面试轮次ID")


class InterviewSessionResponse(BaseModel):
    """面试会话响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    config_id: int
    round_id: int
    user_id: int
    status: str
    current_question_index: int
    total_questions: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class QuestionResponse(BaseModel):
    """问题响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    question_text: str
    question_type: str
    category: Optional[str]
    difficulty: Optional[str]
    expected_points: Optional[str]
    time_limit: Optional[int]
    display_order: int


class AnswerSubmit(BaseModel):
    """提交答案请求"""
    question_id: int = Field(..., description="问题ID")
    text_answer: Optional[str] = Field(None, max_length=5000, description="文字答案")
    audio_file_id: Optional[int] = Field(None, description="音频文件ID")
    answered_at: datetime = Field(default_factory=datetime.now)


class AnswerResponse(BaseModel):
    """答案响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    question_id: int
    text_answer: Optional[str]
    audio_file_id: Optional[int]
    answered_at: datetime


class SessionCompleteRequest(BaseModel):
    """完成会话请求"""
    notes: Optional[str] = Field(None, max_length=2000, description="用户备注")


class SessionCompleteResponse(BaseModel):
    """完成会话响应"""
    session_id: int
    status: str
    completed_at: datetime
    total_answers: int
    message: str


# ==================== 评分相关 ====================

class ScoreRequest(BaseModel):
    """评分请求"""
    question_id: int = Field(..., description="问题ID")
    answer_text: str = Field(..., min_length=10, max_length=5000, description="答案文本")
    audio_duration: Optional[int] = Field(None, ge=0, description="音频时长（秒）")
    expected_duration: Optional[int] = Field(None, ge=0, description="期望时长（秒）")


class ScoreResponse(BaseModel):
    """评分响应"""
    question_id: int
    professional_score: float = Field(..., ge=0, le=100, description="专业能力评分")
    communication_score: float = Field(..., ge=0, le=100, description="沟通表达评分")
    confidence_score: float = Field(..., ge=0, le=100, description="面试状态评分")
    time_score: float = Field(..., ge=0, le=100, description="时间控制评分")
    total_score: float = Field(..., ge=0, le=100, description="总分")
    ai_feedback: str = Field(..., description="AI反馈")
    improvement_suggestions: str = Field(..., description="改进建议")


class ScoreDetailResponse(BaseModel):
    """评分详情响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    professional_score: float
    communication_score: float
    confidence_score: float
    time_score: float
    total_score: float
    ai_feedback: str
    improvement_suggestions: str
    scored_at: datetime


# ==================== 报告相关 ====================

class InterviewReportRequest(BaseModel):
    """生成面试报告请求"""
    session_id: int = Field(..., description="会话ID")


class ReportStrength(BaseModel):
    """报告亮点"""
    category: str = Field(..., description="亮点类别")
    description: str = Field(..., description="亮点描述")


class ReportImprovement(BaseModel):
    """报告改进建议"""
    category: str = Field(..., description="改进类别")
    suggestion: str = Field(..., description="改进建议")
    priority: str = Field(..., pattern="^(high|medium|low)$", description="优先级")


class InterviewReportResponse(BaseModel):
    """面试报告响应"""
    session_id: int
    candidate_name: str
    position_name: str
    overall_score: float
    total_questions: int
    answered_questions: int

    # 分项评分
    average_professional_score: float
    average_communication_score: float
    average_confidence_score: float
    average_time_score: float

    # 总结
    summary: str

    # 亮点
    strengths: List[ReportStrength]

    # 改进建议
    improvements: List[ReportImprovement]

    # 详细评分
    question_scores: List[ScoreDetailResponse]

    # 生成时间
    generated_at: datetime
