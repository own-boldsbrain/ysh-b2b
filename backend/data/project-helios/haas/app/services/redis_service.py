"""Redis service for caching and token blacklist."""

import logging
from typing import Any, Optional
import redis
from app.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Redis client wrapper with connection pooling and error handling."""

    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            # Test connection
            self.client.ping()
            logger.info("Redis connected: %s", settings.REDIS_URL)
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            logger.error("Redis connection failed: %s", exc)
            self.client = None

    def is_available(self) -> bool:
        """Check if Redis is available."""
        if self.client is None:
            return False
        try:
            return self.client.ping()
        except (redis.ConnectionError, redis.TimeoutError):
            return False

    def set(self, key: str, value: Any, expires_in: Optional[int] = None) -> bool:
        """
        Set key-value in Redis with optional TTL.

        Args:
            key: Redis key
            value: Value to store (will be converted to string)
            expires_in: TTL in seconds (None = no expiration)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("Redis unavailable - cannot SET %s", key)
            return False

        try:
            if expires_in:
                self.client.setex(key, expires_in, str(value))
            else:
                self.client.set(key, str(value))
            return True
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            logger.error("Redis SET failed for %s: %s", key, exc)
            return False

    def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis.

        Args:
            key: Redis key

        Returns:
            Value as string or None if not found/error
        """
        if not self.is_available():
            logger.warning("Redis unavailable - cannot GET %s", key)
            return None

        try:
            return self.client.get(key)
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            logger.error("Redis GET failed for %s: %s", key, exc)
            return None

    def delete(self, key: str) -> bool:
        """
        Delete key from Redis.

        Args:
            key: Redis key to delete

        Returns:
            True if deleted, False otherwise
        """
        if not self.is_available():
            logger.warning("Redis unavailable - cannot DELETE %s", key)
            return False

        try:
            self.client.delete(key)
            return True
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            logger.error("Redis DELETE failed for %s: %s", key, exc)
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.

        Args:
            key: Redis key

        Returns:
            True if exists, False otherwise
        """
        if not self.is_available():
            return False

        try:
            return bool(self.client.exists(key))
        except (redis.ConnectionError, redis.TimeoutError) as exc:
            logger.error("Redis EXISTS failed for %s: %s", key, exc)
            return False

    def add_to_blacklist(self, token: str, expires_in: int) -> bool:
        """
        Add JWT token to blacklist with TTL.

        Args:
            token: JWT token to blacklist
            expires_in: TTL in seconds

        Returns:
            True if successful, False otherwise
        """
        key = f"blacklist:{token}"
        return self.set(key, "1", expires_in=expires_in)

    def is_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.

        Args:
            token: JWT token to check

        Returns:
            True if blacklisted, False otherwise
        """
        key = f"blacklist:{token}"
        return self.exists(key)


# Global singleton instance
redis_service = RedisService()
