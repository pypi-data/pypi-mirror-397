"""
Real-time Collaboration API Routes.

Provides HTTP API for collaborative pipeline editing sessions.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from flowmason_studio.models.collaboration import (
    AcquireLockRequest,
    AddCommentRequest,
    ChatMessage,
    CollaborationSession,
    Comment,
    CreateSessionRequest,
    CreateSessionResponse,
    CursorPosition,
    EditChange,
    EditOperation,
    InviteUserRequest,
    JoinSessionRequest,
    JoinSessionResponse,
    LockState,
    PresenceStatus,
    SendChatRequest,
    SendEditRequest,
    SendEditResponse,
    SessionActivity,
    SessionInvite,
    UpdatePresenceRequest,
    UserPresence,
    UserRole,
    WSMessage,
    WSMessageType,
)
from flowmason_studio.services.collaboration_service import get_collaboration_service

router = APIRouter(prefix="/collaboration", tags=["collaboration"])


# =============================================================================
# Session Management
# =============================================================================


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest) -> CreateSessionResponse:
    """
    Create a new collaboration session for a pipeline.

    The creator becomes the session owner with full permissions.
    Returns a join URL and invite code for sharing with collaborators.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_owner"
    username = "Pipeline Owner"

    session, invite_code = service.create_session(
        pipeline_id=request.pipeline_id,
        user_id=user_id,
        username=username,
        max_participants=request.max_participants,
        auto_save=request.auto_save,
        allow_anonymous=request.allow_anonymous,
        require_approval=request.require_approval,
    )

    return CreateSessionResponse(
        session=session,
        join_url=f"/collaborate/{session.id}",
        invite_code=invite_code,
    )


@router.get("/sessions/{session_id}", response_model=CollaborationSession)
async def get_session(session_id: str) -> CollaborationSession:
    """
    Get details of a collaboration session.
    """
    service = get_collaboration_service()
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session


@router.post("/sessions/join", response_model=JoinSessionResponse)
async def join_session(request: JoinSessionRequest) -> JoinSessionResponse:
    """
    Join a collaboration session.

    Can join by session ID or invite code.
    """
    service = get_collaboration_service()

    # Find session
    session = None
    if request.session_id:
        session = service.get_session(request.session_id)
    elif request.invite_code:
        session = service.get_session_by_invite_code(request.invite_code)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.is_active:
        raise HTTPException(status_code=410, detail="Session has ended")

    # TODO: Get actual user from auth context
    user_id = f"user_{len(session.participants) + 1}"
    username = request.username or f"User {len(session.participants) + 1}"

    user = service.join_session(
        session_id=session.id,
        user_id=user_id,
        username=username,
    )

    if not user:
        raise HTTPException(status_code=403, detail="Cannot join session")

    return JoinSessionResponse(
        session=session,
        user=user,
        token=f"ws_token_{session.id}_{user_id}",  # In production, use real JWT
    )


@router.post("/sessions/{session_id}/leave")
async def leave_session(session_id: str) -> dict:
    """
    Leave a collaboration session.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    success = service.leave_session(session_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session or user not found")

    return {"success": True}


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: str) -> dict:
    """
    End a collaboration session (owner only).
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_owner"

    success = service.end_session(session_id, user_id)
    if not success:
        raise HTTPException(
            status_code=403,
            detail="Only the session owner can end the session"
        )

    return {"success": True}


# =============================================================================
# Presence
# =============================================================================


@router.get("/sessions/{session_id}/users", response_model=List[UserPresence])
async def get_online_users(session_id: str) -> List[UserPresence]:
    """
    Get all online users in a session.
    """
    service = get_collaboration_service()
    return service.get_online_users(session_id)


@router.put("/sessions/{session_id}/presence", response_model=UserPresence)
async def update_presence(
    session_id: str,
    request: UpdatePresenceRequest,
) -> UserPresence:
    """
    Update your presence in the session.

    Use this to update cursor position, selection, or status.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    user = service.update_presence(
        session_id=session_id,
        user_id=user_id,
        status=request.status,
        cursor=request.cursor,
        selected_stage=request.selected_stage,
        selected_connection=request.selected_connection,
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not in session")

    return user


# =============================================================================
# Edits
# =============================================================================


@router.post("/sessions/{session_id}/edits", response_model=SendEditResponse)
async def send_edit(
    session_id: str,
    request: SendEditRequest,
) -> SendEditResponse:
    """
    Send an edit operation to the session.

    The edit is validated against the current version to detect conflicts.
    If a conflict is detected, you should sync and retry.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    return service.apply_edit(
        session_id=session_id,
        user_id=user_id,
        operation=request.operation,
        target_id=request.target_id,
        data=request.data,
        base_version=request.base_version,
    )


@router.get("/sessions/{session_id}/edits", response_model=List[EditChange])
async def get_changes(
    session_id: str,
    since_version: int = Query(0, description="Get changes since this version"),
) -> List[EditChange]:
    """
    Get all changes since a specific version.

    Use this to sync your local state with the server.
    """
    service = get_collaboration_service()
    return service.get_changes_since(session_id, since_version)


@router.post("/sessions/{session_id}/undo", response_model=Optional[EditChange])
async def undo(session_id: str) -> Optional[EditChange]:
    """
    Undo the last change by the current user.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    return service.undo(session_id, user_id)


@router.post("/sessions/{session_id}/redo", response_model=Optional[EditChange])
async def redo(session_id: str) -> Optional[EditChange]:
    """
    Redo the last undone change.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    return service.redo(session_id, user_id)


# =============================================================================
# Locks
# =============================================================================


@router.post("/sessions/{session_id}/locks", response_model=LockState)
async def acquire_lock(
    session_id: str,
    request: AcquireLockRequest,
) -> LockState:
    """
    Acquire a lock on a pipeline element.

    Locks prevent concurrent editing of the same element.
    Locks automatically expire after the specified duration.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    lock = service.acquire_lock(
        session_id=session_id,
        user_id=user_id,
        target_id=request.target_id,
        target_type=request.target_type,
        duration=request.duration,
        reason=request.reason,
    )

    if not lock:
        raise HTTPException(status_code=409, detail="Element is locked by another user")

    return lock


@router.delete("/sessions/{session_id}/locks/{target_id}")
async def release_lock(session_id: str, target_id: str) -> dict:
    """
    Release a lock on a pipeline element.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    success = service.release_lock(session_id, user_id, target_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lock not found or not owned")

    return {"success": True}


@router.get("/sessions/{session_id}/locks", response_model=List[LockState])
async def get_locks(session_id: str) -> List[LockState]:
    """
    Get all active locks in a session.
    """
    service = get_collaboration_service()
    return service.get_locks(session_id)


# =============================================================================
# Chat
# =============================================================================


@router.post("/sessions/{session_id}/chat", response_model=ChatMessage)
async def send_chat_message(
    session_id: str,
    request: SendChatRequest,
) -> ChatMessage:
    """
    Send a chat message in the session.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"
    username = "Current User"

    message = service.send_chat_message(
        session_id=session_id,
        user_id=user_id,
        username=username,
        content=request.content,
        reply_to=request.reply_to,
        mentions=request.mentions,
    )

    if not message:
        raise HTTPException(status_code=404, detail="Session not found")

    return message


@router.get("/sessions/{session_id}/chat", response_model=List[ChatMessage])
async def get_chat_messages(
    session_id: str,
    limit: int = Query(50, ge=1, le=200),
    before: Optional[str] = Query(None, description="Get messages before this timestamp"),
) -> List[ChatMessage]:
    """
    Get chat messages for a session.
    """
    service = get_collaboration_service()
    return service.get_chat_messages(session_id, limit, before)


@router.post("/sessions/{session_id}/chat/{message_id}/reactions")
async def add_reaction(
    session_id: str,
    message_id: str,
    emoji: str = Query(..., min_length=1, max_length=10),
) -> dict:
    """
    Add a reaction to a chat message.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    success = service.add_reaction(session_id, message_id, user_id, emoji)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")

    return {"success": True}


# =============================================================================
# Comments
# =============================================================================


@router.post("/sessions/{session_id}/comments", response_model=Comment)
async def add_comment(
    session_id: str,
    request: AddCommentRequest,
) -> Comment:
    """
    Add a comment to a pipeline element.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"
    username = "Current User"

    comment = service.add_comment(
        session_id=session_id,
        user_id=user_id,
        username=username,
        target_type=request.target_type,
        target_id=request.target_id,
        content=request.content,
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Session not found")

    return comment


@router.get("/sessions/{session_id}/comments", response_model=List[Comment])
async def get_comments(
    session_id: str,
    target_id: Optional[str] = Query(None),
    include_resolved: bool = Query(False),
) -> List[Comment]:
    """
    Get comments for a session.
    """
    service = get_collaboration_service()
    return service.get_comments(session_id, target_id, include_resolved)


class ReplyRequest(BaseModel):
    content: str


@router.post("/sessions/{session_id}/comments/{comment_id}/replies")
async def reply_to_comment(
    session_id: str,
    comment_id: str,
    request: ReplyRequest,
) -> dict:
    """
    Reply to a comment.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"
    username = "Current User"

    reply = service.reply_to_comment(
        session_id=session_id,
        comment_id=comment_id,
        user_id=user_id,
        username=username,
        content=request.content,
    )

    if not reply:
        raise HTTPException(status_code=404, detail="Comment not found")

    return {"success": True, "reply": reply.model_dump()}


@router.post("/sessions/{session_id}/comments/{comment_id}/resolve")
async def resolve_comment(session_id: str, comment_id: str) -> dict:
    """
    Resolve a comment.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    success = service.resolve_comment(session_id, comment_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")

    return {"success": True}


# =============================================================================
# Activity Log
# =============================================================================


@router.get("/sessions/{session_id}/activity", response_model=List[SessionActivity])
async def get_activity_log(
    session_id: str,
    limit: int = Query(50, ge=1, le=500),
) -> List[SessionActivity]:
    """
    Get the activity log for a session.
    """
    service = get_collaboration_service()
    return service.get_activity_log(session_id, limit)


# =============================================================================
# Invites
# =============================================================================


@router.post("/sessions/{session_id}/invites", response_model=SessionInvite)
async def invite_user(
    session_id: str,
    request: InviteUserRequest,
) -> SessionInvite:
    """
    Invite a user to join the session.
    """
    service = get_collaboration_service()

    # TODO: Get actual user from auth context
    user_id = "user_current"

    invite = service.create_invite(
        session_id=session_id,
        invited_email=request.email,
        invited_by=user_id,
        role=request.role,
    )

    if not invite:
        raise HTTPException(status_code=404, detail="Session not found")

    return invite


@router.post("/invites/{invite_id}/accept")
async def accept_invite(invite_id: str) -> dict:
    """
    Accept an invitation to join a session.
    """
    service = get_collaboration_service()

    invite = service.accept_invite(invite_id)
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found or expired")

    return {"success": True, "session_id": invite.session_id}


# =============================================================================
# WebSocket Endpoint
# =============================================================================


@router.websocket("/ws/{session_id}")
async def collaboration_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time collaboration.

    Protocol:
    - Send {"type": "auth", "token": "..."} to authenticate
    - Send {"type": "cursor", "x": ..., "y": ..., "selected_stage": "..."} for cursor updates
    - Send {"type": "edit", "operation": "...", "target_id": "...", "data": {...}, "base_version": N}
    - Send {"type": "chat", "content": "..."} for chat messages
    - Send {"type": "typing", "is_typing": true/false} for typing indicator
    - Send {"type": "ping"} for keepalive

    Events received:
    - user_joined: A user joined the session
    - user_left: A user left the session
    - presence_update: User presence changed
    - cursor_move: User cursor moved
    - edit: An edit was made
    - chat_message: A chat message was sent
    - typing: User is typing
    - comment_added: A comment was added
    - lock_acquired/released: Lock state changed
    """
    service = get_collaboration_service()

    # Verify session exists
    session = service.get_session(session_id)
    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    await websocket.accept()

    # Placeholder user (in production, authenticate from token)
    user_id = f"ws_user_{id(websocket)}"
    username = f"User {id(websocket) % 1000}"

    # Join session
    user = service.join_session(session_id, user_id, username)
    if not user:
        await websocket.close(code=4003, reason="Cannot join session")
        return

    # Broadcast handler
    async def handle_broadcast(msg: WSMessage):
        try:
            await websocket.send_json(msg.model_dump())
        except Exception:
            pass

    service.register_broadcast_handler(session_id, handle_broadcast)

    # Send connected message
    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "user": user.model_dump(),
        "version": session.current_version,
    })

    # Broadcast user joined
    from datetime import datetime
    await service.broadcast(WSMessage(
        type=WSMessageType.USER_JOINED,
        session_id=session_id,
        user_id=user_id,
        data={"user": user.model_dump()},
        timestamp=datetime.utcnow().isoformat() + "Z",
    ))

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "cursor":
                cursor = CursorPosition(
                    x=data.get("x", 0),
                    y=data.get("y", 0),
                    viewport_x=data.get("viewport_x", 0),
                    viewport_y=data.get("viewport_y", 0),
                    zoom=data.get("zoom", 1.0),
                )
                service.update_presence(
                    session_id=session_id,
                    user_id=user_id,
                    cursor=cursor,
                    selected_stage=data.get("selected_stage"),
                    selected_connection=data.get("selected_connection"),
                )
                await service.broadcast(WSMessage(
                    type=WSMessageType.CURSOR_MOVE,
                    session_id=session_id,
                    user_id=user_id,
                    data={
                        "cursor": cursor.model_dump(),
                        "selected_stage": data.get("selected_stage"),
                        "selected_connection": data.get("selected_connection"),
                    },
                    timestamp=datetime.utcnow().isoformat() + "Z",
                ))

            elif msg_type == "edit":
                response = service.apply_edit(
                    session_id=session_id,
                    user_id=user_id,
                    operation=EditOperation(data.get("operation")),
                    target_id=data.get("target_id"),
                    data=data.get("data", {}),
                    base_version=data.get("base_version", 0),
                )
                await websocket.send_json({
                    "type": "edit_ack",
                    **response.model_dump(),
                })
                if response.success and response.change:
                    await service.broadcast(WSMessage(
                        type=WSMessageType.EDIT,
                        session_id=session_id,
                        user_id=user_id,
                        data={"change": response.change.model_dump()},
                        timestamp=datetime.utcnow().isoformat() + "Z",
                    ))

            elif msg_type == "chat":
                message = service.send_chat_message(
                    session_id=session_id,
                    user_id=user_id,
                    username=username,
                    content=data.get("content", ""),
                    reply_to=data.get("reply_to"),
                    mentions=data.get("mentions", []),
                )
                if message:
                    await service.broadcast(WSMessage(
                        type=WSMessageType.CHAT_MESSAGE,
                        session_id=session_id,
                        user_id=user_id,
                        data={"message": message.model_dump()},
                        timestamp=datetime.utcnow().isoformat() + "Z",
                    ))

            elif msg_type == "typing":
                await service.broadcast(WSMessage(
                    type=WSMessageType.TYPING,
                    session_id=session_id,
                    user_id=user_id,
                    data={"is_typing": data.get("is_typing", False)},
                    timestamp=datetime.utcnow().isoformat() + "Z",
                ))

    except WebSocketDisconnect:
        pass
    finally:
        service.unregister_broadcast_handler(session_id, handle_broadcast)
        service.leave_session(session_id, user_id)
        await service.broadcast(WSMessage(
            type=WSMessageType.USER_LEFT,
            session_id=session_id,
            user_id=user_id,
            data={"user_id": user_id},
            timestamp=datetime.utcnow().isoformat() + "Z",
        ))
