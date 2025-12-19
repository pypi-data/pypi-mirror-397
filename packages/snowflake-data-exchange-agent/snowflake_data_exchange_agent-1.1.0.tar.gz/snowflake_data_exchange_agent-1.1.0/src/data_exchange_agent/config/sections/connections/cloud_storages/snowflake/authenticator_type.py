"""Snowflake authenticator type enumeration."""

from enum import Enum


class SnowflakeAuthenticatorType(str, Enum):
    """
    Enumeration of supported Snowflake authenticator types.

    This enum defines all the authenticator types that the data exchange agent
    can use.

    Attributes:
        SNOWFLAKE: Default password authenticator
        EXTERNAL_BROWSER: External browser authenticator

    """

    SNOWFLAKE = "snowflake"  # Default password auth
    EXTERNAL_BROWSER = "externalbrowser"

    # TODO: Implement other authenticator types
    # OKTA = "https://<okta_account_name>.okta.com"
    # OAUTH = "oauth"
    # SNOWFLAKE_JWT = "snowflake_jwt"
    # USERNAME_PASSWORD_MFA = "username_password_mfa"
    # OAUTH_AUTHORIZATION_CODE = "oauth_authorization_code"
    # OAUTH_CLIENT_CREDENTIALS = "oauth_client_credentials"
    # PROGRAMMING_ACCESS_TOKEN = "programming_access_token"
    # WORKLOAD_IDENTITY = "workload_identity"

    def __str__(self) -> str:
        """
        Return the string representation of the authenticator type.

        Returns:
            str: The string representation of the authenticator type.

        """
        return self.value
