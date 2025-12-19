from data_exchange_agent.config.sections.task_sources.task_source import TaskSourceConfig


class ApiConfig(TaskSourceConfig):
    """Configuration class for API task source settings."""

    _required_fields = ["key"]

    def __init__(self, key: str):
        """
        Initialize API configuration.

        Args:
            key: API key for authentication

        """
        super().__init__()
        self.key = key

    def _custom_validation(self) -> str | None:
        """
        Validate the API connection configuration.

        Returns:
            str | None: Error message string or None on success.

        """
        validation_error = super()._custom_validation()
        if validation_error:
            return validation_error

        if not all(c.isprintable() for c in self.key):
            return "API key contains invalid characters."

        return None

    def __repr__(self) -> str:
        """Return string representation of API configuration."""
        return "ApiConfig(key='***')"
