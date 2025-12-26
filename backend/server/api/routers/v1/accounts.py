"""Accounts CRUD endpoints."""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from server.api.routers.v1.error_handlers import handle_service_errors
from server.api.schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
)
from server.core.database import get_db
from server.services.account import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("", response_model=List[AccountResponse])
@handle_service_errors
def list_accounts(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[AccountResponse]:
    """List all accounts with pagination."""
    service = AccountService(db)
    return service.list_accounts(skip=skip, limit=limit)


@router.get("/{account_id}", response_model=AccountResponse)
@handle_service_errors
def get_account(account_id: int, db: Session = Depends(get_db)) -> AccountResponse:
    """Get account details by ID."""
    service = AccountService(db)
    return service.get_account(account_id)


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
@handle_service_errors
def create_account(
    account_data: AccountCreate, db: Session = Depends(get_db)
) -> AccountResponse:
    """Create a new account."""
    service = AccountService(db)
    return service.create_account(account_data)


@router.put("/{account_id}", response_model=AccountResponse)
@handle_service_errors
def update_account(
    account_id: int, account_data: AccountUpdate, db: Session = Depends(get_db)
) -> AccountResponse:
    """Update an existing account."""
    service = AccountService(db)
    return service.update_account(account_id, account_data)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_service_errors
def delete_account(account_id: int, db: Session = Depends(get_db)) -> None:
    """Delete an account."""
    service = AccountService(db)
    service.delete_account(account_id)
