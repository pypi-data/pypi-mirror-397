from urllib.parse import quote

from data_exchange_agent.config.sections.connections.jdbc.base import BaseJDBCConnectionConfig
from data_exchange_agent.constants.connection_types import ConnectionType


class PostgreSQLConnectionConfig(BaseJDBCConnectionConfig):
    """Configuration class for PostgreSQL connection settings."""

    def __init__(
        self,
        username: str,
        password: str,
        database: str,
        host: str = "localhost",
        port: int = 5432,
        **extra_options: str | int | float | bool,
    ) -> None:
        """
        Initialize a PostgreSQL JDBC connection configuration.

        Args:
            username: Database username
            password: Database password
            database: Database name
            host: Database host address (default: localhost)
            port: Database port number (default: 5432)
            **extra_options: Extra options to add to the JDBC connection URL as key-value pairs

        """
        super().__init__(
            driver_name=ConnectionType.POSTGRESQL,
            username=username,
            password=password,
            database=database,
            host=host,
            port=port,
            **extra_options,
        )

    def build_url(self) -> str:
        """
        Build the JDBC connection URL for PostgreSQL.

        Format: jdbc:postgresql://host:port/database[?option=value[&option=value]...]

        """
        url = f"jdbc:postgresql://{self.host}:{self.port}/{self.database}"
        if self.extra_options:
            separator = "?"
            for key, value in self.extra_options.items():
                stripped_key = str(key).strip()
                stripped_value = str(value).strip()
                url += f"{separator}{quote(stripped_key)}={quote(stripped_value)}"
                separator = "&"
        return url
