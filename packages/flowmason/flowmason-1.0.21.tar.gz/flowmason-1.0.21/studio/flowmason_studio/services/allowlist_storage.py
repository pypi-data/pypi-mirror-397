"""
Allowlist Storage Service for FlowMason Output Security.

Handles CRUD operations for allowlist entries and stored connections,
plus validation logic for checking if output destinations are permitted.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from ..models.allowlist import (
    AllowlistEntry,
    AllowlistEntryCreate,
    AllowlistEntryType,
    AllowlistEntryUpdate,
    AllowlistValidationRequest,
    AllowlistValidationResult,
    OutputDeliveryLog,
    OutputDeliveryStatus,
    StoredConnection,
    StoredConnectionCreate,
    StoredConnectionType,
    StoredConnectionUpdate,
)
from . import database

# =============================================================================
# Allowlist Entry CRUD
# =============================================================================

def create_allowlist_entry(
    org_id: str,
    entry: AllowlistEntryCreate,
    created_by: Optional[str] = None
) -> AllowlistEntry:
    """Create a new allowlist entry for an organization."""
    entry_id = f"ale-{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    conn = database.get_connection()
    query = database.adapt_query("""
        INSERT INTO output_allowlist (
            id, org_id, entry_type, pattern, description,
            is_active, created_by, created_at, expires_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

    expires_at = entry.expires_at.isoformat() if entry.expires_at else None

    if database.is_postgresql():
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(query, (
                entry_id, org_id, entry.entry_type.value, entry.pattern,
                entry.description, True, created_by, now, expires_at
            ))
    else:
        conn.execute(query, (
            entry_id, org_id, entry.entry_type.value, entry.pattern,
            entry.description, 1, created_by, now, expires_at
        ))

    return AllowlistEntry(
        id=entry_id,
        org_id=org_id,
        entry_type=entry.entry_type,
        pattern=entry.pattern,
        description=entry.description,
        is_active=True,
        created_by=created_by,
        created_at=datetime.fromisoformat(now),
        expires_at=entry.expires_at
    )


def get_allowlist_entry(entry_id: str) -> Optional[AllowlistEntry]:
    """Get a single allowlist entry by ID."""
    row = database.fetchone(
        "SELECT * FROM output_allowlist WHERE id = ?",
        (entry_id,)
    )
    if not row:
        return None
    return _row_to_allowlist_entry(row)


def list_allowlist_entries(
    org_id: str,
    entry_type: Optional[AllowlistEntryType] = None,
    active_only: bool = True
) -> List[AllowlistEntry]:
    """List allowlist entries for an organization."""
    query = "SELECT * FROM output_allowlist WHERE org_id = ?"
    params: List[Any] = [org_id]

    if entry_type:
        query += " AND entry_type = ?"
        params.append(entry_type.value)

    if active_only:
        query += " AND is_active = ?"
        params.append(1 if not database.is_postgresql() else True)

    query += " ORDER BY created_at DESC"

    rows = database.fetchall(query, tuple(params))
    return [_row_to_allowlist_entry(row) for row in rows]


def update_allowlist_entry(
    entry_id: str,
    update: AllowlistEntryUpdate
) -> Optional[AllowlistEntry]:
    """Update an allowlist entry."""
    existing = get_allowlist_entry(entry_id)
    if not existing:
        return None

    updates: List[str] = []
    params: List[Any] = []

    if update.pattern is not None:
        updates.append("pattern = ?")
        params.append(update.pattern)
    if update.description is not None:
        updates.append("description = ?")
        params.append(update.description)
    if update.is_active is not None:
        updates.append("is_active = ?")
        params.append(1 if update.is_active else 0)
    if update.expires_at is not None:
        updates.append("expires_at = ?")
        params.append(update.expires_at.isoformat())

    if not updates:
        return existing

    params.append(entry_id)
    query = database.adapt_query(
        f"UPDATE output_allowlist SET {', '.join(updates)} WHERE id = ?"
    )

    conn = database.get_connection()
    if database.is_postgresql():
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(query, tuple(params))
    else:
        conn.execute(query, tuple(params))

    return get_allowlist_entry(entry_id)


def delete_allowlist_entry(entry_id: str) -> bool:
    """Delete an allowlist entry."""
    conn = database.get_connection()
    query = database.adapt_query("DELETE FROM output_allowlist WHERE id = ?")

    if database.is_postgresql():
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(query, (entry_id,))
            return bool(cur.rowcount > 0)
    else:
        cursor = conn.execute(query, (entry_id,))
        return bool(cursor.rowcount > 0)


def _row_to_allowlist_entry(row: Dict[str, Any]) -> AllowlistEntry:
    """Convert a database row to an AllowlistEntry model."""
    is_active = row["is_active"]
    if isinstance(is_active, int):
        is_active = bool(is_active)

    expires_at = None
    if row.get("expires_at"):
        expires_at = datetime.fromisoformat(row["expires_at"])

    return AllowlistEntry(
        id=row["id"],
        org_id=row["org_id"],
        entry_type=AllowlistEntryType(row["entry_type"]),
        pattern=row["pattern"],
        description=row.get("description"),
        is_active=is_active,
        created_by=row.get("created_by"),
        created_at=datetime.fromisoformat(row["created_at"]),
        expires_at=expires_at
    )


# =============================================================================
# Allowlist Validation
# =============================================================================

def validate_destination(
    org_id: str,
    request: AllowlistValidationRequest
) -> AllowlistValidationResult:
    """Validate a destination against the organization's allowlist.

    Returns whether the destination is permitted and which entry matched.
    """
    # Get all active entries for the org
    entries = list_allowlist_entries(org_id, active_only=True)

    # Filter out expired entries
    now = datetime.utcnow()
    entries = [e for e in entries if not e.expires_at or e.expires_at > now]

    # Map destination type to allowlist entry types
    type_mapping = {
        "webhook": [AllowlistEntryType.WEBHOOK_URL, AllowlistEntryType.WEBHOOK_DOMAIN],
        "email": [AllowlistEntryType.EMAIL_DOMAIN],
        "database": [AllowlistEntryType.DATABASE_CONNECTION],
        "message_queue": [AllowlistEntryType.MESSAGE_QUEUE_CONNECTION],
    }

    allowed_entry_types = type_mapping.get(request.destination_type, [])

    # Filter to relevant entry types
    relevant_entries = [e for e in entries if e.entry_type in allowed_entry_types]

    # Check each entry for a match
    for entry in relevant_entries:
        if _pattern_matches(entry, request.destination_value):
            return AllowlistValidationResult(
                is_allowed=True,
                matched_entry_id=entry.id,
                matched_pattern=entry.pattern,
                reason=None
            )

    # No match found
    return AllowlistValidationResult(
        is_allowed=False,
        matched_entry_id=None,
        matched_pattern=None,
        reason=f"No allowlist entry found for {request.destination_type}: {request.destination_value}"
    )


def _pattern_matches(entry: AllowlistEntry, value: str) -> bool:
    """Check if an allowlist entry pattern matches a value."""
    pattern = entry.pattern

    if entry.entry_type == AllowlistEntryType.WEBHOOK_URL:
        # Exact URL match (case-insensitive path comparison)
        return value.lower() == pattern.lower()

    elif entry.entry_type == AllowlistEntryType.WEBHOOK_DOMAIN:
        # Domain wildcard matching (*.example.com)
        try:
            parsed = urlparse(value)
            host = parsed.netloc.lower()

            # Remove port if present
            if ":" in host:
                host = host.split(":")[0]

            # Check if pattern starts with wildcard
            if pattern.startswith("*."):
                # Match any subdomain
                domain = pattern[2:].lower()
                return host == domain or host.endswith("." + domain)
            else:
                # Exact domain match
                return host == pattern.lower()
        except Exception:
            return False

    elif entry.entry_type == AllowlistEntryType.EMAIL_DOMAIN:
        # Email domain matching (@example.com)
        domain = pattern.lstrip("@").lower()

        # Value could be email address or just domain
        if "@" in value:
            email_domain = value.split("@")[1].lower()
            return email_domain == domain
        else:
            return value.lower() == domain

    elif entry.entry_type in (
        AllowlistEntryType.DATABASE_CONNECTION,
        AllowlistEntryType.MESSAGE_QUEUE_CONNECTION
    ):
        # Connection ID matching (exact match)
        return value == pattern

    return False


# =============================================================================
# Stored Connection CRUD
# =============================================================================

def create_stored_connection(
    org_id: str,
    connection: StoredConnectionCreate,
    created_by: Optional[str] = None
) -> StoredConnection:
    """Create a new stored connection for an organization."""
    conn_id = f"conn-{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    # Encrypt password (for now, just base64 - in production use proper encryption)
    import base64
    password_encrypted = None
    if connection.password:
        password_encrypted = base64.b64encode(connection.password.encode()).decode()

    additional_config_json = json.dumps(connection.additional_config) if connection.additional_config else None

    conn = database.get_connection()
    query = database.adapt_query("""
        INSERT INTO stored_connections (
            id, org_id, name, connection_type, host, port, database_name,
            username, password_encrypted, ssl_enabled, additional_config,
            is_active, created_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """)

    ssl_val = 1 if connection.ssl_enabled else 0
    if database.is_postgresql():
        ssl_val = connection.ssl_enabled
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(query, (
                conn_id, org_id, connection.name, connection.connection_type.value,
                connection.host, connection.port, connection.database,
                connection.username, password_encrypted, ssl_val,
                additional_config_json, True, created_by, now
            ))
    else:
        conn.execute(query, (
            conn_id, org_id, connection.name, connection.connection_type.value,
            connection.host, connection.port, connection.database,
            connection.username, password_encrypted, ssl_val,
            additional_config_json, 1, created_by, now
        ))

    return StoredConnection(
        id=conn_id,
        org_id=org_id,
        name=connection.name,
        connection_type=connection.connection_type,
        host=connection.host,
        port=connection.port,
        database=connection.database,
        username=_mask_username(connection.username),
        ssl_enabled=connection.ssl_enabled,
        is_active=True,
        created_by=created_by,
        created_at=datetime.fromisoformat(now),
        last_used_at=None
    )


def get_stored_connection(connection_id: str) -> Optional[StoredConnection]:
    """Get a single stored connection by ID (password is never returned)."""
    row = database.fetchone(
        "SELECT * FROM stored_connections WHERE id = ?",
        (connection_id,)
    )
    if not row:
        return None
    return _row_to_stored_connection(row)


def list_stored_connections(
    org_id: str,
    connection_type: Optional[StoredConnectionType] = None,
    active_only: bool = True
) -> List[StoredConnection]:
    """List stored connections for an organization."""
    query = "SELECT * FROM stored_connections WHERE org_id = ?"
    params: List[Any] = [org_id]

    if connection_type:
        query += " AND connection_type = ?"
        params.append(connection_type.value)

    if active_only:
        query += " AND is_active = ?"
        params.append(1 if not database.is_postgresql() else True)

    query += " ORDER BY name"

    rows = database.fetchall(query, tuple(params))
    return [_row_to_stored_connection(row) for row in rows]


def update_stored_connection(
    connection_id: str,
    update: StoredConnectionUpdate
) -> Optional[StoredConnection]:
    """Update a stored connection."""
    existing = get_stored_connection(connection_id)
    if not existing:
        return None

    updates: List[str] = []
    params: List[Any] = []

    if update.name is not None:
        updates.append("name = ?")
        params.append(update.name)
    if update.host is not None:
        updates.append("host = ?")
        params.append(update.host)
    if update.port is not None:
        updates.append("port = ?")
        params.append(update.port)
    if update.database is not None:
        updates.append("database_name = ?")
        params.append(update.database)
    if update.username is not None:
        updates.append("username = ?")
        params.append(update.username)
    if update.password is not None:
        import base64
        password_encrypted = base64.b64encode(update.password.encode()).decode()
        updates.append("password_encrypted = ?")
        params.append(password_encrypted)
    if update.ssl_enabled is not None:
        updates.append("ssl_enabled = ?")
        params.append(1 if update.ssl_enabled else 0)
    if update.is_active is not None:
        updates.append("is_active = ?")
        params.append(1 if update.is_active else 0)
    if update.additional_config is not None:
        updates.append("additional_config = ?")
        params.append(json.dumps(update.additional_config))

    if not updates:
        return existing

    params.append(connection_id)
    query = database.adapt_query(
        f"UPDATE stored_connections SET {', '.join(updates)} WHERE id = ?"
    )

    conn = database.get_connection()
    if database.is_postgresql():
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(query, tuple(params))
    else:
        conn.execute(query, tuple(params))

    return get_stored_connection(connection_id)


def delete_stored_connection(connection_id: str) -> bool:
    """Delete a stored connection."""
    conn = database.get_connection()
    query = database.adapt_query("DELETE FROM stored_connections WHERE id = ?")

    if database.is_postgresql():
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(query, (connection_id,))
            return bool(cur.rowcount > 0)
    else:
        cursor = conn.execute(query, (connection_id,))
        return bool(cursor.rowcount > 0)


def get_connection_credentials(connection_id: str) -> Optional[Dict[str, Any]]:
    """Get full connection credentials (including decrypted password).

    This should only be called internally for making actual connections.
    """
    row = database.fetchone(
        "SELECT * FROM stored_connections WHERE id = ?",
        (connection_id,)
    )
    if not row:
        return None

    # Decrypt password
    import base64
    password = None
    if row.get("password_encrypted"):
        password = base64.b64decode(row["password_encrypted"]).decode()

    additional_config = {}
    if row.get("additional_config"):
        if isinstance(row["additional_config"], str):
            additional_config = json.loads(row["additional_config"])
        else:
            additional_config = row["additional_config"]

    return {
        "id": row["id"],
        "connection_type": row["connection_type"],
        "host": row["host"],
        "port": row.get("port"),
        "database": row.get("database_name"),
        "username": row.get("username"),
        "password": password,
        "ssl_enabled": bool(row.get("ssl_enabled", True)),
        "additional_config": additional_config
    }


def _row_to_stored_connection(row: Dict[str, Any]) -> StoredConnection:
    """Convert a database row to a StoredConnection model."""
    is_active = row.get("is_active", True)
    ssl_enabled = row.get("ssl_enabled", True)
    if isinstance(is_active, int):
        is_active = bool(is_active)
    if isinstance(ssl_enabled, int):
        ssl_enabled = bool(ssl_enabled)

    last_used_at = None
    if row.get("last_used_at"):
        last_used_at = datetime.fromisoformat(row["last_used_at"])

    return StoredConnection(
        id=row["id"],
        org_id=row["org_id"],
        name=row["name"],
        connection_type=StoredConnectionType(row["connection_type"]),
        host=row["host"],
        port=row.get("port"),
        database=row.get("database_name"),
        username=_mask_username(row.get("username")),
        ssl_enabled=ssl_enabled,
        is_active=is_active,
        created_by=row.get("created_by"),
        created_at=datetime.fromisoformat(row["created_at"]),
        last_used_at=last_used_at
    )


def _mask_username(username: Optional[str]) -> Optional[str]:
    """Mask username for display (show first 2 and last 2 chars)."""
    if not username or len(username) <= 4:
        return username
    return f"{username[:2]}***{username[-2:]}"


# =============================================================================
# Output Delivery Logging
# =============================================================================

def log_delivery_start(
    run_id: str,
    destination_id: str,
    destination_type: str,
    destination_name: str
) -> str:
    """Log the start of an output delivery attempt."""
    delivery_id = f"del-{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    conn = database.get_connection()
    query = database.adapt_query("""
        INSERT INTO output_deliveries (
            id, run_id, destination_id, destination_type, destination_name,
            status, attempt_count, started_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """)

    if database.is_postgresql():
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(query, (
                delivery_id, run_id, destination_id, destination_type,
                destination_name, "pending", 1, now
            ))
    else:
        conn.execute(query, (
            delivery_id, run_id, destination_id, destination_type,
            destination_name, "pending", 1, now
        ))

    return delivery_id


def log_delivery_success(
    delivery_id: str,
    response_code: Optional[int] = None,
    response_body: Optional[str] = None,
    payload_size: Optional[int] = None
) -> None:
    """Log a successful delivery."""
    now = datetime.utcnow().isoformat()

    # Calculate duration
    delivery = _get_delivery_row(delivery_id)
    duration_ms = None
    if delivery and delivery.get("started_at"):
        started = datetime.fromisoformat(delivery["started_at"])
        duration_ms = int((datetime.utcnow() - started).total_seconds() * 1000)

    conn = database.get_connection()
    query = database.adapt_query("""
        UPDATE output_deliveries SET
            status = ?, response_code = ?, response_body = ?,
            payload_size_bytes = ?, completed_at = ?, duration_ms = ?
        WHERE id = ?
    """)

    # Truncate response body if too long
    if response_body and len(response_body) > 1000:
        response_body = response_body[:1000] + "... (truncated)"

    params = ("success", response_code, response_body, payload_size, now, duration_ms, delivery_id)

    if database.is_postgresql():
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(query, params)
    else:
        conn.execute(query, params)


def log_delivery_failure(
    delivery_id: str,
    error_message: str,
    response_code: Optional[int] = None,
    response_body: Optional[str] = None,
    will_retry: bool = False
) -> None:
    """Log a failed delivery."""
    now = datetime.utcnow().isoformat()
    status = "retrying" if will_retry else "failed"

    # Get current attempt count
    delivery = _get_delivery_row(delivery_id)
    attempt_count = 1
    duration_ms = None
    if delivery:
        attempt_count = delivery.get("attempt_count", 1)
        if will_retry:
            attempt_count += 1
        if delivery.get("started_at"):
            started = datetime.fromisoformat(delivery["started_at"])
            duration_ms = int((datetime.utcnow() - started).total_seconds() * 1000)

    conn = database.get_connection()
    query = database.adapt_query("""
        UPDATE output_deliveries SET
            status = ?, error_message = ?, response_code = ?, response_body = ?,
            attempt_count = ?, completed_at = ?, duration_ms = ?
        WHERE id = ?
    """)

    # Truncate response body if too long
    if response_body and len(response_body) > 1000:
        response_body = response_body[:1000] + "... (truncated)"

    params = (status, error_message, response_code, response_body, attempt_count, now, duration_ms, delivery_id)

    if database.is_postgresql():
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(query, params)
    else:
        conn.execute(query, params)


def get_deliveries_for_run(run_id: str) -> List[OutputDeliveryLog]:
    """Get all delivery logs for a pipeline run."""
    rows = database.fetchall(
        "SELECT * FROM output_deliveries WHERE run_id = ? ORDER BY started_at",
        (run_id,)
    )
    return [_row_to_delivery_log(row) for row in rows]


def _get_delivery_row(delivery_id: str) -> Optional[Dict[str, Any]]:
    """Get raw delivery row."""
    return database.fetchone(
        "SELECT * FROM output_deliveries WHERE id = ?",
        (delivery_id,)
    )


def _row_to_delivery_log(row: Dict[str, Any]) -> OutputDeliveryLog:
    """Convert a database row to an OutputDeliveryLog model."""
    completed_at = None
    if row.get("completed_at"):
        completed_at = datetime.fromisoformat(row["completed_at"])

    return OutputDeliveryLog(
        id=row["id"],
        run_id=row["run_id"],
        destination_id=row["destination_id"],
        destination_type=row["destination_type"],
        destination_name=row["destination_name"],
        status=OutputDeliveryStatus(row["status"]),
        attempt_count=row.get("attempt_count", 1),
        response_code=row.get("response_code"),
        response_body=row.get("response_body"),
        error_message=row.get("error_message"),
        payload_size_bytes=row.get("payload_size_bytes"),
        started_at=datetime.fromisoformat(row["started_at"]),
        completed_at=completed_at,
        duration_ms=row.get("duration_ms")
    )
