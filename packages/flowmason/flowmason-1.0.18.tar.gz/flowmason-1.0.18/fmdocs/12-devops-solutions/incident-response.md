# Incident Response

This guide covers how to build automated incident response workflows with Flowmason, including detection, analysis, remediation, and notification.

## Incident Response Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                 FLOWMASON INCIDENT RESPONSE ARCHITECTURE            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   DETECTION              RESPONSE               COMMUNICATION       │
│   ─────────              ────────               ─────────────       │
│                                                                     │
│   ┌─────────┐        ┌─────────────────┐      ┌─────────┐          │
│   │ Alert   │───────▶│   FLOWMASON     │─────▶│  Slack  │          │
│   │ Source  │ webhook│                 │      └─────────┘          │
│   └─────────┘        │  ┌───────────┐  │      ┌─────────┐          │
│                      │  │  Analyze  │  │─────▶│PagerDuty│          │
│   ┌─────────┐        │  │   (AI)    │  │      └─────────┘          │
│   │ Monitor │───────▶│  └───────────┘  │      ┌─────────┐          │
│   │ Webhook │        │        │        │─────▶│ Status  │          │
│   └─────────┘        │        ▼        │      │  Page   │          │
│                      │  ┌───────────┐  │      └─────────┘          │
│   ┌─────────┐        │  │ Remediate │  │                           │
│   │ Manual  │───────▶│  │ or        │  │      ┌─────────┐          │
│   │ Trigger │        │  │ Escalate  │  │─────▶│  Jira   │          │
│   └─────────┘        │  └───────────┘  │      │ Ticket  │          │
│                      └─────────────────┘      └─────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Incident Response Patterns

### Basic Incident Handler

```json
{
  "id": "basic-incident-handler",
  "name": "Basic Incident Handler",
  "stages": [
    {
      "id": "parse-alert",
      "component_type": "json-transform",
      "config": {
        "data": "{{input}}",
        "template": {
          "alert_id": "{{data.alert_id or data.id}}",
          "severity": "{{data.severity or 'unknown'}}",
          "service": "{{data.service or data.labels.service}}",
          "message": "{{data.message or data.annotations.summary}}",
          "timestamp": "{{data.timestamp or now()}}"
        }
      }
    },
    {
      "id": "log-incident",
      "component_type": "logger",
      "config": {
        "message": "Incident received: {{upstream.parse-alert.alert_id}}",
        "level": "warning",
        "data": "{{upstream.parse-alert}}"
      },
      "depends_on": ["parse-alert"]
    },
    {
      "id": "create-ticket",
      "component_type": "http-request",
      "config": {
        "url": "{{env.JIRA_URL}}/rest/api/2/issue",
        "method": "POST",
        "headers": {
          "Authorization": "Basic {{env.JIRA_AUTH}}",
          "Content-Type": "application/json"
        },
        "body": {
          "fields": {
            "project": {"key": "{{env.JIRA_PROJECT}}"},
            "summary": "[{{upstream.parse-alert.severity}}] {{upstream.parse-alert.service}}: {{upstream.parse-alert.message}}",
            "description": "Auto-generated incident ticket\n\nAlert ID: {{upstream.parse-alert.alert_id}}\nService: {{upstream.parse-alert.service}}\nSeverity: {{upstream.parse-alert.severity}}\nTimestamp: {{upstream.parse-alert.timestamp}}",
            "issuetype": {"name": "Incident"},
            "priority": {"name": "{{upstream.parse-alert.severity}}"}
          }
        }
      },
      "depends_on": ["log-incident"]
    },
    {
      "id": "notify-team",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SLACK_WEBHOOK}}",
        "method": "POST",
        "body": {
          "text": "New Incident: {{upstream.parse-alert.message}}",
          "attachments": [
            {
              "color": "{{  'danger' if upstream.parse-alert.severity == 'critical' else 'warning' }}",
              "fields": [
                {"title": "Service", "value": "{{upstream.parse-alert.service}}", "short": true},
                {"title": "Severity", "value": "{{upstream.parse-alert.severity}}", "short": true},
                {"title": "Ticket", "value": "{{upstream.create-ticket.body.key}}", "short": true}
              ]
            }
          ]
        }
      },
      "depends_on": ["create-ticket"]
    }
  ]
}
```

### AI-Powered Root Cause Analysis

```json
{
  "id": "ai-root-cause-analysis",
  "name": "AI Root Cause Analysis",
  "stages": [
    {
      "id": "parse-incident",
      "component_type": "json-transform",
      "config": {
        "data": "{{input}}",
        "template": {
          "service": "{{data.service}}",
          "error": "{{data.error_message}}",
          "severity": "{{data.severity}}"
        }
      }
    },
    {
      "id": "fetch-logs",
      "component_type": "http-request",
      "config": {
        "url": "{{env.LOGS_API}}/search",
        "method": "POST",
        "body": {
          "query": "service:{{upstream.parse-incident.service}} level:error",
          "from": "now-1h",
          "to": "now",
          "limit": 100
        }
      },
      "depends_on": ["parse-incident"]
    },
    {
      "id": "fetch-metrics",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PROMETHEUS_URL}}/api/v1/query_range",
        "method": "GET",
        "query_params": {
          "query": "rate(http_requests_total{service=\"{{upstream.parse-incident.service}}\",status=~\"5..\"}[5m])",
          "start": "{{input.start_time}}",
          "end": "now",
          "step": "60s"
        }
      },
      "depends_on": ["parse-incident"]
    },
    {
      "id": "fetch-recent-changes",
      "component_type": "http-request",
      "config": {
        "url": "{{env.DEPLOY_API}}/history",
        "method": "GET",
        "query_params": {
          "service": "{{upstream.parse-incident.service}}",
          "limit": "5"
        }
      },
      "depends_on": ["parse-incident"]
    },
    {
      "id": "analyze-root-cause",
      "component_type": "generator",
      "config": {
        "prompt": "Analyze this incident and determine the root cause:\n\n## Incident Details\nService: {{upstream.parse-incident.service}}\nError: {{upstream.parse-incident.error}}\nSeverity: {{upstream.parse-incident.severity}}\n\n## Recent Logs\n{{upstream.fetch-logs.body}}\n\n## Error Rate Metrics\n{{upstream.fetch-metrics.body}}\n\n## Recent Deployments\n{{upstream.fetch-recent-changes.body}}\n\n---\n\nProvide:\n1. Most likely root cause\n2. Contributing factors\n3. Evidence supporting the analysis\n4. Recommended remediation steps\n5. Prevention recommendations",
        "system_prompt": "You are an expert SRE performing root cause analysis. Analyze all available data to identify the root cause of incidents. Be specific and cite evidence from logs, metrics, and deployment history."
      },
      "depends_on": ["fetch-logs", "fetch-metrics", "fetch-recent-changes"]
    },
    {
      "id": "format-analysis",
      "component_type": "json-transform",
      "config": {
        "template": {
          "incident_id": "{{input.incident_id}}",
          "service": "{{upstream.parse-incident.service}}",
          "analysis": "{{upstream.analyze-root-cause.content}}",
          "data_sources": {
            "logs_analyzed": "{{len(upstream.fetch-logs.body.hits) if upstream.fetch-logs.body.hits else 0}}",
            "metric_points": "{{len(upstream.fetch-metrics.body.data.result[0].values) if upstream.fetch-metrics.body.data.result else 0}}",
            "deployments_checked": "{{len(upstream.fetch-recent-changes.body) if upstream.fetch-recent-changes.body else 0}}"
          },
          "analyzed_at": "{{now()}}"
        }
      },
      "depends_on": ["analyze-root-cause"]
    }
  ]
}
```

### Auto-Remediation with Fallback

```json
{
  "id": "auto-remediation",
  "name": "Auto-Remediation Pipeline",
  "stages": [
    {
      "id": "parse-alert",
      "component_type": "json-transform",
      "config": {
        "data": "{{input}}",
        "template": {
          "service": "{{data.service}}",
          "issue_type": "{{data.labels.issue_type or 'unknown'}}",
          "instance": "{{data.labels.instance}}"
        }
      }
    },
    {
      "id": "determine-action",
      "component_type": "router",
      "config": {
        "value": "{{upstream.parse-alert.issue_type}}",
        "routes": {
          "high_memory": ["restart-service"],
          "high_cpu": ["scale-up"],
          "connection_error": ["restart-service"],
          "disk_full": ["cleanup-disk"],
          "certificate_expiry": ["renew-cert"]
        },
        "default_route": ["escalate-to-human"]
      },
      "depends_on": ["parse-alert"]
    },
    {
      "id": "restart-service",
      "component_type": "trycatch",
      "config": {
        "try_stages": ["execute-restart"],
        "catch_stages": ["escalate-to-human"],
        "finally_stages": ["log-remediation"]
      }
    },
    {
      "id": "execute-restart",
      "component_type": "http-request",
      "config": {
        "url": "{{env.K8S_API}}/apis/apps/v1/namespaces/{{input.namespace}}/deployments/{{upstream.parse-alert.service}}/scale",
        "method": "PATCH",
        "headers": {
          "Authorization": "Bearer {{env.K8S_TOKEN}}",
          "Content-Type": "application/strategic-merge-patch+json"
        },
        "body": {
          "spec": {"replicas": 0}
        }
      }
    },
    {
      "id": "wait-for-shutdown",
      "component_type": "http-request",
      "config": {
        "url": "{{env.K8S_API}}/apis/apps/v1/namespaces/{{input.namespace}}/deployments/{{upstream.parse-alert.service}}",
        "method": "GET",
        "headers": {
          "Authorization": "Bearer {{env.K8S_TOKEN}}"
        }
      },
      "depends_on": ["execute-restart"],
      "error_handling": {
        "on_error": "retry",
        "max_retries": 10,
        "retry_delay": 2000
      }
    },
    {
      "id": "scale-back-up",
      "component_type": "http-request",
      "config": {
        "url": "{{env.K8S_API}}/apis/apps/v1/namespaces/{{input.namespace}}/deployments/{{upstream.parse-alert.service}}/scale",
        "method": "PATCH",
        "headers": {
          "Authorization": "Bearer {{env.K8S_TOKEN}}",
          "Content-Type": "application/strategic-merge-patch+json"
        },
        "body": {
          "spec": {"replicas": "{{input.desired_replicas or 2}}"}
        }
      },
      "depends_on": ["wait-for-shutdown"]
    },
    {
      "id": "scale-up",
      "component_type": "http-request",
      "config": {
        "url": "{{env.K8S_API}}/apis/apps/v1/namespaces/{{input.namespace}}/deployments/{{upstream.parse-alert.service}}/scale",
        "method": "PATCH",
        "headers": {
          "Authorization": "Bearer {{env.K8S_TOKEN}}",
          "Content-Type": "application/strategic-merge-patch+json"
        },
        "body": {
          "spec": {"replicas": "{{input.scale_to or 4}}"}
        }
      }
    },
    {
      "id": "escalate-to-human",
      "component_type": "http-request",
      "config": {
        "url": "https://events.pagerduty.com/v2/enqueue",
        "method": "POST",
        "body": {
          "routing_key": "{{env.PAGERDUTY_KEY}}",
          "event_action": "trigger",
          "payload": {
            "summary": "Auto-remediation failed for {{upstream.parse-alert.service}}",
            "severity": "critical",
            "source": "flowmason-remediation",
            "custom_details": {
              "service": "{{upstream.parse-alert.service}}",
              "issue_type": "{{upstream.parse-alert.issue_type}}",
              "attempted_action": "auto-remediation"
            }
          }
        }
      }
    },
    {
      "id": "log-remediation",
      "component_type": "logger",
      "config": {
        "message": "Remediation completed for {{upstream.parse-alert.service}}",
        "level": "info",
        "data": {
          "service": "{{upstream.parse-alert.service}}",
          "issue_type": "{{upstream.parse-alert.issue_type}}",
          "timestamp": "{{now()}}"
        }
      }
    },
    {
      "id": "verify-remediation",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SERVICE_URL}}/{{upstream.parse-alert.service}}/health",
        "method": "GET",
        "timeout": 30000
      },
      "depends_on": ["scale-back-up"],
      "error_handling": {
        "on_error": "retry",
        "max_retries": 5,
        "retry_delay": 5000
      }
    },
    {
      "id": "notify-resolution",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SLACK_WEBHOOK}}",
        "method": "POST",
        "body": {
          "text": "Auto-remediation successful",
          "attachments": [
            {
              "color": "good",
              "fields": [
                {"title": "Service", "value": "{{upstream.parse-alert.service}}", "short": true},
                {"title": "Issue", "value": "{{upstream.parse-alert.issue_type}}", "short": true},
                {"title": "Action", "value": "Service restarted", "short": true},
                {"title": "Status", "value": "Healthy", "short": true}
              ]
            }
          ]
        }
      },
      "depends_on": ["verify-remediation"]
    }
  ]
}
```

### Status Page Update

```json
{
  "id": "update-status-page",
  "name": "Status Page Update",
  "stages": [
    {
      "id": "create-incident",
      "component_type": "http-request",
      "config": {
        "url": "{{env.STATUSPAGE_API}}/pages/{{env.STATUSPAGE_ID}}/incidents",
        "method": "POST",
        "headers": {
          "Authorization": "OAuth {{env.STATUSPAGE_TOKEN}}"
        },
        "body": {
          "incident": {
            "name": "{{input.title}}",
            "status": "investigating",
            "impact_override": "{{input.impact}}",
            "body": "{{input.description}}",
            "component_ids": "{{input.component_ids}}",
            "components": {
              "{{input.component_id}}": "{{input.component_status}}"
            }
          }
        }
      }
    },
    {
      "id": "store-incident-id",
      "component_type": "variable-set",
      "config": {
        "variables": {
          "statuspage_incident_id": "{{upstream.create-incident.body.id}}"
        }
      },
      "depends_on": ["create-incident"]
    }
  ]
}
```

### Incident Resolution

```json
{
  "id": "resolve-incident",
  "name": "Resolve Incident",
  "stages": [
    {
      "id": "update-statuspage",
      "component_type": "http-request",
      "config": {
        "url": "{{env.STATUSPAGE_API}}/pages/{{env.STATUSPAGE_ID}}/incidents/{{input.incident_id}}",
        "method": "PATCH",
        "headers": {
          "Authorization": "OAuth {{env.STATUSPAGE_TOKEN}}"
        },
        "body": {
          "incident": {
            "status": "resolved",
            "body": "{{input.resolution_message}}"
          }
        }
      }
    },
    {
      "id": "resolve-pagerduty",
      "component_type": "http-request",
      "config": {
        "url": "https://events.pagerduty.com/v2/enqueue",
        "method": "POST",
        "body": {
          "routing_key": "{{env.PAGERDUTY_KEY}}",
          "event_action": "resolve",
          "dedup_key": "{{input.dedup_key}}"
        }
      },
      "depends_on": ["update-statuspage"]
    },
    {
      "id": "close-jira-ticket",
      "component_type": "http-request",
      "config": {
        "url": "{{env.JIRA_URL}}/rest/api/2/issue/{{input.jira_ticket}}/transitions",
        "method": "POST",
        "headers": {
          "Authorization": "Basic {{env.JIRA_AUTH}}"
        },
        "body": {
          "transition": {"id": "{{env.JIRA_RESOLVE_TRANSITION}}"},
          "fields": {
            "resolution": {"name": "Done"}
          }
        }
      },
      "depends_on": ["resolve-pagerduty"]
    },
    {
      "id": "notify-resolution",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SLACK_WEBHOOK}}",
        "method": "POST",
        "body": {
          "text": "Incident Resolved: {{input.incident_title}}",
          "attachments": [
            {
              "color": "good",
              "fields": [
                {"title": "Resolution", "value": "{{input.resolution_message}}", "short": false},
                {"title": "Duration", "value": "{{input.duration}}", "short": true},
                {"title": "Root Cause", "value": "{{input.root_cause}}", "short": true}
              ]
            }
          ]
        }
      },
      "depends_on": ["close-jira-ticket"]
    },
    {
      "id": "generate-postmortem",
      "component_type": "generator",
      "config": {
        "prompt": "Generate a postmortem document for this incident:\n\nTitle: {{input.incident_title}}\nDuration: {{input.duration}}\nServices Affected: {{input.services}}\nRoot Cause: {{input.root_cause}}\nResolution: {{input.resolution_message}}\nTimeline: {{input.timeline}}\n\nCreate a postmortem following the blameless postmortem format with:\n1. Executive Summary\n2. Impact Assessment\n3. Timeline of Events\n4. Root Cause Analysis\n5. Resolution Steps\n6. Action Items to Prevent Recurrence\n7. Lessons Learned",
        "system_prompt": "You are an SRE writing blameless postmortems. Focus on systemic improvements, not individual blame."
      },
      "depends_on": ["notify-resolution"]
    }
  ]
}
```

## Runbook Automation

### Execute Runbook Steps

```json
{
  "id": "execute-runbook",
  "name": "Execute Runbook",
  "stages": [
    {
      "id": "fetch-runbook",
      "component_type": "http-request",
      "config": {
        "url": "{{env.RUNBOOK_API}}/runbooks/{{input.runbook_id}}",
        "method": "GET"
      }
    },
    {
      "id": "execute-steps",
      "component_type": "foreach",
      "config": {
        "items": "{{upstream.fetch-runbook.body.steps}}",
        "item_variable": "step",
        "loop_stages": ["execute-step", "verify-step"],
        "collect_results": true,
        "parallel": false
      },
      "depends_on": ["fetch-runbook"]
    },
    {
      "id": "execute-step",
      "component_type": "http-request",
      "config": {
        "url": "{{context.step.endpoint}}",
        "method": "{{context.step.method}}",
        "headers": "{{context.step.headers}}",
        "body": "{{context.step.body}}"
      }
    },
    {
      "id": "verify-step",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.execute-step}}",
        "condition": "{{context.step.success_condition}}"
      }
    },
    {
      "id": "summarize-execution",
      "component_type": "json-transform",
      "config": {
        "data": "{{upstream.execute-steps.results}}",
        "template": {
          "runbook_id": "{{input.runbook_id}}",
          "total_steps": "{{len(data)}}",
          "successful_steps": "{{len([s for s in data if s.get('passed')])}}",
          "failed_steps": "{{len([s for s in data if not s.get('passed')])}}",
          "executed_at": "{{now()}}"
        }
      },
      "depends_on": ["execute-steps"]
    }
  ]
}
```

## Best Practices

### 1. Deduplication

Use dedup keys to prevent alert storms:

```json
{
  "id": "deduplicated-alert",
  "component_type": "http-request",
  "config": {
    "url": "https://events.pagerduty.com/v2/enqueue",
    "method": "POST",
    "body": {
      "routing_key": "{{env.PAGERDUTY_KEY}}",
      "event_action": "trigger",
      "dedup_key": "{{input.service}}-{{input.alert_type}}"
    }
  }
}
```

### 2. Severity-Based Routing

Route based on severity:

```json
{
  "id": "severity-router",
  "component_type": "router",
  "config": {
    "value": "{{input.severity}}",
    "routes": {
      "critical": ["page-oncall", "update-status-page"],
      "high": ["notify-slack-urgent", "create-ticket"],
      "medium": ["notify-slack", "create-ticket"],
      "low": ["log-only"]
    }
  }
}
```

### 3. Time-Based Escalation

Escalate if not acknowledged:

```json
{
  "id": "check-acknowledgement",
  "component_type": "http-request",
  "config": {
    "url": "{{env.INCIDENT_API}}/{{input.incident_id}}/status",
    "method": "GET"
  }
},
{
  "id": "escalate-if-unacked",
  "component_type": "conditional",
  "config": {
    "condition": "{{upstream.check-acknowledgement.body.acknowledged}} == False",
    "true_stages": ["escalate-to-manager"],
    "false_stages": ["log-acknowledged"]
  },
  "depends_on": ["check-acknowledgement"]
}
```

## Related Documentation

- [Monitoring & Alerting](./monitoring-alerting.md)
- [CI/CD Pipelines](./ci-cd-pipelines.md)
- [API Integration](./api-integration.md)
