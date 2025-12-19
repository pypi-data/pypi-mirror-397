"""
FlowMason MCP Server

Exposes FlowMason pipelines to AI assistants via Model Context Protocol.
"""

from .server import create_mcp_server, run_mcp_server

__all__ = ["create_mcp_server", "run_mcp_server"]
