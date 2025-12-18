"""
Python Code Generator Service.

Generates standalone Python code from FlowMason pipelines.
"""

import json
import textwrap
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flowmason_studio.models.codegen import (
    CodeGenOptions,
    CodeGenResult,
    GeneratedFile,
    OutputFormat,
    TargetPlatform,
)


class PythonCodeGenerator:
    """Generates Python code from pipeline definitions."""

    def __init__(self):
        """Initialize the code generator."""
        self.generator_version = "1.0.0"

    def generate(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> CodeGenResult:
        """
        Generate Python code from a pipeline definition.

        Args:
            pipeline: Pipeline configuration dictionary
            options: Code generation options

        Returns:
            CodeGenResult with generated files
        """
        gen_id = str(uuid.uuid4())
        pipeline_id = pipeline.get("id", "pipeline")
        pipeline_name = pipeline.get("name", "generated_pipeline")

        # Sanitize name for Python
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
        elif options.platform == TargetPlatform.DOCKER:
            files.extend(self._generate_docker_files(pipeline, options, module_name))

        # Calculate stats
        total_lines = sum(
            len(f.content.split("\n")) for f in files if not f.is_binary
        )

        # Determine entry point
        entry_point = f"{module_name}/main.py" if options.output_format == OutputFormat.PACKAGE else f"{module_name}.py"

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
        """Convert name to valid Python identifier."""
        # Replace hyphens and spaces with underscores
        name = name.replace("-", "_").replace(" ", "_")
        # Remove invalid characters
        name = "".join(c for c in name if c.isalnum() or c == "_")
        # Ensure doesn't start with number
        if name and name[0].isdigit():
            name = f"pipeline_{name}"
        return name.lower() or "pipeline"

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
                path=f"{module_name}.py",
                content=code,
                description="Complete pipeline implementation",
                executable=True,
            ),
            GeneratedFile(
                path="requirements.txt",
                content=self._generate_requirements(pipeline, options),
                description="Python dependencies",
            ),
        ]

    def _generate_package(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate a proper Python package."""
        files = []

        # __init__.py
        files.append(GeneratedFile(
            path=f"{module_name}/__init__.py",
            content=self._generate_init(pipeline, options),
            description="Package initialization",
        ))

        # main.py - entry point
        files.append(GeneratedFile(
            path=f"{module_name}/main.py",
            content=self._generate_main_code(pipeline, options, standalone=False),
            description="Main pipeline execution",
            executable=True,
        ))

        # stages.py - stage implementations
        files.append(GeneratedFile(
            path=f"{module_name}/stages.py",
            content=self._generate_stages(pipeline, options),
            description="Stage implementations",
        ))

        # config.py - configuration
        files.append(GeneratedFile(
            path=f"{module_name}/config.py",
            content=self._generate_config(pipeline, options),
            description="Pipeline configuration",
        ))

        # utils.py - utilities
        files.append(GeneratedFile(
            path=f"{module_name}/utils.py",
            content=self._generate_utils(options),
            description="Utility functions",
        ))

        # requirements.txt
        files.append(GeneratedFile(
            path="requirements.txt",
            content=self._generate_requirements(pipeline, options),
            description="Python dependencies",
        ))

        # README.md
        files.append(GeneratedFile(
            path="README.md",
            content=self._generate_readme(pipeline, options, module_name),
            description="Documentation",
        ))

        # pyproject.toml
        files.append(GeneratedFile(
            path="pyproject.toml",
            content=self._generate_pyproject(pipeline, options, module_name),
            description="Project configuration",
        ))

        return files

    def _generate_init(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate __init__.py."""
        pipeline_name = pipeline.get("name", "Generated Pipeline")
        lines = []

        if options.include_docstrings:
            lines.append(f'"""{pipeline_name}\n')
            if pipeline.get("description"):
                lines.append(f'{pipeline["description"]}\n')
            lines.append('"""\n')

        lines.append("from .main import run_pipeline, Pipeline\n")
        lines.append("from .config import PipelineConfig\n")
        lines.append("\n__version__ = '1.0.0'\n")
        lines.append(f"__pipeline_name__ = '{pipeline_name}'\n")

        return "".join(lines)

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

        # Build stage execution code
        stage_code = self._build_stage_execution(stages, options)

        # Build main function
        main_func = self._build_main_function(pipeline, options, stages)

        # Combine
        code_parts = [imports]

        if options.include_comments:
            code_parts.append(f"\n# Generated from FlowMason pipeline: {pipeline_name}")
            code_parts.append(f"# Generated at: {datetime.utcnow().isoformat()}")
            code_parts.append(f"# Generator version: {self.generator_version}\n")

        if standalone:
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
        imports = [
            "import os",
            "import json",
        ]

        if options.async_mode:
            imports.append("import asyncio")

        if options.include_logging:
            imports.append("import logging")

        imports.append("from typing import Any, Dict, Optional")
        imports.append("from dataclasses import dataclass, field")

        if not options.minimal_dependencies:
            # Standard AI/HTTP libraries
            imports.append("\ntry:")
            imports.append("    import httpx")
            imports.append("except ImportError:")
            imports.append("    httpx = None")
            imports.append("\ntry:")
            imports.append("    from openai import OpenAI, AsyncOpenAI")
            imports.append("except ImportError:")
            imports.append("    OpenAI = None")
            imports.append("    AsyncOpenAI = None")
            imports.append("\ntry:")
            imports.append("    import anthropic")
            imports.append("except ImportError:")
            imports.append("    anthropic = None")

        if not standalone:
            imports.append("\nfrom .config import PipelineConfig")
            imports.append("from .stages import *")
            imports.append("from .utils import retry, with_timeout")

        return "\n".join(imports) + "\n"

    def _build_stage_execution(
        self,
        stages: List[Dict[str, Any]],
        options: CodeGenOptions,
    ) -> str:
        """Build the stage execution logic."""
        lines = []

        if options.include_logging:
            lines.append("\nlogger = logging.getLogger(__name__)\n")

        # Pipeline class
        lines.append("\n@dataclass")
        lines.append("class Pipeline:")
        if options.include_docstrings:
            lines.append('    """Pipeline execution context."""')
        lines.append("    config: 'PipelineConfig' = field(default_factory=lambda: PipelineConfig())")
        lines.append("    outputs: Dict[str, Any] = field(default_factory=dict)")
        lines.append("    variables: Dict[str, Any] = field(default_factory=dict)")
        lines.append("")

        # Build execution order from dependencies
        stage_order = self._resolve_execution_order(stages)

        # Generate execute method
        if options.async_mode:
            lines.append("    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:")
        else:
            lines.append("    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:")

        if options.include_docstrings:
            lines.append('        """Execute the pipeline with given inputs."""')

        lines.append("        self.outputs = {}")
        lines.append("        self.variables = dict(inputs)")
        lines.append("")

        # Execute each stage
        for stage_id in stage_order:
            stage = next((s for s in stages if s.get("id") == stage_id), None)
            if not stage:
                continue

            stage_name = stage.get("name", stage_id)
            component_type = stage.get("component_type", "unknown")

            if options.include_logging:
                lines.append(f"        logger.info('Executing stage: {stage_name}')")

            if options.include_comments:
                lines.append(f"        # Stage: {stage_name} ({component_type})")

            # Build stage inputs from dependencies
            depends_on = stage.get("depends_on", [])
            if depends_on:
                lines.append(f"        stage_inputs = {{}}")
                for dep in depends_on:
                    lines.append(f"        stage_inputs.update(self.outputs.get('{dep}', {{}}))")
                lines.append("        stage_inputs.update(self.variables)")
            else:
                lines.append("        stage_inputs = dict(self.variables)")

            # Execute stage
            func_name = f"execute_{self._sanitize_name(stage_id)}"
            if options.async_mode:
                lines.append(f"        self.outputs['{stage_id}'] = await {func_name}(stage_inputs, self.config)")
            else:
                lines.append(f"        self.outputs['{stage_id}'] = {func_name}(stage_inputs, self.config)")
            lines.append("")

        # Return final outputs
        lines.append("        return self.outputs")
        lines.append("")

        return "\n".join(lines)

    def _build_main_function(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        stages: List[Dict[str, Any]],
    ) -> str:
        """Build the main run function."""
        lines = []

        if options.async_mode:
            lines.append("\nasync def run_pipeline(")
        else:
            lines.append("\ndef run_pipeline(")

        lines.append("    inputs: Dict[str, Any],")
        lines.append("    config: Optional['PipelineConfig'] = None,")
        lines.append(") -> Dict[str, Any]:")

        if options.include_docstrings:
            pipeline_name = pipeline.get("name", "Pipeline")
            lines.append(f'    """')
            lines.append(f"    Execute the {pipeline_name}.")
            lines.append(f"    ")
            lines.append(f"    Args:")
            lines.append(f"        inputs: Pipeline input data")
            lines.append(f"        config: Optional configuration override")
            lines.append(f"    ")
            lines.append(f"    Returns:")
            lines.append(f"        Dictionary of stage outputs")
            lines.append(f'    """')

        lines.append("    if config is None:")
        lines.append("        config = PipelineConfig()")
        lines.append("")
        lines.append("    pipeline = Pipeline(config=config)")

        if options.async_mode:
            lines.append("    return await pipeline.execute(inputs)")
        else:
            lines.append("    return pipeline.execute(inputs)")

        lines.append("")

        return "\n".join(lines)

    def _build_cli_entry(self, options: CodeGenOptions) -> str:
        """Build CLI entry point."""
        lines = [
            "",
            "if __name__ == '__main__':",
            "    import argparse",
            "    import sys",
            "",
            "    parser = argparse.ArgumentParser(description='Run the pipeline')",
            "    parser.add_argument('--input', '-i', type=str, help='JSON input file or string')",
            "    parser.add_argument('--output', '-o', type=str, help='Output file (default: stdout)')",
            "    parser.add_argument('--pretty', action='store_true', help='Pretty print output')",
            "    args = parser.parse_args()",
            "",
            "    # Parse input",
            "    if args.input:",
            "        if os.path.isfile(args.input):",
            "            with open(args.input) as f:",
            "                inputs = json.load(f)",
            "        else:",
            "            inputs = json.loads(args.input)",
            "    else:",
            "        inputs = {}",
            "",
        ]

        if options.include_logging:
            lines.extend([
                "    # Setup logging",
                "    logging.basicConfig(",
                "        level=logging.INFO,",
                "        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'",
                "    )",
                "",
            ])

        lines.extend([
            "    # Run pipeline",
        ])

        if options.async_mode:
            lines.append("    result = asyncio.run(run_pipeline(inputs))")
        else:
            lines.append("    result = run_pipeline(inputs)")

        lines.extend([
            "",
            "    # Output result",
            "    indent = 2 if args.pretty else None",
            "    output = json.dumps(result, indent=indent, default=str)",
            "",
            "    if args.output:",
            "        with open(args.output, 'w') as f:",
            "            f.write(output)",
            "    else:",
            "        print(output)",
        ])

        return "\n".join(lines)

    def _generate_stages(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate stages.py with individual stage implementations."""
        stages = pipeline.get("stages", [])
        lines = [
            '"""Stage implementations for the pipeline."""',
            "",
            "from typing import Any, Dict",
        ]

        if options.async_mode:
            lines.append("import asyncio")

        lines.append("")

        for stage in stages:
            stage_id = stage.get("id", "unknown")
            stage_name = stage.get("name", stage_id)
            component_type = stage.get("component_type", "unknown")
            config = stage.get("config", {})

            func_name = f"execute_{self._sanitize_name(stage_id)}"

            lines.append("")
            if options.async_mode:
                lines.append(f"async def {func_name}(")
            else:
                lines.append(f"def {func_name}(")

            lines.append("    inputs: Dict[str, Any],")
            lines.append("    config: 'PipelineConfig',")
            lines.append(") -> Dict[str, Any]:")

            if options.include_docstrings:
                lines.append(f'    """')
                lines.append(f"    Execute stage: {stage_name}")
                lines.append(f"    Component: {component_type}")
                lines.append(f'    """')

            # Generate component-specific code
            stage_code = self._generate_component_code(component_type, config, options)
            lines.extend(["    " + line for line in stage_code.split("\n")])
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
        prompt_template = config.get("prompt", "{input}")
        system_prompt = config.get("system_prompt", "")

        lines = [
            "# Resolve prompt template",
            f"prompt_template = '''{prompt_template}'''",
            "prompt = prompt_template.format(**inputs)",
            "",
        ]

        if provider == "openai":
            if options.async_mode:
                lines.extend([
                    "# Call OpenAI",
                    "client = AsyncOpenAI(api_key=config.openai_api_key)",
                    "messages = []",
                ])
            else:
                lines.extend([
                    "# Call OpenAI",
                    "client = OpenAI(api_key=config.openai_api_key)",
                    "messages = []",
                ])

            if system_prompt:
                lines.append(f"messages.append({{'role': 'system', 'content': '''{system_prompt}'''}})")

            lines.append("messages.append({'role': 'user', 'content': prompt})")
            lines.append("")

            if options.async_mode:
                lines.append("response = await client.chat.completions.create(")
            else:
                lines.append("response = client.chat.completions.create(")

            lines.extend([
                f"    model='{model}',",
                "    messages=messages,",
                ")",
                "",
                "return {'output': response.choices[0].message.content}",
            ])

        elif provider == "anthropic":
            if options.async_mode:
                lines.extend([
                    "# Call Anthropic",
                    "client = anthropic.AsyncAnthropic(api_key=config.anthropic_api_key)",
                ])
            else:
                lines.extend([
                    "# Call Anthropic",
                    "client = anthropic.Anthropic(api_key=config.anthropic_api_key)",
                ])

            if options.async_mode:
                lines.append("response = await client.messages.create(")
            else:
                lines.append("response = client.messages.create(")

            lines.extend([
                f"    model='{model}',",
                "    max_tokens=4096,",
            ])

            if system_prompt:
                lines.append(f"    system='''{system_prompt}''',")

            lines.extend([
                "    messages=[{'role': 'user', 'content': prompt}],",
                ")",
                "",
                "return {'output': response.content[0].text}",
            ])

        else:
            lines.extend([
                f"# Provider: {provider}",
                "raise NotImplementedError(f'Provider {provider} not implemented')",
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

        lines = [
            f"url = '{url}'.format(**inputs)",
            f"headers = {json.dumps(headers)}",
            "",
        ]

        if options.async_mode:
            lines.extend([
                "async with httpx.AsyncClient() as client:",
                f"    response = await client.{method.lower()}(url, headers=headers)",
            ])
        else:
            lines.extend([
                "with httpx.Client() as client:",
                f"    response = client.{method.lower()}(url, headers=headers)",
            ])

        lines.extend([
            "",
            "return {",
            "    'status_code': response.status_code,",
            "    'body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,",
            "    'headers': dict(response.headers),",
            "}",
        ])

        return "\n".join(lines)

    def _generate_transform_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for JSON transform component."""
        mapping = config.get("mapping", {})
        expression = config.get("expression", None)

        if expression:
            return f"""# Apply transformation expression
result = eval('''{expression}''', {{'inputs': inputs}})
return {{'output': result}}"""

        if mapping:
            return f"""# Apply field mapping
mapping = {json.dumps(mapping)}
result = {{}}
for target, source in mapping.items():
    # Resolve source path
    value = inputs
    for part in source.split('.'):
        value = value.get(part, {{}}) if isinstance(value, dict) else {{}}
    result[target] = value
return result"""

        return "return dict(inputs)"

    def _generate_filter_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for filter component."""
        condition = config.get("condition", "True")
        return f"""# Apply filter condition
condition = '''{condition}'''
passed = eval(condition, {{'inputs': inputs, **inputs}})
return {{'passed': passed, 'data': inputs if passed else None}}"""

    def _generate_variable_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for variable set component."""
        variables = config.get("variables", {})
        return f"""# Set variables
variables = {json.dumps(variables)}
result = dict(inputs)
for key, value in variables.items():
    if isinstance(value, str) and '{{' in value:
        result[key] = value.format(**inputs)
    else:
        result[key] = value
return result"""

    def _generate_logger_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for logger component."""
        message = config.get("message", "{inputs}")
        level = config.get("level", "info")
        return f"""import logging
logger = logging.getLogger(__name__)
message = '''{message}'''.format(**inputs)
logger.{level}(message)
return inputs"""

    def _generate_passthrough_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate passthrough code for unknown components."""
        return """# Passthrough - implement custom logic here
return dict(inputs)"""

    def _generate_config(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate config.py."""
        lines = [
            '"""Pipeline configuration."""',
            "",
            "import os",
            "from dataclasses import dataclass, field",
            "from typing import Optional",
            "",
            "",
            "@dataclass",
            "class PipelineConfig:",
            '    """Configuration for pipeline execution."""',
            "",
        ]

        prefix = options.secrets_prefix

        # Add API key configs
        lines.append(f"    openai_api_key: Optional[str] = field(")
        lines.append(f"        default_factory=lambda: os.environ.get('{prefix}OPENAI_API_KEY')")
        lines.append("    )")
        lines.append(f"    anthropic_api_key: Optional[str] = field(")
        lines.append(f"        default_factory=lambda: os.environ.get('{prefix}ANTHROPIC_API_KEY')")
        lines.append("    )")
        lines.append("")

        # Add other common configs
        lines.append("    timeout: int = 30")
        lines.append("    max_retries: int = 3")
        lines.append("    retry_delay: float = 1.0")
        lines.append("")

        return "\n".join(lines)

    def _generate_utils(self, options: CodeGenOptions) -> str:
        """Generate utils.py."""
        lines = [
            '"""Utility functions for pipeline execution."""',
            "",
            "import asyncio",
            "import functools",
            "import time",
            "from typing import Callable, TypeVar",
            "",
            "T = TypeVar('T')",
            "",
        ]

        if options.include_retry_logic:
            lines.extend([
                "",
                "def retry(",
                "    max_attempts: int = 3,",
                "    delay: float = 1.0,",
                "    backoff: float = 2.0,",
                "    exceptions: tuple = (Exception,),",
                "):",
                '    """Retry decorator with exponential backoff."""',
                "    def decorator(func: Callable[..., T]) -> Callable[..., T]:",
                "        @functools.wraps(func)",
                "        async def async_wrapper(*args, **kwargs):",
                "            last_exception = None",
                "            current_delay = delay",
                "            for attempt in range(max_attempts):",
                "                try:",
                "                    return await func(*args, **kwargs)",
                "                except exceptions as e:",
                "                    last_exception = e",
                "                    if attempt < max_attempts - 1:",
                "                        await asyncio.sleep(current_delay)",
                "                        current_delay *= backoff",
                "            raise last_exception",
                "",
                "        @functools.wraps(func)",
                "        def sync_wrapper(*args, **kwargs):",
                "            last_exception = None",
                "            current_delay = delay",
                "            for attempt in range(max_attempts):",
                "                try:",
                "                    return func(*args, **kwargs)",
                "                except exceptions as e:",
                "                    last_exception = e",
                "                    if attempt < max_attempts - 1:",
                "                        time.sleep(current_delay)",
                "                        current_delay *= backoff",
                "            raise last_exception",
                "",
                "        if asyncio.iscoroutinefunction(func):",
                "            return async_wrapper",
                "        return sync_wrapper",
                "    return decorator",
                "",
            ])

        lines.extend([
            "",
            "def with_timeout(seconds: float):",
            '    """Timeout decorator for async functions."""',
            "    def decorator(func):",
            "        @functools.wraps(func)",
            "        async def wrapper(*args, **kwargs):",
            "            return await asyncio.wait_for(",
            "                func(*args, **kwargs),",
            "                timeout=seconds",
            "            )",
            "        return wrapper",
            "    return decorator",
            "",
        ])

        return "\n".join(lines)

    def _generate_inline_utils(self, options: CodeGenOptions) -> str:
        """Generate inline utility functions for single-file mode."""
        return self._generate_utils(options)

    def _generate_inline_stages(
        self,
        stages: List[Dict[str, Any]],
        options: CodeGenOptions,
    ) -> str:
        """Generate inline stage functions for single-file mode."""
        lines = ["\n# Stage Implementations\n"]

        for stage in stages:
            stage_id = stage.get("id", "unknown")
            component_type = stage.get("component_type", "unknown")
            config = stage.get("config", {})

            func_name = f"execute_{self._sanitize_name(stage_id)}"

            if options.async_mode:
                lines.append(f"async def {func_name}(inputs: Dict[str, Any], config: 'PipelineConfig') -> Dict[str, Any]:")
            else:
                lines.append(f"def {func_name}(inputs: Dict[str, Any], config: 'PipelineConfig') -> Dict[str, Any]:")

            stage_code = self._generate_component_code(component_type, config, options)
            lines.extend(["    " + line for line in stage_code.split("\n")])
            lines.append("")

        # Add PipelineConfig inline
        lines.extend([
            "",
            "@dataclass",
            "class PipelineConfig:",
            "    openai_api_key: Optional[str] = field(default_factory=lambda: os.environ.get('OPENAI_API_KEY'))",
            "    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.environ.get('ANTHROPIC_API_KEY'))",
            "    timeout: int = 30",
            "    max_retries: int = 3",
            "",
        ])

        return "\n".join(lines)

    def _generate_requirements(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate requirements.txt."""
        deps = []

        # Core dependencies
        if not options.minimal_dependencies:
            deps.append("httpx>=0.25.0")
            deps.append("openai>=1.0.0")
            deps.append("anthropic>=0.18.0")

        # Platform-specific
        if options.platform == TargetPlatform.AWS_LAMBDA:
            deps.append("aws-lambda-powertools>=2.0.0")
        elif options.platform == TargetPlatform.AZURE_FUNCTIONS:
            deps.append("azure-functions>=1.0.0")
        elif options.platform == TargetPlatform.FIREBASE_FUNCTIONS:
            deps.append("firebase-functions>=0.4.0")
            deps.append("firebase-admin>=6.0.0")

        if options.pin_versions:
            return "\n".join(deps)
        else:
            return "\n".join(d.split(">=")[0] for d in deps)

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
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
export FLOWMASON_OPENAI_API_KEY=your-openai-key
export FLOWMASON_ANTHROPIC_API_KEY=your-anthropic-key
```

## Usage

### Command Line

```bash
python -m {module_name}.main --input input.json --output output.json
```

### Python

```python
from {module_name} import run_pipeline
import asyncio

result = asyncio.run(run_pipeline({{"your": "inputs"}}))
print(result)
```

## Generated Files

- `{module_name}/main.py` - Main pipeline execution
- `{module_name}/stages.py` - Stage implementations
- `{module_name}/config.py` - Configuration
- `{module_name}/utils.py` - Utility functions

---

*Generated by FlowMason Code Generator v{self.generator_version}*
"""

    def _generate_pyproject(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> str:
        """Generate pyproject.toml."""
        pipeline_name = pipeline.get("name", "generated-pipeline")

        return f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{module_name}"
version = "1.0.0"
description = "Generated from FlowMason pipeline: {pipeline_name}"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "httpx>=0.25.0",
    "openai>=1.0.0",
    "anthropic>=0.18.0",
]

[project.scripts]
{module_name} = "{module_name}.main:main"
"""

    def _resolve_execution_order(self, stages: List[Dict[str, Any]]) -> List[str]:
        """Resolve stage execution order from dependencies."""
        # Build dependency graph
        graph: Dict[str, List[str]] = {}
        for stage in stages:
            stage_id = stage.get("id", "")
            depends_on = stage.get("depends_on", [])
            graph[stage_id] = depends_on

        # Topological sort
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
                path="handler.py",
                content=self._generate_lambda_handler(module_name, options),
                description="AWS Lambda handler",
            ),
            GeneratedFile(
                path="template.yaml",
                content=self._generate_sam_template(pipeline, module_name),
                description="AWS SAM template",
            ),
        ]

    def _generate_lambda_handler(self, module_name: str, options: CodeGenOptions) -> str:
        """Generate AWS Lambda handler."""
        return f'''"""AWS Lambda handler for the pipeline."""

import json
import asyncio
from {module_name} import run_pipeline


def handler(event, context):
    """Lambda handler function."""
    # Parse input
    if isinstance(event.get("body"), str):
        inputs = json.loads(event["body"])
    else:
        inputs = event.get("body", event)

    # Run pipeline
    result = asyncio.run(run_pipeline(inputs))

    return {{
        "statusCode": 200,
        "headers": {{"Content-Type": "application/json"}},
        "body": json.dumps(result, default=str)
    }}
'''

    def _generate_sam_template(self, pipeline: Dict[str, Any], module_name: str) -> str:
        """Generate AWS SAM template."""
        pipeline_name = pipeline.get("name", module_name)
        return f"""AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: {pipeline_name} - FlowMason Pipeline

Globals:
  Function:
    Timeout: 30
    MemorySize: 256
    Runtime: python3.11

Resources:
  PipelineFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: {module_name}
      Handler: handler.handler
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
                path="wrangler.toml",
                content=self._generate_wrangler_config(pipeline, module_name),
                description="Wrangler configuration",
            ),
        ]

    def _generate_wrangler_config(self, pipeline: Dict[str, Any], module_name: str) -> str:
        """Generate Cloudflare Wrangler config."""
        return f"""name = "{module_name}"
main = "worker.py"
compatibility_date = "2024-01-01"

[vars]
PIPELINE_NAME = "{pipeline.get('name', module_name)}"
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
                path="main.py",
                content=self._generate_firebase_main(pipeline, module_name, options),
                description="Firebase Functions entry point",
            ),
            GeneratedFile(
                path="firebase.json",
                content=self._generate_firebase_config(pipeline, module_name),
                description="Firebase configuration",
            ),
            GeneratedFile(
                path=".firebaserc",
                content=self._generate_firebaserc(module_name),
                description="Firebase project configuration",
            ),
        ]

    def _generate_firebase_main(
        self,
        pipeline: Dict[str, Any],
        module_name: str,
        options: CodeGenOptions,
    ) -> str:
        """Generate Firebase Functions main.py entry point."""
        pipeline_name = pipeline.get("name", module_name)
        return f'''"""
Firebase Cloud Functions entry point for {pipeline_name}.

Generated by FlowMason Code Generator
"""

import json
import asyncio
from firebase_functions import https_fn, options as fn_options
from firebase_admin import initialize_app

# Initialize Firebase Admin
initialize_app()

# Import the pipeline
from {module_name} import run_pipeline


# Configure function options
fn_options.set_global_options(
    max_instances=10,
    memory=fn_options.MemoryOption.MB_256,
    timeout_sec=60,
    region="us-central1",
)


@https_fn.on_request()
def execute_pipeline(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP endpoint to execute the pipeline.

    Accepts POST requests with JSON body containing pipeline inputs.
    Returns JSON response with pipeline outputs.
    """
    # Handle CORS preflight
    if req.method == "OPTIONS":
        headers = {{
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }}
        return https_fn.Response("", status=204, headers=headers)

    # Only accept POST requests
    if req.method != "POST":
        return https_fn.Response(
            json.dumps({{"error": "Method not allowed"}}),
            status=405,
            headers={{"Content-Type": "application/json"}},
        )

    try:
        # Parse input
        inputs = req.get_json(silent=True) or {{}}

        # Run pipeline
        result = asyncio.run(run_pipeline(inputs))

        # Return success response
        return https_fn.Response(
            json.dumps(result, default=str),
            status=200,
            headers={{
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }},
        )

    except Exception as e:
        # Return error response
        return https_fn.Response(
            json.dumps({{"error": str(e)}}),
            status=500,
            headers={{
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            }},
        )


@https_fn.on_call()
def execute_pipeline_callable(req: https_fn.CallableRequest) -> dict:
    """
    Callable function for Firebase SDK clients.

    Can be called directly from Firebase client SDKs.
    """
    try:
        inputs = req.data or {{}}
        result = asyncio.run(run_pipeline(inputs))
        return result
    except Exception as e:
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.INTERNAL,
            message=str(e),
        )
'''

    def _generate_firebase_config(
        self,
        pipeline: Dict[str, Any],
        module_name: str,
    ) -> str:
        """Generate firebase.json configuration."""
        pipeline_name = pipeline.get("name", module_name)
        return f'''{{
  "functions": [
    {{
      "source": ".",
      "codebase": "{module_name}",
      "runtime": "python311",
      "ignore": [
        "venv",
        ".git",
        "firebase-debug.log",
        "firebase-debug.*.log",
        "__pycache__",
        "*.pyc"
      ]
    }}
  ],
  "hosting": {{
    "public": "public",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {{
        "source": "/api/**",
        "function": "execute_pipeline"
      }}
    ]
  }},
  "emulators": {{
    "functions": {{
      "port": 5001
    }},
    "hosting": {{
      "port": 5000
    }},
    "ui": {{
      "enabled": true
    }}
  }}
}}
'''

    def _generate_firebaserc(self, module_name: str) -> str:
        """Generate .firebaserc project configuration."""
        return f'''{{
  "projects": {{
    "default": "{module_name}-project"
  }}
}}
'''

    def _generate_docker_files(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate Docker specific files."""
        return [
            GeneratedFile(
                path="Dockerfile",
                content=self._generate_dockerfile(module_name),
                description="Docker build file",
            ),
            GeneratedFile(
                path="docker-compose.yml",
                content=self._generate_docker_compose(pipeline, module_name),
                description="Docker Compose configuration",
            ),
        ]

    def _generate_dockerfile(self, module_name: str) -> str:
        """Generate Dockerfile."""
        return f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY {module_name}/ {module_name}/

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "{module_name}.main"]
"""

    def _generate_docker_compose(self, pipeline: Dict[str, Any], module_name: str) -> str:
        """Generate docker-compose.yml."""
        return f"""version: '3.8'

services:
  pipeline:
    build: .
    environment:
      - FLOWMASON_OPENAI_API_KEY=${{OPENAI_API_KEY}}
      - FLOWMASON_ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY}}
    volumes:
      - ./data:/app/data
"""

    def _get_deployment_config(
        self,
        options: CodeGenOptions,
        module_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get deployment configuration for the target platform."""
        if options.platform == TargetPlatform.AWS_LAMBDA:
            return {
                "platform": "aws_lambda",
                "runtime": "python3.11",
                "handler": "handler.handler",
                "deploy_command": "sam deploy --guided",
            }
        elif options.platform == TargetPlatform.CLOUDFLARE_WORKERS:
            return {
                "platform": "cloudflare_workers",
                "deploy_command": "wrangler deploy",
            }
        elif options.platform == TargetPlatform.FIREBASE_FUNCTIONS:
            return {
                "platform": "firebase_functions",
                "runtime": "python311",
                "deploy_command": "firebase deploy --only functions",
                "emulator_command": "firebase emulators:start",
                "functions": ["execute_pipeline", "execute_pipeline_callable"],
            }
        elif options.platform == TargetPlatform.DOCKER:
            return {
                "platform": "docker",
                "build_command": "docker build -t " + module_name + " .",
                "run_command": f"docker run -it {module_name}",
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

1. Install AWS SAM CLI: https://docs.aws.amazon.com/serverless-application-model/
2. Configure AWS credentials: `aws configure`
3. Build: `sam build`
4. Deploy: `sam deploy --guided`
"""
        elif options.platform == TargetPlatform.CLOUDFLARE_WORKERS:
            return """## Deploy to Cloudflare Workers

1. Install Wrangler: `npm install -g wrangler`
2. Login: `wrangler login`
3. Deploy: `wrangler deploy`
"""
        elif options.platform == TargetPlatform.FIREBASE_FUNCTIONS:
            return f"""## Deploy to Firebase Functions

### Prerequisites
1. Install Firebase CLI: `npm install -g firebase-tools`
2. Login: `firebase login`
3. Create a project: `firebase projects:create {module_name}-project`

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Start emulators: `firebase emulators:start`
3. Test locally at: http://localhost:5001/{module_name}-project/us-central1/execute_pipeline

### Environment Variables
Set secrets using Firebase:
```bash
firebase functions:secrets:set OPENAI_API_KEY
firebase functions:secrets:set ANTHROPIC_API_KEY
```

### Deployment
1. Initialize Firebase (first time): `firebase init functions`
2. Deploy: `firebase deploy --only functions`

### Usage
- HTTP Endpoint: POST to https://us-central1-{module_name}-project.cloudfunctions.net/execute_pipeline
- Callable: Use Firebase SDK to call `execute_pipeline_callable`

### Monitoring
- View logs: `firebase functions:log`
- Console: https://console.firebase.google.com
"""
        elif options.platform == TargetPlatform.DOCKER:
            return f"""## Deploy with Docker

1. Build: `docker build -t {module_name} .`
2. Run: `docker run -it --env-file .env {module_name}`
"""
        return None


# Singleton instance
_generator: Optional[PythonCodeGenerator] = None


def get_python_code_generator() -> PythonCodeGenerator:
    """Get the singleton PythonCodeGenerator instance."""
    global _generator
    if _generator is None:
        _generator = PythonCodeGenerator()
    return _generator
