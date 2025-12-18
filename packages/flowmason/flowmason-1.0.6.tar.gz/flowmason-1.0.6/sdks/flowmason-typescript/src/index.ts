/**
 * @flowmason/sdk - TypeScript/JavaScript SDK for FlowMason pipeline orchestration
 *
 * @example
 * ```typescript
 * import { FlowMason } from '@flowmason/sdk';
 *
 * const fm = new FlowMason({
 *   studioUrl: 'http://localhost:8999/api/v1',
 *   apiKey: 'your-api-key',
 * });
 *
 * // Run a pipeline
 * const result = await fm.run('pipeline-id', { query: 'Hello, world!' });
 * console.log(result.output);
 *
 * // Run by name with version
 * const result2 = await fm.runByName('content-generator@1.0.0', { topic: 'AI' });
 *
 * // Stream execution updates
 * await fm.runWithStream('pipeline-id', { input: 'data' }, {
 *   onStageStart: (stage) => console.log(`Starting: ${stage.stageId}`),
 *   onStageComplete: (stage) => console.log(`Done: ${stage.stageId}`),
 *   onComplete: (result) => console.log('Pipeline complete!', result.output),
 * });
 * ```
 */

// Client
export { FlowMason, createClient, getDefaultClient, setDefaultClient } from './client';

// Types
export type {
  FlowMasonConfig,
  PipelineInput,
  PipelineResult,
  Pipeline,
  PipelineStage,
  PipelineStatus,
  Component,
  StageResult,
  StageStatus,
  UsageMetrics,
  RunOptions,
  RunStatus,
  OutputConfig,
  OutputDestination,
  JsonSchema,
  ListOptions,
  PipelineListOptions,
  RunListOptions,
  ComponentListOptions,
  PaginatedResponse,
  StreamCallbacks,
  WebSocketMessage,
} from './types';

export { FlowMasonError } from './types';
