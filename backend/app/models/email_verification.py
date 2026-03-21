"""
邮箱验证数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base


class EmailVerification(Base):
    """邮箱验证模型"""
    __tablename__ = "email_verifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    verification_token = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def is_valid(self) -> bool:
        """
        检查验证令牌是否有效

        Returns:
            bool: 令牌是否有效
        """
        if self.verified_at is not None:
            return False
        if self.expires_at < datetime.now(timezone.utc):
            return False
        return True
