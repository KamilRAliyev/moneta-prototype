"""Pydantic schemas for Transaction API."""

import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StatementFileSummary(BaseModel):
    """Minimal statement file info for transaction response."""

    id: uuid.UUID
    original_filename: str
    columns: Optional[List[str]] = None


class AccountSummary(BaseModel):
    """Full account info for transaction response."""

    id: int
    name: str
    institution: str
    currency: str
    type: str
    economic_area: Optional[str] = None
    datelock_from: Optional[date] = None
    datelock_to: Optional[date] = None


class TransactionResponse(BaseModel):
    """Schema for single transaction response."""

    id: uuid.UUID
    row_id: int
    statement_file: StatementFileSummary
    account: AccountSummary
    ingested_content: Dict[str, Any]
    computed_content: Dict[str, Any] = Field(default_factory=dict)
    inserted_at: datetime


class TransactionListMeta(BaseModel):
    """Pagination metadata for transaction list."""

    page: int
    page_size: int
    total: int
    total_pages: int


class TransactionListResponse(BaseModel):
    """Schema for transaction list response with pagination."""

    items: List[TransactionResponse]
    meta: TransactionListMeta


class ColumnMetadata(BaseModel):
    """Metadata for a single column in ingested_content."""

    name: str
    type: str = Field(..., description="Field type: 'date', 'number', or 'string'")
    sample_values: List[str] = Field(default_factory=list)
    nullable: bool = True
    min: Optional[Any] = None  # For date/number types
    max: Optional[Any] = None  # For date/number types


class TransactionMetaResponse(BaseModel):
    """Schema for transaction metadata (column information)."""

    ingested_columns: List[ColumnMetadata] = Field(default_factory=list)
    computed_columns: List[ColumnMetadata] = Field(
        default_factory=list, description="Empty for now (out of scope)"
    )


class IngestionError(BaseModel):
    """Schema for ingestion error details."""

    row_id: int
    reason: str = Field(
        ..., description="Error reason: 'date_lock', 'parse_error', etc."
    )
    message: str


class IngestionSummary(BaseModel):
    """Summary of ingestion results."""

    total_rows: int
    ingested: int
    skipped: int
    errors: int


class IngestionResponse(BaseModel):
    """Schema for ingestion response."""

    statement_id: uuid.UUID
    status: str = Field(..., description="Status: 'completed', 'partial', or 'failed'")
    summary: IngestionSummary
    errors: List[IngestionError] = Field(default_factory=list)
