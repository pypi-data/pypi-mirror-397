"""Snowflake connection configuration module."""

from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.base import (
    SnowflakeConnectionConfig,
    SnowflakeExtendedBaseConnectionConfig,
)
from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.connection_name import (
    SnowflakeConnectionNameConfig,
)
from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.external_browser import (
    SnowflakeConnectionExternalBrowserConfig,
)
from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.password import (
    SnowflakeConnectionPasswordConfig,
)
from data_exchange_agent.config.sections.connections.connection_registry import ConnectionRegistry
from data_exchange_agent.constants.connection_types import ConnectionType


# Register connection types
ConnectionRegistry.register(ConnectionType.SNOWFLAKE_PASSWORD, SnowflakeConnectionPasswordConfig)
ConnectionRegistry.register(ConnectionType.SNOWFLAKE_EXTERNAL_BROWSER, SnowflakeConnectionExternalBrowserConfig)
ConnectionRegistry.register(ConnectionType.SNOWFLAKE_CONNECTION_NAME, SnowflakeConnectionNameConfig)


__all__ = [
    "SnowflakeConnectionConfig",
    "SnowflakeExtendedBaseConnectionConfig",
    "SnowflakeConnectionNameConfig",
    "SnowflakeConnectionPasswordConfig",
    "SnowflakeConnectionExternalBrowserConfig",
]
