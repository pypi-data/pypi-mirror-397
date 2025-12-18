# Testing Pipelines

FlowMason provides a comprehensive testing framework integrated with VSCode's Test Explorer.

## Quick Start

1. Create a `.test.json` file next to your pipeline
2. Define test cases with inputs and assertions
3. Run from Test Explorer or command line

## Test File Format

Create `pipelines/main.test.json`:

```json
{
  "name": "Main Pipeline Tests",
  "pipeline": "pipelines/main.pipeline.json",
  "tests": [
    {
      "name": "processes valid input",
      "input": {
        "url": "https://api.example.com/data"
      },
      "assertions": [
        { "path": "output.success", "equals": true },
        { "path": "output.data", "type": "array" }
      ]
    },
    {
      "name": "handles missing URL",
      "input": {},
      "expectError": "VALIDATION"
    }
  ]
}
```

## Test Structure

### Test File

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Test suite name |
| `pipeline` | string | Yes | Path to pipeline file |
| `setup` | object | No | Setup before all tests |
| `teardown` | object | No | Cleanup after all tests |
| `tests` | array | Yes | Test cases |

### Test Case

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `name` | string | Yes | Test case name |
| `input` | object | Yes | Pipeline input data |
| `assertions` | array | No* | Output assertions |
| `expectError` | string | No* | Expected error type |
| `timeout` | number | No | Test timeout (ms) |
| `skip` | boolean | No | Skip this test |

*Either `assertions` or `expectError` required.

## Assertions

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

### Null/Undefined

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
    "mode": "production",
    "features": ["a", "b"]
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

## Stage-Level Testing

Test specific stages, not just final output:

```json
{
  "tests": [
    {
      "name": "fetch stage returns data",
      "input": { "url": "https://api.example.com" },
      "stageAssertions": {
        "fetch": [
          { "path": "output.status_code", "equals": 200 }
        ],
        "transform": [
          { "path": "output.result", "type": "array" }
        ]
      }
    }
  ]
}
```

## Error Testing

### Expected Error Type

```json
{
  "name": "rejects invalid input",
  "input": { "url": "not-a-url" },
  "expectError": "VALIDATION"
}
```

Error types: `VALIDATION`, `COMPONENT`, `PROVIDER`, `TIMEOUT`, `CONNECTIVITY`, `CONFIGURATION`

### Expected Error Message

```json
{
  "name": "error message check",
  "input": {},
  "expectError": "VALIDATION",
  "errorContains": "url is required"
}
```

## Setup and Teardown

### Global Setup

```json
{
  "name": "API Tests",
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
      "name": "with custom setup",
      "setup": {
        "variables": { "MODE": "verbose" }
      },
      "input": { ... },
      "assertions": [...]
    }
  ]
}
```

## Running Tests

### From VSCode

1. Open Test Explorer (View > Testing)
2. Click Run button on test suite or individual test
3. View results inline

### From Command Line

```bash
# Run all tests
fm test

# Run specific test file
fm test pipelines/main.test.json

# Run tests matching pattern
fm test --filter "valid input"

# Run with coverage
fm test --coverage
```

### From API

```bash
curl -X POST http://localhost:8999/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{
    "test_file": "pipelines/main.test.json"
  }'
```

## Test Coverage

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
pipelines/main.pipeline.json    85%
  ├── fetch                     100%
  ├── transform                 100%
  ├── validate                  75%
  └── output                    66%
───────────────────────────────────────
Total                           85%
```

### Coverage in VSCode

- Gutters show covered/uncovered lines
- Test Explorer shows per-file coverage
- Coverage panel shows summary

## Mocking

### Mock HTTP Responses

```json
{
  "tests": [
    {
      "name": "handles API response",
      "mocks": {
        "http-request": {
          "output": {
            "status_code": 200,
            "body": { "data": [1, 2, 3] }
          }
        }
      },
      "input": { "url": "https://api.example.com" },
      "assertions": [...]
    }
  ]
}
```

### Mock LLM Responses

```json
{
  "tests": [
    {
      "name": "test prompt handling",
      "mocks": {
        "generator": {
          "output": {
            "content": "Mocked response text",
            "usage": { "input_tokens": 10, "output_tokens": 20 }
          }
        }
      },
      "input": { "topic": "test" },
      "assertions": [...]
    }
  ]
}
```

## Snapshot Testing

Compare output against saved snapshots:

```json
{
  "tests": [
    {
      "name": "output matches snapshot",
      "input": { "url": "https://api.example.com" },
      "snapshot": "tests/snapshots/api-response.json"
    }
  ]
}
```

### Update Snapshots

```bash
fm test --update-snapshots
```

## Best Practices

1. **Test the Happy Path**: Always test successful execution
2. **Test Error Cases**: Verify error handling works
3. **Use Mocks**: Mock external services for reliability
4. **Test Stages**: Don't just test final output
5. **Keep Tests Fast**: Use mocks for slow operations
6. **Descriptive Names**: Make test names explain the scenario
7. **Coverage Goals**: Aim for 80%+ coverage

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run FlowMason Tests
  run: |
    fm test --coverage --reporter json > test-results.json

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.json
```

### Test Results Format

```json
{
  "suite": "Main Pipeline Tests",
  "passed": 5,
  "failed": 1,
  "skipped": 0,
  "duration": 3450,
  "tests": [
    {
      "name": "processes valid input",
      "status": "passed",
      "duration": 1200
    },
    {
      "name": "handles edge case",
      "status": "failed",
      "error": "Expected 'success' but got 'error'",
      "duration": 450
    }
  ]
}
```

## See Also

- [Debugging](./debugging/current-debugging.md)
- [VSCode Extension](../07-vscode-extension/overview.md)
- [Pipelines](../03-concepts/pipelines.md)
