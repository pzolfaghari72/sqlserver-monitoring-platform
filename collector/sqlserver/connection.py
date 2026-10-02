"""
SQL Server connectivity module for the monitoring collector platform.

This module provides context-managed lifecycle handling for short-lived
ODBC connections to the target Microsoft SQL Server instance.
"""

import logging
from contextlib import contextmanager
from typing import Generator

import pyodbc

from collector.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class SQLServerConnector:
    """
    Manages short-lived, authenticated ODBC connections to Microsoft SQL Server.

    Handles connection setup, explicit autocommit configuration for read-only
    DMV monitoring, diagnostic logging, and deterministic resource release.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the connector with runtime configuration settings.

        Args:
            settings (Settings): Collector settings containing connection parameters.
        """
        self.settings = settings

    def build_connection_string(self) -> str:
        """Return the ODBC connection string used for SQL Server sessions."""
        return self.settings.sqlserver_odbc_connection_string

    @contextmanager
    def get_connection(self) -> Generator[pyodbc.Connection, None, None]:
        """
        Yield an active pyodbc Connection within a deterministic context.

        The connection lifecycle is split into two phases:
        1. Acquisition: Establishes ODBC connection with autocommit=True to avoid
           dangling locks or open transactions while querying system DMVs.
        2. Execution & Teardown: Yields the active connection to the caller and
           guarantees socket/connection cleanup even upon unexpected query errors.

        Yields:
            pyodbc.Connection: An open, active database connection.

        Raises:
            pyodbc.OperationalError: If the server is unreachable, DNS fails,
                or a network-level timeout occurs.
            pyodbc.Error: For driver, authentication, or ODBC protocol-level failures.
        """
        conn: pyodbc.Connection | None = None

        try:
            logger.debug(
                "Connecting to SQL Server %s:%s (database=%s)",
                self.settings.SQLSERVER_HOST,
                self.settings.SQLSERVER_PORT,
                self.settings.SQLSERVER_DATABASE,
            )

            # Establish the connection using the driver-safe formatted connection string.
            # autocommit=True prevents monitor DMV queries from spawning uncommitted implicit transactions.
            conn = pyodbc.connect(
                self.build_connection_string(),
                timeout=self.settings.SQLSERVER_CONNECTION_TIMEOUT,
                autocommit=True,
            )

        except pyodbc.OperationalError:
            logger.exception(
                "Operational error while connecting to SQL Server %s:%s",
                self.settings.SQLSERVER_HOST,
                self.settings.SQLSERVER_PORT,
            )
            raise

        except pyodbc.Error:
            logger.exception(
                "ODBC error while connecting to SQL Server %s:%s",
                self.settings.SQLSERVER_HOST,
                self.settings.SQLSERVER_PORT,
            )
            raise

        try:
            yield conn

        finally:
            if conn is not None:
                try:
                    conn.close()
                    logger.debug("SQL Server connection closed successfully.")
                except pyodbc.Error:
                    logger.exception("Error while closing SQL Server connection.")


@contextmanager
def get_sql_connection(
    settings: Settings | None = None,
) -> Generator[pyodbc.Connection, None, None]:
    """
    Context manager helper to acquire a transient SQL Server connection.

    Convenience wrapper intended for Airflow tasks, collector routines,
    and service-layer components. If settings are omitted, defaults are
    retrieved from the application environment cache.

    Args:
        settings (Settings, optional): Custom runtime settings. Defaults to None.

    Yields:
        pyodbc.Connection: An open SQL Server database connection.

    Example:
        >>> with get_sql_connection() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT @@VERSION")
    """
    if settings is None:
        settings = get_settings()

    connector = SQLServerConnector(settings)

    with connector.get_connection() as conn:
        yield conn
