import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from server.core import settings
from server.core.logging import get_logger, setup_logging
from server.core.middleware import RequestIDMiddleware
from server.services import data_dir
from server.api.routers.v1 import health, system, uploads

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Setup structured logging
    setup_logging()
    logger.info("Starting Moneta API")

    # Startup: Initialize application
    try:
        data_dir.ensure_data_dir()
        data_dir.ensure_uploads_dir()
    except Exception as e:
        # Log error but don't fail startup
        logger.error("Could not initialize data directory", exc_info=True)

    yield

    # Shutdown: Cleanup code can go here if needed
    logger.info("Shutting down Moneta API")


app = FastAPI(
    title="Moneta API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with structured logging."""
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={"status_code": exc.status_code, "path": request.url.path},
    )

    response_data = {
        "error": exc.detail,
        "status_code": exc.status_code,
        "request_id": getattr(request.state, "request_id", None),
    }

    # Include stack trace in dev environment
    if settings.app_settings.environment == "development":
        response_data["traceback"] = traceback.format_exc()

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with structured logging."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path, "errors": exc.errors()},
    )

    response_data = {
        "error": "Validation error",
        "details": exc.errors(),
        "request_id": getattr(request.state, "request_id", None),
    }

    # Include stack trace in dev environment
    if settings.app_settings.environment == "development":
        response_data["traceback"] = traceback.format_exc()

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions with structured logging and stack traces."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path},
    )

    response_data = {
        "error": "Internal server error",
        "message": (
            str(exc)
            if settings.app_settings.environment == "development"
            else "An error occurred"
        ),
        "request_id": getattr(request.state, "request_id", None),
    }

    # Include stack trace in dev environment
    if settings.app_settings.environment == "development":
        response_data["traceback"] = traceback.format_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data,
    )


# Versioned API v1 endpoints
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v1_router.include_router(health.router)
v1_router.include_router(system.router)
v1_router.include_router(uploads.router)
app.include_router(v1_router)
