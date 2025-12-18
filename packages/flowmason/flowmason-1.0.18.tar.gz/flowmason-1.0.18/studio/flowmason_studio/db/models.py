"""
SQLAlchemy Database Models for FlowMason Studio.

Defines the database schema for pipelines, runs, folders, and settings.
Compatible with both SQLite (development) and PostgreSQL/Supabase (production).
"""

import json
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# =============================================================================
# JSON Serialization Helpers
# =============================================================================

def json_serialize(obj: Any) -> str:
    """Serialize Python object to JSON string."""
    return json.dumps(obj, default=str)


def json_deserialize(s: Any) -> Any:
    """Deserialize JSON string to Python object.

    Accepts Any to handle SQLAlchemy Column types at type-check time.
    At runtime, s is always str or None.
    """
    if s is None:
        return None
    return json.loads(s)


# =============================================================================
# Folder Model
# =============================================================================

class Folder(Base):
    """Folder for organizing pipelines."""

    __tablename__ = "folders"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(
        String(64),
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True
    )
    color = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    children = relationship(
        "Folder",
        backref="parent",
        remote_side=[id],
        cascade="all, delete-orphan",
        single_parent=True
    )
    pipelines = relationship("Pipeline", back_populates="folder")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# =============================================================================
# Pipeline Model
# =============================================================================

class Pipeline(Base):
    """Pipeline configuration storage."""

    __tablename__ = "pipelines"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(32), default="1.0.0")
    folder_id = Column(
        String(64),
        ForeignKey("folders.id", ondelete="SET NULL"),
        nullable=True
    )

    # Configuration stored as JSON
    config = Column(Text, nullable=False)  # JSON: stages, input_schema, output_schema
    input_schema = Column(Text, nullable=True)  # JSON Schema
    output_schema = Column(Text, nullable=True)  # JSON Schema
    output_stage_id = Column(String(64), nullable=True)

    # Metadata
    category = Column(String(64), nullable=True)
    tags = Column(Text, nullable=True)  # JSON array
    is_template = Column(Boolean, default=False)
    is_protected = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    folder = relationship("Folder", back_populates="pipelines")
    runs = relationship("Run", back_populates="pipeline", cascade="all, delete-orphan")
    versions = relationship(
        "PipelineVersion",
        back_populates="pipeline",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "folder_id": self.folder_id,
            "config": json_deserialize(self.config) if self.config else None,
            "input_schema": json_deserialize(self.input_schema) if self.input_schema else None,
            "output_schema": json_deserialize(self.output_schema) if self.output_schema else None,
            "output_stage_id": self.output_stage_id,
            "category": self.category,
            "tags": json_deserialize(self.tags) if self.tags else [],
            "is_template": self.is_template,
            "is_protected": self.is_protected,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pipeline":
        """Create Pipeline from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            version=data.get("version", "1.0.0"),
            folder_id=data.get("folder_id"),
            config=json_serialize(data.get("config", {})),
            input_schema=json_serialize(data.get("input_schema")) if data.get("input_schema") else None,
            output_schema=json_serialize(data.get("output_schema")) if data.get("output_schema") else None,
            output_stage_id=data.get("output_stage_id"),
            category=data.get("category"),
            tags=json_serialize(data.get("tags", [])),
            is_template=data.get("is_template", False),
            is_protected=data.get("is_protected", False),
        )


# =============================================================================
# Pipeline Version Model
# =============================================================================

class PipelineVersion(Base):
    """Pipeline version history for undo/restore functionality."""

    __tablename__ = "pipeline_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(
        String(64),
        ForeignKey("pipelines.id", ondelete="CASCADE"),
        nullable=False
    )
    version = Column(String(32), nullable=False)
    config = Column(Text, nullable=False)  # JSON: full pipeline config
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pipeline = relationship("Pipeline", back_populates="versions")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "version": self.version,
            "config": json_deserialize(self.config) if self.config else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# =============================================================================
# Run Model
# =============================================================================

class Run(Base):
    """Pipeline execution history."""

    __tablename__ = "runs"

    id = Column(String(64), primary_key=True)
    pipeline_id = Column(
        String(64),
        ForeignKey("pipelines.id", ondelete="CASCADE"),
        nullable=False
    )
    trace_id = Column(String(64), nullable=True)

    # Status: pending, running, completed, failed, cancelled
    status = Column(String(32), nullable=False, default="pending")

    # Input/Output
    inputs = Column(Text, nullable=True)  # JSON
    output = Column(Text, nullable=True)  # JSON
    error = Column(Text, nullable=True)

    # Stage results for detailed tracing
    stage_results = Column(Text, nullable=True)  # JSON: {stage_id: StageResult}

    # Usage metrics
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    usage_details = Column(Text, nullable=True)  # JSON: detailed usage breakdown

    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    # Relationships
    pipeline = relationship("Pipeline", back_populates="runs")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "pipeline_id": self.pipeline_id,
            "trace_id": self.trace_id,
            "status": self.status,
            "inputs": json_deserialize(self.inputs) if self.inputs else None,
            "output": json_deserialize(self.output) if self.output else None,
            "error": self.error,
            "stage_results": json_deserialize(self.stage_results) if self.stage_results else None,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "usage_details": json_deserialize(self.usage_details) if self.usage_details else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
        }


# =============================================================================
# Settings Model
# =============================================================================

class Setting(Base):
    """Application settings storage (key-value)."""

    __tablename__ = "settings"

    key = Column(String(255), primary_key=True)
    value = Column(Text, nullable=False)  # JSON

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "value": json_deserialize(self.value) if self.value else None,
        }


# =============================================================================
# Component Package Model
# =============================================================================

class ComponentPackage(Base):
    """Deployed component package metadata."""

    __tablename__ = "component_packages"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(128), nullable=True)
    tags = Column(Text, nullable=True)  # JSON array

    # Component types provided by this package
    component_types = Column(Text, nullable=False)  # JSON array of component type names

    # Package metadata
    author = Column(String(255), nullable=True)
    license = Column(String(64), nullable=True)
    manifest = Column(Text, nullable=True)  # JSON: raw manifest

    # Status
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "tags": json_deserialize(self.tags) if self.tags else [],
            "component_types": json_deserialize(self.component_types) if self.component_types else [],
            "author": self.author,
            "license": self.license,
            "manifest": json_deserialize(self.manifest) if self.manifest else None,
            "is_enabled": self.is_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
