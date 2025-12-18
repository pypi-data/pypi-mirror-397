# Monitoring & Alerting

This guide covers how to build health monitoring, metrics collection, and alerting workflows with Flowmason.

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   FLOWMASON MONITORING ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   SERVICES              FLOWMASON              ALERTING             │
│   ────────              ─────────              ────────             │
│                                                                     │
│   ┌─────────┐        ┌─────────────────┐     ┌─────────┐           │
│   │ API 1   │───────▶│                 │────▶│  Slack  │           │
│   └─────────┘ health │  Health Check   │     └─────────┘           │
│   ┌─────────┐  check │    Pipeline     │     ┌─────────┐           │
│   │ API 2   │───────▶│                 │────▶│PagerDuty│           │
│   └─────────┘        │  ┌───────────┐  │     └─────────┘           │
│   ┌─────────┐        │  │ AI Analyze│  │     ┌─────────┐           │
│   │ API 3   │───────▶│  └───────────┘  │────▶│  Email  │           │
│   └─────────┘        └─────────────────┘     └─────────┘           │
│                              │                                      │
│                              ▼                                      │
│                      ┌─────────────────┐                           │
│                      │   Dashboard     │                           │
│                      │   (Metrics DB)  │                           │
│                      └─────────────────┘                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Health Check Patterns

### Simple Health Check

```json
{
  "id": "simple-health-check",
  "name": "Simple Health Check",
  "stages": [
    {
      "id": "check-endpoint",
      "component_type": "http-request",
      "config": {
        "url": "{{input.service_url}}/health",
        "method": "GET",
        "timeout": 10000
      }
    },
    {
      "id": "evaluate-health",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.check-endpoint}}",
        "condition": "data.get('status_code') == 200"
      },
      "depends_on": ["check-endpoint"]
    },
    {
      "id": "format-result",
      "component_type": "json-transform",
      "config": {
        "template": {
          "service": "{{input.service_name}}",
          "healthy": "{{upstream.evaluate-health.passed}}",
          "response_time_ms": "{{upstream.check-endpoint.elapsed_ms}}",
          "checked_at": "{{now()}}"
        }
      },
      "depends_on": ["evaluate-health"]
    }
  ]
}
```

### Multi-Service Health Monitor

```json
{
  "id": "multi-service-monitor",
  "name": "Multi-Service Health Monitor",
  "stages": [
    {
      "id": "define-services",
      "component_type": "variable-set",
      "config": {
        "variables": {
          "services": [
            {"name": "api", "url": "{{env.API_URL}}/health"},
            {"name": "auth", "url": "{{env.AUTH_URL}}/health"},
            {"name": "database", "url": "{{env.DB_URL}}/health"},
            {"name": "cache", "url": "{{env.CACHE_URL}}/health"}
          ]
        }
      }
    },
    {
      "id": "check-all-services",
      "component_type": "foreach",
      "config": {
        "items": "{{upstream.define-services.services}}",
        "item_variable": "service",
        "loop_stages": ["health-check"],
        "collect_results": true,
        "parallel": true,
        "max_parallel": 4
      },
      "depends_on": ["define-services"]
    },
    {
      "id": "health-check",
      "component_type": "http-request",
      "config": {
        "url": "{{context.service.url}}",
        "method": "GET",
        "timeout": 10000
      }
    },
    {
      "id": "aggregate-results",
      "component_type": "json-transform",
      "config": {
        "data": "{{upstream.check-all-services.results}}",
        "template": {
          "total_services": "{{len(data)}}",
          "healthy_count": "{{len([r for r in data if r.get('status_code') == 200])}}",
          "unhealthy_count": "{{len([r for r in data if r.get('status_code') != 200])}}",
          "results": "{{data}}",
          "all_healthy": "{{all(r.get('status_code') == 200 for r in data)}}"
        }
      },
      "depends_on": ["check-all-services"]
    },
    {
      "id": "check-if-alert-needed",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.aggregate-results}}",
        "condition": "data.get('unhealthy_count', 0) > 0"
      },
      "depends_on": ["aggregate-results"]
    },
    {
      "id": "send-alert",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SLACK_WEBHOOK}}",
        "method": "POST",
        "body": {
          "text": "Health Check Alert: {{upstream.aggregate-results.unhealthy_count}} services unhealthy",
          "attachments": [
            {
              "color": "danger",
              "fields": [
                {"title": "Healthy", "value": "{{upstream.aggregate-results.healthy_count}}", "short": true},
                {"title": "Unhealthy", "value": "{{upstream.aggregate-results.unhealthy_count}}", "short": true}
              ]
            }
          ]
        }
      },
      "depends_on": ["check-if-alert-needed"]
    }
  ]
}
```

### Deep Health Check with Dependencies

```json
{
  "id": "deep-health-check",
  "name": "Deep Health Check",
  "stages": [
    {
      "id": "check-api",
      "component_type": "http-request",
      "config": {
        "url": "{{input.api_url}}/health/deep",
        "method": "GET",
        "timeout": 30000
      }
    },
    {
      "id": "parse-dependencies",
      "component_type": "json-transform",
      "config": {
        "data": "{{upstream.check-api.body}}",
        "template": {
          "api_status": "{{data.status}}",
          "database": "{{data.dependencies.database}}",
          "cache": "{{data.dependencies.cache}}",
          "queue": "{{data.dependencies.queue}}",
          "external_apis": "{{data.dependencies.external}}"
        }
      },
      "depends_on": ["check-api"]
    },
    {
      "id": "analyze-health",
      "component_type": "generator",
      "config": {
        "prompt": "Analyze this health check response and identify any issues:\n\n{{upstream.parse-dependencies}}\n\nProvide:\n1. Overall health status (healthy/degraded/unhealthy)\n2. List any failing or slow dependencies\n3. Recommended actions if any issues found",
        "system_prompt": "You are an SRE analyzing service health. Be concise and actionable."
      },
      "depends_on": ["parse-dependencies"]
    },
    {
      "id": "format-report",
      "component_type": "json-transform",
      "config": {
        "template": {
          "timestamp": "{{now()}}",
          "service": "{{input.service_name}}",
          "raw_status": "{{upstream.parse-dependencies}}",
          "analysis": "{{upstream.analyze-health.content}}",
          "response_time_ms": "{{upstream.check-api.elapsed_ms}}"
        }
      },
      "depends_on": ["analyze-health"]
    }
  ]
}
```

## Metrics Collection

### Collect and Store Metrics

```json
{
  "id": "collect-metrics",
  "name": "Collect Service Metrics",
  "stages": [
    {
      "id": "fetch-prometheus-metrics",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PROMETHEUS_URL}}/api/v1/query",
        "method": "POST",
        "body": {
          "query": "{{input.query}}"
        }
      }
    },
    {
      "id": "transform-metrics",
      "component_type": "json-transform",
      "config": {
        "data": "{{upstream.fetch-prometheus-metrics.body}}",
        "template": {
          "metric_name": "{{input.metric_name}}",
          "values": "{{data.data.result}}",
          "collected_at": "{{now()}}"
        }
      },
      "depends_on": ["fetch-prometheus-metrics"]
    },
    {
      "id": "store-metrics",
      "component_type": "http-request",
      "config": {
        "url": "{{env.METRICS_DB_URL}}/write",
        "method": "POST",
        "body": "{{upstream.transform-metrics}}"
      },
      "depends_on": ["transform-metrics"]
    }
  ]
}
```

### Threshold-Based Alerting

```json
{
  "id": "threshold-alert",
  "name": "Threshold Alert",
  "stages": [
    {
      "id": "fetch-metric",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PROMETHEUS_URL}}/api/v1/query",
        "method": "GET",
        "query_params": {
          "query": "avg(rate(http_request_duration_seconds_sum[5m]))"
        }
      }
    },
    {
      "id": "extract-value",
      "component_type": "json-transform",
      "config": {
        "data": "{{upstream.fetch-metric.body}}",
        "template": {
          "value": "{{float(data.data.result[0].value[1]) if data.data.result else 0}}",
          "threshold": "{{input.threshold}}"
        }
      },
      "depends_on": ["fetch-metric"]
    },
    {
      "id": "check-threshold",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.extract-value}}",
        "condition": "data.get('value', 0) > data.get('threshold', 1)"
      },
      "depends_on": ["extract-value"]
    },
    {
      "id": "alert-threshold-exceeded",
      "component_type": "http-request",
      "config": {
        "url": "{{env.ALERT_WEBHOOK}}",
        "method": "POST",
        "body": {
          "alert": "Threshold exceeded",
          "metric": "{{input.metric_name}}",
          "value": "{{upstream.extract-value.value}}",
          "threshold": "{{input.threshold}}",
          "severity": "warning"
        }
      },
      "depends_on": ["check-threshold"]
    }
  ]
}
```

## Alerting Integrations

### Slack Alert with Rich Formatting

```json
{
  "id": "slack-rich-alert",
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
            "text": "{{input.severity}} Alert: {{input.title}}"
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "{{input.message}}"
          }
        },
        {
          "type": "section",
          "fields": [
            {"type": "mrkdwn", "text": "*Service:*\n{{input.service}}"},
            {"type": "mrkdwn", "text": "*Environment:*\n{{input.environment}}"},
            {"type": "mrkdwn", "text": "*Time:*\n{{now()}}"},
            {"type": "mrkdwn", "text": "*Severity:*\n{{input.severity}}"}
          ]
        },
        {
          "type": "actions",
          "elements": [
            {
              "type": "button",
              "text": {"type": "plain_text", "text": "View Dashboard"},
              "url": "{{input.dashboard_url}}"
            },
            {
              "type": "button",
              "text": {"type": "plain_text", "text": "View Logs"},
              "url": "{{input.logs_url}}"
            }
          ]
        }
      ]
    }
  }
}
```

### PagerDuty Integration

```json
{
  "id": "pagerduty-create-incident",
  "component_type": "http-request",
  "config": {
    "url": "https://events.pagerduty.com/v2/enqueue",
    "method": "POST",
    "body": {
      "routing_key": "{{env.PAGERDUTY_ROUTING_KEY}}",
      "event_action": "trigger",
      "dedup_key": "{{input.dedup_key}}",
      "payload": {
        "summary": "{{input.summary}}",
        "severity": "{{input.severity}}",
        "source": "{{input.source}}",
        "timestamp": "{{now()}}",
        "component": "{{input.component}}",
        "group": "{{input.group}}",
        "class": "{{input.class}}",
        "custom_details": {
          "metric_value": "{{input.metric_value}}",
          "threshold": "{{input.threshold}}",
          "runbook_url": "{{input.runbook_url}}"
        }
      },
      "links": [
        {"href": "{{input.dashboard_url}}", "text": "Dashboard"},
        {"href": "{{input.runbook_url}}", "text": "Runbook"}
      ]
    }
  }
}
```

### OpsGenie Alert

```json
{
  "id": "opsgenie-alert",
  "component_type": "http-request",
  "config": {
    "url": "https://api.opsgenie.com/v2/alerts",
    "method": "POST",
    "headers": {
      "Authorization": "GenieKey {{env.OPSGENIE_API_KEY}}"
    },
    "body": {
      "message": "{{input.message}}",
      "alias": "{{input.alias}}",
      "description": "{{input.description}}",
      "responders": [
        {"type": "team", "name": "{{input.team}}"}
      ],
      "priority": "{{input.priority}}",
      "tags": "{{input.tags}}"
    }
  }
}
```

## AI-Enhanced Monitoring

### Anomaly Detection with AI

```json
{
  "id": "ai-anomaly-detection",
  "name": "AI Anomaly Detection",
  "stages": [
    {
      "id": "fetch-metrics-history",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PROMETHEUS_URL}}/api/v1/query_range",
        "method": "GET",
        "query_params": {
          "query": "{{input.metric_query}}",
          "start": "{{input.start_time}}",
          "end": "{{input.end_time}}",
          "step": "{{input.step}}"
        }
      }
    },
    {
      "id": "analyze-for-anomalies",
      "component_type": "generator",
      "config": {
        "prompt": "Analyze these time-series metrics for anomalies:\n\nMetric: {{input.metric_name}}\nData: {{upstream.fetch-metrics-history.body.data.result}}\n\nIdentify:\n1. Any anomalous spikes or drops\n2. Unusual patterns compared to expected behavior\n3. Trends that may indicate future issues\n4. Severity assessment (low/medium/high/critical)\n\nProvide specific timestamps and values for any anomalies found.",
        "system_prompt": "You are a metrics analysis expert. Identify anomalies in time-series data and provide actionable insights."
      },
      "depends_on": ["fetch-metrics-history"]
    },
    {
      "id": "extract-anomalies",
      "component_type": "json-transform",
      "config": {
        "template": {
          "metric": "{{input.metric_name}}",
          "analysis": "{{upstream.analyze-for-anomalies.content}}",
          "analyzed_at": "{{now()}}",
          "data_points": "{{len(upstream.fetch-metrics-history.body.data.result[0].values) if upstream.fetch-metrics-history.body.data.result else 0}}"
        }
      },
      "depends_on": ["analyze-for-anomalies"]
    }
  ]
}
```

### Smart Alert Summarization

```json
{
  "id": "smart-alert-summary",
  "name": "Smart Alert Summary",
  "stages": [
    {
      "id": "fetch-recent-alerts",
      "component_type": "http-request",
      "config": {
        "url": "{{env.ALERTMANAGER_URL}}/api/v2/alerts",
        "method": "GET",
        "query_params": {
          "filter": "active=true"
        }
      }
    },
    {
      "id": "summarize-alerts",
      "component_type": "generator",
      "config": {
        "prompt": "Summarize these active alerts and identify patterns:\n\n{{upstream.fetch-recent-alerts.body}}\n\nProvide:\n1. Executive summary (2-3 sentences)\n2. Most critical issues requiring immediate attention\n3. Related alerts that may have a common root cause\n4. Recommended priority order for addressing issues",
        "system_prompt": "You are an SRE summarizing alerts. Be concise and prioritize actionability."
      },
      "depends_on": ["fetch-recent-alerts"]
    },
    {
      "id": "format-summary",
      "component_type": "json-transform",
      "config": {
        "template": {
          "summary": "{{upstream.summarize-alerts.content}}",
          "alert_count": "{{len(upstream.fetch-recent-alerts.body)}}",
          "generated_at": "{{now()}}"
        }
      },
      "depends_on": ["summarize-alerts"]
    }
  ]
}
```

## Scheduled Monitoring

### Cron-Style Health Checks

Deploy the pipeline and configure scheduled execution:

```bash
# Deploy the health check pipeline
fm deploy health-monitor.pipeline.json --target production

# Configure scheduled execution (via Kubernetes CronJob or external scheduler)
fm kubernetes crd generate health-monitor --schedule "*/5 * * * *"
```

### Dashboard Data Collection

```json
{
  "id": "dashboard-collector",
  "name": "Dashboard Data Collector",
  "stages": [
    {
      "id": "collect-all-metrics",
      "component_type": "foreach",
      "config": {
        "items": "{{input.metrics_to_collect}}",
        "item_variable": "metric",
        "loop_stages": ["fetch-metric"],
        "collect_results": true,
        "parallel": true
      }
    },
    {
      "id": "fetch-metric",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PROMETHEUS_URL}}/api/v1/query",
        "method": "GET",
        "query_params": {
          "query": "{{context.metric.query}}"
        }
      }
    },
    {
      "id": "aggregate-dashboard-data",
      "component_type": "json-transform",
      "config": {
        "data": "{{upstream.collect-all-metrics.results}}",
        "template": {
          "dashboard_id": "{{input.dashboard_id}}",
          "metrics": "{{data}}",
          "collected_at": "{{now()}}"
        }
      },
      "depends_on": ["collect-all-metrics"]
    },
    {
      "id": "push-to-dashboard",
      "component_type": "http-request",
      "config": {
        "url": "{{env.DASHBOARD_API}}/data",
        "method": "POST",
        "body": "{{upstream.aggregate-dashboard-data}}"
      },
      "depends_on": ["aggregate-dashboard-data"]
    }
  ]
}
```

## Related Documentation

- [Incident Response](./incident-response.md)
- [CI/CD Pipelines](./ci-cd-pipelines.md)
- [API Integration](./api-integration.md)
