"""
Core Package Installer for FlowMason.

Installs core FlowMason packages to new instances.
Core packages are the foundation components that come with every FlowMason instance.

ARCHITECTURE RULE: Core packages are "just packages" - they have NO special treatment
in the runtime. They are dynamically loaded from .fmpkg files like any other package.
"""

import logging
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from flowmason_core.registry import ComponentRegistry

logger = logging.getLogger(__name__)


class CorePackageInstaller:
    """
    Installs core FlowMason packages to new instances.

    Core packages include:
    - Nodes: generator, critic, improver, synthesizer, selector
    - Operators: http_request, json_transform, filter, loop, schema_validate, variable_set, logger

    These packages are bundled with FlowMason and installed automatically
    when a new organization/instance is created.
    """

    # Core packages that come with every FlowMason instance
    CORE_PACKAGES: List[Tuple[str, str]] = [
        # Core nodes (AI-focused components)
        ("generator", "1.0.0"),
        ("critic", "1.0.0"),
        ("improver", "1.0.0"),
        ("synthesizer", "1.0.0"),
        ("selector", "1.0.0"),

        # Core operators (utility components)
        ("http_request", "1.0.0"),
        ("json_transform", "1.0.0"),
        ("filter", "1.0.0"),
        ("loop", "1.0.0"),
        ("schema_validate", "1.0.0"),
        ("variable_set", "1.0.0"),
        ("logger", "1.0.0"),
    ]

    def __init__(
        self,
        registry: Optional[ComponentRegistry] = None,
        bundled_packages_dir: Optional[str | Path] = None,
    ):
        """
        Initialize the core package installer.

        Args:
            registry: ComponentRegistry instance to register packages with.
                     If not provided, uses the global registry.
            bundled_packages_dir: Directory where bundled core packages are stored.
                                Default: /opt/flowmason/core-packages (production)
                                         or dist/packages (development)
        """
        self._registry = registry

        # Determine bundled packages location
        if bundled_packages_dir:
            self._bundled_dir = Path(bundled_packages_dir)
        else:
            # Check common locations
            prod_path = Path("/opt/flowmason/core-packages")
            dev_path = Path(__file__).parent.parent.parent.parent / "dist" / "packages"

            if prod_path.exists():
                self._bundled_dir = prod_path
            elif dev_path.exists():
                self._bundled_dir = dev_path
            else:
                # Default to dist/packages (will be created by package builder)
                self._bundled_dir = dev_path

    @property
    def registry(self) -> ComponentRegistry:
        """Get the component registry."""
        if self._registry is None:
            from flowmason_core.registry import get_registry
            self._registry = get_registry()
        return self._registry

    def get_bundled_package_path(self, package_name: str, version: str) -> Path:
        """Get the path to a bundled package file."""
        return self._bundled_dir / f"{package_name}-{version}.fmpkg"

    async def install_core_packages(
        self,
        organization_id: Optional[str] = None,
        target_packages_dir: Optional[str | Path] = None,
        skip_missing: bool = True,
    ) -> List[str]:
        """
        Install all core packages to an organization.

        This method:
        1. Copies core .fmpkg files from bundled directory to organization's packages dir
        2. Registers each package with the component registry

        Called during instance initialization.

        Args:
            organization_id: Organization ID for multi-tenant setups (optional)
            target_packages_dir: Target directory for packages.
                               Default: registry's packages_dir
            skip_missing: If True, skip packages that don't exist and continue.
                         If False, raise error on missing packages.

        Returns:
            List of successfully installed package names
        """
        installed = []

        # Determine target directory
        if target_packages_dir:
            target_dir = Path(target_packages_dir)
        else:
            target_dir = self.registry.packages_dir

        # Create organization subdirectory if specified
        if organization_id:
            target_dir = target_dir / organization_id

        target_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Installing core packages to {target_dir}")

        for package_name, version in self.CORE_PACKAGES:
            source_path = self.get_bundled_package_path(package_name, version)

            if not source_path.exists():
                msg = f"Core package not found: {source_path}"
                if skip_missing:
                    logger.warning(msg)
                    continue
                else:
                    raise FileNotFoundError(msg)

            try:
                # Copy package to target directory
                target_path = target_dir / source_path.name
                if not target_path.exists():
                    shutil.copy2(source_path, target_path)
                    logger.debug(f"Copied {package_name} to {target_path}")

                # Register with registry
                self.registry.register_package(
                    target_path,
                    is_core=True,
                )

                installed.append(package_name)
                logger.info(f"Installed core package: {package_name}@{version}")

            except Exception as e:
                logger.error(f"Failed to install {package_name}: {e}")
                # Continue with other packages

        logger.info(f"Installed {len(installed)}/{len(self.CORE_PACKAGES)} core packages")
        return installed

    def list_available_packages(self) -> List[Tuple[str, str, bool]]:
        """
        List all core packages and their availability.

        Returns:
            List of (package_name, version, is_available) tuples
        """
        result = []
        for package_name, version in self.CORE_PACKAGES:
            path = self.get_bundled_package_path(package_name, version)
            result.append((package_name, version, path.exists()))
        return result

    def verify_installation(self) -> dict:
        """
        Verify that all core packages are properly installed.

        Returns:
            Dictionary with installation status and any issues found
        """
        issues = []
        installed = []
        missing = []

        for package_name, version in self.CORE_PACKAGES:
            # Check if registered in registry
            if self.registry.has_component(package_name):
                installed.append(package_name)
            else:
                missing.append(package_name)
                issues.append(f"Component '{package_name}' not registered")

        return {
            "healthy": len(issues) == 0,
            "installed": installed,
            "missing": missing,
            "issues": issues,
            "total_expected": len(self.CORE_PACKAGES),
            "total_installed": len(installed),
        }


async def install_core_packages_to_instance(
    organization_id: str,
    packages_dir: Optional[str | Path] = None,
) -> List[str]:
    """
    Convenience function to install core packages to a new instance.

    Args:
        organization_id: The organization/instance ID
        packages_dir: Optional custom packages directory

    Returns:
        List of installed package names
    """
    installer = CorePackageInstaller()
    return await installer.install_core_packages(
        organization_id=organization_id,
        target_packages_dir=packages_dir,
    )
