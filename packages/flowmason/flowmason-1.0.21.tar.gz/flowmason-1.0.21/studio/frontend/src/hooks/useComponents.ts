/**
 * Hook for fetching and managing components from the registry.
 */

import { useState, useEffect, useCallback } from 'react';
import { registry } from '../services/api';
import type { ComponentInfo, RegistryStats } from '../types';

export function useComponents(params?: {
  category?: string;
  kind?: 'node' | 'operator';
}) {
  const [components, setComponents] = useState<ComponentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchComponents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await registry.listComponents(params);
      setComponents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch components');
    } finally {
      setLoading(false);
    }
  }, [params?.category, params?.kind]);

  useEffect(() => {
    fetchComponents();
  }, [fetchComponents]);

  return { components, loading, error, refetch: fetchComponents };
}

export function useComponent(type: string) {
  const [component, setComponent] = useState<ComponentInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!type) {
      setComponent(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    registry
      .getComponent(type)
      .then(setComponent)
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Failed to fetch component');
      })
      .finally(() => setLoading(false));
  }, [type]);

  return { component, loading, error };
}

export function useRegistryStats() {
  const [stats, setStats] = useState<RegistryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await registry.getStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, loading, error, refetch: fetchStats };
}
