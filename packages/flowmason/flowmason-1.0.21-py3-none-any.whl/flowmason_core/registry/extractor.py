"""
Metadata Extractor

Extracts metadata from FlowMason component classes.
"""

import logging
from typing import Any, Dict, Optional, Type

from flowmason_core.registry.types import ComponentInfo

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """
    Extracts metadata from decorated FlowMason component classes.

    Handles:
    - Reading _flowmason_metadata from classes
    - Extracting JSON schemas from Input/Output classes
    - Building ComponentInfo objects
    """

    def extract_from_class(self, cls: Type) -> ComponentInfo:
        """
        Extract all metadata from a decorated component class.

        Args:
            cls: The component class (decorated with @node or @operator)

        Returns:
            ComponentInfo with all extracted metadata

        Raises:
            ValueError: If class is not a valid FlowMason component
        """
        if not hasattr(cls, "_flowmason_metadata"):
            raise ValueError(f"Class {cls.__name__} is not a FlowMason component")

        meta = cls._flowmason_metadata
        component_kind = meta.get("component_kind", "node")

        # Extract AI config if present (only for nodes)
        ai_config = meta.get("ai_config") or {}

        # Determine icon based on component kind
        if component_kind == "node":
            default_icon = "box"
            default_color = "#6B7280"
        elif component_kind == "control_flow":
            default_icon = "git-branch"
            default_color = "#8B5CF6"  # Purple
        else:  # operator
            default_icon = "zap"
            default_color = "#3B82F6"

        return ComponentInfo(
            component_type=meta["name"],
            component_kind=component_kind,
            category=meta.get("category", "general"),
            control_flow_type=meta.get("control_flow_type"),  # For control_flow components
            description=meta.get("description", ""),
            version=meta.get("version", "1.0.0"),
            icon=meta.get("icon", default_icon),
            color=meta.get("color", default_color),
            author=meta.get("author"),
            tags=meta.get("tags", []),
            input_schema=meta.get("input_schema", {}),
            output_schema=meta.get("output_schema", {}),
            requires_llm=meta.get("requires_llm", component_kind == "node"),
            timeout_seconds=meta.get("timeout_seconds", 60 if component_kind == "node" else 30),
            # Full AI config extraction
            recommended_providers=ai_config.get("recommended_providers"),
            default_provider=ai_config.get("default_provider"),
            required_capabilities=ai_config.get("required_capabilities"),
            min_context_window=ai_config.get("min_context_window"),
            require_vision=ai_config.get("require_vision", False),
            require_function_calling=ai_config.get("require_function_calling", False),
            supports_streaming=meta.get("supports_streaming", False),
            max_retries=meta.get("max_retries", 3),
            is_loaded=True,
            is_available=True,
        )

    def extract_input_schema(self, cls: Type) -> Dict[str, Any]:
        """
        Extract the JSON schema from a component's Input class.

        Args:
            cls: The component class

        Returns:
            JSON schema dictionary
        """
        if not hasattr(cls, "Input"):
            return {}

        try:
            schema = cls.Input.model_json_schema()
            return dict(schema) if schema else {}
        except Exception as e:
            logger.warning(f"Failed to extract input schema from {cls.__name__}: {e}")
            return {}

    def extract_output_schema(self, cls: Type) -> Dict[str, Any]:
        """
        Extract the JSON schema from a component's Output class.

        Args:
            cls: The component class

        Returns:
            JSON schema dictionary
        """
        if not hasattr(cls, "Output"):
            return {}

        try:
            schema = cls.Output.model_json_schema()
            return dict(schema) if schema else {}
        except Exception as e:
            logger.warning(f"Failed to extract output schema from {cls.__name__}: {e}")
            return {}

    def extract_decorator_metadata(self, cls: Type) -> Dict[str, Any]:
        """
        Extract raw metadata from the @node or @operator decorator.

        Args:
            cls: The component class

        Returns:
            Metadata dictionary, or empty dict if not a FlowMason component
        """
        if hasattr(cls, "_flowmason_metadata"):
            return dict(cls._flowmason_metadata)
        return {}

    def get_component_type(self, cls: Type) -> Optional[str]:
        """
        Get the component type ('node' or 'operator') from a class.

        Args:
            cls: The component class

        Returns:
            'node', 'operator', or None if not a FlowMason component
        """
        if hasattr(cls, "_flowmason_type"):
            return str(cls._flowmason_type)
        return None

    def validate_component(self, cls: Type) -> tuple[bool, list[str]]:
        """
        Validate that a class is a properly defined FlowMason component.

        Args:
            cls: The class to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for FlowMason metadata
        if not hasattr(cls, "_flowmason_metadata"):
            errors.append("Missing _flowmason_metadata (not decorated with @node or @operator)")
            return False, errors

        if not hasattr(cls, "_flowmason_type"):
            errors.append("Missing _flowmason_type")

        meta = cls._flowmason_metadata

        # Check required metadata fields
        required_fields = ["name", "category", "description"]
        for field in required_fields:
            if field not in meta or not meta[field]:
                errors.append(f"Missing required metadata field: {field}")

        # Check Input class
        if not hasattr(cls, "Input"):
            errors.append("Missing Input class")
        else:
            # Verify it has model_json_schema (Pydantic model)
            if not hasattr(cls.Input, "model_json_schema"):
                errors.append("Input class must be a Pydantic model")

        # Check Output class
        if not hasattr(cls, "Output"):
            errors.append("Missing Output class")
        else:
            if not hasattr(cls.Output, "model_json_schema"):
                errors.append("Output class must be a Pydantic model")

        # Check execute method
        if not hasattr(cls, "execute"):
            errors.append("Missing execute method")
        else:
            import asyncio
            if not asyncio.iscoroutinefunction(cls.execute):
                errors.append("execute must be an async method")

        return len(errors) == 0, errors

    def get_field_info(self, cls: Type, field_type: str = "input") -> Dict[str, Dict[str, Any]]:
        """
        Get detailed field information from Input or Output class.

        Args:
            cls: The component class
            field_type: "input" or "output"

        Returns:
            Dict mapping field names to their info (type, description, default, etc.)
        """
        target_class = cls.Input if field_type == "input" else cls.Output

        if not hasattr(cls, target_class.__name__):
            return {}

        try:
            schema = target_class.model_json_schema()
            properties = schema.get("properties", {})
            required = set(schema.get("required", []))

            field_info = {}
            for name, prop in properties.items():
                field_info[name] = {
                    "type": prop.get("type", "any"),
                    "description": prop.get("description", ""),
                    "required": name in required,
                    "default": prop.get("default"),
                    "examples": prop.get("examples", []),
                }

                # Handle constraints
                for constraint in ["minimum", "maximum", "minLength", "maxLength", "pattern"]:
                    if constraint in prop:
                        field_info[name][constraint] = prop[constraint]

            return field_info

        except Exception as e:
            logger.warning(f"Failed to get field info from {cls.__name__}.{field_type}: {e}")
            return {}
