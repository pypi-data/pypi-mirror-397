"""
Settings API Routes.

Manages application settings including provider API keys.
"""

import os
import signal
from typing import Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from flowmason_core.providers import get_provider, list_providers
from pydantic import BaseModel, Field

from flowmason_studio.services.settings import (
    get_settings_service,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


# Request/Response Models
class ProviderKeyRequest(BaseModel):
    """Request to set a provider API key."""
    api_key: str = Field(..., description="The API key to store")
    default_model: Optional[str] = Field(None, description="Default model for this provider")


class ProviderSettingsResponse(BaseModel):
    """Response with provider settings (key masked)."""
    provider: str
    has_key: bool
    key_preview: str = ""  # Last 4 chars if set
    default_model: Optional[str] = None
    enabled: bool = True
    available_models: List[str] = []


class AppSettingsResponse(BaseModel):
    """Response with full app settings."""
    default_provider: str
    theme: str
    auto_save: bool
    providers: Dict[str, ProviderSettingsResponse]


class AppSettingsUpdateRequest(BaseModel):
    """Request to update app settings."""
    default_provider: Optional[str] = None
    theme: Optional[str] = None
    auto_save: Optional[bool] = None


class ProviderTestResponse(BaseModel):
    """Response from testing a provider."""
    provider: str
    success: bool
    message: str
    model_tested: Optional[str] = None


# Routes

@router.get("", response_model=AppSettingsResponse)
def get_settings():
    """Get current application settings."""
    service = get_settings_service()
    settings = service.get_settings()

    # Build provider responses with masked keys
    provider_responses = {}
    for provider_name in list_providers():
        prov_settings = settings.providers.get(provider_name)

        # Get available models for this provider
        try:
            ProviderClass = get_provider(provider_name)
            available_models = list(ProviderClass.available_models) if hasattr(ProviderClass, 'available_models') else []
        except Exception:
            available_models = []

        if prov_settings and prov_settings.api_key:
            key_preview = f"...{prov_settings.api_key[-4:]}" if len(prov_settings.api_key) >= 4 else "****"
            provider_responses[provider_name] = ProviderSettingsResponse(
                provider=provider_name,
                has_key=True,
                key_preview=key_preview,
                default_model=prov_settings.default_model,
                enabled=prov_settings.enabled,
                available_models=available_models,
            )
        else:
            provider_responses[provider_name] = ProviderSettingsResponse(
                provider=provider_name,
                has_key=False,
                key_preview="",
                default_model=None,
                enabled=True,
                available_models=available_models,
            )

    return AppSettingsResponse(
        default_provider=settings.default_provider,
        theme=settings.theme,
        auto_save=settings.auto_save,
        providers=provider_responses,
    )


@router.put("", response_model=AppSettingsResponse)
def update_settings(request: AppSettingsUpdateRequest):
    """Update application settings."""
    service = get_settings_service()

    service.update_settings(
        default_provider=request.default_provider,
        theme=request.theme,
        auto_save=request.auto_save,
    )

    # Return updated settings
    return get_settings()


@router.get("/providers/{provider_name}", response_model=ProviderSettingsResponse)
def get_provider_settings(provider_name: str):
    """Get settings for a specific provider."""
    if provider_name not in list_providers():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    service = get_settings_service()
    prov_settings = service.get_provider_settings(provider_name)

    # Get available models
    try:
        ProviderClass = get_provider(provider_name)
        available_models = list(ProviderClass.available_models) if ProviderClass and hasattr(ProviderClass, 'available_models') else []
    except Exception:
        available_models = []

    if prov_settings and prov_settings.api_key:
        key_preview = f"...{prov_settings.api_key[-4:]}" if len(prov_settings.api_key) >= 4 else "****"
        return ProviderSettingsResponse(
            provider=provider_name,
            has_key=True,
            key_preview=key_preview,
            default_model=prov_settings.default_model,
            enabled=prov_settings.enabled,
            available_models=available_models,
        )

    return ProviderSettingsResponse(
        provider=provider_name,
        has_key=False,
        key_preview="",
        default_model=None,
        enabled=True,
        available_models=available_models,
    )


@router.put("/providers/{provider_name}/key", response_model=ProviderSettingsResponse)
def set_provider_key(provider_name: str, request: ProviderKeyRequest):
    """Set API key for a provider."""
    if provider_name not in list_providers():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    service = get_settings_service()
    service.set_provider_api_key(
        provider_name=provider_name,
        api_key=request.api_key,
        default_model=request.default_model,
    )

    # Also set in environment for current session
    env_var_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
    }
    env_var = env_var_map.get(provider_name)
    if env_var:
        os.environ[env_var] = request.api_key

    return get_provider_settings(provider_name)


@router.delete("/providers/{provider_name}/key")
def remove_provider_key(provider_name: str):
    """Remove API key for a provider."""
    if provider_name not in list_providers():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    service = get_settings_service()
    removed = service.remove_provider_api_key(provider_name)

    # Also remove from environment
    env_var_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
    }
    env_var = env_var_map.get(provider_name)
    if env_var and env_var in os.environ:
        del os.environ[env_var]

    return {"removed": removed, "provider": provider_name}


@router.put("/providers/{provider_name}/enabled")
def set_provider_enabled(provider_name: str, enabled: bool):
    """Enable or disable a provider."""
    if provider_name not in list_providers():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    service = get_settings_service()
    result = service.set_provider_enabled(provider_name, enabled)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{provider_name}' has no stored settings"
        )

    return {"provider": provider_name, "enabled": enabled}


@router.post("/providers/{provider_name}/test", response_model=ProviderTestResponse)
async def test_provider(provider_name: str):
    """Test a provider's connection and API key."""
    if provider_name not in list_providers():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found"
        )

    # First check if we have a key
    service = get_settings_service()
    prov_settings = service.get_provider_settings(provider_name)

    # Also check environment
    env_var_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
    }
    env_var = env_var_map.get(provider_name)
    env_key = os.environ.get(env_var, "") if env_var else ""

    api_key = None
    if prov_settings and prov_settings.api_key:
        api_key = prov_settings.api_key
    elif env_key:
        api_key = env_key

    if not api_key:
        return ProviderTestResponse(
            provider=provider_name,
            success=False,
            message="No API key configured for this provider",
        )

    # Try to create provider and make a simple call
    try:
        ProviderClass = get_provider(provider_name)
        if not ProviderClass:
            raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")
        provider_instance = ProviderClass(api_key=api_key)

        # Make a minimal test call
        response = await provider_instance.call_async(
            prompt="Say 'hello' in one word.",
            max_tokens=10,
            temperature=0,
        )

        return ProviderTestResponse(
            provider=provider_name,
            success=True,
            message=f"Successfully connected. Response: {response.content[:50]}",
            model_tested=response.model,
        )
    except Exception as e:
        return ProviderTestResponse(
            provider=provider_name,
            success=False,
            message=f"Connection failed: {str(e)}",
        )


@router.post("/apply-to-environment")
def apply_settings_to_environment():
    """Apply saved API keys to environment variables for the current session."""
    service = get_settings_service()
    applied = service.apply_to_environment()

    return {
        "applied": applied,
        "message": f"Applied {len(applied)} API key(s) to environment"
    }


def _do_restart():
    """Perform the actual restart after a short delay."""
    import time
    time.sleep(0.5)  # Give time for response to be sent
    os.kill(os.getpid(), signal.SIGHUP)


@router.post("/restart")
def restart_backend(background_tasks: BackgroundTasks):
    """
    Restart the backend server.

    This triggers a graceful restart of the uvicorn server by sending SIGHUP.
    The server will reload all modules and configurations.

    Note: This only works when running with uvicorn in reload mode or
    when the process is managed by a supervisor that handles SIGHUP.
    """
    background_tasks.add_task(_do_restart)
    return {
        "message": "Backend restart initiated. The server will restart momentarily.",
        "status": "restarting"
    }
