"""Meta endpoints for static option data."""

import csv
from datetime import datetime
from typing import List

import dateinfer
from dateutil import parser as date_parser
from fastapi import APIRouter, File, HTTPException, UploadFile

from server.api.schemas.account import MetaOptionsResponse
from server.api.schemas.statement_file import (
    DateFormatInferenceResponse,
    DateFormatOption,
    DetectedFormat,
    SupportedDateFormatsResponse,
)
from server.core.logging import get_logger
from server.services.meta import MetaService

logger = get_logger(__name__)

router = APIRouter(prefix="/meta", tags=["Meta"])


@router.get("/accounts/options", response_model=MetaOptionsResponse)
def get_accounts_options() -> MetaOptionsResponse:
    """Get all static option data for Accounts UI.

    Returns account types, economic areas, and currencies.
    UI must not hardcode these values.
    """
    service = MetaService()
    return service.get_accounts_options()


@router.post(
    "/statements/infer-date-format",
    response_model=DateFormatInferenceResponse,
)
async def infer_date_format(
    file: UploadFile = File(...),
) -> DateFormatInferenceResponse:
    """Analyze a CSV file to detect date column and infer date format.

    Args:
        file: CSV file to analyze

    Returns:
        Date format inference results

    Raises:
        400: Invalid file or not a CSV
        422: File is empty or unparseable
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV file",
        )

    # Read file content
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
    except Exception as e:
        logger.error(f"Error reading file for date inference: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Failed to read file content",
        ) from e

    if len(content) == 0:
        raise HTTPException(
            status_code=422,
            detail="File cannot be empty",
        )

    # Parse CSV
    try:
        reader = csv.reader(text_content.splitlines())
        header = next(reader)
    except StopIteration:
        raise HTTPException(
            status_code=422,
            detail="File is empty or unparseable",
        )

    # Find date column
    date_column_names = [
        "Date",
        "Transaction Date",
        "Posted Date",
        "date",
        "transaction_date",
    ]
    date_column_index = None
    date_column_name = None

    for idx, col_name in enumerate(header):
        if col_name in date_column_names:
            date_column_index = idx
            date_column_name = col_name
            break

    if date_column_index is None:
        return DateFormatInferenceResponse(
            date_column_detected=False,
            date_column_name=None,
            date_column_index=None,
            inferred_format=None,
            date_range=None,
            total_rows_analyzed=0,
            parsing_errors=0,
            sample_dates=[],
        )

    # Collect date values (first 100 rows)
    date_values = []
    total_rows = 0
    parsing_errors = 0

    for row in reader:
        total_rows += 1
        if total_rows > 100:  # Limit to first 100 rows
            break
        if len(row) > date_column_index:
            date_value = row[date_column_index].strip()
            if date_value:
                date_values.append(date_value)

    if not date_values:
        return DateFormatInferenceResponse(
            date_column_detected=True,
            date_column_name=date_column_name,
            date_column_index=date_column_index,
            inferred_format=None,
            date_range=None,
            total_rows_analyzed=total_rows,
            parsing_errors=0,
            sample_dates=[],
        )

    # Infer date format
    try:
        inferred_format_str = dateinfer.infer(date_values)
    except Exception as e:
        logger.warning(f"dateinfer failed: {e}", exc_info=True)
        inferred_format_str = None

    # Test format and parse dates
    parsed_dates = []
    matches = 0

    if inferred_format_str:
        for date_str in date_values:
            try:
                # Try strptime first with inferred format
                parsed_date = datetime.strptime(date_str, inferred_format_str).date()
                parsed_dates.append(parsed_date)
                matches += 1
            except (ValueError, TypeError):
                # Fallback to dateutil parser
                try:
                    parsed_date = date_parser.parse(date_str).date()
                    parsed_dates.append(parsed_date)
                except (ValueError, TypeError):
                    parsing_errors += 1

    # Calculate confidence
    total_tested = len(date_values)
    confidence = matches / total_tested if total_tested > 0 else 0.0

    # Convert strptime format to human-readable
    format_map = {
        "%Y-%m-%d": "YYYY-MM-DD",
        "%m/%d/%Y": "MM/DD/YYYY",
        "%d/%m/%Y": "DD/MM/YYYY",
        "%d-%m-%Y": "DD-MM-YYYY",
        "%Y/%m/%d": "YYYY/MM/DD",
    }
    human_readable = format_map.get(
        inferred_format_str, inferred_format_str or "Unknown"
    )

    # Get date range
    date_range = None
    if parsed_dates:
        date_range = {
            "earliest": min(parsed_dates),
            "latest": max(parsed_dates),
        }

    inferred_format = None
    if inferred_format_str:
        inferred_format = DetectedFormat(
            strptime_format=inferred_format_str,
            human_readable=human_readable,
            confidence=confidence,
            matches=matches,
            total_tested=total_tested,
        )

    return DateFormatInferenceResponse(
        date_column_detected=True,
        date_column_name=date_column_name,
        date_column_index=date_column_index,
        inferred_format=inferred_format,
        date_range=date_range,
        total_rows_analyzed=total_rows,
        parsing_errors=parsing_errors,
        sample_dates=date_values[:10],  # First 10 samples
    )


@router.get(
    "/statements/date-formats",
    response_model=SupportedDateFormatsResponse,
)
def get_supported_date_formats() -> SupportedDateFormatsResponse:
    """Get list of all date formats supported by the system.

    Returns:
        List of supported date formats with examples
    """
    formats = [
        {
            "format": "YYYY-MM-DD",
            "pattern": "%Y-%m-%d",
            "description": "ISO 8601 format (e.g., 2024-01-15)",
            "example": "2024-01-15",
        },
        {
            "format": "MM/DD/YYYY",
            "pattern": "%m/%d/%Y",
            "description": "US format (e.g., 01/15/2024)",
            "example": "01/15/2024",
        },
        {
            "format": "DD/MM/YYYY",
            "pattern": "%d/%m/%Y",
            "description": "European format (e.g., 15/01/2024)",
            "example": "15/01/2024",
        },
        {
            "format": "DD-MM-YYYY",
            "pattern": "%d-%m-%Y",
            "description": "European format with dashes (e.g., 15-01-2024)",
            "example": "15-01-2024",
        },
        {
            "format": "YYYY/MM/DD",
            "pattern": "%Y/%m/%d",
            "description": "ISO-like with slashes (e.g., 2024/01/15)",
            "example": "2024/01/15",
        },
    ]

    return SupportedDateFormatsResponse(
        supported_formats=[DateFormatOption(**fmt) for fmt in formats]
    )
