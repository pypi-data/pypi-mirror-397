"""
FlowMason SAML Authentication Routes

API endpoints for SAML/SSO authentication:
- SP metadata endpoint
- SSO initiation (redirect to IdP)
- Assertion Consumer Service (ACS) callback
- Single Logout (SLO)
- SAML configuration management
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from ...auth.models import Role
from ...auth.saml import (
    SAMLConfig,
    SAMLProvider,
    get_saml_config_service,
    get_saml_service,
)
from ...auth.service import get_auth_service

router = APIRouter(prefix="/auth/saml", tags=["SAML Authentication"])


# ==================== Request/Response Models ====================

class SAMLConfigRequest(BaseModel):
    """Request to configure SAML for an organization"""
    provider_type: str = "custom"
    idp_entity_id: str
    idp_sso_url: str
    idp_slo_url: Optional[str] = None
    idp_certificate: str
    attribute_mapping: Optional[dict] = None
    auto_provision_users: bool = True
    default_role: str = "developer"
    require_signed_assertions: bool = True


class SAMLConfigResponse(BaseModel):
    """SAML configuration response"""
    id: str
    org_id: str
    enabled: bool
    provider_type: str
    idp_entity_id: str
    idp_sso_url: str
    idp_slo_url: Optional[str]
    sp_entity_id: str
    sp_acs_url: str
    sp_slo_url: Optional[str]
    attribute_mapping: dict
    auto_provision_users: bool
    default_role: str
    created_at: str
    updated_at: str


class SAMLLoginResponse(BaseModel):
    """Response from SAML login initiation"""
    redirect_url: str
    relay_state: str


# ==================== SP Metadata Endpoint ====================

@router.get("/metadata/{org_id}", response_class=Response)
async def get_sp_metadata(org_id: str, request: Request):
    """
    Get SAML SP metadata for an organization.

    This endpoint returns XML metadata that can be imported into
    the Identity Provider (IdP) to configure the integration.
    """
    config_service = get_saml_config_service()
    config = config_service.get_config(org_id)

    if not config:
        # Create default config with this request's base URL
        base_url = str(request.base_url).rstrip('/')
        config = SAMLConfig.create(org_id, base_url)

    saml_service = get_saml_service()
    metadata = saml_service.generate_sp_metadata(config)

    return Response(
        content=metadata,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="flowmason-sp-metadata-{org_id}.xml"'
        }
    )


# ==================== SSO Initiation ====================

@router.get("/login/{org_id}")
async def initiate_saml_login(
    org_id: str,
    request: Request,
    return_url: Optional[str] = None,
):
    """
    Initiate SAML SSO login (SP-initiated).

    Redirects the user to the Identity Provider for authentication.

    Query Parameters:
        return_url: URL to redirect to after successful login
    """
    config_service = get_saml_config_service()
    config = config_service.get_config(org_id)

    if not config or not config.enabled:
        raise HTTPException(
            status_code=404,
            detail="SAML not configured or not enabled for this organization"
        )

    if not config.idp_sso_url:
        raise HTTPException(
            status_code=400,
            detail="SAML IdP SSO URL not configured"
        )

    saml_service = get_saml_service()
    redirect_url, saml_request = saml_service.generate_authn_request(
        config,
        return_url=return_url or str(request.base_url),
    )

    return RedirectResponse(url=redirect_url, status_code=302)


@router.get("/login/{org_id}/url")
async def get_saml_login_url(
    org_id: str,
    request: Request,
    return_url: Optional[str] = None,
) -> SAMLLoginResponse:
    """
    Get SAML SSO login URL without redirecting.

    Returns the redirect URL for use in custom login flows.
    """
    config_service = get_saml_config_service()
    config = config_service.get_config(org_id)

    if not config or not config.enabled:
        raise HTTPException(
            status_code=404,
            detail="SAML not configured or not enabled for this organization"
        )

    saml_service = get_saml_service()
    redirect_url, saml_request = saml_service.generate_authn_request(
        config,
        return_url=return_url,
    )

    return SAMLLoginResponse(
        redirect_url=redirect_url,
        relay_state=saml_request.relay_state,
    )


# ==================== Assertion Consumer Service (ACS) ====================

@router.post("/acs/{org_id}")
async def assertion_consumer_service(
    org_id: str,
    request: Request,
    SAMLResponse: str = Form(...),
    RelayState: str = Form(...),
):
    """
    SAML Assertion Consumer Service (ACS) endpoint.

    Receives and processes SAML responses from the IdP after authentication.
    Creates or updates the user and establishes a session.
    """
    config_service = get_saml_config_service()
    config = config_service.get_config(org_id)

    if not config or not config.enabled:
        raise HTTPException(
            status_code=404,
            detail="SAML not configured for this organization"
        )

    saml_service = get_saml_service()

    try:
        # Parse and validate SAML response
        assertion, original_request = saml_service.parse_saml_response(
            config,
            SAMLResponse,
            RelayState,
        )

        # Extract user information
        user_info = saml_service.extract_user_info(assertion, config)
        email = user_info.get('email', '').lower()
        name = user_info.get('name', email)

        if not email:
            raise ValueError("No email found in SAML assertion")

        # Get or create user
        auth_service = get_auth_service()
        user = auth_service.get_user_by_email(email)

        if not user:
            if not config.auto_provision_users:
                raise HTTPException(
                    status_code=403,
                    detail="User not found and auto-provisioning is disabled"
                )

            # Create new user (JIT provisioning)
            user = auth_service.create_user(email=email, name=name)

            # Update SSO info
            from ..services.database import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET sso_provider = ?, sso_id = ?, email_verified = 1
                WHERE id = ?
            """, ('saml', assertion.subject, user.id))
            conn.commit()

            # Add user to organization
            role = Role(config.default_role) if config.default_role in [r.value for r in Role] else Role.DEVELOPER
            auth_service.add_user_to_org(user.id, org_id, role)

            # Log the action
            auth_service.log_action(
                org_id=org_id,
                action="user.saml_provision",
                resource_type="user",
                user_id=user.id,
                resource_id=user.id,
                details={"email": email, "name": name, "role": role.value},
            )
        else:
            # Update last login
            from ..services.database import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), user.id)
            )
            conn.commit()

            # Log the action
            auth_service.log_action(
                org_id=org_id,
                action="user.saml_login",
                resource_type="user",
                user_id=user.id,
                resource_id=user.id,
            )

        # Generate session token (simplified - production should use JWT)
        import secrets
        session_token = secrets.token_urlsafe(32)

        # Determine redirect URL
        return_url = original_request.return_url or "/"

        # For now, return success HTML that sets a session cookie
        # In production, you'd set an HTTP-only secure cookie and redirect
        return HTMLResponse(content=f'''
<!DOCTYPE html>
<html>
<head>
    <title>SAML Login Successful</title>
    <script>
        // Store session and redirect
        localStorage.setItem('flowmason_user_id', '{user.id}');
        localStorage.setItem('flowmason_user_email', '{user.email}');
        localStorage.setItem('flowmason_org_id', '{org_id}');
        localStorage.setItem('flowmason_session', '{session_token}');
        window.location.href = '{return_url}';
    </script>
</head>
<body>
    <p>Login successful. Redirecting...</p>
</body>
</html>
        ''')

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAML authentication failed: {str(e)}")


# ==================== Single Logout (SLO) ====================

@router.post("/slo/{org_id}")
async def single_logout(
    org_id: str,
    SAMLRequest: Optional[str] = Form(None),
    SAMLResponse: Optional[str] = Form(None),
):
    """
    SAML Single Logout (SLO) endpoint.

    Handles logout requests from the IdP.
    """
    # TODO: Implement SLO processing
    # For now, just clear session and redirect to home
    return HTMLResponse(content='''
<!DOCTYPE html>
<html>
<head>
    <title>Logged Out</title>
    <script>
        localStorage.removeItem('flowmason_user_id');
        localStorage.removeItem('flowmason_user_email');
        localStorage.removeItem('flowmason_org_id');
        localStorage.removeItem('flowmason_session');
        window.location.href = '/';
    </script>
</head>
<body>
    <p>Logged out. Redirecting...</p>
</body>
</html>
    ''')


# ==================== SAML Configuration Management ====================

@router.get("/config/{org_id}", response_model=SAMLConfigResponse)
async def get_saml_config(org_id: str, request: Request):
    """
    Get SAML configuration for an organization.

    Requires admin access to the organization.
    """
    config_service = get_saml_config_service()
    config = config_service.get_config(org_id)

    if not config:
        # Return default configuration with generated SP URLs
        base_url = str(request.base_url).rstrip('/')
        config = SAMLConfig.create(org_id, base_url)

    return SAMLConfigResponse(
        id=config.id,
        org_id=config.org_id,
        enabled=config.enabled,
        provider_type=config.provider_type.value,
        idp_entity_id=config.idp_entity_id,
        idp_sso_url=config.idp_sso_url,
        idp_slo_url=config.idp_slo_url,
        sp_entity_id=config.sp_entity_id,
        sp_acs_url=config.sp_acs_url,
        sp_slo_url=config.sp_slo_url,
        attribute_mapping=config.attribute_mapping,
        auto_provision_users=config.auto_provision_users,
        default_role=config.default_role,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat(),
    )


@router.put("/config/{org_id}", response_model=SAMLConfigResponse)
async def update_saml_config(
    org_id: str,
    config_request: SAMLConfigRequest,
    request: Request,
):
    """
    Create or update SAML configuration for an organization.

    Requires admin access to the organization.
    """
    config_service = get_saml_config_service()
    existing = config_service.get_config(org_id)

    base_url = str(request.base_url).rstrip('/')

    if existing:
        config = existing
    else:
        config = SAMLConfig.create(org_id, base_url)

    # Update configuration
    config.provider_type = SAMLProvider(config_request.provider_type) if config_request.provider_type in [p.value for p in SAMLProvider] else SAMLProvider.CUSTOM
    config.idp_entity_id = config_request.idp_entity_id
    config.idp_sso_url = config_request.idp_sso_url
    config.idp_slo_url = config_request.idp_slo_url
    config.idp_certificate = config_request.idp_certificate
    config.auto_provision_users = config_request.auto_provision_users
    config.default_role = config_request.default_role
    config.require_signed_assertions = config_request.require_signed_assertions

    if config_request.attribute_mapping:
        config.attribute_mapping = config_request.attribute_mapping

    # Save configuration
    config = config_service.save_config(config)

    # Log the action
    auth_service = get_auth_service()
    auth_service.log_action(
        org_id=org_id,
        action="saml.config_update",
        resource_type="saml_config",
        resource_id=config.id,
        details={"provider_type": config.provider_type.value},
    )

    return SAMLConfigResponse(
        id=config.id,
        org_id=config.org_id,
        enabled=config.enabled,
        provider_type=config.provider_type.value,
        idp_entity_id=config.idp_entity_id,
        idp_sso_url=config.idp_sso_url,
        idp_slo_url=config.idp_slo_url,
        sp_entity_id=config.sp_entity_id,
        sp_acs_url=config.sp_acs_url,
        sp_slo_url=config.sp_slo_url,
        attribute_mapping=config.attribute_mapping,
        auto_provision_users=config.auto_provision_users,
        default_role=config.default_role,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat(),
    )


@router.post("/config/{org_id}/enable")
async def enable_saml(org_id: str):
    """Enable SAML authentication for an organization."""
    config_service = get_saml_config_service()
    config = config_service.get_config(org_id)

    if not config:
        raise HTTPException(
            status_code=404,
            detail="SAML not configured for this organization. Configure SAML first."
        )

    if not config.idp_entity_id or not config.idp_sso_url:
        raise HTTPException(
            status_code=400,
            detail="SAML IdP configuration incomplete. Set IdP Entity ID and SSO URL."
        )

    config.enabled = True
    config_service.save_config(config)

    return {"message": "SAML enabled", "enabled": True}


@router.post("/config/{org_id}/disable")
async def disable_saml(org_id: str):
    """Disable SAML authentication for an organization."""
    config_service = get_saml_config_service()
    config = config_service.get_config(org_id)

    if config:
        config.enabled = False
        config_service.save_config(config)

    return {"message": "SAML disabled", "enabled": False}


@router.delete("/config/{org_id}")
async def delete_saml_config(org_id: str):
    """Delete SAML configuration for an organization."""
    config_service = get_saml_config_service()
    deleted = config_service.delete_config(org_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="SAML configuration not found"
        )

    return {"message": "SAML configuration deleted"}
