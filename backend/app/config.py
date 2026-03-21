"""
AI面试官后端应用程序配置
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用程序配置"""
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    # 应用基本信息
    APP_NAME: str = "AI面试官系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_interviewer.db"

    # JWT安全配置
    SECRET_KEY: str = "dev-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 邀请码配置
    INVITATION_CODE_LENGTH: int = 8


settings = Settings()
