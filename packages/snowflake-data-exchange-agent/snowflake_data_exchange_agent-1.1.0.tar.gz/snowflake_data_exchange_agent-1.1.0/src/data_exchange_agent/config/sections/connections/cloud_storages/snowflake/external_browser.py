"""Snowflake external browser authentication configuration."""

from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.authenticator_type import (
    SnowflakeAuthenticatorType,
)
from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.base import (
    SnowflakeExtendedBaseConnectionConfig,
)


class SnowflakeConnectionExternalBrowserConfig(SnowflakeExtendedBaseConnectionConfig):
    """Configuration class for Snowflake connection using external browser authentication."""

    def __init__(
        self,
        account: str,
        user: str,
        role: str,
        warehouse: str,
        database: str,
        schema: str,
    ) -> None:
        """
        Initialize Snowflake configuration with external browser authentication.

        Args:
            account: Snowflake account identifier
            user: Snowflake user
            role: Snowflake role name
            warehouse: Snowflake warehouse name
            database: Snowflake database name
            schema: Snowflake schema name

        """
        super().__init__(
            authenticator=SnowflakeAuthenticatorType.EXTERNAL_BROWSER,
            account=account,
            user=user,
            role=role,
            warehouse=warehouse,
            database=database,
            schema=schema,
        )
