"""
Console session and conversation state management.

This module provides a simple in-memory store for console sessions so that
the AI console can maintain context across turns (goal, requirements,
current pipeline, recent pipelines, etc.).

It is intentionally conservative and can be swapped out for a more
durable store (e.g. SQLite/Redis) in the future.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PipelineRef(BaseModel):
    """Lightweight reference to a pipeline for recent history."""

    id: str
    name: str
    version: str


class PipelineContext(BaseModel):
    """Pipeline context for a conversation."""

    current_pipeline_id: Optional[str] = None
    recent_pipelines: List[PipelineRef] = Field(default_factory=list)


class ConversationState(BaseModel):
    """State for a single console conversation/goal."""

    goal: Optional[str] = None
    requirements: Dict[str, Any] = Field(default_factory=dict)
    pipeline_context: PipelineContext = Field(default_factory=PipelineContext)
    history_summary: str = ""
    last_actions: List[str] = Field(default_factory=list)


class ConsoleSessionState(BaseModel):
    """State for a console session (per session_id)."""

    session_id: str
    conversation: ConversationState = Field(default_factory=ConversationState)


class SessionStore:
    """In-memory store for console session state."""

    def __init__(self) -> None:
        self._sessions: Dict[str, ConsoleSessionState] = {}
        self._lock = threading.Lock()

    def get_or_create(self, session_id: str) -> ConsoleSessionState:
        """Get an existing session or create a new one."""
        if not session_id:
            session_id = "default"

        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = ConsoleSessionState(session_id=session_id)
            return self._sessions[session_id]

    def update_pipeline_context(
        self,
        session_id: str,
        pipeline_id: str,
        name: str,
        version: str,
    ) -> ConsoleSessionState:
        """Update the pipeline context for a session and return the state."""
        state = self.get_or_create(session_id)
        ctx = state.conversation.pipeline_context
        ctx.current_pipeline_id = pipeline_id

        # Prepend or update in recent_pipelines (keep small list)
        existing = [p for p in ctx.recent_pipelines if p.id != pipeline_id]
        ctx.recent_pipelines = [PipelineRef(id=pipeline_id, name=name, version=version)] + existing[:4]

        return state

    def add_action(self, session_id: str, action: str) -> ConsoleSessionState:
        """Append an action label to the conversation's last_actions."""
        state = self.get_or_create(session_id)
        actions = state.conversation.last_actions
        actions.append(action)
        # Keep only a small tail of recent actions
        if len(actions) > 20:
            state.conversation.last_actions = actions[-20:]
        return state

    def update_requirements(self, session_id: str, updates: Dict[str, Any]) -> ConsoleSessionState:
        """Merge requirement updates into the conversation requirements."""
        state = self.get_or_create(session_id)
        reqs = state.conversation.requirements
        reqs.update(updates)
        return state


_SESSION_STORE: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get the global SessionStore instance."""
    global _SESSION_STORE
    if _SESSION_STORE is None:
        _SESSION_STORE = SessionStore()
    return _SESSION_STORE

