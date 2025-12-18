"use strict";
/**
 * Preview Component Command
 *
 * Shows a preview of the FlowMason component in a webview panel.
 * Enhanced with interactive features, JSON schema view, and VS Code theme support.
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
exports.registerPreviewComponentCommand = registerPreviewComponentCommand;
const vscode = __importStar(require("vscode"));
let currentPanel;
function registerPreviewComponentCommand(context, componentParser) {
    const command = vscode.commands.registerCommand('flowmason.previewComponent', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'python') {
            vscode.window.showErrorMessage('Open a Python file with a FlowMason component');
            return;
        }
        const components = componentParser.parseDocument(editor.document);
        if (components.length === 0) {
            vscode.window.showWarningMessage('No FlowMason components found in this file');
            return;
        }
        // Get component at cursor or use first one
        let component = componentParser.getComponentAtPosition(editor.document, editor.selection.active);
        if (!component) {
            component = components[0];
        }
        // Reuse existing panel or create new one
        if (currentPanel) {
            currentPanel.reveal(vscode.ViewColumn.Beside);
            currentPanel.title = `Preview: ${component.name}`;
            currentPanel.webview.html = getPreviewHtml(component, currentPanel.webview, context);
        }
        else {
            currentPanel = vscode.window.createWebviewPanel('flowmasonPreview', `Preview: ${component.name}`, vscode.ViewColumn.Beside, {
                enableScripts: true,
                retainContextWhenHidden: true,
            });
            currentPanel.webview.html = getPreviewHtml(component, currentPanel.webview, context);
            // Handle messages from webview
            currentPanel.webview.onDidReceiveMessage(async (message) => {
                switch (message.command) {
                    case 'test':
                        vscode.commands.executeCommand('flowmason.testComponent');
                        break;
                    case 'openStudio':
                        vscode.commands.executeCommand('flowmason.openStudio');
                        break;
                    case 'copySchema':
                        vscode.env.clipboard.writeText(message.schema);
                        vscode.window.showInformationMessage('Schema copied to clipboard');
                        break;
                }
            }, undefined, context.subscriptions);
            currentPanel.onDidDispose(() => {
                currentPanel = undefined;
            }, null, context.subscriptions);
        }
    });
    context.subscriptions.push(command);
}
function generateJsonSchema(fields) {
    const properties = {};
    const required = [];
    for (const field of fields) {
        properties[field.name] = {
            type: mapPythonTypeToJsonType(field.type),
            description: field.description || undefined,
            default: field.default || undefined,
        };
        if (field.required) {
            required.push(field.name);
        }
    }
    return {
        type: 'object',
        properties,
        required: required.length > 0 ? required : undefined,
    };
}
function mapPythonTypeToJsonType(pythonType) {
    const typeMap = {
        'str': 'string',
        'int': 'integer',
        'float': 'number',
        'bool': 'boolean',
        'list': 'array',
        'dict': 'object',
        'List': 'array',
        'Dict': 'object',
        'Any': 'any',
        'Optional': 'null',
    };
    // Handle generic types like List[str]
    const match = pythonType.match(/^(\w+)\[/);
    if (match) {
        return typeMap[match[1]] || 'object';
    }
    return typeMap[pythonType] || 'string';
}
function getPreviewHtml(component, webview, context) {
    const inputSchema = generateJsonSchema(component.inputFields);
    const outputSchema = generateJsonSchema(component.outputFields);
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Component Preview</title>
    <style>
        :root {
            --vscode-font: var(--vscode-font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
            --bg-primary: var(--vscode-editor-background, #1e1e1e);
            --bg-secondary: var(--vscode-sideBar-background, #252526);
            --text-primary: var(--vscode-editor-foreground, #cccccc);
            --text-secondary: var(--vscode-descriptionForeground, #999999);
            --border-color: var(--vscode-panel-border, #3c3c3c);
            --accent-color: ${component.color || '#6366f1'};
            --button-bg: var(--vscode-button-background, #0e639c);
            --button-fg: var(--vscode-button-foreground, #ffffff);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--vscode-font);
            padding: 16px;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.5;
        }

        .component-card {
            background: var(--bg-secondary);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            overflow: hidden;
        }

        .component-header {
            padding: 20px;
            background: linear-gradient(135deg, var(--accent-color) 0%, ${adjustColor(component.color || '#6366f1', -30)} 100%);
            color: white;
        }

        .header-row {
            display: flex;
            align-items: flex-start;
            gap: 16px;
        }

        .component-icon {
            width: 56px;
            height: 56px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .component-icon svg {
            width: 28px;
            height: 28px;
        }

        .component-info {
            flex: 1;
        }

        .component-name {
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .component-description {
            opacity: 0.9;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .component-badges {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 10px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge-llm {
            background: ${component.requires_llm ? 'rgba(251, 191, 36, 0.3)' : 'rgba(16, 185, 129, 0.3)'};
        }

        .component-body {
            padding: 20px;
        }

        .actions {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            background: var(--button-bg);
            color: var(--button-fg);
            border: none;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: opacity 0.2s;
        }

        .btn:hover {
            opacity: 0.9;
        }

        .btn-secondary {
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }

        .tabs {
            display: flex;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 16px;
        }

        .tab {
            padding: 10px 16px;
            border: none;
            background: none;
            color: var(--text-secondary);
            font-size: 13px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }

        .tab:hover {
            color: var(--text-primary);
        }

        .tab.active {
            color: var(--accent-color);
            border-bottom-color: var(--accent-color);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .section {
            margin-bottom: 20px;
        }

        .section-title {
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }

        .section-title .count {
            background: var(--accent-color);
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
        }

        .field-list {
            list-style: none;
        }

        .field-item {
            padding: 12px;
            background: var(--bg-primary);
            border-radius: 6px;
            margin-bottom: 8px;
            border: 1px solid var(--border-color);
        }

        .field-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
        }

        .field-name {
            font-weight: 600;
            color: var(--accent-color);
        }

        .field-type {
            font-family: monospace;
            font-size: 12px;
            color: var(--text-secondary);
            background: var(--bg-secondary);
            padding: 2px 6px;
            border-radius: 3px;
        }

        .field-required {
            color: #ef4444;
            font-weight: 600;
        }

        .field-description {
            color: var(--text-secondary);
            font-size: 13px;
        }

        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }

        .metadata-item {
            background: var(--bg-primary);
            padding: 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }

        .metadata-label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .metadata-value {
            font-weight: 500;
        }

        .schema-view {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
        }

        .schema-view pre {
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 12px;
            line-height: 1.6;
            margin: 0;
        }

        .copy-btn {
            float: right;
            padding: 4px 8px;
            font-size: 11px;
            margin-left: 8px;
        }

        .no-fields {
            color: var(--text-secondary);
            font-style: italic;
            padding: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="component-card">
        <div class="component-header">
            <div class="header-row">
                <div class="component-icon">
                    ${getIconSvg(component.icon || 'box')}
                </div>
                <div class="component-info">
                    <div class="component-name">${component.name}</div>
                    <div class="component-description">${component.description || 'No description provided.'}</div>
                    <div class="component-badges">
                        <span class="badge">${component.type.toUpperCase()}</span>
                        <span class="badge">${component.category}</span>
                        <span class="badge">v${component.version}</span>
                        <span class="badge badge-llm">${component.requires_llm ? '🧠 LLM Required' : '⚡ No LLM'}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="component-body">
            <div class="actions">
                <button class="btn" onclick="runTest()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    Run Test
                </button>
                <button class="btn btn-secondary" onclick="openStudio()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                    Open in Studio
                </button>
            </div>

            <div class="tabs">
                <button class="tab active" onclick="showTab('fields')">Fields</button>
                <button class="tab" onclick="showTab('schema')">JSON Schema</button>
                <button class="tab" onclick="showTab('metadata')">Metadata</button>
            </div>

            <div id="tab-fields" class="tab-content active">
                <div class="section">
                    <div class="section-title">
                        📥 Input Fields
                        <span class="count">${component.inputFields.length}</span>
                    </div>
                    ${component.inputFields.length > 0 ? `
                    <ul class="field-list">
                        ${component.inputFields.map(field => `
                        <li class="field-item">
                            <div class="field-header">
                                <span class="field-name">${field.name}</span>
                                <span class="field-type">${field.type}</span>
                                ${field.required ? '<span class="field-required">*</span>' : ''}
                            </div>
                            ${field.description ? `<div class="field-description">${field.description}</div>` : ''}
                        </li>
                        `).join('')}
                    </ul>
                    ` : '<div class="no-fields">No input fields defined</div>'}
                </div>

                <div class="section">
                    <div class="section-title">
                        📤 Output Fields
                        <span class="count">${component.outputFields.length}</span>
                    </div>
                    ${component.outputFields.length > 0 ? `
                    <ul class="field-list">
                        ${component.outputFields.map(field => `
                        <li class="field-item">
                            <div class="field-header">
                                <span class="field-name">${field.name}</span>
                                <span class="field-type">${field.type}</span>
                            </div>
                            ${field.description ? `<div class="field-description">${field.description}</div>` : ''}
                        </li>
                        `).join('')}
                    </ul>
                    ` : '<div class="no-fields">No output fields defined</div>'}
                </div>
            </div>

            <div id="tab-schema" class="tab-content">
                <div class="section">
                    <div class="section-title">
                        📥 Input Schema
                        <button class="btn btn-secondary copy-btn" onclick="copySchema('input')">Copy</button>
                    </div>
                    <div class="schema-view">
                        <pre id="input-schema">${JSON.stringify(inputSchema, null, 2)}</pre>
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">
                        📤 Output Schema
                        <button class="btn btn-secondary copy-btn" onclick="copySchema('output')">Copy</button>
                    </div>
                    <div class="schema-view">
                        <pre id="output-schema">${JSON.stringify(outputSchema, null, 2)}</pre>
                    </div>
                </div>
            </div>

            <div id="tab-metadata" class="tab-content">
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <div class="metadata-label">Component Type</div>
                        <div class="metadata-value">${component.type}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Category</div>
                        <div class="metadata-value">${component.category}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Class Name</div>
                        <div class="metadata-value">${component.className}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Version</div>
                        <div class="metadata-value">${component.version}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">LLM Required</div>
                        <div class="metadata-value">${component.requires_llm ? 'Yes' : 'No'}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Icon</div>
                        <div class="metadata-value">${component.icon || 'default'}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Color</div>
                        <div class="metadata-value" style="display: flex; align-items: center; gap: 8px;">
                            <span style="width: 16px; height: 16px; background: ${component.color || '#6366f1'}; border-radius: 3px; display: inline-block;"></span>
                            ${component.color || '#6366f1'}
                        </div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Input Fields</div>
                        <div class="metadata-value">${component.inputFields.length}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            document.querySelector(\`.tab[onclick*="\${tabName}"]\`).classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
        }

        function runTest() {
            vscode.postMessage({ command: 'test' });
        }

        function openStudio() {
            vscode.postMessage({ command: 'openStudio' });
        }

        function copySchema(type) {
            const schema = document.getElementById(type + '-schema').textContent;
            vscode.postMessage({ command: 'copySchema', schema: schema });
        }
    </script>
</body>
</html>`;
}
function adjustColor(color, amount) {
    const hex = color.replace('#', '');
    const r = Math.max(0, Math.min(255, parseInt(hex.slice(0, 2), 16) + amount));
    const g = Math.max(0, Math.min(255, parseInt(hex.slice(2, 4), 16) + amount));
    const b = Math.max(0, Math.min(255, parseInt(hex.slice(4, 6), 16) + amount));
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}
function getIconSvg(icon) {
    const icons = {
        'brain': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/></svg>',
        'sparkles': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>',
        'shuffle': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 18h1.4c1.3 0 2.5-.6 3.3-1.7l6.1-8.6c.7-1.1 2-1.7 3.3-1.7H22"/><path d="m18 2 4 4-4 4"/><path d="M2 6h1.9c1.5 0 2.9.9 3.6 2.2"/><path d="M22 18h-5.9c-1.3 0-2.6-.7-3.3-1.8l-.5-.8"/><path d="m18 14 4 4-4 4"/></svg>',
        'filter': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>',
        'code': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
        'box': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
        'zap': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
        'message-square': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
        'search': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
        'database': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
        'globe': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
        'file-text': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
        'merge': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m8 6 4-4 4 4"/><path d="M12 2v10.3a4 4 0 0 1-1.172 2.872L4 22"/><path d="m20 22-5-5"/></svg>',
        'split': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 3h5v5"/><path d="M8 3H3v5"/><path d="M12 22v-8.3a4 4 0 0 0-1.172-2.872L3 3"/><path d="m15 9 6-6"/></svg>',
        'transform': '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22v-6"/><path d="M12 8V2"/><path d="M4 12H2"/><path d="M10 12H8"/><path d="M16 12h-2"/><path d="M22 12h-2"/><circle cx="12" cy="12" r="2"/></svg>',
    };
    return icons[icon] || icons['box'];
}
//# sourceMappingURL=previewComponent.js.map