"""
评分数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class Score(Base):
    """评分模型"""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), unique=True, nullable=False)
    professional_score = Column(Float)
    communication_score = Column(Float)
    confidence_score = Column(Float)
    time_score = Column(Float)
    total_score = Column(Float)
    ai_feedback = Column(String(2000))
    improvement_suggestions = Column(String(2000))
    scored_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
