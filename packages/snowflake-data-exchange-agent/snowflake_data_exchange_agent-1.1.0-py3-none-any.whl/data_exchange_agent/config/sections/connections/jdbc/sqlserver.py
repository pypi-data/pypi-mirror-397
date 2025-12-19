import re

from urllib.parse import quote

from data_exchange_agent.config.sections.connections.jdbc.base import BaseJDBCConnectionConfig
from data_exchange_agent.constants.connection_types import ConnectionType


class SQLServerConnectionConfig(BaseJDBCConnectionConfig):
    """Configuration class for SQL Server connection settings."""

    INSTANCE_NAME_KEY = "instanceName"

    def __init__(
        self,
        username: str,
        password: str,
        database: str,
        host: str = "localhost",
        port: int = 1433,
        **extra_options: str | int | float | bool,
    ) -> None:
        """
        Initialize a SQL Server JDBC connection configuration.

        Args:
            username: Database username
            password: Database password
            database: Database name
            host: Database host address (default: localhost)
            port: Database port number (default: 1433)
            **extra_options: Extra options to add to the JDBC connection URL as key-value pairs

        """
        super().__init__(
            driver_name=ConnectionType.SQLSERVER,
            username=username,
            password=password,
            database=database,
            host=host,
            port=port,
            **extra_options,
        )

    def build_url(self) -> str:
        r"""
        Build the JDBC connection URL for SQL Server.

        Format: jdbc:sqlserver://host[\instance]:port;databaseName=database[;option=value]...
        """
        instance_name_value = self.extra_options.get(self.INSTANCE_NAME_KEY, "")
        instance_name_value = str(instance_name_value).strip() if instance_name_value else ""
        instance_name = f"\\{instance_name_value}" if instance_name_value else ""
        url = f"jdbc:sqlserver://{self.host}{instance_name}:{self.port};databaseName={self.database}"

        for key, value in self.extra_options.items():
            stripped_key = str(key).strip()
            stripped_value = str(value).strip()
            if stripped_key != self.INSTANCE_NAME_KEY:
                url += f";{quote(stripped_key)}={quote(stripped_value)}"
        return url

    def _validate_extra_options(self) -> str | None:
        parent_error = super()._validate_extra_options()
        if parent_error:
            return parent_error
        instance_name_error = self._validate_instance_name()
        if instance_name_error:
            return instance_name_error
        return None

    def _validate_instance_name(self) -> str | None:
        if self.INSTANCE_NAME_KEY in self.extra_options:
            if not isinstance(self.extra_options[self.INSTANCE_NAME_KEY], str):
                return (
                    f"Instance name must be a string, got {type(self.extra_options[self.INSTANCE_NAME_KEY]).__name__}."
                )
            instance_name_value = str(self.extra_options[self.INSTANCE_NAME_KEY])
            if not instance_name_value:
                return "Instance name cannot be empty."
            stripped_instance_name_value = instance_name_value.strip()
            if not stripped_instance_name_value:
                return "Instance name cannot contain only whitespace."
            if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_$]*", stripped_instance_name_value):
                return (
                    "Instance name must start with a letter, and only contain"
                    " alphanumeric characters, underscores (_), and dollar signs ($)."
                )
            if len(stripped_instance_name_value) > 16:
                return "Instance name length must be less than or equal to 16 characters."
        return None
