"""Tests for StatementFile model."""

import uuid
from datetime import date

import pytest

from server.models.account import Account, AccountType, Currency
from server.models.statement_file import (
    StatementFile,
    StatementFormat,
    StatementStatus,
)


def test_statement_file_model_creation(test_db):
    """Test creating a StatementFile model instance."""
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
            columns=["Date", "Description", "Amount"],
            date_from=date(2024, 1, 1),
            date_to=date(2024, 1, 31),
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )

        session.add(statement)
        session.commit()
        session.refresh(statement)

        assert statement.id is not None
        assert statement.account_id == account.id
        assert statement.original_filename == "test.csv"
        assert statement.format == StatementFormat.CSV
        assert statement.status == StatementStatus.UPLOADED
        assert statement.is_ingested is False
        assert statement.ingested_at is None
        assert statement.ingested_rows_count == 0
        assert statement.ingestion_errors_count == 0
        assert statement.date_column is None
        assert statement.created_at is not None
    finally:
        session.close()


def test_statement_file_model_with_all_fields(test_db):
    """Test StatementFile model with all fields populated."""
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

        # Create statement file with all fields
        statement = StatementFile(
            id=uuid.uuid4(),
            account_id=account.id,
            original_filename="statement_2024.csv",
            stored_filename="def456.csv",
            stored_path="/data/statements/def456.csv",
            format=StatementFormat.CSV,
            size_bytes=2048,
            content_hash="b" * 64,
            row_count=200,
            columns=["Date", "Description", "Amount", "Balance"],
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            status=StatementStatus.UPLOADED,
            is_ingested=True,
        )

        session.add(statement)
        session.commit()
        session.refresh(statement)

        assert statement.columns == ["Date", "Description", "Amount", "Balance"]
        assert statement.date_from == date(2024, 1, 1)
        assert statement.date_to == date(2024, 12, 31)
        assert statement.is_ingested is True
        assert statement.ingested_rows_count == 0
        assert statement.ingestion_errors_count == 0
        assert statement.date_column is None
    finally:
        session.close()


def test_statement_file_model_nullable_fields(test_db):
    """Test StatementFile model with nullable fields as None."""
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

        # Create statement file with nullable fields as None
        statement = StatementFile(
            id=uuid.uuid4(),
            account_id=account.id,
            original_filename="test.csv",
            stored_filename="ghi789.csv",
            stored_path="/data/statements/ghi789.csv",
            format=StatementFormat.CSV,
            size_bytes=512,
            content_hash="c" * 64,
            row_count=0,
            columns=None,
            date_from=None,
            date_to=None,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )

        session.add(statement)
        session.commit()
        session.refresh(statement)

        assert statement.columns is None
        assert statement.date_from is None
        assert statement.date_to is None
        assert statement.ingested_at is None
        assert statement.ingested_rows_count == 0
        assert statement.ingestion_errors_count == 0
        assert statement.date_column is None
    finally:
        session.close()


def test_statement_file_model_timestamps(test_db):
    """Test that StatementFile model has automatic timestamps."""
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
            content_hash="d" * 64,
            row_count=50,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )

        session.add(statement)
        session.commit()
        session.refresh(statement)

        assert statement.created_at is not None
        assert statement.updated_at is None

        # Update statement
        statement.is_ingested = True
        session.commit()
        session.refresh(statement)

        assert statement.updated_at is not None
    finally:
        session.close()


def test_statement_format_enum():
    """Test StatementFormat enum values."""
    assert StatementFormat.CSV.value == "csv"


def test_statement_status_enum():
    """Test StatementStatus enum values."""
    assert StatementStatus.UPLOADED.value == "uploaded"


def test_statement_file_foreign_key_cascade(test_db):
    """Test that deleting account cascades to statement files."""
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
            content_hash="e" * 64,
            row_count=100,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement)
        session.commit()
        statement_id = statement.id

        # Delete account
        session.delete(account)
        session.commit()

        # Verify statement file is also deleted (query in new session to avoid cache)
        new_session = test_db()
        try:
            deleted_statement = (
                new_session.query(StatementFile)
                .filter(StatementFile.id == statement_id)
                .first()
            )
            assert deleted_statement is None
        finally:
            new_session.close()
    finally:
        session.close()


def test_statement_file_unique_constraint(test_db):
    """Test unique constraint on (account_id, content_hash)."""
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

        content_hash = "f" * 64

        # Create first statement file
        statement1 = StatementFile(
            id=uuid.uuid4(),
            account_id=account.id,
            original_filename="test1.csv",
            stored_filename="pqr678.csv",
            stored_path="/data/statements/pqr678.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash=content_hash,
            row_count=100,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement1)
        session.commit()

        # Try to create duplicate (same account_id + content_hash)
        statement2 = StatementFile(
            id=uuid.uuid4(),
            account_id=account.id,
            original_filename="test2.csv",
            stored_filename="stu901.csv",
            stored_path="/data/statements/stu901.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash=content_hash,  # Same hash
            row_count=100,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        session.add(statement2)

        # Should raise IntegrityError
        with pytest.raises(Exception):  # IntegrityError or similar
            session.commit()
    finally:
        session.rollback()
        session.close()


def test_statement_file_query(test_db):
    """Test querying statement files from database."""
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

        # Create multiple statement files
        statement1 = StatementFile(
            id=uuid.uuid4(),
            account_id=account.id,
            original_filename="test1.csv",
            stored_filename="vwx234.csv",
            stored_path="/data/statements/vwx234.csv",
            format=StatementFormat.CSV,
            size_bytes=1024,
            content_hash="1" * 64,
            row_count=100,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )
        statement2 = StatementFile(
            id=uuid.uuid4(),
            account_id=account.id,
            original_filename="test2.csv",
            stored_filename="yza567.csv",
            stored_path="/data/statements/yza567.csv",
            format=StatementFormat.CSV,
            size_bytes=2048,
            content_hash="2" * 64,
            row_count=200,
            status=StatementStatus.UPLOADED,
            is_ingested=False,
        )

        session.add_all([statement1, statement2])
        session.commit()

        # Query all statements
        statements = session.query(StatementFile).all()
        assert len(statements) == 2

        # Query by account_id
        account_statements = (
            session.query(StatementFile)
            .filter(StatementFile.account_id == account.id)
            .all()
        )
        assert len(account_statements) == 2

        # Query by ID
        found_statement = (
            session.query(StatementFile)
            .filter(StatementFile.id == statement1.id)
            .first()
        )
        assert found_statement is not None
        assert found_statement.original_filename == "test1.csv"
    finally:
        session.close()
