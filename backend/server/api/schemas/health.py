"""Pydantic schemas for Health API."""

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Schema for health check response."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    server_time: str
    python_version: str
    system: str
    hostname: str
    process_id: int
    uptime_seconds: float | None
    app_version: str
