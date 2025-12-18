"""
FlowMason Configuration System.

Provides the Config-to-Schema mapping system that converts pipeline
configuration (JSON) into typed component Input models (Pydantic).

Main Components:
- InputMapper: Maps ComponentConfig to Pydantic Input instances
- TemplateResolver: Resolves {{variable}} templates
- TypeCoercer: Safe type conversions
- SchemaValidator: Pre-execution validation

Example:
    from flowmason_core.config import InputMapper, ExecutionContext

    context = ExecutionContext(
        run_id="run_123",
        pipeline_id="my-pipeline",
        pipeline_version="1.0.0",
        pipeline_input={"text": "Hello"}
    )

    mapper = InputMapper(context)

    input_instance = mapper.map_config_to_input(
        component_config,
        ComponentClass.Input,
        upstream_outputs={}
    )
"""

from flowmason_core.config.input_mapper import FieldMapper, InputMapper
from flowmason_core.config.schema_validator import OutputValidator, SchemaValidator
from flowmason_core.config.template_resolver import TemplateResolver
from flowmason_core.config.type_coercion import CoercionError, TypeCoercer
from flowmason_core.config.types import (
    ComponentConfig,
    CompositionConfig,
    ExecutionContext,
    LLMHelper,
    MappingError,
    PipelineConfig,
    PipelineInput,
    PipelineOutput,
    RetryConfig,
    TemplateError,
    ValidationError,
    ValidationResult,
)

__all__ = [
    # Types
    "RetryConfig",
    "ComponentConfig",
    "CompositionConfig",
    "PipelineInput",
    "PipelineOutput",
    "PipelineConfig",
    "ExecutionContext",
    "LLMHelper",
    "ValidationError",
    "ValidationResult",
    "MappingError",
    "TemplateError",
    # Template resolution
    "TemplateResolver",
    # Type coercion
    "TypeCoercer",
    "CoercionError",
    # Input mapping
    "InputMapper",
    "FieldMapper",
    # Validation
    "SchemaValidator",
    "OutputValidator",
]
