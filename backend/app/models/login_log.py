"""
登录日志数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class LoginLog(Base):
    """登录日志模型"""
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    login_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    login_method = Column(String(50))
    status = Column(String(20))
    failure_reason = Column(String(500))
