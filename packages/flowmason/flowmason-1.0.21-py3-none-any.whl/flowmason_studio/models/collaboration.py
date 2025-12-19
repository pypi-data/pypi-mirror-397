"""
Real-time Collaboration Models.

Models for collaborative pipeline editing with multiple users.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """Role of a user in a collaboration session."""

    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class PresenceStatus(str, Enum):
    """User presence status."""

    ONLINE = "online"
    AWAY = "away"
    OFFLINE = "offline"


class CursorPosition(BaseModel):
    """Position of a user's cursor on the canvas."""

    x: float
    y: float
    viewport_x: float = 0
    viewport_y: float = 0
    zoom: float = 1.0


class UserCursor(BaseModel):
    """A user's cursor state in a collaboration session."""

    user_id: str
    position: CursorPosition
    selected_stage: Optional[str] = None
    selected_connection: Optional[str] = None
    color: str = Field(default="#6366f1", description="Cursor color (hex)")
    last_updated: str


class UserPresence(BaseModel):
    """User presence information in a session."""

    user_id: str
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole
    status: PresenceStatus
    cursor: Optional[UserCursor] = None
    joined_at: str
    last_active: str
    color: str = Field(description="Assigned color for this user")


class EditOperation(str, Enum):
    """Types of edit operations."""

    # Stage operations
    ADD_STAGE = "add_stage"
    REMOVE_STAGE = "remove_stage"
    UPDATE_STAGE = "update_stage"
    MOVE_STAGE = "move_stage"

    # Connection operations
    ADD_CONNECTION = "add_connection"
    REMOVE_CONNECTION = "remove_connection"

    # Pipeline operations
    UPDATE_PIPELINE = "update_pipeline"
    UPDATE_SETTINGS = "update_settings"

    # Selection operations
    SELECT = "select"
    DESELECT = "deselect"


class EditChange(BaseModel):
    """A single edit change in the pipeline."""

    id: str
    operation: EditOperation
    target_id: Optional[str] = Field(
        default=None,
        description="ID of the affected stage/connection"
    )
    data: Dict[str, Any] = Field(default_factory=dict)
    user_id: str
    timestamp: str
    version: int = Field(description="Pipeline version after this change")


class EditConflict(BaseModel):
    """A conflict between concurrent edits."""

    id: str
    change_a: EditChange
    change_b: EditChange
    conflict_type: str
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None


class CollaborationSession(BaseModel):
    """A collaboration session for a pipeline."""

    id: str
    pipeline_id: str
    created_at: str
    created_by: str
    is_active: bool = True

    # Participants
    participants: List[UserPresence] = Field(default_factory=list)
    max_participants: int = Field(default=10)

    # State
    current_version: int = Field(default=1)
    last_modified: str
    last_modified_by: Optional[str] = None

    # Settings
    auto_save: bool = Field(default=True)
    auto_save_interval: int = Field(
        default=30,
        description="Auto-save interval in seconds"
    )
    allow_anonymous: bool = Field(default=False)
    require_approval: bool = Field(
        default=False,
        description="Require owner approval to join"
    )


class SessionInvite(BaseModel):
    """An invitation to join a collaboration session."""

    id: str
    session_id: str
    invited_email: str
    invited_by: str
    role: UserRole
    created_at: str
    expires_at: str
    accepted: bool = False
    accepted_at: Optional[str] = None


class ChatMessage(BaseModel):
    """A chat message in a collaboration session."""

    id: str
    session_id: str
    user_id: str
    username: str
    content: str
    timestamp: str
    reply_to: Optional[str] = None
    mentions: List[str] = Field(default_factory=list)
    reactions: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Emoji to list of user IDs"
    )


class Comment(BaseModel):
    """A comment attached to a pipeline element."""

    id: str
    session_id: str
    target_type: str = Field(description="stage, connection, or pipeline")
    target_id: str
    user_id: str
    username: str
    content: str
    created_at: str
    updated_at: Optional[str] = None
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None
    replies: List["CommentReply"] = Field(default_factory=list)


class CommentReply(BaseModel):
    """A reply to a comment."""

    id: str
    comment_id: str
    user_id: str
    username: str
    content: str
    created_at: str


class SessionActivity(BaseModel):
    """Activity log entry for a session."""

    id: str
    session_id: str
    user_id: str
    username: str
    activity_type: str
    description: str
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LockState(BaseModel):
    """Lock state for a pipeline element."""

    target_id: str
    target_type: str
    locked_by: str
    locked_at: str
    expires_at: str
    reason: Optional[str] = None


class UndoRedoState(BaseModel):
    """Undo/redo state for a user in a session."""

    user_id: str
    undo_stack: List[EditChange] = Field(default_factory=list)
    redo_stack: List[EditChange] = Field(default_factory=list)
    max_history: int = Field(default=50)


# API Request/Response Models

class CreateSessionRequest(BaseModel):
    """Request to create a collaboration session."""

    pipeline_id: str
    max_participants: int = Field(default=10, ge=2, le=50)
    auto_save: bool = True
    allow_anonymous: bool = False
    require_approval: bool = False


class CreateSessionResponse(BaseModel):
    """Response with created session."""

    session: CollaborationSession
    join_url: str
    invite_code: str


class JoinSessionRequest(BaseModel):
    """Request to join a session."""

    session_id: Optional[str] = None
    invite_code: Optional[str] = None
    username: Optional[str] = None


class JoinSessionResponse(BaseModel):
    """Response after joining a session."""

    session: CollaborationSession
    user: UserPresence
    token: str = Field(description="WebSocket auth token")


class InviteUserRequest(BaseModel):
    """Request to invite a user."""

    email: str
    role: UserRole = UserRole.EDITOR
    message: Optional[str] = None


class UpdatePresenceRequest(BaseModel):
    """Request to update user presence."""

    status: Optional[PresenceStatus] = None
    cursor: Optional[CursorPosition] = None
    selected_stage: Optional[str] = None
    selected_connection: Optional[str] = None


class SendEditRequest(BaseModel):
    """Request to send an edit operation."""

    operation: EditOperation
    target_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    base_version: int = Field(description="Version this edit is based on")


class SendEditResponse(BaseModel):
    """Response after sending an edit."""

    success: bool
    change: Optional[EditChange] = None
    conflict: Optional[EditConflict] = None
    new_version: int


class SendChatRequest(BaseModel):
    """Request to send a chat message."""

    content: str = Field(..., min_length=1, max_length=2000)
    reply_to: Optional[str] = None
    mentions: List[str] = Field(default_factory=list)


class AddCommentRequest(BaseModel):
    """Request to add a comment."""

    target_type: str
    target_id: str
    content: str = Field(..., min_length=1, max_length=5000)


class ResolveCommentRequest(BaseModel):
    """Request to resolve a comment."""

    comment_id: str


class AcquireLockRequest(BaseModel):
    """Request to acquire a lock."""

    target_id: str
    target_type: str
    duration: int = Field(default=300, description="Lock duration in seconds")
    reason: Optional[str] = None


# WebSocket Message Types

class WSMessageType(str, Enum):
    """WebSocket message types for collaboration."""

    # Connection
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"

    # Presence
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    PRESENCE_UPDATE = "presence_update"
    CURSOR_MOVE = "cursor_move"

    # Edits
    EDIT = "edit"
    EDIT_ACK = "edit_ack"
    EDIT_CONFLICT = "edit_conflict"
    SYNC = "sync"

    # Chat
    CHAT_MESSAGE = "chat_message"
    TYPING = "typing"

    # Comments
    COMMENT_ADDED = "comment_added"
    COMMENT_RESOLVED = "comment_resolved"

    # Locks
    LOCK_ACQUIRED = "lock_acquired"
    LOCK_RELEASED = "lock_released"
    LOCK_EXPIRED = "lock_expired"


class WSMessage(BaseModel):
    """A WebSocket message for collaboration."""

    type: WSMessageType
    session_id: str
    user_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


# Update forward references
Comment.model_rebuild()
