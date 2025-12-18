/**
 * JSON Tree View Provider
 *
 * A read-only Custom Text Editor that displays .pipeline.json files
 * as a collapsible tree view (like browser DevTools).
 *
 * Features:
 * - Collapsible/expandable nodes for objects and arrays
 * - Syntax highlighting using VSCode theme colors
 * - Copy JSON to clipboard
 * - "Edit in DAG Canvas" button
 * - Expand All / Collapse All
 * - Search/filter (optional)
 */

import * as vscode from 'vscode';

export class JsonTreeViewProvider implements vscode.CustomTextEditorProvider {
    public static readonly viewType = 'flowmason.jsonTreeView';

    constructor() {}

    async resolveCustomTextEditor(
        document: vscode.TextDocument,
        webviewPanel: vscode.WebviewPanel,
        _token: vscode.CancellationToken
    ): Promise<void> {
        webviewPanel.webview.options = {
            enableScripts: true
        };

        // Initial render
        this.updateWebview(webviewPanel.webview, document);

        // Watch for document changes (from DAG canvas edits)
        const changeDocumentSubscription = vscode.workspace.onDidChangeTextDocument(e => {
            if (e.document.uri.toString() === document.uri.toString()) {
                this.updateWebview(webviewPanel.webview, document);
            }
        });

        // Handle messages from webview
        webviewPanel.webview.onDidReceiveMessage(async message => {
            switch (message.type) {
                case 'openDagCanvas':
                    vscode.commands.executeCommand('vscode.openWith', document.uri, 'flowmason.dagCanvas');
                    break;

                case 'copyJson':
                    await vscode.env.clipboard.writeText(document.getText());
                    vscode.window.showInformationMessage('JSON copied to clipboard');
                    break;

                case 'copyValue':
                    await vscode.env.clipboard.writeText(message.value);
                    vscode.window.showInformationMessage('Value copied to clipboard');
                    break;
            }
        });

        // Cleanup
        webviewPanel.onDidDispose(() => {
            changeDocumentSubscription.dispose();
        });
    }

    private updateWebview(webview: vscode.Webview, document: vscode.TextDocument): void {
        let jsonData: unknown = null;
        let parseError: string | null = null;

        try {
            jsonData = JSON.parse(document.getText());
        } catch (e) {
            parseError = e instanceof Error ? e.message : 'Invalid JSON';
        }

        webview.html = this.getHtmlForWebview(webview, jsonData, parseError, document.fileName);
    }

    private getHtmlForWebview(
        webview: vscode.Webview,
        data: unknown,
        parseError: string | null,
        fileName: string
    ): string {
        const displayName = fileName.split('/').pop() || fileName;

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JSON Tree View</title>
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
            background: var(--vscode-editor-background);
            padding: 0;
            overflow: hidden;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 16px;
            background: var(--vscode-titleBar-activeBackground);
            border-bottom: 1px solid var(--vscode-panel-border);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-title {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .header-title h2 {
            font-size: 13px;
            font-weight: 500;
        }

        .read-only-badge {
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }

        .header-actions {
            display: flex;
            gap: 8px;
        }

        .btn {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            border: none;
            padding: 4px 12px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .btn:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }

        .btn-primary {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }

        .btn-primary:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .toolbar {
            display: flex;
            gap: 8px;
            padding: 8px 16px;
            background: var(--vscode-editor-background);
            border-bottom: 1px solid var(--vscode-panel-border);
        }

        .search-box {
            flex: 1;
            max-width: 300px;
            padding: 4px 8px;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            color: var(--vscode-input-foreground);
            border-radius: 3px;
            font-size: 12px;
        }

        .search-box:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        .tree-container {
            padding: 16px;
            overflow: auto;
            height: calc(100vh - 90px);
        }

        .error-container {
            padding: 20px;
            text-align: center;
            color: var(--vscode-errorForeground);
        }

        .error-container pre {
            background: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            padding: 12px;
            border-radius: 4px;
            margin-top: 12px;
            text-align: left;
            overflow: auto;
        }

        /* Tree Styles */
        .tree-node {
            font-family: var(--vscode-editor-font-family), monospace;
            font-size: 13px;
            line-height: 1.6;
        }

        .tree-row {
            display: flex;
            align-items: flex-start;
            padding: 2px 0;
            cursor: default;
        }

        .tree-row:hover {
            background: var(--vscode-list-hoverBackground);
        }

        .tree-toggle {
            width: 16px;
            height: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--vscode-foreground);
            opacity: 0.7;
            flex-shrink: 0;
            margin-top: 2px;
        }

        .tree-toggle:hover {
            opacity: 1;
        }

        .tree-toggle.collapsed::before {
            content: '▶';
            font-size: 8px;
        }

        .tree-toggle.expanded::before {
            content: '▼';
            font-size: 8px;
        }

        .tree-toggle.leaf {
            visibility: hidden;
        }

        .tree-indent {
            display: inline-block;
            width: 20px;
            flex-shrink: 0;
        }

        .tree-content {
            display: flex;
            align-items: baseline;
            gap: 4px;
            flex-wrap: wrap;
        }

        .tree-key {
            color: var(--vscode-symbolIcon-propertyForeground, #9cdcfe);
        }

        .tree-colon {
            color: var(--vscode-foreground);
            opacity: 0.6;
        }

        .tree-value-string {
            color: var(--vscode-debugTokenExpression-string, #ce9178);
        }

        .tree-value-number {
            color: var(--vscode-debugTokenExpression-number, #b5cea8);
        }

        .tree-value-boolean {
            color: var(--vscode-debugTokenExpression-boolean, #569cd6);
        }

        .tree-value-null {
            color: var(--vscode-debugTokenExpression-name, #569cd6);
            font-style: italic;
        }

        .tree-bracket {
            color: var(--vscode-foreground);
            opacity: 0.8;
        }

        .tree-type-hint {
            color: var(--vscode-descriptionForeground);
            font-size: 11px;
            margin-left: 8px;
        }

        .tree-children {
            margin-left: 20px;
        }

        .tree-children.collapsed {
            display: none;
        }

        .tree-ellipsis {
            color: var(--vscode-descriptionForeground);
            cursor: pointer;
        }

        .copy-btn {
            opacity: 0;
            background: transparent;
            border: none;
            color: var(--vscode-textLink-foreground);
            cursor: pointer;
            font-size: 11px;
            padding: 0 4px;
        }

        .tree-row:hover .copy-btn {
            opacity: 0.7;
        }

        .copy-btn:hover {
            opacity: 1 !important;
        }

        /* Search highlight */
        .highlight {
            background: var(--vscode-editor-findMatchHighlightBackground);
            border-radius: 2px;
        }

        /* Hidden nodes during search */
        .tree-node.hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">
            <h2>${this.escapeHtml(displayName)}</h2>
            <span class="read-only-badge">Read-Only</span>
        </div>
        <div class="header-actions">
            <button class="btn btn-primary" onclick="openDagCanvas()">
                Edit in DAG Canvas
            </button>
        </div>
    </div>

    <div class="toolbar">
        <button class="btn" onclick="expandAll()">Expand All</button>
        <button class="btn" onclick="collapseAll()">Collapse All</button>
        <button class="btn" onclick="copyJson()">Copy JSON</button>
        <input type="text" class="search-box" placeholder="Search..." oninput="handleSearch(this.value)">
    </div>

    ${parseError ? `
    <div class="error-container">
        <h3>Invalid JSON</h3>
        <pre>${this.escapeHtml(parseError)}</pre>
    </div>
    ` : `
    <div class="tree-container" id="tree-container">
        ${this.renderTreeNode(data, null, 0, true)}
    </div>
    `}

    <script>
        const vscode = acquireVsCodeApi();

        function openDagCanvas() {
            vscode.postMessage({ type: 'openDagCanvas' });
        }

        function copyJson() {
            vscode.postMessage({ type: 'copyJson' });
        }

        function copyValue(value) {
            vscode.postMessage({ type: 'copyValue', value: value });
        }

        function toggleNode(element) {
            const row = element.closest('.tree-node');
            const children = row.querySelector('.tree-children');
            const toggle = row.querySelector('.tree-toggle');

            if (children) {
                children.classList.toggle('collapsed');
                toggle.classList.toggle('collapsed');
                toggle.classList.toggle('expanded');
            }
        }

        function expandAll() {
            document.querySelectorAll('.tree-children.collapsed').forEach(el => {
                el.classList.remove('collapsed');
            });
            document.querySelectorAll('.tree-toggle.collapsed').forEach(el => {
                el.classList.remove('collapsed');
                el.classList.add('expanded');
            });
        }

        function collapseAll() {
            document.querySelectorAll('.tree-children').forEach(el => {
                el.classList.add('collapsed');
            });
            document.querySelectorAll('.tree-toggle.expanded').forEach(el => {
                el.classList.remove('expanded');
                el.classList.add('collapsed');
            });
        }

        function handleSearch(query) {
            const container = document.getElementById('tree-container');
            const allNodes = container.querySelectorAll('.tree-node');

            // Remove existing highlights
            container.querySelectorAll('.highlight').forEach(el => {
                el.outerHTML = el.innerHTML;
            });

            if (!query.trim()) {
                // Show all nodes
                allNodes.forEach(node => node.classList.remove('hidden'));
                return;
            }

            const lowerQuery = query.toLowerCase();

            allNodes.forEach(node => {
                const text = node.textContent.toLowerCase();
                if (text.includes(lowerQuery)) {
                    node.classList.remove('hidden');
                    // Expand parents
                    let parent = node.parentElement;
                    while (parent) {
                        if (parent.classList.contains('tree-children')) {
                            parent.classList.remove('collapsed');
                            const toggle = parent.previousElementSibling?.querySelector('.tree-toggle');
                            if (toggle) {
                                toggle.classList.remove('collapsed');
                                toggle.classList.add('expanded');
                            }
                        }
                        parent = parent.parentElement;
                    }
                } else {
                    node.classList.add('hidden');
                }
            });
        }
    </script>
</body>
</html>`;
    }

    private renderTreeNode(data: unknown, key: string | null, depth: number, expanded: boolean): string {
        const indent = '<span class="tree-indent"></span>'.repeat(depth);

        if (data === null) {
            return this.renderLeafNode(key, '<span class="tree-value-null">null</span>', depth, 'null');
        }

        if (typeof data === 'string') {
            const displayValue = data.length > 100 ? data.substring(0, 100) + '...' : data;
            return this.renderLeafNode(
                key,
                `<span class="tree-value-string">"${this.escapeHtml(displayValue)}"</span>`,
                depth,
                data
            );
        }

        if (typeof data === 'number') {
            return this.renderLeafNode(
                key,
                `<span class="tree-value-number">${data}</span>`,
                depth,
                String(data)
            );
        }

        if (typeof data === 'boolean') {
            return this.renderLeafNode(
                key,
                `<span class="tree-value-boolean">${data}</span>`,
                depth,
                String(data)
            );
        }

        if (Array.isArray(data)) {
            const toggleClass = expanded ? 'expanded' : 'collapsed';
            const childrenClass = expanded ? '' : 'collapsed';
            const typeHint = `(${data.length} item${data.length !== 1 ? 's' : ''})`;

            let html = `<div class="tree-node">
                <div class="tree-row">
                    ${indent}
                    <span class="tree-toggle ${toggleClass}" onclick="toggleNode(this)"></span>
                    <span class="tree-content">
                        ${key !== null ? `<span class="tree-key">"${this.escapeHtml(key)}"</span><span class="tree-colon">:</span>` : ''}
                        <span class="tree-bracket">[</span>
                        <span class="tree-type-hint">${typeHint}</span>
                    </span>
                </div>
                <div class="tree-children ${childrenClass}">`;

            data.forEach((item, index) => {
                html += this.renderTreeNode(item, String(index), depth + 1, depth < 1);
            });

            html += `</div>
                <div class="tree-row">
                    ${indent}<span class="tree-indent"></span>
                    <span class="tree-bracket">]</span>
                </div>
            </div>`;

            return html;
        }

        if (typeof data === 'object') {
            const keys = Object.keys(data as Record<string, unknown>);
            const toggleClass = expanded ? 'expanded' : 'collapsed';
            const childrenClass = expanded ? '' : 'collapsed';
            const typeHint = `(${keys.length} propert${keys.length !== 1 ? 'ies' : 'y'})`;

            let html = `<div class="tree-node">
                <div class="tree-row">
                    ${indent}
                    <span class="tree-toggle ${toggleClass}" onclick="toggleNode(this)"></span>
                    <span class="tree-content">
                        ${key !== null ? `<span class="tree-key">"${this.escapeHtml(key)}"</span><span class="tree-colon">:</span>` : ''}
                        <span class="tree-bracket">{</span>
                        <span class="tree-type-hint">${typeHint}</span>
                    </span>
                </div>
                <div class="tree-children ${childrenClass}">`;

            keys.forEach(k => {
                html += this.renderTreeNode((data as Record<string, unknown>)[k], k, depth + 1, depth < 1);
            });

            html += `</div>
                <div class="tree-row">
                    ${indent}<span class="tree-indent"></span>
                    <span class="tree-bracket">}</span>
                </div>
            </div>`;

            return html;
        }

        return '';
    }

    private renderLeafNode(key: string | null, valueHtml: string, depth: number, rawValue: string): string {
        const indent = '<span class="tree-indent"></span>'.repeat(depth);
        const escapedValue = this.escapeHtml(rawValue).replace(/"/g, '&quot;');

        return `<div class="tree-node">
            <div class="tree-row">
                ${indent}
                <span class="tree-toggle leaf"></span>
                <span class="tree-content">
                    ${key !== null ? `<span class="tree-key">"${this.escapeHtml(key)}"</span><span class="tree-colon">:</span>` : ''}
                    ${valueHtml}
                    <button class="copy-btn" onclick="copyValue('${escapedValue}')" title="Copy value">copy</button>
                </span>
            </div>
        </div>`;
    }

    private escapeHtml(text: string): string {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}

/**
 * Helper function to register the JSON tree view provider
 */
export function registerJsonTreeViewProvider(): vscode.Disposable {
    const provider = new JsonTreeViewProvider();

    return vscode.window.registerCustomEditorProvider(
        JsonTreeViewProvider.viewType,
        provider,
        {
            webviewOptions: {
                retainContextWhenHidden: true
            },
            supportsMultipleEditorsPerDocument: true
        }
    );
}
