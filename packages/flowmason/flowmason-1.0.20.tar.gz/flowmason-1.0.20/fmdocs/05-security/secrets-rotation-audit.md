# Secrets Rotation & Audit

FlowMason provides comprehensive secrets management with automatic rotation policies and full audit logging for compliance and security monitoring.

## Overview

The secrets service provides:
- **Encryption**: Fernet (AES-128) symmetric encryption
- **Key Derivation**: PBKDF2 with per-organization salts
- **Rotation Policies**: Scheduled and automatic rotation
- **Audit Logging**: Complete access history with actor tracking
- **Expiration**: Optional secret expiration with warnings

## Basic Usage

```python
from flowmason_studio.services.secrets import get_secrets_service

# Get secrets service for your organization
secrets = get_secrets_service("my-org")

# Store a secret
secrets.set(
    name="OPENAI_API_KEY",
    value="sk-...",
    description="OpenAI API key for production",
    category="api_key",
    created_by="user@example.com",
)

# Retrieve a secret
value = secrets.get("OPENAI_API_KEY", actor="user@example.com")
```

## Rotation Policies

### Setting a Rotation Policy

```python
# Set a 90-day rotation policy with 7-day warning
policy = secrets.set_rotation_policy(
    secret_name="OPENAI_API_KEY",
    rotation_interval_days=90,
    notify_before_days=7,
    auto_rotate=False,
    actor="admin@example.com",
)

print(f"Next rotation: {policy.next_rotation}")
```

### Checking Rotation Status

```python
# Get secrets due for rotation
due_secrets = secrets.get_secrets_due_for_rotation()

for policy in due_secrets:
    print(f"{policy.secret_name}: due on {policy.next_rotation}")
```

### Manual Secret Rotation

```python
# Rotate a secret with a new value
secrets.rotate_secret(
    secret_name="OPENAI_API_KEY",
    new_value="sk-new-key...",
    actor="admin@example.com",
    actor_ip="192.168.1.100",
)
```

### Automatic Rotation

For secrets that can be automatically rotated (e.g., database passwords), you can register rotation handlers:

```python
# Define a rotation handler
def rotate_db_password(secret_name: str, current_value: str) -> str:
    import secrets as py_secrets
    new_password = py_secrets.token_urlsafe(32)
    # Update database with new password here
    return new_password

# Register the handler
secrets.register_rotation_handler("db_password_rotator", rotate_db_password)

# Set policy with auto-rotation
secrets.set_rotation_policy(
    secret_name="DATABASE_PASSWORD",
    rotation_interval_days=30,
    auto_rotate=True,
    rotation_handler="db_password_rotator",
)

# Run auto-rotations (typically via scheduler)
rotated = secrets.run_auto_rotations(actor="system:scheduler")
print(f"Rotated secrets: {rotated}")
```

### Master Key Rotation

Rotate the master encryption key to re-encrypt all secrets:

```python
# Rotate master key (re-encrypts all secrets)
count = secrets.rotate_key(
    new_master_key="new-secure-master-key-32chars",
    actor="admin@example.com",
)
print(f"Re-encrypted {count} secrets")
```

## Audit Logging

All secret operations are automatically logged with full context.

### Logged Actions

| Action | Description |
|--------|-------------|
| `create` | New secret created |
| `read` | Secret value accessed |
| `update` | Secret value updated |
| `delete` | Secret deleted |
| `rotate_key` | Master key rotated |
| `rotation_scheduled` | Rotation policy created |
| `rotation_completed` | Secret rotated |
| `expiration_warning` | Secret nearing expiration |
| `access_denied` | Access attempt failed |

### Querying Audit Logs

```python
from datetime import datetime, timedelta

# Get all logs from the last 7 days
logs = secrets.get_audit_logs(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
    limit=100,
)

for log in logs:
    print(f"[{log.timestamp}] {log.action} on {log.secret_name} by {log.actor}")
```

### Filter by Secret

```python
# Get access history for a specific secret
history = secrets.get_secret_access_history("OPENAI_API_KEY", days=30)

print(f"Access count: {len(history)}")
for entry in history:
    print(f"  {entry.timestamp}: {entry.action} by {entry.actor}")
```

### Filter by Actor

```python
# Get all activity by a specific user
activity = secrets.get_actor_activity("user@example.com", days=30)

for entry in activity:
    print(f"  {entry.timestamp}: {entry.action} on {entry.secret_name}")
```

### Failed Access Attempts

```python
# Get failed access attempts (security monitoring)
failures = secrets.get_failed_access_attempts(days=7)

if failures:
    print(f"WARNING: {len(failures)} failed access attempts!")
    for entry in failures:
        print(f"  {entry.timestamp}: {entry.secret_name}")
        print(f"    Actor: {entry.actor}, IP: {entry.actor_ip}")
        print(f"    Error: {entry.error_message}")
```

### Export Audit Logs

```python
# Export to JSON
json_export = secrets.export_audit_logs(
    start_date=datetime(2024, 1, 1),
    end_date=datetime.now(),
    format="json",
)

# Export to CSV
csv_export = secrets.export_audit_logs(
    start_date=datetime(2024, 1, 1),
    end_date=datetime.now(),
    format="csv",
)

# Save to file
with open("secrets_audit.csv", "w") as f:
    f.write(csv_export)
```

## Audit Log Entry Fields

Each audit log entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique entry ID |
| `timestamp` | string | ISO 8601 timestamp |
| `action` | string | Action type (see above) |
| `secret_name` | string | Name of the secret |
| `org_id` | string | Organization ID |
| `actor` | string | User/system performing action |
| `actor_ip` | string | IP address of actor |
| `details` | object | Additional context |
| `success` | boolean | Whether action succeeded |
| `error_message` | string | Error details if failed |

## Storage

Audit logs are stored in JSONL format (one entry per line) organized by date:

```
~/.flowmason/secrets/<org-hash>/
├── <secret-hash>.secret     # Encrypted secret value
├── <secret-hash>.meta       # Secret metadata
├── policies/
│   └── <secret-hash>.policy # Rotation policy
└── audit/
    ├── 2024-01-01.jsonl     # Daily audit logs
    ├── 2024-01-02.jsonl
    └── ...
```

## Security Best Practices

1. **Set FLOWMASON_SECRETS_KEY**: Use a strong master key in production
   ```bash
   export FLOWMASON_SECRETS_KEY="your-32-character-master-key..."
   ```

2. **Rotate Keys Regularly**: Rotate master keys quarterly or after security incidents

3. **Monitor Failed Attempts**: Set up alerts for failed access attempts

4. **Review Audit Logs**: Regularly review who is accessing secrets

5. **Use Expiration**: Set expiration dates for temporary secrets

6. **Limit Access**: Only grant secret access to required services/users

## API Reference

### SecretsService Methods

#### Rotation Policy Management

| Method | Description |
|--------|-------------|
| `set_rotation_policy()` | Create/update rotation policy |
| `get_rotation_policy()` | Get policy for a secret |
| `delete_rotation_policy()` | Remove rotation policy |
| `list_rotation_policies()` | List all policies |
| `get_secrets_due_for_rotation()` | Get secrets needing rotation |
| `rotate_secret()` | Rotate a specific secret |
| `register_rotation_handler()` | Register auto-rotation handler |
| `run_auto_rotations()` | Execute due auto-rotations |
| `rotate_key()` | Rotate master encryption key |

#### Audit Log Queries

| Method | Description |
|--------|-------------|
| `get_audit_logs()` | Query audit logs with filters |
| `get_secret_access_history()` | Get history for a secret |
| `get_actor_activity()` | Get activity by actor |
| `get_failed_access_attempts()` | Get failed attempts |
| `export_audit_logs()` | Export logs to JSON/CSV |

## Integration Example

```python
from datetime import datetime, timedelta
from flowmason_studio.services.secrets import get_secrets_service

# Initialize
secrets = get_secrets_service("production")

# Create a secret with rotation policy
secrets.set(
    name="API_KEY",
    value="secret-value",
    category="api_key",
    created_by="admin",
)

secrets.set_rotation_policy(
    secret_name="API_KEY",
    rotation_interval_days=90,
    notify_before_days=14,
    actor="admin",
)

# Use the secret (automatically logged)
api_key = secrets.get("API_KEY", actor="service:api-gateway")

# Check rotation status
due = secrets.get_secrets_due_for_rotation()
for policy in due:
    print(f"Rotate {policy.secret_name} by {policy.next_rotation}")

# Review recent activity
logs = secrets.get_audit_logs(
    start_date=datetime.now() - timedelta(days=1),
    limit=50,
)
print(f"Last 24h: {len(logs)} secret operations")
```
