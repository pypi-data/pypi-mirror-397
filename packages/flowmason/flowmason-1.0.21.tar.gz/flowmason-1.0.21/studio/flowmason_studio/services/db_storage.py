"""
Database-backed Storage Service for FlowMason Studio.

Provides the same interface as the in-memory storage but persists to database.
Uses SQLAlchemy repositories for CRUD operations.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from flowmason_studio.db.connection import get_session
from flowmason_studio.db.models import json_deserialize
from flowmason_studio.db.repositories import PipelineRepository, RunRepository
from flowmason_studio.models.api import (
    PipelineCreate,
    PipelineDetail,
    PipelineStage,
    PipelineSummary,
    PipelineUpdate,
    RunDetail,
    RunSummary,
    StageResult,
)

# =============================================================================
# Database-backed Pipeline Storage
# =============================================================================

class DatabasePipelineStorage:
    """
    Database-backed storage for pipelines.

    Provides the same interface as PipelineStorage but uses database.
    """

    def create(self, pipeline: PipelineCreate) -> PipelineDetail:
        """Create a new pipeline."""
        session = get_session()
        try:
            repo = PipelineRepository(session)

            pipeline_id = f"pipe_{uuid.uuid4().hex[:12]}"

            # Convert stages to dict format
            stages_data = [s.model_dump() for s in pipeline.stages]

            data = {
                "id": pipeline_id,
                "name": pipeline.name,
                "description": pipeline.description,
                "version": "1.0.0",
                "config": {"stages": stages_data},
                "input_schema": pipeline.input_schema.model_dump() if pipeline.input_schema else None,
                "output_schema": pipeline.output_schema.model_dump() if pipeline.output_schema else None,
                "output_stage_id": pipeline.output_stage_id,
                "category": pipeline.category,
                "tags": pipeline.tags or [],
            }

            db_pipeline = repo.create(data)
            return self._to_detail(db_pipeline)
        finally:
            session.close()

    def get(self, pipeline_id: str) -> Optional[PipelineDetail]:
        """Get a pipeline by ID."""
        session = get_session()
        try:
            repo = PipelineRepository(session)
            db_pipeline = repo.get(pipeline_id)
            if not db_pipeline:
                return None
            return self._to_detail(db_pipeline)
        finally:
            session.close()

    def update(self, pipeline_id: str, update: PipelineUpdate) -> Optional[PipelineDetail]:
        """Update an existing pipeline."""
        session = get_session()
        try:
            repo = PipelineRepository(session)

            update_data = update.model_dump(exclude_unset=True)

            # Convert stages if provided
            if "stages" in update_data and update_data["stages"]:
                update_data["stages"] = [
                    s.model_dump() if hasattr(s, 'model_dump') else s
                    for s in update_data["stages"]
                ]

            db_pipeline = repo.update(pipeline_id, update_data)
            if not db_pipeline:
                return None
            return self._to_detail(db_pipeline)
        finally:
            session.close()

    def delete(self, pipeline_id: str) -> bool:
        """Delete a pipeline."""
        session = get_session()
        try:
            repo = PipelineRepository(session)
            return repo.delete(pipeline_id)
        finally:
            session.close()

    def list(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[PipelineSummary], int]:
        """List pipelines with optional filtering."""
        session = get_session()
        try:
            repo = PipelineRepository(session)

            pipelines = repo.get_all(
                category=category,
                tags=tags,
                offset=offset,
                limit=limit,
            )

            total = repo.count(category=category)

            summaries = []
            for p in pipelines:
                config = json_deserialize(p.config) if p.config else {}
                stages = config.get("stages", [])

                summaries.append(PipelineSummary(
                    id=str(p.id),  # type: ignore[arg-type]
                    name=str(p.name),  # type: ignore[arg-type]
                    description=str(p.description) if p.description else "",  # type: ignore[arg-type]
                    version=str(p.version),  # type: ignore[arg-type]
                    stage_count=len(stages),
                    category=str(p.category) if p.category else None,  # type: ignore[arg-type]
                    tags=json_deserialize(p.tags) if p.tags else [],
                    created_at=p.created_at,  # type: ignore[arg-type]
                    updated_at=p.updated_at,  # type: ignore[arg-type]
                ))

            return summaries, total
        finally:
            session.close()

    def _to_detail(self, db_pipeline) -> PipelineDetail:
        """Convert database model to API model."""
        config = json_deserialize(db_pipeline.config) if db_pipeline.config else {}
        stages_data = config.get("stages", [])

        stages = [PipelineStage(**s) for s in stages_data]

        return PipelineDetail(
            id=db_pipeline.id,
            name=db_pipeline.name,
            description=db_pipeline.description,
            version=db_pipeline.version,
            input_schema=json_deserialize(db_pipeline.input_schema) if db_pipeline.input_schema else None,
            output_schema=json_deserialize(db_pipeline.output_schema) if db_pipeline.output_schema else None,
            stages=stages,
            output_stage_id=db_pipeline.output_stage_id,
            category=db_pipeline.category,
            tags=json_deserialize(db_pipeline.tags) if db_pipeline.tags else [],
            created_at=db_pipeline.created_at,
            updated_at=db_pipeline.updated_at,
        )


# =============================================================================
# Database-backed Run Storage
# =============================================================================

class DatabaseRunStorage:
    """
    Database-backed storage for pipeline runs.

    Provides the same interface as RunStorage but uses database.
    """

    def create(
        self,
        pipeline_id: str,
        inputs: Dict[str, Any]
    ) -> RunDetail:
        """Create a new run record."""
        session = get_session()
        try:
            repo = RunRepository(session)

            run_id = f"run_{uuid.uuid4().hex[:12]}"
            trace_id = f"trace_{uuid.uuid4().hex[:8]}"
            now = datetime.utcnow()

            data = {
                "id": run_id,
                "pipeline_id": pipeline_id,
                "trace_id": trace_id,
                "status": "pending",
                "inputs": inputs,
                "started_at": now,
            }

            db_run = repo.create(data)
            return self._to_detail(db_run)
        finally:
            session.close()

    def get(self, run_id: str) -> Optional[RunDetail]:
        """Get a run by ID."""
        session = get_session()
        try:
            repo = RunRepository(session)
            db_run = repo.get(run_id)
            if not db_run:
                return None
            return self._to_detail(db_run)
        finally:
            session.close()

    def update_status(
        self,
        run_id: str,
        status: str,
    ) -> Optional[RunDetail]:
        """Update run status."""
        session = get_session()
        try:
            repo = RunRepository(session)

            update_data: Dict[str, Any] = {"status": status}

            if status in ("completed", "failed", "cancelled"):
                update_data["completed_at"] = datetime.utcnow()

            db_run = repo.update(run_id, update_data)
            if not db_run:
                return None

            # Recalculate duration
            if db_run.started_at and db_run.completed_at:
                duration_ms = int(
                    (db_run.completed_at - db_run.started_at).total_seconds() * 1000
                )
                db_run = repo.update(run_id, {"duration_ms": duration_ms})

            return self._to_detail(db_run)
        finally:
            session.close()

    def complete_run(
        self,
        run_id: str,
        status: str,
        output: Optional[Any] = None,
        error: Optional[str] = None,
        stage_results: Optional[Dict[str, StageResult]] = None,
    ) -> Optional[RunDetail]:
        """Complete a run with results."""
        session = get_session()
        try:
            repo = RunRepository(session)

            # Convert StageResult models to dicts
            stage_results_data = None
            if stage_results:
                stage_results_data = {
                    k: v.model_dump() if hasattr(v, 'model_dump') else v
                    for k, v in stage_results.items()
                }

            db_run = repo.complete(
                run_id=run_id,
                status=status,
                output=output,
                error=error,
                stage_results=stage_results_data,
            )
            if not db_run:
                return None
            return self._to_detail(db_run)
        finally:
            session.close()

    def delete(self, run_id: str) -> bool:
        """Delete a run."""
        session = get_session()
        try:
            repo = RunRepository(session)
            return repo.delete(run_id)
        finally:
            session.close()

    def list(
        self,
        pipeline_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[RunSummary], int]:
        """List runs with optional filtering."""
        session = get_session()
        try:
            repo = RunRepository(session)

            runs = repo.get_all(
                pipeline_id=pipeline_id,
                status=status,
                offset=offset,
                limit=limit,
            )

            total = repo.count(pipeline_id=pipeline_id, status=status)

            summaries = [
                RunSummary(
                    id=str(r.id),  # type: ignore[arg-type]
                    pipeline_id=str(r.pipeline_id),  # type: ignore[arg-type]
                    status=r.status,  # type: ignore[arg-type]
                    started_at=r.started_at,  # type: ignore[arg-type]
                    completed_at=r.completed_at,  # type: ignore[arg-type]
                    duration_ms=r.duration_ms,  # type: ignore[arg-type]
                )
                for r in runs
            ]

            return summaries, total
        finally:
            session.close()

    def _to_detail(self, db_run) -> RunDetail:
        """Convert database model to API model."""
        # Parse stage results
        stage_results = None
        if db_run.stage_results:
            stage_results_data = json_deserialize(db_run.stage_results)
            if stage_results_data:
                stage_results = {
                    k: StageResult(**v) if isinstance(v, dict) else v
                    for k, v in stage_results_data.items()
                }

        return RunDetail(
            id=db_run.id,
            pipeline_id=db_run.pipeline_id,
            status=db_run.status,
            inputs=json_deserialize(db_run.inputs) if db_run.inputs else None,
            output=json_deserialize(db_run.output) if db_run.output else None,
            error=db_run.error,
            stage_results=stage_results,
            started_at=db_run.started_at,
            completed_at=db_run.completed_at,
            duration_ms=db_run.duration_ms,
            trace_id=db_run.trace_id,
        )


# =============================================================================
# Storage Factory
# =============================================================================

def get_storage_backend() -> str:
    """
    Determine which storage backend to use.

    Returns:
        "database" if DATABASE_URL is set, "memory" otherwise
    """
    import os
    return "database" if os.getenv("DATABASE_URL") else "memory"


def create_pipeline_storage():
    """
    Create appropriate pipeline storage based on configuration.

    Returns:
        DatabasePipelineStorage if DATABASE_URL is set,
        PipelineStorage (in-memory) otherwise
    """
    if get_storage_backend() == "database":
        return DatabasePipelineStorage()
    else:
        from flowmason_studio.services.storage import PipelineStorage
        return PipelineStorage()


def create_run_storage():
    """
    Create appropriate run storage based on configuration.

    Returns:
        DatabaseRunStorage if DATABASE_URL is set,
        RunStorage (in-memory) otherwise
    """
    if get_storage_backend() == "database":
        return DatabaseRunStorage()
    else:
        from flowmason_studio.services.storage import RunStorage
        return RunStorage()
