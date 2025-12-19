"""
Event Trigger Storage Service.

Handles storage and retrieval of event triggers using SQLite.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from flowmason_studio.models.triggers import (
    EventTrigger,
    TriggerEvent,
    TriggerStatus,
    TriggerType,
)


class TriggerStorage:
    """SQLite-based storage for event triggers."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the trigger storage."""
        if db_path is None:
            db_path = Path.home() / ".flowmason" / "triggers.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database tables."""
        conn = self._get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS triggers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    pipeline_id TEXT NOT NULL,
                    trigger_type TEXT NOT NULL,
                    config TEXT NOT NULL,
                    enabled INTEGER DEFAULT 1,
                    max_concurrent INTEGER DEFAULT 1,
                    cooldown_seconds REAL DEFAULT 0,
                    default_inputs TEXT DEFAULT '{}',
                    status TEXT DEFAULT 'active',
                    last_triggered_at TEXT,
                    trigger_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by TEXT
                );

                CREATE TABLE IF NOT EXISTS trigger_events (
                    id TEXT PRIMARY KEY,
                    trigger_id TEXT NOT NULL,
                    pipeline_id TEXT NOT NULL,
                    run_id TEXT,
                    event_type TEXT NOT NULL,
                    event_data TEXT DEFAULT '{}',
                    resolved_inputs TEXT DEFAULT '{}',
                    status TEXT DEFAULT 'pending',
                    error_message TEXT,
                    occurred_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    FOREIGN KEY (trigger_id) REFERENCES triggers(id)
                );

                CREATE INDEX IF NOT EXISTS idx_triggers_pipeline
                    ON triggers(pipeline_id);
                CREATE INDEX IF NOT EXISTS idx_triggers_type
                    ON triggers(trigger_type);
                CREATE INDEX IF NOT EXISTS idx_triggers_enabled
                    ON triggers(enabled);
                CREATE INDEX IF NOT EXISTS idx_events_trigger
                    ON trigger_events(trigger_id);
                CREATE INDEX IF NOT EXISTS idx_events_status
                    ON trigger_events(status);
                CREATE INDEX IF NOT EXISTS idx_events_occurred
                    ON trigger_events(occurred_at);
            """)
            conn.commit()
        finally:
            conn.close()

    # Trigger CRUD

    def create_trigger(
        self,
        name: str,
        pipeline_id: str,
        trigger_type: TriggerType,
        config: Dict[str, Any],
        description: str = "",
        enabled: bool = True,
        max_concurrent: int = 1,
        cooldown_seconds: float = 0,
        default_inputs: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
    ) -> EventTrigger:
        """Create a new trigger."""
        trigger_id = str(uuid.uuid4())
        now = datetime.utcnow()
        now_str = now.isoformat()

        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO triggers
                   (id, name, description, pipeline_id, trigger_type, config,
                    enabled, max_concurrent, cooldown_seconds, default_inputs,
                    status, created_at, updated_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    trigger_id, name, description, pipeline_id,
                    trigger_type.value, json.dumps(config),
                    1 if enabled else 0, max_concurrent, cooldown_seconds,
                    json.dumps(default_inputs or {}),
                    TriggerStatus.ACTIVE.value, now_str, now_str, created_by
                )
            )
            conn.commit()

            return EventTrigger(
                id=trigger_id,
                name=name,
                description=description,
                pipeline_id=pipeline_id,
                trigger_type=trigger_type,
                config=config,
                enabled=enabled,
                max_concurrent=max_concurrent,
                cooldown_seconds=cooldown_seconds,
                default_inputs=default_inputs or {},
                status=TriggerStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                created_by=created_by,
            )
        finally:
            conn.close()

    def get_trigger(self, trigger_id: str) -> Optional[EventTrigger]:
        """Get a trigger by ID."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM triggers WHERE id = ?",
                (trigger_id,)
            ).fetchone()

            if not row:
                return None

            return self._row_to_trigger(row)
        finally:
            conn.close()

    def _row_to_trigger(self, row: sqlite3.Row) -> EventTrigger:
        """Convert a database row to an EventTrigger."""
        return EventTrigger(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            pipeline_id=row["pipeline_id"],
            trigger_type=TriggerType(row["trigger_type"]),
            config=json.loads(row["config"]),
            enabled=bool(row["enabled"]),
            max_concurrent=row["max_concurrent"],
            cooldown_seconds=row["cooldown_seconds"],
            default_inputs=json.loads(row["default_inputs"]),
            status=TriggerStatus(row["status"]),
            last_triggered_at=datetime.fromisoformat(row["last_triggered_at"])
                if row["last_triggered_at"] else None,
            trigger_count=row["trigger_count"],
            error_message=row["error_message"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            created_by=row["created_by"],
        )

    def update_trigger(
        self,
        trigger_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        enabled: Optional[bool] = None,
        max_concurrent: Optional[int] = None,
        cooldown_seconds: Optional[float] = None,
        default_inputs: Optional[Dict[str, Any]] = None,
    ) -> Optional[EventTrigger]:
        """Update a trigger."""
        updates: List[str] = []
        values: List[Any] = []

        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        if config is not None:
            updates.append("config = ?")
            values.append(json.dumps(config))
        if enabled is not None:
            updates.append("enabled = ?")
            values.append(1 if enabled else 0)
        if max_concurrent is not None:
            updates.append("max_concurrent = ?")
            values.append(max_concurrent)
        if cooldown_seconds is not None:
            updates.append("cooldown_seconds = ?")
            values.append(cooldown_seconds)
        if default_inputs is not None:
            updates.append("default_inputs = ?")
            values.append(json.dumps(default_inputs))

        if not updates:
            return self.get_trigger(trigger_id)

        updates.append("updated_at = ?")
        values.append(datetime.utcnow().isoformat())
        values.append(trigger_id)

        conn = self._get_conn()
        try:
            result = conn.execute(
                f"UPDATE triggers SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()

            if result.rowcount == 0:
                return None

            return self.get_trigger(trigger_id)
        finally:
            conn.close()

    def delete_trigger(self, trigger_id: str) -> bool:
        """Delete a trigger and its events."""
        conn = self._get_conn()
        try:
            # Delete events first
            conn.execute(
                "DELETE FROM trigger_events WHERE trigger_id = ?",
                (trigger_id,)
            )
            result = conn.execute(
                "DELETE FROM triggers WHERE id = ?",
                (trigger_id,)
            )
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    def list_triggers(
        self,
        pipeline_id: Optional[str] = None,
        trigger_type: Optional[TriggerType] = None,
        enabled_only: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[EventTrigger], int]:
        """List triggers with filtering."""
        conditions: List[str] = []
        values: List[Any] = []

        if pipeline_id:
            conditions.append("pipeline_id = ?")
            values.append(pipeline_id)
        if trigger_type:
            conditions.append("trigger_type = ?")
            values.append(trigger_type.value)
        if enabled_only:
            conditions.append("enabled = 1")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        conn = self._get_conn()
        try:
            # Get total count
            count_row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM triggers {where_clause}",
                values
            ).fetchone()
            total = count_row["cnt"] if count_row else 0

            # Get paginated results
            offset = (page - 1) * page_size
            rows = conn.execute(
                f"""SELECT * FROM triggers {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?""",
                values + [page_size, offset]
            ).fetchall()

            triggers = [self._row_to_trigger(row) for row in rows]
            return triggers, total
        finally:
            conn.close()

    def get_active_triggers_by_type(
        self, trigger_type: TriggerType
    ) -> List[EventTrigger]:
        """Get all active triggers of a specific type."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                """SELECT * FROM triggers
                   WHERE trigger_type = ? AND enabled = 1
                   AND status = ?""",
                (trigger_type.value, TriggerStatus.ACTIVE.value)
            ).fetchall()

            return [self._row_to_trigger(row) for row in rows]
        finally:
            conn.close()

    # Trigger Status Updates

    def update_trigger_status(
        self,
        trigger_id: str,
        status: TriggerStatus,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update trigger status."""
        conn = self._get_conn()
        try:
            result = conn.execute(
                """UPDATE triggers
                   SET status = ?, error_message = ?, updated_at = ?
                   WHERE id = ?""",
                (
                    status.value,
                    error_message,
                    datetime.utcnow().isoformat(),
                    trigger_id
                )
            )
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    def record_trigger_fired(self, trigger_id: str) -> bool:
        """Record that a trigger was fired."""
        conn = self._get_conn()
        try:
            result = conn.execute(
                """UPDATE triggers
                   SET last_triggered_at = ?,
                       trigger_count = trigger_count + 1,
                       updated_at = ?
                   WHERE id = ?""",
                (
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                    trigger_id
                )
            )
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    def can_trigger(self, trigger_id: str) -> bool:
        """Check if a trigger can fire (cooldown check)."""
        trigger = self.get_trigger(trigger_id)
        if not trigger:
            return False
        if not trigger.enabled:
            return False
        if trigger.status != TriggerStatus.ACTIVE:
            return False
        if trigger.cooldown_seconds <= 0:
            return True
        if not trigger.last_triggered_at:
            return True

        cooldown_end = trigger.last_triggered_at + timedelta(
            seconds=trigger.cooldown_seconds
        )
        return datetime.utcnow() >= cooldown_end

    # Trigger Events

    def create_event(
        self,
        trigger_id: str,
        pipeline_id: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
        resolved_inputs: Optional[Dict[str, Any]] = None,
    ) -> TriggerEvent:
        """Create a trigger event record."""
        event_id = str(uuid.uuid4())
        now = datetime.utcnow()

        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO trigger_events
                   (id, trigger_id, pipeline_id, event_type, event_data,
                    resolved_inputs, status, occurred_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    event_id, trigger_id, pipeline_id, event_type,
                    json.dumps(event_data or {}),
                    json.dumps(resolved_inputs or {}),
                    "pending", now.isoformat()
                )
            )
            conn.commit()

            return TriggerEvent(
                id=event_id,
                trigger_id=trigger_id,
                pipeline_id=pipeline_id,
                event_type=event_type,
                event_data=event_data or {},
                resolved_inputs=resolved_inputs or {},
                status="pending",
                occurred_at=now,
            )
        finally:
            conn.close()

    def update_event(
        self,
        event_id: str,
        status: Optional[str] = None,
        run_id: Optional[str] = None,
        error_message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> Optional[TriggerEvent]:
        """Update a trigger event."""
        updates: List[str] = []
        values: List[Any] = []

        if status is not None:
            updates.append("status = ?")
            values.append(status)
        if run_id is not None:
            updates.append("run_id = ?")
            values.append(run_id)
        if error_message is not None:
            updates.append("error_message = ?")
            values.append(error_message)
        if started_at is not None:
            updates.append("started_at = ?")
            values.append(started_at.isoformat())
        if completed_at is not None:
            updates.append("completed_at = ?")
            values.append(completed_at.isoformat())

        if not updates:
            return self.get_event(event_id)

        values.append(event_id)

        conn = self._get_conn()
        try:
            conn.execute(
                f"UPDATE trigger_events SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()
            return self.get_event(event_id)
        finally:
            conn.close()

    def get_event(self, event_id: str) -> Optional[TriggerEvent]:
        """Get an event by ID."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM trigger_events WHERE id = ?",
                (event_id,)
            ).fetchone()

            if not row:
                return None

            return self._row_to_event(row)
        finally:
            conn.close()

    def _row_to_event(self, row: sqlite3.Row) -> TriggerEvent:
        """Convert a database row to a TriggerEvent."""
        return TriggerEvent(
            id=row["id"],
            trigger_id=row["trigger_id"],
            pipeline_id=row["pipeline_id"],
            run_id=row["run_id"],
            event_type=row["event_type"],
            event_data=json.loads(row["event_data"]),
            resolved_inputs=json.loads(row["resolved_inputs"]),
            status=row["status"],
            error_message=row["error_message"],
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            started_at=datetime.fromisoformat(row["started_at"])
                if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"])
                if row["completed_at"] else None,
        )

    def list_events(
        self,
        trigger_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        status: Optional[str] = None,
        since: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[TriggerEvent], int]:
        """List trigger events with filtering."""
        conditions: List[str] = []
        values: List[Any] = []

        if trigger_id:
            conditions.append("trigger_id = ?")
            values.append(trigger_id)
        if pipeline_id:
            conditions.append("pipeline_id = ?")
            values.append(pipeline_id)
        if status:
            conditions.append("status = ?")
            values.append(status)
        if since:
            conditions.append("occurred_at >= ?")
            values.append(since.isoformat())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        conn = self._get_conn()
        try:
            count_row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM trigger_events {where_clause}",
                values
            ).fetchone()
            total = count_row["cnt"] if count_row else 0

            offset = (page - 1) * page_size
            rows = conn.execute(
                f"""SELECT * FROM trigger_events {where_clause}
                    ORDER BY occurred_at DESC
                    LIMIT ? OFFSET ?""",
                values + [page_size, offset]
            ).fetchall()

            events = [self._row_to_event(row) for row in rows]
            return events, total
        finally:
            conn.close()

    # Statistics

    def get_stats(self) -> Dict[str, Any]:
        """Get trigger statistics."""
        conn = self._get_conn()
        try:
            # Trigger counts
            trigger_counts = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN status = 'paused' THEN 1 ELSE 0 END) as paused,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error
                FROM triggers
            """).fetchone()

            # Triggers by type
            type_rows = conn.execute("""
                SELECT trigger_type, COUNT(*) as cnt
                FROM triggers
                GROUP BY trigger_type
            """).fetchall()
            triggers_by_type = {row["trigger_type"]: row["cnt"] for row in type_rows}

            # Event counts for last 24 hours
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            event_counts = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM trigger_events
                WHERE occurred_at >= ?
            """, (yesterday,)).fetchone()

            return {
                "total_triggers": trigger_counts["total"] or 0,
                "active_triggers": trigger_counts["active"] or 0,
                "paused_triggers": trigger_counts["paused"] or 0,
                "error_triggers": trigger_counts["error"] or 0,
                "total_events_24h": event_counts["total"] or 0,
                "successful_events_24h": event_counts["successful"] or 0,
                "failed_events_24h": event_counts["failed"] or 0,
                "triggers_by_type": triggers_by_type,
            }
        finally:
            conn.close()


# Global instance
_trigger_storage: Optional[TriggerStorage] = None


def get_trigger_storage() -> TriggerStorage:
    """Get the global trigger storage instance."""
    global _trigger_storage
    if _trigger_storage is None:
        _trigger_storage = TriggerStorage()
    return _trigger_storage


def reset_trigger_storage() -> None:
    """Reset the global trigger storage instance."""
    global _trigger_storage
    _trigger_storage = None
