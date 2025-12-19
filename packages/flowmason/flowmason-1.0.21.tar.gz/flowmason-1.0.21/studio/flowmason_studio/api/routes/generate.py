"""
Pipeline Generation API Routes.

Provides HTTP API for AI-powered pipeline generation from natural language.
This is a convenience wrapper around the nl-builder service.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from flowmason_studio.api.routes.execution import _execute_pipeline_task  # type: ignore
from flowmason_studio.models.api import (
    PipelineDetail,
    PipelineInputSchema,
    PipelineOutputSchema,
    PipelineStage,
)
from flowmason_studio.services.nl_builder_service import get_nl_builder_service
from flowmason_studio.services import ml_pipeline_proposer
from flowmason_studio.services.storage import get_pipeline_storage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/generate", tags=["generate"])


class GeneratePipelineRequest(BaseModel):
    """Request to generate a pipeline from natural language or diagrams."""
    description: str
    mermaid: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class GeneratedStage(BaseModel):
    """A generated pipeline stage."""
    id: str
    name: str
    component_type: str
    config: Dict[str, Any]
    depends_on: List[str] = []
    rationale: Optional[str] = None


class GeneratedPipeline(BaseModel):
    """A generated pipeline definition."""
    name: str
    version: str = "1.0.0"
    description: str
    input_schema: Dict[str, Any]
    stages: List[GeneratedStage]
    output_stage_id: str
    is_fallback: bool = False


class GeneratePipelineResponse(BaseModel):
    """Response containing the generated pipeline."""
    pipeline: GeneratedPipeline
    analysis: Optional[Dict[str, Any]] = None


class PipelineFeedbackRequest(BaseModel):
    """User feedback on a generated pipeline."""

    pipeline_name: str
    rating: int  # -1 (thumbs down), 0 (neutral), 1 (thumbs up)
    comment: Optional[str] = None
    source: Optional[str] = None  # e.g. "generate_page", "builder"


def _validate_interpreter_pipeline(pipeline: Dict[str, Any]) -> tuple[List[str], List[str]]:
    """
    Basic structural validation for interpreter-proposed pipelines.

    This mirrors the core checks in NLBuilderService._validate_pipeline
    but operates on raw dictionaries returned by the interpreter.
    """
    errors: List[str] = []
    warnings: List[str] = []

    name = pipeline.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("Pipeline name is required")

    stages_raw = pipeline.get("stages")
    if not isinstance(stages_raw, list) or not stages_raw:
        errors.append("Pipeline must have at least one stage")
        return errors, warnings

    # Collect stage IDs and detect basic issues
    stage_ids: set[str] = set()
    for stage in stages_raw:
        if not isinstance(stage, dict):
            errors.append("Stage entry must be an object")
            continue

        stage_id = stage.get("id")
        if not isinstance(stage_id, str) or not stage_id.strip():
            errors.append("Stage ID is required")
        elif stage_id in stage_ids:
            errors.append(f"Duplicate stage ID: {stage_id}")
        stage_ids.add(stage_id)

        component_type = stage.get("component_type") or stage.get("component_type_id")
        if not isinstance(component_type, str) or not component_type.strip():
            errors.append(f"Stage {stage_id or '?'}: component_type is required")

    # Check that dependencies reference valid stages (no dangling edges)
    for stage in stages_raw:
        if not isinstance(stage, dict):
            continue
        stage_id = stage.get("id") or "?"
        depends_on = stage.get("depends_on") or []
        if isinstance(depends_on, list):
            for dep in depends_on:
                if dep not in stage_ids:
                    errors.append(
                        f"Stage {stage_id}: depends_on unknown stage '{dep}'"
                    )

    # Control-flow specific checks (foreach, conditional, http_request)
    for stage in stages_raw:
        if not isinstance(stage, dict):
            continue
        stage_id = stage.get("id") or "?"
        component_type = stage.get("component_type")
        config = stage.get("config") or {}

        if component_type == "foreach":
            loop_stages = config.get("loop_stages")
            if not isinstance(loop_stages, list) or not loop_stages:
                warnings.append(
                    f"Stage {stage_id}: foreach missing non-empty 'loop_stages' list"
                )
            else:
                for loop_id in loop_stages:
                    if loop_id not in stage_ids:
                        warnings.append(
                            f"Stage {stage_id}: foreach.loop_stages references unknown stage '{loop_id}'"
                        )

        if component_type == "conditional":
            true_stages = config.get("true_stages") or []
            false_stages = config.get("false_stages") or []
            if not true_stages and not false_stages:
                warnings.append(
                    f"Stage {stage_id}: conditional has no true_stages or false_stages configured"
                )
            for branch_list, label in (
                (true_stages, "true_stages"),
                (false_stages, "false_stages"),
            ):
                if isinstance(branch_list, list):
                    for branch_id in branch_list:
                        if branch_id not in stage_ids:
                            warnings.append(
                                f"Stage {stage_id}: conditional.{label} references unknown stage '{branch_id}'"
                            )

        if component_type == "http_request":
            url = config.get("url")
            method = config.get("method")
            if not isinstance(url, str) or not url.strip():
                warnings.append(
                    f"Stage {stage_id}: http_request missing 'url' in config"
                )
            if not isinstance(method, str) or not method.strip():
                warnings.append(
                    f"Stage {stage_id}: http_request missing 'method' in config"
                )

    return errors, warnings


def _with_default_stage_config(
    component_type: str,
    config: Dict[str, Any],
    description: str,
    stage_name: str,
) -> Dict[str, Any]:
    """
    Ensure minimally useful defaults for certain stage configs so that
    generated pipelines are runnable out of the box.

    Currently focuses on generator-like components where a prompt is required.
    """
    cfg = dict(config or {})

    if component_type == "generator" and "prompt" not in cfg:
        base_desc = description.strip() or "Process the input and produce a useful result."
        stage_label = stage_name or "This stage"
        cfg.setdefault(
            "prompt",
            f"{stage_label}: {base_desc}\n\n{{{{input}}}}",
        )
        cfg.setdefault("max_tokens", 1000)
        cfg.setdefault("temperature", 0.7)

    return cfg


def _interpret_mermaid_diagram(mermaid: str, description: str) -> Optional[Dict[str, Any]]:
    """
    Lightweight interpretation of a Mermaid diagram into a raw pipeline dict.

    Supports simple flowchart diagrams (flowchart TD/LR) with node and edge
    definitions. This is intentionally conservative: if parsing fails or
    yields no useful nodes, returns None so that normal NL generation can
    proceed unaffected.
    """
    try:
        lines = [ln.strip() for ln in mermaid.strip().splitlines() if ln.strip()]
        if not lines:
            return None

        # Strip ```mermaid fences if present
        if lines[0].startswith("```"):
            # Find first non-fence line
            clean: List[str] = []
            for ln in lines:
                if ln.startswith("```"):
                    continue
                clean.append(ln)
            lines = clean
            if not lines:
                return None

        # Basic check for flowchart
        if not any(ln.lower().startswith("flowchart") for ln in lines):
            # For now, only support flowchart diagrams
            return None

        node_labels: Dict[str, str] = {}
        edges: List[tuple[str, str]] = []

        def _parse_node_token(token: str) -> tuple[Optional[str], Optional[str]]:
            """
            Parse a single node token like:
            A[Label], A((Label)), A{{Label}} or just A.
            Returns (id, label).
            """
            token = token.strip()
            if "[" in token and "]" in token:
                parts = token.split("[", 1)
                node_id = parts[0].strip()
                label = parts[1].split("]", 1)[0].strip()
                return (node_id or None, label or None)
            if "(" in token and ")" in token:
                parts = token.split("(", 1)
                node_id = parts[0].strip()
                label = parts[1].rsplit(")", 1)[0].strip()
                return (node_id or None, label or None)
            if "{" in token and "}" in token:
                parts = token.split("{", 1)
                node_id = parts[0].strip()
                label = parts[1].rsplit("}", 1)[0].strip()
                return (node_id or None, label or None)
            return (token or None, None)

        for ln in lines:
            if not ln or ln.lower().startswith("flowchart"):
                continue

            # Node definition: id[label] or id((label)) or id{{label}}
            # Examples:
            #   A[Validate]
            #   IN((Input))
            #   OUT((Output))
            if "[" in ln and "]" in ln and "--" not in ln:
                try:
                    left, right = ln.split("[", 1)
                    node_id = left.strip()
                    label = right.split("]", 1)[0].strip()
                    if node_id:
                        node_labels[node_id] = label or node_id
                    continue
                except Exception:
                    pass

            # Edge definition: A --> B or A -->|label| B
            if "-->" in ln:
                try:
                    left, right = ln.split("-->", 1)
                    raw_src = left.strip()
                    # Remove optional |label| and other decorations
                    if "|" in right:
                        _, right = right.split("|", 1)
                        if "|" in right:
                            _, right = right.split("|", 1)
                    dst_token = right.strip()

                    src_id, src_label = _parse_node_token(raw_src)
                    dst_id, dst_label = _parse_node_token(dst_token)

                    # Record labels if present
                    if src_id and src_id not in node_labels and src_label:
                        node_labels[src_id] = src_label
                    if dst_id and dst_id not in node_labels and dst_label:
                        node_labels[dst_id] = dst_label

                    if src_id and dst_id:
                        edges.append((src_id, dst_id))
                    continue
                except Exception:
                    pass

        # Filter out obvious non-stage nodes (IN/OUT)
        stage_ids: set[str] = {
            nid for nid in node_labels.keys()
            if nid.upper() not in {"IN", "OUT", "START", "END"}
        }
        if not stage_ids:
            return None

        # Build depends_on from edges
        depends_on_map: Dict[str, List[str]] = {sid: [] for sid in stage_ids}
        for src, dst in edges:
            if dst in stage_ids and src in stage_ids:
                depends_on_map[dst].append(src)
            elif dst in stage_ids and src.upper() in {"IN", "START"}:
                # treat IN/START as pipeline input; no dependency recorded
                continue

        # Heuristic component_type inference from label
        def infer_component_type(label: str) -> str:
            lower = label.lower()
            if "http" in lower or "url" in lower or "request" in lower:
                return "http_request"
            if "validate" in lower or "schema" in lower:
                return "schema_validate"
            if "foreach" in lower or "for each" in lower or "loop" in lower:
                return "foreach"
            if "route" in lower or "switch" in lower or "if " in lower or "when " in lower:
                return "conditional"
            if "log" in lower or "audit" in lower:
                return "logger"
            if "email" in lower or "notify" in lower or "slack" in lower:
                return "notifier"
            # Default to LLM generator for general processing stages
            if any(word in lower for word in ["ai", "summar", "classif", "extract", "transform"]):
                return "generator"
            return "generator"

        stages: List[Dict[str, Any]] = []
        for sid in stage_ids:
            label = node_labels.get(sid, sid)
            component_type = infer_component_type(label)
            stages.append(
                {
                    "id": sid,
                    "name": label,
                    "component_type": component_type,
                    "config": {},
                    "depends_on": depends_on_map.get(sid, []),
                }
            )

        # Determine output stage: node that feeds OUT/END or a terminal node
        terminal_candidates: set[str] = set(stage_ids)
        for src, dst in edges:
            if src in terminal_candidates and dst in stage_ids:
                # src has outgoing edge to another stage, not terminal
                terminal_candidates.discard(src)

        output_stage_id: Optional[str] = None
        # Prefer node that connects to OUT/END if present
        for src, dst in edges:
            if src in stage_ids and dst.upper() in {"OUT", "END"}:
                output_stage_id = src
                break
        if not output_stage_id and terminal_candidates:
            output_stage_id = next(iter(terminal_candidates))

        pipeline = {
            "name": "Diagram-derived Pipeline",
            "version": "1.0.0",
            "description": description.strip() or "Pipeline derived from Mermaid diagram",
            "input_schema": {"type": "object", "properties": {}},
            "stages": stages,
            "output_stage_id": output_stage_id or list(stage_ids)[-1],
        }

        errors, _ = _validate_interpreter_pipeline(pipeline)
        if errors:
            logger.debug("Mermaid diagram validation errors: %s", errors)
            return None

        return pipeline
    except Exception:
        logger.debug("Failed to interpret Mermaid diagram", exc_info=True)
        return None


@router.post("/pipeline", response_model=GeneratePipelineResponse)
async def generate_pipeline(request: GeneratePipelineRequest) -> GeneratePipelineResponse:
    """
    Generate a pipeline from a natural language description.

    The AI analyzes your description and generates a complete pipeline
    with appropriate components and configurations.

    **Example:**
    ```json
    {
      "description": "Summarize a long article, then translate the summary to Spanish",
      "options": {
        "include_validation": true,
        "include_logging": true
      }
    }
    ```
    """
    # Validate primary description
    if not request.description or not request.description.strip():
        raise HTTPException(
            status_code=400,
            detail="Description is required and cannot be empty"
        )

    try:
        logger.debug(
            "Generate pipeline request: %s",
            {
                "description": request.description,
                "has_mermaid": bool(request.mermaid and request.mermaid.strip()),
                "options": request.options,
            },
        )
        # Normalize options and read toggles for advanced behavior.
        # By default we enable the AI interpreter pipeline so that all
        # designs benefit from the pipeline design assistant unless a
        # caller explicitly opts out.
        raw_options = request.options or {}
        if "use_ai_interpreter" in raw_options:
            use_ai_interpreter = bool(raw_options.get("use_ai_interpreter"))
        else:
            use_ai_interpreter = True
        dry_run = bool(raw_options.get("dry_run", False))
        base_context: Dict[str, Any] = {
            k: v for k, v in raw_options.items() if k != "use_ai_interpreter"
        }

        # Include optional Mermaid diagram in context so interpreter/LLM
        # can use it as an additional structural signal.
        mermaid_diagram = (request.mermaid or "").strip() or None
        if mermaid_diagram:
            base_context["mermaid_diagram"] = mermaid_diagram

        # ------------------------------------------------------------------
        # Step 1: Optionally run the NL interpreter pipeline to get context
        # ------------------------------------------------------------------
        interpreter_context: Optional[Dict[str, Any]] = None
        interpreter_error: Optional[str] = None
        interpreter_proposed_pipeline: Optional[Dict[str, Any]] = None
        diagram_proposed_pipeline: Optional[Dict[str, Any]] = None
        preferred_components: Optional[List[str]] = None

        # If a Mermaid diagram is provided, try to interpret it into a raw
        # pipeline candidate up front so it can be used as context and as a
        # fallback candidate later.
        if mermaid_diagram:
            diagram_proposed_pipeline = _interpret_mermaid_diagram(
                mermaid_diagram, request.description
            )

        if use_ai_interpreter:
            storage = get_pipeline_storage()
            interpreter = storage.get_by_name("nl-interpreter")

            # If not found in storage, try loading from the built-in pipeline file
            if not interpreter:
                try:
                    pipeline_path = Path("pipelines") / "nl_interpreter.pipeline.json"
                    if pipeline_path.is_file():
                        with pipeline_path.open("r", encoding="utf-8") as f:
                            pipeline_data = json.load(f)

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

                        interpreter = PipelineDetail(  # type: ignore[call-arg]
                            id=pipeline_data.get("id", "nl-interpreter"),
                            name=pipeline_data.get("name", "nl-interpreter"),
                            description=pipeline_data.get(
                                "description",
                                "Built-in NL interpreter pipeline",
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
                except Exception:
                    interpreter = None

            if interpreter:
                # Minimal inline run of the interpreter pipeline using the same
                # execution task used by the main execution API.
                from flowmason_studio.services.storage import RunStorage, get_run_storage
                from flowmason_studio.api.routes.registry import get_registry

                run_storage: RunStorage = get_run_storage()
                registry = get_registry()

                # Create a temporary run record
                run = run_storage.create(
                    pipeline_id=interpreter.id,
                    inputs={"description": request.description},
                    org_id=None,
                )

                await _execute_pipeline_task(
                    run_id=run.id,
                    pipeline_detail=interpreter,
                    inputs={"description": request.description},
                    registry=registry,
                    run_storage=run_storage,
                    breakpoints=None,
                    org_id=None,
                )

                completed = run_storage.get(run.id, org_id=None)
                if completed and completed.output:
                    # Expect shape: {"context": {...}}
                    output = completed.output
                    if isinstance(output, dict):
                        interpreter_context = output.get("context") or output
                        logger.debug("Interpreter context: %s", interpreter_context)

                        # Extract suggested components from interpreter output, if present
                        suggested = interpreter_context.get("suggested_components")
                        if isinstance(suggested, list):
                            preferred_components = [
                                c for c in suggested if isinstance(c, str) and c.strip()
                            ]

                        # Extract an optional full pipeline proposal if provided
                        proposed = interpreter_context.get("proposed_pipeline")
                        if isinstance(proposed, dict):
                            interpreter_proposed_pipeline = proposed
                else:
                    if completed:
                        interpreter_error = (
                            completed.error
                            or f"Interpreter run failed with status '{completed.status}'"
                        )
                    else:
                        interpreter_error = "Interpreter run not found in run storage"

        # ------------------------------------------------------------------
        # Step 2: Use NL builder with interpreter-derived context
        # ------------------------------------------------------------------
        service = get_nl_builder_service()

        generation_context: Dict[str, Any] = base_context
        if interpreter_context:
            # Merge interpreter context into options; interpreter wins on conflicts
            generation_context = {**generation_context, **interpreter_context}

        result = await service.generate_pipeline(
            description=request.description,
            mode="detailed",
            context=generation_context,
            preferred_components=preferred_components,
        )
        logger.debug(
            "NL builder result status=%s errors=%s warnings=%s",
            result.status,
            result.validation_errors,
            result.validation_warnings,
        )

        # ------------------------------------------------------------------
        # Step 3: Optional ML proposal and candidate selection
        # ------------------------------------------------------------------
        rules_pipeline = result.pipeline
        chosen_pipeline_source = "rules"
        ml_pipeline = None
        ml_validation_errors: List[str] = []
        ml_validation_warnings: List[str] = []
        interpreter_pipeline: Optional[Dict[str, Any]] = None
        interpreter_validation_errors: List[str] = []
        interpreter_validation_warnings: List[str] = []

        try:
            ml_context: Dict[str, Any] = {
                "description": request.description,
                "generation_context": generation_context,
                "analysis": result.analysis.model_dump() if result.analysis else None,
                "rules_pipeline": rules_pipeline.model_dump() if rules_pipeline else None,
            }
            ml_pipeline = ml_pipeline_proposer.propose_pipeline(ml_context)
        except Exception:
            logger.debug("ML pipeline proposer failed; proceeding without ML candidate", exc_info=True)
            ml_pipeline = None

        # Validate ML candidate if present
        if ml_pipeline is not None:
            try:
                ml_validation_errors, ml_validation_warnings = service._validate_pipeline(  # type: ignore[attr-defined]
                    ml_pipeline
                )
            except Exception:
                logger.debug("Failed to validate ML-proposed pipeline", exc_info=True)
                ml_pipeline = None
                ml_validation_errors = []
                ml_validation_warnings = []

        # Candidate selection: prefer ML candidate only if it validates
        # without errors and has no more warnings than the rules-based one.
        if ml_pipeline is not None and not ml_validation_errors:
            rules_errors = result.validation_errors or []
            rules_warnings = result.validation_warnings or []

            if rules_errors:
                chosen_pipeline_source = "ml"
                rules_pipeline = ml_pipeline
            else:
                if len(ml_validation_warnings) <= len(rules_warnings):
                    chosen_pipeline_source = "ml"
                    rules_pipeline = ml_pipeline

        # Validate interpreter-proposed pipeline, if any
        if interpreter_proposed_pipeline is not None:
            interpreter_validation_errors, interpreter_validation_warnings = _validate_interpreter_pipeline(  # type: ignore[arg-type]
                interpreter_proposed_pipeline
            )
            if not interpreter_validation_errors:
                interpreter_pipeline = interpreter_proposed_pipeline

        # Validate diagram-proposed pipeline, if any
        diagram_pipeline: Optional[Dict[str, Any]] = None
        diagram_validation_errors: List[str] = []
        diagram_validation_warnings: List[str] = []
        if diagram_proposed_pipeline is not None:
            diagram_validation_errors, diagram_validation_warnings = _validate_interpreter_pipeline(  # type: ignore[arg-type]
                diagram_proposed_pipeline
            )
            if not diagram_validation_errors:
                diagram_pipeline = diagram_proposed_pipeline

        # ------------------------------------------------------------------
        # Step 4: Choose between rules/ML and interpreter candidates, then
        # build the final pipeline or synthesize a fallback.
        # ------------------------------------------------------------------
        # Start with the current rules/ML choice as the best NL-based candidate.
        best_source = chosen_pipeline_source
        best_kind = "nl"
        best_nl_pipeline = rules_pipeline
        best_raw_pipeline: Optional[Dict[str, Any]] = None
        best_errors = (
            result.validation_errors or []
            if best_source == "rules"
            else ml_validation_errors
        )
        best_warnings = (
            result.validation_warnings or []
            if best_source == "rules"
            else ml_validation_warnings
        )

        # Consider interpreter-proposed pipeline as another candidate:
        # prefer it if it validates (no errors) and has no more warnings
        # than the current best candidate.
        if interpreter_pipeline is not None and not interpreter_validation_errors:
            if best_errors:
                best_source = "interpreter"
                best_kind = "raw"
                best_nl_pipeline = None
                best_raw_pipeline = interpreter_pipeline
                best_errors = interpreter_validation_errors
                best_warnings = interpreter_validation_warnings
            else:
                if len(interpreter_validation_warnings) <= len(best_warnings):
                    best_source = "interpreter"
                    best_kind = "raw"
                    best_nl_pipeline = None
                    best_raw_pipeline = interpreter_pipeline
                    best_errors = interpreter_validation_errors
                    best_warnings = interpreter_validation_warnings

        # Track whether we are returning a synthesized fallback pipeline
        pipeline_is_fallback = False

        # Use the chosen candidate if available; otherwise synthesize a simple
        # one-stage pipeline directly from the prompt so that any non-empty
        # description yields a valid pipeline.
        pipeline: GeneratedPipeline

        if best_kind == "nl" and best_nl_pipeline is not None and best_nl_pipeline.stages:
            pipeline_data = best_nl_pipeline

            # Build a mapping of NL-generated stages by id for merging.
            nl_stages_by_id: Dict[str, Any] = {s.id: s for s in pipeline_data.stages}  # type: ignore[dict-item]

            stages: List[GeneratedStage] = []

            if diagram_pipeline is not None and not diagram_validation_errors:
                # Use the diagram as a structural prior: stage ids and depends_on
                raw = diagram_pipeline
                raw_stages = raw.get("stages") or []
                for raw_stage in raw_stages:
                    if not isinstance(raw_stage, dict):
                        continue
                    stage_id = raw_stage.get("id")
                    if not isinstance(stage_id, str) or not stage_id.strip():
                        continue

                    nl_stage = nl_stages_by_id.get(stage_id)
                    raw_name = raw_stage.get("name") or stage_id
                    name = getattr(nl_stage, "name", None) or raw_name

                    raw_component_type = raw_stage.get("component_type") or raw_stage.get("component_type_id")
                    component_type = getattr(nl_stage, "component_type", None) or raw_component_type or "generator"

                    raw_config = raw_stage.get("config") or {}
                    config = getattr(nl_stage, "config", None) or raw_config
                    config = _with_default_stage_config(
                        component_type=component_type,
                        config=config,
                        description=request.description,
                        stage_name=name,
                    )

                    raw_depends_on = raw_stage.get("depends_on") or []
                    nl_depends_on = getattr(nl_stage, "depends_on", None) if nl_stage is not None else None
                    depends_on = nl_depends_on if nl_depends_on is not None and len(nl_depends_on) > 0 else raw_depends_on

                    stages.append(
                        GeneratedStage(
                            id=stage_id,
                            name=name,
                            component_type=component_type,
                            config=config,
                            depends_on=depends_on,
                            rationale=getattr(nl_stage, "generated_from", None) if nl_stage is not None else None,
                        )
                    )

                # If any NL-only stages exist that aren't in the diagram and the
                # diagram is acting as a hard structural prior, we intentionally
                # drop them rather than guessing where to attach them.
                output_stage_id = raw.get("output_stage_id")
                if not isinstance(output_stage_id, str) or not output_stage_id.strip():
                    all_stage_ids = {s.id for s in stages}
                    dependent_ids = set()
                    for s in stages:
                        dependent_ids.update(s.depends_on)
                    output_candidates = all_stage_ids - dependent_ids
                    output_stage_id = (
                        list(output_candidates)[0]
                        if output_candidates
                        else (stages[-1].id if stages else "output")
                    )

                input_schema = pipeline_data.input_schema or {"type": "object", "properties": {}}  # type: ignore[assignment]
                pipeline = GeneratedPipeline(
                    name=pipeline_data.name,
                    version=getattr(pipeline_data, "version", "1.0.0"),
                    description=pipeline_data.description,
                    input_schema=input_schema,
                    stages=stages,
                    output_stage_id=output_stage_id,
                    is_fallback=False,
                )
            else:
                # No diagram: use the NL pipeline as-is.
                stages = []
                for s in pipeline_data.stages:
                    cfg = s.config if hasattr(s, "config") else {}
                    cfg = _with_default_stage_config(
                        component_type=s.component_type,
                        config=cfg,
                        description=pipeline_data.description,
                        stage_name=s.name,
                    )
                    stages.append(
                        GeneratedStage(
                            id=s.id,
                            name=s.name,
                            component_type=s.component_type,
                            config=cfg,
                            depends_on=s.depends_on if hasattr(s, "depends_on") else [],
                            rationale=getattr(s, "generated_from", None),
                        )
                    )

                # Determine output_stage_id - find stages that no other stage depends on
                all_stage_ids = {s.id for s in stages}
                dependent_ids = set()
                for s in stages:
                    dependent_ids.update(s.depends_on)
                output_candidates = all_stage_ids - dependent_ids
                output_stage_id = (
                    list(output_candidates)[0]
                    if output_candidates
                    else (stages[-1].id if stages else "output")
                )
                pipeline = GeneratedPipeline(
                    name=pipeline_data.name,
                    version=getattr(pipeline_data, "version", "1.0.0"),
                    description=pipeline_data.description,
                    input_schema=pipeline_data.input_schema
                    or {"type": "object", "properties": {}},
                    stages=stages,
                    output_stage_id=output_stage_id,
                    is_fallback=False,
                )
        elif best_kind == "raw" and best_raw_pipeline is not None:
            raw = best_raw_pipeline
            raw_stages = raw.get("stages") or []
            stages: List[GeneratedStage] = []
            for s in raw_stages:
                if not isinstance(s, dict):
                    continue
                stage_id = s.get("id")
                if not isinstance(stage_id, str) or not stage_id.strip():
                    continue
                comp_type = s.get("component_type") or s.get("component_type_id") or ""
                cfg = s.get("config") or {}
                cfg = _with_default_stage_config(
                    component_type=comp_type,
                    config=cfg,
                    description=raw.get("description") or request.description,
                    stage_name=s.get("name") or stage_id,
                )
                stages.append(
                    GeneratedStage(
                        id=stage_id,
                        name=s.get("name") or stage_id,
                        component_type=comp_type,
                        config=cfg,
                        depends_on=s.get("depends_on") or [],
                        rationale=None,
                    )
                )

            # Determine output_stage_id from raw, or infer
            output_stage_id = raw.get("output_stage_id")
            if not isinstance(output_stage_id, str) or not output_stage_id.strip():
                all_stage_ids = {s.id for s in stages}
                dependent_ids = set()
                for s in stages:
                    dependent_ids.update(s.depends_on)
                output_candidates = all_stage_ids - dependent_ids
                output_stage_id = (
                    list(output_candidates)[0]
                    if output_candidates
                    else (stages[-1].id if stages else "output")
                )

            input_schema = raw.get("input_schema") or {"type": "object", "properties": {}}
            pipeline = GeneratedPipeline(
                name=raw.get("name") or "Interpreter Proposed Pipeline",
                version=raw.get("version") or "1.0.0",
                description=raw.get("description") or request.description.strip(),
                input_schema=input_schema,
                stages=stages,
                output_stage_id=output_stage_id,
                is_fallback=False,
            )
        else:
            # Synthesized fallback pipeline:
            # Prefer a valid diagram-derived pipeline if available,
            # otherwise fall back to a simple one-stage generator.
            diagram_used = False
            if diagram_pipeline is not None and not diagram_validation_errors:
                raw = diagram_pipeline
                raw_stages = raw.get("stages") or []
                stages = []
                for s in raw_stages:
                    if not isinstance(s, dict):
                        continue
                    stage_id = s.get("id")
                    if not isinstance(stage_id, str) or not stage_id.strip():
                        continue
                    comp_type = s.get("component_type") or s.get("component_type_id") or ""
                    cfg = s.get("config") or {}
                    cfg = _with_default_stage_config(
                        component_type=comp_type,
                        config=cfg,
                        description=raw.get("description") or request.description,
                        stage_name=s.get("name") or stage_id,
                    )
                    stages.append(
                        GeneratedStage(
                            id=stage_id,
                            name=s.get("name") or stage_id,
                            component_type=comp_type,
                            config=cfg,
                            depends_on=s.get("depends_on") or [],
                            rationale=None,
                        )
                    )

                all_stage_ids = {s.id for s in stages}
                dependent_ids = set()
                for s in stages:
                    dependent_ids.update(s.depends_on)
                output_candidates = all_stage_ids - dependent_ids
                output_stage_id = (
                    list(output_candidates)[0]
                    if output_candidates
                    else (stages[-1].id if stages else "output")
                )

                input_schema = raw.get("input_schema") or {"type": "object", "properties": {}}
                pipeline = GeneratedPipeline(
                    name=raw.get("name") or "Diagram-derived Pipeline",
                    version=raw.get("version") or "1.0.0",
                    description=raw.get("description") or request.description.strip(),
                    input_schema=input_schema,
                    stages=stages,
                    output_stage_id=output_stage_id,
                    is_fallback=False,
                )
                diagram_used = True

            if not diagram_used:
                prompt = request.description.strip()
                stages = [
                    GeneratedStage(
                        id="generator_1",
                        name="Generate content",
                        component_type="generator",
                        config={
                            "prompt": prompt,
                            "max_tokens": 1000,
                            "temperature": 0.7,
                        },
                        depends_on=[],
                    )
                ]
                pipeline_is_fallback = True
                pipeline = GeneratedPipeline(
                    name="Generated Pipeline (fallback)",
                    version="1.0.0",
                    description=prompt,
                    input_schema={
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": "string",
                                "description": "Input text to process",
                            }
                        },
                        "required": ["input"],
                    },
                    stages=stages,
                    output_stage_id="generator_1",
                    is_fallback=True,
                )

        # Log a compact training signal record for future ML/analysis
        try:
            log_record = {
                "description": request.description,
                "options": request.options or {},
                "use_ai_interpreter": use_ai_interpreter,
                "interpreter_context": interpreter_context or {},
                "interpreter_error": interpreter_error,
                "preferred_components": preferred_components or [],
                "result_status": getattr(result.status, "value", str(result.status)),
                "validation_errors": result.validation_errors,
                "validation_warnings": result.validation_warnings,
                "error": result.error,
                "pipeline_name": pipeline.name,
                "pipeline_stage_count": len(pipeline.stages),
                "pipeline_stage_types": [s.component_type for s in pipeline.stages],
                "candidate_pipelines": {
                    "rules": {
                        "has_pipeline": result.pipeline is not None,
                        "stage_count": len(result.pipeline.stages) if result.pipeline else 0,
                        "validation_errors": result.validation_errors,
                        "validation_warnings": result.validation_warnings,
                    },
                    "ml": {
                        "has_pipeline": ml_pipeline is not None,
                        "validation_errors": ml_validation_errors,
                        "validation_warnings": ml_validation_warnings,
                    },
                "interpreter": {
                    "has_pipeline": interpreter_pipeline is not None,
                    "stage_count": len(interpreter_pipeline.get("stages") or []) if interpreter_pipeline else 0,
                    "validation_errors": interpreter_validation_errors,
                    "validation_warnings": interpreter_validation_warnings,
                },
                "diagram": {
                    "has_pipeline": diagram_pipeline is not None,
                    "stage_count": len(diagram_pipeline.get("stages") or []) if diagram_pipeline else 0,  # type: ignore[union-attr]
                    "validation_errors": diagram_validation_errors,
                    "validation_warnings": diagram_validation_warnings,
                },
            },
                "chosen_pipeline_source": best_source,
                "is_fallback_pipeline": pipeline_is_fallback,
            }
            logger.info("PIPEGEN_TRAINING %s", json.dumps(log_record, default=str))
        except Exception:
            # Never fail the request due to logging issues
            logger.debug("Failed to log PIPEGEN_TRAINING record", exc_info=True)

        # Prepare analysis payload with additional diagnostics to surface
        # interpreter/generator issues to the frontend.
        analysis_payload: Optional[Dict[str, Any]] = None
        if result.analysis:
            analysis_payload = result.analysis.model_dump()
        else:
            analysis_payload = {}

        # Optional dry-run style summary of the generated pipeline without
        # executing it or calling any external services.
        dry_run_summary: Optional[Dict[str, Any]] = None
        if dry_run and pipeline.stages:
            uses_llm = any(
                s.component_type
                in {"generator", "critic", "improver", "synthesizer", "selector"}
                for s in pipeline.stages
            )
            uses_external_io = any(s.component_type == "http_request" for s in pipeline.stages)
            stage_count = len(pipeline.stages)
            if stage_count <= 3:
                complexity = "simple"
            elif stage_count <= 7:
                complexity = "moderate"
            else:
                complexity = "complex"

            dry_run_summary = {
                "stage_count": stage_count,
                "uses_llm": uses_llm,
                "uses_external_io": uses_external_io,
                "estimated_complexity": complexity,
            }

        analysis_payload.update(
            {
                "_generation_status": getattr(result.status, "value", str(result.status)),
                "_generation_error": result.error,
                "_validation_errors": result.validation_errors,
                "_validation_warnings": result.validation_warnings,
                "_interpreter_used": use_ai_interpreter,
                "_interpreter_error": interpreter_error,
                "_pipeline_source": best_source,
                "_is_fallback_pipeline": pipeline_is_fallback,
                "_has_mermaid": bool(mermaid_diagram),
                "_diagram_validation_errors": diagram_validation_errors,
                "_diagram_validation_warnings": diagram_validation_warnings,
                "_dry_run_summary": dry_run_summary,
            }
        )

        return GeneratePipelineResponse(
            pipeline=pipeline,
            analysis=analysis_payload or None,
        )

    except HTTPException:
        # Propagate HTTPExceptions (e.g., validation errors) unchanged
        raise
    except Exception as e:
        logger.exception("Failed to generate pipeline: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate pipeline: {str(e)}"
        )


@router.post("/pipeline/feedback")
async def pipeline_feedback(request: PipelineFeedbackRequest) -> Dict[str, Any]:
    """
    Record user feedback about a generated pipeline.

    Feedback is logged for future training/analysis but not persisted
    to a database at this stage.
    """
    try:
        record = {
            "pipeline_name": request.pipeline_name,
            "rating": request.rating,
            "comment": request.comment,
            "source": request.source,
        }
        logger.info("PIPEGEN_FEEDBACK %s", json.dumps(record, default=str))
    except Exception:
        logger.debug("Failed to log PIPEGEN_FEEDBACK record", exc_info=True)

    return {"ok": True}
