"""
FlowMason OAuth 2.0 Support.

Implements OAuth 2.0 authorization flows:
- Authorization Code with PKCE (for web apps)
- Client Credentials (for service-to-service)
- Refresh Token with rotation
"""

import base64
import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional


class OAuthGrantType(str, Enum):
    """Supported OAuth 2.0 grant types."""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"


class OAuthScope(str, Enum):
    """OAuth 2.0 scopes."""
    READ = "read"               # Read access to pipelines, components
    WRITE = "write"             # Create/edit pipelines
    EXECUTE = "execute"         # Run pipelines
    ADMIN = "admin"             # Admin operations
    OPENID = "openid"           # OpenID Connect
    PROFILE = "profile"         # User profile info
    EMAIL = "email"             # User email


# Default scope sets for common use cases
SCOPE_SETS = {
    "basic": {OAuthScope.READ, OAuthScope.EXECUTE},
    "developer": {OAuthScope.READ, OAuthScope.WRITE, OAuthScope.EXECUTE},
    "full": {OAuthScope.READ, OAuthScope.WRITE, OAuthScope.EXECUTE, OAuthScope.ADMIN},
}


@dataclass
class OAuthClient:
    """
    OAuth 2.0 Client (Application).

    Represents an application that can request access tokens.
    """
    id: str                                 # client_id
    secret_hash: Optional[str]              # Hashed client secret (None for public clients)
    name: str                               # Human-readable application name
    description: str

    org_id: str                             # Organization that owns this client
    created_by: str                         # User who created it

    # OAuth configuration
    redirect_uris: List[str]                # Allowed redirect URIs
    grant_types: List[OAuthGrantType]       # Allowed grant types
    scopes: List[OAuthScope]                # Allowed scopes

    # Client type
    is_confidential: bool = True            # False for public clients (SPA, mobile)

    # Metadata
    logo_uri: Optional[str] = None
    homepage_uri: Optional[str] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Status
    is_active: bool = True

    @classmethod
    def create(
        cls,
        name: str,
        org_id: str,
        created_by: str,
        redirect_uris: List[str],
        grant_types: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
        is_confidential: bool = True,
        description: str = "",
    ) -> tuple["OAuthClient", Optional[str]]:
        """
        Create a new OAuth client.

        Returns:
            Tuple of (OAuthClient, raw_secret or None for public clients)
        """
        client_id = f"oa_{secrets.token_urlsafe(24)}"

        raw_secret = None
        secret_hash = None

        if is_confidential:
            raw_secret = secrets.token_urlsafe(32)
            secret_hash = hashlib.sha256(raw_secret.encode()).hexdigest()

        # Parse grant types
        parsed_grants = []
        for gt in (grant_types or ["authorization_code"]):
            try:
                parsed_grants.append(OAuthGrantType(gt))
            except ValueError:
                pass  # Skip invalid grant types

        # Parse scopes
        parsed_scopes = []
        for s in (scopes or ["read", "execute"]):
            try:
                parsed_scopes.append(OAuthScope(s))
            except ValueError:
                pass

        client = cls(
            id=client_id,
            secret_hash=secret_hash,
            name=name,
            description=description,
            org_id=org_id,
            created_by=created_by,
            redirect_uris=redirect_uris,
            grant_types=parsed_grants,
            scopes=parsed_scopes,
            is_confidential=is_confidential,
        )

        return client, raw_secret

    def verify_secret(self, secret: str) -> bool:
        """Verify client secret."""
        if not self.is_confidential or not self.secret_hash:
            return True  # Public clients don't need secret
        expected = hashlib.sha256(secret.encode()).hexdigest()
        return secrets.compare_digest(self.secret_hash, expected)

    def is_redirect_uri_valid(self, uri: str) -> bool:
        """Check if redirect URI is allowed."""
        return uri in self.redirect_uris

    def can_use_grant(self, grant_type: OAuthGrantType) -> bool:
        """Check if grant type is allowed."""
        return grant_type in self.grant_types

    def can_use_scope(self, scope: OAuthScope) -> bool:
        """Check if scope is allowed."""
        return scope in self.scopes


@dataclass
class AuthorizationCode:
    """
    OAuth 2.0 Authorization Code.

    Temporary code exchanged for tokens.
    """
    code: str
    client_id: str
    user_id: str
    org_id: str

    redirect_uri: str
    scopes: List[OAuthScope]

    # PKCE
    code_challenge: Optional[str] = None
    code_challenge_method: str = "S256"     # "plain" or "S256"

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=10))

    # Status
    used: bool = False

    @classmethod
    def create(
        cls,
        client_id: str,
        user_id: str,
        org_id: str,
        redirect_uri: str,
        scopes: List[OAuthScope],
        code_challenge: Optional[str] = None,
        code_challenge_method: str = "S256",
    ) -> "AuthorizationCode":
        """Create a new authorization code."""
        return cls(
            code=secrets.token_urlsafe(32),
            client_id=client_id,
            user_id=user_id,
            org_id=org_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )

    def is_valid(self) -> bool:
        """Check if code is valid and not expired."""
        return not self.used and datetime.utcnow() < self.expires_at

    def verify_pkce(self, code_verifier: str) -> bool:
        """Verify PKCE code verifier."""
        if not self.code_challenge:
            return True  # PKCE not required

        if self.code_challenge_method == "plain":
            return code_verifier == self.code_challenge
        elif self.code_challenge_method == "S256":
            # SHA256 hash then base64url encode
            challenge = hashlib.sha256(code_verifier.encode()).digest()
            encoded = base64.urlsafe_b64encode(challenge).rstrip(b"=").decode()
            return encoded == self.code_challenge

        return False


@dataclass
class OAuthToken:
    """
    OAuth 2.0 Access Token.

    Represents an issued access token.
    """
    # Required fields (no defaults) must come first
    id: str
    access_token: str                       # The actual token
    client_id: str
    org_id: str

    # Optional fields with defaults
    token_type: str = "Bearer"
    user_id: Optional[str] = None           # None for client_credentials
    scopes: List[OAuthScope] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))

    # Status
    revoked: bool = False
    revoked_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        client_id: str,
        org_id: str,
        scopes: List[OAuthScope],
        user_id: Optional[str] = None,
        expires_in: int = 3600,  # seconds
    ) -> "OAuthToken":
        """Create a new access token."""
        return cls(
            id=f"tok_{secrets.token_hex(12)}",
            access_token=secrets.token_urlsafe(48),
            client_id=client_id,
            user_id=user_id,
            org_id=org_id,
            scopes=scopes,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
        )

    def is_valid(self) -> bool:
        """Check if token is valid and not expired."""
        return not self.revoked and datetime.utcnow() < self.expires_at

    @property
    def expires_in(self) -> int:
        """Seconds until expiration."""
        delta = self.expires_at - datetime.utcnow()
        return max(0, int(delta.total_seconds()))


@dataclass
class RefreshToken:
    """
    OAuth 2.0 Refresh Token.

    Used to obtain new access tokens.
    """
    # Required fields (no defaults) must come first
    id: str
    token: str
    client_id: str
    org_id: str

    # Optional fields with defaults
    user_id: Optional[str] = None
    scopes: List[OAuthScope] = field(default_factory=list)

    # Token chain for rotation
    parent_id: Optional[str] = None         # Previous refresh token (for rotation)
    generation: int = 1                     # How many times rotated

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))

    # Status
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    used: bool = False                      # Mark as used after rotation

    @classmethod
    def create(
        cls,
        client_id: str,
        org_id: str,
        scopes: List[OAuthScope],
        user_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        generation: int = 1,
        expires_in_days: int = 30,
    ) -> "RefreshToken":
        """Create a new refresh token."""
        return cls(
            id=f"rtok_{secrets.token_hex(12)}",
            token=secrets.token_urlsafe(64),
            client_id=client_id,
            user_id=user_id,
            org_id=org_id,
            scopes=scopes,
            parent_id=parent_id,
            generation=generation,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
        )

    def is_valid(self) -> bool:
        """Check if token is valid."""
        return not self.revoked and not self.used and datetime.utcnow() < self.expires_at

    def rotate(self) -> "RefreshToken":
        """Create a new refresh token as part of rotation."""
        self.used = True
        return RefreshToken.create(
            client_id=self.client_id,
            org_id=self.org_id,
            scopes=self.scopes,
            user_id=self.user_id,
            parent_id=self.id,
            generation=self.generation + 1,
        )


class OAuthService:
    """
    OAuth 2.0 Service.

    Handles OAuth flows, token management, and client registration.
    """

    def __init__(self):
        # In-memory storage (replace with database in production)
        self._clients: dict[str, OAuthClient] = {}
        self._codes: dict[str, AuthorizationCode] = {}
        self._tokens: dict[str, OAuthToken] = {}
        self._refresh_tokens: dict[str, RefreshToken] = {}

        # Token lookup by access_token value
        self._token_lookup: dict[str, str] = {}  # access_token -> token_id
        self._refresh_lookup: dict[str, str] = {}  # refresh_token -> token_id

    # ==================== Client Management ====================

    def create_client(
        self,
        name: str,
        org_id: str,
        created_by: str,
        redirect_uris: List[str],
        grant_types: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
        is_confidential: bool = True,
        description: str = "",
    ) -> tuple[OAuthClient, Optional[str]]:
        """Create a new OAuth client."""
        client, secret = OAuthClient.create(
            name=name,
            org_id=org_id,
            created_by=created_by,
            redirect_uris=redirect_uris,
            grant_types=grant_types,
            scopes=scopes,
            is_confidential=is_confidential,
            description=description,
        )
        self._clients[client.id] = client
        return client, secret

    def get_client(self, client_id: str) -> Optional[OAuthClient]:
        """Get client by ID."""
        return self._clients.get(client_id)

    def list_clients(self, org_id: str) -> List[OAuthClient]:
        """List all clients for an organization."""
        return [c for c in self._clients.values() if c.org_id == org_id]

    def delete_client(self, client_id: str) -> bool:
        """Delete a client and all its tokens."""
        if client_id not in self._clients:
            return False

        # Revoke all tokens for this client
        for token in list(self._tokens.values()):
            if token.client_id == client_id:
                token.revoked = True

        for refresh in list(self._refresh_tokens.values()):
            if refresh.client_id == client_id:
                refresh.revoked = True

        del self._clients[client_id]
        return True

    def regenerate_client_secret(self, client_id: str) -> Optional[str]:
        """Regenerate client secret."""
        client = self._clients.get(client_id)
        if not client or not client.is_confidential:
            return None

        new_secret = secrets.token_urlsafe(32)
        client.secret_hash = hashlib.sha256(new_secret.encode()).hexdigest()
        client.updated_at = datetime.utcnow()
        return new_secret

    # ==================== Authorization Code Flow ====================

    def create_authorization_code(
        self,
        client_id: str,
        user_id: str,
        org_id: str,
        redirect_uri: str,
        scopes: List[str],
        code_challenge: Optional[str] = None,
        code_challenge_method: str = "S256",
    ) -> Optional[AuthorizationCode]:
        """Create an authorization code for the auth code flow."""
        client = self._clients.get(client_id)
        if not client:
            return None

        if not client.is_redirect_uri_valid(redirect_uri):
            return None

        if not client.can_use_grant(OAuthGrantType.AUTHORIZATION_CODE):
            return None

        # Parse and validate scopes
        parsed_scopes = []
        for s in scopes:
            try:
                scope = OAuthScope(s)
                if client.can_use_scope(scope):
                    parsed_scopes.append(scope)
            except ValueError:
                pass

        code = AuthorizationCode.create(
            client_id=client_id,
            user_id=user_id,
            org_id=org_id,
            redirect_uri=redirect_uri,
            scopes=parsed_scopes,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )

        self._codes[code.code] = code
        return code

    def exchange_code(
        self,
        code: str,
        client_id: str,
        client_secret: Optional[str],
        redirect_uri: str,
        code_verifier: Optional[str] = None,
    ) -> Optional[tuple[OAuthToken, RefreshToken]]:
        """Exchange authorization code for tokens."""
        auth_code = self._codes.get(code)
        if not auth_code or not auth_code.is_valid():
            return None

        if auth_code.client_id != client_id:
            return None

        if auth_code.redirect_uri != redirect_uri:
            return None

        # Verify client
        client = self._clients.get(client_id)
        if not client:
            return None

        if client.is_confidential:
            if not client_secret or not client.verify_secret(client_secret):
                return None

        # Verify PKCE
        if auth_code.code_challenge:
            if not code_verifier or not auth_code.verify_pkce(code_verifier):
                return None

        # Mark code as used
        auth_code.used = True

        # Create tokens
        access_token = OAuthToken.create(
            client_id=client_id,
            org_id=auth_code.org_id,
            scopes=auth_code.scopes,
            user_id=auth_code.user_id,
        )

        refresh_token = RefreshToken.create(
            client_id=client_id,
            org_id=auth_code.org_id,
            scopes=auth_code.scopes,
            user_id=auth_code.user_id,
        )

        # Store tokens
        self._tokens[access_token.id] = access_token
        self._token_lookup[access_token.access_token] = access_token.id

        self._refresh_tokens[refresh_token.id] = refresh_token
        self._refresh_lookup[refresh_token.token] = refresh_token.id

        return access_token, refresh_token

    # ==================== Client Credentials Flow ====================

    def client_credentials_token(
        self,
        client_id: str,
        client_secret: str,
        scopes: List[str],
    ) -> Optional[OAuthToken]:
        """Issue token via client credentials flow."""
        client = self._clients.get(client_id)
        if not client:
            return None

        if not client.is_confidential:
            return None  # Public clients cannot use this flow

        if not client.verify_secret(client_secret):
            return None

        if not client.can_use_grant(OAuthGrantType.CLIENT_CREDENTIALS):
            return None

        # Parse and validate scopes
        parsed_scopes = []
        for s in scopes:
            try:
                scope = OAuthScope(s)
                if client.can_use_scope(scope):
                    parsed_scopes.append(scope)
            except ValueError:
                pass

        # Create access token (no refresh token for client credentials)
        access_token = OAuthToken.create(
            client_id=client_id,
            org_id=client.org_id,
            scopes=parsed_scopes,
            user_id=None,
        )

        self._tokens[access_token.id] = access_token
        self._token_lookup[access_token.access_token] = access_token.id

        return access_token

    # ==================== Refresh Token Flow ====================

    def refresh_tokens(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: Optional[str] = None,
    ) -> Optional[tuple[OAuthToken, RefreshToken]]:
        """Refresh access token using refresh token with rotation."""
        token_id = self._refresh_lookup.get(refresh_token)
        if not token_id:
            return None

        rt = self._refresh_tokens.get(token_id)
        if not rt or not rt.is_valid():
            return None

        if rt.client_id != client_id:
            return None

        # Verify client
        client = self._clients.get(client_id)
        if not client:
            return None

        if client.is_confidential:
            if not client_secret or not client.verify_secret(client_secret):
                return None

        if not client.can_use_grant(OAuthGrantType.REFRESH_TOKEN):
            return None

        # Rotate refresh token
        new_refresh = rt.rotate()

        # Create new access token
        new_access = OAuthToken.create(
            client_id=client_id,
            org_id=rt.org_id,
            scopes=rt.scopes,
            user_id=rt.user_id,
        )

        # Store new tokens
        self._tokens[new_access.id] = new_access
        self._token_lookup[new_access.access_token] = new_access.id

        self._refresh_tokens[new_refresh.id] = new_refresh
        self._refresh_lookup[new_refresh.token] = new_refresh.id

        return new_access, new_refresh

    # ==================== Token Management ====================

    def validate_token(self, access_token: str) -> Optional[OAuthToken]:
        """Validate an access token."""
        token_id = self._token_lookup.get(access_token)
        if not token_id:
            return None

        token = self._tokens.get(token_id)
        if not token or not token.is_valid():
            return None

        return token

    def introspect_token(self, token: str) -> dict:
        """Introspect a token (RFC 7662)."""
        # Try as access token first
        token_id = self._token_lookup.get(token)
        if token_id:
            access_token = self._tokens.get(token_id)
            if access_token and access_token.is_valid():
                return {
                    "active": True,
                    "token_type": access_token.token_type,
                    "scope": " ".join(s.value for s in access_token.scopes),
                    "client_id": access_token.client_id,
                    "sub": access_token.user_id,
                    "exp": int(access_token.expires_at.timestamp()),
                    "iat": int(access_token.created_at.timestamp()),
                }

        # Try as refresh token
        refresh_id = self._refresh_lookup.get(token)
        if refresh_id:
            refresh_token = self._refresh_tokens.get(refresh_id)
            if refresh_token and refresh_token.is_valid():
                return {
                    "active": True,
                    "token_type": "refresh_token",
                    "scope": " ".join(s.value for s in refresh_token.scopes),
                    "client_id": refresh_token.client_id,
                    "sub": refresh_token.user_id,
                    "exp": int(refresh_token.expires_at.timestamp()),
                    "iat": int(refresh_token.created_at.timestamp()),
                }

        return {"active": False}

    def revoke_token(self, token: str) -> bool:
        """Revoke a token (RFC 7009)."""
        # Try as access token
        token_id = self._token_lookup.get(token)
        if token_id:
            access_token = self._tokens.get(token_id)
            if access_token:
                access_token.revoked = True
                access_token.revoked_at = datetime.utcnow()
                return True

        # Try as refresh token
        refresh_id = self._refresh_lookup.get(token)
        if refresh_id:
            refresh_token = self._refresh_tokens.get(refresh_id)
            if refresh_token:
                refresh_token.revoked = True
                refresh_token.revoked_at = datetime.utcnow()
                return True

        return False

    def revoke_all_client_tokens(self, client_id: str) -> int:
        """Revoke all tokens for a client."""
        count = 0
        now = datetime.utcnow()

        for token in self._tokens.values():
            if token.client_id == client_id and not token.revoked:
                token.revoked = True
                token.revoked_at = now
                count += 1

        for refresh in self._refresh_tokens.values():
            if refresh.client_id == client_id and not refresh.revoked:
                refresh.revoked = True
                refresh.revoked_at = now
                count += 1

        return count

    # ==================== Cleanup ====================

    def cleanup_expired(self) -> dict:
        """Remove expired codes and tokens."""
        now = datetime.utcnow()
        removed = {"codes": 0, "tokens": 0, "refresh_tokens": 0}

        # Clean expired authorization codes
        expired_codes = [
            code for code, obj in self._codes.items()
            if obj.expires_at < now or obj.used
        ]
        for code in expired_codes:
            del self._codes[code]
            removed["codes"] += 1

        # Clean expired access tokens
        expired_tokens = [
            tid for tid, token in self._tokens.items()
            if token.expires_at < now
        ]
        for tid in expired_tokens:
            token = self._tokens[tid]
            del self._token_lookup[token.access_token]
            del self._tokens[tid]
            removed["tokens"] += 1

        # Clean expired refresh tokens
        expired_refresh = [
            tid for tid, token in self._refresh_tokens.items()
            if token.expires_at < now
        ]
        for tid in expired_refresh:
            refresh_token = self._refresh_tokens[tid]
            del self._refresh_lookup[refresh_token.token]
            del self._refresh_tokens[tid]
            removed["refresh_tokens"] += 1

        return removed


# Global service instance
_oauth_service: Optional[OAuthService] = None


def get_oauth_service() -> OAuthService:
    """Get the global OAuth service instance."""
    global _oauth_service
    if _oauth_service is None:
        _oauth_service = OAuthService()
    return _oauth_service
