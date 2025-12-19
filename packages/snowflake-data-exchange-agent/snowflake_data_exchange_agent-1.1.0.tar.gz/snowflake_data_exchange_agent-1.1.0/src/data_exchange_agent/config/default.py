from data_exchange_agent.config.base_config import BaseConfig
from data_exchange_agent.config.sections.application import ApplicationConfig
from data_exchange_agent.config.sections.server import ServerConfig
from data_exchange_agent.constants.config_defaults import (
    DEFAULT__APPLICATION__DEBUG_MODE,
    DEFAULT__APPLICATION__TASK_FETCH_INTERVAL,
    DEFAULT__APPLICATION__WORKERS,
    DEFAULT__SERVER__HOST,
    DEFAULT__SERVER__PORT,
)


class DefaultConfig(BaseConfig):
    """Configuration class for default settings."""

    def __init__(self):
        """Initialize default configuration."""
        self.application = ApplicationConfig(
            workers=DEFAULT__APPLICATION__WORKERS,
            task_fetch_interval=DEFAULT__APPLICATION__TASK_FETCH_INTERVAL,
            debug_mode=DEFAULT__APPLICATION__DEBUG_MODE,
        )
        self.server = ServerConfig(
            host=DEFAULT__SERVER__HOST,
            port=DEFAULT__SERVER__PORT,
        )

    def __repr__(self) -> str:
        """Return string representation of default configuration."""
        return f"DefaultConfig(application={self.application}, server={self.server})"
