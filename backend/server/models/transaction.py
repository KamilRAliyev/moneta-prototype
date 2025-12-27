"""Transaction model."""

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Index,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from server.models import Base


class Transaction(Base):
    """Transaction model for storing ingested transaction data."""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    statement_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("statement_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    row_id = Column(Integer, nullable=False)  # Row index in statement file
    ingested_content = Column(
        JSONB().with_variant(JSON(), "sqlite"), nullable=False
    )  # Raw row data as-is (JSONB for PostgreSQL, JSON for SQLite)
    transaction_hash = Column(
        String(64), nullable=False, index=True
    )  # SHA-256 hash for change tracking
    computed_content = Column(
        JSONB().with_variant(JSON(), "sqlite"), nullable=True
    )  # Empty for now (out of scope)
    computed_content_hash = Column(
        String(64), nullable=True
    )  # Hash of computed_content
    inserted_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    computed_at = Column(DateTime(timezone=True), nullable=True)  # Null (out of scope)

    # Unique constraint: prevent duplicate rows from same statement
    __table_args__ = (
        UniqueConstraint(
            "statement_file_id", "row_id", name="uq_transaction_statement_row"
        ),
        # Index for efficient list queries by account, ordered by inserted_at DESC
        Index("ix_transaction_account_inserted", "account_id", "inserted_at"),
    )
