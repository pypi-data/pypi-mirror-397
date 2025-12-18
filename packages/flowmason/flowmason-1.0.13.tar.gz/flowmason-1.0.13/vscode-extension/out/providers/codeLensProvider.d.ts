/**
 * FlowMason CodeLens Provider
 *
 * Shows actionable buttons above execute methods and component decorators.
 */
import * as vscode from 'vscode';
import { ComponentParser } from '../services/componentParser';
export declare class FlowMasonCodeLensProvider implements vscode.CodeLensProvider {
    private _onDidChangeCodeLenses;
    readonly onDidChangeCodeLenses: vscode.Event<void>;
    private componentParser;
    constructor(componentParser: ComponentParser);
    provideCodeLenses(document: vscode.TextDocument, _token: vscode.CancellationToken): vscode.ProviderResult<vscode.CodeLens[]>;
    resolveCodeLens(codeLens: vscode.CodeLens, _token: vscode.CancellationToken): vscode.ProviderResult<vscode.CodeLens>;
    private getComponentCodeLenses;
    private getExecuteCodeLenses;
}
/**
 * Register the run component inline command
 */
export declare function registerRunComponentInlineCommand(context: vscode.ExtensionContext, outputChannel: vscode.OutputChannel): void;
//# sourceMappingURL=codeLensProvider.d.ts.map