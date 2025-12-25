"""Tests for database models."""

import pytest
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from server.models import Base


def test_base_model_inheritance():
    """Test that models can inherit from Base."""

    class TestModel(Base):
        __tablename__ = "test_table"

        id = Column(Integer, primary_key=True)
        name = Column(String(255))

    # Verify it's a proper SQLAlchemy model
    assert hasattr(TestModel, "__table__")
    assert TestModel.__tablename__ == "test_table"


def test_base_model_metadata(test_db):
    """Test that Base metadata works correctly."""

    class TestModel(Base):
        __tablename__ = "test_metadata"

        id = Column(Integer, primary_key=True)
        name = Column(String(255))

    TestSessionLocal = test_db

    # Create tables from metadata
    Base.metadata.create_all(bind=TestSessionLocal().bind)

    # Verify table was created
    from sqlalchemy import inspect

    inspector = inspect(TestSessionLocal().bind)
    tables = inspector.get_table_names()
    assert "test_metadata" in tables


def test_model_with_timestamps(test_db):
    """Test model with timestamp columns."""

    class TimestampModel(Base):
        __tablename__ = "timestamp_test"

        id = Column(Integer, primary_key=True)
        name = Column(String(255))
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    TestSessionLocal = test_db
    session = TestSessionLocal()

    try:
        Base.metadata.create_all(bind=session.bind)

        # Create instance
        model = TimestampModel(name="test")
        session.add(model)
        session.commit()

        # Verify it was saved
        result = session.query(TimestampModel).first()
        assert result is not None
        assert result.name == "test"
        assert result.created_at is not None
    finally:
        session.close()
