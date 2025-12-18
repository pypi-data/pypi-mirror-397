# FlowMason Product Vision

## Executive Summary

FlowMason is an AI pipeline orchestration platform that enables developers to design, build, debug, and deploy intelligent workflows. The platform uses a **Salesforce DX-style hybrid model**:

- **Development**: File-based pipelines (`.pipeline.json`) in VSCode with Git version control
- **Deployment**: Push to staging/production orgs where pipelines run from databases
- **Runtime**: Backend APIs expose pipelines for consumption

**The goal**: Make building AI pipelines feel as natural as building Salesforce applications.

## The Platform Model

### Environment Overview

| Environment | Storage | Execution | Use Case |
|-------------|---------|-----------|----------|
| **Local (File Mode)** | `.pipeline.json` files | Direct from files | Fast development |
| **Local (Org Mode)** | SQLite | From local DB | Test DB behavior |
| **Staging Org** | PostgreSQL | From DB via API | Integration testing |
| **Production Org** | PostgreSQL | From DB via API | Live runtime |

### Developer Workflow

1. **Develop locally** - Edit `.pipeline.json` files in VSCode, run from files
2. **Version with Git** - Commit, push, create pull requests
3. **Deploy to staging** - `flowmason deploy --target staging`
4. **Test in staging** - Run pipelines via API
5. **Deploy to production** - `flowmason deploy --target production`
6. **Consume via API** - REST/WebSocket endpoints for pipeline execution

See [The Hybrid Model](hybrid-model.md) for complete details on the deployment architecture.

## VSCode-Native Development

### Custom Editor Provider

Pipelines open in a visual canvas editor, not as raw JSON:

- Double-click `.pipeline.json` → Opens visual editor
- Ctrl+S → Saves to file (auto-format)
- Native undo/redo via VSCode
- Multiple pipelines in tabs
- Split view: canvas + JSON

### Debug Adapter Protocol (DAP)

Full debugging experience for pipelines:

**Debug Panel Features:**

| Panel | Contents |
|-------|----------|
| Variables | Current stage inputs, outputs, context |
| Watch | Custom expressions to monitor |
| Call Stack | Pipeline → Stage → Sub-pipeline |
| Breakpoints | List of all breakpoints |
| Prompt Editor | Edit and re-run prompts live |

**Breakpoint Types:**
- Stage breakpoints (pause before stage executes)
- Conditional breakpoints (`input.text.length > 1000`)
- Logpoints (log without pausing)
- Exception breakpoints (pause on error)

### Deep Debugging: Prompt Iteration

The killer feature - edit prompts during debug:

```
┌─────────────────────────────────────────────────────────────────┐
│ Debug: Paused at "summarize-content"                            │
├─────────────────────────┬───────────────────────────────────────┤
│ VARIABLES               │ PROMPT EDITOR                         │
│ ├─ input                │ ┌───────────────────────────────────┐ │
│ │  └─ text: "The q..."  │ │ System:                           │ │
│ │                       │ │ You are a concise summarizer.     │ │
│ ├─ context              │ │                                   │ │
│ │  └─ run_id: "r-123"   │ │ User:                             │ │
│ │                       │ │ Summarize this text in            │ │
│ └─ output: (pending)    │ │ {{max_length}} words or less:     │ │
│                         │ │                                   │ │
├─────────────────────────┤ │ {{text}}                          │ │
│ PROMPT VERSIONS         │ │                                   │ │
│ ├─ v1 (original)        │ └───────────────────────────────────┘ │
│ ├─ v2 (shorter)         │                                       │
│ └─ v3 (current) ●       │ [Edit] [Reset] [Save as v4]           │
└─────────────────────────┴───────────────────────────────────────┘
```

**Workflow:**
1. Pause at LLM stage
2. See the prompt being sent
3. Edit prompt directly
4. Re-run just that stage
5. Compare output to previous versions
6. Save successful prompt as new version
7. Continue execution

### Test Explorer Integration

Native VSCode test UI with:

| Test Type | Description |
|-----------|-------------|
| Unit | Single component with mock input |
| Integration | Component chains |
| Sub-pipeline | Partial DAG testing |
| E2E | Full pipeline execution |
| Regression | Golden file comparison |
| Prompt | A/B testing prompts |

## File-Based Pipelines

### Pipeline File Format (`.pipeline.json`)

```json
{
  "name": "content-pipeline",
  "version": "1.0.0",
  "description": "Process and summarize content",
  "stages": [
    {
      "id": "fetch",
      "component": "http-request",
      "config": {
        "url": "{{input.url}}",
        "method": "GET"
      }
    },
    {
      "id": "summarize",
      "component": "generator",
      "depends_on": ["fetch"],
      "config": {
        "prompt": "Summarize: {{fetch.output.body}}",
        "max_tokens": 500
      }
    }
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "url": { "type": "string", "format": "uri" }
    },
    "required": ["url"]
  }
}
```

### Project Structure

```
my-flowmason-project/
├── flowmason.json              # Project manifest
├── .flowmason/
│   ├── state.json              # IDE state (tabs, zoom, selection)
│   ├── cache/                  # Registry cache
│   ├── runs/                   # Local execution history
│   └── prompts/                # Prompt version history
├── pipelines/
│   ├── main.pipeline.json
│   └── tests/
│       └── main.test.json
├── components/
│   ├── nodes/
│   └── operators/
└── packages/                   # Built .fmpkg files
```

### Project Manifest (`flowmason.json`)

```json
{
  "name": "my-flowmason-project",
  "version": "1.0.0",
  "description": "My AI pipeline project",
  "main": "pipelines/main.pipeline.json",
  "components": {
    "include": ["components/**/*.py"]
  },
  "providers": {
    "default": "anthropic",
    "anthropic": { "model": "claude-sonnet-4-20250514" }
  },
  "testing": {
    "timeout": 30000,
    "retries": 2
  }
}
```

## Packaging (.fmpkg)

Self-contained deployable units, like Java WAR files:

```
my-workflow-1.0.0.fmpkg
├── manifest.json           # Metadata, version, dependencies
├── pipelines/              # All pipeline definitions
├── components/             # Custom nodes and operators
├── prompts/                # Prompt templates
├── tests/                  # Test definitions
├── config/                 # Environment configs
└── assets/                 # Additional resources
```

### Package Commands

```bash
flowmason pack                    # Build .fmpkg
flowmason pack --version 1.2.0    # Build with version
flowmason install package.fmpkg   # Install locally
flowmason deploy --target staging # Deploy to org
```

## CI/CD Integration

### GitHub Actions

```yaml
name: FlowMason CI/CD
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: flowmason/setup-action@v1
      - run: flowmason test --coverage

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    steps:
      - run: flowmason deploy --target staging

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - run: flowmason deploy --target production
```

## Migration Strategy

### Current State
- Browser-based Pipeline Builder
- Pipelines stored in SQLite database
- VSCode extension opens browser

### Target State
- VSCode-native Pipeline Builder
- Pipelines as `.pipeline.json` files (local) + database (staging/prod)
- Full debugging/testing integration
- Deploy/pull workflow

### Migration Path

1. **Parallel operation** - Keep browser version working during transition
2. **Export tool** - Export existing pipelines from DB to files
3. **Feature parity** - Match browser functionality in VSCode
4. **Deploy/pull commands** - Enable org management
5. **Complete transition** - VSCode becomes primary interface
