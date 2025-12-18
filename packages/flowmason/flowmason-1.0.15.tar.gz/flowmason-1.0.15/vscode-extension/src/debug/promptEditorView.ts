/**
 * Prompt Editor View
 *
 * A webview panel for editing and iterating on prompts during debug sessions.
 * Allows users to modify prompts, re-run stages, and compare outputs.
 */

import * as vscode from 'vscode';

interface PromptVersion {
    id: string;
    timestamp: Date;
    systemPrompt: string;
    userPrompt: string;
    output?: string;
    tokens?: {
        input: number;
        output: number;
    };
    durationMs?: number;
}

interface ComparisonState {
    enabled: boolean;
    leftVersion?: PromptVersion;
    rightVersion?: PromptVersion;
}

interface StagePromptInfo {
    stageId: string;
    stageName: string;
    componentType: string;
    systemPrompt: string;
    userPrompt: string;
    variables: Record<string, unknown>;
    output?: string;
}

/**
 * Prompt Editor View Provider
 * Shows in the sidebar during debug sessions
 */
export class PromptEditorViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'flowmason.promptEditor';

    private _view?: vscode.WebviewView;
    private _currentPrompt?: StagePromptInfo;
    private _promptVersions: Map<string, PromptVersion[]> = new Map();
    private _comparisonState: ComparisonState = { enabled: false };
    private _onPromptChange = new vscode.EventEmitter<{
        stageId: string;
        systemPrompt: string;
        userPrompt: string;
    }>();
    public readonly onPromptChange = this._onPromptChange.event;

    private _onRerunRequest = new vscode.EventEmitter<{
        stageId: string;
        systemPrompt: string;
        userPrompt: string;
    }>();
    public readonly onRerunRequest = this._onRerunRequest.event;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        token: vscode.CancellationToken
    ): void {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri],
        };

        webviewView.webview.html = this._getHtmlContent();

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(message => {
            switch (message.type) {
                case 'rerun':
                    this._onRerunRequest.fire({
                        stageId: message.stageId,
                        systemPrompt: message.systemPrompt,
                        userPrompt: message.userPrompt,
                    });
                    break;
                case 'saveVersion':
                    this._savePromptVersion(
                        message.stageId,
                        message.systemPrompt,
                        message.userPrompt
                    );
                    break;
                case 'loadVersion':
                    this._loadPromptVersion(message.stageId, message.versionId);
                    break;
                case 'toggleComparison':
                    this._toggleComparison(message.stageId);
                    break;
                case 'selectForComparison':
                    this._selectForComparison(message.stageId, message.versionId, message.side);
                    break;
                case 'promptChanged':
                    this._onPromptChange.fire({
                        stageId: message.stageId,
                        systemPrompt: message.systemPrompt,
                        userPrompt: message.userPrompt,
                    });
                    break;
            }
        });
    }

    /**
     * Show prompt for a stage
     */
    public showPrompt(info: StagePromptInfo): void {
        this._currentPrompt = info;

        if (this._view) {
            this._view.webview.postMessage({
                type: 'showPrompt',
                data: {
                    ...info,
                    versions: this._promptVersions.get(info.stageId) || [],
                },
            });
            this._view.show?.(true);
        }
    }

    /**
     * Update output after re-run
     */
    public updateOutput(stageId: string, output: string, tokens?: { input: number; output: number }): void {
        if (this._view && this._currentPrompt?.stageId === stageId) {
            this._view.webview.postMessage({
                type: 'updateOutput',
                data: { output, tokens },
            });
        }
    }

    /**
     * Signal that streaming is starting for a stage
     */
    public streamStart(stageId: string, stageName?: string): void {
        if (this._view && this._currentPrompt?.stageId === stageId) {
            this._view.webview.postMessage({
                type: 'streamStart',
                data: { stageId, stageName },
            });
        }
    }

    /**
     * Show streaming output chunk
     */
    public streamOutput(stageId: string, chunk: string, tokenIndex?: number): void {
        if (this._view && this._currentPrompt?.stageId === stageId) {
            this._view.webview.postMessage({
                type: 'streamChunk',
                data: { chunk, tokenIndex },
            });
        }
    }

    /**
     * Signal that streaming has ended for a stage
     */
    public streamEnd(stageId: string, totalTokens?: number, finalContent?: string): void {
        if (this._view && this._currentPrompt?.stageId === stageId) {
            this._view.webview.postMessage({
                type: 'streamEnd',
                data: { stageId, totalTokens, finalContent },
            });
        }
    }

    /**
     * Clear the prompt editor
     */
    public clear(): void {
        this._currentPrompt = undefined;
        if (this._view) {
            this._view.webview.postMessage({ type: 'clear' });
        }
    }

    /**
     * Save a prompt version
     */
    private _savePromptVersion(
        stageId: string,
        systemPrompt: string,
        userPrompt: string,
        output?: string,
        tokens?: { input: number; output: number },
        durationMs?: number
    ): void {
        const versions = this._promptVersions.get(stageId) || [];
        const version: PromptVersion = {
            id: `v${versions.length + 1}`,
            timestamp: new Date(),
            systemPrompt,
            userPrompt,
            output: output || this._currentPrompt?.output,
            tokens,
            durationMs,
        };
        versions.push(version);
        this._promptVersions.set(stageId, versions);

        // Update webview with new versions list
        if (this._view) {
            this._view.webview.postMessage({
                type: 'versionsUpdated',
                data: { versions },
            });
        }

        vscode.window.showInformationMessage(`Prompt saved as ${version.id}`);
    }

    /**
     * Toggle comparison mode
     */
    private _toggleComparison(stageId: string): void {
        this._comparisonState.enabled = !this._comparisonState.enabled;

        if (!this._comparisonState.enabled) {
            // Reset comparison state
            this._comparisonState.leftVersion = undefined;
            this._comparisonState.rightVersion = undefined;
        }

        if (this._view) {
            this._view.webview.postMessage({
                type: 'comparisonToggled',
                data: {
                    enabled: this._comparisonState.enabled,
                    versions: this._promptVersions.get(stageId) || [],
                },
            });
        }
    }

    /**
     * Select a version for comparison
     */
    private _selectForComparison(stageId: string, versionId: string, side: 'left' | 'right'): void {
        const versions = this._promptVersions.get(stageId) || [];
        const version = versions.find(v => v.id === versionId);

        if (!version) return;

        if (side === 'left') {
            this._comparisonState.leftVersion = version;
        } else {
            this._comparisonState.rightVersion = version;
        }

        // Send comparison data to webview
        if (this._view) {
            this._view.webview.postMessage({
                type: 'comparisonUpdated',
                data: {
                    left: this._comparisonState.leftVersion,
                    right: this._comparisonState.rightVersion,
                },
            });
        }
    }

    /**
     * Load a prompt version
     */
    private _loadPromptVersion(stageId: string, versionId: string): void {
        const versions = this._promptVersions.get(stageId) || [];
        const version = versions.find(v => v.id === versionId);

        if (version && this._view) {
            this._view.webview.postMessage({
                type: 'loadVersion',
                data: {
                    systemPrompt: version.systemPrompt,
                    userPrompt: version.userPrompt,
                },
            });
        }
    }

    /**
     * Get HTML content for the webview
     */
    private _getHtmlContent(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Editor</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-sideBar-background);
            padding: 12px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        .stage-name {
            font-weight: bold;
            font-size: 14px;
        }
        .component-type {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }
        .section {
            margin-bottom: 16px;
        }
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .section-title {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--vscode-descriptionForeground);
        }
        textarea {
            width: 100%;
            min-height: 100px;
            padding: 8px;
            font-family: var(--vscode-editor-font-family);
            font-size: var(--vscode-editor-font-size);
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            resize: vertical;
        }
        textarea:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }
        .output-area {
            min-height: 80px;
            max-height: 200px;
            overflow-y: auto;
            padding: 8px;
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            font-family: var(--vscode-editor-font-family);
            font-size: var(--vscode-editor-font-size);
            white-space: pre-wrap;
        }
        .buttons {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            flex-wrap: wrap;
        }
        button {
            padding: 6px 12px;
            font-size: 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .primary-btn {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        .primary-btn:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .secondary-btn {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        .secondary-btn:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        .versions {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid var(--vscode-panel-border);
        }
        .version-list {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 8px;
        }
        .version-chip {
            padding: 2px 8px;
            font-size: 11px;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            border-radius: 10px;
            cursor: pointer;
        }
        .version-chip:hover {
            opacity: 0.8;
        }
        .version-chip.active {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        .version-chip.left-selected {
            background: var(--vscode-charts-blue);
            color: white;
        }
        .version-chip.right-selected {
            background: var(--vscode-charts-green);
            color: white;
        }
        .tokens {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            margin-top: 4px;
        }
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--vscode-descriptionForeground);
        }
        .empty-state-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }
        .variables {
            font-size: 11px;
            margin-top: 8px;
            padding: 8px;
            background: var(--vscode-textBlockQuote-background);
            border-radius: 4px;
        }
        .variable-item {
            display: flex;
            margin-bottom: 4px;
        }
        .variable-name {
            color: var(--vscode-symbolIcon-variableForeground);
            margin-right: 8px;
        }
        .variable-value {
            color: var(--vscode-descriptionForeground);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .streaming-cursor {
            display: inline-block;
            width: 8px;
            height: 14px;
            background: var(--vscode-editorCursor-foreground);
            animation: blink 1s infinite;
            vertical-align: text-bottom;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        .output-area.streaming {
            border-color: var(--vscode-progressBar-background);
            box-shadow: 0 0 4px var(--vscode-progressBar-background);
        }
        .streaming-indicator {
            display: inline-flex;
            gap: 4px;
            margin-right: 8px;
        }
        .streaming-dot {
            display: inline-block;
            width: 6px;
            height: 6px;
            background: var(--vscode-progressBar-background);
            border-radius: 50%;
            animation: pulse 1.4s infinite ease-in-out both;
        }
        .streaming-dot:nth-child(1) { animation-delay: -0.32s; }
        .streaming-dot:nth-child(2) { animation-delay: -0.16s; }
        .streaming-dot:nth-child(3) { animation-delay: 0s; }
        @keyframes pulse {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }

        /* Comparison mode styles */
        .comparison-container {
            display: none;
        }
        .comparison-container.active {
            display: block;
        }
        .comparison-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        .comparison-title {
            font-weight: bold;
            font-size: 14px;
        }
        .comparison-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .comparison-side {
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            overflow: hidden;
        }
        .comparison-side.left {
            border-color: var(--vscode-charts-blue);
        }
        .comparison-side.right {
            border-color: var(--vscode-charts-green);
        }
        .comparison-side-header {
            padding: 8px;
            font-size: 11px;
            font-weight: 600;
            background: var(--vscode-editor-background);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .comparison-side.left .comparison-side-header {
            background: color-mix(in srgb, var(--vscode-charts-blue) 20%, var(--vscode-editor-background));
        }
        .comparison-side.right .comparison-side-header {
            background: color-mix(in srgb, var(--vscode-charts-green) 20%, var(--vscode-editor-background));
        }
        .comparison-content {
            padding: 8px;
            font-size: 11px;
            max-height: 200px;
            overflow-y: auto;
        }
        .comparison-section {
            margin-bottom: 12px;
        }
        .comparison-section-title {
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 4px;
        }
        .comparison-text {
            font-family: var(--vscode-editor-font-family);
            white-space: pre-wrap;
            word-break: break-word;
        }
        .comparison-output {
            background: var(--vscode-textBlockQuote-background);
            padding: 8px;
            border-radius: 4px;
            max-height: 150px;
            overflow-y: auto;
        }
        .comparison-stats {
            display: flex;
            gap: 12px;
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-top: 8px;
        }
        .comparison-stat {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .version-selector {
            margin-top: 12px;
        }
        .version-selector-title {
            font-size: 11px;
            margin-bottom: 8px;
            color: var(--vscode-descriptionForeground);
        }
        .version-selector-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }
        .version-selector-label {
            font-size: 11px;
            width: 60px;
        }
        .version-selector-label.left {
            color: var(--vscode-charts-blue);
        }
        .version-selector-label.right {
            color: var(--vscode-charts-green);
        }
        .diff-added {
            background: color-mix(in srgb, var(--vscode-gitDecoration-addedResourceForeground) 20%, transparent);
        }
        .diff-removed {
            background: color-mix(in srgb, var(--vscode-gitDecoration-deletedResourceForeground) 20%, transparent);
            text-decoration: line-through;
        }
        .no-selection {
            padding: 20px;
            text-align: center;
            color: var(--vscode-descriptionForeground);
            font-style: italic;
        }
    </style>
</head>
<body>
    <div id="empty-state" class="empty-state">
        <div class="empty-state-icon">📝</div>
        <div>Pause at an LLM stage to edit prompts</div>
    </div>

    <div id="editor" style="display: none;">
        <div class="header">
            <div>
                <div class="stage-name" id="stage-name"></div>
                <div class="component-type" id="component-type"></div>
            </div>
        </div>

        <!-- Normal Editor View -->
        <div id="editor-view">
            <div class="section">
                <div class="section-header">
                    <span class="section-title">System Prompt</span>
                </div>
                <textarea id="system-prompt" placeholder="System prompt..."></textarea>
            </div>

            <div class="section">
                <div class="section-header">
                    <span class="section-title">User Prompt</span>
                </div>
                <textarea id="user-prompt" placeholder="User prompt..."></textarea>
            </div>

            <div id="variables-section" class="section" style="display: none;">
                <div class="section-title">Variables</div>
                <div class="variables" id="variables"></div>
            </div>

            <div class="section">
                <div class="section-header">
                    <span class="section-title">Output</span>
                    <span class="tokens" id="tokens"></span>
                </div>
                <div class="output-area" id="output">
                    <span class="placeholder">Output will appear here...</span>
                </div>
            </div>

            <div class="buttons">
                <button class="primary-btn" id="rerun-btn">
                    <span>▶</span> Re-run Stage
                </button>
                <button class="secondary-btn" id="save-btn">
                    <span>💾</span> Save Version
                </button>
                <button class="secondary-btn" id="reset-btn">
                    <span>↺</span> Reset
                </button>
                <button class="secondary-btn" id="compare-btn">
                    <span>⚖</span> Compare
                </button>
            </div>

            <div class="versions" id="versions-section" style="display: none;">
                <div class="section-title">Saved Versions</div>
                <div class="version-list" id="version-list"></div>
            </div>
        </div>

        <!-- Comparison View -->
        <div id="comparison-view" class="comparison-container">
            <div class="comparison-header">
                <span class="comparison-title">Side-by-Side Comparison</span>
                <button class="secondary-btn" id="close-comparison-btn">
                    <span>×</span> Close
                </button>
            </div>

            <div class="version-selector">
                <div class="version-selector-title">Select versions to compare:</div>
                <div class="version-selector-row">
                    <span class="version-selector-label left">Left:</span>
                    <div class="version-list" id="left-version-list"></div>
                </div>
                <div class="version-selector-row">
                    <span class="version-selector-label right">Right:</span>
                    <div class="version-list" id="right-version-list"></div>
                </div>
            </div>

            <div class="comparison-grid">
                <div class="comparison-side left">
                    <div class="comparison-side-header">
                        <span id="left-version-label">Select a version</span>
                        <span class="comparison-stats" id="left-stats"></span>
                    </div>
                    <div class="comparison-content" id="left-content">
                        <div class="no-selection">Click a version above</div>
                    </div>
                </div>
                <div class="comparison-side right">
                    <div class="comparison-side-header">
                        <span id="right-version-label">Select a version</span>
                        <span class="comparison-stats" id="right-stats"></span>
                    </div>
                    <div class="comparison-content" id="right-content">
                        <div class="no-selection">Click a version above</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        let currentStageId = null;
        let originalSystemPrompt = '';
        let originalUserPrompt = '';
        let isStreaming = false;
        let comparisonMode = false;
        let versions = [];
        let leftSelectedVersion = null;
        let rightSelectedVersion = null;

        const emptyState = document.getElementById('empty-state');
        const editor = document.getElementById('editor');
        const editorView = document.getElementById('editor-view');
        const comparisonView = document.getElementById('comparison-view');
        const stageName = document.getElementById('stage-name');
        const componentType = document.getElementById('component-type');
        const systemPrompt = document.getElementById('system-prompt');
        const userPrompt = document.getElementById('user-prompt');
        const variablesSection = document.getElementById('variables-section');
        const variables = document.getElementById('variables');
        const output = document.getElementById('output');
        const tokens = document.getElementById('tokens');
        const versionsSection = document.getElementById('versions-section');
        const versionList = document.getElementById('version-list');
        const leftVersionList = document.getElementById('left-version-list');
        const rightVersionList = document.getElementById('right-version-list');
        const leftContent = document.getElementById('left-content');
        const rightContent = document.getElementById('right-content');
        const leftVersionLabel = document.getElementById('left-version-label');
        const rightVersionLabel = document.getElementById('right-version-label');
        const leftStats = document.getElementById('left-stats');
        const rightStats = document.getElementById('right-stats');

        // Button handlers
        document.getElementById('rerun-btn').addEventListener('click', () => {
            if (currentStageId) {
                output.innerHTML = '<span class="streaming-cursor"></span>';
                isStreaming = true;
                vscode.postMessage({
                    type: 'rerun',
                    stageId: currentStageId,
                    systemPrompt: systemPrompt.value,
                    userPrompt: userPrompt.value
                });
            }
        });

        document.getElementById('save-btn').addEventListener('click', () => {
            if (currentStageId) {
                vscode.postMessage({
                    type: 'saveVersion',
                    stageId: currentStageId,
                    systemPrompt: systemPrompt.value,
                    userPrompt: userPrompt.value
                });
            }
        });

        document.getElementById('reset-btn').addEventListener('click', () => {
            systemPrompt.value = originalSystemPrompt;
            userPrompt.value = originalUserPrompt;
        });

        document.getElementById('compare-btn').addEventListener('click', () => {
            if (currentStageId && versions.length >= 2) {
                vscode.postMessage({
                    type: 'toggleComparison',
                    stageId: currentStageId
                });
            } else if (versions.length < 2) {
                alert('Save at least 2 versions to compare');
            }
        });

        document.getElementById('close-comparison-btn').addEventListener('click', () => {
            if (currentStageId) {
                vscode.postMessage({
                    type: 'toggleComparison',
                    stageId: currentStageId
                });
            }
        });

        // Track prompt changes
        systemPrompt.addEventListener('input', () => {
            if (currentStageId) {
                vscode.postMessage({
                    type: 'promptChanged',
                    stageId: currentStageId,
                    systemPrompt: systemPrompt.value,
                    userPrompt: userPrompt.value
                });
            }
        });

        userPrompt.addEventListener('input', () => {
            if (currentStageId) {
                vscode.postMessage({
                    type: 'promptChanged',
                    stageId: currentStageId,
                    systemPrompt: systemPrompt.value,
                    userPrompt: userPrompt.value
                });
            }
        });

        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;

            switch (message.type) {
                case 'showPrompt':
                    showPrompt(message.data);
                    break;
                case 'updateOutput':
                    updateOutput(message.data);
                    break;
                case 'streamStart':
                    startStreaming(message.data.stageId, message.data.stageName);
                    break;
                case 'streamChunk':
                    appendStreamChunk(message.data.chunk, message.data.tokenIndex);
                    break;
                case 'streamEnd':
                    endStreaming(message.data.stageId, message.data.totalTokens, message.data.finalContent);
                    break;
                case 'versionsUpdated':
                    versions = message.data.versions;
                    updateVersions(versions);
                    updateComparisonVersionLists(versions);
                    break;
                case 'loadVersion':
                    systemPrompt.value = message.data.systemPrompt;
                    userPrompt.value = message.data.userPrompt;
                    break;
                case 'comparisonToggled':
                    comparisonMode = message.data.enabled;
                    versions = message.data.versions || versions;
                    toggleComparisonView(comparisonMode);
                    break;
                case 'comparisonUpdated':
                    updateComparisonDisplay(message.data.left, message.data.right);
                    break;
                case 'clear':
                    clearEditor();
                    break;
            }
        });

        function showPrompt(data) {
            currentStageId = data.stageId;
            originalSystemPrompt = data.systemPrompt || '';
            originalUserPrompt = data.userPrompt || '';
            versions = data.versions || [];

            emptyState.style.display = 'none';
            editor.style.display = 'block';

            stageName.textContent = data.stageName || data.stageId;
            componentType.textContent = data.componentType;
            systemPrompt.value = originalSystemPrompt;
            userPrompt.value = originalUserPrompt;

            if (data.output) {
                output.textContent = data.output;
            } else {
                output.innerHTML = '<span class="placeholder">Output will appear here...</span>';
            }

            // Show variables if present
            if (data.variables && Object.keys(data.variables).length > 0) {
                variablesSection.style.display = 'block';
                variables.innerHTML = Object.entries(data.variables)
                    .map(([key, value]) => {
                        const displayValue = typeof value === 'object'
                            ? JSON.stringify(value).substring(0, 50) + '...'
                            : String(value).substring(0, 50);
                        return \`<div class="variable-item">
                            <span class="variable-name">\${key}:</span>
                            <span class="variable-value">\${displayValue}</span>
                        </div>\`;
                    })
                    .join('');
            } else {
                variablesSection.style.display = 'none';
            }

            // Show versions if present
            if (versions.length > 0) {
                updateVersions(versions);
            } else {
                versionsSection.style.display = 'none';
            }

            // Reset comparison state
            comparisonMode = false;
            toggleComparisonView(false);
        }

        function updateOutput(data) {
            isStreaming = false;
            output.textContent = data.output || '';
            if (data.tokens) {
                tokens.textContent = \`\${data.tokens.input} in / \${data.tokens.output} out\`;
            }
        }

        let streamTokenCount = 0;
        let streamStartTime = null;

        function startStreaming(stageId, stageName) {
            isStreaming = true;
            streamTokenCount = 0;
            streamStartTime = Date.now();
            output.innerHTML = '';
            output.classList.add('streaming');
            tokens.textContent = 'Streaming...';

            // Add streaming indicator
            const indicator = document.createElement('div');
            indicator.className = 'streaming-indicator';
            indicator.innerHTML = '<span class="streaming-dot"></span><span class="streaming-dot"></span><span class="streaming-dot"></span>';
            output.appendChild(indicator);

            // Add cursor
            const cursor = document.createElement('span');
            cursor.className = 'streaming-cursor';
            output.appendChild(cursor);

            // Scroll to show output
            output.scrollTop = output.scrollHeight;
        }

        function appendStreamChunk(chunk, tokenIndex) {
            if (isStreaming) {
                // Remove streaming indicator if present
                const indicator = output.querySelector('.streaming-indicator');
                if (indicator) {
                    indicator.remove();
                }

                const cursor = output.querySelector('.streaming-cursor');
                if (cursor) {
                    cursor.remove();
                }

                // Append chunk
                output.appendChild(document.createTextNode(chunk));
                streamTokenCount++;

                // Update token count display
                const elapsed = ((Date.now() - streamStartTime) / 1000).toFixed(1);
                tokens.textContent = \`\${streamTokenCount} tokens | \${elapsed}s...\`;

                // Re-add cursor
                const newCursor = document.createElement('span');
                newCursor.className = 'streaming-cursor';
                output.appendChild(newCursor);

                // Auto-scroll to follow streaming
                output.scrollTop = output.scrollHeight;
            }
        }

        function endStreaming(stageId, totalTokens, finalContent) {
            isStreaming = false;
            output.classList.remove('streaming');

            // Remove cursor
            const cursor = output.querySelector('.streaming-cursor');
            if (cursor) {
                cursor.remove();
            }

            // Remove streaming indicator if still present
            const indicator = output.querySelector('.streaming-indicator');
            if (indicator) {
                indicator.remove();
            }

            // Update final content if provided
            if (finalContent !== undefined && finalContent !== null) {
                output.textContent = finalContent;
            }

            // Update token stats
            const elapsed = streamStartTime ? ((Date.now() - streamStartTime) / 1000).toFixed(1) : '?';
            const displayTokens = totalTokens || streamTokenCount;
            tokens.textContent = \`\${displayTokens} tokens | \${elapsed}s\`;

            streamTokenCount = 0;
            streamStartTime = null;
        }

        function updateVersions(vers) {
            if (vers.length > 0) {
                versionsSection.style.display = 'block';
                versionList.innerHTML = vers
                    .map(v => \`<span class="version-chip" data-id="\${v.id}">\${v.id}</span>\`)
                    .join('');

                versionList.querySelectorAll('.version-chip').forEach(chip => {
                    chip.addEventListener('click', () => {
                        vscode.postMessage({
                            type: 'loadVersion',
                            stageId: currentStageId,
                            versionId: chip.dataset.id
                        });
                    });
                });
            }
        }

        function toggleComparisonView(enabled) {
            if (enabled) {
                editorView.style.display = 'none';
                comparisonView.classList.add('active');
                updateComparisonVersionLists(versions);
            } else {
                editorView.style.display = 'block';
                comparisonView.classList.remove('active');
                leftSelectedVersion = null;
                rightSelectedVersion = null;
            }
        }

        function updateComparisonVersionLists(vers) {
            const leftHtml = vers.map(v => {
                const selected = leftSelectedVersion && leftSelectedVersion.id === v.id ? 'left-selected' : '';
                return \`<span class="version-chip \${selected}" data-id="\${v.id}" data-side="left">\${v.id}</span>\`;
            }).join('');

            const rightHtml = vers.map(v => {
                const selected = rightSelectedVersion && rightSelectedVersion.id === v.id ? 'right-selected' : '';
                return \`<span class="version-chip \${selected}" data-id="\${v.id}" data-side="right">\${v.id}</span>\`;
            }).join('');

            leftVersionList.innerHTML = leftHtml;
            rightVersionList.innerHTML = rightHtml;

            // Add click handlers for version selection
            document.querySelectorAll('#left-version-list .version-chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    vscode.postMessage({
                        type: 'selectForComparison',
                        stageId: currentStageId,
                        versionId: chip.dataset.id,
                        side: 'left'
                    });
                });
            });

            document.querySelectorAll('#right-version-list .version-chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    vscode.postMessage({
                        type: 'selectForComparison',
                        stageId: currentStageId,
                        versionId: chip.dataset.id,
                        side: 'right'
                    });
                });
            });
        }

        function updateComparisonDisplay(left, right) {
            leftSelectedVersion = left;
            rightSelectedVersion = right;

            // Update version chip highlighting
            updateComparisonVersionLists(versions);

            // Update left side
            if (left) {
                leftVersionLabel.textContent = left.id;
                leftContent.innerHTML = renderVersionContent(left, true);
                leftStats.innerHTML = renderVersionStats(left);
            } else {
                leftVersionLabel.textContent = 'Select a version';
                leftContent.innerHTML = '<div class="no-selection">Click a version above</div>';
                leftStats.innerHTML = '';
            }

            // Update right side
            if (right) {
                rightVersionLabel.textContent = right.id;
                rightContent.innerHTML = renderVersionContent(right, false);
                rightStats.innerHTML = renderVersionStats(right);
            } else {
                rightVersionLabel.textContent = 'Select a version';
                rightContent.innerHTML = '<div class="no-selection">Click a version above</div>';
                rightStats.innerHTML = '';
            }
        }

        function renderVersionContent(version, isLeft = true) {
            const other = isLeft ? rightSelectedVersion : leftSelectedVersion;

            // If we have both versions, show diff highlighting
            let systemPromptHtml, userPromptHtml, outputHtml;

            if (other) {
                systemPromptHtml = diffToHtml(
                    version.systemPrompt || '',
                    other.systemPrompt || '',
                    isLeft
                );
                userPromptHtml = diffToHtml(
                    version.userPrompt || '',
                    other.userPrompt || '',
                    isLeft
                );
                outputHtml = diffToHtml(
                    version.output || '',
                    other.output || '',
                    isLeft
                );
            } else {
                systemPromptHtml = escapeHtml(version.systemPrompt || '(empty)');
                userPromptHtml = escapeHtml(version.userPrompt || '(empty)');
                outputHtml = escapeHtml(version.output || '(no output)');
            }

            return \`
                <div class="comparison-section">
                    <div class="comparison-section-title">System Prompt</div>
                    <div class="comparison-text">\${systemPromptHtml}</div>
                </div>
                <div class="comparison-section">
                    <div class="comparison-section-title">User Prompt</div>
                    <div class="comparison-text">\${userPromptHtml}</div>
                </div>
                <div class="comparison-section">
                    <div class="comparison-section-title">Output</div>
                    <div class="comparison-output">\${outputHtml}</div>
                </div>
            \`;
        }

        // Simple word-level diff algorithm
        function diffToHtml(textA, textB, showA) {
            if (!textA && !textB) return '(empty)';
            if (textA === textB) return escapeHtml(textA || '(empty)');

            // Split into words, preserving whitespace
            const wordsA = textA.split(/(\s+)/);
            const wordsB = textB.split(/(\s+)/);

            // Compute LCS (Longest Common Subsequence) for word-level diff
            const lcs = computeLCS(wordsA, wordsB);

            // Build diff HTML
            const html = [];
            let i = 0, j = 0, k = 0;

            while (i < wordsA.length || j < wordsB.length) {
                if (k < lcs.length && i < wordsA.length && wordsA[i] === lcs[k]) {
                    // Common word
                    html.push(escapeHtml(wordsA[i]));
                    i++;
                    if (j < wordsB.length && wordsB[j] === lcs[k]) {
                        j++;
                    }
                    k++;
                } else if (showA) {
                    // Show A's perspective (removed in B)
                    if (i < wordsA.length && (k >= lcs.length || wordsA[i] !== lcs[k])) {
                        // Word removed from A
                        if (wordsA[i].trim()) {
                            html.push('<span class="diff-removed">' + escapeHtml(wordsA[i]) + '</span>');
                        } else {
                            html.push(escapeHtml(wordsA[i]));
                        }
                        i++;
                    } else if (j < wordsB.length && (k >= lcs.length || wordsB[j] !== lcs[k])) {
                        // Word added in B - skip in A's view
                        j++;
                    }
                } else {
                    // Show B's perspective (added in B)
                    if (j < wordsB.length && (k >= lcs.length || wordsB[j] !== lcs[k])) {
                        // Word added in B
                        if (wordsB[j].trim()) {
                            html.push('<span class="diff-added">' + escapeHtml(wordsB[j]) + '</span>');
                        } else {
                            html.push(escapeHtml(wordsB[j]));
                        }
                        j++;
                    } else if (i < wordsA.length && (k >= lcs.length || wordsA[i] !== lcs[k])) {
                        // Word removed in A - skip in B's view
                        i++;
                    }
                }
            }

            return html.join('') || '(empty)';
        }

        // Compute Longest Common Subsequence
        function computeLCS(a, b) {
            const m = a.length;
            const n = b.length;
            const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

            // Fill DP table
            for (let i = 1; i <= m; i++) {
                for (let j = 1; j <= n; j++) {
                    if (a[i-1] === b[j-1]) {
                        dp[i][j] = dp[i-1][j-1] + 1;
                    } else {
                        dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);
                    }
                }
            }

            // Backtrack to find LCS
            const lcs = [];
            let i = m, j = n;
            while (i > 0 && j > 0) {
                if (a[i-1] === b[j-1]) {
                    lcs.unshift(a[i-1]);
                    i--;
                    j--;
                } else if (dp[i-1][j] > dp[i][j-1]) {
                    i--;
                } else {
                    j--;
                }
            }

            return lcs;
        }

        function renderVersionStats(version) {
            const parts = [];
            if (version.tokens) {
                parts.push(\`<span class="comparison-stat">📊 \${version.tokens.input} in / \${version.tokens.output} out</span>\`);
            }
            if (version.durationMs) {
                parts.push(\`<span class="comparison-stat">⏱ \${version.durationMs}ms</span>\`);
            }
            return parts.join('');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function clearEditor() {
            currentStageId = null;
            versions = [];
            emptyState.style.display = 'block';
            editor.style.display = 'none';
            comparisonMode = false;
        }
    </script>
</body>
</html>`;
    }
}

/**
 * Register prompt editor commands
 */
export function registerPromptEditorCommands(
    context: vscode.ExtensionContext,
    promptEditorProvider: PromptEditorViewProvider
): void {
    // Command to show prompt editor
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.showPromptEditor', () => {
            vscode.commands.executeCommand('flowmason.promptEditor.focus');
        })
    );

    // Command to edit current stage prompt
    context.subscriptions.push(
        vscode.commands.registerCommand('flowmason.editStagePrompt', (stageId: string) => {
            // This would be called from the debug session when paused at an LLM node
            vscode.commands.executeCommand('flowmason.promptEditor.focus');
        })
    );
}
