"""
Pipeline Merger for FlowMason.

Merges parent and child pipeline configurations for inheritance.
"""

import copy
import logging
from typing import Any, Dict, List, Optional

from flowmason_core.config.types import ComponentConfig, PipelineConfig

logger = logging.getLogger(__name__)


class MergeConflictError(Exception):
    """Raised when there's a conflict during merge that cannot be resolved."""

    def __init__(self, stage_id: str, field: str, message: str):
        self.stage_id = stage_id
        self.field = field
        super().__init__(f"Merge conflict in stage '{stage_id}', field '{field}': {message}")


class PipelineMerger:
    """
    Merges pipeline configurations for inheritance.

    Merge rules:
    - Child stages with same ID as parent: child config overrides parent
    - Child stages with new ID: added to merged pipeline
    - Parent stages not in child: inherited as-is
    - Child overrides dict: applied to inherited stages
    - Schemas: child schema extends/overrides parent
    - Metadata: child values override parent values
    """

    def merge_chain(self, chain: List[PipelineConfig]) -> PipelineConfig:
        """
        Merge an inheritance chain from base to child.

        Args:
            chain: List of PipelineConfigs from base (first) to child (last)

        Returns:
            Fully merged PipelineConfig
        """
        if not chain:
            raise ValueError("Cannot merge empty inheritance chain")

        if len(chain) == 1:
            return chain[0]

        # Start with base and merge each child
        result = chain[0]
        for i in range(1, len(chain)):
            result = self.merge_two(result, chain[i])

        return result

    def merge_two(
        self,
        parent: PipelineConfig,
        child: PipelineConfig,
    ) -> PipelineConfig:
        """
        Merge a parent and child pipeline config.

        Args:
            parent: Parent pipeline config
            child: Child pipeline config

        Returns:
            Merged PipelineConfig
        """
        logger.debug(f"Merging '{parent.name}' <- '{child.name}'")

        # Start with child's basic identity
        merged_data = {
            "id": child.id,
            "name": child.name,
            "version": child.version,
            "description": child.description or parent.description,
            "abstract": child.abstract,  # Child controls if result is abstract
            "extends": None,  # Resolved pipeline doesn't need extends
            "overrides": {},  # Overrides are applied during merge
        }

        # Merge stages
        merged_stages = self._merge_stages(parent, child)
        merged_data["stages"] = merged_stages

        # Merge compositions
        merged_compositions = self._merge_compositions(parent, child)
        merged_data["compositions"] = merged_compositions

        # Merge schemas
        merged_data["input_schema"] = self._merge_schema(
            parent.input_schema.model_dump(),
            child.input_schema.model_dump(),
        )
        merged_data["output_schema"] = self._merge_schema(
            parent.output_schema.model_dump(),
            child.output_schema.model_dump(),
        )

        # Merge metadata
        merged_data["tags"] = list(set(parent.tags + child.tags))
        merged_data["category"] = child.category or parent.category
        merged_data["output_stage_id"] = child.output_stage_id or parent.output_stage_id

        return PipelineConfig(**merged_data)

    def _merge_stages(
        self,
        parent: PipelineConfig,
        child: PipelineConfig,
    ) -> List[Dict[str, Any]]:
        """
        Merge stages from parent and child.

        Strategy:
        1. Start with parent stages
        2. Apply child overrides to parent stages
        3. Replace/add stages defined in child
        4. Maintain topological order
        """
        # Index parent stages by ID
        parent_stages: Dict[str, ComponentConfig] = {s.id: s for s in parent.stages}
        child_stages: Dict[str, ComponentConfig] = {s.id: s for s in child.stages}

        # Apply overrides from child.overrides to parent stages
        for stage_id, override_config in child.overrides.items():
            if stage_id in parent_stages:
                parent_stages[stage_id] = self._apply_override(
                    parent_stages[stage_id],
                    override_config,
                )
            else:
                logger.warning(
                    f"Override for non-existent stage '{stage_id}' in '{child.name}'"
                )

        # Build merged stage list
        merged: List[Dict[str, Any]] = []
        seen_ids: set = set()

        # First, process parent stages (possibly overridden)
        for parent_stage in parent.stages:
            stage_id = parent_stage.id

            if stage_id in child_stages:
                # Child defines this stage - use child's version
                merged.append(child_stages[stage_id].model_dump())
            else:
                # Use (possibly overridden) parent stage
                merged.append(parent_stages[stage_id].model_dump())

            seen_ids.add(stage_id)

        # Add any new stages from child that weren't in parent
        for child_stage in child.stages:
            if child_stage.id not in seen_ids:
                merged.append(child_stage.model_dump())

        return merged

    def _merge_compositions(
        self,
        parent: PipelineConfig,
        child: PipelineConfig,
    ) -> List[Dict[str, Any]]:
        """
        Merge compositions from parent and child.

        Child compositions with same ID override parent.
        """
        parent_comps = {c.id: c for c in parent.compositions}
        child_comps = {c.id: c for c in child.compositions}

        merged: List[Dict[str, Any]] = []
        seen_ids: set = set()

        # Parent compositions (possibly overridden by child)
        for comp in parent.compositions:
            if comp.id in child_comps:
                merged.append(child_comps[comp.id].model_dump())
            else:
                merged.append(comp.model_dump())
            seen_ids.add(comp.id)

        # New compositions from child
        for comp in child.compositions:
            if comp.id not in seen_ids:
                merged.append(comp.model_dump())

        return merged

    def _apply_override(
        self,
        stage: ComponentConfig,
        override: Dict[str, Any],
    ) -> ComponentConfig:
        """
        Apply override config to a stage.

        Does a deep merge of the override into the stage config.
        """
        stage_dict = stage.model_dump()
        merged = self._deep_merge(stage_dict, override)
        return ComponentConfig(**merged)

    def _deep_merge(
        self,
        base: Dict[str, Any],
        override: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.

        Override values replace base values, except for dicts which are merged recursively.
        """
        result = copy.deepcopy(base)

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)

        return result

    def _merge_schema(
        self,
        parent_schema: Dict[str, Any],
        child_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Merge input/output schemas.

        Child properties extend parent properties.
        Child required fields extend parent required fields.
        """
        merged = copy.deepcopy(parent_schema)

        # Merge properties
        if "properties" in child_schema:
            if "properties" not in merged:
                merged["properties"] = {}
            merged["properties"].update(child_schema["properties"])

        # Merge required fields
        if "required" in child_schema:
            parent_required = set(merged.get("required", []))
            child_required = set(child_schema["required"])
            merged["required"] = list(parent_required | child_required)

        # Child type overrides parent
        if "type" in child_schema:
            merged["type"] = child_schema["type"]

        return merged
