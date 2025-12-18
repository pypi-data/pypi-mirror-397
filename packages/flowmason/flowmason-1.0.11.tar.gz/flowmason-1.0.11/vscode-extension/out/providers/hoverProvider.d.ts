/**
 * FlowMason Hover Provider
 *
 * Provides documentation on hover for FlowMason components and APIs.
 */
import * as vscode from 'vscode';
export declare class FlowMasonHoverProvider implements vscode.HoverProvider {
    private hoverInfos;
    constructor();
    provideHover(document: vscode.TextDocument, position: vscode.Position, _token: vscode.CancellationToken): vscode.ProviderResult<vscode.Hover>;
    private isWithinMatch;
    private createHoverInfos;
    private getDecoratorParamHover;
    private getFieldParamHover;
}
//# sourceMappingURL=hoverProvider.d.ts.map