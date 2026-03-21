"""
API v1 路由聚合
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .interviews import router as interviews_router

router = APIRouter(prefix="/api/v1")

# 包含所有子路由
router.include_router(auth_router)
router.include_router(interviews_router)
