# @flowmason/react

React hooks for FlowMason pipeline orchestration.

## Installation

```bash
npm install @flowmason/react
# or
yarn add @flowmason/react
# or
pnpm add @flowmason/react
```

## Quick Start

```tsx
import { FlowMasonProvider, usePipeline } from '@flowmason/react';

function App() {
  return (
    <FlowMasonProvider config={{ studioUrl: 'http://localhost:8999/api/v1' }}>
      <MyComponent />
    </FlowMasonProvider>
  );
}

function MyComponent() {
  const { run, result, isRunning, error } = usePipeline('my-pipeline-id');

  const handleClick = async () => {
    await run({ query: 'Hello, world!' });
  };

  return (
    <div>
      <button onClick={handleClick} disabled={isRunning}>
        {isRunning ? 'Running...' : 'Run Pipeline'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && <pre>{JSON.stringify(result.output, null, 2)}</pre>}
    </div>
  );
}
```

## Hooks

### `usePipeline(pipelineId)`

Run a pipeline by ID with full state management.

```tsx
const {
  run,           // (input, options?) => Promise<PipelineResult>
  result,        // PipelineResult | null
  status,        // 'idle' | 'loading' | 'running' | 'success' | 'error'
  error,         // string | null
  isLoading,     // boolean
  isRunning,     // boolean
  isSuccess,     // boolean
  isError,       // boolean
  progress,      // PipelineProgress | null
  cancel,        // () => void
  reset,         // () => void
} = usePipeline('pipeline-id');
```

### `usePipelineByName(name, version?)`

Run a pipeline by name (with optional version).

```tsx
const { run, result, isRunning } = usePipelineByName('content-generator', '1.0.0');

await run({ topic: 'AI Safety' });
```

### `usePipelines(options?)`

List available pipelines.

```tsx
const { pipelines, isLoading, error, refresh } = usePipelines({
  status: 'published',
  category: 'content',
  autoFetch: true,
});
```

### `usePipelineDetails(pipelineId)`

Get details for a specific pipeline.

```tsx
const { pipeline, isLoading, error, refresh } = usePipelineDetails('pipeline-id');
```

### `useComponents(options?)`

List available components.

```tsx
const {
  components,
  isLoading,
  error,
  filterByCategory,
  filterByKind,
  refresh,
} = useComponents({
  category: 'ai',
  kind: 'node',
});

const aiNodes = filterByKind('node');
```

### `useRunHistory(options?)`

Get pipeline run history.

```tsx
const { runs, isLoading, error, getRun, refresh } = useRunHistory({
  pipelineId: 'pipeline-id',
  limit: 50,
});
```

### `useStreamingPipeline(pipelineId)`

Run a pipeline with real-time stage updates.

```tsx
const { run, result, stages, progress } = useStreamingPipeline('pipeline-id');

// stages: { 'stage-1': 'completed', 'stage-2': 'running', ... }
```

## Provider

Wrap your app with `FlowMasonProvider` to configure the client:

```tsx
import { FlowMasonProvider } from '@flowmason/react';

function App() {
  return (
    <FlowMasonProvider
      config={{
        studioUrl: 'http://localhost:8999/api/v1',
        apiKey: 'your-api-key',
        orgId: 'your-org-id',
        timeout: 300000,
      }}
    >
      <YourApp />
    </FlowMasonProvider>
  );
}
```

## Direct Client Access

Use the client directly for advanced use cases:

```tsx
import { useFlowMasonClient } from '@flowmason/react';

function MyComponent() {
  const client = useFlowMasonClient();

  const handleCustomOperation = async () => {
    const result = await client.runPipeline('id', { input: 'data' });
    // Handle result
  };
}
```

## TypeScript

Full TypeScript support with exported types:

```tsx
import type {
  PipelineResult,
  Pipeline,
  Component,
  PipelineProgress,
  UsageMetrics,
} from '@flowmason/react';
```

## License

MIT
