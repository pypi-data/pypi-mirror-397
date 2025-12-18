"""
MCP Tool Call Operator - Call tools from MCP servers.

Enables pipelines to call tools exposed by MCP (Model Context Protocol) servers.
"""

import json
import logging
from typing import Any, Dict, Literal, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput

logger = logging.getLogger(__name__)


@operator(
    name="mcp_tool_call",
    category="mcp",
    description="Call a tool from an MCP (Model Context Protocol) server",
    icon="cpu",
    color="#6366F1",
    version="1.0.0",
    author="FlowMason",
    tags=["mcp", "tool", "ai", "integration", "protocol"],
)
class MCPToolCallOperator:
    """
    Call tools exposed by MCP servers.

    This operator enables pipelines to:
    - Connect to MCP servers via stdio or SSE transport
    - Call specific tools with arguments
    - Process tool responses

    MCP (Model Context Protocol) is a standard for AI assistants to interact
    with external tools and data sources.

    Transport options:
    - stdio: Launch server process and communicate via stdin/stdout
    - sse: Connect to HTTP Server-Sent Events endpoint

    Example usage in pipeline:
    ```json
    {
      "id": "call-filesystem-tool",
      "component_type": "mcp_tool_call",
      "config": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "tool_name": "read_file",
        "tool_arguments": {"path": "/tmp/data.txt"}
      }
    }
    ```
    """

    class Input(OperatorInput):
        transport: Literal["stdio", "sse"] = Field(
            default="stdio",
            description="MCP transport type: 'stdio' for process communication, 'sse' for HTTP",
        )

        # stdio transport options
        command: Optional[str] = Field(
            default=None,
            description="Command to start the MCP server (for stdio transport)",
            examples=["npx", "python", "node"],
        )
        args: Optional[list] = Field(
            default=None,
            description="Arguments for the command",
            examples=[["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]],
        )
        env: Optional[Dict[str, str]] = Field(
            default=None,
            description="Environment variables for the server process",
        )

        # SSE transport options
        url: Optional[str] = Field(
            default=None,
            description="URL of the MCP SSE server (for sse transport)",
            examples=["http://localhost:8080/mcp"],
        )

        # Tool call options
        tool_name: str = Field(
            description="Name of the tool to call",
            examples=["read_file", "search", "execute_query"],
        )
        tool_arguments: Optional[Dict[str, Any]] = Field(
            default=None,
            description="Arguments to pass to the tool",
        )

        # Connection options
        timeout: int = Field(
            default=30,
            ge=1,
            le=300,
            description="Timeout in seconds for the tool call",
        )

    class Output(OperatorOutput):
        content: Any = Field(description="Tool response content")
        is_error: bool = Field(description="True if the tool returned an error")
        error_message: Optional[str] = Field(description="Error message if is_error is True")
        tool_name: str = Field(description="Name of the tool that was called")
        elapsed_ms: int = Field(description="Execution time in milliseconds")

    class Config:
        deterministic: bool = False
        timeout_seconds: int = 60

    async def execute(self, input: Input, context) -> Output:
        """Execute MCP tool call."""
        import time

        log = getattr(context, "logger", logger)
        start_time = time.perf_counter()

        try:
            # Try to import mcp package (verify availability)
            try:
                from mcp import ClientSession  # noqa: F401
                from mcp.client.sse import sse_client  # noqa: F401
                from mcp.client.stdio import StdioServerParameters, stdio_client  # noqa: F401
            except ImportError:
                raise RuntimeError(
                    "mcp package is required for MCP operations. "
                    "Install with: pip install 'flowmason[mcp]' or pip install mcp"
                )

            log.info(f"Calling MCP tool '{input.tool_name}' via {input.transport} transport")

            if input.transport == "stdio":
                result = await self._call_via_stdio(input, log)
            else:  # sse
                result = await self._call_via_sse(input, log)

            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            # Parse result
            if hasattr(result, 'content'):
                # Extract content from MCP response
                content_list = result.content
                if len(content_list) == 1:
                    # Single content item - extract text or data
                    item = content_list[0]
                    if hasattr(item, 'text'):
                        content = item.text
                        # Try to parse as JSON
                        try:
                            content = json.loads(content)
                        except (json.JSONDecodeError, TypeError):
                            pass
                    else:
                        content = item
                else:
                    # Multiple content items
                    content = [
                        item.text if hasattr(item, 'text') else item
                        for item in content_list
                    ]

                is_error = getattr(result, 'isError', False)
            else:
                content = result
                is_error = False

            log.info(f"Tool '{input.tool_name}' completed in {elapsed_ms}ms")

            return self.Output(
                content=content,
                is_error=is_error,
                error_message=str(content) if is_error else None,
                tool_name=input.tool_name,
                elapsed_ms=elapsed_ms,
            )

        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            log.error(f"MCP tool call failed: {e}")
            return self.Output(
                content=None,
                is_error=True,
                error_message=str(e),
                tool_name=input.tool_name,
                elapsed_ms=elapsed_ms,
            )

    async def _call_via_stdio(self, input: Input, log):
        """Call tool via stdio transport."""
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client

        if not input.command:
            raise ValueError("command is required for stdio transport")

        server_params = StdioServerParameters(
            command=input.command,
            args=input.args or [],
            env=input.env,
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                log.debug(f"Calling tool: {input.tool_name}")

                # Call the tool
                result = await session.call_tool(
                    input.tool_name,
                    input.tool_arguments or {},
                )

                return result

    async def _call_via_sse(self, input: Input, log):
        """Call tool via SSE transport."""
        from mcp import ClientSession
        from mcp.client.sse import sse_client

        if not input.url:
            raise ValueError("url is required for sse transport")

        async with sse_client(input.url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                log.debug(f"Calling tool: {input.tool_name}")

                # Call the tool
                result = await session.call_tool(
                    input.tool_name,
                    input.tool_arguments or {},
                )

                return result
