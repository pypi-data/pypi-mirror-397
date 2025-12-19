"""
TypeScript/Node.js Code Generator Service.

Generates standalone TypeScript/Node.js code from FlowMason pipelines.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from flowmason_studio.models.codegen import (
    CodeGenOptions,
    CodeGenResult,
    GeneratedFile,
    OutputFormat,
    TargetLanguage,
    TargetPlatform,
)


class TypeScriptCodeGenerator:
    """Generates TypeScript/Node.js code from pipeline definitions."""

    def __init__(self):
        """Initialize the code generator."""
        self.generator_version = "1.0.0"

    def generate(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> CodeGenResult:
        """
        Generate TypeScript/Node.js code from a pipeline definition.

        Args:
            pipeline: Pipeline configuration dictionary
            options: Code generation options

        Returns:
            CodeGenResult with generated files
        """
        gen_id = str(uuid.uuid4())
        pipeline_id = pipeline.get("id", "pipeline")
        pipeline_name = pipeline.get("name", "generated_pipeline")

        # Sanitize name for TypeScript
        module_name = self._sanitize_name(pipeline_name)

        files: List[GeneratedFile] = []

        # Generate based on output format
        if options.output_format == OutputFormat.SINGLE_FILE:
            files = self._generate_single_file(pipeline, options, module_name)
        else:
            files = self._generate_package(pipeline, options, module_name)

        # Add platform-specific files
        if options.platform == TargetPlatform.AWS_LAMBDA:
            files.extend(self._generate_lambda_files(pipeline, options, module_name))
        elif options.platform == TargetPlatform.CLOUDFLARE_WORKERS:
            files.extend(self._generate_workers_files(pipeline, options, module_name))
        elif options.platform == TargetPlatform.FIREBASE_FUNCTIONS:
            files.extend(self._generate_firebase_files(pipeline, options, module_name))

        # Calculate stats
        total_lines = sum(
            len(f.content.split("\n")) for f in files if not f.is_binary
        )

        # Determine entry point
        entry_point = "src/index.ts" if options.output_format == OutputFormat.PACKAGE else f"{module_name}.ts"

        return CodeGenResult(
            id=gen_id,
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            options=options,
            files=files,
            entry_point=entry_point,
            total_lines=total_lines,
            total_files=len(files),
            deployment_config=self._get_deployment_config(options, module_name),
            deploy_instructions=self._get_deploy_instructions(options, module_name),
        )

    def _sanitize_name(self, name: str) -> str:
        """Convert name to valid TypeScript identifier."""
        # Replace hyphens and spaces with underscores
        name = name.replace(" ", "_").replace("-", "_")
        # Remove invalid characters
        name = "".join(c for c in name if c.isalnum() or c == "_")
        # Ensure doesn't start with number
        if name and name[0].isdigit():
            name = f"pipeline_{name}"
        return self._to_camel_case(name) or "pipeline"

    def _to_camel_case(self, name: str) -> str:
        """Convert to camelCase."""
        parts = name.lower().split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    def _to_pascal_case(self, name: str) -> str:
        """Convert to PascalCase."""
        parts = name.lower().split("_")
        return "".join(p.capitalize() for p in parts)

    def _generate_single_file(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate all code in a single file."""
        code = self._generate_main_code(pipeline, options, standalone=True)

        return [
            GeneratedFile(
                path=f"{module_name}.ts",
                content=code,
                description="Complete pipeline implementation",
                executable=True,
            ),
            GeneratedFile(
                path="package.json",
                content=self._generate_package_json(pipeline, options, module_name),
                description="Node.js package configuration",
            ),
            GeneratedFile(
                path="tsconfig.json",
                content=self._generate_tsconfig(),
                description="TypeScript configuration",
            ),
        ]

    def _generate_package(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate a proper TypeScript package."""
        files = []

        # src/index.ts - entry point
        files.append(GeneratedFile(
            path="src/index.ts",
            content=self._generate_index(pipeline, options),
            description="Package entry point",
        ))

        # src/pipeline.ts - main pipeline
        files.append(GeneratedFile(
            path="src/pipeline.ts",
            content=self._generate_main_code(pipeline, options, standalone=False),
            description="Main pipeline execution",
            executable=True,
        ))

        # src/stages.ts - stage implementations
        files.append(GeneratedFile(
            path="src/stages.ts",
            content=self._generate_stages(pipeline, options),
            description="Stage implementations",
        ))

        # src/config.ts - configuration
        files.append(GeneratedFile(
            path="src/config.ts",
            content=self._generate_config(pipeline, options),
            description="Pipeline configuration",
        ))

        # src/types.ts - type definitions
        files.append(GeneratedFile(
            path="src/types.ts",
            content=self._generate_types(pipeline, options),
            description="Type definitions",
        ))

        # src/utils.ts - utilities
        files.append(GeneratedFile(
            path="src/utils.ts",
            content=self._generate_utils(options),
            description="Utility functions",
        ))

        # package.json
        files.append(GeneratedFile(
            path="package.json",
            content=self._generate_package_json(pipeline, options, module_name),
            description="Node.js package configuration",
        ))

        # tsconfig.json
        files.append(GeneratedFile(
            path="tsconfig.json",
            content=self._generate_tsconfig(),
            description="TypeScript configuration",
        ))

        # README.md
        files.append(GeneratedFile(
            path="README.md",
            content=self._generate_readme(pipeline, options, module_name),
            description="Documentation",
        ))

        return files

    def _generate_index(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate index.ts."""
        pipeline_name = pipeline.get("name", "Generated Pipeline")
        return f'''/**
 * {pipeline_name}
 *
 * {pipeline.get("description", "")}
 *
 * Generated by FlowMason Code Generator v{self.generator_version}
 */

export {{ runPipeline, Pipeline }} from './pipeline';
export {{ PipelineConfig }} from './config';
export * from './types';
'''

    def _generate_main_code(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        standalone: bool = False,
    ) -> str:
        """Generate the main pipeline execution code."""
        stages = pipeline.get("stages", [])
        pipeline_name = pipeline.get("name", "Pipeline")

        # Build imports
        imports = self._build_imports(pipeline, options, standalone)

        # Build stage execution
        stage_code = self._build_stage_execution(stages, options)

        # Build main function
        main_func = self._build_main_function(pipeline, options, stages)

        # Combine
        code_parts = [imports]

        if options.include_comments:
            code_parts.append(f"\n// Generated from FlowMason pipeline: {pipeline_name}")
            code_parts.append(f"// Generated at: {datetime.utcnow().isoformat()}")
            code_parts.append(f"// Generator version: {self.generator_version}\n")

        if standalone:
            code_parts.append(self._generate_inline_types())
            code_parts.append(self._generate_inline_config(options))
            code_parts.append(self._generate_inline_utils(options))
            code_parts.append(self._generate_inline_stages(stages, options))

        code_parts.append(stage_code)
        code_parts.append(main_func)

        # Add CLI entry point
        code_parts.append(self._build_cli_entry(options))

        return "\n".join(code_parts)

    def _build_imports(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        standalone: bool,
    ) -> str:
        """Build import statements."""
        imports = []

        if not standalone:
            imports.append("import { PipelineConfig, getConfig } from './config';")
            imports.append("import { StageInput, StageOutput, PipelineResult } from './types';")
            imports.append("import * as stages from './stages';")
            imports.append("import { retry, withTimeout } from './utils';")

        if not options.minimal_dependencies:
            imports.append("")
            imports.append("// External dependencies")
            imports.append("import OpenAI from 'openai';")
            imports.append("import Anthropic from '@anthropic-ai/sdk';")

        return "\n".join(imports) + "\n"

    def _build_stage_execution(
        self,
        stages: List[Dict[str, Any]],
        options: CodeGenOptions,
    ) -> str:
        """Build the stage execution logic."""
        lines = []

        # Pipeline class
        lines.append("""
export interface PipelineState {
  outputs: Record<string, StageOutput>;
  variables: Record<string, any>;
}

export class Pipeline {
  private config: PipelineConfig;
  private state: PipelineState;

  constructor(config?: Partial<PipelineConfig>) {
    this.config = { ...getConfig(), ...config };
    this.state = { outputs: {}, variables: {} };
  }
""")

        # Build execution order from dependencies
        stage_order = self._resolve_execution_order(stages)

        # Generate execute method
        lines.append("  async execute(inputs: Record<string, any>): Promise<PipelineResult> {")
        lines.append("    this.state.outputs = {};")
        lines.append("    this.state.variables = { ...inputs };")
        lines.append("")

        if options.include_logging:
            lines.append("    console.log('Starting pipeline execution...');")
            lines.append("")

        # Execute each stage
        for stage_id in stage_order:
            stage = next((s for s in stages if s.get("id") == stage_id), None)
            if not stage:
                continue

            stage_name = stage.get("name", stage_id)
            func_name = self._to_camel_case(f"execute_{stage_id}")

            if options.include_logging:
                lines.append(f"    console.log('Executing stage: {stage_name}');")

            if options.include_comments:
                lines.append(f"    // Stage: {stage_name}")

            # Build stage inputs from dependencies
            depends_on = stage.get("depends_on", [])
            if depends_on:
                lines.append("    const stageInputs: StageInput = {")
                for dep in depends_on:
                    lines.append(f"      ...this.state.outputs['{dep}'],")
                lines.append("      ...this.state.variables,")
                lines.append("    };")
            else:
                lines.append("    const stageInputs: StageInput = { ...this.state.variables };")

            lines.append(f"    this.state.outputs['{stage_id}'] = await stages.{func_name}(stageInputs, this.config);")
            lines.append("")

        lines.append("    return { outputs: this.state.outputs, success: true };")
        lines.append("  }")
        lines.append("}")

        return "\n".join(lines)

    def _build_main_function(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        stages: List[Dict[str, Any]],
    ) -> str:
        """Build the main run function."""
        pipeline_name = pipeline.get("name", "Pipeline")

        return f'''
/**
 * Execute the {pipeline_name}.
 *
 * @param inputs - Pipeline input data
 * @param config - Optional configuration override
 * @returns Pipeline execution result
 */
export async function runPipeline(
  inputs: Record<string, any>,
  config?: Partial<PipelineConfig>
): Promise<PipelineResult> {{
  const pipeline = new Pipeline(config);
  return pipeline.execute(inputs);
}}
'''

    def _build_cli_entry(self, options: CodeGenOptions) -> str:
        """Build CLI entry point."""
        return '''
// CLI entry point
if (require.main === module) {
  const args = process.argv.slice(2);
  let inputs: Record<string, any> = {};

  // Parse --input argument
  const inputIdx = args.indexOf('--input');
  if (inputIdx !== -1 && args[inputIdx + 1]) {
    const inputArg = args[inputIdx + 1];
    try {
      // Try as JSON string
      inputs = JSON.parse(inputArg);
    } catch {
      // Try as file path
      const fs = require('fs');
      if (fs.existsSync(inputArg)) {
        inputs = JSON.parse(fs.readFileSync(inputArg, 'utf-8'));
      }
    }
  }

  runPipeline(inputs)
    .then(result => {
      const pretty = args.includes('--pretty');
      console.log(JSON.stringify(result, null, pretty ? 2 : undefined));
    })
    .catch(error => {
      console.error('Pipeline execution failed:', error);
      process.exit(1);
    });
}
'''

    def _generate_stages(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate stages.ts with individual stage implementations."""
        stages = pipeline.get("stages", [])
        lines = [
            '/**',
            ' * Stage implementations for the pipeline.',
            ' */',
            '',
            "import { PipelineConfig } from './config';",
            "import { StageInput, StageOutput } from './types';",
            "import OpenAI from 'openai';",
            "import Anthropic from '@anthropic-ai/sdk';",
            '',
        ]

        for stage in stages:
            stage_id = stage.get("id", "unknown")
            stage_name = stage.get("name", stage_id)
            component_type = stage.get("component_type", "unknown")
            config = stage.get("config", {})

            func_name = self._to_camel_case(f"execute_{stage_id}")

            lines.append("")
            lines.append("/**")
            lines.append(f" * Execute stage: {stage_name}")
            lines.append(f" * Component: {component_type}")
            lines.append(" */")
            lines.append(f"export async function {func_name}(")
            lines.append("  inputs: StageInput,")
            lines.append("  config: PipelineConfig")
            lines.append("): Promise<StageOutput> {")

            # Generate component-specific code
            stage_code = self._generate_component_code(component_type, config, options)
            lines.extend(["  " + line for line in stage_code.split("\n")])
            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    def _generate_component_code(
        self,
        component_type: str,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for a specific component type."""
        if component_type == "generator":
            return self._generate_generator_code(config, options)
        elif component_type == "http_request":
            return self._generate_http_code(config, options)
        elif component_type == "json_transform":
            return self._generate_transform_code(config, options)
        elif component_type == "filter":
            return self._generate_filter_code(config, options)
        elif component_type == "variable_set":
            return self._generate_variable_code(config, options)
        elif component_type == "logger":
            return self._generate_logger_code(config, options)
        else:
            return self._generate_passthrough_code(config, options)

    def _generate_generator_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for AI generator component."""
        provider = config.get("provider", "openai")
        model = config.get("model", "gpt-4")
        prompt_template = config.get("prompt", "{input}").replace("`", "\\`")
        system_prompt = config.get("system_prompt", "").replace("`", "\\`")

        lines = [
            "// Resolve prompt template",
            f"const promptTemplate = `{prompt_template}`;",
            "const prompt = promptTemplate.replace(/{(\\w+)}/g, (_, key) => inputs[key] ?? '');",
            "",
        ]

        if provider == "openai":
            lines.extend([
                "// Call OpenAI",
                "const client = new OpenAI({ apiKey: config.openaiApiKey });",
                "const messages: OpenAI.ChatCompletionMessageParam[] = [];",
            ])

            if system_prompt:
                lines.append(f"messages.push({{ role: 'system', content: `{system_prompt}` }});")

            lines.extend([
                "messages.push({ role: 'user', content: prompt });",
                "",
                "const response = await client.chat.completions.create({",
                f"  model: '{model}',",
                "  messages,",
                "});",
                "",
                "return { output: response.choices[0]?.message?.content ?? '' };",
            ])

        elif provider == "anthropic":
            lines.extend([
                "// Call Anthropic",
                "const client = new Anthropic({ apiKey: config.anthropicApiKey });",
                "",
                "const response = await client.messages.create({",
                f"  model: '{model}',",
                "  max_tokens: 4096,",
            ])

            if system_prompt:
                lines.append(f"  system: `{system_prompt}`,")

            lines.extend([
                "  messages: [{ role: 'user', content: prompt }],",
                "});",
                "",
                "const textBlock = response.content.find(b => b.type === 'text');",
                "return { output: textBlock?.text ?? '' };",
            ])

        else:
            lines.extend([
                f"// Provider: {provider}",
                "throw new Error(`Provider ${provider} not implemented`);",
            ])

        return "\n".join(lines)

    def _generate_http_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for HTTP request component."""
        method = config.get("method", "GET").upper()
        url = config.get("url", "")
        headers = config.get("headers", {})

        return f"""// HTTP Request
const url = `{url}`.replace(/{{(\\w+)}}/g, (_, key) => inputs[key] ?? '');
const headers = {json.dumps(headers)};

const response = await fetch(url, {{
  method: '{method}',
  headers,
}});

const contentType = response.headers.get('content-type') ?? '';
const body = contentType.includes('application/json')
  ? await response.json()
  : await response.text();

return {{
  statusCode: response.status,
  body,
  headers: Object.fromEntries(response.headers.entries()),
}};"""

    def _generate_transform_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for JSON transform component."""
        mapping = config.get("mapping", {})
        expression = config.get("expression", None)

        if expression:
            return f"""// Apply transformation expression
const result = (() => {{
  const inputs = arguments[0];
  return {expression};
}})(inputs);
return {{ output: result }};"""

        if mapping:
            return f"""// Apply field mapping
const mapping: Record<string, string> = {json.dumps(mapping)};
const result: Record<string, any> = {{}};

for (const [target, source] of Object.entries(mapping)) {{
  const parts = source.split('.');
  let value: any = inputs;
  for (const part of parts) {{
    value = value?.[part];
  }}
  result[target] = value;
}}

return result;"""

        return "return { ...inputs };"

    def _generate_filter_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for filter component."""
        condition = config.get("condition", "true")
        # Convert Python-style to JS-style
        js_condition = condition.replace(" and ", " && ").replace(" or ", " || ").replace("not ", "!")

        return f"""// Apply filter condition
const passed = (() => {{
  const {{ ...vars }} = inputs;
  return {js_condition};
}})();

return {{ passed, data: passed ? inputs : null }};"""

    def _generate_variable_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for variable set component."""
        variables = config.get("variables", {})
        return f"""// Set variables
const variables: Record<string, any> = {json.dumps(variables)};
const result = {{ ...inputs }};

for (const [key, value] of Object.entries(variables)) {{
  if (typeof value === 'string' && value.includes('{{')) {{
    result[key] = value.replace(/{{(\\w+)}}/g, (_, k) => inputs[k] ?? '');
  }} else {{
    result[key] = value;
  }}
}}

return result;"""

    def _generate_logger_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for logger component."""
        message = config.get("message", "{inputs}").replace("`", "\\`")
        level = config.get("level", "info")
        return f"""// Log message
const message = `{message}`.replace(/{{(\\w+)}}/g, (_, key) => inputs[key] ?? '');
console.{level}(message);
return inputs;"""

    def _generate_passthrough_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate passthrough code for unknown components."""
        return """// Passthrough - implement custom logic here
return { ...inputs };"""

    def _generate_config(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate config.ts."""
        prefix = options.secrets_prefix
        return f'''/**
 * Pipeline configuration.
 */

export interface PipelineConfig {{
  openaiApiKey?: string;
  anthropicApiKey?: string;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
}}

const defaultConfig: PipelineConfig = {{
  openaiApiKey: process.env.{prefix}OPENAI_API_KEY,
  anthropicApiKey: process.env.{prefix}ANTHROPIC_API_KEY,
  timeout: 30000,
  maxRetries: 3,
  retryDelay: 1000,
}};

export function getConfig(): PipelineConfig {{
  return {{ ...defaultConfig }};
}}
'''

    def _generate_types(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate types.ts."""
        return '''/**
 * Type definitions for the pipeline.
 */

export type StageInput = Record<string, any>;
export type StageOutput = Record<string, any>;

export interface PipelineResult {
  outputs: Record<string, StageOutput>;
  success: boolean;
  error?: string;
}

export interface StageExecutionContext {
  stageId: string;
  stageName: string;
  startTime: Date;
}
'''

    def _generate_utils(self, options: CodeGenOptions) -> str:
        """Generate utils.ts."""
        return '''/**
 * Utility functions for pipeline execution.
 */

/**
 * Retry decorator with exponential backoff.
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxAttempts: number = 3,
  delay: number = 1000,
  backoff: number = 2
): Promise<T> {
  let lastError: Error | undefined;
  let currentDelay = delay;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxAttempts - 1) {
        await new Promise(resolve => setTimeout(resolve, currentDelay));
        currentDelay *= backoff;
      }
    }
  }

  throw lastError;
}

/**
 * Timeout wrapper for async functions.
 */
export async function withTimeout<T>(
  fn: () => Promise<T>,
  timeoutMs: number
): Promise<T> {
  return Promise.race([
    fn(),
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error(`Timeout after ${timeoutMs}ms`)), timeoutMs)
    ),
  ]);
}
'''

    def _generate_inline_types(self) -> str:
        """Generate inline type definitions."""
        return '''
// Type definitions
type StageInput = Record<string, any>;
type StageOutput = Record<string, any>;

interface PipelineResult {
  outputs: Record<string, StageOutput>;
  success: boolean;
  error?: string;
}
'''

    def _generate_inline_config(self, options: CodeGenOptions) -> str:
        """Generate inline config."""
        prefix = options.secrets_prefix
        return f'''
// Configuration
interface PipelineConfig {{
  openaiApiKey?: string;
  anthropicApiKey?: string;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
}}

function getConfig(): PipelineConfig {{
  return {{
    openaiApiKey: process.env.{prefix}OPENAI_API_KEY,
    anthropicApiKey: process.env.{prefix}ANTHROPIC_API_KEY,
    timeout: 30000,
    maxRetries: 3,
    retryDelay: 1000,
  }};
}}
'''

    def _generate_inline_utils(self, options: CodeGenOptions) -> str:
        """Generate inline utilities."""
        return self._generate_utils(options)

    def _generate_inline_stages(
        self,
        stages: List[Dict[str, Any]],
        options: CodeGenOptions,
    ) -> str:
        """Generate inline stage functions."""
        lines = ["\n// Stage implementations", "const stages = {"]

        for stage in stages:
            stage_id = stage.get("id", "unknown")
            component_type = stage.get("component_type", "unknown")
            config = stage.get("config", {})

            func_name = self._to_camel_case(f"execute_{stage_id}")
            stage_code = self._generate_component_code(component_type, config, options)
            indented_code = "\n".join("    " + line for line in stage_code.split("\n"))

            lines.append(f"  {func_name}: async (inputs: StageInput, config: PipelineConfig): Promise<StageOutput> => {{")
            lines.append(indented_code)
            lines.append("  },")

        lines.append("};")
        return "\n".join(lines)

    def _generate_package_json(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> str:
        """Generate package.json."""
        pipeline_name = pipeline.get("name", module_name)
        description = pipeline.get("description", f"Generated from FlowMason pipeline: {pipeline_name}")

        deps = {
            "openai": "^4.0.0",
            "@anthropic-ai/sdk": "^0.18.0",
        }

        if options.platform == TargetPlatform.AWS_LAMBDA:
            deps["@aws-lambda-powertools/logger"] = "^1.0.0"
        elif options.platform == TargetPlatform.FIREBASE_FUNCTIONS:
            deps["firebase-admin"] = "^12.0.0"
            deps["firebase-functions"] = "^4.0.0"

        return json.dumps({
            "name": module_name,
            "version": "1.0.0",
            "description": description,
            "main": "dist/index.js",
            "types": "dist/index.d.ts",
            "scripts": {
                "build": "tsc",
                "start": "node dist/index.js",
                "dev": "ts-node src/index.ts"
            },
            "dependencies": deps,
            "devDependencies": {
                "typescript": "^5.0.0",
                "ts-node": "^10.0.0",
                "@types/node": "^20.0.0"
            }
        }, indent=2)

    def _generate_tsconfig(self) -> str:
        """Generate tsconfig.json."""
        return json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"]
        }, indent=2)

    def _generate_readme(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> str:
        """Generate README.md."""
        pipeline_name = pipeline.get("name", "Generated Pipeline")
        description = pipeline.get("description", "")

        return f"""# {pipeline_name}

{description}

## Installation

```bash
npm install
```

## Configuration

Set the following environment variables:

```bash
export FLOWMASON_OPENAI_API_KEY=your-openai-key
export FLOWMASON_ANTHROPIC_API_KEY=your-anthropic-key
```

## Usage

### Build

```bash
npm run build
```

### Run

```bash
npm start -- --input input.json --pretty
```

### Development

```bash
npm run dev -- --input '{{"your": "inputs"}}'
```

### Programmatic

```typescript
import {{ runPipeline }} from './{module_name}';

const result = await runPipeline({{ your: 'inputs' }});
console.log(result);
```

---

*Generated by FlowMason Code Generator v{self.generator_version}*
"""

    def _resolve_execution_order(self, stages: List[Dict[str, Any]]) -> List[str]:
        """Resolve stage execution order from dependencies."""
        graph: Dict[str, List[str]] = {}
        for stage in stages:
            stage_id = stage.get("id", "")
            depends_on = stage.get("depends_on", [])
            graph[stage_id] = depends_on

        order = []
        visited = set()
        visiting = set()

        def visit(node: str):
            if node in visited:
                return
            if node in visiting:
                raise ValueError(f"Circular dependency detected at {node}")
            visiting.add(node)
            for dep in graph.get(node, []):
                visit(dep)
            visiting.remove(node)
            visited.add(node)
            order.append(node)

        for stage_id in graph:
            visit(stage_id)

        return order

    def _generate_lambda_files(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate AWS Lambda specific files."""
        return [
            GeneratedFile(
                path="src/handler.ts",
                content=self._generate_lambda_handler(module_name),
                description="AWS Lambda handler",
            ),
            GeneratedFile(
                path="template.yaml",
                content=self._generate_sam_template_ts(pipeline, module_name),
                description="AWS SAM template",
            ),
        ]

    def _generate_lambda_handler(self, module_name: str) -> str:
        """Generate AWS Lambda handler."""
        return '''/**
 * AWS Lambda handler for the pipeline.
 */

import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { runPipeline } from './pipeline';

export async function handler(event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> {
  try {
    const inputs = event.body ? JSON.parse(event.body) : {};
    const result = await runPipeline(inputs);

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: String(error) }),
    };
  }
}
'''

    def _generate_sam_template_ts(self, pipeline: Dict[str, Any], module_name: str) -> str:
        """Generate AWS SAM template for TypeScript."""
        pipeline_name = pipeline.get("name", module_name)
        return f"""AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: {pipeline_name} - FlowMason Pipeline (TypeScript)

Globals:
  Function:
    Timeout: 30
    MemorySize: 256
    Runtime: nodejs20.x

Resources:
  PipelineFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: {module_name}
      Handler: dist/handler.handler
      CodeUri: .
      Environment:
        Variables:
          FLOWMASON_OPENAI_API_KEY: !Ref OpenAIApiKey
      Events:
        Api:
          Type: Api
          Properties:
            Path: /execute
            Method: post
    Metadata:
      BuildMethod: esbuild
      BuildProperties:
        Minify: true
        Target: "es2020"
        EntryPoints:
          - src/handler.ts

Parameters:
  OpenAIApiKey:
    Type: String
    NoEcho: true
    Description: OpenAI API Key

Outputs:
  ApiEndpoint:
    Description: API Gateway endpoint
    Value: !Sub "https://${{ServerlessRestApi}}.execute-api.${{AWS::Region}}.amazonaws.com/Prod/execute"
"""

    def _generate_workers_files(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate Cloudflare Workers specific files."""
        return [
            GeneratedFile(
                path="src/worker.ts",
                content=self._generate_worker_handler(module_name),
                description="Cloudflare Worker handler",
            ),
            GeneratedFile(
                path="wrangler.toml",
                content=self._generate_wrangler_config_ts(pipeline, module_name),
                description="Wrangler configuration",
            ),
        ]

    def _generate_worker_handler(self, module_name: str) -> str:
        """Generate Cloudflare Worker handler."""
        return '''/**
 * Cloudflare Worker handler for the pipeline.
 */

import { runPipeline } from './pipeline';

export interface Env {
  OPENAI_API_KEY: string;
  ANTHROPIC_API_KEY: string;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Handle CORS
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    try {
      const inputs = await request.json();
      const result = await runPipeline(inputs as Record<string, any>, {
        openaiApiKey: env.OPENAI_API_KEY,
        anthropicApiKey: env.ANTHROPIC_API_KEY,
      });

      return new Response(JSON.stringify(result), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: String(error) }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  },
};
'''

    def _generate_wrangler_config_ts(self, pipeline: Dict[str, Any], module_name: str) -> str:
        """Generate Cloudflare Wrangler config for TypeScript."""
        return f"""name = "{module_name}"
main = "src/worker.ts"
compatibility_date = "2024-01-01"

[vars]
PIPELINE_NAME = "{pipeline.get('name', module_name)}"

# Secrets (set via wrangler secret put)
# OPENAI_API_KEY
# ANTHROPIC_API_KEY
"""

    def _generate_firebase_files(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate Firebase Functions specific files."""
        return [
            GeneratedFile(
                path="src/functions.ts",
                content=self._generate_firebase_functions(pipeline, module_name),
                description="Firebase Functions entry point",
            ),
            GeneratedFile(
                path="firebase.json",
                content=self._generate_firebase_config_ts(module_name),
                description="Firebase configuration",
            ),
        ]

    def _generate_firebase_functions(self, pipeline: Dict[str, Any], module_name: str) -> str:
        """Generate Firebase Functions entry point."""
        return '''/**
 * Firebase Functions entry point.
 */

import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
import { runPipeline } from './pipeline';

admin.initializeApp();

export const executePipeline = functions.https.onRequest(async (req, res) => {
  // Handle CORS
  res.set('Access-Control-Allow-Origin', '*');

  if (req.method === 'OPTIONS') {
    res.set('Access-Control-Allow-Methods', 'POST');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    res.status(204).send('');
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const inputs = req.body || {};
    const result = await runPipeline(inputs);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
});

export const executePipelineCallable = functions.https.onCall(async (data, context) => {
  try {
    return await runPipeline(data || {});
  } catch (error) {
    throw new functions.https.HttpsError('internal', String(error));
  }
});
'''

    def _generate_firebase_config_ts(self, module_name: str) -> str:
        """Generate firebase.json for TypeScript."""
        return json.dumps({
            "functions": {
                "source": ".",
                "runtime": "nodejs20",
                "predeploy": ["npm run build"]
            },
            "emulators": {
                "functions": {"port": 5001},
                "ui": {"enabled": True}
            }
        }, indent=2)

    def _get_deployment_config(
        self,
        options: CodeGenOptions,
        module_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get deployment configuration."""
        if options.platform == TargetPlatform.AWS_LAMBDA:
            return {
                "platform": "aws_lambda",
                "runtime": "nodejs20.x",
                "handler": "dist/handler.handler",
                "deploy_command": "sam build && sam deploy --guided",
            }
        elif options.platform == TargetPlatform.CLOUDFLARE_WORKERS:
            return {
                "platform": "cloudflare_workers",
                "deploy_command": "wrangler deploy",
            }
        elif options.platform == TargetPlatform.FIREBASE_FUNCTIONS:
            return {
                "platform": "firebase_functions",
                "runtime": "nodejs20",
                "deploy_command": "firebase deploy --only functions",
            }
        return None

    def _get_deploy_instructions(
        self,
        options: CodeGenOptions,
        module_name: str,
    ) -> Optional[str]:
        """Get deployment instructions."""
        if options.platform == TargetPlatform.AWS_LAMBDA:
            return """## Deploy to AWS Lambda

1. Install AWS SAM CLI
2. Build: `sam build`
3. Deploy: `sam deploy --guided`
"""
        elif options.platform == TargetPlatform.CLOUDFLARE_WORKERS:
            return """## Deploy to Cloudflare Workers

1. Install Wrangler: `npm install -g wrangler`
2. Login: `wrangler login`
3. Set secrets: `wrangler secret put OPENAI_API_KEY`
4. Deploy: `wrangler deploy`
"""
        elif options.platform == TargetPlatform.FIREBASE_FUNCTIONS:
            return f"""## Deploy to Firebase Functions

1. Install Firebase CLI: `npm install -g firebase-tools`
2. Login: `firebase login`
3. Init: `firebase init functions`
4. Deploy: `firebase deploy --only functions`
"""
        return None


# Singleton instance
_generator: Optional[TypeScriptCodeGenerator] = None


def get_typescript_code_generator() -> TypeScriptCodeGenerator:
    """Get the singleton TypeScriptCodeGenerator instance."""
    global _generator
    if _generator is None:
        _generator = TypeScriptCodeGenerator()
    return _generator
