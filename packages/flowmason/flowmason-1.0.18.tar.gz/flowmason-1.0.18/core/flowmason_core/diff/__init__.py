"""
FlowMason Pipeline Diff & Merge System.

Provides Git-style diff and merge capabilities for pipeline files.

Main Components:
- PipelineDiffer: Computes structural diffs between pipelines
- StageDiffer: Computes stage-level diffs
- PipelineMerger: Three-way merge for pipelines
- DiffFormatter: Formats diffs for display

Example:
    from flowmason_core.diff import PipelineDiffer, DiffResult

    differ = PipelineDiffer()
    diff = differ.diff(pipeline_a, pipeline_b)

    print(f"Added stages: {diff.added_stages}")
    print(f"Removed stages: {diff.removed_stages}")
    print(f"Modified stages: {diff.modified_stages}")
"""

from flowmason_core.diff.pipeline_diff import (
    DiffResult,
    PipelineDiffer,
    StageDiff,
    StageModification,
)
from flowmason_core.diff.merge import MergeConflict, MergeResult, ThreeWayMerger
from flowmason_core.diff.formatter import DiffFormatter

__all__ = [
    # Diff
    "PipelineDiffer",
    "DiffResult",
    "StageDiff",
    "StageModification",
    # Merge
    "ThreeWayMerger",
    "MergeResult",
    "MergeConflict",
    # Formatting
    "DiffFormatter",
]
