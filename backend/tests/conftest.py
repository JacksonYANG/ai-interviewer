"""
测试配置
"""
import pytest
import asyncio


@pytest.fixture
def anyio_backend():
    """配置anyio使用asyncio后端"""
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
