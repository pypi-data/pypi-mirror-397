/**
 * Visual-First Stage Configuration Editor
 *
 * Salesforce Flow-style configuration:
 * - 100% visual, no-code for admins/junior developers
 * - Configuration through forms, dropdowns, point-and-click
 * - JSON is generated automatically, shown read-only
 * - Users NEVER type {{...}} template syntax
 */

import * as vscode from 'vscode';
import { FlowMasonService, ComponentDetail, Provider, AIConfig } from '../services/flowmasonService';
import { PipelineStage, PipelineFile, InputSchema, OutputDestination, OutputConfig } from '../views/pipelineStagesTree';

/**
 * JSON Schema property definition
 */
interface JSONSchemaProperty {
    type?: string;
    description?: string;
    default?: unknown;
    enum?: string[];
    minimum?: number;
    maximum?: number;
    minLength?: number;
    maxLength?: number;
    format?: string;
    items?: JSONSchemaProperty;
    properties?: Record<string, JSONSchemaProperty>;
    required?: string[];
    $ref?: string;
    examples?: unknown[];
}

/**
 * JSON Schema definition
 */
interface JSONSchema {
    type?: string;
    properties?: Record<string, JSONSchemaProperty>;
    required?: string[];
    $defs?: Record<string, JSONSchemaProperty>;
}

interface FieldInfo {
    name: string;
    type: string;
    description?: string;
    required?: boolean;
    default?: unknown;
    enum?: string[];
}

interface DataSource {
    id: string;
    name: string;
    type: 'input' | 'upstream';
    fields: FieldInfo[];
}

interface FieldMapping {
    outputField: string;
    sourceType: 'input' | 'upstream' | 'expression' | 'literal';
    sourcePath?: string;
    expression?: string;
    literalValue?: string;
    defaultValue?: string;
}

/**
 * Icon mapping for component categories (fallback)
 */
const CATEGORY_ICONS: Record<string, string> = {
    'core': '⚙️',
    'ai': '✨',
    'transform': '🔄',
    'integration': '🌐',
    'control-flow': '🔀',
    'debug': '📝',
    'general': '📦',
};

/**
 * Get icon for component based on its metadata
 */
function getComponentIcon(component?: ComponentDetail | null): string {
    if (!component) return '📦';
    if (component.icon) return component.icon;
    if (component.requires_llm) return '✨';
    return CATEGORY_ICONS[component.category?.toLowerCase() || 'general'] || '📦';
}

export class StageConfigEditor {
    private static panels: Map<string, vscode.WebviewPanel> = new Map();

    constructor(
        private readonly extensionUri: vscode.Uri,
        private readonly flowmasonService: FlowMasonService
    ) {}

    async openEditor(stage: PipelineStage, document: vscode.TextDocument): Promise<void> {
        const panelKey = `${document.uri.toString()}:${stage.id}`;

        const existingPanel = StageConfigEditor.panels.get(panelKey);
        if (existingPanel) {
            existingPanel.reveal(vscode.ViewColumn.Two);
            return;
        }

        let pipeline: PipelineFile;
        try {
            pipeline = JSON.parse(document.getText());
        } catch {
            vscode.window.showErrorMessage('Invalid pipeline JSON');
            return;
        }

        // Fetch component detail from API (dynamic, not hardcoded!)
        const componentDetail = await this.flowmasonService.getComponentDetail(stage.component_type);
        if (!componentDetail) {
            vscode.window.showWarningMessage(
                `Could not load component metadata for "${stage.component_type}". ` +
                'Make sure FlowMason Studio is running.'
            );
        }

        // Fetch available providers if this is an AI node
        let providers: Provider[] = [];
        if (componentDetail?.requires_llm) {
            providers = await this.flowmasonService.getProviders();
        }

        const dataSources = this.getDataSources(pipeline, stage.id, componentDetail);

        const panel = vscode.window.createWebviewPanel(
            'flowmason.stageConfig',
            `Configure: ${stage.id}`,
            vscode.ViewColumn.Two,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
            }
        );

        StageConfigEditor.panels.set(panelKey, panel);
        panel.iconPath = vscode.Uri.joinPath(this.extensionUri, 'images', 'flowmason-icon.svg');

        panel.webview.html = this.getHtml(stage, pipeline, dataSources, componentDetail, providers);

        panel.webview.onDidReceiveMessage(async message => {
            switch (message.type) {
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
            StageConfigEditor.panels.delete(panelKey);
        });
    }

    private getDataSources(
        pipeline: PipelineFile,
        currentStageId: string,
        currentComponentDetail?: ComponentDetail | null
    ): DataSource[] {
        const sources: DataSource[] = [];

        // Pipeline Input
        if (pipeline.input_schema?.properties) {
            const fields: FieldInfo[] = [];
            for (const [name, prop] of Object.entries(pipeline.input_schema.properties)) {
                fields.push({
                    name,
                    type: prop.type || 'any',
                    description: prop.description,
                    required: pipeline.input_schema.required?.includes(name),
                    default: prop.default,
                });
            }
            sources.push({
                id: 'input',
                name: 'Pipeline Input',
                type: 'input',
                fields,
            });
        }

        // Upstream stages - extract output fields from output_schema
        for (const stage of pipeline.stages) {
            if (stage.id === currentStageId) continue;

            const isDownstream = this.isDownstream(pipeline, stage.id, currentStageId);
            if (!isDownstream) {
                // Try to get output fields from the stage's component output_schema
                // For now, we'll use a generic output until we fetch each component's schema
                const outputs: FieldInfo[] = [{ name: 'result', type: 'any', description: 'Stage output' }];

                sources.push({
                    id: stage.id,
                    name: stage.id,
                    type: 'upstream',
                    fields: outputs,
                });
            }
        }

        return sources;
    }

    private isDownstream(pipeline: PipelineFile, stageId: string, targetId: string, visited = new Set<string>()): boolean {
        if (visited.has(stageId)) return false;
        visited.add(stageId);

        const stage = pipeline.stages.find(s => s.id === stageId);
        if (!stage?.depends_on) return false;
        if (stage.depends_on.includes(targetId)) return true;

        for (const depId of stage.depends_on) {
            if (this.isDownstream(pipeline, depId, targetId, visited)) return true;
        }
        return false;
    }

    private async saveConfig(
        document: vscode.TextDocument,
        stageId: string,
        config: Record<string, unknown>,
        outputConfig?: OutputConfig | null
    ): Promise<void> {
        try {
            const pipeline = JSON.parse(document.getText()) as PipelineFile;
            const stage = pipeline.stages.find(s => s.id === stageId);
            if (!stage) return;

            stage.config = config;

            // Save output_config if provided
            if (outputConfig && outputConfig.destinations && outputConfig.destinations.length > 0) {
                stage.output_config = outputConfig;
            } else {
                // Remove output_config if no destinations
                delete stage.output_config;
            }

            const edit = new vscode.WorkspaceEdit();
            edit.replace(
                document.uri,
                new vscode.Range(0, 0, document.lineCount, 0),
                JSON.stringify(pipeline, null, 2)
            );
            await vscode.workspace.applyEdit(edit);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to save: ${error}`);
        }
    }

    private getHtml(
        stage: PipelineStage,
        pipeline: PipelineFile,
        dataSources: DataSource[],
        componentDetail: ComponentDetail | null,
        providers: Provider[]
    ): string {
        const config = stage.config || {};
        const icon = getComponentIcon(componentDetail);
        const name = componentDetail?.name || stage.component_type;
        const category = componentDetail?.category || 'custom';
        const description = componentDetail?.description || '';

        // Extract input_schema for dynamic form rendering
        const inputSchema = componentDetail?.input_schema as JSONSchema | undefined;
        const outputSchema = componentDetail?.output_schema as JSONSchema | undefined;

        // Parse field mappings if this is a json_transform
        const existingMappings = this.parseExistingMappings(config);

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                ${this.getStyles()}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <div class="header-icon">${icon}</div>
                    <div class="header-content">
                        <h1>${this.escapeHtml(name)}</h1>
                        <div class="stage-id">${this.escapeHtml(stage.id)}</div>
                        <p class="description">${this.escapeHtml(description)}</p>
                        <span class="badge badge-${category.toLowerCase().replace(' ', '-')}">${this.escapeHtml(category)}</span>
                    </div>
                </div>

                <form id="configForm">
                    <!-- INCOMING DATA Section -->
                    <div class="flow-section incoming-section">
                        <div class="section-header clickable" onclick="toggleSection('incoming')">
                            <span class="section-icon" id="incoming-chevron">▼</span>
                            <span class="section-badge incoming">📥 INCOMING</span>
                            <h2>Input Data</h2>
                        </div>
                        <div class="section-content" id="incoming-content">
                            ${this.renderIncomingSection(dataSources)}
                        </div>
                    </div>

                    <!-- TRANSFORM/INTERNAL Section -->
                    <div class="flow-section transform-section">
                        <div class="section-header clickable" onclick="toggleSection('transform')">
                            <span class="section-icon" id="transform-chevron">▼</span>
                            <span class="section-badge transform">⚙️ TRANSFORM</span>
                            <h2>Processing Logic</h2>
                        </div>
                        <div class="section-content" id="transform-content">
                            ${this.renderTransformSection(inputSchema, config, dataSources, existingMappings, componentDetail, providers)}
                        </div>
                    </div>

                    <!-- OUTGOING DATA Section -->
                    <div class="flow-section outgoing-section">
                        <div class="section-header clickable" onclick="toggleSection('outgoing')">
                            <span class="section-icon" id="outgoing-chevron">▼</span>
                            <span class="section-badge outgoing">📤 OUTGOING</span>
                            <h2>Output Data</h2>
                        </div>
                        <div class="section-content" id="outgoing-content">
                            ${this.renderOutgoingSection(stage, pipeline, outputSchema, existingMappings)}
                        </div>
                    </div>
                </form>

                <!-- Generated JSON (Read-Only) -->
                <div class="flow-section json-section">
                    <div class="section-header clickable" onclick="toggleSection('json')">
                        <span class="section-icon" id="json-chevron">▶</span>
                        <span class="section-badge json">{ }</span>
                        <h2>Generated JSON</h2>
                        <span class="badge badge-readonly">Read-Only</span>
                    </div>
                    <div class="section-content collapsed" id="json-content">
                        <div class="json-view">
                            <pre id="jsonPreview">${this.escapeHtml(JSON.stringify(config, null, 2) || '{}')}</pre>
                            <button type="button" class="copy-btn" onclick="copyJson()">📋 Copy</button>
                        </div>
                    </div>
                </div>

                <!-- Actions -->
                <div class="actions">
                    <button type="button" class="primary" onclick="save()">
                        💾 Save Configuration
                    </button>
                    <button type="button" class="secondary" onclick="cancel()">
                        Cancel
                    </button>
                </div>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                const dataSources = ${JSON.stringify(dataSources)};
                let fieldMappings = ${JSON.stringify(existingMappings)};
                let stageDestinations = ${JSON.stringify(stage.output_config?.destinations || [])};

                function toggleSection(sectionId) {
                    const content = document.getElementById(sectionId + '-content');
                    const chevron = document.getElementById(sectionId + '-chevron');
                    if (content && chevron) {
                        content.classList.toggle('collapsed');
                        chevron.textContent = content.classList.contains('collapsed') ? '▶' : '▼';
                    }
                }

                function toggleJsonView() {
                    const view = document.getElementById('jsonView');
                    const chevron = document.getElementById('json-chevron');
                    view.classList.toggle('collapsed');
                    chevron.textContent = view.classList.contains('collapsed') ? '▶' : '▼';
                }

                function copyJson() {
                    const json = document.getElementById('jsonPreview').textContent;
                    navigator.clipboard.writeText(json);
                }

                function updateJsonPreview() {
                    const config = getConfig();
                    document.getElementById('jsonPreview').textContent = JSON.stringify(config, null, 2);
                }

                function getConfig() {
                    const form = document.getElementById('configForm');
                    const config = {};

                    // Handle regular form fields
                    form.querySelectorAll('input, select, textarea').forEach(el => {
                        const name = el.name;
                        if (!name || name.startsWith('mapping-')) return;

                        let value;
                        if (el.type === 'checkbox') {
                            value = el.checked;
                        } else if (el.type === 'number') {
                            value = el.value ? parseFloat(el.value) : undefined;
                        } else if (el.dataset.type === 'json') {
                            try {
                                value = el.value.trim() ? JSON.parse(el.value) : undefined;
                            } catch {
                                value = el.value;
                            }
                        } else {
                            value = el.value || undefined;
                        }

                        if (value !== undefined && value !== '') {
                            config[name] = value;
                        }
                    });

                    // Handle field mappings (for json_transform)
                    if (fieldMappings.length > 0) {
                        const expr = generateJmesPathExpression();
                        if (expr) {
                            config['jmespath_expression'] = expr;
                        }
                    }

                    return config;
                }

                function generateJmesPathExpression() {
                    if (fieldMappings.length === 0) return null;

                    const parts = fieldMappings.map(m => {
                        let value;
                        if (m.sourceType === 'literal') {
                            // Clean the literal value and wrap in backticks
                            const cleanLiteral = (m.literalValue || '').replace(/^\`|\`$/g, '').trim();
                            value = m.literalValue.startsWith('"') ? m.literalValue : '\`' + cleanLiteral + '\`';
                        } else if (m.sourceType === 'expression') {
                            value = m.expression;
                        } else {
                            value = m.sourcePath?.split('.').pop() || m.sourcePath;
                        }

                        if (m.defaultValue) {
                            // Clean the default value - remove any existing backticks before wrapping
                            const cleanDefault = (m.defaultValue || '').replace(/^\`|\`$/g, '').trim();
                            value = value + ' || \`' + cleanDefault + '\`';
                        }

                        return m.outputField + ': ' + value;
                    });

                    return '{ ' + parts.join(', ') + ' }';
                }

                function addFieldMapping() {
                    fieldMappings.push({
                        outputField: 'field_' + (fieldMappings.length + 1),
                        sourceType: 'input',
                        sourcePath: '',
                        defaultValue: ''
                    });
                    renderFieldMappings();
                    updateJsonPreview();
                }

                function removeFieldMapping(index) {
                    fieldMappings.splice(index, 1);
                    renderFieldMappings();
                    updateJsonPreview();
                }

                function updateMapping(index, field, value) {
                    fieldMappings[index][field] = value;
                    updateJsonPreview();
                }

                function renderFieldMappings() {
                    const container = document.getElementById('fieldMappingsContainer');
                    if (!container) return;

                    container.innerHTML = fieldMappings.map((m, i) => \`
                        <div class="mapping-row">
                            <div class="mapping-output">
                                <label>Output Field</label>
                                <input type="text" value="\${m.outputField}"
                                       onchange="updateMapping(\${i}, 'outputField', this.value)"
                                       placeholder="field_name">
                            </div>
                            <div class="mapping-arrow">←</div>
                            <div class="mapping-source">
                                <label>Source</label>
                                <select onchange="updateMapping(\${i}, 'sourceType', this.value); updateMapping(\${i}, 'sourcePath', ''); renderFieldMappings();">
                                    <option value="input" \${m.sourceType === 'input' ? 'selected' : ''}>Pipeline Input</option>
                                    <option value="expression" \${m.sourceType === 'expression' ? 'selected' : ''}>Expression</option>
                                    <option value="literal" \${m.sourceType === 'literal' ? 'selected' : ''}>Fixed Value</option>
                                    \${dataSources.filter(s => s.type === 'upstream').map(s =>
                                        '<option value="upstream:' + s.id + '" ' + (m.sourceType === 'upstream' && m.sourcePath?.startsWith(s.id) ? 'selected' : '') + '>Stage: ' + s.name + '</option>'
                                    ).join('')}
                                </select>
                                \${renderSourceInput(m, i)}
                            </div>
                            <div class="mapping-default">
                                <label>Default</label>
                                <input type="text" value="\${m.defaultValue || ''}"
                                       onchange="updateMapping(\${i}, 'defaultValue', this.value)"
                                       placeholder="if empty">
                            </div>
                            <button type="button" class="remove-btn" onclick="removeFieldMapping(\${i})">✕</button>
                        </div>
                    \`).join('');
                }

                function renderSourceInput(mapping, index) {
                    if (mapping.sourceType === 'expression') {
                        return '<input type="text" value="' + (mapping.expression || '') + '" onchange="updateMapping(' + index + ', \\'expression\\', this.value)" placeholder="length(text)">';
                    }
                    if (mapping.sourceType === 'literal') {
                        return '<input type="text" value="' + (mapping.literalValue || '') + '" onchange="updateMapping(' + index + ', \\'literalValue\\', this.value)" placeholder="fixed value">';
                    }
                    if (mapping.sourceType === 'input') {
                        const inputSource = dataSources.find(s => s.type === 'input');
                        const fields = inputSource?.fields || [];
                        return '<select onchange="updateMapping(' + index + ', \\'sourcePath\\', this.value)">' +
                            '<option value="">-- Select field --</option>' +
                            fields.map(f => '<option value="' + f.name + '" ' + (mapping.sourcePath === f.name ? 'selected' : '') + '>' + f.name + ' (' + f.type + ')</option>').join('') +
                            '</select>';
                    }
                    if (mapping.sourceType.startsWith('upstream:')) {
                        const stageId = mapping.sourceType.split(':')[1];
                        const source = dataSources.find(s => s.id === stageId);
                        const fields = source?.fields || [];
                        return '<select onchange="updateMapping(' + index + ', \\'sourcePath\\', \\'' + stageId + '.\\' + this.value)">' +
                            '<option value="">-- Select field --</option>' +
                            fields.map(f => '<option value="' + f.name + '" ' + (mapping.sourcePath === stageId + '.' + f.name ? 'selected' : '') + '>' + f.name + ' (' + f.type + ')</option>').join('') +
                            '</select>';
                    }
                    return '';
                }

                function insertVariable(inputId, varRef) {
                    const input = document.querySelector('[name="' + inputId + '"]');
                    if (input) {
                        const start = input.selectionStart || input.value.length;
                        const text = input.value;
                        input.value = text.substring(0, start) + varRef + text.substring(start);
                        input.focus();
                        updateJsonPreview();
                    }
                }

                function save() {
                    const config = getConfig();
                    const outputConfig = stageDestinations.length > 0
                        ? { destinations: stageDestinations }
                        : null;
                    vscode.postMessage({ type: 'save', config, output_config: outputConfig });
                }

                function cancel() {
                    vscode.postMessage({ type: 'cancel' });
                }

                // ========== Destination Management ==========

                function showAddDestinationMenu() {
                    const menu = document.getElementById('destinationTypeMenu');
                    if (menu) {
                        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
                    }
                }

                function hideDestinationMenu() {
                    const menu = document.getElementById('destinationTypeMenu');
                    if (menu) {
                        menu.style.display = 'none';
                    }
                }

                function addDestination(destType) {
                    hideDestinationMenu();

                    // Create a new destination with defaults
                    const newDest = {
                        id: 'dest_' + Date.now(),
                        type: destType,
                        name: getDestinationTypeLabel(destType),
                        enabled: true,
                        on_success: true,
                        on_error: false,
                        config: getDefaultDestinationConfig(destType)
                    };

                    stageDestinations.push(newDest);
                    renderStageDestinations();
                    updateJsonPreview();

                    // Open edit dialog for the new destination
                    editDestination(stageDestinations.length - 1);
                }

                function getDestinationTypeLabel(destType) {
                    const labels = {
                        'webhook': 'New Webhook',
                        'email': 'New Email',
                        'database': 'New Database',
                        'message_queue': 'New Message Queue'
                    };
                    return labels[destType] || destType;
                }

                function getDefaultDestinationConfig(destType) {
                    const configs = {
                        'webhook': { url: '', method: 'POST', headers: {} },
                        'email': { to: [], subject: '', body: '' },
                        'database': { connection: '', table: '', fields: {} },
                        'message_queue': { connection: '', topic: '', format: 'json' }
                    };
                    return configs[destType] || {};
                }

                function removeDestination(index) {
                    stageDestinations.splice(index, 1);
                    renderStageDestinations();
                    updateJsonPreview();
                }

                function editDestination(index) {
                    const dest = stageDestinations[index];
                    if (!dest) return;

                    // Simple prompt-based editing for now
                    // TODO: Replace with proper modal dialog
                    const name = prompt('Destination name:', dest.name || '');
                    if (name === null) return;
                    dest.name = name;

                    if (dest.type === 'webhook') {
                        const url = prompt('Webhook URL:', dest.config.url || '');
                        if (url !== null) dest.config.url = url;
                    } else if (dest.type === 'email') {
                        const to = prompt('Email to (comma-separated):', (dest.config.to || []).join(', '));
                        if (to !== null) dest.config.to = to.split(',').map(e => e.trim()).filter(e => e);

                        const subject = prompt('Email subject:', dest.config.subject || '');
                        if (subject !== null) dest.config.subject = subject;
                    }

                    const onSuccess = confirm('Trigger on success?');
                    dest.on_success = onSuccess;

                    const onError = confirm('Trigger on error?');
                    dest.on_error = onError;

                    renderStageDestinations();
                    updateJsonPreview();
                }

                function renderStageDestinations() {
                    const container = document.getElementById('stageDestinationsContainer');
                    if (!container) return;

                    const typeIcons = { webhook: '🌐', email: '📧', database: '💾', message_queue: '📨' };
                    const typeLabels = { webhook: 'Webhook', email: 'Email', database: 'Database', message_queue: 'Message Queue' };

                    if (stageDestinations.length === 0) {
                        container.innerHTML = '<div class="no-destinations-hint">No stage-specific destinations configured.</div>';
                        return;
                    }

                    container.innerHTML = stageDestinations.map((dest, i) => \`
                        <div class="destination-item stage-specific" data-index="\${i}">
                            <span class="dest-icon">\${typeIcons[dest.type] || '📤'}</span>
                            <span class="dest-name">\${dest.name || 'New Destination'}</span>
                            <span class="dest-type">\${typeLabels[dest.type] || dest.type}</span>
                            \${dest.on_success ? '<span class="dest-badge success">on success</span>' : ''}
                            \${dest.on_error ? '<span class="dest-badge error">on error</span>' : ''}
                            <button type="button" class="dest-edit-btn" onclick="editDestination(\${i})">✏️</button>
                            <button type="button" class="dest-remove-btn" onclick="removeDestination(\${i})">✕</button>
                        </div>
                    \`).join('');
                }

                // Close destination menu when clicking outside
                document.addEventListener('click', (e) => {
                    const menu = document.getElementById('destinationTypeMenu');
                    const addBtn = document.querySelector('.add-destination-btn');
                    if (menu && !menu.contains(e.target) && e.target !== addBtn) {
                        hideDestinationMenu();
                    }
                });

                // Initialize field mappings display
                if (document.getElementById('fieldMappingsContainer')) {
                    renderFieldMappings();
                }

                // Update preview on any change
                document.querySelectorAll('input, select, textarea').forEach(el => {
                    el.addEventListener('change', updateJsonPreview);
                    el.addEventListener('input', updateJsonPreview);
                });

                // Keyboard shortcut
                document.addEventListener('keydown', (e) => {
                    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                        e.preventDefault();
                        save();
                    }
                });
            </script>
        </body>
        </html>`;
    }

    private parseExistingMappings(config: Record<string, unknown>): FieldMapping[] {
        const expr = config['jmespath_expression'] as string;
        if (!expr) return [];

        // Simple parser for { field: value, ... } expressions
        const mappings: FieldMapping[] = [];
        const match = expr.match(/^\{\s*(.+)\s*\}$/);
        if (!match) return [];

        const parts = match[1].split(/,\s*(?=[a-zA-Z_])/);
        for (const part of parts) {
            const [outputField, rest] = part.split(/:\s*/, 2);
            if (!outputField || !rest) continue;

            const mapping: FieldMapping = {
                outputField: outputField.trim(),
                sourceType: 'input',
                sourcePath: '',
            };

            // Check for default value (e.g., "max_tokens || `500`")
            const defaultMatch = rest.match(/(.+?)\s*\|\|\s*(.+)$/);
            const value = defaultMatch ? defaultMatch[1].trim() : rest.trim();
            if (defaultMatch) {
                // Strip backticks/quotes from the default value
                mapping.defaultValue = defaultMatch[2].trim().replace(/^[`"']|[`"']$/g, '');
            }

            // Determine source type
            if (value.startsWith('`') || value.startsWith('"') || /^\d+$/.test(value)) {
                mapping.sourceType = 'literal';
                mapping.literalValue = value.replace(/^[`"']|[`"']$/g, '');
            } else if (value.includes('(')) {
                mapping.sourceType = 'expression';
                mapping.expression = value;
            } else {
                mapping.sourceType = 'input';
                mapping.sourcePath = value;
            }

            mappings.push(mapping);
        }

        return mappings;
    }

    /**
     * Render INCOMING section - shows available data sources
     */
    private renderIncomingSection(dataSources: DataSource[]): string {
        const inputSource = dataSources.find(s => s.type === 'input');
        const upstreamSources = dataSources.filter(s => s.type === 'upstream');

        return `
            <div class="incoming-content">
                <p class="section-description">Data available to this stage from the pipeline and upstream stages.</p>

                ${inputSource && inputSource.fields.length > 0 ? `
                    <div class="data-source-group">
                        <div class="data-source-header">
                            <span class="source-icon">📥</span>
                            <span class="source-title">Pipeline Input</span>
                            <span class="field-count">${inputSource.fields.length} fields</span>
                        </div>
                        <div class="data-source-fields">
                            ${inputSource.fields.map(f => `
                                <div class="field-chip">
                                    <span class="field-name">${f.name}</span>
                                    <span class="field-type">${f.type}</span>
                                    ${f.required ? '<span class="field-required">required</span>' : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : `
                    <div class="no-data-hint">
                        <span class="hint-icon">💡</span>
                        <span>No pipeline input schema defined. Add <code>input_schema</code> to your pipeline to define available inputs.</span>
                    </div>
                `}

                ${upstreamSources.length > 0 ? upstreamSources.map(source => `
                    <div class="data-source-group upstream">
                        <div class="data-source-header">
                            <span class="source-icon">📦</span>
                            <span class="source-title">From: ${source.name}</span>
                            <span class="field-count">${source.fields.length} outputs</span>
                        </div>
                        <div class="data-source-fields">
                            ${source.fields.map(f => `
                                <div class="field-chip">
                                    <span class="field-name">${f.name}</span>
                                    <span class="field-type">${f.type}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('') : ''}

                ${!inputSource?.fields.length && upstreamSources.length === 0 ? `
                    <div class="no-data-hint">
                        <span class="hint-icon">⚠️</span>
                        <span>No data sources available. This stage has no inputs to work with.</span>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Render TRANSFORM section - dynamically generates form from input_schema JSON Schema
     */
    private renderTransformSection(
        inputSchema: JSONSchema | undefined,
        config: Record<string, unknown>,
        dataSources: DataSource[],
        existingMappings: FieldMapping[],
        componentDetail: ComponentDetail | null,
        providers: Provider[]
    ): string {
        const properties = inputSchema?.properties || {};
        const requiredFields = inputSchema?.required || [];
        const defs = inputSchema?.$defs || {};

        const propertyNames = Object.keys(properties);

        if (propertyNames.length === 0) {
            return `
                <div class="no-config-hint">
                    <span class="hint-icon">ℹ️</span>
                    <span>This component has no configurable options.</span>
                </div>
            `;
        }

        // Render AI configuration section if this is an LLM node
        const aiConfigHtml = componentDetail?.requires_llm
            ? this.renderAIConfigSection(componentDetail, providers, config)
            : '';

        // Render form fields from JSON Schema properties
        const fieldsHtml = propertyNames.map(fieldName => {
            const fieldSchema = properties[fieldName];
            const isRequired = requiredFields.includes(fieldName);
            const currentValue = config[fieldName];

            return this.renderSchemaField(fieldName, fieldSchema, isRequired, currentValue, dataSources, defs);
        }).join('');

        return `
            <div class="transform-content">
                <p class="section-description">Configure how this stage processes data.</p>
                ${aiConfigHtml}
                ${fieldsHtml}
            </div>
        `;
    }

    /**
     * Render AI configuration section for LLM nodes
     * Shows provider selection and model selection from available providers
     */
    private renderAIConfigSection(
        componentDetail: ComponentDetail,
        providers: Provider[],
        config: Record<string, unknown>
    ): string {
        const aiConfig = componentDetail.ai_config;
        const recommendedProviders = aiConfig?.recommended_providers || {};
        const defaultProvider = aiConfig?.default_provider || Object.keys(recommendedProviders)[0] || '';

        // Filter available providers to show recommended ones first
        const recommendedProviderNames = Object.keys(recommendedProviders);
        const availableProviders = providers.filter(p =>
            recommendedProviderNames.includes(p.name) || p.configured
        );

        const currentProvider = (config['provider'] as string) || defaultProvider;
        const currentModel = config['model'] as string || '';

        return `
            <div class="config-field ai-config-section">
                <div class="ai-config-header">
                    <span class="ai-icon">🤖</span>
                    <span class="ai-title">LLM Configuration</span>
                </div>

                <div class="ai-config-grid">
                    <div class="ai-field">
                        <label class="field-label">Provider</label>
                        <select name="provider" id="provider-select" onchange="updateModelOptions()">
                            ${availableProviders.map(p => `
                                <option value="${p.name}"
                                    ${currentProvider === p.name ? 'selected' : ''}
                                    data-models='${JSON.stringify(p.available_models)}'
                                    data-default-model="${p.default_model}"
                                    ${!p.configured ? 'class="not-configured"' : ''}>
                                    ${p.name}${recommendedProviderNames.includes(p.name) ? ' ⭐' : ''}
                                    ${!p.configured ? ' (not configured)' : ''}
                                </option>
                            `).join('')}
                        </select>
                        <p class="field-hint">⭐ = Recommended for this component</p>
                    </div>

                    <div class="ai-field">
                        <label class="field-label">Model</label>
                        <select name="model" id="model-select">
                            <!-- Populated by JavaScript based on provider selection -->
                        </select>
                        <p class="field-hint" id="model-hint"></p>
                    </div>
                </div>
            </div>

            <script>
                // Store provider data for model selection
                const providerData = ${JSON.stringify(providers.reduce((acc, p) => {
                    acc[p.name] = { models: p.available_models, defaultModel: p.default_model };
                    return acc;
                }, {} as Record<string, { models: string[]; defaultModel: string }>))};

                const recommendedModels = ${JSON.stringify(recommendedProviders)};

                function updateModelOptions() {
                    const providerSelect = document.getElementById('provider-select');
                    const modelSelect = document.getElementById('model-select');
                    const modelHint = document.getElementById('model-hint');
                    const provider = providerSelect.value;
                    const data = providerData[provider];

                    if (!data) return;

                    // Get recommended model for this provider if available
                    const recommended = recommendedModels[provider];
                    const recommendedModel = recommended?.model || data.defaultModel;

                    modelSelect.innerHTML = data.models.map(model =>
                        '<option value="' + model + '" ' +
                        (model === '${currentModel || ''}' || model === recommendedModel ? 'selected' : '') +
                        '>' + model +
                        (model === recommendedModel ? ' (recommended)' : '') +
                        '</option>'
                    ).join('');

                    // Show hint about recommended model
                    if (recommended) {
                        modelHint.textContent = 'Recommended: ' + recommendedModel;
                    } else {
                        modelHint.textContent = 'Default: ' + data.defaultModel;
                    }

                    updateJsonPreview();
                }

                // Initialize on load
                setTimeout(updateModelOptions, 0);
            </script>
        `;
    }

    /**
     * Render a form field from JSON Schema property
     */
    private renderSchemaField(
        fieldName: string,
        schema: JSONSchemaProperty,
        isRequired: boolean,
        currentValue: unknown,
        dataSources: DataSource[],
        defs: Record<string, JSONSchemaProperty>
    ): string {
        // Handle $ref to resolve definitions
        if (schema.$ref) {
            const refPath = schema.$ref.replace('#/$defs/', '');
            schema = { ...defs[refPath], ...schema, $ref: undefined };
        }

        const fieldType = schema.type || 'string';
        const description = schema.description || '';
        const defaultValue = schema.default;
        const label = this.formatFieldLabel(fieldName);

        // Determine the input type based on schema
        if (schema.enum) {
            return this.renderSchemaSelectField(fieldName, label, description, schema.enum, isRequired, currentValue, defaultValue);
        }

        switch (fieldType) {
            case 'boolean':
                return this.renderSchemaBooleanField(fieldName, label, description, isRequired, currentValue, defaultValue);
            case 'integer':
            case 'number':
                return this.renderSchemaNumberField(fieldName, label, description, isRequired, currentValue, schema);
            case 'array':
                return this.renderSchemaArrayField(fieldName, label, description, isRequired, currentValue, schema, dataSources);
            case 'object':
                return this.renderSchemaObjectField(fieldName, label, description, isRequired, currentValue);
            default:
                // For strings, check if it looks like a prompt field
                const isPromptField = fieldName.toLowerCase().includes('prompt') ||
                    description.toLowerCase().includes('prompt');
                if (isPromptField) {
                    return this.renderSchemaPromptField(fieldName, label, description, isRequired, currentValue, dataSources, schema);
                }
                return this.renderSchemaTextField(fieldName, label, description, isRequired, currentValue, schema);
        }
    }

    /**
     * Format field name to human-readable label
     */
    private formatFieldLabel(fieldName: string): string {
        return fieldName
            .replace(/_/g, ' ')
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    }

    /**
     * Render a select dropdown from enum values
     */
    private renderSchemaSelectField(
        name: string,
        label: string,
        description: string,
        options: string[],
        required: boolean,
        currentValue: unknown,
        defaultValue: unknown
    ): string {
        const value = currentValue ?? defaultValue ?? '';
        return `
            <div class="config-field">
                <div class="field-header">
                    <span class="field-label">${label}${required ? '<span class="required">*</span>' : ''}</span>
                </div>
                <p class="field-description">${this.escapeHtml(description)}</p>
                <select name="${name}">
                    <option value="">-- Select --</option>
                    ${options.map(opt => `<option value="${opt}" ${value === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                </select>
            </div>
        `;
    }

    /**
     * Render a boolean checkbox
     */
    private renderSchemaBooleanField(
        name: string,
        label: string,
        description: string,
        required: boolean,
        currentValue: unknown,
        defaultValue: unknown
    ): string {
        const checked = currentValue ?? defaultValue ?? false;
        return `
            <div class="config-field">
                <div class="field-header">
                    <span class="field-label">${label}</span>
                </div>
                <p class="field-description">${this.escapeHtml(description)}</p>
                <label class="checkbox-wrapper">
                    <input type="checkbox" name="${name}" ${checked ? 'checked' : ''}>
                    <span>Enable</span>
                </label>
            </div>
        `;
    }

    /**
     * Render a number input with constraints
     */
    private renderSchemaNumberField(
        name: string,
        label: string,
        description: string,
        required: boolean,
        currentValue: unknown,
        schema: JSONSchemaProperty
    ): string {
        const value = currentValue ?? schema.default ?? '';
        const min = schema.minimum;
        const max = schema.maximum;
        const step = schema.type === 'integer' ? 1 : 0.1;

        let constraints = '';
        if (min !== undefined && max !== undefined) {
            constraints = `Range: ${min} - ${max}`;
        } else if (min !== undefined) {
            constraints = `Min: ${min}`;
        } else if (max !== undefined) {
            constraints = `Max: ${max}`;
        }

        return `
            <div class="config-field">
                <div class="field-header">
                    <span class="field-label">${label}${required ? '<span class="required">*</span>' : ''}</span>
                </div>
                <p class="field-description">${this.escapeHtml(description)}</p>
                <input type="number" name="${name}" value="${value}"
                    ${min !== undefined ? `min="${min}"` : ''}
                    ${max !== undefined ? `max="${max}"` : ''}
                    step="${step}"
                    placeholder="${schema.default !== undefined ? `Default: ${schema.default}` : ''}">
                ${constraints ? `<p class="field-hint">${constraints}</p>` : ''}
            </div>
        `;
    }

    /**
     * Render a text input
     */
    private renderSchemaTextField(
        name: string,
        label: string,
        description: string,
        required: boolean,
        currentValue: unknown,
        schema: JSONSchemaProperty
    ): string {
        const rawValue = currentValue ?? '';
        // If value is an object, JSON.stringify it to prevent [object Object]
        const value = typeof rawValue === 'object' && rawValue !== null
            ? JSON.stringify(rawValue, null, 2)
            : String(rawValue);

        // Get placeholder from schema examples, default, or fallback
        const placeholder = this.getPlaceholderFromSchema(schema, label);

        return `
            <div class="config-field">
                <div class="field-header">
                    <span class="field-label">${label}${required ? '<span class="required">*</span>' : ''}</span>
                </div>
                <p class="field-description">${this.escapeHtml(description)}</p>
                <input type="text" name="${name}" value="${this.escapeHtml(value)}"
                    placeholder="${this.escapeHtml(placeholder)}">
            </div>
        `;
    }

    /**
     * Render a prompt/textarea field with variable insertion
     */
    private renderSchemaPromptField(
        name: string,
        label: string,
        description: string,
        required: boolean,
        currentValue: unknown,
        dataSources: DataSource[],
        schema: JSONSchemaProperty
    ): string {
        // If value is an object, JSON.stringify it to prevent [object Object]
        const rawValue = currentValue ?? '';
        const value = typeof rawValue === 'object' && rawValue !== null
            ? JSON.stringify(rawValue, null, 2)
            : String(rawValue);
        const inputSource = dataSources.find(s => s.type === 'input');

        // Get placeholder from schema examples, default, or fallback to generic
        const placeholder = this.getPlaceholderFromSchema(schema, label);

        return `
            <div class="config-field prompt-field">
                <div class="field-header">
                    <span class="field-label">${label}${required ? '<span class="required">*</span>' : ''}</span>
                </div>
                <p class="field-description">${this.escapeHtml(description)}</p>

                <div class="prompt-editor">
                    <textarea name="${name}" placeholder="${this.escapeHtml(placeholder)}">${this.escapeHtml(value)}</textarea>

                    <div class="variable-pills">
                        <span class="pills-label">Insert variable:</span>
                        ${inputSource?.fields.map(f => `
                            <button type="button" class="variable-pill" onclick="insertVariable('${name}', '{{input.${f.name}}}')">
                                ${f.name}
                            </button>
                        `).join('') || '<span class="no-vars">No input fields defined</span>'}
                        ${dataSources.filter(s => s.type === 'upstream').map(source => `
                            <button type="button" class="variable-pill upstream" onclick="insertVariable('${name}', '{{upstream.${source.id}.result}}')">
                                ${source.id}.result
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render an array field (multi-select or list)
     */
    private renderSchemaArrayField(
        name: string,
        label: string,
        description: string,
        required: boolean,
        currentValue: unknown,
        schema: JSONSchemaProperty,
        dataSources: DataSource[]
    ): string {
        const value = Array.isArray(currentValue) ? JSON.stringify(currentValue, null, 2) : '';
        return `
            <div class="config-field">
                <div class="field-header">
                    <span class="field-label">${label}${required ? '<span class="required">*</span>' : ''}</span>
                </div>
                <p class="field-description">${this.escapeHtml(description)}</p>
                <textarea name="${name}" data-type="json" placeholder='["item1", "item2"]'>${this.escapeHtml(value)}</textarea>
                <p class="field-hint">Enter as JSON array</p>
            </div>
        `;
    }

    /**
     * Render an object field (JSON editor)
     */
    private renderSchemaObjectField(
        name: string,
        label: string,
        description: string,
        required: boolean,
        currentValue: unknown
    ): string {
        const value = currentValue && typeof currentValue === 'object'
            ? JSON.stringify(currentValue, null, 2)
            : '';
        return `
            <div class="config-field">
                <div class="field-header">
                    <span class="field-label">${label}${required ? '<span class="required">*</span>' : ''}</span>
                </div>
                <p class="field-description">${this.escapeHtml(description)}</p>
                <textarea name="${name}" data-type="json" placeholder='{"key": "value"}'>${this.escapeHtml(value)}</textarea>
                <p class="field-hint">Enter as JSON object</p>
            </div>
        `;
    }

    /**
     * Render OUTGOING section - shows what this stage outputs from output_schema and destination config
     */
    private renderOutgoingSection(
        stage: PipelineStage,
        pipeline: PipelineFile,
        outputSchema: JSONSchema | undefined,
        existingMappings: FieldMapping[]
    ): string {
        // Extract output fields from output_schema
        const outputProperties = outputSchema?.properties || {};
        const outputFieldNames = Object.keys(outputProperties);

        // Get pipeline-level and stage-level destinations
        const pipelineDestinations = pipeline.output_config?.destinations || [];
        const stageDestinations = stage.output_config?.destinations || [];

        // For json_transform, outputs are determined by field mappings
        const isJsonTransform = stage.component_type === 'json_transform';

        const outputFieldsHtml = isJsonTransform
            ? this.renderJsonTransformOutputs(stage, existingMappings)
            : this.renderComponentOutputs(stage, outputFieldNames, outputProperties);

        const destinationsHtml = this.renderOutputDestinations(pipelineDestinations, stageDestinations);

        return `
            <div class="outgoing-content">
                <p class="section-description">Data and destinations for this stage's output.</p>

                ${outputFieldsHtml}

                ${destinationsHtml}

                <div class="downstream-hint">
                    <span class="hint-icon">💡</span>
                    <span>Downstream stages can access: <code>{{upstream.${this.escapeHtml(stage.id)}.result}}</code></span>
                </div>
            </div>
        `;
    }

    /**
     * Render output fields for json_transform component
     */
    private renderJsonTransformOutputs(stage: PipelineStage, existingMappings: FieldMapping[]): string {
        return `
            <div class="output-preview">
                <div class="output-header">
                    <span class="output-icon">📤</span>
                    <span class="output-title">${stage.id}.result</span>
                </div>
                <div class="output-fields" id="outputFieldsPreview">
                    ${existingMappings.length > 0 ? existingMappings.map(m => `
                        <div class="field-chip output">
                            <span class="field-name">${m.outputField}</span>
                            <span class="field-type">from mapping</span>
                        </div>
                    `).join('') : `
                        <div class="no-fields-hint">
                            Configure field mappings above to define outputs.
                        </div>
                    `}
                </div>
            </div>
        `;
    }

    /**
     * Render output fields from component's output_schema
     */
    private renderComponentOutputs(
        stage: PipelineStage,
        outputFieldNames: string[],
        outputProperties: Record<string, JSONSchemaProperty>
    ): string {
        if (outputFieldNames.length === 0) {
            return `
                <div class="no-data-hint">
                    <span class="hint-icon">ℹ️</span>
                    <span>This component does not produce structured output data.</span>
                </div>
            `;
        }

        return `
            <div class="output-preview">
                <div class="output-header">
                    <span class="output-icon">📤</span>
                    <span class="output-title">${this.escapeHtml(stage.id)} outputs</span>
                    <span class="field-count">${outputFieldNames.length} fields</span>
                </div>
                <div class="output-fields">
                    ${outputFieldNames.map(name => {
                        const prop = outputProperties[name];
                        return `
                            <div class="field-chip output">
                                <span class="field-name">${this.escapeHtml(name)}</span>
                                <span class="field-type">${prop.type || 'any'}</span>
                                ${prop.description ? `<span class="field-desc">${this.escapeHtml(prop.description)}</span>` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render output destinations configuration
     */
    private renderOutputDestinations(
        pipelineDestinations: OutputDestination[],
        stageDestinations: OutputDestination[]
    ): string {
        const destinationTypeIcons: Record<string, string> = {
            webhook: '🌐',
            email: '📧',
            database: '💾',
            message_queue: '📨'
        };

        const destinationTypeLabels: Record<string, string> = {
            webhook: 'Webhook',
            email: 'Email',
            database: 'Database',
            message_queue: 'Message Queue'
        };

        return `
            <div class="destinations-section">
                <div class="destinations-header">
                    <span class="destinations-icon">📡</span>
                    <span class="destinations-title">Output Destinations</span>
                </div>

                ${pipelineDestinations.length > 0 ? `
                    <div class="destinations-group">
                        <div class="destinations-group-header">
                            <span class="group-label">Pipeline Defaults (inherited)</span>
                        </div>
                        <div class="destinations-list">
                            ${pipelineDestinations.map((dest, i) => `
                                <div class="destination-item inherited">
                                    <span class="dest-icon">${destinationTypeIcons[dest.type] || '📤'}</span>
                                    <span class="dest-name">${this.escapeHtml(dest.name || dest.type)}</span>
                                    <span class="dest-type">${destinationTypeLabels[dest.type] || dest.type}</span>
                                    ${dest.on_success ? '<span class="dest-badge success">on success</span>' : ''}
                                    ${dest.on_error ? '<span class="dest-badge error">on error</span>' : ''}
                                    <label class="dest-toggle">
                                        <input type="checkbox"
                                               name="dest_inherited_${i}_enabled"
                                               ${dest.enabled !== false ? 'checked' : ''}>
                                        <span>Enabled</span>
                                    </label>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <div class="destinations-group">
                    <div class="destinations-group-header">
                        <span class="group-label">Stage-Specific Destinations</span>
                    </div>
                    <div class="destinations-list" id="stageDestinationsContainer">
                        ${stageDestinations.length > 0 ? stageDestinations.map((dest, i) => `
                            <div class="destination-item stage-specific" data-index="${i}">
                                <span class="dest-icon">${destinationTypeIcons[dest.type] || '📤'}</span>
                                <span class="dest-name">${this.escapeHtml(dest.name || 'New Destination')}</span>
                                <span class="dest-type">${destinationTypeLabels[dest.type] || dest.type}</span>
                                ${dest.on_success ? '<span class="dest-badge success">on success</span>' : ''}
                                ${dest.on_error ? '<span class="dest-badge error">on error</span>' : ''}
                                <button type="button" class="dest-edit-btn" onclick="editDestination(${i})">✏️</button>
                                <button type="button" class="dest-remove-btn" onclick="removeDestination(${i})">✕</button>
                            </div>
                        `).join('') : `
                            <div class="no-destinations-hint">
                                No stage-specific destinations configured.
                            </div>
                        `}
                    </div>
                    <div class="add-destination-container">
                        <button type="button" class="add-destination-btn" onclick="showAddDestinationMenu()">
                            + Add Destination
                        </button>
                        <div class="destination-type-menu" id="destinationTypeMenu" style="display: none;">
                            <button type="button" onclick="addDestination('webhook')">🌐 Webhook</button>
                            <button type="button" onclick="addDestination('email')">📧 Email</button>
                            <button type="button" onclick="addDestination('database')">💾 Database</button>
                            <button type="button" onclick="addDestination('message_queue')">📨 Message Queue</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    private getStyles(): string {
        return `
            * { box-sizing: border-box; margin: 0; padding: 0; }

            body {
                font-family: var(--vscode-font-family);
                font-size: 13px;
                color: var(--vscode-foreground);
                background: var(--vscode-editor-background);
                line-height: 1.5;
            }

            .container {
                max-width: 900px;
                margin: 0 auto;
                padding: 24px;
            }

            /* Header */
            .header {
                display: flex;
                gap: 16px;
                padding-bottom: 20px;
                border-bottom: 1px solid var(--vscode-panel-border);
                margin-bottom: 24px;
            }

            .header-icon {
                font-size: 36px;
                width: 56px;
                height: 56px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, var(--vscode-button-background), var(--vscode-button-hoverBackground));
                border-radius: 12px;
            }

            .header-content h1 {
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 4px;
            }

            .header-content .stage-id {
                font-family: var(--vscode-editor-font-family);
                color: var(--vscode-textLink-foreground);
                font-size: 14px;
            }

            .header-content .description {
                color: var(--vscode-descriptionForeground);
                margin-top: 8px;
            }

            .badge {
                display: inline-block;
                padding: 3px 10px;
                background: var(--vscode-badge-background);
                color: var(--vscode-badge-foreground);
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
                margin-top: 8px;
            }

            .badge-ai { background: #7c3aed; }
            .badge-transform { background: #2563eb; }
            .badge-integration { background: #059669; }
            .badge-control-flow { background: #d97706; }
            .badge-debug { background: #6b7280; }
            .badge-readonly { background: var(--vscode-badge-background); margin-left: auto; }

            /* Config Fields */
            .config-field {
                background: var(--vscode-input-background);
                border: 1px solid var(--vscode-input-border);
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
            }

            .field-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 6px;
            }

            .field-label {
                font-weight: 600;
                font-size: 14px;
            }

            .required {
                color: var(--vscode-errorForeground);
                margin-left: 4px;
            }

            .field-description {
                font-size: 12px;
                color: var(--vscode-descriptionForeground);
                margin-bottom: 12px;
            }

            /* Inputs */
            input[type="text"],
            input[type="number"],
            select,
            textarea {
                width: 100%;
                padding: 10px 12px;
                background: var(--vscode-editor-background);
                border: 1px solid var(--vscode-input-border);
                color: var(--vscode-input-foreground);
                border-radius: 6px;
                font-family: inherit;
                font-size: 13px;
            }

            input:focus, select:focus, textarea:focus {
                outline: none;
                border-color: var(--vscode-focusBorder);
                box-shadow: 0 0 0 1px var(--vscode-focusBorder);
            }

            textarea {
                min-height: 100px;
                resize: vertical;
                font-family: var(--vscode-editor-font-family);
            }

            select.source-select {
                padding-right: 30px;
            }

            /* Checkbox */
            .checkbox-wrapper {
                display: flex;
                align-items: center;
                gap: 10px;
                cursor: pointer;
            }

            .checkbox-wrapper input[type="checkbox"] {
                width: 18px;
                height: 18px;
            }

            /* Field Mapper */
            .field-mapper {
                background: var(--vscode-editor-background);
                border: 1px solid var(--vscode-input-border);
                border-radius: 6px;
                padding: 16px;
            }

            .mapper-header {
                display: grid;
                grid-template-columns: 1fr 30px 2fr 100px 30px;
                gap: 8px;
                padding-bottom: 8px;
                border-bottom: 1px solid var(--vscode-panel-border);
                margin-bottom: 12px;
                font-size: 11px;
                text-transform: uppercase;
                color: var(--vscode-descriptionForeground);
            }

            .mapping-row {
                display: grid;
                grid-template-columns: 1fr 30px 2fr 100px 30px;
                gap: 8px;
                align-items: end;
                margin-bottom: 12px;
                padding-bottom: 12px;
                border-bottom: 1px solid var(--vscode-panel-border);
            }

            .mapping-row:last-child {
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }

            .mapping-row label {
                display: block;
                font-size: 10px;
                color: var(--vscode-descriptionForeground);
                margin-bottom: 4px;
            }

            .mapping-row input,
            .mapping-row select {
                padding: 8px;
                font-size: 12px;
            }

            .mapping-arrow {
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                color: var(--vscode-descriptionForeground);
                padding-top: 20px;
            }

            .mapping-source {
                display: flex;
                flex-direction: column;
                gap: 6px;
            }

            .mapping-source select {
                margin-bottom: 4px;
            }

            .remove-btn {
                padding: 6px 10px;
                background: transparent;
                border: 1px solid var(--vscode-input-border);
                border-radius: 4px;
                color: var(--vscode-errorForeground);
                cursor: pointer;
                margin-top: 20px;
            }

            .remove-btn:hover {
                background: var(--vscode-errorForeground);
                color: white;
            }

            .add-mapping-btn {
                margin-top: 12px;
                padding: 8px 16px;
                background: var(--vscode-button-secondaryBackground);
                border: none;
                border-radius: 6px;
                color: var(--vscode-button-secondaryForeground);
                cursor: pointer;
                font-size: 12px;
            }

            .add-mapping-btn:hover {
                background: var(--vscode-button-secondaryHoverBackground);
            }

            .generated-expression {
                margin-top: 16px;
                padding: 12px;
                background: var(--vscode-textBlockQuote-background);
                border-left: 3px solid var(--vscode-textLink-foreground);
                border-radius: 0 6px 6px 0;
            }

            .generated-expression label {
                font-size: 11px;
                color: var(--vscode-descriptionForeground);
                display: block;
                margin-bottom: 6px;
            }

            .generated-expression code {
                font-family: var(--vscode-editor-font-family);
                font-size: 12px;
                color: var(--vscode-textLink-foreground);
            }

            /* Prompt Field */
            .prompt-editor {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .prompt-editor textarea {
                min-height: 120px;
            }

            .variable-pills {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                align-items: center;
            }

            .pills-label {
                font-size: 11px;
                color: var(--vscode-descriptionForeground);
            }

            .variable-pill {
                padding: 4px 12px;
                background: var(--vscode-badge-background);
                color: var(--vscode-badge-foreground);
                border: none;
                border-radius: 12px;
                font-size: 11px;
                cursor: pointer;
                transition: all 0.15s;
            }

            .variable-pill:hover {
                background: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
            }

            .variable-pill.upstream {
                background: var(--vscode-button-secondaryBackground);
            }

            .no-vars {
                font-size: 11px;
                color: var(--vscode-descriptionForeground);
                font-style: italic;
            }

            /* JSON Section */
            .json-section {
                margin-top: 24px;
            }

            .section-header {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px;
                background: var(--vscode-sideBar-background);
                border-radius: 6px;
            }

            .section-header.clickable {
                cursor: pointer;
            }

            .section-header.clickable:hover {
                background: var(--vscode-list-hoverBackground);
            }

            .section-header h2 {
                font-size: 13px;
                font-weight: 600;
            }

            .section-icon {
                font-size: 12px;
                color: var(--vscode-descriptionForeground);
            }

            .json-view {
                margin-top: 12px;
                position: relative;
            }

            .json-view.collapsed {
                display: none;
            }

            .json-view pre {
                padding: 16px;
                background: var(--vscode-editor-background);
                border: 1px solid var(--vscode-input-border);
                border-radius: 6px;
                font-family: var(--vscode-editor-font-family);
                font-size: 12px;
                overflow-x: auto;
                white-space: pre-wrap;
            }

            .copy-btn {
                position: absolute;
                top: 8px;
                right: 8px;
                padding: 4px 12px;
                background: var(--vscode-button-secondaryBackground);
                border: none;
                border-radius: 4px;
                font-size: 11px;
                cursor: pointer;
                color: var(--vscode-button-secondaryForeground);
            }

            .copy-btn:hover {
                background: var(--vscode-button-secondaryHoverBackground);
            }

            /* AI Config Section */
            .ai-config-section {
                background: linear-gradient(135deg, rgba(124, 58, 237, 0.08), rgba(139, 92, 246, 0.04));
                border: 2px solid rgba(124, 58, 237, 0.3);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }

            .ai-config-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid rgba(124, 58, 237, 0.2);
            }

            .ai-icon {
                font-size: 20px;
            }

            .ai-title {
                font-weight: 600;
                font-size: 14px;
                color: var(--vscode-foreground);
            }

            .ai-config-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
            }

            @media (max-width: 600px) {
                .ai-config-grid {
                    grid-template-columns: 1fr;
                }
            }

            .ai-field {
                display: flex;
                flex-direction: column;
                gap: 6px;
            }

            .ai-field select {
                background: var(--vscode-editor-background);
            }

            .ai-field option.not-configured {
                color: var(--vscode-descriptionForeground);
                font-style: italic;
            }

            /* Field Hints */
            .field-hint {
                font-size: 11px;
                color: var(--vscode-descriptionForeground);
                margin-top: 6px;
                font-style: italic;
            }

            /* Flow Sections - Enhanced with contrasting borders */
            .flow-section {
                margin-bottom: 20px;
                border: 2px solid var(--vscode-panel-border);
                border-radius: 12px;
                overflow: hidden;
                transition: border-color 0.2s ease, box-shadow 0.2s ease;
            }

            .flow-section:hover {
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
            }

            /* Incoming section - Green accent */
            .flow-section:has(.section-badge.incoming) {
                border-color: #10b981;
                border-left-width: 4px;
            }

            /* Transform section - Blue accent */
            .flow-section:has(.section-badge.transform) {
                border-color: #3b82f6;
                border-left-width: 4px;
            }

            /* Outgoing section - Purple accent */
            .flow-section:has(.section-badge.outgoing) {
                border-color: #8b5cf6;
                border-left-width: 4px;
            }

            /* JSON section - Neutral */
            .flow-section:has(.section-badge.json) {
                border-color: var(--vscode-panel-border);
            }

            /* Fallback for browsers without :has() support */
            .flow-section.incoming-section {
                border-color: #10b981;
                border-left-width: 4px;
            }

            .flow-section.transform-section {
                border-color: #3b82f6;
                border-left-width: 4px;
            }

            .flow-section.outgoing-section {
                border-color: #8b5cf6;
                border-left-width: 4px;
            }

            .flow-section .section-header {
                border-radius: 0;
            }

            .section-badge {
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
                white-space: nowrap;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            }

            .section-badge.incoming {
                background: linear-gradient(135deg, #059669, #10b981);
                color: white;
            }

            .section-badge.transform {
                background: linear-gradient(135deg, #2563eb, #3b82f6);
                color: white;
            }

            .section-badge.outgoing {
                background: linear-gradient(135deg, #7c3aed, #8b5cf6);
                color: white;
            }

            .section-badge.json {
                background: var(--vscode-badge-background);
                color: var(--vscode-badge-foreground);
                font-family: var(--vscode-editor-font-family);
            }

            .section-content {
                padding: 16px;
                background: var(--vscode-editor-background);
            }

            .section-content.collapsed {
                display: none;
            }

            .section-description {
                font-size: 12px;
                color: var(--vscode-descriptionForeground);
                margin-bottom: 16px;
            }

            /* Data Source Groups */
            .data-source-group {
                background: var(--vscode-input-background);
                border: 1px solid var(--vscode-input-border);
                border-radius: 8px;
                margin-bottom: 12px;
                overflow: hidden;
            }

            .data-source-group.upstream {
                border-left: 3px solid var(--vscode-textLink-foreground);
            }

            .data-source-header {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 16px;
                background: var(--vscode-sideBar-background);
                border-bottom: 1px solid var(--vscode-panel-border);
            }

            .source-icon {
                font-size: 16px;
            }

            .source-title {
                font-weight: 600;
                font-size: 13px;
            }

            .field-count {
                margin-left: auto;
                font-size: 11px;
                color: var(--vscode-descriptionForeground);
                background: var(--vscode-badge-background);
                padding: 2px 8px;
                border-radius: 10px;
            }

            .data-source-fields {
                padding: 12px 16px;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }

            /* Field Chips */
            .field-chip {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 12px;
                background: var(--vscode-editor-background);
                border: 1px solid var(--vscode-input-border);
                border-radius: 16px;
                font-size: 12px;
            }

            .field-chip.output {
                border-color: var(--vscode-textLink-foreground);
                background: rgba(124, 58, 237, 0.1);
            }

            .field-name {
                font-family: var(--vscode-editor-font-family);
                font-weight: 500;
                color: var(--vscode-foreground);
            }

            .field-type {
                font-size: 10px;
                color: var(--vscode-descriptionForeground);
                padding: 2px 6px;
                background: var(--vscode-badge-background);
                border-radius: 8px;
            }

            .field-required {
                font-size: 9px;
                color: white;
                background: var(--vscode-errorForeground);
                padding: 2px 6px;
                border-radius: 8px;
            }

            .field-desc {
                font-size: 10px;
                color: var(--vscode-descriptionForeground);
                font-style: italic;
            }

            /* Output Preview */
            .output-preview {
                background: var(--vscode-input-background);
                border: 1px solid var(--vscode-input-border);
                border-radius: 8px;
                overflow: hidden;
                margin-bottom: 12px;
            }

            .output-header {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 12px 16px;
                background: var(--vscode-sideBar-background);
                border-bottom: 1px solid var(--vscode-panel-border);
            }

            .output-icon {
                font-size: 16px;
            }

            .output-title {
                font-weight: 600;
                font-size: 13px;
                font-family: var(--vscode-editor-font-family);
            }

            .output-fields {
                padding: 12px 16px;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }

            .no-fields-hint {
                font-size: 12px;
                color: var(--vscode-descriptionForeground);
                font-style: italic;
            }

            /* Destinations Section */
            .destinations-section {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid var(--vscode-panel-border);
            }

            .destinations-header {
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 16px;
            }

            .destinations-icon {
                font-size: 18px;
            }

            .destinations-title {
                font-weight: 600;
                font-size: 14px;
            }

            .destinations-group {
                background: var(--vscode-input-background);
                border: 1px solid var(--vscode-input-border);
                border-radius: 8px;
                margin-bottom: 12px;
                overflow: hidden;
            }

            .destinations-group-header {
                padding: 10px 16px;
                background: var(--vscode-sideBar-background);
                border-bottom: 1px solid var(--vscode-panel-border);
            }

            .group-label {
                font-size: 11px;
                text-transform: uppercase;
                color: var(--vscode-descriptionForeground);
                font-weight: 600;
            }

            .destinations-list {
                padding: 12px 16px;
            }

            .destination-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 10px 12px;
                background: var(--vscode-editor-background);
                border: 1px solid var(--vscode-input-border);
                border-radius: 8px;
                margin-bottom: 8px;
            }

            .destination-item:last-child {
                margin-bottom: 0;
            }

            .destination-item.inherited {
                border-left: 3px solid #10b981;
            }

            .destination-item.stage-specific {
                border-left: 3px solid #8b5cf6;
            }

            .dest-icon {
                font-size: 16px;
            }

            .dest-name {
                font-weight: 500;
                flex: 1;
            }

            .dest-type {
                font-size: 10px;
                color: var(--vscode-descriptionForeground);
                background: var(--vscode-badge-background);
                padding: 2px 8px;
                border-radius: 8px;
            }

            .dest-badge {
                font-size: 9px;
                padding: 2px 6px;
                border-radius: 8px;
                font-weight: 500;
            }

            .dest-badge.success {
                background: #10b981;
                color: white;
            }

            .dest-badge.error {
                background: var(--vscode-errorForeground);
                color: white;
            }

            .dest-toggle {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 11px;
                color: var(--vscode-descriptionForeground);
                cursor: pointer;
            }

            .dest-toggle input {
                width: 14px;
                height: 14px;
            }

            .dest-edit-btn,
            .dest-remove-btn {
                padding: 4px 8px;
                background: transparent;
                border: 1px solid var(--vscode-input-border);
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
            }

            .dest-edit-btn:hover {
                background: var(--vscode-button-secondaryBackground);
            }

            .dest-remove-btn:hover {
                background: var(--vscode-errorForeground);
                color: white;
                border-color: var(--vscode-errorForeground);
            }

            .no-destinations-hint {
                font-size: 12px;
                color: var(--vscode-descriptionForeground);
                font-style: italic;
                padding: 8px 0;
            }

            .add-destination-container {
                padding: 12px 16px;
                border-top: 1px solid var(--vscode-panel-border);
                position: relative;
            }

            .add-destination-btn {
                padding: 8px 16px;
                background: var(--vscode-button-secondaryBackground);
                border: 1px dashed var(--vscode-input-border);
                border-radius: 6px;
                color: var(--vscode-button-secondaryForeground);
                cursor: pointer;
                font-size: 12px;
                width: 100%;
            }

            .add-destination-btn:hover {
                background: var(--vscode-button-secondaryHoverBackground);
                border-style: solid;
            }

            .destination-type-menu {
                position: absolute;
                bottom: 100%;
                left: 16px;
                right: 16px;
                background: var(--vscode-menu-background);
                border: 1px solid var(--vscode-menu-border);
                border-radius: 6px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                overflow: hidden;
                margin-bottom: 4px;
            }

            .destination-type-menu button {
                display: block;
                width: 100%;
                padding: 10px 16px;
                background: transparent;
                border: none;
                text-align: left;
                cursor: pointer;
                font-size: 13px;
                color: var(--vscode-menu-foreground);
            }

            .destination-type-menu button:hover {
                background: var(--vscode-menu-selectionBackground);
                color: var(--vscode-menu-selectionForeground);
            }

            /* Hints */
            .no-data-hint,
            .no-config-hint,
            .downstream-hint {
                display: flex;
                align-items: flex-start;
                gap: 10px;
                padding: 12px 16px;
                background: var(--vscode-textBlockQuote-background);
                border-radius: 8px;
                font-size: 12px;
            }

            .downstream-hint {
                margin-top: 12px;
                border-left: 3px solid var(--vscode-textLink-foreground);
            }

            .hint-icon {
                font-size: 16px;
                flex-shrink: 0;
            }

            .no-data-hint code,
            .downstream-hint code {
                font-family: var(--vscode-editor-font-family);
                background: var(--vscode-badge-background);
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 11px;
            }

            /* Actions */
            .actions {
                display: flex;
                gap: 12px;
                padding-top: 24px;
                border-top: 1px solid var(--vscode-panel-border);
                margin-top: 24px;
                position: sticky;
                bottom: 0;
                background: var(--vscode-editor-background);
                padding-bottom: 24px;
            }

            button {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            button.primary {
                background: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
            }

            button.primary:hover {
                background: var(--vscode-button-hoverBackground);
            }

            button.secondary {
                background: var(--vscode-button-secondaryBackground);
                color: var(--vscode-button-secondaryForeground);
            }

            button.secondary:hover {
                background: var(--vscode-button-secondaryHoverBackground);
            }
        `;
    }

    /**
     * Get placeholder text from schema examples, default, or fallback to label
     */
    private getPlaceholderFromSchema(schema: JSONSchemaProperty, label: string): string {
        // Try examples first
        if (schema.examples && schema.examples.length > 0) {
            const example = schema.examples[0];
            if (typeof example === 'object' && example !== null) {
                return `e.g. ${JSON.stringify(example)}`;
            }
            return `e.g. ${String(example)}`;
        }

        // Try default value
        if (schema.default !== undefined && schema.default !== null) {
            if (typeof schema.default === 'object') {
                return `Default: ${JSON.stringify(schema.default)}`;
            }
            return `Default: ${String(schema.default)}`;
        }

        // Fallback to generic placeholder
        return `Enter ${label.toLowerCase()}...`;
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
