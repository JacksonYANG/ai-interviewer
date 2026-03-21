"""
Token黑名单服务 - 实现Token注销功能
"""
from datetime import datetime, timedelta
from typing import Optional, Set
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken
from app.core.logger import get_logger
import json

logger = get_logger(__name__)


class TokenBlacklist:
    """Token黑名单 - 基于内存存储"""

    def __init__(self):
        """初始化黑名单"""
        # 存储被注销的token {token_jti: expiry_time}
        self._blacklisted_tokens: dict = {}
        # 存储被注销的refresh token {token_id: expiry_time}
        self._blacklisted_refresh_tokens: dict = {}

    def add_to_blacklist(self, token_jti: str, expires_at: datetime):
        """
        将token添加到黑名单

        Args:
            token_jti: token的唯一标识
            expires_at: token的过期时间
        """
        self._blacklisted_tokens[token_jti] = expires_at
        logger.info(f"Token已加入黑名单: {token_jti[:20]}...")

    def is_blacklisted(self, token_jti: str) -> bool:
        """
        检查token是否在黑名单中

        Args:
            token_jti: token的唯一标识

        Returns:
            是否在黑名单中
        """
        if token_jti not in self._blacklisted_tokens:
            return False

        # 检查是否已过期
        expiry_time = self._blacklisted_tokens[token_jti]
        if datetime.now() > expiry_time:
            # 已过期,从黑名单移除
            del self._blacklisted_tokens[token_jti]
            return False

        return True

    def add_refresh_token_to_blacklist(self, token_id: int, expires_at: datetime):
        """
        将refresh token添加到黑名单

        Args:
            token_id: refresh token的ID
            expires_at: token的过期时间
        """
        self._blacklisted_refresh_tokens[token_id] = expires_at
        logger.info(f"Refresh Token已加入黑名单: ID={token_id}")

    def is_refresh_token_blacklisted(self, token_id: int) -> bool:
        """
        检查refresh token是否在黑名单中

        Args:
            token_id: refresh token的ID

        Returns:
            是否在黑名单中
        """
        if token_id not in self._blacklisted_refresh_tokens:
            return False

        # 检查是否已过期
        expiry_time = self._blacklisted_refresh_tokens[token_id]
        if datetime.now() > expiry_time:
            # 已过期,从黑名单移除
            del self._blacklisted_refresh_tokens[token_id]
            return False

        return True

    def cleanup_expired(self):
        """清理已过期的黑名单token"""
        now = datetime.now()

        # 清理access token
        self._blacklisted_tokens = {
            jti: expiry
            for jti, expiry in self._blacklisted_tokens.items()
            if expiry > now
        }

        # 清理refresh token
        self._blacklisted_refresh_tokens = {
            token_id: expiry
            for token_id, expiry in self._blacklisted_refresh_tokens.items()
            if expiry > now
        }


# 全局黑名单实例
token_blacklist = TokenBlacklist()


class TokenBlacklistService:
    """Token黑名单服务 - 基于数据库存储"""

    def __init__(self, db: Session):
        """
        初始化服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def revoke_token(self, token_id: int, user_id: int) -> bool:
        """
        注销token

        Args:
            token_id: token ID
            user_id: 用户ID

        Returns:
            是否成功
        """
        try:
            # 查找token
            token = self.db.query(RefreshToken).filter(
                RefreshToken.id == token_id,
                RefreshToken.user_id == user_id
            ).first()

            if not token:
                logger.warning(f"Token不存在: ID={token_id}, 用户ID={user_id}")
                return False

            # 标记为已撤销
            token.is_revoked = True
            token.revoked_at = datetime.now()

            self.db.commit()

            # 同时添加到内存黑名单
            if token.expires_at:
                token_blacklist.add_refresh_token_to_blacklist(
                    token_id=token_id,
                    expires_at=token.expires_at
                )

            logger.info(f"Token已注销: ID={token_id}, 用户ID={user_id}")
            return True

        except Exception as e:
            logger.error(f"注销token失败: {str(e)}")
            self.db.rollback()
            return False

    def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        注销用户的所有token

        Args:
            user_id: 用户ID

        Returns:
            注销的token数量
        """
        try:
            # 查找用户的所有有效token
            tokens = self.db.query(RefreshToken).filter(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now()
            ).all()

            count = 0
            for token in tokens:
                token.is_revoked = True
                token.revoked_at = datetime.now()

                # 添加到内存黑名单
                if token.expires_at:
                    token_blacklist.add_refresh_token_to_blacklist(
                        token_id=token.id,
                        expires_at=token.expires_at
                    )

                count += 1

            self.db.commit()

            logger.info(f"已注销用户 {user_id} 的 {count} 个token")
            return count

        except Exception as e:
            logger.error(f"注销用户token失败: {str(e)}")
            self.db.rollback()
            return 0

    def is_token_revoked(self, token_id: int) -> bool:
        """
        检查token是否已被注销

        Args:
            token_id: token ID

        Returns:
            是否已注销
        """
        # 先检查内存黑名单
        if token_blacklist.is_refresh_token_blacklisted(token_id):
            return True

        # 再检查数据库
        token = self.db.query(RefreshToken).filter(
            RefreshToken.id == token_id
        ).first()

        if not token:
            return True  # token不存在视为已注销

        return token.is_revoked

    def cleanup_expired_tokens(self):
        """清理过期的token"""
        try:
            # 删除已过期的token
            self.db.query(RefreshToken).filter(
                RefreshToken.expires_at < datetime.now()
            ).delete()

            self.db.commit()

            # 清理内存黑名单
            token_blacklist.cleanup_expired()

            logger.info("已清理过期的token")

        except Exception as e:
            logger.error(f"清理过期token失败: {str(e)}")
            self.db.rollback()
