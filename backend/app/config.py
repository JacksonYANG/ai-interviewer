"""
AI面试官后端应用程序配置
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional


class Settings(BaseSettings):
    """应用程序配置"""
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    # 应用基本信息
    APP_NAME: str = "AI面试官系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库配置 - 使用绝对路径确保正确挂载
    # 注意：环境变量中的4个斜杠会被pydatic规范化为3个，需要重新处理
    DATABASE_URL: str = "sqlite+aiosqlite:////data/database.db"

    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def fix_absolute_path(cls, v: str) -> str:
        """确保SQLite使用绝对路径"""
        if v.startswith('sqlite+aiosqlite:///') and not v.startswith('sqlite+aiosqlite:////'):
            # 如果是相对路径格式（3个斜杠），且路径以/开头，转换为绝对路径
            db_path = v.split('sqlite+aiosqlite:///')[1]
            if db_path.startswith('/'):
                # 这是一个绝对路径，需要使用4个斜杠格式
                return f"sqlite+aiosqlite:////{db_path}"
        return v

    # JWT安全配置
    SECRET_KEY: str = "dev-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 邀请码配置
    INVITATION_CODE_LENGTH: int = 8


settings = Settings()
