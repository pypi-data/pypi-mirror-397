"""
FlowMason Project Manifest (flowmason.json).

Defines the schema for FlowMason projects, similar to package.json for Node.js
or pyproject.toml for Python.

Example flowmason.json:
{
  "name": "my-flowmason-project",
  "version": "1.0.0",
  "description": "My AI pipeline project",
  "main": "pipelines/main.pipeline.json",
  "components": {
    "include": ["components/**/*.py"]
  },
  "providers": {
    "default": "anthropic",
    "anthropic": { "model": "claude-sonnet-4-20250514" }
  },
  "testing": {
    "timeout": 30000,
    "retries": 2
  }
}
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ComponentConfig(BaseModel):
    """Configuration for component discovery."""
    include: List[str] = Field(
        default_factory=lambda: ["components/**/*.py"],
        description="Glob patterns to include components from"
    )
    exclude: List[str] = Field(
        default_factory=list,
        description="Glob patterns to exclude from component discovery"
    )


class ProviderSettings(BaseModel):
    """Settings for a specific LLM provider."""
    model: Optional[str] = Field(default=None, description="Default model for this provider")
    api_key_env: Optional[str] = Field(default=None, description="Environment variable for API key")
    base_url: Optional[str] = Field(default=None, description="Base URL override")
    temperature: Optional[float] = Field(default=None, description="Default temperature")
    max_tokens: Optional[int] = Field(default=None, description="Default max tokens")
    extra: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional provider-specific settings"
    )


class ProviderConfig(BaseModel):
    """Configuration for LLM providers."""
    default: str = Field(default="anthropic", description="Default provider name")
    anthropic: Optional[ProviderSettings] = Field(default=None)
    openai: Optional[ProviderSettings] = Field(default=None)
    azure: Optional[ProviderSettings] = Field(default=None)
    # Additional providers can be added as extra fields
    extra: Dict[str, ProviderSettings] = Field(default_factory=dict)

    def get_provider(self, name: str) -> Optional[ProviderSettings]:
        """Get settings for a specific provider."""
        if name == "anthropic":
            return self.anthropic
        elif name == "openai":
            return self.openai
        elif name == "azure":
            return self.azure
        return self.extra.get(name)


class TestingConfig(BaseModel):
    """Configuration for testing."""
    timeout: int = Field(default=30000, description="Default test timeout in ms")
    retries: int = Field(default=2, description="Number of retries for flaky tests")
    parallel: bool = Field(default=False, description="Run tests in parallel")
    coverage: bool = Field(default=True, description="Collect coverage data")
    test_patterns: List[str] = Field(
        default_factory=lambda: ["**/*.test.json"],
        description="Glob patterns for test files"
    )


class OrgConfig(BaseModel):
    """Configuration for org deployments."""
    default: Optional[str] = Field(default=None, description="Default org alias")


class ProjectManifest(BaseModel):
    """
    FlowMason project manifest (flowmason.json).

    This is the root configuration file for a FlowMason project,
    similar to package.json or pyproject.toml.
    """
    # Required fields
    name: str = Field(description="Project name")
    version: str = Field(default="1.0.0", description="Project version (semver)")

    # Optional metadata
    description: str = Field(default="", description="Project description")
    author: Optional[str] = Field(default=None, description="Project author")
    license: Optional[str] = Field(default=None, description="Project license")
    repository: Optional[str] = Field(default=None, description="Repository URL")

    # Entry points
    main: Optional[str] = Field(
        default=None,
        description="Main pipeline file (e.g., 'pipelines/main.pipeline.json')"
    )

    # Configuration
    components: ComponentConfig = Field(
        default_factory=ComponentConfig,
        description="Component discovery configuration"
    )
    providers: ProviderConfig = Field(
        default_factory=ProviderConfig,
        description="LLM provider configuration"
    )
    testing: TestingConfig = Field(
        default_factory=TestingConfig,
        description="Testing configuration"
    )
    org: OrgConfig = Field(
        default_factory=OrgConfig,
        description="Org deployment configuration"
    )

    # Pipeline directories
    pipeline_dirs: List[str] = Field(
        default_factory=lambda: ["pipelines"],
        description="Directories to search for .pipeline.json files"
    )

    # Extra configuration
    extra: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional project-specific configuration"
    )

    def to_json(self, indent: int = 2) -> str:
        """Serialize manifest to JSON string."""
        return self.model_dump_json(indent=indent, exclude_none=True)

    @classmethod
    def from_json(cls, json_str: str) -> "ProjectManifest":
        """Parse manifest from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


def load_manifest(path: Union[str, Path]) -> ProjectManifest:
    """
    Load a project manifest from a flowmason.json file.

    Args:
        path: Path to flowmason.json file

    Returns:
        Parsed ProjectManifest

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
        ValidationError: If JSON doesn't match schema
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    content = path.read_text()
    return ProjectManifest.from_json(content)


def find_manifest(start_path: Union[str, Path] = ".") -> Optional[Path]:
    """
    Find flowmason.json by searching up from start_path.

    Args:
        start_path: Directory to start searching from (default: current dir)

    Returns:
        Path to flowmason.json if found, None otherwise
    """
    current = Path(start_path).resolve()

    while current != current.parent:
        manifest_path = current / "flowmason.json"
        if manifest_path.exists():
            return manifest_path
        current = current.parent

    # Check root as well
    manifest_path = current / "flowmason.json"
    if manifest_path.exists():
        return manifest_path

    return None


def create_default_manifest(
    name: str,
    version: str = "1.0.0",
    description: str = "",
) -> ProjectManifest:
    """
    Create a default project manifest.

    Args:
        name: Project name
        version: Project version
        description: Project description

    Returns:
        New ProjectManifest with default settings
    """
    return ProjectManifest(
        name=name,
        version=version,
        description=description,
        main="pipelines/main.pipeline.json",
        components=ComponentConfig(),
        providers=ProviderConfig(
            default="anthropic",
            anthropic=ProviderSettings(model="claude-sonnet-4-20250514"),
        ),
        testing=TestingConfig(),
    )
