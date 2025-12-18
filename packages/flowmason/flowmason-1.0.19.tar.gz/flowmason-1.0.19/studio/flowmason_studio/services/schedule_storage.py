"""
Schedule Storage Service.

Manages scheduled pipeline runs using cron expressions.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ScheduledPipeline:
    """A scheduled pipeline configuration."""
    id: str
    name: str
    pipeline_id: str
    pipeline_name: str
    org_id: str

    # Schedule (cron expression)
    cron_expression: str  # e.g., "0 9 * * *" for daily at 9am

    # Pipeline inputs
    inputs: Dict[str, Any] = field(default_factory=dict)

    # Options
    enabled: bool = True
    timezone: str = "UTC"
    description: str = ""

    # Metadata
    created_at: str = ""
    updated_at: str = ""
    next_run_at: Optional[str] = None
    last_run_at: Optional[str] = None
    last_run_id: Optional[str] = None
    last_run_status: Optional[str] = None
    run_count: int = 0
    failure_count: int = 0


@dataclass
class ScheduleRun:
    """Record of a scheduled run."""
    id: str
    schedule_id: str
    run_id: str
    scheduled_at: str  # When it was supposed to run
    started_at: str  # When it actually started
    status: str  # "pending", "running", "completed", "failed"
    error_message: Optional[str] = None


class ScheduleStorage:
    """Storage for scheduled pipelines using SQLite."""

    def __init__(self):
        """Initialize storage and create tables."""
        from flowmason_studio.services.database import get_connection
        self._conn = get_connection()
        self._create_tables()

    def _create_tables(self):
        """Create schedule tables if they don't exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                name TEXT NOT NULL,
                pipeline_id TEXT NOT NULL,
                pipeline_name TEXT NOT NULL,
                cron_expression TEXT NOT NULL,
                inputs TEXT DEFAULT '{}',
                enabled INTEGER DEFAULT 1,
                timezone TEXT DEFAULT 'UTC',
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                next_run_at TEXT,
                last_run_at TEXT,
                last_run_id TEXT,
                last_run_status TEXT,
                run_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0
            )
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_schedules_org ON schedules(org_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_schedules_enabled ON schedules(enabled)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_schedules_next_run ON schedules(next_run_at)
        """)

        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS schedule_runs (
                id TEXT PRIMARY KEY,
                schedule_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                scheduled_at TEXT NOT NULL,
                started_at TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                FOREIGN KEY (schedule_id) REFERENCES schedules(id)
            )
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_schedule_runs_schedule ON schedule_runs(schedule_id)
        """)

        self._conn.commit()

    def create(
        self,
        name: str,
        pipeline_id: str,
        pipeline_name: str,
        org_id: str,
        cron_expression: str,
        inputs: Optional[Dict[str, Any]] = None,
        timezone: str = "UTC",
        description: str = "",
        enabled: bool = True,
    ) -> ScheduledPipeline:
        """Create a new schedule."""
        import uuid

        schedule_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Calculate next run time
        next_run = self._calculate_next_run(cron_expression, timezone)

        self._conn.execute(
            """
            INSERT INTO schedules (
                id, org_id, name, pipeline_id, pipeline_name, cron_expression,
                inputs, enabled, timezone, description, created_at, updated_at,
                next_run_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                schedule_id,
                org_id,
                name,
                pipeline_id,
                pipeline_name,
                cron_expression,
                json.dumps(inputs or {}),
                1 if enabled else 0,
                timezone,
                description,
                now,
                now,
                next_run.isoformat() if next_run else None,
            ),
        )
        self._conn.commit()

        return ScheduledPipeline(
            id=schedule_id,
            name=name,
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            org_id=org_id,
            cron_expression=cron_expression,
            inputs=inputs or {},
            enabled=enabled,
            timezone=timezone,
            description=description,
            created_at=now,
            updated_at=now,
            next_run_at=next_run.isoformat() if next_run else None,
        )

    def _calculate_next_run(
        self,
        cron_expression: str,
        timezone: str = "UTC",
    ) -> Optional[datetime]:
        """Calculate next run time from cron expression."""
        try:
            from croniter import croniter  # type: ignore[import-untyped]
        except ImportError:
            # If croniter not installed, return None
            return None

        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(timezone)
            now = datetime.now(tz)
        except Exception:
            now = datetime.utcnow()

        try:
            cron = croniter(cron_expression, now)
            next_time = cron.get_next(datetime)
            return next_time if isinstance(next_time, datetime) else None
        except Exception:
            return None

    def get(self, schedule_id: str, org_id: Optional[str] = None) -> Optional[ScheduledPipeline]:
        """Get a schedule by ID."""
        query = "SELECT * FROM schedules WHERE id = ?"
        params = [schedule_id]

        if org_id:
            query += " AND org_id = ?"
            params.append(org_id)

        cursor = self._conn.execute(query, params)
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_schedule(row)

    def list(
        self,
        org_id: str,
        pipeline_id: Optional[str] = None,
        enabled_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[ScheduledPipeline], int]:
        """List schedules for an organization."""
        query = "SELECT * FROM schedules WHERE org_id = ?"
        count_query = "SELECT COUNT(*) FROM schedules WHERE org_id = ?"
        params: List[Any] = [org_id]

        if pipeline_id:
            query += " AND pipeline_id = ?"
            count_query += " AND pipeline_id = ?"
            params.append(pipeline_id)

        if enabled_only:
            query += " AND enabled = 1"
            count_query += " AND enabled = 1"

        # Get total count
        cursor = self._conn.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self._conn.execute(query, params)
        schedules = [self._row_to_schedule(row) for row in cursor.fetchall()]

        return schedules, total

    def update(
        self,
        schedule_id: str,
        org_id: str,
        name: Optional[str] = None,
        cron_expression: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        enabled: Optional[bool] = None,
        timezone: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[ScheduledPipeline]:
        """Update a schedule."""
        updates: List[str] = []
        params: List[Any] = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if cron_expression is not None:
            updates.append("cron_expression = ?")
            params.append(cron_expression)

        if inputs is not None:
            updates.append("inputs = ?")
            params.append(json.dumps(inputs))

        if enabled is not None:
            updates.append("enabled = ?")
            params.append(1 if enabled else 0)

        if timezone is not None:
            updates.append("timezone = ?")
            params.append(timezone)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if not updates:
            return self.get(schedule_id, org_id)

        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())

        # Recalculate next run if cron changed
        if cron_expression or timezone:
            schedule = self.get(schedule_id, org_id)
            if schedule:
                next_run = self._calculate_next_run(
                    cron_expression or schedule.cron_expression,
                    timezone or schedule.timezone,
                )
                updates.append("next_run_at = ?")
                params.append(next_run.isoformat() if next_run else None)

        params.extend([schedule_id, org_id])

        self._conn.execute(
            f"UPDATE schedules SET {', '.join(updates)} WHERE id = ? AND org_id = ?",
            params,
        )
        self._conn.commit()

        return self.get(schedule_id, org_id)

    def delete(self, schedule_id: str, org_id: str) -> bool:
        """Delete a schedule."""
        cursor = self._conn.execute(
            "DELETE FROM schedules WHERE id = ? AND org_id = ?",
            (schedule_id, org_id),
        )
        self._conn.commit()
        return bool(cursor.rowcount > 0)

    def get_due_schedules(self) -> List[ScheduledPipeline]:
        """Get all schedules due to run now."""
        now = datetime.utcnow().isoformat()

        cursor = self._conn.execute(
            """
            SELECT * FROM schedules
            WHERE enabled = 1 AND next_run_at <= ?
            ORDER BY next_run_at ASC
            """,
            (now,),
        )

        return [self._row_to_schedule(row) for row in cursor.fetchall()]

    def record_run(
        self,
        schedule_id: str,
        run_id: str,
        scheduled_at: str,
        status: str = "running",
    ) -> str:
        """Record a scheduled run."""
        import uuid

        record_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        self._conn.execute(
            """
            INSERT INTO schedule_runs (
                id, schedule_id, run_id, scheduled_at, started_at, status
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (record_id, schedule_id, run_id, scheduled_at, now, status),
        )

        # Update schedule metadata
        self._conn.execute(
            """
            UPDATE schedules
            SET last_run_at = ?, last_run_id = ?, last_run_status = ?, run_count = run_count + 1
            WHERE id = ?
            """,
            (now, run_id, status, schedule_id),
        )

        self._conn.commit()
        return record_id

    def update_run_status(
        self,
        schedule_id: str,
        run_id: str,
        status: str,
        error_message: Optional[str] = None,
    ):
        """Update the status of a scheduled run."""
        self._conn.execute(
            """
            UPDATE schedule_runs
            SET status = ?, error_message = ?
            WHERE schedule_id = ? AND run_id = ?
            """,
            (status, error_message, schedule_id, run_id),
        )

        # Update schedule metadata
        update_query = "UPDATE schedules SET last_run_status = ?"
        params = [status]

        if status == "failed":
            update_query += ", failure_count = failure_count + 1"

        update_query += " WHERE id = ?"
        params.append(schedule_id)

        self._conn.execute(update_query, params)
        self._conn.commit()

    def update_next_run(self, schedule_id: str):
        """Update the next run time for a schedule."""
        schedule = self.get(schedule_id)
        if not schedule:
            return

        next_run = self._calculate_next_run(schedule.cron_expression, schedule.timezone)

        self._conn.execute(
            "UPDATE schedules SET next_run_at = ? WHERE id = ?",
            (next_run.isoformat() if next_run else None, schedule_id),
        )
        self._conn.commit()

    def get_run_history(
        self,
        schedule_id: str,
        limit: int = 50,
    ) -> List[ScheduleRun]:
        """Get run history for a schedule."""
        cursor = self._conn.execute(
            """
            SELECT * FROM schedule_runs
            WHERE schedule_id = ?
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (schedule_id, limit),
        )

        return [self._row_to_run(row) for row in cursor.fetchall()]

    def _row_to_schedule(self, row) -> ScheduledPipeline:
        """Convert a database row to a ScheduledPipeline."""
        return ScheduledPipeline(
            id=row[0],
            org_id=row[1],
            name=row[2],
            pipeline_id=row[3],
            pipeline_name=row[4],
            cron_expression=row[5],
            inputs=json.loads(row[6]) if row[6] else {},
            enabled=bool(row[7]),
            timezone=row[8] or "UTC",
            description=row[9] or "",
            created_at=row[10],
            updated_at=row[11],
            next_run_at=row[12],
            last_run_at=row[13],
            last_run_id=row[14],
            last_run_status=row[15],
            run_count=row[16] or 0,
            failure_count=row[17] or 0,
        )

    def _row_to_run(self, row) -> ScheduleRun:
        """Convert a database row to a ScheduleRun."""
        return ScheduleRun(
            id=row[0],
            schedule_id=row[1],
            run_id=row[2],
            scheduled_at=row[3],
            started_at=row[4],
            status=row[5],
            error_message=row[6],
        )


# Global instance
_schedule_storage: Optional[ScheduleStorage] = None


def get_schedule_storage() -> ScheduleStorage:
    """Get the global schedule storage instance."""
    global _schedule_storage
    if _schedule_storage is None:
        _schedule_storage = ScheduleStorage()
    return _schedule_storage
