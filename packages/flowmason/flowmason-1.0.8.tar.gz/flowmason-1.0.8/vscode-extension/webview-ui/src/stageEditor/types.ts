/**
 * Stage Editor Types
 *
 * Shared types for the React-based stage configuration editor.
 */

export interface JSONSchemaProperty {
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

export interface JSONSchema {
    type?: string;
    properties?: Record<string, JSONSchemaProperty>;
    required?: string[];
    $defs?: Record<string, JSONSchemaProperty>;
}

export interface FieldInfo {
    name: string;
    type: string;
    description?: string;
    required?: boolean;
    default?: unknown;
    enum?: string[];
}

export interface DataSource {
    id: string;
    name: string;
    type: 'input' | 'upstream';
    fields: FieldInfo[];
}

export interface FieldMapping {
    outputField: string;
    sourceType: 'input' | 'upstream' | 'expression' | 'literal';
    sourcePath?: string;
    expression?: string;
    literalValue?: string;
    defaultValue?: string;
}

export interface OutputDestination {
    id: string;
    type: 'webhook' | 'email' | 'database' | 'message_queue';
    name?: string;
    enabled?: boolean;
    on_success?: boolean;
    on_error?: boolean;
    config: Record<string, unknown>;
}

export interface OutputConfig {
    destinations: OutputDestination[];
}

export interface PipelineStage {
    id: string;
    component_type: string;
    config?: Record<string, unknown>;
    depends_on?: string[];
    output_config?: OutputConfig;
}

export interface AIConfig {
    recommended_providers?: Record<string, { model?: string }>;
    default_provider?: string;
}

export interface ComponentDetail {
    name: string;
    component_type: string;
    category?: string;
    description?: string;
    icon?: string;
    requires_llm?: boolean;
    input_schema?: JSONSchema;
    output_schema?: JSONSchema;
    ai_config?: AIConfig;
}

export interface Provider {
    name: string;
    configured: boolean;
    available_models: string[];
    default_model: string;
}

export interface StageEditorProps {
    stage: PipelineStage;
    componentDetail: ComponentDetail | null;
    dataSources: DataSource[];
    providers: Provider[];
    onSave: (config: Record<string, unknown>, outputConfig?: OutputConfig | null) => void;
    onCancel: () => void;
}

// Message types for VSCode communication
export type WebviewMessage =
    | { type: 'save'; config: Record<string, unknown>; output_config?: OutputConfig | null }
    | { type: 'cancel' }
    | { type: 'ready' };

export type ExtensionMessage =
    | { type: 'init'; data: StageEditorInitData }
    | { type: 'update'; data: Partial<StageEditorInitData> };

export interface StageEditorInitData {
    stage: PipelineStage;
    componentDetail: ComponentDetail | null;
    dataSources: DataSource[];
    providers: Provider[];
    existingMappings: FieldMapping[];
}
