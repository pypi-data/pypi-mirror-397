"""
Dependency injection container for the data exchange agent.

This module defines the main dependency injection container that manages
application dependencies and their lifecycle using the dependency-injector library.

Note: Do not instantiate _Container directly. Use create_container() instead.
"""

import argparse

from dependency_injector import containers, providers

from data_exchange_agent.config.manager import ConfigManager
from data_exchange_agent.constants import config_keys
from data_exchange_agent.data_sources.sf_connection import SnowflakeDataSource
from data_exchange_agent.interfaces import TaskSourceAdapter
from data_exchange_agent.task_sources import TaskSourceAdapterRegistry
from data_exchange_agent.tasks.manager import TaskManager
from data_exchange_agent.uploaders.amazon_s3_uploader import AmazonS3Uploader
from data_exchange_agent.uploaders.azure_blob_uploader import AzureBlobUploader
from data_exchange_agent.uploaders.sf_stage_uploader import SFStageUploader
from data_exchange_agent.utils.sf_logger import SFLogger


# Only export the factory function
__all__ = ["create_container"]

MODULES: list[str] = [
    "data_exchange_agent.utils.decorators",  # Uses sf_logger
    "data_exchange_agent.tasks.manager",  # Uses sf_logger, and program_config
    "data_exchange_agent.task_sources.api",  # Uses program_config
    "data_exchange_agent.task_sources.snowflake_stored_procedure",  # Uses program_config
    "data_exchange_agent.data_sources.jdbc_data_source",  # Uses sf_logger
    "data_exchange_agent.servers.flask_app",  # Uses task_manager, and program_config
    "data_exchange_agent.servers.waitress_app",  # Uses task_manager
    "data_exchange_agent.uploaders.sf_stage_uploader",  # Uses snowflake_datasource
    "data_exchange_agent.data_sources.sf_connection",  # Uses sf_logger, and program_config
]


class _Container(containers.DeclarativeContainer):
    """
    Internal dependency injection container for the data exchange agent.

    ⚠️ WARNING: Do not instantiate this class directly.
    Use create_container() instead to ensure proper initialization.

    This container manages the application's dependencies and their lifecycle.
    It provides singleton instances of core components like TaskManager and SFLogger.

    Attributes:
        config (providers.Configuration): Application configuration provider
        task_manager (providers.Singleton): Singleton provider for TaskManager instance
        sf_logger (providers.Singleton): Singleton provider for SFLogger instance
        sf_stage_uploader (providers.Singleton): Singleton provider for SFStageUploader instance
        amazon_s3_uploader (providers.Singleton): Singleton provider for AmazonS3Uploader instance
        snowflake_datasource (providers.Singleton): Singleton provider for SnowflakeDataSource instance

    """

    config = providers.Configuration()
    program_config: ConfigManager = providers.Singleton(ConfigManager)
    task_source_adapter: TaskSourceAdapter = providers.Dependency()
    task_manager: TaskManager = providers.Dependency()
    sf_logger: SFLogger = providers.Singleton(SFLogger)
    sf_stage_uploader: SFStageUploader = providers.Singleton(SFStageUploader)
    amazon_s3_uploader: AmazonS3Uploader = providers.Singleton(AmazonS3Uploader)
    snowflake_datasource: SnowflakeDataSource = providers.Singleton(SnowflakeDataSource)
    azure_blob_uploader: AzureBlobUploader = providers.Singleton(AzureBlobUploader)


def create_container(args: argparse.Namespace | None = None) -> _Container:
    """
    Create and configure a Container instance (REQUIRED).

    This is the ONLY supported way to create a Container.
    Direct instantiation of _Container is not supported.

    Args:
        args: The command line arguments (optional)

    Returns:
        Properly configured Container instance

    """
    container = _Container()

    # Configure program configuration
    if args is not None:
        container.program_config().load_cli_config(args)
    container.program_config().load_toml_config()

    # Configure task source adapter
    adapter_type = container.program_config()[config_keys.SELECTED_TASK_SOURCE]
    task_source_adapter_class = TaskSourceAdapterRegistry.get(adapter_type)
    container.task_source_adapter.override(providers.Singleton(task_source_adapter_class))

    # Configure task manager
    container.task_manager.override(
        providers.Singleton(
            TaskManager,
            workers=container.program_config()[config_keys.APPLICATION__WORKERS],
            tasks_fetch_interval=container.program_config()[config_keys.APPLICATION__TASK_FETCH_INTERVAL],
        )
    )

    # Wire all modules that use dependency injection
    container.wire(modules=MODULES)

    return container
