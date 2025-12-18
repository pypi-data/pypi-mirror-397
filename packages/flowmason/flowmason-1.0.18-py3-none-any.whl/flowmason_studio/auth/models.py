"""
FlowMason Authentication Models

Data models for users, organizations, and API keys.
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

# Try to import bcrypt, fall back to hashlib if not available
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


class Role(str, Enum):
    """User roles within an organization"""
    OWNER = "owner"           # Full access, can delete org
    ADMIN = "admin"           # Manage users, pipelines, settings
    DEVELOPER = "developer"   # Create/edit pipelines, run executions
    VIEWER = "viewer"         # Read-only access


class APIKeyScope(str, Enum):
    """API key permission scopes"""
    FULL = "full"             # All permissions
    READ = "read"             # Read-only operations
    EXECUTE = "execute"       # Run pipelines only
    DEPLOY = "deploy"         # Deploy pipelines only


@dataclass
class Organization:
    """
    Organization (Org) model.

    An org is a workspace that contains pipelines, components, and users.
    Similar to a Salesforce org or GitHub organization.
    """
    id: str
    name: str
    slug: str                           # URL-friendly identifier (e.g., "acme-corp")
    created_at: datetime
    updated_at: datetime

    # Settings
    plan: str = "free"                  # free, pro, enterprise
    max_users: int = 5
    max_pipelines: int = 10
    max_executions_per_day: int = 100

    # Features
    features: List[str] = field(default_factory=list)  # enabled feature flags

    # Metadata
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(cls, name: str, slug: str) -> "Organization":
        """Create a new organization"""
        now = datetime.utcnow()
        return cls(
            id=f"org_{secrets.token_hex(12)}",
            name=name,
            slug=slug.lower().replace(" ", "-"),
            created_at=now,
            updated_at=now,
        )


@dataclass
class User:
    """
    User model.

    A user belongs to one or more organizations with specific roles.
    """
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: datetime

    # Auth
    password_hash: Optional[str] = None   # For email/password auth
    email_verified: bool = False

    # SSO
    sso_provider: Optional[str] = None    # "google", "github", "okta", etc.
    sso_id: Optional[str] = None

    # Settings
    default_org_id: Optional[str] = None
    preferences: dict = field(default_factory=dict)

    # Status
    is_active: bool = True
    last_login: Optional[datetime] = None

    @classmethod
    def create(cls, email: str, name: str) -> "User":
        """Create a new user"""
        now = datetime.utcnow()
        return cls(
            id=f"user_{secrets.token_hex(12)}",
            email=email.lower(),
            name=name,
            created_at=now,
            updated_at=now,
        )

    def set_password(self, password: str) -> None:
        """
        Set password hash using bcrypt (recommended) or SHA-256 fallback.

        Bcrypt is preferred for production as it:
        - Uses salt automatically
        - Has configurable work factor (rounds)
        - Is designed to be slow to resist brute force
        """
        if BCRYPT_AVAILABLE:
            # Use bcrypt with 12 rounds (recommended for production)
            salt = bcrypt.gensalt(rounds=12)
            self.password_hash = bcrypt.hashpw(password.encode(), salt).decode()
        else:
            # Fallback to SHA-256 with user ID as salt
            self.password_hash = hashlib.sha256(
                (password + self.id).encode()
            ).hexdigest()

    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash.

        Automatically detects bcrypt vs SHA-256 hash format.
        """
        if not self.password_hash:
            return False

        # Detect bcrypt hash (starts with $2b$, $2a$, or $2y$)
        if self.password_hash.startswith(('$2b$', '$2a$', '$2y$')):
            if not BCRYPT_AVAILABLE:
                raise RuntimeError("bcrypt required to verify this password hash")
            return bcrypt.checkpw(password.encode(), self.password_hash.encode())
        else:
            # Legacy SHA-256 hash
            expected = hashlib.sha256(
                (password + self.id).encode()
            ).hexdigest()
            return secrets.compare_digest(self.password_hash, expected)

    def needs_password_rehash(self) -> bool:
        """
        Check if password should be rehashed (e.g., upgrading from SHA-256 to bcrypt).

        Call this after successful login to opportunistically upgrade hashes.
        """
        if not self.password_hash:
            return False
        # If bcrypt is available and hash is not bcrypt format, needs rehash
        if BCRYPT_AVAILABLE and not self.password_hash.startswith(('$2b$', '$2a$', '$2y$')):
            return True
        return False


@dataclass
class OrgMembership:
    """
    Organization membership - links users to orgs with roles.
    """
    id: str
    user_id: str
    org_id: str
    role: Role
    created_at: datetime

    # Permissions override (optional)
    custom_permissions: List[str] = field(default_factory=list)

    @classmethod
    def create(cls, user_id: str, org_id: str, role: Role) -> "OrgMembership":
        """Create a new membership"""
        return cls(
            id=f"mem_{secrets.token_hex(12)}",
            user_id=user_id,
            org_id=org_id,
            role=role,
            created_at=datetime.utcnow(),
        )


@dataclass
class APIKey:
    """
    API Key model.

    API keys are used for programmatic access (CLI, CI/CD, integrations).
    Keys are scoped to an organization and optionally a user.
    """
    id: str
    name: str                           # Human-readable name
    key_prefix: str                     # First 8 chars for identification (e.g., "fm_live_")
    key_hash: str                       # SHA-256 hash of full key

    org_id: str                         # Organization this key belongs to
    user_id: Optional[str] = None       # User who created it (for audit)

    scopes: List[APIKeyScope] = field(default_factory=lambda: [APIKeyScope.FULL])

    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

    # Rate limiting
    rate_limit: int = 1000              # Requests per hour

    # Status
    is_active: bool = True
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None

    @classmethod
    def generate(
        cls,
        name: str,
        org_id: str,
        user_id: Optional[str] = None,
        scopes: Optional[List[APIKeyScope]] = None,
        expires_at: Optional[datetime] = None,
    ) -> tuple["APIKey", str]:
        """
        Generate a new API key.

        Returns:
            Tuple of (APIKey object, raw key string)

        The raw key is only available at creation time and should be
        shown to the user once. It cannot be retrieved later.
        """
        # Generate a secure random key
        # Format: fm_<env>_<random>
        # e.g., fm_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
        env = "live"  # Could be "test" for sandbox keys
        random_part = secrets.token_hex(24)  # 48 chars
        raw_key = f"fm_{env}_{random_part}"

        # Hash the key for storage
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        api_key = cls(
            id=f"key_{secrets.token_hex(12)}",
            name=name,
            key_prefix=raw_key[:12],  # "fm_live_a1b2"
            key_hash=key_hash,
            org_id=org_id,
            user_id=user_id,
            scopes=scopes or [APIKeyScope.FULL],
            expires_at=expires_at,
        )

        return api_key, raw_key

    @staticmethod
    def hash_key(raw_key: str) -> str:
        """Hash a raw API key for comparison"""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def verify(self, raw_key: str) -> bool:
        """Verify a raw API key against this key"""
        if not self.is_active:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return secrets.compare_digest(
            self.key_hash,
            self.hash_key(raw_key)
        )

    def has_scope(self, scope: APIKeyScope) -> bool:
        """Check if key has a specific scope"""
        return APIKeyScope.FULL in self.scopes or scope in self.scopes

    def revoke(self, reason: str = "Manually revoked") -> None:
        """Revoke this API key"""
        self.is_active = False
        self.revoked_at = datetime.utcnow()
        self.revoked_reason = reason


@dataclass
class AuditLogEntry:
    """
    Audit log entry for tracking user actions.
    """
    id: str
    timestamp: datetime

    # Who
    user_id: Optional[str]
    api_key_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]

    # What
    org_id: str
    action: str                         # e.g., "pipeline.create", "execution.run"
    resource_type: str                  # e.g., "pipeline", "component"
    resource_id: Optional[str]

    # Details
    details: dict = field(default_factory=dict)

    # Result
    success: bool = True
    error_message: Optional[str] = None

    @classmethod
    def create(
        cls,
        org_id: str,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "AuditLogEntry":
        """Create a new audit log entry"""
        return cls(
            id=f"audit_{secrets.token_hex(12)}",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            api_key_id=api_key_id,
            ip_address=ip_address,
            user_agent=user_agent,
            org_id=org_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
        )
