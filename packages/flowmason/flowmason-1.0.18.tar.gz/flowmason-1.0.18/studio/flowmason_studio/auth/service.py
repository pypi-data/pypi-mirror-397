"""
FlowMason Authentication Service

Handles authentication operations and database persistence.
"""

import json
from datetime import datetime
from typing import Any, List, Optional, Tuple

from .models import (
    APIKey,
    APIKeyScope,
    AuditLogEntry,
    Organization,
    OrgMembership,
    Role,
    User,
)

# Global auth service instance
_auth_service: Optional["AuthService"] = None


def get_auth_service() -> "AuthService":
    """Get the global auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def set_auth_service(service: "AuthService") -> None:
    """Set the global auth service instance"""
    global _auth_service
    _auth_service = service


class AuthService:
    """
    Authentication service for FlowMason.

    Handles user, organization, API key, and audit log management.
    Uses SQLite for storage (can be swapped for PostgreSQL).
    """

    def __init__(self):
        """Initialize auth service and create tables"""
        self._init_tables()

    def _init_tables(self) -> None:
        """Create auth tables if they don't exist"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        # Organizations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                plan TEXT DEFAULT 'free',
                max_users INTEGER DEFAULT 5,
                max_pipelines INTEGER DEFAULT 10,
                max_executions_per_day INTEGER DEFAULT 100,
                features TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT,
                email_verified INTEGER DEFAULT 0,
                sso_provider TEXT,
                sso_id TEXT,
                default_org_id TEXT,
                preferences TEXT DEFAULT '{}',
                is_active INTEGER DEFAULT 1,
                last_login TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (default_org_id) REFERENCES organizations(id)
            )
        """)

        # Org memberships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS org_memberships (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                org_id TEXT NOT NULL,
                role TEXT NOT NULL,
                custom_permissions TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (org_id) REFERENCES organizations(id),
                UNIQUE (user_id, org_id)
            )
        """)

        # API keys table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                key_prefix TEXT NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                org_id TEXT NOT NULL,
                user_id TEXT,
                scopes TEXT DEFAULT '["full"]',
                rate_limit INTEGER DEFAULT 1000,
                is_active INTEGER DEFAULT 1,
                expires_at TEXT,
                last_used_at TEXT,
                revoked_at TEXT,
                revoked_reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (org_id) REFERENCES organizations(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                api_key_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                org_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT,
                details TEXT DEFAULT '{}',
                success INTEGER DEFAULT 1,
                error_message TEXT,
                FOREIGN KEY (org_id) REFERENCES organizations(id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_org ON api_keys(org_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_org ON audit_log(org_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)")

        conn.commit()

    # ==================== Organization Operations ====================

    def create_org(self, name: str, slug: str) -> Organization:
        """Create a new organization"""
        from ..services.database import get_connection

        org = Organization.create(name, slug)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO organizations (id, name, slug, plan, max_users, max_pipelines,
                max_executions_per_day, features, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            org.id, org.name, org.slug, org.plan, org.max_users, org.max_pipelines,
            org.max_executions_per_day, json.dumps(org.features),
            json.dumps(org.metadata), org.created_at.isoformat(), org.updated_at.isoformat()
        ))
        conn.commit()

        return org

    def get_org(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM organizations WHERE id = ?", (org_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_org(row)

    def get_org_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM organizations WHERE slug = ?", (slug,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_org(row)

    def _row_to_org(self, row) -> Organization:
        """Convert database row to Organization"""
        return Organization(
            id=row[0],
            name=row[1],
            slug=row[2],
            plan=row[3],
            max_users=row[4],
            max_pipelines=row[5],
            max_executions_per_day=row[6],
            features=json.loads(row[7]),
            metadata=json.loads(row[8]),
            created_at=datetime.fromisoformat(row[9]),
            updated_at=datetime.fromisoformat(row[10]),
        )

    # ==================== User Operations ====================

    def create_user(self, email: str, name: str, password: Optional[str] = None) -> User:
        """Create a new user"""
        from ..services.database import get_connection

        user = User.create(email, name)
        if password:
            user.set_password(password)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (id, email, name, password_hash, email_verified,
                sso_provider, sso_id, default_org_id, preferences, is_active,
                last_login, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user.id, user.email, user.name, user.password_hash, user.email_verified,
            user.sso_provider, user.sso_id, user.default_org_id,
            json.dumps(user.preferences), user.is_active, None,
            user.created_at.isoformat(), user.updated_at.isoformat()
        ))
        conn.commit()

        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_user(row)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_user(row)

    def _row_to_user(self, row) -> User:
        """Convert database row to User"""
        return User(
            id=row[0],
            email=row[1],
            name=row[2],
            password_hash=row[3],
            email_verified=bool(row[4]),
            sso_provider=row[5],
            sso_id=row[6],
            default_org_id=row[7],
            preferences=json.loads(row[8]) if row[8] else {},
            is_active=bool(row[9]),
            last_login=datetime.fromisoformat(row[10]) if row[10] else None,
            created_at=datetime.fromisoformat(row[11]),
            updated_at=datetime.fromisoformat(row[12]),
        )

    # ==================== Membership Operations ====================

    def add_user_to_org(self, user_id: str, org_id: str, role: Role) -> OrgMembership:
        """Add a user to an organization"""
        from ..services.database import get_connection

        membership = OrgMembership.create(user_id, org_id, role)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO org_memberships (id, user_id, org_id, role, custom_permissions, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            membership.id, membership.user_id, membership.org_id,
            membership.role.value, json.dumps(membership.custom_permissions),
            membership.created_at.isoformat()
        ))
        conn.commit()

        return membership

    def get_user_orgs(self, user_id: str) -> List[Tuple[Organization, Role]]:
        """Get all organizations a user belongs to"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, m.role FROM organizations o
            JOIN org_memberships m ON o.id = m.org_id
            WHERE m.user_id = ?
        """, (user_id,))

        results = []
        for row in cursor.fetchall():
            org = self._row_to_org(row[:-1])
            role = Role(row[-1])
            results.append((org, role))

        return results

    def get_user_role_in_org(self, user_id: str, org_id: str) -> Optional[Role]:
        """Get user's role in an organization"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM org_memberships WHERE user_id = ? AND org_id = ?",
            (user_id, org_id)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return Role(row[0])

    # ==================== API Key Operations ====================

    def create_api_key(
        self,
        name: str,
        org_id: str,
        user_id: Optional[str] = None,
        scopes: Optional[List[APIKeyScope]] = None,
        expires_at: Optional[datetime] = None,
    ) -> Tuple[APIKey, str]:
        """
        Create a new API key.

        Returns:
            Tuple of (APIKey, raw_key_string)
            The raw key is only returned once at creation time.
        """
        from ..services.database import get_connection

        api_key, raw_key = APIKey.generate(
            name=name,
            org_id=org_id,
            user_id=user_id,
            scopes=scopes,
            expires_at=expires_at,
        )

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_keys (id, name, key_prefix, key_hash, org_id, user_id,
                scopes, rate_limit, is_active, expires_at, last_used_at,
                revoked_at, revoked_reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            api_key.id, api_key.name, api_key.key_prefix, api_key.key_hash,
            api_key.org_id, api_key.user_id,
            json.dumps([s.value for s in api_key.scopes]), api_key.rate_limit,
            api_key.is_active, api_key.expires_at.isoformat() if api_key.expires_at else None,
            None, None, None, api_key.created_at.isoformat()
        ))
        conn.commit()

        return api_key, raw_key

    def verify_api_key(self, raw_key: str) -> Optional[Tuple[APIKey, Organization]]:
        """
        Verify an API key and return the key and org if valid.

        Returns:
            Tuple of (APIKey, Organization) if valid, None otherwise
        """
        from ..services.database import get_connection

        key_hash = APIKey.hash_key(raw_key)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT k.*, o.* FROM api_keys k
            JOIN organizations o ON k.org_id = o.id
            WHERE k.key_hash = ? AND k.is_active = 1
        """, (key_hash,))
        row = cursor.fetchone()

        if not row:
            return None

        # Parse API key (first 14 columns)
        api_key = APIKey(
            id=row[0],
            name=row[1],
            key_prefix=row[2],
            key_hash=row[3],
            org_id=row[4],
            user_id=row[5],
            scopes=[APIKeyScope(s) for s in json.loads(row[6])],
            rate_limit=row[7],
            is_active=bool(row[8]),
            expires_at=datetime.fromisoformat(row[9]) if row[9] else None,
            last_used_at=datetime.fromisoformat(row[10]) if row[10] else None,
            revoked_at=datetime.fromisoformat(row[11]) if row[11] else None,
            revoked_reason=row[12],
            created_at=datetime.fromisoformat(row[13]),
        )

        # Check expiration
        if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
            return None

        # Parse organization (remaining columns)
        org = Organization(
            id=row[14],
            name=row[15],
            slug=row[16],
            plan=row[17],
            max_users=row[18],
            max_pipelines=row[19],
            max_executions_per_day=row[20],
            features=json.loads(row[21]),
            metadata=json.loads(row[22]),
            created_at=datetime.fromisoformat(row[23]),
            updated_at=datetime.fromisoformat(row[24]),
        )

        # Update last_used_at
        cursor.execute(
            "UPDATE api_keys SET last_used_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), api_key.id)
        )
        conn.commit()

        return api_key, org

    def list_api_keys(self, org_id: str) -> List[APIKey]:
        """List all API keys for an organization (without exposing hashes)"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM api_keys WHERE org_id = ? ORDER BY created_at DESC",
            (org_id,)
        )

        keys = []
        for row in cursor.fetchall():
            keys.append(APIKey(
                id=row[0],
                name=row[1],
                key_prefix=row[2],
                key_hash="[hidden]",  # Don't expose hash
                org_id=row[4],
                user_id=row[5],
                scopes=[APIKeyScope(s) for s in json.loads(row[6])],
                rate_limit=row[7],
                is_active=bool(row[8]),
                expires_at=datetime.fromisoformat(row[9]) if row[9] else None,
                last_used_at=datetime.fromisoformat(row[10]) if row[10] else None,
                revoked_at=datetime.fromisoformat(row[11]) if row[11] else None,
                revoked_reason=row[12],
                created_at=datetime.fromisoformat(row[13]),
            ))

        return keys

    def revoke_api_key(self, key_id: str, reason: str = "Manually revoked") -> bool:
        """Revoke an API key"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE api_keys
            SET is_active = 0, revoked_at = ?, revoked_reason = ?
            WHERE id = ?
        """, (datetime.utcnow().isoformat(), reason, key_id))
        conn.commit()

        return cursor.rowcount > 0

    # ==================== Audit Log Operations ====================

    def log_action(
        self,
        org_id: str,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AuditLogEntry:
        """Log an action to the audit log"""
        from ..services.database import get_connection

        entry = AuditLogEntry.create(
            org_id=org_id,
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            api_key_id=api_key_id,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        entry.success = success
        entry.error_message = error_message

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_log (id, timestamp, user_id, api_key_id, ip_address,
                user_agent, org_id, action, resource_type, resource_id, details,
                success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id, entry.timestamp.isoformat(), entry.user_id, entry.api_key_id,
            entry.ip_address, entry.user_agent, entry.org_id, entry.action,
            entry.resource_type, entry.resource_id, json.dumps(entry.details),
            entry.success, entry.error_message
        ))
        conn.commit()

        return entry

    def get_audit_log(
        self,
        org_id: str,
        limit: int = 100,
        offset: int = 0,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[AuditLogEntry]:
        """Get audit log entries for an organization"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM audit_log WHERE org_id = ?"
        params: List[Any] = [org_id]

        if action:
            query += " AND action = ?"
            params.append(action)

        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)

        entries = []
        for row in cursor.fetchall():
            entries.append(AuditLogEntry(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                user_id=row[2],
                api_key_id=row[3],
                ip_address=row[4],
                user_agent=row[5],
                org_id=row[6],
                action=row[7],
                resource_type=row[8],
                resource_id=row[9],
                details=json.loads(row[10]) if row[10] else {},
                success=bool(row[11]),
                error_message=row[12],
            ))

        return entries
