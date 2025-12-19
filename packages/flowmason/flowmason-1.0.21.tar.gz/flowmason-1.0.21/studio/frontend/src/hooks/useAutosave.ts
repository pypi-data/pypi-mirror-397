/**
 * FlowMason Autosave Hook
 *
 * Provides debounced autosave functionality for pipeline changes.
 */

import { useEffect, useRef, useCallback, useState } from 'react';

export interface UseAutosaveOptions {
  /** Delay in ms before saving after last change (default: 2000) */
  delay?: number;
  /** Whether autosave is enabled (default: true) */
  enabled?: boolean;
  /** Callback when save starts */
  onSaveStart?: () => void;
  /** Callback when save completes */
  onSaveComplete?: () => void;
  /** Callback when save fails */
  onSaveError?: (error: Error) => void;
}

export interface UseAutosaveReturn {
  /** Whether a save is currently pending */
  isPending: boolean;
  /** Whether autosave is currently saving */
  isSaving: boolean;
  /** Last save timestamp */
  lastSaved: Date | null;
  /** Manually trigger a save */
  saveNow: () => Promise<void>;
  /** Cancel pending save */
  cancel: () => void;
}

export function useAutosave<T>(
  data: T,
  saveFn: (data: T) => Promise<void>,
  hasChanges: boolean,
  options: UseAutosaveOptions = {}
): UseAutosaveReturn {
  const {
    delay = 2000,
    enabled = true,
    onSaveStart,
    onSaveComplete,
    onSaveError,
  } = options;

  const [isPending, setIsPending] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const dataRef = useRef(data);
  const saveFnRef = useRef(saveFn);

  // Keep refs up to date
  useEffect(() => {
    dataRef.current = data;
  }, [data]);

  useEffect(() => {
    saveFnRef.current = saveFn;
  }, [saveFn]);

  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setIsPending(false);
  }, []);

  const saveNow = useCallback(async () => {
    cancel();
    setIsSaving(true);
    onSaveStart?.();

    try {
      await saveFnRef.current(dataRef.current);
      setLastSaved(new Date());
      onSaveComplete?.();
    } catch (error) {
      onSaveError?.(error instanceof Error ? error : new Error(String(error)));
    } finally {
      setIsSaving(false);
    }
  }, [cancel, onSaveStart, onSaveComplete, onSaveError]);

  // Debounced save effect
  useEffect(() => {
    if (!enabled || !hasChanges) {
      cancel();
      return;
    }

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set pending
    setIsPending(true);

    // Schedule save
    timeoutRef.current = setTimeout(() => {
      saveNow();
    }, delay);

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [data, hasChanges, enabled, delay, saveNow, cancel]);

  return {
    isPending,
    isSaving,
    lastSaved,
    saveNow,
    cancel,
  };
}

export default useAutosave;
