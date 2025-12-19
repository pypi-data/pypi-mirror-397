"""
MCP List Tools Operator - Discover tools from MCP servers.

Lists available tools from an MCP (Model Context Protocol) server.
"""

import logging
from typing import Any, Dict, List, Literal, Optional

from flowmason_core.core.decorators import operator
from flowmason_core.core.types import Field, OperatorInput, OperatorOutput

logger = logging.getLogger(__name__)


@operator(
    name="mcp_list_tools",
    category="mcp",
    description="List available tools from an MCP server",
    icon="list",
    color="#6366F1",
    version="1.0.0",
    author="FlowMason",
    tags=["mcp", "discovery", "tools", "protocol"],
)
class MCPListToolsOperator:
    """
    List tools available from an MCP server.

    This operator enables pipelines to:
    - Discover available tools from an MCP server
    - Get tool descriptions and schemas
    - Build dynamic tool selection logic

    Use this operator to explore MCP server capabilities before
    calling specific tools with mcp_tool_call.

    Example usage in pipeline:
    ```json
    {
      "id": "discover-tools",
      "component_type": "mcp_list_tools",
      "config": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
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
        )
        env: Optional[Dict[str, str]] = Field(
            default=None,
            description="Environment variables for the server process",
        )

        # SSE transport options
        url: Optional[str] = Field(
            default=None,
            description="URL of the MCP SSE server (for sse transport)",
        )

        # Connection options
        timeout: int = Field(
            default=30,
            ge=1,
            le=300,
            description="Timeout in seconds for connecting to the server",
        )

    class Output(OperatorOutput):
        tools: List[Dict[str, Any]] = Field(
            description="List of available tools with name, description, and schema"
        )
        tool_count: int = Field(description="Number of available tools")
        server_name: Optional[str] = Field(description="Name of the MCP server")
        server_version: Optional[str] = Field(description="Version of the MCP server")

    class Config:
        deterministic: bool = False
        timeout_seconds: int = 60

    async def execute(self, input: Input, context) -> Output:
        """List available MCP tools."""

        log = getattr(context, "logger", logger)

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

            log.info(f"Listing tools from MCP server via {input.transport} transport")

            if input.transport == "stdio":
                result = await self._list_via_stdio(input, log)
            else:  # sse
                result = await self._list_via_sse(input, log)

            tools = result.get("tools", [])
            log.info(f"Found {len(tools)} tools")

            return self.Output(
                tools=tools,
                tool_count=len(tools),
                server_name=result.get("server_name"),
                server_version=result.get("server_version"),
            )

        except Exception as e:
            log.error(f"Failed to list MCP tools: {e}")
            raise

    async def _list_via_stdio(self, input: Input, log) -> Dict[str, Any]:
        """List tools via stdio transport."""
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
                result = await session.initialize()

                server_name = None
                server_version = None
                if result and hasattr(result, 'serverInfo'):
                    server_name = getattr(result.serverInfo, 'name', None)
                    server_version = getattr(result.serverInfo, 'version', None)

                log.debug(f"Connected to server: {server_name} v{server_version}")

                # List tools
                tools_result = await session.list_tools()

                tools = []
                for tool in tools_result.tools:
                    tool_info = {
                        "name": tool.name,
                        "description": getattr(tool, 'description', None),
                    }
                    # Include input schema if available
                    if hasattr(tool, 'inputSchema'):
                        tool_info["input_schema"] = tool.inputSchema
                    tools.append(tool_info)

                return {
                    "tools": tools,
                    "server_name": server_name,
                    "server_version": server_version,
                }

    async def _list_via_sse(self, input: Input, log) -> Dict[str, Any]:
        """List tools via SSE transport."""
        from mcp import ClientSession
        from mcp.client.sse import sse_client

        if not input.url:
            raise ValueError("url is required for sse transport")

        async with sse_client(input.url) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                result = await session.initialize()

                server_name = None
                server_version = None
                if result and hasattr(result, 'serverInfo'):
                    server_name = getattr(result.serverInfo, 'name', None)
                    server_version = getattr(result.serverInfo, 'version', None)

                log.debug(f"Connected to server: {server_name} v{server_version}")

                # List tools
                tools_result = await session.list_tools()

                tools = []
                for tool in tools_result.tools:
                    tool_info = {
                        "name": tool.name,
                        "description": getattr(tool, 'description', None),
                    }
                    if hasattr(tool, 'inputSchema'):
                        tool_info["input_schema"] = tool.inputSchema
                    tools.append(tool_info)

                return {
                    "tools": tools,
                    "server_name": server_name,
                    "server_version": server_version,
                }
