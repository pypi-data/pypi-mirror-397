from data_exchange_agent.config.sections.connections.base import BaseConnectionConfig


class BaseCloudStorageConnectionConfig(BaseConnectionConfig):
    """Configuration class for cloud storage connection settings."""

    def _custom_validation(self) -> str | None:
        """
        Validate the cloud storage connection configuration.

        Returns:
            str | None: Error message string or None on success.

        No additional validation required at this level
        as this is a base class for all cloud storage connection configurations.
        This method must be overridden in the subclasses to add additional validation logic.

        """
        return None
