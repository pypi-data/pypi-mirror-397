"""
Snowflake database connection implementation.

This module provides the SnowflakeDataSource class for connecting to and
executing queries against Snowflake databases using the snowflake-connector-python
library. This implementation is thread-safe using thread-local storage for connections.
"""

import threading

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from dependency_injector.wiring import Provide, inject

from data_exchange_agent.config.manager import ConfigManager
from data_exchange_agent.config.sections.connections.cloud_storages.snowflake import (
    SnowflakeConnectionConfig,
    SnowflakeConnectionNameConfig,
)
from data_exchange_agent.constants import config_keys, container_keys
from data_exchange_agent.interfaces.data_source import DataSourceInterface
from data_exchange_agent.utils.sf_logger import SFLogger


class SnowflakeDataSource(DataSourceInterface):
    """
    A thread-safe Snowflake implementation of the DataSourceInterface.

    This class provides functionality to connect to and execute queries against a Snowflake database.
    It manages connections using configuration from a Snowflake config file. Each thread gets its
    own connection to ensure thread safety.

    Attributes:
        connection_name (str | None): Name of connection configuration to use from config file
        _local (threading.local): Thread-local storage for per-thread connections

    """

    @inject
    def __init__(
        self,
        connection_name: str = None,
        logger: SFLogger = Provide[container_keys.SF_LOGGER],
        program_config: ConfigManager = Provide[container_keys.PROGRAM_CONFIG],
    ) -> None:
        """
        Initialize a new thread-safe SnowflakeDataSource.

        Args:
            connection_name (str, optional): Name of connection configuration to use.
                If None, uses default connection from config file.
            logger (SFLogger): Logger instance
            program_config (ConfigManager): Program configuration

        """
        self.logger = logger
        self.connection_name = connection_name
        if not self.connection_name:
            target_connections = program_config[config_keys.CONNECTIONS__TARGET]
            target_connections = {
                k: v for k, v in target_connections.items() if isinstance(v, SnowflakeConnectionConfig)
            }

            # Get the first Snowflake connection name configuration
            snowflake_connection_name_config = next(
                (v for v in target_connections.values() if isinstance(v, SnowflakeConnectionNameConfig)), None
            )

            if snowflake_connection_name_config:
                self.connection_name = snowflake_connection_name_config.connection_name

        # Thread-local storage for per-thread connections
        self._local = threading.local()

    def __enter__(self) -> "SnowflakeDataSource":
        """
        Enter the runtime context for the SnowflakeDataSource.

        Creates a connection for the current thread if one doesn't exist.

        Returns:
            SnowflakeDataSource: The SnowflakeDataSource instance

        """
        self.create_connection()
        return self

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None:
        """
        Exit the runtime context for the SnowflakeDataSource.

        Closes the connection for the current thread.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised

        """
        self.close_connection()

    def create_connection(self) -> None:
        """
        Create a new connection to Snowflake for the current thread if one doesn't exist.

        Uses connection details from ~/.snowflake/config.toml file.
        If connection_name is specified, uses that named connection config,
        otherwise uses the default connection config.

        This method is thread-safe - each thread gets its own connection.
        """
        # Simply call _get_thread_connection to ensure connection exists
        self._get_thread_connection()

    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """
        Context manager for getting a thread-safe cursor.

        Args:
            dict_cursor (bool): Whether to use a dictionary cursor (default: True)

        Yields:
            Cursor object for executing queries

        """
        from snowflake.connector import DictCursor

        connection = self._get_thread_connection()
        cursor_class = DictCursor if dict_cursor else None
        cursor = connection.cursor(cursor_class) if cursor_class else connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def execute_statement(self, statement: str) -> Generator[dict, None, None]:
        """
        Execute a SQL statement against Snowflake in a thread-safe manner.

        Creates a connection for the current thread if one doesn't exist, then executes
        the statement and yields the results. Each thread gets its own connection.

        Args:
            statement (str): The SQL statement to execute

        Yields:
            Results from executing the SQL statement

        """
        with self.get_cursor() as cursor:
            yield from cursor.execute(statement)

    def execute_multiple_statements(self, statements: list[str]) -> list[list[dict[str, Any]]]:
        """
        Execute multiple statements on the same connection (same thread).

        This method is useful when you need to execute multiple statements
        in sequence and want to reuse the same connection.

        Args:
            statements (list[str]): List of SQL statements to execute

        Returns:
            list[list[dict]]: List of results for each statement

        """
        results = []
        with self.get_cursor() as cursor:
            for statement in statements:
                result = list(cursor.execute(statement))
                results.append(result)
        return results

    def is_closed(self) -> bool:
        """
        Check if the Snowflake connection for the current thread is closed.

        Returns:
            bool: True if connection is closed or doesn't exist, False otherwise

        """
        if not hasattr(self._local, "connection") or self._local.connection is None:
            return True
        return self._local.connection.is_closed()

    def close_connection(self) -> None:
        """
        Close the Snowflake connection for the current thread if one exists.

        Closes the connection and removes it from thread-local storage.
        This is thread-safe - only the current thread's connection is closed.
        """
        if hasattr(self._local, "connection") and self._local.connection is not None:
            try:
                self._local.connection.close()
            except Exception as e:
                # Ignore errors during close, log error
                self.logger.error("Failed to close Snowflake connection.", exception=e)
            finally:
                self._local.connection = None

    def _get_thread_connection(self):
        """
        Get or create a connection for the current thread.

        Returns:
            snowflake.connector.SnowflakeConnection: Connection for current thread

        """
        if not hasattr(self._local, "connection") or self._local.connection is None:
            import snowflake.connector

            if self.connection_name is None:
                # Use default connection from snowflake config file (~/.snowflake/config.toml)
                self._local.connection = snowflake.connector.connect()
            else:
                # Use specified named connection from config file
                self._local.connection = snowflake.connector.connect(connection_name=self.connection_name)

        return self._local.connection
