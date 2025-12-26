"""Health check endpoints."""

from fastapi import APIRouter

from server.api.schemas.health import HealthResponse
from server.services import health

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Health check endpoint."""
    return health.get_health_info()
