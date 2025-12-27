"""Tests for Transaction API endpoints."""

import tempfile
import uuid
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from server.main import app
from server.models.account import Account, AccountType, Currency
from server.models.statement_file import StatementFile, StatementFormat, StatementStatus
from server.models.transaction import Transaction
from server.utils.hash import calculate_transaction_hash

client = TestClient(app)


def patch_db_session(test_db):
    """Context manager to patch database session for testing."""
    from server.core.database import SessionLocal

    def override_get_db():
        session = test_db()
        try:
            yield session
        finally:
            session.close()

    from unittest.mock import patch

    return patch("server.core.database.SessionLocal", test_db), patch(
        "server.core.database.get_db", override_get_db
    )


def use_test_db(test_db):
    """Context manager that patches both SessionLocal and get_db."""
    patch_session, patch_get_db = patch_db_session(test_db)
    return patch_session, patch_get_db


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_list_transactions_success(test_db):
    """Test listing transactions successfully."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
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

            # Create transactions
            transactions = [
                Transaction(
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
                for i in range(3)
            ]
            session.add_all(transactions)
            session.commit()
            session.close()

            # Test list endpoint
            response = client.get("/api/v1/transactions")
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "meta" in data
            assert len(data["items"]) == 3
            assert data["meta"]["total"] == 3
            assert data["meta"]["page"] == 1
            assert data["meta"]["page_size"] == 50
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_list_transactions_with_pagination(test_db):
    """Test listing transactions with pagination."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
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

            # Create 5 transactions
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
            session.close()

            # Test pagination
            response = client.get("/api/v1/transactions?page=1&page_size=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 2
            assert data["meta"]["total"] == 5
            assert data["meta"]["page"] == 1
            assert data["meta"]["page_size"] == 2

            # Test second page
            response2 = client.get("/api/v1/transactions?page=2&page_size=2")
            assert response2.status_code == 200
            data2 = response2.json()
            assert len(data2["items"]) == 2
            assert data2["meta"]["page"] == 2
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_list_transactions_with_account_filter(test_db):
    """Test listing transactions filtered by account_id."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
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
                is_ingested=False,
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
                is_ingested=False,
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
                    transaction_hash=calculate_transaction_hash(
                        0, {"date": "2024-01-01"}
                    ),
                ),
                Transaction(
                    id=uuid.uuid4(),
                    account_id=account1.id,
                    statement_file_id=statement1.id,
                    row_id=1,
                    ingested_content={"date": "2024-01-02"},
                    transaction_hash=calculate_transaction_hash(
                        1, {"date": "2024-01-02"}
                    ),
                ),
                Transaction(
                    id=uuid.uuid4(),
                    account_id=account2.id,
                    statement_file_id=statement2.id,
                    row_id=0,
                    ingested_content={"date": "2024-01-03"},
                    transaction_hash=calculate_transaction_hash(
                        0, {"date": "2024-01-03"}
                    ),
                ),
            ]
            session.add_all(transactions)
            session.commit()
            account1_id = account1.id
            session.close()

            # Filter by account1
            response = client.get(f"/api/v1/transactions?account_id={account1_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["meta"]["total"] == 2
            assert all(item["account"]["id"] == account1_id for item in data["items"])
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_get_transaction_meta_success(test_db):
    """Test getting transaction metadata."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
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
                row_count=2,
                status=StatementStatus.UPLOADED,
                is_ingested=False,
            )
            session.add(statement)
            session.commit()
            session.refresh(statement)

            # Create transactions
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
                        {
                            "date": "2024-01-01",
                            "amount": "-10.00",
                            "description": "Coffee",
                        },
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
                        {
                            "date": "2024-01-02",
                            "amount": "100.00",
                            "description": "Salary",
                        },
                    ),
                ),
            ]
            session.add_all(transactions)
            session.commit()
            account_id = account.id
            session.close()

            # Test meta endpoint
            response = client.get(f"/api/v1/transactions/meta?account_id={account_id}")
            assert response.status_code == 200
            data = response.json()
            assert "ingested_columns" in data
            assert "computed_columns" in data
            assert len(data["computed_columns"]) == 0

            # Check column names
            column_names = {col["name"] for col in data["ingested_columns"]}
            assert "date" in column_names
            assert "amount" in column_names
            assert "description" in column_names
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_get_transaction_meta_empty(test_db):
    """Test getting metadata when no transactions exist."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
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
            session.close()

            # Test meta endpoint
            response = client.get(f"/api/v1/transactions/meta?account_id={account.id}")
            assert response.status_code == 200
            data = response.json()
            assert "ingested_columns" in data
            assert "computed_columns" in data
            assert len(data["ingested_columns"]) == 0
            assert len(data["computed_columns"]) == 0
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_delete_transactions_with_account_id(test_db):
    """Test deleting transactions with account_id filter."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
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

            # Create transactions
            transactions = [
                Transaction(
                    id=uuid.uuid4(),
                    account_id=account1.id,
                    statement_file_id=statement1.id,
                    row_id=0,
                    ingested_content={"date": "2024-01-01"},
                    transaction_hash=calculate_transaction_hash(
                        0, {"date": "2024-01-01"}
                    ),
                ),
                Transaction(
                    id=uuid.uuid4(),
                    account_id=account2.id,
                    statement_file_id=statement2.id,
                    row_id=0,
                    ingested_content={"date": "2024-01-02"},
                    transaction_hash=calculate_transaction_hash(
                        0, {"date": "2024-01-02"}
                    ),
                ),
            ]
            session.add_all(transactions)
            session.commit()
            account1_id = account1.id
            account2_id = account2.id
            session.close()

            # Delete transactions for account1
            response = client.delete(f"/api/v1/transactions?account_id={account1_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["deleted_count"] == 1

            # Verify account1 transaction deleted, account2 still exists
            session = test_db()
            count1 = (
                session.query(Transaction)
                .filter(Transaction.account_id == account1_id)
                .count()
            )
            count2 = (
                session.query(Transaction)
                .filter(Transaction.account_id == account2_id)
                .count()
            )
            assert count1 == 0
            assert count2 == 1
            session.close()
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_delete_transactions_all(test_db):
    """Test deleting all transactions (no account_id)."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
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
                row_count=2,
                status=StatementStatus.UPLOADED,
                is_ingested=True,
            )
            session.add(statement)
            session.commit()
            session.refresh(statement)

            # Create transactions
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
                for i in range(2)
            ]
            session.add_all(transactions)
            session.commit()
            session.close()

            # Delete all transactions
            response = client.delete("/api/v1/transactions")
            assert response.status_code == 200
            data = response.json()
            assert data["deleted_count"] == 2

            # Verify all deleted
            session = test_db()
            total_count = session.query(Transaction).count()
            assert total_count == 0
            session.close()
        finally:
            try:
                session.close()
            except Exception:
                pass
