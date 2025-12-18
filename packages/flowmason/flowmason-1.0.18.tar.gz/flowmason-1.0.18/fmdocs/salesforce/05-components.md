# Components

Flowmason provides a library of pre-built components for building AI pipelines.

## AI Components (Nodes)

### generator

Generate text using an LLM provider.

```json
{
  "id": "generate",
  "component_type": "generator",
  "config": {
    "system_prompt": "You are a helpful assistant.",
    "prompt": "Write a summary of: {{input.text}}",
    "max_tokens": 500,
    "temperature": 0.7
  },
  "depends_on": []
}
```

**Config Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `system_prompt` | string | - | System message for the LLM |
| `prompt` | string | Required | User prompt (supports templates) |
| `max_tokens` | integer | 1024 | Maximum tokens to generate |
| `temperature` | number | 0.7 | Creativity (0.0-1.0) |
| `provider` | string | default | Provider name from LLMProviderConfig__mdt |

**Output**:
```json
{
  "content": "Generated text...",
  "prompt": "Original prompt...",
  "generated": "Generated text..."
}
```

**Access**: `{{upstream.generate.content}}`

---

### critic

Evaluate content with structured feedback.

```json
{
  "id": "critique",
  "component_type": "critic",
  "config": {
    "system_prompt": "You are a writing critic. Evaluate the text and provide feedback.",
    "prompt": "Critique this content:\n\n{{input.content}}",
    "max_tokens": 500,
    "temperature": 0.4
  },
  "depends_on": []
}
```

**Use Cases**:
- Content quality evaluation
- Code review automation
- Editorial feedback

---

## Data Operators

### json_transform

Transform data using JMESPath expressions.

```json
{
  "id": "transform",
  "component_type": "json_transform",
  "config": {
    "data": "{{upstream.fetch.body}}",
    "jmespath_expression": "{ name: user.name, email: user.email, active: status == 'active' }"
  },
  "depends_on": ["fetch"]
}
```

**Config Options**:

| Option | Type | Description |
|--------|------|-------------|
| `data` | any | Input data (template or object) |
| `jmespath_expression` | string | JMESPath transformation |

**Common JMESPath Examples**:

```
# Extract fields
{ id: id, name: name }

# Filter arrays
[?status == 'active']

# Array operations
length(items)
items[0:5]

# Nested access
user.profile.email

# Conditional
status == 'ok' && `true` || `false`
```

**Output**: `{{upstream.transform.result}}`

---

### filter

Filter arrays based on conditions.

```json
{
  "id": "filter-active",
  "component_type": "filter",
  "config": {
    "data": "{{input.users}}",
    "condition": "item.status == 'active'"
  },
  "depends_on": []
}
```

**Config Options**:

| Option | Type | Description |
|--------|------|-------------|
| `data` | array | Input array to filter |
| `condition` | string | Filter condition (uses `item` variable) |

---

### schema_validate

Validate data against a JSON Schema.

```json
{
  "id": "validate",
  "component_type": "schema_validate",
  "config": {
    "data": "{{input.payload}}",
    "schema": {
      "type": "object",
      "properties": {
        "email": { "type": "string", "format": "email" },
        "age": { "type": "integer", "minimum": 0 }
      },
      "required": ["email"]
    }
  },
  "depends_on": []
}
```

**Output**:
```json
{
  "valid": true,
  "errors": []
}
```

---

### variable_set

Set context variables for later stages.

```json
{
  "id": "set-vars",
  "component_type": "variable_set",
  "config": {
    "variables": {
      "processed_count": "{{upstream.process.result.count}}",
      "status": "completed"
    }
  },
  "depends_on": ["process"]
}
```

---

## Flow Controls

### conditional

Execute different branches based on conditions.

```json
{
  "id": "check-vip",
  "component_type": "conditional",
  "config": {
    "condition": "{{input.customer_data.lifetime_value}}",
    "condition_expression": "value >= 1000",
    "true_branch_stages": ["vip-treatment"],
    "false_branch_stages": ["standard-treatment"]
  },
  "depends_on": []
}
```

**Config Options**:

| Option | Type | Description |
|--------|------|-------------|
| `condition` | any | Value to evaluate |
| `condition_expression` | string | Expression using `value` variable |
| `true_branch_stages` | array | Stages to execute if true |
| `false_branch_stages` | array | Stages to execute if false |

---

### router

Route to different stages based on values.

```json
{
  "id": "route-request",
  "component_type": "router",
  "config": {
    "value": "{{input.request_type}}",
    "routes": {
      "order": ["process-order"],
      "refund": ["process-refund", "notify-finance"],
      "complaint": ["process-complaint", "escalate-check"]
    },
    "default_route": ["process-inquiry"]
  },
  "depends_on": []
}
```

**Config Options**:

| Option | Type | Description |
|--------|------|-------------|
| `value` | string | Value to route on |
| `routes` | object | Map of values to stage arrays |
| `default_route` | array | Stages when no match found |

---

### foreach

Iterate over arrays with result collection.

```json
{
  "id": "process-items",
  "component_type": "foreach",
  "config": {
    "items": "{{input.items}}",
    "item_variable": "current_item",
    "loop_stages": ["transform-item", "validate-item"],
    "collect_results": true
  },
  "depends_on": []
}
```

**Config Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `items` | array | Required | Array to iterate over |
| `item_variable` | string | `item` | Variable name for current item |
| `loop_stages` | array | Required | Stages to execute per item |
| `collect_results` | boolean | false | Collect results into array |

**Context Variables in Loop**:
- `{{context.current_item}}` - Current item
- `{{context.item_index}}` - Current index (0-based)

---

### trycatch

Handle errors with fallback behavior.

```json
{
  "id": "safe-process",
  "component_type": "trycatch",
  "config": {
    "try_stages": ["risky-operation"],
    "catch_stages": ["fallback-operation"],
    "error_variable": "last_error"
  },
  "depends_on": []
}
```

**Config Options**:

| Option | Type | Description |
|--------|------|-------------|
| `try_stages` | array | Stages to attempt |
| `catch_stages` | array | Stages to execute on error |
| `error_variable` | string | Variable name for error message |

---

## Utilities

### http_request

Make HTTP requests to external APIs.

```json
{
  "id": "fetch-user",
  "component_type": "http_request",
  "config": {
    "url": "https://api.example.com/users/{{input.user_id}}",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer {{input.api_key}}",
      "Accept": "application/json"
    },
    "timeout": 30
  },
  "depends_on": []
}
```

**Config Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url` | string | Required | Request URL (supports templates) |
| `method` | string | GET | HTTP method |
| `headers` | object | {} | Request headers |
| `body` | any | - | Request body (for POST/PUT) |
| `params` | object | {} | Query parameters |
| `timeout` | integer | 30 | Timeout in seconds |

**Output**:
```json
{
  "status_code": 200,
  "body": { ... },
  "headers": { ... }
}
```

**Note**: Requires Remote Site Settings in Salesforce for external endpoints.

---

### logger

Log messages for debugging.

```json
{
  "id": "log-result",
  "component_type": "logger",
  "config": {
    "message": "Processing complete",
    "level": "info",
    "data": "{{upstream.process.result}}",
    "tags": {
      "pipeline": "support-triage",
      "stage": "final"
    }
  },
  "depends_on": ["process"]
}
```

**Config Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `message` | string | Required | Log message |
| `level` | string | info | Log level (debug, info, warn, error) |
| `data` | any | - | Data to include in log |
| `tags` | object | {} | Metadata tags |

---

## Component Availability

| Component | AI Required | Governor Impact |
|-----------|-------------|-----------------|
| generator | Yes | 1 callout per call |
| critic | Yes | 1 callout per call |
| json_transform | No | CPU only |
| filter | No | CPU only |
| schema_validate | No | CPU only |
| variable_set | No | Minimal |
| conditional | No | Minimal |
| router | No | Minimal |
| foreach | No | Multiplied by items |
| trycatch | No | Minimal |
| http_request | No | 1 callout per call |
| logger | No | Minimal |

## Next Steps

- [Execution](06-execution.md) - Sync and async execution
- [Examples](09-examples.md) - Complete pipeline examples
