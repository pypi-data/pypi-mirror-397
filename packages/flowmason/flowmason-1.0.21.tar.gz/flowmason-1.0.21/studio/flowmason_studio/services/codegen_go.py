"""
Go Code Generator Service.

Generates standalone Go code from FlowMason pipelines.
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


class GoCodeGenerator:
    """Generates Go code from pipeline definitions."""

    def __init__(self):
        """Initialize the code generator."""
        self.generator_version = "1.0.0"

    def generate(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> CodeGenResult:
        """
        Generate Go code from a pipeline definition.

        Args:
            pipeline: Pipeline configuration dictionary
            options: Code generation options

        Returns:
            CodeGenResult with generated files
        """
        gen_id = str(uuid.uuid4())
        pipeline_id = pipeline.get("id", "pipeline")
        pipeline_name = pipeline.get("name", "generated_pipeline")

        # Sanitize name for Go
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
        elif options.platform == TargetPlatform.DOCKER:
            files.extend(self._generate_docker_files(pipeline, options, module_name))

        # Calculate stats
        total_lines = sum(
            len(f.content.split("\n")) for f in files if not f.is_binary
        )

        # Determine entry point
        entry_point = "main.go" if options.output_format == OutputFormat.SINGLE_FILE else "cmd/main.go"

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
        """Convert name to valid Go package name."""
        # Replace hyphens and spaces with underscores
        name = name.replace(" ", "_").replace("-", "_")
        # Remove invalid characters
        name = "".join(c for c in name if c.isalnum() or c == "_")
        # Go convention: lowercase package names
        name = name.lower()
        # Ensure doesn't start with number
        if name and name[0].isdigit():
            name = f"pipeline_{name}"
        return name or "pipeline"

    def _to_pascal_case(self, name: str) -> str:
        """Convert to PascalCase for exported functions."""
        parts = name.lower().split("_")
        return "".join(p.capitalize() for p in parts)

    def _to_camel_case(self, name: str) -> str:
        """Convert to camelCase."""
        parts = name.lower().split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    def _generate_single_file(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate all code in a single file."""
        code = self._generate_main_go(pipeline, options, standalone=True)

        return [
            GeneratedFile(
                path="main.go",
                content=code,
                description="Complete pipeline implementation",
                executable=True,
            ),
            GeneratedFile(
                path="go.mod",
                content=self._generate_go_mod(module_name),
                description="Go module file",
            ),
        ]

    def _generate_package(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate a proper Go package structure."""
        files = []

        # cmd/main.go - entry point
        files.append(GeneratedFile(
            path="cmd/main.go",
            content=self._generate_cmd_main(pipeline, options, module_name),
            description="Main entry point",
            executable=True,
        ))

        # internal/pipeline/pipeline.go - main pipeline
        files.append(GeneratedFile(
            path="internal/pipeline/pipeline.go",
            content=self._generate_pipeline_go(pipeline, options),
            description="Pipeline execution logic",
        ))

        # internal/stages/stages.go - stage implementations
        files.append(GeneratedFile(
            path="internal/stages/stages.go",
            content=self._generate_stages_go(pipeline, options),
            description="Stage implementations",
        ))

        # internal/config/config.go - configuration
        files.append(GeneratedFile(
            path="internal/config/config.go",
            content=self._generate_config_go(pipeline, options),
            description="Configuration management",
        ))

        # internal/types/types.go - type definitions
        files.append(GeneratedFile(
            path="internal/types/types.go",
            content=self._generate_types_go(pipeline, options),
            description="Type definitions",
        ))

        # go.mod
        files.append(GeneratedFile(
            path="go.mod",
            content=self._generate_go_mod(module_name),
            description="Go module file",
        ))

        # README.md
        files.append(GeneratedFile(
            path="README.md",
            content=self._generate_readme(pipeline, options, module_name),
            description="Documentation",
        ))

        # Makefile
        files.append(GeneratedFile(
            path="Makefile",
            content=self._generate_makefile(module_name),
            description="Build automation",
        ))

        return files

    def _generate_main_go(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        standalone: bool = False,
    ) -> str:
        """Generate main.go for single-file output."""
        stages = pipeline.get("stages", [])
        pipeline_name = pipeline.get("name", "Pipeline")
        prefix = options.secrets_prefix

        # Build stage functions
        stage_funcs = self._build_stage_functions(stages, options)

        # Build execution order
        stage_order = self._resolve_execution_order(stages)
        execute_stages = self._build_execute_stages(stages, stage_order)

        return f'''// {pipeline_name}
//
// {pipeline.get("description", "")}
//
// Generated by FlowMason Code Generator v{self.generator_version}
// Generated at: {datetime.utcnow().isoformat()}

package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

// Config holds the pipeline configuration
type Config struct {{
	OpenAIAPIKey     string
	AnthropicAPIKey  string
	Timeout          time.Duration
	MaxRetries       int
	RetryDelay       time.Duration
}}

// StageInput represents input to a stage
type StageInput map[string]interface{{}}

// StageOutput represents output from a stage
type StageOutput map[string]interface{{}}

// PipelineResult represents the pipeline execution result
type PipelineResult struct {{
	Outputs map[string]StageOutput `json:"outputs"`
	Success bool                   `json:"success"`
	Error   string                 `json:"error,omitempty"`
}}

// Pipeline represents the pipeline executor
type Pipeline struct {{
	config    Config
	outputs   map[string]StageOutput
	variables map[string]interface{{}}
}}

// NewPipeline creates a new pipeline instance
func NewPipeline(cfg *Config) *Pipeline {{
	if cfg == nil {{
		cfg = DefaultConfig()
	}}
	return &Pipeline{{
		config:    *cfg,
		outputs:   make(map[string]StageOutput),
		variables: make(map[string]interface{{}}),
	}}
}}

// DefaultConfig returns the default configuration
func DefaultConfig() *Config {{
	return &Config{{
		OpenAIAPIKey:    os.Getenv("{prefix}OPENAI_API_KEY"),
		AnthropicAPIKey: os.Getenv("{prefix}ANTHROPIC_API_KEY"),
		Timeout:         30 * time.Second,
		MaxRetries:      3,
		RetryDelay:      time.Second,
	}}
}}

// Execute runs the pipeline with the given inputs
func (p *Pipeline) Execute(ctx context.Context, inputs map[string]interface{{}}) (*PipelineResult, error) {{
	p.outputs = make(map[string]StageOutput)
	p.variables = inputs
{execute_stages}
	return &PipelineResult{{
		Outputs: p.outputs,
		Success: true,
	}}, nil
}}

// Stage functions
{stage_funcs}

// resolveTemplate replaces {{key}} placeholders with values from data
func resolveTemplate(template string, data map[string]interface{{}}) string {{
	result := template
	for key, value := range data {{
		placeholder := "{{" + key + "}}"
		result = strings.ReplaceAll(result, placeholder, fmt.Sprintf("%v", value))
	}}
	return result
}}

// httpRequest performs an HTTP request
func httpRequest(ctx context.Context, method, url string, headers map[string]string, body io.Reader) (int, []byte, error) {{
	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {{
		return 0, nil, err
	}}
	for k, v := range headers {{
		req.Header.Set(k, v)
	}}

	client := &http.Client{{Timeout: 30 * time.Second}}
	resp, err := client.Do(req)
	if err != nil {{
		return 0, nil, err
	}}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	return resp.StatusCode, respBody, err
}}

// RunPipeline is a convenience function to run the pipeline
func RunPipeline(ctx context.Context, inputs map[string]interface{{}}, cfg *Config) (*PipelineResult, error) {{
	pipeline := NewPipeline(cfg)
	return pipeline.Execute(ctx, inputs)
}}

func main() {{
	inputFile := flag.String("input", "", "Path to input JSON file")
	inputJSON := flag.String("json", "", "Input as JSON string")
	pretty := flag.Bool("pretty", false, "Pretty print output")
	flag.Parse()

	var inputs map[string]interface{{}}

	if *inputJSON != "" {{
		if err := json.Unmarshal([]byte(*inputJSON), &inputs); err != nil {{
			fmt.Fprintf(os.Stderr, "Error parsing JSON: %v\\n", err)
			os.Exit(1)
		}}
	}} else if *inputFile != "" {{
		data, err := os.ReadFile(*inputFile)
		if err != nil {{
			fmt.Fprintf(os.Stderr, "Error reading file: %v\\n", err)
			os.Exit(1)
		}}
		if err := json.Unmarshal(data, &inputs); err != nil {{
			fmt.Fprintf(os.Stderr, "Error parsing file: %v\\n", err)
			os.Exit(1)
		}}
	}} else {{
		inputs = make(map[string]interface{{}})
	}}

	ctx := context.Background()
	result, err := RunPipeline(ctx, inputs, nil)
	if err != nil {{
		fmt.Fprintf(os.Stderr, "Pipeline error: %v\\n", err)
		os.Exit(1)
	}}

	var output []byte
	if *pretty {{
		output, _ = json.MarshalIndent(result, "", "  ")
	}} else {{
		output, _ = json.Marshal(result)
	}}
	fmt.Println(string(output))
}}
'''

    def _build_stage_functions(
        self,
        stages: List[Dict[str, Any]],
        options: CodeGenOptions,
    ) -> str:
        """Build stage function implementations."""
        funcs = []
        for stage in stages:
            stage_id = stage.get("id", "unknown")
            stage_name = stage.get("name", stage_id)
            component_type = stage.get("component_type", "unknown")
            config = stage.get("config", {})

            func_name = self._to_camel_case(f"execute_{stage_id}")
            func_code = self._generate_stage_func(stage_id, stage_name, component_type, config, options)
            funcs.append(func_code)

        return "\n".join(funcs)

    def _generate_stage_func(
        self,
        stage_id: str,
        stage_name: str,
        component_type: str,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate a single stage function."""
        func_name = self._to_camel_case(f"execute_{stage_id}")
        body = self._generate_component_code(component_type, config, options)

        return f'''
// {func_name} executes the "{stage_name}" stage ({component_type})
func (p *Pipeline) {func_name}(ctx context.Context, inputs StageInput) (StageOutput, error) {{
{body}
}}
'''

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

        if provider == "openai":
            system_line = 'messages = append(messages, map[string]string{"role": "system", "content": `' + system_prompt + '`})' if system_prompt else ""
            return f'''	// Resolve prompt template
	prompt := resolveTemplate(`{prompt_template}`, inputs)

	// Build OpenAI request
	messages := []map[string]string{{}}
	{system_line}
	messages = append(messages, map[string]string{{"role": "user", "content": prompt}})

	reqBody := map[string]interface{{}}{{
		"model":    "{model}",
		"messages": messages,
	}}

	reqBytes, _ := json.Marshal(reqBody)

	status, respBytes, err := httpRequest(ctx, "POST", "https://api.openai.com/v1/chat/completions",
		map[string]string{{
			"Content-Type":  "application/json",
			"Authorization": "Bearer " + p.config.OpenAIAPIKey,
		}},
		strings.NewReader(string(reqBytes)),
	)
	if err != nil {{
		return nil, fmt.Errorf("OpenAI request failed: %w", err)
	}}
	if status != 200 {{
		return nil, fmt.Errorf("OpenAI returned status %d: %s", status, string(respBytes))
	}}

	var resp map[string]interface{{}}
	if err := json.Unmarshal(respBytes, &resp); err != nil {{
		return nil, err
	}}

	choices := resp["choices"].([]interface{{}})
	if len(choices) == 0 {{
		return nil, fmt.Errorf("no choices in response")
	}}
	message := choices[0].(map[string]interface{{}})["message"].(map[string]interface{{}})
	content := message["content"].(string)

	return StageOutput{{"output": content}}, nil'''

        elif provider == "anthropic":
            system_line = 'reqBody["system"] = `' + system_prompt + '`' if system_prompt else ""
            return f'''	// Resolve prompt template
	prompt := resolveTemplate(`{prompt_template}`, inputs)

	// Build Anthropic request
	reqBody := map[string]interface{{}}{{
		"model":      "{model}",
		"max_tokens": 4096,
		"messages":   []map[string]string{{{{"role": "user", "content": prompt}}}},
	}}
	{system_line}

	reqBytes, _ := json.Marshal(reqBody)

	status, respBytes, err := httpRequest(ctx, "POST", "https://api.anthropic.com/v1/messages",
		map[string]string{{
			"Content-Type":      "application/json",
			"x-api-key":         p.config.AnthropicAPIKey,
			"anthropic-version": "2023-06-01",
		}},
		strings.NewReader(string(reqBytes)),
	)
	if err != nil {{
		return nil, fmt.Errorf("Anthropic request failed: %w", err)
	}}
	if status != 200 {{
		return nil, fmt.Errorf("Anthropic returned status %d: %s", status, string(respBytes))
	}}

	var resp map[string]interface{{}}
	if err := json.Unmarshal(respBytes, &resp); err != nil {{
		return nil, err
	}}

	content := resp["content"].([]interface{{}})
	if len(content) == 0 {{
		return nil, fmt.Errorf("no content in response")
	}}
	text := content[0].(map[string]interface{{}})["text"].(string)

	return StageOutput{{"output": text}}, nil'''

        else:
            return f'''	// Provider: {provider} - not implemented
	return nil, fmt.Errorf("provider {provider} not implemented")'''

    def _generate_http_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for HTTP request component."""
        method = config.get("method", "GET").upper()
        url = config.get("url", "")
        headers = config.get("headers", {})
        headers_go = "map[string]string{" + ", ".join(f'"{k}": "{v}"' for k, v in headers.items()) + "}"

        return f'''	// Resolve URL template
	url := resolveTemplate(`{url}`, inputs)

	status, body, err := httpRequest(ctx, "{method}", url, {headers_go}, nil)
	if err != nil {{
		return nil, fmt.Errorf("HTTP request failed: %w", err)
	}}

	var bodyData interface{{}}
	if err := json.Unmarshal(body, &bodyData); err != nil {{
		bodyData = string(body)
	}}

	return StageOutput{{
		"statusCode": status,
		"body":       bodyData,
	}}, nil'''

    def _generate_transform_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for JSON transform component."""
        mapping = config.get("mapping", {})

        if mapping:
            mapping_lines = []
            for target, source in mapping.items():
                parts = source.split(".")
                path_code = "inputs"
                for part in parts:
                    path_code = f'{path_code}["{part}"]'
                mapping_lines.append(f'\tresult["{target}"] = {path_code}')

            return f'''	result := make(StageOutput)
{chr(10).join(mapping_lines)}
	return result, nil'''

        return '''	// Passthrough - no mapping defined
	result := make(StageOutput)
	for k, v := range inputs {
		result[k] = v
	}
	return result, nil'''

    def _generate_filter_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for filter component."""
        condition = config.get("condition", "true")
        # Note: Real implementation would need proper condition parsing
        return f'''	// Apply filter condition: {condition}
	// Note: Complex conditions need manual implementation
	passed := true  // TODO: Implement condition logic

	if !passed {{
		return StageOutput{{"passed": false, "data": nil}}, nil
	}}
	return StageOutput{{"passed": true, "data": inputs}}, nil'''

    def _generate_variable_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for variable set component."""
        variables = config.get("variables", {})
        var_lines = []
        for key, value in variables.items():
            if isinstance(value, str):
                var_lines.append(f'\tresult["{key}"] = resolveTemplate(`{value}`, inputs)')
            else:
                var_lines.append(f'\tresult["{key}"] = {json.dumps(value)}')

        return f'''	result := make(StageOutput)
	for k, v := range inputs {{
		result[k] = v
	}}
{chr(10).join(var_lines)}
	return result, nil'''

    def _generate_logger_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for logger component."""
        message = config.get("message", "{inputs}")
        level = config.get("level", "info")

        return f'''	// Log message
	message := resolveTemplate(`{message}`, inputs)
	fmt.Printf("[{level.upper()}] %s\\n", message)

	result := make(StageOutput)
	for k, v := range inputs {{
		result[k] = v
	}}
	return result, nil'''

    def _generate_passthrough_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate passthrough code for unknown components."""
        return '''	// Passthrough - implement custom logic here
	result := make(StageOutput)
	for k, v := range inputs {
		result[k] = v
	}
	return result, nil'''

    def _build_execute_stages(
        self,
        stages: List[Dict[str, Any]],
        stage_order: List[str],
    ) -> str:
        """Build stage execution in Execute method."""
        lines = []
        for stage_id in stage_order:
            stage = next((s for s in stages if s.get("id") == stage_id), None)
            if not stage:
                continue

            func_name = self._to_camel_case(f"execute_{stage_id}")
            depends_on = stage.get("depends_on", [])

            lines.append(f"\n\t// Execute stage: {stage_id}")

            # Build inputs from dependencies
            if depends_on:
                lines.append(f"\tstageInputs{stage_id} := make(StageInput)")
                for dep in depends_on:
                    lines.append(f'\tfor k, v := range p.outputs["{dep}"] {{ stageInputs{stage_id}[k] = v }}')
                lines.append(f"\tfor k, v := range p.variables {{ stageInputs{stage_id}[k] = v }}")
                lines.append(f'\tp.outputs["{stage_id}"], _ = p.{func_name}(ctx, stageInputs{stage_id})')
            else:
                lines.append(f'\tp.outputs["{stage_id}"], _ = p.{func_name}(ctx, p.variables)')

        return "\n".join(lines)

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

    def _generate_cmd_main(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> str:
        """Generate cmd/main.go."""
        return f'''// Main entry point for {pipeline.get("name", "Pipeline")}
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"{module_name}/internal/config"
	"{module_name}/internal/pipeline"
)

func main() {{
	inputFile := flag.String("input", "", "Path to input JSON file")
	inputJSON := flag.String("json", "", "Input as JSON string")
	pretty := flag.Bool("pretty", false, "Pretty print output")
	flag.Parse()

	var inputs map[string]interface{{}}

	if *inputJSON != "" {{
		if err := json.Unmarshal([]byte(*inputJSON), &inputs); err != nil {{
			fmt.Fprintf(os.Stderr, "Error parsing JSON: %v\\n", err)
			os.Exit(1)
		}}
	}} else if *inputFile != "" {{
		data, err := os.ReadFile(*inputFile)
		if err != nil {{
			fmt.Fprintf(os.Stderr, "Error reading file: %v\\n", err)
			os.Exit(1)
		}}
		if err := json.Unmarshal(data, &inputs); err != nil {{
			fmt.Fprintf(os.Stderr, "Error parsing file: %v\\n", err)
			os.Exit(1)
		}}
	}} else {{
		inputs = make(map[string]interface{{}})
	}}

	ctx := context.Background()
	cfg := config.Default()

	result, err := pipeline.Run(ctx, inputs, cfg)
	if err != nil {{
		fmt.Fprintf(os.Stderr, "Pipeline error: %v\\n", err)
		os.Exit(1)
	}}

	var output []byte
	if *pretty {{
		output, _ = json.MarshalIndent(result, "", "  ")
	}} else {{
		output, _ = json.Marshal(result)
	}}
	fmt.Println(string(output))
}}
'''

    def _generate_pipeline_go(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate internal/pipeline/pipeline.go."""
        stages = pipeline.get("stages", [])
        stage_order = self._resolve_execution_order(stages)
        execute_stages = self._build_package_execute_stages(stages, stage_order)

        return f'''// Package pipeline implements the main pipeline execution logic.
package pipeline

import (
	"context"

	"{{module}}/internal/config"
	"{{module}}/internal/stages"
	"{{module}}/internal/types"
)

// Pipeline represents the pipeline executor
type Pipeline struct {{
	config    *config.Config
	outputs   map[string]types.StageOutput
	variables map[string]interface{{}}
}}

// New creates a new pipeline instance
func New(cfg *config.Config) *Pipeline {{
	return &Pipeline{{
		config:    cfg,
		outputs:   make(map[string]types.StageOutput),
		variables: make(map[string]interface{{}}),
	}}
}}

// Execute runs the pipeline with the given inputs
func (p *Pipeline) Execute(ctx context.Context, inputs map[string]interface{{}}) (*types.PipelineResult, error) {{
	p.outputs = make(map[string]types.StageOutput)
	p.variables = inputs
{execute_stages}
	return &types.PipelineResult{{
		Outputs: p.outputs,
		Success: true,
	}}, nil
}}

// Run is a convenience function to run the pipeline
func Run(ctx context.Context, inputs map[string]interface{{}}, cfg *config.Config) (*types.PipelineResult, error) {{
	pipeline := New(cfg)
	return pipeline.Execute(ctx, inputs)
}}
'''

    def _build_package_execute_stages(
        self,
        stages: List[Dict[str, Any]],
        stage_order: List[str],
    ) -> str:
        """Build stage execution for package structure."""
        lines = []
        for stage_id in stage_order:
            stage = next((s for s in stages if s.get("id") == stage_id), None)
            if not stage:
                continue

            func_name = self._to_pascal_case(f"execute_{stage_id}")
            depends_on = stage.get("depends_on", [])

            lines.append(f"\n\t// Execute stage: {stage_id}")

            if depends_on:
                lines.append(f"\tstageInputs{stage_id} := make(types.StageInput)")
                for dep in depends_on:
                    lines.append(f'\tfor k, v := range p.outputs["{dep}"] {{ stageInputs{stage_id}[k] = v }}')
                lines.append(f"\tfor k, v := range p.variables {{ stageInputs{stage_id}[k] = v }}")
                lines.append(f'\tp.outputs["{stage_id}"], _ = stages.{func_name}(ctx, stageInputs{stage_id}, p.config)')
            else:
                lines.append(f'\tp.outputs["{stage_id}"], _ = stages.{func_name}(ctx, p.variables, p.config)')

        return "\n".join(lines)

    def _generate_stages_go(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate internal/stages/stages.go."""
        stages = pipeline.get("stages", [])
        funcs = []

        for stage in stages:
            stage_id = stage.get("id", "unknown")
            stage_name = stage.get("name", stage_id)
            component_type = stage.get("component_type", "unknown")
            config = stage.get("config", {})

            func_name = self._to_pascal_case(f"execute_{stage_id}")
            body = self._generate_component_code(component_type, config, options)

            funcs.append(f'''
// {func_name} executes the "{stage_name}" stage ({component_type})
func {func_name}(ctx context.Context, inputs types.StageInput, cfg *config.Config) (types.StageOutput, error) {{
{body}
}}
''')

        return f'''// Package stages implements individual stage functions.
package stages

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"{{module}}/internal/config"
	"{{module}}/internal/types"
)

// resolveTemplate replaces {{key}} placeholders with values from data
func resolveTemplate(template string, data map[string]interface{{}}) string {{
	result := template
	for key, value := range data {{
		placeholder := "{{" + key + "}}"
		result = strings.ReplaceAll(result, placeholder, fmt.Sprintf("%v", value))
	}}
	return result
}}

// httpRequest performs an HTTP request
func httpRequest(ctx context.Context, method, url string, headers map[string]string, body io.Reader) (int, []byte, error) {{
	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {{
		return 0, nil, err
	}}
	for k, v := range headers {{
		req.Header.Set(k, v)
	}}

	client := &http.Client{{Timeout: 30 * time.Second}}
	resp, err := client.Do(req)
	if err != nil {{
		return 0, nil, err
	}}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	return resp.StatusCode, respBody, err
}}
{"".join(funcs)}
'''

    def _generate_config_go(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate internal/config/config.go."""
        prefix = options.secrets_prefix
        return f'''// Package config provides configuration management.
package config

import (
	"os"
	"time"
)

// Config holds the pipeline configuration
type Config struct {{
	OpenAIAPIKey     string
	AnthropicAPIKey  string
	Timeout          time.Duration
	MaxRetries       int
	RetryDelay       time.Duration
}}

// Default returns the default configuration
func Default() *Config {{
	return &Config{{
		OpenAIAPIKey:    os.Getenv("{prefix}OPENAI_API_KEY"),
		AnthropicAPIKey: os.Getenv("{prefix}ANTHROPIC_API_KEY"),
		Timeout:         30 * time.Second,
		MaxRetries:      3,
		RetryDelay:      time.Second,
	}}
}}
'''

    def _generate_types_go(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate internal/types/types.go."""
        return '''// Package types defines common types for the pipeline.
package types

// StageInput represents input to a stage
type StageInput map[string]interface{}

// StageOutput represents output from a stage
type StageOutput map[string]interface{}

// PipelineResult represents the pipeline execution result
type PipelineResult struct {
	Outputs map[string]StageOutput `json:"outputs"`
	Success bool                   `json:"success"`
	Error   string                 `json:"error,omitempty"`
}
'''

    def _generate_go_mod(self, module_name: str) -> str:
        """Generate go.mod file."""
        return f'''module {module_name}

go 1.21

require (
	// Add dependencies here
)
'''

    def _generate_makefile(self, module_name: str) -> str:
        """Generate Makefile."""
        return f'''.PHONY: build run test clean

build:
	go build -o bin/{module_name} ./cmd/main.go

run: build
	./bin/{module_name}

test:
	go test -v ./...

clean:
	rm -rf bin/
'''

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
go mod download
```

## Configuration

Set the following environment variables:

```bash
export FLOWMASON_OPENAI_API_KEY=your-openai-key
export FLOWMASON_ANTHROPIC_API_KEY=your-anthropic-key
```

## Build

```bash
make build
```

## Run

```bash
# With JSON file
./bin/{module_name} -input input.json -pretty

# With inline JSON
./bin/{module_name} -json '{{"key": "value"}}' -pretty
```

## Development

```bash
# Run tests
make test

# Clean build artifacts
make clean
```

---

*Generated by FlowMason Code Generator v{self.generator_version}*
"""

    def _generate_lambda_files(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        module_name: str,
    ) -> List[GeneratedFile]:
        """Generate AWS Lambda specific files."""
        return [
            GeneratedFile(
                path="lambda/handler.go",
                content=self._generate_lambda_handler(module_name),
                description="AWS Lambda handler",
            ),
            GeneratedFile(
                path="template.yaml",
                content=self._generate_sam_template_go(pipeline, module_name),
                description="AWS SAM template",
            ),
        ]

    def _generate_lambda_handler(self, module_name: str) -> str:
        """Generate AWS Lambda handler."""
        return f'''// Lambda handler for the pipeline
package main

import (
	"context"
	"encoding/json"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"

	"{module_name}/internal/config"
	"{module_name}/internal/pipeline"
)

func handler(ctx context.Context, request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {{
	var inputs map[string]interface{{}}
	if request.Body != "" {{
		if err := json.Unmarshal([]byte(request.Body), &inputs); err != nil {{
			return events.APIGatewayProxyResponse{{
				StatusCode: 400,
				Body:       `{{"error": "Invalid JSON"}}`,
			}}, nil
		}}
	}} else {{
		inputs = make(map[string]interface{{}})
	}}

	cfg := config.Default()
	result, err := pipeline.Run(ctx, inputs, cfg)
	if err != nil {{
		return events.APIGatewayProxyResponse{{
			StatusCode: 500,
			Body:       `{{"error": "` + err.Error() + `"}}`,
		}}, nil
	}}

	body, _ := json.Marshal(result)
	return events.APIGatewayProxyResponse{{
		StatusCode: 200,
		Headers:    map[string]string{{"Content-Type": "application/json"}},
		Body:       string(body),
	}}, nil
}}

func main() {{
	lambda.Start(handler)
}}
'''

    def _generate_sam_template_go(self, pipeline: Dict[str, Any], module_name: str) -> str:
        """Generate AWS SAM template for Go."""
        pipeline_name = pipeline.get("name", module_name)
        return f"""AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: {pipeline_name} - FlowMason Pipeline (Go)

Globals:
  Function:
    Timeout: 30
    MemorySize: 256

Resources:
  PipelineFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: {module_name}
      Handler: bootstrap
      Runtime: provided.al2
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
      BuildMethod: go1.x

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
                content=self._generate_dockerfile_go(module_name),
                description="Docker build file",
            ),
            GeneratedFile(
                path="docker-compose.yml",
                content=self._generate_docker_compose_go(pipeline, module_name),
                description="Docker Compose configuration",
            ),
        ]

    def _generate_dockerfile_go(self, module_name: str) -> str:
        """Generate Dockerfile for Go."""
        return f'''# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /{module_name} ./cmd/main.go

# Runtime stage
FROM alpine:3.18

RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /{module_name} .

EXPOSE 8080
ENTRYPOINT ["./{module_name}"]
'''

    def _generate_docker_compose_go(self, pipeline: Dict[str, Any], module_name: str) -> str:
        """Generate docker-compose.yml for Go."""
        return f'''version: '3.8'

services:
  pipeline:
    build: .
    container_name: {module_name}
    environment:
      - FLOWMASON_OPENAI_API_KEY=${{OPENAI_API_KEY}}
      - FLOWMASON_ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY}}
    ports:
      - "8080:8080"
    restart: unless-stopped
'''

    def _get_deployment_config(
        self,
        options: CodeGenOptions,
        module_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get deployment configuration."""
        if options.platform == TargetPlatform.AWS_LAMBDA:
            return {
                "platform": "aws_lambda",
                "runtime": "provided.al2",
                "handler": "bootstrap",
                "deploy_command": "sam build && sam deploy --guided",
            }
        elif options.platform == TargetPlatform.DOCKER:
            return {
                "platform": "docker",
                "deploy_command": "docker-compose up -d",
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
        elif options.platform == TargetPlatform.DOCKER:
            return f"""## Deploy with Docker

1. Build: `docker build -t {module_name} .`
2. Run: `docker-compose up -d`
"""
        return None


# Singleton instance
_generator: Optional[GoCodeGenerator] = None


def get_go_code_generator() -> GoCodeGenerator:
    """Get the singleton GoCodeGenerator instance."""
    global _generator
    if _generator is None:
        _generator = GoCodeGenerator()
    return _generator
