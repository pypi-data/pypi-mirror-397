# FlowMason Console 2.0 – AI-Orchestrated Design & Run Experience

## 1. Goals

- Make the Console feel like a real AI assistant, not a thin wrapper around HTTP.
- Let users describe what they want in natural language and iteratively refine pipelines without thinking about routes or JSON.
- Use AI + tools in a principled way: design, refine, explain, run, debug.
- Maintain session-level memory and context so the assistant “remembers” goals and decisions.
- Keep the system transparent and debuggable: no hidden magic, clear tool usage.

## 2. Current State (v1) – Summary

- Intent detection is simple and per-turn (`RUN_PIPELINE`, `DESIGN_PIPELINE`, etc.).
- AI pipeline generator exists (`/generate/pipeline` + `nl-interpreter`) and works, but is used in a mostly single-shot way.
- Console can:
  - Design a pipeline from a prompt (with optional Mermaid).
  - Ask clarification questions about input schema ambiguities.
  - Save the generated pipeline.
  - Run a pipeline, and show stage results.
  - Explain + diagram a pipeline.
- Some conversational features exist (clarification loop, “modify” intent), but:
  - Session context is minimal (only `pipeline_id` and some one-off answers).
  - There is no explicit “session state” model.
  - There is no planner that chooses and composes tools for a given user request.

## 3. Target Experience – User Narrative

From the user’s perspective:

1. They describe a goal in plain language:
   - “Create a pipeline with two lists as inputs…”
2. The assistant:
   - Asks clarifying questions until the requirements are clear.
   - Proposes and saves a pipeline.
   - Shows an explanation and Mermaid diagram.
3. The user iterates:
   - “Now add a critic stage…”
   - “Change the output so it also works for Salesforce.”
   - “Explain how the foreach over items works.”
   - “Debug why this failed for input X.”
4. The assistant:
   - Understands these as refinements/queries on the current pipeline.
   - Uses tools to modify, validate, run, and debug without the user touching JSON.

Constraints:

- Prompts must be intuitive regardless of domain (Salesforce, ML, ETL, etc.).
- No “secret commands” required; command syntax is optional sugar, not a dependency.
- The assistant must always be explicit about what it did (design, modify, run).

## 4. Core Concepts & Components

### 4.1 Sessions, Conversations, and Pipelines

We distinguish three layers of context:

1. **Session** (per browser tab / client `session_id`)
   - Technical container, used to key server-side state.
2. **Conversation** (per “goal”)
   - A long-running interaction about one main objective.
   - Example: “design and refine the items+questions pipeline”.
3. **Pipeline Context**
   - The concrete pipeline(s) being designed, refined, or run within a conversation.

### 4.1.1 ConsoleSessionState

Introduce an explicit, persistent `ConsoleSessionState` per `session_id`:

- `session_id: str`
- `current_conversation_id: Optional[str]`
- `conversations: Dict[str, ConversationState]` (small map of active/recent conversations)

### 4.1.2 ConversationState

Each conversation tracks:

- `conversation_id: str`
- `goal: Optional[str]` – short natural language summary.
- `requirements: Dict[str, Any]`
  - `data_sources`, `outputs`, `constraints`, `platform`, etc.
  - Clarifications answered so far.
- `pipeline_context: PipelineContext`
  - `current_pipeline_id: Optional[str>`
  - `recent_pipelines: List[{id, name, version}]`
- `history_summary: str`
  - Compressed summary of prior turns.
- `last_actions: List[str]`
  - Recent tools invoked (“design”, “modify”, “run”, etc.).

Storage options:

- Phase 1: in-memory map keyed by `session_id` (single-node dev).
- Later: pluggable storage (SQLite/Redis) for multi-instance deployments.

### 4.2 Planner

Add a planner layer that decides which tools to call for each user turn.

Inputs:

- `message`: latest user input.
- `session_state`: as above.
- Optional: last tool outputs.

Outputs:

- A small plan: ordered list of actions, e.g.:
  - `["DESIGN_PIPELINE"]`
  - `["VIEW_PIPELINE", "EXPLAIN_PIPELINE"]`
  - `["MODIFY_PIPELINE", "VIEW_PIPELINE"]`
  - `["DEBUG_ERROR"]`

Implementation options:

- v1: deterministic rules (similar to current intent detection, but richer and using session_state).
- v2: an AI pipeline (“Console Planner”) that:
  - Reads message + session_state JSON.
  - Returns an action plan.

### 4.3 Tool Abstractions

Model existing capabilities as “tools” with small, stable contracts:

- `DesignPipelineTool`:
  - Calls `/generate/pipeline` with interpreter + NL builder.
  - Returns `pipeline_detail`, `analysis`, and `source` (rules/ml/interpreter/diagram).
- `ModifyPipelineTool`:
  - Calls `/generate/pipeline` with:
    - Existing pipeline description/structure as context.
    - Refinement text.
  - Applies result via `PipelineUpdate`.
  - Returns updated pipeline.
- `ViewPipelineTool`:
  - Calls `/pipelines/{id}/views`.
  - Returns `pipeline`, `explanation`, `mermaid_flow`.
- `ExplainPipelineTool`:
  - Thin wrapper over `ViewPipelineTool`, formatted for chat.
- `RunPipelineTool`:
  - Calls `/pipelines/{id}/test` or `/pipelines/{id}/run`.
  - Returns run status, stage results, and output.
- `DebugPipelineTool`:
  - Calls existing debug endpoints (runs, errors).
  - Returns summarized root causes and suggested fixes.

These already exist as routes; “tool” here means a thin, well-typed wrapper used by the planner.

### 4.3.1 Tool Input Context Contract

For every tool, we define a clear context contract:

- Common fields:
  - `message`: latest user message (string).
  - `conversation_state`: minimal structured data (goal, requirements, current pipeline id).
  - `history_summary`: short summary string.
- Tool-specific requirements:
  - `DesignPipelineTool`:
    - Needs: `message`, `conversation_state.requirements`, optional Mermaid diagram.
  - `ModifyPipelineTool`:
    - Needs: `message`, `current_pipeline_id`, existing pipeline description/structure (fetched via storage/views).
  - `ViewPipelineTool` / `ExplainPipelineTool`:
    - Needs: `current_pipeline_id` or explicit pipeline name/id.
  - `RunPipelineTool`:
    - Needs: pipeline id, input object.
  - `DebugPipelineTool`:
    - Needs: pipeline id, possibly last failing run id.

Tools *must not* depend on raw entire message history; they only see the structured context defined above.

### 4.4 AI Pipeline Designer (Interpreter)

The `nl-interpreter` pipeline becomes the canonical “design core”:

- It:
  - Reads the user’s description and session_state.
  - Produces:
    - `intent`, `actions`, `data_sources`, `outputs`, `constraints`, `ambiguities`.
    - `suggested_components` and `suggested_patterns`.
    - Optional `proposed_pipeline` (rich FlowMason pipeline JSON).
- It should be used in:
  - Initial design.
  - Major refinements (MODIFY).
  - Possibly “explain” requests to generate better explanations.

## 5. Interaction Model

### 5.1 Turn Types

We support the following conceptual turn types:

1. **Start / Goal Setting**
   - “I want to design a pipeline that …”
   - Planner chooses `DESIGN_PIPELINE`.
2. **Refinement**
   - “Now add a critic stage …”
   - Planner chooses `MODIFY_PIPELINE`.
3. **Clarification**
   - Triggered by tools reporting ambiguities.
   - Planner asks questions until ambiguity set is empty or user stops.
4. **Inspection**
   - “Explain this pipeline”, “show me the flow”.
   - Planner chooses `VIEW_PIPELINE` + `EXPLAIN_PIPELINE`.
5. **Execution / Testing**
   - “Run it with sample data”, “test this pipeline”.
   - Planner chooses `RUN_PIPELINE` (possibly with interactive input gather).
6. **Debugging**
   - “Why did it fail for X?”.
   - Planner chooses `DEBUG_ERROR` and explains.

### 5.2 Context & Memory Update Per Turn

On each turn:

1. Planner decides actions based on `message + session_state`.
2. Tools execute in order.
3. The console:
   - Renders AI messages + any diagrams/results.
   - Updates `conversation_state`:
     - `current_pipeline_id` if changed (and push into `recent_pipelines`).
     - `goal` and `requirements` when clarified/refined.
     - Append to `last_actions`.
   - Updates `history_summary`:
     - Keep last N raw messages.
     - Periodically summarize older turns into a short summary string.

## 6. Implementation Phases

### Phase 1 – Formalize Session & Conversation State

- Add `ConsoleSessionState` and `ConversationState` models.
- Add an in-memory `SessionStore` keyed by `session_id`.
- Wire `/console/ai` to:
  - Read `session_id` from `ConsoleRequest`.
  - Load/create session state and a default conversation.
  - Keep `conversation_state.pipeline_context` up to date when design/modify succeeds.

### Phase 2 – Planner v1 (Rule-Based)

- Refactor `_detect_intent` into a small planner that:
  - Uses `message` and `session_state` to choose a list of actions.
  - Still returns a primary `intent` for compatibility with the frontend.
- Implement action execution order in `ai_console`:
  - For now, we mostly execute the first action, but structure the code so we can add more later.

### Phase 3 – Tool Wrappers

- Factor out the logic for:
  - Design (`/generate/pipeline`).
  - Modify (design + `update_pipeline`).
  - View (`/pipelines/{id}/views`).
  - Run (`/pipelines/{id}/test`).
  - Debug (existing debug analysis).
- Each should be a small function that takes strongly-typed inputs and returns clear outputs.
- `ai_console` becomes orchestration glue between planner and tools.

### Phase 4 – Clarification Framework

- Standardize how tools report ambiguities:
  - Interpreter + NL builder already track `ambiguities`; ensure they are consistently surfaced via `analysis`.
  - `ai_console` converts these into `ClarificationQuestion`s.
- Enhance the question text:
  - Use interpreter context to generate more natural, goal-oriented questions.
- Persist clarifications into session `requirements` so they are not re-asked.

### Phase 5 – AI Planner (Optional, but recommended)

- Implement a “Console Planner” pipeline (similar to `nl-interpreter`):
  - Input: `message`, `session_state` JSON.
  - Output: `actions: string[]`, maybe `reasoning`.
- Use this pipeline in place of, or alongside, the rule-based planner.
- Start conservatively:
  - AI planner suggests actions.
  - Apply a guardrail layer that validates actions against allowed set.

### Phase 6 – UX Polish in Frontend

- Console should:
  - Always echo user answers in clarification mode.
  - Show a small “Context” panel with:
    - Current goal.
    - Current pipeline name/id and versions (recent pipelines).
    - Key requirements (data_sources, outputs, platform).
  - Label responses clearly:
    - “AI designed a new pipeline and saved it.”
    - “AI modified your pipeline and bumped version to X.”
    - “AI ran the pipeline with these inputs.”
  - Offer suggested follow-ups (chips/buttons), e.g.:
    - “Explain this pipeline”
    - “Run interactively”
    - “Refine this step”
- Make commands truly optional:
  - Keep help text, but make free-form language the primary path.

## 7. Guardrails, Safety, and Failure Modes

- All AI tools operate within existing validation and storage layers.
- Modify actions use `PipelineUpdate` and existing validation to avoid unsafe edits.
- Versioning:
  - Each AI modification increments version; consider retaining previous versions or a small history for rollback.
  - Optionally support a “propose-only” mode where modifications are shown (diff) before commit.
- Debug responses must clearly distinguish:
  - AI hypotheses vs. actual error messages from the engine.
- When prerequisites are missing (e.g. registry not initialized, no providers configured):
  - Console should not attempt design/modify.
  - Instead, respond with a clear system message describing what is missing and how to fix it.

## 8. Observability & Feedback

- Log structured telemetry for each console turn:
  - Session/conversation id (anonymized).
  - Actions chosen by planner.
  - Tools invoked and high-level outcomes (success/failure).
  - Whether interpreter/NL builder were used.
- Allow optional user feedback on AI designs and modifications:
  - “This design was helpful / not helpful”.
  - Feed these into future tuning.

## 9. Alignment with MCP Assistant and Tools

- FlowMason already has an MCP assistant and tool catalog.
- Console planner and MCP assistant should converge on:
  - A shared tool model and registry.
  - Shared concepts for session and conversation state where possible.
- This avoids duplicating logic and lets improvements in one surface in the other.

## 10. Migration & Backwards Compatibility

- `ConsoleResponse` remains the primary contract to the frontend.
- We keep existing intents (`RUN_PIPELINE`, `DESIGN_PIPELINE`, etc.) for now.
- As the planner gains more intelligence, we:
  - Map its internal `actions` back to a primary `intent`.
  - Gradually deprecate direct command usage in favor of natural language.

---

This document is the architectural guide for evolving the FlowMason API Console from a command-based tool into a session-aware AI assistant that designs, refines, explains, runs, and debugs pipelines in an intuitive, domain-agnostic way. Implementation should follow the phases above, starting with session + conversation state and planner v1, then tool wrappers and clarification, and only then moving to an AI planner.
