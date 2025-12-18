"""
Shared test fixtures for FlowMason tests.
"""

import json
import zipfile
import tempfile
import pytest
from pathlib import Path

# Sample node source code
SAMPLE_NODE_SOURCE = '''
"""Sample Generator Node for testing."""

from flowmason_core.core.types import NodeInput, NodeOutput, Field
from flowmason_core.core.decorators import node


@node(
    name="test_generator",
    category="testing",
    description="A test generator node",
    icon="sparkles",
    color="#8B5CF6",
    version="1.0.0",
    author="FlowMason Test",
    tags=["test", "generator"],
    recommended_providers={
        "anthropic": {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.7,
        },
    },
    default_provider="anthropic",
)
class TestGeneratorNode:
    """A sample generator node for testing the registry."""

    class Input(NodeInput):
        prompt: str = Field(description="The prompt to generate from")
        max_tokens: int = Field(default=1000, ge=1, le=10000, description="Max tokens")

    class Output(NodeOutput):
        content: str
        tokens_used: int = 0

    async def execute(self, input: "TestGeneratorNode.Input", context) -> "TestGeneratorNode.Output":
        # Simulate generation
        return self.Output(
            content=f"Generated from: {input.prompt}",
            tokens_used=100
        )
'''

SAMPLE_OPERATOR_SOURCE = '''
"""Sample Transform Operator for testing."""

from typing import Any
from flowmason_core.core.types import OperatorInput, OperatorOutput, Field
from flowmason_core.core.decorators import operator


@operator(
    name="test_transform",
    category="testing",
    description="A test transform operator",
    icon="zap",
    color="#3B82F6",
    version="1.0.0",
    author="FlowMason Test",
    tags=["test", "transform"],
)
class TestTransformOperator:
    """A sample transform operator for testing the registry."""

    class Input(OperatorInput):
        data: Any = Field(description="Data to transform")
        uppercase: bool = Field(default=False, description="Convert to uppercase")

    class Output(OperatorOutput):
        result: Any
        transformed: bool = True

    async def execute(self, input: "TestTransformOperator.Input", context) -> "TestTransformOperator.Output":
        result = input.data
        if input.uppercase and isinstance(result, str):
            result = result.upper()
        return self.Output(result=result)
'''


def create_sample_manifest(
    name: str,
    version: str = "1.0.0",
    component_type: str = "node",
    entry_point: str = "index.py",
    **kwargs
) -> dict:
    """Create a sample package manifest."""
    return {
        "name": name,
        "version": version,
        "description": f"Test package: {name}",
        "type": component_type,
        "author": {
            "name": "Test Author",
            "email": "test@example.com"
        },
        "license": "MIT",
        "category": "testing",
        "tags": ["test"],
        "entry_point": entry_point,
        "requires_llm": component_type == "node",
        "dependencies": [],
        **kwargs
    }


def create_sample_package(
    output_dir: Path,
    name: str,
    version: str = "1.0.0",
    source_code: str = SAMPLE_NODE_SOURCE,
    component_type: str = "node",
) -> Path:
    """Create a sample .fmpkg package file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    pkg_path = output_dir / f"{name}-{version}.fmpkg"
    manifest = create_sample_manifest(name, version, component_type)

    with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add manifest
        zf.writestr("flowmason-package.json", json.dumps(manifest, indent=2))
        # Add source code
        zf.writestr("index.py", source_code)

    return pkg_path


@pytest.fixture
def temp_packages_dir(tmp_path):
    """Create a temporary packages directory."""
    packages_dir = tmp_path / "packages"
    packages_dir.mkdir()
    return packages_dir


@pytest.fixture
def sample_node_package(temp_packages_dir):
    """Create a sample node package."""
    return create_sample_package(
        temp_packages_dir,
        "test-generator",
        "1.0.0",
        SAMPLE_NODE_SOURCE,
        "node"
    )


@pytest.fixture
def sample_operator_package(temp_packages_dir):
    """Create a sample operator package."""
    return create_sample_package(
        temp_packages_dir,
        "test-transform",
        "1.0.0",
        SAMPLE_OPERATOR_SOURCE,
        "operator"
    )


@pytest.fixture
def multiple_packages(temp_packages_dir):
    """Create multiple sample packages."""
    node_pkg = create_sample_package(
        temp_packages_dir,
        "test-generator",
        "1.0.0",
        SAMPLE_NODE_SOURCE,
        "node"
    )
    operator_pkg = create_sample_package(
        temp_packages_dir,
        "test-transform",
        "1.0.0",
        SAMPLE_OPERATOR_SOURCE,
        "operator"
    )
    return [node_pkg, operator_pkg]
