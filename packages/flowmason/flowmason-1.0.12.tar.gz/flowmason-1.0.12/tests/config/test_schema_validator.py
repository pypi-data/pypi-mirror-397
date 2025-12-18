"""
Tests for the Schema Validator.

Tests pre-execution validation of configurations.
"""

import pytest
from typing import Optional, List
from pydantic import BaseModel, Field

from flowmason_core.config import (
    ComponentConfig,
    PipelineConfig,
    PipelineInput,
    PipelineOutput,
)
from flowmason_core.config.schema_validator import SchemaValidator, OutputValidator
from flowmason_core.core.types import NodeInput, NodeOutput


# Test schemas
class TriageInput(NodeInput):
    """Test triage input."""
    ticket_text: str
    customer_id: str
    priority_hint: Optional[str] = None


class TriageOutput(NodeOutput):
    """Test triage output."""
    category: str
    priority: str
    confidence: float


class GeneratorInput(NodeInput):
    """Test generator input."""
    prompt: str
    max_tokens: int = 1000


class GeneratorOutput(NodeOutput):
    """Test generator output."""
    content: str
    tokens_used: int


class TestSchemaValidatorComponent:
    """Tests for component config validation."""

    def test_validate_valid_config(self):
        """Test validation passes for valid config."""
        validator = SchemaValidator()

        config = ComponentConfig(
            id="triage",
            type="support_triage",
            input_mapping={
                "ticket_text": "{{input.text}}",
                "customer_id": "{{input.customer}}"
            }
        )

        available_context = {
            "input": {"text": "Help!", "customer": "cust_123"},
            "upstream": {},
            "env": {},
            "context": {}
        }

        result = validator.validate_component_config(
            config,
            TriageInput,
            available_context
        )

        assert result.is_valid

    def test_validate_missing_required_field(self):
        """Test validation catches missing required field."""
        validator = SchemaValidator()

        config = ComponentConfig(
            id="triage",
            type="support_triage",
            input_mapping={
                "ticket_text": "{{input.text}}"
                # Missing customer_id
            }
        )

        available_context = {
            "input": {"text": "Help!"},
            "upstream": {},
            "env": {},
            "context": {}
        }

        result = validator.validate_component_config(
            config,
            TriageInput,
            available_context
        )

        assert not result.is_valid
        assert any("customer_id" in e.field for e in result.errors)
        assert any(e.error_type == "missing_required" for e in result.errors)

    def test_validate_invalid_template(self):
        """Test validation catches invalid template references."""
        validator = SchemaValidator()

        config = ComponentConfig(
            id="triage",
            type="support_triage",
            input_mapping={
                "ticket_text": "{{input.nonexistent}}",
                "customer_id": "cust_123"
            }
        )

        available_context = {
            "input": {"text": "Help!"},
            "upstream": {},
            "env": {},
            "context": {}
        }

        result = validator.validate_component_config(
            config,
            TriageInput,
            available_context
        )

        assert not result.is_valid
        assert any(e.error_type == "invalid_template" for e in result.errors)

    def test_validate_unknown_field_warning(self):
        """Test validation warns about unknown fields."""
        validator = SchemaValidator()

        config = ComponentConfig(
            id="triage",
            type="support_triage",
            input_mapping={
                "ticket_text": "text",
                "customer_id": "cust_123",
                "unknown_field": "value"  # Not in schema
            }
        )

        available_context = {
            "input": {},
            "upstream": {},
            "env": {},
            "context": {}
        }

        result = validator.validate_component_config(
            config,
            TriageInput,
            available_context
        )

        assert any("unknown_field" in w for w in result.warnings)

    def test_validate_with_upstream_template(self):
        """Test validation with upstream references."""
        validator = SchemaValidator()

        config = ComponentConfig(
            id="generator",
            type="generator",
            input_mapping={
                "prompt": "{{upstream.classify.category}}"
            }
        )

        available_context = {
            "input": {},
            "upstream": {"classify": {"category": "support"}},
            "env": {},
            "context": {}
        }

        result = validator.validate_component_config(
            config,
            GeneratorInput,
            available_context
        )

        assert result.is_valid


class TestSchemaValidatorPipeline:
    """Tests for pipeline config validation."""

    def test_validate_valid_pipeline(self):
        """Test validation passes for valid pipeline."""
        validator = SchemaValidator()

        pipeline_config = PipelineConfig(
            id="test-pipeline",
            name="Test Pipeline",
            version="1.0.0",
            input_schema=PipelineInput(
                properties={
                    "text": {"type": "string"},
                    "customer": {"type": "string"}
                },
                required=["text", "customer"]
            ),
            output_schema=PipelineOutput(
                properties={
                    "result": {"type": "string"}
                }
            ),
            stages=[
                ComponentConfig(
                    id="triage",
                    type="support_triage",
                    input_mapping={
                        "ticket_text": "{{input.text}}",
                        "customer_id": "{{input.customer}}"
                    }
                )
            ]
        )

        component_schemas = {
            "support_triage": TriageInput
        }

        result = validator.validate_pipeline_config(pipeline_config, component_schemas)

        assert result.is_valid

    def test_validate_duplicate_stage_id(self):
        """Test validation catches duplicate stage IDs."""
        validator = SchemaValidator()

        pipeline_config = PipelineConfig(
            id="test-pipeline",
            name="Test Pipeline",
            version="1.0.0",
            stages=[
                ComponentConfig(id="stage1", type="generator", input_mapping={"prompt": "a"}),
                ComponentConfig(id="stage1", type="generator", input_mapping={"prompt": "b"}),  # Duplicate
            ]
        )

        component_schemas = {"generator": GeneratorInput}

        result = validator.validate_pipeline_config(pipeline_config, component_schemas)

        assert not result.is_valid
        assert any("duplicate" in e.error_type.lower() for e in result.errors)

    def test_validate_invalid_dependency(self):
        """Test validation catches invalid dependencies."""
        validator = SchemaValidator()

        pipeline_config = PipelineConfig(
            id="test-pipeline",
            name="Test Pipeline",
            version="1.0.0",
            stages=[
                ComponentConfig(
                    id="stage2",
                    type="generator",
                    input_mapping={"prompt": "test"},
                    depends_on=["nonexistent"]  # Invalid dependency
                )
            ]
        )

        component_schemas = {"generator": GeneratorInput}

        result = validator.validate_pipeline_config(pipeline_config, component_schemas)

        assert not result.is_valid
        assert any("dependency" in e.error_type.lower() for e in result.errors)

    def test_validate_unknown_component_type(self):
        """Test validation catches unknown component types."""
        validator = SchemaValidator()

        pipeline_config = PipelineConfig(
            id="test-pipeline",
            name="Test Pipeline",
            version="1.0.0",
            stages=[
                ComponentConfig(
                    id="stage1",
                    type="unknown_component",
                    input_mapping={}
                )
            ]
        )

        component_schemas = {"generator": GeneratorInput}  # Doesn't include unknown_component

        result = validator.validate_pipeline_config(pipeline_config, component_schemas)

        assert not result.is_valid
        assert any("unknown_component" in e.error_type.lower() or "unknown_component" in e.message for e in result.errors)

    def test_validate_invalid_output_stage_id(self):
        """Test validation catches invalid output_stage_id."""
        validator = SchemaValidator()

        pipeline_config = PipelineConfig(
            id="test-pipeline",
            name="Test Pipeline",
            version="1.0.0",
            stages=[
                ComponentConfig(id="stage1", type="generator", input_mapping={"prompt": "test"})
            ],
            output_stage_id="nonexistent"  # Invalid
        )

        component_schemas = {"generator": GeneratorInput}

        result = validator.validate_pipeline_config(pipeline_config, component_schemas)

        assert not result.is_valid
        assert any("output_stage_id" in e.field for e in result.errors)


class TestOutputValidator:
    """Tests for output validation."""

    def test_validate_valid_output(self):
        """Test validation passes for valid output."""
        validator = OutputValidator()

        output = TriageOutput(
            category="support",
            priority="high",
            confidence=0.95
        )

        result = validator.validate_output(output, TriageOutput)

        assert result.is_valid

    def test_validate_dict_output(self):
        """Test validation of dict output against schema."""
        validator = OutputValidator()

        output = {
            "category": "support",
            "priority": "high",
            "confidence": 0.95
        }

        result = validator.validate_output(output, TriageOutput)

        assert result.is_valid

    def test_validate_invalid_dict_output(self):
        """Test validation catches invalid dict output."""
        validator = OutputValidator()

        output = {
            "category": "support"
            # Missing priority and confidence
        }

        result = validator.validate_output(output, TriageOutput)

        assert not result.is_valid

    def test_validate_wrong_type(self):
        """Test validation catches wrong type."""
        validator = OutputValidator()

        output = "just a string"

        result = validator.validate_output(output, TriageOutput)

        assert not result.is_valid
        assert any(e.error_type == "type_mismatch" for e in result.errors)


class TestOutputValidatorJsonSchema:
    """Tests for JSON schema validation."""

    def test_validate_json_schema_object(self):
        """Test validating object against JSON schema."""
        validator = OutputValidator()

        output = {
            "name": "Alice",
            "age": 30
        }

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }

        result = validator.validate_against_json_schema(output, schema)

        assert result.is_valid

    def test_validate_json_schema_missing_required(self):
        """Test validation catches missing required property."""
        validator = OutputValidator()

        output = {
            "age": 30
            # Missing required 'name'
        }

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }

        result = validator.validate_against_json_schema(output, schema)

        assert not result.is_valid
        assert any("name" in e.field for e in result.errors)

    def test_validate_json_schema_type_mismatch(self):
        """Test validation catches type mismatch."""
        validator = OutputValidator()

        output = "string instead of object"

        schema = {
            "type": "object"
        }

        result = validator.validate_against_json_schema(output, schema)

        assert not result.is_valid

    def test_validate_json_schema_array(self):
        """Test validating array against JSON schema."""
        validator = OutputValidator()

        output = [1, 2, 3]

        schema = {"type": "array"}

        result = validator.validate_against_json_schema(output, schema)

        assert result.is_valid

    def test_validate_json_schema_string(self):
        """Test validating string against JSON schema."""
        validator = OutputValidator()

        output = "hello"

        schema = {"type": "string"}

        result = validator.validate_against_json_schema(output, schema)

        assert result.is_valid

    def test_validate_json_schema_integer(self):
        """Test validating integer against JSON schema."""
        validator = OutputValidator()

        output = 42

        schema = {"type": "integer"}

        result = validator.validate_against_json_schema(output, schema)

        assert result.is_valid

    def test_validate_json_schema_boolean(self):
        """Test validating boolean against JSON schema."""
        validator = OutputValidator()

        output = True

        schema = {"type": "boolean"}

        result = validator.validate_against_json_schema(output, schema)

        assert result.is_valid
