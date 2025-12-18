/**
 * AI Configuration Component
 *
 * Provider and model selection for LLM-based stages.
 */

import React, { useMemo, useEffect } from 'react';
import type { ComponentDetail, Provider } from '../types';

interface AIConfigProps {
    componentDetail: ComponentDetail;
    providers: Provider[];
    provider: string;
    model: string;
    onProviderChange: (provider: string) => void;
    onModelChange: (model: string) => void;
}

export function AIConfig({
    componentDetail,
    providers,
    provider,
    model,
    onProviderChange,
    onModelChange,
}: AIConfigProps) {
    const aiConfig = componentDetail.ai_config;
    const recommendedProviders = aiConfig?.recommended_providers || {};
    const defaultProvider = aiConfig?.default_provider || Object.keys(recommendedProviders)[0] || '';

    // Filter to show recommended providers first, then configured ones
    const recommendedProviderNames = Object.keys(recommendedProviders);
    const availableProviders = useMemo(() => {
        return providers.filter(
            (p) => recommendedProviderNames.includes(p.name) || p.configured
        );
    }, [providers, recommendedProviderNames]);

    // Get current provider data
    const currentProviderData = useMemo(() => {
        return providers.find((p) => p.name === provider);
    }, [providers, provider]);

    // Get recommended model for current provider
    const recommendedModel = useMemo(() => {
        const recommended = recommendedProviders[provider];
        return recommended?.model || currentProviderData?.default_model || '';
    }, [provider, recommendedProviders, currentProviderData]);

    // Auto-select default provider if none selected
    useEffect(() => {
        if (!provider && defaultProvider) {
            onProviderChange(defaultProvider);
        }
    }, [provider, defaultProvider, onProviderChange]);

    // Auto-select model when provider changes
    useEffect(() => {
        if (provider && (!model || !currentProviderData?.available_models.includes(model))) {
            const newModel = recommendedModel || currentProviderData?.default_model || '';
            if (newModel) {
                onModelChange(newModel);
            }
        }
    }, [provider, model, recommendedModel, currentProviderData, onModelChange]);

    return (
        <div className="ai-config">
            <div className="ai-config__header">
                <span className="ai-config__icon">🤖</span>
                <span className="ai-config__title">LLM Configuration</span>
            </div>

            <div className="ai-config__grid">
                <div className="ai-config__field">
                    <label className="form-field__label" htmlFor="provider">
                        Provider
                    </label>
                    <select
                        id="provider"
                        className="select"
                        value={provider}
                        onChange={(e) => onProviderChange(e.target.value)}
                    >
                        {availableProviders.map((p) => (
                            <option
                                key={p.name}
                                value={p.name}
                                disabled={!p.configured}
                            >
                                {p.name}
                                {recommendedProviderNames.includes(p.name) ? ' ⭐' : ''}
                                {!p.configured ? ' (not configured)' : ''}
                            </option>
                        ))}
                    </select>
                    <p className="form-field__hint">⭐ = Recommended for this component</p>
                </div>

                <div className="ai-config__field">
                    <label className="form-field__label" htmlFor="model">
                        Model
                    </label>
                    <select
                        id="model"
                        className="select"
                        value={model}
                        onChange={(e) => onModelChange(e.target.value)}
                    >
                        {currentProviderData?.available_models.map((m) => (
                            <option key={m} value={m}>
                                {m}
                                {m === recommendedModel ? ' (recommended)' : ''}
                            </option>
                        ))}
                    </select>
                    <p className="form-field__hint">
                        {recommendedModel ? `Recommended: ${recommendedModel}` : `Default: ${currentProviderData?.default_model || 'N/A'}`}
                    </p>
                </div>
            </div>
        </div>
    );
}
