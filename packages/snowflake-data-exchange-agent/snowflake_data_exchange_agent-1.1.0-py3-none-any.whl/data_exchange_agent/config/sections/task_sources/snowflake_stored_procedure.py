from data_exchange_agent.config.sections.task_sources.task_source import TaskSourceConfig


class SnowflakeStoredProcedureConfig(TaskSourceConfig):
    """Configuration class for Snowflake stored procedure task source settings."""

    _required_fields = ["connection_name"]

    def __init__(self, connection_name: str):
        """
        Initialize Snowflake stored procedure configuration.

        Args:
            connection_name: Connection name for Snowflake stored procedure

        """
        super().__init__()
        self.connection_name = connection_name

    def _custom_validation(self) -> str | None:
        """
        Validate the Snowflake stored procedure connection configuration.

        Returns:
            str | None: Error message string or None on success.

        """
        validation_error = super()._custom_validation()
        if validation_error:
            return validation_error

        if not all(c.isprintable() for c in self.connection_name):
            return "Connection name contains invalid characters."

        return None

    def __repr__(self) -> str:
        """Return string representation of Snowflake stored procedure configuration."""
        return f"SnowflakeStoredProcedureConfig(connection_name='{self.connection_name}')"
