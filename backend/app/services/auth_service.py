"""
认证服务：处理用户注册、登录、邀请码验证等业务逻辑
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone

from ..models.user import User
from ..models.invitation_code import InvitationCode
from ..schemas.auth import UserRegister
from ..core.security import get_password_hash


class AuthService:
    """认证服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_invitation_code(self, code: str) -> tuple[bool, Optional[InvitationCode]]:
        """
        验证邀请码

        Args:
            code: 邀请码

        Returns:
            tuple[bool, Optional[InvitationCode]]: (是否有效, 邀请码对象)
        """
        result = await self.db.execute(
            select(InvitationCode).where(InvitationCode.code == code)
        )
        invitation_code = result.scalar_one_or_none()

        if not invitation_code:
            return False, None

        if not invitation_code.is_valid():
            return False, None

        return True, invitation_code

    async def create_user(self, user_data: UserRegister, invitation_code: InvitationCode) -> User:
        """
        创建新用户

        Args:
            user_data: 用户注册数据
            invitation_code: 邀请码对象

        Returns:
            User: 创建的用户对象

        Raises:
            ValueError: 如果用户名或邮箱已存在
        """
        # 检查邮箱是否已存在
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ValueError("邮箱已被注册")

        # 检查用户名是否已存在
        result = await self.db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("用户名已被使用")

        # 创建用户
        user = User(
            email=user_data.email,
            username=user_data.username,
            role="user",
            account_type="beta",
            email_verified=False,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            invitation_code_id=invitation_code.id
        )
        user.set_password(user_data.password)

        self.db.add(user)

        # 增加邀请码使用次数
        invitation_code.increment_usage()

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        验证用户登录

        Args:
            email: 邮箱
            password: 密码

        Returns:
            Optional[User]: 验证成功返回用户对象，失败返回None
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not user.is_active:
            return None

        if not user.verify_password(password):
            return None

        # 更新最后登录时间
        user.last_login = datetime.now(timezone.utc)
        await self.db.commit()

        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            Optional[User]: 用户对象或None
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
