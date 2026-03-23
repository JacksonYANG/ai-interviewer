"""
初始化超级管理员和邀请码

运行方式：python -m scripts.init_admin
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
from datetime import datetime, timedelta
import secrets

from app.database import Base
from app.models.user import User
from app.models.invitation_code import InvitationCode
from app.core.security import create_access_token, create_refresh_token

# 数据库连接（使用同步sqlite3驱动用于脚本）
DATABASE_URL = "sqlite:///./data/database.db"

def init_database():
    """初始化数据库"""
    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    return engine

def create_super_admin(db_session):
    """创建超级管理员账号"""

    # 强密码：至少16位，包含大小写字母、数字和特殊字符
    strong_password = "AI-Interview-Admin#2026!Secure"

    # 检查是否已存在超级管理员
    existing_admin = db_session.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("✅ 超级管理员已存在")
        return existing_admin

    # 使用bcrypt生成密码哈希
    password_bytes = strong_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

    # 创建超级管理员
    admin = User(
        username="admin",
        email="admin@ai-interviewer.local",
        password_hash=password_hash,
        role="admin",
        account_type="admin",
        email_verified=True,
        is_active=True,
        created_at=datetime.utcnow(),
        last_login=None
    )

    db_session.add(admin)
    db_session.commit()

    print("✅ 超级管理员创建成功")
    print(f"   用户名: admin")
    print(f"   密码: {strong_password}")
    print(f"   ⚠️  请立即修改密码！")

    return admin

def create_initial_invitation_codes(db_session, admin_user):
    """创建初始邀请码"""
    codes = []

    # 创建3个不同类型的邀请码
    invitation_codes = [
        {
            "code": "ADMIN-" + secrets.token_hex(4).upper(),
            "code_type": "unlimited",
            "max_uses": None,
            "created_by": admin_user.id,
            "notes": "管理员邀请码 - 无限使用次数"
        },
        {
            "code": "BETA-" + secrets.token_hex(4).upper(),
            "code_type": "limited",
            "max_uses": 10,
            "notes": "Beta测试邀请码 - 限10次"
        },
        {
            "code": "ONCE-" + secrets.token_hex(4).upper(),
            "code_type": "one_time",
            "max_uses": 1,
            "notes": "一次性邀请码"
        }
    ]

    for code_data in invitation_codes:
        code = InvitationCode(
            code=code_data["code"],
            code_type=code_data["code_type"],
            max_uses=code_data["max_uses"],
            used_count=0,
            created_by=admin_user.id,
            is_active=True,
            notes=code_data["notes"],
            created_at=datetime.utcnow()
        )
        db_session.add(code)
        codes.append(code)

    db_session.commit()

    print("✅ 初始邀请码创建成功：")
    for code in codes:
        print(f"   - {code.code} ({code.notes})")

    return codes

def main():
    """主函数"""
    print("=" * 60)
    print("AI面试官系统 - 初始化超级管理员")
    print("=" * 60)

    # 确保数据目录存在
    os.makedirs("./data", exist_ok=True)

    # 初始化数据库
    print("\n[1/3] 初始化数据库...")
    engine = init_database()
    SessionLocal = sessionmaker(bind=engine)

    # 创建会话
    session = SessionLocal()

    try:
        # 创建超级管理员
        print("\n[2/3] 创建超级管理员...")
        admin = create_super_admin(session)

        # 创建初始邀请码
        print("\n[3/3] 创建初始邀请码...")
        codes = create_initial_invitation_codes(session, admin)

        print("\n" + "=" * 60)
        print("✅ 初始化完成！")
        print("=" * 60)
        print("\n📝 登录信息：")
        print(f"   用户名: admin")
        print(f"   密码: AI-Interview-Admin#2026!Secure")
        print(f"\n🎫 邀请码：")
        for code in codes:
            print(f"   - {code.code}")
        print(f"\n⚠️  重要提示：")
        print(f"   1. 请立即登录并修改密码")
        print(f"   2. 妥善保管邀请码，不要泄露")
        print(f"   3. 使用邀请码注册新用户")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
