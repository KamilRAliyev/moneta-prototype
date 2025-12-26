"""Statement file endpoints."""

import uuid
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload

from server.api.routers.v1.error_handlers import handle_service_errors
from server.api.schemas.statement_file import (
    StatementFileResponse,
    StatementFileSummary,
)
from server.core.database import get_db
from server.core.logging import get_logger
from server.models.account import Account
from server.services.account import AccountNotFoundError
from server.services.statement_file import (
    DuplicateStatementFileError,
    StatementFileService,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/statements", tags=["Statements"])


@router.post(
    "", response_model=StatementFileResponse, status_code=status.HTTP_201_CREATED
)
@handle_service_errors
async def upload_statement(
    file: UploadFile = File(...),
    account_id: int = Query(..., description="Account ID"),
    db: Session = Depends(get_db),
) -> StatementFileResponse:
    """Upload a CSV statement file for an account.

    Args:
        file: CSV file to upload
        account_id: Account ID this statement belongs to
        db: Database session

    Returns:
        Created statement file with metadata

    Raises:
        400: Invalid account_id or file
        404: Account not found
        409: Duplicate file (same account_id + content_hash)
        422: File validation failed
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be a CSV file",
        )

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read file content",
        ) from e

    # Validate file size (50MB limit)
    max_size = 50 * 1024 * 1024  # 50MB
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File size exceeds maximum allowed size of {max_size} bytes",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File cannot be empty",
        )

    # Create statement file
    service = StatementFileService(db)
    try:
        statement = service.create_statement_file(
            account_id=account_id,
            original_filename=file.filename or "unknown.csv",
            file_content=content,
        )

        # Get account name for response
        account = db.query(Account).filter(Account.id == account_id).first()
        account_name = account.name if account else None

        # File should exist since we just created it
        file_exists = service._check_file_exists(statement.stored_path)

        return StatementFileResponse(
            id=statement.id,
            account_id=statement.account_id,
            account_name=account_name,
            original_filename=statement.original_filename,
            stored_filename=statement.stored_filename,
            stored_path=statement.stored_path,
            format=statement.format.value,
            size_bytes=statement.size_bytes,
            content_hash=statement.content_hash,
            row_count=statement.row_count,
            columns=statement.columns,
            date_from=statement.date_from,
            date_to=statement.date_to,
            status=statement.status.value,
            is_ingested=statement.is_ingested,
            ingested_at=statement.ingested_at,
            file_exists=file_exists,
            created_at=statement.created_at,
            updated_at=statement.updated_at,
        )
    except AccountNotFoundError as e:
        # Account not found - return 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DuplicateStatementFileError as e:
        # Return 409 with duplicate info (bypass response model)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(e),
                "existing_statement_id": str(e.existing_statement_id),
                "existing_created_at": e.existing_created_at.isoformat(),
            },
        )


@router.get("", response_model=List[StatementFileSummary])
@handle_service_errors
def list_statements(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db),
) -> List[StatementFileSummary]:
    """List statement files with optional filtering by account.

    Args:
        account_id: Optional account ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of statement file summaries
    """
    service = StatementFileService(db)
    statements = service.list_statement_files(
        account_id=account_id, skip=skip, limit=limit
    )

    # Enrich with account names
    # Collect all account IDs and load them in one query
    account_ids = {stmt.account_id for stmt in statements}
    accounts = {
        acc.id: acc
        for acc in db.query(Account).filter(Account.id.in_(account_ids)).all()
    }

    result = []
    for stmt in statements:
        # Get account name from pre-loaded accounts
        account = accounts.get(stmt.account_id)
        account_name = account.name if account else None

        # Check if file exists on disk
        file_exists = service._check_file_exists(stmt.stored_path)

        summary = StatementFileSummary(
            id=stmt.id,
            account_id=stmt.account_id,
            account_name=account_name,
            original_filename=stmt.original_filename,
            size_bytes=stmt.size_bytes,
            row_count=stmt.row_count,
            date_from=stmt.date_from,
            date_to=stmt.date_to,
            status=stmt.status.value,
            is_ingested=stmt.is_ingested,
            ingested_at=stmt.ingested_at,
            file_exists=file_exists,
            created_at=stmt.created_at,
        )
        result.append(summary)

    return result


@router.get("/{statement_id}", response_model=StatementFileResponse)
@handle_service_errors
def get_statement(
    statement_id: uuid.UUID, db: Session = Depends(get_db)
) -> StatementFileResponse:
    """Get statement file details by ID.

    Args:
        statement_id: Statement file ID (UUID)
        db: Database session

    Returns:
        Statement file details

    Raises:
        404: Statement file not found
    """
    service = StatementFileService(db)
    statement = service.get_statement_file(statement_id)

    # Get account name - use account_id directly to avoid DetachedInstanceError
    account_id = statement.account_id
    account = db.query(Account).filter(Account.id == account_id).first()
    account_name = account.name if account else None

    # Check if file exists on disk
    file_exists = service._check_file_exists(statement.stored_path)

    return StatementFileResponse(
        id=statement.id,
        account_id=statement.account_id,
        original_filename=statement.original_filename,
        stored_filename=statement.stored_filename,
        stored_path=statement.stored_path,
        format=statement.format.value,
        size_bytes=statement.size_bytes,
        content_hash=statement.content_hash,
        row_count=statement.row_count,
        columns=statement.columns,
        date_from=statement.date_from,
        date_to=statement.date_to,
        status=statement.status.value,
        is_ingested=statement.is_ingested,
        ingested_at=statement.ingested_at,
        file_exists=file_exists,
        created_at=statement.created_at,
        updated_at=statement.updated_at,
    )


@router.delete("/{statement_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_service_errors
def delete_statement(statement_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    """Delete a statement file.

    Args:
        statement_id: Statement file ID (UUID)
        db: Database session

    Raises:
        404: Statement file not found
    """
    service = StatementFileService(db)
    service.delete_statement_file(statement_id)
