/**
 * Pipeline Diagnostics Provider
 *
 * Validates .pipeline.json files and shows errors/warnings in the
 * native VSCode Problems panel.
 */
import * as vscode from 'vscode';
import { FlowMasonService } from '../services/flowmasonService';
import { PipelineStage } from '../views/pipelineStagesTree';
export declare class PipelineDiagnosticsProvider implements vscode.Disposable {
    private flowmasonService;
    private diagnosticCollection;
    private disposables;
    private knownComponents;
    constructor(flowmasonService: FlowMasonService);
    private loadKnownComponents;
    /**
     * Refresh known components (e.g., after Studio starts)
     */
    refresh(): void;
    validateDocument(document: vscode.TextDocument): Promise<void>;
    private validatePipelineStructure;
    private validateStage;
    /**
     * Detect circular dependencies in the pipeline
     */
    detectCircularDependencies(stages: PipelineStage[], document: vscode.TextDocument, diagnostics: vscode.Diagnostic[]): void;
    private extractErrorPosition;
    private findPropertyRange;
    private findStageRange;
    private findStagePropertyRange;
    dispose(): void;
}
//# sourceMappingURL=pipelineDiagnosticsProvider.d.ts.map