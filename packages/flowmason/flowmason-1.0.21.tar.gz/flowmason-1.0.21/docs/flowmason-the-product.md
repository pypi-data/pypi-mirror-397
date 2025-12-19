# FlowMason: Complete Vision & Implementation Plan

## Document Purpose

This document captures the **complete, corrected vision** for FlowMason and provides a comprehensive implementation plan for Claude Code to execute. This is the definitive reference for what FlowMason is and how to build it.

------

## Executive Summary

**FlowMason is an API infrastructure platform for AI workflows.**

It is NOT a development tool, IDE, or low-code platform. It IS a deployment target for packaged AI components that get composed into pipelines and exposed as APIs.

**The Model:**

- **Development happens in VS Code** (outside FlowMason)
- **Components get packaged** as .fmpkg files
- **Packages get deployed** to FlowMason instances
- **Pipelines get composed** in Studio UI from deployed components
- **Pipelines get exposed** as versioned HTTP APIs
- **Consumers call APIs** from their applications

**The Salesforce Analogy:** FlowMason is to AI workflows what Salesforce is to CRM workflows: a platform where you deploy code, compose flows, and expose APIs. Zero code editing happens in the platform UI.

------

# Part 1: The Complete Architecture Vision

## The Three-Layer Model

### Layer 1: Development (Outside FlowMason)

**Environment:** Developer's local machine (VS Code + Terminal)

**Activities:**

1. Write nodes and operators in Python
2. Define typed Input/Output schemas with Pydantic
3. Implement execute() methods with business logic
4. Write tests (snapshot tests + contract tests)
5. Run local validation: `fm test`
6. Package components: `fm lab-package` → `.fmpkg` files

**Outputs:**

- Validated, tested, packaged components (.fmpkg files)

**Key Principle:**

- **ALL code development happens here**
- No code is written in FlowMason Studio
- No exceptions

------

### Layer 2: FlowMason Platform (The Infrastructure)

**Environment:** FlowMason instances (test/staging/production)

**Components:**

#### A. Package Registry

- Receives deployed .fmpkg files
- Extracts and validates manifests
- Registers components (nodes, operators, future types)
- Manages versions and dependencies
- **Contains ZERO hardcoded components**

#### B. Studio UI (Composition Interface)

**Purposes:**

1. **Package Management:** Upload, view, update, remove packages
2. **Pipeline Composition:** Drag-and-drop components, connect flows
3. **Configuration:** Set prompts, field mappings, provider preferences
4. **Testing:** Run sample inputs, view traces, check costs
5. **API Publishing:** Expose pipelines as versioned endpoints
6. **Observability:** Monitor usage, costs, errors, performance

**NOT for:**

- ❌ Writing code
- ❌ Editing node logic
- ❌ Implementing operators
- ❌ Running Python tests
- ❌ Any form of code editing

#### C. Execution Runtime

- Loads components dynamically from registry
- Maps pipeline config (JSON) to component Input schemas (Pydantic)
- Executes through provider abstraction
- Returns typed Output
- Tracks tokens, costs, timing
- Generates execution traces

#### D. API Gateway

- Each pipeline → HTTP endpoint
- Version management (v1, v2, etc.)
- Authentication & authorization
- Rate limiting & quotas
- OpenAPI spec generation
- Webhook support

**Outputs:**

- Running pipelines accessible as APIs

**Key Principle:**

- FlowMason is **pure infrastructure**
- It executes what's deployed to it
- It has no opinions about what components do
- Everything is dynamic

------

### Layer 3: Consumer Applications (Outside FlowMason)

**Environment:** Customer's applications (web apps, mobile, backend services)

**Activities:**

1. Call pipeline APIs: `POST /api/pipelines/{id}/run`
2. Send JSON payloads matching pipeline input schema
3. Receive JSON responses matching pipeline output schema
4. Build user experiences on top of AI capabilities
5. Integrate with their systems (CRM, support, etc.)

**Examples:**

- Zendesk webhook → FlowMason triage API → Auto-route ticket
- Web app → FlowMason content generation API → Display to user
- Slack bot → FlowMason assistant API → Respond to user

**Key Principle:**

- Consumers don't know or care about FlowMason internals
- They only interact via HTTP APIs
- FlowMason is invisible infrastructure

------

## Component Model: Nodes vs Operators

### Nodes (AI-Focused Components)

**Purpose:** Steps that interact with LLM providers

**Characteristics:**

- Decorated with `@node`
- Have nested `Input` and `Output` classes (inherit from `NodeInput`/`NodeOutput`)
- Implement `async execute(self, input, context)`
- Call providers via `context.providers["provider_name"].call()`
- Enforce structured outputs (JSON schemas)

**Examples:**

- Generator: Create text from prompt
- Critic: Evaluate and provide feedback
- Improver: Refine based on criteria
- Synthesizer: Combine multiple inputs
- Selector: Choose best option from set
- SupportTriageNode: Custom business logic for support tickets
- SalesforceFollowupNode: Domain-specific Salesforce integration

**Key Insight:**

- Some nodes are "core" (provided by you)
- Some nodes are "custom" (created by customers)
- **Architecturally, there is NO difference**
- Both are just packages deployed to registry

------

### Operators (Non-AI Components)

**Purpose:** Utility steps that don't call LLMs

**Characteristics:**

- Decorated with `@operator`
- Have `OperatorInput` and `OperatorOutput`
- Implement non-LLM logic
- Examples: HTTP calls, data transforms, filters, loops

**Examples:**

- HTTPRequestOperator: Make API calls
- JSONTransformOperator: Reshape data
- FilterOperator: Conditional logic
- LoopOperator: Iterate over collections
- SchemaValidateOperator: Validate against JSON schema
- VariableSetOperator: Set context variables
- LoggerOperator: Emit logs

**Key Insight:**

- Operators are "glue" between nodes
- They enable complex workflows
- They integrate FlowMason with external systems

------

## Core vs Custom Packages

### Core Packages (Managed by FlowMason Team)

**What they are:**

- Foundation components everyone needs
- Developed by FlowMason team
- Rigorously tested and maintained
- Versioned and documented
- Labeled as "core" or "managed"

**Examples:**

```
@flowmason/generator
@flowmason/critic
@flowmason/improver
@flowmason/synthesizer
@flowmason/selector
@flowmason/http-request
@flowmason/json-transform
@flowmason/filter
@flowmason/loop
```

**Distribution:**

- Pre-installed on new instances (auto-deployed)
- OR available in Core Package Library for manual install
- Versioned independently
- Updated by FlowMason team

**Business Model:**

- Included in base platform pricing
- Some premium integrations sold separately:
  - `@flowmason/salesforce` - $500/month
  - `@flowmason/zendesk` - $300/month
  - `@flowmason/servicenow` - $400/month

**Key Insight:**

- These are still just packages
- No special treatment in executor
- Architecturally identical to custom packages
- Just maintained and distributed by you

------

### Custom Packages (Created by Customers)

**What they are:**

- Domain-specific components
- Proprietary business logic
- Customer-specific integrations
- Private to that customer's instance

**Examples:**

```
acme-corp/support-classifier
acme-corp/product-recommender
acme-corp/internal-tool-integration
```

**Distribution:**

- Developed by customer developers
- Packaged by customer
- Deployed only to customer's instance
- Not visible to other customers

**Key Insight:**

- This is where customers add unique value
- FlowMason enables them to build custom logic
- Packages are portable (can move between instances)

------

## Pipeline Composition Model

### Pipelines Are APIs

**Pipeline Definition:**

```json
{
  "id": "support-triage",
  "name": "Support Ticket Triage",
  "version": "1.0.0",
  "description": "Automatically classify and route support tickets",
  
  "input_schema": {
    "type": "object",
    "properties": {
      "ticket_text": {"type": "string", "description": "Ticket content"},
      "customer_id": {"type": "string"},
      "metadata": {"type": "object"}
    },
    "required": ["ticket_text"]
  },
  
  "output_schema": {
    "type": "object",
    "properties": {
      "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
      "category": {"type": "string"},
      "assigned_team": {"type": "string"},
      "confidence": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "required": ["priority", "category", "assigned_team"]
  },
  
  "stages": [
    {
      "id": "classify",
      "type": "support_triage",
      "component_package": "acme-corp/support-classifier@1.0.0",
      "provider": "anthropic",
      "input_mapping": {
        "text": "{{input.ticket_text}}",
        "metadata": "{{input.metadata}}"
      }
    },
    {
      "id": "validate",
      "type": "schema_validate",
      "component_package": "@flowmason/schema-validate@1.0.0",
      "schema_ref": "output_schema"
    }
  ]
}
```

**API Endpoint:**

```
POST https://acme.flowmason.io/api/pipelines/support-triage/run
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "ticket_text": "Customer can't login after password reset",
  "customer_id": "12345",
  "metadata": {
    "created_at": "2024-12-09T10:30:00Z",
    "channel": "email"
  }
}
```

**API Response:**

```json
{
  "run_id": "run_abc123",
  "pipeline_id": "support-triage",
  "pipeline_version": "1.0.0",
  "status": "completed",
  "result": {
    "priority": "high",
    "category": "authentication",
    "assigned_team": "engineering",
    "confidence": 0.92
  },
  "usage": {
    "total_tokens": 1250,
    "input_tokens": 450,
    "output_tokens": 800,
    "cost_usd": 0.0234,
    "duration_ms": 850
  },
  "trace_url": "/api/runs/run_abc123/trace"
}
```

------

## Deployment & Environment Model

### Three-Tier Environment Strategy

**Test Instance** (like Salesforce Developer Org)

- Purpose: Development and validation
- Data: Fake/synthetic
- Components: Latest versions, experimental
- Pipelines: In-progress, being tested
- Usage: High churn, constant updates
- Downtime: Acceptable

**Staging Instance** (like Salesforce Sandbox)

- Purpose: Pre-production validation
- Data: Production-like (sanitized)
- Components: Release candidates
- Pipelines: Approved for production
- Usage: Integration testing, QA
- Downtime: Scheduled maintenance only

**Production Instance** (like Salesforce Production Org)

- Purpose: Serving real traffic
- Data: Real customer data
- Components: Stable, tested versions
- Pipelines: Approved, monitored
- Usage: Real API calls from customers
- Downtime: Zero tolerance

------

### Deployment Workflow

**Step 1: Local Development**

```bash
# Developer writes code
code lab/my-company/nodes/my_custom_node.py

# Run tests locally
fm test lab/my-company/nodes/my_custom_node.py

# Passes? Package it
fm lab-package lab/my-company/nodes/my_custom_node.py \
  --name my-custom-node \
  --version 1.0.0 \
  --output dist/
```

**Step 2: Deploy to Test**

```bash
# Deploy package to test instance
fm deploy dist/my-custom-node-1.0.0.fmpkg \
  --instance test.acme.flowmason.io \
  --env test
```

**Step 3: Test in Studio**

```
1. Login to test.acme.flowmason.io
2. See "my-custom-node" in palette
3. Create test pipeline using it
4. Run with sample inputs
5. Validate behavior
6. Check traces and costs
```

**Step 4: Deploy to Staging**

```bash
# If tests pass, promote to staging
fm deploy dist/my-custom-node-1.0.0.fmpkg \
  --instance staging.acme.flowmason.io \
  --env staging

# Update pipelines in staging to use new component
# Run integration tests
# Performance validation
```

**Step 5: Deploy to Production**

```bash
# If staging validates, promote to prod
fm deploy dist/my-custom-node-1.0.0.fmpkg \
  --instance acme.flowmason.io \
  --env production

# Component now available in production
# Can be used in any pipeline
# Exposed via APIs
```

------

## What Must Be Removed From Current Codebase

### Hard Removals (Technical Debt)

**1. Hardcoded Builtin Node Types**

- Location: `studio/flowmason_studio/stages/lab_executor.py`
- What to remove: `NODE_TYPE_MAPPING` dictionary
- What to remove: Special case handling for "generator", "critic", etc.
- Why: These must become normal packages

**2. Special Case Executor Logic**

- Location: `studio/flowmason_studio/stages/lab_executor.py`
- What to remove: `_execute_builtin()` method
- What to remove: Any if/else checking node type
- Why: Executor must be universal

**3. Code Editing Features in Studio**

- Location: `studio/frontend/` (if any exist)
- What to remove: Any code editor components
- What to remove: "Edit node code" buttons
- Why: No code editing in Studio, ever

**4. Components Stored in Database**

- Location: `studio/flowmason_studio/` database schemas
- What to remove: Any tables storing component Python code
- Why: Components come from packages only

**5. Inline Python Execution**

- Location: Any API routes that execute arbitrary Python
- What to remove: Routes that take Python code as input
- Why: Security and architecture violation

------

# Part 2: Implementation Plan

## Overview

This implementation plan transforms FlowMason Studio from a platform with hardcoded components to pure infrastructure that executes deployed packages.

**Total Estimated Timeline:** 4-6 weeks **Phases:** 5 major phases, each with clear deliverables

------

## Phase 1: Universal Component Registry (Week 1)

### Goal

Build a registry that can discover, load, and expose ANY packaged component dynamically, with zero hardcoded types.

### Tasks

#### Task 1.1: Create Universal Registry Interface

**File:** `core/flowmason_core/packages/registry.py`

**Requirements:**

- Registry class that loads from .fmpkg files
- Methods:
  - `get_component_class(component_type: str) -> Type[Node | Operator]`
  - `get_component_metadata(component_type: str) -> ComponentMetadata`
  - `list_available_components(category: Optional[str]) -> List[ComponentInfo]`
  - `register_package(package_path: str) -> PackageInfo`
  - `unregister_package(package_name: str, version: str) -> bool`

**Data Structures:**

```python
@dataclass
class ComponentMetadata:
    name: str
    version: str
    component_type: str  # "node" or "operator"
    category: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    recommended_providers: List[str]
    required_capabilities: List[str]
    package_name: str
    package_version: str

@dataclass
class ComponentInfo:
    component_type: str
    metadata: ComponentMetadata
    is_available: bool
    load_error: Optional[str]
```

**Key Behaviors:**

- Scan packages directory on initialization
- Lazy-load component classes (don't import until needed)
- Cache loaded classes for performance
- Handle version conflicts (latest wins or explicit selection)
- Clear error messages when component not found

------

#### Task 1.2: Dynamic Class Loader

**File:** `core/flowmason_core/packages/loader.py`

**Requirements:**

- Load Python classes from .fmpkg archives
- Extract to temp directory
- Add to Python path
- Import module
- Get class by name
- Handle cleanup

**Methods:**

```python
class PackageLoader:
    def extract_package(self, fmpkg_path: str) -> str:
        """Extract .fmpkg to temp directory, return path"""
    
    def load_component_class(self, 
                            package_path: str, 
                            module_name: str, 
                            class_name: str) -> Type:
        """Dynamically import and return class"""
    
    def unload_package(self, package_path: str):
        """Clean up temp files"""
```

**Security Considerations:**

- Validate package signatures (future)
- Sandboxed execution (future)
- Resource limits (future)
- For now: trust deployed packages

------

#### Task 1.3: Metadata Extraction

**File:** `core/flowmason_core/packages/metadata_extractor.py`

**Requirements:**

- Read decorator metadata from classes
- Extract via introspection (not execution)
- Get Input/Output schemas from Pydantic models
- Parse docstrings for descriptions

**Methods:**

```python
class MetadataExtractor:
    def extract_from_class(self, cls: Type) -> ComponentMetadata:
        """Extract all metadata from decorated class"""
    
    def extract_input_schema(self, cls: Type) -> Dict[str, Any]:
        """Get JSON schema from Input class"""
    
    def extract_output_schema(self, cls: Type) -> Dict[str, Any]:
        """Get JSON schema from Output class"""
    
    def extract_decorator_metadata(self, cls: Type) -> Dict[str, Any]:
        """Get metadata from @node or @operator decorator"""
```

------

#### Task 1.4: Registry Database Schema

**File:** `studio/supabase/migrations/007_component_registry.sql`

**Tables:**

```sql
CREATE TABLE component_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    
    -- Component identification
    component_type TEXT NOT NULL,  -- unique name like "support_triage"
    component_kind TEXT NOT NULL,  -- "node" or "operator"
    category TEXT NOT NULL,
    
    -- Package info
    package_name TEXT NOT NULL,
    package_version TEXT NOT NULL,
    package_path TEXT NOT NULL,  -- path to .fmpkg file
    
    -- Metadata (JSON)
    metadata JSONB NOT NULL,
    input_schema JSONB NOT NULL,
    output_schema JSONB NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_core BOOLEAN DEFAULT false,  -- managed by FlowMason team
    
    -- Audit
    deployed_at TIMESTAMPTZ DEFAULT NOW(),
    deployed_by UUID REFERENCES profiles(id),
    
    -- Constraints
    UNIQUE(organization_id, component_type, package_version)
);

CREATE INDEX idx_component_registry_org_type 
    ON component_registry(organization_id, component_type);
CREATE INDEX idx_component_registry_active 
    ON component_registry(organization_id, is_active);
```

------

#### Task 1.5: Registry API Endpoints

**File:** `studio/flowmason_studio/api/routes/registry.py`

**Endpoints:**

```python
GET  /api/registry/components
     # List all available components
     # Query params: category, kind (node/operator), include_inactive
     
GET  /api/registry/components/{component_type}
     # Get details for specific component
     # Includes: metadata, schemas, versions
     
POST /api/registry/deploy
     # Upload and register new package
     # Body: multipart/form-data with .fmpkg file
     # Extracts, validates, registers
     
DELETE /api/registry/components/{component_type}/{version}
     # Unregister component version
     # Checks: not in use by active pipelines
     
POST /api/registry/refresh
     # Rescan packages directory
     # Re-register all packages
```

------

#### Task 1.6: Update Core Decorators

**File:** `core/flowmason_core/core/decorators.py`

**Requirements:**

- Enhance `@node` and `@operator` decorators
- Store metadata in class attributes
- Make metadata easily extractable

**Example:**

```python
def node(
    name: str,
    category: str,
    description: str = "",
    recommended_providers: List[str] = None,
    required_capabilities: List[str] = None,
    version: str = "1.0.0"
):
    def decorator(cls):
        # Store metadata as class attributes
        cls.__flowmason_type__ = "node"
        cls.__flowmason_name__ = name
        cls.__flowmason_category__ = category
        cls.__flowmason_description__ = description
        cls.__flowmason_recommended_providers__ = recommended_providers or []
        cls.__flowmason_required_capabilities__ = required_capabilities or []
        cls.__flowmason_version__ = version
        
        # Validate class structure
        if not hasattr(cls, 'Input'):
            raise ValueError(f"Node {name} missing Input class")
        if not hasattr(cls, 'Output'):
            raise ValueError(f"Node {name} missing Output class")
        if not hasattr(cls, 'execute'):
            raise ValueError(f"Node {name} missing execute method")
            
        return cls
    return decorator
```

------

### Phase 1 Deliverables

**Code:**

- ✅ Universal registry loads components from packages
- ✅ Dynamic class loader imports components on-demand
- ✅ Metadata extractor reads schemas and decorator info
- ✅ Database schema for registry
- ✅ API endpoints for component management
- ✅ Enhanced decorators store metadata

**Tests:**

- ✅ Registry can load sample .fmpkg
- ✅ Registry lists all components correctly
- ✅ Metadata extraction works for node and operator
- ✅ API endpoints return correct data
- ✅ Duplicate component handling (version conflicts)

**Documentation:**

- ✅ Registry API reference
- ✅ Package format specification
- ✅ Decorator usage guide

**Success Criteria:**

```python
# This should work:
registry = ComponentRegistry()
registry.scan_packages("/path/to/packages")

# List components
components = registry.list_available_components()
assert len(components) > 0

# Load a component
NodeClass = registry.get_component_class("support_triage")
metadata = registry.get_component_metadata("support_triage")

assert NodeClass is not None
assert metadata.component_type == "support_triage"
assert "anthropic" in metadata.recommended_providers
```

------

## Phase 2: Config-to-Schema Mapper (Week 2)

### Goal

Build a system that converts pipeline configuration (JSON) into typed component Input models (Pydantic), enabling any component to be configured via JSON.

### Tasks

#### Task 2.1: Input Mapping System

**File:** `studio/flowmason_studio/config/input_mapper.py`

**Requirements:**

- Take `NodeConfig` JSON
- Take component's `Input` Pydantic model
- Map fields from config to Input instance
- Resolve template variables (e.g., `{{upstream.field}}`)
- Validate all required fields present
- Type coercion where safe

**Core Class:**

```python
class InputMapper:
    def __init__(self, context: ExecutionContext):
        self.context = context
    
    def map_config_to_input(
        self,
        node_config: NodeConfig,
        input_class: Type[NodeInput],
        upstream_outputs: Dict[str, Any] = None
    ) -> NodeInput:
        """
        Convert NodeConfig to typed Input instance
        
        Args:
            node_config: Pipeline node configuration
            input_class: The Input class from the component
            upstream_outputs: Results from previous pipeline stages
        
        Returns:
            Instance of input_class with fields populated
        
        Raises:
            MappingError: If required fields missing or type mismatch
        """
        pass
```

**Template Resolution:**

```python
class TemplateResolver:
    def resolve(self, template: str, context: Dict[str, Any]) -> Any:
        """
        Resolve template variables like:
        - {{input.field}} -> from pipeline input
        - {{upstream.stage_id.field}} -> from previous stage output
        - {{env.VAR_NAME}} -> from environment
        - {{context.run_id}} -> from execution context
        """
        pass
```

------

#### Task 2.2: Field Mapping Configuration

**File:** `studio/flowmason_studio/config/field_mapper.py`

**Requirements:**

- Support explicit field mappings
- Support implicit mappings (same name)
- Handle nested fields
- Handle arrays and objects
- Support default values

**Mapping Syntax in Pipeline Config:**

```json
{
  "stages": [{
    "id": "triage",
    "type": "support_triage",
    "input_mapping": {
      // Explicit mapping
      "text": "{{input.ticket_text}}",
      "category": "{{input.category}}",
      
      // Nested field
      "metadata.customer_id": "{{input.customer.id}}",
      
      // From upstream stage
      "context": "{{upstream.enrich.result}}",
      
      // Static value
      "priority_threshold": 0.8,
      
      // Environment variable
      "api_key": "{{env.INTERNAL_API_KEY}}"
    }
  }]
}
```

------

#### Task 2.3: Schema Validation

**File:** `studio/flowmason_studio/config/schema_validator.py`

**Requirements:**

- Validate config matches component Input schema
- Check required fields present
- Check types are compatible
- Provide clear error messages
- Happen BEFORE execution (fail fast)

**Methods:**

```python
class SchemaValidator:
    def validate_mapping(
        self,
        input_mapping: Dict[str, Any],
        input_schema: Dict[str, Any],
        available_context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate that input_mapping can produce valid input
        
        Returns ValidationResult with:
        - is_valid: bool
        - errors: List[ValidationError]
        - warnings: List[str]
        """
        pass
```

**Validation Errors:**

```python
@dataclass
class ValidationError:
    field: str
    error_type: str  # "missing_required", "type_mismatch", "invalid_template"
    message: str
    suggestion: Optional[str]
```

------

#### Task 2.4: Type Coercion System

**File:** `studio/flowmason_studio/config/type_coercion.py`

**Requirements:**

- Safe type conversions
- String → int, float, bool
- JSON string → dict/list
- Handle None vs missing field
- Clear errors on unsafe coercion

**Examples:**

```python
# Safe coercions:
"123" -> 123 (if field expects int)
"true" -> True (if field expects bool)
'{"key": "value"}' -> dict (if field expects dict)

# Unsafe (error):
"abc" -> int (not valid)
"random" -> bool (ambiguous)
```

------

#### Task 2.5: Update Pipeline Config Schema

**File:** `studio/flowmason_studio/models/pipeline_config.py`

**Add `input_mapping` to NodeConfig:**

```python
class NodeConfig(BaseModel):
    id: str
    type: str  # component_type from registry
    component_package: str  # e.g., "acme/support-triage@1.0.0"
    
    # NEW: How to map to component's Input
    input_mapping: Dict[str, Any]
    
    # Optional overrides
    provider: Optional[str] = None
    timeout_ms: Optional[int] = None
    retry_config: Optional[RetryConfig] = None
```

------

#### Task 2.6: Integration with Executor

**File:** `studio/flowmason_studio/stages/lab_executor.py`

**Update executor to use mapper:**

```python
class LabNodeExecutor:
    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
        self.mapper = InputMapper(context)
    
    async def _execute_node(
        self, 
        node_config: NodeConfig,
        upstream_outputs: Dict[str, Any]
    ):
        # Get component from registry
        NodeClass = self.registry.get_component_class(node_config.type)
        
        # Map config to Input
        node_input = self.mapper.map_config_to_input(
            node_config,
            NodeClass.Input,
            upstream_outputs
        )
        
        # Execute
        node_instance = NodeClass()
        result = await node_instance.execute(node_input, self.context)
        
        return result
```

------

### Phase 2 Deliverables

**Code:**

- ✅ Input mapper converts config to Pydantic models
- ✅ Template resolver handles {{variable}} syntax
- ✅ Field mapper supports nested fields and arrays
- ✅ Schema validator checks config before execution
- ✅ Type coercion for common conversions
- ✅ Executor integration

**Tests:**

- ✅ Map simple flat fields
- ✅ Map nested fields
- ✅ Resolve templates from upstream
- ✅ Validation catches missing required fields
- ✅ Validation catches type mismatches
- ✅ Type coercion works for common cases
- ✅ End-to-end: config → Input → execute

**Documentation:**

- ✅ Input mapping syntax reference
- ✅ Template variable guide
- ✅ Validation error codes

**Success Criteria:**

```python
# This should work:
node_config = NodeConfig(
    type="support_triage",
    input_mapping={
        "text": "{{input.ticket_text}}",
        "metadata": "{{input.metadata}}"
    }
)

mapper = InputMapper(context)
node_input = mapper.map_config_to_input(
    node_config,
    SupportTriageNode.Input,
    upstream_outputs={}
)

assert isinstance(node_input, SupportTriageNode.Input)
assert node_input.text == "Customer can't login..."
```

------

## Phase 3: Universal Executor (Week 3)

### Goal

Replace hardcoded node execution with universal system that works for ANY component type.

### Tasks

#### Task 3.1: Remove Builtin Node Special Cases

**File:** `studio/flowmason_studio/stages/lab_executor.py`

**Actions:**

1. Delete `NODE_TYPE_MAPPING` dictionary
2. Delete `_execute_builtin()` method
3. Delete any if/else checking for specific node types
4. Delete hardcoded imports of builtin nodes

**Before (WRONG):**

```python
NODE_TYPE_MAPPING = {
    "generator": GeneratorNode,
    "critic": CriticNode,
    # ... hardcoded types
}

async def _execute_node(self, node_config):
    if node_config.type in NODE_TYPE_MAPPING:
        return await self._execute_builtin(node_config)
    else:
        raise ValueError(f"Unknown type: {node_config.type}")
```

**After (CORRECT):**

```python
async def _execute_node(self, node_config):
    # Get component from registry (works for ANY type)
    NodeClass = self.registry.get_component_class(node_config.type)
    
    # Map config to input
    node_input = self.mapper.map_config_to_input(...)
    
    # Execute
    return await NodeClass().execute(node_input, self.context)
```

------

#### Task 3.2: Universal Execution Method

**File:** `studio/flowmason_studio/stages/universal_executor.py`

**Create new unified executor:**

```python
class UniversalExecutor:
    """
    Executes ANY component type (node or operator) uniformly.
    No special cases. No hardcoded types.
    """
    
    def __init__(
        self,
        registry: ComponentRegistry,
        context: ExecutionContext
    ):
        self.registry = registry
        self.context = context
        self.mapper = InputMapper(context)
        self.tracer = ExecutionTracer()
    
    async def execute_component(
        self,
        component_config: ComponentConfig,
        upstream_outputs: Dict[str, Any]
    ) -> ComponentResult:
        """
        Execute any component type uniformly.
        
        Steps:
        1. Load component class from registry
        2. Map config to Input model
        3. Validate provider requirements
        4. Execute with tracing
        5. Validate output
        6. Return result
        """
        
        # Start trace span
        with self.tracer.span(component_config.id) as span:
            # Load component
            ComponentClass = self.registry.get_component_class(
                component_config.type
            )
            span.set_attribute("component.class", ComponentClass.__name__)
            
            # Get metadata
            metadata = self.registry.get_component_metadata(
                component_config.type
            )
            
            # Validate provider if needed
            if metadata.recommended_providers:
                self._validate_provider(component_config, metadata)
            
            # Map input
            component_input = self.mapper.map_config_to_input(
                component_config,
                ComponentClass.Input,
                upstream_outputs
            )
            span.set_attribute("input.size", len(str(component_input)))
            
            # Execute
            try:
                component_instance = ComponentClass()
                result = await component_instance.execute(
                    component_input,
                    self.context
                )
                span.set_attribute("status", "success")
            except Exception as e:
                span.set_attribute("status", "error")
                span.set_attribute("error", str(e))
                raise
            
            # Validate output
            self._validate_output(result, metadata.output_schema)
            
            # Return wrapped result
            return ComponentResult(
                component_id=component_config.id,
                component_type=component_config.type,
                output=result.output,
                usage=result.usage,
                trace_id=span.trace_id
            )
```

------

#### Task 3.3: Provider Validation

**File:** `studio/flowmason_studio/stages/provider_validator.py`

**Requirements:**

- Check if selected provider supports component requirements
- Validate capabilities match
- Provide helpful errors

**Methods:**

```python
class ProviderValidator:
    def validate_provider_for_component(
        self,
        provider_name: str,
        component_metadata: ComponentMetadata
    ) -> ValidationResult:
        """
        Check if provider is suitable for component.
        
        Checks:
        - Provider exists
        - Provider has required capabilities
        - Provider recommended by component
        
        Returns warnings, not errors, if suboptimal
        """
        pass
```

------

#### Task 3.4: Output Validation

**File:** `studio/flowmason_studio/stages/output_validator.py`

**Requirements:**

- Validate component output matches declared Output schema
- Catch schema violations before they corrupt pipeline
- Provide clear errors

**Methods:**

```python
class OutputValidator:
    def validate_output(
        self,
        output: Any,
        expected_schema: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate output matches schema.
        
        If invalid, raise OutputValidationError with:
        - Which fields are wrong
        - What was expected vs received
        - Suggestions for fixing
        """
        pass
```

------

#### Task 3.5: DAG Executor Integration

**File:** `studio/flowmason_studio/dag/executor.py`

**Update DAG executor to use UniversalExecutor:**

```python
class DAGExecutor:
    def __init__(
        self,
        registry: ComponentRegistry,
        context: ExecutionContext
    ):
        self.registry = registry
        self.context = context
        self.executor = UniversalExecutor(registry, context)
    
    async def execute(
        self,
        dag_config: DAGConfig,
        run_input: Dict[str, Any]
    ) -> DAGResult:
        """
        Execute entire DAG using universal executor.
        
        For each stage:
        1. Wait for dependencies
        2. Gather upstream outputs
        3. Execute via universal executor
        4. Store result
        """
        
        results = {}
        
        for stage in self._topological_sort(dag_config.stages):
            # Get upstream results
            upstream = {
                dep_id: results[dep_id]
                for dep_id in stage.dependencies
            }
            
            # Execute via universal executor
            result = await self.executor.execute_component(
                stage,
                upstream
            )
            
            results[stage.id] = result
        
        return DAGResult(
            stage_results=results,
            final_output=results[dag_config.output_stage_id],
            usage=self._aggregate_usage(results)
        )
```

------

### Phase 3 Deliverables

**Code:**

- ✅ Removed all hardcoded node types
- ✅ UniversalExecutor works for any component
- ✅ Provider validation integrated
- ✅ Output validation integrated
- ✅ DAG executor uses universal executor

**Tests:**

- ✅ Execute builtin node (generator) via universal path
- ✅ Execute custom node (support_triage) via universal path
- ✅ Execute operator (json_transform) via universal path
- ✅ Provider validation catches unsupported providers
- ✅ Output validation catches schema violations
- ✅ Full DAG execution with mixed component types

**Documentation:**

- ✅ Universal executor architecture
- ✅ Component execution lifecycle
- ✅ Error handling guide

**Success Criteria:**

```python
# This should work for ANY component type:
executor = UniversalExecutor(registry, context)

# Builtin node
result1 = await executor.execute_component(
    ComponentConfig(type="generator", ...),
    upstream_outputs={}
)

# Custom node
result2 = await executor.execute_component(
    ComponentConfig(type="support_triage", ...),
    upstream_outputs={}
)

# Operator
result3 = await executor.execute_component(
    ComponentConfig(type="json_transform", ...),
    upstream_outputs={"data": {...}}
)

# All execute through same code path
assert result1.status == "success"
assert result2.status == "success"
assert result3.status == "success"
```

------

## Phase 4: Extract Builtin Components to Packages (Week 4)

### Goal

Remove all "builtin" components from Studio codebase and convert them to normal packages that get deployed like any other component.

### Tasks

#### Task 4.1: Extract Builtin Nodes

**New Location:** `lab/flowmason_lab/nodes/core/`

**Actions:**

1. Move generator, critic, improver, synthesizer, selector to Lab
2. Ensure they follow standard @node decorator pattern
3. Add comprehensive metadata
4. Write tests for each
5. Package each as separate .fmpkg

**Example Structure:**

```
lab/flowmason_lab/nodes/core/
├── generator.py
├── critic.py
├── improver.py
├── synthesizer.py
├── selector.py
└── __init__.py

tests/nodes/core/
├── test_generator.py
├── test_critic.py
├── test_improver.py
├── test_synthesizer.py
└── test_selector.py
```

**Each node must:**

- Use `@node` decorator with full metadata
- Have typed Input/Output classes
- Implement async execute()
- Have snapshot tests
- Have contract tests (multiple providers)
- Be packageable via `fm lab-package`

------

#### Task 4.2: Extract Builtin Operators

**New Location:** `lab/flowmason_lab/operators/core/`

**Actions:**

1. Move http_request, json_transform, filter, loop, etc. to Lab
2. Follow standard @operator pattern
3. Add metadata
4. Write tests
5. Package each

**Example Structure:**

```
lab/flowmason_lab/operators/core/
├── http_request.py
├── json_transform.py
├── filter.py
├── loop.py
├── schema_validate.py
├── variable_set.py
├── logger.py
└── __init__.py

tests/operators/core/
├── test_http_request.py
├── test_json_transform.py
├── test_filter.py
├── test_loop.py
├── test_schema_validate.py
├── test_variable_set.py
└── test_logger.py
```

------

#### Task 4.3: Package Core Components

**Script:** `scripts/package_core_components.sh`

**Creates packages for all core components:**

```bash
#!/bin/bash

# Package all core nodes
for node in generator critic improver synthesizer selector; do
    fm lab-package \
        lab/flowmason_lab/nodes/core/${node}.py \
        --name ${node} \
        --version 1.0.0 \
        --category core \
        --output dist/core/
done

# Package all core operators
for op in http_request json_transform filter loop schema_validate variable_set logger; do
    fm lab-package \
        lab/flowmason_lab/operators/core/${op}.py \
        --name ${op} \
        --version 1.0.0 \
        --category core \
        --output dist/core/
done
```

------

#### Task 4.4: Core Package Distribution System

**File:** `studio/flowmason_studio/setup/core_packages.py`

**Auto-install core packages on instance creation:**

```python
class CorePackageInstaller:
    """
    Installs core FlowMason packages to new instances.
    """
    
    CORE_PACKAGES = [
        # Core nodes
        ("generator", "1.0.0"),
        ("critic", "1.0.0"),
        ("improver", "1.0.0"),
        ("synthesizer", "1.0.0"),
        ("selector", "1.0.0"),
        
        # Core operators
        ("http_request", "1.0.0"),
        ("json_transform", "1.0.0"),
        ("filter", "1.0.0"),
        ("loop", "1.0.0"),
        ("schema_validate", "1.0.0"),
        ("variable_set", "1.0.0"),
        ("logger", "1.0.0"),
    ]
    
    async def install_core_packages(
        self,
        organization_id: str,
        packages_dir: str = "/opt/flowmason/core-packages"
    ):
        """
        Install all core packages to organization.
        Called during instance initialization.
        """
        
        for package_name, version in self.CORE_PACKAGES:
            package_path = f"{packages_dir}/{package_name}-{version}.fmpkg"
            
            try:
                await self.registry.register_package(
                    package_path,
                    organization_id=organization_id,
                    is_core=True
                )
                logger.info(f"Installed core package: {package_name}@{version}")
            except Exception as e:
                logger.error(f"Failed to install {package_name}: {e}")
                # Continue with other packages
```

------

#### Task 4.5: Remove Builtin Code from Studio

**Files to Clean:**

- `studio/flowmason_studio/stages/builtin_nodes.py` - DELETE
- `studio/flowmason_studio/stages/builtin_operators.py` - DELETE
- Any imports of builtin classes - REMOVE

**Verify:**

- Studio codebase has ZERO component implementations
- Studio only has: registry, executor, API, UI
- All components come from deployed packages

------

#### Task 4.6: Update Instance Initialization

**File:** `studio/flowmason_studio/setup/initialize_instance.py`

**Add core package installation to setup:**

```python
async def initialize_new_instance(
    organization_id: str,
    owner_email: str
):
    """
    Complete setup for new FlowMason instance.
    """
    
    # 1. Create organization in database
    org = await create_organization(organization_id, owner_email)
    
    # 2. Create owner profile
    owner = await create_owner_profile(owner_email, organization_id)
    
    # 3. Install core packages
    installer = CorePackageInstaller()
    await installer.install_core_packages(organization_id)
    
    # 4. Create default pipelines (optional)
    await create_default_pipelines(organization_id)
    
    # 5. Send welcome email
    await send_welcome_email(owner_email)
    
    logger.info(f"Instance initialized: {organization_id}")
```

------

### Phase 4 Deliverables

**Code:**

- ✅ All builtin nodes moved to Lab and packaged
- ✅ All builtin operators moved to Lab and packaged
- ✅ Core package installer
- ✅ Instance initialization installs core packages
- ✅ Studio codebase has zero component implementations

**Packages:**

- ✅ `generator-1.0.0.fmpkg`
- ✅ `critic-1.0.0.fmpkg`
- ✅ `improver-1.0.0.fmpkg`
- ✅ `synthesizer-1.0.0.fmpkg`
- ✅ `selector-1.0.0.fmpkg`
- ✅ `http_request-1.0.0.fmpkg`
- ✅ `json_transform-1.0.0.fmpkg`
- ✅ `filter-1.0.0.fmpkg`
- ✅ `loop-1.0.0.fmpkg`
- ✅ `schema_validate-1.0.0.fmpkg`
- ✅ `variable_set-1.0.0.fmpkg`
- ✅ `logger-1.0.0.fmpkg`

**Tests:**

- ✅ Each core component has snapshot tests
- ✅ Each core component has contract tests
- ✅ Packaging succeeds for all core components
- ✅ Fresh instance auto-installs core packages
- ✅ Can execute pipeline using only deployed packages

**Documentation:**

- ✅ Core packages reference
- ✅ Instance setup guide
- ✅ Core package versioning policy

**Success Criteria:**

```bash
# Fresh instance should:
1. Have ZERO components initially
2. Auto-install 12 core packages
3. Show all core components in palette
4. Execute pipelines using those components
5. Treat core packages identically to custom packages

# Studio codebase should:
1. Have ZERO imports of component classes
2. Have ZERO hardcoded component logic
3. Only reference registry for components
```

------

## Phase 5: Package Deployment & API Gateway (Weeks 5-6)

### Goal

Complete the deployment workflow and API exposure system, making pipelines truly API-first.

### Tasks

#### Task 5.1: Package Upload API

**File:** `studio/flowmason_studio/api/routes/packages.py`

**Endpoint:**

```python
@router.post("/packages/upload")
async def upload_package(
    file: UploadFile,
    organization_id: str = Depends(get_current_org),
    user: User = Depends(require_role(["node_developer", "admin", "owner"]))
):
    """
    Upload .fmpkg file and register components.
    
    Steps:
    1. Validate file is .fmpkg
    2. Extract to temp directory
    3. Read and validate manifest
    4. Check for version conflicts
    5. Copy to packages directory
    6. Register in database
    7. Return component info
    """
    
    # Validate upload
    if not file.filename.endswith('.fmpkg'):
        raise HTTPException(400, "Must be .fmpkg file")
    
    # Save to temp
    temp_path = await save_upload(file)
    
    try:
        # Extract and validate
        package_info = PackageValidator.validate_package(temp_path)
        
        # Check conflicts
        existing = await registry.get_package(
            package_info.name,
            package_info.version,
            organization_id
        )
        if existing:
            raise HTTPException(409, "Package version already exists")
        
        # Install
        final_path = await install_package(
            temp_path,
            organization_id
        )
        
        # Register
        components = await registry.register_package(
            final_path,
            organization_id,
            deployed_by=user.id
        )
        
        return {
            "package": package_info,
            "components": components,
            "status": "deployed"
        }
        
    finally:
        cleanup_temp(temp_path)
```

------

#### Task 5.2: CLI Deploy Command

**File:** `core/flowmason_core/cli/commands.py`

**Add `fm deploy` command:**

```python
@cli.command()
@click.argument('package_path')
@click.option('--instance', required=True, help='FlowMason instance URL')
@click.option('--env', type=click.Choice(['test', 'staging', 'production']))
@click.option('--api-key', help='API key (or set FLOWMASON_API_KEY)')
def deploy(package_path: str, instance: str, env: str, api_key: str):
    """
    Deploy package to FlowMason instance.
    
    Example:
        fm deploy dist/my-node-1.0.0.fmpkg \\
            --instance https://acme.flowmason.io \\
            --env production \\
            --api-key xxx
    """
    
    # Validate package exists
    if not os.path.exists(package_path):
        click.echo(f"Error: Package not found: {package_path}")
        return 1
    
    # Get API key
    api_key = api_key or os.getenv('FLOWMASON_API_KEY')
    if not api_key:
        click.echo("Error: API key required (--api-key or FLOWMASON_API_KEY)")
        return 1
    
    # Upload
    click.echo(f"Deploying {package_path} to {instance} ({env})...")
    
    try:
        response = deploy_package(
            package_path=package_path,
            instance_url=instance,
            api_key=api_key,
            environment=env
        )
        
        click.echo(f"✓ Deployed successfully")
        click.echo(f"  Package: {response['package']['name']}@{response['package']['version']}")
        click.echo(f"  Components: {len(response['components'])}")
        for comp in response['components']:
            click.echo(f"    - {comp['type']} ({comp['kind']})")
        
        return 0
        
    except Exception as e:
        click.echo(f"✗ Deployment failed: {e}")
        return 1
```

------

#### Task 5.3: Pipeline API Endpoints

**File:** `studio/flowmason_studio/api/routes/pipeline_execution.py`

**Execute pipeline via API:**

```python
@router.post("/pipelines/{pipeline_id}/run")
async def execute_pipeline(
    pipeline_id: str,
    run_input: Dict[str, Any],
    version: Optional[str] = None,
    api_key: str = Depends(validate_api_key)
):
    """
    Execute pipeline and return result.
    
    This is the PRIMARY API endpoint that consumers call.
    
    Args:
        pipeline_id: Pipeline identifier
        run_input: JSON payload matching pipeline input schema
        version: Optional specific version (default: latest)
        api_key: API key for authentication
    
    Returns:
        {
            "run_id": "run_xxx",
            "pipeline_id": "support-triage",
            "pipeline_version": "1.0.0",
            "status": "completed" | "failed",
            "result": {...},  # Pipeline output
            "usage": {
                "total_tokens": 1250,
                "cost_usd": 0.023,
                "duration_ms": 850
            },
            "trace_url": "/api/runs/run_xxx/trace"
        }
    """
    
    # Load pipeline
    pipeline = await get_pipeline(pipeline_id, version)
    if not pipeline:
        raise HTTPException(404, "Pipeline not found")
    
    # Validate input against schema
    validate_against_schema(run_input, pipeline.input_schema)
    
    # Create run record
    run = await create_run(
        pipeline_id=pipeline.id,
        pipeline_version=pipeline.version,
        input=run_input
    )
    
    try:
        # Execute via universal executor
        result = await dag_executor.execute(
            pipeline.dag_config,
            run_input
        )
        
        # Update run record
        await update_run(
            run.id,
            status="completed",
            result=result.final_output,
            usage=result.usage
        )
        
        return {
            "run_id": run.id,
            "pipeline_id": pipeline.id,
            "pipeline_version": pipeline.version,
            "status": "completed",
            "result": result.final_output,
            "usage": result.usage,
            "trace_url": f"/api/runs/{run.id}/trace"
        }
        
    except Exception as e:
        # Record failure
        await update_run(
            run.id,
            status="failed",
            error=str(e)
        )
        
        raise HTTPException(500, f"Execution failed: {e}")
```

------

#### Task 5.4: OpenAPI Spec Generation

**File:** `studio/flowmason_studio/api/openapi_generator.py`

**Generate OpenAPI spec for each pipeline:**

```python
class OpenAPIGenerator:
    def generate_for_pipeline(self, pipeline: Pipeline) -> Dict[str, Any]:
        """
        Generate OpenAPI 3.0 spec for pipeline API.
        
        Includes:
        - Endpoint definition
        - Request body schema (from pipeline.input_schema)
        - Response schema (from pipeline.output_schema)
        - Authentication requirements
        - Example requests/responses
        """
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": pipeline.name,
                "version": pipeline.version,
                "description": pipeline.description
            },
            "servers": [{
                "url": f"https://{pipeline.organization_id}.flowmason.io"
            }],
            "paths": {
                f"/api/pipelines/{pipeline.id}/run": {
                    "post": {
                        "summary": f"Execute {pipeline.name}",
                        "security": [{"ApiKeyAuth": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": pipeline.input_schema
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "run_id": {"type": "string"},
                                                "status": {"type": "string"},
                                                "result": pipeline.output_schema,
                                                "usage": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                }
            }
        }
```

**Expose spec via API:**

```python
@router.get("/pipelines/{pipeline_id}/openapi.json")
async def get_pipeline_openapi(pipeline_id: str):
    """Return OpenAPI spec for pipeline"""
    pipeline = await get_pipeline(pipeline_id)
    generator = OpenAPIGenerator()
    return generator.generate_for_pipeline(pipeline)
```

------

#### Task 5.5: API Key Management

**File:** `studio/flowmason_studio/api/auth/api_keys.py`

**Create API key system for pipeline access:**

```python
class APIKeyManager:
    async def create_api_key(
        self,
        organization_id: str,
        name: str,
        permissions: List[str] = ["pipelines:execute"],
        expires_at: Optional[datetime] = None
    ) -> APIKey:
        """
        Create new API key for programmatic access.
        
        Permissions:
        - pipelines:execute - Can execute pipelines
        - pipelines:read - Can read pipeline configs
        - pipelines:write - Can create/update pipelines
        - packages:deploy - Can deploy packages
        """
        
        key = generate_secure_key()
        hashed = hash_api_key(key)
        
        api_key = await db.api_keys.create({
            "organization_id": organization_id,
            "name": name,
            "key_hash": hashed,
            "permissions": permissions,
            "expires_at": expires_at
        })
        
        # Return raw key only once
        return APIKey(
            id=api_key.id,
            name=name,
            key=key,  # Only returned on creation
            permissions=permissions,
            created_at=api_key.created_at
        )
    
    async def validate_api_key(
        self,
        key: str,
        required_permission: str
    ) -> Optional[APIKey]:
        """Validate key and check permission"""
        
        hashed = hash_api_key(key)
        api_key = await db.api_keys.find_by_hash(hashed)
        
        if not api_key:
            return None
        
        if api_key.expires_at and api_key.expires_at < datetime.now():
            return None
        
        if required_permission not in api_key.permissions:
            return None
        
        return api_key
```

------

#### Task 5.6: Rate Limiting & Quotas

**File:** `studio/flowmason_studio/api/middleware/rate_limiter.py`

**Add rate limiting for API endpoints:**

```python
class RateLimiter:
    """
    Rate limit pipeline execution by:
    - Organization
    - API key
    - Pipeline
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_rate_limit(
        self,
        organization_id: str,
        pipeline_id: str,
        limit_type: str = "per_minute"
    ) -> RateLimitResult:
        """
        Check if request is within rate limits.
        
        Limits:
        - 60 requests/minute per organization
        - 1000 requests/hour per organization
        - Per-pipeline custom limits
        """
        
        key = f"ratelimit:{organization_id}:{pipeline_id}:{limit_type}"
        count = await self.redis.incr(key)
        
        if count == 1:
            # Set expiry on first request
            if limit_type == "per_minute":
                await self.redis.expire(key, 60)
            elif limit_type == "per_hour":
                await self.redis.expire(key, 3600)
        
        limit = await self.get_limit(organization_id, pipeline_id, limit_type)
        
        if count > limit:
            return RateLimitResult(
                allowed=False,
                limit=limit,
                remaining=0,
                reset_at=await self.redis.ttl(key)
            )
        
        return RateLimitResult(
            allowed=True,
            limit=limit,
            remaining=limit - count,
            reset_at=await self.redis.ttl(key)
        )
```

------

### Phase 5 Deliverables

**Code:**

- ✅ Package upload API
- ✅ CLI deploy command
- ✅ Pipeline execution API
- ✅ OpenAPI spec generation
- ✅ API key management
- ✅ Rate limiting

**Tests:**

- ✅ Upload package via API
- ✅ Deploy package via CLI
- ✅ Execute pipeline via API
- ✅ OpenAPI spec validates correctly
- ✅ API keys work for authentication
- ✅ Rate limiting blocks excessive requests

**Documentation:**

- ✅ Package deployment guide
- ✅ Pipeline API reference
- ✅ API key management guide
- ✅ Rate limiting documentation

**Success Criteria:**

```bash
# Complete deployment workflow:

# 1. Develop locally
cd lab
code my-node.py
fm test my-node.py

# 2. Package
fm lab-package my-node.py --output dist/

# 3. Deploy to test
fm deploy dist/my-node-1.0.0.fmpkg \
    --instance https://test.acme.flowmason.io \
    --env test

# 4. Compose pipeline in Studio
# (UI-based, drag-and-drop)

# 5. Test pipeline
curl -X POST https://test.acme.flowmason.io/api/pipelines/my-pipeline/run \
  -H "X-API-Key: test_key" \
  -d '{"input": "..."}'

# 6. Deploy to production
fm deploy dist/my-node-1.0.0.fmpkg \
    --instance https://acme.flowmason.io \
    --env production

# 7. Consumer uses API
curl -X POST https://acme.flowmason.io/api/pipelines/my-pipeline/run \
  -H "X-API-Key: prod_key" \
  -d '{"input": "..."}'
```

------

# Part 3: Implementation Checklist

## Week-by-Week Breakdown

### Week 1: Component Registry

- [ ] Create ComponentRegistry class with dynamic loading
- [ ] Build PackageLoader for .fmpkg extraction
- [ ] Implement MetadataExtractor for schema introspection
- [ ] Add database schema for component registry
- [ ] Create registry API endpoints
- [ ] Update @node and @operator decorators
- [ ] Write comprehensive tests
- [ ] Document registry API

### Week 2: Config Mapper

- [ ] Build InputMapper class
- [ ] Implement TemplateResolver for {{variables}}
- [ ] Create FieldMapper for nested fields
- [ ] Build SchemaValidator
- [ ] Add TypeCoercion system
- [ ] Update NodeConfig schema
- [ ] Integrate with executor
- [ ] Write mapping tests
- [ ] Document input mapping syntax

### Week 3: Universal Executor

- [ ] Remove hardcoded NODE_TYPE_MAPPING
- [ ] Delete builtin node special cases
- [ ] Create UniversalExecutor class
- [ ] Build ProviderValidator
- [ ] Build OutputValidator
- [ ] Update DAGExecutor integration
- [ ] Write execution tests
- [ ] Document executor architecture

### Week 4: Extract Builtins

- [ ] Move builtin nodes to Lab
- [ ] Move builtin operators to Lab
- [ ] Write tests for each component
- [ ] Package all core components
- [ ] Build CorePackageInstaller
- [ ] Update instance initialization
- [ ] Remove builtin code from Studio
- [ ] Verify Studio has zero component implementations
- [ ] Document core packages

### Week 5: Deployment System

- [ ] Create package upload API
- [ ] Build `fm deploy` CLI command
- [ ] Add deployment validation
- [ ] Implement version management
- [ ] Create deployment tests
- [ ] Document deployment workflow

### Week 6: API Gateway

- [ ] Build pipeline execution API
- [ ] Create OpenAPIGenerator
- [ ] Implement API key management
- [ ] Add rate limiting
- [ ] Build quota system
- [ ] Write API integration tests
- [ ] Document API usage
- [ ] Create example integrations

------

## Testing Strategy

### Unit Tests

Each component must have unit tests covering:

- Happy path
- Error conditions
- Edge cases
- Invalid inputs

### Integration Tests

Test complete workflows:

- Package → Deploy → Execute
- Config → Mapper → Execute
- API → Pipeline → Result

### End-to-End Tests

Validate complete user journeys:

- Developer: Code → Package → Deploy → Test
- Platform: Compose → Execute → Monitor
- Consumer: API call → Result

### Performance Tests

Benchmark critical paths:

- Component loading time
- Config mapping overhead
- Execution latency
- API response time

------

## Rollout Strategy

### Phase 0: Preparation (Before Week 1)

- [ ] Create feature branch: `feature/universal-architecture`
- [ ] Set up test instances
- [ ] Back up current production data
- [ ] Communicate timeline to stakeholders

### Phase 1-3: Core Architecture (Weeks 1-3)

- [ ] Work in feature branch
- [ ] Daily deployments to test instance
- [ ] No production changes yet
- [ ] Validate each phase before proceeding

### Phase 4: Extract Builtins (Week 4)

- [ ] This is the breaking change
- [ ] Coordinate with any existing users
- [ ] Provide migration guide
- [ ] Run in parallel: old and new systems

### Phase 5-6: Deployment & API (Weeks 5-6)

- [ ] Deploy to staging instance
- [ ] Run integration tests
- [ ] Fix any issues
- [ ] Deploy to production
- [ ] Monitor closely

### Post-Launch:

- [ ] Monitor error rates
- [ ] Track performance metrics
- [ ] Gather user feedback
- [ ] Iterate on pain points

------

## Success Metrics

### Technical Metrics

- [ ] Zero hardcoded component types in Studio
- [ ] All components load from packages
- [ ] Execution time < 2x baseline
- [ ] API response time < 500ms (p95)
- [ ] Test coverage > 80%

### User Metrics

- [ ] Developers can deploy packages
- [ ] Pipelines execute successfully
- [ ] API consumers can integrate
- [ ] Error rates < 1%
- [ ] Positive user feedback

------

## Documentation Deliverables

### For Developers

- [ ] Component development guide
- [ ] Testing framework documentation
- [ ] Packaging tutorial
- [ ] Deployment guide

### For Platform Users

- [ ] Pipeline composition guide
- [ ] Configuration reference
- [ ] Best practices

### For API Consumers

- [ ] API reference
- [ ] OpenAPI specs
- [ ] Integration examples
- [ ] Rate limits & quotas

### For Operations

- [ ] Architecture overview
- [ ] Deployment procedures
- [ ] Monitoring guide
- [ ] Troubleshooting playbook

------

# Appendix: Key Architectural Decisions

## Decision 1: No Hardcoded Components

**Rationale:**

- Enables true extensibility
- Treats all components equally
- Simplifies executor logic
- Enables marketplace/ecosystem

**Tradeoff:**

- More complex initialization
- Dynamic loading overhead
- Slightly harder to debug

**Verdict:** Worth it for architectural purity and future flexibility

------

## Decision 2: Config-to-Schema Mapping

**Rationale:**

- Preserves type safety
- Enables validation before execution
- Clear contract between config and components
- Supports complex nested fields

**Tradeoff:**

- Mapping layer adds complexity
- Template resolution can fail
- Debugging is harder

**Verdict:** Essential for maintaining type safety while allowing JSON configuration

------

## Decision 3: Universal Executor

**Rationale:**

- Single code path for all components
- No special cases to maintain
- Easier to add new component types
- Cleaner architecture

**Tradeoff:**

- Can't optimize for specific types
- Generic path may be slower
- Less obvious what's happening

**Verdict:** Architectural consistency worth minor performance cost

------

## Decision 4: Core Packages Auto-Install

**Rationale:**

- Fresh instances work immediately
- Consistent experience
- Users don't have to find/install basics

**Tradeoff:**

- Opinionated (what's "core"?)
- Larger initial install
- Harder to opt out

**Verdict:** Better UX, users can remove if desired

------

## Decision 5: API-First Pipeline Design

**Rationale:**

- Clear contract with consumers
- OpenAPI spec as documentation
- Enables ecosystem integration
- Professional developer experience

**Tradeoff:**

- More upfront design work
- Versioning complexity
- Breaking changes are painful

**Verdict:** Essential for pipelines as products

------

# Summary

This document provides the complete vision and implementation plan for transforming FlowMason into a true API infrastructure platform for AI workflows.

**Key Takeaways:**

1. **FlowMason is infrastructure, not a development tool**
   - Code is written in VS Code
   - Studio is for deployment, composition, and execution
   - No code editing in the platform
2. **All components are equal**
   - No hardcoded builtins
   - Everything comes from packages
   - Core packages are just packages you maintain
3. **Pipelines are APIs**
   - Each pipeline is a versioned endpoint
   - OpenAPI specs generated automatically
   - Consumed by external applications
4. **4-6 weeks of focused work**
   - Week 1: Registry
   - Week 2: Mapper
   - Week 3: Executor
   - Week 4: Extract builtins
   - Weeks 5-6: Deployment & API
5. **This is achievable**
   - Foundation is solid
   - Scope is bounded
   - Incremental validation at each step

**Next Step:** Have Claude Code start with Phase 1 (Universal Component Registry) and validate the architecture before proceeding.