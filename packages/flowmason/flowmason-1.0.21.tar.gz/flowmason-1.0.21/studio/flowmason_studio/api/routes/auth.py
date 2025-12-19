"""
FlowMason Authentication API Routes

Endpoints for managing organizations, users, and API keys.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...auth import (
    AuthContext,
    AuthService,
    get_auth_service,
    require_auth,
)
from ...auth.models import APIKeyScope, Role

router = APIRouter(prefix="/auth", tags=["auth"])


# ==================== Request/Response Models ====================


class CreateOrgRequest(BaseModel):
    """Request to create a new organization"""
    name: str
    slug: str


class OrgResponse(BaseModel):
    """Organization response"""
    id: str
    name: str
    slug: str
    plan: str
    max_users: int
    max_pipelines: int
    max_executions_per_day: int
    created_at: datetime


class CreateUserRequest(BaseModel):
    """Request to create a new user"""
    email: str  # Email validation should be done in the service layer
    name: str
    password: Optional[str] = None


class UserResponse(BaseModel):
    """User response"""
    id: str
    email: str
    name: str
    email_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class AddUserToOrgRequest(BaseModel):
    """Request to add a user to an organization"""
    user_id: str
    role: str = "developer"


class CreateAPIKeyRequest(BaseModel):
    """Request to create an API key"""
    name: str
    scopes: List[str] = ["full"]
    expires_at: Optional[datetime] = None


class APIKeyResponse(BaseModel):
    """API key response (without sensitive data)"""
    id: str
    name: str
    key_prefix: str
    scopes: List[str]
    rate_limit: int
    is_active: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime


class APIKeyCreatedResponse(BaseModel):
    """Response when creating an API key (includes raw key)"""
    api_key: APIKeyResponse
    raw_key: str  # Only shown once!


class AuditLogEntryResponse(BaseModel):
    """Audit log entry response"""
    id: str
    timestamp: datetime
    user_id: Optional[str]
    api_key_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: dict
    success: bool
    error_message: Optional[str]


class WhoAmIResponse(BaseModel):
    """Response for whoami endpoint"""
    org: OrgResponse
    user: Optional[UserResponse] = None
    api_key: Optional[APIKeyResponse] = None
    scopes: List[str]


# ==================== Organization Endpoints ====================


@router.post("/orgs", response_model=OrgResponse)
async def create_organization(
    request: CreateOrgRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> OrgResponse:
    """
    Create a new organization.

    This is typically an admin/bootstrap operation.
    In production, this would require special privileges.
    """
    # Check if slug already exists
    existing = auth_service.get_org_by_slug(request.slug)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Organization with slug '{request.slug}' already exists"
        )

    org = auth_service.create_org(request.name, request.slug)

    return OrgResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        max_users=org.max_users,
        max_pipelines=org.max_pipelines,
        max_executions_per_day=org.max_executions_per_day,
        created_at=org.created_at,
    )


@router.get("/orgs/current", response_model=OrgResponse)
async def get_current_org(
    auth: AuthContext = Depends(require_auth),
) -> OrgResponse:
    """Get the current organization (from API key)"""
    return OrgResponse(
        id=auth.org.id,
        name=auth.org.name,
        slug=auth.org.slug,
        plan=auth.org.plan,
        max_users=auth.org.max_users,
        max_pipelines=auth.org.max_pipelines,
        max_executions_per_day=auth.org.max_executions_per_day,
        created_at=auth.org.created_at,
    )


# ==================== User Endpoints ====================


@router.post("/users", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Create a new user.

    In production, this would typically be done through
    signup flow or SSO.
    """
    # Check if email already exists
    existing = auth_service.get_user_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"User with email '{request.email}' already exists"
        )

    user = auth_service.create_user(
        email=request.email,
        name=request.name,
        password=request.password,
    )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        email_verified=user.email_verified,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.post("/orgs/current/members")
async def add_user_to_org(
    request: AddUserToOrgRequest,
    auth: AuthContext = Depends(require_auth),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Add a user to the current organization"""
    # Verify user exists
    user = auth_service.get_user(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already a member
    existing_role = auth_service.get_user_role_in_org(request.user_id, auth.org.id)
    if existing_role:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this organization"
        )

    try:
        role = Role(request.role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: {request.role}. Valid roles: owner, admin, developer, viewer"
        )

    membership = auth_service.add_user_to_org(request.user_id, auth.org.id, role)

    # Audit log
    auth_service.log_action(
        org_id=auth.org.id,
        action="user.add",
        resource_type="user",
        resource_id=request.user_id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        details={"role": role.value},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )

    return {
        "message": "User added to organization",
        "membership_id": membership.id,
        "role": role.value,
    }


# ==================== API Key Endpoints ====================


@router.post("/api-keys", response_model=APIKeyCreatedResponse)
async def create_api_key(
    request: CreateAPIKeyRequest,
    auth: AuthContext = Depends(require_auth),
    auth_service: AuthService = Depends(get_auth_service),
) -> APIKeyCreatedResponse:
    """
    Create a new API key for the current organization.

    The raw key is only returned once - store it securely!
    """
    # Parse scopes
    try:
        scopes = [APIKeyScope(s) for s in request.scopes]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid scope. Valid scopes: full, read, execute, deploy"
        )

    api_key, raw_key = auth_service.create_api_key(
        name=request.name,
        org_id=auth.org.id,
        user_id=auth.user.id if auth.user else None,
        scopes=scopes,
        expires_at=request.expires_at,
    )

    # Audit log
    auth_service.log_action(
        org_id=auth.org.id,
        action="api_key.create",
        resource_type="api_key",
        resource_id=api_key.id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        details={"name": request.name, "scopes": request.scopes},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )

    return APIKeyCreatedResponse(
        api_key=APIKeyResponse(
            id=api_key.id,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            scopes=[s.value for s in api_key.scopes],
            rate_limit=api_key.rate_limit,
            is_active=api_key.is_active,
            expires_at=api_key.expires_at,
            last_used_at=api_key.last_used_at,
            created_at=api_key.created_at,
        ),
        raw_key=raw_key,
    )


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    auth: AuthContext = Depends(require_auth),
    auth_service: AuthService = Depends(get_auth_service),
) -> List[APIKeyResponse]:
    """List all API keys for the current organization"""
    keys = auth_service.list_api_keys(auth.org.id)

    return [
        APIKeyResponse(
            id=key.id,
            name=key.name,
            key_prefix=key.key_prefix,
            scopes=[s.value for s in key.scopes],
            rate_limit=key.rate_limit,
            is_active=key.is_active,
            expires_at=key.expires_at,
            last_used_at=key.last_used_at,
            created_at=key.created_at,
        )
        for key in keys
    ]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    reason: str = "Manually revoked",
    auth: AuthContext = Depends(require_auth),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Revoke an API key"""
    success = auth_service.revoke_api_key(key_id, reason)

    if not success:
        raise HTTPException(status_code=404, detail="API key not found")

    # Audit log
    auth_service.log_action(
        org_id=auth.org.id,
        action="api_key.revoke",
        resource_type="api_key",
        resource_id=key_id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        details={"reason": reason},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )

    return {"message": "API key revoked", "key_id": key_id}


# ==================== Auth Info Endpoints ====================


@router.get("/whoami", response_model=WhoAmIResponse)
async def whoami(
    auth: AuthContext = Depends(require_auth),
) -> WhoAmIResponse:
    """Get information about the current authenticated entity"""
    return WhoAmIResponse(
        org=OrgResponse(
            id=auth.org.id,
            name=auth.org.name,
            slug=auth.org.slug,
            plan=auth.org.plan,
            max_users=auth.org.max_users,
            max_pipelines=auth.org.max_pipelines,
            max_executions_per_day=auth.org.max_executions_per_day,
            created_at=auth.org.created_at,
        ),
        user=UserResponse(
            id=auth.user.id,
            email=auth.user.email,
            name=auth.user.name,
            email_verified=auth.user.email_verified,
            is_active=auth.user.is_active,
            created_at=auth.user.created_at,
            last_login=auth.user.last_login,
        ) if auth.user else None,
        api_key=APIKeyResponse(
            id=auth.api_key.id,
            name=auth.api_key.name,
            key_prefix=auth.api_key.key_prefix,
            scopes=[s.value for s in auth.api_key.scopes],
            rate_limit=auth.api_key.rate_limit,
            is_active=auth.api_key.is_active,
            expires_at=auth.api_key.expires_at,
            last_used_at=auth.api_key.last_used_at,
            created_at=auth.api_key.created_at,
        ) if auth.api_key else None,
        scopes=[s.value for s in auth.api_key.scopes] if auth.api_key else ["full"],
    )


# ==================== Audit Log Endpoints ====================


@router.get("/audit-log", response_model=List[AuditLogEntryResponse])
async def get_audit_log(
    limit: int = 100,
    offset: int = 0,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    auth: AuthContext = Depends(require_auth),
    auth_service: AuthService = Depends(get_auth_service),
) -> List[AuditLogEntryResponse]:
    """Get audit log entries for the current organization"""
    entries = auth_service.get_audit_log(
        org_id=auth.org.id,
        limit=limit,
        offset=offset,
        action=action,
        resource_type=resource_type,
    )

    return [
        AuditLogEntryResponse(
            id=entry.id,
            timestamp=entry.timestamp,
            user_id=entry.user_id,
            api_key_id=entry.api_key_id,
            action=entry.action,
            resource_type=entry.resource_type,
            resource_id=entry.resource_id,
            details=entry.details,
            success=entry.success,
            error_message=entry.error_message,
        )
        for entry in entries
    ]


# ==================== Bootstrap Endpoint ====================


@router.post("/bootstrap")
async def bootstrap(
    org_name: str = "Default Organization",
    org_slug: str = "default",
    user_email: str = "admin@flowmason.local",
    user_name: str = "Admin",
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Bootstrap a new FlowMason instance.

    Creates:
    - An organization
    - An admin user
    - An API key

    This endpoint should be disabled in production after initial setup.
    """
    # Check if already bootstrapped
    existing_org = auth_service.get_org_by_slug(org_slug)
    if existing_org:
        raise HTTPException(
            status_code=400,
            detail="Instance already bootstrapped. Use existing credentials."
        )

    # Create org
    org = auth_service.create_org(org_name, org_slug)

    # Create admin user
    user = auth_service.create_user(user_email, user_name)

    # Add user as owner
    auth_service.add_user_to_org(user.id, org.id, Role.OWNER)

    # Create API key
    api_key, raw_key = auth_service.create_api_key(
        name="Bootstrap Key",
        org_id=org.id,
        user_id=user.id,
        scopes=[APIKeyScope.FULL],
    )

    # Log bootstrap
    auth_service.log_action(
        org_id=org.id,
        action="system.bootstrap",
        resource_type="system",
        user_id=user.id,
        details={
            "org_name": org_name,
            "user_email": user_email,
        },
    )

    return {
        "message": "FlowMason instance bootstrapped successfully",
        "org": {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
        },
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
        "api_key": {
            "id": api_key.id,
            "name": api_key.name,
            "key": raw_key,  # Only shown once!
        },
        "important": "Save the API key! It will not be shown again.",
    }
