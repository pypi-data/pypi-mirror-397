/**
 * FlowMason React SDK Types
 */

export interface FlowMasonConfig {
  /** Studio API URL */
  studioUrl?: string;
  /** API key for authentication */
  apiKey?: string;
  /** Organization ID for multi-tenant setups */
  orgId?: string;
  /** Default timeout in milliseconds */
  timeout?: number;
}

export interface PipelineInput {
  [key: string]: unknown;
}

export interface StageResult {
  stageId: string;
  stageName?: string;
  componentType: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  output?: unknown;
  error?: string;
  durationMs?: number;
  startedAt?: string;
  completedAt?: string;
}

export interface UsageMetrics {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  totalCostUsd: number;
  provider?: string;
  model?: string;
}

export interface PipelineResult {
  runId: string;
  pipelineId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  success: boolean;
  output?: unknown;
  error?: string;
  stageResults: Record<string, StageResult>;
  usage?: UsageMetrics;
  startedAt: string;
  completedAt?: string;
  durationMs?: number;
}

export interface PipelineProgress {
  currentStage?: string;
  currentStageName?: string;
  completedStages: string[];
  totalStages: number;
  percentComplete: number;
}

export interface Pipeline {
  id: string;
  name: string;
  description?: string;
  version: string;
  status: 'draft' | 'testing' | 'published' | 'archived';
  stages: PipelineStage[];
  inputSchema?: Record<string, unknown>;
  outputSchema?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface PipelineStage {
  id: string;
  name?: string;
  componentType: string;
  config: Record<string, unknown>;
  dependsOn?: string[];
}

export interface Component {
  componentType: string;
  componentKind: 'node' | 'operator';
  name: string;
  description?: string;
  category?: string;
  version: string;
  icon?: string;
  color?: string;
  inputSchema?: Record<string, unknown>;
  outputSchema?: Record<string, unknown>;
  requiresLlm?: boolean;
}

export interface RunOptions {
  /** Trace ID for observability */
  traceId?: string;
  /** Timeout in milliseconds */
  timeout?: number;
  /** Callback URL for async execution */
  callbackUrl?: string;
  /** Run asynchronously */
  async?: boolean;
}

export type PipelineStatus = 'idle' | 'loading' | 'running' | 'success' | 'error';

export interface UsePipelineReturn {
  /** Run the pipeline with given input */
  run: (input: PipelineInput, options?: RunOptions) => Promise<PipelineResult>;
  /** Current execution result */
  result: PipelineResult | null;
  /** Current status */
  status: PipelineStatus;
  /** Error message if failed */
  error: string | null;
  /** Loading state */
  isLoading: boolean;
  /** Running state */
  isRunning: boolean;
  /** Success state */
  isSuccess: boolean;
  /** Error state */
  isError: boolean;
  /** Current progress during execution */
  progress: PipelineProgress | null;
  /** Cancel the current execution */
  cancel: () => void;
  /** Reset state */
  reset: () => void;
}

export interface UsePipelinesReturn {
  /** List of pipelines */
  pipelines: Pipeline[];
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
  /** Refresh the pipeline list */
  refresh: () => Promise<void>;
}

export interface UseComponentsReturn {
  /** List of components */
  components: Component[];
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
  /** Filter by category */
  filterByCategory: (category: string) => Component[];
  /** Filter by kind */
  filterByKind: (kind: 'node' | 'operator') => Component[];
  /** Refresh the component list */
  refresh: () => Promise<void>;
}

export interface UseRunHistoryReturn {
  /** List of runs */
  runs: PipelineResult[];
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
  /** Get a specific run */
  getRun: (runId: string) => Promise<PipelineResult | null>;
  /** Refresh the run history */
  refresh: () => Promise<void>;
}
