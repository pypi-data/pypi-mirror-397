/**
 * FlowMason Execution WebSocket Hook
 *
 * React hook for managing WebSocket connections for real-time execution updates.
 * Features:
 * - Automatic connection management
 * - Run subscription handling
 * - Event callbacks for execution events
 * - Fallback to polling when WebSocket fails
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import {
  ExecutionWebSocket,
  getWebSocket,
  ConnectionStatus,
  WebSocketMessage,
  WebSocketEventType,
  StageStartedPayload,
  StageCompletedPayload,
  StageFailedPayload,
  RunStartedPayload,
  RunCompletedPayload,
  RunFailedPayload,
  ExecutionPausedPayload,
} from '../services/websocket';

export interface UseExecutionWebSocketOptions {
  /** Run ID to subscribe to (null to not subscribe) */
  runId: string | null;

  /** Callback when a stage starts */
  onStageStarted?: (payload: StageStartedPayload) => void;

  /** Callback when a stage completes */
  onStageCompleted?: (payload: StageCompletedPayload) => void;

  /** Callback when a stage fails */
  onStageFailed?: (payload: StageFailedPayload) => void;

  /** Callback when a run starts */
  onRunStarted?: (payload: RunStartedPayload) => void;

  /** Callback when a run completes */
  onRunCompleted?: (payload: RunCompletedPayload) => void;

  /** Callback when a run fails */
  onRunFailed?: (payload: RunFailedPayload) => void;

  /** Callback when execution is paused */
  onExecutionPaused?: (payload: ExecutionPausedPayload) => void;

  /** Callback when execution is resumed */
  onExecutionResumed?: (payload: { stage_id: string }) => void;

  /** Callback for any event (for logging/debugging) */
  onAnyEvent?: (message: WebSocketMessage) => void;

  /** Whether to connect automatically (default: true) */
  autoConnect?: boolean;

  /** Fallback polling interval in ms when WebSocket fails (default: 500) */
  fallbackPollingInterval?: number;

  /** Timeout before activating fallback in ms (default: 2000) */
  fallbackTimeout?: number;
}

export interface UseExecutionWebSocketReturn {
  /** Current connection status */
  connectionStatus: ConnectionStatus;

  /** Whether we're using polling fallback */
  isUsingFallback: boolean;

  /** Whether WebSocket is connected */
  isConnected: boolean;

  /** Manually connect */
  connect: () => void;

  /** Manually disconnect */
  disconnect: () => void;

  /** Subscribe to a run */
  subscribe: (runId: string) => void;

  /** Unsubscribe from a run */
  unsubscribe: (runId: string) => void;

  /** Send pause command */
  pause: (runId: string) => void;

  /** Send resume command */
  resume: (runId: string) => void;

  /** Send step command */
  step: (runId: string) => void;

  /** Send stop command */
  stop: (runId: string) => void;
}

export function useExecutionWebSocket(
  options: UseExecutionWebSocketOptions
): UseExecutionWebSocketReturn {
  const {
    runId,
    onStageStarted,
    onStageCompleted,
    onStageFailed,
    onRunStarted,
    onRunCompleted,
    onRunFailed,
    onExecutionPaused,
    onExecutionResumed,
    onAnyEvent,
    autoConnect = true,
    fallbackTimeout = 2000,
  } = options;

  const wsRef = useRef<ExecutionWebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [isUsingFallback, setIsUsingFallback] = useState(false);
  const fallbackTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const previousRunIdRef = useRef<string | null>(null);

  // Store callbacks in refs to avoid dependency issues
  const callbacksRef = useRef({
    onStageStarted,
    onStageCompleted,
    onStageFailed,
    onRunStarted,
    onRunCompleted,
    onRunFailed,
    onExecutionPaused,
    onExecutionResumed,
    onAnyEvent,
  });

  // Update callbacks ref when they change
  useEffect(() => {
    callbacksRef.current = {
      onStageStarted,
      onStageCompleted,
      onStageFailed,
      onRunStarted,
      onRunCompleted,
      onRunFailed,
      onExecutionPaused,
      onExecutionResumed,
      onAnyEvent,
    };
  }, [
    onStageStarted,
    onStageCompleted,
    onStageFailed,
    onRunStarted,
    onRunCompleted,
    onRunFailed,
    onExecutionPaused,
    onExecutionResumed,
    onAnyEvent,
  ]);

  // Handle WebSocket events
  const handleEvent = useCallback((message: WebSocketMessage) => {
    const callbacks = callbacksRef.current;

    // Call onAnyEvent for all events
    callbacks.onAnyEvent?.(message);

    // Route to specific callbacks
    switch (message.type as WebSocketEventType) {
      case 'stage_started':
        callbacks.onStageStarted?.(message.payload as unknown as StageStartedPayload);
        break;

      case 'stage_completed':
        callbacks.onStageCompleted?.(message.payload as unknown as StageCompletedPayload);
        break;

      case 'stage_failed':
        callbacks.onStageFailed?.(message.payload as unknown as StageFailedPayload);
        break;

      case 'run_started':
        callbacks.onRunStarted?.(message.payload as unknown as RunStartedPayload);
        break;

      case 'run_completed':
        callbacks.onRunCompleted?.(message.payload as unknown as RunCompletedPayload);
        break;

      case 'run_failed':
        callbacks.onRunFailed?.(message.payload as unknown as RunFailedPayload);
        break;

      case 'execution_paused':
        callbacks.onExecutionPaused?.(message.payload as unknown as ExecutionPausedPayload);
        break;

      case 'execution_resumed':
        callbacks.onExecutionResumed?.(message.payload as { stage_id: string });
        break;
    }
  }, []);

  // Handle status changes
  const handleStatusChange = useCallback((status: ConnectionStatus) => {
    setConnectionStatus(status);

    // Clear fallback timeout if connected
    if (status === 'connected') {
      if (fallbackTimeoutRef.current) {
        clearTimeout(fallbackTimeoutRef.current);
        fallbackTimeoutRef.current = null;
      }
      setIsUsingFallback(false);
    }
  }, []);

  // Initialize WebSocket
  useEffect(() => {
    if (!autoConnect) return;

    const ws = getWebSocket();
    wsRef.current = ws;

    // Subscribe to events and status changes
    const unsubscribeEvent = ws.onEvent(handleEvent);
    const unsubscribeStatus = ws.onStatusChange(handleStatusChange);

    // Connect if not already connected
    if (!ws.isConnected) {
      ws.connect();

      // Set up fallback timeout
      fallbackTimeoutRef.current = setTimeout(() => {
        if (!ws.isConnected) {
          console.warn('[useExecutionWebSocket] WebSocket connection failed, activating fallback');
          setIsUsingFallback(true);
        }
      }, fallbackTimeout);
    } else {
      setConnectionStatus(ws.connectionStatus);
    }

    return () => {
      unsubscribeEvent();
      unsubscribeStatus();

      if (fallbackTimeoutRef.current) {
        clearTimeout(fallbackTimeoutRef.current);
        fallbackTimeoutRef.current = null;
      }
    };
  }, [autoConnect, handleEvent, handleStatusChange, fallbackTimeout]);

  // Handle run subscription changes
  useEffect(() => {
    const ws = wsRef.current;
    if (!ws) return;

    // Unsubscribe from previous run
    if (previousRunIdRef.current && previousRunIdRef.current !== runId) {
      ws.unsubscribe(previousRunIdRef.current);
    }

    // Subscribe to new run
    if (runId) {
      ws.subscribe(runId);
    }

    previousRunIdRef.current = runId;

    return () => {
      // Unsubscribe on unmount
      if (runId) {
        ws.unsubscribe(runId);
      }
    };
  }, [runId]);

  // Manual control functions
  const connect = useCallback(() => {
    wsRef.current?.connect();
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.disconnect();
  }, []);

  const subscribe = useCallback((id: string) => {
    wsRef.current?.subscribe(id);
  }, []);

  const unsubscribe = useCallback((id: string) => {
    wsRef.current?.unsubscribe(id);
  }, []);

  const pause = useCallback((id: string) => {
    wsRef.current?.pause(id);
  }, []);

  const resume = useCallback((id: string) => {
    wsRef.current?.resume(id);
  }, []);

  const step = useCallback((id: string) => {
    wsRef.current?.step(id);
  }, []);

  const stop = useCallback((id: string) => {
    wsRef.current?.stop(id);
  }, []);

  return {
    connectionStatus,
    isUsingFallback,
    isConnected: connectionStatus === 'connected',
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    pause,
    resume,
    step,
    stop,
  };
}

export default useExecutionWebSocket;
