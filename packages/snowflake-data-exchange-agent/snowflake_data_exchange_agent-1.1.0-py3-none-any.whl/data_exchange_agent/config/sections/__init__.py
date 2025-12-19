"""
Configuration sections module.

This module contains configuration classes for different sections of the application:
- application: Application-level settings (workers, intervals, debug mode)
- server: Server settings (host, port)
- connections: Database and storage connections
- task_sources: Task source configurations
- base_section_config: Base section configuration class with validation framework
"""

from data_exchange_agent.config.sections.application import ApplicationConfig
from data_exchange_agent.config.sections.base_section_config import BaseSectionConfig
from data_exchange_agent.config.sections.connections import BaseConnectionConfig, ConnectionRegistry
from data_exchange_agent.config.sections.server import ServerConfig
from data_exchange_agent.config.sections.task_sources import TaskSourceConfig, TaskSourceRegistry


__all__ = [
    "ApplicationConfig",
    "BaseSectionConfig",
    "BaseConnectionConfig",
    "ConnectionRegistry",
    "ServerConfig",
    "TaskSourceConfig",
    "TaskSourceRegistry",
]
