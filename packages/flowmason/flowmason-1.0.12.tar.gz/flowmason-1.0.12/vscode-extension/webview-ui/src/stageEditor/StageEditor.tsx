/**
 * Stage Editor Component
 *
 * Main React component for the visual stage configuration editor.
 * Renders a Salesforce Flow-style interface for configuring pipeline stages.
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Section, DataSourceList, AIConfig, SchemaField } from './components';
import type {
    PipelineStage,
    ComponentDetail,
    DataSource,
    Provider,
    OutputConfig,
    JSONSchema,
} from './types';

interface StageEditorProps {
    stage: PipelineStage;
    componentDetail: ComponentDetail | null;
    dataSources: DataSource[];
    providers: Provider[];
    onSave: (config: Record<string, unknown>, outputConfig?: OutputConfig | null) => void;
    onCancel: () => void;
}

const CATEGORY_ICONS: Record<string, string> = {
    'core': '⚙️',
    'ai': '✨',
    'transform': '🔄',
    'integration': '🌐',
    'control-flow': '🔀',
    'debug': '📝',
    'general': '📦',
};

function getComponentIcon(component?: ComponentDetail | null): string {
    if (!component) return '📦';
    if (component.icon) return component.icon;
    if (component.requires_llm) return '✨';
    return CATEGORY_ICONS[component.category?.toLowerCase() || 'general'] || '📦';
}

export function StageEditor({
    stage,
    componentDetail,
    dataSources,
    providers,
    onSave,
    onCancel,
}: StageEditorProps) {
    // Initialize config state from stage
    const [config, setConfig] = useState<Record<string, unknown>>(() => stage.config || {});
    const [outputConfig, setOutputConfig] = useState<OutputConfig | null>(
        () => stage.output_config || null
    );

    // Sync config when stage changes
    useEffect(() => {
        setConfig(stage.config || {});
        setOutputConfig(stage.output_config || null);
    }, [stage]);

    // Component metadata
    const icon = getComponentIcon(componentDetail);
    const name = componentDetail?.name || stage.component_type;
    const category = componentDetail?.category || 'custom';
    const description = componentDetail?.description || '';

    // Extract schemas
    const inputSchema = componentDetail?.input_schema as JSONSchema | undefined;
    const outputSchema = componentDetail?.output_schema as JSONSchema | undefined;
    const defs = inputSchema?.$defs || {};

    // Get field names from schema
    const fieldNames = useMemo(() => {
        return Object.keys(inputSchema?.properties || {});
    }, [inputSchema]);

    const requiredFields = inputSchema?.required || [];

    // Update a config value
    const updateConfig = useCallback((field: string, value: unknown) => {
        setConfig((prev) => {
            const newConfig = { ...prev };
            if (value === undefined || value === null || value === '') {
                delete newConfig[field];
            } else {
                newConfig[field] = value;
            }
            return newConfig;
        });
    }, []);

    // Handle save
    const handleSave = useCallback(() => {
        onSave(config, outputConfig);
    }, [config, outputConfig, onSave]);

    // Handle keyboard shortcut
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                handleSave();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [handleSave]);

    // Generate JSON preview
    const jsonPreview = useMemo(() => {
        return JSON.stringify(config, null, 2);
    }, [config]);

    // Copy JSON to clipboard
    const copyJson = useCallback(() => {
        navigator.clipboard.writeText(jsonPreview);
    }, [jsonPreview]);

    return (
        <div className="stage-editor">
            {/* Header */}
            <div className="stage-editor__header">
                <div className="stage-editor__icon">{icon}</div>
                <div>
                    <h1 className="stage-editor__title">{name}</h1>
                    <div className="stage-editor__stage-id">{stage.id}</div>
                    {description && <p className="stage-editor__description">{description}</p>}
                    <span className={`badge badge--${category.toLowerCase().replace(' ', '-')}`}>
                        {category}
                    </span>
                </div>
            </div>

            {/* Incoming Data Section */}
            <Section
                id="incoming"
                title="Input Data"
                badge="INCOMING"
                badgeIcon="📥"
                variant="incoming"
                description="Data available to this stage from the pipeline and upstream stages."
            >
                <DataSourceList dataSources={dataSources} />
            </Section>

            {/* Transform Section */}
            <Section
                id="transform"
                title="Processing Logic"
                badge="TRANSFORM"
                badgeIcon="⚙️"
                variant="transform"
                description="Configure how this stage processes data."
            >
                {/* AI Config for LLM nodes */}
                {componentDetail?.requires_llm && providers.length > 0 && (
                    <AIConfig
                        componentDetail={componentDetail}
                        providers={providers}
                        provider={String(config['provider'] || '')}
                        model={String(config['model'] || '')}
                        onProviderChange={(v) => updateConfig('provider', v)}
                        onModelChange={(v) => updateConfig('model', v)}
                    />
                )}

                {/* Dynamic fields from schema */}
                {fieldNames.length > 0 ? (
                    fieldNames.map((fieldName) => {
                        const fieldSchema = inputSchema?.properties?.[fieldName];
                        if (!fieldSchema) return null;

                        // Skip provider/model if already shown in AI config
                        if (componentDetail?.requires_llm && (fieldName === 'provider' || fieldName === 'model')) {
                            return null;
                        }

                        return (
                            <SchemaField
                                key={fieldName}
                                name={fieldName}
                                schema={fieldSchema}
                                value={config[fieldName]}
                                onChange={(v) => updateConfig(fieldName, v)}
                                required={requiredFields.includes(fieldName)}
                                dataSources={dataSources}
                                defs={defs}
                            />
                        );
                    })
                ) : (
                    <div className="hint">
                        <span className="hint__icon">ℹ️</span>
                        <span>This component has no configurable options.</span>
                    </div>
                )}
            </Section>

            {/* Outgoing Data Section */}
            <Section
                id="outgoing"
                title="Output Data"
                badge="OUTGOING"
                badgeIcon="📤"
                variant="outgoing"
                description="Data and destinations for this stage's output."
            >
                {/* Output schema fields */}
                {outputSchema?.properties && Object.keys(outputSchema.properties).length > 0 ? (
                    <div className="data-source">
                        <div className="data-source__header">
                            <span className="data-source__icon">📤</span>
                            <span className="data-source__title">{stage.id} outputs</span>
                            <span className="data-source__count">
                                {Object.keys(outputSchema.properties).length} fields
                            </span>
                        </div>
                        <div className="data-source__fields">
                            {Object.entries(outputSchema.properties).map(([fieldName, fieldSchema]) => (
                                <div key={fieldName} className="field-chip field-chip--output">
                                    <span className="field-chip__name">{fieldName}</span>
                                    <span className="field-chip__type">{fieldSchema.type || 'any'}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="hint">
                        <span className="hint__icon">ℹ️</span>
                        <span>This component produces a single result output.</span>
                    </div>
                )}

                {/* Downstream hint */}
                <div className="hint hint--info" style={{ marginTop: '12px' }}>
                    <span className="hint__icon">💡</span>
                    <span>
                        Downstream stages can access: <code>{`{{upstream.${stage.id}.result}}`}</code>
                    </span>
                </div>
            </Section>

            {/* Generated JSON Section */}
            <Section
                id="json"
                title="Generated JSON"
                badge="{ }"
                badgeIcon=""
                variant="json"
                defaultCollapsed={true}
                headerExtra={<span className="badge">Read-Only</span>}
            >
                <div className="json-preview">
                    <pre className="json-preview__code">{jsonPreview}</pre>
                    <button type="button" className="json-preview__copy" onClick={copyJson}>
                        📋 Copy
                    </button>
                </div>
            </Section>

            {/* Actions */}
            <div className="actions">
                <button type="button" className="btn btn--primary" onClick={handleSave}>
                    💾 Save Configuration
                </button>
                <button type="button" className="btn btn--secondary" onClick={onCancel}>
                    Cancel
                </button>
            </div>
        </div>
    );
}
