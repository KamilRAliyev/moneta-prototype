"""Database models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Import models here so Alembic can detect them
from server.models.account import (
    Account,
    AccountType,
    Currency,
    EconomicArea,
)  # noqa: E402
