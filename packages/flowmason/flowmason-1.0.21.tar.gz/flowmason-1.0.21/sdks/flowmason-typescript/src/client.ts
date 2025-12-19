/**
 * FlowMason TypeScript SDK Client
 */

import type {
  FlowMasonConfig,
  PipelineInput,
  PipelineResult,
  Pipeline,
  Component,
  RunOptions,
  PipelineListOptions,
  RunListOptions,
  ComponentListOptions,
  PaginatedResponse,
  StreamCallbacks,
  StageResult,
} from './types';
import { FlowMasonError } from './types';

export class FlowMason {
  private baseUrl: string;
  private apiKey?: string;
  private orgId?: string;
  private timeout: number;
  private customFetch: typeof fetch;
  private customHeaders: Record<string, string>;
  private abortController?: AbortController;

  constructor(config: FlowMasonConfig = {}) {
    this.baseUrl = (config.studioUrl || 'http://localhost:8999/api/v1').replace(/\/$/, '');
    this.apiKey = config.apiKey || process.env.FLOWMASON_API_KEY;
    this.orgId = config.orgId || process.env.FLOWMASON_ORG_ID;
    this.timeout = config.timeout || 300000;
    this.customFetch = config.fetch || globalThis.fetch;
    this.customHeaders = config.headers || {};
  }

  // ============================================
  // Private Helper Methods
  // ============================================

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...this.customHeaders,
      ...(options.headers as Record<string, string>),
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    if (this.orgId) {
      headers['X-Org-ID'] = this.orgId;
    }

    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await this.customFetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: response.statusText,
          code: 'HTTP_ERROR',
        }));
        throw new FlowMasonError(
          error.detail || `HTTP ${response.status}`,
          error.code || 'HTTP_ERROR',
          response.status,
          error
        );
      }

      return response.json();
    } catch (error) {
      if (error instanceof FlowMasonError) {
        throw error;
      }
      if (error instanceof Error) {
        throw new FlowMasonError(error.message, 'NETWORK_ERROR');
      }
      throw new FlowMasonError('Unknown error', 'UNKNOWN_ERROR');
    }
  }

  private buildQueryString(params: Record<string, unknown>): string {
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.set(key, String(value));
      }
    }
    const query = searchParams.toString();
    return query ? `?${query}` : '';
  }

  // ============================================
  // Pipeline Execution
  // ============================================

  /**
   * Run a pipeline by ID
   */
  async run(
    pipelineId: string,
    input: PipelineInput,
    options: RunOptions = {}
  ): Promise<PipelineResult> {
    this.abortController = new AbortController();

    const timeoutId = setTimeout(() => {
      this.abortController?.abort();
    }, options.timeout || this.timeout);

    try {
      const body = {
        input,
        trace_id: options.traceId,
        callback_url: options.callbackUrl,
        async: options.async,
        output_config: options.outputConfig,
      };

      const result = await this.request<PipelineResult>(
        `/pipelines/${pipelineId}/run`,
        {
          method: 'POST',
          body: JSON.stringify(body),
          signal: this.abortController.signal,
        }
      );

      return result;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Run a pipeline by name (with optional version)
   * Format: "pipeline-name" or "pipeline-name@1.0.0"
   */
  async runByName(
    nameWithVersion: string,
    input: PipelineInput,
    options: RunOptions = {}
  ): Promise<PipelineResult> {
    this.abortController = new AbortController();

    const body = {
      input,
      trace_id: options.traceId,
      callback_url: options.callbackUrl,
      output_config: options.outputConfig,
    };

    return this.request<PipelineResult>(`/run/${nameWithVersion}`, {
      method: 'POST',
      body: JSON.stringify(body),
      signal: this.abortController.signal,
    });
  }

  /**
   * Run a pipeline with real-time streaming updates
   */
  async runWithStream(
    pipelineId: string,
    input: PipelineInput,
    callbacks: StreamCallbacks,
    options: RunOptions = {}
  ): Promise<PipelineResult> {
    // Start the run
    const initialResult = await this.run(pipelineId, input, { ...options, async: true });

    // Connect to WebSocket for updates
    return new Promise((resolve, reject) => {
      const wsUrl = this.baseUrl.replace(/^http/, 'ws').replace('/api/v1', '');
      const ws = new WebSocket(`${wsUrl}/ws/runs/${initialResult.runId}`);

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
          case 'progress':
            callbacks.onProgress?.(data.progress);
            break;
          case 'pipeline_completed':
            callbacks.onComplete?.(data.result);
            ws.close();
            resolve(data.result);
            break;
          case 'pipeline_failed':
            const error = new FlowMasonError(data.error, 'PIPELINE_FAILED');
            callbacks.onError?.(error);
            ws.close();
            reject(error);
            break;
        }
      };

      ws.onerror = () => {
        const error = new FlowMasonError('WebSocket error', 'WEBSOCKET_ERROR');
        callbacks.onError?.(error);
        reject(error);
      };
    });
  }

  /**
   * Get the status of a run
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
   * Wait for a run to complete (polling)
   */
  async waitForCompletion(
    runId: string,
    options: { pollInterval?: number; timeout?: number } = {}
  ): Promise<PipelineResult> {
    const pollInterval = options.pollInterval || 1000;
    const timeout = options.timeout || this.timeout;
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const result = await this.getRunStatus(runId);

      if (['completed', 'failed', 'cancelled', 'timeout'].includes(result.status)) {
        return result;
      }

      await new Promise((resolve) => setTimeout(resolve, pollInterval));
    }

    throw new FlowMasonError('Timeout waiting for run completion', 'TIMEOUT');
  }

  // ============================================
  // Pipeline Management
  // ============================================

  /**
   * List pipelines
   */
  async listPipelines(
    options: PipelineListOptions = {}
  ): Promise<PaginatedResponse<Pipeline>> {
    const query = this.buildQueryString(options);
    const response = await this.request<{ pipelines: Pipeline[]; total: number }>(
      `/pipelines${query}`
    );

    return {
      items: response.pipelines,
      total: response.total,
      limit: options.limit || 50,
      offset: options.offset || 0,
      hasMore: (options.offset || 0) + response.pipelines.length < response.total,
    };
  }

  /**
   * Get a pipeline by ID
   */
  async getPipeline(pipelineId: string): Promise<Pipeline> {
    return this.request<Pipeline>(`/pipelines/${pipelineId}`);
  }

  /**
   * Validate a pipeline without running it
   */
  async validatePipeline(
    pipelineId: string,
    input?: PipelineInput
  ): Promise<{ valid: boolean; errors: string[] }> {
    return this.request(`/pipelines/${pipelineId}/validate`, {
      method: 'POST',
      body: JSON.stringify({ input }),
    });
  }

  // ============================================
  // Run History
  // ============================================

  /**
   * List runs
   */
  async listRuns(options: RunListOptions = {}): Promise<PaginatedResponse<PipelineResult>> {
    const query = this.buildQueryString({
      pipeline_id: options.pipelineId,
      status: options.status,
      start_date: options.startDate,
      end_date: options.endDate,
      limit: options.limit,
      offset: options.offset,
    });

    const response = await this.request<{ runs: PipelineResult[]; total: number }>(
      `/runs${query}`
    );

    return {
      items: response.runs,
      total: response.total,
      limit: options.limit || 50,
      offset: options.offset || 0,
      hasMore: (options.offset || 0) + response.runs.length < response.total,
    };
  }

  /**
   * Get run details
   */
  async getRun(runId: string): Promise<PipelineResult> {
    return this.request<PipelineResult>(`/runs/${runId}`);
  }

  /**
   * Get run logs
   */
  async getRunLogs(runId: string): Promise<Array<{ timestamp: string; level: string; message: string }>> {
    return this.request(`/runs/${runId}/logs`);
  }

  // ============================================
  // Component Registry
  // ============================================

  /**
   * List components
   */
  async listComponents(
    options: ComponentListOptions = {}
  ): Promise<PaginatedResponse<Component>> {
    const query = this.buildQueryString(options);
    const response = await this.request<{ components: Component[]; total: number }>(
      `/registry/components${query}`
    );

    return {
      items: response.components,
      total: response.total,
      limit: options.limit || 100,
      offset: options.offset || 0,
      hasMore: (options.offset || 0) + response.components.length < response.total,
    };
  }

  /**
   * Get component details
   */
  async getComponent(componentType: string): Promise<Component> {
    return this.request<Component>(`/registry/components/${componentType}`);
  }

  /**
   * List component categories
   */
  async listCategories(): Promise<string[]> {
    const response = await this.request<{ categories: string[] }>('/registry/components');
    return response.categories;
  }

  // ============================================
  // Health & Info
  // ============================================

  /**
   * Check if the server is healthy
   */
  async health(): Promise<{ status: string; version: string }> {
    return this.request('/health');
  }

  /**
   * Get server info
   */
  async info(): Promise<Record<string, unknown>> {
    return this.request('/info');
  }
}

// Factory function for convenience
export function createClient(config?: FlowMasonConfig): FlowMason {
  return new FlowMason(config);
}

// Default instance (lazy initialization)
let defaultClient: FlowMason | null = null;

export function getDefaultClient(): FlowMason {
  if (!defaultClient) {
    defaultClient = new FlowMason();
  }
  return defaultClient;
}

export function setDefaultClient(client: FlowMason): void {
  defaultClient = client;
}
