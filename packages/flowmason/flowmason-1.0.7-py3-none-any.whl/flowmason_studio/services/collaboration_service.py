"""
Real-time Collaboration Service.

Manages collaborative pipeline editing sessions.
"""

import asyncio
import secrets
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set

from flowmason_studio.models.collaboration import (
    AcquireLockRequest,
    ChatMessage,
    CollaborationSession,
    Comment,
    CommentReply,
    CursorPosition,
    EditChange,
    EditConflict,
    EditOperation,
    LockState,
    PresenceStatus,
    SendEditResponse,
    SessionActivity,
    SessionInvite,
    UndoRedoState,
    UserCursor,
    UserPresence,
    UserRole,
    WSMessage,
    WSMessageType,
)

# User colors for visual distinction
USER_COLORS = [
    "#ef4444",  # Red
    "#f97316",  # Orange
    "#eab308",  # Yellow
    "#22c55e",  # Green
    "#06b6d4",  # Cyan
    "#3b82f6",  # Blue
    "#8b5cf6",  # Violet
    "#ec4899",  # Pink
    "#14b8a6",  # Teal
    "#f59e0b",  # Amber
]


class CollaborationService:
    """Service for managing real-time collaboration sessions."""

    def __init__(self):
        """Initialize the collaboration service."""
        self._sessions: Dict[str, CollaborationSession] = {}
        self._invites: Dict[str, SessionInvite] = {}
        self._invite_codes: Dict[str, str] = {}  # code -> session_id
        self._changes: Dict[str, List[EditChange]] = {}  # session_id -> changes
        self._comments: Dict[str, List[Comment]] = {}  # session_id -> comments
        self._chat_messages: Dict[str, List[ChatMessage]] = {}
        self._activities: Dict[str, List[SessionActivity]] = {}
        self._locks: Dict[str, Dict[str, LockState]] = {}  # session_id -> {target_id: lock}
        self._undo_redo: Dict[str, Dict[str, UndoRedoState]] = {}  # session_id -> {user_id: state}
        self._user_color_index: Dict[str, int] = {}  # session_id -> next color index
        self._broadcast_handlers: Dict[str, List[Callable]] = {}

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return secrets.token_urlsafe(16)

    def _generate_invite_code(self) -> str:
        """Generate a human-readable invite code."""
        return secrets.token_urlsafe(8).upper()[:8]

    def _now(self) -> str:
        """Get current ISO timestamp."""
        return datetime.utcnow().isoformat() + "Z"

    def _get_user_color(self, session_id: str) -> str:
        """Get next available color for a user."""
        if session_id not in self._user_color_index:
            self._user_color_index[session_id] = 0

        color = USER_COLORS[self._user_color_index[session_id] % len(USER_COLORS)]
        self._user_color_index[session_id] += 1
        return color

    # =========================================================================
    # Session Management
    # =========================================================================

    def create_session(
        self,
        pipeline_id: str,
        user_id: str,
        username: str,
        email: Optional[str] = None,
        max_participants: int = 10,
        auto_save: bool = True,
        allow_anonymous: bool = False,
        require_approval: bool = False,
    ) -> tuple[CollaborationSession, str]:
        """
        Create a new collaboration session.

        Returns:
            Tuple of (session, invite_code)
        """
        session_id = self._generate_id()
        invite_code = self._generate_invite_code()
        now = self._now()

        # Create owner presence
        owner = UserPresence(
            user_id=user_id,
            username=username,
            email=email,
            role=UserRole.OWNER,
            status=PresenceStatus.ONLINE,
            joined_at=now,
            last_active=now,
            color=self._get_user_color(session_id),
        )

        session = CollaborationSession(
            id=session_id,
            pipeline_id=pipeline_id,
            created_at=now,
            created_by=user_id,
            participants=[owner],
            max_participants=max_participants,
            last_modified=now,
            auto_save=auto_save,
            allow_anonymous=allow_anonymous,
            require_approval=require_approval,
        )

        self._sessions[session_id] = session
        self._invite_codes[invite_code] = session_id
        self._changes[session_id] = []
        self._comments[session_id] = []
        self._chat_messages[session_id] = []
        self._activities[session_id] = []
        self._locks[session_id] = {}
        self._undo_redo[session_id] = {user_id: UndoRedoState(user_id=user_id)}

        # Log activity
        self._log_activity(
            session_id=session_id,
            user_id=user_id,
            username=username,
            activity_type="session_created",
            description=f"{username} created the collaboration session",
        )

        return session, invite_code

    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def get_session_by_invite_code(self, invite_code: str) -> Optional[CollaborationSession]:
        """Get a session by invite code."""
        session_id = self._invite_codes.get(invite_code.upper())
        if session_id:
            return self._sessions.get(session_id)
        return None

    def join_session(
        self,
        session_id: str,
        user_id: str,
        username: str,
        email: Optional[str] = None,
        role: UserRole = UserRole.EDITOR,
    ) -> Optional[UserPresence]:
        """
        Join an existing session.

        Returns:
            UserPresence for the new participant, or None if failed
        """
        session = self._sessions.get(session_id)
        if not session or not session.is_active:
            return None

        # Check max participants
        if len(session.participants) >= session.max_participants:
            return None

        # Check if user already in session
        existing = next((p for p in session.participants if p.user_id == user_id), None)
        if existing:
            existing.status = PresenceStatus.ONLINE
            existing.last_active = self._now()
            return existing

        now = self._now()
        user = UserPresence(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            status=PresenceStatus.ONLINE,
            joined_at=now,
            last_active=now,
            color=self._get_user_color(session_id),
        )

        session.participants.append(user)
        self._undo_redo[session_id][user_id] = UndoRedoState(user_id=user_id)

        # Log activity
        self._log_activity(
            session_id=session_id,
            user_id=user_id,
            username=username,
            activity_type="user_joined",
            description=f"{username} joined the session",
        )

        return user

    def leave_session(self, session_id: str, user_id: str) -> bool:
        """Leave a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        participant = next((p for p in session.participants if p.user_id == user_id), None)
        if not participant:
            return False

        participant.status = PresenceStatus.OFFLINE
        participant.last_active = self._now()

        # Release any locks held by this user
        if session_id in self._locks:
            locks_to_release = [
                target_id for target_id, lock in self._locks[session_id].items()
                if lock.locked_by == user_id
            ]
            for target_id in locks_to_release:
                del self._locks[session_id][target_id]

        # Log activity
        self._log_activity(
            session_id=session_id,
            user_id=user_id,
            username=participant.username,
            activity_type="user_left",
            description=f"{participant.username} left the session",
        )

        return True

    def end_session(self, session_id: str, user_id: str) -> bool:
        """End a session (owner only)."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        # Check if user is owner
        owner = next((p for p in session.participants if p.user_id == user_id), None)
        if not owner or owner.role != UserRole.OWNER:
            return False

        session.is_active = False

        # Log activity
        self._log_activity(
            session_id=session_id,
            user_id=user_id,
            username=owner.username,
            activity_type="session_ended",
            description=f"{owner.username} ended the session",
        )

        return True

    # =========================================================================
    # Presence
    # =========================================================================

    def update_presence(
        self,
        session_id: str,
        user_id: str,
        status: Optional[PresenceStatus] = None,
        cursor: Optional[CursorPosition] = None,
        selected_stage: Optional[str] = None,
        selected_connection: Optional[str] = None,
    ) -> Optional[UserPresence]:
        """Update user presence in a session."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        participant = next((p for p in session.participants if p.user_id == user_id), None)
        if not participant:
            return None

        now = self._now()

        if status is not None:
            participant.status = status

        if cursor is not None:
            participant.cursor = UserCursor(
                user_id=user_id,
                position=cursor,
                selected_stage=selected_stage,
                selected_connection=selected_connection,
                color=participant.color,
                last_updated=now,
            )
        elif selected_stage is not None or selected_connection is not None:
            if participant.cursor:
                participant.cursor.selected_stage = selected_stage
                participant.cursor.selected_connection = selected_connection
                participant.cursor.last_updated = now

        participant.last_active = now
        return participant

    def get_online_users(self, session_id: str) -> List[UserPresence]:
        """Get all online users in a session."""
        session = self._sessions.get(session_id)
        if not session:
            return []

        return [p for p in session.participants if p.status == PresenceStatus.ONLINE]

    # =========================================================================
    # Edits
    # =========================================================================

    def apply_edit(
        self,
        session_id: str,
        user_id: str,
        operation: EditOperation,
        target_id: Optional[str],
        data: Dict[str, Any],
        base_version: int,
    ) -> SendEditResponse:
        """
        Apply an edit operation.

        Uses Operational Transformation for conflict resolution.
        """
        session = self._sessions.get(session_id)
        if not session:
            return SendEditResponse(
                success=False,
                new_version=0,
            )

        # Check for conflicts
        if base_version != session.current_version:
            # Find conflicting changes
            conflicting = [
                c for c in self._changes[session_id]
                if c.version > base_version and c.target_id == target_id
            ]

            if conflicting:
                # Create conflict record
                conflict = EditConflict(
                    id=self._generate_id(),
                    change_a=conflicting[-1],
                    change_b=EditChange(
                        id=self._generate_id(),
                        operation=operation,
                        target_id=target_id,
                        data=data,
                        user_id=user_id,
                        timestamp=self._now(),
                        version=base_version,
                    ),
                    conflict_type="concurrent_edit",
                )

                return SendEditResponse(
                    success=False,
                    conflict=conflict,
                    new_version=session.current_version,
                )

        # Check locks
        if target_id and session_id in self._locks:
            lock = self._locks[session_id].get(target_id)
            if lock and lock.locked_by != user_id:
                # Check if lock expired
                if datetime.fromisoformat(lock.expires_at.rstrip("Z")) > datetime.utcnow():
                    return SendEditResponse(
                        success=False,
                        new_version=session.current_version,
                    )
                else:
                    # Lock expired, remove it
                    del self._locks[session_id][target_id]

        # Apply the edit
        session.current_version += 1
        now = self._now()

        change = EditChange(
            id=self._generate_id(),
            operation=operation,
            target_id=target_id,
            data=data,
            user_id=user_id,
            timestamp=now,
            version=session.current_version,
        )

        self._changes[session_id].append(change)
        session.last_modified = now
        session.last_modified_by = user_id

        # Update undo stack
        if session_id in self._undo_redo and user_id in self._undo_redo[session_id]:
            undo_state = self._undo_redo[session_id][user_id]
            undo_state.undo_stack.append(change)
            if len(undo_state.undo_stack) > undo_state.max_history:
                undo_state.undo_stack.pop(0)
            undo_state.redo_stack.clear()

        return SendEditResponse(
            success=True,
            change=change,
            new_version=session.current_version,
        )

    def get_changes_since(
        self,
        session_id: str,
        since_version: int,
    ) -> List[EditChange]:
        """Get all changes since a version."""
        if session_id not in self._changes:
            return []

        return [c for c in self._changes[session_id] if c.version > since_version]

    def undo(self, session_id: str, user_id: str) -> Optional[EditChange]:
        """Undo the last change by this user."""
        if session_id not in self._undo_redo:
            return None

        undo_state = self._undo_redo[session_id].get(user_id)
        if not undo_state or not undo_state.undo_stack:
            return None

        change = undo_state.undo_stack.pop()
        undo_state.redo_stack.append(change)
        return change

    def redo(self, session_id: str, user_id: str) -> Optional[EditChange]:
        """Redo the last undone change by this user."""
        if session_id not in self._undo_redo:
            return None

        undo_state = self._undo_redo[session_id].get(user_id)
        if not undo_state or not undo_state.redo_stack:
            return None

        change = undo_state.redo_stack.pop()
        undo_state.undo_stack.append(change)
        return change

    # =========================================================================
    # Locks
    # =========================================================================

    def acquire_lock(
        self,
        session_id: str,
        user_id: str,
        target_id: str,
        target_type: str,
        duration: int = 300,
        reason: Optional[str] = None,
    ) -> Optional[LockState]:
        """Acquire a lock on a pipeline element."""
        if session_id not in self._locks:
            self._locks[session_id] = {}

        existing = self._locks[session_id].get(target_id)
        if existing:
            # Check if expired
            if datetime.fromisoformat(existing.expires_at.rstrip("Z")) > datetime.utcnow():
                if existing.locked_by != user_id:
                    return None  # Already locked by someone else
            else:
                # Expired, can override
                pass

        now = datetime.utcnow()
        lock = LockState(
            target_id=target_id,
            target_type=target_type,
            locked_by=user_id,
            locked_at=now.isoformat() + "Z",
            expires_at=(now + timedelta(seconds=duration)).isoformat() + "Z",
            reason=reason,
        )

        self._locks[session_id][target_id] = lock
        return lock

    def release_lock(
        self,
        session_id: str,
        user_id: str,
        target_id: str,
    ) -> bool:
        """Release a lock on a pipeline element."""
        if session_id not in self._locks:
            return False

        lock = self._locks[session_id].get(target_id)
        if not lock or lock.locked_by != user_id:
            return False

        del self._locks[session_id][target_id]
        return True

    def get_locks(self, session_id: str) -> List[LockState]:
        """Get all active locks in a session."""
        if session_id not in self._locks:
            return []

        now = datetime.utcnow()
        active_locks = []

        for target_id, lock in list(self._locks[session_id].items()):
            if datetime.fromisoformat(lock.expires_at.rstrip("Z")) > now:
                active_locks.append(lock)
            else:
                # Clean up expired lock
                del self._locks[session_id][target_id]

        return active_locks

    # =========================================================================
    # Chat
    # =========================================================================

    def send_chat_message(
        self,
        session_id: str,
        user_id: str,
        username: str,
        content: str,
        reply_to: Optional[str] = None,
        mentions: Optional[List[str]] = None,
    ) -> Optional[ChatMessage]:
        """Send a chat message in the session."""
        if session_id not in self._chat_messages:
            return None

        message = ChatMessage(
            id=self._generate_id(),
            session_id=session_id,
            user_id=user_id,
            username=username,
            content=content,
            timestamp=self._now(),
            reply_to=reply_to,
            mentions=mentions or [],
        )

        self._chat_messages[session_id].append(message)
        return message

    def get_chat_messages(
        self,
        session_id: str,
        limit: int = 50,
        before: Optional[str] = None,
    ) -> List[ChatMessage]:
        """Get chat messages for a session."""
        if session_id not in self._chat_messages:
            return []

        messages = self._chat_messages[session_id]

        if before:
            messages = [m for m in messages if m.timestamp < before]

        return messages[-limit:]

    def add_reaction(
        self,
        session_id: str,
        message_id: str,
        user_id: str,
        emoji: str,
    ) -> bool:
        """Add a reaction to a chat message."""
        if session_id not in self._chat_messages:
            return False

        message = next(
            (m for m in self._chat_messages[session_id] if m.id == message_id),
            None
        )
        if not message:
            return False

        if emoji not in message.reactions:
            message.reactions[emoji] = []

        if user_id not in message.reactions[emoji]:
            message.reactions[emoji].append(user_id)

        return True

    # =========================================================================
    # Comments
    # =========================================================================

    def add_comment(
        self,
        session_id: str,
        user_id: str,
        username: str,
        target_type: str,
        target_id: str,
        content: str,
    ) -> Optional[Comment]:
        """Add a comment to a pipeline element."""
        if session_id not in self._comments:
            return None

        comment = Comment(
            id=self._generate_id(),
            session_id=session_id,
            target_type=target_type,
            target_id=target_id,
            user_id=user_id,
            username=username,
            content=content,
            created_at=self._now(),
        )

        self._comments[session_id].append(comment)
        return comment

    def reply_to_comment(
        self,
        session_id: str,
        comment_id: str,
        user_id: str,
        username: str,
        content: str,
    ) -> Optional[CommentReply]:
        """Reply to a comment."""
        if session_id not in self._comments:
            return None

        comment = next(
            (c for c in self._comments[session_id] if c.id == comment_id),
            None
        )
        if not comment:
            return None

        reply = CommentReply(
            id=self._generate_id(),
            comment_id=comment_id,
            user_id=user_id,
            username=username,
            content=content,
            created_at=self._now(),
        )

        comment.replies.append(reply)
        return reply

    def resolve_comment(
        self,
        session_id: str,
        comment_id: str,
        user_id: str,
    ) -> bool:
        """Resolve a comment."""
        if session_id not in self._comments:
            return False

        comment = next(
            (c for c in self._comments[session_id] if c.id == comment_id),
            None
        )
        if not comment:
            return False

        comment.resolved = True
        comment.resolved_by = user_id
        comment.resolved_at = self._now()
        return True

    def get_comments(
        self,
        session_id: str,
        target_id: Optional[str] = None,
        include_resolved: bool = False,
    ) -> List[Comment]:
        """Get comments for a session or specific target."""
        if session_id not in self._comments:
            return []

        comments = self._comments[session_id]

        if target_id:
            comments = [c for c in comments if c.target_id == target_id]

        if not include_resolved:
            comments = [c for c in comments if not c.resolved]

        return comments

    # =========================================================================
    # Activity Log
    # =========================================================================

    def _log_activity(
        self,
        session_id: str,
        user_id: str,
        username: str,
        activity_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an activity in the session."""
        if session_id not in self._activities:
            self._activities[session_id] = []

        activity = SessionActivity(
            id=self._generate_id(),
            session_id=session_id,
            user_id=user_id,
            username=username,
            activity_type=activity_type,
            description=description,
            timestamp=self._now(),
            metadata=metadata or {},
        )

        self._activities[session_id].append(activity)

        # Keep only last 1000 activities
        if len(self._activities[session_id]) > 1000:
            self._activities[session_id] = self._activities[session_id][-1000:]

    def get_activity_log(
        self,
        session_id: str,
        limit: int = 50,
    ) -> List[SessionActivity]:
        """Get recent activity log for a session."""
        if session_id not in self._activities:
            return []

        return self._activities[session_id][-limit:]

    # =========================================================================
    # Invites
    # =========================================================================

    def create_invite(
        self,
        session_id: str,
        invited_email: str,
        invited_by: str,
        role: UserRole = UserRole.EDITOR,
        expires_hours: int = 24,
    ) -> Optional[SessionInvite]:
        """Create an invitation to join a session."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        now = datetime.utcnow()
        invite = SessionInvite(
            id=self._generate_id(),
            session_id=session_id,
            invited_email=invited_email,
            invited_by=invited_by,
            role=role,
            created_at=now.isoformat() + "Z",
            expires_at=(now + timedelta(hours=expires_hours)).isoformat() + "Z",
        )

        self._invites[invite.id] = invite
        return invite

    def accept_invite(self, invite_id: str) -> Optional[SessionInvite]:
        """Accept an invitation."""
        invite = self._invites.get(invite_id)
        if not invite:
            return None

        # Check expiration
        if datetime.fromisoformat(invite.expires_at.rstrip("Z")) < datetime.utcnow():
            return None

        invite.accepted = True
        invite.accepted_at = self._now()
        return invite

    # =========================================================================
    # Broadcasting
    # =========================================================================

    def register_broadcast_handler(
        self,
        session_id: str,
        handler: Callable[[WSMessage], None],
    ) -> None:
        """Register a handler for broadcast messages."""
        if session_id not in self._broadcast_handlers:
            self._broadcast_handlers[session_id] = []
        self._broadcast_handlers[session_id].append(handler)

    def unregister_broadcast_handler(
        self,
        session_id: str,
        handler: Callable[[WSMessage], None],
    ) -> None:
        """Unregister a broadcast handler."""
        if session_id in self._broadcast_handlers:
            if handler in self._broadcast_handlers[session_id]:
                self._broadcast_handlers[session_id].remove(handler)

    async def broadcast(self, message: WSMessage) -> None:
        """Broadcast a message to all handlers for a session."""
        handlers = self._broadcast_handlers.get(message.session_id, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception:
                pass  # Don't let one handler failure affect others


# Singleton instance
_service: Optional[CollaborationService] = None


def get_collaboration_service() -> CollaborationService:
    """Get the singleton CollaborationService instance."""
    global _service
    if _service is None:
        _service = CollaborationService()
    return _service
