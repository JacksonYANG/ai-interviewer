"""
轮次总结数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class RoundSummary(Base):
    """轮次总结模型"""
    __tablename__ = "round_summaries"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    interviewer_role = Column(String(100), nullable=False)
    average_score = Column(Float)
    summary_text = Column(String(2000))
    highlights = Column(String(1000))
    weaknesses = Column(String(1000))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
