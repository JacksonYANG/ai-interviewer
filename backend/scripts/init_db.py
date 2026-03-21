#!/usr/bin/env python3
"""
数据库初始化脚本
创建数据库表并插入初始数据
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, Base
from app.core.security import get_password_hash
from app.models import (
    User, InvitationCode, EmailVerification, LoginLog, RefreshToken,
    UserProfile, Resume, InterviewConfig, InterviewRound,
    InterviewSession, Question, Answer, Score, RoundSummary,
    AudioFile, Report
)


async def init_db():
    """初始化数据库"""
    print("开始创建数据库表...")

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✓ 数据库表创建成功")

    # 创建默认管理员
    print("\n创建默认管理员账户...")
    admin = User(
        username="admin",
        email="admin@ai-interviewer.com",
        password_hash=get_password_hash("Admin123!"),
        role="admin",
        account_type="admin",
        email_verified=True,
        is_active=True
    )

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        try:
            # 检查管理员是否已存在
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == "admin@ai-interviewer.com")
            )
            existing_admin = result.scalar_one_or_none()

            if not existing_admin:
                session.add(admin)
                await session.commit()
                print("✓ 默认管理员创建成功")
                print("  用户名: admin")
                print("  密码: Admin123!")
                print("  邮箱: admin@ai-interviewer.com")
            else:
                print("✓ 管理员账户已存在，跳过创建")

            # 创建测试邀请码
            print("\n创建测试邀请码...")
            test_codes = [
                {
                    "code": "BETA-TEST-001",
                    "code_type": "limited",
                    "max_uses": 10,
                    "created_by": 1,
                    "notes": "内测阶段邀请码 - 可使用10次"
                },
                {
                    "code": "BETA-TEST-002",
                    "code_type": "unlimited",
                    "max_uses": 999,
                    "created_by": 1,
                    "notes": "内测阶段无限使用邀请码"
                }
            ]

            for code_data in test_codes:
                result = await session.execute(
                    select(InvitationCode).where(
                        InvitationCode.code == code_data["code"]
                    )
                )
                existing_code = result.scalar_one_or_none()

                if not existing_code:
                    invite_code = InvitationCode(**code_data)
                    session.add(invite_code)

            await session.commit()
            print("✓ 测试邀请码创建成功")
            print("  - BETA-TEST-001 (限量10次)")
            print("  - BETA-TEST-002 (无限使用)")

        except Exception as e:
            await session.rollback()
            print(f"✗ 创建初始数据失败: {e}")
            raise

    print("\n✓ 数据库初始化完成!")


async def drop_all_tables():
    """删除所有表（危险操作，仅用于开发环境）"""
    print("警告：即将删除所有数据库表!")
    confirm = input("确认删除? (输入 'yes' 确认): ")

    if confirm.lower() != "yes":
        print("操作已取消")
        return

    print("正在删除所有表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("✓ 所有表已删除")


async def reset_db():
    """重置数据库：删除所有表并重新创建"""
    await drop_all_tables()
    print()
    await init_db()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库管理脚本")
    parser.add_argument(
        "action",
        choices=["init", "reset", "drop"],
        help="操作类型: init-初始化, reset-重置, drop-删除所有表"
    )

    args = parser.parse_args()

    if args.action == "init":
        asyncio.run(init_db())
    elif args.action == "reset":
        asyncio.run(reset_db())
    elif args.action == "drop":
        asyncio.run(drop_all_tables())
