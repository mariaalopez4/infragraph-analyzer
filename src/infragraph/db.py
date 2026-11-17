"""Database client and connection lifecycle manager for Neo4j."""

import logging
from typing import Self

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError

from infragraph.config import Settings, get_settings

logger = logging.getLogger(__name__)


class Neo4jDatabase:
    """Encapsulates Neo4j driver lifecycle and connectivity checks."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._driver: Driver | None = None

    @property
    def driver(self) -> Driver:
        """Returns the active Driver instance, initializing it lazily if needed."""
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self._settings.neo4j_uri,
                auth=(self._settings.neo4j_user, self._settings.neo4j_password),
            )
        return self._driver

    def verify_connectivity(self) -> bool:
        """Verifies that the database server is reachable and credentials are valid.

        Returns:
            bool: True if connection is healthy, False otherwise.
        """
        try:
            self.driver.verify_connectivity()
            logger.info(
                "Successfully verified connection to Neo4j at %s",
                self._settings.neo4j_uri,
            )
            return True
        except (DriverError, Neo4jError, OSError) as exc:
            logger.warning(
                "Failed to connect to Neo4j at %s: %s",
                self._settings.neo4j_uri,
                exc,
            )
            return False

    def close(self) -> None:
        """Closes all connections in the pool and frees resources cleanly."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            logger.info("Closed Neo4j driver connection pool.")

    def __enter__(self) -> Self:
        """Context manager support for with statements."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Ensures driver pool is closed on context exit."""
        self.close()
