---
title: Local vs Cloud LLM Strategy
---

# Local vs Cloud LLM Strategy

FlowMason is moving toward a **local‑first** AI strategy, with **explicit escalation** to cloud LLMs when needed. This document captures what we want the local LLM to handle, who benefits, and when external models are still required.

## Goals

- Make FlowMason fully usable in **offline / on‑prem / air‑gapped** environments.
- Cover as much **FlowMason‑specific intelligence** as possible with a small, tuned local model.
- Use cloud LLMs **only** when they provide clear, additive value (quality, breadth, or context length).

## A. Product Intelligence (Local‑First)

### 1. FlowMason “How do I…?” Q&A

- **Local LLM can do**
  - Answer questions about components, stages, patterns, deployment, Edge runtime, pipeline schema, and codegen options using internal docs and examples.
- **Who benefits**
  - New users, support, internal teams, solution engineers.
- **External LLM needed when**
  - Questions are mainly about *other* tools/clouds/frameworks or general AI/ML, outside the FlowMason domain.

### 2. Pipeline Explanation & Summarization

- **Local LLM can do**
  - Explain what a pipeline does, summarize stages and dataflow, highlight where inputs/outputs are used, explain simple conditionals/foreach patterns.
- **Who benefits**
  - Developers, support, solution architects.
- **External LLM needed when**
  - Deep system‑level reasoning over many external services/logs is required, or the core issue is outside FlowMason (e.g., infra, databases, auth).

### 3. Basic Pipeline Debugging

- **Local LLM can do**
  - Given a pipeline and error message, point to likely misconfigured stages, missing fields, invalid JSON paths, wrong component ordering, etc.
- **Who benefits**
  - Developers, CS/support, SREs doing first‑line triage.
- **External LLM needed when**
  - Diagnosing complex, cross‑system failures where the majority of context lives outside FlowMason.

### 4. Prompt & `llm_settings` Assistance

- **Local LLM can do**
  - Suggest/improve prompts for generator/critic/summarizer nodes and recommend temperature, max_tokens, top_p, etc., for common patterns.
- **Who benefits**
  - App builders, prompt authors, ML‑adjacent developers.
- **External LLM needed when**
  - High‑end creative writing, very complex reasoning prompts, non‑English or low‑resource languages where a small model is weak.

## B. Pipeline Design & Authoring

### 5. NL → Pipeline Design

- **Local LLM can do**
  - Turn short/medium natural‑language descriptions into draft FlowMason pipelines: stages, component types, dependencies, inputs/outputs, and suggested patterns (e.g., `foreach`, validation+transform, http_ingest+send).
- **Who benefits**
  - New users, SEs, solution architects, pre‑sales.
- **External LLM needed when**
  - Descriptions are very long, complex, or ambiguous; or you want highly creative alternative designs and trade‑offs (GPT‑4‑level “architect”).

### 6. Pattern / Component Suggestions

- **Local LLM can do**
  - Given a partial pipeline, suggest additional stages, common patterns, and best‑practice operators (logging, validation, error handling).
- **Who benefits**
  - Developers expanding pipelines, template authors, internal enablement.
- **External LLM needed when**
  - Exploring completely novel architectures or integrations with many external domains/APIs that the local model hasn’t seen.

### 7. Pipeline “Linting” & Soft Validation

- **Local LLM can do**
  - Soft checks like “does this design make sense?”, “are there obvious missing validations, logging, or error handling?”, and suggest improvements.
- **Who benefits**
  - Teams standardizing pipeline quality and patterns.
- **External LLM needed when**
  - Enforcement of sophisticated, external policies (regulatory, company‑specific rules) that require broader context or non‑FlowMason knowledge.

## C. Code & SDK Work

### 8. Small Scaffolding & Glue Code

- **Local LLM can do**
  - Generate small handlers, config structs, simple helper functions, and glue code tightly constrained by templates and generated SDKs.
- **Who benefits**
  - Developers customizing codegen outputs.
- **External LLM recommended when**
  - Implementing non‑trivial business logic, large functions, multi‑file modules, unfamiliar languages, or major refactors.

### 9. Codegen Guidance (Explain, Don’t Replace)

- **Local LLM can do**
  - Explain the structure of generated projects, what each file does, where to plug in custom logic, and how to configure environments.
- **Who benefits**
  - Developers using FlowMason’s code generators.
- **External LLM recommended when**
  - Asking the model to *author* entirely new services or heavy logic beyond the patterns FlowMason already generates.

### 10. Simple Tests & Examples

- **Local LLM can do**
  - Suggest simple test stubs, example requests, mock payloads, and sample pipelines for docs/demos.
- **Who benefits**
  - Engineers writing tests, docs writers, pre‑sales/demo builders.
- **External LLM recommended when**
  - Designing elaborate test suites, property‑based testing strategies, or very robust coverage plans.

## D. Runtime & Edge

### 11. Edge Summarization & Routing

- **Local LLM can do**
  - Low‑latency summarization of small payloads, simple classifications, routing decisions between a few branches, basic anomaly hints—all via Edge (`OllamaAdapter`, `LlamaCppAdapter`).
- **Who benefits**
  - Edge/IoT deployments, on‑device applications, field engineering.
- **External LLM needed when**
  - Long‑context analysis, complex chain‑of‑thought agents, or heavy planning on the device.

### 12. On‑Prem / Air‑Gapped Intelligent Pipelines

- **Local LLM can do**
  - All FlowMason‑specific reasoning from sections A–C on internal data, fully offline. “Good enough” AI with strong privacy/compliance guarantees.
- **Who benefits**
  - Enterprise, regulated, and cost‑sensitive customers.
- **External LLM needed when**
  - Compliance allows cloud calls *and* the business case requires best‑in‑class reasoning, creativity, or very long context.

## E. Out‑of‑Scope for Local (Today)

These are realistically **cloud‑only** for now:

- High‑quality, large‑scale code generation across many languages and big codebases.
- Very long‑context tasks (large documents, multi‑repo reasoning, long conversations).
- Rich open‑domain Q&A (world knowledge, niche APIs, current events).
- Multimodal tasks (images, audio, video) unless we adopt specialized models.
- Complex autonomous agents that coordinate many tools and steps with high reliability.

## Rule of Thumb

- **Default to local** when the task is:
  - FlowMason‑specific (pipelines, components, docs, runtime behavior),
  - operating on modest context sizes,
  - and “nice to have perfect, but OK if 80–90% good.”
- **Escalate to cloud** when you need:
  - Strong general codegen, long‑context reasoning, broad world/API knowledge,
  - or very high‑stakes accuracy/creativity where small‑model regressions are not acceptable.

