"""
Diff Formatter for FlowMason.

Formats pipeline diffs for human-readable output in various formats.
"""

import json
from typing import Any, Dict, List, Optional

from flowmason_core.diff.pipeline_diff import (
    ChangeType,
    DiffResult,
    FieldChange,
    StageDiff,
)
from flowmason_core.diff.merge import MergeConflict, MergeResult


class DiffFormatter:
    """
    Formats diff results for display.

    Supports multiple output formats:
    - text: Plain text with color markers
    - json: JSON format for programmatic use
    - markdown: Markdown format for documentation
    - unified: Git-style unified diff format
    """

    def format_diff(
        self,
        diff: DiffResult,
        format: str = "text",
        color: bool = True,
    ) -> str:
        """
        Format a diff result for display.

        Args:
            diff: The DiffResult to format
            format: Output format ("text", "json", "markdown", "unified")
            color: Whether to include ANSI color codes (text format only)

        Returns:
            Formatted diff string
        """
        if format == "json":
            return self._format_json(diff)
        elif format == "markdown":
            return self._format_markdown(diff)
        elif format == "unified":
            return self._format_unified(diff, color)
        else:
            return self._format_text(diff, color)

    def _format_text(self, diff: DiffResult, color: bool) -> str:
        """Format diff as plain text."""
        lines: List[str] = []

        # Color codes
        if color:
            RED = "\033[31m"
            GREEN = "\033[32m"
            YELLOW = "\033[33m"
            CYAN = "\033[36m"
            RESET = "\033[0m"
            BOLD = "\033[1m"
        else:
            RED = GREEN = YELLOW = CYAN = RESET = BOLD = ""

        # Header
        lines.append(f"{BOLD}Pipeline Diff{RESET}")
        lines.append(f"Summary: {diff.summary}")
        lines.append("")

        # Metadata changes
        if diff.name_changed:
            lines.append(f"{YELLOW}~ name: {diff.old_name} -> {diff.new_name}{RESET}")
        if diff.version_changed:
            lines.append(f"{YELLOW}~ version: {diff.old_version} -> {diff.new_version}{RESET}")
        if diff.description_changed:
            lines.append(f"{YELLOW}~ description changed{RESET}")

        # Added stages
        if diff.added_stages:
            lines.append("")
            lines.append(f"{BOLD}Added Stages ({len(diff.added_stages)}):{RESET}")
            for stage in diff.added_stages:
                lines.append(f"  {GREEN}+ {stage.stage_id}{RESET}")
                if stage.new_config:
                    component = stage.new_config.get("component_type") or stage.new_config.get("component")
                    if component:
                        lines.append(f"    {CYAN}component: {component}{RESET}")

        # Removed stages
        if diff.removed_stages:
            lines.append("")
            lines.append(f"{BOLD}Removed Stages ({len(diff.removed_stages)}):{RESET}")
            for stage in diff.removed_stages:
                lines.append(f"  {RED}- {stage.stage_id}{RESET}")

        # Modified stages
        if diff.modified_stages:
            lines.append("")
            lines.append(f"{BOLD}Modified Stages ({len(diff.modified_stages)}):{RESET}")
            for stage in diff.modified_stages:
                lines.append(f"  {YELLOW}~ {stage.stage_id}{RESET}")
                if stage.modifications:
                    for change in stage.modifications.changes[:5]:  # Limit to 5 changes
                        lines.append(f"    {self._format_field_change(change, color)}")
                    if len(stage.modifications.changes) > 5:
                        lines.append(f"    ... and {len(stage.modifications.changes) - 5} more changes")

        # Moved stages
        if diff.moved_stages:
            lines.append("")
            lines.append(f"{BOLD}Moved Stages ({len(diff.moved_stages)}):{RESET}")
            for stage in diff.moved_stages:
                lines.append(f"  {CYAN}> {stage.stage_id} [{stage.old_index} -> {stage.new_index}]{RESET}")

        # Schema changes
        if diff.input_schema_changed:
            lines.append("")
            lines.append(f"{YELLOW}~ Input schema changed{RESET}")
            for change in diff.input_schema_changes[:3]:
                lines.append(f"  {self._format_field_change(change, color)}")

        if diff.output_schema_changed:
            lines.append("")
            lines.append(f"{YELLOW}~ Output schema changed{RESET}")
            for change in diff.output_schema_changes[:3]:
                lines.append(f"  {self._format_field_change(change, color)}")

        # Dependency changes
        if diff.dependency_changes:
            lines.append("")
            lines.append(f"{BOLD}Dependency Changes ({len(diff.dependency_changes)}):{RESET}")
            for from_id, to_id, change_type in diff.dependency_changes[:5]:
                if change_type == ChangeType.ADDED:
                    lines.append(f"  {GREEN}+ {from_id} -> {to_id}{RESET}")
                else:
                    lines.append(f"  {RED}- {from_id} -> {to_id}{RESET}")

        return "\n".join(lines)

    def _format_field_change(self, change: FieldChange, color: bool) -> str:
        """Format a single field change."""
        if color:
            RED = "\033[31m"
            GREEN = "\033[32m"
            YELLOW = "\033[33m"
            RESET = "\033[0m"
        else:
            RED = GREEN = YELLOW = RESET = ""

        if change.change_type == ChangeType.ADDED:
            return f"{GREEN}+ {change.field_path}: {self._truncate(change.new_value)}{RESET}"
        elif change.change_type == ChangeType.REMOVED:
            return f"{RED}- {change.field_path}: {self._truncate(change.old_value)}{RESET}"
        elif change.change_type == ChangeType.MODIFIED:
            return f"{YELLOW}~ {change.field_path}: {self._truncate(change.old_value)} -> {self._truncate(change.new_value)}{RESET}"
        return f"  {change.field_path}"

    def _format_json(self, diff: DiffResult) -> str:
        """Format diff as JSON."""
        data = {
            "summary": diff.summary,
            "has_changes": diff.has_changes,
            "is_structural_change": diff.is_structural_change,
            "metadata": {
                "name_changed": diff.name_changed,
                "version_changed": diff.version_changed,
                "description_changed": diff.description_changed,
            },
            "stages": {
                "added": [{"id": s.stage_id, "config": s.new_config} for s in diff.added_stages],
                "removed": [{"id": s.stage_id} for s in diff.removed_stages],
                "modified": [
                    {
                        "id": s.stage_id,
                        "changes": [
                            {
                                "field": c.field_path,
                                "old": c.old_value,
                                "new": c.new_value,
                                "type": c.change_type.value,
                            }
                            for c in (s.modifications.changes if s.modifications else [])
                        ],
                    }
                    for s in diff.modified_stages
                ],
                "moved": [
                    {"id": s.stage_id, "from": s.old_index, "to": s.new_index}
                    for s in diff.moved_stages
                ],
            },
            "schemas": {
                "input_changed": diff.input_schema_changed,
                "output_changed": diff.output_schema_changed,
            },
            "dependencies": [
                {"from": f, "to": t, "type": c.value}
                for f, t, c in diff.dependency_changes
            ],
        }
        return json.dumps(data, indent=2, default=str)

    def _format_markdown(self, diff: DiffResult) -> str:
        """Format diff as Markdown."""
        lines: List[str] = []

        lines.append("# Pipeline Diff")
        lines.append("")
        lines.append(f"**Summary:** {diff.summary}")
        lines.append("")

        # Metadata
        if diff.name_changed or diff.version_changed or diff.description_changed:
            lines.append("## Metadata Changes")
            lines.append("")
            if diff.name_changed:
                lines.append(f"- **Name:** `{diff.old_name}` → `{diff.new_name}`")
            if diff.version_changed:
                lines.append(f"- **Version:** `{diff.old_version}` → `{diff.new_version}`")
            if diff.description_changed:
                lines.append("- **Description:** Changed")
            lines.append("")

        # Added stages
        if diff.added_stages:
            lines.append("## Added Stages")
            lines.append("")
            for stage in diff.added_stages:
                component = ""
                if stage.new_config:
                    component = stage.new_config.get("component_type") or stage.new_config.get("component", "")
                lines.append(f"- **{stage.stage_id}** ({component})")
            lines.append("")

        # Removed stages
        if diff.removed_stages:
            lines.append("## Removed Stages")
            lines.append("")
            for stage in diff.removed_stages:
                lines.append(f"- ~~{stage.stage_id}~~")
            lines.append("")

        # Modified stages
        if diff.modified_stages:
            lines.append("## Modified Stages")
            lines.append("")
            for stage in diff.modified_stages:
                lines.append(f"### {stage.stage_id}")
                lines.append("")
                if stage.modifications:
                    lines.append("| Field | Old | New |")
                    lines.append("|-------|-----|-----|")
                    for change in stage.modifications.changes[:10]:
                        old = self._truncate(change.old_value, 30)
                        new = self._truncate(change.new_value, 30)
                        lines.append(f"| `{change.field_path}` | {old} | {new} |")
                lines.append("")

        return "\n".join(lines)

    def _format_unified(self, diff: DiffResult, color: bool) -> str:
        """Format diff in unified diff style."""
        lines: List[str] = []

        if color:
            RED = "\033[31m"
            GREEN = "\033[32m"
            CYAN = "\033[36m"
            RESET = "\033[0m"
        else:
            RED = GREEN = CYAN = RESET = ""

        lines.append(f"{CYAN}--- a/pipeline{RESET}")
        lines.append(f"{CYAN}+++ b/pipeline{RESET}")
        lines.append(f"{CYAN}@@ stages @@{RESET}")

        # Show stage changes
        all_stage_ids = set()
        for s in diff.added_stages:
            all_stage_ids.add(s.stage_id)
        for s in diff.removed_stages:
            all_stage_ids.add(s.stage_id)
        for s in diff.modified_stages:
            all_stage_ids.add(s.stage_id)
        for s in diff.unchanged_stages:
            all_stage_ids.add(s.stage_id)

        removed_ids = {s.stage_id for s in diff.removed_stages}
        added_ids = {s.stage_id for s in diff.added_stages}
        modified_ids = {s.stage_id for s in diff.modified_stages}

        for stage_id in sorted(all_stage_ids):
            if stage_id in removed_ids:
                lines.append(f"{RED}-  {stage_id}{RESET}")
            elif stage_id in added_ids:
                lines.append(f"{GREEN}+  {stage_id}{RESET}")
            elif stage_id in modified_ids:
                lines.append(f"{RED}-  {stage_id} (old){RESET}")
                lines.append(f"{GREEN}+  {stage_id} (modified){RESET}")
            else:
                lines.append(f"   {stage_id}")

        return "\n".join(lines)

    def format_merge_result(
        self,
        result: MergeResult,
        format: str = "text",
        color: bool = True,
    ) -> str:
        """
        Format a merge result for display.

        Args:
            result: The MergeResult to format
            format: Output format ("text", "json")
            color: Whether to include ANSI color codes

        Returns:
            Formatted merge result string
        """
        if format == "json":
            return self._format_merge_json(result)
        return self._format_merge_text(result, color)

    def _format_merge_text(self, result: MergeResult, color: bool) -> str:
        """Format merge result as text."""
        lines: List[str] = []

        if color:
            RED = "\033[31m"
            GREEN = "\033[32m"
            YELLOW = "\033[33m"
            RESET = "\033[0m"
            BOLD = "\033[1m"
        else:
            RED = GREEN = YELLOW = RESET = BOLD = ""

        if result.is_clean:
            lines.append(f"{GREEN}{BOLD}Merge completed successfully{RESET}")
        else:
            lines.append(f"{RED}{BOLD}Merge has conflicts{RESET}")

        # Auto-resolved
        if result.auto_resolved:
            lines.append("")
            lines.append(f"{BOLD}Auto-resolved ({len(result.auto_resolved)}):{RESET}")
            for item in result.auto_resolved[:10]:
                lines.append(f"  {GREEN}✓{RESET} {item}")
            if len(result.auto_resolved) > 10:
                lines.append(f"  ... and {len(result.auto_resolved) - 10} more")

        # Conflicts
        if result.conflicts:
            lines.append("")
            lines.append(f"{BOLD}{RED}Conflicts ({len(result.conflicts)}):{RESET}")
            for conflict in result.conflicts:
                lines.append(f"  {RED}✗{RESET} {conflict.location}")
                lines.append(f"    {conflict.message}")

        return "\n".join(lines)

    def _format_merge_json(self, result: MergeResult) -> str:
        """Format merge result as JSON."""
        data = {
            "is_clean": result.is_clean,
            "has_conflicts": result.has_conflicts,
            "auto_resolved": result.auto_resolved,
            "conflicts": [
                {
                    "type": c.conflict_type.value,
                    "location": c.location,
                    "message": c.message,
                    "base": c.base_value,
                    "ours": c.ours_value,
                    "theirs": c.theirs_value,
                }
                for c in result.conflicts
            ],
            "merged": result.merged,
        }
        return json.dumps(data, indent=2, default=str)

    def _truncate(self, value: Any, max_len: int = 50) -> str:
        """Truncate a value for display."""
        s = str(value)
        if len(s) > max_len:
            return s[:max_len - 3] + "..."
        return s
