"""Error handling utilities for routers."""

from functools import wraps
from typing import Callable, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from server.services.exceptions import DatabaseError, NotFoundError, ValidationError

F = TypeVar("F", bound=Callable)


def handle_service_errors(func: F) -> F:
    """Decorator to handle service errors and convert to HTTP exceptions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            ) from e
        except DatabaseError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed",
            ) from e
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred",
            ) from e

    return wrapper
