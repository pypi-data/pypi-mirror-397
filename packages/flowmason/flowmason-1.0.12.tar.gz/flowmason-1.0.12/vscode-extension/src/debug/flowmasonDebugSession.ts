/**
 * FlowMason Debug Session
 *
 * Implements VSCode's Debug Adapter Protocol (DAP) for pipeline debugging.
 * Connects to the FlowMason Studio backend for execution control.
 * Uses WebSocket for real-time debug events.
 */

import * as vscode from 'vscode';
import { DebugProtocol } from '@vscode/debugprotocol';
import * as fs from 'fs';
import * as path from 'path';
import axios, { AxiosInstance } from 'axios';
import WebSocket from 'ws';
import {
    FlowMasonLaunchConfig,
    DebugState,
    StageInfo,
    StageExecutionEvent,
    RunExecutionEvent,
    DebugPauseEvent,
    WebSocketMessage,
    WebSocketClientMessage,
    ConditionalBreakpoint,
} from './types';

// Thread ID for the single pipeline execution thread
const PIPELINE_THREAD_ID = 1;

// Frame IDs start at 1
let nextFrameId = 1;

// Variable reference IDs
let nextVariableRef = 1;

/**
 * FlowMason Debug Session
 *
 * Handles debug requests from VSCode and communicates with the backend.
 */
export class FlowMasonDebugSession implements vscode.DebugAdapter {
    private _sendMessage = new vscode.EventEmitter<DebugProtocol.ProtocolMessage>();
    readonly onDidSendMessage: vscode.Event<DebugProtocol.ProtocolMessage> = this._sendMessage.event;

    private _sequence = 1;
    private _client: AxiosInstance;
    private _runId: string | null = null;
    private _pipelinePath: string | null = null;
    private _stages: Map<string, StageInfo> = new Map();
    private _breakpoints: Map<string, ConditionalBreakpoint> = new Map();
    private _exceptionBreakpoints: Set<string> = new Set();
    private _currentStageId: string | null = null;
    private _currentException: any = null;
    private _isPaused = false;
    private _isTerminated = false;

    // Variable references map
    private _variableRefs: Map<number, { type: string; stageId?: string }> = new Map();

    // Streaming state
    private _streamingStageId: string | null = null;
    private _streamingContent: string = '';

    // WebSocket for real-time events
    private _ws: WebSocket | null = null;
    private _wsUrl: string = '';
    private _wsConnected = false;
    private _wsReconnectAttempts = 0;
    private _wsReconnectTimer: NodeJS.Timeout | null = null;
    private _pingInterval: NodeJS.Timeout | null = null;
    private _studioUrl: string = '';

    constructor() {
        const config = vscode.workspace.getConfiguration('flowmason');
        this._studioUrl = config.get<string>('studioUrl') || 'http://localhost:8999';

        // Create WebSocket URL from HTTP URL
        this._wsUrl = this._studioUrl.replace(/^http/, 'ws') + '/api/v1/ws/runs';

        this._client = axios.create({
            baseURL: this._studioUrl,
            timeout: 30000,
            headers: { 'Content-Type': 'application/json' },
        });
    }

    /**
     * Handle messages from VSCode
     */
    handleMessage(message: DebugProtocol.ProtocolMessage): void {
        if (message.type === 'request') {
            this.handleRequest(message as DebugProtocol.Request);
        }
    }

    /**
     * Dispatch request to appropriate handler
     */
    private async handleRequest(request: DebugProtocol.Request): Promise<void> {
        try {
            switch (request.command) {
                case 'initialize':
                    await this.initializeRequest(request as DebugProtocol.InitializeRequest);
                    break;
                case 'launch':
                    await this.launchRequest(request as DebugProtocol.LaunchRequest);
                    break;
                case 'configurationDone':
                    this.configurationDoneRequest(request);
                    break;
                case 'setBreakpoints':
                    await this.setBreakpointsRequest(request as DebugProtocol.SetBreakpointsRequest);
                    break;
                case 'setExceptionBreakpoints':
                    await this.setExceptionBreakpointsRequest(request as DebugProtocol.SetExceptionBreakpointsRequest);
                    break;
                case 'exceptionInfo':
                    await this.exceptionInfoRequest(request as DebugProtocol.ExceptionInfoRequest);
                    break;
                case 'threads':
                    this.threadsRequest(request);
                    break;
                case 'stackTrace':
                    this.stackTraceRequest(request as DebugProtocol.StackTraceRequest);
                    break;
                case 'scopes':
                    this.scopesRequest(request as DebugProtocol.ScopesRequest);
                    break;
                case 'variables':
                    this.variablesRequest(request as DebugProtocol.VariablesRequest);
                    break;
                case 'evaluate':
                    await this.evaluateRequest(request as DebugProtocol.EvaluateRequest);
                    break;
                case 'continue':
                    await this.continueRequest(request as DebugProtocol.ContinueRequest);
                    break;
                case 'next':
                    await this.nextRequest(request as DebugProtocol.NextRequest);
                    break;
                case 'stepIn':
                    await this.stepInRequest(request as DebugProtocol.StepInRequest);
                    break;
                case 'pause':
                    await this.pauseRequest(request as DebugProtocol.PauseRequest);
                    break;
                case 'terminate':
                    await this.terminateRequest(request as DebugProtocol.TerminateRequest);
                    break;
                case 'disconnect':
                    await this.disconnectRequest(request as DebugProtocol.DisconnectRequest);
                    break;
                default:
                    this.sendErrorResponse(request, `Unknown command: ${request.command}`);
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            this.sendErrorResponse(request, message);
        }
    }

    /**
     * Initialize the debug adapter
     */
    private async initializeRequest(request: DebugProtocol.InitializeRequest): Promise<void> {
        // Declare capabilities
        const response: DebugProtocol.InitializeResponse = {
            seq: this._sequence++,
            type: 'response',
            request_seq: request.seq,
            command: request.command,
            success: true,
            body: {
                supportsConfigurationDoneRequest: true,
                supportsFunctionBreakpoints: true,
                supportsConditionalBreakpoints: true,
                supportsHitConditionalBreakpoints: true,
                supportsEvaluateForHovers: true,
                supportsStepBack: false,
                supportsSetVariable: false,
                supportsRestartFrame: false,
                supportsGotoTargetsRequest: false,
                supportsStepInTargetsRequest: false,
                supportsCompletionsRequest: false,
                supportsModulesRequest: false,
                supportsRestartRequest: true,
                supportsExceptionOptions: true,
                supportsValueFormattingOptions: false,
                supportsExceptionInfoRequest: true,
                supportTerminateDebuggee: true,
                supportsDelayedStackTraceLoading: false,
                supportsLoadedSourcesRequest: false,
                supportsLogPoints: true,
                supportsTerminateThreadsRequest: false,
                supportsSetExpression: false,
                supportsTerminateRequest: true,
                supportsDataBreakpoints: false,
                supportsReadMemoryRequest: false,
                supportsDisassembleRequest: false,
                supportsCancelRequest: false,
                supportsBreakpointLocationsRequest: false,
                // Exception breakpoint filters
                exceptionBreakpointFilters: [
                    {
                        filter: 'all',
                        label: 'All Errors',
                        description: 'Pause on all errors',
                        default: false,
                    },
                    {
                        filter: 'uncaught',
                        label: 'Uncaught Errors',
                        description: 'Pause on uncaught errors',
                        default: true,
                    },
                    {
                        filter: 'error',
                        label: 'Error Severity',
                        description: 'Pause on ERROR severity',
                        default: false,
                    },
                    {
                        filter: 'timeout',
                        label: 'Timeout Errors',
                        description: 'Pause on timeout errors',
                        default: false,
                    },
                    {
                        filter: 'validation',
                        label: 'Validation Errors',
                        description: 'Pause on validation errors',
                        default: false,
                    },
                    {
                        filter: 'connectivity',
                        label: 'Connectivity Errors',
                        description: 'Pause on network/connectivity errors',
                        default: false,
                    },
                ],
            },
        };

        this._sendMessage.fire(response);

        // Send initialized event
        this.sendEvent('initialized');
    }

    /**
     * Launch the pipeline for debugging
     */
    private async launchRequest(request: DebugProtocol.LaunchRequest): Promise<void> {
        const config = request.arguments as FlowMasonLaunchConfig;
        this._pipelinePath = config.pipeline;

        try {
            // Load pipeline file
            const pipelineContent = fs.readFileSync(config.pipeline, 'utf-8');
            const pipeline = JSON.parse(pipelineContent);

            // Initialize stages
            this._stages.clear();
            for (const stage of pipeline.stages || []) {
                this._stages.set(stage.id, {
                    id: stage.id,
                    name: stage.id,
                    component_type: stage.component_type,
                    status: 'pending',
                    config: stage.config,
                });
            }

            // Get input data
            let input: Record<string, unknown> = {};
            if (config.input) {
                input = config.input;
            } else if (config.inputFile) {
                const inputContent = fs.readFileSync(config.inputFile, 'utf-8');
                input = JSON.parse(inputContent);
            }

            // Start the debug run with pipeline definition
            const breakpointData = Array.from(this._breakpoints.values()).map(bp => ({
                stage_id: bp.stageId,
                condition: bp.condition,
                hit_condition: bp.hitCondition,
                log_message: bp.logMessage,
            }));
            const runResponse = await this._client.post('/api/v1/debug/run', {
                pipeline: pipeline,
                inputs: input,
                breakpoints: breakpointData,
                stop_on_entry: config.stopOnEntry ?? false,
            });

            this._runId = runResponse.data.id;

            // Connect WebSocket for real-time debug events
            this.connectWebSocket();

            // Send response
            this.sendResponse(request);

            // If stop on entry, we'll receive a pause event from the backend
            if (config.stopOnEntry) {
                this._isPaused = true;
            }

        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            this.sendErrorResponse(request, `Failed to launch pipeline: ${message}`);
        }
    }

    /**
     * Configuration done - called after all breakpoints have been set
     */
    private configurationDoneRequest(request: DebugProtocol.Request): void {
        // Configuration is complete, the debug session is ready
        // The launch has already started execution, so just acknowledge
        this.sendResponse(request);
    }

    /**
     * Set breakpoints (supports conditional breakpoints, hit conditions, and log points)
     */
    private async setBreakpointsRequest(request: DebugProtocol.SetBreakpointsRequest): Promise<void> {
        const args = request.arguments;
        const sourcePath = args.source.path || '';

        // Only handle breakpoints for pipeline files
        if (!sourcePath.endsWith('.pipeline.json')) {
            this.sendResponse(request, { breakpoints: [] });
            return;
        }

        // Clear existing breakpoints for this source
        this._breakpoints.clear();

        // Parse the pipeline to get stage IDs at line numbers
        const breakpoints: DebugProtocol.Breakpoint[] = [];
        const requestedBreakpoints = args.breakpoints || [];

        try {
            const content = fs.readFileSync(sourcePath, 'utf-8');
            const pipeline = JSON.parse(content);

            // Map line numbers to stage IDs
            const stageLines = this.getStageLineNumbers(content, pipeline.stages || []);

            for (const bp of requestedBreakpoints) {
                const stageId = stageLines.get(bp.line);
                if (stageId) {
                    // Create conditional breakpoint
                    const conditionalBp: ConditionalBreakpoint = {
                        stageId,
                        condition: bp.condition,
                        hitCondition: bp.hitCondition,
                        logMessage: bp.logMessage,
                        hitCount: 0,
                    };
                    this._breakpoints.set(stageId, conditionalBp);

                    breakpoints.push({
                        id: breakpoints.length + 1,
                        verified: true,
                        line: bp.line,
                        source: args.source,
                        message: this.getBreakpointDescription(conditionalBp),
                    });
                } else {
                    breakpoints.push({
                        id: breakpoints.length + 1,
                        verified: false,
                        line: bp.line,
                        message: 'No stage at this line',
                    });
                }
            }

            // Update breakpoints on the backend if we have an active run
            if (this._runId) {
                const breakpointData = Array.from(this._breakpoints.values()).map(bp => ({
                    stage_id: bp.stageId,
                    condition: bp.condition,
                    hit_condition: bp.hitCondition,
                    log_message: bp.logMessage,
                }));
                await this._client.post(`/api/v1/runs/${this._runId}/breakpoints`, {
                    breakpoints: breakpointData,
                });
            }

        } catch (error) {
            // Return unverified breakpoints on error
            for (const bp of requestedBreakpoints) {
                breakpoints.push({
                    id: breakpoints.length + 1,
                    verified: false,
                    line: bp.line,
                    message: 'Failed to verify breakpoint',
                });
            }
        }

        this.sendResponse(request, { breakpoints });
    }

    /**
     * Get a description for a conditional breakpoint
     */
    private getBreakpointDescription(bp: ConditionalBreakpoint): string | undefined {
        const parts: string[] = [];
        if (bp.condition) {
            parts.push(`Condition: ${bp.condition}`);
        }
        if (bp.hitCondition) {
            parts.push(`Hit count: ${bp.hitCondition}`);
        }
        if (bp.logMessage) {
            parts.push(`Log: ${bp.logMessage}`);
        }
        return parts.length > 0 ? parts.join(', ') : undefined;
    }

    /**
     * Set exception breakpoints
     */
    private async setExceptionBreakpointsRequest(request: DebugProtocol.SetExceptionBreakpointsRequest): Promise<void> {
        const args = request.arguments;
        const filters = args.filters || [];

        // Store exception breakpoints locally
        this._exceptionBreakpoints.clear();
        for (const filter of filters) {
            this._exceptionBreakpoints.add(filter);
        }

        // Update exception breakpoints on the backend if we have an active run
        if (this._runId) {
            try {
                await this._client.put(`/api/v1/runs/${this._runId}/debug/exception-breakpoints`, {
                    filters: filters,
                });
            } catch (error) {
                // Log but don't fail - breakpoints are stored locally
                console.error('Failed to set exception breakpoints on backend:', error);
            }
        }

        // Return the breakpoints - all verified
        const breakpoints: DebugProtocol.Breakpoint[] = filters.map((filter, index) => ({
            id: index + 1,
            verified: true,
        }));

        this.sendResponse(request, { breakpoints });
    }

    /**
     * Get exception info for the current exception
     */
    private async exceptionInfoRequest(request: DebugProtocol.ExceptionInfoRequest): Promise<void> {
        if (!this._runId) {
            this.sendResponse(request, {
                exceptionId: 'unknown',
                description: 'No active run',
                breakMode: 'never',
            });
            return;
        }

        try {
            // Get exception info from backend
            const response = await this._client.get(`/api/v1/runs/${this._runId}/debug/exception-info`);
            const data = response.data;

            if (data.has_exception && data.exception) {
                const exception = data.exception;
                this._currentException = exception;

                this.sendResponse(request, {
                    exceptionId: exception.exception_id || 'error',
                    description: exception.description || 'Unknown error',
                    breakMode: exception.break_mode || 'always',
                    details: {
                        message: exception.description,
                        typeName: exception.error_type || 'Error',
                        stackTrace: exception.stack_trace,
                        innerException: exception.details ? {
                            message: JSON.stringify(exception.details),
                        } : undefined,
                    },
                });
            } else {
                this.sendResponse(request, {
                    exceptionId: 'none',
                    description: 'No exception',
                    breakMode: 'never',
                });
            }
        } catch (error) {
            this.sendResponse(request, {
                exceptionId: 'error',
                description: error instanceof Error ? error.message : 'Failed to get exception info',
                breakMode: 'never',
            });
        }
    }

    /**
     * Get line numbers for each stage in the pipeline
     */
    private getStageLineNumbers(content: string, stages: Array<{ id: string }>): Map<number, string> {
        const lineMap = new Map<number, string>();
        const lines = content.split('\n');

        for (const stage of stages) {
            const pattern = `"id"\\s*:\\s*"${stage.id}"`;
            const regex = new RegExp(pattern);

            for (let i = 0; i < lines.length; i++) {
                if (regex.test(lines[i])) {
                    lineMap.set(i + 1, stage.id); // Lines are 1-indexed
                    break;
                }
            }
        }

        return lineMap;
    }

    /**
     * Return threads (single thread for pipeline execution)
     */
    private threadsRequest(request: DebugProtocol.ThreadsRequest): void {
        this.sendResponse(request, {
            threads: [
                { id: PIPELINE_THREAD_ID, name: 'Pipeline Execution' },
            ],
        });
    }

    /**
     * Return stack trace (stages as frames)
     */
    private stackTraceRequest(request: DebugProtocol.StackTraceRequest): void {
        const frames: DebugProtocol.StackFrame[] = [];

        // Current stage at the top
        if (this._currentStageId) {
            const stage = this._stages.get(this._currentStageId);
            if (stage) {
                const frameId = nextFrameId++;
                frames.push({
                    id: frameId,
                    name: `${stage.id} (${stage.component_type})`,
                    source: this._pipelinePath ? {
                        name: path.basename(this._pipelinePath),
                        path: this._pipelinePath,
                    } : undefined,
                    line: 1, // Would need to find actual line
                    column: 0,
                });
            }
        }

        // Add completed stages as the "call stack"
        for (const [stageId, stage] of this._stages) {
            if (stage.status === 'completed' && stageId !== this._currentStageId) {
                const frameId = nextFrameId++;
                frames.push({
                    id: frameId,
                    name: `${stage.id} (${stage.component_type}) - completed`,
                    source: this._pipelinePath ? {
                        name: path.basename(this._pipelinePath),
                        path: this._pipelinePath,
                    } : undefined,
                    line: 1,
                    column: 0,
                });
            }
        }

        this.sendResponse(request, {
            stackFrames: frames,
            totalFrames: frames.length,
        });
    }

    /**
     * Return scopes for a frame
     */
    private scopesRequest(request: DebugProtocol.ScopesRequest): void {
        const scopes: DebugProtocol.Scope[] = [];

        // Create variable references for the current stage
        if (this._currentStageId) {
            const inputRef = nextVariableRef++;
            const outputRef = nextVariableRef++;
            const configRef = nextVariableRef++;

            this._variableRefs.set(inputRef, { type: 'input', stageId: this._currentStageId });
            this._variableRefs.set(outputRef, { type: 'output', stageId: this._currentStageId });
            this._variableRefs.set(configRef, { type: 'config', stageId: this._currentStageId });

            scopes.push({
                name: 'Input',
                variablesReference: inputRef,
                expensive: false,
            });

            scopes.push({
                name: 'Output',
                variablesReference: outputRef,
                expensive: false,
            });

            scopes.push({
                name: 'Config',
                variablesReference: configRef,
                expensive: false,
            });
        }

        this.sendResponse(request, { scopes });
    }

    /**
     * Return variables for a scope
     */
    private variablesRequest(request: DebugProtocol.VariablesRequest): void {
        const ref = this._variableRefs.get(request.arguments.variablesReference);
        const variables: DebugProtocol.Variable[] = [];

        if (ref && ref.stageId) {
            const stage = this._stages.get(ref.stageId);
            if (stage) {
                let data: Record<string, unknown> | undefined;

                switch (ref.type) {
                    case 'input':
                        data = stage.input;
                        break;
                    case 'output':
                        data = stage.output;
                        break;
                    case 'config':
                        data = stage.config;
                        break;
                }

                if (data) {
                    for (const [key, value] of Object.entries(data)) {
                        variables.push({
                            name: key,
                            value: this.formatValue(value),
                            type: typeof value,
                            variablesReference: 0, // No nested expansion for now
                        });
                    }
                }
            }
        }

        this.sendResponse(request, { variables });
    }

    /**
     * Evaluate an expression (for watch expressions and hover)
     */
    private async evaluateRequest(request: DebugProtocol.EvaluateRequest): Promise<void> {
        const args = request.arguments;
        const expression = args.expression;
        const context = args.context || 'watch';

        // Try to evaluate the expression locally first
        const localResult = this.evaluateExpressionLocally(expression);
        if (localResult !== undefined) {
            this.sendResponse(request, {
                result: this.formatValue(localResult),
                type: typeof localResult,
                variablesReference: 0,
            });
            return;
        }

        // If we have an active run, try evaluating on the backend
        if (this._runId) {
            try {
                const response = await this._client.post(`/api/v1/runs/${this._runId}/debug/evaluate`, {
                    expression,
                    context,
                });

                const data = response.data;
                this.sendResponse(request, {
                    result: data.result || 'undefined',
                    type: data.type || 'unknown',
                    variablesReference: data.variablesReference || 0,
                    namedVariables: data.namedVariables,
                    indexedVariables: data.indexedVariables,
                });
            } catch (error) {
                // Return error as the result
                const message = error instanceof Error ? error.message : String(error);
                this.sendResponse(request, {
                    result: `<error: ${message}>`,
                    type: 'error',
                    variablesReference: 0,
                });
            }
        } else {
            // No active run - can't evaluate
            this.sendResponse(request, {
                result: '<no active debug session>',
                type: 'error',
                variablesReference: 0,
            });
        }
    }

    /**
     * Evaluate an expression locally using available stage data
     * Supports template syntax: {{stage_id.output.field}} or {{stage_id.input.field}}
     */
    private evaluateExpressionLocally(expression: string): unknown {
        // Check for template syntax
        const templateMatch = expression.match(/^\{\{([^}]+)\}\}$/);
        if (!templateMatch) {
            // Check for simple stage.output.field syntax
            const simpleMatch = expression.match(/^(\w+)\.(output|input|config)\.?(.*)$/);
            if (simpleMatch) {
                const [, stageId, scope, path] = simpleMatch;
                return this.getStageValue(stageId, scope as 'output' | 'input' | 'config', path);
            }
            return undefined;
        }

        const path = templateMatch[1];
        const parts = path.split('.');

        if (parts.length >= 2) {
            const stageId = parts[0];
            const scope = parts[1] as 'output' | 'input' | 'config';
            const remainingPath = parts.slice(2).join('.');
            return this.getStageValue(stageId, scope, remainingPath);
        }

        return undefined;
    }

    /**
     * Get a value from a stage's output/input/config
     */
    private getStageValue(stageId: string, scope: 'output' | 'input' | 'config', path: string): unknown {
        const stage = this._stages.get(stageId);
        if (!stage) {
            return undefined;
        }

        let data: Record<string, unknown> | undefined;
        switch (scope) {
            case 'output':
                data = stage.output;
                break;
            case 'input':
                data = stage.input;
                break;
            case 'config':
                data = stage.config;
                break;
        }

        if (!data) {
            return undefined;
        }

        // Navigate the path
        if (!path) {
            return data;
        }

        const pathParts = path.split('.');
        let current: unknown = data;
        for (const part of pathParts) {
            if (current === null || current === undefined) {
                return undefined;
            }
            if (typeof current === 'object') {
                current = (current as Record<string, unknown>)[part];
            } else {
                return undefined;
            }
        }

        return current;
    }

    /**
     * Format a value for display
     */
    private formatValue(value: unknown): string {
        if (value === null) return 'null';
        if (value === undefined) return 'undefined';
        if (typeof value === 'string') return `"${value}"`;
        if (typeof value === 'object') {
            try {
                return JSON.stringify(value, null, 2);
            } catch {
                return '[Object]';
            }
        }
        return String(value);
    }

    /**
     * Continue execution
     */
    private async continueRequest(request: DebugProtocol.ContinueRequest): Promise<void> {
        if (this._runId) {
            // Prefer WebSocket for real-time commands
            if (this._wsConnected) {
                this.sendWebSocketMessage({
                    type: 'resume',
                    run_id: this._runId,
                });
                this._isPaused = false;
            } else {
                // Fallback to HTTP
                try {
                    await this._client.post(`/api/v1/runs/${this._runId}/debug/resume`);
                    this._isPaused = false;
                } catch (error) {
                    // Ignore errors - run may have completed
                }
            }
        }

        this.sendResponse(request, { allThreadsContinued: true });
    }

    /**
     * Step to next stage
     */
    private async nextRequest(request: DebugProtocol.NextRequest): Promise<void> {
        if (this._runId) {
            // Prefer WebSocket for real-time commands
            if (this._wsConnected) {
                this.sendWebSocketMessage({
                    type: 'step',
                    run_id: this._runId,
                });
            } else {
                // Fallback to HTTP
                try {
                    await this._client.post(`/api/v1/runs/${this._runId}/debug/step`);
                } catch (error) {
                    // Ignore errors
                }
            }
        }

        this.sendResponse(request);
    }

    /**
     * Step into (same as next for pipelines, unless we implement sub-pipeline stepping)
     */
    private async stepInRequest(request: DebugProtocol.StepInRequest): Promise<void> {
        // For now, same as next
        await this.nextRequest(request as unknown as DebugProtocol.NextRequest);
    }

    /**
     * Pause execution
     */
    private async pauseRequest(request: DebugProtocol.PauseRequest): Promise<void> {
        if (this._runId) {
            // Prefer WebSocket for real-time commands
            if (this._wsConnected) {
                this.sendWebSocketMessage({
                    type: 'pause',
                    run_id: this._runId,
                });
                this._isPaused = true;
            } else {
                // Fallback to HTTP
                try {
                    await this._client.post(`/api/v1/runs/${this._runId}/debug/pause`);
                    this._isPaused = true;
                } catch (error) {
                    // Ignore errors
                }
            }
        }

        this.sendResponse(request);
    }

    /**
     * Terminate the debug session
     */
    private async terminateRequest(request: DebugProtocol.TerminateRequest): Promise<void> {
        await this.stopExecution();
        this.sendResponse(request);
    }

    /**
     * Disconnect from the debug session
     */
    private async disconnectRequest(request: DebugProtocol.DisconnectRequest): Promise<void> {
        await this.stopExecution();
        this.sendResponse(request);
    }

    /**
     * Stop execution and cleanup
     */
    private async stopExecution(): Promise<void> {
        this._isTerminated = true;

        // Send stop command via WebSocket if connected
        if (this._runId && this._wsConnected) {
            this.sendWebSocketMessage({
                type: 'stop',
                run_id: this._runId,
            });
        }

        // Disconnect WebSocket
        this.disconnectWebSocket();

        // Also send stop via HTTP as fallback
        if (this._runId) {
            try {
                await this._client.post(`/api/v1/runs/${this._runId}/debug/stop`);
            } catch (error) {
                // Ignore errors - run may have already completed
            }
        }
    }

    /**
     * Connect to WebSocket for real-time debug events
     */
    private connectWebSocket(): void {
        this.disconnectWebSocket();

        try {
            this._ws = new WebSocket(this._wsUrl);

            this._ws.on('open', () => {
                this._wsConnected = true;
                this._wsReconnectAttempts = 0;
                console.log('FlowMason Debug: WebSocket connected');

                // Subscribe to run updates
                if (this._runId) {
                    this.sendWebSocketMessage({
                        type: 'subscribe',
                        run_id: this._runId,
                    });
                }

                // Start ping interval to keep connection alive
                this.startPingInterval();
            });

            this._ws.on('message', (data: WebSocket.RawData) => {
                try {
                    const message = JSON.parse(data.toString()) as WebSocketMessage;
                    this.handleWebSocketMessage(message);
                } catch (error) {
                    console.error('FlowMason Debug: Failed to parse WebSocket message:', error);
                }
            });

            this._ws.on('close', () => {
                this._wsConnected = false;
                console.log('FlowMason Debug: WebSocket disconnected');
                this.stopPingInterval();

                // Attempt to reconnect if not terminated
                if (!this._isTerminated && this._wsReconnectAttempts < 5) {
                    this._wsReconnectAttempts++;
                    const delay = Math.min(1000 * Math.pow(2, this._wsReconnectAttempts), 10000);
                    console.log(`FlowMason Debug: Reconnecting in ${delay}ms (attempt ${this._wsReconnectAttempts})`);
                    this._wsReconnectTimer = setTimeout(() => this.connectWebSocket(), delay);
                }
            });

            this._ws.on('error', (error) => {
                console.error('FlowMason Debug: WebSocket error:', error);
            });

        } catch (error) {
            console.error('FlowMason Debug: Failed to create WebSocket:', error);
        }
    }

    /**
     * Disconnect WebSocket
     */
    private disconnectWebSocket(): void {
        this.stopPingInterval();

        if (this._wsReconnectTimer) {
            clearTimeout(this._wsReconnectTimer);
            this._wsReconnectTimer = null;
        }

        if (this._ws) {
            // Unsubscribe from run before closing
            if (this._runId && this._wsConnected) {
                this.sendWebSocketMessage({
                    type: 'unsubscribe',
                    run_id: this._runId,
                });
            }

            this._ws.close();
            this._ws = null;
        }

        this._wsConnected = false;
    }

    /**
     * Send a message via WebSocket
     */
    private sendWebSocketMessage(message: WebSocketClientMessage): void {
        if (this._ws && this._wsConnected) {
            this._ws.send(JSON.stringify(message));
        }
    }

    /**
     * Start ping interval to keep WebSocket alive
     */
    private startPingInterval(): void {
        this.stopPingInterval();
        this._pingInterval = setInterval(() => {
            this.sendWebSocketMessage({ type: 'ping' });
        }, 30000); // Ping every 30 seconds
    }

    /**
     * Stop ping interval
     */
    private stopPingInterval(): void {
        if (this._pingInterval) {
            clearInterval(this._pingInterval);
            this._pingInterval = null;
        }
    }

    /**
     * Handle incoming WebSocket messages
     */
    private handleWebSocketMessage(message: WebSocketMessage): void {
        // Only process messages for our run
        if (message.run_id && message.run_id !== this._runId) {
            return;
        }

        const payload = message.payload || {};

        switch (message.type) {
            case 'connected':
                console.log('FlowMason Debug: Server confirmed connection');
                break;

            case 'subscribed':
                console.log(`FlowMason Debug: Subscribed to run ${payload.run_id}`);
                break;

            case 'run_started':
                console.log(`FlowMason Debug: Run started`);
                break;

            case 'stage_started': {
                const stageId = payload.stage_id as string;
                if (stageId) {
                    this._currentStageId = stageId;
                    const stage = this._stages.get(stageId);
                    if (stage) {
                        stage.status = 'running';
                        stage.input = payload.input as Record<string, unknown>;
                    }
                    this.sendEvent('output', {
                        category: 'stdout',
                        output: `Stage started: ${stageId}\n`,
                    });
                }
                break;
            }

            case 'stage_completed': {
                const stageId = payload.stage_id as string;
                if (stageId) {
                    const stage = this._stages.get(stageId);
                    if (stage) {
                        stage.status = 'completed';
                        stage.output = payload.output as Record<string, unknown>;
                        stage.duration_ms = payload.duration_ms as number;
                    }
                    this.sendEvent('output', {
                        category: 'stdout',
                        output: `Stage completed: ${stageId} (${payload.duration_ms}ms)\n`,
                    });
                }
                break;
            }

            case 'stage_failed': {
                const stageId = payload.stage_id as string;
                if (stageId) {
                    const stage = this._stages.get(stageId);
                    if (stage) {
                        stage.status = 'failed';
                        stage.error = payload.error as string;
                    }
                    this.sendEvent('output', {
                        category: 'stderr',
                        output: `Stage failed: ${stageId} - ${payload.error}\n`,
                    });

                    // Check if we should pause on this exception
                    if (this.shouldPauseOnException(payload)) {
                        this._currentException = payload;
                        this._isPaused = true;
                        this.sendEvent('stopped', {
                            reason: 'exception',
                            threadId: PIPELINE_THREAD_ID,
                            allThreadsStopped: true,
                            text: payload.error as string,
                        });
                    }
                }
                break;
            }

            case 'run_completed':
                this.sendEvent('output', {
                    category: 'stdout',
                    output: `Run completed successfully\n`,
                });
                this.sendEvent('terminated');
                this.disconnectWebSocket();
                break;

            case 'run_failed':
                this.sendEvent('output', {
                    category: 'stderr',
                    output: `Run failed: ${payload.error}\n`,
                });
                this.sendEvent('terminated');
                this.disconnectWebSocket();
                break;

            case 'execution_paused':
            case 'breakpoint_hit': {
                const stageId = payload.stage_id as string;
                if (stageId) {
                    this._currentStageId = stageId;
                }

                // Check if this is a conditional breakpoint
                if (message.type === 'breakpoint_hit' && stageId) {
                    const bp = this._breakpoints.get(stageId);
                    if (bp) {
                        // Increment hit count
                        bp.hitCount++;

                        // Handle log point (just log, don't break)
                        if (bp.logMessage) {
                            const logOutput = this.interpolateLogMessage(bp.logMessage, stageId);
                            this.sendEvent('output', {
                                category: 'console',
                                output: `[Log Point] ${logOutput}\n`,
                            });
                            // If only a log point (no condition), resume execution
                            if (!bp.condition && !bp.hitCondition) {
                                // Auto-resume - don't pause
                                if (this._wsConnected) {
                                    this.sendWebSocketMessage({
                                        type: 'resume',
                                        run_id: this._runId!,
                                    });
                                }
                                break;
                            }
                        }

                        // Check hit condition
                        if (bp.hitCondition) {
                            const shouldBreak = this.evaluateHitCondition(bp.hitCondition, bp.hitCount);
                            if (!shouldBreak) {
                                // Hit condition not met, resume
                                if (this._wsConnected) {
                                    this.sendWebSocketMessage({
                                        type: 'resume',
                                        run_id: this._runId!,
                                    });
                                }
                                break;
                            }
                        }

                        // Check conditional expression
                        if (bp.condition) {
                            const conditionMet = this.evaluateBreakpointCondition(bp.condition);
                            if (!conditionMet) {
                                // Condition not met, resume
                                if (this._wsConnected) {
                                    this.sendWebSocketMessage({
                                        type: 'resume',
                                        run_id: this._runId!,
                                    });
                                }
                                break;
                            }
                        }
                    }
                }

                this._isPaused = true;
                const reason = message.type === 'breakpoint_hit' ? 'breakpoint' : (payload.reason as string || 'pause');
                this.sendEvent('stopped', {
                    reason,
                    threadId: PIPELINE_THREAD_ID,
                    allThreadsStopped: true,
                });
                break;
            }

            case 'execution_resumed':
                this._isPaused = false;
                this.sendEvent('continued', {
                    threadId: PIPELINE_THREAD_ID,
                    allThreadsContinued: true,
                });
                break;

            case 'stream_start': {
                const stageId = payload.stage_id as string;
                const stageName = payload.stage_name as string | undefined;
                // Emit streaming started event (can be consumed by prompt editor via separate channel)
                this._streamingStageId = stageId;
                this._streamingContent = '';
                this.sendEvent('output', {
                    category: 'stdout',
                    output: `Streaming started: ${stageName || stageId}\n`,
                });
                break;
            }

            case 'token_chunk': {
                const chunk = payload.chunk as string;
                if (chunk && this._streamingStageId) {
                    this._streamingContent += chunk;
                    // Output streaming tokens to debug console (real-time visualization)
                    this.sendEvent('output', {
                        category: 'console',
                        output: chunk,
                    });
                }
                break;
            }

            case 'stream_end': {
                const stageId = payload.stage_id as string;
                const totalTokens = payload.total_tokens as number | undefined;
                this._streamingStageId = null;
                this.sendEvent('output', {
                    category: 'stdout',
                    output: `\nStreaming completed: ${stageId} (${totalTokens || '?'} tokens)\n`,
                });
                break;
            }

            case 'error':
                console.error('FlowMason Debug: Server error:', payload.error);
                break;

            case 'pong':
                // Heartbeat response, connection is alive
                break;

            default:
                console.log(`FlowMason Debug: Unknown message type: ${message.type}`);
        }
    }

    /**
     * Interpolate log message with template variables
     */
    private interpolateLogMessage(message: string, stageId: string): string {
        return message.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
            const parts = path.split('.');
            let targetStageId = stageId;
            let scope = 'output';
            let fieldPath = '';

            if (parts.length >= 2) {
                // Check if first part is a stage ID
                if (this._stages.has(parts[0])) {
                    targetStageId = parts[0];
                    scope = parts[1];
                    fieldPath = parts.slice(2).join('.');
                } else {
                    scope = parts[0];
                    fieldPath = parts.slice(1).join('.');
                }
            } else if (parts.length === 1) {
                fieldPath = parts[0];
            }

            const value = this.getStageValue(targetStageId, scope as 'output' | 'input' | 'config', fieldPath);
            return value !== undefined ? this.formatValue(value) : match;
        });
    }

    /**
     * Evaluate hit count condition (e.g., ">= 5", "== 10", "% 2 == 0")
     */
    private evaluateHitCondition(condition: string, hitCount: number): boolean {
        const trimmed = condition.trim();

        // Handle modulo expressions: "% 2 == 0" means hit on every 2nd time
        const moduloMatch = trimmed.match(/^%\s*(\d+)\s*(==|!=|>=|<=|>|<)\s*(\d+)$/);
        if (moduloMatch) {
            const [, divisor, operator, value] = moduloMatch;
            const result = hitCount % parseInt(divisor, 10);
            return this.compareValues(result, operator, parseInt(value, 10));
        }

        // Handle comparison expressions: ">= 5", "== 10", etc.
        const compareMatch = trimmed.match(/^(==|!=|>=|<=|>|<)\s*(\d+)$/);
        if (compareMatch) {
            const [, operator, value] = compareMatch;
            return this.compareValues(hitCount, operator, parseInt(value, 10));
        }

        // Handle plain number (means "break when hit count equals this")
        const plainNumber = parseInt(trimmed, 10);
        if (!isNaN(plainNumber)) {
            return hitCount === plainNumber;
        }

        // Default: break
        return true;
    }

    /**
     * Compare two values using an operator
     */
    private compareValues(a: number, operator: string, b: number): boolean {
        switch (operator) {
            case '==': return a === b;
            case '!=': return a !== b;
            case '>=': return a >= b;
            case '<=': return a <= b;
            case '>': return a > b;
            case '<': return a < b;
            default: return false;
        }
    }

    /**
     * Evaluate a breakpoint condition expression
     * Supports: {{stage.output.field}} == value, {{stage.output.field}} != value, etc.
     */
    private evaluateBreakpointCondition(condition: string): boolean {
        // Parse condition: {{expr}} op value or just {{expr}} (truthy check)
        const fullMatch = condition.match(/^\{\{([^}]+)\}\}\s*(==|!=|>=|<=|>|<|===|!==)\s*(.+)$/);
        if (fullMatch) {
            const [, expr, operator, valueStr] = fullMatch;
            const leftValue = this.evaluateExpressionLocally(`{{${expr}}}`);

            // Parse the right value
            let rightValue: unknown;
            const trimmedValue = valueStr.trim();
            if (trimmedValue === 'true') {
                rightValue = true;
            } else if (trimmedValue === 'false') {
                rightValue = false;
            } else if (trimmedValue === 'null') {
                rightValue = null;
            } else if (trimmedValue === 'undefined') {
                rightValue = undefined;
            } else if (/^-?\d+(\.\d+)?$/.test(trimmedValue)) {
                rightValue = parseFloat(trimmedValue);
            } else if ((trimmedValue.startsWith('"') && trimmedValue.endsWith('"')) ||
                       (trimmedValue.startsWith("'") && trimmedValue.endsWith("'"))) {
                rightValue = trimmedValue.slice(1, -1);
            } else {
                // Try to evaluate as an expression
                rightValue = this.evaluateExpressionLocally(trimmedValue) ?? trimmedValue;
            }

            // Compare
            switch (operator) {
                case '==':
                case '===':
                    return leftValue === rightValue;
                case '!=':
                case '!==':
                    return leftValue !== rightValue;
                case '>=':
                    return Number(leftValue) >= Number(rightValue);
                case '<=':
                    return Number(leftValue) <= Number(rightValue);
                case '>':
                    return Number(leftValue) > Number(rightValue);
                case '<':
                    return Number(leftValue) < Number(rightValue);
                default:
                    return false;
            }
        }

        // Truthy check: just {{expr}}
        const truthyMatch = condition.match(/^\{\{([^}]+)\}\}$/);
        if (truthyMatch) {
            const value = this.evaluateExpressionLocally(condition);
            return Boolean(value);
        }

        // Simple property check without braces: stage.output.field
        const simpleMatch = condition.match(/^(\w+)\.(output|input|config)\.?(.*)$/);
        if (simpleMatch) {
            const value = this.evaluateExpressionLocally(condition);
            return Boolean(value);
        }

        // Default: condition not understood, break anyway
        console.warn(`FlowMason Debug: Could not parse condition: ${condition}`);
        return true;
    }

    /**
     * Check if we should pause on this exception based on exception breakpoint settings
     */
    private shouldPauseOnException(payload: Record<string, unknown>): boolean {
        // If no exception breakpoints set, don't pause
        if (this._exceptionBreakpoints.size === 0) {
            return false;
        }

        // Check for 'all' filter
        if (this._exceptionBreakpoints.has('all')) {
            return true;
        }

        // Check for 'uncaught' filter (all stage failures are uncaught in pipeline context)
        if (this._exceptionBreakpoints.has('uncaught')) {
            return true;
        }

        // Check for specific error type filters
        const errorType = (payload.error_type as string || '').toLowerCase();

        if (this._exceptionBreakpoints.has('error') && errorType.includes('error')) {
            return true;
        }

        if (this._exceptionBreakpoints.has('timeout') && errorType.includes('timeout')) {
            return true;
        }

        if (this._exceptionBreakpoints.has('validation') && errorType.includes('validation')) {
            return true;
        }

        if (this._exceptionBreakpoints.has('connectivity') &&
            (errorType.includes('connection') || errorType.includes('network') || errorType.includes('http'))) {
            return true;
        }

        return false;
    }

    /**
     * Send a response to VSCode
     */
    private sendResponse(request: DebugProtocol.Request, body?: unknown): void {
        const response: DebugProtocol.Response = {
            seq: this._sequence++,
            type: 'response',
            request_seq: request.seq,
            command: request.command,
            success: true,
            body,
        };
        this._sendMessage.fire(response);
    }

    /**
     * Send an error response
     */
    private sendErrorResponse(request: DebugProtocol.Request, message: string): void {
        const response: DebugProtocol.Response = {
            seq: this._sequence++,
            type: 'response',
            request_seq: request.seq,
            command: request.command,
            success: false,
            message,
        };
        this._sendMessage.fire(response);
    }

    /**
     * Send an event to VSCode
     */
    private sendEvent(event: string, body?: unknown): void {
        const message: DebugProtocol.Event = {
            seq: this._sequence++,
            type: 'event',
            event,
            body,
        };
        this._sendMessage.fire(message);
    }

    /**
     * Dispose of resources
     */
    dispose(): void {
        this.disconnectWebSocket();
        this._sendMessage.dispose();
    }
}
