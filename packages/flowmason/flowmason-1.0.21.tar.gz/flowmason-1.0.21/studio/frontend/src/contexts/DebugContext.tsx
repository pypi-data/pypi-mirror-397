/**
 * Debug Context
 *
 * Centralized state management for pipeline debugging.
 * Provides a unified interface for:
 * - Execution state and control (run, pause, step, stop)
 * - Breakpoint management
 * - Log collection and filtering
 * - Variable inspection
 * - Network call monitoring
 * - Execution trace
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useCallback,
  useRef,
  useEffect,
  useMemo,
} from 'react';
import type {
  DebugMode,
  DebugState,
  LogEntry,
  LogLevel,
  Breakpoint,
  VariableInfo,
  ExecutionStep,
  NetworkCall,
  PipelineRun,
  PipelineStage,
  StageTrace,
} from '../types';
import { runs as runsApi, pipelines as pipelinesApi } from '../services/api';
import {
  getWebSocket,
  ExecutionWebSocket,
  ConnectionStatus,
} from '../services/websocket';

// Extended execution state for canvas visualization
export interface StageExecutionState {
  status: 'idle' | 'pending' | 'running' | 'completed' | 'success' | 'failed';
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
  startTime?: number;
  endTime?: number;
  duration?: number;
}

// Debug action types
type DebugAction =
  | { type: 'SET_MODE'; mode: DebugMode }
  | { type: 'SET_CURRENT_STAGE'; stageId: string | null }
  | { type: 'SET_RUN'; run: PipelineRun | null }
  | { type: 'UPDATE_RUN'; run: PipelineRun }
  | { type: 'ADD_LOG'; log: LogEntry }
  | { type: 'ADD_LOGS'; logs: LogEntry[] }
  | { type: 'CLEAR_LOGS' }
  | { type: 'ADD_BREAKPOINT'; breakpoint: Breakpoint }
  | { type: 'REMOVE_BREAKPOINT'; id: string }
  | { type: 'TOGGLE_BREAKPOINT'; id: string }
  | { type: 'UPDATE_BREAKPOINT'; id: string; updates: Partial<Breakpoint> }
  | { type: 'CLEAR_BREAKPOINTS' }
  | { type: 'SET_VARIABLE'; name: string; info: VariableInfo }
  | { type: 'SET_VARIABLES'; variables: Record<string, VariableInfo> }
  | { type: 'CLEAR_VARIABLES' }
  | { type: 'ADD_EXECUTION_STEP'; step: ExecutionStep }
  | { type: 'UPDATE_EXECUTION_STEP'; stepId: string; updates: Partial<ExecutionStep> }
  | { type: 'SET_EXECUTION_STEPS'; steps: ExecutionStep[] }
  | { type: 'CLEAR_EXECUTION_TRACE' }
  | { type: 'ADD_NETWORK_CALL'; call: NetworkCall }
  | { type: 'UPDATE_NETWORK_CALL'; id: string; updates: Partial<NetworkCall> }
  | { type: 'CLEAR_NETWORK_CALLS' }
  | { type: 'SET_STAGE_EXECUTION_STATES'; states: Record<string, StageExecutionState> }
  | { type: 'UPDATE_STAGE_EXECUTION_STATE'; stageId: string; state: Partial<StageExecutionState> }
  | { type: 'SET_WS_CONNECTION_STATUS'; status: ConnectionStatus }
  | { type: 'BATCH_UPDATE_EXECUTION_STATE'; payload: BatchUpdatePayload }
  | { type: 'RESET' };

// Batch update payload for atomic state updates
interface BatchUpdatePayload {
  stageStates?: Record<string, StageExecutionState>;
  executionSteps?: ExecutionStep[];
  variables?: Record<string, VariableInfo>;
  networkCalls?: NetworkCall[];
  currentStageId?: string | null;
  mode?: DebugMode;
  logs?: LogEntry[];
}

// Extended debug state
interface ExtendedDebugState extends DebugState {
  currentRun: PipelineRun | null;
  stageExecutionStates: Record<string, StageExecutionState>;
  logCounts: { debug: number; info: number; warn: number; error: number };
  wsConnectionStatus: ConnectionStatus;
  isUsingPollingFallback: boolean;
}

const initialState: ExtendedDebugState = {
  mode: 'stopped',
  currentStageId: null,
  breakpoints: [],
  executionTrace: [],
  variables: {},
  logs: [],
  networkCalls: [],
  startTime: null,
  pausedAt: null,
  currentRun: null,
  stageExecutionStates: {},
  logCounts: { debug: 0, info: 0, warn: 0, error: 0 },
  wsConnectionStatus: 'disconnected',
  isUsingPollingFallback: false,
};

function debugReducer(state: ExtendedDebugState, action: DebugAction): ExtendedDebugState {
  switch (action.type) {
    case 'SET_MODE':
      return {
        ...state,
        mode: action.mode,
        startTime: action.mode === 'running' ? new Date().toISOString() : state.startTime,
        pausedAt: action.mode === 'paused' ? new Date().toISOString() : null,
      };

    case 'SET_CURRENT_STAGE':
      return { ...state, currentStageId: action.stageId };

    case 'SET_RUN':
      return {
        ...state,
        currentRun: action.run,
        stageExecutionStates: {},
      };

    case 'UPDATE_RUN':
      return { ...state, currentRun: action.run };

    case 'ADD_LOG': {
      const newLogs = [...state.logs, action.log];
      const newCounts = { ...state.logCounts };
      newCounts[action.log.level]++;
      return { ...state, logs: newLogs, logCounts: newCounts };
    }

    case 'ADD_LOGS': {
      const newLogs = [...state.logs, ...action.logs];
      const newCounts = { ...state.logCounts };
      action.logs.forEach((log) => {
        newCounts[log.level]++;
      });
      return { ...state, logs: newLogs, logCounts: newCounts };
    }

    case 'CLEAR_LOGS':
      return {
        ...state,
        logs: [],
        logCounts: { debug: 0, info: 0, warn: 0, error: 0 },
      };

    case 'ADD_BREAKPOINT':
      return {
        ...state,
        breakpoints: [...state.breakpoints, action.breakpoint],
      };

    case 'REMOVE_BREAKPOINT':
      return {
        ...state,
        breakpoints: state.breakpoints.filter((bp) => bp.id !== action.id),
      };

    case 'TOGGLE_BREAKPOINT':
      return {
        ...state,
        breakpoints: state.breakpoints.map((bp) =>
          bp.id === action.id ? { ...bp, enabled: !bp.enabled } : bp
        ),
      };

    case 'UPDATE_BREAKPOINT':
      return {
        ...state,
        breakpoints: state.breakpoints.map((bp) =>
          bp.id === action.id ? { ...bp, ...action.updates } : bp
        ),
      };

    case 'CLEAR_BREAKPOINTS':
      return { ...state, breakpoints: [] };

    case 'SET_VARIABLE':
      return {
        ...state,
        variables: { ...state.variables, [action.name]: action.info },
      };

    case 'SET_VARIABLES':
      return { ...state, variables: action.variables };

    case 'CLEAR_VARIABLES':
      return { ...state, variables: {} };

    case 'ADD_EXECUTION_STEP':
      return {
        ...state,
        executionTrace: [...state.executionTrace, action.step],
      };

    case 'UPDATE_EXECUTION_STEP':
      return {
        ...state,
        executionTrace: state.executionTrace.map((step) =>
          step.stepId === action.stepId ? { ...step, ...action.updates } : step
        ),
      };

    case 'CLEAR_EXECUTION_TRACE':
      return { ...state, executionTrace: [] };

    case 'ADD_NETWORK_CALL':
      return {
        ...state,
        networkCalls: [...state.networkCalls, action.call],
      };

    case 'UPDATE_NETWORK_CALL':
      return {
        ...state,
        networkCalls: state.networkCalls.map((call) =>
          call.id === action.id ? { ...call, ...action.updates } : call
        ),
      };

    case 'CLEAR_NETWORK_CALLS':
      return { ...state, networkCalls: [] };

    case 'SET_STAGE_EXECUTION_STATES':
      return { ...state, stageExecutionStates: action.states };

    case 'UPDATE_STAGE_EXECUTION_STATE':
      return {
        ...state,
        stageExecutionStates: {
          ...state.stageExecutionStates,
          [action.stageId]: {
            ...state.stageExecutionStates[action.stageId],
            ...action.state,
          },
        },
      };

    case 'SET_EXECUTION_STEPS':
      return { ...state, executionTrace: action.steps };

    case 'SET_WS_CONNECTION_STATUS':
      return {
        ...state,
        wsConnectionStatus: action.status,
        isUsingPollingFallback: action.status !== 'connected' && state.currentRun !== null,
      };

    case 'BATCH_UPDATE_EXECUTION_STATE': {
      // Atomic batch update to prevent race conditions
      const { payload } = action;
      let newState = { ...state };

      if (payload.stageStates !== undefined) {
        newState.stageExecutionStates = payload.stageStates;
      }
      if (payload.executionSteps !== undefined) {
        newState.executionTrace = payload.executionSteps;
      }
      if (payload.variables !== undefined) {
        newState.variables = { ...state.variables, ...payload.variables };
      }
      if (payload.networkCalls !== undefined) {
        newState.networkCalls = [...state.networkCalls, ...payload.networkCalls];
      }
      if (payload.currentStageId !== undefined) {
        newState.currentStageId = payload.currentStageId;
      }
      if (payload.mode !== undefined) {
        newState.mode = payload.mode;
        if (payload.mode === 'paused') {
          newState.pausedAt = new Date().toISOString();
        } else if (payload.mode === 'running') {
          newState.pausedAt = null;
        }
      }
      if (payload.logs !== undefined) {
        newState.logs = [...state.logs, ...payload.logs];
        // Update log counts
        payload.logs.forEach((log) => {
          newState.logCounts = { ...newState.logCounts };
          newState.logCounts[log.level]++;
        });
      }

      return newState;
    }

    case 'RESET':
      return initialState;

    default:
      return state;
  }
}

// Context interface
interface DebugContextValue {
  state: ExtendedDebugState;

  // Execution control
  startExecution: (
    pipelineId: string,
    inputs: Record<string, unknown>,
    stages: PipelineStage[],
    providerOverrides?: Record<string, { provider?: string; model?: string; temperature?: number; max_tokens?: number }>
  ) => Promise<void>;
  pauseExecution: () => void;
  resumeExecution: () => void;
  stepExecution: () => void;
  stopExecution: () => Promise<void>;
  retryStage: (stageId: string) => Promise<void>;

  // Breakpoint management
  addBreakpoint: (stageId: string, condition?: string) => void;
  removeBreakpoint: (id: string) => void;
  toggleBreakpoint: (id: string) => void;
  updateBreakpoint: (id: string, updates: Partial<Breakpoint>) => void;
  clearBreakpoints: () => void;
  hasBreakpoint: (stageId: string) => boolean;

  // Logging
  addLog: (level: LogLevel, message: string, source?: string, stageId?: string, data?: Record<string, unknown>) => void;
  clearLogs: () => void;

  // Variables
  setVariable: (name: string, value: unknown, type: string, source: string) => void;
  clearVariables: () => void;

  // Execution trace
  clearExecutionTrace: () => void;

  // Network calls
  addNetworkCall: (call: Omit<NetworkCall, 'id' | 'timestamp'>) => string;
  updateNetworkCall: (id: string, updates: Partial<NetworkCall>) => void;
  clearNetworkCalls: () => void;

  // Stage execution states (for canvas visualization)
  getStageExecutionState: (stageId: string) => StageExecutionState | undefined;

  // Reset
  reset: () => void;
}

const DebugContext = createContext<DebugContextValue | null>(null);

// Hook to use debug context
export function useDebugContext() {
  const context = useContext(DebugContext);
  if (!context) {
    throw new Error('useDebugContext must be used within a DebugProvider');
  }
  return context;
}

// Provider component
interface DebugProviderProps {
  children: React.ReactNode;
}

export function DebugProvider({ children }: DebugProviderProps) {
  const [state, dispatch] = useReducer(debugReducer, initialState);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stagesRef = useRef<PipelineStage[]>([]);

  // FIX: Use ref for current run ID to avoid stale closure in pollRunStatus
  const currentRunIdRef = useRef<string | null>(null);
  const breakpointsRef = useRef(state.breakpoints);
  const modeRef = useRef(state.mode);

  // WebSocket ref
  const wsRef = useRef<ExecutionWebSocket | null>(null);
  const fallbackTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Keep refs in sync with state
  useEffect(() => {
    currentRunIdRef.current = state.currentRun?.id ?? null;
  }, [state.currentRun?.id]);

  useEffect(() => {
    breakpointsRef.current = state.breakpoints;
  }, [state.breakpoints]);

  useEffect(() => {
    modeRef.current = state.mode;
  }, [state.mode]);

  // Cleanup polling and WebSocket on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
      if (fallbackTimeoutRef.current) {
        clearTimeout(fallbackTimeoutRef.current);
      }
      if (wsRef.current) {
        const runId = currentRunIdRef.current;
        if (runId) {
          wsRef.current.unsubscribe(runId);
        }
      }
    };
  }, []);

  // Generate unique ID
  const generateId = useCallback(() => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // Add log entry
  const addLog = useCallback(
    (
      level: LogLevel,
      message: string,
      source?: string,
      stageId?: string,
      data?: Record<string, unknown>
    ) => {
      const log: LogEntry = {
        id: generateId(),
        level,
        message,
        timestamp: new Date().toISOString(),
        source,
        stageId,
        data,
      };
      dispatch({ type: 'ADD_LOG', log });
    },
    [generateId]
  );

  // Process stage trace into execution steps and stage states
  const processStageTrace = useCallback(
    (stages: StageTrace[], pipelineStages: PipelineStage[]) => {
      const newStates: Record<string, StageExecutionState> = {};
      const newSteps: ExecutionStep[] = [];

      // Initialize all stages as pending
      pipelineStages.forEach((stage) => {
        newStates[stage.id] = { status: 'pending' };
      });

      // Process trace
      stages.forEach((trace) => {
        const pipelineStage = pipelineStages.find((s) => s.id === trace.stage_id);

        // Update execution state
        newStates[trace.stage_id] = {
          status: trace.status === 'completed' ? 'success' : trace.status,
          input: trace.input as Record<string, unknown> | undefined,
          output: trace.output as Record<string, unknown> | undefined,
          error: trace.error,
          startTime: trace.started_at ? new Date(trace.started_at).getTime() : undefined,
          endTime: trace.completed_at ? new Date(trace.completed_at).getTime() : undefined,
          duration: trace.usage?.execution_time_ms,
        };

        // Create execution step
        const step: ExecutionStep = {
          stepId: `${trace.stage_id}-${Date.now()}`,
          stageId: trace.stage_id,
          stageName: pipelineStage?.name || trace.stage_id,
          componentType: trace.component_type,
          timestamp: trace.started_at || new Date().toISOString(),
          duration: trace.usage?.execution_time_ms,
          input: trace.input as Record<string, unknown> | undefined,
          output: trace.output as Record<string, unknown> | undefined,
          status: trace.status,
          error: trace.error,
          logs: [],
        };

        newSteps.push(step);

        // Extract variables from output
        if (trace.output && typeof trace.output === 'object') {
          Object.entries(trace.output).forEach(([key, value]) => {
            dispatch({
              type: 'SET_VARIABLE',
              name: `${trace.stage_id}.${key}`,
              info: {
                name: `${trace.stage_id}.${key}`,
                value,
                type: typeof value,
                source: trace.stage_id,
                timestamp: new Date().toISOString(),
                changed: true,
              },
            });
          });
        }

        // Generate network call for LLM stages
        if (trace.usage && trace.usage.total_tokens > 0) {
          const networkCall: NetworkCall = {
            id: generateId(),
            type: 'llm',
            provider: 'unknown', // Would need backend to provide this
            model: 'unknown',
            timestamp: trace.started_at || new Date().toISOString(),
            duration: trace.usage.execution_time_ms,
            status: trace.status === 'failed' ? 'error' : 'success',
            tokens: {
              input: trace.usage.prompt_tokens,
              output: trace.usage.completion_tokens,
              total: trace.usage.total_tokens,
            },
            error: trace.error,
          };
          dispatch({ type: 'ADD_NETWORK_CALL', call: networkCall });
        }

        // Add log for stage completion/failure
        if (trace.status === 'completed') {
          addLog('info', `Stage "${pipelineStage?.name || trace.stage_id}" completed`, 'executor', trace.stage_id);
        } else if (trace.status === 'failed') {
          addLog('error', `Stage "${pipelineStage?.name || trace.stage_id}" failed: ${trace.error}`, 'executor', trace.stage_id);
        }
      });

      dispatch({ type: 'SET_STAGE_EXECUTION_STATES', states: newStates });

      // Clear and add new execution steps
      dispatch({ type: 'CLEAR_EXECUTION_TRACE' });
      newSteps.forEach((step) => {
        dispatch({ type: 'ADD_EXECUTION_STEP', step });
      });
    },
    [addLog, generateId]
  );

  // Poll for run status - FIX: Use refs to avoid stale closure
  const pollRunStatus = useCallback(async () => {
    // FIX: Use ref instead of state to avoid stale closure
    const runId = currentRunIdRef.current;
    if (!runId) return;

    try {
      const updatedRun = await runsApi.get(runId);
      dispatch({ type: 'UPDATE_RUN', run: updatedRun });

      // Process trace
      if (updatedRun.trace?.stages) {
        processStageTrace(updatedRun.trace.stages, stagesRef.current);
      }

      // Check for breakpoints - FIX: Use refs instead of state
      if (modeRef.current === 'running' && updatedRun.trace?.stages) {
        const runningStage = updatedRun.trace.stages.find((s) => s.status === 'running');
        if (runningStage) {
          const breakpoint = breakpointsRef.current.find(
            (bp) => bp.stageId === runningStage.stage_id && bp.enabled
          );
          if (breakpoint) {
            dispatch({ type: 'SET_MODE', mode: 'paused' });
            dispatch({ type: 'SET_CURRENT_STAGE', stageId: runningStage.stage_id });
            dispatch({
              type: 'UPDATE_BREAKPOINT',
              id: breakpoint.id,
              updates: { hitCount: breakpoint.hitCount + 1 },
            });
            addLog('info', `Breakpoint hit at stage "${runningStage.stage_id}"`, 'debugger');
          }
        }
      }

      // Check if run completed
      if (updatedRun.status !== 'pending' && updatedRun.status !== 'running') {
        dispatch({ type: 'SET_MODE', mode: 'stopped' });

        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }

        if (updatedRun.status === 'completed') {
          addLog('info', 'Pipeline execution completed successfully', 'executor');
        } else if (updatedRun.status === 'failed') {
          addLog('error', `Pipeline execution failed: ${updatedRun.error}`, 'executor');
        } else if (updatedRun.status === 'cancelled') {
          addLog('warn', 'Pipeline execution was cancelled', 'executor');
        }
      }
    } catch (err) {
      addLog('error', `Failed to poll run status: ${err instanceof Error ? err.message : 'Unknown error'}`, 'debugger');
    }
    // FIX: Remove state dependencies since we use refs now
  }, [processStageTrace, addLog]);

  // Start execution
  const startExecution = useCallback(
    async (
      pipelineId: string,
      inputs: Record<string, unknown>,
      stages: PipelineStage[],
      providerOverrides?: Record<string, { provider?: string; model?: string; temperature?: number; max_tokens?: number }>
    ) => {
      // Store stages for later reference
      stagesRef.current = stages;

      // Reset state
      dispatch({ type: 'CLEAR_EXECUTION_TRACE' });
      dispatch({ type: 'CLEAR_VARIABLES' });
      dispatch({ type: 'CLEAR_NETWORK_CALLS' });

      // Initialize all stages as pending
      const initialStates: Record<string, StageExecutionState> = {};
      stages.forEach((stage) => {
        initialStates[stage.id] = { status: 'pending' };
      });
      dispatch({ type: 'SET_STAGE_EXECUTION_STATES', states: initialStates });

      // Set input variables
      Object.entries(inputs).forEach(([key, value]) => {
        dispatch({
          type: 'SET_VARIABLE',
          name: `input.${key}`,
          info: {
            name: `input.${key}`,
            value,
            type: typeof value,
            source: 'input',
            timestamp: new Date().toISOString(),
            changed: false,
          },
        });
      });

      addLog('info', 'Starting pipeline execution...', 'executor');
      dispatch({ type: 'SET_MODE', mode: 'running' });

      try {
        const run = await pipelinesApi.run(pipelineId, inputs, providerOverrides);
        dispatch({ type: 'SET_RUN', run });
        addLog('info', `Run started with ID: ${run.id}`, 'executor');

        // Try to use WebSocket for real-time updates
        const ws = getWebSocket();
        wsRef.current = ws;

        // Subscribe to run updates
        ws.subscribe(run.id);

        // Set up WebSocket event handler
        const unsubscribeEvent = ws.onEvent((message) => {
          if (message.run_id !== run.id) return;

          // Type-safe payload access
          const p = message.payload;

          switch (message.type) {
            case 'stage_started': {
              const stageId = p.stage_id as string;
              const stageName = p.stage_name as string | undefined;
              dispatch({
                type: 'UPDATE_STAGE_EXECUTION_STATE',
                stageId,
                state: { status: 'running', startTime: Date.now() },
              });
              dispatch({ type: 'SET_CURRENT_STAGE', stageId });
              addLog('info', `Stage "${stageName || stageId}" started`, 'executor', stageId);
              break;
            }
            case 'stage_completed': {
              const stageId = p.stage_id as string;
              const stageName = p.stage_name as string | undefined;
              const output = p.output as Record<string, unknown> | undefined;
              const durationMs = p.duration_ms as number | undefined;
              dispatch({
                type: 'UPDATE_STAGE_EXECUTION_STATE',
                stageId,
                state: {
                  status: 'success',
                  output,
                  endTime: Date.now(),
                  duration: durationMs,
                },
              });
              addLog('info', `Stage "${stageName || stageId}" completed`, 'executor', stageId);
              break;
            }
            case 'stage_failed': {
              const stageId = p.stage_id as string;
              const stageName = p.stage_name as string | undefined;
              const error = p.error as string;
              dispatch({
                type: 'UPDATE_STAGE_EXECUTION_STATE',
                stageId,
                state: { status: 'failed', error },
              });
              addLog('error', `Stage "${stageName || stageId}" failed: ${error}`, 'executor', stageId);
              break;
            }
            case 'execution_paused': {
              const stageId = p.stage_id as string;
              const stageName = p.stage_name as string | undefined;
              const reason = p.reason as string;
              dispatch({ type: 'SET_MODE', mode: 'paused' });
              dispatch({ type: 'SET_CURRENT_STAGE', stageId });
              addLog('info', `Execution paused at "${stageName || stageId}" (${reason})`, 'debugger');
              break;
            }
            case 'run_completed': {
              dispatch({ type: 'SET_MODE', mode: 'stopped' });
              addLog('info', 'Pipeline execution completed successfully', 'executor');
              // Cleanup
              ws.unsubscribe(run.id);
              unsubscribeEvent();
              if (pollingRef.current) {
                clearInterval(pollingRef.current);
                pollingRef.current = null;
              }
              break;
            }
            case 'run_failed': {
              const error = p.error as string;
              dispatch({ type: 'SET_MODE', mode: 'stopped' });
              addLog('error', `Pipeline execution failed: ${error}`, 'executor');
              // Cleanup
              ws.unsubscribe(run.id);
              unsubscribeEvent();
              if (pollingRef.current) {
                clearInterval(pollingRef.current);
                pollingRef.current = null;
              }
              break;
            }
          }
        });

        // Set up connection status handler
        ws.onStatusChange((status) => {
          dispatch({ type: 'SET_WS_CONNECTION_STATUS', status });
        });

        // Connect if not already connected
        if (!ws.isConnected) {
          ws.connect();
        }

        // Set up fallback to polling if WebSocket doesn't connect in 2 seconds
        fallbackTimeoutRef.current = setTimeout(() => {
          if (!ws.isConnected) {
            addLog('warn', 'WebSocket connection failed, using polling fallback', 'debugger');
            // Start polling as fallback
            if (!pollingRef.current) {
              pollingRef.current = setInterval(pollRunStatus, 500);
            }
          }
        }, 2000);

      } catch (err) {
        dispatch({ type: 'SET_MODE', mode: 'stopped' });
        addLog('error', `Failed to start execution: ${err instanceof Error ? err.message : 'Unknown error'}`, 'executor');
        throw err;
      }
    },
    [addLog, pollRunStatus]
  );

  // Pause execution - NOW sends real command to backend
  const pauseExecution = useCallback(async () => {
    const runId = currentRunIdRef.current;
    if (!runId) return;

    // Send via WebSocket if connected
    if (wsRef.current?.isConnected) {
      wsRef.current.pause(runId);
    }

    // Also update local state immediately for responsiveness
    dispatch({ type: 'SET_MODE', mode: 'paused' });
    addLog('info', 'Execution pause requested', 'debugger');

    // Call REST API as backup
    try {
      await fetch(`/api/v1/runs/${runId}/debug/pause`, { method: 'POST' });
    } catch (err) {
      addLog('warn', 'Failed to send pause command to backend', 'debugger');
    }
  }, [addLog]);

  // Resume execution - NOW sends real command to backend
  const resumeExecution = useCallback(async () => {
    const runId = currentRunIdRef.current;
    if (!runId) return;

    // Send via WebSocket if connected
    if (wsRef.current?.isConnected) {
      wsRef.current.resume(runId);
    }

    // Also update local state immediately for responsiveness
    dispatch({ type: 'SET_MODE', mode: 'running' });
    addLog('info', 'Execution resume requested', 'debugger');

    // Call REST API as backup
    try {
      await fetch(`/api/v1/runs/${runId}/debug/resume`, { method: 'POST' });
    } catch (err) {
      addLog('warn', 'Failed to send resume command to backend', 'debugger');
    }
  }, [addLog]);

  // Step execution - NOW sends real command to backend
  const stepExecution = useCallback(async () => {
    const runId = currentRunIdRef.current;
    if (!runId) return;

    // Send via WebSocket if connected
    if (wsRef.current?.isConnected) {
      wsRef.current.step(runId);
    }

    dispatch({ type: 'SET_MODE', mode: 'stepping' });
    addLog('info', 'Step execution requested', 'debugger');

    // Call REST API as backup
    try {
      await fetch(`/api/v1/runs/${runId}/debug/step`, { method: 'POST' });
    } catch (err) {
      addLog('warn', 'Failed to send step command to backend', 'debugger');
    }
  }, [addLog]);

  // Stop execution
  const stopExecution = useCallback(async () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }

    if (state.currentRun && (state.currentRun.status === 'pending' || state.currentRun.status === 'running')) {
      try {
        await runsApi.cancel(state.currentRun.id);
        addLog('info', 'Execution cancelled', 'executor');
      } catch (err) {
        addLog('error', `Failed to cancel execution: ${err instanceof Error ? err.message : 'Unknown error'}`, 'executor');
      }
    }

    dispatch({ type: 'SET_MODE', mode: 'stopped' });
  }, [state.currentRun, addLog]);

  // Retry stage (re-run from specific stage)
  const retryStage = useCallback(
    async (stageId: string) => {
      addLog('info', `Retrying stage "${stageId}"...`, 'debugger', stageId);
      // Note: This would require backend support for stage-level retry
      // For now, we'll just log the intent
      addLog('warn', 'Stage retry not yet implemented in backend', 'debugger', stageId);
    },
    [addLog]
  );

  // Breakpoint management
  const addBreakpoint = useCallback(
    (stageId: string, condition?: string) => {
      const breakpoint: Breakpoint = {
        id: generateId(),
        stageId,
        condition,
        enabled: true,
        hitCount: 0,
      };
      dispatch({ type: 'ADD_BREAKPOINT', breakpoint });
      addLog('info', `Breakpoint added at stage "${stageId}"${condition ? ` with condition: ${condition}` : ''}`, 'debugger');
    },
    [generateId, addLog]
  );

  const removeBreakpoint = useCallback(
    (id: string) => {
      dispatch({ type: 'REMOVE_BREAKPOINT', id });
    },
    []
  );

  const toggleBreakpoint = useCallback((id: string) => {
    dispatch({ type: 'TOGGLE_BREAKPOINT', id });
  }, []);

  const updateBreakpoint = useCallback((id: string, updates: Partial<Breakpoint>) => {
    dispatch({ type: 'UPDATE_BREAKPOINT', id, updates });
  }, []);

  const clearBreakpoints = useCallback(() => {
    dispatch({ type: 'CLEAR_BREAKPOINTS' });
    addLog('info', 'All breakpoints cleared', 'debugger');
  }, [addLog]);

  const hasBreakpoint = useCallback(
    (stageId: string) => {
      return state.breakpoints.some((bp) => bp.stageId === stageId);
    },
    [state.breakpoints]
  );

  // Clear functions
  const clearLogs = useCallback(() => {
    dispatch({ type: 'CLEAR_LOGS' });
  }, []);

  const setVariable = useCallback(
    (name: string, value: unknown, type: string, source: string) => {
      dispatch({
        type: 'SET_VARIABLE',
        name,
        info: {
          name,
          value,
          type,
          source,
          timestamp: new Date().toISOString(),
          changed: true,
        },
      });
    },
    []
  );

  const clearVariables = useCallback(() => {
    dispatch({ type: 'CLEAR_VARIABLES' });
  }, []);

  const clearExecutionTrace = useCallback(() => {
    dispatch({ type: 'CLEAR_EXECUTION_TRACE' });
  }, []);

  // Network call management
  const addNetworkCall = useCallback(
    (call: Omit<NetworkCall, 'id' | 'timestamp'>) => {
      const id = generateId();
      const fullCall: NetworkCall = {
        ...call,
        id,
        timestamp: new Date().toISOString(),
      };
      dispatch({ type: 'ADD_NETWORK_CALL', call: fullCall });
      return id;
    },
    [generateId]
  );

  const updateNetworkCall = useCallback((id: string, updates: Partial<NetworkCall>) => {
    dispatch({ type: 'UPDATE_NETWORK_CALL', id, updates });
  }, []);

  const clearNetworkCalls = useCallback(() => {
    dispatch({ type: 'CLEAR_NETWORK_CALLS' });
  }, []);

  // Get stage execution state
  const getStageExecutionState = useCallback(
    (stageId: string) => {
      return state.stageExecutionStates[stageId];
    },
    [state.stageExecutionStates]
  );

  // Reset all state
  const reset = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    dispatch({ type: 'RESET' });
  }, []);

  // Memoize context value
  const contextValue = useMemo<DebugContextValue>(
    () => ({
      state,
      startExecution,
      pauseExecution,
      resumeExecution,
      stepExecution,
      stopExecution,
      retryStage,
      addBreakpoint,
      removeBreakpoint,
      toggleBreakpoint,
      updateBreakpoint,
      clearBreakpoints,
      hasBreakpoint,
      addLog,
      clearLogs,
      setVariable,
      clearVariables,
      clearExecutionTrace,
      addNetworkCall,
      updateNetworkCall,
      clearNetworkCalls,
      getStageExecutionState,
      reset,
    }),
    [
      state,
      startExecution,
      pauseExecution,
      resumeExecution,
      stepExecution,
      stopExecution,
      retryStage,
      addBreakpoint,
      removeBreakpoint,
      toggleBreakpoint,
      updateBreakpoint,
      clearBreakpoints,
      hasBreakpoint,
      addLog,
      clearLogs,
      setVariable,
      clearVariables,
      clearExecutionTrace,
      addNetworkCall,
      updateNetworkCall,
      clearNetworkCalls,
      getStageExecutionState,
      reset,
    ]
  );

  return (
    <DebugContext.Provider value={contextValue}>
      {children}
    </DebugContext.Provider>
  );
}

export default DebugContext;
