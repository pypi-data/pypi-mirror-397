"""
Tests for the Type Coercion System.

Tests safe type conversions from configuration values to typed fields.
"""

import pytest
from typing import Optional, List, Dict, Union
from datetime import datetime, date
from enum import Enum

from flowmason_core.config.type_coercion import TypeCoercer, CoercionError


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TestTypeCoercerBasics:
    """Basic type coercion tests."""

    def test_no_coercion_needed(self):
        """Test that values of correct type pass through."""
        coercer = TypeCoercer()

        assert coercer.coerce("hello", str) == "hello"
        assert coercer.coerce(42, int) == 42
        assert coercer.coerce(3.14, float) == 3.14
        assert coercer.coerce(True, bool) is True
        assert coercer.coerce([1, 2], list) == [1, 2]
        assert coercer.coerce({"a": 1}, dict) == {"a": 1}


class TestStringToNumeric:
    """Tests for string to numeric conversions."""

    def test_string_to_int(self):
        """Test string to int conversion."""
        coercer = TypeCoercer()

        assert coercer.coerce("123", int) == 123
        assert coercer.coerce("-456", int) == -456
        assert coercer.coerce("0", int) == 0

    def test_string_to_int_from_float_string(self):
        """Test string like '123.0' converts to int."""
        coercer = TypeCoercer()

        assert coercer.coerce("123.0", int) == 123

    def test_string_to_int_fails_on_decimal(self):
        """Test string with decimal component fails."""
        coercer = TypeCoercer()

        with pytest.raises(CoercionError):
            coercer.coerce("123.5", int)

    def test_string_to_int_fails_on_invalid(self):
        """Test invalid string fails."""
        coercer = TypeCoercer()

        with pytest.raises(CoercionError):
            coercer.coerce("abc", int)

    def test_string_to_float(self):
        """Test string to float conversion."""
        coercer = TypeCoercer()

        assert coercer.coerce("3.14", float) == 3.14
        assert coercer.coerce("-2.5", float) == -2.5
        assert coercer.coerce("42", float) == 42.0

    def test_string_to_float_fails_on_invalid(self):
        """Test invalid string fails."""
        coercer = TypeCoercer()

        with pytest.raises(CoercionError):
            coercer.coerce("not_a_number", float)


class TestStringToBool:
    """Tests for string to boolean conversions."""

    def test_true_strings(self):
        """Test various true string values."""
        coercer = TypeCoercer()

        assert coercer.coerce("true", bool) is True
        assert coercer.coerce("True", bool) is True
        assert coercer.coerce("TRUE", bool) is True
        assert coercer.coerce("yes", bool) is True
        assert coercer.coerce("1", bool) is True
        assert coercer.coerce("on", bool) is True
        assert coercer.coerce("enabled", bool) is True

    def test_false_strings(self):
        """Test various false string values."""
        coercer = TypeCoercer()

        assert coercer.coerce("false", bool) is False
        assert coercer.coerce("False", bool) is False
        assert coercer.coerce("FALSE", bool) is False
        assert coercer.coerce("no", bool) is False
        assert coercer.coerce("0", bool) is False
        assert coercer.coerce("off", bool) is False
        assert coercer.coerce("disabled", bool) is False

    def test_ambiguous_bool_fails(self):
        """Test that ambiguous strings fail."""
        coercer = TypeCoercer()

        with pytest.raises(CoercionError):
            coercer.coerce("maybe", bool)

        with pytest.raises(CoercionError):
            coercer.coerce("2", bool)


class TestStringToJson:
    """Tests for JSON string conversions."""

    def test_string_to_dict(self):
        """Test JSON string to dict conversion."""
        coercer = TypeCoercer()

        result = coercer.coerce('{"key": "value", "num": 42}', dict)
        assert result == {"key": "value", "num": 42}

    def test_string_to_list(self):
        """Test JSON string to list conversion."""
        coercer = TypeCoercer()

        result = coercer.coerce('[1, 2, 3]', list)
        assert result == [1, 2, 3]

    def test_invalid_json_dict_fails(self):
        """Test invalid JSON fails for dict."""
        coercer = TypeCoercer()

        with pytest.raises(CoercionError):
            coercer.coerce('not valid json', dict)

    def test_wrong_json_type_fails(self):
        """Test JSON of wrong type fails."""
        coercer = TypeCoercer()

        # JSON array when dict expected
        with pytest.raises(CoercionError):
            coercer.coerce('[1, 2, 3]', dict)

        # JSON object when list expected
        with pytest.raises(CoercionError):
            coercer.coerce('{"a": 1}', list)


class TestDateTimeCoercion:
    """Tests for datetime conversions."""

    def test_string_to_datetime(self):
        """Test ISO datetime string conversion."""
        coercer = TypeCoercer()

        result = coercer.coerce("2024-12-09T10:30:00", datetime)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 9
        assert result.hour == 10
        assert result.minute == 30

    def test_string_to_datetime_with_z(self):
        """Test datetime string with Z suffix."""
        coercer = TypeCoercer()

        result = coercer.coerce("2024-12-09T10:30:00Z", datetime)
        assert isinstance(result, datetime)

    def test_string_to_date(self):
        """Test ISO date string conversion."""
        coercer = TypeCoercer()

        result = coercer.coerce("2024-12-09", date)
        assert isinstance(result, date)
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 9

    def test_invalid_datetime_fails(self):
        """Test invalid datetime string fails."""
        coercer = TypeCoercer()

        with pytest.raises(CoercionError):
            coercer.coerce("not a date", datetime)


class TestEnumCoercion:
    """Tests for enum conversions."""

    def test_string_to_enum_by_name(self):
        """Test converting string to enum by name."""
        coercer = TypeCoercer()

        result = coercer.coerce("HIGH", Priority)
        assert result == Priority.HIGH

    def test_string_to_enum_by_value(self):
        """Test converting string to enum by value."""
        coercer = TypeCoercer()

        result = coercer.coerce("high", Priority)
        assert result == Priority.HIGH

    def test_invalid_enum_fails(self):
        """Test invalid enum value fails."""
        coercer = TypeCoercer()

        with pytest.raises(CoercionError):
            coercer.coerce("CRITICAL", Priority)


class TestOptionalCoercion:
    """Tests for Optional type handling."""

    def test_none_to_optional(self):
        """Test None converts to Optional."""
        coercer = TypeCoercer()

        result = coercer.coerce(None, Optional[str])
        assert result is None

    def test_value_to_optional(self):
        """Test value converts for Optional type."""
        coercer = TypeCoercer()

        result = coercer.coerce("hello", Optional[str])
        assert result == "hello"

        result = coercer.coerce("42", Optional[int])
        assert result == 42

    def test_none_to_non_optional_fails(self):
        """Test None fails for non-Optional type."""
        coercer = TypeCoercer()

        with pytest.raises(CoercionError):
            coercer.coerce(None, str)


class TestUnionCoercion:
    """Tests for Union type handling."""

    def test_union_first_match(self):
        """Test Union uses first matching type."""
        coercer = TypeCoercer()

        # String matches str
        result = coercer.coerce("hello", Union[str, int])
        assert result == "hello"

    def test_union_second_match(self):
        """Test Union falls back to second type."""
        coercer = TypeCoercer()

        # Int doesn't match str, but matches int
        result = coercer.coerce(42, Union[str, int])
        # Will match str first since str can accept anything in coercion
        # Actually 42 is int, not str, so it should return 42
        assert result == 42


class TestGenericCoercion:
    """Tests for generic type coercion."""

    def test_typed_list(self):
        """Test list[int] coercion."""
        coercer = TypeCoercer()

        # List of strings to list of ints
        result = coercer.coerce(["1", "2", "3"], List[int])
        assert result == [1, 2, 3]

    def test_typed_dict(self):
        """Test dict[str, int] coercion."""
        coercer = TypeCoercer()

        result = coercer.coerce({"a": "1", "b": "2"}, Dict[str, int])
        assert result == {"a": 1, "b": 2}

    def test_json_string_to_typed_list(self):
        """Test JSON string to typed list."""
        coercer = TypeCoercer()

        result = coercer.coerce('["1", "2", "3"]', List[int])
        assert result == [1, 2, 3]


class TestNumericCoercion:
    """Tests for numeric type coercion."""

    def test_int_to_float(self):
        """Test int to float conversion."""
        coercer = TypeCoercer()

        result = coercer.coerce(42, float)
        assert result == 42.0
        assert isinstance(result, float)

    def test_float_to_int_whole(self):
        """Test whole float to int conversion."""
        coercer = TypeCoercer()

        result = coercer.coerce(42.0, int)
        assert result == 42
        assert isinstance(result, int)

    def test_float_to_int_decimal_fails(self):
        """Test float with decimal to int fails."""
        coercer = TypeCoercer()

        with pytest.raises(CoercionError):
            coercer.coerce(42.5, int)


class TestCanCoerce:
    """Tests for the can_coerce utility method."""

    def test_can_coerce_returns_true(self):
        """Test can_coerce returns True for valid coercions."""
        coercer = TypeCoercer()

        assert coercer.can_coerce("123", int) is True
        assert coercer.can_coerce("true", bool) is True
        assert coercer.can_coerce('{"a": 1}', dict) is True

    def test_can_coerce_returns_false(self):
        """Test can_coerce returns False for invalid coercions."""
        coercer = TypeCoercer()

        assert coercer.can_coerce("abc", int) is False
        assert coercer.can_coerce("maybe", bool) is False
        assert coercer.can_coerce("not json", dict) is False
