"""
FlowMason Webhook Triggers API Routes.

Endpoints for managing webhook triggers and receiving webhook calls.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from flowmason_core.registry import ComponentRegistry
from pydantic import BaseModel, Field

from ...auth import AuthContext, get_auth_service, require_auth, require_scope
from ...auth.models import APIKeyScope
from ...services.storage import PipelineStorage, RunStorage, get_pipeline_storage, get_run_storage
from ...services.webhook_storage import (
    WebhookStorage,
    WebhookTrigger,
    get_webhook_storage,
)
from ..routes.registry import get_registry

logger = logging.getLogger(__name__)


# =============================================================================
# Routers
# =============================================================================

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
trigger_router = APIRouter(tags=["webhook-triggers"])


# =============================================================================
# Request/Response Models
# =============================================================================


class CreateWebhookRequest(BaseModel):
    """Request to create a webhook trigger."""
    name: str = Field(description="Display name for the webhook")
    pipeline_id: str = Field(description="Pipeline ID to trigger")
    input_mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Maps webhook payload fields to pipeline inputs (e.g., {'data.user_id': 'user_id'})"
    )
    default_inputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default values for pipeline inputs"
    )
    require_auth: bool = Field(
        default=True,
        description="Require authentication for webhook calls"
    )
    auth_header: Optional[str] = Field(
        default="X-Webhook-Secret",
        description="Header name for authentication secret"
    )
    auth_secret: Optional[str] = Field(
        default=None,
        description="Secret value for authentication (will be hashed)"
    )
    async_mode: bool = Field(
        default=True,
        description="Return immediately (true) or wait for pipeline completion (false)"
    )
    description: str = Field(
        default="",
        description="Description of the webhook"
    )


class UpdateWebhookRequest(BaseModel):
    """Request to update a webhook trigger."""
    name: Optional[str] = None
    input_mapping: Optional[Dict[str, str]] = None
    default_inputs: Optional[Dict[str, Any]] = None
    require_auth: Optional[bool] = None
    auth_header: Optional[str] = None
    auth_secret: Optional[str] = None
    enabled: Optional[bool] = None
    async_mode: Optional[bool] = None
    description: Optional[str] = None


class WebhookResponse(BaseModel):
    """Response for webhook operations."""
    id: str
    name: str
    pipeline_id: str
    pipeline_name: str
    webhook_url: str  # Full URL for the webhook
    enabled: bool
    require_auth: bool
    auth_header: Optional[str]
    async_mode: bool
    description: str
    input_mapping: Dict[str, str]
    default_inputs: Dict[str, Any]
    created_at: str
    updated_at: str
    last_triggered_at: Optional[str]
    trigger_count: int


class WebhookListResponse(BaseModel):
    """Response for listing webhooks."""
    webhooks: List[WebhookResponse]
    total: int


class WebhookInvocationResponse(BaseModel):
    """Response for webhook invocation."""
    id: str
    webhook_id: str
    run_id: Optional[str]
    status: str
    error_message: Optional[str]
    invoked_at: str


class TriggerResponse(BaseModel):
    """Response when a webhook is triggered."""
    status: str
    message: str
    run_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


# =============================================================================
# Helper Functions
# =============================================================================


def _build_webhook_url(request: Request, token: str) -> str:
    """Build the full webhook URL."""
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/api/v1/webhook/{token}"


def _webhook_to_response(webhook: WebhookTrigger, request: Request) -> WebhookResponse:
    """Convert a WebhookTrigger to a WebhookResponse."""
    return WebhookResponse(
        id=webhook.id,
        name=webhook.name,
        pipeline_id=webhook.pipeline_id,
        pipeline_name=webhook.pipeline_name,
        webhook_url=_build_webhook_url(request, webhook.webhook_token),
        enabled=webhook.enabled,
        require_auth=webhook.require_auth,
        auth_header=webhook.auth_header,
        async_mode=webhook.async_mode,
        description=webhook.description,
        input_mapping=webhook.input_mapping,
        default_inputs=webhook.default_inputs,
        created_at=webhook.created_at,
        updated_at=webhook.updated_at,
        last_triggered_at=webhook.last_triggered_at,
        trigger_count=webhook.trigger_count,
    )


def _extract_nested_value(data: Dict, path: str) -> Any:
    """Extract a value from nested dict using dot notation.

    Example: _extract_nested_value({"data": {"user": {"id": 1}}}, "data.user.id") -> 1
    """
    keys = path.split(".")
    value = data

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None

    return value


def _map_inputs(
    payload: Dict[str, Any],
    input_mapping: Dict[str, str],
    default_inputs: Dict[str, Any],
) -> Dict[str, Any]:
    """Map webhook payload to pipeline inputs."""
    result = dict(default_inputs)  # Start with defaults

    # Apply mappings
    for source_path, target_key in input_mapping.items():
        value = _extract_nested_value(payload, source_path)
        if value is not None:
            result[target_key] = value

    # Also include any top-level keys from payload not in mapping
    # This allows simple payloads to work without explicit mapping
    if not input_mapping:
        result.update(payload)

    return result


# =============================================================================
# Webhook Management Endpoints
# =============================================================================


@router.post("", response_model=WebhookResponse, status_code=201)
async def create_webhook(
    request_data: CreateWebhookRequest,
    request: Request,
    auth: AuthContext = Depends(require_scope(APIKeyScope.FULL)),
    webhook_storage: WebhookStorage = Depends(get_webhook_storage),
    pipeline_storage: PipelineStorage = Depends(get_pipeline_storage),
) -> WebhookResponse:
    """
    Create a new webhook trigger for a pipeline.

    The returned webhook_url can be used to trigger the pipeline via HTTP POST.
    """
    # Verify pipeline exists
    pipeline = pipeline_storage.get(request_data.pipeline_id, org_id=auth.org.id)
    if not pipeline:
        raise HTTPException(status_code=404, detail=f"Pipeline '{request_data.pipeline_id}' not found")

    # Create webhook
    webhook = webhook_storage.create(
        name=request_data.name,
        pipeline_id=request_data.pipeline_id,
        pipeline_name=pipeline.name,
        org_id=auth.org.id,
        input_mapping=request_data.input_mapping,
        default_inputs=request_data.default_inputs,
        require_auth=request_data.require_auth,
        auth_header=request_data.auth_header,
        auth_secret=request_data.auth_secret,
        async_mode=request_data.async_mode,
        description=request_data.description,
    )

    # Audit log
    auth_service = get_auth_service()
    auth_service.log_action(
        org_id=auth.org.id,
        action="webhook.create",
        resource_type="webhook",
        resource_id=webhook.id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        user_id=auth.user.id if auth.user else None,
        details={"name": webhook.name, "pipeline_id": request_data.pipeline_id},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )

    return _webhook_to_response(webhook, request)


@router.get("", response_model=WebhookListResponse)
async def list_webhooks(
    request: Request,
    pipeline_id: Optional[str] = None,
    enabled_only: bool = False,
    limit: int = 100,
    offset: int = 0,
    auth: AuthContext = Depends(require_auth),
    webhook_storage: WebhookStorage = Depends(get_webhook_storage),
) -> WebhookListResponse:
    """List all webhooks for the organization."""
    webhooks, total = webhook_storage.list(
        org_id=auth.org.id,
        pipeline_id=pipeline_id,
        enabled_only=enabled_only,
        limit=limit,
        offset=offset,
    )

    return WebhookListResponse(
        webhooks=[_webhook_to_response(w, request) for w in webhooks],
        total=total,
    )


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    request: Request,
    auth: AuthContext = Depends(require_auth),
    webhook_storage: WebhookStorage = Depends(get_webhook_storage),
) -> WebhookResponse:
    """Get a webhook by ID."""
    webhook = webhook_storage.get(webhook_id, org_id=auth.org.id)
    if not webhook:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")

    return _webhook_to_response(webhook, request)


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    request_data: UpdateWebhookRequest,
    request: Request,
    auth: AuthContext = Depends(require_scope(APIKeyScope.FULL)),
    webhook_storage: WebhookStorage = Depends(get_webhook_storage),
) -> WebhookResponse:
    """Update a webhook."""
    webhook = webhook_storage.update(
        webhook_id=webhook_id,
        org_id=auth.org.id,
        name=request_data.name,
        input_mapping=request_data.input_mapping,
        default_inputs=request_data.default_inputs,
        require_auth=request_data.require_auth,
        auth_header=request_data.auth_header,
        auth_secret=request_data.auth_secret,
        enabled=request_data.enabled,
        async_mode=request_data.async_mode,
        description=request_data.description,
    )

    if not webhook:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")

    # Audit log
    auth_service = get_auth_service()
    auth_service.log_action(
        org_id=auth.org.id,
        action="webhook.update",
        resource_type="webhook",
        resource_id=webhook_id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        user_id=auth.user.id if auth.user else None,
        details={"name": webhook.name},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )

    return _webhook_to_response(webhook, request)


@router.delete("/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: str,
    auth: AuthContext = Depends(require_scope(APIKeyScope.FULL)),
    webhook_storage: WebhookStorage = Depends(get_webhook_storage),
) -> None:
    """Delete a webhook."""
    # Get webhook info before deletion
    webhook = webhook_storage.get(webhook_id, org_id=auth.org.id)
    if not webhook:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")

    success = webhook_storage.delete(webhook_id, org_id=auth.org.id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")

    # Audit log
    auth_service = get_auth_service()
    auth_service.log_action(
        org_id=auth.org.id,
        action="webhook.delete",
        resource_type="webhook",
        resource_id=webhook_id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        user_id=auth.user.id if auth.user else None,
        details={"name": webhook.name, "pipeline_id": webhook.pipeline_id},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )


@router.post("/{webhook_id}/regenerate-token", response_model=WebhookResponse)
async def regenerate_webhook_token(
    webhook_id: str,
    request: Request,
    auth: AuthContext = Depends(require_scope(APIKeyScope.FULL)),
    webhook_storage: WebhookStorage = Depends(get_webhook_storage),
) -> WebhookResponse:
    """Regenerate the webhook token (invalidates old URL)."""
    new_token = webhook_storage.regenerate_token(webhook_id, org_id=auth.org.id)
    if not new_token:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")

    webhook = webhook_storage.get(webhook_id, org_id=auth.org.id)

    # Audit log
    auth_service = get_auth_service()
    auth_service.log_action(
        org_id=auth.org.id,
        action="webhook.regenerate_token",
        resource_type="webhook",
        resource_id=webhook_id,
        api_key_id=auth.api_key.id if auth.api_key else None,
        user_id=auth.user.id if auth.user else None,
        details={"name": webhook.name if webhook else webhook_id},
        ip_address=auth.ip_address,
        user_agent=auth.user_agent,
    )

    return _webhook_to_response(webhook, request)  # type: ignore[arg-type]


@router.get("/{webhook_id}/invocations", response_model=List[WebhookInvocationResponse])
async def get_webhook_invocations(
    webhook_id: str,
    limit: int = 100,
    offset: int = 0,
    auth: AuthContext = Depends(require_auth),
    webhook_storage: WebhookStorage = Depends(get_webhook_storage),
) -> List[WebhookInvocationResponse]:
    """Get invocation history for a webhook."""
    # Verify webhook belongs to org
    webhook = webhook_storage.get(webhook_id, org_id=auth.org.id)
    if not webhook:
        raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")

    invocations = webhook_storage.get_invocations(webhook_id, limit=limit, offset=offset)

    return [
        WebhookInvocationResponse(
            id=inv.id,
            webhook_id=inv.webhook_id,
            run_id=inv.run_id,
            status=inv.status,
            error_message=inv.error_message,
            invoked_at=inv.invoked_at,
        )
        for inv in invocations
    ]


# =============================================================================
# Webhook Trigger Endpoint (Public)
# =============================================================================


@trigger_router.post("/webhook/{token}", response_model=TriggerResponse)
@trigger_router.get("/webhook/{token}", response_model=TriggerResponse)
async def trigger_webhook(
    token: str,
    request: Request,
    background_tasks: BackgroundTasks,
    webhook_storage: WebhookStorage = Depends(get_webhook_storage),
    pipeline_storage: PipelineStorage = Depends(get_pipeline_storage),
    run_storage: RunStorage = Depends(get_run_storage),
    registry: ComponentRegistry = Depends(get_registry),
) -> TriggerResponse:
    """
    Trigger a pipeline via webhook.

    This endpoint is public but may require authentication via the configured auth header.

    For POST requests, the request body is used as the webhook payload.
    For GET requests, query parameters are used as the webhook payload.
    """
    # Get client info
    source_ip = request.client.host if request.client else None
    request_headers = dict(request.headers)

    # Look up webhook by token
    webhook = webhook_storage.get_by_token(token)
    if not webhook:
        return TriggerResponse(
            status="error",
            message="Invalid webhook token",
            error="Webhook not found",
        )

    # Check if enabled
    if not webhook.enabled:
        webhook_storage.log_invocation(
            webhook_id=webhook.id,
            run_id=None,
            request_method=request.method,
            request_headers=request_headers,
            request_body=None,
            source_ip=source_ip,
            status="rejected",
            error_message="Webhook is disabled",
            response_code=403,
        )
        raise HTTPException(status_code=403, detail="Webhook is disabled")

    # Verify authentication
    if webhook.require_auth:
        auth_header = webhook.auth_header or "X-Webhook-Secret"
        auth_value = request.headers.get(auth_header)

        if not webhook_storage.verify_auth(webhook, auth_value):
            webhook_storage.log_invocation(
                webhook_id=webhook.id,
                run_id=None,
                request_method=request.method,
                request_headers=request_headers,
                request_body=None,
                source_ip=source_ip,
                status="rejected",
                error_message="Authentication failed",
                response_code=401,
            )
            raise HTTPException(status_code=401, detail="Authentication required")

    # Get payload
    try:
        if request.method == "POST":
            body = await request.body()
            request_body = body.decode("utf-8") if body else "{}"
            payload = json.loads(request_body) if request_body else {}
        else:
            # GET request - use query params
            request_body = None
            payload = dict(request.query_params)
    except json.JSONDecodeError:
        webhook_storage.log_invocation(
            webhook_id=webhook.id,
            run_id=None,
            request_method=request.method,
            request_headers=request_headers,
            request_body=request_body,
            source_ip=source_ip,
            status="error",
            error_message="Invalid JSON payload",
            response_code=400,
        )
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Map inputs
    pipeline_inputs = _map_inputs(payload, webhook.input_mapping, webhook.default_inputs)

    # Get pipeline
    pipeline = pipeline_storage.get(webhook.pipeline_id, org_id=webhook.org_id)
    if not pipeline:
        webhook_storage.log_invocation(
            webhook_id=webhook.id,
            run_id=None,
            request_method=request.method,
            request_headers=request_headers,
            request_body=request_body,
            source_ip=source_ip,
            status="error",
            error_message=f"Pipeline '{webhook.pipeline_id}' not found",
            response_code=404,
        )
        raise HTTPException(status_code=404, detail=f"Pipeline '{webhook.pipeline_id}' not found")

    # Create run
    run = run_storage.create(
        pipeline_id=webhook.pipeline_id,
        inputs=pipeline_inputs,
        org_id=webhook.org_id,
    )

    # Update webhook stats
    webhook_storage.increment_trigger_count(webhook.id)

    # Import execution task
    from .execution import _execute_pipeline_task

    if webhook.async_mode:
        # Async mode - schedule background execution
        background_tasks.add_task(
            _execute_pipeline_task,
            run.id,
            pipeline,
            pipeline_inputs,
            registry,
            run_storage,
            None,  # breakpoints
            webhook.org_id,
        )

        # Log successful invocation
        webhook_storage.log_invocation(
            webhook_id=webhook.id,
            run_id=run.id,
            request_method=request.method,
            request_headers=request_headers,
            request_body=request_body,
            source_ip=source_ip,
            status="success",
            response_code=202,
        )

        return TriggerResponse(
            status="accepted",
            message="Pipeline execution started",
            run_id=run.id,
        )
    else:
        # Sync mode - wait for completion
        try:
            await _execute_pipeline_task(
                run.id,
                pipeline,
                pipeline_inputs,
                registry,
                run_storage,
                None,  # breakpoints
                webhook.org_id,
            )

            # Get completed run
            completed_run = run_storage.get(run.id, org_id=webhook.org_id)

            # Log successful invocation
            webhook_storage.log_invocation(
                webhook_id=webhook.id,
                run_id=run.id,
                request_method=request.method,
                request_headers=request_headers,
                request_body=request_body,
                source_ip=source_ip,
                status="success" if completed_run and completed_run.status == "completed" else "error",
                response_code=200 if completed_run and completed_run.status == "completed" else 500,
            )

            if completed_run and completed_run.status == "completed":
                return TriggerResponse(
                    status="completed",
                    message="Pipeline execution completed",
                    run_id=run.id,
                    result=completed_run.output,
                )
            else:
                return TriggerResponse(
                    status="failed",
                    message="Pipeline execution failed",
                    run_id=run.id,
                    error=completed_run.error if completed_run else "Unknown error",
                )

        except Exception as e:
            logger.error(f"Error executing webhook pipeline: {e}")

            webhook_storage.log_invocation(
                webhook_id=webhook.id,
                run_id=run.id,
                request_method=request.method,
                request_headers=request_headers,
                request_body=request_body,
                source_ip=source_ip,
                status="error",
                error_message=str(e),
                response_code=500,
            )

            return TriggerResponse(
                status="failed",
                message="Pipeline execution error",
                run_id=run.id,
                error=str(e),
            )
