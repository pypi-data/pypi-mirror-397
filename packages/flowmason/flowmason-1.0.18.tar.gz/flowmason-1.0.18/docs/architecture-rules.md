# FlowMason Architecture Rules

**Version:** 1.0
**Last Updated:** 2025-12-10

This document defines the non-negotiable architectural principles that govern FlowMason's design. Every implementation decision must align with these rules.

---

## The Five Core Rules

### 1. Zero Hardcoded Component Types

**Rule:** FlowMason's codebase must never contain hardcoded component types like "generator", "critic", "filter", etc.

**Why:** This ensures the system remains pure infrastructure. Components are external packages that plug into the system.

**Implementation:**
- All components load from `.fmpkg` packages via the registry
- The registry dynamically discovers and loads components
- No `if component_type == "generator"` logic anywhere
- Core components (generator, critic, etc.) are packages in `dist/packages/`

**Violation Example (BAD):**
```python
# This violates the rule!
if stage.type == "generator":
    result = self._execute_generator(stage)
elif stage.type == "critic":
    result = self._execute_critic(stage)
```

**Correct Approach (GOOD):**
```python
# Universal execution - works for ANY component type
component_class = registry.get_component_class(stage.type)
component = component_class()
result = await component.execute(input, context)
```

---

### 2. No Code Editing in Studio

**Rule:** Studio is a composition tool, not an IDE. Users never write or edit code in the UI.

**Why:** Keeps Studio simple and accessible. Code belongs in packages, composition belongs in Studio.

**Implementation:**
- Studio UI provides drag-and-drop pipeline building
- Configuration is done via forms, not code editors
- Template syntax (`{{input.field}}`) for data mapping
- Components are installed, not created in Studio

**What Studio DOES:**
- Visual pipeline composition (canvas with nodes and edges)
- Stage configuration via forms
- Input mapping with template variables
- Pipeline execution and monitoring
- Package management (upload/install)

**What Studio DOES NOT:**
- Code editors or IDEs
- Inline function definitions
- Custom script execution
- Component code modification

---

### 3. Universal Executor (One Path for All)

**Rule:** There must be ONE execution path that handles ALL component types identically.

**Why:** Prevents special-case code that fragments the architecture. Makes the system predictable and testable.

**Implementation:**
- `UniversalExecutor.execute_component()` handles any component type
- `DAGExecutor` orchestrates pipelines using the universal executor
- No type-specific execution branches

**The Universal Flow:**
```
1. Load component class from registry
2. Map config to Input model via InputMapper
3. Execute component with context
4. Validate output
5. Return result with metrics
```

**Violation Example (BAD):**
```python
class DAGExecutor:
    def execute(self, pipeline):
        for stage in pipeline.stages:
            if stage.type.endswith("_node"):
                result = self._execute_node(stage)
            else:
                result = self._execute_operator(stage)
```

**Correct Approach (GOOD):**
```python
class DAGExecutor:
    def execute(self, pipeline):
        for stage in pipeline.stages:
            result = self.executor.execute_component(stage, upstream)
```

---

### 4. Pipelines Are APIs

**Rule:** Every pipeline automatically becomes a versioned HTTP API endpoint.

**Why:** Maximizes value - pipelines aren't just workflows, they're deployable products.

**Implementation:**
- Pipelines expose execution endpoints via `/api/v1/pipelines/{id}/run`
- Future: Public API with `/api/pipelines/{name}/run` and API keys
- Input/output schemas become OpenAPI specs
- Versioning enables backward compatibility

**Pipeline Lifecycle:**
```
Design (Studio) → Save (Version) → Deploy → Consume (API)
```

**Example:**
```bash
# Execute a pipeline via API
curl -X POST http://localhost:8999/api/v1/pipelines/abc123/run \
  -H "Content-Type: application/json" \
  -d '{"input": {"text": "Hello world"}}'

# Response
{
  "run_id": "run_xyz",
  "status": "completed",
  "output": {...},
  "usage": {"tokens": 150, "cost_usd": 0.01}
}
```

---

### 5. Core Packages Are Just Packages

**Rule:** Components that ship with FlowMason (generator, filter, etc.) are regular packages with no special treatment.

**Why:** Proves the package system works. Ensures third-party packages are first-class citizens.

**Implementation:**
- Core components live in `lab/flowmason_lab/`
- They're built with `scripts/package_builder.py`
- They're installed to `dist/packages/` as `.fmpkg` files
- Registry loads them the same way it loads any other package

**Core Components (12 total):**
| Type | Components |
|------|------------|
| Nodes | generator, critic, improver, synthesizer, selector |
| Operators | http_request, json_transform, filter, loop, schema_validate, variable_set, logger |

---

## Secondary Principles

### Provider Abstraction

LLM providers (Anthropic, OpenAI, Google, Groq) are accessed through a unified interface:

```python
# Nodes use context.llm for LLM access
response = await context.llm.generate_async(
    prompt="...",
    system_prompt="...",
    temperature=0.7
)
```

### Schema-Driven Configuration

All data flows through typed schemas:
- Component inputs/outputs are Pydantic models
- Pipeline configs are validated before execution
- Templates (`{{variable}}`) enable dynamic data mapping

### Observability Built-In

Every execution produces:
- Trace spans per component
- Token usage metrics
- Cost estimates
- Timing data

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     FlowMason Studio                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Component │  │ Pipeline │  │ Pipeline │  │ Package  │   │
│  │ Palette  │  │  Canvas  │  │ Executor │  │ Manager  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                       Studio API                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Registry    │  │ Pipelines   │  │ Execution           │ │
│  │ Routes      │  │ Routes      │  │ Routes              │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    FlowMason Core                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Component    │  │ Config       │  │ Universal        │  │
│  │ Registry     │  │ System       │  │ Executor         │  │
│  │              │  │              │  │                  │  │
│  │ - Load pkgs  │  │ - Templates  │  │ - Execute ANY    │  │
│  │ - Metadata   │  │ - Type coerce│  │   component      │  │
│  │ - List       │  │ - Validation │  │ - DAG execution  │  │
│  └──────┬───────┘  └──────────────┘  └────────┬─────────┘  │
│         │                                      │            │
│         │              ┌──────────────────────┐│            │
│         │              │ LLM Providers        ││            │
│         │              │ - Anthropic          ││            │
│         │              │ - OpenAI             ││            │
│         │              │ - Google             ││            │
│         │              │ - Groq               ││            │
│         │              └──────────────────────┘│            │
└─────────┼──────────────────────────────────────┼────────────┘
          │                                      │
          ▼                                      ▼
   ┌──────────────┐                    ┌──────────────┐
   │   .fmpkg     │                    │    LLM       │
   │   Packages   │                    │    APIs      │
   └──────────────┘                    └──────────────┘
```

---

## Checklist for New Code

Before merging any code, verify:

- [ ] No hardcoded component type names?
- [ ] Uses registry to load components?
- [ ] No UI code editing features?
- [ ] Uses universal executor path?
- [ ] Pipeline exposes API endpoint?
- [ ] Core component changes are in `lab/`, not in core?

---

## FAQ

**Q: Can I add a utility function that only works for generator nodes?**
A: No. Any functionality must work for ALL component types via the universal executor.

**Q: Can I add a "quick script" feature to Studio?**
A: No. Script execution belongs in components, not Studio. Create a package instead.

**Q: Should I add special handling for the "filter" operator in the executor?**
A: No. The filter operator is a package. It loads and executes like any other component.

**Q: How do I add a new built-in component?**
A: Create it in `lab/flowmason_lab/`, build it with `package_builder.py`, install the `.fmpkg`.
