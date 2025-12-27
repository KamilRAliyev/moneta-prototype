"""Tests for Transaction model."""

import uuid
from datetime import datetime

import pytest

from server.models.account import Account, AccountType, Currency
from server.models.statement_file import StatementFile, StatementFormat, StatementStatus
from server.models.transaction import Transaction


def test_transaction_model_creation(test_db):
    """Test creating a Transaction model instance."""
    session = test_db()

    try:
        # Create account first
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
            stored_filename="abc123.csv",
            stored_path="/data/statements/abc123.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="a" * 64,
            row_count=100,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)

        # Create transaction
        transaction = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=0,
            ingested_content={
                "date": "2024-01-01",
                "amount": "-4.50",
                "description": "Coffee",
            },
            transaction_hash="b" * 64,
            computed_content={},
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        assert transaction.id is not None
        assert transaction.account_id == account.id
        assert transaction.statement_file_id == statement.id
        assert transaction.row_id == 0
        assert transaction.ingested_content == {
            "date": "2024-01-01",
            "amount": "-4.50",
            "description": "Coffee",
        }
        assert transaction.transaction_hash == "b" * 64
        assert transaction.computed_content == {}
        assert transaction.computed_content_hash is None
        assert transaction.inserted_at is not None
        assert transaction.updated_at is None
        assert transaction.computed_at is None
    finally:
        session.close()


def test_transaction_model_with_all_fields(test_db):
    """Test Transaction model with all fields populated."""
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
            stored_filename="def456.csv",
            stored_path="/data/statements/def456.csv",
            format=StatementFormat.CSV,
            size_bytes=2048,
            content_hash="c" * 64,
            row_count=200,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)

        # Create transaction with all fields
        transaction = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=42,
            ingested_content={
                "date": "2024-01-15",
                "amount": "100.00",
                "description": "Salary",
            },
            transaction_hash="d" * 64,
            computed_content={"category": "income"},
            computed_content_hash="e" * 64,
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        assert transaction.row_id == 42
        assert transaction.ingested_content["date"] == "2024-01-15"
        assert transaction.computed_content == {"category": "income"}
        assert transaction.computed_content_hash == "e" * 64
    finally:
        session.close()


def test_transaction_model_nullable_fields(test_db):
    """Test Transaction model with nullable fields as None."""
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
            stored_filename="ghi789.csv",
            stored_path="/data/statements/ghi789.csv",
            format=StatementFormat.CSV,
            size_bytes=512,
            content_hash="f" * 64,
            row_count=0,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)

        # Create transaction with nullable fields as None
        transaction = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=0,
            ingested_content={},
            transaction_hash="g" * 64,
            computed_content=None,
            computed_content_hash=None,
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        assert transaction.computed_content is None
        assert transaction.computed_content_hash is None
        assert transaction.computed_at is None
    finally:
        session.close()


def test_transaction_model_timestamps(test_db):
    """Test that Transaction model has automatic timestamps."""
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
            stored_filename="jkl012.csv",
            stored_path="/data/statements/jkl012.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="h" * 64,
            row_count=50,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)

        # Create transaction
        transaction = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=0,
            ingested_content={"date": "2024-01-01"},
            transaction_hash="i" * 64,
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        assert transaction.inserted_at is not None
        assert transaction.updated_at is None

        # Update transaction
        transaction.ingested_content = {"date": "2024-01-02"}
        session.commit()
        session.refresh(transaction)

        assert transaction.updated_at is not None
    finally:
        session.close()


def test_transaction_model_foreign_key_cascade(test_db):
    """Test that deleting account cascades to transactions."""
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
            stored_filename="mno345.csv",
            stored_path="/data/statements/mno345.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="j" * 64,
            row_count=100,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)

        # Create transaction
        transaction = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=0,
            ingested_content={"date": "2024-01-01"},
            transaction_hash="k" * 64,
        )
        session.add(transaction)
        session.commit()
        transaction_id = transaction.id

        # Delete account
        session.delete(account)
        session.commit()

        # Verify transaction is also deleted (query in new session to avoid cache)
        new_session = test_db()
        try:
            deleted_transaction = (
                new_session.query(Transaction)
                .filter(Transaction.id == transaction_id)
                .first()
            )
            assert deleted_transaction is None
        finally:
            new_session.close()
    finally:
        session.close()


def test_transaction_model_statement_file_cascade(test_db):
    """Test that deleting statement file cascades to transactions."""
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
            stored_filename="pqr678.csv",
            stored_path="/data/statements/pqr678.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="l" * 64,
            row_count=100,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)
        statement_id = statement.id

        # Create transaction
        transaction = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=0,
            ingested_content={"date": "2024-01-01"},
            transaction_hash="m" * 64,
        )
        session.add(transaction)
        session.commit()
        transaction_id = transaction.id

        # Delete statement file
        session.delete(statement)
        session.commit()

        # Verify transaction is also deleted
        new_session = test_db()
        try:
            deleted_transaction = (
                new_session.query(Transaction)
                .filter(Transaction.id == transaction_id)
                .first()
            )
            assert deleted_transaction is None
        finally:
            new_session.close()
    finally:
        session.close()


def test_transaction_model_unique_constraint(test_db):
    """Test unique constraint on (statement_file_id, row_id)."""
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
            stored_filename="stu901.csv",
            stored_path="/data/statements/stu901.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="n" * 64,
            row_count=100,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)

        # Create first transaction
        transaction1 = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=5,
            ingested_content={"date": "2024-01-01"},
            transaction_hash="o" * 64,
        )
        session.add(transaction1)
        session.commit()

        # Try to create duplicate (same statement_file_id + row_id)
        transaction2 = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=5,  # Same row_id
            ingested_content={"date": "2024-01-02"},
            transaction_hash="p" * 64,
        )
        session.add(transaction2)

        # Should raise IntegrityError
        with pytest.raises(Exception):  # IntegrityError or similar
            session.commit()
    finally:
        session.rollback()
        session.close()


def test_transaction_model_query(test_db):
    """Test querying transactions from database."""
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
            stored_filename="vwx234.csv",
            stored_path="/data/statements/vwx234.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="q" * 64,
            row_count=100,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        session.refresh(statement)

        # Create multiple transactions
        transaction1 = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=0,
            ingested_content={"date": "2024-01-01", "amount": "-10.00"},
            transaction_hash="1" * 64,
        )
        transaction2 = Transaction(
            id=uuid.uuid4(),
            account_id=account.id,
            statement_file_id=statement.id,
            row_id=1,
            ingested_content={"date": "2024-01-02", "amount": "100.00"},
            transaction_hash="2" * 64,
        )

        session.add_all([transaction1, transaction2])
        session.commit()

        # Query all transactions
        transactions = session.query(Transaction).all()
        assert len(transactions) == 2

        # Query by account_id
        account_transactions = (
            session.query(Transaction)
            .filter(Transaction.account_id == account.id)
            .all()
        )
        assert len(account_transactions) == 2

        # Query by statement_file_id
        statement_transactions = (
            session.query(Transaction)
            .filter(Transaction.statement_file_id == statement.id)
            .all()
        )
        assert len(statement_transactions) == 2

        # Query by ID
        found_transaction = (
            session.query(Transaction).filter(Transaction.id == transaction1.id).first()
        )
        assert found_transaction is not None
        assert found_transaction.row_id == 0
    finally:
        session.close()
