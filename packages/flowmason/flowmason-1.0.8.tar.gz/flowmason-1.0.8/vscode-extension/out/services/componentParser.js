"use strict";
/**
 * Component Parser
 *
 * Parses Python files to extract FlowMason component definitions.
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
exports.ComponentParser = void 0;
const vscode = __importStar(require("vscode"));
class ComponentParser {
    /**
     * Parse a Python document for FlowMason components
     */
    parseDocument(document) {
        const components = [];
        const text = document.getText();
        const lines = text.split('\n');
        let i = 0;
        while (i < lines.length) {
            const line = lines[i];
            // Look for @node or @operator decorator
            const nodeMatch = line.match(/^\s*@node\s*\(/);
            const operatorMatch = line.match(/^\s*@operator\s*\(/);
            if (nodeMatch || operatorMatch) {
                const decoratorType = nodeMatch ? 'node' : 'operator';
                const decoratorStartLine = i;
                // Extract decorator parameters (may span multiple lines)
                let decoratorContent = '';
                let parenDepth = 0;
                let decoratorEndLine = i;
                for (let j = i; j < lines.length; j++) {
                    const currentLine = lines[j];
                    for (const char of currentLine) {
                        if (char === '(')
                            parenDepth++;
                        if (char === ')')
                            parenDepth--;
                    }
                    decoratorContent += currentLine + '\n';
                    decoratorEndLine = j;
                    if (parenDepth === 0 && decoratorContent.includes('(')) {
                        break;
                    }
                }
                // Find the class definition
                let classLine = decoratorEndLine + 1;
                while (classLine < lines.length && !lines[classLine].match(/^\s*class\s+/)) {
                    classLine++;
                }
                if (classLine < lines.length) {
                    const classMatch = lines[classLine].match(/^\s*class\s+(\w+)/);
                    if (classMatch) {
                        const className = classMatch[1];
                        // Parse decorator parameters
                        const params = this.parseDecoratorParams(decoratorContent);
                        // Find Input and Output classes within this class
                        const classEndLine = this.findClassEnd(lines, classLine);
                        const inputFields = this.parseNestedClass(lines, classLine, classEndLine, 'Input');
                        const outputFields = this.parseNestedClass(lines, classLine, classEndLine, 'Output');
                        components.push({
                            type: decoratorType,
                            name: params.name || this.camelToKebab(className.replace(/Node$|Operator$/, '')),
                            className,
                            category: params.category || 'custom',
                            description: params.description || '',
                            icon: params.icon,
                            color: params.color,
                            version: params.version || '1.0.0',
                            requires_llm: params.requires_llm === 'True' || params.requires_llm === true,
                            inputFields,
                            outputFields,
                            configFields: [], // Config is extracted from __init__ or class attributes
                            range: new vscode.Range(new vscode.Position(decoratorStartLine, 0), new vscode.Position(classEndLine, lines[classEndLine]?.length || 0)),
                        });
                    }
                }
                i = classLine + 1;
            }
            else {
                i++;
            }
        }
        return components;
    }
    /**
     * Parse decorator parameters from the decorator string
     */
    parseDecoratorParams(decoratorContent) {
        const params = {};
        // Extract the content inside @node(...) or @operator(...)
        const match = decoratorContent.match(/@(?:node|operator)\s*\(([\s\S]*)\)/);
        if (!match)
            return params;
        const content = match[1];
        // Parse key=value pairs
        const patterns = [
            { key: 'name', pattern: /name\s*=\s*["']([^"']+)["']/ },
            { key: 'category', pattern: /category\s*=\s*["']([^"']+)["']/ },
            { key: 'description', pattern: /description\s*=\s*["']([^"']+)["']/ },
            { key: 'icon', pattern: /icon\s*=\s*["']([^"']+)["']/ },
            { key: 'color', pattern: /color\s*=\s*["']([^"']+)["']/ },
            { key: 'version', pattern: /version\s*=\s*["']([^"']+)["']/ },
            { key: 'requires_llm', pattern: /requires_llm\s*=\s*(True|False)/ },
        ];
        for (const { key, pattern } of patterns) {
            const match = content.match(pattern);
            if (match) {
                params[key] = match[1];
            }
        }
        return params;
    }
    /**
     * Find the end line of a class definition
     */
    findClassEnd(lines, classStartLine) {
        const classIndent = this.getIndent(lines[classStartLine]);
        let endLine = classStartLine + 1;
        while (endLine < lines.length) {
            const line = lines[endLine];
            const trimmed = line.trim();
            // Skip empty lines and comments
            if (trimmed === '' || trimmed.startsWith('#')) {
                endLine++;
                continue;
            }
            const lineIndent = this.getIndent(line);
            // If we find a line with same or less indent (and it's not empty), class ends
            if (lineIndent <= classIndent && trimmed !== '') {
                return endLine - 1;
            }
            endLine++;
        }
        return lines.length - 1;
    }
    /**
     * Parse a nested class (Input or Output) for field definitions
     */
    parseNestedClass(lines, classStartLine, classEndLine, nestedClassName) {
        const fields = [];
        // Find the nested class
        for (let i = classStartLine + 1; i <= classEndLine; i++) {
            const line = lines[i];
            const classMatch = line.match(new RegExp(`^\\s*class\\s+${nestedClassName}\\s*[:(]`));
            if (classMatch) {
                const nestedClassEnd = this.findClassEnd(lines, i);
                // Parse fields within the nested class
                for (let j = i + 1; j <= nestedClassEnd; j++) {
                    const fieldLine = lines[j];
                    const fieldMatch = fieldLine.match(/^\s+(\w+)\s*:\s*([^=]+)(?:\s*=\s*(.+))?/);
                    if (fieldMatch) {
                        const [, fieldName, fieldType, defaultValue] = fieldMatch;
                        // Skip special attributes
                        if (fieldName.startsWith('_') || fieldName === 'model_config') {
                            continue;
                        }
                        const field = {
                            name: fieldName,
                            type: fieldType.trim(),
                            required: !defaultValue || !defaultValue.includes('None'),
                            constraints: {},
                        };
                        // Parse Field() parameters if present
                        if (defaultValue?.includes('Field(')) {
                            const fieldParams = this.parseFieldParams(defaultValue);
                            field.description = fieldParams.description;
                            field.default = fieldParams.default;
                            field.constraints = fieldParams.constraints;
                        }
                        else if (defaultValue && defaultValue.trim() !== 'None') {
                            field.default = defaultValue.trim();
                        }
                        fields.push(field);
                    }
                }
                break;
            }
        }
        return fields;
    }
    /**
     * Parse Field() parameters
     */
    parseFieldParams(fieldStr) {
        const result = {
            constraints: {},
        };
        // Extract description
        const descMatch = fieldStr.match(/description\s*=\s*["']([^"']+)["']/);
        if (descMatch) {
            result.description = descMatch[1];
        }
        // Extract default
        const defaultMatch = fieldStr.match(/default\s*=\s*([^,)]+)/);
        if (defaultMatch) {
            result.default = defaultMatch[1].trim();
        }
        // Extract constraints
        const constraintPatterns = [
            { key: 'ge', pattern: /ge\s*=\s*([^,)]+)/ },
            { key: 'le', pattern: /le\s*=\s*([^,)]+)/ },
            { key: 'gt', pattern: /gt\s*=\s*([^,)]+)/ },
            { key: 'lt', pattern: /lt\s*=\s*([^,)]+)/ },
            { key: 'min_length', pattern: /min_length\s*=\s*([^,)]+)/ },
            { key: 'max_length', pattern: /max_length\s*=\s*([^,)]+)/ },
            { key: 'pattern', pattern: /pattern\s*=\s*["']([^"']+)["']/ },
        ];
        for (const { key, pattern } of constraintPatterns) {
            const match = fieldStr.match(pattern);
            if (match) {
                result.constraints[key] = match[1].trim();
            }
        }
        return result;
    }
    /**
     * Get indentation level of a line
     */
    getIndent(line) {
        const match = line.match(/^(\s*)/);
        return match ? match[1].length : 0;
    }
    /**
     * Convert CamelCase to kebab-case
     */
    camelToKebab(str) {
        return str
            .replace(/([a-z])([A-Z])/g, '$1-$2')
            .replace(/([A-Z])([A-Z][a-z])/g, '$1-$2')
            .toLowerCase();
    }
    /**
     * Check if a document contains FlowMason components
     */
    hasComponents(document) {
        const text = document.getText();
        return text.includes('@node') || text.includes('@operator');
    }
    /**
     * Get component at a specific position
     */
    getComponentAtPosition(document, position) {
        const components = this.parseDocument(document);
        return components.find(c => c.range.contains(position));
    }
}
exports.ComponentParser = ComponentParser;
//# sourceMappingURL=componentParser.js.map