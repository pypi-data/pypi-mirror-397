"""
Providers API Routes.

Endpoints for managing LLM providers:
- List available providers
- Get provider details and models
- Test provider connections
"""

import os
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from flowmason_core.providers import (
    ProviderCapability,
    get_provider,
    list_providers,
)
from pydantic import BaseModel

router = APIRouter(prefix="/providers", tags=["providers"])


class ProviderSummary(BaseModel):
    """Summary information about a provider."""
    name: str
    default_model: str
    available_models: list[str]
    capabilities: list[str]
    configured: bool  # Whether API key is set


class ProviderListResponse(BaseModel):
    """Response for listing providers."""
    providers: list[ProviderSummary]
    total: int


class ProviderModelsResponse(BaseModel):
    """Response for listing provider models."""
    provider: str
    models: list[str]
    default_model: str


class ProviderTestRequest(BaseModel):
    """Request to test a provider."""
    api_key: Optional[str] = None  # Optional override, otherwise uses env var


class ProviderTestResponse(BaseModel):
    """Response from testing a provider."""
    success: bool
    provider: str
    model: str
    message: str
    duration_ms: Optional[int] = None


@router.get(
    "",
    response_model=ProviderListResponse,
    summary="List available providers",
    description="Returns a list of all registered LLM providers."
)
async def list_available_providers() -> ProviderListResponse:
    """List all available LLM providers."""
    provider_names = list_providers()
    summaries = []

    for name in provider_names:
        provider_class = get_provider(name)
        if not provider_class:
            continue

        # Get provider info without instantiating (need API key for that)
        # Create a temporary instance-like object to access class properties
        try:
            temp: Any = object.__new__(provider_class)
            temp.api_key = "temp"
            temp.model = None
            temp.timeout = 120
            temp.max_retries = 3
            temp.pricing = getattr(provider_class, "DEFAULT_PRICING", {})
            temp.extra_config = {}

            # Check if API key is configured
            env_var = f"{name.upper()}_API_KEY"
            configured = bool(os.environ.get(env_var))

            summaries.append(ProviderSummary(
                name=temp.name,
                default_model=temp.default_model,
                available_models=temp.available_models,
                capabilities=[c.value for c in temp.capabilities],
                configured=configured,
            ))
        except Exception:
            # Skip providers that can't be introspected
            continue

    return ProviderListResponse(
        providers=summaries,
        total=len(summaries),
    )


@router.get(
    "/{provider_name}/models",
    response_model=ProviderModelsResponse,
    summary="List provider models",
    description="Returns available models for a specific provider."
)
async def get_provider_models(provider_name: str) -> ProviderModelsResponse:
    """Get available models for a provider."""
    provider_class = get_provider(provider_name)
    if not provider_class:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_name}' not found"
        )

    try:
        temp: Any = object.__new__(provider_class)
        temp.api_key = "temp"
        temp.model = None
        temp.timeout = 120
        temp.max_retries = 3
        temp.pricing = getattr(provider_class, "DEFAULT_PRICING", {})
        temp.extra_config = {}

        return ProviderModelsResponse(
            provider=provider_name,
            models=temp.available_models,
            default_model=temp.default_model,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get models: {str(e)}"
        )


@router.post(
    "/{provider_name}/test",
    response_model=ProviderTestResponse,
    summary="Test provider connection",
    description="Test that a provider is properly configured and working."
)
async def test_provider(
    provider_name: str,
    request: ProviderTestRequest
) -> ProviderTestResponse:
    """Test a provider connection with a simple prompt."""
    provider_class = get_provider(provider_name)
    if not provider_class:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_name}' not found"
        )

    # Get API key from request or environment
    env_var = f"{provider_name.upper()}_API_KEY"
    api_key = request.api_key or os.environ.get(env_var)

    if not api_key:
        return ProviderTestResponse(
            success=False,
            provider=provider_name,
            model="",
            message=f"No API key provided. Set {env_var} environment variable or pass api_key in request.",
        )

    try:
        # Create provider instance
        provider = provider_class(api_key=api_key)

        # Make a simple test call
        response = await provider.call_async(
            prompt="Say 'Hello FlowMason!' in exactly those words.",
            max_tokens=50,
            temperature=0,
        )

        if response.success:
            return ProviderTestResponse(
                success=True,
                provider=provider_name,
                model=response.model,
                message=f"Connection successful. Response: {response.content[:100]}",
                duration_ms=response.duration_ms,
            )
        else:
            return ProviderTestResponse(
                success=False,
                provider=provider_name,
                model=response.model or provider.default_model,
                message=f"Provider returned error: {response.error}",
            )

    except Exception as e:
        return ProviderTestResponse(
            success=False,
            provider=provider_name,
            model="",
            message=f"Test failed: {str(e)}",
        )


@router.get(
    "/capabilities",
    summary="List all provider capabilities",
    description="Returns all possible provider capabilities."
)
async def list_capabilities() -> dict:
    """List all possible provider capabilities."""
    return {
        "capabilities": [c.value for c in ProviderCapability],
        "descriptions": {
            ProviderCapability.TEXT_GENERATION.value: "Generate text responses",
            ProviderCapability.STREAMING.value: "Stream responses token by token",
            ProviderCapability.FUNCTION_CALLING.value: "Call functions/tools",
            ProviderCapability.VISION.value: "Process images",
            ProviderCapability.EMBEDDINGS.value: "Generate embeddings",
            ProviderCapability.CODE_EXECUTION.value: "Execute code",
        }
    }
