# API Integration

This guide covers patterns for integrating with REST APIs, webhooks, and orchestrating multiple services using Flowmason.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                 FLOWMASON API INTEGRATION ARCHITECTURE              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   EXTERNAL APIS          FLOWMASON            DESTINATIONS          │
│   ─────────────          ─────────            ────────────          │
│                                                                     │
│   ┌─────────┐        ┌─────────────────┐     ┌─────────┐           │
│   │  CRM    │◀──────▶│   Integration   │────▶│Database │           │
│   │  API    │        │    Pipeline     │     └─────────┘           │
│   └─────────┘        │                 │                           │
│                      │  ┌───────────┐  │     ┌─────────┐           │
│   ┌─────────┐        │  │ Transform │  │────▶│  Queue  │           │
│   │ Payment │◀──────▶│  │    &      │  │     └─────────┘           │
│   │  API    │        │  │  Enrich   │  │                           │
│   └─────────┘        │  └───────────┘  │     ┌─────────┐           │
│                      │                 │────▶│Downstream│           │
│   ┌─────────┐        │  ┌───────────┐  │     │  API    │           │
│   │Analytics│◀──────▶│  │    AI     │  │     └─────────┘           │
│   │  API    │        │  │ Enhance   │  │                           │
│   └─────────┘        │  └───────────┘  │     ┌─────────┐           │
│                      └─────────────────┘────▶│ Webhook │           │
│                                              └─────────┘           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## HTTP Request Patterns

### Basic GET Request

```json
{
  "id": "fetch-data",
  "component_type": "http-request",
  "config": {
    "url": "https://api.example.com/users/{{input.user_id}}",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer {{env.API_TOKEN}}",
      "Accept": "application/json"
    },
    "timeout": 30000
  }
}
```

### POST with JSON Body

```json
{
  "id": "create-resource",
  "component_type": "http-request",
  "config": {
    "url": "https://api.example.com/resources",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{env.API_TOKEN}}",
      "Content-Type": "application/json"
    },
    "body": {
      "name": "{{input.name}}",
      "type": "{{input.type}}",
      "metadata": {
        "created_by": "flowmason",
        "timestamp": "{{now()}}"
      }
    }
  }
}
```

### Query Parameters

```json
{
  "id": "search-with-params",
  "component_type": "http-request",
  "config": {
    "url": "https://api.example.com/search",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer {{env.API_TOKEN}}"
    },
    "query_params": {
      "q": "{{input.query}}",
      "limit": "{{input.limit or 10}}",
      "offset": "{{input.offset or 0}}",
      "sort": "created_at:desc"
    }
  }
}
```

### Authentication Methods

#### Bearer Token

```json
{
  "headers": {
    "Authorization": "Bearer {{env.API_TOKEN}}"
  }
}
```

#### Basic Auth

```json
{
  "headers": {
    "Authorization": "Basic {{env.BASIC_AUTH}}"
  }
}
```

#### API Key in Header

```json
{
  "headers": {
    "X-API-Key": "{{env.API_KEY}}"
  }
}
```

#### API Key in Query

```json
{
  "query_params": {
    "api_key": "{{env.API_KEY}}"
  }
}
```

#### OAuth Token Refresh

```json
{
  "id": "refresh-oauth-token",
  "component_type": "http-request",
  "config": {
    "url": "{{env.OAUTH_URL}}/token",
    "method": "POST",
    "headers": {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    "body": "grant_type=refresh_token&refresh_token={{env.REFRESH_TOKEN}}&client_id={{env.CLIENT_ID}}&client_secret={{env.CLIENT_SECRET}}"
  }
}
```

## Multi-Service Orchestration

### Sequential API Calls

```json
{
  "id": "sequential-orchestration",
  "name": "Sequential API Orchestration",
  "stages": [
    {
      "id": "fetch-user",
      "component_type": "http-request",
      "config": {
        "url": "{{env.USER_API}}/users/{{input.user_id}}",
        "method": "GET"
      }
    },
    {
      "id": "fetch-orders",
      "component_type": "http-request",
      "config": {
        "url": "{{env.ORDER_API}}/orders",
        "method": "GET",
        "query_params": {
          "user_id": "{{upstream.fetch-user.body.id}}"
        }
      },
      "depends_on": ["fetch-user"]
    },
    {
      "id": "fetch-payments",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PAYMENT_API}}/payments",
        "method": "GET",
        "query_params": {
          "user_id": "{{upstream.fetch-user.body.id}}"
        }
      },
      "depends_on": ["fetch-user"]
    },
    {
      "id": "combine-data",
      "component_type": "json-transform",
      "config": {
        "template": {
          "user": "{{upstream.fetch-user.body}}",
          "orders": "{{upstream.fetch-orders.body}}",
          "payments": "{{upstream.fetch-payments.body}}",
          "summary": {
            "total_orders": "{{len(upstream.fetch-orders.body)}}",
            "total_spent": "{{sum([p.amount for p in upstream.fetch-payments.body])}}"
          }
        }
      },
      "depends_on": ["fetch-orders", "fetch-payments"]
    }
  ]
}
```

### Parallel API Calls

```json
{
  "id": "parallel-fetch",
  "name": "Parallel API Fetch",
  "stages": [
    {
      "id": "fetch-source-a",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SOURCE_A_API}}/data",
        "method": "GET"
      }
    },
    {
      "id": "fetch-source-b",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SOURCE_B_API}}/data",
        "method": "GET"
      }
    },
    {
      "id": "fetch-source-c",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SOURCE_C_API}}/data",
        "method": "GET"
      }
    },
    {
      "id": "merge-all",
      "component_type": "json-transform",
      "config": {
        "template": {
          "source_a": "{{upstream.fetch-source-a.body}}",
          "source_b": "{{upstream.fetch-source-b.body}}",
          "source_c": "{{upstream.fetch-source-c.body}}",
          "merged_at": "{{now()}}"
        }
      },
      "depends_on": ["fetch-source-a", "fetch-source-b", "fetch-source-c"]
    }
  ]
}
```

### Fan-Out Pattern

```json
{
  "id": "fan-out-integration",
  "name": "Fan-Out to Multiple APIs",
  "stages": [
    {
      "id": "prepare-payload",
      "component_type": "json-transform",
      "config": {
        "data": "{{input}}",
        "template": {
          "event_type": "{{data.type}}",
          "payload": "{{data.payload}}",
          "timestamp": "{{now()}}"
        }
      }
    },
    {
      "id": "notify-service-a",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SERVICE_A_WEBHOOK}}",
        "method": "POST",
        "body": "{{upstream.prepare-payload}}"
      },
      "depends_on": ["prepare-payload"]
    },
    {
      "id": "notify-service-b",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SERVICE_B_WEBHOOK}}",
        "method": "POST",
        "body": "{{upstream.prepare-payload}}"
      },
      "depends_on": ["prepare-payload"]
    },
    {
      "id": "notify-service-c",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SERVICE_C_WEBHOOK}}",
        "method": "POST",
        "body": "{{upstream.prepare-payload}}"
      },
      "depends_on": ["prepare-payload"]
    },
    {
      "id": "collect-results",
      "component_type": "json-transform",
      "config": {
        "template": {
          "service_a": {"status": "{{upstream.notify-service-a.status_code}}", "success": "{{upstream.notify-service-a.success}}"},
          "service_b": {"status": "{{upstream.notify-service-b.status_code}}", "success": "{{upstream.notify-service-b.success}}"},
          "service_c": {"status": "{{upstream.notify-service-c.status_code}}", "success": "{{upstream.notify-service-c.success}}"}
        }
      },
      "depends_on": ["notify-service-a", "notify-service-b", "notify-service-c"]
    }
  ]
}
```

## Data Transformation

### Extract and Map Fields

```json
{
  "id": "transform-api-response",
  "component_type": "json-transform",
  "config": {
    "data": "{{upstream.fetch-data.body}}",
    "template": {
      "id": "{{data.id}}",
      "full_name": "{{data.first_name}} {{data.last_name}}",
      "email": "{{data.email.lower()}}",
      "created_date": "{{data.created_at[:10]}}",
      "is_active": "{{data.status == 'active'}}",
      "tags": "{{data.tags or []}}"
    }
  }
}
```

### Aggregate List Data

```json
{
  "id": "aggregate-list",
  "component_type": "json-transform",
  "config": {
    "data": "{{upstream.fetch-items.body.items}}",
    "template": {
      "total_count": "{{len(data)}}",
      "total_value": "{{sum([item.value for item in data])}}",
      "average_value": "{{sum([item.value for item in data]) / len(data) if data else 0}}",
      "by_status": {
        "active": "{{len([i for i in data if i.status == 'active'])}}",
        "inactive": "{{len([i for i in data if i.status == 'inactive'])}}"
      }
    }
  }
}
```

### Flatten Nested Data

```json
{
  "id": "flatten-nested",
  "component_type": "json-transform",
  "config": {
    "data": "{{upstream.fetch-nested.body}}",
    "template": {
      "user_id": "{{data.user.id}}",
      "user_name": "{{data.user.profile.name}}",
      "user_email": "{{data.user.contact.email}}",
      "company_name": "{{data.user.company.name}}",
      "company_size": "{{data.user.company.size}}"
    }
  }
}
```

## Webhook Handling

### Receive and Process Webhook

```json
{
  "id": "webhook-handler",
  "name": "Webhook Handler",
  "input_schema": {
    "type": "object",
    "properties": {
      "event_type": {"type": "string"},
      "payload": {"type": "object"},
      "signature": {"type": "string"}
    }
  },
  "stages": [
    {
      "id": "validate-signature",
      "component_type": "filter",
      "config": {
        "data": "{{input}}",
        "condition": "True"
      }
    },
    {
      "id": "route-by-event",
      "component_type": "router",
      "config": {
        "value": "{{input.event_type}}",
        "routes": {
          "user.created": ["handle-user-created"],
          "user.updated": ["handle-user-updated"],
          "order.placed": ["handle-order-placed"],
          "payment.completed": ["handle-payment"]
        },
        "default_route": ["log-unknown-event"]
      },
      "depends_on": ["validate-signature"]
    },
    {
      "id": "handle-user-created",
      "component_type": "http-request",
      "config": {
        "url": "{{env.USER_SERVICE}}/sync",
        "method": "POST",
        "body": "{{input.payload}}"
      }
    },
    {
      "id": "log-unknown-event",
      "component_type": "logger",
      "config": {
        "message": "Unknown webhook event: {{input.event_type}}",
        "level": "warning",
        "data": "{{input}}"
      }
    }
  ]
}
```

### Send Webhook

```json
{
  "id": "send-webhook",
  "component_type": "http-request",
  "config": {
    "url": "{{input.webhook_url}}",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "X-Webhook-Signature": "{{input.signature}}",
      "X-Webhook-Timestamp": "{{now()}}"
    },
    "body": {
      "event": "{{input.event_type}}",
      "data": "{{input.payload}}",
      "timestamp": "{{now()}}"
    }
  }
}
```

## ETL Patterns

### Extract-Transform-Load

```json
{
  "id": "etl-pipeline",
  "name": "ETL Pipeline",
  "stages": [
    {
      "id": "extract",
      "component_type": "http-request",
      "config": {
        "url": "{{env.SOURCE_API}}/export",
        "method": "GET",
        "query_params": {
          "since": "{{input.last_sync}}",
          "limit": "1000"
        }
      }
    },
    {
      "id": "validate-extract",
      "component_type": "schema-validate",
      "config": {
        "data": "{{upstream.extract.body}}",
        "schema": {
          "type": "object",
          "required": ["records"],
          "properties": {
            "records": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["id", "data"]
              }
            }
          }
        }
      },
      "depends_on": ["extract"]
    },
    {
      "id": "transform",
      "component_type": "foreach",
      "config": {
        "items": "{{upstream.validate-extract.data.records}}",
        "item_variable": "record",
        "loop_stages": ["transform-record"],
        "collect_results": true,
        "parallel": true,
        "max_parallel": 10
      },
      "depends_on": ["validate-extract"]
    },
    {
      "id": "transform-record",
      "component_type": "json-transform",
      "config": {
        "data": "{{context.record}}",
        "template": {
          "id": "{{data.id}}",
          "name": "{{data.data.name.strip()}}",
          "email": "{{data.data.email.lower()}}",
          "created_at": "{{data.created_at}}",
          "synced_at": "{{now()}}"
        }
      }
    },
    {
      "id": "load",
      "component_type": "http-request",
      "config": {
        "url": "{{env.DESTINATION_API}}/import",
        "method": "POST",
        "body": {
          "records": "{{upstream.transform.results}}"
        }
      },
      "depends_on": ["transform"]
    },
    {
      "id": "log-completion",
      "component_type": "logger",
      "config": {
        "message": "ETL completed",
        "level": "info",
        "data": {
          "records_processed": "{{len(upstream.transform.results)}}",
          "load_status": "{{upstream.load.status_code}}"
        }
      },
      "depends_on": ["load"]
    }
  ]
}
```

## Error Handling

### Retry with Backoff

```json
{
  "id": "api-with-retry",
  "component_type": "http-request",
  "config": {
    "url": "{{env.API_URL}}/endpoint",
    "method": "POST",
    "body": "{{input}}"
  },
  "error_handling": {
    "on_error": "retry",
    "max_retries": 3,
    "retry_delay": 1000
  }
}
```

### Fallback on Failure

```json
{
  "id": "api-with-fallback",
  "name": "API with Fallback",
  "stages": [
    {
      "id": "try-primary",
      "component_type": "trycatch",
      "config": {
        "try_stages": ["call-primary-api"],
        "catch_stages": ["call-fallback-api"],
        "finally_stages": ["log-result"]
      }
    },
    {
      "id": "call-primary-api",
      "component_type": "http-request",
      "config": {
        "url": "{{env.PRIMARY_API}}/data",
        "method": "GET",
        "timeout": 5000
      }
    },
    {
      "id": "call-fallback-api",
      "component_type": "http-request",
      "config": {
        "url": "{{env.FALLBACK_API}}/data",
        "method": "GET",
        "timeout": 10000
      }
    },
    {
      "id": "log-result",
      "component_type": "logger",
      "config": {
        "message": "API call completed",
        "level": "info"
      }
    }
  ]
}
```

### Circuit Breaker Pattern

```json
{
  "id": "circuit-breaker",
  "name": "Circuit Breaker",
  "stages": [
    {
      "id": "check-circuit-status",
      "component_type": "http-request",
      "config": {
        "url": "{{env.CIRCUIT_BREAKER_API}}/status/{{input.service}}",
        "method": "GET"
      }
    },
    {
      "id": "evaluate-circuit",
      "component_type": "conditional",
      "config": {
        "condition": "{{upstream.check-circuit-status.body.state}} == 'closed'",
        "true_stages": ["make-api-call"],
        "false_stages": ["return-cached-response"]
      },
      "depends_on": ["check-circuit-status"]
    },
    {
      "id": "make-api-call",
      "component_type": "trycatch",
      "config": {
        "try_stages": ["call-api"],
        "catch_stages": ["record-failure", "return-cached-response"]
      }
    },
    {
      "id": "call-api",
      "component_type": "http-request",
      "config": {
        "url": "{{input.api_url}}",
        "method": "{{input.method}}",
        "body": "{{input.body}}"
      }
    },
    {
      "id": "record-failure",
      "component_type": "http-request",
      "config": {
        "url": "{{env.CIRCUIT_BREAKER_API}}/failure/{{input.service}}",
        "method": "POST"
      }
    },
    {
      "id": "return-cached-response",
      "component_type": "http-request",
      "config": {
        "url": "{{env.CACHE_API}}/{{input.service}}/latest",
        "method": "GET"
      }
    }
  ]
}
```

## Pagination

### Paginated API Fetch

```json
{
  "id": "paginated-fetch",
  "name": "Paginated Fetch",
  "stages": [
    {
      "id": "initialize",
      "component_type": "variable-set",
      "config": {
        "variables": {
          "all_results": [],
          "page": 1,
          "has_more": true
        }
      }
    },
    {
      "id": "fetch-page",
      "component_type": "http-request",
      "config": {
        "url": "{{env.API_URL}}/items",
        "method": "GET",
        "query_params": {
          "page": "{{context.page}}",
          "per_page": "100"
        }
      },
      "depends_on": ["initialize"]
    },
    {
      "id": "check-more-pages",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.fetch-page.body}}",
        "condition": "len(data.get('items', [])) == 100"
      },
      "depends_on": ["fetch-page"]
    },
    {
      "id": "aggregate-results",
      "component_type": "json-transform",
      "config": {
        "template": {
          "items": "{{upstream.fetch-page.body.items}}",
          "total_fetched": "{{len(upstream.fetch-page.body.items)}}"
        }
      },
      "depends_on": ["fetch-page"]
    }
  ]
}
```

## Related Documentation

- [CI/CD Pipelines](./ci-cd-pipelines.md)
- [Monitoring & Alerting](./monitoring-alerting.md)
- [Incident Response](./incident-response.md)
