from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from server.core import settings
from server.services import health, data_dir
from server.api.routers import system


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup: Initialize application
    try:
        data_dir.ensure_data_dir()
    except Exception as e:
        # Log error but don't fail startup
        print(f"Warning: Could not initialize data directory: {e}")

    yield

    # Shutdown: Cleanup code can go here if needed


app = FastAPI(title="Moneta API", version="0.1.0", lifespan=lifespan)

router = APIRouter(prefix="/api")


@router.get("/health", tags=["Health"])
def health_check():
    return health.get_health_info()


app.include_router(router)
app.include_router(system.router, prefix="/api")
