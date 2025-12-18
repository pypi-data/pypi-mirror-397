/**
 * FlowMason Completion Provider
 *
 * Provides IntelliSense auto-completion for FlowMason components.
 */
import * as vscode from 'vscode';
export declare class FlowMasonCompletionProvider implements vscode.CompletionItemProvider {
    provideCompletionItems(document: vscode.TextDocument, position: vscode.Position, _token: vscode.CancellationToken, _context: vscode.CompletionContext): vscode.ProviderResult<vscode.CompletionItem[] | vscode.CompletionList>;
    private getDecoratorCompletions;
    private getImportCompletions;
    private getFieldCompletions;
    private getUpstreamCompletions;
    private getDecoratorOptionCompletions;
    private isInsideIOClass;
    private isInsideDecorator;
}
//# sourceMappingURL=completionProvider.d.ts.map