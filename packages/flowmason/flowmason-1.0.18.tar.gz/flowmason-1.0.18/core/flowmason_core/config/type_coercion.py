"""
Type Coercion System for FlowMason.

Provides safe type conversions when mapping configuration values
to typed Pydantic fields.
"""

import json
from datetime import date, datetime
from enum import Enum
from typing import Any, Type, Union, get_args, get_origin


class CoercionError(Exception):
    """Error during type coercion."""

    def __init__(self, value: Any, target_type: Any, message: str):
        self.value = value
        self.target_type = target_type
        self.message = message
        super().__init__(
            f"Cannot coerce {type(value).__name__} to {target_type}: {message}"
        )


class TypeCoercer:
    """
    Safe type coercion for configuration values.

    Handles common conversions:
    - String to int/float/bool
    - JSON string to dict/list
    - ISO datetime strings
    - None handling

    Always fails safely - never silently produces wrong values.

    Example:
        coercer = TypeCoercer()
        coercer.coerce("123", int)  # Returns 123
        coercer.coerce("true", bool)  # Returns True
        coercer.coerce('{"key": "value"}', dict)  # Returns {"key": "value"}
    """

    # Boolean true/false string mappings
    TRUE_VALUES = {"true", "yes", "1", "on", "enabled"}
    FALSE_VALUES = {"false", "no", "0", "off", "disabled"}

    def coerce(self, value: Any, target_type: Type) -> Any:
        """
        Coerce a value to the target type.

        Args:
            value: The value to coerce
            target_type: The type to coerce to

        Returns:
            The coerced value

        Raises:
            CoercionError: If coercion is not possible
        """
        # Handle None
        if value is None:
            return self._handle_none(target_type)

        # Get the origin type for generics (e.g., list[str] -> list)
        origin = get_origin(target_type)

        # Handle Union types (including Optional)
        if origin is Union:
            return self._coerce_union(value, target_type)

        # Handle generic types (list[str], dict[str, int], etc.)
        # Must check this BEFORE isinstance to avoid TypeError with subscripted generics
        if origin is not None:
            return self._coerce_generic(value, target_type)

        # Handle Any type - accept anything
        if target_type is Any:
            return value

        # Already the correct type (only for non-generic types)
        try:
            if isinstance(value, target_type):
                return value
        except TypeError:
            # Some types like typing.Any cannot be used with isinstance
            pass

        # String to target type conversions
        if isinstance(value, str):
            return self._coerce_from_string(value, target_type)

        # Numeric conversions
        if isinstance(value, (int, float)) and target_type in (int, float):
            return self._coerce_numeric(value, target_type)

        # Dict/list already - check if target is compatible
        if isinstance(value, dict) and target_type is dict:
            return value
        if isinstance(value, list) and target_type is list:
            return value

        # Cannot coerce
        raise CoercionError(
            value,
            target_type,
            f"No coercion available from {type(value).__name__}"
        )

    def _handle_none(self, target_type: Type) -> None:
        """Handle None values - check if type is Optional."""
        origin = get_origin(target_type)
        if origin is Union:
            args = get_args(target_type)
            if type(None) in args:
                return None

        raise CoercionError(None, target_type, "Value is None but type is not Optional")

    def _coerce_union(self, value: Any, target_type: Type) -> Any:
        """Coerce to a Union type by trying each variant."""
        args = get_args(target_type)

        # Skip None type in Union args
        non_none_args = [a for a in args if a is not type(None)]

        # Try each type in order
        errors = []
        for arg_type in non_none_args:
            try:
                return self.coerce(value, arg_type)
            except CoercionError as e:
                errors.append(str(e))

        raise CoercionError(
            value,
            target_type,
            f"Could not coerce to any variant of Union: {errors}"
        )

    def _coerce_generic(self, value: Any, target_type: Type) -> Any:
        """Coerce to a generic type like list[str] or dict[str, int]."""
        from typing import Literal
        origin = get_origin(target_type)
        args = get_args(target_type)

        if origin is list:
            return self._coerce_list(value, args[0] if args else Any)

        if origin is dict:
            key_type = args[0] if args else Any
            value_type = args[1] if len(args) > 1 else Any
            return self._coerce_dict(value, key_type, value_type)

        # Handle Literal types - value must be one of the allowed values
        if origin is Literal:
            return self._coerce_literal(value, args)

        # Other generics - try direct conversion
        if origin is not None:
            return self.coerce(value, origin)
        return value

    def _coerce_literal(self, value: Any, allowed_values: tuple) -> Any:
        """Coerce to a Literal type by checking against allowed values."""
        # Direct match
        if value in allowed_values:
            return value

        # Try string comparison for string literals
        if isinstance(value, str):
            for allowed in allowed_values:
                if isinstance(allowed, str) and value == allowed:
                    return allowed
                # Also try case-insensitive match
                if isinstance(allowed, str) and value.lower() == allowed.lower():
                    return allowed

        # Try numeric coercion for int/float literals
        if isinstance(value, (int, float, str)):
            for allowed in allowed_values:
                if isinstance(allowed, (int, float)):
                    try:
                        coerced = type(allowed)(value)
                        if coerced == allowed:
                            return allowed
                    except (ValueError, TypeError):
                        pass

        raise CoercionError(
            value,
            f"Literal{list(allowed_values)}",
            f"Value '{value}' is not one of the allowed values: {allowed_values}"
        )

    def _coerce_list(self, value: Any, item_type: Type) -> list:
        """Coerce to a list with typed items."""
        # JSON string to list
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if not isinstance(parsed, list):
                    raise CoercionError(value, list, "JSON string is not a list")
                value = parsed
            except json.JSONDecodeError as e:
                raise CoercionError(value, list, f"Invalid JSON: {e}")

        if not isinstance(value, list):
            raise CoercionError(value, list, "Value is not a list")

        # Coerce each item
        if item_type is Any:
            return value

        return [self.coerce(item, item_type) for item in value]

    def _coerce_dict(self, value: Any, key_type: Type, value_type: Type) -> dict:
        """Coerce to a dict with typed keys and values."""
        # JSON string to dict
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if not isinstance(parsed, dict):
                    raise CoercionError(value, dict, "JSON string is not a dict")
                value = parsed
            except json.JSONDecodeError as e:
                raise CoercionError(value, dict, f"Invalid JSON: {e}")

        if not isinstance(value, dict):
            raise CoercionError(value, dict, "Value is not a dict")

        # Coerce keys and values
        if key_type is Any and value_type is Any:
            return value

        return {
            self.coerce(k, key_type): self.coerce(v, value_type)
            for k, v in value.items()
        }

    def _coerce_from_string(self, value: str, target_type: Type) -> Any:
        """Coerce a string to various types."""
        if target_type is str:
            return value

        if target_type is int:
            return self._string_to_int(value)

        if target_type is float:
            return self._string_to_float(value)

        if target_type is bool:
            return self._string_to_bool(value)

        if target_type is dict:
            return self._string_to_dict(value)

        if target_type is list:
            return self._string_to_list(value)

        if target_type is datetime:
            return self._string_to_datetime(value)

        if target_type is date:
            return self._string_to_date(value)

        if isinstance(target_type, type) and issubclass(target_type, Enum):
            return self._string_to_enum(value, target_type)

        raise CoercionError(
            value,
            target_type,
            f"Cannot coerce string to {target_type.__name__}"
        )

    def _string_to_int(self, value: str) -> int:
        """Convert string to int."""
        try:
            # Handle float strings like "123.0"
            float_val = float(value)
            if float_val.is_integer():
                return int(float_val)
            raise CoercionError(value, int, "Value has decimal component")
        except ValueError:
            raise CoercionError(value, int, "Not a valid integer string")

    def _string_to_float(self, value: str) -> float:
        """Convert string to float."""
        try:
            return float(value)
        except ValueError:
            raise CoercionError(value, float, "Not a valid float string")

    def _string_to_bool(self, value: str) -> bool:
        """Convert string to bool."""
        lower = value.lower().strip()

        if lower in self.TRUE_VALUES:
            return True
        if lower in self.FALSE_VALUES:
            return False

        raise CoercionError(
            value,
            bool,
            f"Ambiguous boolean string. Use one of: {self.TRUE_VALUES | self.FALSE_VALUES}"
        )

    def _string_to_dict(self, value: str) -> dict:
        """Convert JSON string to dict."""
        try:
            result = json.loads(value)
            if not isinstance(result, dict):
                raise CoercionError(value, dict, "JSON is not an object")
            return result
        except json.JSONDecodeError as e:
            raise CoercionError(value, dict, f"Invalid JSON: {e}")

    def _string_to_list(self, value: str) -> list:
        """Convert JSON string to list."""
        try:
            result = json.loads(value)
            if not isinstance(result, list):
                raise CoercionError(value, list, "JSON is not an array")
            return result
        except json.JSONDecodeError as e:
            raise CoercionError(value, list, f"Invalid JSON: {e}")

    def _string_to_datetime(self, value: str) -> datetime:
        """Convert ISO format string to datetime."""
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise CoercionError(
                value,
                datetime,
                "Not a valid ISO datetime format"
            )

    def _string_to_date(self, value: str) -> date:
        """Convert ISO format string to date."""
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise CoercionError(value, date, "Not a valid ISO date format")

    def _string_to_enum(self, value: str, enum_type: Type[Enum]) -> Enum:
        """Convert string to enum member."""
        # Try by name first
        try:
            return enum_type[value]
        except KeyError:
            pass

        # Try by value
        for member in enum_type:
            if str(member.value) == value:
                return member

        valid = [m.name for m in enum_type]
        raise CoercionError(
            value,
            enum_type,
            f"Not a valid enum member. Valid values: {valid}"
        )

    def _coerce_numeric(self, value: Union[int, float], target_type: Type) -> Union[int, float]:
        """Convert between numeric types."""
        if target_type is int:
            if isinstance(value, float):
                if value.is_integer():
                    return int(value)
                raise CoercionError(
                    value,
                    int,
                    "Float has decimal component, cannot safely convert to int"
                )
            return int(value)

        if target_type is float:
            return float(value)

        raise CoercionError(value, target_type, "Unknown numeric target type")

    def can_coerce(self, value: Any, target_type: Type) -> bool:
        """
        Check if a value can be coerced to the target type.

        Args:
            value: The value to check
            target_type: The type to coerce to

        Returns:
            True if coercion is possible, False otherwise
        """
        try:
            self.coerce(value, target_type)
            return True
        except CoercionError:
            return False
