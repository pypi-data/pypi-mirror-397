"""
FlowMason Package System.

This module provides support for .fmpkg packages:
- Build packages from projects
- Install packages locally
- Deploy packages to orgs
"""

from flowmason_core.packaging.builder import (
    PackageBuilder,
    build_package,
)
from flowmason_core.packaging.installer import (
    PackageInstaller,
    install_package,
)
from flowmason_core.packaging.manifest import (
    PackageDependency,
    PackageManifest,
    create_manifest,
)

__all__ = [
    # Manifest
    "PackageManifest",
    "PackageDependency",
    "create_manifest",
    # Builder
    "PackageBuilder",
    "build_package",
    # Installer
    "PackageInstaller",
    "install_package",
]
