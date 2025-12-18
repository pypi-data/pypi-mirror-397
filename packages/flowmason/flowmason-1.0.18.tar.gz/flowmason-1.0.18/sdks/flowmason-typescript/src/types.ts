/**
 * FlowMason TypeScript SDK Types
 */

export interface FlowMasonConfig {
  /** Studio API URL (default: http://localhost:8999/api/v1) */
  studioUrl?: string;
  /** API key for authentication */
  apiKey?: string;
  /** Organization ID for multi-tenant setups */
  orgId?: string;
  /** Default timeout in milliseconds (default: 300000) */
  timeout?: number;
  /** Custom fetch implementation */
  fetch?: typeof fetch;
  /** Custom headers to include in all requests */
  headers?: Record<string, string>;
}

export interface PipelineInput {
  [key: string]: unknown;
}

export interface StageResult {
  stageId: string;
  stageName?: string;
  componentType: string;
  status: StageStatus;
  output?: unknown;
  error?: string;
  errorType?: string;
  durationMs?: number;
  startedAt?: string;
  completedAt?: string;
  retryCount?: number;
}

export type StageStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped' | 'cancelled';

export interface UsageMetrics {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  totalCostUsd: number;
  provider?: string;
  model?: string;
  promptTokens?: number;
  completionTokens?: number;
}

export interface PipelineResult {
  runId: string;
  pipelineId: string;
  pipelineName?: string;
  status: RunStatus;
  success: boolean;
  output?: unknown;
  error?: string;
  errorType?: string;
  stageResults: Record<string, StageResult>;
  usage?: UsageMetrics;
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
  traceId?: string;
}

export type RunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'timeout';

export interface Pipeline {
  id: string;
  name: string;
  description?: string;
  version: string;
  status: PipelineStatus;
  category?: string;
  tags?: string[];
  stages: PipelineStage[];
  inputSchema?: JsonSchema;
  outputSchema?: JsonSchema;
  sampleInput?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  publishedAt?: string;
}

export type PipelineStatus = 'draft' | 'testing' | 'published' | 'archived';

export interface PipelineStage {
  id: string;
  name?: string;
  componentType: string;
  config: Record<string, unknown>;
  inputMapping?: Record<string, string>;
  dependsOn?: string[];
  condition?: string;
  timeout?: number;
  retries?: number;
}

export interface JsonSchema {
  type?: string;
  properties?: Record<string, JsonSchema>;
  required?: string[];
  items?: JsonSchema;
  description?: string;
  default?: unknown;
  enum?: unknown[];
  [key: string]: unknown;
}

export interface Component {
  componentType: string;
  componentKind: 'node' | 'operator';
  name: string;
  description?: string;
  category?: string;
  version: string;
  packageName?: string;
  icon?: string;
  color?: string;
  inputSchema?: JsonSchema;
  outputSchema?: JsonSchema;
  requiresLlm?: boolean;
  tags?: string[];
}

export interface RunOptions {
  /** Trace ID for observability */
  traceId?: string;
  /** Timeout in milliseconds */
  timeout?: number;
  /** Callback URL for async execution */
  callbackUrl?: string;
  /** Run asynchronously (returns immediately with run ID) */
  async?: boolean;
  /** Output configuration */
  outputConfig?: OutputConfig;
}

export interface OutputConfig {
  destinations?: OutputDestination[];
  includeStageResults?: boolean;
  format?: 'json' | 'text';
}

export interface OutputDestination {
  type: 'webhook' | 'email' | 'database';
  config: Record<string, unknown>;
  onSuccess?: boolean;
  onError?: boolean;
}

export interface ListOptions {
  limit?: number;
  offset?: number;
}

export interface PipelineListOptions extends ListOptions {
  status?: PipelineStatus;
  category?: string;
  search?: string;
}

export interface RunListOptions extends ListOptions {
  pipelineId?: string;
  status?: RunStatus;
  startDate?: string;
  endDate?: string;
}

export interface ComponentListOptions extends ListOptions {
  category?: string;
  kind?: 'node' | 'operator';
  search?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  hasMore: boolean;
}

export interface WebSocketMessage {
  type: 'stage_started' | 'stage_completed' | 'stage_failed' | 'pipeline_completed' | 'pipeline_failed' | 'progress';
  runId: string;
  timestamp: string;
  data?: unknown;
}

export interface StreamCallbacks {
  onStageStart?: (stage: StageResult) => void;
  onStageComplete?: (stage: StageResult) => void;
  onStageError?: (stage: StageResult) => void;
  onProgress?: (progress: { percentComplete: number; currentStage?: string }) => void;
  onComplete?: (result: PipelineResult) => void;
  onError?: (error: Error) => void;
}

export class FlowMasonError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status?: number,
    public readonly details?: unknown
  ) {
    super(message);
    this.name = 'FlowMasonError';
  }
}
