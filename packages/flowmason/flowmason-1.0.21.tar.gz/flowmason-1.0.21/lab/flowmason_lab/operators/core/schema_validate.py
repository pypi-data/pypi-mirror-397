"""
Schema Validate Operator - Core FlowMason Component.

Validates data against JSON schemas.
Essential for ensuring data integrity in pipelines.
"""

from typing import Any, Dict, List

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput


@operator(
    name="schema_validate",
    category="core",
    description="Validate data against JSON Schema specifications",
    icon="shield-check",
    color="#14B8A6",
    version="1.0.0",
    author="FlowMason",
    tags=["schema", "validation", "json-schema", "data-quality", "core"],
)
class SchemaValidateOperator:
    """
    Validate data against JSON schemas.

    This operator enables:
    - Input validation before processing
    - Output validation after processing
    - Data contract enforcement
    - Schema-based filtering
    - Detailed error reporting
    """

    class Input(OperatorInput):
        data: Any = Field(
            description="The data to validate",
        )
        json_schema: Dict[str, Any] = Field(
            description="JSON Schema to validate against",
            examples=[{
                "type": "object",
                "required": ["name", "email"],
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                },
            }],
        )
        strict: bool = Field(
            default=True,
            description="If True, fail on any validation error",
        )
        coerce_types: bool = Field(
            default=False,
            description="Attempt to coerce data types to match schema",
        )
        collect_all_errors: bool = Field(
            default=True,
            description="Collect all errors instead of stopping at first",
        )

    class Output(OperatorOutput):
        valid: bool = Field(description="Whether the data is valid")
        data: Any = Field(description="Original or coerced data")
        errors: List[Dict[str, Any]] = Field(
            default_factory=list,
            description="List of validation errors"
        )
        error_count: int = Field(
            default=0,
            description="Number of validation errors"
        )

    class Config:
        deterministic: bool = True
        timeout_seconds: int = 10

    async def execute(self, input: Input, context) -> Output:
        """Execute schema validation."""
        data = input.data

        # Type coercion if enabled
        if input.coerce_types:
            data = self._coerce_types(data, input.json_schema)

        # Validate using jsonschema
        try:
            import jsonschema
            from jsonschema import Draft7Validator
        except ImportError:
            # Fallback to basic validation
            return self._basic_validate(data, input.json_schema)

        validator = Draft7Validator(input.json_schema)
        errors = []

        if input.collect_all_errors:
            for error in validator.iter_errors(data):
                errors.append({
                    "path": list(error.absolute_path),
                    "message": error.message,
                    "validator": error.validator,
                    "validator_value": error.validator_value,
                })
        else:
            try:
                validator.validate(data)
            except jsonschema.ValidationError as e:
                errors.append({
                    "path": list(e.absolute_path),
                    "message": e.message,
                    "validator": e.validator,
                    "validator_value": e.validator_value,
                })

        is_valid = len(errors) == 0

        return self.Output(
            valid=is_valid,
            data=data,
            errors=errors,
            error_count=len(errors),
        )

    def _basic_validate(self, data: Any, schema: Dict[str, Any]) -> "SchemaValidateOperator.Output":
        """Basic validation without jsonschema library."""
        errors = []

        # Check type
        schema_type = schema.get("type")
        if schema_type:
            type_map: Dict[str, type | tuple[type, ...]] = {
                "object": dict,
                "array": list,
                "string": str,
                "number": (int, float),
                "integer": int,
                "boolean": bool,
                "null": type(None),
            }
            expected_type = type_map.get(schema_type)
            if expected_type and not isinstance(data, expected_type):  # type: ignore[arg-type]
                errors.append({
                    "path": [],
                    "message": f"Expected type {schema_type}, got {type(data).__name__}",
                    "validator": "type",
                    "validator_value": schema_type,
                })

        # Check required fields for objects
        if isinstance(data, dict):
            required = schema.get("required", [])
            for field in required:
                if field not in data:
                    errors.append({
                        "path": [field],
                        "message": f"'{field}' is a required property",
                        "validator": "required",
                        "validator_value": required,
                    })

        is_valid = len(errors) == 0

        return self.Output(
            valid=is_valid,
            data=data,
            errors=errors,
            error_count=len(errors),
        )

    def _coerce_types(self, data: Any, schema: Dict[str, Any]) -> Any:
        """Attempt to coerce data types to match schema."""
        schema_type = schema.get("type")

        if schema_type == "string" and not isinstance(data, str):
            return str(data)
        elif schema_type == "integer":
            try:
                return int(data)
            except (ValueError, TypeError):
                return data
        elif schema_type == "number":
            try:
                return float(data)
            except (ValueError, TypeError):
                return data
        elif schema_type == "boolean":
            if isinstance(data, str):
                return data.lower() in ("true", "1", "yes")
            return bool(data)
        elif schema_type == "object" and isinstance(data, dict):
            properties = schema.get("properties", {})
            coerced = {}
            for key, value in data.items():
                if key in properties:
                    coerced[key] = self._coerce_types(value, properties[key])
                else:
                    coerced[key] = value
            return coerced
        elif schema_type == "array" and isinstance(data, list):
            items_schema = schema.get("items", {})
            return [self._coerce_types(item, items_schema) for item in data]

        return data
