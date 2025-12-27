"""Transaction endpoints."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from server.api.routers.v1.error_handlers import handle_service_errors
from server.api.schemas.transaction import (
    IngestionResponse,
    TransactionListResponse,
    TransactionMetaResponse,
    TransactionResponse,
)
from server.core.database import get_db
from server.models.account import Account
from server.models.statement_file import StatementFile
from server.models.transaction import Transaction
from server.services.transaction import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
@handle_service_errors
def list_transactions(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    statement_file_id: Optional[uuid.UUID] = Query(
        None, description="Filter by statement file ID"
    ),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(
        "inserted_at",
        description="Field to sort by (inserted_at, row_id, statement_file_id, or ingested_content.<field>)",
    ),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    filters: Optional[str] = Query(
        None,
        description="Filter string (format: field1:operator:value,field2:operator:value)",
    ),
    db: Session = Depends(get_db),
) -> TransactionListResponse:
    """List transactions with pagination, sorting, and filtering.

    Args:
        account_id: Optional account ID filter
        statement_file_id: Optional statement file ID filter
        page: Page number (1-based)
        page_size: Items per page (max 100)
        sort_by: Field to sort by
        sort_dir: Sort direction (asc or desc)
        filters: Filter string

    Returns:
        TransactionListResponse with transactions and pagination info
    """
    service = TransactionService(db)

    # Get column types from metadata for type-aware sorting
    column_types = {}
    if sort_by.startswith("ingested_content."):
        try:
            meta = service.get_transaction_meta(account_id=account_id)
            for col in meta.get("ingested_columns", []):
                column_types[col["name"]] = col.get("type", "string")
        except Exception:
            pass  # Continue without column types if meta fetch fails

    transactions, total_count = service.list_transactions(
        account_id=account_id,
        statement_file_id=statement_file_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_dir=sort_dir,
        filters=filters,
        column_types=column_types,
    )

    # Load related data (account and statement_file) for each transaction
    # Collect all account IDs and statement file IDs to load in bulk
    account_ids = {tx.account_id for tx in transactions}
    statement_file_ids = {tx.statement_file_id for tx in transactions}

    # Load accounts in bulk (only if there are transactions)
    accounts = {}
    if account_ids:
        accounts = {
            acc.id: acc
            for acc in db.query(Account).filter(Account.id.in_(account_ids)).all()
        }

    # Load statement files in bulk (only if there are transactions)
    statement_files = {}
    if statement_file_ids:
        statement_files = {
            stmt.id: stmt
            for stmt in db.query(StatementFile)
            .filter(StatementFile.id.in_(statement_file_ids))
            .all()
        }

    # Build response with related data
    from server.api.schemas.transaction import StatementFileSummary, AccountSummary

    transaction_responses = []
    for tx in transactions:
        account = accounts.get(tx.account_id)
        statement_file = statement_files.get(tx.statement_file_id)

        transaction_responses.append(
            TransactionResponse(
                id=tx.id,
                row_id=tx.row_id,
                statement_file=StatementFileSummary(
                    id=statement_file.id if statement_file else tx.statement_file_id,
                    original_filename=(
                        statement_file.original_filename if statement_file else ""
                    ),
                    columns=statement_file.columns if statement_file else None,
                ),
                account=AccountSummary(
                    id=account.id if account else tx.account_id,
                    name=account.name if account else "Unknown Account",
                    institution=account.institution if account else "Unknown",
                    currency=(
                        account.currency.value
                        if account and hasattr(account, "currency") and account.currency
                        else "USD"
                    ),
                    type=(
                        account.type.value
                        if account and hasattr(account, "type") and account.type
                        else "checking"
                    ),
                    economic_area=(
                        account.economic_area.value
                        if account
                        and hasattr(account, "economic_area")
                        and account.economic_area
                        else None
                    ),
                    datelock_from=account.datelock_from if account else None,
                    datelock_to=account.datelock_to if account else None,
                ),
                ingested_content=tx.ingested_content,
                computed_content=tx.computed_content if tx.computed_content else {},
                inserted_at=tx.inserted_at,
            )
        )

    # Calculate total pages
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0

    from server.api.schemas.transaction import TransactionListMeta

    return TransactionListResponse(
        items=transaction_responses,
        meta=TransactionListMeta(
            page=page,
            page_size=page_size,
            total=total_count,
            total_pages=total_pages,
        ),
    )


@router.get("/meta", response_model=TransactionMetaResponse)
@handle_service_errors
def get_transaction_meta(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    db: Session = Depends(get_db),
) -> TransactionMetaResponse:
    """Get transaction column metadata.

    Args:
        account_id: Optional account ID to filter by

    Returns:
        TransactionMetaResponse with column metadata
    """
    from server.api.schemas.transaction import ColumnMetadata

    service = TransactionService(db)
    meta = service.get_transaction_meta(account_id=account_id)

    # Convert to ColumnMetadata format
    ingested_columns = [
        ColumnMetadata(
            name=col["name"],
            type=col["type"],
            sample_values=col.get("sample_values", [])[:10],
            nullable=col.get("nullable", True),
            min=col.get("min"),
            max=col.get("max"),
        )
        for col in meta.get("ingested_columns", [])
    ]

    return TransactionMetaResponse(
        ingested_columns=ingested_columns,
        computed_columns=[],
    )


@router.delete("", status_code=status.HTTP_200_OK)
@handle_service_errors
def delete_transactions(
    account_id: Optional[int] = Query(
        None,
        description="Delete transactions for specific account (required if not all)",
    ),
    db: Session = Depends(get_db),
) -> dict:
    """Delete transactions.

    Args:
        account_id: Optional account ID to filter by. If not provided, deletes all transactions.

    Returns:
        Dictionary with deleted count
    """
    service = TransactionService(db)
    deleted_count = service.delete_transactions(account_id=account_id)
    return {"deleted_count": deleted_count}
