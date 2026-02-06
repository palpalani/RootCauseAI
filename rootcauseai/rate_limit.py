"""Rate limiting middleware for cost control."""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from collections.abc import Callable

logger = None  # Will be set if logging is configured


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to control API usage."""

    def __init__(
        self,
        app: object,
        requests_per_minute: int = 10,
        requests_per_hour: int = 100,
        requests_per_day: int = 1000,
    ) -> None:
        """Initialize rate limiter.

        Args:
            app: FastAPI application.
            requests_per_minute: Max requests per minute per IP.
            requests_per_hour: Max requests per hour per IP.
            requests_per_day: Max requests per day per IP.
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day

        # Track requests by IP
        self.minute_requests: dict[str, list[float]] = defaultdict(list)
        self.hour_requests: dict[str, list[float]] = defaultdict(list)
        self.day_requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address.

        Args:
            request: FastAPI request.

        Returns:
            Client IP address.
        """
        # Check for forwarded IP (if behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        return request.client.host if request.client else "unknown"

    def _cleanup_old_requests(self, ip: str) -> None:
        """Remove old request timestamps.

        Args:
            ip: Client IP address.
        """
        now = time.time()

        # Clean minute requests (older than 1 minute)
        self.minute_requests[ip] = [
            ts for ts in self.minute_requests[ip] if now - ts < 60
        ]

        # Clean hour requests (older than 1 hour)
        self.hour_requests[ip] = [
            ts for ts in self.hour_requests[ip] if now - ts < 3600
        ]

        # Clean day requests (older than 1 day)
        self.day_requests[ip] = [
            ts for ts in self.day_requests[ip] if now - ts < 86400
        ]

    def _check_rate_limit(self, ip: str) -> tuple[bool, str]:
        """Check if request exceeds rate limits.

        Args:
            ip: Client IP address.

        Returns:
            Tuple of (allowed, reason_if_not_allowed).
        """
        self._cleanup_old_requests(ip)
        now = time.time()

        # Check minute limit
        if len(self.minute_requests[ip]) >= self.requests_per_minute:
            return (
                False,
                f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
            )

        # Check hour limit
        if len(self.hour_requests[ip]) >= self.requests_per_hour:
            return (
                False,
                f"Rate limit exceeded: {self.requests_per_hour} requests per hour",
            )

        # Check day limit
        if len(self.day_requests[ip]) >= self.requests_per_day:
            return (
                False,
                f"Rate limit exceeded: {self.requests_per_day} requests per day",
            )

        # Record request
        self.minute_requests[ip].append(now)
        self.hour_requests[ip].append(now)
        self.day_requests[ip].append(now)

        return (True, "")

    async def dispatch(self, request: Request, call_next: Callable) -> object:
        """Process request with rate limiting.

        Args:
            request: FastAPI request.
            call_next: Next middleware/route handler.

        Returns:
            Response.

        Raises:
            HTTPException: If rate limit exceeded.
        """
        # Only rate limit /analyze endpoint
        if request.url.path == "/analyze" and request.method == "POST":
            ip = self._get_client_ip(request)
            allowed, reason = self._check_rate_limit(ip)

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=reason,
                    headers={"Retry-After": "60"},
                )

        response = await call_next(request)
        return response
