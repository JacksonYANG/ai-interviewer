"""
认证系统测试
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.invitation_code import InvitationCode
from app.core.security import create_access_token
from datetime import datetime, timedelta, timezone


# 创建测试数据库引擎
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="function")
async def db_session():
    """创建测试数据库会话"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    """创建测试客户端"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def create_test_invitation_code(db_session: AsyncSession, code: str = "TESTCODE") -> InvitationCode:
    """辅助函数：创建测试邀请码"""
    invitation_code = InvitationCode(
        code=code,
        code_type="unlimited",
        max_uses=100,
        is_active=True,
        created_by=1,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(invitation_code)
    await db_session.commit()
    await db_session.refresh(invitation_code)
    return invitation_code


@pytest.mark.asyncio
async def test_register_with_valid_code(client: AsyncClient, db_session: AsyncSession):
    """测试使用有效邀请码注册"""
    await create_test_invitation_code(db_session)

    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "Test123!",
        "username": "testuser",
        "invitation_code": "TESTCODE"
    })

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user_id" in data


@pytest.mark.asyncio
async def test_register_with_invalid_code(client: AsyncClient):
    """测试使用无效邀请码注册"""
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "Test123!",
        "username": "testuser",
        "invitation_code": "INVALID"
    })

    assert response.status_code == 400
    assert "邀请码无效" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, db_session: AsyncSession):
    """测试重复邮箱注册"""
    await create_test_invitation_code(db_session)

    # 第一次注册
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "Test123!",
        "username": "testuser1",
        "invitation_code": "TESTCODE"
    })

    # 第二次注册相同邮箱
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "Test123!",
        "username": "testuser2",
        "invitation_code": "TESTCODE"
    })

    assert response.status_code == 400
    assert "邮箱已被注册" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, db_session: AsyncSession):
    """测试重复用户名注册"""
    await create_test_invitation_code(db_session)

    # 第一次注册
    await client.post("/api/v1/auth/register", json={
        "email": "test1@example.com",
        "password": "Test123!",
        "username": "testuser",
        "invitation_code": "TESTCODE"
    })

    # 第二次注册相同用户名
    response = await client.post("/api/v1/auth/register", json={
        "email": "test2@example.com",
        "password": "Test123!",
        "username": "testuser",
        "invitation_code": "TESTCODE"
    })

    assert response.status_code == 400
    assert "用户名已被使用" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    """测试成功登录"""
    await create_test_invitation_code(db_session)

    # 先注册用户
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "Test123!",
        "username": "testuser",
        "invitation_code": "TESTCODE"
    })

    # 登录
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "Test123!"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user_id" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session: AsyncSession):
    """测试错误密码登录"""
    await create_test_invitation_code(db_session)

    # 先注册用户
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "Test123!",
        "username": "testuser",
        "invitation_code": "TESTCODE"
    })

    # 使用错误密码登录
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPassword123!"
    })

    assert response.status_code == 401
    assert "邮箱或密码错误" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """测试不存在的用户登录"""
    response = await client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "Test123!"
    })

    assert response.status_code == 401
    assert "邮箱或密码错误" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, db_session: AsyncSession):
    """测试刷新Token"""
    await create_test_invitation_code(db_session)

    # 先注册用户
    register_response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "Test123!",
        "username": "testuser",
        "invitation_code": "TESTCODE"
    })

    refresh_token = register_response.json()["refresh_token"]

    # 刷新Token
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_invitation_code_one_time_limit(db_session: AsyncSession):
    """测试一次性邀请码限制"""
    invitation_code = InvitationCode(
        code="ONETIME",
        code_type="one_time",
        max_uses=1,
        used_count=0,
        is_active=True,
        created_by=1,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(invitation_code)
    await db_session.commit()

    # 第一次使用
    assert invitation_code.is_valid() == True

    # 增加使用次数
    invitation_code.increment_usage()
    await db_session.commit()

    # 第二次使用应该无效
    assert invitation_code.is_valid() == False


@pytest.mark.asyncio
async def test_invitation_code_expiration(db_session: AsyncSession):
    """测试邀请码过期"""
    invitation_code = InvitationCode(
        code="EXPIRED",
        code_type="unlimited",
        max_uses=100,
        used_count=0,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),  # 昨天过期
        is_active=True,
        created_by=1,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(invitation_code)
    await db_session.commit()

    # 过期的邀请码应该无效
    assert invitation_code.is_valid() == False


@pytest.mark.asyncio
async def test_password_hashing(db_session: AsyncSession):
    """测试密码哈希"""
    user = User(
        email="test@example.com",
        username="testuser",
        created_at=datetime.now(timezone.utc)
    )
    user.set_password("Test123!")

    db_session.add(user)
    await db_session.commit()

    # 验证密码
    assert user.verify_password("Test123!") == True
    assert user.verify_password("WrongPassword") == False


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查端点"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
