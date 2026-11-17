"""Unit tests for the application configuration module."""

import pytest
from pydantic import ValidationError

from infragraph.config import Settings, get_settings


def test_default_settings() -> None:
    """Verifies that default settings match development environment values."""
    settings = Settings()
    assert settings.neo4j_uri == "bolt://localhost:7687"
    assert settings.neo4j_user == "neo4j"
    assert settings.neo4j_password == "infragraph_secret_dev"
    assert settings.api_port == 8000
    assert settings.environment == "development"


def test_settings_singleton_identity() -> None:
    """Verifies that get_settings uses lru_cache to return the same singleton."""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_invalid_api_port_validation() -> None:
    """Verifies that an out-of-range TCP port raises a ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(api_port=99999)
    assert "api_port" in str(exc_info.value)

    with pytest.raises(ValidationError):
        Settings(api_port=0)


def test_custom_settings_override() -> None:
    """Verifies that custom parameters override default settings correctly."""
    custom = Settings(
        neo4j_uri="bolt://production-db:7687",
        api_port=9000,
        environment="production",
    )
    assert custom.neo4j_uri == "bolt://production-db:7687"
    assert custom.api_port == 9000
    assert custom.environment == "production"
