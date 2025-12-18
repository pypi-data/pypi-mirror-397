"""
FlowMason Authentication Middleware

FastAPI dependencies for API authentication.
"""

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .models import APIKey, APIKeyScope, Organization, User
from .service import get_auth_service

# HTTP Bearer scheme for API key auth
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    """
    Authentication context passed to route handlers.

    Contains information about the authenticated entity.
    """
    org: Organization
    api_key: Optional[APIKey] = None
    user: Optional[User] = None

    # Request metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def has_scope(self, scope: APIKeyScope) -> bool:
        """Check if the current auth context has a specific scope"""
        if self.api_key is None:
            return True  # User auth has full scope
        return self.api_key.has_scope(scope)


async def get_api_key_from_header(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[str]:
    """
    Extract API key from request headers.

    Supports two formats:
    - Authorization: Bearer <api_key>
    - X-API-Key: <api_key>
    """
    if authorization:
        return authorization.credentials
    return x_api_key


async def get_current_user(
    request: Request,
    api_key: Optional[str] = Depends(get_api_key_from_header),
) -> Optional[AuthContext]:
    """
    Get the current authenticated user/org from the API key.

    Returns None if no valid authentication is provided.
    Does not raise an exception - use require_auth for protected routes.
    """
    if not api_key:
        return None

    auth_service = get_auth_service()
    result = auth_service.verify_api_key(api_key)

    if not result:
        return None

    key, org = result

    # Get user if key is tied to one
    user = None
    if key.user_id:
        user = auth_service.get_user(key.user_id)

    return AuthContext(
        org=org,
        api_key=key,
        user=user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


async def require_auth(
    auth: Optional[AuthContext] = Depends(get_current_user),
) -> AuthContext:
    """
    Require authentication for a route.

    Raises 401 if no valid authentication is provided.

    Usage:
        @router.get("/protected")
        async def protected_route(auth: AuthContext = Depends(require_auth)):
            return {"org": auth.org.name}
    """
    if not auth:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth


async def optional_auth(
    auth: Optional[AuthContext] = Depends(get_current_user),
) -> Optional[AuthContext]:
    """
    Optional authentication for a route.

    Returns None if no authentication is provided (doesn't raise).

    Usage:
        @router.get("/public")
        async def public_route(auth: Optional[AuthContext] = Depends(optional_auth)):
            if auth:
                return {"org": auth.org.name}
            return {"message": "Anonymous access"}
    """
    return auth


def require_scope(scope: APIKeyScope):
    """
    Decorator factory for requiring a specific API key scope.

    Usage:
        @router.post("/pipelines")
        async def create_pipeline(
            auth: AuthContext = Depends(require_scope(APIKeyScope.FULL))
        ):
            ...
    """
    async def scope_checker(
        auth: AuthContext = Depends(require_auth),
    ) -> AuthContext:
        if not auth.has_scope(scope):
            raise HTTPException(
                status_code=403,
                detail=f"API key does not have required scope: {scope.value}",
            )
        return auth

    return scope_checker


def require_org_role(min_role: str):
    """
    Require minimum organization role for user-based auth.

    Roles in order: viewer < developer < admin < owner

    Usage:
        @router.delete("/pipelines/{id}")
        async def delete_pipeline(
            auth: AuthContext = Depends(require_org_role("admin"))
        ):
            ...
    """
    from .models import Role

    role_hierarchy = {
        Role.VIEWER: 0,
        Role.DEVELOPER: 1,
        Role.ADMIN: 2,
        Role.OWNER: 3,
    }

    required_level = role_hierarchy.get(Role(min_role), 0)

    async def role_checker(
        auth: AuthContext = Depends(require_auth),
    ) -> AuthContext:
        if not auth.user:
            # API key auth - check scopes instead
            if min_role in ("admin", "owner"):
                if not auth.has_scope(APIKeyScope.FULL):
                    raise HTTPException(
                        status_code=403,
                        detail="API key does not have admin scope",
                    )
            return auth

        # User auth - check role
        auth_service = get_auth_service()
        role = auth_service.get_user_role_in_org(auth.user.id, auth.org.id)

        if not role or role_hierarchy.get(role, 0) < required_level:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {min_role}",
            )

        return auth

    return role_checker


class RateLimiter:
    """
    In-memory rate limiter for development.

    For production, use RedisRateLimiter instead.
    """

    def __init__(self):
        self._requests: dict[str, list[float]] = {}

    def check(self, key: str, limit: int, window_seconds: int = 3600) -> bool:
        """
        Check if request is within rate limit.

        Args:
            key: Identifier (e.g., API key ID)
            limit: Maximum requests per window
            window_seconds: Window size in seconds (default: 1 hour)

        Returns:
            True if within limit, False if exceeded
        """
        import time

        now = time.time()
        window_start = now - window_seconds

        # Get requests in window
        if key not in self._requests:
            self._requests[key] = []

        # Clean old requests
        self._requests[key] = [
            t for t in self._requests[key]
            if t > window_start
        ]

        # Check limit
        if len(self._requests[key]) >= limit:
            return False

        # Add this request
        self._requests[key].append(now)
        return True

    def get_remaining(self, key: str, limit: int, window_seconds: int = 3600) -> int:
        """Get remaining requests in window."""
        import time
        now = time.time()
        window_start = now - window_seconds

        if key not in self._requests:
            return limit

        current = len([t for t in self._requests[key] if t > window_start])
        return max(0, limit - current)

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        if key in self._requests:
            del self._requests[key]


class RedisRateLimiter:
    """
    Redis-backed rate limiter for production multi-instance deployments.

    Uses sliding window algorithm with sorted sets for accurate rate limiting.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize Redis rate limiter.

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
        """
        try:
            import redis
            self._redis = redis.from_url(redis_url, decode_responses=True)
            self._available = True
        except ImportError:
            self._redis = None
            self._available = False
        except Exception:
            self._redis = None
            self._available = False

    @property
    def is_available(self) -> bool:
        """Check if Redis connection is available."""
        if not self._available or not self._redis:
            return False
        try:
            self._redis.ping()
            return True
        except Exception:
            return False

    def check(self, key: str, limit: int, window_seconds: int = 3600) -> bool:
        """
        Check if request is within rate limit using sliding window.

        Args:
            key: Identifier (e.g., API key ID)
            limit: Maximum requests per window
            window_seconds: Window size in seconds (default: 1 hour)

        Returns:
            True if within limit, False if exceeded
        """
        if not self._redis:
            return True  # Fail open if Redis unavailable

        import time

        now = time.time()
        window_start = now - window_seconds
        rate_key = f"ratelimit:{key}"

        try:
            pipe = self._redis.pipeline()

            # Remove old entries outside the window
            pipe.zremrangebyscore(rate_key, 0, window_start)

            # Count current entries in window
            pipe.zcard(rate_key)

            # Add current request with timestamp as score
            pipe.zadd(rate_key, {f"{now}:{id(now)}": now})

            # Set expiry on the key
            pipe.expire(rate_key, window_seconds + 60)

            results = pipe.execute()
            current_count = results[1]

            # Check if over limit (check before adding)
            if current_count >= limit:
                # Remove the request we just added since it's over limit
                self._redis.zremrangebyscore(rate_key, now, now + 1)
                return False

            return True

        except Exception:
            # Fail open on Redis errors
            return True

    def get_remaining(self, key: str, limit: int, window_seconds: int = 3600) -> int:
        """Get remaining requests in window."""
        if not self._redis:
            return limit

        import time
        now = time.time()
        window_start = now - window_seconds
        rate_key = f"ratelimit:{key}"

        try:
            # Remove old entries and count
            self._redis.zremrangebyscore(rate_key, 0, window_start)
            current = self._redis.zcard(rate_key)
            return max(0, limit - current)
        except Exception:
            return limit

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        if self._redis:
            try:
                self._redis.delete(f"ratelimit:{key}")
            except Exception:
                pass

    def get_reset_time(self, key: str, window_seconds: int = 3600) -> int:
        """Get seconds until rate limit resets."""
        if not self._redis:
            return window_seconds

        rate_key = f"ratelimit:{key}"
        try:
            # Get oldest entry timestamp
            oldest = self._redis.zrange(rate_key, 0, 0, withscores=True)
            if oldest:
                oldest_time = oldest[0][1]
                reset_time = oldest_time + window_seconds
                import time
                return max(0, int(reset_time - time.time()))
            return window_seconds
        except Exception:
            return window_seconds


class HybridRateLimiter:
    """
    Hybrid rate limiter that uses Redis if available, falls back to in-memory.

    Automatically detects Redis availability and switches between backends.
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize hybrid rate limiter.

        Args:
            redis_url: Optional Redis URL. If None, uses REDIS_URL env var or falls back to in-memory.
        """
        import os
        self._redis_url = redis_url or os.getenv("REDIS_URL")
        self._memory_limiter = RateLimiter()
        self._redis_limiter: Optional[RedisRateLimiter] = None

        if self._redis_url:
            self._redis_limiter = RedisRateLimiter(self._redis_url)

    def _get_backend(self):
        """Get the appropriate backend based on availability."""
        if self._redis_limiter and self._redis_limiter.is_available:
            return self._redis_limiter
        return self._memory_limiter

    def check(self, key: str, limit: int, window_seconds: int = 3600) -> bool:
        """Check if request is within rate limit."""
        return self._get_backend().check(key, limit, window_seconds)

    def get_remaining(self, key: str, limit: int, window_seconds: int = 3600) -> int:
        """Get remaining requests in window."""
        return self._get_backend().get_remaining(key, limit, window_seconds)

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        self._get_backend().reset(key)

    @property
    def backend_type(self) -> str:
        """Get the current backend type."""
        if self._redis_limiter and self._redis_limiter.is_available:
            return "redis"
        return "memory"


# Global rate limiter instance - uses hybrid approach
_rate_limiter = HybridRateLimiter()


async def check_rate_limit(
    auth: AuthContext = Depends(require_auth),
) -> AuthContext:
    """
    Check rate limit for the authenticated entity.

    Raises 429 if rate limit is exceeded.
    """
    if auth.api_key:
        key_id = auth.api_key.id
        limit = auth.api_key.rate_limit
    else:
        # User auth - use org-level limit
        key_id = f"user_{auth.user.id if auth.user else 'unknown'}"
        limit = 1000  # Default limit

    if not _rate_limiter.check(key_id, limit):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": "3600"},
        )

    return auth
