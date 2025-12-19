"""
Data source type constants.

This module defines enumerations for different data source types supported
by the data exchange agent. Data sources are responsible for:
- Exporting data from the data source to a results folder
"""

from enum import Enum


class DataSourceType(str, Enum):
    """
    Enumeration of supported data source types.

    This enum defines all the data source types that the data exchange agent
    can use.

    Attributes:
        JDBC: JDBC data source

    """

    JDBC = "jdbc"

    def __str__(self) -> str:
        """
        Return the string representation of the data source type.

        Returns:
            str: The string representation of the data source type.

        """
        return self.value
