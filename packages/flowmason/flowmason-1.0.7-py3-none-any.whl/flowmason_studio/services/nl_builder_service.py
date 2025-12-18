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


# Component catalog with descriptions for matching
COMPONENT_CATALOG = {
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

        for comp_type, comp_info in COMPONENT_CATALOG.items():
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
                name=COMPONENT_CATALOG[comp_type]["name"],
                description=COMPONENT_CATALOG[comp_type]["description"],
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

        for field in ["actions", "data_sources", "outputs", "constraints", "ambiguities"]:
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
                    info = COMPONENT_CATALOG.get(comp_type, {})
                    suggestions.append(ComponentSuggestion(
                        component_type=comp_type,
                        name=info.get("name", comp_type),
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
                        info = COMPONENT_CATALOG.get(comp_type, {})
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
                        name="HTTP Request",
                        purpose="Fetch data from external API",
                        rationale="Required for external data source",
                        confidence=0.95,
                    ))

        # Add preferred components if not already present
        if preferred:
            for comp_type in preferred:
                if not any(s.component_type == comp_type for s in suggestions):
                    info = COMPONENT_CATALOG.get(comp_type, {})
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
            info = COMPONENT_CATALOG.get("generator", {})
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

        stage_ids = set()
        for stage in pipeline.stages:
            if not stage.id:
                errors.append("Stage ID is required")
            elif stage.id in stage_ids:
                errors.append(f"Duplicate stage ID: {stage.id}")
            stage_ids.add(stage.id)

            if not stage.component_type:
                errors.append(f"Stage {stage.id}: component_type is required")

            # Check dependencies exist
            for dep in stage.depends_on:
                if dep not in stage_ids:
                    # Might be defined later, just warn
                    pass

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
