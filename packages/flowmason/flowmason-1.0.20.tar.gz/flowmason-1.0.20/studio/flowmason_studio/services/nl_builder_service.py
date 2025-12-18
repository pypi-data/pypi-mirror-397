"""
Natural Language Pipeline Builder Service.

Uses LLM to analyze natural language descriptions and generate complete pipelines.
"""

import json
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flowmason_studio.models.nl_builder import (
    ComponentMatch,
    ComponentSuggestion,
    GeneratedPipeline,
    GenerationAnalysis,
    GenerationMode,
    GenerationResult,
    GenerationStatus,
    RefinementResult,
    StageDefinition,
)


# Default component catalog with descriptions for matching.
# This is used as a fallback when the dynamic registry-driven
# catalog is not available (e.g. in limited environments).
DEFAULT_COMPONENT_CATALOG: Dict[str, Dict[str, Any]] = {
    "generator": {
        "name": "Generator",
        "category": "ai",
        "description": "Generate text content using LLM",
        "use_cases": ["summarize", "write", "create", "generate", "compose", "draft"],
        "requires_llm": True,
    },
    "critic": {
        "name": "Critic",
        "category": "ai",
        "description": "Evaluate and critique content using LLM",
        "use_cases": ["review", "evaluate", "validate", "check", "assess", "grade"],
        "requires_llm": True,
    },
    "improver": {
        "name": "Improver",
        "category": "ai",
        "description": "Improve content iteratively using LLM",
        "use_cases": ["improve", "enhance", "refine", "polish", "optimize"],
        "requires_llm": True,
    },
    "synthesizer": {
        "name": "Synthesizer",
        "category": "ai",
        "description": "Combine multiple inputs into a coherent output",
        "use_cases": ["combine", "merge", "synthesize", "aggregate", "unify"],
        "requires_llm": True,
    },
    "selector": {
        "name": "Selector",
        "category": "ai",
        "description": "Select best option from multiple choices using LLM",
        "use_cases": ["select", "choose", "pick", "rank", "best"],
        "requires_llm": True,
    },
    "filter": {
        "name": "Filter",
        "category": "data",
        "description": "Filter items based on conditions",
        "use_cases": ["filter", "exclude", "include", "remove", "keep"],
        "requires_llm": False,
    },
    "json_transform": {
        "name": "JSON Transform",
        "category": "data",
        "description": "Transform and restructure JSON data",
        "use_cases": ["transform", "convert", "format", "restructure", "map"],
        "requires_llm": False,
    },
    "http_request": {
        "name": "HTTP Request",
        "category": "integration",
        "description": "Make HTTP API calls",
        "use_cases": ["api", "http", "fetch", "request", "call", "webhook"],
        "requires_llm": False,
    },
    "loop": {
        "name": "Loop",
        "category": "control",
        "description": "Iterate over items and process each",
        "use_cases": ["loop", "iterate", "each", "batch", "foreach", "process each"],
        "requires_llm": False,
    },
    "conditional": {
        "name": "Conditional",
        "category": "control",
        "description": "Branch execution based on conditions",
        "use_cases": ["if", "condition", "branch", "switch", "when"],
        "requires_llm": False,
    },
    "variable_set": {
        "name": "Variable Set",
        "category": "utility",
        "description": "Store values in pipeline variables",
        "use_cases": ["store", "save", "set", "variable", "remember"],
        "requires_llm": False,
    },
    "schema_validate": {
        "name": "Schema Validate",
        "category": "utility",
        "description": "Validate data against a JSON schema",
        "use_cases": ["validate", "schema", "check format", "verify structure"],
        "requires_llm": False,
    },
    "logger": {
        "name": "Logger",
        "category": "utility",
        "description": "Log messages and data",
        "use_cases": ["log", "debug", "trace", "print", "output"],
        "requires_llm": False,
    },
}


_COMPONENT_CATALOG_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def _build_catalog_from_registry() -> Dict[str, Dict[str, Any]]:
    """
    Build a component catalog from the live ComponentRegistry.

    This uses the Studio registry as the source of truth for
    available components and overlays any default metadata
    defined in DEFAULT_COMPONENT_CATALOG.
    """
    try:
        # Import lazily to avoid hard dependency at import time
        from flowmason_studio.api.routes.registry import get_registry  # type: ignore

        registry = get_registry()
        components = registry.list_components()
    except Exception:
        # Registry not available or not initialized
        return {}

    catalog: Dict[str, Dict[str, Any]] = {}

    for comp in components:
        comp_type = comp.component_type
        base = DEFAULT_COMPONENT_CATALOG.get(comp_type, {})

        # Derive a simple category; prefer existing catalog category
        category = base.get("category") or (comp.category or "unknown")

        catalog[comp_type] = {
            "name": base.get("name") or comp_type,
            "category": category,
            "description": base.get("description") or (comp.description or ""),
            "use_cases": base.get("use_cases", []),
            "requires_llm": getattr(comp, "requires_llm", base.get("requires_llm", False)),
        }

    # Include any default entries that weren't present in the registry
    for comp_type, info in DEFAULT_COMPONENT_CATALOG.items():
        if comp_type not in catalog:
            catalog[comp_type] = info

    return catalog


def get_component_catalog() -> Dict[str, Dict[str, Any]]:
    """
    Get the effective component catalog.

    Prefers the registry-derived catalog when available, falling
    back to DEFAULT_COMPONENT_CATALOG when the registry cannot be
    accessed (e.g. in tests or limited environments).
    """
    global _COMPONENT_CATALOG_CACHE
    if _COMPONENT_CATALOG_CACHE is not None:
        return _COMPONENT_CATALOG_CACHE

    dynamic_catalog = _build_catalog_from_registry()
    if dynamic_catalog:
        _COMPONENT_CATALOG_CACHE = dynamic_catalog
    else:
        _COMPONENT_CATALOG_CACHE = DEFAULT_COMPONENT_CATALOG

    return _COMPONENT_CATALOG_CACHE


class NLBuilderService:
    """Service for generating pipelines from natural language."""

    def __init__(self):
        """Initialize the service."""
        self._generations: Dict[str, GenerationResult] = {}

    async def generate_pipeline(
        self,
        description: str,
        mode: GenerationMode = GenerationMode.DETAILED,
        context: Optional[Dict[str, Any]] = None,
        examples: Optional[List[Dict[str, Any]]] = None,
        preferred_components: Optional[List[str]] = None,
        avoid_components: Optional[List[str]] = None,
    ) -> GenerationResult:
        """Generate a pipeline from a natural language description."""
        generation_id = str(uuid.uuid4())
        started_at = datetime.utcnow()

        result = GenerationResult(
            id=generation_id,
            status=GenerationStatus.ANALYZING,
            started_at=started_at.isoformat(),
        )
        self._generations[generation_id] = result

        try:
            # Step 1: Analyze the request
            result.status = GenerationStatus.ANALYZING
            analysis = await self._analyze_request(description)

            # Enrich/override analysis with any structured context provided
            # (e.g. from the nl-interpreter core pipeline).
            if context:
                self._merge_context_into_analysis(analysis, context)
            result.analysis = analysis

            # Step 2: Match components
            result.status = GenerationStatus.GENERATING
            suggestions = await self._suggest_components(
                analysis,
                preferred=preferred_components,
                avoid=avoid_components,
            )
            result.suggestions = suggestions

            # Step 3: Generate pipeline
            pipeline = await self._generate_pipeline_structure(
                description=description,
                analysis=analysis,
                suggestions=suggestions,
                mode=mode,
                examples=examples,
            )

            # Step 4: Validate
            result.status = GenerationStatus.VALIDATING
            errors, warnings = self._validate_pipeline(pipeline)
            result.validation_errors = errors
            result.validation_warnings = warnings

            if errors:
                result.status = GenerationStatus.FAILED
                result.error = f"Validation failed: {errors[0]}"
            else:
                result.status = GenerationStatus.COMPLETED
                result.pipeline = pipeline

        except Exception as e:
            result.status = GenerationStatus.FAILED
            result.error = str(e)

        completed_at = datetime.utcnow()
        result.completed_at = completed_at.isoformat()
        result.duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        self._generations[generation_id] = result
        return result

    async def analyze_request(self, description: str) -> GenerationAnalysis:
        """Analyze a natural language request without generating a pipeline."""
        return await self._analyze_request(description)

    async def find_components(
        self,
        task: str,
        limit: int = 5,
    ) -> List[ComponentMatch]:
        """Find components that match a task description."""
        task_lower = task.lower()
        matches: List[Tuple[str, float, str]] = []

        catalog = get_component_catalog()

        for comp_type, comp_info in catalog.items():
            score = 0.0
            reasons: List[str] = []

            # Check use cases
            for use_case in comp_info["use_cases"]:
                if use_case in task_lower:
                    score += 0.3
                    reasons.append(f"matches use case '{use_case}'")

            # Check description words
            desc_words = comp_info["description"].lower().split()
            for word in desc_words:
                if len(word) > 3 and word in task_lower:
                    score += 0.1
                    reasons.append(f"contains '{word}'")

            # Check name
            if comp_info["name"].lower() in task_lower:
                score += 0.4
                reasons.append("name match")

            if score > 0:
                matches.append((comp_type, min(score, 1.0), ", ".join(reasons[:3])))

        # Sort by score and limit
        matches.sort(key=lambda x: x[1], reverse=True)
        matches = matches[:limit]

        return [
            ComponentMatch(
                component_type=comp_type,
                name=catalog[comp_type]["name"],
                description=catalog[comp_type]["description"],
                match_score=score,
                match_reason=reason,
            )
            for comp_type, score, reason in matches
        ]

    async def refine_pipeline(
        self,
        generation_id: str,
        feedback: str,
        modifications: Optional[Dict[str, Any]] = None,
    ) -> RefinementResult:
        """Refine a previously generated pipeline based on feedback."""
        original = self._generations.get(generation_id)
        if not original or not original.pipeline:
            raise ValueError(f"Generation {generation_id} not found or incomplete")

        # Create a new generation based on refinement
        refined_description = (
            f"{original.pipeline.description}\n\nRefinement: {feedback}"
        )

        new_result = await self.generate_pipeline(
            description=refined_description,
            mode=GenerationMode.DETAILED,
        )

        changes: List[str] = []
        if new_result.pipeline:
            # Compare pipelines to identify changes
            orig_stages = {s.id for s in original.pipeline.stages}
            new_stages = {s.id for s in new_result.pipeline.stages}

            added = new_stages - orig_stages
            removed = orig_stages - new_stages

            if added:
                changes.append(f"Added stages: {', '.join(added)}")
            if removed:
                changes.append(f"Removed stages: {', '.join(removed)}")
            if not added and not removed:
                changes.append("Modified stage configurations")

        return RefinementResult(
            original_id=generation_id,
            refined_id=new_result.id,
            changes_made=changes,
            pipeline=new_result.pipeline or original.pipeline,
        )

    def get_generation(self, generation_id: str) -> Optional[GenerationResult]:
        """Get a generation result by ID."""
        return self._generations.get(generation_id)

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _merge_context_into_analysis(
        self,
        analysis: GenerationAnalysis,
        context: Dict[str, Any],
    ) -> None:
        """Merge structured context (e.g. from interpreter pipeline) into analysis."""
        # Context may be nested under a top-level 'context' key
        ctx = context.get("context") if isinstance(context.get("context"), dict) else context

        # Intent override
        ctx_intent = ctx.get("intent")
        if isinstance(ctx_intent, str) and ctx_intent.strip():
            # Normalize to the same style used elsewhere (e.g. 'generation', 'summarization')
            analysis.intent = ctx_intent.strip().lower().replace(" ", "_")

        # Helper to merge list-like fields
        def _merge_list_field(field_name: str) -> None:
            existing = getattr(analysis, field_name, [])
            ctx_values = ctx.get(field_name)
            if isinstance(ctx_values, list):
                for v in ctx_values:
                    if isinstance(v, str):
                        v_norm = v.strip()
                        if v_norm and v_norm not in existing:
                            existing.append(v_norm)
                setattr(analysis, field_name, existing)

        for field in ["actions", "data_sources", "outputs", "constraints", "ambiguities", "suggested_patterns"]:
            _merge_list_field(field)

    async def _analyze_request(self, description: str) -> GenerationAnalysis:
        """Analyze the natural language request to extract intent and entities."""
        desc_lower = description.lower()

        # Extract intent
        intent = "unknown"
        if any(w in desc_lower for w in ["summarize", "summary"]):
            intent = "summarization"
        elif any(w in desc_lower for w in ["translate", "translation"]):
            intent = "translation"
        elif any(w in desc_lower for w in ["classify", "categorize"]):
            intent = "classification"
        elif any(w in desc_lower for w in ["extract", "parse"]):
            intent = "extraction"
        elif any(w in desc_lower for w in ["generate", "create", "write"]):
            intent = "generation"
        elif any(w in desc_lower for w in ["transform", "convert"]):
            intent = "transformation"
        elif any(w in desc_lower for w in ["validate", "check", "verify"]):
            intent = "validation"
        elif any(w in desc_lower for w in ["analyze", "evaluate"]):
            intent = "analysis"

        # Extract data sources
        data_sources: List[str] = []
        if "api" in desc_lower or "http" in desc_lower:
            data_sources.append("external_api")
        if "file" in desc_lower:
            data_sources.append("file")
        if "database" in desc_lower or "db" in desc_lower:
            data_sources.append("database")
        if "user input" in desc_lower or "input" in desc_lower:
            data_sources.append("user_input")

        # Extract actions
        actions: List[str] = []
        action_patterns = [
            (r"summarize\s+(\w+)", "summarize"),
            (r"extract\s+(\w+)", "extract"),
            (r"filter\s+(\w+)", "filter"),
            (r"transform\s+(\w+)", "transform"),
            (r"validate\s+(\w+)", "validate"),
            (r"generate\s+(\w+)", "generate"),
            (r"send\s+(\w+)", "send"),
            (r"call\s+(\w+)", "call"),
        ]
        for pattern, action in action_patterns:
            if re.search(pattern, desc_lower):
                actions.append(action)

        # Extract entities (quoted strings, capitalized words)
        entities: List[str] = []
        quoted = re.findall(r'"([^"]+)"', description)
        entities.extend(quoted)

        # Find capitalized phrases
        caps = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', description)
        entities.extend([c for c in caps if c not in ["I", "A"]])

        # Identify outputs
        outputs: List[str] = []
        if "json" in desc_lower:
            outputs.append("json")
        if "text" in desc_lower or "string" in desc_lower:
            outputs.append("text")
        if "email" in desc_lower:
            outputs.append("email")
        if "report" in desc_lower:
            outputs.append("report")

        # Identify constraints
        constraints: List[str] = []
        if "must" in desc_lower:
            must_match = re.search(r"must\s+([^.]+)", desc_lower)
            if must_match:
                constraints.append(must_match.group(1).strip())
        if "should" in desc_lower:
            should_match = re.search(r"should\s+([^.]+)", desc_lower)
            if should_match:
                constraints.append(should_match.group(1).strip())

        # Identify ambiguities
        ambiguities: List[str] = []
        if not data_sources:
            ambiguities.append("Data source not specified")
        if not outputs:
            ambiguities.append("Output format not specified")
        if "or" in desc_lower:
            ambiguities.append("Multiple options mentioned - clarification may be needed")

        return GenerationAnalysis(
            intent=intent,
            entities=list(set(entities))[:10],
            actions=list(set(actions)),
            data_sources=data_sources,
            outputs=outputs,
            constraints=constraints,
            ambiguities=ambiguities,
        )

    async def _suggest_components(
        self,
        analysis: GenerationAnalysis,
        preferred: Optional[List[str]] = None,
        avoid: Optional[List[str]] = None,
    ) -> List[ComponentSuggestion]:
        """Suggest components based on the analysis."""
        suggestions: List[ComponentSuggestion] = []
        avoid_set = set(avoid or [])
        catalog = get_component_catalog()

        # Map intents to components
        intent_components = {
            "summarization": [("generator", "Generate summary from input")],
            "translation": [("generator", "Translate content")],
            "classification": [("generator", "Classify input into categories")],
            "extraction": [("json_transform", "Extract and structure data")],
            "generation": [("generator", "Generate content based on requirements")],
            "transformation": [("json_transform", "Transform data structure")],
            "validation": [
                ("schema_validate", "Validate data structure"),
                ("critic", "Evaluate content quality"),
            ],
            "analysis": [("critic", "Analyze and evaluate content")],
        }

        # Add components based on intent
        if analysis.intent in intent_components:
            for comp_type, purpose in intent_components[analysis.intent]:
                if comp_type not in avoid_set:
                    suggestions.append(ComponentSuggestion(
                        component_type=comp_type,
                        name=catalog.get(comp_type, {}).get("name", comp_type),
                        purpose=purpose,
                        rationale=f"Matches intent: {analysis.intent}",
                        confidence=0.9,
                    ))

        # Add components based on actions
        action_components = {
            "filter": ("filter", "Filter items based on criteria"),
            "transform": ("json_transform", "Transform data format"),
            "validate": ("schema_validate", "Validate data structure"),
            "send": ("http_request", "Send data to external service"),
            "call": ("http_request", "Call external API"),
        }

        for action in analysis.actions:
            if action in action_components:
                comp_type, purpose = action_components[action]
                if comp_type not in avoid_set:
                    # Don't duplicate
                    if not any(s.component_type == comp_type for s in suggestions):
                        info = catalog.get(comp_type, {})
                        suggestions.append(ComponentSuggestion(
                            component_type=comp_type,
                            name=info.get("name", comp_type),
                            purpose=purpose,
                            rationale=f"Required for action: {action}",
                            confidence=0.85,
                        ))

        # Add data source components
        if "external_api" in analysis.data_sources:
            if "http_request" not in avoid_set:
                if not any(s.component_type == "http_request" for s in suggestions):
                    suggestions.insert(0, ComponentSuggestion(
                        component_type="http_request",
                        name=catalog.get("http_request", {}).get("name", "HTTP Request"),
                        purpose="Fetch data from external API",
                        rationale="Required for external data source",
                        confidence=0.95,
                    ))

        # Add preferred components if not already present
        if preferred:
            for comp_type in preferred:
                if not any(s.component_type == comp_type for s in suggestions):
                    info = catalog.get(comp_type, {})
                    suggestions.append(ComponentSuggestion(
                        component_type=comp_type,
                        name=info.get("name", comp_type),
                        purpose="User preferred component",
                        rationale="Explicitly requested by user",
                        confidence=0.8,
                    ))

        # Fallback: ensure at least one stage is suggested
        if not suggestions:
            # Use a generic generator stage so that even vague
            # descriptions produce a simple, valid pipeline.
            info = catalog.get("generator", {})
            suggestions.append(ComponentSuggestion(
                component_type="generator",
                name=info.get("name", "Generator"),
                purpose="Generate content based on the input",
                rationale="Fallback for generic or unclear requests",
                confidence=0.5,
            ))

        return suggestions

    async def _generate_pipeline_structure(
        self,
        description: str,
        analysis: GenerationAnalysis,
        suggestions: List[ComponentSuggestion],
        mode: GenerationMode,
        examples: Optional[List[Dict[str, Any]]] = None,
    ) -> GeneratedPipeline:
        """Generate the full pipeline structure."""
        # Special patterns
        desc_lower = description.lower()
        patterns = {p.lower() for p in getattr(analysis, "suggested_patterns", [])}

        # Pattern: conditional / routing
        if (
            "conditional" in patterns
            or "routing" in patterns
            or "route" in patterns
            or " if " in f" {desc_lower} "
            or " when " in f" {desc_lower} "
            or " otherwise " in f" {desc_lower} "
            or "depending on" in desc_lower
            or "route to" in desc_lower
        ):
            return self._generate_conditional_pipeline(description, analysis)

        # Pattern: validation + transform
        if (
            "validation+transform" in patterns
            or "validation_and_transform" in patterns
            or (
                "validate" in desc_lower
                and (
                    "transform" in desc_lower
                    or "normalize" in desc_lower
                    or "clean" in desc_lower
                )
            )
        ):
            return self._generate_validation_transform_pipeline(description, analysis)

        # Pattern: http ingest + send
        if (
            "http_ingest+send" in patterns
            or "http_ingest_and_send" in patterns
            or (
                ("http" in desc_lower or "api" in desc_lower or "endpoint" in desc_lower or "url" in desc_lower)
                and any(w in desc_lower for w in ["send", "post", "notify", "webhook"])
            )
        ):
            return self._generate_http_ingest_pipeline(description, analysis)

        # Pattern: foreach/loop over items
        if (
            "foreach" in patterns
            or "foreach" in desc_lower
            or "for each" in desc_lower
            or "for every" in desc_lower
            or "each item" in desc_lower
            or "each record" in desc_lower
            or "foreach" in analysis.actions
        ):
            return self._generate_foreach_pipeline(description, analysis)

        generation_id = str(uuid.uuid4())

        # Generate stages from suggestions
        stages: List[StageDefinition] = []
        prev_stage_id: Optional[str] = None

        for i, suggestion in enumerate(suggestions):
            stage_id = f"{suggestion.component_type}_{i + 1}"

            # Generate config based on component type
            config = self._generate_stage_config(
                suggestion.component_type,
                suggestion.purpose,
                prev_stage_id,
                description,
                mode,
            )

            depends_on = [prev_stage_id] if prev_stage_id else []

            stages.append(StageDefinition(
                id=stage_id,
                name=suggestion.purpose[:50],
                component_type=suggestion.component_type,
                config=config,
                depends_on=depends_on,
                description=suggestion.purpose,
                generated_from=suggestion.rationale,
            ))

            prev_stage_id = stage_id

        # Generate pipeline name
        name_words = analysis.intent.replace("_", " ").title()
        pipeline_name = f"{name_words} Pipeline"

        # Generate input schema based on analysis
        input_schema = self._generate_input_schema(analysis, description)

        return GeneratedPipeline(
            name=pipeline_name,
            description=description[:500],
            version="1.0.0",
            stages=stages,
            input_schema=input_schema,
            generation_id=generation_id,
            generated_at=datetime.utcnow().isoformat(),
            original_request=description,
        )

    def _generate_foreach_pipeline(
        self,
        description: str,
        analysis: GenerationAnalysis,
    ) -> GeneratedPipeline:
        """
        Generate a pipeline that iterates over a list of items and
        applies the same analysis/questions to each, collecting the
        results into a structured list.
        """
        generation_id = str(uuid.uuid4())

        # Stages:
        # 1) foreach_items: foreach control-flow over input.items
        # 2) qa_each: generator that processes each item (within loop)
        # 3) aggregate_results: json_transform to shape results

        foreach_stage = StageDefinition(
            id="foreach_items",
            name="Loop over items",
            component_type="foreach",
            config={
                "items": "{{input.items}}",
                "loop_stages": ["qa_each"],
                "item_variable": "item",
                "index_variable": "index",
                "collect_results": True,
                "parallel": False,
            },
            depends_on=[],
            description="Iterate over each item in the input list",
            generated_from="Detected foreach-style description",
        )

        qa_stage = StageDefinition(
            id="qa_each",
            name="Analyze each item with AI",
            component_type="generator",
            config={
                "prompt": (
                    "For the following item, answer the configured questions and "
                    "return a structured JSON object with numbered answers.\n\n"
                    "Item:\n{{upstream.foreach_items.current_item}}"
                ),
                "max_tokens": 512,
                "temperature": 0.3,
            },
            depends_on=["foreach_items"],
            description="Use LLM to analyze each item in the list",
            generated_from="Per-item analysis inside foreach loop",
        )

        aggregate_stage = StageDefinition(
            id="aggregate_results",
            name="Aggregate item answers into list",
            component_type="json_transform",
            config={
                "template": {
                    "items": "{{upstream.foreach_items.results}}",
                    "total_items": "{{upstream.foreach_items.total_items}}",
                }
            },
            depends_on=["foreach_items"],
            description="Aggregate all per-item results into a single payload",
            generated_from="Summarize foreach outputs",
        )

        stages = [foreach_stage, qa_stage, aggregate_stage]

        pipeline_name = "Foreach Pipeline"
        if analysis.intent and analysis.intent != "unknown":
            intent_words = analysis.intent.replace("_", " ").title()
            pipeline_name = f"{intent_words} Foreach Pipeline"

        input_schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": "List of items to process",
                    "items": {"type": "object"},
                }
            },
            "required": ["items"],
        }

        return GeneratedPipeline(
            name=pipeline_name,
            description=description[:500],
            version="1.0.0",
            stages=stages,
            input_schema=input_schema,
            generation_id=generation_id,
            generated_at=datetime.utcnow().isoformat(),
            original_request=description,
        )

    def _generate_conditional_pipeline(
        self,
        description: str,
        analysis: GenerationAnalysis,
    ) -> GeneratedPipeline:
        """
        Generate a conditional branching pipeline using the conditional
        control-flow component and simple true/false paths.
        """
        generation_id = str(uuid.uuid4())

        conditional_stage = StageDefinition(
            id="check_condition",
            name="Check condition",
            component_type="conditional",
            config={
                "condition": "{{input.condition}}",
                "true_stages": ["true_path"],
                "false_stages": ["false_path"],
            },
            depends_on=[],
            description="Branch execution based on the provided condition",
            generated_from="Detected conditional/branching language",
        )

        true_stage = StageDefinition(
            id="true_path",
            name="True branch",
            component_type="logger",
            config={
                "message": "Condition evaluated to true",
                "level": "info",
                "data": "{{input}}",
            },
            depends_on=["check_condition"],
            description="Executed when condition is true",
            generated_from="Conditional true path",
        )

        false_stage = StageDefinition(
            id="false_path",
            name="False branch",
            component_type="logger",
            config={
                "message": "Condition evaluated to false",
                "level": "info",
                "data": "{{input}}",
            },
            depends_on=["check_condition"],
            description="Executed when condition is false",
            generated_from="Conditional false path",
        )

        stages = [conditional_stage, true_stage, false_stage]

        pipeline_name = "Conditional Routing Pipeline"

        input_schema = {
            "type": "object",
            "properties": {
                "condition": {
                    "type": "string",
                    "description": "Expression that evaluates to true/false",
                },
                "data": {
                    "type": "object",
                    "description": "Input data to route based on the condition",
                },
            },
            "required": ["condition"],
        }

        return GeneratedPipeline(
            name=pipeline_name,
            description=description[:500],
            version="1.0.0",
            stages=stages,
            input_schema=input_schema,
            generation_id=generation_id,
            generated_at=datetime.utcnow().isoformat(),
            original_request=description,
        )

    def _generate_validation_transform_pipeline(
        self,
        description: str,
        analysis: GenerationAnalysis,
    ) -> GeneratedPipeline:
        """
        Generate a validation + transform pipeline pattern.
        """
        generation_id = str(uuid.uuid4())

        validate_stage = StageDefinition(
            id="validate_data",
            name="Validate input data",
            component_type="schema_validate",
            config={
                "data": "{{input.data}}",
                "json_schema": {
                    "type": "object",
                    "properties": {},
                },
                "strict": False,
                "collect_all_errors": True,
            },
            depends_on=[],
            description="Validate the incoming data structure",
            generated_from="Detected validation + transform intent",
        )

        transform_stage = StageDefinition(
            id="transform_data",
            name="Transform validated data",
            component_type="json_transform",
            config={
                "data": "{{upstream.validate_data.data}}",
                "jmespath_expression": "@",
            },
            depends_on=["validate_data"],
            description="Transform or normalize the validated data",
            generated_from="Detected validation + transform intent",
        )

        stages = [validate_stage, transform_stage]

        pipeline_name = "Validation and Transform Pipeline"
        if analysis.intent and analysis.intent != "unknown":
            intent_words = analysis.intent.replace("_", " ").title()
            pipeline_name = f"{intent_words} Validation Pipeline"

        input_schema = {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Input data to validate and transform",
                }
            },
            "required": ["data"],
        }

        return GeneratedPipeline(
            name=pipeline_name,
            description=description[:500],
            version="1.0.0",
            stages=stages,
            input_schema=input_schema,
            generation_id=generation_id,
            generated_at=datetime.utcnow().isoformat(),
            original_request=description,
        )

    def _generate_http_ingest_pipeline(
        self,
        description: str,
        analysis: GenerationAnalysis,
    ) -> GeneratedPipeline:
        """
        Generate an HTTP ingest + send pipeline pattern.
        """
        generation_id = str(uuid.uuid4())

        fetch_stage = StageDefinition(
            id="fetch_source",
            name="Fetch data from source API",
            component_type="http_request",
            config={
                "url": "{{input.source_url}}",
                "method": "GET",
                "headers": {},
                "body": None,
                "timeout": 30,
            },
            depends_on=[],
            description="Fetch data from the source endpoint",
            generated_from="Detected http ingest intent",
        )

        transform_stage = StageDefinition(
            id="transform_payload",
            name="Transform fetched data",
            component_type="json_transform",
            config={
                "data": "{{upstream.fetch_source.body}}",
                "jmespath_expression": "@",
            },
            depends_on=["fetch_source"],
            description="Transform the fetched payload into target shape",
            generated_from="Detected http ingest + send intent",
        )

        send_stage = StageDefinition(
            id="send_output",
            name="Send transformed data to target API",
            component_type="http_request",
            config={
                "url": "{{input.target_url}}",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": "{{upstream.transform_payload.result}}",
                "timeout": 30,
            },
            depends_on=["transform_payload"],
            description="Send the transformed data to the target endpoint",
            generated_from="Detected http ingest + send intent",
        )

        stages = [fetch_stage, transform_stage, send_stage]

        pipeline_name = "HTTP Ingest and Send Pipeline"

        input_schema = {
            "type": "object",
            "properties": {
                "source_url": {
                    "type": "string",
                    "description": "Source API URL to fetch data from",
                },
                "target_url": {
                    "type": "string",
                    "description": "Target API URL to send transformed data to",
                },
            },
            "required": ["source_url", "target_url"],
        }

        return GeneratedPipeline(
            name=pipeline_name,
            description=description[:500],
            version="1.0.0",
            stages=stages,
            input_schema=input_schema,
            generation_id=generation_id,
            generated_at=datetime.utcnow().isoformat(),
            original_request=description,
        )

    def _generate_stage_config(
        self,
        component_type: str,
        purpose: str,
        prev_stage_id: Optional[str],
        description: str,
        mode: GenerationMode,
    ) -> Dict[str, Any]:
        """Generate configuration for a stage."""
        input_ref = f"{{{{stages.{prev_stage_id}.output}}}}" if prev_stage_id else "{{input}}"

        if component_type == "generator":
            return {
                "prompt": f"Based on the following input, {purpose.lower()}:\n\n{input_ref}",
                "max_tokens": 1000,
                "temperature": 0.7,
            }
        elif component_type == "critic":
            return {
                "prompt": f"Evaluate the following content. {purpose}:\n\n{input_ref}",
                "criteria": ["accuracy", "relevance", "quality"],
            }
        elif component_type == "improver":
            return {
                "prompt": f"Improve the following content. {purpose}:\n\n{input_ref}",
                "max_iterations": 3,
            }
        elif component_type == "filter":
            return {
                "items_path": f"{input_ref}.items",
                "condition": "True  # Customize this condition",
            }
        elif component_type == "json_transform":
            return {
                "template": {
                    "result": input_ref,
                    "metadata": {"processed": True},
                },
            }
        elif component_type == "http_request":
            return {
                "url": "https://api.example.com/endpoint",
                "method": "POST",
                "body": input_ref,
            }
        elif component_type == "loop":
            return {
                "items_path": f"{input_ref}.items",
                "max_iterations": 100,
            }
        elif component_type == "schema_validate":
            return {
                "schema": {"type": "object"},
                "data_path": input_ref,
            }
        elif component_type == "variable_set":
            return {
                "name": "result",
                "value": input_ref,
            }
        elif component_type == "logger":
            return {
                "message": f"Processing: {input_ref}",
                "level": "info",
            }
        else:
            return {
                "input": input_ref,
            }

    def _generate_input_schema(
        self,
        analysis: GenerationAnalysis,
        description: str,
    ) -> Dict[str, Any]:
        """Generate input schema based on analysis."""
        properties: Dict[str, Dict[str, Any]] = {}
        required: List[str] = []

        # Add common inputs based on data sources
        if "user_input" in analysis.data_sources or not analysis.data_sources:
            if "text" in description.lower() or "content" in description.lower():
                properties["text"] = {
                    "type": "string",
                    "description": "Input text to process",
                }
                required.append("text")
            else:
                properties["data"] = {
                    "type": "object",
                    "description": "Input data to process",
                }
                required.append("data")

        # Add based on entities
        for entity in analysis.entities[:3]:
            prop_name = entity.lower().replace(" ", "_")
            if prop_name not in properties:
                properties[prop_name] = {
                    "type": "string",
                    "description": f"The {entity}",
                }

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }

    def _validate_pipeline(
        self,
        pipeline: GeneratedPipeline,
    ) -> Tuple[List[str], List[str]]:
        """Validate the generated pipeline."""
        errors: List[str] = []
        warnings: List[str] = []

        if not pipeline.name:
            errors.append("Pipeline name is required")

        if not pipeline.stages:
            errors.append("Pipeline must have at least one stage")

        # Collect stage IDs and detect basic issues
        stage_ids: set[str] = set()
        for stage in pipeline.stages:
            if not stage.id:
                errors.append("Stage ID is required")
            elif stage.id in stage_ids:
                errors.append(f"Duplicate stage ID: {stage.id}")
            stage_ids.add(stage.id)

            if not stage.component_type:
                errors.append(f"Stage {stage.id}: component_type is required")

        # Check that dependencies reference valid stages (no dangling edges)
        for stage in pipeline.stages:
            for dep in stage.depends_on:
                if dep not in stage_ids:
                    errors.append(
                        f"Stage {stage.id}: depends_on unknown stage '{dep}'"
                    )

        # Control-flow specific checks (foreach, conditional, http_request)
        for stage in pipeline.stages:
            if stage.component_type == "foreach":
                loop_stages = stage.config.get("loop_stages")
                if not isinstance(loop_stages, list) or not loop_stages:
                    warnings.append(
                        f"Stage {stage.id}: foreach missing non-empty 'loop_stages' list"
                    )
                else:
                    for loop_id in loop_stages:
                        if loop_id not in stage_ids:
                            warnings.append(
                                f"Stage {stage.id}: foreach.loop_stages references unknown stage '{loop_id}'"
                            )

            if stage.component_type == "conditional":
                true_stages = stage.config.get("true_stages") or []
                false_stages = stage.config.get("false_stages") or []
                if not true_stages and not false_stages:
                    warnings.append(
                        f"Stage {stage.id}: conditional has no true_stages or false_stages configured"
                    )
                for branch_list, label in (
                    (true_stages, "true_stages"),
                    (false_stages, "false_stages"),
                ):
                    if isinstance(branch_list, list):
                        for branch_id in branch_list:
                            if branch_id not in stage_ids:
                                warnings.append(
                                    f"Stage {stage.id}: conditional.{label} references unknown stage '{branch_id}'"
                                )

            if stage.component_type == "http_request":
                url = stage.config.get("url")
                method = stage.config.get("method")
                if not isinstance(url, str) or not url.strip():
                    warnings.append(
                        f"Stage {stage.id}: http_request missing 'url' in config"
                    )
                if not isinstance(method, str) or not method.strip():
                    warnings.append(
                        f"Stage {stage.id}: http_request missing 'method' in config"
                    )

        if not pipeline.description:
            warnings.append("Consider adding a description")

        return errors, warnings


# Global instance
_nl_builder_service: Optional[NLBuilderService] = None


def get_nl_builder_service() -> NLBuilderService:
    """Get the global NL builder service instance."""
    global _nl_builder_service
    if _nl_builder_service is None:
        _nl_builder_service = NLBuilderService()
    return _nl_builder_service
