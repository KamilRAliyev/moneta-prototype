"""Statement file model."""

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Index,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from server.models import Base


class StatementFormat(enum.Enum):
    """Statement file format enumeration."""

    CSV = "csv"


class StatementStatus(enum.Enum):
    """Statement file status enumeration."""

    UPLOADED = "uploaded"


class StatementFile(Base):
    """Statement file model for managing uploaded statement files."""

    __tablename__ = "statement_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    stored_path = Column(String(512), nullable=False)
    format = Column(Enum(StatementFormat, native_enum=False), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False)  # SHA-256 hex string
    row_count = Column(Integer, nullable=False)
    columns = Column(JSON, nullable=True)  # Array of column names
    date_from = Column(Date, nullable=True)
    date_to = Column(Date, nullable=True)
    status = Column(Enum(StatementStatus, native_enum=False), nullable=False)
    is_ingested = Column(Boolean, nullable=False, default=False)
    ingested_at = Column(DateTime(timezone=True), nullable=True)
    ingested_rows_count = Column(Integer, nullable=False, default=0)
    ingestion_errors_count = Column(Integer, nullable=False, default=0)
    date_column = Column(String(255), nullable=True)  # Detected date column name
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint: prevent duplicate uploads per account
    __table_args__ = (
        UniqueConstraint(
            "account_id", "content_hash", name="uq_statement_account_hash"
        ),
        # Index for efficient list queries by account, ordered by created_at DESC
        Index("ix_statement_account_created", "account_id", "created_at"),
    )
