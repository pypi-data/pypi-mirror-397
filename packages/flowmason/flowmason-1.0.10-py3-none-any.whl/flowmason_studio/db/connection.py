"""
Database Connection Manager for FlowMason Studio.

Supports both SQLite (development) and PostgreSQL/Supabase (production).
Configuration is determined by environment variables.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from flowmason_studio.db.models import Base

logger = logging.getLogger(__name__)


class Database:
    """
    Database connection manager.

    Supports:
    - SQLite for local development (default)
    - PostgreSQL/Supabase for production

    Configuration:
    - DATABASE_URL: PostgreSQL connection string (takes precedence)
    - FLOWMASON_DB_PATH: SQLite database path (defaults to ~/.flowmason/studio.db)
    """

    db_path: Optional[str]
    db_type: str

    def __init__(
        self,
        database_url: Optional[str] = None,
        db_path: Optional[str] = None,
    ):
        """
        Initialize database connection.

        Args:
            database_url: PostgreSQL connection URL (takes precedence)
                Format: postgresql://user:password@host:port/dbname
                For Supabase: postgresql://postgres:[PASSWORD]@[PROJECT].supabase.co:5432/postgres
            db_path: SQLite database path (used if database_url not provided)
        """
        # Check environment variables
        database_url = database_url or os.getenv("DATABASE_URL")
        db_path = db_path or os.getenv("FLOWMASON_DB_PATH")

        if database_url:
            # Use PostgreSQL/Supabase
            self._init_postgresql(database_url)
        else:
            # Use SQLite
            self._init_sqlite(db_path)

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    def _init_postgresql(self, database_url: str) -> None:
        """Initialize PostgreSQL connection."""
        self.db_path = None
        self.db_type = "postgresql"

        logger.info("Connecting to PostgreSQL database")

        self.engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=10,
            max_overflow=20,
        )

    def _init_sqlite(self, db_path: Optional[str]) -> None:
        """Initialize SQLite connection."""
        if db_path is None:
            # Default to ~/.flowmason/studio.db
            db_dir = Path.home() / ".flowmason"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "studio.db")

        self.db_path = db_path
        self.db_type = "sqlite"

        logger.info(f"Using SQLite database: {db_path}")

        self.engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )

        # Enable foreign keys for SQLite
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def close(self) -> None:
        """Close database connection."""
        self.engine.dispose()
        logger.info("Database connection closed")


# =============================================================================
# Global Database Instance
# =============================================================================

_database: Optional[Database] = None


def init_database(
    database_url: Optional[str] = None,
    db_path: Optional[str] = None,
    create_tables: bool = True,
) -> Database:
    """
    Initialize the global database instance.

    Args:
        database_url: PostgreSQL connection URL
        db_path: SQLite database path
        create_tables: Whether to create tables on init

    Returns:
        Database instance
    """
    global _database
    _database = Database(database_url=database_url, db_path=db_path)
    if create_tables:
        _database.create_tables()
    return _database


def get_database() -> Database:
    """
    Get or create the global database instance.

    Returns:
        Database instance
    """
    global _database
    if _database is None:
        _database = Database()
        _database.create_tables()
    return _database


def get_session() -> Session:
    """
    Get a new database session from the global instance.

    Returns:
        SQLAlchemy Session
    """
    return get_database().get_session()


def set_database(db: Optional[Database]) -> None:
    """
    Set the global database instance (mainly for testing).

    Args:
        db: Database instance or None to reset
    """
    global _database
    _database = db
