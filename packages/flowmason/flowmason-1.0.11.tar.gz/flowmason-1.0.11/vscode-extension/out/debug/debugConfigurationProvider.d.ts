/**
 * FlowMason Debug Configuration Provider
 *
 * Provides launch configurations and resolves debug configurations for FlowMason pipelines.
 */
import * as vscode from 'vscode';
/**
 * Provides initial debug configurations and resolves them before launching
 */
export declare class FlowMasonDebugConfigurationProvider implements vscode.DebugConfigurationProvider {
    /**
     * Provide initial debug configurations when creating launch.json
     */
    provideDebugConfigurations(folder: vscode.WorkspaceFolder | undefined, token?: vscode.CancellationToken): vscode.ProviderResult<vscode.DebugConfiguration[]>;
    /**
     * Resolve a debug configuration before launching
     * This is called to fill in missing fields or validate the configuration
     */
    resolveDebugConfiguration(folder: vscode.WorkspaceFolder | undefined, config: vscode.DebugConfiguration, token?: vscode.CancellationToken): Promise<vscode.DebugConfiguration | undefined>;
    /**
     * Prompt user for pipeline inputs based on input_schema
     */
    private promptForInputs;
    /**
     * Resolve VSCode variables like ${file}, ${workspaceFolder}
     */
    private resolveVariables;
}
/**
 * Debug Adapter Descriptor Factory
 * Creates the debug adapter instance
 */
export declare class FlowMasonDebugAdapterDescriptorFactory implements vscode.DebugAdapterDescriptorFactory {
    createDebugAdapterDescriptor(session: vscode.DebugSession, executable: vscode.DebugAdapterExecutable | undefined): vscode.ProviderResult<vscode.DebugAdapterDescriptor>;
}
/**
 * Register debug commands
 */
export declare function registerDebugCommands(context: vscode.ExtensionContext): void;
//# sourceMappingURL=debugConfigurationProvider.d.ts.map