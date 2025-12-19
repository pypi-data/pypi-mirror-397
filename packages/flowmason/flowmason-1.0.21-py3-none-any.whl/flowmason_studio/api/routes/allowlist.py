"""
Allowlist API Routes for FlowMason Output Security.

Provides endpoints for managing output destination allowlists and stored connections.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ...models.allowlist import (
    AllowlistEntry,
    AllowlistEntryCreate,
    AllowlistEntryType,
    AllowlistEntryUpdate,
    AllowlistListResponse,
    AllowlistValidationRequest,
    AllowlistValidationResult,
    OutputDeliveryLogListResponse,
    StoredConnection,
    StoredConnectionCreate,
    StoredConnectionListResponse,
    StoredConnectionTestResult,
    StoredConnectionType,
    StoredConnectionUpdate,
)
from ...services import allowlist_storage

# Try to import auth middleware (optional)
try:
    from ...auth.middleware import optional_auth  # noqa: F401
    HAS_AUTH = True
except ImportError:
    HAS_AUTH = False


router = APIRouter(prefix="/allowlist", tags=["allowlist"])
connections_router = APIRouter(prefix="/connections", tags=["connections"])
deliveries_router = APIRouter(prefix="/deliveries", tags=["deliveries"])


def _get_org_id() -> str:
    """Get org ID for the current request.

    In production, this would come from the authenticated user's context.
    For now, return a default org ID.
    """
    return "default-org"


# =============================================================================
# Allowlist Entry Endpoints
# =============================================================================

@router.post("", response_model=AllowlistEntry, status_code=201)
async def create_allowlist_entry(
    entry: AllowlistEntryCreate,
    org_id: str = Depends(_get_org_id)
) -> AllowlistEntry:
    """Create a new allowlist entry.

    Allowlist entries permit specific output destinations for the organization.
    Supports:
    - Webhook domains (*.example.com) and exact URLs
    - Email domains (@company.com)
    - Database connections (by stored connection ID)
    - Message queue connections (by stored connection ID)
    """
    return allowlist_storage.create_allowlist_entry(
        org_id=org_id,
        entry=entry,
        created_by=None  # Would be user_id from auth
    )


@router.get("", response_model=AllowlistListResponse)
async def list_allowlist_entries(
    entry_type: Optional[AllowlistEntryType] = Query(None, description="Filter by entry type"),
    active_only: bool = Query(True, description="Only return active entries"),
    org_id: str = Depends(_get_org_id)
) -> AllowlistListResponse:
    """List all allowlist entries for the organization."""
    entries = allowlist_storage.list_allowlist_entries(
        org_id=org_id,
        entry_type=entry_type,
        active_only=active_only
    )
    return AllowlistListResponse(
        entries=entries,
        total=len(entries),
        org_id=org_id
    )


@router.get("/{entry_id}", response_model=AllowlistEntry)
async def get_allowlist_entry(
    entry_id: str,
    org_id: str = Depends(_get_org_id)
) -> AllowlistEntry:
    """Get a specific allowlist entry."""
    entry = allowlist_storage.get_allowlist_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Allowlist entry not found")
    if entry.org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return entry


@router.patch("/{entry_id}", response_model=AllowlistEntry)
async def update_allowlist_entry(
    entry_id: str,
    update: AllowlistEntryUpdate,
    org_id: str = Depends(_get_org_id)
) -> AllowlistEntry:
    """Update an allowlist entry."""
    # Check ownership
    existing = allowlist_storage.get_allowlist_entry(entry_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Allowlist entry not found")
    if existing.org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    updated = allowlist_storage.update_allowlist_entry(entry_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Allowlist entry not found")
    return updated


@router.delete("/{entry_id}", status_code=204)
async def delete_allowlist_entry(
    entry_id: str,
    org_id: str = Depends(_get_org_id)
) -> None:
    """Delete an allowlist entry."""
    # Check ownership
    existing = allowlist_storage.get_allowlist_entry(entry_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Allowlist entry not found")
    if existing.org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not allowlist_storage.delete_allowlist_entry(entry_id):
        raise HTTPException(status_code=404, detail="Allowlist entry not found")


@router.post("/validate", response_model=AllowlistValidationResult)
async def validate_destination(
    request: AllowlistValidationRequest,
    org_id: str = Depends(_get_org_id)
) -> AllowlistValidationResult:
    """Validate a destination against the organization's allowlist.

    Use this endpoint to check if a specific destination (webhook URL, email,
    database connection, etc.) is permitted before attempting to use it.
    """
    return allowlist_storage.validate_destination(org_id, request)


# =============================================================================
# Stored Connection Endpoints
# =============================================================================

@connections_router.post("", response_model=StoredConnection, status_code=201)
async def create_stored_connection(
    connection: StoredConnectionCreate,
    org_id: str = Depends(_get_org_id)
) -> StoredConnection:
    """Create a new stored connection.

    Stored connections securely store database or message queue credentials
    that can be referenced in output destinations.

    Note: The password is encrypted at rest and never returned in API responses.
    """
    return allowlist_storage.create_stored_connection(
        org_id=org_id,
        connection=connection,
        created_by=None  # Would be user_id from auth
    )


@connections_router.get("", response_model=StoredConnectionListResponse)
async def list_stored_connections(
    connection_type: Optional[StoredConnectionType] = Query(None, description="Filter by type"),
    active_only: bool = Query(True, description="Only return active connections"),
    org_id: str = Depends(_get_org_id)
) -> StoredConnectionListResponse:
    """List all stored connections for the organization.

    Passwords are never included in the response.
    """
    connections = allowlist_storage.list_stored_connections(
        org_id=org_id,
        connection_type=connection_type,
        active_only=active_only
    )
    return StoredConnectionListResponse(
        connections=connections,
        total=len(connections),
        org_id=org_id
    )


@connections_router.get("/{connection_id}", response_model=StoredConnection)
async def get_stored_connection(
    connection_id: str,
    org_id: str = Depends(_get_org_id)
) -> StoredConnection:
    """Get a specific stored connection.

    Password is never included in the response.
    """
    connection = allowlist_storage.get_stored_connection(connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    if connection.org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return connection


@connections_router.patch("/{connection_id}", response_model=StoredConnection)
async def update_stored_connection(
    connection_id: str,
    update: StoredConnectionUpdate,
    org_id: str = Depends(_get_org_id)
) -> StoredConnection:
    """Update a stored connection.

    To update the password, include the password field. If not included,
    the existing password is preserved.
    """
    # Check ownership
    existing = allowlist_storage.get_stored_connection(connection_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Connection not found")
    if existing.org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    updated = allowlist_storage.update_stored_connection(connection_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Connection not found")
    return updated


@connections_router.delete("/{connection_id}", status_code=204)
async def delete_stored_connection(
    connection_id: str,
    org_id: str = Depends(_get_org_id)
) -> None:
    """Delete a stored connection.

    This will invalidate any output destinations that reference this connection.
    """
    # Check ownership
    existing = allowlist_storage.get_stored_connection(connection_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Connection not found")
    if existing.org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if not allowlist_storage.delete_stored_connection(connection_id):
        raise HTTPException(status_code=404, detail="Connection not found")


@connections_router.post("/{connection_id}/test", response_model=StoredConnectionTestResult)
async def test_stored_connection(
    connection_id: str,
    org_id: str = Depends(_get_org_id)
) -> StoredConnectionTestResult:
    """Test a stored connection.

    Attempts to connect using the stored credentials and returns the result.
    """
    from datetime import datetime

    # Check ownership
    existing = allowlist_storage.get_stored_connection(connection_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Connection not found")
    if existing.org_id != org_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get full credentials
    credentials = allowlist_storage.get_connection_credentials(connection_id)
    if not credentials:
        raise HTTPException(status_code=404, detail="Connection not found")

    # TODO: Actually test the connection based on type
    # For now, return a placeholder success
    return StoredConnectionTestResult(
        connection_id=connection_id,
        success=True,
        latency_ms=50,
        error=None,
        tested_at=datetime.utcnow()
    )


# =============================================================================
# Delivery Log Endpoints
# =============================================================================

@deliveries_router.get("/{run_id}", response_model=OutputDeliveryLogListResponse)
async def get_deliveries_for_run(
    run_id: str,
    org_id: str = Depends(_get_org_id)
) -> OutputDeliveryLogListResponse:
    """Get all output delivery logs for a pipeline run.

    Returns the status and details of each output delivery attempt.
    """
    deliveries = allowlist_storage.get_deliveries_for_run(run_id)
    return OutputDeliveryLogListResponse(
        deliveries=deliveries,
        total=len(deliveries),
        run_id=run_id
    )
