"""
安全配置和中间件
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
import re
from app.core.logger import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""

    async def dispatch(self, request: Request, call_next):
        """
        添加安全相关的HTTP头

        包括:
        - X-Content-Type-Options: nosniff
        - X-Frame-Options: DENY
        - X-XSS-Protection: 1; mode=block
        - Strict-Transport-Security: max-age=31536000; includeSubDomains
        - Content-Security-Policy: 限制资源加载
        """
        response = await call_next(request)

        # 防止MIME类型嗅探
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 防止点击劫持
        response.headers["X-Frame-Options"] = "DENY"

        # XSS保护
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HSTS (仅在HTTPS下启用)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 内容安全策略
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # 推荐策略
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 权限策略
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )

        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """输入验证中间件"""

    # SQL注入检测模式
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\bexec\b|\bexecute\b)",
        r"(;.*\bwaitfor\b)",
        r"(\bcast\b.*\bconvert\b)",
    ]

    # XSS检测模式
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe[^>]*>",
        r"<embed[^>]*>",
        r"<object[^>]*>",
    ]

    def __init__(self, app):
        super().__init__(app)
        # 编译正则表达式
        self.sql_patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS]
        self.xss_patterns = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]

    def _check_sql_injection(self, data: str) -> bool:
        """
        检测SQL注入

        Args:
            data: 输入数据

        Returns:
            是否包含SQL注入
        """
        for pattern in self.sql_patterns:
            if pattern.search(data):
                logger.warning(f"检测到SQL注入尝试: {data[:100]}")
                return True
        return False

    def _check_xss(self, data: str) -> bool:
        """
        检测XSS攻击

        Args:
            data: 输入数据

        Returns:
            是否包含XSS
        """
        for pattern in self.xss_patterns:
            if pattern.search(data):
                logger.warning(f"检测到XSS攻击尝试: {data[:100]}")
                return True
        return False

    async def dispatch(self, request: Request, call_next):
        """
        验证请求输入

        检查路径参数、查询参数和请求体中的潜在恶意内容
        """
        try:
            # 检查查询参数
            for key, value in request.query_params.items():
                if isinstance(value, str):
                    if self._check_sql_injection(value) or self._check_xss(value):
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={"detail": "检测到非法输入"}
                        )

            # 检查路径参数
            for key, value in request.path_params.items():
                if isinstance(value, str):
                    if self._check_sql_injection(value) or self._check_xss(value):
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={"detail": "检测到非法输入"}
                        )

            # 对于POST/PUT请求,检查请求体
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        body_str = body.decode('utf-8', errors='ignore')
                        if self._check_sql_injection(body_str) or self._check_xss(body_str):
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={"detail": "检测到非法输入"}
                            )
                except Exception as e:
                    logger.error(f"读取请求体失败: {str(e)}")

            return await call_next(request)

        except Exception as e:
            logger.error(f"输入验证中间件错误: {str(e)}")
            return await call_next(request)


class SizeLimitMiddleware(BaseHTTPMiddleware):
    """请求大小限制中间件"""

    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 默认10MB
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        """
        限制请求大小

        防止大文件攻击和DoS攻击
        """
        # 检查Content-Length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_request_size:
                    logger.warning(f"请求过大: {size} bytes")
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "detail": f"请求过大,最大允许{self.max_request_size}字节",
                            "error_code": "request_too_large"
                        }
                    )
            except ValueError:
                pass

        return await call_next(request)


def setup_security_middleware(app):
    """
    设置所有安全中间件

    Args:
        app: FastAPI应用实例
    """
    # CORS中间件 - 只启用CORS来修复网络错误
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",   # Vite dev server
            "http://localhost:3000",    # 可能的生产前端
            "http://localhost",         # Nginx代理
            "http://localhost:80"       # 明确指定80端口
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-RateLimit-Remaining", "X-RateLimit-Limit"]
    )

    logger.info("CORS中间件已配置")
