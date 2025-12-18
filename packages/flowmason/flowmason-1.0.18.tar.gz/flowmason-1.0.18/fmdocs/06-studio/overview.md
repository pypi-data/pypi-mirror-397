# FlowMason Studio

**Version 1.0.0** | **All Features Complete**

Studio is the backend server that provides REST APIs, real-time capabilities, and advanced features for FlowMason.

## Overview

Studio provides:
- REST API for pipeline management and execution
- WebSocket for real-time execution updates
- Full debugging and testing endpoints
- Comprehensive authentication (API keys, OAuth 2.0, JWT, SAML/SSO)
- Pipeline scheduling (cron) and webhook triggers
- Public marketplace for pipeline sharing
- Time travel debugging with execution snapshots
- Database storage with multi-tenancy support
- Security hardening (bcrypt, Redis rate limiting)

## Starting Studio

### From CLI

```bash
# Start with defaults
fm studio start

# Start on custom port
fm studio start --port 9000

# Check status
fm studio status

# Stop
fm studio stop

# Restart
fm studio restart
```

### From VSCode

- Command Palette > "FlowMason: Start Studio"
- Status bar shows connection status

### Programmatically

```python
from flowmason_studio.api.app import run_server

run_server(host="127.0.0.1", port=8999)
```

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Component Registry

```
GET /api/v1/registry/components
GET /api/v1/registry/components/{component_type}
GET /api/v1/registry/packages
POST /api/v1/registry/packages/install
DELETE /api/v1/registry/packages/{package_id}
```

### Pipelines

```
GET /api/v1/pipelines
GET /api/v1/pipelines/{pipeline_id}
POST /api/v1/pipelines
PUT /api/v1/pipelines/{pipeline_id}
DELETE /api/v1/pipelines/{pipeline_id}
POST /api/v1/pipelines/{pipeline_id}/clone
POST /api/v1/pipelines/{pipeline_id}/publish
POST /api/v1/pipelines/{pipeline_id}/unpublish
```

### Execution

```
POST /api/v1/run                           # Run pipeline by name (new)
POST /api/v1/runs
GET /api/v1/runs/{run_id}
GET /api/v1/runs/{run_id}/status
POST /api/v1/runs/{run_id}/pause
POST /api/v1/runs/{run_id}/resume
POST /api/v1/runs/{run_id}/step
POST /api/v1/runs/{run_id}/stop
POST /api/v1/runs/{run_id}/set-breakpoint
POST /api/v1/runs/{run_id}/clear-breakpoint
```

### Input/Output (New)

```
# Named Pipeline Invocation
POST /api/v1/run                           # Run by name: {"pipeline": "my-pipe@1.0.0"}

# Output Destination Allowlist
POST /api/v1/allowlist                     # Create allowlist entry
GET /api/v1/allowlist                      # List allowlist entries
PATCH /api/v1/allowlist/{id}               # Update entry
DELETE /api/v1/allowlist/{id}              # Delete entry
POST /api/v1/allowlist/validate            # Validate destination

# Stored Connections
POST /api/v1/connections                   # Create stored connection
GET /api/v1/connections                    # List connections
PATCH /api/v1/connections/{id}             # Update connection
DELETE /api/v1/connections/{id}            # Delete connection

# Delivery Logs
GET /api/v1/deliveries/{run_id}            # Get delivery log for run
```

See [Input/Output Architecture](api/input-output.md) for full documentation.

### Testing

```
POST /api/v1/tests/run
GET /api/v1/tests/{test_id}/status
GET /api/v1/tests/{test_id}/results
```

### Authentication

```
POST /api/v1/auth/api-keys
GET /api/v1/auth/api-keys
DELETE /api/v1/auth/api-keys/{key_id}
GET /api/v1/auth/me
```

### OAuth 2.0

```
GET /api/v1/oauth/authorize
POST /api/v1/oauth/token
POST /api/v1/oauth/revoke
GET /api/v1/oauth/clients
POST /api/v1/oauth/clients
```

### JWT Sessions

```
POST /api/v1/auth/login                # Get access + refresh tokens
POST /api/v1/auth/refresh              # Refresh access token
POST /api/v1/auth/logout               # Revoke tokens
POST /api/v1/auth/password-reset       # Request password reset
POST /api/v1/auth/password-reset/confirm  # Complete password reset
```

### SAML/SSO

```
GET /api/v1/auth/saml/metadata/{org_id}
GET /api/v1/auth/saml/login/{org_id}
POST /api/v1/auth/saml/acs/{org_id}
GET /api/v1/auth/saml/config/{org_id}
PUT /api/v1/auth/saml/config/{org_id}
POST /api/v1/auth/saml/logout/{org_id}   # SAML Single Logout
```

### Scheduling

```
POST /api/v1/schedules                 # Create cron schedule
GET /api/v1/schedules                  # List schedules
GET /api/v1/schedules/{schedule_id}    # Get schedule
PATCH /api/v1/schedules/{schedule_id}  # Update schedule
DELETE /api/v1/schedules/{schedule_id} # Delete schedule
POST /api/v1/schedules/{schedule_id}/enable
POST /api/v1/schedules/{schedule_id}/disable
```

### Webhooks

```
POST /api/v1/webhooks                  # Create webhook trigger
GET /api/v1/webhooks                   # List webhooks
GET /api/v1/webhooks/{webhook_id}      # Get webhook
PATCH /api/v1/webhooks/{webhook_id}    # Update webhook
DELETE /api/v1/webhooks/{webhook_id}   # Delete webhook
POST /api/v1/webhooks/{webhook_id}/trigger  # Manual trigger
```

### Marketplace

```
GET /api/v1/marketplace/featured       # Featured listings
GET /api/v1/marketplace/trending       # Trending listings
GET /api/v1/marketplace/new            # New listings
GET /api/v1/marketplace/categories     # Categories
GET /api/v1/marketplace/search         # Search listings
GET /api/v1/marketplace/listings/{id}  # Get listing details
POST /api/v1/marketplace/listings/{id}/install  # Install to workspace
GET /api/v1/marketplace/publishers/{id}  # Publisher profile
POST /api/v1/marketplace/favorites/{id}  # Add to favorites
DELETE /api/v1/marketplace/favorites/{id}  # Remove from favorites
```

### Time Travel Debugging

```
GET /api/v1/time-travel/{run_id}/timeline    # Get execution timeline
GET /api/v1/time-travel/{run_id}/snapshots   # List snapshots
GET /api/v1/time-travel/{run_id}/snapshots/{snapshot_id}  # Get snapshot
GET /api/v1/time-travel/{run_id}/diff        # Compare snapshots
POST /api/v1/time-travel/{run_id}/step-back  # Step to previous
POST /api/v1/time-travel/{run_id}/step-forward  # Step to next
POST /api/v1/time-travel/{run_id}/replay     # Replay from snapshot
POST /api/v1/time-travel/{run_id}/what-if    # What-if analysis
```

### Prompt Library

```
GET /api/v1/prompts                    # List prompts
POST /api/v1/prompts                   # Create prompt
GET /api/v1/prompts/{prompt_id}        # Get prompt
PATCH /api/v1/prompts/{prompt_id}      # Update prompt
DELETE /api/v1/prompts/{prompt_id}     # Delete prompt
GET /api/v1/prompts/{prompt_id}/versions  # Prompt versions
```

### Template Gallery

```
GET /api/v1/gallery/templates          # List templates
GET /api/v1/gallery/templates/{id}     # Get template
POST /api/v1/gallery/templates/{id}/install  # Install template
GET /api/v1/gallery/categories         # Template categories
```

### Usage & Analytics

```
GET /api/v1/usage                      # Usage statistics
GET /api/v1/usage/runs                 # Run statistics
GET /api/v1/usage/cost                 # LLM cost tracking
GET /api/v1/analytics/overview         # Analytics overview
GET /api/v1/analytics/pipelines        # Pipeline analytics
```

## WebSocket

Connect for real-time updates:

```
ws://localhost:8999/api/v1/ws/runs
```

### Protocol

**Subscribe to run:**
```json
{
  "type": "subscribe",
  "run_id": "run-abc123"
}
```

**Control commands:**
```json
{ "type": "pause", "run_id": "run-abc123" }
{ "type": "resume", "run_id": "run-abc123" }
{ "type": "step", "run_id": "run-abc123" }
```

### Events

| Event | Description |
|-------|-------------|
| `connected` | WebSocket connected |
| `subscribed` | Subscribed to run |
| `run_started` | Pipeline execution started |
| `stage_started` | Stage began |
| `stage_completed` | Stage finished |
| `stage_failed` | Stage error |
| `execution_paused` | Hit breakpoint |
| `run_completed` | Pipeline finished |
| `run_failed` | Pipeline error |
| `token_chunk` | LLM token received |
| `stream_start` | LLM streaming began |
| `stream_end` | LLM streaming ended |

## Authentication

Studio supports multiple authentication methods for different use cases.

### API Keys

```bash
# Create API key
curl -X POST http://localhost:8999/api/v1/auth/api-keys \
  -H "Content-Type: application/json" \
  -d '{"name": "my-key", "scopes": ["pipelines:read", "runs:write"]}'

# Use API key
curl -H "X-API-Key: fm_xxx" http://localhost:8999/api/v1/pipelines
```

### JWT Tokens

```bash
# Login
curl -X POST http://localhost:8999/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
# Returns: {"access_token": "...", "refresh_token": "..."}

# Use access token
curl -H "Authorization: Bearer <access_token>" http://localhost:8999/api/v1/pipelines

# Refresh token
curl -X POST http://localhost:8999/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "..."}'
```

### OAuth 2.0

```bash
# Authorization Code Flow
GET /api/v1/oauth/authorize?client_id=...&redirect_uri=...&scope=...

# Token exchange
curl -X POST http://localhost:8999/api/v1/oauth/token \
  -d "grant_type=authorization_code&code=...&client_id=...&client_secret=..."
```

### Scopes

| Scope | Description |
|-------|-------------|
| `pipelines:read` | Read pipelines |
| `pipelines:write` | Create/update pipelines |
| `runs:read` | Read execution data |
| `runs:write` | Execute pipelines |
| `registry:read` | Read components |
| `marketplace:read` | Browse marketplace |
| `marketplace:write` | Publish to marketplace |
| `admin` | Full access |

### Security Features

| Feature | Implementation |
|---------|---------------|
| Password Hashing | bcrypt with 12 rounds |
| Rate Limiting | Redis-backed sliding window (with in-memory fallback) |
| SAML Signatures | XML signature verification (signxml) |
| JWT Rotation | Access (1h) + Refresh (30d) with revocation |

## Database

### SQLite (Default)

```
.flowmason/flowmason.db
```

### PostgreSQL (Production)

Set environment variable:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/flowmason
```

### Schema

Key tables:
- `pipelines` - Pipeline definitions (includes output_config)
- `runs` - Execution records
- `stages` - Stage execution details
- `organizations` - Multi-tenancy
- `users` - User accounts
- `api_keys` - API authentication
- `audit_log` - Security audit trail
- `output_allowlist` - Allowed output destinations per org
- `stored_connections` - Encrypted DB/MQ credentials
- `output_deliveries` - Output delivery logs
- `schedules` - Cron schedules
- `webhooks` - Webhook triggers
- `oauth_clients` - OAuth 2.0 clients
- `oauth_tokens` - OAuth tokens
- `refresh_tokens` - JWT refresh tokens
- `password_reset_tokens` - Password reset tokens
- `prompts` - Prompt library
- `prompt_versions` - Prompt version history
- `time_travel_snapshots` - Execution snapshots
- `marketplace_listings` - Marketplace listings
- `marketplace_publishers` - Publisher profiles
- `marketplace_reviews` - Reviews and ratings
- `marketplace_favorites` - User favorites

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWMASON_HOST` | `127.0.0.1` | Server host |
| `FLOWMASON_PORT` | `8999` | Server port |
| `DATABASE_URL` | SQLite | Database connection |
| `LOG_LEVEL` | `info` | Logging level |

### CORS

CORS is enabled by default for development. Configure in production:

```python
app = create_app(
    enable_cors=True,
    cors_origins=["https://app.example.com"]
)
```

## Examples

### Run a Pipeline

```python
import httpx

async def run_pipeline():
    async with httpx.AsyncClient() as client:
        # Create run
        response = await client.post(
            "http://localhost:8999/api/v1/runs",
            json={
                "pipeline_id": "my-pipeline",
                "input": {"url": "https://example.com"}
            }
        )
        run = response.json()
        run_id = run["run_id"]

        # Poll for completion
        while True:
            status = await client.get(
                f"http://localhost:8999/api/v1/runs/{run_id}/status"
            )
            if status.json()["status"] in ["completed", "failed"]:
                break
            await asyncio.sleep(0.5)

        # Get result
        result = await client.get(
            f"http://localhost:8999/api/v1/runs/{run_id}"
        )
        return result.json()
```

### WebSocket Client

```javascript
const ws = new WebSocket("ws://localhost:8999/api/v1/ws/runs");

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: "subscribe",
    run_id: "run-abc123"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Event: ${data.type}`, data);

  if (data.type === "stage_completed") {
    console.log(`Stage ${data.stage_id} completed`);
  }
};
```

## See Also

- [API Reference](api/rest-api.md) - Full API documentation
- [WebSocket Protocol](api/websocket.md) - Real-time communication
- [Authentication](../04-core-framework/auth.md) - Security details
- [OAuth 2.0](oauth.md) - OAuth configuration
- [JWT Tokens](jwt-tokens.md) - JWT session management
- [Scheduling](scheduling.md) - Cron schedules
- [Webhooks](webhooks.md) - Webhook triggers
- [Marketplace](marketplace.md) - Pipeline marketplace
- [Time Travel Debugging](debugging.md#time-travel) - Execution snapshots
- [Docker Deployment](docker.md) - Container deployment
