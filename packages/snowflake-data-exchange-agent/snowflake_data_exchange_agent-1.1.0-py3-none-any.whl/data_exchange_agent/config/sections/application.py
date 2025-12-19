import uuid

from data_exchange_agent.config.sections.base_section_config import BaseSectionConfig


class ApplicationConfig(BaseSectionConfig):
    """Configuration class for application settings."""

    def __init__(
        self,
        workers: int | None = None,
        task_fetch_interval: int | None = None,
        debug_mode: bool | None = None,
    ):
        """
        Initialize application configuration.

        Args:
            workers: Number of worker threads (None = Not configured)
            task_fetch_interval: Interval in seconds to fetch tasks (None = Not configured)
            debug_mode: Enable debug mode (None = Not configured)

        """
        super().__init__()
        self.workers = workers
        self.task_fetch_interval = task_fetch_interval
        self.debug_mode = debug_mode
        self.agent_id = str(uuid.uuid4())

    def _custom_validation(self) -> str | None:
        """
        Validate application configuration.

        Returns:
            str | None: Error message string or None on success.

        """
        if self.workers is not None:
            if not isinstance(self.workers, int):
                return f"Workers must be an integer, got {type(self.workers).__name__}."
            if self.workers < 1:
                return "Workers must be at least 1."
            if self.workers > 100:
                return "Workers cannot exceed 100."

        if self.task_fetch_interval is not None:
            if not isinstance(self.task_fetch_interval, int):
                return f"Task fetch interval must be an integer, got {type(self.task_fetch_interval).__name__}."
            if self.task_fetch_interval < 1:
                return "Task fetch interval must be at least 1 second."

        if self.debug_mode is not None:
            if not isinstance(self.debug_mode, bool):
                return f"Debug mode must be a boolean, got {type(self.debug_mode).__name__}."

        return None

    def __repr__(self) -> str:
        """Return string representation of application configuration."""
        return (
            f"ApplicationConfig(workers={self.workers}, "
            f"task_fetch_interval={self.task_fetch_interval}, "
            f"debug_mode={self.debug_mode})"
        )
