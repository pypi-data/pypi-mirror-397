/**
 * React-based Stage Configuration Editor
 *
 * VSCode webview panel that hosts the React-based stage editor.
 * Provides a modern, visual-first configuration experience.
 */
import * as vscode from 'vscode';
import { FlowMasonService } from '../services/flowmasonService';
import { PipelineStage } from '../views/pipelineStagesTree';
export declare class ReactStageConfigEditor {
    private readonly extensionUri;
    private readonly flowmasonService;
    private static panels;
    constructor(extensionUri: vscode.Uri, flowmasonService: FlowMasonService);
    openEditor(stage: PipelineStage, document: vscode.TextDocument): Promise<void>;
    private getDataSources;
    private isDownstream;
    private parseExistingMappings;
    private saveConfig;
    private getHtml;
}
//# sourceMappingURL=reactStageConfigEditor.d.ts.map