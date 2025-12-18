# Real-time Collaboration

FlowMason Studio supports real-time collaborative editing of pipelines with multiple users.

## Overview

Real-time Collaboration provides:

- **Live Cursors**: See other users' cursor positions in real-time
- **Presence Awareness**: Know who's online and what they're editing
- **Synchronized Editing**: Changes propagate instantly to all participants
- **Conflict Resolution**: Automatic handling of concurrent edits
- **Element Locking**: Prevent conflicts on specific elements
- **Chat & Comments**: In-context communication
- **Undo/Redo**: Per-user undo history
- **Activity Log**: Track all session changes

## Quick Start

### Create a Session

```http
POST /api/v1/collaboration/sessions
Content-Type: application/json

{
  "pipeline_id": "my-pipeline-id",
  "max_participants": 10,
  "auto_save": true,
  "allow_anonymous": false
}
```

**Response:**
```json
{
  "session": {
    "id": "session_abc123",
    "pipeline_id": "my-pipeline-id",
    "created_at": "2024-01-15T10:00:00Z",
    "created_by": "user_owner",
    "is_active": true,
    "participants": [
      {
        "user_id": "user_owner",
        "username": "Pipeline Owner",
        "role": "owner",
        "status": "online",
        "color": "#ef4444"
      }
    ],
    "current_version": 1
  },
  "join_url": "/collaborate/session_abc123",
  "invite_code": "ABC12345"
}
```

### Join a Session

By session ID:
```http
POST /api/v1/collaboration/sessions/join
Content-Type: application/json

{
  "session_id": "session_abc123",
  "username": "Collaborator"
}
```

Or by invite code:
```http
POST /api/v1/collaboration/sessions/join
Content-Type: application/json

{
  "invite_code": "ABC12345",
  "username": "Collaborator"
}
```

**Response:**
```json
{
  "session": {...},
  "user": {
    "user_id": "user_123",
    "username": "Collaborator",
    "role": "editor",
    "status": "online",
    "color": "#3b82f6"
  },
  "token": "ws_token_session_abc123_user_123"
}
```

## WebSocket Connection

Connect to the WebSocket for real-time updates:

```
ws://localhost:8999/api/v1/collaboration/ws/session_abc123
```

### Message Protocol

**Cursor Movement:**
```json
{
  "type": "cursor",
  "x": 250,
  "y": 150,
  "viewport_x": 0,
  "viewport_y": 0,
  "zoom": 1.0,
  "selected_stage": "generator_1"
}
```

**Send Edit:**
```json
{
  "type": "edit",
  "operation": "update_stage",
  "target_id": "generator_1",
  "data": {"config": {"prompt": "New prompt"}},
  "base_version": 5
}
```

**Chat Message:**
```json
{
  "type": "chat",
  "content": "Let's add a filter stage here",
  "mentions": ["user_123"]
}
```

**Typing Indicator:**
```json
{
  "type": "typing",
  "is_typing": true
}
```

### Events Received

**User Joined:**
```json
{
  "type": "user_joined",
  "session_id": "session_abc123",
  "user_id": "user_456",
  "data": {
    "user": {
      "user_id": "user_456",
      "username": "New User",
      "color": "#22c55e"
    }
  }
}
```

**Cursor Move:**
```json
{
  "type": "cursor_move",
  "user_id": "user_456",
  "data": {
    "cursor": {"x": 300, "y": 200},
    "selected_stage": "filter_1"
  }
}
```

**Edit Applied:**
```json
{
  "type": "edit",
  "user_id": "user_456",
  "data": {
    "change": {
      "id": "change_xyz",
      "operation": "update_stage",
      "target_id": "generator_1",
      "data": {...},
      "version": 6
    }
  }
}
```

## Presence

### Get Online Users

```http
GET /api/v1/collaboration/sessions/{session_id}/users
```

**Response:**
```json
[
  {
    "user_id": "user_owner",
    "username": "Pipeline Owner",
    "role": "owner",
    "status": "online",
    "cursor": {
      "position": {"x": 100, "y": 200},
      "selected_stage": "generator_1",
      "color": "#ef4444"
    },
    "color": "#ef4444"
  },
  {
    "user_id": "user_123",
    "username": "Collaborator",
    "role": "editor",
    "status": "online",
    "cursor": {...},
    "color": "#3b82f6"
  }
]
```

### Update Presence

```http
PUT /api/v1/collaboration/sessions/{session_id}/presence
Content-Type: application/json

{
  "status": "away",
  "cursor": {"x": 150, "y": 250},
  "selected_stage": "filter_1"
}
```

## Edit Operations

### Available Operations

| Operation | Description |
|-----------|-------------|
| `add_stage` | Add a new stage |
| `remove_stage` | Remove a stage |
| `update_stage` | Update stage config |
| `move_stage` | Change stage position |
| `add_connection` | Add a connection |
| `remove_connection` | Remove a connection |
| `update_pipeline` | Update pipeline metadata |
| `update_settings` | Update pipeline settings |

### Send an Edit

```http
POST /api/v1/collaboration/sessions/{session_id}/edits
Content-Type: application/json

{
  "operation": "add_stage",
  "target_id": null,
  "data": {
    "stage": {
      "id": "new_stage_1",
      "component_type": "filter",
      "config": {...}
    }
  },
  "base_version": 5
}
```

**Response (Success):**
```json
{
  "success": true,
  "change": {
    "id": "change_abc",
    "operation": "add_stage",
    "target_id": "new_stage_1",
    "data": {...},
    "user_id": "user_123",
    "version": 6
  },
  "new_version": 6
}
```

**Response (Conflict):**
```json
{
  "success": false,
  "conflict": {
    "id": "conflict_xyz",
    "change_a": {...},
    "change_b": {...},
    "conflict_type": "concurrent_edit"
  },
  "new_version": 7
}
```

### Sync Changes

Get all changes since a version:

```http
GET /api/v1/collaboration/sessions/{session_id}/edits?since_version=5
```

### Undo/Redo

```http
POST /api/v1/collaboration/sessions/{session_id}/undo
POST /api/v1/collaboration/sessions/{session_id}/redo
```

## Locking

Prevent concurrent edits on specific elements:

### Acquire Lock

```http
POST /api/v1/collaboration/sessions/{session_id}/locks
Content-Type: application/json

{
  "target_id": "generator_1",
  "target_type": "stage",
  "duration": 300,
  "reason": "Editing configuration"
}
```

**Response:**
```json
{
  "target_id": "generator_1",
  "target_type": "stage",
  "locked_by": "user_123",
  "locked_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-15T10:35:00Z",
  "reason": "Editing configuration"
}
```

### Release Lock

```http
DELETE /api/v1/collaboration/sessions/{session_id}/locks/generator_1
```

### Get Active Locks

```http
GET /api/v1/collaboration/sessions/{session_id}/locks
```

## Chat

### Send Message

```http
POST /api/v1/collaboration/sessions/{session_id}/chat
Content-Type: application/json

{
  "content": "Should we add error handling here?",
  "mentions": ["user_owner"]
}
```

### Get Messages

```http
GET /api/v1/collaboration/sessions/{session_id}/chat?limit=50
```

### Add Reaction

```http
POST /api/v1/collaboration/sessions/{session_id}/chat/{message_id}/reactions?emoji=👍
```

## Comments

Attach comments to specific pipeline elements:

### Add Comment

```http
POST /api/v1/collaboration/sessions/{session_id}/comments
Content-Type: application/json

{
  "target_type": "stage",
  "target_id": "generator_1",
  "content": "This prompt needs to be more specific"
}
```

### Reply to Comment

```http
POST /api/v1/collaboration/sessions/{session_id}/comments/{comment_id}/replies
Content-Type: application/json

{
  "content": "Good point, I'll update it"
}
```

### Resolve Comment

```http
POST /api/v1/collaboration/sessions/{session_id}/comments/{comment_id}/resolve
```

### Get Comments

```http
GET /api/v1/collaboration/sessions/{session_id}/comments?target_id=generator_1&include_resolved=false
```

## Invitations

### Invite User

```http
POST /api/v1/collaboration/sessions/{session_id}/invites
Content-Type: application/json

{
  "email": "collaborator@example.com",
  "role": "editor",
  "message": "Join me to work on this pipeline!"
}
```

### Accept Invite

```http
POST /api/v1/collaboration/invites/{invite_id}/accept
```

## Activity Log

```http
GET /api/v1/collaboration/sessions/{session_id}/activity?limit=50
```

**Response:**
```json
[
  {
    "id": "activity_1",
    "session_id": "session_abc123",
    "user_id": "user_owner",
    "username": "Pipeline Owner",
    "activity_type": "session_created",
    "description": "Pipeline Owner created the collaboration session",
    "timestamp": "2024-01-15T10:00:00Z"
  },
  {
    "id": "activity_2",
    "activity_type": "user_joined",
    "description": "Collaborator joined the session",
    "timestamp": "2024-01-15T10:05:00Z"
  }
]
```

## User Roles

| Role | Capabilities |
|------|--------------|
| `owner` | Full access, can end session, manage roles |
| `editor` | Can edit pipeline, chat, comment |
| `viewer` | Read-only access, can chat and comment |

## Session Settings

| Setting | Description |
|---------|-------------|
| `max_participants` | Maximum users allowed (2-50) |
| `auto_save` | Automatically save changes |
| `auto_save_interval` | Save interval in seconds |
| `allow_anonymous` | Allow anonymous users |
| `require_approval` | Require owner approval to join |

## Frontend Integration

### React Example

```tsx
import { useEffect, useState, useRef } from 'react';

function CollaborativeEditor({ sessionId, token }) {
  const ws = useRef<WebSocket>();
  const [users, setUsers] = useState([]);
  const [cursors, setCursors] = useState({});

  useEffect(() => {
    // Connect to WebSocket
    ws.current = new WebSocket(
      `ws://localhost:8999/api/v1/collaboration/ws/${sessionId}`
    );

    ws.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      switch (msg.type) {
        case 'user_joined':
          setUsers(prev => [...prev, msg.data.user]);
          break;

        case 'user_left':
          setUsers(prev => prev.filter(u => u.user_id !== msg.user_id));
          break;

        case 'cursor_move':
          setCursors(prev => ({
            ...prev,
            [msg.user_id]: msg.data.cursor
          }));
          break;

        case 'edit':
          // Apply the edit to local state
          applyEdit(msg.data.change);
          break;
      }
    };

    return () => ws.current?.close();
  }, [sessionId]);

  const sendCursorUpdate = (x, y, selectedStage) => {
    ws.current?.send(JSON.stringify({
      type: 'cursor',
      x, y,
      selected_stage: selectedStage
    }));
  };

  const sendEdit = (operation, targetId, data, baseVersion) => {
    ws.current?.send(JSON.stringify({
      type: 'edit',
      operation,
      target_id: targetId,
      data,
      base_version: baseVersion
    }));
  };

  return (
    <div className="collaborative-editor">
      {/* User avatars */}
      <div className="user-list">
        {users.map(user => (
          <div
            key={user.user_id}
            className="user-avatar"
            style={{ borderColor: user.color }}
          >
            {user.username[0]}
          </div>
        ))}
      </div>

      {/* Canvas with cursors */}
      <div className="canvas" onMouseMove={handleMouseMove}>
        {Object.entries(cursors).map(([userId, cursor]) => (
          <div
            key={userId}
            className="cursor"
            style={{
              left: cursor.position.x,
              top: cursor.position.y,
              backgroundColor: cursor.color
            }}
          />
        ))}
        {/* Pipeline stages... */}
      </div>
    </div>
  );
}
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/collaboration/sessions` | POST | Create session |
| `/collaboration/sessions/{id}` | GET | Get session |
| `/collaboration/sessions/join` | POST | Join session |
| `/collaboration/sessions/{id}/leave` | POST | Leave session |
| `/collaboration/sessions/{id}/end` | POST | End session |
| `/collaboration/sessions/{id}/users` | GET | Get online users |
| `/collaboration/sessions/{id}/presence` | PUT | Update presence |
| `/collaboration/sessions/{id}/edits` | POST | Send edit |
| `/collaboration/sessions/{id}/edits` | GET | Get changes |
| `/collaboration/sessions/{id}/undo` | POST | Undo |
| `/collaboration/sessions/{id}/redo` | POST | Redo |
| `/collaboration/sessions/{id}/locks` | POST | Acquire lock |
| `/collaboration/sessions/{id}/locks/{tid}` | DELETE | Release lock |
| `/collaboration/sessions/{id}/locks` | GET | Get locks |
| `/collaboration/sessions/{id}/chat` | POST | Send chat |
| `/collaboration/sessions/{id}/chat` | GET | Get messages |
| `/collaboration/sessions/{id}/comments` | POST | Add comment |
| `/collaboration/sessions/{id}/comments` | GET | Get comments |
| `/collaboration/sessions/{id}/invites` | POST | Invite user |
| `/collaboration/sessions/{id}/activity` | GET | Get activity |
| `/collaboration/ws/{id}` | WS | WebSocket |
