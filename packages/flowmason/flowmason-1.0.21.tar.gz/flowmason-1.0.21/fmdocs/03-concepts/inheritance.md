# Pipeline Inheritance & Composition

Pipeline inheritance allows you to create reusable base pipelines that can be extended and customized by child pipelines. This promotes code reuse and standardization across your organization.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Base Pipeline (abstract)                                       │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                   │
│  │validate │────▶│transform│────▶│ output  │                   │
│  │         │     │(abstract)│     │         │                   │
│  └─────────┘     └─────────┘     └─────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ extends
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Customer ETL Pipeline                                          │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                   │
│  │validate │────▶│json_    │────▶│ output  │                   │
│  │(inherited)│   │transform│     │(inherited)│                  │
│  └─────────┘     └─────────┘     └─────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

## Creating a Base Pipeline

Base pipelines define the structure that child pipelines will inherit. Mark a pipeline as `abstract` if it shouldn't be executed directly.

```json
{
  "id": "base-etl",
  "name": "Base ETL Pipeline",
  "abstract": true,
  "stages": [
    {
      "id": "validate",
      "type": "schema_validate",
      "config": {
        "strict": true
      }
    },
    {
      "id": "transform",
      "type": "abstract"
    },
    {
      "id": "output",
      "type": "logger",
      "depends_on": ["transform"]
    }
  ]
}
```

## Extending a Pipeline

Use the `extends` field to inherit from a base pipeline and `overrides` to customize specific stages.

```json
{
  "id": "customer-etl",
  "name": "Customer ETL Pipeline",
  "extends": "base-etl",
  "overrides": {
    "transform": {
      "type": "json_transform",
      "config": {
        "mapping": {
          "customer_id": "{{input.id}}",
          "full_name": "{{input.first_name}} {{input.last_name}}"
        }
      }
    }
  }
}
```

## Python API

### InheritanceResolver

Resolves the complete pipeline configuration by merging parent and child configs.

```python
from flowmason_core.inheritance import InheritanceResolver

resolver = InheritanceResolver()

# Load pipeline with inheritance resolved
pipeline = resolver.resolve("customer-etl", pipeline_registry)

# Check inheritance chain
chain = resolver.get_inheritance_chain("customer-etl", pipeline_registry)
print(chain)  # ['base-etl', 'customer-etl']
```

### PipelineMerger

Merges parent and child pipeline configurations.

```python
from flowmason_core.inheritance import PipelineMerger

merger = PipelineMerger()

# Merge child overrides into parent
merged = merger.merge(parent_config, child_config)
```

### InheritanceValidator

Validates inheritance rules and detects issues.

```python
from flowmason_core.inheritance import InheritanceValidator

validator = InheritanceValidator()

# Validate inheritance configuration
result = validator.validate(pipeline_config, pipeline_registry)

if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

## Validation Rules

The inheritance system enforces several rules:

1. **No Circular Inheritance**: A pipeline cannot extend itself or create a cycle
2. **Abstract Stage Override**: Abstract stages must be overridden in child pipelines
3. **Type Compatibility**: Overridden stages must be compatible with the parent
4. **Dependency Preservation**: Stage dependencies must remain valid after inheritance

## CLI Commands

### Validate Inheritance

```bash
fm validate --check-inheritance customer-etl.pipeline.json
```

### Show Inheritance Chain

```bash
fm info --inheritance customer-etl.pipeline.json
```

## Best Practices

1. **Use Abstract Pipelines**: Mark base pipelines as `abstract` to prevent accidental execution
2. **Document Override Points**: Clearly document which stages are meant to be overridden
3. **Keep Inheritance Shallow**: Avoid deep inheritance chains (max 3 levels recommended)
4. **Version Base Pipelines**: Use semantic versioning for base pipelines

## Example: Multi-Environment ETL

```json
// base-etl.pipeline.json
{
  "id": "base-etl",
  "abstract": true,
  "stages": [
    { "id": "extract", "type": "abstract" },
    { "id": "validate", "type": "schema_validate" },
    { "id": "transform", "type": "abstract" },
    { "id": "load", "type": "abstract" }
  ]
}

// prod-etl.pipeline.json
{
  "id": "prod-etl",
  "extends": "base-etl",
  "overrides": {
    "extract": { "type": "http_request", "config": { "url": "https://api.prod.example.com" } },
    "transform": { "type": "json_transform", "config": { "mapping": {...} } },
    "load": { "type": "database_write", "config": { "connection": "prod-db" } }
  }
}

// dev-etl.pipeline.json
{
  "id": "dev-etl",
  "extends": "base-etl",
  "overrides": {
    "extract": { "type": "file_read", "config": { "path": "./test-data.json" } },
    "transform": { "type": "json_transform", "config": { "mapping": {...} } },
    "load": { "type": "logger", "config": { "level": "debug" } }
  }
}
```
