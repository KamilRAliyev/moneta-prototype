"""Tests for Statements API endpoints."""

import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from server.main import app
from server.models.account import Account, AccountType, Currency
from server.models.statement_file import StatementFile, StatementFormat, StatementStatus

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


def test_upload_statement_success(test_db, temp_data_dir):
    """Test successful statement file upload."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account
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
            account_id = account.id
            session.close()

            # Patch data directory
            with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
                # Create test CSV file
                csv_content = (
                    b"Date,Description,Amount\n2024-01-01,Test Transaction,100.00\n"
                )
                files = {"file": ("test.csv", csv_content, "text/csv")}

                response = client.post(
                    f"/api/v1/statements?account_id={account_id}",
                    files=files,
                )

                assert response.status_code == 201
                data = response.json()
                assert "id" in data
                assert data["account_id"] == account_id
                assert data["original_filename"] == "test.csv"
                assert data["format"] == "csv"
                assert data["status"] == "uploaded"
                assert data["is_ingested"] is False
                assert data["file_exists"] is True  # File should exist after upload
                assert "row_count" in data
                # Verify new fields are set correctly
                # Verify new fields are set correctly
                assert data["ingested_rows_count"] == 0
                assert data["ingestion_errors_count"] == 0
                assert data["date_column"] == "Date"  # Should detect "Date" column
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_upload_statement_invalid_account(test_db, temp_data_dir):
    """Test uploading statement with invalid account ID."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
            csv_content = b"Date,Description,Amount\n2024-01-01,Test,100.00\n"
            files = {"file": ("test.csv", csv_content, "text/csv")}

            response = client.post("/api/v1/statements?account_id=99999", files=files)

            assert response.status_code == 404


def test_upload_statement_duplicate(test_db, temp_data_dir):
    """Test uploading duplicate statement file."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account
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
            account_id = account.id
            session.close()

            with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
                csv_content = b"Date,Description,Amount\n2024-01-01,Test,100.00\n"

                # First upload
                files1 = {"file": ("test1.csv", csv_content, "text/csv")}
                response1 = client.post(
                    f"/api/v1/statements?account_id={account_id}", files=files1
                )
                assert response1.status_code == 201

                # Duplicate upload (same content)
                files2 = {"file": ("test2.csv", csv_content, "text/csv")}
                response2 = client.post(
                    f"/api/v1/statements?account_id={account_id}", files=files2
                )

                assert response2.status_code == 409
                data = response2.json()
                assert "existing_statement_id" in data
                assert "existing_created_at" in data
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_upload_statement_invalid_file_type(test_db, temp_data_dir):
    """Test uploading non-CSV file."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account
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
            account_id = account.id
            session.close()

            with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
                files = {"file": ("test.txt", b"not a csv", "text/plain")}

                response = client.post(
                    f"/api/v1/statements?account_id={account_id}", files=files
                )

                assert response.status_code == 422
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_upload_statement_empty_file(test_db, temp_data_dir):
    """Test uploading empty file."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account
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
            account_id = account.id
            session.close()

            with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
                files = {"file": ("empty.csv", b"", "text/csv")}

                response = client.post(
                    f"/api/v1/statements?account_id={account_id}", files=files
                )

                assert response.status_code == 422
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_list_statements_empty(test_db):
    """Test listing statements when none exist."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        response = client.get("/api/v1/statements")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


def test_list_statements_with_data(test_db, temp_data_dir):
    """Test listing statements with data."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account and statements
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

            statement1 = StatementFile(
                id=uuid.uuid4(),
                account_id=account.id,
                original_filename="test1.csv",
                stored_filename="abc.csv",
                stored_path="/data/statements/abc.csv",
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
                stored_filename="def.csv",
                stored_path="/data/statements/def.csv",
                format=StatementFormat.CSV,
                size_bytes=2048,
                content_hash="2" * 64,
                row_count=200,
                status=StatementStatus.UPLOADED,
                is_ingested=False,
            )
            session.add_all([statement1, statement2])
            session.commit()
            session.close()

            response = client.get("/api/v1/statements")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert all("id" in item for item in data)
            assert all("account_id" in item for item in data)
            assert all("original_filename" in item for item in data)
            assert all(
                "file_exists" in item for item in data
            )  # file_exists should be present
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_list_statements_filter_by_account(test_db, temp_data_dir):
    """Test listing statements filtered by account ID."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create accounts
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
                currency=Currency.EUR,
                type=AccountType.SAVINGS,
            )
            session.add_all([account1, account2])
            session.commit()
            session.refresh(account1)
            session.refresh(account2)
            account1_id = account1.id  # Store ID before closing session
            account2_id = account2.id

            # Create statements for both accounts
            stmt1 = StatementFile(
                id=uuid.uuid4(),
                account_id=account1.id,
                original_filename="stmt1.csv",
                stored_filename="stmt1.csv",
                stored_path="/data/statements/stmt1.csv",
                format=StatementFormat.CSV,
                size_bytes=1024,
                content_hash="1" * 64,
                row_count=100,
                status=StatementStatus.UPLOADED,
                is_ingested=False,
            )
            stmt2 = StatementFile(
                id=uuid.uuid4(),
                account_id=account2.id,
                original_filename="stmt2.csv",
                stored_filename="stmt2.csv",
                stored_path="/data/statements/stmt2.csv",
                format=StatementFormat.CSV,
                size_bytes=2048,
                content_hash="2" * 64,
                row_count=200,
                status=StatementStatus.UPLOADED,
                is_ingested=False,
            )
            session.add_all([stmt1, stmt2])
            session.commit()
            session.close()

            # Filter by account1
            response = client.get(f"/api/v1/statements?account_id={account1_id}")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["account_id"] == account1_id
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_list_statements_pagination(test_db):
    """Test listing statements with pagination."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account and multiple statements
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

            for i in range(5):
                stmt = StatementFile(
                    id=uuid.uuid4(),
                    account_id=account.id,
                    original_filename=f"test{i}.csv",
                    stored_filename=f"test{i}.csv",
                    stored_path=f"/data/statements/test{i}.csv",
                    format=StatementFormat.CSV,
                    size_bytes=1024,
                    content_hash=f"{i}" * 64,
                    row_count=100,
                    status=StatementStatus.UPLOADED,
                    is_ingested=False,
                )
                session.add(stmt)
            session.commit()
            session.close()

            # Test pagination
            response = client.get("/api/v1/statements?skip=2&limit=2")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_get_statement_success(test_db):
    """Test getting a statement by ID."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account and statement
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
                stored_path="/data/statements/test.csv",
                format=StatementFormat.CSV,
                size_bytes=1024,
                content_hash="a" * 64,
                row_count=100,
                columns=["Date", "Description", "Amount"],
                date_from=None,
                date_to=None,
                status=StatementStatus.UPLOADED,
                is_ingested=False,
            )
            session.add(statement)
            session.commit()
            session.refresh(statement)
            statement_id = statement.id
            account_id = account.id  # Store ID before closing session
            session.close()

            response = client.get(f"/api/v1/statements/{statement_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(statement_id)
            assert data["original_filename"] == "test.csv"
            assert data["account_id"] == account_id
            assert data["columns"] == ["Date", "Description", "Amount"]
            assert "file_exists" in data  # file_exists should be present
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_get_statement_not_found(test_db):
    """Test getting a non-existent statement."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/statements/{fake_id}")

        assert response.status_code == 404


def test_delete_statement_success(test_db, temp_data_dir):
    """Test deleting a statement."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        # Create account and statement
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
                stored_path="/data/statements/test.csv",
                format=StatementFormat.CSV,
                size_bytes=1024,
                content_hash="b" * 64,
                row_count=100,
                status=StatementStatus.UPLOADED,
                is_ingested=False,
            )
            session.add(statement)
            session.commit()
            session.refresh(statement)
            statement_id = statement.id
            session.close()

            with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
                response = client.delete(f"/api/v1/statements/{statement_id}")

                assert response.status_code == 204

                # Verify statement is deleted
                get_response = client.get(f"/api/v1/statements/{statement_id}")
                assert get_response.status_code == 404
        finally:
            try:
                session.close()
            except Exception:
                pass


def test_delete_statement_not_found(test_db):
    """Test deleting a non-existent statement."""
    patch_session, patch_get_db = use_test_db(test_db)
    with patch_session, patch_get_db:
        fake_id = uuid.uuid4()
        response = client.delete(f"/api/v1/statements/{fake_id}")

        assert response.status_code == 404


def test_meta_date_formats():
    """Test meta date formats endpoint."""
    response = client.get("/api/v1/meta/statements/date-formats")

    assert response.status_code == 200
    data = response.json()

    assert "supported_formats" in data
    formats = data["supported_formats"]
    assert isinstance(formats, list)
    assert len(formats) > 0

    # Check format structure
    for fmt in formats:
        assert "format" in fmt
        assert "pattern" in fmt
        assert "description" in fmt
        assert "example" in fmt

    # Check specific formats
    format_names = [f["format"] for f in formats]
    assert "YYYY-MM-DD" in format_names
    assert "MM/DD/YYYY" in format_names


def test_meta_infer_date_format_success(temp_data_dir):
    """Test date format inference endpoint."""
    with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
        # Create test CSV with dates
        csv_content = b"Date,Description,Amount\n2024-01-15,Test 1,100.00\n2024-02-20,Test 2,200.00\n"
        files = {"file": ("test.csv", csv_content, "text/csv")}

        response = client.post("/api/v1/meta/statements/infer-date-format", files=files)

        assert response.status_code == 200
        data = response.json()

        assert "date_column_detected" in data
        assert data["date_column_detected"] is True
        assert "date_column_name" in data
        assert "inferred_format" in data
        assert "total_rows_analyzed" in data


def test_meta_infer_date_format_no_date_column(temp_data_dir):
    """Test date format inference with CSV that has no date column."""
    with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
        csv_content = b"Description,Amount\nTest 1,100.00\nTest 2,200.00\n"
        files = {"file": ("test.csv", csv_content, "text/csv")}

        response = client.post("/api/v1/meta/statements/infer-date-format", files=files)

        assert response.status_code == 200
        data = response.json()

        assert data["date_column_detected"] is False
        assert data["date_column_name"] is None
