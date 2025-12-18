/**
 * FlowMason API Service
 *
 * Handles communication with FlowMason Studio backend.
 */

import {
  Pipeline,
  PipelineRun,
  DashboardStats,
  ServerConfig,
  ApiResponse,
} from '../types';

class FlowMasonAPI {
  private baseUrl: string = '';
  private apiKey: string = '';

  /**
   * Configure the API client.
   */
  configure(config: ServerConfig): void {
    this.baseUrl = config.url.replace(/\/$/, '');
    this.apiKey = config.apiKey;
  }

  /**
   * Check if API is configured.
   */
  isConfigured(): boolean {
    return !!this.baseUrl && !!this.apiKey;
  }

  /**
   * Make an API request.
   */
  private async request<T>(
    method: string,
    endpoint: string,
    body?: unknown,
  ): Promise<ApiResponse<T>> {
    if (!this.isConfigured()) {
      return { error: 'API not configured', status: 0 };
    }

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method,
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || data.message || 'Request failed',
          status: response.status,
        };
      }

      return { data, status: response.status };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // Health & Status

  async checkHealth(): Promise<ApiResponse<{ status: string }>> {
    return this.request('GET', '/api/v1/health');
  }

  // Dashboard

  async getDashboard(): Promise<ApiResponse<DashboardStats>> {
    return this.request('GET', '/api/v1/dashboard');
  }

  // Pipelines

  async listPipelines(): Promise<ApiResponse<Pipeline[]>> {
    return this.request('GET', '/api/v1/pipelines');
  }

  async getPipeline(name: string): Promise<ApiResponse<Pipeline>> {
    return this.request('GET', `/api/v1/pipelines/${encodeURIComponent(name)}`);
  }

  // Execution

  async runPipeline(
    name: string,
    inputs: Record<string, unknown> = {},
  ): Promise<ApiResponse<PipelineRun>> {
    return this.request('POST', `/api/v1/execute/${encodeURIComponent(name)}`, {
      inputs,
    });
  }

  async cancelRun(runId: string): Promise<ApiResponse<{ cancelled: boolean }>> {
    return this.request('POST', `/api/v1/runs/${runId}/cancel`);
  }

  // Runs

  async listRuns(
    pipelineName?: string,
    limit: number = 20,
  ): Promise<ApiResponse<PipelineRun[]>> {
    let endpoint = `/api/v1/runs?limit=${limit}`;
    if (pipelineName) {
      endpoint += `&pipeline=${encodeURIComponent(pipelineName)}`;
    }
    return this.request('GET', endpoint);
  }

  async getRun(runId: string): Promise<ApiResponse<PipelineRun>> {
    return this.request('GET', `/api/v1/runs/${runId}`);
  }

  // WebSocket for real-time updates

  connectWebSocket(
    runId: string,
    onMessage: (data: unknown) => void,
    onError?: (error: Event) => void,
  ): WebSocket | null {
    if (!this.isConfigured()) {
      return null;
    }

    const wsUrl = this.baseUrl.replace(/^http/, 'ws');
    const ws = new WebSocket(`${wsUrl}/api/v1/ws/runs/${runId}`);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch {
        console.error('Failed to parse WebSocket message');
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    };

    return ws;
  }

  // Favorites (stored locally but synced with server if supported)

  async getFavorites(): Promise<ApiResponse<string[]>> {
    return this.request('GET', '/api/v1/user/favorites');
  }

  async addFavorite(pipelineName: string): Promise<ApiResponse<{ added: boolean }>> {
    return this.request('POST', '/api/v1/user/favorites', {
      pipeline: pipelineName,
    });
  }

  async removeFavorite(pipelineName: string): Promise<ApiResponse<{ removed: boolean }>> {
    return this.request('DELETE', `/api/v1/user/favorites/${encodeURIComponent(pipelineName)}`);
  }
}

// Export singleton instance
export const api = new FlowMasonAPI();

export default api;
