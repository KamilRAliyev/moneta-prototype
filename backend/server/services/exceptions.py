"""Custom exceptions for services."""


class ServiceError(Exception):
    """Base exception for service errors."""

    pass


class NotFoundError(ServiceError):
    """Raised when a resource is not found."""

    pass


class ValidationError(ServiceError):
    """Raised when validation fails."""

    pass


class DatabaseError(ServiceError):
    """Raised when a database operation fails."""

    pass
