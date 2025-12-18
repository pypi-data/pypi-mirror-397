/**
 * Stage Config View Provider
 *
 * A WebviewView panel in the sidebar for editing stage configuration.
 * Uses VSCode's native styling for a consistent look.
 */
import * as vscode from 'vscode';
import { FlowMasonService } from '../services/flowmasonService';
import { PipelineStage } from './pipelineStagesTree';
export declare class StageConfigViewProvider implements vscode.WebviewViewProvider {
    private readonly _extensionUri;
    private readonly flowmasonService;
    static readonly viewType = "flowmason.stageConfig";
    private _view?;
    private _currentStage?;
    private _currentComponent?;
    private _currentDocument?;
    private _disposables;
    constructor(_extensionUri: vscode.Uri, flowmasonService: FlowMasonService);
    resolveWebviewView(webviewView: vscode.WebviewView, _context: vscode.WebviewViewResolveContext, _token: vscode.CancellationToken): void;
    /**
     * Show configuration for a specific stage
     */
    showStage(stage: PipelineStage, document: vscode.TextDocument): Promise<void>;
    /**
     * Clear the panel
     */
    clear(): void;
    private handleConfigChange;
    private handleDeleteStage;
    private handleDuplicateStage;
    private getEmptyHtml;
    private getStageConfigHtml;
    private generateConfigFields;
    private generateField;
    private escapeHtml;
    dispose(): void;
}
/**
 * Register the command to show stage config
 */
export declare function registerStageConfigCommands(context: vscode.ExtensionContext, stageConfigProvider: StageConfigViewProvider): void;
//# sourceMappingURL=stageConfigView.d.ts.map