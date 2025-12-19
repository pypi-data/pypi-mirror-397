"""
AI Console API Routes.

High-level AI-driven console endpoint that:
- Interprets natural language / command-style input
- Plans actions (design/run/explain) using existing Studio APIs
- Returns a structured response suitable for a chat-style UI.
"""

import json
import os
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from flowmason_core.registry import ComponentRegistry
from flowmason_studio.api.routes.registry import get_registry
from flowmason_studio.api.routes import generate as generate_routes  # type: ignore
from flowmason_studio.api.routes.generate import GeneratePipelineRequest  # type: ignore
from flowmason_studio.models.api import (
    PipelineCreate,
    PipelineInputSchema,
    PipelineOutputSchema,
    PipelineStage,
)
from flowmason_studio.services.storage import (
    get_pipeline_storage,
    get_run_storage,
    PipelineStorage,
    RunStorage,
)
from flowmason_studio.api.routes.pipelines import get_pipeline  # type: ignore
from flowmason_studio.models.api import PipelineDetail, PipelineInputSchema, PipelineOutputSchema, PipelineStage
from flowmason_studio.services.console_session import ConsoleSessionState, get_session_store
from flowmason_studio.api.routes.execution import _execute_pipeline_task  # type: ignore

router = APIRouter(prefix="/console", tags=["console"])


ConsoleIntent = Literal[
    "DESIGN_PIPELINE",
    "MODIFY_PIPELINE",
    "RUN_PIPELINE",
    "VIEW_PIPELINE",
    "EXPLAIN_PIPELINE",
    "SHOW_DIAGRAMS",
    "DEBUG_ERROR",
    "HELP",
    "UNKNOWN",
]


class ConsoleHistoryItem(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ConsoleContext(BaseModel):
    pipeline_id: Optional[str] = None
    pipeline_name: Optional[str] = None
    selected_stage_id: Optional[str] = None
    mode: Literal["auto", "design", "run", "explain", "debug"] = "auto"
    include_diagrams: Literal["none", "flow", "all"] = "flow"


class ClarificationQuestion(BaseModel):
    id: str
    path: str
    question: str
    expected_type: Literal["string", "number", "boolean", "object", "array", "json"]
    required: bool = True
    choices: Optional[List[Dict[str, Any]]] = None
    schema: Optional[Dict[str, Any]] = None
    examples: Optional[List[Any]] = None


class ConsoleOptions(BaseModel):
    allow_state_changes: bool = True
    max_planner_steps: int = 3


class ConsoleRequest(BaseModel):
    version: str = Field("v1", description="API version for the console contract")
    session_id: Optional[str] = None
    message: str
    history: Optional[List[ConsoleHistoryItem]] = None
    context: Optional[ConsoleContext] = None
    clarification_answers: Optional[Dict[str, Any]] = None
    options: Optional[ConsoleOptions] = None


class ConsoleRunStageResult(BaseModel):
    stage_id: str
    component_type: str
    status: str
    duration_ms: Optional[int] = None
    output_preview: Optional[str] = None
    error: Optional[str] = None


class ConsoleRunResult(BaseModel):
    pipeline_id: str
    run_id: Optional[str] = None
    inputs_used: Dict[str, Any] = {}
    stage_results: List[ConsoleRunStageResult] = []
    final_output: Optional[Dict[str, Any]] = None


class ConsoleActionResult(BaseModel):
    kind: Literal[
        "pipeline_design",
        "pipeline_patch",
        "run_result",
        "explanation",
        "diagrams",
        "noop",
    ]
    run: Optional[ConsoleRunResult] = None
    # Additional result kinds can be added over time.


class ConsoleAction(BaseModel):
    id: str
    type: ConsoleIntent | Literal["NOOP"]
    status: Literal["pending", "done", "error", "skipped"]
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[ConsoleActionResult] = None


class ConsolePipelineStageSummary(BaseModel):
    id: str
    name: str
    component_type: str
    depends_on: List[str] = []
    changed_by_ai: bool = False


class ConsolePipelineSummary(BaseModel):
    pipeline_id: str
    name: str
    description: Optional[str] = None
    input_schema: Dict[str, Any] = {}
    output_stage_id: Optional[str] = None
    stages: List[ConsolePipelineStageSummary] = []


class ConsoleDiagrams(BaseModel):
    flowchart: Optional[str] = None
    sequence: Optional[str] = None
    class_: Optional[str] = Field(None, alias="class")

    class Config:
        allow_population_by_field_name = True


class ConsoleError(BaseModel):
    code: str
    message: str
    source: Literal["planner", "mapping", "execution", "llm", "validation", "other"]
    details: Optional[Dict[str, Any]] = None


class ConsoleMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ConsoleResponse(BaseModel):
    version: str = "v1"
    intent: ConsoleIntent
    confidence: float
    needs_clarification: bool = False
    clarification_questions: List[ClarificationQuestion] = []
    actions: List[ConsoleAction] = []
    pipeline_summary: Optional[ConsolePipelineSummary] = None
    diagrams: Optional[ConsoleDiagrams] = None
    errors: List[ConsoleError] = []
    console_messages: List[ConsoleMessage] = []


def _run_console_planner(
    message: str,
    session_state: ConsoleSessionState,
) -> Optional[Dict[str, Any]]:
    """
    Run the console planner pipeline (if available) to propose
    a primary_intent and list of actions for this turn.

    Returns the raw output dict on success, or None on failure.
    """
    from pathlib import Path

    pipeline_path = Path("pipelines") / "console_planner.pipeline.json"
    if not pipeline_path.is_file():
        return None

    try:
        with pipeline_path.open("r", encoding="utf-8") as f:
            pipeline_data = json.load(f)
    except Exception:
        return None

    try:
        # Build a PipelineDetail from the JSON definition
        stages: List[PipelineStage] = []
        for stage_data in pipeline_data.get("stages", []):
            stages.append(
                PipelineStage(
                    id=stage_data.get("id"),
                    name=stage_data.get("name", stage_data.get("id")),
                    component_type=stage_data.get("component_type")
                    or stage_data.get("component"),
                    config=stage_data.get("config", {}),
                    input_mapping=stage_data.get("input_mapping", {}),
                    depends_on=stage_data.get("depends_on", []),
                )
            )

        input_schema_raw = pipeline_data.get("input_schema", {}) or {}
        output_schema_raw = pipeline_data.get("output_schema", {}) or {}

        planner_detail = PipelineDetail(  # type: ignore[call-arg]
            id=pipeline_data.get("id", "console-planner"),
            name=pipeline_data.get("name", "console-planner"),
            description=pipeline_data.get(
                "description",
                "Console planner pipeline",
            ),
            version=pipeline_data.get("version", "1.0.0"),
            input_schema=PipelineInputSchema(**input_schema_raw),
            output_schema=PipelineOutputSchema(**output_schema_raw),
            stages=stages,
            output_stage_id=pipeline_data.get("output_stage_id"),
            category=pipeline_data.get("category"),
            tags=pipeline_data.get("tags", []),
            is_template=False,
            status="draft",  # type: ignore[arg-type]
            sample_input=None,
            last_test_run_id=None,
            published_at=None,
            output_config=None,
        )

        # Execute planner pipeline inline using the same execution task
        # used by the main execution API.
        from flowmason_studio.services.storage import RunStorage, get_run_storage
        from flowmason_studio.api.routes.registry import get_registry  # type: ignore

        run_storage: RunStorage = get_run_storage()
        registry = get_registry()

        # Create a temporary run record
        run = run_storage.create(
            pipeline_id=planner_detail.id,
            inputs={},
            org_id=None,
        )

        planner_input = {
            "message": message,
            "session": session_state.model_dump(mode="json"),
        }

        # Execute synchronously
        import asyncio

        async def _run():
            await _execute_pipeline_task(
                run_id=run.id,
                pipeline_detail=planner_detail,
                inputs=planner_input,
                registry=registry,
                run_storage=run_storage,
                breakpoints=None,
                org_id=None,
            )

        asyncio.run(_run())

        completed = run_storage.get(run.id, org_id=None)
        if completed and completed.output and isinstance(completed.output, dict):
            return completed.output  # type: ignore[return-value]
    except Exception:
        # Planner is best-effort; on failure we simply ignore it
        return None

    return None


def _build_mermaid_from_pipeline(pipeline: PipelineDetail) -> str:
    """Build a simple flowchart TD diagram from a PipelineDetail."""
    stages = pipeline.stages or []
    stage_ids = [s.id for s in stages]

    lines: List[str] = ["flowchart TD", "  IN((Input))"]

    for stage in stages:
        label_text = stage.name or stage.id
        label = f"{label_text}\\n[{stage.component_type}]"
        lines.append(f'  {stage.id}["{label}"]')

    for stage in stages:
        depends = stage.depends_on or []
        if depends:
            for dep in depends:
                if dep in stage_ids:
                    lines.append(f"  {dep} --> {stage.id}")
        else:
            lines.append(f"  IN --> {stage.id}")

    output_id = pipeline.output_stage_id
    if output_id and output_id in stage_ids:
        lines.append(f"  {output_id} --> OUT((Output))")

    return "\n".join(lines)


def _detect_intent(message: str) -> ConsoleIntent:
    """Very small, deterministic intent detection for v1."""
    text = message.strip().lower()
    if not text:
        return "HELP"
    if text in {"help", "?", "commands"}:
        return "HELP"
    # Treat common "design/create/build pipeline" phrasings as design requests.
    if text.startswith(("design ", "design a pipeline", "create pipeline", "build pipeline")):
        return "DESIGN_PIPELINE"
    # Also handle more natural phrasing like "create a pipeline that ..."
    if "pipeline" in text and any(w in text for w in ["design", "create", "build", "generate"]):
        return "DESIGN_PIPELINE"
    if text.startswith(("view ", "show pipeline", "open pipeline")):
        return "VIEW_PIPELINE"
    if text.startswith(("run ", "runi ")):
        return "RUN_PIPELINE"
    if text.startswith(("modify ", "change ", "update ", "refine ")):
        return "MODIFY_PIPELINE"
    if text.startswith(("explain ", "describe ")):
        return "EXPLAIN_PIPELINE"
    if text.startswith(("diagram ", "mermaid ")):
        return "SHOW_DIAGRAMS"
    if any(word in text for word in ["error", "failing", "broken"]):
        return "DEBUG_ERROR"
    # For v1, everything else is treated as a request to run or design pipelines
    return "RUN_PIPELINE"


@router.post("/ai", response_model=ConsoleResponse)
async def ai_console(
    request: ConsoleRequest,
    storage: PipelineStorage = Depends(get_pipeline_storage),
    registry: ComponentRegistry = Depends(get_registry),
    run_storage: RunStorage = Depends(get_run_storage),
) -> ConsoleResponse:
    """
    AI Console entrypoint (v1).

    This implementation is intentionally conservative:
    - Uses simple pattern-based intent detection
    - For RUN_PIPELINE/EXPLAIN_PIPELINE/SHOW_DIAGRAMS, looks up pipelines
    - Falls back to HELP-style responses for unknown cases
    """
    message = request.message.strip()
    intent = _detect_intent(message)
    confidence = 0.7  # Static baseline; may be refined by planner

    # Load or create console session state (per session_id)
    session_id = request.session_id or "default"
    session_store = get_session_store()
    session_state = session_store.get_or_create(session_id)

    # Optional AI planner: if enabled, let the console-planner pipeline
    # propose a primary_intent and actions based on the message and session.
    planner_enabled = os.getenv("FLOWMASON_CONSOLE_PLANNER_ENABLED", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    planner_plan: Optional[Dict[str, Any]] = None
    if planner_enabled:
        planner_plan = _run_console_planner(message, session_state)
        if isinstance(planner_plan, dict):
            planner_intent = str(planner_plan.get("primary_intent") or "").upper()
            if planner_intent in {
                "DESIGN_PIPELINE",
                "MODIFY_PIPELINE",
                "RUN_PIPELINE",
                "VIEW_PIPELINE",
                "EXPLAIN_PIPELINE",
                "SHOW_DIAGRAMS",
                "DEBUG_ERROR",
                "HELP",
                "UNKNOWN",
            }:
                intent = planner_intent  # type: ignore[assignment]
                # Slightly boost confidence when planner is used
                confidence = 0.9

            # Update goal/requirements from planner, if provided
            goal = planner_plan.get("goal")
            if isinstance(goal, str) and goal.strip():
                session_state.conversation.goal = goal.strip()

            req_update = planner_plan.get("requirements_update")
            if isinstance(req_update, dict):
                session_store.update_requirements(session_id, req_update)

    actions: List[ConsoleAction] = []
    pipeline_summary: Optional[ConsolePipelineSummary] = None
    diagrams: Optional[ConsoleDiagrams] = None
    errors: List[ConsoleError] = []
    console_messages: List[ConsoleMessage] = []
    run_result: Optional[ConsoleRunResult] = None
    needs_clarification: bool = False
    clarification_questions: List[ClarificationQuestion] = []

    # v1: if the user references a pipeline by name/id, try to resolve it
    target_pipeline: Optional[PipelineDetail] = None
    remaining = message
    parts = message.split()
    if parts:
        command = parts[0].lower()
        if command in {"run", "runi", "explain", "diagram", "mermaid"}:
            remaining = message[len(parts[0]) :].strip()

    # Resolve pipeline by context or by fuzzy name
    pipeline_hint = request.context.pipeline_id if request.context else None
    pipeline_name_hint = request.context.pipeline_name if request.context else None
    if pipeline_hint:
        try:
            target_pipeline = await get_pipeline(pipeline_hint)  # type: ignore[arg-type]
        except HTTPException:
            target_pipeline = None

    if target_pipeline is None and (remaining or pipeline_name_hint):
        # Fall back to simple name/id lookup
        try:
            summaries, _total = storage.list(limit=100, offset=0)
            candidates = summaries or []
            search_name = (remaining or pipeline_name_hint or "").strip().lower()
            for p in candidates:
                if p.id == search_name or p.name.lower() == search_name:
                    # Load full detail for the matched pipeline
                    target_pipeline = storage.get(p.id, org_id=None)
                    break
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(
                ConsoleError(
                    code="pipeline_lookup_failed",
                    message=str(exc),
                    source="execution",
                )
            )

    # Build pipeline summary if we have one
    if target_pipeline is not None:
        pipeline_summary = ConsolePipelineSummary(
            pipeline_id=target_pipeline.id,
            name=target_pipeline.name,
            description=target_pipeline.description,
            input_schema=target_pipeline.input_schema or {},
            output_stage_id=target_pipeline.output_stage_id,
            stages=[
                ConsolePipelineStageSummary(
                    id=s.id,
                    name=s.name,
                    component_type=s.component_type,
                    depends_on=s.depends_on or [],
                    changed_by_ai=False,
                )
                for s in (target_pipeline.stages or [])
            ],
        )

        if (request.context or ConsoleContext()).include_diagrams != "none":
            flowchart = _build_mermaid_from_pipeline(target_pipeline)
            diagrams = ConsoleDiagrams(flowchart=flowchart)

    # If we have a pipeline in context and the message looks like a
    # refinement request (but wasn't explicitly classified), treat it
    # as MODIFY_PIPELINE to support chat-style editing.
    if intent == "RUN_PIPELINE" and target_pipeline is not None:
        lowered = message.strip().lower()
        if any(
            phrase in lowered
            for phrase in [
                "now add ",
                "add a ",
                "add ",
                "remove ",
                "replace ",
                "change ",
                "update ",
                "refine ",
            ]
        ):
            intent = "MODIFY_PIPELINE"

    # Persist any clarification answers into session requirements so
    # they become part of the broader context for this conversation.
    if request.clarification_answers:
        session_store.update_requirements(session_id, request.clarification_answers)

    # HELP intent: guidance only
    if intent == "HELP":
        console_messages.append(
            ConsoleMessage(
                role="assistant",
                content=(
                    "Welcome to the AI Console (v1).\n\n"
                    "You can say things like:\n"
                    "- \"run <pipeline-name-or-id>\" to execute a pipeline\n"
                    "- \"explain <pipeline-name-or-id>\" to get a structural explanation\n"
                    "- \"diagram <pipeline-name-or-id>\" to see a Mermaid flowchart\n"
                    "- or ask natural questions; future versions of this endpoint will\n"
                    "  use LLMs to plan and execute multi-step actions."
                ),
            )
        )

    elif intent == "DESIGN_PIPELINE":
            # Use the existing generator endpoint to propose a pipeline from NL (and optional Mermaid).
        # If the NL analysis reports ambiguities (e.g. missing data source or output format)
        # we enter a clarification loop instead of immediately creating the pipeline.
        try:
            # Use any text after the first token (e.g. 'design') as the description if present
            description_text = remaining or message

            # Incorporate any clarification answers from a previous turn so that the
            # generator can see the additional requirements in plain text as well.
            clar_answers = request.clarification_answers or {}
            if clar_answers:
                extra_lines: List[str] = []
                for value in clar_answers.values():
                    if isinstance(value, str):
                        cleaned = value.strip()
                        # Tolerate accidental leading/trailing quotes so that
                        # answers like "text summary'" don't pollute the
                        # description while still keeping the user's intent.
                        if (
                            len(cleaned) >= 2
                            and cleaned[0] in {"'", '"'}
                            and cleaned[-1] in {"'", '"'}
                        ):
                            cleaned = cleaned[1:-1].strip()
                        extra_lines.append(cleaned)
                    else:
                        try:
                            extra_lines.append(json.dumps(value))
                        except Exception:
                            extra_lines.append(str(value))
                if extra_lines:
                    description_text = (
                        f"{description_text}\n\nAdditional details provided by the user:\n"
                        + "\n".join(f"- {ln}" for ln in extra_lines if ln)
                    )

            mermaid_diagram: Optional[str] = None
            lower_msg = message.lower()
            if "```mermaid" in message or "flowchart " in lower_msg or "sequencediagram" in lower_msg:
                mermaid_diagram = message

            gen_req = GeneratePipelineRequest(
                description=description_text,
                mermaid=mermaid_diagram,
                # Enable the interpreter AI pipeline so it can analyze
                # the request and propose structure before NL builder runs.
                options={"dry_run": True, "use_ai_interpreter": True},
            )
            gen_resp = await generate_routes.generate_pipeline(gen_req)
            generated = gen_resp.pipeline
            analysis = gen_resp.analysis or {}

            # Look for ambiguities reported by the NL builder.
            ambiguities: List[str] = []
            if isinstance(analysis, dict):
                amb_raw = analysis.get("ambiguities")
                if isinstance(amb_raw, list):
                    ambiguities = [str(a) for a in amb_raw if str(a).strip()]

            # If we have ambiguities and no answers yet, enter clarification mode.
            if ambiguities and not clar_answers:
                needs_clarification = True
                clarification_questions = []
                for idx, amb in enumerate(ambiguities):
                    amb_lower = amb.lower()
                    choices: Optional[List[Dict[str, Any]]] = None
                    # Only generate interactive questions for ambiguities we
                    # know how to ask about in a user-friendly way. Other
                    # ambiguities will still be listed, but not block progress.
                    if "data source" in amb_lower:
                        question_text = (
                            "What data sources should this pipeline use? "
                            "You can answer like: 'none', 'CSV file', 'database', "
                            "or 'Salesforce and external API'."
                        )
                        choices = [
                            {"value": "none", "label": "No external data"},
                            {"value": "CSV file", "label": "CSV / flat file"},
                            {"value": "database", "label": "Database"},
                            {
                                "value": "Salesforce and external API",
                                "label": "Salesforce + external API",
                            },
                        ]
                    elif "output format" in amb_lower:
                        question_text = (
                            "What output format do you expect from this pipeline? "
                            "You can reply with 'json', 'text summary', "
                            "or describe another structured format."
                        )
                        choices = [
                            {"value": "json", "label": "JSON object"},
                            {"value": "text summary", "label": "Text summary"},
                            {
                                "value": "structured fields",
                                "label": "Structured fields for another system",
                            },
                        ]
                    else:
                        # Skip generating a dedicated question for generic or
                        # low-value ambiguities (e.g. 'multiple options mentioned').
                        continue

                    clarification_questions.append(
                        ClarificationQuestion(
                            id=f"design.{idx}",
                            path=f"design.{idx}",
                            question=question_text,
                            expected_type="string",
                            required=True,
                            choices=choices,
                            schema=None,
                            examples=None,
                        )
                    )

                # Briefly explain what needs clarification and ask the first question.
                lines: List[str] = []
                # High-level reflection so the user sees what we understood
                lines.append(
                    "Here's how I understand your request so far:\n"
                    f"- You want: {generated.description or description_text}"
                )
                if generated.stages:
                    stage_kinds = sorted({s.component_type for s in generated.stages})
                    lines.append(f"- I plan to use these component types: {', '.join(stage_kinds)}")
                lines.append("")
                if clarification_questions:
                    lines.append(
                        "Before I finalize this pipeline design, I need to clarify a few points:"
                    )
                    for amb in ambiguities:
                        lines.append(f"- {amb}")
                    first_q = clarification_questions[0]
                    lines.append("")
                    lines.append(first_q.question)

                    console_messages.append(
                        ConsoleMessage(
                            role="assistant",
                            content="\n".join(lines),
                        )
                    )
            else:
                # Clarifications are either not needed or already provided: finalize and save.
                # Derive a friendlier name when the generator returns a very
                # generic one like "Unknown Pipeline".
                effective_name = (generated.name or "").strip()
                if not effective_name or effective_name.lower() == "unknown pipeline":
                    base_desc = (generated.description or description_text).strip()
                    if base_desc:
                        # Drop leading verbs like "design" / "create" / "build" for readability
                        lowered = base_desc.lower()
                        for prefix in ("design ", "create ", "build "):
                            if lowered.startswith(prefix):
                                base_desc = base_desc[len(prefix) :].lstrip()
                                break
                        effective_name = base_desc[:80]
                    else:
                        effective_name = "Generated Pipeline"

                lines: list[str] = []
                lines.append(f"Proposed pipeline: {effective_name} (v{generated.version})")
                lines.append(f"Description: {generated.description}")
                lines.append(f"Stages: {len(generated.stages)}")
                for idx, st in enumerate(generated.stages, start=1):
                    deps = st.depends_on or []
                    dep_text = f" depends on: {', '.join(deps)}" if deps else ""
                    lines.append(f"{idx}. {st.name} [{st.component_type}]{dep_text}")

                created_id: Optional[str] = None
                # Optionally persist the generated pipeline when state changes are allowed
                if not (request.options and request.options.allow_state_changes is False):
                    try:
                        pipeline_storage = storage
                        input_schema = PipelineInputSchema.model_validate(generated.input_schema)  # type: ignore[name-defined]
                        output_schema = PipelineOutputSchema()  # type: ignore[name-defined]
                        stages = [
                            PipelineStage(  # type: ignore[name-defined]
                                id=s.id,
                                name=s.name,
                                component_type=s.component_type,
                                config=s.config,
                                input_mapping={},
                                depends_on=s.depends_on,
                            )
                            for s in generated.stages
                        ]
                        create_req = PipelineCreate(
                            name=effective_name,
                            description=generated.description,
                            input_schema=input_schema,
                            output_schema=output_schema,
                            stages=stages,
                            output_stage_id=generated.output_stage_id,
                        )
                        created = pipeline_storage.create(create_req)
                        created_id = created.id
                        # Update session pipeline context
                        session_store.update_pipeline_context(
                            session_id=session_id,
                            pipeline_id=created.id,
                            name=created.name,
                            version=created.version,
                        )
                        lines.append("")
                        lines.append(f"Saved as pipeline '{created.name}' (id: {created.id}).")

                        # Expose the created pipeline as the current summary/diagram
                        # so the console can immediately show the flow.
                        pipeline_summary = ConsolePipelineSummary(
                            pipeline_id=created.id,
                            name=created.name,
                            description=created.description,
                            input_schema=created.input_schema or {},
                            output_stage_id=created.output_stage_id,
                            stages=[
                                ConsolePipelineStageSummary(
                                    id=s.id,
                                    name=s.name,
                                    component_type=s.component_type,
                                    depends_on=s.depends_on or [],
                                    changed_by_ai=True,
                                )
                                for s in (created.stages or [])
                            ],
                        )
                        flowchart = _build_mermaid_from_pipeline(created)
                        diagrams = ConsoleDiagrams(flowchart=flowchart)
                    except Exception:
                        # If saving fails, we still return the design summary
                        lines.append("")
                    lines.append(
                        "Note: Failed to save this design automatically. "
                        "You can still recreate it in Studio using the stage list above."
                    )

                # Surface a brief summary of how the AI designer worked,
                # so users can see whether the interpreter pipeline and
                # other AI pieces were involved.
                if isinstance(analysis, dict):
                    interpreter_used = analysis.get("_interpreter_used")
                    interpreter_error = analysis.get("_interpreter_error")
                    pipeline_source = analysis.get("_pipeline_source")
                    if interpreter_used is not None or pipeline_source or interpreter_error:
                        lines.append("")
                        lines.append("AI design details:")
                        if interpreter_used is not None:
                            lines.append(
                                f"- Interpreter pipeline used: {'yes' if interpreter_used else 'no'}"
                            )
                        if pipeline_source:
                            lines.append(f"- Primary candidate source: {pipeline_source}")
                        if interpreter_error:
                            lines.append(f"- Interpreter notes: {interpreter_error}")

                if not created_id:
                    lines.append("")
                    lines.append(
                        "You can open this design in the Studio builder to refine it, "
                        "or use the Mermaid-based tools to adjust the structure."
                    )

                console_messages.append(
                    ConsoleMessage(
                        role="assistant",
                        content="\n".join(lines),
                    )
            )

        except HTTPException as exc:
            errors.append(
                ConsoleError(
                    code="design_failed",
                    message=str(exc.detail),
                    source="execution",
                )
            )
            console_messages.append(
                ConsoleMessage(
                    role="assistant",
                    content=f"Failed to design a pipeline from your request: {exc.detail}",
                )
            )
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(
                ConsoleError(
                    code="design_failed",
                    message=str(exc),
                    source="execution",
                )
            )
            console_messages.append(
                ConsoleMessage(
                    role="assistant",
                    content="Failed to design a pipeline from your request. See error details for more information.",
                )
            )

    elif intent == "MODIFY_PIPELINE" and target_pipeline is not None:
        # Treat the message as a refinement request for the current pipeline.
        # We generate a new design using the existing pipeline description and
        # the user's requested changes, then update the pipeline in place.
        try:
            from flowmason_studio.api.routes.pipelines import update_pipeline  # type: ignore
            from flowmason_studio.models.api import PipelineUpdate  # type: ignore

            base_desc = target_pipeline.description or target_pipeline.name or "Existing pipeline"
            refinement_text = (
                f"{base_desc}\n\nUser refinement request:\n{message.strip()}"
            )

            # Optionally include the current pipeline structure in the description
            # so the interpreter/NL builder can see what already exists.
            try:
                from flowmason_studio.api.routes.pipelines import PipelineViewsResponse  # type: ignore # noqa: F401
                mermaid_for_context = _build_mermaid_from_pipeline(target_pipeline)
            except Exception:
                mermaid_for_context = None

            gen_req = GeneratePipelineRequest(
                description=refinement_text,
                mermaid=mermaid_for_context,
                options={"dry_run": True, "use_ai_interpreter": True},
            )
            gen_resp = await generate_routes.generate_pipeline(gen_req)
            generated = gen_resp.pipeline

            # Build updated stages and schemas for the pipeline.
            input_schema = PipelineInputSchema.model_validate(generated.input_schema)  # type: ignore[name-defined]
            output_schema = PipelineOutputSchema()  # type: ignore[name-defined]
            stages = [
                PipelineStage(  # type: ignore[name-defined]
                    id=s.id,
                    name=s.name,
                    component_type=s.component_type,
                    config=s.config,
                    input_mapping={},
                    depends_on=s.depends_on,
                )
                for s in generated.stages
            ]

            update_req = PipelineUpdate(
                description=generated.description,
                input_schema=input_schema,
                output_schema=output_schema,
                stages=stages,
                output_stage_id=generated.output_stage_id,
            )

            # Call the existing update_pipeline route function directly.
            # Note: org/auth scoping is handled inside that route via dependencies;
            # here we assume default org context.
            updated = await update_pipeline(pipeline_id=target_pipeline.id, update=update_req)  # type: ignore[arg-type]

            # Update session pipeline context for the modified pipeline
            session_store.update_pipeline_context(
                session_id=session_id,
                pipeline_id=updated.id,
                name=updated.name,
                version=updated.version,
            )

            # Build a fresh summary and diagram
            pipeline_summary = ConsolePipelineSummary(
                pipeline_id=updated.id,
                name=updated.name,
                description=updated.description,
                input_schema=updated.input_schema or {},
                output_stage_id=updated.output_stage_id,
                stages=[
                    ConsolePipelineStageSummary(
                        id=s.id,
                        name=s.name,
                        component_type=s.component_type,
                        depends_on=s.depends_on or [],
                        changed_by_ai=True,
                    )
                    for s in (updated.stages or [])
                ],
            )
            flowchart = _build_mermaid_from_pipeline(updated)
            diagrams = ConsoleDiagrams(flowchart=flowchart)

            lines: List[str] = []
            lines.append(
                f"Updated pipeline: {updated.name} (v{updated.version}) based on your refinement request."
            )
            lines.append(f"Description: {updated.description}")
            lines.append(f"Stages: {len(updated.stages)}")
            for idx, st in enumerate(updated.stages, start=1):
                deps = st.depends_on or []
                dep_text = f" depends on: {', '.join(deps)}" if deps else ""
                lines.append(
                    f"{idx}. {st.name or st.id} [{st.component_type}]{dep_text}"
                )
            console_messages.append(
                ConsoleMessage(role="assistant", content="\n".join(lines))
            )
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(
                ConsoleError(
                    code="modify_failed",
                    message=str(exc),
                    source="execution",
                )
            )
            console_messages.append(
                ConsoleMessage(
                    role="assistant",
                    content="Failed to modify the pipeline based on your request. See error details for more information.",
                )
            )

    elif intent in {"RUN_PIPELINE", "EXPLAIN_PIPELINE", "SHOW_DIAGRAMS", "VIEW_PIPELINE", "DEBUG_ERROR"}:
        if not target_pipeline:
            console_messages.append(
                ConsoleMessage(
                    role="assistant",
                    content=(
                        "I couldn't determine which pipeline you meant. "
                        "Please specify a pipeline name or id, for example: "
                        "\"run my-pipeline\" or \"explain simple-pipeline\"."
                    ),
                )
            )
        else:
            # For EXPLAIN/SHOW_DIAGRAMS/VIEW_PIPELINE we just return structure/diagrams.
            if intent in {"EXPLAIN_PIPELINE", "SHOW_DIAGRAMS", "VIEW_PIPELINE"}:
                console_messages.append(
                    ConsoleMessage(
                        role="assistant",
                        content=(
                            f"Pipeline: {target_pipeline.name} (v{target_pipeline.version})\n"
                            f"ID: {target_pipeline.id}\n\n"
                            "Here is its structure and Mermaid diagram. "
                            "Use the Studio views to inspect and edit JSON, DAG, and Mermaid in sync."
                        ),
                    )
                )
            # DEBUG_ERROR: summarize recent failed runs for this pipeline
            if intent == "DEBUG_ERROR":
                try:
                    from flowmason_studio.models.api import RunDetail  # type: ignore

                    runs, _total = run_storage.list(
                        pipeline_id=target_pipeline.id,
                        status=None,
                        limit=10,
                        offset=0,
                        org_id=None,
                    )
                    failed_runs: list[RunDetail] = []
                    for r in runs:
                        detail = run_storage.get(r.id, org_id=None)
                        if detail and (detail.status != "completed" or detail.error):
                            failed_runs.append(detail)

                    if not failed_runs:
                        console_messages.append(
                            ConsoleMessage(
                                role="assistant",
                                content=(
                                    "I could not find any recent failed runs for this pipeline. "
                                    "Try running it again and then use `debug` to analyze issues."
                                ),
                            )
                        )
                    else:
                        lines: list[str] = []
                        lines.append(
                            f"Found {len(failed_runs)} recent run(s) with issues for pipeline '{target_pipeline.name}':"
                        )
                        suggested_fixes: list[str] = []

                        for run in failed_runs:
                            lines.append(
                                f"- Run {run.id} status={run.status} "
                                f"duration={run.duration_ms or 'n/a'}ms "
                                f"error={run.error or 'none'}"
                            )
                            if run.stage_results:
                                for sid, sres in run.stage_results.items():
                                    if sres.error:
                                        msg = sres.error
                                        lines.append(f"    • Stage {sid}: {msg}")

                                        lower_msg = msg.lower()
                                        if "mapping" in lower_msg or "input mapping failed" in lower_msg:
                                            suggested_fixes.append(
                                                f"- Stage {sid}: Review input_mapping and input_schema for required fields; "
                                                "ensure JSON shapes match the component's Input model (e.g., lists vs strings)."
                                            )
                                        elif "validation" in lower_msg:
                                            suggested_fixes.append(
                                                f"- Stage {sid}: Add or tighten schema validation before this stage, "
                                                "and align input_schema with actual runtime payloads."
                                            )
                                        elif "http" in lower_msg and ("timeout" in lower_msg or "connection" in lower_msg):
                                            suggested_fixes.append(
                                                f"- Stage {sid}: Configure HTTP timeouts/retries and consider try/catch or fallback routing."
                                            )
                                        elif "llm" in lower_msg or "tokens" in lower_msg:
                                            suggested_fixes.append(
                                                f"- Stage {sid}: Adjust max_tokens/temperature and confirm provider configuration in settings."
                                            )

                        if suggested_fixes:
                            lines.append("")
                            lines.append("Suggested next steps:")
                            # Deduplicate suggestions
                            for fix in sorted(set(suggested_fixes)):
                                lines.append(fix)

                        console_messages.append(
                            ConsoleMessage(
                                role="assistant",
                                content="\n".join(lines),
                            )
                        )
                except Exception as exc:  # pragma: no cover - defensive
                    errors.append(
                        ConsoleError(
                            code="debug_failed",
                            message=str(exc),
                            source="execution",
                        )
                    )
                    console_messages.append(
                        ConsoleMessage(
                            role="assistant",
                            content="Failed to analyze recent runs for this pipeline. See error details for more information.",
                        )
                    )

            # For RUN_PIPELINE (v1): attempt a simple run, optionally via clarification.
            if intent == "RUN_PIPELINE":
                test_input: Dict[str, Any] = {}

                # If clarification answers are provided, build input directly from them
                if request.clarification_answers:
                    for key, value in request.clarification_answers.items():
                        if key.startswith("input."):
                            field_name = key[len("input.") :]
                        else:
                            field_name = key
                        test_input[field_name] = value

                    console_messages.append(
                        ConsoleMessage(
                            role="assistant",
                            content="Running pipeline with your provided answers.",
                        )
                    )
                else:
                    # Determine input: prefer pipeline.sample_input if set,
                    # otherwise attempt empty input when there are no required fields.
                    if target_pipeline.sample_input:
                        if isinstance(target_pipeline.sample_input, dict):
                            test_input = target_pipeline.sample_input  # type: ignore[assignment]
                        else:
                            # Non-dict sample_input; let executor handle it as-is
                            test_input = {"input": target_pipeline.sample_input}  # type: ignore[assignment]
                        console_messages.append(
                            ConsoleMessage(
                                role="assistant",
                                content="Running pipeline using its configured sample_input.",
                            )
                        )
                    else:
                        schema = target_pipeline.input_schema
                        required = list(schema.required) if schema and schema.required else []
                        properties = getattr(schema, "model_dump", None)
                        prop_types: Dict[str, Any] = {}
                        if callable(properties):
                            raw = schema.model_dump()  # type: ignore[call-arg]
                            prop_types = raw.get("properties") or {}

                        if required:
                            # Ask for missing required fields via clarification questions.
                            needs_clarification = True
                            for field_name in required:
                                prop = prop_types.get(field_name, {})
                                field_type = prop.get("type", "json")
                                question_text = prop.get("description") or f'Please provide a value for "{field_name}".'
                                clarification_questions.append(
                                    ClarificationQuestion(
                                        id=f"input.{field_name}",
                                        path=f"input.{field_name}",
                                        question=question_text,
                                        expected_type=field_type
                                        if field_type in {"string", "number", "boolean", "object", "array", "json"}
                                        else "json",
                                        required=True,
                                        choices=None,
                                        schema=None,
                                        examples=None,
                                    )
                                )

                            console_messages.append(
                                ConsoleMessage(
                                    role="assistant",
                                    content=(
                                        "This pipeline expects some inputs. "
                                        "I'll ask you a few questions to collect them."
                                    ),
                                )
                            )
                        else:
                            console_messages.append(
                                ConsoleMessage(
                                    role="assistant",
                                    content="Running pipeline with empty input (no required fields declared).",
                                )
                            )

                # Execute when we have either clarification answers, sample_input,
                # or no required fields.
                if not needs_clarification:
                    try:
                        # Use the same conversion path as the main execution
                        # API so that stage.config is mapped correctly into the
                        # core ComponentConfig input_mapping (especially for
                        # generator-style components that rely on prompt config).
                        from flowmason_core.executor import PipelineExecutor  # type: ignore
                        from flowmason_studio.api.routes.execution import (  # type: ignore
                            _convert_to_core_config,
                        )

                        core_config = _convert_to_core_config(target_pipeline)

                        # Build a simple lookup of stage_id -> component_type
                        type_map: Dict[str, str] = {}
                        for stage in target_pipeline.stages or []:
                            type_map[stage.id] = stage.component_type

                        executor = PipelineExecutor(registry)
                        result = await executor.execute(core_config, test_input)

                        # Map stage results into a compact console-friendly format
                        stage_results: List[ConsoleRunStageResult] = []
                        if result.stage_results:
                            for stage_id, stage_res in result.stage_results.items():
                                status = stage_res.get("status", "unknown")
                                output = stage_res.get("output")
                                error = stage_res.get("error")
                                preview = None
                                if isinstance(output, str):
                                    preview = output[:200]
                                elif output is not None:
                                    try:
                                        preview = str(output)[:200]
                                    except Exception:
                                        preview = None

                                stage_results.append(
                                    ConsoleRunStageResult(
                                        stage_id=stage_id,
                                        component_type=type_map.get(stage_id, "unknown"),
                                        status=status,
                                        duration_ms=None,
                                        output_preview=preview,
                                        error=error,
                                    )
                                )

                        final_output: Optional[Dict[str, Any]] = None
                        if isinstance(result.output, dict):
                            final_output = result.output
                        elif result.output is not None:
                            final_output = {"output": result.output}

                        run_result = ConsoleRunResult(
                            pipeline_id=target_pipeline.id,
                            run_id=None,
                            inputs_used=test_input,
                            stage_results=stage_results,
                            final_output=final_output,
                        )

                        console_messages.append(
                            ConsoleMessage(
                                role="assistant",
                                content=(
                                    "Pipeline execution completed. "
                                    "Stage outputs and final result are available in the structured response."
                                ),
                            )
                        )
                    except Exception as exc:  # pragma: no cover - defensive
                        errors.append(
                            ConsoleError(
                                code="run_failed",
                                message=str(exc),
                                source="execution",
                            )
                        )
                        console_messages.append(
                            ConsoleMessage(
                                role="assistant",
                                content="Pipeline execution failed. See error details for more information.",
                            )
                        )

    # Build single action with appropriate result kind
    if run_result is not None:
        action = ConsoleAction(
            id="act_1",
            type="RUN_PIPELINE",
            status="done",
            error_code=None,
            error_message=None,
            result=ConsoleActionResult(kind="run_result", run=run_result),
        )
    else:
        action = ConsoleAction(
            id="act_1",
            type=intent if intent != "UNKNOWN" else "NOOP",
            status="done",
            error_code=None,
            error_message=None,
            result=ConsoleActionResult(kind="noop"),
        )
    actions.append(action)

    return ConsoleResponse(
        intent=intent,
        confidence=confidence,
        needs_clarification=needs_clarification,
        clarification_questions=clarification_questions,
        actions=actions,
        pipeline_summary=pipeline_summary,
        diagrams=diagrams,
        errors=errors,
        console_messages=console_messages,
    )
