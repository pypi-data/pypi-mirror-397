/**
 * FlowMason React Hooks
 */

import { useState, useCallback, useEffect, useRef, useContext, createContext } from 'react';
import type { ReactNode } from 'react';
import { FlowMasonClient, getClient } from './client';
import type {
  FlowMasonConfig,
  PipelineInput,
  PipelineResult,
  Pipeline,
  Component,
  RunOptions,
  PipelineProgress,
  PipelineStatus,
  UsePipelineReturn,
  UsePipelinesReturn,
  UseComponentsReturn,
  UseRunHistoryReturn,
} from './types';

// Context for FlowMason client
const FlowMasonContext = createContext<FlowMasonClient | null>(null);

export interface FlowMasonProviderProps {
  config?: FlowMasonConfig;
  client?: FlowMasonClient;
  children: ReactNode;
}

/**
 * Provider component for FlowMason client
 */
export function FlowMasonProvider({
  config,
  client,
  children,
}: FlowMasonProviderProps): JSX.Element {
  const clientInstance = client || new FlowMasonClient(config);

  return (
    <FlowMasonContext.Provider value={clientInstance}>
      {children}
    </FlowMasonContext.Provider>
  ) as JSX.Element;
}

/**
 * Get the FlowMason client from context
 */
export function useFlowMasonClient(): FlowMasonClient {
  const client = useContext(FlowMasonContext);
  return client || getClient();
}

/**
 * Hook for running a pipeline
 */
export function usePipeline(pipelineId: string): UsePipelineReturn {
  const client = useFlowMasonClient();
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [status, setStatus] = useState<PipelineStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<PipelineProgress | null>(null);
  const cleanupRef = useRef<(() => void) | null>(null);

  const run = useCallback(
    async (input: PipelineInput, options: RunOptions = {}): Promise<PipelineResult> => {
      setStatus('running');
      setError(null);
      setProgress({
        completedStages: [],
        totalStages: 0,
        percentComplete: 0,
      });

      try {
        const runResult = await client.runPipeline(pipelineId, input, options);

        // Stream updates if not async
        if (!options.async && runResult.runId) {
          cleanupRef.current = client.streamExecution(runResult.runId, {
            onStageStart: (stage) => {
              setProgress((prev) => ({
                ...prev!,
                currentStage: stage.stageId,
                currentStageName: stage.stageName,
              }));
            },
            onStageComplete: (stage) => {
              setProgress((prev) => {
                const completed = [...(prev?.completedStages || []), stage.stageId];
                return {
                  ...prev!,
                  completedStages: completed,
                  percentComplete: prev?.totalStages
                    ? Math.round((completed.length / prev.totalStages) * 100)
                    : 0,
                };
              });
            },
            onComplete: (finalResult) => {
              setResult(finalResult);
              setStatus('success');
              setProgress(null);
            },
            onError: (err) => {
              setError(err.message);
              setStatus('error');
            },
          });
        } else {
          setResult(runResult);
          setStatus(runResult.success ? 'success' : 'error');
          if (!runResult.success) {
            setError(runResult.error || 'Pipeline failed');
          }
        }

        return runResult;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setError(message);
        setStatus('error');
        throw err;
      }
    },
    [client, pipelineId]
  );

  const cancel = useCallback(() => {
    client.cancel();
    cleanupRef.current?.();
    setStatus('idle');
    setProgress(null);
  }, [client]);

  const reset = useCallback(() => {
    setResult(null);
    setStatus('idle');
    setError(null);
    setProgress(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cleanupRef.current?.();
    };
  }, []);

  return {
    run,
    result,
    status,
    error,
    isLoading: status === 'loading',
    isRunning: status === 'running',
    isSuccess: status === 'success',
    isError: status === 'error',
    progress,
    cancel,
    reset,
  };
}

/**
 * Hook for running a pipeline by name
 */
export function usePipelineByName(
  name: string,
  version?: string
): UsePipelineReturn {
  const client = useFlowMasonClient();
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [status, setStatus] = useState<PipelineStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<PipelineProgress | null>(null);

  const run = useCallback(
    async (input: PipelineInput, options: RunOptions = {}): Promise<PipelineResult> => {
      setStatus('running');
      setError(null);

      try {
        const runResult = await client.runPipelineByName(name, input, {
          ...options,
          version,
        });
        setResult(runResult);
        setStatus(runResult.success ? 'success' : 'error');
        if (!runResult.success) {
          setError(runResult.error || 'Pipeline failed');
        }
        return runResult;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error';
        setError(message);
        setStatus('error');
        throw err;
      }
    },
    [client, name, version]
  );

  const cancel = useCallback(() => {
    client.cancel();
    setStatus('idle');
  }, [client]);

  const reset = useCallback(() => {
    setResult(null);
    setStatus('idle');
    setError(null);
    setProgress(null);
  }, []);

  return {
    run,
    result,
    status,
    error,
    isLoading: status === 'loading',
    isRunning: status === 'running',
    isSuccess: status === 'success',
    isError: status === 'error',
    progress,
    cancel,
    reset,
  };
}

/**
 * Hook for listing pipelines
 */
export function usePipelines(options: {
  status?: string;
  category?: string;
  autoFetch?: boolean;
} = {}): UsePipelinesReturn {
  const client = useFlowMasonClient();
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await client.listPipelines({
        status: options.status,
        category: options.category,
      });
      setPipelines(response.pipelines);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [client, options.status, options.category]);

  useEffect(() => {
    if (options.autoFetch !== false) {
      refresh();
    }
  }, [refresh, options.autoFetch]);

  return {
    pipelines,
    isLoading,
    error,
    refresh,
  };
}

/**
 * Hook for getting a single pipeline
 */
export function usePipelineDetails(pipelineId: string): {
  pipeline: Pipeline | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
} {
  const client = useFlowMasonClient();
  const [pipeline, setPipeline] = useState<Pipeline | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await client.getPipeline(pipelineId);
      setPipeline(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [client, pipelineId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    pipeline,
    isLoading,
    error,
    refresh,
  };
}

/**
 * Hook for listing components
 */
export function useComponents(options: {
  category?: string;
  kind?: 'node' | 'operator';
  autoFetch?: boolean;
} = {}): UseComponentsReturn {
  const client = useFlowMasonClient();
  const [components, setComponents] = useState<Component[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await client.listComponents({
        category: options.category,
        kind: options.kind,
      });
      setComponents(response.components);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [client, options.category, options.kind]);

  useEffect(() => {
    if (options.autoFetch !== false) {
      refresh();
    }
  }, [refresh, options.autoFetch]);

  const filterByCategory = useCallback(
    (category: string) => components.filter((c) => c.category === category),
    [components]
  );

  const filterByKind = useCallback(
    (kind: 'node' | 'operator') => components.filter((c) => c.componentKind === kind),
    [components]
  );

  return {
    components,
    isLoading,
    error,
    filterByCategory,
    filterByKind,
    refresh,
  };
}

/**
 * Hook for run history
 */
export function useRunHistory(options: {
  pipelineId?: string;
  limit?: number;
  autoFetch?: boolean;
} = {}): UseRunHistoryReturn {
  const client = useFlowMasonClient();
  const [runs, setRuns] = useState<PipelineResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await client.listRuns({
        pipelineId: options.pipelineId,
        limit: options.limit,
      });
      setRuns(response.runs);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [client, options.pipelineId, options.limit]);

  useEffect(() => {
    if (options.autoFetch !== false) {
      refresh();
    }
  }, [refresh, options.autoFetch]);

  const getRun = useCallback(
    async (runId: string): Promise<PipelineResult | null> => {
      try {
        return await client.getRunStatus(runId);
      } catch {
        return null;
      }
    },
    [client]
  );

  return {
    runs,
    isLoading,
    error,
    getRun,
    refresh,
  };
}

/**
 * Hook for streaming pipeline execution
 */
export function useStreamingPipeline(pipelineId: string): UsePipelineReturn & {
  stages: Record<string, 'pending' | 'running' | 'completed' | 'failed'>;
} {
  const basePipeline = usePipeline(pipelineId);
  const [stages, setStages] = useState<Record<string, 'pending' | 'running' | 'completed' | 'failed'>>({});

  const run = useCallback(
    async (input: PipelineInput, options: RunOptions = {}) => {
      setStages({});
      return basePipeline.run(input, options);
    },
    [basePipeline]
  );

  return {
    ...basePipeline,
    run,
    stages,
  };
}
