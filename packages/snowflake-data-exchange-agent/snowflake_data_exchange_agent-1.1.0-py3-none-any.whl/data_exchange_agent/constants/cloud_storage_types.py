"""
Cloud storage type constants.

This module defines enumerations for different cloud storage types supported
by the data exchange agent.
"""

from enum import Enum


class CloudStorageType(str, Enum):
    """
    Enumeration of supported cloud storage types.

    This enum defines all the cloud storage types that the data exchange agent
    can use.

    Attributes:
        S3: S3 storage
        BLOB: Blob storage
        SNOWFLAKE_STAGE: Snowflake stage storage

    """

    S3 = "s3"
    BLOB = "blob"
    SNOWFLAKE_STAGE = "snowflake:stage"
