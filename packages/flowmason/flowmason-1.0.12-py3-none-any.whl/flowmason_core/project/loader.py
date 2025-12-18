"""
FlowMason Pipeline File Loader.

Loads .pipeline.json files for local file-based execution.
The file format mirrors the PipelineDetail model from Studio
but is optimized for file-based workflows.

Example .pipeline.json:
{
  "$schema": "https://flowmason.dev/schemas/pipeline.schema.json",
  "name": "content-pipeline",
  "version": "1.0.0",
  "description": "Fetch and summarize web content",
  "input_schema": {
    "type": "object",
    "properties": {
      "url": { "type": "string", "description": "URL to fetch" }
    },
    "required": ["url"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "summary": { "type": "string" }
    }
  },
  "stages": [
    {
      "id": "fetch",
      "component": "http-request",
      "config": { "url": "{{input.url}}", "method": "GET" }
    },
    {
      "id": "summarize",
      "component": "generator",
      "depends_on": ["fetch"],
      "config": {
        "prompt": "Summarize: {{fetch.output.body}}"
      },
      "llm_settings": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514"
      }
    }
  ],
  "output_stage_id": "summarize"
}
"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from flowmason_core.project.manifest import ProjectManifest


class LLMSettings(BaseModel):
    """LLM settings for a stage."""
    provider: Optional[str] = Field(default=None, description="Provider name")
    model: Optional[str] = Field(default=None, description="Model name")
    temperature: Optional[float] = Field(default=None, description="Temperature 0.0-2.0")
    max_tokens: Optional[int] = Field(default=None, description="Max response tokens")
    top_p: Optional[float] = Field(default=None, description="Nucleus sampling")
    stop_sequences: Optional[List[str]] = Field(default=None, description="Stop sequences")


class StagePosition(BaseModel):
    """Position of a stage in the canvas."""
    x: float = 0
    y: float = 0


class PipelineStage(BaseModel):
    """
    A single stage in a pipeline.

    Compatible with the Studio API model but adds 'component' as alias for 'component_type'.
    """
    id: str = Field(description="Unique stage identifier within pipeline")
    component_type: Optional[str] = Field(default=None, description="Component type to execute")
    component: Optional[str] = Field(default=None, description="Component type (alias)")
    name: Optional[str] = Field(default=None, description="Display name for the stage")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Static configuration values"
    )
    input_mapping: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mapping from config to component Input"
    )
    depends_on: List[str] = Field(
        default_factory=list,
        description="Stage IDs this stage depends on"
    )
    position: Optional[StagePosition] = Field(default=None, description="Canvas position")
    llm_settings: Optional[LLMSettings] = Field(default=None, description="LLM settings")
    timeout_ms: Optional[int] = Field(default=None, description="Stage timeout")

    def get_component_type(self) -> str:
        """Get the component type, supporting both 'component' and 'component_type' fields."""
        return self.component_type or self.component or ""


class PipelineInputSchema(BaseModel):
    """Schema definition for pipeline input."""
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class PipelineOutputSchema(BaseModel):
    """Schema definition for pipeline output."""
    type: str = "object"
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class CompositionStage(BaseModel):
    """Configuration for composing a sub-pipeline within a parent pipeline."""
    id: str = Field(description="Unique stage ID for this composition")
    pipeline: str = Field(description="Reference to pipeline (name or name@version)")
    input_mapping: Dict[str, Any] = Field(
        default_factory=dict,
        description="Map parent context to sub-pipeline inputs"
    )
    output_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Map sub-pipeline outputs to parent context"
    )
    depends_on: List[str] = Field(
        default_factory=list,
        description="Stage IDs this composition depends on"
    )


class PipelineFile(BaseModel):
    """
    Pipeline loaded from a .pipeline.json file.

    This model represents the file format for pipelines,
    compatible with but separate from the database model.
    """
    # File metadata
    file_path: Optional[str] = Field(default=None, description="Source file path")

    # Schema identifier (optional, for validation)
    schema_: Optional[str] = Field(default=None, alias="$schema")

    # Pipeline identity
    id: Optional[str] = Field(default=None, description="Pipeline unique identifier")
    name: str = Field(description="Pipeline display name")
    version: str = Field(default="1.0.0", description="Pipeline version")
    description: str = Field(default="", description="Pipeline description")

    # Inheritance (P5.1)
    extends: Optional[str] = Field(
        default=None,
        description="Parent pipeline reference (name or name@version)"
    )
    abstract: bool = Field(
        default=False,
        description="If true, pipeline cannot be executed directly"
    )
    overrides: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Override configurations for inherited stages"
    )
    compositions: List[CompositionStage] = Field(
        default_factory=list,
        description="Sub-pipelines to embed within this pipeline"
    )

    # Schema definitions
    input_schema: PipelineInputSchema = Field(default_factory=PipelineInputSchema)
    output_schema: PipelineOutputSchema = Field(default_factory=PipelineOutputSchema)

    # Pipeline structure
    stages: List[PipelineStage] = Field(default_factory=list)
    output_stage_id: Optional[str] = Field(
        default=None,
        description="ID of stage that produces final output"
    )

    # Metadata
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Sample data for testing
    sample_input: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Sample input data for testing"
    )

    class Config:
        populate_by_name = True

    def to_json(self, indent: int = 2) -> str:
        """Serialize pipeline to JSON string."""
        data = self.model_dump(exclude_none=True, by_alias=True)
        # Remove internal fields
        data.pop("file_path", None)
        return json.dumps(data, indent=indent)

    @classmethod
    def from_json(cls, json_str: str, file_path: Optional[str] = None) -> "PipelineFile":
        """Parse pipeline from JSON string."""
        data = json.loads(json_str)
        if file_path:
            data["file_path"] = str(file_path)
        return cls(**data)

    def get_stage(self, stage_id: str) -> Optional[PipelineStage]:
        """Get a stage by ID."""
        for stage in self.stages:
            if stage.id == stage_id:
                return stage
        return None

    def get_execution_order(self) -> List[str]:
        """
        Get stages in topological execution order.

        Returns stage IDs ordered such that dependencies come before dependents.
        """
        # Build dependency graph
        deps: Dict[str, List[str]] = {}
        for stage in self.stages:
            deps[stage.id] = stage.depends_on.copy()

        # Kahn's algorithm for topological sort
        order: List[str] = []
        ready = [sid for sid, d in deps.items() if not d]

        while ready:
            stage_id = ready.pop(0)
            order.append(stage_id)

            for sid, d in deps.items():
                if stage_id in d:
                    d.remove(stage_id)
                    if not d and sid not in order and sid not in ready:
                        ready.append(sid)

        return order


def load_pipeline_file(path: Union[str, Path]) -> PipelineFile:
    """
    Load a pipeline from a .pipeline.json file.

    Args:
        path: Path to .pipeline.json file

    Returns:
        Parsed PipelineFile

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
        ValidationError: If JSON doesn't match schema
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Pipeline file not found: {path}")

    content = path.read_text()
    return PipelineFile.from_json(content, file_path=str(path))


def discover_pipelines(
    directory: Union[str, Path],
    pattern: str = "**/*.pipeline.json",
    recursive: bool = True,
) -> List[Path]:
    """
    Discover pipeline files in a directory.

    Args:
        directory: Directory to search
        pattern: Glob pattern to match pipeline files
        recursive: Whether to search recursively

    Returns:
        List of paths to pipeline files
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []

    if recursive:
        return list(directory.glob(pattern))
    else:
        return list(directory.glob(pattern.replace("**/", "")))


class ProjectLoader:
    """
    Loads a FlowMason project including manifest and pipelines.

    Usage:
        loader = ProjectLoader("/path/to/project")
        manifest = loader.manifest
        pipelines = loader.load_all_pipelines()
    """

    def __init__(self, project_path: Union[str, Path]):
        """
        Initialize project loader.

        Args:
            project_path: Path to project directory (containing flowmason.json)
        """
        self.project_path = Path(project_path).resolve()
        self._manifest: Optional["ProjectManifest"] = None

    @property
    def manifest(self) -> Optional["ProjectManifest"]:
        """Get the project manifest, loading if necessary."""
        if self._manifest is None:
            manifest_path = self.project_path / "flowmason.json"
            if manifest_path.exists():
                from flowmason_core.project.manifest import load_manifest
                self._manifest = load_manifest(manifest_path)
        return self._manifest

    @property
    def has_manifest(self) -> bool:
        """Check if project has a flowmason.json."""
        return (self.project_path / "flowmason.json").exists()

    def get_pipeline_dirs(self) -> List[Path]:
        """Get directories to search for pipelines."""
        if self.manifest:
            return [self.project_path / d for d in self.manifest.pipeline_dirs]
        # Default fallback
        return [self.project_path / "pipelines"]

    def discover_pipelines(self) -> List[Path]:
        """
        Find all pipeline files in the project.

        Returns:
            List of paths to .pipeline.json files
        """
        pipelines: List[Path] = []

        for pipeline_dir in self.get_pipeline_dirs():
            if pipeline_dir.is_dir():
                pipelines.extend(discover_pipelines(pipeline_dir))

        # Also check project root
        pipelines.extend(discover_pipelines(self.project_path, recursive=False))

        return sorted(set(pipelines))

    def load_pipeline(self, name_or_path: str) -> PipelineFile:
        """
        Load a specific pipeline by name or path.

        Args:
            name_or_path: Pipeline name (without .pipeline.json) or full path

        Returns:
            Loaded PipelineFile

        Raises:
            FileNotFoundError: If pipeline not found
        """
        # Check if it's a path
        path = Path(name_or_path)
        if path.exists():
            return load_pipeline_file(path)

        # Check if it's relative to project
        relative_path = self.project_path / name_or_path
        if relative_path.exists():
            return load_pipeline_file(relative_path)

        # Try adding .pipeline.json extension
        if not name_or_path.endswith(".pipeline.json"):
            name_or_path = f"{name_or_path}.pipeline.json"

        # Search in pipeline directories
        for pipeline_dir in self.get_pipeline_dirs():
            candidate = pipeline_dir / name_or_path
            if candidate.exists():
                return load_pipeline_file(candidate)

        raise FileNotFoundError(f"Pipeline not found: {name_or_path}")

    def load_all_pipelines(self) -> Dict[str, PipelineFile]:
        """
        Load all pipelines in the project.

        Returns:
            Dict mapping pipeline names to PipelineFile objects
        """
        pipelines: Dict[str, PipelineFile] = {}

        for path in self.discover_pipelines():
            try:
                pipeline = load_pipeline_file(path)
                pipelines[pipeline.name] = pipeline
            except Exception as e:
                # Log but don't fail on individual pipeline errors
                print(f"Warning: Failed to load {path}: {e}")

        return pipelines

    def get_main_pipeline(self) -> Optional[PipelineFile]:
        """
        Get the main pipeline defined in the manifest.

        Returns:
            Main PipelineFile or None if not defined
        """
        if self.manifest and self.manifest.main:
            try:
                return self.load_pipeline(self.manifest.main)
            except FileNotFoundError:
                return None
        return None


def create_pipeline_file(
    name: str,
    description: str = "",
    stages: Optional[List[Dict[str, Any]]] = None,
) -> PipelineFile:
    """
    Create a new pipeline file structure.

    Args:
        name: Pipeline name
        description: Pipeline description
        stages: Optional list of stage configurations

    Returns:
        New PipelineFile object
    """
    return PipelineFile(
        name=name,
        version="1.0.0",
        description=description,
        input_schema=PipelineInputSchema(),
        output_schema=PipelineOutputSchema(),
        stages=[PipelineStage(**s) for s in (stages or [])],
    )
