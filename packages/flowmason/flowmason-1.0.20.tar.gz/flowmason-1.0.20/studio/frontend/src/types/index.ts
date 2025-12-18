/**
 * FlowMason Studio Types
 *
 * These types mirror the API models from the backend.
 */

// Component kind types
export type ComponentKind = 'node' | 'operator' | 'control_flow';

// Control flow types for different visual representations
export type ControlFlowType =
  | 'conditional'   // Diamond shape (if/else)
  | 'router'        // Diamond shape (switch/case)
  | 'foreach'       // Container shape (loop)
  | 'trycatch'      // Container shape (error handling)
  | 'subpipeline'   // Nested box shape (function call)
  | 'return';       // Arrow shape (early exit)

// Component from Registry
export interface ComponentInfo {
  component_type: string;
  component_kind: ComponentKind;
  name: string;
  version: string;
  description: string;
  category: string;
  icon: string;
  color: string;
  author: string;
  tags: string[];
  input_schema: JsonSchema;
  output_schema: JsonSchema;
  requires_llm: boolean;
  recommended_providers?: Record<string, ProviderConfig>;
  default_provider?: string;
  is_core: boolean;
  is_available: boolean;
  // Control flow specific
  control_flow_type?: ControlFlowType;
}

export interface ProviderConfig {
  model: string;
  temperature?: number;
  max_tokens?: number;
}

export interface JsonSchema {
  type: string;
  properties?: Record<string, JsonSchemaProperty>;
  required?: string[];
  additionalProperties?: boolean;
}

export interface JsonSchemaProperty {
  type: string;
  description?: string;
  default?: unknown;
  examples?: unknown[];
  enum?: unknown[];
  minimum?: number;
  maximum?: number;
  minLength?: number;
  maxLength?: number;
}

// Pipeline Status
export type PipelineStatus = 'draft' | 'published';

// Pipeline Configuration
export interface Pipeline {
  id: string;
  name: string;
  description: string;
  category: string;
  version: string;
  status: PipelineStatus;  // draft or published
  stages?: PipelineStage[];
  stage_count?: number;  // From PipelineSummary
  input_schema?: JsonSchema;
  output_schema?: JsonSchema;
  output_stage_id?: string;
  tags?: string[];
  is_template?: boolean;  // Whether this pipeline is a template
  sample_input?: Record<string, unknown>;  // Sample input for testing
  last_test_run_id?: string;  // ID of successful test run
  published_at?: string;  // When pipeline was published
  created_at: string;
  updated_at: string;
}

export interface PipelineStage {
  id: string;
  component_type: string;
  name: string;
  config: Record<string, unknown>;
  depends_on: string[];
  position?: { x: number; y: number };
  // LLM settings for stages that require LLM
  llm_settings?: LLMSettings;
}

export interface LLMSettings {
  provider?: string;       // Override default provider (e.g., 'anthropic', 'openai')
  model?: string;          // Override default model (e.g., 'claude-sonnet-4-20250514')
  temperature?: number;    // 0.0 - 1.0
  max_tokens?: number;     // Max response tokens
  top_p?: number;          // Nucleus sampling
  stop_sequences?: string[];
}

// Execution
export interface PipelineRun {
  id: string;  // API returns 'id', not 'run_id'
  pipeline_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  inputs: Record<string, unknown>;  // API returns 'inputs' (plural)
  output?: Record<string, unknown>;
  error?: string;
  started_at: string;
  completed_at?: string;
  usage?: UsageMetrics;
  trace?: ExecutionTrace;
}

export interface UsageMetrics {
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_cost: number;
  execution_time_ms: number;
}

export interface ExecutionTrace {
  stages: StageTrace[];
}

export interface StageTrace {
  stage_id: string;
  component_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
  usage?: UsageMetrics;
}

// Registry Stats
export interface RegistryStats {
  total_components: number;
  total_nodes: number;
  total_operators: number;
  total_packages: number;
  loaded_components: number;
  categories: string[];
  core_packages: number;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

// Settings
export interface ProviderSettingsResponse {
  provider: string;
  has_key: boolean;
  key_preview: string;
  default_model: string | null;
  enabled: boolean;
  available_models: string[];
}

export interface AppSettingsResponse {
  default_provider: string;
  theme: string;
  auto_save: boolean;
  providers: Record<string, ProviderSettingsResponse>;
}

export interface ProviderTestResponse {
  provider: string;
  success: boolean;
  message: string;
  model_tested: string | null;
}

// Backend Logging Types
export type BackendLogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
export type LogCategory = 'SYSTEM' | 'API' | 'EXECUTION' | 'PROVIDER' | 'REGISTRY' | 'STORAGE' | 'DATABASE' | 'VALIDATION' | 'CALLOUT';

export interface BackendLogEntry {
  id: string;
  timestamp: string;
  level: BackendLogLevel;
  category: LogCategory;
  message: string;
  logger_name: string;
  details?: Record<string, unknown>;
  duration_ms?: number;
}

export interface LogListResponse {
  entries: BackendLogEntry[];
  total: number;
  limit: number;
  offset: number;
}

export interface LogConfigResponse {
  global_level: BackendLogLevel;
  category_levels: Record<string, BackendLogLevel>;
  max_entries: number;
  enabled: boolean;
  categories: string[];
}

export interface LogStatsResponse {
  total_entries: number;
  entries_by_level: Record<string, number>;
  entries_by_category: Record<string, number>;
}

// Debug Types
export type DebugMode = 'stopped' | 'running' | 'paused' | 'stepping';
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogEntry {
  id: string;
  level: LogLevel;
  message: string;
  timestamp: string;
  source?: string;
  stageId?: string;
  data?: Record<string, unknown>;
}

export interface Breakpoint {
  id: string;
  stageId: string;
  condition?: string;
  enabled: boolean;
  hitCount: number;
  maxHits?: number;
}

export interface VariableInfo {
  name: string;
  value: unknown;
  type: string;
  source: string;
  timestamp: string;
  changed: boolean;
}

export interface ExecutionStep {
  stepId: string;
  stageId: string;
  stageName: string;
  componentType: string;
  timestamp: string;
  duration?: number;
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  error?: string;
  logs: LogEntry[];
}

export interface NetworkCall {
  id: string;
  type: 'api' | 'llm';
  method?: string;
  url?: string;
  provider?: string;
  model?: string;
  timestamp: string;
  duration?: number;
  status: 'pending' | 'success' | 'error';
  requestBody?: unknown;
  responseBody?: unknown;
  tokens?: {
    input: number;
    output: number;
    total: number;
  };
  error?: string;
}

export interface DebugState {
  mode: DebugMode;
  currentStageId: string | null;
  breakpoints: Breakpoint[];
  executionTrace: ExecutionStep[];
  variables: Record<string, VariableInfo>;
  logs: LogEntry[];
  networkCalls: NetworkCall[];
  startTime: string | null;
  pausedAt: string | null;
}

// Pipeline Test/Publish Response Types
export interface TestPipelineResponse {
  run_id: string;
  pipeline_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  is_success: boolean;
  result?: Record<string, unknown>;
  error?: string;
  can_publish: boolean;
}

export interface PublishPipelineResponse {
  pipeline_id: string;
  status: PipelineStatus;
  published_at?: string;
  version: string;
  message: string;
}

export interface UnpublishPipelineResponse {
  pipeline_id: string;
  status: PipelineStatus;
  message: string;
}
