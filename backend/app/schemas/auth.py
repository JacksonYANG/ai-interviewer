"""
认证相关的Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    """用户注册请求"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    username: str = Field(..., min_length=3, max_length=50)
    invitation_code: str = Field(..., min_length=6, max_length=20)


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    refresh_token: str
    user_id: int


class TokenRefresh(BaseModel):
    """刷新Token请求"""
    refresh_token: str


class UserResponse(BaseModel):
    """用户信息响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    role: str
    account_type: str
    email_verified: bool
    created_at: datetime


class InvitationCodeCreate(BaseModel):
    """创建邀请码请求"""
    code_type: str = Field(..., pattern="^(one_time|limited|unlimited)$")
    max_uses: Optional[int] = Field(None, ge=1)
    expires_at: Optional[datetime] = None
    created_for: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=500)


class InvitationCodeResponse(BaseModel):
    """邀请码响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    code_type: str
    max_uses: int
    used_count: int
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
