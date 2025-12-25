"""Structured logging configuration factory with environment variable control."""

import logging
import sys
from contextvars import ContextVar

from pythonjsonlogger import jsonlogger

from server.core.settings import app_settings

# Context variable to store request_id for each request
request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIDFilter(logging.Filter):
    """Log filter to add request_id to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id to log record if available."""
        record.request_id = request_id_context.get() or "no-request-id"
        return True


def _get_log_level() -> int:
    """Convert log level string to logging constant."""
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_map.get(app_settings.logging_level, logging.INFO)


def _create_standard_handler() -> logging.StreamHandler | None:
    """Create standard (human-readable) logging handler.

    Returns:
        StreamHandler configured for stdout, or None if disabled
    """
    if not app_settings.logging_standard_enabled:
        return None

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s [request_id=%(request_id)s]",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())
    return handler


def _create_json_handler() -> logging.StreamHandler | None:
    """Create JSON logging handler for structured logs (Loki/monitoring).

    Returns:
        StreamHandler configured for stderr with JSON formatter, or None if disabled
    """
    if not app_settings.logging_json_enabled:
        return None

    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s",
        timestamp=True,
    )
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())
    return handler


def setup_logging() -> None:
    """Configure logging based on environment variables.

    Supports:
    - LOGGING_STANDARD_ENABLED: Enable/disable standard (human-readable) logs (default: true)
    - LOGGING_JSON_ENABLED: Enable/disable JSON logs for Loki (default: true)
    - LOGGING_LEVEL: Log level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)

    At least one logger must be enabled. If both are disabled, standard logging is enabled.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(_get_log_level())

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create handlers based on configuration
    standard_handler = _create_standard_handler()
    json_handler = _create_json_handler()

    # Ensure at least one handler is enabled
    if not standard_handler and not json_handler:
        # Fallback: force enable standard logging if both are disabled
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s [request_id=%(request_id)s]",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        standard_handler = logging.StreamHandler(sys.stdout)
        standard_handler.setFormatter(formatter)
        standard_handler.addFilter(RequestIDFilter())

    # Add enabled handlers
    if standard_handler:
        root_logger.addHandler(standard_handler)

    if json_handler:
        root_logger.addHandler(json_handler)

    # Set uvicorn loggers to use our handlers
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    The logger will output to the configured handlers (standard and/or JSON)
    based on environment variable settings.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance configured according to settings
    """
    return logging.getLogger(name)
