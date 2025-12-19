"""
FlowMason Project Management.

This module provides support for FlowMason projects:
- flowmason.json project manifest
- .pipeline.json file format
- Project discovery and loading
"""

from flowmason_core.project.loader import (
    PipelineFile,
    ProjectLoader,
    discover_pipelines,
    load_pipeline_file,
)
from flowmason_core.project.manifest import (
    ComponentConfig,
    ProjectManifest,
    ProviderConfig,
    TestingConfig,
    find_manifest,
    load_manifest,
)

__all__ = [
    # Manifest
    "ProjectManifest",
    "ComponentConfig",
    "ProviderConfig",
    "TestingConfig",
    "load_manifest",
    "find_manifest",
    # Loader
    "PipelineFile",
    "ProjectLoader",
    "load_pipeline_file",
    "discover_pipelines",
]
