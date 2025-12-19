from typing import Any

import toml

from data_exchange_agent import custom_exceptions
from data_exchange_agent.config.base_config import BaseConfig
from data_exchange_agent.config.sections.application import ApplicationConfig
from data_exchange_agent.config.sections.connections import BaseConnectionConfig
from data_exchange_agent.config.sections.connections.connection_registry import ConnectionRegistry
from data_exchange_agent.config.sections.task_sources import TaskSourceConfig, TaskSourceRegistry
from data_exchange_agent.constants import config_keys


class TomlConfig(BaseConfig):
    """Configuration class for TOML file settings."""

    def __init__(self):
        """Initialize TOML configuration."""
        self.selected_task_source: str | None = None
        self.application: ApplicationConfig | None = None
        self.task_source: TaskSourceConfig | None = None
        self.connections: dict[str, dict[str, BaseConnectionConfig]] = {
            config_keys.SOURCE: {},
            config_keys.TARGET: {},
        }

    def __repr__(self) -> str:
        """Return string representation of TOML configuration."""
        return (
            f"TomlConfig(selected_task_source={self.selected_task_source}, "
            f"application={self.application}, "
            f"task_source={self.task_source}, "
            f"connections={self.connections})"
        )

    def load_config(self, path_or_dict: str | dict[str, Any]) -> None:
        """
        Load TOML configuration from file or dictionary and load it into the configuration object.

        Args:
            path_or_dict: Path to the TOML file or dictionary

        """
        if isinstance(path_or_dict, str):
            self._load_config_from_toml(path_or_dict)
        elif isinstance(path_or_dict, dict):
            self._load_config_from_dict(path_or_dict)
        elif hasattr(path_or_dict, "__dict__"):
            self._load_config_from_dict(path_or_dict.__dict__)
        else:
            raise TypeError("path_or_dict must be a string, dict or have a __dict__ attribute")

    def _load_config_from_toml(self, toml_file_path: str) -> None:
        """
        Load TOML configuration from file and load it into the configuration object.

        Args:
            toml_file_path: Path to the TOML file

        """
        try:
            config = toml.load(toml_file_path)
            self._load_config_from_dict(config)
        except toml.TomlDecodeError as e:
            raise custom_exceptions.ConfigurationError(
                f"Failed to load configuration file '{toml_file_path}'."
                " Please check if the file is a valid TOML file."
            ) from e
        except OSError as e:
            raise custom_exceptions.ConfigurationError(
                f"Failed to load configuration file '{toml_file_path}'."
                " Please check if the file exists and is readable."
            ) from e
        except (TypeError, ValueError) as e:
            raise custom_exceptions.ConfigurationError(
                f"Invalid configuration data in file '{toml_file_path}'."
                " Please check if the file contains valid configuration data."
            ) from e
        except Exception as e:
            raise custom_exceptions.ConfigurationError(
                f"Unexpected error while loading configuration file '{toml_file_path}': {type(e).__name__}: {e}"
            ) from e

    def _load_config_from_dict(self, config: dict[str, Any]) -> None:
        """
        Load TOML configuration from dictionary and load it into the configuration object.

        Args:
            config: Dictionary containing configuration data

        """
        # Load selected task source and source connection
        if config_keys.SELECTED_TASK_SOURCE in config:
            self.selected_task_source = config[config_keys.SELECTED_TASK_SOURCE]

        # Load application configuration
        self._load_application_config(config)

        # Load task source configuration (dynamic based on type)
        self._load_task_source_config(config)

        # Load connection configuration (dynamic based on type)
        self._load_connections_config(config)

    def _load_application_config(self, config: dict[str, Any]) -> None:
        if config_keys.APPLICATION in config:
            app_config = config[config_keys.APPLICATION]
            self.application = ApplicationConfig(
                workers=app_config.get(config_keys.WORKERS),
                task_fetch_interval=app_config.get(config_keys.TASK_FETCH_INTERVAL),
                debug_mode=app_config.get(config_keys.DEBUG_MODE),
            )

    def _load_task_source_config(self, config: dict[str, Any]) -> None:
        if config_keys.TASK_SOURCE in config:
            if self.selected_task_source is None:
                raise custom_exceptions.ConfigurationError(
                    f"'{config_keys.SELECTED_TASK_SOURCE}' must be set to use '{config_keys.TASK_SOURCE}' configuration"
                )

            if not TaskSourceRegistry.is_registered(self.selected_task_source):
                available = TaskSourceRegistry.list_types()
                raise custom_exceptions.ConfigurationError(
                    f"Unknown task source type '{self.selected_task_source}'. "
                    f"Available types: {', '.join(available)}"
                )

            if self.selected_task_source in config[config_keys.TASK_SOURCE]:
                task_source_config = config[config_keys.TASK_SOURCE][self.selected_task_source]
                self.task_source = TaskSourceRegistry.create(self.selected_task_source, **task_source_config)

    def _load_connections_config(self, config: dict[str, Any]) -> None:
        if config_keys.CONNECTIONS in config:
            connections_config = config[config_keys.CONNECTIONS]

            # Load source connections
            if config_keys.SOURCE in connections_config:
                for conn_type, conn_config in connections_config[config_keys.SOURCE].items():
                    self.connections[config_keys.SOURCE][conn_type] = ConnectionRegistry.create(
                        conn_type, **conn_config
                    )

            # Load target connections
            if config_keys.TARGET in connections_config:
                for conn_type, conn_config in connections_config[config_keys.TARGET].items():
                    self.connections[config_keys.TARGET][conn_type] = ConnectionRegistry.create(
                        conn_type, **conn_config
                    )
