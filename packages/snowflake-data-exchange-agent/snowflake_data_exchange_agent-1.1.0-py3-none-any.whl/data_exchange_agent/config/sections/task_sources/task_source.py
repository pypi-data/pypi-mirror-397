"""Task source configuration module."""

from data_exchange_agent.config.sections.base_section_config import BaseSectionConfig


class TaskSourceConfig(BaseSectionConfig):
    """Base configuration class for task source settings."""

    def _custom_validation(self) -> str | None:
        """
        Validate the task source configuration.

        Returns:
            str | None: Error message string or None on success.

        No additional validation required at this level
        as this is a base class for all task source configurations.
        This method must be overridden in the subclasses to add additional validation logic.

        """
        return None
