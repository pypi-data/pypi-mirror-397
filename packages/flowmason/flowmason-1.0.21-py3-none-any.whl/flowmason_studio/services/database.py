"""
Database Service for FlowMason Studio.

Supports both SQLite (development/testing) and PostgreSQL (production).

Environment Variables:
- FLOWMASON_DB_TYPE: "sqlite" (default) or "postgresql"
- FLOWMASON_DB_PATH: SQLite database file path (default: .flowmason/flowmason.db)
- FLOWMASON_DB_URL: PostgreSQL connection URL (e.g., postgresql://user:pass@host:5432/dbname)
- FLOWMASON_DB_HOST: PostgreSQL host (alternative to URL)
- FLOWMASON_DB_PORT: PostgreSQL port (default: 5432)
- FLOWMASON_DB_NAME: PostgreSQL database name
- FLOWMASON_DB_USER: PostgreSQL username
- FLOWMASON_DB_PASSWORD: PostgreSQL password
- FLOWMASON_DB_SSL: Enable SSL for PostgreSQL (default: false)
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Type alias for connection types
ConnectionType = Union[sqlite3.Connection, Any]  # Any for psycopg2.connection


class DatabaseConfig:
    """Database configuration from environment variables."""

    def __init__(self):
        self.db_type = os.environ.get("FLOWMASON_DB_TYPE", "sqlite").lower()

        # SQLite configuration
        self.sqlite_path = os.environ.get("FLOWMASON_DB_PATH", ".flowmason/flowmason.db")

        # PostgreSQL configuration
        self.pg_url = os.environ.get("FLOWMASON_DB_URL")
        self.pg_host = os.environ.get("FLOWMASON_DB_HOST", "localhost")
        self.pg_port = int(os.environ.get("FLOWMASON_DB_PORT", "5432"))
        self.pg_name = os.environ.get("FLOWMASON_DB_NAME", "flowmason")
        self.pg_user = os.environ.get("FLOWMASON_DB_USER", "flowmason")
        self.pg_password = os.environ.get("FLOWMASON_DB_PASSWORD", "")
        self.pg_ssl = os.environ.get("FLOWMASON_DB_SSL", "false").lower() == "true"

    @property
    def is_postgresql(self) -> bool:
        return bool(self.db_type == "postgresql")

    @property
    def postgresql_dsn(self) -> str:
        """Get PostgreSQL connection DSN."""
        if self.pg_url:
            return str(self.pg_url)

        ssl_param = "?sslmode=require" if self.pg_ssl else ""
        return f"postgresql://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_name}{ssl_param}"


# Global configuration
_config: Optional[DatabaseConfig] = None


def _get_config() -> DatabaseConfig:
    """Get or create the database configuration."""
    global _config
    if _config is None:
        _config = DatabaseConfig()
    return _config


def _get_db_path() -> Path:
    """Get the SQLite database file path."""
    config = _get_config()
    path = Path(config.sqlite_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# Global connections
_sqlite_connection: Optional[sqlite3.Connection] = None
_pg_connection: Optional[Any] = None  # psycopg2.connection


def get_connection() -> ConnectionType:
    """Get or create the database connection based on configuration."""
    config = _get_config()

    if config.is_postgresql:
        return _get_postgresql_connection()
    else:
        return _get_sqlite_connection()


def _get_sqlite_connection() -> sqlite3.Connection:
    """Get or create the SQLite connection."""
    global _sqlite_connection
    if _sqlite_connection is None:
        db_path = _get_db_path()
        _sqlite_connection = sqlite3.connect(
            str(db_path),
            check_same_thread=False,
            isolation_level=None  # autocommit mode
        )
        _sqlite_connection.row_factory = sqlite3.Row
        _init_sqlite_schema(_sqlite_connection)
    return _sqlite_connection


def _get_postgresql_connection() -> Any:
    """Get or create the PostgreSQL connection."""
    global _pg_connection
    if _pg_connection is None:
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError(
                "psycopg2 is required for PostgreSQL support. "
                "Install it with: pip install psycopg2-binary"
            )

        config = _get_config()
        _pg_connection = psycopg2.connect(
            config.postgresql_dsn,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        _pg_connection.autocommit = True
        _init_postgresql_schema(_pg_connection)
    return _pg_connection


def _init_sqlite_schema(conn: sqlite3.Connection) -> None:
    """Initialize the SQLite database schema."""
    # First create base tables without newer columns
    conn.executescript("""
        -- Pipelines table (base schema)
        CREATE TABLE IF NOT EXISTS pipelines (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            version TEXT NOT NULL DEFAULT '1.0.0',
            category TEXT,
            tags TEXT,  -- JSON array
            input_schema TEXT,  -- JSON
            output_schema TEXT,  -- JSON
            stages TEXT,  -- JSON array
            output_stage_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        -- Pipeline runs table
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            pipeline_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            inputs TEXT,  -- JSON
            output TEXT,  -- JSON
            error TEXT,
            stage_results TEXT,  -- JSON
            trace_id TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            duration_ms INTEGER,
            usage TEXT,  -- JSON
            FOREIGN KEY (pipeline_id) REFERENCES pipelines(id)
        );
    """)

    # Migration: Add is_template column if it doesn't exist
    try:
        conn.execute("ALTER TABLE pipelines ADD COLUMN is_template INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: Add status column (draft/published)
    try:
        conn.execute("ALTER TABLE pipelines ADD COLUMN status TEXT NOT NULL DEFAULT 'draft'")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: Add sample_input column (JSON for test data)
    try:
        conn.execute("ALTER TABLE pipelines ADD COLUMN sample_input TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: Add last_test_run_id column (reference to successful test run)
    try:
        conn.execute("ALTER TABLE pipelines ADD COLUMN last_test_run_id TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: Add published_at column (timestamp when published)
    try:
        conn.execute("ALTER TABLE pipelines ADD COLUMN published_at TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: Add is_test_run column to runs table to distinguish test runs
    try:
        conn.execute("ALTER TABLE runs ADD COLUMN is_test_run INTEGER NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: Add debug_data column to runs table for stage input/output debugging
    try:
        conn.execute("ALTER TABLE runs ADD COLUMN debug_data TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: Add org_id column to pipelines table for multi-tenancy
    try:
        conn.execute("ALTER TABLE pipelines ADD COLUMN org_id TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: Add org_id column to runs table for multi-tenancy
    try:
        conn.execute("ALTER TABLE runs ADD COLUMN org_id TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Migration: Add output_config column to pipelines table
    try:
        conn.execute("ALTER TABLE pipelines ADD COLUMN output_config TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Create output_allowlist table for security
    conn.execute("""
        CREATE TABLE IF NOT EXISTS output_allowlist (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            entry_type TEXT NOT NULL,
            pattern TEXT NOT NULL,
            description TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_by TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT
        )
    """)

    # Create stored_connections table for database/MQ connections
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stored_connections (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            name TEXT NOT NULL,
            connection_type TEXT NOT NULL,
            host TEXT NOT NULL,
            port INTEGER,
            database_name TEXT,
            username TEXT,
            password_encrypted TEXT,
            ssl_enabled INTEGER NOT NULL DEFAULT 1,
            additional_config TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_by TEXT,
            created_at TEXT NOT NULL,
            last_used_at TEXT
        )
    """)

    # Create output_deliveries table for delivery logging
    conn.execute("""
        CREATE TABLE IF NOT EXISTS output_deliveries (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            destination_id TEXT NOT NULL,
            destination_type TEXT NOT NULL,
            destination_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            attempt_count INTEGER NOT NULL DEFAULT 1,
            response_code INTEGER,
            response_body TEXT,
            error_message TEXT,
            payload_size_bytes INTEGER,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            duration_ms INTEGER,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
    """)

    # Create indexes (after migrations to ensure columns exist)
    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_pipelines_category ON pipelines(category);
        CREATE INDEX IF NOT EXISTS idx_pipelines_updated_at ON pipelines(updated_at);
        CREATE INDEX IF NOT EXISTS idx_pipelines_is_template ON pipelines(is_template);
        CREATE INDEX IF NOT EXISTS idx_pipelines_status ON pipelines(status);
        CREATE INDEX IF NOT EXISTS idx_pipelines_org_id ON pipelines(org_id);
        CREATE INDEX IF NOT EXISTS idx_pipelines_name ON pipelines(name);
        CREATE INDEX IF NOT EXISTS idx_runs_pipeline_id ON runs(pipeline_id);
        CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
        CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs(started_at);
        CREATE INDEX IF NOT EXISTS idx_runs_is_test_run ON runs(is_test_run);
        CREATE INDEX IF NOT EXISTS idx_runs_org_id ON runs(org_id);
        CREATE INDEX IF NOT EXISTS idx_allowlist_org_id ON output_allowlist(org_id);
        CREATE INDEX IF NOT EXISTS idx_allowlist_entry_type ON output_allowlist(entry_type);
        CREATE INDEX IF NOT EXISTS idx_allowlist_is_active ON output_allowlist(is_active);
        CREATE INDEX IF NOT EXISTS idx_connections_org_id ON stored_connections(org_id);
        CREATE INDEX IF NOT EXISTS idx_connections_type ON stored_connections(connection_type);
        CREATE INDEX IF NOT EXISTS idx_deliveries_run_id ON output_deliveries(run_id);
        CREATE INDEX IF NOT EXISTS idx_deliveries_status ON output_deliveries(status);
    """)


def _init_postgresql_schema(conn: Any) -> None:
    """Initialize the PostgreSQL database schema."""
    with conn.cursor() as cur:
        # Create pipelines table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pipelines (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                version TEXT NOT NULL DEFAULT '1.0.0',
                category TEXT,
                tags JSONB,
                input_schema JSONB,
                output_schema JSONB,
                stages JSONB,
                output_stage_id TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                is_template BOOLEAN NOT NULL DEFAULT FALSE,
                status TEXT NOT NULL DEFAULT 'draft',
                sample_input JSONB,
                last_test_run_id TEXT,
                published_at TIMESTAMP,
                org_id TEXT,
                output_config JSONB
            )
        """)

        # Create runs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                pipeline_id TEXT NOT NULL REFERENCES pipelines(id),
                status TEXT NOT NULL DEFAULT 'pending',
                inputs JSONB,
                output JSONB,
                error TEXT,
                stage_results JSONB,
                trace_id TEXT,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                duration_ms INTEGER,
                usage JSONB,
                is_test_run BOOLEAN NOT NULL DEFAULT FALSE,
                debug_data JSONB,
                org_id TEXT
            )
        """)

        # Create output_allowlist table for security
        cur.execute("""
            CREATE TABLE IF NOT EXISTS output_allowlist (
                id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                pattern TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_by TEXT,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP
            )
        """)

        # Create stored_connections table for database/MQ connections
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stored_connections (
                id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                name TEXT NOT NULL,
                connection_type TEXT NOT NULL,
                host TEXT NOT NULL,
                port INTEGER,
                database_name TEXT,
                username TEXT,
                password_encrypted TEXT,
                ssl_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                additional_config JSONB,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_by TEXT,
                created_at TIMESTAMP NOT NULL,
                last_used_at TIMESTAMP
            )
        """)

        # Create output_deliveries table for delivery logging
        cur.execute("""
            CREATE TABLE IF NOT EXISTS output_deliveries (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL REFERENCES runs(id),
                destination_id TEXT NOT NULL,
                destination_type TEXT NOT NULL,
                destination_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                attempt_count INTEGER NOT NULL DEFAULT 1,
                response_code INTEGER,
                response_body TEXT,
                error_message TEXT,
                payload_size_bytes INTEGER,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                duration_ms INTEGER
            )
        """)

        # Create indexes for pipelines
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pipelines_category ON pipelines(category)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pipelines_updated_at ON pipelines(updated_at)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pipelines_is_template ON pipelines(is_template)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pipelines_status ON pipelines(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pipelines_org_id ON pipelines(org_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_pipelines_name ON pipelines(name)")

        # Create indexes for runs
        cur.execute("CREATE INDEX IF NOT EXISTS idx_runs_pipeline_id ON runs(pipeline_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs(started_at)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_runs_is_test_run ON runs(is_test_run)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_runs_org_id ON runs(org_id)")

        # Create indexes for allowlist
        cur.execute("CREATE INDEX IF NOT EXISTS idx_allowlist_org_id ON output_allowlist(org_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_allowlist_entry_type ON output_allowlist(entry_type)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_allowlist_is_active ON output_allowlist(is_active)")

        # Create indexes for connections
        cur.execute("CREATE INDEX IF NOT EXISTS idx_connections_org_id ON stored_connections(org_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_connections_type ON stored_connections(connection_type)")

        # Create indexes for deliveries
        cur.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_run_id ON output_deliveries(run_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_status ON output_deliveries(status)")


def close_connection() -> None:
    """Close the database connection."""
    global _sqlite_connection, _pg_connection
    if _sqlite_connection is not None:
        _sqlite_connection.close()
        _sqlite_connection = None
    if _pg_connection is not None:
        _pg_connection.close()
        _pg_connection = None


@contextmanager
def transaction():
    """Context manager for transactions."""
    config = _get_config()
    conn = get_connection()

    if config.is_postgresql:
        # PostgreSQL transaction
        old_autocommit = conn.autocommit
        conn.autocommit = False
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.autocommit = old_autocommit
    else:
        # SQLite transaction
        try:
            conn.execute("BEGIN")
            yield conn
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise


def is_postgresql() -> bool:
    """Check if using PostgreSQL."""
    return _get_config().is_postgresql


def get_placeholder(index: int = 1) -> str:
    """Get the parameter placeholder for the current database.

    SQLite uses ? placeholders, PostgreSQL uses $1, $2, etc.
    """
    config = _get_config()
    if config.is_postgresql:
        return f"${index}"
    else:
        return "?"


def adapt_query(query: str) -> str:
    """Adapt a query for the current database.

    Converts ? placeholders to $1, $2, etc. for PostgreSQL.
    """
    config = _get_config()
    if not config.is_postgresql:
        return query

    # Replace ? placeholders with $1, $2, etc.
    result = []
    placeholder_count = 0
    for char in query:
        if char == '?':
            placeholder_count += 1
            result.append(f'${placeholder_count}')
        else:
            result.append(char)
    return ''.join(result)


def execute_query(query: str, params: tuple = ()) -> Any:
    """Execute a query with automatic placeholder adaptation.

    Args:
        query: SQL query with ? placeholders
        params: Query parameters

    Returns:
        Cursor or result depending on database
    """
    config = _get_config()
    conn = get_connection()
    adapted_query = adapt_query(query)

    if config.is_postgresql:
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(adapted_query, params)
            return cur
    else:
        return conn.execute(adapted_query, params)


def fetchall(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a query and fetch all results as dictionaries.

    Args:
        query: SQL query with ? placeholders
        params: Query parameters

    Returns:
        List of dictionaries with column names as keys
    """
    config = _get_config()
    conn = get_connection()
    adapted_query = adapt_query(query)

    if config.is_postgresql:
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(adapted_query, params)
            return [dict(row) for row in cur.fetchall()]
    else:
        cursor = conn.execute(adapted_query, params)
        return [dict(row) for row in cursor.fetchall()]


def fetchone(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Execute a query and fetch one result as a dictionary.

    Args:
        query: SQL query with ? placeholders
        params: Query parameters

    Returns:
        Dictionary with column names as keys, or None
    """
    config = _get_config()
    conn = get_connection()
    adapted_query = adapt_query(query)

    if config.is_postgresql:
        with conn.cursor() as cur:  # type: ignore[union-attr]
            cur.execute(adapted_query, params)
            row = cur.fetchone()
            return dict(row) if row else None
    else:
        cursor = conn.execute(adapted_query, params)
        row = cursor.fetchone()
        return dict(row) if row else None


def setup_test_database() -> None:
    """Set up an in-memory database for testing.

    This resets the global connection and creates a fresh in-memory SQLite database.
    Should be called at the start of each test that needs a clean database.
    """
    global _sqlite_connection, _config

    # Close any existing connection
    close_connection()

    # Reset config to force in-memory database
    _config = DatabaseConfig()
    _config.db_type = "sqlite"
    _config.sqlite_path = ":memory:"

    # Force new connection with schema initialization
    _sqlite_connection = sqlite3.connect(
        ":memory:",
        check_same_thread=False,
        isolation_level=None
    )
    _sqlite_connection.row_factory = sqlite3.Row
    _init_sqlite_schema(_sqlite_connection)


def teardown_test_database() -> None:
    """Tear down the test database.

    Closes connections and resets config to defaults.
    """
    global _config
    close_connection()
    _config = None
