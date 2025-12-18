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

export class FlowMasonDefinitionProvider implements vscode.DefinitionProvider {
    private componentParser: ComponentParser;

    constructor(componentParser: ComponentParser) {
        this.componentParser = componentParser;
    }

    async provideDefinition(
        document: vscode.TextDocument,
        position: vscode.Position,
        _token: vscode.CancellationToken
    ): Promise<vscode.Definition | vscode.LocationLink[] | null> {
        const wordRange = document.getWordRangeAtPosition(position, /["'][\w-]+["']|[\w-]+/);
        if (!wordRange) return null;

        const word = document.getText(wordRange).replace(/["']/g, '');
        const line = document.lineAt(position.line).text;

        // Check for upstream["stage_id"] pattern
        if (line.includes('upstream[') || line.includes('upstream.get(')) {
            return this.findStageDefinition(document, word);
        }

        // Check for depends_on reference
        if (line.includes('depends_on')) {
            return this.findStageDefinition(document, word);
        }

        // Check for component type reference (e.g., in pipeline definitions)
        if (line.includes('component_type') || line.includes('type:')) {
            return this.findComponentDefinition(word);
        }

        // Check for BaseNode/BaseOperator reference
        if (word === 'BaseNode' || word === 'BaseOperator') {
            return this.findBaseClassDefinition(word);
        }

        return null;
    }

    /**
     * Find a stage definition within pipeline files
     */
    private async findStageDefinition(
        currentDocument: vscode.TextDocument,
        stageId: string
    ): Promise<vscode.Location[] | null> {
        const locations: vscode.Location[] = [];

        // Search in current document first
        const currentLocation = this.findStageInDocument(currentDocument, stageId);
        if (currentLocation) {
            locations.push(currentLocation);
        }

        // Search in workspace for pipeline definitions
        const files = await vscode.workspace.findFiles(
            '**/*.{py,json,yaml,yml}',
            '**/node_modules/**'
        );

        for (const file of files) {
            if (file.fsPath === currentDocument.uri.fsPath) continue;

            try {
                const doc = await vscode.workspace.openTextDocument(file);
                const location = this.findStageInDocument(doc, stageId);
                if (location) {
                    locations.push(location);
                }
            } catch {
                // Skip files that can't be opened
            }
        }

        return locations.length > 0 ? locations : null;
    }

    /**
     * Find a stage definition in a specific document
     */
    private findStageInDocument(
        document: vscode.TextDocument,
        stageId: string
    ): vscode.Location | null {
        const text = document.getText();

        // Pattern for stage definitions in pipeline files
        const patterns = [
            // Python: stage_id = "..."
            new RegExp(`["']${stageId}["']\\s*:\\s*\\{`, 'g'),
            // Python: Stage(id="...")
            new RegExp(`Stage\\s*\\([^)]*id\\s*=\\s*["']${stageId}["']`, 'g'),
            // JSON/YAML: "id": "stage-id"
            new RegExp(`"id"\\s*:\\s*["']${stageId}["']`, 'g'),
            // Python decorator with name
            new RegExp(`@(?:node|operator)\\s*\\([^)]*name\\s*=\\s*["']${stageId}["']`, 'g'),
        ];

        for (const pattern of patterns) {
            const match = pattern.exec(text);
            if (match) {
                const pos = document.positionAt(match.index);
                return new vscode.Location(document.uri, pos);
            }
        }

        return null;
    }

    /**
     * Find a component definition by type name
     */
    private async findComponentDefinition(
        componentType: string
    ): Promise<vscode.Location[] | null> {
        const locations: vscode.Location[] = [];

        // Search for Python files with matching component definitions
        const files = await vscode.workspace.findFiles('**/*.py', '**/node_modules/**');

        for (const file of files) {
            try {
                const doc = await vscode.workspace.openTextDocument(file);
                const components = this.componentParser.parseDocument(doc);

                for (const component of components) {
                    if (component.name === componentType) {
                        locations.push(new vscode.Location(
                            doc.uri,
                            component.range.start
                        ));
                    }
                }
            } catch {
                // Skip files that can't be parsed
            }
        }

        return locations.length > 0 ? locations : null;
    }

    /**
     * Find FlowMason base class definition (links to documentation)
     */
    private async findBaseClassDefinition(
        className: string
    ): Promise<vscode.Location | null> {
        // Try to find in flowmason_core package
        const files = await vscode.workspace.findFiles(
            '**/flowmason_core/**/*.py',
            '**/node_modules/**'
        );

        for (const file of files) {
            try {
                const doc = await vscode.workspace.openTextDocument(file);
                const text = doc.getText();

                const pattern = new RegExp(`^class\\s+${className}\\s*[\\(:]`, 'm');
                const match = pattern.exec(text);

                if (match) {
                    const pos = doc.positionAt(match.index);
                    return new vscode.Location(doc.uri, pos);
                }
            } catch {
                // Skip files that can't be opened
            }
        }

        return null;
    }
}

/**
 * FlowMason Reference Provider
 *
 * Finds all references to components and stages.
 */
export class FlowMasonReferenceProvider implements vscode.ReferenceProvider {
    private componentParser: ComponentParser;

    constructor(componentParser: ComponentParser) {
        this.componentParser = componentParser;
    }

    async provideReferences(
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.ReferenceContext,
        _token: vscode.CancellationToken
    ): Promise<vscode.Location[] | null> {
        const wordRange = document.getWordRangeAtPosition(position, /["'][\w-]+["']|[\w-]+/);
        if (!wordRange) return null;

        const word = document.getText(wordRange).replace(/["']/g, '');
        const locations: vscode.Location[] = [];

        // Check if we're on a component definition
        const component = this.componentParser.getComponentAtPosition(document, position);
        if (component) {
            // Find all references to this component
            const refs = await this.findComponentReferences(component.name);
            locations.push(...refs);
        }

        // Find upstream references to this stage
        const stageRefs = await this.findStageReferences(word);
        locations.push(...stageRefs);

        // Include definition if requested
        if (context.includeDeclaration) {
            const declLocation = this.findDeclaration(document, word);
            if (declLocation) {
                locations.unshift(declLocation);
            }
        }

        return locations.length > 0 ? locations : null;
    }

    private async findComponentReferences(componentName: string): Promise<vscode.Location[]> {
        const locations: vscode.Location[] = [];

        const files = await vscode.workspace.findFiles(
            '**/*.{py,json,yaml,yml}',
            '**/node_modules/**'
        );

        for (const file of files) {
            try {
                const doc = await vscode.workspace.openTextDocument(file);
                const text = doc.getText();

                // Find all references to the component name
                const patterns = [
                    new RegExp(`["']${componentName}["']`, 'g'),
                    new RegExp(`component_type\\s*=\\s*["']${componentName}["']`, 'g'),
                    new RegExp(`type:\\s*["']${componentName}["']`, 'g'),
                ];

                for (const pattern of patterns) {
                    let match;
                    while ((match = pattern.exec(text)) !== null) {
                        const pos = doc.positionAt(match.index);
                        locations.push(new vscode.Location(doc.uri, pos));
                    }
                }
            } catch {
                // Skip files that can't be opened
            }
        }

        return locations;
    }

    private async findStageReferences(stageId: string): Promise<vscode.Location[]> {
        const locations: vscode.Location[] = [];

        const files = await vscode.workspace.findFiles(
            '**/*.{py,json,yaml,yml}',
            '**/node_modules/**'
        );

        for (const file of files) {
            try {
                const doc = await vscode.workspace.openTextDocument(file);
                const text = doc.getText();

                // Find upstream references
                const patterns = [
                    new RegExp(`upstream\\s*\\[\\s*["']${stageId}["']\\s*\\]`, 'g'),
                    new RegExp(`depends_on\\s*=\\s*\\[[^\\]]*["']${stageId}["']`, 'g'),
                ];

                for (const pattern of patterns) {
                    let match;
                    while ((match = pattern.exec(text)) !== null) {
                        const pos = doc.positionAt(match.index);
                        locations.push(new vscode.Location(doc.uri, pos));
                    }
                }
            } catch {
                // Skip files that can't be opened
            }
        }

        return locations;
    }

    private findDeclaration(document: vscode.TextDocument, word: string): vscode.Location | null {
        const text = document.getText();
        const pattern = new RegExp(`@(?:node|operator)\\s*\\([^)]*name\\s*=\\s*["']${word}["']`);
        const match = pattern.exec(text);

        if (match) {
            const pos = document.positionAt(match.index);
            return new vscode.Location(document.uri, pos);
        }

        return null;
    }
}
