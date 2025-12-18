"""
Input Mapper for FlowMason.

Maps pipeline configuration (JSON) to component Input models (Pydantic).
This is the core of the Config-to-Schema mapping system.
"""

from typing import Any, Dict, Optional, Type, get_type_hints

from pydantic import BaseModel

from flowmason_core.config.template_resolver import TemplateResolver
from flowmason_core.config.type_coercion import CoercionError, TypeCoercer
from flowmason_core.config.types import (
    ComponentConfig,
    ExecutionContext,
    MappingError,
    ValidationResult,
)


class InputMapper:
    """
    Maps ComponentConfig to typed Pydantic Input instances.

    This is the bridge between JSON pipeline configuration and
    strongly-typed component Input classes.

    The mapping process:
    1. Resolve template variables ({{input.field}}, etc.)
    2. Apply explicit field mappings from input_mapping
    3. Coerce values to match Input field types
    4. Validate the resulting Input instance

    Example:
        mapper = InputMapper(context)

        node_config = ComponentConfig(
            id="classify",
            type="support_triage",
            input_mapping={
                "text": "{{input.ticket_text}}",
                "metadata": "{{input.metadata}}"
            }
        )

        # SupportTriageInput is the component's Input class
        input_instance = mapper.map_config_to_input(
            node_config,
            SupportTriageInput,
            upstream_outputs={}
        )
    """

    def __init__(
        self,
        context: Optional[ExecutionContext] = None,
        strict_templates: bool = True
    ):
        """
        Initialize the mapper.

        Args:
            context: Execution context for resolving templates
            strict_templates: If True, fail on unresolvable templates
        """
        self.context = context
        self.template_resolver = TemplateResolver(strict_mode=strict_templates)
        self.type_coercer = TypeCoercer()

    def map_config_to_input(
        self,
        component_config: ComponentConfig,
        input_class: Type[BaseModel],
        upstream_outputs: Optional[Dict[str, Any]] = None
    ) -> BaseModel:
        """
        Map a ComponentConfig to a typed Input instance.

        Args:
            component_config: The pipeline stage configuration
            input_class: The component's Input class (Pydantic model)
            upstream_outputs: Results from previously executed stages

        Returns:
            Instance of input_class with fields populated

        Raises:
            MappingError: If mapping fails
        """
        # Build resolution context
        resolution_context = self._build_resolution_context(upstream_outputs)

        # Get the input mapping from config (for templates like {{input.field}})
        input_mapping = component_config.input_mapping

        # Get static config values if available (for extra fields passed directly)
        # ComponentConfig uses extra="allow" so extra fields may exist
        static_config = getattr(component_config, 'config', None) or {}

        # Get field info from the Input class
        field_types = self._get_field_types(input_class)
        field_defaults = self._get_field_defaults(input_class)

        # Build the input data by starting with static config values,
        # then applying templates from input_mapping
        input_data: Dict[str, Any] = {}

        # First, apply static config values (with template resolution)
        for field_name, value in static_config.items():
            if field_name in field_types:
                try:
                    # Resolve templates in static config values
                    resolved_value = self.template_resolver.resolve(
                        value,
                        resolution_context
                    )
                    coerced_value = self.type_coercer.coerce(resolved_value, field_types[field_name])
                    input_data[field_name] = coerced_value
                except CoercionError as e:
                    raise MappingError(
                        field_name,
                        f"Type coercion failed for static config: {e.message}",
                        suggestion=f"Expected type: {field_types[field_name]}"
                    )

        for field_name, field_type in field_types.items():
            # Check if field is in input_mapping
            if field_name in input_mapping:
                raw_value = input_mapping[field_name]

                # Resolve templates
                try:
                    resolved_value = self.template_resolver.resolve(
                        raw_value,
                        resolution_context
                    )
                except Exception as e:
                    raise MappingError(
                        field_name,
                        f"Failed to resolve template: {e}",
                        suggestion="Check that the template variables exist in the context"
                    )

                # Coerce to target type
                try:
                    coerced_value = self.type_coercer.coerce(resolved_value, field_type)
                except CoercionError as e:
                    raise MappingError(
                        field_name,
                        f"Type coercion failed: {e.message}",
                        suggestion=f"Expected type: {field_type}"
                    )

                input_data[field_name] = coerced_value

            elif field_name in field_defaults:
                # Field has default, not required in mapping
                pass
            else:
                # Field is required but not in mapping
                # Let Pydantic handle the validation
                pass

        # Create and validate the Input instance
        try:
            return input_class(**input_data)
        except Exception as e:
            raise MappingError(
                "_all",
                f"Failed to create Input instance: {e}",
                suggestion="Check that all required fields are provided in input_mapping"
            )

    def _build_resolution_context(
        self,
        upstream_outputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build the context for template resolution."""
        context_data: Dict[str, Any] = {
            "input": {},
            "upstream": upstream_outputs or {},
            "env": {},
            "context": {},
        }

        if self.context:
            context_data["input"] = self.context.pipeline_input
            context_data["env"] = self.context.environment
            context_data["context"] = {
                "run_id": self.context.run_id,
                "pipeline_id": self.context.pipeline_id,
                "pipeline_version": self.context.pipeline_version,
                "stage_id": self.context.stage_id,
                "trace_id": self.context.trace_id,
                # Include runtime variables for control flow (e.g., loop item, index)
                **getattr(self.context, 'variables', {}),
            }

        return context_data

    def _get_field_types(self, input_class: Type[BaseModel]) -> Dict[str, Type]:
        """Get the types of all fields in the Input class."""
        return get_type_hints(input_class)

    def _get_field_defaults(self, input_class: Type[BaseModel]) -> Dict[str, Any]:
        """Get fields that have default values."""
        defaults = {}
        for field_name, field_info in input_class.model_fields.items():
            if field_info.default is not None or field_info.default_factory is not None:
                defaults[field_name] = (
                    field_info.default if field_info.default_factory is None
                    else field_info.default_factory()  # type: ignore[call-arg]
                )
        return defaults

    def validate_mapping(
        self,
        component_config: ComponentConfig,
        input_class: Type[BaseModel],
        available_context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate that a mapping can produce a valid Input instance.

        This is for pre-execution validation - check that the mapping
        will work before actually running the pipeline.

        Args:
            component_config: The stage configuration
            input_class: The component's Input class
            available_context: Context that will be available at runtime

        Returns:
            ValidationResult with any errors/warnings
        """
        result = ValidationResult(is_valid=True)
        input_mapping = component_config.input_mapping

        # Get required fields
        required_fields = set()
        for field_name, field_info in input_class.model_fields.items():
            if field_info.is_required():
                required_fields.add(field_name)

        # Check that all required fields are mapped
        mapped_fields = set(input_mapping.keys())
        missing_required = required_fields - mapped_fields

        for field in missing_required:
            result.add_error(
                field=field,
                error_type="missing_required",
                message=f"Required field '{field}' is not in input_mapping",
                suggestion=f"Add '{field}' to the input_mapping configuration"
            )

        # Validate templates
        for field_name, value in input_mapping.items():
            template_errors = self.template_resolver.validate_templates(
                value,
                available_context
            )
            for error in template_errors:
                result.add_error(
                    field=field_name,
                    error_type="invalid_template",
                    message=error,
                    suggestion="Check that the referenced path exists in the context"
                )

        # Check for unknown fields (fields in mapping but not in Input class)
        field_types = self._get_field_types(input_class)
        unknown_fields = mapped_fields - set(field_types.keys())

        for field in unknown_fields:
            result.add_warning(
                f"Field '{field}' in input_mapping is not defined in {input_class.__name__}"
            )

        return result


class FieldMapper:
    """
    Utility for mapping nested and complex fields.

    Supports:
    - Nested field access: "customer.id" -> {"customer": {"id": ...}}
    - Array indexing: "items[0]" -> {"items": [...]}
    - Combined paths: "orders[0].product.name"
    """

    @staticmethod
    def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
        """
        Set a value at a nested path.

        Args:
            data: The dictionary to modify
            path: Dot-separated path (e.g., "customer.address.city")
            value: Value to set
        """
        parts = FieldMapper._parse_path(path)

        current: Any = data
        for i, part in enumerate(parts[:-1]):
            if isinstance(part, int):
                # Array index
                while len(current) <= part:
                    current.append({})
                if not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
            else:
                # Dictionary key
                if part not in current:
                    # Peek at next part to determine if we need list or dict
                    next_part = parts[i + 1]
                    current[part] = [] if isinstance(next_part, int) else {}
                current = current[part]

        # Set the final value
        final_key = parts[-1]
        if isinstance(final_key, int):
            while len(current) <= final_key:
                current.append(None)
            current[final_key] = value
        else:
            current[final_key] = value

    @staticmethod
    def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        Get a value at a nested path.

        Args:
            data: The dictionary to read from
            path: Dot-separated path (e.g., "customer.address.city")
            default: Default value if path doesn't exist

        Returns:
            Value at path or default
        """
        parts = FieldMapper._parse_path(path)

        current = data
        for part in parts:
            if isinstance(part, int):
                if not isinstance(current, list) or part >= len(current):
                    return default
                current = current[part]
            else:
                if not isinstance(current, dict) or part not in current:
                    return default
                current = current[part]

        return current

    @staticmethod
    def _parse_path(path: str) -> list:
        """
        Parse a path string into parts.

        "customer.orders[0].name" -> ["customer", "orders", 0, "name"]
        """
        import re

        parts = []
        # Split by dots, but handle array brackets
        tokens = re.split(r'\.(?![^\[]*\])', path)

        for token in tokens:
            # Check for array index
            match = re.match(r'(\w+)\[(\d+)\]', token)
            if match:
                parts.append(match.group(1))
                parts.append(int(match.group(2)))
            else:
                # Check for just index
                index_match = re.match(r'\[(\d+)\]', token)
                if index_match:
                    parts.append(int(index_match.group(1)))
                else:
                    parts.append(token)

        return parts
