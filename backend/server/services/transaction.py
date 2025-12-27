"""Transaction service with business logic."""

import csv
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import dateinfer
from dateutil import parser as date_parser
import sqlalchemy as sa
from sqlalchemy import Numeric, and_, cast, func, or_, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from server.core.logging import get_logger
from server.models.account import Account
from server.models.statement_file import StatementFile
from server.models.transaction import Transaction
from server.services import data_dir
from server.services.exceptions import DatabaseError, NotFoundError
from server.utils.hash import calculate_transaction_hash

logger = get_logger(__name__)


class TransactionNotFoundError(NotFoundError):
    """Raised when transaction is not found."""

    pass


class TransactionService:
    """Service for transaction business logic."""

    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db

    def _should_skip_transaction(
        self, transaction_date: date, account: Account
    ) -> bool:
        """Check if transaction should be skipped based on date lock.

        Returns True if transaction is within locked range (already ingested).
        """
        # No lock - ingest everything
        if account.datelock_from is None and account.datelock_to is None:
            return False

        # Check if within locked range
        within_from = (
            account.datelock_from is None or transaction_date >= account.datelock_from
        )
        within_to = (
            account.datelock_to is None or transaction_date <= account.datelock_to
        )

        # If both conditions met, transaction is within locked range
        return within_from and within_to

    def _parse_date(
        self, date_str: str, date_column: Optional[str], date_format: Optional[str]
    ) -> Optional[date]:
        """Parse date string using inferred format or dateutil parser.

        Args:
            date_str: Date string to parse
            date_column: Name of date column (for logging)
            date_format: Inferred date format (if available)

        Returns:
            Parsed date or None if parsing fails
        """
        if not date_str or not date_str.strip():
            return None

        # Try inferred format first
        if date_format:
            try:
                return datetime.strptime(date_str.strip(), date_format).date()
            except (ValueError, TypeError, Exception):
                # dateinfer may return invalid format strings, fallback to dateutil
                pass

        # Fallback to dateutil parser
        try:
            return date_parser.parse(date_str.strip()).date()
        except (ValueError, TypeError):
            logger.warning(
                f"Failed to parse date '{date_str}' for column '{date_column}'"
            )
            return None

    def _infer_date_format(self, date_values: List[str]) -> Optional[str]:
        """Infer date format from sample values.

        Args:
            date_values: List of date strings

        Returns:
            Inferred format string or None
        """
        if not date_values:
            return None

        try:
            # Use first 100 samples for performance
            samples = date_values[:100]
            inferred_format = dateinfer.infer(samples)
            # Validate format string by trying to parse a sample
            try:
                datetime.strptime(samples[0], inferred_format)
                return inferred_format
            except (ValueError, TypeError, Exception):
                # Invalid format string, return None to use dateutil parser
                logger.warning(f"Invalid date format inferred: {inferred_format}")
                return None
        except Exception as e:
            logger.warning(f"Failed to infer date format: {e}")
            return None

    def _read_csv_rows(
        self, statement_file: StatementFile
    ) -> List[Tuple[int, Dict[str, Any]]]:
        """Read CSV file and return rows as dictionaries.

        Args:
            statement_file: StatementFile model instance

        Returns:
            List of (row_id, row_dict) tuples (row_id is 0-based, excluding header)

        Raises:
            NotFoundError: If file doesn't exist
            DatabaseError: If file cannot be read or parsed
        """
        file_path = Path(statement_file.stored_path)
        if not file_path.exists():
            raise NotFoundError(
                f"Statement file not found at path: {file_path}. "
                f"Statement ID: {statement_file.id}"
            )

        if not file_path.is_file():
            raise DatabaseError(
                f"Path exists but is not a file: {file_path}. "
                f"Statement ID: {statement_file.id}"
            )

        rows = []
        # Try multiple encodings
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        last_error = None

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    for row_id, row in enumerate(reader):
                        # Convert to dict, removing None values and empty strings
                        row_dict = {
                            k: v for k, v in row.items() if v is not None and v.strip()
                        }
                        if row_dict:  # Only add non-empty rows
                            rows.append((row_id, row_dict))
                    # Success - return rows
                    return rows
            except UnicodeDecodeError as e:
                last_error = e
                logger.debug(
                    f"Failed to read file with encoding {encoding}: {e}. "
                    f"Trying next encoding..."
                )
                continue
            except csv.Error as e:
                raise DatabaseError(
                    f"CSV parsing error in file {file_path}: {e}. "
                    f"Statement ID: {statement_file.id}"
                ) from e
            except Exception as e:
                raise DatabaseError(
                    f"Unexpected error reading file {file_path}: {e}. "
                    f"Statement ID: {statement_file.id}"
                ) from e

        # All encodings failed
        raise DatabaseError(
            f"Failed to read file with any encoding. Last error: {last_error}. "
            f"File: {file_path}, Statement ID: {statement_file.id}"
        )

    def ingest_statement(self, statement_file_id: uuid.UUID) -> Dict[str, Any]:
        """Ingest transactions from a statement file.

        Args:
            statement_file_id: UUID of statement file to ingest

        Returns:
            Dictionary with ingestion results (status, summary, errors)

        Raises:
            NotFoundError: If statement file or account not found
            DatabaseError: If database operation fails
        """
        try:
            # Get statement file
            statement_file = (
                self.db.query(StatementFile)
                .filter(StatementFile.id == statement_file_id)
                .first()
            )
            if not statement_file:
                raise NotFoundError(f"Statement file {statement_file_id} not found")

            # Get account
            account = (
                self.db.query(Account)
                .filter(Account.id == statement_file.account_id)
                .first()
            )
            if not account:
                raise NotFoundError(
                    f"Account {statement_file.account_id} not found for statement {statement_file_id}"
                )
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Error fetching statement/account for ingestion: {e}",
                exc_info=True,
            )
            raise DatabaseError(f"Failed to fetch statement or account: {e}") from e

        # Read CSV rows
        try:
            rows = self._read_csv_rows(statement_file)
        except NotFoundError:
            # Re-raise NotFoundError as-is (will be converted to 404)
            raise
        except Exception as e:
            logger.error(
                f"Failed to read CSV file for statement {statement_file_id}: {e}",
                exc_info=True,
            )
            raise DatabaseError(f"Failed to read statement file: {e}") from e

        if not rows:
            # Empty file - mark as ingested with 0 rows
            statement_file.is_ingested = True
            statement_file.ingested_rows_count = 0
            statement_file.ingestion_errors_count = 0
            statement_file.ingested_at = datetime.now(timezone.utc)
            self.db.commit()

            return {
                "statement_id": statement_file_id,
                "status": "completed",
                "summary": {
                    "total_rows": 0,
                    "ingested": 0,
                    "skipped": 0,
                    "errors": 0,
                },
                "errors": [],
            }

        # Get date column
        date_column = statement_file.date_column
        if not date_column and statement_file.columns:
            # Try to find date column in columns
            date_column_names = [
                "Date",
                "Transaction Date",
                "Posted Date",
                "date",
                "transaction_date",
            ]
            for col in statement_file.columns:
                if col in date_column_names:
                    date_column = col
                    break

        # Collect date values for format inference
        date_values = []
        if date_column:
            for row_id, row_dict in rows:
                if date_column in row_dict:
                    date_value = row_dict[date_column]
                    if date_value:
                        date_values.append(str(date_value))

        # Infer date format
        date_format = self._infer_date_format(date_values) if date_values else None

        # Process rows
        transactions_to_insert = []
        errors = []
        skipped_count = 0
        ingested_count = 0

        for row_id, row_dict in rows:
            try:
                # Check if transaction already exists (idempotency)
                # Wrap in try-except to handle failed transaction state
                try:
                    existing = (
                        self.db.query(Transaction)
                        .filter(
                            Transaction.statement_file_id == statement_file_id,
                            Transaction.row_id == row_id,
                        )
                        .first()
                    )
                except (SQLAlchemyError, Exception) as db_err:
                    # If transaction is in failed state, rollback and retry once
                    try:
                        self.db.rollback()
                        existing = (
                            self.db.query(Transaction)
                            .filter(
                                Transaction.statement_file_id == statement_file_id,
                                Transaction.row_id == row_id,
                            )
                            .first()
                        )
                    except Exception:
                        # If retry also fails, skip this row
                        logger.warning(
                            f"Failed to check existing transaction for row {row_id}, skipping"
                        )
                        errors.append(
                            {
                                "row_id": row_id,
                                "reason": "database_error",
                                "message": f"Failed to check existing transaction: {db_err}",
                            }
                        )
                        continue

                if existing:
                    skipped_count += 1
                    continue

                # Parse transaction date if date column exists
                transaction_date = None
                if date_column and date_column in row_dict:
                    transaction_date = self._parse_date(
                        str(row_dict[date_column]), date_column, date_format
                    )

                # Apply date lock
                if transaction_date and self._should_skip_transaction(
                    transaction_date, account
                ):
                    skipped_count += 1
                    # Format date lock range for error message
                    lock_from = account.datelock_from or "unbounded"
                    lock_to = account.datelock_to or "unbounded"
                    errors.append(
                        {
                            "row_id": row_id,
                            "reason": "date_lock",
                            "message": f"Transaction date {transaction_date} is within locked range [{lock_from}, {lock_to}]",
                        }
                    )
                    continue

                # Calculate transaction hash
                transaction_hash = calculate_transaction_hash(row_id, row_dict)

                # Create transaction
                transaction = Transaction(
                    id=uuid.uuid4(),
                    account_id=account.id,
                    statement_file_id=statement_file_id,
                    row_id=row_id,
                    ingested_content=row_dict,
                    transaction_hash=transaction_hash,
                    computed_content={},
                )
                transactions_to_insert.append(transaction)
                ingested_count += 1

            except SQLAlchemyError as e:
                # Database error - rollback transaction and re-raise
                logger.error(
                    f"Database error processing row {row_id} in statement {statement_file_id}: {e}",
                    exc_info=True,
                )
                self.db.rollback()
                errors.append(
                    {
                        "row_id": row_id,
                        "reason": "database_error",
                        "message": str(e),
                    }
                )
                # Continue processing other rows
                continue
            except Exception as e:
                logger.error(
                    f"Error processing row {row_id} in statement {statement_file_id}: {e}",
                    exc_info=True,
                )
                errors.append(
                    {
                        "row_id": row_id,
                        "reason": "parse_error",
                        "message": str(e),
                    }
                )

        # Bulk insert transactions (batches of 1000)
        batch_size = 1000
        for i in range(0, len(transactions_to_insert), batch_size):
            batch = transactions_to_insert[i : i + batch_size]
            try:
                self.db.add_all(batch)
                self.db.commit()
            except IntegrityError:
                # Some transactions might already exist (race condition)
                self.db.rollback()
                # Insert one by one to handle duplicates gracefully
                for tx in batch:
                    try:
                        self.db.add(tx)
                        self.db.commit()
                    except IntegrityError:
                        self.db.rollback()
                        skipped_count += 1
                        ingested_count -= 1
            except SQLAlchemyError as e:
                logger.error(
                    f"Database error inserting transactions batch: {e}",
                    exc_info=True,
                )
                self.db.rollback()
                raise DatabaseError("Failed to insert transactions") from e

        # Update statement file
        statement_file.is_ingested = True
        statement_file.ingested_rows_count = ingested_count
        statement_file.ingestion_errors_count = len(errors)
        statement_file.ingested_at = datetime.now(timezone.utc)
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            logger.error(
                f"Database error updating statement file: {e}",
                exc_info=True,
            )
            self.db.rollback()
            raise DatabaseError("Failed to update statement file") from e

        # Determine status
        total_rows = len(rows)
        # Check if errors are only date_lock errors (expected behavior, not failures)
        date_lock_errors_only = all(err.get("reason") == "date_lock" for err in errors)

        if len(errors) == 0 and ingested_count == total_rows:
            status = "completed"
        elif (len(errors) == 0 and skipped_count == total_rows) or (
            date_lock_errors_only and skipped_count == total_rows
        ):
            # All rows skipped (idempotency or date lock) - still completed
            status = "completed"
        elif ingested_count > 0:
            status = "partial"
        else:
            status = "failed"

        return {
            "statement_id": statement_file_id,
            "status": status,
            "summary": {
                "total_rows": total_rows,
                "ingested": ingested_count,
                "skipped": skipped_count,
                "errors": len(errors),
            },
            "errors": errors,
        }

    def _parse_filters(self, filters_str: Optional[str]) -> List[Dict[str, str]]:
        """Parse filter string into list of filter dictionaries.

        Format: field1:operator:value,field2:operator:value

        Args:
            filters_str: Filter string

        Returns:
            List of filter dictionaries with keys: field, operator, value
        """
        if not filters_str:
            return []

        filters = []
        for filter_part in filters_str.split(","):
            parts = filter_part.split(":", 2)
            if len(parts) == 3:
                filters.append(
                    {"field": parts[0], "operator": parts[1], "value": parts[2]}
                )
        return filters

    def _apply_filter(self, query, filter_dict: Dict[str, str]):
        """Apply a single filter to the query.

        Args:
            query: SQLAlchemy query object
            filter_dict: Filter dictionary with field, operator, value

        Returns:
            Modified query
        """
        field = filter_dict["field"]
        operator = filter_dict["operator"]
        value = filter_dict["value"]

        # Handle regular fields
        if field == "account_id":
            if operator == "=":
                return query.filter(Transaction.account_id == int(value))
            elif operator in ("!=", "not_equal"):
                return query.filter(Transaction.account_id != int(value))
        elif field == "statement_file_id":
            if operator == "=":
                return query.filter(Transaction.statement_file_id == uuid.UUID(value))
            elif operator in ("!=", "not_equal"):
                return query.filter(Transaction.statement_file_id != uuid.UUID(value))
        elif field == "row_id":
            if operator == "=":
                return query.filter(Transaction.row_id == int(value))
            elif operator in ("!=", "not_equal"):
                return query.filter(Transaction.row_id != int(value))
            elif operator == ">":
                return query.filter(Transaction.row_id > int(value))
            elif operator == ">=":
                return query.filter(Transaction.row_id >= int(value))
            elif operator == "<":
                return query.filter(Transaction.row_id < int(value))
            elif operator == "<=":
                return query.filter(Transaction.row_id <= int(value))

        # Handle ingested_content fields (JSONB)
        elif field.startswith("ingested_content."):
            json_key = field.replace("ingested_content.", "")
            json_path = Transaction.ingested_content[json_key]

            if operator == "=":
                return query.filter(json_path.astext == value)
            elif operator in ("!=", "not_equal"):
                return query.filter(json_path.astext != value)
            elif operator == ">":
                # Try to cast to numeric for comparison
                try:
                    num_value = float(value)
                    return query.filter(cast(json_path.astext, Numeric) > num_value)
                except (ValueError, TypeError):
                    # Fallback to text comparison
                    return query.filter(json_path.astext > value)
            elif operator == ">=":
                try:
                    num_value = float(value)
                    return query.filter(cast(json_path.astext, Numeric) >= num_value)
                except (ValueError, TypeError):
                    return query.filter(json_path.astext >= value)
            elif operator == "<":
                try:
                    num_value = float(value)
                    return query.filter(cast(json_path.astext, Numeric) < num_value)
                except (ValueError, TypeError):
                    return query.filter(json_path.astext < value)
            elif operator == "<=":
                try:
                    num_value = float(value)
                    return query.filter(cast(json_path.astext, Numeric) <= num_value)
                except (ValueError, TypeError):
                    return query.filter(json_path.astext <= value)
            elif operator == "contains":
                return query.filter(json_path.astext.contains(value))
            elif operator == "empty":
                return query.filter(or_(json_path.is_(None), json_path.astext == ""))
            elif operator == "not_empty":
                return query.filter(and_(json_path.isnot(None), json_path.astext != ""))

        return query

    def list_transactions(
        self,
        account_id: Optional[int] = None,
        statement_file_id: Optional[uuid.UUID] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "inserted_at",
        sort_dir: str = "desc",
        filters: Optional[str] = None,
        column_types: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[Transaction], int]:
        """List transactions with pagination, sorting, and filtering.

        Args:
            account_id: Optional account ID filter
            statement_file_id: Optional statement file ID filter
            page: Page number (1-based)
            page_size: Items per page
            sort_by: Field to sort by
            sort_dir: Sort direction ('asc' or 'desc')
            filters: Filter string (format: field1:operator:value,field2:operator:value)

        Returns:
            Tuple of (transactions list, total count)
        """
        try:
            query = self.db.query(Transaction)

            # Apply filters
            if account_id is not None:
                query = query.filter(Transaction.account_id == account_id)
            if statement_file_id is not None:
                query = query.filter(Transaction.statement_file_id == statement_file_id)

            # Parse and apply filter string
            filter_list = self._parse_filters(filters)
            for filter_dict in filter_list:
                query = self._apply_filter(query, filter_dict)

            # Get total count before pagination
            total = query.count()

            # Apply sorting
            if sort_by == "inserted_at":
                order_by = Transaction.inserted_at
            elif sort_by == "row_id":
                order_by = Transaction.row_id
            elif sort_by == "statement_file_id":
                order_by = Transaction.statement_file_id
            elif sort_by.startswith("ingested_content."):
                # Dynamic field sorting - get column type from metadata for proper sorting
                json_key = sort_by.replace("ingested_content.", "")
                json_path = Transaction.ingested_content[json_key]
                text_value = func.nullif(json_path.astext, "")

                # Get column type from provided metadata
                column_type = None
                if column_types and json_key in column_types:
                    column_type = column_types[json_key]

                # Use appropriate cast based on type
                if column_type == "number":
                    # Numeric sorting for number fields
                    order_by = cast(text_value, Numeric)
                elif column_type == "date":
                    # Date sorting for date fields
                    order_by = cast(text_value, sa.Date)
                else:
                    # Text sorting for string fields or unknown types
                    order_by = text_value
            else:
                # Default to inserted_at
                order_by = Transaction.inserted_at

            if sort_dir.lower() == "asc":
                query = query.order_by(order_by.asc())
            else:
                query = query.order_by(order_by.desc())

            # Apply pagination
            skip = (page - 1) * page_size
            transactions = query.offset(skip).limit(page_size).all()

            return transactions, total
        except SQLAlchemyError as e:
            logger.error("Database error listing transactions", exc_info=True)
            self.db.rollback()
            raise DatabaseError("Failed to list transactions") from e

    def get_transaction_meta(self, account_id: Optional[int] = None) -> Dict[str, Any]:
        """Get column metadata for transactions.

        Args:
            account_id: Optional account ID to filter by

        Returns:
            Dictionary with ingested_columns and computed_columns metadata
        """
        try:
            # Sample transactions (limit 200 for performance)
            query = self.db.query(Transaction)
            if account_id is not None:
                query = query.filter(Transaction.account_id == account_id)
            sample_transactions = query.limit(200).all()

            if not sample_transactions:
                return {"ingested_columns": [], "computed_columns": []}

            # Extract unique column names from ingested_content
            column_names = set()
            for tx in sample_transactions:
                if tx.ingested_content:
                    column_names.update(tx.ingested_content.keys())

            # Build column metadata
            ingested_columns = []
            for col_name in sorted(column_names):
                # Collect sample values
                sample_values = []
                numeric_values = []
                date_values = []

                for tx in sample_transactions:
                    if tx.ingested_content and col_name in tx.ingested_content:
                        value = tx.ingested_content[col_name]
                        if value is not None:
                            sample_values.append(str(value))
                            # Try to parse as number
                            try:
                                numeric_values.append(float(value))
                            except (ValueError, TypeError):
                                pass
                            # Try to parse as date
                            try:
                                parsed_date = date_parser.parse(str(value)).date()
                                date_values.append(parsed_date)
                            except (ValueError, TypeError):
                                pass

                # Infer type (prioritize: date > number > string)
                # Only mark as date if most values are dates
                if date_values and len(date_values) >= len(numeric_values):
                    # Check if date values are more common than numeric
                    date_ratio = (
                        len(date_values) / len(sample_values) if sample_values else 0
                    )
                    if date_ratio > 0.5:  # More than 50% are dates
                        col_type = "date"
                        col_min = min(date_values).isoformat() if date_values else None
                        col_max = max(date_values).isoformat() if date_values else None
                    elif numeric_values:
                        col_type = "number"
                        col_min = min(numeric_values) if numeric_values else None
                        col_max = max(numeric_values) if numeric_values else None
                    else:
                        col_type = "string"
                        col_min = None
                        col_max = None
                elif numeric_values:
                    col_type = "number"
                    col_min = min(numeric_values) if numeric_values else None
                    col_max = max(numeric_values) if numeric_values else None
                else:
                    col_type = "string"
                    col_min = None
                    col_max = None

                ingested_columns.append(
                    {
                        "name": col_name,
                        "type": col_type,
                        "sample_values": sample_values[:10],  # Limit to 10 samples
                        "nullable": any(
                            tx.ingested_content.get(col_name) is None
                            for tx in sample_transactions
                            if tx.ingested_content
                        ),
                        "min": col_min,
                        "max": col_max,
                    }
                )

            return {"ingested_columns": ingested_columns, "computed_columns": []}
        except SQLAlchemyError as e:
            logger.error("Database error getting transaction metadata", exc_info=True)
            self.db.rollback()
            raise DatabaseError("Failed to get transaction metadata") from e

    def delete_transactions(self, account_id: Optional[int] = None) -> int:
        """Delete transactions, optionally filtered by account.

        Also resets is_ingested flag on affected statement files.

        Args:
            account_id: Optional account ID to filter by (recommended for safety)

        Returns:
            Number of transactions deleted
        """
        try:
            query = self.db.query(Transaction)

            if account_id is not None:
                query = query.filter(Transaction.account_id == account_id)

            # Get affected statement file IDs before deletion
            affected_statement_ids = {tx.statement_file_id for tx in query.all()}

            # Delete transactions
            deleted_count = query.delete(synchronize_session=False)

            # Reset is_ingested flag on affected statements
            if affected_statement_ids:
                self.db.query(StatementFile).filter(
                    StatementFile.id.in_(affected_statement_ids)
                ).update({"is_ingested": False}, synchronize_session=False)

            self.db.commit()
            return deleted_count
        except SQLAlchemyError as e:
            logger.error("Database error deleting transactions", exc_info=True)
            self.db.rollback()
            raise DatabaseError("Failed to delete transactions") from e
