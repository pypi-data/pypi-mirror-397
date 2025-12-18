"""
Salesforce Apex Code Generator Service.

Generates Salesforce Apex classes from FlowMason pipelines.
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


class ApexCodeGenerator:
    """Generates Salesforce Apex code from pipeline definitions."""

    def __init__(self):
        """Initialize the code generator."""
        self.generator_version = "1.0.0"

    def generate(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
    ) -> CodeGenResult:
        """
        Generate Salesforce Apex code from a pipeline definition.

        Args:
            pipeline: Pipeline configuration dictionary
            options: Code generation options

        Returns:
            CodeGenResult with generated files
        """
        gen_id = str(uuid.uuid4())
        pipeline_id = pipeline.get("id", "pipeline")
        pipeline_name = pipeline.get("name", "generated_pipeline")

        # Sanitize name for Apex (PascalCase class names)
        class_name = self._sanitize_class_name(pipeline_name)

        files: List[GeneratedFile] = []

        # Generate based on output format
        if options.output_format == OutputFormat.SINGLE_FILE:
            files = self._generate_single_file(pipeline, options, class_name)
        else:
            files = self._generate_package(pipeline, options, class_name)

        # Calculate stats
        total_lines = sum(
            len(f.content.split("\n")) for f in files if not f.is_binary
        )

        # Determine entry point
        entry_point = f"force-app/main/default/classes/{class_name}.cls"

        return CodeGenResult(
            id=gen_id,
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            options=options,
            files=files,
            entry_point=entry_point,
            total_lines=total_lines,
            total_files=len(files),
            deployment_config=self._get_deployment_config(options, class_name),
            deploy_instructions=self._get_deploy_instructions(options, class_name),
        )

    def _sanitize_class_name(self, name: str) -> str:
        """Convert name to valid Apex class name (PascalCase)."""
        # Replace hyphens and spaces with underscores then convert
        name = name.replace(" ", "_").replace("-", "_")
        # Remove invalid characters
        name = "".join(c for c in name if c.isalnum() or c == "_")
        # Convert to PascalCase
        parts = name.split("_")
        name = "".join(p.capitalize() for p in parts if p)
        # Ensure doesn't start with number
        if name and name[0].isdigit():
            name = f"Pipeline{name}"
        return name or "Pipeline"

    def _generate_single_file(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        class_name: str,
    ) -> List[GeneratedFile]:
        """Generate all code in a single Apex class."""
        code = self._generate_main_class(pipeline, options, class_name, standalone=True)
        meta = self._generate_class_meta(class_name, "47.0")

        return [
            GeneratedFile(
                path=f"{class_name}.cls",
                content=code,
                description="Main pipeline Apex class",
            ),
            GeneratedFile(
                path=f"{class_name}.cls-meta.xml",
                content=meta,
                description="Apex class metadata",
            ),
        ]

    def _generate_package(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        class_name: str,
    ) -> List[GeneratedFile]:
        """Generate a complete SFDX project structure."""
        files = []

        # Main pipeline class
        files.append(GeneratedFile(
            path=f"force-app/main/default/classes/{class_name}.cls",
            content=self._generate_main_class(pipeline, options, class_name, standalone=False),
            description="Main pipeline Apex class",
        ))
        files.append(GeneratedFile(
            path=f"force-app/main/default/classes/{class_name}.cls-meta.xml",
            content=self._generate_class_meta(class_name, "60.0"),
            description="Apex class metadata",
        ))

        # Service class for HTTP callouts
        files.append(GeneratedFile(
            path=f"force-app/main/default/classes/{class_name}Service.cls",
            content=self._generate_service_class(pipeline, options, class_name),
            description="HTTP callout service class",
        ))
        files.append(GeneratedFile(
            path=f"force-app/main/default/classes/{class_name}Service.cls-meta.xml",
            content=self._generate_class_meta(f"{class_name}Service", "60.0"),
            description="Service class metadata",
        ))

        # Test class
        files.append(GeneratedFile(
            path=f"force-app/main/default/classes/{class_name}Test.cls",
            content=self._generate_test_class(pipeline, options, class_name),
            description="Test class for pipeline",
        ))
        files.append(GeneratedFile(
            path=f"force-app/main/default/classes/{class_name}Test.cls-meta.xml",
            content=self._generate_class_meta(f"{class_name}Test", "60.0"),
            description="Test class metadata",
        ))

        # Invocable action for Flow integration
        files.append(GeneratedFile(
            path=f"force-app/main/default/classes/{class_name}Invocable.cls",
            content=self._generate_invocable_class(pipeline, options, class_name),
            description="Invocable action for Flow",
        ))
        files.append(GeneratedFile(
            path=f"force-app/main/default/classes/{class_name}Invocable.cls-meta.xml",
            content=self._generate_class_meta(f"{class_name}Invocable", "60.0"),
            description="Invocable class metadata",
        ))

        # Named Credentials (for secure API key storage)
        files.append(GeneratedFile(
            path="force-app/main/default/namedCredentials/OpenAI.namedCredential-meta.xml",
            content=self._generate_named_credential("OpenAI", "https://api.openai.com"),
            description="OpenAI Named Credential",
        ))
        files.append(GeneratedFile(
            path="force-app/main/default/namedCredentials/Anthropic.namedCredential-meta.xml",
            content=self._generate_named_credential("Anthropic", "https://api.anthropic.com"),
            description="Anthropic Named Credential",
        ))

        # Remote Site Settings
        files.append(GeneratedFile(
            path="force-app/main/default/remoteSiteSettings/OpenAI_API.remoteSite-meta.xml",
            content=self._generate_remote_site("OpenAI_API", "https://api.openai.com"),
            description="OpenAI Remote Site Setting",
        ))
        files.append(GeneratedFile(
            path="force-app/main/default/remoteSiteSettings/Anthropic_API.remoteSite-meta.xml",
            content=self._generate_remote_site("Anthropic_API", "https://api.anthropic.com"),
            description="Anthropic Remote Site Setting",
        ))

        # sfdx-project.json
        files.append(GeneratedFile(
            path="sfdx-project.json",
            content=self._generate_sfdx_project(class_name),
            description="SFDX project configuration",
        ))

        # README
        files.append(GeneratedFile(
            path="README.md",
            content=self._generate_readme(pipeline, options, class_name),
            description="Documentation",
        ))

        return files

    def _generate_main_class(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        class_name: str,
        standalone: bool = False,
    ) -> str:
        """Generate the main pipeline Apex class."""
        stages = pipeline.get("stages", [])
        pipeline_name = pipeline.get("name", "Pipeline")
        description = pipeline.get("description", "")

        # Build stage methods
        stage_methods = self._build_stage_methods(stages, options)

        # Build execution order
        stage_order = self._resolve_execution_order(stages)
        execute_calls = self._build_execute_calls(stages, stage_order)

        return f'''/**
 * {pipeline_name}
 * {description}
 *
 * Generated by FlowMason Code Generator v{self.generator_version}
 * Generated at: {datetime.utcnow().isoformat()}
 */
public with sharing class {class_name} {{

    // Stage outputs storage
    private Map<String, Map<String, Object>> outputs;
    private Map<String, Object> variables;

    /**
     * Pipeline result wrapper
     */
    public class PipelineResult {{
        @AuraEnabled public Map<String, Map<String, Object>> outputs;
        @AuraEnabled public Boolean success;
        @AuraEnabled public String errorMessage;

        public PipelineResult() {{
            this.outputs = new Map<String, Map<String, Object>>();
            this.success = true;
        }}
    }}

    /**
     * Constructor
     */
    public {class_name}() {{
        this.outputs = new Map<String, Map<String, Object>>();
        this.variables = new Map<String, Object>();
    }}

    /**
     * Execute the pipeline with provided inputs
     * @param inputs Map of input values
     * @return PipelineResult with outputs and status
     */
    public PipelineResult execute(Map<String, Object> inputs) {{
        PipelineResult result = new PipelineResult();

        try {{
            this.outputs.clear();
            this.variables = inputs != null ? inputs : new Map<String, Object>();

            // Execute stages
{execute_calls}

            result.outputs = this.outputs;
            result.success = true;

        }} catch (Exception e) {{
            result.success = false;
            result.errorMessage = e.getMessage();
            System.debug(LoggingLevel.ERROR, 'Pipeline error: ' + e.getMessage());
        }}

        return result;
    }}

    // Stage execution methods
{stage_methods}

    /**
     * Resolve template variables in a string
     * @param template String with {{variable}} placeholders
     * @param data Map of variable values
     * @return Resolved string
     */
    private String resolveTemplate(String template, Map<String, Object> data) {{
        String result = template;
        if (data != null) {{
            for (String key : data.keySet()) {{
                String placeholder = '{{' + key + '}}';
                Object value = data.get(key);
                result = result.replace(placeholder, value != null ? String.valueOf(value) : '');
            }}
        }}
        return result;
    }}

    /**
     * Get nested value from a map using dot notation
     * @param data Source map
     * @param path Dot-separated path
     * @return Value at path or null
     */
    private Object getNestedValue(Map<String, Object> data, String path) {{
        if (data == null || String.isBlank(path)) {{
            return null;
        }}

        List<String> parts = path.split('\\\\.');
        Object current = data;

        for (String part : parts) {{
            if (current instanceof Map<String, Object>) {{
                current = ((Map<String, Object>)current).get(part);
            }} else {{
                return null;
            }}
        }}

        return current;
    }}
}}
'''

    def _build_stage_methods(
        self,
        stages: List[Dict[str, Any]],
        options: CodeGenOptions,
    ) -> str:
        """Build stage execution methods."""
        methods = []
        for stage in stages:
            stage_id = stage.get("id", "unknown")
            stage_name = stage.get("name", stage_id)
            component_type = stage.get("component_type", "unknown")
            config = stage.get("config", {})

            method_name = self._to_method_name(f"execute_{stage_id}")
            method_code = self._generate_stage_method(stage_id, stage_name, component_type, config, options)
            methods.append(method_code)

        return "\n".join(methods)

    def _to_method_name(self, name: str) -> str:
        """Convert to valid Apex method name (camelCase)."""
        parts = name.lower().split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    def _generate_stage_method(
        self,
        stage_id: str,
        stage_name: str,
        component_type: str,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate a single stage method."""
        method_name = self._to_method_name(f"execute_{stage_id}")
        body = self._generate_component_code(component_type, config, options)

        return f'''
    /**
     * Execute stage: {stage_name}
     * Component: {component_type}
     */
    private Map<String, Object> {method_name}(Map<String, Object> inputs) {{
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

        return f'''        // Resolve prompt template
        String prompt = resolveTemplate('{prompt_template}', inputs);

        // Build request body
        Map<String, Object> requestBody = new Map<String, Object>();
        requestBody.put('model', '{model}');

        List<Map<String, String>> messages = new List<Map<String, String>>();
        {("messages.add(new Map<String, String>{'role' => 'system', 'content' => '" + system_prompt + "'});" if system_prompt else "// No system prompt")}
        messages.add(new Map<String, String>{{'role' => 'user', 'content' => prompt}});
        requestBody.put('messages', messages);

        // Make API callout
        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:OpenAI/v1/chat/completions');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');
        req.setBody(JSON.serialize(requestBody));
        req.setTimeout(120000);

        HttpResponse res = http.send(req);

        if (res.getStatusCode() != 200) {{
            throw new CalloutException('OpenAI API error: ' + res.getBody());
        }}

        Map<String, Object> response = (Map<String, Object>)JSON.deserializeUntyped(res.getBody());
        List<Object> choices = (List<Object>)response.get('choices');
        Map<String, Object> firstChoice = (Map<String, Object>)choices[0];
        Map<String, Object> message = (Map<String, Object>)firstChoice.get('message');
        String content = (String)message.get('content');

        return new Map<String, Object>{{
            'output' => content
        }};'''

    def _generate_http_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for HTTP request component."""
        method = config.get("method", "GET").upper()
        url = config.get("url", "")
        headers = config.get("headers", {})

        header_lines = "\n".join(
            f"        req.setHeader('{k}', '{v}');"
            for k, v in headers.items()
        )

        return f'''        // Resolve URL template
        String url = resolveTemplate('{url}', inputs);

        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint(url);
        req.setMethod('{method}');
{header_lines}
        req.setTimeout(120000);

        HttpResponse res = http.send(req);

        Object body;
        String contentType = res.getHeader('Content-Type');
        if (contentType != null && contentType.contains('application/json')) {{
            body = JSON.deserializeUntyped(res.getBody());
        }} else {{
            body = res.getBody();
        }}

        return new Map<String, Object>{{
            'statusCode' => res.getStatusCode(),
            'body' => body,
            'headers' => res.getHeaderKeys()
        }};'''

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
                mapping_lines.append(
                    f"        result.put('{target}', getNestedValue(inputs, '{source}'));"
                )
            mapping_code = "\n".join(mapping_lines)

            return f'''        Map<String, Object> result = new Map<String, Object>();
{mapping_code}
        return result;'''

        return '''        // Passthrough - no mapping defined
        return new Map<String, Object>(inputs);'''

    def _generate_filter_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for filter component."""
        condition = config.get("condition", "true")

        return f'''        // Apply filter condition: {condition}
        // Note: Complex conditions need manual implementation
        Boolean passed = true; // TODO: Implement condition logic

        if (!passed) {{
            return new Map<String, Object>{{
                'passed' => false,
                'data' => null
            }};
        }}
        return new Map<String, Object>{{
            'passed' => true,
            'data' => inputs
        }};'''

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
                var_lines.append(f"        result.put('{key}', resolveTemplate('{value}', inputs));")
            else:
                var_lines.append(f"        result.put('{key}', {json.dumps(value)});")

        return f'''        Map<String, Object> result = new Map<String, Object>(inputs);
{chr(10).join(var_lines)}
        return result;'''

    def _generate_logger_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate code for logger component."""
        message = config.get("message", "{inputs}")
        level = config.get("level", "info").upper()

        return f'''        // Log message
        String logMessage = resolveTemplate('{message}', inputs);
        System.debug(LoggingLevel.{level}, logMessage);

        return new Map<String, Object>(inputs);'''

    def _generate_passthrough_code(
        self,
        config: Dict[str, Any],
        options: CodeGenOptions,
    ) -> str:
        """Generate passthrough code for unknown components."""
        return '''        // Passthrough - implement custom logic here
        return new Map<String, Object>(inputs);'''

    def _build_execute_calls(
        self,
        stages: List[Dict[str, Any]],
        stage_order: List[str],
    ) -> str:
        """Build stage execution calls."""
        lines = []
        for stage_id in stage_order:
            stage = next((s for s in stages if s.get("id") == stage_id), None)
            if not stage:
                continue

            method_name = self._to_method_name(f"execute_{stage_id}")
            depends_on = stage.get("depends_on", [])

            lines.append(f"\n            // Execute stage: {stage_id}")

            if depends_on:
                lines.append(f"            Map<String, Object> inputs{stage_id} = new Map<String, Object>();")
                for dep in depends_on:
                    lines.append(f"            inputs{stage_id}.putAll(this.outputs.get('{dep}'));")
                lines.append(f"            inputs{stage_id}.putAll(this.variables);")
                lines.append(f"            this.outputs.put('{stage_id}', this.{method_name}(inputs{stage_id}));")
            else:
                lines.append(f"            this.outputs.put('{stage_id}', this.{method_name}(this.variables));")

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

    def _generate_service_class(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        class_name: str,
    ) -> str:
        """Generate HTTP service class."""
        return f'''/**
 * {class_name} HTTP Service
 *
 * Handles HTTP callouts for the pipeline.
 * Generated by FlowMason Code Generator v{self.generator_version}
 */
public with sharing class {class_name}Service {{

    /**
     * Make an HTTP callout to OpenAI
     * @param endpoint API endpoint
     * @param body Request body
     * @return Response body as Map
     */
    public static Map<String, Object> callOpenAI(String endpoint, Map<String, Object> body) {{
        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:OpenAI' + endpoint);
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');
        req.setBody(JSON.serialize(body));
        req.setTimeout(120000);

        HttpResponse res = http.send(req);

        if (res.getStatusCode() != 200) {{
            throw new CalloutException('OpenAI API error: ' + res.getStatusCode() + ' - ' + res.getBody());
        }}

        return (Map<String, Object>)JSON.deserializeUntyped(res.getBody());
    }}

    /**
     * Make an HTTP callout to Anthropic
     * @param endpoint API endpoint
     * @param body Request body
     * @return Response body as Map
     */
    public static Map<String, Object> callAnthropic(String endpoint, Map<String, Object> body) {{
        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:Anthropic' + endpoint);
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');
        req.setHeader('anthropic-version', '2023-06-01');
        req.setBody(JSON.serialize(body));
        req.setTimeout(120000);

        HttpResponse res = http.send(req);

        if (res.getStatusCode() != 200) {{
            throw new CalloutException('Anthropic API error: ' + res.getStatusCode() + ' - ' + res.getBody());
        }}

        return (Map<String, Object>)JSON.deserializeUntyped(res.getBody());
    }}

    /**
     * Generic HTTP callout
     * @param endpoint Full URL
     * @param method HTTP method
     * @param headers Request headers
     * @param body Request body (optional)
     * @return Response wrapper
     */
    public static HttpResponse makeCallout(String endpoint, String method, Map<String, String> headers, String body) {{
        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint(endpoint);
        req.setMethod(method);

        if (headers != null) {{
            for (String key : headers.keySet()) {{
                req.setHeader(key, headers.get(key));
            }}
        }}

        if (body != null) {{
            req.setBody(body);
        }}

        req.setTimeout(120000);
        return http.send(req);
    }}
}}
'''

    def _generate_test_class(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        class_name: str,
    ) -> str:
        """Generate test class."""
        return f'''/**
 * Test class for {class_name}
 *
 * Generated by FlowMason Code Generator v{self.generator_version}
 */
@isTest
private class {class_name}Test {{

    /**
     * Mock HTTP callout response
     */
    private class MockHttpResponse implements HttpCalloutMock {{
        public HttpResponse respond(HttpRequest req) {{
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            res.setStatusCode(200);

            // Mock OpenAI response
            if (req.getEndpoint().contains('openai')) {{
                res.setBody('{{"choices": [{{"message": {{"content": "Test response"}}}}]}}');
            }}
            // Mock Anthropic response
            else if (req.getEndpoint().contains('anthropic')) {{
                res.setBody('{{"content": [{{"text": "Test response"}}]}}');
            }}
            // Generic response
            else {{
                res.setBody('{{"success": true}}');
            }}

            return res;
        }}
    }}

    @isTest
    static void testPipelineExecution() {{
        Test.setMock(HttpCalloutMock.class, new MockHttpResponse());

        Test.startTest();

        {class_name} pipeline = new {class_name}();
        Map<String, Object> inputs = new Map<String, Object>{{
            'input' => 'Test input'
        }};

        {class_name}.PipelineResult result = pipeline.execute(inputs);

        Test.stopTest();

        System.assertNotEquals(null, result, 'Result should not be null');
        System.assertEquals(true, result.success, 'Pipeline should succeed');
    }}

    @isTest
    static void testPipelineWithNullInputs() {{
        Test.setMock(HttpCalloutMock.class, new MockHttpResponse());

        Test.startTest();

        {class_name} pipeline = new {class_name}();
        {class_name}.PipelineResult result = pipeline.execute(null);

        Test.stopTest();

        System.assertNotEquals(null, result, 'Result should not be null');
    }}

    @isTest
    static void testInvocableAction() {{
        Test.setMock(HttpCalloutMock.class, new MockHttpResponse());

        Test.startTest();

        {class_name}Invocable.Request request = new {class_name}Invocable.Request();
        request.inputJson = '{{"input": "Test"}}';

        List<{class_name}Invocable.Response> responses = {class_name}Invocable.execute(
            new List<{class_name}Invocable.Request>{{ request }}
        );

        Test.stopTest();

        System.assertEquals(1, responses.size(), 'Should have one response');
        System.assertEquals(true, responses[0].success, 'Should succeed');
    }}
}}
'''

    def _generate_invocable_class(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        class_name: str,
    ) -> str:
        """Generate Invocable action for Flow integration."""
        return f'''/**
 * Invocable action for {class_name}
 *
 * Allows the pipeline to be called from Salesforce Flows.
 * Generated by FlowMason Code Generator v{self.generator_version}
 */
global with sharing class {class_name}Invocable {{

    /**
     * Request wrapper for Flow
     */
    global class Request {{
        @InvocableVariable(label='Input JSON' description='JSON string with input values' required=false)
        global String inputJson;

        @InvocableVariable(label='Input Value' description='Single input value' required=false)
        global String inputValue;
    }}

    /**
     * Response wrapper for Flow
     */
    global class Response {{
        @InvocableVariable(label='Output JSON' description='JSON string with all outputs')
        global String outputJson;

        @InvocableVariable(label='Success' description='Whether the pipeline succeeded')
        global Boolean success;

        @InvocableVariable(label='Error Message' description='Error message if failed')
        global String errorMessage;

        @InvocableVariable(label='Output Value' description='Primary output value')
        global String outputValue;
    }}

    /**
     * Execute the pipeline from Flow
     * @param requests List of pipeline requests
     * @return List of pipeline responses
     */
    @InvocableMethod(label='Execute {pipeline.get("name", class_name)}' description='{pipeline.get("description", "Execute the AI pipeline")}'  category='AI Pipeline')
    global static List<Response> execute(List<Request> requests) {{
        List<Response> responses = new List<Response>();

        for (Request req : requests) {{
            Response res = new Response();

            try {{
                // Parse input
                Map<String, Object> inputs = new Map<String, Object>();

                if (String.isNotBlank(req.inputJson)) {{
                    inputs = (Map<String, Object>)JSON.deserializeUntyped(req.inputJson);
                }}

                if (String.isNotBlank(req.inputValue)) {{
                    inputs.put('input', req.inputValue);
                }}

                // Execute pipeline
                {class_name} pipeline = new {class_name}();
                {class_name}.PipelineResult result = pipeline.execute(inputs);

                res.success = result.success;
                res.errorMessage = result.errorMessage;
                res.outputJson = JSON.serialize(result.outputs);

                // Try to extract primary output
                if (result.outputs != null && !result.outputs.isEmpty()) {{
                    for (String key : result.outputs.keySet()) {{
                        Map<String, Object> stageOutput = result.outputs.get(key);
                        if (stageOutput.containsKey('output')) {{
                            res.outputValue = String.valueOf(stageOutput.get('output'));
                            break;
                        }}
                    }}
                }}

            }} catch (Exception e) {{
                res.success = false;
                res.errorMessage = e.getMessage();
            }}

            responses.add(res);
        }}

        return responses;
    }}
}}
'''

    def _generate_class_meta(self, class_name: str, api_version: str) -> str:
        """Generate Apex class metadata XML."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>{api_version}</apiVersion>
    <status>Active</status>
</ApexClass>
'''

    def _generate_named_credential(self, name: str, endpoint: str) -> str:
        """Generate Named Credential metadata."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<NamedCredential xmlns="http://soap.sforce.com/2006/04/metadata">
    <allowMergeFieldsInBody>true</allowMergeFieldsInBody>
    <allowMergeFieldsInHeader>true</allowMergeFieldsInHeader>
    <authProvider>External_{name}</authProvider>
    <calloutStatus>Enabled</calloutStatus>
    <endpoint>{endpoint}</endpoint>
    <generateAuthorizationHeader>true</generateAuthorizationHeader>
    <label>{name}</label>
    <namedCredentialType>SecuredEndpoint</namedCredentialType>
    <oauthRefreshToken>false</oauthRefreshToken>
</NamedCredential>
'''

    def _generate_remote_site(self, name: str, url: str) -> str:
        """Generate Remote Site Setting metadata."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<RemoteSiteSetting xmlns="http://soap.sforce.com/2006/04/metadata">
    <disableProtocolSecurity>false</disableProtocolSecurity>
    <isActive>true</isActive>
    <url>{url}</url>
    <description>Remote site for {name}</description>
</RemoteSiteSetting>
'''

    def _generate_sfdx_project(self, class_name: str) -> str:
        """Generate sfdx-project.json."""
        return json.dumps({
            "packageDirectories": [
                {
                    "path": "force-app",
                    "default": True
                }
            ],
            "name": class_name.lower(),
            "namespace": "",
            "sfdcLoginUrl": "https://login.salesforce.com",
            "sourceApiVersion": "60.0"
        }, indent=2)

    def _generate_readme(
        self,
        pipeline: Dict[str, Any],
        options: CodeGenOptions,
        class_name: str,
    ) -> str:
        """Generate README."""
        pipeline_name = pipeline.get("name", "Generated Pipeline")
        description = pipeline.get("description", "")

        return f"""# {pipeline_name}

{description}

## Prerequisites

1. Salesforce CLI (sfdx) installed
2. Authenticated to a Salesforce org

## Setup

### 1. Deploy to Salesforce

```bash
sfdx force:source:deploy -p force-app
```

### 2. Configure Named Credentials

1. Go to Setup > Named Credentials
2. Create credentials for OpenAI and/or Anthropic with your API keys

### 3. Configure Remote Site Settings

Remote site settings are included but may need to be enabled in Setup.

## Usage

### From Apex

```apex
{class_name} pipeline = new {class_name}();
Map<String, Object> inputs = new Map<String, Object>{{
    'input' => 'Your input text here'
}};
{class_name}.PipelineResult result = pipeline.execute(inputs);
System.debug(result.outputs);
```

### From Flow

1. Add an Action element to your Flow
2. Search for "Execute {pipeline_name}"
3. Configure the Input JSON or Input Value
4. Use the Output JSON or Output Value in subsequent elements

## Testing

```bash
sfdx force:apex:test:run -n {class_name}Test -r human
```

---

*Generated by FlowMason Code Generator v{self.generator_version}*
"""

    def _get_deployment_config(
        self,
        options: CodeGenOptions,
        class_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get deployment configuration."""
        return {
            "platform": "salesforce",
            "deploy_command": "sfdx force:source:deploy -p force-app",
            "test_command": f"sfdx force:apex:test:run -n {class_name}Test",
        }

    def _get_deploy_instructions(
        self,
        options: CodeGenOptions,
        class_name: str,
    ) -> Optional[str]:
        """Get deployment instructions."""
        return f"""## Deploy to Salesforce

1. Install Salesforce CLI: `npm install -g @salesforce/cli`
2. Login: `sf org login web`
3. Deploy: `sfdx force:source:deploy -p force-app`
4. Run tests: `sfdx force:apex:test:run -n {class_name}Test`

### Configure API Access

1. Create Named Credentials for OpenAI/Anthropic in Setup
2. Ensure Remote Site Settings are active
"""


# Singleton instance
_generator: Optional[ApexCodeGenerator] = None


def get_apex_code_generator() -> ApexCodeGenerator:
    """Get the singleton ApexCodeGenerator instance."""
    global _generator
    if _generator is None:
        _generator = ApexCodeGenerator()
    return _generator
