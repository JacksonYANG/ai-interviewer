"""
用户数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    account_type = Column(String(20), default="beta")
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime)
    invitation_code_id = Column(Integer, ForeignKey("invitation_codes.id"), nullable=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # 关系
    invitations = relationship("InvitationCode", foreign_keys="InvitationCode.created_by", back_populates="used_by")
    referrals = relationship("User", remote_side=[id], backref="referred_users")

    def set_password(self, password: str):
        """
        设置密码哈希

        Args:
            password: 明文密码
        """
        from ..core.security import get_password_hash
        self.password_hash = get_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """
        验证密码

        Args:
            password: 明文密码

        Returns:
            bool: 密码是否匹配
        """
        from ..core.security import verify_password
        return verify_password(password, self.password_hash)
