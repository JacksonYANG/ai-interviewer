"""
限流中间件 - 实现请求限流
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import asyncio
from app.core.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """基于内存的限流器"""

    def __init__(self):
        """初始化限流器"""
        # 存储每个IP的请求记录 {ip: [(timestamp, count), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        # 清理锁
        self._lock = asyncio.Lock()

    def _clean_old_requests(self, ip: str, window_seconds: int):
        """
        清理过期的请求记录

        Args:
            ip: 客户端IP
            window_seconds: 时间窗口(秒)
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        # 保留时间窗口内的请求
        self.requests[ip] = [
            (timestamp, count)
            for timestamp, count in self.requests[ip]
            if timestamp > cutoff
        ]

    async def is_allowed(
        self,
        ip: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, int]:
        """
        检查是否允许请求

        Args:
            ip: 客户端IP
            max_requests: 最大请求数
            window_seconds: 时间窗口(秒)

        Returns:
            (是否允许, 剩余请求数)
        """
        async with self._lock:
            now = datetime.now()

            # 清理过期记录
            self._clean_old_requests(ip, window_seconds)

            # 统计时间窗口内的请求数
            total_requests = sum(count for _, count in self.requests[ip])

            if total_requests >= max_requests:
                # 超出限制
                return False, 0

            # 记录本次请求
            self.requests[ip].append((now, 1))
            remaining = max_requests - total_requests - 1

            return True, remaining


# 全局限流器实例
rate_limiter = RateLimiter()


# 限流配置
RATE_LIMIT_CONFIGS = {
    # 登录接口: 5次/分钟
    "POST:/api/v1/auth/login": (5, 60),
    "POST:/api/v1/auth/register": (3, 60),

    # 一般API: 60次/分钟
    "default": (60, 60),

    # 面试相关API: 30次/分钟
    "POST:/api/v1/interviews/score": (10, 60),
    "POST:/api/v1/interviews/transcribe-audio": (5, 60),
}


async def rate_limit_middleware(request: Request, call_next):
    """
    限流中间件

    对API请求进行限流保护
    """
    try:
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"

        # 构建请求标识
        method = request.method
        path = request.url.path
        request_key = f"{method}:{path}"

        # 获取限流配置
        limit_config = RATE_LIMIT_CONFIGS.get(request_key)
        if not limit_config:
            # 使用默认配置
            max_requests, window_seconds = RATE_LIMIT_CONFIGS["default"]
        else:
            max_requests, window_seconds = limit_config

        # 检查是否允许请求
        allowed, remaining = await rate_limiter.is_allowed(
            ip=client_ip,
            max_requests=max_requests,
            window_seconds=window_seconds
        )

        if not allowed:
            logger.warning(f"限流触发: IP={client_ip}, 路径={path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"请求过于频繁，请在{window_seconds}秒后重试",
                    "error_code": "rate_limit_exceeded"
                }
            )

        # 添加响应头
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(max_requests)

        return response

    except Exception as e:
        logger.error(f"限流中间件错误: {str(e)}")
        # 出错时放行请求
        return await call_next(request)
