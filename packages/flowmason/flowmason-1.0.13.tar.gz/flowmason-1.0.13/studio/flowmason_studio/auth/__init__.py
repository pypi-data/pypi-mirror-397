"""
FlowMason Authentication Module

Provides API key and SAML authentication for FlowMason Studio.
"""

from .middleware import AuthContext, get_current_user, optional_auth, require_auth, require_scope
from .models import APIKey, APIKeyScope, Organization, Role, User
from .saml import (
    SAMLConfig,
    SAMLConfigService,
    SAMLProvider,
    SAMLService,
    get_saml_config_service,
    get_saml_service,
)
from .service import AuthService, get_auth_service

__all__ = [
    # Models
    "User",
    "Organization",
    "APIKey",
    "APIKeyScope",
    "Role",
    # Auth context
    "AuthContext",
    "get_current_user",
    "require_auth",
    "optional_auth",
    "require_scope",
    # Auth service
    "AuthService",
    "get_auth_service",
    # SAML
    "SAMLConfig",
    "SAMLProvider",
    "SAMLService",
    "SAMLConfigService",
    "get_saml_service",
    "get_saml_config_service",
]
