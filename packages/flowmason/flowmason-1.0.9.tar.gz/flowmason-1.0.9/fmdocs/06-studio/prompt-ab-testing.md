# Prompt A/B Testing

FlowMason supports A/B testing for prompts, allowing you to compare different prompt variants and determine which performs better using statistical analysis.

## Overview

Prompt A/B testing enables:
- **Variant Comparison**: Test multiple prompt versions side-by-side
- **Traffic Allocation**: Control what percentage of requests use each variant
- **Metric Collection**: Track latency, ratings, custom metrics
- **Statistical Analysis**: Determine winners with confidence levels
- **Sticky Assignment**: Users consistently see the same variant

## Creating an Experiment

### Basic Experiment

```http
POST /api/v1/experiments
Content-Type: application/json

{
  "name": "Summarization Prompt Test",
  "description": "Testing concise vs detailed summaries",
  "variants": [
    {
      "name": "Control",
      "is_control": true,
      "content": "Summarize the following text:\n\n{{text}}",
      "weight": 1.0
    },
    {
      "name": "Concise",
      "content": "Summarize the following text in 2-3 sentences:\n\n{{text}}",
      "weight": 1.0
    },
    {
      "name": "Detailed",
      "content": "Provide a detailed summary with key points:\n\n{{text}}",
      "weight": 1.0
    }
  ],
  "metrics": [
    {
      "name": "rating",
      "type": "rating",
      "description": "User satisfaction (1-5)",
      "higher_is_better": true
    },
    {
      "name": "latency",
      "type": "latency",
      "description": "Response time in ms",
      "higher_is_better": false
    }
  ],
  "primary_metric": "rating",
  "min_samples_per_variant": 100
}
```

### Using Existing Prompts

```json
{
  "name": "Template Comparison",
  "variants": [
    {
      "name": "Current Template",
      "is_control": true,
      "prompt_id": "prompt_abc123"
    },
    {
      "name": "New Template",
      "prompt_id": "prompt_xyz789"
    }
  ]
}
```

### Targeting Specific Pipelines

```json
{
  "name": "Pipeline-Specific Test",
  "pipeline_ids": ["pipe_abc123", "pipe_def456"],
  "stage_ids": ["stage_summarize"],
  "user_percentage": 50.0,
  "variants": [...]
}
```

## Experiment Lifecycle

### 1. Create (Draft)
```http
POST /api/v1/experiments
```

### 2. Start (Running)
```http
POST /api/v1/experiments/{id}/start
```

### 3. Collect Data
Variant selection and metric recording happen automatically during pipeline execution.

### 4. Pause (Optional)
```http
POST /api/v1/experiments/{id}/pause
```

### 5. Complete
```http
POST /api/v1/experiments/{id}/complete
```

## Variant Selection

### Automatic Selection

```http
POST /api/v1/experiments/{experiment_id}/select
Content-Type: application/json

{
  "user_id": "user_123",
  "pipeline_id": "pipe_abc",
  "stage_id": "summarize"
}
```

**Response:**
```json
{
  "experiment_id": "exp_abc123",
  "variant_id": "var_001",
  "variant_name": "Concise",
  "prompt_content": "Summarize the following text in 2-3 sentences:\n\n{{text}}",
  "system_prompt": null,
  "model": "claude-3-5-sonnet-latest",
  "temperature": 0.7,
  "max_tokens": 500,
  "is_control": false
}
```

### Sticky Assignment

Users are consistently assigned to the same variant using a hash of their user ID and experiment ID. This ensures:
- Consistent experience for each user
- No variant switching mid-session
- Reliable A/B comparison

## Recording Metrics

### Single Metric

```http
POST /api/v1/experiments/{experiment_id}/metrics
Content-Type: application/json

{
  "variant_id": "var_001",
  "metric_name": "rating",
  "value": 4.5,
  "user_id": "user_123",
  "run_id": "run_abc"
}
```

### Batch Metrics

```http
POST /api/v1/experiments/{experiment_id}/metrics/batch
Content-Type: application/json

{
  "variant_id": "var_001",
  "metrics": {
    "rating": 4.5,
    "latency": 1250,
    "tokens": 350
  },
  "user_id": "user_123",
  "run_id": "run_abc"
}
```

## Getting Results

```http
GET /api/v1/experiments/{experiment_id}/results
```

**Response:**
```json
{
  "experiment_id": "exp_abc123",
  "experiment_name": "Summarization Prompt Test",
  "status": "running",
  "primary_metric": "rating",
  "variant_stats": [
    {
      "variant_id": "var_001",
      "variant_name": "Control",
      "is_control": true,
      "impressions": 1250,
      "samples": 1180,
      "metrics": {
        "rating": {
          "mean": 3.8,
          "std": 0.9,
          "min": 1.0,
          "max": 5.0,
          "p50": 4.0,
          "p95": 5.0
        }
      }
    },
    {
      "variant_id": "var_002",
      "variant_name": "Concise",
      "is_control": false,
      "impressions": 1245,
      "samples": 1175,
      "metrics": {
        "rating": {
          "mean": 4.2,
          "std": 0.7,
          "min": 2.0,
          "max": 5.0,
          "p50": 4.0,
          "p95": 5.0
        }
      },
      "lift_vs_control": 10.5,
      "p_value": 0.01,
      "is_significant": true
    }
  ],
  "has_winner": true,
  "winner_variant_id": "var_002",
  "winner_variant_name": "Concise",
  "confidence_level": 0.99,
  "recommendation": "'Concise' outperforms control by 10.5% on rating. Confidence: 99.0%",
  "total_samples": 2355,
  "duration_hours": 72.5
}
```

## Metric Types

| Type | Description | Example Values |
|------|-------------|----------------|
| `latency` | Response time in ms | 250, 1500, 3000 |
| `tokens` | Token count | 100, 500, 2000 |
| `rating` | User rating (1-5) | 1, 3, 4.5, 5 |
| `thumbs` | Binary feedback | 0, 1 |
| `completion` | Task completion rate | 0.0 - 1.0 |
| `custom` | Any numeric value | Any float |

## Statistical Analysis

### Confidence Levels

Results show statistical significance using Welch's t-test:

| p-value | Significance | Confidence |
|---------|-------------|------------|
| < 0.01 | Very significant | > 99% |
| < 0.05 | Significant | > 95% |
| < 0.10 | Marginally significant | > 90% |
| >= 0.10 | Not significant | < 90% |

### Minimum Sample Size

Set `min_samples_per_variant` to ensure statistical validity:
- Small effects: 1000+ samples per variant
- Medium effects: 500+ samples
- Large effects: 100+ samples

## Python Integration

### Selecting Variants

```python
from flowmason_studio.services.experiment_storage import get_experiment_storage

storage = get_experiment_storage()

# Select variant for user
result = storage.select_variant(
    experiment_id="exp_abc123",
    user_id="user_456",
    pipeline_id="pipe_summarize",
)

if result:
    experiment, variant = result
    # Use variant.content for prompt
    print(f"Using variant: {variant.name}")
```

### Recording Metrics

```python
# Record single metric
storage.record_metric(
    experiment_id="exp_abc123",
    variant_id="var_001",
    metric_name="rating",
    value=4.5,
    user_id="user_456",
)

# Record multiple metrics
storage.record_metrics(
    experiment_id="exp_abc123",
    variant_id="var_001",
    metrics={
        "rating": 4.5,
        "latency": 1250,
        "tokens": 350,
    },
    user_id="user_456",
)
```

### Getting Results

```python
results = storage.get_results("exp_abc123")

if results.has_winner:
    print(f"Winner: {results.winner_variant_name}")
    print(f"Confidence: {results.confidence_level * 100:.1f}%")
    print(f"Recommendation: {results.recommendation}")
```

## Best Practices

1. **Start with a Control**: Always include your current prompt as the control variant
2. **Equal Weights Initially**: Start with equal traffic allocation
3. **Sufficient Sample Size**: Wait for minimum samples before drawing conclusions
4. **Single Variable Testing**: Change one thing at a time between variants
5. **Monitor Early**: Check for obvious issues in the first few hours
6. **Document Variants**: Use clear names and descriptions

## Traffic Allocation

### Equal Split
```json
{
  "variants": [
    {"name": "Control", "weight": 1.0},
    {"name": "Variant A", "weight": 1.0},
    {"name": "Variant B", "weight": 1.0}
  ]
}
```

### Weighted Split (80/20)
```json
{
  "variants": [
    {"name": "Control", "weight": 4.0},
    {"name": "Risky Variant", "weight": 1.0}
  ]
}
```

### Partial Rollout
```json
{
  "user_percentage": 10.0,
  "variants": [...]
}
```
Only 10% of users participate in the experiment.

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/experiments` | GET | List experiments |
| `/experiments` | POST | Create experiment |
| `/experiments/{id}` | GET | Get experiment |
| `/experiments/{id}` | PUT | Update experiment |
| `/experiments/{id}` | DELETE | Delete experiment |
| `/experiments/{id}/start` | POST | Start experiment |
| `/experiments/{id}/pause` | POST | Pause experiment |
| `/experiments/{id}/resume` | POST | Resume experiment |
| `/experiments/{id}/complete` | POST | Complete experiment |
| `/experiments/{id}/select` | POST | Select variant |
| `/experiments/{id}/metrics` | POST | Record metric |
| `/experiments/{id}/metrics/batch` | POST | Record multiple metrics |
| `/experiments/{id}/results` | GET | Get results |
| `/experiments/{id}/declare-winner` | POST | Manually declare winner |
| `/experiments/running` | GET | List running experiments |
| `/experiments/stats` | GET | Get statistics |
