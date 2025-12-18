"""
WebSocket Connection Manager for FlowMason Studio.

Handles real-time execution updates via WebSocket connections:
- Client connection management with unique IDs
- Run subscription system for targeted broadcasts
- Event broadcasting to subscribed clients
- Automatic ping/pong for connection health
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class WebSocketEventType(str, Enum):
    """Types of WebSocket events."""
    # Connection events
    CONNECTED = "connected"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    ERROR = "error"

    # Execution events
    RUN_STARTED = "run_started"
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    STAGE_FAILED = "stage_failed"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"

    # Debug events
    EXECUTION_PAUSED = "execution_paused"
    EXECUTION_RESUMED = "execution_resumed"
    BREAKPOINT_HIT = "breakpoint_hit"

    # Streaming events
    TOKEN_CHUNK = "token_chunk"
    STREAM_START = "stream_start"
    STREAM_END = "stream_end"

    # System events
    PING = "ping"
    PONG = "pong"


class WebSocketMessage(BaseModel):
    """Standard WebSocket message format."""
    type: WebSocketEventType
    run_id: Optional[str] = None
    payload: Dict[str, Any] = {}
    timestamp: Optional[datetime] = None

    def __init__(self, **data: Any):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


@dataclass
class ClientConnection:
    """Represents a connected WebSocket client."""
    client_id: str
    websocket: WebSocket
    subscribed_runs: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_ping: datetime = field(default_factory=datetime.utcnow)


class ConnectionManager:
    """
    Manages WebSocket connections and run subscriptions.

    Features:
    - Client ID generation and tracking
    - Run subscription management
    - Targeted broadcasting to run subscribers
    - Connection health monitoring via ping/pong
    """

    def __init__(self):
        # client_id -> ClientConnection
        self._connections: Dict[str, ClientConnection] = {}
        # run_id -> set of client_ids
        self._run_subscriptions: Dict[str, Set[str]] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
        # Event hooks for external integration
        self._event_handlers: Dict[str, Callable[[str, Dict], Awaitable[None]]] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept a new WebSocket connection and assign a client ID.

        Args:
            websocket: The WebSocket connection to accept

        Returns:
            Unique client ID for this connection
        """
        await websocket.accept()
        client_id = str(uuid.uuid4())

        async with self._lock:
            self._connections[client_id] = ClientConnection(
                client_id=client_id,
                websocket=websocket,
            )

        logger.info(f"WebSocket client connected: {client_id}")

        # Send connection confirmation
        await self.send_to_client(client_id, WebSocketMessage(
            type=WebSocketEventType.CONNECTED,
            payload={"client_id": client_id}
        ))

        return client_id

    async def disconnect(self, client_id: str):
        """
        Handle client disconnection and cleanup subscriptions.

        Args:
            client_id: The client ID to disconnect
        """
        async with self._lock:
            if client_id not in self._connections:
                return

            connection = self._connections[client_id]

            # Remove from all run subscriptions
            for run_id in list(connection.subscribed_runs):
                if run_id in self._run_subscriptions:
                    self._run_subscriptions[run_id].discard(client_id)
                    # Clean up empty subscription sets
                    if not self._run_subscriptions[run_id]:
                        del self._run_subscriptions[run_id]

            # Remove connection
            del self._connections[client_id]

        logger.info(f"WebSocket client disconnected: {client_id}")

    async def subscribe(self, client_id: str, run_id: str) -> bool:
        """
        Subscribe a client to receive updates for a specific run.

        Args:
            client_id: The client ID to subscribe
            run_id: The run ID to subscribe to

        Returns:
            True if subscription successful, False otherwise
        """
        async with self._lock:
            if client_id not in self._connections:
                logger.warning(f"Cannot subscribe unknown client: {client_id}")
                return False

            connection = self._connections[client_id]
            connection.subscribed_runs.add(run_id)

            if run_id not in self._run_subscriptions:
                self._run_subscriptions[run_id] = set()
            self._run_subscriptions[run_id].add(client_id)

        logger.debug(f"Client {client_id} subscribed to run {run_id}")

        # Confirm subscription
        await self.send_to_client(client_id, WebSocketMessage(
            type=WebSocketEventType.SUBSCRIBED,
            run_id=run_id,
            payload={"run_id": run_id}
        ))

        return True

    async def unsubscribe(self, client_id: str, run_id: str) -> bool:
        """
        Unsubscribe a client from a specific run.

        Args:
            client_id: The client ID to unsubscribe
            run_id: The run ID to unsubscribe from

        Returns:
            True if unsubscription successful, False otherwise
        """
        async with self._lock:
            if client_id not in self._connections:
                return False

            connection = self._connections[client_id]
            connection.subscribed_runs.discard(run_id)

            if run_id in self._run_subscriptions:
                self._run_subscriptions[run_id].discard(client_id)
                if not self._run_subscriptions[run_id]:
                    del self._run_subscriptions[run_id]

        logger.debug(f"Client {client_id} unsubscribed from run {run_id}")

        # Confirm unsubscription
        await self.send_to_client(client_id, WebSocketMessage(
            type=WebSocketEventType.UNSUBSCRIBED,
            run_id=run_id,
            payload={"run_id": run_id}
        ))

        return True

    async def send_to_client(self, client_id: str, message: WebSocketMessage):
        """
        Send a message to a specific client.

        Args:
            client_id: The client ID to send to
            message: The message to send
        """
        async with self._lock:
            if client_id not in self._connections:
                return
            connection = self._connections[client_id]

        try:
            await connection.websocket.send_json(message.model_dump(mode='json'))
        except Exception as e:
            logger.warning(f"Failed to send to client {client_id}: {e}")
            # Don't disconnect here - let the receive loop handle it

    async def broadcast_to_run(self, run_id: str, message: WebSocketMessage):
        """
        Broadcast a message to all clients subscribed to a specific run.

        Args:
            run_id: The run ID to broadcast to
            message: The message to broadcast
        """
        message.run_id = run_id

        async with self._lock:
            client_ids = list(self._run_subscriptions.get(run_id, set()))

        if not client_ids:
            logger.debug(f"No subscribers for run {run_id}")
            return

        logger.debug(f"Broadcasting {message.type} to {len(client_ids)} clients for run {run_id}")

        # Send to all subscribed clients
        tasks = [
            self.send_to_client(client_id, message)
            for client_id in client_ids
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_run_event(
        self,
        run_id: str,
        event_type: WebSocketEventType,
        payload: Dict[str, Any],
    ):
        """
        Convenience method to broadcast a run event.

        Args:
            run_id: The run ID this event is for
            event_type: Type of event
            payload: Event payload data
        """
        message = WebSocketMessage(
            type=event_type,
            run_id=run_id,
            payload=payload,
        )
        await self.broadcast_to_run(run_id, message)

    async def handle_client_message(self, client_id: str, data: Dict[str, Any]):
        """
        Handle an incoming message from a client.

        Args:
            client_id: The client ID that sent the message
            data: The message data
        """
        msg_type = data.get("type", "").lower()

        if msg_type == "subscribe":
            run_id = data.get("run_id")
            if run_id:
                await self.subscribe(client_id, run_id)

        elif msg_type == "unsubscribe":
            run_id = data.get("run_id")
            if run_id:
                await self.unsubscribe(client_id, run_id)

        elif msg_type == "ping":
            # Respond with pong
            await self.send_to_client(client_id, WebSocketMessage(
                type=WebSocketEventType.PONG,
                payload={"timestamp": datetime.utcnow().isoformat()}
            ))
            # Update last ping time
            async with self._lock:
                if client_id in self._connections:
                    self._connections[client_id].last_ping = datetime.utcnow()

        elif msg_type in ["pause", "resume", "step", "stop"]:
            # Debug commands - forward to handler if registered
            run_id = data.get("run_id")
            if run_id and msg_type in self._event_handlers:
                handler = self._event_handlers[msg_type]
                try:
                    await handler(run_id, data)
                except Exception as e:
                    logger.error(f"Error handling {msg_type} command: {e}")
                    await self.send_to_client(client_id, WebSocketMessage(
                        type=WebSocketEventType.ERROR,
                        run_id=run_id,
                        payload={"error": str(e), "command": msg_type}
                    ))

        else:
            logger.warning(f"Unknown message type from {client_id}: {msg_type}")

    def register_handler(self, command: str, handler: Callable[[str, Dict], Awaitable[None]]):
        """
        Register a handler for debug commands (pause, resume, step, stop).

        Args:
            command: The command name to handle
            handler: Async function(run_id, data) to handle the command
        """
        self._event_handlers[command] = handler

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self._connections)

    def get_run_subscriber_count(self, run_id: str) -> int:
        """Get the number of subscribers for a specific run."""
        return len(self._run_subscriptions.get(run_id, set()))

    def has_subscribers(self, run_id: str) -> bool:
        """Check if a run has any subscribers."""
        return run_id in self._run_subscriptions and len(self._run_subscriptions[run_id]) > 0

    async def broadcast_stream_start(
        self,
        run_id: str,
        stage_id: str,
        stage_name: Optional[str] = None,
    ):
        """
        Broadcast that token streaming is starting for a stage.

        Args:
            run_id: The run ID
            stage_id: The stage ID starting to stream
            stage_name: Optional stage name
        """
        await self.broadcast_run_event(
            run_id=run_id,
            event_type=WebSocketEventType.STREAM_START,
            payload={
                "stage_id": stage_id,
                "stage_name": stage_name,
            }
        )

    async def broadcast_token_chunk(
        self,
        run_id: str,
        stage_id: str,
        chunk: str,
        token_index: int = 0,
    ):
        """
        Broadcast a token chunk during streaming.

        Args:
            run_id: The run ID
            stage_id: The stage ID streaming
            chunk: The token chunk text
            token_index: Index of this chunk in the stream
        """
        await self.broadcast_run_event(
            run_id=run_id,
            event_type=WebSocketEventType.TOKEN_CHUNK,
            payload={
                "stage_id": stage_id,
                "chunk": chunk,
                "token_index": token_index,
            }
        )

    async def broadcast_stream_end(
        self,
        run_id: str,
        stage_id: str,
        total_tokens: int = 0,
        final_content: Optional[str] = None,
    ):
        """
        Broadcast that token streaming has completed for a stage.

        Args:
            run_id: The run ID
            stage_id: The stage ID that finished streaming
            total_tokens: Total number of tokens streamed
            final_content: The complete final content
        """
        await self.broadcast_run_event(
            run_id=run_id,
            event_type=WebSocketEventType.STREAM_END,
            payload={
                "stage_id": stage_id,
                "total_tokens": total_tokens,
                "final_content": final_content,
            }
        )


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get or create the global connection manager."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


async def websocket_handler(websocket: WebSocket, manager: ConnectionManager):
    """
    Main WebSocket handler for client connections.

    This function handles the WebSocket lifecycle:
    1. Accept connection and assign client ID
    2. Listen for messages in a loop
    3. Clean up on disconnect

    Args:
        websocket: The WebSocket connection
        manager: The connection manager to use
    """
    client_id = await manager.connect(websocket)

    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_json()
            await manager.handle_client_message(client_id, data)

    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        await manager.disconnect(client_id)
