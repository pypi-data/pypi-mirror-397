# LLM Usage Tracking

FlowMason tracks token usage and costs across all LLM calls in your pipelines.

## Overview

Usage tracking provides:
- Per-run token usage and costs
- Aggregated usage by pipeline, provider, and model
- Daily usage trends
- Cost estimation for planning

## API Endpoints

### Get Usage Summary

```http
GET /api/v1/usage/summary?days=30
Authorization: Bearer <api-key>
```

Response:
```json
{
  "period_start": "2025-01-01T00:00:00",
  "period_end": "2025-01-31T00:00:00",
  "total_runs": 150,
  "total_stages": 450,
  "total_input_tokens": 1250000,
  "total_output_tokens": 320000,
  "total_tokens": 1570000,
  "total_cost_usd": 4.85,
  "by_provider": {
    "anthropic": {
      "input_tokens": 800000,
      "output_tokens": 200000,
      "total_tokens": 1000000,
      "cost_usd": 3.20,
      "request_count": 300
    },
    "openai": {
      "input_tokens": 450000,
      "output_tokens": 120000,
      "total_tokens": 570000,
      "cost_usd": 1.65,
      "request_count": 150
    }
  },
  "by_model": {
    "anthropic:claude-3-5-sonnet-20241022": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "input_tokens": 800000,
      "output_tokens": 200000,
      "cost_usd": 3.20,
      "request_count": 300
    }
  }
}
```

### Get Daily Usage

```http
GET /api/v1/usage/daily?days=7
Authorization: Bearer <api-key>
```

Response:
```json
[
  {
    "date": "2025-01-25",
    "run_count": 25,
    "stage_count": 75,
    "input_tokens": 180000,
    "output_tokens": 45000,
    "total_tokens": 225000,
    "cost_usd": 0.68
  },
  {
    "date": "2025-01-26",
    "run_count": 32,
    "stage_count": 96,
    "input_tokens": 210000,
    "output_tokens": 52000,
    "total_tokens": 262000,
    "cost_usd": 0.79
  }
]
```

### Get Run Usage

```http
GET /api/v1/usage/runs/{run_id}
Authorization: Bearer <api-key>
```

Response:
```json
{
  "run_id": "run-abc123",
  "total_input_tokens": 12500,
  "total_output_tokens": 3200,
  "total_tokens": 15700,
  "total_cost_usd": 0.048,
  "records": [
    {
      "id": "usage-xyz",
      "run_id": "run-abc123",
      "pipeline_id": "pipe-123",
      "stage_id": "generate-summary",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "input_tokens": 8000,
      "output_tokens": 2000,
      "total_tokens": 10000,
      "cost_usd": 0.032,
      "duration_ms": 1250,
      "recorded_at": "2025-01-26T10:30:00Z"
    }
  ]
}
```

### Get Pricing

```http
GET /api/v1/usage/pricing
Authorization: Bearer <api-key>
```

Response:
```json
{
  "pricing": {
    "anthropic": {
      "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
      "claude-3-5-haiku-20241022": {"input": 1.0, "output": 5.0},
      "claude-3-opus-20240229": {"input": 15.0, "output": 75.0}
    },
    "openai": {
      "gpt-4o": {"input": 2.5, "output": 10.0},
      "gpt-4o-mini": {"input": 0.15, "output": 0.60}
    }
  },
  "updated_at": "2025-01-26T00:00:00Z"
}
```

Pricing is in USD per 1 million tokens.

### Estimate Cost

```http
GET /api/v1/usage/estimate?provider=anthropic&model=claude-3-5-sonnet-20241022&input_tokens=10000&output_tokens=2000
Authorization: Bearer <api-key>
```

Response:
```json
{
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022",
  "input_tokens": 10000,
  "output_tokens": 2000,
  "total_tokens": 12000,
  "pricing_per_million": {"input": 3.0, "output": 15.0},
  "estimated_cost": {
    "input_cost_usd": 0.03,
    "output_cost_usd": 0.03,
    "total_cost_usd": 0.06
  }
}
```

## Query Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `days` | Number of days to include | 30 |
| `pipeline_id` | Filter by pipeline | All pipelines |
| `include_by_pipeline` | Include breakdown by pipeline | false |

## Supported Providers

Usage is automatically tracked for all supported LLM providers:

| Provider | Models |
|----------|--------|
| Anthropic | Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku |
| OpenAI | GPT-4o, GPT-4o-mini, GPT-4 Turbo, GPT-4, GPT-3.5 Turbo |
| Google | Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 2.0 Flash |
| Groq | Llama 3.3 70B, Llama 3.1 70B, Mixtral 8x7B |

## How It Works

1. When a pipeline stage makes an LLM call, the provider returns token counts
2. FlowMason records the usage with provider, model, and token counts
3. Cost is calculated based on current pricing
4. Data is aggregated daily for fast queries

## Data Retention

- Detailed per-stage records: 90 days
- Daily aggregates: 1 year
- Summary statistics: Indefinite

## Use Cases

### Cost Optimization

Compare costs across models:

```http
GET /api/v1/usage/summary?days=30&include_by_pipeline=true
```

Identify expensive pipelines and consider:
- Using smaller models for simpler tasks
- Caching common queries
- Batching similar requests

### Budget Monitoring

Track daily spend against budget:

```http
GET /api/v1/usage/daily?days=30
```

### Cost Estimation

Before deploying a pipeline, estimate costs:

```http
GET /api/v1/usage/estimate?provider=anthropic&model=claude-3-5-sonnet-20241022&input_tokens=100000&output_tokens=20000
```

## Best Practices

1. **Choose the right model**: Use smaller models (Haiku, GPT-4o-mini) for simple tasks
2. **Monitor trends**: Watch for unexpected cost increases
3. **Set alerts**: Create webhook triggers for high usage thresholds
4. **Cache when possible**: Use the `memory` operator to cache repeated queries
5. **Batch requests**: Group similar requests to reduce overhead
