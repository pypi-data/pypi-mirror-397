"""
Result Store for FlowMason Edge.

Stores execution results for later sync to cloud.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResultStatus(str, Enum):
    """Status of a stored result."""
    PENDING = "pending"      # Not yet synced
    SYNCING = "syncing"      # Currently syncing
    SYNCED = "synced"        # Successfully synced
    FAILED = "failed"        # Sync failed


@dataclass
class StoredResult:
    """A stored execution result."""
    id: str
    run_id: str
    pipeline_name: str
    status: ResultStatus
    created_at: datetime
    synced_at: Optional[datetime]
    sync_attempts: int
    last_error: Optional[str]
    output: Dict[str, Any]
    metadata: Dict[str, Any]


class ResultStore:
    """
    Store for execution results.

    Provides store-and-forward capability for edge deployments.
    Results are stored locally and synced to cloud when online.

    Example:
        store = ResultStore("/var/flowmason/results")

        # Store a result
        store.store(run_id, pipeline_name, output_data)

        # Get pending results for sync
        pending = store.get_pending()

        # Mark as synced
        store.mark_synced(result_id)
    """

    DB_FILE = "results.db"
    MAX_SYNC_ATTEMPTS = 5

    def __init__(
        self,
        store_dir: str,
        max_results: int = 10000,
        retention_days: int = 30,
    ):
        """
        Initialize the result store.

        Args:
            store_dir: Directory for storage
            max_results: Maximum results to store
            retention_days: Days to retain synced results
        """
        self.store_dir = Path(store_dir)
        self.max_results = max_results
        self.retention_days = retention_days

        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self.store_dir / self.DB_FILE
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database."""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                pipeline_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                synced_at TEXT,
                sync_attempts INTEGER DEFAULT 0,
                last_error TEXT,
                output TEXT NOT NULL,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_results_status
            ON results(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_results_pipeline
            ON results(pipeline_name)
        """)

        conn.commit()
        conn.close()

    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self._db_path)

    def store(
        self,
        run_id: str,
        pipeline_name: str,
        output: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StoredResult:
        """
        Store an execution result.

        Args:
            run_id: Run identifier
            pipeline_name: Pipeline name
            output: Execution output
            metadata: Additional metadata

        Returns:
            StoredResult
        """
        import uuid

        result_id = str(uuid.uuid4())
        now = datetime.utcnow()

        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO results (
                    id, run_id, pipeline_name, status, created_at,
                    output, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                result_id,
                run_id,
                pipeline_name,
                ResultStatus.PENDING.value,
                now.isoformat(),
                json.dumps(output),
                json.dumps(metadata or {}),
            ))

            conn.commit()

            logger.debug(f"Stored result: {result_id} for run {run_id}")

            return StoredResult(
                id=result_id,
                run_id=run_id,
                pipeline_name=pipeline_name,
                status=ResultStatus.PENDING,
                created_at=now,
                synced_at=None,
                sync_attempts=0,
                last_error=None,
                output=output,
                metadata=metadata or {},
            )

        finally:
            conn.close()

        # Enforce limits
        self._enforce_limits()

    def get(self, result_id: str) -> Optional[StoredResult]:
        """Get a result by ID."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM results WHERE id = ?",
                (result_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_result(row, cursor.description)

        finally:
            conn.close()

    def get_pending(self, limit: int = 100) -> List[StoredResult]:
        """Get pending results for sync."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM results
                WHERE status IN (?, ?)
                AND sync_attempts < ?
                ORDER BY created_at ASC
                LIMIT ?
            """, (
                ResultStatus.PENDING.value,
                ResultStatus.FAILED.value,
                self.MAX_SYNC_ATTEMPTS,
                limit,
            ))

            rows = cursor.fetchall()
            return [self._row_to_result(row, cursor.description) for row in rows]

        finally:
            conn.close()

    def get_by_pipeline(
        self,
        pipeline_name: str,
        limit: int = 100,
    ) -> List[StoredResult]:
        """Get results for a pipeline."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM results
                WHERE pipeline_name = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (pipeline_name, limit))

            rows = cursor.fetchall()
            return [self._row_to_result(row, cursor.description) for row in rows]

        finally:
            conn.close()

    def mark_syncing(self, result_id: str) -> bool:
        """Mark a result as currently syncing."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE results
                SET status = ?, sync_attempts = sync_attempts + 1
                WHERE id = ?
            """, (ResultStatus.SYNCING.value, result_id))

            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    def mark_synced(self, result_id: str) -> bool:
        """Mark a result as successfully synced."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE results
                SET status = ?, synced_at = ?, last_error = NULL
                WHERE id = ?
            """, (
                ResultStatus.SYNCED.value,
                datetime.utcnow().isoformat(),
                result_id,
            ))

            conn.commit()
            logger.debug(f"Marked result synced: {result_id}")
            return cursor.rowcount > 0

        finally:
            conn.close()

    def mark_failed(self, result_id: str, error: str) -> bool:
        """Mark a result as failed to sync."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE results
                SET status = ?, last_error = ?
                WHERE id = ?
            """, (ResultStatus.FAILED.value, error, result_id))

            conn.commit()
            logger.warning(f"Marked result failed: {result_id} - {error}")
            return cursor.rowcount > 0

        finally:
            conn.close()

    def delete(self, result_id: str) -> bool:
        """Delete a result."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
            conn.commit()
            return cursor.rowcount > 0

        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            # Total count
            cursor.execute("SELECT COUNT(*) FROM results")
            total = cursor.fetchone()[0]

            # By status
            cursor.execute("""
                SELECT status, COUNT(*)
                FROM results
                GROUP BY status
            """)
            by_status = dict(cursor.fetchall())

            # Oldest pending
            cursor.execute("""
                SELECT MIN(created_at) FROM results
                WHERE status = ?
            """, (ResultStatus.PENDING.value,))
            oldest_pending = cursor.fetchone()[0]

            return {
                "total": total,
                "pending": by_status.get(ResultStatus.PENDING.value, 0),
                "synced": by_status.get(ResultStatus.SYNCED.value, 0),
                "failed": by_status.get(ResultStatus.FAILED.value, 0),
                "oldest_pending": oldest_pending,
            }

        finally:
            conn.close()

    def _row_to_result(self, row, description) -> StoredResult:
        """Convert database row to StoredResult."""
        columns = [col[0] for col in description]
        data = dict(zip(columns, row))

        return StoredResult(
            id=data["id"],
            run_id=data["run_id"],
            pipeline_name=data["pipeline_name"],
            status=ResultStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            synced_at=datetime.fromisoformat(data["synced_at"]) if data["synced_at"] else None,
            sync_attempts=data["sync_attempts"],
            last_error=data["last_error"],
            output=json.loads(data["output"]),
            metadata=json.loads(data["metadata"]) if data["metadata"] else {},
        )

    def _enforce_limits(self) -> None:
        """Enforce storage limits."""
        conn = self._get_conn()
        cursor = conn.cursor()

        try:
            # Delete old synced results
            cutoff = datetime.utcnow().replace(
                day=datetime.utcnow().day - self.retention_days
            )

            cursor.execute("""
                DELETE FROM results
                WHERE status = ? AND synced_at < ?
            """, (ResultStatus.SYNCED.value, cutoff.isoformat()))

            # Delete excess results (keep most recent)
            cursor.execute("""
                DELETE FROM results
                WHERE id NOT IN (
                    SELECT id FROM results
                    ORDER BY created_at DESC
                    LIMIT ?
                )
            """, (self.max_results,))

            conn.commit()

        finally:
            conn.close()
