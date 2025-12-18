# FlowMason Website Development

You are helping build the FlowMason website at flowmason.com. This is a professional, compelling website for an AI pipeline orchestration platform.

## Product Overview

**FlowMason** is a Universal AI Workflow Infrastructure platform that enables developers to design, build, debug, and deploy intelligent pipelines. It uses a **Salesforce DX-style hybrid model**:

- **Development**: File-based pipelines (`.pipeline.json`) in VSCode with Git version control
- **Deployment**: Push to staging/production orgs where pipelines run from databases
- **Runtime**: Backend APIs expose pipelines for consumption

## Current State (v0.4.1)

### Published Distribution
- **PyPI**: `pip install flowmason` (v0.4.1)
- **VSCode Extension**: Ready for Marketplace (flowmason-0.4.0.vsix)
- **Docker**: Pending

### CLI Commands (12 total)
```bash
fm run              # Execute pipeline from file
fm validate         # Validate pipeline files
fm init             # Initialize new project
fm deploy           # Deploy to org
fm pull             # Pull from org
fm pack             # Build .fmpkg package
fm install          # Install package
fm uninstall        # Remove package
fm list             # List packages
fm studio           # Manage Studio backend
fm org              # Manage org connections
fm auth             # Manage authentication
```

### Component Types (3 decorators)
1. **@node** - AI-powered components (LLM calls)
2. **@operator** - Deterministic data transformations
3. **@control_flow** - Pipeline execution control (conditionals, loops, error handling)

### Built-in Components (18 total)
- **Control Flow (6)**: Conditional, ForEach, TryCatch, Router, SubPipeline, Return
- **Operators (7)**: HttpRequest, JsonTransform, Filter, Loop, SchemaValidate, VariableSet, Logger
- **AI Nodes (5)**: Generator, Critic, Improver, Selector, Synthesizer

### VSCode Extension Features
- IntelliSense for decorators
- Visual DAG editor for pipelines
- Debugging with breakpoints (F9, F10, F5)
- Test Explorer integration
- Prompt iteration during debug

## Website Sections Required

### 1. Hero Section
- Compelling headline and tagline
- Quick install command: `pip install flowmason`
- Primary CTA buttons

### 2. Features Section
- Visual Pipeline Builder
- Three Component Types
- Full Debugging (breakpoints, step-through)
- Package System (.fmpkg)
- Multi-Environment (local, staging, production)
- Enterprise Ready (API keys, RBAC, SSO/SAML)

### 3. Documentation (/docs)
Reference existing docs in `fmdocs/`:
- Getting Started
- Core Concepts
- Component Reference
- API Reference
- VSCode Extension Guide

### 4. Tutorials (/tutorials)
5 tutorials exist in `fmdocs/tutorials/`:
1. Getting Started (15 min)
2. Building First Pipeline (30 min)
3. Debugging Pipelines (25 min)
4. Testing Pipelines (25 min)
5. Working with Components (35 min)

### 5. Benchmarks (/benchmarks)
Reference `demos/BENCHMARK_REPORT.md`:
- Pipeline execution performance
- Component throughput
- Parallel execution metrics
- Memory usage

### 6. Use Cases Section
Real-world applications:
- **Content Generation Pipelines** - Blog posts, marketing copy
- **Data Processing Workflows** - ETL, transformation
- **Customer Support Automation** - Ticket triage, response generation
- **Code Analysis** - Review, documentation generation
- **Research Assistants** - Document summarization, Q&A

### 7. Creative Use Cases
Innovative applications:
- **AI Writing Rooms** - Multiple AI critics refining content
- **Automated Journalism** - News aggregation and summarization
- **Educational Content** - Curriculum generation
- **Legal Document Analysis** - Contract review pipelines
- **Healthcare Triage** - Symptom analysis workflows

### 8. Pricing Section
- **Free Tier** - Local development, unlimited pipelines
- **Pro** - Team features, priority support
- **Enterprise** - SSO, audit logs, custom integrations

### 9. Footer
- Links: Docs, Tutorials, GitHub, Support
- Contact: support@flowmason.com
- Social links

## Design Guidelines

### Brand
- **Primary Color**: Professional blue (#2563EB or similar)
- **Secondary**: Dark backgrounds for code blocks
- **Font**: Modern sans-serif (Inter, SF Pro, or similar)

### Style
- Clean, minimal design
- Code examples with syntax highlighting
- Animated diagrams for pipeline flows
- Dark mode support

### Technology Suggestions
- **Framework**: Next.js, Astro, or similar
- **Styling**: Tailwind CSS
- **Docs**: MDX or similar
- **Deployment**: Vercel, Netlify, or similar

## Key URLs
- Homepage: flowmason.com
- Docs: flowmason.com/docs
- Tutorials: flowmason.com/tutorials
- Support: flowmason.com/support
- PyPI: pypi.org/project/flowmason/

## Code Examples for Website

### Quick Start
```bash
pip install flowmason
fm init my-project
cd my-project
fm studio start
fm run pipelines/main.pipeline.json
```

### Define a Node
```python
from flowmason_core import node, NodeInput, NodeOutput, Field

@node(name="summarizer", category="reasoning")
class SummarizerNode:
    class Input(NodeInput):
        text: str = Field(description="Text to summarize")

    class Output(NodeOutput):
        summary: str

    async def execute(self, input: Input, context) -> Output:
        response = await context.llm.generate(
            prompt=f"Summarize: {input.text}"
        )
        return self.Output(summary=response.text)
```

### Pipeline Example
```json
{
  "name": "content-pipeline",
  "version": "1.0.0",
  "stages": [
    {"id": "fetch", "component": "http-request", "config": {"url": "{{input.url}}"}},
    {"id": "extract", "component": "json-transform", "depends_on": ["fetch"]},
    {"id": "summarize", "component": "summarizer", "depends_on": ["extract"]}
  ]
}
```

## Files to Reference
- `fmdocs/` - All documentation
- `demos/BENCHMARK_REPORT.md` - Performance benchmarks
- `demos/benchmark_results.json` - Raw benchmark data
- `docs/PROGRESS_SUMMARY.md` - Current state summary
- `README.md` - Package README

## Instructions

When asked to work on the website:
1. Use the context above to understand the product
2. Create compelling, professional content
3. Reference existing docs/benchmarks where appropriate
4. Keep code examples accurate and working
5. Focus on developer experience and clarity
