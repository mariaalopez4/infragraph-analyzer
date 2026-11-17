"""Configuration module for InfraGraph Analyzer.

Loads and validates environment variables from .env or system environment
using Pydantic Settings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings and external service credentials."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Neo4j Database Configuration
    neo4j_uri: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j connection URI (e.g. bolt://localhost:7687)",
    )
    neo4j_user: str = Field(
        default="neo4j",
        description="Neo4j authentication username",
    )
    neo4j_password: str = Field(
        default="infragraph_secret_dev",
        description="Neo4j authentication password",
    )

    # FastAPI Application Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="Host interface for the REST API server",
    )
    api_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Port for the REST API server",
    )
    environment: str = Field(
        default="development",
        description="Deployment environment (development, staging, production)",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )


@lru_cache
def get_settings() -> Settings:
    """Returns a cached, singleton instance of the application settings."""
    return Settings()
