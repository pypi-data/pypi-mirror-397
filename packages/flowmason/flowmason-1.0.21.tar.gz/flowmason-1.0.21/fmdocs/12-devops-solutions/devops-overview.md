# DevOps Overview

Flowmason is a powerful platform for building DevOps automation workflows. This guide explains how Flowmason's architecture maps to DevOps use cases and best practices for implementation.

## Core Concepts for DevOps

### Pipeline as Workflow

In Flowmason, a **pipeline** represents your DevOps workflow as a directed acyclic graph (DAG) of stages:

```
┌──────────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE EXAMPLE                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│   │  Build  │───▶│  Test   │───▶│ Deploy  │───▶│ Verify  │      │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
│                                       │                          │
│                                       ▼                          │
│                                 ┌──────────┐                     │
│                                 │ Rollback │ (on failure)        │
│                                 └──────────┘                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Operators for DevOps

| Operator | DevOps Use Case |
|----------|-----------------|
| `http-request` | Call CI/CD APIs, cloud providers, monitoring tools |
| `json-transform` | Transform API responses, prepare payloads |
| `filter` | Gate deployments based on conditions |
| `schema-validate` | Validate configuration, API responses |
| `logger` | Audit logging, debugging |
| `variable-set` | Store state between stages |

### Control Flow for Complex Workflows

| Control Flow | DevOps Use Case |
|--------------|-----------------|
| `conditional` | Deploy to prod only if staging succeeds |
| `foreach` | Check multiple services in parallel |
| `trycatch` | Auto-remediate with fallback to manual escalation |
| `router` | Route by environment (dev/staging/prod) |

### AI Nodes for Intelligence

| Node | DevOps Use Case |
|------|-----------------|
| `generator` | Analyze logs, generate reports, suggest fixes |
| `critic` | Evaluate deployment readiness |
| `synthesizer` | Aggregate multi-source data into insights |

## Integration Patterns

### 1. API-First Integration

Most DevOps tools expose REST APIs. Use `http-request` to integrate:

```json
{
  "id": "trigger-github-workflow",
  "component_type": "http-request",
  "config": {
    "url": "https://api.github.com/repos/{{input.owner}}/{{input.repo}}/actions/workflows/{{input.workflow_id}}/dispatches",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{input.github_token}}",
      "Accept": "application/vnd.github.v3+json"
    },
    "body": {
      "ref": "{{input.branch}}",
      "inputs": {
        "environment": "{{input.environment}}"
      }
    }
  }
}
```

### 2. Webhook Receivers

Expose pipelines as HTTP endpoints to receive webhooks:

```bash
# Deploy pipeline and expose as API
fm deploy --target production

# Pipeline is now accessible at:
# POST /api/v1/pipelines/{pipeline_id}/run
```

### 3. Polling for Status

Use retry logic for polling long-running operations:

```json
{
  "id": "poll-deployment",
  "component_type": "http-request",
  "config": {
    "url": "{{input.deployment_url}}/status",
    "method": "GET"
  },
  "error_handling": {
    "on_error": "retry",
    "max_retries": 10,
    "retry_delay": 5000
  }
}
```

### 4. Secret Management

Use environment variables for sensitive data:

```json
{
  "config": {
    "headers": {
      "Authorization": "Bearer {{env.GITHUB_TOKEN}}"
    }
  }
}
```

## Common DevOps Workflows

### Continuous Integration

```
Trigger → Build → Test → Report
```

**Stages:**
1. Receive webhook from source control
2. Trigger build via CI API
3. Poll for build completion
4. Parse test results
5. Post status back to PR

### Continuous Deployment

```
Approve → Deploy Staging → Test → Deploy Prod → Verify
```

**Stages:**
1. Validate deployment request
2. Deploy to staging environment
3. Run integration tests
4. Conditional: proceed or rollback
5. Deploy to production
6. Run smoke tests
7. Update status/notify team

### Infrastructure Provisioning

```
Validate → Plan → Apply → Configure → Verify
```

**Stages:**
1. Validate infrastructure config
2. Call Terraform/Pulumi API to plan
3. Review changes (conditional gate)
4. Apply infrastructure changes
5. Configure services
6. Run health checks

### Incident Response

```
Alert → Triage → Analyze → Remediate → Notify
```

**Stages:**
1. Parse incoming alert
2. Fetch relevant metrics/logs
3. AI analysis for root cause
4. Attempt auto-remediation
5. Escalate if remediation fails
6. Update status page
7. Notify stakeholders

## Best Practices

### 1. Idempotency

Design pipelines to be safely re-runnable:

```json
{
  "id": "check-exists",
  "component_type": "http-request",
  "config": {
    "url": "{{input.resource_url}}",
    "method": "GET"
  }
},
{
  "id": "create-if-missing",
  "component_type": "conditional",
  "config": {
    "condition": "{{upstream.check-exists.status_code}} == 404",
    "true_stages": ["create-resource"],
    "false_stages": ["skip-creation"]
  }
}
```

### 2. Timeout Management

Set appropriate timeouts for different operations:

```json
{
  "config": {
    "timeout": 30000
  },
  "timeout": 60
}
```

- Quick health checks: 5-10 seconds
- API calls: 30 seconds
- Build/deploy operations: 5-10 minutes

### 3. Error Handling Strategy

Use `trycatch` for recoverable errors:

```json
{
  "id": "deploy-with-fallback",
  "component_type": "trycatch",
  "config": {
    "try_stages": ["deploy-primary"],
    "catch_stages": ["deploy-fallback", "notify-team"],
    "finally_stages": ["log-result"]
  }
}
```

### 4. Observability

Add logging at key decision points:

```json
{
  "id": "log-deployment-start",
  "component_type": "logger",
  "config": {
    "message": "Starting deployment to {{input.environment}}",
    "level": "info",
    "data": {
      "version": "{{input.version}}",
      "deployer": "{{input.deployer}}",
      "timestamp": "{{now()}}"
    }
  }
}
```

### 5. Validation Gates

Validate inputs and intermediate results:

```json
{
  "id": "validate-config",
  "component_type": "schema-validate",
  "config": {
    "data": "{{input}}",
    "schema": {
      "type": "object",
      "required": ["environment", "version", "approver"],
      "properties": {
        "environment": {
          "type": "string",
          "enum": ["staging", "production"]
        },
        "version": {
          "type": "string",
          "pattern": "^v[0-9]+\\.[0-9]+\\.[0-9]+$"
        }
      }
    }
  }
}
```

## Security Considerations

### Authentication

- Store API tokens in environment variables
- Use short-lived tokens where possible
- Implement token rotation

### Authorization

- Validate deployer permissions before proceeding
- Require approval for production deployments
- Log all actions with actor identity

### Network Security

- Use HTTPS for all API calls
- Validate SSL certificates
- Restrict outbound network access

## Next Steps

- [CI/CD Pipelines](./ci-cd-pipelines.md) - Detailed CI/CD patterns
- [Monitoring & Alerting](./monitoring-alerting.md) - Health check workflows
- [Incident Response](./incident-response.md) - Auto-remediation
- [API Integration](./api-integration.md) - REST API patterns
