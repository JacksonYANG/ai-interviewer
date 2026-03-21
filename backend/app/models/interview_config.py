"""
面试配置数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class InterviewConfig(Base):
    """面试配置模型"""
    __tablename__ = "interview_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position_name = Column(String(200), nullable=False)
    company_name = Column(String(200))
    job_description = Column(String(2000))
    position_level = Column(String(50))
    company_type = Column(String(50))
    industry = Column(String(100))
    salary_range = Column(String(100))
    ai_suggested_rounds = Column(Integer)
    actual_rounds = Column(Integer, nullable=False)
    is_template = Column(Boolean, default=False)
    template_name = Column(String(200))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
