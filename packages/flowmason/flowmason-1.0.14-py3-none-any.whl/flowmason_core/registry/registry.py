"""
Universal Component Registry

The central registry for all FlowMason components.
Handles dynamic loading, caching, and lookup of components from packages.

CRITICAL: No hardcoded component types. Everything loads dynamically from packages.
"""

import logging
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional, Type

from flowmason_core.registry.extractor import MetadataExtractor
from flowmason_core.registry.loader import PackageLoader
from flowmason_core.registry.types import (
    ComponentInfo,
    ComponentNotFoundError,
    LoadedComponent,
    PackageInfo,
    PackageLoadError,
)

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """
    Universal Component Registry for FlowMason.

    This registry:
    - Scans a packages directory for .fmpkg files
    - Extracts and validates package manifests
    - Dynamically loads component classes on demand
    - Provides lookup methods for components by type/category
    - Caches loaded components for performance

    ARCHITECTURE RULE: This registry has ZERO hardcoded component types.
    All components are loaded dynamically from packages.
    """

    def __init__(
        self,
        packages_dir: Optional[str | Path] = None,
        cache_dir: Optional[str | Path] = None,
        auto_scan: bool = True,
    ):
        """
        Initialize the component registry.

        Args:
            packages_dir: Directory containing .fmpkg files.
                         Default: ~/.flowmason/packages
            cache_dir: Directory for extracted packages.
                      Default: temp directory
            auto_scan: Whether to scan packages_dir on initialization
        """
        self.packages_dir = Path(packages_dir) if packages_dir else Path.home() / ".flowmason" / "packages"
        self.packages_dir.mkdir(parents=True, exist_ok=True)

        # Initialize loader and extractor
        cache_path = Path(cache_dir) if cache_dir else None
        self._loader = PackageLoader(cache_dir=cache_path)
        self._extractor = MetadataExtractor()

        # Thread-safe registries (RLock allows reentrant locking)
        self._lock = RLock()

        # Component registry: component_type -> ComponentInfo
        self._components: Dict[str, ComponentInfo] = {}

        # Loaded classes cache: component_type -> LoadedComponent
        self._loaded_cache: Dict[str, LoadedComponent] = {}

        # Package registry: package_name -> PackageInfo
        self._packages: Dict[str, PackageInfo] = {}

        # Package path index: package_path -> package_name
        self._package_paths: Dict[str, str] = {}

        # Auto-scan if requested
        if auto_scan and self.packages_dir.exists():
            self.scan_packages()

    def auto_discover(self) -> int:
        """
        Auto-discover and register all available components.

        This method:
        1. Scans the packages directory for .fmpkg files
        2. Discovers built-in lab components (nodes, operators, control flow)

        Returns:
            Total number of components registered
        """
        total = 0

        # Scan .fmpkg packages
        total += self.scan_packages()

        # Discover lab components
        total += self._discover_lab_components()

        logger.info(f"Auto-discovered {total} total components")
        return total

    def _discover_lab_components(self) -> int:
        """
        Discover and register built-in lab components.

        Scans flowmason_lab for decorated component classes.

        Returns:
            Number of components registered
        """
        registered = 0

        try:
            # Import lab modules to trigger decorator registration
            from flowmason_lab.nodes.core import critic, generator, improver, selector, synthesizer
            from flowmason_lab.operators.control_flow import (
                conditional,
                foreach,
                return_early,
                router,
                subpipeline,
                trycatch,
            )
            from flowmason_lab.operators.core import (
                filter,
                http_request,
                json_transform,
                loop,
                output_router,
                schema_validate,
                variable_set,
            )
            from flowmason_lab.operators.core import logger as logger_op

            # Get all module references
            lab_modules = [
                # Nodes
                generator, critic, improver, selector, synthesizer,
                # Core operators
                json_transform, http_request, filter, loop,
                variable_set, logger_op, schema_validate, output_router,
                # Control flow
                conditional, router, foreach, trycatch, subpipeline, return_early,
            ]

            # Extract components from each module
            for module in lab_modules:
                for name in dir(module):
                    obj = getattr(module, name)
                    if (
                        isinstance(obj, type) and
                        hasattr(obj, '_flowmason_metadata') and
                        obj._flowmason_metadata is not None
                    ):
                        try:
                            # Extract metadata
                            component_info = self._extractor.extract_from_class(obj)
                            component_info.package_name = "flowmason-lab"
                            component_info.package_version = "builtin"
                            component_info.is_core = True

                            # Register component
                            with self._lock:
                                self._components[component_info.component_type] = component_info

                                # Cache loaded class
                                self._loaded_cache[component_info.component_type] = LoadedComponent(
                                    component_class=obj,
                                    metadata=obj._flowmason_metadata,
                                    info=component_info,
                                    module_name=obj.__module__,
                                    module_path=module.__file__ or "",
                                )

                            registered += 1
                            logger.debug(f"Registered lab component: {component_info.component_type}")

                        except Exception as e:
                            logger.warning(f"Failed to register lab component {name}: {e}")

        except ImportError as e:
            logger.warning(f"Failed to import lab components: {e}")

        logger.info(f"Discovered {registered} lab components")
        return registered

    def scan_packages(self, packages_dir: Optional[str | Path] = None) -> int:
        """
        Scan a directory for .fmpkg files and register them.

        Args:
            packages_dir: Directory to scan. Default: self.packages_dir

        Returns:
            Number of components registered
        """
        scan_dir = Path(packages_dir) if packages_dir else self.packages_dir

        if not scan_dir.exists():
            logger.warning(f"Packages directory does not exist: {scan_dir}")
            return 0

        registered = 0
        fmpkg_files = list(scan_dir.glob("**/*.fmpkg"))

        logger.info(f"Scanning {scan_dir} for packages... Found {len(fmpkg_files)} .fmpkg files")

        for fmpkg_path in fmpkg_files:
            try:
                pkg_info = self.register_package(str(fmpkg_path))
                registered += len(pkg_info.components)
                logger.debug(f"Registered package: {pkg_info.name}@{pkg_info.version}")
            except PackageLoadError as e:
                logger.warning(f"Failed to register package {fmpkg_path}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error registering {fmpkg_path}: {e}")

        logger.info(f"Registered {registered} components from {len(fmpkg_files)} packages")
        return registered

    def register_package(
        self,
        package_path: str | Path,
        is_core: bool = False,
    ) -> PackageInfo:
        """
        Register a package and its components.

        This extracts the package, reads the manifest, and registers
        all components found in the package.

        Args:
            package_path: Path to the .fmpkg file
            is_core: Whether this is a core package (managed by FlowMason team)

        Returns:
            PackageInfo for the registered package

        Raises:
            PackageLoadError: If the package cannot be loaded
        """
        package_path = Path(package_path)

        with self._lock:
            # Check if already registered
            if str(package_path) in self._package_paths:
                pkg_name = self._package_paths[str(package_path)]
                return self._packages[pkg_name]

            # Extract package and read manifest
            extract_dir, manifest = self._loader.extract_package(package_path)

            # Create package info
            pkg_info = self._loader.get_package_info(manifest, str(package_path))
            pkg_info.install_path = str(extract_dir)
            pkg_info.is_core = is_core

            # Load and register components
            entry_point = manifest.get("entry_point", "index.py")

            try:
                # Load the component class
                component_class = self._loader.load_component_class(
                    extract_dir,
                    entry_point,
                )

                # Extract metadata
                component_info = self._extractor.extract_from_class(component_class)
                component_info.package_name = pkg_info.name
                component_info.package_version = pkg_info.version
                component_info.package_path = str(package_path)
                component_info.is_core = is_core

                # Register component
                self._components[component_info.component_type] = component_info
                pkg_info.components.append(component_info.component_type)

                # Cache loaded class
                self._loaded_cache[component_info.component_type] = LoadedComponent(
                    component_class=component_class,
                    metadata=component_class._flowmason_metadata,
                    info=component_info,
                    module_name=component_class.__module__,
                    module_path=str(extract_dir / entry_point),
                )

                logger.debug(f"Registered component: {component_info.component_type}")

            except Exception as e:
                # Record the error but continue
                logger.error(f"Failed to load component from {package_path}: {e}")
                pkg_info.is_active = False

            # Register package
            self._packages[pkg_info.name] = pkg_info
            self._package_paths[str(package_path)] = pkg_info.name

            return pkg_info

    def unregister_package(self, package_name: str, version: Optional[str] = None) -> bool:
        """
        Unregister a package and its components.

        Args:
            package_name: Name of the package to unregister
            version: Optional specific version to unregister

        Returns:
            True if package was unregistered, False if not found
        """
        with self._lock:
            if package_name not in self._packages:
                return False

            pkg_info = self._packages[package_name]

            # If version specified, check it matches
            if version and pkg_info.version != version:
                return False

            # Unregister components
            for component_type in pkg_info.components:
                if component_type in self._components:
                    del self._components[component_type]
                if component_type in self._loaded_cache:
                    del self._loaded_cache[component_type]

            # Unload package from loader
            if pkg_info.install_path:
                self._loader.unload_package(pkg_info.install_path)

            # Remove package registration
            del self._packages[package_name]

            # Remove from path index
            paths_to_remove = [
                path for path, name in self._package_paths.items()
                if name == package_name
            ]
            for path in paths_to_remove:
                del self._package_paths[path]

            logger.info(f"Unregistered package: {package_name}")
            return True

    def get_component_class(self, component_type: str) -> Type:
        """
        Get the component class for a given component type.

        Args:
            component_type: The component type name (e.g., "generator", "support_triage")

        Returns:
            The component class

        Raises:
            ComponentNotFoundError: If component is not registered
        """
        with self._lock:
            # Check cache first
            if component_type in self._loaded_cache:
                return self._loaded_cache[component_type].component_class

            # Check if component is registered but not loaded
            if component_type in self._components:
                # Try to load it
                component_info = self._components[component_type]
                if component_info.package_path:
                    try:
                        self.register_package(component_info.package_path)
                        if component_type in self._loaded_cache:
                            return self._loaded_cache[component_type].component_class
                    except PackageLoadError as e:
                        raise ComponentNotFoundError(component_type) from e

            raise ComponentNotFoundError(component_type)

    def get_component_metadata(self, component_type: str) -> ComponentInfo:
        """
        Get metadata for a component.

        Args:
            component_type: The component type name

        Returns:
            ComponentInfo with all metadata

        Raises:
            ComponentNotFoundError: If component is not registered
        """
        with self._lock:
            if component_type not in self._components:
                raise ComponentNotFoundError(component_type)

            return self._components[component_type]

    def list_components(
        self,
        category: Optional[str] = None,
        component_kind: Optional[str] = None,
        include_inactive: bool = False,
    ) -> List[ComponentInfo]:
        """
        List all available components.

        Args:
            category: Filter by category (e.g., "reasoning", "transformers")
            component_kind: Filter by kind ("node" or "operator")
            include_inactive: Include components that failed to load

        Returns:
            List of ComponentInfo objects
        """
        with self._lock:
            components = list(self._components.values())

            # Apply filters
            if category:
                components = [c for c in components if c.category == category]

            if component_kind:
                components = [c for c in components if c.component_kind == component_kind]

            if not include_inactive:
                components = [c for c in components if c.is_available]

            return components

    def list_nodes(self, category: Optional[str] = None) -> List[ComponentInfo]:
        """List all registered nodes, optionally filtered by category."""
        return self.list_components(category=category, component_kind="node")

    def list_operators(self, category: Optional[str] = None) -> List[ComponentInfo]:
        """List all registered operators, optionally filtered by category."""
        return self.list_components(category=category, component_kind="operator")

    def get_categories(self, component_kind: Optional[str] = None) -> List[str]:
        """
        Get all unique categories.

        Args:
            component_kind: Filter by kind ("node" or "operator")

        Returns:
            List of unique category names
        """
        with self._lock:
            component_list = list(self._components.values())

            if component_kind:
                component_list = [c for c in component_list if c.component_kind == component_kind]

            return sorted(set(c.category for c in component_list))

    def has_component(self, component_type: str) -> bool:
        """Check if a component is registered."""
        with self._lock:
            return component_type in self._components

    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get info about a registered package."""
        with self._lock:
            return self._packages.get(package_name)

    def list_packages(self, include_inactive: bool = False) -> List[PackageInfo]:
        """List all registered packages."""
        with self._lock:
            packages = list(self._packages.values())
            if not include_inactive:
                packages = [p for p in packages if p.is_active]
            return packages

    def refresh(self) -> int:
        """
        Refresh the registry by rescanning the packages directory.

        Returns:
            Number of components registered
        """
        with self._lock:
            # Clear existing registrations
            self._components.clear()
            self._loaded_cache.clear()
            self._packages.clear()
            self._package_paths.clear()

        return self.scan_packages()

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            components = list(self._components.values())
            return {
                "total_components": len(components),
                "total_nodes": len([c for c in components if c.component_kind == "node"]),
                "total_operators": len([c for c in components if c.component_kind == "operator"]),
                "total_packages": len(self._packages),
                "loaded_components": len(self._loaded_cache),
                "categories": self.get_categories(),
                "core_packages": len([p for p in self._packages.values() if p.is_core]),
            }

    def cleanup(self) -> None:
        """Clean up registry resources."""
        with self._lock:
            self._components.clear()
            self._loaded_cache.clear()
            self._packages.clear()
            self._package_paths.clear()

        self._loader.cleanup()

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"ComponentRegistry("
            f"components={stats['total_components']}, "
            f"packages={stats['total_packages']}, "
            f"packages_dir='{self.packages_dir}')"
        )


# Convenience function for getting a global registry instance
_global_registry: Optional[ComponentRegistry] = None


def get_registry(packages_dir: Optional[str | Path] = None) -> ComponentRegistry:
    """
    Get the global component registry instance.

    Creates a new registry if one doesn't exist.

    Args:
        packages_dir: Optional packages directory (only used on first call)

    Returns:
        The global ComponentRegistry instance
    """
    global _global_registry

    if _global_registry is None:
        _global_registry = ComponentRegistry(packages_dir=packages_dir)

    return _global_registry


def reset_registry() -> None:
    """Reset the global registry. Mainly for testing."""
    global _global_registry

    if _global_registry is not None:
        _global_registry.cleanup()
        _global_registry = None
