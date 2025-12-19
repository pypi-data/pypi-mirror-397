# Pipeline-Level Permissions

FlowMason provides fine-grained access control for pipelines, allowing you to control who can view, run, edit, and manage your workflows.

## Overview

The permission system supports:
- **Permission Levels**: VIEW, RUN, EDIT, ADMIN with hierarchical inheritance
- **Visibility Settings**: Private, Organization, Public
- **Principal Types**: Users, Organizations, Teams, API Keys
- **Folder Inheritance**: Pipelines can inherit permissions from parent folders
- **Expiring Grants**: Time-limited access for temporary collaborations

## Permission Levels

| Level | Capabilities |
|-------|-------------|
| `view` | View pipeline definition and execution history |
| `run` | Execute pipeline (includes view) |
| `edit` | Modify pipeline definition (includes run) |
| `admin` | Full control including permission management |

Higher permission levels include all capabilities of lower levels.

## Visibility Settings

| Visibility | Description |
|------------|-------------|
| `private` | Only owner and explicit grants can access |
| `org` | All organization members can view |
| `public` | All authenticated users can view |

## API Reference

### Get Pipeline Permissions

```http
GET /api/v1/permissions/{pipeline_id}
```

Returns the full permission configuration for a pipeline.

**Response:**
```json
{
  "pipeline_id": "pipe_abc123",
  "owner_id": "user_xyz",
  "visibility": "private",
  "inherit_from_folder": true,
  "folder_id": "folder_001",
  "grants": [
    {
      "id": "grant_001",
      "principal_type": "user",
      "principal_id": "user_123",
      "level": "edit",
      "granted_by": "user_xyz",
      "granted_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Create Pipeline Permissions

```http
POST /api/v1/permissions/{pipeline_id}
```

Creates initial permissions for a new pipeline. The current user becomes the owner.

**Query Parameters:**
- `visibility` (optional): Initial visibility setting
- `folder_id` (optional): Parent folder for inheritance

### Update Visibility

```http
PUT /api/v1/permissions/{pipeline_id}/visibility
```

**Request Body:**
```json
{
  "visibility": "org"
}
```

### Grant Permission

```http
POST /api/v1/permissions/{pipeline_id}/grants
```

**Request Body:**
```json
{
  "principal_type": "user",
  "principal_id": "user_456",
  "level": "run",
  "expires_at": "2024-06-01T00:00:00Z"
}
```

### Remove Permission Grant

```http
DELETE /api/v1/permissions/{pipeline_id}/grants/{principal_type}/{principal_id}
```

### Check Permission

```http
GET /api/v1/permissions/{pipeline_id}/check?level=run
```

**Response:**
```json
{
  "has_access": true,
  "effective_level": "edit",
  "grant_source": "direct"
}
```

### Get Effective Permissions

```http
GET /api/v1/permissions/{pipeline_id}/effective
```

Returns detailed information about how permissions are resolved for the current user.

**Response:**
```json
{
  "pipeline_id": "pipe_abc123",
  "user_id": "current_user",
  "is_owner": false,
  "effective_level": "edit",
  "direct_grant": {
    "principal_type": "user",
    "principal_id": "current_user",
    "level": "edit"
  },
  "inherited_grants": [],
  "visibility_access": false,
  "can_view": true,
  "can_run": true,
  "can_edit": true,
  "can_admin": false
}
```

### Share Pipeline (Convenience Endpoint)

```http
POST /api/v1/permissions/{pipeline_id}/share
```

Share a pipeline with multiple users, organizations, or teams at once.

**Request Body:**
```json
{
  "users": ["user_123", "user_456"],
  "orgs": ["org_acme"],
  "teams": ["team_dev"],
  "level": "run",
  "make_public": false
}
```

### List Accessible Pipelines

```http
GET /api/v1/permissions/user/accessible?min_level=view
```

List all pipelines the current user can access at a minimum level.

## Python Integration

### Using Permission Dependencies

```python
from fastapi import Depends
from flowmason_studio.auth.permissions import (
    require_view,
    require_run,
    require_edit,
    require_admin,
    get_user_context,
    UserContext,
)

@router.get("/{pipeline_id}")
async def get_pipeline(
    pipeline_id: str,
    user: UserContext = Depends(require_view()),
):
    """Requires VIEW permission."""
    ...

@router.post("/{pipeline_id}/run")
async def run_pipeline(
    pipeline_id: str,
    user: UserContext = Depends(require_run()),
):
    """Requires RUN permission."""
    ...
```

### Manual Permission Checking

```python
from flowmason_studio.auth.permissions import (
    permission_checker,
    get_user_context,
)

@router.get("/{pipeline_id}/details")
async def get_details(
    pipeline_id: str,
    user: UserContext = Depends(get_user_context),
):
    # Check multiple permissions
    if permission_checker.can_edit(pipeline_id, user):
        # Show edit controls
        ...
    elif permission_checker.can_view(pipeline_id, user):
        # Read-only view
        ...
    else:
        raise HTTPException(status_code=403)
```

### Storage API

```python
from flowmason_studio.services.permission_storage import get_permission_storage
from flowmason_studio.models.permissions import (
    PermissionLevel,
    PipelineVisibility,
    PrincipalType,
)

storage = get_permission_storage()

# Create permissions for a new pipeline
perms = storage.create_pipeline_permissions(
    pipeline_id="pipe_123",
    owner_id="user_abc",
    visibility=PipelineVisibility.PRIVATE,
)

# Grant access
storage.add_grant(
    pipeline_id="pipe_123",
    principal_type=PrincipalType.USER,
    principal_id="user_xyz",
    level=PermissionLevel.RUN,
    granted_by="user_abc",
)

# Check access
has_access = storage.check_permission(
    pipeline_id="pipe_123",
    user_id="user_xyz",
    required_level=PermissionLevel.RUN,
)

# Get effective permissions
effective = storage.get_effective_permissions(
    pipeline_id="pipe_123",
    user_id="user_xyz",
    user_orgs=["org_acme"],
    user_teams=["team_dev"],
)
print(f"Can edit: {effective.can_edit}")
```

## Folder Inheritance

Pipelines can inherit permissions from parent folders:

```python
# Create folder permissions
storage.create_folder_permissions(
    folder_id="folder_projects",
    owner_id="user_admin",
    visibility=PipelineVisibility.ORG,
)

# Grant team access to folder
storage.add_folder_grant(
    folder_id="folder_projects",
    principal_type=PrincipalType.TEAM,
    principal_id="team_dev",
    level=PermissionLevel.EDIT,
    granted_by="user_admin",
)

# Pipeline in folder inherits permissions
storage.create_pipeline_permissions(
    pipeline_id="pipe_new",
    owner_id="user_abc",
    folder_id="folder_projects",  # Inherits from this folder
)
```

## OAuth Scope Integration

Pipeline permissions work alongside OAuth scopes:

| Scope | Permissions |
|-------|-------------|
| `full` | All operations |
| `read` | List/get pipelines, view executions |
| `execute` | Run pipelines (requires `run` permission) |
| `write` | Create/modify pipelines (requires `edit` permission) |

Both scope AND pipeline permission must be satisfied:

```python
from flowmason_studio.auth.permissions import require_scope, require_run

@router.post("/{pipeline_id}/run")
async def run_pipeline(
    pipeline_id: str,
    user: UserContext = Depends(require_scope("execute")),
    _: UserContext = Depends(require_run()),
):
    """Requires both 'execute' scope AND 'run' permission."""
    ...
```

## Best Practices

1. **Least Privilege**: Grant the minimum permission level needed
2. **Use Teams**: Organize users into teams for easier management
3. **Folder Structure**: Use folders to organize pipelines and share permissions
4. **Expiring Grants**: Use expiration for temporary access
5. **Audit**: Track `granted_by` for permission auditing
6. **Visibility**: Start with `private`, expand as needed

## Troubleshooting

### Permission Denied

1. Check effective permissions: `GET /permissions/{pipeline_id}/effective`
2. Verify JWT token contains correct user ID
3. Check if user is in required org/team
4. Verify grant hasn't expired

### Inheritance Not Working

1. Verify `inherit_from_folder` is `true`
2. Check folder permissions exist
3. Verify folder hierarchy (no circular references)

### API Key Access

1. API keys need explicit grants or public visibility
2. Check API key scopes match operation
3. Use principal type `api_key` for API key grants
