/**
 * VSCode Webview Hook
 *
 * Manages communication between the React app and the VSCode extension.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { ExtensionMessage, StageEditorInitData, WebviewMessage } from './types';

interface VsCodeApi {
    postMessage(message: unknown): void;
    getState(): unknown;
    setState(state: unknown): void;
}

declare function acquireVsCodeApi(): VsCodeApi;

// Get the VSCode API instance (only once)
const vscode = acquireVsCodeApi();

export function useVsCode() {
    const [data, setData] = useState<StageEditorInitData | null>(null);
    const [isReady, setIsReady] = useState(false);
    const listenerRef = useRef<((event: MessageEvent) => void) | null>(null);

    // Send message to extension
    const postMessage = useCallback((message: WebviewMessage) => {
        vscode.postMessage(message);
    }, []);

    // Handle messages from extension
    useEffect(() => {
        const handleMessage = (event: MessageEvent<ExtensionMessage>) => {
            const message = event.data;

            switch (message.type) {
                case 'init':
                    setData(message.data);
                    setIsReady(true);
                    // Save state for persistence
                    vscode.setState(message.data);
                    break;

                case 'update':
                    setData(prev => {
                        if (!prev) return message.data as StageEditorInitData;
                        const updated = { ...prev, ...message.data };
                        vscode.setState(updated);
                        return updated;
                    });
                    break;
            }
        };

        listenerRef.current = handleMessage;
        window.addEventListener('message', handleMessage);

        // Try to restore state
        const previousState = vscode.getState() as StageEditorInitData | null;
        if (previousState) {
            setData(previousState);
            setIsReady(true);
        }

        // Signal that webview is ready
        postMessage({ type: 'ready' });

        return () => {
            window.removeEventListener('message', listenerRef.current!);
        };
    }, [postMessage]);

    const save = useCallback((config: Record<string, unknown>, outputConfig?: Record<string, unknown> | null) => {
        postMessage({
            type: 'save',
            config,
            output_config: outputConfig as StageEditorInitData['stage']['output_config'] | null | undefined,
        });
    }, [postMessage]);

    const cancel = useCallback(() => {
        postMessage({ type: 'cancel' });
    }, [postMessage]);

    return {
        data,
        isReady,
        save,
        cancel,
    };
}
