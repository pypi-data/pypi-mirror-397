"""
FlowMason MCP Server Implementation

Exposes FlowMason pipelines as MCP tools for AI assistants.

Features:
- List available pipelines
- Get pipeline details and input schemas
- Execute pipelines with inputs
- Access component registry

Usage:
    fm mcp serve
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# MCP SDK (optional dependency)
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)


def create_mcp_server(
    pipelines_dir: Optional[Path] = None,
    studio_url: str = "http://localhost:8999",
) -> "FastMCP":
    """
    Create a FlowMason MCP server.

    Args:
        pipelines_dir: Directory containing .pipeline.json files
        studio_url: URL of FlowMason Studio API (for execution)

    Returns:
        Configured FastMCP server instance
    """
    if not MCP_AVAILABLE:
        raise ImportError(
            "MCP SDK not installed. Install with: pip install mcp"
        )

    # Initialize server
    mcp = FastMCP("flowmason")

    # Resolve pipelines directory
    if pipelines_dir is None:
        # Look in current directory and common locations
        for candidate in [
            Path.cwd() / "pipelines",
            Path.cwd(),
            Path.home() / ".flowmason" / "pipelines",
        ]:
            if candidate.exists() and list(candidate.glob("*.pipeline.json")):
                pipelines_dir = candidate
                break

    if pipelines_dir is None:
        pipelines_dir = Path.cwd()

    logger.info("FlowMason MCP Server initialized")
    logger.info(f"Pipelines directory: {pipelines_dir}")
    logger.info(f"Studio URL: {studio_url}")

    # =========================================================================
    # Tools
    # =========================================================================

    @mcp.tool()
    async def list_pipelines() -> str:
        """
        List all available FlowMason pipelines.

        Returns a list of pipeline names, descriptions, and their input requirements.
        """
        pipelines = []

        if pipelines_dir and pipelines_dir.exists():
            for pipeline_file in pipelines_dir.glob("*.pipeline.json"):
                try:
                    with open(pipeline_file) as f:
                        data = json.load(f)
                        pipelines.append({
                            "name": data.get("name", pipeline_file.stem),
                            "file": pipeline_file.name,
                            "version": data.get("version", "1.0.0"),
                            "description": data.get("description", "No description"),
                            "stages": len(data.get("stages", [])),
                        })
                except Exception as e:
                    logger.warning(f"Failed to load {pipeline_file}: {e}")

        if not pipelines:
            return "No pipelines found. Place .pipeline.json files in the pipelines directory."

        result = "Available Pipelines:\n\n"
        for p in pipelines:
            result += f"## {p['name']} (v{p['version']})\n"
            result += f"File: {p['file']}\n"
            result += f"Stages: {p['stages']}\n"
            result += f"Description: {p['description']}\n\n"

        return result

    @mcp.tool()
    async def get_pipeline(pipeline_name: str) -> str:
        """
        Get detailed information about a specific pipeline.

        Args:
            pipeline_name: Name of the pipeline or filename (with or without .pipeline.json)

        Returns:
            Pipeline configuration including stages, input schema, and description.
        """
        # Find the pipeline file
        pipeline_file = None

        if pipelines_dir and pipelines_dir.exists():
            # Try exact filename match first
            candidates = [
                pipelines_dir / pipeline_name,
                pipelines_dir / f"{pipeline_name}.pipeline.json",
            ]

            for candidate in candidates:
                if candidate.exists():
                    pipeline_file = candidate
                    break

            # Try matching by pipeline name in JSON
            if not pipeline_file:
                for f in pipelines_dir.glob("*.pipeline.json"):
                    try:
                        with open(f) as fp:
                            data = json.load(fp)
                            if data.get("name", "").lower() == pipeline_name.lower():
                                pipeline_file = f
                                break
                    except Exception:
                        pass

        if not pipeline_file or not pipeline_file.exists():
            return f"Pipeline '{pipeline_name}' not found. Use list_pipelines to see available pipelines."

        try:
            with open(pipeline_file) as pipeline_fp:
                data = json.load(pipeline_fp)

            result = f"# {data.get('name', pipeline_file.stem)}\n\n"
            result += f"**Version:** {data.get('version', '1.0.0')}\n"
            result += f"**Description:** {data.get('description', 'No description')}\n\n"

            # Input schema
            input_schema = data.get("input_schema", {})
            if input_schema:
                result += "## Input Schema\n\n"
                properties = input_schema.get("properties", {})
                required = input_schema.get("required", [])

                for prop_name, prop_def in properties.items():
                    req = " (required)" if prop_name in required else ""
                    prop_type = prop_def.get("type", "any")
                    desc = prop_def.get("description", "")
                    default = prop_def.get("default")
                    default_str = f" [default: {json.dumps(default)}]" if default is not None else ""

                    result += f"- **{prop_name}**{req}: {prop_type}{default_str}\n"
                    if desc:
                        result += f"  {desc}\n"

            # Stages
            stages = data.get("stages", [])
            if stages:
                result += "\n## Stages\n\n"
                for i, stage in enumerate(stages, 1):
                    result += f"{i}. **{stage.get('name', stage.get('id', 'Unknown'))}** ({stage.get('component_type', 'unknown')})\n"

            return result

        except Exception as e:
            return f"Error loading pipeline: {e}"

    @mcp.tool()
    async def run_pipeline(
        pipeline_name: str,
        input_data: Optional[str] = None,
    ) -> str:
        """
        Execute a FlowMason pipeline.

        Args:
            pipeline_name: Name of the pipeline to run
            input_data: JSON string with input data for the pipeline (optional)

        Returns:
            Pipeline execution result or error message.
        """
        import httpx

        # Parse input
        inputs = {}
        if input_data:
            try:
                inputs = json.loads(input_data)
            except json.JSONDecodeError as e:
                return f"Invalid input JSON: {e}"

        # Find pipeline file to get the full name
        if pipelines_dir and pipelines_dir.exists():
            for f in pipelines_dir.glob("*.pipeline.json"):
                try:
                    with open(f) as fp:
                        data = json.load(fp)
                        if data.get("name", "").lower() == pipeline_name.lower():
                            pipeline_name = data.get("name")
                            break
                except Exception:
                    pass

        # Try to execute via Studio API
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # First, try the /run endpoint
                response = await client.post(
                    f"{studio_url}/api/v1/run",
                    json={
                        "pipeline": pipeline_name,
                        "input": inputs,
                        "async_mode": False,  # Wait for result
                    },
                )

                if response.status_code == 404:
                    return f"Pipeline '{pipeline_name}' not found in Studio. Is Studio running and the pipeline uploaded?"

                if response.status_code == 200 or response.status_code == 202:
                    result = response.json()

                    if result.get("status") == "completed":
                        output = result.get("result", {})
                        return f"Pipeline completed successfully!\n\nResult:\n```json\n{json.dumps(output, indent=2)}\n```"
                    elif result.get("status") == "failed":
                        error = result.get("error", "Unknown error")
                        return f"Pipeline failed: {error}"
                    else:
                        return f"Pipeline status: {result.get('status')}\nRun ID: {result.get('run_id')}"

                return f"Studio returned error: {response.status_code} - {response.text}"

        except httpx.ConnectError:
            return f"Cannot connect to FlowMason Studio at {studio_url}. Start Studio with: fm studio start"
        except Exception as e:
            return f"Error executing pipeline: {e}"

    @mcp.tool()
    async def list_components() -> str:
        """
        List available FlowMason components (operators and nodes).

        Returns a list of component types with their descriptions.
        """
        import httpx

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{studio_url}/api/v1/registry/components")

                if response.status_code == 200:
                    components = response.json()

                    if not components:
                        return "No components found. Is FlowMason Lab installed?"

                    result = "Available Components:\n\n"

                    # Group by category
                    by_category: Dict[str, List[Dict[str, Any]]] = {}
                    for comp in components:
                        cat = comp.get("category", "uncategorized")
                        if cat not in by_category:
                            by_category[cat] = []
                        by_category[cat].append(comp)

                    for category, comps in sorted(by_category.items()):
                        result += f"## {category.title()}\n\n"
                        for c in comps:
                            llm = " (requires LLM)" if c.get("requires_llm") else ""
                            result += f"- **{c.get('name')}** (`{c.get('component_type')}`){llm}\n"
                            result += f"  {c.get('description', 'No description')}\n"
                        result += "\n"

                    return result

                return f"Error fetching components: {response.status_code}"

        except httpx.ConnectError:
            return f"Cannot connect to FlowMason Studio at {studio_url}. Start Studio with: fm studio start"
        except Exception as e:
            return f"Error listing components: {e}"

    @mcp.tool()
    async def get_component(component_type: str) -> str:
        """
        Get detailed information about a specific component.

        Args:
            component_type: The component type (e.g., 'generator', 'json_transform')

        Returns:
            Component configuration schema and usage information.
        """
        import httpx

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{studio_url}/api/v1/registry/components/{component_type}"
                )

                if response.status_code == 404:
                    return f"Component '{component_type}' not found. Use list_components to see available components."

                if response.status_code == 200:
                    comp = response.json()

                    result = f"# {comp.get('name')}\n\n"
                    result += f"**Type:** `{comp.get('component_type')}`\n"
                    result += f"**Kind:** {comp.get('component_kind', 'operator')}\n"
                    result += f"**Category:** {comp.get('category', 'uncategorized')}\n"
                    result += f"**Version:** {comp.get('version', '1.0.0')}\n"

                    if comp.get("requires_llm"):
                        result += "**Requires LLM:** Yes\n"

                    result += f"\n{comp.get('description', 'No description')}\n"

                    # Input schema
                    input_schema = comp.get("input_schema", {})
                    if input_schema and input_schema.get("properties"):
                        result += "\n## Configuration\n\n"
                        for prop, schema in input_schema.get("properties", {}).items():
                            prop_type = schema.get("type", "any")
                            desc = schema.get("description", "")
                            result += f"- **{prop}** ({prop_type}): {desc}\n"

                    # Output schema
                    output_schema = comp.get("output_schema", {})
                    if output_schema and output_schema.get("properties"):
                        result += "\n## Output\n\n"
                        for prop, schema in output_schema.get("properties", {}).items():
                            prop_type = schema.get("type", "any")
                            desc = schema.get("description", "")
                            result += f"- **{prop}** ({prop_type}): {desc}\n"

                    return result

                return f"Error fetching component: {response.status_code}"

        except httpx.ConnectError:
            return f"Cannot connect to FlowMason Studio at {studio_url}. Start Studio with: fm studio start"
        except Exception as e:
            return f"Error getting component: {e}"

    # =========================================================================
    # AI Generation Tools
    # =========================================================================

    @mcp.tool()
    async def create_pipeline(
        name: str,
        description: str,
        stages_json: str,
        input_schema_json: Optional[str] = None,
    ) -> str:
        """
        Create a new FlowMason pipeline from a specification.

        Use this to generate pipelines programmatically. You should first use
        list_components to understand available component types.

        Args:
            name: Pipeline name (e.g., "content-summarizer")
            description: What the pipeline does
            stages_json: JSON array of stage objects. Each stage needs:
                - id: Unique stage identifier
                - name: Human-readable stage name
                - component_type: Type of component (use list_components to see options)
                - config: Configuration object for the component
                - depends_on: (optional) Array of stage IDs this stage depends on
            input_schema_json: (optional) JSON Schema for pipeline inputs

        Returns:
            Path to the created pipeline file or error message.

        Example stages_json:
            [
                {
                    "id": "extract",
                    "name": "Extract Key Points",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Extract key points from: {{input.text}}"
                    }
                },
                {
                    "id": "summarize",
                    "name": "Summarize",
                    "component_type": "generator",
                    "config": {
                        "prompt": "Summarize these key points: {{stages.extract.output}}"
                    },
                    "depends_on": ["extract"]
                }
            ]
        """
        try:
            stages = json.loads(stages_json)
        except json.JSONDecodeError as e:
            return f"Invalid stages JSON: {e}"

        input_schema = {}
        if input_schema_json:
            try:
                input_schema = json.loads(input_schema_json)
            except json.JSONDecodeError as e:
                return f"Invalid input_schema JSON: {e}"

        # Validate stages structure
        for i, stage in enumerate(stages):
            if "id" not in stage:
                return f"Stage {i} missing required 'id' field"
            if "component_type" not in stage:
                return f"Stage '{stage.get('id', i)}' missing required 'component_type' field"

        # Build pipeline config
        pipeline = {
            "name": name,
            "version": "1.0.0",
            "description": description,
            "stages": stages,
        }

        if input_schema:
            pipeline["input_schema"] = input_schema

        # Save pipeline file
        safe_name = name.lower().replace(" ", "-").replace("_", "-")
        if pipelines_dir:
            output_path = pipelines_dir / f"{safe_name}.pipeline.json"
        else:
            output_path = Path.cwd() / f"{safe_name}.pipeline.json"

        try:
            with open(output_path, "w") as f:
                json.dump(pipeline, f, indent=2)

            result = f"Pipeline created successfully!\n\n"
            result += f"**File:** {output_path}\n"
            result += f"**Name:** {name}\n"
            result += f"**Stages:** {len(stages)}\n\n"
            result += "```json\n"
            result += json.dumps(pipeline, indent=2)
            result += "\n```\n\n"
            result += "Run with: `fm run " + str(output_path) + "`"

            return result

        except Exception as e:
            return f"Error saving pipeline: {e}"

    @mcp.tool()
    async def generate_stage(
        stage_type: str,
        purpose: str,
        input_source: str = "input",
    ) -> str:
        """
        Generate a stage configuration for a specific component type.

        This helps you build pipeline stages by providing the correct configuration
        structure for each component type.

        Args:
            stage_type: Component type (e.g., "generator", "filter", "json_transform")
            purpose: What this stage should do (used to generate prompt/config)
            input_source: Where to get input from ("input" for pipeline input,
                         or "stages.<stage_id>" for output from another stage)

        Returns:
            Stage configuration JSON that can be used in create_pipeline.
        """
        import httpx
        import uuid

        stage_id = f"{stage_type}-{uuid.uuid4().hex[:6]}"

        # Fetch component info for accurate config
        component_info = {}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{studio_url}/api/v1/registry/components/{stage_type}"
                )
                if response.status_code == 200:
                    component_info = response.json()
        except Exception:
            pass

        # Generate configuration based on component type
        config: Dict[str, Any] = {}

        if stage_type == "generator":
            config = {
                "prompt": f"Based on the following input, {purpose}:\n\n{{{{{input_source}}}}}",
                "max_tokens": 1000,
                "temperature": 0.7,
            }
        elif stage_type == "filter":
            config = {
                "items_path": f"{{{{{input_source}.items}}}}",
                "condition": f"# Condition for: {purpose}\nTrue",
            }
        elif stage_type == "json_transform":
            config = {
                "template": {
                    "result": f"{{{{{input_source}}}}}",
                    "metadata": {
                        "purpose": purpose,
                    },
                },
            }
        elif stage_type == "selector":
            config = {
                "items_path": f"{{{{{input_source}.items}}}}",
                "select": "first",
                "count": 1,
            }
        elif stage_type == "critic":
            config = {
                "prompt": f"Evaluate the following for: {purpose}\n\nContent: {{{{{input_source}}}}}",
                "criteria": ["accuracy", "relevance", "quality"],
            }
        elif stage_type == "loop":
            config = {
                "items_path": f"{{{{{input_source}.items}}}}",
                "max_iterations": 10,
            }
        elif stage_type == "http_request":
            config = {
                "url": "https://api.example.com/endpoint",
                "method": "POST",
                "body": f"{{{{{input_source}}}}}",
            }
        else:
            # Generic config
            config = {
                "input": f"{{{{{input_source}}}}}",
                "purpose": purpose,
            }

        stage = {
            "id": stage_id,
            "name": purpose[:50],
            "component_type": stage_type,
            "config": config,
        }

        if input_source != "input" and input_source.startswith("stages."):
            # Add dependency
            dep_stage_id = input_source.replace("stages.", "").split(".")[0]
            stage["depends_on"] = [dep_stage_id]

        result = f"Generated stage configuration:\n\n"
        result += "```json\n"
        result += json.dumps(stage, indent=2)
        result += "\n```\n\n"

        if component_info:
            result += f"**Component:** {component_info.get('name', stage_type)}\n"
            result += f"**Description:** {component_info.get('description', 'N/A')}\n"
            if component_info.get("requires_llm"):
                result += "**Note:** This component requires an LLM provider.\n"

        return result

    @mcp.tool()
    async def validate_pipeline_config(pipeline_json: str) -> str:
        """
        Validate a pipeline configuration before creating it.

        Args:
            pipeline_json: Full pipeline JSON configuration

        Returns:
            Validation result with any errors or warnings.
        """
        try:
            pipeline = json.loads(pipeline_json)
        except json.JSONDecodeError as e:
            return f"Invalid JSON: {e}"

        errors: List[str] = []
        warnings: List[str] = []

        # Required fields
        if "name" not in pipeline:
            errors.append("Missing required field: 'name'")

        if "stages" not in pipeline:
            errors.append("Missing required field: 'stages'")
        elif not isinstance(pipeline["stages"], list):
            errors.append("'stages' must be an array")
        elif len(pipeline["stages"]) == 0:
            errors.append("Pipeline must have at least one stage")
        else:
            stage_ids = set()
            for i, stage in enumerate(pipeline["stages"]):
                # Required stage fields
                if "id" not in stage:
                    errors.append(f"Stage {i}: missing 'id' field")
                else:
                    if stage["id"] in stage_ids:
                        errors.append(f"Stage {i}: duplicate stage ID '{stage['id']}'")
                    stage_ids.add(stage["id"])

                if "component_type" not in stage:
                    errors.append(f"Stage {i}: missing 'component_type' field")

                # Check dependencies
                if "depends_on" in stage:
                    for dep in stage["depends_on"]:
                        if dep not in stage_ids:
                            # Could be forward reference, which is OK
                            found = any(s.get("id") == dep for s in pipeline["stages"])
                            if not found:
                                errors.append(
                                    f"Stage '{stage.get('id', i)}': depends on unknown stage '{dep}'"
                                )

                # Warnings for best practices
                if "name" not in stage:
                    warnings.append(f"Stage '{stage.get('id', i)}': consider adding 'name' for clarity")

        # Recommendations
        if "description" not in pipeline:
            warnings.append("Consider adding a 'description' field")

        if "version" not in pipeline:
            warnings.append("Consider adding a 'version' field (e.g., '1.0.0')")

        if "input_schema" not in pipeline:
            warnings.append("Consider adding 'input_schema' to document expected inputs")

        # Build result
        if errors:
            result = "## Validation Failed\n\n"
            result += "**Errors:**\n"
            for error in errors:
                result += f"- {error}\n"
        else:
            result = "## Validation Passed\n\n"

        if warnings:
            result += "\n**Warnings:**\n"
            for warning in warnings:
                result += f"- {warning}\n"

        if not errors and not warnings:
            result += "Pipeline configuration is valid with no warnings."

        return result

    @mcp.tool()
    async def suggest_pipeline(task_description: str) -> str:
        """
        Get suggestions for building a pipeline based on a task description.

        Describe what you want to accomplish, and this tool will suggest
        appropriate components and pipeline structure.

        Args:
            task_description: Natural language description of what you want the pipeline to do

        Returns:
            Suggested pipeline structure with recommended components.
        """
        import httpx

        # Fetch available components
        components: List[Dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{studio_url}/api/v1/registry/components")
                if response.status_code == 200:
                    components = response.json()
        except Exception:
            pass

        # Build suggestion based on keywords in task description
        task_lower = task_description.lower()
        suggested_stages: List[Dict[str, str]] = []

        # Analyze task and suggest components
        if any(word in task_lower for word in ["summarize", "summary", "condense"]):
            suggested_stages.append({
                "component": "generator",
                "purpose": "Generate summary",
                "rationale": "Use LLM to create a summary of the input",
            })

        if any(word in task_lower for word in ["filter", "select", "choose", "pick"]):
            suggested_stages.append({
                "component": "filter",
                "purpose": "Filter items based on criteria",
                "rationale": "Filter data to include only relevant items",
            })

        if any(word in task_lower for word in ["transform", "convert", "format", "restructure"]):
            suggested_stages.append({
                "component": "json_transform",
                "purpose": "Transform data structure",
                "rationale": "Restructure data into desired format",
            })

        if any(word in task_lower for word in ["api", "http", "fetch", "request", "call"]):
            suggested_stages.append({
                "component": "http_request",
                "purpose": "Call external API",
                "rationale": "Make HTTP requests to external services",
            })

        if any(word in task_lower for word in ["loop", "iterate", "each", "batch"]):
            suggested_stages.append({
                "component": "loop",
                "purpose": "Process items in a loop",
                "rationale": "Iterate over items and process each one",
            })

        if any(word in task_lower for word in ["validate", "check", "verify", "review"]):
            suggested_stages.append({
                "component": "critic",
                "purpose": "Validate or review content",
                "rationale": "Use LLM to evaluate and validate content",
            })

        if any(word in task_lower for word in ["generate", "create", "write", "produce"]):
            if not any(s["component"] == "generator" for s in suggested_stages):
                suggested_stages.append({
                    "component": "generator",
                    "purpose": "Generate content",
                    "rationale": "Use LLM to generate new content",
                })

        # Build result
        result = f"## Suggested Pipeline for: {task_description[:100]}...\n\n"

        if suggested_stages:
            result += "### Recommended Components\n\n"
            for i, stage in enumerate(suggested_stages, 1):
                result += f"**{i}. {stage['component']}**\n"
                result += f"   Purpose: {stage['purpose']}\n"
                result += f"   Rationale: {stage['rationale']}\n\n"

            result += "### Example Pipeline Structure\n\n"
            result += "```json\n"

            example_stages = []
            prev_stage_id = None
            for i, stage in enumerate(suggested_stages):
                stage_id = f"{stage['component']}-{i+1}"
                stage_config: Dict[str, Any] = {
                    "id": stage_id,
                    "name": stage["purpose"],
                    "component_type": stage["component"],
                    "config": {},
                }
                if prev_stage_id:
                    stage_config["depends_on"] = [prev_stage_id]
                example_stages.append(stage_config)
                prev_stage_id = stage_id

            example = {
                "name": "suggested-pipeline",
                "description": task_description[:200],
                "version": "1.0.0",
                "stages": example_stages,
            }
            result += json.dumps(example, indent=2)
            result += "\n```\n\n"

            result += "Use `generate_stage` to get detailed configuration for each stage, "
            result += "then `create_pipeline` to create the final pipeline."
        else:
            result += "I couldn't automatically suggest components for this task.\n\n"
            result += "Please use `list_components` to see available components, "
            result += "and `get_component` to learn about each one."

        return result

    return mcp


def run_mcp_server(
    pipelines_dir: Optional[Path] = None,
    studio_url: str = "http://localhost:8999",
    transport: str = "stdio",
):
    """
    Run the FlowMason MCP server.

    Args:
        pipelines_dir: Directory containing pipeline files
        studio_url: FlowMason Studio API URL
        transport: Transport type ('stdio' or 'sse')
    """
    mcp = create_mcp_server(pipelines_dir, studio_url)
    mcp.run(transport=transport)
