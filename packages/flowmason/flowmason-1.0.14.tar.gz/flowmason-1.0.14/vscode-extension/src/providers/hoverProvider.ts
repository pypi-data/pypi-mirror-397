/**
 * FlowMason Hover Provider
 *
 * Provides documentation on hover for FlowMason components and APIs.
 */

import * as vscode from 'vscode';

interface HoverInfo {
    pattern: RegExp;
    getHover: (match: RegExpMatchArray) => vscode.MarkdownString;
}

export class FlowMasonHoverProvider implements vscode.HoverProvider {
    private hoverInfos: HoverInfo[];

    constructor() {
        this.hoverInfos = this.createHoverInfos();
    }

    provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.Hover> {
        const range = document.getWordRangeAtPosition(position);
        if (!range) return null;

        const word = document.getText(range);
        const line = document.lineAt(position).text;
        const linePrefix = line.substring(0, position.character);

        // Check for specific hover patterns
        for (const info of this.hoverInfos) {
            // Check if word matches pattern
            const wordMatch = word.match(info.pattern);
            if (wordMatch) {
                return new vscode.Hover(info.getHover(wordMatch), range);
            }

            // Check if line context matches pattern
            const lineMatch = line.match(info.pattern);
            if (lineMatch && this.isWithinMatch(line, position.character, lineMatch)) {
                return new vscode.Hover(info.getHover(lineMatch), range);
            }
        }

        // Check for decorator parameter hover
        if (linePrefix.includes('@node') || linePrefix.includes('@operator')) {
            const paramHover = this.getDecoratorParamHover(word);
            if (paramHover) {
                return new vscode.Hover(paramHover, range);
            }
        }

        // Check for Field parameter hover
        if (line.includes('Field(')) {
            const fieldHover = this.getFieldParamHover(word);
            if (fieldHover) {
                return new vscode.Hover(fieldHover, range);
            }
        }

        return null;
    }

    private isWithinMatch(line: string, position: number, match: RegExpMatchArray): boolean {
        const matchIndex = match.index || 0;
        const matchEnd = matchIndex + match[0].length;
        return position >= matchIndex && position <= matchEnd;
    }

    private createHoverInfos(): HoverInfo[] {
        return [
            // @node decorator
            {
                pattern: /@node/,
                getHover: () => {
                    const md = new vscode.MarkdownString();
                    md.appendMarkdown('## @node Decorator\n\n');
                    md.appendMarkdown('Creates a **FlowMason Node** component.\n\n');
                    md.appendMarkdown('Nodes are AI-powered components that use LLMs for processing.\n\n');
                    md.appendMarkdown('### Parameters\n\n');
                    md.appendMarkdown('| Parameter | Type | Required | Description |\n');
                    md.appendMarkdown('|-----------|------|----------|-------------|\n');
                    md.appendMarkdown('| `name` | str | Yes | Unique identifier (kebab-case) |\n');
                    md.appendMarkdown('| `description` | str | Yes | Human-readable description |\n');
                    md.appendMarkdown('| `category` | str | No | Component category |\n');
                    md.appendMarkdown('| `icon` | str | No | Lucide icon name |\n');
                    md.appendMarkdown('| `color` | str | No | Hex color code |\n');
                    md.appendMarkdown('| `version` | str | No | Component version |\n');
                    md.appendMarkdown('| `tags` | list | No | Searchable tags |\n\n');
                    md.appendCodeblock(
                        '@node(\n' +
                        '    name="my-node",\n' +
                        '    description="Description of my node",\n' +
                        '    category="ai",\n' +
                        '    icon="brain",\n' +
                        '    color="#6366f1"\n' +
                        ')',
                        'python'
                    );
                    return md;
                }
            },
            // @operator decorator
            {
                pattern: /@operator/,
                getHover: () => {
                    const md = new vscode.MarkdownString();
                    md.appendMarkdown('## @operator Decorator\n\n');
                    md.appendMarkdown('Creates a **FlowMason Operator** component.\n\n');
                    md.appendMarkdown('Operators are deterministic components that transform data without LLMs.\n\n');
                    md.appendMarkdown('### Parameters\n\n');
                    md.appendMarkdown('| Parameter | Type | Required | Description |\n');
                    md.appendMarkdown('|-----------|------|----------|-------------|\n');
                    md.appendMarkdown('| `name` | str | Yes | Unique identifier (kebab-case) |\n');
                    md.appendMarkdown('| `description` | str | Yes | Human-readable description |\n');
                    md.appendMarkdown('| `category` | str | No | Component category |\n');
                    md.appendMarkdown('| `icon` | str | No | Lucide icon name |\n');
                    md.appendMarkdown('| `color` | str | No | Hex color code |\n\n');
                    md.appendCodeblock(
                        '@operator(\n' +
                        '    name="my-operator",\n' +
                        '    description="Description of my operator",\n' +
                        '    category="transform",\n' +
                        '    icon="filter",\n' +
                        '    color="#10b981"\n' +
                        ')',
                        'python'
                    );
                    return md;
                }
            },
            // BaseNode class
            {
                pattern: /BaseNode/,
                getHover: () => {
                    const md = new vscode.MarkdownString();
                    md.appendMarkdown('## BaseNode\n\n');
                    md.appendMarkdown('Base class for FlowMason nodes.\n\n');
                    md.appendMarkdown('### Required Methods\n\n');
                    md.appendMarkdown('- `execute(input: Input, context: NodeContext) -> Output`\n\n');
                    md.appendMarkdown('### Context Methods\n\n');
                    md.appendMarkdown('- `context.llm.generate(prompt, system_prompt)` - Generate text\n');
                    md.appendMarkdown('- `context.llm.stream(prompt)` - Stream generation\n');
                    md.appendMarkdown('- `context.upstream["stage_id"]` - Access upstream outputs\n');
                    return md;
                }
            },
            // BaseOperator class
            {
                pattern: /BaseOperator/,
                getHover: () => {
                    const md = new vscode.MarkdownString();
                    md.appendMarkdown('## BaseOperator\n\n');
                    md.appendMarkdown('Base class for FlowMason operators.\n\n');
                    md.appendMarkdown('### Required Methods\n\n');
                    md.appendMarkdown('- `execute(input: Input, context: OperatorContext) -> Output`\n\n');
                    md.appendMarkdown('### Context Methods\n\n');
                    md.appendMarkdown('- `context.upstream["stage_id"]` - Access upstream outputs\n');
                    md.appendMarkdown('- `context.config` - Access operator configuration\n');
                    return md;
                }
            },
            // Field
            {
                pattern: /\bField\b/,
                getHover: () => {
                    const md = new vscode.MarkdownString();
                    md.appendMarkdown('## Field\n\n');
                    md.appendMarkdown('Defines a field in an Input or Output model.\n\n');
                    md.appendMarkdown('### Parameters\n\n');
                    md.appendMarkdown('| Parameter | Type | Description |\n');
                    md.appendMarkdown('|-----------|------|-------------|\n');
                    md.appendMarkdown('| `description` | str | Field description (shown in UI) |\n');
                    md.appendMarkdown('| `default` | Any | Default value |\n');
                    md.appendMarkdown('| `default_factory` | callable | Factory for mutable defaults |\n');
                    md.appendMarkdown('| `min_length` | int | Minimum string length |\n');
                    md.appendMarkdown('| `max_length` | int | Maximum string length |\n');
                    md.appendMarkdown('| `ge` | number | Greater than or equal |\n');
                    md.appendMarkdown('| `le` | number | Less than or equal |\n\n');
                    md.appendCodeblock(
                        'text: str = Field(description="Input text")\n' +
                        'count: int = Field(default=10, ge=1, le=100)\n' +
                        'items: List[str] = Field(default_factory=list)',
                        'python'
                    );
                    return md;
                }
            },
            // NodeContext
            {
                pattern: /NodeContext/,
                getHover: () => {
                    const md = new vscode.MarkdownString();
                    md.appendMarkdown('## NodeContext\n\n');
                    md.appendMarkdown('Context object passed to node execute method.\n\n');
                    md.appendMarkdown('### Properties\n\n');
                    md.appendMarkdown('| Property | Type | Description |\n');
                    md.appendMarkdown('|----------|------|-------------|\n');
                    md.appendMarkdown('| `llm` | LLMClient | LLM client for generation |\n');
                    md.appendMarkdown('| `upstream` | Dict | Outputs from upstream stages |\n');
                    md.appendMarkdown('| `config` | Dict | Node configuration |\n');
                    md.appendMarkdown('| `run_id` | str | Current pipeline run ID |\n\n');
                    md.appendMarkdown('### LLM Methods\n\n');
                    md.appendCodeblock(
                        '# Generate text\n' +
                        'result = await context.llm.generate(\n' +
                        '    prompt="Your prompt here",\n' +
                        '    system_prompt="System instructions"\n' +
                        ')\n\n' +
                        '# Stream generation\n' +
                        'async for chunk in context.llm.stream(prompt):\n' +
                        '    print(chunk)',
                        'python'
                    );
                    return md;
                }
            },
            // OperatorContext
            {
                pattern: /OperatorContext/,
                getHover: () => {
                    const md = new vscode.MarkdownString();
                    md.appendMarkdown('## OperatorContext\n\n');
                    md.appendMarkdown('Context object passed to operator execute method.\n\n');
                    md.appendMarkdown('### Properties\n\n');
                    md.appendMarkdown('| Property | Type | Description |\n');
                    md.appendMarkdown('|----------|------|-------------|\n');
                    md.appendMarkdown('| `upstream` | Dict | Outputs from upstream stages |\n');
                    md.appendMarkdown('| `config` | Dict | Operator configuration |\n');
                    md.appendMarkdown('| `run_id` | str | Current pipeline run ID |\n');
                    return md;
                }
            },
            // upstream access
            {
                pattern: /upstream\[["'](\w+)["']\]/,
                getHover: (match) => {
                    const stageName = match[1];
                    const md = new vscode.MarkdownString();
                    md.appendMarkdown(`## Upstream Reference: \`${stageName}\`\n\n`);
                    md.appendMarkdown('Accesses the output from an upstream pipeline stage.\n\n');
                    md.appendMarkdown('### Usage\n\n');
                    md.appendCodeblock(
                        `# Access the output object\n` +
                        `output = context.upstream["${stageName}"]\n\n` +
                        `# Access specific field\n` +
                        `value = context.upstream["${stageName}"].field_name`,
                        'python'
                    );
                    return md;
                }
            },
            // LLMConfig
            {
                pattern: /LLMConfig/,
                getHover: () => {
                    const md = new vscode.MarkdownString();
                    md.appendMarkdown('## LLMConfig\n\n');
                    md.appendMarkdown('Configuration for LLM providers.\n\n');
                    md.appendMarkdown('### Parameters\n\n');
                    md.appendMarkdown('| Parameter | Type | Description |\n');
                    md.appendMarkdown('|-----------|------|-------------|\n');
                    md.appendMarkdown('| `provider` | Provider | LLM provider (anthropic, openai, etc.) |\n');
                    md.appendMarkdown('| `model` | str | Model identifier |\n');
                    md.appendMarkdown('| `temperature` | float | Sampling temperature (0-1) |\n');
                    md.appendMarkdown('| `max_tokens` | int | Maximum output tokens |\n');
                    return md;
                }
            }
        ];
    }

    private getDecoratorParamHover(word: string): vscode.MarkdownString | null {
        const params: Record<string, string> = {
            'name': '**name** (required)\n\nUnique identifier for the component. Must be kebab-case.\n\nExample: `"my-component"`',
            'description': '**description** (required)\n\nHuman-readable description shown in the UI.\n\nExample: `"Analyzes sentiment of text"`',
            'category': '**category**\n\nComponent category for organization.\n\nCommon values: `"ai"`, `"transform"`, `"analysis"`, `"integration"`, `"utility"`',
            'icon': '**icon**\n\nLucide icon name for the component.\n\nCommon values: `"brain"`, `"sparkles"`, `"zap"`, `"filter"`, `"database"`',
            'color': '**color**\n\nHex color code for the component in the UI.\n\nExample: `"#6366f1"`',
            'version': '**version**\n\nSemantic version string.\n\nExample: `"1.0.0"`',
            'tags': '**tags**\n\nList of searchable tags.\n\nExample: `["ai", "text", "analysis"]`',
            'requires_llm': '**requires_llm** (nodes only)\n\nWhether the node requires an LLM for execution.\n\nDefault: `True`',
            'default_provider': '**default_provider** (nodes only)\n\nDefault LLM provider.\n\nValues: `"anthropic"`, `"openai"`, `"google"`, `"groq"`',
            'default_model': '**default_model** (nodes only)\n\nDefault model identifier.\n\nExample: `"claude-sonnet-4-20250514"`'
        };

        if (params[word]) {
            const md = new vscode.MarkdownString();
            md.appendMarkdown(params[word]);
            return md;
        }

        return null;
    }

    private getFieldParamHover(word: string): vscode.MarkdownString | null {
        const params: Record<string, string> = {
            'description': '**description**\n\nDescription of the field, shown in the UI and documentation.',
            'default': '**default**\n\nDefault value for the field if not provided.',
            'default_factory': '**default_factory**\n\nCallable that returns default value. Use for mutable defaults like lists/dicts.\n\nExample: `default_factory=list`',
            'min_length': '**min_length**\n\nMinimum length for string values.',
            'max_length': '**max_length**\n\nMaximum length for string values.',
            'ge': '**ge** (greater than or equal)\n\nMinimum value for numeric fields.',
            'le': '**le** (less than or equal)\n\nMaximum value for numeric fields.',
            'gt': '**gt** (greater than)\n\nExclusive minimum for numeric fields.',
            'lt': '**lt** (less than)\n\nExclusive maximum for numeric fields.',
            'regex': '**regex**\n\nRegular expression pattern for string validation.',
            'alias': '**alias**\n\nAlternative name for the field in serialization.'
        };

        if (params[word]) {
            const md = new vscode.MarkdownString();
            md.appendMarkdown(params[word]);
            return md;
        }

        return null;
    }
}
