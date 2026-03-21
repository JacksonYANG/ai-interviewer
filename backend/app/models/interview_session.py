"""
面试会话数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class InterviewSession(Base):
    """面试会话模型"""
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("interview_configs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="in_progress")
    current_round = Column(Integer, default=1)
    total_rounds = Column(Integer, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime)
    overall_score = Column(Float)
