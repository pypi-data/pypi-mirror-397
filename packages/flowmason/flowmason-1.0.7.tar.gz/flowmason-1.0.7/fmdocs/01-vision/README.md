# FlowMason Vision

## Overview

FlowMason is an AI pipeline orchestration platform that enables developers to design, build, debug, and deploy intelligent workflows. The platform uses a **Salesforce DX-style hybrid model**:

- **Development**: File-based pipelines (`.pipeline.json`) in VSCode with Git version control
- **Deployment**: Push to staging/production orgs where pipelines run from databases
- **Runtime**: Backend APIs expose pipelines for consumption

**Goal:** Make building AI pipelines feel as natural as building Salesforce applications.

## Documents in This Section

| Document | Description |
|----------|-------------|
| [Hybrid Model](hybrid-model.md) | The Salesforce DX-style deployment architecture |
| [Product Vision](product-vision.md) | Full vision for VSCode-native FlowMason |
| [Roadmap](roadmap.md) | Implementation phases and milestones |
| [Edition Tiers](edition-tiers.md) | Basic, Advanced, Enterprise features |

## The Platform Model

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

### Environments

| Environment | Storage | Execution | Use Case |
|-------------|---------|-----------|----------|
| **Local (File Mode)** | `.pipeline.json` files | Direct from files | Fast development |
| **Local (Org Mode)** | SQLite | From local DB | Test DB behavior |
| **Staging Org** | PostgreSQL | From DB via API | Integration testing |
| **Production Org** | PostgreSQL | From DB via API | Live runtime |

## The Problem

Current browser-based pipeline builders suffer from:

| Problem | Impact |
|---------|--------|
| Context switching | Jump between IDE and browser constantly |
| No version control | Pipelines trapped in databases, not Git |
| Limited debugging | Basic logging, no breakpoints |
| No IDE integration | Miss autocomplete, linting, refactoring |
| Collaboration friction | Can't code review pipelines |
| CI/CD gaps | Manual deployment, no automation |
| No deployment model | Local only, no staging/production |

## The Solution

### VSCode-Native Development

Transform VSCode into the FlowMason IDE:

```
┌─────────────────────────────────────────────────────────────────────┐
│  VSCode + FlowMason                                                 │
├──────────┬────────────────────────────────────────┬─────────────────┤
│ Explorer │  main.pipeline.json (Custom Editor)    │  Debug Panel    │
│ ┌──────┐ │  ┌──────────────────────────────────┐  │  ┌───────────┐  │
│ │ src/ │ │  │     [fetch]──►[process]          │  │  │ Variables │  │
│ │ pipe │ │  │        │          │              │  │  │ input: {} │  │
│ │ comp │ │  │        ▼          ▼              │  │  │ output: {}│  │
│ └──────┘ │  │     [clean]──►[summarize]──►[out]│  │  └───────────┘  │
├──────────┤  └──────────────────────────────────┘  │  ┌───────────┐  │
│FlowMason │                                        │  │Breakpoints│  │
│ ┌──────┐ │  ──────────────────────────────────────│  │ ● stage-2 │  │
│ │Comps │ │  Problems │ Output │ Debug Console     │  │ ○ stage-4 │  │
│ │Pipes │ │  [FlowMason] Stage 'process' complete  │  └───────────┘  │
│ │Tests │ │  [FlowMason] Running 'summarize'...    │                 │
│ └──────┘ │                                        │                 │
└──────────┴────────────────────────────────────────┴─────────────────┘
```

### Org-Based Deployment

Deploy pipelines to staging and production environments:

```bash
# Develop locally
flowmason run pipelines/main.pipeline.json

# Deploy to staging
flowmason deploy --target staging

# Test in staging
flowmason run --target staging --pipeline main

# Deploy to production
flowmason deploy --target production
```

## Key Principles

1. **File-based development** - Pipelines are `.pipeline.json` files, Git-friendly
2. **Database-backed runtime** - Staging/production use PostgreSQL for performance
3. **Project-based** - FlowMason projects with manifest, state, history
4. **Native debugging** - VSCode Debug Adapter Protocol (DAP)
5. **Integrated testing** - VSCode Test Explorer for pipeline tests
6. **Packaged deployment** - `.fmpkg` bundles like Java WAR files
7. **CI/CD ready** - GitHub Actions, tasks, automation

## Key Differentiators

| Traditional Tools | FlowMason Vision |
|-------------------|------------------|
| Browser-based builder | VSCode-native custom editor |
| Database storage only | Files (dev) + Database (staging/prod) |
| Console logging | Debug Adapter Protocol (breakpoints, step-through) |
| No testing framework | VSCode Test Explorer integration |
| Manual deployment | `flowmason deploy` with CI/CD |
| No environments | Local → Staging → Production |
| Single user | Team collaboration with enterprise features |
