"""
FlowMason Secrets API Routes

Endpoints for managing encrypted secrets.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...auth import AuthContext, get_auth_service, require_auth, require_scope
from ...auth.models import APIKeyScope
from ...services.secrets import get_secrets_service

router = APIRouter(prefix="/secrets", tags=["secrets"])


# ==================== Request/Response Models ====================


class CreateSecretRequest(BaseModel):
    """Request to create or update a secret."""
    name: str = Field(description="Secret name (e.g., 'OPENAI_API_KEY')")
    value: str = Field(description="Secret value")
    description: str = Field(default="", description="Description of the secret")
    category: str = Field(
        default="other",
        description="Category: 'api_key', 'token', 'credential', 'other'"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Optional expiration date"
    )


class SecretResponse(BaseModel):
    """Secret metadata response (no value)."""
    id: str
    name: str
    description: str
    category: str
    created_at: str
    updated_at: str
    created_by: Optional[str] = None
    expires_at: Optional[str] = None
    is_expired: bool = False


class SecretValueResponse(BaseModel):
    """Secret with value (only for specific retrieval)."""
    name: str
    value: str
    category: str
    is_expired: bool = False


# ==================== Endpoints ====================


@router.get("", response_model=List[SecretResponse])
async def list_secrets(
    auth: AuthContext = Depends(require_auth),
) -> List[SecretResponse]:
    """
    List all secrets for the organization (metadata only, no values).
    """
    secrets_service = get_secrets_service(auth.org.id)
    secrets = secrets_service.list()

    return [
        SecretResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            category=s.category,
            created_at=s.created_at,
            updated_at=s.updated_at,
            created_by=s.created_by,
            expires_at=s.expires_at,
            is_expired=s.is_expired,
        )
        for s in secrets
    ]


@router.post("", response_model=SecretResponse)
async def create_secret(
    request: CreateSecretRequest,
    auth: AuthContext = Depends(require_scope(APIKeyScope.FULL)),
) -> SecretResponse:
    """
    Create or update a secret.

    Requires full API key scope.
    """
    secrets_service = get_secrets_service(auth.org.id)

    metadata = secrets_service.set(
        name=request.name,
        value=request.value,
        description=request.description,
        category=request.category,
        expires_at=request.expires_at,
        created_by=auth.user.id if auth.user else None,
    )

    # Audit log
    auth_service = get_auth_service()
    auth_service.log_action(
        org_id=auth.org.id,
        action="secret.create",
        resource_type="secret",
        resource_id=metadata.id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        user_id=auth.user.id if auth.user else None,
        details={"name": request.name, "category": request.category},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )

    return SecretResponse(
        id=metadata.id,
        name=metadata.name,
        description=metadata.description,
        category=metadata.category,
        created_at=metadata.created_at,
        updated_at=metadata.updated_at,
        created_by=metadata.created_by,
        expires_at=metadata.expires_at,
        is_expired=metadata.is_expired,
    )


@router.get("/{secret_name}", response_model=SecretValueResponse)
async def get_secret(
    secret_name: str,
    auth: AuthContext = Depends(require_scope(APIKeyScope.FULL)),
) -> SecretValueResponse:
    """
    Get a secret value.

    Requires full API key scope. Access is audit logged.
    """
    secrets_service = get_secrets_service(auth.org.id)

    metadata = secrets_service.get_metadata(secret_name)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Secret '{secret_name}' not found")

    value = secrets_service.get(secret_name)
    if value is None:
        if metadata.is_expired:
            raise HTTPException(status_code=410, detail=f"Secret '{secret_name}' has expired")
        raise HTTPException(status_code=500, detail="Failed to decrypt secret")

    # Audit log (accessing secret value is logged)
    auth_service = get_auth_service()
    auth_service.log_action(
        org_id=auth.org.id,
        action="secret.read",
        resource_type="secret",
        resource_id=metadata.id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        user_id=auth.user.id if auth.user else None,
        details={"name": secret_name},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )

    return SecretValueResponse(
        name=secret_name,
        value=value,
        category=metadata.category,
        is_expired=metadata.is_expired,
    )


@router.delete("/{secret_name}")
async def delete_secret(
    secret_name: str,
    auth: AuthContext = Depends(require_scope(APIKeyScope.FULL)),
) -> dict:
    """
    Delete a secret.

    Requires full API key scope.
    """
    secrets_service = get_secrets_service(auth.org.id)

    # Get metadata before deletion for audit
    metadata = secrets_service.get_metadata(secret_name)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Secret '{secret_name}' not found")

    success = secrets_service.delete(secret_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Secret '{secret_name}' not found")

    # Audit log
    auth_service = get_auth_service()
    auth_service.log_action(
        org_id=auth.org.id,
        action="secret.delete",
        resource_type="secret",
        resource_id=metadata.id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        user_id=auth.user.id if auth.user else None,
        details={"name": secret_name},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )

    return {"message": f"Secret '{secret_name}' deleted"}


@router.get("/{secret_name}/metadata", response_model=SecretResponse)
async def get_secret_metadata(
    secret_name: str,
    auth: AuthContext = Depends(require_auth),
) -> SecretResponse:
    """
    Get secret metadata without the value.
    """
    secrets_service = get_secrets_service(auth.org.id)

    metadata = secrets_service.get_metadata(secret_name)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Secret '{secret_name}' not found")

    return SecretResponse(
        id=metadata.id,
        name=metadata.name,
        description=metadata.description,
        category=metadata.category,
        created_at=metadata.created_at,
        updated_at=metadata.updated_at,
        created_by=metadata.created_by,
        expires_at=metadata.expires_at,
        is_expired=metadata.is_expired,
    )
