"""
FlowMason Type System

Provides base classes for node, operator, and control flow input/output schemas
with Pydantic validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic import Field as PydanticField


def Field(
    default: Any = ...,
    *,
    default_factory: Optional[Any] = None,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    examples: Optional[List[Any]] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    **extra: Any,
) -> Any:
    """
    Enhanced Field definition for component schemas.

    Wraps Pydantic's Field with additional metadata support.

    Args:
        default: Default value for the field
        default_factory: Factory function for default value
        alias: Alternative name for the field
        title: Human-readable title
        description: Description for documentation
        examples: Example values for the field
        gt/ge/lt/le: Numeric constraints
        min_length/max_length: String/list length constraints
        pattern: Regex pattern for strings

    Example:
        class Input(NodeInput):
            topic: str = Field(
                description="The topic to analyze",
                examples=["AI safety", "Climate change"]
            )
            max_tokens: int = Field(
                default=1000,
                ge=1,
                le=100000,
                description="Maximum tokens in response"
            )
    """
    return PydanticField(  # type: ignore[misc, call-overload]
        default=default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        examples=examples,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        **extra,
    )


class NodeInput(BaseModel):
    """
    Base class for node input schemas.

    All node Input classes should inherit from this.
    Provides Pydantic validation and serialization.

    Example:
        class Input(NodeInput):
            prompt: str = Field(description="User prompt")
            temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    """

    model_config = ConfigDict(
        extra="forbid",  # Disallow extra fields
        validate_assignment=True,  # Validate on assignment
        str_strip_whitespace=True,  # Strip whitespace from strings
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert input to dictionary."""
        return self.model_dump()

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for the input."""
        return cls.model_json_schema()

    @classmethod
    def get_field_descriptions(cls) -> Dict[str, str]:
        """Get field descriptions for documentation."""
        schema = cls.model_json_schema()
        properties = schema.get("properties", {})
        return {
            name: prop.get("description", "")
            for name, prop in properties.items()
        }


class NodeOutput(BaseModel):
    """
    Base class for node output schemas.

    All node Output classes should inherit from this.
    Provides Pydantic validation and serialization.

    Example:
        class Output(NodeOutput):
            result: str
            confidence: float = Field(ge=0.0, le=1.0)
            metadata: Dict[str, Any] = Field(default_factory=dict)
    """

    model_config = ConfigDict(
        extra="allow",  # Allow extra fields in output
        validate_assignment=True,
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert output to dictionary."""
        return self.model_dump()

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for the output."""
        return cls.model_json_schema()


class OperatorInput(BaseModel):
    """
    Base class for operator input schemas.

    Operators are non-AI utility components for data transformation,
    integration, and control flow. Unlike nodes, they don't require
    LLM providers and produce deterministic output.

    Example:
        class Input(OperatorInput):
            url: str = Field(description="API endpoint URL")
            method: str = Field(default="GET")
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert input to dictionary."""
        return self.model_dump()

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for the input."""
        return cls.model_json_schema()


class OperatorOutput(BaseModel):
    """
    Base class for operator output schemas.

    Operators produce deterministic outputs - same input always
    yields the same output (unlike AI nodes).

    Example:
        class Output(OperatorOutput):
            status_code: int
            body: Any
            success: bool
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert output to dictionary."""
        return self.model_dump()

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for the output."""
        return cls.model_json_schema()


# =============================================================================
# Control Flow Types
# =============================================================================

class ControlFlowType(str, Enum):
    """Types of control flow directives."""
    CONDITIONAL = "conditional"     # If/else branching
    FOREACH = "foreach"             # Loop over items
    TRYCATCH = "trycatch"           # Error handling
    ROUTER = "router"               # Switch/case routing
    SUBPIPELINE = "subpipeline"     # Call another pipeline
    PARALLEL = "parallel"           # Parallel execution
    RETURN = "return"               # Early exit


class ControlFlowInput(BaseModel):
    """
    Base class for control flow component input schemas.

    Control flow components manage pipeline execution flow, including
    conditionals, loops, error handling, and composition.

    Example:
        class Input(ControlFlowInput):
            condition: bool = Field(description="Branch condition")
            true_branch: str = Field(description="Stage ID for true path")
            false_branch: str = Field(description="Stage ID for false path")
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert input to dictionary."""
        return self.model_dump()

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for the input."""
        return cls.model_json_schema()


class ControlFlowOutput(BaseModel):
    """
    Base class for control flow component output schemas.

    Control flow outputs include both data and execution directives
    that tell the executor which stages to execute or skip.

    Example:
        class Output(ControlFlowOutput):
            branch_taken: str
            data: Any = None
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert output to dictionary."""
        return self.model_dump()

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for the output."""
        return cls.model_json_schema()


class ControlFlowDirective(BaseModel):
    """
    Execution directive returned by control flow components.

    Control flow components return directives that tell the executor
    how to modify the execution flow.

    Attributes:
        directive_type: Type of control flow operation
        skip_stages: List of stage IDs to skip
        execute_stages: List of stage IDs that were/should be executed
        loop_items: Items to iterate over (for foreach)
        loop_results: Results from loop iterations
        nested_results: Results from nested/sub-executions
        error: Error information (for trycatch)
        continue_execution: Whether to continue after directive
        branch_taken: Which branch was taken (for conditional/router)
        metadata: Additional metadata about the directive

    Example (Conditional):
        ControlFlowDirective(
            directive_type=ControlFlowType.CONDITIONAL,
            branch_taken="true_branch",
            skip_stages=["false_path_stage_1", "false_path_stage_2"],
            execute_stages=["true_path_stage_1"],
        )

    Example (ForEach):
        ControlFlowDirective(
            directive_type=ControlFlowType.FOREACH,
            loop_items=[{"id": 1}, {"id": 2}],
            loop_results=[result1, result2],
            execute_stages=["loop_body_stage"],
        )
    """

    directive_type: ControlFlowType = Field(description="Type of control flow")

    # Stage control
    skip_stages: List[str] = Field(
        default_factory=list,
        description="Stage IDs to skip"
    )
    execute_stages: List[str] = Field(
        default_factory=list,
        description="Stage IDs that were executed"
    )

    # Loop support
    loop_items: Optional[List[Any]] = Field(
        default=None,
        description="Items to iterate over"
    )
    loop_results: Optional[List[Any]] = Field(
        default=None,
        description="Results from each loop iteration"
    )
    current_item: Optional[Any] = Field(
        default=None,
        description="Current item in loop iteration"
    )
    current_index: Optional[int] = Field(
        default=None,
        description="Current index in loop"
    )

    # Nested execution
    nested_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results from nested/sub-pipeline executions"
    )

    # Error handling
    error: Optional[str] = Field(
        default=None,
        description="Error message if error occurred"
    )
    error_type: Optional[str] = Field(
        default=None,
        description="Type of error that occurred"
    )
    recovered: bool = Field(
        default=False,
        description="Whether error was recovered"
    )

    # Execution control
    continue_execution: bool = Field(
        default=True,
        description="Whether to continue pipeline execution"
    )
    branch_taken: Optional[str] = Field(
        default=None,
        description="Which branch was taken (conditional/router)"
    )

    # Output data (if any)
    output_data: Optional[Any] = Field(
        default=None,
        description="Output data from control flow"
    )

    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    model_config = ConfigDict(extra="allow")

    def to_dict(self) -> Dict[str, Any]:
        """Convert directive to dictionary."""
        return self.model_dump()


class ControlFlowResult(BaseModel):
    """
    Combined result from control flow component execution.

    Includes both the regular output and the directive.
    """

    output: Any = Field(description="Regular output data")
    directive: ControlFlowDirective = Field(description="Execution directive")

    model_config = ConfigDict(extra="allow")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()


class ComponentMetadata(BaseModel):
    """
    Standardized metadata for any component (node, operator, or control_flow).

    This is the common format used by the ComponentRegistry.
    """

    # Identification
    name: str
    version: str
    component_kind: str  # "node", "operator", or "control_flow"
    category: str
    description: str

    # Control flow specific
    control_flow_type: Optional[ControlFlowType] = None  # For control_flow components

    # Display
    icon: str = "box"
    color: str = "#6B7280"

    # Author info
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Schemas (JSON Schema format)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)

    # Runtime configuration
    requires_llm: bool = False
    timeout_seconds: int = 60

    # AI model configuration (only for nodes that require LLM)
    recommended_providers: Optional[Dict[str, Dict[str, Any]]] = None
    default_provider: Optional[str] = None
    required_capabilities: Optional[List[str]] = None

    # Package info (set when loaded from package)
    package_name: Optional[str] = None
    package_version: Optional[str] = None
    package_path: Optional[str] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")

    @classmethod
    def from_node_class(cls, node_class: type) -> "ComponentMetadata":
        """Extract metadata from a decorated node class."""
        if not hasattr(node_class, "_flowmason_metadata"):
            raise ValueError(f"Class {node_class.__name__} is not a FlowMason node")

        meta = node_class._flowmason_metadata
        return cls(
            name=meta["name"],
            version=meta.get("version", "1.0.0"),
            component_kind="node",
            category=meta["category"],
            description=meta["description"],
            icon=meta.get("icon", "box"),
            color=meta.get("color", "#6B7280"),
            author=meta.get("author"),
            tags=meta.get("tags", []),
            input_schema=meta.get("input_schema", {}),
            output_schema=meta.get("output_schema", {}),
            requires_llm=meta.get("requires_llm", True),
            timeout_seconds=meta.get("timeout_seconds", 60),
            recommended_providers=meta.get("ai_config", {}).get("recommended_providers") if meta.get("ai_config") else None,
            default_provider=meta.get("ai_config", {}).get("default_provider") if meta.get("ai_config") else None,
            required_capabilities=meta.get("ai_config", {}).get("required_capabilities") if meta.get("ai_config") else None,
        )

    @classmethod
    def from_operator_class(cls, operator_class: type) -> "ComponentMetadata":
        """Extract metadata from a decorated operator class."""
        if not hasattr(operator_class, "_flowmason_metadata"):
            raise ValueError(f"Class {operator_class.__name__} is not a FlowMason operator")

        meta = operator_class._flowmason_metadata
        return cls(
            name=meta["name"],
            version=meta.get("version", "1.0.0"),
            component_kind="operator",
            category=meta["category"],
            description=meta["description"],
            icon=meta.get("icon", "zap"),
            color=meta.get("color", "#3B82F6"),
            author=meta.get("author"),
            tags=meta.get("tags", []),
            input_schema=meta.get("input_schema", {}),
            output_schema=meta.get("output_schema", {}),
            requires_llm=False,
            timeout_seconds=meta.get("timeout_seconds", 30),
        )

    @classmethod
    def from_control_flow_class(cls, control_flow_class: type) -> "ComponentMetadata":
        """Extract metadata from a decorated control flow class."""
        if not hasattr(control_flow_class, "_flowmason_metadata"):
            raise ValueError(f"Class {control_flow_class.__name__} is not a FlowMason control flow component")

        meta = control_flow_class._flowmason_metadata
        return cls(
            name=meta["name"],
            version=meta.get("version", "1.0.0"),
            component_kind="control_flow",
            category=meta.get("category", "control_flow"),
            description=meta["description"],
            icon=meta.get("icon", "git-branch"),
            color=meta.get("color", "#EC4899"),  # Pink for control flow
            author=meta.get("author"),
            tags=meta.get("tags", []),
            input_schema=meta.get("input_schema", {}),
            output_schema=meta.get("output_schema", {}),
            requires_llm=False,
            timeout_seconds=meta.get("timeout_seconds", 30),
            control_flow_type=meta.get("control_flow_type"),
        )
