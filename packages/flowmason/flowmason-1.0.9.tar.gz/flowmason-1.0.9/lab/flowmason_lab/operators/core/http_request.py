"""
HTTP Request Operator - Core FlowMason Component.

Makes HTTP requests to external APIs with support for:
- All HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Custom headers and authentication
- JSON request/response bodies
- Query parameters
- Configurable timeouts
"""

import logging
from typing import Any, Dict, Literal, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput

logger = logging.getLogger(__name__)


@operator(
    name="http_request",
    category="core",
    description="Make HTTP requests to external APIs and services",
    icon="globe",
    color="#3B82F6",
    version="1.0.0",
    author="FlowMason",
    tags=["http", "api", "rest", "integration", "web", "core"],
)
class HttpRequestOperator:
    """
    Make HTTP requests to external APIs.

    This operator enables pipelines to:
    - Fetch data from REST APIs
    - Submit data to webhooks
    - Integrate with external services
    - Call internal microservices

    The operator handles:
    - Request construction
    - Response parsing (JSON with text fallback)
    - Error handling
    - Timeout management
    """

    class Input(OperatorInput):
        url: str = Field(
            description="The URL to request",
            examples=[
                "https://api.example.com/data",
                "https://httpbin.org/post",
            ],
        )
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"] = Field(
            default="GET",
            description="HTTP method to use",
        )
        headers: Optional[Dict[str, str]] = Field(
            default=None,
            description="Request headers (e.g., {'Authorization': 'Bearer token'})",
        )
        body: Optional[Dict[str, Any]] = Field(
            default=None,
            description="JSON request body for POST/PUT/PATCH requests",
        )
        params: Optional[Dict[str, str]] = Field(
            default=None,
            description="Query parameters appended to the URL",
        )
        timeout: int = Field(
            default=30,
            ge=1,
            le=300,
            description="Request timeout in seconds",
        )
        follow_redirects: bool = Field(
            default=True,
            description="Whether to follow HTTP redirects",
        )
        verify_ssl: bool = Field(
            default=True,
            description="Whether to verify SSL certificates",
        )

    class Output(OperatorOutput):
        status_code: int = Field(description="HTTP status code (e.g., 200, 404)")
        headers: Dict[str, str] = Field(description="Response headers")
        body: Any = Field(description="Response body (JSON or text)")
        elapsed_ms: int = Field(description="Request duration in milliseconds")
        success: bool = Field(description="True if status code is 2xx")
        url: str = Field(description="Final URL (after redirects)")

    class Config:
        deterministic: bool = False  # Network calls can vary
        timeout_seconds: int = 60

    async def execute(self, input: Input, context) -> Output:
        """Execute HTTP request and return response."""
        try:
            import httpx
        except ImportError:
            raise RuntimeError(
                "httpx is required for HTTP requests. Install with: pip install httpx"
            )

        log = getattr(context, "logger", logger)
        log.info(f"Making {input.method} request to {input.url}")

        try:
            async with httpx.AsyncClient(
                timeout=input.timeout,
                follow_redirects=input.follow_redirects,
                verify=input.verify_ssl,
            ) as client:
                response = await client.request(
                    method=input.method,
                    url=input.url,
                    headers=input.headers,
                    json=input.body if input.body else None,
                    params=input.params,
                )

                # Try to parse JSON, fall back to text
                try:
                    body = response.json()
                except Exception:
                    body = response.text

                elapsed_ms = int(response.elapsed.total_seconds() * 1000)

                log.info(f"Response: {response.status_code} in {elapsed_ms}ms")

                return self.Output(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=body,
                    elapsed_ms=elapsed_ms,
                    success=response.is_success,
                    url=str(response.url),
                )

        except httpx.TimeoutException as e:
            log.error(f"Request timeout: {e}")
            raise TimeoutError(f"Request to {input.url} timed out after {input.timeout}s")

        except httpx.RequestError as e:
            log.error(f"Request error: {e}")
            raise ConnectionError(f"Failed to connect to {input.url}: {e}")
