"""
报告生成服务 - 面试报告生成
"""
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from app.schemas.interview import (
    InterviewReportResponse,
    ReportStrength,
    ReportImprovement,
    ScoreDetailResponse
)
from app.models.interview_session import InterviewSession
from app.models.interview_config import InterviewConfig
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)


class ReportGenerationService:
    """报告生成服务类"""

    def __init__(self, db: Session):
        """
        初始化报告生成服务

        Args:
            db: 数据库会话
        """
        self.db = db

    async def generate_report(self, session_id: int) -> InterviewReportResponse:
        """
        生成面试报告

        Args:
            session_id: 面试会话ID

        Returns:
            面试报告响应
        """
        try:
            # 获取会话信息
            session = self.db.query(InterviewSession).filter(
                InterviewSession.id == session_id
            ).first()

            if not session:
                raise ValueError(f"会话不存在: {session_id}")

            # 获取配置信息
            config = self.db.query(InterviewConfig).filter(
                InterviewConfig.id == session.config_id
            ).first()

            # 获取用户信息
            user = self.db.query(User).filter(User.id == session.user_id).first()

            # 获取所有问题和答案
            questions = self.db.query(Question).filter(
                Question.session_id == session_id
            ).all()

            # 获取所有评分
            scores = self.db.query(Score).filter(
                Score.question_id.in_([q.id for q in questions])
            ).all()

            # 计算平均分
            avg_scores = self._calculate_average_scores(scores)

            # 生成总结
            summary = await self._generate_summary(session, config, avg_scores)

            # 生成亮点
            strengths = await self._generate_strengths(avg_scores, scores)

            # 生成改进建议
            improvements = await self._generate_improvements(avg_scores, scores)

            # 构建评分详情
            question_scores = [
                ScoreDetailResponse(
                    id=score.id,
                    question_id=score.question_id,
                    professional_score=score.professional_score,
                    communication_score=score.communication_score,
                    confidence_score=score.confidence_score,
                    time_score=score.time_score,
                    total_score=score.total_score,
                    ai_feedback=score.ai_feedback,
                    improvement_suggestions=score.improvement_suggestions,
                    scored_at=score.scored_at
                )
                for score in scores
            ]

            return InterviewReportResponse(
                session_id=session_id,
                candidate_name=user.username if user else "未知",
                position_name=config.position_name if config else "未知职位",
                overall_score=avg_scores["total"],
                total_questions=len(questions),
                answered_questions=len(scores),
                average_professional_score=avg_scores["professional"],
                average_communication_score=avg_scores["communication"],
                average_confidence_score=avg_scores["confidence"],
                average_time_score=avg_scores["time"],
                summary=summary,
                strengths=strengths,
                improvements=improvements,
                question_scores=question_scores,
                generated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            raise

    def _calculate_average_scores(self, scores: List[Score]) -> Dict[str, float]:
        """
        计算平均分

        Args:
            scores: 评分列表

        Returns:
            平均分字典
        """
        if not scores:
            return {
                "professional": 0.0,
                "communication": 0.0,
                "confidence": 0.0,
                "time": 0.0,
                "total": 0.0
            }

        total_count = len(scores)
        return {
            "professional": round(sum(s.professional_score for s in scores) / total_count, 2),
            "communication": round(sum(s.communication_score for s in scores) / total_count, 2),
            "confidence": round(sum(s.confidence_score for s in scores) / total_count, 2),
            "time": round(sum(s.time_score for s in scores) / total_count, 2),
            "total": round(sum(s.total_score for s in scores) / total_count, 2)
        }

    async def _generate_summary(
        self,
        session: InterviewSession,
        config: InterviewConfig,
        avg_scores: Dict[str, float]
    ) -> str:
        """
        生成面试总结

        Args:
            session: 面试会话
            config: 面试配置
            avg_scores: 平均分

        Returns:
            总结文本
        """
        total_score = avg_scores["total"]

        # 根据总分生成不同的总结
        if total_score >= 90:
            level = "优秀"
            summary = f"""
面试表现优秀！

本次面试中，候选人在{config.position_name if config else '该职位'}的面试中表现出色。
总体得分{total_score:.1f}分，展现出扎实的专业功底和良好的面试技巧。

各维度表现均衡，特别是{self._get_strongest_aspect(avg_scores)}方面表现突出。
建议在后续面试中继续保持这种状态。
            """.strip()
        elif total_score >= 80:
            level = "良好"
            summary = f"""
面试表现良好。

本次面试中，候选人在{config.position_name if config else '该职位'}的面试中表现良好。
总体得分{total_score:.1f}分，展现出较好的专业能力和沟通技巧。

各维度表现较为均衡，{self._get_strongest_aspect(avg_scores)}是主要优势。
建议针对薄弱环节进行针对性提升。
            """.strip()
        elif total_score >= 70:
            level = "中等"
            summary = f"""
面试表现中等。

本次面试中，候选人在{config.position_name if config else '该职位'}的面试中表现中等。
总体得分{total_score:.1f}分，基本满足职位要求。

在{self._get_strongest_aspect(avg_scores)}方面表现较好，但仍有提升空间。
建议加强练习，特别是在{self._get_weakest_aspect(avg_scores)}方面。
            """.strip()
        else:
            level = "需要提升"
            summary = f"""
面试表现需要提升。

本次面试中，候选人在{config.position_name if config else '该职位'}的面试中表现有待提升。
总体得分{total_score:.1f}分，距离职位要求还有一定差距。

建议在多个方面进行系统性的提升，特别是{self._get_weakest_aspect(avg_scores)}。
建议多进行模拟面试练习，积累经验。
            """.strip()

        return summary

    async def _generate_strengths(
        self,
        avg_scores: Dict[str, float],
        scores: List[Score]
    ) -> List[ReportStrength]:
        """
        生成面试亮点

        Args:
            avg_scores: 平均分
            scores: 评分列表

        Returns:
            亮点列表
        """
        strengths = []

        # 找出得分最高的两个维度
        dimension_scores = {
            "专业能力": avg_scores["professional"],
            "沟通表达": avg_scores["communication"],
            "面试状态": avg_scores["confidence"],
            "时间控制": avg_scores["time"]
        }

        # 按分数排序
        sorted_dimensions = sorted(
            dimension_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # 添加前两个作为亮点
        for dimension, score in sorted_dimensions[:2]:
            if score >= 75:
                strengths.append(ReportStrength(
                    category=dimension,
                    description=f"{dimension}得分{score:.1f}分，表现优秀"
                ))
            elif score >= 65:
                strengths.append(ReportStrength(
                    category=dimension,
                    description=f"{dimension}得分{score:.1f}分，表现良好"
                ))

        # 如果没有明显亮点，添加一条
        if not strengths:
            max_dimension, max_score = sorted_dimensions[0]
            strengths.append(ReportStrength(
                category=max_dimension,
                description=f"{max_dimension}相对较好，得分{max_score:.1f}分"
            ))

        return strengths

    async def _generate_improvements(
        self,
        avg_scores: Dict[str, float],
        scores: List[Score]
    ) -> List[ReportImprovement]:
        """
        生成改进建议

        Args:
            avg_scores: 平均分
            scores: 评分列表

        Returns:
            改进建议列表
        """
        improvements = []

        # 找出得分最低的两个维度
        dimension_scores = {
            "专业能力": avg_scores["professional"],
            "沟通表达": avg_scores["communication"],
            "面试状态": avg_scores["confidence"],
            "时间控制": avg_scores["time"]
        }

        # 按分数排序
        sorted_dimensions = sorted(
            dimension_scores.items(),
            key=lambda x: x[1]
        )

        # 为得分低的维度生成改进建议
        improvement_suggestions = {
            "专业能力": "建议深入学习相关技术栈，多参与实际项目积累经验，关注行业最新动态",
            "沟通表达": "建议练习STAR法则（情境-任务-行动-结果）来组织回答，提升逻辑性和表达清晰度",
            "面试状态": "建议多做模拟面试，增强自信，展现更积极的专业态度",
            "时间控制": "建议练习在规定时间内简洁完整地回答问题，把握重点"
        }

        for dimension, score in sorted_dimensions[:2]:
            if score < 70:
                priority = "high"
            elif score < 80:
                priority = "medium"
            else:
                priority = "low"

            improvements.append(ReportImprovement(
                category=dimension,
                suggestion=improvement_suggestions.get(dimension, "需要持续提升"),
                priority=priority
            ))

        return improvements

    def _get_strongest_aspect(self, avg_scores: Dict[str, float]) -> str:
        """
        获取最强的维度

        Args:
            avg_scores: 平均分

        Returns:
            最强维度名称
        """
        dimension_names = {
            "professional": "专业能力",
            "communication": "沟通表达",
            "confidence": "面试状态",
            "time": "时间控制"
        }

        max_dimension = max(avg_scores.items(), key=lambda x: x[1])
        return dimension_names.get(max_dimension[0], "综合素质")

    def _get_weakest_aspect(self, avg_scores: Dict[str, float]) -> str:
        """
        获取最弱的维度

        Args:
            avg_scores: 平均分

        Returns:
            最弱维度名称
        """
        dimension_names = {
            "professional": "专业能力",
            "communication": "沟通表达",
            "confidence": "面试状态",
            "time": "时间控制"
        }

        min_dimension = min(avg_scores.items(), key=lambda x: x[1])
        return dimension_names.get(min_dimension[0], "综合能力")
