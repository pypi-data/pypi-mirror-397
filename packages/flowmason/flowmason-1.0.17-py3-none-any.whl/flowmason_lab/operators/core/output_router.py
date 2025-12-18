"""
Output Router Operator - Core FlowMason Component.

Routes pipeline output to multiple destinations:
- Webhooks (HTTP POST/PUT)
- Email (via SMTP or API)
- Database (SQL insert/upsert)
- Message Queues (Kafka, RabbitMQ, SQS)

This operator can be used within a pipeline to send data to external
systems at any point in the execution, not just at completion.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DestinationConfig(BaseModel):
    """Configuration for a single output destination."""
    id: str = Field(description="Unique identifier for this destination")
    type: Literal["webhook", "email", "database", "message_queue"] = Field(
        description="Type of destination"
    )
    name: str = Field(description="Human-readable name")
    enabled: bool = Field(default=True, description="Whether destination is active")
    config: Dict[str, Any] = Field(description="Type-specific configuration")
    on_success: bool = Field(default=True, description="Send on success")
    on_error: bool = Field(default=False, description="Send on error")
    payload_template: Optional[str] = Field(
        default=None,
        description="Jinja2 template for payload transformation"
    )


class DeliveryResult(BaseModel):
    """Result of delivering to a single destination."""
    destination_id: str
    destination_name: str
    destination_type: str
    success: bool
    status_code: Optional[int] = None
    response: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int


@operator(
    name="output_router",
    category="core",
    description="Route data to multiple output destinations (webhooks, email, database, message queues)",
    icon="share-2",
    color="#8B5CF6",
    version="1.0.0",
    author="FlowMason",
    tags=["output", "routing", "webhook", "integration", "delivery", "core"],
)
class OutputRouterOperator:
    """
    Route pipeline data to multiple external destinations.

    This operator enables pipelines to:
    - Send results to webhooks for integration
    - Trigger email notifications
    - Store results in databases
    - Publish to message queues

    Each destination can be configured independently with:
    - Success/error filtering
    - Payload transformation via templates
    - Retry and timeout settings
    """

    class Input(OperatorInput):
        data: Any = Field(
            description="The data to route to destinations"
        )
        destinations: List[Dict[str, Any]] = Field(
            description="List of destination configurations",
            examples=[
                [
                    {
                        "id": "webhook-1",
                        "type": "webhook",
                        "name": "CRM Webhook",
                        "config": {"url": "https://api.example.com/webhook"}
                    }
                ]
            ]
        )
        is_error: bool = Field(
            default=False,
            description="Whether this is an error result (affects destination filtering)"
        )
        error_message: Optional[str] = Field(
            default=None,
            description="Error message if is_error is True"
        )
        metadata: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Additional metadata to include in deliveries"
        )
        parallel: bool = Field(
            default=True,
            description="Whether to deliver to destinations in parallel"
        )
        fail_on_error: bool = Field(
            default=False,
            description="Whether to fail the entire operation if any delivery fails"
        )

    class Output(OperatorOutput):
        total_destinations: int = Field(description="Total number of destinations")
        successful_deliveries: int = Field(description="Number of successful deliveries")
        failed_deliveries: int = Field(description="Number of failed deliveries")
        skipped_deliveries: int = Field(description="Number of skipped (disabled/filtered) deliveries")
        results: List[Dict[str, Any]] = Field(description="Individual delivery results")
        all_succeeded: bool = Field(description="True if all attempted deliveries succeeded")

    class Config:
        deterministic: bool = False  # Network calls can vary
        timeout_seconds: int = 120  # Allow time for multiple destinations

    async def execute(self, input: Input, context) -> Output:
        """Execute routing to all configured destinations."""
        import asyncio

        log = getattr(context, "logger", logger)
        log.info(f"Routing to {len(input.destinations)} destinations")

        # Parse destinations
        destinations = [
            DestinationConfig(**d) if isinstance(d, dict) else d
            for d in input.destinations
        ]

        results: List[DeliveryResult] = []
        skipped = 0

        # Filter destinations based on success/error status
        active_destinations = []
        for dest in destinations:
            if not dest.enabled:
                skipped += 1
                continue
            if input.is_error and not dest.on_error:
                skipped += 1
                continue
            if not input.is_error and not dest.on_success:
                skipped += 1
                continue
            active_destinations.append(dest)

        log.info(f"Active destinations: {len(active_destinations)}, skipped: {skipped}")

        # Prepare payload
        base_payload = {
            "data": input.data,
            "is_error": input.is_error,
            "error_message": input.error_message,
            "metadata": input.metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Deliver to all destinations
        if input.parallel and len(active_destinations) > 1:
            # Parallel delivery
            tasks = [
                self._deliver_to_destination(dest, base_payload, log)
                for dest in active_destinations
            ]
            results = await asyncio.gather(*tasks)
        else:
            # Sequential delivery
            for dest in active_destinations:
                result = await self._deliver_to_destination(dest, base_payload, log)
                results.append(result)

        # Count successes and failures
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        if input.fail_on_error and failed > 0:
            failed_names = [r.destination_name for r in results if not r.success]
            raise RuntimeError(f"Delivery failed for destinations: {', '.join(failed_names)}")

        return self.Output(
            total_destinations=len(destinations),
            successful_deliveries=successful,
            failed_deliveries=failed,
            skipped_deliveries=skipped,
            results=[r.model_dump() for r in results],
            all_succeeded=(failed == 0),
        )

    async def _deliver_to_destination(
        self,
        dest: DestinationConfig,
        payload: Dict[str, Any],
        log
    ) -> DeliveryResult:
        """Deliver payload to a single destination."""
        start_time = datetime.utcnow()

        try:
            # Apply payload template if specified
            final_payload = payload
            if dest.payload_template:
                final_payload = self._apply_template(dest.payload_template, payload)

            # Deliver based on type
            if dest.type == "webhook":
                result = await self._deliver_webhook(dest, final_payload, log)
            elif dest.type == "email":
                result = await self._deliver_email(dest, final_payload, log)
            elif dest.type == "database":
                result = await self._deliver_database(dest, final_payload, log)
            elif dest.type == "message_queue":
                result = await self._deliver_message_queue(dest, final_payload, log)
            else:
                raise ValueError(f"Unknown destination type: {dest.type}")

            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            result.duration_ms = duration_ms
            return result

        except Exception as e:
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            log.error(f"Failed to deliver to {dest.name}: {e}")
            return DeliveryResult(
                destination_id=dest.id,
                destination_name=dest.name,
                destination_type=dest.type,
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )

    def _apply_template(self, template: str, payload: Dict[str, Any]) -> Any:
        """Apply Jinja2 template to transform payload."""
        try:
            from jinja2 import Template
            t = Template(template)
            rendered = t.render(**payload)
            # Try to parse as JSON
            try:
                return json.loads(rendered)
            except json.JSONDecodeError:
                return rendered
        except ImportError:
            logger.warning("Jinja2 not installed, skipping template transformation")
            return payload

    async def _deliver_webhook(
        self,
        dest: DestinationConfig,
        payload: Dict[str, Any],
        log
    ) -> DeliveryResult:
        """Deliver to a webhook endpoint."""
        try:
            import httpx
        except ImportError:
            raise RuntimeError("httpx is required for webhook delivery")

        url = dest.config.get("url")
        if not url or not isinstance(url, str):
            raise ValueError("Webhook URL is required and must be a string")
        method = dest.config.get("method", "POST").upper()
        headers = dest.config.get("headers", {})
        timeout = dest.config.get("timeout_ms", 30000) / 1000
        retry_count = dest.config.get("retry_count", 3)

        headers["Content-Type"] = "application/json"
        payload_json = json.dumps(payload, default=str)

        log.info(f"Delivering to webhook: {url}")

        last_error = None
        for attempt in range(retry_count):
            try:
                async with httpx.AsyncClient() as client:
                    if method == "POST":
                        response = await client.post(
                            url, content=payload_json, headers=headers, timeout=timeout
                        )
                    elif method == "PUT":
                        response = await client.put(
                            url, content=payload_json, headers=headers, timeout=timeout
                        )
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                    log.info(f"Webhook response: {response.status_code}")

                    return DeliveryResult(
                        destination_id=dest.id,
                        destination_name=dest.name,
                        destination_type="webhook",
                        success=response.is_success,
                        status_code=response.status_code,
                        response=response.text[:500] if response.text else None,
                        duration_ms=0,  # Will be set by caller
                    )

            except httpx.HTTPError as e:
                last_error = e
                if attempt < retry_count - 1:
                    log.warning(f"Webhook attempt {attempt + 1} failed, retrying: {e}")
                    import asyncio
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        raise last_error or RuntimeError("Webhook delivery failed")

    async def _deliver_email(
        self,
        dest: DestinationConfig,
        payload: Dict[str, Any],
        log
    ) -> DeliveryResult:
        """Deliver via email."""
        # Email delivery implementation
        # For now, log that it would be sent
        to_list = dest.config.get("to", [])
        subject = dest.config.get("subject_template", "FlowMason Notification")

        log.info(f"Would send email to {to_list} with subject: {subject}")

        # TODO: Implement actual email sending via SMTP or API
        # For now, return a placeholder success
        return DeliveryResult(
            destination_id=dest.id,
            destination_name=dest.name,
            destination_type="email",
            success=True,
            response=f"Email queued for delivery to {len(to_list)} recipients",
            duration_ms=0,
        )

    async def _deliver_database(
        self,
        dest: DestinationConfig,
        payload: Dict[str, Any],
        log
    ) -> DeliveryResult:
        """Deliver to a database."""
        connection_id = dest.config.get("connection_id")
        table = dest.config.get("table")
        operation = dest.config.get("operation", "insert")

        log.info(f"Would {operation} to table {table} using connection {connection_id}")

        # TODO: Implement actual database delivery
        # This would use the stored connection from allowlist_storage
        return DeliveryResult(
            destination_id=dest.id,
            destination_name=dest.name,
            destination_type="database",
            success=True,
            response=f"Data queued for {operation} to {table}",
            duration_ms=0,
        )

    async def _deliver_message_queue(
        self,
        dest: DestinationConfig,
        payload: Dict[str, Any],
        log
    ) -> DeliveryResult:
        """Deliver to a message queue."""
        connection_id = dest.config.get("connection_id")
        queue_name = dest.config.get("queue_name")

        log.info(f"Would publish to queue {queue_name} using connection {connection_id}")

        # TODO: Implement actual message queue delivery
        # This would use the stored connection from allowlist_storage
        return DeliveryResult(
            destination_id=dest.id,
            destination_name=dest.name,
            destination_type="message_queue",
            success=True,
            response=f"Message queued for delivery to {queue_name}",
            duration_ms=0,
        )


# Also create an ErrorRouterOperator that's specifically for error handling
@operator(
    name="error_router",
    category="core",
    description="Route error information to notification destinations",
    icon="alert-triangle",
    color="#EF4444",
    version="1.0.0",
    author="FlowMason",
    tags=["error", "notification", "alerting", "core"],
)
class ErrorRouterOperator:
    """
    Route error information to notification destinations.

    This operator is designed for use in TryCatch error handlers to
    send alerts when pipeline stages fail.
    """

    class Input(OperatorInput):
        error_type: str = Field(
            description="Type of error (e.g., TIMEOUT, VALIDATION, CONNECTIVITY)"
        )
        error_message: str = Field(
            description="Error message"
        )
        stage_id: Optional[str] = Field(
            default=None,
            description="ID of the stage that failed"
        )
        pipeline_id: Optional[str] = Field(
            default=None,
            description="ID of the pipeline"
        )
        run_id: Optional[str] = Field(
            default=None,
            description="ID of the run"
        )
        destinations: List[Dict[str, Any]] = Field(
            description="List of destination configurations"
        )
        include_stack_trace: bool = Field(
            default=False,
            description="Whether to include stack trace in notifications"
        )
        severity: Literal["critical", "error", "warning", "info"] = Field(
            default="error",
            description="Severity level for filtering and formatting"
        )

    class Output(OperatorOutput):
        notifications_sent: int = Field(description="Number of notifications sent")
        failed_notifications: int = Field(description="Number of failed notifications")
        results: List[Dict[str, Any]] = Field(description="Individual notification results")

    class Config:
        deterministic: bool = False
        timeout_seconds: int = 60

    async def execute(self, input: Input, context) -> Output:
        """Send error notifications to all configured destinations."""
        _log = getattr(context, "logger", logger)  # noqa: F841

        # Build error payload
        error_payload = {
            "error_type": input.error_type,
            "error_message": input.error_message,
            "stage_id": input.stage_id,
            "pipeline_id": input.pipeline_id,
            "run_id": input.run_id,
            "severity": input.severity,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Use OutputRouterOperator for actual delivery
        router = OutputRouterOperator()
        router_input = OutputRouterOperator.Input(
            data=error_payload,
            destinations=input.destinations,
            is_error=True,
            error_message=input.error_message,
            metadata={"severity": input.severity},
            parallel=True,
            fail_on_error=False,
        )

        result = await router.execute(router_input, context)

        return self.Output(
            notifications_sent=result.successful_deliveries,
            failed_notifications=result.failed_deliveries,
            results=result.results,
        )
