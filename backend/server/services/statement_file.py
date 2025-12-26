"""Statement file service with business logic."""

import csv
import hashlib
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional, Tuple

import dateinfer
from dateutil import parser as date_parser
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from server.core.logging import get_logger
from server.models.account import Account
from server.models.statement_file import (
    StatementFile,
    StatementFormat,
    StatementStatus,
)
from server.services import data_dir
from server.services.account import AccountNotFoundError
from server.services.exceptions import DatabaseError, NotFoundError, ValidationError

logger = get_logger(__name__)


class StatementFileNotFoundError(NotFoundError):
    """Raised when statement file is not found."""

    pass


class DuplicateStatementFileError(ValidationError):
    """Raised when a duplicate statement file is detected."""

    def __init__(
        self,
        message: str,
        existing_statement_id: uuid.UUID,
        existing_created_at: datetime,
    ):
        """Initialize duplicate error with existing statement info."""
        super().__init__(message)
        self.existing_statement_id = existing_statement_id
        self.existing_created_at = existing_created_at


class StatementFileService:
    """Service for statement file business logic."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db

    def _compute_content_hash(self, content: bytes) -> str:
        """Compute SHA-256 hash of file content.

        Args:
            content: File content as bytes

        Returns:
            Hex string of SHA-256 hash (64 characters)
        """
        return hashlib.sha256(content).hexdigest()

    def _check_file_exists(self, stored_path: str) -> bool:
        """Check if statement file exists on disk.

        Args:
            stored_path: Path to the statement file

        Returns:
            True if file exists, False otherwise
        """
        try:
            file_path = Path(stored_path)
            return file_path.exists() and file_path.is_file()
        except Exception:
            return False

    def _extract_csv_metadata(
        self, content: bytes
    ) -> Tuple[int, Optional[List[str]], Optional[date], Optional[date]]:
        """Extract metadata from CSV content.

        Args:
            content: CSV file content as bytes

        Returns:
            Tuple of (row_count, columns, date_from, date_to)
        """
        try:
            # Decode content
            text_content = content.decode("utf-8")
            reader = csv.reader(text_content.splitlines())

            # Read header
            try:
                header = next(reader)
                columns = header if header else None
            except StopIteration:
                # Empty file
                return 0, None, None, None

            # Count rows and find date column
            row_count = 0
            date_column_index = None
            date_values = []

            # Try to find date column by name
            date_column_names = [
                "Date",
                "Transaction Date",
                "Posted Date",
                "date",
                "transaction_date",
            ]
            for idx, col_name in enumerate(header):
                if col_name in date_column_names:
                    date_column_index = idx
                    break

            # Read data rows
            for row in reader:
                if not row:  # Skip empty rows
                    continue
                row_count += 1

                # Collect date values if date column found
                if date_column_index is not None and len(row) > date_column_index:
                    date_value = row[date_column_index].strip()
                    if date_value:
                        date_values.append(date_value)

            # Try to infer date format and parse dates
            date_from = None
            date_to = None

            if date_values:
                try:
                    # Use dateinfer to infer format
                    inferred_format = dateinfer.infer(
                        date_values[:100]
                    )  # Use first 100 samples
                    # Parse dates using inferred format
                    parsed_dates = []
                    for date_str in date_values:
                        try:
                            # Try strptime first
                            parsed_date = datetime.strptime(
                                date_str, inferred_format
                            ).date()
                            parsed_dates.append(parsed_date)
                        except (ValueError, TypeError):
                            # Fallback to dateutil parser
                            try:
                                parsed_date = date_parser.parse(date_str).date()
                                parsed_dates.append(parsed_date)
                            except (ValueError, TypeError):
                                continue

                    if parsed_dates:
                        date_from = min(parsed_dates)
                        date_to = max(parsed_dates)
                except Exception as e:
                    logger.warning(
                        f"Failed to extract date range from CSV: {e}",
                        exc_info=True,
                    )

            return row_count, columns, date_from, date_to

        except Exception as e:
            logger.warning(
                f"Failed to extract CSV metadata: {e}",
                exc_info=True,
            )
            # Return defaults on failure
            return 0, None, None, None

    def _check_duplicate(
        self, account_id: int, content_hash: str
    ) -> Optional[StatementFile]:
        """Check if a statement file with same account_id and content_hash exists.

        Args:
            account_id: Account ID
            content_hash: SHA-256 hash of file content

        Returns:
            Existing StatementFile if duplicate found, None otherwise
        """
        return (
            self.db.query(StatementFile)
            .filter(
                StatementFile.account_id == account_id,
                StatementFile.content_hash == content_hash,
            )
            .first()
        )

    def get_statement_file(self, statement_id: uuid.UUID) -> StatementFile:
        """Get statement file by ID."""
        try:
            statement = (
                self.db.query(StatementFile)
                .filter(StatementFile.id == statement_id)
                .first()
            )
            if not statement:
                raise StatementFileNotFoundError(
                    f"Statement file with ID {statement_id} not found"
                )
            return statement
        except SQLAlchemyError as e:
            logger.error(
                f"Database error getting statement file {statement_id}",
                exc_info=True,
                extra={"statement_id": str(statement_id)},
            )
            self.db.rollback()
            raise DatabaseError("Failed to retrieve statement file") from e

    def list_statement_files(
        self, account_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[StatementFile]:
        """List statement files with optional filtering by account.

        Args:
            account_id: Optional account ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of StatementFile objects
        """
        try:
            query = self.db.query(StatementFile)

            if account_id is not None:
                query = query.filter(StatementFile.account_id == account_id)

            # Order by created_at DESC (newest first)
            query = query.order_by(StatementFile.created_at.desc())

            statements = query.offset(skip).limit(limit).all()
            return statements
        except SQLAlchemyError as e:
            logger.error("Database error listing statement files", exc_info=True)
            self.db.rollback()
            raise DatabaseError("Failed to list statement files") from e

    def create_statement_file(
        self,
        account_id: int,
        original_filename: str,
        file_content: bytes,
    ) -> StatementFile:
        """Create a new statement file with atomic file + DB operations.

        Args:
            account_id: Account ID this statement belongs to
            original_filename: Original uploaded filename
            file_content: File content as bytes

        Returns:
            Created StatementFile object

        Raises:
            AccountNotFoundError: If account doesn't exist
            DuplicateStatementFileError: If duplicate file detected
            DatabaseError: If database operation fails
        """
        # Verify account exists
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise AccountNotFoundError(f"Account with ID {account_id} not found")

        # Compute content hash
        content_hash = self._compute_content_hash(file_content)

        # Check for duplicate
        existing = self._check_duplicate(account_id, content_hash)
        if existing:
            raise DuplicateStatementFileError(
                f"Statement file already exists for account {account_id}",
                existing.id,
                existing.created_at,
            )

        # Generate UUID and file paths
        statement_id = uuid.uuid4()
        statements_dir = data_dir.ensure_statements_dir()
        stored_filename = f"{statement_id}.csv"
        stored_path = statements_dir / stored_filename

        # Extract CSV metadata
        row_count, columns, date_from, date_to = self._extract_csv_metadata(
            file_content
        )

        # Create statement file record
        statement_file = StatementFile(
            id=statement_id,
            account_id=account_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            stored_path=str(stored_path),
            format=StatementFormat.CSV,
            size_bytes=len(file_content),
            content_hash=content_hash,
            row_count=row_count,
            columns=columns,
            date_from=date_from,
            date_to=date_to,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )

        try:
            # Atomic operation: write file first, then DB
            # If DB fails, we'll delete the file
            stored_path.write_bytes(file_content)

            self.db.add(statement_file)
            self.db.commit()
            self.db.refresh(statement_file)

            logger.info(
                f"Statement file created: {statement_id}",
                extra={
                    "statement_id": str(statement_id),
                    "account_id": account_id,
                    "original_filename": original_filename,
                    "size_bytes": len(file_content),
                },
            )

            return statement_file

        except IntegrityError as e:
            # DB constraint violation - delete file if it was written
            if stored_path.exists():
                try:
                    stored_path.unlink()
                except Exception as cleanup_error:
                    logger.error(
                        f"Failed to cleanup file after DB error: {cleanup_error}",
                        exc_info=True,
                    )

            logger.error(
                "Database integrity error creating statement file",
                exc_info=True,
                extra={
                    "account_id": account_id,
                    "original_filename": original_filename,
                },
            )
            self.db.rollback()
            raise DatabaseError(
                "Failed to create statement file: duplicate or constraint violation"
            ) from e

        except Exception as e:
            # Any other error - try to cleanup file
            if stored_path.exists():
                try:
                    stored_path.unlink()
                except Exception as cleanup_error:
                    logger.error(
                        f"Failed to cleanup file after error: {cleanup_error}",
                        exc_info=True,
                    )

            logger.error(
                "Error creating statement file",
                exc_info=True,
                extra={
                    "account_id": account_id,
                    "original_filename": original_filename,
                },
            )
            self.db.rollback()
            raise DatabaseError("Failed to create statement file") from e

    def delete_statement_file(self, statement_id: uuid.UUID) -> None:
        """Delete a statement file (atomic: delete file + DB record).

        Args:
            statement_id: Statement file ID

        Raises:
            StatementFileNotFoundError: If statement file not found
            DatabaseError: If database operation fails
        """
        try:
            statement = self.get_statement_file(statement_id)
            file_path = Path(statement.stored_path)

            # Delete DB record first
            self.db.delete(statement)
            self.db.commit()

            # Then delete file
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.warning(
                        f"Failed to delete file {file_path}: {e}",
                        exc_info=True,
                        extra={
                            "statement_id": str(statement_id),
                            "file_path": str(file_path),
                        },
                    )

            logger.info(
                f"Statement file deleted: {statement_id}",
                extra={"statement_id": str(statement_id)},
            )

        except SQLAlchemyError as e:
            logger.error(
                f"Database error deleting statement file {statement_id}",
                exc_info=True,
                extra={"statement_id": str(statement_id)},
            )
            self.db.rollback()
            raise DatabaseError("Failed to delete statement file") from e
