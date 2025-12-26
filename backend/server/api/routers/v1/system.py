"""System information endpoints."""

from fastapi import APIRouter
from sqlalchemy import text

from server.api.schemas.system import DataDirTestResponse, SystemInfoResponse
from server.core.database import get_engine
from server.core.settings import app_settings
from server.services import data_dir

router = APIRouter(prefix="/system", tags=["System"])


def check_database_connection() -> bool:
    """Check if database is connected and accessible."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@router.get("/info", response_model=SystemInfoResponse)
def get_system_info() -> SystemInfoResponse:
    """Get system information including app version, environment, and database status."""
    return {
        "app_version": app_settings.app_version,
        "environment": app_settings.environment,
        "database_connected": check_database_connection(),
    }


@router.get("/data-dir/test", response_model=DataDirTestResponse)
def test_data_directory() -> DataDirTestResponse:
    """Test data directory read/write capabilities."""
    return data_dir.test_data_dir_write()
