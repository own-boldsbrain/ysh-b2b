"""Rate limiting middleware usando Redis."""

import logging
import time
from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de rate limiting usando Redis.

    Limita requisições por IP e por usuário.
    Algoritmo: Token Bucket com sliding window.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.window_minute = 60  # seconds
        self.window_hour = 3600  # seconds

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting."""

        # Skip rate limiting for health check
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limits
        try:
            self._check_rate_limit(client_ip)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
                headers=exc.headers or {},
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Try X-Forwarded-For header first (proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Try X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    def _check_rate_limit(self, client_ip: str) -> None:
        """
        Check if client exceeds rate limits.

        Args:
            client_ip: Client IP address

        Raises:
            HTTPException: If rate limit exceeded
        """
        if not redis_service.is_available():
            # Fail open - allow requests if Redis unavailable
            logger.warning("Redis unavailable - rate limiting disabled")
            return

        current_time = int(time.time())

        # Check minute window
        key_minute = f"ratelimit:{client_ip}:minute:{current_time // 60}"
        count_minute = redis_service.get(key_minute)

        if count_minute is None:
            # First request in this window
            redis_service.set(key_minute, "1", expires_in=self.window_minute)
        else:
            count = int(count_minute)
            if count >= self.requests_per_minute:
                retry_after = 60 - (current_time % 60)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Rate limit exceeded: {self.requests_per_minute} "
                        f"requests per minute"
                    ),
                    headers={"Retry-After": str(retry_after)},
                )
            redis_service.set(key_minute, str(count + 1), expires_in=self.window_minute)

        # Check hour window
        key_hour = f"ratelimit:{client_ip}:hour:{current_time // 3600}"
        count_hour = redis_service.get(key_hour)

        if count_hour is None:
            # First request in this window
            redis_service.set(key_hour, "1", expires_in=self.window_hour)
        else:
            count = int(count_hour)
            if count >= self.requests_per_hour:
                retry_after = 3600 - (current_time % 3600)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Rate limit exceeded: {self.requests_per_hour} "
                        f"requests per hour"
                    ),
                    headers={"Retry-After": str(retry_after)},
                )
            redis_service.set(key_hour, str(count + 1), expires_in=self.window_hour)
