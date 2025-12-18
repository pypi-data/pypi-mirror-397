# Project 11: Advanced Patterns

Test complex real-world scenarios combining multiple features.

## Purpose
Test sophisticated pipeline patterns:
- Multi-stage content pipelines
- ETL workflows
- Nested control flow
- Pipeline inheritance
- Dynamic routing

## Time Required
~1.5 hours

## Prerequisites
- Studio running
- All providers configured
- Child pipelines saved (for subpipeline tests)

## Test Scenarios

### 11.1 Multi-Stage Content Pipeline
```
Generate → Critique → Improve → Synthesize → Validate
```
Tests: Data flow between AI stages, iterative improvement

### 11.2 ETL Workflow
```
HTTP Fetch → Transform → Validate → Filter → Output
```
Tests: External data, transformation, validation, filtering

### 11.3 Nested Control Flow
```
ForEach {
  TryCatch {
    try: Process
    catch: Handle error
    finally: Log
  }
  Conditional {
    true: Approve
    false: Reject
  }
}
```
Tests: Complex nesting, error handling in loops

### 11.4 Pipeline Inheritance
Base pipeline + child overrides

### 11.5 Dynamic Routing
Route based on data values at runtime
