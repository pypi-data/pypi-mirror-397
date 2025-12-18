"""
Private Package Registry Service.

Manages package storage, access control, and organization-scoped packages.
Supports both public and private packages with authentication.
"""

import hashlib
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from zipfile import ZipFile

from pydantic import BaseModel, Field


class PackageVisibility(str, Enum):
    """Package visibility levels."""
    PUBLIC = "public"           # Anyone can download
    PRIVATE = "private"         # Only organization members
    UNLISTED = "unlisted"       # Anyone with link can download


class PackageAccess(str, Enum):
    """Package access levels."""
    READ = "read"               # Can download
    WRITE = "write"             # Can publish new versions
    ADMIN = "admin"             # Can delete, change visibility


@dataclass
class PackagePermission:
    """Permission for a user/team on a package."""
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    access_level: PackageAccess = PackageAccess.READ


@dataclass
class PackageMetadata:
    """Enhanced package metadata with access control."""
    name: str
    version: str
    description: str = ""
    author: Optional[str] = None
    author_email: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None

    # Access control
    org_id: Optional[str] = None
    visibility: PackageVisibility = PackageVisibility.PUBLIC
    permissions: List[PackagePermission] = field(default_factory=list)

    # Statistics
    downloads: int = 0
    published_at: Optional[datetime] = None
    published_by: Optional[str] = None  # User ID

    # Components
    components: List[str] = field(default_factory=list)


class PackageRegistryConfig(BaseModel):
    """Configuration for the package registry."""
    storage_path: Path = Path.home() / ".flowmason" / "registry"
    allow_anonymous_download: bool = True      # Allow downloading public packages without auth
    require_auth_for_upload: bool = True       # Require auth to upload
    max_package_size_mb: int = 100             # Maximum package size in MB
    retention_days: int = 0                    # Keep old versions (0 = keep forever)


class PackageRegistry:
    """
    Private Package Registry.

    Manages package storage with organization-scoped access control.
    """

    def __init__(self, config: Optional[PackageRegistryConfig] = None):
        self.config = config or PackageRegistryConfig()
        self._packages_dir = self.config.storage_path / "packages"
        self._metadata_dir = self.config.storage_path / "metadata"

        # Ensure directories exist
        self._packages_dir.mkdir(parents=True, exist_ok=True)
        self._metadata_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Package Operations
    # =========================================================================

    def publish_package(
        self,
        package_path: Path,
        org_id: Optional[str] = None,
        user_id: Optional[str] = None,
        visibility: PackageVisibility = PackageVisibility.PUBLIC,
        checksum: Optional[str] = None,
    ) -> PackageMetadata:
        """
        Publish a new package version to the registry.

        Args:
            package_path: Path to the .fmpkg file
            org_id: Organization owning the package (None for public global)
            user_id: ID of the publishing user
            visibility: Package visibility level
            checksum: Optional SHA256 checksum for verification

        Returns:
            PackageMetadata for the published package

        Raises:
            ValueError: If package is invalid
            PermissionError: If user lacks publish permission
            FileExistsError: If version already exists
        """
        # Verify checksum if provided
        if checksum:
            actual = self._calculate_checksum(package_path)
            if actual != checksum:
                raise ValueError(f"Checksum mismatch: expected {checksum}, got {actual}")

        # Check file size
        size_mb = package_path.stat().st_size / (1024 * 1024)
        if size_mb > self.config.max_package_size_mb:
            raise ValueError(
                f"Package too large: {size_mb:.1f}MB (max {self.config.max_package_size_mb}MB)"
            )

        # Parse manifest
        manifest = self._get_manifest(package_path)
        name = manifest.get("name")
        version = manifest.get("version", "1.0.0")

        if not name:
            raise ValueError("Package manifest missing 'name' field")

        # Check if version exists
        if self.get_package(name, version, org_id):
            raise FileExistsError(f"Package {name}@{version} already exists")

        # Determine storage location
        if org_id:
            pkg_dir = self._packages_dir / "orgs" / org_id / name
        else:
            pkg_dir = self._packages_dir / "public" / name

        pkg_dir.mkdir(parents=True, exist_ok=True)
        dest_path = pkg_dir / f"{name}-{version}.fmpkg"

        # Copy package
        shutil.copy2(package_path, dest_path)

        # Create metadata
        metadata = PackageMetadata(
            name=name,
            version=version,
            description=manifest.get("description", ""),
            author=manifest.get("author"),
            author_email=manifest.get("author_email"),
            license=manifest.get("license"),
            homepage=manifest.get("homepage"),
            repository=manifest.get("repository"),
            tags=manifest.get("tags", []),
            category=manifest.get("category"),
            org_id=org_id,
            visibility=visibility,
            downloads=0,
            published_at=datetime.utcnow(),
            published_by=user_id,
            components=manifest.get("components", [manifest.get("component_type", "")]),
        )

        # Save metadata
        self._save_metadata(metadata)

        return metadata

    def get_package(
        self,
        name: str,
        version: Optional[str] = None,
        org_id: Optional[str] = None,
    ) -> Optional[PackageMetadata]:
        """
        Get package metadata.

        If version is None, returns the latest version.
        """
        meta_path = self._get_metadata_path(name, org_id)
        if not meta_path.exists():
            return None

        try:
            with open(meta_path) as f:
                data = json.load(f)
        except Exception:
            return None

        if version:
            # Get specific version
            version_data = data.get("versions", {}).get(version)
            if not version_data:
                return None
            return self._dict_to_metadata(version_data)
        else:
            # Get latest version
            latest = data.get("latest")
            if not latest:
                return None
            version_data = data.get("versions", {}).get(latest)
            if not version_data:
                return None
            return self._dict_to_metadata(version_data)

    def download_package(
        self,
        name: str,
        version: Optional[str] = None,
        org_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Get path to package file for download.

        Increments download counter.
        """
        metadata = self.get_package(name, version, org_id)
        if not metadata:
            return None

        # Determine package path
        if org_id:
            pkg_path = (
                self._packages_dir / "orgs" / org_id / name /
                f"{name}-{metadata.version}.fmpkg"
            )
        else:
            pkg_path = (
                self._packages_dir / "public" / name /
                f"{name}-{metadata.version}.fmpkg"
            )

        if not pkg_path.exists():
            return None

        # Increment download count
        self._increment_downloads(name, metadata.version, org_id)

        return pkg_path

    def delete_package(
        self,
        name: str,
        version: str,
        org_id: Optional[str] = None,
    ) -> bool:
        """Delete a specific package version."""
        # Get package path
        if org_id:
            pkg_path = (
                self._packages_dir / "orgs" / org_id / name /
                f"{name}-{version}.fmpkg"
            )
        else:
            pkg_path = (
                self._packages_dir / "public" / name /
                f"{name}-{version}.fmpkg"
            )

        if not pkg_path.exists():
            return False

        # Delete file
        pkg_path.unlink()

        # Update metadata
        self._remove_version(name, version, org_id)

        return True

    def list_packages(
        self,
        org_id: Optional[str] = None,
        category: Optional[str] = None,
        query: Optional[str] = None,
        include_private: bool = False,
        user_id: Optional[str] = None,
    ) -> List[PackageMetadata]:
        """
        List packages with optional filtering.

        Args:
            org_id: Filter to specific organization
            category: Filter by category
            query: Search query (matches name, description, tags)
            include_private: Include private packages (requires user_id)
            user_id: User ID for access checking
        """
        results = []

        # Scan public packages
        public_dir = self._metadata_dir / "public"
        if public_dir.exists():
            for meta_file in public_dir.glob("*.json"):
                metadata = self._load_latest_metadata(meta_file)
                if metadata and self._matches_filter(
                    metadata, category, query, include_private, user_id
                ):
                    results.append(metadata)

        # Scan org packages
        if org_id:
            org_dir = self._metadata_dir / "orgs" / org_id
            if org_dir.exists():
                for meta_file in org_dir.glob("*.json"):
                    metadata = self._load_latest_metadata(meta_file)
                    if metadata and self._matches_filter(
                        metadata, category, query, include_private, user_id
                    ):
                        results.append(metadata)

        return sorted(results, key=lambda m: m.name)

    def get_versions(
        self,
        name: str,
        org_id: Optional[str] = None,
    ) -> List[str]:
        """Get all versions of a package."""
        meta_path = self._get_metadata_path(name, org_id)
        if not meta_path.exists():
            return []

        try:
            with open(meta_path) as f:
                data = json.load(f)
            versions = list(data.get("versions", {}).keys())
            return sorted(versions, reverse=True)
        except Exception:
            return []

    # =========================================================================
    # Access Control
    # =========================================================================

    def can_access(
        self,
        name: str,
        org_id: Optional[str],
        user_id: Optional[str],
        required_level: PackageAccess = PackageAccess.READ,
    ) -> bool:
        """
        Check if a user can access a package.

        Public packages: anyone can read
        Private packages: only org members
        Write/Admin: specific permission required
        """
        metadata = self.get_package(name, org_id=org_id)
        if not metadata:
            return False

        # Public packages are readable by everyone
        if metadata.visibility == PackageVisibility.PUBLIC:
            if required_level == PackageAccess.READ:
                return True

        # Unlisted packages are readable by anyone with the link
        if metadata.visibility == PackageVisibility.UNLISTED:
            if required_level == PackageAccess.READ:
                return True

        # For private packages or write access, need to check permissions
        if not user_id:
            return False

        # Publisher has admin access
        if metadata.published_by == user_id:
            return True

        # Check explicit permissions
        for perm in metadata.permissions:
            if perm.user_id == user_id:
                return self._access_level_sufficient(perm.access_level, required_level)

        return False

    def grant_access(
        self,
        name: str,
        org_id: Optional[str],
        user_id: str,
        access_level: PackageAccess,
    ) -> bool:
        """Grant a user access to a package."""
        metadata = self.get_package(name, org_id=org_id)
        if not metadata:
            return False

        # Update permissions
        metadata.permissions = [
            p for p in metadata.permissions if p.user_id != user_id
        ]
        metadata.permissions.append(
            PackagePermission(user_id=user_id, access_level=access_level)
        )

        self._save_metadata(metadata)
        return True

    def revoke_access(
        self,
        name: str,
        org_id: Optional[str],
        user_id: str,
    ) -> bool:
        """Revoke a user's access to a package."""
        metadata = self.get_package(name, org_id=org_id)
        if not metadata:
            return False

        metadata.permissions = [
            p for p in metadata.permissions if p.user_id != user_id
        ]

        self._save_metadata(metadata)
        return True

    def set_visibility(
        self,
        name: str,
        org_id: Optional[str],
        visibility: PackageVisibility,
    ) -> bool:
        """Change package visibility."""
        metadata = self.get_package(name, org_id=org_id)
        if not metadata:
            return False

        metadata.visibility = visibility
        self._save_metadata(metadata)
        return True

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(
        self,
        org_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get registry statistics."""
        packages = self.list_packages(org_id=org_id, include_private=True)

        total_downloads = sum(p.downloads for p in packages)
        total_components = sum(len(p.components) for p in packages)

        categories: Dict[str, int] = {}
        for pkg in packages:
            cat = pkg.category or "uncategorized"
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "packages_count": len(packages),
            "components_count": total_components,
            "total_downloads": total_downloads,
            "categories": categories,
        }

    def get_popular_packages(
        self,
        limit: int = 10,
        org_id: Optional[str] = None,
    ) -> List[PackageMetadata]:
        """Get most downloaded packages."""
        packages = self.list_packages(org_id=org_id)
        return sorted(packages, key=lambda p: p.downloads, reverse=True)[:limit]

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _get_manifest(self, package_path: Path) -> Dict[str, Any]:
        """Extract manifest from package."""
        with ZipFile(package_path, "r") as zf:
            if "manifest.json" not in zf.namelist():
                raise ValueError("Package missing manifest.json")
            manifest: Dict[str, Any] = json.loads(zf.read("manifest.json").decode())
            return manifest

    def _get_metadata_path(self, name: str, org_id: Optional[str]) -> Path:
        """Get path to package metadata file."""
        if org_id:
            return self._metadata_dir / "orgs" / org_id / f"{name}.json"
        return self._metadata_dir / "public" / f"{name}.json"

    def _save_metadata(self, metadata: PackageMetadata) -> None:
        """Save package metadata."""
        meta_path = self._get_metadata_path(metadata.name, metadata.org_id)
        meta_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing or create new
        if meta_path.exists():
            with open(meta_path) as f:
                data = json.load(f)
        else:
            data = {"versions": {}, "latest": None}

        # Update version
        data["versions"][metadata.version] = self._metadata_to_dict(metadata)
        data["latest"] = metadata.version

        with open(meta_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _remove_version(self, name: str, version: str, org_id: Optional[str]) -> None:
        """Remove a version from metadata."""
        meta_path = self._get_metadata_path(name, org_id)
        if not meta_path.exists():
            return

        with open(meta_path) as f:
            data = json.load(f)

        if version in data.get("versions", {}):
            del data["versions"][version]

        # Update latest
        if data["latest"] == version:
            versions = list(data.get("versions", {}).keys())
            data["latest"] = sorted(versions, reverse=True)[0] if versions else None

        # Delete metadata file if no versions left
        if not data.get("versions"):
            meta_path.unlink()
        else:
            with open(meta_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

    def _increment_downloads(
        self, name: str, version: str, org_id: Optional[str]
    ) -> None:
        """Increment download counter."""
        metadata = self.get_package(name, version, org_id)
        if metadata:
            metadata.downloads += 1
            self._save_metadata(metadata)

    def _load_latest_metadata(self, meta_path: Path) -> Optional[PackageMetadata]:
        """Load latest version metadata from file."""
        try:
            with open(meta_path) as f:
                data = json.load(f)
            latest = data.get("latest")
            if not latest:
                return None
            version_data = data.get("versions", {}).get(latest)
            if not version_data:
                return None
            return self._dict_to_metadata(version_data)
        except Exception:
            return None

    def _metadata_to_dict(self, metadata: PackageMetadata) -> Dict[str, Any]:
        """Convert metadata to dict for JSON storage."""
        return {
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "author": metadata.author,
            "author_email": metadata.author_email,
            "license": metadata.license,
            "homepage": metadata.homepage,
            "repository": metadata.repository,
            "tags": metadata.tags,
            "category": metadata.category,
            "org_id": metadata.org_id,
            "visibility": metadata.visibility.value,
            "permissions": [
                {
                    "user_id": p.user_id,
                    "team_id": p.team_id,
                    "access_level": p.access_level.value,
                }
                for p in metadata.permissions
            ],
            "downloads": metadata.downloads,
            "published_at": metadata.published_at.isoformat() if metadata.published_at else None,
            "published_by": metadata.published_by,
            "components": metadata.components,
        }

    def _dict_to_metadata(self, data: Dict[str, Any]) -> PackageMetadata:
        """Convert dict to PackageMetadata."""
        permissions = [
            PackagePermission(
                user_id=p.get("user_id"),
                team_id=p.get("team_id"),
                access_level=PackageAccess(p.get("access_level", "read")),
            )
            for p in data.get("permissions", [])
        ]

        published_at = data.get("published_at")
        if published_at and isinstance(published_at, str):
            published_at = datetime.fromisoformat(published_at)

        return PackageMetadata(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            author=data.get("author"),
            author_email=data.get("author_email"),
            license=data.get("license"),
            homepage=data.get("homepage"),
            repository=data.get("repository"),
            tags=data.get("tags", []),
            category=data.get("category"),
            org_id=data.get("org_id"),
            visibility=PackageVisibility(data.get("visibility", "public")),
            permissions=permissions,
            downloads=data.get("downloads", 0),
            published_at=published_at,
            published_by=data.get("published_by"),
            components=data.get("components", []),
        )

    def _matches_filter(
        self,
        metadata: PackageMetadata,
        category: Optional[str],
        query: Optional[str],
        include_private: bool,
        user_id: Optional[str],
    ) -> bool:
        """Check if package matches filters."""
        # Check visibility
        if metadata.visibility == PackageVisibility.PRIVATE and not include_private:
            # Check if user has access
            if not user_id or not self.can_access(
                metadata.name, metadata.org_id, user_id
            ):
                return False

        # Check category
        if category and metadata.category != category:
            return False

        # Check query
        if query:
            query_lower = query.lower()
            searchable = " ".join([
                metadata.name,
                metadata.description,
                " ".join(metadata.tags),
            ]).lower()
            if query_lower not in searchable:
                return False

        return True

    def _access_level_sufficient(
        self, have: PackageAccess, need: PackageAccess
    ) -> bool:
        """Check if access level is sufficient."""
        levels = [PackageAccess.READ, PackageAccess.WRITE, PackageAccess.ADMIN]
        return levels.index(have) >= levels.index(need)


# Singleton instance
_registry: Optional[PackageRegistry] = None


def get_package_registry() -> PackageRegistry:
    """Get the package registry singleton."""
    global _registry
    if _registry is None:
        _registry = PackageRegistry()
    return _registry
