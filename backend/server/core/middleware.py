"""Middleware for request handling."""

import uuid
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from server.core.logging import request_id_context

logger_context: ContextVar[str | None] = ContextVar("logger_context", default=None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request_id to each request."""

    async def dispatch(self, request: Request, call_next):
        """Add request_id to request and response headers."""
        # Generate or get request_id from header
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set in context for logging
        request_id_context.set(request_id)

        # Add to request state
        request.state.request_id = request_id

        # Process request
        response: Response = await call_next(request)

        # Add request_id to response header
        response.headers["X-Request-ID"] = request_id

        return response
