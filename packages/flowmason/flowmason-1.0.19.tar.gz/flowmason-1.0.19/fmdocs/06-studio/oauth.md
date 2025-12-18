# OAuth 2.0 Support

FlowMason Studio supports OAuth 2.0 for secure third-party application access. This enables integrations, external tools, and service-to-service authentication.

## Overview

Supported OAuth 2.0 flows:

| Flow | Use Case |
|------|----------|
| Authorization Code + PKCE | Web applications, SPAs, mobile apps |
| Client Credentials | Service-to-service, backend integrations |
| Refresh Token | Long-lived access with token rotation |

## Quick Start

### 1. Register an OAuth Client

```bash
curl -X POST http://localhost:8999/api/v1/oauth/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Integration",
    "redirect_uris": ["https://myapp.com/callback"],
    "grant_types": ["authorization_code", "refresh_token"],
    "scopes": ["read", "execute"]
  }'
```

Response:
```json
{
  "client_id": "oa_abc123...",
  "client_secret": "xyz789...",
  "name": "My Integration",
  "redirect_uris": ["https://myapp.com/callback"],
  "grant_types": ["authorization_code", "refresh_token"],
  "scopes": ["read", "execute"],
  "is_confidential": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

**Important:** Save the `client_secret` - it's only shown once.

### 2. Get Access Token

#### Authorization Code Flow (Web Apps)

1. Redirect user to authorization endpoint:
```
GET /api/v1/oauth/authorize?
  response_type=code&
  client_id=oa_abc123&
  redirect_uri=https://myapp.com/callback&
  scope=read execute&
  state=random_state_value
```

2. User is redirected back with code:
```
https://myapp.com/callback?code=auth_code_xyz&state=random_state_value
```

3. Exchange code for tokens:
```bash
curl -X POST http://localhost:8999/api/v1/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=auth_code_xyz" \
  -d "redirect_uri=https://myapp.com/callback" \
  -d "client_id=oa_abc123" \
  -d "client_secret=xyz789"
```

#### Client Credentials Flow (Service-to-Service)

```bash
curl -X POST http://localhost:8999/api/v1/oauth/token \
  -d "grant_type=client_credentials" \
  -d "client_id=oa_abc123" \
  -d "client_secret=xyz789" \
  -d "scope=read execute"
```

### 3. Use Access Token

```bash
curl http://localhost:8999/api/v1/pipelines \
  -H "Authorization: Bearer access_token_here"
```

## Client Management

### Register Client

```bash
curl -X POST http://localhost:8999/api/v1/oauth/clients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My App",
    "description": "Integration for pipeline automation",
    "redirect_uris": ["https://myapp.com/callback", "http://localhost:3000/callback"],
    "grant_types": ["authorization_code", "refresh_token", "client_credentials"],
    "scopes": ["read", "write", "execute"],
    "is_confidential": true
  }'
```

### List Clients

```bash
curl http://localhost:8999/api/v1/oauth/clients?org_id=org_default
```

### Get Client Details

```bash
curl http://localhost:8999/api/v1/oauth/clients/{client_id}
```

### Delete Client

```bash
curl -X DELETE http://localhost:8999/api/v1/oauth/clients/{client_id}
```

This also revokes all tokens issued to the client.

### Regenerate Client Secret

```bash
curl -X POST http://localhost:8999/api/v1/oauth/clients/{client_id}/regenerate-secret
```

The old secret is immediately invalidated.

## Authorization Code Flow

### With PKCE (Recommended)

PKCE (Proof Key for Code Exchange) is recommended for all clients, especially public clients (SPAs, mobile apps).

1. Generate code verifier and challenge:
```javascript
// Generate random verifier (43-128 characters)
const verifier = generateRandomString(64);

// Create S256 challenge
const challenge = base64url(sha256(verifier));
```

2. Include in authorization request:
```
GET /api/v1/oauth/authorize?
  response_type=code&
  client_id=oa_abc123&
  redirect_uri=https://myapp.com/callback&
  scope=read execute&
  state=random_state&
  code_challenge=challenge_here&
  code_challenge_method=S256
```

3. Include verifier in token exchange:
```bash
curl -X POST http://localhost:8999/api/v1/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=auth_code_xyz" \
  -d "redirect_uri=https://myapp.com/callback" \
  -d "client_id=oa_abc123" \
  -d "code_verifier=verifier_here"
```

### Without PKCE (Confidential Clients Only)

```bash
curl -X POST http://localhost:8999/api/v1/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=auth_code_xyz" \
  -d "redirect_uri=https://myapp.com/callback" \
  -d "client_id=oa_abc123" \
  -d "client_secret=xyz789"
```

## Token Refresh

Access tokens expire after 1 hour. Use refresh tokens to get new access tokens:

```bash
curl -X POST http://localhost:8999/api/v1/oauth/token \
  -d "grant_type=refresh_token" \
  -d "refresh_token=rtok_xyz" \
  -d "client_id=oa_abc123" \
  -d "client_secret=xyz789"
```

Response includes a new refresh token (rotation):
```json
{
  "access_token": "new_access_token",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "new_refresh_token",
  "scope": "read execute"
}
```

**Important:** Use the new refresh token for subsequent refreshes.

## Token Introspection

Validate a token (RFC 7662):

```bash
curl -X POST http://localhost:8999/api/v1/oauth/introspect \
  -d "token=access_token_here"
```

Response:
```json
{
  "active": true,
  "token_type": "Bearer",
  "scope": "read execute",
  "client_id": "oa_abc123",
  "sub": "user_xyz",
  "exp": 1705320000,
  "iat": 1705316400
}
```

Inactive/expired tokens return:
```json
{
  "active": false
}
```

## Token Revocation

Revoke a token (RFC 7009):

```bash
curl -X POST http://localhost:8999/api/v1/oauth/revoke \
  -d "token=access_token_here"
```

Always returns success (per RFC 7009).

## Scopes

| Scope | Description |
|-------|-------------|
| `read` | Read access to pipelines, components |
| `write` | Create and edit pipelines |
| `execute` | Run pipeline executions |
| `admin` | Administrative operations |
| `openid` | OpenID Connect (user identity) |
| `profile` | User profile information |
| `email` | User email address |

Request scopes in the authorization request:
```
scope=read execute write
```

## Client Types

### Confidential Clients

Server-side applications that can securely store secrets.

```json
{
  "name": "Backend Service",
  "is_confidential": true,
  "grant_types": ["client_credentials", "authorization_code", "refresh_token"]
}
```

### Public Clients

Browser apps (SPAs) and mobile apps that cannot securely store secrets.

```json
{
  "name": "Mobile App",
  "is_confidential": false,
  "grant_types": ["authorization_code", "refresh_token"]
}
```

**Note:** Public clients MUST use PKCE and cannot use client_credentials flow.

## Server Metadata

Discover server configuration (RFC 8414):

```bash
curl http://localhost:8999/api/v1/oauth/.well-known/oauth-authorization-server
```

Response:
```json
{
  "issuer": "http://localhost:8999",
  "authorization_endpoint": "http://localhost:8999/api/v1/oauth/authorize",
  "token_endpoint": "http://localhost:8999/api/v1/oauth/token",
  "introspection_endpoint": "http://localhost:8999/api/v1/oauth/introspect",
  "revocation_endpoint": "http://localhost:8999/api/v1/oauth/revoke",
  "registration_endpoint": "http://localhost:8999/api/v1/oauth/clients",
  "scopes_supported": ["read", "write", "execute", "admin", "openid", "profile", "email"],
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "client_credentials", "refresh_token"],
  "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post", "none"],
  "code_challenge_methods_supported": ["plain", "S256"]
}
```

## Security Best Practices

1. **Always use HTTPS** in production
2. **Use PKCE** for all authorization code flows
3. **Validate redirect URIs** - register exact URIs
4. **Store secrets securely** - never in client-side code
5. **Use short-lived access tokens** (1 hour default)
6. **Rotate refresh tokens** - old tokens are invalidated
7. **Validate state parameter** to prevent CSRF
8. **Request minimal scopes** needed for your use case

## Example: Node.js Integration

```javascript
const axios = require('axios');

class FlowMasonOAuth {
  constructor(clientId, clientSecret, baseUrl = 'http://localhost:8999') {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.baseUrl = baseUrl;
  }

  // Client credentials flow
  async getServiceToken(scopes = ['read', 'execute']) {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/oauth/token`,
      new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: this.clientId,
        client_secret: this.clientSecret,
        scope: scopes.join(' '),
      })
    );
    return response.data;
  }

  // Refresh token
  async refreshToken(refreshToken) {
    const response = await axios.post(
      `${this.baseUrl}/api/v1/oauth/token`,
      new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: refreshToken,
        client_id: this.clientId,
        client_secret: this.clientSecret,
      })
    );
    return response.data;
  }
}

// Usage
const oauth = new FlowMasonOAuth('oa_abc123', 'secret_xyz');
const tokens = await oauth.getServiceToken();
console.log('Access token:', tokens.access_token);
```

## Example: Python Integration

```python
import httpx

class FlowMasonOAuth:
    def __init__(self, client_id: str, client_secret: str, base_url: str = "http://localhost:8999"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url

    async def get_service_token(self, scopes: list[str] = None) -> dict:
        """Get token via client credentials flow."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": " ".join(scopes or ["read", "execute"]),
                }
            )
            response.raise_for_status()
            return response.json()

    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }
            )
            response.raise_for_status()
            return response.json()

# Usage
import asyncio

async def main():
    oauth = FlowMasonOAuth("oa_abc123", "secret_xyz")
    tokens = await oauth.get_service_token()
    print(f"Access token: {tokens['access_token']}")

asyncio.run(main())
```

## Token Lifetimes

| Token Type | Default Lifetime |
|------------|------------------|
| Authorization Code | 10 minutes |
| Access Token | 1 hour |
| Refresh Token | 30 days |

## Error Responses

OAuth errors follow RFC 6749:

```json
{
  "error": "invalid_grant",
  "error_description": "Invalid or expired code"
}
```

Common errors:

| Error | Description |
|-------|-------------|
| `invalid_request` | Missing required parameter |
| `invalid_client` | Client authentication failed |
| `invalid_grant` | Invalid code or refresh token |
| `unauthorized_client` | Client not authorized for grant type |
| `unsupported_grant_type` | Grant type not supported |
| `invalid_scope` | Requested scope not allowed |
