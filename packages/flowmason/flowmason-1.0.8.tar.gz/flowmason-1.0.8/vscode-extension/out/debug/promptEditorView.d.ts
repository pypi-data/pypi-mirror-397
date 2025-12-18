/**
 * Prompt Editor View
 *
 * A webview panel for editing and iterating on prompts during debug sessions.
 * Allows users to modify prompts, re-run stages, and compare outputs.
 */
import * as vscode from 'vscode';
interface StagePromptInfo {
    stageId: string;
    stageName: string;
    componentType: string;
    systemPrompt: string;
    userPrompt: string;
    variables: Record<string, unknown>;
    output?: string;
}
/**
 * Prompt Editor View Provider
 * Shows in the sidebar during debug sessions
 */
export declare class PromptEditorViewProvider implements vscode.WebviewViewProvider {
    private readonly _extensionUri;
    static readonly viewType = "flowmason.promptEditor";
    private _view?;
    private _currentPrompt?;
    private _promptVersions;
    private _comparisonState;
    private _onPromptChange;
    readonly onPromptChange: vscode.Event<{
        stageId: string;
        systemPrompt: string;
        userPrompt: string;
    }>;
    private _onRerunRequest;
    readonly onRerunRequest: vscode.Event<{
        stageId: string;
        systemPrompt: string;
        userPrompt: string;
    }>;
    constructor(_extensionUri: vscode.Uri);
    resolveWebviewView(webviewView: vscode.WebviewView, context: vscode.WebviewViewResolveContext, token: vscode.CancellationToken): void;
    /**
     * Show prompt for a stage
     */
    showPrompt(info: StagePromptInfo): void;
    /**
     * Update output after re-run
     */
    updateOutput(stageId: string, output: string, tokens?: {
        input: number;
        output: number;
    }): void;
    /**
     * Signal that streaming is starting for a stage
     */
    streamStart(stageId: string, stageName?: string): void;
    /**
     * Show streaming output chunk
     */
    streamOutput(stageId: string, chunk: string, tokenIndex?: number): void;
    /**
     * Signal that streaming has ended for a stage
     */
    streamEnd(stageId: string, totalTokens?: number, finalContent?: string): void;
    /**
     * Clear the prompt editor
     */
    clear(): void;
    /**
     * Save a prompt version
     */
    private _savePromptVersion;
    /**
     * Toggle comparison mode
     */
    private _toggleComparison;
    /**
     * Select a version for comparison
     */
    private _selectForComparison;
    /**
     * Load a prompt version
     */
    private _loadPromptVersion;
    /**
     * Get HTML content for the webview
     */
    private _getHtmlContent;
}
/**
 * Register prompt editor commands
 */
export declare function registerPromptEditorCommands(context: vscode.ExtensionContext, promptEditorProvider: PromptEditorViewProvider): void;
export {};
//# sourceMappingURL=promptEditorView.d.ts.map