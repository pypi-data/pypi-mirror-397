"use strict";
/**
 * FlowMason VSCode Extension
 *
 * Development tools for building FlowMason nodes and operators.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
// Commands
const newNode_1 = require("./commands/newNode");
const newOperator_1 = require("./commands/newOperator");
const buildPackage_1 = require("./commands/buildPackage");
const testComponent_1 = require("./commands/testComponent");
const openStudio_1 = require("./commands/openStudio");
const previewComponent_1 = require("./commands/previewComponent");
const deployPackage_1 = require("./commands/deployPackage");
const validateManifest_1 = require("./commands/validateManifest");
const openDocs_1 = require("./commands/openDocs");
const newProject_1 = require("./commands/newProject");
const manageStudio_1 = require("./commands/manageStudio");
const importPackage_1 = require("./commands/importPackage");
const mcpCommands_1 = require("./commands/mcpCommands");
const privateRegistry_1 = require("./commands/privateRegistry");
// Providers
const completionProvider_1 = require("./providers/completionProvider");
const diagnosticsProvider_1 = require("./providers/diagnosticsProvider");
const hoverProvider_1 = require("./providers/hoverProvider");
const codeLensProvider_1 = require("./providers/codeLensProvider");
const codeActionProvider_1 = require("./providers/codeActionProvider");
const definitionProvider_1 = require("./providers/definitionProvider");
const documentSymbolProvider_1 = require("./providers/documentSymbolProvider");
const pipelineSymbolProvider_1 = require("./providers/pipelineSymbolProvider");
const pipelineDiagnosticsProvider_1 = require("./providers/pipelineDiagnosticsProvider");
// Views
const componentsTree_1 = require("./views/componentsTree");
const packagesTree_1 = require("./views/packagesTree");
const pipelinesTree_1 = require("./views/pipelinesTree");
const pipelineStagesTree_1 = require("./views/pipelineStagesTree");
const stageConfigView_1 = require("./views/stageConfigView");
const marketplaceTree_1 = require("./views/marketplaceTree");
const timeTravelTree_1 = require("./views/timeTravelTree");
// Commands
const addStage_1 = require("./commands/addStage");
// Editors
const dagCanvasProvider_1 = require("./editors/dagCanvasProvider");
const jsonTreeViewProvider_1 = require("./editors/jsonTreeViewProvider");
const pipelineDiffProvider_1 = require("./editors/pipelineDiffProvider");
// Services
const flowmasonService_1 = require("./services/flowmasonService");
const componentParser_1 = require("./services/componentParser");
const mcpService_1 = require("./services/mcpService");
// Status Bar
const statusBar_1 = require("./statusBar");
// Debug Adapter
const debug_1 = require("./debug");
// Testing
const testing_1 = require("./testing");
// Webhook Server
const webhookServer_1 = require("./services/webhookServer");
// Output channel for extension logging
let outputChannel;
function activate(context) {
    // Create output channel
    outputChannel = vscode.window.createOutputChannel('FlowMason');
    context.subscriptions.push(outputChannel);
    outputChannel.appendLine('FlowMason extension activating...');
    // Initialize services
    const flowmasonService = new flowmasonService_1.FlowMasonService();
    const componentParser = new componentParser_1.ComponentParser();
    const mcpService = new mcpService_1.MCPService(outputChannel);
    // Register tree view providers
    const componentsProvider = new componentsTree_1.ComponentsTreeProvider(flowmasonService, componentParser);
    const packagesProvider = new packagesTree_1.PackagesTreeProvider(flowmasonService);
    const pipelinesProvider = new pipelinesTree_1.PipelinesTreeProvider(flowmasonService);
    const pipelineStagesProvider = new pipelineStagesTree_1.PipelineStagesTreeProvider();
    const stageConfigProvider = new stageConfigView_1.StageConfigViewProvider(context.extensionUri, flowmasonService);
    vscode.window.registerTreeDataProvider('flowmason.components', componentsProvider);
    vscode.window.registerTreeDataProvider('flowmason.packages', packagesProvider);
    vscode.window.registerTreeDataProvider('flowmason.pipelines', pipelinesProvider);
    vscode.window.registerTreeDataProvider('flowmason.pipelineStages', pipelineStagesProvider);
    vscode.window.registerWebviewViewProvider(stageConfigView_1.StageConfigViewProvider.viewType, stageConfigProvider);
    // Register pipeline stages commands
    (0, pipelineStagesTree_1.registerPipelineStagesCommands)(context);
    (0, stageConfigView_1.registerStageConfigCommands)(context, stageConfigProvider);
    (0, addStage_1.registerAddStageCommand)(context, flowmasonService);
    // Register DAG Canvas custom editor
    context.subscriptions.push((0, dagCanvasProvider_1.registerDagCanvasProvider)(context));
    // Register JSON Tree View (read-only) custom editor
    context.subscriptions.push((0, jsonTreeViewProvider_1.registerJsonTreeViewProvider)());
    // Register Pipeline Diff Provider (P5.2)
    const pipelineDiffProvider = new pipelineDiffProvider_1.PipelineDiffProvider(context);
    (0, pipelineDiffProvider_1.registerPipelineDiffCommands)(context, pipelineDiffProvider);
    // Register open DAG canvas command
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.openDagCanvas', async () => {
        const editor = vscode.window.activeTextEditor;
        if (editor && editor.document.fileName.endsWith('.pipeline.json')) {
            await vscode.commands.executeCommand('vscode.openWith', editor.document.uri, 'flowmason.dagCanvas');
        }
        else {
            vscode.window.showWarningMessage('Open a .pipeline.json file first');
        }
    }));
    // Register refresh pipeline stages command
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.refreshPipelineStages', () => {
        pipelineStagesProvider.refresh();
    }));
    // Register commands
    (0, newNode_1.registerNewNodeCommand)(context);
    (0, newOperator_1.registerNewOperatorCommand)(context);
    (0, buildPackage_1.registerBuildPackageCommand)(context, outputChannel);
    (0, testComponent_1.registerTestComponentCommand)(context, flowmasonService, outputChannel);
    (0, openStudio_1.registerOpenStudioCommand)(context);
    (0, previewComponent_1.registerPreviewComponentCommand)(context, componentParser);
    (0, deployPackage_1.registerDeployPackageCommand)(context, outputChannel);
    (0, validateManifest_1.registerValidateManifestCommand)(context, outputChannel);
    (0, openDocs_1.registerOpenDocsCommand)(context);
    (0, newProject_1.registerNewProjectCommand)(context);
    (0, manageStudio_1.registerManageStudioCommands)(context, outputChannel);
    (0, importPackage_1.registerImportPackageCommand)(context, outputChannel);
    // Register MCP commands for AI-assisted pipeline creation
    (0, mcpCommands_1.registerMCPCommands)(context, mcpService, outputChannel);
    // Register private registry commands
    (0, privateRegistry_1.registerPrivateRegistryCommands)(context, flowmasonService, outputChannel);
    // Register refresh command for components tree
    context.subscriptions.push(vscode.commands.registerCommand('flowmason.refreshRegistry', () => {
        componentsProvider.refresh();
        packagesProvider.refresh();
        pipelinesProvider.refresh();
        vscode.window.showInformationMessage('FlowMason registry refreshed');
    }));
    // Register language providers for Python files
    const pythonSelector = { language: 'python', scheme: 'file' };
    // Completion provider for FlowMason decorators and patterns
    context.subscriptions.push(vscode.languages.registerCompletionItemProvider(pythonSelector, new completionProvider_1.FlowMasonCompletionProvider(), '@', '.', '('));
    // Hover provider for FlowMason documentation
    context.subscriptions.push(vscode.languages.registerHoverProvider(pythonSelector, new hoverProvider_1.FlowMasonHoverProvider()));
    // CodeLens provider for execute methods
    context.subscriptions.push(vscode.languages.registerCodeLensProvider(pythonSelector, new codeLensProvider_1.FlowMasonCodeLensProvider(componentParser)));
    // Register run component inline command
    (0, codeLensProvider_1.registerRunComponentInlineCommand)(context, outputChannel);
    // Code action provider for quick fixes
    context.subscriptions.push(vscode.languages.registerCodeActionsProvider(pythonSelector, new codeActionProvider_1.FlowMasonCodeActionProvider(), {
        providedCodeActionKinds: codeActionProvider_1.FlowMasonCodeActionProvider.providedCodeActionKinds
    }));
    // Definition provider for Go to Definition
    context.subscriptions.push(vscode.languages.registerDefinitionProvider(pythonSelector, new definitionProvider_1.FlowMasonDefinitionProvider(componentParser)));
    // Reference provider for Find All References
    context.subscriptions.push(vscode.languages.registerReferenceProvider(pythonSelector, new definitionProvider_1.FlowMasonReferenceProvider(componentParser)));
    // Document symbol provider for Outline view
    context.subscriptions.push(vscode.languages.registerDocumentSymbolProvider(pythonSelector, new documentSymbolProvider_1.FlowMasonDocumentSymbolProvider(componentParser)));
    // Diagnostics provider for FlowMason validation (Python)
    const diagnosticsProvider = new diagnosticsProvider_1.FlowMasonDiagnosticsProvider();
    context.subscriptions.push(diagnosticsProvider);
    // Pipeline diagnostics provider (JSON)
    const pipelineDiagnosticsProvider = new pipelineDiagnosticsProvider_1.PipelineDiagnosticsProvider(flowmasonService);
    context.subscriptions.push(pipelineDiagnosticsProvider);
    // Pipeline symbol provider for Outline view
    const jsonSelector = { language: 'json', pattern: '**/*.pipeline.json' };
    context.subscriptions.push(vscode.languages.registerDocumentSymbolProvider(jsonSelector, new pipelineSymbolProvider_1.PipelineSymbolProvider()));
    // Watch for document changes to update diagnostics
    context.subscriptions.push(vscode.workspace.onDidChangeTextDocument(event => {
        if (event.document.languageId === 'python') {
            diagnosticsProvider.updateDiagnostics(event.document);
        }
    }));
    // Update diagnostics for active document
    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor(editor => {
        if (editor && editor.document.languageId === 'python') {
            diagnosticsProvider.updateDiagnostics(editor.document);
        }
    }));
    // Initial diagnostics for currently open document
    if (vscode.window.activeTextEditor?.document.languageId === 'python') {
        diagnosticsProvider.updateDiagnostics(vscode.window.activeTextEditor.document);
    }
    // Watch for component preview on save (if enabled)
    const config = vscode.workspace.getConfiguration('flowmason');
    if (config.get('autoPreview')) {
        context.subscriptions.push(vscode.workspace.onDidSaveTextDocument(document => {
            if (document.languageId === 'python') {
                const content = document.getText();
                if (content.includes('@node') || content.includes('@operator')) {
                    vscode.commands.executeCommand('flowmason.previewComponent');
                }
            }
        }));
    }
    // Check FlowMason Studio connection on startup with improved feedback
    flowmasonService.checkConnection().then(connected => {
        if (connected) {
            outputChannel.appendLine('Connected to FlowMason Studio');
        }
        else {
            outputChannel.appendLine('FlowMason Studio not running');
            // Show notification with action to start Studio
            vscode.window.showInformationMessage('FlowMason Studio is not running. Start it to enable full functionality.', 'Start Studio', 'Dismiss').then(action => {
                if (action === 'Start Studio') {
                    vscode.commands.executeCommand('flowmason.startStudio');
                }
            });
        }
    });
    // Create status bar with Studio status and quick actions
    (0, statusBar_1.createStudioStatusBar)(context);
    // Register Debug Adapter
    const debugConfigProvider = new debug_1.FlowMasonDebugConfigurationProvider();
    const debugAdapterFactory = new debug_1.FlowMasonDebugAdapterDescriptorFactory();
    context.subscriptions.push(vscode.debug.registerDebugConfigurationProvider('flowmason', debugConfigProvider));
    context.subscriptions.push(vscode.debug.registerDebugAdapterDescriptorFactory('flowmason', debugAdapterFactory));
    // Register debug commands
    (0, debug_1.registerDebugCommands)(context);
    // Register Prompt Editor View
    const promptEditorProvider = new debug_1.PromptEditorViewProvider(context.extensionUri);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider(debug_1.PromptEditorViewProvider.viewType, promptEditorProvider));
    (0, debug_1.registerPromptEditorCommands)(context, promptEditorProvider);
    outputChannel.appendLine('FlowMason Debug Adapter registered');
    // Register Test Controller
    const testController = new testing_1.FlowMasonTestController(context);
    context.subscriptions.push({ dispose: () => testController.dispose() });
    (0, testing_1.registerTestCommands)(context);
    (0, testing_1.registerCoverageCommands)(context);
    outputChannel.appendLine('FlowMason Test Controller registered');
    // Register Webhook Server
    const webhookServer = (0, webhookServer_1.registerWebhookServer)(context);
    outputChannel.appendLine('FlowMason Webhook Server registered (port configurable in settings)');
    // Register Marketplace
    const marketplaceProvider = (0, marketplaceTree_1.registerMarketplaceCommands)(context, flowmasonService, outputChannel);
    outputChannel.appendLine('FlowMason Marketplace registered');
    // Register Time Travel Debugger
    const timeTravelProvider = (0, timeTravelTree_1.registerTimeTravelCommands)(context, flowmasonService, outputChannel);
    outputChannel.appendLine('FlowMason Time Travel Debugger registered');
    // Watch for Python file changes to auto-refresh component registry
    const fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.py');
    // Debounce refresh to avoid excessive updates
    let refreshTimeout;
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
function deactivate() {
    if (outputChannel) {
        outputChannel.appendLine('FlowMason extension deactivating...');
        outputChannel.dispose();
    }
}
//# sourceMappingURL=extension.js.map