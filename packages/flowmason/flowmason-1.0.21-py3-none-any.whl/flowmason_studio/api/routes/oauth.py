"""
OAuth 2.0 API Routes.

Implements OAuth 2.0 authorization endpoints:
- Client registration and management
- Authorization endpoint
- Token endpoint
- Token introspection and revocation
"""

import urllib.parse
from typing import List, Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from ...auth.oauth import (
    OAuthClient,
    OAuthGrantType,
    OAuthScope,
    get_oauth_service,
)

router = APIRouter(prefix="/oauth", tags=["oauth"])


# ==================== Request/Response Models ====================

class ClientRegistrationRequest(BaseModel):
    """Request to register an OAuth client."""
    name: str = Field(..., description="Application name")
    description: str = Field("", description="Application description")
    redirect_uris: List[str] = Field(..., description="Allowed redirect URIs")
    grant_types: List[str] = Field(
        default=["authorization_code", "refresh_token"],
        description="Allowed grant types"
    )
    scopes: List[str] = Field(
        default=["read", "execute"],
        description="Allowed scopes"
    )
    is_confidential: bool = Field(
        default=True,
        description="True for server apps, False for SPAs/mobile"
    )


class ClientResponse(BaseModel):
    """OAuth client information."""
    client_id: str
    name: str
    description: str
    redirect_uris: List[str]
    grant_types: List[str]
    scopes: List[str]
    is_confidential: bool
    created_at: str


class ClientWithSecretResponse(ClientResponse):
    """OAuth client with secret (only returned on creation)."""
    client_secret: Optional[str] = Field(
        None,
        description="Client secret (only shown once)"
    )


class TokenResponse(BaseModel):
    """OAuth token response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str


class IntrospectionResponse(BaseModel):
    """Token introspection response."""
    active: bool
    token_type: Optional[str] = None
    scope: Optional[str] = None
    client_id: Optional[str] = None
    sub: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None


class AuthorizeRequest(BaseModel):
    """Authorization request parameters."""
    response_type: str = Field(..., description="Must be 'code'")
    client_id: str
    redirect_uri: str
    scope: str = Field(default="read execute")
    state: Optional[str] = None
    code_challenge: Optional[str] = None
    code_challenge_method: str = Field(default="S256")


def _client_to_response(client: OAuthClient) -> ClientResponse:
    """Convert OAuthClient to response model."""
    return ClientResponse(
        client_id=client.id,
        name=client.name,
        description=client.description,
        redirect_uris=client.redirect_uris,
        grant_types=[g.value for g in client.grant_types],
        scopes=[s.value for s in client.scopes],
        is_confidential=client.is_confidential,
        created_at=client.created_at.isoformat(),
    )


# ==================== Client Management ====================

@router.post("/clients", response_model=ClientWithSecretResponse)
async def register_client(
    request: ClientRegistrationRequest,
    # In production, add auth dependency here
    org_id: str = Query(default="org_default", description="Organization ID"),
    user_id: str = Query(default="user_default", description="User ID"),
):
    """
    Register a new OAuth client.

    The client_secret is only returned once at creation time.
    Store it securely - it cannot be retrieved later.
    """
    service = get_oauth_service()

    client, secret = service.create_client(
        name=request.name,
        org_id=org_id,
        created_by=user_id,
        redirect_uris=request.redirect_uris,
        grant_types=request.grant_types,
        scopes=request.scopes,
        is_confidential=request.is_confidential,
        description=request.description,
    )

    response = ClientWithSecretResponse(
        client_id=client.id,
        name=client.name,
        description=client.description,
        redirect_uris=client.redirect_uris,
        grant_types=[g.value for g in client.grant_types],
        scopes=[s.value for s in client.scopes],
        is_confidential=client.is_confidential,
        created_at=client.created_at.isoformat(),
        client_secret=secret,
    )

    return response


@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(
    org_id: str = Query(default="org_default", description="Organization ID"),
):
    """List all OAuth clients for an organization."""
    service = get_oauth_service()
    clients = service.list_clients(org_id)
    return [_client_to_response(c) for c in clients]


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str):
    """Get OAuth client details."""
    service = get_oauth_service()
    client = service.get_client(client_id)

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return _client_to_response(client)


@router.delete("/clients/{client_id}")
async def delete_client(client_id: str):
    """
    Delete an OAuth client.

    This also revokes all tokens issued to this client.
    """
    service = get_oauth_service()

    if not service.delete_client(client_id):
        raise HTTPException(status_code=404, detail="Client not found")

    return {"message": "Client deleted", "client_id": client_id}


@router.post("/clients/{client_id}/regenerate-secret")
async def regenerate_client_secret(client_id: str):
    """
    Regenerate client secret.

    The old secret is immediately invalidated.
    """
    service = get_oauth_service()
    new_secret = service.regenerate_client_secret(client_id)

    if not new_secret:
        raise HTTPException(
            status_code=400,
            detail="Cannot regenerate secret (client not found or is public)"
        )

    return {
        "message": "Secret regenerated",
        "client_id": client_id,
        "client_secret": new_secret,
    }


# ==================== Authorization Endpoint ====================

@router.get("/authorize")
async def authorize(
    response_type: str = Query(..., description="Must be 'code'"),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(default="read execute"),
    state: Optional[str] = Query(None),
    code_challenge: Optional[str] = Query(None, description="PKCE code challenge"),
    code_challenge_method: str = Query(default="S256"),
    # In production, get user from session
    user_id: str = Query(default="user_default"),
    org_id: str = Query(default="org_default"),
):
    """
    OAuth 2.0 Authorization Endpoint.

    Initiates the authorization code flow. In a real implementation,
    this would show a consent screen. For now, it auto-approves.

    Supports PKCE for public clients.
    """
    if response_type != "code":
        return _error_redirect(
            redirect_uri, state,
            error="unsupported_response_type",
            error_description="Only 'code' response type is supported"
        )

    service = get_oauth_service()
    client = service.get_client(client_id)

    if not client:
        return _error_redirect(
            redirect_uri, state,
            error="invalid_client",
            error_description="Client not found"
        )

    if not client.is_active:
        return _error_redirect(
            redirect_uri, state,
            error="invalid_client",
            error_description="Client is not active"
        )

    if not client.is_redirect_uri_valid(redirect_uri):
        # Don't redirect on invalid redirect_uri
        raise HTTPException(
            status_code=400,
            detail="Invalid redirect_uri"
        )

    # Parse scopes
    scopes = scope.split()

    # Create authorization code
    auth_code = service.create_authorization_code(
        client_id=client_id,
        user_id=user_id,
        org_id=org_id,
        redirect_uri=redirect_uri,
        scopes=scopes,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    if not auth_code:
        return _error_redirect(
            redirect_uri, state,
            error="server_error",
            error_description="Failed to create authorization code"
        )

    # Redirect with code
    params = {"code": auth_code.code}
    if state:
        params["state"] = state

    redirect_url = f"{redirect_uri}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=redirect_url, status_code=302)


def _error_redirect(
    redirect_uri: str,
    state: Optional[str],
    error: str,
    error_description: str,
) -> RedirectResponse:
    """Build OAuth error redirect."""
    params = {
        "error": error,
        "error_description": error_description,
    }
    if state:
        params["state"] = state

    redirect_url = f"{redirect_uri}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=redirect_url, status_code=302)


# ==================== Token Endpoint ====================

@router.post("/token", response_model=TokenResponse)
async def token(
    request: Request,
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    code_verifier: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    scope: str = Form(default="read execute"),
):
    """
    OAuth 2.0 Token Endpoint.

    Supports:
    - authorization_code: Exchange code for tokens
    - client_credentials: Direct token issuance for service accounts
    - refresh_token: Refresh access token
    """
    service = get_oauth_service()

    # Extract client credentials from header if not in form
    if not client_id:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Basic "):
            import base64
            try:
                decoded = base64.b64decode(auth_header[6:]).decode()
                client_id, client_secret = decoded.split(":", 1)
            except Exception:
                pass

    if not client_id:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_request", "error_description": "client_id required"}
        )

    # Handle grant types
    if grant_type == "authorization_code":
        if not code:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_request", "error_description": "code required"}
            )

        if not redirect_uri:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_request", "error_description": "redirect_uri required"}
            )

        result = service.exchange_code(
            code=code,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )

        if not result:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_grant", "error_description": "Invalid or expired code"}
            )

        access_token, refresh_tok = result
        return TokenResponse(
            access_token=access_token.access_token,
            token_type=access_token.token_type,
            expires_in=access_token.expires_in,
            refresh_token=refresh_tok.token,
            scope=" ".join(s.value for s in access_token.scopes),
        )

    elif grant_type == "client_credentials":
        if not client_secret:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_client", "error_description": "client_secret required"}
            )

        scopes = scope.split()
        access_token_result = service.client_credentials_token(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
        )

        if not access_token_result:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_client", "error_description": "Invalid client credentials"}
            )

        return TokenResponse(
            access_token=access_token_result.access_token,
            token_type=access_token_result.token_type,
            expires_in=access_token_result.expires_in,
            scope=" ".join(s.value for s in access_token_result.scopes),
        )

    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_request", "error_description": "refresh_token required"}
            )

        result = service.refresh_tokens(
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
        )

        if not result:
            raise HTTPException(
                status_code=400,
                detail={"error": "invalid_grant", "error_description": "Invalid refresh token"}
            )

        access_token, new_refresh = result
        return TokenResponse(
            access_token=access_token.access_token,
            token_type=access_token.token_type,
            expires_in=access_token.expires_in,
            refresh_token=new_refresh.token,
            scope=" ".join(s.value for s in access_token.scopes),
        )

    else:
        raise HTTPException(
            status_code=400,
            detail={"error": "unsupported_grant_type", "error_description": f"Grant type '{grant_type}' not supported"}
        )


# ==================== Token Introspection (RFC 7662) ====================

@router.post("/introspect", response_model=IntrospectionResponse)
async def introspect(
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None),
    # In production, verify client authentication
):
    """
    Token Introspection Endpoint (RFC 7662).

    Allows resource servers to query the authorization server
    about the state of a token.
    """
    service = get_oauth_service()
    result = service.introspect_token(token)
    return IntrospectionResponse(**result)


# ==================== Token Revocation (RFC 7009) ====================

@router.post("/revoke")
async def revoke(
    token: str = Form(...),
    token_type_hint: Optional[str] = Form(None),
    # In production, verify client authentication
):
    """
    Token Revocation Endpoint (RFC 7009).

    Revokes an access token or refresh token.
    """
    service = get_oauth_service()
    service.revoke_token(token)

    # Always return 200 per RFC 7009
    return {"message": "Token revoked"}


# ==================== Well-Known Configuration ====================

@router.get("/.well-known/oauth-authorization-server")
async def oauth_metadata(request: Request):
    """
    OAuth 2.0 Authorization Server Metadata (RFC 8414).

    Returns server configuration for discovery.
    """
    base_url = str(request.base_url).rstrip("/")

    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/api/v1/oauth/authorize",
        "token_endpoint": f"{base_url}/api/v1/oauth/token",
        "introspection_endpoint": f"{base_url}/api/v1/oauth/introspect",
        "revocation_endpoint": f"{base_url}/api/v1/oauth/revoke",
        "registration_endpoint": f"{base_url}/api/v1/oauth/clients",
        "scopes_supported": [s.value for s in OAuthScope],
        "response_types_supported": ["code"],
        "grant_types_supported": [g.value for g in OAuthGrantType],
        "token_endpoint_auth_methods_supported": [
            "client_secret_basic",
            "client_secret_post",
            "none",  # For public clients
        ],
        "code_challenge_methods_supported": ["plain", "S256"],
        "service_documentation": f"{base_url}/docs",
    }
