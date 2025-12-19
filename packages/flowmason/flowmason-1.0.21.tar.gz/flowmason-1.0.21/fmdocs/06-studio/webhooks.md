# Webhook Triggers

FlowMason allows external systems to trigger pipeline executions via HTTP webhooks.

## Overview

Webhooks provide a way to:
- Trigger pipelines from external services (GitHub, Slack, Stripe, etc.)
- Build event-driven automation workflows
- Integrate FlowMason with CI/CD pipelines
- Create public APIs backed by FlowMason pipelines

## Creating a Webhook

### Via API

```http
POST /api/v1/webhooks
Authorization: Bearer <api-key>
Content-Type: application/json

{
  "name": "GitHub Push Handler",
  "pipeline_id": "my-pipeline-id",
  "input_mapping": {
    "repository.full_name": "repo",
    "commits": "commits",
    "pusher.name": "author"
  },
  "default_inputs": {
    "environment": "production"
  },
  "require_auth": true,
  "auth_header": "X-Hub-Signature-256",
  "auth_secret": "my-webhook-secret",
  "async_mode": true,
  "description": "Handles GitHub push events"
}
```

Response:
```json
{
  "id": "wh-abc123",
  "name": "GitHub Push Handler",
  "pipeline_id": "my-pipeline-id",
  "webhook_url": "https://studio.example.com/api/v1/webhook/aBcDeFgHiJkLmNoPqRsTuVwXyZ",
  "enabled": true,
  "require_auth": true,
  "auth_header": "X-Hub-Signature-256",
  "async_mode": true,
  "trigger_count": 0
}
```

## Triggering a Webhook

Once created, the webhook can be called from any HTTP client:

```bash
curl -X POST https://studio.example.com/api/v1/webhook/aBcDeFgHiJkLmNoPqRsTuVwXyZ \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: my-webhook-secret" \
  -d '{"repository": {"full_name": "user/repo"}, "commits": [...]}'
```

### Async Mode (Default)

Returns immediately with a run ID:

```json
{
  "status": "accepted",
  "message": "Pipeline execution started",
  "run_id": "run-xyz789"
}
```

### Sync Mode

When `async_mode: false`, waits for pipeline completion:

```json
{
  "status": "completed",
  "message": "Pipeline execution completed",
  "run_id": "run-xyz789",
  "result": { ... }
}
```

## Input Mapping

Map fields from the webhook payload to pipeline inputs using dot notation:

| Webhook Payload | Input Mapping | Pipeline Input |
|-----------------|---------------|----------------|
| `{"user": {"id": 123}}` | `"user.id": "userId"` | `{"userId": 123}` |
| `{"items": [1, 2, 3]}` | `"items": "data"` | `{"data": [1, 2, 3]}` |
| `{"event": "push"}` | `"event": "action"` | `{"action": "push"}` |

### Default Inputs

Provide fallback values for pipeline inputs:

```json
{
  "default_inputs": {
    "environment": "production",
    "notify": true,
    "retries": 3
  }
}
```

### No Mapping (Pass-Through)

If `input_mapping` is empty, the entire webhook payload is passed as pipeline input.

## Authentication

### Secret Header

```json
{
  "require_auth": true,
  "auth_header": "X-Webhook-Secret",
  "auth_secret": "my-secret-value"
}
```

Requests must include:
```http
X-Webhook-Secret: my-secret-value
```

### Common Integrations

| Service | Auth Header | Documentation |
|---------|-------------|---------------|
| GitHub | `X-Hub-Signature-256` | [GitHub Webhooks](https://docs.github.com/webhooks) |
| Stripe | `Stripe-Signature` | [Stripe Webhooks](https://stripe.com/docs/webhooks) |
| Slack | `X-Slack-Signature` | [Slack Events](https://api.slack.com/events) |

### No Authentication

For testing or internal use:
```json
{
  "require_auth": false
}
```

## Management Endpoints

### List Webhooks

```http
GET /api/v1/webhooks
```

### Get Webhook

```http
GET /api/v1/webhooks/{webhook_id}
```

### Update Webhook

```http
PUT /api/v1/webhooks/{webhook_id}
```

### Delete Webhook

```http
DELETE /api/v1/webhooks/{webhook_id}
```

### Regenerate Token

Invalidates the old webhook URL:

```http
POST /api/v1/webhooks/{webhook_id}/regenerate-token
```

### Get Invocation History

```http
GET /api/v1/webhooks/{webhook_id}/invocations
```

## Invocation Logging

All webhook calls are logged:

```json
{
  "id": "inv-123",
  "webhook_id": "wh-abc123",
  "run_id": "run-xyz789",
  "status": "success",
  "invoked_at": "2025-01-15T10:30:00Z"
}
```

Status values:
- `success`: Webhook processed, pipeline started
- `rejected`: Authentication failed or webhook disabled
- `error`: Processing error (invalid payload, pipeline not found)

## Example: GitHub CI Integration

1. Create webhook:
```json
{
  "name": "Deploy on Push to Main",
  "pipeline_id": "deploy-pipeline",
  "input_mapping": {
    "ref": "branch",
    "repository.full_name": "repo",
    "head_commit.message": "commit_message"
  },
  "auth_header": "X-Hub-Signature-256",
  "auth_secret": "github-webhook-secret"
}
```

2. Configure in GitHub:
   - Payload URL: Copy webhook_url from response
   - Content type: `application/json`
   - Secret: `github-webhook-secret`
   - Events: Push events

3. Pipeline receives:
```json
{
  "branch": "refs/heads/main",
  "repo": "user/my-app",
  "commit_message": "Fix bug in login"
}
```

## Example: Stripe Payment Handler

```json
{
  "name": "Process Stripe Payment",
  "pipeline_id": "payment-processor",
  "input_mapping": {
    "type": "event_type",
    "data.object.id": "payment_id",
    "data.object.amount": "amount",
    "data.object.customer": "customer_id"
  },
  "async_mode": false
}
```

## Security Best Practices

1. **Always use authentication** in production
2. **Validate webhook signatures** for external services
3. **Use HTTPS** for webhook URLs
4. **Regenerate tokens** if compromised
5. **Monitor invocation logs** for suspicious activity
6. **Set appropriate timeouts** for sync mode

## Troubleshooting

### Webhook Not Triggering

1. Check if webhook is enabled
2. Verify the token in the URL
3. Check authentication header/value
4. Review invocation logs for errors

### Invalid Payload Error

1. Ensure Content-Type is `application/json`
2. Validate JSON syntax
3. Check input_mapping paths exist in payload

### Authentication Failed

1. Verify auth_header name matches request
2. Confirm auth_secret matches configured value
3. Check for extra whitespace in header value
