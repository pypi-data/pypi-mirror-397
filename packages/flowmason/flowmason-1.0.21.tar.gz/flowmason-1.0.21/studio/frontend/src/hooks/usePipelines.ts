/**
 * Hooks for pipeline management.
 */

import { useState, useEffect, useCallback } from 'react';
import { pipelines, runs } from '../services/api';
import type { Pipeline, PipelineRun, PaginatedResponse } from '../types';

export function usePipelines(params?: {
  category?: string;
  page?: number;
  page_size?: number;
}) {
  const [data, setData] = useState<PaginatedResponse<Pipeline> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPipelines = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await pipelines.list(params);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch pipelines');
    } finally {
      setLoading(false);
    }
  }, [params?.category, params?.page, params?.page_size]);

  useEffect(() => {
    fetchPipelines();
  }, [fetchPipelines]);

  return {
    pipelines: data?.items ?? [],
    total: data?.total ?? 0,
    loading,
    error,
    refetch: fetchPipelines,
  };
}

export function usePipeline(id: string | null) {
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPipeline = useCallback(async () => {
    if (!id) {
      setPipeline(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await pipelines.get(id);
      setPipeline(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch pipeline');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchPipeline();
  }, [fetchPipeline]);

  const updatePipeline = useCallback(
    async (updates: Partial<Pipeline>) => {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const result = await pipelines.update(id, updates);
        setPipeline(result);
        return result;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update pipeline');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [id]
  );

  return { pipeline, loading, error, refetch: fetchPipeline, updatePipeline };
}

export function usePipelineRuns(pipelineId?: string) {
  const [data, setData] = useState<PaginatedResponse<PipelineRun> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRuns = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await runs.list({ pipeline_id: pipelineId });
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch runs');
    } finally {
      setLoading(false);
    }
  }, [pipelineId]);

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  return {
    runs: data?.items ?? [],
    total: data?.total ?? 0,
    loading,
    error,
    refetch: fetchRuns,
  };
}

export function useRun(runId: string | null) {
  const [run, setRun] = useState<PipelineRun | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRun = useCallback(async () => {
    if (!runId) {
      setRun(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await runs.getTrace(runId);
      setRun(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch run');
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    fetchRun();
  }, [fetchRun]);

  return { run, loading, error, refetch: fetchRun };
}
