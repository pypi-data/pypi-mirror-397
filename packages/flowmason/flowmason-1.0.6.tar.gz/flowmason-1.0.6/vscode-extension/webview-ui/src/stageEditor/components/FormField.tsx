/**
 * Form Field Components
 *
 * Reusable form field components for the stage editor.
 */

import React, { useRef, useCallback } from 'react';
import type { JSONSchemaProperty, DataSource } from '../types';

interface FormFieldProps {
    name: string;
    label: string;
    description?: string;
    required?: boolean;
    hint?: string;
    children: React.ReactNode;
}

export function FormField({ name, label, description, required, hint, children }: FormFieldProps) {
    return (
        <div className="form-field">
            <div className="form-field__header">
                <label className="form-field__label" htmlFor={name}>
                    {label}
                    {required && <span className="form-field__required">*</span>}
                </label>
            </div>
            {description && <p className="form-field__description">{description}</p>}
            {children}
            {hint && <p className="form-field__hint">{hint}</p>}
        </div>
    );
}

interface TextFieldProps {
    name: string;
    label: string;
    description?: string;
    required?: boolean;
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    hint?: string;
}

export function TextField({
    name,
    label,
    description,
    required,
    value,
    onChange,
    placeholder,
    hint,
}: TextFieldProps) {
    return (
        <FormField name={name} label={label} description={description} required={required} hint={hint}>
            <input
                type="text"
                id={name}
                name={name}
                className="input"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
            />
        </FormField>
    );
}

interface NumberFieldProps {
    name: string;
    label: string;
    description?: string;
    required?: boolean;
    value: number | '';
    onChange: (value: number | null) => void;
    min?: number;
    max?: number;
    step?: number;
    hint?: string;
}

export function NumberField({
    name,
    label,
    description,
    required,
    value,
    onChange,
    min,
    max,
    step = 1,
    hint,
}: NumberFieldProps) {
    const constraints = [];
    if (min !== undefined && max !== undefined) {
        constraints.push(`Range: ${min} - ${max}`);
    } else if (min !== undefined) {
        constraints.push(`Min: ${min}`);
    } else if (max !== undefined) {
        constraints.push(`Max: ${max}`);
    }

    return (
        <FormField
            name={name}
            label={label}
            description={description}
            required={required}
            hint={hint || constraints.join(', ')}
        >
            <input
                type="number"
                id={name}
                name={name}
                className="input"
                value={value}
                onChange={(e) => onChange(e.target.value ? parseFloat(e.target.value) : null)}
                min={min}
                max={max}
                step={step}
            />
        </FormField>
    );
}

interface SelectFieldProps {
    name: string;
    label: string;
    description?: string;
    required?: boolean;
    value: string;
    onChange: (value: string) => void;
    options: { value: string; label: string; disabled?: boolean }[];
    hint?: string;
}

export function SelectField({
    name,
    label,
    description,
    required,
    value,
    onChange,
    options,
    hint,
}: SelectFieldProps) {
    return (
        <FormField name={name} label={label} description={description} required={required} hint={hint}>
            <select
                id={name}
                name={name}
                className="select"
                value={value}
                onChange={(e) => onChange(e.target.value)}
            >
                <option value="">-- Select --</option>
                {options.map((opt) => (
                    <option key={opt.value} value={opt.value} disabled={opt.disabled}>
                        {opt.label}
                    </option>
                ))}
            </select>
        </FormField>
    );
}

interface CheckboxFieldProps {
    name: string;
    label: string;
    description?: string;
    checked: boolean;
    onChange: (checked: boolean) => void;
}

export function CheckboxField({ name, label, description, checked, onChange }: CheckboxFieldProps) {
    return (
        <FormField name={name} label="" description={description}>
            <label className="checkbox-wrapper">
                <input
                    type="checkbox"
                    id={name}
                    name={name}
                    checked={checked}
                    onChange={(e) => onChange(e.target.checked)}
                />
                <span>{label}</span>
            </label>
        </FormField>
    );
}

interface TextareaFieldProps {
    name: string;
    label: string;
    description?: string;
    required?: boolean;
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    rows?: number;
    hint?: string;
}

export function TextareaField({
    name,
    label,
    description,
    required,
    value,
    onChange,
    placeholder,
    rows = 4,
    hint,
}: TextareaFieldProps) {
    return (
        <FormField name={name} label={label} description={description} required={required} hint={hint}>
            <textarea
                id={name}
                name={name}
                className="textarea"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                rows={rows}
            />
        </FormField>
    );
}

interface PromptFieldProps {
    name: string;
    label: string;
    description?: string;
    required?: boolean;
    value: string;
    onChange: (value: string) => void;
    dataSources: DataSource[];
    placeholder?: string;
}

export function PromptField({
    name,
    label,
    description,
    required,
    value,
    onChange,
    dataSources,
    placeholder,
}: PromptFieldProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const insertVariable = useCallback((varRef: string) => {
        if (!textareaRef.current) return;

        const textarea = textareaRef.current;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const text = textarea.value;
        const newValue = text.substring(0, start) + varRef + text.substring(end);

        onChange(newValue);

        // Restore cursor position after the inserted variable
        setTimeout(() => {
            textarea.focus();
            textarea.selectionStart = start + varRef.length;
            textarea.selectionEnd = start + varRef.length;
        }, 0);
    }, [onChange]);

    const inputSource = dataSources.find((s) => s.type === 'input');
    const upstreamSources = dataSources.filter((s) => s.type === 'upstream');

    return (
        <FormField name={name} label={label} description={description} required={required}>
            <textarea
                ref={textareaRef}
                id={name}
                name={name}
                className="textarea"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                rows={6}
            />

            <div className="variable-pills">
                <span className="variable-pills__label">Insert variable:</span>
                {inputSource?.fields.map((field) => (
                    <button
                        key={field.name}
                        type="button"
                        className="variable-pill"
                        onClick={() => insertVariable(`{{input.${field.name}}}`)}
                    >
                        {field.name}
                    </button>
                ))}
                {upstreamSources.map((source) => (
                    <button
                        key={source.id}
                        type="button"
                        className="variable-pill variable-pill--upstream"
                        onClick={() => insertVariable(`{{upstream.${source.id}.result}}`)}
                    >
                        {source.id}.result
                    </button>
                ))}
                {!inputSource?.fields.length && upstreamSources.length === 0 && (
                    <span style={{ fontStyle: 'italic', fontSize: '11px', color: 'var(--vscode-descriptionForeground)' }}>
                        No variables available
                    </span>
                )}
            </div>
        </FormField>
    );
}

interface JsonFieldProps {
    name: string;
    label: string;
    description?: string;
    required?: boolean;
    value: unknown;
    onChange: (value: unknown) => void;
    placeholder?: string;
}

export function JsonField({
    name,
    label,
    description,
    required,
    value,
    onChange,
    placeholder,
}: JsonFieldProps) {
    const stringValue = typeof value === 'object' && value !== null
        ? JSON.stringify(value, null, 2)
        : String(value ?? '');

    const handleChange = (text: string) => {
        try {
            const parsed = JSON.parse(text);
            onChange(parsed);
        } catch {
            // Keep raw string if not valid JSON
            onChange(text);
        }
    };

    return (
        <FormField name={name} label={label} description={description} required={required} hint="Enter as JSON">
            <textarea
                id={name}
                name={name}
                className="textarea"
                value={stringValue}
                onChange={(e) => handleChange(e.target.value)}
                placeholder={placeholder}
                rows={4}
            />
        </FormField>
    );
}
