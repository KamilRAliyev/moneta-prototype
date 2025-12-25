"""Application settings."""

from server.core.settings.database import DatabaseSettings

# Initialize settings
db_settings = DatabaseSettings()

__all__ = ["db_settings"]
