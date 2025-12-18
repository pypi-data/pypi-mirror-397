# Installation

This guide covers how to install FlowMason components for development.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for Studio frontend and VSCode extension development)
- VSCode (recommended IDE)

## Installing FlowMason Core

FlowMason Core is the Python framework for building components and executing pipelines.

```bash
# Install from source (development)
cd core
pip install -e ".[all]"

# This installs:
# - flowmason_core - Core framework
# - CLI tools (flowmason, fm commands)
# - All optional dependencies
```

### Core Dependencies

| Package | Purpose |
|---------|---------|
| `pydantic` | Type validation and schemas |
| `typer` | CLI framework |
| `rich` | Terminal formatting |
| `httpx` | HTTP client for API calls |
| `jmespath` | JSON path queries |

## Installing FlowMason Studio

Studio provides the backend API server and optional web UI.

```bash
# Install from source (development)
cd studio
pip install -e .

# Start Studio server
flowmason studio start
# or
fm studio start
```

Studio runs on `http://localhost:8999` by default.

### Studio Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | API framework |
| `uvicorn` | ASGI server |
| `websockets` | Real-time updates |
| `sqlalchemy` | Database ORM |

## Installing the VSCode Extension

### From VSIX (Recommended)

```bash
# Install from .vsix file
code --install-extension vscode-extension/flowmason-0.10.0.vsix
```

### From Source

```bash
cd vscode-extension
npm install
npm run compile
npm run package
code --install-extension flowmason-0.10.0.vsix
```

## Verifying Installation

```bash
# Check CLI
fm --version

# Check Studio
fm studio status

# In VSCode, open Command Palette (Cmd+Shift+P)
# Type "FlowMason" to see available commands
```

## Project Setup

Initialize a new FlowMason project:

```bash
# Create project directory
mkdir my-project && cd my-project

# Initialize FlowMason project
fm init

# This creates:
# - flowmason.json (project manifest)
# - pipelines/ directory
# - components/ directory
# - .flowmason/ directory (state)
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FLOWMASON_HOST` | Studio server host | `127.0.0.1` |
| `FLOWMASON_PORT` | Studio server port | `8999` |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GOOGLE_API_KEY` | Google (Gemini) API key | - |
| `GROQ_API_KEY` | Groq API key | - |
| `PERPLEXITY_API_KEY` | Perplexity API key | - |

## Database Configuration

Studio uses SQLite by default. For production, configure PostgreSQL:

```python
# Set via environment variable
DATABASE_URL=postgresql://user:pass@host:5432/flowmason
```

Or configure in `flowmason.json`:

```json
{
  "database": {
    "type": "postgresql",
    "url": "postgresql://user:pass@host:5432/flowmason"
  }
}
```

## Next Steps

- [Quick Start](quickstart.md) - Build your first pipeline
- [Core Concepts](../03-concepts/architecture-overview.md) - Understand how FlowMason works
- [VSCode Extension](../07-vscode-extension/overview.md) - Use the VSCode integration
