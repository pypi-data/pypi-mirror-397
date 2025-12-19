import argparse

from typing import Any

from data_exchange_agent.config.base_config import BaseConfig
from data_exchange_agent.config.sections.application import ApplicationConfig
from data_exchange_agent.config.sections.server import ServerConfig
from data_exchange_agent.constants import config_keys


class CLIConfig(BaseConfig):
    """Configuration class for CLI settings."""

    def __init__(self):
        """Initialize CLI configuration."""
        self.application: ApplicationConfig | None = None
        self.server: ServerConfig | None = None

    def __repr__(self) -> str:
        """Return string representation of CLI configuration."""
        return f"CLIConfig(application={self.application}, server={self.server})"

    def load_config(self, args: argparse.Namespace | dict[str, Any]) -> None:
        """Load CLI configuration from command line arguments or dictionary."""
        if isinstance(args, argparse.Namespace):
            self._load_config_from_args(args)
        elif isinstance(args, dict):
            self._load_config_from_dict(args)
        elif hasattr(args, "__dict__"):
            self._load_config_from_dict(args.__dict__)
        else:
            raise TypeError("args must be an argparse.Namespace, dict or have a __dict__ attribute")

    def _load_config_from_args(self, args: argparse.Namespace) -> None:
        """Load CLI configuration from command line arguments."""
        self._load_config_from_dict(args.__dict__)

    def _load_config_from_dict(self, config: dict[str, Any]) -> None:
        """Load CLI configuration from dictionary."""
        self.application = ApplicationConfig(
            workers=config.get(config_keys.WORKERS),
            task_fetch_interval=config.get(config_keys.TASK_FETCH_INTERVAL),
            debug_mode=config.get(config_keys.DEBUG_MODE),
        )
        self.server = ServerConfig(
            host=config.get(config_keys.HOST),
            port=config.get(config_keys.PORT),
        )
