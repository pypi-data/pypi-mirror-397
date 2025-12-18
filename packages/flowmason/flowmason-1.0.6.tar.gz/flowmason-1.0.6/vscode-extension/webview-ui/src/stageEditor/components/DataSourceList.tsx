/**
 * Data Source List Component
 *
 * Shows available data sources (pipeline input and upstream stages).
 */

import React from 'react';
import type { DataSource } from '../types';

interface DataSourceListProps {
    dataSources: DataSource[];
}

export function DataSourceList({ dataSources }: DataSourceListProps) {
    const inputSource = dataSources.find((s) => s.type === 'input');
    const upstreamSources = dataSources.filter((s) => s.type === 'upstream');

    if (!inputSource?.fields.length && upstreamSources.length === 0) {
        return (
            <div className="hint">
                <span className="hint__icon">⚠️</span>
                <span>No data sources available. This stage has no inputs to work with.</span>
            </div>
        );
    }

    return (
        <div>
            {inputSource && inputSource.fields.length > 0 && (
                <div className="data-source">
                    <div className="data-source__header">
                        <span className="data-source__icon">📥</span>
                        <span className="data-source__title">Pipeline Input</span>
                        <span className="data-source__count">{inputSource.fields.length} fields</span>
                    </div>
                    <div className="data-source__fields">
                        {inputSource.fields.map((field) => (
                            <div key={field.name} className="field-chip">
                                <span className="field-chip__name">{field.name}</span>
                                <span className="field-chip__type">{field.type}</span>
                                {field.required && <span className="field-chip__required">required</span>}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {!inputSource?.fields.length && (
                <div className="hint" style={{ marginBottom: '12px' }}>
                    <span className="hint__icon">💡</span>
                    <span>
                        No pipeline input schema defined. Add <code>input_schema</code> to your pipeline to define available inputs.
                    </span>
                </div>
            )}

            {upstreamSources.map((source) => (
                <div key={source.id} className="data-source data-source--upstream">
                    <div className="data-source__header">
                        <span className="data-source__icon">📦</span>
                        <span className="data-source__title">From: {source.name}</span>
                        <span className="data-source__count">{source.fields.length} outputs</span>
                    </div>
                    <div className="data-source__fields">
                        {source.fields.map((field) => (
                            <div key={field.name} className="field-chip">
                                <span className="field-chip__name">{field.name}</span>
                                <span className="field-chip__type">{field.type}</span>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}
