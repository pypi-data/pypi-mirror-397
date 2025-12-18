"""
Supabase JWT Authentication Middleware for FlowMason Studio.

Provides middleware and dependencies for verifying Supabase JWT tokens
and extracting user information for role-based access control.

DEPLOYMENT MODEL: Per-Customer Instance
Each FlowMason instance is deployed per-customer with its own Supabase project.
Users authenticate against the instance's Supabase, and roles control access
within that instance.
"""

import logging
import os
from functools import lru_cache
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

class SupabaseConfig:
    """Configuration for Supabase authentication."""

    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL", "")
        self.anon_key = os.environ.get("SUPABASE_ANON_KEY", "")
        self.service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    @property
    def is_configured(self) -> bool:
        """Check if Supabase is configured."""
        return bool(self.url and self.anon_key)


@lru_cache()
def get_supabase_config() -> SupabaseConfig:
    """Get cached Supabase configuration."""
    return SupabaseConfig()


# =============================================================================
# User Roles
# =============================================================================

class UserRole:
    """User role constants."""
    USER = "user"
    PIPELINE_DEVELOPER = "pipeline_developer"
    NODE_DEVELOPER = "node_developer"
    ADMIN = "admin"
    OWNER = "owner"


# =============================================================================
# Authenticated User Model
# =============================================================================

class AuthenticatedUser(BaseModel):
    """Authenticated user information from Supabase JWT."""
    id: str
    email: str
    role: str = UserRole.USER
    organization_id: Optional[str] = None
    display_name: Optional[str] = None


# =============================================================================
# Security Scheme
# =============================================================================

supabase_security = HTTPBearer(auto_error=False)


# =============================================================================
# Token Verification
# =============================================================================

async def verify_supabase_token(token: str, config: SupabaseConfig) -> Optional[dict]:
    """
    Verify a Supabase JWT token by calling the Supabase auth endpoint.

    Args:
        token: The JWT token to verify
        config: Supabase configuration

    Returns:
        User data from Supabase if valid, None if invalid
    """
    if not config.is_configured:
        logger.warning("Supabase is not configured, skipping token verification")
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": config.anon_key,
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                result = response.json()
                return dict(result) if isinstance(result, dict) else None
            else:
                logger.debug(f"Supabase token verification failed: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"Error verifying Supabase token: {e}")
        return None


async def get_user_profile(user_id: str, config: SupabaseConfig) -> Optional[dict]:
    """
    Fetch user profile from Supabase database.

    Args:
        user_id: The Supabase user ID
        config: Supabase configuration

    Returns:
        Profile data if found, None otherwise
    """
    if not config.service_role_key:
        logger.warning("SUPABASE_SERVICE_ROLE_KEY not set, cannot fetch profile")
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.url}/rest/v1/profiles",
                params={"id": f"eq.{user_id}", "select": "*"},
                headers={
                    "Authorization": f"Bearer {config.service_role_key}",
                    "apikey": config.anon_key,
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                profiles = response.json()
                return profiles[0] if profiles else None
            else:
                logger.debug(f"Failed to fetch profile: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        return None


# =============================================================================
# FastAPI Dependencies
# =============================================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(supabase_security),
) -> AuthenticatedUser:
    """
    FastAPI dependency to get the current authenticated user.

    This verifies the Supabase JWT token and fetches the user profile.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        AuthenticatedUser with user information and role

    Raises:
        HTTPException: If authentication fails
    """
    config = get_supabase_config()

    # Development mode: if Supabase not configured, return a dev user
    if not config.is_configured:
        logger.info("Supabase not configured - using development mode")
        return AuthenticatedUser(
            id="dev-user",
            email="dev@flowmason.local",
            role=UserRole.OWNER,
            organization_id=None,
            display_name="Development User",
        )

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Verify token with Supabase
    user_data = await verify_supabase_token(token, config)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = str(user_data.get("id", ""))
    email = user_data.get("email", "")

    # Fetch profile for role and organization
    profile = await get_user_profile(user_id, config) if user_id else None

    role = UserRole.USER
    organization_id = None
    display_name = None

    if profile:
        role = profile.get("role", UserRole.USER)
        organization_id = profile.get("organization_id")
        display_name = profile.get("display_name")

    return AuthenticatedUser(
        id=user_id,
        email=str(email),
        role=role,
        organization_id=organization_id,
        display_name=display_name or email.split("@")[0],
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(supabase_security),
) -> Optional[AuthenticatedUser]:
    """
    Optionally get the current user - returns None if not authenticated.

    Use this for endpoints that can work with or without authentication.
    """
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# =============================================================================
# Role-Based Access Control
# =============================================================================

def require_role(*allowed_roles: str):
    """
    Create a dependency that requires the user to have one of the specified roles.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            user: AuthenticatedUser = Depends(require_role("admin", "owner"))
        ):
            pass

    Args:
        allowed_roles: Tuple of role names that are allowed

    Returns:
        FastAPI dependency function
    """
    async def role_checker(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
            )
        return user

    return role_checker


# Pre-built role dependencies for convenience
require_admin = require_role(UserRole.ADMIN, UserRole.OWNER)
require_node_developer = require_role(
    UserRole.NODE_DEVELOPER,
    UserRole.ADMIN,
    UserRole.OWNER
)
require_pipeline_developer = require_role(
    UserRole.PIPELINE_DEVELOPER,
    UserRole.NODE_DEVELOPER,
    UserRole.ADMIN,
    UserRole.OWNER
)


# =============================================================================
# Permission Helpers
# =============================================================================

def can_access_lab(user: AuthenticatedUser) -> bool:
    """Check if user can access the Lab (Node Workshop)."""
    return user.role in (UserRole.NODE_DEVELOPER, UserRole.ADMIN, UserRole.OWNER)


def can_access_builder(user: AuthenticatedUser) -> bool:
    """Check if user can access the Pipeline Builder."""
    return user.role in (
        UserRole.PIPELINE_DEVELOPER,
        UserRole.NODE_DEVELOPER,
        UserRole.ADMIN,
        UserRole.OWNER,
    )


def can_manage_users(user: AuthenticatedUser) -> bool:
    """Check if user can manage other users."""
    return user.role in (UserRole.ADMIN, UserRole.OWNER)
