"""
Tests for the Input Mapper.

Tests that ComponentConfig is correctly mapped to Pydantic Input instances.
"""

import pytest
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

from flowmason_core.config import (
    InputMapper,
    FieldMapper,
    ComponentConfig,
    ExecutionContext,
    MappingError,
)
from flowmason_core.core.types import NodeInput, OperatorInput


# Test Input classes
class SimpleInput(NodeInput):
    """Simple input for testing."""
    text: str
    count: int = 10


class ComplexInput(NodeInput):
    """Complex input with various types."""
    prompt: str
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1000)
    stop_sequences: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)
    debug: bool = False


class NestedInput(NodeInput):
    """Input with nested structure."""
    text: str
    config: Dict[str, int]


class OptionalInput(NodeInput):
    """Input with optional fields."""
    required_field: str
    optional_field: Optional[str] = None
    default_field: str = "default"


class TestInputMapperBasics:
    """Basic input mapping tests."""

    def test_map_simple_input(self):
        """Test mapping simple fields."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={"text": "Hello", "count": 42}
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "text": "{{input.text}}",
                "count": "{{input.count}}"
            }
        )

        result = mapper.map_config_to_input(config, SimpleInput)

        assert isinstance(result, SimpleInput)
        assert result.text == "Hello"
        assert result.count == 42

    def test_map_with_defaults(self):
        """Test that defaults are used for unmapped fields."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={"text": "Hello"}
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "text": "{{input.text}}"
            }
        )

        result = mapper.map_config_to_input(config, SimpleInput)

        assert result.text == "Hello"
        assert result.count == 10  # Default value

    def test_map_static_values(self):
        """Test mapping static (non-template) values."""
        mapper = InputMapper()

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "text": "Static text",
                "count": 99
            }
        )

        result = mapper.map_config_to_input(config, SimpleInput)

        assert result.text == "Static text"
        assert result.count == 99


class TestInputMapperTemplates:
    """Tests for template resolution in input mapping."""

    def test_map_from_pipeline_input(self):
        """Test mapping from {{input.*}} templates."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={
                "user_text": "Generate something",
                "temp": 0.9
            }
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "prompt": "{{input.user_text}}",
                "temperature": "{{input.temp}}"
            }
        )

        result = mapper.map_config_to_input(config, ComplexInput)

        assert result.prompt == "Generate something"
        assert result.temperature == 0.9

    def test_map_from_upstream(self):
        """Test mapping from {{upstream.*}} templates."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={}
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "text": "{{upstream.previous.output}}"
            }
        )

        upstream_outputs = {
            "previous": {"output": "Previous result"}
        }

        result = mapper.map_config_to_input(config, SimpleInput, upstream_outputs)

        assert result.text == "Previous result"

    def test_map_from_context(self):
        """Test mapping from {{context.*}} templates."""
        context = ExecutionContext(
            run_id="run_abc",
            pipeline_id="my-pipeline",
            pipeline_version="2.0.0",
            pipeline_input={}
        )
        mapper = InputMapper(context)

        # Use a simple test - embed context in a string
        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "text": "Run: {{context.run_id}}"
            }
        )

        result = mapper.map_config_to_input(config, SimpleInput)

        assert "run_abc" in result.text


class TestInputMapperTypeCoercion:
    """Tests for type coercion during mapping."""

    def test_coerce_string_to_int(self):
        """Test coercing string to int."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={"count_str": "42"}
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "text": "hello",
                "count": "{{input.count_str}}"
            }
        )

        result = mapper.map_config_to_input(config, SimpleInput)

        assert result.count == 42
        assert isinstance(result.count, int)

    def test_coerce_string_to_float(self):
        """Test coercing string to float."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={"temp_str": "0.9"}
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "prompt": "test",
                "temperature": "{{input.temp_str}}"
            }
        )

        result = mapper.map_config_to_input(config, ComplexInput)

        assert result.temperature == 0.9
        assert isinstance(result.temperature, float)

    def test_coerce_string_to_bool(self):
        """Test coercing string to bool."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={"debug_str": "true"}
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "prompt": "test",
                "debug": "{{input.debug_str}}"
            }
        )

        result = mapper.map_config_to_input(config, ComplexInput)

        assert result.debug is True


class TestInputMapperComplexTypes:
    """Tests for complex type mapping."""

    def test_map_dict(self):
        """Test mapping dict fields."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={
                "meta": {"key1": "value1", "key2": "value2"}
            }
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "prompt": "test",
                "metadata": "{{input.meta}}"
            }
        )

        result = mapper.map_config_to_input(config, ComplexInput)

        assert result.metadata == {"key1": "value1", "key2": "value2"}

    def test_map_list(self):
        """Test mapping list fields."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={
                "stops": ["END", "STOP", "DONE"]
            }
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "prompt": "test",
                "stop_sequences": "{{input.stops}}"
            }
        )

        result = mapper.map_config_to_input(config, ComplexInput)

        assert result.stop_sequences == ["END", "STOP", "DONE"]


class TestInputMapperValidation:
    """Tests for mapping validation."""

    def test_validate_mapping_success(self):
        """Test validation passes for valid mapping."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={"text": "hello"}
        )
        mapper = InputMapper(context)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "required_field": "{{input.text}}"
            }
        )

        available_context = {
            "input": {"text": "hello"},
            "upstream": {},
            "env": {},
            "context": {}
        }

        result = mapper.validate_mapping(config, OptionalInput, available_context)

        assert result.is_valid

    def test_validate_mapping_missing_required(self):
        """Test validation catches missing required fields."""
        mapper = InputMapper()

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "optional_field": "value"
            }
        )

        available_context = {
            "input": {},
            "upstream": {},
            "env": {},
            "context": {}
        }

        result = mapper.validate_mapping(config, OptionalInput, available_context)

        assert not result.is_valid
        assert any("required_field" in e.field for e in result.errors)


class TestInputMapperErrors:
    """Tests for error handling."""

    def test_missing_template_error(self):
        """Test error when template cannot be resolved."""
        context = ExecutionContext(
            run_id="run_123",
            pipeline_id="test",
            pipeline_version="1.0.0",
            pipeline_input={}
        )
        mapper = InputMapper(context, strict_templates=True)

        config = ComponentConfig(
            id="test",
            type="test_node",
            input_mapping={
                "text": "{{input.nonexistent}}"
            }
        )

        with pytest.raises(MappingError) as exc_info:
            mapper.map_config_to_input(config, SimpleInput)

        assert "template" in str(exc_info.value).lower()


class TestFieldMapper:
    """Tests for the FieldMapper utility."""

    def test_set_nested_value(self):
        """Test setting values at nested paths."""
        data = {}
        FieldMapper.set_nested_value(data, "a.b.c", "value")

        assert data["a"]["b"]["c"] == "value"

    def test_set_nested_value_with_existing(self):
        """Test setting nested value with existing structure."""
        data = {"a": {"existing": 1}}
        FieldMapper.set_nested_value(data, "a.b.c", "value")

        assert data["a"]["existing"] == 1
        assert data["a"]["b"]["c"] == "value"

    def test_get_nested_value(self):
        """Test getting values at nested paths."""
        data = {"a": {"b": {"c": "value"}}}

        result = FieldMapper.get_nested_value(data, "a.b.c")
        assert result == "value"

    def test_get_nested_value_with_default(self):
        """Test getting nested value with default."""
        data = {"a": {"b": {}}}

        result = FieldMapper.get_nested_value(data, "a.b.c", default="missing")
        assert result == "missing"

    def test_set_array_index(self):
        """Test setting value at array index."""
        data = {}
        FieldMapper.set_nested_value(data, "items[0]", "first")

        assert data["items"][0] == "first"

    def test_get_array_index(self):
        """Test getting value at array index."""
        data = {"items": ["a", "b", "c"]}

        result = FieldMapper.get_nested_value(data, "items[1]")
        assert result == "b"
