# Execution Analytics & AI Insights

FlowMason Studio provides AI-powered analytics that automatically detect patterns, anomalies, and optimization opportunities in your pipeline executions.

## Overview

The insights engine analyzes your execution history to provide:

- **Cost Analysis**: Track spending, detect spikes, forecast future costs
- **Performance Monitoring**: Identify degradation, latency outliers, slow stages
- **Reliability Tracking**: Failure patterns, error type distribution, MTTR
- **Usage Patterns**: Peak hours, busiest pipelines, model preferences
- **Optimization Recommendations**: Model selection, cost reduction opportunities

## Quick Start

### Get Insights Summary

```http
GET /api/v1/analytics/insights/summary
```

Returns the most important insights at a glance:

```json
{
  "generated_at": "2024-01-15T10:30:00Z",
  "total_insights": 5,
  "critical_count": 1,
  "warning_count": 2,
  "info_count": 2,
  "top_cost_insight": {
    "type": "cost_spike",
    "severity": "warning",
    "title": "Cost increased by 45%",
    "description": "Spending increased from $12.50 to $18.12..."
  },
  "top_performance_insight": null,
  "top_reliability_insight": {
    "type": "failure_pattern",
    "severity": "critical",
    "title": "Critical failure rate: 28%"
  },
  "estimated_savings": 8.50,
  "performance_change_percent": -5.2,
  "reliability_change_percent": 3.1
}
```

### Get Full Report

```http
GET /api/v1/analytics/insights/report?days=30
```

Returns a comprehensive analysis including:

- Trend analysis (cost, usage, performance, reliability)
- Cost breakdown by provider, model, and pipeline
- Performance metrics (p50, p95, p99 latency)
- Failure analysis with error type distribution
- Cost forecasting
- Optimization opportunities

### Get Filtered Insights

```http
GET /api/v1/analytics/insights?category=cost&severity=warning
```

Filter insights by:
- `category`: cost, performance, reliability, usage, optimization
- `severity`: critical, warning, info
- `pipeline_id`: Focus on a specific pipeline

## Insight Types

### Cost Insights

| Type | Description | Severity |
|------|-------------|----------|
| `cost_spike` | Spending increased significantly | Warning/Critical |
| `cost_optimization` | Model concentration or waste detected | Info |
| `model_recommendation` | Cheaper model could be used | Info |

**Example:**
```json
{
  "type": "cost_spike",
  "severity": "warning",
  "category": "cost",
  "title": "Cost increased by 45%",
  "description": "Spending increased from $12.50 to $18.12 compared to the previous period.",
  "data": {
    "previous_cost": 12.50,
    "current_cost": 18.12,
    "increase_percent": 45
  },
  "recommendations": [
    "Review usage patterns to identify unexpected increases",
    "Consider using smaller models for simple tasks",
    "Check for runaway or stuck pipelines"
  ]
}
```

### Performance Insights

| Type | Description | Severity |
|------|-------------|----------|
| `performance_degradation` | Execution time increased significantly | Warning |
| `performance_improvement` | Execution time decreased | Info |
| `anomaly` | High latency variability detected | Info |

**Example:**
```json
{
  "type": "performance_degradation",
  "severity": "warning",
  "category": "performance",
  "title": "Execution time increased by 35%",
  "description": "Average execution time increased from 1200ms to 1620ms.",
  "data": {
    "previous_avg_ms": 1200,
    "current_avg_ms": 1620
  },
  "recommendations": [
    "Check for slow API responses or rate limiting",
    "Review any recent pipeline changes",
    "Consider caching repeated operations"
  ]
}
```

### Reliability Insights

| Type | Description | Severity |
|------|-------------|----------|
| `failure_pattern` | High or elevated failure rate | Critical/Warning |
| `reliability` | Reliability issues detected | Warning |

**Example:**
```json
{
  "type": "failure_pattern",
  "severity": "critical",
  "category": "reliability",
  "title": "Critical failure rate: 28%",
  "description": "42 of 150 runs failed. Immediate attention required.",
  "data": {
    "failure_rate": 0.28,
    "total_failures": 42,
    "by_error_type": {
      "api_error": 25,
      "timeout": 12,
      "validation_error": 5
    }
  },
  "recommendations": [
    "Check recent changes to pipelines or configurations",
    "Verify API credentials and rate limits",
    "Review error logs for root cause"
  ]
}
```

## Trends and Analysis

### Trend Direction

Each metric includes trend analysis:

```json
{
  "cost_trend": {
    "metric_name": "cost",
    "current_value": 18.12,
    "previous_value": 12.50,
    "change_percent": 44.96,
    "direction": "up",
    "is_significant": true
  }
}
```

Directions: `up`, `down`, `stable`

### Performance Metrics

```json
{
  "performance_metrics": {
    "avg_duration_ms": 1250,
    "p50_duration_ms": 1100,
    "p95_duration_ms": 2800,
    "p99_duration_ms": 4500,
    "slowest_stages": [],
    "fastest_stages": []
  }
}
```

### Failure Analysis

```json
{
  "failure_analysis": {
    "total_failures": 42,
    "failure_rate": 0.28,
    "by_error_type": {
      "api_error": 25,
      "timeout": 12,
      "validation_error": 5
    },
    "by_pipeline": {
      "pipeline_abc": 30,
      "pipeline_xyz": 12
    },
    "common_patterns": [
      "Most failures (25) are api_error",
      "Pipeline pipeline_abc accounts for most failures"
    ]
  }
}
```

## Cost Forecasting

```json
{
  "cost_forecast": {
    "current_daily_avg": 2.50,
    "projected_daily": 2.75,
    "projected_weekly": 19.25,
    "projected_monthly": 82.50,
    "trend": "up",
    "confidence": 0.85
  }
}
```

## Optimization Opportunities

The insights engine identifies actionable optimization opportunities:

```json
{
  "optimization_opportunities": [
    {
      "type": "model_downgrade",
      "description": "Switch from claude-3-opus to claude-3-haiku for simple tasks",
      "current_cost": 45.00,
      "potential_savings": 31.50,
      "savings_percent": 70,
      "recommendation": "Route simpler tasks to claude-3-haiku which is significantly cheaper",
      "difficulty": "medium"
    },
    {
      "type": "reliability",
      "description": "Reduce failures to cut wasted resources",
      "current_cost": 5.60,
      "potential_savings": 4.48,
      "savings_percent": 22,
      "recommendation": "Address common failure causes to reduce wasted API calls",
      "difficulty": "medium"
    }
  ]
}
```

## Model Efficiency

Compare efficiency across models:

```json
{
  "model_efficiency": [
    {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "avg_latency_ms": 1200,
      "avg_tokens_per_request": 850,
      "cost_per_1k_tokens": 0.0045,
      "success_rate": 0.98,
      "usage_count": 1250
    },
    {
      "provider": "openai",
      "model": "gpt-4o-mini",
      "avg_latency_ms": 800,
      "avg_tokens_per_request": 620,
      "cost_per_1k_tokens": 0.00015,
      "success_rate": 0.99,
      "usage_count": 850
    }
  ]
}
```

## Python Integration

```python
from flowmason_studio.services.insights_service import get_insights_service

# Get insights service
service = get_insights_service()

# Generate full report
report = service.generate_report(
    org_id="default",
    days=30,
    include_recommendations=True,
    include_forecasts=True,
)

# Print summary
print(f"Total insights: {len(report.insights)}")
print(f"Estimated savings: ${sum(o.potential_savings for o in report.optimization_opportunities):.2f}")

# Check for critical issues
critical = [i for i in report.insights if i.severity.value == "critical"]
if critical:
    print(f"ALERT: {len(critical)} critical issues detected!")
    for insight in critical:
        print(f"  - {insight.title}")

# Get quick summary
summary = service.get_summary(org_id="default", days=7)
print(f"Critical: {summary.critical_count}")
print(f"Warnings: {summary.warning_count}")

# Filter insights by category
cost_insights = service.get_insights(
    org_id="default",
    days=7,
    category=InsightCategory.COST,
)
```

## Thresholds

The insights engine uses these thresholds for detection:

| Metric | Warning | Critical |
|--------|---------|----------|
| Cost spike | 50% increase | 100% increase |
| Failure rate | 10% | 25% |
| Performance degradation | 30% slower | N/A |
| Significant change | 10% | N/A |

## Best Practices

1. **Review daily**: Check the insights summary daily for critical issues
2. **Act on critical**: Address critical severity insights immediately
3. **Track trends**: Monitor trend directions over time
4. **Optimize incrementally**: Address one optimization opportunity at a time
5. **Set alerts**: Integrate with webhooks to alert on critical insights
6. **Compare periods**: Use different time ranges to spot patterns

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analytics/insights/report` | GET | Full insights report |
| `/analytics/insights/summary` | GET | Quick summary |
| `/analytics/insights` | GET | Filtered insights list |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `org_id` | string | "default" | Organization ID |
| `days` | int | 7-30 | Analysis period |
| `pipeline_id` | string | null | Filter by pipeline |
| `category` | enum | null | cost/performance/reliability/usage/optimization |
| `severity` | enum | null | critical/warning/info |
| `include_recommendations` | bool | true | Include recommendations |
| `include_forecasts` | bool | true | Include cost forecasts |
