/**
 * VSCode Webview API type declarations
 */

interface VsCodeApi {
    postMessage(message: unknown): void;
    getState(): unknown;
    setState(state: unknown): void;
}

declare function acquireVsCodeApi(): VsCodeApi;

declare const vscode: VsCodeApi;
