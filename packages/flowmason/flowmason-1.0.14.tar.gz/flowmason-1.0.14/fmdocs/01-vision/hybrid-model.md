# The Hybrid Model (Salesforce DX-Style)

## Overview

FlowMason uses a **hybrid deployment model** inspired by Salesforce DX:

- **Development**: File-based pipelines (`.pipeline.json`) in VSCode with Git version control
- **Deployment**: Push to staging/production orgs where pipelines run from databases
- **Runtime**: Backend APIs expose pipelines for consumption

**The goal**: Make building AI pipelines feel as natural as building Salesforce applications.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│  LOCAL DEVELOPMENT                                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  .pipeline.json files (Git repo)                             │  │
│  │  - Source of truth during development                        │  │
│  │  - VSCode Custom Editor for visual editing                   │  │
│  │  - Debug with DAP, prompt iteration                          │  │
│  └──────────────────────────┬───────────────────────────────────┘  │
│                             │                                       │
│            ┌────────────────┴────────────────┐                     │
│            │                                 │                      │
│            ▼                                 ▼                      │
│  ┌─────────────────┐              ┌─────────────────────┐          │
│  │  FILE MODE      │              │  ORG MODE (optional)│          │
│  │  (Default)      │              │                     │          │
│  │  F5 = Run from  │              │  flowmason deploy   │          │
│  │  file directly  │              │  --local            │          │
│  │  Fast iteration │              │  Test DB behavior   │          │
│  └─────────────────┘              └─────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
    flowmason deploy            flowmason deploy
    --target staging            --target production
              │                           │
              ▼                           ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│  STAGING ORG            │  │  PRODUCTION ORG         │
│  - PostgreSQL DB        │  │  - PostgreSQL DB        │
│  - Backend API          │  │  - Backend API          │
│  - Pipelines as records │  │  - Pipelines as records │
│  - Full execution       │  │  - Full execution       │
│  - Studio UI (optional) │  │  - Studio UI (optional) │
└─────────────────────────┘  └─────────────────────────┘
```

## Environment Comparison

| Environment | Storage | Execution | Use Case |
|-------------|---------|-----------|----------|
| **Local (File Mode)** | `.pipeline.json` files | Direct from files | Fast development |
| **Local (Org Mode)** | SQLite | From local DB | Test DB behavior |
| **Staging Org** | PostgreSQL | From DB via API | Integration testing |
| **Production Org** | PostgreSQL | From DB via API | Live runtime |

## Like Salesforce DX

| Salesforce DX | FlowMason |
|---------------|-----------|
| `force-app/` directory | `pipelines/` directory |
| `.cls`, `.trigger` files | `.pipeline.json` files |
| `sfdx force:org:login` | `flowmason org:login` |
| `sfdx force:source:push` | `flowmason deploy` |
| `sfdx force:source:pull` | `flowmason pull` |
| Scratch org (dev) | Local backend (file mode) |
| Sandbox (staging) | Staging org |
| Production org | Production org |
| Metadata in org DB | Pipelines in org DB |

## CLI Commands

### Org Management

```bash
# Authorize to an org (like sf org login)
flowmason org:login --alias staging --instance-url https://staging.flowmason.com
flowmason org:login --alias production --instance-url https://prod.flowmason.com

# List authorized orgs
flowmason org:list
# Output:
#   ALIAS       INSTANCE URL                    DEFAULT
#   staging     https://staging.flowmason.com    ✓
#   production  https://prod.flowmason.com

# Set default org
flowmason org:default staging

# View org details
flowmason org:display --target staging

# Logout from org
flowmason org:logout --target staging
```

### Deploy (Local → Org)

```bash
# Deploy all pipelines to default org
flowmason deploy

# Deploy specific pipeline
flowmason deploy pipelines/main.pipeline.json

# Deploy to specific org
flowmason deploy --target production

# Deploy to local DB (test org mode)
flowmason deploy --local

# Preview what would be deployed (dry run)
flowmason deploy --dry-run

# Deploy with validation only (no execution test)
flowmason deploy --check-only
```

### Pull (Org → Local)

```bash
# Pull all pipelines from default org
flowmason pull

# Pull specific pipeline
flowmason pull --pipeline support-triage

# Pull from specific org
flowmason pull --target production

# Preview what would be pulled
flowmason pull --dry-run
```

### Local Execution (File Mode)

```bash
# Run pipeline from file (no deploy needed)
flowmason run pipelines/main.pipeline.json

# Run with input
flowmason run pipelines/main.pipeline.json --input '{"url": "https://..."}'

# Run with input file
flowmason run pipelines/main.pipeline.json --input-file test-input.json

# Debug mode (starts debug server, VSCode connects)
flowmason run pipelines/main.pipeline.json --debug
```

### Org Execution (From Deployed Pipelines)

```bash
# Run on org (must be deployed first)
flowmason run --target staging --pipeline main
```

### Component Management

```bash
# Package components
flowmason pack --output my-components-1.0.0.fmpkg

# Install package locally
flowmason install my-components-1.0.0.fmpkg

# Deploy package to org
flowmason deploy:package my-components-1.0.0.fmpkg --target staging

# List components in org
flowmason component:list --target staging
```

## VSCode Integration with Orgs

```
┌──────────────────────────────────────────────────────────────────────┐
│ VSCode                                                               │
├──────────────────────────────────────────────────────────────────────┤
│ FLOWMASON ORGS                      │  main.pipeline.json            │
│ ├─ 🟢 staging (default)             │  ┌────────────────────────┐    │
│ │   ├─ Status: Connected            │  │    [Visual Editor]     │    │
│ │   ├─ Pipelines: 5 deployed        │  │                        │    │
│ │   └─ Last sync: 2 min ago         │  │    [A]──►[B]──►[C]     │    │
│ ├─ 🟡 production                    │  │                        │    │
│ │   ├─ Status: Connected            │  └────────────────────────┘    │
│ │   ├─ Pipelines: 3 deployed        │                                │
│ │   └─ Last sync: 1 hour ago        │  ┌────────────────────────────┐│
│ └─ ⚪ local                         │  │ [▶ Run Local] [Deploy ▼]   ││
│     └─ File mode (no DB)            │  │  ├─ Deploy to staging      ││
│                                     │  │  ├─ Deploy to production   ││
│ LOCAL PIPELINES                     │  │  └─ Deploy to local DB     ││
│ ├─ main.pipeline.json ✎ (modified)  │  └────────────────────────────┘│
│ ├─ etl.pipeline.json ✓ (synced)     │                                │
│ └─ support.pipeline.json ✎          │  Status: Modified locally      │
│                                     │  Last deployed: staging (2 min)│
│ ✎ = Modified locally, not deployed  │                                │
│ ✓ = In sync with default org        │                                │
└─────────────────────────────────────┴────────────────────────────────┘
```

## Deployment Flow

The typical developer workflow:

### 1. DEVELOP (Local, File Mode)

```
┌─────────────────────────────────────────┐
│ Edit .pipeline.json in VSCode           │
│ F5 → Run from file (fast iteration)     │
│ Debug, iterate, test locally            │
└─────────────────────────────────────────┘
```

- Edit pipelines visually in VSCode Custom Editor
- Run directly from files (no deploy needed)
- Fast iteration with hot reload
- Debug with breakpoints

### 2. COMMIT (Git)

```
┌─────────────────────────────────────────┐
│ git add pipelines/                      │
│ git commit -m "Add support pipeline"    │
│ git push                                │
└─────────────────────────────────────────┘
```

- Version control with Git
- Code review via pull requests
- Collaboration with team

### 3. DEPLOY TO STAGING

```
┌─────────────────────────────────────────┐
│ flowmason deploy --target staging       │
│ - Validates pipeline                    │
│ - Converts to DB records                │
│ - Deploys to staging org                │
└─────────────────────────────────────────┘
```

- Validation before deployment
- Conversion from file to database records
- Full integration testing environment

### 4. TEST IN STAGING

```
┌─────────────────────────────────────────┐
│ flowmason run --target staging          │
│   --pipeline support-triage             │
│ - Runs from staging DB                  │
│ - Full production-like behavior         │
└─────────────────────────────────────────┘
```

- Test in production-like environment
- API endpoints available
- Full observability

### 5. DEPLOY TO PRODUCTION

```
┌─────────────────────────────────────────┐
│ flowmason deploy --target production    │
│ - Same pipeline, production org         │
│ - APIs now available for consumers      │
└─────────────────────────────────────────┘
```

- Promote from staging to production
- Same pipeline definition
- Production APIs activated

### 6. CONSUME VIA API

```
┌─────────────────────────────────────────┐
│ POST https://prod.flowmason.com/api/v1/  │
│   pipelines/support-triage/run          │
│ Body: { "input": {...} }                │
└─────────────────────────────────────────┘
```

- REST API for pipeline execution
- WebSocket for real-time updates
- Full metrics and logging

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/flowmason.yml
name: FlowMason CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup FlowMason
        uses: flowmason/setup-action@v1

      - name: Validate pipelines
        run: flowmason validate pipelines/

      - name: Run tests (file mode)
        run: flowmason test --all

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup FlowMason
        uses: flowmason/setup-action@v1

      - name: Login to staging
        run: flowmason org:login --alias staging --auth-url ${{ secrets.STAGING_AUTH_URL }}

      - name: Deploy to staging
        run: flowmason deploy --target staging

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Setup FlowMason
        uses: flowmason/setup-action@v1

      - name: Login to production
        run: flowmason org:login --alias production --auth-url ${{ secrets.PROD_AUTH_URL }}

      - name: Deploy to production
        run: flowmason deploy --target production
```

## Why Hybrid?

### Benefits of File-Based Development

- **Git version control** - Track changes, review, rollback
- **Fast iteration** - No deploy needed for local testing
- **IDE integration** - IntelliSense, diagnostics, refactoring
- **Collaboration** - Pull requests, code review
- **Offline work** - No server connection needed

### Benefits of Database Runtime

- **Performance** - Optimized queries, caching
- **API exposure** - REST/WebSocket endpoints
- **Scalability** - Multiple instances, load balancing
- **Observability** - Metrics, logging, tracing
- **Management** - Studio UI for monitoring

### The Best of Both Worlds

FlowMason gives you:
- Developer experience of file-based tools
- Production capabilities of database-backed systems
- Seamless transition between local and deployed
