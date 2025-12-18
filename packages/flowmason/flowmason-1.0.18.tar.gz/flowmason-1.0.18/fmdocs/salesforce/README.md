# Flowmason for Salesforce

> AI Pipeline Orchestration Native to Your Salesforce Org

Flowmason for Salesforce brings the power of AI pipelines directly into your Salesforce environment as a managed package. Build, test, and deploy intelligent workflows that integrate seamlessly with your existing Salesforce data and processes.

## Key Features

- **Native Execution** - Runs entirely within Salesforce using Apex
- **AI Integration** - Connect to Claude, GPT, and other LLM providers
- **Governor-Aware** - Automatic handling of Salesforce limits
- **Local Development** - Test pipelines locally, deploy JSON to Salesforce
- **Real-Time Status** - Platform Events for async execution monitoring

## Quick Start

```apex
// Execute a pipeline synchronously
String pipelineJson = '{"name":"My Pipeline","stages":[...]}';
Map<String, Object> input = new Map<String, Object>{'message' => 'Hello'};

ExecutionResult result = PipelineRunner.execute(pipelineJson, input);

if (result.status == 'success') {
    System.debug('Output: ' + result.output);
}
```

## Documentation

| Document | Description |
|----------|-------------|
| [Installation](01-installation.md) | Install the managed package |
| [Getting Started](02-getting-started.md) | Your first pipeline in 5 minutes |
| [Development Workflow](03-development-workflow.md) | Local dev to production |
| [Pipeline Definition](04-pipeline-definition.md) | JSON structure reference |
| [Components](05-components.md) | Available component types |
| [Execution](06-execution.md) | Sync and async execution |
| [Providers](07-providers.md) | LLM provider configuration |
| [Integration Patterns](08-integration-patterns.md) | Triggers, LWC, Flows |
| [Examples](09-examples.md) | Complete pipeline examples |
| [API Reference](10-api-reference.md) | Public Apex API |

## Package Contents

### Global Classes (Public API)

| Class | Description |
|-------|-------------|
| `PipelineRunner` | Execute pipelines synchronously |
| `ExecutionResult` | Pipeline execution result |
| `ExecutionTrace` | Debugging and cost tracking |

### Custom Metadata Types

| Metadata Type | Description |
|---------------|-------------|
| `LLMProviderConfig__mdt` | LLM provider credentials |

### Platform Events

| Event | Description |
|-------|-------------|
| `PipelineStatus__e` | Real-time execution updates |

## Component Library

### AI Components (Nodes)
- `generator` - Generate text using LLM
- `critic` - Evaluate and critique content
- `classifier` - Classify input into categories

### Data Operators
- `json_transform` - JMESPath transformations
- `filter` - Filter arrays based on conditions
- `schema_validate` - Validate data against schemas
- `variable_set` - Set context variables

### Flow Controls
- `conditional` - If/else branching
- `router` - Value-based routing
- `foreach` - Iterate over collections
- `trycatch` - Error handling with fallbacks

### Utilities
- `http_request` - External API calls
- `logger` - Debug logging

## Sample Pipelines

The package includes 9 sample pipelines demonstrating various capabilities:

1. **Customer Support Triage** - AI classification + response generation
2. **Data Validation ETL** - Schema validation and transformation
3. **Multi-API Aggregator** - Parallel HTTP requests
4. **Content Generation** - Multi-format AI content
5. **Error Handling** - TryCatch with fallbacks
6. **Batch Processing** - ForEach iteration
7. **Conditional Workflow** - Dynamic routing
8. **Book Editor v1.0** - Complex AI editorial pipeline
9. **Book Editor v1.1** - Simplified AI editorial pipeline

## Requirements

- Salesforce Enterprise Edition or higher
- API Version 62.0+
- Remote Site Settings for LLM providers (Anthropic, OpenAI)
- Named Credentials recommended for production

## Support

- Documentation: [flowmason.dev/docs/salesforce](https://flowmason.dev/docs/salesforce)
- Issues: [github.com/flowmason/salesforce/issues](https://github.com/flowmason/salesforce/issues)
- Community: [discord.gg/flowmason](https://discord.gg/flowmason)

---

*Flowmason for Salesforce is currently in beta. Coming soon to AppExchange.*
