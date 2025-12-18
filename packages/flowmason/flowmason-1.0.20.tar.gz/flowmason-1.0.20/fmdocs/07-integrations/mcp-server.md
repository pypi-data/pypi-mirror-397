# MCP Server Integration

FlowMason includes a Model Context Protocol (MCP) server that exposes pipelines to AI assistants like Claude.

## Overview

The MCP server allows AI assistants to:
- List available pipelines
- Get detailed pipeline information
- Execute pipelines with input data
- Browse available components

## Installation

Install with MCP support:

```bash
pip install flowmason[mcp]
```

Or install the MCP SDK separately:

```bash
pip install mcp
```

## Quick Start

Start the MCP server:

```bash
fm mcp serve
```

With custom options:

```bash
fm mcp serve --pipelines ./my-pipelines --studio-url http://localhost:8999
```

## Claude Desktop Configuration

To use FlowMason with Claude Desktop:

1. Get the configuration:
   ```bash
   fm mcp config
   ```

2. Add the configuration to your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

Example configuration:

```json
{
  "mcpServers": {
    "flowmason": {
      "command": "python",
      "args": ["-m", "flowmason_core.cli.main", "mcp", "serve"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

3. Restart Claude Desktop

## Available Tools

### list_pipelines

Lists all available FlowMason pipelines with their names, descriptions, and stage counts.

**Example prompt:**
> "Show me available FlowMason pipelines"

### get_pipeline

Gets detailed information about a specific pipeline including its input schema and stages.

**Arguments:**
- `pipeline_name`: Name of the pipeline

**Example prompt:**
> "Show me the details of the data-validation-etl pipeline"

### run_pipeline

Executes a pipeline with optional input data.

**Arguments:**
- `pipeline_name`: Name of the pipeline to run
- `input_data`: JSON string with input data (optional)

**Example prompt:**
> "Run the batch-processing pipeline with items: [{'id': '1', 'value': 100}]"

### list_components

Lists all available FlowMason components (operators and nodes).

**Example prompt:**
> "What components are available in FlowMason?"

### get_component

Gets detailed information about a specific component including its configuration schema.

**Arguments:**
- `component_type`: The component type (e.g., 'generator', 'json_transform')

**Example prompt:**
> "Tell me about the json_transform component"

## Requirements

- FlowMason Studio must be running for pipeline execution
- Pipelines should be in the configured directory or uploaded to Studio

## Testing

Test the MCP server:

```bash
fm mcp test
```

This verifies that the server can be created and lists available tools.

## Troubleshooting

### "Cannot connect to FlowMason Studio"

Start the Studio server:
```bash
fm studio start
```

### "MCP SDK not installed"

Install the MCP dependency:
```bash
pip install flowmason[mcp]
```

### "No pipelines found"

Ensure pipelines are in the correct directory or use `--pipelines` to specify the location.
