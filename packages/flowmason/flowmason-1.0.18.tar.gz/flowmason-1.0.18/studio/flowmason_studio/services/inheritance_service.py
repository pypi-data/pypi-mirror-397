"""
Pipeline Inheritance & Composition Service.

Handles extending and composing pipelines from base templates.
"""

import copy
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flowmason_studio.models.inheritance import (
    BasePipeline,
    ComposedPipeline,
    CompositionMode,
    ExtendPipelineRequest,
    InheritanceMode,
    PipelineInheritance,
    ResolvedPipeline,
    StageAddition,
    StageOverride,
    StageRemoval,
    VariableOverride,
)


class InheritanceService:
    """Service for managing pipeline inheritance and composition."""

    def __init__(self):
        """Initialize the inheritance service."""
        self._base_pipelines: Dict[str, BasePipeline] = {}
        self._compositions: Dict[str, ComposedPipeline] = {}
        self._inheritance_map: Dict[str, PipelineInheritance] = {}

        # Initialize with sample base templates
        self._init_sample_templates()

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())

    def _now(self) -> str:
        """Get current ISO timestamp."""
        return datetime.utcnow().isoformat()

    def _init_sample_templates(self):
        """Initialize with sample base pipeline templates."""
        # AI Chat Template
        self._base_pipelines["tmpl_ai_chat"] = BasePipeline(
            id="tmpl_ai_chat",
            name="AI Chat Pipeline",
            description="Base template for conversational AI pipelines",
            category="ai",
            tags=["ai", "chat", "conversational"],
            stages=[
                {
                    "id": "input_handler",
                    "name": "Input Handler",
                    "component_type": "variable_set",
                    "config": {"variables": {"processed_input": "{input}"}},
                },
                {
                    "id": "ai_response",
                    "name": "AI Response",
                    "component_type": "generator",
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "prompt": "{processed_input}",
                        "system_prompt": "You are a helpful assistant.",
                    },
                    "depends_on": ["input_handler"],
                },
                {
                    "id": "output_formatter",
                    "name": "Output Formatter",
                    "component_type": "json_transform",
                    "config": {"mapping": {"response": "output"}},
                    "depends_on": ["ai_response"],
                },
            ],
            variables={"max_tokens": 1024, "temperature": 0.7},
            required_overrides=["ai_response"],  # Must customize the AI config
        )

        # Data Processing Template
        self._base_pipelines["tmpl_data_etl"] = BasePipeline(
            id="tmpl_data_etl",
            name="Data ETL Pipeline",
            description="Base template for Extract-Transform-Load pipelines",
            category="data",
            tags=["data", "etl", "processing"],
            is_abstract=True,  # Cannot run directly
            stages=[
                {
                    "id": "extract",
                    "name": "Extract",
                    "component_type": "http_request",
                    "config": {"method": "GET", "url": "{source_url}"},
                },
                {
                    "id": "transform",
                    "name": "Transform",
                    "component_type": "json_transform",
                    "config": {"mapping": {}},
                    "depends_on": ["extract"],
                },
                {
                    "id": "load",
                    "name": "Load",
                    "component_type": "http_request",
                    "config": {"method": "POST", "url": "{destination_url}"},
                    "depends_on": ["transform"],
                },
            ],
            required_overrides=["extract", "transform", "load"],
        )

        # API Integration Template
        self._base_pipelines["tmpl_api_integration"] = BasePipeline(
            id="tmpl_api_integration",
            name="API Integration Pipeline",
            description="Base template for REST API integrations",
            category="integration",
            tags=["api", "integration", "rest"],
            stages=[
                {
                    "id": "auth",
                    "name": "Authentication",
                    "component_type": "variable_set",
                    "config": {"variables": {"auth_header": "Bearer {api_key}"}},
                },
                {
                    "id": "request",
                    "name": "API Request",
                    "component_type": "http_request",
                    "config": {
                        "method": "GET",
                        "url": "{api_endpoint}",
                        "headers": {"Authorization": "{auth_header}"},
                    },
                    "depends_on": ["auth"],
                },
                {
                    "id": "response_handler",
                    "name": "Response Handler",
                    "component_type": "json_transform",
                    "config": {"mapping": {"data": "body"}},
                    "depends_on": ["request"],
                },
            ],
            sealed_stages=["auth"],  # Auth logic cannot be modified
        )

        # Content Generation Template
        self._base_pipelines["tmpl_content_gen"] = BasePipeline(
            id="tmpl_content_gen",
            name="Content Generation Pipeline",
            description="Base template for AI content generation workflows",
            category="ai",
            tags=["ai", "content", "generation"],
            stages=[
                {
                    "id": "topic_analysis",
                    "name": "Topic Analysis",
                    "component_type": "generator",
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "prompt": "Analyze this topic: {topic}",
                    },
                },
                {
                    "id": "outline",
                    "name": "Create Outline",
                    "component_type": "generator",
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "prompt": "Create an outline based on: {output}",
                    },
                    "depends_on": ["topic_analysis"],
                },
                {
                    "id": "content",
                    "name": "Generate Content",
                    "component_type": "generator",
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "prompt": "Write content following this outline: {output}",
                    },
                    "depends_on": ["outline"],
                },
                {
                    "id": "review",
                    "name": "Quality Review",
                    "component_type": "generator",
                    "config": {
                        "provider": "openai",
                        "model": "gpt-4",
                        "prompt": "Review and improve: {output}",
                    },
                    "depends_on": ["content"],
                },
            ],
        )

    # =========================================================================
    # Base Pipeline Management
    # =========================================================================

    def create_base_pipeline(
        self,
        name: str,
        stages: List[Dict[str, Any]],
        description: str = "",
        category: str = "general",
        tags: Optional[List[str]] = None,
        is_abstract: bool = False,
        required_overrides: Optional[List[str]] = None,
        sealed_stages: Optional[List[str]] = None,
        variables: Optional[Dict[str, Any]] = None,
        settings: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
    ) -> BasePipeline:
        """Create a new base pipeline template."""
        template_id = f"tmpl_{self._generate_id()[:8]}"

        template = BasePipeline(
            id=template_id,
            name=name,
            description=description,
            category=category,
            tags=tags or [],
            is_abstract=is_abstract,
            required_overrides=required_overrides or [],
            sealed_stages=sealed_stages or [],
            stages=stages,
            variables=variables or {},
            settings=settings or {},
            created_at=self._now(),
            created_by=created_by,
        )

        self._base_pipelines[template_id] = template
        return template

    def get_base_pipeline(self, template_id: str) -> Optional[BasePipeline]:
        """Get a base pipeline by ID."""
        return self._base_pipelines.get(template_id)

    def list_base_pipelines(
        self,
        category: Optional[str] = None,
        include_abstract: bool = True,
    ) -> List[BasePipeline]:
        """List all base pipeline templates."""
        templates = list(self._base_pipelines.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if not include_abstract:
            templates = [t for t in templates if not t.is_abstract]

        return templates

    def get_categories(self) -> List[str]:
        """Get all template categories."""
        categories = set()
        for template in self._base_pipelines.values():
            categories.add(template.category)
        return sorted(categories)

    def delete_base_pipeline(self, template_id: str) -> bool:
        """Delete a base pipeline template."""
        if template_id in self._base_pipelines:
            del self._base_pipelines[template_id]
            return True
        return False

    # =========================================================================
    # Pipeline Extension
    # =========================================================================

    def extend_pipeline(
        self,
        request: ExtendPipelineRequest,
        created_by: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Create a new pipeline by extending a base pipeline.

        Returns:
            Tuple of (resolved_pipeline_dict, warnings)
        """
        base = self._base_pipelines.get(request.base_pipeline_id)
        if not base:
            raise ValueError(f"Base pipeline not found: {request.base_pipeline_id}")

        warnings = []

        # Validate overrides
        validation = self.validate_inheritance(
            request.base_pipeline_id,
            request.stage_overrides,
            request.stage_additions,
            request.stage_removals,
        )

        if not validation["valid"]:
            raise ValueError(f"Invalid inheritance: {validation['errors']}")

        warnings.extend(validation["warnings"])

        # Start with base stages
        stages = copy.deepcopy(base.stages)
        variables = copy.deepcopy(base.variables)
        settings = copy.deepcopy(base.settings)

        # Apply removals first
        for removal in request.stage_removals:
            stages = self._apply_stage_removal(stages, removal)

        # Apply overrides
        for override in request.stage_overrides:
            stages = self._apply_stage_override(stages, override)

        # Apply additions
        for addition in request.stage_additions:
            stages = self._apply_stage_addition(stages, addition)

        # Apply variable overrides
        for var_override in request.variable_overrides:
            variables = self._apply_variable_override(variables, var_override)

        # Create the extended pipeline
        pipeline_id = self._generate_id()
        extended = {
            "id": pipeline_id,
            "name": request.name,
            "description": request.description,
            "stages": stages,
            "variables": variables,
            "settings": settings,
            "extends": {
                "base_id": request.base_pipeline_id,
                "base_version": request.base_version,
            },
            "created_at": self._now(),
            "created_by": created_by,
        }

        # Store inheritance info
        self._inheritance_map[pipeline_id] = PipelineInheritance(
            extends={"pipeline_id": request.base_pipeline_id, "version": request.base_version},
            stage_overrides=request.stage_overrides,
            stage_additions=request.stage_additions,
            stage_removals=request.stage_removals,
            variable_overrides=request.variable_overrides,
        )

        return extended, warnings

    def _apply_stage_removal(
        self,
        stages: List[Dict[str, Any]],
        removal: StageRemoval,
    ) -> List[Dict[str, Any]]:
        """Remove a stage from the pipeline."""
        stage_ids_to_remove = {removal.stage_id}

        if removal.cascade:
            # Find all stages that depend on this one
            def find_dependents(stage_id: str):
                for stage in stages:
                    if stage_id in stage.get("depends_on", []):
                        stage_ids_to_remove.add(stage["id"])
                        find_dependents(stage["id"])

            find_dependents(removal.stage_id)

        return [s for s in stages if s.get("id") not in stage_ids_to_remove]

    def _apply_stage_override(
        self,
        stages: List[Dict[str, Any]],
        override: StageOverride,
    ) -> List[Dict[str, Any]]:
        """Apply an override to a stage."""
        for i, stage in enumerate(stages):
            if stage.get("id") == override.stage_id:
                if override.mode == InheritanceMode.OVERRIDE:
                    # Complete replacement of specified fields
                    if override.config is not None:
                        stages[i]["config"] = override.config
                    if override.component_type is not None:
                        stages[i]["component_type"] = override.component_type
                    if override.depends_on is not None:
                        stages[i]["depends_on"] = override.depends_on
                    if override.enabled is not None:
                        stages[i]["enabled"] = override.enabled

                elif override.mode == InheritanceMode.MERGE:
                    # Deep merge configurations
                    if override.config is not None:
                        existing_config = stages[i].get("config", {})
                        stages[i]["config"] = self._deep_merge(existing_config, override.config)
                    if override.component_type is not None:
                        stages[i]["component_type"] = override.component_type
                    if override.depends_on is not None:
                        # Merge dependencies
                        existing = set(stages[i].get("depends_on", []))
                        stages[i]["depends_on"] = list(existing | set(override.depends_on))
                    if override.enabled is not None:
                        stages[i]["enabled"] = override.enabled

                break

        return stages

    def _apply_stage_addition(
        self,
        stages: List[Dict[str, Any]],
        addition: StageAddition,
    ) -> List[Dict[str, Any]]:
        """Add a new stage to the pipeline."""
        new_stage = {
            "id": addition.id,
            "name": addition.name,
            "component_type": addition.component_type,
            "config": addition.config,
            "depends_on": addition.depends_on,
        }

        if addition.insert_after:
            # Find position and insert after
            for i, stage in enumerate(stages):
                if stage.get("id") == addition.insert_after:
                    stages.insert(i + 1, new_stage)
                    return stages
        elif addition.insert_before:
            # Find position and insert before
            for i, stage in enumerate(stages):
                if stage.get("id") == addition.insert_before:
                    stages.insert(i, new_stage)
                    return stages

        # Default: append to end
        stages.append(new_stage)
        return stages

    def _apply_variable_override(
        self,
        variables: Dict[str, Any],
        override: VariableOverride,
    ) -> Dict[str, Any]:
        """Apply a variable override."""
        if override.mode == InheritanceMode.OVERRIDE:
            variables[override.name] = override.value
        elif override.mode == InheritanceMode.MERGE:
            if isinstance(variables.get(override.name), dict) and isinstance(override.value, dict):
                variables[override.name] = self._deep_merge(
                    variables[override.name], override.value
                )
            else:
                variables[override.name] = override.value
        return variables

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = copy.deepcopy(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        return result

    def validate_inheritance(
        self,
        base_id: str,
        overrides: List[StageOverride],
        additions: List[StageAddition],
        removals: List[StageRemoval],
    ) -> Dict[str, Any]:
        """Validate inheritance configuration."""
        base = self._base_pipelines.get(base_id)
        if not base:
            return {
                "valid": False,
                "errors": [f"Base pipeline not found: {base_id}"],
                "warnings": [],
                "missing_overrides": [],
                "sealed_violations": [],
            }

        errors = []
        warnings = []
        missing_overrides = []
        sealed_violations = []

        # Check required overrides
        override_ids = {o.stage_id for o in overrides}
        for required in base.required_overrides:
            if required not in override_ids:
                missing_overrides.append(required)

        if missing_overrides:
            errors.append(
                f"Missing required overrides: {missing_overrides}"
            )

        # Check sealed stages
        for override in overrides:
            if override.stage_id in base.sealed_stages:
                sealed_violations.append(override.stage_id)

        if sealed_violations:
            errors.append(
                f"Cannot override sealed stages: {sealed_violations}"
            )

        # Check stage existence for overrides
        base_stage_ids = {s.get("id") for s in base.stages}
        for override in overrides:
            if override.stage_id not in base_stage_ids:
                warnings.append(
                    f"Override target not found in base: {override.stage_id}"
                )

        # Check for circular dependencies in additions
        addition_ids = {a.id for a in additions}
        for addition in additions:
            for dep in addition.depends_on:
                if dep in addition_ids:
                    # Check if this creates a cycle
                    if self._has_cycle(additions, addition.id, dep):
                        errors.append(
                            f"Circular dependency detected: {addition.id} -> {dep}"
                        )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "missing_overrides": missing_overrides,
            "sealed_violations": sealed_violations,
        }

    def _has_cycle(
        self,
        additions: List[StageAddition],
        start: str,
        current: str,
        visited: Optional[set] = None,
    ) -> bool:
        """Check for circular dependencies."""
        if visited is None:
            visited = set()

        if current == start:
            return True

        if current in visited:
            return False

        visited.add(current)

        # Find the addition for current
        for addition in additions:
            if addition.id == current:
                for dep in addition.depends_on:
                    if self._has_cycle(additions, start, dep, visited):
                        return True

        return False

    # =========================================================================
    # Pipeline Composition
    # =========================================================================

    def compose_pipelines(
        self,
        name: str,
        pipeline_ids: List[str],
        mode: CompositionMode = CompositionMode.SEQUENTIAL,
        output_mapping: Optional[Dict[str, Dict[str, str]]] = None,
        condition: Optional[str] = None,
        condition_map: Optional[Dict[str, str]] = None,
        default_pipeline: Optional[str] = None,
        merge_strategy: str = "merge",
    ) -> ComposedPipeline:
        """Create a composed pipeline from multiple pipelines."""
        composition_id = f"comp_{self._generate_id()[:8]}"

        composition = ComposedPipeline(
            id=composition_id,
            pipelines=pipeline_ids,
            mode=mode,
            output_mapping=output_mapping or {},
            condition=condition,
            condition_map=condition_map or {},
            default_pipeline=default_pipeline,
            merge_strategy=merge_strategy,
        )

        self._compositions[composition_id] = composition
        return composition

    def get_composition(self, composition_id: str) -> Optional[ComposedPipeline]:
        """Get a composition by ID."""
        return self._compositions.get(composition_id)

    def resolve_composition(
        self,
        composition_id: str,
        pipelines: Dict[str, Dict[str, Any]],
    ) -> ResolvedPipeline:
        """
        Resolve a composition into a single executable pipeline.

        Args:
            composition_id: ID of the composition
            pipelines: Dictionary of pipeline_id -> pipeline_dict
        """
        composition = self._compositions.get(composition_id)
        if not composition:
            raise ValueError(f"Composition not found: {composition_id}")

        all_stages = []
        warnings = []

        if composition.mode == CompositionMode.SEQUENTIAL:
            # Chain pipelines sequentially
            prev_pipeline_id = None

            for i, pid in enumerate(composition.pipelines):
                pipeline = pipelines.get(pid)
                if not pipeline:
                    warnings.append(f"Pipeline not found: {pid}")
                    continue

                stages = copy.deepcopy(pipeline.get("stages", []))

                # Prefix stage IDs to avoid conflicts
                prefix = f"p{i}_"
                for stage in stages:
                    original_id = stage.get("id")
                    stage["id"] = f"{prefix}{original_id}"
                    stage["_source_pipeline"] = pid

                    # Update dependencies
                    if "depends_on" in stage:
                        stage["depends_on"] = [
                            f"{prefix}{dep}" for dep in stage["depends_on"]
                        ]

                # Add dependency on previous pipeline's last stage
                if prev_pipeline_id and stages:
                    # Apply output mapping
                    mapping = composition.output_mapping.get(prev_pipeline_id, {})
                    if mapping:
                        # Add a transform stage for mapping
                        map_stage = {
                            "id": f"{prefix}input_map",
                            "name": "Input Mapping",
                            "component_type": "json_transform",
                            "config": {"mapping": mapping},
                            "depends_on": [all_stages[-1]["id"]] if all_stages else [],
                        }
                        all_stages.append(map_stage)

                        # Make first stage depend on mapping
                        if stages:
                            stages[0]["depends_on"] = [map_stage["id"]]
                    else:
                        # Direct dependency on last stage of previous pipeline
                        if stages and all_stages:
                            stages[0]["depends_on"] = [all_stages[-1]["id"]]

                all_stages.extend(stages)
                prev_pipeline_id = pid

        elif composition.mode == CompositionMode.PARALLEL:
            # Run all pipelines in parallel, merge outputs
            for i, pid in enumerate(composition.pipelines):
                pipeline = pipelines.get(pid)
                if not pipeline:
                    warnings.append(f"Pipeline not found: {pid}")
                    continue

                stages = copy.deepcopy(pipeline.get("stages", []))

                # Prefix stage IDs
                prefix = f"p{i}_"
                for stage in stages:
                    stage["id"] = f"{prefix}{stage.get('id')}"
                    stage["_source_pipeline"] = pid
                    if "depends_on" in stage:
                        stage["depends_on"] = [
                            f"{prefix}{dep}" for dep in stage["depends_on"]
                        ]

                all_stages.extend(stages)

            # Add merge stage
            final_stages = [s for s in all_stages if not any(
                s["id"] in other.get("depends_on", [])
                for other in all_stages if other["id"] != s["id"]
            )]

            if final_stages:
                merge_stage = {
                    "id": "merge_outputs",
                    "name": "Merge Outputs",
                    "component_type": "json_transform",
                    "config": {
                        "merge_strategy": composition.merge_strategy,
                    },
                    "depends_on": [s["id"] for s in final_stages],
                }
                all_stages.append(merge_stage)

        return ResolvedPipeline(
            id=composition_id,
            name=f"Composed: {composition_id}",
            stages=all_stages,
            composed_from=composition.pipelines,
            resolution_warnings=warnings,
        )

    # =========================================================================
    # Resolution
    # =========================================================================

    def resolve_pipeline(
        self,
        pipeline_id: str,
        pipeline: Dict[str, Any],
        get_pipeline_func: callable,
    ) -> ResolvedPipeline:
        """
        Fully resolve a pipeline, including all inheritance.

        Args:
            pipeline_id: ID of the pipeline
            pipeline: Pipeline dictionary
            get_pipeline_func: Function to fetch pipelines by ID
        """
        base_pipelines = []
        warnings = []

        # Check if this pipeline extends another
        extends = pipeline.get("extends")
        if extends:
            base_id = extends.get("base_id")
            if base_id:
                # Check in our templates first
                base = self._base_pipelines.get(base_id)
                if not base:
                    # Try to fetch as regular pipeline
                    base_pipeline = get_pipeline_func(base_id)
                    if base_pipeline:
                        # Recursively resolve the base
                        resolved_base = self.resolve_pipeline(
                            base_id, base_pipeline, get_pipeline_func
                        )
                        base_pipelines.extend(resolved_base.base_pipelines)
                        base_pipelines.append(base_id)
                else:
                    base_pipelines.append(base_id)

        return ResolvedPipeline(
            id=pipeline_id,
            name=pipeline.get("name", ""),
            description=pipeline.get("description", ""),
            stages=pipeline.get("stages", []),
            variables=pipeline.get("variables", {}),
            settings=pipeline.get("settings", {}),
            base_pipelines=base_pipelines,
            resolution_warnings=warnings,
        )


# Singleton instance
_service: Optional[InheritanceService] = None


def get_inheritance_service() -> InheritanceService:
    """Get the singleton InheritanceService instance."""
    global _service
    if _service is None:
        _service = InheritanceService()
    return _service
