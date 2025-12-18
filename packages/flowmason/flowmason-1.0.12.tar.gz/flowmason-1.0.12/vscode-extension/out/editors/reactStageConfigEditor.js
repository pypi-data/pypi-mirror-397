"use strict";
/**
 * React-based Stage Configuration Editor
 *
 * VSCode webview panel that hosts the React-based stage editor.
 * Provides a modern, visual-first configuration experience.
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
exports.ReactStageConfigEditor = void 0;
const vscode = __importStar(require("vscode"));
class ReactStageConfigEditor {
    constructor(extensionUri, flowmasonService) {
        this.extensionUri = extensionUri;
        this.flowmasonService = flowmasonService;
    }
    async openEditor(stage, document) {
        const panelKey = `${document.uri.toString()}:${stage.id}`;
        // Check if panel already exists
        const existingPanel = ReactStageConfigEditor.panels.get(panelKey);
        if (existingPanel) {
            existingPanel.reveal(vscode.ViewColumn.Two);
            return;
        }
        // Parse pipeline
        let pipeline;
        try {
            pipeline = JSON.parse(document.getText());
        }
        catch {
            vscode.window.showErrorMessage('Invalid pipeline JSON');
            return;
        }
        // Fetch component detail
        const componentDetail = await this.flowmasonService.getComponentDetail(stage.component_type);
        if (!componentDetail) {
            vscode.window.showWarningMessage(`Could not load component metadata for "${stage.component_type}". ` +
                'Make sure FlowMason Studio is running.');
        }
        // Fetch providers for LLM nodes
        let providers = [];
        if (componentDetail?.requires_llm) {
            providers = await this.flowmasonService.getProviders();
        }
        // Build data sources
        const dataSources = this.getDataSources(pipeline, stage.id, componentDetail);
        // Parse existing field mappings
        const existingMappings = this.parseExistingMappings(stage.config || {});
        // Create webview panel
        const panel = vscode.window.createWebviewPanel('flowmason.reactStageConfig', `Configure: ${stage.id}`, vscode.ViewColumn.Two, {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: [
                vscode.Uri.joinPath(this.extensionUri, 'out', 'webview-ui'),
                vscode.Uri.joinPath(this.extensionUri, 'images'),
            ],
        });
        ReactStageConfigEditor.panels.set(panelKey, panel);
        panel.iconPath = vscode.Uri.joinPath(this.extensionUri, 'images', 'flowmason-icon.svg');
        // Set HTML content
        panel.webview.html = this.getHtml(panel.webview);
        // Handle messages from webview
        panel.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'ready':
                    // Send initial data
                    const initData = {
                        stage,
                        componentDetail,
                        dataSources,
                        providers,
                        existingMappings,
                    };
                    panel.webview.postMessage({ type: 'init', data: initData });
                    break;
                case 'save':
                    await this.saveConfig(document, stage.id, message.config, message.output_config);
                    vscode.window.showInformationMessage(`Saved configuration for "${stage.id}"`);
                    break;
                case 'cancel':
                    panel.dispose();
                    break;
            }
        });
        panel.onDidDispose(() => {
            ReactStageConfigEditor.panels.delete(panelKey);
        });
    }
    getDataSources(pipeline, currentStageId, currentComponentDetail) {
        const sources = [];
        // Pipeline Input
        if (pipeline.input_schema?.properties) {
            const fields = Object.entries(pipeline.input_schema.properties).map(([name, prop]) => ({
                name,
                type: prop.type || 'any',
                description: prop.description,
                required: pipeline.input_schema?.required?.includes(name),
            }));
            sources.push({
                id: 'input',
                name: 'Pipeline Input',
                type: 'input',
                fields,
            });
        }
        // Upstream stages
        for (const stage of pipeline.stages) {
            if (stage.id === currentStageId)
                continue;
            const isDownstream = this.isDownstream(pipeline, stage.id, currentStageId);
            if (!isDownstream) {
                sources.push({
                    id: stage.id,
                    name: stage.id,
                    type: 'upstream',
                    fields: [{ name: 'result', type: 'any', description: 'Stage output' }],
                });
            }
        }
        return sources;
    }
    isDownstream(pipeline, stageId, targetId, visited = new Set()) {
        if (visited.has(stageId))
            return false;
        visited.add(stageId);
        const stage = pipeline.stages.find((s) => s.id === stageId);
        if (!stage?.depends_on)
            return false;
        if (stage.depends_on.includes(targetId))
            return true;
        for (const depId of stage.depends_on) {
            if (this.isDownstream(pipeline, depId, targetId, visited))
                return true;
        }
        return false;
    }
    parseExistingMappings(config) {
        const expr = config['jmespath_expression'];
        if (!expr)
            return [];
        const mappings = [];
        const match = expr.match(/^\{\s*(.+)\s*\}$/);
        if (!match)
            return [];
        const parts = match[1].split(/,\s*(?=[a-zA-Z_])/);
        for (const part of parts) {
            const [outputField, rest] = part.split(/:\s*/, 2);
            if (!outputField || !rest)
                continue;
            const mapping = {
                outputField: outputField.trim(),
                sourceType: 'input',
                sourcePath: '',
            };
            // Check for default value
            const defaultMatch = rest.match(/(.+?)\s*\|\|\s*(.+)$/);
            const value = defaultMatch ? defaultMatch[1].trim() : rest.trim();
            if (defaultMatch) {
                mapping.defaultValue = defaultMatch[2].trim().replace(/^[`"']|[`"']$/g, '');
            }
            // Determine source type
            if (value.startsWith('`') || value.startsWith('"') || /^\d+$/.test(value)) {
                mapping.sourceType = 'literal';
                mapping.literalValue = value.replace(/^[`"']|[`"']$/g, '');
            }
            else if (value.includes('(')) {
                mapping.sourceType = 'expression';
                mapping.expression = value;
            }
            else {
                mapping.sourceType = 'input';
                mapping.sourcePath = value;
            }
            mappings.push(mapping);
        }
        return mappings;
    }
    async saveConfig(document, stageId, config, outputConfig) {
        try {
            const pipeline = JSON.parse(document.getText());
            const stage = pipeline.stages.find((s) => s.id === stageId);
            if (!stage)
                return;
            stage.config = config;
            if (outputConfig && outputConfig.destinations && outputConfig.destinations.length > 0) {
                stage.output_config = outputConfig;
            }
            else {
                delete stage.output_config;
            }
            const edit = new vscode.WorkspaceEdit();
            edit.replace(document.uri, new vscode.Range(0, 0, document.lineCount, 0), JSON.stringify(pipeline, null, 2));
            await vscode.workspace.applyEdit(edit);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to save: ${error}`);
        }
    }
    getHtml(webview) {
        // Get the React bundle URI
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'out', 'webview-ui', 'stageEditor.js'));
        const nonce = getNonce();
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <title>Stage Configuration</title>
</head>
<body>
    <div id="root"></div>
    <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
    }
}
exports.ReactStageConfigEditor = ReactStageConfigEditor;
ReactStageConfigEditor.panels = new Map();
function getNonce() {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
//# sourceMappingURL=reactStageConfigEditor.js.map