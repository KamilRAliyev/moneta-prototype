"""Tests for database connection and session management."""

import pytest
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import Session
from unittest.mock import patch

from server.models import Base
from server.core.database import get_db, get_db_session


class TestModel(Base):
    """Test model for database tests."""

    __tablename__ = "test_models"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


def test_get_db_session_context_manager(test_db):
    """Test get_db_session context manager."""
    TestSessionLocal = test_db

    # Mock SessionLocal to use test database
    with patch("server.core.database.SessionLocal", TestSessionLocal):
        with get_db_session() as session:
            # Create test table
            Base.metadata.create_all(bind=session.bind)

            # Insert test data
            test_model = TestModel(name="test")
            session.add(test_model)
            # get_db_session commits automatically, but we need to flush first
            session.flush()

            # Verify data was inserted
            result = session.query(TestModel).filter_by(name="test").first()
            assert result is not None
            assert result.name == "test"


def test_get_db_generator(test_db):
    """Test get_db generator function."""
    TestSessionLocal = test_db

    # Mock SessionLocal to use test database
    with patch("server.core.database.SessionLocal", TestSessionLocal):
        # Create test table
        test_session = TestSessionLocal()
        Base.metadata.create_all(bind=test_session.bind)
        test_session.close()

        # Use generator
        db_gen = get_db()
        db = next(db_gen)

        try:
            # Insert test data
            test_model = TestModel(name="generator_test")
            db.add(test_model)
            db.commit()

            # Verify data
            result = db.query(TestModel).filter_by(name="generator_test").first()
            assert result is not None
            assert result.name == "generator_test"
        finally:
            # Close generator (should close session)
            try:
                next(db_gen)
            except StopIteration:
                pass


def test_database_session_rollback(test_db):
    """Test that database session rollback works."""
    TestSessionLocal = test_db
    session = TestSessionLocal()

    try:
        Base.metadata.create_all(bind=session.bind)

        # Add data
        test_model = TestModel(name="rollback_test")
        session.add(test_model)
        session.flush()  # Flush but don't commit

        # Rollback
        session.rollback()

        # Verify data was not committed
        result = session.query(TestModel).filter_by(name="rollback_test").first()
        assert result is None
    finally:
        session.close()


def test_database_query_execution(test_db):
    """Test that database queries can be executed."""
    TestSessionLocal = test_db
    session = TestSessionLocal()

    try:
        Base.metadata.create_all(bind=session.bind)

        # Execute raw SQL query
        result = session.execute(text("SELECT 1 as value"))
        row = result.fetchone()
        assert row[0] == 1
    finally:
        session.close()
