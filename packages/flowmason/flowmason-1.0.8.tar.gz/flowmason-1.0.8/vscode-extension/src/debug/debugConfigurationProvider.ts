/**
 * FlowMason Debug Configuration Provider
 *
 * Provides launch configurations and resolves debug configurations for FlowMason pipelines.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { FlowMasonLaunchConfig } from './types';

/**
 * Provides initial debug configurations and resolves them before launching
 */
export class FlowMasonDebugConfigurationProvider implements vscode.DebugConfigurationProvider {
    /**
     * Provide initial debug configurations when creating launch.json
     */
    provideDebugConfigurations(
        folder: vscode.WorkspaceFolder | undefined,
        token?: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.DebugConfiguration[]> {
        return [
            {
                type: 'flowmason',
                name: 'Debug Pipeline',
                request: 'launch',
                pipeline: '${file}',
                stopOnEntry: true,
            },
            {
                type: 'flowmason',
                name: 'Debug Pipeline with Input',
                request: 'launch',
                pipeline: '${file}',
                inputFile: '${workspaceFolder}/test-input.json',
                stopOnEntry: false,
            },
        ];
    }

    /**
     * Resolve a debug configuration before launching
     * This is called to fill in missing fields or validate the configuration
     */
    async resolveDebugConfiguration(
        folder: vscode.WorkspaceFolder | undefined,
        config: vscode.DebugConfiguration,
        token?: vscode.CancellationToken
    ): Promise<vscode.DebugConfiguration | undefined> {
        // If no configuration, try to debug the current file
        if (!config.type && !config.request && !config.name) {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document.fileName.endsWith('.pipeline.json')) {
                config.type = 'flowmason';
                config.name = 'Debug Current Pipeline';
                config.request = 'launch';
                config.pipeline = editor.document.fileName;
                config.stopOnEntry = true;
            }
        }

        // Validate pipeline path
        if (!config.pipeline) {
            await vscode.window.showErrorMessage('Pipeline file path is required');
            return undefined;
        }

        // Resolve variables in pipeline path
        config.pipeline = this.resolveVariables(config.pipeline, folder);

        // Validate pipeline file exists
        if (!fs.existsSync(config.pipeline)) {
            await vscode.window.showErrorMessage(`Pipeline file not found: ${config.pipeline}`);
            return undefined;
        }

        // Resolve input file if specified
        if (config.inputFile) {
            config.inputFile = this.resolveVariables(config.inputFile, folder);
            if (!fs.existsSync(config.inputFile)) {
                await vscode.window.showWarningMessage(
                    `Input file not found: ${config.inputFile}. Continuing without input.`
                );
                delete config.inputFile;
            }
        }

        // Prompt for required inputs if not provided
        if (!config.input && !config.inputFile) {
            const promptedInput = await this.promptForInputs(config.pipeline);
            if (promptedInput === undefined) {
                // User cancelled
                return undefined;
            }
            if (Object.keys(promptedInput).length > 0) {
                config.input = promptedInput;
            }
        }

        // Get studio URL from settings if not specified
        if (!config.studioUrl) {
            const settings = vscode.workspace.getConfiguration('flowmason');
            config.studioUrl = settings.get<string>('studioUrl') || 'http://localhost:8999';
        }

        return config;
    }

    /**
     * Prompt user for pipeline inputs based on input_schema
     */
    private async promptForInputs(pipelinePath: string): Promise<Record<string, unknown> | undefined> {
        try {
            const pipelineContent = fs.readFileSync(pipelinePath, 'utf-8');
            const pipeline = JSON.parse(pipelineContent);
            const inputSchema = pipeline.input_schema;

            if (!inputSchema || !inputSchema.properties) {
                // No input schema, continue without prompting
                return {};
            }

            const properties = inputSchema.properties as Record<string, any>;
            const required = new Set(inputSchema.required || []);

            // Check if there are any required fields
            if (required.size === 0) {
                // No required fields, continue without prompting
                return {};
            }

            // Build quick pick items for input method
            const inputMethod = await vscode.window.showQuickPick([
                { label: '$(edit) Enter Values', description: 'Fill in required fields one by one' },
                { label: '$(json) Enter JSON', description: 'Type full JSON input directly' },
                { label: '$(file) Select File', description: 'Choose an input JSON file' },
                { label: '$(debug-start) Skip', description: 'Run with empty/default values' },
            ], {
                placeHolder: `Pipeline has ${required.size} required input(s). How would you like to provide input?`,
            });

            if (!inputMethod) {
                // User cancelled
                return undefined;
            }

            if (inputMethod.label.includes('Skip')) {
                return {};
            }

            if (inputMethod.label.includes('JSON')) {
                const jsonInput = await vscode.window.showInputBox({
                    prompt: 'Enter JSON input',
                    placeHolder: '{"key": "value"}',
                    validateInput: (value) => {
                        try {
                            JSON.parse(value);
                            return null;
                        } catch {
                            return 'Invalid JSON';
                        }
                    },
                });
                return jsonInput ? JSON.parse(jsonInput) : undefined;
            }

            if (inputMethod.label.includes('File')) {
                const files = await vscode.window.showOpenDialog({
                    canSelectFiles: true,
                    canSelectFolders: false,
                    canSelectMany: false,
                    filters: { 'JSON files': ['json'] },
                    title: 'Select Input File',
                });
                if (files && files.length > 0) {
                    const content = fs.readFileSync(files[0].fsPath, 'utf-8');
                    return JSON.parse(content);
                }
                return undefined;
            }

            // Enter values one by one
            const inputs: Record<string, unknown> = {};

            for (const [fieldName, schema] of Object.entries(properties)) {
                const prop = schema as any;
                const isRequired = required.has(fieldName);

                if (!isRequired && prop.default !== undefined) {
                    // Skip optional fields with defaults
                    inputs[fieldName] = prop.default;
                    continue;
                }

                const placeholder = prop.examples?.[0]
                    ? `e.g. ${typeof prop.examples[0] === 'object' ? JSON.stringify(prop.examples[0]) : prop.examples[0]}`
                    : prop.default !== undefined
                    ? `Default: ${prop.default}`
                    : undefined;

                const value = await vscode.window.showInputBox({
                    prompt: `${fieldName}${isRequired ? ' (required)' : ''}: ${prop.description || ''}`,
                    placeHolder: placeholder,
                    validateInput: isRequired ? (v) => v ? null : 'This field is required' : undefined,
                });

                if (value === undefined && isRequired) {
                    // User cancelled on a required field
                    return undefined;
                }

                if (value !== undefined && value !== '') {
                    // Try to parse as JSON for objects/arrays/numbers
                    if (prop.type === 'object' || prop.type === 'array') {
                        try {
                            inputs[fieldName] = JSON.parse(value);
                        } catch {
                            inputs[fieldName] = value;
                        }
                    } else if (prop.type === 'number' || prop.type === 'integer') {
                        inputs[fieldName] = Number(value);
                    } else if (prop.type === 'boolean') {
                        inputs[fieldName] = value.toLowerCase() === 'true';
                    } else {
                        inputs[fieldName] = value;
                    }
                } else if (prop.default !== undefined) {
                    inputs[fieldName] = prop.default;
                }
            }

            return inputs;
        } catch (error) {
            // If there's an error reading schema, just continue without prompting
            console.error('Error prompting for inputs:', error);
            return {};
        }
    }

    /**
     * Resolve VSCode variables like ${file}, ${workspaceFolder}
     */
    private resolveVariables(value: string, folder: vscode.WorkspaceFolder | undefined): string {
        const editor = vscode.window.activeTextEditor;
        const workspaceFolder = folder?.uri.fsPath || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';

        return value
            .replace(/\$\{file\}/g, editor?.document.fileName || '')
            .replace(/\$\{workspaceFolder\}/g, workspaceFolder)
            .replace(/\$\{fileBasename\}/g, editor ? path.basename(editor.document.fileName) : '')
            .replace(/\$\{fileBasenameNoExtension\}/g, editor ? path.basename(editor.document.fileName, path.extname(editor.document.fileName)) : '')
            .replace(/\$\{fileDirname\}/g, editor ? path.dirname(editor.document.fileName) : '');
    }
}

/**
 * Debug Adapter Descriptor Factory
 * Creates the debug adapter instance
 */
export class FlowMasonDebugAdapterDescriptorFactory implements vscode.DebugAdapterDescriptorFactory {
    createDebugAdapterDescriptor(
        session: vscode.DebugSession,
        executable: vscode.DebugAdapterExecutable | undefined
    ): vscode.ProviderResult<vscode.DebugAdapterDescriptor> {
        // Import here to avoid circular dependency
        const { FlowMasonDebugSession } = require('./flowmasonDebugSession');
        return new vscode.DebugAdapterInlineImplementation(new FlowMasonDebugSession());
    }
}

/**
 * Register debug commands
 */
export function registerDebugCommands(context: vscode.ExtensionContext): void {
    // Debug Pipeline command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.debugPipeline', async () => {
            const editor = vscode.window.activeTextEditor;
            const { DagCanvasProvider } = await import('../editors/dagCanvasProvider');

            // Check text editor first, then DAG canvas
            let pipelineFile: string | undefined;
            if (editor?.document.fileName.endsWith('.pipeline.json')) {
                pipelineFile = editor.document.fileName;
            } else if (DagCanvasProvider.currentDocument?.fileName.endsWith('.pipeline.json')) {
                pipelineFile = DagCanvasProvider.currentDocument.fileName;
            }

            if (!pipelineFile) {
                vscode.window.showWarningMessage('Open a .pipeline.json file to debug');
                return;
            }

            // Start debugging with the current file
            await vscode.debug.startDebugging(undefined, {
                type: 'flowmason',
                name: 'Debug Pipeline',
                request: 'launch',
                pipeline: pipelineFile,
                stopOnEntry: true,
            });
        })
    );

    // Run Pipeline (without debugging) - Direct API call
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.runPipeline', async () => {
            const editor = vscode.window.activeTextEditor;
            const { DagCanvasProvider } = await import('../editors/dagCanvasProvider');

            // Check text editor first, then DAG canvas
            let pipelineFile: string | undefined;
            if (editor?.document.fileName.endsWith('.pipeline.json')) {
                pipelineFile = editor.document.fileName;
            } else if (DagCanvasProvider.currentDocument?.fileName.endsWith('.pipeline.json')) {
                pipelineFile = DagCanvasProvider.currentDocument.fileName;
            }

            if (!pipelineFile) {
                vscode.window.showWarningMessage('Open a .pipeline.json file to run');
                return;
            }

            // Run directly via API without debug infrastructure
            await runPipelineDirectly(pipelineFile, context);
        })
    );

    // Debug Pipeline with Input command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.debugPipelineWithInput', async () => {
            const editor = vscode.window.activeTextEditor;
            const { DagCanvasProvider } = await import('../editors/dagCanvasProvider');

            // Check text editor first, then DAG canvas
            let pipelineFile: string | undefined;
            if (editor?.document.fileName.endsWith('.pipeline.json')) {
                pipelineFile = editor.document.fileName;
            } else if (DagCanvasProvider.currentDocument?.fileName.endsWith('.pipeline.json')) {
                pipelineFile = DagCanvasProvider.currentDocument.fileName;
            }

            if (!pipelineFile) {
                vscode.window.showWarningMessage('Open a .pipeline.json file to debug');
                return;
            }

            // Ask for input method
            const inputMethod = await vscode.window.showQuickPick([
                { label: 'Enter JSON', description: 'Type JSON input directly' },
                { label: 'Select File', description: 'Choose an input JSON file' },
                { label: 'No Input', description: 'Run without input' },
            ], { placeHolder: 'How would you like to provide input?' });

            if (!inputMethod) return;

            let debugConfig: vscode.DebugConfiguration = {
                type: 'flowmason',
                name: 'Debug Pipeline',
                request: 'launch',
                pipeline: pipelineFile,
                stopOnEntry: true,
            };

            if (inputMethod.label === 'Enter JSON') {
                const jsonInput = await vscode.window.showInputBox({
                    prompt: 'Enter JSON input',
                    placeHolder: '{"key": "value"}',
                    validateInput: (value) => {
                        try {
                            JSON.parse(value);
                            return null;
                        } catch {
                            return 'Invalid JSON';
                        }
                    },
                });
                if (jsonInput) {
                    debugConfig.input = JSON.parse(jsonInput);
                }
            } else if (inputMethod.label === 'Select File') {
                const files = await vscode.window.showOpenDialog({
                    canSelectFiles: true,
                    canSelectFolders: false,
                    canSelectMany: false,
                    filters: { 'JSON files': ['json'] },
                    title: 'Select Input File',
                });
                if (files && files.length > 0) {
                    debugConfig.inputFile = files[0].fsPath;
                }
            }

            await vscode.debug.startDebugging(undefined, debugConfig);
        })
    );

    // Toggle Breakpoint command for pipeline stages
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.toggleBreakpoint', async () => {
            const editor = vscode.window.activeTextEditor;

            if (!editor || !editor.document.fileName.endsWith('.pipeline.json')) {
                vscode.window.showWarningMessage('Open a .pipeline.json file to set breakpoints');
                return;
            }

            // Toggle breakpoint at current line
            const line = editor.selection.active.line;
            const uri = editor.document.uri;

            // Get existing breakpoints
            const breakpoints = vscode.debug.breakpoints.filter(
                bp => bp instanceof vscode.SourceBreakpoint &&
                      (bp as vscode.SourceBreakpoint).location.uri.toString() === uri.toString() &&
                      (bp as vscode.SourceBreakpoint).location.range.start.line === line
            );

            if (breakpoints.length > 0) {
                // Remove existing breakpoint
                vscode.debug.removeBreakpoints(breakpoints);
            } else {
                // Add new breakpoint
                const breakpoint = new vscode.SourceBreakpoint(
                    new vscode.Location(uri, new vscode.Position(line, 0))
                );
                vscode.debug.addBreakpoints([breakpoint]);
            }
        })
    );
}

/**
 * Run pipeline directly via API without debug infrastructure
 */
async function runPipelineDirectly(pipelineFile: string, context: vscode.ExtensionContext): Promise<void> {
    const axios = await import('axios');
    const outputChannel = vscode.window.createOutputChannel('FlowMason Run');
    outputChannel.show(true);

    try {
        // Read pipeline file
        const pipelineContent = fs.readFileSync(pipelineFile, 'utf-8');
        const pipeline = JSON.parse(pipelineContent);

        outputChannel.appendLine(`🚀 Running pipeline: ${pipeline.name || path.basename(pipelineFile)}`);
        outputChannel.appendLine('');

        // Get inputs
        const inputSchema = pipeline.input_schema;
        let inputs: Record<string, unknown> = {};

        if (inputSchema?.properties && inputSchema.required?.length > 0) {
            // Prompt for inputs
            const inputMethod = await vscode.window.showQuickPick([
                { label: '$(edit) Enter Values', description: 'Fill in required fields one by one' },
                { label: '$(json) Enter JSON', description: 'Type full JSON input directly' },
                { label: '$(file) Select File', description: 'Choose an input JSON file' },
                { label: '$(debug-start) Skip', description: 'Run with empty/default values' },
            ], {
                placeHolder: `Pipeline has ${inputSchema.required.length} required input(s). How would you like to provide input?`,
            });

            if (!inputMethod) {
                outputChannel.appendLine('❌ Run cancelled');
                return;
            }

            if (inputMethod.label.includes('JSON')) {
                const jsonInput = await vscode.window.showInputBox({
                    prompt: 'Enter JSON input',
                    placeHolder: '{"key": "value"}',
                });
                if (jsonInput) {
                    inputs = JSON.parse(jsonInput);
                }
            } else if (inputMethod.label.includes('File')) {
                const files = await vscode.window.showOpenDialog({
                    canSelectFiles: true,
                    filters: { 'JSON files': ['json'] },
                    title: 'Select Input File',
                });
                if (files && files.length > 0) {
                    const content = fs.readFileSync(files[0].fsPath, 'utf-8');
                    inputs = JSON.parse(content);
                }
            } else if (inputMethod.label.includes('Enter Values')) {
                const properties = inputSchema.properties as Record<string, any>;
                const required = new Set(inputSchema.required || []);

                for (const [fieldName, schema] of Object.entries(properties)) {
                    const prop = schema as any;
                    const isRequired = required.has(fieldName);

                    if (!isRequired && prop.default !== undefined) {
                        inputs[fieldName] = prop.default;
                        continue;
                    }

                    const value = await vscode.window.showInputBox({
                        prompt: `${fieldName}${isRequired ? ' (required)' : ''}: ${prop.description || ''}`,
                        placeHolder: prop.examples?.[0] ? `e.g. ${prop.examples[0]}` : undefined,
                    });

                    if (value === undefined && isRequired) {
                        outputChannel.appendLine('❌ Run cancelled');
                        return;
                    }

                    if (value) {
                        if (prop.type === 'number' || prop.type === 'integer') {
                            inputs[fieldName] = Number(value);
                        } else {
                            inputs[fieldName] = value;
                        }
                    } else if (prop.default !== undefined) {
                        inputs[fieldName] = prop.default;
                    }
                }
            }
        }

        outputChannel.appendLine(`📥 Inputs: ${JSON.stringify(inputs, null, 2)}`);
        outputChannel.appendLine('');

        // Get studio URL
        const settings = vscode.workspace.getConfiguration('flowmason');
        const studioUrl = settings.get<string>('studioUrl') || 'http://localhost:8999';

        outputChannel.appendLine('⏳ Executing pipeline...');
        const startTime = Date.now();

        // Call the debug/run API (works with inline pipeline definition)
        const startResponse = await axios.default.post(`${studioUrl}/api/v1/debug/run`, {
            pipeline: pipeline,
            inputs: inputs,
            breakpoints: [],
            stop_on_entry: false,
        }, {
            timeout: 30000,
        });

        const runId = startResponse.data.id;
        outputChannel.appendLine(`   Run ID: ${runId}`);

        // Poll for completion
        let status = 'running';
        let result: any = null;
        const pollInterval = 1000; // 1 second
        const maxWait = 300000; // 5 minutes

        while (status === 'running' || status === 'paused') {
            const elapsed = Date.now() - startTime;
            if (elapsed > maxWait) {
                throw new Error('Pipeline execution timed out');
            }

            await new Promise(resolve => setTimeout(resolve, pollInterval));

            const statusResponse = await axios.default.get(`${studioUrl}/api/v1/runs/${runId}`);
            status = statusResponse.data.status;
            result = statusResponse.data;

            // Show progress (stage_results is an object keyed by stage_id)
            if (result.stage_results && typeof result.stage_results === 'object') {
                const stageIds = Object.keys(result.stage_results);
                const lastStageId = stageIds[stageIds.length - 1];
                if (lastStageId) {
                    const currentStage = result.stage_results[lastStageId];
                    outputChannel.appendLine(`   Stage: ${lastStageId} - ${currentStage?.status || 'running'}`);
                }
            }
        }

        const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

        if (status === 'completed') {
            outputChannel.appendLine('');
            outputChannel.appendLine(`✅ Pipeline completed successfully in ${elapsed}s`);
            outputChannel.appendLine('');
            outputChannel.appendLine('📤 Output:');
            outputChannel.appendLine(JSON.stringify(result.output || result.stage_results, null, 2));
        } else {
            outputChannel.appendLine('');
            outputChannel.appendLine(`❌ Pipeline failed after ${elapsed}s`);
            outputChannel.appendLine('');
            outputChannel.appendLine('Error: ' + (result.error || result.status || 'Unknown error'));
            if (result.stage_results && typeof result.stage_results === 'object') {
                // stage_results is an object keyed by stage_id
                for (const [stageId, stageResult] of Object.entries(result.stage_results)) {
                    const stage = stageResult as any;
                    if (stage?.status === 'failed') {
                        outputChannel.appendLine('');
                        outputChannel.appendLine(`Failed stage: ${stageId}`);
                        outputChannel.appendLine('Error: ' + (stage.error || 'Unknown'));
                        break;
                    }
                }
            }
        }

    } catch (error: any) {
        outputChannel.appendLine('');
        outputChannel.appendLine('❌ Pipeline execution failed');
        outputChannel.appendLine('');
        if (error.response?.data) {
            outputChannel.appendLine('Error: ' + JSON.stringify(error.response.data, null, 2));
        } else {
            outputChannel.appendLine('Error: ' + (error.message || String(error)));
        }
    }
}
