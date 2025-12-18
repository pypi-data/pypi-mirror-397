/**
 * New Project Command
 *
 * Creates a new FlowMason project with the necessary folder structure and starter files.
 */

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

interface ProjectOptions {
    name: string;
    description: string;
    author: string;
    includeExampleNode: boolean;
    includeExamplePipeline: boolean;
}

/**
 * Generate flowmason.json content (project manifest)
 */
function getProjectManifest(options: ProjectOptions): string {
    return JSON.stringify({
        name: options.name,
        version: "1.0.0",
        description: options.description,
        author: options.author,
        main: options.includeExamplePipeline ? "pipelines/main.pipeline.json" : null,
        components: {
            include: ["components/**/*.py"]
        },
        providers: {
            default: "anthropic",
            anthropic: {
                model: "claude-sonnet-4-20250514"
            }
        },
        flowmason: {
            version: ">=0.5.0"
        }
    }, null, 2);
}

/**
 * Generate example node content
 */
function getExampleNodeContent(projectName: string): string {
    const className = projectName
        .split('-')
        .map(part => part.charAt(0).toUpperCase() + part.slice(1))
        .join('') + 'Node';

    return `"""
Example FlowMason Node

This is a starter node for the ${projectName} project.
Customize it to fit your needs!
"""

from flowmason_core import node, NodeInput, NodeOutput, Field


@node(
    name="${projectName}-processor",
    category="custom",
    description="An example node for ${projectName}",
)
class ${className}:
    """Example node that processes text with an LLM."""

    class Input(NodeInput):
        text: str = Field(description="The input text to process")
        max_tokens: int = Field(default=500, description="Maximum tokens in response")

    class Output(NodeOutput):
        result: str = Field(description="The processed result")

    async def execute(self, input: Input, context) -> Output:
        """Process the input text using an LLM."""
        provider = context.providers.get("anthropic")
        if provider:
            response = await provider.call(
                prompt=f"Process the following text and provide a helpful response:\\n\\n{input.text}",
                max_tokens=input.max_tokens
            )
            return self.Output(result=response.text)
        return self.Output(result=f"Processed: {input.text}")
`;
}

/**
 * Generate example operator content
 */
function getExampleOperatorContent(projectName: string): string {
    const className = projectName
        .split('-')
        .map(part => part.charAt(0).toUpperCase() + part.slice(1))
        .join('') + 'Operator';

    return `"""
Example FlowMason Operator

Operators are deterministic components that don't require LLM calls.
"""

from flowmason_core import operator, OperatorInput, OperatorOutput, Field
from typing import Dict, Any


@operator(
    name="${projectName}-transform",
    category="transform",
    description="Transform data for ${projectName}",
)
class ${className}:
    """Example operator that transforms data."""

    class Input(OperatorInput):
        data: Dict[str, Any] = Field(description="Input data to transform")
        uppercase: bool = Field(default=False, description="Convert strings to uppercase")

    class Output(OperatorOutput):
        result: Dict[str, Any] = Field(description="Transformed data")

    async def execute(self, input: Input, context) -> Output:
        """Transform the input data."""
        result = {}
        for key, value in input.data.items():
            if isinstance(value, str) and input.uppercase:
                result[key] = value.upper()
            else:
                result[key] = value
        return self.Output(result=result)
`;
}

/**
 * Generate example pipeline JSON content
 *
 * Creates a pipeline demonstrating the Input → Generate → Output pattern
 * with output routing configuration.
 */
function getExamplePipelineContent(projectName: string): string {
    return JSON.stringify({
        name: `${projectName}-pipeline`,
        version: "1.0.0",
        description: `Main pipeline for ${projectName} - demonstrates Input → Generate → Output flow`,
        input_schema: {
            type: "object",
            properties: {
                text: {
                    type: "string",
                    description: "Input text to process"
                },
                max_tokens: {
                    type: "integer",
                    description: "Maximum tokens in response",
                    default: 500
                }
            },
            required: ["text"]
        },
        output_schema: {
            type: "object",
            properties: {
                result: {
                    type: "string",
                    description: "Generated result"
                },
                input_length: {
                    type: "integer",
                    description: "Length of original input"
                }
            }
        },
        // Output routing configuration - results are automatically sent to these destinations
        output_config: {
            destinations: [
                {
                    id: "dev-webhook",
                    type: "webhook",
                    name: "Development Webhook",
                    enabled: true,  // Uses VSCode FlowMason webhook server
                    config: {
                        url: "http://localhost:9999/webhook",  // Start with: FlowMason: Start Webhook Server
                        method: "POST",
                        headers: {},
                        timeout_ms: 30000,
                        retry_count: 3
                    },
                    on_success: true,
                    on_error: true
                }
            ],
            allow_caller_destinations: true,
            allow_caller_override: false
        },
        stages: [
            {
                id: "validate-input",
                name: "Validate Input",
                component_type: "json_transform",
                config: {
                    data: "{{input}}",
                    jmespath_expression: "{ text: text || ``, length: length(text || ``), max_tokens: max_tokens || `500` }"
                },
                depends_on: [],
                position: { x: 100, y: 100 }
            },
            {
                id: "generate",
                name: "Generate Response",
                component_type: "generator",
                config: {
                    system_prompt: "You are a helpful assistant. Process the user's input and provide a thoughtful response.",
                    prompt: "{{upstream.validate-input.result.text}}",
                    max_tokens: 500
                },
                depends_on: ["validate-input"],
                position: { x: 300, y: 100 }
            },
            {
                id: "format-output",
                name: "Format Output",
                component_type: "json_transform",
                config: {
                    data: {
                        generated: "{{upstream.generate.content}}",
                        input_data: "{{upstream.validate-input.result}}"
                    },
                    jmespath_expression: "{ result: generated, input_length: input_data.length }"
                },
                depends_on: ["generate"],
                position: { x: 500, y: 100 }
            }
        ],
        output_stage_id: "format-output"
    }, null, 2);
}

/**
 * Generate .gitignore content
 */
function getGitignoreContent(): string {
    return `# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
.venv/

# IDE
.idea/
.vscode/settings.json
*.swp
*.swo

# FlowMason
.flowmason/
*.fmpkg

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/
`;
}

/**
 * Generate README.md content
 */
function getReadmeContent(options: ProjectOptions): string {
    return `# ${options.name}

${options.description || 'A FlowMason project.'}

## Getting Started

### Prerequisites

- Python 3.11 or higher
- FlowMason CLI
- VSCode with FlowMason extension (recommended)

### Installation

1. Install FlowMason:
   \`\`\`bash
   pip install flowmason
   \`\`\`

2. Verify installation:
   \`\`\`bash
   fm --version
   \`\`\`

### Running the Pipeline

**Using VSCode (Recommended):**
1. Open this folder in VSCode
2. Press \`F5\` to run the pipeline
3. Or use \`Ctrl+Shift+P\` → "FlowMason: Start Studio"

**Using CLI:**
\`\`\`bash
# Start the Studio backend
fm studio start

# Run the pipeline
fm run pipelines/main.pipeline.json --input '{"text": "Hello, world!"}'
\`\`\`

### Debugging

1. Open \`pipelines/main.pipeline.json\` in VSCode
2. Press \`F9\` to set a breakpoint on any stage
3. Press \`F5\` to start debugging
4. Use \`F10\` to step through stages

## Project Structure

\`\`\`
${options.name}/
├── components/              # Custom nodes and operators
│   ├── __init__.py
│   ├── example_node.py      # Example AI node
│   └── example_operator.py  # Example operator
├── pipelines/               # Pipeline definitions
│   └── main.pipeline.json   # Main pipeline (Input → Generate → Output)
├── flowmason.json           # Project manifest
├── requirements.txt         # Python dependencies
└── README.md               # This file
\`\`\`

## Output Routing

The example pipeline includes \`output_config\` for automatic result delivery.
Configure webhooks, email, database, or message queue destinations:

\`\`\`json
"output_config": {
  "destinations": [
    {
      "id": "my-webhook",
      "type": "webhook",
      "name": "My Callback",
      "enabled": true,
      "config": { "url": "https://..." },
      "on_success": true
    }
  ]
}
\`\`\`

See the [Input/Output Architecture](https://flowmason.com/docs/studio/api/input-output) documentation for details.

## Creating New Components

Use VSCode commands:
- \`Ctrl+Shift+P\` → "FlowMason: New Node" - Create an AI-powered node
- \`Ctrl+Shift+P\` → "FlowMason: New Operator" - Create a deterministic operator

## Documentation

Visit [https://flowmason.com/docs](https://flowmason.com/docs) for complete documentation.

## License

MIT
`;
}

/**
 * Generate requirements.txt content
 */
function getRequirementsContent(): string {
    return `# FlowMason
flowmason>=0.5.0

# Add your project dependencies below
`;
}

export function registerNewProjectCommand(context: vscode.ExtensionContext): void {
    const command = vscode.commands.registerCommand('flowmason.newProject', async () => {
        try {
            // Get project name
            const name = await vscode.window.showInputBox({
                prompt: 'Enter the project name (kebab-case)',
                placeHolder: 'my-flowmason-project',
                validateInput: (value) => {
                    if (!value) {
                        return 'Project name is required';
                    }
                    if (!/^[a-z][a-z0-9-]*$/.test(value)) {
                        return 'Project name must be kebab-case (lowercase letters, numbers, hyphens)';
                    }
                    if (value.length < 3) {
                        return 'Project name must be at least 3 characters';
                    }
                    return null;
                },
            });

            if (!name) {
                return;
            }

            // Get description
            const description = await vscode.window.showInputBox({
                prompt: 'Enter a description for the project',
                placeHolder: 'A FlowMason project for...',
            });

            if (description === undefined) {
                return;
            }

            // Get author
            const author = await vscode.window.showInputBox({
                prompt: 'Enter the author name',
                placeHolder: 'Your Name',
                value: process.env.USER || process.env.USERNAME || '',
            });

            if (author === undefined) {
                return;
            }

            // Ask about including example files
            const includeExamples = await vscode.window.showQuickPick(
                [
                    { label: 'Yes', description: 'Include example node, operator, and pipeline', value: true },
                    { label: 'No', description: 'Create empty project', value: false },
                ],
                {
                    placeHolder: 'Include example files?',
                }
            );

            if (!includeExamples) {
                return;
            }

            // Select folder location
            const folderUri = await vscode.window.showOpenDialog({
                canSelectFiles: false,
                canSelectFolders: true,
                canSelectMany: false,
                openLabel: 'Select Parent Folder',
                title: 'Choose where to create the project',
            });

            if (!folderUri || folderUri.length === 0) {
                return;
            }

            const parentPath = folderUri[0].fsPath;
            const projectPath = path.join(parentPath, name);

            // Check if folder already exists
            if (fs.existsSync(projectPath)) {
                const overwrite = await vscode.window.showWarningMessage(
                    `Folder "${name}" already exists. Do you want to continue and potentially overwrite files?`,
                    { modal: true },
                    'Continue',
                    'Cancel'
                );
                if (overwrite !== 'Continue') {
                    return;
                }
            }

            const options: ProjectOptions = {
                name,
                description: description || '',
                author: author || '',
                includeExampleNode: includeExamples.value,
                includeExamplePipeline: includeExamples.value,
            };

            // Create the project structure
            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: `Creating FlowMason project "${name}"...`,
                    cancellable: false,
                },
                async (progress) => {
                    progress.report({ increment: 0, message: 'Creating folders...' });

                    // Create main folder
                    if (!fs.existsSync(projectPath)) {
                        fs.mkdirSync(projectPath, { recursive: true });
                    }

                    // Create subdirectories
                    const componentsPath = path.join(projectPath, 'components');
                    const pipelinesPath = path.join(projectPath, 'pipelines');

                    if (!fs.existsSync(componentsPath)) {
                        fs.mkdirSync(componentsPath);
                    }
                    if (!fs.existsSync(pipelinesPath)) {
                        fs.mkdirSync(pipelinesPath);
                    }

                    progress.report({ increment: 20, message: 'Creating project manifest...' });

                    // Create flowmason.json
                    fs.writeFileSync(
                        path.join(projectPath, 'flowmason.json'),
                        getProjectManifest(options)
                    );

                    progress.report({ increment: 20, message: 'Creating configuration files...' });

                    // Create .gitignore
                    fs.writeFileSync(
                        path.join(projectPath, '.gitignore'),
                        getGitignoreContent()
                    );

                    // Create README.md
                    fs.writeFileSync(
                        path.join(projectPath, 'README.md'),
                        getReadmeContent(options)
                    );

                    // Create requirements.txt
                    fs.writeFileSync(
                        path.join(projectPath, 'requirements.txt'),
                        getRequirementsContent()
                    );

                    progress.report({ increment: 20, message: 'Creating example files...' });

                    // Create __init__.py for components
                    fs.writeFileSync(
                        path.join(componentsPath, '__init__.py'),
                        '"""FlowMason components for this project."""\n'
                    );

                    // Create example files if requested
                    if (options.includeExampleNode) {
                        fs.writeFileSync(
                            path.join(componentsPath, 'example_node.py'),
                            getExampleNodeContent(name)
                        );

                        fs.writeFileSync(
                            path.join(componentsPath, 'example_operator.py'),
                            getExampleOperatorContent(name)
                        );
                    }

                    if (options.includeExamplePipeline) {
                        fs.writeFileSync(
                            path.join(pipelinesPath, 'main.pipeline.json'),
                            getExamplePipelineContent(name)
                        );
                    }

                    progress.report({ increment: 40, message: 'Done!' });
                }
            );

            // Ask if user wants to open the project
            const openProject = await vscode.window.showInformationMessage(
                `FlowMason project "${name}" created successfully!`,
                'Open Project',
                'Open in New Window',
                'Close'
            );

            if (openProject === 'Open Project') {
                // Open in current window
                await vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(projectPath), false);
            } else if (openProject === 'Open in New Window') {
                // Open in new window
                await vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(projectPath), true);
            }

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create project: ${error}`);
        }
    });

    context.subscriptions.push(command);
}
