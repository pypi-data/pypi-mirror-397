/**
 * FlowMason MCP Service
 *
 * Provides MCP (Model Context Protocol) integration for AI-assisted pipeline development.
 * Communicates with the FlowMason MCP server for pipeline generation and management.
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';

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

export class MCPService {
    private outputChannel: vscode.OutputChannel;
    private mcpProcess: cp.ChildProcess | null = null;
    private isRunning: boolean = false;

    constructor(outputChannel?: vscode.OutputChannel) {
        this.outputChannel = outputChannel || vscode.window.createOutputChannel('FlowMason MCP');
    }

    /**
     * Check if MCP server is available via fm CLI
     */
    async checkMCPAvailable(): Promise<boolean> {
        return new Promise((resolve) => {
            cp.exec('fm mcp --help', (error) => {
                resolve(!error);
            });
        });
    }

    /**
     * Start the MCP server
     */
    async startMCPServer(): Promise<boolean> {
        if (this.isRunning) {
            this.outputChannel.appendLine('MCP server is already running');
            return true;
        }

        const config = vscode.workspace.getConfiguration('flowmason');
        const studioUrl = config.get<string>('studioUrl') || 'http://localhost:8999';

        // Get workspace folder for pipelines
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const pipelinesDir = workspaceFolder
            ? path.join(workspaceFolder.uri.fsPath, 'pipelines')
            : undefined;

        return new Promise((resolve) => {
            try {
                const args = ['mcp', 'serve', '--studio-url', studioUrl];
                if (pipelinesDir) {
                    args.push('--pipelines-dir', pipelinesDir);
                }

                this.mcpProcess = cp.spawn('fm', args, {
                    stdio: ['pipe', 'pipe', 'pipe'],
                });

                this.mcpProcess.stdout?.on('data', (data) => {
                    this.outputChannel.appendLine(`[MCP] ${data.toString().trim()}`);
                });

                this.mcpProcess.stderr?.on('data', (data) => {
                    this.outputChannel.appendLine(`[MCP Error] ${data.toString().trim()}`);
                });

                this.mcpProcess.on('error', (error) => {
                    this.outputChannel.appendLine(`[MCP] Failed to start: ${error.message}`);
                    this.isRunning = false;
                    resolve(false);
                });

                this.mcpProcess.on('close', (code) => {
                    this.outputChannel.appendLine(`[MCP] Server stopped with code ${code}`);
                    this.isRunning = false;
                });

                // Give it a moment to start
                setTimeout(() => {
                    this.isRunning = true;
                    this.outputChannel.appendLine('[MCP] Server started');
                    resolve(true);
                }, 1000);

            } catch (error) {
                this.outputChannel.appendLine(`[MCP] Error: ${error}`);
                resolve(false);
            }
        });
    }

    /**
     * Stop the MCP server
     */
    stopMCPServer(): void {
        if (this.mcpProcess) {
            this.mcpProcess.kill();
            this.mcpProcess = null;
            this.isRunning = false;
            this.outputChannel.appendLine('[MCP] Server stopped');
        }
    }

    /**
     * Execute an MCP tool via the fm CLI
     */
    private async executeMCPTool(toolName: string, args: Record<string, unknown>): Promise<MCPToolResult> {
        const config = vscode.workspace.getConfiguration('flowmason');
        const studioUrl = config.get<string>('studioUrl') || 'http://localhost:8999';

        // For now, we'll call the Studio API directly since the MCP tools
        // are wrappers around the same functionality
        return this.executeViaStudioAPI(toolName, args, studioUrl);
    }

    /**
     * Execute MCP tool functionality via Studio API
     */
    private async executeViaStudioAPI(
        toolName: string,
        args: Record<string, unknown>,
        studioUrl: string
    ): Promise<MCPToolResult> {
        const axios = require('axios');

        try {
            switch (toolName) {
                case 'list_pipelines':
                    const pipelinesResp = await axios.get(`${studioUrl}/api/v1/pipelines`);
                    return {
                        success: true,
                        content: this.formatPipelinesList(pipelinesResp.data.pipelines || []),
                    };

                case 'list_components':
                    const componentsResp = await axios.get(`${studioUrl}/api/v1/registry/components`);
                    return {
                        success: true,
                        content: this.formatComponentsList(componentsResp.data.components || []),
                    };

                case 'get_component':
                    const componentResp = await axios.get(
                        `${studioUrl}/api/v1/registry/components/${args.component_type}`
                    );
                    return {
                        success: true,
                        content: this.formatComponentDetail(componentResp.data),
                    };

                case 'suggest_pipeline':
                    return this.suggestPipelineLocally(args.task_description as string);

                case 'generate_stage':
                    return this.generateStageLocally(
                        args.stage_type as string,
                        args.purpose as string,
                        args.input_source as string
                    );

                case 'validate_pipeline':
                    return this.validatePipelineLocally(args.pipeline_json as string);

                default:
                    return {
                        success: false,
                        content: '',
                        error: `Unknown MCP tool: ${toolName}`,
                    };
            }
        } catch (error) {
            const err = error as { message?: string; response?: { data?: { detail?: string } } };
            return {
                success: false,
                content: '',
                error: err.response?.data?.detail || err.message || 'Unknown error',
            };
        }
    }

    /**
     * Suggest a pipeline based on task description
     */
    async suggestPipeline(taskDescription: string): Promise<PipelineSuggestion | null> {
        const result = await this.executeMCPTool('suggest_pipeline', {
            task_description: taskDescription,
        });

        if (!result.success) {
            vscode.window.showErrorMessage(`Failed to get suggestions: ${result.error}`);
            return null;
        }

        // Parse the suggestion from the content
        return this.parseSuggestion(result.content, taskDescription);
    }

    /**
     * Generate a stage configuration
     */
    async generateStage(
        stageType: string,
        purpose: string,
        inputSource: string = 'input'
    ): Promise<GeneratedStage | null> {
        const result = await this.executeMCPTool('generate_stage', {
            stage_type: stageType,
            purpose,
            input_source: inputSource,
        });

        if (!result.success) {
            vscode.window.showErrorMessage(`Failed to generate stage: ${result.error}`);
            return null;
        }

        return this.parseGeneratedStage(result.content);
    }

    /**
     * Validate a pipeline configuration
     */
    async validatePipeline(pipelineJson: string): Promise<ValidationResult> {
        const result = await this.executeMCPTool('validate_pipeline', {
            pipeline_json: pipelineJson,
        });

        if (!result.success) {
            return {
                valid: false,
                errors: [result.error || 'Validation failed'],
                warnings: [],
            };
        }

        return this.parseValidationResult(result.content);
    }

    /**
     * Create a pipeline file
     */
    async createPipeline(
        name: string,
        description: string,
        stages: GeneratedStage[],
        inputSchema?: Record<string, unknown>
    ): Promise<string | null> {
        const pipeline = {
            name,
            version: '1.0.0',
            description,
            stages,
            input_schema: inputSchema,
        };

        // Validate first
        const validation = await this.validatePipeline(JSON.stringify(pipeline));
        if (!validation.valid) {
            const proceed = await vscode.window.showWarningMessage(
                `Pipeline has errors: ${validation.errors.join(', ')}. Create anyway?`,
                'Create',
                'Cancel'
            );
            if (proceed !== 'Create') {
                return null;
            }
        }

        // Get save location
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const defaultUri = workspaceFolder
            ? vscode.Uri.file(path.join(workspaceFolder.uri.fsPath, 'pipelines', `${name}.pipeline.json`))
            : undefined;

        const saveUri = await vscode.window.showSaveDialog({
            defaultUri,
            filters: {
                'Pipeline Files': ['pipeline.json'],
                'JSON Files': ['json'],
            },
            saveLabel: 'Create Pipeline',
        });

        if (!saveUri) {
            return null;
        }

        // Write the file
        const content = JSON.stringify(pipeline, null, 2);
        await vscode.workspace.fs.writeFile(saveUri, Buffer.from(content, 'utf-8'));

        // Open the file
        const document = await vscode.workspace.openTextDocument(saveUri);
        await vscode.window.showTextDocument(document);

        return saveUri.fsPath;
    }

    // =========================================================================
    // Local implementations (when Studio API not available)
    // =========================================================================

    private suggestPipelineLocally(taskDescription: string): MCPToolResult {
        const taskLower = taskDescription.toLowerCase();
        const suggestions: Array<{ component: string; purpose: string; rationale: string }> = [];

        // Analyze task and suggest components
        if (taskLower.match(/summarize|summary|condense/)) {
            suggestions.push({
                component: 'generator',
                purpose: 'Generate summary',
                rationale: 'Use LLM to create a summary of the input',
            });
        }

        if (taskLower.match(/filter|select|choose|pick/)) {
            suggestions.push({
                component: 'filter',
                purpose: 'Filter items based on criteria',
                rationale: 'Filter data to include only relevant items',
            });
        }

        if (taskLower.match(/transform|convert|format|restructure/)) {
            suggestions.push({
                component: 'json_transform',
                purpose: 'Transform data structure',
                rationale: 'Restructure data into desired format',
            });
        }

        if (taskLower.match(/api|http|fetch|request|call/)) {
            suggestions.push({
                component: 'http_request',
                purpose: 'Call external API',
                rationale: 'Make HTTP requests to external services',
            });
        }

        if (taskLower.match(/loop|iterate|each|batch/)) {
            suggestions.push({
                component: 'loop',
                purpose: 'Process items in a loop',
                rationale: 'Iterate over items and process each one',
            });
        }

        if (taskLower.match(/validate|check|verify|review/)) {
            suggestions.push({
                component: 'critic',
                purpose: 'Validate or review content',
                rationale: 'Use LLM to evaluate and validate content',
            });
        }

        if (taskLower.match(/generate|create|write|produce/)) {
            if (!suggestions.some(s => s.component === 'generator')) {
                suggestions.push({
                    component: 'generator',
                    purpose: 'Generate content',
                    rationale: 'Use LLM to generate new content',
                });
            }
        }

        // Build response
        let content = `## Suggested Pipeline for: ${taskDescription.slice(0, 100)}...\n\n`;

        if (suggestions.length > 0) {
            content += '### Recommended Components\n\n';
            suggestions.forEach((s, i) => {
                content += `**${i + 1}. ${s.component}**\n`;
                content += `   Purpose: ${s.purpose}\n`;
                content += `   Rationale: ${s.rationale}\n\n`;
            });

            // Build example pipeline
            const stages = suggestions.map((s, i) => ({
                id: `${s.component}-${i + 1}`,
                name: s.purpose,
                component_type: s.component,
                config: {},
                ...(i > 0 ? { depends_on: [`${suggestions[i - 1].component}-${i}`] } : {}),
            }));

            content += '### Example Pipeline Structure\n\n```json\n';
            content += JSON.stringify({
                name: 'suggested-pipeline',
                description: taskDescription.slice(0, 200),
                version: '1.0.0',
                stages,
            }, null, 2);
            content += '\n```';
        } else {
            content += 'Could not automatically suggest components.\n';
            content += 'Use list_components to see available options.';
        }

        return { success: true, content };
    }

    private generateStageLocally(
        stageType: string,
        purpose: string,
        inputSource: string
    ): MCPToolResult {
        const stageId = `${stageType}-${Date.now().toString(36).slice(-6)}`;
        let config: Record<string, unknown> = {};

        switch (stageType) {
            case 'generator':
                config = {
                    prompt: `Based on the following input, ${purpose}:\n\n{{${inputSource}}}`,
                    max_tokens: 1000,
                    temperature: 0.7,
                };
                break;
            case 'filter':
                config = {
                    items_path: `{{${inputSource}.items}}`,
                    condition: `# Condition for: ${purpose}\nTrue`,
                };
                break;
            case 'json_transform':
                config = {
                    template: {
                        result: `{{${inputSource}}}`,
                        metadata: { purpose },
                    },
                };
                break;
            case 'http_request':
                config = {
                    url: 'https://api.example.com/endpoint',
                    method: 'POST',
                    body: `{{${inputSource}}}`,
                };
                break;
            case 'loop':
                config = {
                    items_path: `{{${inputSource}.items}}`,
                    max_iterations: 10,
                };
                break;
            case 'critic':
                config = {
                    prompt: `Evaluate the following for: ${purpose}\n\nContent: {{${inputSource}}}`,
                    criteria: ['accuracy', 'relevance', 'quality'],
                };
                break;
            default:
                config = {
                    input: `{{${inputSource}}}`,
                    purpose,
                };
        }

        const stage: Record<string, unknown> = {
            id: stageId,
            name: purpose.slice(0, 50),
            component_type: stageType,
            config,
        };

        if (inputSource !== 'input' && inputSource.startsWith('stages.')) {
            const depStageId = inputSource.replace('stages.', '').split('.')[0];
            stage.depends_on = [depStageId];
        }

        const content = `Generated stage configuration:\n\n\`\`\`json\n${JSON.stringify(stage, null, 2)}\n\`\`\``;
        return { success: true, content };
    }

    private validatePipelineLocally(pipelineJson: string): MCPToolResult {
        try {
            const pipeline = JSON.parse(pipelineJson);
            const errors: string[] = [];
            const warnings: string[] = [];

            if (!pipeline.name) {
                errors.push("Missing required field: 'name'");
            }

            if (!pipeline.stages) {
                errors.push("Missing required field: 'stages'");
            } else if (!Array.isArray(pipeline.stages)) {
                errors.push("'stages' must be an array");
            } else if (pipeline.stages.length === 0) {
                errors.push('Pipeline must have at least one stage');
            } else {
                const stageIds = new Set<string>();
                pipeline.stages.forEach((stage: Record<string, unknown>, i: number) => {
                    if (!stage.id) {
                        errors.push(`Stage ${i}: missing 'id' field`);
                    } else {
                        if (stageIds.has(stage.id as string)) {
                            errors.push(`Stage ${i}: duplicate stage ID '${stage.id}'`);
                        }
                        stageIds.add(stage.id as string);
                    }

                    if (!stage.component_type) {
                        errors.push(`Stage ${i}: missing 'component_type' field`);
                    }

                    if (!stage.name) {
                        warnings.push(`Stage '${stage.id || i}': consider adding 'name'`);
                    }
                });
            }

            if (!pipeline.description) {
                warnings.push("Consider adding a 'description' field");
            }

            if (!pipeline.version) {
                warnings.push("Consider adding a 'version' field");
            }

            let content = errors.length > 0 ? '## Validation Failed\n\n' : '## Validation Passed\n\n';

            if (errors.length > 0) {
                content += '**Errors:**\n';
                errors.forEach(e => content += `- ${e}\n`);
            }

            if (warnings.length > 0) {
                content += '\n**Warnings:**\n';
                warnings.forEach(w => content += `- ${w}\n`);
            }

            return { success: true, content };
        } catch (e) {
            return {
                success: false,
                content: '',
                error: `Invalid JSON: ${e}`,
            };
        }
    }

    // =========================================================================
    // Formatters
    // =========================================================================

    private formatPipelinesList(pipelines: Array<Record<string, unknown>>): string {
        if (pipelines.length === 0) {
            return 'No pipelines found.';
        }

        let content = 'Available Pipelines:\n\n';
        pipelines.forEach((p) => {
            content += `## ${p.name} (v${p.version || '1.0.0'})\n`;
            content += `Status: ${p.status || 'unknown'}\n`;
            content += `Stages: ${p.stage_count || 0}\n`;
            content += `${p.description || 'No description'}\n\n`;
        });
        return content;
    }

    private formatComponentsList(components: Array<Record<string, unknown>>): string {
        if (components.length === 0) {
            return 'No components found.';
        }

        // Group by category
        const byCategory: Record<string, Array<Record<string, unknown>>> = {};
        components.forEach((c) => {
            const cat = (c.category as string) || 'uncategorized';
            if (!byCategory[cat]) {
                byCategory[cat] = [];
            }
            byCategory[cat].push(c);
        });

        let content = 'Available Components:\n\n';
        Object.keys(byCategory).sort().forEach((cat) => {
            content += `## ${cat.charAt(0).toUpperCase() + cat.slice(1)}\n\n`;
            byCategory[cat].forEach((c) => {
                const llm = c.requires_llm ? ' (requires LLM)' : '';
                content += `- **${c.name}** (\`${c.component_type}\`)${llm}\n`;
                content += `  ${c.description || 'No description'}\n`;
            });
            content += '\n';
        });
        return content;
    }

    private formatComponentDetail(component: Record<string, unknown>): string {
        let content = `# ${component.name}\n\n`;
        content += `**Type:** \`${component.component_type}\`\n`;
        content += `**Kind:** ${component.component_kind || 'operator'}\n`;
        content += `**Category:** ${component.category || 'uncategorized'}\n`;
        content += `**Version:** ${component.version || '1.0.0'}\n`;

        if (component.requires_llm) {
            content += '**Requires LLM:** Yes\n';
        }

        content += `\n${component.description || 'No description'}\n`;

        const inputSchema = component.input_schema as Record<string, unknown> | undefined;
        if (inputSchema?.properties) {
            content += '\n## Configuration\n\n';
            const props = inputSchema.properties as Record<string, Record<string, unknown>>;
            Object.entries(props).forEach(([prop, schema]) => {
                content += `- **${prop}** (${schema.type || 'any'}): ${schema.description || ''}\n`;
            });
        }

        return content;
    }

    // =========================================================================
    // Parsers
    // =========================================================================

    private parseSuggestion(content: string, taskDescription: string): PipelineSuggestion {
        const stages: Array<{ component: string; purpose: string; rationale: string }> = [];

        // Parse stages from content
        const componentMatches = content.matchAll(/\*\*\d+\.\s+(\w+)\*\*\s*\n\s*Purpose:\s*(.+?)\n\s*Rationale:\s*(.+?)(?=\n\n|\*\*\d+|$)/gs);
        for (const match of componentMatches) {
            stages.push({
                component: match[1],
                purpose: match[2].trim(),
                rationale: match[3].trim(),
            });
        }

        // Try to extract example pipeline JSON
        let examplePipeline: Record<string, unknown> | undefined;
        const jsonMatch = content.match(/```json\n([\s\S]+?)\n```/);
        if (jsonMatch) {
            try {
                examplePipeline = JSON.parse(jsonMatch[1]);
            } catch {
                // Ignore parse errors
            }
        }

        return {
            name: 'suggested-pipeline',
            description: taskDescription.slice(0, 200),
            stages,
            examplePipeline,
        };
    }

    private parseGeneratedStage(content: string): GeneratedStage | null {
        const jsonMatch = content.match(/```json\n([\s\S]+?)\n```/);
        if (!jsonMatch) {
            return null;
        }

        try {
            return JSON.parse(jsonMatch[1]) as GeneratedStage;
        } catch {
            return null;
        }
    }

    private parseValidationResult(content: string): ValidationResult {
        const valid = content.includes('Validation Passed');
        const errors: string[] = [];
        const warnings: string[] = [];

        // Parse errors
        const errorSection = content.match(/\*\*Errors:\*\*\n([\s\S]*?)(?=\n\*\*|$)/);
        if (errorSection) {
            const errorMatches = errorSection[1].matchAll(/^-\s*(.+)$/gm);
            for (const match of errorMatches) {
                errors.push(match[1]);
            }
        }

        // Parse warnings
        const warningSection = content.match(/\*\*Warnings:\*\*\n([\s\S]*?)(?=\n\*\*|$)/);
        if (warningSection) {
            const warningMatches = warningSection[1].matchAll(/^-\s*(.+)$/gm);
            for (const match of warningMatches) {
                warnings.push(match[1]);
            }
        }

        return { valid, errors, warnings };
    }

    /**
     * Dispose resources
     */
    dispose(): void {
        this.stopMCPServer();
        this.outputChannel.dispose();
    }
}
