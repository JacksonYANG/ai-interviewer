"""
回答数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class Answer(Base):
    """回答模型"""
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), unique=True, nullable=False)
    transcript = Column(String(5000))
    audio_file_path = Column(String(500))
    duration_seconds = Column(Integer)
    answered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
