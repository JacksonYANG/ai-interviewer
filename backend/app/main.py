"""
AI面试官后端主应用程序
"""
from fastapi import FastAPI
from .api.v1 import router as api_v1_router
from .middleware.security import setup_security_middleware
from .middleware.rate_limit import rate_limit_middleware
from .core.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="AI面试官系统API",
    description="提供面试官功能的后端API服务",
    version="1.0.0"
)

# 设置安全中间件
setup_security_middleware(app)

# 添加限流中间件
app.middleware("http")(rate_limit_middleware)

# 包含API路由
app.include_router(api_v1_router)


@app.get("/")
async def root():
    """根路径健康检查"""
    return {"message": "AI面试官系统API正在运行", "status": "healthy"}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
