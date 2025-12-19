"""
Registry Type Definitions

Data structures used by the ComponentRegistry system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type


class RegistryError(Exception):
    """Base exception for registry errors."""
    pass


class ComponentNotFoundError(RegistryError):
    """Raised when a component cannot be found in the registry."""

    def __init__(self, component_type: str, version: Optional[str] = None):
        self.component_type = component_type
        self.version = version
        msg = f"Component '{component_type}' not found"
        if version:
            msg += f" (version {version})"
        super().__init__(msg)


class PackageLoadError(RegistryError):
    """Raised when a package fails to load."""

    def __init__(self, package_path: str, reason: str):
        self.package_path = package_path
        self.reason = reason
        super().__init__(f"Failed to load package '{package_path}': {reason}")


class ComponentValidationError(RegistryError):
    """Raised when component validation fails."""

    def __init__(self, component_name: str, errors: List[str]):
        self.component_name = component_name
        self.errors = errors
        msg = f"Component '{component_name}' validation failed:\n"
        msg += "\n".join(f"  - {e}" for e in errors)
        super().__init__(msg)


@dataclass
class ComponentInfo:
    """
    Information about a registered component.

    This represents a component available in the registry,
    including its metadata and load status.
    """

    # Identification
    component_type: str  # Unique name like "generator", "support_triage"
    component_kind: str  # "node", "operator", or "control_flow"
    category: str

    # Description
    description: str
    version: str

    # Display
    icon: str = "box"
    color: str = "#6B7280"

    # Control flow specific (must come after required fields)
    control_flow_type: Optional[str] = None  # For control_flow: "conditional", "foreach", etc.

    # Author
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Schemas (JSON Schema format)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)

    # Runtime
    requires_llm: bool = False
    timeout_seconds: int = 60

    # AI config (for nodes)
    recommended_providers: Optional[Dict[str, Dict[str, Any]]] = None
    default_provider: Optional[str] = None
    required_capabilities: Optional[List[str]] = None
    min_context_window: Optional[int] = None
    require_vision: bool = False
    require_function_calling: bool = False
    supports_streaming: bool = False
    max_retries: int = 3

    # Package info
    package_name: str = ""
    package_version: str = ""
    package_path: str = ""

    # Load status
    is_loaded: bool = False
    is_available: bool = True
    load_error: Optional[str] = None

    # Flags
    is_core: bool = False  # Managed by FlowMason team
    is_deprecated: bool = False
    deprecation_message: Optional[str] = None

    # Timestamps
    registered_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PackageInfo:
    """
    Information about a loaded package.

    A package can contain one or more components.
    """

    # Identification
    name: str
    version: str

    # Description
    description: str

    # Author
    author: Optional[str] = None
    author_email: Optional[str] = None

    # Components in this package
    components: List[str] = field(default_factory=list)  # List of component_type names

    # File info
    package_path: str = ""
    install_path: str = ""

    # Dependencies
    dependencies: List[str] = field(default_factory=list)

    # Flags
    is_core: bool = False
    is_active: bool = True

    # Timestamps
    installed_at: datetime = field(default_factory=datetime.utcnow)

    # Metadata from manifest
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadedComponent:
    """
    A component that has been loaded into memory.

    Contains the actual class and its metadata.
    """

    # The actual component class
    component_class: Type

    # Metadata from decorator
    metadata: Dict[str, Any]

    # Component info
    info: ComponentInfo

    # Module info (for cleanup)
    module_name: str
    module_path: str

    # Load status
    loaded_at: datetime = field(default_factory=datetime.utcnow)
