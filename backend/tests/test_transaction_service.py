"""Tests for Transaction service."""

import csv
import tempfile
import uuid
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from server.models.account import Account, AccountType, Currency
from server.models.statement_file import StatementFile, StatementFormat, StatementStatus
from server.models.transaction import Transaction
from server.services.transaction import TransactionService
from server.utils.hash import calculate_transaction_hash


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_ingest_statement_empty_file(test_db, temp_data_dir):
    """Test ingesting an empty statement file."""
    session = test_db()
    try:
        # Create account
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

        # Create empty statement file
        statement_id = uuid.uuid4()
        statement = StatementFile(
            id=statement_id,
            account_id=account.id,
            original_filename="empty.csv",
            stored_filename=f"{statement_id}.csv",
            stored_path=str(Path(temp_data_dir) / "statements" / f"{statement_id}.csv"),
            format=StatementFormat.CSV,
            size_bytes=0,
            content_hash="empty" * 16,
            row_count=0,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()

        # Create empty CSV file
        statements_dir = Path(temp_data_dir) / "statements"
        statements_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(statement.stored_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("Date,Description,Amount\n", encoding="utf-8")

        # Ingest
        service = TransactionService(session)
        result = service.ingest_statement(statement_id)

        assert result["status"] == "completed"
        assert result["summary"]["total_rows"] == 0
        assert result["summary"]["ingested"] == 0
        assert result["summary"]["skipped"] == 0
        assert result["summary"]["errors"] == 0
        assert len(result["errors"]) == 0

        # Verify statement updated
        session.refresh(statement)
        assert statement.is_ingested is True
        assert statement.ingested_rows_count == 0
        assert statement.ingestion_errors_count == 0
        assert statement.ingested_at is not None
    finally:
        session.close()


def test_ingest_statement_with_date_lock(test_db, temp_data_dir):
    """Test ingesting statement with date lock applied."""
    session = test_db()
    try:
        # Create account with date lock
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
            datelock_from=date(2024, 1, 15),
            datelock_to=date(2024, 1, 20),
        )
        session.add(account)
        session.commit()
        session.refresh(account)

        # Create statement file
        statement_id = uuid.uuid4()
        statement = StatementFile(
            id=statement_id,
            account_id=account.id,
            original_filename="test.csv",
            stored_filename=f"{statement_id}.csv",
            stored_path=str(Path(temp_data_dir) / "statements" / f"{statement_id}.csv"),
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="test" * 16,
            row_count=5,
            columns=["Date", "Description", "Amount"],
            date_column="Date",
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()

        # Create CSV file with dates inside and outside lock range
        statements_dir = Path(temp_data_dir) / "statements"
        statements_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(statement.stored_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        csv_content = """Date,Description,Amount
2024-01-10,Before Lock,-10.00
2024-01-16,Inside Lock,-20.00
2024-01-18,Inside Lock,-30.00
2024-01-25,After Lock,-40.00
2024-01-30,After Lock,-50.00
"""
        file_path.write_text(csv_content, encoding="utf-8")

        # Ingest
        service = TransactionService(session)
        result = service.ingest_statement(statement_id)

        # Should ingest 3 rows (outside lock), skip 2 (inside lock)
        assert result["status"] == "partial"
        assert result["summary"]["total_rows"] == 5
        assert result["summary"]["ingested"] == 3
        assert result["summary"]["skipped"] == 2
        assert result["summary"]["errors"] == 2  # 2 date lock errors

        # Verify transactions created
        transactions = (
            session.query(Transaction)
            .filter(Transaction.statement_file_id == statement_id)
            .all()
        )
        assert len(transactions) == 3

        # Verify dates of ingested transactions
        ingested_dates = {tx.ingested_content.get("Date") for tx in transactions}
        assert "2024-01-10" in ingested_dates
        assert "2024-01-25" in ingested_dates
        assert "2024-01-30" in ingested_dates

        # Verify statement updated
        session.refresh(statement)
        assert statement.is_ingested is True
        assert statement.ingested_rows_count == 3
        assert statement.ingestion_errors_count == 2
    finally:
        session.close()


def test_ingest_statement_idempotency(test_db, temp_data_dir):
    """Test that re-ingesting the same statement is idempotent."""
    session = test_db()
    try:
        # Create account
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

        # Create statement file
        statement_id = uuid.uuid4()
        statement = StatementFile(
            id=statement_id,
            account_id=account.id,
            original_filename="test.csv",
            stored_filename=f"{statement_id}.csv",
            stored_path=str(Path(temp_data_dir) / "statements" / f"{statement_id}.csv"),
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="test" * 16,
            row_count=2,
            columns=["Date", "Description", "Amount"],
            date_column="Date",
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()

        # Create CSV file
        statements_dir = Path(temp_data_dir) / "statements"
        statements_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(statement.stored_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        csv_content = """Date,Description,Amount
2024-01-01,Transaction 1,-10.00
2024-01-02,Transaction 2,-20.00
"""
        file_path.write_text(csv_content, encoding="utf-8")

        # First ingestion
        service = TransactionService(session)
        result1 = service.ingest_statement(statement_id)

        assert result1["status"] == "completed"
        assert result1["summary"]["ingested"] == 2
        assert result1["summary"]["skipped"] == 0

        # Count transactions
        count1 = (
            session.query(Transaction)
            .filter(Transaction.statement_file_id == statement_id)
            .count()
        )
        assert count1 == 2

        # Reset statement
        statement.is_ingested = False
        session.commit()

        # Second ingestion (should skip existing rows)
        result2 = service.ingest_statement(statement_id)

        assert result2["status"] == "completed"
        assert result2["summary"]["ingested"] == 0
        assert result2["summary"]["skipped"] == 2  # Both rows already exist

        # Count should still be 2
        count2 = (
            session.query(Transaction)
            .filter(Transaction.statement_file_id == statement_id)
            .count()
        )
        assert count2 == 2
    finally:
        session.close()


def test_list_transactions(test_db):
    """Test listing transactions with pagination."""
    session = test_db()
    try:
        # Create account
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

        # Create statement file
        statement = StatementFile(
            id=uuid.uuid4(),
            account_id=account.id,
            original_filename="test.csv",
            stored_filename="test.csv",
            stored_path="/data/test.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="test" * 16,
            row_count=5,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)

        # Create transactions
        transactions = []
        for i in range(5):
            tx = Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                statement_file_id=statement.id,
                row_id=i,
                ingested_content={
                    "date": f"2024-01-{i+1:02d}",
                    "amount": f"-{i*10}.00",
                },
                transaction_hash=calculate_transaction_hash(
                    i, {"date": f"2024-01-{i+1:02d}", "amount": f"-{i*10}.00"}
                ),
            )
            transactions.append(tx)
        session.add_all(transactions)
        session.commit()

        # List transactions
        service = TransactionService(session)
        result, total = service.list_transactions(
            account_id=account.id,
            page=1,
            page_size=3,
        )

        assert len(result) == 3
        assert total == 5

        # Test pagination
        result2, total2 = service.list_transactions(
            account_id=account.id,
            page=2,
            page_size=3,
        )

        assert len(result2) == 2
        assert total2 == 5
    finally:
        session.close()


def test_get_transaction_meta(test_db):
    """Test getting transaction metadata."""
    session = test_db()
    try:
        # Create account
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

        # Create statement file
        statement = StatementFile(
            id=uuid.uuid4(),
            account_id=account.id,
            original_filename="test.csv",
            stored_filename="test.csv",
            stored_path="/data/test.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="test" * 16,
            row_count=3,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)

        # Create transactions with different columns
        transactions = [
            Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                statement_file_id=statement.id,
                row_id=0,
                ingested_content={
                    "date": "2024-01-01",
                    "amount": "-10.00",
                    "description": "Coffee",
                },
                transaction_hash=calculate_transaction_hash(
                    0,
                    {"date": "2024-01-01", "amount": "-10.00", "description": "Coffee"},
                ),
            ),
            Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                statement_file_id=statement.id,
                row_id=1,
                ingested_content={
                    "date": "2024-01-02",
                    "amount": "100.00",
                    "description": "Salary",
                },
                transaction_hash=calculate_transaction_hash(
                    1,
                    {"date": "2024-01-02", "amount": "100.00", "description": "Salary"},
                ),
            ),
            Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                statement_file_id=statement.id,
                row_id=2,
                ingested_content={"date": "2024-01-03", "amount": "-50.00"},
                transaction_hash=calculate_transaction_hash(
                    2, {"date": "2024-01-03", "amount": "-50.00"}
                ),
            ),
        ]
        session.add_all(transactions)
        session.commit()

        # Get metadata
        service = TransactionService(session)
        meta = service.get_transaction_meta(account_id=account.id)

        assert "ingested_columns" in meta
        assert "computed_columns" in meta
        assert len(meta["computed_columns"]) == 0

        # Check column names
        column_names = {col["name"] for col in meta["ingested_columns"]}
        assert "date" in column_names
        assert "amount" in column_names
        assert "description" in column_names

        # Check types
        date_col = next(
            col for col in meta["ingested_columns"] if col["name"] == "date"
        )
        assert date_col["type"] == "date"

        amount_col = next(
            col for col in meta["ingested_columns"] if col["name"] == "amount"
        )
        assert amount_col["type"] == "number"
    finally:
        session.close()


def test_delete_transactions(test_db):
    """Test deleting transactions with account filter."""
    session = test_db()
    try:
        # Create two accounts
        account1 = Account(
            name="Account 1",
            institution="Bank 1",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        account2 = Account(
            name="Account 2",
            institution="Bank 2",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add_all([account1, account2])
        session.commit()
        session.refresh(account1)
        session.refresh(account2)

        # Create statement files
        statement1 = StatementFile(
            id=uuid.uuid4(),
            account_id=account1.id,
            original_filename="test1.csv",
            stored_filename="test1.csv",
            stored_path="/data/test1.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="test1" * 13,
            row_count=2,
            status=StatementStatus.UPLOADED,
            is_ingested=True,
        )
        statement2 = StatementFile(
            id=uuid.uuid4(),
            account_id=account2.id,
            original_filename="test2.csv",
            stored_filename="test2.csv",
            stored_path="/data/test2.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="test2" * 13,
            row_count=2,
            status=StatementStatus.UPLOADED,
            is_ingested=True,
        )
        session.add_all([statement1, statement2])
        session.commit()
        session.refresh(statement1)
        session.refresh(statement2)

        # Create transactions for both accounts
        transactions = [
            Transaction(
                id=uuid.uuid4(),
                account_id=account1.id,
                statement_file_id=statement1.id,
                row_id=0,
                ingested_content={"date": "2024-01-01"},
                transaction_hash=calculate_transaction_hash(0, {"date": "2024-01-01"}),
            ),
            Transaction(
                id=uuid.uuid4(),
                account_id=account1.id,
                statement_file_id=statement1.id,
                row_id=1,
                ingested_content={"date": "2024-01-02"},
                transaction_hash=calculate_transaction_hash(1, {"date": "2024-01-02"}),
            ),
            Transaction(
                id=uuid.uuid4(),
                account_id=account2.id,
                statement_file_id=statement2.id,
                row_id=0,
                ingested_content={"date": "2024-01-03"},
                transaction_hash=calculate_transaction_hash(0, {"date": "2024-01-03"}),
            ),
        ]
        session.add_all(transactions)
        session.commit()

        # Delete transactions for account1 only
        service = TransactionService(session)
        deleted_count = service.delete_transactions(account_id=account1.id)

        assert deleted_count == 2

        # Verify account1 transactions deleted
        count1 = (
            session.query(Transaction)
            .filter(Transaction.account_id == account1.id)
            .count()
        )
        assert count1 == 0

        # Verify account2 transactions still exist
        count2 = (
            session.query(Transaction)
            .filter(Transaction.account_id == account2.id)
            .count()
        )
        assert count2 == 1

        # Verify statement1 is_ingested reset to False
        session.refresh(statement1)
        assert statement1.is_ingested is False

        # Verify statement2 still ingested
        session.refresh(statement2)
        assert statement2.is_ingested is True
    finally:
        session.close()
