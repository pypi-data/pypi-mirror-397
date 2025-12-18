"""
FlowMason Studio Database Layer.

Provides SQLAlchemy models and repositories for persistent storage.
Supports both SQLite (development) and PostgreSQL/Supabase (production).
"""

from flowmason_studio.db.connection import (
    Database,
    get_database,
    get_session,
    init_database,
)
from flowmason_studio.db.models import (
    Base,
    ComponentPackage,
    Folder,
    Pipeline,
    PipelineVersion,
    Run,
    Setting,
)
from flowmason_studio.db.repositories import (
    ComponentPackageRepository,
    FolderRepository,
    PipelineRepository,
    RunRepository,
    SettingRepository,
)

__all__ = [
    # Models
    "Base",
    "Pipeline",
    "PipelineVersion",
    "Run",
    "Folder",
    "Setting",
    "ComponentPackage",
    # Connection
    "Database",
    "get_database",
    "get_session",
    "init_database",
    # Repositories
    "PipelineRepository",
    "RunRepository",
    "FolderRepository",
    "SettingRepository",
    "ComponentPackageRepository",
]
