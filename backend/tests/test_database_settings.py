"""Tests for database settings configuration."""

import os
import pytest
from server.core.settings.database import DatabaseSettings


def test_database_settings_defaults():
    """Test that database settings have correct defaults."""
    # Clear environment variables to test defaults
    # Need to clear all DB-related vars including those loaded from .env file
    env_vars = [
        "DB_HOST",
        "DB_PORT",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
        "DB_POOL_SIZE",
        "DB_MAX_OVERFLOW",
        "DB_POOL_PRE_PING",
        "DB_ECHO",
    ]

    # Save original values
    original_values = {}
    for key in env_vars:
        original_values[key] = os.environ.get(key)
        if key in os.environ:
            del os.environ[key]

    try:
        settings = DatabaseSettings()

        assert settings.db_host == "localhost"
        assert settings.db_port == 5432
        assert settings.db_user == "postgres"
        assert settings.db_password == ""
        assert settings.db_name == "moneta"
        assert settings.db_pool_size == 5
        assert settings.db_max_overflow == 10
        assert settings.db_pool_pre_ping is True
        assert settings.db_echo is False
    finally:
        # Restore original values
        for key, value in original_values.items():
            if value is not None:
                os.environ[key] = value


def test_database_settings_from_env():
    """Test that database settings read from environment variables."""
    # Set test environment variables
    os.environ["DB_HOST"] = "test_host"
    os.environ["DB_PORT"] = "5433"
    os.environ["DB_USER"] = "test_user"
    os.environ["DB_PASSWORD"] = "test_password"
    os.environ["DB_NAME"] = "test_db"
    os.environ["DB_POOL_SIZE"] = "10"
    os.environ["DB_MAX_OVERFLOW"] = "20"
    os.environ["DB_POOL_PRE_PING"] = "false"
    os.environ["DB_ECHO"] = "true"

    try:
        settings = DatabaseSettings()

        assert settings.db_host == "test_host"
        assert settings.db_port == 5433
        assert settings.db_user == "test_user"
        assert settings.db_password == "test_password"
        assert settings.db_name == "test_db"
        assert settings.db_pool_size == 10
        assert settings.db_max_overflow == 20
        assert settings.db_pool_pre_ping is False
        assert settings.db_echo is True
    finally:
        # Clean up
        for key in [
            "DB_HOST",
            "DB_PORT",
            "DB_USER",
            "DB_PASSWORD",
            "DB_NAME",
            "DB_POOL_SIZE",
            "DB_MAX_OVERFLOW",
            "DB_POOL_PRE_PING",
            "DB_ECHO",
        ]:
            if key in os.environ:
                del os.environ[key]


def test_database_url_generation():
    """Test database URL generation."""
    settings = DatabaseSettings()

    # Test async URL
    url = settings.database_url
    assert url.startswith("postgresql+psycopg://")
    assert "postgres" in url
    assert "moneta" in url

    # Test sync URL
    sync_url = settings.database_url_sync
    assert sync_url.startswith("postgresql://")
    assert "postgres" in sync_url
    assert "moneta" in sync_url
    assert "+psycopg" not in sync_url
