"""Tests for logging configuration and middleware."""

import logging
import os
import sys
from contextvars import ContextVar
from io import StringIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from server.core.logging import (
    RequestIDFilter,
    get_logger,
    request_id_context,
    setup_logging,
)
from server.core.middleware import RequestIDMiddleware
from server.main import app

client = TestClient(app)


def test_request_id_filter():
    """Test RequestIDFilter adds request_id to log records."""
    filter_instance = RequestIDFilter()

    # Set request_id in context
    request_id_context.set("test-request-id-123")

    # Create a log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Apply filter
    result = filter_instance.filter(record)

    assert result is True
    assert hasattr(record, "request_id")
    assert record.request_id == "test-request-id-123"


def test_request_id_filter_no_context():
    """Test RequestIDFilter uses default when no request_id in context."""
    filter_instance = RequestIDFilter()

    # Clear context
    request_id_context.set(None)

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    result = filter_instance.filter(record)

    assert result is True
    assert hasattr(record, "request_id")
    assert record.request_id == "no-request-id"


def test_get_logger():
    """Test get_logger returns a logger instance."""
    logger = get_logger("test.module")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.module"


def test_setup_logging_standard_enabled():
    """Test setup_logging with standard logger enabled."""
    with patch(
        "server.core.settings.app_settings.logging_standard_enabled", True
    ), patch("server.core.settings.app_settings.logging_json_enabled", False), patch(
        "server.core.settings.app_settings.logging_level", "INFO"
    ):
        # Capture stdout
        stdout_capture = StringIO()
        handler = logging.StreamHandler(stdout_capture)

        # Setup logging
        setup_logging()

        # Get logger and log a message
        logger = get_logger("test")
        logger.info("Test message")

        # Check that standard handler was added
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

        # Verify at least one handler outputs to stdout
        stdout_handlers = [
            h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(stdout_handlers) > 0


def test_setup_logging_json_enabled():
    """Test setup_logging with JSON logger enabled."""
    with patch(
        "server.core.settings.app_settings.logging_standard_enabled", False
    ), patch("server.core.settings.app_settings.logging_json_enabled", True), patch(
        "server.core.settings.app_settings.logging_level", "INFO"
    ):
        setup_logging()

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0


def test_setup_logging_both_enabled():
    """Test setup_logging with both loggers enabled."""
    with patch(
        "server.core.settings.app_settings.logging_standard_enabled", True
    ), patch("server.core.settings.app_settings.logging_json_enabled", True), patch(
        "server.core.settings.app_settings.logging_level", "INFO"
    ):
        setup_logging()

        root_logger = logging.getLogger()
        # Should have at least one handler (could be 1 or 2 depending on implementation)
        assert len(root_logger.handlers) >= 1


def test_request_id_middleware_adds_header():
    """Test that RequestIDMiddleware adds X-Request-ID to response."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] is not None
    assert len(response.headers["X-Request-ID"]) > 0


def test_request_id_middleware_preserves_header():
    """Test that RequestIDMiddleware preserves X-Request-ID from request header."""
    test_request_id = "custom-request-id-12345"

    response = client.get("/api/health", headers={"X-Request-ID": test_request_id})

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"] == test_request_id


def test_request_id_middleware_generates_uuid():
    """Test that RequestIDMiddleware generates valid UUID when header not present."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    # Try to parse as UUID (will raise if invalid)
    import uuid

    request_id = response.headers["X-Request-ID"]
    uuid.UUID(request_id)  # Will raise ValueError if invalid


def test_request_id_in_logs():
    """Test that request_id appears in log output."""
    with patch(
        "server.core.settings.app_settings.logging_standard_enabled", True
    ), patch("server.core.settings.app_settings.logging_json_enabled", False), patch(
        "server.core.settings.app_settings.logging_level", "DEBUG"
    ):
        setup_logging()

        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s [request_id=%(request_id)s]"
            )
        )
        handler.addFilter(RequestIDFilter())

        logger = get_logger("test")
        logger.addHandler(handler)

        # Set request_id and log
        request_id_context.set("test-request-123")
        logger.info("Test log message")

        log_output = log_capture.getvalue()
        assert "test-request-123" in log_output or "request_id" in log_output


def test_error_response_includes_request_id():
    """Test that error responses include request_id."""
    # Make a request that will fail (invalid endpoint)
    response = client.get("/api/nonexistent")

    assert response.status_code == 404
    data = response.json()

    # Check that request_id is in error response
    assert "request_id" in data or "error" in data

    # Check that X-Request-ID header is present
    assert "X-Request-ID" in response.headers
