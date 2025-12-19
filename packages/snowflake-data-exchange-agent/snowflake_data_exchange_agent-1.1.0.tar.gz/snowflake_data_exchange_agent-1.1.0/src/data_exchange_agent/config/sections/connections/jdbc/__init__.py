"""JDBC connection configuration module."""

from data_exchange_agent.config.sections.connections.connection_registry import ConnectionRegistry
from data_exchange_agent.config.sections.connections.jdbc.base import BaseJDBCConnectionConfig
from data_exchange_agent.config.sections.connections.jdbc.postgresql import PostgreSQLConnectionConfig
from data_exchange_agent.config.sections.connections.jdbc.sqlserver import SQLServerConnectionConfig
from data_exchange_agent.constants.connection_types import ConnectionType


# Register connection types
ConnectionRegistry.register(ConnectionType.POSTGRESQL, PostgreSQLConnectionConfig)
ConnectionRegistry.register(ConnectionType.SQLSERVER, SQLServerConnectionConfig)

__all__ = [
    "BaseJDBCConnectionConfig",
    "PostgreSQLConnectionConfig",
    "SQLServerConnectionConfig",
]
