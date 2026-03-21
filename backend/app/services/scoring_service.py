"""
评分服务 - 360度评分系统
"""
from typing import Dict, Optional
from app.schemas.interview import ScoreRequest, ScoreResponse
from app.models.score import Score
from app.models.question import Question
from app.models.answer import Answer
from sqlalchemy.orm import Session
from app.core.logger import get_logger
import json

logger = get_logger(__name__)


class ScoringService:
    """评分服务类 - 实现360度评分"""

    # 评分权重配置
    SCORE_WEIGHTS = {
        "professional": 0.35,      # 专业能力 35%
        "communication": 0.30,     # 沟通表达 30%
        "confidence": 0.20,        # 面试状态 20%
        "time": 0.15              # 时间控制 15%
    }

    def __init__(self, db: Session):
        """
        初始化评分服务

        Args:
            db: 数据库会话
        """
        self.db = db

    async def calculate_score(
        self,
        question_id: int,
        answer_text: str,
        audio_duration: Optional[int] = None,
        expected_duration: Optional[int] = None
    ) -> ScoreResponse:
        """
        计算单个问题的360度评分

        Args:
            question_id: 问题ID
            answer_text: 答案文本
            audio_duration: 音频时长（秒）
            expected_duration: 期望时长（秒）

        Returns:
            评分响应
        """
        try:
            # 获取问题信息
            question = self.db.query(Question).filter(Question.id == question_id).first()
            if not question:
                raise ValueError(f"问题不存在: {question_id}")

            # 计算各项评分
            professional_score = await self._score_professional_ability(
                question.question_text,
                answer_text,
                question.round_number
            )

            communication_score = await self._score_communication(answer_text)

            confidence_score = await self._score_confidence(answer_text)

            time_score = await self._score_time_control(
                audio_duration,
                expected_duration
            )

            # 计算总分（加权平均）
            total_score = (
                professional_score * self.SCORE_WEIGHTS["professional"] +
                communication_score * self.SCORE_WEIGHTS["communication"] +
                confidence_score * self.SCORE_WEIGHTS["confidence"] +
                time_score * self.SCORE_WEIGHTS["time"]
            )

            # 生成AI反馈
            ai_feedback = await self._generate_feedback(
                question.question_text,
                answer_text,
                professional_score,
                communication_score,
                confidence_score
            )

            # 生成改进建议
            improvement_suggestions = await self._generate_improvement_suggestions(
                professional_score,
                communication_score,
                confidence_score,
                time_score
            )

            return ScoreResponse(
                question_id=question_id,
                professional_score=round(professional_score, 2),
                communication_score=round(communication_score, 2),
                confidence_score=round(confidence_score, 2),
                time_score=round(time_score, 2),
                total_score=round(total_score, 2),
                ai_feedback=ai_feedback,
                improvement_suggestions=improvement_suggestions
            )

        except Exception as e:
            logger.error(f"计算评分失败: {str(e)}")
            raise

    async def _score_professional_ability(
        self,
        question_text: str,
        answer_text: str,
        round_number: int
    ) -> float:
        """
        评分专业能力（35%权重）

        评分维度：
        - 技术深度：是否展示出深入的技术理解
        - 问题解决：能否有效分析和解决问题
        - 经验匹配：过往经验与职位要求的匹配度
        - 学习能力：是否展示出持续学习的态度

        Args:
            question_text: 问题文本
            answer_text: 答案文本
            round_number: 面试轮次

        Returns:
            专业能力评分（0-100）
        """
        # 基础分数
        base_score = 60.0

        # 关键词评分
        technical_keywords = [
            "架构", "设计", "优化", "性能", "安全",
            "算法", "数据结构", "系统", "框架", "工具",
            "经验", "项目", "实践", "解决", "实现"
        ]

        keyword_count = sum(1 for keyword in technical_keywords if keyword in answer_text)
        keyword_score = min(keyword_count * 3, 20)  # 最多20分

        # 答案长度评分（过短扣分）
        length_score = 0
        if len(answer_text) >= 500:
            length_score = 10
        elif len(answer_text) >= 300:
            length_score = 7
        elif len(answer_text) >= 100:
            length_score = 5
        else:
            length_score = -5

        # 结构化评分（是否有条理）
        structure_indicators = ["首先", "其次", "最后", "总之", "另外", "此外"]
        structure_count = sum(1 for indicator in structure_indicators if indicator in answer_text)
        structure_score = min(structure_count * 2, 10)

        total_score = base_score + keyword_score + length_score + structure_score
        return max(0, min(100, total_score))

    async def _score_communication(self, answer_text: str) -> float:
        """
        评分沟通表达（30%权重）

        评分维度：
        - 清晰度：表达是否清晰易懂
        - 逻辑性：回答是否有逻辑性
        - 完整性：是否完整回答问题
        - 语言组织：语言是否流畅

        Args:
            answer_text: 答案文本

        Returns:
            沟通表达评分（0-100）
        """
        base_score = 60.0

        # 逻辑性评分
        logic_indicators = ["因为", "所以", "因此", "由于", "导致", "从而"]
        logic_count = sum(1 for indicator in logic_indicators if indicator in answer_text)
        logic_score = min(logic_count * 3, 15)

        # 完整性评分（基于句子数量）
        sentences = answer_text.split("。")
        sentence_count = len([s for s in sentences if len(s.strip()) > 0])
        if sentence_count >= 5:
            completeness_score = 15
        elif sentence_count >= 3:
            completeness_score = 10
        else:
            completeness_score = 5

        # 语言流畅度评分（避免重复词语）
        words = answer_text.split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            fluency_score = unique_ratio * 10
        else:
            fluency_score = 0

        total_score = base_score + logic_score + completeness_score + fluency_score
        return max(0, min(100, total_score))

    async def _score_confidence(self, answer_text: str) -> float:
        """
        评分面试状态（20%权重）

        评分维度：
        - 自信度：是否表现出自信
        - 积极性：是否积极主动
        - 专业度：是否展现专业素养
        - 态度：是否有良好的面试态度

        Args:
            answer_text: 答案文本

        Returns:
            面试状态评分（0-100）
        """
        base_score = 60.0

        # 自信表达
        confident_indicators = ["我认为", "我相信", "我的经验", "我建议", "我建议"]
        confident_count = sum(1 for indicator in confident_indicators if indicator in answer_text)
        confident_score = min(confident_count * 5, 20)

        # 积极性表达
        positive_indicators = ["学习", "改进", "提升", "优化", "发展"]
        positive_count = sum(1 for indicator in positive_indicators if indicator in answer_text)
        positive_score = min(positive_count * 3, 10)

        # 专业度表达
        professional_indicators = ["根据", "基于", "参考", "遵循", "按照"]
        professional_count = sum(1 for indicator in professional_indicators if indicator in answer_text)
        professional_score = min(professional_count * 2, 10)

        total_score = base_score + confident_score + positive_score + professional_score
        return max(0, min(100, total_score))

    async def _score_time_control(
        self,
        audio_duration: Optional[int],
        expected_duration: Optional[int]
    ) -> float:
        """
        评分时间控制（15%权重）

        评分维度：
        - 时间合理性：是否在合理时间内完成
        - 节奏控制：是否掌握好回答节奏
        - 简洁性：是否简洁明了

        Args:
            audio_duration: 实际音频时长（秒）
            expected_duration: 期望时长（秒）

        Returns:
            时间控制评分（0-100）
        """
        # 如果没有音频时长，给中等分数
        if audio_duration is None:
            return 70.0

        if expected_duration is None:
            expected_duration = 120  # 默认2分钟

        # 计算时间偏差比例
        ratio = audio_duration / expected_duration

        # 时间评分曲线
        if 0.8 <= ratio <= 1.2:
            # 在期望时间的80%-120%之间，优秀
            return 95.0
        elif 0.6 <= ratio <= 1.5:
            # 在期望时间的60%-150%之间，良好
            base = 85.0
            penalty = abs(ratio - 1.0) * 20
            return max(70, base - penalty)
        elif 0.4 <= ratio <= 2.0:
            # 在期望时间的40%-200%之间，及格
            base = 70.0
            penalty = abs(ratio - 1.0) * 15
            return max(50, base - penalty)
        else:
            # 过短或过长，不及格
            return 40.0

    async def _generate_feedback(
        self,
        question_text: str,
        answer_text: str,
        professional_score: float,
        communication_score: float,
        confidence_score: float
    ) -> str:
        """
        生成AI反馈

        Args:
            question_text: 问题文本
            answer_text: 答案文本
            professional_score: 专业能力评分
            communication_score: 沟通表达评分
            confidence_score: 面试状态评分

        Returns:
            AI反馈文本
        """
        feedback_parts = []

        # 专业能力反馈
        if professional_score >= 85:
            feedback_parts.append("✓ 专业能力突出，展示出扎实的技术功底和丰富的实践经验。")
        elif professional_score >= 70:
            feedback_parts.append("✓ 专业能力良好，对相关技术有一定的理解和应用。")
        else:
            feedback_parts.append("△ 需要加强专业技术的学习和实践。")

        # 沟通表达反馈
        if communication_score >= 85:
            feedback_parts.append("✓ 表达清晰有条理，逻辑性强，能够有效传达观点。")
        elif communication_score >= 70:
            feedback_parts.append("✓ 表达基本清晰，可以进一步优化语言组织。")
        else:
            feedback_parts.append("△ 建议加强逻辑性和表达清晰度的训练。")

        # 面试状态反馈
        if confidence_score >= 85:
            feedback_parts.append("✓ 展现出良好的专业素养和积极的面试态度。")
        elif confidence_score >= 70:
            feedback_parts.append("✓ 态度积极，继续保持。")
        else:
            feedback_parts.append("△ 建议在面试中展现更多自信和主动性。")

        return "\n".join(feedback_parts)

    async def _generate_improvement_suggestions(
        self,
        professional_score: float,
        communication_score: float,
        confidence_score: float,
        time_score: float
    ) -> str:
        """
        生成改进建议

        Args:
            professional_score: 专业能力评分
            communication_score: 沟通表达评分
            confidence_score: 面试状态评分
            time_score: 时间控制评分

        Returns:
            改进建议文本
        """
        suggestions = []

        # 找出最需要改进的方面
        scores = {
            "专业能力": professional_score,
            "沟通表达": communication_score,
            "面试状态": confidence_score,
            "时间控制": time_score
        }

        # 按评分排序，找出最弱的两个
        weakest_aspects = sorted(scores.items(), key=lambda x: x[1])[:2]

        for aspect, score in weakest_aspects:
            if score < 70:
                if aspect == "专业能力":
                    suggestions.append(f"• {aspect}：建议深入学习相关技术栈，多参与实际项目积累经验。")
                elif aspect == "沟通表达":
                    suggestions.append(f"• {aspect}：建议练习STAR法则（情境-任务-行动-结果）来组织回答。")
                elif aspect == "面试状态":
                    suggestions.append(f"• {aspect}：建议多做模拟面试，增强自信和表达能力。")
                elif aspect == "时间控制":
                    suggestions.append(f"• {aspect}：建议练习在规定时间内简洁完整地回答问题。")

        if not suggestions:
            suggestions.append("• 各方面表现均衡，继续保持！")

        return "\n".join(suggestions)

    def save_score(self, score_data: ScoreResponse) -> Score:
        """
        保存评分到数据库

        Args:
            score_data: 评分数据

        Returns:
            保存的评分记录
        """
        try:
            score = Score(
                question_id=score_data.question_id,
                professional_score=score_data.professional_score,
                communication_score=score_data.communication_score,
                confidence_score=score_data.confidence_score,
                time_score=score_data.time_score,
                total_score=score_data.total_score,
                ai_feedback=score_data.ai_feedback,
                improvement_suggestions=score_data.improvement_suggestions
            )

            self.db.add(score)
            self.db.commit()
            self.db.refresh(score)

            logger.info(f"评分已保存: 问题ID={score_data.question_id}, 总分={score_data.total_score}")
            return score

        except Exception as e:
            logger.error(f"保存评分失败: {str(e)}")
            self.db.rollback()
            raise

    def get_question_score(self, question_id: int) -> Optional[Score]:
        """
        获取问题的评分

        Args:
            question_id: 问题ID

        Returns:
            评分记录
        """
        return self.db.query(Score).filter(Score.question_id == question_id).first()
