/**
 * FlowMason Code Action Provider
 *
 * Provides quick fixes for FlowMason diagnostics.
 */
import * as vscode from 'vscode';
export declare class FlowMasonCodeActionProvider implements vscode.CodeActionProvider {
    static readonly providedCodeActionKinds: vscode.CodeActionKind[];
    provideCodeActions(document: vscode.TextDocument, range: vscode.Range | vscode.Selection, context: vscode.CodeActionContext, _token: vscode.CancellationToken): vscode.ProviderResult<(vscode.CodeAction | vscode.Command)[]>;
    private createAddDecoratorFix;
    private createAddDescriptionFix;
    private createAddFieldDescriptionFix;
    private createKebabCaseFix;
    private createAddInputClassFix;
    private createAddOutputClassFix;
    private createAddReturnTypeFix;
    private createConvertToNodeAction;
    private createConvertToOperatorAction;
    private hasDecoratorAbove;
    private isInsideClass;
    private getIndent;
    private toKebabCase;
}
//# sourceMappingURL=codeActionProvider.d.ts.map