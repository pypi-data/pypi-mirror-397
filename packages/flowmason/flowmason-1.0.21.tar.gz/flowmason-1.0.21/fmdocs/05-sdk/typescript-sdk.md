# TypeScript SDK

FlowMason provides a TypeScript/JavaScript SDK for programmatic pipeline execution in Node.js and browser environments.

## Installation

```bash
npm install @flowmason/sdk
```

## Quick Start

```typescript
import { FlowMason } from '@flowmason/sdk';

const fm = new FlowMason({
  studioUrl: 'http://localhost:8999/api/v1',
  apiKey: process.env.FLOWMASON_API_KEY,
});

// Run a pipeline
const result = await fm.run('pipeline-id', {
  query: 'Hello, world!',
});

console.log(result.output);
```

## Configuration

### Options

```typescript
const fm = new FlowMason({
  // Studio API URL (default: http://localhost:8999/api/v1)
  studioUrl: 'https://studio.example.com/api/v1',

  // API key for authentication
  apiKey: 'sk-...',

  // Organization ID for multi-tenant setups
  orgId: 'org-123',

  // Default timeout in milliseconds (default: 300000)
  timeout: 60000,

  // Custom headers for all requests
  headers: {
    'X-Custom-Header': 'value',
  },

  // Custom fetch implementation (for special environments)
  fetch: customFetch,
});
```

### Environment Variables

The SDK automatically reads these environment variables:

| Variable | Description |
|----------|-------------|
| `FLOWMASON_API_KEY` | API key for authentication |
| `FLOWMASON_ORG_ID` | Organization ID |

## Running Pipelines

### Basic Execution

```typescript
const result = await fm.run('pipeline-id', {
  query: 'Generate content about AI',
  options: { temperature: 0.7 },
});

if (result.success) {
  console.log('Output:', result.output);
  console.log('Tokens used:', result.usage?.totalTokens);
  console.log('Cost:', result.usage?.totalCostUsd);
} else {
  console.error('Failed:', result.error);
}
```

### Run by Name

```typescript
// Latest version
const result = await fm.runByName('content-generator', { topic: 'AI' });

// Specific version
const result = await fm.runByName('content-generator@2.0.0', { topic: 'AI' });
```

### Run Options

```typescript
const result = await fm.run('pipeline-id', { input: 'data' }, {
  // Trace ID for observability
  traceId: 'trace-123',

  // Override timeout
  timeout: 120000,

  // Callback URL for completion notification
  callbackUrl: 'https://myapp.com/webhook/flowmason',

  // Run asynchronously (returns immediately with run ID)
  async: true,

  // Output routing configuration
  outputConfig: {
    destinations: [
      {
        type: 'webhook',
        config: { url: 'https://myapp.com/data' },
        onSuccess: true,
      },
    ],
  },
});
```

### Streaming Execution

Get real-time updates during pipeline execution:

```typescript
const result = await fm.runWithStream(
  'pipeline-id',
  { input: 'data' },
  {
    onStageStart: (stage) => {
      console.log(`Starting stage: ${stage.stageName || stage.stageId}`);
    },

    onStageComplete: (stage) => {
      console.log(`Completed: ${stage.stageId}`);
      console.log(`Duration: ${stage.durationMs}ms`);
    },

    onStageError: (stage) => {
      console.error(`Stage failed: ${stage.stageId}`);
      console.error(`Error: ${stage.error}`);
    },

    onProgress: (progress) => {
      console.log(`Progress: ${progress.percentComplete}%`);
      console.log(`Current: ${progress.currentStage}`);
    },

    onComplete: (result) => {
      console.log('Pipeline complete!');
      console.log('Output:', result.output);
    },

    onError: (error) => {
      console.error('Pipeline failed:', error.message);
    },
  }
);
```

### Async Execution with Polling

```typescript
// Start async run
const initialResult = await fm.run(
  'pipeline-id',
  { input: 'data' },
  { async: true }
);

console.log('Started run:', initialResult.runId);

// Poll for completion
const finalResult = await fm.waitForCompletion(initialResult.runId, {
  pollInterval: 2000,  // Check every 2 seconds
  timeout: 300000,     // 5 minute timeout
});

console.log('Completed:', finalResult.output);
```

### Cancel Execution

```typescript
// Cancel by run ID
await fm.cancelRun('run-id');

// Cancel current request
fm.cancel();
```

## Pipeline Management

### List Pipelines

```typescript
const { items, total, hasMore } = await fm.listPipelines({
  status: 'published',
  category: 'content',
  search: 'generator',
  limit: 20,
  offset: 0,
});

for (const pipeline of items) {
  console.log(`${pipeline.name} v${pipeline.version} - ${pipeline.status}`);
}
```

### Get Pipeline Details

```typescript
const pipeline = await fm.getPipeline('pipeline-id');

console.log('Name:', pipeline.name);
console.log('Description:', pipeline.description);
console.log('Stages:', pipeline.stages.length);
console.log('Input Schema:', JSON.stringify(pipeline.inputSchema, null, 2));
```

### Validate Pipeline

```typescript
const { valid, errors } = await fm.validatePipeline('pipeline-id', {
  query: 'test input',
});

if (!valid) {
  console.error('Validation errors:');
  for (const error of errors) {
    console.error(`  - ${error}`);
  }
}
```

## Run History

### List Runs

```typescript
const { items: runs } = await fm.listRuns({
  pipelineId: 'pipeline-id',
  status: 'completed',
  startDate: '2024-01-01',
  endDate: '2024-12-31',
  limit: 100,
});

for (const run of runs) {
  console.log(`${run.runId}: ${run.status} (${run.durationMs}ms)`);
}
```

### Get Run Details

```typescript
const run = await fm.getRun('run-id');

console.log('Status:', run.status);
console.log('Success:', run.success);
console.log('Output:', run.output);
console.log('Duration:', run.durationMs, 'ms');

// Stage results
for (const [stageId, stage] of Object.entries(run.stageResults)) {
  console.log(`  ${stageId}: ${stage.status}`);
}

// Usage metrics
if (run.usage) {
  console.log('Tokens:', run.usage.totalTokens);
  console.log('Cost: $', run.usage.totalCostUsd.toFixed(4));
}
```

### Get Run Logs

```typescript
const logs = await fm.getRunLogs('run-id');

for (const log of logs) {
  console.log(`[${log.timestamp}] ${log.level}: ${log.message}`);
}
```

## Component Registry

### List Components

```typescript
const { items: components } = await fm.listComponents({
  category: 'ai',
  kind: 'node',
});

for (const comp of components) {
  console.log(`${comp.componentType} (${comp.componentKind})`);
  console.log(`  ${comp.description}`);
  console.log(`  Requires LLM: ${comp.requiresLlm}`);
}
```

### Get Component Details

```typescript
const component = await fm.getComponent('generator');

console.log('Name:', component.name);
console.log('Category:', component.category);
console.log('Version:', component.version);
console.log('Input Schema:', component.inputSchema);
console.log('Output Schema:', component.outputSchema);
```

### List Categories

```typescript
const categories = await fm.listCategories();
console.log('Categories:', categories);
// ['ai', 'utility', 'control_flow', 'integration']
```

## Error Handling

```typescript
import { FlowMason, FlowMasonError } from '@flowmason/sdk';

try {
  const result = await fm.run('pipeline-id', { input: 'data' });
} catch (error) {
  if (error instanceof FlowMasonError) {
    console.error('FlowMason Error');
    console.error('  Message:', error.message);
    console.error('  Code:', error.code);
    console.error('  Status:', error.status);
    console.error('  Details:', error.details);

    switch (error.code) {
      case 'PIPELINE_NOT_FOUND':
        // Handle missing pipeline
        break;
      case 'VALIDATION_ERROR':
        // Handle invalid input
        break;
      case 'TIMEOUT':
        // Handle timeout
        break;
      case 'NETWORK_ERROR':
        // Handle network issues
        break;
    }
  } else {
    throw error;
  }
}
```

## TypeScript Types

Full TypeScript support with exported types:

```typescript
import type {
  FlowMasonConfig,
  Pipeline,
  PipelineResult,
  PipelineStage,
  PipelineStatus,
  Component,
  StageResult,
  StageStatus,
  UsageMetrics,
  RunOptions,
  RunStatus,
  StreamCallbacks,
  PaginatedResponse,
} from '@flowmason/sdk';

// Use in your code
function handleResult(result: PipelineResult) {
  if (result.success) {
    processOutput(result.output);
  }
}
```

## Advanced Usage

### Custom HTTP Client

```typescript
import { FlowMason } from '@flowmason/sdk';

// Use custom fetch (e.g., with retry logic)
const fm = new FlowMason({
  fetch: async (url, options) => {
    let lastError;
    for (let i = 0; i < 3; i++) {
      try {
        return await fetch(url, options);
      } catch (error) {
        lastError = error;
        await new Promise(r => setTimeout(r, 1000 * (i + 1)));
      }
    }
    throw lastError;
  },
});
```

### Batch Execution

```typescript
const pipelineIds = ['pipeline-1', 'pipeline-2', 'pipeline-3'];
const input = { query: 'Hello' };

const results = await Promise.all(
  pipelineIds.map(id => fm.run(id, input))
);

for (const result of results) {
  console.log(`${result.pipelineId}: ${result.success ? 'OK' : 'FAIL'}`);
}
```

### Rate Limiting

```typescript
import pLimit from 'p-limit';

const limit = pLimit(5); // Max 5 concurrent requests

const tasks = pipelines.map(id =>
  limit(() => fm.run(id, { input: 'data' }))
);

const results = await Promise.all(tasks);
```

## Health Check

```typescript
const health = await fm.health();
console.log('Status:', health.status);
console.log('Version:', health.version);

const info = await fm.info();
console.log('Server info:', info);
```
