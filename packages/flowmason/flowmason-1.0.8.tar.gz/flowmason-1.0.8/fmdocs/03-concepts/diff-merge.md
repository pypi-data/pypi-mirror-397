# Visual Pipeline Diff & Merge

FlowMason provides Git-style diff and merge capabilities for pipeline files, with both structural and visual representations.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Pipeline Diff: main.pipeline.json                              │
├─────────────────────────────────────────────────────────────────┤
│  BASE:                                                          │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                   │
│  │ fetch   │────▶│ process │────▶│ output  │                   │
│  └─────────┘     └─────────┘     └─────────┘                   │
│                                                                 │
│  THEIRS:                                                        │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐   │
│  │ fetch   │────▶│ validate│────▶│ process │────▶│ output  │   │
│  └─────────┘     └─────────┘     └─────────┘     └─────────┘   │
│                  ▲ ADDED                                        │
├─────────────────────────────────────────────────────────────────┤
│  + Added stage: validate (schema_validate)                      │
│  ~ Modified: process.config.temperature: 0.7 → 0.9              │
│  - Removed: output.config.format                                │
└─────────────────────────────────────────────────────────────────┘
```

## Comparing Pipelines

### Python API

```python
from flowmason_core.diff import PipelineDiffer, DiffFormatter

# Create differ
differ = PipelineDiffer()

# Compare two pipelines
diff_result = differ.diff(pipeline_a, pipeline_b)

# Check what changed
print(f"Added stages: {diff_result.added_stages}")
print(f"Removed stages: {diff_result.removed_stages}")
print(f"Modified stages: {diff_result.modified_stages}")
print(f"Moved stages: {diff_result.moved_stages}")

# Format diff for display
formatter = DiffFormatter()
print(formatter.format_diff(diff_result))
```

### CLI

```bash
# Compare two pipeline files
fm diff pipeline-v1.json pipeline-v2.json

# Output as colored text
fm diff pipeline-v1.json pipeline-v2.json --format colored

# Output as markdown
fm diff pipeline-v1.json pipeline-v2.json --format markdown
```

## Diff Result Structure

The `DiffResult` contains:

| Property | Type | Description |
|----------|------|-------------|
| `added_stages` | `List[str]` | Stage IDs that exist only in the second pipeline |
| `removed_stages` | `List[str]` | Stage IDs that exist only in the first pipeline |
| `modified_stages` | `List[ModifiedStage]` | Stages with changed configurations |
| `moved_stages` | `List[MovedStage]` | Stages with changed dependencies |
| `config_changes` | `Dict` | Pipeline-level config changes |

## Three-Way Merge

For merging branches with a common ancestor, use the `ThreeWayMerger`.

### Python API

```python
from flowmason_core.diff import ThreeWayMerger

merger = ThreeWayMerger()

# Merge with base (ancestor), ours, and theirs
merge_result = merger.merge(
    base=ancestor_pipeline,
    ours=our_pipeline,
    theirs=their_pipeline
)

if merge_result.is_clean:
    # No conflicts, get merged pipeline
    merged_pipeline = merge_result.merged
else:
    # Handle conflicts
    for conflict in merge_result.conflicts:
        print(f"Conflict in stage: {conflict.stage_id}")
        print(f"  Ours: {conflict.ours}")
        print(f"  Theirs: {conflict.theirs}")
```

### CLI

```bash
# Three-way merge
fm merge base.json ours.json theirs.json --output merged.json

# With conflict markers (if conflicts exist)
fm merge base.json ours.json theirs.json --conflict-markers
```

## Conflict Resolution

When conflicts occur, FlowMason provides several resolution strategies:

```python
from flowmason_core.diff import ThreeWayMerger, ConflictResolution

merger = ThreeWayMerger()

# Auto-resolve with strategy
merge_result = merger.merge(
    base, ours, theirs,
    resolution_strategy=ConflictResolution.OURS  # or THEIRS
)

# Manual resolution
if not merge_result.is_clean:
    for conflict in merge_result.conflicts:
        # Resolve each conflict manually
        merger.resolve_conflict(
            conflict.stage_id,
            resolution=conflict.ours  # Choose which version to keep
        )
```

## Output Formats

### Text Format
```
Pipeline Diff: pipeline.json
=============================
+ Added: validate (schema_validate)
- Removed: legacy_transform
~ Modified: process
    config.temperature: 0.7 → 0.9
    config.model: gpt-4 → claude-3
```

### Colored Format
Uses ANSI colors for terminal display:
- Green: Added stages
- Red: Removed stages
- Yellow: Modified stages

### Markdown Format
```markdown
## Pipeline Diff

### Added Stages
- `validate` (schema_validate)

### Removed Stages
- `legacy_transform`

### Modified Stages
#### process
| Property | Before | After |
|----------|--------|-------|
| config.temperature | 0.7 | 0.9 |
```

## VSCode Integration

The VSCode extension provides visual diff capabilities:

1. **Side-by-side Diff**: View pipelines side by side with highlighting
2. **DAG Overlay**: See structural changes in the visual DAG
3. **Inline Changes**: View config changes inline
4. **Merge UI**: Interactive three-way merge interface

### Opening Diff View

```
Command Palette > FlowMason: Compare Pipelines
```

Or right-click on a pipeline file and select "Compare with..."

## Best Practices

1. **Review Before Merge**: Always review diff output before merging
2. **Use Semantic Commits**: Commit pipeline changes with meaningful messages
3. **Test After Merge**: Run pipeline tests after merging
4. **Resolve Conflicts Carefully**: Don't auto-resolve important conflicts
