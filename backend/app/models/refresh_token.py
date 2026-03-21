"""
刷新令牌数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime, timezone
from ..database import Base


class RefreshToken(Base):
    """刷新令牌模型"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    device_info = Column(String(500))

    def is_valid(self) -> bool:
        """
        检查令牌是否有效

        Returns:
            bool: 令牌是否有效
        """
        if self.revoked:
            return False
        if self.expires_at < datetime.now(timezone.utc):
            return False
        return True

    def revoke(self):
        """撤销令牌"""
        self.revoked = True
        self.revoked_at = datetime.now(timezone.utc)
