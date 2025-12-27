"""Account service with business logic."""

from typing import List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from server.api.schemas.account import AccountCreate, AccountUpdate
from server.core.logging import get_logger
from server.models.account import Account, AccountType, Currency, EconomicArea
from server.services.exceptions import DatabaseError, NotFoundError, ValidationError

logger = get_logger(__name__)


class AccountNotFoundError(NotFoundError):
    """Raised when account is not found."""

    pass


class InvalidCurrencyError(ValidationError):
    """Raised when currency code is invalid."""

    pass


class InvalidAccountTypeError(ValidationError):
    """Raised when account type is invalid."""

    pass


class InvalidEconomicAreaError(ValidationError):
    """Raised when economic area is invalid."""

    pass


class AccountService:
    """Service for account business logic."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db

    def validate_currency(self, currency_code: str) -> Currency:
        """Validate and return Currency enum."""
        try:
            return Currency(currency_code.upper())
        except ValueError:
            raise InvalidCurrencyError(f"Invalid currency code: {currency_code}")

    def validate_account_type(self, account_type: str) -> AccountType:
        """Validate and return AccountType enum."""
        try:
            return AccountType(account_type)
        except ValueError:
            raise InvalidAccountTypeError(f"Invalid account type: {account_type}")

    def validate_economic_area(
        self, economic_area: Optional[str]
    ) -> Optional[EconomicArea]:
        """Validate and return EconomicArea enum or None."""
        if not economic_area:
            return None
        try:
            return EconomicArea(economic_area)
        except ValueError:
            raise InvalidEconomicAreaError(f"Invalid economic area: {economic_area}")

    def get_account(self, account_id: int) -> Account:
        """Get account by ID."""
        try:
            account = self.db.query(Account).filter(Account.id == account_id).first()
            if not account:
                raise AccountNotFoundError(f"Account with ID {account_id} not found")
            return account
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting account {account_id}",
                exc_info=True,
                extra={"account_id": account_id},
            )
            self.db.rollback()
            raise DatabaseError("Failed to retrieve account") from e

    def list_accounts(self, skip: int = 0, limit: int = 100) -> List[Account]:
        """List all accounts with pagination."""
        try:
            accounts = self.db.query(Account).offset(skip).limit(limit).all()
            return accounts
        except SQLAlchemyError as e:
            logger.error("Database error listing accounts", exc_info=True)
            self.db.rollback()
            raise DatabaseError("Failed to list accounts") from e

    def create_account(self, account_data: AccountCreate) -> Account:
        """Create a new account."""
        try:
            # Validate enums
            currency_enum = self.validate_currency(account_data.currency)
            account_type_enum = self.validate_account_type(account_data.account_type)
            economic_area_enum = self.validate_economic_area(account_data.economic_area)

            # Create account
            account = Account(
                name=account_data.name,
                institution=account_data.institution,
                currency=currency_enum,
                type=account_type_enum,
                economic_area=economic_area_enum,
                datelock_from=account_data.datelock_from,
                datelock_to=account_data.datelock_to,
            )

            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)

            logger.info(
                f"Account created: {account.id}", extra={"account_id": account.id}
            )
            return account
        except IntegrityError as e:
            logger.error(
                "Database integrity error creating account",
                exc_info=True,
                extra={"account_data": account_data.model_dump()},
            )
            self.db.rollback()
            raise DatabaseError(
                "Failed to create account: duplicate or constraint violation"
            ) from e
        except SQLAlchemyError as e:
            logger.error(
                "Database error creating account",
                exc_info=True,
                extra={"account_data": account_data.model_dump()},
            )
            self.db.rollback()
            raise DatabaseError("Failed to create account") from e

    def update_account(self, account_id: int, account_data: AccountUpdate) -> Account:
        """Update an existing account."""
        try:
            account = self.get_account(account_id)

            # Update fields if provided
            if account_data.name is not None:
                account.name = account_data.name
            if account_data.institution is not None:
                account.institution = account_data.institution
            if account_data.currency is not None:
                account.currency = self.validate_currency(account_data.currency)
            if account_data.account_type is not None:
                account.type = self.validate_account_type(account_data.account_type)
            if account_data.economic_area is not None:
                if account_data.economic_area == "":
                    account.economic_area = None
                else:
                    account.economic_area = self.validate_economic_area(
                        account_data.economic_area
                    )
            if account_data.datelock_from is not None:
                account.datelock_from = account_data.datelock_from
            if account_data.datelock_to is not None:
                account.datelock_to = account_data.datelock_to

            self.db.commit()
            self.db.refresh(account)

            logger.info(
                f"Account updated: {account.id}", extra={"account_id": account.id}
            )
            return account
        except IntegrityError as e:
            logger.error(
                "Database integrity error updating account",
                exc_info=True,
                extra={"account_id": account_id},
            )
            self.db.rollback()
            raise DatabaseError("Failed to update account: constraint violation") from e
        except SQLAlchemyError as e:
            logger.error(
                "Database error updating account",
                exc_info=True,
                extra={"account_id": account_id},
            )
            self.db.rollback()
            raise DatabaseError("Failed to update account") from e

    def delete_account(self, account_id: int) -> None:
        """Delete an account."""
        try:
            account = self.get_account(account_id)

            self.db.delete(account)
            self.db.commit()

            logger.info(
                f"Account deleted: {account.id}", extra={"account_id": account.id}
            )
        except SQLAlchemyError as e:
            logger.error(
                "Database error deleting account",
                exc_info=True,
                extra={"account_id": account_id},
            )
            self.db.rollback()
            raise DatabaseError("Failed to delete account") from e
