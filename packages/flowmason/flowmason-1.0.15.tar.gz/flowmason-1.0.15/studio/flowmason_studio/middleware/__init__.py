"""
FlowMason Studio Middleware.

Provides authentication, rate limiting, and other middleware components.
"""

from flowmason_studio.middleware.auth import (
    AuthenticatedUser,
    UserRole,
    get_current_user,
    get_optional_user,
    require_admin,
    require_pipeline_developer,
    require_role,
)
from flowmason_studio.middleware.rate_limit import (
    RateLimiter,
    get_rate_limiter,
    rate_limit,
)

__all__ = [
    # Authentication
    "AuthenticatedUser",
    "UserRole",
    "get_current_user",
    "get_optional_user",
    "require_role",
    "require_admin",
    "require_pipeline_developer",
    # Rate limiting
    "RateLimiter",
    "rate_limit",
    "get_rate_limiter",
]
