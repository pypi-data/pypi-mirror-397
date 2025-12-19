/**
 * @flowmason/react - React hooks for FlowMason pipeline orchestration
 *
 * @example
 * ```tsx
 * import { FlowMasonProvider, usePipeline } from '@flowmason/react';
 *
 * function App() {
 *   return (
 *     <FlowMasonProvider config={{ studioUrl: 'http://localhost:8999/api/v1' }}>
 *       <MyComponent />
 *     </FlowMasonProvider>
 *   );
 * }
 *
 * function MyComponent() {
 *   const { run, result, isRunning, error } = usePipeline('my-pipeline-id');
 *
 *   const handleClick = async () => {
 *     await run({ query: 'Hello, world!' });
 *   };
 *
 *   return (
 *     <div>
 *       <button onClick={handleClick} disabled={isRunning}>
 *         {isRunning ? 'Running...' : 'Run Pipeline'}
 *       </button>
 *       {error && <p style={{ color: 'red' }}>{error}</p>}
 *       {result && <pre>{JSON.stringify(result.output, null, 2)}</pre>}
 *     </div>
 *   );
 * }
 * ```
 */

// Types
export type {
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
  UsePipelineReturn,
  UsePipelinesReturn,
  UseComponentsReturn,
  UseRunHistoryReturn,
} from './types';

// Client
export {
  FlowMasonClient,
  getClient,
  setClient,
  configureClient,
} from './client';

// Hooks
export {
  FlowMasonProvider,
  useFlowMasonClient,
  usePipeline,
  usePipelineByName,
  usePipelines,
  usePipelineDetails,
  useComponents,
  useRunHistory,
  useStreamingPipeline,
} from './hooks';
export type { FlowMasonProviderProps } from './hooks';
