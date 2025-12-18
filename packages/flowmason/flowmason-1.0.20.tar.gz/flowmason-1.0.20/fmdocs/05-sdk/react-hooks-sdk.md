# React Hooks SDK

FlowMason provides a React SDK with hooks for seamless pipeline integration in React applications.

## Installation

```bash
npm install @flowmason/react
```

## Quick Start

```tsx
import { FlowMasonProvider, usePipeline } from '@flowmason/react';

function App() {
  return (
    <FlowMasonProvider config={{ studioUrl: 'http://localhost:8999/api/v1' }}>
      <ContentGenerator />
    </FlowMasonProvider>
  );
}

function ContentGenerator() {
  const { run, result, isRunning, error } = usePipeline('content-generator');

  const handleGenerate = async () => {
    await run({ topic: 'AI Safety', style: 'professional' });
  };

  return (
    <div>
      <button onClick={handleGenerate} disabled={isRunning}>
        {isRunning ? 'Generating...' : 'Generate Content'}
      </button>

      {error && <div className="error">{error}</div>}

      {result?.success && (
        <article>{result.output.content}</article>
      )}
    </div>
  );
}
```

## Provider Setup

### Basic Configuration

```tsx
import { FlowMasonProvider } from '@flowmason/react';

function App() {
  return (
    <FlowMasonProvider
      config={{
        studioUrl: 'http://localhost:8999/api/v1',
        apiKey: process.env.REACT_APP_FLOWMASON_API_KEY,
        orgId: 'my-org',
        timeout: 300000, // 5 minutes
      }}
    >
      <YourApp />
    </FlowMasonProvider>
  );
}
```

### With Custom Client

```tsx
import { FlowMasonProvider, FlowMasonClient } from '@flowmason/react';

const client = new FlowMasonClient({
  studioUrl: 'https://studio.example.com/api/v1',
  apiKey: 'sk-...',
});

function App() {
  return (
    <FlowMasonProvider client={client}>
      <YourApp />
    </FlowMasonProvider>
  );
}
```

## Hooks Reference

### usePipeline

Run a pipeline by ID with full state management.

```tsx
function PipelineRunner() {
  const {
    run,           // Execute the pipeline
    result,        // Latest result
    status,        // 'idle' | 'running' | 'success' | 'error'
    error,         // Error message if failed
    isLoading,     // Initial loading state
    isRunning,     // Currently executing
    isSuccess,     // Completed successfully
    isError,       // Failed with error
    progress,      // Execution progress
    cancel,        // Cancel execution
    reset,         // Reset to initial state
  } = usePipeline('pipeline-id');

  const handleRun = async () => {
    try {
      const result = await run(
        { query: 'Hello' },
        { traceId: 'trace-123' }
      );
      console.log('Output:', result.output);
    } catch (err) {
      console.error('Failed:', err);
    }
  };

  return (
    <div>
      <button onClick={handleRun} disabled={isRunning}>
        Run Pipeline
      </button>

      {progress && (
        <div>
          Stage: {progress.currentStageName}
          Progress: {progress.percentComplete}%
        </div>
      )}

      {isSuccess && <pre>{JSON.stringify(result?.output, null, 2)}</pre>}
      {isError && <div className="error">{error}</div>}
    </div>
  );
}
```

### usePipelineByName

Run a pipeline by name with optional version.

```tsx
function VersionedPipeline() {
  const { run, result, isRunning } = usePipelineByName(
    'content-generator',
    '2.0.0' // Optional version
  );

  const handleRun = async () => {
    await run({ topic: 'Machine Learning' });
  };

  return (
    <button onClick={handleRun} disabled={isRunning}>
      Generate with v2.0.0
    </button>
  );
}
```

### usePipelines

List and filter pipelines.

```tsx
function PipelineList() {
  const { pipelines, isLoading, error, refresh } = usePipelines({
    status: 'published',
    category: 'content',
    autoFetch: true,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <button onClick={refresh}>Refresh</button>
      <ul>
        {pipelines.map(p => (
          <li key={p.id}>{p.name} - v{p.version}</li>
        ))}
      </ul>
    </div>
  );
}
```

### usePipelineDetails

Get detailed information about a pipeline.

```tsx
function PipelineDetails({ id }: { id: string }) {
  const { pipeline, isLoading, error } = usePipelineDetails(id);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!pipeline) return null;

  return (
    <div>
      <h2>{pipeline.name}</h2>
      <p>{pipeline.description}</p>
      <h3>Stages ({pipeline.stages.length})</h3>
      <ul>
        {pipeline.stages.map(stage => (
          <li key={stage.id}>
            {stage.name || stage.id} ({stage.componentType})
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### useComponents

List and filter available components.

```tsx
function ComponentLibrary() {
  const {
    components,
    isLoading,
    filterByCategory,
    filterByKind,
    refresh,
  } = useComponents();

  const aiNodes = filterByKind('node');
  const utilityOps = filterByCategory('utility');

  return (
    <div>
      <h2>AI Nodes ({aiNodes.length})</h2>
      <ul>
        {aiNodes.map(c => (
          <li key={c.componentType}>
            <strong>{c.name}</strong>: {c.description}
          </li>
        ))}
      </ul>

      <h2>Utility Operators ({utilityOps.length})</h2>
      <ul>
        {utilityOps.map(c => (
          <li key={c.componentType}>{c.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

### useRunHistory

Access pipeline execution history.

```tsx
function RunHistory({ pipelineId }: { pipelineId: string }) {
  const { runs, isLoading, getRun, refresh } = useRunHistory({
    pipelineId,
    limit: 20,
  });

  const viewDetails = async (runId: string) => {
    const run = await getRun(runId);
    console.log('Run details:', run);
  };

  return (
    <table>
      <thead>
        <tr>
          <th>Run ID</th>
          <th>Status</th>
          <th>Duration</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {runs.map(run => (
          <tr key={run.runId}>
            <td>{run.runId}</td>
            <td>{run.status}</td>
            <td>{run.durationMs}ms</td>
            <td>
              <button onClick={() => viewDetails(run.runId)}>
                View
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### useStreamingPipeline

Real-time stage updates during execution.

```tsx
function StreamingExecution() {
  const { run, result, stages, progress, isRunning } = useStreamingPipeline('pipeline-id');

  return (
    <div>
      <button onClick={() => run({ input: 'data' })} disabled={isRunning}>
        Run with Streaming
      </button>

      <div className="stages">
        {Object.entries(stages).map(([stageId, status]) => (
          <div key={stageId} className={`stage stage-${status}`}>
            {stageId}: {status}
          </div>
        ))}
      </div>

      {progress && (
        <progress value={progress.percentComplete} max={100} />
      )}
    </div>
  );
}
```

## Direct Client Access

For advanced use cases, access the client directly:

```tsx
import { useFlowMasonClient } from '@flowmason/react';

function AdvancedComponent() {
  const client = useFlowMasonClient();

  const handleBatchRun = async () => {
    const pipelines = ['pipeline-1', 'pipeline-2', 'pipeline-3'];

    const results = await Promise.all(
      pipelines.map(id => client.runPipeline(id, { query: 'test' }))
    );

    console.log('Batch results:', results);
  };

  return <button onClick={handleBatchRun}>Run Batch</button>;
}
```

## TypeScript Types

All types are exported for TypeScript users:

```tsx
import type {
  FlowMasonConfig,
  PipelineInput,
  PipelineResult,
  Pipeline,
  PipelineStage,
  Component,
  StageResult,
  UsageMetrics,
  RunOptions,
  PipelineProgress,
  PipelineStatus,
} from '@flowmason/react';
```

## Error Handling

```tsx
function RobustPipeline() {
  const { run, result, error, isError, reset } = usePipeline('pipeline-id');

  const handleRun = async () => {
    try {
      const result = await run({ input: 'data' });

      if (!result.success) {
        console.error('Pipeline failed:', result.error);
        // Handle pipeline-level errors
      }
    } catch (err) {
      // Handle network/client errors
      console.error('Request failed:', err);
    }
  };

  return (
    <div>
      <button onClick={handleRun}>Run</button>

      {isError && (
        <div className="error">
          <p>{error}</p>
          <button onClick={reset}>Try Again</button>
        </div>
      )}
    </div>
  );
}
```

## Best Practices

### 1. Use Provider at App Root

```tsx
// ✅ Good - Provider at root
function App() {
  return (
    <FlowMasonProvider config={config}>
      <Router>
        <Routes />
      </Router>
    </FlowMasonProvider>
  );
}
```

### 2. Handle Loading States

```tsx
// ✅ Good - Complete state handling
function Pipeline() {
  const { run, isRunning, isSuccess, isError, result, error } = usePipeline('id');

  if (isRunning) return <Spinner />;
  if (isError) return <ErrorMessage message={error} />;
  if (isSuccess) return <Result data={result} />;

  return <button onClick={() => run({})}>Start</button>;
}
```

### 3. Cancel on Unmount

The hooks automatically clean up, but for manual operations:

```tsx
function CancellablePipeline() {
  const { run, cancel, isRunning } = usePipeline('id');

  useEffect(() => {
    return () => {
      if (isRunning) cancel();
    };
  }, [isRunning, cancel]);

  return <button onClick={() => run({})}>Run</button>;
}
```

### 4. Use Trace IDs for Debugging

```tsx
function TrackedPipeline() {
  const { run } = usePipeline('id');

  const handleRun = async () => {
    const traceId = `web-${Date.now()}`;
    await run({ input: 'data' }, { traceId });
    console.log('Trace ID for debugging:', traceId);
  };

  return <button onClick={handleRun}>Run with Trace</button>;
}
```
