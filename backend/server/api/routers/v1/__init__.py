"""API v1 routers."""

from server.api.routers.v1 import accounts, health, meta, statements, system, uploads

__all__ = ["accounts", "health", "meta", "statements", "system", "uploads"]
