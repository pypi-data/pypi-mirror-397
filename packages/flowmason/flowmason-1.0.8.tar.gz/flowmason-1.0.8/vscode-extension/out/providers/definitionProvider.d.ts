/**
 * FlowMason Definition Provider
 *
 * Provides Go to Definition support for FlowMason components.
 * Supports navigating to:
 * - depends_on stage references
 * - upstream["stage_id"] references
 * - Component type references
 */
import * as vscode from 'vscode';
import { ComponentParser } from '../services/componentParser';
export declare class FlowMasonDefinitionProvider implements vscode.DefinitionProvider {
    private componentParser;
    constructor(componentParser: ComponentParser);
    provideDefinition(document: vscode.TextDocument, position: vscode.Position, _token: vscode.CancellationToken): Promise<vscode.Definition | vscode.LocationLink[] | null>;
    /**
     * Find a stage definition within pipeline files
     */
    private findStageDefinition;
    /**
     * Find a stage definition in a specific document
     */
    private findStageInDocument;
    /**
     * Find a component definition by type name
     */
    private findComponentDefinition;
    /**
     * Find FlowMason base class definition (links to documentation)
     */
    private findBaseClassDefinition;
}
/**
 * FlowMason Reference Provider
 *
 * Finds all references to components and stages.
 */
export declare class FlowMasonReferenceProvider implements vscode.ReferenceProvider {
    private componentParser;
    constructor(componentParser: ComponentParser);
    provideReferences(document: vscode.TextDocument, position: vscode.Position, context: vscode.ReferenceContext, _token: vscode.CancellationToken): Promise<vscode.Location[] | null>;
    private findComponentReferences;
    private findStageReferences;
    private findDeclaration;
}
//# sourceMappingURL=definitionProvider.d.ts.map