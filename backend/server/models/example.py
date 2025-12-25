"""Example model - delete this file when you create your own models."""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from server.models import Base


class Example(Base):
    """Example model to demonstrate the structure."""

    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
