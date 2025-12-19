# CI/CD Pipelines

This guide covers how to build Continuous Integration and Continuous Deployment workflows with Flowmason.

## CI/CD Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FLOWMASON CI/CD ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   SOURCE CONTROL          FLOWMASON              DEPLOYMENT         │
│   ──────────────          ─────────              ──────────         │
│                                                                     │
│   ┌─────────┐        ┌─────────────────┐        ┌─────────┐        │
│   │ GitHub  │──────▶ │ CI/CD Pipeline  │──────▶ │ Staging │        │
│   │ GitLab  │ webhook│                 │ deploy │         │        │
│   │ Bitbucket│       │  Build → Test   │        └────┬────┘        │
│   └─────────┘        │    ↓      ↓     │             │             │
│                      │  Deploy → Verify│             ▼             │
│                      └─────────────────┘        ┌─────────┐        │
│                              │                  │  Prod   │        │
│                              │ notify           │         │        │
│                              ▼                  └─────────┘        │
│                      ┌─────────────────┐                           │
│                      │  Slack/Teams    │                           │
│                      └─────────────────┘                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Pipeline Patterns

### Basic CI Pipeline

Trigger builds and report results:

```json
{
  "id": "basic-ci",
  "name": "Basic CI Pipeline",
  "stages": [
    {
      "id": "log-trigger",
      "component_type": "logger",
      "config": {
        "message": "CI triggered for {{input.repo}} on branch {{input.branch}}",
        "level": "info"
      }
    },
    {
      "id": "trigger-build",
      "component_type": "http-request",
      "config": {
        "url": "{{input.ci_url}}/build",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{env.CI_TOKEN}}"
        },
        "body": {
          "repo": "{{input.repo}}",
          "branch": "{{input.branch}}",
          "commit": "{{input.commit_sha}}"
        }
      },
      "depends_on": ["log-trigger"]
    },
    {
      "id": "get-build-id",
      "component_type": "json-transform",
      "config": {
        "data": "{{upstream.trigger-build.body}}",
        "template": {
          "build_id": "{{data.id}}",
          "status_url": "{{data.status_url}}"
        }
      },
      "depends_on": ["trigger-build"]
    },
    {
      "id": "wait-for-build",
      "component_type": "http-request",
      "config": {
        "url": "{{upstream.get-build-id.status_url}}",
        "method": "GET",
        "headers": {
          "Authorization": "Bearer {{env.CI_TOKEN}}"
        }
      },
      "depends_on": ["get-build-id"],
      "error_handling": {
        "on_error": "retry",
        "max_retries": 30,
        "retry_delay": 10000
      }
    },
    {
      "id": "report-status",
      "component_type": "http-request",
      "config": {
        "url": "{{input.callback_url}}",
        "method": "POST",
        "body": {
          "status": "{{upstream.wait-for-build.body.status}}",
          "build_id": "{{upstream.get-build-id.build_id}}",
          "logs_url": "{{upstream.wait-for-build.body.logs_url}}"
        }
      },
      "depends_on": ["wait-for-build"]
    }
  ]
}
```

### CD Pipeline with Staging and Production

```json
{
  "id": "staged-deployment",
  "name": "Staged Deployment Pipeline",
  "stages": [
    {
      "id": "validate-request",
      "component_type": "schema-validate",
      "config": {
        "data": "{{input}}",
        "schema": {
          "type": "object",
          "required": ["version", "artifact_url"],
          "properties": {
            "version": {"type": "string"},
            "artifact_url": {"type": "string", "format": "uri"}
          }
        }
      }
    },
    {
      "id": "deploy-staging",
      "component_type": "http-request",
      "config": {
        "url": "{{env.DEPLOY_API}}/staging/deploy",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{env.DEPLOY_TOKEN}}"
        },
        "body": {
          "version": "{{input.version}}",
          "artifact_url": "{{input.artifact_url}}"
        }
      },
      "depends_on": ["validate-request"]
    },
    {
      "id": "run-integration-tests",
      "component_type": "http-request",
      "config": {
        "url": "{{env.TEST_API}}/integration",
        "method": "POST",
        "body": {
          "target": "{{env.STAGING_URL}}",
          "suite": "smoke"
        },
        "timeout": 300000
      },
      "depends_on": ["deploy-staging"]
    },
    {
      "id": "check-test-results",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.run-integration-tests.body}}",
        "condition": "data.get('passed') == True and data.get('failures', 0) == 0"
      },
      "depends_on": ["run-integration-tests"]
    },
    {
      "id": "deploy-production",
      "component_type": "http-request",
      "config": {
        "url": "{{env.DEPLOY_API}}/production/deploy",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{env.DEPLOY_TOKEN}}"
        },
        "body": {
          "version": "{{input.version}}",
          "artifact_url": "{{input.artifact_url}}"
        }
      },
      "depends_on": ["check-test-results"]
    },
    {
      "id": "verify-production",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PROD_URL}}/health",
        "method": "GET",
        "timeout": 30000
      },
      "depends_on": ["deploy-production"],
      "error_handling": {
        "on_error": "retry",
        "max_retries": 5,
        "retry_delay": 5000
      }
    },
    {
      "id": "notify-success",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SLACK_WEBHOOK}}",
        "method": "POST",
        "body": {
          "text": "Deployment v{{input.version}} succeeded to production"
        }
      },
      "depends_on": ["verify-production"]
    }
  ]
}
```

### Blue-Green Deployment

```json
{
  "id": "blue-green-deploy",
  "name": "Blue-Green Deployment",
  "stages": [
    {
      "id": "get-current-env",
      "component_type": "http-request",
      "config": {
        "url": "{{env.LB_API}}/active",
        "method": "GET"
      }
    },
    {
      "id": "determine-target",
      "component_type": "json-transform",
      "config": {
        "data": "{{upstream.get-current-env.body}}",
        "template": {
          "current": "{{data.active}}",
          "target": "{{ 'green' if data.active == 'blue' else 'blue' }}"
        }
      },
      "depends_on": ["get-current-env"]
    },
    {
      "id": "deploy-to-inactive",
      "component_type": "http-request",
      "config": {
        "url": "{{env.DEPLOY_API}}/{{upstream.determine-target.target}}/deploy",
        "method": "POST",
        "body": {
          "version": "{{input.version}}"
        }
      },
      "depends_on": ["determine-target"]
    },
    {
      "id": "health-check-new",
      "component_type": "http-request",
      "config": {
        "url": "{{env.BASE_URL}}/{{upstream.determine-target.target}}/health",
        "method": "GET"
      },
      "depends_on": ["deploy-to-inactive"],
      "error_handling": {
        "on_error": "retry",
        "max_retries": 10,
        "retry_delay": 3000
      }
    },
    {
      "id": "switch-traffic",
      "component_type": "http-request",
      "config": {
        "url": "{{env.LB_API}}/switch",
        "method": "POST",
        "body": {
          "target": "{{upstream.determine-target.target}}"
        }
      },
      "depends_on": ["health-check-new"]
    },
    {
      "id": "verify-switch",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PROD_URL}}/version",
        "method": "GET"
      },
      "depends_on": ["switch-traffic"]
    },
    {
      "id": "validate-version",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.verify-switch.body}}",
        "condition": "data.get('version') == '{{input.version}}'"
      },
      "depends_on": ["verify-switch"]
    }
  ]
}
```

### Rollback Pipeline

```json
{
  "id": "rollback-deployment",
  "name": "Rollback Deployment",
  "stages": [
    {
      "id": "get-previous-version",
      "component_type": "http-request",
      "config": {
        "url": "{{env.DEPLOY_API}}/history?limit=2",
        "method": "GET"
      }
    },
    {
      "id": "extract-rollback-target",
      "component_type": "json-transform",
      "config": {
        "data": "{{upstream.get-previous-version.body}}",
        "template": {
          "rollback_version": "{{data.deployments[1].version}}",
          "rollback_artifact": "{{data.deployments[1].artifact_url}}"
        }
      },
      "depends_on": ["get-previous-version"]
    },
    {
      "id": "execute-rollback",
      "component_type": "http-request",
      "config": {
        "url": "{{env.DEPLOY_API}}/production/deploy",
        "method": "POST",
        "body": {
          "version": "{{upstream.extract-rollback-target.rollback_version}}",
          "artifact_url": "{{upstream.extract-rollback-target.rollback_artifact}}",
          "is_rollback": true
        }
      },
      "depends_on": ["extract-rollback-target"]
    },
    {
      "id": "verify-rollback",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PROD_URL}}/health",
        "method": "GET"
      },
      "depends_on": ["execute-rollback"],
      "error_handling": {
        "on_error": "retry",
        "max_retries": 5,
        "retry_delay": 5000
      }
    },
    {
      "id": "notify-rollback",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SLACK_WEBHOOK}}",
        "method": "POST",
        "body": {
          "text": "ROLLBACK: Reverted to v{{upstream.extract-rollback-target.rollback_version}}"
        }
      },
      "depends_on": ["verify-rollback"]
    }
  ]
}
```

## GitHub Actions Integration

### Trigger Workflow

```json
{
  "id": "trigger-github-workflow",
  "component_type": "http-request",
  "config": {
    "url": "https://api.github.com/repos/{{input.owner}}/{{input.repo}}/actions/workflows/{{input.workflow_file}}/dispatches",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{env.GITHUB_TOKEN}}",
      "Accept": "application/vnd.github.v3+json",
      "X-GitHub-Api-Version": "2022-11-28"
    },
    "body": {
      "ref": "{{input.branch}}",
      "inputs": {
        "environment": "{{input.environment}}",
        "version": "{{input.version}}"
      }
    }
  }
}
```

### Get Workflow Run Status

```json
{
  "id": "get-workflow-runs",
  "component_type": "http-request",
  "config": {
    "url": "https://api.github.com/repos/{{input.owner}}/{{input.repo}}/actions/runs",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer {{env.GITHUB_TOKEN}}",
      "Accept": "application/vnd.github.v3+json"
    },
    "query_params": {
      "branch": "{{input.branch}}",
      "per_page": "1"
    }
  }
}
```

### Update Commit Status

```json
{
  "id": "update-commit-status",
  "component_type": "http-request",
  "config": {
    "url": "https://api.github.com/repos/{{input.owner}}/{{input.repo}}/statuses/{{input.commit_sha}}",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{env.GITHUB_TOKEN}}",
      "Accept": "application/vnd.github.v3+json"
    },
    "body": {
      "state": "{{input.state}}",
      "target_url": "{{input.details_url}}",
      "description": "{{input.description}}",
      "context": "flowmason/deploy"
    }
  }
}
```

## Jenkins Integration

### Trigger Build

```json
{
  "id": "trigger-jenkins-build",
  "component_type": "http-request",
  "config": {
    "url": "{{env.JENKINS_URL}}/job/{{input.job_name}}/buildWithParameters",
    "method": "POST",
    "headers": {
      "Authorization": "Basic {{env.JENKINS_AUTH}}"
    },
    "query_params": {
      "BRANCH": "{{input.branch}}",
      "VERSION": "{{input.version}}"
    }
  }
}
```

### Get Build Status

```json
{
  "id": "get-jenkins-status",
  "component_type": "http-request",
  "config": {
    "url": "{{env.JENKINS_URL}}/job/{{input.job_name}}/{{input.build_number}}/api/json",
    "method": "GET",
    "headers": {
      "Authorization": "Basic {{env.JENKINS_AUTH}}"
    }
  }
}
```

## Notifications

### Slack Notification

```json
{
  "id": "slack-notify",
  "component_type": "http-request",
  "config": {
    "url": "{{env.SLACK_WEBHOOK}}",
    "method": "POST",
    "body": {
      "blocks": [
        {
          "type": "header",
          "text": {
            "type": "plain_text",
            "text": "Deployment {{input.status}}"
          }
        },
        {
          "type": "section",
          "fields": [
            {"type": "mrkdwn", "text": "*Version:*\n{{input.version}}"},
            {"type": "mrkdwn", "text": "*Environment:*\n{{input.environment}}"},
            {"type": "mrkdwn", "text": "*Deployed by:*\n{{input.deployer}}"},
            {"type": "mrkdwn", "text": "*Time:*\n{{now()}}"}
          ]
        }
      ]
    }
  }
}
```

### PagerDuty Alert

```json
{
  "id": "pagerduty-alert",
  "component_type": "http-request",
  "config": {
    "url": "https://events.pagerduty.com/v2/enqueue",
    "method": "POST",
    "body": {
      "routing_key": "{{env.PAGERDUTY_KEY}}",
      "event_action": "trigger",
      "payload": {
        "summary": "Deployment failed: {{input.version}}",
        "severity": "critical",
        "source": "flowmason",
        "custom_details": {
          "version": "{{input.version}}",
          "environment": "{{input.environment}}",
          "error": "{{input.error_message}}"
        }
      }
    }
  }
}
```

## Best Practices

### 1. Use Approval Gates

For production deployments, require approval:

```json
{
  "id": "check-approval",
  "component_type": "http-request",
  "config": {
    "url": "{{env.APPROVAL_API}}/check/{{input.deployment_id}}",
    "method": "GET"
  }
},
{
  "id": "validate-approval",
  "component_type": "filter",
  "config": {
    "data": "{{upstream.check-approval.body}}",
    "condition": "data.get('approved') == True"
  },
  "depends_on": ["check-approval"]
}
```

### 2. Implement Canary Deployments

Deploy to a subset first:

```json
{
  "id": "canary-deploy",
  "component_type": "http-request",
  "config": {
    "url": "{{env.DEPLOY_API}}/canary",
    "method": "POST",
    "body": {
      "version": "{{input.version}}",
      "percentage": 10
    }
  }
}
```

### 3. Monitor After Deploy

Always verify deployments:

```json
{
  "id": "post-deploy-check",
  "component_type": "http-request",
  "config": {
    "url": "{{env.MONITORING_API}}/check",
    "method": "POST",
    "body": {
      "checks": ["health", "latency", "error_rate"],
      "threshold_minutes": 5
    }
  },
  "depends_on": ["deploy"],
  "timeout": 600
}
```

## Related Documentation

- [Monitoring & Alerting](./monitoring-alerting.md)
- [Incident Response](./incident-response.md)
- [GitHub Actions Use Case](./use-cases/github-actions.md)
