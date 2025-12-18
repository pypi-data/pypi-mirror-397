"""
FlowMason Package Builder.

Builds .fmpkg packages from FlowMason projects.

Package structure:
my-workflow-1.0.0.fmpkg (ZIP)
├── manifest.json
├── pipelines/
│   └── main.pipeline.json
├── components/
│   ├── nodes/
│   └── operators/
├── prompts/
│   └── templates/
└── config/
    └── default.env
"""

import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from flowmason_core.packaging.manifest import PackageManifest


class PackageBuilder:
    """
    Builds .fmpkg packages from FlowMason projects.

    Usage:
        builder = PackageBuilder("/path/to/project")
        builder.build("output/my-package-1.0.0.fmpkg")
    """

    def __init__(self, project_path: Union[str, Path]):
        """
        Initialize package builder.

        Args:
            project_path: Path to project directory (containing flowmason.json)
        """
        self.project_path = Path(project_path).resolve()
        self._manifest: Optional[PackageManifest] = None

    @property
    def manifest(self) -> Optional[PackageManifest]:
        """Get or create the package manifest."""
        if self._manifest is None:
            # Try to load from project manifest
            project_manifest = self.project_path / "flowmason.json"
            if project_manifest.exists():
                from flowmason_core.project.manifest import load_manifest
                proj = load_manifest(project_manifest)
                self._manifest = PackageManifest(
                    name=proj.name,
                    version=proj.version,
                    description=proj.description,
                    author=proj.author,
                    entry=proj.main,
                )
        return self._manifest

    def set_manifest(self, manifest: PackageManifest):
        """Set a custom manifest."""
        self._manifest = manifest

    def discover_files(self) -> dict:
        """
        Discover files to include in the package.

        Returns:
            Dict with 'pipelines', 'components', 'prompts', 'config' lists
        """
        files: Dict[str, List[Path]] = {
            "pipelines": [],
            "components": [],
            "prompts": [],
            "config": [],
        }

        # Discover pipelines
        pipelines_dir = self.project_path / "pipelines"
        if pipelines_dir.is_dir():
            for f in pipelines_dir.glob("**/*.pipeline.json"):
                files["pipelines"].append(f.relative_to(self.project_path))

        # Discover components
        components_dir = self.project_path / "components"
        if components_dir.is_dir():
            for f in components_dir.glob("**/*.py"):
                if not f.name.startswith("_"):
                    files["components"].append(f.relative_to(self.project_path))

        # Discover prompts
        prompts_dir = self.project_path / "prompts"
        if prompts_dir.is_dir():
            for f in prompts_dir.glob("**/*"):
                if f.is_file():
                    files["prompts"].append(f.relative_to(self.project_path))

        # Discover config
        config_dir = self.project_path / "config"
        if config_dir.is_dir():
            for f in config_dir.glob("**/*"):
                if f.is_file() and not f.name.startswith("."):
                    files["config"].append(f.relative_to(self.project_path))

        return files

    def build(
        self,
        output_path: Optional[Union[str, Path]] = None,
        version: Optional[str] = None,
    ) -> Path:
        """
        Build a .fmpkg package.

        Args:
            output_path: Output file path (default: packages/<name>-<version>.fmpkg)
            version: Override version (default: from manifest)

        Returns:
            Path to the created package file
        """
        # Ensure we have a manifest
        manifest = self.manifest
        if manifest is None:
            raise ValueError("No manifest available. Create flowmason.json or set manifest manually.")

        # Override version if provided
        if version:
            manifest = PackageManifest(**{**manifest.model_dump(), "version": version})

        # Discover files
        files = self.discover_files()

        # Update manifest with discovered files
        manifest = PackageManifest(**{
            **manifest.model_dump(),
            "pipelines": [str(f) for f in files["pipelines"]],
            "components": [str(f) for f in files["components"]],
            "built_at": datetime.utcnow().isoformat(),
            "built_by": "flowmason-cli",
        })

        # Determine output path
        if output_path is None:
            packages_dir = self.project_path / "packages"
            packages_dir.mkdir(parents=True, exist_ok=True)
            output_path = packages_dir / f"{manifest.name}-{manifest.version}.fmpkg"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build the ZIP file
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Write manifest
            zf.writestr("manifest.json", manifest.to_json())

            # Write all discovered files
            all_files = (
                files["pipelines"] +
                files["components"] +
                files["prompts"] +
                files["config"]
            )
            for rel_path in all_files:
                abs_path = self.project_path / rel_path
                if abs_path.exists():
                    zf.write(abs_path, str(rel_path))

        return output_path


def build_package(
    project_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    version: Optional[str] = None,
) -> Path:
    """
    Build a .fmpkg package from a project.

    Args:
        project_path: Path to project directory
        output_path: Output file path (optional)
        version: Override version (optional)

    Returns:
        Path to the created package file
    """
    builder = PackageBuilder(project_path)
    return builder.build(output_path=output_path, version=version)
