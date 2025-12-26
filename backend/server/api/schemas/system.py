"""Pydantic schemas for System API."""

from pydantic import BaseModel, ConfigDict


class SystemInfoResponse(BaseModel):
    """Schema for system info response."""

    model_config = ConfigDict(from_attributes=True)

    app_version: str
    environment: str
    database_connected: bool


class DataDirTestResponse(BaseModel):
    """Schema for data directory test response."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    data_dir: str
    writable: bool
    test_passed: bool | None = None
    error: str | None = None
