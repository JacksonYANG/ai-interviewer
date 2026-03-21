"""
面试配置相关的API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.interview_config import InterviewConfig
from app.models.interview_round import InterviewRound
from app.models.interview_session import InterviewSession
from app.models.question import Question
from app.models.answer import Answer
from app.models.user import User
from app.schemas.interview import (
    InterviewConfigCreate,
    InterviewConfigUpdate,
    InterviewConfigResponse,
    InterviewConfigDetail,
    InterviewRoundCreate,
    InterviewRoundResponse,
    AIAnalysisRequest,
    AIAnalysisResponse,
    LLMConfig,
    InterviewSessionCreate,
    InterviewSessionResponse,
    QuestionResponse,
    AnswerSubmit,
    AnswerResponse,
    SessionCompleteRequest,
    SessionCompleteResponse,
    ScoreRequest,
    ScoreResponse,
    ScoreDetailResponse,
    InterviewReportResponse,
)
from app.services.ai_service import AIService
from app.services.scoring_service import ScoringService
from app.services.report_service import ReportGenerationService
from app.services.speech_recognition_service import SpeechRecognitionService
from app.core.dependencies import get_current_user
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/interviews", tags=["面试配置"])


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_interview_rounds(
    request: AIAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI分析面试轮数

    根据职位信息，AI自动分析需要几轮面试并给出建议。
    """
    try:
        # TODO: 从用户配置中获取LLM配置
        # 目前使用默认配置
        llm_config = LLMConfig(
            provider="qwen",
            api_key="sk-placeholder",  # 应该从用户配置或环境变量获取
            base_url="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            model_name="qwen-turbo",
            temperature=0.7,
            max_tokens=2000
        )

        ai_service = AIService(llm_config)
        result = await ai_service.analyze_rounds(request)
        await ai_service.close()

        return result

    except Exception as e:
        logger.error(f"AI分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI分析失败: {str(e)}"
        )


@router.post("/configs", response_model=InterviewConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_interview_config(
    config: InterviewConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建面试配置

    创建新的面试配置，可以保存为模板供后续使用。
    """
    try:
        # 创建面试配置
        db_config = InterviewConfig(
            user_id=current_user.id,
            position_name=config.position_name,
            company_name=config.company_name,
            job_description=config.job_description,
            position_level=config.position_level,
            company_type=config.company_type,
            industry=config.industry,
            salary_range=config.salary_range,
            actual_rounds=config.actual_rounds,
            is_template=config.is_template,
            template_name=config.template_name
        )

        db.add(db_config)
        db.commit()
        db.refresh(db_config)

        logger.info(f"用户 {current_user.id} 创建面试配置 {db_config.id}")

        return db_config

    except Exception as e:
        db.rollback()
        logger.error(f"创建面试配置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建面试配置失败: {str(e)}"
        )


@router.get("/configs", response_model=List[InterviewConfigResponse])
async def list_interview_configs(
    is_template: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取面试配置列表

    获取当前用户的所有面试配置，可以按模板筛选。
    """
    try:
        query = db.query(InterviewConfig).filter(
            InterviewConfig.user_id == current_user.id
        )

        if is_template is not None:
            query = query.filter(InterviewConfig.is_template == is_template)

        configs = query.order_by(InterviewConfig.created_at.desc()).all()

        return configs

    except Exception as e:
        logger.error(f"获取面试配置列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取面试配置列表失败: {str(e)}"
        )


@router.get("/configs/{config_id}", response_model=InterviewConfigDetail)
async def get_interview_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取面试配置详情

    获取指定面试配置的详细信息，包含所有轮次。
    """
    try:
        # 获取配置
        config = db.query(InterviewConfig).filter(
            InterviewConfig.id == config_id,
            InterviewConfig.user_id == current_user.id
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试配置不存在"
            )

        # 获取轮次
        rounds = db.query(InterviewRound).filter(
            InterviewRound.config_id == config_id
        ).order_by(InterviewRound.round_number).all()

        # 构建响应
        config_dict = InterviewConfigResponse.model_validate(config).model_dump()
        config_dict["rounds"] = [
            InterviewRoundResponse.model_validate(r).model_dump()
            for r in rounds
        ]

        return config_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取面试配置详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取面试配置详情失败: {str(e)}"
        )


@router.put("/configs/{config_id}", response_model=InterviewConfigResponse)
async def update_interview_config(
    config_id: int,
    config_update: InterviewConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新面试配置

    更新指定的面试配置信息。
    """
    try:
        # 获取配置
        config = db.query(InterviewConfig).filter(
            InterviewConfig.id == config_id,
            InterviewConfig.user_id == current_user.id
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试配置不存在"
            )

        # 更新字段
        update_data = config_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)

        db.commit()
        db.refresh(config)

        logger.info(f"用户 {current_user.id} 更新面试配置 {config_id}")

        return config

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新面试配置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新面试配置失败: {str(e)}"
        )


@router.delete("/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview_config(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除面试配置

    删除指定的面试配置及其所有轮次。
    """
    try:
        # 获取配置
        config = db.query(InterviewConfig).filter(
            InterviewConfig.id == config_id,
            InterviewConfig.user_id == current_user.id
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试配置不存在"
            )

        # 删除轮次（由于外键约束，需要先删除）
        db.query(InterviewRound).filter(
            InterviewRound.config_id == config_id
        ).delete()

        # 删除配置
        db.delete(config)
        db.commit()

        logger.info(f"用户 {current_user.id} 删除面试配置 {config_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除面试配置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除面试配置失败: {str(e)}"
        )


@router.post(
    "/configs/{config_id}/rounds",
    response_model=InterviewRoundResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_interview_round(
    config_id: int,
    round_data: InterviewRoundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    添加面试轮次

    为指定面试配置添加新的面试轮次。
    """
    try:
        # 验证配置存在且属于当前用户
        config = db.query(InterviewConfig).filter(
            InterviewConfig.id == config_id,
            InterviewConfig.user_id == current_user.id
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试配置不存在"
            )

        # 检查轮次是否已存在
        existing = db.query(InterviewRound).filter(
            InterviewRound.config_id == config_id,
            InterviewRound.round_number == round_data.round_number
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"轮次 {round_data.round_number} 已存在"
            )

        # 创建轮次
        db_round = InterviewRound(
            config_id=config_id,
            round_number=round_data.round_number,
            interviewer_role=round_data.interviewer_role,
            role_description=round_data.role_description,
            question_count=round_data.question_count,
            scoring_weights=round_data.scoring_weights
        )

        db.add(db_round)
        db.commit()
        db.refresh(db_round)

        logger.info(f"为配置 {config_id} 添加轮次 {round_data.round_number}")

        return db_round

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"添加面试轮次失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加面试轮次失败: {str(e)}"
        )


@router.put("/configs/{config_id}/rounds/{round_id}", response_model=InterviewRoundResponse)
async def update_interview_round(
    config_id: int,
    round_id: int,
    round_data: InterviewRoundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新面试轮次

    更新指定面试轮次的信息。
    """
    try:
        # 验证配置存在且属于当前用户
        config = db.query(InterviewConfig).filter(
            InterviewConfig.id == config_id,
            InterviewConfig.user_id == current_user.id
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试配置不存在"
            )

        # 获取轮次
        round_obj = db.query(InterviewRound).filter(
            InterviewRound.id == round_id,
            InterviewRound.config_id == config_id
        ).first()

        if not round_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试轮次不存在"
            )

        # 更新字段
        round_obj.round_number = round_data.round_number
        round_obj.interviewer_role = round_data.interviewer_role
        round_obj.role_description = round_data.role_description
        round_obj.question_count = round_data.question_count
        round_obj.scoring_weights = round_data.scoring_weights

        db.commit()
        db.refresh(round_obj)

        logger.info(f"更新轮次 {round_id}")

        return round_obj

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新面试轮次失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新面试轮次失败: {str(e)}"
        )


@router.delete("/configs/{config_id}/rounds/{round_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview_round(
    config_id: int,
    round_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除面试轮次

    删除指定的面试轮次。
    """
    try:
        # 验证配置存在且属于当前用户
        config = db.query(InterviewConfig).filter(
            InterviewConfig.id == config_id,
            InterviewConfig.user_id == current_user.id
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试配置不存在"
            )

        # 获取轮次
        round_obj = db.query(InterviewRound).filter(
            InterviewRound.id == round_id,
            InterviewRound.config_id == config_id
        ).first()

        if not round_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试轮次不存在"
            )

        # 删除轮次
        db.delete(round_obj)
        db.commit()

        logger.info(f"删除轮次 {round_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除面试轮次失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除面试轮次失败: {str(e)}"
        )


# ==================== 面试会话相关 ====================

@router.post("/sessions", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_interview_session(
    session_data: InterviewSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建面试会话

    开始一个新的面试会话，系统会自动生成该轮次的所有问题。
    """
    try:
        # 验证配置存在且属于当前用户
        config = db.query(InterviewConfig).filter(
            InterviewConfig.id == session_data.config_id,
            InterviewConfig.user_id == current_user.id
        ).first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试配置不存在"
            )

        # 验证轮次存在
        round_obj = db.query(InterviewRound).filter(
            InterviewRound.id == session_data.round_id,
            InterviewRound.config_id == session_data.config_id
        ).first()

        if not round_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试轮次不存在"
            )

        # 检查是否有未完成的会话
        existing_session = db.query(InterviewSession).filter(
            InterviewSession.config_id == session_data.config_id,
            InterviewSession.round_id == session_data.round_id,
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == "in_progress"
        ).first()

        if existing_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="存在未完成的面试会话，请先完成或取消"
            )

        # 创建会话
        db_session = InterviewSession(
            config_id=session_data.config_id,
            round_id=session_data.round_id,
            user_id=current_user.id,
            status="in_progress",
            current_question_index=0,
            total_questions=round_obj.question_count
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        # TODO: 使用AI生成问题
        # 这里需要调用AI服务，根据轮次信息生成问题
        # 暂时创建占位问题

        logger.info(f"用户 {current_user.id} 创建面试会话 {db_session.id}")

        return db_session

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建面试会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建面试会话失败: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=InterviewSessionResponse)
async def get_interview_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取面试会话详情

    获取指定面试会话的详细信息。
    """
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试会话不存在"
            )

        return session

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取面试会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取面试会话失败: {str(e)}"
        )


@router.get("/sessions/{session_id}/questions", response_model=List[QuestionResponse])
async def get_session_questions(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取会话的所有问题

    获取指定面试会话的所有问题列表。
    """
    try:
        # 验证会话存在且属于当前用户
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试会话不存在"
            )

        # 获取问题列表
        questions = db.query(Question).filter(
            Question.session_id == session_id
        ).order_by(Question.display_order).all()

        return questions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取问题列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取问题列表失败: {str(e)}"
        )


@router.get("/sessions/{session_id}/current-question", response_model=QuestionResponse)
async def get_current_question(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前问题

    获取面试会话的当前问题（基于current_question_index）。
    """
    try:
        # 验证会话存在且属于当前用户
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试会话不存在"
            )

        if session.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="面试会话未进行中"
            )

        # 获取当前问题
        question = db.query(Question).filter(
            Question.session_id == session_id,
            Question.display_order == session.current_question_index + 1
        ).first()

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="没有更多问题"
            )

        return question

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取当前问题失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取当前问题失败: {str(e)}"
        )


@router.post("/sessions/{session_id}/answers", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def submit_answer(
    session_id: int,
    answer_data: AnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交答案

    提交当前问题的答案（文字或音频）。
    """
    try:
        # 验证会话存在且属于当前用户
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试会话不存在"
            )

        if session.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="面试会话未进行中"
            )

        # 验证问题存在
        question = db.query(Question).filter(
            Question.id == answer_data.question_id,
            Question.session_id == session_id
        ).first()

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="问题不存在"
            )

        # 检查是否已提交答案
        existing_answer = db.query(Answer).filter(
            Answer.session_id == session_id,
            Answer.question_id == answer_data.question_id
        ).first()

        if existing_answer:
            # 更新现有答案
            existing_answer.text_answer = answer_data.text_answer
            existing_answer.audio_file_id = answer_data.audio_file_id
            existing_answer.answered_at = answer_data.answered_at
            db.commit()
            db.refresh(existing_answer)
            logger.info(f"更新会话 {session_id} 问题 {answer_data.question_id} 的答案")
            return existing_answer

        # 创建新答案
        db_answer = Answer(
            session_id=session_id,
            question_id=answer_data.question_id,
            text_answer=answer_data.text_answer,
            audio_file_id=answer_data.audio_file_id,
            answered_at=answer_data.answered_at
        )

        db.add(db_answer)

        # 更新会话的当前问题索引
        if session.current_question_index < session.total_questions - 1:
            session.current_question_index += 1

        db.commit()
        db.refresh(db_answer)

        logger.info(f"提交会话 {session_id} 问题 {answer_data.question_id} 的答案")

        return db_answer

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"提交答案失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交答案失败: {str(e)}"
        )


@router.post("/sessions/{session_id}/complete", response_model=SessionCompleteResponse)
async def complete_session(
    session_id: int,
    request: SessionCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    完成面试会话

    结束当前面试会话，标记为已完成。
    """
    try:
        # 验证会话存在且属于当前用户
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试会话不存在"
            )

        if session.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="面试会话未进行中"
            )

        # 更新会话状态
        session.status = "completed"
        session.completed_at = datetime.now()

        # 保存用户备注（如果有）
        if request.notes:
            session.notes = request.notes

        db.commit()

        # 统计答案数量
        answer_count = db.query(Answer).filter(
            Answer.session_id == session_id
        ).count()

        logger.info(f"用户 {current_user.id} 完成面试会话 {session_id}")

        return SessionCompleteResponse(
            session_id=session_id,
            status="completed",
            completed_at=session.completed_at,
            total_answers=answer_count,
            message="面试会话已完成"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"完成面试会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"完成面试会话失败: {str(e)}"
        )


# ==================== 评分相关 ====================

@router.post("/score", response_model=ScoreResponse)
async def score_answer(
    score_request: ScoreRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    对答案进行360度评分

    基于专业能力、沟通表达、面试状态、时间控制四个维度进行评分。
    """
    try:
        # 验证问题存在
        from app.models.question import Question
        question = db.query(Question).filter(
            Question.id == score_request.question_id
        ).first()

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="问题不存在"
            )

        # 创建评分服务
        scoring_service = ScoringService(db)

        # 计算评分
        score_result = await scoring_service.calculate_score(
            question_id=score_request.question_id,
            answer_text=score_request.answer_text,
            audio_duration=score_request.audio_duration,
            expected_duration=score_request.expected_duration
        )

        # 保存评分
        scoring_service.save_score(score_result)

        logger.info(f"为问题 {score_request.question_id} 评分完成: {score_result.total_score}")

        return score_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"评分失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评分失败: {str(e)}"
        )


@router.get("/questions/{question_id}/score", response_model=ScoreDetailResponse)
async def get_question_score(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取问题的评分详情

    获取指定问题的详细评分信息。
    """
    try:
        from app.services.scoring_service import ScoringService

        scoring_service = ScoringService(db)
        score = scoring_service.get_question_score(question_id)

        if not score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评分不存在"
            )

        return score

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取评分失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评分失败: {str(e)}"
        )


# ==================== 报告相关 ====================

@router.post("/sessions/{session_id}/report", response_model=InterviewReportResponse)
async def generate_interview_report(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成面试报告

    基于面试会话生成详细的面试报告，包括评分、总结、亮点和改进建议。
    """
    try:
        # 验证会话存在且属于当前用户
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="面试会话不存在"
            )

        # 创建报告生成服务
        report_service = ReportGenerationService(db)

        # 生成报告
        report = await report_service.generate_report(session_id)

        logger.info(f"为会话 {session_id} 生成报告")

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成报告失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成报告失败: {str(e)}"
        )


# ==================== 语音识别相关 ====================

@router.post("/transcribe-audio")
async def transcribe_audio(
    audio_file: bytes,
    format: str = "wav",
    current_user: User = Depends(get_current_user)
):
    """
    音频转文字

    将音频文件转换为文字，支持多种格式。
    """
    try:
        # TODO: 从用户配置中获取语音识别配置
        # 目前使用默认配置
        speech_service = SpeechRecognitionService(
            provider="aliyun",
            api_key="placeholder"  # 应该从环境变量或用户配置获取
        )

        # 转录音频
        text = await speech_service.transcribe_audio(audio_file, format)
        await speech_service.close()

        return {"text": text}

    except Exception as e:
        logger.error(f"音频转录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"音频转录失败: {str(e)}"
        )
