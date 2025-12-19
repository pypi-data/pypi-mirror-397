"""
FlowMason Secrets Management Service

Provides encrypted storage for sensitive values like API keys, tokens, and credentials.

Features:
- Fernet symmetric encryption (AES-128)
- Per-organization key derivation
- Automatic key rotation support
- Comprehensive audit logging for secret access
- Rotation scheduling and policy management

Security model:
- Master key derived from org secret + environment variable
- Each secret encrypted with derived key
- Keys never stored in plaintext
- All access logged with timestamps and actors
"""

import hashlib
import json
import logging
import os
import uuid
from base64 import urlsafe_b64encode
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Cryptography is an optional dependency
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class AuditAction(str, Enum):
    """Types of auditable secret operations."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ROTATE_KEY = "rotate_key"
    ROTATION_SCHEDULED = "rotation_scheduled"
    ROTATION_COMPLETED = "rotation_completed"
    EXPIRATION_WARNING = "expiration_warning"
    ACCESS_DENIED = "access_denied"


@dataclass
class AuditLogEntry:
    """An entry in the secret audit log."""
    id: str
    timestamp: str
    action: str
    secret_name: str
    org_id: str
    actor: Optional[str] = None
    actor_ip: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class RotationPolicy:
    """Policy for automatic secret rotation."""
    secret_name: str
    rotation_interval_days: int
    last_rotated: Optional[str] = None
    next_rotation: Optional[str] = None
    notify_before_days: int = 7
    auto_rotate: bool = False
    rotation_handler: Optional[str] = None  # Name of handler function


@dataclass
class Secret:
    """A stored secret."""
    id: str
    name: str
    description: str
    category: str  # 'api_key', 'token', 'credential', 'other'
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    expires_at: Optional[datetime] = None
    # Value is stored encrypted, not in this dataclass


@dataclass
class SecretMetadata:
    """Metadata about a secret (without the value)."""
    id: str
    name: str
    description: str
    category: str
    created_at: str
    updated_at: str
    created_by: Optional[str] = None
    expires_at: Optional[str] = None
    is_expired: bool = False


class SecretsService:
    """
    Service for managing encrypted secrets.

    Usage:
        secrets = SecretsService(org_id="my-org")
        secrets.set("OPENAI_API_KEY", "sk-...", category="api_key")
        value = secrets.get("OPENAI_API_KEY")
    """

    def __init__(
        self,
        org_id: str,
        master_key: Optional[str] = None,
        storage_path: Optional[str] = None,
    ):
        """
        Initialize secrets service.

        Args:
            org_id: Organization ID for key derivation
            master_key: Master encryption key (default: from FLOWMASON_SECRETS_KEY env var)
            storage_path: Path to store encrypted secrets (default: ~/.flowmason/secrets)
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "cryptography package required for secrets management. "
                "Install with: pip install cryptography"
            )

        self.org_id = org_id
        self._master_key = master_key or os.environ.get("FLOWMASON_SECRETS_KEY")

        if not self._master_key:
            # Generate a warning but allow operation with a derived key
            logger.warning(
                "FLOWMASON_SECRETS_KEY not set. Using org-derived key. "
                "Set FLOWMASON_SECRETS_KEY for production use."
            )
            self._master_key = self._derive_default_key()

        # Derive org-specific encryption key
        self._fernet = self._create_fernet()

        # Storage path
        if storage_path:
            self._storage_path = storage_path
        else:
            self._storage_path = os.path.join(
                os.path.expanduser("~/.flowmason"),
                "secrets",
                hashlib.sha256(org_id.encode()).hexdigest()[:16]
            )

        os.makedirs(self._storage_path, exist_ok=True)

        # Audit log path
        self._audit_path = os.path.join(self._storage_path, "audit")
        os.makedirs(self._audit_path, exist_ok=True)

        # Rotation policies path
        self._policies_path = os.path.join(self._storage_path, "policies")
        os.makedirs(self._policies_path, exist_ok=True)

        # Rotation handlers registry
        self._rotation_handlers: Dict[str, Callable[[str, str], str]] = {}

    def _derive_default_key(self) -> str:
        """Derive a default key from org ID (not recommended for production)."""
        # Use a fixed salt + org_id to generate a reproducible but unique key
        combined = f"flowmason-default-key-{self.org_id}".encode()
        return hashlib.sha256(combined).hexdigest()[:32]

    def _create_fernet(self) -> "Fernet":
        """Create Fernet instance with derived key."""
        # Use PBKDF2 to derive a proper key from the master key
        salt = hashlib.sha256(self.org_id.encode()).digest()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )

        # _master_key is guaranteed to be set after __init__
        assert self._master_key is not None
        key = urlsafe_b64encode(kdf.derive(self._master_key.encode()))
        return Fernet(key)

    def _secret_path(self, name: str) -> str:
        """Get storage path for a secret."""
        safe_name = hashlib.sha256(name.encode()).hexdigest()[:32]
        return os.path.join(self._storage_path, f"{safe_name}.secret")

    def _metadata_path(self, name: str) -> str:
        """Get storage path for secret metadata."""
        safe_name = hashlib.sha256(name.encode()).hexdigest()[:32]
        return os.path.join(self._storage_path, f"{safe_name}.meta")

    def _policy_path(self, name: str) -> str:
        """Get storage path for rotation policy."""
        safe_name = hashlib.sha256(name.encode()).hexdigest()[:32]
        return os.path.join(self._policies_path, f"{safe_name}.policy")

    def _audit_log(
        self,
        action: AuditAction,
        secret_name: str,
        actor: Optional[str] = None,
        actor_ip: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AuditLogEntry:
        """Log an audit event."""
        entry = AuditLogEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            action=action.value,
            secret_name=secret_name,
            org_id=self.org_id,
            actor=actor,
            actor_ip=actor_ip,
            details=details,
            success=success,
            error_message=error_message,
        )

        # Store audit log by date for easier querying
        date_str = datetime.now().strftime("%Y-%m-%d")
        audit_file = os.path.join(self._audit_path, f"{date_str}.jsonl")

        with open(audit_file, "a") as f:
            f.write(json.dumps({
                "id": entry.id,
                "timestamp": entry.timestamp,
                "action": entry.action,
                "secret_name": entry.secret_name,
                "org_id": entry.org_id,
                "actor": entry.actor,
                "actor_ip": entry.actor_ip,
                "details": entry.details,
                "success": entry.success,
                "error_message": entry.error_message,
            }) + "\n")

        if not success:
            logger.warning(
                f"Audit: {action.value} on secret '{secret_name}' FAILED - {error_message}"
            )
        else:
            logger.debug(f"Audit: {action.value} on secret '{secret_name}' by {actor}")

        return entry

    def set(
        self,
        name: str,
        value: str,
        description: str = "",
        category: str = "other",
        expires_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        actor_ip: Optional[str] = None,
    ) -> SecretMetadata:
        """
        Store an encrypted secret.

        Args:
            name: Secret name (e.g., 'OPENAI_API_KEY')
            value: Secret value to encrypt
            description: Description of the secret
            category: Category ('api_key', 'token', 'credential', 'other')
            expires_at: Optional expiration datetime
            created_by: User ID who created the secret
            actor_ip: IP address of the actor (for audit)

        Returns:
            Metadata about the stored secret
        """
        now = datetime.now()
        is_update = self.exists(name)
        action = AuditAction.UPDATE if is_update else AuditAction.CREATE

        try:
            # Encrypt the value
            encrypted = self._fernet.encrypt(value.encode())

            # Save encrypted value
            with open(self._secret_path(name), "wb") as f:
                f.write(encrypted)

            # Save metadata (unencrypted, no sensitive data)
            metadata = {
                "id": hashlib.sha256(f"{self.org_id}:{name}".encode()).hexdigest()[:16],
                "name": name,
                "description": description,
                "category": category,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "created_by": created_by,
                "expires_at": expires_at.isoformat() if expires_at else None,
            }

            with open(self._metadata_path(name), "w") as f:
                json.dump(metadata, f, indent=2)

            # Audit log
            self._audit_log(
                action=action,
                secret_name=name,
                actor=created_by,
                actor_ip=actor_ip,
                details={"category": category, "has_expiration": expires_at is not None},
            )

            logger.info(f"Secret '{name}' stored for org {self.org_id}")

            return SecretMetadata(
                id=str(metadata["id"]),
                name=str(metadata["name"]),
                description=str(metadata.get("description", "")),
                category=str(metadata.get("category", "")),
                created_at=str(metadata["created_at"]),
                updated_at=str(metadata["updated_at"]),
                created_by=metadata.get("created_by"),
                expires_at=metadata.get("expires_at"),
                is_expired=bool(expires_at and expires_at < now),
            )

        except Exception as e:
            self._audit_log(
                action=action,
                secret_name=name,
                actor=created_by,
                actor_ip=actor_ip,
                success=False,
                error_message=str(e),
            )
            raise

    def get(
        self,
        name: str,
        actor: Optional[str] = None,
        actor_ip: Optional[str] = None,
    ) -> Optional[str]:
        """
        Retrieve and decrypt a secret.

        Args:
            name: Secret name
            actor: User ID accessing the secret (for audit)
            actor_ip: IP address of the actor (for audit)

        Returns:
            Decrypted secret value, or None if not found or expired
        """
        secret_path = self._secret_path(name)

        if not os.path.exists(secret_path):
            logger.debug(f"Secret '{name}' not found")
            self._audit_log(
                action=AuditAction.READ,
                secret_name=name,
                actor=actor,
                actor_ip=actor_ip,
                success=False,
                error_message="Secret not found",
            )
            return None

        # Check expiration
        metadata = self.get_metadata(name)
        if metadata and metadata.is_expired:
            logger.warning(f"Secret '{name}' has expired")
            self._audit_log(
                action=AuditAction.ACCESS_DENIED,
                secret_name=name,
                actor=actor,
                actor_ip=actor_ip,
                success=False,
                error_message="Secret has expired",
            )
            return None

        # Read and decrypt
        with open(secret_path, "rb") as f:
            encrypted = f.read()

        try:
            decrypted = self._fernet.decrypt(encrypted)

            # Audit successful read
            self._audit_log(
                action=AuditAction.READ,
                secret_name=name,
                actor=actor,
                actor_ip=actor_ip,
            )

            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt secret '{name}': {e}")
            self._audit_log(
                action=AuditAction.READ,
                secret_name=name,
                actor=actor,
                actor_ip=actor_ip,
                success=False,
                error_message=f"Decryption failed: {e}",
            )
            return None

    def get_metadata(self, name: str) -> Optional[SecretMetadata]:
        """Get metadata for a secret without decrypting the value."""
        meta_path = self._metadata_path(name)

        if not os.path.exists(meta_path):
            return None

        with open(meta_path) as f:
            data = json.load(f)

        # Check expiration
        is_expired = False
        if data.get("expires_at"):
            expires_at = datetime.fromisoformat(data["expires_at"])
            is_expired = expires_at < datetime.now()

        return SecretMetadata(**data, is_expired=is_expired)

    def delete(
        self,
        name: str,
        actor: Optional[str] = None,
        actor_ip: Optional[str] = None,
    ) -> bool:
        """
        Delete a secret.

        Args:
            name: Secret name
            actor: User ID deleting the secret (for audit)
            actor_ip: IP address of the actor (for audit)

        Returns:
            True if deleted, False if not found
        """
        secret_path = self._secret_path(name)
        meta_path = self._metadata_path(name)
        policy_path = self._policy_path(name)

        if not os.path.exists(secret_path):
            self._audit_log(
                action=AuditAction.DELETE,
                secret_name=name,
                actor=actor,
                actor_ip=actor_ip,
                success=False,
                error_message="Secret not found",
            )
            return False

        os.remove(secret_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
        if os.path.exists(policy_path):
            os.remove(policy_path)

        self._audit_log(
            action=AuditAction.DELETE,
            secret_name=name,
            actor=actor,
            actor_ip=actor_ip,
        )

        logger.info(f"Secret '{name}' deleted for org {self.org_id}")
        return True

    def list(self) -> List[SecretMetadata]:
        """List all secrets (metadata only, no values)."""
        secrets: List[SecretMetadata] = []

        if not os.path.exists(self._storage_path):
            return secrets

        for filename in os.listdir(self._storage_path):
            if filename.endswith(".meta"):
                with open(os.path.join(self._storage_path, filename)) as f:
                    data = json.load(f)

                is_expired = False
                if data.get("expires_at"):
                    expires_at = datetime.fromisoformat(data["expires_at"])
                    is_expired = expires_at < datetime.now()

                secrets.append(SecretMetadata(**data, is_expired=is_expired))

        return sorted(secrets, key=lambda s: s.name)

    def exists(self, name: str) -> bool:
        """Check if a secret exists."""
        return os.path.exists(self._secret_path(name))

    def rotate_key(
        self,
        new_master_key: str,
        actor: Optional[str] = None,
        actor_ip: Optional[str] = None,
    ) -> int:
        """
        Rotate the master encryption key.

        Re-encrypts all secrets with a new key.

        Args:
            new_master_key: New master key
            actor: User ID performing the rotation (for audit)
            actor_ip: IP address of the actor (for audit)

        Returns:
            Number of secrets re-encrypted
        """
        secrets_to_rotate = []

        # First, decrypt all secrets with old key
        for meta in self.list():
            value = self.get(meta.name)
            if value:
                secrets_to_rotate.append((meta, value))

        # Create new Fernet with new key
        old_master_key = self._master_key
        self._master_key = new_master_key
        self._fernet = self._create_fernet()

        # Re-encrypt all secrets
        count = 0
        for meta, value in secrets_to_rotate:
            try:
                self.set(
                    name=meta.name,
                    value=value,
                    description=meta.description,
                    category=meta.category,
                    expires_at=datetime.fromisoformat(meta.expires_at) if meta.expires_at else None,
                    created_by=meta.created_by,
                )
                count += 1
            except Exception as e:
                logger.error(f"Failed to rotate secret '{meta.name}': {e}")
                # Rollback on failure
                self._master_key = old_master_key
                self._fernet = self._create_fernet()
                self._audit_log(
                    action=AuditAction.ROTATE_KEY,
                    secret_name="*",
                    actor=actor,
                    actor_ip=actor_ip,
                    success=False,
                    error_message=f"Key rotation failed at secret '{meta.name}'",
                )
                raise RuntimeError(f"Key rotation failed at secret '{meta.name}'")

        self._audit_log(
            action=AuditAction.ROTATE_KEY,
            secret_name="*",
            actor=actor,
            actor_ip=actor_ip,
            details={"secrets_rotated": count},
        )

        logger.info(f"Key rotation complete: {count} secrets re-encrypted")
        return count

    # ============================================
    # Rotation Policy Management
    # ============================================

    def set_rotation_policy(
        self,
        secret_name: str,
        rotation_interval_days: int,
        notify_before_days: int = 7,
        auto_rotate: bool = False,
        rotation_handler: Optional[str] = None,
        actor: Optional[str] = None,
    ) -> RotationPolicy:
        """
        Set a rotation policy for a secret.

        Args:
            secret_name: Name of the secret
            rotation_interval_days: Days between rotations
            notify_before_days: Days before rotation to send notification
            auto_rotate: Whether to automatically rotate
            rotation_handler: Name of registered rotation handler
            actor: User setting the policy

        Returns:
            The created rotation policy
        """
        now = datetime.now()
        next_rotation = now + timedelta(days=rotation_interval_days)

        policy = RotationPolicy(
            secret_name=secret_name,
            rotation_interval_days=rotation_interval_days,
            last_rotated=now.isoformat(),
            next_rotation=next_rotation.isoformat(),
            notify_before_days=notify_before_days,
            auto_rotate=auto_rotate,
            rotation_handler=rotation_handler,
        )

        policy_data = {
            "secret_name": policy.secret_name,
            "rotation_interval_days": policy.rotation_interval_days,
            "last_rotated": policy.last_rotated,
            "next_rotation": policy.next_rotation,
            "notify_before_days": policy.notify_before_days,
            "auto_rotate": policy.auto_rotate,
            "rotation_handler": policy.rotation_handler,
        }

        with open(self._policy_path(secret_name), "w") as f:
            json.dump(policy_data, f, indent=2)

        self._audit_log(
            action=AuditAction.ROTATION_SCHEDULED,
            secret_name=secret_name,
            actor=actor,
            details={
                "interval_days": rotation_interval_days,
                "next_rotation": next_rotation.isoformat(),
                "auto_rotate": auto_rotate,
            },
        )

        return policy

    def get_rotation_policy(self, secret_name: str) -> Optional[RotationPolicy]:
        """Get the rotation policy for a secret."""
        policy_path = self._policy_path(secret_name)

        if not os.path.exists(policy_path):
            return None

        with open(policy_path) as f:
            data = json.load(f)

        return RotationPolicy(**data)

    def delete_rotation_policy(self, secret_name: str) -> bool:
        """Delete a rotation policy."""
        policy_path = self._policy_path(secret_name)

        if not os.path.exists(policy_path):
            return False

        os.remove(policy_path)
        return True

    def list_rotation_policies(self) -> List[RotationPolicy]:
        """List all rotation policies."""
        policies: List[RotationPolicy] = []

        if not os.path.exists(self._policies_path):
            return policies

        for filename in os.listdir(self._policies_path):
            if filename.endswith(".policy"):
                with open(os.path.join(self._policies_path, filename)) as f:
                    data = json.load(f)
                policies.append(RotationPolicy(**data))

        return sorted(policies, key=lambda p: p.secret_name)

    def get_secrets_due_for_rotation(self) -> List[RotationPolicy]:
        """Get secrets that are due for rotation or need notification."""
        now = datetime.now()
        due_policies: List[RotationPolicy] = []

        for policy in self.list_rotation_policies():
            if policy.next_rotation:
                next_rotation = datetime.fromisoformat(policy.next_rotation)
                notify_date = next_rotation - timedelta(days=policy.notify_before_days)

                if now >= notify_date:
                    due_policies.append(policy)

        return due_policies

    def rotate_secret(
        self,
        secret_name: str,
        new_value: str,
        actor: Optional[str] = None,
        actor_ip: Optional[str] = None,
    ) -> SecretMetadata:
        """
        Rotate a specific secret with a new value.

        Args:
            secret_name: Name of the secret to rotate
            new_value: New secret value
            actor: User performing the rotation
            actor_ip: IP address of the actor

        Returns:
            Updated secret metadata
        """
        # Get existing metadata
        metadata = self.get_metadata(secret_name)
        if not metadata:
            raise ValueError(f"Secret '{secret_name}' not found")

        # Update the secret
        result = self.set(
            name=secret_name,
            value=new_value,
            description=metadata.description,
            category=metadata.category,
            expires_at=datetime.fromisoformat(metadata.expires_at) if metadata.expires_at else None,
            created_by=metadata.created_by,
            actor_ip=actor_ip,
        )

        # Update rotation policy if exists
        policy = self.get_rotation_policy(secret_name)
        if policy:
            now = datetime.now()
            next_rotation = now + timedelta(days=policy.rotation_interval_days)

            policy.last_rotated = now.isoformat()
            policy.next_rotation = next_rotation.isoformat()

            policy_data = {
                "secret_name": policy.secret_name,
                "rotation_interval_days": policy.rotation_interval_days,
                "last_rotated": policy.last_rotated,
                "next_rotation": policy.next_rotation,
                "notify_before_days": policy.notify_before_days,
                "auto_rotate": policy.auto_rotate,
                "rotation_handler": policy.rotation_handler,
            }

            with open(self._policy_path(secret_name), "w") as f:
                json.dump(policy_data, f, indent=2)

        self._audit_log(
            action=AuditAction.ROTATION_COMPLETED,
            secret_name=secret_name,
            actor=actor,
            actor_ip=actor_ip,
        )

        return result

    def register_rotation_handler(
        self,
        name: str,
        handler: Callable[[str, str], str],
    ) -> None:
        """
        Register a rotation handler function.

        Handler receives (secret_name, current_value) and returns new_value.
        """
        self._rotation_handlers[name] = handler

    def run_auto_rotations(self, actor: Optional[str] = None) -> List[str]:
        """
        Run auto-rotations for secrets that are due.

        Returns:
            List of secret names that were rotated
        """
        rotated: List[str] = []
        now = datetime.now()

        for policy in self.list_rotation_policies():
            if not policy.auto_rotate:
                continue

            if not policy.next_rotation:
                continue

            next_rotation = datetime.fromisoformat(policy.next_rotation)
            if now < next_rotation:
                continue

            # Get handler
            if not policy.rotation_handler:
                logger.warning(
                    f"Secret '{policy.secret_name}' is due for auto-rotation "
                    "but no handler is configured"
                )
                continue

            handler = self._rotation_handlers.get(policy.rotation_handler)
            if not handler:
                logger.warning(
                    f"Rotation handler '{policy.rotation_handler}' not found "
                    f"for secret '{policy.secret_name}'"
                )
                continue

            try:
                current_value = self.get(policy.secret_name)
                if current_value:
                    new_value = handler(policy.secret_name, current_value)
                    self.rotate_secret(
                        secret_name=policy.secret_name,
                        new_value=new_value,
                        actor=actor or "system:auto-rotation",
                    )
                    rotated.append(policy.secret_name)
            except Exception as e:
                logger.error(
                    f"Auto-rotation failed for '{policy.secret_name}': {e}"
                )

        return rotated

    # ============================================
    # Audit Log Queries
    # ============================================

    def get_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        secret_name: Optional[str] = None,
        action: Optional[AuditAction] = None,
        actor: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """
        Query audit logs.

        Args:
            start_date: Start of date range
            end_date: End of date range
            secret_name: Filter by secret name
            action: Filter by action type
            actor: Filter by actor
            limit: Maximum entries to return

        Returns:
            List of matching audit log entries
        """
        if not os.path.exists(self._audit_path):
            return []

        entries: List[AuditLogEntry] = []
        end_date = end_date or datetime.now()
        start_date = start_date or (end_date - timedelta(days=30))

        # List audit files in date range
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            audit_file = os.path.join(self._audit_path, f"{date_str}.jsonl")

            if os.path.exists(audit_file):
                with open(audit_file) as f:
                    for line in f:
                        if not line.strip():
                            continue
                        data = json.loads(line)

                        # Apply filters
                        if secret_name and data.get("secret_name") != secret_name:
                            continue
                        if action and data.get("action") != action.value:
                            continue
                        if actor and data.get("actor") != actor:
                            continue

                        entries.append(AuditLogEntry(
                            id=data["id"],
                            timestamp=data["timestamp"],
                            action=data["action"],
                            secret_name=data["secret_name"],
                            org_id=data["org_id"],
                            actor=data.get("actor"),
                            actor_ip=data.get("actor_ip"),
                            details=data.get("details"),
                            success=data.get("success", True),
                            error_message=data.get("error_message"),
                        ))

                        if len(entries) >= limit:
                            break

            current_date += timedelta(days=1)

            if len(entries) >= limit:
                break

        # Sort by timestamp descending (most recent first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    def get_secret_access_history(
        self,
        secret_name: str,
        days: int = 30,
    ) -> List[AuditLogEntry]:
        """Get access history for a specific secret."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            secret_name=secret_name,
            limit=1000,
        )

    def get_actor_activity(
        self,
        actor: str,
        days: int = 30,
    ) -> List[AuditLogEntry]:
        """Get all secret access activity for a specific actor."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            actor=actor,
            limit=1000,
        )

    def get_failed_access_attempts(
        self,
        days: int = 7,
    ) -> List[AuditLogEntry]:
        """Get all failed access attempts."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        all_entries = self.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            limit=10000,
        )

        return [e for e in all_entries if not e.success]

    def export_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json",
    ) -> str:
        """
        Export audit logs to a string.

        Args:
            start_date: Start of date range
            end_date: End of date range
            format: Output format ('json' or 'csv')

        Returns:
            Formatted audit log data
        """
        entries = self.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
            limit=100000,
        )

        if format == "csv":
            lines = [
                "id,timestamp,action,secret_name,org_id,actor,actor_ip,success,error_message"
            ]
            for e in entries:
                lines.append(
                    f'"{e.id}","{e.timestamp}","{e.action}","{e.secret_name}",'
                    f'"{e.org_id}","{e.actor or ""}","{e.actor_ip or ""}",'
                    f'"{e.success}","{e.error_message or ""}"'
                )
            return "\n".join(lines)
        else:
            return json.dumps(
                [
                    {
                        "id": e.id,
                        "timestamp": e.timestamp,
                        "action": e.action,
                        "secret_name": e.secret_name,
                        "org_id": e.org_id,
                        "actor": e.actor,
                        "actor_ip": e.actor_ip,
                        "details": e.details,
                        "success": e.success,
                        "error_message": e.error_message,
                    }
                    for e in entries
                ],
                indent=2,
            )


# Global secrets service cache
_secrets_services: Dict[str, SecretsService] = {}


def get_secrets_service(org_id: str) -> SecretsService:
    """Get or create a secrets service for an organization."""
    if org_id not in _secrets_services:
        _secrets_services[org_id] = SecretsService(org_id)
    return _secrets_services[org_id]


def clear_secrets_cache():
    """Clear the secrets service cache."""
    _secrets_services.clear()
