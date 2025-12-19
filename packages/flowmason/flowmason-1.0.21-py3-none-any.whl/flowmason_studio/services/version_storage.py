"""
Pipeline Version Storage Service.

Manages version history for pipelines, enabling rollback and auditing.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class PipelineVersion:
    """A stored version of a pipeline."""

    id: str
    pipeline_id: str
    version: str
    org_id: str

    # Pipeline snapshot
    name: str
    description: str
    stages: List[Dict[str, Any]]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    output_stage_id: Optional[str]
    llm_settings: Optional[Dict[str, Any]]

    # Metadata
    created_at: str
    created_by: Optional[str] = None
    message: str = ""  # Commit-style message
    is_published: bool = False
    parent_version_id: Optional[str] = None

    # Diff summary
    changes_summary: Optional[str] = None
    stages_added: List[str] = field(default_factory=list)
    stages_removed: List[str] = field(default_factory=list)
    stages_modified: List[str] = field(default_factory=list)


class VersionStorage:
    """Storage for pipeline version history using SQLite/PostgreSQL."""

    def __init__(self):
        """Initialize storage and create tables."""
        from flowmason_studio.services.database import get_connection
        self._conn = get_connection()
        self._create_tables()

    def _create_tables(self):
        """Create version tables if they don't exist."""
        from flowmason_studio.services.database import is_postgresql

        if is_postgresql():
            self._create_postgresql_tables()
        else:
            self._create_sqlite_tables()

    def _create_sqlite_tables(self):
        """Create SQLite tables."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_versions (
                id TEXT PRIMARY KEY,
                pipeline_id TEXT NOT NULL,
                version TEXT NOT NULL,
                org_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                stages TEXT NOT NULL,
                input_schema TEXT,
                output_schema TEXT,
                output_stage_id TEXT,
                llm_settings TEXT,
                created_at TEXT NOT NULL,
                created_by TEXT,
                message TEXT DEFAULT '',
                is_published INTEGER DEFAULT 0,
                parent_version_id TEXT,
                changes_summary TEXT,
                stages_added TEXT,
                stages_removed TEXT,
                stages_modified TEXT,
                FOREIGN KEY (pipeline_id) REFERENCES pipelines(id)
            )
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_versions_pipeline ON pipeline_versions(pipeline_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_versions_org ON pipeline_versions(org_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_versions_version ON pipeline_versions(pipeline_id, version)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_versions_created ON pipeline_versions(created_at)
        """)

    def _create_postgresql_tables(self):
        """Create PostgreSQL tables."""
        with self._conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_versions (
                    id TEXT PRIMARY KEY,
                    pipeline_id TEXT NOT NULL REFERENCES pipelines(id),
                    version TEXT NOT NULL,
                    org_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    stages JSONB NOT NULL,
                    input_schema JSONB,
                    output_schema JSONB,
                    output_stage_id TEXT,
                    llm_settings JSONB,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    message TEXT DEFAULT '',
                    is_published BOOLEAN DEFAULT FALSE,
                    parent_version_id TEXT,
                    changes_summary TEXT,
                    stages_added JSONB,
                    stages_removed JSONB,
                    stages_modified JSONB
                )
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_versions_pipeline ON pipeline_versions(pipeline_id)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_versions_org ON pipeline_versions(org_id)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_versions_version ON pipeline_versions(pipeline_id, version)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_versions_created ON pipeline_versions(created_at)
            """)

    def create_version(
        self,
        pipeline_id: str,
        org_id: str,
        name: str,
        version: str,
        stages: List[Dict[str, Any]],
        description: str = "",
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        output_stage_id: Optional[str] = None,
        llm_settings: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
        message: str = "",
        is_published: bool = False,
        parent_version_id: Optional[str] = None,
    ) -> PipelineVersion:
        """Create a new version snapshot."""
        import uuid

        version_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Calculate diff from parent version
        changes_summary = None
        stages_added = []
        stages_removed = []
        stages_modified = []

        if parent_version_id:
            parent = self.get(parent_version_id)
            if parent:
                changes = self._calculate_diff(parent.stages, stages)
                changes_summary = changes["summary"]
                stages_added = changes["added"]
                stages_removed = changes["removed"]
                stages_modified = changes["modified"]

        self._conn.execute(
            """
            INSERT INTO pipeline_versions (
                id, pipeline_id, version, org_id, name, description,
                stages, input_schema, output_schema, output_stage_id,
                llm_settings, created_at, created_by, message, is_published,
                parent_version_id, changes_summary, stages_added,
                stages_removed, stages_modified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                version_id,
                pipeline_id,
                version,
                org_id,
                name,
                description,
                json.dumps(stages),
                json.dumps(input_schema) if input_schema else None,
                json.dumps(output_schema) if output_schema else None,
                output_stage_id,
                json.dumps(llm_settings) if llm_settings else None,
                now,
                created_by,
                message,
                1 if is_published else 0,
                parent_version_id,
                changes_summary,
                json.dumps(stages_added),
                json.dumps(stages_removed),
                json.dumps(stages_modified),
            ),
        )

        return PipelineVersion(
            id=version_id,
            pipeline_id=pipeline_id,
            version=version,
            org_id=org_id,
            name=name,
            description=description,
            stages=stages,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            output_stage_id=output_stage_id,
            llm_settings=llm_settings,
            created_at=now,
            created_by=created_by,
            message=message,
            is_published=is_published,
            parent_version_id=parent_version_id,
            changes_summary=changes_summary,
            stages_added=stages_added,
            stages_removed=stages_removed,
            stages_modified=stages_modified,
        )

    def _calculate_diff(
        self,
        old_stages: List[Dict[str, Any]],
        new_stages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Calculate the difference between two stage lists."""
        old_ids = {s["id"]: s for s in old_stages}
        new_ids = {s["id"]: s for s in new_stages}

        added = [s for s in new_ids if s not in old_ids]
        removed = [s for s in old_ids if s not in new_ids]
        modified = []

        for stage_id in new_ids:
            if stage_id in old_ids:
                if json.dumps(old_ids[stage_id], sort_keys=True) != json.dumps(
                    new_ids[stage_id], sort_keys=True
                ):
                    modified.append(stage_id)

        # Build summary
        parts = []
        if added:
            parts.append(f"{len(added)} stage(s) added")
        if removed:
            parts.append(f"{len(removed)} stage(s) removed")
        if modified:
            parts.append(f"{len(modified)} stage(s) modified")

        summary = ", ".join(parts) if parts else "No changes"

        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "summary": summary,
        }

    def get(self, version_id: str) -> Optional[PipelineVersion]:
        """Get a version by ID."""
        cursor = self._conn.execute(
            "SELECT * FROM pipeline_versions WHERE id = ?",
            (version_id,),
        )
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_version(row)

    def get_by_version(
        self,
        pipeline_id: str,
        version: str,
        org_id: Optional[str] = None,
    ) -> Optional[PipelineVersion]:
        """Get a specific version of a pipeline."""
        query = "SELECT * FROM pipeline_versions WHERE pipeline_id = ? AND version = ?"
        params = [pipeline_id, version]

        if org_id:
            query += " AND org_id = ?"
            params.append(org_id)

        cursor = self._conn.execute(query, params)
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_version(row)

    def list_versions(
        self,
        pipeline_id: str,
        org_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[PipelineVersion], int]:
        """List all versions of a pipeline."""
        query = "SELECT * FROM pipeline_versions WHERE pipeline_id = ?"
        count_query = "SELECT COUNT(*) FROM pipeline_versions WHERE pipeline_id = ?"
        params: List[Any] = [pipeline_id]

        if org_id:
            query += " AND org_id = ?"
            count_query += " AND org_id = ?"
            params.append(org_id)

        # Get total count
        cursor = self._conn.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self._conn.execute(query, params)
        versions = [self._row_to_version(row) for row in cursor.fetchall()]

        return versions, total

    def get_latest_version(
        self,
        pipeline_id: str,
        org_id: Optional[str] = None,
    ) -> Optional[PipelineVersion]:
        """Get the most recent version of a pipeline."""
        query = "SELECT * FROM pipeline_versions WHERE pipeline_id = ?"
        params = [pipeline_id]

        if org_id:
            query += " AND org_id = ?"
            params.append(org_id)

        query += " ORDER BY created_at DESC LIMIT 1"

        cursor = self._conn.execute(query, params)
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_version(row)

    def delete_version(self, version_id: str, org_id: Optional[str] = None) -> bool:
        """Delete a version."""
        query = "DELETE FROM pipeline_versions WHERE id = ?"
        params = [version_id]

        if org_id:
            query += " AND org_id = ?"
            params.append(org_id)

        cursor = self._conn.execute(query, params)
        return bool(cursor.rowcount > 0)

    def delete_all_versions(
        self,
        pipeline_id: str,
        org_id: Optional[str] = None,
    ) -> int:
        """Delete all versions of a pipeline."""
        query = "DELETE FROM pipeline_versions WHERE pipeline_id = ?"
        params: List[Any] = [pipeline_id]

        if org_id:
            query += " AND org_id = ?"
            params.append(org_id)

        cursor = self._conn.execute(query, params)
        return int(cursor.rowcount)

    def compare_versions(
        self,
        version_id_1: str,
        version_id_2: str,
    ) -> Optional[Dict[str, Any]]:
        """Compare two versions and return the diff."""
        v1 = self.get(version_id_1)
        v2 = self.get(version_id_2)

        if not v1 or not v2:
            return None

        diff = self._calculate_diff(v1.stages, v2.stages)

        return {
            "version_1": {
                "id": v1.id,
                "version": v1.version,
                "created_at": v1.created_at,
            },
            "version_2": {
                "id": v2.id,
                "version": v2.version,
                "created_at": v2.created_at,
            },
            "stages_added": diff["added"],
            "stages_removed": diff["removed"],
            "stages_modified": diff["modified"],
            "summary": diff["summary"],
        }

    def _row_to_version(self, row) -> PipelineVersion:
        """Convert a database row to a PipelineVersion."""
        return PipelineVersion(
            id=row["id"],
            pipeline_id=row["pipeline_id"],
            version=row["version"],
            org_id=row["org_id"],
            name=row["name"],
            description=row["description"] or "",
            stages=json.loads(row["stages"]) if row["stages"] else [],
            input_schema=json.loads(row["input_schema"]) if row["input_schema"] else {},
            output_schema=json.loads(row["output_schema"]) if row["output_schema"] else {},
            output_stage_id=row["output_stage_id"],
            llm_settings=json.loads(row["llm_settings"]) if row["llm_settings"] else None,
            created_at=row["created_at"],
            created_by=row["created_by"],
            message=row["message"] or "",
            is_published=bool(row["is_published"]),
            parent_version_id=row["parent_version_id"],
            changes_summary=row["changes_summary"],
            stages_added=json.loads(row["stages_added"]) if row["stages_added"] else [],
            stages_removed=json.loads(row["stages_removed"]) if row["stages_removed"] else [],
            stages_modified=json.loads(row["stages_modified"]) if row["stages_modified"] else [],
        )


# Global instance
_version_storage: Optional[VersionStorage] = None


def get_version_storage() -> VersionStorage:
    """Get the global version storage instance."""
    global _version_storage
    if _version_storage is None:
        _version_storage = VersionStorage()
    return _version_storage
