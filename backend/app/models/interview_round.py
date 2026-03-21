"""
面试轮次配置数据模型
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from ..database import Base


class InterviewRound(Base):
    """面试轮次配置模型"""
    __tablename__ = "interview_rounds"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("interview_configs.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    interviewer_role = Column(String(100), nullable=False)
    role_description = Column(String(1000))
    question_count = Column(Integer, default=6)
    scoring_weights = Column(String(500))
