"""
认证API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse, TokenRefresh
from ...services.auth_service import AuthService
from ...deps import get_db
from ...core.security import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册

    需要提供有效的邀请码
    """
    auth_service = AuthService(db)

    # 验证邀请码
    is_valid, invitation_code = await auth_service.validate_invitation_code(user_data.invitation_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请码无效或已过期"
        )

    # 创建用户
    try:
        user = await auth_service.create_user(user_data, invitation_code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 生成Token
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    """
    auth_service = AuthService(db)

    user = await auth_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成Token
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问Token
    """
    payload = decode_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新Token"
        )

    user_id = int(payload.get("sub"))
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )

    # 生成新的Token
    access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user_id=user.id
    )


# TODO: 实现 JWT 认证依赖后取消注释
# @router.get("/me", response_model=UserResponse)
# async def get_current_user(
#     user_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     获取当前用户信息
#     """
#     auth_service = AuthService(db)
#     user = await auth_service.get_user_by_id(user_id)
#
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="用户不存在"
#         )
#
#     return UserResponse(
#         id=user.id,
#         email=user.email,
#         username=user.username,
#         role=user.role,
#         account_type=user.account_type,
#         email_verified=user.email_verified,
#         created_at=user.created_at
#     )
