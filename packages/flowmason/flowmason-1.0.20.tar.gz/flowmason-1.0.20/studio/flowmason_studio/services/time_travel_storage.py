"""
Time Travel Debugging Storage Service.

Manages execution snapshots for time travel debugging:
- Captures state at each stage execution
- Retrieves snapshots for navigation
- Supports replay from any point
- Enables what-if analysis
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flowmason_studio.models.time_travel import (
    ExecutionSnapshot,
    ExecutionTimeline,
    ReplayResult,
    SnapshotType,
    StateDiff,
    TimelineEntry,
    WhatIfResult,
)


def _serialize_json(data: Any) -> Optional[str]:
    """Safely serialize to JSON."""
    if data is None:
        return None
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return json.dumps(str(data))


def _deserialize_json(data: Optional[str]) -> Any:
    """Safely deserialize JSON."""
    if not data:
        return None
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None


class TimeTravelStorage:
    """Storage for time travel debugging snapshots."""

    def __init__(self):
        """Initialize storage and create tables."""
        from flowmason_studio.services.database import get_connection

        self._conn = get_connection()
        self._create_tables()

    def _create_tables(self):
        """Create snapshot tables if they don't exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_snapshots (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                pipeline_id TEXT NOT NULL,
                stage_id TEXT NOT NULL,
                stage_name TEXT,
                stage_index INTEGER NOT NULL,
                snapshot_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration_ms INTEGER,
                pipeline_inputs TEXT,
                stage_inputs TEXT,
                stage_outputs TEXT,
                accumulated_outputs TEXT,
                variables TEXT,
                completed_stages TEXT,
                pending_stages TEXT,
                error TEXT,
                error_type TEXT,
                component_type TEXT,
                provider TEXT,
                model TEXT,
                token_usage TEXT
            )
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_run
            ON execution_snapshots(run_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_stage
            ON execution_snapshots(run_id, stage_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_order
            ON execution_snapshots(run_id, stage_index)
        """)

        # Replay runs table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS replay_runs (
                id TEXT PRIMARY KEY,
                original_run_id TEXT NOT NULL,
                from_snapshot_id TEXT NOT NULL,
                status TEXT NOT NULL,
                modifications TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_ms INTEGER,
                output_differences TEXT,
                stages_executed TEXT
            )
        """)

        self._conn.commit()

    # =========================================================================
    # Snapshot Capture
    # =========================================================================

    def capture_snapshot(
        self,
        run_id: str,
        pipeline_id: str,
        stage_id: str,
        stage_index: int,
        snapshot_type: SnapshotType,
        pipeline_inputs: Dict[str, Any],
        stage_inputs: Dict[str, Any],
        accumulated_outputs: Dict[str, Any],
        completed_stages: List[str],
        pending_stages: List[str],
        stage_name: Optional[str] = None,
        stage_outputs: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        error_type: Optional[str] = None,
        component_type: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        token_usage: Optional[Dict[str, int]] = None,
        duration_ms: Optional[int] = None,
    ) -> ExecutionSnapshot:
        """Capture a snapshot of execution state."""
        snapshot_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        self._conn.execute(
            """
            INSERT INTO execution_snapshots (
                id, run_id, pipeline_id, stage_id, stage_name, stage_index,
                snapshot_type, timestamp, duration_ms, pipeline_inputs,
                stage_inputs, stage_outputs, accumulated_outputs, variables,
                completed_stages, pending_stages, error, error_type,
                component_type, provider, model, token_usage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                run_id,
                pipeline_id,
                stage_id,
                stage_name,
                stage_index,
                snapshot_type.value,
                now,
                duration_ms,
                _serialize_json(pipeline_inputs),
                _serialize_json(stage_inputs),
                _serialize_json(stage_outputs),
                _serialize_json(accumulated_outputs),
                _serialize_json(variables or {}),
                _serialize_json(completed_stages),
                _serialize_json(pending_stages),
                error,
                error_type,
                component_type,
                provider,
                model,
                _serialize_json(token_usage),
            ),
        )
        self._conn.commit()

        return ExecutionSnapshot(
            id=snapshot_id,
            run_id=run_id,
            pipeline_id=pipeline_id,
            stage_id=stage_id,
            stage_name=stage_name,
            stage_index=stage_index,
            snapshot_type=snapshot_type,
            timestamp=now,
            duration_ms=duration_ms,
            pipeline_inputs=pipeline_inputs,
            stage_inputs=stage_inputs,
            stage_outputs=stage_outputs,
            accumulated_outputs=accumulated_outputs,
            variables=variables or {},
            completed_stages=completed_stages,
            pending_stages=pending_stages,
            error=error,
            error_type=error_type,
            component_type=component_type,
            provider=provider,
            model=model,
            token_usage=token_usage,
        )

    # =========================================================================
    # Snapshot Retrieval
    # =========================================================================

    def get_snapshot(self, snapshot_id: str) -> Optional[ExecutionSnapshot]:
        """Get a specific snapshot by ID."""
        cursor = self._conn.execute(
            "SELECT * FROM execution_snapshots WHERE id = ?",
            (snapshot_id,),
        )
        row = cursor.fetchone()
        return self._row_to_snapshot(row) if row else None

    def get_snapshots_for_run(
        self,
        run_id: str,
        snapshot_type: Optional[SnapshotType] = None,
    ) -> List[ExecutionSnapshot]:
        """Get all snapshots for a run, optionally filtered by type."""
        query = "SELECT * FROM execution_snapshots WHERE run_id = ?"
        params: List[Any] = [run_id]

        if snapshot_type:
            query += " AND snapshot_type = ?"
            params.append(snapshot_type.value)

        query += " ORDER BY stage_index, timestamp"

        cursor = self._conn.execute(query, params)
        return [self._row_to_snapshot(row) for row in cursor.fetchall()]

    def get_snapshot_at_stage(
        self,
        run_id: str,
        stage_id: str,
        snapshot_type: Optional[SnapshotType] = None,
    ) -> Optional[ExecutionSnapshot]:
        """Get snapshot at a specific stage."""
        query = "SELECT * FROM execution_snapshots WHERE run_id = ? AND stage_id = ?"
        params: List[Any] = [run_id, stage_id]

        if snapshot_type:
            query += " AND snapshot_type = ?"
            params.append(snapshot_type.value)

        query += " ORDER BY timestamp DESC LIMIT 1"

        cursor = self._conn.execute(query, params)
        row = cursor.fetchone()
        return self._row_to_snapshot(row) if row else None

    def get_timeline(self, run_id: str) -> ExecutionTimeline:
        """Get the complete execution timeline for a run."""
        snapshots = self.get_snapshots_for_run(run_id)

        if not snapshots:
            return ExecutionTimeline(
                run_id=run_id,
                pipeline_id="",
                total_snapshots=0,
                status="unknown",
                entries=[],
            )

        entries: List[TimelineEntry] = []
        total_duration = 0
        status = "completed"
        pipeline_id = snapshots[0].pipeline_id if snapshots else ""

        for i, snap in enumerate(snapshots):
            # Determine status based on snapshot type
            if snap.snapshot_type == SnapshotType.STAGE_FAILED:
                stage_status = "failed"
                status = "failed"
            elif snap.snapshot_type == SnapshotType.STAGE_COMPLETE:
                stage_status = "completed"
            elif snap.snapshot_type == SnapshotType.STAGE_START:
                stage_status = "running"
            else:
                stage_status = "unknown"

            # Create output preview
            output_preview = None
            if snap.stage_outputs:
                preview_text = str(snap.stage_outputs)[:100]
                if len(str(snap.stage_outputs)) > 100:
                    preview_text += "..."
                output_preview = preview_text

            error_preview = None
            if snap.error:
                error_preview = snap.error[:100] if len(snap.error) > 100 else snap.error

            if snap.duration_ms:
                total_duration = snap.duration_ms

            entries.append(TimelineEntry(
                snapshot_id=snap.id,
                stage_id=snap.stage_id,
                stage_name=snap.stage_name,
                component_type=snap.component_type,
                snapshot_type=snap.snapshot_type,
                timestamp=snap.timestamp,
                duration_ms=snap.duration_ms,
                status=stage_status,
                is_current=(i == len(snapshots) - 1),
                has_outputs=snap.stage_outputs is not None,
                output_preview=output_preview,
                error_preview=error_preview,
            ))

        return ExecutionTimeline(
            run_id=run_id,
            pipeline_id=pipeline_id,
            total_snapshots=len(entries),
            total_duration_ms=total_duration,
            status=status,
            entries=entries,
            current_index=len(entries) - 1,
            can_step_back=len(entries) > 1,
            can_step_forward=False,
        )

    # =========================================================================
    # State Comparison
    # =========================================================================

    def get_diff(
        self,
        from_snapshot_id: str,
        to_snapshot_id: str,
    ) -> Optional[StateDiff]:
        """Calculate the difference between two snapshots."""
        from_snap = self.get_snapshot(from_snapshot_id)
        to_snap = self.get_snapshot(to_snapshot_id)

        if not from_snap or not to_snap:
            return None

        # Calculate output differences
        added_outputs: Dict[str, Any] = {}
        modified_outputs: Dict[str, Dict[str, Any]] = {}
        removed_outputs: List[str] = []

        from_outputs = from_snap.accumulated_outputs or {}
        to_outputs = to_snap.accumulated_outputs or {}

        for key, value in to_outputs.items():
            if key not in from_outputs:
                added_outputs[key] = value
            elif from_outputs[key] != value:
                modified_outputs[key] = {
                    "old": from_outputs[key],
                    "new": value,
                }

        for key in from_outputs:
            if key not in to_outputs:
                removed_outputs.append(key)

        # Calculate variable differences
        added_variables: Dict[str, Any] = {}
        modified_variables: Dict[str, Dict[str, Any]] = {}

        from_vars = from_snap.variables or {}
        to_vars = to_snap.variables or {}

        for key, value in to_vars.items():
            if key not in from_vars:
                added_variables[key] = value
            elif from_vars[key] != value:
                modified_variables[key] = {
                    "old": from_vars[key],
                    "new": value,
                }

        # Calculate stages completed between snapshots
        from_completed = set(from_snap.completed_stages or [])
        to_completed = set(to_snap.completed_stages or [])
        stages_completed = list(to_completed - from_completed)

        # Duration and tokens
        from_duration = from_snap.duration_ms or 0
        to_duration = to_snap.duration_ms or 0
        duration_diff = to_duration - from_duration

        from_tokens = (from_snap.token_usage or {}).get("total", 0)
        to_tokens = (to_snap.token_usage or {}).get("total", 0)
        tokens_diff = to_tokens - from_tokens

        return StateDiff(
            from_snapshot_id=from_snapshot_id,
            to_snapshot_id=to_snapshot_id,
            added_outputs=added_outputs,
            modified_outputs=modified_outputs,
            removed_outputs=removed_outputs,
            added_variables=added_variables,
            modified_variables=modified_variables,
            stages_completed=stages_completed,
            duration_ms=duration_diff,
            tokens_used=tokens_diff,
        )

    # =========================================================================
    # Replay Operations
    # =========================================================================

    def create_replay_run(
        self,
        original_run_id: str,
        from_snapshot_id: str,
        modifications: Optional[Dict[str, Any]] = None,
    ) -> ReplayResult:
        """Create a new replay run from a snapshot."""
        replay_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        self._conn.execute(
            """
            INSERT INTO replay_runs (
                id, original_run_id, from_snapshot_id, status,
                modifications, started_at, stages_executed
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                replay_id,
                original_run_id,
                from_snapshot_id,
                "running",
                _serialize_json(modifications or {}),
                now,
                _serialize_json([]),
            ),
        )
        self._conn.commit()

        return ReplayResult(
            original_run_id=original_run_id,
            replay_run_id=replay_id,
            from_snapshot_id=from_snapshot_id,
            status="running",
            modifications_applied=modifications or {},
            started_at=now,
        )

    def complete_replay_run(
        self,
        replay_run_id: str,
        status: str,
        stages_executed: List[str],
        output_differences: Optional[Dict[str, Any]] = None,
    ) -> Optional[ReplayResult]:
        """Complete a replay run with results."""
        now = datetime.utcnow()

        # Get existing replay run
        cursor = self._conn.execute(
            "SELECT * FROM replay_runs WHERE id = ?",
            (replay_run_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        started_at = row["started_at"]
        started_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        started_dt = started_dt.replace(tzinfo=None)
        duration_ms = int((now - started_dt).total_seconds() * 1000)

        self._conn.execute(
            """
            UPDATE replay_runs SET
                status = ?, completed_at = ?, duration_ms = ?,
                stages_executed = ?, output_differences = ?
            WHERE id = ?
            """,
            (
                status,
                now.isoformat(),
                duration_ms,
                _serialize_json(stages_executed),
                _serialize_json(output_differences),
                replay_run_id,
            ),
        )
        self._conn.commit()

        return ReplayResult(
            original_run_id=row["original_run_id"],
            replay_run_id=replay_run_id,
            from_snapshot_id=row["from_snapshot_id"],
            status=status,
            modifications_applied=_deserialize_json(row["modifications"]) or {},
            output_differences=output_differences,
            stages_executed=stages_executed,
            started_at=started_at,
            completed_at=now.isoformat(),
            duration_ms=duration_ms,
        )

    def get_replay_run(self, replay_run_id: str) -> Optional[ReplayResult]:
        """Get a replay run by ID."""
        cursor = self._conn.execute(
            "SELECT * FROM replay_runs WHERE id = ?",
            (replay_run_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        return ReplayResult(
            original_run_id=row["original_run_id"],
            replay_run_id=row["id"],
            from_snapshot_id=row["from_snapshot_id"],
            status=row["status"],
            modifications_applied=_deserialize_json(row["modifications"]) or {},
            output_differences=_deserialize_json(row["output_differences"]),
            stages_executed=_deserialize_json(row["stages_executed"]) or [],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            duration_ms=row["duration_ms"],
        )

    # =========================================================================
    # What-If Analysis
    # =========================================================================

    def create_whatif_analysis(
        self,
        original_run_id: str,
        snapshot_id: str,
        modifications: Dict[str, Any],
    ) -> Tuple[str, ExecutionSnapshot]:
        """Create a what-if analysis session.

        Returns the whatif run ID and the modified snapshot to start from.
        """
        # Get the original snapshot
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        # Create a modified snapshot
        modified_inputs = dict(snapshot.pipeline_inputs)
        modified_variables = dict(snapshot.variables)

        # Apply modifications
        for key, value in modifications.items():
            if key.startswith("var:"):
                var_key = key[4:]
                modified_variables[var_key] = value
            else:
                modified_inputs[key] = value

        # Create replay run
        replay = self.create_replay_run(
            original_run_id=original_run_id,
            from_snapshot_id=snapshot_id,
            modifications=modifications,
        )

        # Create modified snapshot for execution
        modified_snapshot = ExecutionSnapshot(
            id=f"whatif_{snapshot.id}",
            run_id=replay.replay_run_id,
            pipeline_id=snapshot.pipeline_id,
            stage_id=snapshot.stage_id,
            stage_name=snapshot.stage_name,
            stage_index=snapshot.stage_index,
            snapshot_type=SnapshotType.CHECKPOINT,
            timestamp=datetime.utcnow().isoformat(),
            pipeline_inputs=modified_inputs,
            stage_inputs=snapshot.stage_inputs,
            accumulated_outputs=snapshot.accumulated_outputs,
            variables=modified_variables,
            completed_stages=snapshot.completed_stages,
            pending_stages=snapshot.pending_stages,
            component_type=snapshot.component_type,
        )

        return replay.replay_run_id, modified_snapshot

    # =========================================================================
    # Cleanup
    # =========================================================================

    def delete_snapshots_for_run(self, run_id: str) -> int:
        """Delete all snapshots for a run."""
        cursor = self._conn.execute(
            "DELETE FROM execution_snapshots WHERE run_id = ?",
            (run_id,),
        )
        self._conn.commit()
        return cursor.rowcount

    def cleanup_old_snapshots(self, days: int = 7) -> int:
        """Clean up snapshots older than specified days."""
        from datetime import timedelta

        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

        cursor = self._conn.execute(
            "DELETE FROM execution_snapshots WHERE timestamp < ?",
            (cutoff,),
        )
        self._conn.commit()
        return cursor.rowcount

    # =========================================================================
    # Helpers
    # =========================================================================

    def _row_to_snapshot(self, row: Any) -> ExecutionSnapshot:
        """Convert a database row to ExecutionSnapshot."""
        return ExecutionSnapshot(
            id=row["id"],
            run_id=row["run_id"],
            pipeline_id=row["pipeline_id"],
            stage_id=row["stage_id"],
            stage_name=row["stage_name"],
            stage_index=row["stage_index"],
            snapshot_type=SnapshotType(row["snapshot_type"]),
            timestamp=row["timestamp"],
            duration_ms=row["duration_ms"],
            pipeline_inputs=_deserialize_json(row["pipeline_inputs"]) or {},
            stage_inputs=_deserialize_json(row["stage_inputs"]) or {},
            stage_outputs=_deserialize_json(row["stage_outputs"]),
            accumulated_outputs=_deserialize_json(row["accumulated_outputs"]) or {},
            variables=_deserialize_json(row["variables"]) or {},
            completed_stages=_deserialize_json(row["completed_stages"]) or [],
            pending_stages=_deserialize_json(row["pending_stages"]) or [],
            error=row["error"],
            error_type=row["error_type"],
            component_type=row["component_type"],
            provider=row["provider"],
            model=row["model"],
            token_usage=_deserialize_json(row["token_usage"]),
        )


# Global instance
_time_travel_storage: Optional[TimeTravelStorage] = None


def get_time_travel_storage() -> TimeTravelStorage:
    """Get the global time travel storage instance."""
    global _time_travel_storage
    if _time_travel_storage is None:
        _time_travel_storage = TimeTravelStorage()
    return _time_travel_storage
