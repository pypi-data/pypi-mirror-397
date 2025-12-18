"""
Rate Limiting Middleware for FlowMason Studio.

Provides in-memory rate limiting with configurable limits per key.
Uses a sliding window algorithm for accurate rate limiting.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Callable, Dict, List, Optional

from fastapi import HTTPException, Request, status

# =============================================================================
# Rate Limiter
# =============================================================================

class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.

    Tracks request timestamps per key and enforces rate limits.
    """

    def __init__(self, default_limit: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limiter.

        Args:
            default_limit: Default requests per window
            window_seconds: Time window in seconds (default: 1 hour)
        """
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self._cache: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str, limit: Optional[int] = None) -> bool:
        """
        Check if a request is allowed under the rate limit.

        Args:
            key: Unique identifier for rate limiting (e.g., user_id, ip, api_key)
            limit: Optional custom limit (uses default if not provided)

        Returns:
            True if request is allowed, False if rate limited
        """
        rate_limit = limit if limit is not None else self.default_limit
        current_time = time.time()
        window_start = current_time - self.window_seconds

        with self._lock:
            # Get existing timestamps for this key
            timestamps = self._cache[key]

            # Remove timestamps outside the window
            timestamps = [ts for ts in timestamps if ts > window_start]

            # Check if under limit
            if len(timestamps) >= rate_limit:
                self._cache[key] = timestamps
                return False

            # Add current timestamp and update cache
            timestamps.append(current_time)
            self._cache[key] = timestamps
            return True

    def get_remaining(self, key: str, limit: Optional[int] = None) -> int:
        """
        Get remaining requests allowed in the current window.

        Args:
            key: Unique identifier for rate limiting
            limit: Optional custom limit

        Returns:
            Number of remaining requests
        """
        rate_limit = limit if limit is not None else self.default_limit
        current_time = time.time()
        window_start = current_time - self.window_seconds

        with self._lock:
            timestamps = self._cache.get(key, [])
            timestamps = [ts for ts in timestamps if ts > window_start]
            return max(0, rate_limit - len(timestamps))

    def get_reset_time(self, key: str) -> int:
        """
        Get seconds until rate limit resets for a key.

        Args:
            key: Unique identifier for rate limiting

        Returns:
            Seconds until oldest request expires (allowing a new one)
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds

        with self._lock:
            timestamps = self._cache.get(key, [])
            timestamps = [ts for ts in timestamps if ts > window_start]

            if not timestamps:
                return 0

            # Time until oldest timestamp expires
            oldest = min(timestamps)
            return max(0, int((oldest + self.window_seconds) - current_time))

    def clear(self, key: str) -> None:
        """Clear rate limit data for a key."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear_all(self) -> None:
        """Clear all rate limit data."""
        with self._lock:
            self._cache.clear()


# =============================================================================
# Global Rate Limiter Instance
# =============================================================================

_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def set_rate_limiter(limiter: Optional[RateLimiter]) -> None:
    """Set the global rate limiter instance (mainly for testing)."""
    global _rate_limiter
    _rate_limiter = limiter


# =============================================================================
# Rate Limit Dependency
# =============================================================================

def rate_limit(
    limit: int = 100,
    window_seconds: int = 3600,
    key_func: Optional[Callable[[Request], str]] = None,
):
    """
    Create a rate limiting dependency for FastAPI endpoints.

    Usage:
        @router.get("/api/resource")
        async def resource_endpoint(_: None = Depends(rate_limit(limit=10))):
            pass

    Args:
        limit: Maximum requests per window
        window_seconds: Time window in seconds
        key_func: Function to extract rate limit key from request
                 (defaults to client IP)

    Returns:
        FastAPI dependency function
    """
    def get_key(request: Request) -> str:
        """Default key function using client IP."""
        # Try to get real IP from proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    key_extractor = key_func or get_key

    async def rate_limit_dependency(request: Request) -> None:
        """Rate limiting dependency."""
        limiter = get_rate_limiter()
        key = key_extractor(request)

        if not limiter.is_allowed(key, limit):
            reset_seconds = limiter.get_reset_time(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Limit: {limit} requests per {window_seconds} seconds. Retry after {reset_seconds} seconds.",
                headers={
                    "Retry-After": str(reset_seconds),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_seconds),
                },
            )

        # Add rate limit headers to response
        remaining = limiter.get_remaining(key, limit)
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
        }

    return rate_limit_dependency


# =============================================================================
# Rate Limit by User
# =============================================================================

def rate_limit_by_user(
    limit: int = 100,
    window_seconds: int = 3600,
):
    """
    Rate limit by authenticated user ID.

    Requires authentication middleware to have run first.

    Usage:
        @router.get("/api/resource")
        async def resource_endpoint(
            user: AuthenticatedUser = Depends(get_current_user),
            _: None = Depends(rate_limit_by_user(limit=50)),
        ):
            pass
    """
    def get_user_key(request: Request) -> str:
        """Extract user ID from request state."""
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"
        # Fall back to IP if no user
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host}" if request.client else "ip:unknown"

    return rate_limit(
        limit=limit,
        window_seconds=window_seconds,
        key_func=get_user_key,
    )


# =============================================================================
# Rate Limit Middleware (Optional)
# =============================================================================

class RateLimitMiddleware:
    """
    ASGI middleware for global rate limiting.

    Can be used to apply rate limits to all requests.
    """

    def __init__(
        self,
        app,
        limit: int = 1000,
        window_seconds: int = 60,
        exclude_paths: Optional[List[str]] = None,
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: ASGI application
            limit: Maximum requests per window
            window_seconds: Time window in seconds
            exclude_paths: Paths to exclude from rate limiting
        """
        self.app = app
        self.limit = limit
        self.window_seconds = window_seconds
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]
        self.limiter = RateLimiter(
            default_limit=limit,
            window_seconds=window_seconds,
        )

    async def __call__(self, scope, receive, send):
        """Handle ASGI request."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # Skip excluded paths
        if any(path.startswith(ep) for ep in self.exclude_paths):
            await self.app(scope, receive, send)
            return

        # Get client IP
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        # Check for forwarded header
        headers = dict(scope.get("headers", []))
        forwarded = headers.get(b"x-forwarded-for", b"").decode()
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        key = f"global:{client_ip}"

        if not self.limiter.is_allowed(key, self.limit):
            # Send 429 response
            reset_seconds = self.limiter.get_reset_time(key)
            response = {
                "detail": f"Rate limit exceeded. Retry after {reset_seconds} seconds."
            }

            await send({
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    [b"content-type", b"application/json"],
                    [b"retry-after", str(reset_seconds).encode()],
                    [b"x-ratelimit-limit", str(self.limit).encode()],
                    [b"x-ratelimit-remaining", b"0"],
                ],
            })

            import json
            await send({
                "type": "http.response.body",
                "body": json.dumps(response).encode(),
            })
            return

        await self.app(scope, receive, send)
