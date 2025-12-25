"""Database connection and session management."""

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator, Optional

from server.core.settings import db_settings
from server.models import Base


# Lazy initialization of engine and session factory
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """Get or create the database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            db_settings.database_url,
            pool_size=db_settings.db_pool_size,
            max_overflow=db_settings.db_max_overflow,
            pool_pre_ping=db_settings.db_pool_pre_ping,
            echo=db_settings.db_echo,
        )
    return _engine


def get_session_local() -> sessionmaker:
    """Get or create the session factory (lazy initialization)."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal


# Module-level variables for backward compatibility
# These are lazily initialized on first access
engine: Optional[Engine] = None
SessionLocal: Optional[sessionmaker] = None


def _ensure_engine() -> Engine:
    """Ensure engine is initialized."""
    global engine
    if engine is None:
        engine = get_engine()
    return engine


def _ensure_session_local() -> sessionmaker:
    """Ensure SessionLocal is initialized.

    If SessionLocal has been patched (e.g., in tests), it will be used directly.
    Otherwise, it will be lazily initialized.
    """
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = get_session_local()
    # If SessionLocal is not None (either initialized or patched), return it
    return SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session."""
    db = _ensure_session_local()()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    db = _ensure_session_local()()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=_ensure_engine())
