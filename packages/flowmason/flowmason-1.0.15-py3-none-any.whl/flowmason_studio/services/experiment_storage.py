"""
Experiment Storage Service.

Handles storage and retrieval of A/B test experiments and metrics.
"""

import hashlib
import json
import math
import random
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from flowmason_studio.models.experiments import (
    Experiment,
    ExperimentResults,
    ExperimentStatus,
    MetricAggregation,
    MetricDefinition,
    MetricRecord,
    MetricType,
    PromptVariant,
    VariantStats,
)


class ExperimentStorage:
    """SQLite-based storage for experiments and metrics."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the experiment storage."""
        if db_path is None:
            db_path = Path.home() / ".flowmason" / "experiments.db"
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
                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    org_id TEXT NOT NULL,
                    status TEXT DEFAULT 'draft',
                    variants TEXT NOT NULL,
                    metrics TEXT DEFAULT '[]',
                    primary_metric TEXT DEFAULT 'rating',
                    default_model TEXT,
                    default_temperature REAL,
                    default_max_tokens INTEGER,
                    pipeline_ids TEXT DEFAULT '[]',
                    stage_ids TEXT DEFAULT '[]',
                    user_percentage REAL DEFAULT 100.0,
                    min_samples_per_variant INTEGER DEFAULT 100,
                    start_time TEXT,
                    end_time TEXT,
                    winner_variant_id TEXT,
                    confidence_level REAL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by TEXT,
                    tags TEXT DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS metric_records (
                    id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    variant_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    run_id TEXT,
                    pipeline_id TEXT,
                    stage_id TEXT,
                    user_id TEXT,
                    recorded_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (experiment_id) REFERENCES experiments(id)
                );

                CREATE TABLE IF NOT EXISTS variant_assignments (
                    user_hash TEXT NOT NULL,
                    experiment_id TEXT NOT NULL,
                    variant_id TEXT NOT NULL,
                    assigned_at TEXT NOT NULL,
                    PRIMARY KEY (user_hash, experiment_id)
                );

                CREATE INDEX IF NOT EXISTS idx_experiments_org
                    ON experiments(org_id);
                CREATE INDEX IF NOT EXISTS idx_experiments_status
                    ON experiments(status);
                CREATE INDEX IF NOT EXISTS idx_metrics_experiment
                    ON metric_records(experiment_id);
                CREATE INDEX IF NOT EXISTS idx_metrics_variant
                    ON metric_records(variant_id);
                CREATE INDEX IF NOT EXISTS idx_metrics_name
                    ON metric_records(metric_name);
                CREATE INDEX IF NOT EXISTS idx_assignments_experiment
                    ON variant_assignments(experiment_id);
            """)
            conn.commit()
        finally:
            conn.close()

    # Experiment CRUD

    def create_experiment(
        self,
        name: str,
        org_id: str,
        variants: List[PromptVariant],
        description: str = "",
        metrics: Optional[List[MetricDefinition]] = None,
        primary_metric: str = "rating",
        default_model: Optional[str] = None,
        default_temperature: Optional[float] = None,
        default_max_tokens: Optional[int] = None,
        pipeline_ids: Optional[List[str]] = None,
        stage_ids: Optional[List[str]] = None,
        user_percentage: float = 100.0,
        min_samples_per_variant: int = 100,
        created_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Experiment:
        """Create a new experiment."""
        experiment_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Ensure variants have IDs
        for i, variant in enumerate(variants):
            if not variant.id:
                variant.id = str(uuid.uuid4())
            if not variant.created_at:
                variant.created_at = now

        # Set default metrics if none provided
        if not metrics:
            metrics = [
                MetricDefinition(
                    name="latency",
                    type=MetricType.LATENCY,
                    description="Response latency in ms",
                    higher_is_better=False,
                ),
                MetricDefinition(
                    name="rating",
                    type=MetricType.RATING,
                    description="User rating (1-5)",
                    higher_is_better=True,
                ),
            ]

        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO experiments
                   (id, name, description, org_id, status, variants, metrics,
                    primary_metric, default_model, default_temperature,
                    default_max_tokens, pipeline_ids, stage_ids, user_percentage,
                    min_samples_per_variant, created_at, updated_at, created_by, tags)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    experiment_id, name, description, org_id,
                    ExperimentStatus.DRAFT.value,
                    json.dumps([v.model_dump() for v in variants], default=str),
                    json.dumps([m.model_dump() for m in metrics], default=str),
                    primary_metric, default_model, default_temperature,
                    default_max_tokens,
                    json.dumps(pipeline_ids or []),
                    json.dumps(stage_ids or []),
                    user_percentage, min_samples_per_variant,
                    now.isoformat(), now.isoformat(),
                    created_by, json.dumps(tags or [])
                )
            )
            conn.commit()

            return Experiment(
                id=experiment_id,
                name=name,
                description=description,
                org_id=org_id,
                status=ExperimentStatus.DRAFT,
                variants=variants,
                metrics=metrics,
                primary_metric=primary_metric,
                default_model=default_model,
                default_temperature=default_temperature,
                default_max_tokens=default_max_tokens,
                pipeline_ids=pipeline_ids or [],
                stage_ids=stage_ids or [],
                user_percentage=user_percentage,
                min_samples_per_variant=min_samples_per_variant,
                created_at=now,
                updated_at=now,
                created_by=created_by,
                tags=tags or [],
            )
        finally:
            conn.close()

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Get an experiment by ID."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM experiments WHERE id = ?",
                (experiment_id,)
            ).fetchone()

            if not row:
                return None

            return self._row_to_experiment(row)
        finally:
            conn.close()

    def _row_to_experiment(self, row: sqlite3.Row) -> Experiment:
        """Convert a database row to an Experiment."""
        variants_data = json.loads(row["variants"])
        variants = [PromptVariant(**v) for v in variants_data]

        metrics_data = json.loads(row["metrics"])
        metrics = [MetricDefinition(**m) for m in metrics_data]

        return Experiment(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            org_id=row["org_id"],
            status=ExperimentStatus(row["status"]),
            variants=variants,
            metrics=metrics,
            primary_metric=row["primary_metric"],
            default_model=row["default_model"],
            default_temperature=row["default_temperature"],
            default_max_tokens=row["default_max_tokens"],
            pipeline_ids=json.loads(row["pipeline_ids"]),
            stage_ids=json.loads(row["stage_ids"]),
            user_percentage=row["user_percentage"],
            min_samples_per_variant=row["min_samples_per_variant"],
            start_time=datetime.fromisoformat(row["start_time"])
                if row["start_time"] else None,
            end_time=datetime.fromisoformat(row["end_time"])
                if row["end_time"] else None,
            winner_variant_id=row["winner_variant_id"],
            confidence_level=row["confidence_level"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            created_by=row["created_by"],
            tags=json.loads(row["tags"]),
        )

    def update_experiment(
        self,
        experiment_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[ExperimentStatus] = None,
        variants: Optional[List[PromptVariant]] = None,
        metrics: Optional[List[MetricDefinition]] = None,
        primary_metric: Optional[str] = None,
        user_percentage: Optional[float] = None,
        min_samples_per_variant: Optional[int] = None,
        winner_variant_id: Optional[str] = None,
        confidence_level: Optional[float] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[Experiment]:
        """Update an experiment."""
        updates: List[str] = []
        values: List[Any] = []

        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        if status is not None:
            updates.append("status = ?")
            values.append(status.value)
            if status == ExperimentStatus.RUNNING:
                updates.append("start_time = ?")
                values.append(datetime.utcnow().isoformat())
            elif status == ExperimentStatus.COMPLETED:
                updates.append("end_time = ?")
                values.append(datetime.utcnow().isoformat())
        if variants is not None:
            updates.append("variants = ?")
            values.append(json.dumps([v.model_dump() for v in variants]))
        if metrics is not None:
            updates.append("metrics = ?")
            values.append(json.dumps([m.model_dump() for m in metrics]))
        if primary_metric is not None:
            updates.append("primary_metric = ?")
            values.append(primary_metric)
        if user_percentage is not None:
            updates.append("user_percentage = ?")
            values.append(user_percentage)
        if min_samples_per_variant is not None:
            updates.append("min_samples_per_variant = ?")
            values.append(min_samples_per_variant)
        if winner_variant_id is not None:
            updates.append("winner_variant_id = ?")
            values.append(winner_variant_id)
        if confidence_level is not None:
            updates.append("confidence_level = ?")
            values.append(confidence_level)
        if tags is not None:
            updates.append("tags = ?")
            values.append(json.dumps(tags))

        if not updates:
            return self.get_experiment(experiment_id)

        updates.append("updated_at = ?")
        values.append(datetime.utcnow().isoformat())
        values.append(experiment_id)

        conn = self._get_conn()
        try:
            conn.execute(
                f"UPDATE experiments SET {', '.join(updates)} WHERE id = ?",
                values
            )
            conn.commit()
            return self.get_experiment(experiment_id)
        finally:
            conn.close()

    def delete_experiment(self, experiment_id: str) -> bool:
        """Delete an experiment and its data."""
        conn = self._get_conn()
        try:
            conn.execute(
                "DELETE FROM metric_records WHERE experiment_id = ?",
                (experiment_id,)
            )
            conn.execute(
                "DELETE FROM variant_assignments WHERE experiment_id = ?",
                (experiment_id,)
            )
            result = conn.execute(
                "DELETE FROM experiments WHERE id = ?",
                (experiment_id,)
            )
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    def list_experiments(
        self,
        org_id: str,
        status: Optional[ExperimentStatus] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Experiment], int]:
        """List experiments for an organization."""
        conditions = ["org_id = ?"]
        values: List[Any] = [org_id]

        if status:
            conditions.append("status = ?")
            values.append(status.value)

        where_clause = " AND ".join(conditions)

        conn = self._get_conn()
        try:
            count_row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM experiments WHERE {where_clause}",
                values
            ).fetchone()
            total = count_row["cnt"] if count_row else 0

            offset = (page - 1) * page_size
            rows = conn.execute(
                f"""SELECT * FROM experiments WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?""",
                values + [page_size, offset]
            ).fetchall()

            experiments = [self._row_to_experiment(row) for row in rows]
            return experiments, total
        finally:
            conn.close()

    # Variant Selection

    def select_variant(
        self,
        experiment_id: str,
        user_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        stage_id: Optional[str] = None,
    ) -> Optional[Tuple[Experiment, PromptVariant]]:
        """Select a variant for a user.

        Uses consistent hashing for sticky assignment.
        """
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            return None

        if experiment.status != ExperimentStatus.RUNNING:
            return None

        if not experiment.variants:
            return None

        # Check targeting
        if experiment.pipeline_ids and pipeline_id not in experiment.pipeline_ids:
            return None
        if experiment.stage_ids and stage_id not in experiment.stage_ids:
            return None

        # Check user percentage
        if experiment.user_percentage < 100:
            user_hash = self._hash_user(user_id or "anonymous", experiment_id)
            hash_value = int(user_hash, 16) % 100
            if hash_value >= experiment.user_percentage:
                return None

        # Check for existing assignment
        existing = self._get_assignment(user_id or "anonymous", experiment_id)
        if existing:
            for variant in experiment.variants:
                if variant.id == existing:
                    self._increment_impressions(experiment_id, variant.id)
                    return experiment, variant

        # Select new variant based on weights
        selected_variant = self._weighted_random_selection(experiment.variants, user_id)
        if selected_variant is None:
            return None

        self._save_assignment(user_id or "anonymous", experiment_id, selected_variant.id)
        self._increment_impressions(experiment_id, selected_variant.id)

        return experiment, selected_variant

    def _hash_user(self, user_id: str, experiment_id: str) -> str:
        """Create a consistent hash for user assignment."""
        combined = f"{user_id}:{experiment_id}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _get_assignment(
        self, user_id: str, experiment_id: str
    ) -> Optional[str]:
        """Get existing variant assignment for a user."""
        user_hash = self._hash_user(user_id, experiment_id)
        conn = self._get_conn()
        try:
            row = conn.execute(
                """SELECT variant_id FROM variant_assignments
                   WHERE user_hash = ? AND experiment_id = ?""",
                (user_hash, experiment_id)
            ).fetchone()
            return row["variant_id"] if row else None
        finally:
            conn.close()

    def _save_assignment(
        self, user_id: str, experiment_id: str, variant_id: str
    ) -> None:
        """Save variant assignment for a user."""
        user_hash = self._hash_user(user_id, experiment_id)
        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT OR REPLACE INTO variant_assignments
                   (user_hash, experiment_id, variant_id, assigned_at)
                   VALUES (?, ?, ?, ?)""",
                (user_hash, experiment_id, variant_id, datetime.utcnow().isoformat())
            )
            conn.commit()
        finally:
            conn.close()

    def _weighted_random_selection(
        self,
        variants: List[PromptVariant],
        user_id: Optional[str] = None,
    ) -> Optional[PromptVariant]:
        """Select a variant based on weights."""
        if not variants:
            return None

        total_weight = sum(v.weight for v in variants)
        if total_weight <= 0:
            return random.choice(variants)

        # Use user_id for consistent randomization if provided
        if user_id:
            random.seed(hash(user_id))

        r = random.uniform(0, total_weight)
        cumulative: float = 0.0

        for variant in variants:
            cumulative += variant.weight
            if r <= cumulative:
                return variant

        return variants[-1]

    def _increment_impressions(
        self, experiment_id: str, variant_id: str
    ) -> None:
        """Increment impression count for a variant."""
        conn = self._get_conn()
        try:
            # Get current variants
            row = conn.execute(
                "SELECT variants FROM experiments WHERE id = ?",
                (experiment_id,)
            ).fetchone()

            if row:
                variants_data = json.loads(row["variants"])
                for v in variants_data:
                    if v["id"] == variant_id:
                        v["impressions"] = v.get("impressions", 0) + 1
                        break

                conn.execute(
                    "UPDATE experiments SET variants = ? WHERE id = ?",
                    (json.dumps(variants_data), experiment_id)
                )
                conn.commit()
        finally:
            conn.close()

    # Metric Recording

    def record_metric(
        self,
        experiment_id: str,
        variant_id: str,
        metric_name: str,
        value: float,
        run_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        stage_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MetricRecord:
        """Record a metric data point."""
        record_id = str(uuid.uuid4())
        now = datetime.utcnow()

        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO metric_records
                   (id, experiment_id, variant_id, metric_name, value,
                    run_id, pipeline_id, stage_id, user_id, recorded_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record_id, experiment_id, variant_id, metric_name, value,
                    run_id, pipeline_id, stage_id, user_id, now.isoformat(),
                    json.dumps(metadata or {})
                )
            )
            conn.commit()

            return MetricRecord(
                id=record_id,
                experiment_id=experiment_id,
                variant_id=variant_id,
                metric_name=metric_name,
                value=value,
                run_id=run_id,
                pipeline_id=pipeline_id,
                stage_id=stage_id,
                user_id=user_id,
                recorded_at=now,
                metadata=metadata or {},
            )
        finally:
            conn.close()

    def record_metrics(
        self,
        experiment_id: str,
        variant_id: str,
        metrics: Dict[str, float],
        run_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        stage_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[MetricRecord]:
        """Record multiple metrics at once."""
        records = []
        for metric_name, value in metrics.items():
            record = self.record_metric(
                experiment_id=experiment_id,
                variant_id=variant_id,
                metric_name=metric_name,
                value=value,
                run_id=run_id,
                pipeline_id=pipeline_id,
                stage_id=stage_id,
                user_id=user_id,
            )
            records.append(record)
        return records

    # Results and Analysis

    def get_results(self, experiment_id: str) -> Optional[ExperimentResults]:
        """Get experiment results with statistical analysis."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            return None

        conn = self._get_conn()
        try:
            variant_stats = []
            control_stats: Optional[VariantStats] = None

            for variant in experiment.variants:
                stats = self._calculate_variant_stats(
                    conn, experiment_id, variant, experiment.metrics
                )
                variant_stats.append(stats)

                if variant.is_control:
                    control_stats = stats

            # Calculate lift vs control
            if control_stats:
                primary_metric = experiment.primary_metric
                control_mean = control_stats.metrics.get(primary_metric, {}).get("mean")

                if control_mean is not None and control_mean != 0:
                    for stats in variant_stats:
                        if stats.variant_id != control_stats.variant_id:
                            variant_mean = stats.metrics.get(primary_metric, {}).get("mean")
                            if variant_mean is not None:
                                stats.lift_vs_control = (
                                    (variant_mean - control_mean) / abs(control_mean)
                                ) * 100

                                # Calculate p-value using t-test approximation
                                stats.p_value = self._calculate_p_value(
                                    conn, experiment_id,
                                    control_stats.variant_id, stats.variant_id,
                                    primary_metric
                                )
                                stats.is_significant = (
                                    stats.p_value is not None and
                                    stats.p_value < 0.05
                                )

            # Determine winner
            has_winner = False
            winner_id = None
            winner_name = None
            confidence = None
            recommendation = ""

            min_samples = experiment.min_samples_per_variant
            all_have_min_samples = all(
                s.samples >= min_samples for s in variant_stats
            )

            if all_have_min_samples:
                # Find variant with best primary metric
                metric_def = next(
                    (m for m in experiment.metrics
                     if m.name == experiment.primary_metric),
                    None
                )
                higher_is_better = metric_def.higher_is_better if metric_def else True

                best_stats = None
                best_value = None

                for stats in variant_stats:
                    mean = stats.metrics.get(experiment.primary_metric, {}).get("mean")
                    if mean is not None:
                        if best_value is None:
                            best_value = mean
                            best_stats = stats
                        elif higher_is_better and mean > best_value:
                            best_value = mean
                            best_stats = stats
                        elif not higher_is_better and mean < best_value:
                            best_value = mean
                            best_stats = stats

                if best_stats and best_stats.is_significant:
                    has_winner = True
                    winner_id = best_stats.variant_id
                    winner_name = best_stats.variant_name
                    confidence = 1 - (best_stats.p_value or 0.05)

                    if best_stats.lift_vs_control:
                        recommendation = (
                            f"'{winner_name}' outperforms control by "
                            f"{best_stats.lift_vs_control:.1f}% on {experiment.primary_metric}. "
                            f"Confidence: {confidence*100:.1f}%"
                        )
                else:
                    recommendation = (
                        "No statistically significant winner yet. "
                        "Continue collecting data."
                    )
            else:
                samples_needed = max(
                    0, min_samples - min(s.samples for s in variant_stats)
                )
                recommendation = (
                    f"Need {samples_needed} more samples per variant "
                    f"to reach minimum of {min_samples}."
                )

            total_samples = sum(s.samples for s in variant_stats)

            duration_hours = None
            if experiment.start_time:
                end = experiment.end_time or datetime.utcnow()
                duration_hours = (end - experiment.start_time).total_seconds() / 3600

            return ExperimentResults(
                experiment_id=experiment_id,
                experiment_name=experiment.name,
                status=experiment.status,
                primary_metric=experiment.primary_metric,
                variant_stats=variant_stats,
                has_winner=has_winner,
                winner_variant_id=winner_id,
                winner_variant_name=winner_name,
                confidence_level=confidence,
                recommendation=recommendation,
                total_samples=total_samples,
                start_time=experiment.start_time,
                end_time=experiment.end_time,
                duration_hours=duration_hours,
            )
        finally:
            conn.close()

    def _calculate_variant_stats(
        self,
        conn: sqlite3.Connection,
        experiment_id: str,
        variant: PromptVariant,
        metric_defs: List[MetricDefinition],
    ) -> VariantStats:
        """Calculate statistics for a variant."""
        metrics: Dict[str, Dict[str, float]] = {}

        for metric_def in metric_defs:
            rows = conn.execute(
                """SELECT value FROM metric_records
                   WHERE experiment_id = ? AND variant_id = ?
                   AND metric_name = ?
                   ORDER BY value""",
                (experiment_id, variant.id, metric_def.name)
            ).fetchall()

            if rows:
                values = [row["value"] for row in rows]
                n = len(values)
                mean = sum(values) / n
                variance = sum((x - mean) ** 2 for x in values) / n if n > 1 else 0
                std = math.sqrt(variance)

                metrics[metric_def.name] = {
                    "mean": mean,
                    "std": std,
                    "min": min(values),
                    "max": max(values),
                    "count": n,
                    "p50": values[n // 2] if n > 0 else 0,
                    "p95": values[int(n * 0.95)] if n >= 20 else (values[-1] if values else 0),
                }

        # Count total samples (use first metric or impressions)
        sample_row = conn.execute(
            """SELECT COUNT(DISTINCT id) as cnt FROM metric_records
               WHERE experiment_id = ? AND variant_id = ?""",
            (experiment_id, variant.id)
        ).fetchone()
        samples = sample_row["cnt"] if sample_row else 0

        return VariantStats(
            variant_id=variant.id,
            variant_name=variant.name,
            is_control=variant.is_control,
            impressions=variant.impressions,
            samples=samples,
            metrics=metrics,
        )

    def _calculate_p_value(
        self,
        conn: sqlite3.Connection,
        experiment_id: str,
        control_id: str,
        variant_id: str,
        metric_name: str,
    ) -> Optional[float]:
        """Calculate p-value using Welch's t-test approximation."""
        control_rows = conn.execute(
            """SELECT value FROM metric_records
               WHERE experiment_id = ? AND variant_id = ? AND metric_name = ?""",
            (experiment_id, control_id, metric_name)
        ).fetchall()

        variant_rows = conn.execute(
            """SELECT value FROM metric_records
               WHERE experiment_id = ? AND variant_id = ? AND metric_name = ?""",
            (experiment_id, variant_id, metric_name)
        ).fetchall()

        if len(control_rows) < 2 or len(variant_rows) < 2:
            return None

        control_values = [r["value"] for r in control_rows]
        variant_values = [r["value"] for r in variant_rows]

        n1, n2 = len(control_values), len(variant_values)
        mean1 = sum(control_values) / n1
        mean2 = sum(variant_values) / n2

        var1 = sum((x - mean1) ** 2 for x in control_values) / (n1 - 1)
        var2 = sum((x - mean2) ** 2 for x in variant_values) / (n2 - 1)

        # Welch's t-test
        se = math.sqrt(var1 / n1 + var2 / n2)
        if se == 0:
            return None

        t_stat = abs(mean2 - mean1) / se

        # Approximate p-value using normal distribution (for large samples)
        # For more accurate results, use scipy.stats.t
        if t_stat > 4:
            return 0.0001  # Very significant
        elif t_stat > 3:
            return 0.003
        elif t_stat > 2.5:
            return 0.01
        elif t_stat > 2:
            return 0.05
        elif t_stat > 1.5:
            return 0.15
        else:
            return 0.5

    # Statistics

    def get_stats(self, org_id: str) -> Dict[str, Any]:
        """Get experiment statistics for an organization."""
        conn = self._get_conn()
        try:
            stats_row = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN winner_variant_id IS NOT NULL THEN 1 ELSE 0 END) as with_winners
                FROM experiments
                WHERE org_id = ?
            """, (org_id,)).fetchone()

            # Total impressions
            impressions_row = conn.execute("""
                SELECT SUM(json_extract(value, '$.impressions')) as total
                FROM experiments, json_each(variants)
                WHERE org_id = ?
            """, (org_id,)).fetchone()

            return {
                "total_experiments": stats_row["total"] or 0,
                "running_experiments": stats_row["running"] or 0,
                "completed_experiments": stats_row["completed"] or 0,
                "experiments_with_winners": stats_row["with_winners"] or 0,
                "total_impressions": impressions_row["total"] or 0,
            }
        finally:
            conn.close()


# Global instance
_experiment_storage: Optional[ExperimentStorage] = None


def get_experiment_storage() -> ExperimentStorage:
    """Get the global experiment storage instance."""
    global _experiment_storage
    if _experiment_storage is None:
        _experiment_storage = ExperimentStorage()
    return _experiment_storage


def reset_experiment_storage() -> None:
    """Reset the global experiment storage instance."""
    global _experiment_storage
    _experiment_storage = None
