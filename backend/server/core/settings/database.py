"""Database configuration settings."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from env file
# Look for env/dev.env relative to project root (one level up from backend/)
project_root = Path(__file__).parent.parent.parent.parent.parent
env_file = project_root / "env" / "dev.env"
if env_file.exists():
    load_dotenv(env_file)


class DatabaseSettings:
    """Database connection settings."""

    def __init__(self):
        # PostgreSQL connection settings
        db_host = os.getenv("DB_HOST", "localhost")
        # If DB_HOST is set to 'postgres' (Docker service name), use 'localhost' for local development
        # This allows the same env file to work both in Docker and locally
        if db_host == "postgres" and not Path("/.dockerenv").exists():
            db_host = "localhost"
        self.db_host: str = db_host
        self.db_port: int = int(os.getenv("DB_PORT", "5432"))
        self.db_user: str = os.getenv("DB_USER", "postgres")
        self.db_password: str = os.getenv("DB_PASSWORD", "")
        self.db_name: str = os.getenv("DB_NAME", "moneta")

        # Connection pool settings
        self.db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
        self.db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        self.db_pool_pre_ping: bool = (
            os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
        )
        self.db_echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    @property
    def database_url(self) -> str:
        """Generate PostgreSQL database URL."""
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def database_url_sync(self) -> str:
        """Generate synchronous PostgreSQL database URL (for Alembic)."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
