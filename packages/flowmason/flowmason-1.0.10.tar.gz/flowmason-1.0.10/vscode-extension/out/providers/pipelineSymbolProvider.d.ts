/**
 * Pipeline Symbol Provider
 *
 * Provides document symbols for .pipeline.json files to enable
 * the native VSCode Outline view and breadcrumb navigation.
 */
import * as vscode from 'vscode';
export declare class PipelineSymbolProvider implements vscode.DocumentSymbolProvider {
    provideDocumentSymbols(document: vscode.TextDocument, _token: vscode.CancellationToken): vscode.ProviderResult<vscode.DocumentSymbol[]>;
    private buildSymbols;
    private createStageSymbol;
    private getSymbolKind;
    private formatValue;
    /**
     * Find the range of a top-level property in the document
     */
    private findPropertyRange;
    /**
     * Find the range of an entire stage object by its ID
     */
    private findStageRange;
    /**
     * Find a property range within a specific stage
     */
    private findStagePropertyRange;
    /**
     * Expand a range to include the full JSON block that follows
     */
    private expandRangeToBlock;
}
//# sourceMappingURL=pipelineSymbolProvider.d.ts.map