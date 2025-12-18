"""
JWT Token API Routes.

Endpoints for JWT token management:
- Token issuance
- Token refresh
- Token introspection
- Token revocation
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Form, Header, HTTPException, Query
from pydantic import BaseModel, Field

from ...auth.jwt import (
    JWTAlgorithm,
    JWTConfig,
    configure_jwt_service,
    get_jwt_service,
)

router = APIRouter(prefix="/tokens", tags=["tokens"])


# ==================== Request/Response Models ====================

class TokenRequest(BaseModel):
    """Request to create a token."""
    subject: str = Field(..., description="User or client ID")
    org_id: Optional[str] = Field(None, description="Organization ID")
    scopes: List[str] = Field(default=["read", "execute"], description="Token scopes")
    name: Optional[str] = Field(None, description="User display name")
    email: Optional[str] = Field(None, description="User email")
    custom_claims: Optional[Dict[str, Any]] = Field(None, description="Additional claims")
    expires_in: Optional[int] = Field(None, description="Custom expiration in seconds")


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_expires_in: int
    scope: str


class SingleTokenResponse(BaseModel):
    """Single token response."""
    token: str
    token_type: str = "Bearer"
    expires_in: int


class IntrospectionResponse(BaseModel):
    """Token introspection response."""
    active: bool
    sub: Optional[str] = None
    iss: Optional[str] = None
    aud: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    jti: Optional[str] = None
    token_type: Optional[str] = None
    org_id: Optional[str] = None
    scope: Optional[str] = None


class ConfigResponse(BaseModel):
    """JWT configuration response."""
    issuer: str
    audience: str
    algorithm: str
    access_token_expires_seconds: int
    refresh_token_expires_seconds: int


class ConfigRequest(BaseModel):
    """Request to update JWT configuration."""
    issuer: Optional[str] = None
    audience: Optional[str] = None
    algorithm: Optional[str] = None
    secret_key: Optional[str] = Field(None, description="New signing key (sensitive)")
    access_token_expires_seconds: Optional[int] = None
    refresh_token_expires_seconds: Optional[int] = None


# ==================== Token Endpoints ====================

@router.post("/issue", response_model=TokenResponse)
async def issue_tokens(request: TokenRequest):
    """
    Issue a new access/refresh token pair.

    Creates both an access token (short-lived) and refresh token (long-lived).
    """
    service = get_jwt_service()

    token_pair = service.create_token_pair(
        subject=request.subject,
        org_id=request.org_id,
        scopes=request.scopes,
        name=request.name,
        email=request.email,
        custom_claims=request.custom_claims,
    )

    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
        refresh_expires_in=token_pair.refresh_expires_in,
        scope=token_pair.scope,
    )


@router.post("/access", response_model=SingleTokenResponse)
async def create_access_token(request: TokenRequest):
    """
    Create a single access token.

    Use this when you only need an access token without refresh capability.
    """
    service = get_jwt_service()

    token = service.create_access_token(
        subject=request.subject,
        org_id=request.org_id,
        scopes=request.scopes,
        name=request.name,
        email=request.email,
        custom_claims=request.custom_claims,
        expires_in=request.expires_in,
    )

    return SingleTokenResponse(
        token=token,
        expires_in=request.expires_in or service.config.access_token_expires_seconds,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    refresh_token: str = Form(..., description="The refresh token"),
):
    """
    Refresh tokens using a refresh token.

    Returns a new access/refresh token pair. The old refresh token is invalidated
    (token rotation for security).
    """
    service = get_jwt_service()

    token_pair = service.refresh_tokens(refresh_token)

    if not token_pair:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )

    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
        refresh_expires_in=token_pair.refresh_expires_in,
        scope=token_pair.scope,
    )


@router.post("/introspect", response_model=IntrospectionResponse)
async def introspect_token(
    token: str = Form(..., description="The token to introspect"),
):
    """
    Introspect a token.

    Returns token metadata and validity status.
    """
    service = get_jwt_service()
    result = service.introspect(token)
    return IntrospectionResponse(**result)


@router.post("/revoke")
async def revoke_token(
    token: str = Form(..., description="The token to revoke"),
):
    """
    Revoke a token.

    The token's JTI is added to a blacklist and the token becomes invalid.
    """
    service = get_jwt_service()
    success = service.revoke_token(token)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid token format"
        )

    return {"message": "Token revoked"}


@router.post("/revoke/{jti}")
async def revoke_by_jti(jti: str):
    """
    Revoke a token by its JTI (JWT ID).

    Use this when you have the JTI but not the full token.
    """
    service = get_jwt_service()
    service.revoke_by_jti(jti)
    return {"message": f"Token {jti} revoked"}


@router.get("/verify")
async def verify_token(
    authorization: str = Header(..., description="Bearer token"),
):
    """
    Verify a token from the Authorization header.

    Returns token claims if valid.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )

    token = authorization[7:]
    service = get_jwt_service()
    claims = service.get_token_claims(token)

    if not claims:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return {
        "valid": True,
        "claims": claims,
    }


# ==================== Configuration Endpoints ====================

@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """
    Get current JWT configuration.

    Note: The secret key is not returned for security.
    """
    service = get_jwt_service()

    return ConfigResponse(
        issuer=service.config.issuer,
        audience=service.config.audience,
        algorithm=service.config.algorithm.value,
        access_token_expires_seconds=service.config.access_token_expires_seconds,
        refresh_token_expires_seconds=service.config.refresh_token_expires_seconds,
    )


@router.patch("/config", response_model=ConfigResponse)
async def update_config(request: ConfigRequest):
    """
    Update JWT configuration.

    Changes take effect for new tokens. Existing tokens remain valid
    until they expire (unless you update the secret key).

    **Warning:** Changing the secret key invalidates ALL existing tokens.
    """
    current = get_jwt_service().config

    new_config = JWTConfig(
        issuer=request.issuer or current.issuer,
        audience=request.audience or current.audience,
        algorithm=JWTAlgorithm(request.algorithm) if request.algorithm else current.algorithm,
        secret_key=request.secret_key or current.secret_key,
        access_token_expires_seconds=request.access_token_expires_seconds or current.access_token_expires_seconds,
        refresh_token_expires_seconds=request.refresh_token_expires_seconds or current.refresh_token_expires_seconds,
    )

    service = configure_jwt_service(new_config)

    return ConfigResponse(
        issuer=service.config.issuer,
        audience=service.config.audience,
        algorithm=service.config.algorithm.value,
        access_token_expires_seconds=service.config.access_token_expires_seconds,
        refresh_token_expires_seconds=service.config.refresh_token_expires_seconds,
    )


@router.post("/config/rotate-key")
async def rotate_signing_key():
    """
    Rotate the signing key.

    Generates a new random signing key. All existing tokens become invalid.
    Use with caution.
    """
    current = get_jwt_service().config

    # Create new config with fresh key
    new_config = JWTConfig(
        issuer=current.issuer,
        audience=current.audience,
        algorithm=current.algorithm,
        secret_key=None,  # Will generate new key
        access_token_expires_seconds=current.access_token_expires_seconds,
        refresh_token_expires_seconds=current.refresh_token_expires_seconds,
    )

    configure_jwt_service(new_config)

    return {
        "message": "Signing key rotated",
        "warning": "All existing tokens are now invalid",
    }


# ==================== Utility Endpoints ====================

@router.get("/decode")
async def decode_token_unsafe(
    token: str = Query(..., description="JWT token to decode"),
):
    """
    Decode a token without verification.

    **Warning:** This does not verify the signature. Use for debugging only.
    """
    service = get_jwt_service()
    payload = service.decode_token(token, verify=False)

    if not payload:
        raise HTTPException(
            status_code=400,
            detail="Invalid token format"
        )

    return {
        "payload": payload.to_dict(),
        "warning": "Signature not verified",
    }


@router.get("/stats")
async def get_stats():
    """
    Get token service statistics.
    """
    service = get_jwt_service()

    return {
        "revoked_token_count": len(service._revoked_tokens),
        "config": {
            "issuer": service.config.issuer,
            "algorithm": service.config.algorithm.value,
        }
    }
