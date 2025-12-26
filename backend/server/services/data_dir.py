"""Data directory management service."""

import os
from pathlib import Path

from server.core.settings import app_settings


def ensure_data_dir() -> Path:
    """Ensure data directory exists and is writable.

    Returns:
        Path to the data directory

    Raises:
        OSError: If directory cannot be created or is not writable
    """
    data_path = Path(app_settings.data_dir)

    # Create directory if it doesn't exist
    try:
        data_path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise OSError(
            f"Permission denied creating data directory {data_path}. "
            f"Check volume mount permissions. Error: {e}"
        ) from e

    # Try to set permissions (may fail if not root, but that's ok)
    try:
        os.chmod(data_path, 0o755)
    except (OSError, PermissionError):
        # Ignore permission errors when setting chmod
        pass

    # Check if directory is writable
    if not os.access(data_path, os.W_OK):
        # Try to get more info about the issue
        stat_info = data_path.stat()
        raise OSError(
            f"Data directory {data_path} is not writable. "
            f"Mode: {oct(stat_info.st_mode)}, Owner: {stat_info.st_uid}, "
            f"Group: {stat_info.st_gid}. "
            f"Check Docker volume mount permissions."
        )

    return data_path


def ensure_uploads_dir() -> Path:
    """Ensure uploads directory exists within data directory.

    Returns:
        Path to the uploads directory

    Raises:
        OSError: If directory cannot be created or is not writable
    """
    data_path = ensure_data_dir()
    uploads_path = data_path / "uploads"

    # Create directory if it doesn't exist
    try:
        uploads_path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise OSError(
            f"Permission denied creating uploads directory {uploads_path}. "
            f"Check volume mount permissions. Error: {e}"
        ) from e

    # Try to set permissions (may fail if not root, but that's ok)
    try:
        os.chmod(uploads_path, 0o755)
    except (OSError, PermissionError):
        # Ignore permission errors when setting chmod
        pass

    # Check if directory is writable
    if not os.access(uploads_path, os.W_OK):
        # Try to get more info about the issue
        stat_info = uploads_path.stat()
        raise OSError(
            f"Uploads directory {uploads_path} is not writable. "
            f"Mode: {oct(stat_info.st_mode)}, Owner: {stat_info.st_uid}, "
            f"Group: {stat_info.st_gid}. "
            f"Check Docker volume mount permissions."
        )

    return uploads_path


def ensure_statements_dir() -> Path:
    """Ensure statements directory exists within data directory.

    Returns:
        Path to the statements directory

    Raises:
        OSError: If directory cannot be created or is not writable
    """
    data_path = ensure_data_dir()
    statements_path = data_path / "statements"

    # Create directory if it doesn't exist
    try:
        statements_path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise OSError(
            f"Permission denied creating statements directory {statements_path}. "
            f"Check volume mount permissions. Error: {e}"
        ) from e

    # Try to set permissions (may fail if not root, but that's ok)
    try:
        os.chmod(statements_path, 0o755)
    except (OSError, PermissionError):
        # Ignore permission errors when setting chmod
        pass

    # Check if directory is writable
    if not os.access(statements_path, os.W_OK):
        # Try to get more info about the issue
        stat_info = statements_path.stat()
        raise OSError(
            f"Statements directory {statements_path} is not writable. "
            f"Mode: {oct(stat_info.st_mode)}, Owner: {stat_info.st_uid}, "
            f"Group: {stat_info.st_gid}. "
            f"Check Docker volume mount permissions."
        )

    return statements_path


def test_data_dir_write() -> dict:
    """Test writing to data directory.

    Returns:
        dict with test results
    """
    try:
        data_path = ensure_data_dir()
        test_file = data_path / ".test_write"

        # Write test file
        test_file.write_text("test")

        # Read it back
        content = test_file.read_text()

        # Clean up
        test_file.unlink()

        return {
            "status": "ok",
            "data_dir": str(data_path),
            "writable": True,
            "test_passed": content == "test",
        }
    except Exception as e:
        return {
            "status": "error",
            "data_dir": app_settings.data_dir,
            "writable": False,
            "error": str(e),
        }
