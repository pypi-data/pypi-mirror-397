/**
 * Settings Hook
 *
 * Fetches and manages application settings.
 */

import { useState, useEffect, useCallback } from 'react';
import { settings as settingsApi } from '../services/api';
import type { AppSettingsResponse } from '../types';

export function useSettings() {
  const [settings, setSettings] = useState<AppSettingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const data = await settingsApi.get();
      setSettings(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Check if any provider is configured
  const hasConfiguredProvider = settings
    ? Object.values(settings.providers).some((p) => p.has_key && p.enabled)
    : false;

  // Get configured providers list
  const configuredProviders = settings
    ? Object.entries(settings.providers)
        .filter(([, p]) => p.has_key && p.enabled)
        .map(([name]) => name)
    : [];

  return {
    settings,
    loading,
    error,
    refresh,
    hasConfiguredProvider,
    configuredProviders,
  };
}
