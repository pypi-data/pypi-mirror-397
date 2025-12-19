"""
FlowMason Component Decorators

Provides the @node, @operator, and @control_flow decorators for defining components.

IMPORTANT: Unlike the old architecture, these decorators do NOT auto-register
components in a global registry. They only store metadata on the class.
Registration happens when packages are loaded by the ComponentRegistry.

Component Types:
- @node: AI-powered components that use LLM providers
- @operator: Non-AI utility components for data transformation
- @control_flow: Control flow components for conditional, loops, error handling
"""

import asyncio
import inspect
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


def node(
    name: str,
    category: str,
    description: str,
    icon: str = "box",
    color: str = "#6B7280",
    version: str = "1.0.0",
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    # AI Model configuration
    recommended_providers: Optional[Dict[str, Dict[str, Any]]] = None,
    default_provider: Optional[str] = None,
    required_capabilities: Optional[List[str]] = None,
    min_context_window: Optional[int] = None,
    require_vision: bool = False,
    require_function_calling: bool = False,
) -> Callable[[Type], Type]:
    """
    Decorator to define a FlowMason node (AI-powered component).

    This decorator:
    1. Validates the node class structure
    2. Stores metadata on the class as _flowmason_metadata
    3. Wraps the execute method with error handling

    NOTE: Does NOT auto-register in any global registry. Components are
    registered when their packages are loaded by the ComponentRegistry.

    Args:
        name: Unique identifier for the node (snake_case)
        category: Category for grouping (e.g., "reasoning", "control_flow")
        description: Human-readable description
        icon: Lucide icon name for UI
        color: Hex color code for UI
        version: Semantic version string
        author: Author name or organization
        tags: List of searchable tags

        AI Model Configuration:
        recommended_providers: Dict mapping provider_id to recommended settings
        default_provider: Which provider is selected by default
        required_capabilities: Required model capabilities
        min_context_window: Minimum context window size required
        require_vision: Whether the node requires vision capability
        require_function_calling: Whether the node requires function calling

    Returns:
        Decorated class

    Example:
        @node(
            name="code_generator",
            category="reasoning",
            description="Generate code with AI",
            icon="code",
            color="#9333EA",
            recommended_providers={
                "anthropic": {
                    "model": "claude-3-5-sonnet-20241022",
                    "temperature": 0.3,
                },
                "openai": {
                    "model": "gpt-4o",
                    "temperature": 0.3,
                },
            },
            default_provider="anthropic",
        )
        class CodeGeneratorNode:
            class Input(NodeInput):
                prompt: str
                language: str = "python"

            class Output(NodeOutput):
                code: str

            async def execute(self, input: Input, context) -> Output:
                pass
    """

    def decorator(cls: Type) -> Type:
        # Validate class structure
        _validate_node_class(cls, name)

        # Store metadata on the class
        cls._flowmason_metadata = {
            "name": name,
            "category": category,
            "description": description,
            "icon": icon,
            "color": color,
            "version": version,
            "author": author,
            "tags": tags or [],
            "component_kind": "node",
        }

        # Extract Config if present
        if hasattr(cls, "Config"):
            config_cls = cls.Config
            cls._flowmason_metadata["requires_llm"] = getattr(config_cls, "requires_llm", True)
            cls._flowmason_metadata["supports_streaming"] = getattr(
                config_cls, "supports_streaming", False
            )
            cls._flowmason_metadata["timeout_seconds"] = getattr(config_cls, "timeout_seconds", 60)
            cls._flowmason_metadata["max_retries"] = getattr(config_cls, "max_retries", 3)
        else:
            cls._flowmason_metadata["requires_llm"] = True
            cls._flowmason_metadata["supports_streaming"] = False
            cls._flowmason_metadata["timeout_seconds"] = 60
            cls._flowmason_metadata["max_retries"] = 3

        # Store AI model configuration (only if node requires LLM)
        if cls._flowmason_metadata["requires_llm"]:
            cls._flowmason_metadata["ai_config"] = {
                "recommended_providers": recommended_providers,
                "default_provider": default_provider,
                "required_capabilities": required_capabilities,
                "min_context_window": min_context_window,
                "require_vision": require_vision,
                "require_function_calling": require_function_calling,
            }
        else:
            cls._flowmason_metadata["ai_config"] = None

        # Store input/output schemas
        cls._flowmason_metadata["input_schema"] = cls.Input.model_json_schema()
        cls._flowmason_metadata["output_schema"] = cls.Output.model_json_schema()

        # Wrap execute method with error handling
        original_execute = cls.execute
        cls.execute = _wrap_execute(original_execute, name)

        # Mark as FlowMason component
        cls._flowmason_type = "node"

        logger.debug(f"Decorated node: {name} ({cls.__name__})")

        return cls

    return decorator


def operator(
    name: str,
    category: str,
    description: str,
    icon: str = "zap",
    color: str = "#3B82F6",  # Blue for operators
    version: str = "1.0.0",
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Callable[[Type], Type]:
    """
    Decorator to define a FlowMason operator (non-AI utility component).

    Key differences from @node:
    - No LLM provider access in context
    - Deterministic execution (same input = same output)
    - No token/cost tracking
    - Blue color scheme by default
    - Faster execution (no API calls)

    NOTE: Does NOT auto-register in any global registry. Components are
    registered when their packages are loaded by the ComponentRegistry.

    Args:
        name: Unique identifier for the operator (snake_case)
        category: Category for grouping (e.g., "connectors", "transformers")
        description: Human-readable description
        icon: Lucide icon name for UI (default: "zap")
        color: Hex color code for UI (default: blue #3B82F6)
        version: Semantic version string
        author: Author name or organization
        tags: List of searchable tags

    Returns:
        Decorated class

    Example:
        @operator(
            name="http_request",
            category="connectors",
            description="Make HTTP requests to external APIs",
            icon="globe",
            tags=["http", "api", "rest"]
        )
        class HttpRequestOperator:
            class Input(OperatorInput):
                url: str
                method: str = "GET"

            class Output(OperatorOutput):
                status_code: int
                body: Any

            async def execute(self, input: Input, context) -> Output:
                pass
    """

    def decorator(cls: Type) -> Type:
        # Validate class structure
        _validate_operator_class(cls, name)

        # Store metadata on the class
        cls._flowmason_metadata = {
            "name": name,
            "category": category,
            "description": description,
            "icon": icon,
            "color": color,
            "version": version,
            "author": author,
            "tags": tags or [],
            "component_kind": "operator",
            "is_operator": True,  # For compatibility
        }

        # Extract Config if present
        if hasattr(cls, "Config"):
            config_cls = cls.Config
            cls._flowmason_metadata["deterministic"] = getattr(
                config_cls, "deterministic", True
            )
            cls._flowmason_metadata["timeout_seconds"] = getattr(
                config_cls, "timeout_seconds", 30
            )
        else:
            cls._flowmason_metadata["deterministic"] = True
            cls._flowmason_metadata["timeout_seconds"] = 30

        # Operators never require LLM
        cls._flowmason_metadata["requires_llm"] = False

        # Store input/output schemas
        cls._flowmason_metadata["input_schema"] = cls.Input.model_json_schema()
        cls._flowmason_metadata["output_schema"] = cls.Output.model_json_schema()

        # Wrap execute method with error handling
        original_execute = cls.execute
        cls.execute = _wrap_operator_execute(original_execute, name)

        # Mark as FlowMason component
        cls._flowmason_type = "operator"

        logger.debug(f"Decorated operator: {name} ({cls.__name__})")

        return cls

    return decorator


def control_flow(
    name: str,
    description: str,
    control_flow_type: str,  # "conditional", "foreach", "trycatch", "router", "subpipeline"
    category: str = "control_flow",
    icon: str = "git-branch",
    color: str = "#EC4899",  # Pink for control flow
    version: str = "1.0.0",
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Callable[[Type], Type]:
    """
    Decorator to define a FlowMason control flow component.

    Control flow components manage pipeline execution flow:
    - Conditional: If/else branching
    - ForEach: Loop over items
    - TryCatch: Error handling with recovery
    - Router: Switch/case routing
    - SubPipeline: Call another pipeline

    Key differences from @node and @operator:
    - Returns ControlFlowDirective that affects execution
    - Can skip stages, branch execution, or loop
    - Never requires LLM
    - Pink color scheme by default
    - Special handling in executor

    NOTE: Does NOT auto-register in any global registry. Components are
    registered when their packages are loaded by the ComponentRegistry.

    Args:
        name: Unique identifier for the component (snake_case)
        description: Human-readable description
        control_flow_type: Type of control flow ("conditional", "foreach", etc.)
        category: Category for grouping (default: "control_flow")
        icon: Lucide icon name for UI (default: "git-branch")
        color: Hex color code for UI (default: pink #EC4899)
        version: Semantic version string
        author: Author name or organization
        tags: List of searchable tags

    Returns:
        Decorated class

    Example:
        @control_flow(
            name="conditional",
            description="Execute one of two branches based on condition",
            control_flow_type="conditional",
            icon="git-branch",
            tags=["branching", "if-else"]
        )
        class ConditionalComponent:
            class Input(ControlFlowInput):
                condition: bool
                true_branch: List[str]  # Stage IDs
                false_branch: List[str]  # Stage IDs

            class Output(ControlFlowOutput):
                branch_taken: str
                directive: ControlFlowDirective

            async def execute(self, input: Input, context) -> Output:
                pass
    """

    def decorator(cls: Type) -> Type:
        # Validate class structure
        _validate_control_flow_class(cls, name)

        # Store metadata on the class
        cls._flowmason_metadata = {
            "name": name,
            "category": category,
            "description": description,
            "icon": icon,
            "color": color,
            "version": version,
            "author": author,
            "tags": tags or [],
            "component_kind": "control_flow",
            "control_flow_type": control_flow_type,
            "is_control_flow": True,
        }

        # Extract Config if present
        if hasattr(cls, "Config"):
            config_cls = cls.Config
            cls._flowmason_metadata["timeout_seconds"] = getattr(
                config_cls, "timeout_seconds", 30
            )
        else:
            cls._flowmason_metadata["timeout_seconds"] = 30

        # Control flow never requires LLM
        cls._flowmason_metadata["requires_llm"] = False

        # Store input/output schemas
        cls._flowmason_metadata["input_schema"] = cls.Input.model_json_schema()
        cls._flowmason_metadata["output_schema"] = cls.Output.model_json_schema()

        # Wrap execute method with error handling
        original_execute = cls.execute
        cls.execute = _wrap_control_flow_execute(original_execute, name)

        # Mark as FlowMason component
        cls._flowmason_type = "control_flow"

        logger.debug(f"Decorated control_flow: {name} ({cls.__name__})")

        return cls

    return decorator


def _validate_node_class(cls: Type, node_name: str) -> None:
    """
    Validate that a class has the required structure for a node.

    Args:
        cls: The class to validate
        node_name: Name for error messages

    Raises:
        ValueError: If validation fails
    """
    errors = []

    # Check Input class
    if not hasattr(cls, "Input"):
        errors.append("must define an Input class")
    else:
        from flowmason_core.core.types import NodeInput

        if not issubclass(cls.Input, NodeInput):
            errors.append("Input class must inherit from NodeInput")

    # Check Output class
    if not hasattr(cls, "Output"):
        errors.append("must define an Output class")
    else:
        from flowmason_core.core.types import NodeOutput

        if not issubclass(cls.Output, NodeOutput):
            errors.append("Output class must inherit from NodeOutput")

    # Check execute method
    if not hasattr(cls, "execute"):
        errors.append("must define an execute method")
    else:
        execute = cls.execute
        if not callable(execute):
            errors.append("execute must be a callable method")
        elif not asyncio.iscoroutinefunction(execute):
            errors.append("execute must be an async method")
        else:
            # Check method signature
            sig = inspect.signature(execute)
            params = list(sig.parameters.keys())
            if len(params) < 3:  # self, input, context
                errors.append(
                    "execute must accept (self, input, context) parameters"
                )

    if errors:
        error_msg = f"Node '{node_name}' ({cls.__name__}) validation failed:\n"
        error_msg += "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)


def _validate_operator_class(cls: Type, operator_name: str) -> None:
    """
    Validate that a class has the required structure for an operator.

    Args:
        cls: The class to validate
        operator_name: Name for error messages

    Raises:
        ValueError: If validation fails
    """
    errors = []

    # Check Input class
    if not hasattr(cls, "Input"):
        errors.append("must define an Input class")
    else:
        from flowmason_core.core.types import OperatorInput

        if not issubclass(cls.Input, OperatorInput):
            errors.append("Input class must inherit from OperatorInput")

    # Check Output class
    if not hasattr(cls, "Output"):
        errors.append("must define an Output class")
    else:
        from flowmason_core.core.types import OperatorOutput

        if not issubclass(cls.Output, OperatorOutput):
            errors.append("Output class must inherit from OperatorOutput")

    # Check execute method
    if not hasattr(cls, "execute"):
        errors.append("must define an execute method")
    else:
        execute = cls.execute
        if not callable(execute):
            errors.append("execute must be a callable method")
        elif not asyncio.iscoroutinefunction(execute):
            errors.append("execute must be an async method")
        else:
            # Check method signature
            sig = inspect.signature(execute)
            params = list(sig.parameters.keys())
            if len(params) < 3:  # self, input, context
                errors.append(
                    "execute must accept (self, input, context) parameters"
                )

    if errors:
        error_msg = f"Operator '{operator_name}' ({cls.__name__}) validation failed:\n"
        error_msg += "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)


def _validate_control_flow_class(cls: Type, component_name: str) -> None:
    """
    Validate that a class has the required structure for a control flow component.

    Args:
        cls: The class to validate
        component_name: Name for error messages

    Raises:
        ValueError: If validation fails
    """
    errors = []

    # Check Input class
    if not hasattr(cls, "Input"):
        errors.append("must define an Input class")
    else:
        from flowmason_core.core.types import ControlFlowInput

        if not issubclass(cls.Input, ControlFlowInput):
            errors.append("Input class must inherit from ControlFlowInput")

    # Check Output class
    if not hasattr(cls, "Output"):
        errors.append("must define an Output class")
    else:
        from flowmason_core.core.types import ControlFlowOutput

        if not issubclass(cls.Output, ControlFlowOutput):
            errors.append("Output class must inherit from ControlFlowOutput")

    # Check execute method
    if not hasattr(cls, "execute"):
        errors.append("must define an execute method")
    else:
        execute = cls.execute
        if not callable(execute):
            errors.append("execute must be a callable method")
        elif not asyncio.iscoroutinefunction(execute):
            errors.append("execute must be an async method")
        else:
            # Check method signature
            sig = inspect.signature(execute)
            params = list(sig.parameters.keys())
            if len(params) < 3:  # self, input, context
                errors.append(
                    "execute must accept (self, input, context) parameters"
                )

    if errors:
        error_msg = f"Control flow '{component_name}' ({cls.__name__}) validation failed:\n"
        error_msg += "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)


def _wrap_execute(original_execute: Callable, node_name: str) -> Callable:
    """
    Wrap the execute method with error handling and metrics.

    Args:
        original_execute: Original execute method
        node_name: Node name for logging

    Returns:
        Wrapped async method
    """

    @wraps(original_execute)
    async def wrapped_execute(self, input: Any, context: Any) -> Any:
        import time

        start_time = time.time()

        # Set up context tracking if available
        if hasattr(context, "start_execution"):
            context.start_execution(node_name)

        try:
            # Execute the node
            result = await original_execute(self, input, context)

            # Track success
            duration_ms = int((time.time() - start_time) * 1000)
            if hasattr(context, "end_execution"):
                context.end_execution(
                    node_name,
                    success=True,
                    duration_ms=duration_ms
                )

            return result

        except Exception as e:
            # Track failure
            duration_ms = int((time.time() - start_time) * 1000)
            if hasattr(context, "end_execution"):
                context.end_execution(
                    node_name,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(e)
                )

            logger.error(f"Node '{node_name}' execution failed: {e}")
            raise

    return wrapped_execute


def _wrap_operator_execute(original_execute: Callable, operator_name: str) -> Callable:
    """
    Wrap the operator execute method with error handling and timing.

    Unlike nodes, operators don't track tokens/cost since they don't use LLMs.

    Args:
        original_execute: Original execute method
        operator_name: Operator name for logging

    Returns:
        Wrapped async method
    """

    @wraps(original_execute)
    async def wrapped_execute(self, input: Any, context: Any) -> Any:
        import time

        start_time = time.time()

        # Set up context tracking if available
        if hasattr(context, "start_execution"):
            context.start_execution(operator_name)

        try:
            # Execute the operator
            result = await original_execute(self, input, context)

            # Track success
            duration_ms = int((time.time() - start_time) * 1000)
            if hasattr(context, "end_execution"):
                context.end_execution(
                    operator_name,
                    success=True,
                    duration_ms=duration_ms
                )

            return result

        except Exception as e:
            # Track failure
            duration_ms = int((time.time() - start_time) * 1000)
            if hasattr(context, "end_execution"):
                context.end_execution(
                    operator_name,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(e)
                )

            logger.error(f"Operator '{operator_name}' execution failed: {e}")
            raise

    return wrapped_execute


def _wrap_control_flow_execute(original_execute: Callable, component_name: str) -> Callable:
    """
    Wrap the control flow execute method with error handling and timing.

    Control flow components return directives that affect pipeline execution.
    This wrapper ensures proper tracking and error handling.

    Args:
        original_execute: Original execute method
        component_name: Component name for logging

    Returns:
        Wrapped async method
    """

    @wraps(original_execute)
    async def wrapped_execute(self, input: Any, context: Any) -> Any:
        import time

        start_time = time.time()

        # Set up context tracking if available
        if hasattr(context, "start_execution"):
            context.start_execution(component_name)

        try:
            # Execute the control flow component
            result = await original_execute(self, input, context)

            # Track success
            duration_ms = int((time.time() - start_time) * 1000)
            if hasattr(context, "end_execution"):
                context.end_execution(
                    component_name,
                    success=True,
                    duration_ms=duration_ms
                )

            # Log directive info if present
            if hasattr(result, 'directive'):
                logger.debug(
                    f"Control flow '{component_name}' directive: "
                    f"type={result.directive.directive_type}, "
                    f"skip={result.directive.skip_stages}, "
                    f"execute={result.directive.execute_stages}"
                )

            return result

        except Exception as e:
            # Track failure
            duration_ms = int((time.time() - start_time) * 1000)
            if hasattr(context, "end_execution"):
                context.end_execution(
                    component_name,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(e)
                )

            logger.error(f"Control flow '{component_name}' execution failed: {e}")
            raise

    return wrapped_execute


# Utility function to check if a class is a FlowMason component
def is_flowmason_component(cls: Type) -> bool:
    """Check if a class is a decorated FlowMason component."""
    return hasattr(cls, "_flowmason_type") and hasattr(cls, "_flowmason_metadata")


def is_control_flow_component(cls: Type) -> bool:
    """Check if a class is a control flow component."""
    return is_flowmason_component(cls) and cls._flowmason_type == "control_flow"


def get_component_metadata(cls: Type) -> Optional[Dict[str, Any]]:
    """Get metadata from a FlowMason component class."""
    if is_flowmason_component(cls):
        metadata = cls._flowmason_metadata
        return dict(metadata) if isinstance(metadata, dict) else None
    return None


def get_component_type(cls: Type) -> Optional[str]:
    """Get the component type ('node', 'operator', or 'control_flow') from a class."""
    if is_flowmason_component(cls):
        return str(cls._flowmason_type)
    return None


def get_control_flow_type(cls: Type) -> Optional[str]:
    """Get the control flow type (conditional, foreach, etc.) from a class."""
    if is_control_flow_component(cls):
        result = cls._flowmason_metadata.get("control_flow_type")
        return str(result) if result is not None else None
    return None
