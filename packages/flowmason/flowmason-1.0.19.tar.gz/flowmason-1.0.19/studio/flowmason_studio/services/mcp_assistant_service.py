"""
MCP AI Assistant Service.

Provides AI-powered assistance for discovering and using MCP tools:
- Task analysis and tool recommendations
- Tool explanations and documentation
- Smart parameter resolution
- Tool chain creation
"""

import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flowmason_studio.models.mcp_assistant import (
    AutocompleteResult,
    AutocompleteSuggestion,
    ConversationContext,
    ConversationMessage,
    EnhancedTool,
    SmartInvokeResponse,
    TaskAnalysis,
    ToolCapability,
    ToolCategory,
    ToolChain,
    ToolChainStep,
    ToolExplanation,
    ToolRecommendation,
)


# Tool catalog with enhanced metadata
TOOL_CATALOG: Dict[str, Dict[str, Any]] = {
    "list_pipelines": {
        "category": ToolCategory.PIPELINE,
        "description": "List all available FlowMason pipelines in the workspace",
        "capabilities": [
            {"name": "discovery", "description": "Find available pipelines"},
            {"name": "inspection", "description": "View pipeline metadata"},
        ],
        "when_to_use": [
            "When you need to know what pipelines are available",
            "Before running a pipeline to check its existence",
            "To get an overview of the workspace",
        ],
        "prerequisites": [],
        "related_tools": ["get_pipeline", "run_pipeline", "list_components"],
        "parameters": {},
        "required_params": [],
    },
    "list_components": {
        "category": ToolCategory.COMPONENT,
        "description": "List all available FlowMason components for building pipelines",
        "capabilities": [
            {"name": "discovery", "description": "Find available components"},
            {"name": "categorization", "description": "View components by category"},
        ],
        "when_to_use": [
            "When building a new pipeline",
            "To find components for a specific task",
            "To explore available functionality",
        ],
        "prerequisites": [],
        "related_tools": ["get_component", "suggest_pipeline"],
        "parameters": {},
        "required_params": [],
    },
    "get_component": {
        "category": ToolCategory.COMPONENT,
        "description": "Get detailed information about a specific component",
        "capabilities": [
            {"name": "documentation", "description": "View component details"},
            {"name": "schema", "description": "See input/output schemas"},
        ],
        "when_to_use": [
            "After finding a component with list_components",
            "When you need to understand component configuration",
            "Before using a component in a pipeline",
        ],
        "prerequisites": ["Know the component_type from list_components"],
        "related_tools": ["list_components", "generate_stage"],
        "parameters": {
            "component_type": {
                "type": "string",
                "description": "The component type identifier",
                "required": True,
            },
        },
        "required_params": ["component_type"],
    },
    "suggest_pipeline": {
        "category": ToolCategory.PIPELINE,
        "description": "Get AI-powered suggestions for building a pipeline based on a task description",
        "capabilities": [
            {"name": "recommendation", "description": "Suggest appropriate components"},
            {"name": "structure", "description": "Propose pipeline structure"},
        ],
        "when_to_use": [
            "When starting to build a new pipeline",
            "When unsure which components to use",
            "To get AI assistance with pipeline design",
        ],
        "prerequisites": [],
        "related_tools": ["list_components", "generate_stage", "create_pipeline"],
        "parameters": {
            "task_description": {
                "type": "string",
                "description": "Natural language description of what the pipeline should do",
                "required": True,
            },
        },
        "required_params": ["task_description"],
    },
    "generate_stage": {
        "category": ToolCategory.PIPELINE,
        "description": "Generate a stage configuration for a component",
        "capabilities": [
            {"name": "configuration", "description": "Generate stage config"},
            {"name": "templating", "description": "Create stage templates"},
        ],
        "when_to_use": [
            "After choosing a component type",
            "When building a pipeline stage by stage",
            "To get a starting configuration for a stage",
        ],
        "prerequisites": ["Choose component type from list_components"],
        "related_tools": ["get_component", "create_pipeline", "suggest_pipeline"],
        "parameters": {
            "stage_type": {
                "type": "string",
                "description": "The component type for the stage",
                "required": True,
            },
            "purpose": {
                "type": "string",
                "description": "What the stage should accomplish",
                "required": True,
            },
            "input_source": {
                "type": "string",
                "description": "Where input comes from (e.g., 'input' or 'stages.prev.output')",
                "default": "input",
            },
        },
        "required_params": ["stage_type", "purpose"],
    },
    "validate_pipeline_config": {
        "category": ToolCategory.UTILITY,
        "description": "Validate a pipeline configuration for errors",
        "capabilities": [
            {"name": "validation", "description": "Check for configuration errors"},
            {"name": "linting", "description": "Suggest improvements"},
        ],
        "when_to_use": [
            "Before saving or running a pipeline",
            "After making changes to a pipeline",
            "To check for common mistakes",
        ],
        "prerequisites": ["Have a pipeline configuration ready"],
        "related_tools": ["create_pipeline", "suggest_pipeline"],
        "parameters": {
            "pipeline_json": {
                "type": "string",
                "description": "Pipeline configuration as JSON string",
                "required": True,
            },
        },
        "required_params": ["pipeline_json"],
    },
    "create_pipeline": {
        "category": ToolCategory.PIPELINE,
        "description": "Create a new pipeline from a configuration",
        "capabilities": [
            {"name": "creation", "description": "Create new pipelines"},
            {"name": "persistence", "description": "Save pipeline to storage"},
        ],
        "when_to_use": [
            "After designing a pipeline structure",
            "To save a pipeline for later use",
            "After generating stages with generate_stage",
        ],
        "prerequisites": [
            "Have stages ready from generate_stage or suggest_pipeline",
            "Pipeline should be validated with validate_pipeline_config",
        ],
        "related_tools": ["suggest_pipeline", "generate_stage", "validate_pipeline_config"],
        "parameters": {
            "name": {
                "type": "string",
                "description": "Name for the pipeline",
                "required": True,
            },
            "description": {
                "type": "string",
                "description": "Description of what the pipeline does",
                "required": True,
            },
            "stages_json": {
                "type": "string",
                "description": "Stage configurations as JSON string",
                "required": True,
            },
            "input_schema_json": {
                "type": "string",
                "description": "Input schema as JSON string",
                "required": False,
            },
        },
        "required_params": ["name", "description", "stages_json"],
    },
}


class MCPAssistantService:
    """Service for AI-powered MCP tool assistance."""

    def __init__(self):
        """Initialize the service."""
        self._conversations: Dict[str, ConversationContext] = {}
        self._tool_catalog = TOOL_CATALOG

    def get_enhanced_tools(self) -> List[EnhancedTool]:
        """Get all tools with enhanced metadata."""
        tools = []
        for name, info in self._tool_catalog.items():
            capabilities = [
                ToolCapability(**cap) for cap in info.get("capabilities", [])
            ]
            tools.append(EnhancedTool(
                name=name,
                description=info["description"],
                category=info["category"],
                capabilities=capabilities,
                when_to_use=info.get("when_to_use", []),
                prerequisites=info.get("prerequisites", []),
                related_tools=info.get("related_tools", []),
                parameters=info.get("parameters", {}),
                required_params=info.get("required_params", []),
                optional_params=[
                    k for k, v in info.get("parameters", {}).items()
                    if not v.get("required", False)
                ],
            ))
        return tools

    async def analyze_task(
        self,
        task: str,
        available_data: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[str]] = None,
    ) -> TaskAnalysis:
        """Analyze a task and recommend appropriate tools."""
        task_lower = task.lower()

        # Determine intent
        intent = "general"
        if any(w in task_lower for w in ["list", "show", "find", "get"]):
            intent = "discovery"
        elif any(w in task_lower for w in ["create", "build", "make", "generate"]):
            intent = "creation"
        elif any(w in task_lower for w in ["run", "execute", "process"]):
            intent = "execution"
        elif any(w in task_lower for w in ["validate", "check", "verify"]):
            intent = "validation"
        elif any(w in task_lower for w in ["explain", "describe", "how"]):
            intent = "understanding"

        # Identify required capabilities
        capabilities: List[str] = []
        if "pipeline" in task_lower:
            capabilities.append("pipeline_management")
        if "component" in task_lower:
            capabilities.append("component_discovery")
        if any(w in task_lower for w in ["api", "http", "external"]):
            capabilities.append("external_integration")
        if any(w in task_lower for w in ["transform", "convert", "format"]):
            capabilities.append("data_transformation")
        if any(w in task_lower for w in ["ai", "llm", "generate", "summarize"]):
            capabilities.append("ai_processing")

        # Generate recommendations
        recommendations = await self._recommend_tools(task, intent, capabilities)

        # Build suggested workflow
        workflow = self._build_workflow(intent, recommendations)

        # Identify data requirements
        data_requirements: List[str] = []
        if "input" in task_lower:
            data_requirements.append("input_data")
        if "file" in task_lower:
            data_requirements.append("file_path")
        if "api" in task_lower:
            data_requirements.append("api_endpoint")

        return TaskAnalysis(
            task=task,
            intent=intent,
            required_capabilities=capabilities,
            data_requirements=data_requirements,
            suggested_workflow=workflow,
            tool_recommendations=recommendations,
        )

    async def explain_tool(
        self,
        tool_name: str,
        context: Optional[str] = None,
        detail_level: str = "normal",
    ) -> ToolExplanation:
        """Get a detailed explanation of a tool."""
        tool_info = self._tool_catalog.get(tool_name)
        if not tool_info:
            raise ValueError(f"Tool '{tool_name}' not found")

        # Build summary
        summary = tool_info["description"]

        # Build detailed description based on detail level
        detailed = f"{tool_info['description']}\n\n"

        if detail_level in ["normal", "detailed"]:
            detailed += "**When to Use:**\n"
            for use_case in tool_info.get("when_to_use", []):
                detailed += f"- {use_case}\n"

            if tool_info.get("prerequisites"):
                detailed += "\n**Prerequisites:**\n"
                for prereq in tool_info["prerequisites"]:
                    detailed += f"- {prereq}\n"

        if detail_level == "detailed":
            detailed += "\n**Related Tools:**\n"
            for related in tool_info.get("related_tools", []):
                detailed += f"- {related}\n"

        # Parameter explanations
        param_explanations = {}
        for param, info in tool_info.get("parameters", {}).items():
            param_explanations[param] = info.get("description", "No description")

        # Generate tips
        tips = self._generate_tips(tool_name, tool_info)

        # Generate warnings
        warnings = self._generate_warnings(tool_name, tool_info)

        return ToolExplanation(
            tool_name=tool_name,
            summary=summary,
            detailed_description=detailed,
            parameter_explanations=param_explanations,
            common_use_cases=tool_info.get("when_to_use", []),
            tips=tips,
            warnings=warnings,
            see_also=tool_info.get("related_tools", []),
        )

    async def create_tool_chain(
        self,
        goal: str,
        available_tools: Optional[List[str]] = None,
        max_steps: int = 5,
    ) -> ToolChain:
        """Create a chain of tools to accomplish a goal."""
        chain_id = str(uuid.uuid4())
        goal_lower = goal.lower()

        # Determine tools needed
        tools = available_tools or list(self._tool_catalog.keys())

        steps: List[ToolChainStep] = []

        # Check for creation-related patterns
        is_creation = any(w in goal_lower for w in [
            "create", "build", "make", "set up", "setup", "design",
            "develop", "implement", "construct", "generate"
        ])
        is_workflow = any(w in goal_lower for w in [
            "pipeline", "workflow", "process", "chain", "flow", "automation"
        ])
        is_data_task = any(w in goal_lower for w in [
            "data", "processing", "transform", "etl", "extract", "analyze"
        ])

        # Build chain based on goal analysis
        if is_creation and (is_workflow or is_data_task):
            # Pipeline/workflow creation
            steps = [
                ToolChainStep(
                    order=1,
                    tool_name="list_components",
                    description="Discover available components",
                    output_key="components",
                ),
                ToolChainStep(
                    order=2,
                    tool_name="suggest_pipeline",
                    description="Get pipeline suggestions based on goal",
                    parameters={"task_description": goal},
                    output_key="suggestion",
                ),
                ToolChainStep(
                    order=3,
                    tool_name="validate_pipeline_config",
                    description="Validate the suggested pipeline",
                    input_mapping={"pipeline_json": "suggestion.example_pipeline"},
                    output_key="validation",
                ),
                ToolChainStep(
                    order=4,
                    tool_name="create_pipeline",
                    description="Create the validated pipeline",
                    input_mapping={
                        "stages_json": "suggestion.stages",
                    },
                    output_key="pipeline",
                ),
            ]
        elif "list" in goal_lower or "find" in goal_lower or "show" in goal_lower:
            # Discovery workflow
            if "pipeline" in goal_lower:
                steps = [
                    ToolChainStep(
                        order=1,
                        tool_name="list_pipelines",
                        description="List all available pipelines",
                        output_key="pipelines",
                    ),
                ]
            elif "component" in goal_lower:
                steps = [
                    ToolChainStep(
                        order=1,
                        tool_name="list_components",
                        description="List all available components",
                        output_key="components",
                    ),
                ]
            else:
                # General discovery
                steps = [
                    ToolChainStep(
                        order=1,
                        tool_name="list_pipelines",
                        description="List available pipelines",
                        output_key="pipelines",
                    ),
                    ToolChainStep(
                        order=2,
                        tool_name="list_components",
                        description="List available components",
                        output_key="components",
                    ),
                ]
        elif "understand" in goal_lower or "learn" in goal_lower or "explore" in goal_lower:
            # Learning workflow
            steps = [
                ToolChainStep(
                    order=1,
                    tool_name="list_components",
                    description="Get an overview of available components",
                    output_key="components",
                ),
                ToolChainStep(
                    order=2,
                    tool_name="get_component",
                    description="Get details on specific components of interest",
                    parameters={"component_type": "generator"},
                    output_key="component_details",
                ),
            ]
        elif is_data_task:
            # Data processing workflow (without explicit creation keyword)
            steps = [
                ToolChainStep(
                    order=1,
                    tool_name="list_components",
                    description="Explore data processing components",
                    output_key="components",
                ),
                ToolChainStep(
                    order=2,
                    tool_name="suggest_pipeline",
                    description="Get suggestions for data processing",
                    parameters={"task_description": goal},
                    output_key="suggestion",
                ),
            ]
        else:
            # Generic workflow based on goal keywords
            if "component" in goal_lower:
                steps.append(ToolChainStep(
                    order=len(steps) + 1,
                    tool_name="list_components",
                    description="Explore available components",
                    output_key="components",
                ))

            if "pipeline" in goal_lower or is_workflow:
                steps.append(ToolChainStep(
                    order=len(steps) + 1,
                    tool_name="suggest_pipeline",
                    description="Get pipeline suggestions",
                    parameters={"task_description": goal},
                    output_key="suggestion",
                ))

            # If still no steps, provide a default exploration workflow
            if not steps:
                steps = [
                    ToolChainStep(
                        order=1,
                        tool_name="list_components",
                        description="Explore available components",
                        output_key="components",
                    ),
                    ToolChainStep(
                        order=2,
                        tool_name="suggest_pipeline",
                        description="Get AI suggestions for the goal",
                        parameters={"task_description": goal},
                        output_key="suggestion",
                    ),
                ]

        # Limit to max_steps
        steps = steps[:max_steps]

        return ToolChain(
            id=chain_id,
            name=f"Chain for: {goal[:50]}",
            description=f"Tool chain to accomplish: {goal}",
            steps=steps,
            estimated_duration=f"{len(steps) * 2}s",
        )

    async def smart_invoke(
        self,
        tool_name: str,
        natural_language_params: Optional[str] = None,
        partial_params: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SmartInvokeResponse:
        """Resolve parameters intelligently for a tool invocation."""
        tool_info = self._tool_catalog.get(tool_name)
        if not tool_info:
            raise ValueError(f"Tool '{tool_name}' not found")

        resolved_params: Dict[str, Any] = dict(partial_params or {})
        explanations: Dict[str, str] = {}
        warnings: List[str] = []
        confidence = 1.0

        # Process natural language parameters
        if natural_language_params:
            nl_params = self._parse_natural_language_params(
                natural_language_params,
                tool_info.get("parameters", {}),
            )
            for key, value in nl_params.items():
                if key not in resolved_params:
                    resolved_params[key] = value
                    explanations[key] = f"Extracted from: '{natural_language_params}'"
                    confidence *= 0.9  # Slightly lower confidence for NL params

        # Fill from context
        if context:
            for param, info in tool_info.get("parameters", {}).items():
                if param not in resolved_params:
                    # Try to find matching context key
                    for ctx_key, ctx_value in context.items():
                        if param in ctx_key.lower() or ctx_key.lower() in param:
                            resolved_params[param] = ctx_value
                            explanations[param] = f"Inferred from context key: {ctx_key}"
                            confidence *= 0.85

        # Check for missing required parameters
        for required in tool_info.get("required_params", []):
            if required not in resolved_params:
                warnings.append(f"Missing required parameter: {required}")
                confidence *= 0.5

        # Apply defaults
        for param, info in tool_info.get("parameters", {}).items():
            if param not in resolved_params and "default" in info:
                resolved_params[param] = info["default"]
                explanations[param] = "Using default value"

        return SmartInvokeResponse(
            success=len(warnings) == 0,
            resolved_params=resolved_params,
            confidence=confidence,
            explanations=explanations,
            warnings=warnings,
        )

    async def get_autocomplete(
        self,
        tool_name: str,
        parameter: str,
        partial_value: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AutocompleteResult:
        """Get autocomplete suggestions for a parameter."""
        tool_info = self._tool_catalog.get(tool_name)
        if not tool_info:
            raise ValueError(f"Tool '{tool_name}' not found")

        suggestions: List[AutocompleteSuggestion] = []

        # Generate suggestions based on parameter type
        param_info = tool_info.get("parameters", {}).get(parameter, {})

        if parameter == "component_type":
            # Suggest common components
            components = ["generator", "filter", "json_transform", "http_request", "loop"]
            for comp in components:
                if partial_value is None or partial_value.lower() in comp.lower():
                    suggestions.append(AutocompleteSuggestion(
                        value=comp,
                        label=comp,
                        description=f"The {comp} component",
                        source="catalog",
                    ))

        elif parameter == "input_source":
            suggestions = [
                AutocompleteSuggestion(
                    value="input",
                    label="input",
                    description="Use pipeline input",
                    source="schema",
                ),
                AutocompleteSuggestion(
                    value="stages.previous.output",
                    label="stages.previous.output",
                    description="Use output from previous stage",
                    source="schema",
                ),
            ]

        # Add AI-suggested values
        if partial_value:
            suggestions.append(AutocompleteSuggestion(
                value=partial_value,
                label=f"Use: {partial_value}",
                description="Your input",
                source="user",
            ))

        return AutocompleteResult(
            parameter=parameter,
            suggestions=suggestions[:10],
        )

    # =========================================================================
    # Conversation Management
    # =========================================================================

    def create_conversation(self) -> ConversationContext:
        """Create a new conversation context."""
        conv_id = str(uuid.uuid4())
        context = ConversationContext(
            id=conv_id,
            started_at=datetime.utcnow().isoformat(),
        )
        self._conversations[conv_id] = context
        return context

    def get_conversation(self, conv_id: str) -> Optional[ConversationContext]:
        """Get a conversation by ID."""
        return self._conversations.get(conv_id)

    def add_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        tool_call: Optional[Dict[str, Any]] = None,
        tool_result: Optional[Dict[str, Any]] = None,
    ) -> ConversationMessage:
        """Add a message to a conversation."""
        context = self._conversations.get(conv_id)
        if not context:
            raise ValueError(f"Conversation {conv_id} not found")

        message = ConversationMessage(
            role=role,
            content=content,
            tool_call=tool_call,
            tool_result=tool_result,
            timestamp=datetime.utcnow().isoformat(),
        )
        context.messages.append(message)

        if tool_call:
            tool_name = tool_call.get("name", "")
            if tool_name and tool_name not in context.tools_used:
                context.tools_used.append(tool_name)

        return message

    # =========================================================================
    # Internal Methods
    # =========================================================================

    async def _recommend_tools(
        self,
        task: str,
        intent: str,
        capabilities: List[str],
    ) -> List[ToolRecommendation]:
        """Recommend tools based on task analysis."""
        recommendations: List[ToolRecommendation] = []
        task_lower = task.lower()

        # Score each tool
        for name, info in self._tool_catalog.items():
            score = 0.0
            reasons: List[str] = []

            # Check category match
            category = info["category"]
            if category == ToolCategory.PIPELINE and "pipeline" in task_lower:
                score += 0.3
                reasons.append("Matches pipeline task")
            if category == ToolCategory.COMPONENT and "component" in task_lower:
                score += 0.3
                reasons.append("Matches component task")

            # Check when_to_use
            for use_case in info.get("when_to_use", []):
                use_case_lower = use_case.lower()
                words_matched = sum(1 for word in task_lower.split() if word in use_case_lower)
                if words_matched > 0:
                    score += 0.1 * min(words_matched, 3)
                    reasons.append(f"Use case match: {use_case[:50]}")

            # Check description
            desc_lower = info["description"].lower()
            for word in task_lower.split():
                if len(word) > 3 and word in desc_lower:
                    score += 0.05
                    reasons.append(f"Description contains '{word}'")

            if score > 0.1:
                recommendations.append(ToolRecommendation(
                    tool_name=name,
                    relevance_score=min(score, 1.0),
                    reason=reasons[0] if reasons else "General match",
                ))

        # Sort by score
        recommendations.sort(key=lambda r: r.relevance_score, reverse=True)
        return recommendations[:5]

    def _build_workflow(
        self,
        intent: str,
        recommendations: List[ToolRecommendation],
    ) -> List[str]:
        """Build a suggested workflow based on intent and recommendations."""
        workflow: List[str] = []

        if intent == "discovery":
            workflow = [
                "1. Use list_pipelines or list_components to explore",
                "2. Use get_component for detailed info on interesting items",
                "3. Review the results to understand available options",
            ]
        elif intent == "creation":
            workflow = [
                "1. Use list_components to see available building blocks",
                "2. Use suggest_pipeline to get AI recommendations",
                "3. Use generate_stage to create each stage",
                "4. Use validate_pipeline_config to check for errors",
                "5. Use create_pipeline to save the final pipeline",
            ]
        elif intent == "execution":
            workflow = [
                "1. Use list_pipelines to find the pipeline to run",
                "2. Prepare input data according to the pipeline's input schema",
                "3. Execute the pipeline with the prepared input",
            ]
        elif intent == "validation":
            workflow = [
                "1. Use validate_pipeline_config with your pipeline JSON",
                "2. Review errors and warnings",
                "3. Fix issues and re-validate",
            ]
        else:
            # Build from recommendations
            for i, rec in enumerate(recommendations[:3], 1):
                workflow.append(f"{i}. Use {rec.tool_name}: {rec.reason}")

        return workflow

    def _generate_tips(self, tool_name: str, tool_info: Dict) -> List[str]:
        """Generate usage tips for a tool."""
        tips: List[str] = []

        if tool_info.get("related_tools"):
            tips.append(f"Consider using with: {', '.join(tool_info['related_tools'][:3])}")

        if "validate" in tool_name.lower():
            tips.append("Always validate before creating/running pipelines")

        if tool_info.get("category") == ToolCategory.PIPELINE:
            tips.append("Pipeline tools work best in sequence: suggest → generate → validate → create")

        return tips

    def _generate_warnings(self, tool_name: str, tool_info: Dict) -> List[str]:
        """Generate warnings for a tool."""
        warnings: List[str] = []

        if tool_info.get("required_params"):
            warnings.append(f"Required parameters: {', '.join(tool_info['required_params'])}")

        if "create" in tool_name.lower():
            warnings.append("This tool modifies state - review parameters carefully")

        return warnings

    def _parse_natural_language_params(
        self,
        text: str,
        param_schema: Dict[str, Dict],
    ) -> Dict[str, Any]:
        """Extract parameters from natural language text."""
        params: Dict[str, Any] = {}

        for param_name, param_info in param_schema.items():
            # Try to find parameter mentions
            patterns = [
                rf"{param_name}\s*[=:]\s*['\"]?([^'\"]+)['\"]?",
                rf"(?:use|set|with)\s+{param_name}\s+(?:to|as)\s+['\"]?([^'\"]+)['\"]?",
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    params[param_name] = match.group(1).strip()
                    break

        return params


# Global instance
_mcp_assistant_service: Optional[MCPAssistantService] = None


def get_mcp_assistant_service() -> MCPAssistantService:
    """Get the global MCP assistant service instance."""
    global _mcp_assistant_service
    if _mcp_assistant_service is None:
        _mcp_assistant_service = MCPAssistantService()
    return _mcp_assistant_service
