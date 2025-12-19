"""
Webhook Storage Service.

Manages webhook trigger configurations for pipelines.
"""

import hashlib
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class WebhookTrigger:
    """A webhook trigger configuration."""
    id: str
    name: str
    pipeline_id: str
    pipeline_name: str
    org_id: str

    # Webhook URL components
    webhook_token: str  # Secret token for the webhook URL

    # Input mapping
    input_mapping: Dict[str, str] = field(default_factory=dict)  # Maps webhook fields to pipeline inputs
    default_inputs: Dict[str, Any] = field(default_factory=dict)  # Default values for pipeline inputs

    # Authentication
    require_auth: bool = True  # Require API key or secret
    auth_header: Optional[str] = None  # Expected auth header name (e.g., X-Webhook-Secret)
    auth_secret: Optional[str] = None  # Expected secret value (hashed)

    # Options
    enabled: bool = True
    async_mode: bool = True  # Return immediately or wait for completion

    # Metadata
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    last_triggered_at: Optional[str] = None
    trigger_count: int = 0


@dataclass
class WebhookInvocation:
    """Record of a webhook invocation."""
    id: str
    webhook_id: str
    run_id: Optional[str]

    # Request details
    request_method: str
    request_headers: Dict[str, str]
    request_body: Optional[str]
    source_ip: Optional[str]

    # Result
    status: str  # "success", "error", "rejected"
    error_message: Optional[str] = None
    response_code: int = 200

    # Timing
    invoked_at: str = ""
    processed_at: Optional[str] = None


class WebhookStorage:
    """Storage for webhook triggers using SQLite."""

    def __init__(self):
        """Initialize storage and create tables."""
        from flowmason_studio.services.database import get_connection
        self._conn = get_connection()
        self._create_tables()

    def _create_tables(self):
        """Create webhook tables if they don't exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS webhooks (
                id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                name TEXT NOT NULL,
                pipeline_id TEXT NOT NULL,
                pipeline_name TEXT NOT NULL,
                webhook_token TEXT NOT NULL UNIQUE,
                input_mapping TEXT DEFAULT '{}',
                default_inputs TEXT DEFAULT '{}',
                require_auth INTEGER DEFAULT 1,
                auth_header TEXT,
                auth_secret TEXT,
                enabled INTEGER DEFAULT 1,
                async_mode INTEGER DEFAULT 1,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_triggered_at TEXT,
                trigger_count INTEGER DEFAULT 0
            )
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_webhooks_org ON webhooks(org_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_webhooks_token ON webhooks(webhook_token)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_webhooks_pipeline ON webhooks(pipeline_id)
        """)

        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS webhook_invocations (
                id TEXT PRIMARY KEY,
                webhook_id TEXT NOT NULL,
                run_id TEXT,
                request_method TEXT NOT NULL,
                request_headers TEXT,
                request_body TEXT,
                source_ip TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                response_code INTEGER DEFAULT 200,
                invoked_at TEXT NOT NULL,
                processed_at TEXT,
                FOREIGN KEY (webhook_id) REFERENCES webhooks(id)
            )
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_invocations_webhook ON webhook_invocations(webhook_id)
        """)

        self._conn.commit()

    def _generate_token(self) -> str:
        """Generate a secure webhook token."""
        return secrets.token_urlsafe(32)

    def _hash_secret(self, secret: str) -> str:
        """Hash an authentication secret."""
        return hashlib.sha256(secret.encode()).hexdigest()

    def create(
        self,
        name: str,
        pipeline_id: str,
        pipeline_name: str,
        org_id: str,
        input_mapping: Optional[Dict[str, str]] = None,
        default_inputs: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
        auth_header: Optional[str] = None,
        auth_secret: Optional[str] = None,
        async_mode: bool = True,
        description: str = "",
    ) -> WebhookTrigger:
        """Create a new webhook trigger."""
        import uuid

        webhook_id = str(uuid.uuid4())
        webhook_token = self._generate_token()
        now = datetime.utcnow().isoformat()

        # Hash the auth secret if provided
        hashed_secret = self._hash_secret(auth_secret) if auth_secret else None

        self._conn.execute(
            """
            INSERT INTO webhooks (
                id, org_id, name, pipeline_id, pipeline_name, webhook_token,
                input_mapping, default_inputs, require_auth, auth_header, auth_secret,
                enabled, async_mode, description, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                webhook_id,
                org_id,
                name,
                pipeline_id,
                pipeline_name,
                webhook_token,
                json.dumps(input_mapping or {}),
                json.dumps(default_inputs or {}),
                1 if require_auth else 0,
                auth_header,
                hashed_secret,
                1,  # enabled
                1 if async_mode else 0,
                description,
                now,
                now,
            ),
        )
        self._conn.commit()

        return WebhookTrigger(
            id=webhook_id,
            name=name,
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            org_id=org_id,
            webhook_token=webhook_token,
            input_mapping=input_mapping or {},
            default_inputs=default_inputs or {},
            require_auth=require_auth,
            auth_header=auth_header,
            auth_secret=hashed_secret,
            enabled=True,
            async_mode=async_mode,
            description=description,
            created_at=now,
            updated_at=now,
        )

    def get(self, webhook_id: str, org_id: Optional[str] = None) -> Optional[WebhookTrigger]:
        """Get a webhook by ID."""
        query = "SELECT * FROM webhooks WHERE id = ?"
        params = [webhook_id]

        if org_id:
            query += " AND org_id = ?"
            params.append(org_id)

        cursor = self._conn.execute(query, params)
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_webhook(row)

    def get_by_token(self, token: str) -> Optional[WebhookTrigger]:
        """Get a webhook by its token."""
        cursor = self._conn.execute(
            "SELECT * FROM webhooks WHERE webhook_token = ?",
            (token,),
        )
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_webhook(row)

    def list(
        self,
        org_id: str,
        pipeline_id: Optional[str] = None,
        enabled_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[WebhookTrigger], int]:
        """List webhooks for an organization."""
        query = "SELECT * FROM webhooks WHERE org_id = ?"
        count_query = "SELECT COUNT(*) FROM webhooks WHERE org_id = ?"
        params: List[Any] = [org_id]

        if pipeline_id:
            query += " AND pipeline_id = ?"
            count_query += " AND pipeline_id = ?"
            params.append(pipeline_id)

        if enabled_only:
            query += " AND enabled = 1"
            count_query += " AND enabled = 1"

        # Get total count
        cursor = self._conn.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self._conn.execute(query, params)
        webhooks = [self._row_to_webhook(row) for row in cursor.fetchall()]

        return webhooks, total

    def update(
        self,
        webhook_id: str,
        org_id: str,
        name: Optional[str] = None,
        input_mapping: Optional[Dict[str, str]] = None,
        default_inputs: Optional[Dict[str, Any]] = None,
        require_auth: Optional[bool] = None,
        auth_header: Optional[str] = None,
        auth_secret: Optional[str] = None,
        enabled: Optional[bool] = None,
        async_mode: Optional[bool] = None,
        description: Optional[str] = None,
    ) -> Optional[WebhookTrigger]:
        """Update a webhook."""
        updates: List[str] = []
        params: List[Any] = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if input_mapping is not None:
            updates.append("input_mapping = ?")
            params.append(json.dumps(input_mapping))

        if default_inputs is not None:
            updates.append("default_inputs = ?")
            params.append(json.dumps(default_inputs))

        if require_auth is not None:
            updates.append("require_auth = ?")
            params.append(1 if require_auth else 0)

        if auth_header is not None:
            updates.append("auth_header = ?")
            params.append(auth_header)

        if auth_secret is not None:
            updates.append("auth_secret = ?")
            params.append(self._hash_secret(auth_secret) if auth_secret else None)

        if enabled is not None:
            updates.append("enabled = ?")
            params.append(1 if enabled else 0)

        if async_mode is not None:
            updates.append("async_mode = ?")
            params.append(1 if async_mode else 0)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if not updates:
            return self.get(webhook_id, org_id)

        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())

        params.extend([webhook_id, org_id])

        self._conn.execute(
            f"UPDATE webhooks SET {', '.join(updates)} WHERE id = ? AND org_id = ?",
            params,
        )
        self._conn.commit()

        return self.get(webhook_id, org_id)

    def delete(self, webhook_id: str, org_id: str) -> bool:
        """Delete a webhook."""
        cursor = self._conn.execute(
            "DELETE FROM webhooks WHERE id = ? AND org_id = ?",
            (webhook_id, org_id),
        )
        self._conn.commit()
        return bool(cursor.rowcount > 0)

    def regenerate_token(self, webhook_id: str, org_id: str) -> Optional[str]:
        """Regenerate the webhook token."""
        new_token = self._generate_token()

        cursor = self._conn.execute(
            "UPDATE webhooks SET webhook_token = ?, updated_at = ? WHERE id = ? AND org_id = ?",
            (new_token, datetime.utcnow().isoformat(), webhook_id, org_id),
        )
        self._conn.commit()

        if cursor.rowcount > 0:
            return new_token
        return None

    def increment_trigger_count(self, webhook_id: str):
        """Increment the trigger count for a webhook."""
        self._conn.execute(
            """
            UPDATE webhooks
            SET trigger_count = trigger_count + 1, last_triggered_at = ?
            WHERE id = ?
            """,
            (datetime.utcnow().isoformat(), webhook_id),
        )
        self._conn.commit()

    def verify_auth(self, webhook: WebhookTrigger, auth_value: Optional[str]) -> bool:
        """Verify webhook authentication."""
        if not webhook.require_auth:
            return True

        if not auth_value:
            return False

        if webhook.auth_secret:
            return self._hash_secret(auth_value) == webhook.auth_secret

        return True

    def log_invocation(
        self,
        webhook_id: str,
        run_id: Optional[str],
        request_method: str,
        request_headers: Dict[str, str],
        request_body: Optional[str],
        source_ip: Optional[str],
        status: str,
        error_message: Optional[str] = None,
        response_code: int = 200,
    ) -> str:
        """Log a webhook invocation."""
        import uuid

        invocation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        self._conn.execute(
            """
            INSERT INTO webhook_invocations (
                id, webhook_id, run_id, request_method, request_headers,
                request_body, source_ip, status, error_message, response_code,
                invoked_at, processed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                invocation_id,
                webhook_id,
                run_id,
                request_method,
                json.dumps(request_headers),
                request_body[:10000] if request_body else None,  # Limit body size
                source_ip,
                status,
                error_message,
                response_code,
                now,
                now if status != "pending" else None,
            ),
        )
        self._conn.commit()

        return invocation_id

    def get_invocations(
        self,
        webhook_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[WebhookInvocation]:
        """Get invocation history for a webhook."""
        cursor = self._conn.execute(
            """
            SELECT * FROM webhook_invocations
            WHERE webhook_id = ?
            ORDER BY invoked_at DESC
            LIMIT ? OFFSET ?
            """,
            (webhook_id, limit, offset),
        )

        return [self._row_to_invocation(row) for row in cursor.fetchall()]

    def _row_to_webhook(self, row) -> WebhookTrigger:
        """Convert a database row to a WebhookTrigger."""
        return WebhookTrigger(
            id=row[0],
            org_id=row[1],
            name=row[2],
            pipeline_id=row[3],
            pipeline_name=row[4],
            webhook_token=row[5],
            input_mapping=json.loads(row[6]) if row[6] else {},
            default_inputs=json.loads(row[7]) if row[7] else {},
            require_auth=bool(row[8]),
            auth_header=row[9],
            auth_secret=row[10],
            enabled=bool(row[11]),
            async_mode=bool(row[12]),
            description=row[13] or "",
            created_at=row[14],
            updated_at=row[15],
            last_triggered_at=row[16],
            trigger_count=row[17] or 0,
        )

    def _row_to_invocation(self, row) -> WebhookInvocation:
        """Convert a database row to a WebhookInvocation."""
        return WebhookInvocation(
            id=row[0],
            webhook_id=row[1],
            run_id=row[2],
            request_method=row[3],
            request_headers=json.loads(row[4]) if row[4] else {},
            request_body=row[5],
            source_ip=row[6],
            status=row[7],
            error_message=row[8],
            response_code=row[9] or 200,
            invoked_at=row[10],
            processed_at=row[11],
        )


# Global instance
_webhook_storage: Optional[WebhookStorage] = None


def get_webhook_storage() -> WebhookStorage:
    """Get the global webhook storage instance."""
    global _webhook_storage
    if _webhook_storage is None:
        _webhook_storage = WebhookStorage()
    return _webhook_storage
