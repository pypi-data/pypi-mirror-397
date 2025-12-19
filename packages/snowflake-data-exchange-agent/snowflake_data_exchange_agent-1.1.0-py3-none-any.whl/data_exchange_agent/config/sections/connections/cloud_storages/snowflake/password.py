"""Snowflake password authentication configuration."""

from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.authenticator_type import (
    SnowflakeAuthenticatorType,
)
from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.base import (
    SnowflakeExtendedBaseConnectionConfig,
)


class SnowflakeConnectionPasswordConfig(SnowflakeExtendedBaseConnectionConfig):
    """Configuration class for Snowflake connection using user and password."""

    _required_fields = SnowflakeExtendedBaseConnectionConfig._required_fields + ["password"]

    def __init__(
        self,
        account: str,
        user: str,
        password: str,
        role: str,
        warehouse: str,
        database: str,
        schema: str,
    ) -> None:
        """
        Initialize Snowflake configuration with password authentication.

        Args:
            account: Snowflake account identifier
            user: Snowflake user
            password: Snowflake password
            role: Snowflake role name
            warehouse: Snowflake warehouse name
            database: Snowflake database name
            schema: Snowflake schema name

        """
        super().__init__(
            authenticator=SnowflakeAuthenticatorType.SNOWFLAKE,
            account=account,
            user=user,
            role=role,
            warehouse=warehouse,
            database=database,
            schema=schema,
        )
        self.password = password

    def _repr_fields(self) -> str:
        """Get string representation of fields (for use in __repr__)."""
        return super()._repr_fields() + ", password='***'"
