"""
Pipeline Diff & Merge Service.

Provides diffing and merging capabilities for pipelines.
"""

import uuid
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Tuple

from flowmason_studio.models.diff import (
    ChangeType,
    ConflictResolution,
    ConflictType,
    FieldChange,
    MergeConflict,
    MergeResult,
    PipelineDiff,
    SettingsChange,
    StageChange,
    VariableChange,
)


class DiffService:
    """Service for computing and applying pipeline diffs."""

    def __init__(self):
        self._merge_sessions: Dict[str, Dict] = {}

    def compute_diff(
        self,
        base: Dict[str, Any],
        compare: Dict[str, Any],
        include_unchanged: bool = False,
    ) -> PipelineDiff:
        """
        Compute the diff between two pipeline versions.

        Args:
            base: The base/original pipeline
            compare: The pipeline to compare against
            include_unchanged: Whether to include unchanged items

        Returns:
            PipelineDiff with all detected changes
        """
        diff = PipelineDiff(
            base_id=base.get("id", "base"),
            compare_id=compare.get("id", "compare"),
        )

        # Check metadata changes
        if base.get("name") != compare.get("name"):
            diff.name_changed = True
            diff.old_name = base.get("name")
            diff.new_name = compare.get("name")

        if base.get("description") != compare.get("description"):
            diff.description_changed = True
            diff.old_description = base.get("description")
            diff.new_description = compare.get("description")

        # Diff stages
        diff.stage_changes = self._diff_stages(
            base.get("stages", []),
            compare.get("stages", []),
            include_unchanged,
        )

        # Diff variables
        diff.variable_changes = self._diff_variables(
            base.get("variables", {}),
            compare.get("variables", {}),
            include_unchanged,
        )

        # Diff settings
        diff.settings_changes = self._diff_settings(
            base.get("settings", {}),
            compare.get("settings", {}),
            include_unchanged,
        )

        # Compute totals
        diff.total_changes = (
            len([c for c in diff.stage_changes if c.change_type != ChangeType.UNCHANGED])
            + len([c for c in diff.variable_changes if c.change_type != ChangeType.UNCHANGED])
            + len([c for c in diff.settings_changes if c.change_type != ChangeType.UNCHANGED])
            + (1 if diff.name_changed else 0)
            + (1 if diff.description_changed else 0)
        )
        diff.has_changes = diff.total_changes > 0

        return diff

    def _diff_stages(
        self,
        base_stages: List[Dict],
        compare_stages: List[Dict],
        include_unchanged: bool,
    ) -> List[StageChange]:
        """Diff pipeline stages."""
        changes = []

        # Build lookup maps
        base_map = {s["id"]: (i, s) for i, s in enumerate(base_stages)}
        compare_map = {s["id"]: (i, s) for i, s in enumerate(compare_stages)}

        base_ids = set(base_map.keys())
        compare_ids = set(compare_map.keys())

        # Find removed stages
        for stage_id in base_ids - compare_ids:
            pos, stage = base_map[stage_id]
            changes.append(StageChange(
                stage_id=stage_id,
                stage_name=stage.get("name", stage_id),
                change_type=ChangeType.REMOVED,
                old_position=pos,
                stage_data=stage,
            ))

        # Find added stages
        for stage_id in compare_ids - base_ids:
            pos, stage = compare_map[stage_id]
            changes.append(StageChange(
                stage_id=stage_id,
                stage_name=stage.get("name", stage_id),
                change_type=ChangeType.ADDED,
                new_position=pos,
                stage_data=stage,
            ))

        # Find modified/moved stages
        for stage_id in base_ids & compare_ids:
            base_pos, base_stage = base_map[stage_id]
            compare_pos, compare_stage = compare_map[stage_id]

            field_changes = self._diff_stage_fields(base_stage, compare_stage)
            position_changed = base_pos != compare_pos

            if field_changes or position_changed:
                change_type = ChangeType.MODIFIED
                if position_changed and not field_changes:
                    change_type = ChangeType.MOVED

                changes.append(StageChange(
                    stage_id=stage_id,
                    stage_name=compare_stage.get("name", stage_id),
                    change_type=change_type,
                    field_changes=field_changes,
                    old_position=base_pos if position_changed else None,
                    new_position=compare_pos if position_changed else None,
                ))
            elif include_unchanged:
                changes.append(StageChange(
                    stage_id=stage_id,
                    stage_name=compare_stage.get("name", stage_id),
                    change_type=ChangeType.UNCHANGED,
                ))

        return changes

    def _diff_stage_fields(
        self,
        base: Dict,
        compare: Dict,
    ) -> List[FieldChange]:
        """Diff individual fields within a stage."""
        changes = []

        # Fields to compare
        fields = ["name", "component_type", "depends_on", "enabled"]

        for field in fields:
            old_val = base.get(field)
            new_val = compare.get(field)

            if old_val != new_val:
                if old_val is None:
                    change_type = ChangeType.ADDED
                elif new_val is None:
                    change_type = ChangeType.REMOVED
                else:
                    change_type = ChangeType.MODIFIED

                changes.append(FieldChange(
                    field=field,
                    change_type=change_type,
                    old_value=old_val,
                    new_value=new_val,
                ))

        # Deep diff config
        config_changes = self._diff_nested(
            base.get("config", {}),
            compare.get("config", {}),
            "config",
        )
        changes.extend(config_changes)

        return changes

    def _diff_nested(
        self,
        base: Dict,
        compare: Dict,
        prefix: str,
    ) -> List[FieldChange]:
        """Recursively diff nested dictionaries."""
        changes = []

        all_keys = set(base.keys()) | set(compare.keys())

        for key in all_keys:
            path = f"{prefix}.{key}"
            old_val = base.get(key)
            new_val = compare.get(key)

            if old_val == new_val:
                continue

            if isinstance(old_val, dict) and isinstance(new_val, dict):
                # Recurse into nested dicts
                changes.extend(self._diff_nested(old_val, new_val, path))
            else:
                if old_val is None:
                    change_type = ChangeType.ADDED
                elif new_val is None:
                    change_type = ChangeType.REMOVED
                else:
                    change_type = ChangeType.MODIFIED

                changes.append(FieldChange(
                    field=path,
                    change_type=change_type,
                    old_value=old_val,
                    new_value=new_val,
                ))

        return changes

    def _diff_variables(
        self,
        base: Dict,
        compare: Dict,
        include_unchanged: bool,
    ) -> List[VariableChange]:
        """Diff pipeline variables."""
        changes = []
        all_vars = set(base.keys()) | set(compare.keys())

        for var_name in all_vars:
            old_val = base.get(var_name)
            new_val = compare.get(var_name)

            if old_val == new_val:
                if include_unchanged:
                    changes.append(VariableChange(
                        variable_name=var_name,
                        change_type=ChangeType.UNCHANGED,
                        old_value=old_val,
                        new_value=new_val,
                    ))
                continue

            if old_val is None:
                change_type = ChangeType.ADDED
            elif new_val is None:
                change_type = ChangeType.REMOVED
            else:
                change_type = ChangeType.MODIFIED

            changes.append(VariableChange(
                variable_name=var_name,
                change_type=change_type,
                old_value=old_val,
                new_value=new_val,
            ))

        return changes

    def _diff_settings(
        self,
        base: Dict,
        compare: Dict,
        include_unchanged: bool,
    ) -> List[SettingsChange]:
        """Diff pipeline settings."""
        changes = []

        def flatten_settings(d: Dict, prefix: str = "") -> Dict[str, Any]:
            """Flatten nested settings to dot-notation paths."""
            result = {}
            for key, value in d.items():
                path = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    result.update(flatten_settings(value, path))
                else:
                    result[path] = value
            return result

        base_flat = flatten_settings(base)
        compare_flat = flatten_settings(compare)
        all_paths = set(base_flat.keys()) | set(compare_flat.keys())

        for path in all_paths:
            old_val = base_flat.get(path)
            new_val = compare_flat.get(path)

            if old_val == new_val:
                if include_unchanged:
                    changes.append(SettingsChange(
                        setting_path=path,
                        change_type=ChangeType.UNCHANGED,
                        old_value=old_val,
                        new_value=new_val,
                    ))
                continue

            if old_val is None:
                change_type = ChangeType.ADDED
            elif new_val is None:
                change_type = ChangeType.REMOVED
            else:
                change_type = ChangeType.MODIFIED

            changes.append(SettingsChange(
                setting_path=path,
                change_type=change_type,
                old_value=old_val,
                new_value=new_val,
            ))

        return changes

    def three_way_merge(
        self,
        base: Dict[str, Any],
        ours: Dict[str, Any],
        theirs: Dict[str, Any],
        resolutions: Optional[Dict[str, ConflictResolution]] = None,
        manual_values: Optional[Dict[str, Any]] = None,
        auto_resolve: bool = True,
        prefer_ours: bool = False,
    ) -> MergeResult:
        """
        Perform a three-way merge of pipelines.

        Args:
            base: Common ancestor
            ours: Our version
            theirs: Their version
            resolutions: Pre-specified conflict resolutions
            manual_values: Manual values for conflicts
            auto_resolve: Whether to auto-resolve non-conflicts
            prefer_ours: Prefer our changes when auto-resolving

        Returns:
            MergeResult with merged pipeline or conflicts
        """
        resolutions = resolutions or {}
        manual_values = manual_values or {}

        merged = deepcopy(base)
        conflicts: List[MergeConflict] = []
        auto_merged = 0

        # Compute diffs
        ours_diff = self.compute_diff(base, ours)
        theirs_diff = self.compute_diff(base, theirs)

        # Merge metadata
        merged, meta_conflicts, meta_auto = self._merge_metadata(
            base, ours, theirs, ours_diff, theirs_diff, resolutions, prefer_ours
        )
        conflicts.extend(meta_conflicts)
        auto_merged += meta_auto

        # Merge stages
        merged["stages"], stage_conflicts, stage_auto = self._merge_stages(
            base.get("stages", []),
            ours.get("stages", []),
            theirs.get("stages", []),
            resolutions,
            manual_values,
            prefer_ours,
        )
        conflicts.extend(stage_conflicts)
        auto_merged += stage_auto

        # Merge variables
        merged["variables"], var_conflicts, var_auto = self._merge_dict(
            base.get("variables", {}),
            ours.get("variables", {}),
            theirs.get("variables", {}),
            "variable",
            resolutions,
            manual_values,
            prefer_ours,
        )
        conflicts.extend(var_conflicts)
        auto_merged += var_auto

        # Merge settings
        merged["settings"], settings_conflicts, settings_auto = self._merge_dict(
            base.get("settings", {}),
            ours.get("settings", {}),
            theirs.get("settings", {}),
            "setting",
            resolutions,
            manual_values,
            prefer_ours,
        )
        conflicts.extend(settings_conflicts)
        auto_merged += settings_auto

        # Resolve any pre-specified conflicts
        for conflict in conflicts:
            if conflict.id in resolutions:
                conflict.resolution = resolutions[conflict.id]
                if conflict.resolution == ConflictResolution.MANUAL:
                    conflict.resolved_value = manual_values.get(conflict.id)
                elif conflict.resolution == ConflictResolution.USE_OURS:
                    conflict.resolved_value = conflict.ours_value
                elif conflict.resolution == ConflictResolution.USE_THEIRS:
                    conflict.resolved_value = conflict.theirs_value

        has_unresolved = any(c.resolution is None for c in conflicts)

        return MergeResult(
            success=not has_unresolved,
            merged_pipeline=merged if not has_unresolved else None,
            conflicts=conflicts,
            has_conflicts=len(conflicts) > 0,
            auto_merged_changes=auto_merged,
        )

    def _merge_metadata(
        self,
        base: Dict,
        ours: Dict,
        theirs: Dict,
        ours_diff: PipelineDiff,
        theirs_diff: PipelineDiff,
        resolutions: Dict[str, ConflictResolution],
        prefer_ours: bool,
    ) -> Tuple[Dict, List[MergeConflict], int]:
        """Merge pipeline metadata (name, description)."""
        merged = deepcopy(base)
        conflicts = []
        auto_merged = 0

        # Merge name
        if ours_diff.name_changed and theirs_diff.name_changed:
            if ours_diff.new_name != theirs_diff.new_name:
                conflict_id = "meta:name"
                if conflict_id in resolutions:
                    resolution = resolutions[conflict_id]
                    if resolution == ConflictResolution.USE_OURS:
                        merged["name"] = ours_diff.new_name
                    else:
                        merged["name"] = theirs_diff.new_name
                else:
                    conflicts.append(MergeConflict(
                        id=conflict_id,
                        conflict_type=ConflictType.BOTH_MODIFIED,
                        location="metadata.name",
                        base_value=base.get("name"),
                        ours_value=ours_diff.new_name,
                        theirs_value=theirs_diff.new_name,
                        description="Both versions changed the pipeline name",
                    ))
            else:
                merged["name"] = ours_diff.new_name
                auto_merged += 1
        elif ours_diff.name_changed:
            merged["name"] = ours_diff.new_name
            auto_merged += 1
        elif theirs_diff.name_changed:
            merged["name"] = theirs_diff.new_name
            auto_merged += 1

        # Merge description
        if ours_diff.description_changed and theirs_diff.description_changed:
            if ours_diff.new_description != theirs_diff.new_description:
                conflict_id = "meta:description"
                if conflict_id in resolutions:
                    resolution = resolutions[conflict_id]
                    if resolution == ConflictResolution.USE_OURS:
                        merged["description"] = ours_diff.new_description
                    else:
                        merged["description"] = theirs_diff.new_description
                else:
                    conflicts.append(MergeConflict(
                        id=conflict_id,
                        conflict_type=ConflictType.BOTH_MODIFIED,
                        location="metadata.description",
                        base_value=base.get("description"),
                        ours_value=ours_diff.new_description,
                        theirs_value=theirs_diff.new_description,
                        description="Both versions changed the pipeline description",
                    ))
            else:
                merged["description"] = ours_diff.new_description
                auto_merged += 1
        elif ours_diff.description_changed:
            merged["description"] = ours_diff.new_description
            auto_merged += 1
        elif theirs_diff.description_changed:
            merged["description"] = theirs_diff.new_description
            auto_merged += 1

        return merged, conflicts, auto_merged

    def _merge_stages(
        self,
        base_stages: List[Dict],
        ours_stages: List[Dict],
        theirs_stages: List[Dict],
        resolutions: Dict[str, ConflictResolution],
        manual_values: Dict[str, Any],
        prefer_ours: bool,
    ) -> Tuple[List[Dict], List[MergeConflict], int]:
        """Merge pipeline stages."""
        conflicts = []
        auto_merged = 0

        # Build maps
        base_map = {s["id"]: s for s in base_stages}
        ours_map = {s["id"]: s for s in ours_stages}
        theirs_map = {s["id"]: s for s in theirs_stages}

        base_ids = set(base_map.keys())
        ours_ids = set(ours_map.keys())
        theirs_ids = set(theirs_map.keys())

        merged_stages = []

        # Handle stages in all three versions
        all_ids = base_ids | ours_ids | theirs_ids

        for stage_id in all_ids:
            in_base = stage_id in base_ids
            in_ours = stage_id in ours_ids
            in_theirs = stage_id in theirs_ids

            if in_base and in_ours and in_theirs:
                # Stage exists in all three - check for modifications
                base_stage = base_map[stage_id]
                ours_stage = ours_map[stage_id]
                theirs_stage = theirs_map[stage_id]

                ours_changed = ours_stage != base_stage
                theirs_changed = theirs_stage != base_stage

                if ours_changed and theirs_changed:
                    if ours_stage == theirs_stage:
                        # Same change in both - use it
                        merged_stages.append(deepcopy(ours_stage))
                        auto_merged += 1
                    else:
                        # Different changes - conflict
                        conflict_id = f"stage:{stage_id}"
                        if conflict_id in resolutions:
                            resolution = resolutions[conflict_id]
                            if resolution == ConflictResolution.USE_OURS:
                                merged_stages.append(deepcopy(ours_stage))
                            elif resolution == ConflictResolution.USE_THEIRS:
                                merged_stages.append(deepcopy(theirs_stage))
                            elif resolution == ConflictResolution.MANUAL:
                                merged_stages.append(manual_values.get(conflict_id, base_stage))
                        else:
                            conflicts.append(MergeConflict(
                                id=conflict_id,
                                conflict_type=ConflictType.BOTH_MODIFIED,
                                location=f"stage:{stage_id}",
                                base_value=base_stage,
                                ours_value=ours_stage,
                                theirs_value=theirs_stage,
                                description=f"Stage '{stage_id}' modified differently in both versions",
                            ))
                            merged_stages.append(deepcopy(base_stage))  # Keep base for now
                elif ours_changed:
                    merged_stages.append(deepcopy(ours_stage))
                    auto_merged += 1
                elif theirs_changed:
                    merged_stages.append(deepcopy(theirs_stage))
                    auto_merged += 1
                else:
                    merged_stages.append(deepcopy(base_stage))

            elif in_base and in_ours and not in_theirs:
                # Deleted in theirs
                ours_changed = ours_map[stage_id] != base_map[stage_id]
                if ours_changed:
                    # Modified in ours, deleted in theirs - conflict
                    conflict_id = f"stage:{stage_id}:delete"
                    if conflict_id in resolutions:
                        if resolutions[conflict_id] == ConflictResolution.USE_OURS:
                            merged_stages.append(deepcopy(ours_map[stage_id]))
                        # USE_THEIRS means delete, so don't add
                    else:
                        conflicts.append(MergeConflict(
                            id=conflict_id,
                            conflict_type=ConflictType.MODIFY_DELETE,
                            location=f"stage:{stage_id}",
                            base_value=base_map[stage_id],
                            ours_value=ours_map[stage_id],
                            theirs_value=None,
                            description=f"Stage '{stage_id}' modified in ours but deleted in theirs",
                        ))
                        merged_stages.append(deepcopy(ours_map[stage_id]))
                # If not modified in ours, accept deletion

            elif in_base and not in_ours and in_theirs:
                # Deleted in ours
                theirs_changed = theirs_map[stage_id] != base_map[stage_id]
                if theirs_changed:
                    conflict_id = f"stage:{stage_id}:delete"
                    if conflict_id in resolutions:
                        if resolutions[conflict_id] == ConflictResolution.USE_THEIRS:
                            merged_stages.append(deepcopy(theirs_map[stage_id]))
                    else:
                        conflicts.append(MergeConflict(
                            id=conflict_id,
                            conflict_type=ConflictType.MODIFY_DELETE,
                            location=f"stage:{stage_id}",
                            base_value=base_map[stage_id],
                            ours_value=None,
                            theirs_value=theirs_map[stage_id],
                            description=f"Stage '{stage_id}' deleted in ours but modified in theirs",
                        ))

            elif not in_base and in_ours and in_theirs:
                # Added in both
                if ours_map[stage_id] == theirs_map[stage_id]:
                    merged_stages.append(deepcopy(ours_map[stage_id]))
                    auto_merged += 1
                else:
                    conflict_id = f"stage:{stage_id}:add"
                    if conflict_id in resolutions:
                        if resolutions[conflict_id] == ConflictResolution.USE_OURS:
                            merged_stages.append(deepcopy(ours_map[stage_id]))
                        elif resolutions[conflict_id] == ConflictResolution.USE_THEIRS:
                            merged_stages.append(deepcopy(theirs_map[stage_id]))
                        elif resolutions[conflict_id] == ConflictResolution.USE_BOTH:
                            merged_stages.append(deepcopy(ours_map[stage_id]))
                            theirs_copy = deepcopy(theirs_map[stage_id])
                            theirs_copy["id"] = f"{stage_id}_theirs"
                            merged_stages.append(theirs_copy)
                    else:
                        conflicts.append(MergeConflict(
                            id=conflict_id,
                            conflict_type=ConflictType.ADD_ADD,
                            location=f"stage:{stage_id}",
                            ours_value=ours_map[stage_id],
                            theirs_value=theirs_map[stage_id],
                            description=f"Stage '{stage_id}' added differently in both versions",
                        ))
                        merged_stages.append(deepcopy(ours_map[stage_id]))

            elif not in_base and in_ours and not in_theirs:
                # Added only in ours
                merged_stages.append(deepcopy(ours_map[stage_id]))
                auto_merged += 1

            elif not in_base and not in_ours and in_theirs:
                # Added only in theirs
                merged_stages.append(deepcopy(theirs_map[stage_id]))
                auto_merged += 1

        return merged_stages, conflicts, auto_merged

    def _merge_dict(
        self,
        base: Dict,
        ours: Dict,
        theirs: Dict,
        item_type: str,
        resolutions: Dict[str, ConflictResolution],
        manual_values: Dict[str, Any],
        prefer_ours: bool,
    ) -> Tuple[Dict, List[MergeConflict], int]:
        """Merge dictionary (variables or settings)."""
        merged = deepcopy(base)
        conflicts = []
        auto_merged = 0

        all_keys = set(base.keys()) | set(ours.keys()) | set(theirs.keys())

        for key in all_keys:
            in_base = key in base
            in_ours = key in ours
            in_theirs = key in theirs

            base_val = base.get(key)
            ours_val = ours.get(key)
            theirs_val = theirs.get(key)

            if in_base and in_ours and in_theirs:
                ours_changed = ours_val != base_val
                theirs_changed = theirs_val != base_val

                if ours_changed and theirs_changed:
                    if ours_val == theirs_val:
                        merged[key] = ours_val
                        auto_merged += 1
                    else:
                        conflict_id = f"{item_type}:{key}"
                        if conflict_id in resolutions:
                            if resolutions[conflict_id] == ConflictResolution.USE_OURS:
                                merged[key] = ours_val
                            elif resolutions[conflict_id] == ConflictResolution.USE_THEIRS:
                                merged[key] = theirs_val
                            elif resolutions[conflict_id] == ConflictResolution.MANUAL:
                                merged[key] = manual_values.get(conflict_id, base_val)
                        else:
                            conflicts.append(MergeConflict(
                                id=conflict_id,
                                conflict_type=ConflictType.BOTH_MODIFIED,
                                location=f"{item_type}:{key}",
                                base_value=base_val,
                                ours_value=ours_val,
                                theirs_value=theirs_val,
                                description=f"{item_type.title()} '{key}' modified differently",
                            ))
                elif ours_changed:
                    merged[key] = ours_val
                    auto_merged += 1
                elif theirs_changed:
                    merged[key] = theirs_val
                    auto_merged += 1

            elif in_ours and not in_theirs:
                if in_base:
                    # Deleted in theirs
                    if ours_val != base_val:
                        # Modified in ours - conflict
                        conflict_id = f"{item_type}:{key}:delete"
                        conflicts.append(MergeConflict(
                            id=conflict_id,
                            conflict_type=ConflictType.MODIFY_DELETE,
                            location=f"{item_type}:{key}",
                            base_value=base_val,
                            ours_value=ours_val,
                            theirs_value=None,
                        ))
                        merged[key] = ours_val
                    else:
                        # Accept deletion
                        merged.pop(key, None)
                else:
                    # Added in ours
                    merged[key] = ours_val
                    auto_merged += 1

            elif not in_ours and in_theirs:
                if in_base:
                    # Deleted in ours
                    if theirs_val != base_val:
                        conflict_id = f"{item_type}:{key}:delete"
                        conflicts.append(MergeConflict(
                            id=conflict_id,
                            conflict_type=ConflictType.MODIFY_DELETE,
                            location=f"{item_type}:{key}",
                            base_value=base_val,
                            ours_value=None,
                            theirs_value=theirs_val,
                        ))
                    # Keep deleted
                    merged.pop(key, None)
                else:
                    # Added in theirs
                    merged[key] = theirs_val
                    auto_merged += 1

            elif not in_ours and not in_theirs and in_base:
                # Deleted in both
                merged.pop(key, None)
                auto_merged += 1

        return merged, conflicts, auto_merged

    def generate_visual_diff(
        self,
        diff: PipelineDiff,
        side_by_side: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a visual representation of the diff for UI rendering.

        Returns a structure suitable for rendering in a diff viewer.
        """
        visual = {
            "format": "side_by_side" if side_by_side else "unified",
            "summary": {
                "total_changes": diff.total_changes,
                "stages_added": len([c for c in diff.stage_changes if c.change_type == ChangeType.ADDED]),
                "stages_removed": len([c for c in diff.stage_changes if c.change_type == ChangeType.REMOVED]),
                "stages_modified": len([c for c in diff.stage_changes if c.change_type == ChangeType.MODIFIED]),
                "variables_changed": len([c for c in diff.variable_changes if c.change_type != ChangeType.UNCHANGED]),
                "settings_changed": len([c for c in diff.settings_changes if c.change_type != ChangeType.UNCHANGED]),
            },
            "sections": [],
        }

        # Metadata section
        if diff.name_changed or diff.description_changed:
            visual["sections"].append({
                "type": "metadata",
                "title": "Pipeline Metadata",
                "changes": [
                    *([{
                        "field": "name",
                        "old": diff.old_name,
                        "new": diff.new_name,
                        "change_type": "modified",
                    }] if diff.name_changed else []),
                    *([{
                        "field": "description",
                        "old": diff.old_description,
                        "new": diff.new_description,
                        "change_type": "modified",
                    }] if diff.description_changed else []),
                ],
            })

        # Stages section
        if diff.stage_changes:
            stage_section = {
                "type": "stages",
                "title": "Stages",
                "items": [],
            }
            for change in diff.stage_changes:
                item = {
                    "id": change.stage_id,
                    "name": change.stage_name,
                    "change_type": change.change_type.value,
                }
                if change.change_type == ChangeType.MODIFIED:
                    item["field_changes"] = [
                        {
                            "field": fc.field,
                            "old": fc.old_value,
                            "new": fc.new_value,
                            "type": fc.change_type.value,
                        }
                        for fc in change.field_changes
                    ]
                if change.stage_data:
                    item["data"] = change.stage_data
                if change.old_position is not None:
                    item["old_position"] = change.old_position
                if change.new_position is not None:
                    item["new_position"] = change.new_position

                stage_section["items"].append(item)

            visual["sections"].append(stage_section)

        # Variables section
        if diff.variable_changes:
            visual["sections"].append({
                "type": "variables",
                "title": "Variables",
                "items": [
                    {
                        "name": vc.variable_name,
                        "change_type": vc.change_type.value,
                        "old": vc.old_value,
                        "new": vc.new_value,
                    }
                    for vc in diff.variable_changes
                ],
            })

        # Settings section
        if diff.settings_changes:
            visual["sections"].append({
                "type": "settings",
                "title": "Settings",
                "items": [
                    {
                        "path": sc.setting_path,
                        "change_type": sc.change_type.value,
                        "old": sc.old_value,
                        "new": sc.new_value,
                    }
                    for sc in diff.settings_changes
                ],
            })

        return visual

    def apply_diff(
        self,
        target: Dict[str, Any],
        diff: PipelineDiff,
    ) -> Dict[str, Any]:
        """
        Apply a diff to a target pipeline.

        Returns a new pipeline with the diff applied.
        """
        result = deepcopy(target)

        # Apply name change
        if diff.name_changed and diff.new_name:
            result["name"] = diff.new_name

        # Apply description change
        if diff.description_changed and diff.new_description:
            result["description"] = diff.new_description

        # Apply stage changes
        stages = result.get("stages", [])
        stage_map = {s["id"]: s for s in stages}

        for change in diff.stage_changes:
            if change.change_type == ChangeType.REMOVED:
                stage_map.pop(change.stage_id, None)
            elif change.change_type == ChangeType.ADDED and change.stage_data:
                stage_map[change.stage_id] = change.stage_data
            elif change.change_type == ChangeType.MODIFIED:
                if change.stage_id in stage_map:
                    for fc in change.field_changes:
                        self._apply_field_change(stage_map[change.stage_id], fc)

        result["stages"] = list(stage_map.values())

        # Apply variable changes
        variables = result.get("variables", {})
        for vc in diff.variable_changes:
            if vc.change_type == ChangeType.REMOVED:
                variables.pop(vc.variable_name, None)
            elif vc.change_type in (ChangeType.ADDED, ChangeType.MODIFIED):
                variables[vc.variable_name] = vc.new_value

        result["variables"] = variables

        # Apply settings changes
        settings = result.get("settings", {})
        for sc in diff.settings_changes:
            parts = sc.setting_path.split(".")
            self._set_nested(settings, parts, sc.new_value, sc.change_type)

        result["settings"] = settings

        return result

    def _apply_field_change(self, stage: Dict, change: FieldChange) -> None:
        """Apply a field change to a stage."""
        parts = change.field.split(".")

        if len(parts) == 1:
            if change.change_type == ChangeType.REMOVED:
                stage.pop(parts[0], None)
            else:
                stage[parts[0]] = change.new_value
        else:
            # Navigate to nested location
            current = stage
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            if change.change_type == ChangeType.REMOVED:
                current.pop(parts[-1], None)
            else:
                current[parts[-1]] = change.new_value

    def _set_nested(
        self,
        d: Dict,
        path: List[str],
        value: Any,
        change_type: ChangeType,
    ) -> None:
        """Set a value at a nested path."""
        current = d
        for part in path[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        if change_type == ChangeType.REMOVED:
            current.pop(path[-1], None)
        else:
            current[path[-1]] = value


# Singleton instance
_diff_service: Optional[DiffService] = None


def get_diff_service() -> DiffService:
    """Get or create the diff service singleton."""
    global _diff_service
    if _diff_service is None:
        _diff_service = DiffService()
    return _diff_service
