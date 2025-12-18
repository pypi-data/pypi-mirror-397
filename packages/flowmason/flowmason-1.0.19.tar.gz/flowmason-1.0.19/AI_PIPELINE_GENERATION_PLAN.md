# AI Pipeline Generation Roadmap

This document captures the long‑term plan for the natural‑language → pipeline generator so we can keep iterating from a shared roadmap.

## Phase 1 – Stabilize and Observe

- [x] Add focused tests for `NLBuilderService.generate_pipeline`:
  - [x] Simple linear pipeline (e.g. summarize + translate).
  - [x] Foreach prompt → `foreach_items` → `qa_each` → `aggregate_results`.
- [x] Add debug logging for `/api/v1/generate/pipeline`:
  - [x] Log prompt and options (including interpreter flag).
  - [x] Log interpreter context when present.
  - [x] Log NL builder status, validation errors, and warnings.
- [ ] Improve error surfacing for frontend:
  - [ ] Return clear messages when interpreter/generator fails.
  - [ ] Ensure mock/fallback pipelines are clearly indicated as such.

## Phase 2 – Interpreter as Architect

- [x] Extend `nl-interpreter` pipeline output to a richer `GenerationContext`:
  - [x] Intent, actions, data_sources, outputs, constraints, ambiguities.
  - [x] `suggested_components` (real registry component types).
  - [x] `suggested_patterns` (e.g. `foreach`, `validation+transform`, `http_ingest+sink`).
- [ ] Add optional mode where interpreter proposes a full pipeline JSON:
  - [ ] Validate proposed pipeline against schema and registry.
  - [ ] If valid, use as primary candidate; otherwise fall back to planner.

## Phase 3 – Generator as Multi‑Engine Planner

- [x] Use registry‑driven component catalog instead of hard‑coded list.
- [x] Add explicit foreach pattern:
  - [x] Detect foreach/list language in description/analysis.
  - [x] Generate `foreach_items` → `qa_each` → `aggregate_results`.
- [x] Add more explicit patterns:
  - [x] Validation + transform: `schema_validate` → `json_transform`.
  - [x] HTTP ingest + send: `http_request` (source) → transform → `http_request` (sink).
  - [x] Conditional/router for “if/when/otherwise/route” language.
- [x] Define ML proposal interface:
  - [x] `ml_propose_pipeline(context) -> Optional[GeneratedPipeline]`.
  - [x] Wire into `/api/v1/generate/pipeline` as an optional second proposal engine.
- [x] Implement simple candidate selector:
  - [x] Validate candidates structurally.
  - [x] Prefer candidates with fewer validation warnings and better coverage of actions/data_sources.

## Phase 4 – Validation, Simulation, and Cost Awareness

- [ ] Strengthen validation:
  - [ ] Type/shape consistency across edges using component schemas.
  - [ ] Control‑flow checks for foreach/conditional/router wiring.
  - [ ] Ensure required component fields are satisfied by mappings.
- [ ] Add a “dry‑run” simulation mode:
  - [ ] Run generated pipelines with synthetic/sample inputs.
  - [ ] Produce traces without hitting real external APIs/LLMs.
- [ ] Add cost/latency estimation:
  - [ ] Estimate token usage per LLM stage with default providers.
  - [ ] Estimate per‑stage and overall latency.

## Phase 5 – Learning Loop (Data + Models)

- [ ] Log training signals for every generation:
  - [x] Prompt and options.
  - [x] Interpreter output (GenerationContext).
  - [x] Candidate pipeline (`P_rules`) and chosen one.
  - [ ] Final pipeline after user edits.
  - [ ] Explicit feedback (if available).
- [ ] Train offline models:
  - [ ] Proposal model: `prompt/context → pipeline` (or diff).
  - [ ] Ranking model: score candidate pipelines.
- [ ] Integrate models:
  - [ ] Use ML proposals via the Phase 3 interface.
  - [ ] Use ranking model instead of simple heuristics when available.
- [ ] Add org‑level preferences:
  - [ ] Configurable guidelines (logging, validation, providers).
  - [ ] Feed preferences into both rules and ML features.

## Phase 6 – UX: Expose Reasoning and Multi‑Turn Design

- [x] Add “What the AI understood” panel in Generate page:
  - [x] Show analysis (intent/actions/data_sources/ambiguities).
  - [x] Show suggested patterns.
  - [x] Show chosen components with short rationales.
- [ ] Support multi‑turn refinement:
  - [ ] Allow follow‑up instructions (“add error handling”, “make foreach parallel”, etc.).
  - [ ] Treat each turn as refinement of context + pipeline, not a fresh start.
- [ ] Make AI vs rule‑based behavior explicit:
  - [ ] UI indicators for interpreter/LLM/ML usage.
  - [ ] Toggles for “quick draft” vs “deep design”.

## Phase 7 – Safety, Governance, and Meta‑Pipelines

- [ ] Policy‑aware generation:
  - [ ] Define org‑level rules for allowed components/destinations/data.
  - [ ] Enforce these during generation and validation.
- [ ] Versioning and audit:
  - [ ] Record provenance for each generated pipeline (prompts, models, context).
  - [ ] Provide tools to diff and roll back AI‑generated changes.
- [ ] Meta‑pipelines:
  - [ ] Build pipelines that monitor other pipelines (errors, drift, usage).
  - [ ] Trigger suggestions or auto‑refinements when issues are detected.

---

We can update this file as we make progress (checking items off and adding notes per phase) and use it as the canonical reference for future work on the natural‑language pipeline generator.
