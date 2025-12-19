"""
Connection type constants.

This module defines enumerations for different connection types supported
by the data exchange agent.
"""

from enum import Enum

from data_exchange_agent.data_sources.database_engines import DatabaseEngine


class ConnectionType(str, Enum):
    """
    Enumeration of supported connection types.

    This enum defines all the connection types that the data exchange agent
    can use.

    Attributes:
        POSTGRESQL: PostgreSQL connection
        SQLSERVER: SQL Server connection
        S3: S3 connection
        SNOWFLAKE_PASSWORD: Snowflake password connection
        SNOWFLAKE_EXTERNAL_BROWSER: Snowflake external browser connection
        SNOWFLAKE_CONNECTION_NAME: Snowflake connection name connection

    """

    # Database connections
    POSTGRESQL = DatabaseEngine.POSTGRESQL
    SQLSERVER = DatabaseEngine.SQLSERVER

    # Cloud storage connections
    S3 = "s3"
    BLOB = "blob"
    SNOWFLAKE_PASSWORD = "snowflake_password"
    SNOWFLAKE_EXTERNAL_BROWSER = "snowflake_external_browser"
    SNOWFLAKE_CONNECTION_NAME = "snowflake_connection_name"

    def __str__(self) -> str:
        """
        Return the string representation of the connection type.

        Returns:
            str: The string representation of the connection type.

        """
        return self.value
