/**
 * Stage Config View Provider
 *
 * A WebviewView panel in the sidebar for editing stage configuration.
 * Uses VSCode's native styling for a consistent look.
 */

import * as vscode from 'vscode';
import { FlowMasonService, Component } from '../services/flowmasonService';
import { PipelineStage, PipelineFile } from './pipelineStagesTree';
import { DagCanvasProvider } from '../editors/dagCanvasProvider';

export class StageConfigViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'flowmason.stageConfig';

    private _view?: vscode.WebviewView;
    private _currentStage?: PipelineStage;
    private _currentComponent?: Component | null;
    private _currentDocument?: vscode.TextDocument;
    private _disposables: vscode.Disposable[] = [];

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly flowmasonService: FlowMasonService
    ) {}

    resolveWebviewView(
        webviewView: vscode.WebviewView,
        _context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ): void {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        // Set initial content
        webviewView.webview.html = this.getEmptyHtml();

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(
            async message => {
                switch (message.type) {
                    case 'configChange':
                        await this.handleConfigChange(message.config);
                        break;
                    case 'deleteStage':
                        await this.handleDeleteStage();
                        break;
                    case 'duplicateStage':
                        await this.handleDuplicateStage();
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    /**
     * Show configuration for a specific stage
     */
    async showStage(
        stage: PipelineStage,
        document: vscode.TextDocument
    ): Promise<void> {
        this._currentStage = stage;
        this._currentDocument = document;

        // Fetch component info for schema
        this._currentComponent = await this.flowmasonService.getComponent(stage.component_type);

        if (this._view) {
            this._view.webview.html = this.getStageConfigHtml(stage, this._currentComponent);
            this._view.show?.(true);
        }
    }

    /**
     * Clear the panel
     */
    clear(): void {
        this._currentStage = undefined;
        this._currentComponent = undefined;
        this._currentDocument = undefined;

        if (this._view) {
            this._view.webview.html = this.getEmptyHtml();
        }
    }

    private async handleConfigChange(config: Record<string, unknown>): Promise<void> {
        if (!this._currentStage || !this._currentDocument) {
            return;
        }

        const editor = vscode.window.visibleTextEditors.find(
            e => e.document.uri.toString() === this._currentDocument!.uri.toString()
        );

        if (!editor) {
            return;
        }

        // Parse and update the pipeline
        try {
            const pipeline = JSON.parse(this._currentDocument.getText()) as PipelineFile;
            const stageIndex = pipeline.stages.findIndex(s => s.id === this._currentStage!.id);

            if (stageIndex >= 0) {
                pipeline.stages[stageIndex].config = config;

                // Replace document content
                const fullRange = new vscode.Range(
                    this._currentDocument.positionAt(0),
                    this._currentDocument.positionAt(this._currentDocument.getText().length)
                );

                const edit = new vscode.WorkspaceEdit();
                edit.replace(
                    this._currentDocument.uri,
                    fullRange,
                    JSON.stringify(pipeline, null, 2)
                );
                await vscode.workspace.applyEdit(edit);

                // Update current stage reference
                this._currentStage = pipeline.stages[stageIndex];
            }
        } catch (error) {
            vscode.window.showErrorMessage('Failed to update stage configuration');
        }
    }

    private async handleDeleteStage(): Promise<void> {
        if (!this._currentStage || !this._currentDocument) {
            return;
        }

        const confirm = await vscode.window.showWarningMessage(
            `Delete stage "${this._currentStage.id}"?`,
            { modal: true },
            'Delete'
        );

        if (confirm !== 'Delete') {
            return;
        }

        try {
            const pipeline = JSON.parse(this._currentDocument.getText()) as PipelineFile;
            pipeline.stages = pipeline.stages.filter(s => s.id !== this._currentStage!.id);

            const fullRange = new vscode.Range(
                this._currentDocument.positionAt(0),
                this._currentDocument.positionAt(this._currentDocument.getText().length)
            );

            const edit = new vscode.WorkspaceEdit();
            edit.replace(
                this._currentDocument.uri,
                fullRange,
                JSON.stringify(pipeline, null, 2)
            );
            await vscode.workspace.applyEdit(edit);

            this.clear();
            vscode.window.showInformationMessage(`Deleted stage "${this._currentStage.id}"`);
        } catch {
            vscode.window.showErrorMessage('Failed to delete stage');
        }
    }

    private async handleDuplicateStage(): Promise<void> {
        if (!this._currentStage || !this._currentDocument) {
            return;
        }

        try {
            const pipeline = JSON.parse(this._currentDocument.getText()) as PipelineFile;

            // Generate new ID
            let newId = `${this._currentStage.id}_copy`;
            let counter = 1;
            const existingIds = new Set(pipeline.stages.map(s => s.id));
            while (existingIds.has(newId)) {
                newId = `${this._currentStage.id}_copy_${counter}`;
                counter++;
            }

            // Create duplicate
            const newStage: PipelineStage = {
                ...this._currentStage,
                id: newId
            };

            // Insert after current stage
            const currentIndex = pipeline.stages.findIndex(s => s.id === this._currentStage!.id);
            pipeline.stages.splice(currentIndex + 1, 0, newStage);

            const fullRange = new vscode.Range(
                this._currentDocument.positionAt(0),
                this._currentDocument.positionAt(this._currentDocument.getText().length)
            );

            const edit = new vscode.WorkspaceEdit();
            edit.replace(
                this._currentDocument.uri,
                fullRange,
                JSON.stringify(pipeline, null, 2)
            );
            await vscode.workspace.applyEdit(edit);

            vscode.window.showInformationMessage(`Duplicated stage as "${newId}"`);
        } catch {
            vscode.window.showErrorMessage('Failed to duplicate stage');
        }
    }

    private getEmptyHtml(): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    color: var(--vscode-foreground);
                    padding: 12px;
                    margin: 0;
                }
                .empty-state {
                    text-align: center;
                    padding: 20px;
                    color: var(--vscode-descriptionForeground);
                }
                .empty-state code {
                    background: var(--vscode-textCodeBlock-background);
                    padding: 2px 6px;
                    border-radius: 3px;
                }
            </style>
        </head>
        <body>
            <div class="empty-state">
                <p>Select a stage to edit its configuration</p>
                <p><code>Click a stage</code> in the Pipeline Stages tree or Outline view</p>
            </div>
        </body>
        </html>`;
    }

    private getStageConfigHtml(stage: PipelineStage, component: Component | null): string {
        const configFields = this.generateConfigFields(stage, component);

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                    color: var(--vscode-foreground);
                    padding: 12px;
                    margin: 0;
                }
                .header {
                    border-bottom: 1px solid var(--vscode-panel-border);
                    padding-bottom: 12px;
                    margin-bottom: 12px;
                }
                .header h3 {
                    margin: 0 0 4px 0;
                    font-size: 14px;
                    font-weight: 600;
                }
                .header .component-type {
                    color: var(--vscode-descriptionForeground);
                    font-size: 12px;
                }
                .field {
                    margin-bottom: 16px;
                }
                .field label {
                    display: block;
                    margin-bottom: 4px;
                    font-weight: 500;
                    font-size: 12px;
                }
                .field .description {
                    color: var(--vscode-descriptionForeground);
                    font-size: 11px;
                    margin-bottom: 4px;
                }
                input, textarea, select {
                    width: 100%;
                    box-sizing: border-box;
                    padding: 6px 8px;
                    background: var(--vscode-input-background);
                    border: 1px solid var(--vscode-input-border);
                    color: var(--vscode-input-foreground);
                    border-radius: 2px;
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                }
                input:focus, textarea:focus, select:focus {
                    outline: none;
                    border-color: var(--vscode-focusBorder);
                }
                textarea {
                    min-height: 80px;
                    resize: vertical;
                }
                .checkbox-field {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                .checkbox-field input {
                    width: auto;
                }
                .actions {
                    display: flex;
                    gap: 8px;
                    margin-top: 16px;
                    padding-top: 16px;
                    border-top: 1px solid var(--vscode-panel-border);
                }
                button {
                    padding: 6px 12px;
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    border-radius: 2px;
                    cursor: pointer;
                    font-size: 12px;
                }
                button:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                button.secondary {
                    background: var(--vscode-button-secondaryBackground);
                    color: var(--vscode-button-secondaryForeground);
                }
                button.secondary:hover {
                    background: var(--vscode-button-secondaryHoverBackground);
                }
                button.danger {
                    background: var(--vscode-inputValidation-errorBackground);
                    color: var(--vscode-inputValidation-errorForeground);
                }
                .dependencies {
                    margin-top: 16px;
                    padding-top: 16px;
                    border-top: 1px solid var(--vscode-panel-border);
                }
                .dependencies h4 {
                    margin: 0 0 8px 0;
                    font-size: 12px;
                    font-weight: 500;
                }
                .dependency-tag {
                    display: inline-block;
                    background: var(--vscode-badge-background);
                    color: var(--vscode-badge-foreground);
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 11px;
                    margin-right: 4px;
                    margin-bottom: 4px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h3>${this.escapeHtml(stage.id)}</h3>
                <div class="component-type">${this.escapeHtml(stage.component_type)}</div>
            </div>

            <form id="configForm">
                ${configFields}
            </form>

            ${stage.depends_on && stage.depends_on.length > 0 ? `
                <div class="dependencies">
                    <h4>Dependencies</h4>
                    ${stage.depends_on.map(d => `<span class="dependency-tag">${this.escapeHtml(d)}</span>`).join('')}
                </div>
            ` : ''}

            <div class="actions">
                <button type="button" class="secondary" onclick="duplicateStage()">Duplicate</button>
                <button type="button" class="danger" onclick="deleteStage()">Delete</button>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                const form = document.getElementById('configForm');
                let debounceTimer;

                // Collect config from form
                function getConfig() {
                    const config = {};
                    const inputs = form.querySelectorAll('input, textarea, select');

                    inputs.forEach(input => {
                        const name = input.name;
                        if (!name) return;

                        let value;
                        if (input.type === 'checkbox') {
                            value = input.checked;
                        } else if (input.type === 'number') {
                            value = input.value ? parseFloat(input.value) : null;
                        } else if (input.dataset.type === 'json') {
                            try {
                                value = JSON.parse(input.value);
                            } catch {
                                value = input.value;
                            }
                        } else {
                            value = input.value;
                        }

                        config[name] = value;
                    });

                    return config;
                }

                // Send config update with debounce
                function sendConfigUpdate() {
                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(() => {
                        vscode.postMessage({
                            type: 'configChange',
                            config: getConfig()
                        });
                    }, 500);
                }

                // Listen for changes
                form.addEventListener('input', sendConfigUpdate);
                form.addEventListener('change', sendConfigUpdate);

                function deleteStage() {
                    vscode.postMessage({ type: 'deleteStage' });
                }

                function duplicateStage() {
                    vscode.postMessage({ type: 'duplicateStage' });
                }
            </script>
        </body>
        </html>`;
    }

    private generateConfigFields(stage: PipelineStage, component: Component | null): string {
        const config = stage.config || {};
        const schema = component?.input_schema as {
            properties?: Record<string, {
                type?: string;
                description?: string;
                default?: unknown;
                enum?: string[];
            }>;
            required?: string[];
        } | undefined;

        const fields: string[] = [];

        // Generate fields based on schema if available
        if (schema?.properties) {
            for (const [key, prop] of Object.entries(schema.properties)) {
                const value = config[key];
                const isRequired = schema.required?.includes(key) || false;
                fields.push(this.generateField(key, prop, value, isRequired));
            }
        }

        // Also add any config values not in schema
        for (const [key, value] of Object.entries(config)) {
            if (!schema?.properties?.[key]) {
                fields.push(this.generateField(key, { type: typeof value }, value, false));
            }
        }

        if (fields.length === 0) {
            return `<p style="color: var(--vscode-descriptionForeground);">No configuration options</p>`;
        }

        return fields.join('');
    }

    private generateField(
        key: string,
        schema: { type?: string; description?: string; default?: unknown; enum?: string[] },
        value: unknown,
        required: boolean
    ): string {
        const labelHtml = `<label for="${this.escapeHtml(key)}">${this.escapeHtml(key)}${required ? ' *' : ''}</label>`;
        const descHtml = schema.description
            ? `<div class="description">${this.escapeHtml(schema.description)}</div>`
            : '';

        // Enum field - dropdown
        if (schema.enum && schema.enum.length > 0) {
            const options = schema.enum.map(opt =>
                `<option value="${this.escapeHtml(opt)}" ${value === opt ? 'selected' : ''}>${this.escapeHtml(opt)}</option>`
            ).join('');
            return `
                <div class="field">
                    ${labelHtml}
                    ${descHtml}
                    <select name="${this.escapeHtml(key)}">${options}</select>
                </div>
            `;
        }

        // Boolean field - checkbox
        if (schema.type === 'boolean') {
            return `
                <div class="field">
                    <div class="checkbox-field">
                        <input type="checkbox" id="${this.escapeHtml(key)}" name="${this.escapeHtml(key)}" ${value ? 'checked' : ''}>
                        ${labelHtml}
                    </div>
                    ${descHtml}
                </div>
            `;
        }

        // Number field
        if (schema.type === 'number' || schema.type === 'integer') {
            return `
                <div class="field">
                    ${labelHtml}
                    ${descHtml}
                    <input type="number" name="${this.escapeHtml(key)}" value="${value ?? ''}" ${schema.type === 'integer' ? 'step="1"' : 'step="any"'}>
                </div>
            `;
        }

        // Object or array - JSON textarea
        if (schema.type === 'object' || schema.type === 'array' || typeof value === 'object') {
            const jsonValue = typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value ?? '');
            return `
                <div class="field">
                    ${labelHtml}
                    ${descHtml}
                    <textarea name="${this.escapeHtml(key)}" data-type="json">${this.escapeHtml(jsonValue)}</textarea>
                </div>
            `;
        }

        // Default: text input (for strings)
        const stringValue = String(value ?? '');
        // Use textarea for long strings
        if (stringValue.length > 50 || stringValue.includes('\n')) {
            return `
                <div class="field">
                    ${labelHtml}
                    ${descHtml}
                    <textarea name="${this.escapeHtml(key)}">${this.escapeHtml(stringValue)}</textarea>
                </div>
            `;
        }

        return `
            <div class="field">
                ${labelHtml}
                ${descHtml}
                <input type="text" name="${this.escapeHtml(key)}" value="${this.escapeHtml(stringValue)}">
            </div>
        `;
    }

    private escapeHtml(text: string): string {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    dispose(): void {
        for (const d of this._disposables) {
            d.dispose();
        }
    }
}

/**
 * Register the command to show stage config
 */
export function registerStageConfigCommands(
    context: vscode.ExtensionContext,
    stageConfigProvider: StageConfigViewProvider
): void {
    // Import here to avoid circular dependency
    const { StageConfigEditor } = require('../editors/stageConfigEditor');
    const { ReactStageConfigEditor } = require('../editors/reactStageConfigEditor');
    const { FlowMasonService } = require('../services/flowmasonService');

    const flowmasonService = new FlowMasonService();
    const stageConfigEditor = new StageConfigEditor(context.extensionUri, flowmasonService);
    const reactStageConfigEditor = new ReactStageConfigEditor(context.extensionUri, flowmasonService);

    context.subscriptions.push(
        vscode.commands.registerCommand(
            'flowmason.showStageConfig',
            async (stageId: string) => {
                // Try to get document from active text editor first
                let document: vscode.TextDocument | undefined;

                const editor = vscode.window.activeTextEditor;
                if (editor?.document.fileName.endsWith('.pipeline.json')) {
                    document = editor.document;
                }

                // Fall back to DAG canvas document if no text editor is active
                if (!document) {
                    document = DagCanvasProvider.currentDocument;
                }

                if (!document || !document.fileName.endsWith('.pipeline.json')) {
                    vscode.window.showWarningMessage('No pipeline document is active');
                    return;
                }

                try {
                    const pipeline = JSON.parse(document.getText()) as PipelineFile;
                    const stage = pipeline.stages.find(s => s.id === stageId);

                    if (stage) {
                        // Check if React editor is enabled
                        const config = vscode.workspace.getConfiguration('flowmason');
                        const useReactEditor = config.get<boolean>('useReactStageEditor', false);

                        if (useReactEditor) {
                            await reactStageConfigEditor.openEditor(stage, document);
                        } else {
                            await stageConfigEditor.openEditor(stage, document);
                        }
                    }
                } catch {
                    // Invalid JSON
                }
            }
        )
    );

    // Command to explicitly open React-based stage editor
    context.subscriptions.push(
        vscode.commands.registerCommand(
            'flowmason.showReactStageConfig',
            async (stageId: string) => {
                let document: vscode.TextDocument | undefined;

                const editor = vscode.window.activeTextEditor;
                if (editor?.document.fileName.endsWith('.pipeline.json')) {
                    document = editor.document;
                }

                if (!document) {
                    document = DagCanvasProvider.currentDocument;
                }

                if (!document || !document.fileName.endsWith('.pipeline.json')) {
                    vscode.window.showWarningMessage('No pipeline document is active');
                    return;
                }

                try {
                    const pipeline = JSON.parse(document.getText()) as PipelineFile;
                    const stage = pipeline.stages.find(s => s.id === stageId);

                    if (stage) {
                        await reactStageConfigEditor.openEditor(stage, document);
                    }
                } catch {
                    // Invalid JSON
                }
            }
        )
    );
}
