"""Tests for file upload endpoints."""

import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from server.main import app

client = TestClient(app)


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_upload_file_success(temp_data_dir):
    """Test successful file upload."""
    with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
        # Create uploads directory
        uploads_dir = Path(temp_data_dir) / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Create a test CSV file
        test_content = b"col1,col2,col3\nval1,val2,val3\n"
        files = {"file": ("test.csv", test_content, "text/csv")}

        response = client.post("/api/v1/uploads", files=files)

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "file_id" in data
        assert "path" in data
        assert "filename" in data

        # Check file_id is a valid UUID
        file_id = data["file_id"]
        uuid.UUID(file_id)  # Will raise if invalid

        # Check path is correct
        assert data["path"] == str(Path(temp_data_dir) / "uploads" / f"{file_id}.csv")

        # Check filename
        assert data["filename"] == "test.csv"

        # Verify file was actually saved
        file_path = Path(data["path"])
        assert file_path.exists()
        assert file_path.read_bytes() == test_content


def test_upload_file_creates_uploads_dir(temp_data_dir):
    """Test that upload endpoint creates uploads directory if it doesn't exist."""
    with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
        # Don't create uploads directory beforehand
        test_content = b"col1,col2\nval1,val2\n"
        files = {"file": ("test.csv", test_content, "text/csv")}

        response = client.post("/api/v1/uploads", files=files)

        assert response.status_code == 201
        data = response.json()

        # Verify uploads directory was created
        uploads_dir = Path(temp_data_dir) / "uploads"
        assert uploads_dir.exists()
        assert uploads_dir.is_dir()

        # Verify file was saved
        file_path = Path(data["path"])
        assert file_path.exists()


def test_upload_file_without_file():
    """Test upload endpoint without file returns 422."""
    response = client.post("/api/v1/uploads")

    assert response.status_code == 422


def test_upload_file_multiple_uploads(temp_data_dir):
    """Test multiple file uploads generate unique file IDs."""
    with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
        uploads_dir = Path(temp_data_dir) / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        test_content = b"test,data\n"
        files = {"file": ("test1.csv", test_content, "text/csv")}

        # Upload first file
        response1 = client.post("/api/v1/uploads", files=files)
        assert response1.status_code == 201
        file_id1 = response1.json()["file_id"]

        # Upload second file
        files2 = {"file": ("test2.csv", test_content, "text/csv")}
        response2 = client.post("/api/v1/uploads", files=files2)
        assert response2.status_code == 201
        file_id2 = response2.json()["file_id"]

        # Verify file IDs are different
        assert file_id1 != file_id2

        # Verify both files exist
        path1 = Path(response1.json()["path"])
        path2 = Path(response2.json()["path"])
        assert path1.exists()
        assert path2.exists()
        assert path1 != path2


def test_upload_file_response_headers(temp_data_dir):
    """Test that upload response includes X-Request-ID header."""
    with patch("server.core.settings.app_settings.data_dir", temp_data_dir):
        uploads_dir = Path(temp_data_dir) / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        test_content = b"test,data\n"
        files = {"file": ("test.csv", test_content, "text/csv")}

        response = client.post("/api/v1/uploads", files=files)

        assert response.status_code == 201
        # Check that X-Request-ID header is present
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] is not None
