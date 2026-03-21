"""
音频文件数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class AudioFile(Base):
    """音频文件模型"""
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_size = Column(Integer)
    duration_seconds = Column(Integer)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
