"""
问题数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class Question(Base):
    """问题模型"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(String(2000), nullable=False)
    interviewer_role = Column(String(100), nullable=False)
    question_type = Column(String(50))
    ai_generated = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
