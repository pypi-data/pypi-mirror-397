"""
Allowlist Models for FlowMason Output Security.

These models define the allowlist system that controls which output
destinations are permitted for each organization. This provides security
by requiring pre-approval of webhook URLs, email domains, database
connections, and message queue endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# =============================================================================
# Allowlist Entry Types
# =============================================================================

class AllowlistEntryType(str, Enum):
    """Type of allowlist entry."""
    WEBHOOK_DOMAIN = "webhook_domain"      # Allow *.example.com
    WEBHOOK_URL = "webhook_url"            # Allow exact URL
    EMAIL_DOMAIN = "email_domain"          # Allow @example.com
    DATABASE_CONNECTION = "database_connection"      # Allow stored connection
    MESSAGE_QUEUE_CONNECTION = "message_queue_connection"  # Allow stored MQ connection


# =============================================================================
# Allowlist Entry Models
# =============================================================================

class AllowlistEntryCreate(BaseModel):
    """Request to create a new allowlist entry."""
    entry_type: AllowlistEntryType = Field(description="Type of entry")
    pattern: str = Field(
        description="Pattern to match (e.g., '*.example.com', 'https://api.example.com/webhook', '@company.com')"
    )
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of why this entry was added"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Optional expiration date for temporary approvals"
    )


class AllowlistEntry(BaseModel):
    """An allowlist entry that permits a specific output destination."""
    id: str = Field(description="Unique entry identifier")
    org_id: str = Field(description="Organization this entry belongs to")
    entry_type: AllowlistEntryType = Field(description="Type of entry")
    pattern: str = Field(
        description="Pattern to match against destinations"
    )
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description"
    )
    is_active: bool = Field(default=True, description="Whether entry is currently active")
    created_by: Optional[str] = Field(default=None, description="User who created this entry")
    created_at: datetime = Field(description="When entry was created")
    expires_at: Optional[datetime] = Field(
        default=None,
        description="When entry expires (null = never)"
    )


class AllowlistEntryUpdate(BaseModel):
    """Request to update an allowlist entry."""
    pattern: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class AllowlistListResponse(BaseModel):
    """Response for listing allowlist entries."""
    entries: List[AllowlistEntry]
    total: int
    org_id: str


# =============================================================================
# Validation Models
# =============================================================================

class AllowlistValidationRequest(BaseModel):
    """Request to validate a destination against the allowlist."""
    destination_type: str = Field(description="Type of destination (webhook, email, etc.)")
    destination_value: str = Field(
        description="Value to validate (URL, email, connection_id)"
    )


class AllowlistValidationResult(BaseModel):
    """Result of validating a destination against the allowlist."""
    is_allowed: bool = Field(description="Whether the destination is permitted")
    matched_entry_id: Optional[str] = Field(
        default=None,
        description="ID of the allowlist entry that matched (if allowed)"
    )
    matched_pattern: Optional[str] = Field(
        default=None,
        description="Pattern that matched (if allowed)"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Reason for denial (if not allowed)"
    )


# =============================================================================
# Stored Connection Models
# =============================================================================

class StoredConnectionType(str, Enum):
    """Type of stored connection."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    SQS = "sqs"
    REDIS = "redis"


class StoredConnectionCreate(BaseModel):
    """Request to create a stored connection (credentials stored securely)."""
    name: str = Field(description="Human-readable connection name")
    connection_type: StoredConnectionType = Field(description="Type of connection")
    host: str = Field(description="Host/endpoint")
    port: Optional[int] = Field(default=None, description="Port number")
    database: Optional[str] = Field(default=None, description="Database name")
    username: Optional[str] = Field(default=None, description="Username")
    password: Optional[str] = Field(default=None, description="Password (will be encrypted)")
    ssl_enabled: bool = Field(default=True, description="Use SSL/TLS")
    additional_config: dict = Field(
        default_factory=dict,
        description="Additional type-specific configuration"
    )


class StoredConnection(BaseModel):
    """A stored database or message queue connection."""
    id: str = Field(description="Unique connection identifier")
    org_id: str = Field(description="Organization this connection belongs to")
    name: str = Field(description="Human-readable name")
    connection_type: StoredConnectionType = Field(description="Type of connection")
    host: str = Field(description="Host/endpoint (may be masked)")
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = Field(default=None, description="Username (masked)")
    ssl_enabled: bool = True
    is_active: bool = Field(default=True, description="Whether connection is active")
    created_by: Optional[str] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None
    # Note: password is NEVER returned in responses


class StoredConnectionUpdate(BaseModel):
    """Request to update a stored connection."""
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None  # Only set if changing password
    ssl_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    additional_config: Optional[dict] = None


class StoredConnectionListResponse(BaseModel):
    """Response for listing stored connections."""
    connections: List[StoredConnection]
    total: int
    org_id: str


class StoredConnectionTestResult(BaseModel):
    """Result of testing a stored connection."""
    connection_id: str
    success: bool
    latency_ms: Optional[int] = None
    error: Optional[str] = None
    tested_at: datetime


# =============================================================================
# Output Delivery Log Models
# =============================================================================

class OutputDeliveryStatus(str, Enum):
    """Status of an output delivery attempt."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class OutputDeliveryLog(BaseModel):
    """Log entry for a single output delivery attempt."""
    id: str = Field(description="Unique delivery log identifier")
    run_id: str = Field(description="Pipeline run this delivery belongs to")
    destination_id: str = Field(description="Destination that was targeted")
    destination_type: str = Field(description="Type of destination")
    destination_name: str = Field(description="Name of destination")
    status: OutputDeliveryStatus
    attempt_count: int = Field(default=1, description="Number of delivery attempts")
    response_code: Optional[int] = Field(default=None, description="HTTP status code (for webhooks)")
    response_body: Optional[str] = Field(default=None, description="Response body (truncated)")
    error_message: Optional[str] = None
    payload_size_bytes: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


class OutputDeliveryLogListResponse(BaseModel):
    """Response for listing delivery logs."""
    deliveries: List[OutputDeliveryLog]
    total: int
    run_id: Optional[str] = None


# =============================================================================
# Summary Exports
# =============================================================================

__all__ = [
    # Enums
    "AllowlistEntryType",
    "StoredConnectionType",
    "OutputDeliveryStatus",
    # Allowlist models
    "AllowlistEntry",
    "AllowlistEntryCreate",
    "AllowlistEntryUpdate",
    "AllowlistListResponse",
    "AllowlistValidationRequest",
    "AllowlistValidationResult",
    # Connection models
    "StoredConnection",
    "StoredConnectionCreate",
    "StoredConnectionUpdate",
    "StoredConnectionListResponse",
    "StoredConnectionTestResult",
    # Delivery models
    "OutputDeliveryLog",
    "OutputDeliveryLogListResponse",
]
