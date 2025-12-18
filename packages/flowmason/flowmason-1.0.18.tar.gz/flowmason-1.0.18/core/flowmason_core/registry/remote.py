"""
Remote Registry Client

Provides functionality to connect to remote FlowMason registries,
search for packages, download components, and publish packages.
"""

import hashlib
import json
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class RemoteRegistryError(Exception):
    """Base exception for remote registry errors."""
    pass


class RegistryConnectionError(RemoteRegistryError):
    """Failed to connect to registry."""
    pass


class PackageNotFoundError(RemoteRegistryError):
    """Package not found in registry."""
    pass


class PackageDownloadError(RemoteRegistryError):
    """Failed to download package."""
    pass


class PackagePublishError(RemoteRegistryError):
    """Failed to publish package."""
    pass


class AuthenticationError(RemoteRegistryError):
    """Authentication failed."""
    pass


@dataclass
class RegistryConfig:
    """Configuration for a remote registry."""

    name: str
    url: str
    auth_token: Optional[str] = None
    priority: int = 100  # Lower = higher priority
    enabled: bool = True
    is_default: bool = False

    # Capabilities
    can_publish: bool = False
    requires_auth: bool = False

    # Metadata
    description: Optional[str] = None
    added_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RemotePackageInfo:
    """Information about a package in a remote registry."""

    name: str
    version: str
    description: str
    author: Optional[str] = None
    author_email: Optional[str] = None

    # Download info
    download_url: str = ""
    checksum: str = ""  # SHA256
    size_bytes: int = 0

    # Components
    components: List[str] = field(default_factory=list)
    component_count: int = 0

    # Metadata
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None

    # Registry info
    registry_name: str = ""
    registry_url: str = ""

    # Timestamps
    published_at: Optional[datetime] = None
    downloads: int = 0

    # Versions
    available_versions: List[str] = field(default_factory=list)
    latest_version: str = ""


@dataclass
class SearchResult:
    """Result of a package search."""

    packages: List[RemotePackageInfo]
    total_count: int
    page: int
    page_size: int
    query: str


class RemoteRegistryClient:
    """
    Client for interacting with remote FlowMason registries.

    Supports:
    - Multiple registry sources with priority ordering
    - Package search and discovery
    - Package download with verification
    - Package publishing (authenticated)
    - Local caching
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
    ):
        """
        Initialize the remote registry client.

        Args:
            config_path: Path to registries config file.
                        Default: ~/.flowmason/registries.json
            cache_dir: Directory for caching downloaded packages.
                      Default: ~/.flowmason/cache/packages
        """
        self.config_path = config_path or Path.home() / ".flowmason" / "registries.json"
        self.cache_dir = cache_dir or Path.home() / ".flowmason" / "cache" / "packages"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._registries: Dict[str, RegistryConfig] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load registry configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)

                for reg_data in data.get("registries", []):
                    config = RegistryConfig(
                        name=reg_data["name"],
                        url=reg_data["url"],
                        auth_token=reg_data.get("auth_token"),
                        priority=reg_data.get("priority", 100),
                        enabled=reg_data.get("enabled", True),
                        is_default=reg_data.get("is_default", False),
                        can_publish=reg_data.get("can_publish", False),
                        requires_auth=reg_data.get("requires_auth", False),
                        description=reg_data.get("description"),
                    )
                    self._registries[config.name] = config

            except Exception as e:
                logger.warning(f"Failed to load registry config: {e}")

        # Ensure default registry exists
        if not self._registries:
            self._add_default_registry()

    def _add_default_registry(self) -> None:
        """Add the default FlowMason registry."""
        # For now, use localhost Studio as default
        # In production, this would be registry.flowmason.io
        default = RegistryConfig(
            name="local",
            url="http://localhost:8999",
            priority=50,
            enabled=True,
            is_default=True,
            can_publish=True,
            description="Local FlowMason Studio registry",
        )
        self._registries["local"] = default

    def _save_config(self) -> None:
        """Save registry configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "registries": [
                {
                    "name": r.name,
                    "url": r.url,
                    "auth_token": r.auth_token,
                    "priority": r.priority,
                    "enabled": r.enabled,
                    "is_default": r.is_default,
                    "can_publish": r.can_publish,
                    "requires_auth": r.requires_auth,
                    "description": r.description,
                }
                for r in self._registries.values()
            ]
        }

        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def _get_http_client(self):
        """Get HTTP client (lazy import to avoid dependency)."""
        try:
            import httpx
            return httpx
        except ImportError:
            import urllib.request
            import urllib.error
            return None  # Will use urllib fallback

    def _make_request(
        self,
        registry: RegistryConfig,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Make an HTTP request to a registry."""
        url = urljoin(registry.url.rstrip("/") + "/", f"api/v1/registry/{endpoint.lstrip('/')}")

        headers = {"Content-Type": "application/json"}
        if registry.auth_token:
            headers["Authorization"] = f"Bearer {registry.auth_token}"

        httpx = self._get_http_client()

        if httpx:
            # Use httpx if available
            try:
                with httpx.Client(timeout=timeout) as client:
                    if method == "GET":
                        response = client.get(url, headers=headers)
                    elif method == "POST":
                        response = client.post(url, headers=headers, json=data)
                    else:
                        raise ValueError(f"Unsupported method: {method}")

                    response.raise_for_status()
                    result: Dict[str, Any] = response.json()
                    return result

            except httpx.ConnectError as e:
                raise RegistryConnectionError(f"Failed to connect to {registry.url}: {e}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError(f"Authentication failed for {registry.name}")
                elif e.response.status_code == 404:
                    raise PackageNotFoundError(f"Not found: {endpoint}")
                raise RemoteRegistryError(f"HTTP error: {e}")

        else:
            # Fallback to urllib
            import urllib.request
            import urllib.error

            try:
                req = urllib.request.Request(url, headers=headers)
                if method == "POST" and data:
                    req.data = json.dumps(data).encode()

                with urllib.request.urlopen(req, timeout=timeout) as response:
                    urllib_result: Dict[str, Any] = json.loads(response.read().decode())
                    return urllib_result

            except urllib.error.URLError as e:
                raise RegistryConnectionError(f"Failed to connect to {registry.url}: {e}")
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    raise AuthenticationError(f"Authentication failed for {registry.name}")
                elif e.code == 404:
                    raise PackageNotFoundError(f"Not found: {endpoint}")
                raise RemoteRegistryError(f"HTTP error: {e}")

    # ==========================================================================
    # Registry Management
    # ==========================================================================

    def add_registry(
        self,
        name: str,
        url: str,
        auth_token: Optional[str] = None,
        priority: int = 100,
        set_default: bool = False,
    ) -> RegistryConfig:
        """
        Add a new registry.

        Args:
            name: Unique name for the registry
            url: Base URL of the registry
            auth_token: Optional authentication token
            priority: Priority (lower = higher priority)
            set_default: Whether to set as default registry

        Returns:
            The created RegistryConfig
        """
        if name in self._registries:
            raise ValueError(f"Registry '{name}' already exists")

        config = RegistryConfig(
            name=name,
            url=url,
            auth_token=auth_token,
            priority=priority,
            is_default=set_default,
        )

        # Test connection
        try:
            self._make_request(config, "GET", "health")
            config.enabled = True
        except RemoteRegistryError:
            logger.warning(f"Could not connect to registry {url}, adding anyway")
            config.enabled = False

        if set_default:
            for reg in self._registries.values():
                reg.is_default = False

        self._registries[name] = config
        self._save_config()

        return config

    def remove_registry(self, name: str) -> bool:
        """
        Remove a registry.

        Args:
            name: Name of the registry to remove

        Returns:
            True if removed, False if not found
        """
        if name not in self._registries:
            return False

        del self._registries[name]
        self._save_config()
        return True

    def list_registries(self, include_disabled: bool = False) -> List[RegistryConfig]:
        """
        List all configured registries.

        Args:
            include_disabled: Include disabled registries

        Returns:
            List of registry configurations sorted by priority
        """
        registries = list(self._registries.values())

        if not include_disabled:
            registries = [r for r in registries if r.enabled]

        return sorted(registries, key=lambda r: r.priority)

    def get_registry(self, name: str) -> Optional[RegistryConfig]:
        """Get a registry by name."""
        return self._registries.get(name)

    def get_default_registry(self) -> Optional[RegistryConfig]:
        """Get the default registry."""
        for reg in self._registries.values():
            if reg.is_default and reg.enabled:
                return reg
        # Return highest priority enabled registry
        enabled = [r for r in self._registries.values() if r.enabled]
        if enabled:
            return min(enabled, key=lambda r: r.priority)
        return None

    def set_default_registry(self, name: str) -> bool:
        """Set a registry as the default."""
        if name not in self._registries:
            return False

        for reg in self._registries.values():
            reg.is_default = reg.name == name

        self._save_config()
        return True

    # ==========================================================================
    # Package Search & Discovery
    # ==========================================================================

    def search(
        self,
        query: str,
        registry_name: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResult:
        """
        Search for packages across registries.

        Args:
            query: Search query
            registry_name: Specific registry to search (None = all)
            category: Filter by category
            page: Page number
            page_size: Results per page

        Returns:
            SearchResult with matching packages
        """
        all_packages: List[RemotePackageInfo] = []

        registries = (
            [self._registries[registry_name]]
            if registry_name and registry_name in self._registries
            else self.list_registries()
        )

        for registry in registries:
            try:
                params = {
                    "q": query,
                    "page": page,
                    "page_size": page_size,
                }
                if category:
                    params["category"] = category

                result = self._make_request(
                    registry, "GET",
                    f"packages/search?q={query}&page={page}&page_size={page_size}"
                )

                for pkg_data in result.get("packages", []):
                    pkg = self._parse_package_info(pkg_data, registry)
                    all_packages.append(pkg)

            except RemoteRegistryError as e:
                logger.warning(f"Search failed on {registry.name}: {e}")

        return SearchResult(
            packages=all_packages,
            total_count=len(all_packages),
            page=page,
            page_size=page_size,
            query=query,
        )

    def get_package(
        self,
        name: str,
        version: Optional[str] = None,
        registry_name: Optional[str] = None,
    ) -> Optional[RemotePackageInfo]:
        """
        Get information about a specific package.

        Args:
            name: Package name
            version: Specific version (None = latest)
            registry_name: Specific registry (None = search all)

        Returns:
            Package info or None if not found
        """
        registries = (
            [self._registries[registry_name]]
            if registry_name and registry_name in self._registries
            else self.list_registries()
        )

        for registry in registries:
            try:
                endpoint = f"packages/{name}"
                if version:
                    endpoint += f"/{version}"

                result = self._make_request(registry, "GET", endpoint)
                return self._parse_package_info(result, registry)

            except PackageNotFoundError:
                continue
            except RemoteRegistryError as e:
                logger.warning(f"Failed to get package from {registry.name}: {e}")

        return None

    def list_versions(
        self,
        name: str,
        registry_name: Optional[str] = None,
    ) -> List[str]:
        """
        List all available versions of a package.

        Args:
            name: Package name
            registry_name: Specific registry (None = default)

        Returns:
            List of version strings
        """
        registry = (
            self._registries.get(registry_name)
            if registry_name
            else self.get_default_registry()
        )

        if not registry:
            return []

        try:
            result = self._make_request(registry, "GET", f"packages/{name}/versions")
            versions: List[str] = result.get("versions", [])
            return versions
        except RemoteRegistryError:
            return []

    def _parse_package_info(
        self,
        data: Dict[str, Any],
        registry: RegistryConfig,
    ) -> RemotePackageInfo:
        """Parse package data from API response."""
        published_at = None
        if data.get("published_at"):
            try:
                published_at = datetime.fromisoformat(data["published_at"].replace("Z", "+00:00"))
            except ValueError:
                pass

        return RemotePackageInfo(
            name=data.get("name", ""),
            version=data.get("version", ""),
            description=data.get("description", ""),
            author=data.get("author"),
            author_email=data.get("author_email"),
            download_url=data.get("download_url", ""),
            checksum=data.get("checksum", ""),
            size_bytes=data.get("size_bytes", 0),
            components=data.get("components", []),
            component_count=data.get("component_count", len(data.get("components", []))),
            tags=data.get("tags", []),
            category=data.get("category"),
            license=data.get("license"),
            homepage=data.get("homepage"),
            repository=data.get("repository"),
            registry_name=registry.name,
            registry_url=registry.url,
            published_at=published_at,
            downloads=data.get("downloads", 0),
            available_versions=data.get("available_versions", []),
            latest_version=data.get("latest_version", data.get("version", "")),
        )

    # ==========================================================================
    # Package Download
    # ==========================================================================

    def download(
        self,
        name: str,
        version: Optional[str] = None,
        registry_name: Optional[str] = None,
        verify: bool = True,
    ) -> Path:
        """
        Download a package to the local cache.

        Args:
            name: Package name
            version: Specific version (None = latest)
            registry_name: Specific registry (None = search all)
            verify: Verify checksum after download

        Returns:
            Path to the downloaded .fmpkg file

        Raises:
            PackageNotFoundError: If package not found
            PackageDownloadError: If download fails
        """
        # Get package info
        pkg_info = self.get_package(name, version, registry_name)
        if not pkg_info:
            raise PackageNotFoundError(f"Package '{name}' not found")

        # Check cache first
        cache_path = self.cache_dir / f"{name}-{pkg_info.version}.fmpkg"
        if cache_path.exists():
            if not verify or self._verify_checksum(cache_path, pkg_info.checksum):
                logger.info(f"Using cached package: {cache_path}")
                return cache_path

        # Download package
        download_url = pkg_info.download_url
        if not download_url:
            # Construct default download URL
            registry = self._registries.get(pkg_info.registry_name)
            if registry:
                download_url = urljoin(
                    registry.url.rstrip("/") + "/",
                    f"api/v1/registry/packages/{name}/{pkg_info.version}/download"
                )

        if not download_url:
            raise PackageDownloadError(f"No download URL for package '{name}'")

        logger.info(f"Downloading {name}@{pkg_info.version} from {pkg_info.registry_name}...")

        try:
            self._download_file(download_url, cache_path, pkg_info)
        except Exception as e:
            raise PackageDownloadError(f"Failed to download package: {e}")

        # Verify checksum
        if verify and pkg_info.checksum:
            if not self._verify_checksum(cache_path, pkg_info.checksum):
                cache_path.unlink()
                raise PackageDownloadError("Checksum verification failed")

        logger.info(f"Downloaded to: {cache_path}")
        return cache_path

    def _download_file(
        self,
        url: str,
        dest_path: Path,
        pkg_info: RemotePackageInfo,
    ) -> None:
        """Download a file from URL."""
        headers = {}

        # Add auth if available
        registry = self._registries.get(pkg_info.registry_name)
        if registry and registry.auth_token:
            headers["Authorization"] = f"Bearer {registry.auth_token}"

        httpx = self._get_http_client()

        if httpx:
            with httpx.stream("GET", url, headers=headers, follow_redirects=True) as response:
                response.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
        else:
            import urllib.request
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                with open(dest_path, "wb") as f:
                    shutil.copyfileobj(response, f)

    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify file checksum."""
        if not expected_checksum:
            return True

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)

        actual = sha256_hash.hexdigest()
        return actual == expected_checksum

    def install(
        self,
        name: str,
        version: Optional[str] = None,
        registry_name: Optional[str] = None,
        packages_dir: Optional[Path] = None,
    ) -> Path:
        """
        Download and install a package to the packages directory.

        Args:
            name: Package name
            version: Specific version (None = latest)
            registry_name: Specific registry (None = search all)
            packages_dir: Installation directory.
                         Default: ~/.flowmason/packages

        Returns:
            Path to the installed .fmpkg file
        """
        packages_dir = packages_dir or Path.home() / ".flowmason" / "packages"
        packages_dir.mkdir(parents=True, exist_ok=True)

        # Download to cache
        cache_path = self.download(name, version, registry_name)

        # Copy to packages directory
        pkg_info = self.get_package(name, version, registry_name)
        if not pkg_info:
            raise PackageNotFoundError(f"Package '{name}' not found")

        install_path = packages_dir / f"{name}-{pkg_info.version}.fmpkg"
        shutil.copy2(cache_path, install_path)

        logger.info(f"Installed package to: {install_path}")
        return install_path

    # ==========================================================================
    # Package Publishing
    # ==========================================================================

    def publish(
        self,
        package_path: Path,
        registry_name: Optional[str] = None,
    ) -> RemotePackageInfo:
        """
        Publish a package to a registry.

        Args:
            package_path: Path to the .fmpkg file
            registry_name: Registry to publish to (None = default)

        Returns:
            Info about the published package

        Raises:
            PackagePublishError: If publishing fails
            AuthenticationError: If not authenticated
        """
        registry = (
            self._registries.get(registry_name)
            if registry_name
            else self.get_default_registry()
        )

        if not registry:
            raise PackagePublishError("No registry configured")

        if not registry.can_publish:
            raise PackagePublishError(f"Registry '{registry.name}' does not support publishing")

        if registry.requires_auth and not registry.auth_token:
            raise AuthenticationError(f"Authentication required for {registry.name}")

        if not package_path.exists():
            raise PackagePublishError(f"Package file not found: {package_path}")

        # Calculate checksum
        sha256_hash = hashlib.sha256()
        with open(package_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        checksum = sha256_hash.hexdigest()

        # Upload package
        url = urljoin(
            registry.url.rstrip("/") + "/",
            "api/v1/registry/packages/upload"
        )

        headers = {}
        if registry.auth_token:
            headers["Authorization"] = f"Bearer {registry.auth_token}"

        try:
            httpx = self._get_http_client()

            if httpx:
                with open(package_path, "rb") as f:
                    files = {"file": (package_path.name, f, "application/octet-stream")}
                    data = {"checksum": checksum}
                    with httpx.Client() as client:
                        response = client.post(url, headers=headers, files=files, data=data)
                        response.raise_for_status()
                        result = response.json()
            else:
                raise PackagePublishError("httpx is required for publishing")

            return self._parse_package_info(result, registry)

        except Exception as e:
            raise PackagePublishError(f"Failed to publish package: {e}")

    # ==========================================================================
    # Cache Management
    # ==========================================================================

    def clear_cache(self, older_than_days: Optional[int] = None) -> int:
        """
        Clear the package cache.

        Args:
            older_than_days: Only clear packages older than N days.
                           None = clear all.

        Returns:
            Number of packages removed
        """
        if not self.cache_dir.exists():
            return 0

        removed = 0
        now = datetime.utcnow()

        for file in self.cache_dir.glob("*.fmpkg"):
            if older_than_days is not None:
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                age_days = (now - mtime).days
                if age_days < older_than_days:
                    continue

            file.unlink()
            removed += 1

        return removed

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.cache_dir.exists():
            return {"packages": 0, "total_size_bytes": 0}

        packages = list(self.cache_dir.glob("*.fmpkg"))
        total_size = sum(p.stat().st_size for p in packages)

        return {
            "packages": len(packages),
            "total_size_bytes": total_size,
            "cache_dir": str(self.cache_dir),
        }


# Convenience singleton
_client: Optional[RemoteRegistryClient] = None


def get_remote_registry() -> RemoteRegistryClient:
    """Get the global remote registry client."""
    global _client
    if _client is None:
        _client = RemoteRegistryClient()
    return _client


def reset_remote_registry() -> None:
    """Reset the global client. Mainly for testing."""
    global _client
    _client = None
