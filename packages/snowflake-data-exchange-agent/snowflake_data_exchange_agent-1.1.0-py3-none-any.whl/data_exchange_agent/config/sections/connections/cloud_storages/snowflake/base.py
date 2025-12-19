"""Snowflake base connection configuration classes."""

import re

from data_exchange_agent.config.sections.connections.cloud_storages.base import BaseCloudStorageConnectionConfig
from data_exchange_agent.config.sections.connections.cloud_storages.snowflake.authenticator_type import (
    SnowflakeAuthenticatorType,
)


class SnowflakeConnectionConfig(BaseCloudStorageConnectionConfig):
    """Base configuration class for Snowflake connection settings."""

    _SNOWFLAKE_IDENTIFIER_WITH_DOLLAR_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_\$]*$")
    _SNOWFLAKE_IDENTIFIER_WITH_HYPHEN_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_\-]*$")
    _SNOWFLAKE_ACCOUNT_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\.\-]*[a-zA-Z0-9]$")

    def _validate_identifier_with_dollar(self, value: str, field_name: str) -> str | None:
        """
        Validate a Snowflake identifier that allows dollar signs.

        Args:
            value: The value to validate
            field_name: The name of the field being validated

        Returns:
            str | None: Error message or None if valid

        """
        if not self._SNOWFLAKE_IDENTIFIER_WITH_DOLLAR_PATTERN.fullmatch(value):
            return (
                f"{field_name} must start with a letter or underscore,"
                " and only contain alphanumeric characters, underscores (_), and dollar signs ($)."
            )
        return None

    def _validate_identifier_with_hyphen(self, value: str, field_name: str) -> str | None:
        """
        Validate a Snowflake identifier that allows hyphens.

        Args:
            value: The value to validate
            field_name: The name of the field being validated

        Returns:
            str | None: Error message or None if valid

        """
        if not self._SNOWFLAKE_IDENTIFIER_WITH_HYPHEN_PATTERN.fullmatch(value):
            return (
                f"{field_name} must start with a letter or underscore,"
                " and only contain alphanumeric characters, underscores (_), and hyphens (-)."
            )

        return None


class SnowflakeExtendedBaseConnectionConfig(SnowflakeConnectionConfig):
    """
    Configuration class for Snowflake connection using extended base authentication.

    This is a base class for specific authentication methods (password, external browser).
    Do not instantiate directly - use subclasses instead.

    Example:
        >>> config = SnowflakeConnectionPasswordConfig(
        ...     account="myaccount",
        ...     user="myuser",
        ...     password="secret",
        ...     role="ANALYST",
        ...     warehouse="COMPUTE_WH",
        ...     database="MYDB",
        ...     schema="PUBLIC"
        ... )

    """

    _required_fields = ["authenticator", "account", "user", "role", "warehouse", "database", "schema"]

    def __init__(
        self,
        authenticator: SnowflakeAuthenticatorType,
        account: str,
        user: str,
        role: str,
        warehouse: str,
        database: str,
        schema: str,
    ) -> None:
        """
        Initialize Snowflake configuration with extended base parameters.

        Args:
            authenticator: Snowflake authenticator type
            account: Snowflake account identifier
            user: Snowflake user
            role: Snowflake role name
            warehouse: Snowflake warehouse name
            database: Snowflake database name
            schema: Snowflake schema name

        """
        super().__init__()
        self.authenticator = authenticator
        self.account = account
        self.user = user
        self.role = role
        self.warehouse = warehouse
        self.database = database
        self.schema = schema

    def _repr_fields(self) -> str:
        """Get string representation of fields (for use in __repr__)."""
        return (
            f"authenticator='{self.authenticator}', "
            f"account='{self._mask_sensitive_data(self.account)}', "
            f"user='{self.user}', "
            f"role='{self.role}', "
            f"warehouse='{self.warehouse}', "
            f"database='{self.database}', "
            f"schema='{self.schema}'"
        )

    def __repr__(self) -> str:
        """Return string representation of Snowflake extended base configuration."""
        class_name = self.__class__.__name__
        return f"{class_name}({self._repr_fields()})"

    def _custom_validation(self) -> str | None:
        """
        Validate the Snowflake extended base connection configuration.

        Returns:
            str | None: Error message string or None on success.

        """
        validation_error = super()._custom_validation()
        if validation_error:
            return validation_error

        if not isinstance(self.authenticator, SnowflakeAuthenticatorType):
            return (
                f"Authenticator must be a valid Snowflake authenticator type, got {type(self.authenticator).__name__}."
            )

        if not self._SNOWFLAKE_ACCOUNT_PATTERN.fullmatch(self.account):
            return (
                "Account must start with a letter or number,"
                " and only contain letters, numbers, hyphens (-), and dots (.)."
            )

        user_error = self._validate_identifier_with_hyphen(self.user, "User")
        if user_error:
            return user_error

        role_error = self._validate_identifier_with_dollar(self.role, "Role")
        if role_error:
            return role_error

        warehouse_error = self._validate_identifier_with_dollar(self.warehouse, "Warehouse")
        if warehouse_error:
            return warehouse_error

        database_error = self._validate_identifier_with_dollar(self.database, "Database")
        if database_error:
            return database_error

        schema_error = self._validate_identifier_with_dollar(self.schema, "Schema")
        if schema_error:
            return schema_error

        return None
