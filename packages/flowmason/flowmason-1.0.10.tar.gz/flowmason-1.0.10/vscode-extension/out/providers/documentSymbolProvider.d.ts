/**
 * FlowMason Document Symbol Provider
 *
 * Provides outline view symbols for FlowMason components.
 * Shows:
 * - Component class
 * - Input/Output classes with their fields
 * - execute method
 * - Configuration fields
 */
import * as vscode from 'vscode';
import { ComponentParser } from '../services/componentParser';
export declare class FlowMasonDocumentSymbolProvider implements vscode.DocumentSymbolProvider {
    private componentParser;
    constructor(componentParser: ComponentParser);
    provideDocumentSymbols(document: vscode.TextDocument, _token: vscode.CancellationToken): vscode.ProviderResult<vscode.SymbolInformation[] | vscode.DocumentSymbol[]>;
    private createComponentSymbol;
    private createIOClassSymbol;
    private findExecuteMethod;
    private findFieldLine;
    private getIndent;
}
//# sourceMappingURL=documentSymbolProvider.d.ts.map