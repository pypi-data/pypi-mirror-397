/**
 * FlowMason API Client
 *
 * Handles all API communication with the FlowMason backend.
 */

import type {
  ComponentInfo,
  Pipeline,
  PipelineRun,
  RegistryStats,
  PaginatedResponse,
  AppSettingsResponse,
  ProviderSettingsResponse,
  ProviderTestResponse,
  LogListResponse,
  LogConfigResponse,
  LogStatsResponse,
  BackendLogLevel,
  TestPipelineResponse,
  PublishPipelineResponse,
  UnpublishPipelineResponse,
} from '../types';

const API_BASE = '/api/v1';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(
      error.detail || `Request failed: ${response.statusText}`,
      response.status,
      error
    );
  }

  return response.json();
}

// Registry API
export const registry = {
  async listComponents(params?: {
    category?: string;
    kind?: 'node' | 'operator';
  }): Promise<ComponentInfo[]> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set('category', params.category);
    if (params?.kind) searchParams.set('kind', params.kind);

    const query = searchParams.toString();
    const response = await request<{ components: ComponentInfo[]; total: number; categories: string[] }>(
      `/registry/components${query ? `?${query}` : ''}`
    );
    return response.components;
  },

  async getComponent(type: string): Promise<ComponentInfo> {
    return request<ComponentInfo>(`/registry/components/${type}`);
  },

  async getStats(): Promise<RegistryStats> {
    return request<RegistryStats>('/registry/stats');
  },

  async refresh(): Promise<{ message: string }> {
    return request<{ message: string }>('/registry/refresh', {
      method: 'POST',
    });
  },

  async deployPackage(file: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('package', file);

    const response = await fetch(`${API_BASE}/registry/deploy`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        error.detail || 'Deploy failed',
        response.status,
        error
      );
    }

    return response.json();
  },

  async unregister(type: string): Promise<{ message: string }> {
    return request<{ message: string }>(`/registry/components/${type}`, {
      method: 'DELETE',
    });
  },
};

// Pipelines API
export const pipelines = {
  async list(params?: {
    category?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Pipeline>> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set('category', params.category);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.page_size)
      searchParams.set('page_size', params.page_size.toString());

    const query = searchParams.toString();
    return request<PaginatedResponse<Pipeline>>(
      `/pipelines${query ? `?${query}` : ''}`
    );
  },

  async get(id: string): Promise<Pipeline> {
    return request<Pipeline>(`/pipelines/${id}`);
  },

  async create(
    pipeline: Omit<Pipeline, 'id' | 'created_at' | 'updated_at'>
  ): Promise<Pipeline> {
    return request<Pipeline>('/pipelines', {
      method: 'POST',
      body: JSON.stringify(pipeline),
    });
  },

  async update(
    id: string,
    pipeline: Partial<Pipeline>
  ): Promise<Pipeline> {
    return request<Pipeline>(`/pipelines/${id}`, {
      method: 'PUT',
      body: JSON.stringify(pipeline),
    });
  },

  async delete(id: string): Promise<{ message: string }> {
    return request<{ message: string }>(`/pipelines/${id}`, {
      method: 'DELETE',
    });
  },

  async clone(
    id: string,
    newName?: string
  ): Promise<Pipeline> {
    return request<Pipeline>(`/pipelines/${id}/clone`, {
      method: 'POST',
      body: JSON.stringify({ new_name: newName }),
    });
  },

  async validate(id: string): Promise<{ valid: boolean; errors: string[] }> {
    return request<{ valid: boolean; errors: string[] }>(
      `/pipelines/${id}/validate`,
      { method: 'POST' }
    );
  },

  async run(
    id: string,
    inputs: Record<string, unknown>,
    providerOverrides?: Record<string, { provider?: string; model?: string; temperature?: number; max_tokens?: number }>
  ): Promise<PipelineRun> {
    return request<PipelineRun>(`/pipelines/${id}/run`, {
      method: 'POST',
      body: JSON.stringify({
        inputs,
        provider_overrides: providerOverrides,
      }),
    });
  },

  async test(
    id: string,
    sampleInput?: Record<string, unknown>
  ): Promise<TestPipelineResponse> {
    return request<TestPipelineResponse>(`/pipelines/${id}/test`, {
      method: 'POST',
      body: JSON.stringify(sampleInput ? { sample_input: sampleInput } : {}),
    });
  },

  async publish(
    id: string,
    testRunId: string
  ): Promise<PublishPipelineResponse> {
    return request<PublishPipelineResponse>(`/pipelines/${id}/publish`, {
      method: 'POST',
      body: JSON.stringify({ test_run_id: testRunId }),
    });
  },

  async unpublish(id: string): Promise<UnpublishPipelineResponse> {
    return request<UnpublishPipelineResponse>(`/pipelines/${id}/unpublish`, {
      method: 'POST',
    });
  },
};

// Runs API
export const runs = {
  async list(params?: {
    pipeline_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<PipelineRun>> {
    const searchParams = new URLSearchParams();
    if (params?.pipeline_id)
      searchParams.set('pipeline_id', params.pipeline_id);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.page_size)
      searchParams.set('page_size', params.page_size.toString());

    const query = searchParams.toString();
    return request<PaginatedResponse<PipelineRun>>(
      `/runs${query ? `?${query}` : ''}`
    );
  },

  async get(runId: string): Promise<PipelineRun> {
    return request<PipelineRun>(`/runs/${runId}`);
  },

  async getTrace(runId: string): Promise<PipelineRun> {
    return request<PipelineRun>(`/runs/${runId}/trace`);
  },

  async cancel(runId: string): Promise<{ message: string }> {
    return request<{ message: string }>(`/runs/${runId}/cancel`, {
      method: 'POST',
    });
  },

  async delete(runId: string): Promise<{ message: string }> {
    return request<{ message: string }>(`/runs/${runId}`, {
      method: 'DELETE',
    });
  },
};

// Settings API
export const settings = {
  async get(): Promise<AppSettingsResponse> {
    return request<AppSettingsResponse>('/settings');
  },

  async update(params: {
    default_provider?: string;
    theme?: string;
    auto_save?: boolean;
  }): Promise<AppSettingsResponse> {
    return request<AppSettingsResponse>('/settings', {
      method: 'PUT',
      body: JSON.stringify(params),
    });
  },

  async getProviderSettings(provider: string): Promise<ProviderSettingsResponse> {
    return request<ProviderSettingsResponse>(`/settings/providers/${provider}`);
  },

  async setProviderKey(
    provider: string,
    apiKey: string,
    defaultModel?: string
  ): Promise<ProviderSettingsResponse> {
    return request<ProviderSettingsResponse>(`/settings/providers/${provider}/key`, {
      method: 'PUT',
      body: JSON.stringify({
        api_key: apiKey,
        default_model: defaultModel,
      }),
    });
  },

  async removeProviderKey(provider: string): Promise<{ removed: boolean }> {
    return request<{ removed: boolean }>(`/settings/providers/${provider}/key`, {
      method: 'DELETE',
    });
  },

  async testProvider(provider: string): Promise<ProviderTestResponse> {
    return request<ProviderTestResponse>(`/settings/providers/${provider}/test`, {
      method: 'POST',
    });
  },

  async restartBackend(): Promise<{ message: string; status: string }> {
    return request<{ message: string; status: string }>('/settings/restart', {
      method: 'POST',
    });
  },
};

// Logs API
export const logs = {
  async list(params?: {
    limit?: number;
    offset?: number;
    level?: BackendLogLevel;
    category?: string;
    search?: string;
    since?: string;
  }): Promise<LogListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.offset) searchParams.set('offset', params.offset.toString());
    if (params?.level) searchParams.set('level', params.level);
    if (params?.category) searchParams.set('category', params.category);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.since) searchParams.set('since', params.since);

    const query = searchParams.toString();
    return request<LogListResponse>(`/logs${query ? `?${query}` : ''}`);
  },

  async getConfig(): Promise<LogConfigResponse> {
    return request<LogConfigResponse>('/logs/config');
  },

  async updateConfig(params: {
    global_level?: BackendLogLevel;
    category_levels?: Record<string, BackendLogLevel>;
    max_entries?: number;
    enabled?: boolean;
  }): Promise<LogConfigResponse> {
    return request<LogConfigResponse>('/logs/config', {
      method: 'PUT',
      body: JSON.stringify(params),
    });
  },

  async clear(): Promise<{ message: string; cleared: boolean }> {
    return request<{ message: string; cleared: boolean }>('/logs', {
      method: 'DELETE',
    });
  },

  async getStats(): Promise<LogStatsResponse> {
    return request<LogStatsResponse>('/logs/stats');
  },

  async getLevels(): Promise<{ levels: string[]; categories: string[] }> {
    return request<{ levels: string[]; categories: string[] }>('/logs/levels');
  },
};

// Templates API
export interface TemplateSummary {
  id: string;
  name: string;
  description: string;
  version: string;
  stage_count: number;
  category: string;
  tags: string[];
  difficulty: string;
  use_cases: string[];
  source: 'builtin' | 'user';
  is_template: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface TemplateDetail extends TemplateSummary {
  stages: unknown[];
  input_schema: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
  output_stage_id?: string;
}

export interface TemplatesListResponse {
  templates: TemplateSummary[];
  total: number;
  by_category: Record<string, TemplateSummary[]>;
  categories: string[];
}

export interface CategoryInfo {
  id: string;
  name: string;
  icon: string;
  count: number;
}

export const templates = {
  async list(params?: {
    category?: string;
    difficulty?: string;
  }): Promise<TemplatesListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set('category', params.category);
    if (params?.difficulty) searchParams.set('difficulty', params.difficulty);

    const query = searchParams.toString();
    return request<TemplatesListResponse>(
      `/templates${query ? `?${query}` : ''}`
    );
  },

  async get(id: string): Promise<TemplateDetail> {
    return request<TemplateDetail>(`/templates/${id}`);
  },

  async instantiate(id: string, name?: string): Promise<Pipeline> {
    const searchParams = new URLSearchParams();
    if (name) searchParams.set('name', name);
    const query = searchParams.toString();
    return request<Pipeline>(`/templates/${id}/instantiate${query ? `?${query}` : ''}`, {
      method: 'POST',
    });
  },

  async listCategories(): Promise<{ categories: CategoryInfo[]; total: number }> {
    return request<{ categories: CategoryInfo[]; total: number }>('/templates/categories/list');
  },
};

// Health check
export async function healthCheck(): Promise<{ status: string }> {
  return request<{ status: string }>('/health');
}

export { ApiError };
