"""
FlowMason Standalone JWT Token Service.

Provides JWT token issuing and verification without external dependencies.
Supports configurable signing algorithms (HS256, RS256) and custom claims.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class JWTAlgorithm(str, Enum):
    """Supported JWT signing algorithms."""
    HS256 = "HS256"  # HMAC with SHA-256 (symmetric)
    HS384 = "HS384"  # HMAC with SHA-384 (symmetric)
    HS512 = "HS512"  # HMAC with SHA-512 (symmetric)
    # RS256 would require cryptography library for RSA


@dataclass
class JWTConfig:
    """JWT service configuration."""
    issuer: str = "flowmason"
    audience: str = "flowmason-api"
    algorithm: JWTAlgorithm = JWTAlgorithm.HS256
    secret_key: Optional[str] = None  # For HS* algorithms
    access_token_expires_seconds: int = 3600  # 1 hour
    refresh_token_expires_seconds: int = 86400 * 30  # 30 days

    def __post_init__(self):
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(64)


@dataclass
class TokenPayload:
    """JWT token payload."""
    sub: str                            # Subject (user_id or client_id)
    iss: str                            # Issuer
    aud: str                            # Audience
    exp: int                            # Expiration timestamp
    iat: int                            # Issued at timestamp
    jti: str                            # JWT ID (unique identifier)

    # Custom claims
    org_id: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    token_type: str = "access"          # "access" or "refresh"

    # Optional claims
    name: Optional[str] = None
    email: Optional[str] = None

    # Additional custom claims
    custom: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for encoding."""
        result = {
            "sub": self.sub,
            "iss": self.iss,
            "aud": self.aud,
            "exp": self.exp,
            "iat": self.iat,
            "jti": self.jti,
            "token_type": self.token_type,
        }

        if self.org_id:
            result["org_id"] = self.org_id
        if self.scopes:
            result["scopes"] = self.scopes
        if self.name:
            result["name"] = self.name
        if self.email:
            result["email"] = self.email
        if self.custom:
            result.update(self.custom)

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenPayload":
        """Create from dictionary."""
        known_keys = {"sub", "iss", "aud", "exp", "iat", "jti", "org_id",
                      "scopes", "token_type", "name", "email"}
        custom = {k: v for k, v in data.items() if k not in known_keys}

        return cls(
            sub=data.get("sub", ""),
            iss=data.get("iss", ""),
            aud=data.get("aud", ""),
            exp=data.get("exp", 0),
            iat=data.get("iat", 0),
            jti=data.get("jti", ""),
            org_id=data.get("org_id"),
            scopes=data.get("scopes", []),
            token_type=data.get("token_type", "access"),
            name=data.get("name"),
            email=data.get("email"),
            custom=custom,
        )


@dataclass
class TokenPair:
    """Access and refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_expires_in: int = 2592000
    scope: str = ""


class JWTService:
    """
    JWT Token Service.

    Handles JWT creation, verification, and revocation.
    """

    def __init__(self, config: Optional[JWTConfig] = None):
        self.config = config or JWTConfig()
        self._revoked_tokens: Set[str] = set()  # JTI blacklist
        self._refresh_tokens: Dict[str, str] = {}  # jti -> parent_jti for rotation

    # ==================== Token Encoding/Decoding ====================

    def _base64url_encode(self, data: bytes) -> str:
        """Base64url encode without padding."""
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    def _base64url_decode(self, data: str) -> bytes:
        """Base64url decode with padding restoration."""
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    def _sign(self, message: str, algorithm: JWTAlgorithm) -> str:
        """Sign a message using the configured algorithm."""
        # secret_key is guaranteed to be set after __post_init__
        assert self.config.secret_key is not None
        key = self.config.secret_key.encode()

        if algorithm == JWTAlgorithm.HS256:
            signature = hmac.new(key, message.encode(), hashlib.sha256).digest()
        elif algorithm == JWTAlgorithm.HS384:
            signature = hmac.new(key, message.encode(), hashlib.sha384).digest()
        elif algorithm == JWTAlgorithm.HS512:
            signature = hmac.new(key, message.encode(), hashlib.sha512).digest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        return self._base64url_encode(signature)

    def _verify_signature(self, message: str, signature: str, algorithm: JWTAlgorithm) -> bool:
        """Verify a signature."""
        expected = self._sign(message, algorithm)
        return hmac.compare_digest(expected, signature)

    def encode_token(self, payload: TokenPayload) -> str:
        """Encode a JWT token."""
        # Header
        header = {
            "alg": self.config.algorithm.value,
            "typ": "JWT"
        }
        header_b64 = self._base64url_encode(json.dumps(header).encode())

        # Payload
        payload_b64 = self._base64url_encode(json.dumps(payload.to_dict()).encode())

        # Signature
        message = f"{header_b64}.{payload_b64}"
        signature = self._sign(message, self.config.algorithm)

        return f"{header_b64}.{payload_b64}.{signature}"

    def decode_token(self, token: str, verify: bool = True) -> Optional[TokenPayload]:
        """
        Decode and optionally verify a JWT token.

        Returns None if token is invalid.
        """
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature = parts

            # Decode header
            header = json.loads(self._base64url_decode(header_b64))

            if verify:
                # Verify algorithm matches
                alg = header.get("alg")
                if alg != self.config.algorithm.value:
                    return None

                # Verify signature
                message = f"{header_b64}.{payload_b64}"
                if not self._verify_signature(message, signature, self.config.algorithm):
                    return None

            # Decode payload
            payload_data = json.loads(self._base64url_decode(payload_b64))
            payload = TokenPayload.from_dict(payload_data)

            if verify:
                # Verify expiration
                if payload.exp < int(time.time()):
                    return None

                # Verify issuer
                if payload.iss != self.config.issuer:
                    return None

                # Check revocation
                if payload.jti in self._revoked_tokens:
                    return None

            return payload

        except Exception:
            return None

    # ==================== Token Creation ====================

    def create_access_token(
        self,
        subject: str,
        org_id: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
        expires_in: Optional[int] = None,
    ) -> str:
        """Create an access token."""
        now = int(time.time())
        exp = now + (expires_in or self.config.access_token_expires_seconds)

        payload = TokenPayload(
            sub=subject,
            iss=self.config.issuer,
            aud=self.config.audience,
            exp=exp,
            iat=now,
            jti=f"jti_{secrets.token_hex(16)}",
            org_id=org_id,
            scopes=scopes or [],
            token_type="access",
            name=name,
            email=email,
            custom=custom_claims or {},
        )

        return self.encode_token(payload)

    def create_refresh_token(
        self,
        subject: str,
        org_id: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        expires_in: Optional[int] = None,
    ) -> str:
        """Create a refresh token."""
        now = int(time.time())
        exp = now + (expires_in or self.config.refresh_token_expires_seconds)

        payload = TokenPayload(
            sub=subject,
            iss=self.config.issuer,
            aud=self.config.audience,
            exp=exp,
            iat=now,
            jti=f"rtjti_{secrets.token_hex(16)}",
            org_id=org_id,
            scopes=scopes or [],
            token_type="refresh",
        )

        token = self.encode_token(payload)
        return token

    def create_token_pair(
        self,
        subject: str,
        org_id: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
    ) -> TokenPair:
        """Create an access/refresh token pair."""
        access_token = self.create_access_token(
            subject=subject,
            org_id=org_id,
            scopes=scopes,
            name=name,
            email=email,
            custom_claims=custom_claims,
        )

        refresh_token = self.create_refresh_token(
            subject=subject,
            org_id=org_id,
            scopes=scopes,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.config.access_token_expires_seconds,
            refresh_expires_in=self.config.refresh_token_expires_seconds,
            scope=" ".join(scopes or []),
        )

    # ==================== Token Refresh ====================

    def refresh_tokens(self, refresh_token: str) -> Optional[TokenPair]:
        """
        Refresh tokens using a refresh token.

        Implements token rotation - the old refresh token is invalidated.
        """
        payload = self.decode_token(refresh_token)

        if not payload:
            return None

        if payload.token_type != "refresh":
            return None

        # Revoke old refresh token
        self._revoked_tokens.add(payload.jti)

        # Create new token pair
        return self.create_token_pair(
            subject=payload.sub,
            org_id=payload.org_id,
            scopes=payload.scopes,
        )

    # ==================== Token Verification ====================

    def verify_token(self, token: str) -> Optional[TokenPayload]:
        """Verify a token and return its payload."""
        return self.decode_token(token, verify=True)

    def get_token_claims(self, token: str) -> Optional[Dict[str, Any]]:
        """Get all claims from a token."""
        payload = self.decode_token(token, verify=True)
        if payload:
            return payload.to_dict()
        return None

    # ==================== Token Revocation ====================

    def revoke_token(self, token: str) -> bool:
        """Revoke a token by its JTI."""
        payload = self.decode_token(token, verify=False)
        if payload:
            self._revoked_tokens.add(payload.jti)
            return True
        return False

    def revoke_by_jti(self, jti: str) -> None:
        """Revoke a token by JTI directly."""
        self._revoked_tokens.add(jti)

    def is_revoked(self, jti: str) -> bool:
        """Check if a token is revoked."""
        return jti in self._revoked_tokens

    def cleanup_revoked(self) -> int:
        """
        Cleanup revoked tokens older than refresh token lifetime.

        In production, store expiration time with JTI for proper cleanup.
        """
        # For now, just track count - in production, implement time-based cleanup
        count = len(self._revoked_tokens)
        return count

    # ==================== Token Introspection ====================

    def introspect(self, token: str) -> Dict[str, Any]:
        """
        Introspect a token (similar to OAuth introspection).
        """
        payload = self.decode_token(token, verify=True)

        if not payload:
            return {"active": False}

        return {
            "active": True,
            "sub": payload.sub,
            "iss": payload.iss,
            "aud": payload.aud,
            "exp": payload.exp,
            "iat": payload.iat,
            "jti": payload.jti,
            "token_type": payload.token_type,
            "org_id": payload.org_id,
            "scope": " ".join(payload.scopes),
        }


# Global service instance
_jwt_service: Optional[JWTService] = None


def get_jwt_service() -> JWTService:
    """Get the global JWT service instance."""
    global _jwt_service
    if _jwt_service is None:
        _jwt_service = JWTService()
    return _jwt_service


def configure_jwt_service(config: JWTConfig) -> JWTService:
    """Configure and return the JWT service."""
    global _jwt_service
    _jwt_service = JWTService(config)
    return _jwt_service
