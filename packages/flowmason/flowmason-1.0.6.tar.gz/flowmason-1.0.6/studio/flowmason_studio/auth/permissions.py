"""
Permission Enforcement Dependencies.

FastAPI dependencies for enforcing pipeline-level permissions on endpoints.
"""

from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from flowmason_studio.models.permissions import (
    EffectivePermissions,
    PermissionLevel,
)
from flowmason_studio.services.permission_storage import get_permission_storage


# Optional bearer token for extracting user info
security = HTTPBearer(auto_error=False)


class UserContext:
    """User context extracted from authentication."""

    def __init__(
        self,
        user_id: str,
        orgs: Optional[List[str]] = None,
        teams: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
        is_anonymous: bool = False,
    ):
        self.user_id = user_id
        self.orgs = orgs or []
        self.teams = teams or []
        self.scopes = scopes or []
        self.is_anonymous = is_anonymous


async def get_user_context(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> UserContext:
    """Extract user context from the request.

    Integrates with JWT tokens if present, otherwise returns anonymous context.

    TODO: Full JWT integration - extract claims from token.
    """
    if credentials and credentials.credentials:
        # In production, decode JWT and extract claims
        # For now, return a placeholder authenticated user
        token = credentials.credentials

        # Try to extract user info from JWT
        try:
            from flowmason_studio.auth.jwt import get_jwt_service
            jwt_service = get_jwt_service()
            payload = jwt_service.verify_token(token)
            if payload:
                # Extract orgs/teams from custom claims if present
                orgs = payload.custom.get("orgs", [])
                if payload.org_id:
                    orgs = [payload.org_id] if not orgs else orgs
                teams = payload.custom.get("teams", [])
                return UserContext(
                    user_id=payload.sub or "authenticated_user",
                    orgs=orgs if isinstance(orgs, list) else [],
                    teams=teams if isinstance(teams, list) else [],
                    scopes=payload.scopes or [],
                    is_anonymous=False,
                )
        except Exception:
            pass

        # Fallback for valid-looking token
        return UserContext(
            user_id="authenticated_user",
            is_anonymous=False,
        )

    # Check for API key in header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        # TODO: Lookup API key and get associated user/scopes
        return UserContext(
            user_id="api_key_user",
            scopes=["full"],  # Default scopes for API key
            is_anonymous=False,
        )

    # Anonymous user
    return UserContext(
        user_id="anonymous",
        is_anonymous=True,
    )


def require_permission(
    required_level: PermissionLevel,
    pipeline_id_param: str = "pipeline_id",
) -> Callable:
    """Create a dependency that requires a specific permission level.

    Args:
        required_level: The minimum permission level required
        pipeline_id_param: Name of the path parameter containing pipeline ID

    Usage:
        @router.get("/{pipeline_id}/run")
        async def run_pipeline(
            pipeline_id: str,
            user: UserContext = Depends(require_permission(PermissionLevel.RUN))
        ):
            ...
    """
    async def dependency(
        request: Request,
        user: UserContext = Depends(get_user_context),
    ) -> UserContext:
        # Get pipeline ID from path parameters
        pipeline_id = request.path_params.get(pipeline_id_param)
        if not pipeline_id:
            raise HTTPException(
                status_code=400,
                detail=f"Missing path parameter: {pipeline_id_param}"
            )

        storage = get_permission_storage()

        # Check permission
        has_access = storage.check_permission(
            pipeline_id,
            user.user_id,
            required_level,
            user.orgs,
            user.teams,
        )

        if not has_access:
            # Check if pipeline exists
            perms = storage.get_pipeline_permissions(pipeline_id)
            if not perms:
                raise HTTPException(
                    status_code=404,
                    detail="Pipeline not found"
                )

            raise HTTPException(
                status_code=403,
                detail=f"Requires {required_level.value} permission"
            )

        return user

    return dependency


def require_view(pipeline_id_param: str = "pipeline_id") -> Callable:
    """Require VIEW permission."""
    return require_permission(PermissionLevel.VIEW, pipeline_id_param)


def require_run(pipeline_id_param: str = "pipeline_id") -> Callable:
    """Require RUN permission."""
    return require_permission(PermissionLevel.RUN, pipeline_id_param)


def require_edit(pipeline_id_param: str = "pipeline_id") -> Callable:
    """Require EDIT permission."""
    return require_permission(PermissionLevel.EDIT, pipeline_id_param)


def require_admin(pipeline_id_param: str = "pipeline_id") -> Callable:
    """Require ADMIN permission."""
    return require_permission(PermissionLevel.ADMIN, pipeline_id_param)


def require_scope(required_scope: str) -> Callable:
    """Require a specific OAuth scope.

    Args:
        required_scope: The scope required (e.g., 'execute', 'read')
    """
    async def dependency(
        user: UserContext = Depends(get_user_context),
    ) -> UserContext:
        # Anonymous users have no scopes
        if user.is_anonymous:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )

        # Check for full access or specific scope
        if "full" not in user.scopes and required_scope not in user.scopes:
            raise HTTPException(
                status_code=403,
                detail=f"Requires '{required_scope}' scope"
            )

        return user

    return dependency


async def get_effective_permissions(
    pipeline_id: str,
    user: UserContext = Depends(get_user_context),
) -> EffectivePermissions:
    """Get the effective permissions for a user on a pipeline.

    Can be used to customize behavior based on user's access level.
    """
    storage = get_permission_storage()
    return storage.get_effective_permissions(
        pipeline_id,
        user.user_id,
        user.orgs,
        user.teams,
    )


class PermissionChecker:
    """Reusable permission checker for use within route handlers.

    Usage:
        checker = PermissionChecker()

        @router.get("/{pipeline_id}")
        async def get_pipeline(
            pipeline_id: str,
            user: UserContext = Depends(get_user_context),
        ):
            if not checker.can_view(pipeline_id, user):
                raise HTTPException(status_code=403)
            ...
    """

    def __init__(self):
        self.storage = get_permission_storage()

    def can_view(
        self,
        pipeline_id: str,
        user: UserContext,
    ) -> bool:
        """Check if user can view pipeline."""
        result: bool = self.storage.check_permission(
            pipeline_id, user.user_id, PermissionLevel.VIEW,
            user.orgs, user.teams
        )
        return result

    def can_run(
        self,
        pipeline_id: str,
        user: UserContext,
    ) -> bool:
        """Check if user can run pipeline."""
        result: bool = self.storage.check_permission(
            pipeline_id, user.user_id, PermissionLevel.RUN,
            user.orgs, user.teams
        )
        return result

    def can_edit(
        self,
        pipeline_id: str,
        user: UserContext,
    ) -> bool:
        """Check if user can edit pipeline."""
        result: bool = self.storage.check_permission(
            pipeline_id, user.user_id, PermissionLevel.EDIT,
            user.orgs, user.teams
        )
        return result

    def can_admin(
        self,
        pipeline_id: str,
        user: UserContext,
    ) -> bool:
        """Check if user can administer pipeline."""
        result: bool = self.storage.check_permission(
            pipeline_id, user.user_id, PermissionLevel.ADMIN,
            user.orgs, user.teams
        )
        return result

    def get_effective(
        self,
        pipeline_id: str,
        user: UserContext,
    ) -> EffectivePermissions:
        """Get effective permissions for user."""
        result: EffectivePermissions = self.storage.get_effective_permissions(
            pipeline_id, user.user_id, user.orgs, user.teams
        )
        return result


# Global checker instance
permission_checker = PermissionChecker()
