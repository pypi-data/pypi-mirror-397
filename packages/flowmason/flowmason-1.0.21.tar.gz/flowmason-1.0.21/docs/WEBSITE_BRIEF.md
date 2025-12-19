# FlowMason Website Development Brief

## Project Overview

Build a professional, compelling website for **FlowMason** - an AI pipeline orchestration platform at **flowmason.com**.

---

## Product Summary

FlowMason is **Universal AI Workflow Infrastructure** that enables developers to:
- **Design** - Visual pipeline builder with drag-and-drop components
- **Build** - Three component types: Nodes (AI), Operators (deterministic), Control Flow
- **Debug** - Full debugging with breakpoints, step-through, prompt iteration
- **Deploy** - File-based development → Database-backed production (Salesforce DX-style)

### The Pitch
> "Build AI pipelines like Salesforce apps - develop locally with files, deploy to production orgs, expose as APIs."

---

## Current State (v0.4.1)

### Distribution Channels
| Channel | Status | Command/URL |
|---------|--------|-------------|
| **PyPI** | ✅ Live | `pip install flowmason` |
| **VSCode** | Ready | Pending Marketplace publish |
| **Docker** | Pending | `flowmason/studio:0.4.1` |

### CLI Commands
```
fm run, fm validate, fm init, fm deploy, fm pull,
fm pack, fm install, fm uninstall, fm list,
fm studio, fm org, fm auth
```

### Components (18 built-in)
- **6 Control Flow**: Conditional, ForEach, TryCatch, Router, SubPipeline, Return
- **7 Operators**: HttpRequest, JsonTransform, Filter, Loop, SchemaValidate, VariableSet, Logger
- **5 AI Nodes**: Generator, Critic, Improver, Selector, Synthesizer

---

## Website Structure

### Pages Required

```
flowmason.com/
├── /                    # Homepage (hero, features, CTA)
├── /docs/               # Documentation hub
│   ├── /getting-started
│   ├── /concepts
│   ├── /components
│   ├── /api
│   └── /vscode
├── /tutorials/          # Step-by-step guides
│   ├── /getting-started
│   ├── /first-pipeline
│   ├── /debugging
│   ├── /testing
│   └── /components
├── /use-cases/          # Real-world applications
├── /benchmarks/         # Performance data
├── /pricing/            # Tiers and plans
├── /blog/               # Updates and articles
└── /support/            # Contact and help
```

---

## Homepage Sections

### 1. Hero
**Headline Options:**
- "Build AI Pipelines That Scale"
- "From Prototype to Production in Minutes"
- "The Developer Platform for AI Workflows"

**Subheadline:**
> "Design, debug, and deploy intelligent pipelines with a Salesforce DX-style workflow. File-based development, database-backed production."

**CTAs:**
- Primary: "Get Started Free" → Installation
- Secondary: "View Documentation" → Docs

**Quick Install:**
```bash
pip install flowmason
fm init my-project && fm studio start
```

### 2. Key Features (6 cards)

| Feature | Description | Icon Idea |
|---------|-------------|-----------|
| **Visual Pipeline Builder** | Design workflows visually in VSCode or Studio | Flowchart |
| **Three Component Types** | Nodes (AI), Operators (data), Control Flow | Blocks |
| **Full Debugging** | Breakpoints, step-through, prompt iteration | Bug |
| **Package System** | Distribute as .fmpkg, install anywhere | Package |
| **Multi-Environment** | Local → Staging → Production | Cloud layers |
| **Enterprise Ready** | API keys, RBAC, SSO/SAML, audit logs | Shield |

### 3. How It Works (3 steps)

**Step 1: Define Components**
```python
@node(name="summarizer")
class SummarizerNode:
    async def execute(self, input, context):
        return await context.llm.generate(input.prompt)
```

**Step 2: Compose Pipelines**
```json
{
  "stages": [
    {"id": "fetch", "component": "http-request"},
    {"id": "process", "component": "summarizer", "depends_on": ["fetch"]}
  ]
}
```

**Step 3: Deploy & Scale**
```bash
fm deploy --target production
# Pipeline now available at: POST /api/pipelines/my-pipeline/run
```

### 4. Use Cases Grid

| Industry | Use Case | Pipeline Example |
|----------|----------|------------------|
| **Content** | Blog Generation | Research → Draft → Edit → Publish |
| **Support** | Ticket Triage | Classify → Route → Draft Response |
| **Data** | ETL Pipelines | Extract → Transform → Validate → Load |
| **Code** | PR Review | Analyze → Comment → Suggest Fixes |
| **Legal** | Contract Analysis | Parse → Extract Clauses → Flag Risks |
| **Research** | Paper Summarization | Fetch → Summarize → Cross-Reference |

### 5. Benchmarks Preview

From `demos/BENCHMARK_REPORT.md`:
- **Throughput**: X pipelines/second
- **Latency**: <Yms average stage execution
- **Parallel**: Up to 10 concurrent stages
- **Memory**: Efficient streaming for large payloads

### 6. Testimonials/Social Proof
(Placeholder for future testimonials)

### 7. Pricing Preview

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | Local dev, unlimited pipelines, community support |
| **Pro** | $29/user/mo | Team features, priority support, advanced debugging |
| **Enterprise** | Custom | SSO, audit logs, SLA, dedicated support |

### 8. Footer
- **Product**: Features, Pricing, Roadmap
- **Resources**: Docs, Tutorials, Blog, Benchmarks
- **Company**: About, Contact, Careers
- **Legal**: Privacy, Terms, License

---

## Documentation Content

### Existing Docs (in fmdocs/)
```
fmdocs/
├── 00-status/           # Implementation status
├── 01-vision/           # Product vision, hybrid model
├── 02-getting-started/  # Installation, quickstart
├── 03-concepts/         # Architecture, components, pipelines
├── 04-core-framework/   # Decorators, types, execution
├── 05-components/       # Component reference
├── 06-studio/           # Backend API reference
├── 07-vscode-extension/ # Extension features
├── 08-packaging-deployment/ # CI/CD, publishing
├── 09-debugging-testing/    # Debug and test guides
└── 10-architecture/     # System deep dive
```

### Tutorials (in fmdocs/tutorials/)
| # | Title | Duration |
|---|-------|----------|
| 1 | Getting Started | 15 min |
| 2 | Building Your First Pipeline | 30 min |
| 3 | Debugging Pipelines | 25 min |
| 4 | Testing Pipelines | 25 min |
| 5 | Working with Components | 35 min |

---

## Design Requirements

### Brand Identity
- **Name**: FlowMason
- **Tagline**: "Universal AI Workflow Infrastructure"
- **Domain**: flowmason.com
- **Email**: support@flowmason.com

### Color Palette
- **Primary**: Blue (#2563EB) - Trust, technology
- **Secondary**: Slate (#1E293B) - Code blocks, dark mode
- **Accent**: Green (#10B981) - Success, CTA
- **Background**: White/Slate variants

### Typography
- **Headings**: Bold, modern sans-serif (Inter, Plus Jakarta Sans)
- **Body**: Clean, readable (Inter, system fonts)
- **Code**: Monospace (JetBrains Mono, Fira Code)

### Visual Elements
- **Icons**: Lucide, Heroicons, or custom
- **Illustrations**: Pipeline flow diagrams, architecture visuals
- **Code Blocks**: Syntax highlighted, copy button
- **Animations**: Subtle, purposeful (pipeline flow, connections)

---

## Technical Stack Suggestions

### Option A: Next.js + MDX
```
Pros: React ecosystem, great for docs, Vercel deployment
Stack: Next.js 14, Tailwind CSS, MDX, Contentlayer
```

### Option B: Astro
```
Pros: Fast, content-focused, great for docs
Stack: Astro, Tailwind CSS, MDX
```

### Option C: Docusaurus
```
Pros: Built for docs, search included
Stack: Docusaurus 3, React, Algolia
```

### Deployment
- **Host**: Vercel (recommended) or Netlify
- **CDN**: Cloudflare
- **Analytics**: Plausible or PostHog

---

## Content to Migrate

### From Repository
| Source | Destination |
|--------|-------------|
| `fmdocs/*.md` | /docs/* |
| `fmdocs/tutorials/*.md` | /tutorials/* |
| `demos/BENCHMARK_REPORT.md` | /benchmarks |
| `README.md` | Reference for homepage |

### Benchmark Data
From `demos/benchmark_results.json` - extract key metrics for visualization.

---

## SEO Targets

### Primary Keywords
- AI pipeline builder
- LLM workflow orchestration
- AI workflow automation
- Pipeline debugging tool
- AI development platform

### Pages to Optimize
- Homepage: "FlowMason - AI Pipeline Orchestration Platform"
- Docs: "FlowMason Documentation - Build AI Workflows"
- Tutorials: "FlowMason Tutorials - Learn AI Pipeline Development"

---

## Launch Checklist

- [ ] Homepage with all sections
- [ ] Documentation migrated from fmdocs/
- [ ] Tutorials published
- [ ] Benchmarks page with visualizations
- [ ] Use cases with examples
- [ ] Pricing page
- [ ] Contact/Support page
- [ ] SEO meta tags
- [ ] Open Graph images
- [ ] Analytics setup
- [ ] SSL certificate
- [ ] 404 page
- [ ] Mobile responsive
- [ ] Dark mode (optional)

---

## Prompt for New Session

Use this to start a new Claude session for website development:

```
I'm building the website for FlowMason (flowmason.com) - an AI pipeline orchestration platform.

Key context:
- Product: Universal AI Workflow Infrastructure for building, debugging, and deploying AI pipelines
- Model: Salesforce DX-style (file-based development → database production)
- Current version: 0.4.1 on PyPI (pip install flowmason)
- Repository: /Users/sam/Documents/CCAT/flow/flowmason

Reference files:
- docs/WEBSITE_BRIEF.md - Full website brief
- fmdocs/ - All documentation content
- demos/BENCHMARK_REPORT.md - Performance benchmarks
- README.md - Product overview

I need a professional, compelling website with:
1. Homepage (hero, features, use cases, CTA)
2. Documentation (from fmdocs/)
3. Tutorials (5 existing tutorials)
4. Benchmarks (performance data)
5. Use cases (real-world examples)
6. Pricing page

Please help me build this website using [Next.js/Astro/your preferred framework].
```

---

## Claude Command

A Claude command has been created at `.claude/commands/website.md` that can be invoked with `/website` to get full context for website work.
