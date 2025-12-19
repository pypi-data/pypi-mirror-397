# @flowmason/sdk

TypeScript/JavaScript SDK for FlowMason pipeline orchestration.

## Installation

```bash
npm install @flowmason/sdk
# or
yarn add @flowmason/sdk
# or
pnpm add @flowmason/sdk
```

## Quick Start

```typescript
import { FlowMason } from '@flowmason/sdk';

const fm = new FlowMason({
  studioUrl: 'http://localhost:8999/api/v1',
  apiKey: 'your-api-key',
});

// Run a pipeline
const result = await fm.run('pipeline-id', { query: 'Hello, world!' });
console.log(result.output);
```

## Configuration

```typescript
const fm = new FlowMason({
  // Studio API URL (default: http://localhost:8999/api/v1)
  studioUrl: 'https://studio.example.com/api/v1',

  // API key for authentication
  apiKey: 'sk-...',

  // Organization ID for multi-tenant setups
  orgId: 'org-123',

  // Default timeout in milliseconds (default: 300000 = 5 min)
  timeout: 60000,

  // Custom headers
  headers: {
    'X-Custom-Header': 'value',
  },
});
```

### Environment Variables

```bash
FLOWMASON_API_KEY=your-api-key
FLOWMASON_ORG_ID=your-org-id
```

## Running Pipelines

### By ID

```typescript
const result = await fm.run('pipeline-id', {
  query: 'Hello, world!',
  options: { temperature: 0.7 },
});

if (result.success) {
  console.log('Output:', result.output);
} else {
  console.error('Error:', result.error);
}
```

### By Name (with Optional Version)

```typescript
// Latest version
const result = await fm.runByName('content-generator', { topic: 'AI' });

// Specific version
const result2 = await fm.runByName('content-generator@1.0.0', { topic: 'AI' });
```

### With Options

```typescript
const result = await fm.run('pipeline-id', { input: 'data' }, {
  // Trace ID for observability
  traceId: 'trace-123',

  // Timeout override
  timeout: 60000,

  // Callback URL for async notification
  callbackUrl: 'https://myapp.com/webhook',

  // Run asynchronously (returns immediately)
  async: true,
});
```

### Streaming Execution

```typescript
const result = await fm.runWithStream(
  'pipeline-id',
  { input: 'data' },
  {
    onStageStart: (stage) => {
      console.log(`Starting: ${stage.stageId}`);
    },
    onStageComplete: (stage) => {
      console.log(`Completed: ${stage.stageId}`);
      console.log(`Output:`, stage.output);
    },
    onStageError: (stage) => {
      console.error(`Failed: ${stage.stageId}`, stage.error);
    },
    onProgress: (progress) => {
      console.log(`Progress: ${progress.percentComplete}%`);
    },
    onComplete: (result) => {
      console.log('Pipeline complete!', result.output);
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
const initialResult = await fm.run('pipeline-id', { input: 'data' }, { async: true });
console.log('Run ID:', initialResult.runId);

// Wait for completion
const finalResult = await fm.waitForCompletion(initialResult.runId, {
  pollInterval: 2000, // Check every 2 seconds
  timeout: 300000,    // 5 minute timeout
});

console.log('Final output:', finalResult.output);
```

## Pipeline Management

### List Pipelines

```typescript
const { items: pipelines, total } = await fm.listPipelines({
  status: 'published',
  category: 'content',
  limit: 20,
  offset: 0,
});

for (const pipeline of pipelines) {
  console.log(`${pipeline.name} v${pipeline.version}`);
}
```

### Get Pipeline Details

```typescript
const pipeline = await fm.getPipeline('pipeline-id');
console.log('Stages:', pipeline.stages.length);
console.log('Input schema:', pipeline.inputSchema);
```

### Validate Pipeline

```typescript
const { valid, errors } = await fm.validatePipeline('pipeline-id', {
  query: 'test input',
});

if (!valid) {
  console.error('Validation errors:', errors);
}
```

## Run History

### List Runs

```typescript
const { items: runs } = await fm.listRuns({
  pipelineId: 'pipeline-id',
  status: 'completed',
  limit: 50,
});

for (const run of runs) {
  console.log(`${run.runId}: ${run.status} (${run.durationMs}ms)`);
}
```

### Get Run Details

```typescript
const run = await fm.getRun('run-id');
console.log('Status:', run.status);
console.log('Output:', run.output);
console.log('Usage:', run.usage);
```

### Cancel a Run

```typescript
await fm.cancelRun('run-id');
```

## Components

### List Components

```typescript
const { items: components } = await fm.listComponents({
  category: 'ai',
  kind: 'node',
});

for (const comp of components) {
  console.log(`${comp.componentType}: ${comp.description}`);
}
```

### Get Component Details

```typescript
const component = await fm.getComponent('generator');
console.log('Input schema:', component.inputSchema);
console.log('Requires LLM:', component.requiresLlm);
```

## Error Handling

```typescript
import { FlowMasonError } from '@flowmason/sdk';

try {
  const result = await fm.run('pipeline-id', { input: 'data' });
} catch (error) {
  if (error instanceof FlowMasonError) {
    console.error('FlowMason error:', error.message);
    console.error('Code:', error.code);
    console.error('Status:', error.status);
    console.error('Details:', error.details);
  } else {
    throw error;
  }
}
```

## TypeScript Types

```typescript
import type {
  FlowMasonConfig,
  Pipeline,
  PipelineResult,
  PipelineStage,
  Component,
  StageResult,
  UsageMetrics,
  RunOptions,
} from '@flowmason/sdk';
```

## Node.js Usage

```typescript
import { FlowMason } from '@flowmason/sdk';

async function main() {
  const fm = new FlowMason();

  const result = await fm.run('pipeline-id', { query: 'Hello' });
  console.log(result.output);
}

main().catch(console.error);
```

## Browser Usage

```html
<script type="module">
  import { FlowMason } from 'https://esm.sh/@flowmason/sdk';

  const fm = new FlowMason({
    studioUrl: 'https://studio.example.com/api/v1',
  });

  const result = await fm.run('pipeline-id', { query: 'Hello' });
  console.log(result.output);
</script>
```

## License

MIT
