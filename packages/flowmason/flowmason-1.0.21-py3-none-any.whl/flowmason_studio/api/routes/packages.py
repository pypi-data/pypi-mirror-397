"""
Package Registry API Routes.

Provides HTTP API for package management, search, and distribution.
This enables Studio to act as a remote registry server.
"""

import hashlib
import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zipfile import ZipFile

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from flowmason_studio.services.storage import get_pipeline_storage

router = APIRouter(prefix="/registry", tags=["registry"])


# =============================================================================
# Models
# =============================================================================


class PackageMetadata(BaseModel):
    """Package metadata from manifest."""

    name: str
    version: str
    description: str = ""
    author: Optional[str] = None
    author_email: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None


class PackageInfo(BaseModel):
    """Package information for API responses."""

    name: str
    version: str
    description: str = ""
    author: Optional[str] = None
    author_email: Optional[str] = None

    # Download info
    download_url: str = ""
    checksum: str = ""
    size_bytes: int = 0

    # Components
    components: List[str] = Field(default_factory=list)
    component_count: int = 0

    # Metadata
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None

    # Timestamps
    published_at: Optional[datetime] = None
    downloads: int = 0

    # Versions
    available_versions: List[str] = Field(default_factory=list)
    latest_version: str = ""


class SearchResponse(BaseModel):
    """Search results response."""

    packages: List[PackageInfo]
    total_count: int
    page: int
    page_size: int
    query: str


class VersionsResponse(BaseModel):
    """Package versions response."""

    name: str
    versions: List[str]
    latest: str


class HealthResponse(BaseModel):
    """Registry health response."""

    status: str
    registry_name: str
    version: str
    packages_count: int
    components_count: int


# =============================================================================
# Package Storage
# =============================================================================


def get_packages_dir() -> Path:
    """Get the packages storage directory."""
    packages_dir = Path.home() / ".flowmason" / "registry" / "packages"
    packages_dir.mkdir(parents=True, exist_ok=True)
    return packages_dir


def get_package_manifest(package_path: Path) -> Dict[str, Any]:
    """Extract manifest from a package."""
    with ZipFile(package_path, "r") as zf:
        if "manifest.json" not in zf.namelist():
            raise ValueError("Package missing manifest.json")
        manifest: Dict[str, Any] = json.loads(zf.read("manifest.json").decode())
        return manifest


def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def list_stored_packages() -> List[Dict[str, Any]]:
    """List all packages in storage."""
    packages_dir = get_packages_dir()
    packages = []

    for pkg_file in packages_dir.glob("**/*.fmpkg"):
        try:
            manifest = get_package_manifest(pkg_file)
            checksum = calculate_checksum(pkg_file)
            size_bytes = pkg_file.stat().st_size
            mtime = datetime.fromtimestamp(pkg_file.stat().st_mtime)

            packages.append({
                "file_path": pkg_file,
                "manifest": manifest,
                "checksum": checksum,
                "size_bytes": size_bytes,
                "published_at": mtime,
            })
        except Exception:
            continue

    return packages


def get_stored_package(name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a specific package from storage."""
    packages_dir = get_packages_dir()

    # Look for package file
    pattern = f"{name}-{version}.fmpkg" if version else f"{name}-*.fmpkg"
    matches = list(packages_dir.glob(pattern))

    if not matches:
        # Try without version prefix
        matches = list(packages_dir.glob(f"{name}.fmpkg"))

    if not matches:
        return None

    # If no specific version, get latest
    if version:
        pkg_file = next((m for m in matches if f"-{version}.fmpkg" in str(m)), None)
    else:
        # Sort by version (assuming semantic versioning)
        pkg_file = sorted(matches, reverse=True)[0] if matches else None

    if not pkg_file:
        return None

    try:
        manifest = get_package_manifest(pkg_file)
        return {
            "file_path": pkg_file,
            "manifest": manifest,
            "checksum": calculate_checksum(pkg_file),
            "size_bytes": pkg_file.stat().st_size,
            "published_at": datetime.fromtimestamp(pkg_file.stat().st_mtime),
        }
    except Exception:
        return None


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/health", response_model=HealthResponse)
async def registry_health() -> HealthResponse:
    """Check registry health and capabilities."""
    packages = list_stored_packages()
    component_count = sum(
        len(p["manifest"].get("components", [p["manifest"].get("component_type", "")]))
        for p in packages
    )

    return HealthResponse(
        status="healthy",
        registry_name="FlowMason Studio Registry",
        version="1.0.0",
        packages_count=len(packages),
        components_count=component_count,
    )


@router.get("/packages/search", response_model=SearchResponse)
async def search_packages(
    q: str = Query("", description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
) -> SearchResponse:
    """Search for packages."""
    all_packages = list_stored_packages()
    query_lower = q.lower()

    # Filter packages
    matching = []
    for pkg in all_packages:
        manifest = pkg["manifest"]

        # Search in name, description, tags
        searchable = " ".join([
            manifest.get("name", ""),
            manifest.get("description", ""),
            " ".join(manifest.get("tags", [])),
        ]).lower()

        if q and query_lower not in searchable:
            continue

        if category and manifest.get("category") != category:
            continue

        matching.append(pkg)

    # Paginate
    total = len(matching)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = matching[start:end]

    # Convert to response format
    packages = []
    for pkg in page_items:
        manifest = pkg["manifest"]
        packages.append(PackageInfo(
            name=manifest.get("name", ""),
            version=manifest.get("version", "1.0.0"),
            description=manifest.get("description", ""),
            author=manifest.get("author"),
            author_email=manifest.get("author_email"),
            download_url=f"/api/v1/registry/packages/{manifest.get('name')}/{manifest.get('version')}/download",
            checksum=pkg["checksum"],
            size_bytes=pkg["size_bytes"],
            components=manifest.get("components", [manifest.get("component_type", "")]),
            component_count=len(manifest.get("components", [manifest.get("component_type", "")])),
            tags=manifest.get("tags", []),
            category=manifest.get("category"),
            license=manifest.get("license"),
            homepage=manifest.get("homepage"),
            repository=manifest.get("repository"),
            published_at=pkg["published_at"],
            downloads=0,  # TODO: Track downloads
            latest_version=manifest.get("version", "1.0.0"),
        ))

    return SearchResponse(
        packages=packages,
        total_count=total,
        page=page,
        page_size=page_size,
        query=q,
    )


@router.get("/packages/{name}", response_model=PackageInfo)
async def get_package(name: str) -> PackageInfo:
    """Get information about a specific package (latest version)."""
    pkg = get_stored_package(name)
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")

    manifest = pkg["manifest"]
    return PackageInfo(
        name=manifest.get("name", name),
        version=manifest.get("version", "1.0.0"),
        description=manifest.get("description", ""),
        author=manifest.get("author"),
        author_email=manifest.get("author_email"),
        download_url=f"/api/v1/registry/packages/{name}/{manifest.get('version')}/download",
        checksum=pkg["checksum"],
        size_bytes=pkg["size_bytes"],
        components=manifest.get("components", [manifest.get("component_type", "")]),
        component_count=len(manifest.get("components", [manifest.get("component_type", "")])),
        tags=manifest.get("tags", []),
        category=manifest.get("category"),
        license=manifest.get("license"),
        homepage=manifest.get("homepage"),
        repository=manifest.get("repository"),
        published_at=pkg["published_at"],
        downloads=0,
        latest_version=manifest.get("version", "1.0.0"),
    )


@router.get("/packages/{name}/{version}", response_model=PackageInfo)
async def get_package_version(name: str, version: str) -> PackageInfo:
    """Get information about a specific package version."""
    pkg = get_stored_package(name, version)
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{name}@{version}' not found")

    manifest = pkg["manifest"]
    return PackageInfo(
        name=manifest.get("name", name),
        version=manifest.get("version", version),
        description=manifest.get("description", ""),
        author=manifest.get("author"),
        author_email=manifest.get("author_email"),
        download_url=f"/api/v1/registry/packages/{name}/{version}/download",
        checksum=pkg["checksum"],
        size_bytes=pkg["size_bytes"],
        components=manifest.get("components", [manifest.get("component_type", "")]),
        component_count=len(manifest.get("components", [manifest.get("component_type", "")])),
        tags=manifest.get("tags", []),
        category=manifest.get("category"),
        license=manifest.get("license"),
        homepage=manifest.get("homepage"),
        repository=manifest.get("repository"),
        published_at=pkg["published_at"],
        downloads=0,
        latest_version=manifest.get("version", version),
    )


@router.get("/packages/{name}/versions", response_model=VersionsResponse)
async def get_package_versions(name: str) -> VersionsResponse:
    """Get all available versions of a package."""
    packages_dir = get_packages_dir()

    # Find all versions
    matches = list(packages_dir.glob(f"{name}-*.fmpkg"))
    versions = []

    for match in matches:
        try:
            manifest = get_package_manifest(match)
            versions.append(manifest.get("version", "1.0.0"))
        except Exception:
            continue

    if not versions:
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")

    # Sort versions (assuming semantic versioning)
    versions.sort(reverse=True)

    return VersionsResponse(
        name=name,
        versions=versions,
        latest=versions[0] if versions else "",
    )


@router.get("/packages/{name}/{version}/download")
async def download_package(name: str, version: str):
    """Download a package file."""
    pkg = get_stored_package(name, version)
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{name}@{version}' not found")

    return FileResponse(
        path=pkg["file_path"],
        filename=f"{name}-{version}.fmpkg",
        media_type="application/octet-stream",
    )


@router.post("/packages/upload", response_model=PackageInfo)
async def upload_package(
    file: UploadFile = File(...),
    checksum: Optional[str] = Form(None),
):
    """
    Upload a new package to the registry.

    The package must be a valid .fmpkg file with a manifest.json.
    """
    if not file.filename or not file.filename.endswith(".fmpkg"):
        raise HTTPException(status_code=400, detail="File must be a .fmpkg package")

    # Save to temp file first
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fmpkg") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Verify checksum if provided
        if checksum:
            actual_checksum = calculate_checksum(tmp_path)
            if actual_checksum != checksum:
                raise HTTPException(status_code=400, detail="Checksum verification failed")

        # Parse manifest
        try:
            manifest = get_package_manifest(tmp_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid package: {e}")

        name = manifest.get("name")
        version = manifest.get("version", "1.0.0")

        if not name:
            raise HTTPException(status_code=400, detail="Package manifest missing 'name' field")

        # Move to packages directory
        packages_dir = get_packages_dir()
        dest_path = packages_dir / f"{name}-{version}.fmpkg"

        if dest_path.exists():
            raise HTTPException(
                status_code=409,
                detail=f"Package {name}@{version} already exists"
            )

        shutil.move(str(tmp_path), str(dest_path))

        # Return package info
        return PackageInfo(
            name=name,
            version=version,
            description=manifest.get("description", ""),
            author=manifest.get("author"),
            author_email=manifest.get("author_email"),
            download_url=f"/api/v1/registry/packages/{name}/{version}/download",
            checksum=calculate_checksum(dest_path),
            size_bytes=dest_path.stat().st_size,
            components=manifest.get("components", [manifest.get("component_type", "")]),
            component_count=len(manifest.get("components", [manifest.get("component_type", "")])),
            tags=manifest.get("tags", []),
            category=manifest.get("category"),
            license=manifest.get("license"),
            homepage=manifest.get("homepage"),
            repository=manifest.get("repository"),
            published_at=datetime.utcnow(),
            downloads=0,
            latest_version=version,
        )

    finally:
        # Clean up temp file if still exists
        if tmp_path.exists():
            tmp_path.unlink()


@router.delete("/packages/{name}/{version}")
async def delete_package(name: str, version: str):
    """Delete a package from the registry."""
    pkg = get_stored_package(name, version)
    if not pkg:
        raise HTTPException(status_code=404, detail=f"Package '{name}@{version}' not found")

    pkg["file_path"].unlink()

    return {"message": f"Package {name}@{version} deleted", "success": True}


@router.get("/categories")
async def list_categories() -> List[str]:
    """List all package categories."""
    packages = list_stored_packages()
    categories = set()

    for pkg in packages:
        cat = pkg["manifest"].get("category")
        if cat:
            categories.add(cat)

    return sorted(categories)


@router.get("/stats")
async def registry_stats() -> Dict[str, Any]:
    """Get registry statistics."""
    packages = list_stored_packages()

    total_size = sum(p["size_bytes"] for p in packages)
    component_count = sum(
        len(p["manifest"].get("components", [p["manifest"].get("component_type", "")]))
        for p in packages
    )

    categories: Dict[str, int] = {}
    for p in packages:
        cat = p["manifest"].get("category", "uncategorized")
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "packages_count": len(packages),
        "components_count": component_count,
        "total_size_bytes": total_size,
        "categories": categories,
    }
