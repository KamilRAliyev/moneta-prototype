"""Application configuration settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from env file
# Look for env/dev.env relative to project root (one level up from backend/)
project_root = Path(__file__).parent.parent.parent.parent.parent
env_file = project_root / "env" / "dev.env"
if env_file.exists():
    load_dotenv(env_file)


class AppSettings:
    """Application settings."""

    def __init__(self):
        # App version - can be overridden by env var, otherwise from pyproject.toml
        self.app_version: str = os.getenv("APP_VERSION", "0.1.0")

        # Environment (dev, staging, prod, etc.)
        self.environment: str = os.getenv("ENVIRONMENT", "development")

        # Data directory for persistent storage
        self.data_dir: str = os.getenv("DATA_DIR", "/data")

        # Logging configuration
        # Enable standard (human-readable) logging (default: true)
        self.logging_standard_enabled: bool = os.getenv(
            "LOGGING_STANDARD_ENABLED", "true"
        ).lower() in ("true", "1", "yes")

        # Enable JSON logging for Loki/monitoring (default: true)
        self.logging_json_enabled: bool = os.getenv(
            "LOGGING_JSON_ENABLED", "true"
        ).lower() in ("true", "1", "yes")

        # Log level (default: INFO)
        self.logging_level: str = os.getenv("LOGGING_LEVEL", "INFO").upper()
