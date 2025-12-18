/**
 * FlowMason VSCode Extension
 *
 * Development tools for building FlowMason nodes and operators.
 */

import * as vscode from 'vscode';

// Commands
import { registerNewNodeCommand } from './commands/newNode';
import { registerNewOperatorCommand } from './commands/newOperator';
import { registerBuildPackageCommand } from './commands/buildPackage';
import { registerTestComponentCommand } from './commands/testComponent';
import { registerOpenStudioCommand } from './commands/openStudio';
import { registerPreviewComponentCommand } from './commands/previewComponent';
import { registerDeployPackageCommand } from './commands/deployPackage';
import { registerValidateManifestCommand } from './commands/validateManifest';
import { registerOpenDocsCommand } from './commands/openDocs';
import { registerNewProjectCommand } from './commands/newProject';
import { registerManageStudioCommands } from './commands/manageStudio';
import { registerImportPackageCommand } from './commands/importPackage';
import { registerMCPCommands } from './commands/mcpCommands';
import { registerPrivateRegistryCommands } from './commands/privateRegistry';

// Providers
import { FlowMasonCompletionProvider } from './providers/completionProvider';
import { FlowMasonDiagnosticsProvider } from './providers/diagnosticsProvider';
import { FlowMasonHoverProvider } from './providers/hoverProvider';
import { FlowMasonCodeLensProvider, registerRunComponentInlineCommand } from './providers/codeLensProvider';
import { FlowMasonCodeActionProvider } from './providers/codeActionProvider';
import { FlowMasonDefinitionProvider, FlowMasonReferenceProvider } from './providers/definitionProvider';
import { FlowMasonDocumentSymbolProvider } from './providers/documentSymbolProvider';
import { PipelineSymbolProvider } from './providers/pipelineSymbolProvider';
import { PipelineDiagnosticsProvider } from './providers/pipelineDiagnosticsProvider';

// Views
import { ComponentsTreeProvider } from './views/componentsTree';
import { PackagesTreeProvider } from './views/packagesTree';
import { PipelinesTreeProvider } from './views/pipelinesTree';
import { PipelineStagesTreeProvider, registerPipelineStagesCommands } from './views/pipelineStagesTree';
import { StageConfigViewProvider, registerStageConfigCommands } from './views/stageConfigView';
import { MarketplaceTreeProvider, registerMarketplaceCommands } from './views/marketplaceTree';
import { TimeTravelTreeProvider, registerTimeTravelCommands } from './views/timeTravelTree';

// Commands
import { registerAddStageCommand } from './commands/addStage';

// Editors
import { registerDagCanvasProvider, DagCanvasProvider } from './editors/dagCanvasProvider';
import { registerJsonTreeViewProvider } from './editors/jsonTreeViewProvider';
import { StageConfigEditor } from './editors/stageConfigEditor';
import { PipelineDiffProvider, registerPipelineDiffCommands } from './editors/pipelineDiffProvider';

// Services
import { FlowMasonService } from './services/flowmasonService';
import { ComponentParser } from './services/componentParser';
import { MCPService } from './services/mcpService';

// Status Bar
import { createStudioStatusBar } from './statusBar';

// Debug Adapter
import {
    FlowMasonDebugConfigurationProvider,
    FlowMasonDebugAdapterDescriptorFactory,
    registerDebugCommands,
    PromptEditorViewProvider,
    registerPromptEditorCommands,
} from './debug';

// Testing
import { FlowMasonTestController, registerTestCommands, registerCoverageCommands } from './testing';

// Webhook Server
import { registerWebhookServer } from './services/webhookServer';

// Output channel for extension logging
let outputChannel: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
    // Create output channel
    outputChannel = vscode.window.createOutputChannel('FlowMason');
    context.subscriptions.push(outputChannel);

    outputChannel.appendLine('FlowMason extension activating...');

    // Initialize services
    const flowmasonService = new FlowMasonService();
    const componentParser = new ComponentParser();
    const mcpService = new MCPService(outputChannel);

    // Register tree view providers
    const componentsProvider = new ComponentsTreeProvider(flowmasonService, componentParser);
    const packagesProvider = new PackagesTreeProvider(flowmasonService);
    const pipelinesProvider = new PipelinesTreeProvider(flowmasonService);
    const pipelineStagesProvider = new PipelineStagesTreeProvider();
    const stageConfigProvider = new StageConfigViewProvider(context.extensionUri, flowmasonService);

    vscode.window.registerTreeDataProvider('flowmason.components', componentsProvider);
    vscode.window.registerTreeDataProvider('flowmason.packages', packagesProvider);
    vscode.window.registerTreeDataProvider('flowmason.pipelines', pipelinesProvider);
    vscode.window.registerTreeDataProvider('flowmason.pipelineStages', pipelineStagesProvider);
    vscode.window.registerWebviewViewProvider(StageConfigViewProvider.viewType, stageConfigProvider);

    // Register pipeline stages commands
    registerPipelineStagesCommands(context);
    registerStageConfigCommands(context, stageConfigProvider);
    registerAddStageCommand(context, flowmasonService);

    // Register DAG Canvas custom editor
    context.subscriptions.push(registerDagCanvasProvider(context));

    // Register JSON Tree View (read-only) custom editor
    context.subscriptions.push(registerJsonTreeViewProvider());

    // Register Pipeline Diff Provider (P5.2)
    const pipelineDiffProvider = new PipelineDiffProvider(context);
    registerPipelineDiffCommands(context, pipelineDiffProvider);

    // Register open DAG canvas command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.openDagCanvas', async () => {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document.fileName.endsWith('.pipeline.json')) {
                await vscode.commands.executeCommand(
                    'vscode.openWith',
                    editor.document.uri,
                    'flowmason.dagCanvas'
                );
            } else {
                vscode.window.showWarningMessage('Open a .pipeline.json file first');
            }
        })
    );

    // Register refresh pipeline stages command
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.refreshPipelineStages', () => {
            pipelineStagesProvider.refresh();
        })
    );

    // Register commands
    registerNewNodeCommand(context);
    registerNewOperatorCommand(context);
    registerBuildPackageCommand(context, outputChannel);
    registerTestComponentCommand(context, flowmasonService, outputChannel);
    registerOpenStudioCommand(context);
    registerPreviewComponentCommand(context, componentParser);
    registerDeployPackageCommand(context, outputChannel);
    registerValidateManifestCommand(context, outputChannel);
    registerOpenDocsCommand(context);
    registerNewProjectCommand(context);
    registerManageStudioCommands(context, outputChannel);
    registerImportPackageCommand(context, outputChannel);

    // Register MCP commands for AI-assisted pipeline creation
    registerMCPCommands(context, mcpService, outputChannel);

    // Register private registry commands
    registerPrivateRegistryCommands(context, flowmasonService, outputChannel);

    // Register refresh command for components tree
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.refreshRegistry', () => {
            componentsProvider.refresh();
            packagesProvider.refresh();
            pipelinesProvider.refresh();
            vscode.window.showInformationMessage('FlowMason registry refreshed');
        })
    );

    // Register language providers for Python files
    const pythonSelector = { language: 'python', scheme: 'file' };

    // Completion provider for FlowMason decorators and patterns
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(
            pythonSelector,
            new FlowMasonCompletionProvider(),
            '@', '.', '('
        )
    );

    // Hover provider for FlowMason documentation
    context.subscriptions.push(
        vscode.languages.registerHoverProvider(
            pythonSelector,
            new FlowMasonHoverProvider()
        )
    );

    // CodeLens provider for execute methods
    context.subscriptions.push(
        vscode.languages.registerCodeLensProvider(
            pythonSelector,
            new FlowMasonCodeLensProvider(componentParser)
        )
    );

    // Register run component inline command
    registerRunComponentInlineCommand(context, outputChannel);

    // Code action provider for quick fixes
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            pythonSelector,
            new FlowMasonCodeActionProvider(),
            {
                providedCodeActionKinds: FlowMasonCodeActionProvider.providedCodeActionKinds
            }
        )
    );

    // Definition provider for Go to Definition
    context.subscriptions.push(
        vscode.languages.registerDefinitionProvider(
            pythonSelector,
            new FlowMasonDefinitionProvider(componentParser)
        )
    );

    // Reference provider for Find All References
    context.subscriptions.push(
        vscode.languages.registerReferenceProvider(
            pythonSelector,
            new FlowMasonReferenceProvider(componentParser)
        )
    );

    // Document symbol provider for Outline view
    context.subscriptions.push(
        vscode.languages.registerDocumentSymbolProvider(
            pythonSelector,
            new FlowMasonDocumentSymbolProvider(componentParser)
        )
    );

    // Diagnostics provider for FlowMason validation (Python)
    const diagnosticsProvider = new FlowMasonDiagnosticsProvider();
    context.subscriptions.push(diagnosticsProvider);

    // Pipeline diagnostics provider (JSON)
    const pipelineDiagnosticsProvider = new PipelineDiagnosticsProvider(flowmasonService);
    context.subscriptions.push(pipelineDiagnosticsProvider);

    // Pipeline symbol provider for Outline view
    const jsonSelector = { language: 'json', pattern: '**/*.pipeline.json' };
    context.subscriptions.push(
        vscode.languages.registerDocumentSymbolProvider(
            jsonSelector,
            new PipelineSymbolProvider()
        )
    );

    // Watch for document changes to update diagnostics
    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(event => {
            if (event.document.languageId === 'python') {
                diagnosticsProvider.updateDiagnostics(event.document);
            }
        })
    );

    // Update diagnostics for active document
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor && editor.document.languageId === 'python') {
                diagnosticsProvider.updateDiagnostics(editor.document);
            }
        })
    );

    // Initial diagnostics for currently open document
    if (vscode.window.activeTextEditor?.document.languageId === 'python') {
        diagnosticsProvider.updateDiagnostics(vscode.window.activeTextEditor.document);
    }

    // Watch for component preview on save (if enabled)
    const config = vscode.workspace.getConfiguration('flowmason');
    if (config.get<boolean>('autoPreview')) {
        context.subscriptions.push(
            vscode.workspace.onDidSaveTextDocument(document => {
                if (document.languageId === 'python') {
                    const content = document.getText();
                    if (content.includes('@node') || content.includes('@operator')) {
                        vscode.commands.executeCommand('flowmason.previewComponent');
                    }
                }
            })
        );
    }

    // Check FlowMason Studio connection on startup with improved feedback
    flowmasonService.checkConnection().then(connected => {
        if (connected) {
            outputChannel.appendLine('Connected to FlowMason Studio');
        } else {
            outputChannel.appendLine('FlowMason Studio not running');
            // Show notification with action to start Studio
            vscode.window.showInformationMessage(
                'FlowMason Studio is not running. Start it to enable full functionality.',
                'Start Studio',
                'Dismiss'
            ).then(action => {
                if (action === 'Start Studio') {
                    vscode.commands.executeCommand('flowmason.startStudio');
                }
            });
        }
    });

    // Create status bar with Studio status and quick actions
    createStudioStatusBar(context);

    // Register Debug Adapter
    const debugConfigProvider = new FlowMasonDebugConfigurationProvider();
    const debugAdapterFactory = new FlowMasonDebugAdapterDescriptorFactory();

    context.subscriptions.push(
        vscode.debug.registerDebugConfigurationProvider('flowmason', debugConfigProvider)
    );
    context.subscriptions.push(
        vscode.debug.registerDebugAdapterDescriptorFactory('flowmason', debugAdapterFactory)
    );

    // Register debug commands
    registerDebugCommands(context);

    // Register Prompt Editor View
    const promptEditorProvider = new PromptEditorViewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(PromptEditorViewProvider.viewType, promptEditorProvider)
    );
    registerPromptEditorCommands(context, promptEditorProvider);

    outputChannel.appendLine('FlowMason Debug Adapter registered');

    // Register Test Controller
    const testController = new FlowMasonTestController(context);
    context.subscriptions.push({ dispose: () => testController.dispose() });
    registerTestCommands(context);
    registerCoverageCommands(context);
    outputChannel.appendLine('FlowMason Test Controller registered');

    // Register Webhook Server
    const webhookServer = registerWebhookServer(context);
    outputChannel.appendLine('FlowMason Webhook Server registered (port configurable in settings)');

    // Register Marketplace
    const marketplaceProvider = registerMarketplaceCommands(context, flowmasonService, outputChannel);
    outputChannel.appendLine('FlowMason Marketplace registered');

    // Register Time Travel Debugger
    const timeTravelProvider = registerTimeTravelCommands(context, flowmasonService, outputChannel);
    outputChannel.appendLine('FlowMason Time Travel Debugger registered');

    // Watch for Python file changes to auto-refresh component registry
    const fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.py');

    // Debounce refresh to avoid excessive updates
    let refreshTimeout: NodeJS.Timeout | undefined;
    const debouncedRefresh = () => {
        if (refreshTimeout) {
            clearTimeout(refreshTimeout);
        }
        refreshTimeout = setTimeout(() => {
            componentsProvider.refresh();
            outputChannel.appendLine('Component registry refreshed (file change detected)');
        }, 1000);
    };

    fileWatcher.onDidCreate(debouncedRefresh);
    fileWatcher.onDidChange(debouncedRefresh);
    fileWatcher.onDidDelete(debouncedRefresh);
    context.subscriptions.push(fileWatcher);

    // Also watch for flowmason-package.json changes
    const packageWatcher = vscode.workspace.createFileSystemWatcher('**/flowmason-package.json');
    packageWatcher.onDidCreate(() => packagesProvider.refresh());
    packageWatcher.onDidChange(() => packagesProvider.refresh());
    packageWatcher.onDidDelete(() => packagesProvider.refresh());
    context.subscriptions.push(packageWatcher);

    outputChannel.appendLine('FlowMason extension activated');
}

export function deactivate() {
    if (outputChannel) {
        outputChannel.appendLine('FlowMason extension deactivating...');
        outputChannel.dispose();
    }
}
