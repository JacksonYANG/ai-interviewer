"""
邀请码数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class InvitationCode(Base):
    """邀请码模型"""
    __tablename__ = "invitation_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    code_type = Column(String(20), nullable=False)  # one_time, limited, unlimited
    max_uses = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    expires_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_for = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # 关系
    used_by = relationship("User", foreign_keys="User.invitation_code_id")

    def is_valid(self) -> bool:
        """
        检查邀请码是否有效

        Returns:
            bool: 邀请码是否有效
        """
        if not self.is_active:
            return False

        # 检查是否过期
        if self.expires_at and self.expires_at < datetime.now(timezone.utc):
            return False

        # 检查使用次数
        if self.code_type == "one_time" and self.used_count >= 1:
            return False
        elif self.code_type == "limited" and self.used_count >= self.max_uses:
            return False

        return True

    def increment_usage(self):
        """增加使用次数"""
        self.used_count += 1
