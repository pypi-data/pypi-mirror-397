"""
Pipeline Permission Models.

Defines the data structures for fine-grained pipeline access control.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class PermissionLevel(str, Enum):
    """Permission levels for pipeline access."""

    VIEW = "view"  # Can view pipeline definition and execution history
    RUN = "run"  # Can execute pipeline (includes view)
    EDIT = "edit"  # Can modify pipeline (includes run)
    ADMIN = "admin"  # Full control including permissions management


class PipelineVisibility(str, Enum):
    """Pipeline visibility settings."""

    PRIVATE = "private"  # Only owner and explicit grants
    ORG = "org"  # Visible to organization members
    PUBLIC = "public"  # Visible to all authenticated users


class PrincipalType(str, Enum):
    """Types of permission principals."""

    USER = "user"
    ORG = "org"
    TEAM = "team"
    API_KEY = "api_key"
    WILDCARD = "*"  # All authenticated users


class PermissionGrant(BaseModel):
    """A single permission grant to a principal."""

    id: str = Field(default="", description="Unique identifier for this grant")
    principal_type: PrincipalType = Field(
        default=PrincipalType.USER,
        description="Type of principal receiving the grant"
    )
    principal_id: str = Field(
        description="ID of the user, org, team, or '*' for wildcard"
    )
    level: PermissionLevel = Field(
        description="Permission level granted"
    )
    granted_by: Optional[str] = Field(
        default=None,
        description="User ID who granted this permission"
    )
    granted_at: Optional[datetime] = Field(
        default=None,
        description="When the permission was granted"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Optional expiration time for the grant"
    )


class PipelinePermissions(BaseModel):
    """Complete permission set for a pipeline."""

    pipeline_id: str = Field(description="Pipeline ID these permissions apply to")
    owner_id: str = Field(description="User ID of the pipeline owner")
    visibility: PipelineVisibility = Field(
        default=PipelineVisibility.PRIVATE,
        description="Base visibility setting"
    )
    grants: List[PermissionGrant] = Field(
        default_factory=list,
        description="Explicit permission grants"
    )
    inherit_from_folder: bool = Field(
        default=True,
        description="Whether to inherit permissions from parent folder"
    )
    folder_id: Optional[str] = Field(
        default=None,
        description="Parent folder ID for permission inheritance"
    )
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class FolderPermissions(BaseModel):
    """Permission set for a folder (for inheritance)."""

    folder_id: str = Field(description="Folder ID")
    owner_id: str = Field(description="User ID of the folder owner")
    visibility: PipelineVisibility = Field(
        default=PipelineVisibility.PRIVATE
    )
    grants: List[PermissionGrant] = Field(default_factory=list)
    parent_folder_id: Optional[str] = Field(
        default=None,
        description="Parent folder for nested inheritance"
    )
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


# API Request/Response Models


class GrantPermissionRequest(BaseModel):
    """Request to grant permission to a principal."""

    principal_type: PrincipalType = Field(default=PrincipalType.USER)
    principal_id: str = Field(description="ID of principal to grant access to")
    level: PermissionLevel = Field(description="Permission level to grant")
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Optional expiration time"
    )


class UpdateVisibilityRequest(BaseModel):
    """Request to update pipeline visibility."""

    visibility: PipelineVisibility


class BulkPermissionRequest(BaseModel):
    """Request to set multiple permissions at once."""

    visibility: Optional[PipelineVisibility] = None
    grants: List[GrantPermissionRequest] = Field(default_factory=list)
    inherit_from_folder: Optional[bool] = None


class PermissionCheckResult(BaseModel):
    """Result of a permission check."""

    has_access: bool = Field(description="Whether access is granted")
    effective_level: Optional[PermissionLevel] = Field(
        default=None,
        description="The effective permission level if access is granted"
    )
    grant_source: Optional[str] = Field(
        default=None,
        description="Where the permission came from (direct, folder, visibility, owner)"
    )


class EffectivePermissions(BaseModel):
    """Complete effective permissions for a user on a pipeline."""

    pipeline_id: str
    user_id: str
    is_owner: bool = False
    effective_level: Optional[PermissionLevel] = None
    direct_grant: Optional[PermissionGrant] = None
    inherited_grants: List[PermissionGrant] = Field(default_factory=list)
    visibility_access: bool = False
    can_view: bool = False
    can_run: bool = False
    can_edit: bool = False
    can_admin: bool = False


# Permission level hierarchy helpers


PERMISSION_HIERARCHY = {
    PermissionLevel.VIEW: 1,
    PermissionLevel.RUN: 2,
    PermissionLevel.EDIT: 3,
    PermissionLevel.ADMIN: 4,
}


def level_includes(granted: PermissionLevel, required: PermissionLevel) -> bool:
    """Check if a granted permission level includes the required level."""
    return PERMISSION_HIERARCHY[granted] >= PERMISSION_HIERARCHY[required]


def get_max_level(
    levels: List[PermissionLevel]
) -> Optional[PermissionLevel]:
    """Get the highest permission level from a list."""
    if not levels:
        return None
    return max(levels, key=lambda l: PERMISSION_HIERARCHY[l])
