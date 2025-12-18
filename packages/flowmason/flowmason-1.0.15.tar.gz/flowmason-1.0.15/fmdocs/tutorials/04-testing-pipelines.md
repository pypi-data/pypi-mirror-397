# Tutorial 4: Testing Pipelines

This tutorial covers writing and running tests for FlowMason pipelines using VSCode's Test Explorer.

## What You'll Learn

- Creating test files (`.test.json`)
- Writing assertions
- Using mocks
- Running tests from VSCode
- Viewing coverage reports

## Prerequisites

- Completed [Tutorial 2: Building Your First Pipeline](./02-building-first-pipeline.md)
- A pipeline to test
- Studio running

## Test File Format

FlowMason tests are defined in `.test.json` files alongside your pipelines.

### Basic Structure

Create `pipelines/content-summarizer.test.json`:

```json
{
  "name": "Content Summarizer Tests",
  "pipeline": "pipelines/content-summarizer.pipeline.json",
  "tests": [
    {
      "name": "summarizes valid URL",
      "input": {
        "url": "https://example.com/article",
        "max_length": 100
      },
      "assertions": [
        { "path": "output.summary", "type": "string" },
        { "path": "output.summary.length", "greaterThan": 0 }
      ]
    }
  ]
}
```

## Step 1: Create Your First Test

### Test Case Structure

```json
{
  "name": "descriptive test name",
  "input": { /* pipeline input */ },
  "assertions": [ /* what to verify */ ]
}
```

### Example: Happy Path Test

```json
{
  "name": "processes valid input successfully",
  "input": {
    "url": "https://httpbin.org/json"
  },
  "assertions": [
    { "path": "output.summary", "exists": true },
    { "path": "output.summary", "type": "string" },
    { "path": "output.source_url", "equals": "https://httpbin.org/json" }
  ]
}
```

### Example: Error Test

```json
{
  "name": "handles missing URL",
  "input": {},
  "expectError": "VALIDATION"
}
```

## Step 2: Assertion Types

### Equality

```json
{ "path": "output.status", "equals": "success" }
{ "path": "output.count", "equals": 42 }
{ "path": "output.enabled", "equals": true }
```

### Type Checks

```json
{ "path": "output.data", "type": "array" }
{ "path": "output.name", "type": "string" }
{ "path": "output.count", "type": "number" }
{ "path": "output.valid", "type": "boolean" }
{ "path": "output.config", "type": "object" }
```

### Comparisons

```json
{ "path": "output.score", "greaterThan": 0.5 }
{ "path": "output.score", "lessThan": 1.0 }
{ "path": "output.count", "greaterOrEqual": 10 }
{ "path": "output.count", "lessOrEqual": 100 }
```

### String Matching

```json
{ "path": "output.message", "contains": "success" }
{ "path": "output.email", "matches": "^[a-z]+@example\\.com$" }
{ "path": "output.url", "startsWith": "https://" }
{ "path": "output.filename", "endsWith": ".json" }
```

### Array Assertions

```json
{ "path": "output.items", "length": 5 }
{ "path": "output.items", "minLength": 1 }
{ "path": "output.items", "maxLength": 100 }
{ "path": "output.items", "contains": "apple" }
{ "path": "output.items", "notContains": "error" }
```

### Object Assertions

```json
{ "path": "output.data", "hasProperty": "id" }
{ "path": "output.data", "notHasProperty": "password" }
```

### Existence Checks

```json
{ "path": "output.result", "exists": true }
{ "path": "output.error", "exists": false }
{ "path": "output.value", "notNull": true }
```

### Deep Equality

```json
{
  "path": "output.config",
  "deepEquals": {
    "enabled": true,
    "mode": "production"
  }
}
```

### Custom Expressions

```json
{
  "path": "output",
  "expression": "data.length > 0 && data.every(item => item.valid)"
}
```

## Step 3: Stage-Level Testing

Test specific stages, not just final output:

```json
{
  "name": "fetch stage returns 200",
  "input": { "url": "https://httpbin.org/json" },
  "stageAssertions": {
    "fetch": [
      { "path": "output.status_code", "equals": 200 }
    ],
    "extract": [
      { "path": "output.result", "type": "object" }
    ]
  }
}
```

## Step 4: Using Mocks

### Mock HTTP Responses

Avoid hitting real APIs in tests:

```json
{
  "name": "handles API response",
  "mocks": {
    "http-request": {
      "output": {
        "status_code": 200,
        "body": {
          "content": "This is mock content for testing."
        }
      }
    }
  },
  "input": { "url": "https://example.com" },
  "assertions": [
    { "path": "output.summary", "contains": "mock content" }
  ]
}
```

### Mock LLM Responses

Control AI outputs for deterministic tests:

```json
{
  "name": "test summarization",
  "mocks": {
    "generator": {
      "output": {
        "content": "This is a mocked summary.",
        "usage": { "input_tokens": 100, "output_tokens": 20 }
      }
    }
  },
  "input": { "url": "https://example.com" },
  "assertions": [
    { "path": "output.summary", "equals": "This is a mocked summary." }
  ]
}
```

### Mock Multiple Components

```json
{
  "mocks": {
    "http-request": {
      "output": { "status_code": 200, "body": "..." }
    },
    "generator": {
      "output": { "content": "..." }
    },
    "json-transform": {
      "output": { "result": {...} }
    }
  }
}
```

## Step 5: Setup and Teardown

### Global Setup

```json
{
  "name": "API Integration Tests",
  "pipeline": "pipelines/api.pipeline.json",
  "setup": {
    "variables": {
      "API_URL": "https://test.api.example.com",
      "AUTH_TOKEN": "test-token-123"
    }
  },
  "teardown": {
    "cleanup": ["temp_files"]
  },
  "tests": [...]
}
```

### Per-Test Setup

```json
{
  "tests": [
    {
      "name": "with verbose mode",
      "setup": {
        "variables": { "LOG_LEVEL": "debug" }
      },
      "input": {...},
      "assertions": [...]
    }
  ]
}
```

## Step 6: Error Testing

### Expected Error Type

```json
{
  "name": "rejects invalid URL",
  "input": { "url": "not-a-url" },
  "expectError": "VALIDATION"
}
```

### Error Types

| Type | Description |
|------|-------------|
| `VALIDATION` | Input validation failed |
| `COMPONENT` | Component execution error |
| `PROVIDER` | LLM provider error |
| `TIMEOUT` | Execution timed out |
| `CONNECTIVITY` | Network/connection error |
| `CONFIGURATION` | Configuration error |

### Error Message Check

```json
{
  "name": "error message includes details",
  "input": {},
  "expectError": "VALIDATION",
  "errorContains": "url is required"
}
```

## Step 7: Running Tests

### From VSCode Test Explorer

1. Open Test Explorer (`View > Testing`)
2. Your test files appear in the tree
3. Click "Run" on a test suite or individual test
4. View results inline

```
TEST EXPLORER
├── ▼ content-summarizer.test.json
│   ├── ✓ summarizes valid URL (1.2s)
│   ├── ✓ handles missing URL (0.1s)
│   ├── ✓ handles API error (0.3s)
│   └── ✗ handles long content (timeout)
```

### From Command Line

```bash
# Run all tests
fm test

# Run specific test file
fm test pipelines/content-summarizer.test.json

# Run tests matching pattern
fm test --filter "valid URL"

# Run with verbose output
fm test --verbose

# Run with coverage
fm test --coverage
```

### From Context Menu

1. Right-click on a `.test.json` file
2. Select "FlowMason: Run Tests"

### Keyboard Shortcut

- `Cmd+; A` - Run all tests
- `Cmd+; F` - Run tests in current file
- `Cmd+; L` - Run last test

## Step 8: Test Coverage

### Enable Coverage

```bash
fm test --coverage
```

### Coverage Report

```
Coverage Report
───────────────────────────────────────
Pipeline                    Coverage
───────────────────────────────────────
content-summarizer.pipeline.json    85%
  ├── fetch                     100%
  ├── extract                   100%
  ├── summarize                  75%
  └── output                     66%
───────────────────────────────────────
Total                           85%
```

### Coverage in VSCode

- Test Explorer shows per-file coverage
- Editor gutters show covered/uncovered stages (future feature)

## Step 9: Snapshot Testing

Compare output against saved snapshots:

```json
{
  "name": "output matches snapshot",
  "input": { "url": "https://example.com" },
  "snapshot": "tests/snapshots/summarizer-output.json"
}
```

### Update Snapshots

When expected output changes:

```bash
fm test --update-snapshots
```

## Complete Test File Example

`pipelines/content-summarizer.test.json`:

```json
{
  "name": "Content Summarizer Tests",
  "pipeline": "pipelines/content-summarizer.pipeline.json",
  "setup": {
    "variables": {
      "TEST_MODE": "true"
    }
  },
  "tests": [
    {
      "name": "summarizes valid URL",
      "mocks": {
        "http-request": {
          "output": {
            "status_code": 200,
            "body": { "content": "The quick brown fox jumps over the lazy dog. This is a test article about animals and their behaviors." }
          }
        },
        "generator": {
          "output": {
            "content": "An article about animal behavior, specifically foxes and dogs.",
            "usage": { "input_tokens": 50, "output_tokens": 15 }
          }
        }
      },
      "input": {
        "url": "https://example.com/article",
        "max_length": 100
      },
      "assertions": [
        { "path": "output.summary", "type": "string" },
        { "path": "output.summary.length", "greaterThan": 0 },
        { "path": "output.source_url", "equals": "https://example.com/article" }
      ],
      "stageAssertions": {
        "fetch": [
          { "path": "output.status_code", "equals": 200 }
        ]
      }
    },
    {
      "name": "handles missing URL",
      "input": {},
      "expectError": "VALIDATION",
      "errorContains": "url"
    },
    {
      "name": "handles API error gracefully",
      "mocks": {
        "http-request": {
          "error": {
            "type": "CONNECTIVITY",
            "message": "Connection refused"
          }
        }
      },
      "input": {
        "url": "https://invalid.example.com"
      },
      "expectError": "CONNECTIVITY"
    },
    {
      "name": "respects max_length parameter",
      "skip": false,
      "timeout": 30000,
      "mocks": {
        "http-request": {
          "output": {
            "status_code": 200,
            "body": { "content": "Long content here..." }
          }
        },
        "generator": {
          "output": {
            "content": "Short summary.",
            "usage": { "input_tokens": 100, "output_tokens": 5 }
          }
        }
      },
      "input": {
        "url": "https://example.com/long-article",
        "max_length": 50
      },
      "assertions": [
        { "path": "output.summary", "type": "string" }
      ]
    }
  ]
}
```

## Best Practices

### 1. Test the Happy Path

Always have a test for successful execution:

```json
{
  "name": "processes valid input",
  "input": { /* valid input */ },
  "assertions": [ /* verify success */ ]
}
```

### 2. Test Error Cases

```json
{
  "name": "handles empty input",
  "input": {},
  "expectError": "VALIDATION"
}
```

### 3. Use Mocks for External Services

Don't hit real APIs in tests:

```json
{
  "mocks": {
    "http-request": { "output": {...} }
  }
}
```

### 4. Test Individual Stages

Use `stageAssertions` for granular testing:

```json
{
  "stageAssertions": {
    "fetch": [...],
    "transform": [...]
  }
}
```

### 5. Keep Tests Fast

Use mocks and avoid timeouts:

```json
{
  "timeout": 5000,
  "mocks": {...}
}
```

### 6. Use Descriptive Names

```json
// Good
"name": "returns error when URL is malformed"

// Bad
"name": "test 1"
```

### 7. Aim for 80%+ Coverage

```bash
fm test --coverage
```

## CI/CD Integration

### GitHub Actions

```yaml
name: FlowMason Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup FlowMason
        run: |
          pip install flowmason flowmason-studio

      - name: Run Tests
        run: fm test --coverage --reporter json > results.json

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
```

## Next Steps

- [Tutorial 5: Working with Components](./05-working-with-components.md) - Create custom nodes and operators
