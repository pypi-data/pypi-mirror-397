# FlowMason Documentation

**Version 1.0.0** | **All Milestones Complete** | **Production Ready**

Welcome to FlowMason - an AI pipeline orchestration platform for building, debugging, and deploying intelligent workflows.

## Platform Status

FlowMason is **fully production-ready** with all planned milestones complete:

| Milestone | Status | Key Features |
|-----------|--------|--------------|
| **P1 - Quick Wins** | ✅ Complete | Docker, Auth, MCP Server, Secrets, Visual Polish |
| **P2 - Core Platform** | ✅ Complete | OAuth, JWT, Scheduling, Webhooks, SDK, Gallery |
| **P3 - Advanced** | ✅ Complete | Marketplace, Time Travel Debugger, Collaboration |
| **P4 - Code Generation** | ✅ Complete | Python, TypeScript, Go, Apex code generation |

## The FlowMason Platform

FlowMason uses a **Salesforce DX-style hybrid model**:

```
LOCAL DEVELOPMENT                    STAGING/PRODUCTION
┌─────────────────────┐             ┌─────────────────────┐
│ .pipeline.json      │  deploy     │ PostgreSQL Database │
│ files (Git repo)    │────────────>│ Backend APIs        │
│ VSCode + Extension  │             │ Runtime Execution   │
└─────────────────────┘             └─────────────────────┘
        │                                    │
   Fast iteration                    Production runtime
   Version control                   API consumption
   Debug & test                      Full observability
```

- **Development**: File-based pipelines (`.pipeline.json`) in VSCode with Git version control
- **Deployment**: Push to staging/production orgs where pipelines run from databases
- **Runtime**: Backend APIs expose pipelines for consumption

See [The Hybrid Model](01-vision/hybrid-model.md) for details.

## Quick Links

| I want to... | Go to |
|--------------|-------|
| **Follow step-by-step tutorials** | [Tutorials](tutorials/README.md) |
| **Check implementation status** | [Implementation Status](00-status/implementation-status.md) |
| **Build DevOps pipelines** | [DevOps Solutions](12-devops-solutions/README.md) |
| Understand the platform model | [Hybrid Model](01-vision/hybrid-model.md) |
| Get started quickly | [Getting Started](02-getting-started/quickstart.md) |
| Understand the concepts | [Concepts](03-concepts/architecture-overview.md) |
| Build a node | [Building Nodes](04-core-framework/decorators/node.md) |
| Build an operator | [Building Operators](04-core-framework/decorators/operator.md) |
| Use control flow | [Control Flow](03-concepts/control-flow.md) |
| Debug a pipeline | [Debugging](06-studio/debugging.md) |
| Use time travel debugging | [Time Travel](06-studio/debugging.md#time-travel) |
| Browse the marketplace | [Marketplace](06-studio/marketplace.md) |
| Use the VSCode extension | [VSCode Extension](07-vscode-extension/overview.md) |
| Deploy to staging/production | [Docker Deployment](06-studio/docker.md) |
| Understand the architecture | [Architecture](10-architecture/system-overview.md) |

## Tutorials

New to FlowMason? Start here:

| Tutorial | Duration | Description |
|----------|----------|-------------|
| [1. Getting Started](tutorials/01-getting-started.md) | 15 min | Install and set up FlowMason |
| [2. Building Your First Pipeline](tutorials/02-building-first-pipeline.md) | 30 min | Create a 3-stage AI pipeline |
| [3. Debugging Pipelines](tutorials/03-debugging-pipelines.md) | 25 min | Breakpoints, stepping, time travel |
| [4. Testing Pipelines](tutorials/04-testing-pipelines.md) | 25 min | Write tests, mocks, coverage |
| [5. Working with Components](tutorials/05-working-with-components.md) | 35 min | Create custom nodes and operators |

## Documentation Structure

```
fmdocs/
├── 00-status/          # Implementation status and remaining work
├── tutorials/          # Step-by-step tutorials (start here!)
├── 01-vision/          # Platform vision, hybrid model, roadmap
├── 02-getting-started/ # Installation and first steps
├── 03-concepts/        # Core concepts explained
├── 04-core-framework/  # Decorators, types, execution engine
├── 05-sdk/             # Python, TypeScript, React SDKs
├── 05-security/        # Security, secrets, permissions
├── 06-studio/          # Studio backend, marketplace, debugging
├── 07-vscode-extension/# VSCode extension features
├── 07-integrations/    # MCP, OpenTelemetry, remote registry
├── 08-packaging-deployment/ # Packages, Docker, CI/CD
├── 09-debugging-testing/    # Debug and test pipelines
├── 10-architecture/    # System architecture deep dive
├── 11-contributing/    # How to contribute
└── 12-devops-solutions/# DevOps, Integration & IT Operations
```

## What is FlowMason?

FlowMason is a complete platform for building AI-powered pipelines that:

- **Design** - Visual pipeline editor, AI-assisted generation, component library
- **Execute** - Run pipelines with full observability and control
- **Debug** - Step through execution, time travel, inspect data, iterate on prompts
- **Test** - Unit test nodes, integration test pipelines, coverage reporting
- **Deploy** - Docker containers for staging/production with multi-region support
- **Share** - Marketplace for discovering and installing pipeline templates
- **Version** - Git-friendly file format for collaboration

## Key Features

### Core Framework
- 3 decorators: `@node`, `@operator`, `@control_flow`
- 18+ built-in components (control flow, operators, nodes)
- UniversalExecutor with timeout, retry, and cancellation support
- DAGExecutor for pipeline execution with control flow handling

### CLI Commands
```bash
fm run              # Execute pipeline from file
fm validate         # Validate pipeline files
fm init             # Initialize new FlowMason project
fm deploy           # Deploy pipelines to org
fm pull             # Pull pipelines from org
fm pack             # Build .fmpkg package
fm install          # Install .fmpkg package
fm studio           # start/stop/status/restart
fm org              # login/logout/list/default/display
fm auth             # API key management
```

### Studio Backend
- FastAPI backend with REST API and WebSocket support
- Full authentication: API keys, OAuth 2.0, JWT, SAML/SSO
- Pipeline scheduling (cron), webhooks, event triggers
- Marketplace for sharing/discovering pipelines
- Multi-region deployment support
- Real-time collaboration

### VSCode Extension (v0.10.0)

**Language Features:**
- IntelliSense for decorators and component patterns
- Diagnostics for FlowMason validation
- Hover documentation
- CodeLens (Run/Preview buttons)
- Go to Definition / Find References
- Document symbols for Outline view

**Pipeline Editing:**
- DAG Canvas custom editor for visual pipeline editing
- Pipeline stages tree view
- Stage configuration panel (standard and React-based)
- Native Outline integration for pipeline structure

**Debugging (DAP):**
- Full Debug Adapter Protocol integration
- Breakpoints on pipeline stages (F9)
- Conditional breakpoints and hit counts
- Watch expressions
- Step through execution (F10, F11)
- Variables panel with stage inputs/outputs
- **Time Travel Debugging** - Step backwards through execution history

**Prompt Iteration:**
- Prompt Editor sidebar panel during debug
- View and edit system/user prompts
- Re-run individual stages with modified prompts
- Prompt version history
- Side-by-side output comparison with diff highlighting

**Test Explorer:**
- VSCode Test Explorer integration
- `.test.json` test file format
- Coverage gutters in editor
- Pipeline and component testing

**Marketplace Integration:**
- Browse featured, trending, new pipelines
- Search and filter by category
- Install directly to workspace
- Publisher profiles

### Security
- API key authentication with scoped permissions
- OAuth 2.0 with PKCE support
- JWT session management with token rotation
- SAML/SSO with signature verification
- bcrypt password hashing
- Redis-backed distributed rate limiting
- Secrets management with rotation and audit

### Code Generation
Generate standalone code from pipelines in multiple languages:
- Python (standalone, AWS Lambda, Firebase Functions)
- TypeScript (standalone, AWS Lambda, Cloudflare Workers)
- Go (standalone, AWS Lambda, Docker)
- Salesforce Apex

## Component Types

FlowMason has three types of components:

| Type | Decorator | Purpose | Example |
|------|-----------|---------|---------|
| **Node** | `@node` | AI-powered operations requiring LLM | Text generation, summarization |
| **Operator** | `@operator` | Deterministic data transformations | JSON parsing, filtering, HTTP calls |
| **Control Flow** | `@control_flow` | Pipeline execution control | Conditionals, loops, error handling |

## Environments

| Environment | Storage | Execution | Use Case |
|-------------|---------|-----------|----------|
| **Local (File Mode)** | `.pipeline.json` files | Direct from files | Fast development |
| **Local (Org Mode)** | SQLite | From local DB | Test DB behavior |
| **Staging Org** | PostgreSQL | From DB via API | Integration testing |
| **Production Org** | PostgreSQL | From DB via API | Live runtime |

## Installation

```bash
# Install FlowMason (includes core, studio, lab)
pip install flowmason

# Start Studio
fm studio start

# Install VSCode extension
code --install-extension flowmason.flowmason
```

## Quick Start

```bash
# Initialize a new project
fm init my-project
cd my-project

# Create your first pipeline
# Edit pipelines/hello.pipeline.json

# Run the pipeline
fm run pipelines/hello.pipeline.json

# Start Studio for visual editing
fm studio start
```

## Docker Deployment

```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Staging
docker-compose -f docker-compose.staging.yml up

# Production
docker-compose -f docker-compose.prod.yml up
```

## Next Steps

1. [Quick Start Guide](02-getting-started/quickstart.md) - Build your first pipeline
2. [Tutorials](tutorials/README.md) - Step-by-step learning path
3. [Core Concepts](03-concepts/architecture-overview.md) - Understand how FlowMason works
4. [VSCode Extension](07-vscode-extension/overview.md) - Master the development environment
5. [Marketplace](06-studio/marketplace.md) - Discover pipeline templates
