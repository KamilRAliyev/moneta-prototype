"""Health check endpoints."""

from fastapi import APIRouter

from server.services import health

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    """Health check endpoint."""
    return health.get_health_info()
