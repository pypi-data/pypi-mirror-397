/**
 * Schema Field Component
 *
 * Dynamically renders form fields based on JSON Schema properties.
 */

import React from 'react';
import {
    TextField,
    NumberField,
    SelectField,
    CheckboxField,
    TextareaField,
    PromptField,
    JsonField,
} from './FormField';
import type { JSONSchemaProperty, DataSource } from '../types';

interface SchemaFieldProps {
    name: string;
    schema: JSONSchemaProperty;
    value: unknown;
    onChange: (value: unknown) => void;
    required?: boolean;
    dataSources: DataSource[];
    defs?: Record<string, JSONSchemaProperty>;
}

export function SchemaField({
    name,
    schema,
    value,
    onChange,
    required = false,
    dataSources,
    defs = {},
}: SchemaFieldProps) {
    // Handle $ref to resolve definitions
    let resolvedSchema = schema;
    if (schema.$ref) {
        const refPath = schema.$ref.replace('#/$defs/', '');
        resolvedSchema = { ...defs[refPath], ...schema, $ref: undefined };
    }

    const fieldType = resolvedSchema.type || 'string';
    const description = resolvedSchema.description || '';
    const defaultValue = resolvedSchema.default;
    const label = formatFieldLabel(name);

    // Enum field - dropdown
    if (resolvedSchema.enum && resolvedSchema.enum.length > 0) {
        return (
            <SelectField
                name={name}
                label={label}
                description={description}
                required={required}
                value={String(value ?? defaultValue ?? '')}
                onChange={(v) => onChange(v || undefined)}
                options={resolvedSchema.enum.map((opt) => ({ value: opt, label: opt }))}
            />
        );
    }

    // Boolean field
    if (fieldType === 'boolean') {
        return (
            <CheckboxField
                name={name}
                label={label}
                description={description}
                checked={Boolean(value ?? defaultValue ?? false)}
                onChange={(checked) => onChange(checked)}
            />
        );
    }

    // Number/integer field
    if (fieldType === 'number' || fieldType === 'integer') {
        return (
            <NumberField
                name={name}
                label={label}
                description={description}
                required={required}
                value={value !== undefined && value !== null ? Number(value) : ''}
                onChange={(v) => onChange(v)}
                min={resolvedSchema.minimum}
                max={resolvedSchema.maximum}
                step={fieldType === 'integer' ? 1 : 0.1}
            />
        );
    }

    // Array field
    if (fieldType === 'array') {
        return (
            <JsonField
                name={name}
                label={label}
                description={description}
                required={required}
                value={value ?? defaultValue ?? []}
                onChange={(v) => onChange(v)}
                placeholder='["item1", "item2"]'
            />
        );
    }

    // Object field
    if (fieldType === 'object') {
        return (
            <JsonField
                name={name}
                label={label}
                description={description}
                required={required}
                value={value ?? defaultValue ?? {}}
                onChange={(v) => onChange(v)}
                placeholder='{"key": "value"}'
            />
        );
    }

    // Check if it's a prompt field
    const isPromptField = name.toLowerCase().includes('prompt') ||
        description.toLowerCase().includes('prompt');

    if (isPromptField) {
        return (
            <PromptField
                name={name}
                label={label}
                description={description}
                required={required}
                value={String(value ?? defaultValue ?? '')}
                onChange={(v) => onChange(v || undefined)}
                dataSources={dataSources}
                placeholder={getPlaceholder(resolvedSchema, label)}
            />
        );
    }

    // Check if value is long or multiline - use textarea
    const stringValue = String(value ?? defaultValue ?? '');
    if (stringValue.length > 50 || stringValue.includes('\n')) {
        return (
            <TextareaField
                name={name}
                label={label}
                description={description}
                required={required}
                value={stringValue}
                onChange={(v) => onChange(v || undefined)}
                placeholder={getPlaceholder(resolvedSchema, label)}
            />
        );
    }

    // Default: text field
    return (
        <TextField
            name={name}
            label={label}
            description={description}
            required={required}
            value={stringValue}
            onChange={(v) => onChange(v || undefined)}
            placeholder={getPlaceholder(resolvedSchema, label)}
        />
    );
}

/**
 * Format field name to human-readable label
 */
function formatFieldLabel(fieldName: string): string {
    return fieldName
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, (str) => str.toUpperCase())
        .trim();
}

/**
 * Get placeholder text from schema
 */
function getPlaceholder(schema: JSONSchemaProperty, label: string): string {
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
