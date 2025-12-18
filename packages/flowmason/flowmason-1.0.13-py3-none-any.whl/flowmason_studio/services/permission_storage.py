"""
Pipeline Permission Storage Service.

Handles storage and retrieval of pipeline permissions using SQLite.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from flowmason_studio.models.permissions import (
    EffectivePermissions,
    FolderPermissions,
    PermissionGrant,
    PermissionLevel,
    PipelinePermissions,
    PipelineVisibility,
    PrincipalType,
    get_max_level,
    level_includes,
)


class PermissionStorage:
    """SQLite-based storage for pipeline permissions."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the permission storage."""
        if db_path is None:
            db_path = Path.home() / ".flowmason" / "permissions.db"
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
                CREATE TABLE IF NOT EXISTS pipeline_permissions (
                    pipeline_id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    visibility TEXT NOT NULL DEFAULT 'private',
                    inherit_from_folder INTEGER DEFAULT 1,
                    folder_id TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );

                CREATE TABLE IF NOT EXISTS permission_grants (
                    id TEXT PRIMARY KEY,
                    pipeline_id TEXT,
                    folder_id TEXT,
                    principal_type TEXT NOT NULL,
                    principal_id TEXT NOT NULL,
                    level TEXT NOT NULL,
                    granted_by TEXT,
                    granted_at TEXT,
                    expires_at TEXT,
                    UNIQUE(pipeline_id, principal_type, principal_id),
                    UNIQUE(folder_id, principal_type, principal_id)
                );

                CREATE TABLE IF NOT EXISTS folder_permissions (
                    folder_id TEXT PRIMARY KEY,
                    owner_id TEXT NOT NULL,
                    visibility TEXT NOT NULL DEFAULT 'private',
                    parent_folder_id TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_grants_pipeline
                    ON permission_grants(pipeline_id);
                CREATE INDEX IF NOT EXISTS idx_grants_folder
                    ON permission_grants(folder_id);
                CREATE INDEX IF NOT EXISTS idx_grants_principal
                    ON permission_grants(principal_type, principal_id);
            """)
            conn.commit()
        finally:
            conn.close()

    # Pipeline Permission CRUD

    def get_pipeline_permissions(
        self, pipeline_id: str
    ) -> Optional[PipelinePermissions]:
        """Get permissions for a pipeline."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM pipeline_permissions WHERE pipeline_id = ?",
                (pipeline_id,)
            ).fetchone()

            if not row:
                return None

            # Get grants
            grants = self._get_pipeline_grants(conn, pipeline_id)

            return PipelinePermissions(
                pipeline_id=row["pipeline_id"],
                owner_id=row["owner_id"],
                visibility=PipelineVisibility(row["visibility"]),
                inherit_from_folder=bool(row["inherit_from_folder"]),
                folder_id=row["folder_id"],
                grants=grants,
                created_at=datetime.fromisoformat(row["created_at"])
                    if row["created_at"] else None,
                updated_at=datetime.fromisoformat(row["updated_at"])
                    if row["updated_at"] else None,
            )
        finally:
            conn.close()

    def _get_pipeline_grants(
        self, conn: sqlite3.Connection, pipeline_id: str
    ) -> List[PermissionGrant]:
        """Get all grants for a pipeline."""
        rows = conn.execute(
            """SELECT * FROM permission_grants
               WHERE pipeline_id = ?
               AND (expires_at IS NULL OR expires_at > datetime('now'))""",
            (pipeline_id,)
        ).fetchall()

        return [self._row_to_grant(row) for row in rows]

    def _row_to_grant(self, row: sqlite3.Row) -> PermissionGrant:
        """Convert a database row to a PermissionGrant."""
        return PermissionGrant(
            id=row["id"],
            principal_type=PrincipalType(row["principal_type"]),
            principal_id=row["principal_id"],
            level=PermissionLevel(row["level"]),
            granted_by=row["granted_by"],
            granted_at=datetime.fromisoformat(row["granted_at"])
                if row["granted_at"] else None,
            expires_at=datetime.fromisoformat(row["expires_at"])
                if row["expires_at"] else None,
        )

    def create_pipeline_permissions(
        self,
        pipeline_id: str,
        owner_id: str,
        visibility: PipelineVisibility = PipelineVisibility.PRIVATE,
        folder_id: Optional[str] = None,
    ) -> PipelinePermissions:
        """Create initial permissions for a pipeline."""
        now = datetime.utcnow().isoformat()
        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO pipeline_permissions
                   (pipeline_id, owner_id, visibility, inherit_from_folder,
                    folder_id, created_at, updated_at)
                   VALUES (?, ?, ?, 1, ?, ?, ?)""",
                (pipeline_id, owner_id, visibility.value, folder_id, now, now)
            )
            conn.commit()

            return PipelinePermissions(
                pipeline_id=pipeline_id,
                owner_id=owner_id,
                visibility=visibility,
                inherit_from_folder=True,
                folder_id=folder_id,
                grants=[],
                created_at=datetime.fromisoformat(now),
                updated_at=datetime.fromisoformat(now),
            )
        finally:
            conn.close()

    def update_visibility(
        self,
        pipeline_id: str,
        visibility: PipelineVisibility,
    ) -> Optional[PipelinePermissions]:
        """Update pipeline visibility."""
        now = datetime.utcnow().isoformat()
        conn = self._get_conn()
        try:
            result = conn.execute(
                """UPDATE pipeline_permissions
                   SET visibility = ?, updated_at = ?
                   WHERE pipeline_id = ?""",
                (visibility.value, now, pipeline_id)
            )
            conn.commit()

            if result.rowcount == 0:
                return None

            return self.get_pipeline_permissions(pipeline_id)
        finally:
            conn.close()

    def set_folder_inheritance(
        self,
        pipeline_id: str,
        inherit: bool,
        folder_id: Optional[str] = None,
    ) -> Optional[PipelinePermissions]:
        """Set folder inheritance for a pipeline."""
        now = datetime.utcnow().isoformat()
        conn = self._get_conn()
        try:
            result = conn.execute(
                """UPDATE pipeline_permissions
                   SET inherit_from_folder = ?, folder_id = ?, updated_at = ?
                   WHERE pipeline_id = ?""",
                (1 if inherit else 0, folder_id, now, pipeline_id)
            )
            conn.commit()

            if result.rowcount == 0:
                return None

            return self.get_pipeline_permissions(pipeline_id)
        finally:
            conn.close()

    # Grant Management

    def add_grant(
        self,
        pipeline_id: str,
        principal_type: PrincipalType,
        principal_id: str,
        level: PermissionLevel,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> PermissionGrant:
        """Add or update a permission grant."""
        grant_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        expires_str = expires_at.isoformat() if expires_at else None

        conn = self._get_conn()
        try:
            # Upsert the grant
            conn.execute(
                """INSERT INTO permission_grants
                   (id, pipeline_id, principal_type, principal_id, level,
                    granted_by, granted_at, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(pipeline_id, principal_type, principal_id)
                   DO UPDATE SET level = ?, granted_by = ?, granted_at = ?,
                                 expires_at = ?""",
                (
                    grant_id, pipeline_id, principal_type.value, principal_id,
                    level.value, granted_by, now, expires_str,
                    level.value, granted_by, now, expires_str
                )
            )
            conn.commit()

            return PermissionGrant(
                id=grant_id,
                principal_type=principal_type,
                principal_id=principal_id,
                level=level,
                granted_by=granted_by,
                granted_at=datetime.fromisoformat(now),
                expires_at=expires_at,
            )
        finally:
            conn.close()

    def remove_grant(
        self,
        pipeline_id: str,
        principal_type: PrincipalType,
        principal_id: str,
    ) -> bool:
        """Remove a permission grant."""
        conn = self._get_conn()
        try:
            result = conn.execute(
                """DELETE FROM permission_grants
                   WHERE pipeline_id = ?
                   AND principal_type = ?
                   AND principal_id = ?""",
                (pipeline_id, principal_type.value, principal_id)
            )
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    def remove_all_grants(self, pipeline_id: str) -> int:
        """Remove all grants for a pipeline."""
        conn = self._get_conn()
        try:
            result = conn.execute(
                "DELETE FROM permission_grants WHERE pipeline_id = ?",
                (pipeline_id,)
            )
            conn.commit()
            return result.rowcount
        finally:
            conn.close()

    # Folder Permissions

    def get_folder_permissions(
        self, folder_id: str
    ) -> Optional[FolderPermissions]:
        """Get permissions for a folder."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM folder_permissions WHERE folder_id = ?",
                (folder_id,)
            ).fetchone()

            if not row:
                return None

            # Get grants
            grants = self._get_folder_grants(conn, folder_id)

            return FolderPermissions(
                folder_id=row["folder_id"],
                owner_id=row["owner_id"],
                visibility=PipelineVisibility(row["visibility"]),
                parent_folder_id=row["parent_folder_id"],
                grants=grants,
                created_at=datetime.fromisoformat(row["created_at"])
                    if row["created_at"] else None,
                updated_at=datetime.fromisoformat(row["updated_at"])
                    if row["updated_at"] else None,
            )
        finally:
            conn.close()

    def _get_folder_grants(
        self, conn: sqlite3.Connection, folder_id: str
    ) -> List[PermissionGrant]:
        """Get all grants for a folder."""
        rows = conn.execute(
            """SELECT * FROM permission_grants
               WHERE folder_id = ?
               AND (expires_at IS NULL OR expires_at > datetime('now'))""",
            (folder_id,)
        ).fetchall()

        return [self._row_to_grant(row) for row in rows]

    def create_folder_permissions(
        self,
        folder_id: str,
        owner_id: str,
        visibility: PipelineVisibility = PipelineVisibility.PRIVATE,
        parent_folder_id: Optional[str] = None,
    ) -> FolderPermissions:
        """Create permissions for a folder."""
        now = datetime.utcnow().isoformat()
        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO folder_permissions
                   (folder_id, owner_id, visibility, parent_folder_id,
                    created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (folder_id, owner_id, visibility.value, parent_folder_id, now, now)
            )
            conn.commit()

            return FolderPermissions(
                folder_id=folder_id,
                owner_id=owner_id,
                visibility=visibility,
                parent_folder_id=parent_folder_id,
                grants=[],
                created_at=datetime.fromisoformat(now),
                updated_at=datetime.fromisoformat(now),
            )
        finally:
            conn.close()

    def add_folder_grant(
        self,
        folder_id: str,
        principal_type: PrincipalType,
        principal_id: str,
        level: PermissionLevel,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> PermissionGrant:
        """Add a permission grant to a folder."""
        grant_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        expires_str = expires_at.isoformat() if expires_at else None

        conn = self._get_conn()
        try:
            conn.execute(
                """INSERT INTO permission_grants
                   (id, folder_id, principal_type, principal_id, level,
                    granted_by, granted_at, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(folder_id, principal_type, principal_id)
                   DO UPDATE SET level = ?, granted_by = ?, granted_at = ?,
                                 expires_at = ?""",
                (
                    grant_id, folder_id, principal_type.value, principal_id,
                    level.value, granted_by, now, expires_str,
                    level.value, granted_by, now, expires_str
                )
            )
            conn.commit()

            return PermissionGrant(
                id=grant_id,
                principal_type=principal_type,
                principal_id=principal_id,
                level=level,
                granted_by=granted_by,
                granted_at=datetime.fromisoformat(now),
                expires_at=expires_at,
            )
        finally:
            conn.close()

    # Permission Resolution

    def check_permission(
        self,
        pipeline_id: str,
        user_id: str,
        required_level: PermissionLevel,
        user_orgs: Optional[List[str]] = None,
        user_teams: Optional[List[str]] = None,
    ) -> bool:
        """Check if a user has the required permission level."""
        effective = self.get_effective_permissions(
            pipeline_id, user_id, user_orgs, user_teams
        )
        if effective.effective_level is None:
            return False
        return level_includes(effective.effective_level, required_level)

    def get_effective_permissions(
        self,
        pipeline_id: str,
        user_id: str,
        user_orgs: Optional[List[str]] = None,
        user_teams: Optional[List[str]] = None,
    ) -> EffectivePermissions:
        """Calculate effective permissions for a user on a pipeline."""
        user_orgs = user_orgs or []
        user_teams = user_teams or []

        result = EffectivePermissions(
            pipeline_id=pipeline_id,
            user_id=user_id,
        )

        # Get pipeline permissions
        perms = self.get_pipeline_permissions(pipeline_id)
        if not perms:
            return result

        # Check ownership
        if perms.owner_id == user_id:
            result.is_owner = True
            result.effective_level = PermissionLevel.ADMIN
            result.can_view = True
            result.can_run = True
            result.can_edit = True
            result.can_admin = True
            return result

        levels: List[PermissionLevel] = []

        # Check direct grants
        for grant in perms.grants:
            if self._grant_matches_user(grant, user_id, user_orgs, user_teams):
                levels.append(grant.level)
                if grant.principal_type == PrincipalType.USER and \
                   grant.principal_id == user_id:
                    result.direct_grant = grant

        # Check folder inheritance
        if perms.inherit_from_folder and perms.folder_id:
            inherited = self._get_inherited_grants(
                perms.folder_id, user_id, user_orgs, user_teams
            )
            result.inherited_grants = inherited
            levels.extend([g.level for g in inherited])

        # Check visibility-based access
        if perms.visibility == PipelineVisibility.PUBLIC:
            result.visibility_access = True
            levels.append(PermissionLevel.VIEW)
        elif perms.visibility == PipelineVisibility.ORG and user_orgs:
            # User is in an org, grant view access
            result.visibility_access = True
            levels.append(PermissionLevel.VIEW)

        # Check wildcard grants
        for grant in perms.grants:
            if grant.principal_type == PrincipalType.WILDCARD:
                levels.append(grant.level)

        # Calculate effective level
        result.effective_level = get_max_level(levels)

        # Set capability flags
        if result.effective_level:
            result.can_view = level_includes(
                result.effective_level, PermissionLevel.VIEW
            )
            result.can_run = level_includes(
                result.effective_level, PermissionLevel.RUN
            )
            result.can_edit = level_includes(
                result.effective_level, PermissionLevel.EDIT
            )
            result.can_admin = level_includes(
                result.effective_level, PermissionLevel.ADMIN
            )

        return result

    def _grant_matches_user(
        self,
        grant: PermissionGrant,
        user_id: str,
        user_orgs: List[str],
        user_teams: List[str],
    ) -> bool:
        """Check if a grant applies to a user."""
        if grant.principal_type == PrincipalType.USER:
            return grant.principal_id == user_id
        elif grant.principal_type == PrincipalType.ORG:
            return grant.principal_id in user_orgs
        elif grant.principal_type == PrincipalType.TEAM:
            return grant.principal_id in user_teams
        elif grant.principal_type == PrincipalType.WILDCARD:
            return True
        return False

    def _get_inherited_grants(
        self,
        folder_id: str,
        user_id: str,
        user_orgs: List[str],
        user_teams: List[str],
        visited: Optional[set] = None,
    ) -> List[PermissionGrant]:
        """Get grants inherited from folder hierarchy."""
        if visited is None:
            visited = set()

        if folder_id in visited:
            return []  # Prevent cycles

        visited.add(folder_id)

        folder_perms = self.get_folder_permissions(folder_id)
        if not folder_perms:
            return []

        matching: List[PermissionGrant] = []

        for grant in folder_perms.grants:
            if self._grant_matches_user(grant, user_id, user_orgs, user_teams):
                matching.append(grant)

        # Recurse to parent folder
        if folder_perms.parent_folder_id:
            matching.extend(self._get_inherited_grants(
                folder_perms.parent_folder_id, user_id, user_orgs, user_teams,
                visited
            ))

        return matching

    # Cleanup

    def delete_pipeline_permissions(self, pipeline_id: str) -> bool:
        """Delete all permissions for a pipeline."""
        conn = self._get_conn()
        try:
            conn.execute(
                "DELETE FROM permission_grants WHERE pipeline_id = ?",
                (pipeline_id,)
            )
            result = conn.execute(
                "DELETE FROM pipeline_permissions WHERE pipeline_id = ?",
                (pipeline_id,)
            )
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    def delete_folder_permissions(self, folder_id: str) -> bool:
        """Delete all permissions for a folder."""
        conn = self._get_conn()
        try:
            conn.execute(
                "DELETE FROM permission_grants WHERE folder_id = ?",
                (folder_id,)
            )
            result = conn.execute(
                "DELETE FROM folder_permissions WHERE folder_id = ?",
                (folder_id,)
            )
            conn.commit()
            return result.rowcount > 0
        finally:
            conn.close()

    # List operations

    def list_user_accessible_pipelines(
        self,
        user_id: str,
        min_level: PermissionLevel = PermissionLevel.VIEW,
        user_orgs: Optional[List[str]] = None,
        user_teams: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """List all pipelines a user can access at a minimum level."""
        user_orgs = user_orgs or []
        user_teams = user_teams or []

        conn = self._get_conn()
        try:
            # Get all pipeline permissions
            rows = conn.execute(
                "SELECT * FROM pipeline_permissions"
            ).fetchall()

            accessible: List[Dict[str, Any]] = []

            for row in rows:
                pipeline_id = row["pipeline_id"]
                effective = self.get_effective_permissions(
                    pipeline_id, user_id, user_orgs, user_teams
                )

                if effective.effective_level and level_includes(
                    effective.effective_level, min_level
                ):
                    accessible.append({
                        "pipeline_id": pipeline_id,
                        "effective_level": effective.effective_level.value,
                        "is_owner": effective.is_owner,
                    })

            return accessible
        finally:
            conn.close()


# Global instance
_permission_storage: Optional[PermissionStorage] = None


def get_permission_storage() -> PermissionStorage:
    """Get the global permission storage instance."""
    global _permission_storage
    if _permission_storage is None:
        _permission_storage = PermissionStorage()
    return _permission_storage


def reset_permission_storage() -> None:
    """Reset the global permission storage instance."""
    global _permission_storage
    _permission_storage = None
