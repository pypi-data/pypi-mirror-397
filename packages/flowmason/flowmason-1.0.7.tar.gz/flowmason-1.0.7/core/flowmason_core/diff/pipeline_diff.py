"""
Pipeline Diff Algorithm for FlowMason.

Computes structural differences between two pipeline configurations.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class ChangeType(str, Enum):
    """Type of change in a diff."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    MOVED = "moved"
    UNCHANGED = "unchanged"


@dataclass
class FieldChange:
    """A single field-level change."""
    field_path: str
    old_value: Any
    new_value: Any
    change_type: ChangeType

    def __str__(self) -> str:
        if self.change_type == ChangeType.ADDED:
            return f"+ {self.field_path}: {self.new_value}"
        elif self.change_type == ChangeType.REMOVED:
            return f"- {self.field_path}: {self.old_value}"
        elif self.change_type == ChangeType.MODIFIED:
            return f"~ {self.field_path}: {self.old_value} -> {self.new_value}"
        return f"  {self.field_path}: {self.old_value}"


@dataclass
class StageModification:
    """Detailed modifications to a stage."""
    stage_id: str
    changes: List[FieldChange] = field(default_factory=list)

    @property
    def is_significant(self) -> bool:
        """Check if modifications are significant (not just position)."""
        return any(
            c.field_path not in ("position", "position.x", "position.y")
            for c in self.changes
        )


@dataclass
class StageDiff:
    """Diff information for a single stage."""
    stage_id: str
    change_type: ChangeType
    old_index: Optional[int] = None
    new_index: Optional[int] = None
    old_config: Optional[Dict[str, Any]] = None
    new_config: Optional[Dict[str, Any]] = None
    modifications: Optional[StageModification] = None


@dataclass
class DiffResult:
    """Result of comparing two pipelines."""
    # Pipeline-level changes
    name_changed: bool = False
    old_name: Optional[str] = None
    new_name: Optional[str] = None

    version_changed: bool = False
    old_version: Optional[str] = None
    new_version: Optional[str] = None

    description_changed: bool = False
    old_description: Optional[str] = None
    new_description: Optional[str] = None

    # Stage-level changes
    added_stages: List[StageDiff] = field(default_factory=list)
    removed_stages: List[StageDiff] = field(default_factory=list)
    modified_stages: List[StageDiff] = field(default_factory=list)
    moved_stages: List[StageDiff] = field(default_factory=list)
    unchanged_stages: List[StageDiff] = field(default_factory=list)

    # Schema changes
    input_schema_changed: bool = False
    output_schema_changed: bool = False
    input_schema_changes: List[FieldChange] = field(default_factory=list)
    output_schema_changes: List[FieldChange] = field(default_factory=list)

    # Dependency graph changes
    dependency_changes: List[Tuple[str, str, ChangeType]] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return bool(
            self.name_changed
            or self.version_changed
            or self.description_changed
            or self.added_stages
            or self.removed_stages
            or self.modified_stages
            or self.moved_stages
            or self.input_schema_changed
            or self.output_schema_changed
        )

    @property
    def is_structural_change(self) -> bool:
        """Check if the change affects pipeline structure (stages/dependencies)."""
        return bool(
            self.added_stages
            or self.removed_stages
            or self.dependency_changes
        )

    @property
    def summary(self) -> str:
        """Get a human-readable summary of changes."""
        parts = []
        if self.added_stages:
            parts.append(f"+{len(self.added_stages)} stages")
        if self.removed_stages:
            parts.append(f"-{len(self.removed_stages)} stages")
        if self.modified_stages:
            parts.append(f"~{len(self.modified_stages)} stages")
        if self.moved_stages:
            parts.append(f">{len(self.moved_stages)} moved")
        if self.input_schema_changed:
            parts.append("input schema")
        if self.output_schema_changed:
            parts.append("output schema")
        return ", ".join(parts) if parts else "no changes"


class PipelineDiffer:
    """
    Computes structural differences between two pipelines.

    The differ produces a DiffResult that describes:
    - Added, removed, modified, and moved stages
    - Configuration changes within stages
    - Schema changes
    - Dependency graph changes
    """

    def diff(
        self,
        old_pipeline: Any,
        new_pipeline: Any,
        ignore_position: bool = True,
    ) -> DiffResult:
        """
        Compute the diff between two pipelines.

        Args:
            old_pipeline: The original pipeline (base)
            new_pipeline: The new pipeline (target)
            ignore_position: If True, position changes don't count as modifications

        Returns:
            DiffResult with all detected changes
        """
        result = DiffResult()

        # Compare metadata
        self._diff_metadata(old_pipeline, new_pipeline, result)

        # Compare stages
        self._diff_stages(old_pipeline, new_pipeline, result, ignore_position)

        # Compare schemas
        self._diff_schemas(old_pipeline, new_pipeline, result)

        # Analyze dependency changes
        self._diff_dependencies(old_pipeline, new_pipeline, result)

        return result

    def _diff_metadata(
        self,
        old_pipeline: Any,
        new_pipeline: Any,
        result: DiffResult,
    ) -> None:
        """Compare pipeline-level metadata."""
        # Name
        old_name = getattr(old_pipeline, "name", None)
        new_name = getattr(new_pipeline, "name", None)
        if old_name != new_name:
            result.name_changed = True
            result.old_name = old_name
            result.new_name = new_name

        # Version
        old_version = getattr(old_pipeline, "version", None)
        new_version = getattr(new_pipeline, "version", None)
        if old_version != new_version:
            result.version_changed = True
            result.old_version = old_version
            result.new_version = new_version

        # Description
        old_desc = getattr(old_pipeline, "description", None)
        new_desc = getattr(new_pipeline, "description", None)
        if old_desc != new_desc:
            result.description_changed = True
            result.old_description = old_desc
            result.new_description = new_desc

    def _diff_stages(
        self,
        old_pipeline: Any,
        new_pipeline: Any,
        result: DiffResult,
        ignore_position: bool,
    ) -> None:
        """Compare pipeline stages."""
        old_stages = getattr(old_pipeline, "stages", [])
        new_stages = getattr(new_pipeline, "stages", [])

        # Build maps by ID
        old_stage_map: Dict[str, Tuple[int, Any]] = {}
        for i, stage in enumerate(old_stages):
            stage_id = getattr(stage, "id", None)
            if stage_id:
                old_stage_map[stage_id] = (i, stage)

        new_stage_map: Dict[str, Tuple[int, Any]] = {}
        for i, stage in enumerate(new_stages):
            stage_id = getattr(stage, "id", None)
            if stage_id:
                new_stage_map[stage_id] = (i, stage)

        old_ids = set(old_stage_map.keys())
        new_ids = set(new_stage_map.keys())

        # Added stages
        for stage_id in new_ids - old_ids:
            new_idx, new_stage = new_stage_map[stage_id]
            result.added_stages.append(StageDiff(
                stage_id=stage_id,
                change_type=ChangeType.ADDED,
                new_index=new_idx,
                new_config=self._stage_to_dict(new_stage),
            ))

        # Removed stages
        for stage_id in old_ids - new_ids:
            old_idx, old_stage = old_stage_map[stage_id]
            result.removed_stages.append(StageDiff(
                stage_id=stage_id,
                change_type=ChangeType.REMOVED,
                old_index=old_idx,
                old_config=self._stage_to_dict(old_stage),
            ))

        # Compare existing stages
        for stage_id in old_ids & new_ids:
            old_idx, old_stage = old_stage_map[stage_id]
            new_idx, new_stage = new_stage_map[stage_id]

            modifications = self._diff_stage_config(
                stage_id, old_stage, new_stage, ignore_position
            )

            if modifications.changes:
                if modifications.is_significant:
                    result.modified_stages.append(StageDiff(
                        stage_id=stage_id,
                        change_type=ChangeType.MODIFIED,
                        old_index=old_idx,
                        new_index=new_idx,
                        old_config=self._stage_to_dict(old_stage),
                        new_config=self._stage_to_dict(new_stage),
                        modifications=modifications,
                    ))
                elif old_idx != new_idx:
                    result.moved_stages.append(StageDiff(
                        stage_id=stage_id,
                        change_type=ChangeType.MOVED,
                        old_index=old_idx,
                        new_index=new_idx,
                    ))
                else:
                    result.unchanged_stages.append(StageDiff(
                        stage_id=stage_id,
                        change_type=ChangeType.UNCHANGED,
                        old_index=old_idx,
                        new_index=new_idx,
                    ))
            elif old_idx != new_idx:
                result.moved_stages.append(StageDiff(
                    stage_id=stage_id,
                    change_type=ChangeType.MOVED,
                    old_index=old_idx,
                    new_index=new_idx,
                ))
            else:
                result.unchanged_stages.append(StageDiff(
                    stage_id=stage_id,
                    change_type=ChangeType.UNCHANGED,
                    old_index=old_idx,
                    new_index=new_idx,
                ))

    def _diff_stage_config(
        self,
        stage_id: str,
        old_stage: Any,
        new_stage: Any,
        ignore_position: bool,
    ) -> StageModification:
        """Compare two stage configurations and return modifications."""
        modifications = StageModification(stage_id=stage_id)

        old_dict = self._stage_to_dict(old_stage)
        new_dict = self._stage_to_dict(new_stage)

        # Recursively compare dicts
        self._diff_dicts(old_dict, new_dict, "", modifications.changes, ignore_position)

        return modifications

    def _diff_dicts(
        self,
        old_dict: Dict[str, Any],
        new_dict: Dict[str, Any],
        prefix: str,
        changes: List[FieldChange],
        ignore_position: bool,
    ) -> None:
        """Recursively compare two dictionaries."""
        all_keys = set(old_dict.keys()) | set(new_dict.keys())

        for key in all_keys:
            field_path = f"{prefix}.{key}" if prefix else key

            # Skip position fields if requested
            if ignore_position and key in ("position", "x", "y"):
                if prefix in ("", "position"):
                    continue

            old_value = old_dict.get(key)
            new_value = new_dict.get(key)

            if key not in old_dict:
                changes.append(FieldChange(
                    field_path=field_path,
                    old_value=None,
                    new_value=new_value,
                    change_type=ChangeType.ADDED,
                ))
            elif key not in new_dict:
                changes.append(FieldChange(
                    field_path=field_path,
                    old_value=old_value,
                    new_value=None,
                    change_type=ChangeType.REMOVED,
                ))
            elif isinstance(old_value, dict) and isinstance(new_value, dict):
                self._diff_dicts(old_value, new_value, field_path, changes, ignore_position)
            elif old_value != new_value:
                changes.append(FieldChange(
                    field_path=field_path,
                    old_value=old_value,
                    new_value=new_value,
                    change_type=ChangeType.MODIFIED,
                ))

    def _diff_schemas(
        self,
        old_pipeline: Any,
        new_pipeline: Any,
        result: DiffResult,
    ) -> None:
        """Compare input/output schemas."""
        # Input schema
        old_input = self._schema_to_dict(getattr(old_pipeline, "input_schema", None))
        new_input = self._schema_to_dict(getattr(new_pipeline, "input_schema", None))
        if old_input != new_input:
            result.input_schema_changed = True
            self._diff_dicts(old_input, new_input, "", result.input_schema_changes, False)

        # Output schema
        old_output = self._schema_to_dict(getattr(old_pipeline, "output_schema", None))
        new_output = self._schema_to_dict(getattr(new_pipeline, "output_schema", None))
        if old_output != new_output:
            result.output_schema_changed = True
            self._diff_dicts(old_output, new_output, "", result.output_schema_changes, False)

    def _diff_dependencies(
        self,
        old_pipeline: Any,
        new_pipeline: Any,
        result: DiffResult,
    ) -> None:
        """Compare dependency graphs."""
        old_deps = self._extract_dependencies(old_pipeline)
        new_deps = self._extract_dependencies(new_pipeline)

        # Added dependencies
        for dep in new_deps - old_deps:
            result.dependency_changes.append((dep[0], dep[1], ChangeType.ADDED))

        # Removed dependencies
        for dep in old_deps - new_deps:
            result.dependency_changes.append((dep[0], dep[1], ChangeType.REMOVED))

    def _extract_dependencies(self, pipeline: Any) -> Set[Tuple[str, str]]:
        """Extract all dependency edges from a pipeline."""
        deps: Set[Tuple[str, str]] = set()
        stages = getattr(pipeline, "stages", [])
        for stage in stages:
            stage_id = getattr(stage, "id", None)
            depends_on = getattr(stage, "depends_on", [])
            for dep in depends_on:
                deps.add((dep, stage_id))
        return deps

    def _stage_to_dict(self, stage: Any) -> Dict[str, Any]:
        """Convert a stage object to a dictionary."""
        if hasattr(stage, "model_dump"):
            return stage.model_dump()
        elif hasattr(stage, "dict"):
            return stage.dict()
        elif isinstance(stage, dict):
            return stage
        else:
            # Fallback: extract common attributes
            return {
                "id": getattr(stage, "id", None),
                "component_type": getattr(stage, "component_type", None),
                "component": getattr(stage, "component", None),
                "config": getattr(stage, "config", {}),
                "input_mapping": getattr(stage, "input_mapping", {}),
                "depends_on": getattr(stage, "depends_on", []),
            }

    def _schema_to_dict(self, schema: Any) -> Dict[str, Any]:
        """Convert a schema object to a dictionary."""
        if schema is None:
            return {}
        if hasattr(schema, "model_dump"):
            return schema.model_dump()
        elif hasattr(schema, "dict"):
            return schema.dict()
        elif isinstance(schema, dict):
            return schema
        return {}
