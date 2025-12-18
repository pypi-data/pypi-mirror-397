"""
Storage Service for FlowMason Studio.

Uses SQLite for development/testing, can be switched to PostgreSQL for production.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from flowmason_studio.models.api import (
    PipelineCreate,
    PipelineDetail,
    PipelineInputSchema,
    PipelineOutputSchema,
    PipelineStage,
    PipelineStatus,
    PipelineSummary,
    PipelineUpdate,
    RunDetail,
    RunStatus,
    RunSummary,
    StageResult,
    UsageMetricsResponse,
)
from flowmason_studio.services.database import get_connection


def _serialize_json(data: Any) -> Optional[str]:
    """Serialize data to JSON string."""
    if data is None:
        return None
    if hasattr(data, 'model_dump'):
        return json.dumps(data.model_dump(mode="json"), default=str)
    return json.dumps(data, default=str)


def _deserialize_json(text: Optional[str]) -> Any:
    """Deserialize JSON string to data."""
    if text is None:
        return None
    return json.loads(text)


def _parse_datetime(text: Optional[str]) -> Optional[datetime]:
    """Parse ISO datetime string."""
    if text is None:
        return None
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO string."""
    if dt is None:
        return None
    return dt.isoformat()


class PipelineStorage:
    """
    SQLite-backed storage for pipelines.
    """

    def create(self, pipeline: PipelineCreate, org_id: Optional[str] = None) -> PipelineDetail:
        """Create a new pipeline."""
        conn = get_connection()
        pipeline_id = f"pipe_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        detail = PipelineDetail(
            id=pipeline_id,
            name=pipeline.name,
            description=pipeline.description,
            version="1.0.0",
            input_schema=pipeline.input_schema,
            output_schema=pipeline.output_schema,
            stages=pipeline.stages,
            output_stage_id=pipeline.output_stage_id,
            category=pipeline.category,
            tags=pipeline.tags,
            is_template=pipeline.is_template,
            status=PipelineStatus.DRAFT,
            sample_input=pipeline.sample_input,
            output_config=pipeline.output_config,
            last_test_run_id=None,
            published_at=None,
            created_at=now,
            updated_at=now,
        )

        conn.execute("""
            INSERT INTO pipelines (
                id, name, description, version, category, tags,
                input_schema, output_schema, stages, output_stage_id,
                is_template, status, sample_input, output_config, created_at, updated_at, org_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            detail.id,
            detail.name,
            detail.description,
            detail.version,
            detail.category,
            _serialize_json(detail.tags),
            _serialize_json(detail.input_schema),
            _serialize_json(detail.output_schema),
            _serialize_json([s.model_dump(mode="json") for s in detail.stages]),
            detail.output_stage_id,
            1 if detail.is_template else 0,
            detail.status.value,
            _serialize_json(detail.sample_input),
            _serialize_json(detail.output_config),
            _format_datetime(detail.created_at),
            _format_datetime(detail.updated_at),
            org_id,
        ))

        return detail

    def get(self, pipeline_id: str, org_id: Optional[str] = None) -> Optional[PipelineDetail]:
        """Get a pipeline by ID, optionally scoped to an organization."""
        conn = get_connection()

        if org_id:
            row = conn.execute(
                "SELECT * FROM pipelines WHERE id = ? AND (org_id = ? OR org_id IS NULL)",
                (pipeline_id, org_id)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM pipelines WHERE id = ?",
                (pipeline_id,)
            ).fetchone()

        if not row:
            return None

        return self._row_to_detail(row)

    def get_by_name(self, name: str, org_id: Optional[str] = None) -> Optional[PipelineDetail]:
        """Get a pipeline by name (for deploy/pull commands), optionally scoped to an organization."""
        conn = get_connection()

        if org_id:
            row = conn.execute(
                "SELECT * FROM pipelines WHERE name = ? AND (org_id = ? OR org_id IS NULL)",
                (name, org_id)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM pipelines WHERE name = ?",
                (name,)
            ).fetchone()

        if not row:
            return None

        return self._row_to_detail(row)

    def _row_to_detail(self, row) -> PipelineDetail:
        """Convert a database row to PipelineDetail."""
        stages_data = _deserialize_json(row["stages"]) or []
        stages = [PipelineStage(**s) for s in stages_data]

        input_schema_data = _deserialize_json(row["input_schema"])
        output_schema_data = _deserialize_json(row["output_schema"])

        # Handle is_template with fallback for migration
        is_template = False
        try:
            is_template = bool(row["is_template"])
        except (KeyError, IndexError):
            pass

        # Handle status with fallback for migration
        status = PipelineStatus.DRAFT
        try:
            status_val = row["status"]
            if status_val:
                status = PipelineStatus(status_val)
        except (KeyError, IndexError, ValueError):
            pass

        # Handle sample_input with fallback for migration
        sample_input = None
        try:
            sample_input = _deserialize_json(row["sample_input"])
        except (KeyError, IndexError):
            pass

        # Handle last_test_run_id with fallback for migration
        last_test_run_id = None
        try:
            last_test_run_id = row["last_test_run_id"]
        except (KeyError, IndexError):
            pass

        # Handle published_at with fallback for migration
        published_at = None
        try:
            published_at = _parse_datetime(row["published_at"])
        except (KeyError, IndexError):
            pass

        # Handle output_config with fallback for migration
        output_config = None
        try:
            output_config = _deserialize_json(row["output_config"])
        except (KeyError, IndexError):
            pass

        return PipelineDetail(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            version=row["version"],
            category=row["category"],
            tags=_deserialize_json(row["tags"]) or [],
            input_schema=PipelineInputSchema(**input_schema_data) if input_schema_data else PipelineInputSchema(),
            output_schema=PipelineOutputSchema(**output_schema_data) if output_schema_data else PipelineOutputSchema(),
            stages=stages,
            output_stage_id=row["output_stage_id"],
            is_template=is_template,
            status=status,
            sample_input=sample_input,
            output_config=output_config,
            last_test_run_id=last_test_run_id,
            published_at=published_at,
            created_at=_parse_datetime(row["created_at"]),
            updated_at=_parse_datetime(row["updated_at"]),
        )

    def update(self, pipeline_id: str, update: PipelineUpdate, org_id: Optional[str] = None) -> Optional[PipelineDetail]:
        """Update an existing pipeline, optionally scoped to an organization."""
        conn = get_connection()
        existing = self.get(pipeline_id, org_id)
        if not existing:
            return None

        # Update fields that are provided
        update_data = update.model_dump(exclude_unset=True)
        pipeline_data = existing.model_dump()

        for key, value in update_data.items():
            if value is not None:
                pipeline_data[key] = value

        # Increment version
        version_parts = pipeline_data["version"].split(".")
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        pipeline_data["version"] = ".".join(version_parts)
        pipeline_data["updated_at"] = datetime.utcnow()

        # Reconstruct stages as PipelineStage objects
        stages_raw = pipeline_data.get("stages", [])
        stages = [PipelineStage(**s) if isinstance(s, dict) else s for s in stages_raw]

        # Handle is_template with default
        is_template = pipeline_data.get("is_template", False)

        # Handle sample_input - keep as-is (can be None or dict)
        sample_input = pipeline_data.get("sample_input")

        # Handle output_config - keep as-is (can be None or dict)
        output_config = pipeline_data.get("output_config")

        conn.execute("""
            UPDATE pipelines SET
                name = ?, description = ?, version = ?, category = ?, tags = ?,
                input_schema = ?, output_schema = ?, stages = ?, output_stage_id = ?,
                is_template = ?, sample_input = ?, output_config = ?, updated_at = ?
            WHERE id = ?
        """, (
            pipeline_data["name"],
            pipeline_data["description"],
            pipeline_data["version"],
            pipeline_data["category"],
            _serialize_json(pipeline_data["tags"]),
            _serialize_json(pipeline_data["input_schema"]),
            _serialize_json(pipeline_data["output_schema"]),
            _serialize_json([s.model_dump(mode="json") if hasattr(s, 'model_dump') else s for s in stages]),
            pipeline_data["output_stage_id"],
            1 if is_template else 0,
            _serialize_json(sample_input),
            _serialize_json(output_config),
            _format_datetime(pipeline_data["updated_at"]),
            pipeline_id,
        ))

        return self.get(pipeline_id, org_id)

    def publish(self, pipeline_id: str, test_run_id: str, org_id: Optional[str] = None) -> Optional[PipelineDetail]:
        """Publish a pipeline after successful test, optionally scoped to an organization."""
        conn = get_connection()
        now = datetime.utcnow()

        # Verify the pipeline exists and belongs to org (if org_id specified)
        existing = self.get(pipeline_id, org_id)
        if not existing:
            return None

        conn.execute("""
            UPDATE pipelines SET
                status = ?, last_test_run_id = ?, published_at = ?, updated_at = ?
            WHERE id = ?
        """, (
            PipelineStatus.PUBLISHED.value,
            test_run_id,
            _format_datetime(now),
            _format_datetime(now),
            pipeline_id,
        ))

        return self.get(pipeline_id, org_id)

    def unpublish(self, pipeline_id: str, org_id: Optional[str] = None) -> Optional[PipelineDetail]:
        """Unpublish a pipeline (set back to draft), optionally scoped to an organization."""
        conn = get_connection()
        now = datetime.utcnow()

        # Verify the pipeline exists and belongs to org (if org_id specified)
        existing = self.get(pipeline_id, org_id)
        if not existing:
            return None

        conn.execute("""
            UPDATE pipelines SET
                status = ?, updated_at = ?
            WHERE id = ?
        """, (
            PipelineStatus.DRAFT.value,
            _format_datetime(now),
            pipeline_id,
        ))

        return self.get(pipeline_id, org_id)

    def delete(self, pipeline_id: str, org_id: Optional[str] = None) -> bool:
        """Delete a pipeline, optionally scoped to an organization."""
        conn = get_connection()

        # Verify the pipeline exists and belongs to org (if org_id specified)
        if org_id:
            existing = self.get(pipeline_id, org_id)
            if not existing:
                return False

        cursor = conn.execute("DELETE FROM pipelines WHERE id = ?", (pipeline_id,))
        return cursor.rowcount > 0

    def list(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[str] = None,
        org_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[PipelineSummary], int]:
        """List pipelines with optional filtering, optionally scoped to an organization."""
        conn = get_connection()

        # Build query
        query = "SELECT * FROM pipelines WHERE 1=1"
        params: List[Any] = []

        # Filter by org_id if provided (include NULL for backward compatibility)
        if org_id:
            query += " AND (org_id = ? OR org_id IS NULL)"
            params.append(org_id)

        if category:
            query += " AND category = ?"
            params.append(category)

        if status:
            query += " AND status = ?"
            params.append(status)

        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        total = conn.execute(count_query, params).fetchone()[0]

        # Add ordering and pagination
        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()

        summaries = []
        for row in rows:
            stages = _deserialize_json(row["stages"]) or []
            row_tags = _deserialize_json(row["tags"]) or []

            # Filter by tags if specified
            if tags and not any(t in row_tags for t in tags):
                continue

            # Handle is_template with fallback for migration
            is_template = False
            try:
                is_template = bool(row["is_template"])
            except (KeyError, IndexError):
                pass

            # Handle status with fallback for migration
            pipeline_status = PipelineStatus.DRAFT
            try:
                status_val = row["status"]
                if status_val:
                    pipeline_status = PipelineStatus(status_val)
            except (KeyError, IndexError, ValueError):
                pass

            # Handle last_test_run_id with fallback for migration
            last_test_run_id = None
            try:
                last_test_run_id = row["last_test_run_id"]
            except (KeyError, IndexError):
                pass

            # Handle published_at with fallback for migration
            published_at = None
            try:
                published_at = _parse_datetime(row["published_at"])
            except (KeyError, IndexError):
                pass

            summaries.append(PipelineSummary(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                version=row["version"],
                stage_count=len(stages),
                category=row["category"],
                tags=row_tags,
                is_template=is_template,
                status=pipeline_status,
                last_test_run_id=last_test_run_id,
                published_at=published_at,
                created_at=_parse_datetime(row["created_at"]),
                updated_at=_parse_datetime(row["updated_at"]),
            ))

        return summaries, total


class RunStorage:
    """
    SQLite-backed storage for pipeline runs.
    """

    def create(
        self,
        pipeline_id: str,
        inputs: Dict[str, Any],
        org_id: Optional[str] = None
    ) -> RunDetail:
        """Create a new run record, optionally scoped to an organization."""
        conn = get_connection()
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        detail = RunDetail(
            id=run_id,
            pipeline_id=pipeline_id,
            status=RunStatus.PENDING,
            inputs=inputs,
            started_at=now,
            trace_id=f"trace_{uuid.uuid4().hex[:8]}",
        )

        conn.execute("""
            INSERT INTO runs (
                id, pipeline_id, status, inputs, trace_id, started_at, org_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            detail.id,
            detail.pipeline_id,
            detail.status,
            _serialize_json(detail.inputs),
            detail.trace_id,
            _format_datetime(detail.started_at),
            org_id,
        ))

        return detail

    def get(self, run_id: str, org_id: Optional[str] = None) -> Optional[RunDetail]:
        """Get a run by ID, optionally scoped to an organization."""
        conn = get_connection()

        if org_id:
            row = conn.execute(
                "SELECT * FROM runs WHERE id = ? AND (org_id = ? OR org_id IS NULL)",
                (run_id, org_id)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM runs WHERE id = ?",
                (run_id,)
            ).fetchone()

        if not row:
            return None

        return self._row_to_detail(row)

    def _row_to_detail(self, row) -> RunDetail:
        """Convert a database row to RunDetail."""
        stage_results_data = _deserialize_json(row["stage_results"])
        stage_results = None
        if stage_results_data:
            stage_results = {
                k: StageResult(**v) if isinstance(v, dict) else v
                for k, v in stage_results_data.items()
            }

        usage_data = _deserialize_json(row["usage"])
        usage = UsageMetricsResponse(**usage_data) if usage_data else None

        return RunDetail(
            id=row["id"],
            pipeline_id=row["pipeline_id"],
            status=row["status"],
            inputs=_deserialize_json(row["inputs"]) or {},
            output=_deserialize_json(row["output"]),
            error=row["error"],
            stage_results=stage_results,
            trace_id=row["trace_id"],
            started_at=_parse_datetime(row["started_at"]),
            completed_at=_parse_datetime(row["completed_at"]),
            duration_ms=row["duration_ms"],
            usage=usage,
        )

    def update_status(
        self,
        run_id: str,
        status: str,
        org_id: Optional[str] = None,
    ) -> Optional[RunDetail]:
        """Update run status, optionally scoped to an organization."""
        conn = get_connection()

        # Verify the run exists and belongs to org (if org_id specified)
        if org_id:
            existing = self.get(run_id, org_id)
            if not existing:
                return None

        completed_at = None
        duration_ms = None

        if status in ("completed", "failed", "cancelled"):
            completed_at = datetime.utcnow()
            row = conn.execute(
                "SELECT started_at FROM runs WHERE id = ?",
                (run_id,)
            ).fetchone()
            if row and row["started_at"]:
                started = _parse_datetime(row["started_at"])
                if started:
                    duration_ms = int((completed_at - started).total_seconds() * 1000)

        conn.execute("""
            UPDATE runs SET status = ?, completed_at = ?, duration_ms = ?
            WHERE id = ?
        """, (status, _format_datetime(completed_at), duration_ms, run_id))

        return self.get(run_id, org_id)

    def complete_run(
        self,
        run_id: str,
        status: str,
        output: Optional[Any] = None,
        error: Optional[str] = None,
        stage_results: Optional[Dict[str, StageResult]] = None,
        org_id: Optional[str] = None,
    ) -> Optional[RunDetail]:
        """Complete a run with results, optionally scoped to an organization."""
        conn = get_connection()

        # Verify the run exists and belongs to org (if org_id specified)
        if org_id:
            existing = self.get(run_id, org_id)
            if not existing:
                return None

        row = conn.execute(
            "SELECT started_at FROM runs WHERE id = ?",
            (run_id,)
        ).fetchone()

        if not row:
            return None

        completed_at = datetime.utcnow()
        duration_ms = None
        started = _parse_datetime(row["started_at"])
        if started:
            duration_ms = int((completed_at - started).total_seconds() * 1000)

        # Serialize stage_results
        stage_results_json = None
        if stage_results:
            stage_results_json = _serialize_json({
                k: v.model_dump(mode="json") if hasattr(v, 'model_dump') else v
                for k, v in stage_results.items()
            })

        conn.execute("""
            UPDATE runs SET
                status = ?, completed_at = ?, duration_ms = ?,
                output = ?, error = ?, stage_results = ?
            WHERE id = ?
        """, (
            status,
            _format_datetime(completed_at),
            duration_ms,
            _serialize_json(output),
            error,
            stage_results_json,
            run_id,
        ))

        return self.get(run_id, org_id)

    def delete(self, run_id: str, org_id: Optional[str] = None) -> bool:
        """Delete a run, optionally scoped to an organization."""
        conn = get_connection()

        # Verify the run exists and belongs to org (if org_id specified)
        if org_id:
            existing = self.get(run_id, org_id)
            if not existing:
                return False

        cursor = conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
        return cursor.rowcount > 0

    def list(
        self,
        pipeline_id: Optional[str] = None,
        status: Optional[str] = None,
        org_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[RunSummary], int]:
        """List runs with optional filtering, optionally scoped to an organization."""
        conn = get_connection()

        # Build query
        query = "SELECT * FROM runs WHERE 1=1"
        params: List[Any] = []

        # Filter by org_id if provided (include NULL for backward compatibility)
        if org_id:
            query += " AND (org_id = ? OR org_id IS NULL)"
            params.append(org_id)

        if pipeline_id:
            query += " AND pipeline_id = ?"
            params.append(pipeline_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        total = conn.execute(count_query, params).fetchone()[0]

        # Add ordering and pagination
        query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()

        summaries = [
            RunSummary(
                id=row["id"],
                pipeline_id=row["pipeline_id"],
                status=row["status"],
                started_at=_parse_datetime(row["started_at"]),
                completed_at=_parse_datetime(row["completed_at"]),
                duration_ms=row["duration_ms"],
            )
            for row in rows
        ]

        return summaries, total


# Global storage instances (singleton pattern for the app)
_pipeline_storage: Optional[PipelineStorage] = None
_run_storage: Optional[RunStorage] = None


def get_pipeline_storage() -> PipelineStorage:
    """Get or create the pipeline storage singleton."""
    global _pipeline_storage
    if _pipeline_storage is None:
        _pipeline_storage = PipelineStorage()
    return _pipeline_storage


def set_pipeline_storage(storage: PipelineStorage) -> None:
    """Set the pipeline storage singleton."""
    global _pipeline_storage
    _pipeline_storage = storage


def get_run_storage() -> RunStorage:
    """Get or create the run storage singleton."""
    global _run_storage
    if _run_storage is None:
        _run_storage = RunStorage()
    return _run_storage


def set_run_storage(storage: RunStorage) -> None:
    """Set the run storage singleton."""
    global _run_storage
    _run_storage = storage
