"""
依赖注入工具
"""
from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db


__all__ = ["get_db"]
