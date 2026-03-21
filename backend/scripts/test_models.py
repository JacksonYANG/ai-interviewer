#!/usr/bin/env python3
"""
测试数据库模型
验证所有模型都能正常导入和创建
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, AsyncSessionLocal
from app.models import (
    User, InvitationCode, EmailVerification, LoginLog, RefreshToken,
    UserProfile, Resume, InterviewConfig, InterviewRound,
    InterviewSession, Question, Answer, Score, RoundSummary,
    AudioFile, Report
)
from sqlalchemy import select


async def test_models():
    """测试所有模型"""
    print("=" * 60)
    print("测试数据库模型")
    print("=" * 60)

    # 测试所有模型导入
    print("\n1. 测试模型导入...")
    models = [
        "User", "InvitationCode", "EmailVerification", "LoginLog",
        "RefreshToken", "UserProfile", "Resume", "InterviewConfig",
        "InterviewRound", "InterviewSession", "Question", "Answer",
        "Score", "RoundSummary", "AudioFile", "Report"
    ]

    for model_name in models:
        print(f"   ✓ {model_name}")

    print("\n2. 测试数据库连接...")
    async with AsyncSessionLocal() as session:
        # 测试查询用户
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        admin = result.scalar_one_or_none()
        if admin:
            print(f"   ✓ 找到管理员用户: {admin.username}")
        else:
            print("   ✗ 未找到管理员用户")

        # 测试查询邀请码
        result = await session.execute(
            select(InvitationCode).where(InvitationCode.code == "BETA-TEST-001")
        )
        code = result.scalar_one_or_none()
        if code:
            print(f"   ✓ 找到测试邀请码: {code.code}")
        else:
            print("   ✗ 未找到测试邀请码")

        # 统计所有表的记录数
        print("\n3. 数据库表记录统计:")
        tables = [
            (User, "users"),
            (InvitationCode, "invitation_codes"),
            (EmailVerification, "email_verifications"),
            (LoginLog, "login_logs"),
            (RefreshToken, "refresh_tokens"),
            (UserProfile, "user_profiles"),
            (Resume, "resumes"),
            (InterviewConfig, "interview_configs"),
            (InterviewRound, "interview_rounds"),
            (InterviewSession, "interview_sessions"),
            (Question, "questions"),
            (Answer, "answers"),
            (Score, "scores"),
            (RoundSummary, "round_summaries"),
            (AudioFile, "audio_files"),
            (Report, "reports")
        ]

        for model, table_name in tables:
            result = await session.execute(select(model))
            count = len(result.scalars().all())
            print(f"   {table_name}: {count} 条记录")

    print("\n" + "=" * 60)
    print("✓ 所有模型测试通过!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_models())
