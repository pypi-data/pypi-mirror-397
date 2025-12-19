"""
End-to-End Integration Tests for FlowMason.

Tests the complete flow from package loading to pipeline execution.
Verifies the core principles:
- ZERO hardcoded components - everything from packages
- Universal executor - ONE code path for ALL components
- Dynamic loading from registry
"""

import json
import zipfile
import pytest
from pathlib import Path

from flowmason_core.registry import ComponentRegistry
from flowmason_core.config import (
    ComponentConfig,
    PipelineConfig,
    ExecutionContext,
)
from flowmason_core.execution import (
    UniversalExecutor,
    DAGExecutor,
    UsageMetrics,
)


# ============================================================================
# Test Component Source Code
# ============================================================================

SUMMARIZER_NODE_SOURCE = '''
"""Summarizer Node - summarizes text content."""

from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node


@node(
    name="summarizer",
    category="nlp",
    description="Summarize text content",
    version="1.0.0",
    author="Integration Test",
    tags=["nlp", "summarization"],
)
class SummarizerNode:
    """Summarizes text content."""

    class Input(NodeInput):
        text: str = Field(description="Text to summarize")
        max_length: int = Field(default=100, description="Max summary length")

    class Output(NodeOutput):
        summary: str
        original_length: int = 0
        summary_length: int = 0

    async def execute(self, input: "SummarizerNode.Input", context) -> "SummarizerNode.Output":
        # Simulate summarization
        summary = input.text[:input.max_length] + "..."
        return self.Output(
            summary=summary,
            original_length=len(input.text),
            summary_length=len(summary)
        )
'''

SENTIMENT_NODE_SOURCE = '''
"""Sentiment Analysis Node - analyzes sentiment of text."""

from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node


@node(
    name="sentiment_analyzer",
    category="nlp",
    description="Analyze sentiment of text",
    version="1.0.0",
    author="Integration Test",
    tags=["nlp", "sentiment"],
)
class SentimentAnalyzerNode:
    """Analyzes text sentiment."""

    class Input(NodeInput):
        text: str = Field(description="Text to analyze")

    class Output(NodeOutput):
        sentiment: str
        confidence: float = 0.9

    async def execute(self, input: "SentimentAnalyzerNode.Input", context) -> "SentimentAnalyzerNode.Output":
        # Simulate sentiment analysis
        text_lower = input.text.lower()
        if any(word in text_lower for word in ["great", "excellent", "amazing", "good"]):
            sentiment = "positive"
        elif any(word in text_lower for word in ["bad", "terrible", "awful", "poor"]):
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return self.Output(sentiment=sentiment, confidence=0.85)
'''

TEXT_CONCAT_OPERATOR_SOURCE = '''
"""Text Concatenation Operator - joins multiple texts."""

from typing import List
from flowmason_core.core.types import OperatorInput, OperatorOutput, Field
from flowmason_core.core.decorators import operator


@operator(
    name="text_concat",
    category="transform",
    description="Concatenate multiple text strings",
    version="1.0.0",
    author="Integration Test",
    tags=["text", "transform"],
)
class TextConcatOperator:
    """Concatenates text strings."""

    class Input(OperatorInput):
        texts: List[str] = Field(description="List of texts to concatenate")
        separator: str = Field(default=" ", description="Separator between texts")

    class Output(OperatorOutput):
        result: str
        count: int = 0

    async def execute(self, input: "TextConcatOperator.Input", context) -> "TextConcatOperator.Output":
        result = input.separator.join(input.texts)
        return self.Output(result=result, count=len(input.texts))
'''

FILTER_OPERATOR_SOURCE = '''
"""Filter Operator - conditionally passes data through."""

from typing import Any
from flowmason_core.core.types import OperatorInput, OperatorOutput, Field
from flowmason_core.core.decorators import operator


@operator(
    name="conditional_filter",
    category="control",
    description="Filter data based on condition",
    version="1.0.0",
    author="Integration Test",
    tags=["filter", "control"],
)
class ConditionalFilterOperator:
    """Conditionally filters data."""

    class Input(OperatorInput):
        data: Any = Field(description="Data to filter")
        condition: str = Field(description="Filter condition: 'pass' or 'block'")

    class Output(OperatorOutput):
        result: Any = None
        passed: bool = False

    async def execute(self, input: "ConditionalFilterOperator.Input", context) -> "ConditionalFilterOperator.Output":
        passed = input.condition.lower() == "pass"
        return self.Output(
            result=input.data if passed else None,
            passed=passed
        )
'''


# ============================================================================
# Fixtures
# ============================================================================

def create_package(output_dir: Path, name: str, source: str, comp_type: str = "node") -> Path:
    """Create a .fmpkg package file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    pkg_path = output_dir / f"{name}-1.0.0.fmpkg"

    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": f"Integration test package: {name}",
        "type": comp_type,
        "author": {"name": "Integration Test", "email": "test@test.com"},
        "license": "MIT",
        "category": "testing",
        "tags": ["integration-test"],
        "entry_point": "index.py",
        "requires_llm": comp_type == "node",
        "dependencies": []
    }

    with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("flowmason-package.json", json.dumps(manifest, indent=2))
        zf.writestr("index.py", source)

    return pkg_path


@pytest.fixture
def integration_packages_dir(tmp_path):
    """Create a directory with all integration test packages."""
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir()

    # Create all test packages
    create_package(packages_dir, "summarizer", SUMMARIZER_NODE_SOURCE, "node")
    create_package(packages_dir, "sentiment_analyzer", SENTIMENT_NODE_SOURCE, "node")
    create_package(packages_dir, "text_concat", TEXT_CONCAT_OPERATOR_SOURCE, "operator")
    create_package(packages_dir, "conditional_filter", FILTER_OPERATOR_SOURCE, "operator")

    return packages_dir


@pytest.fixture
def registry(integration_packages_dir):
    """Create a registry with all integration test packages."""
    reg = ComponentRegistry(integration_packages_dir, auto_scan=True)
    return reg


@pytest.fixture
def execution_context():
    """Create a standard execution context."""
    return ExecutionContext(
        run_id="integration_test_run",
        pipeline_id="integration-test-pipeline",
        pipeline_version="1.0.0",
        pipeline_input={}
    )


# ============================================================================
# Test: Dynamic Package Loading
# ============================================================================

class TestDynamicLoading:
    """Tests that components load dynamically from packages."""

    def test_all_packages_loaded(self, registry):
        """Verify all test packages were loaded."""
        components = registry.list_components()
        component_types = [c.component_type for c in components]

        assert "summarizer" in component_types
        assert "sentiment_analyzer" in component_types
        assert "text_concat" in component_types
        assert "conditional_filter" in component_types

    def test_nodes_and_operators_distinguished(self, registry):
        """Verify nodes and operators are correctly categorized."""
        components = registry.list_components()

        nodes = [c for c in components if c.component_kind == "node"]
        operators = [c for c in components if c.component_kind == "operator"]

        assert len(nodes) == 2
        assert len(operators) == 2

        node_types = [n.component_type for n in nodes]
        assert "summarizer" in node_types
        assert "sentiment_analyzer" in node_types

        operator_types = [o.component_type for o in operators]
        assert "text_concat" in operator_types
        assert "conditional_filter" in operator_types

    def test_component_metadata_extracted(self, registry):
        """Verify component metadata is correctly extracted."""
        summarizer = registry.get_component_metadata("summarizer")

        assert summarizer.component_type == "summarizer"
        assert summarizer.category == "nlp"
        assert summarizer.version == "1.0.0"
        assert "nlp" in summarizer.tags

    def test_component_schemas_extracted(self, registry):
        """Verify input/output schemas are extracted."""
        summarizer = registry.get_component_metadata("summarizer")

        # Check input schema
        assert "text" in summarizer.input_schema["properties"]
        assert "max_length" in summarizer.input_schema["properties"]

        # Check output schema
        assert "summary" in summarizer.output_schema["properties"]


# ============================================================================
# Test: Universal Executor (One Path for All)
# ============================================================================

class TestUniversalExecution:
    """Tests that ANY component executes through the same code path."""

    @pytest.mark.asyncio
    async def test_execute_node(self, registry, execution_context):
        """Test executing a node component."""
        executor = UniversalExecutor(registry, execution_context)

        config = ComponentConfig(
            id="summarize_step",
            type="summarizer",
            input_mapping={
                "text": "This is a long text that needs to be summarized into something shorter.",
                "max_length": 20
            }
        )

        result = await executor.execute_component(config)

        assert result.status == "success"
        assert result.component_type == "summarizer"
        assert "summary" in result.output
        assert len(result.output["summary"]) <= 25  # 20 + "..."

    @pytest.mark.asyncio
    async def test_execute_operator(self, registry, execution_context):
        """Test executing an operator component."""
        executor = UniversalExecutor(registry, execution_context)

        config = ComponentConfig(
            id="concat_step",
            type="text_concat",
            input_mapping={
                "texts": ["Hello", "World", "!"],
                "separator": "-"
            }
        )

        result = await executor.execute_component(config)

        assert result.status == "success"
        assert result.component_type == "text_concat"
        assert result.output["result"] == "Hello-World-!"
        assert result.output["count"] == 3

    @pytest.mark.asyncio
    async def test_execute_with_template_resolution(self, registry, execution_context):
        """Test executing with pipeline input templates."""
        execution_context.pipeline_input = {
            "input_text": "The quick brown fox jumps over the lazy dog."
        }

        executor = UniversalExecutor(registry, execution_context)

        config = ComponentConfig(
            id="summarize_step",
            type="summarizer",
            input_mapping={
                "text": "{{input.input_text}}",
                "max_length": 15
            }
        )

        result = await executor.execute_component(config)

        assert result.status == "success"
        assert "The quick brown" in result.output["summary"]


# ============================================================================
# Test: Multi-Stage DAG Execution
# ============================================================================

class TestDAGExecution:
    """Tests for multi-stage pipeline execution."""

    @pytest.mark.asyncio
    async def test_two_stage_pipeline(self, registry, execution_context):
        """Test a simple two-stage pipeline."""
        execution_context.pipeline_input = {
            "text": "This is a great product! I love it!"
        }

        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="summarize",
                type="summarizer",
                input_mapping={
                    "text": "{{input.text}}",
                    "max_length": 50
                },
                depends_on=[]
            ),
            ComponentConfig(
                id="analyze",
                type="sentiment_analyzer",
                input_mapping={
                    "text": "{{upstream.summarize.summary}}"
                },
                depends_on=["summarize"]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        assert "summarize" in results
        assert "analyze" in results
        assert results["summarize"].status == "success"
        assert results["analyze"].status == "success"
        assert results["analyze"].output["sentiment"] == "positive"

    @pytest.mark.asyncio
    async def test_parallel_then_merge(self, registry, execution_context):
        """Test parallel execution followed by merge."""
        execution_context.pipeline_input = {
            "text1": "First text",
            "text2": "Second text"
        }

        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            # Two parallel summarizers
            ComponentConfig(
                id="summarize1",
                type="summarizer",
                input_mapping={
                    "text": "{{input.text1}}",
                    "max_length": 20
                },
                depends_on=[]
            ),
            ComponentConfig(
                id="summarize2",
                type="summarizer",
                input_mapping={
                    "text": "{{input.text2}}",
                    "max_length": 20
                },
                depends_on=[]
            ),
            # Merge results
            ComponentConfig(
                id="merge",
                type="text_concat",
                input_mapping={
                    "texts": [
                        "{{upstream.summarize1.summary}}",
                        "{{upstream.summarize2.summary}}"
                    ],
                    "separator": "-SEP-"
                },
                depends_on=["summarize1", "summarize2"]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        assert results["merge"].status == "success"
        assert "-SEP-" in results["merge"].output["result"]
        assert results["merge"].output["count"] == 2

    @pytest.mark.asyncio
    async def test_three_stage_chain(self, registry, execution_context):
        """Test a three-stage linear chain."""
        execution_context.pipeline_input = {
            "original": "This is excellent work! Amazing results."
        }

        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="step1_summarize",
                type="summarizer",
                input_mapping={
                    "text": "{{input.original}}",
                    "max_length": 30
                },
                depends_on=[]
            ),
            ComponentConfig(
                id="step2_sentiment",
                type="sentiment_analyzer",
                input_mapping={
                    "text": "{{upstream.step1_summarize.summary}}"
                },
                depends_on=["step1_summarize"]
            ),
            ComponentConfig(
                id="step3_report",
                type="text_concat",
                input_mapping={
                    "texts": [
                        "Summary: {{upstream.step1_summarize.summary}}",
                        "Sentiment: {{upstream.step2_sentiment.sentiment}}"
                    ],
                    "separator": " --- "
                },
                depends_on=["step1_summarize", "step2_sentiment"]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        assert all(r.status == "success" for r in results.values())
        assert "Summary:" in results["step3_report"].output["result"]
        assert "Sentiment:" in results["step3_report"].output["result"]

    @pytest.mark.asyncio
    async def test_usage_aggregation(self, registry, execution_context):
        """Test that usage metrics are aggregated across stages."""
        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="s1",
                type="summarizer",
                input_mapping={"text": "Test 1"},
                depends_on=[]
            ),
            ComponentConfig(
                id="s2",
                type="summarizer",
                input_mapping={"text": "Test 2"},
                depends_on=[]
            )
        ]

        results = await dag_executor.execute(stages, {})
        total_usage = dag_executor.aggregate_usage(results)

        assert isinstance(total_usage, UsageMetrics)
        # Duration is tracked per stage, may be 0 for fast ops
        assert total_usage.duration_ms >= 0


# ============================================================================
# Test: Mixed Node/Operator Pipelines
# ============================================================================

class TestMixedPipelines:
    """Tests pipelines that mix nodes and operators."""

    @pytest.mark.asyncio
    async def test_node_then_operator(self, registry, execution_context):
        """Test node followed by operator."""
        execution_context.pipeline_input = {"text": "Sample text"}

        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="node_stage",
                type="summarizer",
                input_mapping={"text": "{{input.text}}"},
                depends_on=[]
            ),
            ComponentConfig(
                id="operator_stage",
                type="conditional_filter",
                input_mapping={
                    "data": "{{upstream.node_stage.summary}}",
                    "condition": "pass"
                },
                depends_on=["node_stage"]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        assert results["node_stage"].status == "success"
        assert results["operator_stage"].status == "success"
        assert results["operator_stage"].output["passed"] is True

    @pytest.mark.asyncio
    async def test_operator_then_node(self, registry, execution_context):
        """Test operator followed by node."""
        execution_context.pipeline_input = {
            "part1": "Great",
            "part2": "product"
        }

        dag_executor = DAGExecutor(registry, execution_context)

        stages = [
            ComponentConfig(
                id="concat_stage",
                type="text_concat",
                input_mapping={
                    "texts": ["{{input.part1}}", "{{input.part2}}"],
                    "separator": " "
                },
                depends_on=[]
            ),
            ComponentConfig(
                id="sentiment_stage",
                type="sentiment_analyzer",
                input_mapping={
                    "text": "{{upstream.concat_stage.result}}"
                },
                depends_on=["concat_stage"]
            )
        ]

        results = await dag_executor.execute(stages, execution_context.pipeline_input)

        # The result should contain both parts (separator may be stripped/modified)
        assert "Great" in results["concat_stage"].output["result"]
        assert "product" in results["concat_stage"].output["result"]
        assert results["sentiment_stage"].output["sentiment"] == "positive"


# ============================================================================
# Test: Pipeline Configuration Structure
# ============================================================================

class TestPipelineConfiguration:
    """Tests for pipeline configuration structure."""

    def test_valid_pipeline_config(self, registry):
        """Test creating a valid pipeline configuration."""
        config = PipelineConfig(
            id="test-pipeline-001",
            name="test-pipeline",
            version="1.0.0",
            stages=[
                ComponentConfig(
                    id="stage1",
                    type="summarizer",
                    input_mapping={"text": "{{input.content}}"},
                    depends_on=[]
                )
            ],
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string"}
                },
                "required": ["content"]
            },
            output_stage_id="stage1"
        )

        assert config.name == "test-pipeline"
        assert len(config.stages) == 1
        assert config.stages[0].type == "summarizer"

    def test_multi_stage_pipeline_config(self, registry):
        """Test creating a multi-stage pipeline configuration."""
        config = PipelineConfig(
            id="multi-stage-001",
            name="multi-stage-pipeline",
            version="1.0.0",
            stages=[
                ComponentConfig(
                    id="stage1",
                    type="summarizer",
                    input_mapping={"text": "{{input.content}}"},
                    depends_on=[]
                ),
                ComponentConfig(
                    id="stage2",
                    type="sentiment_analyzer",
                    input_mapping={"text": "{{upstream.stage1.summary}}"},
                    depends_on=["stage1"]
                )
            ],
            input_schema={"type": "object"},
            output_stage_id="stage2"
        )

        assert len(config.stages) == 2
        assert config.stages[1].depends_on == ["stage1"]

    def test_pipeline_dependency_order(self, registry):
        """Test that dependencies are correctly specified."""
        config = PipelineConfig(
            id="dag-pipeline-001",
            name="dag-pipeline",
            version="1.0.0",
            stages=[
                ComponentConfig(id="a", type="summarizer", input_mapping={"text": "test"}, depends_on=[]),
                ComponentConfig(id="b", type="summarizer", input_mapping={"text": "test"}, depends_on=[]),
                ComponentConfig(id="c", type="text_concat", input_mapping={"texts": []}, depends_on=["a", "b"]),
            ],
            input_schema={"type": "object"},
            output_stage_id="c"
        )

        # Stage c should depend on both a and b
        stage_c = next(s for s in config.stages if s.id == "c")
        assert "a" in stage_c.depends_on
        assert "b" in stage_c.depends_on


# ============================================================================
# Test: Error Handling
# ============================================================================

class TestErrorHandling:
    """Tests for error handling in execution."""

    @pytest.mark.asyncio
    async def test_unknown_component_error(self, registry, execution_context):
        """Test error when component doesn't exist."""
        executor = UniversalExecutor(registry, execution_context)

        config = ComponentConfig(
            id="bad_stage",
            type="nonexistent_component",
            input_mapping={}
        )

        with pytest.raises(Exception) as exc_info:
            await executor.execute_component(config)

        assert "nonexistent_component" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_missing_required_input(self, registry, execution_context):
        """Test error when required input is missing."""
        executor = UniversalExecutor(registry, execution_context)

        config = ComponentConfig(
            id="missing_input_stage",
            type="summarizer",
            input_mapping={
                # Missing required "text" field
                "max_length": 100
            }
        )

        # Should raise an error due to missing required field
        with pytest.raises(Exception):
            await executor.execute_component(config)


# ============================================================================
# Test: Context Variables
# ============================================================================

class TestContextVariables:
    """Tests for context variable resolution."""

    @pytest.mark.asyncio
    async def test_context_run_id(self, registry, execution_context):
        """Test that context.run_id is accessible."""
        execution_context.run_id = "test_run_12345"

        executor = UniversalExecutor(registry, execution_context)

        config = ComponentConfig(
            id="test_stage",
            type="text_concat",
            input_mapping={
                "texts": ["Run ID:", "{{context.run_id}}"],
                "separator": " "
            }
        )

        result = await executor.execute_component(config)

        assert result.status == "success"
        assert "test_run_12345" in result.output["result"]
