"""Database configuration and dependencies."""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

# Get DATABASE_URL from environment - no hardcoded default
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    error_msg = "DATABASE_URL environment variable is not set"
    logger.error(error_msg)
    raise ValueError(error_msg)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session dependency."""
    logger.debug("Creating new database session")
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        db.close()
