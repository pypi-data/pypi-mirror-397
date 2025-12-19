"""
FlowMason Universal Component Registry

Provides dynamic loading and management of FlowMason components from packages.
Includes remote registry support for package distribution.
"""

from flowmason_core.registry.extractor import MetadataExtractor
from flowmason_core.registry.loader import PackageLoader
from flowmason_core.registry.registry import ComponentRegistry, get_registry, reset_registry
from flowmason_core.registry.remote import (
    RemoteRegistryClient,
    RemotePackageInfo,
    RegistryConfig,
    SearchResult,
    get_remote_registry,
    reset_remote_registry,
)
from flowmason_core.registry.types import (
    ComponentInfo,
    ComponentNotFoundError,
    PackageInfo,
    PackageLoadError,
    RegistryError,
)

__all__ = [
    # Local registry
    "ComponentRegistry",
    "PackageLoader",
    "MetadataExtractor",
    "ComponentInfo",
    "PackageInfo",
    "RegistryError",
    "ComponentNotFoundError",
    "PackageLoadError",
    "get_registry",
    "reset_registry",
    # Remote registry
    "RemoteRegistryClient",
    "RemotePackageInfo",
    "RegistryConfig",
    "SearchResult",
    "get_remote_registry",
    "reset_remote_registry",
]
