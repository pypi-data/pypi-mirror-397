"""
FlowMason Package Manifest (manifest.json).

Defines the schema for .fmpkg package manifests.

Example manifest.json:
{
  "name": "my-workflow",
  "version": "1.0.0",
  "description": "Content processing pipeline",
  "author": "team@company.com",
  "license": "MIT",
  "flowmason": ">=0.1.0",
  "entry": "pipelines/main.pipeline.json",
  "exports": ["pipelines/main.pipeline.json"],
  "dependencies": {
    "flowmason-http": "^1.0.0"
  }
}
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class PackageDependency(BaseModel):
    """A package dependency."""
    name: str = Field(description="Package name")
    version: str = Field(description="Version constraint (semver)")


class PackageManifest(BaseModel):
    """
    FlowMason package manifest (manifest.json).

    Defines metadata and contents of a .fmpkg package.
    """
    # Required fields
    name: str = Field(description="Package name (lowercase, hyphens allowed)")
    version: str = Field(description="Package version (semver)")

    # Optional metadata
    description: str = Field(default="", description="Package description")
    author: Optional[str] = Field(default=None, description="Package author")
    license: Optional[str] = Field(default=None, description="License (SPDX identifier)")
    repository: Optional[str] = Field(default=None, description="Repository URL")
    homepage: Optional[str] = Field(default=None, description="Homepage URL")
    keywords: List[str] = Field(default_factory=list, description="Search keywords")

    # FlowMason version compatibility
    flowmason: str = Field(default=">=0.1.0", description="FlowMason version constraint")

    # Entry points
    entry: Optional[str] = Field(
        default=None,
        description="Main entry point (pipeline or component)"
    )
    exports: List[str] = Field(
        default_factory=list,
        description="Exported files (pipelines, components)"
    )

    # Dependencies
    dependencies: Dict[str, str] = Field(
        default_factory=dict,
        description="Package dependencies (name -> version)"
    )

    # Build metadata
    built_at: Optional[str] = Field(default=None, description="Build timestamp")
    built_by: Optional[str] = Field(default=None, description="Build tool version")

    # Contents summary (generated during build)
    pipelines: List[str] = Field(
        default_factory=list,
        description="List of pipeline files in package"
    )
    components: List[str] = Field(
        default_factory=list,
        description="List of component files in package"
    )

    def to_json(self, indent: int = 2) -> str:
        """Serialize manifest to JSON string."""
        return self.model_dump_json(indent=indent, exclude_none=True)

    @classmethod
    def from_json(cls, json_str: str) -> "PackageManifest":
        """Parse manifest from JSON string."""
        data = json.loads(json_str)
        return cls(**data)

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "PackageManifest":
        """Load manifest from file."""
        path = Path(path)
        content = path.read_text()
        return cls.from_json(content)


def create_manifest(
    name: str,
    version: str,
    description: str = "",
    author: Optional[str] = None,
    entry: Optional[str] = None,
) -> PackageManifest:
    """
    Create a new package manifest.

    Args:
        name: Package name
        version: Package version
        description: Package description
        author: Package author
        entry: Main entry point

    Returns:
        New PackageManifest
    """
    return PackageManifest(
        name=name,
        version=version,
        description=description,
        author=author,
        entry=entry,
    )
