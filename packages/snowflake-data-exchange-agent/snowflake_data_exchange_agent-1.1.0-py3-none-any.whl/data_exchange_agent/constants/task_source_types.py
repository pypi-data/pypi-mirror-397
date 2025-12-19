"""
Task source type constants.

This module defines enumerations for different task source types supported
by the data exchange agent.
"""

from enum import Enum


class TaskSourceType(str, Enum):
    """
    Enumeration of supported task source types.

    This enum defines all the task source types that the data exchange agent
    can use.

    Attributes:
        API: API connection
        FILE: File connection
        DATABASE: Database connection

    """

    API = "api"
    SNOWFLAKE_STORED_PROCEDURE = "snowflake_stored_procedure"
