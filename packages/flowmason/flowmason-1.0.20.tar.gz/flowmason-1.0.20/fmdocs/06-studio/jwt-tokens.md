# Standalone JWT Tokens

FlowMason Studio includes a standalone JWT token service for authentication without external dependencies. This provides flexible token-based authentication with configurable signing and custom claims.

## Overview

Features:
- Configurable signing algorithms (HS256, HS384, HS512)
- Custom claims support
- Access + refresh token pattern
- Token rotation for security
- JTI-based revocation blacklist
- Token introspection

## Quick Start

### Issue Token Pair

```bash
curl -X POST http://localhost:8999/api/v1/tokens/issue \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "user_123",
    "org_id": "org_456",
    "scopes": ["read", "execute"],
    "name": "John Doe",
    "email": "john@example.com"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_expires_in": 2592000,
  "scope": "read execute"
}
```

### Use Token

```bash
curl http://localhost:8999/api/v1/pipelines \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## Token Endpoints

### Issue Token Pair

Create both access and refresh tokens:

```bash
curl -X POST http://localhost:8999/api/v1/tokens/issue \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "user_123",
    "org_id": "org_456",
    "scopes": ["read", "write", "execute"],
    "name": "John Doe",
    "email": "john@example.com",
    "custom_claims": {
      "role": "admin",
      "department": "engineering"
    }
  }'
```

### Create Access Token Only

For single-use tokens without refresh capability:

```bash
curl -X POST http://localhost:8999/api/v1/tokens/access \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "service_abc",
    "scopes": ["execute"],
    "expires_in": 300
  }'
```

Response:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

### Refresh Tokens

Exchange refresh token for new token pair:

```bash
curl -X POST http://localhost:8999/api/v1/tokens/refresh \
  -d "refresh_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

The old refresh token is invalidated (rotation).

### Verify Token

Verify token from Authorization header:

```bash
curl http://localhost:8999/api/v1/tokens/verify \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

Response:
```json
{
  "valid": true,
  "claims": {
    "sub": "user_123",
    "org_id": "org_456",
    "scopes": ["read", "execute"],
    "exp": 1705320000,
    "iat": 1705316400
  }
}
```

### Introspect Token

Get token metadata:

```bash
curl -X POST http://localhost:8999/api/v1/tokens/introspect \
  -d "token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

Response:
```json
{
  "active": true,
  "sub": "user_123",
  "iss": "flowmason",
  "aud": "flowmason-api",
  "exp": 1705320000,
  "iat": 1705316400,
  "jti": "jti_abc123...",
  "token_type": "access",
  "org_id": "org_456",
  "scope": "read execute"
}
```

### Revoke Token

Revoke by token:
```bash
curl -X POST http://localhost:8999/api/v1/tokens/revoke \
  -d "token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

Revoke by JTI:
```bash
curl -X POST http://localhost:8999/api/v1/tokens/revoke/jti_abc123
```

## Token Structure

### Standard Claims

| Claim | Description |
|-------|-------------|
| `sub` | Subject (user or client ID) |
| `iss` | Issuer ("flowmason" by default) |
| `aud` | Audience ("flowmason-api" by default) |
| `exp` | Expiration timestamp |
| `iat` | Issued at timestamp |
| `jti` | JWT ID (unique identifier) |

### Custom Claims

| Claim | Description |
|-------|-------------|
| `org_id` | Organization ID |
| `scopes` | Permission scopes array |
| `token_type` | "access" or "refresh" |
| `name` | User display name |
| `email` | User email |

Add any custom claims via `custom_claims`:

```json
{
  "custom_claims": {
    "role": "admin",
    "team": "platform",
    "features": ["beta", "experimental"]
  }
}
```

## Configuration

### Get Current Config

```bash
curl http://localhost:8999/api/v1/tokens/config
```

Response:
```json
{
  "issuer": "flowmason",
  "audience": "flowmason-api",
  "algorithm": "HS256",
  "access_token_expires_seconds": 3600,
  "refresh_token_expires_seconds": 2592000
}
```

### Update Configuration

```bash
curl -X PATCH http://localhost:8999/api/v1/tokens/config \
  -H "Content-Type: application/json" \
  -d '{
    "issuer": "my-company",
    "access_token_expires_seconds": 1800,
    "algorithm": "HS512"
  }'
```

### Rotate Signing Key

**Warning:** This invalidates ALL existing tokens.

```bash
curl -X POST http://localhost:8999/api/v1/tokens/config/rotate-key
```

## Signing Algorithms

| Algorithm | Type | Key Size |
|-----------|------|----------|
| HS256 | HMAC-SHA256 | 256 bits |
| HS384 | HMAC-SHA384 | 384 bits |
| HS512 | HMAC-SHA512 | 512 bits |

All algorithms use symmetric keys (same key for signing and verification).

## Token Lifetimes

| Token Type | Default Lifetime | Typical Use |
|------------|------------------|-------------|
| Access Token | 1 hour | API authentication |
| Refresh Token | 30 days | Obtaining new access tokens |

Customize via configuration or per-request:

```json
{
  "subject": "user_123",
  "expires_in": 300
}
```

## Security Best Practices

1. **Use HTTPS** in production
2. **Rotate keys periodically** using the rotate-key endpoint
3. **Keep tokens short-lived** - 1 hour or less for access tokens
4. **Implement token rotation** - use refresh flow for long sessions
5. **Revoke tokens** when users log out or on security events
6. **Validate all claims** - check issuer, audience, expiration
7. **Store refresh tokens securely** - never in localStorage
8. **Use appropriate scopes** - principle of least privilege

## Token Revocation

Tokens are revoked by adding their JTI to a blacklist. The blacklist is checked on every token verification.

```bash
# Revoke by token (extracts JTI automatically)
curl -X POST http://localhost:8999/api/v1/tokens/revoke \
  -d "token=..."

# Revoke by JTI directly
curl -X POST http://localhost:8999/api/v1/tokens/revoke/jti_abc123
```

## Debugging

### Decode Token (Without Verification)

For debugging only - does not verify signature:

```bash
curl "http://localhost:8999/api/v1/tokens/decode?token=eyJ0eXAi..."
```

Response:
```json
{
  "payload": {
    "sub": "user_123",
    "exp": 1705320000,
    ...
  },
  "warning": "Signature not verified"
}
```

### Service Statistics

```bash
curl http://localhost:8999/api/v1/tokens/stats
```

Response:
```json
{
  "revoked_token_count": 15,
  "config": {
    "issuer": "flowmason",
    "algorithm": "HS256"
  }
}
```

## Integration Examples

### Python

```python
import httpx

class FlowMasonAuth:
    def __init__(self, base_url: str = "http://localhost:8999"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None

    async def login(self, user_id: str, org_id: str = None):
        """Get tokens for a user."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/tokens/issue",
                json={
                    "subject": user_id,
                    "org_id": org_id,
                    "scopes": ["read", "execute"]
                }
            )
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            return data

    async def refresh(self):
        """Refresh tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/tokens/refresh",
                data={"refresh_token": self.refresh_token}
            )
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            return data

    def get_headers(self) -> dict:
        """Get authorization headers."""
        return {"Authorization": f"Bearer {self.access_token}"}
```

### JavaScript/Node.js

```javascript
class FlowMasonAuth {
  constructor(baseUrl = 'http://localhost:8999') {
    this.baseUrl = baseUrl;
    this.accessToken = null;
    this.refreshToken = null;
  }

  async login(userId, orgId = null) {
    const response = await fetch(`${this.baseUrl}/api/v1/tokens/issue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subject: userId,
        org_id: orgId,
        scopes: ['read', 'execute']
      })
    });
    const data = await response.json();
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    return data;
  }

  async refresh() {
    const response = await fetch(`${this.baseUrl}/api/v1/tokens/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `refresh_token=${this.refreshToken}`
    });
    const data = await response.json();
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    return data;
  }

  getHeaders() {
    return { Authorization: `Bearer ${this.accessToken}` };
  }
}
```

## Comparison with OAuth 2.0

| Feature | JWT Tokens | OAuth 2.0 |
|---------|------------|-----------|
| External Auth | Not needed | Required for auth code flow |
| Client Registration | Not needed | Required |
| Complexity | Simple | More complex |
| Use Case | Internal services | Third-party apps |
| Token Format | JWT | JWT or opaque |

Use JWT tokens for:
- Service-to-service auth
- Internal applications
- Simple authentication needs

Use OAuth 2.0 for:
- Third-party integrations
- User consent flows
- External client management
