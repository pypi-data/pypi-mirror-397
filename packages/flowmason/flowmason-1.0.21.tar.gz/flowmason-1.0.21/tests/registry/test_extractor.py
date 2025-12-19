"""
Tests for the Metadata Extractor.

Tests extraction of metadata from decorated component classes.
"""

import pytest

from flowmason_core.core.types import NodeInput, NodeOutput, OperatorInput, OperatorOutput, Field
from flowmason_core.core.decorators import node, operator
from flowmason_core.registry.extractor import MetadataExtractor


# Sample decorated classes for testing
@node(
    name="sample_node",
    category="testing",
    description="A sample node for testing",
    icon="test",
    color="#FF0000",
    version="2.0.0",
    author="Test Author",
    tags=["sample", "test"],
    recommended_providers={
        "anthropic": {"model": "claude-3-5-sonnet", "temperature": 0.5},
    },
    default_provider="anthropic",
    required_capabilities=["text_generation"],
)
class SampleNode:
    class Input(NodeInput):
        prompt: str = Field(description="The prompt")
        temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    class Output(NodeOutput):
        result: str
        confidence: float = 0.0

    async def execute(self, input, context):
        return self.Output(result="test", confidence=1.0)


@operator(
    name="sample_operator",
    category="testing",
    description="A sample operator for testing",
    icon="zap",
    color="#0000FF",
    version="1.5.0",
    author="Test Author",
    tags=["sample", "operator"],
)
class SampleOperator:
    class Input(OperatorInput):
        data: str = Field(description="Input data")

    class Output(OperatorOutput):
        transformed: str

    async def execute(self, input, context):
        return self.Output(transformed=input.data.upper())


# Invalid class (not decorated)
class NotAComponent:
    pass


class TestExtractFromClass:
    """Tests for extracting metadata from component classes."""

    def test_extract_node_metadata(self):
        """Test extracting metadata from a node class."""
        extractor = MetadataExtractor()

        info = extractor.extract_from_class(SampleNode)

        assert info.component_type == "sample_node"
        assert info.component_kind == "node"
        assert info.category == "testing"
        assert info.description == "A sample node for testing"
        assert info.version == "2.0.0"
        assert info.icon == "test"
        assert info.color == "#FF0000"
        assert info.author == "Test Author"
        assert info.tags == ["sample", "test"]
        assert info.requires_llm is True

    def test_extract_operator_metadata(self):
        """Test extracting metadata from an operator class."""
        extractor = MetadataExtractor()

        info = extractor.extract_from_class(SampleOperator)

        assert info.component_type == "sample_operator"
        assert info.component_kind == "operator"
        assert info.category == "testing"
        assert info.description == "A sample operator for testing"
        assert info.version == "1.5.0"
        assert info.requires_llm is False

    def test_extract_ai_config(self):
        """Test extracting AI configuration from a node."""
        extractor = MetadataExtractor()

        info = extractor.extract_from_class(SampleNode)

        assert info.recommended_providers is not None
        assert "anthropic" in info.recommended_providers
        assert info.default_provider == "anthropic"
        assert info.required_capabilities == ["text_generation"]

    def test_extract_from_invalid_class(self):
        """Test extracting from a non-component class."""
        extractor = MetadataExtractor()

        with pytest.raises(ValueError) as exc_info:
            extractor.extract_from_class(NotAComponent)

        assert "not a FlowMason component" in str(exc_info.value)


class TestSchemaExtraction:
    """Tests for schema extraction."""

    def test_extract_input_schema(self):
        """Test extracting input schema."""
        extractor = MetadataExtractor()

        schema = extractor.extract_input_schema(SampleNode)

        assert "properties" in schema
        assert "prompt" in schema["properties"]
        assert "temperature" in schema["properties"]
        assert schema["properties"]["prompt"]["type"] == "string"

    def test_extract_output_schema(self):
        """Test extracting output schema."""
        extractor = MetadataExtractor()

        schema = extractor.extract_output_schema(SampleNode)

        assert "properties" in schema
        assert "result" in schema["properties"]
        assert "confidence" in schema["properties"]

    def test_extract_decorator_metadata(self):
        """Test extracting raw decorator metadata."""
        extractor = MetadataExtractor()

        metadata = extractor.extract_decorator_metadata(SampleNode)

        assert metadata["name"] == "sample_node"
        assert metadata["category"] == "testing"
        assert "input_schema" in metadata
        assert "output_schema" in metadata


class TestComponentValidation:
    """Tests for component validation."""

    def test_validate_valid_node(self):
        """Test validating a valid node."""
        extractor = MetadataExtractor()

        is_valid, errors = extractor.validate_component(SampleNode)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_valid_operator(self):
        """Test validating a valid operator."""
        extractor = MetadataExtractor()

        is_valid, errors = extractor.validate_component(SampleOperator)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_class(self):
        """Test validating an invalid class."""
        extractor = MetadataExtractor()

        is_valid, errors = extractor.validate_component(NotAComponent)

        assert is_valid is False
        assert len(errors) > 0
        assert any("_flowmason_metadata" in e for e in errors)


class TestFieldInfo:
    """Tests for field info extraction."""

    def test_get_input_field_info(self):
        """Test getting input field info."""
        extractor = MetadataExtractor()

        field_info = extractor.get_field_info(SampleNode, "input")

        assert "prompt" in field_info
        assert field_info["prompt"]["type"] == "string"
        assert field_info["prompt"]["required"] is True

        assert "temperature" in field_info
        assert field_info["temperature"]["required"] is False

    def test_get_output_field_info(self):
        """Test getting output field info."""
        extractor = MetadataExtractor()

        field_info = extractor.get_field_info(SampleNode, "output")

        assert "result" in field_info
        assert "confidence" in field_info


class TestComponentTypeDetection:
    """Tests for component type detection."""

    def test_get_node_type(self):
        """Test getting component type for a node."""
        extractor = MetadataExtractor()

        comp_type = extractor.get_component_type(SampleNode)

        assert comp_type == "node"

    def test_get_operator_type(self):
        """Test getting component type for an operator."""
        extractor = MetadataExtractor()

        comp_type = extractor.get_component_type(SampleOperator)

        assert comp_type == "operator"

    def test_get_type_for_non_component(self):
        """Test getting component type for a non-component."""
        extractor = MetadataExtractor()

        comp_type = extractor.get_component_type(NotAComponent)

        assert comp_type is None
