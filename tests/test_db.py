"""Unit tests for Neo4j database lifecycle and connectivity management."""

from unittest.mock import MagicMock

from neo4j.exceptions import ServiceUnavailable

from infragraph.config import Settings
from infragraph.db import Neo4jDatabase


def test_database_lazy_driver_initialization() -> None:
    """Verifies that the driver is not initialized until accessed."""
    db = Neo4jDatabase(settings=Settings())
    assert db._driver is None


def test_verify_connectivity_returns_false_when_unreachable() -> None:
    """Verifies that unreachable database returns False instead of raising exception."""
    unreachable_settings = Settings(
        neo4j_uri="bolt://127.0.0.1:9999",  # Port with no service
        neo4j_user="neo4j",
        neo4j_password="dev",
    )
    db = Neo4jDatabase(settings=unreachable_settings)
    is_connected = db.verify_connectivity()
    assert is_connected is False
    db.close()


def test_verify_connectivity_returns_true_when_healthy() -> None:
    """Verifies that verify_connectivity returns True when driver confirms health."""
    db = Neo4jDatabase(settings=Settings())
    mock_driver = MagicMock()
    mock_driver.verify_connectivity.return_value = None
    db._driver = mock_driver

    assert db.verify_connectivity() is True
    mock_driver.verify_connectivity.assert_called_once()


def test_verify_connectivity_handles_neo4j_errors() -> None:
    """Verifies that driver errors during healthcheck return False gracefully."""
    db = Neo4jDatabase(settings=Settings())
    mock_driver = MagicMock()
    mock_driver.verify_connectivity.side_effect = ServiceUnavailable("DB Down")
    db._driver = mock_driver

    assert db.verify_connectivity() is False


def test_database_close_cleans_resources() -> None:
    """Verifies that close() shuts down driver pool and resets state to None."""
    db = Neo4jDatabase(settings=Settings())
    mock_driver = MagicMock()
    db._driver = mock_driver

    db.close()
    mock_driver.close.assert_called_once()
    assert db._driver is None


def test_database_context_manager() -> None:
    """Verifies that with statement automatically calls close() on exit."""
    mock_driver = MagicMock()
    with Neo4jDatabase(settings=Settings()) as db:
        db._driver = mock_driver

    mock_driver.close.assert_called_once()
    assert db._driver is None
