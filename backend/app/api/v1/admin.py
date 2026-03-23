"""
邀请码管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.invitation_code import InvitationCode
from app.schemas.auth import TokenResponse
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, create_refresh_token
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/invitation-codes", tags=["邀请码管理"])


@router.post("/create")
async def create_invitation_code(
    code_type: str,
    max_uses: int = None,
    notes: str = None,
    expires_in_days: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建邀请码

    需要管理员权限
    - code_type: one_time, limited, unlimited
    - max_uses: 使用次数限制（limited类型必需）
    - notes: 备注
    - expires_in_days: 过期天数（可选）
    """
    # 验证管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建邀请码"
        )

    # 验证邀请码类型
    valid_types = ["one_time", "limited", "unlimited"]
    if code_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的邀请码类型，必须是: {', '.join(valid_types)}"
        )

    # limited类型需要max_uses
    if code_type == "limited" and max_uses is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limited类型邀请码必须指定max_uses"
        )

    # 生成邀请码
    import secrets
    code = f"{code_type.upper()}-{secrets.token_hex(4).upper()}"

    # 计算过期时间
    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    # 创建邀请码
    invitation_code = InvitationCode(
        code=code,
        code_type=code_type,
        max_uses=max_uses,
        used_count=0,
        created_by=current_user.id,
        is_active=True,
        notes=notes,
        expires_at=expires_at,
        created_at=datetime.utcnow()
    )

    db.add(invitation_code)
    db.commit()
    db.refresh(invitation_code)

    logger.info(f"管理员 {current_user.username} 创建邀请码: {code}")

    return {
        "id": invitation_code.id,
        "code": invitation_code.code,
        "code_type": invitation_code.code_type,
        "max_uses": invitation_code.max_uses,
        "used_count": invitation_code.used_count,
        "notes": invitation_code.notes,
        "expires_at": invitation_code.expires_at,
        "created_at": invitation_code.created_at
    }


@router.get("/list", response_model=List[dict])
async def list_invitation_codes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取邀请码列表

    需要管理员权限
    """
    # 验证管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看邀请码"
        )

    codes = db.query(InvitationCode).order_by(InvitationCode.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for code in codes:
        result.append({
            "id": code.id,
            "code": code.code,
            "code_type": code.code_type,
            "max_uses": code.max_uses,
            "used_count": code.used_count,
            "is_active": code.is_active,
            "notes": code.notes,
            "expires_at": code.expires_at,
            "created_at": code.created_at,
            "created_by": code.created_by
        })

    return result


@router.post("/deactivate/{code_id}")
async def deactivate_invitation_code(
    code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    停用邀请码

    需要管理员权限
    """
    # 验证管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以停用邀请码"
        )

    invitation_code = db.query(InvitationCode).filter(InvitationCode.id == code_id).first()

    if not invitation_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请码不存在"
        )

    invitation_code.is_active = False
    db.commit()

    logger.info(f"管理员 {current_user.username} 停用邀请码: {invitation_code.code}")

    return {"message": "邀请码已停用"}


@router.get("/stats")
async def get_invitation_code_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取邀请码统计信息

    需要管理员权限
    """
    # 验证管理员权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看统计"
        )

    total = db.query(InvitationCode).count()
    active = db.query(InvitationCode).filter(InvitationCode.is_active == True).count()
    inactive = db.query(InvitationCode).filter(InvitationCode.is_active == False).count()

    # 按类型统计
    by_type = {}
    for code_type in ["one_time", "limited", "unlimited"]:
        count = db.query(InvitationCode).filter(
            InvitationCode.code_type == code_type,
            InvitationCode.is_active == True
        ).count()
        by_type[code_type] = count

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "by_type": by_type
    }
