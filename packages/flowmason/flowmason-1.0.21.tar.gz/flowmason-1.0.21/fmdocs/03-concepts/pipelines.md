# Pipelines

## What is a Pipeline?

A **Pipeline** is a directed acyclic graph (DAG) of stages that process data. Stages are connected by dependencies, and the executor runs them in topological order.

## Pipeline Structure

### Current Format (Studio Database)

Pipelines are currently stored in SQLite with this structure:

```json
{
  "id": "pipeline-uuid",
  "name": "content-processing",
  "description": "Process and summarize content",
  "version": "1.0.0",
  "status": "DRAFT",
  "category": "text",
  "tags": ["content", "summarization"],
  "stages": [...],
  "input_schema": {...},
  "output_schema": {...},
  "sample_input": {...},
  "created_at": "2025-12-11T00:00:00Z",
  "updated_at": "2025-12-11T00:00:00Z"
}
```

### Future Format (`.pipeline.json`)

File-based pipelines for Git versioning:

```json
{
  "name": "content-processing",
  "version": "1.0.0",
  "description": "Process and summarize content",
  "stages": [
    {
      "id": "fetch",
      "component": "http-request",
      "config": {
        "url": "{{input.url}}",
        "method": "GET"
      }
    },
    {
      "id": "summarize",
      "component": "generator",
      "depends_on": ["fetch"],
      "config": {
        "prompt": "Summarize: {{fetch.output.body}}"
      }
    }
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "url": { "type": "string", "format": "uri" }
    },
    "required": ["url"]
  }
}
```

## Stages

A stage is a single step in the pipeline:

```json
{
  "id": "summarize",
  "component": "generator",
  "depends_on": ["fetch", "clean"],
  "config": {
    "prompt": "{{fetch.output.body}}",
    "max_tokens": 500
  },
  "llm_settings": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.7
  }
}
```

### Stage Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique stage identifier |
| `component` | string | Yes | Component name to execute |
| `depends_on` | string[] | No | Stage IDs this depends on |
| `config` | object | Yes | Component input configuration |
| `llm_settings` | object | No | LLM override settings |

## Dependencies

Stages specify dependencies with `depends_on`:

```
       ┌─────────┐
       │  fetch  │
       └────┬────┘
            │
       ┌────▼────┐
       │  clean  │
       └────┬────┘
            │
    ┌───────┴───────┐
    │               │
┌───▼───┐      ┌────▼────┐
│extract│      │summarize│
└───┬───┘      └────┬────┘
    │               │
    └───────┬───────┘
            │
       ┌────▼────┐
       │ combine │
       └─────────┘
```

```json
[
  { "id": "fetch", "component": "http-request" },
  { "id": "clean", "component": "json-transform", "depends_on": ["fetch"] },
  { "id": "extract", "component": "json-transform", "depends_on": ["clean"] },
  { "id": "summarize", "component": "generator", "depends_on": ["clean"] },
  { "id": "combine", "component": "synthesizer", "depends_on": ["extract", "summarize"] }
]
```

## Input Mapping

Reference upstream outputs with template syntax:

### Accessing Upstream Outputs

```json
{
  "config": {
    "text": "{{fetch.output.body}}",
    "count": "{{extract.output.items.length}}"
  }
}
```

### Accessing Pipeline Input

```json
{
  "config": {
    "url": "{{input.url}}",
    "max_length": "{{input.settings.max_length}}"
  }
}
```

### Template Syntax

| Syntax | Description |
|--------|-------------|
| `{{input.field}}` | Pipeline input |
| `{{stage_id.output.field}}` | Stage output |
| `{{stage_id.output.nested.field}}` | Nested field |
| `{{stage_id.output.items[0]}}` | Array index |

## Pipeline Status

| Status | Description |
|--------|-------------|
| `DRAFT` | Being edited, not ready for production |
| `PUBLISHED` | Validated and ready for use |

**Publish Requirements:**
- At least one successful test run
- All stages have valid components
- No circular dependencies

## Execution

### How Execution Works

1. **Parse** - Load pipeline definition
2. **Validate** - Check dependencies, component availability
3. **Topological Sort** - Order stages by dependencies
4. **Execute** - Run each stage in order
5. **Collect Results** - Aggregate outputs and metrics

### Current Execution (Sequential)

The DAGExecutor currently runs stages sequentially:

```
Stage 1 → Stage 2 → Stage 3 → Stage 4
```

Independent stages still run one at a time.

### Future: Parallel Execution

Independent stages could run in parallel:

```
Stage 1 ─┬─► Stage 2a ─┬─► Stage 3
         └─► Stage 2b ─┘
```

## Execution Results

### Run Result

```json
{
  "run_id": "run-uuid",
  "pipeline_id": "pipeline-uuid",
  "status": "COMPLETED",
  "stage_results": {
    "fetch": {
      "status": "success",
      "output": { "body": "..." },
      "duration_ms": 234
    },
    "summarize": {
      "status": "success",
      "output": { "summary": "..." },
      "duration_ms": 1523
    }
  },
  "final_output": { "summary": "..." },
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 200,
    "total_tokens": 1700,
    "cost_usd": 0.0051,
    "duration_ms": 1757
  }
}
```

### Stage Result

```json
{
  "component_id": "summarize",
  "component_type": "generator",
  "status": "success",
  "output": { "summary": "...", "word_count": 50 },
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 200,
    "duration_ms": 1523,
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514"
  },
  "started_at": "2025-12-11T10:00:00Z",
  "completed_at": "2025-12-11T10:00:01.523Z"
}
```

## Debugging

### Breakpoints

Set breakpoints on stages to pause execution:

```json
{
  "breakpoints": ["summarize", "combine"]
}
```

### Debug Commands

| Command | Description |
|---------|-------------|
| `pause` | Pause execution at current stage |
| `resume` | Continue execution |
| `step` | Execute one stage, then pause |
| `stop` | Stop execution entirely |

### WebSocket Events

Real-time updates during execution:

| Event | Description |
|-------|-------------|
| `RUN_STARTED` | Pipeline execution began |
| `STAGE_STARTED` | Stage execution began |
| `STAGE_COMPLETED` | Stage finished successfully |
| `STAGE_FAILED` | Stage encountered error |
| `BREAKPOINT_HIT` | Paused at breakpoint |
| `RUN_COMPLETED` | Pipeline finished |
| `RUN_FAILED` | Pipeline failed |

## Best Practices

1. **Meaningful stage IDs** - `fetch-user-data` not `stage1`
2. **Single responsibility** - Each stage does one thing
3. **Handle errors** - Use trycatch for risky operations
4. **Validate inputs** - Use guard clauses (return component)
5. **Test incrementally** - Test stages individually first
6. **Version pipelines** - Use semantic versioning
7. **Document** - Clear descriptions for stages
