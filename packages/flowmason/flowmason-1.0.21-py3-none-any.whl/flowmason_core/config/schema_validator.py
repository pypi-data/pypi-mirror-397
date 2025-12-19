"""
Schema Validator for FlowMason.

Validates that configurations match their expected schemas before execution.
This enables "fail fast" behavior - catch errors before running pipelines.
"""

from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from flowmason_core.config.template_resolver import TemplateResolver
from flowmason_core.config.types import (
    ComponentConfig,
    PipelineConfig,
    ValidationResult,
)


class SchemaValidator:
    """
    Validates configurations against schemas before execution.

    Pre-execution validation catches:
    - Missing required fields
    - Type mismatches
    - Invalid template references
    - Schema violations

    Example:
        validator = SchemaValidator()

        result = validator.validate_component_config(
            component_config,
            ComponentClass.Input,
            available_context
        )

        if not result.is_valid:
            for error in result.errors:
                print(f"{error.field}: {error.message}")
    """

    def __init__(self):
        self.template_resolver = TemplateResolver(strict_mode=False)

    def validate_component_config(
        self,
        component_config: ComponentConfig,
        input_class: Type[BaseModel],
        available_context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate a component configuration against its Input schema.

        Args:
            component_config: The stage configuration to validate
            input_class: The component's Input class
            available_context: Context that will be available at runtime

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult(is_valid=True)
        input_mapping = component_config.input_mapping
        available_context = available_context or {}

        # Get schema information from Input class
        field_types = get_type_hints(input_class)
        required_fields = self._get_required_fields(input_class)

        # Check required fields are present
        for field in required_fields:
            if field not in input_mapping:
                result.add_error(
                    field=field,
                    error_type="missing_required",
                    message=f"Required field '{field}' is not provided in input_mapping",
                    suggestion=f"Add '{field}: \"...\"' to the input_mapping"
                )

        # Validate each mapped field
        for field_name, value in input_mapping.items():
            # Check field exists in schema
            if field_name not in field_types:
                result.add_warning(
                    f"Field '{field_name}' is not defined in {input_class.__name__}. "
                    "It will be ignored."
                )
                continue

            expected_type = field_types[field_name]

            # Validate templates
            self._validate_templates_in_value(
                value,
                field_name,
                available_context,
                result
            )

            # Check type compatibility (where possible without runtime values)
            self._validate_type_compatibility(
                value,
                expected_type,
                field_name,
                result
            )

        return result

    def validate_pipeline_config(
        self,
        pipeline_config: PipelineConfig,
        component_schemas: Dict[str, Type[BaseModel]]
    ) -> ValidationResult:
        """
        Validate an entire pipeline configuration.

        Args:
            pipeline_config: The pipeline to validate
            component_schemas: Mapping of component type -> Input class

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult(is_valid=True)

        # Track stage IDs for dependency validation
        stage_ids = set()
        upstream_outputs: Dict[str, Dict[str, Any]] = {}

        # Validate each stage
        for stage in pipeline_config.stages:
            # Check for duplicate stage IDs
            if stage.id in stage_ids:
                result.add_error(
                    field=f"stages[{stage.id}]",
                    error_type="duplicate_id",
                    message=f"Duplicate stage ID: '{stage.id}'",
                    suggestion="Use unique IDs for each stage"
                )
            stage_ids.add(stage.id)

            # Validate dependencies exist
            for dep_id in stage.depends_on:
                if dep_id not in stage_ids:
                    result.add_error(
                        field=f"stages[{stage.id}].depends_on",
                        error_type="invalid_dependency",
                        message=f"Stage '{stage.id}' depends on unknown stage '{dep_id}'",
                        suggestion="Check that dependencies are defined before their dependents"
                    )

            # Get component schema
            if stage.type not in component_schemas:
                result.add_error(
                    field=f"stages[{stage.id}].type",
                    error_type="unknown_component",
                    message=f"Unknown component type: '{stage.type}'",
                    suggestion="Check that the component is registered"
                )
                continue

            input_class = component_schemas[stage.type]

            # Build available context for this stage
            available_context = {
                "input": self._schema_to_mock_data(pipeline_config.input_schema.properties),
                "upstream": upstream_outputs,
                "env": {},
                "context": {
                    "run_id": "<run_id>",
                    "pipeline_id": pipeline_config.id,
                    "pipeline_version": pipeline_config.version,
                }
            }

            # Validate the stage
            stage_result = self.validate_component_config(
                stage,
                input_class,
                available_context
            )

            # Merge errors with stage context
            for error in stage_result.errors:
                result.add_error(
                    field=f"stages[{stage.id}].{error.field}",
                    error_type=error.error_type,
                    message=error.message,
                    suggestion=error.suggestion
                )

            for warning in stage_result.warnings:
                result.add_warning(f"stages[{stage.id}]: {warning}")

            # Add this stage's output to upstream for subsequent stages
            upstream_outputs[stage.id] = {"<output>": "..."}

        # Validate output_stage_id if specified
        if pipeline_config.output_stage_id:
            if pipeline_config.output_stage_id not in stage_ids:
                result.add_error(
                    field="output_stage_id",
                    error_type="invalid_reference",
                    message=f"output_stage_id '{pipeline_config.output_stage_id}' "
                            "does not match any stage",
                    suggestion="Set output_stage_id to an existing stage ID"
                )

        return result

    def _get_required_fields(self, model_class: Type[BaseModel]) -> List[str]:
        """Get list of required fields from a Pydantic model."""
        required = []
        for field_name, field_info in model_class.model_fields.items():
            if field_info.is_required():
                required.append(field_name)
        return required

    def _validate_templates_in_value(
        self,
        value: Any,
        field_name: str,
        available_context: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """Validate all template references in a value."""
        templates = self.template_resolver.find_templates(value)

        for template_path in templates:
            errors = self.template_resolver.validate_templates(
                f"{{{{{template_path}}}}}",
                available_context
            )
            for error in errors:
                result.add_error(
                    field=field_name,
                    error_type="invalid_template",
                    message=error,
                    suggestion="Check that the template path exists in the available context"
                )

    def _validate_type_compatibility(
        self,
        value: Any,
        expected_type: Type,
        field_name: str,
        result: ValidationResult
    ) -> None:
        """
        Validate that a value is compatible with expected type.

        For literal values, check directly.
        For templates, we can only check at runtime.
        """
        # If value contains templates, skip type checking
        if isinstance(value, str):
            if "{{" in value and "}}" in value:
                return  # Templates are checked at runtime

        # For literal values, check type compatibility
        origin = get_origin(expected_type)

        if origin is Union:
            # For Optional/Union, check against any variant
            args = get_args(expected_type)
            if not any(self._is_type_compatible(value, arg) for arg in args):
                result.add_warning(
                    f"Field '{field_name}' value may not match expected type "
                    f"{expected_type}"
                )
        elif origin is list:
            if not isinstance(value, list):
                # Could be JSON string, will be coerced
                if not isinstance(value, str):
                    result.add_error(
                        field=field_name,
                        error_type="type_mismatch",
                        message=f"Expected list, got {type(value).__name__}",
                        suggestion="Provide a list or JSON array string"
                    )
        elif origin is dict:
            if not isinstance(value, dict):
                # Could be JSON string, will be coerced
                if not isinstance(value, str):
                    result.add_error(
                        field=field_name,
                        error_type="type_mismatch",
                        message=f"Expected dict, got {type(value).__name__}",
                        suggestion="Provide a dict or JSON object string"
                    )
        else:
            if not self._is_type_compatible(value, expected_type):
                # Might still be coercible
                result.add_warning(
                    f"Field '{field_name}' value type ({type(value).__name__}) "
                    f"differs from expected ({expected_type}). "
                    "Type coercion will be attempted."
                )

    def _is_type_compatible(self, value: Any, expected_type: Type) -> bool:
        """Check if a value is compatible with a type."""
        if expected_type is type(None):
            return value is None

        origin = get_origin(expected_type)
        if origin is not None:
            # Generic type
            if origin is Union:
                args = get_args(expected_type)
                return any(self._is_type_compatible(value, arg) for arg in args)
            elif origin is list:
                return isinstance(value, list)
            elif origin is dict:
                return isinstance(value, dict)
            return isinstance(value, origin)

        # Simple type
        try:
            return isinstance(value, expected_type)
        except TypeError:
            # Some types don't support isinstance
            return False

    def _schema_to_mock_data(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock data from a JSON schema properties dict for validation."""
        mock: Dict[str, Any] = {}
        for name, prop in properties.items():
            prop_type = prop.get("type", "string")
            if prop_type == "string":
                mock[name] = "<string>"
            elif prop_type == "integer":
                mock[name] = 0
            elif prop_type == "number":
                mock[name] = 0.0
            elif prop_type == "boolean":
                mock[name] = False
            elif prop_type == "object":
                mock[name] = {}
            elif prop_type == "array":
                mock[name] = []
            else:
                mock[name] = None
        return mock


class OutputValidator:
    """
    Validates component outputs against their declared schemas.

    Ensures components return what they promise.
    """

    def validate_output(
        self,
        output: Any,
        output_class: Type[BaseModel]
    ) -> ValidationResult:
        """
        Validate that output matches the Output schema.

        Args:
            output: The actual output from execution
            output_class: The expected Output class

        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)

        # If output is already the right type, we're good
        if isinstance(output, output_class):
            return result

        # If output is a dict, try to validate against schema
        if isinstance(output, dict):
            try:
                output_class(**output)
            except Exception as e:
                result.add_error(
                    field="_output",
                    error_type="schema_violation",
                    message=f"Output does not match schema: {e}",
                    suggestion="Check that execute() returns the correct Output type"
                )
        else:
            result.add_error(
                field="_output",
                error_type="type_mismatch",
                message=f"Expected {output_class.__name__}, got {type(output).__name__}",
                suggestion="Return an instance of the Output class from execute()"
            )

        return result

    def validate_against_json_schema(
        self,
        output: Any,
        json_schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate output against a JSON schema.

        Args:
            output: The output to validate
            json_schema: JSON Schema definition

        Returns:
            ValidationResult
        """
        result = ValidationResult(is_valid=True)

        # Basic type checking based on JSON schema
        expected_type = json_schema.get("type")

        if expected_type == "object":
            if not isinstance(output, dict):
                result.add_error(
                    field="_output",
                    error_type="type_mismatch",
                    message=f"Expected object, got {type(output).__name__}",
                    suggestion=None
                )
                return result

            # Check required properties
            required = json_schema.get("required", [])
            properties = json_schema.get("properties", {})

            for prop in required:
                if prop not in output:
                    result.add_error(
                        field=prop,
                        error_type="missing_required",
                        message=f"Required property '{prop}' is missing from output",
                        suggestion=None
                    )

            # Validate property types
            for prop_name, prop_schema in properties.items():
                if prop_name in output:
                    prop_result = self.validate_against_json_schema(
                        output[prop_name],
                        prop_schema
                    )
                    for error in prop_result.errors:
                        result.add_error(
                            field=f"{prop_name}.{error.field}".lstrip("."),
                            error_type=error.error_type,
                            message=error.message,
                            suggestion=error.suggestion
                        )

        elif expected_type == "array":
            if not isinstance(output, list):
                result.add_error(
                    field="_output",
                    error_type="type_mismatch",
                    message=f"Expected array, got {type(output).__name__}",
                    suggestion=None
                )

        elif expected_type == "string":
            if not isinstance(output, str):
                result.add_error(
                    field="_output",
                    error_type="type_mismatch",
                    message=f"Expected string, got {type(output).__name__}",
                    suggestion=None
                )

        elif expected_type == "integer":
            if not isinstance(output, int) or isinstance(output, bool):
                result.add_error(
                    field="_output",
                    error_type="type_mismatch",
                    message=f"Expected integer, got {type(output).__name__}",
                    suggestion=None
                )

        elif expected_type == "number":
            if not isinstance(output, (int, float)) or isinstance(output, bool):
                result.add_error(
                    field="_output",
                    error_type="type_mismatch",
                    message=f"Expected number, got {type(output).__name__}",
                    suggestion=None
                )

        elif expected_type == "boolean":
            if not isinstance(output, bool):
                result.add_error(
                    field="_output",
                    error_type="type_mismatch",
                    message=f"Expected boolean, got {type(output).__name__}",
                    suggestion=None
                )

        return result
