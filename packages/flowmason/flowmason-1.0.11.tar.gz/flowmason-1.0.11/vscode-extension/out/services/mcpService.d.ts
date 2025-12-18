/**
 * FlowMason MCP Service
 *
 * Provides MCP (Model Context Protocol) integration for AI-assisted pipeline development.
 * Communicates with the FlowMason MCP server for pipeline generation and management.
 */
import * as vscode from 'vscode';
/**
 * MCP Tool Call Result
 */
export interface MCPToolResult {
    success: boolean;
    content: string;
    error?: string;
}
/**
 * Pipeline Suggestion from MCP
 */
export interface PipelineSuggestion {
    name: string;
    description: string;
    stages: Array<{
        component: string;
        purpose: string;
        rationale: string;
    }>;
    examplePipeline?: Record<string, unknown>;
}
/**
 * Generated Stage Configuration
 */
export interface GeneratedStage {
    id: string;
    name: string;
    component_type: string;
    config: Record<string, unknown>;
    depends_on?: string[];
}
/**
 * Validation Result
 */
export interface ValidationResult {
    valid: boolean;
    errors: string[];
    warnings: string[];
}
export declare class MCPService {
    private outputChannel;
    private mcpProcess;
    private isRunning;
    constructor(outputChannel?: vscode.OutputChannel);
    /**
     * Check if MCP server is available via fm CLI
     */
    checkMCPAvailable(): Promise<boolean>;
    /**
     * Start the MCP server
     */
    startMCPServer(): Promise<boolean>;
    /**
     * Stop the MCP server
     */
    stopMCPServer(): void;
    /**
     * Execute an MCP tool via the fm CLI
     */
    private executeMCPTool;
    /**
     * Execute MCP tool functionality via Studio API
     */
    private executeViaStudioAPI;
    /**
     * Suggest a pipeline based on task description
     */
    suggestPipeline(taskDescription: string): Promise<PipelineSuggestion | null>;
    /**
     * Generate a stage configuration
     */
    generateStage(stageType: string, purpose: string, inputSource?: string): Promise<GeneratedStage | null>;
    /**
     * Validate a pipeline configuration
     */
    validatePipeline(pipelineJson: string): Promise<ValidationResult>;
    /**
     * Create a pipeline file
     */
    createPipeline(name: string, description: string, stages: GeneratedStage[], inputSchema?: Record<string, unknown>): Promise<string | null>;
    private suggestPipelineLocally;
    private generateStageLocally;
    private validatePipelineLocally;
    private formatPipelinesList;
    private formatComponentsList;
    private formatComponentDetail;
    private parseSuggestion;
    private parseGeneratedStage;
    private parseValidationResult;
    /**
     * Dispose resources
     */
    dispose(): void;
}
//# sourceMappingURL=mcpService.d.ts.map