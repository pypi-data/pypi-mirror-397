/**
 * Debug Adapter Types for FlowMason
 *
 * Types and interfaces for the Debug Adapter Protocol (DAP) implementation.
 */

import { DebugProtocol } from '@vscode/debugprotocol';

/**
 * FlowMason-specific launch configuration
 */
export interface FlowMasonLaunchConfig extends DebugProtocol.LaunchRequestArguments {
    /** Pipeline file to debug */
    pipeline: string;
    /** Input data for the pipeline (optional) */
    input?: Record<string, unknown>;
    /** Input file path (optional, alternative to input) */
    inputFile?: string;
    /** Stop on entry (pause before first stage) */
    stopOnEntry?: boolean;
    /** Studio backend URL */
    studioUrl?: string;
}

/**
 * Debug mode from the backend
 */
export type DebugMode = 'running' | 'paused' | 'stepping' | 'stopped';

/**
 * Debug state from the backend
 */
export interface DebugState {
    run_id: string;
    mode: DebugMode;
    breakpoints: string[];
    current_stage_id: string | null;
    paused_at: string | null;
    timeout_at: string | null;
    pause_reason: string | null;
}

/**
 * Stage execution event from WebSocket
 */
export interface StageExecutionEvent {
    run_id: string;
    stage_id: string;
    stage_name?: string;
    component_type: string;
    event_type: 'started' | 'completed' | 'failed';
    timestamp: string;
    status?: string;
    duration_ms?: number;
    output?: Record<string, unknown>;
    error?: string;
    input_tokens?: number;
    output_tokens?: number;
}

/**
 * Run execution event from WebSocket
 */
export interface RunExecutionEvent {
    run_id: string;
    pipeline_id: string;
    event_type: 'started' | 'completed' | 'failed';
    timestamp: string;
    stage_ids?: string[];
    inputs?: Record<string, unknown>;
    status?: string;
    output?: unknown;
    total_duration_ms?: number;
    error?: string;
    failed_stage_id?: string;
}

/**
 * Pause event from WebSocket
 */
export interface DebugPauseEvent {
    run_id: string;
    stage_id: string;
    stage_name?: string;
    reason: string;
    timeout_seconds: number;
    timestamp: string;
    completed_stages: string[];
    pending_stages: string[];
}

/**
 * Stage information for the call stack and variables
 */
export interface StageInfo {
    id: string;
    name?: string;
    component_type: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    input?: Record<string, unknown>;
    output?: Record<string, unknown>;
    config?: Record<string, unknown>;
    error?: string;
    duration_ms?: number;
}

/**
 * Pipeline information for debugging
 */
export interface PipelineInfo {
    name: string;
    version?: string;
    stages: StageInfo[];
}

/**
 * WebSocket message types (matches backend WebSocketEventType)
 */
export type WebSocketEventType =
    // Connection events
    | 'connected'
    | 'subscribed'
    | 'unsubscribed'
    | 'error'
    // Execution events
    | 'run_started'
    | 'run_completed'
    | 'run_failed'
    | 'stage_started'
    | 'stage_completed'
    | 'stage_failed'
    // Debug events
    | 'execution_paused'
    | 'execution_resumed'
    | 'breakpoint_hit'
    // Streaming events
    | 'stream_start'
    | 'token_chunk'
    | 'stream_end'
    // System events
    | 'ping'
    | 'pong';

/**
 * Stream start event payload
 */
export interface StreamStartEvent {
    stage_id: string;
    stage_name?: string;
}

/**
 * Token chunk event payload
 */
export interface TokenChunkEvent {
    stage_id: string;
    chunk: string;
    token_index: number;
}

/**
 * Stream end event payload
 */
export interface StreamEndEvent {
    stage_id: string;
    total_tokens: number;
    final_content?: string;
}

/**
 * WebSocket message envelope (matches backend WebSocketMessage)
 */
export interface WebSocketMessage {
    type: WebSocketEventType;
    run_id?: string;
    payload: Record<string, unknown>;
    timestamp?: string;
}

/**
 * WebSocket client message types (sent from client to server)
 */
export type WebSocketClientMessageType =
    | 'subscribe'
    | 'unsubscribe'
    | 'ping'
    | 'pause'
    | 'resume'
    | 'step'
    | 'stop';

/**
 * WebSocket client message
 */
export interface WebSocketClientMessage {
    type: WebSocketClientMessageType;
    run_id?: string;
    [key: string]: unknown;
}

/**
 * Debug command types
 */
export type DebugCommand = 'pause' | 'resume' | 'step' | 'stop' | 'set_breakpoint' | 'remove_breakpoint';

/**
 * Debug command request
 */
export interface DebugCommandRequest {
    command: DebugCommand;
    stage_id?: string;
}

/**
 * Debug command response
 */
export interface DebugCommandResponse {
    run_id: string;
    success: boolean;
    mode: DebugMode;
    message: string;
    current_stage_id?: string;
    breakpoints: string[];
}

/**
 * Conditional breakpoint with expression
 */
export interface ConditionalBreakpoint {
    /** Stage ID where the breakpoint is set */
    stageId: string;
    /** Condition expression using template syntax: {{stage_id.output.field}} == value */
    condition?: string;
    /** Hit count condition (e.g., ">= 5") */
    hitCondition?: string;
    /** Log message instead of breaking */
    logMessage?: string;
    /** Current hit count */
    hitCount: number;
}

/**
 * Watch expression for evaluating during debug
 */
export interface WatchExpression {
    /** The expression to evaluate (e.g., "{{fetch.output.status}}") */
    expression: string;
    /** Evaluated value (null if not yet evaluated) */
    value?: unknown;
    /** Error message if evaluation failed */
    error?: string;
}

/**
 * Evaluate request to backend
 */
export interface EvaluateRequest {
    run_id: string;
    expression: string;
    context?: 'watch' | 'hover' | 'repl';
}

/**
 * Evaluate response from backend
 */
export interface EvaluateResponse {
    result: string;
    type?: string;
    variablesReference: number;
    namedVariables?: number;
    indexedVariables?: number;
}
