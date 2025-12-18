"""
Pipeline Permission API Routes.

Provides HTTP API for managing pipeline-level permissions.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from flowmason_studio.models.permissions import (
    BulkPermissionRequest,
    EffectivePermissions,
    GrantPermissionRequest,
    PermissionCheckResult,
    PermissionGrant,
    PermissionLevel,
    PipelinePermissions,
    PipelineVisibility,
    PrincipalType,
    UpdateVisibilityRequest,
    level_includes,
)
from flowmason_studio.services.permission_storage import get_permission_storage

router = APIRouter(prefix="/permissions", tags=["permissions"])


# =============================================================================
# Helper Functions
# =============================================================================


def get_current_user_id() -> str:
    """Get the current user ID from auth context.

    TODO: Integrate with JWT auth to get real user ID.
    For now, returns a placeholder.
    """
    # In production, this would extract user_id from JWT token
    return "current_user"


def get_user_context() -> dict:
    """Get full user context including orgs and teams.

    TODO: Integrate with auth system.
    """
    return {
        "user_id": "current_user",
        "orgs": [],
        "teams": [],
    }


def require_admin(pipeline_id: str, user_id: str) -> None:
    """Require admin permission on a pipeline."""
    storage = get_permission_storage()
    if not storage.check_permission(
        pipeline_id, user_id, PermissionLevel.ADMIN
    ):
        raise HTTPException(
            status_code=403,
            detail="Admin permission required for this operation"
        )


# =============================================================================
# Response Models
# =============================================================================


class PermissionResponse(BaseModel):
    """Response for permission operations."""

    success: bool
    message: str
    permissions: Optional[PipelinePermissions] = None


class GrantListResponse(BaseModel):
    """Response listing all grants."""

    pipeline_id: str
    grants: List[PermissionGrant]
    total: int


class AccessiblePipelinesResponse(BaseModel):
    """Response listing accessible pipelines."""

    pipelines: List[dict]
    total: int


# =============================================================================
# Pipeline Permission Endpoints
# =============================================================================


@router.get("/{pipeline_id}", response_model=PipelinePermissions)
async def get_permissions(pipeline_id: str) -> PipelinePermissions:
    """Get permissions for a pipeline.

    Requires at least VIEW permission on the pipeline.
    """
    user = get_user_context()
    storage = get_permission_storage()

    perms = storage.get_pipeline_permissions(pipeline_id)
    if not perms:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Check view permission
    if not storage.check_permission(
        pipeline_id, user["user_id"], PermissionLevel.VIEW,
        user.get("orgs"), user.get("teams")
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return perms


@router.post("/{pipeline_id}", response_model=PipelinePermissions)
async def create_permissions(
    pipeline_id: str,
    visibility: PipelineVisibility = PipelineVisibility.PRIVATE,
    folder_id: Optional[str] = None,
) -> PipelinePermissions:
    """Create permissions for a new pipeline.

    Should be called when creating a new pipeline.
    The current user becomes the owner.
    """
    user_id = get_current_user_id()
    storage = get_permission_storage()

    # Check if already exists
    existing = storage.get_pipeline_permissions(pipeline_id)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Permissions already exist for this pipeline"
        )

    return storage.create_pipeline_permissions(
        pipeline_id=pipeline_id,
        owner_id=user_id,
        visibility=visibility,
        folder_id=folder_id,
    )


@router.put("/{pipeline_id}/visibility", response_model=PipelinePermissions)
async def update_visibility(
    pipeline_id: str,
    request: UpdateVisibilityRequest,
) -> PipelinePermissions:
    """Update pipeline visibility.

    Requires ADMIN permission.
    """
    user_id = get_current_user_id()
    storage = get_permission_storage()

    require_admin(pipeline_id, user_id)

    result = storage.update_visibility(pipeline_id, request.visibility)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    return result


@router.put("/{pipeline_id}/inheritance", response_model=PipelinePermissions)
async def update_inheritance(
    pipeline_id: str,
    inherit: bool = True,
    folder_id: Optional[str] = None,
) -> PipelinePermissions:
    """Update folder inheritance settings.

    Requires ADMIN permission.
    """
    user_id = get_current_user_id()
    storage = get_permission_storage()

    require_admin(pipeline_id, user_id)

    result = storage.set_folder_inheritance(pipeline_id, inherit, folder_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    return result


@router.delete("/{pipeline_id}", response_model=PermissionResponse)
async def delete_permissions(pipeline_id: str) -> PermissionResponse:
    """Delete all permissions for a pipeline.

    Requires ADMIN permission. Usually called when deleting a pipeline.
    """
    user_id = get_current_user_id()
    storage = get_permission_storage()

    require_admin(pipeline_id, user_id)

    success = storage.delete_pipeline_permissions(pipeline_id)
    return PermissionResponse(
        success=success,
        message="Permissions deleted" if success else "Pipeline not found",
    )


# =============================================================================
# Grant Management
# =============================================================================


@router.get("/{pipeline_id}/grants", response_model=GrantListResponse)
async def list_grants(pipeline_id: str) -> GrantListResponse:
    """List all permission grants for a pipeline.

    Requires VIEW permission.
    """
    user = get_user_context()
    storage = get_permission_storage()

    perms = storage.get_pipeline_permissions(pipeline_id)
    if not perms:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    # Check view permission
    if not storage.check_permission(
        pipeline_id, user["user_id"], PermissionLevel.VIEW,
        user.get("orgs"), user.get("teams")
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return GrantListResponse(
        pipeline_id=pipeline_id,
        grants=perms.grants,
        total=len(perms.grants),
    )


@router.post("/{pipeline_id}/grants", response_model=PermissionGrant)
async def add_grant(
    pipeline_id: str,
    request: GrantPermissionRequest,
) -> PermissionGrant:
    """Add a permission grant to a pipeline.

    Requires ADMIN permission. Cannot grant higher than your own level.
    """
    user = get_user_context()
    user_id = user["user_id"]
    storage = get_permission_storage()

    # Check admin permission
    effective = storage.get_effective_permissions(
        pipeline_id, user_id, user.get("orgs"), user.get("teams")
    )

    if not effective.can_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin permission required to grant permissions"
        )

    # Cannot grant higher than own level (unless owner)
    if not effective.is_owner and effective.effective_level:
        if not level_includes(effective.effective_level, request.level):
            raise HTTPException(
                status_code=403,
                detail="Cannot grant permission level higher than your own"
            )

    return storage.add_grant(
        pipeline_id=pipeline_id,
        principal_type=request.principal_type,
        principal_id=request.principal_id,
        level=request.level,
        granted_by=user_id,
        expires_at=request.expires_at,
    )


@router.delete(
    "/{pipeline_id}/grants/{principal_type}/{principal_id}",
    response_model=PermissionResponse
)
async def remove_grant(
    pipeline_id: str,
    principal_type: PrincipalType,
    principal_id: str,
) -> PermissionResponse:
    """Remove a permission grant.

    Requires ADMIN permission.
    """
    user_id = get_current_user_id()
    storage = get_permission_storage()

    require_admin(pipeline_id, user_id)

    success = storage.remove_grant(pipeline_id, principal_type, principal_id)
    return PermissionResponse(
        success=success,
        message="Grant removed" if success else "Grant not found",
    )


@router.delete("/{pipeline_id}/grants", response_model=PermissionResponse)
async def remove_all_grants(pipeline_id: str) -> PermissionResponse:
    """Remove all grants from a pipeline.

    Requires ADMIN permission. Does not affect visibility or inheritance.
    """
    user_id = get_current_user_id()
    storage = get_permission_storage()

    require_admin(pipeline_id, user_id)

    count = storage.remove_all_grants(pipeline_id)
    return PermissionResponse(
        success=True,
        message=f"Removed {count} grants",
    )


# =============================================================================
# Bulk Operations
# =============================================================================


@router.put("/{pipeline_id}/bulk", response_model=PipelinePermissions)
async def bulk_update(
    pipeline_id: str,
    request: BulkPermissionRequest,
) -> PipelinePermissions:
    """Update visibility and grants in a single operation.

    Requires ADMIN permission.
    """
    user = get_user_context()
    user_id = user["user_id"]
    storage = get_permission_storage()

    require_admin(pipeline_id, user_id)

    # Update visibility if provided
    if request.visibility is not None:
        storage.update_visibility(pipeline_id, request.visibility)

    # Update inheritance if provided
    if request.inherit_from_folder is not None:
        storage.set_folder_inheritance(
            pipeline_id, request.inherit_from_folder
        )

    # Add grants
    for grant_req in request.grants:
        storage.add_grant(
            pipeline_id=pipeline_id,
            principal_type=grant_req.principal_type,
            principal_id=grant_req.principal_id,
            level=grant_req.level,
            granted_by=user_id,
            expires_at=grant_req.expires_at,
        )

    result = storage.get_pipeline_permissions(pipeline_id)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return result


# =============================================================================
# Permission Checking
# =============================================================================


@router.get("/{pipeline_id}/check", response_model=PermissionCheckResult)
async def check_permission(
    pipeline_id: str,
    level: PermissionLevel = Query(
        PermissionLevel.VIEW,
        description="Permission level to check"
    ),
) -> PermissionCheckResult:
    """Check if the current user has a specific permission level.

    Returns whether access is granted and the effective permission level.
    """
    user = get_user_context()
    storage = get_permission_storage()

    effective = storage.get_effective_permissions(
        pipeline_id, user["user_id"], user.get("orgs"), user.get("teams")
    )

    has_access = False
    grant_source: Optional[str] = None

    if effective.effective_level:
        has_access = level_includes(effective.effective_level, level)

        if effective.is_owner:
            grant_source = "owner"
        elif effective.direct_grant:
            grant_source = "direct"
        elif effective.inherited_grants:
            grant_source = "folder"
        elif effective.visibility_access:
            grant_source = "visibility"

    return PermissionCheckResult(
        has_access=has_access,
        effective_level=effective.effective_level,
        grant_source=grant_source,
    )


@router.get("/{pipeline_id}/effective", response_model=EffectivePermissions)
async def get_effective_permissions(
    pipeline_id: str,
) -> EffectivePermissions:
    """Get the effective permissions for the current user.

    Returns detailed information about how permissions are resolved.
    """
    user = get_user_context()
    storage = get_permission_storage()

    return storage.get_effective_permissions(
        pipeline_id, user["user_id"], user.get("orgs"), user.get("teams")
    )


# =============================================================================
# User Access List
# =============================================================================


@router.get("/user/accessible", response_model=AccessiblePipelinesResponse)
async def list_accessible_pipelines(
    min_level: PermissionLevel = Query(
        PermissionLevel.VIEW,
        description="Minimum permission level required"
    ),
) -> AccessiblePipelinesResponse:
    """List all pipelines the current user can access.

    Filters by minimum permission level.
    """
    user = get_user_context()
    storage = get_permission_storage()

    pipelines = storage.list_user_accessible_pipelines(
        user["user_id"],
        min_level,
        user.get("orgs"),
        user.get("teams"),
    )

    return AccessiblePipelinesResponse(
        pipelines=pipelines,
        total=len(pipelines),
    )


# =============================================================================
# Share Shortcut
# =============================================================================


class ShareRequest(BaseModel):
    """Request to share a pipeline with users."""

    users: List[str] = Field(
        default_factory=list,
        description="User IDs to share with"
    )
    orgs: List[str] = Field(
        default_factory=list,
        description="Organization IDs to share with"
    )
    teams: List[str] = Field(
        default_factory=list,
        description="Team IDs to share with"
    )
    level: PermissionLevel = Field(
        default=PermissionLevel.VIEW,
        description="Permission level to grant"
    )
    make_public: bool = Field(
        default=False,
        description="Make the pipeline publicly viewable"
    )


class ShareResponse(BaseModel):
    """Response from share operation."""

    success: bool
    grants_added: int
    visibility_changed: bool


@router.post("/{pipeline_id}/share", response_model=ShareResponse)
async def share_pipeline(
    pipeline_id: str,
    request: ShareRequest,
) -> ShareResponse:
    """Share a pipeline with users, organizations, or teams.

    Convenience endpoint that wraps grant and visibility operations.
    Requires ADMIN permission.
    """
    user_id = get_current_user_id()
    storage = get_permission_storage()

    require_admin(pipeline_id, user_id)

    grants_added = 0

    # Add user grants
    for uid in request.users:
        storage.add_grant(
            pipeline_id=pipeline_id,
            principal_type=PrincipalType.USER,
            principal_id=uid,
            level=request.level,
            granted_by=user_id,
        )
        grants_added += 1

    # Add org grants
    for org_id in request.orgs:
        storage.add_grant(
            pipeline_id=pipeline_id,
            principal_type=PrincipalType.ORG,
            principal_id=org_id,
            level=request.level,
            granted_by=user_id,
        )
        grants_added += 1

    # Add team grants
    for team_id in request.teams:
        storage.add_grant(
            pipeline_id=pipeline_id,
            principal_type=PrincipalType.TEAM,
            principal_id=team_id,
            level=request.level,
            granted_by=user_id,
        )
        grants_added += 1

    # Update visibility if requested
    visibility_changed = False
    if request.make_public:
        storage.update_visibility(pipeline_id, PipelineVisibility.PUBLIC)
        visibility_changed = True

    return ShareResponse(
        success=True,
        grants_added=grants_added,
        visibility_changed=visibility_changed,
    )
