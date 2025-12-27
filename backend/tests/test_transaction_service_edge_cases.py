"""Edge case tests for Transaction service."""

import tempfile
import uuid
from datetime import date
from pathlib import Path

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


def test_ingest_date_lock_only_from(test_db, temp_data_dir):
    """Test date lock with only datelock_from set (no upper bound)."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
            datelock_from=date(2024, 1, 15),  # Only from, no to
            datelock_to=None,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

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
            row_count=3,
            columns=["Date", "Description", "Amount"],
            date_column="Date",
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()

        # CSV with dates before and after datelock_from
        statements_dir = Path(temp_data_dir) / "statements"
        statements_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(statement.stored_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        csv_content = """Date,Description,Amount
2024-01-10,Before Lock,-10.00
2024-01-15,On Boundary,-20.00
2024-01-20,After Lock,-30.00
"""
        file_path.write_text(csv_content, encoding="utf-8")

        service = TransactionService(session)
        result = service.ingest_statement(statement_id)

        # Should skip dates >= 2024-01-15, ingest dates < 2024-01-15
        assert result["summary"]["ingested"] == 1  # Only 2024-01-10
        assert result["summary"]["skipped"] == 2  # 2024-01-15 and 2024-01-20
    finally:
        session.close()


def test_ingest_date_lock_only_to(test_db, temp_data_dir):
    """Test date lock with only datelock_to set (no lower bound)."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
            datelock_from=None,
            datelock_to=date(2024, 1, 20),  # Only to, no from
        )
        session.add(account)
        session.commit()
        session.refresh(account)

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
            row_count=3,
            columns=["Date", "Description", "Amount"],
            date_column="Date",
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()

        # CSV with dates before and after datelock_to
        statements_dir = Path(temp_data_dir) / "statements"
        statements_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(statement.stored_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        csv_content = """Date,Description,Amount
2024-01-15,Before Boundary,-10.00
2024-01-20,On Boundary,-20.00
2024-01-25,After Boundary,-30.00
"""
        file_path.write_text(csv_content, encoding="utf-8")

        service = TransactionService(session)
        result = service.ingest_statement(statement_id)

        # Should skip dates <= 2024-01-20, ingest dates > 2024-01-20
        assert result["summary"]["ingested"] == 1  # Only 2024-01-25
        assert result["summary"]["skipped"] == 2  # 2024-01-15 and 2024-01-20
    finally:
        session.close()


def test_ingest_date_lock_same_date(test_db, temp_data_dir):
    """Test date lock with datelock_from == datelock_to (single date locked)."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
            datelock_from=date(2024, 1, 15),
            datelock_to=date(2024, 1, 15),  # Same date
        )
        session.add(account)
        session.commit()
        session.refresh(account)

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
            row_count=3,
            columns=["Date", "Description", "Amount"],
            date_column="Date",
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()

        # CSV with dates before, on, and after the locked date
        statements_dir = Path(temp_data_dir) / "statements"
        statements_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(statement.stored_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        csv_content = """Date,Description,Amount
2024-01-14,Before,-10.00
2024-01-15,On Date,-20.00
2024-01-16,After,-30.00
"""
        file_path.write_text(csv_content, encoding="utf-8")

        service = TransactionService(session)
        result = service.ingest_statement(statement_id)

        # Should skip only 2024-01-15, ingest others
        assert result["summary"]["ingested"] == 2  # 2024-01-14 and 2024-01-16
        assert result["summary"]["skipped"] == 1  # Only 2024-01-15
    finally:
        session.close()


def test_ingest_no_date_column(test_db, temp_data_dir):
    """Test ingestion when statement has no date_column (should ingest all rows)."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
            datelock_from=date(2024, 1, 1),
            datelock_to=date(2024, 1, 31),
        )
        session.add(account)
        session.commit()
        session.refresh(account)

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
            columns=["Description", "Amount"],  # No date column
            date_column=None,  # No date column detected
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()

        # CSV without date column
        statements_dir = Path(temp_data_dir) / "statements"
        statements_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(statement.stored_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        csv_content = """Description,Amount
Coffee,-10.00
Salary,100.00
"""
        file_path.write_text(csv_content, encoding="utf-8")

        service = TransactionService(session)
        result = service.ingest_statement(statement_id)

        # Should ingest all rows (no date lock applied)
        assert result["status"] == "completed"
        assert result["summary"]["ingested"] == 2
        assert result["summary"]["skipped"] == 0
    finally:
        session.close()


def test_ingest_date_parsing_failure(test_db, temp_data_dir):
    """Test ingestion when date parsing fails for some rows."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

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
            row_count=3,
            columns=["Date", "Description", "Amount"],
            date_column="Date",
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()

        # CSV with invalid dates
        statements_dir = Path(temp_data_dir) / "statements"
        statements_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(statement.stored_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        csv_content = """Date,Description,Amount
2024-01-01,Valid Date,-10.00
invalid-date,Invalid Date,-20.00
2024-01-03,Valid Date 2,-30.00
"""
        file_path.write_text(csv_content, encoding="utf-8")

        service = TransactionService(session)
        result = service.ingest_statement(statement_id)

        # Invalid date parsing fails, but row is still ingested (date lock not applied)
        # All 3 rows should be ingested since date lock only applies when date parsing succeeds
        # Parse errors are logged but not added to errors list (row is still ingested)
        assert result["summary"]["ingested"] == 3  # All rows ingested
        assert (
            result["summary"]["errors"] == 0
        )  # Parse errors are logged, not tracked in errors
    finally:
        session.close()


def test_ingest_all_rows_skipped_date_lock(test_db, temp_data_dir):
    """Test when all rows are skipped due to date lock (status should be completed)."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
            datelock_from=date(2024, 1, 1),
            datelock_to=date(2024, 1, 31),
        )
        session.add(account)
        session.commit()
        session.refresh(account)

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

        # All dates within lock range
        statements_dir = Path(temp_data_dir) / "statements"
        statements_dir.mkdir(parents=True, exist_ok=True)
        file_path = Path(statement.stored_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        csv_content = """Date,Description,Amount
2024-01-15,Inside Lock,-10.00
2024-01-20,Inside Lock,-20.00
"""
        file_path.write_text(csv_content, encoding="utf-8")

        service = TransactionService(session)
        result = service.ingest_statement(statement_id)

        # Status should be completed (all skipped, only date lock errors, no parse errors)
        # Note: date lock skips are counted as errors in the summary
        assert (
            result["status"] == "completed"
        )  # All skipped with no parse errors = completed
        assert result["summary"]["ingested"] == 0
        assert result["summary"]["skipped"] == 2
        assert result["summary"]["errors"] == 2  # Date lock errors
        session.refresh(statement)
        assert statement.is_ingested is True
    finally:
        session.close()


def test_list_transactions_filtering(test_db):
    """Test filtering transactions with various operators."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

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

        # Create transactions with different amounts
        transactions = [
            Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                statement_file_id=statement.id,
                row_id=i,
                ingested_content={
                    "date": f"2024-01-{i+1:02d}",
                    "amount": f"{i*10}.00",
                    "description": f"Transaction {i}",
                },
                transaction_hash=calculate_transaction_hash(
                    i,
                    {
                        "date": f"2024-01-{i+1:02d}",
                        "amount": f"{i*10}.00",
                        "description": f"Transaction {i}",
                    },
                ),
            )
            for i in range(5)
        ]
        session.add_all(transactions)
        session.commit()

        service = TransactionService(session)

        # Filter: amount > 20.00 (should get 30.00 and 40.00)
        result, total = service.list_transactions(
            account_id=account.id,
            filters="ingested_content.amount:>:20.00",
        )
        assert total == 2  # Rows with amount 30.00 and 40.00 (strictly > 20.00)

        # Filter: description contains "Transaction"
        result2, total2 = service.list_transactions(
            account_id=account.id,
            filters="ingested_content.description:contains:Transaction",
        )
        assert total2 == 5  # All contain "Transaction"
    finally:
        session.close()


def test_list_transactions_sorting_dynamic_fields(test_db):
    """Test sorting by dynamic ingested_content fields."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

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

        # Create transactions with different amounts
        transactions = [
            Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                statement_file_id=statement.id,
                row_id=i,
                ingested_content={
                    "date": f"2024-01-{i+1:02d}",
                    "amount": f"{(3-i)*10}.00",  # Descending: 30, 20, 10
                },
                transaction_hash=calculate_transaction_hash(
                    i, {"date": f"2024-01-{i+1:02d}", "amount": f"{(3-i)*10}.00"}
                ),
            )
            for i in range(3)
        ]
        session.add_all(transactions)
        session.commit()

        service = TransactionService(session)

        # Sort by amount ascending
        result, total = service.list_transactions(
            account_id=account.id,
            sort_by="ingested_content.amount",
            sort_dir="asc",
        )
        assert len(result) == 3
        # First should be smallest amount
        assert float(result[0].ingested_content["amount"]) < float(
            result[1].ingested_content["amount"]
        )
    finally:
        session.close()


def test_list_transactions_pagination_edge_cases(test_db):
    """Test pagination edge cases."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

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

        transactions = [
            Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                statement_file_id=statement.id,
                row_id=i,
                ingested_content={"date": f"2024-01-{i+1:02d}"},
                transaction_hash=calculate_transaction_hash(
                    i, {"date": f"2024-01-{i+1:02d}"}
                ),
            )
            for i in range(5)
        ]
        session.add_all(transactions)
        session.commit()

        service = TransactionService(session)

        # Page beyond total (should return empty)
        result, total = service.list_transactions(
            account_id=account.id, page=10, page_size=10
        )
        assert len(result) == 0
        assert total == 5

        # Last page (should return remaining items)
        result2, total2 = service.list_transactions(
            account_id=account.id, page=2, page_size=3
        )
        assert len(result2) == 2  # Remaining 2 items
        assert total2 == 5
    finally:
        session.close()


def test_get_transaction_meta_empty(test_db):
    """Test getting metadata when no transactions exist."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

        service = TransactionService(session)
        meta = service.get_transaction_meta(account_id=account.id)

        assert "ingested_columns" in meta
        assert "computed_columns" in meta
        assert len(meta["ingested_columns"]) == 0
        assert len(meta["computed_columns"]) == 0
    finally:
        session.close()


def test_delete_transactions_no_account_id(test_db):
    """Test deleting all transactions (no account_id filter)."""
    session = test_db()
    try:
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

        statement1 = StatementFile(
            id=uuid.uuid4(),
            account_id=account1.id,
            original_filename="test1.csv",
            stored_filename="test1.csv",
            stored_path="/data/test1.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="test1" * 13,
            row_count=1,
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
            row_count=1,
            status=StatementStatus.UPLOADED,
            is_ingested=True,
        )
        session.add_all([statement1, statement2])
        session.commit()
        session.refresh(statement1)
        session.refresh(statement2)

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
                account_id=account2.id,
                statement_file_id=statement2.id,
                row_id=0,
                ingested_content={"date": "2024-01-02"},
                transaction_hash=calculate_transaction_hash(0, {"date": "2024-01-02"}),
            ),
        ]
        session.add_all(transactions)
        session.commit()

        # Delete all transactions (no account_id)
        service = TransactionService(session)
        deleted_count = service.delete_transactions(account_id=None)

        assert deleted_count == 2

        # Verify all transactions deleted
        total_count = session.query(Transaction).count()
        assert total_count == 0

        # Verify both statements reset
        session.refresh(statement1)
        session.refresh(statement2)
        assert statement1.is_ingested is False
        assert statement2.is_ingested is False
    finally:
        session.close()


def test_delete_transactions_no_transactions(test_db):
    """Test deleting when no transactions exist."""
    session = test_db()
    try:
        account = Account(
            name="Test Account",
            institution="Test Bank",
            currency=Currency.USD,
            type=AccountType.CHECKING,
        )
        session.add(account)
        session.commit()
        session.refresh(account)

        service = TransactionService(session)
        deleted_count = service.delete_transactions(account_id=account.id)

        assert deleted_count == 0
    finally:
        session.close()
