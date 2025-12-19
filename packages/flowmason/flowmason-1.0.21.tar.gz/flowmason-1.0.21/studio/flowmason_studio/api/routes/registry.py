"""
Registry API Routes.

Endpoints for managing the component registry:
- List available components
- Get component details
- Deploy packages
- Unregister components
"""

import shutil
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from flowmason_core.registry import ComponentNotFoundError, ComponentRegistry, PackageLoadError

from flowmason_studio.auth import AuthContext, get_auth_service, optional_auth
from flowmason_studio.models.api import (
    AIConfig,
    APIError,
    ComponentDetail,
    ComponentKind,
    ComponentListResponse,
    ComponentSummary,
    ControlFlowType,
    DeployPackageResponse,
    PackageListResponse,
    PackageSummary,
)

router = APIRouter(prefix="/registry", tags=["registry"])


# Global registry instance (will be set by app startup)
_registry: Optional[ComponentRegistry] = None


def get_registry() -> ComponentRegistry:
    """Dependency to get the component registry."""
    if _registry is None:
        raise HTTPException(
            status_code=503,
            detail="Component registry not initialized"
        )
    return _registry


def set_registry(registry: ComponentRegistry) -> None:
    """Set the global registry instance (called during app startup)."""
    global _registry
    _registry = registry


@router.get(
    "/components",
    response_model=ComponentListResponse,
    summary="List all available components",
    description="Returns a list of all registered components with optional filtering."
)
async def list_components(
    category: Optional[str] = Query(None, description="Filter by category"),
    kind: Optional[ComponentKind] = Query(None, description="Filter by kind (node/operator)"),
    registry: ComponentRegistry = Depends(get_registry)
) -> ComponentListResponse:
    """List all available components."""
    # Get all components
    components = registry.list_components(category=category)

    # Filter by kind if specified
    if kind:
        components = [c for c in components if c.component_kind == kind.value]

    # Convert to API models
    summaries = []
    for comp in components:
        # Parse control_flow_type if present
        cf_type = None
        if comp.control_flow_type:
            try:
                cf_type = ControlFlowType(comp.control_flow_type)
            except ValueError:
                cf_type = None

        summaries.append(ComponentSummary(
            component_type=comp.component_type,
            component_kind=ComponentKind(comp.component_kind),
            name=comp.component_type,  # Use type as name
            category=comp.category,
            description=comp.description,
            version=comp.version,
            package_name=comp.package_name or "unknown",
            icon=comp.icon,
            color=comp.color,
            # Include schema and LLM info for StageConfigPanel
            input_schema=comp.input_schema,
            output_schema=comp.output_schema,
            requires_llm=comp.requires_llm,
            # Control flow specific
            control_flow_type=cf_type,
        ))

    # Get unique categories
    categories = list(registry.get_categories())

    return ComponentListResponse(
        components=summaries,
        total=len(summaries),
        categories=categories,
    )


@router.get(
    "/components/{component_type}",
    response_model=ComponentDetail,
    summary="Get component details",
    description="Returns detailed information about a specific component.",
    responses={404: {"model": APIError}}
)
async def get_component(
    component_type: str,
    registry: ComponentRegistry = Depends(get_registry)
) -> ComponentDetail:
    """Get detailed information about a component."""
    try:
        metadata = registry.get_component_metadata(component_type)
    except ComponentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Component '{component_type}' not found"
        )

    # Parse control_flow_type if present
    cf_type = None
    if metadata.control_flow_type:
        try:
            cf_type = ControlFlowType(metadata.control_flow_type)
        except ValueError:
            cf_type = None

    # Build AI config if component requires LLM
    ai_config = None
    if metadata.requires_llm and metadata.recommended_providers:
        ai_config = AIConfig(
            recommended_providers=metadata.recommended_providers,
            default_provider=metadata.default_provider,
            required_capabilities=metadata.required_capabilities,
            min_context_window=getattr(metadata, 'min_context_window', None),
            require_vision=getattr(metadata, 'require_vision', False),
            require_function_calling=getattr(metadata, 'require_function_calling', False),
        )

    return ComponentDetail(
        component_type=metadata.component_type,
        component_kind=ComponentKind(metadata.component_kind),
        name=metadata.component_type,
        category=metadata.category,
        description=metadata.description,
        version=metadata.version,
        package_name=metadata.package_name or "unknown",
        icon=metadata.icon,
        color=metadata.color,
        input_schema=metadata.input_schema,
        output_schema=metadata.output_schema,
        author=metadata.author,
        tags=metadata.tags,
        requires_llm=metadata.requires_llm,
        # Full AI configuration
        ai_config=ai_config,
        # Backwards compatible fields
        recommended_providers=(
            list(metadata.recommended_providers.keys())
            if metadata.recommended_providers else None
        ),
        default_provider=metadata.default_provider,
        package_version=metadata.package_version or metadata.version,
        control_flow_type=cf_type,
        # Runtime config
        timeout_seconds=getattr(metadata, 'timeout_seconds', 60),
        max_retries=getattr(metadata, 'max_retries', 3),
        supports_streaming=getattr(metadata, 'supports_streaming', False),
    )


@router.get(
    "/packages",
    response_model=PackageListResponse,
    summary="List all packages",
    description="Returns a list of all registered packages."
)
async def list_packages(
    registry: ComponentRegistry = Depends(get_registry)
) -> PackageListResponse:
    """List all registered packages."""
    packages = registry.list_packages()

    summaries = []
    for pkg in packages:
        summaries.append(PackageSummary(
            name=pkg.name,
            version=pkg.version,
            description=pkg.description or "",
            component_count=len(pkg.components),
            components=list(pkg.components),  # components is already a list of str
        ))

    return PackageListResponse(
        packages=summaries,
        total=len(summaries),
    )


@router.post(
    "/deploy",
    response_model=DeployPackageResponse,
    summary="Deploy a package",
    description="Upload and register a .fmpkg package file.",
    responses={400: {"model": APIError}}
)
async def deploy_package(
    file: UploadFile = File(..., description="The .fmpkg package file"),
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> DeployPackageResponse:
    """Deploy a package to the registry."""
    if not file.filename or not file.filename.endswith(".fmpkg"):
        raise HTTPException(
            status_code=400,
            detail="File must be a .fmpkg package"
        )

    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(suffix=".fmpkg", delete=False) as tmp:
        try:
            shutil.copyfileobj(file.file, tmp)  # type: ignore[misc]
            tmp_path = tmp.name
        finally:
            file.file.close()

    try:
        # Register the package
        pkg_info = registry.register_package(tmp_path)

        # Audit log if authenticated
        if auth:
            auth_service = get_auth_service()
            auth_service.log_action(
                org_id=auth.org.id,
                action="package.deploy",
                resource_type="package",
                resource_id=pkg_info.name,
                api_key_id=auth.api_key.id if auth.api_key else None,
                user_id=auth.user.id if auth.user else None,
                details={
                    "filename": file.filename,
                    "version": pkg_info.version,
                    "components": list(pkg_info.components),
                },
                ip_address=auth.ip_address,
                user_agent=auth.user_agent,
            )

        return DeployPackageResponse(
            package_name=pkg_info.name,
            package_version=pkg_info.version,
            components_registered=list(pkg_info.components),
            message=f"Successfully deployed {pkg_info.name}@{pkg_info.version}",
        )

    except PackageLoadError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load package: {str(e)}"
        )
    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)


@router.delete(
    "/components/{component_type}",
    summary="Unregister a component",
    description="Remove a component from the registry.",
    responses={404: {"model": APIError}}
)
async def unregister_component(
    component_type: str,
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> dict:
    """Unregister a component (by unregistering its package)."""
    try:
        metadata = registry.get_component_metadata(component_type)
    except ComponentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Component '{component_type}' not found"
        )

    package_name = metadata.package_name
    if not package_name:
        raise HTTPException(
            status_code=400,
            detail="Cannot determine package for component"
        )

    success = registry.unregister_package(package_name)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Package '{package_name}' not found"
        )

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="package.unregister",
            resource_type="package",
            resource_id=package_name,
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={"component_type": component_type},
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    return {"message": f"Successfully unregistered package '{package_name}'"}


@router.post(
    "/refresh",
    summary="Refresh the registry",
    description="Rescan the packages directory and reload all components."
)
async def refresh_registry(
    registry: ComponentRegistry = Depends(get_registry),
    auth: Optional[AuthContext] = Depends(optional_auth),
) -> dict:
    """Refresh the registry by rescanning packages."""
    count = registry.refresh()
    stats = registry.get_stats()

    # Audit log if authenticated
    if auth:
        auth_service = get_auth_service()
        auth_service.log_action(
            org_id=auth.org.id,
            action="registry.refresh",
            resource_type="registry",
            api_key_id=auth.api_key.id if auth.api_key else None,
            user_id=auth.user.id if auth.user else None,
            details={
                "packages_loaded": count,
                "total_components": stats["total_components"],
            },
            ip_address=auth.ip_address,
            user_agent=auth.user_agent,
        )

    return {
        "message": "Registry refreshed",
        "packages_loaded": count,
        "total_components": stats["total_components"],
        "total_nodes": stats["total_nodes"],
        "total_operators": stats["total_operators"],
    }


@router.get(
    "/stats",
    summary="Get registry statistics",
    description="Returns statistics about the component registry."
)
async def get_stats(
    registry: ComponentRegistry = Depends(get_registry)
) -> dict:
    """Get registry statistics."""
    return registry.get_stats()
