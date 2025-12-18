"""
Package Loader

Handles extraction and loading of .fmpkg packages.
"""

import importlib
import importlib.util
import json
import logging
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from flowmason_core.registry.types import (
    PackageInfo,
    PackageLoadError,
)

logger = logging.getLogger(__name__)


class PackageLoader:
    """
    Loads FlowMason packages (.fmpkg files).

    Handles:
    - Extracting packages to temp/install directories
    - Reading and validating manifests
    - Dynamically importing component classes
    - Managing Python path for loaded packages
    """

    MANIFEST_FILENAME = "flowmason-package.json"

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the package loader.

        Args:
            cache_dir: Directory for extracted packages. If None, uses temp directory.
        """
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "flowmason_packages"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Track loaded modules for cleanup
        self._loaded_modules: Dict[str, str] = {}  # module_name -> path

    def extract_package(self, fmpkg_path: str | Path) -> Tuple[Path, Dict[str, Any]]:
        """
        Extract a .fmpkg file and return the extraction path and manifest.

        Args:
            fmpkg_path: Path to the .fmpkg file

        Returns:
            Tuple of (extraction_path, manifest_dict)

        Raises:
            PackageLoadError: If extraction or manifest parsing fails
        """
        fmpkg_path = Path(fmpkg_path)

        if not fmpkg_path.exists():
            raise PackageLoadError(str(fmpkg_path), "Package file not found")

        if not fmpkg_path.suffix == ".fmpkg":
            raise PackageLoadError(str(fmpkg_path), "Not a .fmpkg file")

        try:
            with zipfile.ZipFile(fmpkg_path, "r") as zf:
                # Check for manifest
                if self.MANIFEST_FILENAME not in zf.namelist():
                    raise PackageLoadError(
                        str(fmpkg_path),
                        f"Missing {self.MANIFEST_FILENAME}"
                    )

                # Read manifest
                manifest_json = zf.read(self.MANIFEST_FILENAME).decode("utf-8")
                manifest = json.loads(manifest_json)

                # Create extraction directory
                pkg_name = manifest.get("name", fmpkg_path.stem)
                pkg_version = manifest.get("version", "unknown")
                extract_dir = self.cache_dir / pkg_name / pkg_version

                # Clean existing extraction if present
                if extract_dir.exists():
                    shutil.rmtree(extract_dir)

                extract_dir.mkdir(parents=True, exist_ok=True)

                # Extract all files
                zf.extractall(extract_dir)

                logger.info(f"Extracted package {pkg_name}@{pkg_version} to {extract_dir}")

                return extract_dir, manifest

        except zipfile.BadZipFile as e:
            raise PackageLoadError(str(fmpkg_path), f"Invalid zip file: {e}")
        except json.JSONDecodeError as e:
            raise PackageLoadError(str(fmpkg_path), f"Invalid manifest JSON: {e}")
        except Exception as e:
            raise PackageLoadError(str(fmpkg_path), str(e))

    def read_manifest(self, fmpkg_path: str | Path) -> Dict[str, Any]:
        """
        Read the manifest from a .fmpkg file without extracting.

        Args:
            fmpkg_path: Path to the .fmpkg file

        Returns:
            Manifest dictionary

        Raises:
            PackageLoadError: If manifest cannot be read
        """
        fmpkg_path = Path(fmpkg_path)

        if not fmpkg_path.exists():
            raise PackageLoadError(str(fmpkg_path), "Package file not found")

        try:
            with zipfile.ZipFile(fmpkg_path, "r") as zf:
                if self.MANIFEST_FILENAME not in zf.namelist():
                    raise PackageLoadError(
                        str(fmpkg_path),
                        f"Missing {self.MANIFEST_FILENAME}"
                    )

                manifest_json = zf.read(self.MANIFEST_FILENAME).decode("utf-8")
                result = json.loads(manifest_json)
                return dict(result) if isinstance(result, dict) else {}

        except zipfile.BadZipFile as e:
            raise PackageLoadError(str(fmpkg_path), f"Invalid zip file: {e}")
        except json.JSONDecodeError as e:
            raise PackageLoadError(str(fmpkg_path), f"Invalid manifest JSON: {e}")

    def load_component_class(
        self,
        package_path: str | Path,
        entry_point: str,
        class_name: Optional[str] = None,
    ) -> Type:
        """
        Dynamically import and return a component class from a package.

        Args:
            package_path: Path to extracted package directory
            entry_point: Entry point file (e.g., "index.py", "generator.py")
            class_name: Optional specific class name to load.
                       If None, finds the first FlowMason component class.

        Returns:
            The component class

        Raises:
            PackageLoadError: If the class cannot be loaded
        """
        package_path = Path(package_path)
        entry_file = package_path / entry_point

        if not entry_file.exists():
            raise PackageLoadError(
                str(package_path),
                f"Entry point '{entry_point}' not found"
            )

        try:
            # Generate unique module name including parent directory (package name)
            # e.g., flowmason_pkg_critic_1.0.0_index
            pkg_name = package_path.parent.name if package_path.parent != self.cache_dir else "unknown"
            module_name = f"flowmason_pkg_{pkg_name}_{package_path.name}_{entry_point.replace('.py', '')}"

            # CRITICAL: Remove old module from sys.modules to force reload
            # This ensures we always use the freshly extracted code
            if module_name in sys.modules:
                logger.debug(f"Removing cached module {module_name} to force reload")
                del sys.modules[module_name]

            # Add package path to sys.path if not already there
            pkg_str = str(package_path)
            if pkg_str not in sys.path:
                sys.path.insert(0, pkg_str)

            # Load the module fresh
            spec = importlib.util.spec_from_file_location(module_name, entry_file)
            if spec is None or spec.loader is None:
                raise PackageLoadError(
                    str(package_path),
                    f"Could not create module spec for {entry_point}"
                )

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Track loaded module
            self._loaded_modules[module_name] = str(entry_file)

            # Find component class
            if class_name:
                # Load specific class
                if not hasattr(module, class_name):
                    raise PackageLoadError(
                        str(package_path),
                        f"Class '{class_name}' not found in {entry_point}"
                    )
                component_class = getattr(module, class_name)
            else:
                # Find first FlowMason component class
                component_class = self._find_component_class(module)
                if component_class is None:
                    raise PackageLoadError(
                        str(package_path),
                        f"No FlowMason component found in {entry_point}"
                    )

            # Validate it's a FlowMason component
            if not hasattr(component_class, "_flowmason_metadata"):
                raise PackageLoadError(
                    str(package_path),
                    f"Class '{component_class.__name__}' is not a FlowMason component"
                )

            logger.debug(f"Loaded component class: {component_class.__name__}")
            return component_class  # type: ignore[no-any-return]

        except PackageLoadError:
            raise
        except Exception as e:
            raise PackageLoadError(str(package_path), f"Failed to load module: {e}")

    def _find_component_class(self, module) -> Optional[Type]:
        """
        Find the first FlowMason component class in a module.

        Args:
            module: The loaded Python module

        Returns:
            The component class, or None if not found
        """
        import inspect

        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Check if it's a FlowMason component (has our metadata)
            if hasattr(obj, "_flowmason_metadata") and hasattr(obj, "_flowmason_type"):
                # Make sure it's defined in this module (not imported)
                if obj.__module__ == module.__name__:
                    return obj

        return None

    def find_all_component_classes(self, module) -> List[Type]:
        """
        Find all FlowMason component classes in a module.

        Args:
            module: The loaded Python module

        Returns:
            List of component classes
        """
        import inspect

        components = []

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, "_flowmason_metadata") and hasattr(obj, "_flowmason_type"):
                if obj.__module__ == module.__name__:
                    components.append(obj)

        return components

    def unload_package(self, package_path: str | Path) -> None:
        """
        Unload a package and clean up its resources.

        Args:
            package_path: Path to the extracted package directory
        """
        package_path = Path(package_path)

        # Remove from sys.path
        pkg_str = str(package_path)
        if pkg_str in sys.path:
            sys.path.remove(pkg_str)

        # Remove loaded modules
        to_remove = []
        for module_name, module_path in self._loaded_modules.items():
            if module_path.startswith(pkg_str):
                to_remove.append(module_name)

        for module_name in to_remove:
            if module_name in sys.modules:
                del sys.modules[module_name]
            del self._loaded_modules[module_name]

        # Optionally clean up extracted files
        if package_path.exists() and str(package_path).startswith(str(self.cache_dir)):
            try:
                shutil.rmtree(package_path)
                logger.debug(f"Cleaned up package directory: {package_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {package_path}: {e}")

    def get_package_info(self, manifest: Dict[str, Any], package_path: str) -> PackageInfo:
        """
        Create PackageInfo from manifest.

        Args:
            manifest: The package manifest dictionary
            package_path: Path to the .fmpkg file

        Returns:
            PackageInfo instance
        """
        author_info = manifest.get("author", {})
        if isinstance(author_info, dict):
            author_name = author_info.get("name")
            author_email = author_info.get("email")
        else:
            author_name = str(author_info) if author_info else None
            author_email = None

        return PackageInfo(
            name=manifest.get("name", "unknown"),
            version=manifest.get("version", "0.0.0"),
            description=manifest.get("description", ""),
            author=author_name,
            author_email=author_email,
            package_path=package_path,
            dependencies=[
                d.get("name", d) if isinstance(d, dict) else d
                for d in manifest.get("dependencies", [])
            ],
            is_core=manifest.get("is_core", False),
            metadata=manifest,
        )

    def cleanup(self) -> None:
        """Clean up all loaded packages and temporary files."""
        # Remove all loaded modules
        for module_name in list(self._loaded_modules.keys()):
            if module_name in sys.modules:
                del sys.modules[module_name]
        self._loaded_modules.clear()

        # Clean up cache directory
        if self.cache_dir.exists():
            try:
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Failed to clean up cache directory: {e}")
