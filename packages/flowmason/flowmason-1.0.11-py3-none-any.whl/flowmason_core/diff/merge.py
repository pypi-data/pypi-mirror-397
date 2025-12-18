"""
Three-Way Pipeline Merge for FlowMason.

Implements Git-style three-way merge for pipeline configurations.
"""

import copy
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from flowmason_core.diff.pipeline_diff import ChangeType, PipelineDiffer

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Type of merge conflict."""
    STAGE_MODIFIED_BOTH = "stage_modified_both"
    STAGE_REMOVED_MODIFIED = "stage_removed_modified"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    SCHEMA_CONFLICT = "schema_conflict"
    FIELD_CONFLICT = "field_conflict"


@dataclass
class MergeConflict:
    """A merge conflict that requires manual resolution."""
    conflict_type: ConflictType
    location: str  # e.g., "stages.transform", "input_schema.properties.name"
    base_value: Any
    ours_value: Any
    theirs_value: Any
    message: str

    def __str__(self) -> str:
        return f"CONFLICT ({self.conflict_type.value}): {self.location} - {self.message}"


@dataclass
class MergeResult:
    """Result of a three-way merge."""
    merged: Optional[Dict[str, Any]] = None
    conflicts: List[MergeConflict] = field(default_factory=list)
    auto_resolved: List[str] = field(default_factory=list)
    is_clean: bool = True

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


class ThreeWayMerger:
    """
    Implements three-way merge for pipeline configurations.

    Three-way merge uses a common ancestor (base) to determine
    which changes should be applied when merging two divergent
    versions (ours and theirs).

    Merge rules:
    - If only one side changed, take that change
    - If both sides made the same change, take it
    - If both sides made different changes, conflict
    - Deleted items + modifications = conflict
    """

    def __init__(self):
        self.differ = PipelineDiffer()

    def merge(
        self,
        base: Any,
        ours: Any,
        theirs: Any,
        favor: Optional[str] = None,
    ) -> MergeResult:
        """
        Perform a three-way merge.

        Args:
            base: The common ancestor
            ours: Our version (local changes)
            theirs: Their version (remote changes)
            favor: Conflict resolution strategy ("ours" or "theirs")

        Returns:
            MergeResult with merged pipeline or conflicts
        """
        result = MergeResult()

        # Compute diffs
        ours_diff = self.differ.diff(base, ours)
        theirs_diff = self.differ.diff(base, theirs)

        # Start with base as the merge target
        merged = self._to_dict(base)

        # Merge metadata
        self._merge_metadata(merged, base, ours, theirs, ours_diff, theirs_diff, result, favor)

        # Merge stages
        self._merge_stages(merged, base, ours, theirs, ours_diff, theirs_diff, result, favor)

        # Merge schemas
        self._merge_schemas(merged, base, ours, theirs, ours_diff, theirs_diff, result, favor)

        result.merged = merged if not result.has_conflicts else None
        result.is_clean = not result.has_conflicts

        return result

    def _merge_metadata(
        self,
        merged: Dict[str, Any],
        base: Any,
        ours: Any,
        theirs: Any,
        ours_diff: Any,
        theirs_diff: Any,
        result: MergeResult,
        favor: Optional[str],
    ) -> None:
        """Merge pipeline-level metadata."""
        # Name
        if ours_diff.name_changed and theirs_diff.name_changed:
            if ours_diff.new_name == theirs_diff.new_name:
                merged["name"] = ours_diff.new_name
                result.auto_resolved.append("name (same change)")
            elif favor:
                merged["name"] = ours_diff.new_name if favor == "ours" else theirs_diff.new_name
                result.auto_resolved.append(f"name (favoring {favor})")
            else:
                result.conflicts.append(MergeConflict(
                    conflict_type=ConflictType.FIELD_CONFLICT,
                    location="name",
                    base_value=ours_diff.old_name,
                    ours_value=ours_diff.new_name,
                    theirs_value=theirs_diff.new_name,
                    message="Both sides changed the pipeline name differently",
                ))
        elif ours_diff.name_changed:
            merged["name"] = ours_diff.new_name
        elif theirs_diff.name_changed:
            merged["name"] = theirs_diff.new_name

        # Version
        if ours_diff.version_changed and theirs_diff.version_changed:
            if ours_diff.new_version == theirs_diff.new_version:
                merged["version"] = ours_diff.new_version
            elif favor:
                merged["version"] = ours_diff.new_version if favor == "ours" else theirs_diff.new_version
            else:
                result.conflicts.append(MergeConflict(
                    conflict_type=ConflictType.FIELD_CONFLICT,
                    location="version",
                    base_value=ours_diff.old_version,
                    ours_value=ours_diff.new_version,
                    theirs_value=theirs_diff.new_version,
                    message="Both sides changed the version differently",
                ))
        elif ours_diff.version_changed:
            merged["version"] = ours_diff.new_version
        elif theirs_diff.version_changed:
            merged["version"] = theirs_diff.new_version

        # Description
        if ours_diff.description_changed and theirs_diff.description_changed:
            if ours_diff.new_description == theirs_diff.new_description:
                merged["description"] = ours_diff.new_description
            elif favor:
                merged["description"] = ours_diff.new_description if favor == "ours" else theirs_diff.new_description
            else:
                result.conflicts.append(MergeConflict(
                    conflict_type=ConflictType.FIELD_CONFLICT,
                    location="description",
                    base_value=ours_diff.old_description,
                    ours_value=ours_diff.new_description,
                    theirs_value=theirs_diff.new_description,
                    message="Both sides changed the description differently",
                ))
        elif ours_diff.description_changed:
            merged["description"] = ours_diff.new_description
        elif theirs_diff.description_changed:
            merged["description"] = theirs_diff.new_description

    def _merge_stages(
        self,
        merged: Dict[str, Any],
        base: Any,
        ours: Any,
        theirs: Any,
        ours_diff: Any,
        theirs_diff: Any,
        result: MergeResult,
        favor: Optional[str],
    ) -> None:
        """Merge pipeline stages."""
        # Build sets of changed stage IDs
        ours_added = {s.stage_id for s in ours_diff.added_stages}
        ours_removed = {s.stage_id for s in ours_diff.removed_stages}
        ours_modified = {s.stage_id for s in ours_diff.modified_stages}

        theirs_added = {s.stage_id for s in theirs_diff.added_stages}
        theirs_removed = {s.stage_id for s in theirs_diff.removed_stages}
        theirs_modified = {s.stage_id for s in theirs_diff.modified_stages}

        # Build stage maps
        base_stages = {s.id: s for s in getattr(base, "stages", []) if hasattr(s, "id")}
        ours_stages = {s.id: s for s in getattr(ours, "stages", []) if hasattr(s, "id")}
        theirs_stages = {s.id: s for s in getattr(theirs, "stages", []) if hasattr(s, "id")}

        merged_stages: List[Dict[str, Any]] = []
        processed_ids: Set[str] = set()

        # Process all stage IDs
        all_ids = set(base_stages.keys()) | set(ours_stages.keys()) | set(theirs_stages.keys())

        for stage_id in all_ids:
            processed_ids.add(stage_id)

            in_ours_added = stage_id in ours_added
            in_theirs_added = stage_id in theirs_added
            in_ours_removed = stage_id in ours_removed
            in_theirs_removed = stage_id in theirs_removed
            in_ours_modified = stage_id in ours_modified
            in_theirs_modified = stage_id in theirs_modified

            # Both added same stage (possibly differently)
            if in_ours_added and in_theirs_added:
                ours_stage = self._stage_to_dict(ours_stages[stage_id])
                theirs_stage = self._stage_to_dict(theirs_stages[stage_id])
                if ours_stage == theirs_stage:
                    merged_stages.append(ours_stage)
                    result.auto_resolved.append(f"stages.{stage_id} (both added same)")
                elif favor:
                    merged_stages.append(ours_stage if favor == "ours" else theirs_stage)
                    result.auto_resolved.append(f"stages.{stage_id} (favoring {favor})")
                else:
                    result.conflicts.append(MergeConflict(
                        conflict_type=ConflictType.STAGE_MODIFIED_BOTH,
                        location=f"stages.{stage_id}",
                        base_value=None,
                        ours_value=ours_stage,
                        theirs_value=theirs_stage,
                        message=f"Both sides added stage '{stage_id}' with different configs",
                    ))

            # Only ours added
            elif in_ours_added:
                merged_stages.append(self._stage_to_dict(ours_stages[stage_id]))

            # Only theirs added
            elif in_theirs_added:
                merged_stages.append(self._stage_to_dict(theirs_stages[stage_id]))

            # Both removed
            elif in_ours_removed and in_theirs_removed:
                # Stage is removed in both - don't add to merged
                result.auto_resolved.append(f"stages.{stage_id} (both removed)")

            # Ours removed, theirs modified
            elif in_ours_removed and in_theirs_modified:
                if favor == "ours":
                    result.auto_resolved.append(f"stages.{stage_id} (removed, favoring ours)")
                elif favor == "theirs":
                    merged_stages.append(self._stage_to_dict(theirs_stages[stage_id]))
                    result.auto_resolved.append(f"stages.{stage_id} (kept modified, favoring theirs)")
                else:
                    result.conflicts.append(MergeConflict(
                        conflict_type=ConflictType.STAGE_REMOVED_MODIFIED,
                        location=f"stages.{stage_id}",
                        base_value=self._stage_to_dict(base_stages[stage_id]),
                        ours_value=None,
                        theirs_value=self._stage_to_dict(theirs_stages[stage_id]),
                        message=f"We removed '{stage_id}' but they modified it",
                    ))

            # Theirs removed, ours modified
            elif in_theirs_removed and in_ours_modified:
                if favor == "theirs":
                    result.auto_resolved.append(f"stages.{stage_id} (removed, favoring theirs)")
                elif favor == "ours":
                    merged_stages.append(self._stage_to_dict(ours_stages[stage_id]))
                    result.auto_resolved.append(f"stages.{stage_id} (kept modified, favoring ours)")
                else:
                    result.conflicts.append(MergeConflict(
                        conflict_type=ConflictType.STAGE_REMOVED_MODIFIED,
                        location=f"stages.{stage_id}",
                        base_value=self._stage_to_dict(base_stages[stage_id]),
                        ours_value=self._stage_to_dict(ours_stages[stage_id]),
                        theirs_value=None,
                        message=f"They removed '{stage_id}' but we modified it",
                    ))

            # Only ours removed
            elif in_ours_removed:
                # Stage is removed - don't add to merged
                pass

            # Only theirs removed
            elif in_theirs_removed:
                # Stage is removed - don't add to merged
                pass

            # Both modified
            elif in_ours_modified and in_theirs_modified:
                ours_stage = self._stage_to_dict(ours_stages[stage_id])
                theirs_stage = self._stage_to_dict(theirs_stages[stage_id])
                if ours_stage == theirs_stage:
                    merged_stages.append(ours_stage)
                    result.auto_resolved.append(f"stages.{stage_id} (same modification)")
                elif favor:
                    merged_stages.append(ours_stage if favor == "ours" else theirs_stage)
                    result.auto_resolved.append(f"stages.{stage_id} (favoring {favor})")
                else:
                    result.conflicts.append(MergeConflict(
                        conflict_type=ConflictType.STAGE_MODIFIED_BOTH,
                        location=f"stages.{stage_id}",
                        base_value=self._stage_to_dict(base_stages[stage_id]),
                        ours_value=ours_stage,
                        theirs_value=theirs_stage,
                        message=f"Both sides modified stage '{stage_id}' differently",
                    ))

            # Only ours modified
            elif in_ours_modified:
                merged_stages.append(self._stage_to_dict(ours_stages[stage_id]))

            # Only theirs modified
            elif in_theirs_modified:
                merged_stages.append(self._stage_to_dict(theirs_stages[stage_id]))

            # Unchanged
            else:
                if stage_id in base_stages:
                    merged_stages.append(self._stage_to_dict(base_stages[stage_id]))

        merged["stages"] = merged_stages

    def _merge_schemas(
        self,
        merged: Dict[str, Any],
        base: Any,
        ours: Any,
        theirs: Any,
        ours_diff: Any,
        theirs_diff: Any,
        result: MergeResult,
        favor: Optional[str],
    ) -> None:
        """Merge input/output schemas."""
        # Input schema
        if ours_diff.input_schema_changed and theirs_diff.input_schema_changed:
            ours_schema = self._schema_to_dict(getattr(ours, "input_schema", None))
            theirs_schema = self._schema_to_dict(getattr(theirs, "input_schema", None))
            if ours_schema == theirs_schema:
                merged["input_schema"] = ours_schema
                result.auto_resolved.append("input_schema (same change)")
            elif favor:
                merged["input_schema"] = ours_schema if favor == "ours" else theirs_schema
                result.auto_resolved.append(f"input_schema (favoring {favor})")
            else:
                result.conflicts.append(MergeConflict(
                    conflict_type=ConflictType.SCHEMA_CONFLICT,
                    location="input_schema",
                    base_value=self._schema_to_dict(getattr(base, "input_schema", None)),
                    ours_value=ours_schema,
                    theirs_value=theirs_schema,
                    message="Both sides changed input_schema differently",
                ))
        elif ours_diff.input_schema_changed:
            merged["input_schema"] = self._schema_to_dict(getattr(ours, "input_schema", None))
        elif theirs_diff.input_schema_changed:
            merged["input_schema"] = self._schema_to_dict(getattr(theirs, "input_schema", None))

        # Output schema
        if ours_diff.output_schema_changed and theirs_diff.output_schema_changed:
            ours_schema = self._schema_to_dict(getattr(ours, "output_schema", None))
            theirs_schema = self._schema_to_dict(getattr(theirs, "output_schema", None))
            if ours_schema == theirs_schema:
                merged["output_schema"] = ours_schema
                result.auto_resolved.append("output_schema (same change)")
            elif favor:
                merged["output_schema"] = ours_schema if favor == "ours" else theirs_schema
                result.auto_resolved.append(f"output_schema (favoring {favor})")
            else:
                result.conflicts.append(MergeConflict(
                    conflict_type=ConflictType.SCHEMA_CONFLICT,
                    location="output_schema",
                    base_value=self._schema_to_dict(getattr(base, "output_schema", None)),
                    ours_value=ours_schema,
                    theirs_value=theirs_schema,
                    message="Both sides changed output_schema differently",
                ))
        elif ours_diff.output_schema_changed:
            merged["output_schema"] = self._schema_to_dict(getattr(ours, "output_schema", None))
        elif theirs_diff.output_schema_changed:
            merged["output_schema"] = self._schema_to_dict(getattr(theirs, "output_schema", None))

    def _to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert an object to a dictionary."""
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "dict"):
            return obj.dict()
        elif isinstance(obj, dict):
            return copy.deepcopy(obj)
        return {}

    def _stage_to_dict(self, stage: Any) -> Dict[str, Any]:
        """Convert a stage to a dictionary."""
        if hasattr(stage, "model_dump"):
            return stage.model_dump()
        elif hasattr(stage, "dict"):
            return stage.dict()
        elif isinstance(stage, dict):
            return stage
        return {}

    def _schema_to_dict(self, schema: Any) -> Dict[str, Any]:
        """Convert a schema to a dictionary."""
        if schema is None:
            return {}
        if hasattr(schema, "model_dump"):
            return schema.model_dump()
        elif hasattr(schema, "dict"):
            return schema.dict()
        elif isinstance(schema, dict):
            return schema
        return {}
