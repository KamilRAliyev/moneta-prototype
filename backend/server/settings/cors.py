from typing import List
from pydantic_settings import BaseSettings


class CorsSettings(BaseSettings):
    """CORS middleware settings."""

    origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]

    class Config:
        case_sensitive = False
