/**
 * Component Parser
 *
 * Parses Python files to extract FlowMason component definitions.
 */
import * as vscode from 'vscode';
export interface ParsedComponent {
    type: 'node' | 'operator';
    name: string;
    className: string;
    category: string;
    description: string;
    icon?: string;
    color?: string;
    version: string;
    requires_llm: boolean;
    inputClass?: string;
    outputClass?: string;
    inputFields: ParsedField[];
    outputFields: ParsedField[];
    configFields: ParsedField[];
    range: vscode.Range;
}
export interface ParsedField {
    name: string;
    type: string;
    description?: string;
    default?: string;
    required: boolean;
    constraints: Record<string, unknown>;
}
export declare class ComponentParser {
    /**
     * Parse a Python document for FlowMason components
     */
    parseDocument(document: vscode.TextDocument): ParsedComponent[];
    /**
     * Parse decorator parameters from the decorator string
     */
    private parseDecoratorParams;
    /**
     * Find the end line of a class definition
     */
    private findClassEnd;
    /**
     * Parse a nested class (Input or Output) for field definitions
     */
    private parseNestedClass;
    /**
     * Parse Field() parameters
     */
    private parseFieldParams;
    /**
     * Get indentation level of a line
     */
    private getIndent;
    /**
     * Convert CamelCase to kebab-case
     */
    private camelToKebab;
    /**
     * Check if a document contains FlowMason components
     */
    hasComponents(document: vscode.TextDocument): boolean;
    /**
     * Get component at a specific position
     */
    getComponentAtPosition(document: vscode.TextDocument, position: vscode.Position): ParsedComponent | undefined;
}
//# sourceMappingURL=componentParser.d.ts.map