"use strict";
/**
 * FlowMason Definition Provider
 *
 * Provides Go to Definition support for FlowMason components.
 * Supports navigating to:
 * - depends_on stage references
 * - upstream["stage_id"] references
 * - Component type references
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowMasonReferenceProvider = exports.FlowMasonDefinitionProvider = void 0;
const vscode = __importStar(require("vscode"));
class FlowMasonDefinitionProvider {
    constructor(componentParser) {
        this.componentParser = componentParser;
    }
    async provideDefinition(document, position, _token) {
        const wordRange = document.getWordRangeAtPosition(position, /["'][\w-]+["']|[\w-]+/);
        if (!wordRange)
            return null;
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
    async findStageDefinition(currentDocument, stageId) {
        const locations = [];
        // Search in current document first
        const currentLocation = this.findStageInDocument(currentDocument, stageId);
        if (currentLocation) {
            locations.push(currentLocation);
        }
        // Search in workspace for pipeline definitions
        const files = await vscode.workspace.findFiles('**/*.{py,json,yaml,yml}', '**/node_modules/**');
        for (const file of files) {
            if (file.fsPath === currentDocument.uri.fsPath)
                continue;
            try {
                const doc = await vscode.workspace.openTextDocument(file);
                const location = this.findStageInDocument(doc, stageId);
                if (location) {
                    locations.push(location);
                }
            }
            catch {
                // Skip files that can't be opened
            }
        }
        return locations.length > 0 ? locations : null;
    }
    /**
     * Find a stage definition in a specific document
     */
    findStageInDocument(document, stageId) {
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
    async findComponentDefinition(componentType) {
        const locations = [];
        // Search for Python files with matching component definitions
        const files = await vscode.workspace.findFiles('**/*.py', '**/node_modules/**');
        for (const file of files) {
            try {
                const doc = await vscode.workspace.openTextDocument(file);
                const components = this.componentParser.parseDocument(doc);
                for (const component of components) {
                    if (component.name === componentType) {
                        locations.push(new vscode.Location(doc.uri, component.range.start));
                    }
                }
            }
            catch {
                // Skip files that can't be parsed
            }
        }
        return locations.length > 0 ? locations : null;
    }
    /**
     * Find FlowMason base class definition (links to documentation)
     */
    async findBaseClassDefinition(className) {
        // Try to find in flowmason_core package
        const files = await vscode.workspace.findFiles('**/flowmason_core/**/*.py', '**/node_modules/**');
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
            }
            catch {
                // Skip files that can't be opened
            }
        }
        return null;
    }
}
exports.FlowMasonDefinitionProvider = FlowMasonDefinitionProvider;
/**
 * FlowMason Reference Provider
 *
 * Finds all references to components and stages.
 */
class FlowMasonReferenceProvider {
    constructor(componentParser) {
        this.componentParser = componentParser;
    }
    async provideReferences(document, position, context, _token) {
        const wordRange = document.getWordRangeAtPosition(position, /["'][\w-]+["']|[\w-]+/);
        if (!wordRange)
            return null;
        const word = document.getText(wordRange).replace(/["']/g, '');
        const locations = [];
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
    async findComponentReferences(componentName) {
        const locations = [];
        const files = await vscode.workspace.findFiles('**/*.{py,json,yaml,yml}', '**/node_modules/**');
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
            }
            catch {
                // Skip files that can't be opened
            }
        }
        return locations;
    }
    async findStageReferences(stageId) {
        const locations = [];
        const files = await vscode.workspace.findFiles('**/*.{py,json,yaml,yml}', '**/node_modules/**');
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
            }
            catch {
                // Skip files that can't be opened
            }
        }
        return locations;
    }
    findDeclaration(document, word) {
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
exports.FlowMasonReferenceProvider = FlowMasonReferenceProvider;
//# sourceMappingURL=definitionProvider.js.map