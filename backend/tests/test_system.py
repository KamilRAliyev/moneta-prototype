"""Tests for system information endpoints."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from server.main import app

client = TestClient(app)


def test_system_info():
    """Test GET /api/v1/system/info endpoint."""
    r = client.get("/api/v1/system/info")
    assert r.status_code == 200
    data = r.json()

    # Check required fields
    assert "app_version" in data
    assert "environment" in data
    assert "database_connected" in data

    # Check types
    assert isinstance(data["app_version"], str)
    assert isinstance(data["environment"], str)
    assert isinstance(data["database_connected"], bool)


def test_data_dir_test_endpoint():
    """Test GET /api/v1/system/data-dir/test endpoint."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("server.core.settings.app_settings.data_dir", tmpdir):
            r = client.get("/api/v1/system/data-dir/test")
            assert r.status_code == 200
            data = r.json()

            # Check response structure
            assert "status" in data
            assert "data_dir" in data
            assert "writable" in data

            # If successful, should have test_passed
            if data["status"] == "ok":
                assert "test_passed" in data
                assert data["test_passed"] is True
                assert data["writable"] is True
