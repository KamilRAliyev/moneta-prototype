"""Application settings."""

from server.core.settings.database import DatabaseSettings
from server.core.settings.app import AppSettings

# Initialize settings
db_settings = DatabaseSettings()
app_settings = AppSettings()

__all__ = ["db_settings", "app_settings"]
