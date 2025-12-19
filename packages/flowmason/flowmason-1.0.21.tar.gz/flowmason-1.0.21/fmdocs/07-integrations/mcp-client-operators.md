# MCP Client Operators

FlowMason provides operators to call tools from MCP (Model Context Protocol) servers, enabling pipelines to leverage external AI tools and services.

## Overview

MCP client operators allow pipelines to:
- Discover available tools from MCP servers
- Call specific tools with arguments
- Process tool responses in pipeline stages

## Available Operators

### mcp_tool_call

Call a tool from an MCP server.

```json
{
  "id": "call-tool",
  "component_type": "mcp_tool_call",
  "config": {
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"],
    "tool_name": "read_file",
    "tool_arguments": {
      "path": "/data/config.json"
    }
  }
}
```

#### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transport` | "stdio" \| "sse" | No | Transport type (default: "stdio") |
| `command` | string | For stdio | Command to start MCP server |
| `args` | list | No | Command arguments |
| `env` | object | No | Environment variables |
| `url` | string | For sse | URL of MCP SSE server |
| `tool_name` | string | Yes | Name of the tool to call |
| `tool_arguments` | object | No | Arguments to pass to the tool |
| `timeout` | int | No | Timeout in seconds (default: 30) |

#### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `content` | any | Tool response content |
| `is_error` | bool | True if the tool returned an error |
| `error_message` | string | Error message if is_error is true |
| `tool_name` | string | Name of the tool called |
| `elapsed_ms` | int | Execution time in milliseconds |

### mcp_list_tools

Discover available tools from an MCP server.

```json
{
  "id": "discover-tools",
  "component_type": "mcp_list_tools",
  "config": {
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"]
  }
}
```

#### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transport` | "stdio" \| "sse" | No | Transport type (default: "stdio") |
| `command` | string | For stdio | Command to start MCP server |
| `args` | list | No | Command arguments |
| `env` | object | No | Environment variables |
| `url` | string | For sse | URL of MCP SSE server |
| `timeout` | int | No | Timeout in seconds (default: 30) |

#### Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `tools` | list | List of available tools |
| `tool_count` | int | Number of available tools |
| `server_name` | string | Name of the MCP server |
| `server_version` | string | Version of the MCP server |

## Transport Types

### stdio (Process Communication)

Launch an MCP server process and communicate via stdin/stdout:

```json
{
  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {"GITHUB_TOKEN": "{{secrets.GITHUB_TOKEN}}"}
}
```

Commonly used with:
- NPM packages: `npx -y @modelcontextprotocol/server-*`
- Python servers: `python -m mcp_server_name`
- Node.js scripts: `node /path/to/server.js`

### sse (HTTP Server-Sent Events)

Connect to an MCP server running as an HTTP service:

```json
{
  "transport": "sse",
  "url": "http://mcp-server.example.com:8080"
}
```

Useful for:
- Remote MCP servers
- Shared infrastructure
- High-availability deployments

## Example Pipelines

### File Operations

Read and process files using the filesystem MCP server:

```json
{
  "name": "file-processor",
  "stages": [
    {
      "id": "read-config",
      "component_type": "mcp_tool_call",
      "config": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/app"],
        "tool_name": "read_file",
        "tool_arguments": {"path": "/app/config.json"}
      }
    },
    {
      "id": "process-config",
      "component_type": "json_transform",
      "depends_on": ["read-config"],
      "config": {
        "expression": "$.config | parse_json"
      }
    }
  ]
}
```

### GitHub Integration

Query GitHub repositories using the GitHub MCP server:

```json
{
  "name": "github-analyzer",
  "stages": [
    {
      "id": "list-issues",
      "component_type": "mcp_tool_call",
      "config": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_TOKEN": "{{secrets.GITHUB_TOKEN}}"},
        "tool_name": "list_issues",
        "tool_arguments": {
          "owner": "anthropics",
          "repo": "claude-code",
          "state": "open"
        }
      }
    }
  ]
}
```

### Database Queries

Query databases using the Postgres MCP server:

```json
{
  "name": "data-pipeline",
  "stages": [
    {
      "id": "query-users",
      "component_type": "mcp_tool_call",
      "config": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres"],
        "env": {"DATABASE_URL": "{{secrets.DATABASE_URL}}"},
        "tool_name": "query",
        "tool_arguments": {
          "sql": "SELECT * FROM users WHERE active = true LIMIT 100"
        }
      }
    }
  ]
}
```

### Dynamic Tool Discovery

Discover available tools and call them dynamically:

```json
{
  "name": "tool-explorer",
  "stages": [
    {
      "id": "list-available-tools",
      "component_type": "mcp_list_tools",
      "config": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-everything"]
      }
    },
    {
      "id": "select-tool",
      "component_type": "router",
      "depends_on": ["list-available-tools"],
      "config": {
        "routes": [
          {"condition": "search in $.tools[*].name", "next_stage": "call-search"},
          {"default": true, "next_stage": "no-search"}
        ]
      }
    }
  ]
}
```

## Installation

MCP operators require the `mcp` package:

```bash
pip install flowmason[mcp]
# or
pip install mcp
```

## Popular MCP Servers

| Server | NPM Package | Description |
|--------|-------------|-------------|
| Filesystem | `@modelcontextprotocol/server-filesystem` | File read/write operations |
| GitHub | `@modelcontextprotocol/server-github` | GitHub API integration |
| Postgres | `@modelcontextprotocol/server-postgres` | PostgreSQL queries |
| Brave Search | `@modelcontextprotocol/server-brave-search` | Web search |
| Memory | `@modelcontextprotocol/server-memory` | Key-value storage |
| Puppeteer | `@modelcontextprotocol/server-puppeteer` | Browser automation |

See [MCP Servers](https://modelcontextprotocol.io/servers) for more options.

## Error Handling

Handle tool errors in your pipeline:

```json
{
  "stages": [
    {
      "id": "call-tool",
      "component_type": "mcp_tool_call",
      "config": {"..."}
    },
    {
      "id": "handle-result",
      "component_type": "conditional",
      "depends_on": ["call-tool"],
      "config": {
        "condition": "$.is_error == false",
        "true_stage": "process-success",
        "false_stage": "handle-error"
      }
    }
  ]
}
```

## Best Practices

1. **Use secrets for credentials**: Store API keys and tokens in FlowMason secrets
2. **Set appropriate timeouts**: MCP calls can be slow; set realistic timeouts
3. **Handle errors gracefully**: Check `is_error` in downstream stages
4. **Discover before calling**: Use `mcp_list_tools` to validate tool availability
5. **Use SSE for production**: stdio transport creates new processes; SSE is more efficient
