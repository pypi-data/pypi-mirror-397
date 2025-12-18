/**
 * FlowMason API Client
 */

import type {
  FlowMasonConfig,
  PipelineInput,
  PipelineResult,
  Pipeline,
  Component,
  RunOptions,
  StageResult,
} from './types';

export class FlowMasonClient {
  private baseUrl: string;
  private apiKey?: string;
  private orgId?: string;
  private timeout: number;
  private abortController?: AbortController;

  constructor(config: FlowMasonConfig = {}) {
    this.baseUrl = config.studioUrl || 'http://localhost:8999/api/v1';
    this.apiKey = config.apiKey;
    this.orgId = config.orgId;
    this.timeout = config.timeout || 300000; // 5 minutes default
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    if (this.orgId) {
      headers['X-Org-ID'] = this.orgId;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * Run a pipeline by ID
   */
  async runPipeline(
    pipelineId: string,
    input: PipelineInput,
    options: RunOptions = {}
  ): Promise<PipelineResult> {
    this.abortController = new AbortController();

    const body = {
      input,
      trace_id: options.traceId,
      callback_url: options.callbackUrl,
      async: options.async,
    };

    return this.request<PipelineResult>(`/pipelines/${pipelineId}/run`, {
      method: 'POST',
      body: JSON.stringify(body),
      signal: this.abortController.signal,
    });
  }

  /**
   * Run a pipeline by name (with optional version)
   */
  async runPipelineByName(
    name: string,
    input: PipelineInput,
    options: RunOptions & { version?: string } = {}
  ): Promise<PipelineResult> {
    this.abortController = new AbortController();

    const body = {
      input,
      trace_id: options.traceId,
      callback_url: options.callbackUrl,
    };

    const nameWithVersion = options.version ? `${name}@${options.version}` : name;

    return this.request<PipelineResult>(`/run/${nameWithVersion}`, {
      method: 'POST',
      body: JSON.stringify(body),
      signal: this.abortController.signal,
    });
  }

  /**
   * Get run status
   */
  async getRunStatus(runId: string): Promise<PipelineResult> {
    return this.request<PipelineResult>(`/runs/${runId}`);
  }

  /**
   * Cancel a running pipeline
   */
  async cancelRun(runId: string): Promise<void> {
    await this.request(`/runs/${runId}/cancel`, { method: 'POST' });
    this.abortController?.abort();
  }

  /**
   * Cancel current request
   */
  cancel(): void {
    this.abortController?.abort();
  }

  /**
   * List pipelines
   */
  async listPipelines(options: {
    status?: string;
    category?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<{ pipelines: Pipeline[]; total: number }> {
    const params = new URLSearchParams();
    if (options.status) params.set('status', options.status);
    if (options.category) params.set('category', options.category);
    if (options.limit) params.set('limit', options.limit.toString());
    if (options.offset) params.set('offset', options.offset.toString());

    const query = params.toString();
    return this.request(`/pipelines${query ? `?${query}` : ''}`);
  }

  /**
   * Get a pipeline by ID
   */
  async getPipeline(pipelineId: string): Promise<Pipeline> {
    return this.request<Pipeline>(`/pipelines/${pipelineId}`);
  }

  /**
   * List components
   */
  async listComponents(options: {
    category?: string;
    kind?: 'node' | 'operator';
  } = {}): Promise<{ components: Component[]; total: number }> {
    const params = new URLSearchParams();
    if (options.category) params.set('category', options.category);
    if (options.kind) params.set('kind', options.kind);

    const query = params.toString();
    return this.request(`/registry/components${query ? `?${query}` : ''}`);
  }

  /**
   * Get component details
   */
  async getComponent(componentType: string): Promise<Component> {
    return this.request<Component>(`/registry/components/${componentType}`);
  }

  /**
   * List run history
   */
  async listRuns(options: {
    pipelineId?: string;
    status?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<{ runs: PipelineResult[]; total: number }> {
    const params = new URLSearchParams();
    if (options.pipelineId) params.set('pipeline_id', options.pipelineId);
    if (options.status) params.set('status', options.status);
    if (options.limit) params.set('limit', options.limit.toString());
    if (options.offset) params.set('offset', options.offset.toString());

    const query = params.toString();
    return this.request(`/runs${query ? `?${query}` : ''}`);
  }

  /**
   * Stream pipeline execution via WebSocket
   */
  streamExecution(
    runId: string,
    callbacks: {
      onStageStart?: (stage: StageResult) => void;
      onStageComplete?: (stage: StageResult) => void;
      onStageError?: (stage: StageResult) => void;
      onComplete?: (result: PipelineResult) => void;
      onError?: (error: Error) => void;
    }
  ): () => void {
    const wsUrl = this.baseUrl.replace(/^http/, 'ws').replace('/api/v1', '');
    const ws = new WebSocket(`${wsUrl}/ws/runs/${runId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'stage_started':
          callbacks.onStageStart?.(data.stage);
          break;
        case 'stage_completed':
          callbacks.onStageComplete?.(data.stage);
          break;
        case 'stage_failed':
          callbacks.onStageError?.(data.stage);
          break;
        case 'pipeline_completed':
          callbacks.onComplete?.(data.result);
          break;
        case 'pipeline_failed':
          callbacks.onError?.(new Error(data.error));
          break;
      }
    };

    ws.onerror = (event) => {
      callbacks.onError?.(new Error('WebSocket error'));
    };

    // Return cleanup function
    return () => ws.close();
  }
}

// Default client instance
let defaultClient: FlowMasonClient | null = null;

export function getClient(): FlowMasonClient {
  if (!defaultClient) {
    defaultClient = new FlowMasonClient();
  }
  return defaultClient;
}

export function setClient(client: FlowMasonClient): void {
  defaultClient = client;
}

export function configureClient(config: FlowMasonConfig): FlowMasonClient {
  defaultClient = new FlowMasonClient(config);
  return defaultClient;
}
