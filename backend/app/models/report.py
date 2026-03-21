"""
面试报告数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class Report(Base):
    """面试报告模型"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    overall_score = Column(Float, nullable=False)
    radar_chart_data = Column(String(1000))
    dimension_scores = Column(String(1000))
    overall_summary = Column(String(2000))
    strengths = Column(String(2000))
    areas_for_improvement = Column(String(2000))
    detailed_suggestions = Column(String(3000))
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
