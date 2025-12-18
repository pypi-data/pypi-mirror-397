/**
 * Development Webhook Server
 *
 * A built-in webhook server for testing pipeline output_config during development.
 * Received payloads are displayed in the VSCode Output panel.
 */
import * as vscode from 'vscode';
export declare class WebhookServer {
    private readonly context;
    private server;
    private outputChannel;
    private statusBarItem;
    private port;
    private requestCount;
    private payloads;
    private maxPayloads;
    constructor(context: vscode.ExtensionContext);
    get isRunning(): boolean;
    get serverUrl(): string;
    start(): Promise<void>;
    stop(): Promise<void>;
    toggle(): Promise<void>;
    private handleRequest;
    private handleRawView;
    private handleClear;
    private handleWebView;
    private generateWebViewHtml;
    private formatHeaders;
    private escapeHtml;
    private logPayload;
    private updateStatusBar;
    copyUrl(): void;
    dispose(): void;
}
/**
 * Register webhook server commands
 */
export declare function registerWebhookServer(context: vscode.ExtensionContext): WebhookServer;
//# sourceMappingURL=webhookServer.d.ts.map