# Pipeline Versioning

FlowMason Studio provides version control for pipelines, enabling you to track changes, compare versions, and restore previous states.

## Overview

Pipeline versioning allows you to:
- Create named snapshots of pipeline configurations
- Track who made changes and when
- Compare versions to see what changed
- Restore pipelines to any previous version
- Maintain audit trails for compliance

## Creating Versions

### Manual Snapshot

Create a version snapshot at any time:

```bash
curl -X POST http://localhost:8999/api/v1/pipelines/{pipeline_id}/versions \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Added input validation stage",
    "created_by": "developer@example.com"
  }'
```

Response:
```json
{
  "id": "version-abc123",
  "pipeline_id": "pipeline-xyz",
  "version": "1.2.0",
  "name": "data-processor",
  "created_at": "2024-01-15T10:30:00Z",
  "created_by": "developer@example.com",
  "message": "Added input validation stage",
  "changes_summary": "1 stage(s) added",
  "stages_added": ["validate-input"],
  "stages_removed": [],
  "stages_modified": []
}
```

### Automatic Versioning

Versions are automatically created when:
- A pipeline is published
- A restore operation is performed (saves current state first)

## Listing Versions

View all versions of a pipeline:

```bash
curl http://localhost:8999/api/v1/pipelines/{pipeline_id}/versions
```

Response:
```json
{
  "versions": [
    {
      "id": "version-abc123",
      "version": "1.2.0",
      "message": "Added validation",
      "created_at": "2024-01-15T10:30:00Z",
      "changes_summary": "1 stage(s) added"
    },
    {
      "id": "version-xyz789",
      "version": "1.1.0",
      "message": "Initial version",
      "created_at": "2024-01-10T08:00:00Z",
      "changes_summary": null
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

## Getting Version Details

### By Version ID

```bash
curl http://localhost:8999/api/v1/pipelines/{pipeline_id}/versions/{version_id}
```

### By Version Number

```bash
curl http://localhost:8999/api/v1/pipelines/{pipeline_id}/versions/by-version/1.2.0
```

### Latest Version

```bash
curl http://localhost:8999/api/v1/pipelines/{pipeline_id}/versions/latest
```

Response includes full pipeline configuration:
```json
{
  "id": "version-abc123",
  "version": "1.2.0",
  "name": "data-processor",
  "description": "Process incoming data",
  "stages": [
    {
      "id": "validate-input",
      "component_type": "schema_validate",
      "config": { ... }
    },
    {
      "id": "process-data",
      "component_type": "json_transform",
      "config": { ... }
    }
  ],
  "input_schema": { ... },
  "output_schema": { ... },
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Comparing Versions

Compare two versions to see what changed:

```bash
curl http://localhost:8999/api/v1/pipelines/{pipeline_id}/versions/{version_id_1}/compare/{version_id_2}
```

Response:
```json
{
  "version_1": {
    "id": "version-abc123",
    "version": "1.2.0",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "version_2": {
    "id": "version-xyz789",
    "version": "1.1.0",
    "created_at": "2024-01-10T08:00:00Z"
  },
  "stages_added": ["validate-input"],
  "stages_removed": [],
  "stages_modified": ["process-data"],
  "summary": "1 stage(s) added, 1 stage(s) modified"
}
```

## Restoring Versions

Restore a pipeline to a previous version:

```bash
curl -X POST http://localhost:8999/api/v1/pipelines/{pipeline_id}/versions/{version_id}/restore
```

Response:
```json
{
  "pipeline_id": "pipeline-xyz",
  "restored_from_version": "1.1.0",
  "new_version": "1.3.0",
  "message": "Successfully restored from version 1.1.0"
}
```

The restore operation:
1. Saves the current state as a new version (so nothing is lost)
2. Updates the pipeline with the restored version's configuration
3. Creates a new version recording the restore

## Deleting Versions

Delete a specific version:

```bash
curl -X DELETE http://localhost:8999/api/v1/pipelines/{pipeline_id}/versions/{version_id}
```

## Version Fields

| Field | Description |
|-------|-------------|
| `id` | Unique version identifier |
| `pipeline_id` | Parent pipeline ID |
| `version` | Semantic version (e.g., "1.2.0") |
| `name` | Pipeline name at time of snapshot |
| `description` | Pipeline description |
| `stages` | Full stage configuration |
| `input_schema` | Input schema at snapshot |
| `output_schema` | Output schema at snapshot |
| `created_at` | When version was created |
| `created_by` | User who created the version |
| `message` | Commit-style message |
| `is_published` | Whether pipeline was published |
| `parent_version_id` | Previous version (for lineage) |
| `changes_summary` | Human-readable change summary |
| `stages_added` | List of added stage IDs |
| `stages_removed` | List of removed stage IDs |
| `stages_modified` | List of modified stage IDs |

## Best Practices

1. **Write meaningful messages**: Describe what changed and why
2. **Version before major changes**: Create a snapshot before significant edits
3. **Use comparison for review**: Compare versions before restoring
4. **Track with created_by**: Pass user identity for audit trails
5. **Clean up old versions**: Delete obsolete versions to save storage

## Database Storage

Versions are stored in the `pipeline_versions` table with full pipeline snapshots. Each version contains:
- Complete stage configurations
- Schema definitions
- LLM settings
- Diff metadata for quick comparison

The versioning system supports both SQLite (development) and PostgreSQL (production).

## Integration with Pipeline Updates

The standard pipeline update flow:
1. Edit pipeline in Studio or VSCode
2. Create version snapshot with message
3. Continue editing or publish
4. Restore if needed

Versions preserve the complete pipeline state, making it safe to experiment with changes.
