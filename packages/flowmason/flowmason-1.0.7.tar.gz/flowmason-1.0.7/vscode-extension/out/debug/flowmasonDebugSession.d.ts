/**
 * FlowMason Debug Session
 *
 * Implements VSCode's Debug Adapter Protocol (DAP) for pipeline debugging.
 * Connects to the FlowMason Studio backend for execution control.
 * Uses WebSocket for real-time debug events.
 */
import * as vscode from 'vscode';
import { DebugProtocol } from '@vscode/debugprotocol';
/**
 * FlowMason Debug Session
 *
 * Handles debug requests from VSCode and communicates with the backend.
 */
export declare class FlowMasonDebugSession implements vscode.DebugAdapter {
    private _sendMessage;
    readonly onDidSendMessage: vscode.Event<DebugProtocol.ProtocolMessage>;
    private _sequence;
    private _client;
    private _runId;
    private _pipelinePath;
    private _stages;
    private _breakpoints;
    private _exceptionBreakpoints;
    private _currentStageId;
    private _currentException;
    private _isPaused;
    private _isTerminated;
    private _variableRefs;
    private _streamingStageId;
    private _streamingContent;
    private _ws;
    private _wsUrl;
    private _wsConnected;
    private _wsReconnectAttempts;
    private _wsReconnectTimer;
    private _pingInterval;
    private _studioUrl;
    constructor();
    /**
     * Handle messages from VSCode
     */
    handleMessage(message: DebugProtocol.ProtocolMessage): void;
    /**
     * Dispatch request to appropriate handler
     */
    private handleRequest;
    /**
     * Initialize the debug adapter
     */
    private initializeRequest;
    /**
     * Launch the pipeline for debugging
     */
    private launchRequest;
    /**
     * Configuration done - called after all breakpoints have been set
     */
    private configurationDoneRequest;
    /**
     * Set breakpoints (supports conditional breakpoints, hit conditions, and log points)
     */
    private setBreakpointsRequest;
    /**
     * Get a description for a conditional breakpoint
     */
    private getBreakpointDescription;
    /**
     * Set exception breakpoints
     */
    private setExceptionBreakpointsRequest;
    /**
     * Get exception info for the current exception
     */
    private exceptionInfoRequest;
    /**
     * Get line numbers for each stage in the pipeline
     */
    private getStageLineNumbers;
    /**
     * Return threads (single thread for pipeline execution)
     */
    private threadsRequest;
    /**
     * Return stack trace (stages as frames)
     */
    private stackTraceRequest;
    /**
     * Return scopes for a frame
     */
    private scopesRequest;
    /**
     * Return variables for a scope
     */
    private variablesRequest;
    /**
     * Evaluate an expression (for watch expressions and hover)
     */
    private evaluateRequest;
    /**
     * Evaluate an expression locally using available stage data
     * Supports template syntax: {{stage_id.output.field}} or {{stage_id.input.field}}
     */
    private evaluateExpressionLocally;
    /**
     * Get a value from a stage's output/input/config
     */
    private getStageValue;
    /**
     * Format a value for display
     */
    private formatValue;
    /**
     * Continue execution
     */
    private continueRequest;
    /**
     * Step to next stage
     */
    private nextRequest;
    /**
     * Step into (same as next for pipelines, unless we implement sub-pipeline stepping)
     */
    private stepInRequest;
    /**
     * Pause execution
     */
    private pauseRequest;
    /**
     * Terminate the debug session
     */
    private terminateRequest;
    /**
     * Disconnect from the debug session
     */
    private disconnectRequest;
    /**
     * Stop execution and cleanup
     */
    private stopExecution;
    /**
     * Connect to WebSocket for real-time debug events
     */
    private connectWebSocket;
    /**
     * Disconnect WebSocket
     */
    private disconnectWebSocket;
    /**
     * Send a message via WebSocket
     */
    private sendWebSocketMessage;
    /**
     * Start ping interval to keep WebSocket alive
     */
    private startPingInterval;
    /**
     * Stop ping interval
     */
    private stopPingInterval;
    /**
     * Handle incoming WebSocket messages
     */
    private handleWebSocketMessage;
    /**
     * Interpolate log message with template variables
     */
    private interpolateLogMessage;
    /**
     * Evaluate hit count condition (e.g., ">= 5", "== 10", "% 2 == 0")
     */
    private evaluateHitCondition;
    /**
     * Compare two values using an operator
     */
    private compareValues;
    /**
     * Evaluate a breakpoint condition expression
     * Supports: {{stage.output.field}} == value, {{stage.output.field}} != value, etc.
     */
    private evaluateBreakpointCondition;
    /**
     * Check if we should pause on this exception based on exception breakpoint settings
     */
    private shouldPauseOnException;
    /**
     * Send a response to VSCode
     */
    private sendResponse;
    /**
     * Send an error response
     */
    private sendErrorResponse;
    /**
     * Send an event to VSCode
     */
    private sendEvent;
    /**
     * Dispose of resources
     */
    dispose(): void;
}
//# sourceMappingURL=flowmasonDebugSession.d.ts.map