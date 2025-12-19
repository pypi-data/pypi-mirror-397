"""Snowflake connection name configuration."""

from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.base import SnowflakeConnectionConfig


class SnowflakeConnectionNameConfig(SnowflakeConnectionConfig):
    """Configuration class for Snowflake connection using a named connection."""

    _required_fields = ["connection_name"]

    def __init__(self, connection_name: str) -> None:
        """
        Initialize Snowflake configuration with connection name only.

        Args:
            connection_name: Named connection from Snowflake config file

        """
        super().__init__()
        self.connection_name = connection_name

    def __repr__(self) -> str:
        """Return string representation of Snowflake connection name configuration."""
        return f"SnowflakeConnectionNameConfig(connection_name='{self.connection_name}')"

    def _custom_validation(self) -> str | None:
        """
        Validate the Snowflake connection name configuration.

        Returns:
            str | None: Error message string or None on success.

        """
        validation_error = super()._custom_validation()
        if validation_error:
            return validation_error

        connection_name_error = self._validate_identifier_with_hyphen(self.connection_name, "Connection name")
        if connection_name_error:
            return connection_name_error
        return None
