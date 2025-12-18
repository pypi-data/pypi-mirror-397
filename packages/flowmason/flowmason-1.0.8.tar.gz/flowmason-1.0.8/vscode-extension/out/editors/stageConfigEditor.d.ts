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
import { FlowMasonService } from '../services/flowmasonService';
import { PipelineStage } from '../views/pipelineStagesTree';
export declare class StageConfigEditor {
    private readonly extensionUri;
    private readonly flowmasonService;
    private static panels;
    constructor(extensionUri: vscode.Uri, flowmasonService: FlowMasonService);
    openEditor(stage: PipelineStage, document: vscode.TextDocument): Promise<void>;
    private getDataSources;
    private isDownstream;
    private saveConfig;
    private getHtml;
    private parseExistingMappings;
    /**
     * Render INCOMING section - shows available data sources
     */
    private renderIncomingSection;
    /**
     * Render TRANSFORM section - dynamically generates form from input_schema JSON Schema
     */
    private renderTransformSection;
    /**
     * Render AI configuration section for LLM nodes
     * Shows provider selection and model selection from available providers
     */
    private renderAIConfigSection;
    /**
     * Render a form field from JSON Schema property
     */
    private renderSchemaField;
    /**
     * Format field name to human-readable label
     */
    private formatFieldLabel;
    /**
     * Render a select dropdown from enum values
     */
    private renderSchemaSelectField;
    /**
     * Render a boolean checkbox
     */
    private renderSchemaBooleanField;
    /**
     * Render a number input with constraints
     */
    private renderSchemaNumberField;
    /**
     * Render a text input
     */
    private renderSchemaTextField;
    /**
     * Render a prompt/textarea field with variable insertion
     */
    private renderSchemaPromptField;
    /**
     * Render an array field (multi-select or list)
     */
    private renderSchemaArrayField;
    /**
     * Render an object field (JSON editor)
     */
    private renderSchemaObjectField;
    /**
     * Render OUTGOING section - shows what this stage outputs from output_schema and destination config
     */
    private renderOutgoingSection;
    /**
     * Render output fields for json_transform component
     */
    private renderJsonTransformOutputs;
    /**
     * Render output fields from component's output_schema
     */
    private renderComponentOutputs;
    /**
     * Render output destinations configuration
     */
    private renderOutputDestinations;
    private getStyles;
    /**
     * Get placeholder text from schema examples, default, or fallback to label
     */
    private getPlaceholderFromSchema;
    private escapeHtml;
}
//# sourceMappingURL=stageConfigEditor.d.ts.map