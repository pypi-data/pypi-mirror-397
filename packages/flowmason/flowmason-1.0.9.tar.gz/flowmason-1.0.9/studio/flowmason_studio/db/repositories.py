"""
Repository Classes for FlowMason Studio Database Operations.

Provides clean CRUD interfaces for database operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from flowmason_studio.db.models import (
    ComponentPackage,
    Folder,
    Pipeline,
    PipelineVersion,
    Run,
    Setting,
    json_deserialize,
    json_serialize,
)

# =============================================================================
# Pipeline Repository
# =============================================================================

class PipelineRepository:
    """Repository for pipeline CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: Dict[str, Any]) -> Pipeline:
        """Create a new pipeline."""
        pipeline = Pipeline.from_dict(data)
        self.session.add(pipeline)
        self.session.commit()
        self.session.refresh(pipeline)

        # Create initial version
        version = PipelineVersion(
            pipeline_id=pipeline.id,
            version=pipeline.version,
            config=pipeline.config,
        )
        self.session.add(version)
        self.session.commit()

        return pipeline

    def get(self, pipeline_id: str) -> Optional[Pipeline]:
        """Get pipeline by ID."""
        return self.session.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    def get_all(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        include_templates: bool = True,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[Pipeline]:
        """Get all pipelines with optional filtering."""
        query = self.session.query(Pipeline)

        if not include_templates:
            query = query.filter(Pipeline.is_template.is_(False))

        if category:
            query = query.filter(Pipeline.category == category)

        query = query.order_by(Pipeline.updated_at.desc())

        if offset > 0:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        pipelines = query.all()

        # Filter by tags if provided (in-memory for now, could optimize with JSON queries)
        if tags:
            filtered = []
            for p in pipelines:
                pipeline_tags = json_deserialize(p.tags) if p.tags else []
                if any(t in pipeline_tags for t in tags):
                    filtered.append(p)
            return filtered

        return pipelines

    def count(
        self,
        category: Optional[str] = None,
        include_templates: bool = True,
    ) -> int:
        """Count total pipelines."""
        query = self.session.query(Pipeline)

        if not include_templates:
            query = query.filter(Pipeline.is_template.is_(False))

        if category:
            query = query.filter(Pipeline.category == category)

        return query.count()

    def update(
        self,
        pipeline_id: str,
        data: Dict[str, Any],
        create_version: bool = True,
    ) -> Optional[Pipeline]:
        """Update a pipeline."""
        pipeline = self.get(pipeline_id)
        if not pipeline:
            return None

        # Update allowed fields
        if "name" in data:
            pipeline.name = data["name"]
        if "description" in data:
            pipeline.description = data["description"]
        if "folder_id" in data:
            pipeline.folder_id = data["folder_id"]
        if "config" in data:
            pipeline.config = json_serialize(data["config"])  # type: ignore[assignment]
        if "input_schema" in data:
            pipeline.input_schema = json_serialize(data["input_schema"]) if data["input_schema"] else None  # type: ignore[assignment]
        if "output_schema" in data:
            pipeline.output_schema = json_serialize(data["output_schema"]) if data["output_schema"] else None  # type: ignore[assignment]
        if "output_stage_id" in data:
            pipeline.output_stage_id = data["output_stage_id"]
        if "category" in data:
            pipeline.category = data["category"]
        if "tags" in data:
            pipeline.tags = json_serialize(data["tags"])  # type: ignore[assignment]
        if "is_template" in data:
            pipeline.is_template = data["is_template"]
        if "stages" in data:
            # Update stages in config
            current_config = json_deserialize(pipeline.config) if pipeline.config else {}
            current_config["stages"] = data["stages"]
            pipeline.config = json_serialize(current_config)  # type: ignore[assignment]

        # Increment version
        if create_version:
            # Parse current version and increment patch
            version_parts = pipeline.version.split(".")
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            pipeline.version = ".".join(version_parts)  # type: ignore[assignment]

            # Create version record
            version = PipelineVersion(
                pipeline_id=pipeline.id,
                version=pipeline.version,
                config=pipeline.config,
            )
            self.session.add(version)

        pipeline.updated_at = datetime.utcnow()  # type: ignore[assignment]
        self.session.commit()
        self.session.refresh(pipeline)

        return pipeline

    def delete(self, pipeline_id: str) -> bool:
        """Delete a pipeline."""
        pipeline = self.get(pipeline_id)
        if not pipeline:
            return False
        self.session.delete(pipeline)
        self.session.commit()
        return True

    def duplicate(
        self,
        pipeline_id: str,
        new_id: str,
        new_name: str,
    ) -> Optional[Pipeline]:
        """Duplicate a pipeline."""
        original = self.get(pipeline_id)
        if not original:
            return None

        data = original.to_dict()
        data["id"] = new_id
        data["name"] = new_name
        data["is_template"] = False
        data["version"] = "1.0.0"

        return self.create(data)

    def get_versions(self, pipeline_id: str) -> List[PipelineVersion]:
        """Get version history for a pipeline."""
        return (
            self.session.query(PipelineVersion)
            .filter(PipelineVersion.pipeline_id == pipeline_id)
            .order_by(PipelineVersion.version.desc())
            .all()
        )

    def restore_version(
        self,
        pipeline_id: str,
        version: str,
    ) -> Optional[Pipeline]:
        """Restore a pipeline to a specific version."""
        version_record = (
            self.session.query(PipelineVersion)
            .filter(
                PipelineVersion.pipeline_id == pipeline_id,
                PipelineVersion.version == version,
            )
            .first()
        )
        if not version_record:
            return None

        pipeline = self.get(pipeline_id)
        if not pipeline:
            return None

        # Restore config from version
        pipeline.config = version_record.config

        # Increment version
        version_parts = pipeline.version.split(".")
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        pipeline.version = ".".join(version_parts)  # type: ignore[assignment]

        # Create new version record
        new_version = PipelineVersion(
            pipeline_id=pipeline.id,
            version=pipeline.version,
            config=pipeline.config,
        )
        self.session.add(new_version)

        pipeline.updated_at = datetime.utcnow()  # type: ignore[assignment]
        self.session.commit()
        self.session.refresh(pipeline)

        return pipeline


# =============================================================================
# Run Repository
# =============================================================================

class RunRepository:
    """Repository for run CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: Dict[str, Any]) -> Run:
        """Create a new run."""
        run = Run(
            id=data["id"],
            pipeline_id=data["pipeline_id"],
            trace_id=data.get("trace_id"),
            status=data.get("status", "pending"),
            inputs=json_serialize(data.get("inputs")) if data.get("inputs") else None,
            started_at=data.get("started_at", datetime.utcnow()),
        )
        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run

    def get(self, run_id: str) -> Optional[Run]:
        """Get run by ID."""
        return self.session.query(Run).filter(Run.id == run_id).first()

    def get_all(
        self,
        pipeline_id: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Run]:
        """Get all runs with optional filtering."""
        query = self.session.query(Run)

        if pipeline_id:
            query = query.filter(Run.pipeline_id == pipeline_id)

        if status:
            query = query.filter(Run.status == status)

        query = query.order_by(Run.started_at.desc())

        if offset > 0:
            query = query.offset(offset)

        return query.limit(limit).all()

    def count(
        self,
        pipeline_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count total runs."""
        query = self.session.query(Run)

        if pipeline_id:
            query = query.filter(Run.pipeline_id == pipeline_id)

        if status:
            query = query.filter(Run.status == status)

        return query.count()

    def update(self, run_id: str, data: Dict[str, Any]) -> Optional[Run]:
        """Update a run."""
        run = self.get(run_id)
        if not run:
            return None

        if "status" in data:
            run.status = data["status"]  # type: ignore[assignment]
        if "output" in data:
            run.output = json_serialize(data["output"])  # type: ignore[assignment]
        if "error" in data:
            run.error = data["error"]
        if "stage_results" in data:
            run.stage_results = json_serialize(data["stage_results"])  # type: ignore[assignment]
        if "total_tokens" in data:
            run.total_tokens = data["total_tokens"]
        if "total_cost" in data:
            run.total_cost = data["total_cost"]
        if "usage_details" in data:
            run.usage_details = json_serialize(data["usage_details"])  # type: ignore[assignment]
        if "completed_at" in data:
            run.completed_at = data["completed_at"]
        if "duration_ms" in data:
            run.duration_ms = data["duration_ms"]

        self.session.commit()
        self.session.refresh(run)
        return run

    def complete(
        self,
        run_id: str,
        status: str,
        output: Optional[Any] = None,
        error: Optional[str] = None,
        stage_results: Optional[Dict[str, Any]] = None,
        usage_details: Optional[Dict[str, Any]] = None,
    ) -> Optional[Run]:
        """Complete a run with results."""
        run = self.get(run_id)
        if not run:
            return None

        completed_at = datetime.utcnow()
        duration_ms = None
        if run.started_at:
            duration_ms = int((completed_at - run.started_at).total_seconds() * 1000)

        run.status = status  # type: ignore[assignment]
        run.completed_at = completed_at  # type: ignore[assignment]
        run.duration_ms = duration_ms  # type: ignore[assignment]

        if output is not None:
            run.output = json_serialize(output)  # type: ignore[assignment]
        if error is not None:
            run.error = error  # type: ignore[assignment]
        if stage_results is not None:
            run.stage_results = json_serialize(stage_results)  # type: ignore[assignment]
        if usage_details is not None:
            run.usage_details = json_serialize(usage_details)  # type: ignore[assignment]
            # Extract totals from usage details
            run.total_tokens = usage_details.get("total_tokens", 0)
            run.total_cost = usage_details.get("total_cost", 0.0)

        self.session.commit()
        self.session.refresh(run)
        return run

    def delete(self, run_id: str) -> bool:
        """Delete a run."""
        run = self.get(run_id)
        if not run:
            return False
        self.session.delete(run)
        self.session.commit()
        return True


# =============================================================================
# Folder Repository
# =============================================================================

class FolderRepository:
    """Repository for folder CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: Dict[str, Any]) -> Folder:
        """Create a new folder."""
        folder = Folder(
            id=data["id"],
            name=data["name"],
            parent_id=data.get("parent_id"),
            color=data.get("color"),
        )
        self.session.add(folder)
        self.session.commit()
        self.session.refresh(folder)
        return folder

    def get(self, folder_id: str) -> Optional[Folder]:
        """Get folder by ID."""
        return self.session.query(Folder).filter(Folder.id == folder_id).first()

    def get_all(
        self,
        parent_id: Optional[str] = None,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[Folder]:
        """Get all folders with optional filtering."""
        query = self.session.query(Folder)

        if parent_id is not None:
            query = query.filter(Folder.parent_id == parent_id)

        query = query.order_by(Folder.name)

        if offset > 0:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def get_root_folders(self) -> List[Folder]:
        """Get all root folders (no parent)."""
        return (
            self.session.query(Folder)
            .filter(Folder.parent_id.is_(None))
            .order_by(Folder.name)
            .all()
        )

    def update(self, folder_id: str, data: Dict[str, Any]) -> Optional[Folder]:
        """Update a folder."""
        folder = self.get(folder_id)
        if not folder:
            return None

        if "name" in data:
            folder.name = data["name"]
        if "parent_id" in data:
            folder.parent_id = data["parent_id"]
        if "color" in data:
            folder.color = data["color"]

        folder.updated_at = datetime.utcnow()  # type: ignore[assignment]
        self.session.commit()
        self.session.refresh(folder)
        return folder

    def delete(self, folder_id: str) -> bool:
        """Delete a folder. Pipelines in folder will have folder_id set to NULL."""
        folder = self.get(folder_id)
        if not folder:
            return False
        self.session.delete(folder)
        self.session.commit()
        return True

    def count(self, parent_id: Optional[str] = None) -> int:
        """Count total folders."""
        query = self.session.query(Folder)
        if parent_id is not None:
            query = query.filter(Folder.parent_id == parent_id)
        return query.count()


# =============================================================================
# Setting Repository
# =============================================================================

class SettingRepository:
    """Repository for settings operations."""

    def __init__(self, session: Session):
        self.session = session

    def get(self, key: str) -> Optional[Any]:
        """Get a setting value."""
        setting = self.session.query(Setting).filter(Setting.key == key).first()
        if not setting:
            return None
        return json_deserialize(setting.value)

    def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        settings = self.session.query(Setting).all()
        return {str(s.key): json_deserialize(s.value) for s in settings}

    def set(self, key: str, value: Any) -> Setting:
        """Set a setting value."""
        setting = self.session.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = json_serialize(value)  # type: ignore[assignment]
        else:
            setting = Setting(key=key, value=json_serialize(value))
            self.session.add(setting)
        self.session.commit()
        return setting

    def delete(self, key: str) -> bool:
        """Delete a setting."""
        setting = self.session.query(Setting).filter(Setting.key == key).first()
        if not setting:
            return False
        self.session.delete(setting)
        self.session.commit()
        return True


# =============================================================================
# Component Package Repository
# =============================================================================

class ComponentPackageRepository:
    """Repository for component package CRUD operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: Dict[str, Any]) -> ComponentPackage:
        """Create a new component package record."""
        package = ComponentPackage(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            description=data.get("description"),
            category=data.get("category"),
            tags=json_serialize(data.get("tags", [])),
            component_types=json_serialize(data.get("component_types", [])),
            author=data.get("author"),
            license=data.get("license"),
            manifest=json_serialize(data.get("manifest")) if data.get("manifest") else None,
            is_enabled=data.get("is_enabled", True),
        )
        self.session.add(package)
        self.session.commit()
        self.session.refresh(package)
        return package

    def get(self, package_id: str) -> Optional[ComponentPackage]:
        """Get package by ID."""
        return self.session.query(ComponentPackage).filter(ComponentPackage.id == package_id).first()

    def get_by_name_version(self, name: str, version: str) -> Optional[ComponentPackage]:
        """Get package by name and version."""
        return (
            self.session.query(ComponentPackage)
            .filter(ComponentPackage.name == name, ComponentPackage.version == version)
            .first()
        )

    def get_all(
        self,
        category: Optional[str] = None,
        enabled_only: bool = True,
        offset: int = 0,
        limit: Optional[int] = None,
    ) -> List[ComponentPackage]:
        """Get all packages with optional filtering."""
        query = self.session.query(ComponentPackage)

        if enabled_only:
            query = query.filter(ComponentPackage.is_enabled.is_(True))

        if category:
            query = query.filter(ComponentPackage.category == category)

        query = query.order_by(ComponentPackage.name, ComponentPackage.version.desc())

        if offset > 0:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def update(self, package_id: str, data: Dict[str, Any]) -> Optional[ComponentPackage]:
        """Update a package."""
        package = self.get(package_id)
        if not package:
            return None

        if "description" in data:
            package.description = data["description"]
        if "category" in data:
            package.category = data["category"]
        if "tags" in data:
            package.tags = json_serialize(data["tags"])  # type: ignore[assignment]
        if "is_enabled" in data:
            package.is_enabled = data["is_enabled"]

        self.session.commit()
        self.session.refresh(package)
        return package

    def delete(self, package_id: str) -> bool:
        """Delete a package."""
        package = self.get(package_id)
        if not package:
            return False
        self.session.delete(package)
        self.session.commit()
        return True

    def count(
        self,
        category: Optional[str] = None,
        enabled_only: bool = True,
    ) -> int:
        """Count total packages."""
        query = self.session.query(ComponentPackage)

        if enabled_only:
            query = query.filter(ComponentPackage.is_enabled.is_(True))

        if category:
            query = query.filter(ComponentPackage.category == category)

        return query.count()
