/**
 * FlowMason Debug Hook
 *
 * Provides comprehensive debugging capabilities for pipeline development:
 * - Debug mode control (start, pause, resume, stop, step)
 * - Log management with filtering
 * - Variable inspection
 * - Breakpoint management
 * - Execution trace tracking
 * - Network call monitoring
 */

import { useState, useCallback, useMemo } from 'react';
import type {
  DebugMode,
  DebugState,
  LogLevel,
  LogEntry,
  Breakpoint,
  VariableInfo,
  ExecutionStep,
  NetworkCall,
} from '../types';

const generateId = () => Math.random().toString(36).substring(2, 11);

const initialDebugState: DebugState = {
  mode: 'stopped',
  currentStageId: null,
  breakpoints: [],
  executionTrace: [],
  variables: {},
  logs: [],
  networkCalls: [],
  startTime: null,
  pausedAt: null,
};

export interface UseDebugReturn {
  // State
  state: DebugState;
  mode: DebugMode;
  currentStageId: string | null;
  breakpoints: Breakpoint[];
  executionTrace: ExecutionStep[];
  variables: Record<string, VariableInfo>;
  logs: LogEntry[];
  networkCalls: NetworkCall[];

  // Mode controls
  start: () => void;
  pause: () => void;
  resume: () => void;
  stop: () => void;
  step: () => void;

  // Logging
  log: (level: LogLevel, message: string, source?: string, stageId?: string, data?: Record<string, unknown>) => void;
  clearLogs: () => void;
  getFilteredLogs: (levels?: LogLevel[]) => LogEntry[];

  // Variables
  setVariable: (name: string, value: unknown, source: string) => void;
  clearVariables: () => void;

  // Breakpoints
  addBreakpoint: (stageId: string, condition?: string, maxHits?: number) => void;
  removeBreakpoint: (id: string) => void;
  toggleBreakpoint: (id: string) => void;
  clearBreakpoints: () => void;
  isBreakpoint: (stageId: string) => boolean;

  // Execution trace
  addStep: (step: Omit<ExecutionStep, 'stepId' | 'logs'>) => string;
  updateStep: (stepId: string, updates: Partial<ExecutionStep>) => void;
  clearTrace: () => void;

  // Network calls
  addNetworkCall: (call: Omit<NetworkCall, 'id'>) => string;
  updateNetworkCall: (id: string, updates: Partial<NetworkCall>) => void;
  clearNetworkCalls: () => void;

  // Utilities
  reset: () => void;
  setCurrentStage: (stageId: string | null) => void;

  // Stats
  logCounts: { debug: number; info: number; warn: number; error: number };
}

export function useDebug(): UseDebugReturn {
  const [state, setState] = useState<DebugState>(initialDebugState);

  // Mode controls
  const start = useCallback(() => {
    setState((prev) => ({
      ...prev,
      mode: 'running',
      startTime: new Date().toISOString(),
      pausedAt: null,
    }));
  }, []);

  const pause = useCallback(() => {
    setState((prev) => ({
      ...prev,
      mode: 'paused',
      pausedAt: new Date().toISOString(),
    }));
  }, []);

  const resume = useCallback(() => {
    setState((prev) => ({
      ...prev,
      mode: 'running',
      pausedAt: null,
    }));
  }, []);

  const stop = useCallback(() => {
    setState((prev) => ({
      ...prev,
      mode: 'stopped',
      startTime: null,
      pausedAt: null,
    }));
  }, []);

  const step = useCallback(() => {
    setState((prev) => ({
      ...prev,
      mode: 'stepping',
    }));
  }, []);

  // Logging
  const log = useCallback(
    (level: LogLevel, message: string, source?: string, stageId?: string, data?: Record<string, unknown>) => {
      const entry: LogEntry = {
        id: generateId(),
        level,
        message,
        timestamp: new Date().toISOString(),
        source,
        stageId,
        data,
      };
      setState((prev) => ({
        ...prev,
        logs: [...prev.logs, entry],
      }));
    },
    []
  );

  const clearLogs = useCallback(() => {
    setState((prev) => ({
      ...prev,
      logs: [],
    }));
  }, []);

  const getFilteredLogs = useCallback(
    (levels?: LogLevel[]) => {
      if (!levels || levels.length === 0) return state.logs;
      return state.logs.filter((log) => levels.includes(log.level));
    },
    [state.logs]
  );

  // Variables
  const setVariable = useCallback((name: string, value: unknown, source: string) => {
    setState((prev) => {
      const existing = prev.variables[name];
      const changed = existing ? JSON.stringify(existing.value) !== JSON.stringify(value) : true;

      return {
        ...prev,
        variables: {
          ...prev.variables,
          [name]: {
            name,
            value,
            type: typeof value,
            source,
            timestamp: new Date().toISOString(),
            changed,
          },
        },
      };
    });
  }, []);

  const clearVariables = useCallback(() => {
    setState((prev) => ({
      ...prev,
      variables: {},
    }));
  }, []);

  // Breakpoints
  const addBreakpoint = useCallback((stageId: string, condition?: string, maxHits?: number) => {
    const breakpoint: Breakpoint = {
      id: generateId(),
      stageId,
      condition,
      enabled: true,
      hitCount: 0,
      maxHits,
    };
    setState((prev) => ({
      ...prev,
      breakpoints: [...prev.breakpoints, breakpoint],
    }));
  }, []);

  const removeBreakpoint = useCallback((id: string) => {
    setState((prev) => ({
      ...prev,
      breakpoints: prev.breakpoints.filter((bp) => bp.id !== id),
    }));
  }, []);

  const toggleBreakpoint = useCallback((id: string) => {
    setState((prev) => ({
      ...prev,
      breakpoints: prev.breakpoints.map((bp) =>
        bp.id === id ? { ...bp, enabled: !bp.enabled } : bp
      ),
    }));
  }, []);

  const clearBreakpoints = useCallback(() => {
    setState((prev) => ({
      ...prev,
      breakpoints: [],
    }));
  }, []);

  const isBreakpoint = useCallback(
    (stageId: string) => {
      return state.breakpoints.some((bp) => bp.stageId === stageId && bp.enabled);
    },
    [state.breakpoints]
  );

  // Execution trace
  const addStep = useCallback((step: Omit<ExecutionStep, 'stepId' | 'logs'>): string => {
    const stepId = generateId();
    const newStep: ExecutionStep = {
      ...step,
      stepId,
      logs: [],
    };
    setState((prev) => ({
      ...prev,
      executionTrace: [...prev.executionTrace, newStep],
      currentStageId: step.stageId,
    }));
    return stepId;
  }, []);

  const updateStep = useCallback((stepId: string, updates: Partial<ExecutionStep>) => {
    setState((prev) => ({
      ...prev,
      executionTrace: prev.executionTrace.map((step) =>
        step.stepId === stepId ? { ...step, ...updates } : step
      ),
    }));
  }, []);

  const clearTrace = useCallback(() => {
    setState((prev) => ({
      ...prev,
      executionTrace: [],
    }));
  }, []);

  // Network calls
  const addNetworkCall = useCallback((call: Omit<NetworkCall, 'id'>): string => {
    const id = generateId();
    const newCall: NetworkCall = { ...call, id };
    setState((prev) => ({
      ...prev,
      networkCalls: [...prev.networkCalls, newCall],
    }));
    return id;
  }, []);

  const updateNetworkCall = useCallback((id: string, updates: Partial<NetworkCall>) => {
    setState((prev) => ({
      ...prev,
      networkCalls: prev.networkCalls.map((call) =>
        call.id === id ? { ...call, ...updates } : call
      ),
    }));
  }, []);

  const clearNetworkCalls = useCallback(() => {
    setState((prev) => ({
      ...prev,
      networkCalls: [],
    }));
  }, []);

  // Utilities
  const reset = useCallback(() => {
    setState(initialDebugState);
  }, []);

  const setCurrentStage = useCallback((stageId: string | null) => {
    setState((prev) => ({
      ...prev,
      currentStageId: stageId,
    }));
  }, []);

  // Log counts
  const logCounts = useMemo(() => {
    return state.logs.reduce(
      (acc, log) => {
        acc[log.level]++;
        return acc;
      },
      { debug: 0, info: 0, warn: 0, error: 0 }
    );
  }, [state.logs]);

  return {
    // State
    state,
    mode: state.mode,
    currentStageId: state.currentStageId,
    breakpoints: state.breakpoints,
    executionTrace: state.executionTrace,
    variables: state.variables,
    logs: state.logs,
    networkCalls: state.networkCalls,

    // Mode controls
    start,
    pause,
    resume,
    stop,
    step,

    // Logging
    log,
    clearLogs,
    getFilteredLogs,

    // Variables
    setVariable,
    clearVariables,

    // Breakpoints
    addBreakpoint,
    removeBreakpoint,
    toggleBreakpoint,
    clearBreakpoints,
    isBreakpoint,

    // Execution trace
    addStep,
    updateStep,
    clearTrace,

    // Network calls
    addNetworkCall,
    updateNetworkCall,
    clearNetworkCalls,

    // Utilities
    reset,
    setCurrentStage,

    // Stats
    logCounts,
  };
}

export default useDebug;
