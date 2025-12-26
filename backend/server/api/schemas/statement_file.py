"""Pydantic schemas for StatementFile API."""

import uuid
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class StatementFileResponse(BaseModel):
    """Schema for statement file response (full details)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: int
    account_name: Optional[str] = None  # Will be populated from join
    original_filename: str
    stored_filename: str
    stored_path: str
    format: str
    size_bytes: int
    content_hash: str
    row_count: int
    columns: Optional[List[str]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status: str
    is_ingested: bool
    ingested_at: Optional[datetime] = None
    file_exists: bool = Field(..., description="Whether the file exists on disk")
    created_at: datetime
    updated_at: Optional[datetime] = None


class StatementFileSummary(BaseModel):
    """Schema for statement file summary (abbreviated for list)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: int
    account_name: Optional[str] = None  # Will be populated from join
    original_filename: str
    size_bytes: int
    row_count: int
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status: str
    is_ingested: bool
    ingested_at: Optional[datetime] = None
    file_exists: bool = Field(..., description="Whether the file exists on disk")
    created_at: datetime


class DuplicateStatementFileResponse(BaseModel):
    """Schema for duplicate statement file error response."""

    detail: str
    existing_statement_id: uuid.UUID
    existing_created_at: datetime


class DateFormatInferenceRequest(BaseModel):
    """Schema for date format inference request (file will be in multipart)."""

    pass


class DetectedFormat(BaseModel):
    """Schema for detected date format."""

    strptime_format: str = Field(..., description="Python strptime format string")
    human_readable: str = Field(..., description="Human-readable format name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    matches: int = Field(..., description="Number of dates that match this format")
    total_tested: int = Field(..., description="Total number of dates tested")


class DateFormatInferenceResponse(BaseModel):
    """Schema for date format inference response."""

    date_column_detected: bool
    date_column_name: Optional[str] = None
    date_column_index: Optional[int] = None
    inferred_format: Optional[DetectedFormat] = None
    date_range: Optional[dict[str, date]] = None
    total_rows_analyzed: int
    parsing_errors: int
    sample_dates: List[str] = Field(default_factory=list)


class DateFormatOption(BaseModel):
    """Schema for supported date format option."""

    format: str = Field(..., description="Human-readable format name")
    pattern: str = Field(..., description="Python strptime pattern")
    description: str = Field(..., description="Format description")
    example: str = Field(..., description="Example date in this format")


class SupportedDateFormatsResponse(BaseModel):
    """Schema for supported date formats response."""

    supported_formats: List[DateFormatOption]
