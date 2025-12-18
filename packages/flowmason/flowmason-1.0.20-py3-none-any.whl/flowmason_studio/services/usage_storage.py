"""
LLM Usage Tracking Service.

Tracks and aggregates LLM token usage and costs across runs, pipelines, and organizations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class UsageRecord:
    """A single LLM usage record (per stage)."""
    id: str
    org_id: str
    run_id: str
    pipeline_id: str
    stage_id: str

    # Provider and model info
    provider: str
    model: str

    # Token counts
    input_tokens: int
    output_tokens: int
    total_tokens: int

    # Cost
    cost_usd: float

    # Timing
    duration_ms: int
    recorded_at: str


@dataclass
class UsageSummary:
    """Aggregated usage summary."""
    period_start: str
    period_end: str
    total_runs: int
    total_stages: int

    # Token totals
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int

    # Cost
    total_cost_usd: float

    # Breakdown by provider
    by_provider: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Breakdown by model
    by_model: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Breakdown by pipeline (optional)
    by_pipeline: Optional[Dict[str, Dict[str, Any]]] = None


# Provider pricing per 1M tokens (updated periodically)
PROVIDER_PRICING = {
    "anthropic": {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-haiku-20241022": {"input": 1.00, "output": 5.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    },
    "openai": {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    },
    "google": {
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    },
    "groq": {
        "llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
        "llama-3.1-70b-versatile": {"input": 0.59, "output": 0.79},
        "mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
    },
}


class UsageStorage:
    """Storage for LLM usage tracking using SQLite."""

    def __init__(self):
        """Initialize storage and create tables."""
        from flowmason_studio.services.database import get_connection
        self._conn = get_connection()
        self._create_tables()

    def _create_tables(self):
        """Create usage tables if they don't exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS llm_usage (
                id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                pipeline_id TEXT NOT NULL,
                stage_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                cost_usd REAL NOT NULL,
                duration_ms INTEGER DEFAULT 0,
                recorded_at TEXT NOT NULL
            )
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_org ON llm_usage(org_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_run ON llm_usage(run_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_pipeline ON llm_usage(pipeline_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_recorded ON llm_usage(recorded_at)
        """)

        # Daily aggregates table for faster querying
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS llm_usage_daily (
                id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                pipeline_id TEXT,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                date TEXT NOT NULL,
                run_count INTEGER DEFAULT 0,
                stage_count INTEGER DEFAULT 0,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                total_duration_ms INTEGER DEFAULT 0,
                UNIQUE(org_id, pipeline_id, provider, model, date)
            )
        """)

        self._conn.commit()

    def record_usage(
        self,
        org_id: str,
        run_id: str,
        pipeline_id: str,
        stage_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: Optional[float] = None,
        duration_ms: int = 0,
    ) -> UsageRecord:
        """Record a single LLM usage event."""
        import uuid

        record_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        total_tokens = input_tokens + output_tokens

        # Calculate cost if not provided
        if cost_usd is None:
            cost_usd = self._calculate_cost(provider, model, input_tokens, output_tokens)

        self._conn.execute(
            """
            INSERT INTO llm_usage (
                id, org_id, run_id, pipeline_id, stage_id,
                provider, model, input_tokens, output_tokens, total_tokens,
                cost_usd, duration_ms, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                org_id,
                run_id,
                pipeline_id,
                stage_id,
                provider,
                model,
                input_tokens,
                output_tokens,
                total_tokens,
                cost_usd,
                duration_ms,
                now,
            ),
        )
        self._conn.commit()

        # Update daily aggregate
        self._update_daily_aggregate(
            org_id, pipeline_id, provider, model,
            input_tokens, output_tokens, cost_usd, duration_ms
        )

        return UsageRecord(
            id=record_id,
            org_id=org_id,
            run_id=run_id,
            pipeline_id=pipeline_id,
            stage_id=stage_id,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
            duration_ms=duration_ms,
            recorded_at=now,
        )

    def _calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost based on provider pricing."""
        provider_pricing = PROVIDER_PRICING.get(provider.lower(), {})
        model_pricing = provider_pricing.get(model, {"input": 0, "output": 0})

        input_cost = (input_tokens / 1_000_000) * model_pricing.get("input", 0)
        output_cost = (output_tokens / 1_000_000) * model_pricing.get("output", 0)

        return round(input_cost + output_cost, 6)

    def _update_daily_aggregate(
        self,
        org_id: str,
        pipeline_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        duration_ms: int,
    ):
        """Update daily aggregate for faster querying."""
        import uuid

        today = datetime.utcnow().strftime("%Y-%m-%d")

        # Try to update existing record
        cursor = self._conn.execute(
            """
            UPDATE llm_usage_daily
            SET stage_count = stage_count + 1,
                input_tokens = input_tokens + ?,
                output_tokens = output_tokens + ?,
                total_tokens = total_tokens + ?,
                cost_usd = cost_usd + ?,
                total_duration_ms = total_duration_ms + ?
            WHERE org_id = ? AND pipeline_id = ? AND provider = ? AND model = ? AND date = ?
            """,
            (
                input_tokens,
                output_tokens,
                input_tokens + output_tokens,
                cost_usd,
                duration_ms,
                org_id,
                pipeline_id or "",
                provider,
                model,
                today,
            ),
        )

        if cursor.rowcount == 0:
            # Insert new record
            self._conn.execute(
                """
                INSERT INTO llm_usage_daily (
                    id, org_id, pipeline_id, provider, model, date,
                    run_count, stage_count, input_tokens, output_tokens, total_tokens,
                    cost_usd, total_duration_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    org_id,
                    pipeline_id or "",
                    provider,
                    model,
                    today,
                    0,  # run_count updated separately
                    1,
                    input_tokens,
                    output_tokens,
                    input_tokens + output_tokens,
                    cost_usd,
                    duration_ms,
                ),
            )

        self._conn.commit()

    def increment_run_count(self, org_id: str, pipeline_id: str):
        """Increment run count for daily aggregates."""
        today = datetime.utcnow().strftime("%Y-%m-%d")

        self._conn.execute(
            """
            UPDATE llm_usage_daily
            SET run_count = run_count + 1
            WHERE org_id = ? AND pipeline_id = ? AND date = ?
            """,
            (org_id, pipeline_id or "", today),
        )
        self._conn.commit()

    def get_run_usage(self, run_id: str, org_id: Optional[str] = None) -> List[UsageRecord]:
        """Get all usage records for a run."""
        query = "SELECT * FROM llm_usage WHERE run_id = ?"
        params = [run_id]

        if org_id:
            query += " AND org_id = ?"
            params.append(org_id)

        cursor = self._conn.execute(query, params)
        return [self._row_to_record(row) for row in cursor.fetchall()]

    def get_summary(
        self,
        org_id: str,
        pipeline_id: Optional[str] = None,
        days: int = 30,
        include_by_pipeline: bool = False,
    ) -> UsageSummary:
        """Get aggregated usage summary."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        query = """
            SELECT
                COUNT(DISTINCT run_id) as run_count,
                COUNT(*) as stage_count,
                SUM(input_tokens) as input_tokens,
                SUM(output_tokens) as output_tokens,
                SUM(total_tokens) as total_tokens,
                SUM(cost_usd) as cost_usd
            FROM llm_usage
            WHERE org_id = ? AND recorded_at >= ?
        """
        params = [org_id, start_date.isoformat()]

        if pipeline_id:
            query += " AND pipeline_id = ?"
            params.append(pipeline_id)

        cursor = self._conn.execute(query, params)
        row = cursor.fetchone()

        # Get breakdown by provider
        provider_query = """
            SELECT
                provider,
                SUM(input_tokens) as input_tokens,
                SUM(output_tokens) as output_tokens,
                SUM(total_tokens) as total_tokens,
                SUM(cost_usd) as cost_usd,
                COUNT(*) as request_count
            FROM llm_usage
            WHERE org_id = ? AND recorded_at >= ?
        """
        provider_params = [org_id, start_date.isoformat()]
        if pipeline_id:
            provider_query += " AND pipeline_id = ?"
            provider_params.append(pipeline_id)
        provider_query += " GROUP BY provider"

        cursor = self._conn.execute(provider_query, provider_params)
        by_provider = {}
        for prow in cursor.fetchall():
            by_provider[prow[0]] = {
                "input_tokens": prow[1] or 0,
                "output_tokens": prow[2] or 0,
                "total_tokens": prow[3] or 0,
                "cost_usd": round(prow[4] or 0, 6),
                "request_count": prow[5] or 0,
            }

        # Get breakdown by model
        model_query = """
            SELECT
                provider, model,
                SUM(input_tokens) as input_tokens,
                SUM(output_tokens) as output_tokens,
                SUM(total_tokens) as total_tokens,
                SUM(cost_usd) as cost_usd,
                COUNT(*) as request_count
            FROM llm_usage
            WHERE org_id = ? AND recorded_at >= ?
        """
        model_params = [org_id, start_date.isoformat()]
        if pipeline_id:
            model_query += " AND pipeline_id = ?"
            model_params.append(pipeline_id)
        model_query += " GROUP BY provider, model"

        cursor = self._conn.execute(model_query, model_params)
        by_model = {}
        for mrow in cursor.fetchall():
            model_key = f"{mrow[0]}:{mrow[1]}"
            by_model[model_key] = {
                "provider": mrow[0],
                "model": mrow[1],
                "input_tokens": mrow[2] or 0,
                "output_tokens": mrow[3] or 0,
                "total_tokens": mrow[4] or 0,
                "cost_usd": round(mrow[5] or 0, 6),
                "request_count": mrow[6] or 0,
            }

        # Get breakdown by pipeline (optional)
        by_pipeline = None
        if include_by_pipeline and not pipeline_id:
            pipeline_query = """
                SELECT
                    pipeline_id,
                    COUNT(DISTINCT run_id) as run_count,
                    SUM(input_tokens) as input_tokens,
                    SUM(output_tokens) as output_tokens,
                    SUM(total_tokens) as total_tokens,
                    SUM(cost_usd) as cost_usd
                FROM llm_usage
                WHERE org_id = ? AND recorded_at >= ?
                GROUP BY pipeline_id
            """
            cursor = self._conn.execute(pipeline_query, [org_id, start_date.isoformat()])
            by_pipeline = {}
            for piperow in cursor.fetchall():
                by_pipeline[piperow[0]] = {
                    "run_count": piperow[1] or 0,
                    "input_tokens": piperow[2] or 0,
                    "output_tokens": piperow[3] or 0,
                    "total_tokens": piperow[4] or 0,
                    "cost_usd": round(piperow[5] or 0, 6),
                }

        return UsageSummary(
            period_start=start_date.isoformat(),
            period_end=end_date.isoformat(),
            total_runs=row[0] or 0,
            total_stages=row[1] or 0,
            total_input_tokens=row[2] or 0,
            total_output_tokens=row[3] or 0,
            total_tokens=row[4] or 0,
            total_cost_usd=round(row[5] or 0, 6),
            by_provider=by_provider,
            by_model=by_model,
            by_pipeline=by_pipeline,
        )

    def get_daily_usage(
        self,
        org_id: str,
        pipeline_id: Optional[str] = None,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get daily usage breakdown."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        query = """
            SELECT
                date,
                SUM(run_count) as run_count,
                SUM(stage_count) as stage_count,
                SUM(input_tokens) as input_tokens,
                SUM(output_tokens) as output_tokens,
                SUM(total_tokens) as total_tokens,
                SUM(cost_usd) as cost_usd
            FROM llm_usage_daily
            WHERE org_id = ? AND date >= ?
        """
        params = [org_id, start_date.strftime("%Y-%m-%d")]

        if pipeline_id:
            query += " AND pipeline_id = ?"
            params.append(pipeline_id)

        query += " GROUP BY date ORDER BY date"

        cursor = self._conn.execute(query, params)

        return [
            {
                "date": row[0],
                "run_count": row[1] or 0,
                "stage_count": row[2] or 0,
                "input_tokens": row[3] or 0,
                "output_tokens": row[4] or 0,
                "total_tokens": row[5] or 0,
                "cost_usd": round(row[6] or 0, 6),
            }
            for row in cursor.fetchall()
        ]

    def get_pricing(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Get current pricing information."""
        return PROVIDER_PRICING

    def _row_to_record(self, row) -> UsageRecord:
        """Convert a database row to a UsageRecord."""
        return UsageRecord(
            id=row[0],
            org_id=row[1],
            run_id=row[2],
            pipeline_id=row[3],
            stage_id=row[4],
            provider=row[5],
            model=row[6],
            input_tokens=row[7],
            output_tokens=row[8],
            total_tokens=row[9],
            cost_usd=row[10],
            duration_ms=row[11] or 0,
            recorded_at=row[12],
        )


# Global instance
_usage_storage: Optional[UsageStorage] = None


def get_usage_storage() -> UsageStorage:
    """Get the global usage storage instance."""
    global _usage_storage
    if _usage_storage is None:
        _usage_storage = UsageStorage()
    return _usage_storage
