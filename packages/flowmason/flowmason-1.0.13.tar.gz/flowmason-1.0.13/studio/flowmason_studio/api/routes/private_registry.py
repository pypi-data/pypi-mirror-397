"""
Private Package Registry API Routes.

Authenticated endpoints for managing private packages with organization-scoped access control.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from flowmason_studio.auth import AuthContext, require_auth
from flowmason_studio.services.package_registry import (
    PackageAccess,
    PackageMetadata,
    PackageRegistry,
    PackageVisibility,
    get_package_registry,
)

router = APIRouter(prefix="/private-registry", tags=["private-registry"])


# =============================================================================
# API Models
# =============================================================================


class PackageResponse(BaseModel):
    """Package information response."""
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

    # Access control
    org_id: Optional[str] = None
    visibility: str = "public"

    # Statistics
    downloads: int = 0
    published_at: Optional[datetime] = None
    published_by: Optional[str] = None

    # Components
    components: List[str] = Field(default_factory=list)
    component_count: int = 0

    # Download info
    download_url: str = ""
    checksum: str = ""


class PackageListResponse(BaseModel):
    """List of packages response."""
    packages: List[PackageResponse]
    total: int
    page: int = 1
    page_size: int = 20


class VersionsResponse(BaseModel):
    """Package versions response."""
    name: str
    versions: List[str]
    latest: str


class AccessGrantRequest(BaseModel):
    """Request to grant access to a package."""
    user_id: str
    access_level: str = "read"  # read, write, admin


class VisibilityRequest(BaseModel):
    """Request to change package visibility."""
    visibility: str  # public, private, unlisted


class StatsResponse(BaseModel):
    """Registry statistics response."""
    packages_count: int
    components_count: int
    total_downloads: int
    categories: dict


def _metadata_to_response(
    metadata: PackageMetadata,
    registry: PackageRegistry,
) -> PackageResponse:
    """Convert PackageMetadata to API response."""
    # Build download URL
    if metadata.org_id:
        download_url = f"/api/v1/private-registry/packages/{metadata.name}/{metadata.version}/download?org_id={metadata.org_id}"
    else:
        download_url = f"/api/v1/private-registry/packages/{metadata.name}/{metadata.version}/download"

    return PackageResponse(
        name=metadata.name,
        version=metadata.version,
        description=metadata.description,
        author=metadata.author,
        author_email=metadata.author_email,
        license=metadata.license,
        homepage=metadata.homepage,
        repository=metadata.repository,
        tags=metadata.tags,
        category=metadata.category,
        org_id=metadata.org_id,
        visibility=metadata.visibility.value,
        downloads=metadata.downloads,
        published_at=metadata.published_at,
        published_by=metadata.published_by,
        components=metadata.components,
        component_count=len(metadata.components),
        download_url=download_url,
        checksum="",  # Would need to compute from file
    )


# =============================================================================
# Package Operations
# =============================================================================


@router.post("/packages/publish", response_model=PackageResponse)
async def publish_package(
    file: UploadFile = File(..., description="The .fmpkg package file"),
    visibility: str = Form("public", description="Package visibility (public/private/unlisted)"),
    checksum: Optional[str] = Form(None, description="SHA256 checksum for verification"),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
) -> PackageResponse:
    """
    Publish a new package to the private registry.

    Requires authentication. The package will be scoped to the user's organization.
    """
    if not file.filename or not file.filename.endswith(".fmpkg"):
        raise HTTPException(status_code=400, detail="File must be a .fmpkg package")

    # Save uploaded file to temp location
    import tempfile
    import shutil

    with tempfile.NamedTemporaryFile(suffix=".fmpkg", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Validate visibility
        try:
            pkg_visibility = PackageVisibility(visibility)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid visibility: {visibility}. Must be public, private, or unlisted"
            )

        # Publish package
        metadata = registry.publish_package(
            package_path=tmp_path,
            org_id=auth.org.id,
            user_id=auth.user.id if auth.user else None,
            visibility=pkg_visibility,
            checksum=checksum,
        )

        return _metadata_to_response(metadata, registry)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()


@router.get("/packages", response_model=PackageListResponse)
async def list_packages(
    org_id: Optional[str] = Query(None, description="Filter by organization"),
    category: Optional[str] = Query(None, description="Filter by category"),
    q: Optional[str] = Query(None, description="Search query"),
    include_private: bool = Query(False, description="Include private packages"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
) -> PackageListResponse:
    """
    List packages accessible to the authenticated user.
    """
    # Use authenticated user's org if not specified
    if org_id is None:
        org_id = auth.org.id

    user_id = auth.user.id if auth.user else None

    packages = registry.list_packages(
        org_id=org_id,
        category=category,
        query=q,
        include_private=include_private,
        user_id=user_id,
    )

    # Paginate
    total = len(packages)
    start = (page - 1) * page_size
    end = start + page_size
    page_packages = packages[start:end]

    return PackageListResponse(
        packages=[_metadata_to_response(p, registry) for p in page_packages],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/packages/{name}", response_model=PackageResponse)
async def get_package(
    name: str,
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
) -> PackageResponse:
    """Get package information (latest version)."""
    # Use authenticated user's org if not specified
    if org_id is None:
        org_id = auth.org.id

    # Check access
    user_id = auth.user.id if auth.user else None
    if not registry.can_access(name, org_id, user_id, PackageAccess.READ):
        raise HTTPException(status_code=403, detail="Access denied to this package")

    metadata = registry.get_package(name, org_id=org_id)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")

    return _metadata_to_response(metadata, registry)


@router.get("/packages/{name}/{version}", response_model=PackageResponse)
async def get_package_version(
    name: str,
    version: str,
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
) -> PackageResponse:
    """Get specific package version information."""
    if org_id is None:
        org_id = auth.org.id

    user_id = auth.user.id if auth.user else None
    if not registry.can_access(name, org_id, user_id, PackageAccess.READ):
        raise HTTPException(status_code=403, detail="Access denied to this package")

    metadata = registry.get_package(name, version, org_id=org_id)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"Package '{name}@{version}' not found")

    return _metadata_to_response(metadata, registry)


@router.get("/packages/{name}/versions", response_model=VersionsResponse)
async def get_package_versions(
    name: str,
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
) -> VersionsResponse:
    """Get all versions of a package."""
    if org_id is None:
        org_id = auth.org.id

    user_id = auth.user.id if auth.user else None
    if not registry.can_access(name, org_id, user_id, PackageAccess.READ):
        raise HTTPException(status_code=403, detail="Access denied to this package")

    versions = registry.get_versions(name, org_id)
    if not versions:
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")

    return VersionsResponse(
        name=name,
        versions=versions,
        latest=versions[0] if versions else "",
    )


@router.get("/packages/{name}/{version}/download")
async def download_package(
    name: str,
    version: str,
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
):
    """Download a package file."""
    if org_id is None:
        org_id = auth.org.id

    user_id = auth.user.id if auth.user else None
    if not registry.can_access(name, org_id, user_id, PackageAccess.READ):
        raise HTTPException(status_code=403, detail="Access denied to this package")

    pkg_path = registry.download_package(name, version, org_id, user_id)
    if not pkg_path:
        raise HTTPException(status_code=404, detail=f"Package '{name}@{version}' not found")

    return FileResponse(
        path=pkg_path,
        filename=f"{name}-{version}.fmpkg",
        media_type="application/octet-stream",
    )


@router.delete("/packages/{name}/{version}")
async def delete_package(
    name: str,
    version: str,
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
):
    """Delete a specific package version."""
    if org_id is None:
        org_id = auth.org.id

    user_id = auth.user.id if auth.user else None
    if not registry.can_access(name, org_id, user_id, PackageAccess.ADMIN):
        raise HTTPException(status_code=403, detail="Admin access required to delete packages")

    if not registry.delete_package(name, version, org_id):
        raise HTTPException(status_code=404, detail=f"Package '{name}@{version}' not found")

    return {"message": f"Package {name}@{version} deleted", "success": True}


# =============================================================================
# Access Control
# =============================================================================


@router.post("/packages/{name}/access")
async def grant_package_access(
    name: str,
    request: AccessGrantRequest,
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
):
    """Grant a user access to a package."""
    if org_id is None:
        org_id = auth.org.id

    # Check if requester has admin access
    user_id = auth.user.id if auth.user else None
    if not registry.can_access(name, org_id, user_id, PackageAccess.ADMIN):
        raise HTTPException(status_code=403, detail="Admin access required to manage permissions")

    try:
        access_level = PackageAccess(request.access_level)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid access level: {request.access_level}. Must be read, write, or admin"
        )

    if not registry.grant_access(name, org_id, request.user_id, access_level):
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")

    return {"message": f"Granted {request.access_level} access to user {request.user_id}"}


@router.delete("/packages/{name}/access/{user_id}")
async def revoke_package_access(
    name: str,
    user_id: str,
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
):
    """Revoke a user's access to a package."""
    if org_id is None:
        org_id = auth.org.id

    # Check if requester has admin access
    requester_id = auth.user.id if auth.user else None
    if not registry.can_access(name, org_id, requester_id, PackageAccess.ADMIN):
        raise HTTPException(status_code=403, detail="Admin access required to manage permissions")

    if not registry.revoke_access(name, org_id, user_id):
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")

    return {"message": f"Revoked access for user {user_id}"}


@router.patch("/packages/{name}/visibility")
async def set_package_visibility(
    name: str,
    request: VisibilityRequest,
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
):
    """Change package visibility."""
    if org_id is None:
        org_id = auth.org.id

    # Check if requester has admin access
    user_id = auth.user.id if auth.user else None
    if not registry.can_access(name, org_id, user_id, PackageAccess.ADMIN):
        raise HTTPException(status_code=403, detail="Admin access required to change visibility")

    try:
        visibility = PackageVisibility(request.visibility)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid visibility: {request.visibility}. Must be public, private, or unlisted"
        )

    if not registry.set_visibility(name, org_id, visibility):
        raise HTTPException(status_code=404, detail=f"Package '{name}' not found")

    return {"message": f"Package visibility set to {request.visibility}"}


# =============================================================================
# Statistics
# =============================================================================


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
) -> StatsResponse:
    """Get registry statistics for the organization."""
    if org_id is None:
        org_id = auth.org.id

    stats = registry.get_stats(org_id)
    return StatsResponse(**stats)


@router.get("/popular", response_model=List[PackageResponse])
async def get_popular_packages(
    limit: int = Query(10, ge=1, le=50),
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
) -> List[PackageResponse]:
    """Get most downloaded packages."""
    if org_id is None:
        org_id = auth.org.id

    packages = registry.get_popular_packages(limit, org_id)
    return [_metadata_to_response(p, registry) for p in packages]


@router.get("/categories")
async def list_categories(
    org_id: Optional[str] = Query(None),
    auth: AuthContext = Depends(require_auth),
    registry: PackageRegistry = Depends(get_package_registry),
) -> List[str]:
    """List all package categories."""
    if org_id is None:
        org_id = auth.org.id

    packages = registry.list_packages(org_id=org_id, include_private=True, user_id=auth.user.id if auth.user else None)
    categories = set()
    for pkg in packages:
        if pkg.category:
            categories.add(pkg.category)

    return sorted(categories)
