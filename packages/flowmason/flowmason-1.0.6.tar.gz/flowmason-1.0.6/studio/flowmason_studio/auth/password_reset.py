"""
FlowMason Password Reset Service

Handles secure password reset flow with token-based verification.
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from .models import User


@dataclass
class PasswordResetToken:
    """
    Password reset token.

    Tokens are single-use and expire after a configurable period.
    """
    id: str
    user_id: str
    email: str
    token_hash: str  # SHA-256 hash of the token
    created_at: datetime
    expires_at: datetime
    used_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        user_id: str,
        email: str,
        expires_in_hours: int = 24,
    ) -> tuple["PasswordResetToken", str]:
        """
        Create a new password reset token.

        Returns:
            Tuple of (PasswordResetToken, raw_token)

        The raw token is only available at creation time and should be
        included in the reset link sent to the user.
        """
        # Generate a secure random token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        now = datetime.utcnow()
        reset_token = cls(
            id=f"reset_{secrets.token_hex(12)}",
            user_id=user_id,
            email=email.lower(),
            token_hash=token_hash,
            created_at=now,
            expires_at=now + timedelta(hours=expires_in_hours),
        )

        return reset_token, raw_token

    def is_expired(self) -> bool:
        """Check if the token has expired"""
        return datetime.utcnow() > self.expires_at

    def is_used(self) -> bool:
        """Check if the token has been used"""
        return self.used_at is not None

    def is_valid(self) -> bool:
        """Check if the token is valid (not expired and not used)"""
        return not self.is_expired() and not self.is_used()

    def verify(self, raw_token: str) -> bool:
        """Verify a raw token against this reset token"""
        if not self.is_valid():
            return False
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        return secrets.compare_digest(self.token_hash, token_hash)

    def mark_used(self) -> None:
        """Mark the token as used"""
        self.used_at = datetime.utcnow()


class PasswordResetService:
    """
    Service for handling password reset flow.

    Flow:
    1. User requests reset via email
    2. System generates token and sends email with reset link
    3. User clicks link and provides new password
    4. System verifies token and updates password
    """

    def __init__(self, base_url: str = "http://localhost:8999"):
        """
        Initialize password reset service.

        Args:
            base_url: Base URL for generating reset links
        """
        self.base_url = base_url
        self._init_tables()

    def _init_tables(self) -> None:
        """Create database tables if they don't exist"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reset_email ON password_reset_tokens(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reset_user ON password_reset_tokens(user_id)")
        conn.commit()

    def request_reset(
        self,
        email: str,
        expires_in_hours: int = 24,
    ) -> tuple[Optional[PasswordResetToken], Optional[str], str]:
        """
        Request a password reset for an email address.

        Args:
            email: The user's email address
            expires_in_hours: Token expiration time

        Returns:
            Tuple of (token, raw_token, reset_url) if user exists, else (None, None, "")

        Note: For security, always return the same message whether the user
        exists or not to prevent email enumeration.
        """
        from .service import get_auth_service

        auth_service = get_auth_service()

        # Look up user by email
        user = auth_service.get_user_by_email(email)
        if not user:
            # User doesn't exist - return None but don't reveal this
            return None, None, ""

        # Invalidate any existing tokens for this user
        self._invalidate_existing_tokens(user.id)

        # Create new token
        token, raw_token = PasswordResetToken.create(
            user_id=user.id,
            email=email,
            expires_in_hours=expires_in_hours,
        )

        # Save token
        self._save_token(token)

        # Generate reset URL
        reset_url = f"{self.base_url}/reset-password?token={raw_token}"

        return token, raw_token, reset_url

    def verify_token(self, raw_token: str) -> tuple[bool, Optional[PasswordResetToken], Optional[str]]:
        """
        Verify a password reset token.

        Args:
            raw_token: The raw token from the reset URL

        Returns:
            Tuple of (is_valid, token, error_message)
        """
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token = self._get_token_by_hash(token_hash)

        if not token:
            return False, None, "Invalid or expired reset token"

        if token.is_used():
            return False, token, "This reset link has already been used"

        if token.is_expired():
            return False, token, "This reset link has expired"

        return True, token, None

    def reset_password(
        self,
        raw_token: str,
        new_password: str,
        min_password_length: int = 8,
    ) -> tuple[bool, Optional[str]]:
        """
        Complete the password reset.

        Args:
            raw_token: The raw token from the reset URL
            new_password: The new password to set
            min_password_length: Minimum password length requirement

        Returns:
            Tuple of (success, error_message)
        """
        # Validate password
        if len(new_password) < min_password_length:
            return False, f"Password must be at least {min_password_length} characters"

        # Verify token
        is_valid, token, error = self.verify_token(raw_token)
        if not is_valid or not token:
            return False, error or "Invalid token"

        # Get user
        from .service import get_auth_service
        auth_service = get_auth_service()
        user = auth_service.get_user(token.user_id)

        if not user:
            return False, "User not found"

        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()

        # Save user (update password hash in database)
        self._update_user_password(user)

        # Mark token as used
        token.mark_used()
        self._update_token(token)

        return True, None

    def _save_token(self, token: PasswordResetToken) -> None:
        """Save a reset token to the database"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO password_reset_tokens (
                id, user_id, email, token_hash, created_at, expires_at, used_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            token.id,
            token.user_id,
            token.email,
            token.token_hash,
            token.created_at.isoformat(),
            token.expires_at.isoformat(),
            token.used_at.isoformat() if token.used_at else None,
        ))
        conn.commit()

    def _update_token(self, token: PasswordResetToken) -> None:
        """Update a reset token in the database"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE password_reset_tokens
            SET used_at = ?
            WHERE id = ?
        """, (
            token.used_at.isoformat() if token.used_at else None,
            token.id,
        ))
        conn.commit()

    def _get_token_by_hash(self, token_hash: str) -> Optional[PasswordResetToken]:
        """Get a reset token by its hash"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM password_reset_tokens WHERE token_hash = ?",
            (token_hash,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return PasswordResetToken(
            id=row[0],
            user_id=row[1],
            email=row[2],
            token_hash=row[3],
            created_at=datetime.fromisoformat(row[4]),
            expires_at=datetime.fromisoformat(row[5]),
            used_at=datetime.fromisoformat(row[6]) if row[6] else None,
        )

    def _invalidate_existing_tokens(self, user_id: str) -> None:
        """Invalidate all existing tokens for a user"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        # Mark all unused tokens as used
        cursor.execute("""
            UPDATE password_reset_tokens
            SET used_at = ?
            WHERE user_id = ? AND used_at IS NULL
        """, (datetime.utcnow().isoformat(), user_id))
        conn.commit()

    def _update_user_password(self, user: User) -> None:
        """Update user's password in the database"""
        from ..services.database import get_connection

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET password_hash = ?, updated_at = ?
            WHERE id = ?
        """, (
            user.password_hash,
            user.updated_at.isoformat(),
            user.id,
        ))
        conn.commit()

    def cleanup_expired_tokens(self, older_than_days: int = 7) -> int:
        """
        Clean up expired tokens from the database.

        Args:
            older_than_days: Delete tokens older than this many days

        Returns:
            Number of tokens deleted
        """
        from ..services.database import get_connection

        cutoff = datetime.utcnow() - timedelta(days=older_than_days)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM password_reset_tokens WHERE expires_at < ?",
            (cutoff.isoformat(),)
        )
        conn.commit()

        return cursor.rowcount


# Global service instance
_password_reset_service: Optional[PasswordResetService] = None


def get_password_reset_service() -> PasswordResetService:
    """Get the global password reset service instance"""
    global _password_reset_service
    if _password_reset_service is None:
        import os
        base_url = os.getenv("FLOWMASON_BASE_URL", "http://localhost:8999")
        _password_reset_service = PasswordResetService(base_url)
    return _password_reset_service
