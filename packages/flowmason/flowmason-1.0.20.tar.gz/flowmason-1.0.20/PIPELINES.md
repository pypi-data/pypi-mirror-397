# FlowMason Pipeline Generation Guide

This document provides AI assistants with the context needed to generate valid FlowMason pipelines.

## Pipeline JSON Structure

```json
{
  "name": "Pipeline Name",
  "version": "1.0.0",
  "description": "What this pipeline does",
  "input_schema": {
    "type": "object",
    "properties": {
      "input_name": {
        "type": "string",
        "description": "Description of this input",
        "default": "optional default value"
      }
    },
    "required": ["input_name"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "output_name": { "type": "string" }
    }
  },
  "stages": [
    {
      "id": "unique-stage-id",
      "name": "Human Readable Name",
      "component_type": "component_name",
      "config": {
        "param1": "value1",
        "param2": "{{input.input_name}}"
      },
      "depends_on": [],
      "position": { "x": 100, "y": 200 }
    }
  ],
  "output_stage_id": "final-stage-id"
}
```

## Template Syntax

FlowMason uses `{{...}}` template syntax for dynamic values:

| Pattern | Description | Example |
|---------|-------------|---------|
| `{{input.field}}` | Pipeline input value | `{{input.customer_id}}` |
| `{{upstream.stage-id.result}}` | Result from upstream stage | `{{upstream.transform.result}}` |
| `{{upstream.stage-id.field}}` | Specific field from upstream | `{{upstream.validate.valid}}` |
| `{{context.var}}` | Context variable (in loops) | `{{context.current_item}}` |
| `{{env.VAR}}` | Environment variable | `{{env.API_KEY}}` |

## Available Components

### Core Operators

#### logger
Log messages during pipeline execution.
```json
{
  "component_type": "logger",
  "config": {
    "message": "Processing started",
    "level": "info",
    "data": { "count": "{{input.items}}" }
  }
}
```
- `message` (string): Log message
- `level` (string): "debug", "info", "warning", "error"
- `data` (any): Additional data to log

#### json_transform
Transform data using JMESPath expressions.
```json
{
  "component_type": "json_transform",
  "config": {
    "data": "{{upstream.fetch-data.result}}",
    "jmespath_expression": "items[*].{id: id, name: name, total: price * quantity}"
  }
}
```
- `data` (any): Input data to transform
- `jmespath_expression` (string): JMESPath query ([jmespath.org](https://jmespath.org))

#### filter
Filter data based on conditions.
```json
{
  "component_type": "filter",
  "config": {
    "data": "{{upstream.transform.result}}",
    "condition": "item.get('status') == 'active'",
    "filter_mode": "filter_array"
  }
}
```
- `data` (any): Data to filter
- `condition` (string): Python expression
  - In `filter_array` mode: use `item` variable
  - In `pass_fail` mode: use `data` variable
- `filter_mode` (string): "filter_array" or "pass_fail"
- `invert` (boolean): Invert the condition result

#### variable_set
Store a value in pipeline context.
```json
{
  "component_type": "variable_set",
  "config": {
    "name": "processed_count",
    "value": "{{upstream.filter.data}}",
    "scope": "pipeline"
  }
}
```
- `name` (string): Variable name
- `value` (any): Value to store
- `scope` (string): "pipeline" or "stage"

#### schema_validate
Validate data against a JSON Schema.
```json
{
  "component_type": "schema_validate",
  "config": {
    "data": "{{input.records}}",
    "json_schema": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "email"],
        "properties": {
          "id": { "type": "string" },
          "email": { "type": "string", "format": "email" }
        }
      }
    },
    "strict": false,
    "collect_all_errors": true
  }
}
```
- `data` (any): Data to validate
- `json_schema` (object): JSON Schema definition
- `strict` (boolean): Fail on additional properties
- `collect_all_errors` (boolean): Report all errors vs. first only

### Control Flow Operators

#### foreach
Iterate over items and execute stages for each.
```json
{
  "component_type": "foreach",
  "config": {
    "items": "{{input.records}}",
    "loop_stages": ["process-item", "validate-item"],
    "item_variable": "current_item",
    "index_variable": "item_index",
    "collect_results": true,
    "parallel": false
  }
}
```
- `items` (array): Items to iterate over
- `loop_stages` (array): Stage IDs to execute for each item
- `item_variable` (string): Variable name for current item (default: "current_item")
- `index_variable` (string): Variable name for index (default: "item_index")
- `collect_results` (boolean): Collect results from each iteration
- `parallel` (boolean): Execute iterations in parallel

**Inside loop stages, access:**
- `{{context.current_item}}` - Current item
- `{{context.item_index}}` - Current index (0-based)

#### conditional
Execute different branches based on conditions.
```json
{
  "component_type": "conditional",
  "config": {
    "condition": "{{upstream.check.result.score}} >= 80",
    "true_stages": ["high-score-path"],
    "false_stages": ["low-score-path"]
  }
}
```
- `condition` (string): Condition expression
- `true_stages` (array): Stages to run if condition is true
- `false_stages` (array): Stages to run if condition is false

#### router
Route to different stages based on value matching.
```json
{
  "component_type": "router",
  "config": {
    "value": "{{input.category}}",
    "routes": {
      "sales": ["process-sales"],
      "support": ["process-support"],
      "billing": ["process-billing"]
    },
    "default_route": ["process-other"]
  }
}
```
- `value` (string): Value to match
- `routes` (object): Map of value -> stage IDs
- `default_route` (array): Stages if no match

### HTTP Operators

#### http_request
Make HTTP API calls.
```json
{
  "component_type": "http_request",
  "config": {
    "url": "https://api.example.com/data",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer {{env.API_TOKEN}}",
      "Content-Type": "application/json"
    },
    "body": {
      "query": "{{input.search_term}}"
    },
    "timeout": 30
  }
}
```
- `url` (string): Request URL
- `method` (string): HTTP method (GET, POST, PUT, DELETE, etc.)
- `headers` (object): Request headers
- `body` (any): Request body (for POST/PUT)
- `timeout` (integer): Timeout in seconds

### AI/LLM Operators

#### generator
Generate content using an LLM.
```json
{
  "component_type": "generator",
  "config": {
    "prompt": "Summarize the following text:\n\n{{input.text}}",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```
- `prompt` (string): Prompt template
- `model` (string): Model name
- `temperature` (number): Randomness (0-1)
- `max_tokens` (integer): Max response length

#### critic
Evaluate content against criteria.
```json
{
  "component_type": "critic",
  "config": {
    "content": "{{upstream.generator.result}}",
    "criteria": [
      "Is the summary concise?",
      "Does it capture the main points?",
      "Is the language professional?"
    ],
    "model": "gpt-4"
  }
}
```
- `content` (any): Content to evaluate
- `criteria` (array): Evaluation criteria
- `model` (string): Model for evaluation

#### selector
Select the best option from multiple candidates.
```json
{
  "component_type": "selector",
  "config": {
    "candidates": "{{upstream.generate-options.result}}",
    "selection_criteria": "Select the most concise and accurate response",
    "model": "gpt-4"
  }
}
```
- `candidates` (array): Options to choose from
- `selection_criteria` (string): How to select
- `model` (string): Model for selection

## Studio Features for Designing Pipelines

When building pipelines in FlowMason Studio, you can use several AI‑assisted tools:

- **Generate from prompt** (Generate page):
  - Describe the desired pipeline in natural language.
  - See the generated stages, what the AI understood (intent, actions, patterns), and whether it used the interpreter/ML or a fallback.
  - Rate the generated pipeline (thumbs up/down) to log feedback for future improvement.

- **Pipeline Builder (Enhanced)**:
  - Visual canvas for editing stages and dependencies.
  - JSON editor:
    - Edit pipeline JSON directly.
    - Validate JSON structure inline.
    - Auto‑fix common issues (dangling dependencies, foreach/conditional wiring, http_request defaults).
    - View a short JSON history and restore previous snapshots.
  - Stage configuration:
    - Configure component inputs and LLM settings.
    - “Analyze Stage” to get structural suggestions from the validator.
  - Pattern awareness:
    - Detects common patterns (foreach, validation+transform, http_ingest+send, conditional) and shows them as badges.
    - “Explain” button provides a human‑readable summary of the current pipeline structure.

## Pipeline Patterns

### Pattern 1: ETL (Extract, Transform, Load)
```json
{
  "stages": [
    {
      "id": "extract",
      "component_type": "http_request",
      "config": { "url": "{{input.source_url}}", "method": "GET" },
      "depends_on": []
    },
    {
      "id": "validate",
      "component_type": "schema_validate",
      "config": { "data": "{{upstream.extract.result}}" },
      "depends_on": ["extract"]
    },
    {
      "id": "transform",
      "component_type": "json_transform",
      "config": { "data": "{{upstream.validate.data}}" },
      "depends_on": ["validate"]
    },
    {
      "id": "filter",
      "component_type": "filter",
      "config": { "data": "{{upstream.transform.result}}" },
      "depends_on": ["transform"]
    }
  ]
}
```

### Pattern 2: Batch Processing with Foreach
```json
{
  "stages": [
    {
      "id": "process-items",
      "component_type": "foreach",
      "config": {
        "items": "{{input.items}}",
        "loop_stages": ["transform-item"],
        "item_variable": "item"
      },
      "depends_on": []
    },
    {
      "id": "transform-item",
      "component_type": "json_transform",
      "config": {
        "data": "{{context.item}}",
        "jmespath_expression": "{ id: id, processed: `true` }"
      },
      "depends_on": ["process-items"]
    },
    {
      "id": "aggregate",
      "component_type": "json_transform",
      "config": {
        "data": "{{upstream.process-items.results}}"
      },
      "depends_on": ["process-items"]
    }
  ]
}
```

### Pattern 3: Conditional Branching
```json
{
  "stages": [
    {
      "id": "check-type",
      "component_type": "router",
      "config": {
        "value": "{{input.request_type}}",
        "routes": {
          "urgent": ["handle-urgent"],
          "normal": ["handle-normal"]
        },
        "default_route": ["handle-other"]
      },
      "depends_on": []
    },
    {
      "id": "handle-urgent",
      "component_type": "logger",
      "config": { "message": "Urgent request", "level": "warning" },
      "depends_on": ["check-type"]
    },
    {
      "id": "handle-normal",
      "component_type": "logger",
      "config": { "message": "Normal request", "level": "info" },
      "depends_on": ["check-type"]
    }
  ]
}
```

### Pattern 4: AI Content Generation with Review
```json
{
  "stages": [
    {
      "id": "generate",
      "component_type": "generator",
      "config": {
        "prompt": "Write a blog post about {{input.topic}}"
      },
      "depends_on": []
    },
    {
      "id": "review",
      "component_type": "critic",
      "config": {
        "content": "{{upstream.generate.result}}",
        "criteria": ["Accuracy", "Engagement", "SEO"]
      },
      "depends_on": ["generate"]
    },
    {
      "id": "decide",
      "component_type": "conditional",
      "config": {
        "condition": "{{upstream.review.result.score}} >= 0.8",
        "true_stages": ["publish"],
        "false_stages": ["revise"]
      },
      "depends_on": ["review"]
    }
  ]
}
```

## Stage Dependencies

- `depends_on: []` - Stage runs first (entry point)
- `depends_on: ["stage-a"]` - Runs after stage-a completes
- `depends_on: ["stage-a", "stage-b"]` - Runs after both complete (parallel join)

Multiple stages can depend on the same upstream stage (fan-out).
A stage can depend on multiple stages (fan-in/join).

## Best Practices

1. **Use descriptive stage IDs**: `validate-user-input` not `stage1`
2. **Always set `depends_on`**: Even if empty array for entry points
3. **Use `output_stage_id`**: Specify which stage produces the final output
4. **Template everything**: Use `{{input.*}}` and `{{upstream.*}}` for dynamic values
5. **Validate early**: Put schema_validate near the start of pipelines
6. **Log key milestones**: Add logger stages at important checkpoints
7. **Handle errors**: Use conditional stages for error handling paths

## Example: Complete Pipeline

```json
{
  "name": "Customer Data Processing",
  "version": "1.0.0",
  "description": "Validates, transforms, and categorizes customer records",
  "input_schema": {
    "type": "object",
    "properties": {
      "customers": {
        "type": "array",
        "description": "Array of customer records",
        "items": {
          "type": "object",
          "properties": {
            "id": { "type": "string" },
            "email": { "type": "string" },
            "spend": { "type": "number" }
          }
        }
      },
      "vip_threshold": {
        "type": "number",
        "description": "Spend threshold for VIP status",
        "default": 1000
      }
    },
    "required": ["customers"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "vip_customers": { "type": "array" },
      "regular_customers": { "type": "array" },
      "summary": { "type": "object" }
    }
  },
  "stages": [
    {
      "id": "log-start",
      "name": "Log Processing Start",
      "component_type": "logger",
      "config": {
        "message": "Starting customer processing",
        "level": "info",
        "data": { "count": "{{input.customers}}" }
      },
      "depends_on": [],
      "position": { "x": 100, "y": 200 }
    },
    {
      "id": "validate",
      "name": "Validate Customer Data",
      "component_type": "schema_validate",
      "config": {
        "data": "{{input.customers}}",
        "json_schema": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "email"],
            "properties": {
              "id": { "type": "string", "minLength": 1 },
              "email": { "type": "string", "format": "email" },
              "spend": { "type": "number", "minimum": 0 }
            }
          }
        }
      },
      "depends_on": ["log-start"],
      "position": { "x": 300, "y": 200 }
    },
    {
      "id": "transform",
      "name": "Normalize Customer Records",
      "component_type": "json_transform",
      "config": {
        "data": {
          "customers": "{{upstream.validate.data}}",
          "threshold": "{{input.vip_threshold}}"
        },
        "jmespath_expression": "customers[*].{ id: id, email: email, spend: spend || `0`, is_vip: spend >= threshold }"
      },
      "depends_on": ["validate"],
      "position": { "x": 500, "y": 200 }
    },
    {
      "id": "filter-vip",
      "name": "Filter VIP Customers",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.transform.result}}",
        "condition": "item.get('is_vip') == True",
        "filter_mode": "filter_array"
      },
      "depends_on": ["transform"],
      "position": { "x": 700, "y": 100 }
    },
    {
      "id": "filter-regular",
      "name": "Filter Regular Customers",
      "component_type": "filter",
      "config": {
        "data": "{{upstream.transform.result}}",
        "condition": "item.get('is_vip') == False",
        "filter_mode": "filter_array"
      },
      "depends_on": ["transform"],
      "position": { "x": 700, "y": 300 }
    },
    {
      "id": "create-summary",
      "name": "Create Summary",
      "component_type": "json_transform",
      "config": {
        "data": {
          "all": "{{upstream.transform.result}}",
          "vip": "{{upstream.filter-vip.data}}",
          "regular": "{{upstream.filter-regular.data}}"
        },
        "jmespath_expression": "{ total: length(all), vip_count: length(vip), regular_count: length(regular), vip_customers: vip, regular_customers: regular }"
      },
      "depends_on": ["filter-vip", "filter-regular"],
      "position": { "x": 900, "y": 200 }
    },
    {
      "id": "log-complete",
      "name": "Log Processing Complete",
      "component_type": "logger",
      "config": {
        "message": "Customer processing complete",
        "level": "info",
        "data": "{{upstream.create-summary.result}}"
      },
      "depends_on": ["create-summary"],
      "position": { "x": 1100, "y": 200 }
    }
  ],
  "output_stage_id": "create-summary"
}
```

## Prompting Tips for AI

When asking an AI to generate a pipeline:

1. **Describe the goal**: "Create a pipeline that processes customer orders and identifies high-value customers"
2. **Specify inputs**: "The input is an array of order objects with customer_id, amount, and date fields"
3. **Describe transformations**: "Filter orders over $100, group by customer, calculate total spend"
4. **Mention desired output**: "Output should include a list of VIP customers and a summary"

Example prompt:
```
Create a FlowMason pipeline that:
- Takes an array of product reviews as input
- Validates each review has 'text' and 'rating' fields
- Filters to only 4-5 star reviews
- Uses AI to summarize the positive feedback themes
- Outputs the summary and count of reviews processed
```
