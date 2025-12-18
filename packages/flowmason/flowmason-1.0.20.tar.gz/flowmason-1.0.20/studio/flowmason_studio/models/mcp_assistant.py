"""
MCP AI Assistant Models.

Models for AI-powered MCP tool discovery and usage assistance.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolCategory(str, Enum):
    """Categories for MCP tools."""

    PIPELINE = "pipeline"
    COMPONENT = "component"
    DATA = "data"
    INTEGRATION = "integration"
    UTILITY = "utility"


class ToolCapability(BaseModel):
    """A capability that a tool provides."""

    name: str
    description: str
    examples: List[str] = Field(default_factory=list)


class EnhancedTool(BaseModel):
    """Enhanced tool information with AI-generated metadata."""

    name: str
    description: str
    category: ToolCategory
    capabilities: List[ToolCapability] = Field(default_factory=list)

    # Usage hints
    when_to_use: List[str] = Field(
        default_factory=list,
        description="Scenarios when this tool is useful"
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Requirements before using this tool"
    )
    related_tools: List[str] = Field(
        default_factory=list,
        description="Tools that work well with this one"
    )

    # Parameters
    parameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    required_params: List[str] = Field(default_factory=list)
    optional_params: List[str] = Field(default_factory=list)

    # Examples
    usage_examples: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Example invocations with inputs and outputs"
    )


class ToolRecommendation(BaseModel):
    """A recommended tool for a task."""

    tool_name: str
    relevance_score: float = Field(ge=0, le=1)
    reason: str
    suggested_params: Dict[str, Any] = Field(default_factory=dict)
    example_usage: Optional[str] = None


class TaskAnalysis(BaseModel):
    """Analysis of a user's task to recommend tools."""

    task: str
    intent: str
    required_capabilities: List[str] = Field(default_factory=list)
    data_requirements: List[str] = Field(default_factory=list)
    suggested_workflow: List[str] = Field(
        default_factory=list,
        description="Ordered steps to complete the task"
    )
    tool_recommendations: List[ToolRecommendation] = Field(default_factory=list)


class ToolChain(BaseModel):
    """A chain of tools to accomplish a complex task."""

    id: str
    name: str
    description: str
    steps: List["ToolChainStep"]
    estimated_duration: Optional[str] = None


class ToolChainStep(BaseModel):
    """A step in a tool chain."""

    order: int
    tool_name: str
    description: str
    input_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="How to map inputs from previous steps"
    )
    parameters: Dict[str, Any] = Field(default_factory=dict)
    output_key: Optional[str] = Field(
        default=None,
        description="Key to store output for later steps"
    )


class ConversationContext(BaseModel):
    """Context for an AI-assisted MCP conversation."""

    id: str
    started_at: str
    messages: List["ConversationMessage"] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    current_task: Optional[str] = None
    accumulated_data: Dict[str, Any] = Field(default_factory=dict)


class ConversationMessage(BaseModel):
    """A message in an MCP conversation."""

    role: str  # user, assistant, tool
    content: str
    tool_call: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None
    timestamp: str


class ToolExplanation(BaseModel):
    """Detailed explanation of a tool."""

    tool_name: str
    summary: str
    detailed_description: str
    parameter_explanations: Dict[str, str] = Field(default_factory=dict)
    common_use_cases: List[str] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    see_also: List[str] = Field(default_factory=list)


class AutocompleteResult(BaseModel):
    """Result for tool parameter autocomplete."""

    parameter: str
    suggestions: List["AutocompleteSuggestion"]


class AutocompleteSuggestion(BaseModel):
    """A single autocomplete suggestion."""

    value: Any
    label: str
    description: Optional[str] = None
    source: str = "ai"  # ai, history, schema


# API Request/Response Models

class AnalyzeTaskRequest(BaseModel):
    """Request to analyze a task and recommend tools."""

    task: str = Field(..., min_length=5, description="Task description")
    available_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Data currently available"
    )
    constraints: Optional[List[str]] = Field(
        default=None,
        description="Constraints to consider"
    )


class AnalyzeTaskResponse(BaseModel):
    """Response with task analysis and recommendations."""

    analysis: TaskAnalysis
    success: bool
    message: str


class ExplainToolRequest(BaseModel):
    """Request to explain a tool."""

    tool_name: str
    context: Optional[str] = Field(
        default=None,
        description="Context for the explanation"
    )
    detail_level: str = Field(
        default="normal",
        description="brief, normal, or detailed"
    )


class CreateChainRequest(BaseModel):
    """Request to create a tool chain."""

    goal: str = Field(..., description="What the chain should accomplish")
    available_tools: Optional[List[str]] = Field(
        default=None,
        description="Limit to these tools"
    )
    max_steps: int = Field(default=5, ge=1, le=10)


class AutocompleteRequest(BaseModel):
    """Request for parameter autocomplete."""

    tool_name: str
    parameter: str
    partial_value: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class SmartInvokeRequest(BaseModel):
    """Request for AI-assisted tool invocation."""

    tool_name: str
    natural_language_params: Optional[str] = Field(
        default=None,
        description="Parameters described in natural language"
    )
    partial_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Partially filled parameters"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Context data to use for filling parameters"
    )


class SmartInvokeResponse(BaseModel):
    """Response with smart invocation result."""

    success: bool
    resolved_params: Dict[str, Any]
    confidence: float
    explanations: Dict[str, str] = Field(
        default_factory=dict,
        description="Why each parameter was set to its value"
    )
    warnings: List[str] = Field(default_factory=list)


# Update forward references
ToolChain.model_rebuild()
ConversationContext.model_rebuild()
AutocompleteResult.model_rebuild()
