/**
 * FlowMason Mobile Types
 */

export interface Pipeline {
  name: string;
  version: string;
  description?: string;
  stages: Stage[];
  schedule?: string;
  lastRun?: PipelineRun;
}

export interface Stage {
  id: string;
  component_type: string;
  config: Record<string, unknown>;
  dependencies?: string[];
}

export interface PipelineRun {
  id: string;
  pipeline_name: string;
  status: RunStatus;
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  output?: unknown;
  error?: string;
  stages: StageRun[];
}

export interface StageRun {
  id: string;
  status: RunStatus;
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  output?: unknown;
  error?: string;
}

export type RunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface ServerConfig {
  url: string;
  apiKey: string;
  name?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface DashboardStats {
  totalPipelines: number;
  activePipelines: number;
  runsToday: number;
  successRate: number;
  recentRuns: PipelineRun[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info';
  title: string;
  message: string;
  pipeline?: string;
  run_id?: string;
  timestamp: string;
  read: boolean;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}
