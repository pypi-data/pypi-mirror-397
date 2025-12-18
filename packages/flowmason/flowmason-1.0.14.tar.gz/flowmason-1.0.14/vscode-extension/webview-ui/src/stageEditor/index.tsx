/**
 * Stage Editor Entry Point
 *
 * Mounts the React-based stage configuration editor in the VSCode webview.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import { StageEditor } from './StageEditor';
import { useVsCode } from './useVsCode';
import './styles.css';

function App() {
    const { data, isReady, save, cancel } = useVsCode();

    if (!isReady || !data) {
        return (
            <div className="loading">
                <div className="loading__spinner" />
                <span>Loading stage configuration...</span>
            </div>
        );
    }

    return (
        <StageEditor
            stage={data.stage}
            componentDetail={data.componentDetail}
            dataSources={data.dataSources}
            providers={data.providers}
            onSave={save}
            onCancel={cancel}
        />
    );
}

// Mount the app
const container = document.getElementById('root');
if (container) {
    const root = createRoot(container);
    root.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    );
}
