# Secrets Management

FlowMason provides encrypted storage for sensitive values like API keys, tokens, and credentials.

## Overview

The secrets management system:
- Uses Fernet symmetric encryption (AES-128)
- Derives per-organization encryption keys
- Supports key rotation
- Logs all secret access for auditing

## Installation

Install with secrets support:

```bash
pip install flowmason[secrets]
```

Or install cryptography separately:

```bash
pip install cryptography
```

## Configuration

### Environment Variable

Set the master encryption key:

```bash
export FLOWMASON_SECRETS_KEY="your-32-char-secret-key-here"
```

**Important:** This key is used to derive organization-specific encryption keys. Keep it secure!

If not set, a default key is derived from the organization ID (not recommended for production).

### Storage Location

Secrets are stored in:
- `~/.flowmason/secrets/<org-hash>/`

Each secret has two files:
- `<secret-hash>.secret` - Encrypted value
- `<secret-hash>.meta` - Unencrypted metadata (name, description, category)

## API Endpoints

### List Secrets

```http
GET /api/v1/secrets
Authorization: Bearer <api-key>
```

Returns metadata for all secrets (no values).

### Create/Update Secret

```http
POST /api/v1/secrets
Authorization: Bearer <api-key>
Content-Type: application/json

{
  "name": "OPENAI_API_KEY",
  "value": "sk-...",
  "description": "OpenAI API key for production",
  "category": "api_key",
  "expires_at": "2025-12-31T23:59:59Z"
}
```

Categories: `api_key`, `token`, `credential`, `other`

### Get Secret Value

```http
GET /api/v1/secrets/{name}
Authorization: Bearer <api-key>
```

Requires full API key scope. Access is audit logged.

### Delete Secret

```http
DELETE /api/v1/secrets/{name}
Authorization: Bearer <api-key>
```

### Get Metadata Only

```http
GET /api/v1/secrets/{name}/metadata
Authorization: Bearer <api-key>
```

Returns metadata without the value.

## Python API

```python
from flowmason_studio.services.secrets import SecretsService

# Initialize for an organization
secrets = SecretsService(org_id="my-org")

# Store a secret
secrets.set(
    name="OPENAI_API_KEY",
    value="sk-...",
    description="OpenAI API key",
    category="api_key"
)

# Retrieve a secret
value = secrets.get("OPENAI_API_KEY")

# List all secrets (metadata only)
for secret in secrets.list():
    print(f"{secret.name}: {secret.category}")

# Check if secret exists
if secrets.exists("OPENAI_API_KEY"):
    ...

# Delete a secret
secrets.delete("OPENAI_API_KEY")
```

## Key Rotation

Rotate the master encryption key:

```python
secrets.rotate_key("new-master-key")
```

This re-encrypts all secrets with the new key.

## Security Best Practices

1. **Set FLOWMASON_SECRETS_KEY** in production
2. **Rotate keys periodically** (recommended: every 90 days)
3. **Use expiration dates** for temporary credentials
4. **Monitor audit logs** for suspicious access
5. **Limit scope** - only use full-scope API keys when needed

## Audit Logging

All secret operations are logged:
- `secret.create` - Secret created or updated
- `secret.read` - Secret value accessed
- `secret.delete` - Secret deleted

View audit logs:

```http
GET /api/v1/auth/audit-log?resource_type=secret
```

## Integration with Pipelines

Secrets can be referenced in pipelines using the `secrets` context:

```json
{
  "stages": [
    {
      "id": "call-api",
      "component_type": "http_request",
      "config": {
        "headers": {
          "Authorization": "Bearer {{secrets.OPENAI_API_KEY}}"
        }
      }
    }
  ]
}
```

The executor resolves `{{secrets.NAME}}` at runtime from the organization's encrypted storage.

## Error Handling

| Error | Meaning |
|-------|---------|
| 404 | Secret not found |
| 410 | Secret expired |
| 500 | Decryption failed (key mismatch) |
