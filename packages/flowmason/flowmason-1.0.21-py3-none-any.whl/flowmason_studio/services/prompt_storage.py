"""
Prompt Library Storage Service.

Manages reusable prompt templates that can be shared across stages and pipelines.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class PromptTemplate:
    """A reusable prompt template."""

    id: str
    name: str
    org_id: str

    # Template content
    content: str  # The prompt text with {{variables}}
    system_prompt: Optional[str] = None  # Optional system prompt

    # Metadata
    description: str = ""
    category: str = ""  # e.g., "extraction", "generation", "analysis"
    tags: List[str] = field(default_factory=list)

    # Variables
    variables: List[str] = field(default_factory=list)  # Extracted from {{var}} syntax
    default_values: Dict[str, str] = field(default_factory=dict)

    # Model preferences
    recommended_model: Optional[str] = None  # e.g., "claude-3-5-sonnet-latest"
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

    # Tracking
    version: str = "1.0.0"
    created_at: str = ""
    updated_at: str = ""
    created_by: Optional[str] = None
    usage_count: int = 0
    last_used_at: Optional[str] = None

    # Sharing
    is_public: bool = False  # Visible to all orgs
    is_featured: bool = False  # Featured in gallery


class PromptStorage:
    """Storage for prompt templates using SQLite/PostgreSQL."""

    def __init__(self):
        """Initialize storage and create tables."""
        from flowmason_studio.services.database import get_connection
        self._conn = get_connection()
        self._create_tables()

    def _create_tables(self):
        """Create prompt tables if they don't exist."""
        from flowmason_studio.services.database import is_postgresql

        if is_postgresql():
            self._create_postgresql_tables()
        else:
            self._create_sqlite_tables()

    def _create_sqlite_tables(self):
        """Create SQLite tables."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS prompt_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                org_id TEXT NOT NULL,
                content TEXT NOT NULL,
                system_prompt TEXT,
                description TEXT DEFAULT '',
                category TEXT DEFAULT '',
                tags TEXT,
                variables TEXT,
                default_values TEXT,
                recommended_model TEXT,
                temperature REAL,
                max_tokens INTEGER,
                version TEXT DEFAULT '1.0.0',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                created_by TEXT,
                usage_count INTEGER DEFAULT 0,
                last_used_at TEXT,
                is_public INTEGER DEFAULT 0,
                is_featured INTEGER DEFAULT 0
            )
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompts_org ON prompt_templates(org_id)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompt_templates(category)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompts_public ON prompt_templates(is_public)
        """)

        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_prompts_name ON prompt_templates(name)
        """)

    def _create_postgresql_tables(self):
        """Create PostgreSQL tables."""
        with self._conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    org_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    system_prompt TEXT,
                    description TEXT DEFAULT '',
                    category TEXT DEFAULT '',
                    tags JSONB,
                    variables JSONB,
                    default_values JSONB,
                    recommended_model TEXT,
                    temperature REAL,
                    max_tokens INTEGER,
                    version TEXT DEFAULT '1.0.0',
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    created_by TEXT,
                    usage_count INTEGER DEFAULT 0,
                    last_used_at TIMESTAMP,
                    is_public BOOLEAN DEFAULT FALSE,
                    is_featured BOOLEAN DEFAULT FALSE
                )
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompts_org ON prompt_templates(org_id)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompt_templates(category)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompts_public ON prompt_templates(is_public)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompts_name ON prompt_templates(name)
            """)

    def _extract_variables(self, content: str) -> List[str]:
        """Extract variable names from {{variable}} syntax."""
        import re
        pattern = r'\{\{(\w+)\}\}'
        matches = re.findall(pattern, content)
        return list(set(matches))  # Unique variables

    def create(
        self,
        name: str,
        org_id: str,
        content: str,
        system_prompt: Optional[str] = None,
        description: str = "",
        category: str = "",
        tags: Optional[List[str]] = None,
        default_values: Optional[Dict[str, str]] = None,
        recommended_model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        created_by: Optional[str] = None,
        is_public: bool = False,
    ) -> PromptTemplate:
        """Create a new prompt template."""
        import uuid

        prompt_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Extract variables from content
        variables = self._extract_variables(content)
        if system_prompt:
            variables.extend(self._extract_variables(system_prompt))
            variables = list(set(variables))

        self._conn.execute(
            """
            INSERT INTO prompt_templates (
                id, name, org_id, content, system_prompt, description,
                category, tags, variables, default_values, recommended_model,
                temperature, max_tokens, created_at, updated_at, created_by,
                is_public
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prompt_id,
                name,
                org_id,
                content,
                system_prompt,
                description,
                category,
                json.dumps(tags or []),
                json.dumps(variables),
                json.dumps(default_values or {}),
                recommended_model,
                temperature,
                max_tokens,
                now,
                now,
                created_by,
                1 if is_public else 0,
            ),
        )

        return PromptTemplate(
            id=prompt_id,
            name=name,
            org_id=org_id,
            content=content,
            system_prompt=system_prompt,
            description=description,
            category=category,
            tags=tags or [],
            variables=variables,
            default_values=default_values or {},
            recommended_model=recommended_model,
            temperature=temperature,
            max_tokens=max_tokens,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            is_public=is_public,
        )

    def get(self, prompt_id: str, org_id: Optional[str] = None) -> Optional[PromptTemplate]:
        """Get a prompt by ID."""
        query = "SELECT * FROM prompt_templates WHERE id = ?"
        params = [prompt_id]

        if org_id:
            # Allow access if org matches OR prompt is public
            query += " AND (org_id = ? OR is_public = 1)"
            params.append(org_id)

        cursor = self._conn.execute(query, params)
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_prompt(row)

    def get_by_name(
        self,
        name: str,
        org_id: str,
    ) -> Optional[PromptTemplate]:
        """Get a prompt by name."""
        cursor = self._conn.execute(
            """
            SELECT * FROM prompt_templates
            WHERE name = ? AND (org_id = ? OR is_public = 1)
            ORDER BY org_id = ? DESC
            LIMIT 1
            """,
            (name, org_id, org_id),
        )
        row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_prompt(row)

    def list(
        self,
        org_id: str,
        category: Optional[str] = None,
        search: Optional[str] = None,
        include_public: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[PromptTemplate], int]:
        """List prompts for an organization."""
        if include_public:
            query = "SELECT * FROM prompt_templates WHERE (org_id = ? OR is_public = 1)"
            count_query = "SELECT COUNT(*) FROM prompt_templates WHERE (org_id = ? OR is_public = 1)"
        else:
            query = "SELECT * FROM prompt_templates WHERE org_id = ?"
            count_query = "SELECT COUNT(*) FROM prompt_templates WHERE org_id = ?"

        params: List[Any] = [org_id]

        if category:
            query += " AND category = ?"
            count_query += " AND category = ?"
            params.append(category)

        if search:
            query += " AND (name LIKE ? OR description LIKE ? OR content LIKE ?)"
            count_query += " AND (name LIKE ? OR description LIKE ? OR content LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        # Get total count
        cursor = self._conn.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        query += " ORDER BY is_featured DESC, usage_count DESC, updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self._conn.execute(query, params)
        prompts = [self._row_to_prompt(row) for row in cursor.fetchall()]

        return prompts, total

    def list_categories(self, org_id: str) -> List[str]:
        """List all categories for an organization."""
        cursor = self._conn.execute(
            """
            SELECT DISTINCT category FROM prompt_templates
            WHERE (org_id = ? OR is_public = 1) AND category != ''
            ORDER BY category
            """,
            (org_id,),
        )
        return [row[0] for row in cursor.fetchall()]

    def update(
        self,
        prompt_id: str,
        org_id: str,
        name: Optional[str] = None,
        content: Optional[str] = None,
        system_prompt: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        default_values: Optional[Dict[str, str]] = None,
        recommended_model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        is_public: Optional[bool] = None,
    ) -> Optional[PromptTemplate]:
        """Update a prompt template."""
        updates: List[str] = []
        params: List[Any] = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if content is not None:
            updates.append("content = ?")
            params.append(content)
            # Re-extract variables
            variables = self._extract_variables(content)
            updates.append("variables = ?")
            params.append(json.dumps(variables))

        if system_prompt is not None:
            updates.append("system_prompt = ?")
            params.append(system_prompt)

        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if category is not None:
            updates.append("category = ?")
            params.append(category)

        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))

        if default_values is not None:
            updates.append("default_values = ?")
            params.append(json.dumps(default_values))

        if recommended_model is not None:
            updates.append("recommended_model = ?")
            params.append(recommended_model)

        if temperature is not None:
            updates.append("temperature = ?")
            params.append(temperature)

        if max_tokens is not None:
            updates.append("max_tokens = ?")
            params.append(max_tokens)

        if is_public is not None:
            updates.append("is_public = ?")
            params.append(1 if is_public else 0)

        if not updates:
            return self.get(prompt_id, org_id)

        # Increment version
        updates.append("version = (SELECT CAST(CAST(SUBSTR(version, 1, INSTR(version, '.') - 1) AS INTEGER) AS TEXT) || '.' || CAST(CAST(SUBSTR(version, INSTR(version, '.') + 1, INSTR(SUBSTR(version, INSTR(version, '.') + 1), '.') - 1) AS INTEGER) AS TEXT) || '.' || CAST(CAST(SUBSTR(version, LENGTH(version) - INSTR(REVERSE(version), '.') + 2) AS INTEGER) + 1 AS TEXT) FROM prompt_templates WHERE id = ?)")
        params.append(prompt_id)

        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())

        params.extend([prompt_id, org_id])

        self._conn.execute(
            f"UPDATE prompt_templates SET {', '.join(updates)} WHERE id = ? AND org_id = ?",
            params,
        )

        return self.get(prompt_id, org_id)

    def delete(self, prompt_id: str, org_id: str) -> bool:
        """Delete a prompt template."""
        cursor = self._conn.execute(
            "DELETE FROM prompt_templates WHERE id = ? AND org_id = ?",
            (prompt_id, org_id),
        )
        return bool(cursor.rowcount > 0)

    def record_usage(self, prompt_id: str):
        """Record that a prompt was used."""
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            """
            UPDATE prompt_templates
            SET usage_count = usage_count + 1, last_used_at = ?
            WHERE id = ?
            """,
            (now, prompt_id),
        )

    def render(
        self,
        prompt_id: str,
        org_id: str,
        variables: Dict[str, str],
    ) -> Optional[Dict[str, str]]:
        """
        Render a prompt template with variables.

        Returns dict with 'content' and optionally 'system_prompt'.
        """
        prompt = self.get(prompt_id, org_id)
        if not prompt:
            return None

        # Merge default values with provided values
        merged = {**prompt.default_values, **variables}

        # Render content
        rendered_content = prompt.content
        for var_name, var_value in merged.items():
            rendered_content = rendered_content.replace(f"{{{{{var_name}}}}}", str(var_value))

        result = {"content": rendered_content}

        # Render system prompt if present
        if prompt.system_prompt:
            rendered_system = prompt.system_prompt
            for var_name, var_value in merged.items():
                rendered_system = rendered_system.replace(f"{{{{{var_name}}}}}", str(var_value))
            result["system_prompt"] = rendered_system

        # Record usage
        self.record_usage(prompt_id)

        return result

    def _row_to_prompt(self, row) -> PromptTemplate:
        """Convert a database row to a PromptTemplate."""
        return PromptTemplate(
            id=row["id"],
            name=row["name"],
            org_id=row["org_id"],
            content=row["content"],
            system_prompt=row["system_prompt"],
            description=row["description"] or "",
            category=row["category"] or "",
            tags=json.loads(row["tags"]) if row["tags"] else [],
            variables=json.loads(row["variables"]) if row["variables"] else [],
            default_values=json.loads(row["default_values"]) if row["default_values"] else {},
            recommended_model=row["recommended_model"],
            temperature=row["temperature"],
            max_tokens=row["max_tokens"],
            version=row["version"] or "1.0.0",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            created_by=row["created_by"],
            usage_count=row["usage_count"] or 0,
            last_used_at=row["last_used_at"],
            is_public=bool(row["is_public"]),
            is_featured=bool(row["is_featured"]),
        )


# Global instance
_prompt_storage: Optional[PromptStorage] = None


def get_prompt_storage() -> PromptStorage:
    """Get the global prompt storage instance."""
    global _prompt_storage
    if _prompt_storage is None:
        _prompt_storage = PromptStorage()
    return _prompt_storage
